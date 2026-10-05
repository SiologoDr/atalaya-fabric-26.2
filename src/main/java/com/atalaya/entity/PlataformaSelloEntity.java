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
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.storage.ValueInput;
import net.minecraft.world.level.storage.ValueOutput;
import net.minecraft.world.phys.Vec3;
import org.jspecify.annotations.Nullable;

import java.util.ArrayList;
import java.util.List;

/**
 * Una pieza del Sello de la Tierra, hecha por nosotros (no son bloques del
 * mundo): se pisa como el suelo, pero es una entidad con su caja de choque.
 *
 *   - La columna: una torre de bloques de roca algo torcidos, como los
 *     pilares del Terremoto pero ancha y alta (26 bloques), con la hierba
 *     arriba y el totem encima. Avisa en el suelo, sube retumbando y quien
 *     estuviera en su sitio sale despedido.
 *   - Las piedras: losas de roca con hierba que flotan en espiral alrededor
 *     de la columna; cada una sube desde el suelo a su sitio y desde ahi se
 *     puede pisar. Son el parkour para llegar arriba.
 *
 * Al acabar el Sello se hunden (la columna) o se desmoronan (las piedras); a
 * quien este encima no le duele la caida. No se guardan con el mundo.
 *
 * El juego solo busca choques con entidades cuyo origen este a menos de unos
 * 4 bloques por debajo de quien se mueve: la columna, ya arriba, se pisa por
 * sus tramos (cajas invisibles de 3 bloques apiladas, del tipo TRAMO).
 */
public class PlataformaSelloEntity extends Entity {

    public static final int COLUMNA = 0;
    public static final int PIEDRA = 1;
    /** Un tramo invisible de la caja de la columna. */
    public static final int TRAMO = 2;
    private static final float ALTO_TRAMO = 3.0F;

    /** Ticks de aviso de la columna, lo que tarda en subir y lo que tarda en hundirse. */
    public static final int AVISO = 20;
    public static final int SUBE = 60;
    public static final int BAJA = 40;
    /** Lo que tarda una piedra en llegar a su sitio y en caerse. */
    public static final int VUELA = 12;
    public static final int CAE = 14;
    /** Grueso de la losa que se pisa de una piedra. */
    public static final float GRUESO = 0.6F;

    private static final EntityDataAccessor<Integer> DATA_TIPO =
            SynchedEntityData.defineId(PlataformaSelloEntity.class, EntityDataSerializers.INT);
    private static final EntityDataAccessor<Float> DATA_ANCHO =
            SynchedEntityData.defineId(PlataformaSelloEntity.class, EntityDataSerializers.FLOAT);
    private static final EntityDataAccessor<Float> DATA_ALTO =
            SynchedEntityData.defineId(PlataformaSelloEntity.class, EntityDataSerializers.FLOAT);
    private static final EntityDataAccessor<Integer> DATA_SEMILLA =
            SynchedEntityData.defineId(PlataformaSelloEntity.class, EntityDataSerializers.INT);
    /** Tick (de la propia pieza) en que empieza a subir o a volar a su sitio. */
    private static final EntityDataAccessor<Integer> DATA_NACE =
            SynchedEntityData.defineId(PlataformaSelloEntity.class, EntityDataSerializers.INT);
    /** Lo que sube volando una piedra hasta su sitio. */
    private static final EntityDataAccessor<Float> DATA_VUELO =
            SynchedEntityData.defineId(PlataformaSelloEntity.class, EntityDataSerializers.FLOAT);
    /** Tick en que empezo a irse (-1: sigue en pie). */
    private static final EntityDataAccessor<Integer> DATA_SE_VA =
            SynchedEntityData.defineId(PlataformaSelloEntity.class, EntityDataSerializers.INT);

    private @Nullable RajangEntity dueno;
    private float altoVisto = -1.0F;
    private final List<PlataformaSelloEntity> tramos = new ArrayList<>();

    public PlataformaSelloEntity(EntityType<? extends PlataformaSelloEntity> tipo, Level nivel) {
        super(tipo, nivel);
        this.noPhysics = true;
        setNoGravity(true);
    }

    /** La columna, con su base en el suelo; sube tras el aviso y 'retraso' ticks. */
    public static PlataformaSelloEntity columna(ServerLevel nivel, RajangEntity dueno, Vec3 base, float ancho, float alto, int retraso) {
        PlataformaSelloEntity p = crear(nivel, dueno, COLUMNA, base, ancho, alto, retraso + AVISO);
        nivel.sendParticles(AtalayaParticulas.RAJANG_AVISO, true, true, base.x, base.y + 0.07, base.z, 0,
                ancho * 0.8, retraso + AVISO + 4, 0.0, 1.0);
        nivel.playSound(null, base.x, base.y, base.z, AtalayaSonidos.RAJANG_AVISO, SoundSource.HOSTILE, 2.0F, 0.7F);
        return p;
    }

    /** Una piedra del parkour con su cara de arriba a la altura 'arriba'; vuela a su sitio en 'retraso' ticks. */
    public static PlataformaSelloEntity piedra(ServerLevel nivel, RajangEntity dueno, Vec3 centro, double arriba, float ancho, int retraso) {
        PlataformaSelloEntity p = crear(nivel, dueno, PIEDRA, new Vec3(centro.x, arriba - GRUESO, centro.z), ancho, GRUESO, retraso);
        p.entityData.set(DATA_VUELO, (float) Math.max(1.0, arriba - centro.y));
        return p;
    }

    private static PlataformaSelloEntity crear(ServerLevel nivel, RajangEntity dueno, int tipo, Vec3 donde, float ancho,
                                               float alto, int nace) {
        PlataformaSelloEntity p = new PlataformaSelloEntity(AtalayaEntities.PLATAFORMA_SELLO, nivel);
        p.dueno = dueno;
        p.entityData.set(DATA_TIPO, tipo);
        p.entityData.set(DATA_ANCHO, ancho);
        p.entityData.set(DATA_ALTO, alto);
        p.entityData.set(DATA_SEMILLA, nivel.getRandom().nextInt());
        p.entityData.set(DATA_NACE, nace);
        p.setYRot(nivel.getRandom().nextFloat() * 360.0F);
        p.setPos(donde.x, donde.y, donde.z);
        p.refreshDimensions();
        nivel.addFreshEntity(p);
        return p;
    }

    @Override
    protected void defineSynchedData(SynchedEntityData.Builder datos) {
        datos.define(DATA_TIPO, COLUMNA);
        datos.define(DATA_ANCHO, 4.0F);
        datos.define(DATA_ALTO, 13.0F);
        datos.define(DATA_SEMILLA, 0);
        datos.define(DATA_NACE, 0);
        datos.define(DATA_VUELO, 0.0F);
        datos.define(DATA_SE_VA, -1);
    }

    public int getTipo() {
        return entityData.get(DATA_TIPO);
    }

    public float getAncho() {
        return entityData.get(DATA_ANCHO);
    }

    public float getAlto() {
        return entityData.get(DATA_ALTO);
    }

    public int getSemilla() {
        return entityData.get(DATA_SEMILLA);
    }

    public int getNace() {
        return entityData.get(DATA_NACE);
    }

    public int getSeVa() {
        return entityData.get(DATA_SE_VA);
    }

    /**
     * De 0 a 1, cuanto ha subido (la columna) o llegado (la piedra) y, al
     * irse, cuanto queda; con rebote al llegar arriba.
     */
    public static float salida(int tipo, float edad, int nace, int seVa) {
        if (seVa >= 0 && edad >= seVa) {
            float k = (edad - seVa) / (tipo == COLUMNA ? BAJA : CAE);
            return Mth.clamp(1.0F - k, 0.0F, 1.0F);
        }
        float e = edad - nace;
        if (e <= 0) {
            return 0.0F;
        }
        float dura = tipo == COLUMNA ? SUBE : VUELA;
        if (e >= dura) {
            return 1.0F;
        }
        float k = e / dura;
        if (tipo == COLUMNA) {
            // Sube a empellones, de capa en capa, como si empujara la tierra.
            float paso = (float) Math.floor(k * 9.0F) / 9.0F;
            float dentro = k * 9.0F - (float) Math.floor(k * 9.0F);
            return Mth.clamp(paso + (1.0F / 9.0F) * (float) Math.pow(dentro, 0.35), 0.0F, 1.0F);
        }
        return 1.0F - (float) Math.pow(1.0F - k, 3);
    }

    private float salida() {
        return salida(getTipo(), tickCount, getNace(), getSeVa());
    }

    /** En pie y en su sitio: ya se puede pisar. */
    public boolean firme() {
        int tipo = getTipo();
        return getSeVa() < 0 && tickCount >= getNace() + (tipo == PIEDRA ? VUELA : tipo == COLUMNA ? 2 : 0);
    }

    @Override
    public void onSyncedDataUpdated(EntityDataAccessor<?> dato) {
        super.onSyncedDataUpdated(dato);
        if (DATA_ANCHO.equals(dato) || DATA_ALTO.equals(dato) || DATA_TIPO.equals(dato)) {
            refreshDimensions();
        }
    }

    /** La caja de choque: la columna crece con lo que ha subido; la piedra, solo la losa de arriba. */
    @Override
    public EntityDimensions getDimensions(Pose pose) {
        float alto = getAlto();
        if (getTipo() == COLUMNA) {
            alto *= salida();
        }
        return EntityDimensions.fixed(getAncho(), Math.max(0.01F, alto));
    }

    @Override
    public boolean canBeCollidedWith(@Nullable Entity otro) {
        return !isRemoved() && (getTipo() == COLUMNA ? salida() > 0.05F : firme());
    }

    @Override
    public boolean canCollideWith(Entity otro) {
        return false;
    }

    @Override
    public void tick() {
        super.tick();
        int tipo = getTipo();
        // La columna crece y mengua: su caja tambien (en los dos lados, cada tick).
        if (tipo == COLUMNA) {
            float alto = getAlto() * salida();
            if (Math.abs(alto - altoVisto) > 1.0E-3F) {
                altoVisto = alto;
                refreshDimensions();
            }
        }
        if (tipo == TRAMO) {
            if (!level().isClientSide() && (dueno == null || dueno.isRemoved())) {
                discard();
            }
            return;
        }
        if (level().isClientSide()) {
            particulasCliente(tipo);
            return;
        }
        ServerLevel nivel = (ServerLevel) level();
        int seVa = getSeVa();
        if (seVa < 0 && (dueno == null || dueno.isRemoved())) {
            irse(nivel);
            return;
        }
        if (seVa >= 0) {
            // Mientras se va, a quien estuviera encima no le duele la caida.
            for (Player p : nivel.getEntitiesOfClass(Player.class, getBoundingBox().inflate(4.0, 20.0, 4.0))) {
                p.resetFallDistance();
            }
            if (tickCount - seVa >= (tipo == COLUMNA ? BAJA : CAE) + 2) {
                discard();
            }
            return;
        }
        int e = tickCount - getNace();
        if (tipo == COLUMNA) {
            tickColumna(nivel, e);
        } else if (e == 0) {
            nivel.playSound(null, getX(), getY(), getZ(), AtalayaSonidos.RAJANG_PLATAFORMA, SoundSource.HOSTILE, 1.0F,
                    1.3F + random.nextFloat() * 0.3F);
        } else if (e == VUELA) {
            nivel.sendParticles(AtalayaParticulas.RAJANG_POLVO, true, true, getX(), getY() + GRUESO, getZ(), 6, getAncho() * 0.3,
                    0.1, getAncho() * 0.3, 0.02);
        }
    }

    private void tickColumna(ServerLevel nivel, int e) {
        if (e == 0) {
            // Quien este en su sitio sale despedido: la tierra revienta hacia arriba.
            double r = getAncho() * 0.5 + 0.6;
            for (LivingEntity v : nivel.getEntitiesOfClass(LivingEntity.class, getBoundingBox().inflate(0.6, 3.0, 0.6),
                    x -> !(x instanceof RajangEntity))) {
                if (RajangEntity.horizontal(position(), v.position()) > r * 1.45) {
                    continue;
                }
                Vec3 fuera = RajangEntity.horizontalHacia(position(), v.position());
                v.setDeltaMovement(fuera.x * 0.9, 0.55, fuera.z * 0.9);
                v.hurtMarked = true;
            }
            nivel.sendParticles(AtalayaParticulas.RAJANG_ROCA, true, true, getX(), getY() + 0.5, getZ(), 24, 1.2, 0.4, 1.2, 0.3);
            nivel.sendParticles(AtalayaParticulas.RAJANG_ONDA, true, true, getX(), getY() + 0.1, getZ(), 0, 1.6, 7.0, 0.0, 1.0);
        }
        if (e == SUBE && tramos.isEmpty() && dueno != null) {
            // Ya arriba: los tramos que se pisan.
            for (float y = 0.0F; y < getAlto() - 0.01F; y += ALTO_TRAMO) {
                tramos.add(crear(nivel, dueno, TRAMO, position().add(0, y, 0), getAncho(), Math.min(ALTO_TRAMO, getAlto() - y), 0));
            }
        }
        if (e >= 0 && e < SUBE && e % 5 == 0) {
            nivel.playSound(null, getX(), getY() + getAlto() * salida(), getZ(), AtalayaSonidos.RAJANG_PLATAFORMA,
                    SoundSource.HOSTILE, 2.5F, 0.75F + 0.3F * e / SUBE);
        }
    }

    private void particulasCliente(int tipo) {
        int e = tickCount - getNace();
        float ancho = getAncho();
        if (getSeVa() >= 0) {
            if (tickCount % 2 == 0) {
                double y = getY() + (tipo == COLUMNA ? getAlto() * salida() : GRUESO);
                level().addParticle(AtalayaParticulas.RAJANG_ROCA, getX() + (random.nextDouble() - 0.5) * ancho, y,
                        getZ() + (random.nextDouble() - 0.5) * ancho, 0, -0.1, 0);
            }
            return;
        }
        if (tipo == COLUMNA) {
            if (e < 0 && tickCount % 3 == 0) {
                // El suelo tiembla donde va a salir.
                level().addParticle(AtalayaParticulas.RAJANG_POLVO, getX() + random.nextGaussian() * ancho * 0.4, getY() + 0.1,
                        getZ() + random.nextGaussian() * ancho * 0.4, 0, 0.05, 0);
            }
            if (e >= 0 && e < SUBE) {
                for (int i = 0; i < 3; i++) {
                    double a = random.nextDouble() * Math.PI * 2;
                    double r = ancho * 0.55 + random.nextDouble() * 0.6;
                    level().addParticle(AtalayaParticulas.RAJANG_POLVO, getX() + Math.cos(a) * r, getY() + 0.3,
                            getZ() + Math.sin(a) * r, Math.cos(a) * 0.08, 0.06, Math.sin(a) * 0.08);
                }
            }
            return;
        }
        // La piedra: sube dejando un reguero de tierra y, ya quieta, suelta algo de polvo por debajo.
        if (e >= 0 && e < VUELA) {
            float k = salida();
            double y = getY() - getVuelo() * (1.0F - k);
            level().addParticle(AtalayaParticulas.RAJANG_POLVO, getX(), y, getZ(), 0, -0.02, 0);
        } else if (e >= VUELA && tickCount % 24 == 0) {
            level().addParticle(AtalayaParticulas.RAJANG_POLVO, getX() + (random.nextDouble() - 0.5) * ancho * 0.5, getY() - 0.6,
                    getZ() + (random.nextDouble() - 0.5) * ancho * 0.5, 0, -0.02, 0);
        }
    }

    /** Lo que sube volando una piedra: de donde sale en el suelo hasta su sitio. */
    public float getVuelo() {
        return entityData.get(DATA_VUELO);
    }

    /** Se acaba el Sello: la columna se hunde y las piedras se desmoronan. */
    public void irse(ServerLevel nivel) {
        if (isRemoved() || getSeVa() >= 0) {
            return;
        }
        quitarTramos();
        if (getTipo() == TRAMO) {
            discard();
            return;
        }
        if (getTipo() == COLUMNA) {
            altoVisto = -1.0F;
            nivel.playSound(null, getX(), getY() + getAlto(), getZ(), AtalayaSonidos.RAJANG_PLATAFORMA, SoundSource.HOSTILE, 4.0F, 0.6F);
            nivel.sendParticles(AtalayaParticulas.RAJANG_POLVO, true, true, getX(), getY() + 1.0, getZ(), 30, getAncho() * 0.5,
                    0.5, getAncho() * 0.5, 0.05);
        } else {
            nivel.sendParticles(AtalayaParticulas.RAJANG_ROCA, true, true, getX(), getY(), getZ(), 6, 0.4, 0.2, 0.4, 0.1);
        }
        entityData.set(DATA_SE_VA, tickCount);
    }

    private void quitarTramos() {
        for (PlataformaSelloEntity t : tramos) {
            t.discard();
        }
        tramos.clear();
    }

    @Override
    public void remove(RemovalReason motivo) {
        super.remove(motivo);
        quitarTramos();
    }

    @Override
    public boolean isPickable() {
        return false;
    }

    @Override
    public boolean isPushable() {
        return false;
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
