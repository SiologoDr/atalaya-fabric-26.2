package com.atalaya.bestiario.mobs;

import com.atalaya.Atalaya;
import com.atalaya.bestiario.Bestia;
import com.atalaya.bestiario.BestiaEntity;
import com.atalaya.bestiario.CorazonesRobados;
import com.atalaya.bestiario.Fichas;
import com.atalaya.effect.EnraizadoEffect;
import com.atalaya.item.AtalayaItems;
import com.atalaya.mixin.TotemInvoker;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.ResourceKey;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.util.Mth;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.damagesource.DamageType;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.control.FlyingMoveControl;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.entity.ai.goal.LookAtPlayerGoal;
import net.minecraft.world.entity.ai.goal.target.HurtByTargetGoal;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.ai.navigation.FlyingPathNavigation;
import net.minecraft.world.entity.ai.navigation.PathNavigation;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.storage.ValueInput;
import net.minecraft.world.level.storage.ValueOutput;
import net.minecraft.world.phys.Vec3;
import org.jspecify.annotations.Nullable;

import java.util.EnumSet;
import java.util.List;
import java.util.UUID;

/**
 * Los fantasmas del bestiario (DEDsafio 3 y 4), recreados de sus dibujos: la cabeza con su cara, el cuerpo que flota
 * (no tienen piernas: vuelan) y los brazos en «¡bu!». Todos vuelan, te ven desde lejos y van a por ti, y cualquier arma
 * les hace dano (Juan, 19-10-2026: «la espada fantasmal no la hagas, que cualquier arma les haga dano»). Su zarpazo no
 * empuja (atalaya:fantasma). Cada uno, lo suyo:
 *
 * <pre>
 *   Blanco    golpea rapidisimo (un zarpazo cada ocho ticks) y cada zarpazo te deja con Lentitud
 *   Negro     cada golpe te quita un corazon para siempre (CorazonesRobados); al morir suelta un Corazon Blanco por
 *             cada uno que robo, que te lo devuelve
 *   Amarillo  su golpe te hace gastar un totem (si llevas uno en la mano); luego se te mete dentro y, a los cinco
 *             segundos, sale a dos bloques y va a por otro jugador de cerca (si no hay otro, a por ti), sin pegar
 *             durante dos segundos
 *   Rojo      te agarra y no te suelta: te deja clavado donde estas y te sigue pegando hasta que muere el o mueres tu
 *             (gastando totem tras totem)
 * </pre>
 */
public final class Fantasmas {

    /** Su zarpazo: un dano propio que no empuja (con el empujon no podrian encadenar los golpes ni sujetarte). */
    public static final ResourceKey<DamageType> ZARPAZO = ResourceKey.create(Registries.DAMAGE_TYPE,
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "fantasma"));

    private Fantasmas() {
    }

    private static AttributeSupplier.Builder base(double vida, double vuelo, double dano) {
        return Monster.createMonsterAttributes()
                .add(Attributes.MAX_HEALTH, vida)
                .add(Attributes.FLYING_SPEED, vuelo)
                .add(Attributes.MOVEMENT_SPEED, vuelo * 0.6)
                .add(Attributes.ATTACK_DAMAGE, dano)
                .add(Attributes.FOLLOW_RANGE, 32.0);
    }

    private static boolean jugable(@Nullable Entity e) {
        return e instanceof LivingEntity v && v.isAlive() && !v.isSpectator()
                && !(v instanceof Player p && p.isCreative());
    }

    // ------------------------------------------------------------------
    //  La base
    // ------------------------------------------------------------------

    /**
     * Lo de todos: vuela como las bombas (sin caer ni hacerse dano al caer), va a por el jugador que ve, se le pone
     * delante a la altura de la cara y le da zarpazos (cada 'cadencia' ticks); sin nadie, revolotea por la zona.
     */
    public abstract static class Fantasma extends BestiaEntity {

        /** Los ticks entre zarpazo y zarpazo. */
        protected int cadencia = 20;
        private int espera;

        protected Fantasma(EntityType<? extends Monster> tipo, Level nivel) {
            super(tipo, nivel);
            this.moveControl = new FlyingMoveControl(this, 20, true);
            setNoGravity(true);
        }

        @Override
        protected PathNavigation createNavigation(Level nivel) {
            return new FlyingPathNavigation(this, nivel);
        }

        @Override
        protected void registerGoals() {
            goalSelector.addGoal(1, new Acosar());
            goalSelector.addGoal(5, new Revolotear());
            goalSelector.addGoal(6, new LookAtPlayerGoal(this, Player.class, 16.0F));
            targetSelector.addGoal(1, new HurtByTargetGoal(this));
            targetSelector.addGoal(2, new NearestAttackableTargetGoal<>(this, Player.class, true));
        }

        /** Si ahora va a por su presa (el Amarillo dentro de alguien o el Rojo agarrando, no). */
        protected boolean acosa() {
            return true;
        }

        @Override
        public void tick() {
            super.tick();
            if (espera > 0) {
                espera--;
            }
        }

        /** Que tarde un rato en volver a dar un zarpazo. */
        protected void descansar(int ticks) {
            espera = Math.max(espera, ticks);
        }

        /** Su zarpazo: la animacion, el sonido, el dano (que no empuja) y lo suyo si le ha dado. */
        protected boolean zarpazo(ServerLevel nivel, LivingEntity v) {
            espera = cadencia;
            animar(EV_ATAQUE);
            sonar("zarpazo", 0.9F);
            boolean dio = doHurtTarget(nivel, v);
            if (dio) {
                alDar(nivel, v);
            }
            return dio;
        }

        @Override
        public boolean doHurtTarget(ServerLevel nivel, Entity objetivo) {
            if (!(objetivo instanceof LivingEntity v)) {
                return false;
            }
            boolean dio = v.hurtServer(nivel, golpe(nivel), (float) getAttributeValue(Attributes.ATTACK_DAMAGE));
            if (dio) {
                setLastHurtMob(v);
            }
            return dio;
        }

        protected DamageSource golpe(ServerLevel nivel) {
            return new DamageSource(nivel.registryAccess().lookupOrThrow(Registries.DAMAGE_TYPE).getOrThrow(ZARPAZO), this);
        }

        /** Lo de cada uno cuando su zarpazo da. */
        protected abstract void alDar(ServerLevel nivel, LivingEntity v);

        /** Mirar a algo (la cabeza y el cuerpo). */
        protected void mirarA(Entity e) {
            double dx = e.getX() - getX();
            double dz = e.getZ() - getZ();
            float giro = (float) (Mth.atan2(dz, dx) * Mth.RAD_TO_DEG) - 90.0F;
            setYRot(giro);
            yBodyRot = giro;
            yHeadRot = giro;
        }

        /** Vuela como la abeja (lo de siempre, en el aire, va frenadisimo). */
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

        /** Ir a por la presa: delante de ella, a la altura de su cara, y darle zarpazos en cuanto la tenga al alcance. */
        private final class Acosar extends Goal {
            Acosar() {
                setFlags(EnumSet.of(Flag.MOVE, Flag.LOOK));
            }

            @Override
            public boolean canUse() {
                return acosa() && presa() != null;
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
                Vec3 lado = position().subtract(t.position()).multiply(1.0, 0.0, 1.0);
                lado = lado.lengthSqr() < 1.0E-4 ? new Vec3(0.0, 0.0, 1.0) : lado.normalize();
                double cerca = getBbWidth() * 0.5 + t.getBbWidth() * 0.5 + 0.5;
                Vec3 meta = t.position().add(lado.scale(cerca)).add(0.0, 0.1, 0.0);
                Vec3 falta = meta.subtract(position());
                if (falta.length() < 4.5) {
                    // La recta final, directa y sin pasarse: se le planta delante.
                    Vec3 v = falta.scale(0.3);
                    if (v.length() > 0.5) {
                        v = v.normalize().scale(0.5);
                    }
                    setDeltaMovement(v);
                    mirarA(t);
                } else {
                    getMoveControl().setWantedPosition(meta.x, meta.y, meta.z, 1.0);
                }
                getLookControl().setLookAt(t, 30.0F, 30.0F);
                if (espera <= 0 && alAlcance(t, 0.9) && getSensing().hasLineOfSight(t)) {
                    zarpazo(nivel, t);
                }
            }
        }

        /** Revolotear por la zona cuando no tiene a nadie: un punto al azar cerca, en el aire. */
        private final class Revolotear extends Goal {
            Revolotear() {
                setFlags(EnumSet.of(Flag.MOVE));
            }

            @Override
            public boolean canUse() {
                return acosa() && presa() == null && !getMoveControl().hasWanted() && random.nextInt(20) == 0;
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

    // ------------------------------------------------------------------
    //  El Blanco
    // ------------------------------------------------------------------

    public static class Blanco extends Fantasma {

        /** Lo que dura la Lentitud de cada zarpazo (se alarga con cada uno, hasta el doble). */
        private static final int LENTITUD = 60;

        public Blanco(EntityType<? extends Monster> tipo, Level nivel) {
            super(tipo, nivel);
            cadencia = 8;
        }

        public static AttributeSupplier.Builder atributos() {
            return base(20.0, 0.6, 2.0);
        }

        @Override
        public Bestia bestia() {
            return Fichas.ESPECTRO_BLANCO;
        }

        @Override
        protected void alDar(ServerLevel nivel, LivingEntity v) {
            v.invulnerableTime = Math.min(v.invulnerableTime, 6);
            MobEffectInstance antes = v.getEffect(MobEffects.SLOWNESS);
            int ticks = Math.min(LENTITUD * 2, (antes != null ? antes.getDuration() : 0) + LENTITUD / 2 + 10);
            BestiaEntity.efecto(v, MobEffects.SLOWNESS, Math.max(LENTITUD, ticks), 1, this);
            particulas(nivel, "escarcha", v.getX(), v.getY() + 0.5, v.getZ(), 6, 0.3, 0.3, 0.02);
        }
    }

    // ------------------------------------------------------------------
    //  El Negro
    // ------------------------------------------------------------------

    public static class Negro extends Fantasma {

        /** Los corazones que lleva robados (los suelta en Corazones Blancos al morir). */
        private int robados;

        public Negro(EntityType<? extends Monster> tipo, Level nivel) {
            super(tipo, nivel);
            cadencia = 30;
        }

        public static AttributeSupplier.Builder atributos() {
            return base(26.0, 0.5, 3.0);
        }

        @Override
        public Bestia bestia() {
            return Fichas.ESPECTRO_NEGRO;
        }

        @Override
        protected void alDar(ServerLevel nivel, LivingEntity v) {
            if (v instanceof ServerPlayer p && !p.isCreative() && CorazonesRobados.robar(p)) {
                robados++;
                setPersistenceRequired();
                sonar("roba", 1.0F);
                // El corazon sale de su pecho y se va al fantasma.
                Vec3 de = p.position().add(0.0, p.getBbHeight() * 0.6, 0.0);
                Vec3 a = position().add(0.0, getBbHeight() * 0.5, 0.0).subtract(de);
                for (int i = 0; i <= 4; i++) {
                    Vec3 q = de.add(a.scale(i / 4.0));
                    particulas(nivel, "corazon", q.x, q.y, q.z, 2, 0.1, 0.1, 0.01);
                }
            }
        }

        @Override
        protected void dropCustomDeathLoot(ServerLevel nivel, DamageSource fuente, boolean reciente) {
            super.dropCustomDeathLoot(nivel, fuente, reciente);
            if (robados > 0) {
                spawnAtLocation(nivel, new ItemStack(AtalayaItems.CORAZON_BLANCO, robados));
            }
        }

        @Override
        protected void addAdditionalSaveData(ValueOutput salida) {
            super.addAdditionalSaveData(salida);
            salida.putInt("Robados", robados);
        }

        @Override
        protected void readAdditionalSaveData(ValueInput entrada) {
            super.readAdditionalSaveData(entrada);
            robados = entrada.getIntOr("Robados", 0);
        }
    }

    // ------------------------------------------------------------------
    //  El Amarillo
    // ------------------------------------------------------------------

    public static class Amarillo extends Fantasma {

        private static final int DENTRO = 1;
        /** Lo que esta dentro de alguien antes de salir y lo que tarda en volver a pegar al salir (ticks). */
        private static final int POSESION = 100;
        private static final int SALIDO = 40;

        private @Nullable UUID huesped;
        private int dentro;

        public Amarillo(EntityType<? extends Monster> tipo, Level nivel) {
            super(tipo, nivel);
            cadencia = 20;
        }

        public static AttributeSupplier.Builder atributos() {
            return base(22.0, 0.6, 3.0);
        }

        @Override
        public Bestia bestia() {
            return Fichas.ESPECTRO_AMARILLO;
        }

        @Override
        protected boolean acosa() {
            return huesped == null;
        }

        @Override
        protected void alDar(ServerLevel nivel, LivingEntity v) {
            if (!(v instanceof ServerPlayer p) || p.isCreative()) {
                return;
            }
            // Te hace gastar un totem (el de la mano, como si fueras a morir).
            ((TotemInvoker) p).atalaya$gastarTotem(golpe(nivel));
            // Y se te mete dentro.
            huesped = p.getUUID();
            dentro = POSESION;
            setEstado(DENTRO);
            setInvisible(true);
            setInvulnerable(true);
            noPhysics = true;
            getNavigation().stop();
            sonar("posee", 1.0F);
            particulas(nivel, "chispa", p.getX(), p.getY() + 1.0, p.getZ(), 20, 0.3, 0.5, 0.06);
        }

        @Override
        public void tick() {
            super.tick();
            if (huesped == null || !(level() instanceof ServerLevel nivel) || !isAlive()) {
                return;
            }
            Entity e = nivel.getEntity(huesped);
            if (!jugable(e)) {
                salir(nivel, null);
                return;
            }
            setPos(e.getX(), e.getY() + 0.1, e.getZ());
            setDeltaMovement(Vec3.ZERO);
            if (dentro % 10 == 0) {
                particulas(nivel, "chispa", e.getX(), e.getY() + 1.0, e.getZ(), 3, 0.25, 0.4, 0.02);
            }
            if (--dentro <= 0) {
                salir(nivel, (LivingEntity) e);
            }
        }

        /**
         * Sale del que poseia (o de donde estaba, si ya no esta) y va a por otro jugador de cerca; si no hay, a por el.
         * Tarda dos segundos en volver a pegar: que se le vea fuera y se le pueda dar.
         */
        private void salir(ServerLevel nivel, @Nullable LivingEntity de) {
            huesped = null;
            setEstado(0);
            setInvisible(false);
            setInvulnerable(false);
            noPhysics = false;
            if (de != null) {
                // Sale de su cuerpo hacia un lado, a dos bloques: que se le vea salir.
                double giro = random.nextDouble() * Math.PI * 2.0;
                Vec3 fuera = de.position().add(Math.cos(giro) * 2.0, 0.3, Math.sin(giro) * 2.0);
                setPos(fuera.x, fuera.y, fuera.z);
                mirarA(de);
            }
            animar(EV_APARECE);
            sonar("sale", 1.1F);
            particulas(nivel, "alma", getX(), getY() + 1.0, getZ(), 18, 0.4, 0.5, 0.05);
            List<Player> otros = nivel.getEntitiesOfClass(Player.class, getBoundingBox().inflate(24.0),
                    p -> jugable(p) && p != de);
            Player otro = null;
            for (Player p : otros) {
                if (otro == null || p.distanceToSqr(this) < otro.distanceToSqr(this)) {
                    otro = p;
                }
            }
            setTarget(otro != null ? otro : de);
            descansar(SALIDO);
        }

        @Override
        public boolean isPickable() {
            return huesped == null && super.isPickable();
        }

        @Override
        public boolean isPushable() {
            return huesped == null && super.isPushable();
        }

        @Override
        protected void readAdditionalSaveData(ValueInput entrada) {
            super.readAdditionalSaveData(entrada);
            // Si se guardo dentro de alguien, vuelve fuera.
            setInvulnerable(false);
            setInvisible(false);
        }
    }

    // ------------------------------------------------------------------
    //  El Rojo
    // ------------------------------------------------------------------

    public static class Rojo extends Fantasma {

        private static final int AGARRA = 1;

        private @Nullable UUID agarrado;

        public Rojo(EntityType<? extends Monster> tipo, Level nivel) {
            super(tipo, nivel);
            cadencia = 20;
        }

        public static AttributeSupplier.Builder atributos() {
            return base(24.0, 0.65, 3.0);
        }

        @Override
        public Bestia bestia() {
            return Fichas.ESPECTRO_ROJO;
        }

        @Override
        protected boolean acosa() {
            return agarrado == null;
        }

        @Override
        protected void alDar(ServerLevel nivel, LivingEntity v) {
            if (agarrado == null && jugable(v)) {
                agarrado = v.getUUID();
                setEstado(AGARRA);
                getNavigation().stop();
                sonar("agarra", 1.1F);
                particulas(nivel, "ceniza", v.getX(), v.getY() + 1.0, v.getZ(), 10, 0.3, 0.4, 0.03);
            }
        }

        @Override
        public void tick() {
            super.tick();
            if (agarrado == null || !(level() instanceof ServerLevel nivel) || !isAlive()) {
                return;
            }
            Entity e = nivel.getEntity(agarrado);
            if (!jugable(e) || e.distanceToSqr(this) > 4.0 * 4.0) {
                agarrado = null;
                setEstado(0);
                return;
            }
            LivingEntity v = (LivingEntity) e;
            // Delante de el, cara a cara, y el clavado donde esta.
            Vec3 mira = v.getLookAngle().multiply(1.0, 0.0, 1.0);
            mira = mira.lengthSqr() < 1.0E-4 ? new Vec3(0.0, 0.0, 1.0) : mira.normalize();
            Vec3 aqui = v.position().add(mira.scale(getBbWidth() * 0.5 + v.getBbWidth() * 0.5 + 0.2));
            setPos(aqui.x, v.getY() + 0.1, aqui.z);
            setDeltaMovement(Vec3.ZERO);
            mirarA(v);
            MobEffectInstance quieto = v.getEffect(EnraizadoEffect.ENRAIZADO);
            if (quieto == null || quieto.getDuration() < 5) {
                v.addEffect(new MobEffectInstance(EnraizadoEffect.ENRAIZADO, 20, 0, false, false, true), this);
            }
            if (tickCount % cadencia == 0) {
                zarpazo(nivel, v);
            }
        }
    }
}
