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
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.storage.ValueInput;
import net.minecraft.world.level.storage.ValueOutput;
import net.minecraft.world.phys.Vec3;

/**
 * Una Perla del Abismo lanzada (la Pesca del Abismo de Nerea): vuela, con su
 * estela de luz, derecha al corazon de Nerea, que se ve dentro de su pecho. Al
 * llegar cuenta una perla; con las que hacen falta, el corazon se le apaga.
 */
public class PerlaLanzadaEntity extends Entity {

    private static final double VELOCIDAD = 1.3;

    private static final EntityDataAccessor<Integer> DATA_NEREA =
            SynchedEntityData.defineId(PerlaLanzadaEntity.class, EntityDataSerializers.INT);

    public PerlaLanzadaEntity(EntityType<? extends PerlaLanzadaEntity> tipo, Level nivel) {
        super(tipo, nivel);
        this.noPhysics = true;
        setNoGravity(true);
    }

    static void lanzar(ServerLevel nivel, Player p, NereaEntity n) {
        PerlaLanzadaEntity e = new PerlaLanzadaEntity(AtalayaEntities.PERLA_LANZADA, nivel);
        e.entityData.set(DATA_NEREA, n.getId());
        Vec3 ojo = p.getEyePosition().add(p.getLookAngle().scale(0.5)).add(0, -0.2, 0);
        e.setPos(ojo.x, ojo.y, ojo.z);
        nivel.addFreshEntity(e);
        nivel.playSound(null, p.getX(), p.getEyeY(), p.getZ(), AtalayaSonidos.NEREA_PERLA_LANZAR, SoundSource.PLAYERS, 1.2F, 1.0F);
    }

    @Override
    protected void defineSynchedData(SynchedEntityData.Builder datos) {
        datos.define(DATA_NEREA, -1);
    }

    @Override
    public void tick() {
        super.tick();
        if (level().isClientSide()) {
            level().addParticle(AtalayaParticulas.NEREA_BURBUJA, getX(), getY(), getZ(), 0, 0.01, 0);
            return;
        }
        ServerLevel nivel = (ServerLevel) level();
        if (!(nivel.getEntity(entityData.get(DATA_NEREA)) instanceof NereaEntity n) || n.isRemoved() || tickCount > 80) {
            discard();
            return;
        }
        Vec3 corazon = n.puntoMundo(NereaGeometria.CORAZON);
        Vec3 d = corazon.subtract(position());
        double largo = d.length();
        if (largo < VELOCIDAD + 0.3) {
            n.alRecibirPerla(nivel);
            nivel.sendParticles(AtalayaParticulas.NEREA_CORAZON, true, true, corazon.x, corazon.y, corazon.z, 20, 0.5, 0.5, 0.5, 0.2);
            nivel.playSound(null, corazon.x, corazon.y, corazon.z, AtalayaSonidos.NEREA_PERLA_CORAZON, SoundSource.HOSTILE, 3.0F, 1.0F);
            discard();
            return;
        }
        Vec3 paso = d.scale(VELOCIDAD / largo);
        setPos(getX() + paso.x, getY() + paso.y, getZ() + paso.z);
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
        return distancia < 128 * 128;
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
