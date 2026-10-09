package com.atalaya.client;

import com.atalaya.Atalaya;
import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import net.minecraft.client.renderer.rendertype.RenderType;
import net.minecraft.client.renderer.rendertype.RenderTypes;
import net.minecraft.resources.Identifier;
import net.minecraft.util.Mth;
import net.minecraft.world.phys.Vec3;

/**
 * Como se dibuja una morena del abismo (octubre de 2026; Juan: "mejora su
 * diseno y animaciones, se ven simples"): un cuerpo largo de doce tramos que se
 * estrecha hacia la cola, con la piel de la morena reticulada (verde abisal y
 * la red clara), el vientre palido y la aleta que le corre por el lomo; la
 * cabeza alta con el hocico, las narices de tubo, la mandibula que se abre, los
 * colmillos, los ojos cian de la maldicion y, al morder, la segunda mandibula
 * que le sale de la garganta (como las de verdad).
 *
 * La textura es morena.png (nerea_minijuegos.py); las regiones son las de alli.
 * Quien la usa (MorenaNereaRenderer, MorenaSaltoRenderer) solo calcula la
 * espina: los puntos de la cola al cuello, y hacia donde mira la cabeza.
 */
final class MorenaDibujo {

    static final RenderType PIEL = RenderTypes.entityCutout(
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "textures/entity/nerea/morena.png"));

    private static final float T = 64.0F;
    // Las regiones de morena.png (x, y, ancho, alto), como en nerea_minijuegos.py.
    private static final int[] LADO = {0, 0, 64, 12};
    private static final int[] LOMO = {0, 12, 64, 8};
    private static final int[] PANZA = {0, 20, 64, 6};
    private static final int[] ALETA = {0, 26, 64, 8};
    private static final int[] CAB_LADO = {0, 34, 16, 12};
    private static final int[] CAB_ARRIBA = {16, 34, 16, 12};
    private static final int[] HOCICO = {32, 34, 8, 8};
    private static final int[] MANDIBULA = {40, 34, 16, 8};
    private static final int[] BOCA = {56, 34, 8, 8};
    private static final int[] DIENTE = {0, 46, 4, 4};
    private static final int[] OJO = {4, 46, 4, 4};
    static final int[] ROCA = {8, 46, 16, 16};
    private static final int[] EXTREMO = {24, 46, 8, 8};
    private static final int[] FARINGE = {32, 46, 8, 8};

    private static final int A_PLENA_LUZ = 0xF000F0;
    private static final Vec3 ARRIBA = new Vec3(0, 1, 0);

    private MorenaDibujo() {
    }

    /** El grosor del cuerpo en t (0 la punta de la cola, 1 el cuello). */
    static double grosor(double t) {
        double r = 0.06 + 0.24 * Math.pow(Math.sin(Math.min(1.0, t * 1.45) * Math.PI / 2), 0.8);
        if (t > 0.85) {
            r -= (t - 0.85) / 0.15 * 0.03;
        }
        return r;
    }

    /**
     * El cuerpo: un tramo entre cada dos puntos de la espina (de la cola al
     * cuello), cada uno con su trozo de piel para que la red siga de uno a otro,
     * y la aleta por el lomo.
     */
    static void cuerpo(VertexConsumer buf, PoseStack.Pose p, Vec3[] espina, float escala, int luz, int overlay, int tinte) {
        int n = espina.length - 1;
        Vec3 arribaAntes = ARRIBA;
        for (int i = 0; i < n; i++) {
            Vec3 a = espina[i];
            Vec3 b = espina[i + 1];
            Vec3 eje = b.subtract(a);
            double largo = eje.length();
            if (largo < 1.0E-4) {
                continue;
            }
            Vec3 t = eje.scale(1.0 / largo);
            // El lado: perpendicular a la espina y al "arriba" que trae del tramo de antes (no gira de golpe).
            Vec3 lado = arribaAntes.cross(t);
            if (lado.lengthSqr() < 1.0E-6) {
                lado = new Vec3(1, 0, 0).cross(t);
            }
            lado = lado.normalize();
            Vec3 arr = t.cross(lado).normalize();
            arribaAntes = arr;
            double tm = (i + 0.5) / n;
            double r = grosor(tm) * escala;
            Vec3 c = a.add(b).scale(0.5);
            float u0 = LADO[2] * (float) i / n;
            float u1 = LADO[2] * (float) (i + 1) / n;
            Vec3 ht = t.scale(largo * 0.6);
            Vec3 hs = lado.scale(r * 0.78);
            Vec3 hu = arr.scale(r);
            // Los costados, el lomo, el vientre y las puntas.
            cara(buf, p, c.add(hs), ht, hu, lado, LADO[0] + u0, LADO[1], LADO[0] + u1, LADO[1] + LADO[3], tinte, luz, overlay);
            cara(buf, p, c.subtract(hs), ht, hu, lado.scale(-1), LADO[0] + u0, LADO[1], LADO[0] + u1, LADO[1] + LADO[3], tinte, luz, overlay);
            cara(buf, p, c.add(hu), ht, hs, arr, LOMO[0] + u0, LOMO[1], LOMO[0] + u1, LOMO[1] + LOMO[3], tinte, luz, overlay);
            cara(buf, p, c.subtract(hu), ht, hs, arr.scale(-1), PANZA[0] + u0, PANZA[1], PANZA[0] + u1, PANZA[1] + PANZA[3], tinte, luz, overlay);
            if (i == 0) {
                cara(buf, p, c.subtract(ht), hs, hu, t.scale(-1), EXTREMO, tinte, luz, overlay);
            }
            // La aleta del lomo, de la cola casi hasta la cabeza; y la de abajo, en la mitad de atras.
            if (tm > 0.08 && tm < 0.94) {
                double alto = escala * (0.07 + 0.07 * Math.sin(tm * Math.PI));
                Vec3 ca = c.add(arr.scale(r + alto * 0.85));
                Vec3 ha = arr.scale(alto);
                Vec3 grueso = lado.scale(0.012 * escala);
                cara(buf, p, ca.add(grueso), ht, ha, lado, ALETA[0] + u0, ALETA[1], ALETA[0] + u1, ALETA[1] + ALETA[3], tinte, luz, overlay);
                cara(buf, p, ca.subtract(grueso), ht, ha, lado.scale(-1), ALETA[0] + u0, ALETA[1], ALETA[0] + u1, ALETA[1] + ALETA[3], tinte, luz, overlay);
            }
            if (tm > 0.05 && tm < 0.45) {
                double alto = escala * 0.06 * Math.sin(tm / 0.45 * Math.PI);
                Vec3 ca = c.subtract(arr.scale(r + alto * 0.85));
                Vec3 ha = arr.scale(-alto);
                Vec3 grueso = lado.scale(0.012 * escala);
                cara(buf, p, ca.add(grueso), ht, ha, lado, ALETA[0] + u0, ALETA[1], ALETA[0] + u1, ALETA[1] + ALETA[3], tinte, luz, overlay);
                cara(buf, p, ca.subtract(grueso), ht, ha, lado.scale(-1), ALETA[0] + u0, ALETA[1], ALETA[0] + u1, ALETA[1] + ALETA[3], tinte, luz, overlay);
            }
        }
    }

    /**
     * La cabeza en el cuello, mirando a f (con arriba u): craneo, hocico, narices,
     * mandibula abierta "boca" (0 cerrada, 1 del todo), la boca roja, los
     * colmillos, los ojos y la segunda mandibula ("faringe", de 0 a 1).
     */
    static void cabeza(VertexConsumer buf, PoseStack.Pose p, Vec3 cuello, Vec3 f, Vec3 u, float boca, float faringe,
                       float escala, int luz, int overlay, int tinte) {
        f = f.normalize();
        Vec3 s = u.cross(f);
        if (s.lengthSqr() < 1.0E-6) {
            s = new Vec3(1, 0, 0);
        }
        s = s.normalize();
        u = f.cross(s).normalize();
        double e = escala;
        // El craneo, alto y algo levantado sobre el cuello.
        Vec3 craneo = cuello.add(f.scale(0.2 * e)).add(u.scale(0.03 * e));
        caja(buf, p, craneo, f.scale(0.26 * e), s.scale(0.235 * e), u.scale(0.26 * e),
                CAB_LADO, CAB_ARRIBA, BOCA, HOCICO, EXTREMO, tinte, luz, overlay);
        // El hocico, mas estrecho, delante.
        Vec3 hocico = craneo.add(f.scale(0.38 * e)).add(u.scale(0.05 * e));
        caja(buf, p, hocico, f.scale(0.14 * e), s.scale(0.17 * e), u.scale(0.15 * e),
                CAB_LADO, CAB_ARRIBA, BOCA, HOCICO, EXTREMO, tinte, luz, overlay);
        // Las narices de tubo, encima de la punta.
        for (int l = -1; l <= 1; l += 2) {
            Vec3 nariz = hocico.add(f.scale(0.12 * e)).add(u.scale(0.17 * e)).add(s.scale(0.08 * e * l));
            caja(buf, p, nariz, f.scale(0.025 * e), s.scale(0.025 * e), u.scale(0.05 * e),
                    EXTREMO, EXTREMO, EXTREMO, EXTREMO, EXTREMO, tinte, luz, overlay);
        }
        // La mandibula: gira hacia abajo desde la bisagra, bajo el craneo.
        double a = Mth.clamp(boca, 0.0F, 1.0F) * 0.95;
        Vec3 fj = f.scale(Math.cos(a)).subtract(u.scale(Math.sin(a)));
        Vec3 uj = u.scale(Math.cos(a)).add(f.scale(Math.sin(a)));
        Vec3 bisagra = cuello.add(u.scale(-0.2 * e)).add(f.scale(0.02 * e));
        Vec3 mand = bisagra.add(fj.scale(0.36 * e)).add(uj.scale(-0.02 * e));
        caja(buf, p, mand, fj.scale(0.36 * e), s.scale(0.19 * e), uj.scale(0.075 * e),
                MANDIBULA, BOCA, MANDIBULA, MANDIBULA, EXTREMO, tinte, luz, overlay);
        // Lo rojo de dentro, entre las dos mandibulas.
        if (a > 0.05) {
            Vec3 dentro = bisagra.add(f.scale(0.3 * e)).add(u.scale(0.07 * e)).add(fj.scale(0.04 * e));
            caja(buf, p, dentro, f.scale(0.28 * e), s.scale(0.17 * e), u.scale((0.05 + 0.12 * a) * e),
                    BOCA, BOCA, BOCA, BOCA, BOCA, tinte, luz, overlay);
        }
        // Colmillos: arriba, por el filo del craneo y el hocico; abajo, en la mandibula.
        double[] arriba = {0.12, 0.26, 0.42, 0.58};
        for (int l = -1; l <= 1; l += 2) {
            for (int k = 0; k < arriba.length; k++) {
                Vec3 d = cuello.add(f.scale(arriba[k] * e)).add(u.scale(-0.2 * e)).add(s.scale((0.15 - 0.02 * k) * e * l));
                double largo = (k == 3 ? 0.075 : 0.05) * e;
                caja(buf, p, d.subtract(u.scale(largo)), f.scale(0.018 * e), s.scale(0.018 * e), u.scale(largo),
                        DIENTE, DIENTE, DIENTE, DIENTE, DIENTE, 0xFFFFFF, luz, overlay);
            }
            for (int k = 0; k < 3; k++) {
                Vec3 d = bisagra.add(fj.scale((0.22 + 0.17 * k) * e)).add(s.scale((0.13 - 0.02 * k) * e * l));
                caja(buf, p, d.add(uj.scale(0.1 * e)), fj.scale(0.016 * e), s.scale(0.016 * e), uj.scale(0.045 * e),
                        DIENTE, DIENTE, DIENTE, DIENTE, DIENTE, 0xFFFFFF, luz, overlay);
            }
        }
        // Los ojos, a los lados del craneo, a plena luz.
        for (int l = -1; l <= 1; l += 2) {
            Vec3 o = craneo.add(f.scale(0.12 * e)).add(u.scale(0.11 * e)).add(s.scale(0.24 * e * l));
            caja(buf, p, o, f.scale(0.055 * e), s.scale(0.012 * e), u.scale(0.05 * e),
                    OJO, OJO, OJO, OJO, OJO, 0xFFFFFF, A_PLENA_LUZ, overlay);
        }
        // La segunda mandibula: sale de la garganta al morder.
        if (faringe > 0.02F) {
            Vec3 fa = cuello.add(f.scale((0.05 + 0.55 * faringe) * e)).add(u.scale(-0.08 * e));
            caja(buf, p, fa, f.scale(0.12 * e), s.scale(0.08 * e), u.scale(0.06 * e),
                    FARINGE, FARINGE, FARINGE, FARINGE, FARINGE, tinte, luz, overlay);
            for (int l = -1; l <= 1; l += 2) {
                Vec3 d = fa.add(f.scale(0.1 * e)).add(s.scale(0.05 * e * l));
                caja(buf, p, d, f.scale(0.014 * e), s.scale(0.014 * e), u.scale(0.07 * e),
                        DIENTE, DIENTE, DIENTE, DIENTE, DIENTE, 0xFFFFFF, luz, overlay);
            }
        }
    }

    /** Una caja con un trozo de textura por cara: costados, arriba, abajo, delante (+f) y detras. */
    static void caja(VertexConsumer buf, PoseStack.Pose p, Vec3 c, Vec3 hf, Vec3 hs, Vec3 hu,
                     int[] lado, int[] arriba, int[] abajo, int[] delante, int[] detras, int tinte, int luz, int overlay) {
        Vec3 nf = hf.normalize();
        Vec3 ns = hs.normalize();
        Vec3 nu = hu.normalize();
        cara(buf, p, c.add(hs), hf, hu, ns, lado, tinte, luz, overlay);
        cara(buf, p, c.subtract(hs), hf, hu, ns.scale(-1), lado, tinte, luz, overlay);
        cara(buf, p, c.add(hu), hf, hs, nu, arriba, tinte, luz, overlay);
        cara(buf, p, c.subtract(hu), hf, hs, nu.scale(-1), abajo, tinte, luz, overlay);
        cara(buf, p, c.add(hf), hs, hu, nf, delante, tinte, luz, overlay);
        cara(buf, p, c.subtract(hf), hs, hu, nf.scale(-1), detras, tinte, luz, overlay);
    }

    static void cara(VertexConsumer buf, PoseStack.Pose p, Vec3 c, Vec3 eu, Vec3 ev, Vec3 n, int[] r, int tinte, int luz,
                     int overlay) {
        cara(buf, p, c, eu, ev, n, r[0], r[1], r[0] + r[2], r[1] + r[3], tinte, luz, overlay);
    }

    /**
     * Una cara: centro c, medio eje eu (a lo ancho de la textura) y ev (hacia
     * arriba de la textura), mirando a n. Da la vuelta a eu si hace falta para
     * que el giro de los vertices salga hacia n (las caras de atras no se pintan).
     */
    static void cara(VertexConsumer buf, PoseStack.Pose p, Vec3 c, Vec3 eu, Vec3 ev, Vec3 n,
                     float u0, float v0, float u1, float v1, int tinte, int luz, int overlay) {
        if (eu.cross(ev).dot(n) < 0) {
            eu = eu.scale(-1);
            float x = u0;
            u0 = u1;
            u1 = x;
        }
        Vec3 nn = n.normalize();
        // Arriba algo mas claro y abajo mas oscuro, como CajaDibujo: se lee el volumen.
        int col = CajaDibujo.escalar(tinte, (float) (0.84 + 0.16 * nn.y));
        vertice(buf, p, c.subtract(eu).subtract(ev), u0 / T, v1 / T, col, luz, overlay, nn);
        vertice(buf, p, c.add(eu).subtract(ev), u1 / T, v1 / T, col, luz, overlay, nn);
        vertice(buf, p, c.add(eu).add(ev), u1 / T, v0 / T, col, luz, overlay, nn);
        vertice(buf, p, c.subtract(eu).add(ev), u0 / T, v0 / T, col, luz, overlay, nn);
    }

    private static void vertice(VertexConsumer buf, PoseStack.Pose p, Vec3 q, float u, float v, int color, int luz, int overlay,
                                Vec3 n) {
        buf.addVertex(p, (float) q.x, (float) q.y, (float) q.z)
                .setColor((color >> 16) & 255, (color >> 8) & 255, color & 255, 255)
                .setUv(u, v)
                .setOverlay(overlay)
                .setLight(luz)
                .setNormal(p, (float) n.x, (float) n.y, (float) n.z);
    }

    /**
     * Una curva suave por los puntos de control (Catmull-Rom), con "cuantos"
     * puntos repartidos por su largo: la espina de la morena.
     */
    static Vec3[] repartir(Vec3[] control, int cuantos) {
        int muestras = 64;
        Vec3[] fina = new Vec3[muestras + 1];
        double[] largo = new double[muestras + 1];
        int tramos = control.length - 1;
        for (int i = 0; i <= muestras; i++) {
            double g = i / (double) muestras * tramos;
            int k = Math.min(tramos - 1, (int) g);
            double t = g - k;
            Vec3 p0 = control[Math.max(0, k - 1)];
            Vec3 p1 = control[k];
            Vec3 p2 = control[k + 1];
            Vec3 p3 = control[Math.min(tramos, k + 2)];
            fina[i] = catmull(p0, p1, p2, p3, t);
            largo[i] = i == 0 ? 0 : largo[i - 1] + fina[i].distanceTo(fina[i - 1]);
        }
        Vec3[] out = new Vec3[cuantos];
        double total = largo[muestras];
        int j = 0;
        for (int i = 0; i < cuantos; i++) {
            double objetivo = total * i / (cuantos - 1);
            while (j < muestras - 1 && largo[j + 1] < objetivo) {
                j++;
            }
            double tramo = largo[j + 1] - largo[j];
            double k = tramo < 1.0E-9 ? 0 : (objetivo - largo[j]) / tramo;
            out[i] = fina[j].lerp(fina[j + 1], Mth.clamp(k, 0, 1));
        }
        return out;
    }

    private static Vec3 catmull(Vec3 p0, Vec3 p1, Vec3 p2, Vec3 p3, double t) {
        double t2 = t * t;
        double t3 = t2 * t;
        return p0.scale(-0.5 * t3 + t2 - 0.5 * t)
                .add(p1.scale(1.5 * t3 - 2.5 * t2 + 1.0))
                .add(p2.scale(-1.5 * t3 + 2.0 * t2 + 0.5 * t))
                .add(p3.scale(0.5 * t3 - 0.5 * t2));
    }
}
