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
 * Una bala de canon a lo Minecraft (Juan: primero "mas redondas, mas reales";
 * luego, al verlas lisas, "son muy redondas para lo que es Minecraft"): una
 * bola de pixeles, ocho de lado, hecha de tres cajas cruzadas (8x6x6, 6x8x6 y
 * 6x6x8), como se hacen las cosas redondas en el juego. Cada cara lleva su
 * trozo de bala.png (nerea_minijuegos.py) a un texel por pixel, asi que todas
 * tienen el mismo grano. La usan la pila, el canon cargado, la bala en vuelo y
 * la que lleva en brazos el cargador.
 */
public final class BalaDibujo {

    public static final RenderType HIERRO = RenderTypes.entityCutout(
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "textures/entity/nerea/bala.png"));

    /** Las tres cajas, en pixeles de la bola (medio lado por eje). */
    private static final int[][] CAJAS = {{4, 3, 3}, {3, 4, 3}, {3, 3, 4}};

    private BalaDibujo() {
    }

    /** Una bala de "radio" r (medio lado, en bloques) en c, girada "giro" sobre la vertical y "vuelta" sobre el lado. */
    public static void bola(VertexConsumer buf, PoseStack.Pose p, Vec3 c, double r, float giro, float vuelta, int luz) {
        double px = r / 4.0;
        Vec3 ex = new Vec3(1, 0, 0).xRot(vuelta).yRot(giro);
        Vec3 ey = new Vec3(0, 1, 0).xRot(vuelta).yRot(giro);
        Vec3 ez = new Vec3(0, 0, 1).xRot(vuelta).yRot(giro);
        for (int[] caja : CAJAS) {
            Vec3 hx = ex.scale(caja[0] * px);
            Vec3 hy = ey.scale(caja[1] * px);
            Vec3 hz = ez.scale(caja[2] * px);
            // Cada cara: su trozo de textura, del tamano de la cara en pixeles y centrado.
            cara(buf, p, c.add(hx), hz, hy, ex, caja[2], caja[1], luz);
            cara(buf, p, c.subtract(hx), hz, hy, ex.scale(-1), caja[2], caja[1], luz);
            cara(buf, p, c.add(hy), hx, hz, ey, caja[0], caja[2], luz);
            cara(buf, p, c.subtract(hy), hx, hz, ey.scale(-1), caja[0], caja[2], luz);
            cara(buf, p, c.add(hz), hx, hy, ez, caja[0], caja[1], luz);
            cara(buf, p, c.subtract(hz), hx, hy, ez.scale(-1), caja[0], caja[1], luz);
        }
    }

    private static void cara(VertexConsumer buf, PoseStack.Pose p, Vec3 c, Vec3 eu, Vec3 ev, Vec3 n, int mu, int mv, int luz) {
        float u0 = (8 - mu) / 16.0F;
        float u1 = (8 + mu) / 16.0F;
        float v0 = (8 - mv) / 16.0F;
        float v1 = (8 + mv) / 16.0F;
        if (eu.cross(ev).dot(n) < 0) {
            eu = eu.scale(-1);
        }
        // Arriba algo mas claro y abajo mas oscuro, como el resto de cajas del mod.
        int k = (int) (255 * (0.84 + 0.16 * n.y));
        vertice(buf, p, c.subtract(eu).subtract(ev), u0, v1, k, luz, n);
        vertice(buf, p, c.add(eu).subtract(ev), u1, v1, k, luz, n);
        vertice(buf, p, c.add(eu).add(ev), u1, v0, k, luz, n);
        vertice(buf, p, c.subtract(eu).add(ev), u0, v0, k, luz, n);
    }

    private static void vertice(VertexConsumer buf, PoseStack.Pose p, Vec3 q, float u, float v, int k, int luz, Vec3 n) {
        buf.addVertex(p, (float) q.x, (float) q.y, (float) q.z)
                .setColor(k, k, k, 255)
                .setUv(u, v)
                .setOverlay(OverlayTexture.NO_OVERLAY)
                .setLight(luz)
                .setNormal(p, (float) n.x, (float) n.y, (float) n.z);
    }
}
