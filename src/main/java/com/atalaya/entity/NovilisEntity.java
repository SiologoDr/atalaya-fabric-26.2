package com.atalaya.entity;

import com.atalaya.Atalaya;
import com.atalaya.effect.BendicionSolEffect;
import com.atalaya.effect.QuemaduraEffect;
import com.atalaya.particula.AtalayaParticulas;
import com.atalaya.sonido.AtalayaSonidos;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleOptions;
import net.minecraft.network.chat.Component;
import net.minecraft.network.protocol.game.ClientboundStopSoundPacket;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.Identifier;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundSource;
import net.minecraft.tags.DamageTypeTags;
import net.minecraft.util.Mth;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.damagesource.DamageType;
import net.minecraft.world.damagesource.DamageTypes;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.AnimationState;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.MoverType;
import net.minecraft.world.entity.Relative;
import net.minecraft.world.entity.ai.attributes.AttributeInstance;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.target.HurtByTargetGoal;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.level.storage.ValueInput;
import net.minecraft.world.level.storage.ValueOutput;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;
import org.jspecify.annotations.Nullable;

import java.util.ArrayList;
import java.util.Collections;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.UUID;

/**
 * Novilis, el Caballero Solar: el cuarto de los jefes elementales, el del
 * fuego. Un guerrero de leyenda con una armadura forjada con lava y el poder
 * del sol; trae su propio sol, que flota sobre el y del que saca su poder.
 * Mide 16 bloques hasta el yelmo (18 con el halo).
 *
 * Nace de rodilla, con la espada clavada delante y la cabeza gacha, hasta que
 * ve a alguien; se invoca con su huevo.
 *
 * <pre>
 *   fase I    Brasa       Barrido de fuego (cuatro tajos: la hoja de cerca y
 *                         medias lunas de fuego que vuelan), Castigo solar
 *                         (un sello bajo cada jugador y un rayo que cae),
 *                         Espada del Fuego (su embestida: 3 s cargando, 40
 *                         bloques en linea recta y un camino de llamas detras)
 *   fase II   Llamarada   + el Castigo acaba clavando la espada: una onda de
 *                         fuego por el suelo (se salta), Sol Abrasador (tres
 *                         soles que revientan en fuego y lava y la Supernova,
 *                         un cuarto mas grande y mas lento), Trompetas del
 *                         Apocalipsis (cuatro angeles en lo alto de sus
 *                         estrados tocan una melodia: si alguno sigue en pie al
 *                         acabar, entra en Furia), Sombra del Escudo (lanza su
 *                         sol al cielo y abrasa la arena 12 s: solo se salva
 *                         quien esta a la sombra de una Egida)
 *   fase III  Mediodia    + Furia Infernal (salta sobre uno, cae clavando la
 *                         espada, la grieta escupe lava y revienta), Ofrenda al
 *                         Sol (coge a uno, lo alza y el atrapado tiene que
 *                         seguir una secuencia de teclas)
 *   fase IV   Dios de la Guerra   + Mar de Llamas (hunde la espada y el suelo se
 *                         raja por toda la arena: bocas de fuego que se quedan
 *                         hasta que acaba), Dios de la Guerra (llamas carmesi y
 *                         soles a tres zonas con explosiones en cadena: mata a
 *                         quien tiene quemadura grave)
 * </pre>
 *
 * Las Fuentes solares y el Grito de guerra que soltaban si fallaban se
 * quitaron el 08-10-2026 (Juan).
 *
 * El fuego deja Quemadura (I a III, QuemaduraEffect). La Furia es de fuego
 * azul: un 25 % mas rapido, un 35 % mas de dano y un 35 % menos de espera; se
 * va al aturdirlo (una Ofrenda superada o el sol apagado en la Sombra).
 *
 * Como los otros tres, el estado vive en un numero sincronizado y el cliente
 * arranca la animacion que toca al verlo cambiar. Los ticks de cada golpe y los
 * puntos del cuerpo salen de {@link NovilisGeometria}, generado con las mismas
 * poses que las animaciones.
 */
public class NovilisEntity extends Monster {

    public static final int LIBRE = 0;
    public static final int DORMIDO = 1;
    public static final int DESPERTAR = 2;
    public static final int BARRIDO = 3;
    public static final int CASTIGO = 4;
    public static final int SOL = 5;
    public static final int TROMPETAS = 6;
    public static final int OFRENDA = 8;
    public static final int DIOS = 9;
    public static final int ATURDIDO = 10;
    public static final int TAMBALEO = 11;
    public static final int GRITO = 12;
    public static final int CASTIGO_ONDA = 13;
    /** La Sombra del Escudo (octubre de 2026, la que eligio Juan de la segunda ficha de fuego). */
    public static final int SOMBRA = 14;
    /** Los ataques de octubre de 2026 (Juan): la embestida, el salto y el suelo en llamas. */
    public static final int ESPADA = 15;
    public static final int INFERNAL = 16;
    public static final int MAR = 17;

    /** Vida EFECTIVA: 16 500, la misma con cualquier numero de jugadores (el tope de vanilla es 1024). */
    public static final float VIDA = 16500.0F;
    private static final float VIDA_VANILLA = 1024.0F;
    // --- Danos por fase (I, II, III, IV): la misma escala que los otros tres ---
    // Recortado el 07-10-2026 (Juan): -50 % lo de area y -45 % lo individual. Con
    // 60 jugadores y 3-4 totems cada uno, lo normal no debe gastar totems: eso
    // es cosa de los especiales mortales, que no cambian. En la III y la IV,
    // otro -15 % y -20 % (Juan, tras probarlo: las fases I y II estaban bien).
    public static final float[] DANO_HOJA = {18, 23.5F, 25.5F, 32};
    public static final float[] DANO_TAJO = {13, 17, 18.7F, 23.2F};
    public static final float[] DANO_RAYO = {19, 24, 26.4F, 32.8F};
    public static final float[] DANO_ONDA = {12, 16, 17, 21.6F};
    public static final float[] DANO_SOL = {27.5F, 35, 37.4F, 44};
    /** El cuarto sol del Sol Abrasador, el grande (radio RADIO_SUPERNOVA). */
    public static final float[] DANO_SUPERNOVA = {36, 45, 49, 57};
    /** La Espada del Fuego: su cuerpo y la hoja a la carrera, y el camino de llamas (cada medio segundo). */
    public static final float[] DANO_ESPADA = {24, 31, 34, 42};
    public static final float[] DANO_CAMINO = {3, 4, 5, 6};
    /** La Furia Infernal: la caida, cada chorro de la grieta y la explosion final. */
    public static final float[] DANO_INFERNAL = {26, 33, 36, 45};
    public static final float[] DANO_GEISER = {10, 13, 14, 18};
    public static final float[] DANO_EXPLOSION_INFERNAL = {22, 28, 31, 38};
    /** Cada boca del Mar de Llamas, cada medio segundo dentro. */
    public static final float[] DANO_MAR = {8, 10, 12, 14};
    public static final float[] DANO_DIOS = {174, 174, 174, 174};
    /** El sol de la Sombra del Escudo, cada segundo al sol (pasa la armadura: solo vale la sombra). */
    public static final float[] DANO_ABRASA = {4, 4, 5, 6};
    /** Lo que mata salvo totem (todas las bypasses_* menos la de invulnerabilidad). */
    public static final float MORTAL = 10000.0F;
    /**
     * Golpes que aguanta cada estatua, sean cuantos sean los jugadores (15 desde
     * el 08-10-2026: Juan queria que costara mas; antes, 10).
     */
    public static final int GOLPES = 15;

    // --- La Furia (fuego azul) ---
    private static final float FURIA_RITMO = 1.15F;
    private static final float FURIA_DANO = 1.2F;
    private static final float FURIA_ENFRIA = 0.75F;
    private static final double FURIA_ANDA = 1.1;
    /**
     * Lo que se pide al control de movimiento al andar y al correr. Vanilla
     * empuja con (atributo x esto) al cuadrado, asi que con 0,27 de atributo:
     * andar 1,37 son unos 6 bloques/s y correr 2,0 unos 13 (15 en la IV).
     */
    private static final double ANDA = 1.37;
    private static final double CORRE = 2.0;
    private static final double CORRE_IV = 2.16;
    /** Corre si su blanco esta mas lejos que esto (bloques); vuelve a andar por debajo de ANDA_DESDE. */
    private static final double CORRE_DESDE = 20.0;
    private static final double ANDA_DESDE = 15.0;
    /** A partir de que velocidad (bloques por tick) el cliente pasa de andar a correr. */
    public static final float VEL_CORRER = 0.44F;

    /** Lo que alcanza la hoja de cerca en el Barrido (bloques desde sus pies). */
    public static final double RADIO_HOJA = 12.0;
    /** El rayo del Castigo: el radio del sello. */
    public static final float RADIO_RAYO = 2.6F;
    /** La onda de fuego del Castigo: hasta donde llega y lo que avanza por tick. */
    public static final float ONDA_MAX = 26.0F;
    public static final float ONDA_VEL = 0.9F;
    /** El sello del Sol x3 (donde revienta) y el de la Supernova, el cuarto. */
    public static final float RADIO_SOL = 4.0F;
    public static final float RADIO_SUPERNOVA = 12.0F;
    /** Cada zona del Dios de la Guerra. */
    public static final float RADIO_ZONA = 6.0F;
    /** Lo que dura la melodia de las Trompetas (24 s, como los cuatro .ogg). */
    public static final int MELODIA = 480;
    /** A cuanto del centro salen las estatuas. */
    private static final double RADIO_ESTATUAS = 15.0;
    public static final int NUM_ESTATUAS = 4;
    /**
     * La Espada del Fuego: el carril que corre (bloques) y su ancho. Juan
     * (08-10-2026): 20 se quedaba corto, 40; y dos bloques mas a cada lado, 8.
     */
    public static final float ESPADA_LARGO = 40.0F;
    public static final float ESPADA_ANCHO = 8.0F;
    /** Los dos primeros segundos de la carga sigue a su presa; el ultimo, el carril queda fijo. */
    public static final int ESPADA_SIGUE = 40;
    /** La Furia Infernal: cuando queda fijo donde cae, lo alto del salto, el radio del golpe y de la explosion. */
    private static final int INFERNAL_MARCA = 6;
    private static final double ALTURA_SALTO = 6.0;
    private static final float RADIO_INFERNAL = 7.0F;
    private static final float RADIO_EXPLOSION_INFERNAL = 11.0F;
    private static final float GRIETA_LARGO = 16.0F;
    /** El Mar de Llamas: lo que dura, cada cuanto se raja otra vez, el aviso y cada boca. */
    public static final int MAR_DURA = 300;
    private static final int MAR_OLA = 90;
    private static final int MAR_AVISO = 30;
    private static final float MAR_RADIO = 2.6F;
    private static final int MAR_JUGADORES = 20;
    private static final int MAR_SUELTAS = 8;
    /** El tiempo de la Ofrenda: 8 s para las teclas (y un poco mas en el servidor, por el lag). */
    public static final int OFRENDA_TIEMPO = 160;
    /**
     * Los 3 s para prepararse antes de las teclas (Juan, 08-10-2026: al agarrarte
     * no te enterabas, tocabas algo y fallabas). Mientras, las teclas no cuentan.
     */
    public static final int OFRENDA_PREPARA = 60;
    /** Las teclas de la Ofrenda: 12 en la fase III y 14 en la IV (Juan, 08-10-2026; antes 10 y 12). */
    public static final int TECLAS_III = 12;
    public static final int TECLAS_IV = 14;
    /** El pulso de los angeles de las Trompetas: apenas dana, lo que hace es tirar del estrado. */
    public static final float[] DANO_PULSO = {6, 6, 8, 8};
    private static final int OFRENDA_GRACIA = 10;
    /**
     * Lo que se aleja la camara del atrapado (camera_distance, en tercera
     * persona): a los 4 bloques de siempre los guanteletes tapaban la pantalla.
     * Es transitorio (no se guarda) y se quita al soltarlo.
     */
    private static final double CAMARA_OFRENDA = 10.0;
    private static final Identifier ID_CAMARA_OFRENDA = Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "ofrenda_camara");
    /** Lo que quema estar en sus manos: la vida maxima del atrapado, por segundo. */
    private static final float OFRENDA_CALOR = 0.04F;
    private static final int ATURDIDO_OFRENDA = 100;
    /** Deslumbrado: lo que queda aturdido si nadie se quemo con la Sombra del Escudo. */
    private static final int ATURDIDO_SOMBRA = 80;

    /** Lo lejos que se aparta de donde nacio. */
    private static final double CORREA = 40.0;
    /** A partir de aqui suelta al objetivo. */
    private static final double LEJOS = 72.0;

    private static final EntityDataAccessor<Integer> DATA_ESTADO =
            SynchedEntityData.defineId(NovilisEntity.class, EntityDataSerializers.INT);
    private static final EntityDataAccessor<Integer> DATA_FASE =
            SynchedEntityData.defineId(NovilisEntity.class, EntityDataSerializers.INT);
    private static final EntityDataAccessor<Boolean> DATA_FURIA =
            SynchedEntityData.defineId(NovilisEntity.class, EntityDataSerializers.BOOLEAN);
    /** Cuando se le acaba la Furia (tiempo del mundo; 0: sin Furia): el cliente pinta la cuenta atras. */
    private static final EntityDataAccessor<Long> DATA_FURIA_FIN =
            SynchedEntityData.defineId(NovilisEntity.class, EntityDataSerializers.LONG);
    /** Golpes de cada estatua: 4 bits por estatua. */
    private static final EntityDataAccessor<Integer> DATA_GOLPES_ESTATUAS =
            SynchedEntityData.defineId(NovilisEntity.class, EntityDataSerializers.INT);
    /** Lo que va de la melodia (0 a 1); -1 si no suena. */
    private static final EntityDataAccessor<Float> DATA_MELODIA =
            SynchedEntityData.defineId(NovilisEntity.class, EntityDataSerializers.FLOAT);
    /** A quien senala el haz de su sol antes de cogerlo (Ofrenda). -1 si a nadie. */
    private static final EntityDataAccessor<Integer> DATA_MARCA =
            SynchedEntityData.defineId(NovilisEntity.class, EntityDataSerializers.INT);
    /** A quien tiene en las manos (Ofrenda). -1 si a nadie. */
    private static final EntityDataAccessor<Integer> DATA_OFRENDA =
            SynchedEntityData.defineId(NovilisEntity.class, EntityDataSerializers.INT);
    private static final EntityDataAccessor<Integer> DATA_SEMILLA =
            SynchedEntityData.defineId(NovilisEntity.class, EntityDataSerializers.INT);
    private static final EntityDataAccessor<Integer> DATA_TECLAS =
            SynchedEntityData.defineId(NovilisEntity.class, EntityDataSerializers.INT);
    private static final EntityDataAccessor<Integer> DATA_ACIERTOS =
            SynchedEntityData.defineId(NovilisEntity.class, EntityDataSerializers.INT);
    /** Lo que va de la Sombra del Escudo (0 mientras sube el sol, hasta 1 al acabar); -1 si no hay. */
    private static final EntityDataAccessor<Float> DATA_SOMBRA =
            SynchedEntityData.defineId(NovilisEntity.class, EntityDataSerializers.FLOAT);
    /** Los que estan a la sombra (8 bits bajos) y los que pelean (los de encima): la cuenta de la barra. */
    private static final EntityDataAccessor<Integer> DATA_SOMBRA_CUENTA =
            SynchedEntityData.defineId(NovilisEntity.class, EntityDataSerializers.INT);

    // --- Solo cliente ---
    public final AnimationState dormido = new AnimationState();
    public final AnimationState despertar = new AnimationState();
    public final AnimationState barrido = new AnimationState();
    public final AnimationState castigo = new AnimationState();
    public final AnimationState castigoOnda = new AnimationState();
    public final AnimationState sol = new AnimationState();
    public final AnimationState trompetas = new AnimationState();
    public final AnimationState ofrenda = new AnimationState();
    public final AnimationState dios = new AnimationState();
    public final AnimationState aturdido = new AnimationState();
    public final AnimationState tambaleo = new AnimationState();
    public final AnimationState grito = new AnimationState();
    public final AnimationState liberacion = new AnimationState();
    public final AnimationState espada = new AnimationState();
    public final AnimationState infernal = new AnimationState();
    public final AnimationState mar = new AnimationState();
    /** Tick del cliente en que empezo el estado actual. */
    public int inicioEstado;
    /** Ritmo de la animacion actual en el cliente (el mismo que usa el servidor). */
    public float ritmoCliente = 1.0F;
    /** Hasta cuando solo anda (la orden de pruebas "perseguir"). */
    private int soloAndarHasta;
    /**
     * El reloj de la animacion de andar (ms), en el cliente: avanza lo que anda,
     * una vuelta (dos pasos) cada NovilisGeometria.ZANCADA bloques, asi que los
     * pies van con el suelo a cualquier velocidad (con walkAnimationPos se
     * saturaba: pasado 0,25 bloques por tick los pies patinaban).
     */
    public float relojAndar;
    public float relojAndarAnt;
    /** El reloj de correr, igual (una vuelta cada NovilisGeometria.ZANCADA_CORRER bloques). */
    public float relojCorrer;
    public float relojCorrerAnt;
    /** Lo que pesa correr frente a andar (0 a 1), suavizado. */
    public float corre;
    public float correAnt;
    private boolean corriendo;
    /** Lo que pesa andar (0 quieto, 1 andando), suavizado. */
    public float andar;
    public float andarAnt;
    private float velocidadCliente;
    /** El tick (cliente) en que le prendio la Furia. */
    public int furiaDesde = -1000;
    private boolean furiaVista;
    /** Cuanto pesan andar y reposo (0 a 1): baja al empezar un ataque y sube al acabar. */
    public float pesoLibre = 1.0F;
    public float pesoLibreAnt = 1.0F;

    // --- Solo servidor ---
    private @Nullable BlockPos centro;
    private float factorGrupo = VIDA_VANILLA / VIDA;
    private int jugadoresGrupo = 1;
    private int t;
    private int duracion;
    private float ritmoEstado = 1.0F;
    private int respiro = 10;
    /** Lo que le queda en escena tras despertar (ticks): quieto, sin atacar e inmune. */
    private int escena;
    private int enfBarrido;
    private int enfCastigo = 60;
    private int enfSol = 120;
    private int enfTrompetas = 400;
    private int enfEspada = 120;
    private int enfInfernal = 300;
    private int enfMar = 300;
    private int enfOfrenda = 300;
    private int enfDios = 200;
    private int enfSombra = 600;
    private int ultimoAvisoInmune;
    private final Set<UUID> golpeados = new HashSet<>();
    /** A quienes ya lanzo un sol en este Sol x3 (para repartirlos). */
    private final List<UUID> blancosSol = new ArrayList<>();
    /** A quien va el sol que se esta formando (para irse girando hacia el). */
    private @Nullable LivingEntity solBlanco;
    private final List<Vec3> zonasDios = new ArrayList<>();
    // Las Trompetas
    private final EstatuaNovilisEntity[] estatuas = new EstatuaNovilisEntity[NUM_ESTATUAS];
    private int melodia = -1;
    // La Espada del Fuego: el rumbo, la velocidad y lo que lleva recorrido de la carrera
    private Vec3 dirCarga = Vec3.ZERO;
    private double velCarga;
    private double avanceCarga;
    private double recorrido;
    private final Set<Integer> arrollados = new HashSet<>();
    // La Furia Infernal: el salto, donde cae y el rumbo de las grietas
    private boolean saltando;
    private double gravedadSalto = 0.1;
    private @Nullable Vec3 destinoSalto;
    private @Nullable Vec3 golpeInfernal;
    private float rumboInfernal;
    // El Mar de Llamas: corre aparte del estado, como la melodia
    private int marCampo = -1;
    private final List<GrietaNovilisEntity> bocas = new ArrayList<>();
    // La Ofrenda
    private @Nullable LivingEntity presa;
    private @Nullable LivingEntity captivo;
    private int inicioCaptura;
    private char[] secuencia = new char[0];
    // La Sombra del Escudo: corre aparte del estado, como la melodia
    private int sombra = -1;
    private @Nullable SolCenitEntity solCenit;
    private final List<EgidaNovilisEntity> egidas = new ArrayList<>();
    /** Cuantas veces se ha quemado cada uno: con mas de una, ya no cae deslumbrado. */
    private final java.util.Map<UUID, Integer> quemadosSombra = new java.util.HashMap<>();

    public NovilisEntity(EntityType<? extends Monster> tipo, Level nivel) {
        super(tipo, nivel);
        this.xpReward = 500;
    }

    public static AttributeSupplier.Builder crearAtributos() {
        return Monster.createMonsterAttributes()
                .add(Attributes.MAX_HEALTH, VIDA_VANILLA)
                .add(Attributes.ARMOR, 16.0D)
                .add(Attributes.ARMOR_TOUGHNESS, 10.0D)
                .add(Attributes.ATTACK_DAMAGE, 14.0D)
                // Un caballero de 16 bloques: cada zancada son 5 bloques, pero no corre.
                .add(Attributes.MOVEMENT_SPEED, 0.27D)
                .add(Attributes.FOLLOW_RANGE, 72.0D)
                .add(Attributes.KNOCKBACK_RESISTANCE, 1.0D)
                .add(Attributes.STEP_HEIGHT, 2.0D);
    }

    @Override
    protected void defineSynchedData(SynchedEntityData.Builder datos) {
        super.defineSynchedData(datos);
        datos.define(DATA_ESTADO, DORMIDO);
        datos.define(DATA_FASE, 1);
        datos.define(DATA_FURIA, false);
        datos.define(DATA_FURIA_FIN, 0L);
        datos.define(DATA_GOLPES_ESTATUAS, 0);
        datos.define(DATA_MELODIA, -1.0F);
        datos.define(DATA_MARCA, -1);
        datos.define(DATA_OFRENDA, -1);
        datos.define(DATA_SEMILLA, 0);
        datos.define(DATA_TECLAS, 0);
        datos.define(DATA_ACIERTOS, 0);
        datos.define(DATA_SOMBRA, -1.0F);
        datos.define(DATA_SOMBRA_CUENTA, 0);
    }

    @Override
    protected void registerGoals() {
        // Sin goals de movimiento: andar lo decide customServerAiStep, que sabe
        // hasta donde le deja su correa.
        targetSelector.addGoal(1, new HurtByTargetGoal(this));
        targetSelector.addGoal(2, new NearestAttackableTargetGoal<>(this, Player.class, false));
    }

    // ------------------------------------------------------------------
    //  Lo que se lee desde fuera (el cliente, la barra, las estatuas)
    // ------------------------------------------------------------------

    public int getEstado() {
        return entityData.get(DATA_ESTADO);
    }

    /** I a IV segun la vida que le queda. */
    public int fase() {
        return entityData.get(DATA_FASE);
    }

    public boolean tieneFuria() {
        return entityData.get(DATA_FURIA);
    }

    /** El tiempo del mundo en que se le acaba la Furia (0 si no la tiene). */
    public long getFuriaFin() {
        return entityData.get(DATA_FURIA_FIN);
    }

    public int numEstatuas() {
        return NUM_ESTATUAS;
    }

    /** Golpes de la estatua i (0 a GOLPES; con GOLPES, rota). */
    public int getGolpesEstatua(int i) {
        return (entityData.get(DATA_GOLPES_ESTATUAS) >> (i * 4)) & 15;
    }

    /** Lo que va de la melodia de las Trompetas (0 a 1), o -1 si no suena. */
    public float getMelodia() {
        return entityData.get(DATA_MELODIA);
    }

    public int getIdMarca() {
        return entityData.get(DATA_MARCA);
    }

    /** A quien tiene en las manos en la Ofrenda, o -1. */
    public int getIdOfrenda() {
        return entityData.get(DATA_OFRENDA);
    }

    public int getSemillaOfrenda() {
        return entityData.get(DATA_SEMILLA);
    }

    public int getTeclasOfrenda() {
        return entityData.get(DATA_TECLAS);
    }

    public int getAciertosOfrenda() {
        return entityData.get(DATA_ACIERTOS);
    }

    /** Lo que va de la Sombra del Escudo (0 a 1), o -1 si no hay: mientras, su sol esta en el cielo. */
    public float getSombra() {
        return entityData.get(DATA_SOMBRA);
    }

    /** Cuantos estan a la sombra ahora. */
    public int getSombraDentro() {
        return entityData.get(DATA_SOMBRA_CUENTA) & 255;
    }

    /** Cuantos pelean (los que deberian estar a la sombra). */
    public int getSombraTotal() {
        return (entityData.get(DATA_SOMBRA_CUENTA) >> 8) & 255;
    }

    /** Lo que lleva de la secuencia el atrapado (0 a 1): la barra de los demas. */
    public float getProgresoOfrenda() {
        int n = getTeclasOfrenda();
        return n <= 0 || getIdOfrenda() < 0 ? 0.0F : Mth.clamp((float) getAciertosOfrenda() / n, 0.0F, 1.0F);
    }

    public @Nullable BlockPos getCentro() {
        return centro;
    }

    /**
     * La secuencia de la Ofrenda: n letras de la A a la Z sacadas de la semilla,
     * sin repetir la misma dos veces seguidas. El servidor y el cliente la sacan
     * igual, asi que por la red solo va la semilla.
     */
    public static char[] teclasOfrenda(int semilla, int n) {
        java.util.Random r = new java.util.Random(semilla);
        char[] out = new char[Math.max(0, n)];
        char antes = 0;
        for (int i = 0; i < out.length; i++) {
            char c;
            do {
                c = (char) ('A' + r.nextInt(26));
            } while (c == antes);
            out[i] = c;
            antes = c;
        }
        return out;
    }

    private int faseSegunVida() {
        float k = getHealth() / getMaxHealth();
        return k > 0.75F ? 1 : k > 0.5F ? 2 : k > 0.25F ? 3 : 4;
    }

    private void ponerEstado(int estado, int dur) {
        entityData.set(DATA_ESTADO, estado);
        t = 0;
        ritmoEstado = ritmo(estado, fase(), tieneFuria());
        avisoEstado = aviso(estado);
        duracion = (int) Math.ceil(dur / ritmoEstado) + avisoEstado;
    }

    /**
     * Lo rapido que van los ataques en cada fase: x1, x1,12, x1,25 y x1,4, y un
     * 25 % mas con la Furia. Lo que cuenta con el tiempo de los jugadores (la
     * Ofrenda, las Trompetas, la carga de la Espada del Fuego, el salto de la
     * Furia Infernal, el Mar de Llamas) no se acelera nunca. El cliente usa el
     * mismo numero para la animacion.
     */
    public static float ritmo(int estado, int fase, boolean furia) {
        float k = switch (estado) {
            case BARRIDO, CASTIGO, CASTIGO_ONDA, SOL, DIOS ->
                    new float[]{1.0F, 1.0F, 1.12F, 1.18F, 1.28F}[Mth.clamp(fase, 1, 4)];
            default -> 1.0F;
        };
        return furia && k > 1.0F ? k * FURIA_RITMO : (furia && (estado == BARRIDO || estado == SOL) ? FURIA_RITMO : k);
    }

    /** Ticks de animacion transcurridos en el estado (los reales por el ritmo). */
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
            case BARRIDO -> 10;
            default -> 0;
        };
    }

    /** La espera de aviso del estado actual (ticks reales). */
    private int avisoEstado;

    /** Si este tick cruza el tick de animacion k: los golpes caen donde la animacion. */
    private boolean cruza(int k) {
        return (t - 1 - avisoEstado) * ritmoEstado < k && (t - avisoEstado) * ritmoEstado >= k;
    }

    /** El dano de un ataque en la fase actual; con la Furia, un 35 % mas. */
    public float dano(float[] porFase) {
        float d = porFase[Mth.clamp(fase(), 1, 4) - 1];
        return tieneFuria() ? d * FURIA_DANO : d;
    }

    /** Si el Dios de la Guerra mata a este (quemadura grave). */
    public boolean mataDios(LivingEntity v) {
        return QuemaduraEffect.nivel(v) >= 3;
    }

    /** Pega con su fuego: el dano y los niveles de quemadura. */
    public boolean quemar(ServerLevel nivel, LivingEntity v, ResourceKey<DamageType> tipo, float cantidad, int niveles,
                          @Nullable Entity directo) {
        if (!esPresa(v)) {
            return false;
        }
        boolean entra = v.hurtServer(nivel, NovilisDanos.fuente(nivel, tipo, directo == null ? this : directo, this), cantidad);
        if (entra && niveles > 0) {
            QuemaduraEffect.quemar(v, niveles);
        }
        return entra;
    }

    // ------------------------------------------------------------------
    //  Cliente: animaciones y las particulas que no gastan red
    // ------------------------------------------------------------------

    @Override
    public void onSyncedDataUpdated(EntityDataAccessor<?> dato) {
        super.onSyncedDataUpdated(dato);
        if (DATA_ESTADO.equals(dato) && level().isClientSide()) {
            arrancarAnimacion();
        }
    }

    private AnimationState[] acciones() {
        return new AnimationState[]{dormido, despertar, barrido, castigo, castigoOnda, sol, trompetas, ofrenda,
                dios, aturdido, tambaleo, grito, espada, infernal, mar};
    }

    private @Nullable AnimationState animacionDe(int estado) {
        return switch (estado) {
            case DORMIDO -> dormido;
            case DESPERTAR -> despertar;
            case BARRIDO -> barrido;
            case CASTIGO -> castigo;
            case CASTIGO_ONDA -> castigoOnda;
            case SOL -> sol;
            case TROMPETAS, SOMBRA -> trompetas;
            case OFRENDA -> ofrenda;
            case DIOS -> dios;
            case ATURDIDO -> aturdido;
            case TAMBALEO -> tambaleo;
            case GRITO -> grito;
            case ESPADA -> espada;
            case INFERNAL -> infernal;
            case MAR -> mar;
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
        relojAndarAnt = relojAndar;
        relojCorrerAnt = relojCorrer;
        andarAnt = andar;
        correAnt = corre;
        double vx = getX() - xo;
        double vz = getZ() - zo;
        float v = getEstado() == LIBRE && !muriendo ? (float) Math.sqrt(vx * vx + vz * vz) : 0.0F;
        velocidadCliente += (v - velocidadCliente) * 0.35F;
        relojAndar += 1000.0F * NovilisGeometria.PERIODO_ANDAR * velocidadCliente / NovilisGeometria.ZANCADA;
        relojCorrer += 1000.0F * NovilisGeometria.PERIODO_CORRER * velocidadCliente / NovilisGeometria.ZANCADA_CORRER;
        float objetivoCorre = Mth.clamp((velocidadCliente - (VEL_CORRER - 0.06F)) / 0.12F, 0.0F, 1.0F);
        corre += (objetivoCorre - corre) * 0.25F;
        float objetivoAndar = Mth.clamp(velocidadCliente / 0.06F, 0.0F, 1.0F);
        andar += (objetivoAndar - andar) * 0.3F;
        if (tieneFuria() != furiaVista) {
            furiaVista = tieneFuria();
            if (furiaVista) {
                furiaDesde = tickCount;
            }
        }
        float objetivoPeso = getEstado() == LIBRE && !muriendo ? 1.0F : 0.0F;
        pesoLibre = objetivoPeso > pesoLibre ? Math.min(objetivoPeso, pesoLibre + 0.2F) : Math.max(objetivoPeso, pesoLibre - 0.25F);
        if (muriendo && !liberacion.isStarted()) {
            for (AnimationState a : acciones()) {
                a.stop();
            }
            liberacion.start(tickCount);
        }
        if (muriendo) {
            return;
        }
        int e = getEstado();
        // Las brasas que se le escapan por las grietas: pocas en la fase I, a chorros en la IV.
        int brasas = e == DORMIDO ? 1 : new int[]{0, 2, 3, 4, 6}[Mth.clamp(fase(), 1, 4)];
        for (int i = 0; i < brasas; i++) {
            if (random.nextInt(3) == 0) {
                Vec3 a = puntoMundo(new Vec3((random.nextDouble() - 0.5) * 5.0, 1.0 + random.nextDouble() * 13.5,
                        (random.nextDouble() - 0.5) * 3.0));
                level().addParticle(AtalayaParticulas.NOVILIS_BRASA, a.x, a.y, a.z, 0, 0.04 + random.nextDouble() * 0.04, 0);
            }
        }
        if (tieneFuria() && e != DORMIDO) {
            for (int i = 0; i < 3; i++) {
                Vec3 a = puntoMundo(new Vec3((random.nextDouble() - 0.5) * 5.5, 0.5 + random.nextDouble() * 15.0,
                        (random.nextDouble() - 0.5) * 3.5));
                level().addParticle(AtalayaParticulas.NOVILIS_AZUL, a.x, a.y, a.z, 0, 0.06 + random.nextDouble() * 0.04, 0);
            }
        }
        if (e == DIOS) {
            for (int i = 0; i < 4; i++) {
                Vec3 a = puntoMundo(new Vec3((random.nextDouble() - 0.5) * 5.5, 0.5 + random.nextDouble() * 15.0,
                        (random.nextDouble() - 0.5) * 3.5));
                level().addParticle(AtalayaParticulas.NOVILIS_CARMESI, a.x, a.y, a.z, 0, 0.07 + random.nextDouble() * 0.05, 0);
            }
        }
        if (e == ESPADA && tickCount - inicioEstado < NovilisGeometria.ESPADA_SALE && tickCount % 2 == 0) {
            // La carga: brasas que se levantan por los cantos del carril.
            double a = random.nextDouble() * ESPADA_LARGO;
            double l = (random.nextBoolean() ? 1 : -1) * ESPADA_ANCHO * 0.5;
            Vec3 c = puntoMundo(new Vec3(l, 0.15, a));
            level().addParticle(AtalayaParticulas.NOVILIS_BRASA, c.x, c.y, c.z, 0, 0.05 + random.nextDouble() * 0.04, 0);
        }
        if (e == ATURDIDO && tickCount % 4 == 0) {
            Vec3 c = puntoMundo(NovilisGeometria.CABEZA).add(0, -2.0, 0);
            level().addParticle(AtalayaParticulas.NOVILIS_HUMO, c.x, c.y, c.z, 0, 0.05, 0);
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
        if (getEstado() != DORMIDO && !isDeadOrDying()) {
            int nueva = faseSegunVida();
            if (nueva > fase()) {
                alCambiarFase(nivel, nueva);
            }
        }
        LivingEntity objetivo = getTarget();
        if (objetivo != null && (!objetivo.isAlive() || objetivo.distanceToSqr(Vec3.atCenterOf(centro)) > LEJOS * LEJOS)) {
            setTarget(null);
            objetivo = null;
        }
        if (getEstado() != DORMIDO && !isDeadOrDying()) {
            objetivo = PresasJefe.revisar(nivel, this, objetivo, Vec3.atCenterOf(centro), LEJOS);
            // La Muralla de Jade: si un tanque le provoca, ese es su objetivo.
            objetivo = com.atalaya.habilidad.Provocacion.objetivo(this, objetivo, com.atalaya.habilidad.Provocacion.ALCANCE);
            if (objetivo != null && getTarget() != objetivo) {
                setTarget(objetivo);
            }
        }

        if (respiro > 0) respiro--;
        if (escena > 0) escena--;
        if (enfBarrido > 0) enfBarrido--;
        if (enfCastigo > 0) enfCastigo--;
        if (enfSol > 0) enfSol--;
        if (enfTrompetas > 0) enfTrompetas--;
        if (enfEspada > 0) enfEspada--;
        if (enfInfernal > 0) enfInfernal--;
        if (enfMar > 0) enfMar--;
        if (enfOfrenda > 0) enfOfrenda--;
        if (enfDios > 0) enfDios--;
        if (enfSombra > 0) enfSombra--;

        tickMelodia(nivel);
        tickSombra(nivel);
        tickMar(nivel);

        int e = getEstado();
        t++;
        switch (e) {
            case DORMIDO -> tickDormido(nivel);
            case DESPERTAR -> tickDespertar(nivel);
            case LIBRE -> tickLibre(nivel, objetivo);
            case BARRIDO -> tickBarrido(nivel, objetivo);
            case CASTIGO, CASTIGO_ONDA -> tickCastigo(nivel, objetivo, e == CASTIGO_ONDA);
            case SOL -> tickSol(nivel, objetivo);
            case TROMPETAS -> tickTrompetas(nivel);
            case SOMBRA -> tickSombraAlza(nivel);
            case OFRENDA -> tickOfrenda(nivel);
            case DIOS -> tickDios(nivel, objetivo);
            case GRITO -> tickGrito(nivel);
            case ESPADA -> tickEspada(nivel, objetivo);
            case INFERNAL -> tickInfernal(nivel, objetivo);
            case MAR -> tickMarEstado(nivel);
            case ATURDIDO, TAMBALEO -> fijarRumbo(yBodyRot);
            default -> {
            }
        }
        if (e != LIBRE && e != DORMIDO && getEstado() == e && t >= duracion) {
            terminar(nivel);
        }
        if (getEstado() != LIBRE) {
            getNavigation().stop();
        }
    }

    /** Vuelve a LIBRE y deja un respiro antes del siguiente ataque. */
    private void terminar(ServerLevel nivel) {
        int e = getEstado();
        if (e == OFRENDA) {
            soltarCaptivo(nivel, false);
        }
        velCarga = 0.0;
        saltando = false;
        entityData.set(DATA_MARCA, -1);
        presa = null;
        ponerEstado(LIBRE, 0);
        respiro = new int[]{0, 16, 12, 11, 9}[fase()];
        if (e == DESPERTAR) {
            respiro = Math.max(respiro, PresasJefe.RESPIRO_PRESENTACION);
            escena = PresasJefe.ESCENA_QUIETO;
        }
        if (tieneFuria()) {
            respiro = (int) (respiro * FURIA_ENFRIA);
        }
    }

    private void tickLibre(ServerLevel nivel, @Nullable LivingEntity objetivo) {
        if (escena > 0) {
            // En escena tras despertar (su cartel aun se lee): ni se mueve ni ataca.
            getNavigation().stop();
            getMoveControl().setWantedPosition(getX(), getY(), getZ(), 0.0);
            setDeltaMovement(0.0, getDeltaMovement().y, 0.0);
            return;
        }
        if (objetivo == null) {
            Vec3 c = Vec3.atBottomCenterOf(centro);
            if (horizontal(position(), c) > 3.0) {
                getMoveControl().setWantedPosition(c.x, c.y, c.z, 0.8);
            }
            return;
        }
        getLookControl().setLookAt(objetivo, 20.0F, 20.0F);
        if (sombra >= 0 && solCenit != null) {
            // Con su sol en el cielo, lo mira (y como en las Trompetas, ni ataca ni se mueve).
            getLookControl().setLookAt(solCenit.getX(), solCenit.getY(), solCenit.getZ(), 10.0F, 10.0F);
        }
        if (melodia >= 0 || sombra >= 0) {
            // Mientras tocan los angeles no ataca ni se mueve (Juan, 08-10-2026): se
            // queda plantado donde esta y los dirige. La amenaza son sus pulsos.
            getNavigation().stop();
            getMoveControl().setWantedPosition(getX(), getY(), getZ(), 0.0);
            setDeltaMovement(0.0, getDeltaMovement().y, 0.0);
            return;
        }
        if (respiro <= 0 && tickCount >= soloAndarHasta && elegirAtaque(nivel, objetivo)) {
            return;
        }
        double lejos = horizontal(position(), objetivo.position());
        if (lejos > CORRE_DESDE) {
            corriendo = true;
        } else if (lejos < ANDA_DESDE) {
            corriendo = false;
        }
        if (lejos > 11.0) {
            Vec3 c = Vec3.atBottomCenterOf(centro);
            Vec3 destino = objetivo.position();
            Vec3 desde = new Vec3(destino.x - c.x, 0, destino.z - c.z);
            if (desde.length() > CORREA) {
                desde = desde.normalize().scale(CORREA);
            }
            Vec3 punto = new Vec3(c.x + desde.x, getY(), c.z + desde.z);
            if (horizontal(position(), punto) > 1.0) {
                double paso = corriendo ? (fase() == 4 ? CORRE_IV : CORRE) : ANDA * (fase() == 4 ? 1.1 : 1.0);
                getMoveControl().setWantedPosition(punto.x, punto.y, punto.z, paso * (tieneFuria() ? FURIA_ANDA : 1.0));
            }
        }
    }

    private boolean elegirAtaque(ServerLevel nivel, LivingEntity objetivo) {
        int fase = fase();
        double d = horizontal(position(), objetivo.position());
        List<int[]> opciones = new ArrayList<>();
        boolean campo = melodia >= 0 || sombra >= 0 || marCampo >= 0;
        LivingEntity lejos = presaEntre(nivel, 8.0, 30.0, objetivo);
        if (enfBarrido <= 0 && d < 16) opciones.add(new int[]{BARRIDO, 5});
        if (enfCastigo <= 0 && !presas(nivel, 48).isEmpty()) opciones.add(new int[]{fase >= 2 ? CASTIGO_ONDA : CASTIGO, 4});
        if (enfEspada <= 0 && lejos != null) opciones.add(new int[]{ESPADA, 4});
        if (fase >= 2 && enfSol <= 0 && !presas(nivel, 44).isEmpty()) opciones.add(new int[]{SOL, 3});
        if (fase >= 2 && enfTrompetas <= 0 && !campo) opciones.add(new int[]{TROMPETAS, 2});
        if (fase >= 2 && enfSombra <= 0 && !campo && !presas(nivel, 48).isEmpty()) opciones.add(new int[]{SOMBRA, 3});
        if (fase >= 3 && enfInfernal <= 0 && lejos != null) opciones.add(new int[]{INFERNAL, 3});
        if (fase >= 3 && enfOfrenda <= 0 && presaOfrenda(nivel) != null) opciones.add(new int[]{OFRENDA, 2});
        if (fase >= 4 && enfMar <= 0 && !campo) opciones.add(new int[]{MAR, 3});
        if (fase >= 4 && enfDios <= 0) opciones.add(new int[]{DIOS, 3});
        if (opciones.isEmpty()) {
            return false;
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
        if (elegido == ESPADA || elegido == INFERNAL) {
            // A uno que este a media distancia (ni encima ni fuera de su alcance).
            presa = lejos;
        }
        if (elegido == BARRIDO) {
            // Al mas cercano (antes, uno al azar a 30 bloques: tajaba al aire).
            List<LivingEntity> cerca = presas(nivel, 16);
            cerca.sort(java.util.Comparator.comparingDouble(this::distanceToSqr));
            if (!cerca.isEmpty()) {
                setTarget(com.atalaya.habilidad.Provocacion.objetivo(this, cerca.get(0), 16));
            }
        }
        return iniciar(nivel, elegido);
    }

    /** Uno al azar entre min y max bloques (si no hay, el objetivo si esta en ese tramo). */
    private @Nullable LivingEntity presaEntre(ServerLevel nivel, double min, double max, @Nullable LivingEntity objetivo) {
        List<LivingEntity> todos = new ArrayList<>();
        for (LivingEntity v : presas(nivel, max)) {
            if (horizontal(position(), v.position()) >= min) {
                todos.add(v);
            }
        }
        if (!todos.isEmpty()) {
            return todos.get(random.nextInt(todos.size()));
        }
        if (objetivo != null) {
            double d = horizontal(position(), objetivo.position());
            if (d >= min && d <= max) {
                return objetivo;
            }
        }
        return null;
    }

    /** Arranca un ataque. */
    private boolean iniciar(ServerLevel nivel, int ataque) {
        // Cada fase todo vuelve antes: en la IV, con un 40 % menos de espera.
        float k = new float[]{1.0F, 1.0F, 0.85F, 0.78F, 0.68F}[Mth.clamp(fase(), 1, 4)];
        if (tieneFuria()) {
            k *= FURIA_ENFRIA;
        }
        switch (ataque) {
            case BARRIDO -> {
                enfBarrido = (int) (90 * k);
                ponerEstado(BARRIDO, NovilisGeometria.DURACION_BARRIDO);
            }
            case CASTIGO, CASTIGO_ONDA -> {
                enfCastigo = (int) (220 * k);
                ponerEstado(ataque, ataque == CASTIGO_ONDA ? NovilisGeometria.DURACION_CASTIGO_ONDA
                        : NovilisGeometria.DURACION_CASTIGO);
                sonido(AtalayaSonidos.NOVILIS_CASTIGO_ALZA, 5.0F);
            }
            case SOL -> {
                enfSol = (int) (300 * k);
                blancosSol.clear();
                solBlanco = null;
                ponerEstado(SOL, NovilisGeometria.DURACION_SOL);
                sonido(AtalayaSonidos.NOVILIS_SOL_FORMA, 4.0F);
            }
            case TROMPETAS -> {
                enfTrompetas = (int) (1800 * k);
                ponerEstado(TROMPETAS, NovilisGeometria.DURACION_TROMPETAS);
                sonido(AtalayaSonidos.NOVILIS_RUGIDO, 6.0F);
            }
            case SOMBRA -> {
                enfSombra = (int) (1500 * k);
                ponerEstado(SOMBRA, NovilisGeometria.DURACION_TROMPETAS);
                sonido(AtalayaSonidos.NOVILIS_SOL_FORMA, 6.0F);
            }
            case ESPADA -> {
                enfEspada = (int) (320 * k);
                velCarga = 0.0;
                ponerEstado(ESPADA, NovilisGeometria.DURACION_ESPADA);
                sonido(AtalayaSonidos.NOVILIS_CARGA, 5.0F);
            }
            case INFERNAL -> {
                enfInfernal = (int) (420 * k);
                destinoSalto = null;
                golpeInfernal = null;
                saltando = false;
                ponerEstado(INFERNAL, NovilisGeometria.DURACION_INFERNAL);
                sonido(AtalayaSonidos.NOVILIS_RUGIDO, 5.0F);
            }
            case MAR -> {
                enfMar = (int) (1400 * k);
                ponerEstado(MAR, NovilisGeometria.DURACION_MAR);
                sonido(AtalayaSonidos.NOVILIS_RUGIDO, 7.0F);
            }
            case OFRENDA -> {
                LivingEntity p = presaOfrenda(nivel);
                if (p == null) {
                    return false;
                }
                enfOfrenda = (int) (900 * k);
                presa = p;
                entityData.set(DATA_MARCA, p.getId());
                ponerEstado(OFRENDA, NovilisGeometria.DURACION_OFRENDA);
                duracion = Integer.MAX_VALUE;
                girarHacia(p.position(), 180.0F);
                sonido(AtalayaSonidos.NOVILIS_OFRENDA_MARCA, 5.0F);
            }
            case DIOS -> {
                enfDios = (int) (700 * k);
                zonasDios.clear();
                ponerEstado(DIOS, NovilisGeometria.DURACION_DIOS);
                sonido(AtalayaSonidos.NOVILIS_DIOS, 7.0F);
            }
            default -> {
                return false;
            }
        }
        return true;
    }

    /**
     * Para probar: fuerza un ataque o un momento del combate. Apunta al ser vivo
     * mas cercano que no sea el (un jugador o un maniqui de pruebas).
     *
     * @return falso si no reconoce la orden
     */
    public boolean forzar(ServerLevel nivel, String orden) {
        LivingEntity blanco = null;
        double mejor = 64 * 64;
        for (LivingEntity v : nivel.getEntitiesOfClass(LivingEntity.class, getBoundingBox().inflate(64), this::esPresa)) {
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
            case "furia" -> {
                ponerFuria(nivel, !tieneFuria());
                return true;
            }
            case "perseguir" -> {
                // Para ver el paso: anda tras el blanco 8 s sin atacar.
                if (getEstado() == DORMIDO) {
                    despertarse(blanco);
                }
                if (blanco != null) {
                    setTarget(blanco);
                }
                soloAndarHasta = tickCount + 160;
                return true;
            }
            case "estatua" -> {
                for (EstatuaNovilisEntity s : estatuas) {
                    if (s != null && !s.isRoto()) {
                        s.hurtServer(nivel, nivel.damageSources().generic(), 1.0F);
                        break;
                    }
                }
                return true;
            }
            default -> {
            }
        }
        int ataque = switch (orden) {
            case "barrido" -> BARRIDO;
            case "castigo" -> CASTIGO;
            case "onda" -> CASTIGO_ONDA;
            case "sol" -> SOL;
            case "trompetas" -> TROMPETAS;
            case "sombra" -> SOMBRA;
            case "espada" -> ESPADA;
            case "infernal" -> INFERNAL;
            case "mar" -> MAR;
            case "ofrenda" -> OFRENDA;
            case "dios" -> DIOS;
            case "aturdido" -> ATURDIDO;
            default -> -1;
        };
        if (ataque < 0) {
            return false;
        }
        if (getEstado() == DORMIDO) {
            despertarse(blanco);
        }
        if (blanco != null) {
            setTarget(blanco);
            girarHacia(blanco.position(), 180.0F);
        }
        if (getEstado() == OFRENDA) {
            soltarCaptivo(nivel, false);
        }
        if (ataque == ESPADA || ataque == INFERNAL) {
            presa = blanco;
        }
        if (ataque == SOMBRA || ataque == TROMPETAS) {
            acabarSombra(nivel, false, false);
        }
        entityData.set(DATA_MARCA, -1);
        velCarga = 0.0;
        saltando = false;
        if (ataque == MAR) {
            acabarMar(nivel);
        }
        // Pasa por LIBRE para que el cliente vea el cambio aunque repita ataque.
        ponerEstado(LIBRE, 0);
        if (ataque == ATURDIDO) {
            aturdir(nivel, ATURDIDO_OFRENDA);
        } else if (ataque == TROMPETAS && melodia >= 0) {
            acabarMelodia(nivel, false);
            iniciar(nivel, ataque);
        } else {
            iniciar(nivel, ataque);
        }
        return true;
    }

    // ------------------------------------------------------------------
    //  Dormido y despertar
    // ------------------------------------------------------------------

    private static final double RANGO_DESPERTAR = 40.0;

    private void tickDormido(ServerLevel nivel) {
        getNavigation().stop();
        setDeltaMovement(getDeltaMovement().multiply(0, 1, 0));
        if (t % 5 != 0) {
            return;
        }
        for (Player p : jugadores(nivel, RANGO_DESPERTAR, 0)) {
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
        ponerEstado(DESPERTAR, NovilisGeometria.DURACION_DESPERTAR);
        sonido(AtalayaSonidos.NOVILIS_DESPERTAR, 7.0F);
    }

    private void tickDespertar(ServerLevel nivel) {
        if (t == 1) {
            // La pelea empieza de verdad: cuenta al grupo y llena la vida.
            jugadoresGrupo = Math.max(1, jugadores(nivel, 80, 0).size());
            factorGrupo = VIDA_VANILLA / VIDA;
            setHealth(getMaxHealth());
            entityData.set(DATA_FASE, 1);
        }
        if (t == NovilisGeometria.DESPERTAR_RUGE) {
            sonido(AtalayaSonidos.NOVILIS_RUGIDO, 8.0F);
            // El rugido ya no empuja: en la presentacion el jefe no golpea.
            golpeSuelo(nivel, position(), 2.6F, 18.0F, 18);
            anillo(nivel, AtalayaParticulas.NOVILIS_LLAMA, 7.0, 48, 0.5);
        }
    }

    // ------------------------------------------------------------------
    //  Barrido de fuego: cuatro tajos; de cerca la hoja, de lejos el fuego vuela
    // ------------------------------------------------------------------

    private void tickBarrido(ServerLevel nivel, @Nullable LivingEntity objetivo) {
        int[] golpes = {NovilisGeometria.TAJO_1, NovilisGeometria.TAJO_2, NovilisGeometria.TAJO_3, NovilisGeometria.TAJO_4};
        // La espera de aviso: por delante de el, en el suelo, el arco de fuego hasta donde llega la hoja.
        if (t <= avisoEstado && t % 2 == 0) {
            for (int g = -105; g <= 105; g += 15) {
                float rumbo = (yBodyRot + g) * Mth.DEG_TO_RAD;
                for (double r : new double[]{RADIO_HOJA * 0.5, RADIO_HOJA}) {
                    nivel.sendParticles(AtalayaParticulas.NOVILIS_LLAMA, true, true, getX() - Mth.sin(rumbo) * r, getY() + 0.15,
                            getZ() + Mth.cos(rumbo) * r, 1, 0.1, 0.05, 0.1, 0.01);
                }
            }
        }
        // Se encara deprisa mientras carga el primer tajo y luego le sigue entre tajo y tajo.
        if (objetivo != null) {
            girarHacia(objetivo.position(), ta() < NovilisGeometria.TAJO_1 ? 24.0F : 10.0F);
        }
        for (int i = 0; i < 4; i++) {
            if (cruza(golpes[i] - 8)) {
                sonido(AtalayaSonidos.NOVILIS_TAJO, 5.0F);
            }
            if (!cruza(golpes[i])) {
                continue;
            }
            Vec3 frente = frente();
            // De cerca: la hoja, en todo lo que tiene delante.
            for (LivingEntity v : presas(nivel, RADIO_HOJA)) {
                Vec3 hacia = horizontalHacia(position(), v.position());
                if (hacia.dot(frente) < -0.25) {
                    continue;
                }
                if (quemar(nivel, v, NovilisDanos.HOJA, dano(DANO_HOJA), 0, this)) {
                    v.setDeltaMovement(hacia.x * 1.4, 0.45, hacia.z * 1.4);
                    v.hurtMarked = true;
                }
            }
            // De lejos: medias lunas de fuego que salen volando (una sola y larga en el tajo de arriba).
            float[] angulos = i == 2 ? new float[]{0.0F} : new float[]{-24.0F, 0.0F, 24.0F};
            for (float a : angulos) {
                float rumbo = yBodyRot + a;
                Vec3 dir = new Vec3(-Mth.sin(rumbo * Mth.DEG_TO_RAD), 0, Mth.cos(rumbo * Mth.DEG_TO_RAD));
                Vec3 desde = position().add(dir.scale(7.0)).add(0, 1.0, 0);
                TajoNovilisEntity.lanzar(nivel, this, desde, dir, dano(DANO_TAJO), fase(), i == 2);
            }
            sonido(AtalayaSonidos.NOVILIS_TAJO_FUEGO, 5.0F);
            Vec3 punta = puntoMundo(new Vec3[]{NovilisGeometria.PUNTA_TAJO_1, NovilisGeometria.PUNTA_TAJO_2,
                    NovilisGeometria.PUNTA_TAJO_3, NovilisGeometria.PUNTA_TAJO_4}[i]);
            nivel.sendParticles(AtalayaParticulas.NOVILIS_CHISPA, true, true, punta.x, punta.y, punta.z, 24, 1.2, 0.6, 1.2, 0.25);
            if (i == 2) {
                golpeSuelo(nivel, punta.multiply(1, 0, 1).add(0, getY(), 0), 1.6F, 8.0F, 10);
            }
        }
    }

    // ------------------------------------------------------------------
    //  Castigo solar: alza la espada al sol, un sello bajo cada uno y cae el
    //  rayo; desde la II, clava la espada y sale la onda de fuego
    // ------------------------------------------------------------------

    private void tickCastigo(ServerLevel nivel, @Nullable LivingEntity objetivo, boolean conOnda) {
        if (ta() < NovilisGeometria.CASTIGO_MARCA && objetivo != null) {
            girarHacia(objetivo.position(), 8.0F);
        } else {
            fijarRumbo(yBodyRot);
        }
        if (cruza(NovilisGeometria.CASTIGO_MARCA)) {
            int retraso = (int) Math.ceil((NovilisGeometria.CASTIGO_RAYO - NovilisGeometria.CASTIGO_MARCA) / ritmoEstado);
            for (LivingEntity v : presas(nivel, 48)) {
                SelloSolEntity.poner(nivel, this, v.position(), RADIO_RAYO, retraso, SelloSolEntity.RAYO, dano(DANO_RAYO), fase());
            }
            sonido(AtalayaSonidos.NOVILIS_CASTIGO_AVISO, 5.0F);
        }
        if (conOnda && cruza(NovilisGeometria.ONDA_CLAVA)) {
            Vec3 p = puntoMundo(NovilisGeometria.PUNTA_CLAVA);
            Vec3 suelo = new Vec3(p.x, getY(), p.z);
            OndaFuegoEntity.lanzar(nivel, this, suelo, ONDA_MAX, ONDA_VEL, dano(DANO_ONDA), fase());
            sonido(AtalayaSonidos.NOVILIS_CASTIGO_CLAVA, 8.0F);
            sonido(AtalayaSonidos.NOVILIS_ONDA, 6.0F);
            golpeSuelo(nivel, suelo, 3.0F, 20.0F, 24);
        }
    }

    // ------------------------------------------------------------------
    //  Sol x3: tres soles, cada uno a uno distinto
    // ------------------------------------------------------------------

    private void tickSol(ServerLevel nivel, @Nullable LivingEntity objetivo) {
        tickSupernova(nivel, objetivo);
        int[] lanza = {NovilisGeometria.SOL_LANZA_1, NovilisGeometria.SOL_LANZA_2, NovilisGeometria.SOL_LANZA_3};
        Vec3[] manos = {NovilisGeometria.MANO_LANZA_1, NovilisGeometria.MANO_LANZA_2, NovilisGeometria.MANO_LANZA_3};
        for (int i = 0; i < 3; i++) {
            if (cruza(lanza[i] - 10)) {
                sonido(AtalayaSonidos.NOVILIS_SOL_FORMA, 4.0F);
            }
            if (cruza(lanza[i] - 12) || (i == 0 && solBlanco == null)) {
                // A quien va este sol: se elige al formarlo, para encararlo antes de lanzar.
                solBlanco = blancoSol(nivel, objetivo);
            }
            if (!cruza(lanza[i])) {
                continue;
            }
            LivingEntity blanco = solBlanco != null && solBlanco.isAlive() ? solBlanco : blancoSol(nivel, objetivo);
            if (blanco == null) {
                continue;
            }
            girarHacia(blanco.position(), 45.0F);
            Vec3 desde = puntoMundo(manos[i]);
            SolNovilisEntity.lanzar(nivel, this, desde, sueloBajo(nivel, blanco.position()), 28, SolNovilisEntity.SOL,
                    dano(DANO_SOL), fase());
            sonido(AtalayaSonidos.NOVILIS_SOL_LANZA, 5.0F);
        }
    }

    /**
     * La Supernova (08-10-2026): tras los tres soles, alza la espada y en la otra
     * mano se le forma un cuarto, mas grande, que crece mas tiempo; lo lanza con
     * todo el cuerpo. Vuela mas despacio y revienta en un sello de 9 bloques.
     */
    private void tickSupernova(ServerLevel nivel, @Nullable LivingEntity objetivo) {
        if (cruza(NovilisGeometria.SOL_NOVA_FORMA)) {
            sonido(AtalayaSonidos.NOVILIS_SOL_FORMA, 7.0F);
            solBlanco = objetivo != null && objetivo.isAlive() ? objetivo : blancoSol(nivel, objetivo);
        }
        if (ta() > NovilisGeometria.SOL_NOVA_FORMA && ta() < NovilisGeometria.SOL_LANZA_4 && solBlanco != null) {
            girarHacia(solBlanco.position(), 8.0F);
            if (t % 3 == 0) {
                Vec3 m = puntoMundo(NovilisGeometria.MANO_NOVA);
                nivel.sendParticles(AtalayaParticulas.NOVILIS_CHISPA, true, true, m.x, m.y, m.z, 3, 1.4, 1.4, 1.4, 0.15);
            }
        }
        if (!cruza(NovilisGeometria.SOL_LANZA_4)) {
            return;
        }
        LivingEntity blanco = solBlanco != null && solBlanco.isAlive() ? solBlanco : blancoSol(nivel, objetivo);
        if (blanco == null) {
            return;
        }
        girarHacia(blanco.position(), 45.0F);
        SolNovilisEntity.lanzar(nivel, this, puntoMundo(NovilisGeometria.MANO_LANZA_4), sueloBajo(nivel, blanco.position()), 44,
                SolNovilisEntity.SUPERNOVA, dano(DANO_SUPERNOVA), fase());
        sonido(AtalayaSonidos.NOVILIS_SOL_LANZA, 8.0F);
    }

    private @Nullable LivingEntity blancoSol(ServerLevel nivel, @Nullable LivingEntity objetivo) {
        List<LivingEntity> todos = presas(nivel, 44);
        Collections.shuffle(todos, new java.util.Random(random.nextLong()));
        for (LivingEntity v : todos) {
            if (!blancosSol.contains(v.getUUID())) {
                blancosSol.add(v.getUUID());
                return v;
            }
        }
        return !todos.isEmpty() ? todos.get(0) : objetivo;
    }

    // ------------------------------------------------------------------
    //  Trompetas del Apocalipsis: cuatro estatuas y su melodia
    // ------------------------------------------------------------------

    private void tickTrompetas(ServerLevel nivel) {
        fijarRumbo(yBodyRot);
        if (!cruza(NovilisGeometria.TROMPETAS_ALZA)) {
            return;
        }
        acabarMelodia(nivel, false);
        Vec3 c = Vec3.atBottomCenterOf(centro);
        for (int i = 0; i < NUM_ESTATUAS; i++) {
            double a = Math.PI / 2 * i + Math.PI / 4;
            Vec3 donde = sueloBajo(nivel, new Vec3(c.x + Math.cos(a) * RADIO_ESTATUAS, c.y, c.z + Math.sin(a) * RADIO_ESTATUAS));
            float mira = (float) (Mth.atan2(c.z - donde.z, c.x - donde.x) * Mth.RAD_TO_DEG) - 90.0F;
            estatuas[i] = EstatuaNovilisEntity.alzar(nivel, this, donde, i, mira);
        }
        entityData.set(DATA_GOLPES_ESTATUAS, 0);
        melodia = 0;
        entityData.set(DATA_MELODIA, 0.0F);
        sonido(AtalayaSonidos.NOVILIS_ESTATUAS, 7.0F);
    }

    /** La melodia corre aparte del estado: mientras suena, el sigue peleando. */
    private void tickMelodia(ServerLevel nivel) {
        if (melodia < 0) {
            return;
        }
        melodia++;
        entityData.set(DATA_MELODIA, Math.min(1.0F, (float) melodia / MELODIA));
        boolean queda = false;
        for (EstatuaNovilisEntity s : estatuas) {
            if (s != null && !s.isRoto() && !s.isRemoved()) {
                queda = true;
            }
        }
        if (!queda) {
            // Las cuatro rotas a tiempo: la melodia se rompe y no pasa nada.
            acabarMelodia(nivel, false);
            return;
        }
        if (melodia >= MELODIA) {
            // Ha sonado entera: la Furia.
            acabarMelodia(nivel, true);
        }
    }

    private void acabarMelodia(ServerLevel nivel, boolean furia) {
        if (melodia < 0) {
            return;
        }
        melodia = -1;
        entityData.set(DATA_MELODIA, -1.0F);
        for (int i = 0; i < NUM_ESTATUAS; i++) {
            if (estatuas[i] != null) {
                estatuas[i].desmontar(nivel);
                estatuas[i] = null;
            }
            cortarSonido(nivel, melodiaDe(i));
        }
        if (furia && !tieneFuria()) {
            ponerFuria(nivel, true);
            if (getEstado() == LIBRE) {
                ponerEstado(GRITO, NovilisGeometria.DURACION_GRITO);
            }
        }
    }

    public static SoundEvent melodiaDe(int i) {
        return switch (i) {
            case 0 -> AtalayaSonidos.NOVILIS_MELODIA_1;
            case 1 -> AtalayaSonidos.NOVILIS_MELODIA_2;
            case 2 -> AtalayaSonidos.NOVILIS_MELODIA_3;
            default -> AtalayaSonidos.NOVILIS_MELODIA_4;
        };
    }

    /** Una estatua ha recibido un golpe (EstatuaNovilisEntity). */
    void alGolpearEstatua(int i, int golpes) {
        int v = entityData.get(DATA_GOLPES_ESTATUAS) & ~(15 << (i * 4));
        entityData.set(DATA_GOLPES_ESTATUAS, v | (Math.min(GOLPES, golpes) << (i * 4)));
    }

    /** Una estatua se ha roto: su trompeta se calla. */
    void alRomperEstatua(ServerLevel nivel, int i) {
        alGolpearEstatua(i, GOLPES);
        cortarSonido(nivel, melodiaDe(i));
    }

    // ------------------------------------------------------------------
    //  Sombra del Escudo (octubre de 2026): alza la mano y lanza su sol al
    //  cielo; 12 s abrasa a todo el que este al sol. Un tercio de los que
    //  pelean lleva la Egida: si mira al sol, da sombra detras. Si nadie se
    //  quema mas de una vez, el sol se apaga y el queda deslumbrado 4 s.
    // ------------------------------------------------------------------

    private void tickSombraAlza(ServerLevel nivel) {
        fijarRumbo(yBodyRot);
        if (cruza(NovilisGeometria.TROMPETAS_ALZA)) {
            lanzarSolCenit(nivel);
        }
    }

    private void lanzarSolCenit(ServerLevel nivel) {
        acabarSombra(nivel, false, false);
        List<LivingEntity> todos = presas(nivel, 64);
        if (todos.isEmpty() || centro == null) {
            return;
        }
        int color = tieneFuria() ? 5 : fase();
        SolCenitEntity sol = SolCenitEntity.lanzar(nivel, this, puntoMundo(NovilisGeometria.SOL_PROPIO),
                Vec3.atBottomCenterOf(centro), color);
        solCenit = sol;
        // Un tercio lleva la Egida (minimo uno; jugando solo, tu).
        Collections.shuffle(todos, new java.util.Random(random.nextLong()));
        int n = Math.max(1, (todos.size() + 2) / 3);
        for (int i = 0; i < todos.size(); i++) {
            LivingEntity v = todos.get(i);
            if (i < n) {
                egidas.add(EgidaNovilisEntity.dar(nivel, v, sol, color));
                nivel.playSound(null, v.getX(), v.getEyeY(), v.getZ(), AtalayaSonidos.NOVILIS_INMUNE, SoundSource.PLAYERS, 1.5F, 0.8F);
                nivel.sendParticles(AtalayaParticulas.NOVILIS_LUZ, true, true, v.getX(), v.getY() + 2.0, v.getZ(), 16, 0.6, 0.8, 0.6, 0.05);
                if (v instanceof Player p) {
                    p.sendOverlayMessage(Component.translatable("hud.atalaya.novilis.egida").withStyle(ChatFormatting.GOLD));
                }
            }
        }
        quemadosSombra.clear();
        sombra = 0;
        entityData.set(DATA_SOMBRA, 0.0F);
        entityData.set(DATA_SOMBRA_CUENTA, Math.min(255, todos.size()) << 8);
        sonido(AtalayaSonidos.NOVILIS_SOL_LANZA, 7.0F);
    }

    /** La Sombra corre aparte del estado: mientras su sol esta en el cielo, el se queda quieto mirandolo. */
    private void tickSombra(ServerLevel nivel) {
        if (sombra < 0) {
            return;
        }
        sombra++;
        SolCenitEntity sol = solCenit;
        if (sol == null || sol.isRemoved() || sol.getFin() >= 0) {
            acabarSombra(nivel, false, true);
            return;
        }
        egidas.removeIf(Entity::isRemoved);
        int abrasa = sombra - SolCenitEntity.SUBE;
        entityData.set(DATA_SOMBRA, Mth.clamp((float) abrasa / SolCenitEntity.ABRASA, 0.0F, 1.0F));
        Vec3 cielo = sol.position();
        List<LivingEntity> todos = presas(nivel, 64);
        if (sombra % 5 == 0) {
            int dentro = 0;
            for (LivingEntity v : todos) {
                if (aLaSombra(v, cielo)) {
                    dentro++;
                }
            }
            entityData.set(DATA_SOMBRA_CUENTA, Math.min(255, dentro) | (Math.min(255, todos.size()) << 8));
        }
        if (abrasa > 0 && abrasa % 20 == 0 && abrasa <= SolCenitEntity.ABRASA) {
            for (LivingEntity v : todos) {
                if (aLaSombra(v, cielo)) {
                    continue;
                }
                quemar(nivel, v, NovilisDanos.ABRASA, dano(DANO_ABRASA), 0, sol);
                v.setRemainingFireTicks(Math.max(v.getRemainingFireTicks(), 30));
                quemadosSombra.merge(v.getUUID(), 1, Integer::sum);
                nivel.sendParticles(AtalayaParticulas.NOVILIS_LLAMA, true, true, v.getX(), v.getY() + 1.0, v.getZ(), 10, 0.3, 0.6, 0.3, 0.03);
                if (v instanceof Player p) {
                    p.sendOverlayMessage(Component.translatable("hud.atalaya.novilis.al_sol").withStyle(ChatFormatting.GOLD));
                }
            }
            // A los portadores que no miran bien al sol: hacia que lado girarse.
            for (EgidaNovilisEntity e : egidas) {
                if (e.getPortador() instanceof Player p) {
                    Vec3 pies = p.position();
                    if (EgidaNovilisEntity.deCara(p.getYRot(), pies, cielo) < 0.8) {
                        Vec3 derecha = EgidaNovilisEntity.frente(p.getYRot() + 90.0F);
                        boolean aLaDerecha = derecha.dot(EgidaNovilisEntity.haciaSol(pies, cielo)) > 0;
                        p.sendOverlayMessage(Component.translatable(aLaDerecha ? "hud.atalaya.novilis.egida_derecha"
                                : "hud.atalaya.novilis.egida_izquierda").withStyle(ChatFormatting.GOLD));
                    }
                }
            }
        }
        if (abrasa >= SolCenitEntity.ABRASA) {
            boolean nadie = true;
            for (int q : quemadosSombra.values()) {
                if (q > 1) {
                    nadie = false;
                }
            }
            acabarSombra(nivel, nadie && !todos.isEmpty(), true);
        }
    }

    /** Si v esta a la sombra de alguna Egida. */
    private boolean aLaSombra(LivingEntity v, Vec3 sol) {
        for (EgidaNovilisEntity e : egidas) {
            LivingEntity b = e.getPortador();
            if (b != null && EgidaNovilisEntity.aLaSombra(new Vec3(b.getX(), e.getY(), b.getZ()), b.getYRot(), sol, v.position())) {
                return true;
            }
        }
        return false;
    }

    /** Se acaba: si nadie se ha quemado mas de una vez, el sol se apaga y el queda deslumbrado. */
    private void acabarSombra(ServerLevel nivel, boolean exito, boolean avisar) {
        boolean estaba = sombra >= 0;
        sombra = -1;
        entityData.set(DATA_SOMBRA, -1.0F);
        entityData.set(DATA_SOMBRA_CUENTA, 0);
        for (EgidaNovilisEntity e : egidas) {
            e.discard();
        }
        egidas.clear();
        if (solCenit != null) {
            solCenit.acabar(exito);
            solCenit = null;
        }
        quemadosSombra.clear();
        if (!estaba || !avisar || isDeadOrDying()) {
            return;
        }
        for (Player p : jugadores(nivel, 80, 0)) {
            p.sendOverlayMessage(Component.translatable(exito ? "hud.atalaya.novilis.sombra_exito" : "hud.atalaya.novilis.sombra_fallo")
                    .withStyle(exito ? ChatFormatting.GOLD : ChatFormatting.GRAY));
        }
        if (exito) {
            sonido(AtalayaSonidos.NOVILIS_SOL_APAGA, 7.0F);
            int e = getEstado();
            if (e != OFRENDA && e != DESPERTAR && e != DORMIDO) {
                aturdir(nivel, ATURDIDO_SOMBRA);
            }
        }
    }

    // ------------------------------------------------------------------
    //  Espada del Fuego (la embestida, 08-10-2026): elige a uno a media
    //  distancia y se planta 3 s cargando con la espada atras; el carril (40 x 8)
    //  se ve en el suelo y le sigue los dos primeros segundos, el ultimo queda
    //  fijo. Sale disparado arrastrando la punta: a quien pille, su cuerpo y la
    //  hoja; detras deja un camino de llamas malditas. Frena y remata con un
    //  tajo hacia arriba
    // ------------------------------------------------------------------

    private void tickEspada(ServerLevel nivel, @Nullable LivingEntity objetivo) {
        LivingEntity p = presa != null && presa.isAlive() ? presa : objetivo;
        if (ta() < NovilisGeometria.ESPADA_SALE) {
            if (p != null && t < ESPADA_SIGUE) {
                girarHacia(p.position(), 12.0F);
            } else {
                fijarRumbo(yBodyRot);
            }
            return;
        }
        if (cruza(NovilisGeometria.ESPADA_SALE)) {
            empezarEmbestida(nivel);
        }
        fijarRumbo(yBodyRot);
        if (velCarga > 0.0) {
            recorrido += avanceCarga;
            arrollar(nivel);
            boolean choca = ta() > NovilisGeometria.ESPADA_SALE + 1 && horizontalCollision && avanceCarga < velCarga * 0.35;
            boolean fuera = centro != null && horizontal(position(), Vec3.atBottomCenterOf(centro)) > CORREA + 8.0;
            if (recorrido >= ESPADA_LARGO || choca || fuera || ta() >= NovilisGeometria.ESPADA_PARA + 2) {
                velCarga = 0.0;
                golpeSuelo(nivel, position(), 1.6F, 9.0F, 18);
            }
        }
        if (cruza(NovilisGeometria.ESPADA_TAJO)) {
            remateEspada(nivel);
        }
    }

    /** Se acaba la carga: el rumbo queda fijo y sale disparado; detras prende el camino. */
    private void empezarEmbestida(ServerLevel nivel) {
        dirCarga = frente();
        velCarga = ESPADA_LARGO / Math.max(1, NovilisGeometria.ESPADA_PARA - NovilisGeometria.ESPADA_SALE);
        avanceCarga = velCarga;
        recorrido = 0.0;
        arrollados.clear();
        cortarSonido(nivel, AtalayaSonidos.NOVILIS_CARGA);
        sonido(AtalayaSonidos.NOVILIS_EMBESTIDA, 8.0F);
        sonido(AtalayaSonidos.NOVILIS_CAMINO, 5.0F);
        golpeSuelo(nivel, position(), 1.8F, 10.0F, 24);
        CaminoLlamasEntity.lanzar(nivel, this, position(), yBodyRot, ESPADA_LARGO, ESPADA_ANCHO,
                NovilisGeometria.ESPADA_PARA - NovilisGeometria.ESPADA_SALE, dano(DANO_CAMINO), tieneFuria() ? 5 : fase());
    }

    /** Su cuerpo y la hoja, a la carrera: a quien este en el carril, el golpe, fuego y fuera de su camino. */
    private void arrollar(ServerLevel nivel) {
        Vec3 f = dirCarga;
        Vec3 izq = new Vec3(f.z, 0, -f.x);
        for (LivingEntity v : nivel.getEntitiesOfClass(LivingEntity.class, getBoundingBox().inflate(8, 3, 8), this::esPresa)) {
            if (arrollados.contains(v.getId())) {
                continue;
            }
            Vec3 d = v.position().subtract(position());
            double largo = d.x * f.x + d.z * f.z;
            double lado = d.x * izq.x + d.z * izq.z;
            if (largo < -3.0 || largo > 5.0 || Math.abs(lado) > ESPADA_ANCHO * 0.5 + v.getBbWidth() * 0.5 || d.y < -1.5 || d.y > 12.0) {
                continue;
            }
            arrollados.add(v.getId());
            if (quemar(nivel, v, NovilisDanos.EMBESTIDA, dano(DANO_ESPADA), 1, this)) {
                double s = lado >= 0 ? 1.0 : -1.0;
                v.setDeltaMovement(izq.x * s * 1.3 + f.x * 0.6, 0.75, izq.z * s * 1.3 + f.z * 0.6);
                v.hurtMarked = true;
                v.igniteForSeconds(3.0F);
            }
        }
    }

    /** El tajo hacia arriba con que remata: lo que tenga delante sale por los aires. */
    private void remateEspada(ServerLevel nivel) {
        sonido(AtalayaSonidos.NOVILIS_TAJO, 5.0F);
        Vec3 frente = frente();
        for (LivingEntity v : presas(nivel, 10.0)) {
            Vec3 hacia = horizontalHacia(position(), v.position());
            if (hacia.dot(frente) < 0.2) {
                continue;
            }
            if (quemar(nivel, v, NovilisDanos.HOJA, dano(DANO_HOJA), 0, this)) {
                v.setDeltaMovement(hacia.x * 0.6, 0.95, hacia.z * 0.6);
                v.hurtMarked = true;
            }
        }
        Vec3 c = position().add(frente.scale(6.0)).add(0, 5.0, 0);
        nivel.sendParticles(AtalayaParticulas.NOVILIS_CHISPA, true, true, c.x, c.y, c.z, 30, 1.5, 3.0, 1.5, 0.3);
    }

    // ------------------------------------------------------------------
    //  Furia Infernal (08-10-2026): se agacha con la espada a dos manos,
    //  elige a uno y el sello marca donde va a caer; salta, cae clavando la
    //  espada, el suelo se abre en tres grietas que escupen lava y fuego, y al
    //  arrancarla todo revienta
    // ------------------------------------------------------------------

    private void tickInfernal(ServerLevel nivel, @Nullable LivingEntity objetivo) {
        LivingEntity p = presa != null && presa.isAlive() ? presa : objetivo;
        if (t < INFERNAL_MARCA) {
            if (p != null) {
                girarHacia(p.position(), 20.0F);
                destinoSalto = p.position();
            }
            return;
        }
        if (t == INFERNAL_MARCA) {
            // Queda fijo: el sello en el suelo y ya no le sigue.
            if (destinoSalto == null) {
                destinoSalto = position().add(frente().scale(12.0));
            }
            destinoSalto = sueloBajo(nivel, destinoSalto);
            int dura = Math.max(1, NovilisGeometria.INFERNAL_ATERRIZA - INFERNAL_MARCA);
            SelloSolEntity.poner(nivel, this, destinoSalto, RADIO_INFERNAL, dura, SelloSolEntity.AVISO_DIOS, 0.0F,
                    tieneFuria() ? 5 : fase());
            sonido(AtalayaSonidos.NOVILIS_CASTIGO_AVISO, 5.0F);
        }
        if (destinoSalto != null && ta() < NovilisGeometria.INFERNAL_DESPEGA) {
            girarHacia(destinoSalto, 30.0F);
        } else {
            fijarRumbo(yBodyRot);
        }
        if (cruza(NovilisGeometria.INFERNAL_DESPEGA) && destinoSalto != null) {
            saltar(nivel);
        }
        if (cruza(NovilisGeometria.INFERNAL_ATERRIZA)) {
            saltando = false;
            setDeltaMovement(0, Math.min(0, getDeltaMovement().y), 0);
            aterrizarInfernal(nivel);
        }
        if (cruza(NovilisGeometria.INFERNAL_EXPLOTA)) {
            explotarInfernal(nivel);
        }
    }

    /** Una parabola que sube ALTURA_SALTO y cae justo al acabar el vuelo de la animacion, con la punta en el sello. */
    private void saltar(ServerLevel nivel) {
        double vuelo = Math.max(6.0, (NovilisGeometria.INFERNAL_ATERRIZA - NovilisGeometria.INFERNAL_DESPEGA) / ritmoEstado);
        Vec3 punta = puntoMundo(NovilisGeometria.PUNTA_INFERNAL, Vec3.ZERO, yBodyRot);
        Vec3 meta = new Vec3(destinoSalto.x - punta.x, destinoSalto.y, destinoSalto.z - punta.z);
        gravedadSalto = Math.max(0.08, 8.0 * ALTURA_SALTO / (vuelo * vuelo));
        double vy = 0.5 * gravedadSalto * vuelo + (meta.y - getY()) / vuelo;
        setDeltaMovement((meta.x - getX()) / vuelo, vy, (meta.z - getZ()) / vuelo);
        saltando = true;
        sonido(AtalayaSonidos.NOVILIS_INFERNAL_SALTO, 7.0F);
        golpeSuelo(nivel, position(), 1.2F, 8.0F, 20);
    }

    /** Cae clavando la espada: el golpe alrededor de la punta y tres grietas que se abren. */
    private void aterrizarInfernal(ServerLevel nivel) {
        Vec3 punta = puntoMundo(NovilisGeometria.PUNTA_INFERNAL);
        Vec3 c = new Vec3(punta.x, getY(), punta.z);
        golpeInfernal = c;
        rumboInfernal = yBodyRot;
        sonido(AtalayaSonidos.NOVILIS_INFERNAL_GOLPE, 9.0F);
        sonido(AtalayaSonidos.NOVILIS_GRIETA, 6.0F);
        golpeSuelo(nivel, c, 3.2F, 22.0F, 60);
        for (LivingEntity v : presas(nivel, 40.0)) {
            double d = horizontal(c, v.position());
            if (d > RADIO_INFERNAL + v.getBbWidth() * 0.5 || Math.abs(v.getY() - c.y) > 4.0) {
                continue;
            }
            if (quemar(nivel, v, NovilisDanos.INFERNAL, dano(DANO_INFERNAL), 1, this)) {
                Vec3 fuera = horizontalHacia(c, v.position());
                v.setDeltaMovement(fuera.x * 1.4, 0.7, fuera.z * 1.4);
                v.hurtMarked = true;
            }
        }
        int dura = Math.max(8, (int) Math.ceil((NovilisGeometria.INFERNAL_EXPLOTA - NovilisGeometria.INFERNAL_ATERRIZA) / ritmoEstado));
        int color = tieneFuria() ? 5 : fase();
        for (int k = -1; k <= 1; k++) {
            GrietaNovilisEntity.linea(nivel, this, c, rumboInfernal + k * 120.0F, GRIETA_LARGO, 6, dura, dano(DANO_GEISER), color);
        }
    }

    /** Arranca la espada y todo revienta: en el centro y en la punta de cada grieta. */
    private void explotarInfernal(ServerLevel nivel) {
        Vec3 c = golpeInfernal != null ? golpeInfernal : position();
        sonido(AtalayaSonidos.NOVILIS_INFERNAL_EXPLOTA, 10.0F);
        explosionInfernal(nivel, c, RADIO_EXPLOSION_INFERNAL, 1.0F);
        golpeSuelo(nivel, c, 3.6F, 30.0F, 50);
        for (int k = -1; k <= 1; k++) {
            float b = (rumboInfernal + k * 120.0F) * Mth.DEG_TO_RAD;
            Vec3 fin = c.add(-Mth.sin(b) * GRIETA_LARGO, 0, Mth.cos(b) * GRIETA_LARGO);
            explosionInfernal(nivel, sueloBajo(nivel, fin), 4.5F, 0.7F);
        }
    }

    private void explosionInfernal(ServerLevel nivel, Vec3 c, float radio, float k) {
        nivel.sendParticles(AtalayaParticulas.NOVILIS_LLAMA, true, true, c.x, c.y + 1.5, c.z, (int) (radio * 10), radio * 0.4, 1.5,
                radio * 0.4, 0.3);
        nivel.sendParticles(AtalayaParticulas.NOVILIS_CHISPA, true, true, c.x, c.y + 1.5, c.z, (int) (radio * 6), radio * 0.3, 1.2,
                radio * 0.3, 0.6);
        nivel.sendParticles(AtalayaParticulas.NOVILIS_HUMO, true, true, c.x, c.y + 2.0, c.z, (int) (radio * 3), radio * 0.3, 1.0,
                radio * 0.3, 0.04);
        nivel.sendParticles(AtalayaParticulas.NOVILIS_ONDA, true, true, c.x, c.y + 0.12, c.z, 0, 2.0, radio * 2.2, 0.0, 1.0);
        for (LivingEntity v : presas(nivel, 48.0)) {
            double d = horizontal(c, v.position());
            if (d > radio + v.getBbWidth() * 0.5 || v.getY() - c.y > 6.0 || v.getY() - c.y < -3.0) {
                continue;
            }
            if (quemar(nivel, v, NovilisDanos.INFERNAL, dano(DANO_EXPLOSION_INFERNAL) * k, 2, this)) {
                Vec3 fuera = horizontalHacia(c, v.position());
                v.setDeltaMovement(fuera.x * 1.8 * k, 0.9, fuera.z * 1.8 * k);
                v.hurtMarked = true;
                v.igniteForSeconds(5.0F);
            }
        }
    }

    // ------------------------------------------------------------------
    //  Mar de Llamas (08-10-2026): alza la espada a dos manos y la hunde de
    //  rodilla; el suelo se raja por toda la arena. Cada 4,5 s se raja otra vez
    //  (una boca bajo cada uno y otras sueltas): primero brilla la grieta y,
    //  1,5 s despues, sale el fuego, que se queda hasta que acaba el Mar (15 s).
    //  Corre aparte del estado: mientras, el sigue peleando
    // ------------------------------------------------------------------

    private void tickMarEstado(ServerLevel nivel) {
        fijarRumbo(yBodyRot);
        if (cruza(NovilisGeometria.MAR_CLAVA)) {
            empezarMar(nivel);
        }
    }

    private void empezarMar(ServerLevel nivel) {
        acabarMar(nivel);
        marCampo = 0;
        Vec3 p = puntoMundo(NovilisGeometria.PUNTA_MAR);
        sonido(AtalayaSonidos.NOVILIS_CASTIGO_CLAVA, 8.0F);
        sonido(AtalayaSonidos.NOVILIS_MAR, 10.0F);
        golpeSuelo(nivel, new Vec3(p.x, getY(), p.z), 3.0F, 40.0F, 40);
        olaMar(nivel);
    }

    /** El Mar corre aparte del estado: cada MAR_OLA ticks, otra tanda de bocas. */
    private void tickMar(ServerLevel nivel) {
        if (marCampo < 0) {
            return;
        }
        marCampo++;
        bocas.removeIf(Entity::isRemoved);
        if (marCampo % MAR_OLA == 0 && marCampo < MAR_DURA - MAR_AVISO - 20) {
            olaMar(nivel);
        }
        if (marCampo >= MAR_DURA + GrietaNovilisEntity.APAGA) {
            marCampo = -1;
            bocas.clear();
        }
    }

    /** Una tanda: una boca bajo cada uno (hasta MAR_JUGADORES) y otras sueltas por la arena. */
    private void olaMar(ServerLevel nivel) {
        int dura = Math.max(MAR_AVISO + 20, MAR_DURA - marCampo);
        int color = tieneFuria() ? 5 : fase();
        float d = dano(DANO_MAR);
        List<LivingEntity> todos = presas(nivel, 56.0);
        Collections.shuffle(todos, new java.util.Random(random.nextLong()));
        for (int i = 0; i < Math.min(MAR_JUGADORES, todos.size()); i++) {
            bocas.add(GrietaNovilisEntity.boca(nivel, this, sueloBajo(nivel, todos.get(i).position()), MAR_RADIO, MAR_AVISO, dura,
                    d, color));
        }
        Vec3 c = Vec3.atBottomCenterOf(centro != null ? centro : blockPosition());
        for (int k = 0; k < MAR_SUELTAS; k++) {
            double a = random.nextDouble() * Math.PI * 2;
            double r = 8.0 + random.nextDouble() * 30.0;
            Vec3 p = new Vec3(c.x + Math.cos(a) * r, c.y, c.z + Math.sin(a) * r);
            if (horizontal(p, position()) < 7.0) {
                continue;
            }
            bocas.add(GrietaNovilisEntity.boca(nivel, this, sueloBajo(nivel, p), MAR_RADIO, MAR_AVISO, dura, d, color));
        }
        sonido(AtalayaSonidos.NOVILIS_GRIETA, 8.0F);
    }

    private void acabarMar(ServerLevel nivel) {
        marCampo = -1;
        for (GrietaNovilisEntity b : bocas) {
            b.discard();
        }
        bocas.clear();
    }

    /**
     * En el salto de la Furia Infernal vuela con su propia gravedad; en la
     * embestida va en linea recta a su velocidad (sube escalones de dos bloques
     * y cae si hay hueco); en el resto, como cualquiera.
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
    //  Ofrenda al Sol: coge a uno, lo alza y el atrapado sigue las teclas
    // ------------------------------------------------------------------

    private @Nullable LivingEntity presaOfrenda(ServerLevel nivel) {
        List<Player> js = jugadores(nivel, 40, 0);
        if (!js.isEmpty()) {
            return js.get(random.nextInt(js.size()));
        }
        List<LivingEntity> otros = presas(nivel, 40);
        return otros.isEmpty() ? null : otros.get(random.nextInt(otros.size()));
    }

    private void tickOfrenda(ServerLevel nivel) {
        if (captivo == null) {
            // El haz de su sol senala a quien va: no se puede evitar.
            if (presa == null || !presa.isAlive() || presa.isRemoved()) {
                terminar(nivel);
                return;
            }
            girarHacia(presa.position(), 10.0F);
            if (cruza(NovilisGeometria.OFRENDA_AGARRA)) {
                capturar(nivel, presa);
            }
            return;
        }
        fijarRumbo(yBodyRot);
        if (!captivo.isAlive() || captivo.isRemoved()) {
            // Se ha muerto (o se ha ido) en sus manos: la ofrenda se ha cumplido.
            soltarCaptivo(nivel, false);
            ponerFuria(nivel, true);
            ponerEstado(GRITO, NovilisGeometria.DURACION_GRITO);
            return;
        }
        sujetar(nivel);
        // Primero los 3 s para prepararse (sin calor); luego las teclas y el calor.
        int dentro = t - inicioCaptura - OFRENDA_PREPARA;
        if (dentro > 0 && dentro % 20 == 0) {
            captivo.hurtServer(nivel, NovilisDanos.fuente(nivel, NovilisDanos.CALOR, this, this),
                    captivo.getMaxHealth() * OFRENDA_CALOR);
        }
        if (dentro > OFRENDA_TIEMPO + OFRENDA_GRACIA) {
            fallarOfrenda(nivel);
        }
    }

    private void capturar(ServerLevel nivel, LivingEntity v) {
        captivo = v;
        presa = null;
        entityData.set(DATA_MARCA, -1);
        inicioCaptura = t;
        int semilla = random.nextInt();
        int n = fase() >= 4 ? TECLAS_IV : TECLAS_III;
        secuencia = teclasOfrenda(semilla, n);
        entityData.set(DATA_SEMILLA, semilla);
        entityData.set(DATA_TECLAS, n);
        entityData.set(DATA_ACIERTOS, 0);
        entityData.set(DATA_OFRENDA, v.getId());
        AttributeInstance camara = v.getAttribute(Attributes.CAMERA_DISTANCE);
        if (camara != null && !camara.hasModifier(ID_CAMARA_OFRENDA)) {
            camara.addTransientModifier(new AttributeModifier(ID_CAMARA_OFRENDA, CAMARA_OFRENDA,
                    AttributeModifier.Operation.ADD_VALUE));
        }
        sonido(AtalayaSonidos.NOVILIS_OFRENDA_AGARRA, 6.0F);
        sujetar(nivel);
    }

    /** Lo pone entre sus manos (la cintura en el punto medio de los punos). */
    private void sujetar(ServerLevel nivel) {
        if (captivo == null) {
            return;
        }
        Vec3 manos = puntoMundo(NovilisGeometria.manosOfrenda(ta()));
        double x = manos.x;
        double y = manos.y - captivo.getBbHeight() * 0.5;
        double z = manos.z;
        if (captivo instanceof ServerPlayer sp) {
            sp.teleportTo(nivel, x, y, z, Set.of(Relative.X_ROT, Relative.Y_ROT), 0.0F, 0.0F, false);
        } else {
            captivo.setPos(x, y, z);
        }
        captivo.setDeltaMovement(Vec3.ZERO);
        captivo.resetFallDistance();
    }

    /** Lo suelta: si salio bien, cae despacio; si no, ya le ha llegado lo suyo. */
    private void soltarCaptivo(ServerLevel nivel, boolean exito) {
        LivingEntity v = captivo;
        captivo = null;
        entityData.set(DATA_OFRENDA, -1);
        entityData.set(DATA_TECLAS, 0);
        entityData.set(DATA_ACIERTOS, 0);
        AttributeInstance camara = v != null ? v.getAttribute(Attributes.CAMERA_DISTANCE) : null;
        if (camara != null) {
            camara.removeModifier(ID_CAMARA_OFRENDA);
        }
        if (v != null && v.isAlive()) {
            v.addEffect(new MobEffectInstance(MobEffects.SLOW_FALLING, exito ? 80 : 60, 0));
            Vec3 fuera = frente().scale(exito ? 0.8 : 0.4);
            v.setDeltaMovement(fuera.x, 0.3, fuera.z);
            v.hurtMarked = true;
        }
    }

    private void exitoOfrenda(ServerLevel nivel) {
        Vec3 p = captivo != null ? captivo.position() : position();
        nivel.playSound(null, p.x, p.y, p.z, AtalayaSonidos.NOVILIS_OFRENDA_LIBRE, SoundSource.HOSTILE, 5.0F, 1.0F);
        nivel.sendParticles(AtalayaParticulas.NOVILIS_LUZ, true, true, p.x, p.y + 1, p.z, 40, 1.0, 1.0, 1.0, 0.15);
        soltarCaptivo(nivel, true);
        aturdir(nivel, ATURDIDO_OFRENDA);
    }

    private void fallarOfrenda(ServerLevel nivel) {
        LivingEntity v = captivo;
        if (v != null) {
            nivel.playSound(null, v.getX(), v.getY(), v.getZ(), AtalayaSonidos.NOVILIS_OFRENDA_FALLO, SoundSource.HOSTILE,
                    5.0F, 1.0F);
            nivel.sendParticles(AtalayaParticulas.NOVILIS_LLAMA, true, true, v.getX(), v.getY() + 1, v.getZ(), 50, 0.6, 1.0,
                    0.6, 0.2);
            v.hurtServer(nivel, NovilisDanos.fuente(nivel, NovilisDanos.MORTAL, this, this), MORTAL);
        }
        soltarCaptivo(nivel, false);
        ponerFuria(nivel, true);
        ponerEstado(GRITO, NovilisGeometria.DURACION_GRITO);
    }

    /** Llega una tecla del atrapado (AtalayaRed.OfrendaTecla). */
    public static void alPulsarTecla(ServerPlayer p, int jefe, int indice, boolean bien) {
        if (!(p.level() instanceof ServerLevel nivel) || !(nivel.getEntity(jefe) instanceof NovilisEntity n)) {
            return;
        }
        if (n.getEstado() != OFRENDA || n.captivo != p) {
            return;
        }
        if (n.t - n.inicioCaptura < OFRENDA_PREPARA - 4) {
            // Aun preparandose: el cliente no las manda, pero por si acaso no cuentan.
            return;
        }
        if (!bien) {
            n.fallarOfrenda(nivel);
            return;
        }
        int hechas = n.getAciertosOfrenda();
        if (indice != hechas) {
            return;
        }
        hechas++;
        n.entityData.set(DATA_ACIERTOS, hechas);
        if (hechas >= n.getTeclasOfrenda()) {
            n.exitoOfrenda(nivel);
        }
    }

    // ------------------------------------------------------------------
    //  Dios de la Guerra: llamas carmesi y soles a tres zonas
    // ------------------------------------------------------------------

    private void tickDios(ServerLevel nivel, @Nullable LivingEntity objetivo) {
        fijarRumbo(yBodyRot);
        int[] lanza = {NovilisGeometria.DIOS_LANZA_1, NovilisGeometria.DIOS_LANZA_2, NovilisGeometria.DIOS_LANZA_3};
        // Antes de cada lanzamiento se gira hacia su zona (antes los tiraba de espaldas).
        for (int i = 0; i < 3 && i < zonasDios.size(); i++) {
            if (ta() > lanza[i] - 14 && ta() <= lanza[i]) {
                girarHacia(zonasDios.get(i), 18.0F);
                break;
            }
        }
        Vec3[] manos = {NovilisGeometria.DIOS_LANZA_1_P, NovilisGeometria.DIOS_LANZA_2_P, NovilisGeometria.DIOS_LANZA_3_P};
        if (cruza(NovilisGeometria.DIOS_MARCA)) {
            // Tres zonas: sobre los jugadores (al azar) y, si faltan, en cualquier sitio del altar.
            List<LivingEntity> todos = presas(nivel, 44);
            Collections.shuffle(todos, new java.util.Random(random.nextLong()));
            Vec3 c = Vec3.atBottomCenterOf(centro);
            for (int i = 0; i < 3; i++) {
                Vec3 z;
                if (i < todos.size()) {
                    z = todos.get(i).position();
                } else {
                    double a = random.nextDouble() * Math.PI * 2;
                    double r = 8 + random.nextDouble() * 18;
                    z = new Vec3(c.x + Math.cos(a) * r, c.y, c.z + Math.sin(a) * r);
                }
                z = sueloBajo(nivel, z);
                zonasDios.add(z);
                int dura = (int) Math.ceil((lanza[i] - NovilisGeometria.DIOS_MARCA) / ritmoEstado) + 20 + 30;
                SelloSolEntity.poner(nivel, this, z, RADIO_ZONA, dura, SelloSolEntity.AVISO_DIOS, 0.0F, 4);
            }
            sonido(AtalayaSonidos.NOVILIS_DIOS_AVISO, 6.0F);
        }
        for (int i = 0; i < 3; i++) {
            if (cruza(lanza[i]) && i < zonasDios.size()) {
                SolNovilisEntity.lanzar(nivel, this, puntoMundo(manos[i]), zonasDios.get(i), 20, SolNovilisEntity.DIOS,
                        dano(DANO_DIOS), 4);
                sonido(AtalayaSonidos.NOVILIS_SOL_LANZA, 6.0F);
            }
        }
    }

    // ------------------------------------------------------------------
    //  Grito, aturdido, Furia y fases
    // ------------------------------------------------------------------

    private void tickGrito(ServerLevel nivel) {
        fijarRumbo(yBodyRot);
        if (cruza(NovilisGeometria.GRITO_RUGE)) {
            sonido(AtalayaSonidos.NOVILIS_GRITO, 8.0F);
            golpeSuelo(nivel, position(), 2.4F, 16.0F, 0);
            anillo(nivel, tieneFuria() ? AtalayaParticulas.NOVILIS_AZUL : AtalayaParticulas.NOVILIS_CARMESI, 6.0, 40, 0.5);
        }
    }

    /** Derribado: cae de rodilla, con dano doble; la Furia se le va. */
    private void aturdir(ServerLevel nivel, int ticks) {
        ponerFuria(nivel, false);
        velCarga = 0.0;
        saltando = false;
        ponerEstado(ATURDIDO, ticks);
        sonido(AtalayaSonidos.NOVILIS_ATURDIDO, 6.0F);
    }

    /** La Furia: el fuego se le vuelve azul. */
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
        Vec3 c = puntoMundo(NovilisGeometria.PECHO);
        if (si) {
            sonido(AtalayaSonidos.NOVILIS_FURIA, 8.0F);
            nivel.sendParticles(AtalayaParticulas.NOVILIS_AZUL, true, true, c.x, c.y, c.z, 90, 3.0, 5.0, 3.0, 0.2);
            nivel.sendParticles(AtalayaParticulas.NOVILIS_ONDA, true, true, getX(), getY() + 0.12, getZ(), 0, 2.8, 16.0, 0.0, 1.0);
        } else {
            nivel.sendParticles(AtalayaParticulas.NOVILIS_HUMO, true, true, c.x, c.y, c.z, 40, 2.5, 4.0, 2.5, 0.05);
        }
    }

    /** Pasa de fase: la armadura se raja mas y las grietas cambian de color; se tambalea. */
    private void alCambiarFase(ServerLevel nivel, int nueva) {
        entityData.set(DATA_FASE, nueva);
        Vec3 pecho = puntoMundo(NovilisGeometria.PECHO);
        nivel.playSound(null, pecho.x, pecho.y, pecho.z, AtalayaSonidos.NOVILIS_TAMBALEO, SoundSource.HOSTILE, 7.0F, 1.0F);
        nivel.sendParticles(AtalayaParticulas.NOVILIS_CHISPA, true, true, pecho.x, pecho.y, pecho.z, 50, 1.5, 2.0, 1.5, 0.4);
        nivel.sendParticles(AtalayaParticulas.NOVILIS_LLAMA, true, true, pecho.x, pecho.y, pecho.z, 40, 1.5, 2.5, 1.5, 0.2);
        nivel.sendParticles(AtalayaParticulas.NOVILIS_ONDA, true, true, getX(), getY() + 0.12, getZ(), 0, 2.6, 18.0, 0.0, 1.0);
        int e = getEstado();
        if (e == DORMIDO || e == DESPERTAR) {
            return;
        }
        if (e == OFRENDA) {
            soltarCaptivo(nivel, false);
        }
        velCarga = 0.0;
        saltando = false;
        entityData.set(DATA_MARCA, -1);
        presa = null;
        if (e != TAMBALEO) {
            ponerEstado(TAMBALEO, NovilisGeometria.DURACION_TAMBALEO);
        }
        // La primera vez que entra en una fase, lo nuevo de esa fase llega pronto.
        if (nueva == 2) {
            enfSol = Math.min(enfSol, 160);
            enfTrompetas = Math.min(enfTrompetas, 500);
            enfSombra = Math.min(enfSombra, 900);
        } else if (nueva == 3) {
            enfInfernal = Math.min(enfInfernal, 200);
            enfOfrenda = Math.min(enfOfrenda, 300);
        } else if (nueva == 4) {
            enfMar = Math.min(enfMar, 240);
            enfDios = Math.min(enfDios, 200);
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
        if (fuente.is(DamageTypes.IN_WALL) || fuente.is(DamageTypes.DROWN) || fuente.is(DamageTypes.FALL)
                || fuente.is(DamageTypes.CRAMMING) || fuente.is(DamageTypeTags.IS_FIRE)) {
            return false;
        }
        Entity causante = fuente.getEntity();
        if (PresasJefe.esJefe(causante)) {
            return false;
        }
        int e = getEstado();
        if (e == DORMIDO) {
            despertarse(causante);
            avisoInmune(nivel, causante);
            return false;
        }
        if (e == DESPERTAR || escena > 0 || e == OFRENDA) {
            // Mientras ofrece a alguien a su sol no recibe dano: lo que sirve es la
            // secuencia de teclas.
            avisoInmune(nivel, causante);
            return false;
        }
        if (e == TROMPETAS || melodia >= 0) {
            // Las Trompetas: mientras alza a los angeles y suena su melodia no se le
            // puede pegar (Juan, 08-10-2026): lo que sirve es romper las estatuas.
            avisoInmune(nivel, causante);
            return false;
        }
        if (tieneFuria()) {
            // La Furia: inmune mientras dura (30 s); lo de romper (ojos, nucleos...) va aparte.
            avisoInmune(nivel, causante);
            return false;
        }
        if (causante instanceof LivingEntity vivo && random.nextInt(4) == 0) {
            setTarget(vivo);
        }
        float k = factorGrupo * (e == ATURDIDO ? 2.0F : 1.0F);
        boolean entra = super.hurtServer(nivel, fuente, cantidad * k);
        if (entra) {
            Vec3 c = puntoMundo(NovilisGeometria.PECHO);
            nivel.sendParticles(AtalayaParticulas.NOVILIS_CHISPA, c.x, c.y, c.z, 6, 0.6, 0.6, 0.6, 0.15);
        }
        return entra;
    }

    /** Clang de armadura y chispas: se tiene que entender que no le hace nada. */
    private void avisoInmune(ServerLevel nivel, @Nullable Entity causante) {
        if (tickCount - ultimoAvisoInmune < 5) {
            return;
        }
        ultimoAvisoInmune = tickCount;
        Vec3 p = puntoMundo(NovilisGeometria.PECHO);
        if (causante != null) {
            Vec3 fuera = horizontalHacia(position(), causante.position());
            double y = Mth.clamp(causante.getEyeY(), getY() + 0.5, getY() + 14.0);
            p = new Vec3(getX() + fuera.x * 2.6, y, getZ() + fuera.z * 2.6);
        }
        nivel.playSound(null, p.x, p.y, p.z, AtalayaSonidos.NOVILIS_INMUNE, SoundSource.HOSTILE, 1.5F,
                0.9F + random.nextFloat() * 0.2F);
        nivel.sendParticles(AtalayaParticulas.NOVILIS_CHISPA, p.x, p.y, p.z, 6, 0.2, 0.2, 0.2, 0.15);
    }

    // ------------------------------------------------------------------
    //  La liberacion: su "muerte". Cae de rodilla sobre la espada, su sol se
    //  vuelve de oro y se deshace en brasas y luz
    // ------------------------------------------------------------------

    @Override
    public void kill(ServerLevel nivel) {
        limpiar(nivel);
        discard();
    }

    @Override
    public void die(DamageSource fuente) {
        super.die(fuente);
        if (level() instanceof ServerLevel nivel) {
            limpiar(nivel);
        }
    }

    /** Ya se ha apuntado como el de su tipo en el mundo (JefesUnicos). */
    private boolean admitido;

    @Override
    public void remove(RemovalReason motivo) {
        if (motivo.shouldDestroy() && admitido && level() instanceof ServerLevel nivelFuera) {
            JefesUnicos.soltar(nivelFuera, this);
        }
        if (level() instanceof ServerLevel nivel) {
            limpiar(nivel);
        }
        super.remove(motivo);
    }

    /** Suelta al atrapado y quita estatuas, la melodia, el sol del cielo y las bocas de fuego. */
    private void limpiar(ServerLevel nivel) {
        if (captivo != null) {
            soltarCaptivo(nivel, false);
        }
        acabarMar(nivel);
        acabarMelodia(nivel, false);
        acabarSombra(nivel, false, false);
        entityData.set(DATA_MARCA, -1);
    }

    @Override
    protected void tickDeath() {
        ++deathTime;
        if (!(level() instanceof ServerLevel nivel) || isRemoved()) {
            return;
        }
        if (deathTime == 1) {
            sonido(AtalayaSonidos.NOVILIS_LIBERACION, 6.0F);
        }
        if (deathTime == 30) {
            playSound(AtalayaSonidos.NOVILIS_PASO, 5.0F, 0.7F);
            golpeSuelo(nivel, position(), 2.2F, 9.0F, 16);
        }
        Vec3 c = puntoMundo(NovilisGeometria.PECHO);
        if (deathTime == NovilisGeometria.LIBERACION_ORO) {
            nivel.sendParticles(AtalayaParticulas.NOVILIS_LUZ, c.x, c.y, c.z, 60, 1.5, 2.0, 1.5, 0.08);
        }
        if (deathTime > NovilisGeometria.LIBERACION_ORO && deathTime % 3 == 0) {
            nivel.sendParticles(AtalayaParticulas.NOVILIS_LUZ, c.x, c.y, c.z, 3, 1.8, 2.5, 1.8, 0.01);
        }
        if (deathTime == 150) {
            Vec3 m = position();
            for (Player p : nivel.getEntitiesOfClass(Player.class, new AABB(m, m).inflate(80))) {
                p.addEffect(new MobEffectInstance(BendicionSolEffect.BENDICION, 20 * 60 * 10, 0), this);
                QuemaduraEffect.apagar(p);
            }
        }
        if (deathTime == 160) {
            sonido(AtalayaSonidos.NOVILIS_DISOLVER, 5.0F);
        }
        if (deathTime >= NovilisGeometria.DURACION_LIBERACION) {
            golpeSuelo(nivel, position(), 1.2F, 9.0F, 0);
            nivel.sendParticles(AtalayaParticulas.NOVILIS_BRASA, getX(), getY() + 7.0, getZ(), 120, 3.0, 6.0, 3.0, 0.08);
            nivel.sendParticles(AtalayaParticulas.NOVILIS_LUZ, getX(), getY() + 8.0, getZ(), 90, 3.0, 6.0, 3.0, 0.05);
            remove(RemovalReason.KILLED);
        }
    }

    // ------------------------------------------------------------------
    //  Geometria: del espacio del cuerpo (NovilisGeometria) al mundo
    // ------------------------------------------------------------------

    public Vec3 puntoMundo(Vec3 local) {
        return puntoMundo(local, position(), yBodyRot);
    }

    public static Vec3 puntoMundo(Vec3 local, Vec3 pies, float rumboCuerpo) {
        float b = rumboCuerpo * Mth.DEG_TO_RAD;
        double c = Mth.cos(b);
        double s = Mth.sin(b);
        return new Vec3(pies.x + local.x * c - local.z * s, pies.y + local.y, pies.z + local.x * s + local.z * c);
    }

    private Vec3 frente() {
        float b = yBodyRot * Mth.DEG_TO_RAD;
        return new Vec3(-Mth.sin(b), 0, Mth.cos(b));
    }

    private float rumboHacia(Vec3 p) {
        return (float) (Mth.atan2(p.z - getZ(), p.x - getX()) * Mth.RAD_TO_DEG) - 90.0F;
    }

    private void girarHacia(Vec3 p, float paso) {
        float deseado = rumboHacia(p);
        float actual = getYRot();
        float nuevo = actual + Mth.clamp(Mth.wrapDegrees(deseado - actual), -paso, paso);
        fijarRumbo(nuevo);
    }

    private void fijarRumbo(float r) {
        setYRot(r);
        yBodyRot = r;
        yHeadRot = r;
    }

    private static double horizontal(Vec3 a, Vec3 b) {
        double dx = a.x - b.x;
        double dz = a.z - b.z;
        return Math.sqrt(dx * dx + dz * dz);
    }

    static Vec3 horizontalHacia(Vec3 desde, Vec3 hasta) {
        Vec3 d = new Vec3(hasta.x - desde.x, 0, hasta.z - desde.z);
        return d.lengthSqr() < 1.0E-4 ? new Vec3(1, 0, 0) : d.normalize();
    }

    /** El suelo bajo un punto (la cima de lo que hay), para posar marcas, estatuas y fuentes. */
    static Vec3 sueloBajo(ServerLevel nivel, Vec3 p) {
        int y = nivel.getHeight(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, Mth.floor(p.x), Mth.floor(p.z));
        // Si el punto esta muy por debajo (una cueva), se queda donde esta.
        return y > p.y + 6 ? p : new Vec3(p.x, y, p.z);
    }

    /** Lo que sus ataques pueden golpear: solo jugadores (y maniquies de prueba), nunca otro jefe (PresasJefe.presa). */
    boolean esPresa(LivingEntity v) {
        return v != this && PresasJefe.presa(v);
    }

    /** Jugadores (que no sean creativo ni espectador) entre min y max bloques de el. */
    private List<Player> jugadores(ServerLevel nivel, double max, double min) {
        List<Player> out = new ArrayList<>();
        for (Player p : nivel.getEntitiesOfClass(Player.class, getBoundingBox().inflate(max))) {
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

    /** A quien pega: los jugadores; sin jugadores (pruebas con maniquies), lo vivo de alrededor. */
    List<LivingEntity> presas(ServerLevel nivel, double max) {
        List<LivingEntity> out = new ArrayList<>(jugadores(nivel, max, 0));
        if (out.isEmpty()) {
            for (LivingEntity v : nivel.getEntitiesOfClass(LivingEntity.class, getBoundingBox().inflate(max, 20, max), this::esPresa)) {
                if (!(v instanceof Player) && horizontal(position(), v.position()) <= max) {
                    out.add(v);
                }
            }
        }
        return out;
    }

    /** Un golpe contra el suelo: la onda (que sacude la camara), roca y llamas. */
    void golpeSuelo(ServerLevel nivel, Vec3 p, float temblor, float radio, int rocas) {
        double y = p.y;
        nivel.sendParticles(AtalayaParticulas.NOVILIS_ONDA, true, true, p.x, y + 0.12, p.z, 0, temblor, radio, 0.0, 1.0);
        for (int i = 0; i < rocas; i++) {
            double a = random.nextDouble() * Math.PI * 2;
            double v = 0.15 + random.nextDouble() * 0.35;
            nivel.sendParticles(AtalayaParticulas.NOVILIS_ROCA, p.x, y + 0.3, p.z, 0,
                    Math.cos(a) * v, 0.35 + random.nextDouble() * 0.45, Math.sin(a) * v, 1.0);
        }
        nivel.sendParticles(AtalayaParticulas.NOVILIS_HUMO, p.x, y + 0.3, p.z, 8 + (int) (radio * 1.5), radio * 0.3, 0.2,
                radio * 0.3, 0.02);
        nivel.sendParticles(AtalayaParticulas.NOVILIS_LLAMA, p.x, y + 0.3, p.z, 6 + (int) radio, radio * 0.25, 0.1,
                radio * 0.25, 0.04);
    }

    private void anillo(ServerLevel nivel, ParticleOptions tipo, double r, int n, double vel) {
        for (int i = 0; i < n; i++) {
            double a = Math.PI * 2 * i / n;
            nivel.sendParticles(tipo, getX() + Math.cos(a) * r, getY() + 0.3, getZ() + Math.sin(a) * r, 0,
                    Math.cos(a), 0.15, Math.sin(a), vel);
        }
    }

    private void sonido(SoundEvent s, float volumen) {
        playSound(s, volumen, 1.0F);
    }

    /** Corta un sonido largo (la carga, una voz de la melodia) a quien lo este oyendo. */
    void cortarSonido(ServerLevel nivel, SoundEvent s) {
        ClientboundStopSoundPacket paquete = new ClientboundStopSoundPacket(s.location(), SoundSource.HOSTILE);
        for (ServerPlayer p : nivel.players()) {
            if (p.distanceToSqr(this) < 128 * 128) {
                p.connection.send(paquete);
            }
        }
    }

    // ------------------------------------------------------------------
    //  Sonidos propios y detalles de gigante
    // ------------------------------------------------------------------

    @Override
    protected @Nullable SoundEvent getAmbientSound() {
        return getEstado() == DORMIDO || getEstado() == LIBRE ? AtalayaSonidos.NOVILIS_AMBIENTE : null;
    }

    @Override
    public int getAmbientSoundInterval() {
        return 200;
    }

    @Override
    protected SoundEvent getHurtSound(DamageSource fuente) {
        return AtalayaSonidos.NOVILIS_HERIDO;
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
        playSound(AtalayaSonidos.NOVILIS_PASO, 2.5F, 0.9F + random.nextFloat() * 0.2F);
    }

    /** Una pisada por paso: media zancada al andar (unos 4 bloques) y al correr (unos 7). */
    @Override
    protected float nextStep() {
        boolean rapido = getDeltaMovement().horizontalDistance() > VEL_CORRER;
        return moveDist + (rapido ? NovilisGeometria.ZANCADA_CORRER : NovilisGeometria.ZANCADA) / 2.0F;
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
