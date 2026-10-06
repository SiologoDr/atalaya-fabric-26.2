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
 * Un Geiser del Abismo (desde la fase II): Nerea clava el tridente y bajo los
 * pies de cada uno se abre un remolino oscuro que burbujea. A los 1,5 s
 * revienta una columna de agua de catorce bloques: a quien siga encima lo
 * golpea y lo lanza unos doce bloques al cielo (y la caida duele). Basta con
 * salir del remolino a tiempo.
 *
 * Lo dibuja GeiserNereaRenderer: el remolino del aviso, la columna y el aro de
 * espuma del suelo.
 */
public class GeiserNereaEntity extends Entity {

    /** Ticks de aviso (el remolino) y ticks que dura la columna. */
    public static final int AVISO = 30;
    public static final int CHORRO = 18;
    /** Lo que alcanza (bloques desde el centro) y el alto de la columna. */
    public static final float RADIO = 2.2F;
    public static final float ALTO = 14.0F;
    /** La velocidad hacia arriba con que lanza: unos doce bloques. */
    private static final double LANZA = 1.75;
    /** Ticks del reventon en que aun pilla a quien se meta. */
    private static final int PILLA = 4;

    private static final EntityDataAccessor<Integer> DATA_FASE =
            SynchedEntityData.defineId(GeiserNereaEntity.class, EntityDataSerializers.INT);

    private @Nullable NereaEntity duena;
    private float dano;
    private final Set<UUID> golpeados = new HashSet<>();

    public GeiserNereaEntity(EntityType<? extends GeiserNereaEntity> tipo, Level nivel) {
        super(tipo, nivel);
        this.noPhysics = true;
        setNoGravity(true);
    }

    public static GeiserNereaEntity brotar(ServerLevel nivel, NereaEntity duena, Vec3 donde, float dano, int fase) {
        GeiserNereaEntity g = new GeiserNereaEntity(AtalayaEntities.GEISER_NEREA, nivel);
        g.duena = duena;
        g.dano = dano;
        g.entityData.set(DATA_FASE, fase);
        g.setPos(donde.x, donde.y, donde.z);
        nivel.addFreshEntity(g);
        nivel.playSound(null, donde.x, donde.y, donde.z, AtalayaSonidos.NEREA_GEISER_AVISO, SoundSource.HOSTILE, 1.6F,
                0.9F + nivel.getRandom().nextFloat() * 0.2F);
        return g;
    }

    @Override
    protected void defineSynchedData(SynchedEntityData.Builder datos) {
        datos.define(DATA_FASE, 1);
    }

    public int getFase() {
        return entityData.get(DATA_FASE);
    }

    @Override
    public void tick() {
        super.tick();
        if (level().isClientSide()) {
            particulas();
            return;
        }
        if (duena == null || duena.isRemoved()) {
            discard();
            return;
        }
        ServerLevel nivel = (ServerLevel) level();
        if (tickCount == AVISO) {
            nivel.playSound(null, getX(), getY(), getZ(), AtalayaSonidos.NEREA_GEISER, SoundSource.HOSTILE, 3.0F,
                    0.9F + random.nextFloat() * 0.2F);
            nivel.sendParticles(AtalayaParticulas.NEREA_ONDA, true, true, getX(), getY() + 0.12, getZ(), 0, 1.4, RADIO + 2.5, 0.0, 1.0);
            nivel.sendParticles(AtalayaParticulas.NEREA_ESPUMA, true, true, getX(), getY() + 1.0, getZ(), 30, 0.8, 1.2, 0.8, 0.15);
            nivel.sendParticles(AtalayaParticulas.NEREA_ROCA, true, true, getX(), getY() + 0.3, getZ(), 10, 0.6, 0.2, 0.6, 0.35);
        }
        if (tickCount >= AVISO && tickCount < AVISO + PILLA) {
            golpear(nivel);
        }
        if (tickCount >= AVISO + CHORRO + 10) {
            discard();
        }
    }

    /** Burbujas que suben en el remolino mientras avisa; agua que cae mientras sale el chorro. */
    private void particulas() {
        if (tickCount < AVISO) {
            int n = 1 + tickCount / 10;
            for (int i = 0; i < n; i++) {
                double a = random.nextDouble() * Math.PI * 2;
                double r = Math.sqrt(random.nextDouble()) * RADIO;
                level().addParticle(AtalayaParticulas.NEREA_BURBUJA, getX() + Math.cos(a) * r, getY() + 0.1,
                        getZ() + Math.sin(a) * r, 0, 0.06 + random.nextDouble() * 0.05, 0);
            }
            return;
        }
        if (tickCount < AVISO + CHORRO) {
            for (int i = 0; i < 4; i++) {
                double a = random.nextDouble() * Math.PI * 2;
                level().addParticle(AtalayaParticulas.NEREA_GOTA, getX() + Math.cos(a) * 0.8, getY() + ALTO * 0.95,
                        getZ() + Math.sin(a) * 0.8, Math.cos(a) * 0.25, 0.1, Math.sin(a) * 0.25);
            }
            if (random.nextInt(2) == 0) {
                level().addParticle(AtalayaParticulas.NEREA_ESPUMA, getX() + random.nextGaussian() * 0.6, getY() + 0.3,
                        getZ() + random.nextGaussian() * 0.6, random.nextGaussian() * 0.12, 0.05, random.nextGaussian() * 0.12);
            }
        }
    }

    /** Lo que siga encima del remolino sale volando. */
    private void golpear(ServerLevel nivel) {
        AABB caja = new AABB(getX() - RADIO - 1, getY() - 1.0, getZ() - RADIO - 1, getX() + RADIO + 1, getY() + 4.0, getZ() + RADIO + 1);
        DamageSource fuente = NereaDanos.fuente(nivel, NereaDanos.GEISER, this, duena);
        for (LivingEntity v : nivel.getEntitiesOfClass(LivingEntity.class, caja, x -> duena != null && duena.esPresa(x))) {
            double dx = v.getX() - getX();
            double dz = v.getZ() - getZ();
            if (golpeados.contains(v.getUUID()) || Math.sqrt(dx * dx + dz * dz) > RADIO + v.getBbWidth() / 2) {
                continue;
            }
            golpeados.add(v.getUUID());
            v.hurtServer(nivel, fuente, dano);
            // Sin quitarle la caida que ya llevara: al bajar, duele.
            v.setDeltaMovement(v.getDeltaMovement().x * 0.3, LANZA, v.getDeltaMovement().z * 0.3);
            v.hurtMarked = true;
            nivel.sendParticles(AtalayaParticulas.NEREA_GOTA, true, true, v.getX(), v.getY() + 0.5, v.getZ(), 14, 0.4, 0.4, 0.4, 0.35);
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
