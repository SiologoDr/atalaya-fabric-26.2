package com.atalaya.client;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import net.minecraft.util.Mth;
import net.minecraft.world.phys.Vec3;
import org.jspecify.annotations.Nullable;

import java.util.ArrayList;
import java.util.List;
import java.util.Random;

/**
 * La geometria de las piezas de los ataques de Rajang, hecha a mano y con
 * semilla (la misma en todos los clientes): las esquirlas de roca de la Garra
 * (prisma irregular con su punta, inclinado), los bloques torcidos de los
 * pilares del Terremoto y los terrones. Es lo mismo que tierra_ataques.py
 * dibujo para la ficha, pasado a Java.
 *
 * Todo en bloques, con Y hacia arriba y +Z hacia delante. Cada cara es un
 * cuadrilatero (los triangulos repiten un vertice) con su UV.
 */
final class RajangDibujo {

    /** Un cuadrilatero: cuatro puntos y sus UV (u0 v0 u1 v1 u2 v2 u3 v3). */
    record Cara(Vec3 a, Vec3 b, Vec3 c, Vec3 d, float[] uv) {
    }

    private static final float TAU = (float) (Math.PI * 2);

    private RajangDibujo() {
    }

    // ------------------------------------------------------------------
    //  Esquirlas
    // ------------------------------------------------------------------

    /**
     * Una esquirla que sale del suelo en (x, z): prisma irregular de 'lados'
     * caras que se estrecha y acaba en punta, inclinado (ix, iz). Con extras,
     * las esquirlas menores abiertas alrededor y los terrones al pie.
     */
    static void esquirla(List<Cara> out, Random r, double x, double z, double alto, double radio, double ix, double iz,
                         int lados, boolean extras) {
        Vec3 e = new Vec3(ix, 1.0, iz).normalize();
        Vec3 a = e.cross(new Vec3(0, 0, 1));
        if (a.lengthSqr() < 1.0E-6) {
            a = new Vec3(1, 0, 0);
        }
        a = a.normalize();
        Vec3 b = e.cross(a);
        double largo = alto / e.y;
        Vec3 base = new Vec3(x, 0, z);
        double giro = r.nextDouble() * TAU;
        Vec3[] A = anillo(r, base, e, a, b, largo, -0.15, 1.0, radio, lados, giro);
        double tb = 0.6 + r.nextDouble() * 0.12;
        Vec3[] B = anillo(r, base, e, a, b, largo, tb, 0.75 + r.nextDouble() * 0.15, radio, lados, giro);
        Vec3 apice = base.add(e.scale(largo)).add(a.scale((r.nextDouble() - 0.5) * 0.24 * radio))
                .add(b.scale((r.nextDouble() - 0.5) * 0.24 * radio));
        float vt = (float) tb;
        for (int i = 0; i < lados; i++) {
            int j = (i + 1) % lados;
            out.add(new Cara(A[i], A[j], B[j], B[i], new float[]{0, 1, 1, 1, 1, 1 - vt, 0, 1 - vt}));
            out.add(new Cara(B[i], B[j], apice, apice, new float[]{0, 1 - vt, 1, 1 - vt, 0.5F, 0, 0.5F, 0}));
        }
        if (!extras) {
            return;
        }
        int n = 3 + r.nextInt(3);
        for (int k = 0; k < n; k++) {
            double ang = r.nextDouble() * TAU;
            double d = radio * (0.7 + r.nextDouble() * 0.5);
            double ab = 0.3 + r.nextDouble() * 0.3;
            esquirla(out, r, x + Math.cos(ang) * d, z + Math.sin(ang) * d, alto * (0.35 + r.nextDouble() * 0.35),
                    radio * (0.4 + r.nextDouble() * 0.2), Math.cos(ang) * ab, Math.sin(ang) * ab, 5, false);
        }
        int m = 5 + r.nextInt(4);
        for (int k = 0; k < m; k++) {
            double ang = TAU * k / 6.0 + (r.nextDouble() - 0.5) * 0.6;
            double d = radio * (1.1 + r.nextDouble() * 0.8);
            double tam = radio * (0.28 + r.nextDouble() * 0.22);
            roca(out, r, x + Math.cos(ang) * d, tam * 0.4, z + Math.sin(ang) * d, tam, 1.0,
                    r.nextDouble() * 80 - 40, r.nextDouble() * 360, r.nextDouble() * 80 - 40);
        }
    }

    private static Vec3[] anillo(Random r, Vec3 base, Vec3 e, Vec3 a, Vec3 b, double largo, double t, double k,
                                 double radio, int lados, double giro) {
        Vec3[] out = new Vec3[lados];
        for (int i = 0; i < lados; i++) {
            double ang = giro + (i + (r.nextDouble() - 0.5) * 0.4) / lados * TAU;
            double rr = radio * k * (0.85 + r.nextDouble() * 0.27);
            out[i] = base.add(e.scale(largo * t)).add(a.scale(Math.cos(ang) * rr)).add(b.scale(Math.sin(ang) * rr));
        }
        return out;
    }

    // ------------------------------------------------------------------
    //  Rocas en bloque y pilares
    // ------------------------------------------------------------------

    /** Una roca: caja irregular de medio lado tam (y aplanada), girada (grados x, y, z). */
    static void roca(List<Cara> out, Random r, double x, double y, double z, double tam, double aplanar,
                     double gx, double gy, double gz) {
        double hx = tam * (0.75 + r.nextDouble() * 0.45);
        double hy = tam * (0.6 + r.nextDouble() * 0.4) * aplanar;
        double hz = tam * (0.75 + r.nextDouble() * 0.45);
        Vec3[] v = new Vec3[8];
        for (int i = 0; i < 8; i++) {
            double sx = (i & 1) != 0 ? 1 : -1;
            double sy = (i & 2) != 0 ? 1 : -1;
            double sz = (i & 4) != 0 ? 1 : -1;
            Vec3 q = new Vec3(sx * hx * (0.85 + r.nextDouble() * 0.25), sy * hy * (0.85 + r.nextDouble() * 0.25),
                    sz * hz * (0.85 + r.nextDouble() * 0.25));
            q = q.zRot((float) Math.toRadians(gz)).xRot((float) Math.toRadians(gx)).yRot((float) Math.toRadians(gy));
            v[i] = q.add(x, y, z);
        }
        int[][] caras = {{0, 4, 6, 2}, {1, 3, 7, 5}, {0, 1, 5, 4}, {2, 6, 7, 3}, {0, 2, 3, 1}, {4, 5, 7, 6}};
        for (int[] c : caras) {
            float u0 = r.nextFloat() * 0.5F;
            float v0 = r.nextFloat() * 0.5F;
            out.add(new Cara(v[c[0]], v[c[1]], v[c[2]], v[c[3]], new float[]{u0, v0 + 0.5F, u0 + 0.5F, v0 + 0.5F,
                    u0 + 0.5F, v0, u0, v0}));
        }
    }

    /** Las caras de una caja por sus esquinas (bit 0: x, bit 1: y, bit 2: z), con el primer lado en horizontal. */
    private static final int[][] CARAS_CAJA = {{0, 4, 6, 2}, {5, 1, 3, 7}, {1, 0, 2, 3}, {4, 5, 7, 6}, {2, 6, 7, 3}, {0, 1, 5, 4}};

    /**
     * Un bloque de roca de medio lado (hx, hy, hz) con las esquinas algo
     * movidas ('mover', en fraccion) y girado (grados x, y, z). La textura va
     * a 'densidad' pixeles por bloque (los estratos siempre en horizontal),
     * de una textura de texAncho x texAlto. Con 'tapa', la cara de arriba va
     * ahi entera (para la hierba).
     */
    static void bloque(List<Cara> out, @Nullable List<Cara> tapa, Random r, double x, double y,
                       double z, double hx, double hy, double hz, double mover, double gx, double gy, double gz,
                       float densidad, int texAncho, int texAlto) {
        Vec3[] v = new Vec3[8];
        for (int i = 0; i < 8; i++) {
            double sx = (i & 1) != 0 ? 1 : -1;
            double sy = (i & 2) != 0 ? 1 : -1;
            double sz = (i & 4) != 0 ? 1 : -1;
            Vec3 q = new Vec3(sx * hx * (1.0 + (r.nextDouble() - 0.5) * mover), sy * hy * (1.0 + (r.nextDouble() - 0.5) * mover),
                    sz * hz * (1.0 + (r.nextDouble() - 0.5) * mover));
            q = q.zRot((float) Math.toRadians(gz)).xRot((float) Math.toRadians(gx)).yRot((float) Math.toRadians(gy));
            v[i] = q.add(x, y, z);
        }
        double[][] lados = {{hz, hy}, {hz, hy}, {hx, hy}, {hx, hy}, {hz, hx}, {hx, hz}};
        for (int k = 0; k < 6; k++) {
            int[] c = CARAS_CAJA[k];
            if (k == 4 && tapa != null) {
                tapa.add(new Cara(v[c[0]], v[c[1]], v[c[2]], v[c[3]], new float[]{0, 1, 1, 1, 1, 0, 0, 0}));
                continue;
            }
            float du = Math.min(1.0F, (float) (2 * lados[k][0] * densidad / texAncho));
            float dv = Math.min(1.0F, (float) (2 * lados[k][1] * densidad / texAlto));
            float u0 = r.nextFloat() * (1.0F - du);
            float v0 = r.nextFloat() * (1.0F - dv);
            out.add(new Cara(v[c[0]], v[c[1]], v[c[2]], v[c[3]], new float[]{u0, v0 + dv, u0 + du, v0 + dv, u0 + du, v0, u0, v0}));
        }
    }

    /**
     * La hierba que cuelga por los cuatro lados de una tapa cuadrada de medio
     * lado m, desde la altura y hasta 'largo' mas abajo (cesped_borde.png, un
     * tramo cada dos bloques).
     */
    static void borde(List<Cara> out, double m, double y, double largo) {
        double e = m + 0.02;
        int n = Math.max(1, (int) Math.ceil(m));
        double abajo = y - largo;
        for (int lado = 0; lado < 4; lado++) {
            for (int i = 0; i < n; i++) {
                double t0 = -m + 2 * m * i / n;
                double t1 = -m + 2 * m * (i + 1) / n;
                float du = (float) Math.min(1.0, (t1 - t0) / 2.0);
                Vec3 a, b, c, d;
                switch (lado) {
                    case 0 -> {
                        a = new Vec3(t0, abajo, e);
                        b = new Vec3(t1, abajo, e);
                        c = new Vec3(t1, y, e);
                        d = new Vec3(t0, y, e);
                    }
                    case 1 -> {
                        a = new Vec3(-t0, abajo, -e);
                        b = new Vec3(-t1, abajo, -e);
                        c = new Vec3(-t1, y, -e);
                        d = new Vec3(-t0, y, -e);
                    }
                    case 2 -> {
                        a = new Vec3(e, abajo, -t0);
                        b = new Vec3(e, abajo, -t1);
                        c = new Vec3(e, y, -t1);
                        d = new Vec3(e, y, -t0);
                    }
                    default -> {
                        a = new Vec3(-e, abajo, t0);
                        b = new Vec3(-e, abajo, t1);
                        c = new Vec3(-e, y, t1);
                        d = new Vec3(-e, y, t0);
                    }
                }
                float u0 = (i % 2) * 0.5F * (1.0F - du) * 2.0F;
                out.add(new Cara(a, b, c, d, new float[]{u0, 1, u0 + du, 1, u0 + du, 0, u0, 0}));
            }
        }
    }

    /**
     * Un pincho de roca en bloques, como una estalagmita de Minecraft: tramos
     * rectos apilados que se estrechan hasta un taco en la punta, inclinado
     * 'inclina' grados hacia delante (+Z) y 'ladea' hacia el lado (+X).
     */
    static void pincho(List<Cara> out, Random r, double x, double z, double alto, double ancho, double inclina, double ladea) {
        Vec3 e = new Vec3(0, 1, 0).zRot((float) Math.toRadians(ladea)).xRot((float) Math.toRadians(-inclina));
        int n = Mth.clamp((int) Math.round(alto / Math.max(0.45, ancho * 0.75)), 3, 7);
        double paso = alto / e.y / n;
        Vec3 base = new Vec3(x, 0, z);
        double s = -0.35;
        for (int i = 0; i < n; i++) {
            double k = (double) i / n;
            double m = Math.max(0.09, ancho * 0.5 * Math.pow(1.0 - k, 0.8));
            double h = paso * (0.95 + r.nextDouble() * 0.15);
            Vec3 c = base.add(e.scale(s + h / 2));
            bloque(out, null, r, c.x, c.y, c.z, m * (0.9 + r.nextDouble() * 0.15), h / 2 * 1.04, m * (0.85 + r.nextDouble() * 0.2),
                    0.1, -inclina, (r.nextDouble() - 0.5) * 18, ladea, 12, 32, 64);
            s += h * 0.9;
        }
        double m = Math.max(0.07, ancho * 0.08);
        Vec3 c = base.add(e.scale(s + paso * 0.25));
        bloque(out, null, r, c.x, c.y, c.z, m, paso * 0.3, m, 0.1, -inclina, (r.nextDouble() - 0.5) * 18, ladea, 12, 32, 64);
    }

    /** Un pilar: bloques de roca apilados, cada uno algo torcido y mas estrecho, con la punta en esquirla. */
    static void pilar(List<Cara> out, Random r, double x, double z, double alto, double ancho) {
        double y = -0.4;
        int i = 0;
        while (y < alto - ancho * 0.6 && i < 12) {
            double w = ancho * (1.0 - 0.1 * i) * (0.92 + r.nextDouble() * 0.13);
            double h = w * (0.7 + r.nextDouble() * 0.3);
            double cx = x + (r.nextDouble() - 0.5) * 0.24 * ancho;
            double cz = z + (r.nextDouble() - 0.5) * 0.24 * ancho;
            roca(out, r, cx, y + h / 2, cz, w / 2, 1.0, r.nextDouble() * 14 - 7, r.nextDouble() * 90, r.nextDouble() * 14 - 7);
            y += h * 0.9;
            i++;
        }
        List<Cara> punta = new ArrayList<>();
        esquirla(punta, r, 0, 0, ancho * 1.2, ancho * 0.36, (r.nextDouble() - 0.5) * 0.4, (r.nextDouble() - 0.5) * 0.4, 5, false);
        Vec3 sube = new Vec3(x, y - 0.2, z);
        for (Cara c : punta) {
            out.add(new Cara(c.a().add(sube), c.b().add(sube), c.c().add(sube), c.d().add(sube), c.uv()));
        }
    }

    // ------------------------------------------------------------------
    //  Al buffer
    // ------------------------------------------------------------------

    static void emitir(VertexConsumer buf, PoseStack.Pose p, List<Cara> caras, int r, int g, int b, int a, int luz) {
        for (Cara c : caras) {
            Vec3 n = c.b().subtract(c.a()).cross(c.d().subtract(c.a()));
            if (n.lengthSqr() < 1.0E-9) {
                n = c.c().subtract(c.a()).cross(c.b().subtract(c.a())).scale(-1);
            }
            n = n.lengthSqr() < 1.0E-9 ? new Vec3(0, 1, 0) : n.normalize();
            float nx = (float) n.x;
            float ny = (float) n.y;
            float nz = (float) n.z;
            float[] uv = c.uv();
            AeralisDibujo.vertice(buf, p, c.a().x, c.a().y, c.a().z, uv[0], uv[1], r, g, b, a, luz, nx, ny, nz);
            AeralisDibujo.vertice(buf, p, c.b().x, c.b().y, c.b().z, uv[2], uv[3], r, g, b, a, luz, nx, ny, nz);
            AeralisDibujo.vertice(buf, p, c.c().x, c.c().y, c.c().z, uv[4], uv[5], r, g, b, a, luz, nx, ny, nz);
            AeralisDibujo.vertice(buf, p, c.d().x, c.d().y, c.d().z, uv[6], uv[7], r, g, b, a, luz, nx, ny, nz);
        }
    }

    /** Una caja recta (de x0,y0,z0 a x1,y1,z1) con la misma UV en cada lado. */
    static void caja(List<Cara> out, double x0, double y0, double z0, double x1, double y1, double z1, float[] uvLado,
                     float[] uvTapa) {
        Vec3 a = new Vec3(x0, y0, z0), b = new Vec3(x1, y0, z0), c = new Vec3(x1, y0, z1), d = new Vec3(x0, y0, z1);
        Vec3 e = new Vec3(x0, y1, z0), f = new Vec3(x1, y1, z0), g = new Vec3(x1, y1, z1), h = new Vec3(x0, y1, z1);
        out.add(new Cara(a, b, f, e, uvLado));
        out.add(new Cara(b, c, g, f, uvLado));
        out.add(new Cara(c, d, h, g, uvLado));
        out.add(new Cara(d, a, e, h, uvLado));
        out.add(new Cara(e, f, g, h, uvTapa));
        out.add(new Cara(d, c, b, a, uvTapa));
    }

    /** La UV de un rectangulo de la textura (u0, v0 arriba a la izquierda; u1, v1 abajo a la derecha), como Cara la quiere. */
    static float[] uv(float u0, float v0, float u1, float v1) {
        return new float[]{u0, v1, u1, v1, u1, v0, u0, v0};
    }
}
