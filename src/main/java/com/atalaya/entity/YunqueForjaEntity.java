package com.atalaya.entity;

import com.atalaya.particula.AtalayaParticulas;
import com.atalaya.sonido.AtalayaSonidos;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
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
 * Un yunque de la Forja del Juramento: basalto con su banda de oro y, encima,
 * una hoja al rojo. Sobre la hoja se cierra un aro de luz, una y otra vez: hay
 * que golpearla cuando el aro la toca (perfecto, bien o a destiempo). Con
 * GOLPES buenos la hoja queda forjada, de oro. A destiempo saltan chispas que
 * queman al que golpea.
 *
 * El aro va con el tiempo del mundo (el mismo en el cliente y en el servidor):
 * empieza en DATA_INICIO y se cierra en PERIODO ticks. Al juzgar un golpe se
 * descuenta la latencia de quien golpea (lo que tarda en verlo y en llegar su
 * golpe).
 */
public class YunqueForjaEntity extends Entity {

    public static final float ANCHO = 3.2F;
    /** Mas alta que el yunque (1,7): asi se le da apuntando a la hoja o al aro que tiene encima. */
    public static final float ALTO = 2.4F;
    /** Lo que tarda en salir del suelo y en hundirse. */
    public static final int SUBE = 20;
    public static final int BAJA = 20;
    /** Lo que tarda el aro en cerrarse sobre la hoja y la pausa tras un buen golpe. */
    public static final int PERIODO = 30;
    private static final int PAUSA = 6;
    /** Los golpes buenos que pide cada hoja. */
    public static final int GOLPES = 6;
    /** Lo que se perdona: a 2 ticks del toque es perfecto, a 4 bien. */
    private static final int PERFECTO = 2;
    private static final int BIEN = 4;
    /** El aro: de donde sale (radio, bloques) y el tamano de la hoja, donde la toca. */
    public static final float ARO_SALE = 2.6F;
    public static final float ARO_HOJA = 0.6F;
    /** A que altura va la hoja (el centro del aro). */
    public static final float ALTO_HOJA = 1.62F;

    public static final int MAL = 0;
    public static final int BIEN_HECHO = 1;
    public static final int PERFECTO_HECHO = 2;

    private static final EntityDataAccessor<Long> DATA_INICIO =
            SynchedEntityData.defineId(YunqueForjaEntity.class, EntityDataSerializers.LONG);
    private static final EntityDataAccessor<Integer> DATA_GOLPES =
            SynchedEntityData.defineId(YunqueForjaEntity.class, EntityDataSerializers.INT);
    /** Tiempo del mundo del ultimo golpe y como fue (MAL, BIEN_HECHO, PERFECTO_HECHO). */
    private static final EntityDataAccessor<Long> DATA_ULTIMO =
            SynchedEntityData.defineId(YunqueForjaEntity.class, EntityDataSerializers.LONG);
    private static final EntityDataAccessor<Integer> DATA_CALIDAD =
            SynchedEntityData.defineId(YunqueForjaEntity.class, EntityDataSerializers.INT);
    /** Tick en que empezo a hundirse (-1: en pie). */
    private static final EntityDataAccessor<Integer> DATA_BAJA =
            SynchedEntityData.defineId(YunqueForjaEntity.class, EntityDataSerializers.INT);
    /** Si la hoja ha salido volando hacia el (ya no esta en el yunque). */
    private static final EntityDataAccessor<Boolean> DATA_VUELA =
            SynchedEntityData.defineId(YunqueForjaEntity.class, EntityDataSerializers.BOOLEAN);

    private @Nullable ForjaNovilis juego;

    public YunqueForjaEntity(EntityType<? extends YunqueForjaEntity> tipo, Level nivel) {
        super(tipo, nivel);
        setNoGravity(true);
    }

    static YunqueForjaEntity alzar(ServerLevel nivel, ForjaNovilis juego, Vec3 donde, float rumbo) {
        YunqueForjaEntity y = new YunqueForjaEntity(AtalayaEntities.YUNQUE_FORJA, nivel);
        y.juego = juego;
        y.snapTo(donde.x, donde.y, donde.z, rumbo, 0.0F);
        y.entityData.set(DATA_INICIO, nivel.getGameTime() + SUBE + nivel.getRandom().nextInt(PERIODO));
        nivel.addFreshEntity(y);
        nivel.sendParticles(AtalayaParticulas.NOVILIS_ROCA, true, true, donde.x, donde.y + 0.3, donde.z, 14, 1.0, 0.2, 1.0, 0.15);
        nivel.sendParticles(AtalayaParticulas.NOVILIS_LLAMA, true, true, donde.x, donde.y + 0.3, donde.z, 16, 1.2, 0.1, 1.2, 0.04);
        return y;
    }

    @Override
    protected void defineSynchedData(SynchedEntityData.Builder datos) {
        datos.define(DATA_INICIO, 0L);
        datos.define(DATA_GOLPES, 0);
        datos.define(DATA_ULTIMO, -100L);
        datos.define(DATA_CALIDAD, MAL);
        datos.define(DATA_BAJA, -1);
        datos.define(DATA_VUELA, false);
    }

    public int getGolpes() {
        return entityData.get(DATA_GOLPES);
    }

    public boolean forjada() {
        return getGolpes() >= GOLPES;
    }

    public long getUltimo() {
        return entityData.get(DATA_ULTIMO);
    }

    public int getCalidad() {
        return entityData.get(DATA_CALIDAD);
    }

    public int getBaja() {
        return entityData.get(DATA_BAJA);
    }

    public boolean vuela() {
        return entityData.get(DATA_VUELA);
    }

    /**
     * El radio del aro en este momento del mundo (bloques), o -1 si no hay aro
     * (en la pausa tras un golpe, con la hoja forjada o mientras sale del suelo).
     */
    public float radioAro(long tiempo, float parcial) {
        if (forjada() || getBaja() >= 0) {
            return -1.0F;
        }
        float dt = tiempo - entityData.get(DATA_INICIO) + parcial;
        if (dt < 0.0F) {
            return -1.0F;
        }
        float k = (dt % PERIODO) / PERIODO;
        return ARO_HOJA + (ARO_SALE - ARO_HOJA) * (1.0F - k);
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

    @Override
    public EntityDimensions getDimensions(Pose pose) {
        return EntityDimensions.fixed(ANCHO, ALTO);
    }

    @Override
    public boolean canCollideWith(Entity otro) {
        return false;
    }

    @Override
    public boolean isPickable() {
        return !isRemoved() && getBaja() < 0 && tickCount >= SUBE / 2;
    }

    @Override
    public boolean isPushable() {
        return false;
    }

    @Override
    public boolean hurtServer(ServerLevel nivel, DamageSource fuente, float cantidad) {
        if (juego == null || getBaja() >= 0 || !(fuente.getEntity() instanceof Player p) || p.isSpectator()) {
            return false;
        }
        if (forjada()) {
            nivel.playSound(null, getX(), getY() + ALTO_HOJA, getZ(), AtalayaSonidos.NOVILIS_FORJA_BIEN, SoundSource.PLAYERS, 0.6F, 1.6F);
            return true;
        }
        long ahora = nivel.getGameTime();
        // Lo que tarda en verlo y en llegar su golpe (ida y vuelta), en ticks.
        int retraso = p instanceof ServerPlayer sp ? Mth.clamp(sp.connection.latency() / 50, 0, 8) : 0;
        long dt = ahora - retraso - entityData.get(DATA_INICIO);
        int calidad = MAL;
        if (dt >= PERIODO - BIEN) {
            long m = dt % PERIODO;
            long d = Math.min(m, PERIODO - m);
            calidad = d <= PERFECTO ? PERFECTO_HECHO : d <= BIEN ? BIEN_HECHO : MAL;
        }
        entityData.set(DATA_ULTIMO, ahora);
        entityData.set(DATA_CALIDAD, calidad);
        Vec3 h = position().add(0, ALTO_HOJA, 0);
        if (calidad == MAL) {
            nivel.playSound(null, h.x, h.y, h.z, AtalayaSonidos.NOVILIS_FORJA_MAL, SoundSource.PLAYERS, 1.4F, 0.9F + random.nextFloat() * 0.2F);
            nivel.sendParticles(AtalayaParticulas.NOVILIS_CHISPA, true, true, h.x, h.y, h.z, 14, 0.5, 0.2, 0.5, 0.25);
            juego.alFallar(nivel, this, p);
            return true;
        }
        int g = getGolpes() + 1;
        entityData.set(DATA_GOLPES, g);
        // Tras un buen golpe, el aro vuelve a salir (despues de una pausa).
        entityData.set(DATA_INICIO, ahora + PAUSA);
        boolean perfecto = calidad == PERFECTO_HECHO;
        nivel.playSound(null, h.x, h.y, h.z, perfecto ? AtalayaSonidos.NOVILIS_FORJA_PERFECTO : AtalayaSonidos.NOVILIS_FORJA_BIEN,
                SoundSource.PLAYERS, 2.0F, 0.95F + 0.03F * g);
        nivel.sendParticles(AtalayaParticulas.NOVILIS_CHISPA, true, true, h.x, h.y, h.z, perfecto ? 30 : 16, 0.6, 0.2, 0.6, 0.3);
        if (perfecto) {
            nivel.sendParticles(AtalayaParticulas.NOVILIS_LUZ, true, true, h.x, h.y + 0.2, h.z, 10, 0.5, 0.2, 0.5, 0.05);
        }
        if (g >= GOLPES) {
            nivel.playSound(null, h.x, h.y, h.z, AtalayaSonidos.NOVILIS_FORJA_HOJA, SoundSource.PLAYERS, 3.0F, 1.0F);
            nivel.sendParticles(AtalayaParticulas.NOVILIS_LUZ, true, true, h.x, h.y + 0.3, h.z, 40, 1.0, 0.4, 1.0, 0.08);
        }
        juego.alAcertar(nivel, this, p, perfecto);
        return true;
    }

    /** La hoja sale volando hacia el. */
    void volar() {
        entityData.set(DATA_VUELA, true);
    }

    /** Se acabo: se hunde en el suelo. */
    void hundir() {
        if (getBaja() < 0) {
            entityData.set(DATA_BAJA, tickCount);
        }
    }

    @Override
    public void tick() {
        super.tick();
        if (level().isClientSide()) {
            if (getBaja() < 0 && !vuela() && random.nextInt(forjada() ? 3 : 5) == 0) {
                // La hoja al rojo suelta brasas; la forjada, motas de oro.
                Vec3 p = Vec3.directionFromRotation(0.0F, getYRot() + 90.0F).scale((random.nextDouble() - 0.5) * 2.0);
                level().addParticle(forjada() ? AtalayaParticulas.NOVILIS_LUZ : AtalayaParticulas.NOVILIS_BRASA,
                        getX() + p.x, getY() + ALTO_HOJA + 0.1, getZ() + p.z, 0, 0.03, 0);
            }
            return;
        }
        if (juego == null || (getBaja() >= 0 && tickCount - getBaja() > BAJA + 2)) {
            discard();
        }
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
