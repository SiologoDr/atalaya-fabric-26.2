package com.atalaya.entity;

import com.atalaya.particula.AtalayaParticulas;
import com.atalaya.sonido.AtalayaSonidos;
import java.util.UUID;
import net.minecraft.ChatFormatting;
import net.minecraft.core.UUIDUtil;
import net.minecraft.network.chat.Component;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.storage.ValueInput;
import net.minecraft.world.level.storage.ValueOutput;
import net.minecraft.world.phys.Vec3;
import org.jspecify.annotations.Nullable;

/**
 * El remolino de la Rafaga Ladrona (Aeralis, octubre de 2026): una rafaga le
 * arranca el arma de la mano a alguien y la mete en un remolino pequeno que
 * gira alrededor de su dueno, a la altura de la espada. Tres golpes de quien
 * sea (de un companero o del mismo, a punetazos) lo rompen y el arma VUELVE A
 * SU MANO (Juan: "que se regrese a su portador, no a su lado"); si su mano esta
 * ocupada, a su inventario; si no cabe, a sus pies. A los 15 s vuelve sola.
 *
 * El arma nunca se pierde: el remolino se guarda con el mundo, y si lo quitan
 * o su dueno no esta, la deja caer donde este.
 */
public class RemolinoLadronEntity extends Entity {

    /** Golpes para romperlo. */
    public static final int GOLPES = 3;
    /** Lo que dura (ticks): 15 s. */
    private static final int VIDA = 300;
    /** A que distancia de su dueno gira y a que altura sobre sus pies: a mano de espada, para que pueda romperlo solo. */
    private static final double RADIO = 2.3;
    private static final double ALTO = 1.2;

    private static final EntityDataAccessor<ItemStack> DATA_BOTIN =
            SynchedEntityData.defineId(RemolinoLadronEntity.class, EntityDataSerializers.ITEM_STACK);
    private static final EntityDataAccessor<Integer> DATA_GOLPES =
            SynchedEntityData.defineId(RemolinoLadronEntity.class, EntityDataSerializers.INT);
    private static final EntityDataAccessor<Integer> DATA_FASE =
            SynchedEntityData.defineId(RemolinoLadronEntity.class, EntityDataSerializers.INT);

    private @Nullable UUID dueno;
    private int vida = VIDA;
    private float giro;
    private int ultimoGolpe = -10;

    public RemolinoLadronEntity(EntityType<? extends RemolinoLadronEntity> tipo, Level nivel) {
        super(tipo, nivel);
        this.noPhysics = true;
        setNoGravity(true);
    }

    /** Le quita a "v" lo que lleva en la mano y lo mete en un remolino a su lado. null si no llevaba nada. */
    public static @Nullable RemolinoLadronEntity robar(ServerLevel nivel, AeralisEntity aeralis, LivingEntity v) {
        ItemStack mano = v.getMainHandItem();
        if (mano.isEmpty()) {
            return null;
        }
        RemolinoLadronEntity r = new RemolinoLadronEntity(AtalayaEntities.REMOLINO_LADRON, nivel);
        r.dueno = v.getUUID();
        r.entityData.set(DATA_BOTIN, mano.copy());
        r.entityData.set(DATA_FASE, aeralis.fase());
        v.setItemInHand(InteractionHand.MAIN_HAND, ItemStack.EMPTY);
        r.giro = (float) (nivel.getRandom().nextDouble() * Math.PI * 2);
        Vec3 p = r.sitio(v);
        r.setPos(p.x, p.y, p.z);
        nivel.addFreshEntity(r);
        nivel.sendParticles(AtalayaParticulas.AERALIS_JIRON, true, true, v.getX(), v.getY() + 1.2, v.getZ(), 14, 0.4, 0.5, 0.4, 0.15);
        nivel.playSound(null, v.getX(), v.getEyeY(), v.getZ(), AtalayaSonidos.AERALIS_TORNADO_ATRAPA, SoundSource.HOSTILE, 1.5F, 1.4F);
        if (v instanceof Player p2) {
            p2.sendOverlayMessage(Component.translatable("hud.atalaya.aeralis.ladrona_robado").withStyle(ChatFormatting.AQUA));
        }
        return r;
    }

    @Override
    protected void defineSynchedData(SynchedEntityData.Builder datos) {
        datos.define(DATA_BOTIN, ItemStack.EMPTY);
        datos.define(DATA_GOLPES, 0);
        datos.define(DATA_FASE, 2);
    }

    public ItemStack getBotin() {
        return entityData.get(DATA_BOTIN);
    }

    public int getGolpes() {
        return entityData.get(DATA_GOLPES);
    }

    public int getFase() {
        return entityData.get(DATA_FASE);
    }

    /** Donde va: alrededor de su dueno, a la altura de la espada. */
    private Vec3 sitio(Entity d) {
        return new Vec3(d.getX() + Math.cos(giro) * RADIO, d.getY() + ALTO, d.getZ() + Math.sin(giro) * RADIO);
    }

    private @Nullable LivingEntity elDueno(ServerLevel nivel) {
        if (dueno == null) {
            return null;
        }
        Entity e = nivel.getEntity(dueno);
        return e instanceof LivingEntity v && v.isAlive() ? v : null;
    }

    @Override
    public void tick() {
        super.tick();
        if (level().isClientSide()) {
            // El remolino: motas de viento en espiral alrededor del arma.
            if (tickCount % 2 == 0) {
                double a = tickCount * 0.6;
                for (int i = 0; i < 2; i++) {
                    double b = a + i * Math.PI;
                    level().addParticle(AtalayaParticulas.AERALIS_VIENTO, getX() + Math.cos(b) * 0.8, getY() + 0.2 + Math.sin(a * 0.5) * 0.3,
                            getZ() + Math.sin(b) * 0.8, -Math.sin(b) * 0.2, 0.02, Math.cos(b) * 0.2);
                }
            }
            return;
        }
        ServerLevel nivel = (ServerLevel) level();
        if (getBotin().isEmpty()) {
            discard();
            return;
        }
        LivingEntity d = elDueno(nivel);
        if (d != null) {
            giro += 0.045F;
            Vec3 p = sitio(d);
            Vec3 aqui = position();
            Vec3 paso = p.subtract(aqui);
            if (paso.length() > 8.0) {
                setPos(p.x, p.y, p.z);
            } else {
                Vec3 n = aqui.add(paso.scale(0.25));
                setPos(n.x, n.y, n.z);
            }
        }
        if (--vida <= 0) {
            devolver(nivel);
        }
    }

    @Override
    public boolean isPickable() {
        return true;
    }

    @Override
    public boolean hurtServer(ServerLevel nivel, DamageSource fuente, float cantidad) {
        Entity quien = fuente.getEntity();
        if (isRemoved() || !(quien instanceof Player) || tickCount - ultimoGolpe < 4) {
            return false;
        }
        ultimoGolpe = tickCount;
        int g = getGolpes() + 1;
        entityData.set(DATA_GOLPES, g);
        nivel.playSound(null, getX(), getY(), getZ(), AtalayaSonidos.AERALIS_NUCLEO_GOLPE, SoundSource.PLAYERS, 1.2F,
                1.0F + 0.25F * g);
        nivel.sendParticles(AtalayaParticulas.AERALIS_LUZ, true, true, getX(), getY() + 0.3, getZ(), 6, 0.3, 0.3, 0.3, 0.1);
        if (g >= GOLPES) {
            devolver(nivel);
        }
        return true;
    }

    /** El arma vuelve a la mano de su dueno (o a su inventario, o a sus pies); sin dueno, cae aqui. */
    public void devolver(ServerLevel nivel) {
        ItemStack botin = getBotin().copy();
        entityData.set(DATA_BOTIN, ItemStack.EMPTY);
        if (botin.isEmpty()) {
            discard();
            return;
        }
        LivingEntity d = elDueno(nivel);
        if (d == null) {
            ItemEntity it = new ItemEntity(nivel, getX(), getY(), getZ(), botin);
            it.setDefaultPickUpDelay();
            nivel.addFreshEntity(it);
        } else {
            if (d.getMainHandItem().isEmpty()) {
                d.setItemInHand(InteractionHand.MAIN_HAND, botin);
            } else if (d instanceof Player p) {
                if (!p.getInventory().add(botin)) {
                    p.drop(botin, false);
                }
            } else {
                ItemEntity it = new ItemEntity(nivel, d.getX(), d.getY() + 0.5, d.getZ(), botin);
                nivel.addFreshEntity(it);
            }
            nivel.playSound(null, d.getX(), d.getEyeY(), d.getZ(), AtalayaSonidos.AERALIS_NUCLEO_ROTO, SoundSource.PLAYERS, 1.2F, 1.6F);
            nivel.sendParticles(AtalayaParticulas.AERALIS_LUZ, true, true, d.getX(), d.getY() + 1.2, d.getZ(), 16, 0.4, 0.6, 0.4, 0.2);
            if (d instanceof Player p) {
                p.sendOverlayMessage(Component.translatable("hud.atalaya.aeralis.ladrona_vuelve").withStyle(ChatFormatting.AQUA));
            }
        }
        nivel.sendParticles(AtalayaParticulas.AERALIS_JIRON, true, true, getX(), getY() + 0.3, getZ(), 18, 0.5, 0.5, 0.5, 0.2);
        discard();
    }

    @Override
    public void remove(RemovalReason motivo) {
        // Si lo quitan con el arma dentro (un /kill, una limpieza), el arma no se pierde.
        if (motivo.shouldDestroy() && !getBotin().isEmpty() && level() instanceof ServerLevel nivel) {
            ItemStack botin = getBotin().copy();
            entityData.set(DATA_BOTIN, ItemStack.EMPTY);
            ItemEntity it = new ItemEntity(nivel, getX(), getY(), getZ(), botin);
            nivel.addFreshEntity(it);
        }
        super.remove(motivo);
    }

    @Override
    public boolean shouldRenderAtSqrDistance(double distancia) {
        return distancia < 96 * 96;
    }

    @Override
    protected void readAdditionalSaveData(ValueInput entrada) {
        dueno = entrada.read("dueno", UUIDUtil.CODEC).orElse(null);
        vida = entrada.getIntOr("vida", VIDA);
        entityData.set(DATA_GOLPES, entrada.getIntOr("golpes", 0));
        entityData.set(DATA_FASE, entrada.getIntOr("fase", 2));
        entityData.set(DATA_BOTIN, entrada.read("botin", ItemStack.OPTIONAL_CODEC).orElse(ItemStack.EMPTY));
    }

    @Override
    protected void addAdditionalSaveData(ValueOutput salida) {
        salida.storeNullable("dueno", UUIDUtil.CODEC, dueno);
        salida.putInt("vida", vida);
        salida.putInt("golpes", getGolpes());
        salida.putInt("fase", getFase());
        salida.store("botin", ItemStack.OPTIONAL_CODEC, getBotin());
    }
}
