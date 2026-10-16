package com.atalaya.client;

import com.atalaya.Atalaya;
import net.fabricmc.fabric.api.client.rendering.v1.hud.HudElement;
import net.minecraft.client.DeltaTracker;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphicsExtractor;
import net.minecraft.client.renderer.RenderPipelines;
import net.minecraft.resources.Identifier;
import net.minecraft.util.Mth;
import org.joml.Matrix3x2f;

import java.util.ArrayList;
import java.util.List;
import java.util.Random;

/**
 * Lo que se ve en pantalla del Momento Maldicion (el calendario y el estado,
 * en MomentoMaldicionCliente; las grietas del cielo, en CieloRoto). Se pinta a
 * la resolucion de la pantalla, no a la del HUD: trazos finos que giran de
 * verdad, con su brillo, en vez de bloques.
 *
 * Desde el 16-10-2026 (revision en el juego: "las motas se ven en cajas, la
 * fractura en cuadrados rosas"), lo blando se pinta con piezas suaves
 * (momento_maldicion.py, en textures/gui/momento, con filtro lineal): el brillo
 * de los trazos y de las motas, los haces de luz, los discos, la vineta del
 * latido y un triangulo suave que, estirado, pinta los trozos de cristal de la
 * fractura. Asi nada sale en cajas ni con el borde en escalera.
 *
 * Cada fotograma se pinta en dos pasadas: primero todos los brillos (las piezas
 * blandas) y despues los trazos, los discos y las esquirlas, para que el juego
 * los junte en pocas tandas. Y se pinta lo justo (menos haces, tramos, motas,
 * chispas y esquirlas, y una sola capa de brillo por trazo): con la grafica del
 * procesador, la fractura bajaba a 24 FPS.
 *
 * <pre>
 *   EL SELLO   el latido en los bordes; el sello que se dibuja con una punta
 *              de luz (doble anillo con sus marcas, anillo de dentro, estrella
 *              de siete puntas, heptagono, siete circulos en las puntas, las
 *              runas que giran con el anillo); los rayos de luz y las motas que
 *              se traga en espiral; el titulo de fuego que entra letra a letra;
 *              las grietas; el silencio en blanco; y la fractura: la pantalla
 *              se raja como un cristal golpeado y se cae a trozos; el sello
 *              roto, la onda y las chispas
 *   MALDITO    nada mas (Juan: "solo la animacion"): manda el cielo;
 *              en la prueba, solo el contador, arriba en el centro
 *   FIN        la luz que entra (y el contador que se apaga)
 * </pre>
 */
public class MomentoMaldicionHud implements HudElement {

    private static final int NEGRO = 0xFF050003;
    private static final int ROJO = 0xFFF0362A;
    private static final int ROJO_HONDO = 0xFFA01018;
    private static final int CALIENTE = 0xFFFF8A5A;
    private static final int BLANCO = 0xFFFFF0E6;

    // Las piezas suaves (blancas: se tinen al pintarlas).
    private static final Identifier BRILLO = pieza("brillo");
    private static final Identifier DISCO = pieza("disco");
    private static final Identifier HAZ = pieza("haz");
    private static final Identifier TRAZO = pieza("trazo");
    private static final Identifier VINETA = pieza("vineta");
    /**
     * Un triangulo blanco (el de abajo a la izquierda de su cuadrado), de bordes suaves: estirado, pinta cualquier
     * triangulo, y con ellos los trozos de cristal de la fractura.
     */
    private static final Identifier TRIANGULO = pieza("triangulo");
    /**
     * Los numeros del contador (momento_maldicion.py, reloj): 0 a 9 en celdas de 28 y los dos puntos en una de 16,
     * blancos con su contorno oscuro (se tiñen de rojo al final). Sin blur: se pintan a pixeles enteros.
     */
    private static final Identifier RELOJ = pieza("reloj");
    private static final int RELOJ_W = 296;
    private static final int RELOJ_H = 32;
    private static final int CELDA = 28;
    private static final int CELDA_PUNTOS = 16;
    private static final int CELDA_ALTO = 32;
    /** La pasada: 0 todo, 1 solo los brillos, 2 solo lo demas. */
    private static int pasada;

    private static Identifier pieza(String nombre) {
        return Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "textures/gui/momento/" + nombre + ".png");
    }

    private static long semilla;
    private static int escW = -1;
    private static int escH = -1;
    private static float[][] motas = new float[0][];
    private static float[][] grietas = new float[0][];
    /**
     * El cristal de la pantalla en la fractura: los trozos (sus puntos, desde el centro) y sus datos (centro x, y,
     * cuando se sueltan, hacia donde salen x, y, como giran, lo oscuro de su cristal y si llevan reflejo). Sus filos
     * son las grietas.
     */
    private static float[][][] trozos = new float[0][][];
    private static float[][] trozoDatos = new float[0][];
    private static float lejosCristal = 1;

    public static void preparar(long nuevaSemilla, String nuevoTitulo) {
        semilla = nuevaSemilla;
        escW = -1;
    }

    @Override
    public void extractRenderState(GuiGraphicsExtractor g, DeltaTracker delta) {
        MomentoMaldicionCliente.Fase fase = MomentoMaldicionCliente.fase();
        if (fase == MomentoMaldicionCliente.Fase.NADA) {
            return;
        }
        float parcial = delta.getGameTimeDeltaPartialTick(false);
        int gs = Math.max(1, Minecraft.getInstance().getWindow().getGuiScale());
        int SW = g.guiWidth() * gs;
        int SH = g.guiHeight() * gs;
        float u = Math.max(1.0F, SH / 540.0F);
        if (SW != escW || SH != escH) {
            escena(SW, SH, u);
        }
        float t = MomentoMaldicionCliente.tiempo(parcial);
        // Todo a pixeles de pantalla.
        g.pose().pushMatrix();
        g.pose().scale(1.0F / gs, 1.0F / gs);
        switch (fase) {
            case INTRO -> intro(g, SW, SH, u, t);
            case MALDITO -> contador(g, SW, SH, parcial, 1.0F);
            case FIN -> {
                contador(g, SW, SH, parcial, 1.0F - Mth.clamp(t / 20.0F, 0.0F, 1.0F));
                if (t < 12) {
                    g.fill(0, 0, SW, SH, conAlfa(0xFFFFE8DC, 0.35F * (1.0F - t / 12.0F)));
                }
            }
            default -> {
            }
        }
        g.pose().popMatrix();
    }

    // ------------------------------------------------------------------
    //  El contador de la prueba
    // ------------------------------------------------------------------

    /**
     * El contador de la prueba, arriba en el centro (16-10-2026, Juan: "arriba en el centro vamos a poner un
     * contador"; y luego: "el numero debe ser mas pequeño y de color blanco"): M:SS en blanco, pequeño y a pixeles
     * enteros. Baja al acabar la cinematica y los dos puntos laten cada segundo; en los diez ultimos, cada segundo se
     * enciende en rojo y vuelve al blanco. A cero, el 0:00 rojo parpadea y se queda hasta que el momento se va. No
     * dice lo que lleva roto nadie (Juan: "si cumples no te va a avisar").
     */
    private static void contador(GuiGraphicsExtractor g, int SW, int SH, float parcial, float alfa) {
        int total = MomentoMaldicionCliente.contador();
        if (total <= 0 || alfa <= 0.0F) {
            return;
        }
        pasada = 0;
        float pasa = MomentoMaldicionCliente.malditoCielo(parcial);
        float resta = total - pasa;
        int s = resta > 0 ? Mth.ceil(resta / 20.0F) : 0;
        String txt = (s / 60) + ":" + (s % 60 < 10 ? "0" : "") + (s % 60);
        // Entra bajando, en medio segundo.
        float entra = Mth.clamp(pasa / 10.0F, 0.0F, 1.0F);
        alfa *= entra;
        // A cero, parpadea cuatro veces y se queda.
        float tras = -resta;
        if (tras >= 0 && tras < 64 && ((int) tras / 8) % 2 == 1) {
            alfa *= 0.15F;
        }
        // El rojo de cada segundo, en los diez ultimos (y rojo del todo a cero).
        float rojo = resta > 0 && resta <= 200 ? 0.35F + 0.65F * (float) Math.pow((resta % 20.0F) / 20.0F, 2) : resta <= 0 ? 1.0F : 0.0F;
        int tinte = mezcla(0xFFFFFFFF, 0xFFFF3A2A, rojo);
        boolean puntos = resta <= 0 || (resta % 20.0F) > 10.0F;
        int f = Math.max(1, SH / 720);
        int ancho = 0;
        for (int i = 0; i < txt.length(); i++) {
            ancho += txt.charAt(i) == ':' ? CELDA_PUNTOS : CELDA;
        }
        int x0 = Math.round(SW / 2.0F - ancho * f / 2.0F);
        int y0 = Math.max(2, Math.round(SH * 0.01F)) - Math.round((1.0F - suave(entra)) * CELDA_ALTO * f);
        float mx = SW / 2.0F;
        float my = y0 + CELDA_ALTO * f / 2.0F;
        // Una sombra blanda para que se lea encima de cualquier cosa.
        pintar(g, BRILLO, 128, 128, mx, my, ancho * f * 1.4F, CELDA_ALTO * f * 2.0F, 0.0F, conAlfa(0xFF000000, 0.4F * alfa));
        g.pose().pushMatrix();
        g.pose().translate(x0, y0);
        g.pose().scale(f, f);
        int x = 0;
        for (int i = 0; i < txt.length(); i++) {
            char c = txt.charAt(i);
            boolean dos = c == ':';
            int w = dos ? CELDA_PUNTOS : CELDA;
            int uu = dos ? 10 * CELDA : (c - '0') * CELDA;
            float a = dos && !puntos ? alfa * 0.35F : alfa;
            g.blit(RenderPipelines.GUI_TEXTURED, RELOJ, x, 0, uu, 0, w, CELDA_ALTO, w, CELDA_ALTO, RELOJ_W, RELOJ_H,
                    conAlfa(tinte, a));
            x += w;
        }
        g.pose().popMatrix();
    }

    // ------------------------------------------------------------------
    //  La cinematica
    // ------------------------------------------------------------------

    private static void intro(GuiGraphicsExtractor g, int SW, int SH, float u, float t) {
        float cx = SW / 2.0F;
        float cy = SH / 2.0F;
        float R = Math.min(SW, SH) * 0.27F;
        boolean silencio = t >= MomentoMaldicionCliente.T_SILENCIO && t < MomentoMaldicionCliente.T_FRACTURA;
        float late = MomentoMaldicionCliente.latidoIntro(t);
        if (t < MomentoMaldicionCliente.T_FRACTURA) {
            // El fondo se oscurece a medias: se sigue viendo el mundo y se puede jugar (16-10-2026, Juan: "que la
            // animacion salga pero que no les impida hacer lo que tienen que hacer"; antes llegaba al 90 %).
            float osc = t < 20 ? 0.5F * t / 20.0F : t < MomentoMaldicionCliente.T_TITULO ? 0.5F : silencio ? 0.72F : 0.58F;
            g.fill(0, 0, SW, SH, conAlfa(silencio ? 0xFF0E0406 : NEGRO, osc));
            // El sello late con el corazon, se inclina como si estuviera en el aire y, en el silencio, se acerca un poco.
            float escala = 1.0F + 0.03F * late + (silencio ? 0.05F * (t - MomentoMaldicionCliente.T_SILENCIO) / 6.0F : 0.0F);
            float inclina = inclinacion(t);
            for (int p = 1; p <= 2; p++) {
                pasada = p;
                if (!silencio) {
                    latidoBordes(g, SW, SH, u, late);
                    rayos(g, cx, cy, SW, SH, u, t, late);
                    motas(g, cx, cy, u, t);
                }
                g.pose().pushMatrix();
                g.pose().translate(cx, cy);
                g.pose().rotate(inclina * 0.35F);
                g.pose().scale(escala, escala * Mth.cos(inclina));
                sello(g, R, u, t, giro(t), silencio);
                g.pose().popMatrix();
                nucleo(g, cx, cy, R, u, t, late, escala, silencio);
                if (t >= MomentoMaldicionCliente.T_GRIETAS) {
                    grietas(g, cx, cy, u, t, silencio);
                }
            }
            pasada = 0;
        } else {
            fractura(g, SW, SH, cx, cy, R, u, t);
        }
    }

    /** Lo que ha girado el sello (radianes): quieto al principio, cada vez mas deprisa, parado en el silencio. */
    private static float giro(float t) {
        float a = 0.0F;
        float t1 = Math.min(t, MomentoMaldicionCliente.T_TITULO);
        if (t1 > MomentoMaldicionCliente.T_CIRCULO2) {
            a += (t1 - MomentoMaldicionCliente.T_CIRCULO2) * 0.35F;
        }
        float t2 = Math.min(t, MomentoMaldicionCliente.T_SILENCIO) - MomentoMaldicionCliente.T_TITULO;
        if (t2 > 0) {
            float d = MomentoMaldicionCliente.T_SILENCIO - MomentoMaldicionCliente.T_TITULO;
            a += 0.35F * t2 + 5.65F * t2 * t2 / (2.0F * d);
        }
        return a * Mth.DEG_TO_RAD;
    }

    /** El latido en los bordes: un marco rojo blando que se apaga hacia dentro. */
    private static void latidoBordes(GuiGraphicsExtractor g, int SW, int SH, float u, float k) {
        if (k <= 0.01F) {
            return;
        }
        // Una vineta suave (antes, diez marcos que se veian en escalones).
        pintar(g, VINETA, 256, 144, SW / 2.0F, SH / 2.0F, SW, SH, 0.0F, conAlfa(0xFF8A0A10, 0.6F * k));
    }

    /** Los rayos de luz que salen del sello, cada vez mas fuertes, y que laten. */
    private static void rayos(GuiGraphicsExtractor g, float cx, float cy, int SW, int SH, float u, float t, float late) {
        float k = Mth.clamp((t - MomentoMaldicionCliente.T_ESTRELLA) / 60.0F, 0.0F, 1.0F);
        if (k <= 0) {
            return;
        }
        float largo = (float) Math.hypot(SW, SH);
        for (int i = 0; i < 10; i++) {
            float a = i * Mth.TWO_PI / 10 + t * 0.004F + hash(i, 9) * 0.3F;
            float ancho = (18 + 40 * hash(i, 4)) * u;
            float alfa = k * (0.05F + 0.06F * late) * (0.6F + 0.4F * Mth.sin(t * 0.07F + i));
            // Un haz que nace suave en el sello y se apaga hacia fuera (antes, dos bandas planas).
            g.pose().pushMatrix();
            g.pose().translate(cx, cy);
            g.pose().rotate(a);
            pintar(g, HAZ, 128, 32, largo * 0.4F, 0.0F, largo * 0.8F, ancho * 1.3F, 0.0F, conAlfa(0xFFFF4A2A, alfa * 3.2F));
            g.pose().popMatrix();
        }
    }

    /** Las motas de luz que vienen de los bordes y caen al sello en espiral, con su estela. */
    private static void motas(GuiGraphicsExtractor g, float cx, float cy, float u, float t) {
        for (float[] m : motas) {
            float a = (t - m[2]) / m[3];
            if (a < 0 || a >= 1) {
                continue;
            }
            float[] p = posMota(m, a);
            float[] q = posMota(m, Math.max(0, a - 0.06F));
            int c = a > 0.75F ? CALIENTE : ROJO;
            // Un punto de luz con su estela fina (antes, una raya dentro de una caja de brillo).
            float r = (3.0F + 4.0F * m[4]) * u;
            float aparece = Mth.clamp(a * 6.0F, 0.0F, 1.0F);
            trazo(g, cx + q[0], cy + q[1], cx + p[0], cy + p[1], (0.8F + m[4]) * u, conAlfa(c, 0.7F * aparece), 0.0F);
            pintar(g, BRILLO, 128, 128, cx + p[0], cy + p[1], r * 3.0F, r * 3.0F, 0.0F, conAlfa(c, 0.6F * aparece));
            disco(g, cx + p[0], cy + p[1], r * 0.32F, conAlfa(a > 0.75F ? BLANCO : CALIENTE, aparece));
        }
    }

    private static float[] posMota(float[] m, float a) {
        float f = (1 - a) * (1 - a);
        float giro = a * m[5];
        float x = m[0] * f;
        float y = m[1] * f;
        float co = Mth.cos(giro);
        float si = Mth.sin(giro);
        return new float[]{x * co - y * si, x * si + y * co};
    }

    /** El sello, en coordenadas del sello (el centro en 0,0), girado. */
    private static void sello(GuiGraphicsExtractor g, float R, float u, float t, float giro, boolean silencio) {
        int color = silencio ? BLANCO : ROJO;
        int fino = silencio ? BLANCO : ROJO_HONDO;
        float grueso = 2.6F * u;
        // El doble anillo de fuera con sus marcas, en el sentido de las agujas.
        float c1 = progreso(t, MomentoMaldicionCliente.T_CIRCULO, MomentoMaldicionCliente.T_CIRCULO2);
        circulo(g, R, giro, c1, false, grueso, color, true);
        circulo(g, R * 1.07F, giro, c1, false, grueso * 0.55F, fino, false);
        marcas(g, R, R * 1.07F, giro, c1, grueso * 0.5F, fino);
        // El anillo de dentro, al reves.
        float c2 = progreso(t, MomentoMaldicionCliente.T_CIRCULO2, MomentoMaldicionCliente.T_ESTRELLA);
        circulo(g, R * 0.62F, -giro * 1.3F, c2, true, grueso * 0.8F, color, true);
        circulo(g, R * 0.56F, giro * 0.8F, c2, false, grueso * 0.35F, fino, false);
        // La estrella {7/3}, punta a punta, y el heptagono de dentro.
        float ce = (t - MomentoMaldicionCliente.T_ESTRELLA) / (MomentoMaldicionCliente.T_RUNAS - MomentoMaldicionCliente.T_ESTRELLA) * 7.0F;
        for (int k = 0; k < 7 && ce > 0; k++) {
            float parte = Mth.clamp(ce - k, 0.0F, 1.0F);
            if (parte <= 0) {
                break;
            }
            float[] a = vertice(R * 0.86F, giro * 0.6F, k);
            float[] b = vertice(R * 0.86F, giro * 0.6F, (k + 3) % 7);
            linea(g, a[0], a[1], b[0], b[1], parte, grueso * 0.8F, color, true);
        }
        float ch = progreso(t, MomentoMaldicionCliente.T_ESTRELLA + 12, MomentoMaldicionCliente.T_RUNAS);
        for (int k = 0; k < 7 && ch > 0; k++) {
            float[] a = vertice(R * 0.42F, -giro * 0.9F, k);
            float[] b = vertice(R * 0.42F, -giro * 0.9F, k + 1);
            linea(g, a[0], a[1], b[0], b[1], ch, grueso * 0.5F, fino, false);
        }
        // Siete circulos pequeños en las puntas de la estrella.
        float cc = progreso(t, MomentoMaldicionCliente.T_RUNAS - 4, MomentoMaldicionCliente.T_RUNAS + 8);
        if (cc > 0) {
            for (int k = 0; k < 7; k++) {
                float[] v = vertice(R * 0.86F, giro * 0.6F, k);
                g.pose().pushMatrix();
                g.pose().translate(v[0], v[1]);
                circulo(g, R * 0.07F * suave(cc), giro * 2, 1.0F, false, grueso * 0.5F, color, false);
                disco(g, 0, 0, R * 0.022F * suave(cc), silencio ? BLANCO : CALIENTE);
                g.pose().popMatrix();
            }
        }
        // El anillo de los sigilos y los dieciseis sigilos, que giran al reves, de cara al centro.
        float ca = progreso(t, MomentoMaldicionCliente.T_RUNAS, MomentoMaldicionCliente.T_RUNAS + 16);
        float giroSigilos = -giro * 0.5F;
        circulo(g, R * 1.34F, giroSigilos, ca, false, grueso * 0.6F, fino, true);
        float paso = (MomentoMaldicionCliente.T_RUNAS_FIN - MomentoMaldicionCliente.T_RUNAS) / (float) MomentoMaldicionCliente.RUNAS;
        for (int i = 0; i < MomentoMaldicionCliente.RUNAS; i++) {
            float sale = MomentoMaldicionCliente.T_RUNAS + i * paso;
            if (t < sale) {
                break;
            }
            float a = giroSigilos + i * Mth.TWO_PI / MomentoMaldicionCliente.RUNAS - Mth.HALF_PI;
            float k = Mth.clamp((t - sale) / 6.0F, 0.0F, 1.0F);
            g.pose().pushMatrix();
            g.pose().translate(Mth.cos(a) * R * 1.205F, Mth.sin(a) * R * 1.205F);
            g.pose().rotate(a + Mth.HALF_PI);
            float crece = 0.4F + 0.6F * suave(k) + 0.6F * (1 - k);
            g.pose().scale(crece, crece);
            int c = silencio ? BLANCO : conAlfa(k < 0.5F ? BLANCO : ROJO, k);
            sigilo(g, i * 5 + (int) (semilla & 7), R * 0.08F, grueso * 0.55F, c);
            g.pose().popMatrix();
        }
    }

    private static float progreso(float t, float desde, float hasta) {
        return Mth.clamp((t - desde) / (hasta - desde), 0.0F, 1.0F);
    }

    private static float[] vertice(float r, float giro, int k) {
        float a = giro + k * Mth.TWO_PI / 7 - Mth.HALF_PI;
        return new float[]{Mth.cos(a) * r, Mth.sin(a) * r};
    }

    private static void circulo(GuiGraphicsExtractor g, float cx, float cy, float r, float giro, float frac, boolean alReves,
                                float grosor, int color, boolean brilla) {
        g.pose().pushMatrix();
        g.pose().translate(cx, cy);
        circulo(g, r, giro, frac, alReves, grosor, color, brilla);
        g.pose().popMatrix();
    }

    /** Un circulo de trazos; frac lo dibujado (con la punta encendida si no esta entero). */
    private static void circulo(GuiGraphicsExtractor g, float r, float giro, float frac, boolean alReves, float grosor, int color,
                                boolean brilla) {
        if (frac <= 0 || r <= 0.5F) {
            return;
        }
        int n = Mth.clamp((int) (Mth.TWO_PI * r / 18), 24, 120);
        int hasta = Math.round(n * frac);
        float s = alReves ? -1 : 1;
        float px = 0;
        float py = 0;
        for (int k = 0; k < hasta; k++) {
            float a0 = giro - Mth.HALF_PI + s * k * Mth.TWO_PI / n;
            float a1 = giro - Mth.HALF_PI + s * (k + 1) * Mth.TWO_PI / n;
            float x0 = Mth.cos(a0) * r;
            float y0 = Mth.sin(a0) * r;
            px = Mth.cos(a1) * r;
            py = Mth.sin(a1) * r;
            trazo(g, x0, y0, px, py, grosor, color, brilla ? 1.0F : 0.4F);
        }
        if (frac < 1 && hasta > 0) {
            punta(g, px, py, grosor);
        }
    }

    /** Las marcas entre los dos anillos de fuera. */
    private static void marcas(GuiGraphicsExtractor g, float r0, float r1, float giro, float frac, float grosor, int color) {
        int n = 56;
        for (int k = 0; k < Math.round(n * frac); k++) {
            float a = giro - Mth.HALF_PI + k * Mth.TWO_PI / n;
            float largo = k % 7 == 0 ? 1.0F : 0.55F;
            float ra = r0 + (r1 - r0) * (1 - largo) * 0.5F;
            float rb = r1 - (r1 - r0) * (1 - largo) * 0.5F;
            trazo(g, Mth.cos(a) * ra, Mth.sin(a) * ra, Mth.cos(a) * rb, Mth.sin(a) * rb, grosor, color, 0.3F);
        }
    }

    /** Una linea de la que se ve una parte, con la punta encendida. */
    private static void linea(GuiGraphicsExtractor g, float x0, float y0, float x1, float y1, float frac, float grosor, int color,
                              boolean brilla) {
        float x = Mth.lerp(frac, x0, x1);
        float y = Mth.lerp(frac, y0, y1);
        trazo(g, x0, y0, x, y, grosor, color, brilla ? 1.0F : 0.4F);
        if (frac < 1) {
            punta(g, x, y, grosor);
        }
    }

    /** La punta que dibuja: un destello blanco con su cruz de luz. */
    private static void punta(GuiGraphicsExtractor g, float x, float y, float grosor) {
        float r = grosor * 7;
        trazo(g, x - r, y, x + r, y, grosor * 0.7F, BLANCO, 1.0F);
        trazo(g, x, y - r, x, y + r, grosor * 0.7F, BLANCO, 1.0F);
        int m = Math.round(grosor * 2.2F);
        if (pasada != 1) {
            g.fill(Math.round(x) - m, Math.round(y) - m, Math.round(x) + m, Math.round(y) + m, 0xFFFFFFFF);
        }
    }

    /**
     * Cuanto se inclina el sello (radianes): al encenderse las runas se echa
     * hacia atras como si estuviera en el aire, al llegar el nucleo se levanta
     * hasta mirar de frente y, al rajarse, tiembla.
     */
    private static float inclinacion(float t) {
        if (t < MomentoMaldicionCliente.T_RUNAS) {
            return 0.0F;
        }
        if (t < MomentoMaldicionCliente.T_TITULO) {
            return 0.55F * suave(progreso(t, MomentoMaldicionCliente.T_RUNAS, MomentoMaldicionCliente.T_TITULO));
        }
        float v = 0.55F * (1.0F - suave(progreso(t, MomentoMaldicionCliente.T_TITULO, MomentoMaldicionCliente.T_GRIETAS)));
        if (t >= MomentoMaldicionCliente.T_GRIETAS && t < MomentoMaldicionCliente.T_SILENCIO) {
            v += 0.05F * Mth.sin(t * 1.7F) * progreso(t, MomentoMaldicionCliente.T_GRIETAS, MomentoMaldicionCliente.T_SILENCIO);
        }
        return v;
    }

    /** Lo que hace la pose del sello a un punto suyo (escala, inclinacion y el giro de la inclinacion). */
    private static float[] aPantalla(float x, float y, float t, float escala) {
        float inclina = inclinacion(t);
        float sx = x * escala;
        float sy = y * escala * Mth.cos(inclina);
        float a = inclina * 0.35F;
        return new float[]{sx * Mth.cos(a) - sy * Mth.sin(a), sx * Mth.sin(a) + sy * Mth.cos(a)};
    }

    /**
     * El nucleo del sello: una esfera de luz en el centro que nace con los
     * sigilos, crece y late con el corazon, se calienta hasta el blanco y lanza
     * rayos que saltan a las puntas de la estrella.
     */
    private static void nucleo(GuiGraphicsExtractor g, float cx, float cy, float R, float u, float t, float late, float escala,
                               boolean silencio) {
        float k = progreso(t, MomentoMaldicionCliente.T_RUNAS, MomentoMaldicionCliente.T_TITULO);
        if (k <= 0) {
            return;
        }
        float carga = progreso(t, MomentoMaldicionCliente.T_TITULO, MomentoMaldicionCliente.T_SILENCIO);
        float r = R * (0.04F + 0.08F * suave(k) + 0.11F * carga) * (1.0F + 0.14F * late);
        int borde = silencio ? BLANCO : mezcla(ROJO_HONDO, ROJO, carga);
        int medio = silencio ? BLANCO : mezcla(ROJO, CALIENTE, carga);
        int centro = silencio ? 0xFFFFFFFF : mezcla(CALIENTE, 0xFFFFF4E8, 0.4F + 0.6F * carga);
        disco(g, cx, cy, r * 3.4F, conAlfa(medio, 0.05F + 0.07F * late + 0.05F * carga));
        disco(g, cx, cy, r * 2.1F, conAlfa(medio, 0.12F + 0.1F * late));
        disco(g, cx, cy, r, borde);
        disco(g, cx, cy, r * 0.74F, medio);
        disco(g, cx, cy, r * 0.42F, centro);
        // Un anillo que gira pegado a la esfera.
        circulo(g, cx, cy, r * 1.35F, t * 0.09F, 0.7F, false, 1.4F * u, conAlfa(medio, 0.8F), true);
        if (silencio || t < MomentoMaldicionCliente.T_TITULO + 6) {
            return;
        }
        // Los rayos que saltan a las puntas de la estrella (cambian cada dos ticks).
        int tic = (int) (t / 2);
        float giroEstrella = giro(t) * 0.6F;
        for (int i = 0; i < 7; i++) {
            if (hash(tic, i + 40) < 0.55F - 0.45F * carga) {
                continue;
            }
            float[] v = vertice(R * 0.86F, giroEstrella, i);
            float[] p = aPantalla(v[0], v[1], t, escala);
            relampago(g, cx, cy, cx + p[0], cy + p[1], tic * 7 + i, u, carga);
        }
    }

    /** Un rayo quebrado de (x0, y0) a (x1, y1), con una rama, blanco por dentro y rojo por fuera. */
    private static void relampago(GuiGraphicsExtractor g, float x0, float y0, float x1, float y1, int s, float u, float carga) {
        float dx = x1 - x0;
        float dy = y1 - y0;
        float largo = (float) Math.sqrt(dx * dx + dy * dy);
        float nx = -dy / Math.max(1, largo);
        float ny = dx / Math.max(1, largo);
        int tramos = 9;
        float px = x0;
        float py = y0;
        for (int i = 1; i <= tramos; i++) {
            float f = i / (float) tramos;
            float desvio = i == tramos ? 0 : (hash(s, i) - 0.5F) * largo * 0.16F;
            float qx = x0 + dx * f + nx * desvio;
            float qy = y0 + dy * f + ny * desvio;
            trazo(g, px, py, qx, qy, (1.6F + 1.2F * carga) * u, mezcla(ROJO, CALIENTE, carga), 1.0F);
            trazo(g, px, py, qx, qy, 0.8F * u, 0xFFFFF4EC, 0.0F);
            if (i == 4) {
                float bx = qx + (nx * (hash(s, 30) - 0.5F) * 0.6F + dx / largo * 0.4F) * largo * 0.3F;
                float by = qy + (ny * (hash(s, 31) - 0.5F) * 0.6F + dy / largo * 0.4F) * largo * 0.3F;
                trazo(g, qx, qy, bx, by, 1.1F * u, ROJO, 0.8F);
            }
            px = qx;
            py = qy;
        }
    }

    /** Un disco relleno, con el borde suave (antes, por franjas, y el borde salia en escalera). */
    private static void disco(GuiGraphicsExtractor g, float cx, float cy, float r, int color) {
        if (r < 0.5F || ((color >>> 24) & 255) == 0) {
            return;
        }
        pintar(g, DISCO, 256, 256, cx, cy, 2 * r, 2 * r, 0.0F, color);
    }

    /**
     * Una pieza suave de tw x th estirada a w x h, con el centro en (cx, cy),
     * girada ang y tenida de color (las piezas son blancas).
     */
    private static void pintar(GuiGraphicsExtractor g, Identifier id, int tw, int th, float cx, float cy, float w, float h,
                               float ang, int color) {
        pintar(g, id, tw, th, 0, 0, tw, th, cx, cy, w, h, ang, color);
    }

    /** Lo mismo con un trozo (u, v, tw x th) de una hoja de hw x hh. */
    private static void pintar(GuiGraphicsExtractor g, Identifier id, int hw, int hh, int u, int v, int tw, int th, float cx,
                               float cy, float w, float h, float ang, int color) {
        if (((color >>> 24) & 255) == 0 || w < 0.5F || h < 0.5F) {
            return;
        }
        boolean blanda = id == BRILLO || id == HAZ || id == TRAZO || id == VINETA;
        if (pasada == 1 && !blanda || pasada == 2 && blanda) {
            return;
        }
        g.pose().pushMatrix();
        g.pose().translate(cx, cy);
        if (ang != 0.0F) {
            g.pose().rotate(ang);
        }
        g.pose().scale(w / tw, h / th);
        g.blit(RenderPipelines.GUI_TEXTURED, id, -tw / 2, -th / 2, u, v, tw, th, tw, th, hw, hh, color);
        g.pose().popMatrix();
    }

    /**
     * Un sigilo (sin letras: Juan no quiere texto en la animacion): figuras
     * de trazos de un tamaño s, en coordenadas del sigilo.
     */
    private static void sigilo(GuiGraphicsExtractor g, int tipo, float s, float grosor, int color) {
        switch (tipo % 6) {
            case 0 -> {
                circulo(g, 0, 0, s * 0.5F, 0, 1.0F, false, grosor, color, true);
                disco(g, 0, 0, s * 0.16F, color);
            }
            case 1 -> {
                float[][] p = {{0, -s * 0.55F}, {s * 0.5F, s * 0.4F}, {-s * 0.5F, s * 0.4F}};
                for (int i = 0; i < 3; i++) {
                    trazo(g, p[i][0], p[i][1], p[(i + 1) % 3][0], p[(i + 1) % 3][1], grosor, color, 1.0F);
                }
                trazo(g, 0, -s * 0.85F, 0, s * 0.7F, grosor * 0.7F, color, 0.5F);
            }
            case 2 -> {
                float[][] p = {{0, -s * 0.6F}, {s * 0.45F, 0}, {0, s * 0.6F}, {-s * 0.45F, 0}};
                for (int i = 0; i < 4; i++) {
                    trazo(g, p[i][0], p[i][1], p[(i + 1) % 4][0], p[(i + 1) % 4][1], grosor, color, 1.0F);
                }
                trazo(g, -s * 0.2F, 0, s * 0.2F, 0, grosor * 0.7F, color, 0.5F);
                trazo(g, 0, -s * 0.25F, 0, s * 0.25F, grosor * 0.7F, color, 0.5F);
            }
            case 3 -> {
                circulo(g, 0, 0, s * 0.5F, -1.2F, 0.62F, false, grosor, color, true);
                circulo(g, s * 0.16F, 0, s * 0.36F, -1.4F, 0.55F, false, grosor * 0.7F, color, false);
            }
            case 4 -> {
                trazo(g, -s * 0.5F, -s * 0.3F, s * 0.5F, -s * 0.3F, grosor, color, 1.0F);
                for (int i = -1; i <= 1; i++) {
                    disco(g, i * s * 0.3F, s * 0.15F, s * 0.11F, color);
                }
                trazo(g, 0, -s * 0.3F, 0, s * 0.6F, grosor * 0.7F, color, 0.5F);
            }
            default -> {
                circulo(g, 0, s * 0.15F, s * 0.45F, Mth.PI, 0.5F, false, grosor, color, true);
                trazo(g, -s * 0.55F, s * 0.15F, s * 0.55F, s * 0.15F, grosor, color, 1.0F);
                disco(g, 0, -s * 0.1F, s * 0.12F, color);
            }
        }
    }

    /** Las grietas del sello: salen del titulo y crecen hasta los bordes, al rojo blanco en la punta. */
    private static void grietas(GuiGraphicsExtractor g, float cx, float cy, float u, float t, boolean silencio) {
        for (float[] s : grietas) {
            if (t < s[4]) {
                continue;
            }
            float k = Mth.clamp((t - s[4]) / 2.0F, 0.0F, 1.0F);
            float x1 = Mth.lerp(k, s[0], s[2]);
            float y1 = Mth.lerp(k, s[1], s[3]);
            int c = silencio ? BLANCO : t - s[4] < 4 ? BLANCO : CALIENTE;
            trazo(g, cx + s[0], cy + s[1], cx + x1, cy + y1, s[5] * u, c, 1.0F);
        }
    }

    /**
     * La fractura, como un cristal de verdad (16-10-2026, Juan: "que no se rompa como una pared sino como un vidrio
     * que se rompe"): el golpe en el centro (un destello corto), las grietas que corren por toda la pantalla desde el
     * golpe (rayos curvos y arcos, como un cristal golpeado) y se abre el agujero; un momento despues los trozos se
     * sueltan, de dentro afuera: llevan el oscuro de la pantalla y el filo encendido, caen girando y se apagan, y
     * dejan ver el mundo maldito. Encima, las astillas finas que saltan.
     */
    private static void fractura(GuiGraphicsExtractor g, int SW, int SH, float cx, float cy, float R, float u, float t) {
        float d = t - MomentoMaldicionCliente.T_FRACTURA;
        pasada = 0;
        // El cristal: cada trozo, quieto hasta que se suelta y luego cayendo.
        float frente = 26 * u + d / 7.0F * lejosCristal * 1.1F;
        int filoQuieto = d < 4 ? BLANCO : mezcla(BLANCO, CALIENTE, Mth.clamp((d - 4) / 6.0F, 0, 1));
        for (int k = 0; k < trozos.length; k++) {
            float[] dt = trozoDatos[k];
            float tau = d - dt[2];
            float alfa = tau < 0 ? 1.0F : 1.0F - Mth.clamp((tau - 8) / 16.0F, 0.0F, 1.0F);
            if (alfa <= 0) {
                continue;
            }
            float[][] pts = trozos[k];
            float[] xs = new float[pts.length];
            float[] ys = new float[pts.length];
            float ox = 0, oy = 0, gira = 0, esc = 1;
            if (tau > 0) {
                ox = dt[3] * tau * u;
                oy = (dt[4] * tau + 0.42F * tau * tau) * u;
                gira = dt[5] * tau;
                esc = Math.max(0.55F, 1.0F - 0.014F * tau);
            }
            float cs = Mth.cos(gira), sn = Mth.sin(gira);
            for (int i = 0; i < pts.length; i++) {
                float px = (pts[i][0] - dt[0]) * esc;
                float py = (pts[i][1] - dt[1]) * esc;
                xs[i] = cx + dt[0] + ox + px * cs - py * sn;
                ys[i] = cy + dt[1] + oy + px * sn + py * cs;
            }
            // El cristal oscuro (y alguno con un reflejo que lo cruza).
            poligono(g, xs, ys, conAlfa(NEGRO, dt[6] * alfa));
            if (dt[7] > 0 && tau > -3) {
                int n = xs.length;
                trazo(g, (xs[0] + xs[1]) / 2, (ys[0] + ys[1]) / 2, (xs[n / 2] + xs[n / 2 + 1]) / 2, (ys[n / 2] + ys[n / 2 + 1]) / 2,
                        1.4F * u, conAlfa(0xFFFFE8DC, 0.22F * alfa), 0.0F);
            }
            // El filo: quieto, son las grietas que corren desde el golpe (cada una la pintan sus dos trozos: va a
            // media luz); suelto, va con el trozo y se enfria.
            for (int i = 0; i < xs.length; i++) {
                int i1 = (i + 1) % xs.length;
                float m = (float) Math.hypot((pts[i][0] + pts[i1][0]) / 2, (pts[i][1] + pts[i1][1]) / 2);
                if (tau <= 0) {
                    if (m > frente) {
                        continue;
                    }
                    float grosor = Math.max(1.0F, 2.6F - m / lejosCristal * 2.2F) * u;
                    trazo(g, xs[i], ys[i], xs[i1], ys[i1], grosor, conAlfa(filoQuieto, 0.62F), 0.7F);
                } else {
                    int filo = tau < 4 ? BLANCO : mezcla(CALIENTE, ROJO, Mth.clamp((tau - 4) / 10.0F, 0, 1));
                    trazo(g, xs[i], ys[i], xs[i1], ys[i1], 1.6F * u, conAlfa(filo, alfa), 0.5F);
                }
            }
        }
        // El destello del golpe: corto, blanco y luego caliente.
        if (d < 8) {
            int c = d < 2 ? 0xFFFFFFFF : mezcla(0xFFFFF0E2, CALIENTE, (d - 2) / 6.0F);
            float al = d < 2 ? 0.85F : 0.5F * (1.0F - (d - 2) / 6.0F);
            g.fill(0, 0, SW, SH, conAlfa(c, al));
        }
        for (int p = 1; p <= 2; p++) {
            pasada = p;
            fracturaTrazos(g, cx, cy, R, u, d);
        }
        pasada = 0;
        // El primer instante, blanco del todo por encima de todo: ciega.
        if (d < 1.5F) {
            g.fill(0, 0, SW, SH, conAlfa(0xFFFFFFFF, 1.0F - d / 1.5F));
        }
    }

    /** Un poligono lleno (en abanico desde su centro), con triangulos estirados. */
    private static void poligono(GuiGraphicsExtractor g, float[] xs, float[] ys, int color) {
        if (((color >>> 24) & 255) == 0) {
            return;
        }
        float mx = 0, my = 0;
        for (int i = 0; i < xs.length; i++) {
            mx += xs[i] / xs.length;
            my += ys[i] / ys.length;
        }
        for (int i = 0; i < xs.length; i++) {
            int i1 = (i + 1) % xs.length;
            triangulo(g, mx, my, xs[i], ys[i], xs[i1], ys[i1], color);
        }
    }

    /** Un triangulo lleno de a, b, c: el triangulo de la hoja, estirado (su esquina va a 'a'). */
    private static void triangulo(GuiGraphicsExtractor g, float ax, float ay, float bx, float by, float cx, float cy, int color) {
        g.pose().pushMatrix();
        g.pose().mul(new Matrix3x2f(bx - ax, by - ay, cx - ax, cy - ay, ax, ay));
        g.blit(RenderPipelines.GUI_TEXTURED, TRIANGULO, 0, 0, 0, 0, 1, 1, 64, 64, 64, 64, color);
        g.pose().popMatrix();
    }

    /**
     * Lo que vuela en la fractura (en dos pasadas): solo las astillas finas que saltan del golpe (antes, tambien el
     * sello roto, un disco de luz y una onda, que tapaban el cristal).
     */
    private static void fracturaTrazos(GuiGraphicsExtractor g, float cx, float cy, float R, float u, float d) {
        // Las chispas.
        if (d < 30) {
            for (int i = 0; i < 60; i++) {
                float a = hash(i, 1) * Mth.TWO_PI;
                float v = (8 + 26 * hash(i, 2)) * u;
                float x = cx + Mth.cos(a) * v * d;
                float y = cy + Mth.sin(a) * v * d + 0.9F * d * d * u;
                float x0 = cx + Mth.cos(a) * v * (d - 1.2F);
                float y0 = cy + Mth.sin(a) * v * (d - 1.2F) + 0.9F * (d - 1.2F) * (d - 1.2F) * u;
                trazo(g, x0, y0, x, y, 2.0F * u, conAlfa(hash(i, 3) > 0.5F ? CALIENTE : BLANCO, 1.0F - d / 30.0F), 0.6F);
            }
        }
    }

    // ------------------------------------------------------------------
    //  Lo que se prepara para cada pantalla
    // ------------------------------------------------------------------

    private static void escena(int SW, int SH, float u) {
        escW = SW;
        escH = SH;
        Random r = new Random(semilla);
        float mw = SW / 2.0F;
        float mh = SH / 2.0F;
        List<float[]> lm = new ArrayList<>();
        for (int i = 0; i < 110; i++) {
            float a = r.nextFloat() * Mth.TWO_PI;
            float sx = Mth.cos(a);
            float sy = Mth.sin(a);
            float esc = Math.min(mw / Math.max(0.01F, Math.abs(sx)), mh / Math.max(0.01F, Math.abs(sy))) * (1.0F + r.nextFloat() * 0.2F);
            lm.add(new float[]{sx * esc, sy * esc, 20 + r.nextFloat() * 142, 18 + r.nextFloat() * 18, r.nextFloat(),
                    (r.nextBoolean() ? 1 : -1) * (0.8F + r.nextFloat() * 1.6F)});
        }
        motas = lm.toArray(new float[0][]);
        List<float[]> lg = new ArrayList<>();
        float durG = MomentoMaldicionCliente.T_SILENCIO - MomentoMaldicionCliente.T_GRIETAS - 2;
        float lejos = (float) Math.hypot(mw, mh);
        for (int i = 0; i < 11; i++) {
            float a = (i + r.nextFloat() * 0.6F) * Mth.TWO_PI / 11;
            float x = 0;
            float y = 0;
            float paso = (14 + r.nextFloat() * 14) * u;
            for (int k = 0; k < 80; k++) {
                a += (r.nextFloat() - 0.5F) * 0.6F;
                float nx = x + Mth.cos(a) * paso;
                float ny = y + Mth.sin(a) * paso;
                float nace = MomentoMaldicionCliente.T_GRIETAS + durG * (float) Math.hypot(x, y) / lejos;
                float grosor = Math.max(1.0F, 3.0F - k * 0.08F);
                lg.add(new float[]{x, y, nx, ny, nace, grosor});
                if (r.nextFloat() < 0.2F) {
                    float b = a + (r.nextBoolean() ? 1 : -1) * (0.6F + r.nextFloat() * 0.6F);
                    lg.add(new float[]{nx, ny, nx + Mth.cos(b) * paso * 1.6F, ny + Mth.sin(b) * paso * 1.6F, nace + 1, grosor * 0.6F});
                }
                x = nx;
                y = ny;
                if (Math.abs(x) > mw || Math.abs(y) > mh) {
                    break;
                }
            }
        }
        grietas = lg.toArray(new float[0][]);
        cristal(r, mw, mh, u);
    }

    /**
     * El cristal de la pantalla para la fractura, como un cristal golpeado de verdad: unos trece rayos de rumbo al
     * azar (curvos) que salen del agujero del golpe, y en cada hueco entre dos rayos unos anillos quebrados (el
     * primero siempre, los otros no siempre), que lo parten en trozos con forma de cuña; el ultimo, mas alla de las
     * esquinas. Los de dentro se sueltan antes.
     */
    private static void cristal(Random r, float mw, float mh, float u) {
        float lejos = (float) Math.hypot(mw, mh);
        lejosCristal = lejos;
        int n = 13;
        float[] ang = new float[n];
        int puestos = 0;
        for (int intento = 0; intento < 500 && puestos < n; intento++) {
            float a = r.nextFloat() * Mth.TWO_PI;
            boolean bien = true;
            for (int k = 0; k < puestos; k++) {
                float dif = Math.abs(Mth.wrapDegrees((float) Math.toDegrees(a - ang[k])));
                if (dif < 15) {
                    bien = false;
                }
            }
            if (bien) {
                ang[puestos++] = a;
            }
        }
        n = puestos;
        java.util.Arrays.sort(ang, 0, n);
        float[] curva = new float[n];
        for (int k = 0; k < n; k++) {
            curva[k] = (r.nextFloat() - 0.5F) * 0.5F;
        }
        // Los anillos de cada rayo: el agujero, tres anillos y el de mas alla de las esquinas.
        float[][] anillos = new float[5][n];
        for (int k = 0; k < n; k++) {
            anillos[0][k] = (22 + 10 * r.nextFloat()) * u;
            anillos[1][k] = (70 + 35 * r.nextFloat()) * u;
            anillos[2][k] = (170 + 70 * r.nextFloat()) * u;
            anillos[3][k] = (320 + 110 * r.nextFloat()) * u;
            anillos[4][k] = lejos * 1.3F;
        }
        boolean[][] hay = new boolean[5][n];
        for (int k = 0; k < n; k++) {
            hay[0][k] = true;
            hay[1][k] = true;
            hay[2][k] = r.nextFloat() < 0.75F;
            hay[3][k] = r.nextFloat() < 0.6F;
            hay[4][k] = true;
        }
        List<float[][]> lt = new ArrayList<>();
        List<float[]> ld = new ArrayList<>();
        for (int k = 0; k < n; k++) {
            int k1 = (k + 1) % n;
            float a0 = ang[k];
            float a1 = ang[k1] + (k1 == 0 ? Mth.TWO_PI : 0);
            int nivel = 0;
            for (int m = 1; m < 5; m++) {
                if (!hay[m][k]) {
                    continue;
                }
                // Un trozo: del anillo 'nivel' al 'm', entre el rayo k y el k1 (con un codo en cada lado).
                float ra0 = anillos[nivel][k], ra1 = anillos[nivel][k1];
                float rb0 = anillos[m][k], rb1 = anillos[m][k1];
                List<float[]> pol = new ArrayList<>();
                pol.add(punto(a0, curva[k], ra0, lejos));
                pol.add(punto(a0, curva[k], (ra0 + rb0) / 2, lejos));
                pol.add(punto(a0, curva[k], rb0, lejos));
                if (m < 4) {
                    float comba = 0.96F + 0.1F * r.nextFloat();
                    pol.add(punto((a0 + a1) / 2, 0, (rb0 + rb1) / 2 * comba, lejos));
                }
                pol.add(punto(a1, curva[k1], rb1, lejos));
                pol.add(punto(a1, curva[k1], (ra1 + rb1) / 2, lejos));
                pol.add(punto(a1, curva[k1], ra1, lejos));
                float bajo = nivel == 0 ? 0.88F + 0.08F * r.nextFloat() : 0.96F + 0.1F * r.nextFloat();
                pol.add(punto((a0 + a1) / 2, 0, (ra0 + ra1) / 2 * bajo, lejos));
                float[][] pts = pol.toArray(new float[0][]);
                float px = 0, py = 0;
                for (float[] q : pts) {
                    px += q[0] / pts.length;
                    py += q[1] / pts.length;
                }
                float dist = (float) Math.hypot(px, py);
                float sale = 0.6F + 1.6F * r.nextFloat();
                ld.add(new float[]{px, py, 4 + 10 * Math.min(1, dist / lejos) + 2 * r.nextFloat(),
                        px / Math.max(1, dist) * sale, py / Math.max(1, dist) * sale - 1.2F, (r.nextFloat() - 0.5F) * 0.16F,
                        0.52F + 0.1F * r.nextFloat(), r.nextFloat() < 0.35F ? 1 : 0});
                lt.add(pts);
                nivel = m;
            }
        }
        trozos = lt.toArray(new float[0][][]);
        trozoDatos = ld.toArray(new float[0][]);
    }

    /** Un punto del cristal: en el rumbo 'a' (torcido por 'curva' segun lo lejos que este) a 'radio' del golpe. */
    private static float[] punto(float a, float curva, float radio, float lejos) {
        float t = radio / lejos;
        float ang = a + curva * t * t;
        return new float[]{Mth.cos(ang) * radio, Mth.sin(ang) * radio};
    }

    // ------------------------------------------------------------------
    //  El trazo con brillo y pequeñas ayudas
    // ------------------------------------------------------------------

    /**
     * Un trazo de (x0, y0) a (x1, y1) de un grosor, con su brillo en dos capas
     * (ancha y tenue, media) si brillo > 0: un rectangulo girado, asi las
     * lineas son finas y lisas en cualquier direccion.
     */
    private static void trazo(GuiGraphicsExtractor g, float x0, float y0, float x1, float y1, float grosor, int color, float brillo) {
        float dx = x1 - x0;
        float dy = y1 - y0;
        float largo = (float) Math.sqrt(dx * dx + dy * dy);
        if (largo < 0.5F) {
            return;
        }
        float alfa = ((color >>> 24) & 255) / 255.0F;
        if (pasada == 1 && brillo <= 0) {
            return;
        }
        g.pose().pushMatrix();
        g.pose().translate(x0, y0);
        g.pose().rotate((float) Math.atan2(dy, dx));
        int L = Math.round(largo) + 1;
        if (brillo > 0 && pasada != 2) {
            // El brillo, una campana suave con las puntas redondas (antes, dos rectangulos que se veian como cajas).
            float a = grosor * 3.8F;
            pintar(g, TRAZO, 64, 16, L / 2.0F, 0.0F, L + a * 1.4F, a * 2.0F, 0.0F, conAlfa(color, 0.36F * brillo * alfa));
        }
        int h = Math.max(1, Math.round(grosor));
        if (pasada != 1) {
            g.fill(0, -h / 2, L, h - h / 2, color);
        }
        g.pose().popMatrix();
    }

    private static float hash(int a, int b) {
        long h = (a * 73856093L) ^ (b * 19349663L) ^ (semilla * 83492791L);
        h ^= (h >>> 13);
        h *= 0x5bd1e995L;
        h ^= (h >>> 15);
        return (h & 0xFFFF) / 65535.0F;
    }

    private static int conAlfa(int argb, float k) {
        int a = Math.round(((argb >>> 24) & 255) * Mth.clamp(k, 0.0F, 1.0F));
        return (a << 24) | (argb & 0xFFFFFF);
    }

    private static int mezcla(int a, int b, float k) {
        k = Mth.clamp(k, 0.0F, 1.0F);
        int r = (int) Mth.lerp(k, (a >> 16) & 255, (b >> 16) & 255);
        int gg = (int) Mth.lerp(k, (a >> 8) & 255, (b >> 8) & 255);
        int bl = (int) Mth.lerp(k, a & 255, b & 255);
        int al = (int) Mth.lerp(k, (a >>> 24) & 255, (b >>> 24) & 255);
        return (al << 24) | (r << 16) | (gg << 8) | bl;
    }

    private static float suave(float x) {
        return x * x * (3 - 2 * x);
    }
}
