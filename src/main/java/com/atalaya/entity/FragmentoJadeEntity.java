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

/**
 * Un fragmento de jade del Cataclismo: un racimo de cristales envuelto en llama
 * verde que cae del cielo rajado sobre su marca (la marca avisa 1,5 s antes, con la
 * cuenta atras en su aro). Cae en linea recta, algo inclinado, y llega justo
 * cuando la cuenta se cierra.
 *
 * Encima del impacto, la muerte (el totem de la inmortalidad aun salva); cerca,
 * hasta 12 bloques, el dano de la fase (de la mitad al todo) y el empujon.
 * Despues se queda clavado, brillando, hasta que se apaga.
 *
 * Desde octubre de 2026 son mas grandes (tamano 2,3 a 2,7) y caen menos: la
 * muerte llega a 4,8-5,7 bloques del impacto en vez de 2 (los 3,3-4 de la primera
 * version, y luego 4-4,8, se quedaron cortos al verlos en el juego).
 */
public class FragmentoJadeEntity extends Entity {

    /** Desde donde cae (bloques por encima y hacia atras de la marca). */
    public static final Vec3 DESDE = new Vec3(-9.0, 40.0, 7.0);
    public static final int CLAVADO = 60;
    /** La muerte llega a 2,1 bloques por cada punto de tamano: de 4,8 a 5,7 bloques. */
    private static final double MUERTE = 2.1;
    private static final double CERCA = 12.0;

    /** Hasta donde mata un fragmento de tamano 'tam' (para dibujar su marca a juego). */
    public static double radioMuerte(float tam) {
        return MUERTE * tam;
    }

    private static final EntityDataAccessor<Float> DATA_TAM =
            SynchedEntityData.defineId(FragmentoJadeEntity.class, EntityDataSerializers.FLOAT);
    private static final EntityDataAccessor<Integer> DATA_CAIDA =
            SynchedEntityData.defineId(FragmentoJadeEntity.class, EntityDataSerializers.INT);
    private static final EntityDataAccessor<Integer> DATA_SEMILLA =
            SynchedEntityData.defineId(FragmentoJadeEntity.class, EntityDataSerializers.INT);

    private @Nullable RajangEntity dueno;
    private float dano;
    private Vec3 marca = Vec3.ZERO;

    public FragmentoJadeEntity(EntityType<? extends FragmentoJadeEntity> tipo, Level nivel) {
        super(tipo, nivel);
        this.noPhysics = true;
        setNoGravity(true);
    }

    public static FragmentoJadeEntity caer(ServerLevel nivel, RajangEntity dueno, Vec3 marca, int caida, float tam, float dano) {
        FragmentoJadeEntity f = new FragmentoJadeEntity(AtalayaEntities.FRAGMENTO_JADE, nivel);
        f.dueno = dueno;
        f.dano = dano;
        f.marca = marca;
        f.entityData.set(DATA_TAM, tam);
        f.entityData.set(DATA_CAIDA, caida);
        f.entityData.set(DATA_SEMILLA, nivel.getRandom().nextInt());
        Vec3 desde = marca.add(DESDE);
        f.setPos(desde.x, desde.y, desde.z);
        f.setDeltaMovement(marca.subtract(desde).scale(1.0 / caida));
        nivel.addFreshEntity(f);
        nivel.playSound(null, marca.x, marca.y + 6, marca.z, AtalayaSonidos.RAJANG_FRAGMENTO, SoundSource.HOSTILE, 4.0F,
                0.9F + nivel.getRandom().nextFloat() * 0.2F);
        return f;
    }

    @Override
    protected void defineSynchedData(SynchedEntityData.Builder datos) {
        datos.define(DATA_TAM, 1.0F);
        datos.define(DATA_CAIDA, 30);
        datos.define(DATA_SEMILLA, 0);
    }

    public float getTam() {
        return entityData.get(DATA_TAM);
    }

    public int getCaida() {
        return entityData.get(DATA_CAIDA);
    }

    public int getSemilla() {
        return entityData.get(DATA_SEMILLA);
    }

    /** Ya ha caido y esta clavado en el suelo. */
    public boolean isClavado() {
        return tickCount >= getCaida();
    }

    @Override
    public void tick() {
        super.tick();
        int caida = getCaida();
        if (tickCount < caida) {
            Vec3 v = getDeltaMovement();
            setPos(getX() + v.x, getY() + v.y, getZ() + v.z);
            if (level().isClientSide()) {
                // La llama que se queda atras y alguna chispa.
                float tam = getTam();
                for (int i = 0; i < 3; i++) {
                    double k = random.nextDouble();
                    level().addParticle(AtalayaParticulas.RAJANG_LLAMA, getX() - v.x * k + random.nextGaussian() * 0.35 * tam,
                            getY() - v.y * k + random.nextGaussian() * 0.35 * tam, getZ() - v.z * k + random.nextGaussian() * 0.35 * tam,
                            -v.x * 0.12, -v.y * 0.12, -v.z * 0.12);
                }
                if (random.nextInt(2) == 0) {
                    level().addParticle(AtalayaParticulas.RAJANG_CHISPA, getX(), getY(), getZ(), random.nextGaussian() * 0.12,
                            random.nextGaussian() * 0.12, random.nextGaussian() * 0.12);
                }
            }
            return;
        }
        if (level().isClientSide()) {
            if (tickCount % 4 == 0) {
                level().addParticle(AtalayaParticulas.RAJANG_CHISPA, getX() + random.nextGaussian() * 0.4, getY() + 0.5,
                        getZ() + random.nextGaussian() * 0.4, 0, 0.04, 0);
            }
            return;
        }
        if (tickCount == caida) {
            setDeltaMovement(Vec3.ZERO);
            impactar((ServerLevel) level());
        }
        if (tickCount > caida + CLAVADO) {
            discard();
        }
    }

    private void impactar(ServerLevel nivel) {
        float tam = getTam();
        Vec3 p = position();
        nivel.playSound(null, p.x, p.y, p.z, AtalayaSonidos.RAJANG_IMPACTO, SoundSource.HOSTILE, 4.0F + 2.0F * tam,
                0.9F + nivel.getRandom().nextFloat() * 0.2F);
        nivel.sendParticles(AtalayaParticulas.RAJANG_ONDA, true, true, p.x, p.y + 0.12, p.z, 0, 1.2 * tam, 7.0, 0.0, 1.0);
        nivel.sendParticles(AtalayaParticulas.RAJANG_JADE, true, true, p.x, p.y + 0.5, p.z, (int) (20 * tam), 0.6, 0.4, 0.6, 0.35);
        nivel.sendParticles(AtalayaParticulas.RAJANG_LLAMA, true, true, p.x, p.y + 0.5, p.z, (int) (24 * tam), 0.8, 0.4, 0.8, 0.12);
        nivel.sendParticles(AtalayaParticulas.RAJANG_ROCA, true, true, p.x, p.y + 0.5, p.z, (int) (16 * tam), 0.8, 0.3, 0.8, 0.3);
        nivel.sendParticles(AtalayaParticulas.RAJANG_POLVO, true, true, p.x, p.y + 0.4, p.z, (int) (20 * tam), 1.6, 0.4, 1.6, 0.05);
        for (int k = 0; k < 5; k++) {
            double a = Math.PI * 2 * k / 5 + nivel.getRandom().nextDouble() * 0.6;
            nivel.sendParticles(AtalayaParticulas.RAJANG_GRIETA, true, true, p.x + Math.cos(a) * 1.4, p.y + 0.06, p.z + Math.sin(a) * 1.4,
                    0, 1.4, 100.0, 0.0, 1.0);
        }
        if (dueno == null) {
            return;
        }
        DamageSource muerte = RajangDanos.fuente(nivel, RajangDanos.FRAGMENTO, this, dueno);
        DamageSource cerca = RajangDanos.fuente(nivel, RajangDanos.IMPACTO, this, dueno);
        for (LivingEntity v : nivel.getEntitiesOfClass(LivingEntity.class, new AABB(p, p).inflate(CERCA, 4, CERCA), dueno::esPresa)) {
            double d = RajangEntity.horizontal(p, v.position());
            if (d <= radioMuerte(tam) && Math.abs(v.getY() - p.y) < 3.5) {
                v.hurtServer(nivel, muerte, 10000.0F);
                if (!v.isAlive()) {
                    dueno.alMatar(v);
                }
            } else if (d <= CERCA) {
                v.hurtServer(nivel, cerca, RajangEntity.contraArmadura(v, dano * (float) (1.0 - 0.5 * d / CERCA)));
                Vec3 fuera = RajangEntity.horizontalHacia(p, v.position());
                v.setDeltaMovement(fuera.x * 1.0, 0.45, fuera.z * 1.0);
                v.hurtMarked = true;
                if (!v.isAlive()) {
                    dueno.alMatar(v);
                }
            }
        }
    }

    @Override
    public boolean isPickable() {
        return false;
    }

    @Override
    public boolean hurtServer(ServerLevel nivel, DamageSource fuente, float cantidad) {
        return false;
    }

    @Override
    public boolean shouldBeSaved() {
        return false;
    }

    @Override
    public boolean shouldRenderAtSqrDistance(double distancia) {
        return distancia < 200 * 200;
    }

    @Override
    protected void readAdditionalSaveData(ValueInput entrada) {
    }

    @Override
    protected void addAdditionalSaveData(ValueOutput salida) {
    }
}
