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
import org.jspecify.annotations.Nullable;

/**
 * Un sello de sol en el suelo: el aviso de lo que va a caer ahi.
 *
 * <ul>
 *   <li>RAYO (Castigo solar): sale bajo un jugador, justo donde esta, y al
 *       acabar la cuenta cae el rayo de su sol. Pega a quien siga dentro.</li>
 *   <li>AVISO_DIOS (Dios de la Guerra): la zona carmesi donde van a caer los
 *       soles; solo avisa, las explosiones las hace el sol al llegar.</li>
 * </ul>
 *
 * El renderer lo pinta girando y cerrandose segun la cuenta; el rayo, al final,
 * una columna de luz del cielo.
 */
public class SelloSolEntity extends Entity {

    public static final int RAYO = 0;
    public static final int AVISO_DIOS = 1;
    /** Lo que dura la columna de luz del rayo despues de caer. */
    public static final int APAGA = 10;

    private static final EntityDataAccessor<Float> DATA_RADIO =
            SynchedEntityData.defineId(SelloSolEntity.class, EntityDataSerializers.FLOAT);
    private static final EntityDataAccessor<Integer> DATA_DURA =
            SynchedEntityData.defineId(SelloSolEntity.class, EntityDataSerializers.INT);
    private static final EntityDataAccessor<Integer> DATA_TIPO =
            SynchedEntityData.defineId(SelloSolEntity.class, EntityDataSerializers.INT);
    /** Fase del dueno (el color: ambar, oro, blanco, carmesi); 5 la Furia. */
    private static final EntityDataAccessor<Integer> DATA_COLOR =
            SynchedEntityData.defineId(SelloSolEntity.class, EntityDataSerializers.INT);

    private @Nullable NovilisEntity dueno;
    private float dano;

    public SelloSolEntity(EntityType<? extends SelloSolEntity> tipo, Level nivel) {
        super(tipo, nivel);
        this.noPhysics = true;
        setNoGravity(true);
    }

    public static SelloSolEntity poner(ServerLevel nivel, NovilisEntity dueno, net.minecraft.world.phys.Vec3 donde, float radio,
                                       int dura, int tipo, float dano, int fase) {
        SelloSolEntity s = new SelloSolEntity(AtalayaEntities.SELLO_SOL, nivel);
        s.dueno = dueno;
        s.dano = dano;
        s.entityData.set(DATA_RADIO, radio);
        s.entityData.set(DATA_DURA, Math.max(1, dura));
        s.entityData.set(DATA_TIPO, tipo);
        s.entityData.set(DATA_COLOR, dueno.tieneFuria() && tipo == RAYO ? 5 : fase);
        s.setPos(donde.x, donde.y, donde.z);
        nivel.addFreshEntity(s);
        return s;
    }

    @Override
    protected void defineSynchedData(SynchedEntityData.Builder datos) {
        datos.define(DATA_RADIO, 2.6F);
        datos.define(DATA_DURA, 24);
        datos.define(DATA_TIPO, RAYO);
        datos.define(DATA_COLOR, 1);
    }

    public float getRadio() {
        return entityData.get(DATA_RADIO);
    }

    public int getDura() {
        return entityData.get(DATA_DURA);
    }

    public int getTipo() {
        return entityData.get(DATA_TIPO);
    }

    public int getColor() {
        return entityData.get(DATA_COLOR);
    }

    @Override
    public void tick() {
        super.tick();
        int dura = getDura();
        if (level().isClientSide()) {
            if (getTipo() == RAYO && tickCount < dura && tickCount % 3 == 0) {
                double a = random.nextDouble() * Math.PI * 2;
                double r = getRadio() * (0.9 + random.nextDouble() * 0.1);
                level().addParticle(AtalayaParticulas.NOVILIS_BRASA, getX() + Math.cos(a) * r, getY() + 0.1,
                        getZ() + Math.sin(a) * r, 0, 0.06, 0);
            }
            return;
        }
        if (dueno == null || dueno.isRemoved()) {
            discard();
            return;
        }
        ServerLevel nivel = (ServerLevel) level();
        if (getTipo() == RAYO && tickCount == dura) {
            caer(nivel);
        }
        if (tickCount >= dura + (getTipo() == RAYO ? APAGA : 0)) {
            discard();
        }
    }

    /** Cae el rayo: a quien siga en el sello, el golpe y un nivel de quemadura. */
    private void caer(ServerLevel nivel) {
        float r = getRadio();
        nivel.playSound(null, getX(), getY(), getZ(), AtalayaSonidos.NOVILIS_CASTIGO_RAYO, SoundSource.HOSTILE, 4.0F,
                0.9F + random.nextFloat() * 0.2F);
        nivel.sendParticles(AtalayaParticulas.NOVILIS_LLAMA, true, true, getX(), getY() + 0.5, getZ(), 30, r * 0.4, 0.4, r * 0.4, 0.15);
        nivel.sendParticles(AtalayaParticulas.NOVILIS_CHISPA, true, true, getX(), getY() + 1.0, getZ(), 24, r * 0.3, 1.0, r * 0.3, 0.4);
        nivel.sendParticles(AtalayaParticulas.NOVILIS_ONDA, true, true, getX(), getY() + 0.12, getZ(), 0, 0.8, r * 1.6, 0.0, 1.0);
        AABB caja = new AABB(getX() - r, getY() - 1, getZ() - r, getX() + r, getY() + 4, getZ() + r);
        for (LivingEntity v : nivel.getEntitiesOfClass(LivingEntity.class, caja, x -> dueno != null && dueno.esPresa(x))) {
            double dx = v.getX() - getX();
            double dz = v.getZ() - getZ();
            if (dx * dx + dz * dz > (r + v.getBbWidth() / 2) * (r + v.getBbWidth() / 2)) {
                continue;
            }
            dueno.quemar(nivel, v, NovilisDanos.RAYO, dano, 1, this);
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
