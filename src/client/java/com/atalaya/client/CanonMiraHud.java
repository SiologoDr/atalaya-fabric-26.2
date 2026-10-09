package com.atalaya.client;

import com.atalaya.Atalaya;
import net.minecraft.client.DeltaTracker;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphicsExtractor;
import net.minecraft.client.renderer.RenderPipelines;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.Identifier;
import net.minecraft.util.Mth;

/**
 * El catalejo del Canon del Naufragio (Juan: "que sea como el telescopio y ahi
 * este la mira"): mientras se va subido, la vista se acerca (CanonZoomMixin) y
 * se mira por un catalejo propio, como con el de vanilla pero nuestro
 * (nerea_catalejo.png): negro alrededor, el aro de bronce verdeado, la cruz fina
 * y las marcas de caida. En el centro, la mira (nerea_mira_canon.png): blanca,
 * y dorada y latiendo si el camino de la bala da en Nerea, con "EN EL BLANCO".
 * Abajo, dentro del cristal, si esta cargado o si falta la bala. El camino de la
 * bala en el mundo lo pinta CanonNaufragioRenderer; la cuenta, CanonMira.
 */
public final class CanonMiraHud {

    private static final Identifier CATALEJO = Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "textures/gui/nerea_catalejo.png");
    private static final Identifier MIRA = Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "textures/gui/nerea_mira_canon.png");
    private static final int LADO_MIRA = 33;
    private static final int LADO_CATALEJO = 128;
    /** Lo que tarda en abrirse el catalejo al subirse (ticks). */
    private static final float ABRE = 6.0F;

    private static long subidoDesde = -1;

    private CanonMiraHud() {
    }

    /** Lo llama la cruz de vanilla cuando no se va en un canon: se olvida de cuando se subio. */
    public static void bajado() {
        subidoDesde = -1;
    }

    public static void dibujar(GuiGraphicsExtractor g, DeltaTracker tiempo) {
        Minecraft mc = Minecraft.getInstance();
        if (mc.player == null || mc.level == null) {
            return;
        }
        float parcial = tiempo.getGameTimeDeltaPartialTick(false);
        if (subidoDesde < 0) {
            subidoDesde = mc.level.getGameTime();
        }
        float t = mc.player.tickCount + parcial;
        float abre = Mth.clamp((mc.level.getGameTime() - subidoDesde + parcial) / ABRE, 0.0F, 1.0F);
        abre = 1.0F - (1.0F - abre) * (1.0F - abre);
        int w = g.guiWidth();
        int h = g.guiHeight();
        int cx = w / 2;
        int cy = h / 2;
        // El catalejo: un cuadrado del alto de la pantalla (se abre un poco al subirse) y negro alrededor.
        int lado = Math.round(h * (0.75F + 0.33F * abre));
        int x0 = cx - lado / 2;
        int y0 = cy - lado / 2;
        int negro = 0xFF040608;
        g.fill(0, 0, w, Math.max(0, y0), negro);
        g.fill(0, Math.min(h, y0 + lado), w, h, negro);
        g.fill(0, Math.max(0, y0), Math.max(0, x0), Math.min(h, y0 + lado), negro);
        g.fill(Math.min(w, x0 + lado), Math.max(0, y0), w, Math.min(h, y0 + lado), negro);
        g.blit(RenderPipelines.GUI_TEXTURED, CATALEJO, x0, y0, 0.0F, 0.0F, lado, lado, LADO_CATALEJO, LADO_CATALEJO,
                LADO_CATALEJO, LADO_CATALEJO, 0xFFFFFFFF);
        // La mira del centro.
        boolean blanco = CanonMira.enNerea();
        int color = blanco ? 0xFFFFD24A : 0xE6E8F6FF;
        int m = blanco ? LADO_MIRA + Math.round(2 * (0.5F + 0.5F * Mth.sin(t * 0.5F))) * 2 : LADO_MIRA;
        g.blit(RenderPipelines.GUI_TEXTURED, MIRA, cx - m / 2, cy - m / 2, 0.0F, 0.0F, m, m, LADO_MIRA, LADO_MIRA, LADO_MIRA,
                LADO_MIRA, color);
        if (blanco) {
            texto(g, mc, Component.translatable("hud.atalaya.nerea.canon_en_blanco"), cx, cy - m / 2 - 12, 0xFFFFD24A);
        }
        Component abajo = CanonMira.cargado() ? Component.translatable("hud.atalaya.nerea.canon_fuego")
                : Component.translatable("hud.atalaya.nerea.canon_falta");
        texto(g, mc, abajo, cx, cy + LADO_MIRA / 2 + 14, CanonMira.cargado() ? 0xFFFFE07A : 0xFFB8C4CC);
    }

    private static void texto(GuiGraphicsExtractor g, Minecraft mc, Component c, int cx, int y, int color) {
        g.text(mc.font, c, cx - mc.font.width(c) / 2, y, color, true);
    }
}
