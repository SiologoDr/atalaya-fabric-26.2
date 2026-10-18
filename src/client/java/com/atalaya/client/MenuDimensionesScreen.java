package com.atalaya.client;

import com.atalaya.Atalaya;
import com.atalaya.net.AtalayaRed;
import net.fabricmc.fabric.api.client.networking.v1.ClientPlayNetworking;
import net.minecraft.ChatFormatting;
import net.minecraft.client.gui.GuiGraphicsExtractor;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.client.input.MouseButtonEvent;
import net.minecraft.client.renderer.RenderPipelines;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.Identifier;
import net.minecraft.util.FormattedCharSequence;

import java.util.List;

/**
 * El menu de las dimensiones (/atalaya menu dimensiones; CambiosDificultad en el servidor). Juan: "vamos a tener uno
 * para las dimensiones, con ON y OFF en Nether y End". Dos tarjetas, con su dibujo animado (el remolino del portal del
 * Nether; las estrellas del portal del End), su nombre, si esta abierta o cerrada (y el candado encima si lo esta) y su
 * interruptor. Se abren y se cierran al momento.
 */
public class MenuDimensionesScreen extends Screen {

    private static final Identifier PANEL = sprite("panel");
    private static final Identifier FILA = sprite("fila");
    private static final Identifier FILA_ENCIMA = sprite("fila_encima");
    private static final Identifier TITULO = sprite("titulo_dimensiones");
    private static final Identifier ON = sprite("interruptor_on");
    private static final Identifier OFF = sprite("interruptor_off");
    private static final Identifier CANDADO = sprite("candado");
    private static final Identifier[] DIBUJO = {sprite("nether"), sprite("end")};
    private static final String[] NOMBRE = {"NETHER", "END"};
    private static final int[] COLOR = {0xFFFF8A5A, 0xFFC8B4FF};
    private static final int TITULO_W = 137;
    private static final int TITULO_H = 18;

    private final boolean[] abierta = new boolean[2];
    private int px;
    private int py;
    private int pw;
    private int ph;

    public MenuDimensionesScreen(boolean nether, boolean end) {
        super(Component.literal("Dimensiones"));
        actualizar(nether, end);
    }

    private static Identifier sprite(String nombre) {
        return Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "menu/" + nombre);
    }

    public void actualizar(boolean nether, boolean end) {
        abierta[0] = nether;
        abierta[1] = end;
    }

    @Override
    protected void init() {
        pw = Math.min(340, width - 24);
        ph = Math.min(230, height - 20);
        px = (width - pw) / 2;
        py = (height - ph) / 2;
    }

    @Override
    public boolean isPauseScreen() {
        return false;
    }

    @Override
    public void extractBackground(GuiGraphicsExtractor g, int mx, int my, float parcial) {
        g.fill(0, 0, width, height, 0xB4080410);
    }

    @Override
    public void extractRenderState(GuiGraphicsExtractor g, int mx, int my, float parcial) {
        g.blitSprite(RenderPipelines.GUI_TEXTURED, PANEL, px, py, pw, ph);
        g.blitSprite(RenderPipelines.GUI_TEXTURED, TITULO, px + (pw - TITULO_W) / 2, py + 12, TITULO_W, TITULO_H);
        for (int i = 0; i < 2; i++) {
            int[] c = tarjeta(i);
            boolean encima = mx >= c[0] && mx < c[0] + c[2] && my >= c[1] && my < c[1] + c[3];
            g.blitSprite(RenderPipelines.GUI_TEXTURED, encima ? FILA_ENCIMA : FILA, c[0], c[1], c[2], c[3]);
            int ax = c[0] + (c[2] - 64) / 2;
            int ay = c[1] + 8;
            g.blitSprite(RenderPipelines.GUI_TEXTURED, DIBUJO[i], ax, ay, 64, 64);
            if (!abierta[i]) {
                // Cerrada: el dibujo apagado y el candado encima (a escala 2, sus pixeles enteros).
                g.fill(ax + 2, ay + 2, ax + 62, ay + 62, 0xA0000000);
                g.blitSprite(RenderPipelines.GUI_TEXTURED, CANDADO, ax + 16, ay + 16, 32, 32);
            }
            int cx = c[0] + c[2] / 2;
            g.centeredText(font, Component.literal(NOMBRE[i]).withStyle(ChatFormatting.BOLD), cx, ay + 70, COLOR[i]);
            g.centeredText(font, Component.literal(abierta[i] ? "ABIERTO" : "CERRADO"), cx, ay + 82,
                    abierta[i] ? 0xFF6EE36E : 0xFFFF6A5A);
            g.blitSprite(RenderPipelines.GUI_TEXTURED, abierta[i] ? ON : OFF, cx - 17, c[1] + c[3] - 24, 34, 16);
        }
        List<FormattedCharSequence> lineas = font.split(Component.literal(
                "Cerrada: sus portales no llevan a ninguna parte y quien esté dentro vuelve al mundo."), pw - 40);
        for (int i = 0; i < Math.min(2, lineas.size()); i++) {
            g.centeredText(font, lineas.get(i), width / 2, py + ph - 26 + i * 10, 0xFF9A90AA);
        }
        super.extractRenderState(g, mx, my, parcial);
    }

    /** Donde va la tarjeta i: x, y, ancho y alto. */
    private int[] tarjeta(int i) {
        int hueco = 12;
        int w = (pw - 40 - hueco) / 2;
        int h = ph - 40 - 34;
        return new int[]{px + 20 + i * (w + hueco), py + 38, w, h};
    }

    @Override
    public boolean mouseClicked(MouseButtonEvent evento, boolean doble) {
        if (evento.button() == 0) {
            for (int i = 0; i < 2; i++) {
                int[] c = tarjeta(i);
                if (evento.x() >= c[0] && evento.x() < c[0] + c[2] && evento.y() >= c[1] && evento.y() < c[1] + c[3]) {
                    ClientPlayNetworking.send(new AtalayaRed.PulsaDimension(i));
                    MenusCliente.sonar(!abierta[i]);
                    return true;
                }
            }
        }
        return super.mouseClicked(evento, doble);
    }
}
