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
 * Un golpe de pinchos de roca de la Garra Terrestre: revienta el suelo en un
 * abrir y cerrar de ojos, se queda unos segundos clavado y se hunde. El
 * pincho grande, en bloques que se estrechan, va inclinado hacia donde corre
 * la grieta; alrededor, otros menores abiertos y los terrones del suelo roto
 * (los dibuja PicoTierraRenderer con su semilla).
 *
 * Al salir golpea a quien este encima, lo lanza unos diez bloques hacia arriba
 * y le deja el Peso de la Tierra tres segundos. El ultimo de la fila, el mayor
 * (6 bloques), sale dentro del aro que avisaba.
 *
 * Los de la Embestida son mortales (como un fragmento del Cataclismo encima:
 * solo salva un totem) y lanzan unos quince bloques; las vetas les brillan mas.
 * Los de la Tumba de Raices son solo de adorno: el dano ya lo ha hecho ella.
 */
public class PicoTierraEntity extends Entity {

    /** Ticks que tarda en salir, que se queda y que tarda en hundirse. */
    public static final int SUBE = 5;
    public static final int DURA = 70;
    public static final int BAJA = 16;
    /** Alto del pico de tamano 1, en bloques. */
    public static final float ALTO = 6.0F;
    /** Lo que lanza un pico normal: unos diez bloques hacia arriba. */
    public static final double LANZA = 1.36;

    private static final EntityDataAccessor<Float> DATA_TAM =
            SynchedEntityData.defineId(PicoTierraEntity.class, EntityDataSerializers.FLOAT);
    private static final EntityDataAccessor<Integer> DATA_SEMILLA =
            SynchedEntityData.defineId(PicoTierraEntity.class, EntityDataSerializers.INT);
    /** Uno de la Embestida: mata (salvo totem). */
    private static final EntityDataAccessor<Boolean> DATA_MORTAL =
            SynchedEntityData.defineId(PicoTierraEntity.class, EntityDataSerializers.BOOLEAN);

    private @Nullable RajangEntity dueno;
    private float dano;
    /** Solo de adorno (los de la Tumba): no golpea a nadie. */
    private boolean adorno;

    public PicoTierraEntity(EntityType<? extends PicoTierraEntity> tipo, Level nivel) {
        super(tipo, nivel);
        this.noPhysics = true;
        setNoGravity(true);
    }

    /** Un pincho mortal de la Embestida, a un lado de su camino. */
    public static PicoTierraEntity brotarMortal(ServerLevel nivel, RajangEntity dueno, Vec3 donde, float tam, float rumbo) {
        PicoTierraEntity p = brotar(nivel, dueno, donde, tam, rumbo, RajangEntity.MORTAL);
        p.entityData.set(DATA_MORTAL, true);
        return p;
    }

    /** Un pincho que solo se ve (las raices que revientan en la Tumba). */
    public static PicoTierraEntity brotarAdorno(ServerLevel nivel, RajangEntity dueno, Vec3 donde, float tam, float rumbo) {
        PicoTierraEntity p = brotar(nivel, dueno, donde, tam, rumbo, 0.0F);
        p.adorno = true;
        return p;
    }

    public static PicoTierraEntity brotar(ServerLevel nivel, RajangEntity dueno, Vec3 donde, float tam, float rumbo, float dano) {
        PicoTierraEntity p = new PicoTierraEntity(AtalayaEntities.PICO_TIERRA, nivel);
        p.dueno = dueno;
        p.dano = dano;
        p.entityData.set(DATA_TAM, tam);
        p.entityData.set(DATA_SEMILLA, nivel.getRandom().nextInt());
        p.setYRot(rumbo);
        p.setPos(donde.x, donde.y, donde.z);
        p.refreshDimensions();
        nivel.addFreshEntity(p);
        nivel.playSound(null, donde.x, donde.y, donde.z, AtalayaSonidos.RAJANG_PICO, SoundSource.HOSTILE,
                1.5F + 3.0F * tam, 1.25F - 0.45F * tam);
        nivel.sendParticles(AtalayaParticulas.RAJANG_POLVO, true, true, donde.x, donde.y + 0.3, donde.z,
                (int) (6 + 14 * tam), 0.6 + tam, 0.3, 0.6 + tam, 0.05);
        nivel.sendParticles(AtalayaParticulas.RAJANG_ROCA, true, true, donde.x, donde.y + 0.5, donde.z,
                (int) (4 + 10 * tam), 0.5, 0.3, 0.5, 0.25);
        if (tam > 0.6F) {
            nivel.sendParticles(AtalayaParticulas.RAJANG_ONDA, true, true, donde.x, donde.y + 0.1, donde.z, 0,
                    0.8 * tam, 4.0 * tam, 0.0, 1.0);
        }
        return p;
    }

    @Override
    protected void defineSynchedData(SynchedEntityData.Builder datos) {
        datos.define(DATA_TAM, 1.0F);
        datos.define(DATA_SEMILLA, 0);
        datos.define(DATA_MORTAL, false);
    }

    public boolean isMortal() {
        return entityData.get(DATA_MORTAL);
    }

    public float getTam() {
        return entityData.get(DATA_TAM);
    }

    public int getSemilla() {
        return entityData.get(DATA_SEMILLA);
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
        return EntityDimensions.scalable(1.0F + 1.6F * tam, ALTO * tam);
    }

    @Override
    public void tick() {
        super.tick();
        float tam = getTam();
        if (level().isClientSide()) {
            if (tickCount < SUBE + 2) {
                for (int i = 0; i < 3; i++) {
                    level().addParticle(AtalayaParticulas.RAJANG_POLVO, getX() + random.nextGaussian() * tam, getY() + 0.2,
                            getZ() + random.nextGaussian() * tam, random.nextGaussian() * 0.06, 0.08, random.nextGaussian() * 0.06);
                }
            }
            if (tickCount > DURA && tickCount % 2 == 0) {
                level().addParticle(AtalayaParticulas.RAJANG_POLVO, getX() + random.nextGaussian() * tam, getY() + 0.3,
                        getZ() + random.nextGaussian() * tam, 0, 0.04, 0);
            }
            return;
        }
        if (dueno == null || dueno.isRemoved()) {
            discard();
            return;
        }
        if (tickCount == 2 && !adorno) {
            golpear((ServerLevel) level(), tam);
        }
        if (tickCount == DURA) {
            level().playSound(null, getX(), getY(), getZ(), AtalayaSonidos.RAJANG_PICO, SoundSource.HOSTILE, 1.0F + tam, 0.6F);
        }
        if (tickCount >= DURA + BAJA) {
            discard();
        }
    }

    /**
     * Lo que esta encima sale volando: unos diez bloques (quince el de la
     * Embestida, que ademas mata salvo totem), y se queda con el Peso tres segundos.
     */
    private void golpear(ServerLevel nivel, float tam) {
        double radio = 0.8 + 1.3 * tam;
        boolean mortal = isMortal();
        DamageSource fuente = RajangDanos.fuente(nivel, mortal ? RajangDanos.EMBESTIDA : RajangDanos.GARRA, this, dueno);
        AABB caja = new AABB(getX() - radio, getY() - 0.5, getZ() - radio, getX() + radio, getY() + ALTO * tam, getZ() + radio);
        Vec3 empuje = Vec3.directionFromRotation(0, getYRot()).scale(mortal ? 0.4 : 0.25);
        for (LivingEntity v : nivel.getEntitiesOfClass(LivingEntity.class, caja, x -> dueno != null && dueno.esPresa(x))) {
            if (RajangEntity.horizontal(position(), v.position()) > radio) {
                continue;
            }
            v.hurtServer(nivel, fuente, mortal ? RajangEntity.MORTAL : RajangEntity.contraArmadura(v, dano * (0.6F + 0.4F * tam)));
            RajangEntity.lanzar(v, empuje, mortal ? RajangEntity.LANZA_MORTAL : LANZA);
            if (dueno != null) {
                dueno.lastrar(v, RajangEntity.PESO_PINCHO);
            }
            nivel.playSound(null, v.getX(), v.getY(), v.getZ(), AtalayaSonidos.RAJANG_PICO_GOLPE, SoundSource.HOSTILE, 1.5F, 1.0F);
            nivel.sendParticles(AtalayaParticulas.RAJANG_ROCA, true, true, v.getX(), v.getY() + 0.5, v.getZ(), 8, 0.3, 0.3, 0.3, 0.2);
        }
    }

    /** De 0 a 1 lo que ha salido (con un poco de rebote) y lo que se ha hundido al final. */
    public static float salida(float edad) {
        if (edad < SUBE) {
            float k = edad / SUBE;
            return Mth.clamp(1.0F + 1.4F * (float) Math.pow(k - 1.0F, 3) + 0.4F * (float) Math.pow(k - 1.0F, 2), 0.0F, 1.08F);
        }
        if (edad > DURA) {
            return Mth.clamp(1.0F - (edad - DURA) / BAJA, 0.0F, 1.0F);
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
