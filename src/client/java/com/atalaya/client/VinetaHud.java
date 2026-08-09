package com.atalaya.client;

import com.atalaya.Atalaya;
import com.atalaya.effect.HipotermiaEffect;
import com.atalaya.effect.InsolacionEffect;
import net.fabricmc.fabric.api.client.rendering.v1.hud.HudElement;
import net.minecraft.client.DeltaTracker;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphicsExtractor;
import net.minecraft.client.player.LocalPlayer;
import net.minecraft.client.renderer.RenderPipelines;
import net.minecraft.resources.Identifier;
import net.minecraft.world.effect.MobEffectInstance;

/**
 * Halo que cierra la pantalla por los bordes cuando el cuerpo va mal: naranja de
 * calor con la insolacion, azul de hielo con la hipotermia.
 *
 * Sustituye a la nausea como forma principal de "visto borroso". La nausea de
 * vanilla tiene una sola intensidad —el amplificador no la cambia— y a bastante
 * gente le sienta mal de verdad; en un servidor con mucha gente eso significa
 * jugadores que no pueden cruzar el desierto. Un halo propio se gradua a
 * voluntad y no marea a nadie.
 *
 * La intensidad sale de la columna "vision" de la tabla de escalones de cada
 * efecto, asi que se ajusta sin tocar este fichero.
 *
 * UN SOLO HALO A LA VEZ, a proposito. Los dos efectos pueden coincidir —se sale
 * de la nieve todavia helado y se entra en un desierto—, y dibujar los dos
 * encima sumaria las opacidades hasta dejar la pantalla casi cerrada. Se pinta
 * el que mas aprieta, que ademas es el que interesa ver.
 *
 * No hace falta red: los efectos viajan solos al cliente como cualquier otro,
 * asi que el jugador ya tiene su nivel cuando le toca dibujar.
 */
public class VinetaHud implements HudElement {

    /**
     * Blanca con alfa radial: transparente en el centro y opaca en las esquinas.
     *
     * Al ser blanca, el TINTE decide el color. Una sola imagen sirve para los
     * dos halos: el naranja del calor y el azul del frio.
     *
     * Por eso se llama "vineta" a secas y no "insolacion_vineta", que es como
     * nacio: el nombre venia de para que se hizo, no de lo que es, y en cuanto
     * la hipotermia empezo a usarla se volvio enganoso.
     */
    private static final Identifier TEXTURA =
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "textures/gui/vineta.png");

    /**
     * Es grande a proposito. El HUD estira con vecino mas cercano, asi que una
     * textura pequena se veria a bloques al ocupar la pantalla entera.
     */
    private static final int TAM_TEXTURA = 256;

    /** Naranja de sol, el mismo del icono de la insolacion. */
    private static final int NARANJA = 0xFF7C26;

    /** Azul de escarcha, el mismo del icono de la hipotermia. */
    private static final int HIELO = 0x6FC0F0;

    /**
     * Opacidad con la vision al maximo.
     *
     * Deliberadamente bajo: esto tiene que estorbar lo justo para que se note
     * que vas mal, no impedir jugar. Cerrar del todo la pantalla a alguien que
     * ya esta perdiendo vida seria castigarle dos veces.
     */
    private static final float ALFA_MAXIMA = 0.45f;

    @Override
    public void extractRenderState(GuiGraphicsExtractor grafico, DeltaTracker delta) {
        LocalPlayer jugador = Minecraft.getInstance().player;
        if (jugador == null) {
            return;
        }

        float calor = vision(jugador, InsolacionEffect.INSOLACION, true);
        float frio = vision(jugador, HipotermiaEffect.HIPOTERMIA, false);
        if (calor <= 0 && frio <= 0) {
            return;
        }

        // Gana el que mas cierra la vista. Empatados —que es lo normal, porque
        // las dos tablas traen los mismos numeros— se queda el frio, que es el
        // que estaria pasando en ese momento si acabas de salir de la nieve.
        boolean esFrio = frio >= calor;
        float vision = esFrio ? frio : calor;

        int alfa = Math.round(Math.min(1f, vision) * ALFA_MAXIMA * 255f);
        if (alfa <= 0) {
            return;
        }

        // La textura se ESTIRA a toda la pantalla.
        //
        // Hace falta la variante que separa el tamano de dibujo de la region de
        // origen. La corta usa el ancho de dibujo tambien como region, asi que
        // pedir 850 pixeles de una textura de 256 la repite en mosaico en vez de
        // agrandarla: salen circulos repetidos por toda la pantalla.
        //
        //   x, y | u, v | ancho y alto de DIBUJO | region de ORIGEN | textura | color
        grafico.blit(RenderPipelines.GUI_TEXTURED, TEXTURA,
                0, 0, 0f, 0f,
                grafico.guiWidth(), grafico.guiHeight(),
                TAM_TEXTURA, TAM_TEXTURA,
                TAM_TEXTURA, TAM_TEXTURA,
                (alfa << 24) | (esFrio ? HIELO : NARANJA));
    }

    /** Cuanto cierra la vista ese efecto, o 0 si el jugador no lo tiene. */
    private static float vision(LocalPlayer jugador,
                                net.minecraft.core.Holder<net.minecraft.world.effect.MobEffect> efecto,
                                boolean esInsolacion) {
        if (efecto == null) {
            return 0f;
        }
        MobEffectInstance instancia = jugador.getEffect(efecto);
        if (instancia == null) {
            return 0f;
        }
        // El amplificador es el nivel menos uno, tal como lo guarda el juego.
        int nivel = instancia.getAmplifier() + 1;
        return esInsolacion
                ? InsolacionEffect.escalon(nivel).vision()
                : HipotermiaEffect.escalon(nivel).vision();
    }
}
