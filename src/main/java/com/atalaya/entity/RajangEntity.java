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
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.storage.ValueInput;
import net.minecraft.world.level.storage.ValueOutput;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;
import org.jspecify.annotations.Nullable;

import java.util.ArrayList;
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
 *   fase I    100-75 %   Selva: Garra Terrestre, Terremoto Ancestral
 *   fase II    75-50 %   Grieta: + Sello de la Tierra (inmune mientras dura; si los
 *                        totems no caen a tiempo, el Rugido de Jade mata a todos)
 *   fase III   50-25 %   Raiz: + Cataclismo de Jade (seis oleadas de fragmentos)
 *   fase IV    25-0 %    Corazon: el peto revienta, salta sobre sus presas y
 *                        el Cataclismo vuelve antes
 * </pre>
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

    /** Vida EFECTIVA: 15 000 (Nerea 12 500, Aeralis 13 500). La de vanilla tiene tope de 1024: el dano se divide. */
    public static final float VIDA = 15000.0F;
    private static final float VIDA_VANILLA = 1024.0F;

    // --- Danos por fase (I, II, III, IV) ---
    // Pensados para 40 jugadores en hardcore con netherita entera, Proteccion IV
    // y manzana de Notch (18 corazones contando la absorcion): un golpe fuerte
    // les quita 3,5 / 5 / 7,5 / 11 corazones (6, 4, 3 y 2 golpes para matarlos;
    // sin la manzana, en la fase IV basta uno); los de area 2,5 / 4 / 5,5 / 8;
    // los que duran, 1 / 1,5 / 2 / 3 por segundo. Los tipos de dano no escalan
    // con la dificultad.
    /** El zarpazo y el pincho grande de la Garra (los pequenos, algo menos). */
    public static final float[] DANO_GARRA = {34, 42, 53, 70};
    public static final float[] DANO_TERREMOTO = {27, 37, 44, 55};
    public static final float[] DANO_SALTO = {34, 42, 53, 70};
    /** Cerca del impacto de un fragmento (de la mitad al 100 %); encima, la muerte. */
    public static final float[] DANO_FRAGMENTO = {34, 45, 54, 67};
    /**
     * El Rugido de Jade (el Sello sin romper a tiempo), en cualquier fase: mata a
     * todos los que pelean con el en su rango. Pasa la armadura, el escudo, los
     * encantamientos, los efectos y la resistencia; solo salva un totem de la
     * inmortalidad (y lo gasta).
     */
    private static final float RUGIDO_MATA = 10000.0F;
    /** La tierra aplasta: contra armadura sus golpes pegan hasta un 30 % mas. */
    private static final float PERFORA_MAXIMO = 0.3F;
    /** Piel de Jade (tras el Terremoto): recibe un 40 % menos durante 10 s. */
    private static final float PIEL_REDUCE = 0.4F;
    private static final int PIEL_TICKS = 200;
    private static final int PESO_TICKS = 160;

    /** El Sello: 45 s para subir y romper los cuatro totems. Un totem roto se queda roto. */
    public static final int SELLO_TICKS = 900;
    /** Lo que tarda en volver el Sello desde que acaba: 2 min en la II, 1,5 en la III, 1,3 en la IV. */
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
    /** El Cataclismo: tres oleadas, cada 2 s; la marca avisa 1,5 s antes. */
    /** Seis oleadas de fragmentos, una cada 2 s: 12 s de lluvia de jade. */
    private static final int OLEADAS = 6;
    private static final int CADA_OLEADA = 40;
    public static final int AVISO_FRAGMENTO = 30;

    private static final double ALCANCE_GARRA = 30.0;
    private static final double CORREA = 40.0;
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
    private int enfGarra = 30;
    private int enfTerremoto = 140;
    private int enfSello = 120;
    private int enfCataclismo = 140;
    private int enfSalto = 80;
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
    }

    @Override
    protected void registerGoals() {
        // Sin goals de movimiento: andar, correr y saltar lo decide
        // customServerAiStep, que sabe hasta donde le deja su templo.
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
        entityData.set(DATA_ESTADO, estado);
        t = 0;
        ritmoEstado = ritmo(estado, fase());
        duracion = (int) Math.ceil(dur / ritmoEstado);
    }

    /** Lo rapido que van sus ataques: x1,05 en la fase I hasta x1,45 en la IV. El cliente usa el mismo numero. */
    public static float ritmo(int estado, int fase) {
        return switch (estado) {
            case GARRA, TERREMOTO, SALTO, CATACLISMO, CATACLISMO_BAJA, RUGIDO ->
                    new float[]{1.0F, 1.05F, 1.15F, 1.3F, 1.45F}[Mth.clamp(fase, 1, 4)];
            default -> 1.0F;
        };
    }

    private float ta() {
        return t * ritmoEstado;
    }

    private boolean cruza(int k) {
        return (t - 1) * ritmoEstado < k && t * ritmoEstado >= k;
    }

    /** Lo que pega a v un golpe de dano base "dano": la tierra aplasta la armadura, hasta un 30 % mas. */
    public static float contraArmadura(LivingEntity v, float dano) {
        float armadura = v.getArmorValue();
        float dureza = (float) v.getAttributeValue(Attributes.ARMOR_TOUGHNESS);
        return dano * (1.0F + Math.min(PERFORA_MAXIMO, armadura * 0.012F + dureza * 0.01F));
    }

    /** El dano de un ataque en la fase actual: cada ataque lleva el suyo de la fase I a la IV. */
    public float dano(float[] porFase) {
        return porFase[Mth.clamp(fase(), 1, 4) - 1];
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
                cataclismoBaja, aturdido, paralizado, salto, tambaleo};
    }

    private @Nullable AnimationState animacionDe(int estado) {
        return switch (estado) {
            case DORMIDO -> dormido;
            case DESPERTAR -> despertar;
            case GARRA -> garra;
            case TERREMOTO -> terremoto;
            case RUGIDO -> rugido;
            case SELLO -> sello;
            case CATACLISMO -> cataclismo;
            case CATACLISMO_SOSTIENE -> cataclismoSostiene;
            case CATACLISMO_BAJA -> cataclismoBaja;
            case ATURDIDO -> aturdido;
            case PARALIZADO -> paralizado;
            case SALTO -> salto;
            case TAMBALEO -> tambaleo;
            default -> null;
        };
    }

    private void arrancarAnimacion() {
        for (AnimationState a : acciones()) {
            a.stop();
        }
        inicioEstado = tickCount;
        ritmoCliente = ritmo(getEstado(), fase());
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
        // resbalen: al paso las zarpas recorren 0.16 bloques por tick y al galope 0.89.
        relojAndar += 50.0F * andar * Mth.clamp(velocidad / 0.16F, 0.4F, 1.6F);
        relojCorrer += 50.0F * Mth.clamp(velocidad / 0.89F, 0.3F, 1.2F);
        // Pisadas: dos por ciclo (las manos de cada lado) al andar, una por ciclo al galope.
        if (velocidad > 0.03F) {
            boolean corre = velocidad > 0.25F;
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
            case ATURDIDO, PARALIZADO -> {
                if (tickCount % 5 == 0) {
                    Vec3 c = puntoMundo(RajangGeometria.CABEZA).add(0, e == ATURDIDO ? -3.5 : 0.5, 0);
                    double a = tickCount * 0.3;
                    level().addParticle(AtalayaParticulas.RAJANG_JADE, c.x + Math.cos(a) * 1.4, c.y + 1.2, c.z + Math.sin(a) * 1.4, 0, 0.02, 0);
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
        if (respiro > 0) respiro--;
        if (enfGarra > 0) enfGarra--;
        if (enfTerremoto > 0) enfTerremoto--;
        if (enfSello > 0) enfSello--;
        if (enfCataclismo > 0) enfCataclismo--;
        if (enfSalto > 0) enfSalto--;
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
            default -> {
            }
        }
        if (e != LIBRE && e != DORMIDO && getEstado() == e && t >= duracion) {
            alAcabar(nivel, e);
        }
        if (getEstado() != LIBRE) {
            quieto();
            if (!saltando) {
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
                ponerEstado(CATACLISMO_SOSTIENE, OLEADAS * CADA_OLEADA + AVISO_FRAGMENTO + 6);
                mato = false;
            }
            case CATACLISMO_SOSTIENE -> {
                ponerEstado(CATACLISMO_BAJA, RajangGeometria.DURACION_CATACLISMO_BAJA);
            }
            case CATACLISMO_BAJA -> {
                if (mato) {
                    // Se ha cobrado una vida: recupera un 5 %.
                    heal(getMaxHealth() * 0.05F);
                    sonido(AtalayaSonidos.RAJANG_CURA, 5.0F);
                    Vec3 c = puntoMundo(RajangGeometria.PECHO);
                    nivel.sendParticles(AtalayaParticulas.RAJANG_CHISPA, true, true, c.x, c.y, c.z, 40, 2.0, 2.0, 2.0, 0.08);
                    terminar();
                } else {
                    // Nadie ha caido: se queda paralizado, con la piedra trabada.
                    ponerEstado(PARALIZADO, RajangGeometria.DURACION_PARALIZADO);
                    sonido(AtalayaSonidos.RAJANG_PARALIZADO, 5.0F);
                }
            }
            case SALTO -> {
                saltando = false;
                terminar();
            }
            default -> terminar();
        }
    }

    private void terminar() {
        ponerEstado(LIBRE, 0);
        presa = null;
        entityData.set(DATA_OBJETIVO, -1);
        respiro = new int[]{0, 18, 14, 10, 7}[fase()];
    }

    /** Cada fase todo vuelve antes: en la IV, con un 36 % menos de espera. */
    private float enfriamiento() {
        return new float[]{1.0F, 1.0F, 0.88F, 0.76F, 0.64F}[Mth.clamp(fase(), 1, 4)];
    }

    // ------------------------------------------------------------------
    //  Libre: corre, anda y elige el siguiente golpe
    // ------------------------------------------------------------------

    private void tickLibre(ServerLevel nivel, @Nullable LivingEntity objetivo) {
        Vec3 c = Vec3.atBottomCenterOf(centro);
        if (objetivo == null) {
            if (horizontal(position(), c) > 4.0) {
                getMoveControl().setWantedPosition(c.x, c.y, c.z, 0.8);
            }
            return;
        }
        double d = horizontal(position(), objetivo.position());
        // Hacia su presa, sin salir de su templo: corre si esta lejos, anda si
        // esta a media distancia, y de cerca se planta mirandola.
        Vec3 meta = objetivo.position();
        Vec3 rel = new Vec3(meta.x - c.x, 0, meta.z - c.z);
        if (rel.length() > CORREA) {
            rel = rel.normalize().scale(CORREA);
            meta = new Vec3(c.x + rel.x, meta.y, c.z + rel.z);
        }
        if (d > 16.0) {
            getMoveControl().setWantedPosition(meta.x, meta.y, meta.z, fase() >= 4 ? 1.9 : 1.6);
        } else if (d > 7.0) {
            getMoveControl().setWantedPosition(meta.x, meta.y, meta.z, 0.75);
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
        if (fase >= 4 && enfSalto <= 0 && d > 8.0 && d < 26.0) opciones.add(new int[]{SALTO, 4});
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
            // La garra va a alguien a tiro, al azar entre los que tiene delante.
            List<Player> cerca = jugadores(nivel, ALCANCE_GARRA, 0);
            if (!cerca.isEmpty()) {
                objetivo = cerca.get(random.nextInt(cerca.size()));
                setTarget(objetivo);
            }
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
                ponerEstado(TERREMOTO, RajangGeometria.DURACION_TERREMOTO);
                sonido(AtalayaSonidos.RAJANG_RUGIDO, 5.0F);
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
                // Persigue al ser vivo mas lejano (para ver el paso y el galope).
                LivingEntity lejos = null;
                double max = 0;
                for (LivingEntity v : nivel.getEntitiesOfClass(LivingEntity.class, getBoundingBox().inflate(56), this::esPresa)) {
                    double d = v.distanceToSqr(this);
                    if (d > max) {
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
            case "romper" -> {
                // Rompe los totems que queden en pie (para ver el final bueno del Sello).
                for (TotemSelloEntity tot : new ArrayList<>(totems)) {
                    if (!tot.isRoto()) {
                        tot.romper(nivel);
                    }
                }
                return true;
            }
            default -> {
            }
        }
        int ataque = switch (orden) {
            case "garra" -> GARRA;
            case "terremoto" -> TERREMOTO;
            case "sello" -> RUGIDO;
            case "cataclismo" -> CATACLISMO;
            case "salto" -> SALTO;
            case "aturdido" -> ATURDIDO;
            case "paralizado" -> PARALIZADO;
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
            if (hasLineOfSight(p)) {
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
        sonido(AtalayaSonidos.RAJANG_DESPERTAR, 8.0F);
    }

    private void tickDespertar(ServerLevel nivel) {
        if (t == 1) {
            jugadoresGrupo = Math.max(1, jugadores(nivel, 80, 0).size());
            factorGrupo = VIDA_VANILLA / VIDA;
            setHealth(getMaxHealth());
            entityData.set(DATA_FASE, 1);
        }
        if (t == RajangGeometria.DESPERTAR_SE_ALZA) {
            // Se pone en pie: la piedra cruje y se le cae el polvo de siglos.
            Vec3 c = puntoMundo(RajangGeometria.LOMO);
            nivel.sendParticles(AtalayaParticulas.RAJANG_POLVO, true, true, c.x, c.y, c.z, 60, 4.0, 2.0, 6.0, 0.04);
            nivel.sendParticles(AtalayaParticulas.RAJANG_HOJA, true, true, c.x, c.y + 2, c.z, 30, 4.0, 1.0, 6.0, 0.02);
            golpeSuelo(nivel, position(), 1.2F, 10.0F, 20);
        }
        if (t == RajangGeometria.DESPERTAR_RUGE) {
            for (Player p : jugadores(nivel, 16, 0)) {
                Vec3 fuera = horizontalHacia(position(), p.position());
                p.setDeltaMovement(fuera.x * 1.3, 0.5, fuera.z * 1.3);
                p.hurtMarked = true;
            }
            Vec3 b = puntoMundo(RajangGeometria.BOCA_RUGIDO);
            nivel.sendParticles(AtalayaParticulas.RAJANG_ONDA, true, true, b.x, getY() + 0.1, b.z, 0, 2.6, 18.0, 0.0, 1.0);
            nivel.sendParticles(AtalayaParticulas.RAJANG_CHISPA, true, true, b.x, b.y, b.z, 30, 1.0, 1.0, 1.0, 0.15);
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
        if (destino != null && ta() >= RajangGeometria.GARRA_ALZA && ta() < RajangGeometria.GARRA_GOLPE && t % 2 == 0) {
            Vec3 desde = puntoMundo(RajangGeometria.ZARPA_GARRA);
            double y0 = sueloBajo(nivel, destino.x, destino.y + 2, destino.z);
            float k = (ta() - RajangGeometria.GARRA_ALZA) / Math.max(1.0F, RajangGeometria.GARRA_GOLPE - RajangGeometria.GARRA_ALZA);
            Vec3 p = desde.lerp(new Vec3(destino.x, y0, destino.z), k);
            nivel.sendParticles(AtalayaParticulas.RAJANG_GRIETA, true, true, p.x, sueloBajo(nivel, p.x, p.y + 2, p.z) + 0.06, p.z,
                    0, 1.6, 40.0, 0.0, 1.0);
            if (t % 6 == 0) {
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
     * lo barre hacia el lado.
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
            Vec3 barre = f.scale(0.7).add(izq.scale(1.2));
            v.setDeltaMovement(barre.x, 0.55, barre.z);
            v.hurtMarked = true;
            nivel.sendParticles(AtalayaParticulas.RAJANG_CHISPA, true, true, v.getX(), v.getY() + 1.0, v.getZ(), 10, 0.3, 0.5, 0.3, 0.12);
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
            nivel.sendParticles(AtalayaParticulas.RAJANG_LASTRE, true, true, p.getX(), p.getY() + 0.06, p.getZ(), 0, 1.4, 60.0, 0.0, 1.0);
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
            PilarTierraEntity.avisar(nivel, this, new Vec3(p.x, y, p.z), 0.8F + random.nextFloat() * 0.45F, 6 + i * 3,
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
        int aguanta = 6 + jugadoresGrupo / 4;
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
                plataformas.add(PlataformaSelloEntity.piedra(nivel, this, p, y0 + sube * (k + 1), PIEDRA_ANCHO, arriba + 4 + k * 3));
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
    }

    /** Un totem roto (lo avisa el propio totem). */
    public void alRomperTotem(ServerLevel nivel, TotemSelloEntity tot) {
        if (getEstado() != SELLO) {
            return;
        }
        entityData.set(DATA_TOTEMS, getTotemsRotos() | (1 << tot.getIndice()));
        boolean todos = totems.size() == 4;
        for (TotemSelloEntity x : totems) {
            todos &= x.isRoto();
        }
        if (todos) {
            // El sello se rompe: las columnas se hunden y el cae aturdido.
            cancelarSello(nivel, true);
            ponerEstado(ATURDIDO, RajangGeometria.DURACION_ATURDIDO);
            sonido(AtalayaSonidos.RAJANG_ATURDIDO, 6.0F);
            sonido(AtalayaSonidos.RAJANG_RUGIDO, 5.0F);
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
            v.hurtServer(nivel, fuente, RUGIDO_MATA);
            v.setDeltaMovement(fuera.x * 1.6, 0.7, fuera.z * 1.6);
            v.hurtMarked = true;
            nivel.sendParticles(AtalayaParticulas.RAJANG_CHISPA, true, true, v.getX(), v.getY() + 1, v.getZ(), 10, 0.4, 0.6, 0.4, 0.1);
        }
        cancelarSello(nivel, true);
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
        int extra = Math.min(40, 10 + jugadoresGrupo / 2 + 3 * fase());
        for (int i = 0; i < extra; i++) {
            double a = random.nextDouble() * Math.PI * 2;
            double d = 6.0 + random.nextDouble() * 30.0;
            blancos.add(new Vec3(c.x + Math.cos(a) * d, c.y, c.z + Math.sin(a) * d));
        }
        for (Vec3 p : blancos) {
            double y = sueloBajo(nivel, p.x, p.y + 3, p.z);
            float tam = 1.0F + random.nextFloat() * 0.6F;
            nivel.sendParticles(AtalayaParticulas.RAJANG_MARCA, true, true, p.x, y + 0.08, p.z, 0, 1.6 + tam, AVISO_FRAGMENTO, 0.0, 1.0);
            FragmentoJadeEntity.caer(nivel, this, new Vec3(p.x, y, p.z), AVISO_FRAGMENTO, tam, dano(DANO_FRAGMENTO));
        }
        nivel.playSound(null, getX(), getY() + 10, getZ(), AtalayaSonidos.RAJANG_MARCA, SoundSource.HOSTILE, 6.0F, 1.0F);
        sonido(AtalayaSonidos.RAJANG_RUGIDO, 5.0F);
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

    /** En el salto vuela con su propia gravedad; en el resto, como cualquiera. */
    @Override
    public void travel(Vec3 entrada) {
        if (saltando) {
            Vec3 v = getDeltaMovement();
            move(MoverType.SELF, v);
            setDeltaMovement(v.x, v.y - gravedadSalto, v.z);
            return;
        }
        super.travel(entrada);
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
    //  Las cajas de la cabeza y la grupa
    // ------------------------------------------------------------------

    private void crearPartes(ServerLevel nivel) {
        partes.add(RajangParteEntity.crear(nivel, this, "cabeza", 3.6F, 3.6F));
        partes.add(RajangParteEntity.crear(nivel, this, "grupa", 5.0F, 5.0F));
        moverPartes();
    }

    private void moverPartes() {
        int e = getEstado();
        boolean tumbado = e == DORMIDO || e == ATURDIDO || isDeadOrDying();
        for (RajangParteEntity p : partes) {
            Vec3 local;
            if (p.getNombre().equals("cabeza")) {
                local = (e == CATACLISMO_SOSTIENE || e == CATACLISMO) ? RajangGeometria.BOCA_CATACLISMO : RajangGeometria.CABEZA;
                if (tumbado) {
                    local = new Vec3(local.x, 2.6, local.z);
                }
            } else {
                local = RajangGeometria.GRUPA;
                if (tumbado) {
                    local = new Vec3(local.x, 2.2, local.z);
                }
            }
            Vec3 w = puntoMundo(local);
            p.colocar(w.x, w.y - p.getBbHeight() / 2, w.z);
        }
    }

    /** El dano que llega por la cabeza o la grupa. */
    public boolean hurtDesdeParte(ServerLevel nivel, RajangParteEntity parte, DamageSource fuente, float cantidad) {
        return hurtServer(nivel, fuente, cantidad);
    }

    @Override
    public void remove(RemovalReason motivo) {
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
        if (causante instanceof RajangEntity || directo instanceof PicoTierraEntity || directo instanceof PilarTierraEntity
                || directo instanceof FragmentoJadeEntity) {
            return false;
        }
        int e = getEstado();
        if (e == DORMIDO) {
            despertarse(causante);
            avisoInmune(nivel, causante);
            return false;
        }
        if (e == DESPERTAR) {
            avisoInmune(nivel, causante);
            return false;
        }
        if (e == SELLO || e == RUGIDO) {
            // Mientras sostiene el Sello la tierra lo cubre entero: no le entra nada,
            // lo unico que sirve es romper los totems.
            avisoInmune(nivel, causante);
            return false;
        }
        if (causante instanceof LivingEntity vivo && random.nextInt(4) == 0 && e == LIBRE) {
            setTarget(vivo);
        }
        float k = factorGrupo;
        if (e == ATURDIDO || e == PARALIZADO) {
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

    /** Lo que sus ataques pueden golpear: todo lo vivo menos el y los jugadores en creativo o espectador. */
    public boolean esPresa(LivingEntity v) {
        if (v == this || v instanceof RajangEntity || !v.isAlive()) {
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
    }

    @Override
    protected void readAdditionalSaveData(ValueInput entrada) {
        super.readAdditionalSaveData(entrada);
        centro = entrada.read("centro", BlockPos.CODEC).orElse(null);
        factorGrupo = entrada.getFloatOr("factor_grupo", VIDA_VANILLA / VIDA);
        jugadoresGrupo = entrada.getIntOr("jugadores_grupo", 1);
        entityData.set(DATA_FASE, entrada.getIntOr("fase", 1));
        ponerEstado(entrada.getBooleanOr("dormido", true) ? DORMIDO : LIBRE, 0);
    }
}
