package com.atalaya.client;

import com.atalaya.Atalaya;
import net.fabricmc.fabric.api.client.rendering.v1.hud.HudElement;
import net.minecraft.client.DeltaTracker;
import net.minecraft.client.gui.GuiGraphicsExtractor;
import net.minecraft.client.renderer.RenderPipelines;
import net.minecraft.resources.Identifier;

/**
 * El miedo: cuando Nerea ruge cerca o te elige con la Mirada del Abismo, los
 * bordes de la pantalla se cierran en el azul negro del fondo del mar, con
 * vetas de agua que se cuelan hacia el centro. Textura propia (nerea_extras.py).
 * Con Aeralis, en cambio, se cierran nubes de tormenta (aeralis_extras.py), y con
 * Rajang, la selva y las grietas de jade (rajang_extras.py).
 */
public class MiedoHud implements HudElement {

    private static final Identifier TEXTURA =
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "textures/gui/miedo_nerea.png");
    /** El de Aeralis: nubes de tormenta y rayos que se cierran (aeralis_extras.py). */
    private static final Identifier TEXTURA_AIRE =
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "textures/gui/miedo_aeralis.png");
    /** El de Rajang: la selva y las grietas de jade que se cierran (rajang_extras.py). */
    private static final Identifier TEXTURA_TIERRA =
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "textures/gui/miedo_rajang.png");
    /** El de Novilis: los bordes se queman y se cierran entre brasas (novilis_extras.py). */
    private static final Identifier TEXTURA_FUEGO =
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "textures/gui/miedo_novilis.png");
    private static final int TAM = 256;
    private static final int ABISMO = 0xFFFFFF;
    private static final float ALFA_MAXIMA = 0.82F;

    @Override
    public void extractRenderState(GuiGraphicsExtractor grafico, DeltaTracker delta) {
        float miedo = NereaPresencia.miedo(delta.getGameTimeDeltaPartialTick(false));
        int alfa = Math.round(Math.min(1.0F, miedo) * ALFA_MAXIMA * 255.0F);
        if (alfa <= 2) {
            return;
        }
        grafico.blit(RenderPipelines.GUI_TEXTURED, NereaPresencia.miedoDeFuego() ? TEXTURA_FUEGO : NereaPresencia.miedoDeTierra() ? TEXTURA_TIERRA
                        : NereaPresencia.miedoDeAire() ? TEXTURA_AIRE : TEXTURA,
                0, 0, 0.0F, 0.0F,
                grafico.guiWidth(), grafico.guiHeight(),
                TAM, TAM, TAM, TAM,
                (alfa << 24) | ABISMO);
    }
}
