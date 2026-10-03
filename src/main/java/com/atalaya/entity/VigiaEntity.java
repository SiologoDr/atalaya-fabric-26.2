package com.atalaya.entity;

import com.atalaya.particula.AtalayaParticulas;
import com.atalaya.sonido.AtalayaSonidos;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.util.Mth;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.AnimationState;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.FloatGoal;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.entity.ai.goal.MeleeAttackGoal;
import net.minecraft.world.entity.ai.goal.WaterAvoidingRandomStrollGoal;
import net.minecraft.world.entity.ai.goal.target.HurtByTargetGoal;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;

import java.util.EnumSet;

/**
 * El Vigia: el centinela de la atalaya.
 *
 * Alto, encorvado, con una linterna por cabeza y un solo ojo dentro. Lo que
 * mira, lo maldice. Es el primer bicho del mod con malla y animaciones propias,
 * y esta pensado como amenaza de fase: lento, duro, y con un ataque a distancia
 * que AVISA antes de caer, porque en hardcore un golpe que no se ve venir no es
 * dificultad, es loteria.
 *
 * Los estados viven en un solo numero sincronizado, y el cliente arranca
 * la animacion que toca al ver el cambio. Asi no hace falta inventar eventos de
 * entidad con bytes que vanilla quiza ya use, y quien entra tarde a la zona ve
 * el bicho en el estado correcto.
 *
 * <pre>
 *   LIBRE     anda, persigue, mira alrededor
 *   ALERTA    acaba de verte: se yergue y ruge. Quieto 1,2 s — el aviso.
 *   CEPO      abre los brazos en cruz y los cierra delante como una trampa.
 *   MIRADA    se clava, el ojo carga 2 s y, si aun te ve, te marca.
 *   TAMBALEO  le han dado por la espalda: pierde el turno 1,2 s.
 *   BUSCAR    te ha perdido de vista: escudrina a los lados antes de rendirse.
 * </pre>
 *
 * Y la muerte, que no es un estado sino tres segundos propios: cae de
 * rodillas, echa una ultima mirada, el farol se apaga y se le desprende.
 * Vanilla retira el cuerpo a los 20 ticks; aqui se retiene hasta que acaba.
 */
public class VigiaEntity extends Monster {

    public static final int LIBRE = 0;
    public static final int ALERTA = 1;
    public static final int CEPO = 2;
    public static final int MIRADA = 3;
    public static final int TAMBALEO = 4;
    public static final int BUSCAR = 5;

    // Duraciones en ticks. Tienen que cuadrar con las animaciones del cliente
    // (VigiaAnimaciones): si el estado acaba antes que la animacion, esta se
    // corta a medias; si acaba despues, el bicho se queda posando.
    public static final int DURACION_ALERTA = 24;
    public static final int DURACION_CEPO = 22;
    public static final int DURACION_MIRADA = 40;
    public static final int DURACION_TAMBALEO = 24;
    public static final int DURACION_BUSCAR = 50;

    /** La muerte entera, en ticks: lo que dura la animacion de la ultima guardia. */
    public static final int DURACION_MUERTE = 60;

    /** Tick de la muerte en que se apaga el ojo. */
    public static final int MUERTE_APAGARSE = 44;

    /** Tick de la muerte en que el farol toca el suelo. */
    public static final int MUERTE_FAROL_CAE = 52;

    /**
     * Persiguiendo va un 35 % mas rapido que patrullando. Con 0,24 de base
     * queda en lo que anda un jugador: andando no lo sueltas, corriendo si.
     */
    private static final double VELOCIDAD_PERSECUCION = 1.35D;

    /** Patrullando, sin prisa: es un centinela haciendo su ronda. */
    private static final double VELOCIDAD_PATRULLA = 0.6D;

    /**
     * Tick del cepo en que se cierran los brazos, contado desde que empieza.
     *
     * El dano NO entra al pulsar el ataque sino aqui, tras medio segundo de
     * anticipacion. Es lo que hace que la animacion signifique algo: verle
     * abrir los brazos en cruz es la ventana para echarse atras.
     */
    private static final int IMPACTO_CEPO = 11;

    /** Lo que tarda en poder repetir el cepo tras acabar uno. */
    private static final int ENFRIAMIENTO_CEPO = 12;

    /** Lo que te deja clavado si te pilla: un segundo de Lentitud IV. */
    private static final int ATRAPADO = 20;

    /** Entre una mirada y la siguiente. */
    private static final int ENFRIAMIENTO_MIRADA = 240;

    /** Si la mirada se corta porque te escondes, vuelve antes: no es castigo para el. */
    private static final int ENFRIAMIENTO_MIRADA_FALLIDA = 120;

    /** Ticks seguidos sin verte que tolera la mirada antes de apagarse. */
    private static final int MARGEN_SIN_VER = 6;

    private static final double MIRADA_MIN = 5.0;
    private static final double MIRADA_MAX = 24.0;

    /** Multiplicador del dano que entra por la espalda. */
    private static final float DANO_ESPALDA = 1.5F;

    /** Para no encadenar tambaleos: uno cada 5 s como mucho. */
    private static final int ENFRIAMIENTO_TAMBALEO = 100;

    private static final EntityDataAccessor<Integer> DATA_ESTADO =
            SynchedEntityData.defineId(VigiaEntity.class, EntityDataSerializers.INT);

    /** Si tiene presa. En el cliente decide el color del ojo. */
    private static final EntityDataAccessor<Boolean> DATA_CAZANDO =
            SynchedEntityData.defineId(VigiaEntity.class, EntityDataSerializers.BOOLEAN);

    // --- Solo cliente: lo que lee el renderer ---
    public final AnimationState reposo = new AnimationState();
    public final AnimationState alerta = new AnimationState();
    public final AnimationState cepo = new AnimationState();
    public final AnimationState mirada = new AnimationState();
    public final AnimationState tambaleo = new AnimationState();
    public final AnimationState buscar = new AnimationState();
    public final AnimationState muerte = new AnimationState();

    // --- Solo servidor ---
    private int ticksEstado;
    private int enfriamientoCepo;
    private int enfriamientoMirada = 100;
    private int enfriamientoTambaleo;
    private int ticksSinVer;
    private boolean teniaPresa;

    public VigiaEntity(EntityType<? extends Monster> tipo, Level nivel) {
        super(tipo, nivel);
        this.xpReward = 20;
    }

    public static AttributeSupplier.Builder crearAtributos() {
        return Monster.createMonsterAttributes()
                // 30 corazones: con espada de diamante son unos 9 golpes.
                .add(Attributes.MAX_HEALTH, 60.0D)
                .add(Attributes.ARMOR, 8.0D)
                .add(Attributes.ATTACK_DAMAGE, 9.0D)
                .add(Attributes.ATTACK_KNOCKBACK, 1.2D)
                // Lento: un jugador andando le saca distancia. La amenaza es
                // la mirada, no la persecucion.
                .add(Attributes.MOVEMENT_SPEED, 0.24D)
                .add(Attributes.FOLLOW_RANGE, 40.0D)
                .add(Attributes.KNOCKBACK_RESISTANCE, 0.6D)
                .add(Attributes.STEP_HEIGHT, 1.0D);
    }

    @Override
    protected void defineSynchedData(SynchedEntityData.Builder datos) {
        super.defineSynchedData(datos);
        datos.define(DATA_ESTADO, LIBRE);
        datos.define(DATA_CAZANDO, false);
    }

    @Override
    protected void registerGoals() {
        goalSelector.addGoal(0, new FloatGoal(this));
        // Quieto va por encima de todo lo que mueve: mientras ruge, mira o se
        // tambalea, el resto de la IA queda en suspenso sin tocar sus goals.
        goalSelector.addGoal(1, new QuietoGoal());
        goalSelector.addGoal(2, new AtaqueGoal());
        goalSelector.addGoal(5, new WaterAvoidingRandomStrollGoal(this, VELOCIDAD_PATRULLA));
        // Sin LookAtPlayer ni RandomLookAround a proposito: en calma, a donde
        // mira lo decide la animacion de vigilar, que barre el horizonte como
        // un faro. Esos goals le harian quedarse mirando a cualquiera que pase
        // aunque no lo haya detectado, y eso es justo lo que no es.

        targetSelector.addGoal(1, new HurtByTargetGoal(this));
        targetSelector.addGoal(2, new NearestAttackableTargetGoal<>(this, Player.class, true));
    }

    // ------------------------------------------------------------------
    //  Estado
    // ------------------------------------------------------------------

    public int getEstado() {
        return entityData.get(DATA_ESTADO);
    }

    public boolean isCazando() {
        return entityData.get(DATA_CAZANDO);
    }

    private void ponerEstado(int estado, int duracion) {
        entityData.set(DATA_ESTADO, estado);
        ticksEstado = duracion;
    }

    @Override
    public void onSyncedDataUpdated(EntityDataAccessor<?> dato) {
        super.onSyncedDataUpdated(dato);
        if (!DATA_ESTADO.equals(dato) || !level().isClientSide()) {
            return;
        }
        // Una animacion de accion a la vez. Arrancar la nueva sin parar la
        // anterior las mezclaria: los dos brazos arriba y a la vez abiertos.
        alerta.stop();
        cepo.stop();
        mirada.stop();
        tambaleo.stop();
        buscar.stop();
        switch (getEstado()) {
            case ALERTA -> alerta.start(tickCount);
            case CEPO -> cepo.start(tickCount);
            case MIRADA -> mirada.start(tickCount);
            case TAMBALEO -> tambaleo.start(tickCount);
            case BUSCAR -> buscar.start(tickCount);
            default -> {
            }
        }
    }

    @Override
    public void tick() {
        super.tick();
        if (level().isClientSide()) {
            // El reposo (respirar, la capa meciendose) solo cuando no hace
            // otra cosa. Andar lo pone el modelo con la velocidad de paso.
            boolean muriendo = isDeadOrDying();
            // El reposo solo parado: andando ya tiene su propio vaiven, y el
            // barrido de vigilar encima de la zancada la ensuciaria.
            reposo.animateWhen(getEstado() == LIBRE && !muriendo && !walkAnimation.isMoving(), tickCount);
            if (muriendo && !muerte.isStarted()) {
                // La muerte tapa todo lo demas: si moria a mitad de un cepo,
                // los brazos no deben quedarse cerrando en el aire.
                alerta.stop();
                cepo.stop();
                mirada.stop();
                tambaleo.stop();
                buscar.stop();
                muerte.start(tickCount);
            }
            if (getEstado() == MIRADA) {
                chispasDelOjo();
            }
        }
    }

    /** Particulas que el cliente pinta solo: el ojo cargando. No gastan red. */
    private void chispasDelOjo() {
        Vec3 ojo = posicionOjo();
        for (int i = 0; i < 2; i++) {
            double dx = (random.nextDouble() - 0.5) * 1.6;
            double dy = (random.nextDouble() - 0.5) * 1.6;
            double dz = (random.nextDouble() - 0.5) * 1.6;
            // Nacen alrededor y van hacia el ojo: se lee como que absorbe luz.
            level().addParticle(AtalayaParticulas.VIGIA_CHISPA,
                    ojo.x + dx, ojo.y + dy, ojo.z + dz, -dx * 0.15, -dy * 0.15, -dz * 0.15);
        }
    }

    // ------------------------------------------------------------------
    //  IA del servidor
    // ------------------------------------------------------------------

    @Override
    protected void customServerAiStep(ServerLevel nivel) {
        super.customServerAiStep(nivel);

        LivingEntity presa = getTarget();
        boolean tienePresa = presa != null && presa.isAlive();
        if (tienePresa != isCazando()) {
            entityData.set(DATA_CAZANDO, tienePresa);
        }

        if (enfriamientoCepo > 0) enfriamientoCepo--;
        if (enfriamientoMirada > 0) enfriamientoMirada--;
        if (enfriamientoTambaleo > 0) enfriamientoTambaleo--;

        // Te acaba de ver: ruge antes de hacer nada. Es el aviso de que la
        // cosa va contigo, y da un segundo para decidir si correr o pelear.
        if (tienePresa && !teniaPresa && (getEstado() == LIBRE || getEstado() == BUSCAR)) {
            ponerEstado(ALERTA, DURACION_ALERTA);
            playSound(AtalayaSonidos.VIGIA_ALERTA, 2.5F, 1.0F);
        }
        // Y al reves: se le ha escapado. No vuelve a patrullar sin mas: se
        // para a buscar. Es lo que hace que esconderse tenga tension, porque
        // durante dos segundos y medio el farol barre justo por donde estas.
        if (!tienePresa && teniaPresa && getEstado() == LIBRE) {
            ponerEstado(BUSCAR, DURACION_BUSCAR);
            playSound(AtalayaSonidos.VIGIA_BUSCAR, 1.5F, 1.0F);
        }
        teniaPresa = tienePresa;

        switch (getEstado()) {
            case CEPO -> tickCepo(nivel, presa);
            case MIRADA -> tickMirada(nivel, presa);
            case LIBRE -> intentarMirada(presa);
            default -> {
            }
        }

        if (getEstado() != LIBRE && --ticksEstado <= 0) {
            if (getEstado() == CEPO) {
                enfriamientoCepo = ENFRIAMIENTO_CEPO;
            }
            ponerEstado(LIBRE, 0);
        }
    }

    /**
     * MeleeAttackGoal llama aqui cuando esta a tiro. No pega: ARRANCA el
     * cepo. El golpe de verdad lo da {@link #tickCepo} cuando los brazos se
     * cierran.
     */
    @Override
    public boolean doHurtTarget(ServerLevel nivel, Entity objetivo) {
        if (getEstado() != LIBRE || enfriamientoCepo > 0) {
            return false;
        }
        ponerEstado(CEPO, DURACION_CEPO);
        // El crujido de cadenas al abrir los brazos: el aviso que se oye.
        playSound(AtalayaSonidos.VIGIA_CEPO_ABRIR, 1.5F, 1.0F);
        return true;
    }

    private void tickCepo(ServerLevel nivel, LivingEntity presa) {
        int transcurrido = DURACION_CEPO - ticksEstado;
        if (transcurrido != IMPACTO_CEPO || presa == null) {
            return;
        }
        Vec3 frente = frente();
        double x = getX() + frente.x * 1.6;
        double z = getZ() + frente.z * 1.6;
        // Si te apartaste mientras abria los brazos, se cierran en el aire.
        if (isWithinMeleeAttackRange(presa) && super.doHurtTarget(nivel, presa)) {
            // Sin particulas de vanilla: el atrapado lo cuentan las esquirlas.
            presa.addEffect(new MobEffectInstance(MobEffects.SLOWNESS, ATRAPADO, 3, false, false), this);
            playSound(AtalayaSonidos.VIGIA_CEPO_CERRAR, 1.5F, 1.0F);
            nivel.sendParticles(AtalayaParticulas.VIGIA_ESQUIRLA, presa.getX(), presa.getY() + 1.0, presa.getZ(),
                    10, 0.3, 0.4, 0.3, 0.05);
        } else {
            playSound(AtalayaSonidos.VIGIA_CEPO_FALLO, 1.2F, 1.0F);
        }
        // Cuenta 0: la particula sale exactamente ahi, sin dispersion.
        nivel.sendParticles(AtalayaParticulas.VIGIA_ZARPA, x, getY() + 1.4, z, 0, 0, 0, 0, 0);
    }

    /**
     * Brazos largos: alcanza mas que un zombi. Un bloque de mas por cada lado,
     * lo justo para que retroceder un paso no baste y haya que retroceder dos.
     */
    @Override
    protected AABB getAttackBoundingBox(double alcance) {
        return super.getAttackBoundingBox(alcance).inflate(0.9, 0.0, 0.9);
    }

    // ------------------------------------------------------------------
    //  La mirada
    // ------------------------------------------------------------------

    private void intentarMirada(LivingEntity presa) {
        if (presa == null || enfriamientoMirada > 0 || !hasLineOfSight(presa)) {
            return;
        }
        double distancia = distanceTo(presa);
        // Ni pegado —ahi ya tiene el cepo— ni mas lejos de lo que distingue.
        if (distancia < MIRADA_MIN || distancia > MIRADA_MAX) {
            return;
        }
        ponerEstado(MIRADA, DURACION_MIRADA);
        ticksSinVer = 0;
        playSound(AtalayaSonidos.VIGIA_MIRADA_CARGA, 2.0F, 1.0F);
    }

    private void tickMirada(ServerLevel nivel, LivingEntity presa) {
        if (presa == null || !presa.isAlive()) {
            cortarMirada();
            return;
        }
        // Esconderse funciona, pero no un parpadeo: tras un pilar fino te
        // sigue viendo por los lados, y eso no deberia salvarte.
        if (hasLineOfSight(presa)) {
            ticksSinVer = 0;
        } else if (++ticksSinVer > MARGEN_SIN_VER) {
            cortarMirada();
            return;
        }

        if (ticksEstado == 1) {
            dispararMirada(nivel, presa);
        }
    }

    private void cortarMirada() {
        playSound(AtalayaSonidos.VIGIA_MIRADA_CORTE, 1.2F, 1.0F);
        enfriamientoMirada = ENFRIAMIENTO_MIRADA_FALLIDA;
        ponerEstado(LIBRE, 0);
    }

    /**
     * Acaba la carga: el ojo dispara. No hace dano aqui; lo hace el rayo si
     * llega. Se apunta a donde esta la presa en este tick, asi que quien se
     * mueve de lado en el ultimo momento lo esquiva.
     */
    private void dispararMirada(ServerLevel nivel, LivingEntity presa) {
        enfriamientoMirada = ENFRIAMIENTO_MIRADA;
        RayoVigiaEntity.disparar(nivel, this, posicionOjo(), presa.getEyePosition().add(0, -0.3, 0));
        playSound(AtalayaSonidos.VIGIA_MIRADA_DISPARO, 2.0F, 1.0F);
        playSound(AtalayaSonidos.VIGIA_RAYO_VUELO, 1.5F, 1.0F);
    }

    // ------------------------------------------------------------------
    //  El punto ciego
    // ------------------------------------------------------------------

    /**
     * Lo que le entra por la espalda duele mas y le hace perder el turno.
     *
     * Es la contrapartida de la mirada y lo que convierte el combate en algo de
     * equipo: mientras uno le aguanta la cara, otro rodea. Un golpe por detras
     * corta la mirada en seco.
     */
    @Override
    public boolean hurtServer(ServerLevel nivel, DamageSource fuente, float cantidad) {
        if (fuente.getEntity() instanceof LivingEntity atacante && porLaEspalda(atacante)) {
            cantidad *= DANO_ESPALDA;
            if (enfriamientoTambaleo <= 0 && getEstado() != TAMBALEO) {
                enfriamientoTambaleo = ENFRIAMIENTO_TAMBALEO;
                ponerEstado(TAMBALEO, DURACION_TAMBALEO);
                playSound(AtalayaSonidos.VIGIA_TAMBALEO, 1.5F, 1.0F);
                nivel.sendParticles(AtalayaParticulas.VIGIA_ESQUIRLA,
                        getX(), getY() + 2.3, getZ(), 14, 0.3, 0.2, 0.3, 0.05);
            }
        }
        return super.hurtServer(nivel, fuente, cantidad);
    }

    private boolean porLaEspalda(LivingEntity atacante) {
        Vec3 haciaAtacante = new Vec3(atacante.getX() - getX(), 0, atacante.getZ() - getZ());
        if (haciaAtacante.lengthSqr() < 1.0E-4) {
            return false;
        }
        // Mas de ~110 grados respecto a donde mira el cuerpo.
        return frente().dot(haciaAtacante.normalize()) < -0.35;
    }

    /** Hacia donde mira el CUERPO, no la cabeza: el punto ciego es la espalda. */
    private Vec3 frente() {
        float rad = yBodyRot * Mth.DEG_TO_RAD;
        return new Vec3(-Mth.sin(rad), 0, Mth.cos(rad));
    }

    private Vec3 posicionOjo() {
        Vec3 frente = frente();
        return new Vec3(getX() + frente.x * 0.6, getY() + 2.45, getZ() + frente.z * 0.6);
    }

    // ------------------------------------------------------------------
    //  Sonidos: todos propios (AtalayaSonidos), ninguno de vanilla
    // ------------------------------------------------------------------

    /** En calma respira dentro del farol; con presa, grune. */
    @Override
    protected SoundEvent getAmbientSound() {
        return isCazando() ? AtalayaSonidos.VIGIA_ACECHO : AtalayaSonidos.VIGIA_AMBIENTE;
    }

    @Override
    protected SoundEvent getHurtSound(DamageSource fuente) {
        return AtalayaSonidos.VIGIA_HERIDO;
    }

    @Override
    protected SoundEvent getDeathSound() {
        return AtalayaSonidos.VIGIA_MUERTE;
    }

    /** Los sonidos ya son graves de por si: aqui solo una pizca de variacion. */
    @Override
    public float getVoicePitch() {
        return 0.92F + random.nextFloat() * 0.16F;
    }

    @Override
    public int getAmbientSoundInterval() {
        return 160;
    }

    /** Pisa mas fuerte cuando persigue: se le oye venir. */
    @Override
    protected void playStepSound(BlockPos pos, BlockState bloque) {
        playSound(AtalayaSonidos.VIGIA_PASO, isCazando() ? 0.9F : 0.55F, 0.9F + random.nextFloat() * 0.2F);
    }

    // ------------------------------------------------------------------
    //  La ultima guardia
    // ------------------------------------------------------------------

    /**
     * Sustituye la muerte de vanilla, que tumba el cuerpo de lado y lo quita a
     * los 20 ticks. Aqui el cuerpo se queda los 60 que dura la animacion, y el
     * servidor pone en su tick los dos momentos que se oyen: el ojo que se
     * apaga y el farol que golpea el suelo.
     */
    @Override
    protected void tickDeath() {
        ++deathTime;
        if (!(level() instanceof ServerLevel nivel) || isRemoved()) {
            return;
        }
        Vec3 frente = frente();
        if (deathTime == MUERTE_APAGARSE) {
            playSound(AtalayaSonidos.VIGIA_APAGARSE, 1.5F, 1.0F);
            // De rodillas, con la cabeza alzada: el ojo queda a 1,9 de alto.
            nivel.sendParticles(AtalayaParticulas.VIGIA_HUMO,
                    getX() + frente.x * 0.5, getY() + 1.9, getZ() + frente.z * 0.5,
                    10, 0.12, 0.12, 0.12, 0.0);
        }
        if (deathTime == MUERTE_FAROL_CAE) {
            playSound(AtalayaSonidos.VIGIA_FAROL_CAE, 1.5F, 1.0F);
            nivel.sendParticles(AtalayaParticulas.VIGIA_HUMO,
                    getX() + frente.x * 1.6, getY() + 0.2, getZ() + frente.z * 1.6,
                    8, 0.25, 0.05, 0.25, 0.0);
            nivel.sendParticles(AtalayaParticulas.VIGIA_ESQUIRLA,
                    getX() + frente.x * 1.6, getY() + 0.3, getZ() + frente.z * 1.6,
                    12, 0.2, 0.05, 0.2, 0.05);
        }
        if (deathTime >= DURACION_MUERTE) {
            // Lo que se escapa del farol al final: almas que suben, y el
            // cuerpo se deshace en humo. Sin el "puf" de vanilla (evento 60):
            // todo lo que se ve morir es suyo.
            nivel.sendParticles(AtalayaParticulas.VIGIA_ALMA,
                    getX(), getY() + 0.6, getZ(), 12, 0.6, 0.3, 0.6, 0.0);
            nivel.sendParticles(AtalayaParticulas.VIGIA_HUMO,
                    getX(), getY() + 0.4, getZ(), 16, 0.7, 0.3, 0.7, 0.0);
            remove(RemovalReason.KILLED);
        }
    }

    // ------------------------------------------------------------------
    //  Goals
    // ------------------------------------------------------------------

    /**
     * Ocupa movimiento y mirada mientras ruge, mira o se tambalea, asi que el
     * selector aparta los goals que andan. Al volver a LIBRE se suelta y la
     * persecucion sigue donde estaba.
     */
    private final class QuietoGoal extends Goal {

        QuietoGoal() {
            setFlags(EnumSet.of(Flag.MOVE, Flag.LOOK, Flag.JUMP));
        }

        @Override
        public boolean canUse() {
            int e = getEstado();
            return e == ALERTA || e == MIRADA || e == TAMBALEO || e == CEPO || e == BUSCAR;
        }

        @Override
        public void start() {
            getNavigation().stop();
        }

        @Override
        public boolean requiresUpdateEveryTick() {
            return true;
        }

        @Override
        public void tick() {
            LivingEntity presa = getTarget();
            // Tambaleandose no apunta a nadie: es justo lo que lo hace un respiro.
            if (presa != null && getEstado() != TAMBALEO) {
                getLookControl().setLookAt(presa, 30.0F, 30.0F);
                // Gira el cuerpo con la cabeza, o el punto ciego quedaria hacia
                // donde andaba y no hacia donde mira.
                yBodyRot = Mth.rotLerp(0.3F, yBodyRot, yHeadRot);
            }
        }
    }

    /** El melee de siempre, pero solo cuando esta libre para atacar. */
    private final class AtaqueGoal extends MeleeAttackGoal {

        AtaqueGoal() {
            super(VigiaEntity.this, VELOCIDAD_PERSECUCION, true);
        }

        @Override
        public boolean canUse() {
            return getEstado() == LIBRE && super.canUse();
        }

        @Override
        public boolean canContinueToUse() {
            return getEstado() == LIBRE && super.canContinueToUse();
        }
    }
}
