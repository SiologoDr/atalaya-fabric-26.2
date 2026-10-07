package com.atalaya.client;

import com.atalaya.Atalaya;
import net.fabricmc.fabric.api.client.rendering.v1.hud.HudElement;
import net.minecraft.client.DeltaTracker;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphicsExtractor;
import net.minecraft.client.renderer.RenderPipelines;
import net.minecraft.resources.Identifier;
import net.minecraft.util.Mth;

/**
 * Lo que se ve encima en la presentacion de un jefe (PresentacionJefe): las
 * bandas negras de cine arriba y abajo (con un filo de luz del color del jefe)
 * y, al rugir, su cartel en el tercio de abajo, como en los posters
 * (presentacion_jefes.py): el destello que cruza, el NOMBRE que se abre desde
 * el centro, la linea, lo que es (JEFE DEL FUEGO) y su epiteto con el lema.
 *
 * El cartel se pinta pixel a pixel de pantalla (no a la escala del HUD): sus
 * PNG vienen en cuatro anchos y se coge el mayor que quepa, asi las letras
 * salen limpias a cualquier resolucion.
 */
public class PresentacionHud implements HudElement {

    private static final int[] ANCHOS = {480, 720, 960, 1440};
    private static final Identifier DESTELLO = tex("destello");
    private static final int DESTELLO_ANCHO = 512;
    private static final int DESTELLO_ALTO = 64;
    /** Lo que miden las bandas (de la altura de la pantalla, cada una). */
    private static final float BANDA = 0.115F;
    /** Donde va el centro del cartel (de la altura de la pantalla). */
    private static final float CARTEL_Y = 0.69F;

    private static Identifier tex(String nombre) {
        return Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "textures/gui/presentacion/" + nombre + ".png");
    }

    @Override
    public void extractRenderState(GuiGraphicsExtractor g, DeltaTracker delta) {
        PresentacionJefe.Ficha f = PresentacionJefe.ficha();
        if (f == null) {
            return;
        }
        Minecraft mc = Minecraft.getInstance();
        float parcial = delta.getGameTimeDeltaPartialTick(false);
        float t = PresentacionJefe.tiempo(parcial);
        float vuelta = PresentacionJefe.vuelta();
        // Todo se apaga en la vuelta de la camara.
        float apaga = 1.0F - suave(Mth.clamp((t - vuelta - 2.0F) / (PresentacionJefe.VUELTA - 4.0F), 0.0F, 1.0F));
        if (apaga <= 0.0F) {
            return;
        }

        // --- Las bandas de cine ---
        int ancho = g.guiWidth();
        int alto = g.guiHeight();
        float entra = suave(Mth.clamp(t / 10.0F, 0.0F, 1.0F));
        int banda = Math.round(alto * BANDA * entra * apaga);
        if (banda > 0) {
            g.fill(0, 0, ancho, banda, 0xF2050507);
            g.fill(0, alto - banda, ancho, alto, 0xF2050507);
            int filo = conAlfa(f.color(), 0.55F * entra * apaga);
            g.fill(0, banda, ancho, banda + 1, filo);
            g.fill(0, alto - banda - 1, ancho, alto - banda, filo);
        }

        // --- El cartel ---
        float tr = t - PresentacionJefe.revela();
        if (tr < 0.0F) {
            return;
        }
        int gs = Math.max(1, mc.getWindow().getGuiScale());
        int sw = mc.getWindow().getWidth();
        int sh = mc.getWindow().getHeight();
        int w = ANCHOS[0];
        for (int a : ANCHOS) {
            if (a <= sw * 0.62F) {
                w = a;
            }
        }
        int h = Math.round(w * 0.34F);
        String lengua = mc.options.languageCode != null && mc.options.languageCode.startsWith("es") ? "es" : "en";
        String j = f.id();
        int x0 = (sw - w) / 2;
        int y0 = Math.round(sh * CARTEL_Y - h / 2.0F);

        g.pose().pushMatrix();
        g.pose().scale(1.0F / gs, 1.0F / gs);
        // El destello: una raya de luz del color del jefe que se abre por la linea del nombre y se apaga.
        float de = suave(Mth.clamp(tr / 6.0F, 0.0F, 1.0F));
        float da = (1.0F - Mth.clamp((tr - 3.0F) / 12.0F, 0.0F, 1.0F)) * apaga;
        if (da > 0.0F) {
            int dw = Math.round(w * 1.15F * de);
            int dh = Math.round(h * 0.26F);
            g.blit(RenderPipelines.GUI_TEXTURED, DESTELLO, sw / 2 - dw / 2, y0 + Math.round(h * 0.455F) - dh / 2, 0.0F, 0.0F,
                    dw, dh, DESTELLO_ANCHO, DESTELLO_ALTO, DESTELLO_ANCHO, DESTELLO_ALTO,
                    conAlfa(mezcla(f.color(), 0xFFFFFF, 0.35F), da));
        }
        // El nombre, que se abre desde el centro y sube un poco.
        capa(g, tex(j + "_" + w + "_nombre"), x0, y0, w, h, abre(tr, 1.0F, 9.0F), 1.0F * apaga,
                Math.round(8 * (1.0F - suave(Mth.clamp(tr / 12.0F, 0.0F, 1.0F)))));
        // La linea, que se abre detras.
        capa(g, tex(j + "_" + w + "_linea"), x0, y0, w, h, abre(tr, 6.0F, 8.0F), apaga, 0);
        // Lo que es, encima: aparece y baja.
        float aa = Mth.clamp((tr - 8.0F) / 8.0F, 0.0F, 1.0F);
        capa(g, tex(j + "_" + lengua + "_" + w + "_ante"), x0, y0, w, h, 1.0F, aa * apaga,
                -Math.round(6 * (1.0F - suave(aa))));
        // El epiteto y el lema, debajo: aparecen y suben.
        float ea = Mth.clamp((tr - 13.0F) / 10.0F, 0.0F, 1.0F);
        capa(g, tex(j + "_" + lengua + "_" + w + "_epiteto"), x0, y0, w, h, 1.0F, ea * apaga,
                Math.round(6 * (1.0F - suave(ea))));
        g.pose().popMatrix();
    }

    /** Lo que se ve de una capa que se abre desde el centro (0 a 1). */
    private static float abre(float tr, float desde, float dura) {
        return suave(Mth.clamp((tr - desde) / dura, 0.0F, 1.0F));
    }

    /**
     * Una capa del cartel: se ve la franja central de "visible" (0 a 1) de su
     * ancho, con alfa "alfa", desplazada "dy" pixeles hacia abajo.
     */
    private static void capa(GuiGraphicsExtractor g, Identifier t, int x0, int y0, int w, int h, float visible, float alfa,
                             int dy) {
        if (alfa <= 0.01F || visible <= 0.0F) {
            return;
        }
        int vw = Math.round(w * visible);
        int u = (w - vw) / 2;
        g.blit(RenderPipelines.GUI_TEXTURED, t, x0 + u, y0 + dy, u, 0.0F, vw, h, vw, h, w, h, conAlfa(0xFFFFFF, alfa));
    }

    private static float suave(float k) {
        return k * k * (3.0F - 2.0F * k);
    }

    private static int conAlfa(int rgb, float a) {
        return (Math.round(Mth.clamp(a, 0.0F, 1.0F) * 255) << 24) | (rgb & 0xFFFFFF);
    }

    private static int mezcla(int a, int b, float k) {
        int r = Math.round(((a >> 16) & 255) * (1 - k) + ((b >> 16) & 255) * k);
        int gg = Math.round(((a >> 8) & 255) * (1 - k) + ((b >> 8) & 255) * k);
        int bb = Math.round((a & 255) * (1 - k) + (b & 255) * k);
        return (r << 16) | (gg << 8) | bb;
    }
}
