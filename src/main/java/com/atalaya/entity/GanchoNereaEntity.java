package com.atalaya.entity;

import com.atalaya.particula.AtalayaParticulas;
import com.atalaya.sonido.AtalayaSonidos;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.projectile.ThrowableProjectile;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.EntityHitResult;
import net.minecraft.world.phys.Vec3;
import org.jspecify.annotations.Nullable;

/**
 * El ancla del Arpon (desde el remake de octubre de 2026; antes, un garfio de
 * hueso): la del extremo de la cadena-latigo.
 *
 * Vuela hacia el jugador mas lejano, con una estela de espuma y burbujas, y
 * marca con un aro de espuma el suelo de a quien va. Desde el 09-10-2026 le
 * sigue (gira hasta GIRO por tick): antes volaba recto a donde estaba al
 * lanzarla y fallaba con solo moverse (Juan: "a veces falla"). Lo paran un
 * bloque en medio o un escudo. Si lo alcanza, Nerea decide
 * ({@link NereaEntity#alEngancharGancho}): un escudo la hace rebotar; si no,
 * se queda clavada y lo arrastra hasta la punta del tridente. La cadena que la
 * une a la mano la pinta su renderer.
 */
public class GanchoNereaEntity extends ThrowableProjectile {

    public static final float VELOCIDAD = 2.1F;
    private static final int VUELO = 40;
    /** Lo que puede girar por tick siguiendo a su blanco (radianes): unos 7 grados. */
    private static final double GIRO = Math.toRadians(7.0);

    /** A quien lleva enganchado (id de entidad), para que el cliente lo pinte encima. */
    private static final EntityDataAccessor<Integer> DATA_ENGANCHADO =
            SynchedEntityData.defineId(GanchoNereaEntity.class, EntityDataSerializers.INT);
    /** A quien va (id de entidad): el cliente le marca el suelo con un aro mientras vuela. */
    private static final EntityDataAccessor<Integer> DATA_BLANCO =
            SynchedEntityData.defineId(GanchoNereaEntity.class, EntityDataSerializers.INT);

    private @Nullable LivingEntity enganchado;

    public GanchoNereaEntity(EntityType<? extends GanchoNereaEntity> tipo, Level nivel) {
        super(tipo, nivel);
    }

    public static GanchoNereaEntity lanzar(ServerLevel nivel, NereaEntity nerea, Vec3 desde, LivingEntity blanco) {
        Vec3 hacia = blanco.getEyePosition().add(0, -0.4, 0);
        GanchoNereaEntity g = new GanchoNereaEntity(AtalayaEntities.GANCHO_NEREA, nivel);
        g.setOwner(nerea);
        g.entityData.set(DATA_BLANCO, blanco.getId());
        g.setPos(desde.x, desde.y, desde.z);
        Vec3 d = hacia.subtract(desde);
        g.shoot(d.x, d.y, d.z, VELOCIDAD, 0.0F);
        nivel.addFreshEntity(g);
        return g;
    }

    @Override
    protected void defineSynchedData(SynchedEntityData.Builder datos) {
        datos.define(DATA_ENGANCHADO, -1);
        datos.define(DATA_BLANCO, -1);
    }

    public int getIdEnganchado() {
        return entityData.get(DATA_ENGANCHADO);
    }

    public int getIdBlanco() {
        return entityData.get(DATA_BLANCO);
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
        if (enganchado != null || getIdEnganchado() >= 0) {
            // Clavado: va donde va su presa, sin volar por su cuenta.
            Entity presa = enganchado != null ? enganchado : level().getEntity(getIdEnganchado());
            if (presa != null) {
                setPos(presa.getX(), presa.getY() + presa.getBbHeight() * 0.55, presa.getZ());
                setDeltaMovement(Vec3.ZERO);
            }
            baseTick();
            if (!level().isClientSide() && (presa == null || !presa.isAlive() || tickCount > 120)) {
                discard();
            }
            return;
        }
        seguir();
        super.tick();
        if (level().isClientSide()) {
            // La estela: espuma y burbujas que deja el ancla por donde pasa.
            Vec3 v = getDeltaMovement();
            for (int i = 0; i < 3; i++) {
                double k = random.nextDouble();
                level().addParticle(i == 0 ? AtalayaParticulas.NEREA_ESPUMA : AtalayaParticulas.NEREA_BURBUJA,
                        getX() - v.x * k + random.nextGaussian() * 0.15, getY() - v.y * k + random.nextGaussian() * 0.15,
                        getZ() - v.z * k + random.nextGaussian() * 0.15, 0, 0.02, 0);
            }
        } else if (tickCount > VUELO) {
            fallar();
        }
    }

    /** Gira un poco hacia su blanco (en los dos lados, que saben a quien va). */
    private void seguir() {
        Entity b = level().getEntity(getIdBlanco());
        Vec3 v = getDeltaMovement();
        if (!(b instanceof LivingEntity blanco) || !blanco.isAlive() || v.lengthSqr() < 1.0E-6) {
            return;
        }
        Vec3 hacia = blanco.getEyePosition().add(0, -0.4, 0).subtract(position());
        if (hacia.lengthSqr() < 1.0E-4) {
            return;
        }
        Vec3 a = v.normalize();
        Vec3 d = hacia.normalize();
        double cos = Math.clamp(a.dot(d), -1.0, 1.0);
        Vec3 nueva;
        if (Math.acos(cos) <= GIRO) {
            nueva = d;
        } else {
            Vec3 perp = d.subtract(a.scale(cos));
            nueva = perp.lengthSqr() < 1.0E-8 ? a : a.scale(Math.cos(GIRO)).add(perp.normalize().scale(Math.sin(GIRO)));
        }
        setDeltaMovement(nueva.scale(VELOCIDAD));
    }

    @Override
    protected boolean canHitEntity(Entity e) {
        if (!(e instanceof LivingEntity) || e instanceof NereaEntity) {
            return false;
        }
        if (e instanceof Player p && (p.isSpectator() || p.isCreative())) {
            return false;
        }
        return super.canHitEntity(e);
    }

    @Override
    protected void onHitEntity(EntityHitResult golpe) {
        if (!(level() instanceof ServerLevel nivel) || !(golpe.getEntity() instanceof LivingEntity victima)) {
            return;
        }
        if (getOwner() instanceof NereaEntity nerea && nerea.alEngancharGancho(nivel, this, victima)) {
            enganchado = victima;
            entityData.set(DATA_ENGANCHADO, victima.getId());
            nivel.sendParticles(AtalayaParticulas.NEREA_CHISPA, getX(), getY(), getZ(), 8, 0.15, 0.15, 0.15, 0.2);
        } else {
            discard();
        }
    }

    @Override
    protected void onHitBlock(BlockHitResult golpe) {
        super.onHitBlock(golpe);
        if (level() instanceof ServerLevel nivel) {
            Vec3 p = golpe.getLocation();
            nivel.playSound(null, p.x, p.y, p.z, AtalayaSonidos.NEREA_ARPON_REBOTA, SoundSource.HOSTILE, 1.5F, 0.8F);
            nivel.sendParticles(AtalayaParticulas.NEREA_CHISPA, p.x, p.y, p.z, 8, 0.1, 0.1, 0.1, 0.2);
            fallar();
        }
    }

    private void fallar() {
        if (getOwner() instanceof NereaEntity nerea) {
            nerea.alFallarGancho(this);
        }
        discard();
    }
}
