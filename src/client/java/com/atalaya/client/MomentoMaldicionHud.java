package com.atalaya.client;

import net.fabricmc.fabric.api.client.rendering.v1.hud.HudElement;
import net.minecraft.client.DeltaTracker;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphicsExtractor;
import net.minecraft.util.Mth;

import java.util.ArrayList;
import java.util.List;
import java.util.Random;

/**
 * Lo que se ve en pantalla del Momento Maldicion (el calendario y el estado,
 * en MomentoMaldicionCliente; las grietas del cielo, en CieloRoto). Se pinta a
 * la resolucion de la pantalla, no a la del HUD: trazos finos que giran de
 * verdad, con su brillo en capas, en vez de bloques.
 *
 * <pre>
 *   EL SELLO   el latido en los bordes; el sello que se dibuja con una punta
 *              de luz (doble anillo con sus marcas, anillo de dentro, estrella
 *              de siete puntas, heptagono, siete circulos en las puntas, las
 *              runas que giran con el anillo); los rayos de luz y las motas que
 *              se traga en espiral; el titulo de fuego que entra letra a letra;
 *              las grietas; el silencio en blanco; y la fractura: la pantalla
 *              en esquirlas que giran, el sello roto en trozos, la onda y las
 *              chispas
 *   MALDITO    nada en el HUD (Juan: "solo la animacion"): manda el cielo
 *   FIN        la luz que entra
 * </pre>
 */
public class MomentoMaldicionHud implements HudElement {

    private static final int NEGRO = 0xFF050003;
    private static final int ROJO = 0xFFF0362A;
    private static final int ROJO_HONDO = 0xFFA01018;
    private static final int CALIENTE = 0xFFFF8A5A;
    private static final int BLANCO = 0xFFFFF0E6;

    private static long semilla;
    private static int escW = -1;
    private static int escH = -1;
    private static float[][] motas = new float[0][];
    private static float[][] grietas = new float[0][];
    private static float[][] esquirlas = new float[0][];

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
            case FIN -> {
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
    //  La cinematica
    // ------------------------------------------------------------------

    private static void intro(GuiGraphicsExtractor g, int SW, int SH, float u, float t) {
        float cx = SW / 2.0F;
        float cy = SH / 2.0F;
        float R = Math.min(SW, SH) * 0.27F;
        boolean silencio = t >= MomentoMaldicionCliente.T_SILENCIO && t < MomentoMaldicionCliente.T_FRACTURA;
        float late = MomentoMaldicionCliente.latidoIntro(t);
        if (t < MomentoMaldicionCliente.T_FRACTURA) {
            float osc = t < 20 ? 0.82F * t / 20.0F : t < MomentoMaldicionCliente.T_TITULO ? 0.82F : silencio ? 0.95F : 0.9F;
            g.fill(0, 0, SW, SH, conAlfa(silencio ? 0xFF0E0406 : NEGRO, osc));
            if (!silencio) {
                latidoBordes(g, SW, SH, u, late);
                rayos(g, cx, cy, SW, SH, u, t, late);
                motas(g, cx, cy, u, t);
            }
            // El sello late con el corazon, se inclina como si estuviera en el aire y, en el silencio, se acerca un poco.
            float escala = 1.0F + 0.03F * late + (silencio ? 0.05F * (t - MomentoMaldicionCliente.T_SILENCIO) / 6.0F : 0.0F);
            float inclina = inclinacion(t);
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
        int capas = 10;
        int e = Math.round(6 * u);
        for (int i = 0; i < capas; i++) {
            int c = conAlfa(0xFF8A0A10, 0.28F * k * (1.0F - i / (float) capas));
            int d = i * e;
            g.fill(d, d, SW - d, d + e, c);
            g.fill(d, SH - d - e, SW - d, SH - d, c);
            g.fill(d, d + e, d + e, SH - d - e, c);
            g.fill(SW - d - e, d + e, SW - d, SH - d - e, c);
        }
    }

    /** Los rayos de luz que salen del sello, cada vez mas fuertes, y que laten. */
    private static void rayos(GuiGraphicsExtractor g, float cx, float cy, int SW, int SH, float u, float t, float late) {
        float k = Mth.clamp((t - MomentoMaldicionCliente.T_ESTRELLA) / 60.0F, 0.0F, 1.0F);
        if (k <= 0) {
            return;
        }
        float largo = (float) Math.hypot(SW, SH);
        for (int i = 0; i < 14; i++) {
            float a = i * Mth.TWO_PI / 14 + t * 0.004F + hash(i, 9) * 0.3F;
            float ancho = (18 + 40 * hash(i, 4)) * u;
            float alfa = k * (0.05F + 0.06F * late) * (0.6F + 0.4F * Mth.sin(t * 0.07F + i));
            g.pose().pushMatrix();
            g.pose().translate(cx, cy);
            g.pose().rotate(a);
            g.fill(0, Math.round(-ancho / 2), Math.round(largo), Math.round(ancho / 2), conAlfa(0xFFFF3A20, alfa));
            g.fill(0, Math.round(-ancho / 6), Math.round(largo), Math.round(ancho / 6), conAlfa(0xFFFF8A60, alfa));
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
            trazo(g, cx + q[0], cy + q[1], cx + p[0], cy + p[1], (1.5F + m[4] * 2) * u, c, 0.8F);
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
        int n = Mth.clamp((int) (Mth.TWO_PI * r / 7), 24, 220);
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
        g.fill(Math.round(x) - m, Math.round(y) - m, Math.round(x) + m, Math.round(y) + m, 0xFFFFFFFF);
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

    /** Un disco relleno, por franjas. */
    private static void disco(GuiGraphicsExtractor g, float cx, float cy, float r, int color) {
        if (r < 0.5F || ((color >>> 24) & 255) == 0) {
            return;
        }
        int paso = Math.max(1, Math.round(r / 48));
        for (float y = -r; y < r; y += paso) {
            float m = (float) Math.sqrt(Math.max(0, r * r - (y + paso / 2.0F) * (y + paso / 2.0F)));
            g.fill(Math.round(cx - m), Math.round(cy + y), Math.round(cx + m), Math.round(cy + y + paso), color);
        }
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
     * La fractura: destello, la oscuridad en esquirlas que salen girando con
     * el filo encendido, el sello roto en trozos que giran, la onda y las
     * chispas.
     */
    private static void fractura(GuiGraphicsExtractor g, int SW, int SH, float cx, float cy, float R, float u, float t) {
        float d = t - MomentoMaldicionCliente.T_FRACTURA;
        if (d < 32) {
            float apaga = 1.0F - Mth.clamp((d - 14) / 18.0F, 0.0F, 1.0F);
            for (float[] e : esquirlas) {
                float x = cx + e[0] + e[4] * d * u;
                float y = cy + e[1] + (e[5] * d + 0.35F * d * d) * u;
                float giro = e[7] + e[6] * d;
                g.pose().pushMatrix();
                g.pose().translate(x, y);
                g.pose().rotate(giro);
                int w = Math.round(e[2] / 2);
                int h = Math.round(e[3] / 2);
                g.fill(-w, -h, w, h, conAlfa(NEGRO, 0.92F * apaga));
                int filo = Math.max(1, Math.round(2 * u));
                g.fill(-w, -h, w, -h + filo, conAlfa(d < 6 ? BLANCO : 0xFFFF4020, apaga));
                g.fill(-w, -h, -w + filo, h, conAlfa(0xFFB01818, apaga * 0.8F));
                g.pose().popMatrix();
            }
        }
        // El sello roto: sus trazos salen hacia fuera girando y se apagan.
        if (d < 26) {
            float giro0 = giro(MomentoMaldicionCliente.T_SILENCIO);
            float a = 1.0F - d / 26.0F;
            int n = 64;
            for (float rr : new float[]{R, R * 0.62F, R * 1.07F, R * 1.34F}) {
                for (int k = 0; k < n; k++) {
                    float ang0 = giro0 + k * Mth.TWO_PI / n;
                    float ang1 = giro0 + (k + 1) * Mth.TWO_PI / n;
                    float h = hash(k, Math.round(rr));
                    float v = d * (2.5F + 6 * h) * u;
                    float mx = Mth.cos((ang0 + ang1) / 2);
                    float my = Mth.sin((ang0 + ang1) / 2);
                    float ox = mx * v;
                    float oy = my * v + 0.3F * d * d * u;
                    float gira = (h - 0.5F) * d * 0.25F;
                    float x0 = Mth.cos(ang0) * rr;
                    float y0 = Mth.sin(ang0) * rr;
                    float x1 = Mth.cos(ang1) * rr;
                    float y1 = Mth.sin(ang1) * rr;
                    float px = (x0 + x1) / 2;
                    float py = (y0 + y1) / 2;
                    g.pose().pushMatrix();
                    g.pose().translate(cx + px + ox, cy + py + oy);
                    g.pose().rotate(gira);
                    trazo(g, x0 - px, y0 - py, x1 - px, y1 - py, 2.2F * u, conAlfa(d < 5 ? BLANCO : CALIENTE, a), a);
                    g.pose().popMatrix();
                }
            }
        }
        if (d < 10) {
            disco(g, cx, cy, R * (0.2F + d * 0.3F), conAlfa(0xFFFFF0E0, 1.0F - d / 10.0F));
        }
        if (d < 8) {
            // Blanco del todo un instante (las esquirlas solo se ven ya volando) y luego se va.
            g.fill(0, 0, SW, SH, conAlfa(0xFFFFFFFF, d < 3 ? 1.0F : 1.0F - (d - 3) / 5.0F));
        }
        if (d < 22) {
            g.fill(0, 0, SW, SH, conAlfa(0xFFB0101A, 0.4F * (1.0F - d / 22.0F)));
        }
        // La onda, con su brillo.
        if (d < 24) {
            float r = (4 + d * 34) * u;
            float k = 1.0F - d / 24.0F;
            g.pose().pushMatrix();
            g.pose().translate(cx, cy);
            circulo(g, r, 0, 1.0F, false, (3 + 5 * k) * u, conAlfa(d < 5 ? BLANCO : 0xFFFF5030, k), true);
            g.pose().popMatrix();
        }
        // Las chispas.
        if (d < 30) {
            for (int i = 0; i < 140; i++) {
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
        for (int i = 0; i < 180; i++) {
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
        // Las esquirlas: la pantalla en losas de tamaños distintos, algo movidas, que salen del centro girando.
        List<float[]> le = new ArrayList<>();
        float base = 46 * u;
        for (float y = -mh - base * 0.5F; y < mh + base; ) {
            float alto = base * (0.6F + r.nextFloat() * 0.9F);
            for (float x = -mw - r.nextFloat() * base; x < mw + base; ) {
                float ancho = base * (0.6F + r.nextFloat() * 1.0F);
                float mx = x + ancho / 2;
                float my = y + alto / 2;
                float dist = Math.max(1, (float) Math.hypot(mx, my));
                float v = 1.5F + r.nextFloat() * 3.5F;
                le.add(new float[]{mx, my, ancho * 1.1F, alto * 1.1F, mx / dist * v * 4, my / dist * v * 4 - 3,
                        (r.nextFloat() - 0.5F) * 0.12F, (r.nextFloat() - 0.5F) * 0.9F});
                x += ancho;
            }
            y += alto;
        }
        esquirlas = le.toArray(new float[0][]);
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
        g.pose().pushMatrix();
        g.pose().translate(x0, y0);
        g.pose().rotate((float) Math.atan2(dy, dx));
        int L = Math.round(largo) + 1;
        if (brillo > 0) {
            int a = Math.round(grosor * 5.0F);
            g.fill(-a / 2, -a, L + a / 2, a, conAlfa(color, 0.10F * brillo * alfa));
            int b = Math.round(grosor * 2.0F);
            g.fill(-b / 2, -b, L + b / 2, b, conAlfa(color, 0.28F * brillo * alfa));
        }
        int h = Math.max(1, Math.round(grosor));
        g.fill(0, -h / 2, L, h - h / 2, color);
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
