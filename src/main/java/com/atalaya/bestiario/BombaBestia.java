package com.atalaya.bestiario;

import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.util.RandomSource;
import net.minecraft.world.Difficulty;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.EntitySpawnReason;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.control.FlyingMoveControl;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.entity.ai.goal.LookAtPlayerGoal;
import net.minecraft.world.entity.ai.goal.target.HurtByTargetGoal;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.ai.navigation.FlyingPathNavigation;
import net.minecraft.world.entity.ai.navigation.PathNavigation;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.ServerLevelAccessor;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.Vec3;

import java.util.EnumSet;

/**
 * La base de las bombas voladoras del bestiario: vuelan siempre (no caen ni se hacen dano al caer), te ven desde lejos,
 * van a por ti y, en cuanto te tienen encima, se les enciende la mecha (un segundo) sin dejar de seguirte: se te ponen
 * sobre la cabeza y revientan. Si no tienen a nadie, revolotean por la zona. Su estallido es el de su ficha (sin humo ni
 * sonido de vanilla) y lo suyo (alEstallar).
 */
public abstract class BombaBestia extends BestiaEntity implements ConMecha {

    /** Los ticks de la mecha. */
    protected int mecha = 20;
    /** El radio de la explosion. */
    protected float radio = 3.0F;
    /** Si su estallido prende fuego alrededor. */
    protected boolean fuego;
    /** A que distancia se le enciende la mecha (bloques). */
    protected double alcanceMecha = 2.4;
    /** Lo que lleva encendida (-1: apagada). */
    private int encendida = -1;

    protected BombaBestia(EntityType<? extends Monster> tipo, Level nivel) {
        super(tipo, nivel);
        this.moveControl = new FlyingMoveControl(this, 20, true);
        setNoGravity(true);
    }

    /** Sale en el aire o donde sea, con oscuridad (de noche o bajo tierra). */
    public static boolean enLaOscuridad(EntityType<?> tipo, ServerLevelAccessor nivel, EntitySpawnReason motivo,
                                        BlockPos pos, RandomSource azar) {
        return nivel.getDifficulty() != Difficulty.PEACEFUL && Monster.isDarkEnoughToSpawn(nivel, pos, azar);
    }

    @Override
    protected PathNavigation createNavigation(Level nivel) {
        return new FlyingPathNavigation(this, nivel);
    }

    @Override
    protected void registerGoals() {
        goalSelector.addGoal(1, new Perseguir());
        goalSelector.addGoal(5, new Revolotear());
        goalSelector.addGoal(6, new LookAtPlayerGoal(this, Player.class, 16.0F));
        objetivos();
    }

    /** A quien persigue: al jugador que ve (desde lejos: FOLLOW_RANGE) y a quien le pega. */
    protected void objetivos() {
        targetSelector.addGoal(1, new NearestAttackableTargetGoal<>(this, Player.class, true));
        targetSelector.addGoal(2, new HurtByTargetGoal(this));
    }

    /** Si lo tiene a tiro para encender la mecha (por defecto, si lo ve). */
    protected boolean aTiro(LivingEntity objetivo) {
        return getSensing().hasLineOfSight(objetivo);
    }

    public boolean encendida() {
        return encendida >= 0;
    }

    /** Lo que pasa al encenderse la mecha (una vez): su sonido y su animacion. */
    protected void alEncender() {
        sonar("mecha", 1.2F, 0.95F + random.nextFloat() * 0.1F);
        animar(EV_ESPECIAL);
    }

    @Override
    public void tick() {
        super.tick();
        if (!(level() instanceof ServerLevel nivel) || !isAlive()) {
            return;
        }
        LivingEntity t = presa();
        if (encendida < 0 && t != null && distanceToSqr(t) < alcanceMecha * alcanceMecha && aTiro(t)) {
            encendida = 0;
            alEncender();
        }
        if (encendida >= 0) {
            encendida++;
            setValor(encendida / (float) mecha);
            if (encendida >= mecha) {
                estallar(nivel);
            }
        }
    }

    /** Revienta: la explosion de su ficha, lo suyo y fuera. */
    protected void estallar(ServerLevel nivel) {
        if (isRemoved()) {
            return;
        }
        dead = true;
        String particula = bestia().particulaMuerte != null ? bestia().particulaMuerte : "";
        estallido(nivel, this, bestia(), getX(), getY() + getBbHeight() * 0.5, getZ(), radio, fuego, particula, "estalla");
        alEstallar(nivel);
        discard();
    }

    /** Lo de cada una al estallar (secar el agua, prender fuego, la oscuridad...). */
    protected void alEstallar(ServerLevel nivel) {
    }

    /** Vuela como la abeja (lo de siempre, en el aire, va frenadisimo: la velocidad de vuelo de los mobs es casi cero). */
    @Override
    public void travel(Vec3 entrada) {
        travelFlying(entrada, getSpeed());
    }

    @Override
    public boolean causeFallDamage(double distancia, float multiplicador, DamageSource fuente) {
        return false;
    }

    @Override
    protected void checkFallDamage(double y, boolean enSuelo, BlockState estado, BlockPos pos) {
    }

    /** Ir a por la presa: a la altura de sus ojos y, con la mecha encendida, encima de su cabeza. */
    private final class Perseguir extends Goal {
        Perseguir() {
            setFlags(EnumSet.of(Flag.MOVE, Flag.LOOK));
        }

        @Override
        public boolean canUse() {
            return presa() != null;
        }

        @Override
        public void tick() {
            LivingEntity t = presa();
            if (t == null) {
                return;
            }
            double y = encendida >= 0 ? t.getY() + t.getBbHeight() + 0.4 : t.getEyeY() + 0.4;
            Vec3 meta = new Vec3(t.getX(), y, t.getZ());
            Vec3 falta = meta.subtract(position());
            if (falta.length() < 4.5) {
                // La recta final, directa y sin pasarse: se le pega encima.
                Vec3 v = falta.scale(0.3);
                if (v.length() > 0.55) {
                    v = v.normalize().scale(0.55);
                }
                setDeltaMovement(v);
            } else {
                getMoveControl().setWantedPosition(meta.x, meta.y, meta.z, encendida >= 0 ? 1.4 : 1.0);
            }
            getLookControl().setLookAt(t, 30.0F, 30.0F);
        }
    }

    /** Revolotear por la zona cuando no tiene a nadie: un punto al azar cerca, en el aire libre. */
    private final class Revolotear extends Goal {
        Revolotear() {
            setFlags(EnumSet.of(Flag.MOVE));
        }

        @Override
        public boolean canUse() {
            return presa() == null && !getMoveControl().hasWanted() && random.nextInt(20) == 0;
        }

        @Override
        public boolean canContinueToUse() {
            return false;
        }

        @Override
        public void start() {
            for (int i = 0; i < 4; i++) {
                Vec3 p = position().add((random.nextDouble() - 0.5) * 14.0, (random.nextDouble() - 0.5) * 6.0,
                        (random.nextDouble() - 0.5) * 14.0);
                if (level().isEmptyBlock(BlockPos.containing(p))) {
                    getMoveControl().setWantedPosition(p.x, p.y, p.z, 0.6);
                    return;
                }
            }
        }
    }
}
