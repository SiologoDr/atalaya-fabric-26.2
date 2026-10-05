package com.atalaya.client;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.world.phys.Vec3;

/**
 * Lo comun a lo que se dibuja a mano de Aeralis (cuchillas, tornados, rafagas
 * y nucleos): vertices y caras en el formato de las entidades.
 */
final class AeralisDibujo {

    static final int A_PLENA_LUZ = 0xF000F0;
    /** El color de cada fase (el filo de las alas y la barra): cian, anil, violeta y magenta. */
    static final int[] COLOR_FASE = {0x5FD2FF, 0x8F9BFF, 0xB98CFF, 0xFF6FDF};
    /** La tormenta oscura de cada fase (lo de dentro de los embudos). */
    static final int[] TORMENTA_FASE = {0x2C5480, 0x2C3488, 0x3A2678, 0x4A1448};

    static int fase(int f) {
        return COLOR_FASE[Math.clamp(f, 1, 4) - 1];
    }

    static int tormenta(int f) {
        return TORMENTA_FASE[Math.clamp(f, 1, 4) - 1];
    }

    /** El color c aclarado hacia el blanco (k de 0 a 1). */
    static int claro(int c, float k) {
        int r = (c >> 16) & 255, g = (c >> 8) & 255, b = c & 255;
        return ((int) (r + (255 - r) * k) << 16) | ((int) (g + (255 - g) * k) << 8) | (int) (b + (255 - b) * k);
    }

    static int r(int c) {
        return (c >> 16) & 255;
    }

    static int g(int c) {
        return (c >> 8) & 255;
    }

    static int b(int c) {
        return c & 255;
    }

    /**
     * Un rayo de a a b: una polilinea quebrada (la semilla decide el quiebro)
     * hecha de dos cintas cruzadas, para que se vea desde cualquier lado.
     */
    static void rayo(VertexConsumer buf, PoseStack.Pose p, Vec3 a, Vec3 b, Vec3 ojo, long semilla, int tramos, double sacude,
                     float ancho, int color, int alfa) {
        java.util.Random r = new java.util.Random(semilla);
        Vec3[] pts = new Vec3[tramos + 1];
        for (int i = 0; i <= tramos; i++) {
            Vec3 q = a.lerp(b, i / (double) tramos);
            if (i > 0 && i < tramos) {
                q = q.add((r.nextDouble() - 0.5) * sacude * 2, (r.nextDouble() - 0.5) * sacude * 2, (r.nextDouble() - 0.5) * sacude * 2);
            }
            pts[i] = q;
        }
        // Cada tramo es una cinta que da la cara a quien mira (ojo, en las mismas
        // coordenadas), por las dos caras: asi nunca se ve de canto.
        for (int i = 0; i < tramos; i++) {
            Vec3 q0 = pts[i], q1 = pts[i + 1];
            Vec3 lado = q1.subtract(q0).cross(ojo.subtract(q0.add(q1).scale(0.5)));
            lado = lado.lengthSqr() < 1.0E-8 ? new Vec3(ancho, 0, 0) : lado.normalize().scale(ancho);
            for (int cara = 0; cara < 2; cara++) {
                Vec3 l = cara == 0 ? lado : lado.reverse();
                vertice(buf, p, q0.x - l.x, q0.y - l.y, q0.z - l.z, 0.0F, 0.0F, r(color), g(color), b(color), alfa, A_PLENA_LUZ, 0, 1, 0);
                vertice(buf, p, q0.x + l.x, q0.y + l.y, q0.z + l.z, 1.0F, 0.0F, r(color), g(color), b(color), alfa, A_PLENA_LUZ, 0, 1, 0);
                vertice(buf, p, q1.x + l.x, q1.y + l.y, q1.z + l.z, 1.0F, 1.0F, r(color), g(color), b(color), alfa, A_PLENA_LUZ, 0, 1, 0);
                vertice(buf, p, q1.x - l.x, q1.y - l.y, q1.z - l.z, 0.0F, 1.0F, r(color), g(color), b(color), alfa, A_PLENA_LUZ, 0, 1, 0);
            }
        }
    }

    /** Un cuadrado tumbado de medio lado m, centrado en c, por las dos caras. */
    static void suelo(VertexConsumer buf, PoseStack.Pose p, double cx, double cy, double cz, float m, float giro,
                      int color, int alfa) {
        float co = (float) Math.cos(giro) * m, si = (float) Math.sin(giro) * m;
        double[][] q = {{-co + si, -si - co}, {co + si, si - co}, {co - si, si + co}, {-co - si, -si + co}};
        float[][] uv = {{0, 0}, {1, 0}, {1, 1}, {0, 1}};
        for (int k = 0; k < 4; k++) {
            vertice(buf, p, cx + q[k][0], cy, cz + q[k][1], uv[k][0], uv[k][1], r(color), g(color), b(color), alfa, A_PLENA_LUZ, 0, 1, 0);
        }
        for (int k = 3; k >= 0; k--) {
            vertice(buf, p, cx + q[k][0], cy, cz + q[k][1], uv[k][0], uv[k][1], r(color), g(color), b(color), alfa, A_PLENA_LUZ, 0, -1, 0);
        }
    }

    private AeralisDibujo() {
    }

    static void vertice(VertexConsumer buf, PoseStack.Pose p, double x, double y, double z, float u, float v,
                        int r, int g, int b, int a, int luz, float nx, float ny, float nz) {
        buf.addVertex(p, (float) x, (float) y, (float) z)
                .setColor(r, g, b, a)
                .setUv(u, v)
                .setOverlay(OverlayTexture.NO_OVERLAY)
                .setLight(luz)
                .setNormal(p, nx, ny, nz);
    }

    /** Un cuadrilatero (c + lado * su + alto * sv), con la textura entera. */
    static void cara(VertexConsumer buf, PoseStack.Pose p, Vec3 c, Vec3 lado, Vec3 alto, int r, int g, int b, int a, int luz) {
        Vec3 n = lado.cross(alto);
        n = n.lengthSqr() < 1.0E-6 ? new Vec3(0, 1, 0) : n.normalize();
        float nx = (float) n.x;
        float ny = (float) n.y;
        float nz = (float) n.z;
        Vec3 q0 = c.subtract(lado).subtract(alto);
        Vec3 q1 = c.add(lado).subtract(alto);
        Vec3 q2 = c.add(lado).add(alto);
        Vec3 q3 = c.subtract(lado).add(alto);
        vertice(buf, p, q0.x, q0.y, q0.z, 0.0F, 1.0F, r, g, b, a, luz, nx, ny, nz);
        vertice(buf, p, q1.x, q1.y, q1.z, 1.0F, 1.0F, r, g, b, a, luz, nx, ny, nz);
        vertice(buf, p, q2.x, q2.y, q2.z, 1.0F, 0.0F, r, g, b, a, luz, nx, ny, nz);
        vertice(buf, p, q3.x, q3.y, q3.z, 0.0F, 0.0F, r, g, b, a, luz, nx, ny, nz);
    }

    /** Un cubo centrado en el origen de lado 2*m, girado por la pila de poses, con la textura en cada cara. */
    static void cubo(VertexConsumer buf, PoseStack.Pose p, float m, int r, int g, int b, int a, int luz) {
        Vec3[] ejes = {new Vec3(m, 0, 0), new Vec3(0, m, 0), new Vec3(0, 0, m)};
        for (int k = 0; k < 3; k++) {
            Vec3 n = ejes[k];
            Vec3 e1 = ejes[(k + 1) % 3];
            Vec3 e2 = ejes[(k + 2) % 3];
            for (int s = -1; s <= 1; s += 2) {
                cara(buf, p, n.scale(s), s > 0 ? e1 : e2, s > 0 ? e2 : e1, r, g, b, a, luz);
            }
        }
    }
}
