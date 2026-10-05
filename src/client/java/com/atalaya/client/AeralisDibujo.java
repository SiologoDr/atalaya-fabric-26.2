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
