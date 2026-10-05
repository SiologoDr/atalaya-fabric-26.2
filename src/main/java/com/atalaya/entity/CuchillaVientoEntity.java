package com.atalaya.entity;

import com.atalaya.particula.AtalayaParticulas;
import com.atalaya.sonido.AtalayaSonidos;
import net.minecraft.core.BlockPos;
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

import java.util.HashSet;
import java.util.Set;
import java.util.UUID;

/**
 * Una cuchilla de viento del Aleteo Cortante: una media luna de aire que sale
 * de la punta del ala, baja en picado hasta la altura que le toca y sigue
 * recta, a ras de suelo, unos 48 bloques.
 *
 * Las bajas (de los pies a la rodilla) se SALTAN; las altas (del pecho a la
 * cintura) hay que esquivarlas apartandose. El escudo las para de frente.
 * Atraviesa a todos los que pilla: 14 de dano (+9 por fase, y hasta un 30 %
 * mas contra armadura), un empujon fuerte y, una de cada cuatro veces, te
 * levanta unos tres bloques.
 */
public class CuchillaVientoEntity extends Entity {

    /** Media anchura de la cuchilla (de punta a punta mide el doble) y media altura. */
    private static final double MEDIO_ANCHO = 1.9;
    private static final double MEDIO_ALTO = 0.5;

    private @Nullable AeralisEntity duena;
    private double alturaObjetivo;
    /** Lo que baja (o sube) por tick hasta su altura: llega a ella antes que al blanco. */
    private double bajada = 0.9;
    private float dano;
    private double recorrido;
    private final Set<UUID> golpeados = new HashSet<>();

    public CuchillaVientoEntity(EntityType<? extends CuchillaVientoEntity> tipo, Level nivel) {
        super(tipo, nivel);
        this.noPhysics = true;
    }

    public static CuchillaVientoEntity lanzar(ServerLevel nivel, AeralisEntity duena, Vec3 desde, float rumbo,
                                              double alturaObjetivo, double bajada, double velocidad, float dano) {
        CuchillaVientoEntity c = new CuchillaVientoEntity(AtalayaEntities.CUCHILLA_VIENTO, nivel);
        c.duena = duena;
        c.alturaObjetivo = alturaObjetivo;
        c.bajada = bajada;
        c.dano = dano;
        c.setPos(desde.x, desde.y, desde.z);
        c.setYRot(rumbo);
        c.yRotO = rumbo;
        float b = rumbo * Mth.DEG_TO_RAD;
        c.setDeltaMovement(-Mth.sin(b) * velocidad, 0.0, Mth.cos(b) * velocidad);
        nivel.addFreshEntity(c);
        return c;
    }

    @Override
    protected void defineSynchedData(SynchedEntityData.Builder datos) {
    }

    @Override
    public void tick() {
        super.tick();
        Vec3 antes = position();
        Vec3 v = getDeltaMovement();
        if (!level().isClientSide()) {
            // Baja en picado desde el ala y luego va a ras de suelo.
            double vy = Mth.clamp(alturaObjetivo - getY(), -bajada, bajada);
            v = new Vec3(v.x, vy, v.z);
            setDeltaMovement(v);
        }
        setPos(antes.add(v));
        if (level().isClientSide()) {
            // A ras de suelo levanta una raya de polvo.
            if (level().getBlockState(blockPosition().below()).isSolid() && random.nextInt(2) == 0) {
                level().addParticle(AtalayaParticulas.AERALIS_POLVO, getX(), getY() - 0.3, getZ(), v.x * 0.15, 0.04, v.z * 0.15);
            }
            for (int i = 0; i < 2; i++) {
                double l = (random.nextDouble() - 0.5) * 2.0 * MEDIO_ANCHO;
                Vec3 lado = new Vec3(-v.z, 0, v.x).normalize();
                level().addParticle(AtalayaParticulas.AERALIS_VIENTO, getX() + lado.x * l, getY(), getZ() + lado.z * l,
                        v.x * 0.3, 0.0, v.z * 0.3);
            }
            return;
        }
        ServerLevel nivel = (ServerLevel) level();
        if (duena == null || duena.isRemoved()) {
            discard();
            return;
        }
        recorrido += Math.sqrt(v.x * v.x + v.z * v.z);
        golpear(nivel, antes, position());
        BlockPos b = blockPosition();
        if (recorrido > AeralisEntity.ALCANCE_CUCHILLA
                || (tickCount > 4 && !nivel.getBlockState(b).getCollisionShape(nivel, b).isEmpty())) {
            deshacer(nivel);
        }
    }

    private void golpear(ServerLevel nivel, Vec3 desde, Vec3 hasta) {
        Vec3 d = new Vec3(hasta.x - desde.x, 0, hasta.z - desde.z);
        double largo = d.length();
        if (largo < 1.0E-4) {
            return;
        }
        Vec3 dir = d.scale(1.0 / largo);
        AABB caja = new AABB(desde, hasta).inflate(MEDIO_ANCHO + 1.0, MEDIO_ALTO + 2.0, MEDIO_ANCHO + 1.0);
        for (LivingEntity v : nivel.getEntitiesOfClass(LivingEntity.class, caja, duena::esPresa)) {
            if (golpeados.contains(v.getUUID())) {
                continue;
            }
            Vec3 rel = v.position().subtract(desde);
            double a = rel.x * dir.x + rel.z * dir.z;
            double l = Math.abs(rel.x * -dir.z + rel.z * dir.x);
            boolean dentro = a >= -v.getBbWidth() && a <= largo + v.getBbWidth()
                    && l <= MEDIO_ANCHO + v.getBbWidth() / 2
                    && v.getY() < getY() + MEDIO_ALTO && v.getY() + v.getBbHeight() > getY() - MEDIO_ALTO;
            if (!dentro) {
                continue;
            }
            golpeados.add(v.getUUID());
            DamageSource fuente = AeralisDanos.fuente(nivel, AeralisDanos.CUCHILLA, this, duena);
            if (v.hurtServer(nivel, fuente, AeralisEntity.contraArmadura(v, dano))) {
                boolean levanta = random.nextInt(4) == 0;
                v.setDeltaMovement(dir.x * 1.3, levanta ? 0.85 : 0.35, dir.z * 1.3);
                v.hurtMarked = true;
                nivel.playSound(null, v.getX(), v.getY(), v.getZ(), AtalayaSonidos.AERALIS_CUCHILLA_GOLPE,
                        SoundSource.HOSTILE, 2.0F, 0.9F + random.nextFloat() * 0.2F);
                nivel.sendParticles(AtalayaParticulas.AERALIS_JIRON, true, true, v.getX(), v.getY() + 1.0, v.getZ(), 6, 0.3, 0.4, 0.3, 0.1);
            } else {
                // Parada con el escudo (o sin efecto): el viento se abre a los lados.
                nivel.playSound(null, v.getX(), v.getY(), v.getZ(), AtalayaSonidos.AERALIS_INMUNE,
                        SoundSource.HOSTILE, 1.2F, 1.2F);
                nivel.sendParticles(AtalayaParticulas.AERALIS_VIENTO, true, true, v.getX(), v.getY() + 1.0, v.getZ(), 8, 0.5, 0.3, 0.5, 0.2);
            }
        }
    }

    private void deshacer(ServerLevel nivel) {
        nivel.sendParticles(AtalayaParticulas.AERALIS_JIRON, true, true, getX(), getY(), getZ(), 6, 0.8, 0.2, 0.8, 0.05);
        nivel.sendParticles(AtalayaParticulas.AERALIS_POLVO, true, true, getX(), getY(), getZ(), 4, 0.8, 0.2, 0.8, 0.02);
        discard();
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
        return distancia < 128 * 128;
    }

    @Override
    protected void readAdditionalSaveData(ValueInput entrada) {
    }

    @Override
    protected void addAdditionalSaveData(ValueOutput salida) {
    }
}
