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
import net.minecraft.world.level.Level;
import net.minecraft.world.level.storage.ValueInput;
import net.minecraft.world.level.storage.ValueOutput;
import net.minecraft.world.phys.Vec3;
import org.jspecify.annotations.Nullable;

/**
 * Una trampa de oro de El Rayo del Prisma: un hoyo cuadrado en el suelo, con el
 * borde de oro y pinchos de jade dentro. Si Rajang cae en ella al saltar sobre
 * la luz, los pinchos le muerden (RajangEntity.alCaerEnTrampa) y la trampa
 * queda rota. Sale del suelo y se hunde al acabar.
 */
public class TrampaOroEntity extends Entity {

    /** El lado del hoyo (bloques) y hasta donde cuenta que ha caido dentro (desde el centro). */
    public static final float LADO = 4.0F;
    public static final double CAE_DENTRO = 3.4;
    /** Lo que tarda en abrirse y en cerrarse (ticks). */
    public static final int ABRE = 15;

    private static final EntityDataAccessor<Boolean> DATA_USADA =
            SynchedEntityData.defineId(TrampaOroEntity.class, EntityDataSerializers.BOOLEAN);
    private static final EntityDataAccessor<Integer> DATA_CIERRA =
            SynchedEntityData.defineId(TrampaOroEntity.class, EntityDataSerializers.INT);

    private @Nullable RajangEntity rajang;

    public TrampaOroEntity(EntityType<? extends TrampaOroEntity> tipo, Level nivel) {
        super(tipo, nivel);
        this.noPhysics = true;
        setNoGravity(true);
    }

    static TrampaOroEntity abrir(ServerLevel nivel, RajangEntity r, Vec3 donde) {
        TrampaOroEntity t = new TrampaOroEntity(AtalayaEntities.TRAMPA_ORO, nivel);
        t.rajang = r;
        t.setPos(donde.x, donde.y, donde.z);
        nivel.addFreshEntity(t);
        nivel.sendParticles(AtalayaParticulas.RAJANG_POLVO, true, true, donde.x, donde.y + 0.3, donde.z, 24, 1.2, 0.2, 1.2, 0.04);
        nivel.playSound(null, donde.x, donde.y, donde.z, AtalayaSonidos.RAJANG_TRAMPA_ABRE, SoundSource.HOSTILE, 2.0F, 1.0F);
        return t;
    }

    @Override
    protected void defineSynchedData(SynchedEntityData.Builder datos) {
        datos.define(DATA_USADA, false);
        datos.define(DATA_CIERRA, -1);
    }

    public boolean usada() {
        return entityData.get(DATA_USADA);
    }

    public int cierra() {
        return entityData.get(DATA_CIERRA);
    }

    /** Rajang ha caido dentro: los pinchos se rompen contra el. */
    void usar(ServerLevel nivel) {
        entityData.set(DATA_USADA, true);
        Vec3 p = position();
        nivel.sendParticles(AtalayaParticulas.RAJANG_ORO, true, true, p.x, p.y + 0.6, p.z, 40, 1.4, 0.6, 1.4, 0.2);
        nivel.sendParticles(AtalayaParticulas.RAJANG_JADE, true, true, p.x, p.y + 0.6, p.z, 30, 1.2, 0.6, 1.2, 0.25);
        nivel.sendParticles(AtalayaParticulas.RAJANG_ROCA, true, true, p.x, p.y + 0.4, p.z, 16, 1.0, 0.4, 1.0, 0.25);
        nivel.playSound(null, p.x, p.y, p.z, AtalayaSonidos.RAJANG_TRAMPA_CAE, SoundSource.HOSTILE, 5.0F, 1.0F);
    }

    void cerrar() {
        if (cierra() < 0) {
            entityData.set(DATA_CIERRA, tickCount);
        }
    }

    @Override
    public void tick() {
        super.tick();
        if (level().isClientSide()) {
            if (!usada() && cierra() < 0 && random.nextInt(4) == 0) {
                // Que se vea desde lejos: chispas de oro que suben del borde.
                double a = random.nextDouble() * Math.PI * 2;
                level().addParticle(AtalayaParticulas.RAJANG_ORO, getX() + Math.cos(a) * LADO / 2, getY() + 0.2,
                        getZ() + Math.sin(a) * LADO / 2, 0, 0.06, 0);
            }
            return;
        }
        if (rajang == null || rajang.isRemoved() || (cierra() >= 0 && tickCount - cierra() > ABRE)) {
            discard();
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
        return distancia < 160 * 160;
    }

    @Override
    protected void readAdditionalSaveData(ValueInput entrada) {
    }

    @Override
    protected void addAdditionalSaveData(ValueOutput salida) {
    }
}
