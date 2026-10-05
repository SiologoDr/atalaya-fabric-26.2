package com.atalaya.effect;

import com.atalaya.Atalaya;
import com.atalaya.particula.AtalayaParticulas;
import net.minecraft.core.Holder;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.ResourceKey;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.effect.MobEffect;
import net.minecraft.world.effect.MobEffectCategory;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;

/**
 * Efecto "Marcado": te ha visto el Vigia.
 *
 * Es una maldicion, no un dano. Mientras dura, cada segundo los monstruos de
 * alrededor que no tengan a quien perseguir pasan a perseguirte a ti, aunque
 * no te vean. El Vigia lo pone junto con el Brillo de vanilla, que es lo que
 * deja verte a traves de las paredes: entre los dos, esconderse deja de servir
 * durante medio minuto.
 *
 * Por eso no tiene niveles ni castigo propio. Lo que duele es lo que atrae.
 *
 * Solo arrastra a quien esta libre: un monstruo que ya pelea con otro jugador
 * sigue con el suyo. Si no, marcar a uno vaciaria el combate de los demas, y la
 * maldicion tiene que ser tuya, no del grupo.
 */
public class MarcadoEffect extends MobEffect {

    /** Rojo de ojo en caza, el mismo de la capa de brillo del Vigia. */
    private static final int COLOR = 0xD8261A;

    /** Hasta donde llega la llamada. */
    private static final double RADIO = 24.0;

    public static final ResourceKey<MobEffect> CLAVE = ResourceKey.create(
            Registries.MOB_EFFECT,
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "marcado"));

    public static Holder<MobEffect> MARCADO;

    protected MarcadoEffect() {
        // La particula del efecto es la propia: el ojito rojo que flota
        // alrededor del marcado, en vez de los remolinos de vanilla.
        super(MobEffectCategory.HARMFUL, COLOR, AtalayaParticulas.VIGIA_MARCA);
    }

    public static void registrar() {
        MARCADO = Registry.registerForHolder(BuiltInRegistries.MOB_EFFECT, CLAVE, new MarcadoEffect());
    }

    /** Una vez por segundo: de sobra para que se note, barato con mucha gente. */
    @Override
    public boolean shouldApplyEffectTickThisTick(int duracion, int amplificador) {
        return duracion % 20 == 0;
    }

    @Override
    public boolean applyEffectTick(ServerLevel nivel, LivingEntity entidad, int amplificador) {
        if (!(entidad instanceof Player jugador) || jugador.isCreative() || jugador.isSpectator()) {
            return true;
        }
        for (Monster monstruo : nivel.getEntitiesOfClass(Monster.class,
                jugador.getBoundingBox().inflate(RADIO))) {
            if (monstruo.getTarget() == null && monstruo.isAlive()) {
                monstruo.setTarget(jugador);
            }
        }
        return true;
    }
}
