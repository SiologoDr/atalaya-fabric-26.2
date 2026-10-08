package com.atalaya.entity;

import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.util.Mth;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.storage.ValueInput;
import net.minecraft.world.level.storage.ValueOutput;
import net.minecraft.world.phys.Vec3;
import org.jspecify.annotations.Nullable;

/**
 * La Egida de la Sombra del Escudo (Novilis, octubre de 2026): un escudo
 * enorme, oscuro y con el canto de oro, que lleva en alto un tercio de los que
 * pelean mientras el sol de Novilis (SolCenitEntity) abrasa la arena.
 *
 * Si su portador mira al sol, el escudo le da sombra a el y a los que se ponen
 * detras: una franja en el suelo que sale del escudo hacia el lado contrario al
 * sol y se ensancha con la distancia. Cuanto mas de lado mira, mas estrecha (el
 * escudo se ve de canto); pasado un angulo, no da sombra.
 *
 * La entidad va a los pies de su portador (en el suelo, para que la sombra no
 * salte con el); el escudo y la sombra los dibuja EgidaNovilisRenderer con la
 * misma cuenta que usa el servidor (aLaSombra). No se guarda con el mundo.
 */
public class EgidaNovilisEntity extends Entity {

    /** La sombra: lo que mide de largo y su media anchura junto al escudo y al final (bloques). */
    public static final double LARGO = 10.0;
    public static final double ANCHO_CERCA = 1.4;
    public static final double ANCHO_LEJOS = 2.6;
    /** Lo que va el escudo por delante de su portador. */
    public static final double DELANTE = 0.9;
    /** De cara al sol a partir de aqui (coseno del angulo entre lo que mira y el sol: unos 70 grados). */
    public static final double MIN_CARA = 0.35;
    /** Lo que se perdona de alto entre el portador y los de su sombra. */
    private static final double ALTO_SOMBRA = 3.5;

    private static final EntityDataAccessor<Integer> DATA_PORTADOR =
            SynchedEntityData.defineId(EgidaNovilisEntity.class, EntityDataSerializers.INT);
    private static final EntityDataAccessor<Integer> DATA_SOL =
            SynchedEntityData.defineId(EgidaNovilisEntity.class, EntityDataSerializers.INT);
    private static final EntityDataAccessor<Integer> DATA_COLOR =
            SynchedEntityData.defineId(EgidaNovilisEntity.class, EntityDataSerializers.INT);

    public EgidaNovilisEntity(EntityType<? extends EgidaNovilisEntity> tipo, Level nivel) {
        super(tipo, nivel);
        this.noPhysics = true;
        setNoGravity(true);
    }

    public static EgidaNovilisEntity dar(ServerLevel nivel, LivingEntity v, SolCenitEntity sol, int color) {
        EgidaNovilisEntity e = new EgidaNovilisEntity(AtalayaEntities.EGIDA_NOVILIS, nivel);
        e.entityData.set(DATA_PORTADOR, v.getId());
        e.entityData.set(DATA_SOL, sol.getId());
        e.entityData.set(DATA_COLOR, color);
        e.setPos(v.getX(), v.getY(), v.getZ());
        nivel.addFreshEntity(e);
        return e;
    }

    @Override
    protected void defineSynchedData(SynchedEntityData.Builder datos) {
        datos.define(DATA_PORTADOR, -1);
        datos.define(DATA_SOL, -1);
        datos.define(DATA_COLOR, 2);
    }

    public int getIdPortador() {
        return entityData.get(DATA_PORTADOR);
    }

    public int getIdSol() {
        return entityData.get(DATA_SOL);
    }

    public int getColor() {
        return entityData.get(DATA_COLOR);
    }

    /** Quien la lleva (vivo y en este mundo), o null. */
    public @Nullable LivingEntity getPortador() {
        Entity e = level().getEntity(getIdPortador());
        return e instanceof LivingEntity v && v.isAlive() && !v.isRemoved() ? v : null;
    }

    /** Hacia donde mira, en horizontal, quien tiene este rumbo (grados, como getYRot). */
    public static Vec3 frente(float rumbo) {
        float b = rumbo * Mth.DEG_TO_RAD;
        return new Vec3(-Mth.sin(b), 0, Mth.cos(b));
    }

    /** Del portador al sol, en horizontal y de largo 1. */
    public static Vec3 haciaSol(Vec3 pies, Vec3 sol) {
        Vec3 d = new Vec3(sol.x - pies.x, 0, sol.z - pies.z);
        return d.lengthSqr() < 1.0E-6 ? new Vec3(1, 0, 0) : d.normalize();
    }

    /** Cuanto mira al sol (coseno del angulo, en horizontal): 1 de frente, 0 de lado. */
    public static double deCara(float rumbo, Vec3 pies, Vec3 sol) {
        return frente(rumbo).dot(haciaSol(pies, sol));
    }

    /**
     * Si p (unos pies) esta a la sombra del escudo de quien esta en pies
     * mirando a rumbo, con el sol en sol. La misma cuenta que dibuja la sombra.
     */
    public static boolean aLaSombra(Vec3 pies, float rumbo, Vec3 sol, Vec3 p) {
        double c = deCara(rumbo, pies, sol);
        if (c < MIN_CARA || Math.abs(p.y - pies.y) > ALTO_SOMBRA) {
            return false;
        }
        Vec3 s = haciaSol(pies, sol);
        Vec3 f = frente(rumbo);
        double ox = pies.x + f.x * DELANTE;
        double oz = pies.z + f.z * DELANTE;
        double rx = p.x - ox;
        double rz = p.z - oz;
        double largo = -(rx * s.x + rz * s.z);
        if (largo < -0.4 || largo > LARGO) {
            return false;
        }
        double lado = Math.abs(rx * -s.z + rz * s.x);
        double ancho = (ANCHO_CERCA + (ANCHO_LEJOS - ANCHO_CERCA) * Mth.clamp(largo / LARGO, 0.0, 1.0)) * c;
        // Se cuenta media anchura de jugador: con medio cuerpo dentro ya esta a la sombra.
        return lado <= ancho + 0.3;
    }

    @Override
    public void tick() {
        super.tick();
        if (level().isClientSide()) {
            return;
        }
        LivingEntity v = getPortador();
        Entity sol = level().getEntity(getIdSol());
        if (v == null || !(sol instanceof SolCenitEntity s) || s.getFin() >= 0
                || tickCount > SolCenitEntity.SUBE + SolCenitEntity.ABRASA + 60) {
            discard();
            return;
        }
        // En el suelo: si salta, la sombra se queda abajo.
        double y = v.onGround() || v.getY() < getY() ? v.getY() : getY();
        setPos(v.getX(), y, v.getZ());
    }

    @Override
    public boolean isPickable() {
        return false;
    }

    @Override
    public boolean shouldBeSaved() {
        return false;
    }

    @Override
    public boolean shouldRenderAtSqrDistance(double distancia) {
        return distancia < 128 * 128;
    }

    @Override
    public boolean hurtServer(ServerLevel nivel, DamageSource fuente, float cantidad) {
        return false;
    }

    @Override
    protected void readAdditionalSaveData(ValueInput entrada) {
    }

    @Override
    protected void addAdditionalSaveData(ValueOutput salida) {
    }
}
