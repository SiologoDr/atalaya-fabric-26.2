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
 * Una de las cuatro estatuas de las Trompetas del Apocalipsis: un angel de
 * marmol con su trompeta de oro, en su pedestal. Sale del suelo y toca su voz
 * de la melodia (cada una la suya: melodia_1 a melodia_4). Aguanta 10 golpes,
 * sean cuantos sean los jugadores; rota, su trompeta se calla.
 *
 * Si la melodia acaba con alguna en pie, Novilis entra en Furia.
 */
public class EstatuaNovilisEntity extends Entity {

    /** Lo que tarda en salir del suelo (ticks): el cliente la sube en ese tiempo. */
    public static final int SALE = 30;

    private static final EntityDataAccessor<Integer> DATA_GOLPES =
            SynchedEntityData.defineId(EstatuaNovilisEntity.class, EntityDataSerializers.INT);
    private static final EntityDataAccessor<Boolean> DATA_ROTO =
            SynchedEntityData.defineId(EstatuaNovilisEntity.class, EntityDataSerializers.BOOLEAN);
    private static final EntityDataAccessor<Integer> DATA_INDICE =
            SynchedEntityData.defineId(EstatuaNovilisEntity.class, EntityDataSerializers.INT);

    /** Solo cliente: el tick del ultimo golpe (el temblor) y de cuando se rompio. */
    public int ultimoGolpe = -100;
    public int cuandoRota = -100;
    private int golpesVistos;
    private boolean rotaVista;

    private @Nullable NovilisEntity dueno;

    public EstatuaNovilisEntity(EntityType<? extends EstatuaNovilisEntity> tipo, Level nivel) {
        super(tipo, nivel);
        this.noPhysics = true;
        setNoGravity(true);
    }

    public static EstatuaNovilisEntity alzar(ServerLevel nivel, NovilisEntity dueno, Vec3 donde, int indice, float rumbo) {
        EstatuaNovilisEntity s = new EstatuaNovilisEntity(AtalayaEntities.ESTATUA_NOVILIS, nivel);
        s.dueno = dueno;
        s.entityData.set(DATA_INDICE, indice);
        s.setYRot(rumbo);
        s.setPos(donde.x, donde.y, donde.z);
        nivel.addFreshEntity(s);
        nivel.sendParticles(AtalayaParticulas.NOVILIS_ROCA, true, true, donde.x, donde.y + 0.3, donde.z, 24, 1.2, 0.3, 1.2, 0.2);
        nivel.sendParticles(AtalayaParticulas.NOVILIS_HUMO, true, true, donde.x, donde.y + 0.5, donde.z, 20, 1.4, 0.4, 1.4, 0.03);
        // Su voz de la melodia, desde ella: se oye en toda la arena.
        nivel.playSound(null, donde.x, donde.y + 6, donde.z, NovilisEntity.melodiaDe(indice), SoundSource.HOSTILE, 8.0F, 1.0F);
        return s;
    }

    @Override
    protected void defineSynchedData(SynchedEntityData.Builder datos) {
        datos.define(DATA_GOLPES, 0);
        datos.define(DATA_ROTO, false);
        datos.define(DATA_INDICE, 0);
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
            if (!isRoto() && tickCount > SALE && tickCount % 7 == 0) {
                // Las notas salen de la campana de la trompeta: en la malla, a
                // (-26,4, -93,4, -22) px, 7,3 bloques arriba, 1,4 delante y 1,65 a un lado.
                float b = getYRot() * net.minecraft.util.Mth.DEG_TO_RAD;
                Vec3 frente = new Vec3(-net.minecraft.util.Mth.sin(b), 0, net.minecraft.util.Mth.cos(b));
                Vec3 lado = new Vec3(net.minecraft.util.Mth.cos(b), 0, net.minecraft.util.Mth.sin(b));
                Vec3 boca = position().add(frente.scale(1.375)).add(lado.scale(-1.65)).add(0, 7.34, 0);
                level().addParticle(AtalayaParticulas.NOVILIS_NOTA, boca.x, boca.y, boca.z, frente.x * 0.12, 0.06, frente.z * 0.12);
            }
            return;
        }
        if (dueno == null || dueno.isRemoved() || dueno.isDeadOrDying() || dueno.getMelodia() < 0) {
            desmontar((ServerLevel) level());
        }
    }

    public void romper(ServerLevel nivel) {
        if (isRoto()) {
            return;
        }
        entityData.set(DATA_ROTO, true);
        Vec3 c = position().add(0, 3.5, 0);
        nivel.playSound(null, c.x, c.y, c.z, AtalayaSonidos.NOVILIS_ESTATUA_ROTA, SoundSource.HOSTILE, 5.0F, 1.0F);
        nivel.sendParticles(AtalayaParticulas.NOVILIS_ROCA, true, true, c.x, c.y, c.z, 40, 1.0, 2.0, 1.0, 0.3);
        nivel.sendParticles(AtalayaParticulas.NOVILIS_HUMO, true, true, c.x, c.y, c.z, 24, 1.0, 2.0, 1.0, 0.05);
        nivel.sendParticles(AtalayaParticulas.NOVILIS_NOTA, true, true, c.x, c.y + 2, c.z, 10, 1.0, 1.0, 1.0, 0.1);
        if (dueno != null) {
            dueno.alRomperEstatua(nivel, getIndice());
        }
    }

    /** Se acaba la melodia: se deshace en polvo de marmol. */
    public void desmontar(ServerLevel nivel) {
        if (isRemoved()) {
            return;
        }
        nivel.sendParticles(AtalayaParticulas.NOVILIS_HUMO, true, true, getX(), getY() + 3.0, getZ(), 20, 1.0, 2.0, 1.0, 0.03);
        nivel.sendParticles(AtalayaParticulas.NOVILIS_ROCA, true, true, getX(), getY() + 3.0, getZ(), 14, 0.8, 2.0, 0.8, 0.12);
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
        Vec3 c = position().add(0, 3.5, 0);
        nivel.playSound(null, c.x, c.y, c.z, AtalayaSonidos.NOVILIS_ESTATUA_GOLPE, SoundSource.HOSTILE, 2.5F,
                0.8F + 0.6F * golpes / NovilisEntity.GOLPES);
        nivel.sendParticles(AtalayaParticulas.NOVILIS_ROCA, true, true, c.x, c.y, c.z, 6, 0.5, 1.0, 0.5, 0.15);
        if (dueno != null) {
            dueno.alGolpearEstatua(getIndice(), golpes);
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
