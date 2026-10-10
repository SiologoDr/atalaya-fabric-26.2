package com.atalaya.client;

import com.atalaya.Atalaya;
import com.atalaya.entity.AeralisEntity;
import com.atalaya.entity.ChispaAeralisEntity;
import com.atalaya.entity.MinijuegosAeralis;
import com.atalaya.item.AtalayaItems;
import net.fabricmc.fabric.api.client.rendering.v1.hud.HudElement;
import net.minecraft.client.DeltaTracker;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphicsExtractor;
import net.minecraft.client.renderer.RenderPipelines;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.Identifier;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.item.ItemStack;
import org.jspecify.annotations.Nullable;

/**
 * Lo que se ve en pantalla en los minijuegos de Aeralis (aeralis_minijuegos.py,
 * aeralis_minijuegos.png): la placa de polilla, justo bajo su barra (en lugar
 * de la linea de texto del minijuego). En el medallon, lo que pasa; en los
 * ocelos de las alas, la cuenta; debajo, la mecha del tiempo y lo que hay que
 * hacer, en grande.
 *
 *   Ocelos       a todos: el ojo abierto (rojo, "¡QUIETOS!"), entornado (ambar,
 *                "¡Van a abrirse!") o cerrado (cian, "¡AVANZA!"); las alas se
 *                encienden segun lo cerca que esta el mas cercano.
 *   Pararrayos   al que esta cargado: el rayo, "¡CARGADO!", la mecha de la
 *                carga y las descargas en las alas.
 *   La Chispa    a quien la lleva: la chispa con la cuenta encima, "¡LA LLEVAS!"
 *                (o de oro, "¡CARGADA!"), la mecha y los pases en las alas.
 *
 * Las Veletas, y los demas en la Chispa y los Pararrayos, se entienden con la
 * linea de texto bajo la barra y con lo que pasa en el mundo.
 */
public class AeralisMinijuegosHud implements HudElement {

    private static final Identifier HOJA = Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "textures/gui/aeralis_minijuegos.png");
    private static final int HOJA_W = 256;
    private static final int HOJA_H = 128;
    private static final int PLACA_W = 176;
    private static final int PLACA_H = 48;
    /** Los iconos del medallon (32 x 32), en la fila y = 48. */
    private static final int OJO_ABIERTO = 0;
    private static final int OJO_ENTORNADO = 1;
    private static final int OJO_CERRADO = 2;
    private static final int CHISPA = 3;
    private static final int CHISPA_ORO = 4;
    private static final int RAYO = 5;
    /** Los ocelos de las alas (11 x 11), en la fila y = 88, cada 12. */
    private static final int HUECO_APAGADO = 0;
    private static final int HUECO_CIAN = 1;
    private static final int HUECO_ROJO = 2;
    private static final int HUECO_ORO = 4;
    private static final int HUECO_AMBAR = 5;
    /** Donde van (centro) los de la izquierda; los de la derecha, en espejo. Los de aeralis_minijuegos.py. */
    private static final int[][] HUECOS = {{52, 18}, {36, 13}, {18, 11}, {60, 40}};

    /** Si la placa esta en pantalla (AeralisBarraHud no pone entonces su linea de texto). */
    static boolean placaVisible;

    @Override
    public void extractRenderState(GuiGraphicsExtractor g, DeltaTracker delta) {
        placaVisible = false;
        Minecraft mc = Minecraft.getInstance();
        if (mc.level == null || mc.player == null) {
            return;
        }
        AeralisEntity a = enMinijuego(mc);
        if (a == null) {
            return;
        }
        float parcial = delta.getGameTimeDeltaPartialTick(false);
        float ahora = mc.player.tickCount + parcial;
        int y = 5 + (NereaBarraHud.visible ? NereaBarraHud.ALTO + 6 : 0) + 45;
        int tipo = a.minijuego();
        if (tipo == MinijuegosAeralis.OCELOS && a.getEstado() == AeralisEntity.OCELOS) {
            ocelos(g, mc, a, y, ahora);
        } else if (tipo == MinijuegosAeralis.CHISPA) {
            chispa(g, mc, a, y, ahora, parcial);
        } else if (tipo == MinijuegosAeralis.PARARRAYOS) {
            pararrayos(g, mc, a, y, ahora, parcial);
        }
    }

    private static void ocelos(GuiGraphicsExtractor g, Minecraft mc, AeralisEntity a, int y, float ahora) {
        int ojos = MinijuegosAeralis.ojosOcelos(a.getMiniInfo());
        boolean abiertos = ojos == MinijuegosAeralis.OJOS_ABIERTOS;
        boolean aviso = ojos == MinijuegosAeralis.OJOS_AVISO;
        int cx = g.guiWidth() / 2;
        placa(g, cx, y);
        icono(g, cx, y, abiertos ? OJO_ABIERTO : aviso ? OJO_ENTORNADO : OJO_CERRADO, 0xFFFFFFFF);
        // Las alas: lo que ha avanzado el mas cercano (cuenta: lo que le falta), con el color de los ojos.
        int falta = a.getMiniCuenta();
        int total = Math.max(1, a.getMiniNecesario());
        int llenos = Mth.clamp(Math.round(8.0F * (total - falta) / total), 0, 8);
        huecos(g, cx, y, 8, llenos, abiertos ? HUECO_ROJO : aviso ? HUECO_AMBAR : HUECO_CIAN);
        Component t = Component.translatable(abiertos ? "hud.atalaya.aeralis.ocelos_quietos_grande"
                : aviso ? "hud.atalaya.aeralis.ocelos_aviso_grande" : "hud.atalaya.aeralis.ocelos_avanza_grande");
        int color = abiertos ? 0xFFFF5A6A : aviso ? 0xFFFFD86A : 0xFF7AF08A;
        grande(g, mc, t, cx, y + PLACA_H + 3, abiertos && ((int) (ahora / 4)) % 2 == 0 ? 0xFFFFB0B8 : color);
    }

    private static void chispa(GuiGraphicsExtractor g, Minecraft mc, AeralisEntity a, int y, float ahora, float parcial) {
        ChispaAeralisEntity mia = null;
        for (Entity e : mc.level.entitiesForRendering()) {
            if (e instanceof ChispaAeralisEntity c && c.getPortador() == mc.player.getId()) {
                mia = c;
            }
        }
        if (mia == null) {
            return;
        }
        int cx = g.guiWidth() / 2;
        boolean cargada = mia.cargada();
        float queda = mia.getFin() - (mc.level.getGameTime() + parcial);
        int seg = (int) Math.max(1, Math.ceil(queda / 20.0));
        boolean ultimo = seg <= 1 && ((int) (ahora / 3)) % 2 == 0;
        placa(g, cx, y);
        icono(g, cx, y, cargada ? CHISPA_ORO : CHISPA, 0x90FFFFFF);
        huecos(g, cx, y, a.getMiniNecesario(), a.getMiniCuenta(), cargada ? HUECO_ORO : HUECO_CIAN);
        // La cuenta, grande, en el medallon.
        int late = ultimo ? 0xFFFF6A6A : cargada ? 0xFFFFE08A : 0xFFFFFFFF;
        escrito(g, mc, Component.literal(Integer.toString(seg)), cx, y + 24, 2.0F, late);
        float total = cargada ? 100.0F : 60.0F;
        mecha(g, cx, y + PLACA_H + 1, queda / total, ultimo ? 0xFFFF5A5A : cargada ? 0xFFFFD86A : 0xFFC8A8FF);
        Component t = Component.translatable(cargada ? "hud.atalaya.aeralis.chispa_cargada_grande" : "hud.atalaya.aeralis.chispa_la_llevas_grande");
        grande(g, mc, t, cx, y + PLACA_H + 6, ultimo ? 0xFFFF6A6A : cargada ? 0xFFFFD86A : 0xFFE0C8FF);
    }

    private static void pararrayos(GuiGraphicsExtractor g, Minecraft mc, AeralisEntity a, int y, float ahora, float parcial) {
        long fin = 0L;
        Inventory inv = mc.player.getInventory();
        for (int i = 0; i < inv.getContainerSize(); i++) {
            ItemStack s = inv.getItem(i);
            if (s.is(AtalayaItems.PARARRAYOS_TORMENTA)) {
                fin = Math.max(fin, MinijuegosAeralis.finCarga(s));
            }
        }
        float queda = fin - (mc.level.getGameTime() + parcial);
        if (fin <= 0L || queda <= 0.0F) {
            return;
        }
        int cx = g.guiWidth() / 2;
        boolean ultimo = queda < 20.0F && ((int) (ahora / 3)) % 2 == 0;
        placa(g, cx, y);
        icono(g, cx, y, RAYO, ultimo ? 0xFFFFA0A0 : 0xFFFFFFFF);
        huecos(g, cx, y, a.getMiniNecesario(), a.getMiniCuenta(), HUECO_ORO);
        mecha(g, cx, y + PLACA_H + 1, queda / 100.0F, ultimo ? 0xFFFF5A5A : 0xFFFFD86A);
        grande(g, mc, Component.translatable("hud.atalaya.aeralis.pararrayos_cargado_grande"), cx, y + PLACA_H + 6,
                ultimo ? 0xFFFF6A6A : 0xFFFFD86A);
    }

    // --- Las piezas ---

    private static void placa(GuiGraphicsExtractor g, int cx, int y) {
        placaVisible = true;
        g.blit(RenderPipelines.GUI_TEXTURED, HOJA, cx - PLACA_W / 2, y, 0.0F, 0.0F, PLACA_W, PLACA_H, PLACA_W, PLACA_H, HOJA_W, HOJA_H,
                0xFFFFFFFF);
    }

    private static void icono(GuiGraphicsExtractor g, int cx, int y, int k, int color) {
        g.blit(RenderPipelines.GUI_TEXTURED, HOJA, cx - 16, y + 8, k * 32.0F, 48.0F, 32, 32, 32, 32, HOJA_W, HOJA_H, color);
    }

    /** Los ocelos de las alas: n huecos (hasta ocho, de dentro a fuera y a un lado y al otro), los primeros 'llenos' encendidos. */
    private static void huecos(GuiGraphicsExtractor g, int cx, int y, int n, int llenos, int encendido) {
        int x0 = cx - PLACA_W / 2;
        for (int i = 0; i < Math.min(8, n); i++) {
            int[] h = HUECOS[i / 2];
            int hx = i % 2 == 0 ? h[0] : PLACA_W - 1 - h[0];
            int k = i < llenos ? encendido : HUECO_APAGADO;
            g.blit(RenderPipelines.GUI_TEXTURED, HOJA, x0 + hx - 5, y + h[1] - 5, k * 12.0F, 88.0F, 11, 11, 11, 11, HOJA_W, HOJA_H,
                    0xFFFFFFFF);
        }
    }

    /** La mecha del tiempo, bajo el medallon: se consume hacia el centro desde los dos lados. */
    private static void mecha(GuiGraphicsExtractor g, int cx, int y, float k, int color) {
        int media = 44;
        int w = Math.round(media * Mth.clamp(k, 0.0F, 1.0F));
        g.fill(cx - media - 1, y, cx + media + 1, y + 3, 0xC00A0E18);
        if (w > 0) {
            g.fill(cx - w, y + 1, cx + w, y + 2, color);
            g.fill(cx - w - 1, y, cx - w + 1, y + 3, 0xFFFFFFFF);
            g.fill(cx + w - 1, y, cx + w + 1, y + 3, 0xFFFFFFFF);
        }
    }

    /** Lo que hay que hacer, en grande (el doble si cabe sin tocar la mira; si no, normal). */
    private static void grande(GuiGraphicsExtractor g, Minecraft mc, Component t, int cx, int y, int color) {
        float escala = y + 20 <= g.guiHeight() / 2 - 6 ? 2.0F : 1.0F;
        escrito(g, mc, t, cx, y + (int) (4.5F * escala), escala, color);
    }

    /** Un texto centrado en (x, y) a la escala que sea. */
    private static void escrito(GuiGraphicsExtractor g, Minecraft mc, Component t, int x, int y, float escala, int color) {
        g.pose().pushMatrix();
        g.pose().translate(x, y);
        g.pose().scale(escala, escala);
        g.centeredText(mc.font, t, 0, -4, color);
        g.pose().popMatrix();
    }

    /** La Aeralis con un minijuego en marcha mas cercana (a menos de 120 bloques). */
    private static @Nullable AeralisEntity enMinijuego(Minecraft mc) {
        AeralisEntity mejor = null;
        double d = 120 * 120;
        for (Entity e : mc.level.entitiesForRendering()) {
            if (e instanceof AeralisEntity a && a.minijuego() != MinijuegosAeralis.NINGUNO && !a.isRemoved() && !a.isDeadOrDying()) {
                double dd = a.distanceToSqr(mc.player);
                if (dd < d) {
                    d = dd;
                    mejor = a;
                }
            }
        }
        return mejor;
    }
}
