package com.atalaya.entity;

import com.atalaya.particula.AtalayaParticulas;
import com.atalaya.sonido.AtalayaSonidos;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.level.ClipContext;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.storage.ValueInput;
import net.minecraft.world.level.storage.ValueOutput;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;
import org.jspecify.annotations.Nullable;

/**
 * Una cupula de refugio de la Marea Alta (Nerea, octubre de 2026): media esfera
 * de agua celeste apoyada en el suelo (Juan: "celeste y como una cupula"), donde
 * caben "aforo" jugadores. Al acabar
 * la cuenta atras, quien no este dentro de una revienta el totem. Encima lleva
 * cuantos caben ("1/2"); llena se pone roja y se cierra: echa hacia fuera a
 * quien intente entrar, hasta que salga alguno de los de dentro.
 *
 * Hay las justas: una por cada "aforo" jugadores, repartidas por la arena. Hay
 * que repartirse: el que llega tarde a una llena tiene que buscar otra.
 */
public class RefugioNereaEntity extends Entity {

    /** El radio de la cupula (bloques): caben dos de pie con holgura. */
    public static final float RADIO = 2.4F;

    private static final EntityDataAccessor<Integer> DATA_AFORO =
            SynchedEntityData.defineId(RefugioNereaEntity.class, EntityDataSerializers.INT);
    private static final EntityDataAccessor<Integer> DATA_DENTRO =
            SynchedEntityData.defineId(RefugioNereaEntity.class, EntityDataSerializers.INT);

    private @Nullable NereaEntity duena;
    /** Los de dentro, por orden de llegada: los primeros "aforo" estan a salvo. */
    private final List<UUID> dentro = new ArrayList<>();
    /** A quien ha echado y cuando (el aviso y el sonido, no mas de uno cada 0,75 s). */
    private final Map<UUID, Integer> avisados = new HashMap<>();
    /** Lo fuerte que echa la cupula llena (bloques/tick, hacia fuera). */
    private static final double EMPUJE = 0.55;
    private int vida = 260;

    public RefugioNereaEntity(EntityType<? extends RefugioNereaEntity> tipo, Level nivel) {
        super(tipo, nivel);
        this.noPhysics = true;
        setNoGravity(true);
    }

    /** Una burbuja en (x, z), apoyada en el suelo de por alli. */
    public static RefugioNereaEntity crear(ServerLevel nivel, NereaEntity duena, double x, double y, double z, int aforo) {
        RefugioNereaEntity r = new RefugioNereaEntity(AtalayaEntities.REFUGIO_NEREA, nivel);
        r.duena = duena;
        r.entityData.set(DATA_AFORO, aforo);
        BlockHitResult suelo = nivel.clip(new ClipContext(new Vec3(x, y + 8, z), new Vec3(x, y - 16, z),
                ClipContext.Block.COLLIDER, ClipContext.Fluid.NONE, duena));
        double ys = suelo.getType() == HitResult.Type.MISS ? y : suelo.getLocation().y;
        r.setPos(x, ys, z);
        r.rotular();
        nivel.addFreshEntity(r);
        nivel.sendParticles(AtalayaParticulas.NEREA_BURBUJA, true, true, x, ys + RADIO, z, 30, 1.0, 1.0, 1.0, 0.1);
        nivel.sendParticles(AtalayaParticulas.NEREA_ESPUMA, true, true, x, ys + 0.1, z, 20, 1.2, 0.05, 1.2, 0.05);
        return r;
    }

    @Override
    protected void defineSynchedData(SynchedEntityData.Builder datos) {
        datos.define(DATA_AFORO, 2);
        datos.define(DATA_DENTRO, 0);
    }

    public int getAforo() {
        return entityData.get(DATA_AFORO);
    }

    public int getDentro() {
        return entityData.get(DATA_DENTRO);
    }

    /** El centro de la cupula (a media altura, para las particulas). */
    public Vec3 centro() {
        return position().add(0, RADIO * 0.5, 0);
    }

    /** Esta dentro y le toca sitio: con la cupula llena no entra nadie mas. */
    public boolean protege(LivingEntity v) {
        return dentro.contains(v.getUUID());
    }

    /** Los pies a menos de "r" del centro (en planta) y a la altura de la cupula. */
    private boolean bajo(LivingEntity v, double r) {
        double dx = v.getX() - getX();
        double dz = v.getZ() - getZ();
        return dx * dx + dz * dz <= r * r && v.getY() >= getY() - 0.5 && v.getY() <= getY() + RADIO + 0.5;
    }

    /** La cupula llena echa hacia fuera al que intenta entrar, y le dice que busque otra. */
    private void echar(ServerLevel nivel, LivingEntity v) {
        double dx = v.getX() - getX();
        double dz = v.getZ() - getZ();
        double d = Math.sqrt(dx * dx + dz * dz);
        if (d < 1.0E-3) {
            double a = random.nextDouble() * Math.PI * 2;
            dx = Math.cos(a);
            dz = Math.sin(a);
            d = 1.0;
        }
        v.setDeltaMovement(dx / d * EMPUJE, Math.max(v.getDeltaMovement().y, 0.12), dz / d * EMPUJE);
        v.hurtMarked = true;
        int ahora = tickCount;
        Integer antes = avisados.get(v.getUUID());
        if (antes == null || ahora - antes >= 15) {
            avisados.put(v.getUUID(), ahora);
            Vec3 p = position().add(dx / d * RADIO, Math.min(v.getY() - getY() + 1.0, RADIO), dz / d * RADIO);
            nivel.sendParticles(AtalayaParticulas.NEREA_ESPUMA, true, true, p.x, p.y, p.z, 10, 0.3, 0.4, 0.3, 0.05);
            nivel.playSound(null, p.x, p.y, p.z, AtalayaSonidos.NEREA_BURBUJA_POMPA, SoundSource.HOSTILE, 1.0F, 0.6F);
            if (v instanceof ServerPlayer jugador) {
                jugador.sendOverlayMessage(Component.translatable("hud.atalaya.nerea.refugio_lleno")
                        .withStyle(ChatFormatting.GOLD, ChatFormatting.BOLD));
            }
        }
    }

    @Override
    public void tick() {
        super.tick();
        if (level().isClientSide()) {
            return;
        }
        ServerLevel nivel = (ServerLevel) level();
        if (duena == null || duena.isRemoved() || duena.isDeadOrDying() || --vida <= 0) {
            reventar(nivel, false);
            return;
        }
        // Quien esta dentro: los pies bajo la cupula. Entran por orden de llegada
        // hasta llenarla; llena, se cierra y a los demas los echa (Juan, 08-10-2026:
        // "si ya se llego a un cupo que no deje pasar a otra persona").
        Vec3 c = centro();
        double muro = RADIO + 0.9;
        List<LivingEntity> cerca = nivel.getEntitiesOfClass(LivingEntity.class, new AABB(c, c).inflate(muro + 0.5, RADIO + 1.0,
                muro + 0.5), PresasJefe::presa);
        List<UUID> ahora = new ArrayList<>();
        for (LivingEntity v : cerca) {
            if (bajo(v, RADIO + 0.2)) {
                ahora.add(v.getUUID());
            }
        }
        dentro.removeIf(u -> !ahora.contains(u));
        boolean llenaAntes = dentro.size() >= getAforo();
        for (LivingEntity v : cerca) {
            if (dentro.contains(v.getUUID())) {
                continue;
            }
            if (ahora.contains(v.getUUID()) && dentro.size() < getAforo()) {
                dentro.add(v.getUUID());
                nivel.playSound(null, c.x, c.y, c.z, AtalayaSonidos.NEREA_BURBUJA_POMPA, SoundSource.HOSTILE, 1.0F, 1.2F);
            } else if (dentro.size() >= getAforo() && bajo(v, muro)) {
                echar(nivel, v);
            }
        }
        if (!llenaAntes && dentro.size() >= getAforo()) {
            // Se cierra: la pompa se endurece con un golpe sordo.
            nivel.playSound(null, c.x, c.y, c.z, AtalayaSonidos.NEREA_REFUGIO, SoundSource.HOSTILE, 1.6F, 0.7F);
            nivel.sendParticles(AtalayaParticulas.NEREA_ESPUMA, true, true, c.x, getY() + 0.1, c.z, 24, RADIO * 0.7, 0.05,
                    RADIO * 0.7, 0.04);
        }
        if (dentro.size() != getDentro()) {
            entityData.set(DATA_DENTRO, dentro.size());
            rotular();
        }
        if (tickCount % 4 == 0) {
            nivel.sendParticles(AtalayaParticulas.NEREA_BURBUJA, true, true, c.x, getY() + 0.3, c.z, 1, RADIO * 0.5, 0.1,
                    RADIO * 0.5, 0.02);
        }
    }

    /** "1/2" encima: dorado con sitio libre, rojo llena o con uno de mas. */
    private void rotular() {
        int n = Math.min(getDentro(), 99);
        int aforo = getAforo();
        ChatFormatting color = n >= aforo ? ChatFormatting.RED : ChatFormatting.GOLD;
        setCustomName(Component.literal(n + "/" + aforo).withStyle(color, ChatFormatting.BOLD));
        setCustomNameVisible(true);
    }

    /** Se acaba la Marea Alta (o la quitan): la pompa revienta en espuma. */
    public void reventar(ServerLevel nivel, boolean conSonido) {
        if (isRemoved()) {
            return;
        }
        Vec3 c = centro();
        nivel.sendParticles(AtalayaParticulas.NEREA_BURBUJA, true, true, c.x, c.y, c.z, 24, RADIO * 0.6, RADIO * 0.6, RADIO * 0.6,
                0.2);
        nivel.sendParticles(AtalayaParticulas.NEREA_GOTA, true, true, c.x, c.y, c.z, 20, RADIO * 0.6, RADIO * 0.6, RADIO * 0.6, 0.3);
        if (conSonido) {
            nivel.playSound(null, c.x, c.y, c.z, AtalayaSonidos.NEREA_BURBUJA_REVIENTA, SoundSource.HOSTILE, 1.5F, 1.4F);
        }
        discard();
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
