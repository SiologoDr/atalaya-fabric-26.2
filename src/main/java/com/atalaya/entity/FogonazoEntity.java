package com.atalaya.entity;

import com.atalaya.mixin.CreeperAccessor;
import com.atalaya.mixin.NivelExplosionAccessor;
import com.atalaya.net.AtalayaRed;
import com.atalaya.particula.AtalayaParticulas;
import com.atalaya.sonido.AtalayaSonidos;
import net.fabricmc.fabric.api.networking.v1.ServerPlayNetworking;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.monster.Creeper;
import net.minecraft.world.level.ClipContext;
import net.minecraft.world.level.Explosion;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;
import net.minecraft.world.phys.shapes.CollisionContext;

/**
 * El Fogonazo: un bicho-luciernaga de la noche que lleva la luz dentro, en el farol que levanta sobre el lomo. Si se te
 * acerca, se abre y estalla: te empuja, te hace dano y te deja la pantalla en blanco (Juan, 16-10-2026: «que estalle a 3
 * bloques; el blanco, 4 segundos; que al estallar sea como la explosion de un creeper: te va a empujar, cegar y hacer
 * dano»). El diseno es el del Destello de su ficha (materiales/fichas/mobs/fogonazo).
 *
 * Como el Fulminante, hereda de {@link Creeper} entero: la IA, el acercarse, el cebarse a 3 bloques, el hincharse y la
 * explosion. Lo suyo es la mecha (un segundo, contra el segundo y medio del creeper), el silencio (no suena al andar ni
 * quieto: solo al pegarle, al morir, la mecha y el estallido), que corre como un jugador esprintando, el estallido (con su sonido y un destello blanco) y el blanco en
 * la pantalla de quien lo ve estallar.
 *
 * Por ahora solo sale con su huevo: ningun mob ni jefe de Atalaya aparece todavia solo (Juan, 16-10-2026).
 */
public class FogonazoEntity extends Creeper {

    /** Ticks de mecha: un segundo de aviso para apartarse (el creeper, 30). */
    public static final int MECHA = 20;
    /** A quien deja en blanco: a menos de seis bloques y viendo el estallido (una pared tapa la luz). */
    public static final double ALCANCE = 6.0;
    /** La pantalla en blanco: cuatro segundos del todo y dos en irse. */
    public static final int BLANCO = 80;
    public static final int FUNDE = 40;

    public FogonazoEntity(EntityType<? extends Creeper> tipo, Level nivel) {
        super(tipo, nivel);
        ((CreeperAccessor) (Object) this).atalaya$ponerMecha(MECHA);
    }

    /*
     * En silencio (Juan, 16-10-2026: «no va a tener ruido, va a ser silencio; un segundo antes de que explote recien va
     * a sonar»): no suena al andar ni estando quieto (sin sonido de ambiente ni pasos); lo unico que le delata es su
     * luz. Al pegarle y al morir, si («sonido cuando le atacas si debe tener, lo mismo al morir»).
     */

    @Override
    protected SoundEvent getHurtSound(DamageSource fuente) {
        return AtalayaSonidos.FOGONAZO_HERIDO;
    }

    @Override
    protected SoundEvent getDeathSound() {
        return AtalayaSonidos.FOGONAZO_MUERTE;
    }

    @Override
    protected void playStepSound(BlockPos pos, BlockState bloque) {
    }

    /**
     * Lo primero que se le oye: al cebarse, un segundo antes de estallar, el farol que se hincha y zumba (dura lo que la
     * mecha). El creeper suena ahi con playSound(CREEPER_PRIMED); el Fogonazo, con lo suyo.
     */
    @Override
    public void playSound(SoundEvent sonido, float volumen, float tono) {
        if (sonido == SoundEvents.CREEPER_PRIMED) {
            super.playSound(AtalayaSonidos.FOGONAZO_MECHA, 1.0F, 1.0F);
            return;
        }
        super.playSound(sonido, volumen, tono);
    }

    /**
     * El estallido, en lugar de la explosion del creeper (FogonazoMixin): la misma explosion (el mismo radio, el mismo
     * dano y el mismo empujon), con su sonido; encima, el destello blanco; y el blanco en la pantalla de quien lo ve.
     */
    public void estallar(ServerLevel nivel, double x, double y, double z, float radio, Level.ExplosionInteraction interaccion) {
        nivel.explode(this, Explosion.getDefaultDamageSource(nivel, this), null, x, y, z, radio, false, interaccion,
                ParticleTypes.EXPLOSION, ParticleTypes.EXPLOSION_EMITTER, NivelExplosionAccessor.atalaya$particulasBloque(),
                BuiltInRegistries.SOUND_EVENT.wrapAsHolder(AtalayaSonidos.FOGONAZO_ESTALLIDO));
        Vec3 luz = new Vec3(x, y + 0.9, z);
        // El destello: blanco (el elemento 4 de MiniJefeParticula) y grande; uno mas pequeno dentro, mas vivo.
        nivel.sendParticles(AtalayaParticulas.MJ_DESTELLO, luz.x, luz.y, luz.z, 0, 4.5, 0.0, 4.0, 1.0);
        nivel.sendParticles(AtalayaParticulas.MJ_DESTELLO, luz.x, luz.y, luz.z, 0, 2.2, 0.0, 4.0, 1.0);
        deslumbrar(nivel, luz);
    }

    /** La pantalla en blanco a cada jugador que este cerca y lo vea (sin una pared en medio). */
    private void deslumbrar(ServerLevel nivel, Vec3 luz) {
        for (ServerPlayer jugador : nivel.players()) {
            if (jugador.isSpectator()) {
                continue;
            }
            Vec3 ojos = jugador.getEyePosition();
            if (ojos.distanceToSqr(luz) > ALCANCE * ALCANCE) {
                continue;
            }
            HitResult choque = nivel.clip(new ClipContext(luz, ojos, ClipContext.Block.VISUAL, ClipContext.Fluid.NONE,
                    CollisionContext.empty()));
            if (choque.getType() != HitResult.Type.MISS) {
                continue;
            }
            ServerPlayNetworking.send(jugador, new AtalayaRed.Deslumbre(BLANCO, FUNDE));
        }
    }
}
