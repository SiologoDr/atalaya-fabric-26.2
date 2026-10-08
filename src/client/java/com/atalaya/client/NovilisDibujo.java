package com.atalaya.client;

import com.atalaya.Atalaya;
import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import net.minecraft.client.renderer.SubmitNodeCollector;
import net.minecraft.client.renderer.rendertype.RenderType;
import net.minecraft.client.renderer.rendertype.RenderTypes;
import net.minecraft.resources.Identifier;
import net.minecraft.util.Mth;
import net.minecraft.world.phys.Vec3;

/**
 * Lo comun a lo que se dibuja a mano de Novilis: su sol, los haces, los sellos
 * del suelo, la onda de fuego, las medias lunas y los soles que lanza. Las
 * texturas son las de novilis_extras.py; los vertices, los de NereaDibujo (con
 * entityTranslucent, que no recorta la cara de atras: cada cara una vez).
 *
 * Ojo con la cara de atras: en 26.2 entityTranslucent alumbra cada cara por su
 * lado (PER_FACE_LIGHTING), y la que se ve por detras se queda con la luz de
 * ambiente (un 40 %). El sol y las medias lunas salian pardos. Por eso lo que
 * se ve de pie pasa por cara(), que gira la normal hacia quien mira.
 *
 * El sol, los sellos, los haces y la estela van en blanco o grises y se tinen
 * con el color de la fase; las llamas y el charco llevan su color.
 */
final class NovilisDibujo {

    static final int A_PLENA_LUZ = NereaDibujo.A_PLENA_LUZ;
    /** El fuego de cada fase: ambar, oro, blanco solar, carmesi. */
    static final int[] COLOR_FASE = {0xFF8A1E, 0xFFC23A, 0xFFF0B0, 0xFF2A3A};
    /** El fuego azul de la Furia. */
    static final int FURIA = 0x5AD8FF;
    /** El oro calmo de la liberacion. */
    static final int LIBRE = 0xFFD86A;

    static final RenderType SELLO = translucido("sello");
    static final RenderType HAZ = translucido("haz");
    static final RenderType LLAMAS_N = translucido("llamas_n");
    static final RenderType LLAMAS_C = translucido("llamas_c");
    static final RenderType LLAMAS_A = translucido("llamas_a");
    static final RenderType MEDIA_LUNA = translucido("media_luna");
    static final RenderType SOL = translucido("sol");
    static final RenderType CHARCO = translucido("charco");
    static final RenderType ESTELA = translucido("estela");
    static final RenderType QUEMADO = translucido("chispas_suelo");
    static final RenderType TAJO = translucido("tajo_estela");
    static final RenderType GRIETA = translucido("grieta");
    static final RenderType GRIETA_BOCA = translucido("grieta_boca");
    /** El cubo de plasma de los soles que lanza (sol_cubo.png, en grises). */
    static final RenderType SOL_CUBO = translucido("sol_cubo");
    /**
     * Las llamaradas de esos soles: la llama de NovilisLlamasLayer, pero
     * transparente y tenida (no sumada a la luz: de dia, contra el cielo, la
     * suma se quedaba en blanco).
     */
    static final RenderType LLAMARADA = translucido("llama_sprite");

    private NovilisDibujo() {
    }

    private static RenderType translucido(String nombre) {
        return RenderTypes.entityTranslucent(Identifier.fromNamespaceAndPath(Atalaya.MOD_ID,
                "textures/entity/novilis/" + nombre + ".png"));
    }

    /** El color de una fase (1-4) o de la Furia (5). */
    static int color(int fase) {
        return fase >= 5 ? FURIA : COLOR_FASE[Math.clamp(fase, 1, 4) - 1];
    }

    /** Las llamas del color de la fase: carmesi en la IV, azules con la Furia y naranja el resto. */
    static RenderType llamas(int fase) {
        return fase >= 5 ? LLAMAS_A : fase == 4 ? LLAMAS_C : LLAMAS_N;
    }

    static int claro(int c, float k) {
        return NereaDibujo.claro(c, k);
    }

    /**
     * Un cuadrilatero (q0..q3 en orden) con su UV, alumbrado por el lado que ve
     * quien mira (ojo): la normal va hacia arriba si lo ve de frente y hacia
     * abajo si lo ve por detras, y el sombreado por caras lo deja a plena luz.
     */
    static void cara(VertexConsumer buf, PoseStack.Pose p, Vec3 ojo, Vec3 q0, Vec3 q1, Vec3 q2, Vec3 q3,
                     float u0, float u1, float v0, float v1, int color, int alfa0, int alfa1) {
        Vec3 n = q1.subtract(q0).cross(q2.subtract(q0));
        float ny = n.dot(ojo.subtract(q0)) >= 0.0 ? 1.0F : -1.0F;
        NereaDibujo.vertice(buf, p, q0.x, q0.y, q0.z, u0, v0, color, alfa0, 0, ny, 0);
        NereaDibujo.vertice(buf, p, q1.x, q1.y, q1.z, u1, v0, color, alfa0, 0, ny, 0);
        NereaDibujo.vertice(buf, p, q2.x, q2.y, q2.z, u1, v1, color, alfa1, 0, ny, 0);
        NereaDibujo.vertice(buf, p, q3.x, q3.y, q3.z, u0, v1, color, alfa1, 0, ny, 0);
    }

    /** Un cuadrado de cara a quien mira, de medio lado m, girado en su plano (la textura entera). */
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
        cara(buf, p, ojo, c.subtract(a).subtract(b), c.add(a).subtract(b), c.add(a).add(b), c.subtract(a).add(b),
                0, 1, 1, 0, color, alfa, alfa);
    }

    /** Una cinta de a a b de cara a quien mira, de medio ancho w, con la textura a lo largo (v de v0 a v1). */
    static void cinta(VertexConsumer buf, PoseStack.Pose p, Vec3 a, Vec3 b, Vec3 ojo, float w, float v0, float v1,
                      int color, int alfa) {
        Vec3 lado = b.subtract(a).cross(ojo.subtract(a.add(b).scale(0.5)));
        if (lado.lengthSqr() < 1.0E-8) {
            return;
        }
        lado = lado.normalize().scale(w);
        cara(buf, p, ojo, a.subtract(lado), a.add(lado), b.add(lado), b.subtract(lado), 0, 1, v0, v1, color, alfa, alfa);
    }

    /**
     * Un anillo de llamas de pie: un muro de radio r y alto h alrededor de
     * (cx, cy, cz), con la textura de llamas a lo largo (u) y de abajo arriba (v).
     */
    static void anillo(VertexConsumer buf, PoseStack.Pose p, Vec3 ojo, double cx, double cy, double cz, float r, float h,
                       int lados, float vueltas, float corre, int color, int alfa) {
        for (int i = 0; i < lados; i++) {
            double a0 = Math.PI * 2 * i / lados;
            double a1 = Math.PI * 2 * (i + 1) / lados;
            Vec3 q0 = new Vec3(cx + Math.cos(a0) * r, cy, cz + Math.sin(a0) * r);
            Vec3 q1 = new Vec3(cx + Math.cos(a1) * r, cy, cz + Math.sin(a1) * r);
            Vec3 q2 = q1.add(0, h, 0);
            Vec3 q3 = q0.add(0, h, 0);
            float u0 = (float) i / lados * vueltas + corre;
            float u1 = (float) (i + 1) / lados * vueltas + corre;
            cara(buf, p, ojo, q0, q1, q2, q3, u0, u1, 1.0F, 0.0F, color, alfa, alfa);
        }
    }

    /**
     * Un muro de llamas en cuadro, de medio lado r alrededor del centro (en y),
     * como anillo pero por los cuatro lados de un escalon: un tramo por bloque.
     */
    static void cuadro(VertexConsumer buf, PoseStack.Pose p, Vec3 ojo, double y, float r, float h, float corre, int color, int alfa) {
        int n = Math.max(1, Math.round(r * 2.0F));
        double[][] esquinas = {{r, r}, {-r, r}, {-r, -r}, {r, -r}, {r, r}};
        for (int lado = 0; lado < 4; lado++) {
            double[] a = esquinas[lado];
            double[] b = esquinas[lado + 1];
            for (int i = 0; i < n; i++) {
                double t0 = (double) i / n;
                double t1 = (double) (i + 1) / n;
                Vec3 q0 = new Vec3(a[0] + (b[0] - a[0]) * t0, y, a[1] + (b[1] - a[1]) * t0);
                Vec3 q1 = new Vec3(a[0] + (b[0] - a[0]) * t1, y, a[1] + (b[1] - a[1]) * t1);
                float u0 = (float) (lado * n + i) / 2.0F + corre;
                cara(buf, p, ojo, q0, q1, q1.add(0, h, 0), q0.add(0, h, 0), u0, u0 + 0.5F, 1.0F, 0.0F, color, alfa, alfa);
            }
        }
    }

    /**
     * Un haz (columna de luz) de a a b de cara a quien mira: dos cintas, la de
     * fuera del color y la del alma, mas clara.
     */
    static void haz(VertexConsumer buf, PoseStack.Pose p, Vec3 a, Vec3 b, Vec3 ojo, float ancho, float corre, int color, int alfa) {
        float largo = (float) a.distanceTo(b);
        cinta(buf, p, a, b, ojo, ancho, corre, corre + largo / 6.0F, color, alfa);
        cinta(buf, p, a, b, ojo, ancho * 0.4F, corre * 1.4F, corre * 1.4F + largo / 6.0F, claro(color, 0.7F),
                Math.min(255, alfa + 30));
    }

    /**
     * Un sol de los que lanza (el Sol Abrasador, la Supernova, los del Dios de la
     * Guerra y el que se le forma en la mano), rediseñado el 08-10-2026 (Juan):
     * dentro, un cubo de plasma casi blanco que gira; alrededor, otro mayor y
     * transparente que gira al reves; llamaradas que salen en abanico y giran
     * despacio; y el resplandor detras. La Supernova (nova) lleva mas llamaradas
     * y un anillo de cubos pequenos que le dan vueltas.
     */
    static void solBomba(SubmitNodeCollector colector, PoseStack pose, Vec3 c, Vec3 ojo, float r, float edad, int color, int alfa,
                         boolean nova) {
        float late = 1.0F + 0.06F * Mth.sin(edad * 0.5F);
        int nucleo = claro(color, 0.25F);
        int brillo = claro(color, 0.55F);
        colector.submitCustomGeometry(pose, SOL, (p, buf) ->
                cartel(buf, p, c, ojo, r * 2.3F * late, edad * 0.01F, color, (int) (alfa * 0.5F)));
        float g1 = edad * 0.09F;
        float g2 = -edad * 0.06F;
        colector.submitCustomGeometry(pose, SOL_CUBO, (p, buf) -> {
            cubo(buf, p, ojo, c, r * 0.6F, g1, g1 * 0.7F, nucleo, 255, false);
            cubo(buf, p, ojo, c, r * 0.92F * late, g2, g2 * 1.3F + 0.6F, color, (int) (alfa * 0.38F), true);
            if (nova) {
                for (int k = 0; k < 8; k++) {
                    double a = edad * 0.08 + k * Math.PI / 4;
                    Vec3 q = c.add(Math.cos(a) * r * 1.6, Math.sin(a * 0.5 + k) * r * 0.35, Math.sin(a) * r * 1.6);
                    cubo(buf, p, ojo, q, r * 0.14F, g1 * 2.0F + k, g1 + k, brillo, 255, false);
                }
            }
        });
        int n = nova ? 10 : 6;
        colector.submitCustomGeometry(pose, LLAMARADA, (p, buf) -> {
            for (int k = 0; k < n; k++) {
                float ang = edad * 0.03F + k * (float) (Math.PI * 2.0) / n;
                float largo = r * (nova ? 1.7F : 1.3F) * (0.8F + 0.25F * Mth.sin(edad * 0.4F + k * 1.9F));
                int cuadro = (int) (edad / 1.4F + k * 3) % 8;
                llamarada(buf, p, c, ojo, r * 0.45F, largo, r * 0.75F, ang, cuadro, color, alfa);
            }
        });
    }

    /**
     * Un cubo de medio lado h en c, girado (cabeceo y guinada, en radianes), con
     * la textura entera en cada cara. Con soloFrente, solo las caras que dan a
     * quien mira (para el cubo transparente de fuera: si no, se ven las de
     * detras a traves).
     */
    static void cubo(VertexConsumer buf, PoseStack.Pose p, Vec3 ojo, Vec3 c, float h, float guinada, float cabeceo, int color,
                     int alfa, boolean soloFrente) {
        double cg = Math.cos(guinada), sg = Math.sin(guinada), cc = Math.cos(cabeceo), sc = Math.sin(cabeceo);
        Vec3[] v = new Vec3[8];
        for (int i = 0; i < 8; i++) {
            double x = (i & 1) == 0 ? -h : h;
            double y = (i & 2) == 0 ? -h : h;
            double z = (i & 4) == 0 ? -h : h;
            double y1 = y * cc - z * sc;
            double z1 = y * sc + z * cc;
            v[i] = new Vec3(c.x + x * cg + z1 * sg, c.y + y1, c.z - x * sg + z1 * cg);
        }
        int[][] caras = {{0, 2, 3, 1}, {4, 5, 7, 6}, {0, 1, 5, 4}, {2, 6, 7, 3}, {0, 4, 6, 2}, {1, 3, 7, 5}};
        for (int[] f : caras) {
            Vec3 q0 = v[f[0]];
            Vec3 q1 = v[f[1]];
            Vec3 q2 = v[f[2]];
            Vec3 q3 = v[f[3]];
            if (soloFrente) {
                Vec3 centro = q0.add(q2).scale(0.5);
                Vec3 fuera = centro.subtract(c);
                if (fuera.dot(ojo.subtract(centro)) <= 0.0) {
                    continue;
                }
            }
            cara(buf, p, ojo, q0, q1, q2, q3, 0, 1, 0, 1, color, alfa, alfa);
        }
    }

    /**
     * Una llamarada: un cuadro de la llama que sale de c hacia fuera (de "desde" a
     * "desde + largo"), en el plano de quien mira y girada "ang". La base (v = 1)
     * junto al sol y la punta fuera. Va con LLAMARADA.
     */
    static void llamarada(VertexConsumer buf, PoseStack.Pose p, Vec3 c, Vec3 ojo, float desde, float largo, float ancho, float ang,
                          int cuadro, int color, int alfa) {
        Vec3 d = ojo.subtract(c);
        if (d.lengthSqr() < 1.0E-6) {
            return;
        }
        d = d.normalize();
        Vec3 der = d.cross(new Vec3(0, 1, 0));
        der = der.lengthSqr() < 1.0E-6 ? new Vec3(1, 0, 0) : der.normalize();
        Vec3 arr = der.cross(d).normalize();
        Vec3 fuera = der.scale(Math.cos(ang)).add(arr.scale(Math.sin(ang)));
        Vec3 lado = der.scale(-Math.sin(ang)).add(arr.scale(Math.cos(ang))).scale(ancho * 0.5);
        Vec3 b = c.add(fuera.scale(desde));
        Vec3 a = c.add(fuera.scale(desde + largo));
        float u0 = cuadro / 8.0F;
        float u1 = (cuadro + 1) / 8.0F;
        NereaDibujo.vertice(buf, p, b.x - lado.x, b.y - lado.y, b.z - lado.z, u0, 1, color, alfa, (float) d.x, (float) d.y, (float) d.z);
        NereaDibujo.vertice(buf, p, b.x + lado.x, b.y + lado.y, b.z + lado.z, u1, 1, color, alfa, (float) d.x, (float) d.y, (float) d.z);
        NereaDibujo.vertice(buf, p, a.x + lado.x, a.y + lado.y, a.z + lado.z, u1, 0, color, alfa, (float) d.x, (float) d.y, (float) d.z);
        NereaDibujo.vertice(buf, p, a.x - lado.x, a.y - lado.y, a.z - lado.z, u0, 0, color, alfa, (float) d.x, (float) d.y, (float) d.z);
    }

    /** Un sol (el brillo y la corona de cara a quien mira), de radio r, que late y gira. */
    static void sol(VertexConsumer buf, PoseStack.Pose p, Vec3 c, Vec3 ojo, float r, float edad, int color, int alfa) {
        float late = 1.0F + 0.05F * Mth.sin(edad * 0.35F);
        // Cada capa un poco mas cerca de quien mira: en el mismo plano se pisaban
        // en la profundidad y solo se veia la de fuera (un disco pardo).
        Vec3 haciaOjo = ojo.subtract(c);
        Vec3 paso = haciaOjo.lengthSqr() > 1.0E-6 ? haciaOjo.normalize().scale(Math.min(0.15, r * 0.06)) : Vec3.ZERO;
        cartel(buf, p, c, ojo, r * 2.2F * late, edad * 0.01F, color, (int) (alfa * 0.55F));
        cartel(buf, p, c.add(paso), ojo, r * 1.3F, -edad * 0.025F, claro(color, 0.35F), alfa);
        cartel(buf, p, c.add(paso.scale(2)), ojo, r * 0.8F * late, edad * 0.04F, claro(color, 0.75F), alfa);
    }
}
