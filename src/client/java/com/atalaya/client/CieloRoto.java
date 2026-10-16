package com.atalaya.client;

import com.atalaya.Atalaya;
import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import net.fabricmc.fabric.api.client.rendering.v1.level.LevelRenderContext;
import net.fabricmc.fabric.api.client.rendering.v1.level.LevelRenderEvents;
import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.rendertype.RenderType;
import net.minecraft.client.renderer.rendertype.RenderTypes;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.resources.Identifier;
import net.minecraft.util.Mth;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Random;

/**
 * El cielo que se rompe en el Momento Maldicion (Juan, 15-10-2026: "el cielo
 * esta god... podrias hacer que el cielo se este fracturando"; "las grietas
 * deberian ser en todo el cielo y tener animacion"; "el cielo falta mejorar").
 *
 * Todo el cielo es un cristal roto: un mosaico de trozos irregulares (las
 * celdas de Voronoi de puntos repartidos por la cupula) cuyas juntas son
 * grietas quebradas, al rojo blanco por dentro y con un halo rojo. Con la
 * fractura se rajan desde lo alto hacia el horizonte, trozo a trozo; por las
 * grietas corren ondas de luz que salen de lo alto y todo late con el corazon
 * de la musica. Algunos trozos ya faltan (dejan ver la luz roja de detras) y,
 * mientras dura, cada pocos segundos se desprende otro: se enciende, cae
 * dando vueltas hacia el horizonte y deja su hueco de luz (con su sonido:
 * MomentoMaldicionCliente). En lo alto, una rasgadura de borde quebrado que
 * respira. Al pararlo, todo se cierra hacia arriba.
 *
 * Son cintas y abanicos emisivos en una cupula alrededor de la camara (se
 * mueven con ella: parecen estar infinitamente lejos).
 */
public final class CieloRoto {

    private static final RenderType GRIETA = RenderTypes.entityTranslucentEmissive(
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "textures/entity/momento/grieta.png"));
    /** El radio de la cupula (bloques): dentro de la niebla del cielo maldito. */
    private static final float RADIO = 42.0F;
    private static final int A_PLENA_LUZ = 0xF000F0;
    /** Los trozos del cristal. */
    private static final int TROZOS = 80;
    /** Los que ya faltan al romperse. */
    public static final int FALTAN_AL_ROMPER = 7;
    /** Cada cuanto se desprende otro mientras dura (ticks) y lo que tarda en caer. */
    public static final int CADA_DESPRENDE = 110;
    public static final int CAE = 46;

    private static long semilla = Long.MIN_VALUE;
    /** Las grietas: x0, y0, z0, x1, y1, z1, cuando se abre (0 a 1), grosor y la distancia a lo alto (para las ondas). */
    private static float[][] tramos = new float[0][];
    /** Los trozos: su centro y su borde (direcciones), en el orden en que se desprenden. */
    private static float[][] centros = new float[0][];
    private static float[][][] bordes = new float[0][][];
    /** La rasgadura: su borde quebrado (direcciones) y su centro. */
    private static float[][] rasgadura = new float[0][];
    private static float[] centroRasgadura = {0, 1, 0};

    private CieloRoto() {
    }

    public static void registrar() {
        LevelRenderEvents.COLLECT_SUBMITS.register(CieloRoto::pintar);
    }

    private static void pintar(LevelRenderContext ctx) {
        float parcial = Minecraft.getInstance().getDeltaTracker().getGameTimeDeltaPartialTick(false);
        float abierto = MomentoMaldicionCliente.grietasCielo(parcial);
        if (abierto <= 0) {
            return;
        }
        long s = MomentoMaldicionCliente.semilla();
        if (s != semilla) {
            semilla = s;
            preparar(s);
        }
        float late = MomentoMaldicionCliente.latido(parcial);
        float destello = MomentoMaldicionCliente.destelloCielo(parcial);
        float reloj = MomentoMaldicionCliente.relojCielo(parcial);
        float maldito = MomentoMaldicionCliente.malditoCielo(parcial);
        ctx.submitNodeCollector().submitCustomGeometry(ctx.poseStack(), GRIETA, (p, buf) -> {
            // Los huecos de luz y los trozos que caen.
            for (int i = 0; i < centros.length; i++) {
                float desde = desprende(i);
                if (desde == Float.MAX_VALUE) {
                    continue;
                }
                float d = maldito - desde;
                if (i < FALTAN_AL_ROMPER) {
                    hueco(buf, p, i, abierto * Mth.clamp((abierto - 0.3F) * 2.0F, 0.0F, 1.0F), late);
                } else if (d >= 0) {
                    hueco(buf, p, i, Mth.clamp(d / 10.0F, 0.0F, 1.0F) * abierto, late);
                    if (d < CAE) {
                        cae(buf, p, i, d / CAE);
                    }
                }
            }
            // La rasgadura de lo alto.
            float respira = 1.0F + 0.12F * Mth.sin(reloj * 0.05F) + 0.2F * late;
            rasgadura(buf, p, Mth.clamp(abierto * 1.5F, 0.0F, 1.0F) * respira, late, destello);
            // Las grietas, con las ondas de luz que bajan de lo alto.
            float onda = (reloj / 40.0F) % 1.0F;
            for (float[] q : tramos) {
                if (q[6] > abierto) {
                    continue;
                }
                float nuevo = Mth.clamp(1.0F - (abierto - q[6]) * 5.0F, 0.0F, 1.0F);
                float pulso = (float) Math.exp(-Math.pow((q[8] - onda) / 0.06F, 2))
                        + 0.6F * (float) Math.exp(-Math.pow((q[8] - (onda + 0.5F) % 1.0F) / 0.05F, 2));
                float g = q[7] * (1.0F + 0.25F * late + 0.6F * pulso);
                float brillo = Mth.clamp(0.4F + 0.3F * late + 0.6F * pulso + 0.5F * nuevo + 0.4F * destello, 0.0F, 1.0F);
                cinta(buf, p, q, g * 4.5F, 0xFF1E10, (int) (255 * Mth.clamp(0.06F + 0.1F * late + 0.18F * pulso + 0.25F * destello, 0, 1)));
                cinta(buf, p, q, g * 1.6F, 0xFF3A20, (int) (255 * brillo));
                cinta(buf, p, q, g * 0.45F, pulso > 0.35F || nuevo > 0.3F || destello > 0.4F ? 0xFFFFFF : 0xFFD0B4, 250);
            }
        });
    }

    /** Cuando se desprende el trozo i (ticks de maldito; los primeros ya faltan al romper), o MAX_VALUE si no toca. */
    public static float desprende(int i) {
        if (i < FALTAN_AL_ROMPER) {
            return -1;
        }
        return 40 + (i - FALTAN_AL_ROMPER) * (float) CADA_DESPRENDE;
    }

    /** El hueco de un trozo: un abanico de luz, al rojo vivo en el centro y rojo hondo en el borde, que late. */
    private static void hueco(VertexConsumer buf, PoseStack.Pose p, int i, float k, float late) {
        if (k <= 0) {
            return;
        }
        float[] c = centros[i];
        float[][] b = bordes[i];
        int centro = (int) (255 * Mth.clamp((0.85F + 0.15F * late) * k, 0, 1));
        int filo = (int) (255 * Mth.clamp(0.45F * k, 0, 1));
        abanico(buf, p, c, b, 0.96F, 0xFFB070, centro, 0xD01818, filo, 0.0F);
        abanico(buf, p, c, b, 0.45F, 0xFFF0E0, (int) (centro * 0.8F), 0xFF8A50, (int) (centro * 0.3F), 0.0F);
    }

    /** Un trozo que cae: se enciende, se encoge, da vueltas y baja hacia el horizonte. */
    private static void cae(VertexConsumer buf, PoseStack.Pose p, int i, float u) {
        float[] c = centros[i];
        float[][] b = bordes[i];
        float baja = u * u * 26.0F;
        float encoge = 1.0F - 0.7F * u;
        int a = (int) (255 * (1.0F - u));
        float[][] m = new float[b.length][];
        float giro = u * 2.5F;
        for (int k = 0; k < b.length; k++) {
            // Cada borde gira alrededor del centro del trozo y se acerca a el.
            float dx = (b[k][0] - c[0]) * encoge;
            float dy = (b[k][1] - c[1]) * encoge;
            float dz = (b[k][2] - c[2]) * encoge;
            float rx = dx * Mth.cos(giro) - dz * Mth.sin(giro);
            float rz = dx * Mth.sin(giro) + dz * Mth.cos(giro);
            m[k] = new float[]{c[0] + rx, c[1] + dy, c[2] + rz};
        }
        abanico(buf, p, c, m, 1.0F, 0xFFFFFF, a, 0xFF4A20, (int) (a * 0.8F), -baja);
    }

    /** Un abanico del centro c al borde b (encogido por k), con un color en el centro y otro en el borde; baja en Y. */
    private static void abanico(VertexConsumer buf, PoseStack.Pose p, float[] c, float[][] b, float k, int colorCentro, int alfaCentro,
                                int colorBorde, int alfaBorde, float baja) {
        float cx = c[0] * RADIO, cy = c[1] * RADIO + baja, cz = c[2] * RADIO;
        int r0 = (colorCentro >> 16) & 255, g0 = (colorCentro >> 8) & 255, b0 = colorCentro & 255;
        int r1 = (colorBorde >> 16) & 255, g1 = (colorBorde >> 8) & 255, b1 = colorBorde & 255;
        for (int i = 0; i < b.length; i++) {
            float[] e0 = b[i];
            float[] e1 = b[(i + 1) % b.length];
            float x0 = Mth.lerp(k, c[0], e0[0]) * RADIO, y0 = Mth.lerp(k, c[1], e0[1]) * RADIO + baja, z0 = Mth.lerp(k, c[2], e0[2]) * RADIO;
            float x1 = Mth.lerp(k, c[0], e1[0]) * RADIO, y1 = Mth.lerp(k, c[1], e1[1]) * RADIO + baja, z1 = Mth.lerp(k, c[2], e1[2]) * RADIO;
            for (int cara = 0; cara < 2; cara++) {
                vertice(buf, p, cx, cy, cz, 0.5F, 0.5F, r0, g0, b0, alfaCentro);
                if (cara == 0) {
                    vertice(buf, p, x0, y0, z0, 0.5F, 0.0F, r1, g1, b1, alfaBorde);
                    vertice(buf, p, x1, y1, z1, 0.5F, 1.0F, r1, g1, b1, alfaBorde);
                } else {
                    vertice(buf, p, x1, y1, z1, 0.5F, 1.0F, r1, g1, b1, alfaBorde);
                    vertice(buf, p, x0, y0, z0, 0.5F, 0.0F, r1, g1, b1, alfaBorde);
                }
                vertice(buf, p, cx, cy, cz, 0.5F, 0.5F, r0, g0, b0, alfaCentro);
            }
        }
    }

    /** La rasgadura de lo alto: el interior de luz (blanco en el centro) y su borde quebrado encendido. */
    private static void rasgadura(VertexConsumer buf, PoseStack.Pose p, float abre, float late, float destello) {
        if (abre <= 0.01F || rasgadura.length == 0) {
            return;
        }
        float[][] borde = new float[rasgadura.length][];
        for (int i = 0; i < rasgadura.length; i++) {
            float[] q = rasgadura[i];
            borde[i] = new float[]{Mth.lerp(abre, centroRasgadura[0], q[0]), Mth.lerp(abre, centroRasgadura[1], q[1]),
                    Mth.lerp(abre, centroRasgadura[2], q[2])};
        }
        abanico(buf, p, centroRasgadura, borde, 1.25F, 0xFF2A14, (int) (90 + 60 * late), 0x8A0A10, 0, 0);
        abanico(buf, p, centroRasgadura, borde, 1.0F, 0xFFF4E8, 255, 0xFF3A20, (int) (200 + 55 * destello), 0);
        for (int i = 0; i < borde.length; i++) {
            float[] a = borde[i];
            float[] b = borde[(i + 1) % borde.length];
            float[] q = {a[0], a[1], a[2], b[0], b[1], b[2]};
            cinta(buf, p, q, 1.6F, 0xFF3A20, (int) (180 + 60 * late));
            cinta(buf, p, q, 0.5F, 0xFFFFFF, 255);
        }
    }

    /** Una cinta entre dos direcciones de la cupula, de cara a la camara (en el centro), por las dos caras. */
    private static void cinta(VertexConsumer buf, PoseStack.Pose p, float[] q, float ancho, int color, int alfa) {
        float ax = q[0] * RADIO, ay = q[1] * RADIO, az = q[2] * RADIO;
        float bx = q[3] * RADIO, by = q[4] * RADIO, bz = q[5] * RADIO;
        float dx = bx - ax, dy = by - ay, dz = bz - az;
        float mx = (ax + bx) / 2, my = (ay + by) / 2, mz = (az + bz) / 2;
        float lx = dy * mz - dz * my;
        float ly = dz * mx - dx * mz;
        float lz = dx * my - dy * mx;
        float l = (float) Math.sqrt(lx * lx + ly * ly + lz * lz);
        if (l < 1.0E-5F || alfa <= 0) {
            return;
        }
        alfa = Math.min(255, alfa);
        lx *= ancho / 2 / l;
        ly *= ancho / 2 / l;
        lz *= ancho / 2 / l;
        int r = (color >> 16) & 255, g = (color >> 8) & 255, b = color & 255;
        for (int cara = 0; cara < 2; cara++) {
            float s = cara == 0 ? 1 : -1;
            vertice(buf, p, ax - lx * s, ay - ly * s, az - lz * s, 0, 0, r, g, b, alfa);
            vertice(buf, p, ax + lx * s, ay + ly * s, az + lz * s, 1, 0, r, g, b, alfa);
            vertice(buf, p, bx + lx * s, by + ly * s, bz + lz * s, 1, 1, r, g, b, alfa);
            vertice(buf, p, bx - lx * s, by - ly * s, bz - lz * s, 0, 1, r, g, b, alfa);
        }
    }

    private static void vertice(VertexConsumer buf, PoseStack.Pose p, float x, float y, float z, float u, float v, int r, int g, int b, int a) {
        buf.addVertex(p, x, y, z).setColor(r, g, b, a).setUv(u, v).setOverlay(OverlayTexture.NO_OVERLAY)
                .setLight(A_PLENA_LUZ).setNormal(p, 0, 1, 0);
    }

    // ------------------------------------------------------------------
    //  El cristal: Voronoi en la cupula
    // ------------------------------------------------------------------

    /**
     * Los puntos del cristal (repartidos por la cupula, mas juntos en lo alto),
     * sus celdas de Voronoi (los vertices son los puntos a la misma distancia de
     * tres semillas sin ninguna mas cerca) y las grietas (las juntas entre dos
     * celdas, quebradas en tres tramos). Cada grieta se abre por orden de
     * distancia a lo alto, recorriendo las celdas desde la de arriba.
     */
    private static void preparar(long s) {
        Random r = new Random(s ^ 0x5EEDL);
        // Las semillas: una espiral de Fibonacci en la cupula (por encima de 4 grados), algo movida, y unas pocas bajo
        // el horizonte para cerrar las celdas de abajo.
        List<float[]> semillas = new ArrayList<>();
        int n = TROZOS;
        for (int i = 0; i < n; i++) {
            float y = 1.0F - (i + 0.5F) / n * 0.95F;
            float rad = (float) Math.sqrt(Math.max(0, 1 - y * y));
            float a = i * 2.39996F + r.nextFloat() * 0.5F;
            semillas.add(normal(new float[]{rad * Mth.cos(a), y + (r.nextFloat() - 0.5F) * 0.05F, rad * Mth.sin(a)}));
        }
        for (int i = 0; i < 10; i++) {
            float a = i * Mth.TWO_PI / 10;
            semillas.add(normal(new float[]{Mth.cos(a), -0.35F, Mth.sin(a)}));
        }
        float[][] sem = semillas.toArray(new float[0][]);
        int m = sem.length;
        // Los vecinos cercanos de cada semilla (para no probar todas las ternas).
        int[][] vecinos = new int[m][];
        for (int i = 0; i < m; i++) {
            Integer[] idx = new Integer[m];
            for (int j = 0; j < m; j++) {
                idx[j] = j;
            }
            final int ii = i;
            Arrays.sort(idx, (a, b) -> Float.compare(dist(sem[ii], sem[a]), dist(sem[ii], sem[b])));
            vecinos[i] = new int[Math.min(12, m - 1)];
            for (int k = 0; k < vecinos[i].length; k++) {
                vecinos[i][k] = idx[k + 1];
            }
        }
        // Los vertices de Voronoi: para cada terna de vecinos, el punto a la misma distancia de las tres.
        Map<Long, float[]> vertices = new HashMap<>();
        Map<Long, List<Long>> porArista = new HashMap<>();
        for (int i = 0; i < m; i++) {
            for (int a = 0; a < vecinos[i].length; a++) {
                for (int b = a + 1; b < vecinos[i].length; b++) {
                    int j = vecinos[i][a];
                    int k = vecinos[i][b];
                    if (!(i < j && j < k) && !(i < k && k < j)) {
                        continue;
                    }
                    int[] t3 = {i, Math.min(j, k), Math.max(j, k)};
                    long clave = ((long) t3[0] << 40) | ((long) t3[1] << 20) | t3[2];
                    if (vertices.containsKey(clave)) {
                        continue;
                    }
                    float[] v = equidistante(sem[t3[0]], sem[t3[1]], sem[t3[2]]);
                    if (v == null) {
                        continue;
                    }
                    float d = dist(v, sem[t3[0]]);
                    boolean libre = true;
                    for (int q = 0; q < m && libre; q++) {
                        if (q != t3[0] && q != t3[1] && q != t3[2] && dist(v, sem[q]) < d - 1.0E-5F) {
                            libre = false;
                        }
                    }
                    if (!libre) {
                        continue;
                    }
                    vertices.put(clave, v);
                    for (int[] par : new int[][]{{t3[0], t3[1]}, {t3[0], t3[2]}, {t3[1], t3[2]}}) {
                        porArista.computeIfAbsent(((long) par[0] << 20) | par[1], x -> new ArrayList<>()).add(clave);
                    }
                }
            }
        }
        // Las grietas: cada junta entre dos celdas, quebrada en tres tramos (solo lo que esta sobre el horizonte).
        int arriba = 0;
        for (int i = 1; i < n; i++) {
            if (sem[i][1] > sem[arriba][1]) {
                arriba = i;
            }
        }
        float[] cenit = {0, 1, 0};
        List<float[]> lista = new ArrayList<>();
        Map<Integer, List<float[]>> bordesDe = new HashMap<>();
        for (Map.Entry<Long, List<Long>> e : porArista.entrySet()) {
            if (e.getValue().size() != 2) {
                continue;
            }
            float[] a = vertices.get(e.getValue().get(0));
            float[] b = vertices.get(e.getValue().get(1));
            int si = (int) (e.getKey() >> 20);
            int sj = (int) (e.getKey() & 0xFFFFF);
            bordesDe.computeIfAbsent(si, x -> new ArrayList<>()).add(a);
            bordesDe.computeIfAbsent(si, x -> new ArrayList<>()).add(b);
            bordesDe.computeIfAbsent(sj, x -> new ArrayList<>()).add(a);
            bordesDe.computeIfAbsent(sj, x -> new ArrayList<>()).add(b);
            if (a[1] < 0.06F && b[1] < 0.06F) {
                continue;
            }
            float[] p0 = a;
            for (int k = 1; k <= 3; k++) {
                float f = k / 3.0F;
                float[] p1 = k == 3 ? b : normal(lerp(a, b, f));
                if (k < 3) {
                    // Un codo: se aparta un poco de la recta.
                    float[] lado = normal(cruz(sub(b, a), p1));
                    float desvio = (r.nextFloat() - 0.5F) * 0.35F * dist(a, b);
                    p1 = normal(new float[]{p1[0] + lado[0] * desvio, p1[1] + lado[1] * desvio, p1[2] + lado[2] * desvio});
                }
                float alto = 1.0F - Math.max(0, Math.min(p0[1], p1[1]));
                float hacia = (float) Math.acos(Mth.clamp(punto(normal(lerp(p0, p1, 0.5F)), cenit), -1, 1)) / Mth.HALF_PI;
                float grosor = 1.5F - 0.6F * hacia + 0.3F * r.nextFloat();
                lista.add(new float[]{p0[0], p0[1], p0[2], p1[0], p1[1], p1[2], Mth.clamp(hacia * 0.9F, 0, 1), grosor, hacia});
                p0 = p1;
            }
        }
        tramos = lista.toArray(new float[0][]);
        // Los trozos: los que estan sobre el horizonte, con su borde ordenado alrededor del centro; se desprenden en
        // un orden al azar (los que faltan al romper, primero).
        List<Integer> orden = new ArrayList<>();
        for (int i = 0; i < n; i++) {
            if (sem[i][1] > 0.25F && sem[i][1] < 0.97F && bordesDe.containsKey(i)) {
                orden.add(i);
            }
        }
        java.util.Collections.shuffle(orden, r);
        centros = new float[orden.size()][];
        bordes = new float[orden.size()][][];
        for (int k = 0; k < orden.size(); k++) {
            int i = orden.get(k);
            centros[k] = sem[i];
            bordes[k] = ordenar(sem[i], bordesDe.get(i));
        }
        // La rasgadura, alrededor de lo alto: un huso de borde quebrado.
        centroRasgadura = normal(new float[]{(r.nextFloat() - 0.5F) * 0.08F, 1, (r.nextFloat() - 0.5F) * 0.08F});
        float ang = r.nextFloat() * Mth.TWO_PI;
        float[] e1 = {Mth.cos(ang), 0, Mth.sin(ang)};
        float[] e2 = {-Mth.sin(ang), 0, Mth.cos(ang)};
        int puntos = 26;
        rasgadura = new float[puntos][];
        for (int i = 0; i < puntos; i++) {
            float a = i * Mth.TWO_PI / puntos;
            float x = Mth.cos(a) * 0.30F;
            float y = Math.signum(Mth.sin(a)) * (float) Math.pow(Math.abs(Mth.sin(a)), 1.5) * 0.085F * (0.7F + 0.6F * r.nextFloat());
            rasgadura[i] = normal(new float[]{centroRasgadura[0] + e1[0] * x + e2[0] * y, centroRasgadura[1],
                    centroRasgadura[2] + e1[2] * x + e2[2] * y});
        }
    }

    /** Los puntos del borde de una celda, sin repetir y en orden alrededor de su centro. */
    private static float[][] ordenar(float[] c, List<float[]> puntos) {
        List<float[]> unicos = new ArrayList<>();
        for (float[] q : puntos) {
            boolean ya = false;
            for (float[] u : unicos) {
                if (dist(u, q) < 1.0E-4F) {
                    ya = true;
                    break;
                }
            }
            if (!ya) {
                unicos.add(q);
            }
        }
        float[] e1 = normal(cruz(c, Math.abs(c[1]) < 0.9F ? new float[]{0, 1, 0} : new float[]{1, 0, 0}));
        float[] e2 = cruz(c, e1);
        unicos.sort((a, b) -> Float.compare((float) Math.atan2(punto(a, e2), punto(a, e1)), (float) Math.atan2(punto(b, e2), punto(b, e1))));
        return unicos.toArray(new float[0][]);
    }

    /** El punto de la esfera a la misma distancia de a, b y c (el del lado de a). */
    private static float[] equidistante(float[] a, float[] b, float[] c) {
        float[] n = cruz(sub(b, a), sub(c, a));
        float l = (float) Math.sqrt(punto(n, n));
        if (l < 1.0E-7F) {
            return null;
        }
        n = new float[]{n[0] / l, n[1] / l, n[2] / l};
        return punto(n, a) >= 0 ? n : new float[]{-n[0], -n[1], -n[2]};
    }

    private static float dist(float[] a, float[] b) {
        float dx = a[0] - b[0], dy = a[1] - b[1], dz = a[2] - b[2];
        return (float) Math.sqrt(dx * dx + dy * dy + dz * dz);
    }

    private static float[] sub(float[] a, float[] b) {
        return new float[]{a[0] - b[0], a[1] - b[1], a[2] - b[2]};
    }

    private static float[] cruz(float[] a, float[] b) {
        return new float[]{a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]};
    }

    private static float punto(float[] a, float[] b) {
        return a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
    }

    private static float[] lerp(float[] a, float[] b, float f) {
        return new float[]{Mth.lerp(f, a[0], b[0]), Mth.lerp(f, a[1], b[1]), Mth.lerp(f, a[2], b[2])};
    }

    private static float[] normal(float[] a) {
        float l = (float) Math.sqrt(punto(a, a));
        return l < 1.0E-7F ? new float[]{0, 1, 0} : new float[]{a[0] / l, a[1] / l, a[2] / l};
    }

    /** Cuantos trozos hay (para los sonidos de los que se desprenden). */
    public static int trozos() {
        return centros.length;
    }
}
