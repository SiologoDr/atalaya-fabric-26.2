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

/**
 * El camino de llamas malditas de la Espada del Fuego (08-10-2026): la franja
 * por la que paso Novilis al embestir (40 bloques de largo y 8 de ancho) se
 * queda ardiendo. Prende de atras hacia delante al ritmo de su carrera, arde
 * diez segundos y se apaga. A quien este dentro y en el suelo: su fuego cada
 * medio segundo y un nivel de Quemadura cada dos.
 *
 * La entidad esta donde empieza el camino; el rumbo, el largo, el ancho y lo
 * que tarda en prender van sincronizados para que el cliente pinte la franja.
 */
public class CaminoLlamasEntity extends Entity {

    /** Lo que arde (ticks) y lo que tarda en apagarse al final. */
    public static final int DURA = 200;
    public static final int APAGA = 30;

    private static final EntityDataAccessor<Float> DATA_RUMBO =
            SynchedEntityData.defineId(CaminoLlamasEntity.class, EntityDataSerializers.FLOAT);
    private static final EntityDataAccessor<Float> DATA_LARGO =
            SynchedEntityData.defineId(CaminoLlamasEntity.class, EntityDataSerializers.FLOAT);
    private static final EntityDataAccessor<Float> DATA_ANCHO =
            SynchedEntityData.defineId(CaminoLlamasEntity.class, EntityDataSerializers.FLOAT);
    private static final EntityDataAccessor<Integer> DATA_PRENDE =
            SynchedEntityData.defineId(CaminoLlamasEntity.class, EntityDataSerializers.INT);
    /** Fase del dueno (el color del fuego); 5 la Furia. */
    private static final EntityDataAccessor<Integer> DATA_COLOR =
            SynchedEntityData.defineId(CaminoLlamasEntity.class, EntityDataSerializers.INT);

    private @Nullable NovilisEntity dueno;
    private float dano;

    public CaminoLlamasEntity(EntityType<? extends CaminoLlamasEntity> tipo, Level nivel) {
        super(tipo, nivel);
        this.noPhysics = true;
        setNoGravity(true);
    }

    public static CaminoLlamasEntity lanzar(ServerLevel nivel, NovilisEntity dueno, Vec3 desde, float rumbo, float largo,
                                            float ancho, int prende, float dano, int color) {
        CaminoLlamasEntity c = new CaminoLlamasEntity(AtalayaEntities.CAMINO_LLAMAS, nivel);
        c.dueno = dueno;
        c.dano = dano;
        c.entityData.set(DATA_RUMBO, rumbo);
        c.entityData.set(DATA_LARGO, largo);
        c.entityData.set(DATA_ANCHO, ancho);
        c.entityData.set(DATA_PRENDE, Math.max(1, prende));
        c.entityData.set(DATA_COLOR, color);
        c.setPos(desde.x, desde.y, desde.z);
        nivel.addFreshEntity(c);
        return c;
    }

    @Override
    protected void defineSynchedData(SynchedEntityData.Builder datos) {
        datos.define(DATA_RUMBO, 0.0F);
        datos.define(DATA_LARGO, 20.0F);
        datos.define(DATA_ANCHO, 4.0F);
        datos.define(DATA_PRENDE, 12);
        datos.define(DATA_COLOR, 1);
    }

    public float getRumbo() {
        return entityData.get(DATA_RUMBO);
    }

    public float getLargo() {
        return entityData.get(DATA_LARGO);
    }

    public float getAncho() {
        return entityData.get(DATA_ANCHO);
    }

    public int getColor() {
        return entityData.get(DATA_COLOR);
    }

    /** Hacia donde va el camino (horizontal). */
    public Vec3 frente() {
        float b = getRumbo() * Mth.DEG_TO_RAD;
        return new Vec3(-Mth.sin(b), 0, Mth.cos(b));
    }

    /** Lo que ya arde del camino (bloques desde el principio). */
    public float encendido(float edad) {
        return getLargo() * Mth.clamp(edad / entityData.get(DATA_PRENDE), 0.0F, 1.0F);
    }

    /** Lo fuerte que arde (0 a 1): baja al final. */
    public float fuerza(float edad) {
        return Mth.clamp((DURA - edad) / APAGA, 0.0F, 1.0F);
    }

    @Override
    public void tick() {
        super.tick();
        Vec3 f = frente();
        if (level().isClientSide()) {
            float k = fuerza(tickCount);
            float hasta = encendido(tickCount);
            if (k > 0.05F && random.nextFloat() < 0.8F * k) {
                double a = random.nextDouble() * hasta;
                double l = (random.nextDouble() - 0.5) * getAncho();
                Vec3 p = position().add(f.scale(a)).add(f.z * l, 0.15, -f.x * l);
                level().addParticle(random.nextInt(3) == 0 ? AtalayaParticulas.NOVILIS_BRASA : AtalayaParticulas.NOVILIS_LLAMA,
                        p.x, p.y, p.z, 0, 0.06 + random.nextDouble() * 0.05, 0);
            }
            return;
        }
        if (dueno == null || dueno.isRemoved() || tickCount >= DURA) {
            discard();
            return;
        }
        if (tickCount % 10 == 0 && fuerza(tickCount) > 0.3F) {
            quemar((ServerLevel) level(), f, encendido(tickCount), tickCount % 40 == 0);
        }
    }

    private void quemar(ServerLevel nivel, Vec3 f, float hasta, boolean marca) {
        Vec3 fin = position().add(f.scale(hasta));
        double m = getAncho() * 0.5 + 0.5;
        AABB caja = new AABB(position(), fin).inflate(m, 0.0, m).expandTowards(0, 2.5, 0).move(0, -0.5, 0);
        for (LivingEntity v : nivel.getEntitiesOfClass(LivingEntity.class, caja, x -> dueno != null && dueno.esPresa(x))) {
            Vec3 d = v.position().subtract(position());
            double largo = d.x * f.x + d.z * f.z;
            double lado = Math.abs(d.x * f.z - d.z * f.x);
            if (largo < -0.5 || largo > hasta + 0.5 || lado > getAncho() * 0.5 + v.getBbWidth() * 0.5 || d.y > 2.0 || d.y < -1.0) {
                continue;
            }
            if (dueno.quemar(nivel, v, NovilisDanos.LLAMAS, dano, marca ? 1 : 0, this)) {
                v.igniteForSeconds(2.0F);
            }
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
        return distancia < 160 * 160;
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
