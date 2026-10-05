package com.atalaya.entity;

import com.atalaya.effect.BendicionVientosEffect;
import com.atalaya.effect.MarcaVendavalEffect;
import com.atalaya.effect.ParalisisEffect;
import com.atalaya.particula.AtalayaParticulas;
import com.atalaya.sonido.AtalayaSonidos;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.network.protocol.game.ClientboundStopSoundPacket;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundSource;
import net.minecraft.tags.DamageTypeTags;
import net.minecraft.util.Mth;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.damagesource.DamageTypes;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.entity.AnimationState;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.MoverType;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.target.HurtByTargetGoal;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.storage.ValueInput;
import net.minecraft.world.level.storage.ValueOutput;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;
import org.jspecify.annotations.Nullable;

import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;

/**
 * Aeralis, la Mariposa del Vendaval: el segundo de los cuatro jefes elementales.
 *
 * La Maldicion del Aliento le encendio un ojo de huracan en el pecho. Pelea
 * desde el aire, con el torax a unos nueve bloques del suelo: se le pega sobre
 * todo con arcos, ballestas y tridentes, y solo baja al alcance de la espada
 * cuando cae aturdida (los cuatro nucleos del Juicio rotos) o agotada (fase
 * IV). Las alas no tienen caja de golpe: solo cuenta el cuerpo.
 *
 * Nace posada, con las alas cerradas, hasta que ve a alguien; se invoca con su
 * huevo generador. Es el segundo jefe: 13 500 de vida y cada ataque pega mas
 * en cada fase (ver los DANO_*).
 *
 * <pre>
 *   fase I    100-75 %   Brisa: Aleteo Cortante, Tornados
 *   fase II    75-50 %   Rafaga: + La Caceria del Vendaval y el Picado del Vendaval
 *                        (se lanza por una linea que marca en el suelo, mata
 *                        salvo totem y lanza al cielo; se posa 3 s, con dano
 *                        doble: la ventana de la espada); el viento de los
 *                        tornados rotos vuelve a ella y, al juntar 10 (20 en la
 *                        III, 30 en la IV), cae aturdida 5 s
 *   fase III   50-25 %   Tempestad: + Juicio del Ciclon y Escamas de Tormenta (rayos en las alas; inmune
 *                        mientras dura: solo sirve romper los nucleos)
 *   fase IV    25-0 %    Ojo de la tormenta: todo mas seguido y cada 25 s
 *                        cae al suelo agotada (dano doble)
 * </pre>
 *
 * Si el Juicio sale mal (no rompen los cuatro nucleos), al marcado lo mata
 * (salvo totem) y ella entra en la <b>Furia del Vendaval</b>, como la Furia de
 * Jade de Rajang: un aura de rayos violetas, todo un 25 % mas rapido, un 35 %
 * mas de dano y un 35 % menos de espera. Se le va cuando la derriban (cae
 * aturdida: los cuatro nucleos de otro Juicio o el viento de vuelta lleno).
 *
 * Como Nerea, el estado vive en un numero sincronizado, el cliente arranca la
 * animacion que toca al verlo cambiar y los ticks de cada golpe y los puntos
 * del cuerpo salen de {@link AeralisGeometria}, generada con las mismas poses.
 */
public class AeralisEntity extends Monster {

    public static final int LIBRE = 0;
    public static final int DORMIDA = 1;
    public static final int DESPERTAR = 2;
    public static final int ALETEO = 3;
    public static final int TORNADOS = 4;
    public static final int MARCA = 5;
    public static final int RAFAGA = 6;
    public static final int DOBLE_RAFAGA = 7;
    public static final int JUICIO_SUBE = 8;
    public static final int JUICIO_SOSTIENE = 9;
    public static final int JUICIO_GOLPE = 10;
    public static final int ATURDIDA = 11;
    public static final int AGOTADA = 12;
    public static final int TAMBALEO = 13;
    /** El Picado del Vendaval: sube y marca la linea; se lanza; se posa (dano doble). */
    public static final int PICADO_AVISO = 14;
    public static final int PICADO = 15;
    public static final int POSADA = 16;
    /** Escamas de Tormenta: sacude las alas y el suelo se carga donde caen. */
    public static final int ESCAMAS = 17;

    /**
     * Vida EFECTIVA: 13 500 (Nerea, 11 250), la misma con cualquier numero de
     * jugadores. La de vanilla tiene tope de 1024: el dano se divide.
     */
    public static final float VIDA = 13500.0F;
    private static final float VIDA_VANILLA = 1024.0F;

    // --- Danos por fase (I, II, III, IV) ---
    // Pensados para 40 jugadores en hardcore con netherita entera, Proteccion IV
    // y manzana de Notch (18 corazones contando la absorcion): un golpe fuerte
    // les quita 3,5 / 5 / 7,5 / 11 corazones (6, 4, 3 y 2 golpes para matarlos;
    // sin la manzana, en la fase IV basta uno); los de area 2,5 / 4 / 5,5 / 8;
    // los que duran, 1 / 1,5 / 2 / 3 por segundo. Los tipos de dano no escalan
    // con la dificultad.
    public static final float[] DANO_CUCHILLA = {31, 39, 49, 61};
    /** Por segundo mientras un tornado te tiene atrapado (pasa la armadura). */
    public static final float[] DANO_TORNADO = {7, 10, 14, 21};
    /** Cuando el tornado revienta y te lanza. */
    public static final float[] DANO_ESTALLIDO = {27, 37, 44, 55};
    public static final float[] DANO_RAFAGA = {34, 42, 53, 70};
    /**
     * El Picado (desde la fase II): al que pilla lo mata (salvo totem, que lo
     * gasta) pase lo que pase (armadura, escudo, encantamientos, efectos) y lo
     * lanza al cielo, unos 24 bloques: la caida tambien duele.
     */
    public static final float MORTAL = 10000.0F;
    /** La descarga de una mancha de escamas (desde la fase III), y Paralisis 2 s. */
    public static final float[] DANO_ESCAMAS = {20, 20, 20, 28};
    /**
     * El viento corta y se mete por las juntas: contra armadura sus golpes
     * pegan hasta un 30 % mas (con una de diamante o netherita entera).
     */
    private static final float PERFORA_MAXIMO = 0.3F;
    /**
     * El golpe del Juicio al marcado (pasa la armadura): con los cuatro nucleos
     * en pie mata aunque lleve la manzana de Notch; cada nucleo roto le quita
     * un cuarto. A los de alrededor, la mitad.
     */
    public static final float[] DANO_JUICIO = {139, 139, 139, 174};
    public static final float JUICIO_POR_NUCLEO = 0.25F;
    /** Los golpes que aguanta cada nucleo del Juicio, sean cuantos sean. */
    private static final int GOLPES_NUCLEO = 10;
    /** La Furia del Vendaval (el Juicio fallido): mas rapido, mas dano, menos espera. */
    private static final float FURIA_RITMO = 1.25F;
    private static final float FURIA_DANO = 1.35F;
    private static final float FURIA_ENFRIA = 0.65F;
    private static final double FURIA_VUELA = 1.1;

    /**
     * Bloques entre el suelo y la base de la caja al volar: el torax queda a
     * unos 15. Desde el remake sus alas miden unos 38 bloques y las colas de las
     * de abajo bajan 13 por debajo del torax: mas abajo rozarian el suelo.
     */
    public static final double ALTURA_VUELO = 7.5;
    /** A donde sube para el Juicio. */
    public static final double ALTURA_JUICIO = 13.0;
    /** Lo bajo que pasa en la pasada rasante (las colas, a ras de suelo). */
    private static final double ALTURA_RASANTE = 5.5;
    /**
     * El Picado: la linea mide lo que hay hasta la presa mas 14 (de 36 a 60
     * bloques) y lo recorre a 45 bloques/s: baja en el primer tercio y luego
     * barre el suelo hasta el final. Pilla lo que haya en la linea (su medio
     * ancho, PICADO_LADO) y lo lanza al cielo (unos 24 bloques).
     */
    private static final double VEL_PICADO = 2.25;
    private static final double PICADO_MIN = 36.0;
    private static final double PICADO_MAX = 60.0;
    private static final double PICADO_PASA = 14.0;
    private static final double PICADO_LANZA = 2.2;
    private static final double PICADO_LADO = 3.0;
    /** A que altura barre el suelo y en que parte de la linea termina de bajar. */
    private static final double PICADO_RAS = 1.0;
    private static final double PICADO_BAJA = 0.3;
    /** Las manchas de escamas: radio, vida, cuando se cargan y cada cuanto descargan. */
    public static final double MANCHA_RADIO = 2.5;
    private static final int MANCHA_VIDA = 120;
    private static final int MANCHA_CARGA = 20;
    private static final int MANCHA_CADA = 30;
    private static final double ESCAMAS_RADIO = 15.0;
    /** Lo que paraliza una descarga (2 s) y cuando puede volver a paralizarte (3 s despues: 1 s para salir). */
    private static final int PARALISIS_ESCAMAS = 40;
    private static final int PARALISIS_RESPIRO = 60;
    /**
     * El viento de vuelta (desde la fase II): cada tornado roto le devuelve su
     * viento, un orbe que vuela a su pecho. Con 10 en la fase II, 20 en la III
     * y 30 en la IV se llena la barra y cae aturdida 5 s.
     */
    private static final int[] VIENTO_NECESARIO = {0, 10, 20, 30};
    private static final double VEL_VIENTO = 1.1;
    /** Hasta donde llegan las cuchillas del Aleteo. */
    public static final double ALCANCE_CUCHILLA = 48.0;
    /** Lo lejos que se aparta de donde nacio. */
    private static final double CORREA = 40.0;
    private static final int CADA_AGOTADA = 500;
    /** Lo que dura La Caceria: 15 s. */
    private static final int CAZA = 300;
    /** Lo que sostiene el ciclon del Juicio antes del golpe: 12 s. */
    public static final int JUICIO_TICKS = 240;
    /** A partir de cuantos bloques del resto del grupo se acelera la caza. */
    private static final double LEJOS_DEL_GRUPO = 12.0;
    private static final double RANGO_DESPERTAR = 40.0;

    private static final EntityDataAccessor<Integer> DATA_ESTADO =
            SynchedEntityData.defineId(AeralisEntity.class, EntityDataSerializers.INT);
    /** Fase (1-4): las alas se oscurecen y se rasgan con cada una. */
    private static final EntityDataAccessor<Integer> DATA_FASE =
            SynchedEntityData.defineId(AeralisEntity.class, EntityDataSerializers.INT);
    /** La presa de la Caceria o el marcado del Juicio. -1 si nadie. */
    private static final EntityDataAccessor<Integer> DATA_OBJETIVO =
            SynchedEntityData.defineId(AeralisEntity.class, EntityDataSerializers.INT);
    /** La presa se ha alejado del grupo: la caza va mas deprisa. */
    private static final EntityDataAccessor<Boolean> DATA_ACELERADA =
            SynchedEntityData.defineId(AeralisEntity.class, EntityDataSerializers.BOOLEAN);
    /** El Picado: lo que le queda de linea por delante (0: no hay linea). */
    private static final EntityDataAccessor<Float> DATA_PICADO =
            SynchedEntityData.defineId(AeralisEntity.class, EntityDataSerializers.FLOAT);
    /** Los orbes de viento de vuelta que lleva (la raya fina bajo su barra). */
    private static final EntityDataAccessor<Integer> DATA_VIENTO =
            SynchedEntityData.defineId(AeralisEntity.class, EntityDataSerializers.INT);
    /** Los nucleos del Juicio rotos, uno por bit (para la barra, como los totems de Rajang). */
    private static final EntityDataAccessor<Integer> DATA_NUCLEOS =
            SynchedEntityData.defineId(AeralisEntity.class, EntityDataSerializers.INT);
    /** La Furia del Vendaval: el aura de rayos. */
    private static final EntityDataAccessor<Boolean> DATA_FURIA =
            SynchedEntityData.defineId(AeralisEntity.class, EntityDataSerializers.BOOLEAN);

    // --- Solo cliente ---
    public final AnimationState dormida = new AnimationState();
    public final AnimationState despertar = new AnimationState();
    public final AnimationState aleteo = new AnimationState();
    public final AnimationState tornados = new AnimationState();
    public final AnimationState marca = new AnimationState();
    public final AnimationState rafaga = new AnimationState();
    public final AnimationState dobleRafaga = new AnimationState();
    public final AnimationState juicioSube = new AnimationState();
    public final AnimationState juicioSostiene = new AnimationState();
    public final AnimationState juicioGolpe = new AnimationState();
    public final AnimationState aturdida = new AnimationState();
    public final AnimationState agotada = new AnimationState();
    public final AnimationState tambaleo = new AnimationState();
    public final AnimationState liberacion = new AnimationState();
    public final AnimationState picadoAviso = new AnimationState();
    public final AnimationState picado = new AnimationState();
    public final AnimationState posada = new AnimationState();
    public final AnimationState escamas = new AnimationState();
    /** Tick del cliente en que empezo el estado actual. */
    public int inicioEstado;
    /** Ritmo de la animacion actual en el cliente (el mismo que el servidor). */
    public float ritmoCliente = 1.0F;
    /** Cuanto pesa el vuelo (0 a 1): baja al empezar un ataque y sube al acabar. */
    public float pesoLibre = 1.0F;
    public float pesoLibreAnt = 1.0F;
    /**
     * Como vuela, en el cliente: cuanto se inclina hacia delante al avanzar y
     * cuanto se ladea al desplazarse de lado o girar (grados), y cuanto pesa el
     * vuelo rapido (0 a 1). Se suavizan tick a tick: tiene inercia.
     */
    public float cabeceo;
    public float cabeceoAnt;
    public float alabeo;
    public float alabeoAnt;
    public float avance;
    public float avanceAnt;
    /** Reloj de la batida (ms de animacion): corre mas deprisa cuanto mas rapido vuela. */
    public float relojVuelo;
    public float relojVueloAnt;

    // --- Solo servidor ---
    private @Nullable BlockPos centro;
    private float factorGrupo = VIDA_VANILLA / VIDA;
    private int jugadoresGrupo = 1;
    private int t;
    private int duracion;
    private float ritmoEstado = 1.0F;
    private int respiro = 20;
    private int enfAleteo = 20;
    private int enfTornados = 90;
    private int enfCaza = 120;
    private int enfJuicio = 200;
    private int enfPicado = 160;
    private int enfEscamas = 300;
    /** El Picado: rumbo, largo de la linea, lo que lleva y a quien ya ha golpeado. */
    private Vec3 dirPicado = new Vec3(0, 0, 1);
    private double largoPicado;
    private double recorridoPicado;
    private @Nullable LivingEntity blancoPicado;
    private final java.util.Set<Integer> golpeadosPicado = new java.util.HashSet<>();
    /** Las manchas de escamas en el suelo: x, y, z y edad (ticks). */
    private final List<double[]> manchas = new ArrayList<>();
    private @Nullable Vec3 centroEscamas;
    /** A quien paralizo una descarga y en que tick (para dejarle salir de la mancha). */
    private final java.util.Map<Integer, Integer> paralizados = new java.util.HashMap<>();
    /** Los orbes de viento de vuelta en camino: x, y, z y edad. */
    private final List<double[]> vientos = new ArrayList<>();
    private boolean aturdidaPendiente;
    private int relojAgotado = CADA_AGOTADA;
    private int relojTrueno = 160;
    private int ultimoAvisoInmune;
    /** Hacia donde rodea al grupo (1 o -1) y por donde va. */
    private int sentido = 1;
    private float orbita;
    private @Nullable LivingEntity presa;
    /** Ticks que le quedan a La Caceria (0: no hay caza) y cuantas rafagas lleva. */
    private int caza;
    private int cazaPaso;
    private final List<TornadoAeralisEntity> tornadosVivos = new ArrayList<>();
    private final List<NucleoVientoEntity> nucleos = new ArrayList<>();
    /** Los cuatro nucleos del Juicio en su orden (para saber cual se ha roto). */
    private final NucleoVientoEntity[] nucleosJuicio = new NucleoVientoEntity[4];
    private @Nullable TornadoAeralisEntity ciclon;
    /** Los que atrapa el ciclon del Juicio: un tercio de los que pelean, los de menos vida. */
    private final List<LivingEntity> juzgados = new ArrayList<>();
    private int nucleosRotos;
    /** Pasada rasante entre ataques: ticks que le quedan y a donde va. */
    private int rasante;
    private int relojRasante = 160;
    private @Nullable Vec3 destinoRasante;

    public AeralisEntity(EntityType<? extends Monster> tipo, Level nivel) {
        super(tipo, nivel);
        this.xpReward = 400;
        // Vuela: ni gravedad ni choques. La altura y la ruta las lleva ella
        // (volar()); con 38 bloques de alas, chocar con cada arbol la frenaria.
        this.noPhysics = true;
        setNoGravity(true);
    }

    public static AttributeSupplier.Builder crearAtributos() {
        return Monster.createMonsterAttributes()
                .add(Attributes.MAX_HEALTH, VIDA_VANILLA)
                .add(Attributes.ARMOR, 14.0D)
                .add(Attributes.ARMOR_TOUGHNESS, 8.0D)
                .add(Attributes.ATTACK_DAMAGE, 12.0D)
                .add(Attributes.MOVEMENT_SPEED, 0.3D)
                .add(Attributes.FLYING_SPEED, 0.6D)
                .add(Attributes.FOLLOW_RANGE, 72.0D)
                .add(Attributes.KNOCKBACK_RESISTANCE, 1.0D);
    }

    @Override
    protected void defineSynchedData(SynchedEntityData.Builder datos) {
        super.defineSynchedData(datos);
        datos.define(DATA_ESTADO, DORMIDA);
        datos.define(DATA_FASE, 1);
        datos.define(DATA_OBJETIVO, -1);
        datos.define(DATA_ACELERADA, false);
        datos.define(DATA_PICADO, 0.0F);
        datos.define(DATA_VIENTO, 0);
        datos.define(DATA_FURIA, false);
        datos.define(DATA_NUCLEOS, 0);
    }

    @Override
    protected void registerGoals() {
        targetSelector.addGoal(1, new HurtByTargetGoal(this));
        targetSelector.addGoal(2, new NearestAttackableTargetGoal<>(this, Player.class, false));
    }

    // ------------------------------------------------------------------
    //  Lo que se lee desde fuera
    // ------------------------------------------------------------------

    public int getEstado() {
        return entityData.get(DATA_ESTADO);
    }

    public int fase() {
        return entityData.get(DATA_FASE);
    }

    public int getIdObjetivo() {
        return entityData.get(DATA_OBJETIVO);
    }

    public boolean isAcelerada() {
        return entityData.get(DATA_ACELERADA);
    }

    /** La linea del Picado que le queda por delante (bloques); 0 si no hay. */
    public float getPicado() {
        return entityData.get(DATA_PICADO);
    }

    /** Los orbes de viento de vuelta que lleva para la siguiente vez que cae aturdida. */
    public int getViento() {
        return entityData.get(DATA_VIENTO);
    }

    /** Los nucleos del Juicio que ya han roto, un bit cada uno. */
    public int getNucleosRotos() {
        return entityData.get(DATA_NUCLEOS);
    }

    /** Con la Furia del Vendaval (el aura de rayos): ha fallado un Juicio y aun no la han derribado. */
    public boolean tieneFuria() {
        return entityData.get(DATA_FURIA);
    }

    /** Cuantos orbes hacen falta en esa fase para aturdirla (en la fase I no cuentan). */
    public static int vientoNecesario(int fase) {
        return VIENTO_NECESARIO[Mth.clamp(fase, 1, 4) - 1];
    }

    public @Nullable BlockPos getCentro() {
        return centro;
    }

    /** Cuantos jugadores habia al despertar: mas tornados, mas cuchillas. */
    public int getJugadoresGrupo() {
        return jugadoresGrupo;
    }

    private int faseSegunVida() {
        float k = getHealth() / getMaxHealth();
        return k > 0.75F ? 1 : k > 0.5F ? 2 : k > 0.25F ? 3 : 4;
    }

    private void ponerEstado(int estado, int dur) {
        entityData.set(DATA_ESTADO, estado);
        t = 0;
        ritmoEstado = ritmo(estado, fase(), isAcelerada(), tieneFuria());
        duracion = (int) Math.ceil(dur / ritmoEstado);
    }

    /**
     * Lo rapido que van sus ataques: x1,05 en la fase I hasta x1,45 en la IV
     * (Nerea iba de x1 a x1,4), las rafagas un 30 % mas si la presa se aleja
     * del grupo y todo un 25 % mas con la Furia. El cliente usa el mismo numero
     * para la animacion.
     */
    public static float ritmo(int estado, int fase, boolean acelerada, boolean furia) {
        float k = switch (estado) {
            case ALETEO, TORNADOS, MARCA, RAFAGA, DOBLE_RAFAGA, JUICIO_GOLPE, PICADO_AVISO, ESCAMAS ->
                    new float[]{1.0F, 1.05F, 1.15F, 1.3F, 1.45F}[Mth.clamp(fase, 1, 4)];
            default -> 1.0F;
        };
        if (acelerada && (estado == RAFAGA || estado == DOBLE_RAFAGA)) {
            k *= 1.3F;
        }
        if (furia && k > 1.0F) {
            k *= FURIA_RITMO;
        }
        return k;
    }

    private float ta() {
        return t * ritmoEstado;
    }

    private boolean cruza(int k) {
        return (t - 1) * ritmoEstado < k && t * ritmoEstado >= k;
    }

    /**
     * Lo que pega a v un golpe de dano base "dano": cuanta mas armadura (y
     * dureza) lleva, mas se mete el viento por las juntas, hasta un 30 % mas.
     */
    public static float contraArmadura(LivingEntity v, float dano) {
        float armadura = v.getArmorValue();
        float dureza = (float) v.getAttributeValue(Attributes.ARMOR_TOUGHNESS);
        return dano * (1.0F + Math.min(PERFORA_MAXIMO, armadura * 0.012F + dureza * 0.01F));
    }

    /** El dano de un ataque en la fase actual: cada ataque lleva el suyo de la fase I a la IV; con la Furia, un 35 % mas. */
    public float dano(float[] porFase) {
        float d = porFase[Mth.clamp(fase(), 1, 4) - 1];
        return tieneFuria() ? d * FURIA_DANO : d;
    }

    @Override
    public void onSyncedDataUpdated(EntityDataAccessor<?> dato) {
        super.onSyncedDataUpdated(dato);
        if (DATA_ESTADO.equals(dato) && level().isClientSide()) {
            arrancarAnimacion();
        }
    }

    private AnimationState[] acciones() {
        return new AnimationState[]{dormida, despertar, aleteo, tornados, marca, rafaga, dobleRafaga, juicioSube,
                juicioSostiene, juicioGolpe, aturdida, agotada, tambaleo, picadoAviso, picado, posada, escamas};
    }

    private @Nullable AnimationState animacionDe(int estado) {
        return switch (estado) {
            case DORMIDA -> dormida;
            case DESPERTAR -> despertar;
            case ALETEO -> aleteo;
            case TORNADOS -> tornados;
            case MARCA -> marca;
            case RAFAGA -> rafaga;
            case DOBLE_RAFAGA -> dobleRafaga;
            case JUICIO_SUBE -> juicioSube;
            case JUICIO_SOSTIENE -> juicioSostiene;
            case JUICIO_GOLPE -> juicioGolpe;
            case ATURDIDA -> aturdida;
            case AGOTADA -> agotada;
            case TAMBALEO -> tambaleo;
            case PICADO_AVISO -> picadoAviso;
            case PICADO -> picado;
            case POSADA -> posada;
            case ESCAMAS -> escamas;
            default -> null;
        };
    }

    private void arrancarAnimacion() {
        for (AnimationState a : acciones()) {
            a.stop();
        }
        inicioEstado = tickCount;
        ritmoCliente = ritmo(getEstado(), fase(), isAcelerada(), tieneFuria());
        AnimationState actual = animacionDe(getEstado());
        if (actual != null) {
            actual.start(tickCount);
        }
    }

    // ------------------------------------------------------------------
    //  Cliente: lo que se ve sin gastar red
    // ------------------------------------------------------------------

    @Override
    public void tick() {
        super.tick();
        if (!level().isClientSide()) {
            return;
        }
        boolean muriendo = isDeadOrDying();
        AnimationState actual = animacionDe(getEstado());
        if (!muriendo && actual != null && !actual.isStarted()) {
            arrancarAnimacion();
        }
        pesoLibreAnt = pesoLibre;
        float objetivoPeso = getEstado() == LIBRE && !muriendo ? 1.0F : 0.0F;
        pesoLibre = objetivoPeso > pesoLibre ? Math.min(objetivoPeso, pesoLibre + 0.2F) : Math.max(objetivoPeso, pesoLibre - 0.25F);
        dinamicaVuelo(muriendo);
        if (muriendo) {
            if (!liberacion.isStarted()) {
                for (AnimationState a : acciones()) {
                    a.stop();
                }
                liberacion.start(tickCount);
            }
            return;
        }
        int e = getEstado();
        int f = fase();
        if (e == JUICIO_SUBE) {
            // El silencio: ni una mota. Hasta el ojo de la tormenta se apaga.
            return;
        }
        // El batir del vuelo: el golpe de las alas suena con la animacion (con
        // su reloj, que se acelera al volar rapido) y empuja aire hacia abajo.
        float periodo = AeralisGeometria.PERIODO_VUELO * 50.0F;
        float golpe = AeralisGeometria.VUELO_GOLPE * 50.0F;
        if (e == LIBRE && Math.floor((relojVuelo - golpe) / periodo) != Math.floor((relojVueloAnt - golpe) / periodo)) {
            level().playLocalSound(getX(), getY() + 6.0, getZ(), AtalayaSonidos.AERALIS_ALETEO, SoundSource.HOSTILE,
                    2.2F + avance, 0.9F + random.nextFloat() * 0.2F - 0.1F * avance, false);
            for (Vec3 punta : new Vec3[]{AeralisGeometria.PUNTA_ALA_IZQ, AeralisGeometria.PUNTA_ALA_DER}) {
                Vec3 p = puntoMundo(punta.scale(0.6));
                for (int i = 0; i < 4; i++) {
                    level().addParticle(AtalayaParticulas.AERALIS_VIENTO, p.x + random.nextGaussian(), p.y - 2.0,
                            p.z + random.nextGaussian(), random.nextGaussian() * 0.05, -0.55, random.nextGaussian() * 0.05);
                }
            }
            if (getY() - sueloBajo(level(), getX(), getY(), getZ()) < 6.0) {
                // Cerca del suelo, la batida levanta polvo.
                for (int i = 0; i < 10; i++) {
                    double a = random.nextDouble() * Math.PI * 2;
                    double y0 = sueloBajo(level(), getX(), getY(), getZ());
                    level().addParticle(AtalayaParticulas.AERALIS_POLVO, getX() + Math.cos(a) * 2, y0 + 0.2,
                            getZ() + Math.sin(a) * 2, Math.cos(a) * 0.35, 0.03, Math.sin(a) * 0.35);
                }
            }
        }
        // Volando deprisa, las puntas de las alas dejan estela.
        if (e == LIBRE && avance > 0.45F && tickCount % 2 == 0) {
            Vec3 atras = frente().scale(-0.4 * avance);
            for (Vec3 punta : new Vec3[]{AeralisGeometria.PUNTA_ALA_IZQ, AeralisGeometria.PUNTA_ALA_DER}) {
                Vec3 p = puntoMundo(punta.scale(0.9));
                level().addParticle(AtalayaParticulas.AERALIS_VIENTO, p.x, p.y, p.z, atras.x, -0.05, atras.z);
            }
        }
        efectosAtaque(e);
        // La Furia: luz que le sube por el cuerpo y rayos que le saltan por las alas.
        if (tieneFuria()) {
            for (int i = 0; i < 2; i++) {
                Vec3 p = puntoMundo(new Vec3((random.nextDouble() - 0.5) * 6.0, 4.0 + random.nextDouble() * 12.0,
                        (random.nextDouble() - 0.5) * 4.0));
                level().addParticle(AtalayaParticulas.AERALIS_LUZ, p.x, p.y, p.z, random.nextGaussian() * 0.02, 0.09,
                        random.nextGaussian() * 0.02);
            }
            if (random.nextInt(2) == 0) {
                Vec3 punta = random.nextBoolean() ? AeralisGeometria.PUNTA_ALA_IZQ : AeralisGeometria.PUNTA_ALA_DER;
                Vec3 p = puntoMundo(punta.scale(0.2 + random.nextDouble() * 0.8));
                level().addParticle(AtalayaParticulas.AERALIS_RAYO, p.x, p.y, p.z, 0, 0, 0);
            }
        }
        // El ojo de la tormenta gira y suelta motas: mas cuanto mas avanzada la fase.
        if (e != DORMIDA && tickCount % Math.max(2, 7 - f) == 0) {
            Vec3 c = puntoMundo(AeralisGeometria.NUCLEO);
            double a = random.nextDouble() * Math.PI * 2;
            level().addParticle(AtalayaParticulas.AERALIS_LUZ, c.x + Math.cos(a) * 0.9, c.y + Math.sin(a) * 0.9, c.z,
                    -Math.sin(a) * 0.06, Math.cos(a) * 0.06, 0.02);
        }
        // Escamas que se le caen de las alas.
        if (e != DORMIDA && random.nextInt(8) == 0) {
            Vec3 punta = random.nextBoolean() ? AeralisGeometria.PUNTA_ALA_IZQ : AeralisGeometria.PUNTA_ALA_DER;
            Vec3 p = puntoMundo(punta.scale(0.3 + random.nextDouble() * 0.6));
            level().addParticle(AtalayaParticulas.AERALIS_ESCAMA, p.x, p.y, p.z, 0, -0.02, 0);
        }
        // Tempestad: los rayos le saltan dentro de las alas.
        if (f >= 3 && e != DORMIDA && random.nextInt(f >= 4 ? 4 : 7) == 0) {
            Vec3 punta = random.nextBoolean() ? AeralisGeometria.PUNTA_ALA_IZQ : AeralisGeometria.PUNTA_ALA_DER;
            Vec3 p = puntoMundo(punta.scale(0.25 + random.nextDouble() * 0.65));
            level().addParticle(AtalayaParticulas.AERALIS_RAYO, p.x, p.y, p.z, 0, 0, 0);
        }
        if (e == DORMIDA && tickCount % 12 == 0) {
            Vec3 c = puntoMundo(new Vec3(0, 4.5, 1.0));
            level().addParticle(AtalayaParticulas.AERALIS_LUZ, c.x + random.nextGaussian() * 0.3, c.y,
                    c.z + random.nextGaussian() * 0.3, 0, 0.02, 0);
        }
    }

    /**
     * Cliente: la inercia del vuelo. Se inclina hacia donde avanza, se ladea
     * al desplazarse de lado y al girar, y el vuelo rapido pesa mas cuanto mas
     * corre. En el suelo (dormida, aturdida, agotada) se endereza.
     */
    private void dinamicaVuelo(boolean muriendo) {
        cabeceoAnt = cabeceo;
        alabeoAnt = alabeo;
        avanceAnt = avance;
        relojVueloAnt = relojVuelo;
        int e = getEstado();
        boolean enAire = !muriendo && e != DORMIDA && e != ATURDIDA && e != AGOTADA && e != POSADA && e != PICADO;
        double vx = getX() - xo;
        double vz = getZ() - zo;
        float b = yBodyRot * Mth.DEG_TO_RAD;
        double delante = -vx * Mth.sin(b) + vz * Mth.cos(b);
        double lado = vx * Mth.cos(b) + vz * Mth.sin(b);
        float giro = Mth.wrapDegrees(yBodyRot - yBodyRotO);
        float objCabeceo = enAire ? Mth.clamp((float) delante * 50.0F, -14.0F, 26.0F) : 0.0F;
        float objAlabeo = enAire ? Mth.clamp((float) lado * 55.0F - giro * 1.6F, -30.0F, 30.0F) : 0.0F;
        float objAvance = enAire && e == LIBRE ? Mth.clamp((float) Math.sqrt(vx * vx + vz * vz) / 0.42F, 0.0F, 1.0F) : 0.0F;
        cabeceo += (objCabeceo - cabeceo) * 0.15F;
        alabeo += (objAlabeo - alabeo) * 0.12F;
        avance += (objAvance - avance) * 0.1F;
        relojVuelo += 50.0F * (1.0F + 0.3F * avance);
    }

    /**
     * Cliente: lo que acompana a cada ataque y no necesita al servidor: el
     * aire que se junta en las alas antes del tajo, la estela del tajo, la
     * bola de viento que se forma en el pecho antes de cada rafaga, el hilo de
     * runas de las antenas a la presa marcada y el polvo que sube hacia ella
     * antes de los tornados.
     */
    private void efectosAtaque(int e) {
        float ta = (tickCount - inicioEstado) * ritmoCliente;
        Vec3 f = frente();
        switch (e) {
            case ALETEO -> {
                if (ta >= AeralisGeometria.ALETEO_CARGA && ta < AeralisGeometria.ALETEO_SUELTA) {
                    for (Vec3 punta : new Vec3[]{new Vec3(12.0, 13.5, -2.0), new Vec3(-12.0, 13.5, -2.0)}) {
                        Vec3 p = puntoMundo(punta);
                        for (int i = 0; i < 2; i++) {
                            Vec3 d = new Vec3(random.nextGaussian(), random.nextGaussian(), random.nextGaussian()).normalize().scale(5.0);
                            level().addParticle(AtalayaParticulas.AERALIS_VIENTO, p.x + d.x, p.y + d.y, p.z + d.z,
                                    -d.x * 0.16, -d.y * 0.16, -d.z * 0.16);
                        }
                        level().addParticle(AtalayaParticulas.AERALIS_LUZ, p.x, p.y, p.z, 0, 0, 0);
                    }
                }
                if (ta >= AeralisGeometria.ALETEO_SUELTA - 1 && ta < AeralisGeometria.ALETEO_SUELTA + 5) {
                    // El tajo: un arco de viento de punta a punta, por delante.
                    for (int i = 0; i < 14; i++) {
                        double k = random.nextDouble() * 2 - 1;
                        Vec3 local = new Vec3(k * 15.0, 7.0 + random.nextDouble() * 2.0, 9.0 - 5.0 * k * k);
                        Vec3 p = puntoMundo(local);
                        level().addParticle(i % 3 == 0 ? AtalayaParticulas.AERALIS_JIRON : AtalayaParticulas.AERALIS_VIENTO,
                                p.x, p.y, p.z, f.x * 0.8, -0.1, f.z * 0.8);
                    }
                }
            }
            case RAFAGA, DOBLE_RAFAGA -> {
                int[] sueltas = e == RAFAGA ? new int[]{AeralisGeometria.RAFAGA_SUELTA}
                        : new int[]{AeralisGeometria.DOBLE_SUELTA_1, AeralisGeometria.DOBLE_SUELTA_2};
                for (int s : sueltas) {
                    if (ta >= s - 6 && ta < s) {
                        Vec3 c = puntoMundo(AeralisGeometria.NUCLEO).add(f.scale(2.5));
                        for (int i = 0; i < 4; i++) {
                            Vec3 d = new Vec3(random.nextGaussian(), random.nextGaussian(), random.nextGaussian()).normalize().scale(3.0);
                            level().addParticle(AtalayaParticulas.AERALIS_VIENTO, c.x + d.x, c.y + d.y, c.z + d.z,
                                    -d.x * 0.25, -d.y * 0.25, -d.z * 0.25);
                        }
                    }
                }
            }
            case MARCA -> {
                Entity presaCliente = level().getEntity(getIdObjetivo());
                if (presaCliente != null && ta >= AeralisGeometria.MARCA_FIJA - 4) {
                    // El hilo de runas: de las antenas a la presa.
                    Vec3 a = puntoMundo(new Vec3(0, 14.5, 2.0));
                    Vec3 b2 = presaCliente.position().add(0, presaCliente.getBbHeight() * 0.6, 0);
                    for (int i = 0; i < 6; i++) {
                        Vec3 p = a.lerp(b2, random.nextDouble());
                        level().addParticle(AtalayaParticulas.AERALIS_MARCA, p.x, p.y, p.z, 0, 0.01, 0);
                    }
                }
            }
            case TORNADOS -> {
                if (ta < AeralisGeometria.TORNADOS_GOLPE) {
                    // El aire se le va hacia arriba: el polvo del suelo sube a ella.
                    double y0 = sueloBajo(level(), getX(), getY(), getZ());
                    for (int i = 0; i < 3; i++) {
                        double a = random.nextDouble() * Math.PI * 2;
                        double r = 3.0 + random.nextDouble() * 8.0;
                        level().addParticle(AtalayaParticulas.AERALIS_POLVO, getX() + Math.cos(a) * r, y0 + 0.2,
                                getZ() + Math.sin(a) * r, -Math.cos(a) * 0.2, 0.25, -Math.sin(a) * 0.2);
                    }
                }
            }
            case PICADO -> {
                // La estela: de las puntas de las alas plegadas y del cuerpo, hacia atras.
                Vec3 atras = f.scale(-0.6);
                for (Vec3 local : new Vec3[]{new Vec3(3.0, 9.0, -4.0), new Vec3(-3.0, 9.0, -4.0), new Vec3(0, 7.0, -2.0)}) {
                    Vec3 p = puntoMundo(local);
                    level().addParticle(AtalayaParticulas.AERALIS_JIRON, p.x, p.y, p.z, atras.x, 0.1, atras.z);
                }
            }
            case PICADO_AVISO -> {
                // El viento se le junta en las alas antes de lanzarse.
                if (tickCount % 2 == 0) {
                    Vec3 c = puntoMundo(AeralisGeometria.NUCLEO);
                    Vec3 d = new Vec3(random.nextGaussian(), random.nextGaussian(), random.nextGaussian()).normalize().scale(7.0);
                    level().addParticle(AtalayaParticulas.AERALIS_VIENTO, c.x + d.x, c.y + d.y, c.z + d.z,
                            -d.x * 0.12, -d.y * 0.12, -d.z * 0.12);
                }
            }
            case JUICIO_SOSTIENE -> {
                if (random.nextInt(3) == 0) {
                    Vec3 c = puntoMundo(AeralisGeometria.NUCLEO);
                    double a = tickCount * 0.4;
                    level().addParticle(AtalayaParticulas.AERALIS_LUZ, c.x + Math.cos(a) * 1.4, c.y + Math.sin(a) * 1.4, c.z,
                            -Math.cos(a) * 0.08, -Math.sin(a) * 0.08, 0);
                }
            }
            default -> {
            }
        }
    }

    // ------------------------------------------------------------------
    //  Servidor
    // ------------------------------------------------------------------

    @Override
    protected void customServerAiStep(ServerLevel nivel) {
        super.customServerAiStep(nivel);
        if (centro == null) {
            centro = blockPosition();
        }
        if (getEstado() != DORMIDA && !isDeadOrDying()) {
            int nueva = faseSegunVida();
            if (nueva > fase()) {
                alCambiarFase(nivel, nueva);
            }
        }
        LivingEntity objetivo = getTarget();
        if (objetivo != null && (!objetivo.isAlive() || objetivo.distanceToSqr(Vec3.atCenterOf(centro)) > 72 * 72)) {
            setTarget(null);
            objetivo = null;
        }
        if (respiro > 0) respiro--;
        if (enfAleteo > 0) enfAleteo--;
        if (enfTornados > 0) enfTornados--;
        if (enfCaza > 0 && caza <= 0) enfCaza--;
        if (enfJuicio > 0) enfJuicio--;
        if (enfPicado > 0) enfPicado--;
        if (enfEscamas > 0) enfEscamas--;
        tornadosVivos.removeIf(Entity::isRemoved);
        tickManchas(nivel);
        tickVientos(nivel);

        int e = getEstado();
        t++;
        if (caza > 0) {
            tickCaza(nivel);
        }
        switch (e) {
            case DORMIDA -> tickDormida(nivel);
            case DESPERTAR -> tickDespertar(nivel);
            case LIBRE -> tickLibre(nivel, objetivo);
            case ALETEO -> tickAleteo(nivel, objetivo);
            case TORNADOS -> tickTornados(nivel, objetivo);
            case MARCA -> tickMarca(nivel);
            case RAFAGA -> tickRafaga(nivel, false);
            case DOBLE_RAFAGA -> tickRafaga(nivel, true);
            case JUICIO_SUBE -> tickJuicioSube(nivel);
            case JUICIO_SOSTIENE -> tickJuicioSostiene(nivel);
            case JUICIO_GOLPE -> tickJuicioGolpe(nivel);
            case ATURDIDA -> tickAturdida(nivel);
            case AGOTADA -> tickAgotada(nivel);
            case TAMBALEO -> tickTambaleo(nivel);
            case PICADO_AVISO -> tickPicadoAviso(nivel);
            case PICADO -> tickPicado(nivel);
            case POSADA -> tickPosada(nivel);
            case ESCAMAS -> tickEscamas(nivel, objetivo);
            default -> {
            }
        }
        if (e != LIBRE && e != DORMIDA && getEstado() == e && t >= duracion) {
            alAcabar(nivel, e);
        }
        if (aturdidaPendiente && aturdible(getEstado()) && !isDeadOrDying()) {
            aturdidaPendiente = false;
            aturdir(nivel);
        }
        if (fase() >= 3 && getEstado() != DORMIDA && getEstado() != JUICIO_SUBE && --relojTrueno <= 0) {
            relojTrueno = 140 + random.nextInt(160) - fase() * 20;
            sonido(AtalayaSonidos.AERALIS_TRUENO, 6.0F);
            for (int i = 0; i < 6; i++) {
                Vec3 punta = random.nextBoolean() ? AeralisGeometria.PUNTA_ALA_IZQ : AeralisGeometria.PUNTA_ALA_DER;
                Vec3 p = puntoMundo(punta.scale(0.3 + random.nextDouble() * 0.6));
                nivel.sendParticles(AtalayaParticulas.AERALIS_RAYO, true, true, p.x, p.y, p.z, 1, 0.4, 0.4, 0.4, 0.0);
            }
        }
        volar(nivel, objetivo);
    }

    /** Lo que pasa al acabar cada estado: casi todos vuelven a volar libres. */
    private void alAcabar(ServerLevel nivel, int e) {
        switch (e) {
            case JUICIO_SUBE -> empezarCiclon(nivel);
            case PICADO_AVISO -> empezarPicado(nivel);
            case PICADO -> posarse(nivel);
            case JUICIO_SOSTIENE -> {
                ponerEstado(JUICIO_GOLPE, AeralisGeometria.DURACION_JUICIO_GOLPE);
                sonido(AtalayaSonidos.AERALIS_JUICIO_GOLPE, 8.0F);
                if (ciclon != null && !ciclon.isRemoved()) {
                    ciclon.lanzarAlCielo();
                }
            }
            default -> terminar();
        }
    }

    private void terminar() {
        ponerEstado(LIBRE, 0);
        respiro = caza > 0 ? new int[]{0, 14, 12, 10, 8}[fase()] : new int[]{0, 16, 12, 9, 6}[fase()];
        if (tieneFuria()) {
            respiro /= 2;
        }
    }

    /** Cada fase todo vuelve antes: en la IV, con un 36 % menos de espera; con la Furia, un 35 % menos encima. */
    private float enfriamiento() {
        float k = new float[]{1.0F, 1.0F, 0.88F, 0.76F, 0.64F}[Mth.clamp(fase(), 1, 4)];
        return tieneFuria() ? k * FURIA_ENFRIA : k;
    }

    private void tickLibre(ServerLevel nivel, @Nullable LivingEntity objetivo) {
        LivingEntity mira = caza > 0 && presa != null ? presa : objetivo;
        if (mira == null) {
            return;
        }
        if (rasante > 0 && destinoRasante != null) {
            // En la pasada mira a donde va; al acabarla se vuelve a su presa.
            girarHacia(destinoRasante, 9.0F);
            return;
        }
        girarHacia(mira.position(), 12.0F);
        if (caza > 0) {
            if (respiro <= 0) {
                // La caza: rafaga, rafaga, doble rafaga, y vuelta a empezar.
                int paso = cazaPaso++ % 3;
                if (paso < 2) {
                    ponerEstado(RAFAGA, AeralisGeometria.DURACION_RAFAGA);
                } else {
                    ponerEstado(DOBLE_RAFAGA, AeralisGeometria.DURACION_DOBLE_RAFAGA);
                }
            }
            return;
        }
        if (fase() == 4 && --relojAgotado <= 0) {
            empezarAgotada();
            return;
        }
        if (respiro <= 0 && rasante <= 0) {
            elegirAtaque(nivel, objetivo);
        }
    }

    private void elegirAtaque(ServerLevel nivel, @Nullable LivingEntity objetivo) {
        if (objetivo == null) {
            return;
        }
        int fase = fase();
        double d = horizontal(position(), objetivo.position());
        List<int[]> opciones = new ArrayList<>();
        if (enfAleteo <= 0 && d < ALCANCE_CUCHILLA - 4) opciones.add(new int[]{ALETEO, 5});
        if (enfTornados <= 0 && tornadosVivos.size() < 10) opciones.add(new int[]{TORNADOS, 4});
        LivingEntity cazable = fase >= 2 && enfCaza <= 0 ? elegirPresa(nivel) : null;
        if (cazable != null) opciones.add(new int[]{MARCA, 5});
        if (fase >= 3 && enfJuicio <= 0 && !jugadores(nivel, 56, 0).isEmpty()) opciones.add(new int[]{JUICIO_SUBE, 7});
        if (fase >= 2 && enfPicado <= 0 && d >= 12.0 && d <= 50.0) opciones.add(new int[]{PICADO_AVISO, 4});
        if (fase >= 3 && enfEscamas <= 0) opciones.add(new int[]{ESCAMAS, 3});
        if (opciones.isEmpty()) {
            return;
        }
        int total = 0;
        for (int[] o : opciones) total += o[1];
        int r = random.nextInt(total);
        int elegido = opciones.get(0)[0];
        for (int[] o : opciones) {
            r -= o[1];
            if (r < 0) {
                elegido = o[0];
                break;
            }
        }
        if (elegido == PICADO_AVISO || elegido == ESCAMAS) {
            iniciar(nivel, elegido, objetivo);
            return;
        }
        if (elegido == ALETEO) {
            List<Player> cerca = jugadores(nivel, ALCANCE_CUCHILLA - 4, 0);
            if (!cerca.isEmpty()) {
                setTarget(cerca.get(random.nextInt(cerca.size())));
            }
        }
        iniciar(nivel, elegido, cazable);
    }

    private void iniciar(ServerLevel nivel, int ataque, @Nullable LivingEntity presaElegida) {
        float k = enfriamiento();
        rasante = 0;
        switch (ataque) {
            case ALETEO -> {
                enfAleteo = (int) (70 * k);
                ponerEstado(ALETEO, AeralisGeometria.DURACION_ALETEO);
            }
            case TORNADOS -> {
                enfTornados = (int) (300 * k);
                ponerEstado(TORNADOS, AeralisGeometria.DURACION_TORNADOS);
                sonido(AtalayaSonidos.AERALIS_CHILLIDO, 4.0F);
            }
            case MARCA -> {
                if (presaElegida == null) {
                    return;
                }
                presa = presaElegida;
                entityData.set(DATA_OBJETIVO, presaElegida.getId());
                ponerEstado(MARCA, AeralisGeometria.DURACION_MARCA);
                sonido(AtalayaSonidos.AERALIS_CHILLIDO, 6.0F);
            }
            case JUICIO_SUBE -> {
                enfJuicio = (int) (900 * k);
                empezarJuicio(nivel);
            }
            case PICADO_AVISO -> {
                enfPicado = (int) (400 * k);
                blancoPicado = presaElegida != null ? presaElegida : getTarget();
                golpeadosPicado.clear();
                ponerEstado(PICADO_AVISO, AeralisGeometria.DURACION_PICADO_AVISO);
                entityData.set(DATA_PICADO, (float) PICADO_MIN);
                sonido(AtalayaSonidos.AERALIS_PICADO_AVISO, 6.0F);
            }
            case ESCAMAS -> {
                enfEscamas = (int) (500 * k);
                LivingEntity c = presaElegida != null ? presaElegida : getTarget();
                centroEscamas = c != null ? c.position() : position();
                ponerEstado(ESCAMAS, AeralisGeometria.DURACION_ESCAMAS);
                sonido(AtalayaSonidos.AERALIS_ESCAMAS, 6.0F);
            }
            default -> {
            }
        }
    }

    /**
     * Para probar y para el operador de la serie: fuerza un ataque o un momento
     * del combate. Apunta al ser vivo mas cercano que no sea ella.
     *
     * @return falso si no reconoce la orden
     */
    public boolean forzar(ServerLevel nivel, String orden) {
        LivingEntity blanco = null;
        double mejor = 72 * 72;
        for (LivingEntity v : nivel.getEntitiesOfClass(LivingEntity.class, getBoundingBox().inflate(72), this::esPresa)) {
            double d = v.distanceToSqr(this);
            if (d < mejor) {
                mejor = d;
                blanco = v;
            }
        }
        switch (orden) {
            case "despertar" -> {
                despertarse(blanco);
                return true;
            }
            case "fase" -> {
                int siguiente = Math.min(4, fase() + 1);
                if (getEstado() == DORMIDA) {
                    despertarse(blanco);
                }
                setHealth(getMaxHealth() * (1.0F - 0.25F * (siguiente - 1)) - 1.0F);
                return true;
            }
            case "liberar" -> {
                hurtServer(nivel, nivel.damageSources().genericKill(), Float.MAX_VALUE);
                return true;
            }
            case "romper" -> {
                // Rompe sus tornados como si les hubieran dado los tres golpes: su viento vuelve a ella.
                for (TornadoAeralisEntity tor : new ArrayList<>(tornadosVivos)) {
                    tor.romper(nivel);
                }
                return true;
            }
            case "viento" -> {
                // Le devuelve de golpe el viento que le falta para sacudirse, desde el suelo de alrededor.
                if (getEstado() == DORMIDA) {
                    despertarse(blanco);
                }
                int faltan = Math.max(1, vientoNecesario(Math.max(2, fase())) - getViento());
                for (int i = 0; i < faltan; i++) {
                    double a = random.nextDouble() * Math.PI * 2;
                    double r = 10.0 + random.nextDouble() * 8.0;
                    double x = getX() + Math.cos(a) * r;
                    double z = getZ() + Math.sin(a) * r;
                    vientoDeVuelta(nivel, new Vec3(x, sueloBajo(nivel, x, getY(), z), z));
                }
                return true;
            }
            case "nucleo" -> {
                // Rompe uno de los nucleos del Juicio que queden (para ver la barra).
                if (!nucleos.isEmpty()) {
                    NucleoVientoEntity n = nucleos.get(random.nextInt(nucleos.size()));
                    for (int i = 0; i < GOLPES_NUCLEO && !n.isRemoved(); i++) {
                        n.hurtServer(nivel, nivel.damageSources().generic(), 1.0F);
                    }
                }
                return true;
            }
            case "furia" -> {
                // Le pone o le quita la Furia del Vendaval (para verla sin fallar un Juicio).
                if (getEstado() == DORMIDA) {
                    despertarse(blanco);
                }
                ponerFuria(nivel, !tieneFuria());
                return true;
            }
            case "mancha" -> {
                // Una mancha de escamas bajo cada presa a 24 bloques (para ver la descarga y la Paralisis).
                for (LivingEntity v : nivel.getEntitiesOfClass(LivingEntity.class, getBoundingBox().inflate(24), this::esPresa)) {
                    double y = sueloBajo(nivel, v.getX(), v.getY() + 2, v.getZ());
                    manchas.add(new double[]{v.getX(), y, v.getZ(), 0});
                    nivel.sendParticles(AtalayaParticulas.AERALIS_CIRCULO, true, true, v.getX(), y + 0.06, v.getZ(), 0, MANCHA_RADIO,
                            MANCHA_VIDA, 0.0, 1.0);
                }
                return true;
            }
            default -> {
            }
        }
        int ataque = switch (orden) {
            case "aleteo" -> ALETEO;
            case "tornados" -> TORNADOS;
            case "caceria" -> MARCA;
            case "rafaga" -> RAFAGA;
            case "doble" -> DOBLE_RAFAGA;
            case "juicio" -> JUICIO_SUBE;
            case "aturdida" -> ATURDIDA;
            case "agotada" -> AGOTADA;
            case "picado" -> PICADO_AVISO;
            case "posada" -> POSADA;
            case "escamas" -> ESCAMAS;
            default -> -1;
        };
        if (ataque < 0) {
            return false;
        }
        if (blanco != null) {
            setTarget(blanco);
            girarHacia(blanco.position(), 180.0F);
        }
        cancelarJuicio(nivel);
        ponerEstado(LIBRE, 0);
        if (getEstado() == DORMIDA || fase() < 1) {
            entityData.set(DATA_FASE, Math.max(1, fase()));
        }
        switch (ataque) {
            case AGOTADA -> empezarAgotada();
            case POSADA -> posarse(nivel);
            case ATURDIDA -> aturdir(nivel);
            case RAFAGA, DOBLE_RAFAGA -> {
                if (blanco == null) {
                    return true;
                }
                if (caza <= 0) {
                    presa = blanco;
                    entityData.set(DATA_OBJETIVO, blanco.getId());
                    empezarCaza();
                }
                ponerEstado(ataque, ataque == RAFAGA ? AeralisGeometria.DURACION_RAFAGA : AeralisGeometria.DURACION_DOBLE_RAFAGA);
            }
            case MARCA -> {
                terminarCaza();
                iniciar(nivel, MARCA, blanco);
            }
            default -> iniciar(nivel, ataque, blanco);
        }
        return true;
    }

    // ------------------------------------------------------------------
    //  Vuelo
    // ------------------------------------------------------------------

    /**
     * A donde quiere estar este tick y hacia alli, con inercia. Rodea al grupo
     * a media distancia, se queda quieta mientras ataca, sube para el Juicio y
     * baja al suelo dormida, aturdida o agotada.
     */
    private void volar(ServerLevel nivel, @Nullable LivingEntity objetivo) {
        int e = getEstado();
        if (e == PICADO) {
            volarPicado(nivel);
            return;
        }
        double suelo = sueloBajo(nivel, getX(), getY(), getZ());
        double altura = switch (e) {
            case LIBRE -> ALTURA_VUELO + 1.0 * Mth.sin(tickCount * 0.045F);
            // Sube para golpear el aire y baja con el golpe.
            case TORNADOS -> ta() < AeralisGeometria.TORNADOS_GOLPE ? ALTURA_VUELO + 3.0 : ALTURA_VUELO - 0.8;
            case DORMIDA, ATURDIDA -> 0.0;
            case DESPERTAR -> t < AeralisGeometria.DESPERTAR_ALZA ? 0.0 : ALTURA_VUELO;
            case AGOTADA -> ta() >= AeralisGeometria.AGOTADA_ALZA ? ALTURA_VUELO : 0.0;
            case JUICIO_SUBE, JUICIO_SOSTIENE, JUICIO_GOLPE -> ALTURA_JUICIO;
            // El Picado sube antes de lanzarse; posada, en el suelo hasta que se arranca.
            case PICADO_AVISO -> ALTURA_VUELO + 4.5;
            case POSADA -> ta() >= AeralisGeometria.POSADA_ALZA ? ALTURA_VUELO : 0.0;
            case ESCAMAS -> ALTURA_VUELO + 3.0;
            default -> ALTURA_VUELO;
        };
        Vec3 c = Vec3.atBottomCenterOf(centro);
        double x = getX();
        double z = getZ();
        double vmax = 0.32;
        if (e == LIBRE) {
            LivingEntity mira = caza > 0 && presa != null ? presa : objetivo;
            // Entre ataque y ataque, de vez en cuando, una pasada rasante: cruza
            // por encima del grupo al otro lado, baja y deja el viento detras.
            if (mira != null && caza <= 0 && rasante <= 0 && --relojRasante <= 0) {
                relojRasante = 130 + random.nextInt(110) - fase() * 12;
                float lado = (float) Mth.atan2(getZ() - mira.getZ(), getX() - mira.getX()) + Mth.PI
                        + (random.nextFloat() - 0.5F) * 1.2F;
                double r = 10.0 + random.nextDouble() * 4.0;
                destinoRasante = new Vec3(mira.getX() + Math.cos(lado) * r, 0, mira.getZ() + Math.sin(lado) * r);
                rasante = 60;
            }
            if (rasante > 0 && destinoRasante != null) {
                rasante--;
                x = destinoRasante.x;
                z = destinoRasante.z;
                vmax = 0.78;
                altura = ALTURA_RASANTE;
                if (horizontal(position(), destinoRasante) < 3.0) {
                    rasante = 0;
                }
            } else if (mira != null) {
                // Da vueltas alrededor de su blanco, a 11-15 bloques, y de vez en
                // cuando cambia de sentido.
                if (random.nextInt(160) == 0) {
                    sentido = -sentido;
                }
                double radio = caza > 0 ? 9.0 : 12.0 + 3.0 * Mth.sin(tickCount * 0.02F);
                float actual = (float) Mth.atan2(getZ() - mira.getZ(), getX() - mira.getX());
                orbita = actual + sentido * 0.12F;
                x = mira.getX() + Math.cos(orbita) * radio;
                z = mira.getZ() + Math.sin(orbita) * radio;
                vmax = (fase() >= 4 ? 0.5 : 0.4) * (tieneFuria() ? FURIA_VUELA : 1.0);
                if (caza > 0 && isAcelerada()) {
                    vmax = 0.62;
                }
            } else {
                x = c.x;
                z = c.z;
            }
        } else if (e == JUICIO_SUBE || e == JUICIO_SOSTIENE || e == JUICIO_GOLPE) {
            // El Juicio se dicta desde el centro de la arena.
            x = Mth.lerp(0.5, getX(), c.x);
            z = Mth.lerp(0.5, getZ(), c.z);
            vmax = 0.2;
        } else if (e == TAMBALEO) {
            Vec3 atras = frente().scale(-0.6);
            x += atras.x;
            z += atras.z;
        }
        // La correa: no se va de la zona del combate.
        Vec3 desde = new Vec3(x - c.x, 0, z - c.z);
        if (desde.length() > CORREA) {
            desde = desde.normalize().scale(CORREA);
            x = c.x + desde.x;
            z = c.z + desde.z;
        }
        double y = suelo + altura;
        Vec3 dif = new Vec3(x - getX(), y - getY(), z - getZ());
        Vec3 quiero = new Vec3(dif.x * 0.12, 0, dif.z * 0.12);
        if (quiero.length() > vmax) {
            quiero = quiero.normalize().scale(vmax);
        }
        // Lo que el golpe hace con su cuerpo: se echa atras al cargar y se
        // lanza con el tajo, retrocede al soltar cada rafaga, la sacude el rayo.
        quiero = quiero.add(frente().scale(empuje(e)));
        // En vertical: cae de golpe al estrellarse y sube con calma.
        boolean deGolpe = (altura == 0.0 && e != DESPERTAR) || (e == TORNADOS && ta() >= AeralisGeometria.TORNADOS_GOLPE);
        double vy = Mth.clamp(dif.y * 0.15, deGolpe ? -0.9 : -0.35, 0.35);
        Vec3 v = getDeltaMovement();
        setDeltaMovement(v.x + (quiero.x - v.x) * 0.2, vy, v.z + (quiero.z - v.z) * 0.2);
    }

    /** Bloques por tick que su propio golpe le da hacia delante (negativo: hacia atras). */
    private double empuje(int e) {
        float a = ta();
        return switch (e) {
            case ALETEO -> a >= AeralisGeometria.ALETEO_CARGA && a < AeralisGeometria.ALETEO_SUELTA ? -0.12
                    : a >= AeralisGeometria.ALETEO_SUELTA && a < AeralisGeometria.ALETEO_SUELTA + 7 ? 0.7 : 0.0;
            case RAFAGA -> a >= AeralisGeometria.RAFAGA_SUELTA && a < AeralisGeometria.RAFAGA_SUELTA + 4 ? -0.35 : 0.0;
            case DOBLE_RAFAGA -> (a >= AeralisGeometria.DOBLE_SUELTA_1 && a < AeralisGeometria.DOBLE_SUELTA_1 + 3)
                    || (a >= AeralisGeometria.DOBLE_SUELTA_2 && a < AeralisGeometria.DOBLE_SUELTA_2 + 3) ? -0.3 : 0.0;
            case MARCA -> a >= AeralisGeometria.MARCA_FIJA - 2 && a < AeralisGeometria.MARCA_FIJA + 6 ? 0.3 : 0.0;
            case JUICIO_GOLPE -> a >= AeralisGeometria.JUICIO_GOLPE && a < AeralisGeometria.JUICIO_GOLPE + 5 ? 0.45 : 0.0;
            case TAMBALEO -> t < 10 ? -0.5 : 0.0;
            default -> 0.0;
        };
    }

    /** Sin rozamiento de vanilla: la velocidad la decide volar(). */
    @Override
    public void travel(Vec3 entrada) {
        move(MoverType.SELF, getDeltaMovement());
    }

    /** El cuerpo mira siempre a donde ella apunta, no a donde se desplaza. */
    @Override
    protected void tickHeadTurn(float rumboCuerpo) {
        this.yBodyRot = getYRot();
        this.yHeadRot = getYRot();
    }

    /**
     * Lo alto del primer bloque solido bajo (x, y + 2, z), buscando hasta 48
     * bloques hacia abajo. Si no hay nada (el vacio), su propia altura.
     */
    public static double sueloBajo(BlockGetter nivel, double x, double y, double z) {
        BlockPos.MutableBlockPos p = new BlockPos.MutableBlockPos(Mth.floor(x), Mth.floor(y + 2.0), Mth.floor(z));
        for (int i = 0; i < 48; i++) {
            BlockState b = nivel.getBlockState(p);
            if (!b.getCollisionShape(nivel, p).isEmpty()) {
                return p.getY() + b.getCollisionShape(nivel, p).max(Direction.Axis.Y);
            }
            p.move(0, -1, 0);
        }
        return y - ALTURA_VUELO;
    }

    // ------------------------------------------------------------------
    //  Dormida y despertar
    // ------------------------------------------------------------------

    private void tickDormida(ServerLevel nivel) {
        if (t % 5 != 0) {
            return;
        }
        for (Player p : jugadores(nivel, RANGO_DESPERTAR, 0)) {
            if (hasLineOfSight(p)) {
                despertarse(p);
                return;
            }
        }
    }

    private void despertarse(@Nullable Entity quien) {
        if (getEstado() != DORMIDA) {
            return;
        }
        if (quien instanceof LivingEntity vivo) {
            setTarget(vivo);
        }
        ponerEstado(DESPERTAR, AeralisGeometria.DURACION_DESPERTAR);
        sonido(AtalayaSonidos.AERALIS_DESPERTAR, 7.0F);
    }

    private void tickDespertar(ServerLevel nivel) {
        if (t == 1) {
            jugadoresGrupo = Math.max(1, jugadores(nivel, 80, 0).size());
            factorGrupo = VIDA_VANILLA / VIDA;
            setHealth(getMaxHealth());
            entityData.set(DATA_FASE, 1);
        }
        if (t == AeralisGeometria.DESPERTAR_ALZA) {
            // La primera batida la despega del suelo: polvo y una onda.
            golpeAire(nivel, position(), 1.6F, 12.0F, 30);
        }
        if (t == AeralisGeometria.DESPERTAR_CHILLA) {
            // El chillido empuja: aparta a quien se acerco a despertarla.
            for (Player p : jugadores(nivel, 16, 0)) {
                Vec3 fuera = horizontalHacia(position(), p.position());
                p.setDeltaMovement(fuera.x * 1.4, 0.55, fuera.z * 1.4);
                p.hurtMarked = true;
            }
            Vec3 b = puntoMundo(AeralisGeometria.BOCA);
            nivel.sendParticles(AtalayaParticulas.AERALIS_ONDA, true, true, b.x, b.y, b.z, 0, 2.6, 16.0, 0.0, 1.0);
        }
    }

    // ------------------------------------------------------------------
    //  Aleteo Cortante: un abanico de cuchillas de viento
    // ------------------------------------------------------------------

    private void tickAleteo(ServerLevel nivel, @Nullable LivingEntity objetivo) {
        if (ta() < AeralisGeometria.ALETEO_SUELTA - 2 && objetivo != null) {
            girarHacia(objetivo.position(), 14.0F);
        }
        if (cruza(AeralisGeometria.ALETEO_CARGA)) {
            sonido(AtalayaSonidos.AERALIS_ALETEO_CARGA, 4.0F);
        }
        if (!cruza(AeralisGeometria.ALETEO_SUELTA)) {
            return;
        }
        sonido(AtalayaSonidos.AERALIS_ALETEO_CORTE, 5.0F);
        // 3, una mas por cada 10 jugadores y otra en la III y en la IV.
        int n = Math.min(10, 3 + jugadoresGrupo / 10 + (fase() >= 3 ? 1 : 0) + (fase() >= 4 ? 1 : 0));
        float abre = 11.0F;
        Vec3 blanco = objetivo != null ? objetivo.position()
                : position().add(frente().scale(20)).add(0, -ALTURA_VUELO, 0);
        double ySuelo = objetivo != null ? objetivo.getY() : sueloBajo(nivel, getX(), getY(), getZ());
        double vel = 1.25 + 0.08 * (fase() - 1);
        // Salen del arco que dibujan las alas por delante (mas cerca de ella si
        // el blanco esta cerca) y cada una apunta AL BLANCO desde donde sale,
        // abierta en abanico: la del centro va derecha a el y las demas cierran
        // los lados. Bajan a su altura antes de llegar, este lejos o cerca.
        double d = horizontal(position(), blanco);
        double delante = Math.min(8.0, d * 0.4);
        for (int i = 0; i < n; i++) {
            double k = n == 1 ? 0.0 : i / (n - 1.0) * 2.0 - 1.0;
            Vec3 desde = puntoMundo(new Vec3(-k * 11.0, 7.5, delante - 3.5 * k * k));
            float base = (float) (Mth.atan2(blanco.z - desde.z, blanco.x - desde.x) * Mth.RAD_TO_DEG) - 90.0F;
            float rumbo = base + (i - (n - 1) / 2.0F) * abre;
            boolean alta = i % 2 == 1;
            double altura = ySuelo + (alta ? 1.35 : 0.35);
            double ticks = Math.max(1.0, horizontal(desde, blanco) / vel);
            double bajada = Math.max(0.25, Math.abs(desde.y - altura) / Math.max(2.0, ticks * 0.6));
            CuchillaVientoEntity.lanzar(nivel, this, desde, rumbo, altura, bajada, vel, dano(DANO_CUCHILLA), alta);
        }
        for (Vec3 punta : new Vec3[]{AeralisGeometria.PUNTA_ALA_IZQ_ALETEO, AeralisGeometria.PUNTA_ALA_DER_ALETEO}) {
            Vec3 p = puntoMundo(punta);
            nivel.sendParticles(AtalayaParticulas.AERALIS_JIRON, true, true, p.x, p.y, p.z, 8, 0.8, 0.8, 0.8, 0.08);
        }
        Vec3 f = frente();
        Vec3 b = puntoMundo(AeralisGeometria.NUCLEO);
        nivel.sendParticles(AtalayaParticulas.AERALIS_ONDA, true, true, b.x + f.x * 3, b.y, b.z + f.z * 3, 0, 1.2, 9.0, 0.0, 1.0);
    }

    // ------------------------------------------------------------------
    //  Tornados: golpea el aire contra el suelo y nacen remolinos que vagan
    // ------------------------------------------------------------------

    private void tickTornados(ServerLevel nivel, @Nullable LivingEntity objetivo) {
        if (ta() < AeralisGeometria.TORNADOS_GOLPE && objetivo != null) {
            girarHacia(objetivo.position(), 10.0F);
        }
        if (!cruza(AeralisGeometria.TORNADOS_GOLPE)) {
            return;
        }
        sonido(AtalayaSonidos.AERALIS_TORNADOS_GOLPE, 5.0F);
        Vec3 bajo = new Vec3(getX(), sueloBajo(nivel, getX(), getY(), getZ()), getZ());
        golpeAire(nivel, bajo, 2.2F, 16.0F, 40);
        // 3, uno mas por cada 8 jugadores (hasta 8) y otro en la IV. Nacen junto
        // a los jugadores, repartidos, y avisan un segundo con el polvo.
        int n = Math.min(8, 3 + jugadoresGrupo / 8) + (fase() >= 4 ? 1 : 0);
        List<Player> ps = jugadores(nivel, 52, 0);
        Vec3 c = Vec3.atBottomCenterOf(centro);
        for (int i = 0; i < n; i++) {
            double a = random.nextDouble() * Math.PI * 2;
            Vec3 p;
            if (!ps.isEmpty()) {
                Player pl = ps.get(i % ps.size());
                double d = 5.0 + random.nextDouble() * 5.0;
                p = new Vec3(pl.getX() + Math.cos(a) * d, pl.getY(), pl.getZ() + Math.sin(a) * d);
            } else {
                double d = 6.0 + random.nextDouble() * 14.0;
                p = new Vec3(getX() + Math.cos(a) * d, getY(), getZ() + Math.sin(a) * d);
            }
            Vec3 rel = new Vec3(p.x - c.x, 0, p.z - c.z);
            if (rel.length() > CORREA + 10) {
                rel = rel.normalize().scale(CORREA + 10);
                p = new Vec3(c.x + rel.x, p.y, c.z + rel.z);
            }
            double y = sueloBajo(nivel, p.x, p.y + 4, p.z);
            tornadosVivos.add(TornadoAeralisEntity.nacer(nivel, this, new Vec3(p.x, y, p.z), fase()));
        }
    }

    // ------------------------------------------------------------------
    //  La Caceria del Vendaval
    // ------------------------------------------------------------------

    /** La presa: un jugador a la vista, al azar (el que mas lejos este, a veces). */
    private @Nullable LivingEntity elegirPresa(ServerLevel nivel) {
        List<Player> vistos = new ArrayList<>();
        for (Player p : jugadores(nivel, 44, 0)) {
            if (hasLineOfSight(p)) {
                vistos.add(p);
            }
        }
        return vistos.isEmpty() ? null : vistos.get(random.nextInt(vistos.size()));
    }

    private void tickMarca(ServerLevel nivel) {
        if (!presaValida()) {
            terminarCaza();
            terminar();
            return;
        }
        girarHacia(presa.position(), 14.0F);
        if (ta() < AeralisGeometria.MARCA_FIJA) {
            // Las antenas se tensan hacia ella: una columna de runas la senala.
            if (t % 3 == 0) {
                nivel.sendParticles(AtalayaParticulas.AERALIS_MARCA, true, true, presa.getX(), presa.getY() + 0.2, presa.getZ(),
                        2, 0.3, 1.2, 0.3, 0.02);
            }
            return;
        }
        if (cruza(AeralisGeometria.MARCA_FIJA)) {
            sonido(AtalayaSonidos.AERALIS_MARCA, 5.0F);
            nivel.playSound(null, presa.getX(), presa.getY(), presa.getZ(), AtalayaSonidos.AERALIS_MARCA,
                    SoundSource.HOSTILE, 1.5F, 1.2F);
            for (int i = 0; i < 12; i++) {
                nivel.sendParticles(AtalayaParticulas.AERALIS_MARCA, true, true, presa.getX(), presa.getY() + i * 0.6, presa.getZ(),
                        2, 0.25, 0.1, 0.25, 0.02);
            }
            nivel.sendParticles(AtalayaParticulas.AERALIS_CIRCULO, true, true, presa.getX(), presa.getY() + 0.06, presa.getZ(),
                    0, 2.2, 50.0, 0.0, 1.0);
            empezarCaza();
        }
    }

    private void empezarCaza() {
        caza = CAZA;
        cazaPaso = 0;
        enfCaza = (int) (640 * enfriamiento());
        if (presa != null) {
            marcar(presa, CAZA);
        }
    }

    /** Cada tick de la caza: la marca no se quita y, si se aleja del grupo, acelera. */
    private void tickCaza(ServerLevel nivel) {
        caza--;
        if (!presaValida()) {
            terminarCaza();
            return;
        }
        if (t % 10 == 0 && !presa.hasEffect(MarcaVendavalEffect.MARCA)) {
            marcar(presa, caza);
        }
        if (t % 10 == 0) {
            double lejos = Double.MAX_VALUE;
            boolean hayGrupo = false;
            for (Player p : jugadores(nivel, 80, 0)) {
                if (p != presa) {
                    hayGrupo = true;
                    lejos = Math.min(lejos, p.distanceTo(presa));
                }
            }
            entityData.set(DATA_ACELERADA, hayGrupo && lejos > LEJOS_DEL_GRUPO);
        }
        if (caza <= 0) {
            terminarCaza();
        }
    }

    private void terminarCaza() {
        if (presa != null && getEstado() != JUICIO_SOSTIENE && getEstado() != JUICIO_GOLPE) {
            presa.removeEffect(MarcaVendavalEffect.MARCA);
        }
        caza = 0;
        entityData.set(DATA_ACELERADA, false);
        if (getEstado() != JUICIO_SOSTIENE && getEstado() != JUICIO_GOLPE) {
            presa = null;
            entityData.set(DATA_OBJETIVO, -1);
        }
    }

    private void marcar(LivingEntity v, int ticks) {
        v.addEffect(new MobEffectInstance(MarcaVendavalEffect.MARCA, Math.max(20, ticks), 0, false, true, true), this);
    }

    private boolean presaValida() {
        return presa != null && presa.isAlive() && !presa.isRemoved() && presa.distanceToSqr(this) < 80 * 80
                && !(presa instanceof Player p && (p.isCreative() || p.isSpectator()));
    }

    private void tickRafaga(ServerLevel nivel, boolean doble) {
        if (!presaValida()) {
            terminarCaza();
            terminar();
            return;
        }
        girarHacia(presa.position(), 16.0F);
        boolean suelta = doble
                ? cruza(AeralisGeometria.DOBLE_SUELTA_1) || cruza(AeralisGeometria.DOBLE_SUELTA_2)
                : cruza(AeralisGeometria.RAFAGA_SUELTA);
        if (!suelta) {
            return;
        }
        Vec3 f = frente();
        Vec3 desde = puntoMundo(AeralisGeometria.NUCLEO).add(f.scale(2.5));
        // Cuantos golpes aguanta en el aire: uno, y uno mas por cada 12 jugadores.
        int aguanta = 1 + jugadoresGrupo / 12;
        RafagaAeralisEntity.lanzar(nivel, this, desde, presa, fase(), isAcelerada(), aguanta, dano(DANO_RAFAGA));
        sonido(AtalayaSonidos.AERALIS_RAFAGA, 4.0F);
        nivel.sendParticles(AtalayaParticulas.AERALIS_JIRON, true, true, desde.x, desde.y, desde.z, 10, 0.6, 0.6, 0.6, 0.05);
    }

    // ------------------------------------------------------------------
    //  Juicio del Ciclon
    // ------------------------------------------------------------------

    private void empezarJuicio(ServerLevel nivel) {
        terminarCaza();
        nucleosRotos = 0;
        entityData.set(DATA_NUCLEOS, 0);
        ponerEstado(JUICIO_SUBE, AeralisGeometria.DURACION_JUICIO_SUBE);
        // El silencio: el viento de toda la arena se calla. Los tornados se
        // deshacen, las rafagas se apagan y a todos se les corta el viento.
        for (TornadoAeralisEntity tor : tornadosVivos) {
            tor.deshacer(false);
        }
        tornadosVivos.clear();
        for (RafagaAeralisEntity r : nivel.getEntitiesOfClass(RafagaAeralisEntity.class, getBoundingBox().inflate(80))) {
            r.discard();
        }
        for (SoundEvent s : new SoundEvent[]{AtalayaSonidos.AERALIS_AMBIENTE, AtalayaSonidos.AERALIS_TORNADO,
                AtalayaSonidos.AERALIS_TRUENO, AtalayaSonidos.AERALIS_ALETEO}) {
            cortarSonido(nivel, s);
        }
        sonido(AtalayaSonidos.AERALIS_JUICIO_SILENCIO, 8.0F);
    }

    private void tickJuicioSube(ServerLevel nivel) {
        if (t == duracion - 6) {
            // Aparece el circulo enorme bajo todos, y uno pequeno bajo cada uno.
            Vec3 c = Vec3.atBottomCenterOf(centro);
            double radio = 10.0;
            for (Player p : jugadores(nivel, 64, 0)) {
                radio = Math.max(radio, horizontal(c, p.position()) + 6.0);
                nivel.sendParticles(AtalayaParticulas.AERALIS_CIRCULO, true, true, p.getX(), p.getY() + 0.06, p.getZ(),
                        0, 3.2, 90.0, 0.0, 1.0);
            }
            radio = Math.min(radio, 56.0);
            double y = sueloBajo(nivel, c.x, c.y + 4, c.z);
            nivel.sendParticles(AtalayaParticulas.AERALIS_CIRCULO, true, true, c.x, y + 0.05, c.z, 0, radio, JUICIO_TICKS + 60, 0.0, 1.0);
            sonido(AtalayaSonidos.AERALIS_JUICIO_CIRCULO, 8.0F);
        }
    }

    /** Elige al que menos vida tiene y levanta el ciclon a su alrededor. */
    private void empezarCiclon(ServerLevel nivel) {
        // Atrapa a un tercio de los que pelean (redondeando hacia arriba: 30
        // jugadores, 10; 4, 2; uno solo, 1): los de menos vida, todos en el mismo
        // ciclon. Sin jugadores a tiro (maniquies de pruebas, otros bichos), las
        // presas de alrededor.
        List<LivingEntity> candidatos = new ArrayList<>(jugadores(nivel, 60, 0));
        if (candidatos.isEmpty()) {
            candidatos.addAll(nivel.getEntitiesOfClass(LivingEntity.class, getBoundingBox().inflate(60, 24, 60), this::esPresa));
        }
        if (candidatos.isEmpty()) {
            terminar();
            return;
        }
        candidatos.sort(Comparator.comparingDouble(LivingEntity::getHealth));
        juzgados.clear();
        juzgados.addAll(candidatos.subList(0, (candidatos.size() + 2) / 3));
        presa = juzgados.get(0);
        entityData.set(DATA_OBJETIVO, presa.getId());
        for (LivingEntity v : juzgados) {
            marcar(v, JUICIO_TICKS + 60);
        }
        ponerEstado(JUICIO_SOSTIENE, JUICIO_TICKS);
        sonido(AtalayaSonidos.AERALIS_CHILLIDO, 7.0F);
        sonido(AtalayaSonidos.AERALIS_JUICIO_CICLON, 7.0F);
        ciclon = TornadoAeralisEntity.ciclon(nivel, this, juzgados);
        // Los cuatro nucleos, repartidos por la arena alrededor de su centro.
        Vec3 c = Vec3.atBottomCenterOf(centro);
        float giro = random.nextFloat() * Mth.TWO_PI;
        nucleos.clear();
        for (int i = 0; i < 4; i++) {
            double a = giro + i * Math.PI / 2 + (random.nextDouble() - 0.5) * 0.5;
            double d = 15.0 + random.nextDouble() * 6.0;
            double x = c.x + Math.cos(a) * d;
            double z = c.z + Math.sin(a) * d;
            double y = sueloBajo(nivel, x, c.y + 6, z) + 2.2;
            nucleosJuicio[i] = NucleoVientoEntity.crear(nivel, this, new Vec3(x, y, z), GOLPES_NUCLEO);
            nucleos.add(nucleosJuicio[i]);
        }
    }

    private void tickJuicioSostiene(ServerLevel nivel) {
        juzgados.removeIf(v -> !v.isAlive() || v.isRemoved());
        if (juzgados.isEmpty()) {
            cancelarJuicio(nivel);
            terminar();
            return;
        }
        if (presa != juzgados.get(0)) {
            presa = juzgados.get(0);
            entityData.set(DATA_OBJETIVO, presa.getId());
        }
        girarHacia(ciclon != null ? ciclon.position() : presa.position(), 4.0F);
        if (t % 110 == 0) {
            sonido(AtalayaSonidos.AERALIS_JUICIO_CICLON, 7.0F);
        }
        if (t % 20 == 0) {
            for (LivingEntity v : juzgados) {
                if (!v.hasEffect(MarcaVendavalEffect.MARCA)) {
                    marcar(v, duracion - t + 40);
                }
            }
        }
    }

    /** Un nucleo de viento roto: el ciclon se debilita. Con los cuatro, se deshace. */
    public void alRomperNucleo(ServerLevel nivel, NucleoVientoEntity n) {
        nucleos.remove(n);
        if (getEstado() != JUICIO_SOSTIENE) {
            return;
        }
        nucleosRotos++;
        for (int i = 0; i < nucleosJuicio.length; i++) {
            if (nucleosJuicio[i] == n) {
                entityData.set(DATA_NUCLEOS, getNucleosRotos() | (1 << i));
            }
        }
        if (ciclon != null && !ciclon.isRemoved()) {
            ciclon.debilitar(nucleosRotos);
        }
        if (nucleosRotos >= 4) {
            // Los cuatro: el ciclon se deshace y ella cae aturdida.
            if (ciclon != null) {
                ciclon.deshacer(true);
                ciclon = null;
            }
            soltarJuzgados();
            aturdir(nivel);
            sonido(AtalayaSonidos.AERALIS_CHILLIDO, 6.0F);
        }
    }

    private void tickJuicioGolpe(ServerLevel nivel) {
        if (!cruza(AeralisGeometria.JUICIO_GOLPE)) {
            return;
        }
        // La explosion de presion donde este el primero de los juzgados (lanzados al cielo).
        Vec3 p = presa != null && presa.isAlive() ? presa.position().add(0, 1, 0)
                : (ciclon != null ? ciclon.position().add(0, 6, 0) : puntoMundo(AeralisGeometria.NUCLEO_JUICIO));
        // No han roto los cuatro nucleos: a cada juzgado, la muerte (salvo totem); a
        // los de alrededor, la mitad del golpe (menos por cada nucleo roto).
        float dano = dano(DANO_JUICIO) * Math.max(0.0F, 1.0F - JUICIO_POR_NUCLEO * nucleosRotos);
        DamageSource fuente = AeralisDanos.fuente(nivel, AeralisDanos.JUICIO, this, this);
        for (LivingEntity v : juzgados) {
            if (v.isAlive()) {
                v.hurtServer(nivel, fuente, MORTAL);
                nivel.sendParticles(AtalayaParticulas.AERALIS_RAYO, true, true, v.getX(), v.getY() + 1, v.getZ(), 3, 0.6, 0.8, 0.6, 0.0);
                nivel.sendParticles(AtalayaParticulas.AERALIS_LUZ, true, true, v.getX(), v.getY() + 1, v.getZ(), 10, 0.5, 0.6, 0.5, 0.2);
            }
        }
        for (LivingEntity v : nivel.getEntitiesOfClass(LivingEntity.class, new AABB(p, p).inflate(8), this::esPresa)) {
            if (!juzgados.contains(v) && v.distanceToSqr(p) < 64 && dano > 0) {
                v.hurtServer(nivel, fuente, dano * 0.5F);
                Vec3 fuera = horizontalHacia(p, v.position());
                v.setDeltaMovement(fuera.x * 1.3, 0.5, fuera.z * 1.3);
                v.hurtMarked = true;
            }
        }
        nivel.sendParticles(AtalayaParticulas.AERALIS_ONDA, true, true, p.x, p.y, p.z, 0, 3.2, 20.0, 0.0, 1.0);
        nivel.sendParticles(AtalayaParticulas.AERALIS_JIRON, true, true, p.x, p.y, p.z, 40, 2.0, 2.0, 2.0, 0.25);
        nivel.sendParticles(AtalayaParticulas.AERALIS_LUZ, true, true, p.x, p.y, p.z, 30, 1.5, 1.5, 1.5, 0.3);
        nivel.sendParticles(AtalayaParticulas.AERALIS_RAYO, true, true, p.x, p.y, p.z, 8, 2.0, 2.0, 2.0, 0.0);
        rayoDelCielo(nivel, p);
        double ys = sueloBajo(nivel, p.x, p.y, p.z);
        nivel.sendParticles(AtalayaParticulas.AERALIS_ONDA, true, true, p.x, ys + 0.1, p.z, 0, 2.0, 18.0, 0.0, 1.0);
        cancelarJuicio(nivel);
        // Y a los que queden se la encuentran con la Furia.
        ponerFuria(nivel, true);
    }

    /** Cae aturdida 5 s (dano doble). La han derribado: si tenia la Furia, se le va. */
    private void aturdir(ServerLevel nivel) {
        aturdidaPendiente = false;
        entityData.set(DATA_PICADO, 0.0F);
        ponerEstado(ATURDIDA, AeralisGeometria.DURACION_ATURDIDA);
        sonido(AtalayaSonidos.AERALIS_ATURDIDA, 6.0F);
        ponerFuria(nivel, false);
    }

    /** La Furia del Vendaval: el aura de rayos (con su chillido y un rayo al prenderse) o se le apaga. */
    private void ponerFuria(ServerLevel nivel, boolean si) {
        if (tieneFuria() == si) {
            return;
        }
        entityData.set(DATA_FURIA, si);
        Vec3 c = puntoMundo(AeralisGeometria.NUCLEO);
        if (si) {
            sonido(AtalayaSonidos.AERALIS_CHILLIDO, 8.0F);
            sonido(AtalayaSonidos.AERALIS_TRUENO, 8.0F);
            rayoDelCielo(nivel, c);
            nivel.sendParticles(AtalayaParticulas.AERALIS_RAYO, true, true, c.x, c.y, c.z, 20, 6.0, 4.0, 6.0, 0.0);
            nivel.sendParticles(AtalayaParticulas.AERALIS_LUZ, true, true, c.x, c.y, c.z, 60, 3.0, 3.0, 3.0, 0.2);
            nivel.sendParticles(AtalayaParticulas.AERALIS_ONDA, true, true, getX(), sueloBajo(nivel, getX(), getY(), getZ()) + 0.1,
                    getZ(), 0, 2.4, 24.0, 0.0, 1.0);
        } else {
            nivel.sendParticles(AtalayaParticulas.AERALIS_ESCAMA, true, true, c.x, c.y, c.z, 40, 4.0, 2.0, 4.0, 0.05);
        }
    }

    /** Quita el ciclon, los nucleos y la marca del Juicio. */
    private void cancelarJuicio(ServerLevel nivel) {
        if (ciclon != null) {
            ciclon.deshacer(true);
            ciclon = null;
        }
        for (NucleoVientoEntity n : nucleos) {
            n.apagar();
        }
        nucleos.clear();
        int e = getEstado();
        if (e == JUICIO_SOSTIENE || e == JUICIO_GOLPE) {
            soltarJuzgados();
        }
    }

    /** Les quita la marca del Juicio a los juzgados y los olvida. */
    private void soltarJuzgados() {
        for (LivingEntity v : juzgados) {
            v.removeEffect(MarcaVendavalEffect.MARCA);
        }
        juzgados.clear();
        presa = null;
        entityData.set(DATA_OBJETIVO, -1);
    }

    // ------------------------------------------------------------------
    //  Aturdida, agotada y los cambios de fase
    // ------------------------------------------------------------------

    private void tickAturdida(ServerLevel nivel) {
        if (t == 14) {
            golpeAire(nivel, new Vec3(getX(), sueloBajo(nivel, getX(), getY(), getZ()), getZ()), 2.4F, 12.0F, 40);
        }
        if (t % 6 == 0) {
            Vec3 c = puntoMundo(AeralisGeometria.CABEZA);
            nivel.sendParticles(AtalayaParticulas.AERALIS_RAYO, true, true, c.x, c.y, c.z, 1, 1.2, 0.6, 1.2, 0.0);
            nivel.sendParticles(AtalayaParticulas.AERALIS_ESCAMA, true, true, c.x, c.y, c.z, 2, 2.0, 1.0, 2.0, 0.02);
        }
    }

    // ------------------------------------------------------------------
    //  El Picado del Vendaval: sube y marca en el suelo una linea de galones
    //  hacia su presa; se lanza por ella con las alas plegadas, lanzando por
    //  los aires a quien pille; al final se estrella y se posa 3 s (dano doble)
    // ------------------------------------------------------------------

    private void tickPicadoAviso(ServerLevel nivel) {
        LivingEntity b = blancoPicado;
        if (b != null && b.isAlive() && ta() < AeralisGeometria.DURACION_PICADO_AVISO - 4) {
            girarHacia(b.position(), 10.0F);
            double d = horizontal(position(), b.position());
            entityData.set(DATA_PICADO, (float) Mth.clamp(d + PICADO_PASA, PICADO_MIN, PICADO_MAX));
        }
    }

    private void empezarPicado(ServerLevel nivel) {
        dirPicado = frente();
        largoPicado = Math.max(PICADO_MIN, getPicado());
        recorridoPicado = 0.0;
        golpeadosPicado.clear();
        ponerEstado(PICADO, (int) Math.ceil(largoPicado / VEL_PICADO) + 6);
        sonido(AtalayaSonidos.AERALIS_PICADO, 7.0F);
        sonido(AtalayaSonidos.AERALIS_CHILLIDO, 5.0F);
    }

    /** En picado: por la linea, a 45 bloques/s; baja en el primer tercio y despues barre el suelo. */
    private void volarPicado(ServerLevel nivel) {
        double ras = sueloBajo(nivel, getX(), getY(), getZ()) + PICADO_RAS;
        double bajada = largoPicado * PICADO_BAJA;
        double vy;
        if (recorridoPicado < bajada) {
            double queda = Math.max(VEL_PICADO, bajada - recorridoPicado);
            vy = -Math.max(0.0, getY() - ras) / Math.max(1.0, queda / VEL_PICADO);
        } else {
            vy = (ras - getY()) * 0.5;
        }
        setDeltaMovement(dirPicado.x * VEL_PICADO, vy, dirPicado.z * VEL_PICADO);
    }

    private void tickPicado(ServerLevel nivel) {
        recorridoPicado += VEL_PICADO;
        entityData.set(DATA_PICADO, (float) Math.max(0.0, largoPicado - recorridoPicado));
        fijarRumbo(getYRot());
        // Lo que pilla: lo que este en la linea (de lado, lo que mide la linea), de
        // su cola a un poco por delante, y de los pies a lo alto de su cuerpo.
        DamageSource fuente = AeralisDanos.fuente(nivel, AeralisDanos.PICADO, this, this);
        Vec3 lado = new Vec3(dirPicado.z, 0, -dirPicado.x);
        for (LivingEntity v : nivel.getEntitiesOfClass(LivingEntity.class, getBoundingBox().inflate(8.0, 4.0, 8.0), this::esPresa)) {
            Vec3 d = v.position().subtract(position());
            double largo = d.x * dirPicado.x + d.z * dirPicado.z;
            double ancho = Math.abs(d.x * lado.x + d.z * lado.z);
            if (golpeadosPicado.contains(v.getId()) || largo < -4.0 || largo > 5.0
                    || ancho > PICADO_LADO + v.getBbWidth() * 0.5 || d.y < -4.0 || d.y > 9.0) {
                continue;
            }
            golpeadosPicado.add(v.getId());
            // La muerte, salvo totem; y al cielo: la caida cuenta desde arriba del todo.
            v.hurtServer(nivel, fuente, MORTAL);
            v.resetFallDistance();
            v.setDeltaMovement(dirPicado.x * 0.6, PICADO_LANZA, dirPicado.z * 0.6);
            v.hurtMarked = true;
            nivel.sendParticles(AtalayaParticulas.AERALIS_JIRON, true, true, v.getX(), v.getY() + 1, v.getZ(), 10, 0.4, 0.6, 0.4, 0.15);
        }
        if (recorridoPicado >= largoPicado) {
            posarse(nivel);
        }
    }

    /** Se estrella al final de la linea y se queda posada, jadeando: la ventana de la espada. */
    private void posarse(ServerLevel nivel) {
        entityData.set(DATA_PICADO, 0.0F);
        ponerEstado(POSADA, AeralisGeometria.DURACION_POSADA);
        setDeltaMovement(Vec3.ZERO);
        double suelo = sueloBajo(nivel, getX(), getY(), getZ());
        Vec3 bajo = new Vec3(getX(), suelo, getZ());
        sonido(AtalayaSonidos.AERALIS_POSADA, 7.0F);
        golpeAire(nivel, bajo, 2.8F, 14.0F, 60);
        nivel.sendParticles(AtalayaParticulas.AERALIS_CIRCULO, true, true, bajo.x, bajo.y + 0.06, bajo.z, 0, 9.0,
                AeralisGeometria.DURACION_POSADA - 4, 0.0, 1.0);
        // El aire del golpe aparta a los que estan encima, sin dano.
        for (LivingEntity v : nivel.getEntitiesOfClass(LivingEntity.class, getBoundingBox().inflate(6.0, 3.0, 6.0), this::esPresa)) {
            Vec3 fuera = horizontalHacia(position(), v.position());
            v.setDeltaMovement(fuera.x * 0.9, 0.35, fuera.z * 0.9);
            v.hurtMarked = true;
        }
    }

    private void tickPosada(ServerLevel nivel) {
        fijarRumbo(yBodyRot);
        if (t % 16 == 8 && ta() < AeralisGeometria.POSADA_ALZA) {
            sonido(AtalayaSonidos.AERALIS_JADEO, 3.0F);
            Vec3 c = puntoMundo(AeralisGeometria.NUCLEO_POSADA);
            nivel.sendParticles(AtalayaParticulas.AERALIS_LUZ, true, true, c.x, c.y, c.z, 4, 0.4, 0.4, 0.4, 0.02);
        }
    }

    // ------------------------------------------------------------------
    //  Escamas de Tormenta: sacude las alas sobre el grupo; caen escamas que
    //  brillan y, donde se posan, el suelo se carga y descarga rayos
    // ------------------------------------------------------------------

    private void tickEscamas(ServerLevel nivel, @Nullable LivingEntity objetivo) {
        if (objetivo != null) {
            girarHacia(objetivo.position(), 6.0F);
        }
        float a = ta();
        if (a < AeralisGeometria.ESCAMAS_SUELTA || a >= AeralisGeometria.ESCAMAS_ACABA) {
            return;
        }
        Vec3 c = centroEscamas != null ? centroEscamas : position();
        double alto = getY() + 6.0;
        // La nube que cae.
        for (int i = 0; i < 6; i++) {
            double an = random.nextDouble() * Math.PI * 2;
            double r = Math.sqrt(random.nextDouble()) * ESCAMAS_RADIO;
            nivel.sendParticles(AtalayaParticulas.AERALIS_ESCAMA, true, true, c.x + Math.cos(an) * r, alto + random.nextDouble() * 3,
                    c.z + Math.sin(an) * r, 1, 0.3, 0.3, 0.3, 0.0);
        }
        // Las manchas: una cada 3 ticks, y algunas justo bajo los jugadores.
        if (t % 3 == 0 && manchas.size() < 18) {
            Vec3 p;
            List<Player> ps = jugadores(nivel, 40, 0);
            if (!ps.isEmpty() && random.nextInt(3) == 0) {
                Player pl = ps.get(random.nextInt(ps.size()));
                p = pl.position().add(random.nextGaussian() * 1.5, 0, random.nextGaussian() * 1.5);
            } else {
                double an = random.nextDouble() * Math.PI * 2;
                double r = Math.sqrt(random.nextDouble()) * ESCAMAS_RADIO;
                p = new Vec3(c.x + Math.cos(an) * r, c.y, c.z + Math.sin(an) * r);
            }
            double y = sueloBajo(nivel, p.x, p.y + 4, p.z);
            manchas.add(new double[]{p.x, y, p.z, 0});
            nivel.sendParticles(AtalayaParticulas.AERALIS_CIRCULO, true, true, p.x, y + 0.06, p.z, 0, MANCHA_RADIO, MANCHA_VIDA, 0.0, 1.0);
        }
    }

    /** Las manchas se cargan 1 s y descargan cada 1,5 s mientras duran (6 s). */
    private void tickManchas(ServerLevel nivel) {
        if (manchas.isEmpty()) {
            return;
        }
        DamageSource fuente = AeralisDanos.fuente(nivel, AeralisDanos.ESCAMAS, this, this);
        float dano = dano(DANO_ESCAMAS);
        paralizados.values().removeIf(desde -> tickCount - desde > PARALISIS_RESPIRO);
        for (double[] m : manchas) {
            int edad = (int) ++m[3];
            if (edad < MANCHA_CARGA) {
                if (edad % 4 == 0) {
                    nivel.sendParticles(AtalayaParticulas.AERALIS_LUZ, true, true, m[0], m[1] + 0.2, m[2], 2, 1.2, 0.1, 1.2, 0.01);
                }
                continue;
            }
            if ((edad - MANCHA_CARGA) % MANCHA_CADA != 0) {
                continue;
            }
            for (int k = 0; k < 5; k++) {
                nivel.sendParticles(AtalayaParticulas.AERALIS_RAYO, true, true, m[0] + random.nextGaussian() * 0.8, m[1] + 0.4 + k * 0.5,
                        m[2] + random.nextGaussian() * 0.8, 1, 0.2, 0.2, 0.2, 0.0);
            }
            nivel.playSound(null, m[0], m[1], m[2], AtalayaSonidos.AERALIS_ESCAMAS_DESCARGA, SoundSource.HOSTILE, 1.6F,
                    0.9F + random.nextFloat() * 0.3F);
            AABB caja = new AABB(m[0] - MANCHA_RADIO, m[1] - 1.0, m[2] - MANCHA_RADIO, m[0] + MANCHA_RADIO, m[1] + 3.0, m[2] + MANCHA_RADIO);
            for (LivingEntity v : nivel.getEntitiesOfClass(LivingEntity.class, caja, this::esPresa)) {
                if (Math.hypot(v.getX() - m[0], v.getZ() - m[2]) > MANCHA_RADIO + v.getBbWidth() * 0.5) {
                    continue;
                }
                v.hurtServer(nivel, fuente, contraArmadura(v, dano));
                paralizar(v);
            }
        }
        manchas.removeIf(m -> m[3] > MANCHA_VIDA);
    }

    /**
     * La descarga paraliza 2 s: ni andar ni saltar (pegar, el inventario y los
     * objetos, si). Al que se acaba de soltar no lo vuelve a clavar hasta
     * pasado 1 s, para que pueda salir de la mancha.
     */
    private void paralizar(LivingEntity v) {
        Integer antes = paralizados.get(v.getId());
        if (antes != null && tickCount - antes < PARALISIS_RESPIRO) {
            return;
        }
        paralizados.put(v.getId(), tickCount);
        v.addEffect(new MobEffectInstance(ParalisisEffect.PARALISIS, PARALISIS_ESCAMAS, 0, false, true, true), this);
        Vec3 m = v.getDeltaMovement();
        v.setDeltaMovement(0, Math.min(0, m.y), 0);
        v.hurtMarked = true;
    }

    // ------------------------------------------------------------------
    //  El viento de vuelta: cada tornado roto (desde la fase II) le devuelve
    //  su viento, un orbe que vuela a su pecho. Al llenarse la raya fina bajo
    //  su barra (10, 20 o 30 segun la fase), cae aturdida 5 s
    // ------------------------------------------------------------------

    /** Un tornado suyo roto a golpes: su viento vuelve a ella (desde la fase II). */
    public void vientoDeVuelta(ServerLevel nivel, Vec3 desde) {
        if (fase() < 2 || isDeadOrDying()) {
            return;
        }
        vientos.add(new double[]{desde.x, desde.y + 2.5, desde.z, 0});
        nivel.playSound(null, desde.x, desde.y, desde.z, AtalayaSonidos.AERALIS_VIENTO_VUELTA, SoundSource.HOSTILE, 2.0F,
                0.9F + random.nextFloat() * 0.2F);
    }

    private void tickVientos(ServerLevel nivel) {
        if (vientos.isEmpty()) {
            return;
        }
        Vec3 pecho = puntoMundo(AeralisGeometria.NUCLEO);
        java.util.Iterator<double[]> it = vientos.iterator();
        while (it.hasNext()) {
            double[] o = it.next();
            Vec3 p = new Vec3(o[0], o[1], o[2]);
            Vec3 falta = pecho.subtract(p);
            double d = falta.length();
            // Sale despacio y acelera hacia ella.
            double paso = Math.min(d, VEL_VIENTO * Math.min(1.0, 0.35 + o[3] * 0.05));
            if (d > 1.0E-4) {
                p = p.add(falta.scale(paso / d));
            }
            o[0] = p.x;
            o[1] = p.y;
            o[2] = p.z;
            o[3]++;
            nivel.sendParticles(AtalayaParticulas.AERALIS_LUZ, true, true, p.x, p.y, p.z, 2, 0.15, 0.15, 0.15, 0.0);
            if (o[3] % 2 == 0) {
                nivel.sendParticles(AtalayaParticulas.AERALIS_JIRON, true, true, p.x, p.y, p.z, 1, 0.1, 0.1, 0.1, 0.02);
            }
            if (d - paso > 1.2 && o[3] <= 200) {
                continue;
            }
            it.remove();
            nivel.sendParticles(AtalayaParticulas.AERALIS_LUZ, true, true, pecho.x, pecho.y, pecho.z, 8, 0.5, 0.5, 0.5, 0.08);
            if (fase() >= 2 && !isDeadOrDying()) {
                int n = getViento() + 1;
                if (n >= vientoNecesario(fase())) {
                    n = 0;
                    aturdidaPendiente = true;
                }
                entityData.set(DATA_VIENTO, n);
            }
        }
    }

    /** Se le puede cortar lo que hace para aturdirla: volando o atacando; no en el Juicio, el suelo, el Picado ni la Marca. */
    private static boolean aturdible(int e) {
        return e == LIBRE || e == ALETEO || e == TORNADOS || e == RAFAGA || e == DOBLE_RAFAGA || e == PICADO_AVISO
                || e == ESCAMAS;
    }

    private void empezarAgotada() {
        relojAgotado = CADA_AGOTADA;
        ponerEstado(AGOTADA, AeralisGeometria.DURACION_AGOTADA);
        sonido(AtalayaSonidos.AERALIS_AGOTADA, 5.0F);
    }

    private void tickAgotada(ServerLevel nivel) {
        fijarRumbo(yBodyRot);
        if (cruza(AeralisGeometria.AGOTADA_CAE + 6)) {
            golpeAire(nivel, new Vec3(getX(), sueloBajo(nivel, getX(), getY(), getZ()), getZ()), 2.6F, 13.0F, 50);
        }
        if (t % 30 == 15 && ta() < AeralisGeometria.AGOTADA_ALZA) {
            sonido(AtalayaSonidos.AERALIS_JADEO, 3.0F);
            Vec3 c = puntoMundo(AeralisGeometria.NUCLEO);
            nivel.sendParticles(AtalayaParticulas.AERALIS_LUZ, true, true, c.x, c.y, c.z, 4, 0.4, 0.4, 0.4, 0.02);
        }
    }

    private void tickTambaleo(ServerLevel nivel) {
        if (t == 16) {
            sonido(AtalayaSonidos.AERALIS_CHILLIDO, 7.0F);
        }
    }

    /**
     * Pasa de fase: un rayo la sacude, las alas se oscurecen y se rasgan, se le
     * corta lo que estuviera haciendo y se revuelve en el aire.
     */
    private void alCambiarFase(ServerLevel nivel, int nueva) {
        entityData.set(DATA_FASE, nueva);
        Vec3 c = puntoMundo(AeralisGeometria.NUCLEO);
        rayoDelCielo(nivel, c);
        nivel.sendParticles(AtalayaParticulas.AERALIS_RAYO, true, true, c.x, c.y, c.z, 14, 3.0, 2.0, 3.0, 0.0);
        nivel.sendParticles(AtalayaParticulas.AERALIS_LUZ, true, true, c.x, c.y, c.z, 30, 1.0, 1.0, 1.0, 0.25);
        nivel.sendParticles(AtalayaParticulas.AERALIS_ESCAMA, true, true, c.x, c.y, c.z, 40, 5.0, 2.0, 5.0, 0.05);
        nivel.sendParticles(AtalayaParticulas.AERALIS_ONDA, true, true, c.x, c.y, c.z, 0, 2.4, 18.0, 0.0, 1.0);
        int e = getEstado();
        if (e == DORMIDA || e == DESPERTAR) {
            return;
        }
        // Empuja a los de debajo: el aire que suelta al revolverse.
        for (Player p : jugadores(nivel, 12, 0)) {
            Vec3 fuera = horizontalHacia(position(), p.position());
            p.setDeltaMovement(fuera.x * 1.1, 0.4, fuera.z * 1.1);
            p.hurtMarked = true;
        }
        cancelarJuicio(nivel);
        terminarCaza();
        if (e != TAMBALEO) {
            ponerEstado(TAMBALEO, AeralisGeometria.DURACION_TAMBALEO);
            sonido(AtalayaSonidos.AERALIS_TAMBALEO, 7.0F);
        }
        if (nueva == 2) {
            enfCaza = 80;
        }
        if (nueva == 3) {
            enfJuicio = 140;
        }
        if (nueva == 4) {
            relojAgotado = 300;
        }
    }

    @Override
    public void remove(RemovalReason motivo) {
        super.remove(motivo);
        limpiar();
    }

    /** Lo suyo que queda por ahi (tornados, ciclon, nucleos) se va con ella. */
    private void limpiar() {
        manchas.clear();
        vientos.clear();
        entityData.set(DATA_PICADO, 0.0F);
        for (TornadoAeralisEntity tor : tornadosVivos) {
            tor.discard();
        }
        tornadosVivos.clear();
        if (ciclon != null) {
            ciclon.discard();
            ciclon = null;
        }
        for (NucleoVientoEntity n : nucleos) {
            n.discard();
        }
        nucleos.clear();
        if (presa != null) {
            presa.removeEffect(MarcaVendavalEffect.MARCA);
        }
    }

    // ------------------------------------------------------------------
    //  Dano: la vida efectiva del grupo
    // ------------------------------------------------------------------

    @Override
    public boolean hurtServer(ServerLevel nivel, DamageSource fuente, float cantidad) {
        if (fuente.is(DamageTypeTags.BYPASSES_INVULNERABILITY)) {
            return super.hurtServer(nivel, fuente, cantidad);
        }
        if (fuente.is(DamageTypes.IN_WALL) || fuente.is(DamageTypes.FALL) || fuente.is(DamageTypes.DROWN)
                || fuente.is(DamageTypes.CRAMMING) || fuente.is(DamageTypes.FLY_INTO_WALL)) {
            return false;
        }
        Entity causante = fuente.getEntity();
        Entity directo = fuente.getDirectEntity();
        if (causante instanceof AeralisEntity || directo instanceof RafagaAeralisEntity
                || directo instanceof CuchillaVientoEntity || directo instanceof TornadoAeralisEntity) {
            return false;
        }
        int e = getEstado();
        if (e == DORMIDA) {
            despertarse(causante);
            avisoInmune(nivel, causante);
            return false;
        }
        if (e == DESPERTAR) {
            avisoInmune(nivel, causante);
            return false;
        }
        if (e == JUICIO_SUBE || e == JUICIO_SOSTIENE || e == JUICIO_GOLPE) {
            // El Juicio del Ciclon es cooperativo: dentro del ciclon no se le puede pegar,
            // lo unico que sirve es romper los cuatro nucleos.
            avisoInmune(nivel, causante);
            return false;
        }
        if (causante instanceof LivingEntity vivo && random.nextInt(4) == 0 && caza <= 0) {
            setTarget(vivo);
        }
        // Aturdida, agotada o posada tras el Picado, en el suelo: el doble.
        float k = factorGrupo * ((e == AGOTADA || e == ATURDIDA || e == POSADA) ? 2.0F : 1.0F);
        boolean entra = super.hurtServer(nivel, fuente, cantidad * k);
        if (entra) {
            Vec3 p = directo != null ? directo.position() : puntoMundo(AeralisGeometria.NUCLEO);
            nivel.sendParticles(AtalayaParticulas.AERALIS_ESCAMA, true, true, p.x, p.y, p.z, 6, 0.4, 0.4, 0.4, 0.05);
        }
        return entra;
    }

    /** El golpe resbala en la quitina y el viento que la envuelve lo desvia. */
    private void avisoInmune(ServerLevel nivel, @Nullable Entity causante) {
        if (tickCount - ultimoAvisoInmune < 5) {
            return;
        }
        ultimoAvisoInmune = tickCount;
        Vec3 p = puntoMundo(AeralisGeometria.NUCLEO);
        if (causante != null) {
            Vec3 fuera = horizontalHacia(position(), causante.position());
            double y = Mth.clamp(causante.getEyeY(), getY() + 0.5, getY() + 9.0);
            p = new Vec3(getX() + fuera.x * 1.8, y, getZ() + fuera.z * 1.8);
        }
        nivel.playSound(null, p.x, p.y, p.z, AtalayaSonidos.AERALIS_INMUNE, SoundSource.HOSTILE, 1.5F,
                0.9F + random.nextFloat() * 0.2F);
        nivel.sendParticles(AtalayaParticulas.AERALIS_VIENTO, true, true, p.x, p.y, p.z, 6, 0.3, 0.3, 0.3, 0.2);
    }

    // ------------------------------------------------------------------
    //  La liberacion: el ojo de la tormenta se apaga, baja planeando, se
    //  posa con las alas abiertas al sol y se deshace en una rafaga tibia.
    // ------------------------------------------------------------------

    @Override
    public void kill(ServerLevel nivel) {
        limpiar();
        discard();
    }

    @Override
    public void die(DamageSource fuente) {
        super.die(fuente);
        entityData.set(DATA_OBJETIVO, -1);
        entityData.set(DATA_FURIA, false);
        if (level() instanceof ServerLevel nivel) {
            cancelarJuicio(nivel);
        }
        terminarCaza();
        limpiar();
    }

    @Override
    protected void tickDeath() {
        ++deathTime;
        if (!(level() instanceof ServerLevel nivel) || isRemoved()) {
            return;
        }
        if (deathTime == 1) {
            sonido(AtalayaSonidos.AERALIS_LIBERACION, 6.0F);
        }
        // Baja planeando hasta posarse.
        double suelo = sueloBajo(nivel, getX(), getY(), getZ());
        if (getY() > suelo + 0.05) {
            setPos(getX(), Math.max(suelo, getY() - Math.max(0.03, (getY() - suelo) * 0.05)), getZ());
        }
        setDeltaMovement(Vec3.ZERO);
        Vec3 c = puntoMundo(AeralisGeometria.NUCLEO);
        if (deathTime == AeralisGeometria.LIBERACION_OJOS_ORO) {
            nivel.sendParticles(AtalayaParticulas.AERALIS_ORO, true, true, c.x, c.y, c.z, 50, 1.2, 1.6, 1.2, 0.1);
            nivel.sendParticles(AtalayaParticulas.AERALIS_LUZ, true, true, c.x, c.y + 6, c.z, 60, 8.0, 3.0, 8.0, 0.05);
        }
        if (deathTime > AeralisGeometria.LIBERACION_OJOS_ORO && deathTime % 3 == 0) {
            nivel.sendParticles(AtalayaParticulas.AERALIS_ORO, true, true, c.x, c.y, c.z, 2, 3.0, 2.0, 3.0, 0.01);
        }
        if (deathTime == 150) {
            Vec3 m = position();
            for (Player p : nivel.getEntitiesOfClass(Player.class, new AABB(m, m).inflate(80))) {
                p.addEffect(new MobEffectInstance(BendicionVientosEffect.BENDICION, 20 * 60 * 10, 0), this);
            }
        }
        if (deathTime == 160) {
            sonido(AtalayaSonidos.AERALIS_DISOLVER, 5.0F);
        }
        if (deathTime >= AeralisGeometria.DURACION_LIBERACION) {
            nivel.sendParticles(AtalayaParticulas.AERALIS_JIRON, true, true, getX(), getY() + 6.0, getZ(), 70, 3.0, 4.0, 3.0, 0.08);
            nivel.sendParticles(AtalayaParticulas.AERALIS_ORO, true, true, getX(), getY() + 6.0, getZ(), 50, 3.0, 4.0, 3.0, 0.05);
            nivel.sendParticles(AtalayaParticulas.AERALIS_ESCAMA, true, true, getX(), getY() + 6.0, getZ(), 40, 6.0, 3.0, 6.0, 0.02);
            remove(RemovalReason.KILLED);
        }
    }

    // ------------------------------------------------------------------
    //  Geometria
    // ------------------------------------------------------------------

    /** Un punto en bloques (izquierda, alto, frente) del cuerpo, en el mundo. */
    public Vec3 puntoMundo(Vec3 local) {
        return NereaEntity.puntoMundo(local, position(), yBodyRot);
    }

    public Vec3 frente() {
        float b = yBodyRot * Mth.DEG_TO_RAD;
        return new Vec3(-Mth.sin(b), 0, Mth.cos(b));
    }

    private float rumboHacia(Vec3 p) {
        return (float) (Mth.atan2(p.z - getZ(), p.x - getX()) * Mth.RAD_TO_DEG) - 90.0F;
    }

    private void girarHacia(Vec3 p, float paso) {
        float deseado = rumboHacia(p);
        float actual = getYRot();
        fijarRumbo(actual + Mth.clamp(Mth.wrapDegrees(deseado - actual), -paso, paso));
    }

    private void fijarRumbo(float r) {
        setYRot(r);
        yBodyRot = r;
        yHeadRot = r;
    }

    static double horizontal(Vec3 a, Vec3 b) {
        double dx = a.x - b.x;
        double dz = a.z - b.z;
        return Math.sqrt(dx * dx + dz * dz);
    }

    static Vec3 horizontalHacia(Vec3 desde, Vec3 hasta) {
        Vec3 d = new Vec3(hasta.x - desde.x, 0, hasta.z - desde.z);
        return d.lengthSqr() < 1.0E-4 ? new Vec3(1, 0, 0) : d.normalize();
    }

    /** Lo que sus ataques pueden golpear: todo lo vivo menos ella y los jugadores en creativo o espectador. */
    public boolean esPresa(LivingEntity v) {
        if (v == this || v instanceof AeralisEntity || !v.isAlive()) {
            return false;
        }
        return !(v instanceof Player p) || (!p.isCreative() && !p.isSpectator());
    }

    private List<Player> jugadores(ServerLevel nivel, double max, double min) {
        List<Player> out = new ArrayList<>();
        for (Player p : nivel.getEntitiesOfClass(Player.class, getBoundingBox().inflate(max, max + 16, max))) {
            if (p.isCreative() || p.isSpectator() || !p.isAlive()) {
                continue;
            }
            double d = horizontal(position(), p.position());
            if (d <= max && d >= min) {
                out.add(p);
            }
        }
        return out;
    }

    /**
     * Un rayo que cae del cielo en p: una columna de chispas de rayo de treinta
     * bloques y el trueno. Al cambiar de fase la alcanza a ella; en el golpe
     * del Juicio, al marcado.
     */
    private void rayoDelCielo(ServerLevel nivel, Vec3 p) {
        double x = p.x;
        double z = p.z;
        for (int k = 0; k < 20; k++) {
            x += (random.nextDouble() - 0.5) * 0.9;
            z += (random.nextDouble() - 0.5) * 0.9;
            nivel.sendParticles(AtalayaParticulas.AERALIS_RAYO, true, true, x, p.y + k * 1.5, z, 1, 0.1, 0.3, 0.1, 0.0);
        }
        nivel.sendParticles(AtalayaParticulas.AERALIS_LUZ, true, true, p.x, p.y, p.z, 20, 0.6, 0.6, 0.6, 0.25);
        nivel.playSound(null, p.x, p.y, p.z, AtalayaSonidos.AERALIS_TRUENO, SoundSource.HOSTILE, 6.0F, 1.1F);
    }

    /** Una batida o un golpe contra el suelo: onda de presion (que sacude la camara cerca) y polvo. */
    private void golpeAire(ServerLevel nivel, Vec3 p, float temblor, float radio, int polvo) {
        nivel.sendParticles(AtalayaParticulas.AERALIS_ONDA, true, true, p.x, p.y + 0.12, p.z, 0, temblor, radio, 0.0, 1.0);
        for (int i = 0; i < polvo; i++) {
            double a = random.nextDouble() * Math.PI * 2;
            double v = 0.25 + random.nextDouble() * 0.45;
            nivel.sendParticles(i % 3 == 0 ? AtalayaParticulas.AERALIS_VIENTO : AtalayaParticulas.AERALIS_POLVO,
                    p.x + Math.cos(a) * 1.5, p.y + 0.3, p.z + Math.sin(a) * 1.5, 0, Math.cos(a) * v, 0.05, Math.sin(a) * v, 1.0);
        }
    }

    private void sonido(SoundEvent s, float volumen) {
        playSound(s, volumen, 1.0F);
    }

    private void cortarSonido(ServerLevel nivel, SoundEvent s) {
        ClientboundStopSoundPacket paquete = new ClientboundStopSoundPacket(s.location(), SoundSource.HOSTILE);
        for (ServerPlayer p : nivel.players()) {
            if (p.distanceToSqr(this) < 112 * 112) {
                p.connection.send(paquete);
            }
        }
    }

    // ------------------------------------------------------------------
    //  Sonidos y detalles de gigante
    // ------------------------------------------------------------------

    @Override
    protected @Nullable SoundEvent getAmbientSound() {
        int e = getEstado();
        return e == DORMIDA || e == LIBRE ? AtalayaSonidos.AERALIS_AMBIENTE : null;
    }

    @Override
    public int getAmbientSoundInterval() {
        return 160;
    }

    @Override
    protected SoundEvent getHurtSound(DamageSource fuente) {
        return AtalayaSonidos.AERALIS_HERIDO;
    }

    @Override
    protected @Nullable SoundEvent getDeathSound() {
        return null;
    }

    @Override
    protected float getSoundVolume() {
        return 3.0F;
    }

    @Override
    protected void playStepSound(BlockPos pos, BlockState bloque) {
    }

    @Override
    public boolean causeFallDamage(double distancia, float multiplicador, DamageSource fuente) {
        return false;
    }

    @Override
    public boolean isPushable() {
        return false;
    }

    @Override
    public boolean canBeLeashed() {
        return false;
    }

    @Override
    public boolean removeWhenFarAway(double distancia) {
        return false;
    }

    @Override
    public boolean requiresCustomPersistence() {
        return true;
    }

    @Override
    public boolean canUsePortal(boolean ignorarPasajero) {
        return false;
    }

    @Override
    protected void addAdditionalSaveData(ValueOutput salida) {
        super.addAdditionalSaveData(salida);
        salida.storeNullable("centro", BlockPos.CODEC, centro);
        salida.putBoolean("dormida", getEstado() == DORMIDA);
        salida.putFloat("factor_grupo", factorGrupo);
        salida.putInt("jugadores_grupo", jugadoresGrupo);
        salida.putInt("fase", fase());
        salida.putInt("viento", getViento());
        salida.putBoolean("furia", tieneFuria());
    }

    @Override
    protected void readAdditionalSaveData(ValueInput entrada) {
        super.readAdditionalSaveData(entrada);
        centro = entrada.read("centro", BlockPos.CODEC).orElse(null);
        factorGrupo = entrada.getFloatOr("factor_grupo", VIDA_VANILLA / VIDA);
        jugadoresGrupo = entrada.getIntOr("jugadores_grupo", 1);
        entityData.set(DATA_FASE, entrada.getIntOr("fase", 1));
        entityData.set(DATA_VIENTO, entrada.getIntOr("viento", 0));
        entityData.set(DATA_FURIA, entrada.getBooleanOr("furia", false));
        ponerEstado(entrada.getBooleanOr("dormida", true) ? DORMIDA : LIBRE, 0);
    }
}
