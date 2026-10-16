package com.atalaya.mixin;

import net.minecraft.core.particles.ExplosionParticleInfo;
import net.minecraft.util.random.WeightedList;
import net.minecraft.world.level.Level;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.gen.Accessor;

/**
 * Las particulas de bloque de una explosion normal (el humo y el polvo), que son privadas: el estallido del Fogonazo
 * las necesita para pedir la explosion con su propio sonido, que solo admite la llamada larga.
 */
@Mixin(Level.class)
public interface NivelExplosionAccessor {

    @Accessor("DEFAULT_EXPLOSION_BLOCK_PARTICLES")
    static WeightedList<ExplosionParticleInfo> atalaya$particulasBloque() {
        throw new AssertionError();
    }
}
