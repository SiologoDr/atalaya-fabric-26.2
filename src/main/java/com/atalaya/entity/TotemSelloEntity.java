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
 * Un totem del Sello de la Tierra: una columna de piedra verde en tres tramos,
 * cada cara con su glifo (el numero maya, el ojo, la espiral, la mascara del
 * jaguar) que brilla mientras alimenta el sello. Esta en lo alto de una
 * plataforma de tierra: hay que subir saltando por las piedras y romperlo.
 *
 * Aguanta 10 golpes, sean cuantos sean los jugadores; cualquier golpe cuenta
 * (espada, flecha, tridente). Roto, se le apagan los glifos y se parte en dos.
 * Roto, se queda roto hasta que acaba el Sello: hay que romper los cuatro
 * antes de que se acabe el tiempo.
 */
public class TotemSelloEntity extends Entity {

    private static final EntityDataAccessor<Integer> DATA_GOLPES =
            SynchedEntityData.defineId(TotemSelloEntity.class, EntityDataSerializers.INT);
    private static final EntityDataAccessor<Integer> DATA_AGUANTA =
            SynchedEntityData.defineId(TotemSelloEntity.class, EntityDataSerializers.INT);
    private static final EntityDataAccessor<Boolean> DATA_ROTO =
            SynchedEntityData.defineId(TotemSelloEntity.class, EntityDataSerializers.BOOLEAN);
    private static final EntityDataAccessor<Integer> DATA_INDICE =
            SynchedEntityData.defineId(TotemSelloEntity.class, EntityDataSerializers.INT);

    /** Solo cliente: tick del ultimo golpe (el destello) y de cuando se rompio o se rehizo. */
    public int ultimoGolpe = -100;
    public int cambio = -100;
    private int golpesVistos;
    private boolean rotoVisto;

    private @Nullable RajangEntity dueno;

    public TotemSelloEntity(EntityType<? extends TotemSelloEntity> tipo, Level nivel) {
        super(tipo, nivel);
        this.noPhysics = true;
        setNoGravity(true);
    }

    public static TotemSelloEntity alzar(ServerLevel nivel, RajangEntity dueno, Vec3 donde, int indice, int aguanta) {
        TotemSelloEntity t = new TotemSelloEntity(AtalayaEntities.TOTEM_SELLO, nivel);
        t.dueno = dueno;
        t.entityData.set(DATA_AGUANTA, aguanta);
        t.entityData.set(DATA_INDICE, indice);
        t.setYRot(indice * 90.0F + 45.0F);
        t.setPos(donde.x, donde.y, donde.z);
        nivel.addFreshEntity(t);
        nivel.playSound(null, donde.x, donde.y, donde.z, AtalayaSonidos.RAJANG_TOTEM, SoundSource.HOSTILE, 3.0F, 1.0F);
        nivel.sendParticles(AtalayaParticulas.RAJANG_POLVO, true, true, donde.x, donde.y + 0.5, donde.z, 16, 0.8, 0.4, 0.8, 0.04);
        nivel.sendParticles(AtalayaParticulas.RAJANG_CHISPA, true, true, donde.x, donde.y + 2.5, donde.z, 20, 0.6, 1.4, 0.6, 0.06);
        return t;
    }

    @Override
    protected void defineSynchedData(SynchedEntityData.Builder datos) {
        datos.define(DATA_GOLPES, 0);
        datos.define(DATA_AGUANTA, 6);
        datos.define(DATA_ROTO, false);
        datos.define(DATA_INDICE, 0);
    }

    public int getGolpes() {
        return entityData.get(DATA_GOLPES);
    }

    public int getAguanta() {
        return entityData.get(DATA_AGUANTA);
    }

    public boolean isRoto() {
        return entityData.get(DATA_ROTO);
    }

    public int getIndice() {
        return entityData.get(DATA_INDICE);
    }

    @Override
    public void tick() {
        super.tick();
        if (level().isClientSide()) {
            particulasCliente();
            return;
        }
        if (dueno == null || dueno.isRemoved() || dueno.getEstado() != RajangEntity.SELLO) {
            desmontar((ServerLevel) level());
            return;
        }
        if (!isRoto() && tickCount % 60 == 0) {
            level().playSound(null, getX(), getY() + 2, getZ(), AtalayaSonidos.RAJANG_TOTEM, SoundSource.HOSTILE, 2.0F, 1.0F);
        }
    }

    private void particulasCliente() {
        if (getGolpes() != golpesVistos) {
            golpesVistos = getGolpes();
            ultimoGolpe = tickCount;
        }
        if (isRoto() != rotoVisto) {
            rotoVisto = isRoto();
            cambio = tickCount;
        }
        if (isRoto()) {
            if (tickCount % 6 == 0) {
                level().addParticle(AtalayaParticulas.RAJANG_POLVO, getX(), getY() + 2.5, getZ(), 0, 0.02, 0);
            }
            return;
        }
        // Los glifos sueltan chispas, y una corriente de luz va hacia Rajang.
        if (tickCount % 3 == 0) {
            double a = random.nextDouble() * Math.PI * 2;
            level().addParticle(AtalayaParticulas.RAJANG_CHISPA, getX() + Math.cos(a) * 0.9, getY() + 0.6 + random.nextDouble() * 4.0,
                    getZ() + Math.sin(a) * 0.9, 0, 0.03, 0);
        }
        if (tickCount % 2 == 0) {
            for (Entity e : level().getEntities(this, getBoundingBox().inflate(48), x -> x instanceof RajangEntity)) {
                Vec3 hacia = e.position().add(0, 5.0, 0).subtract(position().add(0, 4.8, 0));
                Vec3 v = hacia.normalize().scale(1.1);
                level().addParticle(AtalayaParticulas.RAJANG_CHISPA, getX(), getY() + 4.8, getZ(), v.x, v.y, v.z);
                break;
            }
        }
    }

    public void romper(ServerLevel nivel) {
        if (isRoto()) {
            return;
        }
        entityData.set(DATA_ROTO, true);
        Vec3 c = position().add(0, 3.0, 0);
        nivel.playSound(null, c.x, c.y, c.z, AtalayaSonidos.RAJANG_TOTEM_ROTO, SoundSource.HOSTILE, 4.0F, 1.0F);
        nivel.sendParticles(AtalayaParticulas.RAJANG_JADE, true, true, c.x, c.y, c.z, 30, 0.6, 1.2, 0.6, 0.2);
        nivel.sendParticles(AtalayaParticulas.RAJANG_ROCA, true, true, c.x, c.y, c.z, 20, 0.6, 1.0, 0.6, 0.25);
        nivel.sendParticles(AtalayaParticulas.RAJANG_ONDA, true, true, getX(), getY() + 0.1, getZ(), 0, 0.8, 5.0, 0.0, 1.0);
        if (dueno != null) {
            dueno.alRomperTotem(nivel, this);
        }
    }

    /** Se acaba el Sello: se deshace en polvo. */
    public void desmontar(ServerLevel nivel) {
        if (isRemoved()) {
            return;
        }
        nivel.sendParticles(AtalayaParticulas.RAJANG_POLVO, true, true, getX(), getY() + 2.0, getZ(), 16, 0.6, 1.2, 0.6, 0.03);
        nivel.sendParticles(AtalayaParticulas.RAJANG_ROCA, true, true, getX(), getY() + 2.0, getZ(), 8, 0.5, 1.0, 0.5, 0.1);
        discard();
    }

    @Override
    public boolean isPickable() {
        return !isRoto();
    }

    @Override
    public boolean hurtServer(ServerLevel nivel, DamageSource fuente, float cantidad) {
        if (isRemoved() || isRoto() || fuente.getEntity() instanceof RajangEntity) {
            return false;
        }
        int golpes = getGolpes() + 1;
        entityData.set(DATA_GOLPES, golpes);
        Vec3 c = position().add(0, 2.6, 0);
        nivel.playSound(null, c.x, c.y, c.z, AtalayaSonidos.RAJANG_TOTEM_GOLPE, SoundSource.HOSTILE, 2.0F,
                0.8F + 0.6F * golpes / Math.max(1, getAguanta()));
        nivel.sendParticles(AtalayaParticulas.RAJANG_JADE, true, true, c.x, c.y, c.z, 6, 0.3, 0.6, 0.3, 0.15);
        if (golpes >= getAguanta()) {
            romper(nivel);
        }
        return true;
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
