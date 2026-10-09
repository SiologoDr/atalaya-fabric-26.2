package com.atalaya.entity;

import com.atalaya.item.BalaCanonItem;
import com.atalaya.particula.AtalayaParticulas;
import com.atalaya.particula.ParticulaSiguiente;
import com.atalaya.sonido.AtalayaSonidos;
import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.Mth;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityDimensions;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.storage.ValueInput;
import net.minecraft.world.level.storage.ValueOutput;
import net.minecraft.world.phys.Vec3;
import org.jspecify.annotations.Nullable;

/**
 * Un canon del barco hundido (los Canones del Naufragio de Nerea, octubre de
 * 2026: las armas de asedio de Monster Hunter). Sale del suelo con su cureña
 * de madera podrida.
 *
 * El cargador mete una bala (clic derecho con la Bala de canon de la pila en la
 * mano). El artillero se sube (clic derecho con la mano libre): el canon apunta
 * a donde mira, dispara con ESPACIO y se baja con SHIFT. Cada bala que le da a
 * Nerea le quita un 3 % y la hace tambalearse; tres seguidas, aturdida.
 */
public class CanonNaufragioEntity extends Entity {

    /** Lo que tarda en salir del suelo y en hundirse (ticks). */
    public static final int SALE = 20;
    /** El alza del canon (grados): de un poco hacia abajo a bastante hacia arriba. */
    public static final float ALZA_MIN = -8.0F;
    public static final float ALZA_MAX = 40.0F;
    /** Donde esta la boca: a esta altura sobre el suelo y a este largo del munon. */
    public static final double BOCA_ALTO = 0.95;
    public static final double BOCA_LARGO = 1.6;

    private static final EntityDataAccessor<Boolean> DATA_CARGADO =
            SynchedEntityData.defineId(CanonNaufragioEntity.class, EntityDataSerializers.BOOLEAN);
    private static final EntityDataAccessor<Float> DATA_ALZA =
            SynchedEntityData.defineId(CanonNaufragioEntity.class, EntityDataSerializers.FLOAT);
    private static final EntityDataAccessor<Integer> DATA_HUNDE =
            SynchedEntityData.defineId(CanonNaufragioEntity.class, EntityDataSerializers.INT);
    /** El tick del ultimo disparo (el retroceso y el fogonazo). */
    private static final EntityDataAccessor<Integer> DATA_DISPARO =
            SynchedEntityData.defineId(CanonNaufragioEntity.class, EntityDataSerializers.INT);

    private @Nullable NereaEntity duena;
    private boolean saltoAntes;

    public CanonNaufragioEntity(EntityType<? extends CanonNaufragioEntity> tipo, Level nivel) {
        super(tipo, nivel);
        this.noPhysics = true;
        setNoGravity(true);
    }

    static CanonNaufragioEntity alzar(ServerLevel nivel, NereaEntity duena, Vec3 donde, float rumbo) {
        CanonNaufragioEntity c = new CanonNaufragioEntity(AtalayaEntities.CANON_NAUFRAGIO, nivel);
        c.duena = duena;
        c.setYRot(rumbo);
        c.yRotO = rumbo;
        c.setPos(donde.x, donde.y, donde.z);
        nivel.addFreshEntity(c);
        nivel.sendParticles(AtalayaParticulas.NEREA_POLVO, true, true, donde.x, donde.y + 0.3, donde.z, 20, 1.0, 0.2, 1.0, 0.03);
        nivel.playSound(null, donde.x, donde.y, donde.z, AtalayaSonidos.NEREA_CANON_SALE, SoundSource.HOSTILE, 1.4F,
                0.9F + nivel.getRandom().nextFloat() * 0.2F);
        return c;
    }

    @Override
    protected void defineSynchedData(SynchedEntityData.Builder datos) {
        datos.define(DATA_CARGADO, false);
        datos.define(DATA_ALZA, 10.0F);
        datos.define(DATA_HUNDE, -1);
        datos.define(DATA_DISPARO, -100);
    }

    public boolean cargado() {
        return entityData.get(DATA_CARGADO);
    }

    public float alza() {
        return entityData.get(DATA_ALZA);
    }

    public int hunde() {
        return entityData.get(DATA_HUNDE);
    }

    public int ultimoDisparo() {
        return entityData.get(DATA_DISPARO);
    }

    void hundir() {
        if (hunde() < 0) {
            entityData.set(DATA_HUNDE, tickCount);
            ejectPassengers();
        }
    }

    @Override
    public void tick() {
        super.tick();
        Entity jinete = getFirstPassenger();
        if (jinete instanceof Player p) {
            // Apunta a donde mira el artillero.
            setYRot(p.getYRot());
            if (!level().isClientSide()) {
                entityData.set(DATA_ALZA, Mth.clamp(-p.getXRot(), ALZA_MIN, ALZA_MAX));
            }
        }
        if (level().isClientSide()) {
            if (cargado() && tickCount % 5 == 0) {
                // La mecha encendida: humo fino y alguna chispa.
                Vec3 m = mecha();
                ParticulaSiguiente.escala = 0.35F;
                level().addParticle(AtalayaParticulas.NEREA_HUMO, m.x, m.y, m.z, 0, 0.03, 0);
                if (random.nextInt(3) == 0) {
                    level().addParticle(AtalayaParticulas.NEREA_CHISPA, m.x, m.y, m.z, 0, 0.05, 0);
                }
            }
            int d = tickCount - ultimoDisparo();
            if (d == 0) {
                fogonazo();
            }
            return;
        }
        ServerLevel nivel = (ServerLevel) level();
        if (duena == null || duena.isRemoved() || (hunde() >= 0 && tickCount - hunde() > SALE)) {
            ejectPassengers();
            discard();
            return;
        }
        if (jinete instanceof ServerPlayer sp) {
            boolean salto = sp.getLastClientInput().jump();
            if (salto && !saltoAntes) {
                disparar(nivel, sp);
            }
            saltoAntes = salto;
        } else {
            saltoAntes = false;
        }
    }

    /** Hacia donde apunta la boca (con el rumbo y el alza). */
    public Vec3 apunta() {
        float y = getYRot() * Mth.DEG_TO_RAD;
        float a = alza() * Mth.DEG_TO_RAD;
        return new Vec3(-Mth.sin(y) * Mth.cos(a), Mth.sin(a), Mth.cos(y) * Mth.cos(a));
    }

    /** La boca del canon (de donde sale la bala). */
    public Vec3 boca() {
        return position().add(0, BOCA_ALTO, 0).add(apunta().scale(BOCA_LARGO));
    }

    /** En el cliente: el fogonazo y la nube de humo que salen de la boca al disparar. */
    private void fogonazo() {
        Vec3 b = boca();
        Vec3 a = apunta();
        for (int i = 0; i < 4; i++) {
            level().addParticle(AtalayaParticulas.NEREA_FOGONAZO, b.x + a.x * i * 0.35, b.y + a.y * i * 0.35, b.z + a.z * i * 0.35,
                    a.x, a.y, a.z);
        }
        for (int i = 0; i < 18; i++) {
            double k = random.nextDouble();
            level().addParticle(AtalayaParticulas.NEREA_HUMO, b.x + (random.nextDouble() - 0.5) * 0.5, b.y + (random.nextDouble() - 0.5) * 0.5,
                    b.z + (random.nextDouble() - 0.5) * 0.5, a.x * 0.25 * k + (random.nextDouble() - 0.5) * 0.08,
                    a.y * 0.25 * k + 0.02, a.z * 0.25 * k + (random.nextDouble() - 0.5) * 0.08);
        }
    }

    private Vec3 mecha() {
        return position().add(0, 1.2, 0).subtract(apunta().scale(0.6));
    }

    private void disparar(ServerLevel nivel, ServerPlayer sp) {
        if (!cargado() || hunde() >= 0) {
            sp.sendOverlayMessage(Component.translatable("hud.atalaya.nerea.canon_sin_bala").withStyle(ChatFormatting.GRAY));
            nivel.playSound(null, getX(), getY() + 1.0, getZ(), AtalayaSonidos.NEREA_CANON_VACIO, SoundSource.PLAYERS, 1.0F, 1.0F);
            return;
        }
        entityData.set(DATA_CARGADO, false);
        entityData.set(DATA_DISPARO, tickCount);
        Vec3 b = boca();
        BalaCanonEntity.disparar(nivel, duena, b, apunta());
        nivel.playSound(null, b.x, b.y, b.z, AtalayaSonidos.NEREA_CANON_DISPARO, SoundSource.PLAYERS, 4.0F,
                0.95F + random.nextFloat() * 0.1F);
    }

    /** Solo pruebas: cargado sin bala en la mano. */
    void cargarPrueba() {
        entityData.set(DATA_CARGADO, true);
    }

    /** Solo pruebas: dispara como si el artillero pulsara ESPACIO. */
    void dispararPrueba(ServerLevel nivel, ServerPlayer sp) {
        disparar(nivel, sp);
    }

    @Override
    public InteractionResult interact(Player p, InteractionHand mano, Vec3 donde) {
        if (hunde() >= 0) {
            return InteractionResult.PASS;
        }
        ItemStack lleva = p.getItemInHand(mano);
        if (lleva.getItem() instanceof BalaCanonItem) {
            if (cargado()) {
                return InteractionResult.PASS;
            }
            if (!level().isClientSide()) {
                lleva.shrink(1);
                entityData.set(DATA_CARGADO, true);
                level().playSound(null, getX(), getY() + 1.0, getZ(), AtalayaSonidos.NEREA_CANON_CARGAR, SoundSource.PLAYERS, 1.2F, 1.0F);
                p.sendOverlayMessage(Component.translatable("hud.atalaya.nerea.canon_cargado").withStyle(ChatFormatting.GOLD));
            }
            return InteractionResult.SUCCESS;
        }
        if (mano == InteractionHand.MAIN_HAND && !isVehicle() && !p.isPassenger()) {
            if (!level().isClientSide()) {
                p.startRiding(this);
                p.sendOverlayMessage(Component.translatable(cargado() ? "hud.atalaya.nerea.canon_subido"
                        : "hud.atalaya.nerea.canon_subido_vacio").withStyle(ChatFormatting.GOLD));
            }
            return InteractionResult.SUCCESS;
        }
        return InteractionResult.PASS;
    }

    @Override
    protected boolean canAddPassenger(Entity e) {
        return getPassengers().isEmpty() && e instanceof Player && hunde() < 0;
    }

    @Override
    protected Vec3 getPassengerAttachmentPoint(Entity e, EntityDimensions dim, float escala) {
        return new Vec3(0, 0.25, -1.45).yRot(-getYRot() * Mth.DEG_TO_RAD);
    }

    @Override
    public @Nullable LivingEntity getControllingPassenger() {
        return null;
    }

    @Override
    public boolean isPickable() {
        return hunde() < 0;
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
