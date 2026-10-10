package com.atalaya.entity;

import com.atalaya.particula.AtalayaParticulas;
import com.atalaya.sonido.AtalayaSonidos;
import net.minecraft.core.BlockPos;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityDimensions;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.Pose;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.storage.ValueInput;
import net.minecraft.world.level.storage.ValueOutput;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;
import org.jspecify.annotations.Nullable;

/**
 * Una brasa enterrada de Frio o Caliente: no se ve hasta que alguien golpea el
 * suelo justo encima (a RADIO_HALLAR); entonces la tierra se raja, brilla y la
 * brasa sale chisporroteando. Si se acaba el tiempo, revienta en lava donde
 * estaba. El termometro de cada uno (TermometroHud) mide lo lejos que esta la
 * mas cercana.
 */
public class BrasaEnterradaEntity extends Entity {

    /** Lo cerca que hay que golpear el suelo (bloques, en horizontal) para sacarla. */
    public static final double RADIO_HALLAR = 1.8;
    /** Lo que se queda la grieta brillando tras sacarla y lo que dura el reventon. */
    public static final int HALLADA_DURA = 40;
    public static final int REVIENTA_DURA = 30;
    /** El reventon: su radio. */
    private static final double RADIO_REVIENTA = 4.0;

    /** Tick en que la sacaron (-1: sigue enterrada). */
    private static final EntityDataAccessor<Integer> DATA_HALLADA =
            SynchedEntityData.defineId(BrasaEnterradaEntity.class, EntityDataSerializers.INT);
    /** Tick en que revento (-1: no). */
    private static final EntityDataAccessor<Integer> DATA_REVIENTA =
            SynchedEntityData.defineId(BrasaEnterradaEntity.class, EntityDataSerializers.INT);

    private @Nullable CalienteNovilis juego;

    public BrasaEnterradaEntity(EntityType<? extends BrasaEnterradaEntity> tipo, Level nivel) {
        super(tipo, nivel);
        this.noPhysics = true;
        setNoGravity(true);
    }

    static BrasaEnterradaEntity enterrar(ServerLevel nivel, CalienteNovilis juego, Vec3 donde) {
        BrasaEnterradaEntity b = new BrasaEnterradaEntity(AtalayaEntities.BRASA_ENTERRADA, nivel);
        b.juego = juego;
        b.snapTo(donde.x, donde.y, donde.z, nivel.getRandom().nextFloat() * 360.0F, 0.0F);
        nivel.addFreshEntity(b);
        return b;
    }

    @Override
    protected void defineSynchedData(SynchedEntityData.Builder datos) {
        datos.define(DATA_HALLADA, -1);
        datos.define(DATA_REVIENTA, -1);
    }

    public int getHallada() {
        return entityData.get(DATA_HALLADA);
    }

    public int getRevienta() {
        return entityData.get(DATA_REVIENTA);
    }

    /** Sigue enterrada (la busca el termometro). */
    public boolean enterrada() {
        return getHallada() < 0 && getRevienta() < 0;
    }

    @Override
    public EntityDimensions getDimensions(Pose pose) {
        return EntityDimensions.fixed(0.5F, 0.2F);
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
    public boolean hurtServer(ServerLevel nivel, DamageSource fuente, float cantidad) {
        return false;
    }

    /**
     * Alguien golpea un bloque: si hay una brasa enterrada justo debajo (o al
     * lado), sale. En el cliente solo dice si la hay (para no romper el bloque).
     */
    public static boolean alGolpearBloque(Player p, Level nivel, BlockPos pos) {
        Vec3 c = Vec3.atCenterOf(pos);
        BrasaEnterradaEntity mejor = null;
        double d = RADIO_HALLAR * RADIO_HALLAR;
        for (BrasaEnterradaEntity b : nivel.getEntitiesOfClass(BrasaEnterradaEntity.class, new AABB(pos).inflate(3.0),
                BrasaEnterradaEntity::enterrada)) {
            double dx = b.getX() - c.x;
            double dz = b.getZ() - c.z;
            double dd = dx * dx + dz * dz;
            if (dd <= d && Math.abs(b.getY() - (pos.getY() + 1.0)) <= 2.5) {
                d = dd;
                mejor = b;
            }
        }
        if (mejor == null) {
            return false;
        }
        if (nivel instanceof ServerLevel servidor) {
            mejor.hallar(servidor, p);
        }
        return true;
    }

    /** La sacan: la tierra se raja, brilla y la brasa sale chisporroteando. */
    void hallar(ServerLevel nivel, Player p) {
        if (!enterrada() || juego == null) {
            return;
        }
        entityData.set(DATA_HALLADA, tickCount);
        nivel.playSound(null, getX(), getY() + 0.5, getZ(), AtalayaSonidos.NOVILIS_CALIENTE_HALLADA, SoundSource.PLAYERS, 3.0F, 1.0F);
        nivel.sendParticles(AtalayaParticulas.NOVILIS_BRASA, true, true, getX(), getY() + 0.3, getZ(), 40, 0.5, 0.3, 0.5, 0.08);
        nivel.sendParticles(AtalayaParticulas.NOVILIS_CHISPA, true, true, getX(), getY() + 0.3, getZ(), 30, 0.4, 0.2, 0.4, 0.3);
        nivel.sendParticles(AtalayaParticulas.NOVILIS_LUZ, true, true, getX(), getY() + 1.0, getZ(), 20, 0.3, 0.8, 0.3, 0.05);
        nivel.sendParticles(AtalayaParticulas.NOVILIS_ROCA, true, true, getX(), getY() + 0.3, getZ(), 10, 0.5, 0.2, 0.5, 0.2);
        juego.alHallar(nivel, this, p);
    }

    /** Se acabo el tiempo: revienta en lava donde estaba. */
    void reventar(ServerLevel nivel, NovilisEntity n) {
        if (!enterrada()) {
            return;
        }
        entityData.set(DATA_REVIENTA, tickCount);
        nivel.playSound(null, getX(), getY() + 0.5, getZ(), AtalayaSonidos.NOVILIS_CALIENTE_REVIENTA, SoundSource.HOSTILE, 5.0F, 1.0F);
        nivel.sendParticles(AtalayaParticulas.NOVILIS_LLAMA, true, true, getX(), getY() + 0.5, getZ(), 60, 1.2, 1.5, 1.2, 0.12);
        nivel.sendParticles(AtalayaParticulas.NOVILIS_ROCA, true, true, getX(), getY() + 0.3, getZ(), 24, 0.8, 0.3, 0.8, 0.4);
        nivel.sendParticles(AtalayaParticulas.NOVILIS_ONDA, true, true, getX(), getY() + 0.12, getZ(), 0, 1.4, RADIO_REVIENTA * 1.5, 0.0, 1.0);
        for (var v : n.presasMini(nivel, 64)) {
            if (v.distanceToSqr(this) < RADIO_REVIENTA * RADIO_REVIENTA) {
                n.quemar(nivel, v, NovilisDanos.INFERNAL, n.dano(NovilisEntity.DANO_GEISER) * 1.5F, 2, this);
            }
        }
    }

    /** Lo deja sin juego: se va sin mas (un corte). */
    void soltar() {
        juego = null;
    }

    @Override
    public void tick() {
        super.tick();
        if (level().isClientSide()) {
            int h = getHallada();
            if (h >= 0 && tickCount - h < HALLADA_DURA && random.nextInt(2) == 0) {
                level().addParticle(AtalayaParticulas.NOVILIS_BRASA, getX() + (random.nextDouble() - 0.5), getY() + 0.2,
                        getZ() + (random.nextDouble() - 0.5), 0, 0.06, 0);
            }
            return;
        }
        int h = getHallada();
        int r = getRevienta();
        if ((juego == null && enterrada()) || (h >= 0 && tickCount - h > HALLADA_DURA) || (r >= 0 && tickCount - r > REVIENTA_DURA)) {
            discard();
        }
    }

    @Override
    public boolean shouldBeSaved() {
        return false;
    }

    @Override
    public boolean shouldRenderAtSqrDistance(double distancia) {
        return distancia < 96 * 96;
    }

    @Override
    protected void readAdditionalSaveData(ValueInput entrada) {
    }

    @Override
    protected void addAdditionalSaveData(ValueOutput salida) {
    }
}
