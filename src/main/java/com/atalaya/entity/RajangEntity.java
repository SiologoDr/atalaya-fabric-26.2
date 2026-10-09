package com.atalaya.entity;

import com.atalaya.effect.BendicionTierraEffect;
import com.atalaya.effect.PesoTierraEffect;
import com.atalaya.particula.AtalayaParticulas;
import com.atalaya.sonido.AtalayaSonidos;
import net.minecraft.core.BlockPos;
import net.minecraft.network.protocol.game.ClientboundStopSoundPacket;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundSource;
import net.minecraft.tags.DamageTypeTags;
import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.util.Mth;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.damagesource.DamageTypes;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.entity.AnimationState;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.entity.MoverType;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.ClipContext;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.storage.ValueInput;
import net.minecraft.world.level.storage.ValueOutput;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;
import org.jspecify.annotations.Nullable;

import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;

/**
 * Rajang, el Jaguar de Jade: el tercero de los cuatro jefes elementales.
 *
 * Un dientes de sable colosal tallado en bloques de jade y oro por un pueblo
 * que ya no existe. La Maldicion de la Raiz le subio por la tierra hasta el
 * sol de jade del pecho y lo encendio por dentro. Es el primer jefe que corre:
 * pelea a ras de suelo, a cuatro patas, persiguiendo a sus presas.
 *
 * Nace tumbado como una esfinge ante su templo, hasta que ve a alguien; se
 * invoca con su huevo. Es el tercero: 15 000 de vida y cada ataque pega mas en
 * cada fase (ver los DANO_*).
 *
 * <pre>
 *   fase I    100-75 %   Selva: Garra Terrestre, Terremoto Ancestral, Embestida de Jade
 *   fase II    75-50 %   Grieta: + Sello de la Tierra (inmune mientras dura; si los
 *                        totems no caen a tiempo, el Rugido de Jade mata a todos
 *                        y le deja la Furia), + Tumba de Raices
 *   fase III   50-25 %   Raiz: + Cataclismo de Jade (seis oleadas de fragmentos)
 *   fase IV    25-0 %    Corazon: el peto revienta, salta sobre sus presas y
 *                        el Cataclismo vuelve antes
 * </pre>
 *
 * Las mejoras de octubre de 2026 (tras las pruebas del grupo: "tosco y lento"):
 * la Embestida y la Tumba, los pinchos que lanzan a diez bloques y dejan el
 * Peso dos segundos, fragmentos del Cataclismo mas grandes y menos, escalones
 * del Sello que se caen, el pulso de cada totem roto y la Furia de Jade.
 *
 * Como Nerea y Aeralis, el estado vive en un numero sincronizado, el cliente
 * arranca la animacion que toca al verlo cambiar y los ticks de cada golpe y
 * los puntos del cuerpo salen de {@link RajangGeometria}, generada con las
 * mismas poses. Mide 17 bloques de largo: la caja principal tapa el pecho y
 * las patas de delante, y la cabeza y la grupa llevan cajas propias
 * ({@link RajangParteEntity}) que le pasan el dano.
 */
public class RajangEntity extends Monster {

    public static final int LIBRE = 0;
    public static final int DORMIDO = 1;
    public static final int DESPERTAR = 2;
    public static final int GARRA = 3;
    public static final int TERREMOTO = 4;
    public static final int RUGIDO = 5;
    public static final int SELLO = 6;
    public static final int CATACLISMO = 7;
    public static final int CATACLISMO_SOSTIENE = 8;
    public static final int CATACLISMO_BAJA = 9;
    public static final int ATURDIDO = 10;
    public static final int PARALIZADO = 11;
    public static final int SALTO = 12;
    public static final int TAMBALEO = 13;
    public static final int EMBESTIDA_AVISO = 14;
    public static final int EMBESTIDA = 15;
    public static final int EMBESTIDA_FRENA = 16;
    public static final int ESTAMPADO = 17;
    public static final int TUMBA = 18;
    /** El Idolo de Oro (octubre de 2026): ruge y lanza el idolo; luego 25 s de persecucion. */
    public static final int IDOLO = 19;

    /** Vida EFECTIVA: 15 000 (Nerea 12 500, Aeralis 13 500). La de vanilla tiene tope de 1024: el dano se divide. */
    public static final float VIDA = 15000.0F;
    private static final float VIDA_VANILLA = 1024.0F;

    // --- Danos por fase (I, II, III, IV) ---
    // Pensados para 40 jugadores en hardcore con netherita entera, Proteccion IV
    // y manzana de Notch (18 corazones contando la absorcion): un golpe fuerte
    // les quita 3,5 / 5 / 7,5 / 11 corazones (6, 4, 3 y 2 golpes para matarlos;
    // sin la manzana, en la fase IV basta uno); los de area 2,5 / 4 / 5,5 / 8;
    // los que duran, 1 / 1,5 / 2 / 3 por segundo. Los tipos de dano no escalan
    // con la dificultad. Tras la prueba de octubre de 2026, la II, la III y la IV
    // pegan un 8, un 12 y un 15 % mas.
    /** El zarpazo y el pincho grande de la Garra (los pequenos, algo menos). */
    // Recortado el 07-10-2026 (Juan): -50 % lo de area y -45 % lo individual. Con
    // 60 jugadores y 3-4 totems cada uno, lo normal no debe gastar totems: eso
    // es cosa de los especiales mortales, que no cambian. En la III y la IV,
    // otro -15 % y -20 % (Juan, tras probarlo: las fases I y II estaban bien).
    public static final float[] DANO_GARRA = {17, 22.5F, 25, 32};
    /** Lo que dura el Idolo de Oro fuera (ticks): 25 s. */
    private static final int IDOLO_TICKS = 500;
    /** Con el idolo fuera, a cuanto tiene que estar el portador para lanzarle la Garra (su zarpazo llega a 13). */
    private static final double GARRA_IDOLO = 11.0;
    public static final float[] DANO_TERREMOTO = {13.5F, 20, 21, 25.2F};
    public static final float[] DANO_SALTO = {19, 25, 27.5F, 35.2F};
    /**
     * El Rugido de Jade (el Sello sin romper a tiempo), en cualquier fase: mata a
     * todos los que pelean con el en su rango. Pasa la armadura, el escudo, los
     * encantamientos, los efectos y la resistencia; solo salva un totem de la
     * inmortalidad (y lo gasta).
     */
    public static final float MORTAL = 10000.0F;
    /** La tierra aplasta: contra armadura sus golpes pegan hasta un 30 % mas. */
    private static final float PERFORA_MAXIMO = 0.3F;
    /** Piel de Jade (tras el Terremoto): recibe un 40 % menos durante 10 s. */
    private static final float PIEL_REDUCE = 0.4F;
    private static final int PIEL_TICKS = 200;
    /** El Peso de la Tierra dura 2 s, venga de donde venga (Juan, 08-10-2026: antes 8 s el del Terremoto). */
    private static final int PESO_TICKS = 40;
    /** El Peso que deja un pincho de tierra, sea del ataque que sea. */
    public static final int PESO_PINCHO = PESO_TICKS;

    /**
     * La Embestida: 26 bloques/s, contra una presa a 10-36 bloques. La flecha
     * mide el doble de lo que hay hasta 6 bloques mas alla de ella (24 a 72): se
     * pasa de largo otro tanto. Si su templo no la deja ir tan lejos, la flecha
     * se acorta a lo que de verdad corre.
     */
    private static final double VEL_CARGA = 1.3;
    private static final double CARGA_ALCANCE = 36.0;
    private static final double CARGA_MIN = 24.0;
    private static final double CARGA_MAX = 72.0;
    private static final double CARGA_PASA = 6.0;
    private static final double CARGA_VECES = 2.0;
    /** Lo que la cabeza va por delante de las manos mas lo que derrapa al frenar: el pecho corre la flecha menos esto. */
    private static final double CARGA_CABEZA = 9.5;
    /** Los pinchos de la Embestida: a 4,2 bloques de su linea, uno a cada lado cada 2,2. */
    private static final double PINCHO_LADO = 4.2;
    private static final double PINCHO_CADA = 2.2;
    /** Lo que lanza la Embestida: unos 15 bloques hacia arriba. */
    public static final double LANZA_MORTAL = 1.7;
    /** El zarpazo de la Garra empuja unos 6 bloques (unos 9 ticks en el aire, y algo de derrape). */
    private static final double GARRA_EMPUJE = 0.9;

    /**
     * La Tumba de Raices: un circulo de 36 bloques que se llena en 6 s (siempre
     * igual, RajangGeometria.TUMBA_ESTALLA). Desde el cuerpo a cuerpo hay que
     * correr unos 32: esprintando sobran 0,3 s, y saltando al esprintar 1,5. Quien
     * dude mas, no sale.
     */
    public static final double TUMBA_RADIO = 36.0;
    /**
     * La Tumba en anillo (una de cada dos, testers 07-10-2026): se llena desde el
     * borde hacia el y solo se salva el circulo de este radio a su alrededor.
     */
    public static final double TUMBA_SEGURO = 10.0;
    private static final double TUMBA_CERCA = 15.5;

    /**
     * Al paso (acecha de 6 a 10 bloques) y al galope (a mas de 10); en la fase IV
     * galopa mas. Lo que avanza va con el cuadrado: unos 6,5 bloques/s al paso, 17
     * al galope y 20 en la IV (con la Furia, un 20 % mas).
     */
    private static final double PASO = 1.3;
    private static final double GALOPE = 2.1;
    private static final double GALOPE_IV = 2.3;
    /** Cliente: por encima de esto (bloques/tick) galopa; por debajo, anda (al paso no pasa de 0,4). */
    public static final float VEL_GALOPE = 0.6F;
    private static final int TUMBA_PESO = PESO_TICKS;
    /** Sin Tumba hasta 8 s despues de un Terremoto: con su Peso no se puede escapar. */
    private static final int TUMBA_TRAS_TERREMOTO = 160;

    /** La Furia de Jade (el Sello fallido): mas rapido, mas dano, menos espera. */
    private static final float FURIA_RITMO = 1.15F;
    private static final float FURIA_DANO = 1.2F;
    private static final float FURIA_ENFRIA = 0.75F;
    private static final double FURIA_CORRE = 1.1;

    /** El pulso de cada totem roto: 7 bloques alrededor, y te echa en horizontal. */
    private static final double PULSO_RADIO = 7.0;
    private static final double PULSO_EMPUJE = 2.4;
    /**
     * Cada cuanto tiembla un escalon del Sello al azar (y cae un segundo despues).
     * Aparte, el que se pisa tiembla al rato (PlataformaSelloEntity.PISADA).
     */
    private static final int ESCALON_CADA = 30;

    /** El Sello: 45 s para subir y romper los cuatro totems. Un totem roto se queda roto. */
    public static final int SELLO_TICKS = 900;
    /** Lo que tarda en volver el Sello desde que acaba: 1,7 min en la II, 1,4 en la III, 1,2 en la IV. */
    private static final int SELLO_DESCANSO = 2400;
    /** Las columnas: 26 bloques de alto y 4 de ancho, a 18 de el en sus cuatro diagonales. */
    private static final float SELLO_ALTO = 26.0F;
    private static final float SELLO_ANCHO = 4.0F;
    private static final double SELLO_RADIO = 18.0;
    /** Las piedras para subir: 25 en espiral alrededor de cada columna, un bloque mas alta cada una. */
    private static final int SELLO_PIEDRAS = 25;
    private static final double PIEDRA_RADIO = 4.0;
    private static final float PIEDRA_ANCHO = 1.8F;
    private static final double PIEDRA_GIRO = 0.62;
    /**
     * Seis oleadas de fragmentos, una cada 2 s: 12 s de lluvia de jade; la marca
     * avisa 2,2 s antes (1 s esperando y 1,2 s de caida, RETRASO_FRAGMENTO).
     * Desde el centro de la marca hay que correr 4,8-5,7 bloques.
     */
    private static final int OLEADAS = 6;
    private static final int CADA_OLEADA = 40;
    public static final int AVISO_FRAGMENTO = 24;
    /**
     * Lo que espera cada fragmento con su marca ya en el suelo antes de empezar a
     * caer (ticks): 1 s mas de aviso, con la misma caida (Juan, 09-10-2026: "su
     * caida es buena, solo hay que retrasarlo 1 s").
     */
    public static final int RETRASO_FRAGMENTO = 20;
    /** Los fragmentos con la marca puesta que aun no han empezado a caer: donde, su tamano y cuando. */
    private record FragmentoPendiente(Vec3 marca, float tam, int cuando) {
    }

    private final List<FragmentoPendiente> fragmentosPendientes = new ArrayList<>();

    private static final double ALCANCE_GARRA = 30.0;
    private static final double CORREA = 40.0;
    /** Hasta donde llega su pecho en una Embestida: una carga se pasa de la correa de andar. */
    private static final double CORREA_CARGA = CORREA + 24.0;
    private static final double RANGO_DESPERTAR = 40.0;

    private static final EntityDataAccessor<Integer> DATA_ESTADO =
            SynchedEntityData.defineId(RajangEntity.class, EntityDataSerializers.INT);
    private static final EntityDataAccessor<Integer> DATA_FASE =
            SynchedEntityData.defineId(RajangEntity.class, EntityDataSerializers.INT);
    /** La presa de la Garra o del salto. -1 si nadie. */
    private static final EntityDataAccessor<Integer> DATA_OBJETIVO =
            SynchedEntityData.defineId(RajangEntity.class, EntityDataSerializers.INT);
    /** Lleva puesta la Piel de Jade (los aros de runas). */
    private static final EntityDataAccessor<Boolean> DATA_PIEL =
            SynchedEntityData.defineId(RajangEntity.class, EntityDataSerializers.BOOLEAN);
    /** Ticks que le quedan al Sello (0: no hay Sello) y los totems rotos (bits). */
    private static final EntityDataAccessor<Integer> DATA_SELLO =
            SynchedEntityData.defineId(RajangEntity.class, EntityDataSerializers.INT);
    private static final EntityDataAccessor<Integer> DATA_TOTEMS =
            SynchedEntityData.defineId(RajangEntity.class, EntityDataSerializers.INT);
    /** La Furia de Jade: el aura verde. */
    private static final EntityDataAccessor<Boolean> DATA_FURIA =
            SynchedEntityData.defineId(RajangEntity.class, EntityDataSerializers.BOOLEAN);
    /** Esta Tumba es en anillo: se salva quien esta cerca de el. */
    private static final EntityDataAccessor<Boolean> DATA_TUMBA_ANILLO =
            SynchedEntityData.defineId(RajangEntity.class, EntityDataSerializers.BOOLEAN);
    /** Cuando se le acaba la Furia (tiempo del mundo; 0: sin Furia): el cliente pinta la cuenta atras. */
    private static final EntityDataAccessor<Long> DATA_FURIA_FIN =
            SynchedEntityData.defineId(RajangEntity.class, EntityDataSerializers.LONG);
    /** Lo que mide la flecha de la Embestida desde sus manos (0: no hay flecha). */
    private static final EntityDataAccessor<Float> DATA_CARGA =
            SynchedEntityData.defineId(RajangEntity.class, EntityDataSerializers.FLOAT);
    /** Quien lleva el Idolo de Oro (id de entidad, -1 nadie): el cliente se lo pinta en la cabeza. */
    private static final EntityDataAccessor<Integer> DATA_PORTADOR =
            SynchedEntityData.defineId(RajangEntity.class, EntityDataSerializers.INT);

    // --- Solo cliente ---
    public final AnimationState dormido = new AnimationState();
    public final AnimationState despertar = new AnimationState();
    public final AnimationState garra = new AnimationState();
    public final AnimationState terremoto = new AnimationState();
    public final AnimationState rugido = new AnimationState();
    public final AnimationState sello = new AnimationState();
    public final AnimationState cataclismo = new AnimationState();
    public final AnimationState cataclismoSostiene = new AnimationState();
    public final AnimationState cataclismoBaja = new AnimationState();
    public final AnimationState aturdido = new AnimationState();
    public final AnimationState paralizado = new AnimationState();
    public final AnimationState salto = new AnimationState();
    public final AnimationState tambaleo = new AnimationState();
    public final AnimationState embestidaAviso = new AnimationState();
    public final AnimationState embestida = new AnimationState();
    public final AnimationState embestidaFrena = new AnimationState();
    public final AnimationState estampado = new AnimationState();
    public final AnimationState tumba = new AnimationState();
    public final AnimationState liberacion = new AnimationState();
    public int inicioEstado;
    public float ritmoCliente = 1.0F;
    /** Cuanto pesa el reposo/andar/correr (0 a 1): baja al atacar. */
    public float pesoLibre = 1.0F;
    public float pesoLibreAnt = 1.0F;
    /** Bloques por tick a los que va, suavizado. */
    public float velocidad;
    public float velocidadAnt;
    /** Relojes del paso y del galope (ms de animacion): corren con la velocidad. */
    public float relojAndar;
    public float relojAndarAnt;
    public float relojCorrer;
    public float relojCorrerAnt;

    // --- Solo servidor ---
    private @Nullable BlockPos centro;
    private float factorGrupo = VIDA_VANILLA / VIDA;
    private int jugadoresGrupo = 1;
    private int t;
    private int duracion;
    private float ritmoEstado = 1.0F;
    private int respiro = 30;
    /** Lo que le queda en escena tras despertar (ticks): quieto, sin atacar e inmune. */
    private int escena;
    private int enfGarra = 30;
    private int enfTerremoto = 140;
    private int enfSello = 120;
    private int enfCataclismo = 140;
    private int enfSalto = 80;
    private int enfEmbestida = 60;
    private int enfTumba = 200;
    private int enfIdolo = 300;
    /** El Idolo de Oro fuera: lo que le queda, el altar, quien lo lleva o donde esta tirado. */
    private int idoloQueda;
    private @Nullable Vec3 altar;
    /** El pilar del altar, donde se pone el idolo. */
    private @Nullable AltarIdoloEntity pilarAltar;
    private @Nullable Player portador;
    /** Quien lo llevaba el tick de antes: si lo suelta con la Q, el idolo sale lanzado. */
    private @Nullable Player portadorAntes;
    /** El ultimo idolo lanzado con la Q (su id de entidad), para no lanzarlo dos veces. */
    private int idoloLanzado = -1;
    private @Nullable ItemEntity idoloSuelo;
    /** Lo que espera antes de poder dar el zarpazo al portador (que le de tiempo a correr). */
    private int idoloAgarra;
    private int ultimoTerremoto = -1000;
    private int ultimoEscalon;
    private int ultimoAvisoInmune;
    private int piel;
    private @Nullable LivingEntity presa;
    private @Nullable Vec3 destino;
    private boolean saltando;
    private final List<RajangParteEntity> partes = new ArrayList<>();
    /** La Garra: los picos que faltan por salir (tick en que salen, sitio, tamano, rumbo). */
    private final List<double[]> picos = new ArrayList<>();
    // El Sello
    private final List<PlataformaSelloEntity> plataformas = new ArrayList<>();
    private final List<TotemSelloEntity> totems = new ArrayList<>();
    /** Los totems que faltan por salir: tick, la cima (x, y, z) y su indice. */
    private final List<double[]> totemsPendientes = new ArrayList<>();
    private int sinCaida;
    /** El Sello no se rompio a tiempo: el rugido que viene es el Rugido de Jade. */
    private boolean rugidoFinal;
    // El Cataclismo
    private boolean mato;
    // La Embestida
    private Vec3 dirCarga = new Vec3(0, 0, 1);
    /** Lo que mide la flecha (desde sus manos) y lo que corre su pecho. */
    private double largoFlecha;
    private double largoCarga;
    private double recorrido;
    private double siguientePincho;
    /** Lo deprisa que va en la carga o la frenada (bloques por tick); 0: no carga. */
    private double velCarga;
    private double avanceCarga;
    private final java.util.Set<Integer> arrollados = new java.util.HashSet<>();
    // La Tumba
    private @Nullable Vec3 centroTumba;
    /** Las Tumbas que lleva: las impares van en anillo. */
    private int tumbas;

    public RajangEntity(EntityType<? extends Monster> tipo, Level nivel) {
        super(tipo, nivel);
        this.xpReward = 450;
    }

    public static AttributeSupplier.Builder crearAtributos() {
        return Monster.createMonsterAttributes()
                .add(Attributes.MAX_HEALTH, VIDA_VANILLA)
                .add(Attributes.ARMOR, 16.0D)
                .add(Attributes.ARMOR_TOUGHNESS, 10.0D)
                .add(Attributes.ATTACK_DAMAGE, 14.0D)
                .add(Attributes.MOVEMENT_SPEED, 0.3D)
                .add(Attributes.FOLLOW_RANGE, 72.0D)
                .add(Attributes.KNOCKBACK_RESISTANCE, 1.0D)
                .add(Attributes.STEP_HEIGHT, 2.1D);
    }

    @Override
    protected void defineSynchedData(SynchedEntityData.Builder datos) {
        super.defineSynchedData(datos);
        datos.define(DATA_ESTADO, DORMIDO);
        datos.define(DATA_FASE, 1);
        datos.define(DATA_OBJETIVO, -1);
        datos.define(DATA_PIEL, false);
        datos.define(DATA_SELLO, 0);
        datos.define(DATA_TOTEMS, 0);
        datos.define(DATA_FURIA, false);
        datos.define(DATA_FURIA_FIN, 0L);
        datos.define(DATA_TUMBA_ANILLO, false);
        datos.define(DATA_CARGA, 0.0F);
        datos.define(DATA_PORTADOR, -1);
    }

    @Override
    protected void registerGoals() {
        // Sin goals de movimiento: andar, correr y saltar lo decide
        // customServerAiStep, que sabe hasta donde le deja su templo.
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

    public boolean tienePiel() {
        return entityData.get(DATA_PIEL);
    }

    /** Ticks que le quedan al Sello (0 si no hay). */
    public int getSello() {
        return entityData.get(DATA_SELLO);
    }

    /** Los totems rotos, un bit cada uno. */
    public int getTotemsRotos() {
        return entityData.get(DATA_TOTEMS);
    }

    /** Con la Furia de Jade (el aura verde): ha fallado un Sello y aun no lo han derribado. */
    public boolean tieneFuria() {
        return entityData.get(DATA_FURIA);
    }

    /** La Tumba que hace ahora es en anillo (cliente y servidor). */
    public boolean isTumbaAnillo() {
        return entityData.get(DATA_TUMBA_ANILLO);
    }

    /** El tiempo del mundo en que se le acaba la Furia (0 si no la tiene). */
    public long getFuriaFin() {
        return entityData.get(DATA_FURIA_FIN);
    }

    /** Lo que mide la flecha de la Embestida desde sus manos (0: no hay). */
    public float getCarga() {
        return entityData.get(DATA_CARGA);
    }

    public @Nullable BlockPos getCentro() {
        return centro;
    }

    public int getJugadoresGrupo() {
        return jugadoresGrupo;
    }

    private int faseSegunVida() {
        float k = getHealth() / getMaxHealth();
        return k > 0.75F ? 1 : k > 0.5F ? 2 : k > 0.25F ? 3 : 4;
    }

    private void ponerEstado(int estado, int dur) {
        if (estado != SALTO && saltando) {
            // Un salto cortado a medias (por otro ataque o una orden) no puede seguir
            // empujandolo: sin esto, alzado en el Cataclismo seguia resbalando hacia delante.
            saltando = false;
            Vec3 v = getDeltaMovement();
            setDeltaMovement(0, Math.min(0, v.y), 0);
        }
        if (estado != EMBESTIDA && estado != EMBESTIDA_FRENA) {
            velCarga = 0.0;
        }
        if (estado != EMBESTIDA_AVISO && estado != EMBESTIDA) {
            entityData.set(DATA_CARGA, 0.0F);
        }
        entityData.set(DATA_ESTADO, estado);
        t = 0;
        ritmoEstado = ritmo(estado, fase(), tieneFuria());
        avisoEstado = aviso(estado);
        duracion = (int) Math.ceil(dur / ritmoEstado) + avisoEstado;
    }

    /**
     * Lo rapido que van sus ataques: x1,05 en la fase I hasta x1,45 en la IV, y
     * con la Furia un 25 % mas. El cliente usa el mismo numero. La Tumba no va
     * con la fase: escapar de ella cuesta siempre lo mismo.
     */
    public static float ritmo(int estado, int fase, boolean furia) {
        return switch (estado) {
            case GARRA, TERREMOTO, SALTO, CATACLISMO, CATACLISMO_BAJA, RUGIDO, EMBESTIDA_AVISO ->
                    new float[]{1.0F, 1.05F, 1.22F, 1.3F, 1.42F}[Mth.clamp(fase, 1, 4)] * (furia ? FURIA_RITMO : 1.0F);
            default -> 1.0F;
        };
    }

    private float ta() {
        return Math.max(0, t - avisoEstado) * ritmoEstado;
    }

    /**
     * La espera de aviso al empezar un ataque (ticks reales, no se acelera con la
     * fase ni con la Furia): carga quieto mientras sale el aviso y suena la
     * alerta, y luego el ataque corre como siempre. Asi de aviso a golpe hay al
     * menos 0,8 s (testers, 07-10-2026).
     */
    public static int aviso(int estado) {
        return switch (estado) {
            case GARRA -> 11;
            // La Embestida: 2 s mas con la flecha en el suelo (Juan, 08-10-2026),
            // para que de tiempo a correr antes de que cargue.
            case EMBESTIDA_AVISO -> EMBESTIDA_ESPERA;
            default -> 0;
        };
    }

    /** La espera de aviso del estado actual (ticks reales). */
    private int avisoEstado;
    /** Lo que espera la Embestida con la flecha puesta antes de agazaparse (ticks reales). */
    public static final int EMBESTIDA_ESPERA = 40;
    /**
     * Lo que sigue a su presa con la flecha al empezar la Embestida (ticks reales):
     * despues el rumbo y el largo quedan fijos unos 2 s, para apartarse de la linea.
     */
    public static final int EMBESTIDA_SIGUE = 20;

    private boolean cruza(int k) {
        return (t - 1 - avisoEstado) * ritmoEstado < k && (t - avisoEstado) * ritmoEstado >= k;
    }

    /** Lo que pega a v un golpe de dano base "dano": la tierra aplasta la armadura, hasta un 30 % mas. */
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

    /** El Peso de la Tierra que deja un golpe suyo (sin rebajar uno que ya sea mas largo). */
    public void lastrar(LivingEntity v, int ticks) {
        v.addEffect(new MobEffectInstance(PesoTierraEffect.PESO, ticks, 0, false, true, true), this);
    }

    @Override
    public void onSyncedDataUpdated(EntityDataAccessor<?> dato) {
        super.onSyncedDataUpdated(dato);
        if (DATA_ESTADO.equals(dato) && level().isClientSide()) {
            arrancarAnimacion();
        }
    }

    private AnimationState[] acciones() {
        return new AnimationState[]{dormido, despertar, garra, terremoto, rugido, sello, cataclismo, cataclismoSostiene,
                cataclismoBaja, aturdido, paralizado, salto, tambaleo, embestidaAviso, embestida, embestidaFrena, estampado, tumba};
    }

    private @Nullable AnimationState animacionDe(int estado) {
        return switch (estado) {
            case DORMIDO -> dormido;
            case DESPERTAR -> despertar;
            case GARRA -> garra;
            case TERREMOTO -> terremoto;
            case RUGIDO, IDOLO -> rugido;
            case SELLO -> sello;
            case CATACLISMO -> cataclismo;
            case CATACLISMO_SOSTIENE -> cataclismoSostiene;
            case CATACLISMO_BAJA -> cataclismoBaja;
            case ATURDIDO -> aturdido;
            case PARALIZADO -> paralizado;
            case SALTO -> salto;
            case TAMBALEO -> tambaleo;
            case EMBESTIDA_AVISO -> embestidaAviso;
            case EMBESTIDA -> embestida;
            case EMBESTIDA_FRENA -> embestidaFrena;
            case ESTAMPADO -> estampado;
            case TUMBA -> tumba;
            default -> null;
        };
    }

    private void arrancarAnimacion() {
        for (AnimationState a : acciones()) {
            a.stop();
        }
        // Con espera de aviso, la animacion (y su reloj) empieza al acabarla.
        inicioEstado = tickCount + aviso(getEstado());
        ritmoCliente = ritmo(getEstado(), fase(), tieneFuria());
        AnimationState actual = animacionDe(getEstado());
        if (actual != null) {
            // Si empieza en el futuro, hasta entonces se queda en su primer fotograma.
            actual.start(inicioEstado);
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
        pesoLibre = objetivoPeso > pesoLibre ? Math.min(objetivoPeso, pesoLibre + 0.15F) : Math.max(objetivoPeso, pesoLibre - 0.25F);
        dinamicaPaso();
        if (muriendo) {
            if (!liberacion.isStarted()) {
                for (AnimationState a : acciones()) {
                    a.stop();
                }
                liberacion.start(tickCount);
            }
            return;
        }
        efectosCliente();
    }

    /**
     * Cliente: la velocidad a la que va, suavizada, y los relojes del paso y
     * del galope, que corren con ella. Cada pisada suena y levanta polvo.
     */
    private void dinamicaPaso() {
        velocidadAnt = velocidad;
        relojAndarAnt = relojAndar;
        relojCorrerAnt = relojCorrer;
        double vx = getX() - xo;
        double vz = getZ() - zo;
        float v = getEstado() == LIBRE ? (float) Math.sqrt(vx * vx + vz * vz) : 0.0F;
        velocidad += (v - velocidad) * 0.25F;
        float andar = Mth.clamp(velocidad / 0.06F, 0.0F, 1.0F);
        float periodoAndar = RajangGeometria.PERIODO_ANDAR * 50.0F;
        float periodoCorrer = RajangGeometria.PERIODO_CORRER * 50.0F;
        // Cada reloj corre lo justo para que las zarpas que apoyan vayan con el suelo y no
        // resbalen: lo que recorren por tick al paso y al galope lo mide rajang_juego_anim.py.
        // El galope esta hecho para 1 bloque/tick y va a 0,86: no baja del 80 % de su ritmo
        // (a la mitad se veia pesado), aunque las zarpas resbalen un poco.
        relojAndar += 50.0F * andar * Mth.clamp(velocidad / RajangGeometria.ZANCADA_ANDAR, 0.4F, 2.6F);
        relojCorrer += 50.0F * Mth.clamp(velocidad / RajangGeometria.ZANCADA_CORRER, 0.8F, 1.3F);
        // Pisadas: dos por ciclo (las manos de cada lado) al andar, una por ciclo al galope.
        if (velocidad > 0.03F) {
            boolean corre = velocidad > VEL_GALOPE;
            float reloj = corre ? relojCorrer : relojAndar;
            float ant = corre ? relojCorrerAnt : relojAndarAnt;
            float periodo = (corre ? periodoCorrer : periodoAndar) / 2.0F;
            if (Math.floor(reloj / periodo) != Math.floor(ant / periodo)) {
                pisada(corre);
            }
        }
    }

    private void pisada(boolean corre) {
        Vec3[] patas = {RajangGeometria.ZARPA_IZQ, RajangGeometria.ZARPA_DER, RajangGeometria.PATA_IZQ, RajangGeometria.PATA_DER};
        Vec3 p = puntoMundo(patas[random.nextInt(4)]);
        level().playLocalSound(p.x, p.y, p.z, AtalayaSonidos.RAJANG_PASO, SoundSource.HOSTILE, corre ? 2.6F : 1.8F,
                0.85F + random.nextFloat() * 0.2F, false);
        for (int i = 0; i < (corre ? 6 : 3); i++) {
            double a = random.nextDouble() * Math.PI * 2;
            level().addParticle(AtalayaParticulas.RAJANG_POLVO, p.x + Math.cos(a) * 0.8, p.y + 0.15, p.z + Math.sin(a) * 0.8,
                    Math.cos(a) * 0.08, 0.03, Math.sin(a) * 0.08);
        }
        if (corre && random.nextInt(2) == 0) {
            level().addParticle(AtalayaParticulas.RAJANG_ROCA, p.x, p.y + 0.3, p.z, random.nextGaussian() * 0.12, 0.25,
                    random.nextGaussian() * 0.12);
        }
    }

    /**
     * Cliente: lo que acompana a cada ataque y al cuerpo: chispas de la
     * maldicion por las grietas, el aliento verde de la boca, los aros de runas
     * de la Piel de Jade, el polvo que se le cae al moverse y las hojas.
     */
    private void efectosCliente() {
        int e = getEstado();
        int f = fase();
        float ta = (tickCount - inicioEstado) * ritmoCliente;
        if (e == DORMIDO) {
            if (tickCount % 30 == 0) {
                Vec3 b = puntoMundo(new Vec3(0, 2.2, RajangGeometria.BOCA.z - 0.6));
                level().addParticle(AtalayaParticulas.RAJANG_POLVO, b.x, b.y, b.z, 0, 0.02, 0);
            }
            if (random.nextInt(14) == 0) {
                Vec3 p = puntoMundo(new Vec3((random.nextDouble() - 0.5) * 4, 3.5 + random.nextDouble(), (random.nextDouble() - 0.5) * 10));
                level().addParticle(AtalayaParticulas.RAJANG_HOJA, p.x, p.y + 4.0, p.z, 0, -0.02, 0);
            }
            return;
        }
        // La maldicion: chispas que salen por las grietas (mas cuanto mas avanzada la fase).
        if (f >= 2 && random.nextInt(Math.max(1, 7 - f * 1)) == 0) {
            Vec3 p = puntoMundo(new Vec3((random.nextDouble() - 0.5) * 3.8, 3.5 + random.nextDouble() * 4.5,
                    RajangGeometria.PECHO.z - random.nextDouble() * (f >= 4 ? 11.0 : f >= 3 ? 6.0 : 2.5)));
            level().addParticle(AtalayaParticulas.RAJANG_CHISPA, p.x, p.y, p.z, 0, 0.03, 0);
        }
        // Los cristales del lomo, los hombros y la corona sueltan luz: mas y mas viva en cada
        // fase (verde, lima, amarillo y, en la IV, con chispas de oro).
        int cada = f >= 4 ? 2 : f == 3 ? 3 : f == 2 ? 6 : 10;
        if (tickCount % cada == 0) {
            double z = -4.2 + random.nextDouble() * 10.7;
            double x = (random.nextDouble() - 0.5) * (z > 2.0 && z < 3.3 ? 3.4 : 0.9);
            Vec3 p = puntoMundo(new Vec3(x, 8.4 + random.nextDouble() * (0.8 + 0.45 * f), z));
            boolean oro = f >= 4 && random.nextInt(3) == 0;
            level().addParticle(oro ? AtalayaParticulas.RAJANG_ORO : AtalayaParticulas.RAJANG_CHISPA, p.x, p.y, p.z,
                    random.nextGaussian() * 0.01, 0.03 + 0.012 * f, random.nextGaussian() * 0.01);
        }
        // El aliento: polvo verde que se le escapa entre los sables.
        if (tickCount % 9 == 0) {
            Vec3 b = puntoMundo(RajangGeometria.BOCA);
            level().addParticle(AtalayaParticulas.RAJANG_CHISPA, b.x, b.y - 0.2, b.z, 0, -0.01, 0);
        }
        // La Furia: llamas verdes que le suben por todo el cuerpo.
        if (tieneFuria()) {
            for (int i = 0; i < 2; i++) {
                Vec3 p = puntoMundo(new Vec3((random.nextDouble() - 0.5) * 4.6, 1.5 + random.nextDouble() * 7.0,
                        -7.0 + random.nextDouble() * 16.0));
                level().addParticle(AtalayaParticulas.RAJANG_LLAMA, p.x, p.y, p.z, random.nextGaussian() * 0.02, 0.06,
                        random.nextGaussian() * 0.02);
            }
            if (random.nextInt(3) == 0) {
                Vec3 p = puntoMundo(new Vec3((random.nextDouble() - 0.5) * 4.0, 2.0 + random.nextDouble() * 6.0,
                        -6.0 + random.nextDouble() * 14.0));
                level().addParticle(AtalayaParticulas.RAJANG_CHISPA, p.x, p.y, p.z, 0, 0.05, 0);
            }
        }
        // La Piel de Jade: runas de oro dando vueltas.
        if (tienePiel() && tickCount % 2 == 0) {
            for (int k = 0; k < 2; k++) {
                double a = tickCount * 0.12 + k * Math.PI;
                double y = getY() + (k == 0 ? 2.2 : 5.4);
                double r = k == 0 ? 5.6 : 4.6;
                level().addParticle(AtalayaParticulas.RAJANG_RUNA, getX() + Math.cos(a) * r, y, getZ() + Math.sin(a) * r,
                        -Math.sin(a) * 0.1, 0, Math.cos(a) * 0.1);
            }
        }
        switch (e) {
            case GARRA -> {
                if (ta >= RajangGeometria.GARRA_ALZA && ta < RajangGeometria.GARRA_GOLPE) {
                    // Las garras de la zarpa en alto se cargan de luz verde.
                    Vec3 z = puntoMundo(RajangGeometria.ZARPA_CARGA);
                    for (int i = 0; i < 2; i++) {
                        level().addParticle(AtalayaParticulas.RAJANG_CHISPA, z.x + random.nextGaussian() * 0.6, z.y + random.nextGaussian() * 0.6,
                                z.z + random.nextGaussian() * 0.6, 0, 0.03, 0);
                    }
                }
            }
            case TERREMOTO -> {
                if (ta < RajangGeometria.TERREMOTO_GOLPE && tickCount % 2 == 0) {
                    double a = random.nextDouble() * Math.PI * 2;
                    double r = 3.0 + random.nextDouble() * 6.0;
                    level().addParticle(AtalayaParticulas.RAJANG_POLVO, getX() + Math.cos(a) * r, getY() + 0.1, getZ() + Math.sin(a) * r,
                            -Math.cos(a) * 0.12, 0.05, -Math.sin(a) * 0.12);
                }
            }
            case SELLO, RUGIDO -> {
                if (tickCount % 3 == 0) {
                    Vec3 b = puntoMundo(RajangGeometria.BOCA_RUGIDO);
                    level().addParticle(AtalayaParticulas.RAJANG_CHISPA, b.x, b.y, b.z, random.nextGaussian() * 0.05, 0.08,
                            random.nextGaussian() * 0.05);
                }
            }
            case CATACLISMO_SOSTIENE -> {
                Vec3 b = puntoMundo(RajangGeometria.BOCA_CATACLISMO);
                level().addParticle(AtalayaParticulas.RAJANG_LLAMA, b.x, b.y, b.z, random.nextGaussian() * 0.03, 0.35, random.nextGaussian() * 0.03);
            }
            case ATURDIDO, PARALIZADO, ESTAMPADO -> {
                if (tickCount % 5 == 0) {
                    Vec3 c = puntoMundo(RajangGeometria.CABEZA).add(0, e == ATURDIDO ? -3.5 : 0.5, 0);
                    double a = tickCount * 0.3;
                    level().addParticle(AtalayaParticulas.RAJANG_JADE, c.x + Math.cos(a) * 1.4, c.y + 1.2, c.z + Math.sin(a) * 1.4, 0, 0.02, 0);
                }
            }
            case EMBESTIDA_AVISO -> {
                // Rasca el suelo: polvo y terrones donde la mano raya la tierra.
                if (ta >= RajangGeometria.EMBESTIDA_RASCA_1 - 2 && tickCount % 2 == 0) {
                    Vec3 z = puntoMundo(RajangGeometria.ZARPA_RASCA);
                    level().addParticle(AtalayaParticulas.RAJANG_POLVO, z.x + random.nextGaussian() * 0.5, getY() + 0.2,
                            z.z + random.nextGaussian() * 0.5, random.nextGaussian() * 0.05, 0.04, random.nextGaussian() * 0.05);
                }
                // El aliento se le escapa a resoplidos.
                if (tickCount % 4 == 0) {
                    Vec3 b = puntoMundo(RajangGeometria.BOCA);
                    level().addParticle(AtalayaParticulas.RAJANG_CHISPA, b.x, b.y - 0.6, b.z, 0, -0.02, 0);
                }
            }
            case EMBESTIDA, EMBESTIDA_FRENA -> {
                // La carga levanta un muro de polvo y terrones a su paso.
                if (e == EMBESTIDA || ta < RajangGeometria.EMBESTIDA_FRENA_PARA) {
                    for (int i = 0; i < 3; i++) {
                        Vec3 p = puntoMundo(new Vec3((random.nextDouble() - 0.5) * 6.0, 0.2, -4.0 + random.nextDouble() * 8.0));
                        level().addParticle(AtalayaParticulas.RAJANG_POLVO, p.x, getY() + 0.2, p.z, random.nextGaussian() * 0.08,
                                0.06, random.nextGaussian() * 0.08);
                    }
                    if (random.nextInt(2) == 0) {
                        Vec3 p = puntoMundo(new Vec3((random.nextDouble() - 0.5) * 5.0, 0.2, random.nextDouble() * 4.0));
                        level().addParticle(AtalayaParticulas.RAJANG_ROCA, p.x, getY() + 0.3, p.z, random.nextGaussian() * 0.15, 0.3,
                                random.nextGaussian() * 0.15);
                    }
                }
            }
            case TUMBA -> {
                if (ta < RajangGeometria.TUMBA_ESTALLA && tickCount % 3 == 0) {
                    Vec3 b = puntoMundo(RajangGeometria.BOCA);
                    level().addParticle(AtalayaParticulas.RAJANG_CHISPA, b.x + random.nextGaussian() * 0.6, getY() + 0.4,
                            b.z + random.nextGaussian() * 0.6, random.nextGaussian() * 0.06, 0.02, random.nextGaussian() * 0.06);
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
        // Un jefe de cada tipo por mundo: si ya habia otro, este se va (JefesUnicos).
        if (!admitido) {
            JefesUnicos.Registro otro = JefesUnicos.admitir(nivel, this);
            if (otro != null) {
                JefesUnicos.avisarRepetido(nivel, this, otro);
                discard();
                return;
            }
            admitido = true;
        } else if (tickCount % 200 == 0 && !isDeadOrDying()) {
            JefesUnicos.apuntar(nivel, this);
        }
        if (furiaQueda > 0 && --furiaQueda == 0) {
            ponerFuria(nivel, false);
        }
        if (centro == null) {
            centro = blockPosition();
        }
        if (partes.isEmpty()) {
            crearPartes(nivel);
        }
        moverPartes();
        if (getEstado() != DORMIDO && !isDeadOrDying()) {
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
        // Despierto, siempre persigue a alguien si hay un jugador a tiro: el objetivo
        // de vanilla pide verlo, y con este tamano el ojo se queda entre las hojas o
        // tras una loma (se quedaba quieto aunque hubiera alguien al lado).
        if (getEstado() != DORMIDO && !isDeadOrDying()) {
            soltarFragmentos(nivel);
            objetivo = PresasJefe.revisar(nivel, this, objetivo, Vec3.atCenterOf(centro), 72, getEstado() == LIBRE);
            // En Furia persigue al que mas lejos le esta: que el arquero sienta el miedo.
            if (tieneFuria()) {
                Player lejos = masLejano(nivel, 0.0, 56.0, false);
                if (lejos != null) {
                    objetivo = lejos;
                }
            }
            // La Muralla de Jade: si un tanque le provoca, ese es su objetivo.
            objetivo = com.atalaya.habilidad.Provocacion.objetivo(this, objetivo, com.atalaya.habilidad.Provocacion.ALCANCE);
            if (objetivo != null && getTarget() != objetivo) {
                setTarget(objetivo);
            }
        }
        if (respiro > 0) respiro--;
        if (escena > 0) escena--;
        if (enfGarra > 0) enfGarra--;
        if (enfTerremoto > 0) enfTerremoto--;
        if (enfSello > 0) enfSello--;
        if (enfCataclismo > 0) enfCataclismo--;
        if (enfSalto > 0) enfSalto--;
        if (enfEmbestida > 0) enfEmbestida--;
        if (enfTumba > 0) enfTumba--;
        if (enfIdolo > 0) enfIdolo--;
        if (idoloQueda > 0) {
            tickIdoloFuera(nivel);
        }
        if (piel > 0 && --piel == 0) {
            entityData.set(DATA_PIEL, false);
        }
        tickPicos(nivel);
        tickPiezasSello(nivel);

        int e = getEstado();
        t++;
        switch (e) {
            case DORMIDO -> tickDormido(nivel);
            case DESPERTAR -> tickDespertar(nivel);
            case LIBRE -> tickLibre(nivel, objetivo);
            case GARRA -> tickGarra(nivel);
            case TERREMOTO -> tickTerremoto(nivel);
            case RUGIDO -> tickRugido(nivel);
            case SELLO -> tickSello(nivel);
            case CATACLISMO -> tickCataclismo(nivel);
            case CATACLISMO_SOSTIENE -> tickOleadas(nivel);
            case CATACLISMO_BAJA -> tickBaja(nivel);
            case ATURDIDO, PARALIZADO -> tickAturdido(nivel);
            case SALTO -> tickSalto(nivel);
            case TAMBALEO -> tickTambaleo(nivel);
            case EMBESTIDA_AVISO -> tickEmbestidaAviso(nivel);
            case EMBESTIDA -> tickEmbestida(nivel);
            case EMBESTIDA_FRENA -> tickFrena(nivel);
            case ESTAMPADO -> tickEstampado(nivel);
            case TUMBA -> tickTumba(nivel);
            case IDOLO -> tickIdolo(nivel);
            default -> {
            }
        }
        if (e != LIBRE && e != DORMIDO && getEstado() == e && t >= duracion) {
            alAcabar(nivel, e);
        }
        if (getEstado() != LIBRE) {
            quieto();
            if (!saltando && velCarga <= 0.0) {
                Vec3 v = getDeltaMovement();
                setDeltaMovement(0, v.y, 0);
            }
        }
    }

    /** Que el control de movimiento no lo arrastre: se queda donde esta y no gira solo. */
    private void quieto() {
        getNavigation().stop();
        getMoveControl().setWantedPosition(getX(), getY(), getZ(), 0.0);
    }

    private void alAcabar(ServerLevel nivel, int e) {
        switch (e) {
            case RUGIDO -> {
                if (rugidoFinal) {
                    rugidoFinal = false;
                    terminar();
                } else {
                    empezarSello(nivel);
                }
            }
            case SELLO -> {
                // Se acabo el tiempo: los totems se apagan y ruge con toda la tierra.
                rugidoFinal = true;
                entityData.set(DATA_SELLO, 0);
                ponerEstado(RUGIDO, RajangGeometria.DURACION_RUGIDO);
                sonido(AtalayaSonidos.RAJANG_SELLO, 8.0F);
            }
            case CATACLISMO -> {
                ponerEstado(CATACLISMO_SOSTIENE, OLEADAS * CADA_OLEADA + RETRASO_FRAGMENTO + AVISO_FRAGMENTO + 6);
                mato = false;
            }
            case CATACLISMO_SOSTIENE -> {
                ponerEstado(CATACLISMO_BAJA, RajangGeometria.DURACION_CATACLISMO_BAJA);
            }
            case CATACLISMO_BAJA -> {
                if (mato) {
                    // Se ha cobrado una vida: ruge y sigue (ya no se cura: ningun jefe se cura con
                    // sus ataques, Juan, 09-10-2026).
                    sonido(AtalayaSonidos.RAJANG_RUGIDO, 5.0F);
                    Vec3 c = puntoMundo(RajangGeometria.PECHO);
                    nivel.sendParticles(AtalayaParticulas.RAJANG_CHISPA, true, true, c.x, c.y, c.z, 40, 2.0, 2.0, 2.0, 0.08);
                    terminar();
                } else {
                    // Nadie ha caido: se queda paralizado, con la piedra trabada. Lo han derribado: se le va la Furia.
                    ponerEstado(PARALIZADO, RajangGeometria.DURACION_PARALIZADO);
                    sonido(AtalayaSonidos.RAJANG_PARALIZADO, 5.0F);
                    ponerFuria(nivel, false);
                }
            }
            case SALTO -> {
                saltando = false;
                terminar();
            }
            case EMBESTIDA_AVISO -> empezarCarga(nivel);
            case EMBESTIDA -> frenar(nivel);
            default -> terminar();
        }
    }

    private void terminar() {
        boolean despertaba = getEstado() == DESPERTAR;
        ponerEstado(LIBRE, 0);
        presa = null;
        entityData.set(DATA_OBJETIVO, -1);
        respiro = new int[]{0, 18, 13, 10, 8}[fase()];
        if (despertaba) {
            respiro = Math.max(respiro, PresasJefe.RESPIRO_PRESENTACION);
            escena = PresasJefe.ESCENA_QUIETO;
        }
        if (tieneFuria()) {
            respiro /= 2;
        }
    }

    /** Cada fase todo vuelve antes: en la IV, con un 40 % menos de espera; con la Furia, un 35 % menos encima. */
    private float enfriamiento() {
        float k = new float[]{1.0F, 1.0F, 0.84F, 0.78F, 0.68F}[Mth.clamp(fase(), 1, 4)];
        return tieneFuria() ? k * FURIA_ENFRIA : k;
    }

    // ------------------------------------------------------------------
    //  Libre: corre, anda y elige el siguiente golpe
    // ------------------------------------------------------------------

    private void tickLibre(ServerLevel nivel, @Nullable LivingEntity objetivo) {
        if (idoloQueda > 0 && escena <= 0) {
            // Con el idolo fuera solo anda o corre a por el y, si alcanza a quien
            // lo lleva, la Garra (nada de ataques especiales: Juan, 08-10-2026).
            perseguirIdolo();
            if (portador != null && idoloAgarra <= 0 && respiro <= 0 && enfGarra <= 0
                    && horizontal(position(), portador.position()) < GARRA_IDOLO) {
                iniciar(nivel, GARRA, portador);
            }
            return;
        }
        if (escena > 0) {
            // En escena tras despertar (su cartel aun se lee): ni se mueve ni ataca.
            getNavigation().stop();
            getMoveControl().setWantedPosition(getX(), getY(), getZ(), 0.0);
            setDeltaMovement(0.0, getDeltaMovement().y, 0.0);
            return;
        }
        Vec3 c = Vec3.atBottomCenterOf(centro);
        if (objetivo == null) {
            if (horizontal(position(), c) > 4.0) {
                getMoveControl().setWantedPosition(c.x, c.y, c.z, 0.8);
            }
            return;
        }
        double d = horizontal(position(), objetivo.position());
        // Hacia su presa, sin salir de su templo: corre si esta lejos, la acecha a
        // paso vivo a media distancia, y de cerca se planta mirandola.
        Vec3 meta = objetivo.position();
        Vec3 rel = new Vec3(meta.x - c.x, 0, meta.z - c.z);
        if (rel.length() > CORREA) {
            rel = rel.normalize().scale(CORREA);
            meta = new Vec3(c.x + rel.x, meta.y, c.z + rel.z);
        }
        double furia = tieneFuria() ? FURIA_CORRE : 1.0;
        if (d > 10.0) {
            getMoveControl().setWantedPosition(meta.x, meta.y, meta.z, (fase() >= 4 ? GALOPE_IV : GALOPE) * furia);
        } else if (d > 6.0) {
            getMoveControl().setWantedPosition(meta.x, meta.y, meta.z, PASO * furia);
        } else {
            quieto();
            girarHacia(objetivo.position(), 9.0F);
        }
        if (respiro <= 0) {
            elegirAtaque(nivel, objetivo, d);
        }
    }

    private void elegirAtaque(ServerLevel nivel, LivingEntity objetivo, double d) {
        int fase = fase();
        List<int[]> opciones = new ArrayList<>();
        if (enfGarra <= 0 && d < ALCANCE_GARRA) opciones.add(new int[]{GARRA, 5});
        if (enfTerremoto <= 0) opciones.add(new int[]{TERREMOTO, 3});
        if (fase >= 2 && enfSello <= 0 && !jugadores(nivel, 56, 0).isEmpty()) opciones.add(new int[]{RUGIDO, 2});
        if (fase >= 3 && enfCataclismo <= 0) opciones.add(new int[]{CATACLISMO, 7});
        // La Embestida y el Salto van a por el jugador mas lejano a tiro: los arqueros
        // de lejos salian casi ilesos (testers, 07-10-2026).
        LivingEntity salto = null;
        if (fase >= 4 && enfSalto <= 0) {
            salto = masLejano(nivel, 8.0, 26.0, false);
            if (salto == null && d > 8.0 && d < 26.0) {
                salto = objetivo;
            }
        }
        if (salto != null) opciones.add(new int[]{SALTO, 4});
        LivingEntity carga = null;
        if (enfEmbestida <= 0) {
            carga = masLejano(nivel, 10.0, CARGA_ALCANCE, true);
            if (carga == null && d >= 10.0 && d <= CARGA_ALCANCE && caminoLibre(nivel, objetivo)) {
                carga = objetivo;
            }
        }
        if (carga != null) opciones.add(new int[]{EMBESTIDA_AVISO, 5});
        if (fase >= 2 && enfIdolo <= 0 && idoloQueda <= 0 && !jugadores(nivel, 48, 0).isEmpty()) {
            opciones.add(new int[]{IDOLO, 3});
        }
        if (fase >= 2 && enfTumba <= 0 && tickCount - ultimoTerremoto >= TUMBA_TRAS_TERREMOTO
                && !jugadores(nivel, TUMBA_CERCA, 0).isEmpty()) {
            opciones.add(new int[]{TUMBA, 3});
        }
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
        if (elegido == GARRA) {
            // La garra va a alguien a tiro, al azar entre los que tiene delante (en Furia, al mas lejano).
            List<Player> cerca = jugadores(nivel, ALCANCE_GARRA, 0);
            if (!cerca.isEmpty()) {
                Player a = tieneFuria() ? masLejano(nivel, 0.0, ALCANCE_GARRA, false) : null;
                if (a == null) {
                    a = cerca.get(random.nextInt(cerca.size()));
                }
                objetivo = com.atalaya.habilidad.Provocacion.objetivo(this, a, ALCANCE_GARRA);
                setTarget(objetivo);
            }
        }
        if (elegido == EMBESTIDA_AVISO && carga != null) {
            objetivo = carga;
        }
        if (elegido == SALTO && salto != null) {
            objetivo = salto;
        }
        iniciar(nivel, elegido, objetivo);
    }

    private void iniciar(ServerLevel nivel, int ataque, @Nullable LivingEntity blanco) {
        float k = enfriamiento();
        getNavigation().stop();
        switch (ataque) {
            case GARRA -> {
                enfGarra = (int) (80 * k);
                presa = blanco;
                destino = blanco != null ? blanco.position() : position().add(frente().scale(16));
                if (blanco != null) {
                    entityData.set(DATA_OBJETIVO, blanco.getId());
                }
                ponerEstado(GARRA, RajangGeometria.DURACION_GARRA);
                sonido(AtalayaSonidos.RAJANG_GRUNIDO, 4.0F);
            }
            case TERREMOTO -> {
                enfTerremoto = (int) (320 * k);
                ultimoTerremoto = tickCount;
                ponerEstado(TERREMOTO, RajangGeometria.DURACION_TERREMOTO);
                sonido(AtalayaSonidos.RAJANG_RUGIDO, 5.0F);
            }
            case EMBESTIDA_AVISO -> {
                enfEmbestida = (int) (260 * k);
                presa = blanco;
                if (blanco != null) {
                    entityData.set(DATA_OBJETIVO, blanco.getId());
                }
                ponerEstado(EMBESTIDA_AVISO, RajangGeometria.DURACION_EMBESTIDA_AVISO);
                sonido(AtalayaSonidos.RAJANG_EMBESTIDA_AVISO, 6.0F);
            }
            case TUMBA -> {
                enfTumba = (int) (600 * k);
                centroTumba = null;
                // Una de cada dos, en anillo: hay que acercarse a el (con un rugido mas agudo encima).
                boolean anillo = tumbas++ % 2 == 1;
                entityData.set(DATA_TUMBA_ANILLO, anillo);
                ponerEstado(TUMBA, RajangGeometria.DURACION_TUMBA);
                sonido(AtalayaSonidos.RAJANG_TUMBA, 8.0F);
                if (anillo) {
                    nivel.playSound(null, getX(), getEyeY(), getZ(), AtalayaSonidos.RAJANG_TUMBA, SoundSource.HOSTILE, 8.0F, 1.35F);
                }
            }
            case RUGIDO -> {
                enfSello = (int) (1100 * k);
                ponerEstado(RUGIDO, RajangGeometria.DURACION_RUGIDO);
                sonido(AtalayaSonidos.RAJANG_SELLO, 8.0F);
            }
            case CATACLISMO -> {
                enfCataclismo = (int) ((fase() >= 4 ? 520 : 820) * k);
                ponerEstado(CATACLISMO, RajangGeometria.DURACION_CATACLISMO);
                sonido(AtalayaSonidos.RAJANG_CATACLISMO, 8.0F);
            }
            case IDOLO -> {
                enfIdolo = (int) (1200 * k);
                ponerEstado(IDOLO, RajangGeometria.DURACION_RUGIDO);
                sonido(AtalayaSonidos.RAJANG_RUGIDO, 6.0F);
            }
            case SALTO -> {
                enfSalto = (int) (150 * k);
                presa = blanco;
                if (blanco != null) {
                    entityData.set(DATA_OBJETIVO, blanco.getId());
                }
                ponerEstado(SALTO, RajangGeometria.DURACION_SALTO);
                sonido(AtalayaSonidos.RAJANG_GRUNIDO, 4.0F);
            }
            default -> {
            }
        }
    }

    /**
     * Para probar y para el operador de la serie: fuerza un ataque o un momento
     * del combate. Apunta al ser vivo mas cercano que no sea el.
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
                if (getEstado() == DORMIDO) {
                    despertarse(blanco);
                }
                setHealth(getMaxHealth() * (1.0F - 0.25F * (siguiente - 1)) - 1.0F);
                return true;
            }
            case "liberar" -> {
                hurtServer(nivel, nivel.damageSources().genericKill(), Float.MAX_VALUE);
                return true;
            }
            case "perseguir" -> {
                // Persigue al ser vivo mas lejano (para ver el paso y el galope), a menos
                // de 56 bloques de verdad (no en las esquinas de la caja) y dentro de la
                // correa, que si no lo suelta en el tick siguiente y se queda quieto.
                LivingEntity lejos = null;
                double max = 0;
                Vec3 casa = centro != null ? Vec3.atCenterOf(centro) : position();
                for (LivingEntity v : nivel.getEntitiesOfClass(LivingEntity.class, getBoundingBox().inflate(56), this::esPresa)) {
                    double d = v.distanceToSqr(this);
                    if (d > max && d <= 56 * 56 && v.distanceToSqr(casa) <= 72 * 72) {
                        max = d;
                        lejos = v;
                    }
                }
                if (getEstado() == DORMIDO) {
                    despertarse(lejos);
                    return true;
                }
                if (lejos != null) {
                    setTarget(lejos);
                }
                ponerEstado(LIBRE, 0);
                respiro = 160;
                return true;
            }
            case "pisar" -> {
                // Sube al jugador mas cercano a un escalon alto del Sello (para ver que el que se pisa se cae).
                if (blanco instanceof ServerPlayer jp) {
                    for (PlataformaSelloEntity p : plataformas) {
                        if (p.getTipo() == PlataformaSelloEntity.PIEDRA && p.getEscalon() >= 6 && p.firme() && !p.enCaida()) {
                            jp.teleportTo(p.getX(), p.getBoundingBox().maxY + 0.05, p.getZ());
                            break;
                        }
                    }
                }
                return true;
            }
            case "romper" -> {
                // Rompe los totems que queden en pie (para ver el final bueno del Sello).
                for (TotemSelloEntity tot : new ArrayList<>(totems)) {
                    if (!tot.isRoto()) {
                        tot.romper(nivel);
                    }
                }
                return true;
            }
            case "furia" -> {
                // Le pone o le quita la Furia de Jade (para verla sin fallar un Sello).
                ponerFuria(nivel, !tieneFuria());
                return true;
            }
            case "escalon" -> {
                // Hace temblar ya un escalon del Sello (si hay Sello).
                temblarEscalon(nivel);
                return true;
            }
            default -> {
            }
        }
        if (orden.equals("altar")) {
            // Junto al pilar (encima no: es una caja de choque).
            Player p = nivel.getNearestPlayer(this, 96);
            if (p != null && altar != null) {
                p.teleportTo(altar.x + 1.6, altar.y + 0.1, altar.z);
            }
            return true;
        }
        if (orden.equals("tumba") || orden.equals("anillo")) {
            tumbas = orden.equals("anillo") ? 1 : 0;
        }
        int ataque = switch (orden) {
            case "garra" -> GARRA;
            case "terremoto" -> TERREMOTO;
            case "sello" -> RUGIDO;
            case "cataclismo" -> CATACLISMO;
            case "salto" -> SALTO;
            case "embestida" -> EMBESTIDA_AVISO;
            case "tumba", "anillo" -> TUMBA;
            case "idolo" -> IDOLO;
            case "aturdido" -> ATURDIDO;
            case "paralizado" -> PARALIZADO;
            case "estampado" -> ESTAMPADO;
            default -> -1;
        };
        if (ataque < 0) {
            return false;
        }
        if (getEstado() == DORMIDO) {
            entityData.set(DATA_FASE, Math.max(1, fase()));
        }
        if (blanco != null) {
            setTarget(blanco);
            girarHacia(blanco.position(), 180.0F);
        }
        cancelarSello(nivel, false);
        rugidoFinal = false;
        ponerEstado(LIBRE, 0);
        switch (ataque) {
            case ATURDIDO -> {
                ponerEstado(ATURDIDO, RajangGeometria.DURACION_ATURDIDO);
                sonido(AtalayaSonidos.RAJANG_ATURDIDO, 5.0F);
            }
            case PARALIZADO -> {
                ponerEstado(PARALIZADO, RajangGeometria.DURACION_PARALIZADO);
                sonido(AtalayaSonidos.RAJANG_PARALIZADO, 5.0F);
            }
            case ESTAMPADO -> estampar(nivel);
            default -> iniciar(nivel, ataque, blanco);
        }
        return true;
    }

    // ------------------------------------------------------------------
    //  Dormido y despertar
    // ------------------------------------------------------------------

    private void tickDormido(ServerLevel nivel) {
        if (t % 5 != 0) {
            return;
        }
        for (Player p : jugadores(nivel, RANGO_DESPERTAR, 0)) {
            // Lo ve desde los ojos, el pecho o las rodillas, o lo tiene muy cerca.
            if (PresasJefe.despierta(nivel, this, p)) {
                despertarse(p);
                return;
            }
        }
    }

    private void despertarse(@Nullable Entity quien) {
        if (getEstado() != DORMIDO) {
            return;
        }
        if (quien instanceof LivingEntity vivo) {
            setTarget(vivo);
        }
        ponerEstado(DESPERTAR, RajangGeometria.DURACION_DESPERTAR);
        // Respira hondo, aun dormido (el resto suena con cada paso del despertar).
        sonido(AtalayaSonidos.RAJANG_AMBIENTE, 5.0F);
    }

    /**
     * Cuando suena despertar.ogg: la piedra que muele, la costra que se raja, los
     * glifos y, a los 2,75 s (55 ticks), el rugido, que asi cae en DESPERTAR_RUGE.
     */
    private static final int DESPERTAR_SUENA = RajangGeometria.DESPERTAR_RUGE - 55;

    /**
     * El despertar de la presentacion (los tiempos, en RajangGeometria): respira
     * cada vez mas hondo; abre los ojos y grune; saca las manos de la tierra y se
     * estira; se agazapa con la cresta erizada; y se alza y ruge.
     */
    private void tickDespertar(ServerLevel nivel) {
        if (t == 1) {
            jugadoresGrupo = Math.max(1, jugadores(nivel, 80, 0).size());
            factorGrupo = VIDA_VANILLA / VIDA;
            setHealth(getMaxHealth());
            entityData.set(DATA_FASE, 1);
        }
        if (t == RajangGeometria.DESPERTAR_ABRE) {
            // Se le encienden los ojos y grune por lo bajo.
            sonido(AtalayaSonidos.RAJANG_GRUNIDO, 5.0F);
            Vec3 c = puntoMundo(RajangGeometria.cabezaDespertar(t));
            nivel.sendParticles(AtalayaParticulas.RAJANG_CHISPA, true, true, c.x, c.y, c.z, 12, 0.8, 0.4, 0.8, 0.02);
        }
        if (t == RajangGeometria.DESPERTAR_SE_ALZA) {
            // Se pone en pie: la piedra cruje y se le cae el polvo de siglos.
            sonido(AtalayaSonidos.RAJANG_ESCALON_TIEMBLA, 6.0F);
            Vec3 c = puntoMundo(RajangGeometria.LOMO);
            nivel.sendParticles(AtalayaParticulas.RAJANG_POLVO, true, true, c.x, c.y - 3.0, c.z, 60, 4.0, 1.5, 6.0, 0.04);
            nivel.sendParticles(AtalayaParticulas.RAJANG_HOJA, true, true, c.x, c.y - 1.0, c.z, 30, 4.0, 1.0, 6.0, 0.02);
        }
        if (t == RajangGeometria.DESPERTAR_SE_ALZA + 6) {
            // Las manos salen de la tierra, delante de el.
            golpeSuelo(nivel, puntoMundo(RajangGeometria.MANOS_DESPERTAR), 1.2F, 10.0F, 20);
        }
        if (t == DESPERTAR_SUENA) {
            sonido(AtalayaSonidos.RAJANG_DESPERTAR, 8.0F);
        }
        if (t == RajangGeometria.DESPERTAR_ALZADO) {
            // Agazapado, grune con la cabeza baja.
            sonido(AtalayaSonidos.RAJANG_GRUNIDO, 6.0F);
        }
        if (t == RajangGeometria.DESPERTAR_ALZADO + 8) {
            // La cresta se eriza: le salta el jade del lomo.
            Vec3 c = puntoMundo(RajangGeometria.LOMO);
            nivel.sendParticles(AtalayaParticulas.RAJANG_JADE, true, true, c.x, c.y, c.z, 30, 1.0, 0.6, 4.5, 0.05);
        }
        if (t == RajangGeometria.DESPERTAR_RUGE) {
            // El rugido ya no empuja: en la presentacion el jefe no golpea.
            Vec3 b = puntoMundo(RajangGeometria.cabezaDespertar(t));
            nivel.sendParticles(AtalayaParticulas.RAJANG_ONDA, true, true, b.x, getY() + 0.1, b.z, 0, 2.6, 18.0, 0.0, 1.0);
            nivel.sendParticles(AtalayaParticulas.RAJANG_CHISPA, true, true, b.x, b.y, b.z, 30, 1.0, 1.0, 1.0, 0.15);
        }
        if (t == RajangGeometria.DESPERTAR_APOYA) {
            // Vuelve a apoyar las manos.
            sonido(AtalayaSonidos.RAJANG_PASO, 6.0F);
            golpeSuelo(nivel, puntoMundo(new Vec3(0.0, 0.0, RajangGeometria.ZARPA_IZQ.z)), 0.7F, 8.0F, 12);
        }
    }

    // ------------------------------------------------------------------
    //  Garra Terrestre: el zarpazo (tres garras que cortan el aire delante
    //  de el) y, por donde rayan el suelo, una fila de pinchos de roca que
    //  revienta hasta su presa, cada uno mas grande
    // ------------------------------------------------------------------

    private void tickGarra(ServerLevel nivel) {
        if (presa != null && presa.isAlive() && ta() < RajangGeometria.GARRA_GOLPE - 3) {
            destino = presa.position();
        }
        if (destino != null && ta() < RajangGeometria.GARRA_GOLPE) {
            girarHacia(destino, 12.0F);
        }
        if (cruza(RajangGeometria.GARRA_ALZA)) {
            sonido(AtalayaSonidos.RAJANG_GARRA_ALZA, 4.0F);
        }
        // El aviso: la grieta que corre por el suelo hacia la presa y el aro
        // donde va a salir el ultimo pico.
        if (destino != null && (t <= avisoEstado || ta() >= RajangGeometria.GARRA_ALZA)
                && ta() < RajangGeometria.GARRA_GOLPE && t % 2 == 0) {
            Vec3 desde = puntoMundo(RajangGeometria.ZARPA_GARRA);
            double y0 = sueloBajo(nivel, destino.x, destino.y + 2, destino.z);
            // En la espera de aviso la grieta se queda en la zarpa (k = 0) y el aro ya marca el sitio.
            float k = Mth.clamp((ta() - RajangGeometria.GARRA_ALZA)
                    / Math.max(1.0F, RajangGeometria.GARRA_GOLPE - RajangGeometria.GARRA_ALZA), 0.0F, 1.0F);
            Vec3 p = desde.lerp(new Vec3(destino.x, y0, destino.z), k);
            nivel.sendParticles(AtalayaParticulas.RAJANG_GRIETA, true, true, p.x, sueloBajo(nivel, p.x, p.y + 2, p.z) + 0.06, p.z,
                    0, 1.6, 40.0, 0.0, 1.0);
            if (t % 6 == 0 || t == 2) {
                nivel.sendParticles(AtalayaParticulas.RAJANG_AVISO, true, true, destino.x, y0 + 0.07, destino.z, 0, 2.8, 16.0, 0.0, 1.0);
            }
        }
        if (!cruza(RajangGeometria.GARRA_GOLPE) || destino == null) {
            return;
        }
        sonido(AtalayaSonidos.RAJANG_ZARPAZO, 6.0F);
        sonido(AtalayaSonidos.RAJANG_GARRA_GOLPE, 5.0F);
        sonido(AtalayaSonidos.RAJANG_GRIETA, 5.0F);
        zarpazo(nivel);
        Vec3 desde = puntoMundo(RajangGeometria.ZARPA_GARRA);
        golpeSuelo(nivel, new Vec3(desde.x, sueloBajo(nivel, desde.x, desde.y + 2, desde.z), desde.z), 1.8F, 9.0F, 30);
        Vec3 dir = horizontalHacia(desde, destino);
        double largo = Math.min(ALCANCE_GARRA, horizontal(desde, destino) + 1.5);
        int n = Math.max(4, (int) Math.round(largo / 2.6));
        float rumbo = (float) (Mth.atan2(dir.z, dir.x) * Mth.RAD_TO_DEG) - 90.0F;
        for (int i = 0; i < n; i++) {
            double k = (i + 1.0) / n;
            double x = desde.x + dir.x * largo * k + (random.nextDouble() - 0.5) * 0.6;
            double z = desde.z + dir.z * largo * k + (random.nextDouble() - 0.5) * 0.6;
            double tam = i == n - 1 ? 1.0 : 0.3 + 0.55 * Math.pow(k, 1.4);
            picos.add(new double[]{tickCount + 1 + i * 2, x, z, tam, rumbo});
        }
    }

    /**
     * El zarpazo: tres garras de luz que cortan el aire delante de el, de
     * arriba a su derecha a abajo a su izquierda, y rayan el suelo. A quien
     * pille delante (hasta 13 bloques, en un abanico de 125 grados) le pega y
     * lo empuja unos 6 bloques, lejos de el y casi sin levantarlo.
     */
    private void zarpazo(ServerLevel nivel) {
        Vec3 f = frente();
        Vec3 izq = new Vec3(f.z, 0, -f.x);
        Vec3 c = position().add(f.scale(9.0)).add(0, 3.6, 0);
        nivel.sendParticles(AtalayaParticulas.RAJANG_ZARPAZO, true, true, c.x, c.y, c.z, 0, 21.0, 9.0, -0.6, 1.0);
        nivel.sendParticles(AtalayaParticulas.RAJANG_JADE, true, true, c.x, c.y - 1.0, c.z, 16, 2.8, 1.4, 2.8, 0.25);
        nivel.sendParticles(AtalayaParticulas.RAJANG_CHISPA, true, true, c.x, c.y, c.z, 24, 3.0, 1.6, 3.0, 0.12);
        // Las tres zarpas rayan el suelo: las marcas tumbadas, a lo ancho delante de el.
        Vec3 m = position().add(f.scale(8.5));
        double ym = sueloBajo(nivel, m.x, getY() + 3, m.z);
        double giro = Math.atan2(f.x, f.z);
        nivel.sendParticles(AtalayaParticulas.RAJANG_ZARPAZO, true, true, m.x, ym + 0.07, m.z, 0, 15.0, 80.0, 100.0 + giro, 1.0);
        for (int k = -2; k <= 2; k++) {
            Vec3 p = m.add(izq.scale(k * 2.4));
            nivel.sendParticles(AtalayaParticulas.RAJANG_POLVO, true, true, p.x, ym + 0.3, p.z, 3, 0.6, 0.1, 0.6, 0.05);
            nivel.sendParticles(AtalayaParticulas.RAJANG_ROCA, true, true, p.x, ym + 0.3, p.z, 2, 0.4, 0.1, 0.4, 0.2);
        }
        DamageSource fuente = RajangDanos.fuente(nivel, RajangDanos.GARRA, this, this);
        float dano = dano(DANO_GARRA);
        for (LivingEntity v : nivel.getEntitiesOfClass(LivingEntity.class, getBoundingBox().inflate(14, 6, 14), this::esPresa)) {
            double dx = v.getX() - getX();
            double dz = v.getZ() - getZ();
            double d = Math.sqrt(dx * dx + dz * dz);
            if (d > 13.0 || d < 0.5 || (dx * f.x + dz * f.z) / d < 0.45 || v.getY() > getY() + 9.0) {
                continue;
            }
            v.hurtServer(nivel, fuente, contraArmadura(v, dano));
            lanzar(v, new Vec3(dx / d, 0, dz / d).scale(GARRA_EMPUJE), 0.3);
            nivel.sendParticles(AtalayaParticulas.RAJANG_CHISPA, true, true, v.getX(), v.getY() + 1.0, v.getZ(), 10, 0.3, 0.5, 0.3, 0.12);
            if (idoloQueda > 0 && v == portador) {
                recuperarIdolo(nivel, portador);
            }
        }
    }

    /** Los picos de la Garra salen uno tras otro, como una ola de roca. */
    private void tickPicos(ServerLevel nivel) {
        if (picos.isEmpty()) {
            return;
        }
        List<double[]> salen = new ArrayList<>();
        for (double[] p : picos) {
            if (p[0] <= tickCount) {
                salen.add(p);
            }
        }
        picos.removeAll(salen);
        for (double[] p : salen) {
            double y = sueloBajo(nivel, p[1], getY() + 4, p[2]);
            PicoTierraEntity.brotar(nivel, this, new Vec3(p[1], y, p[2]), (float) p[3], (float) p[4], dano(DANO_GARRA));
        }
    }

    // ------------------------------------------------------------------
    //  Terremoto Ancestral: golpe con las dos zarpas, la onda, los pilares al
    //  azar, el lastre para todos y la Piel de Jade para el
    // ------------------------------------------------------------------

    private void tickTerremoto(ServerLevel nivel) {
        LivingEntity objetivo = getTarget();
        if (objetivo != null && ta() < RajangGeometria.TERREMOTO_GOLPE) {
            girarHacia(objetivo.position(), 6.0F);
        }
        if (!cruza(RajangGeometria.TERREMOTO_GOLPE)) {
            return;
        }
        sonido(AtalayaSonidos.RAJANG_TERREMOTO, 8.0F);
        sonido(AtalayaSonidos.RAJANG_ONDA, 6.0F);
        Vec3 c = puntoMundo(RajangGeometria.ZARPA_IZQ_TERREMOTO).lerp(puntoMundo(RajangGeometria.ZARPA_DER_TERREMOTO), 0.5);
        double y0 = sueloBajo(nivel, c.x, c.y + 2, c.z);
        golpeSuelo(nivel, new Vec3(c.x, y0, c.z), 3.0F, 18.0F, 60);
        nivel.sendParticles(AtalayaParticulas.RAJANG_ONDA, true, true, c.x, y0 + 0.14, c.z, 0, 1.6, 34.0, 0.0, 1.0);
        for (int k = 0; k < 9; k++) {
            double a = Math.PI * 2 * k / 9 + random.nextDouble() * 0.4;
            for (int j = 1; j < 7; j++) {
                double r = 2.0 + j * 2.0;
                double x = c.x + Math.cos(a) * r;
                double z = c.z + Math.sin(a) * r;
                nivel.sendParticles(AtalayaParticulas.RAJANG_GRIETA, true, true, x, sueloBajo(nivel, x, y0 + 3, z) + 0.06, z,
                        0, 1.8, 120.0, 0.0, 1.0);
            }
        }
        // El lastre: la tierra tira de todos los que pisan su templo.
        for (Player p : jugadores(nivel, 40, 0)) {
            p.addEffect(new MobEffectInstance(PesoTierraEffect.PESO, PESO_TICKS, 0, false, true, true), this);
            nivel.sendParticles(AtalayaParticulas.RAJANG_LASTRE, true, true, p.getX(), p.getY() + 0.06, p.getZ(), 0, 1.4, PESO_TICKS,
                    0.0, 1.0);
        }
        sonido(AtalayaSonidos.RAJANG_LASTRE, 4.0F);
        // La Piel de Jade.
        piel = PIEL_TICKS;
        entityData.set(DATA_PIEL, true);
        sonido(AtalayaSonidos.RAJANG_PIEL_JADE, 5.0F);
        // Los pilares: unos bajo los pies de los jugadores, otros al azar por la plaza.
        int n = Math.min(16, 6 + jugadoresGrupo / 4 + (fase() - 1));
        List<Player> ps = jugadores(nivel, 44, 0);
        Vec3 cen = Vec3.atBottomCenterOf(centro);
        for (int i = 0; i < n; i++) {
            Vec3 p;
            if (i < n / 2 && !ps.isEmpty()) {
                Player pl = ps.get(i % ps.size());
                double a = random.nextDouble() * Math.PI * 2;
                double d = random.nextDouble() * 2.5;
                p = new Vec3(pl.getX() + Math.cos(a) * d, pl.getY(), pl.getZ() + Math.sin(a) * d);
            } else {
                double a = random.nextDouble() * Math.PI * 2;
                double d = 7.0 + random.nextDouble() * 28.0;
                p = new Vec3(cen.x + Math.cos(a) * d, getY(), cen.z + Math.sin(a) * d);
            }
            double y = sueloBajo(nivel, p.x, p.y + 4, p.z);
            // Pilares de 0,95 a 1,45: pegan a 2,5-3,2 bloques de su centro.
            PilarTierraEntity.avisar(nivel, this, new Vec3(p.x, y, p.z), 0.95F + random.nextFloat() * 0.5F, 6 + i * 3,
                    dano(DANO_TERREMOTO));
        }
    }

    // ------------------------------------------------------------------
    //  Sello de la Tierra: cuatro columnas de roca con un totem encima y
    //  piedras flotando en espiral para subir; si no caen a tiempo, el
    //  Rugido de Jade
    // ------------------------------------------------------------------

    private void tickRugido(ServerLevel nivel) {
        if (!cruza(RajangGeometria.RUGIDO_RUGE)) {
            return;
        }
        if (rugidoFinal) {
            rugidoDeJade(nivel);
            return;
        }
        Vec3 b = puntoMundo(RajangGeometria.BOCA_RUGIDO);
        nivel.sendParticles(AtalayaParticulas.RAJANG_ONDA, true, true, b.x, getY() + 0.1, b.z, 0, 2.2, 22.0, 0.0, 1.0);
        nivel.sendParticles(AtalayaParticulas.RAJANG_CHISPA, true, true, b.x, b.y, b.z, 40, 1.2, 1.2, 1.2, 0.2);
        for (Player p : jugadores(nivel, 14, 0)) {
            Vec3 fuera = horizontalHacia(position(), p.position());
            p.setDeltaMovement(fuera.x * 1.1, 0.4, fuera.z * 1.1);
            p.hurtMarked = true;
        }
        planearSello(nivel);
    }

    /**
     * Las cuatro columnas alrededor de el, en sus diagonales (lejos de la
     * cabeza y de la cola), y alrededor de cada una su espiral de piedras: la
     * primera a un bloque del suelo, mirando hacia el, y cada una un bloque
     * mas alta, hasta la que deja saltar arriba.
     */
    private void planearSello(ServerLevel nivel) {
        cancelarSello(nivel, false);
        Vec3 c = position();
        Vec3 f = frente();
        double giro = Math.atan2(f.z, f.x) + Math.PI / 4;
        double sube = SELLO_ALTO / (SELLO_PIEDRAS + 1.0);
        // Cada totem aguanta 10 golpes, sean cuantos sean los jugadores.
        int aguanta = 10;
        for (int i = 0; i < 4; i++) {
            double a = giro + i * Math.PI / 2;
            double x = c.x + Math.cos(a) * SELLO_RADIO;
            double z = c.z + Math.sin(a) * SELLO_RADIO;
            double y0 = sueloBajo(nivel, x, c.y + 10, z);
            int retraso = i * 5;
            plataformas.add(PlataformaSelloEntity.columna(nivel, this, new Vec3(x, y0, z), SELLO_ANCHO, SELLO_ALTO, retraso));
            int arriba = PlataformaSelloEntity.AVISO + retraso + PlataformaSelloEntity.SUBE;
            double a0 = a + Math.PI + (random.nextDouble() - 0.5) * 0.8;
            double sentido = random.nextBoolean() ? 1.0 : -1.0;
            for (int k = 0; k < SELLO_PIEDRAS; k++) {
                double ak = a0 + sentido * k * PIEDRA_GIRO;
                Vec3 p = new Vec3(x + Math.cos(ak) * PIEDRA_RADIO, y0, z + Math.sin(ak) * PIEDRA_RADIO);
                plataformas.add(PlataformaSelloEntity.piedra(nivel, this, p, y0 + sube * (k + 1), PIEDRA_ANCHO, arriba + 4 + k * 3, i, k));
            }
            totemsPendientes.add(new double[]{tickCount + arriba + 2, x, y0 + SELLO_ALTO, z, i, aguanta});
        }
        nivel.playSound(null, c.x, c.y, c.z, AtalayaSonidos.RAJANG_COLUMNA, SoundSource.HOSTILE, 8.0F, 1.0F);
    }

    /** Saca cada totem cuando su columna ya esta arriba; y al bajar, que nadie se rompa las piernas. */
    private void tickPiezasSello(ServerLevel nivel) {
        if (!totemsPendientes.isEmpty() && getEstado() == SELLO) {
            List<double[]> salen = new ArrayList<>();
            for (double[] p : totemsPendientes) {
                if (p[0] <= tickCount) {
                    salen.add(p);
                    totems.add(TotemSelloEntity.alzar(nivel, this, new Vec3(p[1], p[2], p[3]), (int) p[4], (int) p[5]));
                }
            }
            totemsPendientes.removeAll(salen);
        }
        plataformas.removeIf(Entity::isRemoved);
        if (sinCaida > 0) {
            sinCaida--;
            for (Player p : jugadores(nivel, 60, 0)) {
                p.resetFallDistance();
            }
        }
    }

    private void empezarSello(ServerLevel nivel) {
        ponerEstado(SELLO, SELLO_TICKS);
        entityData.set(DATA_SELLO, SELLO_TICKS);
        entityData.set(DATA_TOTEMS, 0);
    }

    private void tickSello(ServerLevel nivel) {
        Player cerca = nivel.getNearestPlayer(this, 64);
        if (cerca != null) {
            girarHacia(cerca.position(), 3.0F);
        }
        entityData.set(DATA_SELLO, Math.max(1, duracion - t));
        int queda = duracion - t;
        if (queda <= 100 && queda % 20 == 0) {
            sonido(AtalayaSonidos.RAJANG_RELOJ, 5.0F);
        }
        // La escalera no se queda quieta: cada poco tiembla un escalon y se cae.
        if (t >= 60 && t - ultimoEscalon >= ESCALON_CADA) {
            temblarEscalon(nivel);
        }
    }

    /**
     * Un escalon al azar empieza a temblar (y un segundo despues se cae; vuelve a
     * los tres). Nunca de las tres de abajo, que no tendria gracia, ni dos a la
     * vez en la misma columna.
     */
    private void temblarEscalon(ServerLevel nivel) {
        ultimoEscalon = t;
        java.util.Set<Integer> ocupadas = new java.util.HashSet<>();
        List<PlataformaSelloEntity> libres = new ArrayList<>();
        for (PlataformaSelloEntity p : plataformas) {
            if (p.getTipo() == PlataformaSelloEntity.PIEDRA && p.enCaida()) {
                ocupadas.add(p.getColumna());
            }
        }
        for (PlataformaSelloEntity p : plataformas) {
            if (p.getTipo() == PlataformaSelloEntity.PIEDRA && p.firme() && p.getEscalon() >= 3 && !ocupadas.contains(p.getColumna())) {
                libres.add(p);
            }
        }
        if (!libres.isEmpty()) {
            libres.get(random.nextInt(libres.size())).temblar(nivel);
        }
    }

    /** Un totem roto (lo avisa el propio totem). */
    public void alRomperTotem(ServerLevel nivel, TotemSelloEntity tot) {
        if (getEstado() != SELLO) {
            return;
        }
        pulsoTotem(nivel, tot);
        entityData.set(DATA_TOTEMS, getTotemsRotos() | (1 << tot.getIndice()));
        boolean todos = totems.size() == 4;
        for (TotemSelloEntity x : totems) {
            todos &= x.isRoto();
        }
        if (todos) {
            // El sello se rompe: las columnas se hunden y el cae aturdido. Lo han
            // derribado: si tenia la Furia, se le va.
            cancelarSello(nivel, true);
            ponerEstado(ATURDIDO, RajangGeometria.DURACION_ATURDIDO);
            sonido(AtalayaSonidos.RAJANG_ATURDIDO, 6.0F);
            sonido(AtalayaSonidos.RAJANG_RUGIDO, 5.0F);
            ponerFuria(nivel, false);
        }
    }

    /**
     * El pulso de tierra de un totem roto: dano a quien este cerca (la cima y las
     * piedras de arriba) y un empujon fuerte en horizontal que lo echa de la
     * columna. No alza: solo un saltito para despegarlo del suelo, que si no el
     * roce lo frena en dos bloques.
     */
    private void pulsoTotem(ServerLevel nivel, TotemSelloEntity tot) {
        Vec3 c = tot.position();
        nivel.playSound(null, c.x, c.y + 1, c.z, AtalayaSonidos.RAJANG_TOTEM_PULSO, SoundSource.HOSTILE, 5.0F, 1.0F);
        nivel.sendParticles(AtalayaParticulas.RAJANG_ONDA, true, true, c.x, c.y + 0.15, c.z, 0, 1.8, PULSO_RADIO, 0.0, 1.0);
        nivel.sendParticles(AtalayaParticulas.RAJANG_ROCA, true, true, c.x, c.y + 1.0, c.z, 30, 2.0, 0.6, 2.0, 0.4);
        nivel.sendParticles(AtalayaParticulas.RAJANG_POLVO, true, true, c.x, c.y + 0.5, c.z, 24, 2.5, 0.4, 2.5, 0.1);
        DamageSource fuente = RajangDanos.fuente(nivel, RajangDanos.PULSO, tot, this);
        float dano = dano(DANO_TERREMOTO);
        for (LivingEntity v : nivel.getEntitiesOfClass(LivingEntity.class, new AABB(c, c).inflate(PULSO_RADIO, 5.0, PULSO_RADIO),
                this::esPresa)) {
            if (horizontal(c, v.position()) > PULSO_RADIO) {
                continue;
            }
            v.hurtServer(nivel, fuente, contraArmadura(v, dano));
            Vec3 fuera = horizontalHacia(c, v.position());
            v.setDeltaMovement(fuera.x * PULSO_EMPUJE, 0.12, fuera.z * PULSO_EMPUJE);
            v.hurtMarked = true;
        }
    }

    /** La Furia de Jade: el aura verde (y su rugido al prenderse) o se le apaga. */
    /** Lo que le queda de Furia (ticks, servidor). */
    private int furiaQueda;

    private void ponerFuria(ServerLevel nivel, boolean si) {
        if (tieneFuria() == si) {
            return;
        }
        entityData.set(DATA_FURIA, si);
        // Dura 30 s y mientras es inmune: solo toca esquivar (testers, 07-10-2026).
        furiaQueda = si ? PresasJefe.FURIA_TICKS : 0;
        entityData.set(DATA_FURIA_FIN, si ? nivel.getGameTime() + PresasJefe.FURIA_TICKS : 0L);
        PresasJefe.avisarFuria(nivel, this, si);
        Vec3 c = puntoMundo(RajangGeometria.PECHO);
        if (si) {
            sonido(AtalayaSonidos.RAJANG_FURIA, 8.0F);
            nivel.sendParticles(AtalayaParticulas.RAJANG_LLAMA, true, true, c.x, c.y, c.z, 60, 3.0, 3.0, 5.0, 0.15);
            nivel.sendParticles(AtalayaParticulas.RAJANG_ONDA, true, true, getX(), getY() + 0.1, getZ(), 0, 2.0, 24.0, 0.0, 1.0);
        } else {
            nivel.sendParticles(AtalayaParticulas.RAJANG_POLVO, true, true, c.x, c.y, c.z, 30, 3.0, 2.0, 5.0, 0.05);
        }
    }

    /** El Rugido de Jade: ruge con toda la tierra y la onda verde mata a todos en su rango; las columnas se hunden. */
    private void rugidoDeJade(ServerLevel nivel) {
        sonido(AtalayaSonidos.RAJANG_RUGIDO_JADE, 10.0F);
        Vec3 b = puntoMundo(RajangGeometria.BOCA_RUGIDO);
        double y0 = sueloBajo(nivel, getX(), getY() + 3, getZ());
        nivel.sendParticles(AtalayaParticulas.RAJANG_ONDA, true, true, getX(), y0 + 0.15, getZ(), 0, 3.5, 60.0, 0.0, 1.0);
        nivel.sendParticles(AtalayaParticulas.RAJANG_ONDA, true, true, getX(), y0 + 0.2, getZ(), 0, 2.2, 36.0, 0.0, 1.0);
        nivel.sendParticles(AtalayaParticulas.RAJANG_CHISPA, true, true, b.x, b.y, b.z, 70, 1.6, 1.6, 1.6, 0.35);
        nivel.sendParticles(AtalayaParticulas.RAJANG_JADE, true, true, b.x, b.y, b.z, 40, 1.2, 1.2, 1.2, 0.3);
        DamageSource fuente = RajangDanos.fuente(nivel, RajangDanos.RUGIDO, this, this);
        for (LivingEntity v : nivel.getEntitiesOfClass(LivingEntity.class, getBoundingBox().inflate(64, 32, 64), this::esPresa)) {
            Vec3 fuera = horizontalHacia(position(), v.position());
            v.hurtServer(nivel, fuente, MORTAL);
            v.setDeltaMovement(fuera.x * 1.6, 0.7, fuera.z * 1.6);
            v.hurtMarked = true;
            nivel.sendParticles(AtalayaParticulas.RAJANG_CHISPA, true, true, v.getX(), v.getY() + 1, v.getZ(), 10, 0.4, 0.6, 0.4, 0.1);
        }
        cancelarSello(nivel, true);
        // Y a los que queden se lo encuentran con la Furia.
        ponerFuria(nivel, true);
    }

    /**
     * Quita los totems y hunde las columnas y las piedras (o las quita de
     * golpe). El Sello no vuelve hasta dos minutos despues de acabar (algo menos
     * en las ultimas fases): el enfriamiento cuenta desde aqui, no desde que empezo.
     */
    private void cancelarSello(ServerLevel nivel, boolean poco_a_poco) {
        enfSello = Math.max(enfSello, (int) (SELLO_DESCANSO * enfriamiento()));
        for (TotemSelloEntity tot : totems) {
            tot.desmontar(nivel);
        }
        totems.clear();
        totemsPendientes.clear();
        entityData.set(DATA_SELLO, 0);
        entityData.set(DATA_TOTEMS, 0);
        if (plataformas.isEmpty()) {
            return;
        }
        for (PlataformaSelloEntity p : plataformas) {
            if (poco_a_poco) {
                p.irse(nivel);
            } else {
                p.discard();
            }
        }
        plataformas.clear();
        if (poco_a_poco) {
            sinCaida = 100;
            sonido(AtalayaSonidos.RAJANG_PLATAFORMA, 6.0F);
        }
    }

    // ------------------------------------------------------------------
    //  Cataclismo de Jade: se alza, ruge al cielo y llueven fragmentos
    // ------------------------------------------------------------------

    private void tickCataclismo(ServerLevel nivel) {
        if (!cruza(RajangGeometria.CATACLISMO_RUGE)) {
            return;
        }
        sonido(AtalayaSonidos.RAJANG_CIELO, 10.0F);
        // El cielo se raja: una grieta de luz verde muy alta.
        Vec3 c = Vec3.atBottomCenterOf(centro).add(0, 46, 0);
        double x = c.x - 24;
        double z = c.z + (random.nextDouble() - 0.5) * 8;
        for (int k = 0; k < 40; k++) {
            x += 1.2;
            z += (random.nextDouble() - 0.5) * 2.4;
            nivel.sendParticles(AtalayaParticulas.RAJANG_LLAMA, true, true, x, c.y + (random.nextDouble() - 0.5) * 2, z, 3, 0.3, 0.3, 0.3, 0.02);
        }
        Vec3 b = puntoMundo(RajangGeometria.BOCA_CATACLISMO);
        nivel.sendParticles(AtalayaParticulas.RAJANG_ONDA, true, true, getX(), getY() + 0.1, getZ(), 0, 2.4, 20.0, 0.0, 1.0);
        nivel.sendParticles(AtalayaParticulas.RAJANG_CHISPA, true, true, b.x, b.y, b.z, 40, 1.0, 1.0, 1.0, 0.25);
    }

    private void tickOleadas(ServerLevel nivel) {
        if ((t - 1) % CADA_OLEADA != 0 || t > OLEADAS * CADA_OLEADA) {
            return;
        }
        // Una marca bajo cada jugador y otras al azar por el templo.
        List<Vec3> blancos = new ArrayList<>();
        for (Player p : jugadores(nivel, 60, 0)) {
            blancos.add(p.position());
        }
        if (blancos.isEmpty() && getTarget() != null) {
            blancos.add(getTarget().position());
        }
        Vec3 c = Vec3.atBottomCenterOf(centro);
        // Fragmentos grandes y pocos: cada uno tapa unas siete veces el suelo de antes
        // (4,8-5,7 bloques de radio), asi que los que caen al azar son un tercio de los
        // de antes; aun en la oleada mas llena tapan como un tercio del templo.
        // El de cada jugador se queda.
        int extra = Math.min(14, 3 + jugadoresGrupo / 6 + fase());
        for (int i = 0; i < extra; i++) {
            double a = random.nextDouble() * Math.PI * 2;
            double d = 6.0 + random.nextDouble() * 30.0;
            blancos.add(new Vec3(c.x + Math.cos(a) * d, c.y, c.z + Math.sin(a) * d));
        }
        for (Vec3 p : blancos) {
            double y = sueloBajo(nivel, p.x, p.y + 3, p.z);
            float tam = 2.3F + random.nextFloat() * 0.4F;
            nivel.sendParticles(AtalayaParticulas.RAJANG_MARCA, true, true, p.x, y + 0.08, p.z, 0,
                    FragmentoJadeEntity.radioMuerte(tam) + 0.6, RETRASO_FRAGMENTO + AVISO_FRAGMENTO, 0.0, 1.0);
            fragmentosPendientes.add(new FragmentoPendiente(new Vec3(p.x, y, p.z), tam, tickCount + RETRASO_FRAGMENTO));
        }
        nivel.playSound(null, getX(), getY() + 10, getZ(), AtalayaSonidos.RAJANG_MARCA, SoundSource.HOSTILE, 6.0F, 1.0F);
        sonido(AtalayaSonidos.RAJANG_RUGIDO, 5.0F);
    }

    /** Suelta los fragmentos a los que ya les toca caer (aunque el ya este en otra cosa: su marca ya esta en el suelo). */
    private void soltarFragmentos(ServerLevel nivel) {
        if (fragmentosPendientes.isEmpty()) {
            return;
        }
        java.util.Iterator<FragmentoPendiente> it = fragmentosPendientes.iterator();
        while (it.hasNext()) {
            FragmentoPendiente f = it.next();
            if (tickCount >= f.cuando()) {
                FragmentoJadeEntity.caer(nivel, this, f.marca(), AVISO_FRAGMENTO, f.tam());
                it.remove();
            }
        }
    }

    /** Un fragmento ha matado a alguien: el Cataclismo se cobra su vida. */
    public void alMatar(LivingEntity victima) {
        if (victima instanceof Player) {
            mato = true;
        }
    }

    private void tickBaja(ServerLevel nivel) {
        if (!cruza(RajangGeometria.CATACLISMO_BAJA_GOLPE)) {
            return;
        }
        sonido(AtalayaSonidos.RAJANG_ATERRIZA, 7.0F);
        Vec3 c = puntoMundo(RajangGeometria.ZARPA_IZQ_TERREMOTO).lerp(puntoMundo(RajangGeometria.ZARPA_DER_TERREMOTO), 0.5);
        golpeSuelo(nivel, new Vec3(c.x, sueloBajo(nivel, c.x, c.y + 2, c.z), c.z), 2.6F, 16.0F, 50);
    }

    // ------------------------------------------------------------------
    //  El salto de la fase IV
    // ------------------------------------------------------------------

    /** Lo alto que llega en el salto (bloques) y la gravedad de ese vuelo (sale del tiempo que dura). */
    private static final double ALTURA_SALTO = 3.5;
    private double gravedadSalto = 0.1;

    private void tickSalto(ServerLevel nivel) {
        if (presa != null && presa.isAlive() && ta() < RajangGeometria.SALTO_DESPEGA) {
            girarHacia(presa.position(), 15.0F);
            destino = presa.position();
        }
        // Donde va a caer: el aro de aviso, desde que se agacha hasta que aterriza (testers: no se veia).
        if (destino != null && ta() < RajangGeometria.SALTO_ATERRIZA && t % 4 == 0) {
            double y0 = sueloBajo(nivel, destino.x, destino.y + 2, destino.z);
            nivel.sendParticles(AtalayaParticulas.RAJANG_AVISO, true, true, destino.x, y0 + 0.07, destino.z, 0, 6.5, 16.0,
                    0.0, 1.0);
        }
        if (cruza(RajangGeometria.SALTO_DESPEGA) && destino != null) {
            double vuelo = Math.max(6.0, (RajangGeometria.SALTO_ATERRIZA - RajangGeometria.SALTO_DESPEGA) / ritmoEstado);
            Vec3 desde = position();
            Vec3 meta = destino.subtract(frente().scale(2.0));
            double vx = (meta.x - desde.x) / vuelo;
            double vz = (meta.z - desde.z) / vuelo;
            // Una parabola que sube ALTURA_SALTO y cae justo al acabar el vuelo de la animacion.
            gravedadSalto = Math.max(0.08, 8.0 * ALTURA_SALTO / (vuelo * vuelo));
            double vy = 0.5 * gravedadSalto * vuelo + (meta.y - desde.y) / vuelo;
            setDeltaMovement(vx, vy, vz);
            saltando = true;
            sonido(AtalayaSonidos.RAJANG_SALTO, 6.0F);
            golpeSuelo(nivel, position(), 1.0F, 6.0F, 20);
        }
        if (saltando && cruza(RajangGeometria.SALTO_ATERRIZA)) {
            saltando = false;
            setDeltaMovement(0, Math.min(0, getDeltaMovement().y), 0);
            sonido(AtalayaSonidos.RAJANG_ATERRIZA, 8.0F);
            Vec3 c = puntoMundo(RajangGeometria.ZARPA_IZQ_TERREMOTO).lerp(puntoMundo(RajangGeometria.ZARPA_DER_TERREMOTO), 0.5);
            double y0 = sueloBajo(nivel, c.x, c.y + 3, c.z);
            golpeSuelo(nivel, new Vec3(c.x, y0, c.z), 2.8F, 14.0F, 60);
            DamageSource fuente = RajangDanos.fuente(nivel, RajangDanos.SALTO, this, this);
            for (LivingEntity v : nivel.getEntitiesOfClass(LivingEntity.class, new AABB(c, c).inflate(6.5, 4, 6.5), this::esPresa)) {
                if (horizontal(c, v.position()) > 6.5) {
                    continue;
                }
                v.hurtServer(nivel, fuente, contraArmadura(v, dano(DANO_SALTO)));
                Vec3 fuera = horizontalHacia(c, v.position());
                v.setDeltaMovement(fuera.x * 1.4, 0.6, fuera.z * 1.4);
                v.hurtMarked = true;
            }
            for (int k = 0; k < 6; k++) {
                double a = Math.PI * 2 * k / 6 + random.nextDouble() * 0.5;
                for (int j = 1; j < 4; j++) {
                    nivel.sendParticles(AtalayaParticulas.RAJANG_GRIETA, true, true, c.x + Math.cos(a) * j * 1.8, y0 + 0.06,
                            c.z + Math.sin(a) * j * 1.8, 0, 1.6, 80.0, 0.0, 1.0);
                }
            }
        }
    }

    /**
     * En el salto vuela con su propia gravedad; en la carga y la frenada va en
     * linea recta a su velocidad (sube escalones de dos bloques y cae si hay
     * hueco); en el resto, como cualquiera.
     */
    @Override
    public void travel(Vec3 entrada) {
        if (saltando) {
            Vec3 v = getDeltaMovement();
            move(MoverType.SELF, v);
            setDeltaMovement(v.x, v.y - gravedadSalto, v.z);
            return;
        }
        if (velCarga > 0.0) {
            double vy = onGround() ? -0.08 : getDeltaMovement().y - 0.08;
            Vec3 antes = position();
            move(MoverType.SELF, new Vec3(dirCarga.x * velCarga, vy, dirCarga.z * velCarga));
            avanceCarga = horizontal(antes, position());
            setDeltaMovement(0, onGround() ? 0 : vy * 0.98, 0);
            return;
        }
        super.travel(entrada);
    }

    // ------------------------------------------------------------------
    //  Embestida de Jade: se agazapa y rasca el suelo mientras la flecha
    //  se llena; carga en linea recta y a su paso revientan pinchos a los
    //  dos lados. Su cuerpo y los pinchos matan (salvo totem) y lanzan al
    //  cielo. Frena derrapando y jadea; contra un muro, se estampa
    // ------------------------------------------------------------------

    private void tickEmbestidaAviso(ServerLevel nivel) {
        // Sigue a su presa el primer segundo; luego el rumbo y el largo quedan fijos
        // hasta que carga (unos 2 s), y quien se aparte de la flecha se salva.
        if (presa != null && presa.isAlive() && t < EMBESTIDA_SIGUE) {
            girarHacia(presa.position(), 10.0F);
            double d = horizontal(puntoMundo(RajangGeometria.ZARPA_IZQ), presa.position());
            double largo = Mth.clamp((d + CARGA_PASA) * CARGA_VECES, CARGA_MIN, CARGA_MAX);
            entityData.set(DATA_CARGA, (float) Math.min(largo, flechaMaxima(frente())));
        } else if (getCarga() <= 0.0F) {
            entityData.set(DATA_CARGA, (float) Math.min(CARGA_MIN, flechaMaxima(frente())));
        }
        if (cruza(RajangGeometria.EMBESTIDA_RASCA_1) || cruza(RajangGeometria.EMBESTIDA_RASCA_2)) {
            Vec3 z = puntoMundo(RajangGeometria.ZARPA_RASCA);
            double y0 = sueloBajo(nivel, z.x, getY() + 2, z.z);
            nivel.playSound(null, z.x, y0, z.z, AtalayaSonidos.RAJANG_GRIETA, SoundSource.HOSTILE, 2.0F, 1.3F);
            nivel.sendParticles(AtalayaParticulas.RAJANG_ROCA, true, true, z.x, y0 + 0.3, z.z, 6, 0.5, 0.1, 0.5, 0.2);
            nivel.sendParticles(AtalayaParticulas.RAJANG_GRIETA, true, true, z.x, y0 + 0.06, z.z, 0, 1.2, 50.0, 0.0, 1.0);
        }
    }

    /**
     * Se acaba el aviso: el rumbo y el largo quedan fijos y sale disparado. La
     * flecha se mide desde sus manos, pero lo que corre es su pecho, con la cabeza
     * nueve bloques y medio por delante y unos dos de frenada: el pecho recorre la
     * flecha menos eso, para que lo que mata no pase de la punta que se ha visto.
     */
    private void empezarCarga(ServerLevel nivel) {
        dirCarga = frente();
        largoFlecha = Math.min(Math.max(CARGA_MIN, getCarga()), flechaMaxima(dirCarga));
        largoCarga = Math.max(4.0, largoFlecha - CARGA_CABEZA);
        recorrido = 0.0;
        avanceCarga = VEL_CARGA;
        siguientePincho = 1.0;
        arrollados.clear();
        ponerEstado(EMBESTIDA, (int) Math.ceil(largoCarga / VEL_CARGA) + 16);
        entityData.set(DATA_CARGA, (float) largoFlecha);
        velCarga = VEL_CARGA;
        sonido(AtalayaSonidos.RAJANG_EMBESTIDA, 8.0F);
        sonido(AtalayaSonidos.RAJANG_RUGIDO, 5.0F);
        golpeSuelo(nivel, position(), 1.4F, 8.0F, 30);
    }

    private void tickEmbestida(ServerLevel nivel) {
        recorrido += avanceCarga;
        // Contra un muro: lo que ha avanzado en el ultimo tick es casi nada, o la
        // cabeza (que va nueve bloques por delante de su caja) ya da en el.
        if (t > 1 && (horizontalCollision && avanceCarga < VEL_CARGA * 0.35 || muroDelante(nivel))) {
            estampar(nivel);
            return;
        }
        arrollar(nivel);
        while (recorrido >= siguientePincho) {
            pinchosCarga(nivel);
            siguientePincho += PINCHO_CADA;
        }
        entityData.set(DATA_CARGA, (float) Math.max(0.0, largoFlecha - recorrido));
        boolean fuera = centro != null && horizontal(position(), Vec3.atBottomCenterOf(centro)) > CORREA_CARGA + 2.0;
        if (recorrido >= largoCarga || fuera) {
            frenar(nivel);
        }
    }

    /** Su cuerpo, a la carrera: a lo que pille, la muerte (salvo totem) y al cielo. */
    private void arrollar(ServerLevel nivel) {
        Vec3 f = dirCarga;
        Vec3 izq = new Vec3(f.z, 0, -f.x);
        DamageSource fuente = RajangDanos.fuente(nivel, RajangDanos.EMBESTIDA, this, this);
        for (LivingEntity v : nivel.getEntitiesOfClass(LivingEntity.class, getBoundingBox().inflate(11, 3, 11), this::esPresa)) {
            if (arrollados.contains(v.getId())) {
                continue;
            }
            Vec3 d = v.position().subtract(position());
            double largo = d.x * f.x + d.z * f.z;
            double lado = Math.abs(d.x * izq.x + d.z * izq.z);
            if (largo < -7.0 || largo > 9.8 || lado > 3.4 + v.getBbWidth() * 0.5 || d.y < -1.5 || d.y > 8.0) {
                continue;
            }
            arrollados.add(v.getId());
            v.hurtServer(nivel, fuente, MORTAL);
            lanzar(v, f.scale(0.6), LANZA_MORTAL);
            lastrar(v, PESO_PINCHO);
            nivel.sendParticles(AtalayaParticulas.RAJANG_JADE, true, true, v.getX(), v.getY() + 1, v.getZ(), 12, 0.4, 0.6, 0.4, 0.2);
            nivel.playSound(null, v.getX(), v.getY(), v.getZ(), AtalayaSonidos.RAJANG_PICO_GOLPE, SoundSource.HOSTILE, 3.0F, 0.7F);
        }
    }

    /** A los dos lados de su camino, un pincho mortal cada uno. */
    private void pinchosCarga(ServerLevel nivel) {
        Vec3 f = dirCarga;
        Vec3 izq = new Vec3(f.z, 0, -f.x);
        float rumbo = (float) (Mth.atan2(f.z, f.x) * Mth.RAD_TO_DEG) - 90.0F;
        for (int lado = -1; lado <= 1; lado += 2) {
            Vec3 p = position().subtract(f.scale(1.0)).add(izq.scale(lado * (PINCHO_LADO + (random.nextDouble() - 0.5) * 0.4)));
            double y = sueloBajo(nivel, p.x, getY() + 4, p.z);
            float tam = 0.62F + random.nextFloat() * 0.16F;
            PicoTierraEntity.brotarMortal(nivel, this, new Vec3(p.x, y, p.z), tam, rumbo + lado * (60.0F + random.nextFloat() * 30.0F));
        }
    }

    private void frenar(ServerLevel nivel) {
        double v = velCarga;
        ponerEstado(EMBESTIDA_FRENA, RajangGeometria.DURACION_EMBESTIDA_FRENA);
        velCarga = Math.max(v, 0.6);
        entityData.set(DATA_CARGA, 0.0F);
        sonido(AtalayaSonidos.RAJANG_EMBESTIDA_FRENA, 6.0F);
    }

    /** Derrapa con las cuatro hasta pararse (aun arrolla mientras va deprisa) y jadea: la ventana para pegarle. */
    private void tickFrena(ServerLevel nivel) {
        if (velCarga > 0.0) {
            if (velCarga > 0.5) {
                arrollar(nivel);
            }
            velCarga *= 0.78;
            if (velCarga < 0.05 || t >= RajangGeometria.EMBESTIDA_FRENA_PARA) {
                velCarga = 0.0;
            }
        }
        if (t == RajangGeometria.EMBESTIDA_FRENA_PARA) {
            sonido(AtalayaSonidos.RAJANG_GRUNIDO, 3.0F);
        }
    }

    /** La Embestida contra un muro: se estampa y se queda 2 s aturdido (y recibe el doble). */
    private void estampar(ServerLevel nivel) {
        ponerEstado(ESTAMPADO, RajangGeometria.DURACION_ESTAMPADO);
        sonido(AtalayaSonidos.RAJANG_ESTAMPADO, 8.0F);
        Vec3 c = puntoMundo(RajangGeometria.CABEZA);
        nivel.sendParticles(AtalayaParticulas.RAJANG_ROCA, true, true, c.x, c.y, c.z, 30, 1.5, 1.5, 1.5, 0.35);
        nivel.sendParticles(AtalayaParticulas.RAJANG_POLVO, true, true, c.x, c.y, c.z, 30, 2.0, 1.5, 2.0, 0.08);
        nivel.sendParticles(AtalayaParticulas.RAJANG_JADE, true, true, c.x, c.y, c.z, 16, 1.0, 1.0, 1.0, 0.2);
        golpeSuelo(nivel, position(), 2.6F, 10.0F, 30);
    }

    private void tickEstampado(ServerLevel nivel) {
        if (t % 10 == 0) {
            Vec3 c = puntoMundo(RajangGeometria.CABEZA);
            nivel.sendParticles(AtalayaParticulas.RAJANG_POLVO, true, true, c.x, c.y, c.z, 4, 1.0, 0.6, 1.0, 0.02);
        }
    }

    /**
     * Hay un muro justo delante de la cabeza (a la altura del pecho y de la cara,
     * y a lo ancho de los sables). La caja de choque solo tapa el pecho: sin esto
     * se pararia con la cabeza metida cinco bloques en la pared.
     */
    private boolean muroDelante(ServerLevel nivel) {
        Vec3 f = dirCarga;
        Vec3 izq = new Vec3(f.z, 0, -f.x);
        for (double delante : new double[]{8.0, 9.6}) {
            for (double lado : new double[]{-1.8, 0.0, 1.8}) {
                for (double alto : new double[]{2.5, 4.5, 6.0}) {
                    Vec3 p = position().add(f.scale(delante)).add(izq.scale(lado)).add(0, alto, 0);
                    BlockPos b = BlockPos.containing(p);
                    if (!nivel.getBlockState(b).getCollisionShape(nivel, b).isEmpty()) {
                        return true;
                    }
                }
            }
        }
        return false;
    }

    /**
     * Lo mas larga que puede ser la flecha hacia 'f' sin que su pecho salga de
     * CORREA_CARGA (donde frena): el pecho corre la flecha menos CARGA_CABEZA.
     */
    private double flechaMaxima(Vec3 f) {
        if (centro == null) {
            return CARGA_MAX;
        }
        Vec3 c = Vec3.atBottomCenterOf(centro);
        double rx = getX() - c.x;
        double rz = getZ() - c.z;
        double b = rx * f.x + rz * f.z;
        double disc = b * b - (rx * rx + rz * rz) + CORREA_CARGA * CORREA_CARGA;
        double pecho = disc > 0.0 ? -b + Math.sqrt(disc) : 0.0;
        return Math.max(CARGA_CABEZA + 4.0, pecho + CARGA_CABEZA);
    }

    /** Hay linea limpia (sin bloques) desde el hasta su presa, a la altura del pecho y de los hombros. */
    /** El jugador mas lejano entre min y max bloques (con camino libre para cargar, si se pide). */
    private @Nullable Player masLejano(ServerLevel nivel, double min, double max, boolean conCamino) {
        // Del mas lejano al mas cercano: el camino (que cuesta mirar) solo se mira hasta dar con uno.
        List<Player> ps = jugadores(nivel, max, min);
        ps.sort(Comparator.comparingDouble((Player p) -> horizontal(position(), p.position())).reversed());
        for (Player p : ps) {
            if (!conCamino || caminoLibre(nivel, p)) {
                return p;
            }
        }
        return null;
    }

    /** Un aviso en la barra de accion a todos los que pelean. */
    private void avisar(ServerLevel nivel, Component texto) {
        for (Player p : jugadores(nivel, 64, 0)) {
            p.sendOverlayMessage(texto);
        }
    }

    private boolean caminoLibre(ServerLevel nivel, LivingEntity objetivo) {
        for (double h : new double[]{1.5, 4.0}) {
            Vec3 desde = position().add(0, h, 0);
            Vec3 hasta = new Vec3(objetivo.getX(), getY() + h, objetivo.getZ());
            if (nivel.clip(new ClipContext(desde, hasta, ClipContext.Block.COLLIDER, ClipContext.Fluid.NONE, this)).getType()
                    != HitResult.Type.MISS) {
                return false;
            }
        }
        return true;
    }

    /** Lo lanza al cielo (vy) con algo de empujon (horizontal); sin acumular la caida que ya llevara. */
    static void lanzar(LivingEntity v, Vec3 empuje, double vy) {
        v.resetFallDistance();
        v.setDeltaMovement(empuje.x, vy, empuje.z);
        v.hurtMarked = true;
    }

    // ------------------------------------------------------------------
    //  Tumba de Raices: clava las garras y ruge contra el suelo. Un circulo
    //  de 16 bloques se llena desde el en 3,5 s (siempre igual, sea la fase
    //  que sea) y el es inmune mientras tanto; al llenarse, lo que siga
    //  dentro muere (salvo totem) y el que se salve se queda con el Peso
    // ------------------------------------------------------------------

    private void tickTumba(ServerLevel nivel) {
        if (centroTumba == null) {
            // El circulo (el borde y lo llenado) lo pinta RajangRenderer bajo el: no se mueve en todo el ataque.
            centroTumba = new Vec3(getX(), sueloBajo(nivel, getX(), getY() + 3, getZ()), getZ());
            golpeSuelo(nivel, centroTumba, 1.2F, 8.0F, 30);
        }
        Vec3 c = centroTumba;
        if (t < RajangGeometria.TUMBA_ESTALLA) {
            if (t == RajangGeometria.TUMBA_RUGE_2) {
                // A mitad, toma aire y vuelve a rugir contra el suelo.
                sonido(AtalayaSonidos.RAJANG_TUMBA, 7.0F);
            }
            // Las raices avanzan: grietas y polvo en el frente del llenado (mas cuanto mas largo es).
            if (t % 4 == 0) {
                // En anillo, el frente va del borde hacia el.
                double avance = (double) t / RajangGeometria.TUMBA_ESTALLA;
                double r = isTumbaAnillo() ? TUMBA_RADIO - (TUMBA_RADIO - TUMBA_SEGURO) * avance : TUMBA_RADIO * avance;
                for (int k = 0; k < 2 + (int) (r / 6.0); k++) {
                    double a = random.nextDouble() * Math.PI * 2;
                    double x = c.x + Math.cos(a) * r;
                    double z = c.z + Math.sin(a) * r;
                    double y = sueloBajo(nivel, x, c.y + 3, z);
                    nivel.sendParticles(AtalayaParticulas.RAJANG_GRIETA, true, true, x, y + 0.06, z, 0, 1.4, 40.0, 0.0, 1.0);
                    nivel.sendParticles(AtalayaParticulas.RAJANG_POLVO, true, true, x, y + 0.3, z, 2, 0.4, 0.1, 0.4, 0.03);
                }
            }
            return;
        }
        if (t == RajangGeometria.TUMBA_ESTALLA) {
            estallarTumba(nivel, c);
        }
    }

    private void estallarTumba(ServerLevel nivel, Vec3 c) {
        sonido(AtalayaSonidos.RAJANG_TUMBA_ESTALLA, 10.0F);
        golpeSuelo(nivel, c, 3.2F, (float) TUMBA_RADIO + 4.0F, 80);
        DamageSource fuente = RajangDanos.fuente(nivel, RajangDanos.RAIZ, this, this);
        for (LivingEntity v : nivel.getEntitiesOfClass(LivingEntity.class, new AABB(c, c).inflate(TUMBA_RADIO, 6.0, TUMBA_RADIO),
                this::esPresa)) {
            double dv = horizontal(c, v.position());
            if (dv > TUMBA_RADIO || (isTumbaAnillo() && dv <= TUMBA_SEGURO)) {
                continue;
            }
            v.hurtServer(nivel, fuente, MORTAL);
            if (v.isAlive()) {
                lastrar(v, TUMBA_PESO);
                lanzar(v, Vec3.ZERO, 0.6);
            }
            nivel.sendParticles(AtalayaParticulas.RAJANG_JADE, true, true, v.getX(), v.getY() + 1, v.getZ(), 10, 0.4, 0.6, 0.4, 0.15);
        }
        // Las raices revientan por todo el circulo: pinchos y grietas (solo se ven, el dano ya esta hecho).
        for (int k = 0; k < 40; k++) {
            double a = random.nextDouble() * Math.PI * 2;
            double r0 = isTumbaAnillo() ? TUMBA_SEGURO + 1.0 : 3.0;
            double r = r0 + random.nextDouble() * (TUMBA_RADIO - 0.5 - r0);
            double x = c.x + Math.cos(a) * r;
            double z = c.z + Math.sin(a) * r;
            double y = sueloBajo(nivel, x, c.y + 3, z);
            PicoTierraEntity.brotarAdorno(nivel, this, new Vec3(x, y, z), 0.35F + random.nextFloat() * 0.35F,
                    (float) Math.toDegrees(a) - 90.0F);
        }
        for (int k = 0; k < 22; k++) {
            double a = Math.PI * 2 * k / 22 + random.nextDouble() * 0.2;
            for (int j = 1; j < 11; j++) {
                double r = j * TUMBA_RADIO / 10.5;
                if (isTumbaAnillo() && r <= TUMBA_SEGURO) {
                    continue;
                }
                double x = c.x + Math.cos(a) * r;
                double z = c.z + Math.sin(a) * r;
                nivel.sendParticles(AtalayaParticulas.RAJANG_GRIETA, true, true, x, sueloBajo(nivel, x, c.y + 3, z) + 0.06, z,
                        0, 1.8, 100.0, 0.0, 1.0);
            }
        }
    }

    // ------------------------------------------------------------------
    //  Aturdido, paralizado y los cambios de fase
    // ------------------------------------------------------------------

    private void tickAturdido(ServerLevel nivel) {
        if (getEstado() == ATURDIDO && t == RajangGeometria.ATURDIDO_CAE) {
            golpeSuelo(nivel, position(), 2.0F, 12.0F, 50);
        }
        if (t % 8 == 0) {
            Vec3 c = puntoMundo(RajangGeometria.CABEZA);
            nivel.sendParticles(AtalayaParticulas.RAJANG_JADE, true, true, c.x, c.y - 2, c.z, 2, 1.2, 0.6, 1.2, 0.02);
        }
    }

    private void tickTambaleo(ServerLevel nivel) {
        if (t == RajangGeometria.TAMBALEO_RUGE) {
            sonido(AtalayaSonidos.RAJANG_RUGIDO, 7.0F);
        }
    }

    /**
     * Pasa de fase: la grieta le cruza el cuerpo, el jade se oscurece, los
     * cristales crecen y (en la IV) el peto revienta. Se le corta lo que
     * estuviera haciendo y se tambalea.
     */
    private void alCambiarFase(ServerLevel nivel, int nueva) {
        entityData.set(DATA_FASE, nueva);
        Vec3 c = puntoMundo(RajangGeometria.PECHO);
        nivel.sendParticles(AtalayaParticulas.RAJANG_JADE, true, true, c.x, c.y, c.z, 40, 2.0, 2.0, 3.0, 0.15);
        nivel.sendParticles(AtalayaParticulas.RAJANG_CHISPA, true, true, c.x, c.y, c.z, 40, 1.5, 1.5, 1.5, 0.2);
        nivel.sendParticles(AtalayaParticulas.RAJANG_ONDA, true, true, getX(), getY() + 0.1, getZ(), 0, 2.4, 18.0, 0.0, 1.0);
        if (nueva == 4) {
            // El peto de oro revienta: el sol queda al aire.
            nivel.sendParticles(AtalayaParticulas.RAJANG_ORO, true, true, c.x, c.y, c.z, 40, 0.8, 0.8, 0.8, 0.25);
        }
        int e = getEstado();
        if (e == DORMIDO || e == DESPERTAR) {
            return;
        }
        for (Player p : jugadores(nivel, 10, 0)) {
            Vec3 fuera = horizontalHacia(position(), p.position());
            p.setDeltaMovement(fuera.x * 1.1, 0.4, fuera.z * 1.1);
            p.hurtMarked = true;
        }
        if (e == SELLO || e == RUGIDO) {
            cancelarSello(nivel, true);
            rugidoFinal = false;
        }
        saltando = false;
        picos.clear();
        if (e != TAMBALEO) {
            ponerEstado(TAMBALEO, RajangGeometria.DURACION_TAMBALEO);
            sonido(AtalayaSonidos.RAJANG_TAMBALEO, 7.0F);
        }
        if (nueva == 2) {
            enfSello = 600;
        }
        if (nueva == 3) {
            enfCataclismo = 160;
        }
        if (nueva == 4) {
            enfSalto = 40;
            enfCataclismo = Math.min(enfCataclismo, 300);
        }
    }

    // ------------------------------------------------------------------
    //  El Idolo de Oro (octubre de 2026, Juan: "sobre Rajang me gusta el
    //  Idolo de Oro"): lo arranca de su templo y lo lanza; quien lo coja lo
    //  lleva al pilar del altar mientras el le persigue. Se pasa de mano en
    //  mano: con la Q sale lanzado hacia donde mira, o con un clic a un
    //  companero (IdoloOro). Sin textos (Juan, 08-10-2026: "no pongas textos
    //  ahi"): solo se le dice a quien lo coge que con la Q lo lanza; el camino
    //  al altar son los puntos de oro del suelo y las chispas del pilar.
    // ------------------------------------------------------------------

    /** El idolo esta fuera: lo busca (IdoloOroItem lo deshace si no). */
    public boolean idoloFuera() {
        return idoloQueda > 0;
    }

    /** Ruge con el idolo en alto y, al rugir, lo lanza a un lado de la arena; el pilar del altar sale al otro. */
    private void tickIdolo(ServerLevel nivel) {
        if (t != RajangGeometria.RUGIDO_RUGE) {
            return;
        }
        Vec3 c = Vec3.atBottomCenterOf(centro);
        double a = random.nextDouble() * Math.PI * 2;
        Vec3 dir = new Vec3(Math.cos(a), 0, Math.sin(a));
        Vec3 cae = c.add(dir.scale(10.0 + random.nextDouble() * 5.0));
        Vec3 al = c.subtract(dir.scale(20.0));
        altar = new Vec3(al.x, sueloBajo(nivel, al.x, c.y + 6, al.z), al.z);
        // El pilar, de cara al centro de la arena (por donde llegan).
        pilarAltar = AltarIdoloEntity.alzar(nivel, this, altar, (float) (Mth.atan2(dir.z, dir.x) * Mth.RAD_TO_DEG) - 90.0F);
        Vec3 desde = puntoMundo(RajangGeometria.PECHO).add(0, 2.0, 0);
        ItemEntity it = new ItemEntity(nivel, desde.x, desde.y,
                desde.z, IdoloOro.crear(this));
        double vuelo = 22.0;
        it.setDeltaMovement((cae.x - desde.x) / vuelo, 0.55, (cae.z - desde.z) / vuelo);
        it.setPickUpDelay(12);
        it.setUnlimitedLifetime();
        it.setGlowingTag(true);
        nivel.addFreshEntity(it);
        // Donde va a caer, marcado en el suelo desde ya.
        double yc = sueloBajo(nivel, cae.x, c.y + 6, cae.z);
        nivel.sendParticles(AtalayaParticulas.RAJANG_AVISO, true, true, cae.x, yc + 0.07, cae.z, 0, 2.2, 30.0, 0.0, 1.0);
        idoloQueda = IDOLO_TICKS;
        idoloAgarra = 80;
        IdoloOro.activar(this);
        sonido(AtalayaSonidos.RAJANG_TOTEM_REHACE, 6.0F);
        nivel.sendParticles(AtalayaParticulas.RAJANG_ORO, true, true, desde.x, desde.y, desde.z, 30, 0.6, 0.6, 0.6, 0.2);
    }

    /** Cada tick con el idolo fuera: el portador va lento y brilla, lo lanza, lo pone en el pilar o lo atrapa. */
    private void tickIdoloFuera(ServerLevel nivel) {
        idoloQueda--;
        portador = IdoloOro.portador(nivel, this);
        idoloSuelo = portador == null ? IdoloOro.enSuelo(nivel, this) : null;
        if (portador != null && portador != portadorAntes) {
            // Lo unico que se le dice: con que tecla lo lanza.
            portador.sendOverlayMessage(Component.translatable("hud.atalaya.rajang.idolo_lanzar",
                    Component.keybind("key.drop")).withStyle(ChatFormatting.GOLD));
        }
        if (portador == null && idoloSuelo != null && portadorAntes != null && idoloSuelo.getId() != idoloLanzado
                && idoloSuelo.tickCount <= 2 && idoloSuelo.getOwner() == portadorAntes) {
            lanzarIdolo(nivel, portadorAntes, idoloSuelo);
        }
        portadorAntes = portador;
        if (idoloAgarra > 0) {
            idoloAgarra--;
        }
        idoloEnCabeza(portador);
        if (portador != null) {
            portador.addEffect(new net.minecraft.world.effect.MobEffectInstance(net.minecraft.world.effect.MobEffects.SLOWNESS, 12,
                    0, false, false), this);
            portador.addEffect(new net.minecraft.world.effect.MobEffectInstance(net.minecraft.world.effect.MobEffects.GLOWING, 12,
                    0, false, false), this);
            if (altar != null && tickCount % 4 == 0) {
                senalarAltar(nivel, portador);
            }
            if (altar != null && horizontal(portador.position(), altar) < IDOLO_ENTREGA && Math.abs(portador.getY() - altar.y) < 3.0) {
                entregarIdolo(nivel, portador);
                return;
            }
        } else if (idoloSuelo != null) {
            // Tirado: una columna de oro encima y un aro en el suelo, para verlo desde lejos.
            Vec3 q = idoloSuelo.position();
            if (tickCount % 3 == 0) {
                nivel.sendParticles(AtalayaParticulas.RAJANG_ORO, true, true, q.x, q.y + 0.5 + random.nextDouble() * 6.0, q.z, 2, 0.08,
                        0.4, 0.08, 0.01);
            }
            if (tickCount % 12 == 0 && idoloSuelo.onGround()) {
                nivel.sendParticles(AtalayaParticulas.RAJANG_AVISO, true, true, q.x, q.y + 0.07, q.z, 0, 1.6, 14.0, 0.0, 1.0);
            }
            // Solo si ya esta en el suelo y paso el margen: al lanzarlo sale de su pecho.
            if (idoloAgarra <= 0 && idoloSuelo.onGround()
                    && horizontal(position(), idoloSuelo.position()) < getBbWidth() * 0.5 + 2.0) {
                // Lo recoge del suelo con la boca: lo recupera (sin curarse).
                Vec3 p = idoloSuelo.position();
                nivel.sendParticles(AtalayaParticulas.RAJANG_ORO, true, true, p.x, p.y + 0.5, p.z, 30, 0.5, 0.5, 0.5, 0.2);
                sonido(AtalayaSonidos.RAJANG_RUGIDO, 5.0F);
                acabarIdolo(nivel);
                return;
            }
        } else {
            // Ni lo lleva nadie ni esta en el suelo (lo han guardado o se ha perdido): se acabo.
            acabarIdolo(nivel);
            return;
        }
        if (idoloQueda <= 0) {
            // Se acabo el tiempo: el idolo se deshace en polvo de oro donde este.
            Vec3 q = portador != null ? portador.position().add(0, portador.getBbHeight() + 0.4, 0)
                    : idoloSuelo != null ? idoloSuelo.position().add(0, 0.4, 0) : null;
            if (q != null) {
                nivel.sendParticles(AtalayaParticulas.RAJANG_ORO, true, true, q.x, q.y, q.z, 40, 0.3, 0.3, 0.3, 0.08);
                nivel.playSound(null, q.x, q.y, q.z, AtalayaSonidos.RAJANG_TOTEM_ROTO, SoundSource.HOSTILE, 2.5F, 1.4F);
            }
            acabarIdolo(nivel);
        }
    }

    /** Lo cerca que hay que llegar del pilar (al centro, en horizontal) para poner el idolo encima. */
    private static final double IDOLO_ENTREGA = 2.2;

    /**
     * Lo ha soltado con la Q: sale lanzado hacia donde mira (unos diez bloques),
     * para pasarselo a un companero de lejos; se puede coger enseguida.
     */
    private void lanzarIdolo(ServerLevel nivel, Player p, ItemEntity it) {
        idoloLanzado = it.getId();
        Vec3 mira = p.getLookAngle();
        Vec3 h = new Vec3(mira.x, 0, mira.z);
        h = h.lengthSqr() < 1.0E-4 ? Vec3.directionFromRotation(0, p.getYRot()) : h.normalize();
        it.setDeltaMovement(h.x * 0.6, 0.32 + Math.max(0.0, mira.y) * 0.3, h.z * 0.6);
        it.setPickUpDelay(8);
        nivel.playSound(null, p.getX(), p.getEyeY(), p.getZ(), AtalayaSonidos.RAJANG_TOTEM, SoundSource.PLAYERS, 1.2F, 1.7F);
        nivel.sendParticles(AtalayaParticulas.RAJANG_ORO, true, true, it.getX(), it.getY(), it.getZ(), 10, 0.15, 0.15, 0.15, 0.05);
    }

    /** Persigue al portador al galope, o va a por el idolo tirado; no ataca con otra cosa. */
    private void perseguirIdolo() {
        Vec3 meta = portador != null ? portador.position() : idoloSuelo != null ? idoloSuelo.position() : null;
        if (meta == null) {
            quieto();
            return;
        }
        Vec3 c = Vec3.atBottomCenterOf(centro);
        Vec3 rel = new Vec3(meta.x - c.x, 0, meta.z - c.z);
        if (rel.length() > CORREA) {
            rel = rel.normalize().scale(CORREA);
            meta = new Vec3(c.x + rel.x, meta.y, c.z + rel.z);
        }
        double d = horizontal(position(), meta);
        double furia = tieneFuria() ? FURIA_CORRE : 1.0;
        if (d > 10.0) {
            getMoveControl().setWantedPosition(meta.x, meta.y, meta.z, (fase() >= 4 ? GALOPE_IV : GALOPE) * furia);
        } else if (d > 5.0 || portador == null) {
            getMoveControl().setWantedPosition(meta.x, meta.y, meta.z, PASO * furia);
        } else {
            quieto();
        }
        girarHacia(meta, 12.0F);
    }

    /**
     * El idolo, en la cabeza de quien lo lleva (Juan: "el idolo debe tenerlo en
     * la cabeza el jugador"): se sincroniza quien es y el cliente lo pinta encima
     * de su cabeza (RajangRenderer). Un jugador no se puede montar (el servidor
     * no deja), asi que no vale un objeto de exhibicion montado en el.
     */
    private void idoloEnCabeza(@Nullable Player p) {
        int id = p != null ? p.getId() : -1;
        if (entityData.get(DATA_PORTADOR) != id) {
            entityData.set(DATA_PORTADOR, id);
        }
    }

    /** Quien lleva el idolo (id de entidad; -1 si nadie): el cliente se lo pinta en la cabeza. */
    public int getPortadorIdolo() {
        return entityData.get(DATA_PORTADOR);
    }

    /**
     * El camino al pilar: puntos de oro en el suelo delante del portador, que ven
     * todos (sin textos: Juan, 08-10-2026).
     */
    private void senalarAltar(ServerLevel nivel, Player p) {
        double dx = altar.x - p.getX();
        double dz = altar.z - p.getZ();
        double lejos = Math.sqrt(dx * dx + dz * dz);
        if (lejos < 2.0) {
            return;
        }
        double ux = dx / lejos;
        double uz = dz / lejos;
        for (double k = 1.5; k < Math.min(lejos, 10.5); k += 1.5) {
            double x = p.getX() + ux * k;
            double z = p.getZ() + uz * k;
            nivel.sendParticles(AtalayaParticulas.RAJANG_ORO, true, true, x, sueloBajo(nivel, x, p.getY() + 2, z) + 0.15, z, 1, 0.05,
                    0.02, 0.05, 0.0);
        }
    }

    /**
     * Llega al pilar: pone el idolo encima (se queda un momento y revientan los
     * dos, AltarIdoloEntity), le quita un 5 % de vida y cae aturdido con dano doble.
     */
    private void entregarIdolo(ServerLevel nivel, Player p) {
        IdoloOro.quitar(p, this);
        if (pilarAltar != null && !pilarAltar.isRemoved()) {
            pilarAltar.recibir(nivel);
        }
        setHealth(Math.max(1.0F, getHealth() - getMaxHealth() * 0.05F));
        acabarIdolo(nivel);
        cancelarSello(nivel, false);
        ponerEstado(ATURDIDO, RajangGeometria.DURACION_ATURDIDO);
        sonido(AtalayaSonidos.RAJANG_ATURDIDO, 7.0F);
    }

    /** Su Garra ha pillado al portador: recupera el idolo (sin curarse). */
    private void recuperarIdolo(ServerLevel nivel, Player p) {
        IdoloOro.quitar(p, this);
        sonido(AtalayaSonidos.RAJANG_ZARPAZO, 6.0F);
        nivel.sendParticles(AtalayaParticulas.RAJANG_ORO, true, true, p.getX(), p.getY() + 1.0, p.getZ(), 30, 0.5, 0.8, 0.5, 0.25);
        acabarIdolo(nivel);
    }

    /** Se acabo el idolo (bien o mal): fuera de donde este y vuelve a pelear como siempre. */
    private void acabarIdolo(ServerLevel nivel) {
        idoloQueda = 0;
        idoloEnCabeza(null);
        IdoloOro.quitarTodos(nivel, this);
        IdoloOro.desactivar(this);
        // El pilar se hunde, salvo que ya tenga el idolo encima (entonces revienta el solo).
        if (pilarAltar != null && !pilarAltar.isRemoved() && !pilarAltar.conIdolo()) {
            pilarAltar.retirar(nivel);
        }
        pilarAltar = null;
        altar = null;
        portador = null;
        portadorAntes = null;
        idoloSuelo = null;
    }

    // ------------------------------------------------------------------
    //  Las cajas de la cabeza y la grupa
    // ------------------------------------------------------------------

    /** Lo alto de la caja de la grupa, de pie: del suelo a encima del lomo. */
    private static final float GRUPA_ALTO = 8.6F;

    private void crearPartes(ServerLevel nivel) {
        partes.add(RajangParteEntity.crear(nivel, this, "cabeza", 3.6F, 3.6F));
        // La grupa va del suelo al lomo: tapa tambien las patas de atras (testers,
        // 07-10-2026: antes empezaba a 3,75 bloques y por detras no se le daba).
        partes.add(RajangParteEntity.crear(nivel, this, "grupa", 5.0F, GRUPA_ALTO));
        moverPartes();
    }

    private void moverPartes() {
        int e = getEstado();
        boolean tumbado = e == DORMIDO || e == ATURDIDO || isDeadOrDying();
        for (RajangParteEntity p : partes) {
            Vec3 local;
            if (p.getNombre().equals("cabeza")) {
                local = (e == CATACLISMO_SOSTIENE || e == CATACLISMO) ? RajangGeometria.BOCA_CATACLISMO : RajangGeometria.CABEZA;
                if (e == DESPERTAR) {
                    // la cabeza va con la animacion del despertar (de tumbado a alzado)
                    local = RajangGeometria.cabezaDespertar(t);
                }
                if (tumbado) {
                    local = new Vec3(local.x, 2.6, local.z);
                }
            } else {
                // Del suelo (sus pies) al lomo; tumbado, mas baja.
                p.medidas(5.0F, tumbado ? 4.6F : GRUPA_ALTO);
                Vec3 w = puntoMundo(RajangGeometria.GRUPA);
                p.colocar(w.x, getY(), w.z);
                continue;
            }
            Vec3 w = puntoMundo(local);
            p.colocar(w.x, w.y - p.getBbHeight() / 2, w.z);
        }
    }

    /** El dano que llega por la cabeza o la grupa. */
    public boolean hurtDesdeParte(ServerLevel nivel, RajangParteEntity parte, DamageSource fuente, float cantidad) {
        return hurtServer(nivel, fuente, cantidad);
    }

    /** Ya se ha apuntado como el de su tipo en el mundo (JefesUnicos). */
    private boolean admitido;

    @Override
    public void remove(RemovalReason motivo) {
        if (motivo.shouldDestroy() && admitido && level() instanceof ServerLevel nivelFuera) {
            JefesUnicos.soltar(nivelFuera, this);
        }
        if (idoloQueda > 0 && level() instanceof ServerLevel nivelIdolo) {
            acabarIdolo(nivelIdolo);
        }
        super.remove(motivo);
        limpiar();
    }

    /** Lo suyo que queda por ahi (picos, pilares, totems, columnas y piedras, sus cajas) se va con el. */
    private void limpiar() {
        if (level() instanceof ServerLevel nivel) {
            cancelarSello(nivel, false);
            for (Entity x : nivel.getEntitiesOfClass(Entity.class, getBoundingBox().inflate(96),
                    x -> x instanceof PicoTierraEntity || x instanceof PilarTierraEntity || x instanceof FragmentoJadeEntity
                            || x instanceof PlataformaSelloEntity || x instanceof TotemSelloEntity)) {
                x.discard();
            }
        }
        for (RajangParteEntity p : partes) {
            p.discard();
        }
        partes.clear();
        picos.clear();
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
        if (PresasJefe.esJefe(causante) || directo instanceof PicoTierraEntity || directo instanceof PilarTierraEntity
                || directo instanceof FragmentoJadeEntity) {
            return false;
        }
        int e = getEstado();
        if (e == DORMIDO) {
            despertarse(causante);
            avisoInmune(nivel, causante);
            return false;
        }
        if (e == DESPERTAR || escena > 0) {
            avisoInmune(nivel, causante);
            return false;
        }
        if (e == SELLO || e == RUGIDO || (e == TUMBA && t < RajangGeometria.TUMBA_ESTALLA)) {
            // Mientras sostiene el Sello la tierra lo cubre entero: no le entra nada,
            // lo unico que sirve es romper los totems. Igual mientras llena la Tumba.
            avisoInmune(nivel, causante);
            return false;
        }
        if (tieneFuria()) {
            // La Furia: inmune mientras dura (30 s); lo de romper (ojos, nucleos...) va aparte.
            avisoInmune(nivel, causante);
            return false;
        }
        if (causante instanceof LivingEntity vivo && random.nextInt(4) == 0 && e == LIBRE) {
            setTarget(vivo);
        }
        float k = factorGrupo;
        if (e == ATURDIDO || e == PARALIZADO || e == ESTAMPADO) {
            k *= 2.0F;
        }
        if (piel > 0) {
            k *= 1.0F - PIEL_REDUCE;
        }
        boolean entra = super.hurtServer(nivel, fuente, cantidad * k);
        if (entra) {
            Vec3 p = directo != null ? directo.position().add(0, directo.getBbHeight() * 0.5, 0) : puntoMundo(RajangGeometria.PECHO);
            nivel.sendParticles(AtalayaParticulas.RAJANG_JADE, true, true, p.x, p.y, p.z, 6, 0.4, 0.4, 0.4, 0.08);
            if (piel > 0) {
                nivel.sendParticles(AtalayaParticulas.RAJANG_RUNA, true, true, p.x, p.y, p.z, 3, 0.3, 0.3, 0.3, 0.05);
            }
        }
        return entra;
    }

    /** El golpe resbala en el jade de la esfinge dormida. */
    private void avisoInmune(ServerLevel nivel, @Nullable Entity causante) {
        if (tickCount - ultimoAvisoInmune < 5) {
            return;
        }
        ultimoAvisoInmune = tickCount;
        Vec3 p = puntoMundo(RajangGeometria.PECHO);
        if (causante != null) {
            Vec3 fuera = horizontalHacia(position(), causante.position());
            p = new Vec3(getX() + fuera.x * 2.8, Mth.clamp(causante.getEyeY(), getY() + 0.5, getY() + 6.0), getZ() + fuera.z * 2.8);
        }
        nivel.playSound(null, p.x, p.y, p.z, AtalayaSonidos.RAJANG_INMUNE, SoundSource.HOSTILE, 1.5F, 0.9F + random.nextFloat() * 0.2F);
        nivel.sendParticles(AtalayaParticulas.RAJANG_JADE, true, true, p.x, p.y, p.z, 5, 0.3, 0.3, 0.3, 0.1);
    }

    // ------------------------------------------------------------------
    //  La liberacion: el sol se apaga, las grietas se cierran en oro, se
    //  tumba como una esfinge con los ojos en oro y la piedra vuelve a ser
    //  piedra.
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
        entityData.set(DATA_PIEL, false);
        entityData.set(DATA_FURIA, false);
        entityData.set(DATA_CARGA, 0.0F);
        velCarga = 0.0;
        if (level() instanceof ServerLevel nivel) {
            cancelarSello(nivel, true);
        }
        picos.clear();
        saltando = false;
    }

    @Override
    protected void tickDeath() {
        ++deathTime;
        if (!(level() instanceof ServerLevel nivel) || isRemoved()) {
            return;
        }
        if (deathTime == 1) {
            sonido(AtalayaSonidos.RAJANG_LIBERACION, 7.0F);
        }
        tickPiezasSello(nivel);
        moverPartes();
        setDeltaMovement(0, Math.min(0, getDeltaMovement().y), 0);
        Vec3 c = puntoMundo(RajangGeometria.PECHO);
        if (deathTime == RajangGeometria.LIBERACION_OJOS_ORO) {
            nivel.sendParticles(AtalayaParticulas.RAJANG_ORO, true, true, c.x, c.y - 2, c.z, 60, 2.0, 1.6, 3.0, 0.1);
            nivel.sendParticles(AtalayaParticulas.RAJANG_HOJA, true, true, c.x, c.y + 6, c.z, 50, 8.0, 3.0, 8.0, 0.02);
        }
        if (deathTime > RajangGeometria.LIBERACION_OJOS_ORO && deathTime % 3 == 0) {
            nivel.sendParticles(AtalayaParticulas.RAJANG_ORO, true, true, c.x, c.y - 2, c.z, 2, 3.0, 2.0, 5.0, 0.01);
        }
        if (deathTime == 150) {
            Vec3 m = position();
            for (Player p : nivel.getEntitiesOfClass(Player.class, new AABB(m, m).inflate(80))) {
                p.addEffect(new MobEffectInstance(BendicionTierraEffect.BENDICION, 20 * 60 * 10, 0), this);
            }
        }
        if (deathTime == 160) {
            sonido(AtalayaSonidos.RAJANG_DISOLVER, 6.0F);
        }
        if (deathTime >= RajangGeometria.DURACION_LIBERACION) {
            nivel.sendParticles(AtalayaParticulas.RAJANG_POLVO, true, true, getX(), getY() + 3.0, getZ(), 80, 4.0, 2.0, 6.0, 0.06);
            nivel.sendParticles(AtalayaParticulas.RAJANG_ORO, true, true, getX(), getY() + 3.0, getZ(), 50, 4.0, 2.0, 6.0, 0.05);
            nivel.sendParticles(AtalayaParticulas.RAJANG_ROCA, true, true, getX(), getY() + 3.0, getZ(), 40, 4.0, 2.0, 6.0, 0.05);
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

    /** El cuerpo mira siempre a donde apunta: con 17 bloques, girar la cabeza sola queda raro. */
    @Override
    protected void tickHeadTurn(float rumboCuerpo) {
        this.yBodyRot = getYRot();
        this.yHeadRot = getYRot();
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

    /** Lo que sus ataques pueden golpear: solo jugadores (y maniquies de prueba), nunca otro jefe (PresasJefe.presa). */
    public boolean esPresa(LivingEntity v) {
        return v != this && PresasJefe.presa(v);
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

    /** Lo alto del primer bloque solido bajo (x, y, z). */
    public static double sueloBajo(ServerLevel nivel, double x, double y, double z) {
        return AeralisEntity.sueloBajo(nivel, x, y, z);
    }

    /** Un golpe contra el suelo: la onda (que sacude la camara cerca), polvo y piedras. */
    void golpeSuelo(ServerLevel nivel, Vec3 p, float temblor, float radio, int polvo) {
        nivel.sendParticles(AtalayaParticulas.RAJANG_ONDA, true, true, p.x, p.y + 0.12, p.z, 0, temblor, radio, 0.0, 1.0);
        for (int i = 0; i < polvo; i++) {
            double a = random.nextDouble() * Math.PI * 2;
            double v = 0.15 + random.nextDouble() * 0.35;
            nivel.sendParticles(i % 4 == 0 ? AtalayaParticulas.RAJANG_ROCA : AtalayaParticulas.RAJANG_POLVO,
                    p.x + Math.cos(a) * 1.5, p.y + 0.3, p.z + Math.sin(a) * 1.5, 0, Math.cos(a) * v, 0.08 + (i % 4 == 0 ? 0.25 : 0), Math.sin(a) * v, 1.0);
        }
    }

    private void sonido(SoundEvent s, float volumen) {
        playSound(s, volumen, 1.0F);
    }

    void cortarSonido(ServerLevel nivel, SoundEvent s) {
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
        return e == DORMIDO ? AtalayaSonidos.RAJANG_DORMIDO : e == LIBRE ? AtalayaSonidos.RAJANG_AMBIENTE : null;
    }

    @Override
    public int getAmbientSoundInterval() {
        return 140;
    }

    @Override
    protected SoundEvent getHurtSound(DamageSource fuente) {
        return AtalayaSonidos.RAJANG_HERIDO;
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
        salida.putBoolean("dormido", getEstado() == DORMIDO);
        salida.putFloat("factor_grupo", factorGrupo);
        salida.putInt("jugadores_grupo", jugadoresGrupo);
        salida.putInt("fase", fase());
        salida.putBoolean("furia", tieneFuria());
        salida.putInt("furia_queda", furiaQueda);
    }

    @Override
    protected void readAdditionalSaveData(ValueInput entrada) {
        super.readAdditionalSaveData(entrada);
        centro = entrada.read("centro", BlockPos.CODEC).orElse(null);
        factorGrupo = entrada.getFloatOr("factor_grupo", VIDA_VANILLA / VIDA);
        jugadoresGrupo = entrada.getIntOr("jugadores_grupo", 1);
        entityData.set(DATA_FASE, entrada.getIntOr("fase", 1));
        entityData.set(DATA_FURIA, entrada.getBooleanOr("furia", false));
        furiaQueda = tieneFuria() ? entrada.getIntOr("furia_queda", PresasJefe.FURIA_TICKS) : 0;
        entityData.set(DATA_FURIA_FIN, furiaQueda > 0 ? level().getGameTime() + furiaQueda : 0L);
        ponerEstado(entrada.getBooleanOr("dormido", true) ? DORMIDO : LIBRE, 0);
    }
}
