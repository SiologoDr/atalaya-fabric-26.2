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
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.storage.ValueInput;
import net.minecraft.world.level.storage.ValueOutput;
import net.minecraft.world.phys.Vec3;
import org.jspecify.annotations.Nullable;

/**
 * El pilar del altar del Idolo de Oro (08-10-2026, Juan: "donde debe poner el
 * idolo debe ser en un pilar pequeno, corto"): un pilar de jade con el jaguar
 * tallado en oro y el capitel de oro con el hueco del idolo, de poco mas de un
 * bloque. Sale del suelo cuando Rajang lanza el idolo, al otro lado de la arena;
 * quien lleva el idolo lo pone encima al llegar a su lado. Entonces el idolo se
 * queda sobre el pilar un momento y los dos revientan en oro.
 *
 * Se pisa (es una caja de choque, solo para los jugadores: Rajang no tropieza
 * con el). Se va con su Rajang y no se guarda con el mundo.
 */
public class AltarIdoloEntity extends Entity {

    /** Medidas del pilar, en bloques (AltarIdoloRenderer lo pinta igual). */
    public static final float ANCHO = 1.44F;
    public static final float ALTO = 1.3125F;
    /** Lo que tarda en salir del suelo. */
    public static final int SALE = 10;
    /** Lo que se queda el idolo encima antes de reventar. */
    public static final int CON_IDOLO = 36;

    private static final EntityDataAccessor<Boolean> DATA_IDOLO =
            SynchedEntityData.defineId(AltarIdoloEntity.class, EntityDataSerializers.BOOLEAN);

    private @Nullable RajangEntity dueno;
    private int recibido = -1;

    public AltarIdoloEntity(EntityType<? extends AltarIdoloEntity> tipo, Level nivel) {
        super(tipo, nivel);
        this.noPhysics = true;
        setNoGravity(true);
    }

    /** El pilar, en donde (sus pies), mirando hacia rumbo (grados). */
    public static AltarIdoloEntity alzar(ServerLevel nivel, RajangEntity dueno, Vec3 donde, float rumbo) {
        AltarIdoloEntity a = new AltarIdoloEntity(AtalayaEntities.ALTAR_IDOLO, nivel);
        a.dueno = dueno;
        a.setYRot(rumbo);
        a.setPos(donde.x, donde.y, donde.z);
        nivel.addFreshEntity(a);
        nivel.sendParticles(AtalayaParticulas.RAJANG_POLVO, true, true, donde.x, donde.y + 0.3, donde.z, 16, 0.7, 0.2, 0.7, 0.04);
        nivel.playSound(null, donde.x, donde.y, donde.z, AtalayaSonidos.RAJANG_PILAR, SoundSource.HOSTILE, 2.5F, 1.5F);
        return a;
    }

    @Override
    protected void defineSynchedData(SynchedEntityData.Builder datos) {
        datos.define(DATA_IDOLO, false);
    }

    /** Ya tiene el idolo encima. */
    public boolean conIdolo() {
        return entityData.get(DATA_IDOLO);
    }

    /** Lo que ha salido del suelo, de 0 a 1. */
    public float salida(float parcial) {
        return Mth.clamp((tickCount + parcial) / SALE, 0.0F, 1.0F);
    }

    /** Donde se pone el idolo: encima del capitel. */
    public Vec3 cima() {
        return position().add(0, ALTO, 0);
    }

    /** Le ponen el idolo encima: se queda un momento y revientan los dos. */
    public void recibir(ServerLevel nivel) {
        entityData.set(DATA_IDOLO, true);
        recibido = tickCount;
        Vec3 c = cima();
        nivel.sendParticles(AtalayaParticulas.RAJANG_ORO, true, true, c.x, c.y + 0.4, c.z, 40, 0.4, 0.4, 0.4, 0.12);
        nivel.playSound(null, c.x, c.y, c.z, AtalayaSonidos.RAJANG_TOTEM, SoundSource.HOSTILE, 4.0F, 0.7F);
    }

    /** Se acabo sin idolo: se hunde con un poco de polvo. */
    public void retirar(ServerLevel nivel) {
        nivel.sendParticles(AtalayaParticulas.RAJANG_POLVO, true, true, getX(), getY() + 0.5, getZ(), 18, 0.6, 0.4, 0.6, 0.04);
        discard();
    }

    private void reventar(ServerLevel nivel) {
        Vec3 c = cima();
        nivel.sendParticles(AtalayaParticulas.RAJANG_ORO, true, true, c.x, c.y + 0.3, c.z, 90, 0.9, 1.2, 0.9, 0.35);
        nivel.sendParticles(AtalayaParticulas.RAJANG_JADE, true, true, getX(), getY() + 0.7, getZ(), 40, 0.6, 0.6, 0.6, 0.25);
        nivel.sendParticles(AtalayaParticulas.RAJANG_ROCA, true, true, getX(), getY() + 0.6, getZ(), 14, 0.5, 0.4, 0.5, 0.25);
        nivel.playSound(null, c.x, c.y, c.z, AtalayaSonidos.RAJANG_TOTEM_ROTO, SoundSource.HOSTILE, 6.0F, 0.8F);
        discard();
    }

    @Override
    public void tick() {
        super.tick();
        // Grande y se pisa: que se encuentre al buscar con que se choca (ColisionGrande).
        ColisionGrande.apuntar(this);
        if (level().isClientSide()) {
            return;
        }
        ServerLevel nivel = (ServerLevel) level();
        if (recibido < 0 && (dueno == null || dueno.isRemoved() || !dueno.idoloFuera())) {
            retirar(nivel);
            return;
        }
        if (recibido >= 0) {
            if (tickCount - recibido >= CON_IDOLO) {
                reventar(nivel);
            }
            return;
        }
        // Que se vea desde lejos: chispas de oro que suben de su capitel.
        if (tickCount % 3 == 0) {
            Vec3 c = cima();
            nivel.sendParticles(AtalayaParticulas.RAJANG_ORO, true, true, c.x + random.nextGaussian() * 0.2,
                    c.y + 0.2 + random.nextDouble() * 9.0, c.z + random.nextGaussian() * 0.2, 1, 0.04, 0.2, 0.04, 0.02);
        }
    }

    @Override
    public EntityDimensions getDimensions(Pose pose) {
        return EntityDimensions.fixed(ANCHO, ALTO);
    }

    @Override
    public boolean canBeCollidedWith(@Nullable Entity otro) {
        return !isRemoved() && otro instanceof Player && salida(0.0F) > 0.5F;
    }

    @Override
    public boolean canCollideWith(Entity otro) {
        return false;
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
        return distancia < 192 * 192;
    }

    @Override
    protected void readAdditionalSaveData(ValueInput entrada) {
    }

    @Override
    protected void addAdditionalSaveData(ValueOutput salida) {
    }
}
