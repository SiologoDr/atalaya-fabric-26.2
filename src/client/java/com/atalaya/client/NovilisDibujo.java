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
     * Un haz (columna de luz) de a a b de cara a quien mira: dos cintas, la de
     * fuera del color y la del alma, mas clara.
     */
    static void haz(VertexConsumer buf, PoseStack.Pose p, Vec3 a, Vec3 b, Vec3 ojo, float ancho, float corre, int color, int alfa) {
        float largo = (float) a.distanceTo(b);
        cinta(buf, p, a, b, ojo, ancho, corre, corre + largo / 6.0F, color, alfa);
        cinta(buf, p, a, b, ojo, ancho * 0.4F, corre * 1.4F, corre * 1.4F + largo / 6.0F, claro(color, 0.7F),
                Math.min(255, alfa + 30));
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
