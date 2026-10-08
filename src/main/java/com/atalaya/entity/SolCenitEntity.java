package com.atalaya.entity;

import com.atalaya.particula.AtalayaParticulas;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.storage.ValueInput;
import net.minecraft.world.level.storage.ValueOutput;
import net.minecraft.world.phys.Vec3;
import org.jspecify.annotations.Nullable;

/**
 * El sol de la Sombra del Escudo (Novilis, octubre de 2026): Novilis lo lanza
 * desde su espalda, sube al cielo, bajo y enorme, y lo cruza despacio mientras
 * abrasa la arena. Solo se salva quien esta a la sombra de una Egida
 * (EgidaNovilisEntity).
 *
 * La entidad ES el sol: Novilis la mueve cada tick (sitio), asi que su
 * posicion es la del sol para todo, la sombra y las ordenes de prueba
 * ("facing entity"). Al acabar, se apaga (si nadie se quemo: humo y gris) o se
 * desvanece, y se va sola. No se guarda con el mundo.
 */
public class SolCenitEntity extends Entity {

    /** Lo que tarda en subir de su espalda al cielo (ticks): sin dano, para ponerse a la sombra. */
    public static final int SUBE = 40;
    /** Lo que abrasa (ticks): 12 s. */
    public static final int ABRASA = 240;
    /** Lo que tarda en irse al acabar. */
    public static final int APAGA = 30;
    /** A que distancia del centro del altar cruza el cielo, a que altura y cuanto gira (radianes). */
    private static final double RADIO = 40.0;
    private static final double ALTO = 16.0;
    private static final double GIRO = Math.toRadians(150.0);

    private static final EntityDataAccessor<Integer> DATA_FIN =
            SynchedEntityData.defineId(SolCenitEntity.class, EntityDataSerializers.INT);
    private static final EntityDataAccessor<Boolean> DATA_EXITO =
            SynchedEntityData.defineId(SolCenitEntity.class, EntityDataSerializers.BOOLEAN);
    private static final EntityDataAccessor<Integer> DATA_COLOR =
            SynchedEntityData.defineId(SolCenitEntity.class, EntityDataSerializers.INT);

    private @Nullable NovilisEntity dueno;
    private Vec3 desde = Vec3.ZERO;
    private Vec3 centro = Vec3.ZERO;
    private double rumbo0;
    private int sentido = 1;

    public SolCenitEntity(EntityType<? extends SolCenitEntity> tipo, Level nivel) {
        super(tipo, nivel);
        this.noPhysics = true;
        setNoGravity(true);
    }

    /** Lo lanza desde su espalda: cruzara el cielo alrededor de centro (el suelo del altar). */
    public static SolCenitEntity lanzar(ServerLevel nivel, NovilisEntity dueno, Vec3 desde, Vec3 centro, int color) {
        SolCenitEntity s = new SolCenitEntity(AtalayaEntities.SOL_CENIT, nivel);
        s.dueno = dueno;
        s.desde = desde;
        s.centro = centro;
        // Sale por el lado del altar donde esta Novilis, de lado, para que el sol barra la arena.
        double haciaEl = Math.atan2(desde.z - centro.z, desde.x - centro.x);
        s.sentido = nivel.getRandom().nextBoolean() ? 1 : -1;
        s.rumbo0 = haciaEl - s.sentido * GIRO * 0.5 + (nivel.getRandom().nextDouble() - 0.5) * 0.6;
        s.entityData.set(DATA_COLOR, color);
        s.setPos(desde.x, desde.y, desde.z);
        nivel.addFreshEntity(s);
        return s;
    }

    @Override
    protected void defineSynchedData(SynchedEntityData.Builder datos) {
        datos.define(DATA_FIN, -1);
        datos.define(DATA_EXITO, false);
        datos.define(DATA_COLOR, 2);
    }

    /** El tick en que acabo (-1 si sigue abrasando). */
    public int getFin() {
        return entityData.get(DATA_FIN);
    }

    /** Si acabo apagado (nadie se quemo). */
    public boolean isExito() {
        return entityData.get(DATA_EXITO);
    }

    public int getColor() {
        return entityData.get(DATA_COLOR);
    }

    /** Si ya esta arriba abrasando. */
    public boolean abrasando() {
        return getFin() < 0 && tickCount >= SUBE;
    }

    /** Donde va el sol a los e ticks de lanzarlo: sube en arco de su espalda y luego cruza el cielo. */
    private Vec3 sitio(int e) {
        Vec3 arriba = cielo(0);
        if (e < SUBE) {
            double k = (double) e / SUBE;
            double suave = k * k * (3 - 2 * k);
            Vec3 recta = desde.lerp(arriba, suave);
            return recta.add(0, 10.0 * 4 * k * (1 - k), 0);
        }
        return cielo(Math.min(ABRASA, e - SUBE));
    }

    private Vec3 cielo(int k) {
        double a = rumbo0 + sentido * GIRO * k / ABRASA;
        return new Vec3(centro.x + Math.cos(a) * RADIO, centro.y + ALTO, centro.z + Math.sin(a) * RADIO);
    }

    /** Se acaba: apagado (exito) o desvanecido. */
    public void acabar(boolean exito) {
        if (getFin() >= 0) {
            return;
        }
        entityData.set(DATA_EXITO, exito);
        entityData.set(DATA_FIN, tickCount);
        if (exito && level() instanceof ServerLevel nivel) {
            nivel.sendParticles(AtalayaParticulas.NOVILIS_HUMO, true, true, getX(), getY(), getZ(), 60, 3.0, 3.0, 3.0, 0.05);
            nivel.sendParticles(AtalayaParticulas.NOVILIS_CHISPA, true, true, getX(), getY(), getZ(), 40, 3.0, 3.0, 3.0, 0.3);
        }
    }

    @Override
    public void tick() {
        super.tick();
        if (level().isClientSide()) {
            if (getFin() < 0 && tickCount % 2 == 0) {
                // Brasas que se le desprenden y caen despacio.
                level().addParticle(AtalayaParticulas.NOVILIS_BRASA, getX() + (random.nextDouble() - 0.5) * 6.0,
                        getY() - 2.0 - random.nextDouble() * 2.0, getZ() + (random.nextDouble() - 0.5) * 6.0, 0, -0.05, 0);
            }
            return;
        }
        if (dueno == null || dueno.isRemoved() || dueno.isDeadOrDying()) {
            acabar(false);
        }
        int fin = getFin();
        if (fin < 0) {
            Vec3 p = sitio(tickCount);
            setPos(p.x, p.y, p.z);
        } else if (tickCount - fin >= APAGA) {
            discard();
        }
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
        return distancia < 256 * 256;
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
