package com.atalaya.entity;

import com.atalaya.particula.AtalayaParticulas;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.util.Mth;
import net.minecraft.world.damagesource.DamageSource;
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
 * Una media luna de fuego del Barrido de Novilis: sale del filo y vuela recta
 * a ras de suelo. A quien pilla: el golpe, fuego 4 s y un nivel de quemadura.
 *
 * Como las olas de Nerea, la entidad se queda donde nacio: lo lejos que va se
 * calcula con la edad en los dos lados, asi que no hace falta mandar su
 * posicion tick a tick.
 */
public class TajoNovilisEntity extends net.minecraft.world.entity.Entity {

    /** Lo que avanza por tick. */
    public static final float VEL = 1.1F;
    /** Ticks que vuela (unos 29 bloques). */
    public static final int VUELO = 26;
    /** Medio ancho de la media luna y su alto. */
    public static final float MEDIO_ANCHO = 2.4F;
    public static final float ALTO = 2.6F;

    private static final EntityDataAccessor<Integer> DATA_FASE =
            SynchedEntityData.defineId(TajoNovilisEntity.class, EntityDataSerializers.INT);
    /** La del tajo de arriba: mas grande. */
    private static final EntityDataAccessor<Boolean> DATA_GRANDE =
            SynchedEntityData.defineId(TajoNovilisEntity.class, EntityDataSerializers.BOOLEAN);
    private static final EntityDataAccessor<Boolean> DATA_FURIA =
            SynchedEntityData.defineId(TajoNovilisEntity.class, EntityDataSerializers.BOOLEAN);

    private @Nullable NovilisEntity dueno;
    private float dano;
    private final Set<UUID> golpeados = new HashSet<>();

    public TajoNovilisEntity(EntityType<? extends TajoNovilisEntity> tipo, Level nivel) {
        super(tipo, nivel);
        this.noPhysics = true;
        setNoGravity(true);
    }

    public static TajoNovilisEntity lanzar(ServerLevel nivel, NovilisEntity dueno, Vec3 desde, Vec3 dir, float dano, int fase,
                                           boolean grande) {
        TajoNovilisEntity t = new TajoNovilisEntity(AtalayaEntities.TAJO_NOVILIS, nivel);
        t.dueno = dueno;
        t.dano = dano;
        t.entityData.set(DATA_FASE, fase);
        t.entityData.set(DATA_GRANDE, grande);
        t.entityData.set(DATA_FURIA, dueno.tieneFuria());
        t.setYRot((float) (Mth.atan2(-dir.x, dir.z) * Mth.RAD_TO_DEG));
        t.setPos(desde.x, desde.y, desde.z);
        nivel.addFreshEntity(t);
        return t;
    }

    @Override
    protected void defineSynchedData(SynchedEntityData.Builder datos) {
        datos.define(DATA_FASE, 1);
        datos.define(DATA_GRANDE, false);
        datos.define(DATA_FURIA, false);
    }

    public int getFase() {
        return entityData.get(DATA_FASE);
    }

    public boolean esGrande() {
        return entityData.get(DATA_GRANDE);
    }

    public boolean esFuria() {
        return entityData.get(DATA_FURIA);
    }

    public Vec3 dir() {
        float b = getYRot() * Mth.DEG_TO_RAD;
        return new Vec3(-Mth.sin(b), 0, Mth.cos(b));
    }

    /** Lo que ha avanzado desde donde nacio, a la edad dada (ticks). */
    public float avance(float edad) {
        return Math.min(VEL * VUELO, edad * VEL);
    }

    @Override
    public void tick() {
        super.tick();
        Vec3 p = position().add(dir().scale(avance(tickCount)));
        if (level().isClientSide()) {
            if (tickCount <= VUELO) {
                for (int i = 0; i < 3; i++) {
                    double l = (random.nextDouble() * 2 - 1) * MEDIO_ANCHO;
                    Vec3 lado = new Vec3(-dir().z, 0, dir().x);
                    level().addParticle(random.nextBoolean() ? AtalayaParticulas.NOVILIS_LLAMA : AtalayaParticulas.NOVILIS_BRASA,
                            p.x + lado.x * l, p.y + random.nextDouble() * ALTO * 0.6, p.z + lado.z * l, 0, 0.05, 0);
                }
            }
            return;
        }
        if (dueno == null || dueno.isRemoved()) {
            discard();
            return;
        }
        if (tickCount <= VUELO) {
            golpear((ServerLevel) level(), p);
        }
        if (tickCount > VUELO + 4) {
            discard();
        }
    }

    private void golpear(ServerLevel nivel, Vec3 p) {
        float ancho = esGrande() ? MEDIO_ANCHO * 1.5F : MEDIO_ANCHO;
        AABB caja = new AABB(p, p).inflate(ancho + 0.5, 0, ancho + 0.5).expandTowards(0, ALTO + 0.5, 0).expandTowards(0, -1.5, 0);
        for (LivingEntity v : nivel.getEntitiesOfClass(LivingEntity.class, caja, x -> dueno != null && dueno.esPresa(x))) {
            if (golpeados.contains(v.getUUID())) {
                continue;
            }
            Vec3 rel = v.position().subtract(p);
            double l = rel.x * -dir().z + rel.z * dir().x;
            double a = rel.x * dir().x + rel.z * dir().z;
            if (Math.abs(l) > ancho + v.getBbWidth() / 2 || Math.abs(a) > 1.4) {
                continue;
            }
            golpeados.add(v.getUUID());
            if (dueno.quemar(nivel, v, NovilisDanos.TAJO, dano, 1, this)) {
                v.igniteForSeconds(4.0F);
                v.setDeltaMovement(dir().x * 0.9, 0.35, dir().z * 0.9);
                v.hurtMarked = true;
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
