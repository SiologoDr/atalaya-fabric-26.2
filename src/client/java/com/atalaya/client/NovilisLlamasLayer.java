package com.atalaya.client;

import com.atalaya.Atalaya;
import com.atalaya.entity.NovilisEntity;
import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import net.minecraft.client.renderer.SubmitNodeCollector;
import net.minecraft.client.renderer.entity.RenderLayerParent;
import net.minecraft.client.renderer.entity.layers.RenderLayer;
import net.minecraft.client.renderer.rendertype.RenderType;
import net.minecraft.client.renderer.rendertype.RenderTypes;
import net.minecraft.resources.Identifier;
import net.minecraft.util.Mth;
import org.joml.Matrix4f;
import org.joml.Vector3f;

/**
 * El fuego de la Furia (azul) y del Dios de la Guerra (carmesi): lenguas de
 * fuego que le salen del yelmo, de las hombreras, de los punos y de la hoja,
 * cada una pegada a su hueso (siguen la animacion) y siempre de cara a quien
 * mira, subiendo hacia arriba del mundo aunque el se doble.
 *
 * Antes era la malla entera hinchada con bandas de fuego encima: lo tapaba todo
 * con un manto azul y no se le veia ("la Furia se ve rara"). Ahora se le ve la
 * armadura (con las grietas en azul, la piel de la Furia) y el fuego sale de
 * donde arde.
 *
 * Se pinta con suma de luz (energySwirl, como la carga del creeper): lo oscuro
 * de llama_sprite.png no se ve y lo claro brilla sin luz. La llama es una fila
 * de 8 cuadros; cada lengua va desfasada para que no latan a la vez.
 */
public class NovilisLlamasLayer extends RenderLayer<NovilisRenderState, NovilisModel> {

    private static final RenderType FUEGO = RenderTypes.energySwirl(
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "textures/entity/novilis/llama_sprite.png"), 0.0F, 0.0F);
    private static final int CUADROS = 8;
    /** Ticks por cuadro de la llama. */
    private static final float CADA = 1.4F;
    /** Lo que tarda en prender del todo al entrar en Furia (ticks). */
    private static final float PRENDE = 12.0F;

    /** Donde arde: hueso, punto (px del hueso), alto y ancho (px), y en que fuego. */
    private record Lengua(String hueso, float x, float y, float z, float alto, float ancho, boolean grito) {
    }

    private static final Lengua[] LENGUAS = {
            new Lengua("cabeza", 0, -28, 0, 54, 26, true),
            new Lengua("cabeza", 9, -22, 3, 32, 16, false),
            new Lengua("cabeza", -9, -22, 3, 32, 16, false),
            new Lengua("hombro_izq", 5, -12, 0, 44, 24, true),
            new Lengua("hombro_der", -5, -12, 0, 44, 24, true),
            new Lengua("hombro_izq", 11, -8, 9, 30, 16, false),
            new Lengua("hombro_der", -11, -8, 9, 30, 16, false),
            new Lengua("hombro_izq", 2, -10, -9, 26, 14, false),
            new Lengua("hombro_der", -2, -10, -9, 26, 14, false),
            new Lengua("mano_izq", 0, 5, -2, 28, 17, false),
            new Lengua("torso", 0, -44, 14, 34, 28, false),
            new Lengua("torso", 12, -40, 13, 26, 18, false),
            new Lengua("torso", -12, -40, 13, 26, 18, false),
    };
    /** Lo largo de la hoja (px desde el agarre de la espada, hacia la punta). */
    private static final float[] HOJA = {28, 38, 48, 58, 68, 78};

    public NovilisLlamasLayer(RenderLayerParent<NovilisRenderState, NovilisModel> padre) {
        super(padre);
    }

    @Override
    public void submit(PoseStack pose, SubmitNodeCollector colector, int luz, NovilisRenderState s, float yRot, float xRot) {
        if (s.deathTime > 0) {
            return;
        }
        int color;
        float k;
        boolean soloGrito = false;
        if (s.furia) {
            color = NovilisDibujo.FURIA;
            k = Mth.clamp(s.desdeFuria / PRENDE, 0.0F, 1.0F);
        } else if (s.estado == NovilisEntity.DIOS) {
            color = NovilisDibujo.COLOR_FASE[3];
            k = 1.15F;
        } else if (s.grito) {
            color = NovilisDibujo.COLOR_FASE[3];
            k = 0.7F;
            soloGrito = true;
        } else {
            return;
        }
        NovilisModel modelo = getParentModel();
        float t = s.ageInTicks;
        int i = 0;
        for (Lengua l : LENGUAS) {
            i++;
            if (soloGrito && !l.grito()) {
                continue;
            }
            lengua(pose, colector, modelo, l.hueso(), l.x(), l.y(), l.z(), l.alto() * k, l.ancho() * k, color, t, i);
        }
        if (!soloGrito) {
            String hoja = modelo.espadaEnMano() ? "espada" : "espada_suelta";
            for (float y : HOJA) {
                i++;
                lengua(pose, colector, modelo, hoja, 0, y, 0, 22 * k, 13 * k, color, t, i);
            }
        }
    }

    private static void lengua(PoseStack pose, SubmitNodeCollector colector, NovilisModel modelo, String hueso,
                               float x, float y, float z, float alto, float ancho, int color, float t, int i) {
        if (alto < 0.5F) {
            return;
        }
        pose.pushPose();
        modelo.aPieza(pose, hueso);
        // Quien mira y "arriba" del mundo, en el espacio del hueso.
        Matrix4f inv = new Matrix4f(pose.last().pose()).invert();
        Vector3f ojo = inv.transformPosition(new Vector3f());
        Vector3f arriba = inv.transformDirection(new Vector3f(0, 1, 0)).normalize();
        Vector3f c = new Vector3f(x / 16.0F, y / 16.0F, z / 16.0F);
        // El tamano va en px del modelo: crece con el.
        float h = alto / 16.0F * (0.9F + 0.12F * Mth.sin(t * 0.37F + i * 1.7F));
        float w = ancho / 16.0F;
        Vector3f haciaOjo = new Vector3f(ojo).sub(c);
        Vector3f lado = new Vector3f(arriba).cross(haciaOjo);
        if (lado.lengthSquared() < 1.0E-8F) {
            pose.popPose();
            return;
        }
        lado.normalize(w * 0.5F);
        int cuadro = (int) (t / CADA + i * 3) % CUADROS;
        float u0 = cuadro / (float) CUADROS;
        float u1 = (cuadro + 1) / (float) CUADROS;
        Vector3f hacia = new Vector3f(haciaOjo).normalize(0.02F);
        colector.submitCustomGeometry(pose, FUEGO, (p, buf) -> {
            quad(buf, p, c, lado, arriba, h, u0, u1, color, 1.0F);
            // el alma, mas clara y mas baja
            Vector3f c2 = new Vector3f(c).add(hacia);
            quad(buf, p, c2, new Vector3f(lado).mul(0.55F), arriba, h * 0.6F, u0, u1, NovilisDibujo.claro(color, 0.4F), 0.75F);
        });
        pose.popPose();
    }

    private static void quad(VertexConsumer buf, PoseStack.Pose p, Vector3f c, Vector3f lado, Vector3f arriba, float h,
                             float u0, float u1, int color, float k) {
        // la base un poco por debajo del punto, para que la llama salga de dentro
        Vector3f b = new Vector3f(arriba).mul(-h * 0.14F).add(c);
        Vector3f a = new Vector3f(arriba).mul(h * 0.86F).add(c);
        int r = (int) (((color >> 16) & 255) * k);
        int g = (int) (((color >> 8) & 255) * k);
        int bl = (int) ((color & 255) * k);
        int col = (r << 16) | (g << 8) | bl;
        NereaDibujo.vertice(buf, p, b.x - lado.x, b.y - lado.y, b.z - lado.z, u0, 1, col, 255, arriba.x, arriba.y, arriba.z);
        NereaDibujo.vertice(buf, p, b.x + lado.x, b.y + lado.y, b.z + lado.z, u1, 1, col, 255, arriba.x, arriba.y, arriba.z);
        NereaDibujo.vertice(buf, p, a.x + lado.x, a.y + lado.y, a.z + lado.z, u1, 0, col, 255, arriba.x, arriba.y, arriba.z);
        NereaDibujo.vertice(buf, p, a.x - lado.x, a.y - lado.y, a.z - lado.z, u0, 0, col, 255, arriba.x, arriba.y, arriba.z);
    }
}
