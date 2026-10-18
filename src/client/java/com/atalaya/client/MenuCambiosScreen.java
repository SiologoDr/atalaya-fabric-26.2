package com.atalaya.client;

import com.atalaya.Atalaya;
import com.atalaya.cambios.Cambio;
import com.atalaya.net.AtalayaRed;
import net.fabricmc.fabric.api.client.networking.v1.ClientPlayNetworking;
import net.minecraft.ChatFormatting;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphicsExtractor;
import net.minecraft.client.gui.components.EditBox;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.client.input.MouseButtonEvent;
import net.minecraft.client.renderer.RenderPipelines;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.Identifier;
import net.minecraft.util.FormattedCharSequence;
import net.minecraft.util.Mth;

import java.text.Normalizer;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;

/**
 * El menu de los cambios de dificultad (/atalaya menu cambios; CambiosDificultad en el servidor). Juan: "un menu
 * personalizado bonito, no el de Minecraft ... deben verse ON u OFF ... que haya un buscador".
 *
 * Una pantalla propia con el aire de la Ruleta (menus_cambios.py): el panel de laca con su marco de oro, el titulo en
 * nuestra letra con el brillo que lo cruza, el buscador y una fila por cambio con su icono, su titulo, su texto y el
 * interruptor (ON, OFF, o dorado mientras espera a que pare su Ruleta). Pulsar una fila apagada lanza la Ruleta y cierra
 * el menu (para verla); pulsar una encendida la apaga al momento. Lo que dura dice cuanto le queda.
 */
public class MenuCambiosScreen extends Screen {

    private static final Identifier PANEL = sprite("panel");
    private static final Identifier FILA = sprite("fila");
    private static final Identifier FILA_ENCIMA = sprite("fila_encima");
    private static final Identifier BUSCADOR = sprite("buscador");
    private static final Identifier LUPA = sprite("lupa");
    private static final Identifier TITULO = sprite("titulo_cambios");
    private static final Identifier ON = sprite("interruptor_on");
    private static final Identifier OFF = sprite("interruptor_off");
    private static final Identifier ESPERA = sprite("interruptor_espera");
    private static final int TITULO_W = 251;
    private static final int TITULO_H = 18;
    private static final int FILA_ALTO = 40;
    private static final int FILA_HUECO = 4;
    private static final int AMARILLO = 0xFFFFD23A;
    private static final int TEXTO = 0xFFD8CCE4;
    private static final int APAGADO = 0xFF9A90AA;

    /** El estado de cada cambio (por su id) y el tiempo de juego en que llego. */
    private final Map<String, AtalayaRed.EstadoCambio> estados = new HashMap<>();
    private long recibido;
    private EditBox buscador;
    private String filtro = "";
    private float desplazado;
    private int px;
    private int py;
    private int pw;
    private int ph;

    public MenuCambiosScreen(List<AtalayaRed.EstadoCambio> estados) {
        super(Component.literal("Cambios de dificultad"));
        actualizar(estados);
    }

    private static Identifier sprite(String nombre) {
        return Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "menu/" + nombre);
    }

    /** Escribe en el buscador (lo usa FotosPrueba para probarlo). */
    public void buscar(String texto) {
        buscador.setValue(texto);
    }

    /** El servidor manda el estado nuevo (alguien ha pulsado, o ha salido el aviso de una Ruleta). */
    public void actualizar(List<AtalayaRed.EstadoCambio> nuevos) {
        estados.clear();
        for (AtalayaRed.EstadoCambio e : nuevos) {
            estados.put(e.id(), e);
        }
        Minecraft mc = Minecraft.getInstance();
        recibido = mc.level != null ? mc.level.getGameTime() : 0;
    }

    @Override
    protected void init() {
        pw = Math.min(400, width - 24);
        ph = height - 20;
        px = (width - pw) / 2;
        py = 10;
        String antes = buscador != null ? buscador.getValue() : filtro;
        buscador = new EditBox(font, px + 36, py + 38, pw - 60, 10, Component.literal("Buscar"));
        buscador.setBordered(false);
        buscador.setMaxLength(40);
        buscador.setTextColor(0xFFF4ECFA);
        buscador.setValue(antes);
        buscador.setResponder(t -> {
            filtro = t;
            desplazado = 0;
        });
        addRenderableWidget(buscador);
        setInitialFocus(buscador);
    }

    @Override
    public boolean isPauseScreen() {
        return false;
    }

    // ------------------------------------------------------------------
    //  Lo que se ve
    // ------------------------------------------------------------------

    @Override
    public void extractBackground(GuiGraphicsExtractor g, int mx, int my, float parcial) {
        // El mundo, apagado (sin el desenfoque ni el fondo de los menus de Minecraft).
        g.fill(0, 0, width, height, 0xB4080410);
    }

    @Override
    public void extractRenderState(GuiGraphicsExtractor g, int mx, int my, float parcial) {
        g.blitSprite(RenderPipelines.GUI_TEXTURED, PANEL, px, py, pw, ph);
        g.blitSprite(RenderPipelines.GUI_TEXTURED, TITULO, px + (pw - TITULO_W) / 2, py + 12, TITULO_W, TITULO_H);
        g.blitSprite(RenderPipelines.GUI_TEXTURED, BUSCADOR, px + 20, py + 34, pw - 40, 16);
        g.blitSprite(RenderPipelines.GUI_TEXTURED, LUPA, px + 24, py + 37, 10, 10);
        super.extractRenderState(g, mx, my, parcial);
        // La pista del buscador, tambien con el foco puesto (la de Minecraft solo sale sin el).
        if (buscador.getValue().isEmpty()) {
            g.text(font, Component.literal("Buscar un cambio..."), px + 38, py + 38, 0xFF7A6A8E, false);
        }

        List<Cambio> lista = visibles();
        int arriba = listaArriba();
        int abajo = listaAbajo();
        int contenido = lista.size() * (FILA_ALTO + FILA_HUECO) - FILA_HUECO;
        desplazado = Mth.clamp(desplazado, 0, Math.max(0, contenido - (abajo - arriba)));
        g.enableScissor(px + 14, arriba, px + pw - 14, abajo);
        int y = arriba - Math.round(desplazado);
        for (Cambio c : lista) {
            if (y + FILA_ALTO > arriba && y < abajo) {
                fila(g, c, px + 20, y, pw - 40, mx, my, arriba, abajo);
            }
            y += FILA_ALTO + FILA_HUECO;
        }
        g.disableScissor();
        if (lista.isEmpty()) {
            g.centeredText(font, Component.literal("Ningún cambio con «" + filtro.strip() + "»"), width / 2, arriba + 20, APAGADO);
        }
        // La barra de desplazamiento, si no cabe todo.
        if (contenido > abajo - arriba) {
            int alto = abajo - arriba;
            int barra = Math.max(16, alto * alto / contenido);
            int by = arriba + Math.round((alto - barra) * desplazado / (contenido - alto));
            g.fill(px + pw - 16, arriba, px + pw - 14, abajo, 0x60000000);
            g.fill(px + pw - 16, by, px + pw - 14, by + barra, 0xFFD49A28);
        }
        g.centeredText(font, Component.literal("ON: sale la Ruleta y se aplica con su aviso  ·  OFF: se quita al momento"),
                width / 2, py + ph - 17, APAGADO);
    }

    private void fila(GuiGraphicsExtractor g, Cambio c, int x, int y, int w, int mx, int my, int arriba, int abajo) {
        boolean encima = mx >= x && mx < x + w && my >= y && my < y + FILA_ALTO && my >= arriba && my < abajo;
        g.blitSprite(RenderPipelines.GUI_TEXTURED, encima ? FILA_ENCIMA : FILA, x, y, w, FILA_ALTO);
        g.blitSprite(RenderPipelines.GUI_TEXTURED, sprite("cambio/" + c.id), x + 8, y + 12, 16, 16);
        AtalayaRed.EstadoCambio e = estados.get(c.id);
        int estado = e == null ? AtalayaRed.EstadoCambio.APAGADO : e.estado();
        int textoW = w - 30 - 50;
        g.text(font, Component.literal(c.titulo).withStyle(ChatFormatting.BOLD), x + 30, y + 7, AMARILLO);
        List<FormattedCharSequence> lineas = font.split(Component.literal(c.texto), textoW);
        for (int i = 0; i < Math.min(2, lineas.size()); i++) {
            g.text(font, lineas.get(i), x + 30, y + 19 + i * 9, TEXTO);
        }
        Identifier inter = estado == AtalayaRed.EstadoCambio.ENCENDIDO ? ON
                : estado == AtalayaRed.EstadoCambio.ESPERA ? ESPERA : OFF;
        int sx = x + w - 8 - 34;
        int sy = y + 10;
        g.blitSprite(RenderPipelines.GUI_TEXTURED, inter, sx, sy, 34, 16);
        // Lo que le queda a uno que dura; y el que espera, lo dice.
        if (estado == AtalayaRed.EstadoCambio.ENCENDIDO && e.quedan() > 0) {
            Minecraft mc = Minecraft.getInstance();
            long pasado = mc.level != null ? mc.level.getGameTime() - recibido : 0;
            int s = (int) Math.max(0, (e.quedan() - pasado) / 20);
            g.centeredText(font, Component.literal(String.format("%d:%02d", s / 60, s % 60)), sx + 17, sy + 18, 0xFFB8F0C0);
        } else if (estado == AtalayaRed.EstadoCambio.ESPERA) {
            g.centeredText(font, Component.literal("girando"), sx + 17, sy + 18, 0xFFE8C060);
        }
    }

    private int listaArriba() {
        return py + 58;
    }

    private int listaAbajo() {
        return py + ph - 24;
    }

    /** Los cambios que pasan el filtro del buscador (sin mayusculas ni tildes). */
    private List<Cambio> visibles() {
        String f = normal(filtro);
        List<Cambio> out = new ArrayList<>();
        for (Cambio c : Cambio.values()) {
            if (f.isEmpty() || normal(c.titulo).contains(f) || normal(c.texto).contains(f)) {
                out.add(c);
            }
        }
        return out;
    }

    private static String normal(String s) {
        return Normalizer.normalize(s.strip(), Normalizer.Form.NFD).replaceAll("\\p{M}", "").toLowerCase(Locale.ROOT);
    }

    // ------------------------------------------------------------------
    //  Lo que se pulsa
    // ------------------------------------------------------------------

    @Override
    public boolean mouseClicked(MouseButtonEvent evento, boolean doble) {
        if (super.mouseClicked(evento, doble)) {
            return true;
        }
        double mx = evento.x();
        double my = evento.y();
        int arriba = listaArriba();
        int abajo = listaAbajo();
        if (evento.button() != 0 || my < arriba || my >= abajo || mx < px + 20 || mx >= px + pw - 20) {
            return false;
        }
        int y = arriba - Math.round(desplazado);
        for (Cambio c : visibles()) {
            if (my >= y && my < y + FILA_ALTO) {
                pulsar(c);
                return true;
            }
            y += FILA_ALTO + FILA_HUECO;
        }
        return false;
    }

    private void pulsar(Cambio c) {
        AtalayaRed.EstadoCambio e = estados.get(c.id);
        int estado = e == null ? AtalayaRed.EstadoCambio.APAGADO : e.estado();
        if (estado == AtalayaRed.EstadoCambio.ESPERA) {
            return;
        }
        ClientPlayNetworking.send(new AtalayaRed.PulsaCambio(c.id));
        MenusCliente.sonar(estado == AtalayaRed.EstadoCambio.APAGADO);
        if (estado == AtalayaRed.EstadoCambio.APAGADO) {
            // Encendido: se cierra para ver la Ruleta.
            onClose();
        }
    }

    @Override
    public boolean mouseScrolled(double mx, double my, double dx, double dy) {
        if (my >= listaArriba() && my < listaAbajo()) {
            desplazado -= (float) dy * 22;
            return true;
        }
        return super.mouseScrolled(mx, my, dx, dy);
    }
}
