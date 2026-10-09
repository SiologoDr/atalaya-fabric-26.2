package com.atalaya.entity;

import com.atalaya.particula.AtalayaParticulas;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.util.Mth;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.storage.ValueInput;
import net.minecraft.world.level.storage.ValueOutput;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;
import org.jspecify.annotations.Nullable;

import java.util.HashSet;
import java.util.Set;
import java.util.UUID;

/**
 * Una pared de agua que avanza en linea recta, desde el remake de octubre de
 * 2026 (antes las olas eran solo particulas):
 *
 * <ul>
 *   <li>la ola del Rompeolas: solo se ve; el golpe lo sigue dando Nerea
 *       ({@link NereaEntity}, golpearLinea) con los numeros de siempre;</li>
 *   <li>la Gran Marea: cruza la arena de lado a lado (80 bloques) con un solo
 *       hueco, que se marca en el suelo antes de que salga. Golpea ella misma:
 *       si te pilla, te arrastra y te mata; solo salva un totem (y se gasta).</li>
 * </ul>
 *
 * No se mueve: se queda donde nacio y el frente se calcula con la edad (igual
 * en el servidor y en el cliente), asi que mientras avanza no gasta red. La
 * dibuja OlaNereaRenderer.
 */
public class OlaNereaEntity extends Entity {

    /** Lo que tarda en apagarse cuando llega al final. */
    public static final int APAGA = 12;

    /** Medio ancho (de lado a lado), alto, bloques por tick y lo que recorre. */
    private static final EntityDataAccessor<Float> DATA_ANCHO =
            SynchedEntityData.defineId(OlaNereaEntity.class, EntityDataSerializers.FLOAT);
    private static final EntityDataAccessor<Float> DATA_ALTO =
            SynchedEntityData.defineId(OlaNereaEntity.class, EntityDataSerializers.FLOAT);
    private static final EntityDataAccessor<Float> DATA_VEL =
            SynchedEntityData.defineId(OlaNereaEntity.class, EntityDataSerializers.FLOAT);
    private static final EntityDataAccessor<Float> DATA_LARGO =
            SynchedEntityData.defineId(OlaNereaEntity.class, EntityDataSerializers.FLOAT);
    /** El hueco de la Gran Marea: donde cae (bloques a un lado, como "lado") y su ancho; 0 si no hay. */
    private static final EntityDataAccessor<Float> DATA_HUECO =
            SynchedEntityData.defineId(OlaNereaEntity.class, EntityDataSerializers.FLOAT);
    private static final EntityDataAccessor<Float> DATA_HUECO_ANCHO =
            SynchedEntityData.defineId(OlaNereaEntity.class, EntityDataSerializers.FLOAT);

    private @Nullable NereaEntity duena;
    /** Solo la Gran Marea golpea (y mata, salvo totem); las del Rompeolas, no. */
    private float dano;
    private final Set<UUID> golpeados = new HashSet<>();

    public OlaNereaEntity(EntityType<? extends OlaNereaEntity> tipo, Level nivel) {
        super(tipo, nivel);
        this.noPhysics = true;
        setNoGravity(true);
    }

    /** Una ola del Rompeolas (solo se ve): sale de "desde" hacia "dir". */
    public static OlaNereaEntity ola(ServerLevel nivel, NereaEntity duena, Vec3 desde, Vec3 dir, float medioAncho, float alto,
                                     float vel, float largo) {
        OlaNereaEntity o = new OlaNereaEntity(AtalayaEntities.OLA_NEREA, nivel);
        o.duena = duena;
        o.entityData.set(DATA_ANCHO, medioAncho);
        o.entityData.set(DATA_ALTO, alto);
        o.entityData.set(DATA_VEL, vel);
        o.entityData.set(DATA_LARGO, largo);
        o.setYRot(rumbo(dir));
        o.setPos(desde.x, duena.getY(), desde.z);
        nivel.addFreshEntity(o);
        return o;
    }

    /** La Gran Marea: de lado a lado, con el hueco en "hueco" bloques a un lado. */
    public static OlaNereaEntity marea(ServerLevel nivel, NereaEntity duena, Vec3 desde, Vec3 dir, float hueco) {
        OlaNereaEntity o = ola(nivel, duena, desde, dir, NereaEntity.MAREA_ANCHO / 2.0F, NereaEntity.MAREA_ALTO,
                NereaEntity.MAREA_VEL, NereaEntity.MAREA_LARGO + NereaEntity.MAREA_ATRAS);
        o.dano = NereaEntity.MORTAL;
        o.entityData.set(DATA_HUECO, hueco);
        o.entityData.set(DATA_HUECO_ANCHO, NereaEntity.MAREA_HUECO);
        return o;
    }

    /** El rumbo (grados, como el de las entidades) que mira hacia dir. */
    public static float rumbo(Vec3 dir) {
        return (float) (Mth.atan2(-dir.x, dir.z) * Mth.RAD_TO_DEG);
    }

    /** Hacia donde avanza (horizontal, unitario). */
    public Vec3 dir() {
        float b = getYRot() * Mth.DEG_TO_RAD;
        return new Vec3(-Mth.sin(b), 0, Mth.cos(b));
    }

    /** A un lado del avance: la coordenada "lado" de la ola y del hueco. */
    public static Vec3 lado(Vec3 dir) {
        return new Vec3(-dir.z, 0, dir.x);
    }

    @Override
    protected void defineSynchedData(SynchedEntityData.Builder datos) {
        datos.define(DATA_ANCHO, 2.6F);
        datos.define(DATA_ALTO, 3.2F);
        datos.define(DATA_VEL, 1.0F);
        datos.define(DATA_LARGO, 30.0F);
        datos.define(DATA_HUECO, 0.0F);
        datos.define(DATA_HUECO_ANCHO, 0.0F);
    }

    public float getAncho() {
        return entityData.get(DATA_ANCHO);
    }

    public float getAlto() {
        return entityData.get(DATA_ALTO);
    }

    public float getLargo() {
        return entityData.get(DATA_LARGO);
    }

    public float getHueco() {
        return entityData.get(DATA_HUECO);
    }

    public float getHuecoAncho() {
        return entityData.get(DATA_HUECO_ANCHO);
    }

    public boolean esMarea() {
        return getHuecoAncho() > 0.0F;
    }

    /** Ticks que tarda en recorrer todo su camino. */
    public float viaje() {
        return getLargo() / Math.max(0.01F, entityData.get(DATA_VEL));
    }

    /** Donde va el frente (bloques desde donde nacio) a la edad dada. */
    public float frente(float edad) {
        return Math.min(getLargo(), edad * entityData.get(DATA_VEL));
    }

    @Override
    public void tick() {
        super.tick();
        float viaje = viaje();
        if (level().isClientSide()) {
            espuma(viaje);
            return;
        }
        if (duena == null || duena.isRemoved()) {
            discard();
            return;
        }
        if (dano > 0.0F && tickCount <= viaje + 1) {
            golpear((ServerLevel) level());
        }
        if (tickCount > viaje + APAGA) {
            discard();
        }
    }

    /** La espuma que salta de la cresta mientras avanza (solo en el cliente). */
    private void espuma(float viaje) {
        if (tickCount > viaje) {
            return;
        }
        Vec3 dir = dir();
        Vec3 lado = lado(dir);
        float f = frente(tickCount);
        float ancho = getAncho();
        float alto = getAlto();
        int n = esMarea() ? 10 : 3;
        for (int i = 0; i < n; i++) {
            double l = (random.nextDouble() * 2 - 1) * ancho;
            if (enHueco(l, 0.0)) {
                continue;
            }
            Vec3 p = position().add(dir.scale(f + 0.4)).add(lado.scale(l));
            level().addParticle(AtalayaParticulas.NEREA_ESPUMA, p.x, p.y + alto * (0.85 + random.nextDouble() * 0.2), p.z,
                    dir.x * 0.25, 0.05, dir.z * 0.25);
            if (random.nextInt(3) == 0) {
                level().addParticle(AtalayaParticulas.NEREA_GOTA, p.x, p.y + alto * 0.9, p.z, dir.x * 0.3, 0.2, dir.z * 0.3);
            }
        }
    }

    /** Si "l" (a un lado del avance) cae en el hueco, con medio ancho de margen. */
    public boolean enHueco(double l, double margen) {
        float h = getHuecoAncho();
        return h > 0.0F && Math.abs(l - getHueco()) < h / 2.0 - margen;
    }

    /**
     * La Gran Marea barre lo que pilla el frente este tick, una vez a cada uno:
     * el golpe (mortal: solo salva un totem, que se gasta) y el arrastre en su
     * sentido. Quien este en el hueco, o detras de ella, no se moja.
     */
    private void golpear(ServerLevel nivel) {
        Vec3 dir = dir();
        Vec3 lado = lado(dir);
        double antes = frente(tickCount - 1) - 1.0;
        double ahora = frente(tickCount) + 0.6;
        float ancho = getAncho();
        Vec3 o = position();
        AABB caja = new AABB(o, o.add(dir.scale(ahora))).inflate(ancho + 1, 0, ancho + 1).expandTowards(0, getAlto(), 0)
                .expandTowards(0, -2, 0);
        DamageSource fuente = NereaDanos.fuente(nivel, NereaDanos.MAREA, this, duena);
        for (LivingEntity v : nivel.getEntitiesOfClass(LivingEntity.class, caja, x -> duena != null && duena.esPresa(x))) {
            if (golpeados.contains(v.getUUID())) {
                continue;
            }
            Vec3 rel = v.position().subtract(o);
            double a = rel.x * dir.x + rel.z * dir.z;
            double l = rel.x * lado.x + rel.z * lado.z;
            double dy = v.getY() - o.y;
            if (a < antes || a > ahora || Math.abs(l) > ancho || dy < -2.0 || dy > getAlto()
                    || enHueco(l, v.getBbWidth() / 2.0)) {
                continue;
            }
            golpeados.add(v.getUUID());
            v.hurtServer(nivel, fuente, dano);
            v.setDeltaMovement(dir.x * 1.6, 0.7, dir.z * 1.6);
            v.hurtMarked = true;
            nivel.sendParticles(AtalayaParticulas.NEREA_ESPUMA, true, true, v.getX(), v.getY() + 1.0, v.getZ(), 12, 0.5, 0.6, 0.5, 0.1);
            nivel.sendParticles(AtalayaParticulas.NEREA_GOTA, true, true, v.getX(), v.getY() + 1.0, v.getZ(), 10, 0.4, 0.5, 0.4, 0.3);
        }
    }

    @Override
    public boolean isPickable() {
        return false;
    }

    @Override
    public boolean shouldBeSaved() {
        return false;
    }

    @Override
    public boolean shouldRenderAtSqrDistance(double distancia) {
        return distancia < 192 * 192;
    }

    @Override
    public boolean hurtServer(ServerLevel nivel, DamageSource fuente, float cantidad) {
        return false;
    }

    @Override
    protected void readAdditionalSaveData(ValueInput entrada) {
    }

    @Override
    protected void addAdditionalSaveData(ValueOutput salida) {
    }
}
