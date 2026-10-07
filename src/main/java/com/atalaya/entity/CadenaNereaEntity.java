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
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.storage.ValueInput;
import net.minecraft.world.level.storage.ValueOutput;
import net.minecraft.world.phys.Vec3;
import org.jspecify.annotations.Nullable;

/**
 * Una cadena de Encadenados (Nerea, octubre de 2026): ata a dos jugadores (o a
 * uno, si juega solo o sobra, a un ancla clavada en el suelo) durante 15 s.
 *
 * Si se separan mas de LARGO bloques, la cadena se tensa de golpe: los junta
 * de un tiron y les hace dano a los dos (como mucho una vez por segundo). Hay
 * que esquivar en pareja. La entidad va en el punto medio (para que el cliente
 * la tenga cargada) y la dibuja CadenaNereaRenderer de un extremo a otro.
 */
public class CadenaNereaEntity extends Entity {

    /** Lo que da de si la cadena (bloques) antes de tirar. */
    public static final double LARGO = 10.0;
    /** Lo que dura (ticks): 15 s. */
    public static final int VIDA = 300;
    /** Entre tiron y tiron (ticks). */
    private static final int ENTRE_TIRONES = 20;

    private static final EntityDataAccessor<Integer> DATA_A =
            SynchedEntityData.defineId(CadenaNereaEntity.class, EntityDataSerializers.INT);
    /** El otro extremo; -1 si va a un ancla clavada (DATA_ANCLA). */
    private static final EntityDataAccessor<Integer> DATA_B =
            SynchedEntityData.defineId(CadenaNereaEntity.class, EntityDataSerializers.INT);
    private static final EntityDataAccessor<BlockPos> DATA_ANCLA =
            SynchedEntityData.defineId(CadenaNereaEntity.class, EntityDataSerializers.BLOCK_POS);
    /** Lo tensa que esta: distancia entre extremos / LARGO (el cliente la pinta roja al acercarse a 1). */
    private static final EntityDataAccessor<Float> DATA_TENSION =
            SynchedEntityData.defineId(CadenaNereaEntity.class, EntityDataSerializers.FLOAT);

    private @Nullable NereaEntity duena;
    private @Nullable LivingEntity a;
    private @Nullable LivingEntity b;
    private int vida = VIDA;
    private int tiron;

    public CadenaNereaEntity(EntityType<? extends CadenaNereaEntity> tipo, Level nivel) {
        super(tipo, nivel);
        this.noPhysics = true;
        setNoGravity(true);
    }

    /** Ata a dos (b null: a un ancla clavada donde esta a). */
    public static CadenaNereaEntity atar(ServerLevel nivel, NereaEntity duena, LivingEntity a, @Nullable LivingEntity b) {
        CadenaNereaEntity c = new CadenaNereaEntity(AtalayaEntities.CADENA_NEREA, nivel);
        c.duena = duena;
        c.a = a;
        c.b = b;
        c.entityData.set(DATA_A, a.getId());
        c.entityData.set(DATA_B, b == null ? -1 : b.getId());
        c.entityData.set(DATA_ANCLA, a.blockPosition());
        Vec3 m = b == null ? a.position() : a.position().add(b.position()).scale(0.5);
        c.setPos(m.x, m.y, m.z);
        nivel.addFreshEntity(c);
        for (LivingEntity v : b == null ? new LivingEntity[]{a} : new LivingEntity[]{a, b}) {
            nivel.sendParticles(AtalayaParticulas.NEREA_GOTA, true, true, v.getX(), v.getY() + 1.0, v.getZ(), 14, 0.4, 0.5, 0.4, 0.2);
        }
        if (b == null) {
            nivel.sendParticles(AtalayaParticulas.NEREA_ESPUMA, true, true, a.getX(), a.getY() + 0.1, a.getZ(), 20, 0.6, 0.05, 0.6, 0.05);
        }
        return c;
    }

    @Override
    protected void defineSynchedData(SynchedEntityData.Builder datos) {
        datos.define(DATA_A, -1);
        datos.define(DATA_B, -1);
        datos.define(DATA_ANCLA, BlockPos.ZERO);
        datos.define(DATA_TENSION, 0.0F);
    }

    public int getIdA() {
        return entityData.get(DATA_A);
    }

    public int getIdB() {
        return entityData.get(DATA_B);
    }

    public BlockPos getAncla() {
        return entityData.get(DATA_ANCLA);
    }

    public float getTension() {
        return entityData.get(DATA_TENSION);
    }

    /** Este ser vivo esta atado a otro por esta cadena. */
    public boolean ata(Entity e) {
        return e == a || e == b;
    }

    @Override
    public void tick() {
        super.tick();
        if (level().isClientSide()) {
            return;
        }
        ServerLevel nivel = (ServerLevel) level();
        if (duena == null || duena.isRemoved() || duena.isDeadOrDying() || !vale(a) || (getIdB() >= 0 && !vale(b))
                || --vida <= 0) {
            soltar(nivel);
            return;
        }
        Vec3 pa = a.position();
        Vec3 pb = b != null ? b.position() : Vec3.atBottomCenterOf(getAncla());
        Vec3 m = pa.add(pb).scale(0.5);
        setPos(m.x, m.y, m.z);
        double d = pa.distanceTo(pb);
        float tension = (float) (d / LARGO);
        if (Math.abs(tension - getTension()) > 0.02F) {
            entityData.set(DATA_TENSION, tension);
        }
        if (tiron > 0) {
            tiron--;
        }
        if (d > LARGO && tiron <= 0) {
            tirar(nivel, pa, pb, d);
        }
    }

    /** Se tenso: los junta de un tiron y les hace dano a los dos. */
    private void tirar(ServerLevel nivel, Vec3 pa, Vec3 pb, double d) {
        tiron = ENTRE_TIRONES;
        Vec3 dir = pb.subtract(pa).scale(1.0 / Math.max(0.001, d));
        double fuerza = Math.min(2.2, 0.9 + (d - LARGO) * 0.25);
        DamageSource fuente = NereaDanos.fuente(nivel, NereaDanos.CADENA, this, duena);
        float dano = duena.dano(NereaEntity.DANO_TIRON);
        tirarDe(nivel, a, dir.scale(fuerza), fuente, dano);
        if (b != null) {
            tirarDe(nivel, b, dir.scale(-fuerza), fuente, dano);
        }
        Vec3 m = pa.add(pb).scale(0.5).add(0, 1.0, 0);
        nivel.playSound(null, m.x, m.y, m.z, AtalayaSonidos.NEREA_CADENA_TIRON, SoundSource.HOSTILE, 2.5F,
                0.9F + random.nextFloat() * 0.2F);
        for (int i = 0; i <= 8; i++) {
            Vec3 p = pa.lerp(pb, i / 8.0).add(0, 1.0, 0);
            nivel.sendParticles(AtalayaParticulas.NEREA_GOTA, true, true, p.x, p.y, p.z, 2, 0.1, 0.1, 0.1, 0.15);
        }
    }

    private static void tirarDe(ServerLevel nivel, LivingEntity v, Vec3 empuje, DamageSource fuente, float dano) {
        v.setDeltaMovement(empuje.x, 0.35, empuje.z);
        v.hurtMarked = true;
        v.hurtServer(nivel, fuente, dano);
    }

    private static boolean vale(@Nullable LivingEntity v) {
        return v != null && v.isAlive() && !v.isRemoved() && PresasJefe.presa(v);
    }

    /** Se acaba: los eslabones se deshacen en agua. */
    public void soltar(ServerLevel nivel) {
        if (isRemoved()) {
            return;
        }
        Vec3 pa = a != null ? a.position() : position();
        Vec3 pb = b != null ? b.position() : Vec3.atBottomCenterOf(getAncla());
        for (int i = 0; i <= 6; i++) {
            Vec3 p = pa.lerp(pb, i / 6.0).add(0, 1.0, 0);
            nivel.sendParticles(AtalayaParticulas.NEREA_GOTA, true, true, p.x, p.y, p.z, 3, 0.2, 0.2, 0.2, 0.05);
        }
        nivel.playSound(null, getX(), getY() + 1.0, getZ(), AtalayaSonidos.NEREA_CADENA_ROMPE, SoundSource.HOSTILE, 1.5F, 1.2F);
        discard();
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
