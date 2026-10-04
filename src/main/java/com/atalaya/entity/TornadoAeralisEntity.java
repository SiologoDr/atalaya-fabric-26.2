package com.atalaya.entity;

import com.atalaya.particula.AtalayaParticulas;
import com.atalaya.sonido.AtalayaSonidos;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.Mth;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityDimensions;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Pose;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.storage.ValueInput;
import net.minecraft.world.level.storage.ValueOutput;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;
import org.jspecify.annotations.Nullable;

import java.util.ArrayList;
import java.util.List;

/**
 * Un tornado de Aeralis. Dos tamanos:
 *
 * <ul>
 *   <li><b>Tornado</b> (el ataque Tornados): nace donde el polvo empieza a
 *   girar (un segundo de aviso) y vaga por la arena 12 s hacia el ser vivo mas
 *   cercano. Si te pilla, subes poco a poco dando vueltas, sin control, y
 *   pierdes 7 de vida por segundo (ni la armadura lo para); a los 3 s revienta
 *   y te lanza por los aires (13 de dano +9 por fase, mas la caida). Un
 *   companero te saca rompiendolo con 3 golpes (flechas, tridentes o a
 *   espadazos): te deja en el suelo con suavidad.</li>
 *   <li><b>Ciclon</b> (el Juicio): gigante, alrededor del marcado. Lo levanta
 *   despacio y aparta a los demas. No se rompe a golpes: lo debilitan los
 *   cuatro nucleos de viento.</li>
 * </ul>
 */
public class TornadoAeralisEntity extends Entity {

    /** Ticks del aviso: el polvo gira donde va a nacer. */
    public static final int NACER = 20;
    private static final int VIDA = 240;
    private static final int ATRAPA = 60;
    private static final int GOLPES = 3;
    private static final double RADIO = 1.9;
    /** Cuanto mas grande dibuja (y mide) el ciclon del Juicio. */
    public static final float ESCALA_CICLON = 3.0F;

    private static final EntityDataAccessor<Boolean> DATA_CICLON =
            SynchedEntityData.defineId(TornadoAeralisEntity.class, EntityDataSerializers.BOOLEAN);
    /** Lo fuerte que gira (1 entero; el ciclon pierde con cada nucleo roto). */
    private static final EntityDataAccessor<Float> DATA_FUERZA =
            SynchedEntityData.defineId(TornadoAeralisEntity.class, EntityDataSerializers.FLOAT);
    /** Se esta deshaciendo: el cliente lo desvanece. */
    private static final EntityDataAccessor<Boolean> DATA_DESHACE =
            SynchedEntityData.defineId(TornadoAeralisEntity.class, EntityDataSerializers.BOOLEAN);

    /** Solo cliente: tick en que empezo a deshacerse. */
    public int inicioDeshacer = -1;

    private @Nullable AeralisEntity duena;
    private int fase = 1;
    private int vida = VIDA;
    private int golpes;
    private int inicioAtrapa = -1;
    private int deshaciendo;
    private float rumbo;
    private final List<LivingEntity> atrapados = new ArrayList<>();
    /** Los que solto con suavidad: no se hacen dano al caer mientras se deshace. */
    private final List<LivingEntity> liberados = new ArrayList<>();
    private @Nullable LivingEntity marcado;

    public TornadoAeralisEntity(EntityType<? extends TornadoAeralisEntity> tipo, Level nivel) {
        super(tipo, nivel);
        this.noPhysics = true;
    }

    public static TornadoAeralisEntity nacer(ServerLevel nivel, AeralisEntity duena, Vec3 donde, int fase) {
        TornadoAeralisEntity t = new TornadoAeralisEntity(AtalayaEntities.TORNADO_AERALIS, nivel);
        t.duena = duena;
        t.fase = fase;
        t.rumbo = nivel.getRandom().nextFloat() * Mth.TWO_PI;
        t.setPos(donde.x, donde.y, donde.z);
        nivel.addFreshEntity(t);
        nivel.playSound(null, donde.x, donde.y, donde.z, AtalayaSonidos.AERALIS_TORNADO_NACE, SoundSource.HOSTILE, 2.5F,
                0.9F + nivel.getRandom().nextFloat() * 0.2F);
        return t;
    }

    /** El ciclon del Juicio, alrededor del marcado. */
    public static TornadoAeralisEntity ciclon(ServerLevel nivel, AeralisEntity duena, LivingEntity marcado) {
        TornadoAeralisEntity t = new TornadoAeralisEntity(AtalayaEntities.TORNADO_AERALIS, nivel);
        t.duena = duena;
        t.fase = duena.fase();
        t.marcado = marcado;
        t.vida = Integer.MAX_VALUE;
        double y = AeralisEntity.sueloBajo(nivel, marcado.getX(), marcado.getY(), marcado.getZ());
        t.setPos(marcado.getX(), y, marcado.getZ());
        t.entityData.set(DATA_CICLON, true);
        t.refreshDimensions();
        nivel.addFreshEntity(t);
        t.atrapar(marcado);
        return t;
    }

    @Override
    protected void defineSynchedData(SynchedEntityData.Builder datos) {
        datos.define(DATA_CICLON, false);
        datos.define(DATA_FUERZA, 1.0F);
        datos.define(DATA_DESHACE, false);
    }

    public boolean isCiclon() {
        return entityData.get(DATA_CICLON);
    }

    public float getFuerza() {
        return entityData.get(DATA_FUERZA);
    }

    public boolean isDeshaciendose() {
        return entityData.get(DATA_DESHACE);
    }

    @Override
    public void onSyncedDataUpdated(EntityDataAccessor<?> dato) {
        super.onSyncedDataUpdated(dato);
        if (DATA_CICLON.equals(dato)) {
            refreshDimensions();
        }
        if (DATA_DESHACE.equals(dato) && isDeshaciendose() && inicioDeshacer < 0) {
            inicioDeshacer = tickCount;
        }
    }

    @Override
    public EntityDimensions getDimensions(Pose pose) {
        return isCiclon() ? super.getDimensions(pose).scale(ESCALA_CICLON) : super.getDimensions(pose);
    }

    @Override
    public void tick() {
        super.tick();
        if (level().isClientSide()) {
            particulasCliente();
            return;
        }
        ServerLevel nivel = (ServerLevel) level();
        if (duena == null || duena.isRemoved()) {
            soltar(true);
            discard();
            return;
        }
        if (deshaciendo > 0) {
            for (LivingEntity v : liberados) {
                v.resetFallDistance();
            }
            // El ciclon aguanta mas: el marcado cae desde muy alto y llega al suelo sin hacerse dano.
            if (++deshaciendo > (isCiclon() ? 110 : 50)) {
                discard();
            }
            return;
        }
        if (tickCount < NACER) {
            return;
        }
        if (tickCount == NACER || (!isCiclon() && tickCount % 60 == 0)) {
            nivel.playSound(null, getX(), getY(), getZ(), AtalayaSonidos.AERALIS_TORNADO, SoundSource.HOSTILE,
                    isCiclon() ? 4.0F : 2.5F, 0.9F + random.nextFloat() * 0.2F);
        }
        if (--vida <= 0 && atrapados.isEmpty()) {
            deshacer(false);
            return;
        }
        mover(nivel);
        if (isCiclon()) {
            tickCiclon(nivel);
        } else {
            tickTornado(nivel);
        }
    }

    /** Vaga hacia el ser vivo mas cercano, haciendo eses, pegado al suelo. */
    private void mover(ServerLevel nivel) {
        double vel = 0;
        if (!isCiclon()) {
            LivingEntity cerca = null;
            double mejor = 28 * 28;
            for (LivingEntity v : nivel.getEntitiesOfClass(LivingEntity.class, getBoundingBox().inflate(28), duena::esPresa)) {
                double d = v.distanceToSqr(this);
                if (d < mejor && !atrapados.contains(v)) {
                    mejor = d;
                    cerca = v;
                }
            }
            if (cerca != null) {
                float hacia = (float) Mth.atan2(cerca.getZ() - getZ(), cerca.getX() - getX());
                rumbo += Mth.clamp(Mth.wrapDegrees((hacia - rumbo) * Mth.RAD_TO_DEG), -6.0F, 6.0F) * Mth.DEG_TO_RAD;
            } else {
                rumbo += (random.nextFloat() - 0.5F) * 0.3F;
            }
            vel = (0.11 + 0.02 * (fase - 1)) * (atrapados.isEmpty() ? 1.0 : 0.5);
        }
        double eses = Mth.sin(tickCount * 0.15F) * 0.35;
        double x = getX() + Math.cos(rumbo + eses) * vel;
        double z = getZ() + Math.sin(rumbo + eses) * vel;
        if (duena.getCentro() != null) {
            Vec3 c = Vec3.atBottomCenterOf(duena.getCentro());
            Vec3 rel = new Vec3(x - c.x, 0, z - c.z);
            if (rel.length() > 52) {
                rel = rel.normalize().scale(52);
                x = c.x + rel.x;
                z = c.z + rel.z;
                rumbo += Mth.PI;
            }
        }
        double suelo = AeralisEntity.sueloBajo(nivel, x, getY() + 1.0, z);
        setPos(x, getY() + Mth.clamp(suelo - getY(), -0.6, 0.6), z);
    }

    private void tickTornado(ServerLevel nivel) {
        // Atrapa a lo que entre en el embudo (hasta tres a la vez).
        if (atrapados.size() < 3) {
            for (LivingEntity v : nivel.getEntitiesOfClass(LivingEntity.class, getBoundingBox().inflate(0.5), duena::esPresa)) {
                double dy = v.getY() - getY();
                if (AeralisEntity.horizontal(position(), v.position()) <= RADIO + v.getBbWidth() / 2 && dy > -1.0
                        && dy < 6.0 && !atrapados.contains(v) && atrapados.size() < 3) {
                    atrapar(v);
                }
            }
        }
        if (atrapados.isEmpty()) {
            return;
        }
        int dentro = tickCount - inicioAtrapa;
        DamageSource fuente = AeralisDanos.fuente((ServerLevel) level(), AeralisDanos.TORNADO, this, duena);
        for (int i = 0; i < atrapados.size(); i++) {
            LivingEntity v = atrapados.get(i);
            if (!v.isAlive() || v.isRemoved()) {
                continue;
            }
            float k = Mth.clamp(dentro / (float) ATRAPA, 0.0F, 1.0F);
            girar(v, i, 0.5 + 5.0 * k, 1.1);
            if (dentro > 0 && dentro % 20 == 0) {
                v.hurtServer(nivel, fuente, AeralisEntity.DANO_TORNADO);
            }
        }
        atrapados.removeIf(v -> !v.isAlive() || v.isRemoved());
        if (dentro >= ATRAPA) {
            explotar(nivel);
        }
    }

    private void tickCiclon(ServerLevel nivel) {
        float fuerza = getFuerza();
        // El marcado sube despacio en el centro, dando vueltas.
        if (marcado != null && marcado.isAlive() && !marcado.isRemoved()) {
            int dentro = tickCount - inicioAtrapa;
            float k = Mth.clamp(dentro / 200.0F, 0.0F, 1.0F);
            girar(marcado, 0, 1.0 + 9.0 * k * (0.5F + 0.5F * fuerza), 0.7);
        }
        // Y aparta a los demas: un muro de viento que empuja hacia fuera.
        double radio = 6.5 * fuerza;
        for (LivingEntity v : nivel.getEntitiesOfClass(LivingEntity.class, getBoundingBox().inflate(2), duena::esPresa)) {
            if (v == marcado) {
                continue;
            }
            double d = AeralisEntity.horizontal(position(), v.position());
            if (d < radio && v.getY() - getY() < 16) {
                Vec3 fuera = AeralisEntity.horizontalHacia(position(), v.position());
                Vec3 giro = new Vec3(-fuera.z, 0, fuera.x);
                v.setDeltaMovement(fuera.x * 0.7 + giro.x * 0.3, 0.25, fuera.z * 0.7 + giro.z * 0.3);
                v.hurtMarked = true;
            }
        }
    }

    /** Lleva a v en espiral alrededor del eje, a la altura dada. */
    private void girar(LivingEntity v, int i, double altura, double radio) {
        double a = tickCount * 0.45 + i * (Math.PI * 2 / 3);
        Vec3 destino = new Vec3(getX() + Math.cos(a) * radio, getY() + altura, getZ() + Math.sin(a) * radio);
        Vec3 vel = destino.subtract(v.position()).scale(0.4);
        if (vel.length() > 1.2) {
            vel = vel.normalize().scale(1.2);
        }
        v.setDeltaMovement(vel);
        v.hurtMarked = true;
        v.resetFallDistance();
    }

    private void atrapar(LivingEntity v) {
        if (atrapados.isEmpty()) {
            inicioAtrapa = tickCount;
        }
        atrapados.add(v);
        level().playSound(null, v.getX(), v.getY(), v.getZ(), AtalayaSonidos.AERALIS_TORNADO_ATRAPA, SoundSource.HOSTILE,
                2.0F, 1.0F);
    }

    /** Revienta: lanza a los que tenia por los aires. */
    private void explotar(ServerLevel nivel) {
        Vec3 c = position().add(0, 3.0, 0);
        nivel.playSound(null, c.x, c.y, c.z, AtalayaSonidos.AERALIS_TORNADO_EXPLOTA, SoundSource.HOSTILE, 3.0F, 1.0F);
        nivel.sendParticles(AtalayaParticulas.AERALIS_ONDA, true, true, getX(), getY() + 0.1, getZ(), 0, 1.6, 8.0, 0.0, 1.0);
        nivel.sendParticles(AtalayaParticulas.AERALIS_JIRON, true, true, c.x, c.y, c.z, 30, 1.2, 2.5, 1.2, 0.2);
        nivel.sendParticles(AtalayaParticulas.AERALIS_POLVO, true, true, getX(), getY() + 0.5, getZ(), 20, 1.5, 0.4, 1.5, 0.08);
        DamageSource fuente = AeralisDanos.fuente(nivel, AeralisDanos.ESTALLIDO, this, duena);
        float dano = duena.dano(AeralisEntity.DANO_ESTALLIDO);
        for (LivingEntity v : atrapados) {
            if (!v.isAlive()) {
                continue;
            }
            v.hurtServer(nivel, fuente, AeralisEntity.contraArmadura(v, dano));
            Vec3 fuera = AeralisEntity.horizontalHacia(position(), v.position());
            v.setDeltaMovement(fuera.x * 1.0, 1.4, fuera.z * 1.0);
            v.hurtMarked = true;
        }
        atrapados.clear();
        discard();
    }

    /** Lo rompen o se le acaba el tiempo: se deshace y deja a los suyos en el suelo con suavidad. */
    public void deshacer(boolean roto) {
        if (deshaciendo > 0 || isRemoved()) {
            return;
        }
        if (roto) {
            level().playSound(null, getX(), getY(), getZ(), AtalayaSonidos.AERALIS_TORNADO_ROMPE, SoundSource.HOSTILE,
                    isCiclon() ? 5.0F : 2.5F, 1.0F);
        }
        if (level() instanceof ServerLevel nivel) {
            nivel.sendParticles(AtalayaParticulas.AERALIS_JIRON, true, true, getX(), getY() + 3.0, getZ(), isCiclon() ? 50 : 16,
                    1.2, 2.5, 1.2, 0.08);
        }
        soltar(false);
        deshaciendo = 1;
        entityData.set(DATA_DESHACE, true);
    }

    private void soltar(boolean deGolpe) {
        for (LivingEntity v : atrapados) {
            if (!deGolpe) {
                v.setDeltaMovement(0, 0.05, 0);
                v.hurtMarked = true;
                v.resetFallDistance();
                liberados.add(v);
            }
        }
        atrapados.clear();
        marcado = null;
    }

    /** Juicio: tira al marcado hacia el cielo justo antes del golpe. */
    public void lanzarAlCielo() {
        if (marcado != null && marcado.isAlive()) {
            marcado.setDeltaMovement(0, 1.6, 0);
            marcado.hurtMarked = true;
        }
        LivingEntity m = marcado;
        atrapados.clear();
        marcado = null;
        if (m != null) {
            liberados.add(m);
        }
        deshaciendo = 1;
        entityData.set(DATA_DESHACE, true);
    }

    /** Juicio: cada nucleo roto le quita fuerza. */
    public void debilitar(int rotos) {
        entityData.set(DATA_FUERZA, Math.max(0.25F, 1.0F - 0.2F * rotos));
        level().playSound(null, getX(), getY() + 4, getZ(), AtalayaSonidos.AERALIS_TORNADO_ROMPE, SoundSource.HOSTILE,
                3.0F, 1.2F);
    }

    // ------------------------------------------------------------------
    //  Golpes: tres lo rompen (el ciclon no se rompe asi)
    // ------------------------------------------------------------------

    @Override
    public boolean isPickable() {
        return !isCiclon() && !isDeshaciendose() && tickCount >= NACER;
    }

    @Override
    public boolean hurtServer(ServerLevel nivel, DamageSource fuente, float cantidad) {
        if (isRemoved() || deshaciendo > 0 || isCiclon() || tickCount < NACER
                || fuente.getEntity() instanceof AeralisEntity) {
            return false;
        }
        golpes++;
        nivel.sendParticles(AtalayaParticulas.AERALIS_JIRON, true, true, getX(), getY() + 2.0, getZ(), 6, 0.6, 1.2, 0.6, 0.12);
        nivel.playSound(null, getX(), getY() + 2, getZ(), AtalayaSonidos.AERALIS_INMUNE, SoundSource.HOSTILE, 1.5F,
                0.8F + 0.2F * golpes);
        if (golpes >= GOLPES) {
            deshacer(true);
        }
        return true;
    }

    // ------------------------------------------------------------------
    //  Cliente: el polvo de la base y lo que sube por el embudo
    // ------------------------------------------------------------------

    private void particulasCliente() {
        boolean ciclon = isCiclon();
        if (isDeshaciendose()) {
            return;
        }
        float esc = ciclon ? ESCALA_CICLON * getFuerza() : 1.0F;
        if (tickCount < NACER) {
            // El aviso: el polvo empieza a girar donde va a nacer.
            if (tickCount % 2 == 0) {
                level().addParticle(AtalayaParticulas.AERALIS_REMOLINO, getX(), getY() + 0.1, getZ(), 0, 0, 0);
            }
            double a = random.nextDouble() * Math.PI * 2;
            level().addParticle(AtalayaParticulas.AERALIS_POLVO, getX() + Math.cos(a) * 1.4, getY() + 0.2,
                    getZ() + Math.sin(a) * 1.4, -Math.sin(a) * 0.15, 0.03, Math.cos(a) * 0.15);
            return;
        }
        int n = ciclon ? 5 : 2;
        for (int i = 0; i < n; i++) {
            double a = random.nextDouble() * Math.PI * 2;
            double r = (0.8 + random.nextDouble() * 0.8) * esc;
            level().addParticle(AtalayaParticulas.AERALIS_POLVO, getX() + Math.cos(a) * r, getY() + 0.2,
                    getZ() + Math.sin(a) * r, -Math.sin(a) * 0.25 * esc, 0.05, Math.cos(a) * 0.25 * esc);
        }
        if (tickCount % 3 == 0) {
            level().addParticle(AtalayaParticulas.AERALIS_REMOLINO, getX(), getY() + 0.1, getZ(), esc, 0, 0);
        }
        if (random.nextInt(ciclon ? 1 : 3) == 0) {
            double h = random.nextDouble() * 7.0 * esc;
            double a = random.nextDouble() * Math.PI * 2;
            double r = (0.6 + h * 0.3) * (ciclon ? 1.0 : 1.0);
            level().addParticle(AtalayaParticulas.AERALIS_JIRON, getX() + Math.cos(a) * r, getY() + h,
                    getZ() + Math.sin(a) * r, -Math.sin(a) * 0.3, 0.08, Math.cos(a) * 0.3);
        }
    }

    @Override
    public boolean shouldBeSaved() {
        return false;
    }

    @Override
    public boolean shouldRenderAtSqrDistance(double distancia) {
        return distancia < 160 * 160;
    }

    @Override
    protected void readAdditionalSaveData(ValueInput entrada) {
    }

    @Override
    protected void addAdditionalSaveData(ValueOutput salida) {
    }
}
