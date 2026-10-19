package com.atalaya.bestiario.mobs;

import com.atalaya.bestiario.Bestia;
import com.atalaya.bestiario.BestiaEntity;
import com.atalaya.bestiario.Fichas;
import com.atalaya.cambios.Insomnio;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerTickEvents;
import net.minecraft.core.BlockPos;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.Mth;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.control.MoveControl;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.entity.ai.goal.target.HurtByTargetGoal;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.Vec3;

import java.util.ArrayList;
import java.util.EnumSet;
import java.util.Iterator;
import java.util.List;

/**
 * Los phantoms del bestiario (DEDsafio 4, el cartel del 07-10: el Phantom Oscuro y el Phantom Explosivo): las
 * pesadillas, que bajan del cielo a los que no duermen (Insomnio) y salen con su huevo. Vuelan como el phantom de
 * Minecraft, al doble: dan vueltas muy por encima de su presa y, cada 4-5 segundos, se lanzan en picado.
 *
 * <pre>
 *   Oscuro     su golpe te hace soltar un hueco entero del inventario, al azar (la mano de al lado incluida)
 *   Explosivo  su golpe te deja una brasa encendida donde estas, que revienta al segundo y medio
 * </pre>
 */
public final class Phantoms {

    /** Las brasas que ha dejado el Explosivo, hasta que revientan. */
    private static final List<Brasa> BRASAS = new ArrayList<>();

    private record Brasa(ServerLevel nivel, Vec3 donde, int[] faltan) {
    }

    private Phantoms() {
    }

    /** Las pesadillas del Insomnio son ellos (en vez del phantom de siempre); y las brasas, cada tick. */
    public static void registrarEventos() {
        Insomnio.PESADILLAS.add(() -> tipo(Fichas.PHANTOM_OSCURO));
        Insomnio.PESADILLAS.add(() -> tipo(Fichas.PHANTOM_EXPLOSIVO));
        ServerTickEvents.END_SERVER_TICK.register(Phantoms::brasas);
    }

    @SuppressWarnings("unchecked")
    private static EntityType<? extends Mob> tipo(Bestia b) {
        return (EntityType<? extends Mob>) b.tipo;
    }

    private static AttributeSupplier.Builder base(double vida, double vuelo, double dano) {
        return Monster.createMonsterAttributes()
                .add(Attributes.MAX_HEALTH, vida)
                .add(Attributes.FLYING_SPEED, vuelo)
                .add(Attributes.MOVEMENT_SPEED, vuelo * 0.6)
                .add(Attributes.ATTACK_DAMAGE, dano)
                .add(Attributes.FOLLOW_RANGE, 64.0);
    }

    /** Las brasas: chisporrotean donde se quedaron y, al acabarse la mecha, revientan. */
    private static void brasas(MinecraftServer s) {
        if (BRASAS.isEmpty()) {
            return;
        }
        Bestia b = Fichas.PHANTOM_EXPLOSIVO;
        for (Iterator<Brasa> it = BRASAS.iterator(); it.hasNext(); ) {
            Brasa br = it.next();
            Vec3 d = br.donde();
            if (--br.faltan()[0] <= 0) {
                it.remove();
                BestiaEntity.estallido(br.nivel(), null, b, d.x, d.y + 0.3, d.z, 3.0F, false, "humo", "estalla");
                continue;
            }
            if (br.faltan()[0] % 3 == 0) {
                BestiaEntity.particulas(br.nivel(), b.particula("chispa"), d.x, d.y + 0.3, d.z, 3, 0.15, 0.1, 0.04);
            }
        }
    }

    // ------------------------------------------------------------------
    //  La base
    // ------------------------------------------------------------------

    /**
     * Lo de los dos: vuelan como el phantom de Minecraft (Juan, 19-10-2026: «que sea como un phantom normal, pero al
     * doble todo al estar en el cielo; en picada que sea el doble de rápido, y para lanzarse igual el doble de rápido»).
     * Es su misma forma de volar, copiada del phantom (Phantom, PhantomMoveControl y sus metas), con la velocidad, la
     * aceleración y el giro al doble y la mitad de espera entre picado y picado:
     *
     * <pre>
     *   en el cielo  dan vueltas alrededor de un punto de 20 a 40 bloques por encima de su presa, a 5-15 bloques de el,
     *                cambiando de altura y de sentido de vez en cuando (sin presa, alrededor de donde estan)
     *   picado       cada 4-5 segundos (el phantom, cada 8-11) se lanzan a por el centro de su presa; al tocarla le dan
     *                y vuelven a las vueltas (tambien si chocan o les pegan)
     * </pre>
     */
    public abstract static class Phantom extends BestiaEntity {

        /** Al doble que el phantom de Minecraft. */
        private static final float DOBLE = 2.0F;

        private boolean picando;
        private Vec3 meta = Vec3.ZERO;
        private BlockPos ancla = BlockPos.ZERO;

        protected Phantom(EntityType<? extends Monster> tipo, Level nivel) {
            super(tipo, nivel);
            this.moveControl = new Vuelo();
            setNoGravity(true);
        }

        @Override
        protected void registerGoals() {
            goalSelector.addGoal(1, new Estrategia());
            goalSelector.addGoal(2, new Picado());
            goalSelector.addGoal(3, new Vueltas());
            targetSelector.addGoal(1, new HurtByTargetGoal(this));
            targetSelector.addGoal(2, new NearestAttackableTargetGoal<>(this, Player.class, false));
        }

        /** Lo de cada uno cuando su golpe da. */
        protected abstract void alDar(ServerLevel nivel, LivingEntity v);

        /** Vuela con su inercia (lo de siempre en el aire; quien lo mueve es su Vuelo). */
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

        /** El punto de las vueltas: de 20 a 40 bloques por encima de su presa (nunca por debajo del mar). */
        private void anclarSobre(LivingEntity t) {
            ancla = t.blockPosition().above(20 + random.nextInt(20));
            if (ancla.getY() < level().getSeaLevel()) {
                ancla = new BlockPos(ancla.getX(), level().getSeaLevel() + 1, ancla.getZ());
            }
        }

        /**
         * Como mueve el phantom: gira hacia su meta (el doble de rapido: 8 grados por tick), acelera mientras va recto
         * (hasta 3,6, el doble de 1,8) y frena al girar (hasta 0,4); y su velocidad se acerca poco a poco a la que toca.
         */
        private final class Vuelo extends MoveControl {
            private float rapidez = 0.1F * DOBLE;

            Vuelo() {
                super(Phantom.this);
            }

            @Override
            public void tick() {
                if (horizontalCollision) {
                    setYRot(getYRot() + 180.0F);
                    rapidez = 0.1F * DOBLE;
                }
                double dx = meta.x - getX();
                double dy = meta.y - getY();
                double dz = meta.z - getZ();
                double h = Math.sqrt(dx * dx + dz * dz);
                if (Math.abs(h) <= 1.0E-5F) {
                    return;
                }
                double f = 1.0 - Math.abs(dy * 0.7F) / h;
                dx *= f;
                dz *= f;
                h = Math.sqrt(dx * dx + dz * dz);
                double d = Math.sqrt(dx * dx + dz * dz + dy * dy);
                float antes = getYRot();
                float hacia = Mth.wrapDegrees((float) Mth.atan2(dz, dx) * Mth.RAD_TO_DEG);
                setYRot(Mth.approachDegrees(Mth.wrapDegrees(getYRot() + 90.0F), hacia, 4.0F * DOBLE) - 90.0F);
                yBodyRot = getYRot();
                yHeadRot = getYRot();
                if (Mth.degreesDifferenceAbs(antes, getYRot()) < 3.0F * DOBLE) {
                    rapidez = Mth.approach(rapidez, 1.8F * DOBLE, 0.005F * DOBLE * (1.8F * DOBLE / rapidez));
                } else {
                    rapidez = Mth.approach(rapidez, 0.2F * DOBLE, 0.025F * DOBLE);
                }
                float cabeceo = (float) -(Mth.atan2(-dy, h) * Mth.RAD_TO_DEG);
                setXRot(cabeceo);
                float giro = getYRot() + 90.0F;
                double vx = rapidez * Mth.cos(giro * Mth.DEG_TO_RAD) * Math.abs(dx / d);
                double vz = rapidez * Mth.sin(giro * Mth.DEG_TO_RAD) * Math.abs(dz / d);
                double vy = rapidez * Mth.sin(cabeceo * Mth.DEG_TO_RAD) * Math.abs(dy / d);
                Vec3 v = getDeltaMovement();
                setDeltaMovement(v.add(new Vec3(vx, vy, vz).subtract(v).scale(0.2)));
            }
        }

        /** Cuando toca lanzarse en picado (y el punto de las vueltas, encima de su presa). */
        private final class Estrategia extends Goal {
            private int siguiente;

            @Override
            public boolean canUse() {
                LivingEntity t = getTarget();
                return t != null && canAttack(t);
            }

            @Override
            public void start() {
                siguiente = adjustedTickDelay(5);
                picando = false;
                anclarSobre(getTarget());
            }

            @Override
            public void stop() {
                ancla = level().getHeightmapPos(net.minecraft.world.level.levelgen.Heightmap.Types.MOTION_BLOCKING, ancla)
                        .above(10 + random.nextInt(20));
            }

            @Override
            public void tick() {
                if (!picando && --siguiente <= 0) {
                    picando = true;
                    anclarSobre(getTarget());
                    siguiente = adjustedTickDelay((4 + random.nextInt(2)) * 20);
                    sonar("picado", 1.0F);
                    animar(EV_ATAQUE);
                }
            }
        }

        /** El picado: a por el centro de su presa; al tocarla le da y vuelve a las vueltas (o si choca o le pegan). */
        private final class Picado extends Goal {
            Picado() {
                setFlags(EnumSet.of(Flag.MOVE));
            }

            @Override
            public boolean canUse() {
                return getTarget() != null && picando;
            }

            @Override
            public boolean canContinueToUse() {
                LivingEntity t = getTarget();
                return t != null && t.isAlive() && !t.isSpectator() && !(t instanceof Player p && p.isCreative())
                        && canUse();
            }

            @Override
            public void stop() {
                picando = false;
            }

            @Override
            public void tick() {
                LivingEntity t = getTarget();
                if (t == null || !(level() instanceof ServerLevel nivel)) {
                    return;
                }
                meta = new Vec3(t.getX(), t.getY(0.5), t.getZ());
                if (getBoundingBox().inflate(0.2).intersects(t.getBoundingBox())) {
                    if (doHurtTarget(nivel, t)) {
                        alDar(nivel, t);
                    }
                    picando = false;
                } else if (horizontalCollision || hurtTime > 0) {
                    picando = false;
                }
            }
        }

        /** Las vueltas alrededor del punto (como el phantom): un tramo de 15 grados cada vez que llega a su meta. */
        private final class Vueltas extends Goal {
            private float angulo;
            private float distancia;
            private float altura;
            private float sentido;

            Vueltas() {
                setFlags(EnumSet.of(Flag.MOVE));
            }

            @Override
            public boolean canUse() {
                return getTarget() == null || !picando;
            }

            @Override
            public void start() {
                distancia = 5.0F + random.nextFloat() * 10.0F;
                altura = -4.0F + random.nextFloat() * 9.0F;
                sentido = random.nextBoolean() ? 1.0F : -1.0F;
                siguiente();
            }

            @Override
            public void tick() {
                if (random.nextInt(adjustedTickDelay(350)) == 0) {
                    altura = -4.0F + random.nextFloat() * 9.0F;
                }
                if (random.nextInt(adjustedTickDelay(250)) == 0) {
                    distancia++;
                    if (distancia > 15.0F) {
                        distancia = 5.0F;
                        sentido = -sentido;
                    }
                }
                if (random.nextInt(adjustedTickDelay(450)) == 0) {
                    angulo = random.nextFloat() * 2.0F * Mth.PI;
                    siguiente();
                }
                if (meta.distanceToSqr(getX(), getY(), getZ()) < 4.0) {
                    siguiente();
                }
                if (meta.y < getY() && !level().isEmptyBlock(blockPosition().below(1))) {
                    altura = Math.max(1.0F, altura);
                    siguiente();
                }
                if (meta.y > getY() && !level().isEmptyBlock(blockPosition().above(1))) {
                    altura = Math.min(-1.0F, altura);
                    siguiente();
                }
            }

            private void siguiente() {
                if (BlockPos.ZERO.equals(ancla)) {
                    ancla = blockPosition();
                }
                angulo += sentido * 15.0F * Mth.DEG_TO_RAD;
                meta = Vec3.atLowerCornerOf(ancla).add(distancia * Mth.cos(angulo), -4.0F + altura,
                        distancia * Mth.sin(angulo));
            }
        }
    }

    // ------------------------------------------------------------------
    //  El Oscuro
    // ------------------------------------------------------------------

    public static class Oscuro extends Phantom {

        public Oscuro(EntityType<? extends Monster> tipo, Level nivel) {
            super(tipo, nivel);
        }

        public static AttributeSupplier.Builder atributos() {
            return base(20.0, 0.45, 2.0);
        }

        @Override
        public Bestia bestia() {
            return Fichas.PHANTOM_OSCURO;
        }

        /** Te arranca un hueco entero del inventario, al azar (la otra mano incluida), y cae al suelo. */
        @Override
        protected void alDar(ServerLevel nivel, LivingEntity v) {
            if (!(v instanceof ServerPlayer p) || p.isCreative()) {
                return;
            }
            Inventory inv = p.getInventory();
            List<Integer> llenos = new ArrayList<>();
            for (int i = 0; i < 36; i++) {
                if (!inv.getItem(i).isEmpty()) {
                    llenos.add(i);
                }
            }
            if (!inv.getItem(Inventory.SLOT_OFFHAND).isEmpty()) {
                llenos.add(Inventory.SLOT_OFFHAND);
            }
            if (llenos.isEmpty()) {
                return;
            }
            int hueco = llenos.get(random.nextInt(llenos.size()));
            ItemStack fuera = inv.removeItemNoUpdate(hueco);
            inv.setChanged();
            p.drop(fuera, true, false);
            sonar("arranca", 1.0F);
            particulas(nivel, "humo", p.getX(), p.getY() + 1.0, p.getZ(), 8, 0.3, 0.4, 0.03);
            particulas(nivel, "hueso", p.getX(), p.getY() + 1.0, p.getZ(), 6, 0.3, 0.3, 0.08);
        }
    }

    // ------------------------------------------------------------------
    //  El Explosivo
    // ------------------------------------------------------------------

    public static class Explosivo extends Phantom {

        /** Lo que tarda en reventar la brasa que deja (ticks). */
        private static final int MECHA = 30;

        public Explosivo(EntityType<? extends Monster> tipo, Level nivel) {
            super(tipo, nivel);
        }

        public static AttributeSupplier.Builder atributos() {
            return base(20.0, 0.45, 2.0);
        }

        @Override
        public Bestia bestia() {
            return Fichas.PHANTOM_EXPLOSIVO;
        }

        /** Te deja una brasa encendida donde estas, que revienta al segundo y medio. */
        @Override
        protected void alDar(ServerLevel nivel, LivingEntity v) {
            Vec3 donde = v.position();
            BRASAS.add(new Brasa(nivel, donde, new int[]{MECHA}));
            SoundEvent mecha = bestia().sonido("mecha");
            if (mecha != null) {
                nivel.playSound(null, donde.x, donde.y, donde.z, mecha, SoundSource.HOSTILE, 1.2F, 1.0F);
            }
            particulas(nivel, "chispa", donde.x, donde.y + 0.3, donde.z, 12, 0.2, 0.1, 0.08);
        }

        @Override
        public void aiStep() {
            super.aiStep();
            if (level() instanceof ServerLevel nivel && tickCount % 4 == 0) {
                particulas(nivel, "chispa", getX(), getY() + 0.2, getZ(), 1, 0.3, 0.05, 0.01);
            }
        }
    }
}
