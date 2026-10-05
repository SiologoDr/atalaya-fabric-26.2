package com.atalaya.entity;

import com.atalaya.effect.MarcadoEffect;
import com.atalaya.particula.AtalayaParticulas;
import com.atalaya.sonido.AtalayaSonidos;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.projectile.ThrowableProjectile;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.EntityHitResult;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;

/**
 * El rayo de la mirada: lo que dispara el ojo del Vigia al acabar la carga.
 *
 * Es un proyectil de verdad, como una flecha, y no un golpe instantaneo. Eso
 * cambia la pelea: se apunta adonde estabas al dispararse y tarda en llegar,
 * asi que hay DOS salidas en vez de una —cortarle la vista mientras carga, o
 * echarse a un lado cuando sale—. Y una pared lo para.
 *
 * Vuela recto: sin gravedad y sin frenarse en el aire. Si no da con nada en
 * dos segundos se deshace.
 */
public class RayoVigiaEntity extends ThrowableProjectile {

    /** Bloques por tick. A 24 bloques, lo maximo de la mirada, tarda un segundo. */
    public static final float VELOCIDAD = 1.25F;

    private static final int VIDA = 40;

    /** Magico: la armadura no protege de que te vean. */
    private static final float DANO = 6.0F;

    /** 30 s de marca, y de brillo, que es lo que te delata. */
    private static final int DURACION_MARCA = 600;

    public RayoVigiaEntity(EntityType<? extends RayoVigiaEntity> tipo, Level nivel) {
        super(tipo, nivel);
    }

    /** Sale del ojo hacia donde esta la presa AHORA: si te mueves, falla. */
    public static RayoVigiaEntity disparar(ServerLevel nivel, LivingEntity tirador, Vec3 desde, Vec3 hacia) {
        RayoVigiaEntity rayo = new RayoVigiaEntity(AtalayaEntities.RAYO_VIGIA, nivel);
        rayo.setOwner(tirador);
        rayo.setPos(desde.x, desde.y, desde.z);
        Vec3 dir = hacia.subtract(desde);
        rayo.shoot(dir.x, dir.y, dir.z, VELOCIDAD, 0.0F);
        nivel.addFreshEntity(rayo);
        return rayo;
    }

    @Override
    protected void defineSynchedData(SynchedEntityData.Builder datos) {
    }

    @Override
    protected double getDefaultGravity() {
        return 0.0;
    }

    /** Sin rozamiento: un rayo no pierde fuerza en el aire. */
    @Override
    protected float getAirDrag() {
        return 1.0F;
    }

    @Override
    public void tick() {
        super.tick();
        if (level().isClientSide()) {
            // El rayo y su estela son la malla del renderer. Aqui solo alguna
            // chispa suelta que salta al pasar: mas, y volveria a parecer una
            // ristra de puntos.
            if (random.nextInt(3) == 0) {
                level().addParticle(AtalayaParticulas.VIGIA_CHISPA, getX(), getY(), getZ(),
                        (random.nextDouble() - 0.5) * 0.1, (random.nextDouble() - 0.5) * 0.1,
                        (random.nextDouble() - 0.5) * 0.1);
            }
        } else if (tickCount > VIDA) {
            discard();
        }
    }

    /** Ni el propio Vigia ni otro Vigia: entre ellos no se marcan. */
    @Override
    protected boolean canHitEntity(Entity entidad) {
        return !(entidad instanceof VigiaEntity) && super.canHitEntity(entidad);
    }

    @Override
    protected void onHitEntity(EntityHitResult golpe) {
        super.onHitEntity(golpe);
        if (!(level() instanceof ServerLevel nivel) || !(golpe.getEntity() instanceof LivingEntity presa)) {
            return;
        }
        Entity tirador = getOwner();
        presa.hurtServer(nivel, nivel.damageSources().indirectMagic(this, tirador), DANO);
        presa.addEffect(new MobEffectInstance(MarcadoEffect.MARCADO, DURACION_MARCA, 0), tirador);
        // El brillo, sin remolinos ni icono propios: lo que se ve de la
        // maldicion es la marca, no el efecto de vanilla que la acompana.
        presa.addEffect(new MobEffectInstance(MobEffects.GLOWING, DURACION_MARCA, 0, false, false), tirador);
        nivel.sendParticles(AtalayaParticulas.VIGIA_MALDICION,
                presa.getX(), presa.getY() + 1.0, presa.getZ(), 8, 0.35, 0.5, 0.35, 0.0);
    }

    @Override
    protected void onHit(HitResult golpe) {
        super.onHit(golpe);
        if (level() instanceof ServerLevel nivel) {
            Vec3 p = golpe.getLocation();
            nivel.playSound(null, p.x, p.y, p.z, AtalayaSonidos.VIGIA_RAYO_IMPACTO, SoundSource.HOSTILE, 1.6F, 1.0F);
            nivel.sendParticles(AtalayaParticulas.VIGIA_CHISPA, p.x, p.y, p.z, 14, 0.15, 0.15, 0.15, 0.25);
            if (golpe instanceof BlockHitResult) {
                // Contra una pared revienta en esquirlas: la mirada se rompe.
                nivel.sendParticles(AtalayaParticulas.VIGIA_ESQUIRLA, p.x, p.y, p.z, 8, 0.1, 0.1, 0.1, 0.05);
            }
            discard();
        }
    }
}
