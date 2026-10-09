package com.atalaya.client;

import com.atalaya.Atalaya;
import com.atalaya.entity.NereaEntity;
import net.fabricmc.fabric.api.client.rendering.v1.hud.HudElement;
import net.minecraft.client.DeltaTracker;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphicsExtractor;
import net.minecraft.client.renderer.RenderPipelines;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.Identifier;
import net.minecraft.util.Mth;

/**
 * La pantalla del Duelo de Canto de Nerea (la del elegido), rehecha en octubre
 * de 2026 para que se vea de Minecraft (Juan: "mas interactivo y con un diseno
 * de MC"): todo son texturas pixel a pixel al tamano en que se pintan
 * (nerea_duelo_hud.py) y la letra del juego.
 *
 *   - el panel de bloques de prismarina, con el titulo y el medidor del duelo:
 *     se llena con cada acierto hacia la cara de Nerea; la marca de oro es lo
 *     que hace falta (12 de 16). Dorado al llegar, rojo si ya no se puede;
 *   - cuatro carriles de agua de color por los que bajan las notas (corcheas y
 *     negras de pixeles, cada una con su brillo), hasta la cuerda de oro del arpa;
 *   - la cuerda vibra donde aciertas y sale un estallido del color del carril
 *     (dorado si es perfecta); el carril se enciende al pulsar su tecla y se pone
 *     rojo al fallar;
 *   - abajo, las teclas A S D F, que se hunden al pulsarlas;
 *   - a la derecha, el letrero de cada nota (PERFECTO, BIEN, FALLO) que salta, y
 *     la racha;
 *   - la cuenta atras grande (3, 2, 1, CANTA) y el final (GANASTE o TRANCE);
 *   - con cada fallo, la pantalla se tine de violeta por los bordes: el trance
 *     que se acerca.
 *
 * Va a la izquierda, a media altura, sin tapar el corazon de la barra del jefe.
 * El estado lo lleva DueloCantoCliente.
 */
public class DueloCantoHud implements HudElement {

    private static final Identifier PANEL = tex("nerea_duelo_panel");
    private static final Identifier CUERDA = tex("nerea_duelo_cuerda");
    private static final Identifier TECLA = tex("nerea_duelo_tecla");
    private static final Identifier NOTAS = tex("nerea_duelo_notas");
    private static final Identifier HALO = tex("nerea_duelo_halo");
    private static final Identifier ESTALLIDO = tex("nerea_duelo_estallido");
    private static final Identifier MEDIDOR = tex("nerea_duelo_medidor");
    private static final Identifier CARA = tex("nerea_duelo_nerea");

    // Las medidas de nerea_duelo_hud.py.
    private static final int PANEL_W = 100;
    private static final int PANEL_H = 170;
    private static final int CARRIL = 22;
    private static final int CARRILES_X = 6;
    private static final int TITULO_Y = 4;
    private static final int MEDIDOR_Y = 19;
    private static final int CARRILES_Y = 32;
    private static final int LINEA_Y = 128;
    private static final int TECLAS_Y = 144;
    private static final int MEDIDOR_W = 84;
    private static final int LLENO_W = 70;
    /** Lo mas arriba que empieza el panel: por debajo del corazon de la barra del jefe. */
    private static final int TECHO = 54;

    private static final int[] COLOR = {0x4FD8F0, 0x9A7BFF, 0xD45AF0, 0xF06AA8};
    private static final String[] TECLAS = {"A", "S", "D", "F"};

    private static Identifier tex(String nombre) {
        return Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "textures/gui/" + nombre + ".png");
    }

    @Override
    public void extractRenderState(GuiGraphicsExtractor g, DeltaTracker tiempo) {
        Minecraft mc = Minecraft.getInstance();
        float parcial = tiempo.getGameTimeDeltaPartialTick(false);
        boolean activo = DueloCantoCliente.activo();
        float desdeFin = DueloCantoCliente.desdeFin(parcial);
        vineta(g, DueloCantoCliente.trance());
        if (!activo && desdeFin > 50) {
            return;
        }
        // Al acabar se queda un momento y se apaga: el alfa va en el tinte de todo.
        float k = activo ? 1.0F : Mth.clamp((50 - desdeFin) / 8.0F, 0.0F, 1.0F);
        int a = Math.round(255 * k);
        if (a <= 4) {
            return;
        }
        int blanco = (a << 24) | 0xFFFFFF;
        float reloj = DueloCantoCliente.reloj(parcial);
        int x0 = 6;
        int y0 = Math.max((g.guiHeight() - PANEL_H) / 2, TECHO);
        if (y0 + PANEL_H > g.guiHeight() - 2) {
            y0 = Math.max(2, g.guiHeight() - PANEL_H - 2);
        }
        pieza(g, PANEL, x0, y0, PANEL_W, PANEL_H, blanco);
        int cx = x0 + CARRILES_X;
        // El titulo.
        Component titulo = Component.translatable("hud.atalaya.nerea.duelo_titulo");
        g.text(mc.font, titulo, cx + 44 - mc.font.width(titulo) / 2, y0 + TITULO_Y + 2, (a << 24) | 0xBFF4FF, true);
        medidor(g, mc, cx + 2, y0 + MEDIDOR_Y + 2, a);
        pieza(g, CARA, cx + 88 - 12, y0 + MEDIDOR_Y - 1, 11, 11, blanco);

        // Los carriles: se encienden al pulsar y se ponen rojos al fallar.
        int arriba = y0 + CARRILES_Y;
        int linea = y0 + LINEA_Y;
        for (int c = 0; c < 4; c++) {
            int lx = cx + c * CARRIL + 1;
            float dp = DueloCantoCliente.desdePulsado(c, parcial);
            if (dp < 6) {
                int al = Math.round(90 * (1 - dp / 6) * k);
                g.fillGradient(lx, arriba, lx + CARRIL - 1, linea + 10, COLOR[c], (al << 24) | COLOR[c]);
            }
            float df = DueloCantoCliente.desdeFallo(c, parcial);
            if (df < 8) {
                int al = Math.round(110 * (1 - df / 8) * k);
                g.fill(lx, linea - 20, lx + CARRIL - 1, linea + 10, (al << 24) | 0xFF2A3A);
            }
        }
        // Las notas, con su brillo; el brillo crece al acercarse a la cuerda.
        float ahora = DueloCantoCliente.ahora(parcial);
        int[][] notas = DueloCantoCliente.notas();
        int[] juicio = DueloCantoCliente.juicio();
        float antes = DueloCantoCliente.ANTES;
        for (int i = 0; i < notas.length && activo; i++) {
            float faltan = notas[i][0] - ahora;
            if (juicio[i] != 0 || faltan > antes || faltan < -DueloCantoCliente.VENTANA - 2) {
                continue;
            }
            int c = notas[i][1];
            int y = linea - Math.round((linea - arriba - 6) * faltan / antes);
            int nx = cx + c * CARRIL + 5;
            float cerca = Mth.clamp(1.0F - Math.abs(faltan) / 8.0F, 0.0F, 1.0F);
            int halo = Math.round((90 + 140 * cerca) * k);
            pieza(g, HALO, nx - 2, y - 8, 16, 16, (halo << 24) | COLOR[c]);
            g.blit(RenderPipelines.GUI_TEXTURED, NOTAS, nx, y - 6, DueloCantoCliente.forma(i) * 12.0F, 0.0F, 12, 12, 12, 12,
                    48, 12, (a << 24) | COLOR[c]);
        }
        // La cuerda del arpa, un trozo por carril: vibra donde aciertas.
        for (int c = 0; c < 4; c++) {
            float da = DueloCantoCliente.desdeAcierto(c, parcial);
            int vibra = da < 8 ? Math.round(Mth.sin(reloj * 2.7F) * 2.0F * (1 - da / 8)) : 0;
            g.blit(RenderPipelines.GUI_TEXTURED, CUERDA, cx + c * CARRIL, linea - 1 + vibra, c * CARRIL, 0.0F, CARRIL, 3,
                    CARRIL, 3, 88, 3, blanco);
        }
        // Los estallidos al acertar.
        for (int c = 0; c < 4; c++) {
            float da = DueloCantoCliente.desdeAcierto(c, parcial);
            if (da >= 8) {
                continue;
            }
            float t = da / 8;
            int al = Math.round(255 * (1 - t) * k);
            int color = DueloCantoCliente.perfecto(c) ? 0xFFD24A : COLOR[c];
            float escala = 0.5F + 1.1F * t;
            g.pose().pushMatrix();
            g.pose().translate(cx + c * CARRIL + CARRIL / 2.0F, linea);
            g.pose().scale(escala, escala);
            pieza(g, ESTALLIDO, -12, -12, 24, 24, (al << 24) | color);
            g.pose().popMatrix();
        }
        // Las teclas: se hunden al pulsarlas; la letra, del color de su carril.
        for (int c = 0; c < 4; c++) {
            int tx = cx + c * CARRIL + 1;
            int ty = y0 + TECLAS_Y + 1;
            boolean hundida = DueloCantoCliente.desdePulsado(c, parcial) < 4;
            boolean acierto = DueloCantoCliente.desdeAcierto(c, parcial) < 6;
            int tinte = acierto ? (a << 24) | NereaDibujo.claro(COLOR[c], 0.6F) : blanco;
            g.blit(RenderPipelines.GUI_TEXTURED, TECLA, tx, ty, 0.0F, hundida ? 20.0F : 0.0F, 20, 20, 20, 20, 20, 40, tinte);
            int w = mc.font.width(TECLAS[c]);
            int color = acierto ? 0xFFFFFF : COLOR[c];
            g.text(mc.font, TECLAS[c], tx + 10 - w / 2, ty + (hundida ? 7 : 5), (a << 24) | color, true);
        }
        int dx = x0 + PANEL_W + 5;
        // El letrero de la ultima nota: salta y se apaga.
        float dj = DueloCantoCliente.desdeJuicio(parcial);
        if (activo && dj < 14) {
            int j = DueloCantoCliente.ultimoJuicio();
            String clave = j == 2 ? "hud.atalaya.nerea.duelo_perfecto" : j == 1 ? "hud.atalaya.nerea.duelo_bien"
                    : "hud.atalaya.nerea.duelo_fallo_nota";
            int color = j == 2 ? 0xFFE07A : j == 1 ? 0xBFF4FF : 0xFF6A6A;
            float salto = dj < 4 ? 1.5F - 0.5F * (dj / 4) : 1.0F;
            int al = Math.round(255 * Mth.clamp((14 - dj) / 5.0F, 0.0F, 1.0F) * k);
            escrito(g, mc, Component.translatable(clave), dx, linea - 4 - Math.round(dj * 0.6F), salto, (al << 24) | color, false);
        }
        // La racha.
        int racha = DueloCantoCliente.racha();
        if (activo && racha >= 2) {
            float dr = DueloCantoCliente.desdeRacha(parcial);
            float salto = dr < 4 ? 2.6F - 0.6F * (dr / 4) : 2.0F;
            g.text(mc.font, Component.translatable("hud.atalaya.nerea.duelo_racha"), dx, arriba + 18, (a << 24) | 0x8FD0BD, true);
            escrito(g, mc, Component.literal("x" + racha), dx, arriba + 30, salto, (a << 24) | (racha >= 8 ? 0xFFD24A : 0xBFF4FF),
                    false);
        }
        int mitadX = cx + 44;
        int mitadY = arriba + (linea - arriba) / 2;
        // La cuenta atras, grande, y a cantar.
        if (activo && ahora < 0) {
            int seg = Mth.clamp((int) Math.ceil(-ahora / 20.0F), 1, 3);
            float dentro = (-ahora) % 20 / 20.0F;
            escrito(g, mc, Component.literal(String.valueOf(seg)), mitadX, mitadY - 12, 2.5F + dentro, blanco, true);
            escrito(g, mc, Component.translatable("hud.atalaya.nerea.duelo_prepara"), mitadX, mitadY + 18, 1.0F,
                    (a << 24) | 0xBFF4FF, true);
        } else if (activo && ahora < 14) {
            int al = Math.round(255 * (1 - ahora / 14) * k);
            escrito(g, mc, Component.translatable("hud.atalaya.nerea.duelo_canta"), mitadX, mitadY - 10, 2.0F + ahora / 14,
                    (al << 24) | 0xFFD24A, true);
        }
        if (!activo) {
            boolean gano = DueloCantoCliente.gano();
            float salto = desdeFin < 5 ? 3.2F - 0.8F * (desdeFin / 5) : 2.4F;
            escrito(g, mc, Component.translatable(gano ? "hud.atalaya.nerea.duelo_ganaste" : "hud.atalaya.nerea.duelo_perdiste"),
                    mitadX, mitadY - 10, salto, (a << 24) | (gano ? 0xFFD24A : 0xFF8AC8), true);
        }
    }

    /** El medidor: se llena con los aciertos hacia la cara de Nerea; la marca de oro, lo que hace falta. */
    private static void medidor(GuiGraphicsExtractor g, Minecraft mc, int x, int y, int a) {
        int aciertos = DueloCantoCliente.aciertos();
        int fallos = DueloCantoCliente.fallos();
        int total = NereaEntity.DUELO_NOTAS;
        int hace = NereaEntity.DUELO_ACIERTOS;
        boolean llega = aciertos >= hace;
        boolean imposible = total - fallos < hace;
        int color = llega ? 0xFFD24A : imposible ? 0xD8303C : 0x4FD8F0;
        int lleno = Math.round(LLENO_W * Math.min(1.0F, aciertos / (float) total));
        if (lleno > 0) {
            g.blit(RenderPipelines.GUI_TEXTURED, MEDIDOR, x, y, 0.0F, 0.0F, lleno, 6, lleno, 6, MEDIDOR_W, 6, (a << 24) | color);
        }
        int marca = x + Math.round(LLENO_W * hace / (float) total);
        g.fill(marca, y - 1, marca + 1, y + 7, (a << 24) | 0xFFE08A);
        String cuenta = aciertos + "/" + hace;
        g.text(mc.font, cuenta, marca - mc.font.width(cuenta) - 2, y - 1, (a << 24) | 0xFFFFFF, true);
    }

    /** Un texto con la letra del juego, a escala, desde x (o centrado en x). */
    private static void escrito(GuiGraphicsExtractor g, Minecraft mc, Component c, int x, int y, float escala, int color,
                                boolean centrado) {
        g.pose().pushMatrix();
        g.pose().translate(x, y);
        g.pose().scale(escala, escala);
        int w = mc.font.width(c);
        g.text(mc.font, c, centrado ? -w / 2 : 0, 0, color, true);
        g.pose().popMatrix();
    }

    /** El trance que se acerca: los bordes de la pantalla se tinen de violeta. */
    private static void vineta(GuiGraphicsExtractor g, float trance) {
        if (trance <= 0.01F) {
            return;
        }
        int w = g.guiWidth();
        int h = g.guiHeight();
        int al = Math.round(150 * Math.min(1.0F, trance));
        int violeta = 0x7A1AA8;
        int banda = h / 4;
        g.fillGradient(0, 0, w, banda, (al << 24) | violeta, violeta);
        g.fillGradient(0, h - banda, w, h, violeta, (al << 24) | violeta);
        int tiras = 10;
        int ancho = Math.max(1, w / 6 / tiras);
        for (int i = 0; i < tiras; i++) {
            int ai = Math.round(al * (1.0F - i / (float) tiras)) / 2;
            g.fill(i * ancho, 0, (i + 1) * ancho, h, (ai << 24) | violeta);
            g.fill(w - (i + 1) * ancho, 0, w - i * ancho, h, (ai << 24) | violeta);
        }
    }

    private static void pieza(GuiGraphicsExtractor g, Identifier t, int x, int y, int w, int h, int tinte) {
        g.blit(RenderPipelines.GUI_TEXTURED, t, x, y, 0.0F, 0.0F, w, h, w, h, w, h, tinte);
    }
}
