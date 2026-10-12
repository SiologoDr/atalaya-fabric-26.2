package com.atalaya.client;

import com.atalaya.Atalaya;
import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import net.minecraft.client.renderer.rendertype.RenderType;
import net.minecraft.client.renderer.rendertype.RenderTypes;
import net.minecraft.client.renderer.state.level.CameraRenderState;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.resources.Identifier;
import net.minecraft.util.Mth;
import net.minecraft.world.phys.Vec3;
import org.joml.Vector3f;

/**
 * Las piezas con que se pintan los efectos grandes de los mini jefes (sus
 * texturas, de minijefes_extras.py, en textures/entity/minijefes/efectos):
 * destellos de cara a la camara, cintas (las estelas de las armas), anillos
 * tumbados, bandas en anillo (olas, viento, fuego), conos (el ciclon, la columna
 * de fuego), cristales de jade y el muro del tsunami. Todo a plena luz y con
 * alfa, en el espacio de la entidad (el origen en sus pies).
 */
public final class MiniJefeDibujo {

    private static final int LUZ = 0xF000F0;

    private MiniJefeDibujo() {
    }

    public static Identifier tex(String nombre) {
        return Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "textures/entity/minijefes/efectos/" + nombre + ".png");
    }

    /** Un tipo de pintado con luz propia y transparencia para la textura de efecto "nombre". */
    public static RenderType luz(String nombre) {
        return RenderTypes.entityTranslucentEmissive(tex(nombre));
    }

    public static void vertice(VertexConsumer buf, PoseStack.Pose p, float x, float y, float z, float u, float v, int color) {
        buf.addVertex(p, x, y, z).setColor(color).setUv(u, v).setOverlay(OverlayTexture.NO_OVERLAY).setLight(LUZ)
                .setNormal(p, 0.0F, 1.0F, 0.0F);
    }

    /** Un cuadrilatero por las dos caras. */
    public static void cuadro(VertexConsumer buf, PoseStack.Pose p, Vec3 a, Vec3 b, Vec3 c, Vec3 d, float u0, float v0, float u1,
                              float v1, int color) {
        cuadro(buf, p, a, b, c, d, u0, v0, u1, v1, color, color);
    }

    /** Un cuadrilatero por las dos caras, con un color abajo (a, b) y otro arriba (c, d). */
    public static void cuadro(VertexConsumer buf, PoseStack.Pose p, Vec3 a, Vec3 b, Vec3 c, Vec3 d, float u0, float v0, float u1,
                              float v1, int colorAb, int colorAr) {
        vertice(buf, p, (float) a.x, (float) a.y, (float) a.z, u0, v1, colorAb);
        vertice(buf, p, (float) b.x, (float) b.y, (float) b.z, u1, v1, colorAb);
        vertice(buf, p, (float) c.x, (float) c.y, (float) c.z, u1, v0, colorAr);
        vertice(buf, p, (float) d.x, (float) d.y, (float) d.z, u0, v0, colorAr);
        vertice(buf, p, (float) d.x, (float) d.y, (float) d.z, u0, v0, colorAr);
        vertice(buf, p, (float) c.x, (float) c.y, (float) c.z, u1, v0, colorAr);
        vertice(buf, p, (float) b.x, (float) b.y, (float) b.z, u1, v1, colorAb);
        vertice(buf, p, (float) a.x, (float) a.y, (float) a.z, u0, v1, colorAb);
    }

    /** Un destello de cara a la camara, centrado en c, de medio lado "r" y girado "giro" radianes. */
    public static void destello(VertexConsumer buf, PoseStack.Pose p, CameraRenderState cam, Vec3 c, float r, float giro, int color) {
        Vector3f der = new Vector3f(1, 0, 0).rotate(cam.orientation);
        Vector3f arr = new Vector3f(0, 1, 0).rotate(cam.orientation);
        float cg = Mth.cos(giro);
        float sg = Mth.sin(giro);
        Vec3 x = new Vec3(der.x * cg + arr.x * sg, der.y * cg + arr.y * sg, der.z * cg + arr.z * sg).scale(r);
        Vec3 y = new Vec3(arr.x * cg - der.x * sg, arr.y * cg - der.y * sg, arr.z * cg - der.z * sg).scale(r);
        cuadro(buf, p, c.subtract(x).subtract(y), c.add(x).subtract(y), c.add(x).add(y), c.subtract(x).add(y), 0, 0, 1, 1, color);
    }

    /** Un cuadro tumbado (de medio lado r) en c, girado "giro" radianes. */
    public static void tumbado(VertexConsumer buf, PoseStack.Pose p, Vec3 c, float r, float giro, int color) {
        float cg = Mth.cos(giro) * r;
        float sg = Mth.sin(giro) * r;
        Vec3 a = c.add(-cg + sg, 0, -sg - cg);
        Vec3 b = c.add(cg + sg, 0, sg - cg);
        Vec3 d = c.add(-cg - sg, 0, -sg + cg);
        Vec3 e = c.add(cg - sg, 0, sg + cg);
        cuadro(buf, p, a, b, e, d, 0, 0, 1, 1, color);
    }

    /**
     * Una banda vertical en anillo alrededor de c: de radio r0 abajo (y0) a r1
     * arriba (y1), en n tramos, la textura repetida "vueltas" veces y corrida
     * "corre" (u); colores abajo y arriba (con su alfa). Sirve para olas,
     * anillos de viento y de fuego, el ciclon y la columna de llamas.
     */
    public static void banda(VertexConsumer buf, PoseStack.Pose p, Vec3 c, float r0, float r1, float y0, float y1, int n,
                             float vueltas, float corre, float v0, float v1, int colorAb, int colorAr) {
        for (int i = 0; i < n; i++) {
            float a0 = Mth.TWO_PI * i / n;
            float a1 = Mth.TWO_PI * (i + 1) / n;
            float c0 = Mth.cos(a0);
            float s0 = Mth.sin(a0);
            float c1 = Mth.cos(a1);
            float s1 = Mth.sin(a1);
            float u0 = corre + vueltas * i / n;
            float u1 = corre + vueltas * (i + 1) / n;
            cuadro(buf, p, c.add(c0 * r0, y0, s0 * r0), c.add(c1 * r0, y0, s1 * r0), c.add(c1 * r1, y1, s1 * r1),
                    c.add(c0 * r1, y1, s0 * r1), u0, v0, u1, v1, colorAb, colorAr);
        }
    }

    /** Una corona tumbada entre rDentro y rFuera, en c (la textura en u alrededor, en v de dentro a fuera). */
    public static void corona(VertexConsumer buf, PoseStack.Pose p, Vec3 c, float rDentro, float rFuera, int n, float vueltas,
                              float corre, int color) {
        for (int i = 0; i < n; i++) {
            float a0 = Mth.TWO_PI * i / n;
            float a1 = Mth.TWO_PI * (i + 1) / n;
            float c0 = Mth.cos(a0);
            float s0 = Mth.sin(a0);
            float c1 = Mth.cos(a1);
            float s1 = Mth.sin(a1);
            float u0 = corre + vueltas * i / n;
            float u1 = corre + vueltas * (i + 1) / n;
            cuadro(buf, p, c.add(c0 * rDentro, 0, s0 * rDentro), c.add(c1 * rDentro, 0, s1 * rDentro),
                    c.add(c1 * rFuera, 0, s1 * rFuera), c.add(c0 * rFuera, 0, s0 * rFuera), u0, 0, u1, 1, color);
        }
    }

    /**
     * Una cinta entre pares de puntos (a[i], b[i]): la estela de un arma. La
     * textura va en u a lo largo (0 la cola, 1 la cabeza) y en v de la base a la
     * punta; el alfa crece de la cola a la cabeza.
     */
    public static void cinta(VertexConsumer buf, PoseStack.Pose p, Vec3[] a, Vec3[] b, int n, int rgb, float alfa) {
        for (int i = 0; i + 1 < n; i++) {
            float k0 = i / (float) (n - 1);
            float k1 = (i + 1) / (float) (n - 1);
            int c0 = color(rgb, alfa * k0 * k0);
            int c1 = color(rgb, alfa * k1 * k1);
            vertice(buf, p, (float) a[i].x, (float) a[i].y, (float) a[i].z, k0, 1, c0);
            vertice(buf, p, (float) a[i + 1].x, (float) a[i + 1].y, (float) a[i + 1].z, k1, 1, c1);
            vertice(buf, p, (float) b[i + 1].x, (float) b[i + 1].y, (float) b[i + 1].z, k1, 0, c1);
            vertice(buf, p, (float) b[i].x, (float) b[i].y, (float) b[i].z, k0, 0, c0);
            vertice(buf, p, (float) b[i].x, (float) b[i].y, (float) b[i].z, k0, 0, c0);
            vertice(buf, p, (float) b[i + 1].x, (float) b[i + 1].y, (float) b[i + 1].z, k1, 0, c1);
            vertice(buf, p, (float) a[i + 1].x, (float) a[i + 1].y, (float) a[i + 1].z, k1, 1, c1);
            vertice(buf, p, (float) a[i].x, (float) a[i].y, (float) a[i].z, k0, 1, c0);
        }
    }

    /**
     * Un cristal de jade: un prisma de "lados" caras de radio r que sale de la
     * base b en la direccion d (unitaria) "alto" bloques y acaba en punta.
     */
    public static void cristal(VertexConsumer buf, PoseStack.Pose p, Vec3 b, Vec3 d, float r, float alto, int lados, float giro,
                               int color) {
        Vec3 e1 = Math.abs(d.y) < 0.9 ? d.cross(new Vec3(0, 1, 0)).normalize() : d.cross(new Vec3(1, 0, 0)).normalize();
        Vec3 e2 = d.cross(e1).normalize();
        Vec3 cuello = b.add(d.scale(alto * 0.72));
        Vec3 punta = b.add(d.scale(alto));
        for (int i = 0; i < lados; i++) {
            float a0 = giro + Mth.TWO_PI * i / lados;
            float a1 = giro + Mth.TWO_PI * (i + 1) / lados;
            Vec3 o0 = e1.scale(Mth.cos(a0) * r).add(e2.scale(Mth.sin(a0) * r));
            Vec3 o1 = e1.scale(Mth.cos(a1) * r).add(e2.scale(Mth.sin(a1) * r));
            float u0 = i / (float) lados;
            float u1 = (i + 1) / (float) lados;
            int oscuro = escalar(color, 0.62F + 0.38F * Math.abs(Mth.cos(a0 * 0.5F + 0.6F)));
            cuadro(buf, p, b.add(o0), b.add(o1), cuello.add(o1.scale(0.92)), cuello.add(o0.scale(0.92)), u0, 0.25F, u1, 1.0F,
                    oscuro, color);
            // La punta: un triangulo (cuadro con dos vertices iguales).
            cuadro(buf, p, cuello.add(o0.scale(0.92)), cuello.add(o1.scale(0.92)), punta, punta, u0, 0.0F, u1, 0.25F, color, color);
        }
    }

    /** Una lengua de muro (el tsunami): una superficie de "an" bloques de ancho, con su perfil. */
    public interface Perfil {
        /** Para cada altura relativa (0 abajo, 1 la cresta), cuanto se adelanta (bloques). */
        float adelanta(float v);
    }

    /**
     * Un muro curvo: centrado en c, de ancho "ancho" (a lo largo de "lado"), de
     * alto "alto" (hacia arriba), adelantado segun el perfil hacia "frente", en
     * na x nv tramos. La textura en u a lo ancho (repetida "repite" veces y corrida)
     * y en v de la cresta (0) a la base (1).
     */
    public static void muro(VertexConsumer buf, PoseStack.Pose p, Vec3 c, Vec3 frente, Vec3 lado, float ancho, float alto,
                            Perfil perfil, int na, int nv, float repite, float corre, int colorAb, int colorAr) {
        for (int i = 0; i < na; i++) {
            float x0 = -ancho / 2 + ancho * i / na;
            float x1 = -ancho / 2 + ancho * (i + 1) / na;
            // Los extremos bajan: la ola se abre por los lados.
            float h0 = alto * (1.0F - (float) Math.pow(Math.abs(x0) / (ancho / 2), 4) * 0.7F);
            float h1 = alto * (1.0F - (float) Math.pow(Math.abs(x1) / (ancho / 2), 4) * 0.7F);
            for (int j = 0; j < nv; j++) {
                float v0 = j / (float) nv;
                float v1 = (j + 1) / (float) nv;
                Vec3 a = c.add(lado.scale(x0)).add(frente.scale(perfil.adelanta(v0) * h0 / alto)).add(0, h0 * v0, 0);
                Vec3 b = c.add(lado.scale(x1)).add(frente.scale(perfil.adelanta(v0) * h1 / alto)).add(0, h1 * v0, 0);
                Vec3 d = c.add(lado.scale(x0)).add(frente.scale(perfil.adelanta(v1) * h0 / alto)).add(0, h0 * v1, 0);
                Vec3 e = c.add(lado.scale(x1)).add(frente.scale(perfil.adelanta(v1) * h1 / alto)).add(0, h1 * v1, 0);
                int cab = mezcla(colorAb, colorAr, v0);
                int car = mezcla(colorAb, colorAr, v1);
                float u0 = corre + repite * i / na;
                float u1 = corre + repite * (i + 1) / na;
                cuadro(buf, p, a, b, e, d, u0, 1.0F - v1, u1, 1.0F - v0, cab, car);
            }
        }
    }

    // ------------------------------------------------------------------
    //  Colores
    // ------------------------------------------------------------------

    public static int color(int rgb, float alfa) {
        return (Math.round(Mth.clamp(alfa, 0.0F, 1.0F) * 255) << 24) | (rgb & 0xFFFFFF);
    }

    public static int escalar(int argb, float k) {
        int r = Math.min(255, (int) (((argb >> 16) & 255) * k));
        int g = Math.min(255, (int) (((argb >> 8) & 255) * k));
        int b = Math.min(255, (int) ((argb & 255) * k));
        return (argb & 0xFF000000) | (r << 16) | (g << 8) | b;
    }

    public static int mezcla(int a, int b, float k) {
        int aa = (a >>> 24) & 255;
        int ab = (b >>> 24) & 255;
        int r = Math.round(((a >> 16) & 255) * (1 - k) + ((b >> 16) & 255) * k);
        int g = Math.round(((a >> 8) & 255) * (1 - k) + ((b >> 8) & 255) * k);
        int bl = Math.round((a & 255) * (1 - k) + (b & 255) * k);
        int al = Math.round(aa * (1 - k) + ab * k);
        return (al << 24) | (r << 16) | (g << 8) | bl;
    }

    /** De 0 a 1 entre t0 y t1, con subida suave. */
    public static float tramo(float t, float t0, float t1) {
        float k = Mth.clamp((t - t0) / Math.max(1.0E-3F, t1 - t0), 0.0F, 1.0F);
        return k * k * (3 - 2 * k);
    }

    /** Un punto del cuerpo (bloques: izquierda, alto, frente) con el rumbo r, respecto a los pies. */
    public static Vec3 cuerpo(float x, float y, float z, float rumbo) {
        float b = rumbo * Mth.DEG_TO_RAD;
        float c = Mth.cos(b);
        float s = Mth.sin(b);
        return new Vec3(x * c - z * s, y, x * s + z * c);
    }

    /** Un punto de una tabla de trazo (fila k, desde "desde": 0 la base, 3 la punta), con el rumbo r. */
    public static Vec3 trazo(float[][] tabla, float k, int desde, float rumbo) {
        int n = tabla.length - 1;
        k = Mth.clamp(k, 0, n);
        int i = Math.min((int) k, n - 1);
        float f = k - i;
        float x = Mth.lerp(f, tabla[i][desde], tabla[i + 1][desde]);
        float y = Mth.lerp(f, tabla[i][desde + 1], tabla[i + 1][desde + 1]);
        float z = Mth.lerp(f, tabla[i][desde + 2], tabla[i + 1][desde + 2]);
        return cuerpo(x, y, z, rumbo);
    }

    /**
     * La estela de un arma: la cinta entre la base y la punta de los ultimos
     * "largo" ticks de la tabla, solo donde la punta va deprisa (mas de "minimo"
     * bloques por tick).
     */
    public static void estela(VertexConsumer buf, PoseStack.Pose p, float[][] tabla, float t, float largo, float minimo,
                              float rumbo, int rgb, float alfa) {
        int n = 10;
        Vec3[] a = new Vec3[n];
        Vec3[] b = new Vec3[n];
        float rapidez = 0;
        for (int i = 0; i < n; i++) {
            float k = t - largo + largo * i / (n - 1);
            a[i] = trazo(tabla, k, 0, rumbo);
            b[i] = trazo(tabla, k, 3, rumbo);
            if (i > 0) {
                rapidez = Math.max(rapidez, (float) b[i].distanceTo(b[i - 1]) * (n - 1) / largo);
            }
        }
        float k = Mth.clamp((rapidez - minimo) / minimo, 0.0F, 1.0F);
        if (k > 0.01F) {
            cinta(buf, p, a, b, n, rgb, alfa * k);
        }
    }
}
