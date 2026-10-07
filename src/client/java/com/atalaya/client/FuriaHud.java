package com.atalaya.client;

import com.atalaya.entity.PresasJefe;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphicsExtractor;
import net.minecraft.util.Mth;

/**
 * La cuenta atras de la Furia en las barras de los jefes: una franja clara del
 * color de la Furia, por dentro de la vida y arriba, que se acorta en los 30 s
 * que dura (mientras es inmune). La misma en los cuatro.
 */
public final class FuriaHud {

    private FuriaHud() {
    }

    private static int mezclar(int a, int b, float k) {
        int r = Math.round(((a >> 16) & 0xFF) * (1 - k) + ((b >> 16) & 0xFF) * k);
        int g = Math.round(((a >> 8) & 0xFF) * (1 - k) + ((b >> 8) & 0xFF) * k);
        int bl = Math.round((a & 0xFF) * (1 - k) + (b & 0xFF) * k);
        return (r << 16) | (g << 8) | bl;
    }

    /** fin: el tiempo del mundo en que se acaba (getFuriaFin); hx, hy: la esquina del hueco de la vida. */
    public static void cuentaAtras(GuiGraphicsExtractor g, long fin, int hx, int hy, int ancho, int color, float parcial) {
        Minecraft mc = Minecraft.getInstance();
        if (fin <= 0 || mc.level == null) {
            return;
        }
        float queda = fin - mc.level.getGameTime() - parcial;
        if (queda <= 0) {
            return;
        }
        // Por dentro de la barra, arriba: una franja clara (el color de la Furia
        // aclarado) que se acorta; lo que ya ha pasado, oscurecido. Fuera del
        // hueco se confundia con el marco.
        float k = Mth.clamp(queda / PresasJefe.FURIA_TICKS, 0.0F, 1.0F);
        int w = Math.round(ancho * k);
        int claro = mezclar(color, 0xFFFFFF, 0.55F);
        g.fill(hx + w, hy, hx + ancho, hy + 2, 0x70000000);
        g.fill(hx, hy, hx + w, hy + 2, 0xF0000000 | claro);
        g.fill(hx, hy + 2, hx + w, hy + 3, 0x60000000);
        if (w > 0) {
            g.fill(hx + w - 1, hy, hx + w, hy + 3, 0xFFFFFFFF);
        }
    }
}
