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
import net.minecraft.world.entity.Pose;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.storage.ValueInput;
import net.minecraft.world.level.storage.ValueOutput;
import net.minecraft.world.phys.Vec3;
import org.jspecify.annotations.Nullable;

/**
 * Una columna de Glifos del Templo: zocalo y capitel de oro, fuste de sillares
 * de jade y, en sus cuatro caras, un glifo tallado que brilla (uno de los
 * ocho de MinijuegosRajang.NOMBRES_GLIFOS). Todas se ven iguales salvo el glifo: cual
 * es verdadero solo lo sabe el Vidente. Una verdadera se raja con cada golpe y
 * a los tres se rompe en oro; una falsa estalla al primero. Se pisa como el
 * suelo (ColisionGrande) y se hunde al acabar.
 */
public class GlifoTemploEntity extends Entity {

    public static final float ANCHO = 2.2F;
    public static final float ALTO = 4.6F;
    /** Lo que tarda en salir del suelo y en hundirse, y lo que dura el destrozo. */
    public static final int SUBE = 30;
    public static final int BAJA = 30;
    public static final int ROMPE = 16;
    /** Lo que hay que esperar entre golpe y golpe para que cuente otro (ticks). */
    private static final int ENTRE_GOLPES = 6;

    private static final EntityDataAccessor<Integer> DATA_GLIFO =
            SynchedEntityData.defineId(GlifoTemploEntity.class, EntityDataSerializers.INT);
    private static final EntityDataAccessor<Integer> DATA_GOLPES =
            SynchedEntityData.defineId(GlifoTemploEntity.class, EntityDataSerializers.INT);
    /** Tick en que se rompio (verdadera) o estallo (falsa); -1 si sigue entera. */
    private static final EntityDataAccessor<Integer> DATA_ROTA =
            SynchedEntityData.defineId(GlifoTemploEntity.class, EntityDataSerializers.INT);
    private static final EntityDataAccessor<Boolean> DATA_ESTALLO =
            SynchedEntityData.defineId(GlifoTemploEntity.class, EntityDataSerializers.BOOLEAN);
    /** Tick en que empezo a hundirse (-1: en pie). */
    private static final EntityDataAccessor<Integer> DATA_BAJA =
            SynchedEntityData.defineId(GlifoTemploEntity.class, EntityDataSerializers.INT);
    /** Tick del ultimo golpe (para que tiemble). */
    private static final EntityDataAccessor<Integer> DATA_GOLPEADA =
            SynchedEntityData.defineId(GlifoTemploEntity.class, EntityDataSerializers.INT);

    private @Nullable GlifosRajang juego;
    /** Solo en el servidor: si es de las buenas. */
    private boolean buena;
    private int ultimoGolpe = -100;

    public GlifoTemploEntity(EntityType<? extends GlifoTemploEntity> tipo, Level nivel) {
        super(tipo, nivel);
        this.noPhysics = true;
        setNoGravity(true);
    }

    static GlifoTemploEntity alzar(ServerLevel nivel, GlifosRajang juego, Vec3 donde, int glifo, boolean buena, float rumbo) {
        GlifoTemploEntity g = new GlifoTemploEntity(AtalayaEntities.GLIFO_TEMPLO, nivel);
        g.juego = juego;
        g.buena = buena;
        g.entityData.set(DATA_GLIFO, glifo);
        g.snapTo(donde.x, donde.y, donde.z, rumbo, 0.0F);
        nivel.addFreshEntity(g);
        nivel.sendParticles(AtalayaParticulas.RAJANG_POLVO, true, true, donde.x, donde.y + 0.3, donde.z, 20, 1.0, 0.2, 1.0, 0.04);
        return g;
    }

    @Override
    protected void defineSynchedData(SynchedEntityData.Builder datos) {
        datos.define(DATA_GLIFO, 0);
        datos.define(DATA_GOLPES, 0);
        datos.define(DATA_ROTA, -1);
        datos.define(DATA_ESTALLO, false);
        datos.define(DATA_BAJA, -1);
        datos.define(DATA_GOLPEADA, -100);
    }

    public int getGlifo() {
        return entityData.get(DATA_GLIFO);
    }

    public int getGolpes() {
        return entityData.get(DATA_GOLPES);
    }

    public int getRota() {
        return entityData.get(DATA_ROTA);
    }

    public boolean estallo() {
        return entityData.get(DATA_ESTALLO);
    }

    public int getBaja() {
        return entityData.get(DATA_BAJA);
    }

    public int getGolpeada() {
        return entityData.get(DATA_GOLPEADA);
    }

    /** Lo que ha salido del suelo (0 a 1): sube al nacer y baja al hundirse. */
    public float salida(float parcial) {
        float sube = Mth.clamp((tickCount + parcial) / SUBE, 0.0F, 1.0F);
        int baja = getBaja();
        if (baja >= 0) {
            sube = Math.min(sube, 1.0F - Mth.clamp((tickCount - baja + parcial) / BAJA, 0.0F, 1.0F));
        }
        return 1.0F - (1.0F - sube) * (1.0F - sube);
    }

    /** Entera y en pie (se puede golpear). */
    public boolean entera() {
        return getRota() < 0 && getBaja() < 0 && tickCount >= SUBE;
    }

    @Override
    public EntityDimensions getDimensions(Pose pose) {
        return EntityDimensions.fixed(ANCHO, ALTO);
    }

    @Override
    public boolean canBeCollidedWith(@Nullable Entity otro) {
        return !isRemoved() && getRota() < 0 && salida(0.0F) > 0.6F;
    }

    @Override
    public boolean canCollideWith(Entity otro) {
        return false;
    }

    @Override
    public boolean isPickable() {
        return !isRemoved() && entera();
    }

    @Override
    public boolean isPushable() {
        return false;
    }

    @Override
    public boolean hurtServer(ServerLevel nivel, DamageSource fuente, float cantidad) {
        if (!entera() || juego == null || tickCount - ultimoGolpe < ENTRE_GOLPES) {
            return false;
        }
        Entity quien = fuente.getEntity();
        if (!(quien instanceof Player)) {
            return false;
        }
        ultimoGolpe = tickCount;
        entityData.set(DATA_GOLPEADA, tickCount);
        juego.alGolpear(nivel, this, (Player) quien);
        return true;
    }

    boolean esBuena() {
        return buena;
    }

    /** Un golpe a una buena: se raja (y suena). Devuelve los que lleva. */
    int rajar(ServerLevel nivel) {
        int g = getGolpes() + 1;
        entityData.set(DATA_GOLPES, g);
        Vec3 p = position().add(0, ALTO * 0.55, 0);
        nivel.sendParticles(AtalayaParticulas.RAJANG_JADE, true, true, p.x, p.y, p.z, 10, 0.6, 0.6, 0.6, 0.12);
        nivel.playSound(null, p.x, p.y, p.z, AtalayaSonidos.RAJANG_GLIFO_GOLPE, SoundSource.HOSTILE, 2.0F, 0.9F + 0.1F * g);
        return g;
    }

    /** La buena se rompe: el glifo revienta en oro y la columna se viene abajo. */
    void romper(ServerLevel nivel) {
        entityData.set(DATA_ROTA, tickCount);
        Vec3 p = position().add(0, ALTO * 0.55, 0);
        nivel.sendParticles(AtalayaParticulas.RAJANG_ORO, true, true, p.x, p.y, p.z, 50, 0.8, 1.2, 0.8, 0.25);
        nivel.sendParticles(AtalayaParticulas.RAJANG_ROCA, true, true, p.x, p.y, p.z, 30, 0.8, 1.4, 0.8, 0.3);
        nivel.sendParticles(AtalayaParticulas.RAJANG_POLVO, true, true, p.x, getY() + 0.5, p.z, 30, 1.4, 0.4, 1.4, 0.05);
        nivel.playSound(null, p.x, p.y, p.z, AtalayaSonidos.RAJANG_GLIFO_ROMPE, SoundSource.HOSTILE, 4.0F, 1.0F);
    }

    /** La falsa estalla. */
    void estallar(ServerLevel nivel) {
        entityData.set(DATA_ESTALLO, true);
        entityData.set(DATA_ROTA, tickCount);
        Vec3 p = position().add(0, ALTO * 0.5, 0);
        nivel.sendParticles(AtalayaParticulas.RAJANG_CHISPA, true, true, p.x, p.y, p.z, 60, 1.0, 1.4, 1.0, 0.35);
        nivel.sendParticles(AtalayaParticulas.RAJANG_ROCA, true, true, p.x, p.y, p.z, 40, 1.0, 1.6, 1.0, 0.45);
        nivel.sendParticles(AtalayaParticulas.RAJANG_ONDA, true, true, getX(), getY() + 0.1, getZ(), 0, 1.6, 7.0, 0.0, 1.0);
        nivel.playSound(null, p.x, p.y, p.z, AtalayaSonidos.RAJANG_GLIFO_FALSO, SoundSource.HOSTILE, 4.0F, 1.0F);
    }

    /** Se acabo: se hunde en el suelo. */
    void hundir(ServerLevel nivel) {
        if (getBaja() < 0) {
            entityData.set(DATA_BAJA, tickCount);
            if (getRota() < 0) {
                nivel.sendParticles(AtalayaParticulas.RAJANG_POLVO, true, true, getX(), getY() + 0.3, getZ(), 16, 1.0, 0.2, 1.0, 0.03);
            }
        }
    }

    @Override
    public void tick() {
        super.tick();
        ColisionGrande.apuntar(this);
        if (level().isClientSide()) {
            if (entera() && random.nextInt(6) == 0) {
                // Unas motas de luz que suben del glifo (igual en todas: no delatan).
                double a = random.nextDouble() * Math.PI * 2;
                level().addParticle(AtalayaParticulas.RAJANG_CHISPA, getX() + Math.cos(a) * 1.0, getY() + 2.0 + random.nextDouble(),
                        getZ() + Math.sin(a) * 1.0, 0, 0.03, 0);
            }
            return;
        }
        int rota = getRota();
        if (juego == null || (rota >= 0 && tickCount - rota > ROMPE + 4) || (getBaja() >= 0 && tickCount - getBaja() > BAJA + 2)) {
            discard();
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
