package com.atalaya.entity;

import com.atalaya.particula.AtalayaParticulas;
import com.atalaya.sonido.AtalayaSonidos;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.Mth;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityDimensions;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.Pose;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.storage.ValueInput;
import net.minecraft.world.level.storage.ValueOutput;
import net.minecraft.world.phys.Vec3;
import org.jspecify.annotations.Nullable;

/**
 * Una losa de Suelo que se Hunde: 3 x 3 bloques de jade pulido con su filo de
 * oro, en alto sobre el foso de pinchos. Se pisa como el suelo (con su media
 * anchura por debajo de 2 bloques, vanilla la encuentra sola: no hace falta
 * ColisionGrande). Al pisarla (lo mira SueloRajang, jugador a jugador: con
 * cientos de losas, que cada una buscase quien la pisa era mucho) se agrieta y
 * al segundo cae (la luz de la maldicion sale por las grietas); no vuelve.
 * Debajo, en el suelo, sus pinchos de jade (LosaJadeRenderer). Sube del suelo
 * al empezar y, al acabar, se deshace.
 */
public class LosaJadeEntity extends Entity {

    public static final float LADO = 3.0F;
    public static final float GRUESO = 0.5F;
    /** Lo que tarda en subir, lo que aguanta pisada y lo que tarda en caer y deshacerse. */
    public static final int SUBE = 24;
    public static final int CRUJE = 20;
    public static final int CAE = 24;

    /** Tick (de la losa) en que empieza a subir. */
    private static final EntityDataAccessor<Integer> DATA_NACE =
            SynchedEntityData.defineId(LosaJadeEntity.class, EntityDataSerializers.INT);
    /** Tick en que la pisaron (-1: entera). */
    private static final EntityDataAccessor<Integer> DATA_PISADA =
            SynchedEntityData.defineId(LosaJadeEntity.class, EntityDataSerializers.INT);
    /** Tick en que empezo a caer (-1: en su sitio). */
    private static final EntityDataAccessor<Integer> DATA_CAE =
            SynchedEntityData.defineId(LosaJadeEntity.class, EntityDataSerializers.INT);
    /** Lo que hay de su cara de abajo al suelo (los pinchos van alli). */
    private static final EntityDataAccessor<Float> DATA_HONDO =
            SynchedEntityData.defineId(LosaJadeEntity.class, EntityDataSerializers.FLOAT);
    private static final EntityDataAccessor<Integer> DATA_SEMILLA =
            SynchedEntityData.defineId(LosaJadeEntity.class, EntityDataSerializers.INT);

    private @Nullable RajangEntity dueno;

    public LosaJadeEntity(EntityType<? extends LosaJadeEntity> tipo, Level nivel) {
        super(tipo, nivel);
        this.noPhysics = true;
        setNoGravity(true);
    }

    /** Una losa con su cara de arriba en 'arriba'; el suelo de debajo en 'suelo'. Sube a los 'retraso' ticks. */
    static LosaJadeEntity alzar(ServerLevel nivel, RajangEntity dueno, double x, double arriba, double z, double suelo, int retraso) {
        LosaJadeEntity l = new LosaJadeEntity(AtalayaEntities.LOSA_JADE, nivel);
        l.dueno = dueno;
        l.entityData.set(DATA_NACE, retraso);
        l.entityData.set(DATA_HONDO, (float) Math.max(0.5, arriba - GRUESO - suelo));
        l.entityData.set(DATA_SEMILLA, nivel.getRandom().nextInt());
        l.setPos(x, arriba - GRUESO, z);
        nivel.addFreshEntity(l);
        return l;
    }

    @Override
    protected void defineSynchedData(SynchedEntityData.Builder datos) {
        datos.define(DATA_NACE, 0);
        datos.define(DATA_PISADA, -1);
        datos.define(DATA_CAE, -1);
        datos.define(DATA_HONDO, 3.0F);
        datos.define(DATA_SEMILLA, 0);
    }

    public int getNace() {
        return entityData.get(DATA_NACE);
    }

    public int getPisada() {
        return entityData.get(DATA_PISADA);
    }

    public int getCae() {
        return entityData.get(DATA_CAE);
    }

    public float getHondo() {
        return entityData.get(DATA_HONDO);
    }

    public int getSemilla() {
        return entityData.get(DATA_SEMILLA);
    }

    /** Lo que ha subido (0 a 1). */
    public float subida(float parcial) {
        float k = Mth.clamp((tickCount - getNace() + parcial) / SUBE, 0.0F, 1.0F);
        return 1.0F - (1.0F - k) * (1.0F - k);
    }

    /** Arriba, entera o agrietada: se puede pisar. */
    public boolean firme() {
        return getCae() < 0 && tickCount >= getNace() + SUBE;
    }

    @Override
    public EntityDimensions getDimensions(Pose pose) {
        return EntityDimensions.fixed(LADO, GRUESO);
    }

    @Override
    public boolean canBeCollidedWith(@Nullable Entity otro) {
        return !isRemoved() && firme();
    }

    @Override
    public boolean canCollideWith(Entity otro) {
        return false;
    }

    @Override
    public void tick() {
        super.tick();
        if (level().isClientSide()) {
            int pisada = getPisada();
            if (pisada >= 0 && getCae() < 0 && random.nextInt(3) == 0) {
                // Se agrieta: polvo y la luz verde que se escapa.
                level().addParticle(AtalayaParticulas.RAJANG_POLVO, getX() + (random.nextDouble() - 0.5) * LADO, getY() + GRUESO,
                        getZ() + (random.nextDouble() - 0.5) * LADO, 0, 0.03, 0);
                if (tickCount - pisada > CRUJE / 2) {
                    level().addParticle(AtalayaParticulas.RAJANG_CHISPA, getX() + (random.nextDouble() - 0.5) * LADO, getY() + GRUESO,
                            getZ() + (random.nextDouble() - 0.5) * LADO, 0, 0.05, 0);
                }
            }
            return;
        }
        ServerLevel nivel = (ServerLevel) level();
        int cae = getCae();
        if (cae >= 0) {
            if (tickCount - cae > CAE) {
                discard();
            }
            return;
        }
        if (dueno == null || dueno.isRemoved()) {
            caer(nivel, false);
            return;
        }
        int pisada = getPisada();
        if (pisada >= 0 && tickCount - pisada >= CRUJE) {
            caer(nivel, true);
        }
    }

    /** Alguien la pisa: se agrieta (y al segundo cae). */
    void pisar(ServerLevel nivel) {
        if (getPisada() >= 0 || !firme()) {
            return;
        }
        entityData.set(DATA_PISADA, tickCount);
        nivel.playSound(null, getX(), getY() + GRUESO, getZ(), AtalayaSonidos.RAJANG_LOSA_CRUJE, SoundSource.HOSTILE, 1.2F,
                0.9F + random.nextFloat() * 0.2F);
    }

    /** Cae al foso (con ruido si es porque la pisaron; al acabar, en silencio, que son muchas). */
    void caer(ServerLevel nivel, boolean ruido) {
        if (getCae() >= 0) {
            return;
        }
        entityData.set(DATA_CAE, tickCount);
        if (ruido) {
            nivel.playSound(null, getX(), getY(), getZ(), AtalayaSonidos.RAJANG_LOSA_CAE, SoundSource.HOSTILE, 1.5F,
                    0.9F + random.nextFloat() * 0.2F);
            nivel.sendParticles(AtalayaParticulas.RAJANG_ROCA, true, true, getX(), getY(), getZ(), 8, 0.6, 0.2, 0.6, 0.1);
        }
        nivel.sendParticles(AtalayaParticulas.RAJANG_POLVO, true, true, getX(), getY() + GRUESO, getZ(), 6, 0.6, 0.1, 0.6, 0.02);
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

    /** El centro de su cara de arriba. */
    public Vec3 arriba() {
        return new Vec3(getX(), getY() + GRUESO, getZ());
    }
}
