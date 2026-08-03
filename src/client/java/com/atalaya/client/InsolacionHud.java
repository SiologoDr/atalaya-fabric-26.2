package com.atalaya.client;

import com.atalaya.Atalaya;
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
 * Halo de calor: la pantalla se cierra por los bordes segun sube la insolacion.
 *
 * Sustituye a la nausea como forma principal de "visto borrosa". La nausea de
 * vanilla tiene una sola intensidad —el amplificador no la cambia— y a bastante
 * gente le sienta mal de verdad; en un servidor con mucha gente eso significa
 * jugadores que no pueden cruzar el desierto. Un halo propio se gradua a
 * voluntad y no marea a nadie.
 *
 * La intensidad sale de la columna "vision" de la tabla de escalones, asi que se
 * ajusta sin tocar este fichero.
 *
 * No hace falta red: el efecto viaja solo al cliente como cualquier otro, asi
 * que el jugador ya tiene su propio nivel cuando le toca dibujar.
 */
public class InsolacionHud implements HudElement {

    /**
     * Blanca con alfa radial: transparente en el centro y opaca en las esquinas.
     *
     * Al ser blanca, el TINTE decide el color. Una sola imagen sirve para
     * cualquier tono, igual que hace la gota de la hidratacion.
     */
    private static final Identifier TEXTURA =
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "textures/gui/insolacion_vineta.png");

    /**
     * Es grande a proposito. El HUD estira con vecino mas cercano, asi que una
     * textura pequena se veria a bloques al ocupar la pantalla entera.
     */
    private static final int TAM_TEXTURA = 256;

    /** Naranja de sol, el mismo del icono del efecto. */
    private static final int NARANJA = 0xFF7C26;

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

        MobEffectInstance insolacion = jugador.getEffect(InsolacionEffect.INSOLACION);
        if (insolacion == null) {
            return;
        }

        // El amplificador es el nivel menos uno, tal como lo guarda el juego.
        float vision = InsolacionEffect.escalon(insolacion.getAmplifier() + 1).vision();
        if (vision <= 0) {
            return; // los primeros escalones no tocan la vista
        }

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
                (alfa << 24) | NARANJA);
    }
}
