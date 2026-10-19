package com.atalaya.bestiario.mobs;

import com.atalaya.bestiario.Bestia;
import com.atalaya.bestiario.Bestiario;
import com.atalaya.bestiario.CreeperBestia;
import com.atalaya.bestiario.Fichas;
import com.atalaya.net.AtalayaRed;
import com.atalaya.radiation.RadiationManager;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerTickEvents;
import net.fabricmc.fabric.api.networking.v1.ServerPlayNetworking;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.EntitySpawnReason;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;

/**
 * El Creeper Atomico (el «Creeper Nuclear» del DEDsafio): grande, lento y acorazado. Su mecha es una sirena de tres
 * segundos que se oye desde lejos (da tiempo a correr), y su estallido arrasa: un crater enorme, un destello que ciega a
 * quien lo mira y una onda expansiva que llega a cuarenta bloques, te tira lejos y te deja la lluvia radiactiva (la
 * Radiacion, mas fuerte cuanto mas cerca). La onda solo se para con un escudo bien puesto hacia el estallido, y el
 * escudo no sobrevive.
 *
 * Sale en los biomas nevados y en el techo del Nether (por encima de la roca madre, donde no sale nada). Alli arriba es
 * peor: te encuentra a traves de las paredes y rompe lo que se le ponga delante para llegar hasta ti.
 */
public class AtomicoEntity extends CreeperBestia {

    private static final double ALCANCE_ONDA = 40.0;

    public AtomicoEntity(EntityType<? extends Monster> tipo, Level nivel) {
        super(tipo, nivel);
        mecha = 60;
        radio = 9.0F;
        alcanceMecha = 3.5;
    }

    public static AttributeSupplier.Builder atributos() {
        return Monster.createMonsterAttributes()
                .add(Attributes.MAX_HEALTH, 40.0)
                .add(Attributes.MOVEMENT_SPEED, 0.21)
                .add(Attributes.ARMOR, 8.0)
                .add(Attributes.KNOCKBACK_RESISTANCE, 0.8)
                .add(Attributes.FOLLOW_RANGE, 28.0);
    }

    @Override
    public Bestia bestia() {
        return Fichas.ATOMICO;
    }

    /** Si esta en el techo del Nether (alli ve a traves de las paredes y rompe lo que se le ponga delante). */
    private boolean enElTecho() {
        return level().dimension() == Level.NETHER && getY() >= 127.0;
    }

    @Override
    protected void objetivos() {
        super.objetivos();
        targetSelector.addGoal(1, new NearestAttackableTargetGoal<>(this, Player.class, 10, false, false,
                (t, nivel) -> enElTecho()));
    }

    @Override
    protected boolean aTiro(LivingEntity objetivo) {
        return enElTecho() || super.aTiro(objetivo);
    }

    /** En el techo, si algo le corta el paso hacia su presa, lo rompe (a la altura de los pies, del pecho y de la cabeza). */
    private void abrirPaso(ServerLevel nivel) {
        LivingEntity t = presa();
        if (t == null || !(horizontalCollision || getNavigation().isDone())) {
            return;
        }
        Direction d = Direction.getApproximateNearest(t.getX() - getX(), 0.0, t.getZ() - getZ());
        BlockPos delante = blockPosition().relative(d);
        for (int dy = 0; dy < 3; dy++) {
            BlockPos p = delante.above(dy);
            BlockState b = nivel.getBlockState(p);
            if (!b.isAir() && b.getDestroySpeed(nivel, p) >= 0 && !b.is(Blocks.BEDROCK)) {
                nivel.destroyBlock(p, true, this);
            }
        }
    }

    @Override
    protected void alEncender() {
        // La sirena se oye lejos (el volumen alto es el alcance).
        sonar("mecha", 4.0F, 1.0F);
        animar(EV_ESPECIAL);
    }

    @Override
    public void tick() {
        super.tick();
        if (level() instanceof ServerLevel nivel && isAlive()) {
            if (enElTecho() && tickCount % 10 == 0 && !encendido() && puedeTocarElMundo(nivel)) {
                abrirPaso(nivel);
            }
            if (encendido() && tickCount % 3 == 0) {
                particulas(nivel, "radiacion", getX(), getY() + 1.2, getZ(), 4, 0.6, 0.8, 0.05);
            } else if (tickCount % 20 == 0) {
                particulas(nivel, "radiacion", getX(), getY() + 1.4, getZ(), 1, 0.4, 0.4, 0.01);
            }
        }
    }

    @Override
    protected void alEstallar(ServerLevel nivel) {
        Vec3 c = position();
        // La seta: la columna, el sombrero y el anillo del suelo.
        for (int i = 0; i < 28; i++) {
            particulas(nivel, "radiacion", c.x, c.y + i * 0.55, c.z, 6, 0.5 + i * 0.02, 0.2, 0.6 + i * 0.02);
        }
        particulas(nivel, "radiacion", c.x, c.y + 16, c.z, 120, 4.5, 1.0, 0.05);
        particulas(nivel, "radiacion", c.x, c.y + 0.5, c.z, 90, 6.0, 0.2, 0.5);
        particulas(nivel, "chapa", c.x, c.y + 1.0, c.z, 40, 1.5, 1.0, 0.6);
        SoundEvent onda = bestia().sonido("onda");
        for (ServerPlayer p : nivel.players()) {
            double d = p.position().distanceTo(c);
            if (d < 72 && ServerPlayNetworking.canSend(p, AtalayaRed.Deslumbre.TIPO)) {
                ServerPlayNetworking.send(p, new AtalayaRed.Deslumbre(d < 24 ? 8 : 3, d < 24 ? 50 : 30));
            }
            if (p.isCreative() || p.isSpectator() || d > ALCANCE_ONDA) {
                continue;
            }
            float k = (float) (1.0 - d / ALCANCE_ONDA);
            if (onda != null) {
                nivel.playSound(null, p.getX(), p.getY(), p.getZ(), onda, SoundSource.HOSTILE, 1.0F + k, 1.0F);
            }
            Vec3 haciaEstallido = c.subtract(p.position()).normalize();
            boolean escudo = p.isBlocking() && p.getViewVector(1.0F).dot(haciaEstallido) > 0.3;
            float dano;
            if (escudo) {
                ItemStack s = p.getUseItem();
                s.hurtAndBreak(s.getMaxDamage(), p, p.getUsedItemHand());
                p.stopUsingItem();
                dano = 4.0F * k;
            } else {
                dano = 6.0F + 30.0F * k;
            }
            p.hurtServer(nivel, nivel.damageSources().explosion(this, this), dano);
            Vec3 lejos = haciaEstallido.scale(-1);
            p.setDeltaMovement(p.getDeltaMovement().add(lejos.x * (0.4 + 1.6 * k), 0.25 + 0.5 * k, lejos.z * (0.4 + 1.6 * k)));
            p.hurtMarked = true;
            int nivelRadiacion = d < 10 ? 3 : d < 20 ? 2 : d < 30 ? 1 : 0;
            RadiationManager.lluvia(p, nivelRadiacion, 600 + (int) (900 * k));
        }
    }

    // ------------------------------------------------------------------
    //  El techo del Nether: alli no sale nada (es roca madre), asi que se le saca a mano
    // ------------------------------------------------------------------

    public static void registrarEventos() {
        ServerTickEvents.END_SERVER_TICK.register(AtomicoEntity::techo);
    }

    private static void techo(MinecraftServer servidor) {
        if (servidor.getTickCount() % 400 != 0 || !Bestiario.suelto(servidor, Fichas.ATOMICO)) {
            return;
        }
        ServerLevel nether = servidor.getLevel(Level.NETHER);
        if (nether == null) {
            return;
        }
        for (ServerPlayer p : nether.players()) {
            if (p.isCreative() || p.isSpectator() || p.getY() < 128 || nether.getRandom().nextFloat() > 0.35F) {
                continue;
            }
            if (!nether.getEntitiesOfClass(AtomicoEntity.class, p.getBoundingBox().inflate(64)).isEmpty()) {
                continue;
            }
            for (int intento = 0; intento < 8; intento++) {
                double a = nether.getRandom().nextDouble() * Math.PI * 2;
                double r = 14 + nether.getRandom().nextDouble() * 12;
                BlockPos pos = BlockPos.containing(p.getX() + Math.cos(a) * r, 128, p.getZ() + Math.sin(a) * r);
                if (nether.getBlockState(pos.below()).isSolid() && nether.getBlockState(pos).isAir()
                        && nether.getBlockState(pos.above()).isAir() && nether.getBlockState(pos.above(2)).isAir()) {
                    AtomicoEntity e = (AtomicoEntity) Fichas.ATOMICO.tipo.create(nether, EntitySpawnReason.NATURAL);
                    if (e != null) {
                        e.snapTo(pos.getX() + 0.5, pos.getY(), pos.getZ() + 0.5, nether.getRandom().nextFloat() * 360.0F, 0.0F);
                        nether.addFreshEntity(e);
                    }
                    break;
                }
            }
        }
    }
}
