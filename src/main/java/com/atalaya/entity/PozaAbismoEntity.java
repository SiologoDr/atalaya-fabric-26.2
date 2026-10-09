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
 * Una poza del abismo de la Pesca del Abismo (Nerea, octubre de 2026): un
 * circulo de agua negra en el suelo, con el borde de espuma cian, donde se
 * pescan las Perlas del Abismo con la cana (CorchoAbismoEntity). Se cierra al
 * acabar la pesca; si se acaba sin perlas, revienta en un geiser.
 */
public class PozaAbismoEntity extends Entity {

    /** El radio de la poza (bloques): donde tiene que caer el corcho. */
    public static final float RADIO = 1.8F;
    /** Lo que tarda en abrirse y en cerrarse (ticks). */
    public static final int ABRE = 12;

    private static final EntityDataAccessor<Integer> DATA_CIERRA =
            SynchedEntityData.defineId(PozaAbismoEntity.class, EntityDataSerializers.INT);

    private @Nullable NereaEntity duena;

    public PozaAbismoEntity(EntityType<? extends PozaAbismoEntity> tipo, Level nivel) {
        super(tipo, nivel);
        this.noPhysics = true;
        setNoGravity(true);
    }

    static PozaAbismoEntity abrir(ServerLevel nivel, NereaEntity duena, Vec3 donde) {
        PozaAbismoEntity p = new PozaAbismoEntity(AtalayaEntities.POZA_ABISMO, nivel);
        p.duena = duena;
        p.setPos(donde.x, donde.y, donde.z);
        nivel.addFreshEntity(p);
        return p;
    }

    @Override
    protected void defineSynchedData(SynchedEntityData.Builder datos) {
        datos.define(DATA_CIERRA, -1);
    }

    /** El tick en que empezo a cerrarse (-1 si sigue abierta). */
    public int getCierra() {
        return entityData.get(DATA_CIERRA);
    }

    void cerrar() {
        if (getCierra() < 0) {
            entityData.set(DATA_CIERRA, tickCount);
        }
    }

    /** Si un punto (un corcho) cae dentro de la poza. */
    public boolean dentro(Vec3 p) {
        double dx = p.x - getX();
        double dz = p.z - getZ();
        return dx * dx + dz * dz <= (RADIO + 0.3) * (RADIO + 0.3) && Math.abs(p.y - getY()) < 1.6;
    }

    @Override
    public void tick() {
        super.tick();
        if (level().isClientSide()) {
            if (getCierra() < 0 && random.nextInt(4) == 0) {
                double a = random.nextDouble() * Math.PI * 2;
                double r = random.nextDouble() * RADIO * 0.8;
                level().addParticle(AtalayaParticulas.NEREA_BURBUJA, getX() + Math.cos(a) * r, getY() + 0.1,
                        getZ() + Math.sin(a) * r, 0, 0.06, 0);
            }
            return;
        }
        if (duena == null || duena.isRemoved() || (getCierra() >= 0 && tickCount - getCierra() > ABRE)) {
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
