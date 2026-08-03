package com.atalaya.effect;

import com.atalaya.Atalaya;
import com.atalaya.hidratacion.Hidratacion;
import net.minecraft.core.Holder;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.effect.MobEffect;
import net.minecraft.world.effect.MobEffectCategory;

/**
 * Efecto de estado "Insolacion": lo que le pasa a quien se queda sin agua en el
 * desierto.
 *
 * A diferencia de la radiacion, aqui NO se usan los modificadores de atributo
 * del propio efecto. La radiacion tiene una sola penalizacion que crece con el
 * nivel, asi que le vale el mecanismo de vanilla; la insolacion suma castigos
 * DISTINTOS en cada escalon, y eso el efecto no lo sabe expresar: su
 * multiplicador es lineal con el amplificador y siempre sobre el mismo atributo.
 *
 * Por eso el efecto es solo la cara visible (icono, nombre y color de la barra)
 * y quien reparte los castigos es
 * {@link com.atalaya.hidratacion.HidratacionManager}, que ademas es el unico que
 * conoce la hidratacion exacta.
 *
 * El nivel NO se guarda: se deduce de los puntos que queden, asi que sube y baja
 * solo segun bebas o te sequen. No hay estado que pueda quedar desincronizado.
 */
public class InsolacionEffect extends MobEffect {

    /** Naranja de sol, tomado del propio icono del efecto. */
    private static final int COLOR = 0xFF7C26;

    public static final ResourceKey<MobEffect> CLAVE = ResourceKey.create(
            Registries.MOB_EFFECT,
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "insolacion"));

    public static Holder<MobEffect> INSOLACION;

    protected InsolacionEffect() {
        super(MobEffectCategory.HARMFUL, COLOR);
    }

    public static void registrar() {
        INSOLACION = Registry.registerForHolder(
                BuiltInRegistries.MOB_EFFECT, CLAVE, new InsolacionEffect());
    }

    // ------------------------------------------------------------------
    //  Los escalones
    // ------------------------------------------------------------------

    /**
     * Desde aqui hacia abajo empieza la insolacion. Es la mitad del deposito.
     */
    private static final int UMBRAL_NIVEL_1 = Hidratacion.MAXIMO / 2;

    /**
     * Nivel de insolacion para unos puntos de hidratacion. Cero significa que no
     * hay efecto.
     *
     * Solo hay dos escalones y no cuatro: uno que avisa y otro que mata. Con un
     * deposito de 50 puntos, cuatro tramos habrian quedado tan cortos que el
     * jugador no llegaria a distinguirlos. Asi el mensaje es claro: o vas bien,
     * o vas mal, o te estas muriendo.
     */
    public static int nivelPorHidratacion(int puntos) {
        if (puntos <= 0) {
            return 2;
        }
        if (puntos <= UMBRAL_NIVEL_1) {
            return 1;
        }
        return 0;
    }

    // ------------------------------------------------------------------
    //  Castigos de cada escalon
    // ------------------------------------------------------------------

    /**
     * Lo que castiga un nivel, ENTERO. No es lo que anade sobre el anterior:
     * es el total, ya sumado.
     *
     * Se guarda asi a proposito. Escribirlo como "lo que anade cada escalon"
     * saldria mas corto, pero obligaria a leer todas las condiciones para saber
     * que hace el nivel 3, y ataria los niveles a ser acumulativos para siempre.
     * Con el total explicito, la progresion entera se lee de un vistazo y se
     * puede aflojar un castigo en un nivel concreto cambiando un numero.
     *
     * No cuesta mas: el manager toca los mismos atributos en todos los niveles,
     * poniendo cero donde no hay castigo.
     *
     * @param mineria    fraccion que se resta a la velocidad de picado
     * @param ataque     fraccion que se resta a la velocidad de golpeo
     * @param movimiento fraccion que se resta a la velocidad de andar
     * @param fuerza     fraccion que se resta al dano de golpe
     * @param hambre     puntos de agotamiento por segundo (0.1 = Hambre I)
     * @param vision     cuanto falla la vista, de 0 a 1. Un solo mando para las
     *                   dos cosas: el halo de calor de los bordes y el mareo
     *                   suave, que los dibuja el cliente leyendo este numero
     * @param dano       vida que quita cada revision, o sea cada 2 s. Va en
     *                   puntos de vida, asi que un corazon son 2.0
     */
    public record Escalon(double mineria, double ataque, double movimiento,
                          double fuerza, float hambre, float vision, float dano) {
    }

    /**
     * La progresion completa, del nivel 0 al 2.
     *
     * El nivel 2 es el 1 mas el dano: todo lo demas se mantiene igual. Lo que
     * cambia al llegar a cero no es que vayas peor, es que te estas muriendo.
     */
    private static final Escalon[] ESCALONES = {
            //             mineria  ataque  movim.  fuerza  hambre  vision  dano
            new Escalon(     0.00,   0.00,   0.00,   0.00,   0.0f,   0.0f,  0.0f),  // 0: bien
            new Escalon(    -0.25,  -0.25,  -0.25,  -0.25,   0.1f,   0.5f,  0.0f),  // 1: insolado
            new Escalon(    -0.25,  -0.25,  -0.25,  -0.25,   0.1f,   0.5f,  2.0f),  // 2: muriendo
    };

    /** Los castigos del nivel dado. Fuera de rango devuelve los extremos. */
    public static Escalon escalon(int nivel) {
        return ESCALONES[Math.max(0, Math.min(ESCALONES.length - 1, nivel))];
    }

    /** Identificadores de los modificadores que cuelga y descuelga el manager. */
    public static final Identifier ID_MINERIA = id("insolacion_mineria");
    public static final Identifier ID_ATAQUE = id("insolacion_ataque");
    public static final Identifier ID_MOVIMIENTO = id("insolacion_movimiento");
    public static final Identifier ID_FUERZA = id("insolacion_fuerza");

    private static Identifier id(String ruta) {
        return Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, ruta);
    }
}
