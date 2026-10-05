package com.atalaya.entity;

import com.atalaya.particula.AtalayaParticulas;
import com.atalaya.sonido.AtalayaSonidos;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.storage.ValueInput;
import net.minecraft.world.level.storage.ValueOutput;
import net.minecraft.world.phys.Vec3;
import org.jspecify.annotations.Nullable;

/**
 * Un nucleo de viento del Juicio del Ciclon: aire comprimido en un cristal de
 * cielo que gira, flotando sobre el suelo, y alimenta el ciclon del marcado
 * (se ve la corriente de luz que va de uno a otro).
 *
 * Hay cuatro repartidos por la arena. Cada uno aguanta 6 golpes, y uno mas por
 * cada 4 jugadores; cualquier golpe cuenta (espada, flecha, tridente). Cada
 * nucleo roto quita 11 al golpe del Juicio; con los cuatro, el ciclon se
 * deshace y Aeralis cae aturdida.
 */
public class NucleoVientoEntity extends Entity {

    private static final EntityDataAccessor<Integer> DATA_GOLPES =
            SynchedEntityData.defineId(NucleoVientoEntity.class, EntityDataSerializers.INT);
    private static final EntityDataAccessor<Integer> DATA_AGUANTA =
            SynchedEntityData.defineId(NucleoVientoEntity.class, EntityDataSerializers.INT);

    /** Solo cliente: tick del ultimo golpe (para el destello). */
    public int ultimoGolpe = -100;
    private int golpesVistos;

    private @Nullable AeralisEntity duena;

    public NucleoVientoEntity(EntityType<? extends NucleoVientoEntity> tipo, Level nivel) {
        super(tipo, nivel);
        this.noPhysics = true;
    }

    public static NucleoVientoEntity crear(ServerLevel nivel, AeralisEntity duena, Vec3 donde, int aguanta) {
        NucleoVientoEntity n = new NucleoVientoEntity(AtalayaEntities.NUCLEO_VIENTO, nivel);
        n.duena = duena;
        n.entityData.set(DATA_AGUANTA, aguanta);
        n.setPos(donde.x, donde.y, donde.z);
        nivel.addFreshEntity(n);
        nivel.playSound(null, donde.x, donde.y, donde.z, AtalayaSonidos.AERALIS_NUCLEO, SoundSource.HOSTILE, 2.5F, 1.0F);
        nivel.sendParticles(AtalayaParticulas.AERALIS_JIRON, true, true, donde.x, donde.y, donde.z, 16, 0.6, 0.6, 0.6, 0.1);
        nivel.sendParticles(AtalayaParticulas.AERALIS_ONDA, true, true, donde.x, donde.y - 2.0, donde.z, 0, 0.6, 5.0, 0.0, 1.0);
        return n;
    }

    @Override
    protected void defineSynchedData(SynchedEntityData.Builder datos) {
        datos.define(DATA_GOLPES, 0);
        datos.define(DATA_AGUANTA, 6);
    }

    public int getGolpes() {
        return entityData.get(DATA_GOLPES);
    }

    public int getAguanta() {
        return entityData.get(DATA_AGUANTA);
    }

    @Override
    public void tick() {
        super.tick();
        if (level().isClientSide()) {
            particulasCliente();
            return;
        }
        if (duena == null || duena.isRemoved() || duena.getEstado() != AeralisEntity.JUICIO_SOSTIENE) {
            apagar();
            return;
        }
        if (tickCount % 48 == 0) {
            level().playSound(null, getX(), getY(), getZ(), AtalayaSonidos.AERALIS_NUCLEO, SoundSource.HOSTILE, 2.0F, 1.0F);
        }
    }

    private void particulasCliente() {
        if (getGolpes() != golpesVistos) {
            golpesVistos = getGolpes();
            ultimoGolpe = tickCount;
        }
        double a = tickCount * 0.35;
        for (int i = 0; i < 2; i++) {
            double b = a + i * Math.PI;
            level().addParticle(AtalayaParticulas.AERALIS_VIENTO, getX() + Math.cos(b) * 1.3, getY() + 0.8 + Math.sin(a * 0.7) * 0.4,
                    getZ() + Math.sin(b) * 1.3, -Math.sin(b) * 0.25, 0, Math.cos(b) * 0.25);
        }
        // La corriente que alimenta el ciclon: motas que vuelan hacia el.
        if (tickCount % 2 == 0) {
            for (Entity e : level().getEntities(this, getBoundingBox().inflate(72),
                    x -> x instanceof TornadoAeralisEntity t && t.isCiclon())) {
                Vec3 hacia = e.position().add(0, 5.0, 0).subtract(position());
                Vec3 v = hacia.normalize().scale(0.9);
                level().addParticle(AtalayaParticulas.AERALIS_LUZ, getX(), getY() + 0.8, getZ(), v.x, v.y, v.z);
                break;
            }
        }
    }

    /** Se queda sin el Juicio: se deshace sin mas. */
    public void apagar() {
        if (level() instanceof ServerLevel nivel && !isRemoved()) {
            nivel.sendParticles(AtalayaParticulas.AERALIS_JIRON, true, true, getX(), getY() + 0.8, getZ(), 8, 0.4, 0.4, 0.4, 0.05);
        }
        discard();
    }

    @Override
    public boolean isPickable() {
        return true;
    }

    @Override
    public boolean hurtServer(ServerLevel nivel, DamageSource fuente, float cantidad) {
        if (isRemoved() || fuente.getEntity() instanceof AeralisEntity) {
            return false;
        }
        int golpes = getGolpes() + 1;
        entityData.set(DATA_GOLPES, golpes);
        Vec3 c = position().add(0, 0.8, 0);
        nivel.playSound(null, c.x, c.y, c.z, AtalayaSonidos.AERALIS_NUCLEO_GOLPE, SoundSource.HOSTILE, 2.0F,
                0.8F + 0.6F * golpes / Math.max(1, getAguanta()));
        nivel.sendParticles(AtalayaParticulas.AERALIS_LUZ, true, true, c.x, c.y, c.z, 6, 0.3, 0.3, 0.3, 0.15);
        if (golpes >= getAguanta()) {
            nivel.playSound(null, c.x, c.y, c.z, AtalayaSonidos.AERALIS_NUCLEO_ROTO, SoundSource.HOSTILE, 4.0F, 1.0F);
            nivel.sendParticles(AtalayaParticulas.AERALIS_JIRON, true, true, c.x, c.y, c.z, 30, 0.8, 0.8, 0.8, 0.25);
            nivel.sendParticles(AtalayaParticulas.AERALIS_LUZ, true, true, c.x, c.y, c.z, 30, 0.6, 0.6, 0.6, 0.35);
            nivel.sendParticles(AtalayaParticulas.AERALIS_ONDA, true, true, c.x, c.y, c.z, 0, 1.2, 7.0, 0.0, 1.0);
            if (duena != null) {
                duena.alRomperNucleo(nivel, this);
            }
            discard();
        }
        return true;
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
    protected void readAdditionalSaveData(ValueInput entrada) {
    }

    @Override
    protected void addAdditionalSaveData(ValueOutput salida) {
    }
}
