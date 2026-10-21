package com.atalaya.bestiario.mobs;

import com.atalaya.bestiario.Bestia;
import com.atalaya.bestiario.BestiaEntity;
import com.atalaya.bestiario.Fichas;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.tags.DamageTypeTags;
import net.minecraft.world.DifficultyInstance;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntitySpawnReason;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.SpawnGroupData;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.FloatGoal;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.entity.ai.goal.LookAtPlayerGoal;
import net.minecraft.world.entity.ai.goal.MeleeAttackGoal;
import net.minecraft.world.entity.ai.goal.RandomLookAroundGoal;
import net.minecraft.world.entity.ai.goal.WaterAvoidingRandomStrollGoal;
import net.minecraft.world.entity.ai.goal.target.HurtByTargetGoal;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.ServerLevelAccessor;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.storage.ValueInput;
import net.minecraft.world.level.storage.ValueOutput;
import org.jspecify.annotations.Nullable;

import java.util.EnumSet;
import java.util.List;

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
}
