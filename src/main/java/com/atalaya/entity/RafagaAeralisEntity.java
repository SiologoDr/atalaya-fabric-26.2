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
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.projectile.ThrowableProjectile;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.EntityHitResult;
import net.minecraft.world.phys.Vec3;
import org.jspecify.annotations.Nullable;

/**
 * Una rafaga de La Caceria del Vendaval: una bola de viento en espiral que
 * persigue a la presa marcada. Es lenta a proposito (unos 8 bloques por
 * segundo, 11 si la presa se ha alejado del grupo): los demas tienen tiempo de
 * reventarla en el aire a golpes o a flechazos. Aguanta un golpe, y uno mas por
 * cada 12 jugadores.
 *
 * Si llega, revienta en una explosion de presion (AeralisEntity.DANO_RAFAGA) en
 * 3,5 bloques y un empujon. Ponerse delante tambien la para... y te la comes tu.
 */
public class RafagaAeralisEntity extends ThrowableProjectile {

    private static final double VELOCIDAD = 0.42;
    private static final double GIRO = 0.08;
    private static final int VIDA = 180;
    private static final double RADIO = 3.5;

    private @Nullable LivingEntity blanco;
    private int fase = 2;
    private boolean acelerada;
    private int aguanta = 1;
    private int golpes;
    private float dano = AeralisEntity.DANO_RAFAGA[0];

    private static final EntityDataAccessor<Integer> DATA_FASE =
            SynchedEntityData.defineId(RafagaAeralisEntity.class, EntityDataSerializers.INT);

    public RafagaAeralisEntity(EntityType<? extends RafagaAeralisEntity> tipo, Level nivel) {
        super(tipo, nivel);
    }

    public static RafagaAeralisEntity lanzar(ServerLevel nivel, AeralisEntity duena, Vec3 desde, LivingEntity blanco,
                                             int fase, boolean acelerada, int aguanta, float dano) {
        RafagaAeralisEntity r = new RafagaAeralisEntity(AtalayaEntities.RAFAGA_AERALIS, nivel);
        r.setOwner(duena);
        r.blanco = blanco;
        r.fase = fase;
        r.entityData.set(DATA_FASE, fase);
        r.acelerada = acelerada;
        r.aguanta = aguanta;
        r.dano = dano;
        r.setPos(desde.x, desde.y, desde.z);
        Vec3 hacia = blanco.getEyePosition().subtract(desde);
        r.setDeltaMovement(hacia.lengthSqr() > 1.0E-4 ? hacia.normalize().scale(VELOCIDAD * 0.7) : Vec3.ZERO);
        nivel.addFreshEntity(r);
        return r;
    }

    @Override
    protected void defineSynchedData(SynchedEntityData.Builder datos) {
        datos.define(DATA_FASE, 1);
    }

    public int getFase() {
        return entityData.get(DATA_FASE);
    }

    @Override
    protected double getDefaultGravity() {
        return 0.0;
    }

    @Override
    protected float getAirDrag() {
        return 1.0F;
    }

    @Override
    public void tick() {
        super.tick();
        if (level().isClientSide()) {
            level().addParticle(AtalayaParticulas.AERALIS_JIRON, getX() + (random.nextDouble() - 0.5) * 0.8,
                    getY() + 0.4 + (random.nextDouble() - 0.5) * 0.8, getZ() + (random.nextDouble() - 0.5) * 0.8,
                    0, 0, 0);
            if (random.nextInt(2) == 0) {
                double a = tickCount * 0.6;
                level().addParticle(AtalayaParticulas.AERALIS_VIENTO, getX() + Math.cos(a) * 0.9, getY() + 0.4,
                        getZ() + Math.sin(a) * 0.9, -Math.sin(a) * 0.2, 0, Math.cos(a) * 0.2);
            }
            return;
        }
        if (tickCount > VIDA) {
            pinchar((ServerLevel) level());
            return;
        }
        Vec3 v = getDeltaMovement();
        double vel = VELOCIDAD * (1.0 + 0.08 * (fase - 2)) * (acelerada ? 1.35 : 1.0);
        if (blanco != null && blanco.isAlive()) {
            Vec3 hacia = blanco.position().add(0, blanco.getBbHeight() * 0.5, 0).subtract(position());
            if (hacia.lengthSqr() > 1.0E-3) {
                v = v.scale(1.0 - GIRO).add(hacia.normalize().scale(vel * GIRO));
            }
        }
        double l = v.length();
        if (l > 1.0E-4) {
            v = v.scale(Math.min(vel, Math.max(l, vel * 0.7)) / l);
        }
        setDeltaMovement(v);
    }

    @Override
    protected boolean canHitEntity(Entity e) {
        if (e instanceof AeralisEntity || e instanceof RafagaAeralisEntity || e instanceof TornadoAeralisEntity
                || e instanceof NucleoVientoEntity || e instanceof CuchillaVientoEntity) {
            return false;
        }
        if (e instanceof Player p && (p.isSpectator() || p.isCreative())) {
            return false;
        }
        return super.canHitEntity(e);
    }

    @Override
    protected void onHitEntity(EntityHitResult golpe) {
        if (level() instanceof ServerLevel nivel) {
            reventar(nivel);
        }
    }

    @Override
    protected void onHitBlock(BlockHitResult golpe) {
        super.onHitBlock(golpe);
        if (level() instanceof ServerLevel nivel) {
            reventar(nivel);
        }
    }

    /** Los golpes y los proyectiles la revientan; para eso tiene que poder recibirlos. */
    @Override
    public boolean isPickable() {
        return true;
    }

    @Override
    public boolean hurtServer(ServerLevel nivel, DamageSource fuente, float cantidad) {
        if (isRemoved() || fuente.getEntity() instanceof AeralisEntity) {
            return false;
        }
        golpes++;
        nivel.sendParticles(AtalayaParticulas.AERALIS_JIRON, true, true, getX(), getY() + 0.4, getZ(), 6, 0.3, 0.3, 0.3, 0.1);
        if (golpes >= aguanta) {
            pinchar(nivel);
        } else {
            nivel.playSound(null, getX(), getY(), getZ(), AtalayaSonidos.AERALIS_INMUNE, SoundSource.HOSTILE, 1.2F, 1.3F);
        }
        return true;
    }

    /** Reventada en el aire: se deshace sin dano. */
    private void pinchar(ServerLevel nivel) {
        nivel.playSound(null, getX(), getY(), getZ(), AtalayaSonidos.AERALIS_RAFAGA_ROMPE, SoundSource.HOSTILE, 2.0F, 1.0F);
        nivel.sendParticles(AtalayaParticulas.AERALIS_JIRON, true, true, getX(), getY() + 0.4, getZ(), 14, 0.5, 0.5, 0.5, 0.12);
        nivel.sendParticles(AtalayaParticulas.AERALIS_LUZ, true, true, getX(), getY() + 0.4, getZ(), 8, 0.4, 0.4, 0.4, 0.15);
        discard();
    }

    private void reventar(ServerLevel nivel) {
        if (isRemoved()) {
            return;
        }
        Vec3 c = position().add(0, 0.4, 0);
        nivel.playSound(null, c.x, c.y, c.z, AtalayaSonidos.AERALIS_RAFAGA_GOLPE, SoundSource.HOSTILE, 3.0F, 1.0F);
        nivel.sendParticles(AtalayaParticulas.AERALIS_ONDA, true, true, c.x, c.y, c.z, 0, 1.4, RADIO + 1.5, 0.0, 1.0);
        nivel.sendParticles(AtalayaParticulas.AERALIS_JIRON, true, true, c.x, c.y, c.z, 24, 0.8, 0.8, 0.8, 0.2);
        nivel.sendParticles(AtalayaParticulas.AERALIS_POLVO, true, true, c.x, c.y, c.z, 10, 1.0, 0.4, 1.0, 0.06);
        Entity duena = getOwner();
        DamageSource fuente = AeralisDanos.fuente(nivel, AeralisDanos.RAFAGA, this, duena);
        for (LivingEntity v : nivel.getEntitiesOfClass(LivingEntity.class, new AABB(c, c).inflate(RADIO))) {
            if (!PresasJefe.presa(v) || v.distanceToSqr(c) > RADIO * RADIO) {
                continue;
            }
            v.hurtServer(nivel, fuente, AeralisEntity.contraArmadura(v, dano));
            Vec3 fuera = AeralisEntity.horizontalHacia(c, v.position());
            v.setDeltaMovement(fuera.x * 1.2, 0.5, fuera.z * 1.2);
            v.hurtMarked = true;
        }
        discard();
    }
}
