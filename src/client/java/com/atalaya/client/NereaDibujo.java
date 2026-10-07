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
 * Lo comun a lo que se dibuja a mano de Nerea desde el remake (las paredes de
 * agua, los remolinos, los geiseres, los aros de espuma y los chorros de la
 * Mirada): las texturas de nerea_mejoras_extras.py y caras en el formato de
 * las entidades.
 *
 * Todo va con entityTranslucent, que NO recorta la cara de atras: cada cara se
 * pinta una sola vez y se ve por los dos lados, con la normal hacia arriba (el
 * sombreado no la apaga). Se probo en el juego: entityTranslucentEmissive SI la
 * recorta (los aros y el paso de la Marea se veian grises o no se veian), y
 * pintar dos caras en entityTranslucent hacia que se pelearan entre ellas (la
 * pared de la Marea salia a cuadros).
 */
final class NereaDibujo {

    static final int A_PLENA_LUZ = 0xF000F0;
    /** El color de la maldicion en cada fase (ojos, chorro de la Mirada): cian, violeta, magenta y rojo. */
    static final int[] COLOR_FASE = {0x3FE0FF, 0x9A6BFF, 0xD43CFF, 0xFF2050};
    /** El verde abismo de la Furia de las Mareas. */
    static final int FURIA = 0x20F0B0;
    /** Donde cae el aro en espuma_aro.png: a 58 de los 64 pixeles del medio lado. */
    static final float ARO_EN_TEXTURA = 58.0F / 64.0F;

    static final RenderType AGUA = translucido("ola");
    static final RenderType FLUJO = translucido("ola_flujo");
    static final RenderType ESTELA = translucido("estela");
    static final RenderType REMOLINO = translucido("remolino");
    static final RenderType COLUMNA = translucido("columna");
    static final RenderType ARO = brillante("espuma_aro");
    static final RenderType BURBUJA_AIRE = translucido("burbuja_aire");
    static final RenderType CHORRO = brillante("rayo_agua");
    static final RenderType ARO_OJO = brillante("aro_ojo");
    static final RenderType SENDERO = brillante("sendero");
    static final RenderType AVISO_CALLE = brillante("aviso_calle");
    static final RenderType CORAZON = brillante("corazon_burbuja");
    static final RenderType[] GRIETAS = {translucido("grieta_ojo_1"), translucido("grieta_ojo_2"),
            translucido("grieta_ojo_3"), translucido("grieta_ojo_4")};

    private NereaDibujo() {
    }

    private static Identifier tex(String nombre) {
        return Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "textures/entity/nerea/" + nombre + ".png");
    }

    private static RenderType translucido(String nombre) {
        return RenderTypes.entityTranslucent(tex(nombre));
    }

    /** Lo que brilla: los mismos (pintado a plena luz), sin la cara de atras recortada. */
    private static RenderType brillante(String nombre) {
        return RenderTypes.entityTranslucent(tex(nombre));
    }

    static int fase(int f) {
        return COLOR_FASE[Math.clamp(f, 1, 4) - 1];
    }

    /** El color c aclarado hacia el blanco (k de 0 a 1). */
    static int claro(int c, float k) {
        int r = (c >> 16) & 255, g = (c >> 8) & 255, b = c & 255;
        return ((int) (r + (255 - r) * k) << 16) | ((int) (g + (255 - g) * k) << 8) | (int) (b + (255 - b) * k);
    }

    static void vertice(VertexConsumer buf, PoseStack.Pose p, double x, double y, double z, float u, float v,
                        int color, int alfa, float nx, float ny, float nz) {
        buf.addVertex(p, (float) x, (float) y, (float) z)
                .setColor((color >> 16) & 255, (color >> 8) & 255, color & 255, Math.clamp(alfa, 0, 255))
                .setUv(u, v)
                .setOverlay(OverlayTexture.NO_OVERLAY)
                .setLight(A_PLENA_LUZ)
                .setNormal(p, nx, ny, nz);
    }

    /** Un cuadrado tumbado de medio lado m, centrado en c y girado (la textura entera). */
    static void suelo(VertexConsumer buf, PoseStack.Pose p, double cx, double cy, double cz, float m, float giro,
                      int color, int alfa) {
        double co = Math.cos(giro) * m, si = Math.sin(giro) * m;
        double[][] q = {{-co + si, -si - co}, {co + si, si - co}, {co - si, si + co}, {-co - si, -si + co}};
        float[][] uv = {{0, 0}, {1, 0}, {1, 1}, {0, 1}};
        for (int k = 3; k >= 0; k--) {
            vertice(buf, p, cx + q[k][0], cy, cz + q[k][1], uv[k][0], uv[k][1], color, alfa, 0, 1, 0);
        }
    }

    /** Un cuadrado de cara a quien mira (ojo, en las mismas coordenadas), de medio lado m, girado en su plano. */
    static void cartel(VertexConsumer buf, PoseStack.Pose p, Vec3 c, Vec3 ojo, float m, float giro, int color, int alfa) {
        Vec3 haciaOjo = ojo.subtract(c);
        if (haciaOjo.lengthSqr() < 1.0E-6) {
            return;
        }
        Vec3 d = haciaOjo.normalize();
        Vec3 der = d.cross(new Vec3(0, 1, 0));
        der = der.lengthSqr() < 1.0E-6 ? new Vec3(1, 0, 0) : der.normalize();
        Vec3 arr = der.cross(d).normalize();
        double co = Math.cos(giro), si = Math.sin(giro);
        Vec3 a = der.scale(co * m).add(arr.scale(si * m));
        Vec3 b = der.scale(-si * m).add(arr.scale(co * m));
        Vec3[] q = {c.subtract(a).subtract(b), c.add(a).subtract(b), c.add(a).add(b), c.subtract(a).add(b)};
        float[][] uv = {{0, 1}, {1, 1}, {1, 0}, {0, 0}};
        for (int k = 0; k < 4; k++) {
            vertice(buf, p, q[k].x, q[k].y, q[k].z, uv[k][0], uv[k][1], color, alfa, 0, 1, 0);
        }
    }

    /**
     * Una cinta de a a b de cara a quien mira, de medio ancho w, con la textura
     * a lo largo (v de v0 a v1): nunca se ve de canto.
     */
    static void cinta(VertexConsumer buf, PoseStack.Pose p, Vec3 a, Vec3 b, Vec3 ojo, float w, float v0, float v1,
                      int color, int alfa) {
        Vec3 medio = a.add(b).scale(0.5);
        Vec3 lado = b.subtract(a).cross(ojo.subtract(medio));
        if (lado.lengthSqr() < 1.0E-8) {
            return;
        }
        lado = lado.normalize().scale(w);
        vertice(buf, p, a.x - lado.x, a.y - lado.y, a.z - lado.z, 0.0F, v0, color, alfa, 0, 1, 0);
        vertice(buf, p, a.x + lado.x, a.y + lado.y, a.z + lado.z, 1.0F, v0, color, alfa, 0, 1, 0);
        vertice(buf, p, b.x + lado.x, b.y + lado.y, b.z + lado.z, 1.0F, v1, color, alfa, 0, 1, 0);
        vertice(buf, p, b.x - lado.x, b.y - lado.y, b.z - lado.z, 0.0F, v1, color, alfa, 0, 1, 0);
    }

    /**
     * Una tira tumbada en el suelo de a a b (a la altura de a), de medio ancho w,
     * con la textura de lado a lado (u) y a lo largo (v de v0 a v1).
     */
    static void tira(VertexConsumer buf, PoseStack.Pose p, Vec3 a, Vec3 b, float w, float v0, float v1, int color, int alfa) {
        Vec3 d = new Vec3(b.x - a.x, 0, b.z - a.z);
        if (d.lengthSqr() < 1.0E-6) {
            return;
        }
        Vec3 l = new Vec3(-d.z, 0, d.x).normalize().scale(w);
        double y = a.y;
        vertice(buf, p, a.x - l.x, y, a.z - l.z, 0.0F, v0, color, alfa, 0, 1, 0);
        vertice(buf, p, a.x + l.x, y, a.z + l.z, 1.0F, v0, color, alfa, 0, 1, 0);
        vertice(buf, p, b.x + l.x, y, b.z + l.z, 1.0F, v1, color, alfa, 0, 1, 0);
        vertice(buf, p, b.x - l.x, y, b.z - l.z, 0.0F, v1, color, alfa, 0, 1, 0);
    }

    /**
     * Un cuadrilatero (q0..q3 en orden) con su UV. La normal va hacia arriba:
     * son agua y espuma, y asi el sombreado no las apaga se mire por donde se mire.
     */
    static void cuadro(VertexConsumer buf, PoseStack.Pose p, Vec3 q0, Vec3 q1, Vec3 q2, Vec3 q3,
                       float u0, float u1, float v0, float v1, int color, int alfa0, int alfa1) {
        vertice(buf, p, q0.x, q0.y, q0.z, u0, v0, color, alfa0, 0, 1, 0);
        vertice(buf, p, q1.x, q1.y, q1.z, u1, v0, color, alfa0, 0, 1, 0);
        vertice(buf, p, q2.x, q2.y, q2.z, u1, v1, color, alfa1, 0, 1, 0);
        vertice(buf, p, q3.x, q3.y, q3.z, u0, v1, color, alfa1, 0, 1, 0);
    }
}
