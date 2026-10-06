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
 * Una fuente solar de las Fuentes (el golpe cooperativo de Novilis): un
 * obelisco de marmol y oro con su sol flotando encima, que le manda fuego
 * mientras carga. Aguanta 10 golpes, sean cuantos sean los jugadores. Rota, se
 * apaga y deja de darle fuego: con las tres rotas antes de que se llene la
 * carga, a el se le apaga el sol y cae aturdido.
 */
public class FuenteSolarEntity extends Entity {

    /** Lo que tarda en salir del suelo (ticks). */
    public static final int SALE = 20;

    private static final EntityDataAccessor<Integer> DATA_GOLPES =
            SynchedEntityData.defineId(FuenteSolarEntity.class, EntityDataSerializers.INT);
    private static final EntityDataAccessor<Boolean> DATA_ROTO =
            SynchedEntityData.defineId(FuenteSolarEntity.class, EntityDataSerializers.BOOLEAN);
    private static final EntityDataAccessor<Integer> DATA_INDICE =
            SynchedEntityData.defineId(FuenteSolarEntity.class, EntityDataSerializers.INT);
    /** El id de Novilis: el cliente pinta el haz de fuego de la fuente a su pecho. */
    private static final EntityDataAccessor<Integer> DATA_DUENO =
            SynchedEntityData.defineId(FuenteSolarEntity.class, EntityDataSerializers.INT);

    public int ultimoGolpe = -100;
    public int cuandoRota = -100;
    private int golpesVistos;
    private boolean rotaVista;

    private @Nullable NovilisEntity dueno;

    public FuenteSolarEntity(EntityType<? extends FuenteSolarEntity> tipo, Level nivel) {
        super(tipo, nivel);
        this.noPhysics = true;
        setNoGravity(true);
    }

    public static FuenteSolarEntity alzar(ServerLevel nivel, NovilisEntity dueno, Vec3 donde, int indice) {
        FuenteSolarEntity f = new FuenteSolarEntity(AtalayaEntities.FUENTE_SOLAR, nivel);
        f.dueno = dueno;
        f.entityData.set(DATA_INDICE, indice);
        f.entityData.set(DATA_DUENO, dueno.getId());
        f.setYRot(indice * 120.0F);
        f.setPos(donde.x, donde.y, donde.z);
        nivel.addFreshEntity(f);
        nivel.sendParticles(AtalayaParticulas.NOVILIS_ROCA, true, true, donde.x, donde.y + 0.3, donde.z, 20, 1.0, 0.3, 1.0, 0.2);
        nivel.sendParticles(AtalayaParticulas.NOVILIS_LLAMA, true, true, donde.x, donde.y + 1.0, donde.z, 24, 0.8, 1.0, 0.8, 0.1);
        return f;
    }

    @Override
    protected void defineSynchedData(SynchedEntityData.Builder datos) {
        datos.define(DATA_GOLPES, 0);
        datos.define(DATA_ROTO, false);
        datos.define(DATA_INDICE, 0);
        datos.define(DATA_DUENO, -1);
    }

    public int getGolpes() {
        return entityData.get(DATA_GOLPES);
    }

    public boolean isRoto() {
        return entityData.get(DATA_ROTO);
    }

    public int getIndice() {
        return entityData.get(DATA_INDICE);
    }

    public int getIdDueno() {
        return entityData.get(DATA_DUENO);
    }

    @Override
    public void tick() {
        super.tick();
        if (level().isClientSide()) {
            if (getGolpes() != golpesVistos) {
                golpesVistos = getGolpes();
                ultimoGolpe = tickCount;
            }
            if (isRoto() != rotaVista) {
                rotaVista = isRoto();
                cuandoRota = tickCount;
            }
            if (!isRoto() && tickCount % 3 == 0) {
                double a = random.nextDouble() * Math.PI * 2;
                level().addParticle(AtalayaParticulas.NOVILIS_BRASA, getX() + Math.cos(a) * 0.9, getY() + 0.5 + random.nextDouble() * 4.5,
                        getZ() + Math.sin(a) * 0.9, 0, 0.04, 0);
            }
            return;
        }
        if (dueno == null || dueno.isRemoved() || dueno.getEstado() != NovilisEntity.FUENTES) {
            desmontar((ServerLevel) level());
        }
    }

    public void romper(ServerLevel nivel) {
        if (isRoto()) {
            return;
        }
        entityData.set(DATA_ROTO, true);
        Vec3 c = position().add(0, 3.0, 0);
        nivel.playSound(null, c.x, c.y, c.z, AtalayaSonidos.NOVILIS_FUENTE_ROTA, SoundSource.HOSTILE, 5.0F, 1.0F);
        nivel.sendParticles(AtalayaParticulas.NOVILIS_ROCA, true, true, c.x, c.y, c.z, 30, 0.8, 1.6, 0.8, 0.3);
        nivel.sendParticles(AtalayaParticulas.NOVILIS_CHISPA, true, true, c.x, c.y + 2, c.z, 30, 0.6, 0.6, 0.6, 0.4);
        nivel.sendParticles(AtalayaParticulas.NOVILIS_ONDA, true, true, getX(), getY() + 0.1, getZ(), 0, 0.8, 5.0, 0.0, 1.0);
        if (dueno != null) {
            dueno.alGolpearFuente(getIndice(), NovilisEntity.GOLPES);
        }
    }

    public void desmontar(ServerLevel nivel) {
        if (isRemoved()) {
            return;
        }
        nivel.sendParticles(AtalayaParticulas.NOVILIS_HUMO, true, true, getX(), getY() + 2.5, getZ(), 16, 0.6, 1.5, 0.6, 0.03);
        nivel.sendParticles(AtalayaParticulas.NOVILIS_ROCA, true, true, getX(), getY() + 2.5, getZ(), 10, 0.6, 1.5, 0.6, 0.12);
        discard();
    }

    @Override
    public boolean isPickable() {
        return !isRoto() && tickCount > SALE / 2;
    }

    @Override
    public boolean hurtServer(ServerLevel nivel, DamageSource fuente, float cantidad) {
        if (isRemoved() || isRoto() || fuente.getEntity() instanceof NovilisEntity || tickCount < SALE / 2) {
            return false;
        }
        int golpes = getGolpes() + 1;
        entityData.set(DATA_GOLPES, golpes);
        Vec3 c = position().add(0, 2.6, 0);
        nivel.playSound(null, c.x, c.y, c.z, AtalayaSonidos.NOVILIS_FUENTE_GOLPE, SoundSource.HOSTILE, 2.5F,
                0.8F + 0.6F * golpes / NovilisEntity.GOLPES);
        nivel.sendParticles(AtalayaParticulas.NOVILIS_CHISPA, true, true, c.x, c.y, c.z, 8, 0.4, 0.8, 0.4, 0.2);
        if (dueno != null) {
            dueno.alGolpearFuente(getIndice(), golpes);
        }
        if (golpes >= NovilisEntity.GOLPES) {
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
        return distancia < 192 * 192;
    }

    @Override
    protected void readAdditionalSaveData(ValueInput entrada) {
    }

    @Override
    protected void addAdditionalSaveData(ValueOutput salida) {
    }
}
