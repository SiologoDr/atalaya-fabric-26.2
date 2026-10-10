package com.atalaya.entity;

import com.atalaya.particula.AtalayaParticulas;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.EntityDimensions;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.Pose;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.storage.ValueInput;
import net.minecraft.world.level.storage.ValueOutput;
import net.minecraft.world.phys.Vec3;
import org.jspecify.annotations.Nullable;

/**
 * Un remolino de La Chispa, jugando solo: un torbellino pequeno que gira quieto
 * a tu alrededor. Pasarle la chispa (pegarle) cuenta como un pase, y te la
 * devuelve al momento. No hace dano; es todo viento (particulas).
 */
public class RemolinoChispaEntity extends net.minecraft.world.entity.Entity {

    private @Nullable ChispaAeralis juego;

    public RemolinoChispaEntity(EntityType<? extends RemolinoChispaEntity> tipo, Level nivel) {
        super(tipo, nivel);
        this.noPhysics = true;
        setNoGravity(true);
    }

    static RemolinoChispaEntity crear(ServerLevel nivel, ChispaAeralis juego, Vec3 donde) {
        RemolinoChispaEntity r = new RemolinoChispaEntity(AtalayaEntities.REMOLINO_CHISPA, nivel);
        r.juego = juego;
        r.snapTo(donde.x, donde.y, donde.z, 0.0F, 0.0F);
        nivel.addFreshEntity(r);
        nivel.sendParticles(AtalayaParticulas.AERALIS_POLVO, true, true, donde.x, donde.y + 0.3, donde.z, 10, 0.5, 0.2, 0.5, 0.04);
        return r;
    }

    @Override
    protected void defineSynchedData(net.minecraft.network.syncher.SynchedEntityData.Builder datos) {
    }

    void soltar() {
        juego = null;
    }

    @Override
    public void tick() {
        super.tick();
        if (level().isClientSide()) {
            // El torbellino: motas de viento que suben girando.
            for (int i = 0; i < 2; i++) {
                double a = tickCount * 0.5 + i * Math.PI;
                double h = (tickCount * 0.12 + i * 1.1) % 2.4;
                double r = 0.35 + h * 0.25;
                level().addParticle(AtalayaParticulas.AERALIS_REMOLINO, getX() + Math.cos(a) * r, getY() + h, getZ() + Math.sin(a) * r,
                        0, 0.02, 0);
            }
            return;
        }
        if (juego == null) {
            discard();
        }
    }

    @Override
    public EntityDimensions getDimensions(Pose pose) {
        return EntityDimensions.fixed(1.0F, 2.4F);
    }

    @Override
    public boolean isPickable() {
        return !isRemoved();
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
    protected void readAdditionalSaveData(ValueInput entrada) {
    }

    @Override
    protected void addAdditionalSaveData(ValueOutput salida) {
    }
}
