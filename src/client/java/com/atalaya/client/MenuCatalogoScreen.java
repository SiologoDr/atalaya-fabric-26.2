package com.atalaya.client;

import com.atalaya.Atalaya;
import com.atalaya.catalogo.Catalogo;
import com.atalaya.catalogo.Categoria;
import com.atalaya.catalogo.Entrada;
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
 * Los menus del catalogo (/atalaya menu cambios | mobs | momentos; Catalogo en el servidor). Juan: "un menu
 * personalizado bonito, no el de Minecraft ... deben verse ON u OFF ... que haya un buscador"; y luego, "categorizalo
 * bien": los cambios de dificultad, los mobs nuevos y los momentos, cada uno en su menu.
 *
 * Una pantalla propia con el aire de la Ruleta (menus_cambios.py y catalogo.py): el panel de laca con su marco de oro, las
 * tres pestanas arriba (para pasar de un menu a otro), el titulo en nuestra letra con el brillo que lo cruza, el
 * buscador y una fila por entrada con su icono, su titulo, su texto y el interruptor (ON, OFF, o dorado mientras espera a
 * que pare su Ruleta). Las filas van por grupos, con el nombre del grupo encima. Pulsar una fila apagada la lanza y cierra
 * el menu (para ver la Ruleta o el Momento); pulsar una encendida la apaga al momento. Lo que dura dice cuanto le queda.
 */
public class MenuCatalogoScreen extends Screen {

    private static final Identifier PANEL = sprite("panel");
    private static final Identifier FILA = sprite("fila");
    private static final Identifier FILA_ENCIMA = sprite("fila_encima");
    private static final Identifier BUSCADOR = sprite("buscador");
    private static final Identifier LUPA = sprite("lupa");
    private static final Identifier PESTANA = sprite("pestana");
    private static final Identifier PESTANA_ACTIVA = sprite("pestana_activa");
    private static final Identifier ON = sprite("interruptor_on");
    private static final Identifier OFF = sprite("interruptor_off");
    private static final Identifier ESPERA = sprite("interruptor_espera");
    /** Los titulos de los menus (catalogo.py los hace y dice lo que miden). */
    private static final int[][] TITULOS = {{251, 18}, {139, 18}, {106, 18}};
    private static final int FILA_ALTO = 40;
    private static final int FILA_HUECO = 4;
    private static final int GRUPO_ALTO = 14;
    private static final int TEXTO = 0xFFD8CCE4;
    private static final int APAGADO = 0xFF9A90AA;
    private static final int GRUPO = 0xFFB8A6D0;
    private static final String[] PESTANAS = {"CAMBIOS", "MOBS", "MOMENTOS"};

    private final Categoria categoria;
    /** El estado de cada entrada (por su id) y el tiempo de juego en que llego. */
    private final Map<String, AtalayaRed.EstadoCambio> estados = new HashMap<>();
    private long recibido;
    private EditBox buscador;
    private String filtro = "";
    private float desplazado;
    private int px;
    private int py;
    private int pw;
    private int ph;

    /** Una linea de la lista: el nombre de un grupo o una entrada. */
    private record Linea(String grupo, Entrada entrada) {
        int alto() {
            return entrada == null ? GRUPO_ALTO : FILA_ALTO + FILA_HUECO;
        }
    }

    public MenuCatalogoScreen(Categoria categoria, List<AtalayaRed.EstadoCambio> estados) {
        super(Component.literal(switch (categoria) {
            case CAMBIO -> "Cambios de dificultad";
            case MOB -> "Nuevos mobs";
            case MOMENTO -> "Momentos";
        }));
        this.categoria = categoria;
        actualizar(estados);
    }

    public Categoria categoria() {
        return categoria;
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
        pw = Math.min(420, width - 24);
        ph = height - 20;
        px = (width - pw) / 2;
        py = 10;
        String antes = buscador != null ? buscador.getValue() : filtro;
        buscador = new EditBox(font, px + 36, py + 56, pw - 60, 10, Component.literal("Buscar"));
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
        pestanas(g, mx, my);
        int[] t = TITULOS[categoria.ordinal()];
        g.blitSprite(RenderPipelines.GUI_TEXTURED, sprite(categoria.titulo), px + (pw - t[0]) / 2, py + 30, t[0], t[1]);
        g.blitSprite(RenderPipelines.GUI_TEXTURED, BUSCADOR, px + 20, py + 52, pw - 40, 16);
        g.blitSprite(RenderPipelines.GUI_TEXTURED, LUPA, px + 24, py + 55, 10, 10);
        super.extractRenderState(g, mx, my, parcial);
        // La pista del buscador, tambien con el foco puesto (la de Minecraft solo sale sin el).
        if (buscador.getValue().isEmpty()) {
            g.text(font, Component.literal(categoria.pista), px + 38, py + 56, 0xFF7A6A8E, false);
        }

        List<Linea> lista = lineas();
        int arriba = listaArriba();
        int abajo = listaAbajo();
        int contenido = 0;
        for (Linea l : lista) {
            contenido += l.alto();
        }
        contenido -= FILA_HUECO;
        desplazado = Mth.clamp(desplazado, 0, Math.max(0, contenido - (abajo - arriba)));
        g.enableScissor(px + 14, arriba, px + pw - 14, abajo);
        int y = arriba - Math.round(desplazado);
        for (Linea l : lista) {
            if (y + l.alto() > arriba && y < abajo) {
                if (l.entrada() == null) {
                    grupo(g, l.grupo(), px + 22, y);
                } else {
                    fila(g, l.entrada(), px + 20, y, pw - 40, mx, my, arriba, abajo);
                }
            }
            y += l.alto();
        }
        g.disableScissor();
        if (lista.isEmpty()) {
            g.centeredText(font, Component.literal("Nada con «" + filtro.strip() + "»"), width / 2, arriba + 20, APAGADO);
        }
        // La barra de desplazamiento, si no cabe todo.
        if (contenido > abajo - arriba) {
            int alto = abajo - arriba;
            int barra = Math.max(16, alto * alto / contenido);
            int by = arriba + Math.round((alto - barra) * desplazado / (contenido - alto));
            g.fill(px + pw - 16, arriba, px + pw - 14, abajo, 0x60000000);
            g.fill(px + pw - 16, by, px + pw - 14, by + barra, 0xFFD49A28);
        }
        g.centeredText(font, Component.literal(switch (categoria) {
            case CAMBIO -> "ON: sale la Ruleta y se aplica con su aviso  ·  OFF: se quita al momento";
            case MOB -> "ON: sale la Ruleta y empieza a aparecer con su aviso  ·  OFF: deja de aparecer";
            case MOMENTO -> "ON: empieza el Momento Fractura  ·  OFF: se acaba al momento";
        }), width / 2, py + ph - 17, APAGADO);
    }

    /** Las tres pestanas de arriba: la del menu abierto, encendida. */
    private void pestanas(GuiGraphicsExtractor g, int mx, int my) {
        int ancho = 92;
        int x0 = px + (pw - ancho * 3 - 8) / 2;
        for (int i = 0; i < 3; i++) {
            int x = x0 + i * (ancho + 4);
            boolean esta = i == categoria.ordinal();
            boolean encima = mx >= x && mx < x + ancho && my >= py + 8 && my < py + 24;
            g.blitSprite(RenderPipelines.GUI_TEXTURED, esta ? PESTANA_ACTIVA : PESTANA, x, py + 8, ancho, 16);
            int color = esta ? Categoria.values()[i].color : encima ? 0xFFE8DCF4 : APAGADO;
            g.centeredText(font, Component.literal(PESTANAS[i]).withStyle(ChatFormatting.BOLD), x + ancho / 2, py + 12, color);
        }
    }

    private void grupo(GuiGraphicsExtractor g, String nombre, int x, int y) {
        g.text(font, Component.literal(nombre).withStyle(ChatFormatting.BOLD), x, y + 3, GRUPO, false);
        int w = font.width(Component.literal(nombre).withStyle(ChatFormatting.BOLD));
        g.fill(x + w + 6, y + 7, px + pw - 22, y + 8, 0x50D49A28);
    }

    private void fila(GuiGraphicsExtractor g, Entrada c, int x, int y, int w, int mx, int my, int arriba, int abajo) {
        boolean encima = mx >= x && mx < x + w && my >= y && my < y + FILA_ALTO && my >= arriba && my < abajo;
        g.blitSprite(RenderPipelines.GUI_TEXTURED, encima ? FILA_ENCIMA : FILA, x, y, w, FILA_ALTO);
        // Los mobs llevan su retrato de 32; los cambios y los momentos, su icono de 16.
        int tx;
        if (categoria == Categoria.MOB) {
            g.blitSprite(RenderPipelines.GUI_TEXTURED, sprite(c.icono()), x + 4, y + 4, 32, 32);
            tx = x + 42;
        } else {
            g.blitSprite(RenderPipelines.GUI_TEXTURED, sprite(c.icono()), x + 8, y + 12, 16, 16);
            tx = x + 30;
        }
        AtalayaRed.EstadoCambio e = estados.get(c.id());
        int estado = e == null ? AtalayaRed.EstadoCambio.APAGADO : e.estado();
        int textoW = x + w - 50 - tx;
        g.text(font, Component.literal(c.titulo()).withStyle(ChatFormatting.BOLD), tx, y + 7, categoria.color);
        List<FormattedCharSequence> lineas = font.split(Component.literal(c.texto()), textoW);
        for (int i = 0; i < Math.min(2, lineas.size()); i++) {
            g.text(font, lineas.get(i), tx, y + 19 + i * 9, TEXTO);
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
            g.centeredText(font, Component.literal(categoria == Categoria.MOMENTO ? "empieza" : "girando"), sx + 17,
                    sy + 18, 0xFFE8C060);
        }
    }

    private int listaArriba() {
        return py + 76;
    }

    private int listaAbajo() {
        return py + ph - 24;
    }

    /** Las lineas que pasan el filtro del buscador (sin mayusculas ni tildes), con el nombre de cada grupo encima. */
    private List<Linea> lineas() {
        String f = normal(filtro);
        List<Linea> out = new ArrayList<>();
        String grupo = null;
        for (Entrada c : Catalogo.entradas(categoria)) {
            if (!f.isEmpty() && !normal(c.titulo()).contains(f) && !normal(c.texto()).contains(f)
                    && !normal(c.etiquetas()).contains(f) && !normal(c.grupo()).contains(f)) {
                continue;
            }
            if (!c.grupo().isEmpty() && !c.grupo().equals(grupo)) {
                grupo = c.grupo();
                out.add(new Linea(grupo, null));
            }
            out.add(new Linea(null, c));
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
        if (evento.button() != 0) {
            return false;
        }
        // Las pestanas: piden al servidor el otro menu (que lo abre con su estado).
        int ancho = 92;
        int x0 = px + (pw - ancho * 3 - 8) / 2;
        if (my >= py + 8 && my < py + 24) {
            for (int i = 0; i < 3; i++) {
                int x = x0 + i * (ancho + 4);
                if (mx >= x && mx < x + ancho && i != categoria.ordinal()) {
                    ClientPlayNetworking.send(new AtalayaRed.PulsaCatalogo(i, ""));
                    MenusCliente.sonar(true);
                    return true;
                }
            }
        }
        int arriba = listaArriba();
        int abajo = listaAbajo();
        if (my < arriba || my >= abajo || mx < px + 20 || mx >= px + pw - 20) {
            return false;
        }
        int y = arriba - Math.round(desplazado);
        for (Linea l : lineas()) {
            if (l.entrada() != null && my >= y && my < y + FILA_ALTO) {
                pulsar(l.entrada());
                return true;
            }
            y += l.alto();
        }
        return false;
    }

    private void pulsar(Entrada c) {
        AtalayaRed.EstadoCambio e = estados.get(c.id());
        int estado = e == null ? AtalayaRed.EstadoCambio.APAGADO : e.estado();
        if (estado == AtalayaRed.EstadoCambio.ESPERA) {
            return;
        }
        ClientPlayNetworking.send(new AtalayaRed.PulsaCatalogo(categoria.ordinal(), c.id()));
        MenusCliente.sonar(estado == AtalayaRed.EstadoCambio.APAGADO);
        if (estado == AtalayaRed.EstadoCambio.APAGADO) {
            // Encendido: se cierra para ver la Ruleta (o el Momento).
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
