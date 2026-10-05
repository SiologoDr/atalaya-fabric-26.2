package com.atalaya.client;

import com.atalaya.Atalaya;
import com.atalaya.entity.TornadoAeralisEntity;
import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import net.minecraft.client.renderer.SubmitNodeCollector;
import net.minecraft.client.renderer.entity.EntityRenderer;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.state.EntityRenderState;
import net.minecraft.client.renderer.rendertype.RenderType;
import net.minecraft.client.renderer.rendertype.RenderTypes;
import net.minecraft.client.renderer.state.level.CameraRenderState;
import net.minecraft.resources.Identifier;
import net.minecraft.util.Mth;

/**
 * Un tornado de Aeralis: un embudo de viento que se ensancha hacia arriba, de
 * dos capas que giran a distinta velocidad (la de dentro mas deprisa) y con
 * las vetas subiendo. Se tuerce un poco, como uno de verdad. Al nacer crece
 * desde el remolino de polvo; al deshacerse se abre y se desvanece.
 *
 * El ciclon del Juicio es el mismo, tres veces mas grande, y se encoge con cada
 * nucleo roto.
 */
public class TornadoAeralisRenderer extends EntityRenderer<TornadoAeralisEntity, TornadoAeralisRenderer.Estado> {

    private static final RenderType TIPO = RenderTypes.entityTranslucent(
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "textures/entity/aeralis/tornado.png"));
    private static final int ALTURAS = 14;
    private static final int LADOS = 18;

    public static class Estado extends EntityRenderState {
        public float edad;
        public boolean ciclon;
        public float fuerza = 1.0F;
        public float desvanece;
    }

    public TornadoAeralisRenderer(EntityRendererProvider.Context contexto) {
        super(contexto);
    }

    @Override
    public Estado createRenderState() {
        return new Estado();
    }

    @Override
    public void extractRenderState(TornadoAeralisEntity t, Estado s, float parcial) {
        super.extractRenderState(t, s, parcial);
        s.edad = t.tickCount + parcial;
        s.ciclon = t.isCiclon();
        s.fuerza = t.getFuerza();
        s.desvanece = t.inicioDeshacer >= 0
                ? Mth.clamp((t.tickCount + parcial - t.inicioDeshacer) / 20.0F, 0.0F, 1.0F) : 0.0F;
    }

    @Override
    protected boolean affectedByCulling(TornadoAeralisEntity t) {
        return false;
    }

    @Override
    public void submit(Estado s, PoseStack pose, SubmitNodeCollector colector, CameraRenderState camara) {
        float crece = Mth.clamp((s.edad - TornadoAeralisEntity.NACER) / 10.0F, 0.0F, 1.0F);
        if (crece <= 0.0F || s.desvanece >= 1.0F) {
            return;
        }
        float esc = s.ciclon ? TornadoAeralisEntity.ESCALA_CICLON * (0.55F + 0.45F * s.fuerza) : 1.0F;
        float alto = 8.5F * esc * (float) Math.pow(crece, 0.7) * (1.0F - 0.3F * s.desvanece);
        float ancho = esc * (0.4F + 0.6F * crece) * (1.0F + 0.8F * s.desvanece);
        float alfa = (1.0F - s.desvanece) * (s.ciclon ? 0.85F : 0.8F);
        colector.submitCustomGeometry(pose, TIPO, (p, buf) -> {
            capa(buf, p, s.edad, alto, ancho, 1.0F, 1.0F, alfa, 200, 210, 226);
            capa(buf, p, s.edad + 13.0F, alto * 0.96F, ancho * 0.66F, 1.9F, -1.4F, alfa * 0.75F, 236, 242, 250);
            faldon(buf, p, s.edad, ancho, alfa);
        });
        super.submit(s, pose, colector, camara);
    }

    /** Una capa del embudo: anillos que se ensanchan hacia arriba y se tuercen. */
    /** El faldon de polvo de la base: un anillo bajo y ancho que gira deprisa. */
    private static void faldon(VertexConsumer buf, PoseStack.Pose p, float edad, float ancho, float alfa) {
        for (int i = 0; i < LADOS; i++) {
            for (int j = 0; j < 2; j++) {
                float a0 = i / (float) LADOS;
                float a1 = (i + 1) / (float) LADOS;
                float h0 = j / 2.0F;
                float h1 = (j + 1) / 2.0F;
                falda(buf, p, edad, ancho, alfa, a0, h0);
                falda(buf, p, edad, ancho, alfa, a1, h0);
                falda(buf, p, edad, ancho, alfa, a1, h1);
                falda(buf, p, edad, ancho, alfa, a0, h1);
            }
        }
    }

    private static void falda(VertexConsumer buf, PoseStack.Pose p, float edad, float ancho, float alfa, float a, float h) {
        double ang = a * Mth.TWO_PI;
        float r = ancho * (1.4F + 1.3F * h);
        double y = h * 1.3F * ancho;
        int al = (int) (200 * alfa * (1.0F - h));
        AeralisDibujo.vertice(buf, p, Math.cos(ang) * r, y, Math.sin(ang) * r, a * 3.0F + edad * 0.09F, h * 0.5F,
                176, 168, 150, Math.max(0, al), AeralisDibujo.A_PLENA_LUZ, (float) Math.cos(ang), 0.3F, (float) Math.sin(ang));
    }

    private static void capa(VertexConsumer buf, PoseStack.Pose p, float edad, float alto, float ancho, float giro,
                             float sube, float alfa, int rr, int gg, int bb) {
        for (int j = 0; j < ALTURAS; j++) {
            for (int i = 0; i < LADOS; i++) {
                float a0 = i / (float) LADOS;
                float a1 = (i + 1) / (float) LADOS;
                float h0 = j / (float) ALTURAS;
                float h1 = (j + 1) / (float) ALTURAS;
                punto(buf, p, edad, alto, ancho, giro, sube, alfa, a0, h0, rr, gg, bb);
                punto(buf, p, edad, alto, ancho, giro, sube, alfa, a1, h0, rr, gg, bb);
                punto(buf, p, edad, alto, ancho, giro, sube, alfa, a1, h1, rr, gg, bb);
                punto(buf, p, edad, alto, ancho, giro, sube, alfa, a0, h1, rr, gg, bb);
            }
        }
    }

    private static void punto(VertexConsumer buf, PoseStack.Pose p, float edad, float alto, float ancho, float giro,
                              float sube, float alfa, float a, float h, int rr, int gg, int bb) {
        double ang = a * Mth.TWO_PI;
        float r = ancho * (0.42F + 2.2F * (float) Math.pow(h, 1.5));
        // El eje se tuerce y baila: arriba se va mas que abajo.
        double ox = Mth.sin(h * 3.0F + edad * 0.11F) * 0.45F * h * ancho;
        double oz = Mth.cos(h * 2.6F + edad * 0.09F) * 0.45F * h * ancho;
        double x = ox + Math.cos(ang) * r;
        double z = oz + Math.sin(ang) * r;
        double y = h * alto;
        float u = a * 2.0F + edad * 0.045F * giro;
        float v = h * 3.0F - edad * 0.03F * sube;
        // Se deshace por abajo y por arriba.
        float borde = Math.min(1.0F, h / 0.12F) * Math.min(1.0F, (1.0F - h) / 0.2F);
        int al = (int) (255 * alfa * Mth.clamp(borde, 0.0F, 1.0F));
        AeralisDibujo.vertice(buf, p, x, y, z, u, v, rr, gg, bb, al, AeralisDibujo.A_PLENA_LUZ,
                (float) Math.cos(ang), 0.0F, (float) Math.sin(ang));
    }
}
