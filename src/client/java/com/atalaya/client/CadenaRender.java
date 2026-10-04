package com.atalaya.client;

import com.atalaya.Atalaya;
import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import net.minecraft.client.renderer.SubmitNodeCollector;
import net.minecraft.client.renderer.rendertype.RenderType;
import net.minecraft.client.renderer.rendertype.RenderTypes;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.resources.Identifier;
import net.minecraft.world.phys.Vec3;

/**
 * Cadenas largas tendidas entre dos puntos: la de cada sello al pecho de
 * Nerea y la del gancho a su mano. Eslabones macizos, alternando canto y
 * frente como las cadenas que lleva en el cuerpo.

 */
public final class CadenaRender {


    private CadenaRender() {
    }

    /** Una cadena del grosor pedido (bloques) de "desde" a "hasta", relativos a la pila de poses. */
    public static void dibujar(PoseStack pose, SubmitNodeCollector colector, Vec3 desde, Vec3 hasta, int luz, float ancho) {
        eslabones(pose, colector, desde, hasta, luz, ancho * 1.35F, ancho, ancho * 0.36F, ancho * 1.05F);
    }

    private static final Identifier OXIDO = Identifier.fromNamespaceAndPath(Atalaya.MOD_ID,
            "textures/entity/nerea/gancho.png");
    private static final RenderType TIPO_ESLABON = RenderTypes.entityCutout(OXIDO);

    /**
     * Una cadena de eslabones de verdad: cajas planas alternas, una de canto y
     * otra de frente, como las cadenas que lleva Nerea en el cuerpo. Se ve
     * maciza desde cualquier lado, que con dos planos cruzados no pasa.
     *
     * @param largo  lo que mide un eslabon a lo largo (bloques)
     * @param ancho  lo ancho de un eslabon
     * @param grueso lo grueso del hierro
     * @param paso   distancia entre eslabones (menor que el largo: se solapan)
     */
    public static void eslabones(PoseStack pose, SubmitNodeCollector colector, Vec3 desde, Vec3 hasta, int luz,
                                 float largo, float ancho, float grueso, float paso) {
        Vec3 d = hasta.subtract(desde);
        double total = d.length();
        if (total < 0.05) {
            return;
        }
        Vec3 dir = d.scale(1.0 / total);
        Vec3 ref = Math.abs(dir.y) > 0.95 ? new Vec3(1, 0, 0) : new Vec3(0, 1, 0);
        Vec3 a = dir.cross(ref).normalize();
        Vec3 b = dir.cross(a).normalize();
        int n = Math.max(1, (int) Math.ceil((total - largo) / paso) + 1);
        colector.submitCustomGeometry(pose, TIPO_ESLABON, (p, buf) -> {
            for (int i = 0; i < n; i++) {
                double centro = Math.min(i * paso + largo / 2.0, total - largo / 2.0);
                Vec3 c = desde.add(dir.scale(centro));
                Vec3 lado = (i & 1) == 0 ? a : b;
                Vec3 canto = (i & 1) == 0 ? b : a;
                caja(buf, p, c, dir.scale(largo / 2.0), lado.scale(ancho / 2.0), canto.scale(grueso / 2.0), luz, i);
            }
        });
    }

    /** Una caja orientada: centro y medio-ejes. Las UV caen en el oxido de gancho.png. */
    private static void caja(VertexConsumer buf, PoseStack.Pose p, Vec3 c, Vec3 hx, Vec3 hy, Vec3 hz, int luz, int semilla) {
        Vec3[] ejes = {hx, hy, hz};
        float u0 = ((semilla * 5) % 24) / 32.0F;
        float u1 = u0 + 4 / 32.0F;
        float v0 = 0.0F;
        float v1 = 4 / 32.0F;
        for (int k = 0; k < 3; k++) {
            Vec3 n = ejes[k];
            Vec3 e1 = ejes[(k + 1) % 3];
            Vec3 e2 = ejes[(k + 2) % 3];
            for (int s = -1; s <= 1; s += 2) {
                Vec3 cara = c.add(n.scale(s));
                Vec3 nn = n.normalize().scale(s);
                Vec3[] q = {cara.add(e1).add(e2), cara.add(e1).subtract(e2), cara.subtract(e1).subtract(e2), cara.subtract(e1).add(e2)};
                float[][] uv = {{u1, v0}, {u1, v1}, {u0, v1}, {u0, v0}};
                for (int i = 0; i < 4; i++) {
                    buf.addVertex(p, (float) q[i].x, (float) q[i].y, (float) q[i].z)
                            .setColor(255, 255, 255, 255)
                            .setUv(uv[i][0], uv[i][1])
                            .setOverlay(OverlayTexture.NO_OVERLAY)
                            .setLight(luz)
                            .setNormal(p, (float) nn.x, (float) nn.y, (float) nn.z);
                }
            }
        }
    }
}
