package com.atalaya.bestiario;

import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.goal.FloatGoal;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.entity.ai.goal.target.HurtByTargetGoal;
import net.minecraft.world.entity.ai.goal.LookAtPlayerGoal;
import net.minecraft.world.entity.ai.goal.MeleeAttackGoal;
import net.minecraft.world.entity.ai.goal.RandomLookAroundGoal;
import net.minecraft.world.entity.ai.goal.WaterAvoidingRandomStrollGoal;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;

import java.util.EnumSet;

/**
 * La base de los creepers del bestiario: como el creeper de siempre (se acerca, se le enciende la mecha cuando te tiene
 * a tiro, se hincha y revienta; si te alejas a tiempo, se le apaga), con su mecha, su radio y lo suyo al estallar
 * (alEstallar). Lo hinchado va en el valor de la Bestia (de 0 a 1): el render lo hincha y lo hace parpadear en blanco.
 * Muere con su animacion si lo matan antes; si estalla, desaparece en el estallido.
 *
 * Cada uno cambia lo que necesita: lo que hace mientras no esta encendido (metas), a quien persigue (objetivos), cuando
 * lo tiene a tiro (aTiro: el Ciego no ve, oye) y lo que pasa al encenderse y al estallar.
 */
public abstract class CreeperBestia extends BestiaEntity implements ConMecha {

    /** Los ticks de la mecha. */
    protected int mecha = 30;
    /** El radio de la explosion. */
    protected float radio = 3.0F;
    /** Si su estallido prende fuego alrededor. */
    protected boolean fuego;
    /** A que distancia se le enciende la mecha (bloques). */
    protected double alcanceMecha = 3.0;
    private int hinchado;
    private int direccion = -1;
    /** Los ticks en que no se le puede encender la mecha (se la han apagado del todo). */
    private int sinMecha;

    protected CreeperBestia(EntityType<? extends Monster> tipo, Level nivel) {
        super(tipo, nivel);
    }

    @Override
    protected void registerGoals() {
        goalSelector.addGoal(1, new FloatGoal(this));
        goalSelector.addGoal(2, new Mecha());
        metas();
        objetivos();
    }

    /** Lo que hace cuando no esta encendido: como el creeper, ir a por ti, pasear y mirar. */
    protected void metas() {
        goalSelector.addGoal(4, new MeleeAttackGoal(this, 1.0, false));
        goalSelector.addGoal(5, new WaterAvoidingRandomStrollGoal(this, 0.8));
        goalSelector.addGoal(6, new LookAtPlayerGoal(this, Player.class, 8.0F));
        goalSelector.addGoal(6, new RandomLookAroundGoal(this));
    }

    /** A quien persigue: al jugador que ve y a quien le pega. */
    protected void objetivos() {
        targetSelector.addGoal(1, new NearestAttackableTargetGoal<>(this, Player.class, true));
        targetSelector.addGoal(2, new HurtByTargetGoal(this));
    }

    /** Si lo tiene a tiro para seguir con la mecha encendida (el de siempre: si lo ve). */
    protected boolean aTiro(LivingEntity objetivo) {
        return getSensing().hasLineOfSight(objetivo);
    }

    /** Si la mecha esta encendida (o se le esta apagando). */
    public boolean encendido() {
        return hinchado > 0;
    }

    /** Lo enciende ya (un mechero, un rayo, otro estallido...). */
    public void encender() {
        direccion = 1;
    }

    /** Se la apaga (deja de hincharse y se deshincha poco a poco). */
    protected void apagar() {
        direccion = -1;
    }

    /** Se la apaga del todo y no se le vuelve a encender en esos ticks (el jugador que se le escapa de las lianas). */
    protected void desactivar(int ticks) {
        direccion = -1;
        hinchado = 0;
        sinMecha = ticks;
        setValor(0.0F);
    }

    /** Lo que pasa al encenderse la mecha (una vez): su sonido y su animacion. */
    protected void alEncender() {
        sonar("mecha", 1.0F, 0.9F + random.nextFloat() * 0.2F);
        animar(EV_ESPECIAL);
    }

    @Override
    public void tick() {
        if (isAlive() && !level().isClientSide()) {
            if (sinMecha > 0) {
                sinMecha--;
                direccion = -1;
            }
            if (direccion > 0 && hinchado == 0) {
                alEncender();
            }
            hinchado = Math.max(0, Math.min(mecha, hinchado + direccion));
            setValor(hinchado / (float) mecha);
            if (hinchado >= mecha) {
                estallar();
            }
        }
        super.tick();
    }

    /** Revienta: la explosion (con su radio), lo suyo y fuera. */
    protected void estallar() {
        if (!(level() instanceof ServerLevel nivel) || isRemoved()) {
            return;
        }
        dead = true;
        String particula = bestia().particulaMuerte != null ? bestia().particulaMuerte : "";
        estallido(nivel, this, bestia(), getX(), getY(), getZ(), radio, fuego, particula, "estalla");
        alEstallar(nivel);
        discard();
    }

    /** Lo de cada uno al estallar (la lava, el wither, la nata...). */
    protected void alEstallar(ServerLevel nivel) {
    }

    /** Si el juego deja a los mobs romper y poner bloques (la lava, las rosas...). */
    protected boolean puedeTocarElMundo(ServerLevel nivel) {
        return nivel.getGameRules().get(net.minecraft.world.level.gamerules.GameRules.MOB_GRIEFING);
    }

    /** La mecha: con su presa a tiro, se enciende; si se aleja (o deja de tenerla a tiro), se apaga. */
    private final class Mecha extends Goal {
        Mecha() {
            setFlags(EnumSet.of(Flag.MOVE));
        }

        @Override
        public boolean canUse() {
            LivingEntity t = getTarget();
            return sinMecha <= 0 && (hinchado > 0 || (t != null && distanceToSqr(t) < alcanceMecha * alcanceMecha && aTiro(t)));
        }

        @Override
        public void start() {
            getNavigation().stop();
        }

        @Override
        public void stop() {
            direccion = -1;
        }

        @Override
        public boolean requiresUpdateEveryTick() {
            return true;
        }

        @Override
        public void tick() {
            LivingEntity t = getTarget();
            if (t == null || distanceToSqr(t) > (alcanceMecha + 4.0) * (alcanceMecha + 4.0) || !aTiro(t)) {
                direccion = -1;
            } else {
                direccion = 1;
            }
        }
    }
}
