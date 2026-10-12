package com.atalaya.entity;

import com.atalaya.particula.AtalayaParticulas;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleOptions;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.resources.ResourceKey;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundSource;
import net.minecraft.tags.DamageTypeTags;
import net.minecraft.util.Mth;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.damagesource.DamageType;
import net.minecraft.world.damagesource.DamageTypes;
import net.minecraft.world.entity.AnimationState;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.storage.ValueInput;
import net.minecraft.world.level.storage.ValueOutput;
import net.minecraft.world.phys.Vec3;
import org.joml.Vector3f;
import org.joml.Vector3fc;
import org.jspecify.annotations.Nullable;

import java.util.ArrayList;
import java.util.List;

/**
 * Lo comun de los cuatro mini jefes (Moctezuma, Yiatzo, Atlahua y Xiuhquetzal),
 * con las reglas de Juan (10-10-2026): una sola barra de vida y sin fases, sin
 * tocar el clima, sin minijuegos ni nada que haya que hacer aparte de pelear, y
 * solo tres ataques: el normal, el de area y el especial.
 *
 * Como los jefes, nacen dormidos (cada uno en su postura) y despiertan al ver a
 * un jugador o al recibir un golpe, con la presentacion de cine
 * (PresentacionJefe): mientras despiertan y su cartel se lee no se mueven, no
 * atacan y no se les hace dano. La vida es "efectiva": la de vanilla tiene tope
 * de 1024, asi que el dano que reciben se divide (factorGrupo). Al morir hacen
 * su animacion y se deshacen (MiniJefeRenderer).
 *
 * Lo que pinta el cliente (la ola, el ciclon, los tajos...) sale del estado, del
 * tiempo que lleva en el y de dos datos del ataque que se mandan al empezarlo:
 * hacia donde va (getRumbo) y su punto (getPunto). Asi no hacen falta entidades
 * para los efectos grandes y el servidor pega con las mismas cuentas.
 *
 * Cada mini jefe pone sus tiempos (los de su Geometria), como se mueve, cuando
 * ataca y que hace cada ataque en cada tick.
 */
public abstract class MiniJefeEntity extends Monster {

    public static final int LIBRE = 0;
    public static final int DORMIDO = 1;
    public static final int DESPERTAR = 2;
    public static final int NORMAL = 3;
    public static final int AREA = 4;
    public static final int ESPECIAL = 5;

    /** La vida de vanilla (su tope); la de verdad es vidaEfectiva(). */
    protected static final float VIDA_VANILLA = 1024.0F;
    /** Hasta donde ve para despertar (bloques). */
    protected static final double RANGO_DESPERTAR = 28.0;
    /** Lo que se aparta de donde nacio, como mucho (bloques). */
    protected static final double CORREA = 48.0;

    private static final EntityDataAccessor<Integer> DATA_ESTADO =
            SynchedEntityData.defineId(MiniJefeEntity.class, EntityDataSerializers.INT);
    /** Hacia donde va el ataque en curso (grados, como el giro del cuerpo). */
    private static final EntityDataAccessor<Float> DATA_RUMBO =
            SynchedEntityData.defineId(MiniJefeEntity.class, EntityDataSerializers.FLOAT);
    /** El punto del ataque en curso (en el mundo): donde va a caer, a quien apunta... */
    private static final EntityDataAccessor<Vector3fc> DATA_PUNTO =
            SynchedEntityData.defineId(MiniJefeEntity.class, EntityDataSerializers.VECTOR3);
    /**
     * Hacia donde mira la cabeza respecto al cuerpo, para los que la mueven solos (el fenix): x el giro (grados, a su
     * izquierda positivo como el rumbo) e y la inclinacion (grados, positiva hacia abajo).
     */
    private static final EntityDataAccessor<Vector3fc> DATA_MIRA =
            SynchedEntityData.defineId(MiniJefeEntity.class, EntityDataSerializers.VECTOR3);

    // --- Cliente ---
    public final AnimationState dormido = new AnimationState();
    public final AnimationState despertar = new AnimationState();
    public final AnimationState normal = new AnimationState();
    public final AnimationState area = new AnimationState();
    public final AnimationState especial = new AnimationState();
    public final AnimationState muerte = new AnimationState();
    /** Cuando empezo el estado actual (tick del cliente). */
    public int inicioEstado;
    /** Lo que pesa la animacion de reposo y paso (1 libre, 0 atacando), suavizado. */
    public float pesoLibre;
    public float pesoLibreAnt;
    /** Lo deprisa que va (bloques por tick), suavizado, y el reloj del paso, que corre con ella. */
    public float velocidad;
    public float velocidadAnt;
    public float relojAndar;
    public float relojAndarAnt;
    /** Hacia donde mira la cabeza (DATA_MIRA), suavizado en el cliente. */
    public float miraGiro;
    public float miraGiroAnt;
    public float miraAlto;
    public float miraAltoAnt;

    // --- Servidor ---
    protected @Nullable BlockPos centro;
    protected int t;
    protected int duracion;
    protected int respiro;
    /** En escena tras despertar (su cartel aun se lee): ni se mueve, ni ataca, ni le entra nada. */
    protected int escena;
    protected final int[] enfriamiento = new int[3];
    private int ultimoAvisoInmune;
    /** Lo que tiene que pasar dentro de unos ticks (los fragmentos que caen, las plumas que llegan...). */
    private final List<Pendiente> pendientes = new ArrayList<>();

    private record Pendiente(int cuando, java.util.function.Consumer<ServerLevel> que) {
    }

    protected MiniJefeEntity(EntityType<? extends MiniJefeEntity> tipo, Level nivel) {
        super(tipo, nivel);
        this.xpReward = 120;
        setPersistenceRequired();
    }

    public static AttributeSupplier.Builder atributosBase(double armadura, double velocidad) {
        return Monster.createMonsterAttributes()
                .add(Attributes.MAX_HEALTH, VIDA_VANILLA)
                .add(Attributes.ARMOR, armadura)
                .add(Attributes.ARMOR_TOUGHNESS, 8.0D)
                .add(Attributes.ATTACK_DAMAGE, 10.0D)
                .add(Attributes.MOVEMENT_SPEED, velocidad)
                .add(Attributes.FOLLOW_RANGE, 64.0D)
                .add(Attributes.KNOCKBACK_RESISTANCE, 1.0D)
                .add(Attributes.STEP_HEIGHT, 1.6D);
    }

    // ------------------------------------------------------------------
    //  Lo de cada mini jefe
    // ------------------------------------------------------------------

    /** Su vida de verdad (el dano que recibe se divide en esa proporcion). */
    protected abstract float vidaEfectiva();

    /** Lo que dura cada estado (ticks): DESPERTAR, NORMAL, AREA y ESPECIAL. */
    protected abstract int duracion(int estado);

    /** Lo que tarda en desaparecer al morir (ticks): su animacion de muerte y deshacerse. */
    public abstract int duracionMuerte();

    /** Desde que tick de la muerte empieza a deshacerse. */
    public abstract int disolverDesde();

    /** El ataque que toca (NORMAL, AREA o ESPECIAL), o -1 si ninguno. */
    protected abstract int elegirAtaque(ServerLevel nivel, LivingEntity objetivo, double distancia);

    /** Lo que hace cada tick del ataque (t empieza en 1). */
    protected abstract void tickAtaque(ServerLevel nivel, int estado, int t, @Nullable LivingEntity objetivo);

    /** Lo que suena y salta mientras despierta (t empieza en 1). */
    protected abstract void tickDespertar(ServerLevel nivel, int t);

    /** Lo que suena y salta mientras muere (deathTime empieza en 1). */
    protected abstract void tickMuerte(ServerLevel nivel, int tiempo);

    /** Lo que ve el cliente en cada tick (particulas, segun el estado y el tiempo que lleva en el). */
    protected abstract void efectosCliente(int estado, int tiempo);

    /** Lo que espera tras cada ataque antes del siguiente (ticks). */
    protected int pausa(int estado) {
        return 16;
    }

    /** Hasta donde se acerca a su presa antes de plantarse (bloques). */
    protected double alcance() {
        return 3.5;
    }

    /** Lo deprisa que anda (multiplicador del control de movimiento). */
    protected double paso() {
        return 1.0;
    }

    /** Al empezar un ataque (el sonido, el enfriamiento...). */
    protected void alIniciar(ServerLevel nivel, int estado, @Nullable LivingEntity objetivo) {
    }

    /** Al acabar un ataque. */
    protected void alAcabar(ServerLevel nivel, int estado) {
    }

    // ------------------------------------------------------------------
    //  Datos
    // ------------------------------------------------------------------

    @Override
    protected void defineSynchedData(SynchedEntityData.Builder datos) {
        super.defineSynchedData(datos);
        datos.define(DATA_ESTADO, DORMIDO);
        datos.define(DATA_RUMBO, 0.0F);
        datos.define(DATA_PUNTO, new Vector3f());
        datos.define(DATA_MIRA, new Vector3f());
    }

    @Override
    protected void registerGoals() {
        // Sin goals de movimiento: andar y atacar lo decide customServerAiStep.
        targetSelector.addGoal(2, new NearestAttackableTargetGoal<>(this, Player.class, false));
    }

    public int getEstado() {
        return entityData.get(DATA_ESTADO);
    }

    public float getRumbo() {
        return entityData.get(DATA_RUMBO);
    }

    public Vec3 getPunto() {
        Vector3fc p = entityData.get(DATA_PUNTO);
        return new Vec3(p.x(), p.y(), p.z());
    }

    protected void ponerRumbo(float rumbo) {
        entityData.set(DATA_RUMBO, rumbo);
    }

    protected void ponerPunto(Vec3 p) {
        entityData.set(DATA_PUNTO, new Vector3f((float) p.x, (float) p.y, (float) p.z));
    }

    protected void ponerEstado(int estado, int dur) {
        entityData.set(DATA_ESTADO, estado);
        t = 0;
        duracion = dur;
    }

    /** Lo que lleva en el estado (ticks, con la fraccion del fotograma), visto desde el cliente. */
    public float tiempoEstado(float parcial) {
        return tickCount - inicioEstado + parcial;
    }

    // ------------------------------------------------------------------
    //  Cliente
    // ------------------------------------------------------------------

    @Override
    public void onSyncedDataUpdated(EntityDataAccessor<?> dato) {
        super.onSyncedDataUpdated(dato);
        if (DATA_ESTADO.equals(dato) && level().isClientSide()) {
            arrancarAnimacion();
        }
    }

    private AnimationState[] acciones() {
        return new AnimationState[]{dormido, despertar, normal, area, especial};
    }

    private @Nullable AnimationState animacionDe(int estado) {
        return switch (estado) {
            case DORMIDO -> dormido;
            case DESPERTAR -> despertar;
            case NORMAL -> normal;
            case AREA -> area;
            case ESPECIAL -> especial;
            default -> null;
        };
    }

    private void arrancarAnimacion() {
        for (AnimationState a : acciones()) {
            a.stop();
        }
        inicioEstado = tickCount;
        AnimationState actual = animacionDe(getEstado());
        if (actual != null) {
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
        float objetivoPeso = getEstado() == LIBRE && !muriendo ? 1.0F : 0.0F;
        pesoLibre = objetivoPeso > pesoLibre ? Math.min(objetivoPeso, pesoLibre + 0.12F) : Math.max(objetivoPeso, pesoLibre - 0.34F);
        velocidadAnt = velocidad;
        relojAndarAnt = relojAndar;
        miraGiroAnt = miraGiro;
        miraAltoAnt = miraAlto;
        Vector3fc mira = entityData.get(DATA_MIRA);
        miraGiro += (mira.x() - miraGiro) * 0.3F;
        miraAlto += (mira.y() - miraAlto) * 0.3F;
        double vx = getX() - xo;
        double vz = getZ() - zo;
        float v = getEstado() == LIBRE && !muriendo ? (float) Math.sqrt(vx * vx + vz * vz) : 0.0F;
        velocidad += (v - velocidad) * 0.3F;
        // El reloj del paso corre con lo que anda: las pisadas van con el suelo.
        relojAndar += 50.0F * Mth.clamp(velocidad / zancada(), 0.0F, 2.5F);
        if (muriendo) {
            if (!muerte.isStarted()) {
                for (AnimationState a : acciones()) {
                    a.stop();
                }
                muerte.start(tickCount);
            }
            efectosMuerte(deathTime);
            return;
        }
        efectosCliente(getEstado(), tickCount - inicioEstado);
    }

    /** Lo que avanza el cuerpo por tick en un ciclo de paso a su ritmo (bloques): el de su Geometria. */
    protected float zancada() {
        return 0.12F;
    }

    /** Lo que ve el cliente mientras muere. */
    protected void efectosMuerte(int tiempo) {
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
        if (isDeadOrDying()) {
            pendientes.clear();
            return;
        }
        if (!pendientes.isEmpty()) {
            List<Pendiente> ahora = new ArrayList<>();
            pendientes.removeIf(q -> {
                if (q.cuando() <= tickCount) {
                    ahora.add(q);
                    return true;
                }
                return false;
            });
            for (Pendiente q : ahora) {
                q.que().accept(nivel);
            }
        }
        t++;
        if (respiro > 0) respiro--;
        if (escena > 0) escena--;
        for (int i = 0; i < enfriamiento.length; i++) {
            if (enfriamiento[i] > 0) enfriamiento[i]--;
        }
        int e = getEstado();
        LivingEntity objetivo = getTarget();
        if (e != DORMIDO) {
            objetivo = PresasJefe.revisar(nivel, this, objetivo, Vec3.atCenterOf(centro), CORREA + 16, e == LIBRE);
            objetivo = com.atalaya.habilidad.Provocacion.objetivo(this, objetivo, com.atalaya.habilidad.Provocacion.ALCANCE);
            if (objetivo != null && getTarget() != objetivo) {
                setTarget(objetivo);
            }
        }
        switch (e) {
            case DORMIDO -> {
                quieto();
                if (t % 5 == 0) {
                    for (Player p : jugadores(nivel, RANGO_DESPERTAR)) {
                        if (PresasJefe.despierta(nivel, this, p)) {
                            despertarse(p);
                            break;
                        }
                    }
                }
            }
            case DESPERTAR -> {
                quieto();
                if (objetivo != null) {
                    // Se gira hacia quien le desperto despacio, mientras se levanta.
                    girarHacia(objetivo.position(), 1.5F);
                }
                tickDespertar(nivel, t);
                if (t >= duracion) {
                    ponerEstado(LIBRE, 0);
                    escena = PresasJefe.ESCENA_QUIETO;
                    respiro = PresasJefe.RESPIRO_PRESENTACION;
                }
            }
            case LIBRE -> tickLibre(nivel, objetivo);
            default -> {
                quieto();
                tickAtaque(nivel, e, t, objetivo);
                if (t >= duracion && getEstado() == e) {
                    alAcabar(nivel, e);
                    ponerEstado(LIBRE, 0);
                    respiro = pausa(e);
                }
            }
        }
    }

    private void tickLibre(ServerLevel nivel, @Nullable LivingEntity objetivo) {
        if (escena > 0) {
            quieto();
            return;
        }
        double d = objetivo == null ? 0.0 : horizontal(position(), objetivo.position());
        moverse(nivel, objetivo, d);
        if (objetivo != null && respiro <= 0) {
            int a = elegirAtaque(nivel, objetivo, d);
            if (a >= 0) {
                iniciar(nivel, a, objetivo);
            }
        }
    }

    /** Empieza un ataque: de cara a su presa, con su rumbo y su punto para el cliente. */
    public void iniciar(ServerLevel nivel, int estado, @Nullable LivingEntity objetivo) {
        if (objetivo != null) {
            fijarRumbo(rumboHacia(objetivo.position()));
            ponerPunto(objetivo.position());
        } else {
            ponerPunto(position().add(frente().scale(6.0)));
        }
        ponerRumbo(getYRot());
        ponerEstado(estado, duracion(estado));
        alIniciar(nivel, estado, objetivo);
    }

    /** Hacia su presa (sin salir de su sitio): anda si esta lejos y de cerca se planta mirandola. */
    protected void moverse(ServerLevel nivel, @Nullable LivingEntity objetivo, double d) {
        Vec3 c = Vec3.atBottomCenterOf(centro);
        if (objetivo == null) {
            if (horizontal(position(), c) > 4.0) {
                getMoveControl().setWantedPosition(c.x, c.y, c.z, paso() * 0.8);
            } else {
                quieto();
            }
            return;
        }
        Vec3 meta = objetivo.position();
        Vec3 rel = new Vec3(meta.x - c.x, 0, meta.z - c.z);
        if (rel.length() > CORREA) {
            rel = rel.normalize().scale(CORREA);
            meta = new Vec3(c.x + rel.x, meta.y, c.z + rel.z);
        }
        if (d > alcance()) {
            getMoveControl().setWantedPosition(meta.x, meta.y, meta.z, paso());
        } else {
            quieto();
            girarHacia(objetivo.position(), 12.0F);
        }
    }

    /**
     * Para probar (/atalaya minijefe): despertar, un ataque ya (normal, area o
     * especial, contra el jugador mas cercano aunque este en creativo), volver a
     * dormir o morir.
     */
    public boolean forzar(ServerLevel nivel, String orden) {
        LivingEntity o = getTarget();
        if (o == null) {
            o = nivel.getNearestPlayer(this, 64.0);
        }
        switch (orden) {
            case "despertar" -> {
                if (getEstado() != DORMIDO) {
                    ponerEstado(DORMIDO, 0);
                }
                despertarse(o);
            }
            case "normal", "area", "especial" -> {
                escena = 0;
                respiro = 0;
                iniciar(nivel, orden.equals("normal") ? NORMAL : orden.equals("area") ? AREA : ESPECIAL, o);
            }
            case "dormir" -> ponerEstado(DORMIDO, 0);
            case "libre" -> {
                ponerEstado(LIBRE, 0);
                escena = 0;
            }
            case "morir" -> kill(nivel);
            default -> {
                return false;
            }
        }
        return true;
    }

    private void despertarse(@Nullable Entity quien) {
        if (getEstado() != DORMIDO) {
            return;
        }
        if (quien instanceof LivingEntity vivo && PresasJefe.vale(vivo)) {
            setTarget(vivo);
        }
        ponerEstado(DESPERTAR, duracion(DESPERTAR));
    }

    /** Si el ataque esta listo (su enfriamiento a cero). */
    protected boolean listo(int estado) {
        return enfriamiento[estado - NORMAL] <= 0;
    }

    protected void enfriar(int estado, int ticks) {
        enfriamiento[estado - NORMAL] = ticks;
    }

    /** Que el control de movimiento no lo arrastre: se queda donde esta y no gira solo. */
    protected void quieto() {
        getNavigation().stop();
        getMoveControl().setWantedPosition(getX(), getY(), getZ(), 0.0);
        if (!isNoGravity()) {
            Vec3 v = getDeltaMovement();
            setDeltaMovement(0.0, v.y, 0.0);
        }
    }

    // ------------------------------------------------------------------
    //  Dano
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
        if (PresasJefe.esJefe(causante)) {
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
        if (causante instanceof LivingEntity vivo && PresasJefe.vale(vivo) && random.nextInt(4) == 0 && e == LIBRE) {
            setTarget(vivo);
        }
        return super.hurtServer(nivel, fuente, cantidad * VIDA_VANILLA / vidaEfectiva());
    }

    /** El golpe que no le entra (dormido, despertando, en escena): un chasquido y unas chispas donde le dieron. */
    private void avisoInmune(ServerLevel nivel, @Nullable Entity causante) {
        if (tickCount - ultimoAvisoInmune < 5) {
            return;
        }
        ultimoAvisoInmune = tickCount;
        Vec3 p = position().add(0, getBbHeight() * 0.6, 0);
        if (causante != null) {
            Vec3 fuera = horizontalHacia(position(), causante.position());
            p = new Vec3(getX() + fuera.x * getBbWidth() * 0.6, Mth.clamp(causante.getEyeY(), getY() + 0.5, getY() + getBbHeight()),
                    getZ() + fuera.z * getBbWidth() * 0.6);
        }
        SoundEvent s = sonidoInmune();
        if (s != null) {
            nivel.playSound(null, p.x, p.y, p.z, s, SoundSource.HOSTILE, 1.2F, 0.9F + random.nextFloat() * 0.2F);
        }
        nivel.sendParticles(particulaInmune(), true, true, p.x, p.y, p.z, 5, 0.3, 0.3, 0.3, 0.1);
    }

    protected @Nullable SoundEvent sonidoInmune() {
        return null;
    }

    protected ParticleOptions particulaInmune() {
        return AtalayaParticulas.ESTRELLA;
    }

    /**
     * Pega a v un golpe de dano base "dano" (los de la ficha: contra netherita P4
     * y manzana de Notch, como los jefes) y lo empuja "empuje" (bloques por tick,
     * hacia fuera desde "desde") y "sube" hacia arriba.
     */
    protected boolean golpear(ServerLevel nivel, LivingEntity v, ResourceKey<DamageType> tipo, float dano, Vec3 desde,
                              double empuje, double sube) {
        if (!esPresa(v)) {
            return false;
        }
        boolean entra = v.hurtServer(nivel, MiniJefeDanos.fuente(nivel, tipo, this, this), RajangEntity.contraArmadura(v, dano));
        if (empuje > 0.0 || sube > 0.0) {
            Vec3 fuera = horizontalHacia(desde, v.position());
            double k = 1.0 - Mth.clamp(v.getAttributeValue(Attributes.KNOCKBACK_RESISTANCE), 0.0, 1.0) * 0.6;
            v.setDeltaMovement(v.getDeltaMovement().multiply(0.3, 0.0, 0.3)
                    .add(fuera.x * empuje * k, sube * k, fuera.z * empuje * k));
            v.hurtMarked = true;
        }
        return entra;
    }

    /** Lo que sus ataques pueden golpear: solo jugadores (y maniquies de prueba), nunca otro jefe. */
    public boolean esPresa(LivingEntity v) {
        return v != this && PresasJefe.presa(v);
    }

    /** Las presas a menos de "radio" (en horizontal) de p y a menos de "alto" en vertical. */
    protected List<LivingEntity> presasCerca(ServerLevel nivel, Vec3 p, double radio, double alto) {
        List<LivingEntity> out = new ArrayList<>();
        for (LivingEntity v : nivel.getEntitiesOfClass(LivingEntity.class,
                new net.minecraft.world.phys.AABB(p, p).inflate(radio, alto, radio), this::esPresa)) {
            if (horizontal(p, v.position()) <= radio) {
                out.add(v);
            }
        }
        return out;
    }

    protected List<Player> jugadores(ServerLevel nivel, double max) {
        List<Player> out = new ArrayList<>();
        for (Player p : nivel.getEntitiesOfClass(Player.class, getBoundingBox().inflate(max, max + 16, max))) {
            if (p.isCreative() || p.isSpectator() || !p.isAlive()) {
                continue;
            }
            if (horizontal(position(), p.position()) <= max) {
                out.add(p);
            }
        }
        return out;
    }

    /** Que pase algo dentro de "ticks" ticks (aunque el ataque ya haya acabado). */
    protected void programar(int ticks, java.util.function.Consumer<ServerLevel> que) {
        pendientes.add(new Pendiente(tickCount + Math.max(1, ticks), que));
    }

    /** Particulas que se ven de lejos (el grupo esta lejos): n alrededor de c con esa dispersion y velocidad. */
    protected static void particulas(ServerLevel nivel, ParticleOptions p, Vec3 c, int n, double dx, double dy, double dz,
                                     double vel) {
        nivel.sendParticles(p, true, true, c.x, c.y, c.z, n, dx, dy, dz, vel);
    }

    /** Una particula con sus tres numeros (la onda, la marca, la grieta...: count 0 y velocidad 1). */
    protected static void particula(ServerLevel nivel, ParticleOptions p, Vec3 c, double a, double b, double d) {
        nivel.sendParticles(p, true, true, c.x, c.y, c.z, 0, a, b, d, 1.0);
    }

    /** Lo alto del suelo bajo (x, z), buscando desde y hacia abajo (hasta 24 bloques). */
    protected double suelo(ServerLevel nivel, double x, double y, double z) {
        BlockPos.MutableBlockPos b = new BlockPos.MutableBlockPos(Mth.floor(x), Mth.floor(y), Mth.floor(z));
        for (int i = 0; i < 24; i++) {
            if (!nivel.getBlockState(b).getCollisionShape(nivel, b).isEmpty()) {
                return b.getY() + nivel.getBlockState(b).getCollisionShape(nivel, b).max(net.minecraft.core.Direction.Axis.Y);
            }
            b.move(0, -1, 0);
        }
        return y - 24;
    }

    protected void sonido(SoundEvent s, float volumen) {
        playSound(s, volumen, 1.0F);
    }

    protected void sonido(SoundEvent s, float volumen, float tono) {
        playSound(s, volumen, tono);
    }

    // ------------------------------------------------------------------
    //  Muerte
    // ------------------------------------------------------------------

    @Override
    protected void tickDeath() {
        ++deathTime;
        if (!(level() instanceof ServerLevel nivel) || isRemoved()) {
            return;
        }
        if (!isNoGravity()) {
            setDeltaMovement(0, Math.min(0, getDeltaMovement().y), 0);
        }
        tickMuerte(nivel, deathTime);
        if (deathTime >= duracionMuerte()) {
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

    /** Un punto en bloques (izquierda, alto, frente) desde p y con el rumbo r (grados). */
    public static Vec3 puntoMundo(Vec3 local, Vec3 p, float r) {
        return NereaEntity.puntoMundo(local, p, r);
    }

    public Vec3 frente() {
        float b = yBodyRot * Mth.DEG_TO_RAD;
        return new Vec3(-Mth.sin(b), 0, Mth.cos(b));
    }

    public static Vec3 frente(float rumbo) {
        float b = rumbo * Mth.DEG_TO_RAD;
        return new Vec3(-Mth.sin(b), 0, Mth.cos(b));
    }

    protected float rumboHacia(Vec3 p) {
        return (float) (Mth.atan2(p.z - getZ(), p.x - getX()) * Mth.RAD_TO_DEG) - 90.0F;
    }

    /**
     * Lleva la mirada (la cabeza, no el cuerpo) hacia un punto del mundo, poco a poco; sin punto, al frente. 'ojos' es
     * donde tiene la cabeza, en bloques del cuerpo (su Geometria.CABEZA).
     */
    protected void mirarA(@Nullable Vec3 p, Vec3 ojos) {
        Vector3fc m = entityData.get(DATA_MIRA);
        float giro = 0.0F;
        float alto = 0.0F;
        if (p != null) {
            Vec3 o = puntoMundo(ojos);
            giro = Mth.clamp(Mth.wrapDegrees(rumboHacia(p) - getYRot()), -70.0F, 70.0F);
            alto = (float) Mth.clamp(Math.toDegrees(Math.atan2(o.y - p.y, Math.max(0.5, horizontal(o, p)))), -35.0, 60.0);
        }
        float g = m.x() + (giro - m.x()) * 0.25F;
        float a = m.y() + (alto - m.y()) * 0.25F;
        if (Math.abs(g - m.x()) > 0.05F || Math.abs(a - m.y()) > 0.05F) {
            entityData.set(DATA_MIRA, new Vector3f(g, a, 0.0F));
        }
    }

    protected void girarHacia(Vec3 p, float paso) {
        float deseado = rumboHacia(p);
        float actual = getYRot();
        fijarRumbo(actual + Mth.clamp(Mth.wrapDegrees(deseado - actual), -paso, paso));
    }

    protected void fijarRumbo(float r) {
        setYRot(r);
        yBodyRot = r;
        yHeadRot = r;
    }

    /** El cuerpo mira siempre a donde apunta: girar la cabeza sola, con este tamano, queda raro. */
    @Override
    protected void tickHeadTurn(float rumboCuerpo) {
        this.yBodyRot = getYRot();
        this.yHeadRot = getYRot();
    }

    public static double horizontal(Vec3 a, Vec3 b) {
        double dx = a.x - b.x;
        double dz = a.z - b.z;
        return Math.sqrt(dx * dx + dz * dz);
    }

    public static Vec3 horizontalHacia(Vec3 desde, Vec3 hasta) {
        Vec3 d = new Vec3(hasta.x - desde.x, 0, hasta.z - desde.z);
        return d.lengthSqr() < 1.0E-4 ? new Vec3(1, 0, 0) : d.normalize();
    }

    /** El angulo (grados, -180 a 180) entre su rumbo r y la direccion hacia p desde o. */
    public static float anguloHacia(Vec3 o, float r, Vec3 p) {
        float hacia = (float) (Mth.atan2(p.z - o.z, p.x - o.x) * Mth.RAD_TO_DEG) - 90.0F;
        return Mth.wrapDegrees(hacia - r);
    }

    // ------------------------------------------------------------------
    //  Vanilla
    // ------------------------------------------------------------------

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
    protected void addAdditionalSaveData(ValueOutput salida) {
        super.addAdditionalSaveData(salida);
        if (centro != null) {
            salida.store("centro", BlockPos.CODEC, centro);
        }
        // Despierto se queda despierto (sin volver a presentarse); a medio ataque, libre.
        salida.putInt("estado", getEstado() == DORMIDO ? DORMIDO : LIBRE);
    }

    @Override
    protected void readAdditionalSaveData(ValueInput entrada) {
        super.readAdditionalSaveData(entrada);
        centro = entrada.read("centro", BlockPos.CODEC).orElse(null);
        entityData.set(DATA_ESTADO, entrada.getIntOr("estado", DORMIDO));
    }
}
