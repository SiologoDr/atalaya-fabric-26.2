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
 * La pantalla de la Ofrenda al Sol, la que ve el cautivo (novilis_hud.py).
 *
 * Arriba, OFRENDA AL SOL y SIGUE LAS TECLAS. Debajo, la fila de teclas: las
 * hechas pequenas y grises a la izquierda, con su marca verde; la de ahora
 * grande, de oro y encendida en el centro; las cuatro siguientes de acero a la
 * derecha, cada una mas apagada. Debajo, la LIBERACION (las hechas sobre el
 * total) y la losa del tiempo, que se vacia hacia la izquierda y es roja en su
 * ultimo cuarto.
 *
 * Al acabar se queda un segundo y medio y se apaga: si ha fallado, FALLASTE con
 * la tecla rajada y la liberacion que se pierde (deja atras un rastro rojo); si
 * ha acertado todas, LIBRE con la ultima tecla marcada y la liberacion llena.
 *
 * Todo son texturas al tamano en que se pintan (cada texel en un pixel de
 * interfaz) y posiciones enteras, asi que sale limpio a cualquier escala. Va
 * centrado, en la mitad de abajo, por encima de los corazones.
 *
 * El estado lo lleva OfrendaCliente; aqui solo se dibuja.
 */
public class OfrendaHud implements HudElement {

    private static final Identifier TECLA_ACTUAL = tex("novilis_qte_tecla_actual");
    private static final Identifier TECLA_SIGUIENTE = tex("novilis_qte_tecla_siguiente");
    private static final Identifier TECLA_HECHA = tex("novilis_qte_tecla_hecha");
    private static final Identifier TECLA_ROTA = tex("novilis_qte_tecla_rota");
    private static final Identifier GRIETAS = tex("novilis_qte_grietas");
    private static final Identifier HALO = tex("novilis_qte_halo");
    private static final Identifier MARCA = tex("novilis_qte_marca");
    /** Las 26 letras: grandes (fila 0 la de ahora, fila 1 la rota) y pequenas (fila 0 siguientes, fila 1 hechas). */
    private static final Identifier LETRAS_GRANDES = tex("novilis_qte_letras_grandes");
    private static final Identifier LETRAS_PEQUENAS = tex("novilis_qte_letras_pequenas");
    private static final Identifier TITULO = tex("novilis_qte_titulo");
    private static final Identifier SIGUE = tex("novilis_qte_sigue");
    private static final Identifier FALLASTE = tex("novilis_qte_fallaste");
    private static final Identifier LIBRE = tex("novilis_qte_libre");
    private static final Identifier ETIQUETA = tex("novilis_qte_etiqueta");
    private static final Identifier LIBERACION_LOSA = tex("novilis_qte_liberacion_losa");
    private static final Identifier LIBERACION = tex("novilis_qte_liberacion");
    private static final Identifier TIEMPO_LOSA = tex("novilis_qte_tiempo_losa");
    private static final Identifier TIEMPO = tex("novilis_qte_tiempo");
    private static final Identifier RELOJ = tex("novilis_qte_reloj");

    /** Las medidas de novilis_hud.py. */
    private static final int GRANDE = 28;
    private static final int SIGUIENTE = 18;
    private static final int HECHA = 14;
    /** La tecla va en (HALO_BORDE, HALO_BORDE) de su halo. */
    private static final int HALO_LADO = 42;
    private static final int HALO_BORDE = 7;
    /** Las grietas de la rota saltan fuera de la tecla: la tecla va en (4, 3) de su lienzo. */
    private static final int GRIETAS_ANCHO = 38;
    private static final int GRIETAS_ALTO = 31;
    private static final int GRIETAS_X = 4;
    private static final int GRIETAS_Y = 3;
    private static final int MARCA_ANCHO = 9;
    private static final int MARCA_ALTO = 7;
    /** Las celdas de las letras y donde cae la celda dentro de cada tecla (centrada en su cara). */
    private static final int CELDA_GRANDE_ANCHO = 14;
    private static final int CELDA_GRANDE_ALTO = 15;
    private static final int CELDA_PEQUENA = 8;
    private static final int LETRAS = 26;
    private static final int LETRA_GRANDE_X = 7;
    private static final int LETRA_GRANDE_Y = 5;
    private static final int LETRA_SIGUIENTE_X = 5;
    private static final int LETRA_SIGUIENTE_Y = 4;
    private static final int LETRA_HECHA_X = 3;
    private static final int LETRA_HECHA_Y = 2;
    private static final int TITULO_ANCHO = 91;
    private static final int SIGUE_ANCHO = 63;
    private static final int SIGUE_ALTO = 8;
    private static final int FALLASTE_ANCHO = 63;
    private static final int LIBRE_ANCHO = 40;
    private static final int LETRAS_ALTO = 10;
    private static final int ETIQUETA_ANCHO = 41;
    private static final int ETIQUETA_ALTO = 8;
    private static final int LOSA_ANCHO = 160;
    private static final int LIBERACION_ALTO = 7;
    private static final int TIEMPO_ALTO = 5;
    private static final int RELOJ_ANCHO = 5;
    private static final int RELOJ_ALTO = 7;

    /** Cuantas teclas hechas y siguientes se ven, y lo apagadas que van segun se alejan. */
    private static final float[] APAGAR_SIGUIENTES = {0.0F, 0.22F, 0.4F, 0.55F};
    private static final float[] APAGAR_HECHAS = {0.0F, 0.0F, 0.3F, 0.5F};

    /** Lo que dura en pantalla el final (1,5 s) y lo que tarda en apagarse al acabar. */
    private static final int FIN_TICKS = 30;
    private static final float FUNDIDO = 6.0F;
    /** Lo que tarda en vaciarse la liberacion al fallar. */
    private static final float PERDIDA = 12.0F;

    private static final int ROJO_RASTRO = 0xD8FF2A3A;
    private static final int VERDE_FRENTE = 0xE6FFD4;

    private int indiceAntes = -1;
    private float aciertoEn = -100.0F;

    private static Identifier tex(String nombre) {
        return Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "textures/gui/" + nombre + ".png");
    }

    @Override
    public void extractRenderState(GuiGraphicsExtractor g, DeltaTracker delta) {
        Minecraft mc = Minecraft.getInstance();
        if (mc.player == null) {
            return;
        }
        float parcial = delta.getGameTimeDeltaPartialTick(false);
        boolean fallo = OfrendaCliente.fallo();
        boolean exito = !fallo && OfrendaCliente.exito();
        boolean fin = fallo || exito;
        float desdeFin = fin ? OfrendaCliente.ticksDesdeFin(parcial) : 0.0F;
        if (fin ? desdeFin > FIN_TICKS : !OfrendaCliente.activo()) {
            indiceAntes = -1;
            return;
        }
        char[] teclas = OfrendaCliente.teclas();
        if (teclas == null || teclas.length == 0) {
            return;
        }
        float ahora = mc.player.tickCount + parcial;
        int total = teclas.length;
        int indice = Mth.clamp(OfrendaCliente.indice(), 0, total);
        if (indice != indiceAntes) {
            if (indiceAntes >= 0 && indice > indiceAntes) {
                aciertoEn = ahora;   // el halo da un fogonazo con cada acierto
            }
            indiceAntes = indice;
        }

        // Al final se apaga en sus ultimos ticks: el alfa va en el tinte de todo.
        float k = fin ? Mth.clamp((FIN_TICKS - desdeFin) / FUNDIDO, 0.0F, 1.0F) : 1.0F;
        int a = Math.round(255 * k);
        if (a <= 0) {
            return;
        }
        int blanco = (a << 24) | 0xFFFFFF;

        // Centrado, en la mitad de abajo; nunca tan abajo que pise los corazones.
        int cx = g.guiWidth() / 2;
        int yc = Math.min(g.guiHeight() / 2 + 28, g.guiHeight() - 86);

        pieza(g, TITULO, cx - TITULO_ANCHO / 2, yc - 42, TITULO_ANCHO, LETRAS_ALTO, blanco);
        if (fallo) {
            pieza(g, FALLASTE, cx - FALLASTE_ANCHO / 2, yc - 29, FALLASTE_ANCHO, LETRAS_ALTO, blanco);
        } else if (exito) {
            pieza(g, LIBRE, cx - LIBRE_ANCHO / 2, yc - 29, LIBRE_ANCHO, LETRAS_ALTO, blanco);
        } else {
            pieza(g, SIGUE, cx - SIGUE_ANCHO / 2, yc - 28, SIGUE_ANCHO, SIGUE_ALTO, blanco);
        }

        // La de ahora (al acertarlas todas, la ultima, marcada).
        int actual = Math.min(indice, total - 1);
        int xa = cx - GRANDE / 2;
        int ya = yc - GRANDE / 2;
        if (fallo && desdeFin < 8.0F) {
            xa += ((int) desdeFin % 2 == 0) ? 1 : -1;   // la tecla fallada tiembla
        }
        if (!fallo) {
            float brillo = exito || ahora - aciertoEn < 4.0F ? 1.0F
                    : 0.7F + 0.3F * (0.5F + 0.5F * Mth.sin(ahora * 0.25F));
            pieza(g, HALO, xa - HALO_BORDE, ya - HALO_BORDE, HALO_LADO, HALO_LADO,
                    (Math.round(a * brillo) << 24) | 0xFFFFFF);
        }
        pieza(g, fallo ? TECLA_ROTA : TECLA_ACTUAL, xa, ya, GRANDE, GRANDE, blanco);
        letraGrande(g, teclas[actual], fallo ? 1 : 0, xa + LETRA_GRANDE_X, ya + LETRA_GRANDE_Y, blanco);
        if (fallo) {
            pieza(g, GRIETAS, xa - GRIETAS_X, ya - GRIETAS_Y, GRIETAS_ANCHO, GRIETAS_ALTO, blanco);
        }
        if (exito) {
            pieza(g, MARCA, xa + GRANDE - MARCA_ANCHO + 2, ya + GRANDE - MARCA_ALTO - 1, MARCA_ANCHO, MARCA_ALTO, blanco);
        }

        // Las cuatro siguientes, a la derecha, cada una mas apagada.
        int x = cx + GRANDE / 2 + 9;
        for (int j = 0; j < APAGAR_SIGUIENTES.length && !exito; j++) {
            int i = actual + 1 + j;
            if (i >= total) {
                break;
            }
            int tinte = apagado(APAGAR_SIGUIENTES[j], a);
            int y = yc - 7;
            pieza(g, TECLA_SIGUIENTE, x, y, SIGUIENTE, SIGUIENTE, tinte);
            letraPequena(g, teclas[i], 0, x + LETRA_SIGUIENTE_X, y + LETRA_SIGUIENTE_Y, tinte);
            x += SIGUIENTE + 4;
        }
        // Las ultimas hechas, a la izquierda, con su marca verde.
        x = cx - GRANDE / 2 - 9;
        for (int j = 0; j < APAGAR_HECHAS.length; j++) {
            int i = actual - 1 - j;
            if (i < 0) {
                break;
            }
            int tinte = apagado(APAGAR_HECHAS[j], a);
            int y = yc - 3;
            x -= HECHA;
            pieza(g, TECLA_HECHA, x, y, HECHA, HECHA, tinte);
            letraPequena(g, teclas[i], 1, x + LETRA_HECHA_X, y + LETRA_HECHA_Y, tinte);
            pieza(g, MARCA, x + HECHA - 7, y + HECHA - 8, MARCA_ANCHO, MARCA_ALTO, tinte);
            x -= 4;
        }

        // La liberacion: las hechas sobre el total.
        int bx = cx - LOSA_ANCHO / 2;
        int by = yc + 28;
        int ancho = LOSA_ANCHO - 2;
        pieza(g, ETIQUETA, bx - 1, by - 9, ETIQUETA_ANCHO, ETIQUETA_ALTO, blanco);
        pieza(g, LIBERACION_LOSA, bx, by, LOSA_ANCHO, LIBERACION_ALTO, blanco);
        float lib = exito ? 1.0F : indice / (float) total;
        int lleno = Math.round(ancho * lib);
        if (fallo) {
            // Se pierde: el verde se vacia y deja atras el rastro rojo de lo que llevaba.
            int queda = Math.round(ancho * lib * (1.0F - Mth.clamp(desdeFin / PERDIDA, 0.0F, 1.0F)));
            if (lleno > queda) {
                g.fill(bx + 1 + queda, by + 1, bx + 1 + lleno, by + LIBERACION_ALTO - 1, conAlfa(ROJO_RASTRO, k));
            }
            lleno = queda;
        }
        if (lleno > 0) {
            recorte(g, LIBERACION, bx + 1, by + 1, lleno, LIBERACION_ALTO - 2, ancho, blanco);
            g.fill(bx + lleno, by + 1, bx + lleno + 1, by + LIBERACION_ALTO - 1, (a << 24) | VERDE_FRENTE);
        }

        // El tiempo: se vacia hacia la izquierda; en el ultimo cuarto (el rojo) el reloj y la losa parpadean.
        int ty = by + 11;
        float t = Mth.clamp(OfrendaCliente.tiempoRestante(parcial), 0.0F, 1.0F);
        boolean parpadeo = !fin && t < 0.25F && ((int) (ahora / 3.0F)) % 2 == 0;
        pieza(g, RELOJ, bx - 8, ty - 1, RELOJ_ANCHO, RELOJ_ALTO, parpadeo ? (a << 24) | 0xFF8060 : blanco);
        pieza(g, TIEMPO_LOSA, bx, ty, LOSA_ANCHO, TIEMPO_ALTO, blanco);
        int w = Math.round(ancho * t);
        if (w > 0) {
            recorte(g, TIEMPO, bx + 1, ty + 1, w, TIEMPO_ALTO - 2, ancho, parpadeo ? apagado(0.3F, a) : blanco);
        }
    }

    /** La letra de la tecla grande (fila 0 la de ahora, 1 la rota). Solo A-Z. */
    private static void letraGrande(GuiGraphicsExtractor g, char letra, int fila, int x, int y, int tinte) {
        int i = Character.toUpperCase(letra) - 'A';
        if (i < 0 || i >= LETRAS) {
            return;
        }
        g.blit(RenderPipelines.GUI_TEXTURED, LETRAS_GRANDES, x, y, i * CELDA_GRANDE_ANCHO, fila * CELDA_GRANDE_ALTO,
                CELDA_GRANDE_ANCHO, CELDA_GRANDE_ALTO, CELDA_GRANDE_ANCHO, CELDA_GRANDE_ALTO,
                LETRAS * CELDA_GRANDE_ANCHO, 2 * CELDA_GRANDE_ALTO, tinte);
    }

    /** La letra de una tecla pequena (fila 0 las siguientes, 1 las hechas). Solo A-Z. */
    private static void letraPequena(GuiGraphicsExtractor g, char letra, int fila, int x, int y, int tinte) {
        int i = Character.toUpperCase(letra) - 'A';
        if (i < 0 || i >= LETRAS) {
            return;
        }
        g.blit(RenderPipelines.GUI_TEXTURED, LETRAS_PEQUENAS, x, y, i * CELDA_PEQUENA, fila * CELDA_PEQUENA,
                CELDA_PEQUENA, CELDA_PEQUENA, CELDA_PEQUENA, CELDA_PEQUENA,
                LETRAS * CELDA_PEQUENA, 2 * CELDA_PEQUENA, tinte);
    }

    /** Una pieza entera, del tamano de su textura. */
    private static void pieza(GuiGraphicsExtractor g, Identifier t, int x, int y, int w, int h, int tinte) {
        g.blit(RenderPipelines.GUI_TEXTURED, t, x, y, 0.0F, 0.0F, w, h, w, h, w, h, tinte);
    }

    /** Los primeros w pixeles de una textura de ancho texAncho (lo que se llena o se vacia). */
    private static void recorte(GuiGraphicsExtractor g, Identifier t, int x, int y, int w, int h, int texAncho, int tinte) {
        g.blit(RenderPipelines.GUI_TEXTURED, t, x, y, 0.0F, 0.0F, w, h, w, h, texAncho, h, tinte);
    }

    /** Un gris que oscurece lo que tine (0 lo deja igual), con el alfa del fundido. */
    private static int apagado(float cuanto, int a) {
        int v = Math.round(255 * (1.0F - cuanto));
        return (a << 24) | (v << 16) | (v << 8) | v;
    }

    private static int conAlfa(int argb, float k) {
        return (Math.round((argb >>> 24) * k) << 24) | (argb & 0xFFFFFF);
    }
}
