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
 * La Chispa de Aeralis: una estrella de rayos que flota sobre quien la lleva,
 * con la cuenta atras encima. La mueve ChispaAeralis (sobre la cabeza del que la
 * lleva o volando de uno a otro); aqui solo esta lo que el cliente necesita
 * para dibujarla.
 */
public class ChispaAeralisEntity extends Entity {

    /** Quien la lleva (id de entidad; -1: vuela o no hay nadie). */
    private static final EntityDataAccessor<Integer> DATA_PORTADOR =
            SynchedEntityData.defineId(ChispaAeralisEntity.class, EntityDataSerializers.INT);
    /** Cuando revienta (tiempo del mundo; 0: no cuenta). */
    private static final EntityDataAccessor<Long> DATA_FIN =
            SynchedEntityData.defineId(ChispaAeralisEntity.class, EntityDataSerializers.LONG);
    private static final EntityDataAccessor<Boolean> DATA_CARGADA =
            SynchedEntityData.defineId(ChispaAeralisEntity.class, EntityDataSerializers.BOOLEAN);

    private @Nullable ChispaAeralis juego;

    public ChispaAeralisEntity(EntityType<? extends ChispaAeralisEntity> tipo, Level nivel) {
        super(tipo, nivel);
        this.noPhysics = true;
        setNoGravity(true);
    }

    static ChispaAeralisEntity crear(ServerLevel nivel, ChispaAeralis juego, double x, double y, double z) {
        ChispaAeralisEntity c = new ChispaAeralisEntity(AtalayaEntities.CHISPA_AERALIS, nivel);
        c.juego = juego;
        c.snapTo(x, y, z, 0.0F, 0.0F);
        nivel.addFreshEntity(c);
        return c;
    }

    @Override
    protected void defineSynchedData(SynchedEntityData.Builder datos) {
        datos.define(DATA_PORTADOR, -1);
        datos.define(DATA_FIN, 0L);
        datos.define(DATA_CARGADA, false);
    }

    public int getPortador() {
        return entityData.get(DATA_PORTADOR);
    }

    public long getFin() {
        return entityData.get(DATA_FIN);
    }

    public boolean cargada() {
        return entityData.get(DATA_CARGADA);
    }

    void ponerPortador(@Nullable Entity e, long fin) {
        entityData.set(DATA_PORTADOR, e == null ? -1 : e.getId());
        entityData.set(DATA_FIN, fin);
    }

    void cargar(boolean si) {
        entityData.set(DATA_CARGADA, si);
    }

    void soltar() {
        juego = null;
    }

    @Override
    public void tick() {
        super.tick();
        if (!level().isClientSide() && juego == null) {
            discard();
        }
    }

    @Override
    public EntityDimensions getDimensions(Pose pose) {
        return EntityDimensions.fixed(0.6F, 0.6F);
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
