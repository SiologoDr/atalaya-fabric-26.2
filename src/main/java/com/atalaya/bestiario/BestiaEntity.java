package com.atalaya.bestiario;

import com.atalaya.Atalaya;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Holder;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.particles.ParticleOptions;
import net.minecraft.core.particles.SimpleParticleType;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.util.Mth;
import net.minecraft.resources.Identifier;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.effect.MobEffect;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.entity.AnimationState;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.storage.ValueInput;
import net.minecraft.world.level.storage.ValueOutput;
import org.jspecify.annotations.Nullable;

import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;

/**
 * La base de los mobs del bestiario (Bestias): lo que todos hacen igual, para que cada uno solo traiga su mecanica.
 *
 * - Sus sonidos son los suyos (bestia.&lt;id&gt;.ambiente, herido, muerte, paso...: bestiario_sonidos.py), nunca los de
 *   Minecraft.
 * - Sus animaciones de golpe (el ataque, los especiales, la muerte y la aparicion) se arrancan en el servidor con
 *   {@link #animar} y llegan a cada cliente como un evento de la entidad; las que van solas (el reposo, el paso y las de
 *   cada estado) las lleva el modelo (BestiaModel).
 * - Un estado (enterrado, agarrado, cargando...) y una variante (su textura) que se ven en el cliente, y un valor de 0 a
 *   1 que cada uno usa para lo suyo (lo hinchado, lo encendido).
 * - Lo que pasa a destiempo (el dano en el fotograma del golpe) se programa con {@link #luego}.
 * - Muere con su propia animacion: no se tumba de lado como los de Minecraft (el render no lo voltea) y no se va hasta
 *   que la acaba; entonces se deshace en sus particulas.
 */
public abstract class BestiaEntity extends Monster {

    public static final byte EV_ATAQUE = 70;
    public static final byte EV_ESPECIAL = 71;
    public static final byte EV_ESPECIAL2 = 72;
    public static final byte EV_MUERTE = 73;
    public static final byte EV_APARECE = 74;

    private static final EntityDataAccessor<Integer> DATA_ESTADO =
            SynchedEntityData.defineId(BestiaEntity.class, EntityDataSerializers.INT);
    private static final EntityDataAccessor<Integer> DATA_VARIANTE =
            SynchedEntityData.defineId(BestiaEntity.class, EntityDataSerializers.INT);
    private static final EntityDataAccessor<Float> DATA_VALOR =
            SynchedEntityData.defineId(BestiaEntity.class, EntityDataSerializers.FLOAT);

    public final AnimationState ataque = new AnimationState();
    public final AnimationState especial = new AnimationState();
    public final AnimationState especial2 = new AnimationState();
    public final AnimationState muerte = new AnimationState();
    public final AnimationState aparece = new AnimationState();
    /** El tick en que cambio de estado (en los dos lados). */
    public int estadoDesde;
    /** El valor del tick anterior (para suavizarlo en el cliente). */
    private float valorAnt;
    private float valorAhora;

    /** Lo programado: cuantos ticks le faltan y que hacer. */
    private final List<Programado> programados = new ArrayList<>();

    private static final class Programado {
        int faltan;
        final Runnable que;

        Programado(int faltan, Runnable que) {
            this.faltan = faltan;
            this.que = que;
        }
    }

    protected BestiaEntity(EntityType<? extends Monster> tipo, Level nivel) {
        super(tipo, nivel);
    }

    /** Su ficha del bestiario. */
    public abstract Bestia bestia();

    @Override
    protected void defineSynchedData(SynchedEntityData.Builder datos) {
        super.defineSynchedData(datos);
        datos.define(DATA_ESTADO, 0);
        datos.define(DATA_VARIANTE, 0);
        datos.define(DATA_VALOR, 0.0F);
    }

    @Override
    public void onSyncedDataUpdated(EntityDataAccessor<?> dato) {
        super.onSyncedDataUpdated(dato);
        if (DATA_ESTADO.equals(dato)) {
            estadoDesde = tickCount;
        }
    }

    // ------------------------------------------------------------------
    //  Estado, variante y valor
    // ------------------------------------------------------------------

    public int getEstado() {
        return entityData.get(DATA_ESTADO);
    }

    public void setEstado(int estado) {
        if (getEstado() != estado) {
            entityData.set(DATA_ESTADO, estado);
            estadoDesde = tickCount;
        }
    }

    /** Los ticks que lleva en su estado. */
    public int enEstado() {
        return tickCount - estadoDesde;
    }

    public int getVariante() {
        return entityData.get(DATA_VARIANTE);
    }

    public void setVariante(int variante) {
        entityData.set(DATA_VARIANTE, variante);
    }

    public float getValor() {
        return entityData.get(DATA_VALOR);
    }

    public void setValor(float valor) {
        entityData.set(DATA_VALOR, Mth.clamp(valor, 0.0F, 1.0F));
    }

    /** El valor suavizado entre ticks (para el render). */
    public float valorCliente(float parcial) {
        return Mth.lerp(parcial, valorAnt, valorAhora);
    }

    @Override
    protected void addAdditionalSaveData(ValueOutput salida) {
        super.addAdditionalSaveData(salida);
        salida.putInt("Variante", getVariante());
    }

    @Override
    protected void readAdditionalSaveData(ValueInput entrada) {
        super.readAdditionalSaveData(entrada);
        setVariante(entrada.getIntOr("Variante", 0));
    }

    // ------------------------------------------------------------------
    //  El tick: lo programado
    // ------------------------------------------------------------------

    @Override
    public void tick() {
        super.tick();
        valorAnt = valorAhora;
        valorAhora = getValor();
        if (!level().isClientSide()) {
            setAggressive(presa() != null);
        }
        if (!programados.isEmpty() && !level().isClientSide()) {
            List<Programado> listos = new ArrayList<>();
            for (Iterator<Programado> it = programados.iterator(); it.hasNext(); ) {
                Programado p = it.next();
                if (--p.faltan <= 0) {
                    it.remove();
                    listos.add(p);
                }
            }
            for (Programado p : listos) {
                if (isAlive()) {
                    p.que.run();
                }
            }
        }
    }

    /** Hace algo dentro de unos ticks (si sigue vivo): el dano en el fotograma del golpe, el final de un salto... */
    public void luego(int ticks, Runnable que) {
        if (ticks <= 0) {
            que.run();
        } else {
            programados.add(new Programado(ticks, que));
        }
    }

    /** Olvida lo programado (al cambiar de idea: aturdido, muerto...). */
    public void olvidarLoProgramado() {
        programados.clear();
    }

    // ------------------------------------------------------------------
    //  Animaciones
    // ------------------------------------------------------------------

    /** Arranca una animacion de golpe en todos los clientes (EV_ATAQUE, EV_ESPECIAL...). */
    public void animar(byte evento) {
        if (!level().isClientSide()) {
            level().broadcastEntityEvent(this, evento);
        }
    }

    @Override
    public void handleEntityEvent(byte evento) {
        switch (evento) {
            case EV_ATAQUE -> ataque.start(tickCount);
            case EV_ESPECIAL -> especial.start(tickCount);
            case EV_ESPECIAL2 -> especial2.start(tickCount);
            case EV_MUERTE -> {
                ataque.stop();
                especial.stop();
                especial2.stop();
                muerte.start(tickCount);
            }
            case EV_APARECE -> aparece.start(tickCount);
            default -> super.handleEntityEvent(evento);
        }
    }

    // ------------------------------------------------------------------
    //  El dano y la muerte
    // ------------------------------------------------------------------

    @Override
    public boolean hurtServer(ServerLevel nivel, DamageSource fuente, float dano) {
        float vidaAntes = getHealth();
        boolean herido = super.hurtServer(nivel, fuente, dano);
        if (herido) {
            float quitado = vidaAntes - getHealth();
            if (quitado > 0.0F) {
                mostrarCorazonesDano(nivel, fuente, quitado);
            }
        }
        return herido;
    }

    /** Suelta los corazones de dano en el costado que recibe el golpe (fuera de la malla en los mobs grandes). */
    private void mostrarCorazonesDano(ServerLevel nivel, DamageSource fuente, float quitado) {
        int corazones = Mth.clamp(Math.round(quitado * 0.5F), 1, 14);
        double px = getX();
        double py = getY() + Math.min(getBbHeight() * 0.55, 1.5);
        double pz = getZ();
        Entity origen = fuente.getDirectEntity() != null ? fuente.getDirectEntity() : fuente.getEntity();
        if (origen != null) {
            double dx = origen.getX() - getX();
            double dz = origen.getZ() - getZ();
            double dist = Math.hypot(dx, dz);
            if (dist > 1.0E-3) {
                double r = getBbWidth() * 0.55;
                px += (dx / dist) * r;
                pz += (dz / dist) * r;
            }
            py = Mth.clamp(origen.getEyeY() - 0.15, getY() + 0.4, getY() + getBbHeight() * 0.85);
        }
        double dispersion = Math.max(0.18, getBbWidth() * 0.22);
        nivel.sendParticles(net.minecraft.core.particles.ParticleTypes.DAMAGE_INDICATOR,
                px, py, pz, corazones, dispersion, 0.12, dispersion, 0.18);
    }

    @Override
    public void die(DamageSource fuente) {
        super.die(fuente);
        olvidarLoProgramado();
        animar(EV_MUERTE);
    }

    /** Hasta que acaba su animacion de muerte no se va; luego, sus particulas (alDeshacerse) y fuera. */
    @Override
    protected void tickDeath() {
        deathTime++;
        if (deathTime >= bestia().muerteTicks && !level().isClientSide() && !isRemoved()) {
            if (level() instanceof ServerLevel nivel) {
                alDeshacerse(nivel);
            }
            remove(RemovalReason.KILLED);
        }
    }

    /** Lo que suelta al deshacerse (sus particulas): cada uno el suyo. */
    protected void alDeshacerse(ServerLevel nivel) {
        if (bestia().particulaMuerte != null) {
            particulas(nivel, bestia().particulaMuerte, getX(), getY() + getBbHeight() * 0.5, getZ(), 24,
                    getBbWidth() * 0.45, getBbHeight() * 0.35, 0.05);
        }
    }

    /** Suelta unas de sus particulas (por su nombre) alrededor de un punto. */
    public void particulas(ServerLevel nivel, String nombre, double x, double y, double z, int cuantas, double ancho,
                           double alto, double velocidad) {
        SimpleParticleType tipo = bestia().particula(nombre);
        if (tipo != null) {
            particulas(nivel, tipo, x, y, z, cuantas, ancho, alto, velocidad);
        }
    }

    public static void particulas(ServerLevel nivel, ParticleOptions tipo, double x, double y, double z, int cuantas,
                                  double ancho, double alto, double velocidad) {
        nivel.sendParticles(tipo, x, y, z, cuantas, ancho, alto, ancho, velocidad);
    }

    /**
     * Un estallido sin nada de vanilla: rompe y hace dano como el de siempre, pero en el centro sale una particula del
     * mob (no el humo de vanilla), sin cascotes de vanilla, y suena su sonido (no el de la explosion de vanilla). Las
     * particulas de verdad las suelta cada uno alrededor (su alEstallar).
     */
    public static void estallido(ServerLevel nivel, @Nullable Entity fuente, Bestia b, double x, double y, double z,
                                 float radio, boolean fuego, String particula, String sonido) {
        SimpleParticleType p = b.particula(particula);
        SoundEvent s = b.sonido(sonido);
        ParticleOptions centro = p != null ? p : net.minecraft.core.particles.ParticleTypes.EXPLOSION;
        net.minecraft.core.Holder<SoundEvent> ruido = s != null
                ? net.minecraft.core.registries.BuiltInRegistries.SOUND_EVENT.wrapAsHolder(s)
                : net.minecraft.sounds.SoundEvents.GENERIC_EXPLODE;
        nivel.explode(fuente, null, null, x, y, z, radio, fuego, Level.ExplosionInteraction.MOB, centro, centro,
                net.minecraft.util.random.WeightedList.of(), ruido);
    }

    // ------------------------------------------------------------------
    //  Los sonidos (los suyos)
    // ------------------------------------------------------------------

    @Override
    protected @Nullable SoundEvent getAmbientSound() {
        return bestia().sonido("ambiente");
    }

    @Override
    protected @Nullable SoundEvent getHurtSound(DamageSource fuente) {
        return bestia().sonido("herido");
    }

    @Override
    protected @Nullable SoundEvent getDeathSound() {
        return bestia().sonido("muerte");
    }

    @Override
    protected void playStepSound(BlockPos pos, BlockState estado) {
        SoundEvent paso = bestia().sonido("paso");
        if (paso != null) {
            playSound(paso, 0.35F, 0.9F + random.nextFloat() * 0.2F);
        }
    }

    /** Suena uno de sus sonidos (si lo tiene), desde el. */
    public void sonar(String nombre, float volumen, float tono) {
        SoundEvent s = bestia().sonido(nombre);
        if (s != null) {
            playSound(s, volumen, tono);
        }
    }

    /** Lo mismo, con un poco de variacion en el tono. */
    public void sonar(String nombre, float volumen) {
        sonar(nombre, volumen, 0.92F + random.nextFloat() * 0.16F);
    }

    // ------------------------------------------------------------------
    //  Ayudas para las mecanicas
    // ------------------------------------------------------------------

    /** Si este es su objetivo y esta a su alcance para un golpe cuerpo a cuerpo. */
    protected boolean alAlcance(Entity objetivo, double extra) {
        double r = getBbWidth() * 0.5 + objetivo.getBbWidth() * 0.5 + extra;
        return distanceToSqr(objetivo) <= r * r + 1.0;
    }

    /**
     * Le pone un efecto sin las particulas de remolino de Minecraft: el efecto y su icono, si; lo que se ve alrededor
     * lo pone cada mob con las suyas. Los efectos de Atalaya (radiacion, enraizado, congelado...) llevan su particula,
     * que es nuestra, y esa si se ve.
     */
    public static void efecto(LivingEntity v, Holder<MobEffect> efecto, int ticks, int nivel, @Nullable Entity fuente) {
        Identifier id = BuiltInRegistries.MOB_EFFECT.getKey(efecto.value());
        boolean nuestro = id != null && Atalaya.MOD_ID.equals(id.getNamespace());
        v.addEffect(new MobEffectInstance(efecto, ticks, nivel, false, nuestro, true), fuente);
    }

    /** Su objetivo si sigue vivo y a tiro, o null. */
    protected @Nullable LivingEntity presa() {
        LivingEntity t = getTarget();
        return t != null && t.isAlive() && !t.isSpectator() ? t : null;
    }
}
