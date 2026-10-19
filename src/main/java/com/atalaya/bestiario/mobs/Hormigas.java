package com.atalaya.bestiario.mobs;

import com.atalaya.bestiario.Bestia;
import com.atalaya.bestiario.BestiaEntity;
import com.atalaya.bestiario.BestiaRed;
import com.atalaya.bestiario.Fichas;
import com.atalaya.effect.RadiacionEffect;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerTickEvents;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.FloatGoal;
import net.minecraft.world.entity.ai.goal.LookAtPlayerGoal;
import net.minecraft.world.entity.ai.goal.MeleeAttackGoal;
import net.minecraft.world.entity.ai.goal.RandomLookAroundGoal;
import net.minecraft.world.entity.ai.goal.WaterAvoidingRandomStrollGoal;
import net.minecraft.world.entity.ai.goal.target.HurtByTargetGoal;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;

import java.util.HashSet;
import java.util.Iterator;
import java.util.Set;
import java.util.UUID;

/**
 * Las hormigas del bestiario: van en grupo, muerden con las mandibulas y cada una deja lo suyo. A ninguna le hacen mas
 * dano Castigo ni Perdicion de los artropodos (no estan en esas listas).
 *
 * <pre>
 *   Lancera     la soldado: pega fuerte con su lanza (algo mas de alcance)
 *   Polvorin    lleva una bomba: cuando te tiene cerca se le enciende y revienta; todo el que este a quince bloques se
 *               queda alucinando diez segundos (la pantalla se le tuerce de colores y se marea)
 *   Cabezona    su mordisco te deja lentisimo (lentitud III, cinco segundos)
 *   Radiactiva  su mordisco deja radiacion (cinco segundos, la de las geodas)
 *   Brasa       tocarla (o que te muerda) te prende un fuego que no se apaga hasta que te metes en el agua o te llueve
 * </pre>
 */
public final class Hormigas {

    /** Los que arden por la Hormiga Brasa (hasta que les toca el agua). */
    private static final Set<UUID> ARDIENDO = new HashSet<>();

    private Hormigas() {
    }

    public static void registrarEventos() {
        ServerTickEvents.END_SERVER_TICK.register(Hormigas::avivar);
    }

    /** El fuego de la Brasa: se aviva cada tick hasta que el agua lo apaga (o muere el que arde). */
    private static void avivar(MinecraftServer servidor) {
        if (ARDIENDO.isEmpty()) {
            return;
        }
        for (Iterator<UUID> it = ARDIENDO.iterator(); it.hasNext(); ) {
            ServerPlayer p = servidor.getPlayerList().getPlayer(it.next());
            if (p == null || !p.isAlive() || p.isCreative() || p.isSpectator() || p.isInWaterOrRain()) {
                if (p != null && p.isInWaterOrRain()) {
                    p.clearFire();
                }
                it.remove();
                continue;
            }
            if (p.getRemainingFireTicks() < 20) {
                p.setRemainingFireTicks(60);
            }
        }
    }

    static void prender(LivingEntity v) {
        v.setRemainingFireTicks(Math.max(v.getRemainingFireTicks(), 100));
        if (v instanceof ServerPlayer p && !p.isCreative() && !p.isSpectator()) {
            ARDIENDO.add(p.getUUID());
        }
    }

    private static AttributeSupplier.Builder base(double vida, double velocidad, double dano) {
        return Monster.createMonsterAttributes()
                .add(Attributes.MAX_HEALTH, vida)
                .add(Attributes.MOVEMENT_SPEED, velocidad)
                .add(Attributes.ATTACK_DAMAGE, dano)
                .add(Attributes.FOLLOW_RANGE, 24.0);
    }

    // ------------------------------------------------------------------
    //  La base
    // ------------------------------------------------------------------

    public abstract static class Hormiga extends BestiaEntity {

        protected Hormiga(EntityType<? extends Monster> tipo, Level nivel) {
            super(tipo, nivel);
        }

        @Override
        protected void registerGoals() {
            goalSelector.addGoal(1, new FloatGoal(this));
            metas();
            goalSelector.addGoal(5, new WaterAvoidingRandomStrollGoal(this, 0.8));
            goalSelector.addGoal(6, new LookAtPlayerGoal(this, Player.class, 8.0F));
            goalSelector.addGoal(6, new RandomLookAroundGoal(this));
            targetSelector.addGoal(1, new HurtByTargetGoal(this).setAlertOthers());
            targetSelector.addGoal(2, new NearestAttackableTargetGoal<>(this, Player.class, true));
        }

        protected void metas() {
            goalSelector.addGoal(4, new MeleeAttackGoal(this, 1.1, true));
        }

        @Override
        public boolean doHurtTarget(ServerLevel nivel, Entity objetivo) {
            animar(EV_ATAQUE);
            sonar("mordisco", 1.0F);
            boolean dio = super.doHurtTarget(nivel, objetivo);
            if (dio && objetivo instanceof LivingEntity v) {
                alMorder(nivel, v);
            }
            return dio;
        }

        protected void alMorder(ServerLevel nivel, LivingEntity v) {
        }
    }

    // ------------------------------------------------------------------
    //  Las cinco
    // ------------------------------------------------------------------

    public static class Lancera extends Hormiga {

        public Lancera(EntityType<? extends Monster> tipo, Level nivel) {
            super(tipo, nivel);
        }

        public static AttributeSupplier.Builder atributos() {
            return base(16.0, 0.3, 6.0).add(Attributes.ENTITY_INTERACTION_RANGE, 1.0);
        }

        @Override
        public Bestia bestia() {
            return Fichas.LANCERA;
        }
    }

    public static class Polvorin extends Hormiga {

        private int mecha = -1;

        public Polvorin(EntityType<? extends Monster> tipo, Level nivel) {
            super(tipo, nivel);
        }

        public static AttributeSupplier.Builder atributos() {
            return base(12.0, 0.32, 2.0);
        }

        @Override
        public Bestia bestia() {
            return Fichas.POLVORIN;
        }

        @Override
        public void tick() {
            super.tick();
            if (!(level() instanceof ServerLevel nivel) || !isAlive()) {
                return;
            }
            LivingEntity t = presa();
            if (mecha < 0 && t != null && distanceToSqr(t) < 2.6 * 2.6) {
                mecha = 0;
                animar(EV_ESPECIAL);
                sonar("mecha", 1.2F);
            }
            if (mecha >= 0) {
                mecha++;
                if (mecha % 3 == 0) {
                    particulas(nivel, "chispa", getX(), getY() + 1.1, getZ(), 2, 0.1, 0.1, 0.05);
                }
                if (mecha >= 30) {
                    reventar(nivel);
                }
            }
        }

        private void reventar(ServerLevel nivel) {
            if (isRemoved()) {
                return;
            }
            dead = true;
            estallido(nivel, this, bestia(), getX(), getY() + 0.5, getZ(), 2.5F, false, "barro", "estalla");
            particulas(nivel, "barro", getX(), getY() + 0.6, getZ(), 30, 0.8, 0.5, 0.35);
            particulas(nivel, "humo", getX(), getY() + 0.6, getZ(), 14, 1.4, 0.8, 0.05);
            for (ServerPlayer p : nivel.players()) {
                if (!p.isSpectator() && !p.isCreative() && p.distanceToSqr(this) < 15 * 15) {
                    BestiaRed.pantalla(p, BestiaRed.ALUCINACION, 200);
                    BestiaEntity.efecto(p, MobEffects.NAUSEA, 200, 0, this);
                }
            }
            discard();
        }
    }

    public static class Cabezona extends Hormiga {

        public Cabezona(EntityType<? extends Monster> tipo, Level nivel) {
            super(tipo, nivel);
        }

        public static AttributeSupplier.Builder atributos() {
            return base(20.0, 0.27, 5.0).add(Attributes.KNOCKBACK_RESISTANCE, 0.3);
        }

        @Override
        public Bestia bestia() {
            return Fichas.CABEZONA;
        }

        @Override
        protected void alMorder(ServerLevel nivel, LivingEntity v) {
            BestiaEntity.efecto(v, MobEffects.SLOWNESS, 100, 2, this);
        }
    }

    public static class Radiactiva extends Hormiga {

        public Radiactiva(EntityType<? extends Monster> tipo, Level nivel) {
            super(tipo, nivel);
        }

        public static AttributeSupplier.Builder atributos() {
            return base(14.0, 0.3, 4.0);
        }

        @Override
        public Bestia bestia() {
            return Fichas.RADIACTIVA;
        }

        @Override
        public void tick() {
            super.tick();
            if (level() instanceof ServerLevel nivel && isAlive() && tickCount % 16 == 0) {
                particulas(nivel, "radiacion", getX(), getY() + 0.6, getZ(), 1, 0.3, 0.2, 0.01);
            }
        }

        @Override
        protected void alMorder(ServerLevel nivel, LivingEntity v) {
            v.addEffect(new MobEffectInstance(RadiacionEffect.RADIACION, 100, 1), this);
        }
    }

    public static class Brasa extends Hormiga {

        public Brasa(EntityType<? extends Monster> tipo, Level nivel) {
            super(tipo, nivel);
        }

        public static AttributeSupplier.Builder atributos() {
            return base(14.0, 0.31, 4.0);
        }

        @Override
        public Bestia bestia() {
            return Fichas.BRASA;
        }

        @Override
        public void tick() {
            super.tick();
            if (level() instanceof ServerLevel nivel && isAlive() && tickCount % 10 == 0) {
                particulas(nivel, "brasa", getX(), getY() + 0.7, getZ(), 1, 0.3, 0.2, 0.01);
            }
        }

        @Override
        protected void alMorder(ServerLevel nivel, LivingEntity v) {
            prender(v);
            sonar("quema", 1.0F);
        }

        /** Quien la toca con la mano (un golpe cuerpo a cuerpo) tambien se prende. */
        @Override
        public boolean hurtServer(ServerLevel nivel, DamageSource fuente, float dano) {
            boolean herida = super.hurtServer(nivel, fuente, dano);
            if (fuente.getDirectEntity() instanceof Player p && fuente.getEntity() == p) {
                prender(p);
                sonar("quema", 1.0F);
            }
            return herida;
        }
    }
}
