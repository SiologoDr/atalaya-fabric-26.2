package com.atalaya.entity;

import com.atalaya.effect.BendicionMareasEffect;
import com.atalaya.effect.CorrienteAbismalEffect;
import com.atalaya.particula.AtalayaParticulas;
import com.atalaya.sonido.AtalayaSonidos;
import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
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
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.target.HurtByTargetGoal;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.projectile.Projectile;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.ClipContext;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.storage.ValueInput;
import net.minecraft.world.level.storage.ValueOutput;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;
import org.jspecify.annotations.Nullable;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.UUID;

/**
 * Nerea, Guardian de los Mares: el primero de los cuatro jefes elementales.
 *
 * La Maldicion del Corazon lo consumio y lo hizo mas fuerte. Esta pensado
 * para un grupo grande (30-40 jugadores): la vida que aguanta y el alcance de
 * sus ataques crecen con la gente que lo despierta. Nace inmovil, encadenado,
 * hasta que ve a alguien; se invoca con su huevo generador.
 *
 * Las fases van por la vida que le queda. Con cada una salta una de las
 * cadenas del pecho y el corazon maldito se raja un poco mas y se apaga: al
 * final, sin cadenas, se libera. No muere: se arrodilla y entrega lo que
 * guardaba.
 *
 * <pre>
 *   fase I    100-75 %   Rompeolas (tres olas), Remolino, Burbujas bomba
 *   fase II    75-50 %   + Molino de cadenas, Arpon (un gancho por cada 10)
 *   fase III   50-25 %   + Mirada del Abismo
 *   fase IV    25-0 %    las costillas se abren: todo mas seguido y cada
 *                        25 s cae de rodillas agotado (dano doble)
 * </pre>
 *
 * Como el Vigia, el estado vive en un numero sincronizado y el cliente arranca
 * la animacion que toca al verlo cambiar. Los ticks de cada golpe y los puntos
 * del cuerpo (ojos, manos, punta del tridente) salen de {@link NereaGeometria},
 * que se genera con las mismas poses que las animaciones: lo que se ve y lo
 * que pega van siempre juntos.
 */
public class NereaEntity extends Monster {

    public static final int LIBRE = 0;
    public static final int DORMIDO = 1;
    public static final int DESPERTAR = 2;
    public static final int ROMPEOLAS = 3;
    public static final int REMOLINO = 4;
    public static final int BURBUJAS = 5;
    public static final int MOLINO = 6;
    public static final int ARPON_LANZAR = 7;
    public static final int ARPON_ESPERA = 8;
    public static final int ARPON_TIRAR = 9;
    public static final int MIRADA = 10;
    public static final int ATURDIDO = 11;
    public static final int TAMBALEO = 12;
    public static final int AGOTADO = 13;

    /**
     * Vida EFECTIVA: 12 500, la misma con cualquier numero de jugadores. La de
     * vanilla tiene tope de 1024, asi que el dano que recibe se divide para
     * que aguante esto.
     */
    public static final float VIDA = 12500.0F;
    private static final float VIDA_VANILLA = 1024.0F;
    /** Lo que suma cada fase a todos sus ataques: +8 en la II, +16 en la III, +24 en la IV. */
    public static final float DANO_POR_FASE = 8.0F;
    /** Lo que quita el Remolino por segundo a quien arrastra (sin escalar con la fase). */
    private static final float DANO_REMOLINO = 10.0F;

    // --- Numeros del boceto: se ajustan aqui tras las pruebas ---
    private static final float DANO_ROMPEOLAS = 12.0F;
    private static final float DANO_MOLINO = 10.0F;
    private static final float DANO_GANCHO = 6.0F;
    private static final float DANO_ESTOCADA = 14.0F;
    private static final float DANO_MIRADA = 18.0F;

    private static final double LARGO_OLA = 34.0;
    private static final int TICKS_OLA = 14;
    /** El Rompeolas abre tres olas en abanico: centro y a cada lado. */
    private static final float ABANICO_OLAS = 20.0F;
    /** Hasta donde arrastra el remolino (y hasta donde se ve girar el agua, en el cliente). */
    public static final double RADIO_REMOLINO = 64.0;
    /** Lo que alcanzan las cadenas del molino: las del modelo, alargadas por ESCALA_MOLINO. */
    public static final double RADIO_MOLINO = 21.0;
    /** Cuanto se alargan (y engordan) las cadenas del molino del modelo: 14,5 bloques x 1,45. */
    public static final float ESCALA_MOLINO = 1.45F;
    private static final double MOLINO_PIES = 2.8;
    private static final int ESPERA_GANCHO = 40;
    private static final int CADA_AGOTADO = 500;

    /** Lo lejos que se aparta de donde nacio: no se va de la zona del combate. */
    private static final double CORREA = 28.0;

    private static final EntityDataAccessor<Integer> DATA_ESTADO =
            SynchedEntityData.defineId(NereaEntity.class, EntityDataSerializers.INT);
    /** Fase (1-4). El modelo quita una cadena del pecho y raja el corazon con cada una. */
    private static final EntityDataAccessor<Integer> DATA_FASE =
            SynchedEntityData.defineId(NereaEntity.class, EntityDataSerializers.INT);
    /** A quien mira (la Mirada) o a quien arrastra (el Arpon). -1 si a nadie. */
    private static final EntityDataAccessor<Integer> DATA_OBJETIVO =
            SynchedEntityData.defineId(NereaEntity.class, EntityDataSerializers.INT);
    /** Ojos apagados a flechazos: bit 0 el izquierdo, bit 1 el derecho. */
    private static final EntityDataAccessor<Integer> DATA_OJOS =
            SynchedEntityData.defineId(NereaEntity.class, EntityDataSerializers.INT);

    // --- Solo cliente ---
    public final AnimationState reposo = new AnimationState();
    public final AnimationState dormido = new AnimationState();
    public final AnimationState despertar = new AnimationState();
    public final AnimationState rompeolas = new AnimationState();
    public final AnimationState remolino = new AnimationState();
    public final AnimationState burbujas = new AnimationState();
    public final AnimationState molino = new AnimationState();
    public final AnimationState arponLanzar = new AnimationState();
    public final AnimationState arponEspera = new AnimationState();
    public final AnimationState arponTirar = new AnimationState();
    public final AnimationState mirada = new AnimationState();
    public final AnimationState aturdido = new AnimationState();
    public final AnimationState tambaleo = new AnimationState();
    public final AnimationState agotado = new AnimationState();
    public final AnimationState liberacion = new AnimationState();
    /** Tick del cliente en que empezo el estado actual. */
    public int inicioEstado;
    /** Ritmo de la animacion actual en el cliente (el mismo que usa el servidor). */
    public float ritmoCliente = 1.0F;
    /**
     * Cuanto pesan andar y reposo (0 a 1). Baja en cuatro ticks al empezar un
     * ataque y sube al acabar: vanilla no mezcla animaciones, y sin esto el
     * cuerpo saltaria de la zancada a la postura del golpe de un fotograma a otro.
     */
    public float pesoLibre = 1.0F;
    public float pesoLibreAnt = 1.0F;

    // --- Solo servidor ---
    private @Nullable BlockPos centro;
    /** Por cuanto se multiplica el dano que recibe (la vida efectiva). */
    private float factorGrupo = VIDA_VANILLA / VIDA;
    private int jugadoresGrupo = 1;
    private int golpesPorOjo = 3;
    private int t;
    private int duracion;
    /** Lo rapido que va el estado actual: los ataques se aceleran con cada fase. */
    private float ritmoEstado = 1.0F;
    private int tickImpacto = -1;
    private int respiro = 10;
    private int enfRompeolas;
    private int enfRemolino = 120;
    private int enfBurbujas = 40;
    private int enfMolino;
    private int enfArpon = 40;
    private int enfMirada = 120;
    private int relojAgotado = CADA_AGOTADO;
    private int ultimoAvisoInmune;
    private int golpesOjoIzq;
    private int golpesOjoDer;
    private final List<LivingEntity> blancosBurbujas = new ArrayList<>();
    private float rumbo;
    private final Set<UUID> golpeados = new HashSet<>();
    private final Map<UUID, Integer> ultimoGolpe = new HashMap<>();
    private final List<GanchoNereaEntity> ganchos = new ArrayList<>();
    private final List<LivingEntity> enganchados = new ArrayList<>();
    private Vec3[] olaOrigenes = new Vec3[0];
    private Vec3[] olaDirs = new Vec3[0];
    private @Nullable LivingEntity presa;

    public NereaEntity(EntityType<? extends Monster> tipo, Level nivel) {
        super(tipo, nivel);
        this.xpReward = 300;
    }

    public static AttributeSupplier.Builder crearAtributos() {
        return Monster.createMonsterAttributes()
                .add(Attributes.MAX_HEALTH, VIDA_VANILLA)
                .add(Attributes.ARMOR, 14.0D)
                .add(Attributes.ARMOR_TOUGHNESS, 8.0D)
                .add(Attributes.ATTACK_DAMAGE, 12.0D)
                // Lento: menos que un jugador andando. Lo que alcanza son los
                // ataques, no las piernas.
                .add(Attributes.MOVEMENT_SPEED, 0.27D)
                .add(Attributes.FOLLOW_RANGE, 64.0D)
                .add(Attributes.KNOCKBACK_RESISTANCE, 1.0D)
                .add(Attributes.STEP_HEIGHT, 1.6D);
    }

    @Override
    protected void defineSynchedData(SynchedEntityData.Builder datos) {
        super.defineSynchedData(datos);
        // Nace inmovil: hasta que no ve a un jugador cerca, es una estatua encadenada.
        datos.define(DATA_ESTADO, DORMIDO);
        datos.define(DATA_FASE, 1);
        datos.define(DATA_OBJETIVO, -1);
        datos.define(DATA_OJOS, 0);
    }

    @Override
    protected void registerGoals() {
        // Sin goals de movimiento: con diez bloques de alto y una arena
        // redonda, andar lo decide customServerAiStep, que sabe hasta donde le
        // dejan las cadenas.
        targetSelector.addGoal(1, new HurtByTargetGoal(this));
        targetSelector.addGoal(2, new NearestAttackableTargetGoal<>(this, Player.class, false));
    }

    // ------------------------------------------------------------------
    //  Lo que se lee desde fuera (el cliente, los sellos, la arena)
    // ------------------------------------------------------------------

    public int getEstado() {
        return entityData.get(DATA_ESTADO);
    }

    /** Cadenas del pecho que le quedan: cuatro en la fase I, una en la IV. */
    public int getCadenas() {
        return isDeadOrDying() ? 0 : 5 - fase();
    }

    public int getIdObjetivo() {
        return entityData.get(DATA_OBJETIVO);
    }

    public int getOjosRotos() {
        return entityData.get(DATA_OJOS);
    }

    /** I a IV segun la vida que le queda. */
    public int fase() {
        return entityData.get(DATA_FASE);
    }

    private int faseSegunVida() {
        float k = getHealth() / getMaxHealth();
        return k > 0.75F ? 1 : k > 0.5F ? 2 : k > 0.25F ? 3 : 4;
    }

    public @Nullable BlockPos getCentro() {
        return centro;
    }

    private void ponerEstado(int estado, int dur) {
        entityData.set(DATA_ESTADO, estado);
        t = 0;
        ritmoEstado = ritmo(estado, fase());
        duracion = (int) Math.ceil(dur / ritmoEstado);
    }

    /**
     * Lo rapido que van los ataques en cada fase: x1, x1,12, x1,25 y x1,4. El
     * cliente usa el mismo numero para la velocidad de la animacion, asi que lo
     * que se ve y lo que pega siguen yendo juntos.
     */
    public static float ritmo(int estado, int fase) {
        return switch (estado) {
            case ROMPEOLAS, BURBUJAS, MOLINO, ARPON_LANZAR, ARPON_TIRAR, MIRADA ->
                    new float[]{1.0F, 1.0F, 1.12F, 1.25F, 1.4F}[Mth.clamp(fase, 1, 4)];
            default -> 1.0F;
        };
    }

    /** Ticks de animacion transcurridos en el estado (los reales por el ritmo). */
    private float ta() {
        return t * ritmoEstado;
    }

    /** Si este tick cruza el tick de animacion k: los golpes caen donde la animacion. */
    private boolean cruza(int k) {
        return (t - 1) * ritmoEstado < k && t * ritmoEstado >= k;
    }

    /** El dano de un ataque en la fase actual: el base y +8 por cada fase. */
    private float dano(float base) {
        return base + DANO_POR_FASE * (Mth.clamp(fase(), 1, 4) - 1);
    }

    @Override
    public void onSyncedDataUpdated(EntityDataAccessor<?> dato) {
        super.onSyncedDataUpdated(dato);
        if (!DATA_ESTADO.equals(dato) || !level().isClientSide()) {
            return;
        }
        arrancarAnimacion();
    }

    private AnimationState[] acciones() {
        return new AnimationState[]{dormido, despertar, rompeolas, remolino, burbujas, molino, arponLanzar,
                arponEspera, arponTirar, mirada, aturdido, tambaleo, agotado};
    }

    private @Nullable AnimationState animacionDe(int estado) {
        return switch (estado) {
            case DORMIDO -> dormido;
            case DESPERTAR -> despertar;
            case ROMPEOLAS -> rompeolas;
            case REMOLINO -> remolino;
            case BURBUJAS -> burbujas;
            case MOLINO -> molino;
            case ARPON_LANZAR -> arponLanzar;
            case ARPON_ESPERA -> arponEspera;
            case ARPON_TIRAR -> arponTirar;
            case MIRADA -> mirada;
            case ATURDIDO -> aturdido;
            case TAMBALEO -> tambaleo;
            case AGOTADO -> agotado;
            default -> null;
        };
    }

    /**
     * Una animacion de accion a la vez: si se mezclaran, el brazo que lanza el
     * gancho acabaria a medio camino del que clava el tridente.
     */
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
    //  Cliente: reposo, liberacion y las particulas que no gastan red
    // ------------------------------------------------------------------

    @Override
    public void tick() {
        super.tick();
        if (!level().isClientSide()) {
            return;
        }
        boolean muriendo = isDeadOrDying();
        // Si el estado llego sin aviso (al nacer dormido, que es el valor por
        // defecto, no se sincroniza ningun cambio), se arranca aqui.
        AnimationState actual = animacionDe(getEstado());
        if (!muriendo && actual != null && !actual.isStarted()) {
            arrancarAnimacion();
        }
        pesoLibreAnt = pesoLibre;
        float objetivoPeso = getEstado() == LIBRE && !muriendo ? 1.0F : 0.0F;
        pesoLibre = objetivoPeso > pesoLibre ? Math.min(objetivoPeso, pesoLibre + 0.2F) : Math.max(objetivoPeso, pesoLibre - 0.25F);
        if (muriendo && !liberacion.isStarted()) {
            for (AnimationState a : new AnimationState[]{dormido, despertar, rompeolas, remolino, burbujas, molino,
                    arponLanzar, arponEspera, arponTirar, mirada, aturdido, tambaleo, agotado}) {
                a.stop();
            }
            liberacion.start(tickCount);
        }
        if (muriendo) {
            return;
        }
        int e = getEstado();
        if (e == MIRADA && (tickCount - inicioEstado) * ritmoCliente >= NereaGeometria.MIRADA_FIJA - 8) {
            // Luz que el abismo le mete en los ojos: nace alrededor y va hacia ellos.
            for (Vec3 ojo : new Vec3[]{puntoMundo(NereaGeometria.OJO_IZQ_MIRADA), puntoMundo(NereaGeometria.OJO_DER_MIRADA)}) {
                double dx = (random.nextDouble() - 0.5) * 2.4;
                double dy = (random.nextDouble() - 0.5) * 2.4;
                double dz = (random.nextDouble() - 0.5) * 2.4;
                level().addParticle(AtalayaParticulas.NEREA_OJO, ojo.x + dx, ojo.y + dy, ojo.z + dz,
                        -dx * 0.12, -dy * 0.12, -dz * 0.12);
            }
        }
        // El corazon late a la vista; en la fase IV, desbocado.
        int cada = fase() >= 4 ? 14 : 30 - fase() * 3;
        if (e != DORMIDO && tickCount % cada == 0) {
            Vec3 c = puntoMundo(e == AGOTADO ? NereaGeometria.CORAZON_AGOTADO : NereaGeometria.CORAZON);
            level().addParticle(AtalayaParticulas.NEREA_CORAZON, c.x, c.y, c.z, 0, 0.02, 0);
        }
        // La maldicion se le escapa del cuerpo: nada en la fase I, a borbotones en la IV.
        int aura = new int[]{0, 0, 1, 2, 4}[Mth.clamp(fase(), 1, 4)];
        if (e != DORMIDO) {
            for (int i = 0; i < aura; i++) {
                if (random.nextInt(3) == 0) {
                    Vec3 a = puntoMundo(new Vec3((random.nextDouble() - 0.5) * 3.0, 1.0 + random.nextDouble() * 7.0,
                            (random.nextDouble() - 0.5) * 2.0));
                    level().addParticle(AtalayaParticulas.NEREA_CORAZON, a.x, a.y, a.z, 0, 0.03 + random.nextDouble() * 0.03, 0);
                }
            }
        }
        if (e == DORMIDO && tickCount % 9 == 0) {
            Vec3 b = puntoMundo(new Vec3(0, 4.3, 2.0));
            level().addParticle(AtalayaParticulas.NEREA_BURBUJA, b.x + random.nextGaussian() * 0.2, b.y,
                    b.z + random.nextGaussian() * 0.2, 0, 0.05, 0);
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
        if (getEstado() != DORMIDO && !isDeadOrDying()) {
            int nueva = faseSegunVida();
            if (nueva > fase()) {
                alCambiarFase(nivel, nueva);
            }
        }
        LivingEntity objetivo = getTarget();
        if (objetivo != null && (!objetivo.isAlive() || objetivo.distanceToSqr(Vec3.atCenterOf(centro)) > 64 * 64)) {
            setTarget(null);
            objetivo = null;
        }

        if (respiro > 0) respiro--;
        if (enfRompeolas > 0) enfRompeolas--;
        if (enfRemolino > 0) enfRemolino--;
        if (enfBurbujas > 0) enfBurbujas--;
        if (enfMolino > 0) enfMolino--;
        if (enfArpon > 0) enfArpon--;
        if (enfMirada > 0) enfMirada--;

        int e = getEstado();
        t++;
        switch (e) {
            case DORMIDO -> tickDormido(nivel);
            case DESPERTAR -> tickDespertar(nivel);
            case LIBRE -> tickLibre(nivel, objetivo);
            case ROMPEOLAS -> tickRompeolas(nivel, objetivo);
            case REMOLINO -> tickRemolino(nivel);
            case BURBUJAS -> tickBurbujas(nivel, objetivo);
            case MOLINO -> tickMolino(nivel);
            case ARPON_LANZAR -> tickArponLanzar(nivel);
            case ARPON_ESPERA -> tickArponEspera();
            case ARPON_TIRAR -> tickArponTirar(nivel);
            case MIRADA -> tickMirada(nivel);
            case ATURDIDO -> tickAturdido(nivel);
            case TAMBALEO -> tickTambaleo();
            case AGOTADO -> tickAgotado(nivel);
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
        if (e == MIRADA || e == ATURDIDO || e == ARPON_TIRAR || e == ARPON_ESPERA) {
            entityData.set(DATA_OBJETIVO, -1);
            entityData.set(DATA_OJOS, 0);
        }
        soltarGancho();
        presa = null;
        ponerEstado(LIBRE, 0);
        respiro = new int[]{0, 18, 14, 10, 6}[fase()];
    }

    private void tickLibre(ServerLevel nivel, @Nullable LivingEntity objetivo) {
        if (objetivo == null) {
            // Sin nadie a quien pelear vuelve al centro de su santuario.
            Vec3 c = Vec3.atBottomCenterOf(centro);
            if (horizontal(position(), c) > 3.0) {
                getMoveControl().setWantedPosition(c.x, c.y, c.z, 0.8);
            }
            return;
        }
        getLookControl().setLookAt(objetivo, 20.0F, 20.0F);
        if (fase() == 4 && --relojAgotado <= 0) {
            empezarAgotado();
            return;
        }
        if (respiro <= 0 && elegirAtaque(nivel, objetivo)) {
            return;
        }
        if (horizontal(position(), objetivo.position()) > 7.0) {
            // Hacia el objetivo, pero sin pasar de donde llegan las cadenas.
            Vec3 c = Vec3.atBottomCenterOf(centro);
            Vec3 destino = objetivo.position();
            Vec3 desde = new Vec3(destino.x - c.x, 0, destino.z - c.z);
            if (desde.length() > CORREA) {
                desde = desde.normalize().scale(CORREA);
            }
            Vec3 punto = new Vec3(c.x + desde.x, getY(), c.z + desde.z);
            if (horizontal(position(), punto) > 1.0) {
                getMoveControl().setWantedPosition(punto.x, punto.y, punto.z, fase() == 4 ? 1.3 : 1.0);
            }
        }
    }

    private boolean elegirAtaque(ServerLevel nivel, LivingEntity objetivo) {
        int fase = fase();
        double d = horizontal(position(), objetivo.position());
        List<int[]> opciones = new ArrayList<>();
        if (enfRompeolas <= 0 && d < 42) opciones.add(new int[]{ROMPEOLAS, 5});
        if (enfBurbujas <= 0) opciones.add(new int[]{BURBUJAS, 3});
        if (enfRemolino <= 0 && jugadores(nivel, RADIO_REMOLINO, 10.0).size() >= Math.max(1, jugadoresGrupo / 4)) opciones.add(new int[]{REMOLINO, 3});
        if (fase >= 2 && enfMolino <= 0 && !jugadoresEnAnillo(nivel).isEmpty()) opciones.add(new int[]{MOLINO, 6});
        LivingEntity lejano = fase >= 2 && enfArpon <= 0 ? presaArpon(nivel) : null;
        if (lejano != null) opciones.add(new int[]{ARPON_LANZAR, 3});
        LivingEntity mirado = fase >= 3 && enfMirada <= 0 ? presaMirada(nivel) : null;
        if (mirado != null) opciones.add(new int[]{MIRADA, 4});
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
        if (elegido == ROMPEOLAS) {
            // Con mucha gente no va siempre a por el mismo: elige entre los que tiene a tiro.
            List<Player> cerca = jugadores(nivel, 42, 0);
            if (!cerca.isEmpty()) {
                setTarget(cerca.get(random.nextInt(cerca.size())));
            }
        }
        iniciar(nivel, elegido, elegido == ARPON_LANZAR ? lejano : mirado);
        return true;
    }

    /** Arranca un ataque. "presa" solo la usan el Arpon y la Mirada. */
    private void iniciar(ServerLevel nivel, int ataque, @Nullable LivingEntity presaElegida) {
        // Cada fase todo vuelve antes: en la IV, con un 40 % menos de espera.
        float k = new float[]{1.0F, 1.0F, 0.85F, 0.72F, 0.6F}[Mth.clamp(fase(), 1, 4)];
        switch (ataque) {
            case ROMPEOLAS -> {
                enfRompeolas = (int) (60 * k);
                golpeados.clear();
                tickImpacto = -1;
                ponerEstado(ROMPEOLAS, NereaGeometria.DURACION_ROMPEOLAS);
                sonido(AtalayaSonidos.NEREA_ROMPEOLAS_ALZAR, 3.0F);
            }
            case BURBUJAS -> {
                enfBurbujas = (int) (150 * k);
                // Una por jugador; si solo hay uno, todas a por el.
                blancosBurbujas.clear();
                List<Player> todos = jugadores(nivel, 56, 0);
                if (todos.size() <= 1) {
                    LivingEntity unico = todos.isEmpty() ? getTarget() : todos.get(0);
                    for (int i = 0; i < 4 && unico != null; i++) {
                        blancosBurbujas.add(unico);
                    }
                } else {
                    blancosBurbujas.addAll(todos.subList(0, Math.min(40, todos.size())));
                }
                ponerEstado(BURBUJAS, NereaGeometria.DURACION_BURBUJAS);
                sonido(AtalayaSonidos.NEREA_BURBUJAS, 3.0F);
            }
            case REMOLINO -> {
                enfRemolino = (int) (340 * k);
                ponerEstado(REMOLINO, NereaGeometria.DURACION_REMOLINO);
                sonido(AtalayaSonidos.NEREA_REMOLINO_AVISO, 3.0F);
            }
            case MOLINO -> {
                enfMolino = (int) (220 * k);
                rumbo = yBodyRot;
                ultimoGolpe.clear();
                ponerEstado(MOLINO, NereaGeometria.DURACION_MOLINO);
            }
            case ARPON_LANZAR -> {
                if (presaElegida == null) {
                    return;
                }
                enfArpon = (int) (200 * k);
                presa = presaElegida;
                ponerEstado(ARPON_LANZAR, NereaGeometria.DURACION_ARPON_LANZAR);
                sonido(AtalayaSonidos.NEREA_ARPON_LANZAR, 3.0F);
            }
            case MIRADA -> {
                if (presaElegida == null) {
                    return;
                }
                enfMirada = (int) (480 * k);
                presa = presaElegida;
                golpesOjoIzq = 0;
                golpesOjoDer = 0;
                // Con mas gente disparando, los ojos aguantan mas impactos.
                golpesPorOjo = 3 + jugadoresGrupo / 6;
                entityData.set(DATA_OJOS, 0);
                entityData.set(DATA_OBJETIVO, presaElegida.getId());
                ponerEstado(MIRADA, NereaGeometria.DURACION_MIRADA);
                sonido(AtalayaSonidos.NEREA_RUGIDO, 6.0F);
                sonido(AtalayaSonidos.NEREA_MIRADA_CARGA, 3.0F);
            }
            default -> {
            }
        }
    }

    /**
     * Para probar y para el operador de la serie: fuerza un ataque o un momento
     * del combate sin esperar a que salga solo. Apunta al ser vivo mas cercano
     * que no sea el (un jugador, o un maniqui de pruebas); "lejano" lanza el
     * Arpon al mas lejano.
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
        if (orden.equals("lejano")) {
            double lejos = 0;
            for (LivingEntity v : nivel.getEntitiesOfClass(LivingEntity.class, getBoundingBox().inflate(44), this::esPresa)) {
                double d = v.distanceToSqr(this);
                if (d > lejos) {
                    lejos = d;
                    blanco = v;
                }
            }
            orden = "arpon";
        }
        switch (orden) {
            case "despertar" -> {
                despertarse(blanco);
                return true;
            }
            case "fase" -> {
                // Le baja la vida justo por debajo del siguiente umbral.
                int siguiente = Math.min(4, fase() + 1);
                if (getEstado() == DORMIDO) {
                    despertarse(blanco);
                }
                setHealth(getMaxHealth() * (1.0F - 0.25F * (siguiente - 1)) - 1.0F);
                return true;
            }
            case "liberar" -> {
                // Como si le vaciaran el corazon: pasa por la liberacion entera.
                hurtServer(nivel, nivel.damageSources().genericKill(), Float.MAX_VALUE);
                return true;
            }
            default -> {
            }
        }
        int ataque = switch (orden) {
            case "rompeolas" -> ROMPEOLAS;
            case "remolino" -> REMOLINO;
            case "burbujas" -> BURBUJAS;
            case "molino" -> MOLINO;
            case "arpon" -> ARPON_LANZAR;
            case "mirada" -> MIRADA;
            case "agotado" -> AGOTADO;
            case "aturdido" -> ATURDIDO;
            default -> -1;
        };
        if (ataque < 0) {
            return false;
        }
        if (blanco != null) {
            setTarget(blanco);
            girarHacia(blanco.position(), 180.0F);
        }
        cortarSonido(nivel, AtalayaSonidos.NEREA_MIRADA_RAYO);
        soltarGancho();
        entityData.set(DATA_OBJETIVO, -1);
        entityData.set(DATA_OJOS, 0);
        // Pasa por LIBRE para que el cliente vea el cambio aunque repita ataque.
        ponerEstado(LIBRE, 0);
        if (ataque == AGOTADO) {
            empezarAgotado();
        } else if (ataque == ATURDIDO) {
            entityData.set(DATA_OJOS, 3);
            ponerEstado(ATURDIDO, NereaGeometria.DURACION_ATURDIDO);
            sonido(AtalayaSonidos.NEREA_ATURDIDO, 3.0F);
        } else {
            iniciar(nivel, ataque, blanco);
        }
        return true;
    }

    // ------------------------------------------------------------------
    //  Dormido y despertar
    // ------------------------------------------------------------------

    /** Lo que alcanza a sentir dormido: un jugador a esta distancia y a la vista. */
    private static final double RANGO_DESPERTAR = 40.0;

    private void tickDormido(ServerLevel nivel) {
        // Quieto del todo: ni anda ni se gira hasta que despierta.
        getNavigation().stop();
        setDeltaMovement(getDeltaMovement().multiply(0, 1, 0));
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
        ponerEstado(DESPERTAR, NereaGeometria.DURACION_DESPERTAR);
        sonido(AtalayaSonidos.NEREA_DESPERTAR, 7.0F);
    }

    private void tickDespertar(ServerLevel nivel) {
        if (t == 42) {
            // El rugido empuja: aparta a quien se acerco a despertarlo.
            for (Player p : jugadores(nivel, 13, 0)) {
                Vec3 fuera = horizontalHacia(position(), p.position());
                p.setDeltaMovement(fuera.x * 1.2, 0.5, fuera.z * 1.2);
                p.hurtMarked = true;
            }
            golpeSuelo(nivel, position(), 2.4F, 13.0F, 16, 0);
            anillo(nivel, AtalayaParticulas.NEREA_ESPUMA, 4.0, 36, 0.45);
        }
        if (t == 1) {
            // La pelea empieza de verdad: cuenta al grupo (ganchos, golpes por
            // ojo) y llena la vida.
            jugadoresGrupo = Math.max(1, jugadores(nivel, 80, 0).size());
            factorGrupo = VIDA_VANILLA / VIDA;
            setHealth(getMaxHealth());
            entityData.set(DATA_FASE, 1);
        }
    }

    // ------------------------------------------------------------------
    //  Rompeolas: el tridente cae y sale una ola en linea recta
    // ------------------------------------------------------------------

    private void tickRompeolas(ServerLevel nivel, @Nullable LivingEntity objetivo) {
        int impacto = NereaGeometria.IMPACTO_ROMPEOLAS;
        if (ta() < impacto - 2 && objetivo != null) {
            girarHacia(objetivo.position(), 14.0F);
        } else {
            fijarRumbo(yBodyRot);
        }
        double punta = NereaGeometria.PUNTA_ROMPEOLAS.z;
        if (cruza(impacto)) {
            tickImpacto = t;
            Vec3 p = puntoMundo(NereaGeometria.PUNTA_ROMPEOLAS);
            nivel.playSound(null, p.x, p.y, p.z, AtalayaSonidos.NEREA_ROMPEOLAS_GOLPE, SoundSource.HOSTILE, 5.0F, 1.0F);
            nivel.playSound(null, p.x, p.y, p.z, AtalayaSonidos.NEREA_OLA, SoundSource.HOSTILE, 4.0F, 1.0F);
            golpeSuelo(nivel, p, 3.6F, 11.0F, 44, 36);
            // Olas en abanico desde la punta: una en la fase I, tres en la II y
            // cinco desde la III.
            int olas = new int[]{1, 1, 3, 5, 5}[Mth.clamp(fase(), 1, 4)];
            olaOrigenes = new Vec3[olas];
            olaDirs = new Vec3[olas];
            for (int w = 0; w < olas; w++) {
                float abre = (w - (olas - 1) / 2.0F) * ABANICO_OLAS;
                olaOrigenes[w] = p;
                olaDirs[w] = enRumbo(yBodyRot + abre, 1).subtract(position());
            }
            // El asta al caer: lo que estaba debajo, de sus pies a la punta.
            golpearLinea(nivel, position(), olaDirs[0], 3.0, punta + 1.0, 1.4);
        }
        if (tickImpacto >= 0 && t > tickImpacto && t <= tickImpacto + TICKS_OLA) {
            double paso = LARGO_OLA / TICKS_OLA;
            double d0 = (t - tickImpacto - 1) * paso;
            for (int w = 0; w < olaDirs.length; w++) {
                Vec3 o = olaOrigenes[w];
                Vec3 dir = olaDirs[w];
                golpearLinea(nivel, o, dir, d0, d0 + paso, 2.6);
                Vec3 lado = new Vec3(-dir.z, 0, dir.x);
                for (int k = 0; k < 8; k++) {
                    double a = d0 + random.nextDouble() * paso;
                    double l = (k - 3.5) * 0.75;
                    Vec3 q = o.add(dir.scale(a)).add(lado.scale(l));
                    nivel.sendParticles(AtalayaParticulas.NEREA_OLA, q.x, getY() + 0.5, q.z, 0, dir.x, 0.0, dir.z, 0.3);
                    nivel.sendParticles(AtalayaParticulas.NEREA_ESPUMA, q.x, getY() + 0.3, q.z, 1, 0.2, 0.1, 0.2, 0.02);
                }
                Vec3 q = o.add(dir.scale(d0 + paso));
                nivel.sendParticles(AtalayaParticulas.NEREA_GOTA, q.x, getY() + 0.8, q.z, 5, 1.2, 0.3, 1.2, 0.3);
            }
        }
    }

    private void golpearLinea(ServerLevel nivel, Vec3 origen, Vec3 dir, double desde, double hasta, double ancho) {
        Vec3 lado = new Vec3(-dir.z, 0, dir.x);
        AABB caja = new AABB(origen, origen.add(dir.scale(hasta))).inflate(ancho + 1, 3, ancho + 1);
        for (LivingEntity v : nivel.getEntitiesOfClass(LivingEntity.class, caja, this::esPresa)) {
            if (golpeados.contains(v.getUUID())) {
                continue;
            }
            Vec3 rel = v.position().subtract(origen);
            double a = rel.x * dir.x + rel.z * dir.z;
            double l = Math.abs(rel.x * lado.x + rel.z * lado.z);
            double dy = v.getY() - getY();
            if (a < desde || a > hasta || l > ancho + v.getBbWidth() / 2 || dy < -1.5 || dy > 3.0) {
                continue;
            }
            golpeados.add(v.getUUID());
            if (v.hurtServer(nivel, NereaDanos.fuente(nivel, NereaDanos.OLA, this, this), dano(DANO_ROMPEOLAS))) {
                // Te tumba: la ola te levanta y te lleva.
                v.setDeltaMovement(dir.x * 0.9, 0.55, dir.z * 0.9);
                v.hurtMarked = true;
            }
        }
    }

    // ------------------------------------------------------------------
    //  Remolino: arrastra a todos hacia el. Solo la antorcha lo para.
    // ------------------------------------------------------------------

    private void tickRemolino(ServerLevel nivel) {
        // Arrastra a todo lo vivo en su radio, no solo a los jugadores.
        List<LivingEntity> presas = new ArrayList<>();
        for (LivingEntity v : nivel.getEntitiesOfClass(LivingEntity.class, getBoundingBox().inflate(RADIO_REMOLINO), this::esPresa)) {
            if (horizontal(position(), v.position()) <= RADIO_REMOLINO) {
                presas.add(v);
            }
        }
        if (t < NereaGeometria.REMOLINO_TIRA) {
            // El aviso: burbujas que suben bajo los pies de cada uno.
            for (LivingEntity p : presas) {
                nivel.sendParticles(AtalayaParticulas.NEREA_BURBUJA, p.getX(), p.getY() + 0.1, p.getZ(),
                        3, 0.35, 0.05, 0.35, 0.03);
            }
            return;
        }
        if (t == NereaGeometria.REMOLINO_TIRA) {
            sonido(AtalayaSonidos.NEREA_REMOLINO, 4.0F);
        }
        if (t >= NereaGeometria.REMOLINO_SUELTA) {
            return;
        }
        for (LivingEntity p : presas) {
            if (p instanceof Player jugador && llevaAntorcha(jugador)) {
                if (t == NereaGeometria.REMOLINO_TIRA) {
                    nivel.playSound(null, p.getX(), p.getY(), p.getZ(), AtalayaSonidos.NEREA_ANTORCHA,
                            SoundSource.PLAYERS, 1.2F, 1.0F);
                }
                if (t % 3 == 0) {
                    nivel.sendParticles(AtalayaParticulas.NEREA_LUZ, p.getX(), p.getY() + 1.0, p.getZ(),
                            2, 0.5, 0.6, 0.5, 0.01);
                }
                continue;
            }
            if (t % 10 == 0) {
                // La corriente sigue tirando de las piernas 4 s despues de soltarte.
                corriente(p, NereaGeometria.REMOLINO_SUELTA - t + 80, fase() >= 3 ? 1 : 0);
            }
            if ((t - NereaGeometria.REMOLINO_TIRA) % 20 == 0) {
                // Y ahoga: 10 por segundo mientras te arrastra.
                p.hurtServer(nivel, NereaDanos.fuente(nivel, NereaDanos.REMOLINO, this, this), DANO_REMOLINO);
            }
            Vec3 hacia = new Vec3(getX() - p.getX(), 0, getZ() - p.getZ());
            double d = hacia.length();
            if (d < 3.5) {
                continue;
            }
            Vec3 dir = hacia.scale(1.0 / d);
            Vec3 giro = new Vec3(-dir.z, 0, dir.x);
            Vec3 v = p.getDeltaMovement();
            // Desde lejos tira mas: que nadie en todo el radio se libre.
            float fuerza = new float[]{0.3F, 0.3F, 0.34F, 0.39F, 0.45F}[Mth.clamp(fase(), 1, 4)]
                    * (float) (1.0 + d / 48.0);
            p.setDeltaMovement(v.x * 0.5 + dir.x * fuerza + giro.x * 0.1, v.y, v.z * 0.5 + dir.z * fuerza + giro.z * 0.1);
            p.hurtMarked = true;
            // Su propio remolino: agua que sube en espiral alrededor de el.
            for (int k = 0; k < 3; k++) {
                double a = (tickCount * 0.55) + k * (Math.PI * 2 / 3);
                double h = ((tickCount + k * 7) % 20) / 20.0 * 2.4;
                double r = 1.5 - h * 0.25;
                nivel.sendParticles(k == 0 ? AtalayaParticulas.NEREA_ESPUMA : AtalayaParticulas.NEREA_GOTA,
                        p.getX() + Math.cos(a) * r, p.getY() + h, p.getZ() + Math.sin(a) * r, 0,
                        -Math.sin(a) * 0.35, 0.08, Math.cos(a) * 0.35, 1.0);
            }
            if (t % 3 == 0) {
                nivel.sendParticles(AtalayaParticulas.NEREA_REMOLINO, p.getX(), p.getY() + 0.15, p.getZ(),
                        1, 0.0, 0.0, 0.0, 0.0);
            }
        }
        // El gran remolino (brazos de agua en todo el radio) lo dibuja cada
        // cliente cerca de si: NereaEfectosCliente.remolinoGigante.
    }

    /** La Corriente Abismal (lentitud propia de Nerea), sin rebajar una que ya sea mas fuerte o mas larga. */
    private void corriente(LivingEntity v, int ticks, int nivelEfecto) {
        v.addEffect(new MobEffectInstance(CorrienteAbismalEffect.CORRIENTE, ticks, nivelEfecto, false, true, true), this);
    }

    /** La luz rompe la corriente de la maldicion: una antorcha en cualquier mano. */
    private static boolean llevaAntorcha(Player p) {
        return p.isHolding(Items.TORCH) || p.isHolding(Items.SOUL_TORCH) || p.isHolding(Items.COPPER_TORCH);
    }

    // ------------------------------------------------------------------
    //  Burbujas bomba: las bombea el corazon
    // ------------------------------------------------------------------

    private void tickBurbujas(ServerLevel nivel, @Nullable LivingEntity objetivo) {
        if (objetivo != null) {
            girarHacia(objetivo.position(), 5.0F);
        }
        int suelta = NereaGeometria.BURBUJAS_SUELTA;
        if (ta() >= suelta && !blancosBurbujas.isEmpty()) {
            // Salen en rafaga: hasta seis por tick, cada una a por su jugador.
            Vec3 c = puntoMundo(NereaGeometria.CORAZON_BURBUJAS);
            int n = Math.min(6, blancosBurbujas.size());
            for (int i = 0; i < n; i++) {
                LivingEntity blanco = blancosBurbujas.remove(blancosBurbujas.size() - 1);
                Vec3 hacia = horizontalHacia(position(), blanco.position());
                BurbujaNereaEntity.lanzar(nivel, this, c.add(random.nextGaussian() * 0.5, random.nextGaussian() * 0.4,
                        random.nextGaussian() * 0.5), frente().add(hacia).normalize(), blanco, fase());
            }
            nivel.sendParticles(AtalayaParticulas.NEREA_CORAZON, c.x, c.y, c.z, 3, 0.3, 0.3, 0.3, 0.02);
        }
    }

    // ------------------------------------------------------------------
    //  Molino: dos vueltas de cadena a ras de suelo
    // ------------------------------------------------------------------

    private void tickMolino(ServerLevel nivel) {
        fijarRumbo(rumbo);
        if (cruza(NereaGeometria.MOLINO_VISIBLE)) {
            sonido(AtalayaSonidos.NEREA_MOLINO_ARRASTRE, 3.0F);
        }
        if (ta() < NereaGeometria.MOLINO_VISIBLE) {
            return;
        }
        float giro = NereaGeometria.giroMolino(ta());
        // Chispas en las dos cadenas, donde rozan el suelo.
        for (float brazo : new float[]{-90.0F, 90.0F}) {
            for (double r : new double[]{5.0, 9.0, 13.0, 17.0, RADIO_MOLINO - 0.5}) {
                Vec3 p = enRumbo(rumbo + giro + brazo, r);
                nivel.sendParticles(AtalayaParticulas.NEREA_CHISPA, p.x, getY() + 0.2, p.z, 1, 0.15, 0.05, 0.15, 0.12);
            }
            if (ta() >= NereaGeometria.MOLINO_GOLPEA) {
                Vec3 p = enRumbo(rumbo + giro + brazo, RADIO_MOLINO - 1.0);
                nivel.sendParticles(AtalayaParticulas.NEREA_POLVO, p.x, getY() + 0.2, p.z, 3, 0.4, 0.05, 0.4, 0.02);
                if (random.nextInt(3) == 0) {
                    nivel.sendParticles(AtalayaParticulas.NEREA_ROCA, p.x, getY() + 0.3, p.z, 0,
                            (random.nextDouble() - 0.5) * 0.4, 0.35 + random.nextDouble() * 0.2, (random.nextDouble() - 0.5) * 0.4, 1.0);
                }
            }
        }
        if (ta() < NereaGeometria.MOLINO_GOLPEA || ta() > NereaGeometria.MOLINO_PARA) {
            return;
        }
        if (t % 8 == 0) {
            sonido(AtalayaSonidos.NEREA_MOLINO_GIRO, 3.0F);
        }
        float antes = rumbo + NereaGeometria.giroMolino((t - 1) * ritmoEstado);
        float ahora = rumbo + giro;
        AABB caja = getBoundingBox().inflate(RADIO_MOLINO + 1, 0, RADIO_MOLINO + 1).expandTowards(0, 1, 0);
        for (LivingEntity v : nivel.getEntitiesOfClass(LivingEntity.class, caja, this::esPresa)) {
            double r = horizontal(position(), v.position());
            double dy = v.getY() - getY();
            // Pegado a sus pies no llega; y por encima de un bloque, la has saltado.
            if (r < MOLINO_PIES || r > RADIO_MOLINO + v.getBbWidth() / 2 || dy > 0.9 || dy < -2.0) {
                continue;
            }
            float c = rumboHacia(v.position());
            boolean tocado = false;
            for (float brazo : new float[]{-90.0F, 90.0F}) {
                tocado |= barre(antes + brazo, ahora + brazo, c);
            }
            Integer ultimo = ultimoGolpe.get(v.getUUID());
            if (!tocado || (ultimo != null && tickCount - ultimo < 8)) {
                continue;
            }
            ultimoGolpe.put(v.getUUID(), tickCount);
            if (v.hurtServer(nivel, NereaDanos.fuente(nivel, NereaDanos.CADENA, this, this), dano(DANO_MOLINO))) {
                Vec3 fuera = horizontalHacia(position(), v.position());
                v.setDeltaMovement(fuera.x * (0.9 + 0.15 * fase()), 0.3 + 0.05 * fase(), fuera.z * (0.9 + 0.15 * fase()));
                v.hurtMarked = true;
            }
        }
    }

    /** Si el rumbo c quedo entre "antes" y "ahora" (en el sentido del giro). */
    private static boolean barre(float antes, float ahora, float c) {
        float tramo = ahora - antes;
        float d = Mth.wrapDegrees(c - antes);
        if (tramo >= 0) {
            return d >= 0 && d <= tramo;
        }
        return d <= 0 && d >= tramo;
    }

    // ------------------------------------------------------------------
    //  Arpon: lanza ganchos a los mas lejanos, los arrastra a sus pies y
    //  los clava con el tridente
    // ------------------------------------------------------------------

    private void tickArponLanzar(ServerLevel nivel) {
        if (presa == null || !presa.isAlive()) {
            terminar(nivel);
            return;
        }
        girarHacia(presa.position(), 14.0F);
        if (cruza(NereaGeometria.ARPON_SUELTA)) {
            // Un gancho por cada diez jugadores (hasta cuatro), y uno mas desde la
            // fase III: a los mas lejanos.
            Vec3 mano = puntoMundo(NereaGeometria.MANO_IZQ_LANZAR);
            int n = Mth.clamp(jugadoresGrupo / 10, 1, 4) + (fase() >= 3 ? 1 : 0);
            List<Player> lejanos = new ArrayList<>(jugadores(nivel, 46, 6));
            lejanos.removeIf(p -> !hasLineOfSight(p));
            lejanos.sort((a, b) -> Double.compare(b.distanceToSqr(this), a.distanceToSqr(this)));
            List<LivingEntity> blancos = new ArrayList<>(lejanos.subList(0, Math.min(n, lejanos.size())));
            if (blancos.isEmpty()) {
                blancos.add(presa);
            }
            ganchos.clear();
            enganchados.clear();
            for (LivingEntity b : blancos) {
                ganchos.add(GanchoNereaEntity.lanzar(nivel, this, mano, b.getEyePosition().add(0, -0.4, 0)));
            }
            ponerEstado(ARPON_ESPERA, ESPERA_GANCHO);
        }
    }

    private void tickArponEspera() {
        if (presa != null && presa.isAlive()) {
            girarHacia(presa.position(), 4.0F);
        }
        ganchos.removeIf(Entity::isRemoved);
        if (ganchos.isEmpty()) {
            t = duracion;
        }
    }

    /** Un gancho ha dado en alguien. Devuelve si se engancha (o si el escudo lo para). */
    public boolean alEngancharGancho(ServerLevel nivel, GanchoNereaEntity g, LivingEntity victima) {
        boolean tirando = getEstado() == ARPON_TIRAR && ta() < NereaGeometria.ARPON_ARRASTRE;
        if ((getEstado() != ARPON_ESPERA && !tirando) || !ganchos.contains(g)) {
            return false;
        }
        boolean entra = victima.hurtServer(nivel, NereaDanos.fuente(nivel, NereaDanos.TRIDENTE, g, this), dano(DANO_GANCHO));
        if (!entra) {
            // Escudo: el gancho rebota.
            nivel.playSound(null, g.getX(), g.getY(), g.getZ(), AtalayaSonidos.NEREA_ARPON_REBOTA, SoundSource.HOSTILE, 2.0F, 1.0F);
            nivel.sendParticles(AtalayaParticulas.NEREA_CHISPA, g.getX(), g.getY(), g.getZ(), 10, 0.2, 0.2, 0.2, 0.25);
            ganchos.remove(g);
            return false;
        }
        enganchados.add(victima);
        // Te arrastra y te deja la Corriente Abismal: no te alejas a tiempo de la estocada.
        corriente(victima, 120, fase() >= 4 ? 2 : 1);
        nivel.playSound(null, victima.getX(), victima.getY(), victima.getZ(), AtalayaSonidos.NEREA_ARPON_ENGANCHA,
                SoundSource.HOSTILE, 2.5F, 1.0F);
        if (getEstado() == ARPON_ESPERA) {
            presa = victima;
            entityData.set(DATA_OBJETIVO, victima.getId());
            ponerEstado(ARPON_TIRAR, NereaGeometria.DURACION_ARPON_TIRAR);
        }
        return true;
    }

    /** Un gancho no ha dado en nada. */
    public void alFallarGancho(GanchoNereaEntity g) {
        ganchos.remove(g);
    }

    private void tickArponTirar(ServerLevel nivel) {
        if (presa != null && presa.isAlive() && ta() < NereaGeometria.ARPON_ARRASTRE) {
            girarHacia(presa.position(), 6.0F);
        } else {
            fijarRumbo(yBodyRot);
        }
        if (ta() < NereaGeometria.ARPON_ARRASTRE) {
            // A sus pies, cada uno a un lado para que no se amontonen.
            Vec3 punta = puntoMundo(new Vec3(NereaGeometria.PUNTA_ESTOCADA.x, 0, NereaGeometria.PUNTA_ESTOCADA.z));
            for (int i = 0; i < enganchados.size(); i++) {
                LivingEntity v = enganchados.get(i);
                if (!v.isAlive()) {
                    continue;
                }
                double a = yBodyRot * Mth.DEG_TO_RAD + (i - (enganchados.size() - 1) / 2.0) * 0.5;
                Vec3 destino = punta.add(Math.cos(a) * 0.9 * (i == 0 ? 0 : 1), 0, Math.sin(a) * 0.9 * (i == 0 ? 0 : 1));
                Vec3 dif = new Vec3(destino.x - v.getX(), 0, destino.z - v.getZ());
                double d = dif.length();
                if (d > 0.6) {
                    Vec3 vel = dif.normalize().scale(Math.min(2.2, d * 0.45));
                    v.setDeltaMovement(vel.x, v.onGround() ? 0.15 : v.getDeltaMovement().y, vel.z);
                    v.hurtMarked = true;
                    nivel.sendParticles(AtalayaParticulas.NEREA_ESPUMA, v.getX(), v.getY() + 0.1, v.getZ(),
                            2, 0.3, 0.05, 0.3, 0.01);
                }
            }
        }
        if (cruza(NereaGeometria.ARPON_ARRASTRE)) {
            soltarGancho();
        }
        if (cruza(NereaGeometria.ARPON_ESTOCADA)) {
            Vec3 p = puntoMundo(NereaGeometria.PUNTA_ESTOCADA);
            nivel.playSound(null, p.x, p.y, p.z, AtalayaSonidos.NEREA_ESTOCADA, SoundSource.HOSTILE, 4.0F, 1.0F);
            golpeSuelo(nivel, p, 2.8F, 6.5F, 24, 20);
            AABB zona = new AABB(p, p).inflate(5.0, 0, 5.0).expandTowards(0, 3, 0).expandTowards(0, -1, 0);
            for (LivingEntity v : nivel.getEntitiesOfClass(LivingEntity.class, zona, this::esPresa)) {
                v.hurtServer(nivel, NereaDanos.fuente(nivel, NereaDanos.TRIDENTE, this, this), dano(DANO_ESTOCADA));
            }
            enganchados.clear();
        }
    }

    private void soltarGancho() {
        for (GanchoNereaEntity g : ganchos) {
            g.discard();
        }
        ganchos.clear();
    }

    // ------------------------------------------------------------------
    //  Mirada del Abismo
    // ------------------------------------------------------------------

    private void tickMirada(ServerLevel nivel) {
        if (presa == null || !presa.isAlive() || presa.isRemoved()) {
            cortarSonido(nivel, AtalayaSonidos.NEREA_MIRADA_RAYO);
            terminar(nivel);
            return;
        }
        girarHacia(presa.position(), ta() < NereaGeometria.MIRADA_FIJA ? 10.0F : 2.5F + fase() * 0.6F);
        if (cruza(NereaGeometria.MIRADA_FIJA)) {
            sonido(AtalayaSonidos.NEREA_MIRADA_RAYO, 4.0F);
        }
        if (t == duracion - 2) {
            Vec3 ojos = puntoMundo(NereaGeometria.OJO_IZQ_MIRADA).add(puntoMundo(NereaGeometria.OJO_DER_MIRADA)).scale(0.5);
            Vec3 fin = presa.getEyePosition().add(0, -0.3, 0);
            BlockHitResult choque = nivel.clip(new ClipContext(ojos, fin, ClipContext.Block.COLLIDER, ClipContext.Fluid.NONE, this));
            if (choque.getType() == HitResult.Type.MISS) {
                presa.hurtServer(nivel, NereaDanos.fuente(nivel, NereaDanos.MIRADA, this, this), dano(DANO_MIRADA));
                nivel.playSound(null, fin.x, fin.y, fin.z, AtalayaSonidos.NEREA_MIRADA_IMPACTO, SoundSource.HOSTILE, 3.0F, 1.0F);
                nivel.sendParticles(AtalayaParticulas.NEREA_OJO, fin.x, fin.y, fin.z, 24, 0.4, 0.5, 0.4, 0.3);
            } else {
                // Escondido tras un bloque: el rayo revienta contra el.
                Vec3 p = choque.getLocation();
                nivel.playSound(null, p.x, p.y, p.z, AtalayaSonidos.NEREA_MIRADA_IMPACTO, SoundSource.HOSTILE, 3.0F, 1.0F);
                nivel.sendParticles(AtalayaParticulas.NEREA_OJO, p.x, p.y, p.z, 20, 0.3, 0.3, 0.3, 0.3);
            }
        }
    }

    /** Una flecha (o lo que sea que vuela) que pasa por un ojo encendido. */
    private boolean impactoEnOjo(ServerLevel nivel, Projectile proyectil) {
        Vec3 p = proyectil.position();
        Vec3 v = proyectil.getDeltaMovement();
        Vec3 dir = v.lengthSqr() > 1.0E-4 ? v.normalize() : null;
        int ojos = getOjosRotos();
        int mejor = -1;
        double mejorD = 1.0;
        Vec3[] pos = {puntoMundo(NereaGeometria.OJO_IZQ_MIRADA), puntoMundo(NereaGeometria.OJO_DER_MIRADA)};
        for (int i = 0; i < 2; i++) {
            if ((ojos & (1 << i)) != 0) {
                continue;
            }
            Vec3 rel = pos[i].subtract(p);
            double d;
            if (dir == null) {
                d = rel.length();
            } else {
                double s = rel.dot(dir);
                if (s < -4 || s > 4) {
                    continue;
                }
                d = rel.subtract(dir.scale(s)).length();
            }
            if (d < mejorD) {
                mejorD = d;
                mejor = i;
            }
        }
        if (mejor < 0) {
            return false;
        }
        Vec3 ojo = pos[mejor];
        int golpes = mejor == 0 ? ++golpesOjoIzq : ++golpesOjoDer;
        nivel.sendParticles(AtalayaParticulas.NEREA_SELLO, ojo.x, ojo.y, ojo.z, 6, 0.1, 0.1, 0.1, 0.15);
        nivel.playSound(null, ojo.x, ojo.y, ojo.z, AtalayaSonidos.NEREA_SELLO_GOLPE, SoundSource.HOSTILE, 2.0F,
                1.0F + 0.6F * golpes / golpesPorOjo);
        if (golpes >= golpesPorOjo) {
            int rotos = ojos | (1 << mejor);
            entityData.set(DATA_OJOS, rotos);
            nivel.playSound(null, ojo.x, ojo.y, ojo.z, AtalayaSonidos.NEREA_OJO_ROTO, SoundSource.HOSTILE, 3.0F, 1.0F);
            nivel.sendParticles(AtalayaParticulas.NEREA_OJO, ojo.x, ojo.y, ojo.z, 18, 0.2, 0.2, 0.2, 0.25);
            if (rotos == 3) {
                // Los dos apagados: la mirada se rompe y se queda aturdido.
                cortarSonido(nivel, AtalayaSonidos.NEREA_MIRADA_RAYO);
                presa = null;
                ponerEstado(ATURDIDO, NereaGeometria.DURACION_ATURDIDO);
                sonido(AtalayaSonidos.NEREA_ATURDIDO, 3.0F);
            }
        }
        return true;
    }

    private void tickAturdido(ServerLevel nivel) {
        if (t % 8 == 0) {
            Vec3 c = puntoMundo(new Vec3(0, 7.2, 1.8));
            nivel.sendParticles(AtalayaParticulas.NEREA_SELLO, c.x, c.y, c.z, 2, 0.6, 0.2, 0.6, 0.02);
        }
    }

    private void tickTambaleo() {
        fijarRumbo(yBodyRot);
        if (t == 56) {
            sonido(AtalayaSonidos.NEREA_RUGIDO, 6.0F);
        }
    }

    private void empezarAgotado() {
        relojAgotado = CADA_AGOTADO;
        ponerEstado(AGOTADO, NereaGeometria.DURACION_AGOTADO);
        sonido(AtalayaSonidos.NEREA_AGOTADO, 3.0F);
    }

    private void tickAgotado(ServerLevel nivel) {
        fijarRumbo(yBodyRot);
        if (t == 12) {
            golpeSuelo(nivel, position(), 2.0F, 6.5F, 14, 0);
        }
        if (t % 16 == 0) {
            sonido(AtalayaSonidos.NEREA_LATIDO, 2.5F);
            Vec3 c = puntoMundo(NereaGeometria.CORAZON_AGOTADO);
            nivel.sendParticles(AtalayaParticulas.NEREA_CORAZON, c.x, c.y, c.z, 4, 0.3, 0.3, 0.3, 0.02);
        }
    }

    // ------------------------------------------------------------------
    //  Fases: las cadenas del pecho y el corazon
    // ------------------------------------------------------------------

    /**
     * Pasa de fase: le salta una cadena del pecho y el corazon se raja mas. Se
     * le corta lo que estuviera haciendo y se tambalea.
     */
    private void alCambiarFase(ServerLevel nivel, int nueva) {
        entityData.set(DATA_FASE, nueva);
        Vec3 pecho = puntoMundo(NereaGeometria.PECHO);
        nivel.playSound(null, pecho.x, pecho.y, pecho.z, AtalayaSonidos.NEREA_CADENA_ROMPE, SoundSource.HOSTILE, 5.0F, 1.0F);
        nivel.playSound(null, pecho.x, pecho.y, pecho.z, AtalayaSonidos.NEREA_SELLO_ROTO, SoundSource.HOSTILE, 4.0F, 0.8F);
        nivel.sendParticles(AtalayaParticulas.NEREA_CHISPA, pecho.x, pecho.y, pecho.z, 30, 0.9, 0.9, 0.9, 0.35);
        nivel.sendParticles(AtalayaParticulas.NEREA_CORAZON, pecho.x, pecho.y, pecho.z, 14, 0.5, 0.5, 0.5, 0.15);
        nivel.sendParticles(AtalayaParticulas.NEREA_ONDA, getX(), getY() + 0.12, getZ(), 0, 2.6, 13.0, 0.0, 1.0);
        int e = getEstado();
        if (e == DORMIDO || e == DESPERTAR) {
            return;
        }
        cortarSonido(nivel, AtalayaSonidos.NEREA_MIRADA_RAYO);
        soltarGancho();
        presa = null;
        entityData.set(DATA_OBJETIVO, -1);
        entityData.set(DATA_OJOS, 0);
        if (e != TAMBALEO) {
            ponerEstado(TAMBALEO, NereaGeometria.DURACION_TAMBALEO);
            sonido(AtalayaSonidos.NEREA_TAMBALEO, 6.0F);
        }
        if (nueva == 4) {
            relojAgotado = 300;
        }
    }

    @Override
    public void remove(RemovalReason motivo) {
        super.remove(motivo);
        soltarGancho();
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
                || fuente.is(DamageTypes.CRAMMING)) {
            return false;
        }
        Entity causante = fuente.getEntity();
        if (causante instanceof NereaEntity || fuente.getDirectEntity() instanceof BurbujaNereaEntity) {
            return false;
        }
        int e = getEstado();
        if (e == DORMIDO) {
            despertarse(causante);
            avisoInmune(nivel, causante);
            return false;
        }
        if (e == MIRADA && ta() >= NereaGeometria.MIRADA_FIJA - 6 && fuente.getDirectEntity() instanceof Projectile proyectil
                && impactoEnOjo(nivel, proyectil)) {
            return true;
        }
        if (e == DESPERTAR) {
            avisoInmune(nivel, causante);
            return false;
        }
        if (causante instanceof LivingEntity vivo && random.nextInt(4) == 0) {
            setTarget(vivo);
        }
        // La vida efectiva del grupo; agotado o aturdido, el doble.
        float k = factorGrupo * ((e == AGOTADO || e == ATURDIDO) ? 2.0F : 1.0F);
        boolean entra = super.hurtServer(nivel, fuente, cantidad * k);
        if (entra) {
            Vec3 c = puntoMundo(e == AGOTADO ? NereaGeometria.CORAZON_AGOTADO : NereaGeometria.CORAZON);
            nivel.sendParticles(AtalayaParticulas.NEREA_CORAZON, c.x, c.y, c.z, 6, 0.4, 0.4, 0.4, 0.05);
        }
        return entra;
    }

    /** Clang de cadena y chispas: se tiene que entender que no le hace nada. */
    private void avisoInmune(ServerLevel nivel, @Nullable Entity causante) {
        if (tickCount - ultimoAvisoInmune < 5) {
            return;
        }
        ultimoAvisoInmune = tickCount;
        Vec3 p = puntoMundo(NereaGeometria.PECHO);
        if (causante != null) {
            Vec3 fuera = horizontalHacia(position(), causante.position());
            double y = Mth.clamp(causante.getEyeY(), getY() + 0.5, getY() + 8.0);
            p = new Vec3(getX() + fuera.x * 1.6, y, getZ() + fuera.z * 1.6);
        }
        nivel.playSound(null, p.x, p.y, p.z, AtalayaSonidos.NEREA_INMUNE, SoundSource.HOSTILE, 1.5F,
                0.9F + random.nextFloat() * 0.2F);
        nivel.sendParticles(AtalayaParticulas.NEREA_SELLO, p.x, p.y, p.z, 5, 0.2, 0.2, 0.2, 0.12);
    }

    // ------------------------------------------------------------------
    //  La liberacion: su "muerte". No muere: se arrodilla, se le apagan
    //  las cadenas, los ojos pasan a oro y se deshace en agua.
    // ------------------------------------------------------------------

    /**
     * /kill la retira al momento, sin liberacion ni botin: es una orden de
     * administrador, no el final del combate.
     */
    @Override
    public void kill(ServerLevel nivel) {
        soltarGancho();
        discard();
    }

    @Override
    public void die(DamageSource fuente) {
        super.die(fuente);
        entityData.set(DATA_OBJETIVO, -1);
        soltarGancho();
    }

    @Override
    protected void tickDeath() {
        ++deathTime;
        if (!(level() instanceof ServerLevel nivel) || isRemoved()) {
            return;
        }
        if (deathTime == 1) {
            sonido(AtalayaSonidos.NEREA_LIBERACION, 5.0F);
        }
        if (deathTime == 46) {
            playSound(AtalayaSonidos.NEREA_PASO, 4.0F, 0.7F);
            golpeSuelo(nivel, position(), 2.2F, 7.0F, 16, 0);
        }
        Vec3 c = puntoMundo(NereaGeometria.CORAZON_AGOTADO);
        if (deathTime == NereaGeometria.LIBERACION_OJOS_ORO) {
            nivel.sendParticles(AtalayaParticulas.NEREA_LUZ, c.x, c.y, c.z, 40, 1.0, 1.4, 1.0, 0.08);
        }
        if (deathTime > NereaGeometria.LIBERACION_OJOS_ORO && deathTime % 3 == 0) {
            nivel.sendParticles(AtalayaParticulas.NEREA_LUZ, c.x, c.y, c.z, 2, 1.2, 1.6, 1.2, 0.01);
        }
        if (deathTime == 150) {
            Vec3 m = position();
            for (Player p : nivel.getEntitiesOfClass(Player.class, new AABB(m, m).inflate(80))) {
                p.addEffect(new MobEffectInstance(BendicionMareasEffect.BENDICION, 20 * 60 * 10, 0), this);
            }
        }
        if (deathTime == 160) {
            sonido(AtalayaSonidos.NEREA_DISOLVER, 4.0F);
        }
        if (deathTime >= NereaGeometria.DURACION_LIBERACION) {
            golpeSuelo(nivel, position(), 1.2F, 8.0F, 0, 30);
            nivel.sendParticles(AtalayaParticulas.NEREA_ESPUMA, getX(), getY() + 3.0, getZ(), 60, 1.4, 2.5, 1.4, 0.05);
            nivel.sendParticles(AtalayaParticulas.NEREA_GOTA, getX(), getY() + 4.0, getZ(), 50, 1.4, 2.5, 1.4, 0.2);
            nivel.sendParticles(AtalayaParticulas.NEREA_LUZ, getX(), getY() + 4.0, getZ(), 50, 1.4, 3.0, 1.4, 0.05);
            remove(RemovalReason.KILLED);
        }
    }

    // ------------------------------------------------------------------
    //  Geometria: del espacio del cuerpo (NereaGeometria) al mundo
    // ------------------------------------------------------------------

    /** Un punto en bloques (izquierda, alto, frente) del cuerpo, en el mundo. */
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

    private Vec3 enRumbo(float grados, double r) {
        float b = grados * Mth.DEG_TO_RAD;
        return new Vec3(getX() - Mth.sin(b) * r, getY(), getZ() + Mth.cos(b) * r);
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

    private static Vec3 horizontalHacia(Vec3 desde, Vec3 hasta) {
        Vec3 d = new Vec3(hasta.x - desde.x, 0, hasta.z - desde.z);
        return d.lengthSqr() < 1.0E-4 ? new Vec3(1, 0, 0) : d.normalize();
    }

    private boolean esPresa(LivingEntity v) {
        if (v == this || v instanceof NereaEntity || !v.isAlive()) {
            return false;
        }
        return !(v instanceof Player p) || (!p.isCreative() && !p.isSpectator());
    }

    /** Jugadores (que no sean creativo ni espectador) entre min y max bloques del centro de la arena... de el. */
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

    private List<Player> jugadoresEnAnillo(ServerLevel nivel) {
        List<Player> out = new ArrayList<>();
        for (Player p : jugadores(nivel, RADIO_MOLINO - 0.5, MOLINO_PIES + 0.5)) {
            out.add(p);
        }
        return out;
    }

    private @Nullable LivingEntity presaArpon(ServerLevel nivel) {
        Player mejor = null;
        double lejos = 0;
        for (Player p : jugadores(nivel, 40, 8)) {
            double d = horizontal(position(), p.position());
            if (d > lejos && hasLineOfSight(p)) {
                lejos = d;
                mejor = p;
            }
        }
        return mejor;
    }

    private @Nullable LivingEntity presaMirada(ServerLevel nivel) {
        List<Player> vistos = new ArrayList<>();
        Vec3 ojos = puntoMundo(NereaGeometria.OJO_IZQ_MIRADA);
        for (Player p : jugadores(nivel, 48, 4)) {
            BlockHitResult choque = nivel.clip(new ClipContext(ojos, p.getEyePosition(), ClipContext.Block.COLLIDER,
                    ClipContext.Fluid.NONE, this));
            if (choque.getType() == HitResult.Type.MISS) {
                vistos.add(p);
            }
        }
        return vistos.isEmpty() ? null : vistos.get(random.nextInt(vistos.size()));
    }

    /**
     * Un golpe contra el suelo: la onda expansiva (que en el cliente sacude la
     * camara de quien este cerca), esquirlas de piedra que saltan, polvo y, si
     * se pide, un geiser de agua que sube y cae.
     */
    private void golpeSuelo(ServerLevel nivel, Vec3 p, float temblor, float radio, int rocas, int geiser) {
        double y = getY();
        nivel.sendParticles(AtalayaParticulas.NEREA_ONDA, p.x, y + 0.12, p.z, 0, temblor, radio, 0.0, 1.0);
        for (int i = 0; i < rocas; i++) {
            double a = random.nextDouble() * Math.PI * 2;
            double v = 0.15 + random.nextDouble() * 0.35;
            nivel.sendParticles(AtalayaParticulas.NEREA_ROCA, p.x, y + 0.3, p.z, 0,
                    Math.cos(a) * v, 0.35 + random.nextDouble() * 0.45, Math.sin(a) * v, 1.0);
        }
        nivel.sendParticles(AtalayaParticulas.NEREA_POLVO, p.x, y + 0.2, p.z, 10 + (int) (radio * 3), radio * 0.3, 0.1,
                radio * 0.3, 0.03);
        for (int i = 0; i < geiser; i++) {
            double ox = random.nextGaussian() * 0.5;
            double oz = random.nextGaussian() * 0.5;
            nivel.sendParticles(i % 2 == 0 ? AtalayaParticulas.NEREA_ESPUMA : AtalayaParticulas.NEREA_GOTA,
                    p.x + ox, y + 0.3, p.z + oz, 0, ox * 0.15, 0.7 + random.nextDouble() * 0.7, oz * 0.15, 1.0);
        }
    }

    private void anillo(ServerLevel nivel, net.minecraft.core.particles.SimpleParticleType tipo, double r, int n, double vel) {
        for (int i = 0; i < n; i++) {
            double a = Math.PI * 2 * i / n;
            nivel.sendParticles(tipo, getX() + Math.cos(a) * r, getY() + 0.2, getZ() + Math.sin(a) * r, 0,
                    Math.cos(a), 0.15, Math.sin(a), vel);
        }
    }

    private void sonido(SoundEvent s, float volumen) {
        playSound(s, volumen, 1.0F);
    }

    /** Corta un sonido largo (el zumbido de la mirada) a quien lo este oyendo. */
    private void cortarSonido(ServerLevel nivel, SoundEvent s) {
        ClientboundStopSoundPacket paquete = new ClientboundStopSoundPacket(s.location(), SoundSource.HOSTILE);
        for (ServerPlayer p : nivel.players()) {
            if (p.distanceToSqr(this) < 96 * 96) {
                p.connection.send(paquete);
            }
        }
    }

    // ------------------------------------------------------------------
    //  Sonidos propios y detalles de gigante
    // ------------------------------------------------------------------

    @Override
    protected @Nullable SoundEvent getAmbientSound() {
        return getEstado() == DORMIDO || getEstado() == LIBRE ? AtalayaSonidos.NEREA_AMBIENTE : null;
    }

    @Override
    public int getAmbientSoundInterval() {
        return 220;
    }

    @Override
    protected SoundEvent getHurtSound(DamageSource fuente) {
        return AtalayaSonidos.NEREA_HERIDO;
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
        playSound(AtalayaSonidos.NEREA_PASO, 2.0F, 0.9F + random.nextFloat() * 0.2F);
    }

    /** Una pisada cada 2,3 bloques: las zancadas de un gigante. */
    @Override
    protected float nextStep() {
        return moveDist + 2.3F;
    }

    @Override
    public boolean causeFallDamage(double distancia, float multiplicador, DamageSource fuente) {
        return false;
    }

    @Override
    public boolean canBreatheUnderwater() {
        return true;
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
