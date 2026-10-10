package com.atalaya.entity;

import com.atalaya.particula.AtalayaParticulas;
import com.atalaya.sonido.AtalayaSonidos;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.Mth;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityDimensions;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.Pose;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.storage.ValueInput;
import net.minecraft.world.level.storage.ValueOutput;
import net.minecraft.world.phys.Vec3;
import org.jspecify.annotations.Nullable;

/**
 * Una veleta del Vendaval: un poste de la piedra de la cima con la espiral del
 * viento tallada, el cristal de tormenta, la cruz de bronce con las letras de
 * los vientos y, arriba, la flecha con su cola de polilla; a sus pies, la rosa
 * de los vientos. Un clic derecho la gira 45 grados (en el sentido del reloj;
 * agachado, al reves). Cuando apunta a Aeralis, la flecha, el cristal y la
 * espiral se encienden; si ella se sale de su rumbo, aguanta enganchada un rato
 * (parpadea). Sale del suelo y se hunde al acabar.
 */
public class VeletaAeralisEntity extends Entity {

    public static final float ANCHO = 1.2F;
    public static final float ALTO = 4.4F;
    public static final int SUBE = 30;
    public static final int BAJA = 30;
    /** Lo que hay que esperar entre giro y giro (ticks): asi un grupo no la hace girar como un molino. */
    private static final int ENTRE_GIROS = 5;

    /** Hacia donde apunta: 0 a 7, cada uno 45 grados (0: hacia +Z, 2: hacia -X...). */
    private static final EntityDataAccessor<Integer> DATA_RUMBO =
            SynchedEntityData.defineId(VeletaAeralisEntity.class, EntityDataSerializers.INT);
    /** La luz: apagada, enganchada (ella se ha salido de su rumbo hace poco) o apuntandole. */
    private static final EntityDataAccessor<Integer> DATA_LUZ =
            SynchedEntityData.defineId(VeletaAeralisEntity.class, EntityDataSerializers.INT);
    public static final int APAGADA = 0;
    public static final int ENGANCHADA = 1;
    public static final int APUNTA = 2;
    /** Tick en que empezo a hundirse (-1: en pie). */
    private static final EntityDataAccessor<Integer> DATA_BAJA =
            SynchedEntityData.defineId(VeletaAeralisEntity.class, EntityDataSerializers.INT);

    private @Nullable VeletasAeralis juego;
    private int ultimoGiro = -100;
    /** Solo servidor: lo que le queda de enganche (ticks). */
    int enganche;
    /** Solo cliente: el angulo que se ve de la flecha (sigue al rumbo con suavidad). */
    public float anguloVisto = Float.NaN;
    public float anguloVistoAnt;

    public VeletaAeralisEntity(EntityType<? extends VeletaAeralisEntity> tipo, Level nivel) {
        super(tipo, nivel);
        this.noPhysics = true;
        setNoGravity(true);
    }

    static VeletaAeralisEntity alzar(ServerLevel nivel, VeletasAeralis juego, Vec3 donde, int rumbo) {
        VeletaAeralisEntity v = new VeletaAeralisEntity(AtalayaEntities.VELETA_AERALIS, nivel);
        v.juego = juego;
        v.entityData.set(DATA_RUMBO, Math.floorMod(rumbo, 8));
        v.snapTo(donde.x, donde.y, donde.z, 0.0F, 0.0F);
        nivel.addFreshEntity(v);
        nivel.sendParticles(AtalayaParticulas.AERALIS_POLVO, true, true, donde.x, donde.y + 0.3, donde.z, 16, 0.8, 0.2, 0.8, 0.04);
        return v;
    }

    @Override
    protected void defineSynchedData(SynchedEntityData.Builder datos) {
        datos.define(DATA_RUMBO, 0);
        datos.define(DATA_LUZ, APAGADA);
        datos.define(DATA_BAJA, -1);
    }

    public int getRumbo() {
        return entityData.get(DATA_RUMBO);
    }

    public int getLuz() {
        return entityData.get(DATA_LUZ);
    }

    public boolean encendida() {
        return getLuz() != APAGADA;
    }

    public int getBaja() {
        return entityData.get(DATA_BAJA);
    }

    /** El angulo (grados, rumbo de Minecraft) de cada uno de los ocho rumbos. */
    public static float grados(int rumbo) {
        return rumbo * 45.0F;
    }

    /** El rumbo (0 a 7) mas cercano a la direccion de aqui a p. */
    public int rumboHacia(Vec3 p) {
        return Math.floorMod(Math.round(gradosHacia(p) / 45.0F), 8);
    }

    private float gradosHacia(Vec3 p) {
        return (float) (Mth.atan2(p.z - getZ(), p.x - getX()) * Mth.RAD_TO_DEG) - 90.0F;
    }

    /** Si la flecha apunta a p con 'tolerancia' grados a cada lado (mas que el medio rumbo: se solapan). */
    boolean apuntaA(Vec3 p, double tolerancia) {
        return Math.abs(Mth.wrapDegrees(gradosHacia(p) - grados(getRumbo()))) <= tolerancia;
    }

    /** Lo que ha salido del suelo (0 a 1). */
    public float salida(float parcial) {
        float sube = Mth.clamp((tickCount + parcial) / SUBE, 0.0F, 1.0F);
        int baja = getBaja();
        if (baja >= 0) {
            sube = Math.min(sube, 1.0F - Mth.clamp((tickCount - baja + parcial) / BAJA, 0.0F, 1.0F));
        }
        return 1.0F - (1.0F - sube) * (1.0F - sube);
    }

    void encender(ServerLevel nivel, int luz) {
        int antes = getLuz();
        if (antes != luz) {
            entityData.set(DATA_LUZ, luz);
            if (luz == APUNTA) {
                Vec3 p = position().add(0, ALTO, 0);
                nivel.playSound(null, p.x, p.y, p.z, AtalayaSonidos.AERALIS_VELETA_APUNTA, SoundSource.HOSTILE, 2.0F, 1.0F);
                nivel.sendParticles(AtalayaParticulas.AERALIS_LUZ, true, true, p.x, p.y, p.z, 10, 0.5, 0.2, 0.5, 0.05);
            }
        }
    }

    @Override
    public InteractionResult interact(Player p, InteractionHand mano, Vec3 donde) {
        if (level().isClientSide()) {
            return InteractionResult.SUCCESS;
        }
        if (juego == null || getBaja() >= 0 || tickCount < SUBE || tickCount - ultimoGiro < ENTRE_GIROS) {
            return InteractionResult.PASS;
        }
        ultimoGiro = tickCount;
        // Agachado, al reves; al girarla se suelta el enganche.
        entityData.set(DATA_RUMBO, Math.floorMod(getRumbo() + (p.isShiftKeyDown() ? -1 : 1), 8));
        enganche = 0;
        Vec3 c = position().add(0, ALTO - 0.4, 0);
        level().playSound(null, c.x, c.y, c.z, AtalayaSonidos.AERALIS_VELETA_GIRA, SoundSource.PLAYERS, 1.6F, 0.9F + random.nextFloat() * 0.2F);
        if (level() instanceof ServerLevel nivel) {
            nivel.sendParticles(AtalayaParticulas.AERALIS_VIENTO, true, true, c.x, c.y, c.z, 6, 0.5, 0.1, 0.5, 0.08);
            juego.alGirar(nivel, this, p);
        }
        return InteractionResult.SUCCESS;
    }

    void hundir() {
        if (getBaja() < 0) {
            entityData.set(DATA_BAJA, tickCount);
            entityData.set(DATA_LUZ, APAGADA);
        }
    }

    @Override
    public EntityDimensions getDimensions(Pose pose) {
        return EntityDimensions.fixed(ANCHO, ALTO);
    }

    @Override
    public boolean isPickable() {
        return !isRemoved() && getBaja() < 0;
    }

    @Override
    public boolean canBeCollidedWith(@Nullable Entity otro) {
        return !isRemoved() && salida(0.0F) > 0.6F;
    }

    @Override
    public boolean canCollideWith(Entity otro) {
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
    public void tick() {
        super.tick();
        if (level().isClientSide()) {
            float objetivo = grados(getRumbo());
            if (Float.isNaN(anguloVisto)) {
                anguloVisto = objetivo;
            }
            anguloVistoAnt = anguloVisto;
            anguloVisto += Mth.wrapDegrees(objetivo - anguloVisto) * 0.35F;
            return;
        }
        if (juego == null || (getBaja() >= 0 && tickCount - getBaja() > BAJA + 2)) {
            discard();
        }
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
    protected void readAdditionalSaveData(ValueInput entrada) {
    }

    @Override
    protected void addAdditionalSaveData(ValueOutput salida) {
    }
}
