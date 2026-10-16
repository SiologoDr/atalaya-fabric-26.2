package com.atalaya.entity;

import com.atalaya.Atalaya;
import com.atalaya.particula.AtalayaParticulas;
import com.atalaya.sonido.AtalayaSonidos;
import net.fabricmc.fabric.api.event.player.AttackBlockCallback;
import net.fabricmc.fabric.api.event.player.AttackEntityCallback;
import net.fabricmc.fabric.api.event.player.UseBlockCallback;
import net.fabricmc.fabric.api.event.player.UseEntityCallback;
import net.fabricmc.fabric.api.event.player.UseItemCallback;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.ResourceKey;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.damagesource.DamageType;
import net.minecraft.world.entity.AnimationState;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityDimensions;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.FloatGoal;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.entity.ai.goal.LookAtPlayerGoal;
import net.minecraft.world.entity.ai.goal.RandomLookAroundGoal;
import net.minecraft.world.entity.ai.goal.WaterAvoidingRandomStrollGoal;
import net.minecraft.world.entity.ai.goal.target.HurtByTargetGoal;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.Vec3;
import org.jspecify.annotations.Nullable;

import java.util.EnumSet;

/**
 * El Coco (16-10-2026), el mob que te mete en la barriga. Juan: «hagamos un mob que meta al jugador dentro de su panza,
 * como atrapado, y le quite vida lentamente; no tanto daño, pero si no hay una persona cerca esa cosa puede ser mortal;
 * la unica forma de salvar a un jugador es matando al mob». Es el Gloton de la ficha («haz el diseño 1»).
 *
 * Lo que hace:
 * - Te ve y viene a por ti, encorvado. A 2,5 bloques se para y da el segundo de aviso (alza las manos y abre la
 *   cascara). Si sigues a su alcance cuando acaba, te traga.
 * - Tragado, vas dentro de su barriga (montado en el, sin poder bajarte), no se te ve, y no puedes pegar, romper ni usar
 *   nada. Cada 2 segundos te quita medio corazon, sin que cuente la armadura, y dentro no te curas solo (CocoSinCurarMixin):
 *   con la vida llena son 40 segundos.
 * - Encima del Coco sale el aviso para los demas: el icono de alerta, tu nombre y «¡ha sido atrapado!» (CocoRenderer).
 * - Con alguien dentro no se mueve: se queda haciendo la digestion y a quien se le acerque le da un manotazo.
 * - Solo sales si alguien lo mata: la barriga revienta y caes fuera.
 *
 * Por ahora solo sale con su huevo, como todos (Juan, 16-10-2026).
 */
public class CocoEntity extends Monster {

    /** El segundo de aviso, antes de tragarte. */
    public static final int AVISO = 20;
    /** Lo que dura tragar (la animacion; el jugador ya va dentro). */
    public static final int TRAGA = 12;
    /** Cada cuanto quita vida al de dentro: medio corazon cada 2 segundos. */
    public static final int CADA = 40;
    public static final float MORDISCO = 1.0F;
    /** A cuanto empieza el aviso y a cuanto te traga al acabarlo (de centro a centro). */
    private static final double ALCANCE = 2.5;
    private static final double ALCANCE_FIN = 3.4;
    private static final double ALCANCE_MANOTAZO = 3.2;

    public static final byte LIBRE = 0;
    public static final byte AVISANDO = 1;
    public static final byte TRAGANDO = 2;
    public static final byte LLENO = 3;
    /** El evento de entidad del manotazo (el mismo numero que el golpe del golem de hierro). */
    private static final byte EVENTO_MANOTAZO = 4;

    public static final ResourceKey<DamageType> DIGERIDO = ResourceKey.create(Registries.DAMAGE_TYPE,
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "coco"));

    private static final EntityDataAccessor<Byte> DATA_ESTADO =
            SynchedEntityData.defineId(CocoEntity.class, EntityDataSerializers.BYTE);
    /** El nombre del que tiene dentro (vacio si no tiene a nadie): el aviso de encima lo pinta. */
    private static final EntityDataAccessor<String> DATA_ATRAPADO =
            SynchedEntityData.defineId(CocoEntity.class, EntityDataSerializers.STRING);

    // Las animaciones del cliente.
    public final AnimationState aviso = new AnimationState();
    public final AnimationState traga = new AnimationState();
    public final AnimationState manotazo = new AnimationState();

    private int ticksEstado;
    private int enfria;
    private int digiere;
    private int enfriaManotazo;
    private int avisoDentro;
    private boolean metiendo;

    public CocoEntity(EntityType<? extends CocoEntity> tipo, Level nivel) {
        super(tipo, nivel);
        xpReward = 10;
    }

    public static AttributeSupplier.Builder crearAtributos() {
        return Monster.createMonsterAttributes()
                .add(Attributes.MAX_HEALTH, 40.0D)
                .add(Attributes.MOVEMENT_SPEED, 0.25D)
                .add(Attributes.ATTACK_DAMAGE, 5.0D)
                .add(Attributes.ATTACK_KNOCKBACK, 1.0D)
                .add(Attributes.FOLLOW_RANGE, 24.0D)
                .add(Attributes.KNOCKBACK_RESISTANCE, 0.6D)
                .add(Attributes.ARMOR, 2.0D)
                .add(Attributes.STEP_HEIGHT, 1.0D);
    }

    @Override
    protected void defineSynchedData(SynchedEntityData.Builder datos) {
        super.defineSynchedData(datos);
        datos.define(DATA_ESTADO, LIBRE);
        datos.define(DATA_ATRAPADO, "");
    }

    @Override
    protected void registerGoals() {
        goalSelector.addGoal(0, new FloatGoal(this));
        goalSelector.addGoal(2, new CazarGoal());
        goalSelector.addGoal(6, new WaterAvoidingRandomStrollGoal(this, 0.8D) {
            @Override
            public boolean canUse() {
                return getEstado() == LIBRE && super.canUse();
            }
        });
        goalSelector.addGoal(7, new LookAtPlayerGoal(this, Player.class, 10.0F));
        goalSelector.addGoal(8, new RandomLookAroundGoal(this));
        targetSelector.addGoal(1, new HurtByTargetGoal(this));
        targetSelector.addGoal(2, new NearestAttackableTargetGoal<>(this, Player.class, true));
    }

    // ------------------------------------------------------------------
    //  Estado
    // ------------------------------------------------------------------

    public byte getEstado() {
        return entityData.get(DATA_ESTADO);
    }

    /** El nombre del atrapado, o "" si no tiene a nadie dentro. */
    public String getAtrapado() {
        return entityData.get(DATA_ATRAPADO);
    }

    private void ponerEstado(byte estado, int duracion) {
        entityData.set(DATA_ESTADO, estado);
        ticksEstado = duracion;
    }

    @Override
    public void onSyncedDataUpdated(EntityDataAccessor<?> dato) {
        super.onSyncedDataUpdated(dato);
        if (!DATA_ESTADO.equals(dato) || !level().isClientSide()) {
            return;
        }
        switch (getEstado()) {
            case AVISANDO -> aviso.start(tickCount);
            case TRAGANDO -> {
                aviso.stop();
                traga.start(tickCount);
            }
            case LIBRE -> {
                aviso.stop();
                traga.stop();
            }
            default -> aviso.stop();
        }
    }

    @Override
    public void handleEntityEvent(byte evento) {
        if (evento == EVENTO_MANOTAZO) {
            manotazo.start(tickCount);
        } else {
            super.handleEntityEvent(evento);
        }
    }

    /** El jugador que lleva dentro, si lleva a alguien. */
    public @Nullable Player dentro() {
        return getFirstPassenger() instanceof Player jugador ? jugador : null;
    }

    // ------------------------------------------------------------------
    //  La IA del servidor
    // ------------------------------------------------------------------

    @Override
    protected void customServerAiStep(ServerLevel nivel) {
        super.customServerAiStep(nivel);
        if (enfria > 0) {
            enfria--;
        }
        if (enfriaManotazo > 0) {
            enfriaManotazo--;
        }
        Player jugador = dentro();
        byte estado = getEstado();
        // Lo que lleva dentro manda: si ya no hay nadie (ha muerto, se ha ido), vuelve a cazar; si hay alguien y no lo
        // sabia (al cargar el mundo con el jugador dentro), lo sabe.
        if (jugador == null && (estado == TRAGANDO || estado == LLENO)) {
            entityData.set(DATA_ATRAPADO, "");
            ponerEstado(LIBRE, 0);
            enfria = 60;
            return;
        }
        if (jugador != null && estado != TRAGANDO && estado != LLENO) {
            entityData.set(DATA_ATRAPADO, jugador.getName().getString());
            ponerEstado(LLENO, 0);
            digiere = CADA;
            estado = LLENO;
        }
        LivingEntity presa = getTarget();
        switch (estado) {
            case LIBRE -> {
                if (enfria == 0 && sePuedeTragar(presa) && distanceToSqr(presa) <= ALCANCE * ALCANCE
                        && hasLineOfSight(presa)) {
                    ponerEstado(AVISANDO, AVISO);
                    getNavigation().stop();
                    playSound(AtalayaSonidos.COCO_AVISO, 1.6F, 1.0F);
                }
            }
            case AVISANDO -> {
                getNavigation().stop();
                if (presa != null) {
                    getLookControl().setLookAt(presa, 60.0F, 60.0F);
                }
                if (--ticksEstado <= 0) {
                    if (sePuedeTragar(presa) && distanceToSqr(presa) <= ALCANCE_FIN * ALCANCE_FIN && hasLineOfSight(presa)) {
                        tragar(nivel, (Player) presa);
                    } else {
                        ponerEstado(LIBRE, 0);
                        enfria = 30;
                    }
                }
            }
            case TRAGANDO -> {
                getNavigation().stop();
                if (--ticksEstado <= 0) {
                    ponerEstado(LLENO, 0);
                }
                digerir(nivel, jugador);
            }
            case LLENO -> {
                getNavigation().stop();
                digerir(nivel, jugador);
                defenderse(nivel, jugador);
            }
            default -> {
            }
        }
    }

    private boolean sePuedeTragar(@Nullable LivingEntity quien) {
        return quien instanceof Player jugador && jugador.isAlive() && !jugador.isCreative() && !jugador.isSpectator()
                && !(jugador.getVehicle() instanceof CocoEntity) && getPassengers().isEmpty();
    }

    /** Te traga: vas a su barriga (montado en el) y encima sale el aviso. */
    private void tragar(ServerLevel nivel, Player jugador) {
        metiendo = true;
        boolean dentro = jugador.startRiding(this, true, true);
        metiendo = false;
        if (!dentro) {
            ponerEstado(LIBRE, 0);
            enfria = 30;
            return;
        }
        entityData.set(DATA_ATRAPADO, jugador.getName().getString());
        ponerEstado(TRAGANDO, TRAGA);
        digiere = CADA;
        avisoDentro = 3;
        setTarget(null);
        playSound(AtalayaSonidos.COCO_TRAGA, 1.8F, 1.0F);
    }

    /** Cada 2 segundos, medio corazon al de dentro (la armadura no cuenta) y las tripas que suenan. */
    private void digerir(ServerLevel nivel, @Nullable Player jugador) {
        if (jugador == null) {
            return;
        }
        if (avisoDentro > 0 && --avisoDentro == 0) {
            // El mensaje va un par de ticks despues de montarlo, para tapar el «pulsa mayusculas para bajar» de vanilla.
            jugador.sendOverlayMessage(Component.translatable("entity.atalaya.coco.dentro"));
        }
        if (--digiere > 0) {
            return;
        }
        digiere = CADA;
        playSound(AtalayaSonidos.COCO_DIGIERE, 1.2F, 0.9F + random.nextFloat() * 0.2F);
        jugador.hurtServer(nivel, fuenteDigerido(), MORDISCO);
    }

    private DamageSource fuenteDigerido() {
        return new DamageSource(level().registryAccess().lookupOrThrow(Registries.DAMAGE_TYPE).getOrThrow(DIGERIDO),
                this, this);
    }

    /** Lleno no se mueve, pero a quien se acerca (para salvar al de dentro) le da un manotazo. */
    private void defenderse(ServerLevel nivel, Player jugadorDentro) {
        if (enfriaManotazo > 0) {
            return;
        }
        Player cerca = nivel.getNearestPlayer(getX(), getY(), getZ(), ALCANCE_MANOTAZO,
                p -> p != jugadorDentro && p instanceof Player j && !j.isCreative() && !j.isSpectator());
        if (cerca == null) {
            return;
        }
        getLookControl().setLookAt(cerca, 60.0F, 60.0F);
        nivel.broadcastEntityEvent(this, EVENTO_MANOTAZO);
        playSound(AtalayaSonidos.COCO_MANOTAZO, 1.3F, 1.0F);
        doHurtTarget(nivel, cerca);
        enfriaManotazo = 30;
    }

    // ------------------------------------------------------------------
    //  El de dentro
    // ------------------------------------------------------------------

    @Override
    protected boolean canAddPassenger(Entity pasajero) {
        return metiendo && pasajero instanceof Player && getPassengers().isEmpty();
    }

    /** El de dentro va en la barriga (no se le ve: CocoRenderer lo esconde). */
    @Override
    protected Vec3 getPassengerAttachmentPoint(Entity pasajero, EntityDimensions medidas, float escala) {
        return new Vec3(0.0, 0.3 * escala, 0.15 * escala);
    }

    @Override
    public boolean dismountsUnderwater() {
        return false;
    }

    @Override
    public boolean hurtServer(ServerLevel nivel, DamageSource fuente, float cantidad) {
        // Desde dentro no se le puede pegar (por si algo se cuela: los golpes ya se cortan en registrarEventos).
        Entity quien = fuente.getEntity();
        if (quien != null && quien == getFirstPassenger()) {
            return false;
        }
        return super.hurtServer(nivel, fuente, cantidad);
    }

    /** Al morir con alguien dentro, la barriga revienta y sale. */
    @Override
    public void die(DamageSource fuente) {
        Player jugador = dentro();
        super.die(fuente);
        if (jugador != null && level() instanceof ServerLevel nivel) {
            jugador.stopRiding();
            Vec3 delante = Vec3.directionFromRotation(0.0F, getYRot()).scale(0.9);
            jugador.teleportTo(getX() + delante.x, getY() + 0.2, getZ() + delante.z);
            jugador.setDeltaMovement(delante.x * 0.4, 0.45, delante.z * 0.4);
            jugador.hurtMarked = true;
            entityData.set(DATA_ATRAPADO, "");
            playSound(AtalayaSonidos.COCO_REVIENTA, 2.0F, 1.0F);
            nivel.sendParticles(AtalayaParticulas.RAJANG_POLVO, getX(), getY() + 1.0, getZ(), 24, 0.6, 0.6, 0.6, 0.05);
        }
    }

    // ------------------------------------------------------------------
    //  Lo que no puede hacer el de dentro
    // ------------------------------------------------------------------

    /** Si el jugador va dentro de un Coco. */
    public static boolean atrapado(@Nullable Entity quien) {
        return quien instanceof Player && quien.getVehicle() instanceof CocoEntity;
    }

    /**
     * Dentro no se puede pegar (ni al Coco ni a nadie), romper, poner ni usar nada: ni comer, ni una perla de ender, ni
     * un tótem a mano. Solo sales si alguien lo mata.
     */
    public static void registrarEventos() {
        AttackEntityCallback.EVENT.register((jugador, nivel, mano, entidad, golpe) ->
                atrapado(jugador) ? InteractionResult.FAIL : InteractionResult.PASS);
        AttackBlockCallback.EVENT.register((jugador, nivel, mano, pos, cara) ->
                atrapado(jugador) ? InteractionResult.FAIL : InteractionResult.PASS);
        UseBlockCallback.EVENT.register((jugador, nivel, mano, golpe) ->
                atrapado(jugador) ? InteractionResult.FAIL : InteractionResult.PASS);
        UseEntityCallback.EVENT.register((jugador, nivel, mano, entidad, golpe) ->
                atrapado(jugador) ? InteractionResult.FAIL : InteractionResult.PASS);
        UseItemCallback.EVENT.register((jugador, nivel, mano) ->
                atrapado(jugador) ? InteractionResult.FAIL : InteractionResult.PASS);
    }

    // ------------------------------------------------------------------
    //  Sonidos
    // ------------------------------------------------------------------

    @Override
    protected SoundEvent getAmbientSound() {
        return AtalayaSonidos.COCO_AMBIENTE;
    }

    @Override
    public int getAmbientSoundInterval() {
        return 140;
    }

    @Override
    protected SoundEvent getHurtSound(DamageSource fuente) {
        return AtalayaSonidos.COCO_HERIDO;
    }

    @Override
    protected SoundEvent getDeathSound() {
        return AtalayaSonidos.COCO_MUERTE;
    }

    @Override
    protected void playStepSound(BlockPos pos, BlockState bloque) {
        playSound(AtalayaSonidos.COCO_PASO, 0.7F, 0.9F + random.nextFloat() * 0.2F);
    }

    // ------------------------------------------------------------------
    //  Cazar: ir hacia la presa mientras esta libre
    // ------------------------------------------------------------------

    /** Va hacia su presa, encorvado; el aviso y el trago los lleva customServerAiStep. */
    private class CazarGoal extends Goal {
        private int repensar;

        CazarGoal() {
            setFlags(EnumSet.of(Flag.MOVE, Flag.LOOK));
        }

        @Override
        public boolean canUse() {
            LivingEntity presa = getTarget();
            return getEstado() == LIBRE && presa != null && presa.isAlive() && sePuedeTragar(presa);
        }

        @Override
        public boolean canContinueToUse() {
            return canUse();
        }

        @Override
        public void start() {
            repensar = 0;
        }

        @Override
        public void stop() {
            getNavigation().stop();
        }

        @Override
        public boolean requiresUpdateEveryTick() {
            return true;
        }

        @Override
        public void tick() {
            LivingEntity presa = getTarget();
            if (presa == null) {
                return;
            }
            getLookControl().setLookAt(presa, 30.0F, 30.0F);
            if (--repensar <= 0) {
                repensar = 8;
                getNavigation().moveTo(presa, 1.0D);
            }
        }
    }
}
