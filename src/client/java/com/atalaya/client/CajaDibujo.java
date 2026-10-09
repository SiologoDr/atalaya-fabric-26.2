package com.atalaya.client;

import com.atalaya.Atalaya;
import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import net.minecraft.client.renderer.rendertype.RenderType;
import net.minecraft.client.renderer.rendertype.RenderTypes;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.resources.Identifier;
import net.minecraft.world.phys.Vec3;

/**
 * Cajas orientadas con la luz del mundo, para lo que se dibuja a mano de los
 * minijuegos de Nerea (la morena, el canon, la pila de balas, el corcho). La
 * textura es un gris con grano (nerea_minijuegos.py) y el color lo pone cada
 * caja con el tinte: asi una sola textura sirve para el bronce, la madera, el
 * hierro o la piel de la morena (DISENO.md, punto 7).
 */
final class CajaDibujo {

    static final RenderType SOLIDO = RenderTypes.entityCutout(
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "textures/entity/nerea/solido.png"));

    private CajaDibujo() {
    }

    /** Una caja: centro c y medios ejes hx, hy, hz (pueden ir girados), del color dado. */
    static void caja(VertexConsumer buf, PoseStack.Pose p, Vec3 c, Vec3 hx, Vec3 hy, Vec3 hz, int color, int luz) {
        Vec3[] ejes = {hx, hy, hz};
        for (int k = 0; k < 3; k++) {
            Vec3 n = ejes[k];
            Vec3 e1 = ejes[(k + 1) % 3];
            Vec3 e2 = ejes[(k + 2) % 3];
            for (int s = -1; s <= 1; s += 2) {
                Vec3 cara = c.add(n.scale(s));
                Vec3 nn = n.lengthSqr() < 1.0E-9 ? new Vec3(0, 1, 0) : n.normalize().scale(s);
                // Las caras de arriba algo mas claras y las de abajo mas oscuras: se lee el volumen.
                float k2 = (float) (0.82 + 0.18 * nn.y);
                int col = escalar(color, k2);
                Vec3 a = s > 0 ? e1 : e2;
                Vec3 b = s > 0 ? e2 : e1;
                vertice(buf, p, cara.subtract(a).subtract(b), 0, 0, col, luz, nn);
                vertice(buf, p, cara.add(a).subtract(b), 1, 0, col, luz, nn);
                vertice(buf, p, cara.add(a).add(b), 1, 1, col, luz, nn);
                vertice(buf, p, cara.subtract(a).add(b), 0, 1, col, luz, nn);
            }
        }
    }

    /** Una caja alineada con los ejes, de medio tamano (ax, ay, az). */
    static void caja(VertexConsumer buf, PoseStack.Pose p, Vec3 c, double ax, double ay, double az, int color, int luz) {
        caja(buf, p, c, new Vec3(ax, 0, 0), new Vec3(0, ay, 0), new Vec3(0, 0, az), color, luz);
    }

    private static void vertice(VertexConsumer buf, PoseStack.Pose p, Vec3 q, float u, float v, int color, int luz, Vec3 n) {
        buf.addVertex(p, (float) q.x, (float) q.y, (float) q.z)
                .setColor((color >> 16) & 255, (color >> 8) & 255, color & 255, 255)
                .setUv(u, v)
                .setOverlay(OverlayTexture.NO_OVERLAY)
                .setLight(luz)
                .setNormal(p, (float) n.x, (float) n.y, (float) n.z);
    }

    static int escalar(int rgb, float k) {
        int r = Math.min(255, (int) (((rgb >> 16) & 255) * k));
        int g = Math.min(255, (int) (((rgb >> 8) & 255) * k));
        int b = Math.min(255, (int) ((rgb & 255) * k));
        return (r << 16) | (g << 8) | b;
    }

    /** Gira un vector alrededor del eje vertical (grados, como el rumbo de las entidades). */
    static Vec3 rumbo(Vec3 v, float grados) {
        return v.yRot(-grados * (float) (Math.PI / 180.0));
    }
}
