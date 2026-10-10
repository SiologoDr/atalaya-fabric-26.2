package com.atalaya.entity;

import com.atalaya.particula.AtalayaParticulas;
import com.atalaya.sonido.AtalayaSonidos;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityDimensions;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.Pose;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.storage.ValueInput;
import net.minecraft.world.level.storage.ValueOutput;
import net.minecraft.world.phys.Vec3;
import org.jspecify.annotations.Nullable;

/**
 * Un circulo de los Pararrayos: marca en el suelo donde va a caer un rayo (el
 * sello de tormenta, con un aro de luz que se va cerrando hasta el aro de
 * dentro: entonces cae). Al acabar la cuenta cae el rayo del cielo y el juego
 * decide: si dentro hay alguien con un pararrayos en la mano, se lo lleva (queda
 * cargado); si no, revienta el suelo, que queda quemado un momento.
 */
public class CirculoRayoEntity extends Entity {

    public static final float RADIO = 2.2F;
    /** Lo que se queda el suelo quemado tras el rayo (y lo que dura el rayo, que cae del cielo). */
    public static final int QUEMADO = 40;
    public static final int RAYO = 8;

    /** Lo que tarda en caer el rayo (ticks desde que sale). */
    private static final EntityDataAccessor<Integer> DATA_CUENTA =
            SynchedEntityData.defineId(CirculoRayoEntity.class, EntityDataSerializers.INT);
    /** Tick en que cayo (-1: aun no). */
    private static final EntityDataAccessor<Integer> DATA_CAYO =
            SynchedEntityData.defineId(CirculoRayoEntity.class, EntityDataSerializers.INT);

    private @Nullable PararrayosAeralis juego;

    public CirculoRayoEntity(EntityType<? extends CirculoRayoEntity> tipo, Level nivel) {
        super(tipo, nivel);
        this.noPhysics = true;
        setNoGravity(true);
    }

    static CirculoRayoEntity poner(ServerLevel nivel, PararrayosAeralis juego, Vec3 donde, int cuenta) {
        CirculoRayoEntity c = new CirculoRayoEntity(AtalayaEntities.CIRCULO_RAYO, nivel);
        c.juego = juego;
        c.entityData.set(DATA_CUENTA, cuenta);
        c.snapTo(donde.x, donde.y, donde.z, nivel.getRandom().nextFloat() * 360.0F, 0.0F);
        nivel.addFreshEntity(c);
        return c;
    }

    @Override
    protected void defineSynchedData(SynchedEntityData.Builder datos) {
        datos.define(DATA_CUENTA, 60);
        datos.define(DATA_CAYO, -1);
    }

    public int getCuenta() {
        return entityData.get(DATA_CUENTA);
    }

    public int getCayo() {
        return entityData.get(DATA_CAYO);
    }

    /** Si p esta dentro (en horizontal y a poca altura). */
    boolean dentro(Entity p) {
        return Math.hypot(p.getX() - getX(), p.getZ() - getZ()) <= RADIO + p.getBbWidth() * 0.5 && Math.abs(p.getY() - getY()) < 3.0;
    }

    @Override
    public void tick() {
        super.tick();
        if (level().isClientSide()) {
            if (getCayo() < 0 && random.nextInt(3) == 0) {
                double a = random.nextDouble() * Math.PI * 2;
                double r = random.nextDouble() * RADIO;
                level().addParticle(AtalayaParticulas.AERALIS_RAYO, getX() + Math.cos(a) * r, getY() + 0.2 + random.nextDouble() * 1.5,
                        getZ() + Math.sin(a) * r, 0, 0, 0);
            }
            return;
        }
        ServerLevel nivel = (ServerLevel) level();
        if (juego == null) {
            discard();
            return;
        }
        if (tickCount == 1) {
            nivel.playSound(null, getX(), getY(), getZ(), AtalayaSonidos.AERALIS_PARARRAYOS_MARCA, SoundSource.HOSTILE, 1.6F,
                    0.9F + random.nextFloat() * 0.2F);
        }
        int cayo = getCayo();
        if (cayo < 0 && tickCount >= getCuenta()) {
            entityData.set(DATA_CAYO, tickCount);
            // El rayo: una columna desde el cielo.
            double x = getX();
            double z = getZ();
            for (int k = 0; k < 18; k++) {
                x += (random.nextDouble() - 0.5) * 0.8;
                z += (random.nextDouble() - 0.5) * 0.8;
                nivel.sendParticles(AtalayaParticulas.AERALIS_RAYO, true, true, x, getY() + k * 1.6, z, 1, 0.1, 0.3, 0.1, 0.0);
            }
            nivel.sendParticles(AtalayaParticulas.AERALIS_LUZ, true, true, getX(), getY() + 0.5, getZ(), 16, 0.6, 0.4, 0.6, 0.2);
            juego.alCaer(nivel, this);
        }
        if (cayo >= 0 && tickCount - cayo > QUEMADO) {
            discard();
        }
    }

    void soltar() {
        juego = null;
    }

    @Override
    public EntityDimensions getDimensions(Pose pose) {
        return EntityDimensions.fixed(0.5F, 0.2F);
    }

    @Override
    public boolean isPickable() {
        return false;
    }

    @Override
    public boolean isPushable() {
        return false;
    }

    @Override
    public boolean hurtServer(ServerLevel nivel, DamageSource fuente, float cantidad) {
        return false;
    }

    @Override
    public boolean shouldBeSaved() {
        return false;
    }

    @Override
    public boolean shouldRenderAtSqrDistance(double distancia) {
        return distancia < 128 * 128;
    }

    @Override
    protected void readAdditionalSaveData(ValueInput entrada) {
    }

    @Override
    protected void addAdditionalSaveData(ValueOutput salida) {
    }
}
