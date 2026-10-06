package com.atalaya.client;

import com.atalaya.Atalaya;
import com.atalaya.effect.QuemaduraEffect;
import net.fabricmc.fabric.api.client.rendering.v1.hud.HudElement;
import net.minecraft.client.DeltaTracker;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphicsExtractor;
import net.minecraft.client.player.LocalPlayer;
import net.minecraft.client.renderer.RenderPipelines;
import net.minecraft.resources.Identifier;
import net.minecraft.util.Mth;
import net.minecraft.world.effect.MobEffectInstance;

/**
 * La quemadura de Novilis junto a los corazones: una llama con su numero (I,
 * II o III) que crece y se oscurece hacia el carmesi; la III lleva la calavera
 * y late despacio, porque con ella el Dios de la Guerra mata de un golpe.
 *
 * COLOCACION. A la IZQUIERDA de la fila de corazones, fuera de la hotbar, y no
 * encima: encima estan la armadura (guiHeight - 49) y, con absorcion o mucha
 * vida, mas filas de corazones que suben. Al lado no hay nada de vanilla:
 *
 *   centerX - 91         donde empiezan los corazones (y la hotbar)
 *   guiHeight - 39       la fila de corazones; el icono va centrado en ella
 *   guiHeight - 23       el hueco de la mano secundaria, a la izquierda de la
 *                        hotbar: el icono acaba 3 pixeles por encima
 *
 * El icono mide 18 y se pinta a 18: cada texel en un pixel de interfaz. Solo
 * en supervivencia y aventura, que es cuando hay corazones al lado.
 */
public class QuemaduraHud implements HudElement {

    private static final Identifier[] ICONOS = {
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "textures/gui/novilis_quemadura_1.png"),
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "textures/gui/novilis_quemadura_2.png"),
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "textures/gui/novilis_quemadura_3.png")};

    private static final int TAM = 18;
    /** Media hotbar: los corazones empiezan aqui a la izquierda del centro. */
    private static final int MEDIA_HOTBAR = 91;
    /** El aire entre el icono y el primer corazon. */
    private static final int SEPARACION = 2;
    /** Cuanto sube respecto al borde de abajo: centrado en la fila de corazones. */
    private static final int ALTURA = 44;

    @Override
    public void extractRenderState(GuiGraphicsExtractor g, DeltaTracker delta) {
        Minecraft mc = Minecraft.getInstance();
        LocalPlayer jugador = mc.player;
        if (jugador == null || jugador.isCreative() || jugador.isSpectator() || QuemaduraEffect.QUEMADURA == null) {
            return;
        }
        MobEffectInstance efecto = jugador.getEffect(QuemaduraEffect.QUEMADURA);
        if (efecto == null) {
            return;
        }
        int nivel = Mth.clamp(efecto.getAmplifier(), 0, 2);
        int tinte = 0xFFFFFFFF;
        if (nivel == 2) {
            // La III late despacio: de entera a un poco apagada, sin parpadear.
            float parcial = delta.getGameTimeDeltaPartialTick(false);
            float k = 0.8F + 0.2F * (0.5F + 0.5F * Mth.sin((jugador.tickCount + parcial) * 0.2F));
            int v = Math.round(255 * k);
            tinte = 0xFF000000 | (v << 16) | (v << 8) | v;
        }
        int x = g.guiWidth() / 2 - MEDIA_HOTBAR - SEPARACION - TAM;
        int y = g.guiHeight() - ALTURA;
        g.blit(RenderPipelines.GUI_TEXTURED, ICONOS[nivel], x, y, 0.0F, 0.0F, TAM, TAM, TAM, TAM, tinte);
    }
}
