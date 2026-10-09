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
 * Un agujero de las Morenas de las Pozas (Nerea, octubre de 2026: el "golpea al
 * topo"). Nerea abre ocho alrededor y las morenas asoman de una en una (luego de
 * dos en dos), cada una un segundo. Un golpe de un jugador mientras asoma es un
 * acierto y la esconde; si se esconde sin que nadie le de, muerde al mas
 * cercano. No cura a Nerea: ningun jefe se cura (Juan, 09-10-2026).
 *
 * Como se ve (MorenaNereaRenderer, MorenaDibujo): el agua del agujero hierve y
 * la morena revienta hacia arriba; mientras esta fuera se mece, abre y cierra
 * la boca y mira al jugador mas cercano; en su ultimo tercio de segundo se echa
 * atras con la boca abierta (el aviso, con su siseo) y, si nadie le ha dado,
 * se lanza a morder con la segunda mandibula y se mete. Si le dan, se pone roja
 * como cualquier bicho, da un respingo y se mete enroscandose.
 */
public class MorenaNereaEntity extends Entity {

    public static final int OCULTA = 0;
    public static final int SUBE = 1;
    public static final int FUERA = 2;
    public static final int BAJA = 3;
    /** Lo que tarda en asomar y en esconderse (ticks). */
    public static final int T_SUBE = 6;
    public static final int T_BAJA = 9;
    /** Lo que dura el aviso antes de morder: se echa atras con la boca abierta (ticks). */
    public static final int T_AVISO = 6;
    /** Lo que muerde si se esconde sin que nadie le de (pasa la armadura). */
    public static final float[] DANO_MORDISCO = {8, 10, 12, 15};
    /** Hasta donde llega su mordisco. */
    private static final double ALCANCE = 5.5;

    private static final EntityDataAccessor<Integer> DATA_FASE =
            SynchedEntityData.defineId(MorenaNereaEntity.class, EntityDataSerializers.INT);
    /** El tick (del servidor, el mismo numero que tickCount del cliente mas o menos) en que empezo la fase. */
    private static final EntityDataAccessor<Integer> DATA_DESDE =
            SynchedEntityData.defineId(MorenaNereaEntity.class, EntityDataSerializers.INT);
    /** Si la ultima vez se escondio por un golpe (el cliente pinta el destello). */
    private static final EntityDataAccessor<Boolean> DATA_GOLPEADA =
            SynchedEntityData.defineId(MorenaNereaEntity.class, EntityDataSerializers.BOOLEAN);
    /** Lo que va a estar fuera esta vez (el cliente lo necesita para el aviso). */
    private static final EntityDataAccessor<Integer> DATA_DURA =
            SynchedEntityData.defineId(MorenaNereaEntity.class, EntityDataSerializers.INT);

    private @Nullable NereaEntity duena;
    private int reloj;
    private int fuera;
    private int cierra = -1;

    public MorenaNereaEntity(EntityType<? extends MorenaNereaEntity> tipo, Level nivel) {
        super(tipo, nivel);
        this.noPhysics = true;
        setNoGravity(true);
    }

    static MorenaNereaEntity abrir(ServerLevel nivel, NereaEntity duena, Vec3 donde, float rumbo) {
        MorenaNereaEntity m = new MorenaNereaEntity(AtalayaEntities.MORENA_NEREA, nivel);
        m.duena = duena;
        m.setYRot(rumbo);
        m.setPos(donde.x, donde.y, donde.z);
        nivel.addFreshEntity(m);
        return m;
    }

    @Override
    protected void defineSynchedData(SynchedEntityData.Builder datos) {
        datos.define(DATA_FASE, OCULTA);
        datos.define(DATA_DESDE, 0);
        datos.define(DATA_GOLPEADA, false);
        datos.define(DATA_DURA, 16);
    }

    public int getFase() {
        return entityData.get(DATA_FASE);
    }

    /** Ticks desde que empezo la fase (en el cliente, con el reloj del cliente). */
    public int desde() {
        return tickCount - entityData.get(DATA_DESDE);
    }

    public boolean golpeada() {
        return entityData.get(DATA_GOLPEADA);
    }

    /** Lo que esta fuera esta vez (ticks). */
    public int dura() {
        return entityData.get(DATA_DURA);
    }

    /** Si el agujero se esta cerrando (al acabar el minijuego). */
    public boolean cerrando() {
        return cierra >= 0;
    }

    public boolean oculta() {
        return getFase() == OCULTA;
    }

    private void fase(int f, int ticks) {
        entityData.set(DATA_FASE, f);
        entityData.set(DATA_DESDE, tickCount);
        reloj = ticks;
        if (f == BAJA && level() instanceof ServerLevel nivel) {
            nivel.playSound(null, getX(), getY() + 0.5, getZ(), AtalayaSonidos.NEREA_MORENA_BAJA, SoundSource.HOSTILE, 1.0F,
                    0.9F + random.nextFloat() * 0.2F);
        }
    }

    /** Asoma durante "ticks" ticks (si esta escondida). */
    void asomar(int ticks) {
        if (getFase() != OCULTA || cierra >= 0) {
            return;
        }
        fuera = ticks;
        entityData.set(DATA_GOLPEADA, false);
        entityData.set(DATA_DURA, ticks);
        fase(SUBE, T_SUBE);
        if (level() instanceof ServerLevel nivel) {
            nivel.playSound(null, getX(), getY(), getZ(), AtalayaSonidos.NEREA_MORENA_SALE, SoundSource.HOSTILE, 1.3F,
                    0.9F + random.nextFloat() * 0.2F);
        }
    }

    void cerrar() {
        if (cierra < 0) {
            cierra = tickCount;
            if (getFase() == SUBE || getFase() == FUERA) {
                fase(BAJA, T_BAJA);
            }
        }
    }

    @Override
    public void tick() {
        super.tick();
        if (level().isClientSide()) {
            int f = getFase();
            int d = desde();
            if (f == SUBE && d < 2) {
                // Hierve el agua justo antes de que reviente.
                for (int i = 0; i < 3; i++) {
                    level().addParticle(AtalayaParticulas.NEREA_BURBUJA, getX() + (random.nextDouble() - 0.5) * 0.9, getY() + 0.1,
                            getZ() + (random.nextDouble() - 0.5) * 0.9, 0, 0.08, 0);
                }
            } else if (f == SUBE && d == 2) {
                // La corona de agua al salir.
                for (int i = 0; i < 14; i++) {
                    double a = i / 14.0 * Math.PI * 2;
                    level().addParticle(AtalayaParticulas.NEREA_GOTA, getX() + Math.cos(a) * 0.5, getY() + 0.2,
                            getZ() + Math.sin(a) * 0.5, Math.cos(a) * 0.12, 0.25, Math.sin(a) * 0.12);
                }
                level().addParticle(AtalayaParticulas.NEREA_ESPUMA, getX(), getY() + 0.3, getZ(), 0, 0.05, 0);
            } else if (f == FUERA && random.nextInt(3) == 0) {
                level().addParticle(AtalayaParticulas.NEREA_GOTA, getX() + (random.nextDouble() - 0.5) * 0.5, getY() + 1.6,
                        getZ() + (random.nextDouble() - 0.5) * 0.5, 0, 0, 0);
            } else if (f == BAJA && d == 4) {
                for (int i = 0; i < 8; i++) {
                    level().addParticle(AtalayaParticulas.NEREA_GOTA, getX() + (random.nextDouble() - 0.5) * 0.8, getY() + 0.2,
                            getZ() + (random.nextDouble() - 0.5) * 0.8, 0, 0.15, 0);
                }
            }
            return;
        }
        ServerLevel nivel = (ServerLevel) level();
        if (duena == null || duena.isRemoved() || (cierra >= 0 && tickCount - cierra > T_BAJA + 4)) {
            discard();
            return;
        }
        if (getFase() == FUERA && reloj == T_AVISO + 1) {
            // El aviso: se echa atras y sisea.
            nivel.playSound(null, getX(), getY() + 1.5, getZ(), AtalayaSonidos.NEREA_MORENA_AVISO, SoundSource.HOSTILE, 1.2F,
                    0.9F + random.nextFloat() * 0.2F);
        }
        if (getFase() == OCULTA || --reloj > 0) {
            return;
        }
        switch (getFase()) {
            case SUBE -> fase(FUERA, fuera);
            case FUERA -> {
                // Nadie le ha dado: muerde al mas cercano y se esconde.
                morder(nivel);
                fase(BAJA, T_BAJA);
            }
            case BAJA -> fase(OCULTA, 0);
            default -> {
            }
        }
    }

    private void morder(ServerLevel nivel) {
        NereaEntity n = duena;
        if (n == null) {
            return;
        }
        LivingEntity mejor = null;
        double d = ALCANCE * ALCANCE;
        for (LivingEntity v : nivel.getEntitiesOfClass(LivingEntity.class, getBoundingBox().inflate(ALCANCE), n::esPresa)) {
            double dd = v.distanceToSqr(this);
            if (dd < d) {
                d = dd;
                mejor = v;
            }
        }
        nivel.playSound(null, getX(), getY() + 1.5, getZ(), AtalayaSonidos.NEREA_MORENA_MORDISCO, SoundSource.HOSTILE, 1.5F, 1.0F);
        if (mejor != null) {
            mejor.hurtServer(nivel, NereaDanos.fuente(nivel, NereaDanos.MORENA, this, n), n.dano(DANO_MORDISCO));
            nivel.sendParticles(AtalayaParticulas.NEREA_GOTA, true, true, mejor.getX(), mejor.getY() + 1.0, mejor.getZ(), 10, 0.3, 0.4,
                    0.3, 0.2);
        }
    }

    @Override
    public boolean isPickable() {
        int f = getFase();
        return (f == SUBE || f == FUERA) && cierra < 0;
    }

    @Override
    public boolean hurtServer(ServerLevel nivel, DamageSource fuente, float cantidad) {
        int f = getFase();
        if ((f != SUBE && f != FUERA) || cierra >= 0 || !(fuente.getEntity() instanceof Player)) {
            return false;
        }
        entityData.set(DATA_GOLPEADA, true);
        fase(BAJA, T_BAJA);
        nivel.playSound(null, getX(), getY() + 1.5, getZ(), AtalayaSonidos.NEREA_MORENA_GOLPE, SoundSource.HOSTILE, 1.6F,
                0.9F + random.nextFloat() * 0.2F);
        nivel.sendParticles(AtalayaParticulas.NEREA_CHISPA, true, true, getX(), getY() + 1.8, getZ(), 10, 0.3, 0.3, 0.3, 0.2);
        if (duena != null) {
            duena.alAcertarMorena(nivel);
        }
        return true;
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
