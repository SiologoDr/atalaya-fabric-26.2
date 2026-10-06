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

    // --- Las de Aeralis (aeralis_extras.py). Ninguna es de vanilla. ---

    /** Estela de viento: la arena corre con ella. Se orienta con su velocidad. */
    public static SimpleParticleType AERALIS_VIENTO;
    /** Escama de las alas, que cae revoloteando con los golpes y al batir. */
    public static SimpleParticleType AERALIS_ESCAMA;
    /** Espiral de polvo que gira: donde va a nacer un tornado y en su base. */
    public static SimpleParticleType AERALIS_REMOLINO;
    /** Rayo que salta dentro de las alas desde la fase III. */
    public static SimpleParticleType AERALIS_RAYO;
    /** Runa de viento azul: la Marca del Vendaval. */
    public static SimpleParticleType AERALIS_MARCA;
    /** Mota de cielo: el ojo de la tormenta, los nucleos, la bendicion. */
    public static SimpleParticleType AERALIS_LUZ;
    /** Mota dorada de la liberacion. */
    public static SimpleParticleType AERALIS_ORO;
    /**
     * Onda de presion: un anillo tumbado que se abre. Como la de Nerea, lleva
     * la fuerza del temblor en la velocidad X y el radio en la Y.
     */
    public static SimpleParticleType AERALIS_ONDA;
    /**
     * El circulo del Juicio, tumbado en el suelo. Lleva el radio en la
     * velocidad X y los ticks que dura en la Y.
     */
    public static SimpleParticleType AERALIS_CIRCULO;
    /** Polvo que levanta el viento. */
    public static SimpleParticleType AERALIS_POLVO;
    /** Jiron de nube que se estira y se deshace: estelas de rafagas y tornados. */
    public static SimpleParticleType AERALIS_JIRON;

    // --- Rajang, el Jaguar de Jade ---
    /** Polvo y tierra que levantan sus pasos y sus golpes. */
    public static SimpleParticleType RAJANG_POLVO;
    /** Terrones y piedras que saltan y caen. */
    public static SimpleParticleType RAJANG_ROCA;
    /** Astillas de jade: los golpes que recibe, los totems que se rompen. */
    public static SimpleParticleType RAJANG_JADE;
    /** Brasa verde de la maldicion: por las grietas, la boca, los totems. */
    public static SimpleParticleType RAJANG_CHISPA;
    /** Hojas de la selva que caen. */
    public static SimpleParticleType RAJANG_HOJA;
    /** La onda de un golpe contra el suelo, tumbada (sacude la camara cerca). Fuerza en la X, radio en la Y. */
    public static SimpleParticleType RAJANG_ONDA;
    /** Grieta que brilla en el suelo, tumbada. Tamano en la X, ticks en la Y. */
    public static SimpleParticleType RAJANG_GRIETA;
    /** El hexagono roto donde va a salir algo, tumbado. Tamano en la X, ticks en la Y. */
    public static SimpleParticleType RAJANG_AVISO;
    /** La marca del Cataclismo con su cuenta atras, tumbada. Tamano en la X, ticks en la Y. */
    public static SimpleParticleType RAJANG_MARCA;
    /** El circulo del Sello de la Tierra, tumbado. Tamano en la X, ticks en la Y. */
    public static SimpleParticleType RAJANG_SELLO;
    /** Runa de oro de la Piel de Jade. */
    public static SimpleParticleType RAJANG_RUNA;
    /** Llama verde: la estela de los fragmentos y la grieta del cielo. */
    public static SimpleParticleType RAJANG_LLAMA;
    /** El lastre bajo los pies (Peso de la Tierra), tumbado. Tamano en la X, ticks en la Y. */
    public static SimpleParticleType RAJANG_LASTRE;
    /** Chispa de oro: la liberacion. */
    public static SimpleParticleType RAJANG_ORO;
    /** El zarpazo: tres garras en arco que cortan el aire. Tamano en la X, ticks en la Y, giro en la Z. */
    public static SimpleParticleType RAJANG_ZARPAZO;
    /** El tajo de cada espada de jefe al golpear: una media luna del color del tema. */
    public static SimpleParticleType MAREAS_TAJO;
    public static SimpleParticleType JADE_TAJO;
    public static SimpleParticleType VENDAVAL_TAJO;

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

        // Las de aviso de Aeralis (donde nace un tornado, la marca, el circulo
        // del Juicio, la onda) siempre visibles.
        AERALIS_VIENTO = registrar("aeralis_viento", false);
        AERALIS_ESCAMA = registrar("aeralis_escama", false);
        AERALIS_REMOLINO = registrar("aeralis_remolino", true);
        AERALIS_RAYO = registrar("aeralis_rayo", false);
        AERALIS_MARCA = registrar("aeralis_marca", true);
        AERALIS_LUZ = registrar("aeralis_luz", false);
        AERALIS_ORO = registrar("aeralis_oro", false);
        AERALIS_ONDA = registrar("aeralis_onda", true);
        AERALIS_CIRCULO = registrar("aeralis_circulo", true);
        AERALIS_POLVO = registrar("aeralis_polvo", false);
        AERALIS_JIRON = registrar("aeralis_jiron", false);
        RAJANG_POLVO = registrar("rajang_polvo", false);
        RAJANG_ROCA = registrar("rajang_roca", false);
        RAJANG_JADE = registrar("rajang_jade", false);
        RAJANG_CHISPA = registrar("rajang_chispa", true);
        RAJANG_HOJA = registrar("rajang_hoja", false);
        RAJANG_ONDA = registrar("rajang_onda", true);
        RAJANG_GRIETA = registrar("rajang_grieta", true);
        RAJANG_AVISO = registrar("rajang_aviso", true);
        RAJANG_MARCA = registrar("rajang_marca", true);
        RAJANG_SELLO = registrar("rajang_sello", true);
        RAJANG_RUNA = registrar("rajang_runa", true);
        RAJANG_LLAMA = registrar("rajang_llama", true);
        RAJANG_LASTRE = registrar("rajang_lastre", true);
        RAJANG_ORO = registrar("rajang_oro", true);
        RAJANG_ZARPAZO = registrar("rajang_zarpazo", true);
        MAREAS_TAJO = registrar("mareas_tajo", true);
        JADE_TAJO = registrar("jade_tajo", true);
        VENDAVAL_TAJO = registrar("vendaval_tajo", true);
    }

    private static SimpleParticleType registrar(String nombre, boolean siempre) {
        return Registry.register(BuiltInRegistries.PARTICLE_TYPE,
                Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, nombre),
                FabricParticleTypes.simple(siempre));
    }
}
