package com.atalaya.client;

import com.atalaya.Atalaya;
import com.atalaya.entity.NovilisEntity;
import com.atalaya.entity.RajangEntity;
import net.fabricmc.fabric.api.client.rendering.v1.hud.HudElement;
import net.minecraft.client.DeltaTracker;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphicsExtractor;
import net.minecraft.client.renderer.RenderPipelines;
import net.minecraft.resources.Identifier;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.Entity;
import org.jspecify.annotations.Nullable;

/**
 * La barra de jefe de Novilis, el Caballero Solar, propia (novilis_hud.py), del
 * tamano y el estilo de las de Nerea, Aeralis y Rajang: unas lenguas de fuego
 * salen del emblema y lamen el canto del marco de acero quemado (filo de oro,
 * grietas de lava que crecen con la fase y la punta de rayo); el emblema es el
 * yelmo del caballero ante su sol, con la corona de llamas de la fase; dentro
 * corre la lava del color de la fase (naranja, oro, oro palido, carmesi) con su
 * frente encendido, una chispa que salta y el rastro claro del ultimo golpe;
 * las muescas son rayos de sol de oro que se apagan y se rajan al pasarlos.
 * "NOVILIS" y la fase, en letras de pixel. Con la Furia, todo en fuego azul y
 * el rotulo FURIA; con el Grito de guerra, el cuerno carmesi junto al rotulo.
 * Liberado, oro en calma.
 *
 * Debajo, segun lo que este haciendo (como los totems del Sello de Rajang):
 *   Trompetas  los cuatro angeles (enteros, rajados o en cascotes) y la melodia
 *              que van tocando; al final espera la llama azul de la Furia.
 *   Fuentes    las tres fuentes solares, que se rajan golpe a golpe, y la carga
 *              del sol, del oro al rojo, hasta el estallido.
 *   Ofrenda    el sol con el cautivo dentro y lo que lleva de liberacion (lo que
 *              ven los demas; el cautivo ve ademas OfrendaHud).
 *
 * Va debajo de las de Nerea, Aeralis y Rajang si estan a la vista.
 */
public class NovilisBarraHud implements HudElement {

    private static final String[] CLAVES = {"1", "2", "3", "4", "furia", "libre"};
    private static final Identifier[] MARCOS = new Identifier[6];
    private static final Identifier[] RELLENOS = new Identifier[6];
    private static final Identifier[] NUCLEOS = new Identifier[6];
    /** La muesca entera lleva el fuego de cada clave en el nucleo. */
    private static final Identifier[] RAYOS = new Identifier[6];
    private static final Identifier RAYO_ROTO = tex("novilis_barra_rayo_roto");
    /** Las letras, en pixel (novilis_hud.py): nada de la fuente de Minecraft. */
    private static final Identifier NOMBRE = tex("novilis_barra_nombre");
    /** FASE I-IV, FURIA y LIBERADO, en el orden de CLAVES: en gris, para tenirlos. */
    private static final Identifier[] ROTULOS = {tex("novilis_barra_fase_1"), tex("novilis_barra_fase_2"),
            tex("novilis_barra_fase_3"), tex("novilis_barra_fase_4"), tex("novilis_barra_furia"), tex("novilis_barra_libre")};
    private static final Identifier CUERNO = tex("novilis_barra_cuerno");

    private static final Identifier FUENTE = tex("novilis_barra_fuente");
    private static final Identifier[] FUENTE_RAJADA = {tex("novilis_barra_fuente_rajada_1"),
            tex("novilis_barra_fuente_rajada_2"), tex("novilis_barra_fuente_rajada_3")};
    private static final Identifier FUENTE_ROTA = tex("novilis_barra_fuente_rota");
    private static final Identifier CARGA_LOSA = tex("novilis_barra_carga_losa");
    private static final Identifier CARGA = tex("novilis_barra_carga");
    private static final Identifier ESTALLIDO = tex("novilis_barra_estallido");

    private static final Identifier ESTATUA = tex("novilis_barra_estatua");
    private static final Identifier[] ESTATUA_RAJADA = {tex("novilis_barra_estatua_rajada_1"),
            tex("novilis_barra_estatua_rajada_2")};
    private static final Identifier ESTATUA_ROTA = tex("novilis_barra_estatua_rota");
    private static final Identifier MELODIA = tex("novilis_barra_melodia");
    private static final Identifier MELODIA_LUZ = tex("novilis_barra_melodia_luz");
    private static final Identifier LLAMA_AZUL = tex("novilis_barra_llama_azul");

    private static final Identifier OFRENDA_SOL = tex("novilis_barra_ofrenda_sol");
    private static final Identifier CAUTIVO = tex("novilis_barra_cautivo");
    private static final Identifier LIBERACION_LOSA = tex("novilis_barra_liberacion_losa");
    private static final Identifier LIBERACION = tex("novilis_barra_liberacion");

    static {
        for (int i = 0; i < CLAVES.length; i++) {
            MARCOS[i] = tex("novilis_barra_marco_" + CLAVES[i]);
            RELLENOS[i] = tex("novilis_barra_relleno_" + CLAVES[i]);
            NUCLEOS[i] = tex("novilis_barra_nucleo_" + CLAVES[i]);
            RAYOS[i] = tex("novilis_barra_rayo_" + CLAVES[i]);
        }
    }

    /** El color de cada rotulo, en el orden de CLAVES: el de la fase, el azul de la Furia y el oro del liberado. */
    private static final int[] COLOR_ROTULO = {0xFF8A1E, 0xFFC23A, 0xFFF0B0, 0xFF2A3A, 0x5AD8FF, 0xFFD77A};
    /** Los tres ultimos pasos de la rampa de cada clave: la chispa, el frente y su borde encendido. */
    private static final int[] FUEGO = {0xFF8A1E, 0xFFC23A, 0xFFF0B0, 0xFF2A3A, 0x5AD8FF, 0xF8DC8C};
    private static final int[] MEDIO = {0xFFC070, 0xFFE48A, 0xFFFADC, 0xFF9A84, 0xB4F2FF, 0xFFF2C8};
    private static final int[] CLARO = {0xFFF0D0, 0xFFFAE0, 0xFFFFF2, 0xFFE4D8, 0xF0FDFF, 0xFFFCF0};
    private static final int RASTRO = 0xD8FFF2D8;
    private static final int RASTRO_FURIA = 0xD8E4F8FF;
    private static final int FURIA = 4;
    private static final int LIBRE = 5;

    /** Las medidas de novilis_hud.py (las del marco, las mismas que las de las otras tres). */
    private static final int ANCHO = 240;
    private static final int MARCO_ALTO = 44;
    /**
     * Lo que ocupa con lo de debajo: 56 y no 44, porque las fuentes, los angeles
     * y el sol de la ofrenda bajan hasta ahi. Lo usaria una barra que fuera debajo.
     */
    public static final int ALTO = 56;
    private static final int HUECO_X = 40;
    private static final int HUECO_Y = 22;
    private static final int HUECO_ANCHO = 190;
    private static final int HUECO_ALTO = 9;
    private static final int EMBLEMA_X = 19;
    private static final int EMBLEMA_Y = 26;
    private static final int NUCLEO = 24;
    private static final int RAYO_ANCHO = 7;
    private static final int RAYO_ALTO = 9;
    private static final int NOMBRE_X = 92;
    private static final int NOMBRE_Y = 9;
    private static final int NOMBRE_ANCHO = 46;
    private static final int ROTULO_X = 167;
    private static final int ROTULO_Y = 8;
    private static final int ROTULO_ANCHO = 64;
    private static final int LETRAS_ALTO = 10;
    /** Lo que ocupa el texto de cada rotulo (va pegado a la derecha): el cuerno se pone justo a su izquierda. */
    private static final int[] TEXTO_ROTULO = {37, 42, 47, 44, 34, 55};
    private static final int CUERNO_ANCHO = 16;
    private static final int CUERNO_ALTO = 15;
    private static final int CUERNO_Y = 2;

    /** Las vistas de debajo, relativas al marco. */
    private static final int DEBAJO_Y = 36;
    private static final int FUENTE_X = 40;
    private static final int FUENTE_PASO = 13;
    private static final int FUENTE_ANCHO = 11;
    private static final int FUENTE_ALTO = 18;
    private static final int CARGA_X = 84;
    private static final int CARGA_Y = 42;
    private static final int CARGA_ANCHO = 134;
    private static final int CARGA_ALTO = 7;
    private static final int ESTALLIDO_X = 217;
    private static final int ESTALLIDO_Y = 39;
    private static final int ESTALLIDO_LADO = 13;
    private static final int ESTATUA_X = 38;
    private static final int ESTATUA_PASO = 15;
    private static final int ESTATUA_ANCHO = 14;
    private static final int ESTATUA_ALTO = 16;
    private static final int MELODIA_X = 102;
    private static final int MELODIA_Y = 38;
    private static final int MELODIA_ANCHO = 116;
    private static final int MELODIA_ALTO = 13;
    /** Las notas del pentagrama: la primera en x = 8 y una cada 6,5 (como en novilis_hud.py). */
    private static final int NOTAS = 16;
    private static final float PASO_NOTAS = 6.5F;
    private static final int LLAMA_X = 217;
    private static final int LLAMA_Y = 36;
    private static final int LLAMA_LADO = 13;
    private static final int SOL_X = 40;
    private static final int SOL_Y = 35;
    private static final int SOL_LADO = 21;
    private static final int CAUTIVO_X = 47;
    private static final int CAUTIVO_Y = 42;
    private static final int CAUTIVO_LADO = 6;
    private static final int LIBERA_X = 65;
    private static final int LIBERA_Y = 42;
    private static final int LIBERA_ANCHO = 163;
    private static final int LIBERA_ALTO = 7;
    private static final int LIBERA_FRENTE = 0xFFE6FFD4;
    private static final int CARGA_FRENTE = 0xFFFFF4E0;
    private static final int BLANCO = 0xFFFFFFFF;

    /** Si se ha dibujado este fotograma: una barra que fuera debajo la miraria. */
    public static boolean visible;

    private float fantasma = 1.0F;
    private int ultimo = -1;
    private int vistaAntes = -1;
    /** Los golpes de cada fuente o angel en el fotograma anterior, y cuando subieron: tiemblan al recibirlos. */
    private final int[] golpesAntes = new int[4];
    private final float[] golpeEn = new float[4];

    private static Identifier tex(String nombre) {
        return Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "textures/gui/" + nombre + ".png");
    }

    @Override
    public void extractRenderState(GuiGraphicsExtractor g, DeltaTracker delta) {
        Minecraft mc = Minecraft.getInstance();
        NovilisEntity n = cercano(mc);
        visible = n != null;
        if (n == null) {
            ultimo = -1;
            return;
        }
        float parcial = delta.getGameTimeDeltaPartialTick(false);
        float ahora = n.tickCount + parcial;
        boolean libre = n.isDeadOrDying();
        float vida = libre ? 0.0F : Mth.clamp(n.getHealth() / n.getMaxHealth(), 0.0F, 1.0F);
        boolean nuevo = n.getId() != ultimo;
        if (nuevo) {
            ultimo = n.getId();
            fantasma = vida;
        }
        // El rastro claro del dano se queda atras y alcanza a la vida poco a poco.
        fantasma = vida > fantasma ? vida : fantasma + (vida - fantasma) * 0.04F;

        int fase = Mth.clamp(n.fase(), 1, 4);
        boolean furia = n.tieneFuria() && !libre;
        int i = libre ? LIBRE : furia ? FURIA : fase - 1;
        int x0 = (g.guiWidth() - ANCHO) / 2;
        // Debajo de las otras tres, si estan a la vista.
        int y0 = 5 + (NereaBarraHud.visible ? NereaBarraHud.ALTO + 6 : 0)
                + (AeralisBarraHud.visible ? AeralisBarraHud.ALTO + 6 : 0)
                + (rajangALaVista(mc) ? RajangBarraHud.ALTO + 6 : 0);
        pieza(g, MARCOS[i], x0, y0, ANCHO, MARCO_ALTO, BLANCO);

        int hx = x0 + HUECO_X;
        int hy = y0 + HUECO_Y;
        int lleno = Math.round(HUECO_ANCHO * vida);
        int rastro = Math.round(HUECO_ANCHO * fantasma);
        if (rastro > lleno) {
            g.fill(hx + lleno, hy, hx + rastro, hy + HUECO_ALTO, furia ? RASTRO_FURIA : RASTRO);
        }
        int color = 0xFF000000 | COLOR_ROTULO[i];
        int tinte = BLANCO;
        if (furia) {
            // Con la Furia, el fuego azul y el rotulo laten deprisa.
            float k = 0.8F + 0.25F * Mth.sin(ahora * 0.45F);
            color = 0xFF000000 | escalar(COLOR_ROTULO[FURIA], k);
            tinte = 0xFF000000 | escalar(0xFFFFFF, 0.88F + 0.15F * Mth.sin(ahora * 0.45F));
        } else if (fase == 4 && !libre) {
            // En la ultima fase la lava late, carmesi.
            tinte = 0xFF000000 | escalar(0xFFFFFF, 0.85F + 0.15F * Mth.sin(ahora * 0.25F));
        }
        // La lava corre despacio hacia la derecha: el relleno es un mosaico que se desplaza.
        int desplaza = 64 - (int) (ahora * 0.7F) % 64;
        for (int x = 0; x < lleno; ) {
            int u = (x + desplaza) % 64;
            int w = Math.min(64 - u, lleno - x);
            g.blit(RenderPipelines.GUI_TEXTURED, RELLENOS[i], hx + x, hy, u, 0.0F, w, HUECO_ALTO, w, HUECO_ALTO, 64, HUECO_ALTO, tinte);
            x += w;
        }
        if (lleno >= 3) {
            frente(g, hx + lleno, hy, i, ahora);
        }
        // Las muescas: un rayo de sol de oro que se apaga y se raja al pasar la vida por el.
        for (float corte : new float[]{0.75F, 0.5F, 0.25F}) {
            int ex = hx + Math.round(HUECO_ANCHO * corte) - 3;
            pieza(g, vida < corte ? RAYO_ROTO : RAYOS[i], ex, hy - 5, RAYO_ANCHO, RAYO_ALTO, BLANCO);
        }
        int cx = x0 + EMBLEMA_X - NUCLEO / 2;
        int cy = y0 + EMBLEMA_Y - NUCLEO / 2;
        if (!libre && n.hurtTime > 0) {
            cx += (n.hurtTime % 2 == 0) ? 1 : -1;   // tiembla al recibir el golpe
        }
        pieza(g, NUCLEOS[i], cx, cy, NUCLEO, NUCLEO, BLANCO);

        pieza(g, NOMBRE, x0 + NOMBRE_X, y0 + NOMBRE_Y, NOMBRE_ANCHO, LETRAS_ALTO, BLANCO);
        pieza(g, ROTULOS[i], x0 + ROTULO_X, y0 + ROTULO_Y, ROTULO_ANCHO, LETRAS_ALTO, color);
        if (n.tieneGrito() && !libre) {
            // El cuerno del Grito de guerra, justo a la izquierda del rotulo: late como si sonara.
            float k = 0.82F + 0.18F * (0.5F + 0.5F * Mth.sin(ahora * 0.3F));
            int gx = x0 + ROTULO_X + ROTULO_ANCHO - (TEXTO_ROTULO[i] - 1) - CUERNO_ANCHO;
            pieza(g, CUERNO, gx, y0 + CUERNO_Y, CUERNO_ANCHO, CUERNO_ALTO, 0xFF000000 | escalar(0xFFFFFF, k));
        }

        if (libre) {
            return;
        }
        int e = n.getEstado();
        // Al cambiar de vista (o de jefe) los golpes se toman como estan, sin temblar.
        boolean sincronizar = nuevo || e != vistaAntes;
        vistaAntes = e;
        if (e == NovilisEntity.FUENTES) {
            fuentesBajo(g, n, x0, y0, ahora, sincronizar);
        } else if (e == NovilisEntity.TROMPETAS) {
            trompetasBajo(g, n, x0, y0, ahora, sincronizar);
        } else if (e == NovilisEntity.OFRENDA) {
            ofrendaBajo(g, n, x0, y0);
        }
    }

    /** El frente encendido de la lava y la chispa que salta por encima del canto (sube y se apaga). */
    private static void frente(GuiGraphicsExtractor g, int x, int hy, int i, float ahora) {
        int medio = 0xFF000000 | MEDIO[i];
        int claro = 0xFF000000 | CLARO[i];
        g.fill(x - 3, hy, x - 2, hy + 3, medio);
        g.fill(x - 2, hy, x - 1, hy + 5, claro);
        g.fill(x - 2, hy + 5, x - 1, hy + HUECO_ALTO, medio);
        g.fill(x - 1, hy, x, hy + HUECO_ALTO, claro);
        g.fill(x - 1, hy - 1, x, hy, medio);
        int salto = (int) (ahora / 3.0F) % 4;
        if (salto < 3) {
            int sx = x - 2 - salto / 2;
            int sy = hy - 2 - salto;
            g.fill(sx, sy, sx + 1, sy + 1, 0xFF000000 | FUEGO[i]);
        }
    }

    /** Las tres fuentes solares (rajandose golpe a golpe) y la carga del sol hasta el estallido. */
    private void fuentesBajo(GuiGraphicsExtractor g, NovilisEntity n, int x0, int y0, float ahora, boolean sincronizar) {
        int cuantas = Math.min(n.numFuentes(), 3);
        for (int k = 0; k < cuantas; k++) {
            int golpes = Mth.clamp(n.getGolpesFuente(k), 0, NovilisEntity.GOLPES);
            Identifier t = golpes >= NovilisEntity.GOLPES ? FUENTE_ROTA : golpes == 0 ? FUENTE
                    : FUENTE_RAJADA[Math.min(2, (golpes - 1) * 3 / Math.max(1, NovilisEntity.GOLPES - 1))];
            int dx = temblor(k, golpes, ahora, sincronizar);
            pieza(g, t, x0 + FUENTE_X + k * FUENTE_PASO + dx, y0 + DEBAJO_Y, FUENTE_ANCHO, FUENTE_ALTO, BLANCO);
        }
        // La carga: el relleno lleva pintado el paso del oro al rojo; se recorta por la izquierda.
        float carga = Mth.clamp(n.getCarga(), 0.0F, 1.0F);
        int lx = x0 + CARGA_X;
        int ly = y0 + CARGA_Y;
        pieza(g, CARGA_LOSA, lx, ly, CARGA_ANCHO, CARGA_ALTO, BLANCO);
        int w = Math.round((CARGA_ANCHO - 2) * carga);
        if (w > 0) {
            recorte(g, CARGA, lx + 1, ly + 1, w, CARGA_ALTO - 2, CARGA_ANCHO - 2, BLANCO);
        }
        if (w > 1) {
            g.fill(lx + w, ly + 1, lx + w + 1, ly + CARGA_ALTO - 1, CARGA_FRENTE);
        }
        // El estallido que viene: parpadea en el ultimo tramo, y mas deprisa al final.
        int tinte = BLANCO;
        if (carga > 0.8F && ((int) (ahora / (carga > 0.95F ? 2.0F : 4.0F))) % 2 == 0) {
            tinte = 0xFF000000 | escalar(0xFFFFFF, 0.65F);
        }
        pieza(g, ESTALLIDO, x0 + ESTALLIDO_X, y0 + ESTALLIDO_Y, ESTALLIDO_LADO, ESTALLIDO_LADO, tinte);
    }

    /** Los cuatro angeles (enteros, rajados o en cascotes) y la melodia que van tocando. */
    private void trompetasBajo(GuiGraphicsExtractor g, NovilisEntity n, int x0, int y0, float ahora, boolean sincronizar) {
        int cuantas = Math.min(n.numEstatuas(), 4);
        for (int k = 0; k < cuantas; k++) {
            int golpes = Mth.clamp(n.getGolpesEstatua(k), 0, NovilisEntity.GOLPES);
            Identifier t = golpes >= NovilisEntity.GOLPES ? ESTATUA_ROTA : golpes == 0 ? ESTATUA
                    : ESTATUA_RAJADA[Math.min(1, (golpes - 1) * 2 / Math.max(1, NovilisEntity.GOLPES - 1))];
            int dx = temblor(k, golpes, ahora, sincronizar);
            pieza(g, t, x0 + ESTATUA_X + k * ESTATUA_PASO + dx, y0 + DEBAJO_Y, ESTATUA_ANCHO, ESTATUA_ALTO, BLANCO);
        }
        // El pentagrama apagado y, encima, el encendido recortado hasta la ultima nota que ha sonado.
        float melodia = Mth.clamp(n.getMelodia(), 0.0F, 1.0F);
        int mx = x0 + MELODIA_X;
        int my = y0 + MELODIA_Y;
        pieza(g, MELODIA, mx, my, MELODIA_ANCHO, MELODIA_ALTO, BLANCO);
        int sonadas = Math.min(NOTAS, (int) (melodia * NOTAS + 1.0E-4F));
        if (sonadas > 0) {
            int w = sonadas >= NOTAS ? MELODIA_ANCHO : 8 + Math.round(sonadas * PASO_NOTAS) - 1;
            recorte(g, MELODIA_LUZ, mx, my, w, MELODIA_ALTO, MELODIA_ANCHO, BLANCO);
        }
        // La llama azul de la Furia, al final: en la ultima cuarta parte se aviva.
        int tinte = BLANCO;
        if (melodia > 0.75F) {
            tinte = 0xFF000000 | escalar(0xFFFFFF, 0.7F + 0.3F * Math.abs(Mth.sin(ahora * 0.6F)));
        }
        pieza(g, LLAMA_AZUL, x0 + LLAMA_X, y0 + LLAMA_Y, LLAMA_LADO, LLAMA_LADO, tinte);
    }

    /** El sol con el cautivo dentro y la liberacion que lleva (lo que ven los demas). */
    private static void ofrendaBajo(GuiGraphicsExtractor g, NovilisEntity n, int x0, int y0) {
        pieza(g, OFRENDA_SOL, x0 + SOL_X, y0 + SOL_Y, SOL_LADO, SOL_LADO, BLANCO);
        if (n.getIdOfrenda() >= 0) {
            pieza(g, CAUTIVO, x0 + CAUTIVO_X, y0 + CAUTIVO_Y, CAUTIVO_LADO, CAUTIVO_LADO, BLANCO);
        }
        float progreso = Mth.clamp(n.getProgresoOfrenda(), 0.0F, 1.0F);
        int lx = x0 + LIBERA_X;
        int ly = y0 + LIBERA_Y;
        pieza(g, LIBERACION_LOSA, lx, ly, LIBERA_ANCHO, LIBERA_ALTO, BLANCO);
        int w = Math.round((LIBERA_ANCHO - 2) * progreso);
        if (w > 0) {
            recorte(g, LIBERACION, lx + 1, ly + 1, w, LIBERA_ALTO - 2, LIBERA_ANCHO - 2, BLANCO);
            g.fill(lx + w, ly + 1, lx + w + 1, ly + LIBERA_ALTO - 1, LIBERA_FRENTE);
        }
    }

    /** Cuanto se mueve la fuente o el angel k: un pixel a cada lado durante 6 ticks tras cada golpe. */
    private int temblor(int k, int golpes, float ahora, boolean sincronizar) {
        if (sincronizar) {
            golpesAntes[k] = golpes;
            golpeEn[k] = -100.0F;
        } else if (golpes != golpesAntes[k]) {
            if (golpes > golpesAntes[k]) {
                golpeEn[k] = ahora;
            }
            golpesAntes[k] = golpes;
        }
        float t = ahora - golpeEn[k];
        return t >= 0.0F && t < 6.0F ? (((int) t) % 2 == 0 ? 1 : -1) : 0;
    }

    /** Una pieza entera, del tamano de su textura (cada texel en un pixel de interfaz). */
    private static void pieza(GuiGraphicsExtractor g, Identifier t, int x, int y, int w, int h, int tinte) {
        g.blit(RenderPipelines.GUI_TEXTURED, t, x, y, 0.0F, 0.0F, w, h, w, h, w, h, tinte);
    }

    /** Los primeros w pixeles de una textura de ancho texAncho (los rellenos que se llenan). */
    private static void recorte(GuiGraphicsExtractor g, Identifier t, int x, int y, int w, int h, int texAncho, int tinte) {
        g.blit(RenderPipelines.GUI_TEXTURED, t, x, y, 0.0F, 0.0F, w, h, w, h, texAncho, h, tinte);
    }

    private static int escalar(int rgb, float k) {
        int r = Math.min(255, (int) (((rgb >> 16) & 255) * k));
        int gr = Math.min(255, (int) (((rgb >> 8) & 255) * k));
        int b = Math.min(255, (int) ((rgb & 255) * k));
        return (r << 16) | (gr << 8) | b;
    }

    /**
     * Si la barra de Rajang esta a la vista. RajangBarraHud no lo publica (no
     * tiene su "visible"), asi que se hace aqui la misma cuenta que ella: un
     * Rajang despierto a menos de 120 bloques.
     */
    private static boolean rajangALaVista(Minecraft mc) {
        if (mc.level == null || mc.player == null) {
            return false;
        }
        for (Entity e : mc.level.entitiesForRendering()) {
            if (e instanceof RajangEntity r && r.getEstado() != RajangEntity.DORMIDO && !r.isRemoved()
                    && r.distanceToSqr(mc.player) < 120 * 120) {
                return true;
            }
        }
        return false;
    }

    /** El Novilis despierto mas cercano, a menos de 120 bloques. */
    private static @Nullable NovilisEntity cercano(Minecraft mc) {
        if (mc.level == null || mc.player == null) {
            return null;
        }
        NovilisEntity mejor = null;
        double d = 120 * 120;
        for (Entity e : mc.level.entitiesForRendering()) {
            if (e instanceof NovilisEntity n && n.getEstado() != NovilisEntity.DORMIDO && !n.isRemoved()) {
                double dd = n.distanceToSqr(mc.player);
                if (dd < d) {
                    d = dd;
                    mejor = n;
                }
            }
        }
        return mejor;
    }
}
