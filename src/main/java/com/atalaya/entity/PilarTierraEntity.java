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
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Pose;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.storage.ValueInput;
import net.minecraft.world.level.storage.ValueOutput;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;
import org.jspecify.annotations.Nullable;

/**
 * Un grupo de pilares de roca del Terremoto Ancestral. Primero avisa: un
 * hexagono roto que brilla en el suelo un segundo (mas si sale tarde), y
 * luego revienta: la torre de roca en bloques, cada bloque algo torcido, con
 * su punta en esquirla y dos a cuatro menores alrededor (las dibuja
 * PilarTierraRenderer con su semilla). Golpea a quien este encima, lo lanza
 * unos diez bloques y le deja el Peso tres segundos; se queda cuatro segundos
 * y se hunde.
 */
public class PilarTierraEntity extends Entity {

    public static final int SUBE = 6;
    public static final int DURA = 90;
    public static final int BAJA = 20;
    /** Alto del pilar de tamano 1, en bloques. */
    public static final float ALTO = 5.4F;

    private static final EntityDataAccessor<Float> DATA_TAM =
            SynchedEntityData.defineId(PilarTierraEntity.class, EntityDataSerializers.FLOAT);
    private static final EntityDataAccessor<Integer> DATA_SEMILLA =
            SynchedEntityData.defineId(PilarTierraEntity.class, EntityDataSerializers.INT);
    /** Ticks de aviso antes de salir. */
    private static final EntityDataAccessor<Integer> DATA_AVISO =
            SynchedEntityData.defineId(PilarTierraEntity.class, EntityDataSerializers.INT);

    private @Nullable RajangEntity dueno;
    private float dano;

    public PilarTierraEntity(EntityType<? extends PilarTierraEntity> tipo, Level nivel) {
        super(tipo, nivel);
        this.noPhysics = true;
        setNoGravity(true);
    }

    /** Un pilar que saldra en 20 + retraso ticks. */
    public static PilarTierraEntity avisar(ServerLevel nivel, RajangEntity dueno, Vec3 donde, float tam, int retraso, float dano) {
        PilarTierraEntity p = new PilarTierraEntity(AtalayaEntities.PILAR_TIERRA, nivel);
        p.dueno = dueno;
        p.dano = dano;
        int aviso = 20 + retraso;
        p.entityData.set(DATA_TAM, tam);
        p.entityData.set(DATA_SEMILLA, nivel.getRandom().nextInt());
        p.entityData.set(DATA_AVISO, aviso);
        p.setYRot(nivel.getRandom().nextFloat() * 360.0F);
        p.setPos(donde.x, donde.y, donde.z);
        p.refreshDimensions();
        nivel.addFreshEntity(p);
        nivel.sendParticles(AtalayaParticulas.RAJANG_AVISO, true, true, donde.x, donde.y + 0.07, donde.z, 0,
                1.2 + 1.3 * tam, aviso + 2, 0.0, 1.0);
        nivel.playSound(null, donde.x, donde.y, donde.z, AtalayaSonidos.RAJANG_AVISO, SoundSource.HOSTILE, 1.6F, 0.9F + 0.2F * tam);
        return p;
    }

    @Override
    protected void defineSynchedData(SynchedEntityData.Builder datos) {
        datos.define(DATA_TAM, 1.0F);
        datos.define(DATA_SEMILLA, 0);
        datos.define(DATA_AVISO, 20);
    }

    public float getTam() {
        return entityData.get(DATA_TAM);
    }

    public int getSemilla() {
        return entityData.get(DATA_SEMILLA);
    }

    public int getAviso() {
        return entityData.get(DATA_AVISO);
    }

    @Override
    public void onSyncedDataUpdated(EntityDataAccessor<?> dato) {
        super.onSyncedDataUpdated(dato);
        if (DATA_TAM.equals(dato)) {
            refreshDimensions();
        }
    }

    @Override
    public EntityDimensions getDimensions(Pose pose) {
        float tam = getTam();
        return EntityDimensions.scalable(2.0F + 2.4F * tam, ALTO * tam);
    }

    @Override
    public void tick() {
        super.tick();
        int aviso = getAviso();
        float tam = getTam();
        if (level().isClientSide()) {
            if (tickCount < aviso && tickCount % 3 == 0) {
                // El suelo tiembla donde va a salir: polvo que salta.
                level().addParticle(AtalayaParticulas.RAJANG_POLVO, getX() + random.nextGaussian() * tam, getY() + 0.1,
                        getZ() + random.nextGaussian() * tam, 0, 0.04, 0);
            }
            if (tickCount >= aviso && tickCount < aviso + SUBE + 2) {
                for (int i = 0; i < 4; i++) {
                    level().addParticle(AtalayaParticulas.RAJANG_POLVO, getX() + random.nextGaussian() * tam * 1.5, getY() + 0.3,
                            getZ() + random.nextGaussian() * tam * 1.5, random.nextGaussian() * 0.08, 0.1, random.nextGaussian() * 0.08);
                }
            }
            return;
        }
        if (dueno == null || dueno.isRemoved()) {
            discard();
            return;
        }
        if (tickCount == aviso) {
            ServerLevel nivel = (ServerLevel) level();
            nivel.playSound(null, getX(), getY(), getZ(), AtalayaSonidos.RAJANG_PILAR, SoundSource.HOSTILE, 3.0F + 2.0F * tam,
                    1.1F - 0.25F * tam);
            nivel.sendParticles(AtalayaParticulas.RAJANG_ROCA, true, true, getX(), getY() + 1.0, getZ(), 16, 0.8, 0.5, 0.8, 0.3);
            nivel.sendParticles(AtalayaParticulas.RAJANG_POLVO, true, true, getX(), getY() + 0.5, getZ(), 20, 1.5, 0.5, 1.5, 0.06);
            nivel.sendParticles(AtalayaParticulas.RAJANG_ONDA, true, true, getX(), getY() + 0.1, getZ(), 0, 1.0 * tam, 5.0, 0.0, 1.0);
        }
        if (tickCount == aviso + 2) {
            golpear((ServerLevel) level(), tam);
        }
        if (tickCount >= aviso + DURA + BAJA) {
            discard();
        }
    }

    private void golpear(ServerLevel nivel, float tam) {
        double radio = 1.2 + 1.4 * tam;
        DamageSource fuente = RajangDanos.fuente(nivel, RajangDanos.TERREMOTO, this, dueno);
        AABB caja = new AABB(getX() - radio, getY() - 0.5, getZ() - radio, getX() + radio, getY() + ALTO * tam, getZ() + radio);
        for (LivingEntity v : nivel.getEntitiesOfClass(LivingEntity.class, caja, x -> dueno != null && dueno.esPresa(x))) {
            if (RajangEntity.horizontal(position(), v.position()) > radio) {
                continue;
            }
            v.hurtServer(nivel, fuente, RajangEntity.contraArmadura(v, dano));
            Vec3 fuera = RajangEntity.horizontalHacia(position(), v.position());
            // Unos diez bloques hacia arriba, y el Peso tres segundos.
            RajangEntity.lanzar(v, fuera.scale(0.5), PicoTierraEntity.LANZA);
            if (dueno != null) {
                dueno.lastrar(v, RajangEntity.PESO_PINCHO);
            }
        }
    }

    /** De 0 a 1 lo que ha salido (con rebote) y lo que se hunde al final; negativo: aun avisa. */
    public static float salida(float edad, int aviso) {
        float e = edad - aviso;
        if (e < 0) {
            return 0.0F;
        }
        if (e < SUBE) {
            float k = e / SUBE;
            return Mth.clamp(1.0F + 1.3F * (float) Math.pow(k - 1.0F, 3) + 0.35F * (float) Math.pow(k - 1.0F, 2), 0.0F, 1.06F);
        }
        if (e > DURA) {
            return Mth.clamp(1.0F - (e - DURA) / BAJA, 0.0F, 1.0F);
        }
        return 1.0F;
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
        return distancia < 160 * 160;
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
