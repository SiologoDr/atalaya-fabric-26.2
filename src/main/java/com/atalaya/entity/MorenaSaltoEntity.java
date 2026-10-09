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
import net.minecraft.world.level.Level;
import net.minecraft.world.level.storage.ValueInput;
import net.minecraft.world.level.storage.ValueOutput;
import net.minecraft.world.phys.Vec3;
import org.jspecify.annotations.Nullable;

/**
 * La morena que salta de una poza de la Pesca del Abismo cuando el pescador
 * recoge antes de que pique (Juan: "deberia salir algo que te haga el dano").
 * Asoma, salta en arco hasta el pescador y le muerde; luego cae y se deshace en
 * agua. Se dibuja con MorenaDibujo, como las de los agujeros.
 */
public class MorenaSaltoEntity extends Entity {

    /** Lo que tarda en asomar, en llegar de un salto y en caer y deshacerse (ticks). */
    public static final int T_ASOMA = 5;
    public static final int T_SALTO = 8;
    public static final int T_CAE = 12;
    /** Lo mas lejos que llega de un salto (bloques): mas alla, se queda corta. */
    public static final double ALCANCE = 14.0;

    private static final EntityDataAccessor<Integer> DATA_PRESA =
            SynchedEntityData.defineId(MorenaSaltoEntity.class, EntityDataSerializers.INT);

    private @Nullable NereaEntity duena;
    private float dano;

    public MorenaSaltoEntity(EntityType<? extends MorenaSaltoEntity> tipo, Level nivel) {
        super(tipo, nivel);
        this.noPhysics = true;
        setNoGravity(true);
    }

    static void saltar(ServerLevel nivel, NereaEntity duena, Vec3 donde, Player presa, float dano) {
        MorenaSaltoEntity m = new MorenaSaltoEntity(AtalayaEntities.MORENA_SALTO, nivel);
        m.duena = duena;
        m.dano = dano;
        m.entityData.set(DATA_PRESA, presa.getId());
        m.setPos(donde.x, donde.y, donde.z);
        nivel.addFreshEntity(m);
        nivel.playSound(null, donde.x, donde.y, donde.z, AtalayaSonidos.NEREA_MORENA_SALE, SoundSource.HOSTILE, 1.6F, 1.0F);
        nivel.sendParticles(AtalayaParticulas.NEREA_GOTA, true, true, donde.x, donde.y + 0.3, donde.z, 16, 0.4, 0.2, 0.4, 0.25);
        nivel.sendParticles(AtalayaParticulas.NEREA_ESPUMA, true, true, donde.x, donde.y + 0.2, donde.z, 6, 0.4, 0.1, 0.4, 0.05);
    }

    @Override
    protected void defineSynchedData(SynchedEntityData.Builder datos) {
        datos.define(DATA_PRESA, -1);
    }

    /** El pescador al que salta (en el cliente tambien). */
    public @Nullable LivingEntity presa() {
        return level().getEntity(entityData.get(DATA_PRESA)) instanceof LivingEntity v ? v : null;
    }

    /** Donde muerde: el pecho de la presa, sin pasar del alcance. */
    public Vec3 destino(float parcial) {
        LivingEntity v = presa();
        Vec3 o = position();
        if (v == null) {
            return o.add(0, 1.0, 0);
        }
        Vec3 d = v.getPosition(parcial).add(0, v.getBbHeight() * 0.45, 0).subtract(o);
        double largo = Math.sqrt(d.x * d.x + d.z * d.z);
        // Se queda delante, a la altura del pecho: muerde sin meterse en la cara de quien mira.
        double hasta = Math.min(ALCANCE, Math.max(0.0, largo - 1.6));
        if (largo > 1.0E-3) {
            d = new Vec3(d.x * hasta / largo, d.y, d.z * hasta / largo);
        }
        return o.add(d);
    }

    @Override
    public void tick() {
        super.tick();
        int t = tickCount;
        if (level().isClientSide()) {
            if (t == T_ASOMA + T_SALTO + T_CAE - 3) {
                // Se deshace en agua donde cae.
                Vec3 c = destino(0.0F);
                for (int i = 0; i < 18; i++) {
                    level().addParticle(AtalayaParticulas.NEREA_GOTA, c.x + (random.nextDouble() - 0.5), c.y - 0.6,
                            c.z + (random.nextDouble() - 0.5), 0, 0.05, 0);
                }
            }
            return;
        }
        ServerLevel nivel = (ServerLevel) level();
        if (t == T_ASOMA + T_SALTO) {
            morder(nivel);
        }
        if (t > T_ASOMA + T_SALTO + T_CAE || duena == null || duena.isRemoved()) {
            discard();
        }
    }

    private void morder(ServerLevel nivel) {
        LivingEntity v = presa();
        NereaEntity n = duena;
        if (v == null || n == null || !v.isAlive()) {
            return;
        }
        Vec3 c = destino(0.0F);
        nivel.playSound(null, c.x, c.y, c.z, AtalayaSonidos.NEREA_MORENA_MORDISCO, SoundSource.HOSTILE, 1.6F, 1.0F);
        if (v.position().add(0, v.getBbHeight() * 0.45, 0).distanceTo(c) < 2.8) {
            v.hurtServer(nivel, NereaDanos.fuente(nivel, NereaDanos.MORENA, this, n), dano);
            nivel.sendParticles(AtalayaParticulas.NEREA_GOTA, true, true, c.x, c.y, c.z, 12, 0.3, 0.3, 0.3, 0.2);
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
        return distancia < 128 * 128;
    }

    @Override
    protected void readAdditionalSaveData(ValueInput entrada) {
    }

    @Override
    protected void addAdditionalSaveData(ValueOutput salida) {
    }
}
