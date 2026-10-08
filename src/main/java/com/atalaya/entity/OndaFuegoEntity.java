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
 * Tambien es el pulso de los angeles de las Trompetas (lanzarPulso): cada 5 s
 * baja por los cinco escalones de su estrado, un cuadro de llamas por escalon
 * que corre por su pisada, y a quien este subiendo lo expulsa dos o tres
 * bloques hacia fuera (08-10-2026, Juan: "va a expulsar 2 a 3 bloques"); apenas
 * hace dano y no quema. Se salta igual.
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
    /** El pulso de un escalon: cuadrado (como el escalon) y desde donde empieza su pisada. */
    private static final EntityDataAccessor<Boolean> DATA_CUADRO =
            SynchedEntityData.defineId(OndaFuegoEntity.class, EntityDataSerializers.BOOLEAN);
    private static final EntityDataAccessor<Float> DATA_DESDE =
            SynchedEntityData.defineId(OndaFuegoEntity.class, EntityDataSerializers.FLOAT);
    /** Lo alto de las llamas del pulso. */
    public static final float ALTO_PULSO = 1.2F;
    /** Lo rapido que baja el pulso por el estrado (bloques por tick). */
    private static final float VEL_PULSO = 0.45F;

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

    /**
     * El pulso de un angel de las Trompetas en uno de sus escalones (a la altura
     * de su pisada): un cuadro de llamas que crece desde el centro del estrado y
     * se ve y golpea solo por la pisada, de desde (el borde del escalon de
     * encima) a max (el suyo). Todos salen a la vez: como el de abajo tiene mas
     * camino, el fuego baja escalon a escalon.
     */
    public static OndaFuegoEntity lanzarPulso(ServerLevel nivel, NovilisEntity dueno, Vec3 centro, float desde, float max,
                                              float dano, int fase) {
        OndaFuegoEntity o = lanzar(nivel, dueno, centro, max, VEL_PULSO, dano, fase);
        o.pulso = true;
        o.entityData.set(DATA_CUADRO, true);
        o.entityData.set(DATA_DESDE, desde);
        return o;
    }

    @Override
    protected void defineSynchedData(SynchedEntityData.Builder datos) {
        datos.define(DATA_MAX, 26.0F);
        datos.define(DATA_VEL, 0.9F);
        datos.define(DATA_COLOR, 1);
        datos.define(DATA_CUADRO, false);
        datos.define(DATA_DESDE, 0.0F);
    }

    public boolean esCuadro() {
        return entityData.get(DATA_CUADRO);
    }

    public float getDesde() {
        return entityData.get(DATA_DESDE);
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
            if (esCuadro()) {
                // El pulso: chispas por el frente del cuadro, solo por su pisada.
                if (tickCount <= viaje() && r >= getDesde()) {
                    for (int i = 0; i < 3; i++) {
                        double t = random.nextDouble() * 2.0 - 1.0;
                        double x = random.nextBoolean() ? r : -r;
                        double z = t * r;
                        if (random.nextBoolean()) {
                            double c = x;
                            x = z;
                            z = c;
                        }
                        level().addParticle(AtalayaParticulas.NOVILIS_CHISPA, getX() + x, getY() + 0.2 + random.nextDouble() * ALTO_PULSO,
                                getZ() + z, Math.signum(x) * 0.05, 0.08, Math.signum(z) * 0.05);
                    }
                }
                return;
            }
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
            double dy = v.getY() - getY();
            if (pulso) {
                // El pulso de un escalon: en cuadro y solo a quien pisa este escalon (saltandolo a
                // tiempo, pasa por debajo; los de los otros escalones los pilla su propio cuadro).
                double d = Math.max(Math.abs(dx), Math.abs(dz));
                if (d < desde || d > hasta || d < getDesde() - 0.3 || d > getMax() + 0.4 || dy > 0.9 || dy < -0.4) {
                    continue;
                }
                golpeados.add(v.getUUID());
                // Hacia fuera, por el lado del escalon en que esta: dos o tres bloques, escalones abajo.
                Vec3 fuera = Math.abs(dx) >= Math.abs(dz) ? new Vec3(Math.signum(dx), 0, 0) : new Vec3(0, 0, Math.signum(dz));
                dueno.quemar(nivel, v, NovilisDanos.ONDA, dano, 0, this);
                v.setDeltaMovement(fuera.x * 0.5, 0.34, fuera.z * 0.5);
                v.hurtMarked = true;
                continue;
            }
            double d = Math.sqrt(dx * dx + dz * dz);
            // Solo a quien esta en el suelo: saltandola, pasa por debajo.
            if (d < desde || d > hasta || dy > 1.0 || dy < -1.5) {
                continue;
            }
            golpeados.add(v.getUUID());
            Vec3 fuera = d < 1.0E-3 ? new Vec3(1, 0, 0) : new Vec3(dx, 0, dz).normalize();
            if (dueno.quemar(nivel, v, NovilisDanos.ONDA, dano, 1, this)) {
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
