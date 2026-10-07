package com.atalaya.entity;

import com.atalaya.particula.AtalayaParticulas;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerLevel;
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

import java.util.HashSet;
import java.util.Set;
import java.util.UUID;

/**
 * La onda de fuego del Castigo solar: un anillo de llamas que sale de donde
 * clava la espada y corre por el suelo. Se salta: solo quema a quien pilla con
 * los pies en el suelo al pasar (y un nivel de quemadura).
 *
 * Tambien es el pulso de los angeles de las Trompetas (lanzarPulso): un anillo
 * corto que sale de los pies del angel por su estrado cada 5 s y tira abajo a
 * quien este encima (empuja mas, apenas hace dano y no quema). Se salta igual.
 *
 * El radio sale de la edad en los dos lados: no hace falta mandarlo.
 */
public class OndaFuegoEntity extends Entity {

    /** Lo alto que son las llamas del anillo. */
    public static final float ALTO = 1.9F;

    private static final EntityDataAccessor<Float> DATA_MAX =
            SynchedEntityData.defineId(OndaFuegoEntity.class, EntityDataSerializers.FLOAT);
    private static final EntityDataAccessor<Float> DATA_VEL =
            SynchedEntityData.defineId(OndaFuegoEntity.class, EntityDataSerializers.FLOAT);
    private static final EntityDataAccessor<Integer> DATA_COLOR =
            SynchedEntityData.defineId(OndaFuegoEntity.class, EntityDataSerializers.INT);

    private @Nullable NovilisEntity dueno;
    private float dano;
    /** El pulso de los angeles: empuja mas, sin quemadura ni fuego. */
    private boolean pulso;
    private final Set<UUID> golpeados = new HashSet<>();

    public OndaFuegoEntity(EntityType<? extends OndaFuegoEntity> tipo, Level nivel) {
        super(tipo, nivel);
        this.noPhysics = true;
        setNoGravity(true);
    }

    public static OndaFuegoEntity lanzar(ServerLevel nivel, NovilisEntity dueno, Vec3 centro, float max, float vel, float dano,
                                         int fase) {
        OndaFuegoEntity o = new OndaFuegoEntity(AtalayaEntities.ONDA_FUEGO, nivel);
        o.dueno = dueno;
        o.dano = dano;
        o.entityData.set(DATA_MAX, max);
        o.entityData.set(DATA_VEL, vel);
        o.entityData.set(DATA_COLOR, dueno.tieneFuria() ? 5 : fase);
        o.setPos(centro.x, centro.y, centro.z);
        nivel.addFreshEntity(o);
        return o;
    }

    /** El pulso de un angel de las Trompetas: corto, rapido y para tirar del estrado. */
    public static OndaFuegoEntity lanzarPulso(ServerLevel nivel, NovilisEntity dueno, Vec3 centro, float max, float dano,
                                              int fase) {
        OndaFuegoEntity o = lanzar(nivel, dueno, centro, max, 0.7F, dano, fase);
        o.pulso = true;
        return o;
    }

    @Override
    protected void defineSynchedData(SynchedEntityData.Builder datos) {
        datos.define(DATA_MAX, 26.0F);
        datos.define(DATA_VEL, 0.9F);
        datos.define(DATA_COLOR, 1);
    }

    public float getMax() {
        return entityData.get(DATA_MAX);
    }

    public int getColor() {
        return entityData.get(DATA_COLOR);
    }

    public float radio(float edad) {
        return Math.min(getMax(), edad * entityData.get(DATA_VEL));
    }

    /** Ticks hasta llegar al final. */
    public float viaje() {
        return getMax() / Math.max(0.01F, entityData.get(DATA_VEL));
    }

    @Override
    public void tick() {
        super.tick();
        float r = radio(tickCount);
        if (level().isClientSide()) {
            if (tickCount <= viaje()) {
                int n = 4 + (int) (r / 4);
                for (int i = 0; i < n; i++) {
                    double a = random.nextDouble() * Math.PI * 2;
                    level().addParticle(random.nextInt(3) == 0 ? AtalayaParticulas.NOVILIS_CHISPA : AtalayaParticulas.NOVILIS_LLAMA,
                            getX() + Math.cos(a) * r, getY() + 0.2 + random.nextDouble() * ALTO, getZ() + Math.sin(a) * r,
                            Math.cos(a) * 0.1, 0.08, Math.sin(a) * 0.1);
                }
            }
            return;
        }
        if (dueno == null || dueno.isRemoved()) {
            discard();
            return;
        }
        if (tickCount <= viaje()) {
            golpear((ServerLevel) level(), radio(tickCount - 1) - 0.8F, r + 0.8F);
        }
        if (tickCount > viaje() + 8) {
            discard();
        }
    }

    private void golpear(ServerLevel nivel, float desde, float hasta) {
        AABB caja = new AABB(getX() - hasta, getY() - 1, getZ() - hasta, getX() + hasta, getY() + ALTO, getZ() + hasta);
        for (LivingEntity v : nivel.getEntitiesOfClass(LivingEntity.class, caja, x -> dueno != null && dueno.esPresa(x))) {
            if (golpeados.contains(v.getUUID())) {
                continue;
            }
            double dx = v.getX() - getX();
            double dz = v.getZ() - getZ();
            double d = Math.sqrt(dx * dx + dz * dz);
            // Solo a quien esta en el suelo: saltandola, pasa por debajo.
            double dy = v.getY() - getY();
            if (d < desde || d > hasta || dy > 1.0 || dy < -1.5) {
                continue;
            }
            golpeados.add(v.getUUID());
            Vec3 fuera = d < 1.0E-3 ? new Vec3(1, 0, 0) : new Vec3(dx, 0, dz).normalize();
            if (pulso) {
                // Del estrado abajo: unos 7 bloques hacia fuera, entre o no el dano.
                dueno.quemar(nivel, v, NovilisDanos.ONDA, dano, 0, this);
                v.setDeltaMovement(fuera.x * 0.7, 0.45, fuera.z * 0.7);
                v.hurtMarked = true;
            } else if (dueno.quemar(nivel, v, NovilisDanos.ONDA, dano, 1, this)) {
                v.setDeltaMovement(fuera.x * 0.8, 0.55, fuera.z * 0.8);
                v.hurtMarked = true;
                v.igniteForSeconds(3.0F);
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
