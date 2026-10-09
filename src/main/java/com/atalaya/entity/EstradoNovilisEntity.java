package com.atalaya.entity;

import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.util.Mth;
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
 * Un escalon del estrado de un angel de las Trompetas: una losa de marmol con
 * filo de oro que se pisa como el suelo (es una entidad con su caja de choque,
 * como las piedras del Sello de Rajang). Cada angel esta sobre cinco, de uno a
 * cinco bloques de alto y cada uno mas estrecho (EstatuaNovilisEntity.ESTRADO_ANCHOS):
 * hay que subirlos todos para pegarle, y cada 5 s su pulso de fuego baja por
 * todos y expulsa dos o tres bloques a quien este subiendo (salvo que salte a tiempo).
 *
 * Sale del suelo a la vez que el angel y se va con el al acabar la melodia. No
 * se guarda con el mundo.
 */
public class EstradoNovilisEntity extends Entity {

    private static final EntityDataAccessor<Float> DATA_ANCHO =
            SynchedEntityData.defineId(EstradoNovilisEntity.class, EntityDataSerializers.FLOAT);
    private static final EntityDataAccessor<Float> DATA_ALTO =
            SynchedEntityData.defineId(EstradoNovilisEntity.class, EntityDataSerializers.FLOAT);

    private @Nullable EstatuaNovilisEntity estatua;
    private float altoVisto = -1.0F;

    public EstradoNovilisEntity(EntityType<? extends EstradoNovilisEntity> tipo, Level nivel) {
        super(tipo, nivel);
        this.noPhysics = true;
        setNoGravity(true);
    }

    public static EstradoNovilisEntity alzar(ServerLevel nivel, EstatuaNovilisEntity estatua, Vec3 donde, float ancho,
                                             float alto) {
        EstradoNovilisEntity e = new EstradoNovilisEntity(AtalayaEntities.ESTRADO_NOVILIS, nivel);
        e.estatua = estatua;
        e.entityData.set(DATA_ANCHO, ancho);
        e.entityData.set(DATA_ALTO, alto);
        e.setYRot(estatua.getYRot());
        e.setPos(donde.x, donde.y, donde.z);
        e.refreshDimensions();
        nivel.addFreshEntity(e);
        return e;
    }

    @Override
    protected void defineSynchedData(SynchedEntityData.Builder datos) {
        datos.define(DATA_ANCHO, 1.0F);
        datos.define(DATA_ALTO, 1.0F);
    }

    public float getAncho() {
        return entityData.get(DATA_ANCHO);
    }

    public float getAlto() {
        return entityData.get(DATA_ALTO);
    }

    /** Lo que ha salido del suelo, de 0 a 1 (sube con el angel). */
    public float salida(float parcial) {
        return Mth.clamp((tickCount + parcial) / EstatuaNovilisEntity.SALE, 0.0F, 1.0F);
    }

    @Override
    public void onSyncedDataUpdated(EntityDataAccessor<?> dato) {
        super.onSyncedDataUpdated(dato);
        if (DATA_ANCHO.equals(dato) || DATA_ALTO.equals(dato)) {
            refreshDimensions();
        }
    }

    /** La caja crece con lo que ha subido: quien estuviera en su sitio sube con ella. */
    @Override
    public EntityDimensions getDimensions(Pose pose) {
        return EntityDimensions.fixed(getAncho(), Math.max(0.01F, getAlto() * salida(0.0F)));
    }

    @Override
    public boolean canBeCollidedWith(@Nullable Entity otro) {
        return !isRemoved() && salida(0.0F) > 0.05F;
    }

    @Override
    public boolean canCollideWith(Entity otro) {
        return false;
    }

    @Override
    public void tick() {
        super.tick();
        // Grande y se pisa: que se encuentre al buscar con que se choca (ColisionGrande).
        ColisionGrande.apuntar(this);
        float alto = getAlto() * salida(0.0F);
        if (Math.abs(alto - altoVisto) > 1.0E-3F) {
            altoVisto = alto;
            refreshDimensions();
        }
        if (!level().isClientSide() && (estatua == null || estatua.isRemoved())) {
            discard();
        }
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
        return distancia < 192 * 192;
    }

    @Override
    protected void readAdditionalSaveData(ValueInput entrada) {
    }

    @Override
    protected void addAdditionalSaveData(ValueOutput salida) {
    }
}
