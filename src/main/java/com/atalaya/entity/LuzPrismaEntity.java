package com.atalaya.entity;

import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.storage.ValueInput;
import net.minecraft.world.level.storage.ValueOutput;
import net.minecraft.world.phys.Vec3;
import org.jspecify.annotations.Nullable;

/**
 * El punto de luz del Prisma de Jade (El Rayo del Prisma de Rajang): va donde
 * mira quien mantiene el prisma, y Rajang salta sobre el. Lo mueve RajangEntity
 * cada tick; el cliente pinta el rayo desde la mano del que lo lleva y el
 * punto en el suelo (LuzPrismaRenderer). Apagado, no se ve.
 */
public class LuzPrismaEntity extends Entity {

    /** Quien lleva el prisma encendido (id de entidad, -1 apagado). */
    private static final EntityDataAccessor<Integer> DATA_DUENO =
            SynchedEntityData.defineId(LuzPrismaEntity.class, EntityDataSerializers.INT);

    private @Nullable RajangEntity rajang;

    public LuzPrismaEntity(EntityType<? extends LuzPrismaEntity> tipo, Level nivel) {
        super(tipo, nivel);
        this.noPhysics = true;
        setNoGravity(true);
    }

    static LuzPrismaEntity crear(ServerLevel nivel, RajangEntity r, Vec3 donde) {
        LuzPrismaEntity l = new LuzPrismaEntity(AtalayaEntities.LUZ_PRISMA, nivel);
        l.rajang = r;
        l.setPos(donde.x, donde.y, donde.z);
        nivel.addFreshEntity(l);
        return l;
    }

    @Override
    protected void defineSynchedData(SynchedEntityData.Builder datos) {
        datos.define(DATA_DUENO, -1);
    }

    /** Quien la proyecta (en el cliente tambien), o null si esta apagada. */
    public @Nullable Player dueno() {
        return level().getEntity(entityData.get(DATA_DUENO)) instanceof Player p ? p : null;
    }

    public boolean encendida() {
        return entityData.get(DATA_DUENO) >= 0;
    }

    void encender(@Nullable Player p, Vec3 donde) {
        int id = p == null ? -1 : p.getId();
        if (entityData.get(DATA_DUENO) != id) {
            entityData.set(DATA_DUENO, id);
        }
        if (p != null) {
            setPos(donde.x, donde.y, donde.z);
        }
    }

    @Override
    public void tick() {
        super.tick();
        if (!level().isClientSide() && (rajang == null || rajang.isRemoved() || rajang.minijuego() != MinijuegosRajang.PRISMA)) {
            discard();
        }
    }

    @Override
    public boolean isPickable() {
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
        return distancia < 160 * 160;
    }

    @Override
    protected void readAdditionalSaveData(ValueInput entrada) {
    }

    @Override
    protected void addAdditionalSaveData(ValueOutput salida) {
    }
}
