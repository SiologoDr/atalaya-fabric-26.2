package com.atalaya.entity;

import com.atalaya.particula.AtalayaParticulas;
import com.atalaya.sonido.AtalayaSonidos;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;
import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerLevel;
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
 * la cuenta atras, quien no este dentro de una (de los primeros en entrar, hasta
 * llenarla) revienta el totem. Encima lleva cuantos caben ("1/2"); llena se
 * pone roja.
 *
 * Hay las justas: una por cada "aforo" jugadores, repartidas por la arena. Hay
 * que repartirse: si se mete uno de mas, ese no esta a salvo.
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

    /** Esta dentro y le toca sitio (de los primeros "aforo" en entrar). */
    public boolean protege(LivingEntity v) {
        int i = dentro.indexOf(v.getUUID());
        return i >= 0 && i < getAforo();
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
        // Quien esta dentro: los pies bajo la cupula. El orden de llegada se guarda.
        Vec3 c = centro();
        List<UUID> ahora = new ArrayList<>();
        for (LivingEntity v : nivel.getEntitiesOfClass(LivingEntity.class, new AABB(c, c).inflate(RADIO + 0.5),
                PresasJefe::presa)) {
            double dx = v.getX() - getX();
            double dz = v.getZ() - getZ();
            if (dx * dx + dz * dz <= (RADIO + 0.2) * (RADIO + 0.2) && v.getY() >= getY() - 0.5 && v.getY() <= getY() + RADIO) {
                ahora.add(v.getUUID());
            }
        }
        dentro.removeIf(u -> !ahora.contains(u));
        for (UUID u : ahora) {
            if (!dentro.contains(u)) {
                dentro.add(u);
                nivel.playSound(null, c.x, c.y, c.z, AtalayaSonidos.NEREA_BURBUJA_POMPA, SoundSource.HOSTILE, 1.0F, 1.2F);
            }
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
