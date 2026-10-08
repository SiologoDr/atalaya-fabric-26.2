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
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.storage.ValueInput;
import net.minecraft.world.level.storage.ValueOutput;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;
import org.jspecify.annotations.Nullable;

/**
 * Una grieta de fuego de Novilis (08-10-2026).
 *
 * <ul>
 *   <li>LINEA (Furia Infernal): la raja recta que abre la espada al caer. Se
 *       abre de cerca a lejos en AVISO ticks y, hasta que el la arranca (DURA),
 *       escupe lava y fuego por toda ella: chorros que revientan aqui y alla y
 *       queman a quien este encima de la raja.</li>
 *   <li>BOCA (Mar de Llamas): un agujero con grietas alrededor. Primero solo se
 *       raja y brilla (el aviso); luego sale una columna de fuego que se queda
 *       hasta que acaba el Mar y quema a quien este dentro.</li>
 * </ul>
 *
 * Como el sello, la entidad no se mueve: el rumbo, el largo o el radio y los
 * tiempos van sincronizados y el cliente pinta la grieta y el fuego.
 */
public class GrietaNovilisEntity extends Entity {

    public static final int LINEA = 0;
    public static final int BOCA = 1;
    /** Lo que se tarda en apagar al final (ticks). */
    public static final int APAGA = 12;
    /** Cada cuanto quema (ticks). */
    private static final int QUEMA_CADA = 10;

    private static final EntityDataAccessor<Integer> DATA_TIPO =
            SynchedEntityData.defineId(GrietaNovilisEntity.class, EntityDataSerializers.INT);
    private static final EntityDataAccessor<Float> DATA_RUMBO =
            SynchedEntityData.defineId(GrietaNovilisEntity.class, EntityDataSerializers.FLOAT);
    /** El largo de la raja (LINEA) o el radio de la boca (BOCA). */
    private static final EntityDataAccessor<Float> DATA_TAM =
            SynchedEntityData.defineId(GrietaNovilisEntity.class, EntityDataSerializers.FLOAT);
    private static final EntityDataAccessor<Integer> DATA_AVISO =
            SynchedEntityData.defineId(GrietaNovilisEntity.class, EntityDataSerializers.INT);
    private static final EntityDataAccessor<Integer> DATA_DURA =
            SynchedEntityData.defineId(GrietaNovilisEntity.class, EntityDataSerializers.INT);
    /** Fase del dueno (el color del fuego); 5 la Furia. */
    private static final EntityDataAccessor<Integer> DATA_COLOR =
            SynchedEntityData.defineId(GrietaNovilisEntity.class, EntityDataSerializers.INT);

    private @Nullable NovilisEntity dueno;
    private float dano;

    public GrietaNovilisEntity(EntityType<? extends GrietaNovilisEntity> tipo, Level nivel) {
        super(tipo, nivel);
        this.noPhysics = true;
        setNoGravity(true);
    }

    /** La raja de la Furia Infernal, de "desde" hacia "rumbo". */
    public static GrietaNovilisEntity linea(ServerLevel nivel, NovilisEntity dueno, Vec3 desde, float rumbo, float largo, int aviso,
                                            int dura, float dano, int color) {
        return poner(nivel, dueno, desde, LINEA, rumbo, largo, aviso, dura, dano, color);
    }

    /** Una boca del Mar de Llamas. */
    public static GrietaNovilisEntity boca(ServerLevel nivel, NovilisEntity dueno, Vec3 donde, float radio, int aviso, int dura,
                                           float dano, int color) {
        return poner(nivel, dueno, donde, BOCA, nivel.getRandom().nextFloat() * 360.0F, radio, aviso, dura, dano, color);
    }

    private static GrietaNovilisEntity poner(ServerLevel nivel, NovilisEntity dueno, Vec3 donde, int tipo, float rumbo, float tam,
                                             int aviso, int dura, float dano, int color) {
        GrietaNovilisEntity g = new GrietaNovilisEntity(AtalayaEntities.GRIETA_NOVILIS, nivel);
        g.dueno = dueno;
        g.dano = dano;
        g.entityData.set(DATA_TIPO, tipo);
        g.entityData.set(DATA_RUMBO, rumbo);
        g.entityData.set(DATA_TAM, tam);
        g.entityData.set(DATA_AVISO, Math.max(1, aviso));
        g.entityData.set(DATA_DURA, Math.max(aviso + 1, dura));
        g.entityData.set(DATA_COLOR, color);
        g.setPos(donde.x, donde.y, donde.z);
        nivel.addFreshEntity(g);
        return g;
    }

    @Override
    protected void defineSynchedData(SynchedEntityData.Builder datos) {
        datos.define(DATA_TIPO, BOCA);
        datos.define(DATA_RUMBO, 0.0F);
        datos.define(DATA_TAM, 2.6F);
        datos.define(DATA_AVISO, 30);
        datos.define(DATA_DURA, 200);
        datos.define(DATA_COLOR, 4);
    }

    public int getTipo() {
        return entityData.get(DATA_TIPO);
    }

    public float getRumbo() {
        return entityData.get(DATA_RUMBO);
    }

    public float getTam() {
        return entityData.get(DATA_TAM);
    }

    public int getAviso() {
        return entityData.get(DATA_AVISO);
    }

    public int getDura() {
        return entityData.get(DATA_DURA);
    }

    public int getColor() {
        return entityData.get(DATA_COLOR);
    }

    public Vec3 frente() {
        float b = getRumbo() * Mth.DEG_TO_RAD;
        return new Vec3(-Mth.sin(b), 0, Mth.cos(b));
    }

    /** Lo abierta que esta la raja (0 a 1): crece durante el aviso. */
    public float abierta(float edad) {
        return Mth.clamp(edad / getAviso(), 0.0F, 1.0F);
    }

    /** Lo fuerte que arde (0 antes de reventar; 1 mientras dura; baja al final). */
    public float fuego(float edad) {
        if (edad < getAviso()) {
            return 0.0F;
        }
        return Mth.clamp(Math.min((edad - getAviso()) / 4.0F, (getDura() + APAGA - edad) / APAGA), 0.0F, 1.0F);
    }

    /** Un punto al azar sobre la raja (LINEA) o dentro de la boca (BOCA). */
    private Vec3 puntoAlAzar(float hasta) {
        if (getTipo() == LINEA) {
            return position().add(frente().scale(random.nextDouble() * hasta));
        }
        double a = random.nextDouble() * Math.PI * 2;
        double r = Math.sqrt(random.nextDouble()) * getTam() * 0.8;
        return position().add(Math.cos(a) * r, 0, Math.sin(a) * r);
    }

    @Override
    public void tick() {
        super.tick();
        int aviso = getAviso();
        int dura = getDura();
        float k = fuego(tickCount);
        if (level().isClientSide()) {
            if (k <= 0.05F) {
                // el aviso: humo y brasas que salen de la raja
                if (random.nextInt(3) == 0) {
                    Vec3 p = puntoAlAzar(getTam() * abierta(tickCount));
                    level().addParticle(random.nextBoolean() ? AtalayaParticulas.NOVILIS_HUMO : AtalayaParticulas.NOVILIS_BRASA,
                            p.x, p.y + 0.1, p.z, 0, 0.04, 0);
                }
                return;
            }
            int n = getTipo() == LINEA ? 3 : 2;
            for (int i = 0; i < n; i++) {
                if (random.nextFloat() > k) {
                    continue;
                }
                Vec3 p = puntoAlAzar(getTam());
                double sube = getTipo() == BOCA ? 0.35 + random.nextDouble() * 0.25 : 0.2 + random.nextDouble() * 0.3;
                level().addParticle(random.nextInt(4) == 0 ? AtalayaParticulas.NOVILIS_CHISPA : AtalayaParticulas.NOVILIS_LLAMA,
                        p.x, p.y + 0.2, p.z, (random.nextDouble() - 0.5) * 0.05, sube, (random.nextDouble() - 0.5) * 0.05);
            }
            return;
        }
        if (dueno == null || dueno.isRemoved() || tickCount >= dura + APAGA) {
            discard();
            return;
        }
        ServerLevel nivel = (ServerLevel) level();
        if (tickCount == aviso) {
            // revienta: el fuego sale de golpe
            Vec3 c = getTipo() == LINEA ? position().add(frente().scale(getTam() * 0.5)) : position();
            nivel.playSound(null, c.x, c.y, c.z, AtalayaSonidos.NOVILIS_GEISER, SoundSource.HOSTILE, getTipo() == LINEA ? 4.0F : 2.2F,
                    0.9F + random.nextFloat() * 0.2F);
            if (getTipo() == BOCA) {
                nivel.sendParticles(AtalayaParticulas.NOVILIS_LLAMA, true, true, c.x, c.y + 1.0, c.z, 24, getTam() * 0.4, 1.2,
                        getTam() * 0.4, 0.12);
            }
        }
        if (tickCount >= aviso && tickCount < dura) {
            if (getTipo() == LINEA && tickCount % 4 == 0) {
                // los chorros de lava que revientan por la raja
                Vec3 p = puntoAlAzar(getTam());
                nivel.sendParticles(AtalayaParticulas.NOVILIS_LLAMA, true, true, p.x, p.y + 0.5, p.z, 10, 0.4, 1.0, 0.4, 0.15);
                nivel.sendParticles(AtalayaParticulas.NOVILIS_CHISPA, true, true, p.x, p.y + 0.5, p.z, 8, 0.3, 0.8, 0.3, 0.35);
                if (tickCount % 12 == 0) {
                    nivel.playSound(null, p.x, p.y, p.z, AtalayaSonidos.NOVILIS_GEISER, SoundSource.HOSTILE, 2.5F,
                            0.85F + random.nextFloat() * 0.3F);
                }
            }
            if ((tickCount - aviso) % QUEMA_CADA == 0) {
                quemar(nivel, (tickCount - aviso) % (QUEMA_CADA * 2) == 0);
            }
        }
    }

    private void quemar(ServerLevel nivel, boolean marca) {
        boolean linea = getTipo() == LINEA;
        Vec3 f = frente();
        double ancho = linea ? 1.6 : getTam();
        Vec3 fin = linea ? position().add(f.scale(getTam())) : position();
        AABB caja = new AABB(position(), fin).inflate(ancho + 1.0, 0.0, ancho + 1.0).expandTowards(0, 4.0, 0).move(0, -1.0, 0);
        for (LivingEntity v : nivel.getEntitiesOfClass(LivingEntity.class, caja, x -> dueno != null && dueno.esPresa(x))) {
            Vec3 d = v.position().subtract(position());
            double dist;
            if (linea) {
                double largo = Mth.clamp(d.x * f.x + d.z * f.z, 0.0, getTam());
                dist = Math.hypot(d.x - f.x * largo, d.z - f.z * largo);
            } else {
                dist = Math.hypot(d.x, d.z);
            }
            if (dist > ancho + v.getBbWidth() * 0.5 || d.y > (linea ? 3.0 : 6.0) || d.y < -1.5) {
                continue;
            }
            if (dueno.quemar(nivel, v, linea ? NovilisDanos.INFERNAL : NovilisDanos.LLAMAS, dano, marca ? 1 : 0, this)) {
                v.igniteForSeconds(3.0F);
                if (linea) {
                    // el chorro lanza hacia arriba
                    v.setDeltaMovement(v.getDeltaMovement().x * 0.5, 0.55, v.getDeltaMovement().z * 0.5);
                    v.hurtMarked = true;
                }
            }
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
        return distancia < 160 * 160;
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
