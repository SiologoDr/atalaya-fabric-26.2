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
import net.minecraft.world.entity.projectile.Projectile;
import net.minecraft.world.entity.projectile.ThrowableProjectile;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.EntityHitResult;
import net.minecraft.world.phys.Vec3;
import org.jspecify.annotations.Nullable;

/**
 * Burbuja bomba: la escupe el corazon de Nerea de golpe y sale disparada
 * hacia un jugador, corrigiendo el rumbo sobre la marcha. A veinte bloques
 * llega en unos dos segundos: hay que reaccionar, no esperarla.
 *
 * Revienta al tocar un bloque o a alguien: 8 de dano en 4 bloques y una onda
 * que empuja. La salida es reventarla ANTES, desde lejos: una flecha, un
 * tridente o una bola de nieve la pinchan sin dano para nadie. Si la revientas
 * de un espadazo, en cambio, te explota en la cara.
 *
 * Desde el remake lleva el corazon maldito dentro y marca en el suelo, con un
 * aro de espuma, hasta donde llega su reventon (BurbujaNereaRenderer).
 */
public class BurbujaNereaEntity extends ThrowableProjectile {

    /** Bloques por tick una vez lanzada (fase I): unos diez por segundo. Sube con la fase. */
    private static final double VELOCIDAD = 0.5;
    /** Lo que corrige el rumbo cada tick: persigue, pero un quiebro tardio la esquiva. */
    private static final double GIRO = 0.09;
    private static final int VIDA = 120;
    private static final double RADIO = 5.5;
    /** La fase del jefe al soltarla: mas rapida y mas grande cuanto mas avanzada. El cliente la usa para el aro. */
    private static final EntityDataAccessor<Integer> DATA_FASE =
            SynchedEntityData.defineId(BurbujaNereaEntity.class, EntityDataSerializers.INT);
    /** Lo que quita al reventar (el de la fase, y mas con la Furia). */
    private float dano;

    private @Nullable LivingEntity blanco;

    public BurbujaNereaEntity(EntityType<? extends BurbujaNereaEntity> tipo, Level nivel) {
        super(tipo, nivel);
    }

    public static BurbujaNereaEntity lanzar(ServerLevel nivel, NereaEntity nerea, Vec3 desde, Vec3 frente,
                                            @Nullable LivingEntity blanco, int fase, float dano) {
        BurbujaNereaEntity b = new BurbujaNereaEntity(AtalayaEntities.BURBUJA_NEREA, nivel);
        b.setOwner(nerea);
        b.blanco = blanco;
        b.entityData.set(DATA_FASE, fase);
        b.dano = dano;
        b.setPos(desde.x, desde.y, desde.z);
        // Sale disparada hacia delante y abriendose en abanico: no en fila.
        Vec3 v = frente.scale(0.6).add((nivel.getRandom().nextDouble() - 0.5) * 0.35, 0.08,
                (nivel.getRandom().nextDouble() - 0.5) * 0.35);
        b.setDeltaMovement(v);
        nivel.addFreshEntity(b);
        return b;
    }

    @Override
    protected void defineSynchedData(SynchedEntityData.Builder datos) {
        datos.define(DATA_FASE, 1);
    }

    public int getFase() {
        return entityData.get(DATA_FASE);
    }

    /** Hasta donde llega el reventon en la fase dada (bloques). */
    public static double radio(int fase) {
        return RADIO + 0.75 * (Math.clamp(fase, 1, 4) - 1);
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
            if (random.nextInt(4) == 0) {
                level().addParticle(AtalayaParticulas.NEREA_BURBUJA, getX() + (random.nextDouble() - 0.5) * 0.6,
                        getY() + random.nextDouble() * 0.6, getZ() + (random.nextDouble() - 0.5) * 0.6, 0, 0.02, 0);
            }
            return;
        }
        if (tickCount > VIDA) {
            pinchar((ServerLevel) level());
            return;
        }
        // Persigue a su blanco cabeceando como lo que va por el agua.
        Vec3 v = getDeltaMovement();
        if (blanco != null && blanco.isAlive()) {
            Vec3 hacia = blanco.position().add(0, blanco.getBbHeight() * 0.5, 0).subtract(position());
            if (hacia.lengthSqr() > 1.0E-3) {
                v = v.scale(1.0 - GIRO).add(hacia.normalize().scale(VELOCIDAD * GIRO));
            }
        }
        double vel = VELOCIDAD * (1.0 + 0.1 * (getFase() - 1));
        double l = v.length();
        if (l > 1.0E-4) {
            v = v.scale(Math.min(vel, Math.max(l, vel * 0.6)) / l);
        }
        v = v.add(0, Math.sin(tickCount * 0.5) * 0.01, 0);
        setDeltaMovement(v);
    }

    @Override
    protected boolean canHitEntity(Entity e) {
        if (e instanceof NereaEntity || e instanceof BurbujaNereaEntity || e instanceof GanchoNereaEntity) {
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

    /** Las flechas y demas proyectiles la pinchan; para eso tiene que poder recibirlos. */
    @Override
    public boolean isPickable() {
        return true;
    }

    @Override
    public boolean hurtServer(ServerLevel nivel, DamageSource fuente, float cantidad) {
        if (isRemoved()) {
            return false;
        }
        if (fuente.getDirectEntity() instanceof Projectile) {
            pinchar(nivel);
        } else {
            reventar(nivel);
        }
        return true;
    }

    /** Pinchada desde lejos: se deshace sin hacer dano. */
    private void pinchar(ServerLevel nivel) {
        nivel.playSound(null, getX(), getY(), getZ(), AtalayaSonidos.NEREA_BURBUJA_POMPA, SoundSource.HOSTILE, 1.5F, 1.0F);
        nivel.sendParticles(AtalayaParticulas.NEREA_BURBUJA, getX(), getY() + 0.3, getZ(), 10, 0.3, 0.3, 0.3, 0.05);
        nivel.sendParticles(AtalayaParticulas.NEREA_GOTA, getX(), getY() + 0.3, getZ(), 8, 0.3, 0.3, 0.3, 0.15);
        discard();
    }

    private void reventar(ServerLevel nivel) {
        if (isRemoved()) {
            return;
        }
        Vec3 c = position().add(0, 0.45, 0);
        double radio = radio(getFase());
        nivel.playSound(null, c.x, c.y, c.z, AtalayaSonidos.NEREA_BURBUJA_REVIENTA, SoundSource.HOSTILE, 2.5F, 1.0F);
        nivel.sendParticles(AtalayaParticulas.NEREA_ONDA, c.x, getY() + 0.1, c.z, 0, 1.6, radio, 0.0, 1.0);
        nivel.sendParticles(AtalayaParticulas.NEREA_ESPUMA, c.x, c.y, c.z, 30, 1.0, 0.7, 1.0, 0.1);
        nivel.sendParticles(AtalayaParticulas.NEREA_GOTA, c.x, c.y, c.z, 30, 0.6, 0.5, 0.6, 0.4);
        nivel.sendParticles(AtalayaParticulas.NEREA_CORAZON, c.x, c.y, c.z, 6, 0.4, 0.4, 0.4, 0.1);
        Entity duena = getOwner();
        DamageSource fuente = NereaDanos.fuente(nivel, NereaDanos.BURBUJA, this, duena);
        for (LivingEntity v : nivel.getEntitiesOfClass(LivingEntity.class, new AABB(c, c).inflate(radio))) {
            if (!PresasJefe.presa(v) || v.distanceToSqr(c) > radio * radio) {
                continue;
            }
            v.hurtServer(nivel, fuente, dano);
            Vec3 fuera = v.position().subtract(c);
            Vec3 h = new Vec3(fuera.x, 0, fuera.z);
            h = h.lengthSqr() < 1.0E-4 ? new Vec3(0, 0, 0) : h.normalize();
            v.setDeltaMovement(h.x * 1.1, 0.45, h.z * 1.1);
            v.hurtMarked = true;
        }
        discard();
    }
}
