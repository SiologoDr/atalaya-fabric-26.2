package com.atalaya.entity;

import com.atalaya.item.AtalayaItems;
import com.atalaya.particula.AtalayaParticulas;
import com.atalaya.sonido.AtalayaSonidos;
import java.util.UUID;
import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.projectile.ThrowableProjectile;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.Vec3;
import org.jspecify.annotations.Nullable;

/**
 * El corcho de la Cana del Abismo (la Pesca del Abismo de Nerea, octubre de
 * 2026). Se lanza en arco; si cae en una poza (PozaAbismoEntity), espera un
 * rato y pica UNA vez: se hunde a tirones y le sale un aro dorado que se va
 * cerrando sobre el corcho durante un segundo (Juan: "asi se mide la agilidad").
 * Si se recoge mientras pica, sale una Perla del Abismo; si no, se escapa y hay
 * que recoger y volver a lanzar. Si se recoge antes de que pique, salta una
 * morena de la poza y muerde. Fuera de una poza no pica nunca.
 */
public class CorchoAbismoEntity extends ThrowableProjectile {

    public static final int VUELA = 0;
    public static final int FLOTA = 1;
    public static final int ESPERA = 2;
    public static final int PICA = 3;
    /** Ha picado y nadie recogio a tiempo: ya no pica mas (hay que volver a lanzar). */
    public static final int ESCAPO = 4;
    /** Lo que dura la picada (ticks): un segundo para recoger. */
    public static final int PICADA = 20;
    /** Lo que muerde la morena si recoges a destiempo (pasa la armadura). */
    public static final float[] DANO_MORDISCO = {6, 8, 9, 11};

    private static final EntityDataAccessor<Integer> DATA_ESTADO =
            SynchedEntityData.defineId(CorchoAbismoEntity.class, EntityDataSerializers.INT);

    private @Nullable NereaEntity duena;
    private @Nullable UUID lanzador;
    private int reloj;
    private int vida;
    /** En el cliente: el tick en que empezo a picar (para cerrar el aro). */
    private int inicioPica = -100;
    /** Solo pruebas (/atalaya nerea cana_auto): recoge solo en cuanto pica. */
    boolean autoRecoger;

    public CorchoAbismoEntity(EntityType<? extends CorchoAbismoEntity> tipo, Level nivel) {
        super(tipo, nivel);
    }

    static CorchoAbismoEntity lanzar(ServerLevel nivel, Player p, NereaEntity duena) {
        CorchoAbismoEntity c = new CorchoAbismoEntity(AtalayaEntities.CORCHO_ABISMO, nivel);
        c.duena = duena;
        c.lanzador = p.getUUID();
        c.setOwner(p);
        Vec3 ojo = p.getEyePosition();
        Vec3 mira = p.getLookAngle();
        c.setPos(ojo.x + mira.x * 0.6, ojo.y - 0.2 + mira.y * 0.6, ojo.z + mira.z * 0.6);
        c.shootFromRotation(p, p.getXRot(), p.getYRot(), 0.0F, 1.15F, 1.0F);
        nivel.addFreshEntity(c);
        MinijuegosNerea.ponerCorcho(p, c);
        nivel.playSound(null, p.getX(), p.getY(), p.getZ(), AtalayaSonidos.NEREA_PESCA_LANZAR, SoundSource.PLAYERS, 1.0F, 1.0F);
        return c;
    }

    @Override
    protected void defineSynchedData(SynchedEntityData.Builder datos) {
        datos.define(DATA_ESTADO, VUELA);
    }

    public int getEstado() {
        return entityData.get(DATA_ESTADO);
    }

    /** En el cliente: cuanto lleva picando, de 0 a 1 (el aro se cierra con esto). */
    public float picada(float parcial) {
        return Math.clamp((tickCount + parcial - inicioPica) / PICADA, 0.0F, 1.0F);
    }

    @Override
    public void onSyncedDataUpdated(EntityDataAccessor<?> dato) {
        super.onSyncedDataUpdated(dato);
        if (DATA_ESTADO.equals(dato) && getEstado() == PICA) {
            inicioPica = tickCount;
        }
    }

    @Override
    protected double getDefaultGravity() {
        return 0.04;
    }

    @Override
    public void tick() {
        int e = getEstado();
        if (e == VUELA) {
            super.tick();
        } else {
            baseTick();
            setDeltaMovement(Vec3.ZERO);
        }
        if (level().isClientSide()) {
            if (e == PICA && tickCount % 2 == 0) {
                level().addParticle(AtalayaParticulas.NEREA_ESPUMA, getX() + (random.nextDouble() - 0.5) * 0.6, getY() + 0.1,
                        getZ() + (random.nextDouble() - 0.5) * 0.6, 0, 0.12, 0);
            }
            return;
        }
        ServerLevel nivel = (ServerLevel) level();
        Entity duenoCana = getOwner();
        if (++vida > 600 || duena == null || duena.isRemoved() || duena.minijuego() != MinijuegosNerea.PESCA
                || !(duenoCana instanceof Player p) || !p.isAlive() || p.distanceToSqr(this) > 40 * 40) {
            quitar();
            return;
        }
        if (e == ESPERA && --reloj <= 0) {
            entityData.set(DATA_ESTADO, PICA);
            reloj = PICADA;
            if (autoRecoger && duenoCana instanceof Player pp) {
                recoger(nivel, pp);
                return;
            }
            nivel.playSound(null, getX(), getY(), getZ(), AtalayaSonidos.NEREA_PESCA_PICA, SoundSource.PLAYERS, 1.6F, 1.0F);
            nivel.sendParticles(AtalayaParticulas.NEREA_GOTA, true, true, getX(), getY() + 0.2, getZ(), 10, 0.2, 0.1, 0.2, 0.15);
        } else if (e == PICA && --reloj <= 0) {
            // Nadie ha recogido a tiempo: se escapa y ya no vuelve a picar.
            entityData.set(DATA_ESTADO, ESCAPO);
            nivel.playSound(null, getX(), getY(), getZ(), AtalayaSonidos.NEREA_PESCA_ESCAPA, SoundSource.PLAYERS, 1.0F, 1.0F);
            nivel.sendParticles(AtalayaParticulas.NEREA_BURBUJA, true, true, getX(), getY() + 0.1, getZ(), 8, 0.2, 0.05, 0.2, 0.0);
            p.sendOverlayMessage(Component.translatable("hud.atalaya.nerea.pesca_escapa").withStyle(ChatFormatting.GRAY));
        }
    }

    @Override
    protected boolean canHitEntity(Entity e) {
        return false;
    }

    @Override
    protected void onHitBlock(BlockHitResult golpe) {
        if (!(level() instanceof ServerLevel nivel)) {
            return;
        }
        Vec3 p = golpe.getLocation();
        setPos(p.x, p.y + 0.05, p.z);
        setDeltaMovement(Vec3.ZERO);
        setNoGravity(true);
        if (duena != null && duena.pozaEn(p) != null) {
            entityData.set(DATA_ESTADO, ESPERA);
            reloj = 25 + random.nextInt(45);
            nivel.playSound(null, p.x, p.y, p.z, AtalayaSonidos.NEREA_PESCA_CAE, SoundSource.PLAYERS, 1.0F, 1.0F);
            nivel.sendParticles(AtalayaParticulas.NEREA_GOTA, true, true, p.x, p.y + 0.1, p.z, 6, 0.15, 0.05, 0.15, 0.1);
        } else {
            entityData.set(DATA_ESTADO, FLOTA);
        }
    }

    /**
     * Lo recoge su pescador: perla si picaba; si estaba en la poza esperando,
     * salta una morena (MorenaSaltoEntity) que muerde; si no, nada.
     */
    void recoger(ServerLevel nivel, Player p) {
        int e = getEstado();
        NereaEntity n = duena;
        nivel.playSound(null, p.getX(), p.getY(), p.getZ(), AtalayaSonidos.NEREA_PESCA_RECOGER, SoundSource.PLAYERS, 1.0F, 1.0F);
        if (e == PICA && n != null) {
            MinijuegosNerea.dar(p, MinijuegosNerea.crear(n, AtalayaItems.PERLA_ABISMO));
            nivel.playSound(null, p.getX(), p.getY(), p.getZ(), AtalayaSonidos.NEREA_PERLA_PESCADA, SoundSource.PLAYERS, 1.4F, 1.0F);
            nivel.sendParticles(AtalayaParticulas.NEREA_BURBUJA, true, true, getX(), getY() + 0.3, getZ(), 14, 0.3, 0.3, 0.3, 0.1);
            p.sendOverlayMessage(Component.translatable("hud.atalaya.nerea.perla_pescada").withStyle(ChatFormatting.AQUA));
        } else if (e == ESPERA && n != null) {
            MorenaSaltoEntity.saltar(nivel, n, position(), p, n.dano(DANO_MORDISCO));
            p.sendOverlayMessage(Component.translatable("hud.atalaya.nerea.pesca_morena").withStyle(ChatFormatting.RED));
        }
        quitar();
    }

    private void quitar() {
        if (lanzador != null) {
            MinijuegosNerea.quitarCorcho(lanzador, this);
        }
        discard();
    }

    @Override
    public boolean shouldBeSaved() {
        return false;
    }
}
