package com.atalaya.effect;

import com.atalaya.Atalaya;
import com.atalaya.frio.Frio;
import net.minecraft.core.Holder;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.effect.MobEffect;
import net.minecraft.world.effect.MobEffectCategory;

/**
 * Efecto de estado "Hipotermia": la contraparte de la insolacion.
 *
 * Misma estructura que aquella y por las mismas razones: el efecto es solo la
 * cara visible —icono, nombre y color— y quien reparte los castigos es
 * {@link com.atalaya.frio.FrioManager}, que es el unico que conoce los puntos
 * exactos. Los modificadores del propio efecto no valen aqui porque cada escalon
 * toca atributos DISTINTOS, y el mecanismo de vanilla solo sabe escalar uno.
 *
 * Y el nivel tampoco se guarda: se deduce del frio acumulado, asi que sube y
 * baja solo segun te acerques al fuego o te alejes. No hay estado que pueda
 * quedar desincronizado.
 *
 * La diferencia con la insolacion esta en el sentido de la cuenta. Alli el nivel
 * sube cuando los puntos BAJAN; aqui sube cuando SUBEN.
 */
public class HipotermiaEffect extends MobEffect {

    /**
     * Azul de hielo, casi blanco.
     *
     * Se separa a proposito del azul medio del empapado: los dos son agua, pero
     * uno es mojarse y el otro congelarse, y en la barra tienen que distinguirse
     * de un vistazo.
     */
    private static final int COLOR = 0xAFE6F5;

    public static final ResourceKey<MobEffect> CLAVE = ResourceKey.create(
            Registries.MOB_EFFECT,
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "hipotermia"));

    public static Holder<MobEffect> HIPOTERMIA;

    protected HipotermiaEffect() {
        super(MobEffectCategory.HARMFUL, COLOR);
    }

    public static void registrar() {
        HIPOTERMIA = Registry.registerForHolder(
                BuiltInRegistries.MOB_EFFECT, CLAVE, new HipotermiaEffect());
    }

    // ------------------------------------------------------------------
    //  Los escalones
    // ------------------------------------------------------------------

    /** Desde aqui hacia arriba empieza a doler. Es la mitad del deposito. */
    private static final int UMBRAL_NIVEL_1 = Frio.MAXIMO / 2;

    /**
     * Nivel de hipotermia para unos puntos de frio. Cero significa que no hay
     * efecto.
     *
     * Dos escalones, como la insolacion: uno que avisa y otro que mata.
     */
    public static int nivelPorFrio(int puntos) {
        if (puntos >= Frio.MAXIMO) {
            return 2;
        }
        if (puntos >= UMBRAL_NIVEL_1) {
            return 1;
        }
        return 0;
    }

    /**
     * Lo que castiga un nivel, ENTERO. No es lo que anade sobre el anterior.
     *
     * Los numeros son los mismos que los de la insolacion, y no por pereza: el
     * cuerpo agarrotado de frio y el cocido por el sol fallan igual. Las manos
     * van lentas, cuesta avanzar, se pierde fuerza y se quema mas comida
     * —tiritar consume, igual que sudar— y la vista se enturbia.
     *
     * @param mineria    fraccion que se resta a la velocidad de picado
     * @param ataque     fraccion que se resta a la velocidad de golpeo
     * @param movimiento fraccion que se resta a la velocidad de andar
     * @param fuerza     fraccion que se resta al dano de golpe
     * @param hambre     puntos de agotamiento por segundo (0.1 = Hambre I)
     * @param vision     cuanto falla la vista, de 0 a 1. Un solo mando para el
     *                   halo de los bordes y el mareo suave
     * @param dano       vida que quita cada dos segundos. Un corazon son 2.0
     */
    public record Escalon(double mineria, double ataque, double movimiento,
                          double fuerza, float hambre, float vision, float dano) {
    }

    private static final Escalon[] ESCALONES = {
            //             mineria  ataque  movim.  fuerza  hambre  vision  dano
            new Escalon(     0.00,   0.00,   0.00,   0.00,   0.0f,   0.0f,  0.0f),  // 0: bien
            new Escalon(    -0.25,  -0.25,  -0.25,  -0.25,   0.1f,   0.5f,  0.0f),  // 1: aterido
            new Escalon(    -0.25,  -0.25,  -0.25,  -0.25,   0.1f,   0.5f,  2.0f),  // 2: congelandose
    };

    /** Los castigos del nivel dado. Fuera de rango devuelve los extremos. */
    public static Escalon escalon(int nivel) {
        return ESCALONES[Math.max(0, Math.min(ESCALONES.length - 1, nivel))];
    }

    /** Identificadores de los modificadores que cuelga y descuelga el manager. */
    public static final Identifier ID_MINERIA = id("hipotermia_mineria");
    public static final Identifier ID_ATAQUE = id("hipotermia_ataque");
    public static final Identifier ID_MOVIMIENTO = id("hipotermia_movimiento");
    public static final Identifier ID_FUERZA = id("hipotermia_fuerza");

    private static Identifier id(String ruta) {
        return Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, ruta);
    }
}
