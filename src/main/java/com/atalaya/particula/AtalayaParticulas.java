package com.atalaya.particula;

import com.atalaya.Atalaya;
import net.fabricmc.fabric.api.particle.v1.FabricParticleTypes;
import net.minecraft.core.Registry;
import net.minecraft.core.particles.SimpleParticleType;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.Identifier;

/**
 * Particulas propias del mod.
 *
 * De momento solo las estrellas del aturdimiento. Vanilla no trae ninguna que
 * sirva: lo mas parecido son chispas y destellos, y ninguno lee como "ver las
 * estrellas", que es un dibujo muy concreto y muy reconocible.
 */
public final class AtalayaParticulas {

    /**
     * La estrellita que da vueltas sobre la cabeza del aturdido.
     *
     * "simple" porque no lleva datos: todas son iguales y el sitio lo decide
     * quien la lanza. El true dice que se vea aunque el jugador tenga las
     * particulas al minimo — es informacion, no adorno: avisa de que estas
     * aturdido y no de que el juego se ha quedado colgado.
     */
    public static SimpleParticleType ESTRELLA;

    private AtalayaParticulas() {
    }

    public static void registrar() {
        ESTRELLA = Registry.register(BuiltInRegistries.PARTICLE_TYPE,
                Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "estrella"),
                FabricParticleTypes.simple(true));
    }
}
