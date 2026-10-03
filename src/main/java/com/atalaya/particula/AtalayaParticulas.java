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
 * Las estrellas del aturdimiento y las del Vigia. Vanilla no trae ninguna que
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

    // --- Las del Vigia. Todas dibujadas para el: ninguna es de vanilla. ---

    /** Brasa que vuela hacia el ojo mientras carga la mirada. */
    public static SimpleParticleType VIGIA_CHISPA;
    /**
     * Mota del hilo de la mirada. Lleva la carga (0 a 1) en la velocidad X,
     * que la particula no usa para moverse: es como se le pasa un numero a
     * una particula simple sin inventar un tipo con datos.
     */
    public static SimpleParticleType VIGIA_RAYO;
    /** Runa-ojo que se abre sobre quien recibe la mirada. */
    public static SimpleParticleType VIGIA_MALDICION;
    /** Ojito rojo que flota alrededor del marcado: la particula del efecto. */
    public static SimpleParticleType VIGIA_MARCA;
    /** Los tres tajos del cepo. */
    public static SimpleParticleType VIGIA_ZARPA;
    /** Trozos de cristal y de hierro del farol: golpes y tambaleos. */
    public static SimpleParticleType VIGIA_ESQUIRLA;
    /** Bocanada del farol al apagarse y al caer. */
    public static SimpleParticleType VIGIA_HUMO;
    /** Lo ultimo que sale del farol al morir. */
    public static SimpleParticleType VIGIA_ALMA;

    private AtalayaParticulas() {
    }

    public static void registrar() {
        ESTRELLA = Registry.register(BuiltInRegistries.PARTICLE_TYPE,
                Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "estrella"),
                FabricParticleTypes.simple(true));

        // Las del Vigia van con "siempre visible" las que son aviso (la carga,
        // el rayo, la marca, la zarpa): con particulas al minimo no pueden
        // desaparecer, o el jugador pierde la unica pista de lo que viene.
        VIGIA_CHISPA = registrar("vigia_chispa", true);
        VIGIA_RAYO = registrar("vigia_rayo", true);
        VIGIA_MALDICION = registrar("vigia_maldicion", true);
        VIGIA_MARCA = registrar("vigia_marca", true);
        VIGIA_ZARPA = registrar("vigia_zarpa", true);
        VIGIA_ESQUIRLA = registrar("vigia_esquirla", false);
        VIGIA_HUMO = registrar("vigia_humo", false);
        VIGIA_ALMA = registrar("vigia_alma", false);
    }

    private static SimpleParticleType registrar(String nombre, boolean siempre) {
        return Registry.register(BuiltInRegistries.PARTICLE_TYPE,
                Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, nombre),
                FabricParticleTypes.simple(siempre));
    }
}
