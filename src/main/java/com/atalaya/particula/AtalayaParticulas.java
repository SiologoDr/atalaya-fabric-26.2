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

    // --- Las de Nerea (nerea_extras.py). Tampoco ninguna es de vanilla. ---

    /** Burbuja que sube y revienta: avisa del remolino y de la maldicion. */
    public static SimpleParticleType NEREA_BURBUJA;
    /** Bocanada de espuma: impactos, olas, burbujas que revientan. */
    public static SimpleParticleType NEREA_ESPUMA;
    /** Gota de agua con peso: lo que salpica. */
    public static SimpleParticleType NEREA_GOTA;
    /** La cresta del Rompeolas avanzando por el suelo. */
    public static SimpleParticleType NEREA_OLA;
    /** Espiral de agua alrededor de quien arrastra el remolino. */
    public static SimpleParticleType NEREA_REMOLINO;
    /** Chispas de las cadenas al arrastrarse por la piedra. */
    public static SimpleParticleType NEREA_CHISPA;
    /** Destello que vuela hacia los ojos durante la mirada. */
    public static SimpleParticleType NEREA_OJO;
    /** Esquirlas de cristal y laton de los sellos. */
    public static SimpleParticleType NEREA_SELLO;
    /** El latido del corazon maldito. */
    public static SimpleParticleType NEREA_CORAZON;
    /** Mota dorada de la liberacion. */
    public static SimpleParticleType NEREA_LUZ;
    /**
     * Onda expansiva: un anillo tumbado que se abre por el suelo. Lleva la
     * fuerza del temblor en la velocidad X y el radio en la Y, y al nacer en el
     * cliente sacude la camara de quien este cerca.
     */
    public static SimpleParticleType NEREA_ONDA;
    /** Esquirlas de prismarina que saltan con los golpes. */
    public static SimpleParticleType NEREA_ROCA;
    /** Polvo de arena que levantan las pisadas y las caidas. */
    public static SimpleParticleType NEREA_POLVO;

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

        // Las de aviso de Nerea (el remolino que viene, la ola, los ojos que
        // cargan, el sello que se agrieta) siempre visibles, como las del Vigia.
        NEREA_BURBUJA = registrar("nerea_burbuja", true);
        NEREA_ESPUMA = registrar("nerea_espuma", false);
        NEREA_GOTA = registrar("nerea_gota", false);
        NEREA_OLA = registrar("nerea_ola", true);
        NEREA_REMOLINO = registrar("nerea_remolino", true);
        NEREA_CHISPA = registrar("nerea_chispa", true);
        NEREA_OJO = registrar("nerea_ojo", true);
        NEREA_SELLO = registrar("nerea_sello", true);
        NEREA_CORAZON = registrar("nerea_corazon", false);
        NEREA_LUZ = registrar("nerea_luz", false);
        NEREA_ONDA = registrar("nerea_onda", true);
        NEREA_ROCA = registrar("nerea_roca", false);
        NEREA_POLVO = registrar("nerea_polvo", false);
    }

    private static SimpleParticleType registrar(String nombre, boolean siempre) {
        return Registry.register(BuiltInRegistries.PARTICLE_TYPE,
                Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, nombre),
                FabricParticleTypes.simple(siempre));
    }
}
