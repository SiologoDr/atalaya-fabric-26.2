package com.atalaya.entity;

import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityDimensions;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.Pose;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.storage.ValueInput;
import net.minecraft.world.level.storage.ValueOutput;
import org.jspecify.annotations.Nullable;

/**
 * Una caja de golpe de Rajang que no es la principal: la cabeza o la grupa.
 * Con 17 bloques de largo, una sola caja cuadrada o deja la cabeza fuera o le
 * ocupa media plaza. Esta va pegada a su sitio del cuerpo cada tick (la mueve
 * Rajang), no choca con nada, no se ve y todo el dano que recibe se lo pasa a
 * el. No se guarda con el mundo.
 */
public class RajangParteEntity extends Entity {

    private static final EntityDataAccessor<Float> DATA_ANCHO =
            SynchedEntityData.defineId(RajangParteEntity.class, EntityDataSerializers.FLOAT);
    private static final EntityDataAccessor<Float> DATA_ALTO =
            SynchedEntityData.defineId(RajangParteEntity.class, EntityDataSerializers.FLOAT);

    private @Nullable RajangEntity dueno;
    private String nombre = "";

    public RajangParteEntity(EntityType<? extends RajangParteEntity> tipo, Level nivel) {
        super(tipo, nivel);
        this.noPhysics = true;
        setNoGravity(true);
    }

    public static RajangParteEntity crear(ServerLevel nivel, RajangEntity dueno, String nombre, float ancho, float alto) {
        RajangParteEntity p = new RajangParteEntity(AtalayaEntities.RAJANG_PARTE, nivel);
        p.dueno = dueno;
        p.nombre = nombre;
        p.entityData.set(DATA_ANCHO, ancho);
        p.entityData.set(DATA_ALTO, alto);
        p.refreshDimensions();
        p.setPos(dueno.getX(), dueno.getY(), dueno.getZ());
        nivel.addFreshEntity(p);
        return p;
    }

    @Override
    protected void defineSynchedData(SynchedEntityData.Builder datos) {
        datos.define(DATA_ANCHO, 3.0F);
        datos.define(DATA_ALTO, 3.0F);
    }

    @Override
    public void onSyncedDataUpdated(EntityDataAccessor<?> dato) {
        super.onSyncedDataUpdated(dato);
        if (DATA_ANCHO.equals(dato) || DATA_ALTO.equals(dato)) {
            refreshDimensions();
        }
    }

    @Override
    public EntityDimensions getDimensions(Pose pose) {
        return EntityDimensions.scalable(entityData.get(DATA_ANCHO), entityData.get(DATA_ALTO));
    }

    public String getNombre() {
        return nombre;
    }

    /** Cambia lo que mide (solo si cambia: se manda al cliente). */
    public void medidas(float ancho, float alto) {
        if (entityData.get(DATA_ANCHO) != ancho || entityData.get(DATA_ALTO) != alto) {
            entityData.set(DATA_ANCHO, ancho);
            entityData.set(DATA_ALTO, alto);
            refreshDimensions();
        }
    }

    /** La pone en su sitio (los pies de la caja en y). */
    public void colocar(double x, double y, double z) {
        setPos(x, y, z);
    }

    @Override
    public void tick() {
        super.tick();
        if (!level().isClientSide() && (dueno == null || dueno.isRemoved())) {
            discard();
        }
    }

    @Override
    public boolean isPickable() {
        return dueno == null || !dueno.isRemoved();
    }

    @Override
    public boolean hurtServer(ServerLevel nivel, DamageSource fuente, float cantidad) {
        if (dueno == null || dueno.isRemoved() || isInvulnerableToBase(fuente)) {
            return false;
        }
        return dueno.hurtDesdeParte(nivel, this, fuente, cantidad);
    }

    @Override
    public boolean is(Entity otra) {
        return this == otra || dueno == otra;
    }

    @Override
    public boolean shouldBeSaved() {
        return false;
    }

    @Override
    public boolean canBeCollidedWith(@Nullable Entity otra) {
        return false;
    }

    @Override
    protected void readAdditionalSaveData(ValueInput entrada) {
    }

    @Override
    protected void addAdditionalSaveData(ValueOutput salida) {
    }
}
