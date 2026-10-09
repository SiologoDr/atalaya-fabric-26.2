package com.atalaya.entity;

import com.atalaya.particula.AtalayaParticulas;
import com.atalaya.particula.ParticulaSiguiente;
import com.atalaya.sonido.AtalayaSonidos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.projectile.ThrowableProjectile;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.EntityHitResult;
import net.minecraft.world.phys.Vec3;
import org.jspecify.annotations.Nullable;

/**
 * La bala de un Canon del Naufragio: una bola de hierro negra que vuela en arco
 * con su estela de humo. Solo le da a Nerea (pasa por los jugadores); si cae al
 * suelo o se pierde, rompe la racha de aciertos.
 */
public class BalaCanonEntity extends ThrowableProjectile {

    /** Lo bastante lenta para verla volar hasta Nerea (Juan: "debe verse cuando va hacia Nerea"). */
    public static final float VELOCIDAD = 1.7F;
    public static final double GRAVEDAD = 0.02;

    private @Nullable NereaEntity duena;
    private boolean contada;

    public BalaCanonEntity(EntityType<? extends BalaCanonEntity> tipo, Level nivel) {
        super(tipo, nivel);
    }

    static void disparar(ServerLevel nivel, @Nullable NereaEntity duena, Vec3 desde, Vec3 dir) {
        BalaCanonEntity b = new BalaCanonEntity(AtalayaEntities.BALA_CANON, nivel);
        b.duena = duena;
        b.setPos(desde.x, desde.y, desde.z);
        b.shoot(dir.x, dir.y, dir.z, VELOCIDAD, 0.0F);
        nivel.addFreshEntity(b);
    }

    @Override
    protected void defineSynchedData(net.minecraft.network.syncher.SynchedEntityData.Builder datos) {
    }

    @Override
    protected double getDefaultGravity() {
        return GRAVEDAD;
    }

    @Override
    public void tick() {
        super.tick();
        if (level().isClientSide()) {
            // La estela de humo de polvora, entre donde estaba y donde esta.
            Vec3 v = getDeltaMovement();
            for (int i = 0; i < 2; i++) {
                double k = i * 0.5;
                ParticulaSiguiente.escala = 0.55F;
                level().addParticle(AtalayaParticulas.NEREA_HUMO, getX() - v.x * k, getY() + 0.1 - v.y * k, getZ() - v.z * k, 0, 0.01, 0);
            }
            return;
        }
        if (tickCount > 100) {
            fallar((ServerLevel) level());
        }
    }

    @Override
    protected boolean canHitEntity(Entity e) {
        return e instanceof NereaEntity;
    }

    @Override
    protected void onHitEntity(EntityHitResult golpe) {
        if (!(level() instanceof ServerLevel nivel) || contada) {
            return;
        }
        contada = true;
        Vec3 p = position();
        nivel.sendParticles(AtalayaParticulas.NEREA_FOGONAZO, true, true, p.x, p.y, p.z, 6, 0.6, 0.6, 0.6, 0.1);
        nivel.sendParticles(AtalayaParticulas.NEREA_HUMO, true, true, p.x, p.y, p.z, 20, 0.7, 0.7, 0.7, 0.06);
        nivel.sendParticles(AtalayaParticulas.NEREA_ROCA, true, true, p.x, p.y, p.z, 14, 0.4, 0.4, 0.4, 0.3);
        nivel.playSound(null, p.x, p.y, p.z, AtalayaSonidos.NEREA_BALA_IMPACTO, SoundSource.HOSTILE, 4.0F, 1.0F);
        if (duena != null && golpe.getEntity() == duena) {
            duena.alImpactoCanon(nivel, p);
        }
        discard();
    }

    @Override
    protected void onHitBlock(BlockHitResult golpe) {
        super.onHitBlock(golpe);
        if (level() instanceof ServerLevel nivel) {
            Vec3 p = golpe.getLocation();
            nivel.sendParticles(AtalayaParticulas.NEREA_POLVO, true, true, p.x, p.y + 0.3, p.z, 14, 0.5, 0.2, 0.5, 0.05);
            nivel.sendParticles(AtalayaParticulas.NEREA_HUMO, true, true, p.x, p.y + 0.3, p.z, 6, 0.3, 0.2, 0.3, 0.03);
            nivel.playSound(null, p.x, p.y, p.z, AtalayaSonidos.NEREA_BALA_CAE, SoundSource.PLAYERS, 2.0F, 1.0F);
            fallar(nivel);
        }
    }

    private void fallar(ServerLevel nivel) {
        if (!contada) {
            contada = true;
            if (duena != null) {
                duena.alFallarCanon(nivel);
            }
        }
        discard();
    }

    @Override
    public boolean shouldBeSaved() {
        return false;
    }
}
