package com.atalaya.bestiario.mobs;

import com.atalaya.Atalaya;
import com.atalaya.bestiario.Bestia;
import com.atalaya.bestiario.BestiaEntity;
import com.atalaya.bestiario.Camuflada;
import com.atalaya.bestiario.Fichas;
import com.atalaya.effect.CongeladoEffect;
import com.atalaya.effect.EnraizadoEffect;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.ResourceKey;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.damagesource.DamageType;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.PathfinderMob;
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
import net.minecraft.world.entity.npc.villager.AbstractVillager;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;
import org.jspecify.annotations.Nullable;

import java.util.EnumSet;
import java.util.UUID;

/**
 * Las plantas del bestiario.
 *
 * <pre>
 *   Fauces (verde, carmin, escarcha)  plantadas: no se mueven. Siguen con la cabeza al que se acerca y, si lo tienen a
 *                                     tiro (tres bloques), se echan atras y le muerden. La verde envenena (veneno II,
 *                                     cinco segundos), la carmin quema (cinco segundos; es del Nether y el fuego no le
 *                                     hace nada) y la de escarcha te congela (cinco segundos sin moverte, con la
 *                                     escarcha en la pantalla) y te envenena dos.
 *   Trampa Verde                      escondida en la hierba: al pisarla se cierra de golpe y te tiene tres segundos
 *                                     (enraizado y veneno II; mastica cada segundo); luego se abre y se vuelve a
 *                                     esconder. Si le pegas mientras espera, se cierra y te ensena las pestanas.
 *   Pina Brava                        chica, rapida y con mala leche: un punetazo cada ocho ticks (sin el respiro que
 *                                     da Minecraft entre golpe y golpe, o la mitad no harian nada).
 *   Zombi Planta                      un zombi comido por las plantas: cada golpe te clava al suelo (enraizado un
 *                                     segundo y lentitud IV, cuatro). Al sol no arde: florece y se cura.
 * </pre>
 */
public final class Plantas {

    private Plantas() {
    }

    private static AttributeSupplier.Builder base(double vida, double velocidad, double dano) {
        return Monster.createMonsterAttributes()
                .add(Attributes.MAX_HEALTH, vida)
                .add(Attributes.MOVEMENT_SPEED, velocidad)
                .add(Attributes.ATTACK_DAMAGE, dano)
                .add(Attributes.FOLLOW_RANGE, 24.0);
    }

    // ------------------------------------------------------------------
    //  Lo plantado: ni anda, ni se empuja, ni se lo lleva el agua
    // ------------------------------------------------------------------

    public abstract static class Plantada extends BestiaEntity {

        protected Plantada(EntityType<? extends Monster> tipo, Level nivel) {
            super(tipo, nivel);
        }

        @Override
        public boolean isPushable() {
            return false;
        }

        @Override
        protected void doPush(Entity otro) {
        }

        @Override
        public boolean isPushedByFluid() {
            return false;
        }

        @Override
        public boolean canBeLeashed() {
            return false;
        }
    }

    // ------------------------------------------------------------------
    //  Las Fauces
    // ------------------------------------------------------------------

    public abstract static class Fauces extends Plantada {

        /** Hasta donde llega el mordisco (desde su centro, en horizontal) y cada cuanto muerde (ticks). */
        private static final double ALCANCE = 3.0;
        private static final int ESPERA = 24;
        /** El fotograma en que la boca se cierra (0,28 s de su animacion de ataque). */
        private static final int CIERRA = 6;

        private int espera;

        protected Fauces(EntityType<? extends Monster> tipo, Level nivel) {
            super(tipo, nivel);
        }

        protected static AttributeSupplier.Builder atributosFauces(double dano) {
            return base(30.0, 0.0, dano)
                    .add(Attributes.ARMOR, 2.0)
                    .add(Attributes.KNOCKBACK_RESISTANCE, 1.0)
                    .add(Attributes.FOLLOW_RANGE, 12.0);
        }

        @Override
        protected void registerGoals() {
            goalSelector.addGoal(1, new Morder(this));
            goalSelector.addGoal(6, new LookAtPlayerGoal(this, Player.class, 10.0F));
            goalSelector.addGoal(7, new RandomLookAroundGoal(this));
            targetSelector.addGoal(1, new HurtByTargetGoal(this));
            targetSelector.addGoal(2, new NearestAttackableTargetGoal<>(this, Player.class, true));
        }

        @Override
        public void tick() {
            super.tick();
            if (espera > 0) {
                espera--;
            }
            if (level() instanceof ServerLevel nivel && isAlive() && tickCount % 30 == 0) {
                // Lo que le cae (o le sale) de la boca: acido, brasas o copos.
                Vec3 boca = boca();
                particulas(nivel, "savia", boca.x, boca.y, boca.z, 1, 0.12, 0.05, 0.01);
            }
        }

        /** Mas o menos donde tiene la boca (delante del tallo, a su altura). */
        protected Vec3 boca() {
            Vec3 frente = Vec3.directionFromRotation(0.0F, getYHeadRot()).scale(0.2);
            return new Vec3(getX() + frente.x, getY() + 1.15, getZ() + frente.z);
        }

        boolean aTiro(LivingEntity t) {
            double dx = t.getX() - getX();
            double dz = t.getZ() - getZ();
            double dy = t.getY() - getY();
            return dx * dx + dz * dz <= ALCANCE * ALCANCE && dy > -1.5 && dy < 2.5;
        }

        void morder() {
            espera = ESPERA;
            animar(EV_ATAQUE);
            sonar("mordisco", 1.0F);
            luego(CIERRA, () -> {
                LivingEntity v = presa();
                if (v != null && aTiro(v) && level() instanceof ServerLevel nivel) {
                    doHurtTarget(nivel, v);
                }
            });
        }

        @Override
        public boolean doHurtTarget(ServerLevel nivel, Entity objetivo) {
            boolean dio = super.doHurtTarget(nivel, objetivo);
            if (dio && objetivo instanceof LivingEntity v) {
                // La savia salta donde se cierra la boca (entre la planta y la presa, no en la cara de la presa: a quien
                // muerden no se le tapa la vista).
                Vec3 boca = boca();
                Vec3 hacia = v.position().subtract(boca).multiply(1.0, 0.0, 1.0).normalize().scale(0.45);
                particulas(nivel, "savia", boca.x + hacia.x, boca.y - 0.1, boca.z + hacia.z, 8, 0.2, 0.15, 0.08);
                particulas(nivel, "hoja", getX(), getY() + 1.2, getZ(), 3, 0.3, 0.2, 0.04);
                alMorder(nivel, v);
            }
            return dio;
        }

        protected abstract void alMorder(ServerLevel nivel, LivingEntity v);

        /** Mira a su presa y, si la tiene a tiro (y la ve) y ya le toca, muerde. */
        static final class Morder extends Goal {

            private final Fauces f;

            Morder(Fauces f) {
                this.f = f;
                setFlags(EnumSet.of(Flag.LOOK));
            }

            @Override
            public boolean canUse() {
                LivingEntity t = f.presa();
                return t != null && f.distanceToSqr(t) < 14.0 * 14.0;
            }

            @Override
            public boolean requiresUpdateEveryTick() {
                return true;
            }

            @Override
            public void tick() {
                LivingEntity t = f.presa();
                if (t == null) {
                    return;
                }
                f.getLookControl().setLookAt(t, 30.0F, 30.0F);
                if (f.espera <= 0 && f.aTiro(t) && f.getSensing().hasLineOfSight(t)) {
                    f.morder();
                }
            }
        }
    }

    public static class FaucesVerde extends Fauces {

        public FaucesVerde(EntityType<? extends Monster> tipo, Level nivel) {
            super(tipo, nivel);
        }

        public static AttributeSupplier.Builder atributos() {
            return atributosFauces(5.0);
        }

        @Override
        public Bestia bestia() {
            return Fichas.FAUCES_VERDE;
        }

        @Override
        protected void alMorder(ServerLevel nivel, LivingEntity v) {
            BestiaEntity.efecto(v, MobEffects.POISON, 100, 1, this);
            sonar("acido", 0.9F);
        }
    }

    public static class FaucesCarmin extends Fauces {

        public FaucesCarmin(EntityType<? extends Monster> tipo, Level nivel) {
            super(tipo, nivel);
        }

        public static AttributeSupplier.Builder atributos() {
            return atributosFauces(5.0);
        }

        @Override
        public Bestia bestia() {
            return Fichas.FAUCES_CARMIN;
        }

        @Override
        protected void alMorder(ServerLevel nivel, LivingEntity v) {
            v.setRemainingFireTicks(Math.max(v.getRemainingFireTicks(), 100));
            sonar("quema", 1.0F);
        }
    }

    public static class FaucesEscarcha extends Fauces {

        public FaucesEscarcha(EntityType<? extends Monster> tipo, Level nivel) {
            super(tipo, nivel);
        }

        public static AttributeSupplier.Builder atributos() {
            return atributosFauces(4.0);
        }

        @Override
        public Bestia bestia() {
            return Fichas.FAUCES_ESCARCHA;
        }

        @Override
        public void tick() {
            super.tick();
            if (level() instanceof ServerLevel nivel && isAlive() && tickCount % 12 == 0) {
                particulas(nivel, "escarcha", getX(), getY() + 1.3, getZ(), 1, 0.4, 0.3, 0.01);
            }
        }

        @Override
        protected void alMorder(ServerLevel nivel, LivingEntity v) {
            v.addEffect(new MobEffectInstance(CongeladoEffect.CONGELADO, 100, 0), this);
            BestiaEntity.efecto(v, MobEffects.POISON, 40, 0, this);
            v.clearFire();
            sonar("hiela", 1.0F);
            // Los copos, por las piernas (a la altura de los ojos taparian la vista).
            particulas(nivel, "escarcha", v.getX(), v.getY() + 0.4, v.getZ(), 16, 0.4, 0.25, 0.03);
        }
    }

    // ------------------------------------------------------------------
    //  La Trampa Verde
    // ------------------------------------------------------------------

    public static class Trampa extends Plantada implements Camuflada {

        private static final int ESCONDIDA = 1;
        /** Lo que te tiene (ticks), lo que tarda en poder volver a cerrarse y lo que se queda cerrada si la golpean. */
        private static final int SUJETA = 60;
        private static final int RESPIRO = 100;
        private static final int ENFADADA = 80;

        private @Nullable UUID atrapado;
        private int sujeta;
        private int respiro;
        private int cerrada;

        public Trampa(EntityType<? extends Monster> tipo, Level nivel) {
            super(tipo, nivel);
            setEstado(ESCONDIDA);
        }

        public static AttributeSupplier.Builder atributos() {
            return base(20.0, 0.0, 3.0)
                    .add(Attributes.KNOCKBACK_RESISTANCE, 1.0)
                    .add(Attributes.FOLLOW_RANGE, 4.0);
        }

        @Override
        public Bestia bestia() {
            return Fichas.TRAMPA;
        }

        @Override
        protected void registerGoals() {
            // Nada: espera a que la pisen.
        }

        @Override
        public boolean camuflada() {
            return getEstado() == ESCONDIDA;
        }

        @Override
        public void tick() {
            super.tick();
            if (!(level() instanceof ServerLevel nivel) || !isAlive()) {
                return;
            }
            if (respiro > 0) {
                respiro--;
            }
            if (atrapado != null) {
                sujetar(nivel);
                return;
            }
            if (cerrada > 0) {
                if (--cerrada == 0) {
                    esconder();
                }
                return;
            }
            if (getEstado() == ESCONDIDA && respiro <= 0) {
                AABB pisada = new AABB(getX() - 0.7, getY() - 0.2, getZ() - 0.7, getX() + 0.7, getY() + 0.7,
                        getZ() + 0.7);
                for (Player p : nivel.getEntitiesOfClass(Player.class, pisada,
                        p -> p.isAlive() && !p.isSpectator() && !p.isCreative())) {
                    atrapar(nivel, p);
                    break;
                }
            }
        }

        private void atrapar(ServerLevel nivel, LivingEntity v) {
            atrapado = v.getUUID();
            sujeta = SUJETA;
            setEstado(0);
            animar(EV_APARECE);
            sonar("cierra", 1.4F);
            // Al centro de la trampa: que se vea que te tiene cogido.
            v.teleportTo(getX(), v.getY(), getZ());
            v.setDeltaMovement(Vec3.ZERO);
            v.addEffect(new MobEffectInstance(EnraizadoEffect.ENRAIZADO, SUJETA, 0), this);
            BestiaEntity.efecto(v, MobEffects.POISON, SUJETA, 1, this);
            v.hurtServer(nivel, damageSources().mobAttack(this), (float) getAttributeValue(Attributes.ATTACK_DAMAGE));
            particulas(nivel, "hoja", getX(), getY() + 0.4, getZ(), 14, 0.5, 0.2, 0.12);
            particulas(nivel, "pestana", getX(), getY() + 0.6, getZ(), 8, 0.4, 0.2, 0.1);
        }

        private void sujetar(ServerLevel nivel) {
            Entity e = nivel.getEntity(atrapado);
            if (!(e instanceof LivingEntity v) || !v.isAlive() || v.distanceToSqr(this) > 2.0 * 2.0 || --sujeta <= 0) {
                atrapado = null;
                respiro = RESPIRO;
                esconder();
                return;
            }
            if (sujeta % 20 == 0) {
                animar(EV_ATAQUE);
                sonar("mastica", 1.0F);
                particulas(nivel, "hoja", getX(), getY() + 0.5, getZ(), 4, 0.4, 0.2, 0.05);
            }
        }

        private void esconder() {
            setEstado(ESCONDIDA);
            animar(EV_ESPECIAL);
            sonar("abre", 0.8F);
        }

        /** Si le pegas mientras espera, se cierra de golpe (y se queda asi un rato, ensenando las pestanas). */
        @Override
        public boolean hurtServer(ServerLevel nivel, DamageSource fuente, float dano) {
            boolean herida = super.hurtServer(nivel, fuente, dano);
            if (herida && isAlive() && atrapado == null && getEstado() == ESCONDIDA) {
                setEstado(0);
                animar(EV_APARECE);
                sonar("cierra", 1.2F);
                cerrada = ENFADADA;
            }
            return herida;
        }
    }

    // ------------------------------------------------------------------
    //  La Pina Brava
    // ------------------------------------------------------------------

    public static class Pina extends BestiaEntity {

        /** El dano de su punetazo (atalaya:pina: no empuja, damage_type/no_knockback). */
        public static final ResourceKey<DamageType> PUNETAZO = ResourceKey.create(Registries.DAMAGE_TYPE,
                Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "pina"));

        public Pina(EntityType<? extends Monster> tipo, Level nivel) {
            super(tipo, nivel);
        }

        public static AttributeSupplier.Builder atributos() {
            return base(14.0, 0.34, 2.5);
        }

        @Override
        public Bestia bestia() {
            return Fichas.PINA;
        }

        @Override
        protected void registerGoals() {
            goalSelector.addGoal(1, new FloatGoal(this));
            goalSelector.addGoal(3, new Rafaga(this));
            goalSelector.addGoal(5, new WaterAvoidingRandomStrollGoal(this, 0.9));
            goalSelector.addGoal(6, new LookAtPlayerGoal(this, Player.class, 8.0F));
            goalSelector.addGoal(6, new RandomLookAroundGoal(this));
            targetSelector.addGoal(1, new HurtByTargetGoal(this).setAlertOthers());
            targetSelector.addGoal(2, new NearestAttackableTargetGoal<>(this, Player.class, true));
        }

        /**
         * Su punetazo: un dano propio que no empuja (con el empujon de siempre te sacaria de su alcance a cada golpe y
         * no podria encadenarlos), un empujoncito suyo de nada y sin el respiro entre golpe y golpe.
         */
        @Override
        public boolean doHurtTarget(ServerLevel nivel, Entity objetivo) {
            animar(EV_ATAQUE);
            sonar("puno", 0.9F);
            if (!(objetivo instanceof LivingEntity v)) {
                return false;
            }
            DamageSource golpe = new DamageSource(nivel.registryAccess().lookupOrThrow(Registries.DAMAGE_TYPE)
                    .getOrThrow(PUNETAZO), this);
            boolean dio = v.hurtServer(nivel, golpe, (float) getAttributeValue(Attributes.ATTACK_DAMAGE));
            if (dio) {
                setLastHurtMob(v);
                v.invulnerableTime = Math.min(v.invulnerableTime, 10);
                Vec3 empuje = v.position().subtract(position()).multiply(1.0, 0.0, 1.0).normalize().scale(0.12);
                v.push(empuje.x, 0.02, empuje.z);
                v.hurtMarked = true;
                particulas(nivel, "jugo", v.getX(), v.getY() + v.getBbHeight() * 0.35, v.getZ(), 3, 0.25, 0.15, 0.06);
            }
            return dio;
        }

        /** El cuerpo a cuerpo de siempre, con un golpe cada ocho ticks en vez de cada veinte. */
        static final class Rafaga extends MeleeAttackGoal {

            private int espera;

            Rafaga(PathfinderMob mob) {
                super(mob, 1.25, true);
            }

            @Override
            public void start() {
                super.start();
                espera = 0;
            }

            @Override
            public void tick() {
                super.tick();
                if (espera > 0) {
                    espera--;
                }
            }

            @Override
            protected boolean isTimeToAttack() {
                return espera <= 0;
            }

            @Override
            protected void resetAttackCooldown() {
                espera = 8;
            }
        }
    }

    // ------------------------------------------------------------------
    //  El Zombi Planta
    // ------------------------------------------------------------------

    public static class ZombiPlanta extends BestiaEntity {

        public ZombiPlanta(EntityType<? extends Monster> tipo, Level nivel) {
            super(tipo, nivel);
        }

        public static AttributeSupplier.Builder atributos() {
            return base(26.0, 0.23, 4.0)
                    .add(Attributes.ARMOR, 2.0)
                    .add(Attributes.FOLLOW_RANGE, 35.0);
        }

        @Override
        public Bestia bestia() {
            return Fichas.ZOMBI_PLANTA;
        }

        @Override
        protected void registerGoals() {
            goalSelector.addGoal(1, new FloatGoal(this));
            goalSelector.addGoal(2, new MeleeAttackGoal(this, 1.0, false));
            goalSelector.addGoal(7, new WaterAvoidingRandomStrollGoal(this, 0.8));
            goalSelector.addGoal(8, new LookAtPlayerGoal(this, Player.class, 8.0F));
            goalSelector.addGoal(8, new RandomLookAroundGoal(this));
            targetSelector.addGoal(1, new HurtByTargetGoal(this));
            targetSelector.addGoal(2, new NearestAttackableTargetGoal<>(this, Player.class, true));
            targetSelector.addGoal(3, new NearestAttackableTargetGoal<>(this, AbstractVillager.class, false));
        }

        @Override
        public boolean doHurtTarget(ServerLevel nivel, Entity objetivo) {
            animar(EV_ATAQUE);
            boolean dio = super.doHurtTarget(nivel, objetivo);
            if (dio && objetivo instanceof LivingEntity v) {
                v.addEffect(new MobEffectInstance(EnraizadoEffect.ENRAIZADO, 20, 0), this);
                BestiaEntity.efecto(v, MobEffects.SLOWNESS, 80, 3, this);
                sonar("enraiza", 1.0F);
                particulas(nivel, "raiz", v.getX(), v.getY() + 0.1, v.getZ(), 12, 0.35, 0.05, 0.08);
            }
            return dio;
        }

        @Override
        public void tick() {
            super.tick();
            if (level() instanceof ServerLevel nivel && isAlive() && tickCount % 40 == 0 && alSol(nivel)) {
                if (getHealth() < getMaxHealth()) {
                    heal(2.0F);
                    particulas(nivel, "polen", getX(), getY() + 1.9, getZ(), 6, 0.4, 0.3, 0.02);
                    if (random.nextInt(3) == 0) {
                        sonar("florece", 0.7F);
                    }
                } else if (random.nextInt(4) == 0) {
                    particulas(nivel, "polen", getX(), getY() + 2.0, getZ(), 2, 0.3, 0.2, 0.01);
                }
            }
        }

        /** De dia, sin llover encima y con el cielo a la vista. */
        private boolean alSol(ServerLevel nivel) {
            BlockPos cabeza = BlockPos.containing(getX(), getEyeY(), getZ());
            return nivel.isBrightOutside() && !nivel.isRainingAt(cabeza) && nivel.canSeeSky(cabeza);
        }
    }
}
