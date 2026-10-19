package com.atalaya.bestiario.mobs;

import com.atalaya.bestiario.BestiaEntity;
import com.atalaya.bestiario.Bestia;
import com.atalaya.bestiario.CreeperBestia;
import com.atalaya.bestiario.Fichas;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.entity.ai.goal.RandomLookAroundGoal;
import net.minecraft.world.entity.ai.goal.WaterAvoidingRandomStrollGoal;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;
import org.jspecify.annotations.Nullable;

import java.util.EnumSet;

/**
 * El Creeper Ciego (el «Creeper Warden» del DEDsafio): de sculk y sin ojos. No te ve: te OYE. Correr se oye de lejos,
 * andar un poco menos, y agachado no se te oye (salvo que lo roces); pegar, saltar o hacerle dano tambien suenan. Va a
 * donde oyo el ultimo ruido, no a donde estas: si te quedas quieto y callado, se pierde. Cuando te encuentra chilla, y la
 * mecha solo sigue encendida mientras te oye. Su estallido deja la oscuridad del sculk.
 *
 * Sale en la Oscuridad Profunda.
 */
public class CiegoEntity extends CreeperBestia {

    /** De donde oyo el ultimo ruido y hace cuantos ticks. */
    private @Nullable Vec3 oido;
    private int sinOir = 1000;
    private int ultimoChillido = -1000;

    public CiegoEntity(EntityType<? extends Monster> tipo, Level nivel) {
        super(tipo, nivel);
        mecha = 30;
        radio = 3.5F;
        alcanceMecha = 3.0;
    }

    public static AttributeSupplier.Builder atributos() {
        return Monster.createMonsterAttributes()
                .add(Attributes.MAX_HEALTH, 24.0)
                .add(Attributes.MOVEMENT_SPEED, 0.27)
                .add(Attributes.FOLLOW_RANGE, 24.0);
    }

    @Override
    public Bestia bestia() {
        return Fichas.CIEGO;
    }

    @Override
    protected void metas() {
        goalSelector.addGoal(4, new IrAlRuido());
        goalSelector.addGoal(5, new WaterAvoidingRandomStrollGoal(this, 0.7));
        goalSelector.addGoal(6, new RandomLookAroundGoal(this));
    }

    @Override
    protected void objetivos() {
        // Nada de verte: el objetivo se lo pone el oido (escuchar).
    }

    /** Lo tiene a tiro si lo esta oyendo (o lo toca). */
    @Override
    protected boolean aTiro(LivingEntity objetivo) {
        return sinOir < 20 || distanceToSqr(objetivo) < 2.0 * 2.0;
    }

    @Override
    public void tick() {
        super.tick();
        if (level() instanceof ServerLevel nivel && isAlive() && tickCount % 2 == 0) {
            escuchar(nivel);
        }
    }

    /** Lo que se oye: quien corre, anda, salta o pega (agachado, nada); de mas lejos cuanto mas ruido hace. */
    private void escuchar(ServerLevel nivel) {
        sinOir += 2;
        ServerPlayer mejor = null;
        double mejorD = Double.MAX_VALUE;
        for (ServerPlayer p : nivel.players()) {
            if (p.isSpectator() || p.isCreative() || !p.isAlive()) {
                continue;
            }
            double d = p.distanceToSqr(this);
            double alcance = com.atalaya.bestiario.Oido.alcance(p);
            if (d < 2.0 * 2.0) {
                alcance = Math.max(alcance, 2.0);
            }
            if (alcance > 0 && d < alcance * alcance && d < mejorD) {
                mejor = p;
                mejorD = d;
            }
        }
        if (mejor == null) {
            if (sinOir > 120 && getTarget() != null) {
                setTarget(null);
                oido = null;
            }
            return;
        }
        boolean nuevo = getTarget() != mejor || sinOir > 60;
        oido = mejor.position();
        sinOir = 0;
        setTarget(mejor);
        if (nuevo && tickCount - ultimoChillido > 60) {
            ultimoChillido = tickCount;
            animar(EV_ESPECIAL2);
            sonar("escucha", 1.2F);
            luego(8, () -> sonar("chillido", 1.6F));
            particulas(nivel, "vibracion", getX(), getY() + 2.0, getZ(), 6, 0.3, 0.2, 0.05);
        }
    }

    @Override
    public boolean hurtServer(ServerLevel nivel, DamageSource fuente, float dano) {
        boolean herido = super.hurtServer(nivel, fuente, dano);
        // Quien le pega se oye.
        if (herido && fuente.getEntity() instanceof ServerPlayer p && !p.isCreative()) {
            oido = p.position();
            sinOir = 0;
            setTarget(p);
        }
        return herido;
    }

    /** Va a donde oyo el ruido (no a donde esta el jugador). */
    private final class IrAlRuido extends Goal {
        IrAlRuido() {
            setFlags(EnumSet.of(Flag.MOVE, Flag.LOOK));
        }

        @Override
        public boolean canUse() {
            return oido != null && position().distanceToSqr(oido) > 1.5 * 1.5;
        }

        @Override
        public boolean canContinueToUse() {
            return oido != null && position().distanceToSqr(oido) > 1.2 * 1.2 && sinOir < 140;
        }

        @Override
        public void tick() {
            if (oido != null && tickCount % 5 == 0) {
                getNavigation().moveTo(oido.x, oido.y, oido.z, sinOir < 20 ? 1.2 : 0.9);
                getLookControl().setLookAt(oido.x, oido.y + 1.0, oido.z);
            }
        }

        @Override
        public void stop() {
            getNavigation().stop();
        }
    }

    @Override
    protected void alEstallar(ServerLevel nivel) {
        particulas(nivel, "sculk", getX(), getY() + 1.0, getZ(), 40, 1.2, 0.8, 0.35);
        particulas(nivel, "vibracion", getX(), getY() + 1.0, getZ(), 40, 1.6, 1.0, 0.2);
        for (ServerPlayer p : nivel.players()) {
            if (!p.isSpectator() && !p.isCreative() && p.distanceToSqr(this) < 10 * 10) {
                BestiaEntity.efecto(p, MobEffects.DARKNESS, 240, 0, this);
            }
        }
    }
}
