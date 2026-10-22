package com.atalaya.bestiario.mobs;

import com.atalaya.bestiario.Bestia;
import com.atalaya.bestiario.BestiaEntity;
import com.atalaya.bestiario.Fichas;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.tags.BlockTags;
import net.minecraft.tags.DamageTypeTags;
import net.minecraft.util.Mth;
import net.minecraft.world.DifficultyInstance;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityDimensions;
import net.minecraft.world.entity.EntitySpawnReason;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.SpawnGroupData;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.control.FlyingMoveControl;
import net.minecraft.world.entity.ai.goal.FloatGoal;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.entity.ai.goal.LookAtPlayerGoal;
import net.minecraft.world.entity.ai.goal.MeleeAttackGoal;
import net.minecraft.world.entity.ai.goal.RandomLookAroundGoal;
import net.minecraft.world.entity.ai.goal.RandomStrollGoal;
import net.minecraft.world.entity.ai.goal.WaterAvoidingRandomStrollGoal;
import net.minecraft.world.entity.ai.goal.target.HurtByTargetGoal;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.ai.navigation.FlyingPathNavigation;
import net.minecraft.world.entity.ai.navigation.PathNavigation;
import net.minecraft.world.entity.ai.navigation.WallClimberNavigation;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.ServerLevelAccessor;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.gamerules.GameRules;
import net.minecraft.world.level.storage.ValueInput;
import net.minecraft.world.level.storage.ValueOutput;
import net.minecraft.world.phys.Vec3;
import org.jspecify.annotations.Nullable;

import java.util.EnumSet;
import java.util.List;
import java.util.UUID;

/**
 * Los reptiles del bestiario (DEDsafio 2 y 4), con lo que dice de cada uno su cartel:
 *
 * <pre>
 *   Salvaje      cuerpo a cuerpo: zarpazos con sus garras de hueso, que empujan
 *   Guerrero     cuerpo a cuerpo; su golpe deja Veneno Primitivo (veneno II, ocho segundos)
 *   Rojo         el depredador de fuerza brutal: su mordisco quita muchisimo. En manada
 *   Azul         el depredador velocisimo: muerde menos, pero corre muchisimo. En manada
 *   Plumosaurio  el coloso pacifico: no ataca a nadie, pero si le pegas se revuelve y su golpe hace muchisimo dano y
 *                te lanza por los aires; a los treinta segundos sin que le peguen, se calma
 *   Molusco      Molusco Rocoso: lento, ataca al que se le acerca; si te alejas demasiado, se entierra (solo asoman
 *                las puntas de sus prismas y no se le puede herir), te sigue bajo tierra mas deprisa y sale debajo de
 *                ti de un mordisco que te lanza hacia arriba
 * </pre>
 *
 * La manada de los dromoraptores: cada uno que sale (de su huevo, de un comando...) trae dos mas de los suyos; cuando
 * uno ve una presa, se la dice a los de su manada que esten cerca y sin presa; y sin presa, los que se quedan atras
 * van a donde esta el que guia (el mas antiguo de los cercanos).
 */
public final class Reptiles {

    private Reptiles() {
    }

    private static AttributeSupplier.Builder base(double vida, double velocidad, double dano) {
        return Monster.createMonsterAttributes()
                .add(Attributes.MAX_HEALTH, vida)
                .add(Attributes.MOVEMENT_SPEED, velocidad)
                .add(Attributes.ATTACK_DAMAGE, dano)
                .add(Attributes.FOLLOW_RANGE, 32.0);
    }

    // ------------------------------------------------------------------
    //  La base: los que atacan cuerpo a cuerpo
    // ------------------------------------------------------------------

    public abstract static class Reptil extends BestiaEntity {

        protected Reptil(EntityType<? extends Monster> tipo, Level nivel) {
            super(tipo, nivel);
        }

        @Override
        protected void registerGoals() {
            goalSelector.addGoal(1, new FloatGoal(this));
            goalSelector.addGoal(4, new MeleeAttackGoal(this, velocidadAtaque(), true));
            metas();
            goalSelector.addGoal(6, new WaterAvoidingRandomStrollGoal(this, 0.8));
            goalSelector.addGoal(7, new LookAtPlayerGoal(this, Player.class, 10.0F));
            goalSelector.addGoal(7, new RandomLookAroundGoal(this));
            presas();
        }

        protected double velocidadAtaque() {
            return 1.15;
        }

        /** Metas de mas (la manada). */
        protected void metas() {
        }

        /** A quien ataca: al que le pega y, de los que se ven, a los jugadores. */
        protected void presas() {
            targetSelector.addGoal(1, new HurtByTargetGoal(this).setAlertOthers());
            targetSelector.addGoal(2, new NearestAttackableTargetGoal<>(this, Player.class, true));
        }

        /** El nombre del sonido de su golpe. */
        protected abstract String sonidoGolpe();

        @Override
        public boolean doHurtTarget(ServerLevel nivel, Entity objetivo) {
            animar(EV_ATAQUE);
            sonar(sonidoGolpe(), 1.0F);
            boolean dio = super.doHurtTarget(nivel, objetivo);
            if (dio && objetivo instanceof LivingEntity v) {
                alGolpear(nivel, v);
            }
            return dio;
        }

        protected void alGolpear(ServerLevel nivel, LivingEntity v) {
        }
    }

    // ------------------------------------------------------------------
    //  Los reptisaurios: rugen al ver una presa
    // ------------------------------------------------------------------

    public abstract static class Reptisaurio extends Reptil {

        protected Reptisaurio(EntityType<? extends Monster> tipo, Level nivel) {
            super(tipo, nivel);
        }

        /** Cuando ve una presa (y no tenia), ruge: la cabeza atras, la boca abierta y los brazos abiertos. */
        @Override
        public void setTarget(@Nullable LivingEntity objetivo) {
            LivingEntity antes = getTarget();
            super.setTarget(objetivo);
            if (objetivo != null && antes == null && !level().isClientSide()) {
                animar(EV_ESPECIAL);
                sonar("rugido", 1.4F);
            }
        }
    }

    public static class Salvaje extends Reptisaurio {

        public Salvaje(EntityType<? extends Monster> tipo, Level nivel) {
            super(tipo, nivel);
        }

        public static AttributeSupplier.Builder atributos() {
            return base(30.0, 0.27, 7.0).add(Attributes.ATTACK_KNOCKBACK, 0.8)
                    .add(Attributes.KNOCKBACK_RESISTANCE, 0.3);
        }

        @Override
        public Bestia bestia() {
            return Fichas.REPTISAURIO_SALVAJE;
        }

        @Override
        protected String sonidoGolpe() {
            return "zarpazo";
        }
    }

    public static class Guerrero extends Reptisaurio {

        public Guerrero(EntityType<? extends Monster> tipo, Level nivel) {
            super(tipo, nivel);
        }

        public static AttributeSupplier.Builder atributos() {
            return base(34.0, 0.26, 6.0).add(Attributes.ATTACK_KNOCKBACK, 0.5)
                    .add(Attributes.KNOCKBACK_RESISTANCE, 0.4).add(Attributes.ARMOR, 4.0);
        }

        @Override
        public Bestia bestia() {
            return Fichas.REPTISAURIO_GUERRERO;
        }

        @Override
        protected String sonidoGolpe() {
            return "zarpazo";
        }

        /** El Veneno Primitivo: veneno II, ocho segundos, con sus gotas. */
        @Override
        protected void alGolpear(ServerLevel nivel, LivingEntity v) {
            BestiaEntity.efecto(v, MobEffects.POISON, 160, 1, this);
            sonar("veneno", 0.9F);
            particulas(nivel, "veneno", v.getX(), v.getY() + v.getBbHeight() * 0.6, v.getZ(), 10, 0.3, 0.4, 0.02);
        }
    }

    /**
     * El Reptisaurio Arquero (DEDsafio 4): dispara flechas de hueso impregnadas en Veneno Primitivo desde lejos,
     * da un zarpazo venenoso si te le pegas encima, y puede ir montado sobre un Narval (estado 1: postura sentada).
     */
    public static class Arquero extends Reptisaurio {

        private int esperaDisparo = 20;

        public Arquero(EntityType<? extends Monster> tipo, Level nivel) {
            super(tipo, nivel);
        }

        public static AttributeSupplier.Builder atributos() {
            return base(32.0, 0.27, 6.0).add(Attributes.ATTACK_KNOCKBACK, 0.4)
                    .add(Attributes.KNOCKBACK_RESISTANCE, 0.3).add(Attributes.ARMOR, 3.0);
        }

        @Override
        public Bestia bestia() {
            return Fichas.REPTISAURIO_ARQUERO;
        }

        @Override
        protected String sonidoGolpe() {
            return "zarpazo";
        }

        @Override
        protected void registerGoals() {
            goalSelector.addGoal(1, new FloatGoal(this));
            goalSelector.addGoal(3, new CombateArquero());
            goalSelector.addGoal(6, new WaterAvoidingRandomStrollGoal(this, 0.8));
            goalSelector.addGoal(7, new LookAtPlayerGoal(this, Player.class, 12.0F));
            goalSelector.addGoal(7, new RandomLookAroundGoal(this));
            presas();
        }

        @Override
        public void tick() {
            super.tick();
            if (!level().isClientSide()) {
                setEstado(isPassenger() ? 1 : 0);
                if (esperaDisparo > 0) {
                    esperaDisparo--;
                }
            }
        }

        @Override
        public boolean doHurtTarget(ServerLevel nivel, Entity objetivo) {
            animar(EV_ESPECIAL2);
            sonar("zarpazo", 1.0F);
            boolean dio = super.doHurtTarget(nivel, objetivo);
            if (dio && objetivo instanceof LivingEntity v) {
                alGolpear(nivel, v);
            }
            return dio;
        }

        @Override
        protected void alGolpear(ServerLevel nivel, LivingEntity v) {
            BestiaEntity.efecto(v, MobEffects.POISON, 160, 1, this);
            sonar("veneno", 0.9F);
            particulas(nivel, "veneno", v.getX(), v.getY() + v.getBbHeight() * 0.6, v.getZ(), 10, 0.3, 0.4, 0.02);
        }

        /** Dispara una flecha de hueso envenenada hacia su presa, dejando estela de hueso y veneno. */
        private void dispararFlecha(ServerLevel nivel) {
            LivingEntity t = presa();
            if (t == null || !isAlive()) {
                return;
            }
            sonar("disparo", 1.1F);
            Vec3 origen = new Vec3(getX(), getY() + getBbHeight() * 0.72, getZ());
            Vec3 destino = new Vec3(t.getX(), t.getY() + t.getBbHeight() * 0.6, t.getZ());
            Vec3 dir = destino.subtract(origen);
            double dist = dir.length();
            if (dist < 1.0E-3) {
                return;
            }
            Vec3 paso = dir.scale(1.55 / dist);
            float dano = (float) getAttributeValue(Attributes.ATTACK_DAMAGE);
            for (int i = 1; i <= 18; i++) {
                final int etapa = i;
                luego(i, () -> {
                    if (!(level() instanceof ServerLevel srv)) {
                        return;
                    }
                    Vec3 p = origen.add(paso.scale(etapa)).add(0.0, -0.008 * etapa * etapa, 0.0);
                    BlockPos bp = BlockPos.containing(p);
                    if (!srv.getBlockState(bp).getCollisionShape(srv, bp).isEmpty()) {
                        particulas(srv, "pluma", p.x, p.y, p.z, 6, 0.12, 0.12, 0.06);
                        olvidarLoProgramado();
                        return;
                    }
                    particulas(srv, "veneno", p.x, p.y, p.z, 2, 0.06, 0.06, 0.01);
                    particulas(srv, "pluma", p.x, p.y, p.z, 1, 0.04, 0.04, 0.02);
                    List<LivingEntity> tocados = srv.getEntitiesOfClass(LivingEntity.class,
                            getBoundingBox().move(p.subtract(position())).inflate(0.35),
                            v -> v != this && v != getVehicle() && v.isAlive() && !(v instanceof Reptil)
                                    && v.getBoundingBox().inflate(0.35).contains(p));
                    if (!tocados.isEmpty()) {
                        LivingEntity v = tocados.get(0);
                        if (v.hurtServer(srv, damageSources().mobProjectile(this, this), dano)) {
                            alGolpear(srv, v);
                        }
                        particulas(srv, "pluma", p.x, p.y, p.z, 8, 0.2, 0.2, 0.08);
                        olvidarLoProgramado();
                    }
                });
            }
        }

        private final class CombateArquero extends Goal {
            CombateArquero() {
                setFlags(EnumSet.of(Flag.MOVE, Flag.LOOK));
            }

            @Override
            public boolean canUse() {
                return presa() != null;
            }

            @Override
            public boolean canContinueToUse() {
                return presa() != null;
            }

            @Override
            public boolean requiresUpdateEveryTick() {
                return true;
            }

            @Override
            public void tick() {
                LivingEntity t = presa();
                if (t == null || !(level() instanceof ServerLevel nivel)) {
                    return;
                }
                getLookControl().setLookAt(t, 30.0F, 30.0F);
                double d2 = distanceToSqr(t);
                boolean ve = getSensing().hasLineOfSight(t);
                if (!isPassenger()) {
                    if (!ve || d2 > 14.0 * 14.0) {
                        getNavigation().moveTo(t, 1.1);
                    } else if (d2 < 3.6 * 3.6) {
                        getNavigation().moveTo(t, 1.15);
                    } else {
                        getNavigation().stop();
                    }
                }
                if (alAlcance(t, 0.8) && esperaDisparo <= 0) {
                    esperaDisparo = 22;
                    doHurtTarget(nivel, t);
                } else if (ve && d2 <= 20.0 * 20.0 && esperaDisparo <= 0) {
                    esperaDisparo = 38;
                    animar(EV_ATAQUE);
                    luego(10, () -> dispararFlecha(nivel));
                }
            }
        }
    }

    /**
     * El Reptisaurio Lancero (DEDsafio 4): su lanza de hueso de dos metros y medio le da mas alcance,
     * alterna estocadas y embestidas a dos manos, y deja Veneno Primitivo en cada golpe.
     */
    public static class Lancero extends Reptisaurio {

        private int golpes;
        private int esperaEmbestida = 40;

        public Lancero(EntityType<? extends Monster> tipo, Level nivel) {
            super(tipo, nivel);
        }

        public static AttributeSupplier.Builder atributos() {
            return base(38.0, 0.28, 8.0).add(Attributes.ATTACK_KNOCKBACK, 0.7)
                    .add(Attributes.KNOCKBACK_RESISTANCE, 0.4).add(Attributes.ARMOR, 5.0)
                    .add(Attributes.ENTITY_INTERACTION_RANGE, 1.2);
        }

        @Override
        public Bestia bestia() {
            return Fichas.REPTISAURIO_LANCERO;
        }

        @Override
        protected String sonidoGolpe() {
            return "lanza";
        }

        @Override
        public void tick() {
            super.tick();
            if (!(level() instanceof ServerLevel) || !isAlive()) {
                return;
            }
            if (esperaEmbestida > 0) {
                esperaEmbestida--;
            } else {
                LivingEntity t = presa();
                if (t != null && onGround() && distanceToSqr(t) > 3.2 * 3.2 && distanceToSqr(t) < 6.5 * 6.5
                        && getSensing().hasLineOfSight(t)) {
                    esperaEmbestida = 70;
                    animar(EV_ESPECIAL2);
                    sonar("lanza", 1.15F);
                    Vec3 dir = t.position().subtract(position()).multiply(1.0, 0.0, 1.0);
                    if (dir.lengthSqr() > 1.0E-4) {
                        dir = dir.normalize().scale(0.85);
                        setDeltaMovement(dir.x, 0.28, dir.z);
                    }
                }
            }
        }

        @Override
        public boolean doHurtTarget(ServerLevel nivel, Entity objetivo) {
            golpes++;
            if (golpes % 3 == 0) {
                animar(EV_ESPECIAL2);
                sonar("lanza", 1.15F);
            } else {
                animar(EV_ATAQUE);
                sonar("lanza", 1.0F);
            }
            boolean dio = super.doHurtTarget(nivel, objetivo);
            if (dio && objetivo instanceof LivingEntity v) {
                alGolpear(nivel, v);
            }
            return dio;
        }

        @Override
        protected void alGolpear(ServerLevel nivel, LivingEntity v) {
            BestiaEntity.efecto(v, MobEffects.POISON, 160, 1, this);
            sonar("veneno", 0.9F);
            particulas(nivel, "veneno", v.getX(), v.getY() + v.getBbHeight() * 0.6, v.getZ(), 10, 0.3, 0.4, 0.02);
        }
    }

    // ------------------------------------------------------------------
    //  Los dromoraptores: en manada
    // ------------------------------------------------------------------

    public abstract static class Raptor extends Reptil {

        /** Si es de los que trae otro al salir (y no trae mas). */
        private boolean deManada;

        protected Raptor(EntityType<? extends Monster> tipo, Level nivel) {
            super(tipo, nivel);
        }

        @Override
        protected void metas() {
            goalSelector.addGoal(5, new SeguirManada());
        }

        @Override
        protected String sonidoGolpe() {
            return "mordisco";
        }

        @Override
        public SpawnGroupData finalizeSpawn(ServerLevelAccessor nivel, DifficultyInstance dificultad,
                                            EntitySpawnReason motivo, @Nullable SpawnGroupData datos) {
            SpawnGroupData d = super.finalizeSpawn(nivel, dificultad, motivo, datos);
            if (!deManada && motivo != EntitySpawnReason.REINFORCEMENT && motivo != EntitySpawnReason.LOAD) {
                traerManada(nivel, dificultad);
            }
            return d;
        }

        /** Trae dos mas de los suyos, a su lado. */
        private void traerManada(ServerLevelAccessor nivel, DifficultyInstance dificultad) {
            ServerLevel n = nivel.getLevel();
            for (int k = 0; k < 2; k++) {
                Entity e = bestia().tipo.create(n, EntitySpawnReason.REINFORCEMENT);
                if (!(e instanceof Raptor r)) {
                    continue;
                }
                r.deManada = true;
                double ang = random.nextDouble() * Math.PI * 2.0;
                double x = getX() + Math.cos(ang) * 1.8;
                double z = getZ() + Math.sin(ang) * 1.8;
                BlockPos pos = BlockPos.containing(x, getY(), z);
                double y = n.getBlockState(pos).isAir() ? getY() : getY() + 1.0;
                r.snapTo(x, y, z, random.nextFloat() * 360.0F, 0.0F);
                r.finalizeSpawn(nivel, dificultad, EntitySpawnReason.REINFORCEMENT, null);
                nivel.addFreshEntity(r);
            }
            sonar("llamada", 1.2F);
        }

        /** Los de su manada que estan cerca (los de su misma especie). */
        private List<Raptor> manada(double radio) {
            return level().getEntitiesOfClass(Raptor.class, getBoundingBox().inflate(radio),
                    r -> r != this && r.isAlive() && r.getType() == getType());
        }

        /** Cuando ve una presa, se la dice a los de su manada que esten cerca y sin presa. */
        @Override
        public void setTarget(@Nullable LivingEntity objetivo) {
            LivingEntity antes = getTarget();
            super.setTarget(objetivo);
            if (objetivo != null && antes == null && !level().isClientSide()) {
                animar(EV_ESPECIAL);
            }
            if (objetivo != null && objetivo != antes && !level().isClientSide()) {
                boolean aviso = false;
                for (Raptor r : manada(20.0)) {
                    if (r.getTarget() == null) {
                        r.setTarget(objetivo);
                        aviso = true;
                    }
                }
                if (aviso) {
                    sonar("llamada", 1.0F);
                }
            }
        }

        @Override
        protected void addAdditionalSaveData(ValueOutput salida) {
            super.addAdditionalSaveData(salida);
            salida.putBoolean("DeManada", deManada);
        }

        @Override
        protected void readAdditionalSaveData(ValueInput entrada) {
            super.readAdditionalSaveData(entrada);
            deManada = entrada.getBooleanOr("DeManada", false);
        }

        /** Sin presa, el que se queda atras va con el que guia (el mas antiguo de los cercanos). */
        private final class SeguirManada extends Goal {

            private @Nullable Raptor guia;
            private int pensar;

            SeguirManada() {
                setFlags(EnumSet.of(Goal.Flag.MOVE));
            }

            @Override
            public boolean canUse() {
                if (getTarget() != null || --pensar > 0) {
                    return false;
                }
                pensar = 20;
                guia = null;
                for (Raptor r : manada(24.0)) {
                    if (r.tickCount > tickCount && (guia == null || r.tickCount > guia.tickCount)) {
                        guia = r;
                    }
                }
                return guia != null && distanceToSqr(guia) > 7.0 * 7.0;
            }

            @Override
            public boolean canContinueToUse() {
                return guia != null && guia.isAlive() && getTarget() == null && distanceToSqr(guia) > 4.0 * 4.0;
            }

            @Override
            public void tick() {
                if (guia != null && getNavigation().isDone()) {
                    getNavigation().moveTo(guia, 1.1);
                }
            }

            @Override
            public void stop() {
                guia = null;
                getNavigation().stop();
            }
        }
    }

    public static class Rojo extends Raptor {

        public Rojo(EntityType<? extends Monster> tipo, Level nivel) {
            super(tipo, nivel);
        }

        public static AttributeSupplier.Builder atributos() {
            return base(34.0, 0.33, 11.0).add(Attributes.ATTACK_KNOCKBACK, 1.0)
                    .add(Attributes.KNOCKBACK_RESISTANCE, 0.3).add(Attributes.STEP_HEIGHT, 1.1);
        }

        @Override
        public Bestia bestia() {
            return Fichas.DROMORAPTOR_ROJO;
        }
    }

    public static class Azul extends Raptor {

        public Azul(EntityType<? extends Monster> tipo, Level nivel) {
            super(tipo, nivel);
        }

        public static AttributeSupplier.Builder atributos() {
            return base(26.0, 0.44, 6.0).add(Attributes.ATTACK_KNOCKBACK, 0.3).add(Attributes.STEP_HEIGHT, 1.1);
        }

        @Override
        public Bestia bestia() {
            return Fichas.DROMORAPTOR_AZUL;
        }

        @Override
        protected double velocidadAtaque() {
            return 1.3;
        }
    }

    public static class Verde extends Raptor {

        public Verde(EntityType<? extends Monster> tipo, Level nivel) {
            super(tipo, nivel);
        }

        public static AttributeSupplier.Builder atributos() {
            return base(30.0, 0.37, 7.0).add(Attributes.ATTACK_KNOCKBACK, 0.5).add(Attributes.STEP_HEIGHT, 1.1);
        }

        @Override
        public Bestia bestia() {
            return Fichas.DROMORAPTOR_VERDE;
        }

        @Override
        protected double velocidadAtaque() {
            return 1.22;
        }

        /** Su mordisco envenena dos segundos con Veneno II. */
        @Override
        protected void alGolpear(ServerLevel nivel, LivingEntity v) {
            BestiaEntity.efecto(v, MobEffects.POISON, 40, 1, this);
            sonar("veneno", 0.9F);
            particulas(nivel, "veneno", v.getX(), v.getY() + v.getBbHeight() * 0.6, v.getZ(), 8, 0.25, 0.35, 0.02);
        }
    }

    // ------------------------------------------------------------------
    //  El Plumosaurio: pacifico hasta que le pegas
    // ------------------------------------------------------------------

    public static class Plumosaurio extends Reptil {

        public Plumosaurio(EntityType<? extends Monster> tipo, Level nivel) {
            super(tipo, nivel);
        }

        public static AttributeSupplier.Builder atributos() {
            return base(90.0, 0.2, 16.0).add(Attributes.ATTACK_KNOCKBACK, 2.5)
                    .add(Attributes.KNOCKBACK_RESISTANCE, 0.9).add(Attributes.STEP_HEIGHT, 1.1);
        }

        @Override
        public Bestia bestia() {
            return Fichas.PLUMOSAURIO;
        }

        @Override
        protected String sonidoGolpe() {
            return "golpe";
        }

        @Override
        protected double velocidadAtaque() {
            return 1.4;
        }

        /** Solo va a por el que le pega (y avisa a los suyos). */
        @Override
        protected void presas() {
            targetSelector.addGoal(1, new HurtByTargetGoal(this).setAlertOthers());
        }

        /** Su golpe te lanza por los aires. */
        @Override
        protected void alGolpear(ServerLevel nivel, LivingEntity v) {
            v.setDeltaMovement(v.getDeltaMovement().add(0.0, 0.75, 0.0));
            v.hurtMarked = true;
            particulas(nivel, "polvo", v.getX(), v.getY() + 0.2, v.getZ(), 16, 0.6, 0.2, 0.05);
        }

        /** Su cabeza, en lo alto de un cuello larguisimo: gira poco y despacio (si no, el cuello da bandazos). */
        @Override
        public int getMaxHeadYRot() {
            return 30;
        }

        @Override
        public int getHeadRotSpeed() {
            return 4;
        }

        @Override
        public int getMaxHeadXRot() {
            return 20;
        }

        /** A los treinta segundos sin que nadie le pegue, se calma. */
        @Override
        public void tick() {
            super.tick();
            if (!level().isClientSide() && getTarget() != null && tickCount - getLastHurtByMobTimestamp() > 600) {
                setTarget(null);
                setLastHurtByMob(null);
            }
        }
    }

    // ------------------------------------------------------------------
    //  El Cavador: se entierra y sale debajo de ti
    // ------------------------------------------------------------------

    /**
     * El Molusco Rocoso (el «Cavador» hasta que salio su nombre en el libro del juego). Como en el original: pequeño y
     * lento, ataca a quien se le acerque; si te alejas demasiado, se entierra (solo asoman las puntas de sus prismas y no
     * se le puede herir), te sigue bajo tierra, mas deprisa, hasta encontrarte, y sale debajo de ti de un mordisco que te
     * lanza. Suelta un hongo marron y, a veces, un fragmento de netherita.
     */
    public static class Molusco extends Reptil {

        public static final int ENTERRADO = 1;
        /** A quien este a esta distancia, lo ataca. */
        private static final double CERCA = 8.0;
        /** Si su presa se aleja mas que esto, se entierra para seguirla. */
        private static final double LEJOS = 6.0;
        /** Bajo tierra va asi de deprisa (por su velocidad de andar). */
        private static final double BAJO_TIERRA = 2.6;

        /** Lo que le falta para poder enterrarse otra vez. */
        private int espera = 40;
        /** Lo que lleva bajo tierra. */
        private int bajoTierra;
        /** Lo que lleva bajo tierra sin presa. */
        private int sinPresa;
        /** Si se esta hundiendo (de que empieza a escarbar a que queda enterrado). */
        private boolean hundiendose;

        public Molusco(EntityType<? extends Monster> tipo, Level nivel) {
            super(tipo, nivel);
        }

        public static AttributeSupplier.Builder atributos() {
            return base(18.0, 0.18, 5.0);
        }

        @Override
        public Bestia bestia() {
            return Fichas.MOLUSCO_ROCOSO;
        }

        @Override
        protected String sonidoGolpe() {
            return "mordisco";
        }

        @Override
        protected double velocidadAtaque() {
            return 1.0;
        }

        /** Solo va a por el que se le acerca (y por el que le pega). */
        @Override
        protected void presas() {
            targetSelector.addGoal(1, new HurtByTargetGoal(this));
            targetSelector.addGoal(2, new NearestAttackableTargetGoal<>(this, Player.class, 10, true, false,
                    (t, nivel) -> t.distanceToSqr(this) < CERCA * CERCA));
        }

        @Override
        public void tick() {
            super.tick();
            if (!(level() instanceof ServerLevel nivel) || !isAlive()) {
                return;
            }
            LivingEntity t = presa();
            if (getEstado() != ENTERRADO) {
                if (espera > 0) {
                    espera--;
                } else if (!hundiendose && t != null && onGround() && distanceToSqr(t) > LEJOS * LEJOS) {
                    enterrarse(nivel);
                }
                return;
            }
            // Bajo tierra: va hacia su presa, mas deprisa, y sale cuando la tiene encima.
            bajoTierra++;
            if (tickCount % 3 == 0) {
                particulas(nivel, "tierra", getX(), getY() + 0.1, getZ(), 3, 0.35, 0.05, 0.08);
            }
            if (t == null) {
                if (++sinPresa > 60) {
                    salir(nivel, null);
                }
                return;
            }
            sinPresa = 0;
            if (tickCount % 10 == 0) {
                getNavigation().moveTo(t, BAJO_TIERRA);
            }
            if (distanceToSqr(t) < 1.8 * 1.8 || bajoTierra > 600) {
                salir(nivel, t);
            }
        }

        /** Escarba y se hunde (doce ticks, su animacion especial); luego queda enterrado. */
        private void enterrarse(ServerLevel nivel) {
            hundiendose = true;
            getNavigation().stop();
            animar(EV_ESPECIAL);
            sonar("entierra", 1.0F);
            particulas(nivel, "tierra", getX(), getY() + 0.3, getZ(), 24, 0.5, 0.3, 0.12);
            luego(12, () -> {
                hundiendose = false;
                setEstado(ENTERRADO);
                bajoTierra = 0;
                sinPresa = 0;
            });
        }

        /** Sale de la tierra: si su presa esta encima, la muerde y la lanza hacia arriba. */
        private void salir(ServerLevel nivel, @Nullable LivingEntity t) {
            setEstado(0);
            getNavigation().stop();
            animar(EV_APARECE);
            sonar("sale", 1.2F);
            espera = 60;
            particulas(nivel, "tierra", getX(), getY() + 0.4, getZ(), 30, 0.6, 0.4, 0.2);
            particulas(nivel, "astilla", getX(), getY() + 0.6, getZ(), 10, 0.5, 0.4, 0.15);
            if (t != null && distanceToSqr(t) < 2.4 * 2.4) {
                float dano = (float) getAttributeValue(Attributes.ATTACK_DAMAGE) * 1.6F;
                if (t.hurtServer(nivel, damageSources().mobAttack(this), dano)) {
                    t.setDeltaMovement(t.getDeltaMovement().add(0.0, 0.6, 0.0));
                    t.hurtMarked = true;
                }
            }
        }

        /** Bajo tierra no se le puede herir (salvo lo que lo atraviesa todo, como /kill). */
        @Override
        public boolean hurtServer(ServerLevel nivel, DamageSource fuente, float dano) {
            if (getEstado() == ENTERRADO && !fuente.is(DamageTypeTags.BYPASSES_INVULNERABILITY)) {
                return false;
            }
            return super.hurtServer(nivel, fuente, dano);
        }

        /** Bajo tierra no muerde: acecha. */
        @Override
        public boolean doHurtTarget(ServerLevel nivel, Entity objetivo) {
            if (getEstado() == ENTERRADO) {
                return false;
            }
            return super.doHurtTarget(nivel, objetivo);
        }

        /** Un hongo marron siempre y, una de cada tres veces, un fragmento de netherita (como en el original). */
        @Override
        protected void dropCustomDeathLoot(ServerLevel nivel, DamageSource fuente, boolean reciente) {
            super.dropCustomDeathLoot(nivel, fuente, reciente);
            spawnAtLocation(nivel, new ItemStack(Items.BROWN_MUSHROOM));
            if (random.nextInt(3) == 0) {
                spawnAtLocation(nivel, new ItemStack(Items.NETHERITE_SCRAP));
            }
        }

        @Override
        public boolean isPushable() {
            return getEstado() != ENTERRADO && super.isPushable();
        }

        @Override
        protected void playStepSound(BlockPos pos, BlockState estado) {
            if (getEstado() != ENTERRADO) {
                super.playStepSound(pos, estado);
            }
        }
    }

    // ------------------------------------------------------------------
    //  El Narval: cetaceo acorazado de cuerno espiral y montura
    // ------------------------------------------------------------------

    /**
     * El Narval (DEDsafio 4): nada rapido en el agua y repta en tierra, embiste con su colmillo en espiral
     * lanzando por los aires, y cuando lleva un jinete (a veces sale con un Reptisaurio Arquero encima)
     * muestra su silla de cuero y hueso.
     */
    public static class Narval extends Reptil {

        private int esperaEmbiste = 40;
        private int embistiendo;

        public Narval(EntityType<? extends Monster> tipo, Level nivel) {
            super(tipo, nivel);
        }

        public static AttributeSupplier.Builder atributos() {
            return base(56.0, 0.28, 10.0).add(Attributes.ATTACK_KNOCKBACK, 1.2)
                    .add(Attributes.KNOCKBACK_RESISTANCE, 0.6).add(Attributes.ARMOR, 6.0)
                    .add(Attributes.STEP_HEIGHT, 1.0);
        }

        @Override
        public Bestia bestia() {
            return Fichas.NARVAL;
        }

        @Override
        protected String sonidoGolpe() {
            return "mordisco";
        }

        @Override
        protected void registerGoals() {
            goalSelector.addGoal(2, new MeleeAttackGoal(this, 1.25, true));
            goalSelector.addGoal(5, new RandomStrollGoal(this, 0.85));
            goalSelector.addGoal(6, new LookAtPlayerGoal(this, Player.class, 12.0F));
            goalSelector.addGoal(6, new RandomLookAroundGoal(this));
            presas();
        }

        @Override
        public boolean canBreatheUnderwater() {
            return true;
        }

        @Override
        public boolean isPushedByFluid() {
            return false;
        }

        @Override
        protected Vec3 getPassengerAttachmentPoint(Entity pasajero, EntityDimensions dims, float escala) {
            return new Vec3(0.0, dims.height() * 0.72, 0.15);
        }

        @Override
        public SpawnGroupData finalizeSpawn(ServerLevelAccessor nivel, DifficultyInstance dificultad,
                                            EntitySpawnReason motivo, @Nullable SpawnGroupData datos) {
            SpawnGroupData d = super.finalizeSpawn(nivel, dificultad, motivo, datos);
            if (motivo != EntitySpawnReason.LOAD && motivo != EntitySpawnReason.REINFORCEMENT
                    && random.nextFloat() < 0.35F) {
                ServerLevel n = nivel.getLevel();
                Entity e = Fichas.REPTISAURIO_ARQUERO.tipo.create(n, EntitySpawnReason.JOCKEY);
                if (e instanceof Arquero jinete) {
                    jinete.snapTo(getX(), getY(), getZ(), getYRot(), 0.0F);
                    jinete.finalizeSpawn(nivel, dificultad, EntitySpawnReason.JOCKEY, null);
                    jinete.startRiding(this, true, true);
                    nivel.addFreshEntity(jinete);
                }
            }
            return d;
        }

        @Override
        public void tick() {
            super.tick();
            if (!(level() instanceof ServerLevel nivel) || !isAlive()) {
                return;
            }
            setValor(isVehicle() ? 1.0F : 0.0F);
            LivingEntity t = presa();
            if (isInWater() && t != null && embistiendo <= 0) {
                Vec3 hacia = t.position().add(0.0, t.getBbHeight() * 0.3, 0.0).subtract(position());
                double d = hacia.length();
                if (d > 1.2) {
                    Vec3 v = hacia.scale(0.08 / d);
                    setDeltaMovement(getDeltaMovement().scale(0.88).add(v));
                }
            }
            if (embistiendo > 0) {
                embistiendo--;
                particulas(nivel, "espuma", getX(), getY() + 0.5, getZ(), 4, 0.5, 0.25, 0.08);
                if (t != null && alAlcance(t, 1.1)) {
                    embistiendo = 0;
                    float dano = (float) getAttributeValue(Attributes.ATTACK_DAMAGE) * 1.35F;
                    if (t.hurtServer(nivel, damageSources().mobAttack(this), dano)) {
                        Vec3 emp = t.position().subtract(position()).multiply(1.0, 0.0, 1.0);
                        emp = emp.lengthSqr() < 1.0E-4 ? new Vec3(0.0, 0.0, 1.0) : emp.normalize().scale(0.95);
                        t.setDeltaMovement(emp.x, 0.58, emp.z);
                        t.hurtMarked = true;
                        particulas(nivel, "espuma", t.getX(), t.getY() + 0.6, t.getZ(), 16, 0.5, 0.4, 0.15);
                    }
                }
                return;
            }
            if (esperaEmbiste > 0) {
                esperaEmbiste--;
            } else if (t != null && distanceToSqr(t) > 3.5 * 3.5 && distanceToSqr(t) < 11.0 * 11.0
                    && getSensing().hasLineOfSight(t)) {
                esperaEmbiste = 85;
                embistiendo = 14;
                animar(EV_ESPECIAL);
                sonar("embiste", 1.2F);
                Vec3 dir = t.position().subtract(position()).multiply(1.0, 0.0, 1.0);
                if (dir.lengthSqr() > 1.0E-4) {
                    dir = dir.normalize().scale(isInWater() ? 1.35 : 1.05);
                    setDeltaMovement(dir.x, isInWater() ? 0.08 : 0.25, dir.z);
                }
            }
        }
    }

    // ------------------------------------------------------------------
    //  El Fluviosaurus: trepa paredes, nada y rompe bloques
    // ------------------------------------------------------------------

    /**
     * El Fluviosaurus (DEDsafio 4): anfibio de rio que nada, trepa por las paredes en postura vertical (estado 1)
     * y destroza los bloques que se interponen entre el y su presa.
     */
    public static class Fluviosaurus extends Reptil {

        private int esperaRomper = 20;

        public Fluviosaurus(EntityType<? extends Monster> tipo, Level nivel) {
            super(tipo, nivel);
        }

        public static AttributeSupplier.Builder atributos() {
            return base(28.0, 0.32, 6.0).add(Attributes.ATTACK_KNOCKBACK, 0.4).add(Attributes.STEP_HEIGHT, 1.1);
        }

        @Override
        public Bestia bestia() {
            return Fichas.FLUVIOSAURUS;
        }

        @Override
        protected String sonidoGolpe() {
            return "mordisco";
        }

        @Override
        protected PathNavigation createNavigation(Level nivel) {
            return new WallClimberNavigation(this, nivel);
        }

        @Override
        public boolean canBreatheUnderwater() {
            return true;
        }

        @Override
        public boolean isPushedByFluid() {
            return false;
        }

        @Override
        public boolean onClimbable() {
            return getEstado() == 1 || super.onClimbable();
        }

        @Override
        public void tick() {
            super.tick();
            if (!(level() instanceof ServerLevel nivel) || !isAlive()) {
                return;
            }
            setEstado(horizontalCollision ? 1 : 0);
            LivingEntity t = presa();
            if (isInWater() && t != null) {
                Vec3 hacia = t.position().subtract(position());
                double d = hacia.length();
                if (d > 1.0) {
                    setDeltaMovement(getDeltaMovement().scale(0.86).add(hacia.scale(0.07 / d)));
                }
            }
            if (esperaRomper > 0) {
                esperaRomper--;
            } else if (t != null && horizontalCollision && nivel.getGameRules().get(GameRules.MOB_GRIEFING)) {
                if (romperFrente(nivel, 1, 5.0F)) {
                    esperaRomper = 28;
                    animar(EV_ESPECIAL);
                    sonar("rompe", 1.0F);
                    particulas(nivel, "escama", getX(), getY() + 0.35, getZ(), 14, 0.4, 0.25, 0.12);
                } else {
                    esperaRomper = 15;
                }
            }
        }

        /** Rompe un bloque blando o medio justo delante de el si le cierra el paso. */
        protected boolean romperFrente(ServerLevel nivel, int altoMax, float durezaMax) {
            float rad = getYRot() * Mth.DEG_TO_RAD;
            double paso = getBbWidth() * 0.55 + 0.65;
            int cx = Mth.floor(getX() - Mth.sin(rad) * paso);
            int cz = Mth.floor(getZ() + Mth.cos(rad) * paso);
            int by = Mth.floor(getY());
            boolean rompio = false;
            for (int dy = 0; dy <= altoMax; dy++) {
                BlockPos p = new BlockPos(cx, by + dy, cz);
                BlockState st = nivel.getBlockState(p);
                if (st.isAir() || !st.getFluidState().isEmpty() || st.is(BlockTags.WITHER_IMMUNE)) {
                    continue;
                }
                float d = st.getDestroySpeed(nivel, p);
                if (d >= 0.0F && d <= durezaMax) {
                    nivel.destroyBlock(p, true, this);
                    rompio = true;
                }
            }
            return rompio;
        }
    }

    // ------------------------------------------------------------------
    //  La Zarinosa Espigueya: salta a la cabeza, ciega y muerde
    // ------------------------------------------------------------------

    /**
     * La Zarinosa Espigueya (DEDsafio 4): salta a la cabeza de su presa, se le aferra (estado 1) dejandola a ciegas
     * y mordiendola cada segundo hasta que alguien le pega un golpe para soltarla.
     */
    public static class Zarinosa extends Reptil {

        private static final int AFERRADA = 1;

        private @Nullable UUID victima;
        private int esperaSalto = 30;

        public Zarinosa(EntityType<? extends Monster> tipo, Level nivel) {
            super(tipo, nivel);
        }

        public static AttributeSupplier.Builder atributos() {
            return base(24.0, 0.35, 5.0).add(Attributes.STEP_HEIGHT, 1.0);
        }

        @Override
        public Bestia bestia() {
            return Fichas.ZARINOSA;
        }

        @Override
        protected String sonidoGolpe() {
            return "mordisco";
        }

        @Override
        public void tick() {
            super.tick();
            if (!(level() instanceof ServerLevel nivel) || !isAlive()) {
                return;
            }
            if (victima != null) {
                Entity e = nivel.getEntity(victima);
                if (!(e instanceof LivingEntity v) || !v.isAlive() || v.isSpectator()
                        || (v instanceof Player p && p.isCreative()) || v.distanceToSqr(this) > 5.0 * 5.0) {
                    soltar();
                    return;
                }
                setPos(v.getX(), v.getY() + v.getBbHeight() - 0.15, v.getZ());
                setDeltaMovement(Vec3.ZERO);
                setYRot(v.getYRot());
                yBodyRot = v.getYRot();
                yHeadRot = v.getYRot();
                BestiaEntity.efecto(v, MobEffects.BLINDNESS, 45, 0, this);
                if (tickCount % 20 == 0) {
                    animar(EV_ATAQUE);
                    sonar("mordisco", 0.95F);
                    v.hurtServer(nivel, damageSources().mobAttack(this),
                            (float) getAttributeValue(Attributes.ATTACK_DAMAGE));
                    particulas(nivel, "espora", v.getX(), v.getY() + v.getBbHeight(), v.getZ(), 5, 0.25, 0.2, 0.06);
                }
                return;
            }
            if (esperaSalto > 0) {
                esperaSalto--;
                return;
            }
            LivingEntity t = presa();
            if (t == null) {
                return;
            }
            double d2 = distanceToSqr(t);
            if (onGround() && d2 > 1.8 * 1.8 && d2 < 5.8 * 5.8 && getSensing().hasLineOfSight(t)) {
                esperaSalto = 45;
                animar(EV_ESPECIAL);
                sonar("salta", 1.1F);
                Vec3 dir = t.position().subtract(position()).multiply(1.0, 0.0, 1.0);
                if (dir.lengthSqr() > 1.0E-4) {
                    dir = dir.normalize().scale(0.85);
                    setDeltaMovement(dir.x, 0.44, dir.z);
                }
            } else if (d2 < 1.9 * 1.9 && !(t instanceof Player p && p.isCreative())) {
                victima = t.getUUID();
                setEstado(AFERRADA);
                getNavigation().stop();
                sonar("salta", 1.0F);
                particulas(nivel, "escama", t.getX(), t.getY() + t.getBbHeight(), t.getZ(), 10, 0.3, 0.25, 0.05);
            }
        }

        private void soltar() {
            victima = null;
            setEstado(0);
            esperaSalto = 65;
        }

        /** Un golpe la despega de la cabeza al instante. */
        @Override
        public boolean hurtServer(ServerLevel nivel, DamageSource fuente, float dano) {
            boolean herida = super.hurtServer(nivel, fuente, dano);
            if (herida && victima != null) {
                soltar();
                double ang = random.nextDouble() * Math.PI * 2.0;
                setDeltaMovement(Math.cos(ang) * 0.45, 0.32, Math.sin(ang) * 0.45);
            }
            return herida;
        }

        @Override
        public boolean isPushable() {
            return victima == null && super.isPushable();
        }
    }

    // ------------------------------------------------------------------
    //  El Kragtops: coloso acorazado neutral de cuernos y maza caudal
    // ------------------------------------------------------------------

    /**
     * El Kragtops (DEDsafio 4): neutral (solo ataca si le pegas y se calma a los treinta segundos); embiste con sus
     * cuernos lanzandote hacia arriba y sacude su maza caudal de roca.
     */
    public static class Kragtops extends Reptil {

        private int golpes;
        private int esperaCarga = 30;

        public Kragtops(EntityType<? extends Monster> tipo, Level nivel) {
            super(tipo, nivel);
        }

        public static AttributeSupplier.Builder atributos() {
            return base(84.0, 0.25, 13.0).add(Attributes.ATTACK_KNOCKBACK, 1.8)
                    .add(Attributes.KNOCKBACK_RESISTANCE, 0.85).add(Attributes.ARMOR, 10.0)
                    .add(Attributes.STEP_HEIGHT, 1.1);
        }

        @Override
        public Bestia bestia() {
            return Fichas.KRAGTOPS;
        }

        @Override
        protected String sonidoGolpe() {
            return "embiste";
        }

        @Override
        protected double velocidadAtaque() {
            return 1.3;
        }

        /** Neutral: solo responde al que le pega (y avisa a los suyos). */
        @Override
        protected void presas() {
            targetSelector.addGoal(1, new HurtByTargetGoal(this).setAlertOthers());
        }

        @Override
        public void tick() {
            super.tick();
            if (!(level() instanceof ServerLevel) || !isAlive()) {
                return;
            }
            if (getTarget() != null && tickCount - getLastHurtByMobTimestamp() > 600) {
                setTarget(null);
                setLastHurtByMob(null);
                return;
            }
            if (esperaCarga > 0) {
                esperaCarga--;
            } else {
                LivingEntity t = presa();
                if (t != null && onGround() && distanceToSqr(t) > 4.0 * 4.0 && distanceToSqr(t) < 10.0 * 10.0
                        && getSensing().hasLineOfSight(t)) {
                    esperaCarga = 75;
                    sonar("embiste", 1.15F);
                    Vec3 dir = t.position().subtract(position()).multiply(1.0, 0.0, 1.0);
                    if (dir.lengthSqr() > 1.0E-4) {
                        dir = dir.normalize().scale(0.95);
                        setDeltaMovement(dir.x, 0.22, dir.z);
                    }
                }
            }
        }

        @Override
        public boolean doHurtTarget(ServerLevel nivel, Entity objetivo) {
            golpes++;
            boolean maza = golpes % 2 == 0;
            animar(maza ? EV_ESPECIAL : EV_ATAQUE);
            sonar(maza ? "maza" : "embiste", 1.15F);
            boolean dio = super.doHurtTarget(nivel, objetivo);
            if (dio && objetivo instanceof LivingEntity v) {
                if (maza) {
                    Vec3 emp = v.position().subtract(position()).multiply(1.0, 0.0, 1.0);
                    emp = emp.lengthSqr() < 1.0E-4 ? new Vec3(0.0, 0.0, 1.0) : emp.normalize().scale(1.3);
                    v.setDeltaMovement(emp.x, 0.38, emp.z);
                    v.hurtMarked = true;
                    particulas(nivel, "esquirla", v.getX(), v.getY() + 0.5, v.getZ(), 12, 0.4, 0.3, 0.12);
                    particulas(nivel, "polvo", v.getX(), v.getY() + 0.2, v.getZ(), 18, 0.6, 0.2, 0.06);
                } else {
                    v.setDeltaMovement(v.getDeltaMovement().add(0.0, 0.62, 0.0));
                    v.hurtMarked = true;
                    particulas(nivel, "polvo", v.getX(), v.getY() + 0.2, v.getZ(), 14, 0.5, 0.2, 0.05);
                }
            }
            return dio;
        }
    }

    // ------------------------------------------------------------------
    //  El Dactylo Adulto: vuela, picotea y te sube por los aires
    // ------------------------------------------------------------------

    /**
     * El Dactylo Adulto (DEDsafio 4): vuela en circulos, baja en picado a dar picotazos o te agarra con las garras
     * (estado 1), te sube durante tres segundos por los aires y te deja caer desde las alturas.
     */
    public static class DactyloAdulto extends BestiaEntity {

        private static final int LLEVANDO = 1;

        private @Nullable UUID agarrado;
        private int tiempoAgarre;
        private int esperaAgarre = 40;
        private int esperaPicotazo;

        public DactyloAdulto(EntityType<? extends Monster> tipo, Level nivel) {
            super(tipo, nivel);
            this.moveControl = new FlyingMoveControl(this, 20, true);
            setNoGravity(true);
        }

        public static AttributeSupplier.Builder atributos() {
            return Monster.createMonsterAttributes()
                    .add(Attributes.MAX_HEALTH, 38.0)
                    .add(Attributes.FLYING_SPEED, 0.65)
                    .add(Attributes.MOVEMENT_SPEED, 0.34)
                    .add(Attributes.ATTACK_DAMAGE, 7.0)
                    .add(Attributes.FOLLOW_RANGE, 36.0);
        }

        @Override
        public Bestia bestia() {
            return Fichas.DACTYLO_ADULTO;
        }

        @Override
        protected PathNavigation createNavigation(Level nivel) {
            return new FlyingPathNavigation(this, nivel);
        }

        @Override
        protected void registerGoals() {
            goalSelector.addGoal(1, new CazarVolando());
            goalSelector.addGoal(5, new Planear());
            goalSelector.addGoal(6, new LookAtPlayerGoal(this, Player.class, 16.0F));
            targetSelector.addGoal(1, new HurtByTargetGoal(this).setAlertOthers());
            targetSelector.addGoal(2, new NearestAttackableTargetGoal<>(this, Player.class, true));
        }

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

        @Override
        public void tick() {
            super.tick();
            if (!(level() instanceof ServerLevel nivel) || !isAlive()) {
                return;
            }
            if (esperaAgarre > 0) {
                esperaAgarre--;
            }
            if (esperaPicotazo > 0) {
                esperaPicotazo--;
            }
            if (agarrado != null) {
                Entity e = nivel.getEntity(agarrado);
                if (!(e instanceof LivingEntity v) || !v.isAlive() || v.isSpectator()
                        || (v instanceof Player p && p.isCreative()) || --tiempoAgarre <= 0) {
                    soltarPresa();
                    return;
                }
                setDeltaMovement(0.0, 0.34, 0.0);
                v.setPos(getX(), getY() - v.getBbHeight() + 0.15, getZ());
                v.setDeltaMovement(Vec3.ZERO);
                v.hurtMarked = true;
                v.fallDistance = 0.0F;
                if (tickCount % 8 == 0) {
                    sonar("paso", 0.55F);
                    particulas(nivel, "pluma", getX(), getY() + 0.4, getZ(), 3, 0.45, 0.2, 0.04);
                }
            }
        }

        private void soltarPresa() {
            agarrado = null;
            tiempoAgarre = 0;
            setEstado(0);
            esperaAgarre = 130;
        }

        @Override
        public boolean hurtServer(ServerLevel nivel, DamageSource fuente, float dano) {
            boolean herido = super.hurtServer(nivel, fuente, dano);
            if (herido && agarrado != null && dano >= 4.0F) {
                soltarPresa();
            }
            return herido;
        }

        private final class CazarVolando extends Goal {
            CazarVolando() {
                setFlags(EnumSet.of(Flag.MOVE, Flag.LOOK));
            }

            @Override
            public boolean canUse() {
                return agarrado == null && presa() != null;
            }

            @Override
            public boolean canContinueToUse() {
                return canUse();
            }

            @Override
            public boolean requiresUpdateEveryTick() {
                return true;
            }

            @Override
            public void tick() {
                LivingEntity t = presa();
                if (t == null || !(level() instanceof ServerLevel nivel)) {
                    return;
                }
                getLookControl().setLookAt(t, 30.0F, 30.0F);
                Vec3 meta = t.position().add(0.0, t.getBbHeight() * 0.65, 0.0);
                Vec3 falta = meta.subtract(position());
                double dist = falta.length();
                if (dist < 5.5) {
                    Vec3 v = falta.scale(0.32);
                    if (v.length() > 0.58) {
                        v = v.normalize().scale(0.58);
                    }
                    setDeltaMovement(v);
                } else {
                    if (esperaPicotazo == 0 && dist < 12.0 && getY() > t.getY() + 2.5) {
                        animar(EV_ESPECIAL2);
                    }
                    getMoveControl().setWantedPosition(meta.x, meta.y, meta.z, 1.15);
                }
                if (alAlcance(t, 1.0) && getSensing().hasLineOfSight(t)) {
                    if (esperaAgarre <= 0 && !(t instanceof Player p && p.isCreative())) {
                        agarrado = t.getUUID();
                        tiempoAgarre = 65;
                        setEstado(LLEVANDO);
                        animar(EV_ESPECIAL);
                        sonar("agarra", 1.2F);
                        particulas(nivel, "pluma", getX(), getY() + 0.5, getZ(), 12, 0.5, 0.3, 0.08);
                    } else if (esperaPicotazo <= 0) {
                        esperaPicotazo = 22;
                        animar(EV_ATAQUE);
                        sonar("picotazo", 1.0F);
                        doHurtTarget(nivel, t);
                        setDeltaMovement(getDeltaMovement().add(0.0, 0.32, 0.0));
                    }
                }
            }
        }

        private final class Planear extends Goal {
            Planear() {
                setFlags(EnumSet.of(Flag.MOVE));
            }

            @Override
            public boolean canUse() {
                return agarrado == null && presa() == null && !getMoveControl().hasWanted() && random.nextInt(18) == 0;
            }

            @Override
            public boolean canContinueToUse() {
                return false;
            }

            @Override
            public void start() {
                for (int i = 0; i < 4; i++) {
                    Vec3 p = position().add((random.nextDouble() - 0.5) * 16.0, (random.nextDouble() - 0.4) * 7.0,
                            (random.nextDouble() - 0.5) * 16.0);
                    if (level().isEmptyBlock(BlockPos.containing(p))) {
                        getMoveControl().setWantedPosition(p.x, p.y, p.z, 0.75);
                        return;
                    }
                }
            }
        }
    }

    // ------------------------------------------------------------------
    //  La Chelonia: tortuga de geoda que dispara cristales y se esconde
    // ------------------------------------------------------------------

    /**
     * La Chelonia (DEDsafio 4): tortuga acorazada con cristales amatista en el caparazon; dispara rafagas de cristal
     * desde lejos y, al verse amenazada, se esconde dentro de su caparazon (estado 1), donde las flechas y proyectiles
     * rebotan y solo se la puede herir cuerpo a cuerpo.
     */
    public static class Chelonia extends Reptil {

        public static final int ESCONDIDA = 1;

        private int tiempoEscondida;
        private int esperaCaparazon = 40;
        private int esperaCristal = 25;

        public Chelonia(EntityType<? extends Monster> tipo, Level nivel) {
            super(tipo, nivel);
        }

        public static AttributeSupplier.Builder atributos() {
            return base(68.0, 0.2, 9.0).add(Attributes.ATTACK_KNOCKBACK, 0.8)
                    .add(Attributes.KNOCKBACK_RESISTANCE, 0.9).add(Attributes.ARMOR, 12.0)
                    .add(Attributes.STEP_HEIGHT, 1.0);
        }

        @Override
        public Bestia bestia() {
            return Fichas.CHELONIA;
        }

        @Override
        protected String sonidoGolpe() {
            return "mordisco";
        }

        @Override
        public boolean canBreatheUnderwater() {
            return true;
        }

        @Override
        public boolean isPushedByFluid() {
            return false;
        }

        @Override
        public void tick() {
            super.tick();
            if (!(level() instanceof ServerLevel nivel) || !isAlive()) {
                return;
            }
            if (esperaCaparazon > 0) {
                esperaCaparazon--;
            }
            if (esperaCristal > 0) {
                esperaCristal--;
            }
            LivingEntity t = presa();
            if (getEstado() == ESCONDIDA) {
                getNavigation().stop();
                setDeltaMovement(0.0, getDeltaMovement().y, 0.0);
                if (t != null && esperaCristal <= 0 && distanceToSqr(t) <= 16.0 * 16.0
                        && getSensing().hasLineOfSight(t)) {
                    dispararCristales(nivel, t);
                }
                if (--tiempoEscondida <= 0) {
                    setEstado(0);
                    animar(EV_APARECE);
                    esperaCaparazon = 110;
                }
                return;
            }
            if (t != null && esperaCristal <= 0 && distanceToSqr(t) > 3.2 * 3.2 && distanceToSqr(t) <= 15.0 * 15.0
                    && getSensing().hasLineOfSight(t)) {
                dispararCristales(nivel, t);
            }
        }

        private void esconderse(ServerLevel nivel) {
            setEstado(ESCONDIDA);
            tiempoEscondida = 85;
            getNavigation().stop();
            sonar("esconde", 1.15F);
            particulas(nivel, "cristal", getX(), getY() + 0.8, getZ(), 14, 0.6, 0.35, 0.06);
        }

        /** Sacude el caparazon y lanza una rafaga de cristales amatista hacia su presa. */
        private void dispararCristales(ServerLevel nivel, LivingEntity t) {
            esperaCristal = 38;
            animar(EV_ESPECIAL);
            sonar("cristal", 1.15F);
            Vec3 origen = new Vec3(getX(), getY() + 0.95, getZ());
            Vec3 destino = new Vec3(t.getX(), t.getY() + t.getBbHeight() * 0.55, t.getZ());
            Vec3 dir = destino.subtract(origen);
            double dist = dir.length();
            if (dist < 1.0E-3) {
                return;
            }
            Vec3 paso = dir.scale(1.4 / dist);
            for (int i = 1; i <= 14; i++) {
                final int etapa = i;
                luego(i, () -> {
                    if (!(level() instanceof ServerLevel srv)) {
                        return;
                    }
                    Vec3 p = origen.add(paso.scale(etapa));
                    particulas(srv, "cristal", p.x, p.y, p.z, 3, 0.14, 0.14, 0.04);
                    List<LivingEntity> tocados = srv.getEntitiesOfClass(LivingEntity.class,
                            getBoundingBox().move(p.subtract(position())).inflate(0.4),
                            v -> v != this && v.isAlive() && !(v instanceof Reptil)
                                    && v.getBoundingBox().inflate(0.4).contains(p));
                    if (!tocados.isEmpty()) {
                        LivingEntity v = tocados.get(0);
                        if (v.hurtServer(srv, damageSources().mobProjectile(this, this), 8.0F)) {
                            Vec3 emp = paso.multiply(1.0, 0.0, 1.0);
                            emp = emp.lengthSqr() < 1.0E-4 ? new Vec3(0.0, 0.0, 1.0) : emp.normalize().scale(0.55);
                            v.setDeltaMovement(v.getDeltaMovement().add(emp.x, 0.22, emp.z));
                            v.hurtMarked = true;
                        }
                        particulas(srv, "cristal", p.x, p.y, p.z, 12, 0.25, 0.25, 0.1);
                        olvidarLoProgramado();
                    }
                });
            }
        }

        /** En su caparazon las flechas y proyectiles rebotan; solo el cuerpo a cuerpo la hiere. */
        @Override
        public boolean hurtServer(ServerLevel nivel, DamageSource fuente, float dano) {
            if (getEstado() == ESCONDIDA) {
                if (fuente.is(DamageTypeTags.IS_PROJECTILE)) {
                    sonar("cristal", 0.95F, 1.35F);
                    particulas(nivel, "cristal", getX(), getY() + 0.85, getZ(), 10, 0.55, 0.35, 0.08);
                    return false;
                }
                return super.hurtServer(nivel, fuente, dano * 0.7F);
            }
            boolean herida = super.hurtServer(nivel, fuente, dano);
            if (herida && isAlive() && esperaCaparazon <= 0 && (fuente.is(DamageTypeTags.IS_PROJECTILE)
                    || getHealth() < getMaxHealth() * 0.75F)) {
                esconderse(nivel);
            }
            return herida;
        }

        @Override
        public boolean doHurtTarget(ServerLevel nivel, Entity objetivo) {
            if (getEstado() == ESCONDIDA) {
                return false;
            }
            return super.doHurtTarget(nivel, objetivo);
        }
    }

    // ------------------------------------------------------------------
    //  Los tres colosos bipedos: Tyrannok, Mastodino y Espinosaurio
    // ------------------------------------------------------------------

    /**
     * La base de los tres grandes dinosaurios bipedos (Tyrannok, Mastodino y Espinosaurio): rugen al ver una presa
     * y se abren paso rompiendo bloques cuando persiguen.
     */
    public abstract static class ColosoBipedo extends Reptil {

        protected int golpes;
        private int esperaRomper = 20;

        protected ColosoBipedo(EntityType<? extends Monster> tipo, Level nivel) {
            super(tipo, nivel);
        }

        @Override
        protected String sonidoGolpe() {
            return "mordisco";
        }

        @Override
        protected double velocidadAtaque() {
            return 1.25;
        }

        @Override
        public int getMaxHeadYRot() {
            return 35;
        }

        @Override
        public int getHeadRotSpeed() {
            return 5;
        }

        @Override
        public void setTarget(@Nullable LivingEntity objetivo) {
            LivingEntity antes = getTarget();
            super.setTarget(objetivo);
            if (objetivo != null && antes == null && !level().isClientSide()) {
                animar(EV_ESPECIAL);
                sonar("rugido", 1.5F);
                if (level() instanceof ServerLevel nivel) {
                    alRugir(nivel);
                }
            }
        }

        protected void alRugir(ServerLevel nivel) {
        }

        @Override
        public void tick() {
            super.tick();
            if (!(level() instanceof ServerLevel nivel) || !isAlive()) {
                return;
            }
            if (esperaRomper > 0) {
                esperaRomper--;
            } else if (presa() != null && horizontalCollision && nivel.getGameRules().get(GameRules.MOB_GRIEFING)) {
                if (romperPaso(nivel)) {
                    esperaRomper = 24;
                    sonar("rompe", 1.1F);
                    particulas(nivel, "polvo", getX(), getY() + 1.5, getZ(), 20, 0.8, 0.8, 0.1);
                    particulas(nivel, "escama", getX(), getY() + 1.5, getZ(), 14, 0.7, 0.7, 0.1);
                } else {
                    esperaRomper = 12;
                }
            }
        }

        /** Abre camino delante de sus fauces cuando choca persiguiendo a una presa. */
        protected boolean romperPaso(ServerLevel nivel) {
            float rad = getYRot() * Mth.DEG_TO_RAD;
            double paso = getBbWidth() * 0.55 + 0.8;
            int cx = Mth.floor(getX() - Mth.sin(rad) * paso);
            int cz = Mth.floor(getZ() + Mth.cos(rad) * paso);
            int by = Mth.floor(getY());
            boolean rompio = false;
            for (int dx = -1; dx <= 1; dx++) {
                for (int dz = -1; dz <= 1; dz++) {
                    for (int dy = 0; dy <= 3; dy++) {
                        BlockPos p = new BlockPos(cx + dx, by + dy, cz + dz);
                        BlockState st = nivel.getBlockState(p);
                        if (st.isAir() || !st.getFluidState().isEmpty() || st.is(BlockTags.WITHER_IMMUNE)) {
                            continue;
                        }
                        float d = st.getDestroySpeed(nivel, p);
                        if (d >= 0.0F && d <= 8.0F) {
                            nivel.destroyBlock(p, true, this);
                            rompio = true;
                        }
                    }
                }
            }
            return rompio;
        }
    }

    /**
     * El Tyrannok (DEDsafio 4): coloso rojo con cicatrices; su mordisco deja Lentitud II, da coletazos que barren
     * y rompe bloques al perseguir.
     */
    public static class Tyrannok extends ColosoBipedo {

        public Tyrannok(EntityType<? extends Monster> tipo, Level nivel) {
            super(tipo, nivel);
        }

        public static AttributeSupplier.Builder atributos() {
            return base(130.0, 0.29, 18.0).add(Attributes.ATTACK_KNOCKBACK, 1.6)
                    .add(Attributes.KNOCKBACK_RESISTANCE, 0.9).add(Attributes.ARMOR, 8.0)
                    .add(Attributes.STEP_HEIGHT, 1.5).add(Attributes.ENTITY_INTERACTION_RANGE, 1.2);
        }

        @Override
        public Bestia bestia() {
            return Fichas.TYRANNOK;
        }

        @Override
        public boolean doHurtTarget(ServerLevel nivel, Entity objetivo) {
            golpes++;
            if (golpes % 3 == 0) {
                animar(EV_ESPECIAL2);
                sonar("mordisco", 1.15F);
            } else {
                animar(EV_ATAQUE);
                sonar("mordisco", 1.0F);
            }
            boolean dio = super.doHurtTarget(nivel, objetivo);
            if (dio && objetivo instanceof LivingEntity v) {
                alGolpear(nivel, v);
            }
            return dio;
        }

        @Override
        protected void alGolpear(ServerLevel nivel, LivingEntity v) {
            BestiaEntity.efecto(v, MobEffects.SLOWNESS, 100, 1, this);
            particulas(nivel, "polvo", v.getX(), v.getY() + 0.3, v.getZ(), 14, 0.5, 0.25, 0.06);
        }
    }

    /**
     * El Mastodino (DEDsafio 4): coloso verde musgo con cuernos de toro y montura en el lomo; su rugido con pisoton
     * impulsa por los aires a todos los que esten cerca, y tambien rompe bloques en su camino.
     */
    public static class Mastodino extends ColosoBipedo {

        private int esperaRugido = 100;

        public Mastodino(EntityType<? extends Monster> tipo, Level nivel) {
            super(tipo, nivel);
        }

        public static AttributeSupplier.Builder atributos() {
            return base(140.0, 0.28, 17.0).add(Attributes.ATTACK_KNOCKBACK, 1.8)
                    .add(Attributes.KNOCKBACK_RESISTANCE, 0.9).add(Attributes.ARMOR, 10.0)
                    .add(Attributes.STEP_HEIGHT, 1.5).add(Attributes.ENTITY_INTERACTION_RANGE, 1.2);
        }

        @Override
        public Bestia bestia() {
            return Fichas.MASTODINO;
        }

        @Override
        protected Vec3 getPassengerAttachmentPoint(Entity pasajero, EntityDimensions dims, float escala) {
            return new Vec3(0.0, dims.height() * 0.78, 0.1);
        }

        @Override
        public void tick() {
            super.tick();
            if (!(level() instanceof ServerLevel nivel) || !isAlive()) {
                return;
            }
            setValor(isVehicle() ? 1.0F : 0.0F);
            if (esperaRugido > 0) {
                esperaRugido--;
            } else {
                LivingEntity t = presa();
                if (t != null && distanceToSqr(t) < 6.5 * 6.5) {
                    esperaRugido = 140;
                    animar(EV_ESPECIAL);
                    sonar("rugido", 1.5F);
                    alRugir(nivel);
                }
            }
        }

        /** Su rugido con pisoton lanza hacia arriba a todos los que esten alrededor. */
        @Override
        protected void alRugir(ServerLevel nivel) {
            particulas(nivel, "polvo", getX(), getY() + 0.2, getZ(), 32, 2.2, 0.3, 0.12);
            for (LivingEntity v : nivel.getEntitiesOfClass(LivingEntity.class, getBoundingBox().inflate(6.0),
                    e -> e != this && e != getFirstPassenger() && e.isAlive() && !(e instanceof Reptil))) {
                v.hurtServer(nivel, damageSources().mobAttack(this), 6.0F);
                v.setDeltaMovement(v.getDeltaMovement().add(0.0, 0.82, 0.0));
                v.hurtMarked = true;
            }
        }

        @Override
        public boolean doHurtTarget(ServerLevel nivel, Entity objetivo) {
            golpes++;
            boolean cornada = golpes % 2 == 0;
            animar(cornada ? EV_ESPECIAL2 : EV_ATAQUE);
            sonar("mordisco", 1.1F);
            boolean dio = super.doHurtTarget(nivel, objetivo);
            if (dio && objetivo instanceof LivingEntity v && cornada) {
                v.setDeltaMovement(v.getDeltaMovement().add(0.0, 0.58, 0.0));
                v.hurtMarked = true;
            }
            return dio;
        }
    }

    /**
     * El Espinosaurio (DEDsafio 4): coloso semiacuatico de vela dorsal; su mordisco envenena con Veneno II,
     * ruge y rompe bloques en su camino.
     */
    public static class Espinosaurio extends ColosoBipedo {

        public Espinosaurio(EntityType<? extends Monster> tipo, Level nivel) {
            super(tipo, nivel);
        }

        public static AttributeSupplier.Builder atributos() {
            return base(120.0, 0.31, 16.0).add(Attributes.ATTACK_KNOCKBACK, 1.4)
                    .add(Attributes.KNOCKBACK_RESISTANCE, 0.85).add(Attributes.ARMOR, 8.0)
                    .add(Attributes.STEP_HEIGHT, 1.5).add(Attributes.ENTITY_INTERACTION_RANGE, 1.2);
        }

        @Override
        public Bestia bestia() {
            return Fichas.ESPINOSAURIO;
        }

        @Override
        public boolean canBreatheUnderwater() {
            return true;
        }

        @Override
        public boolean isPushedByFluid() {
            return false;
        }

        @Override
        public boolean doHurtTarget(ServerLevel nivel, Entity objetivo) {
            golpes++;
            animar(golpes % 3 == 0 ? EV_ESPECIAL2 : EV_ATAQUE);
            sonar("mordisco", 1.05F);
            boolean dio = super.doHurtTarget(nivel, objetivo);
            if (dio && objetivo instanceof LivingEntity v) {
                alGolpear(nivel, v);
            }
            return dio;
        }

        @Override
        protected void alGolpear(ServerLevel nivel, LivingEntity v) {
            BestiaEntity.efecto(v, MobEffects.POISON, 120, 1, this);
            sonar("veneno", 0.9F);
            particulas(nivel, "veneno", v.getX(), v.getY() + v.getBbHeight() * 0.6, v.getZ(), 12, 0.35, 0.45, 0.03);
        }
    }
}
