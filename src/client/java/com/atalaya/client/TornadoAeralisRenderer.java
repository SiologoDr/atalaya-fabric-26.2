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
import net.minecraft.world.phys.Vec3;

/**
 * Un tornado de Aeralis: un embudo de viento que se ensancha hacia arriba, de
 * dos capas que giran a distinta velocidad (la de dentro, de tormenta oscura,
 * mas deprisa) y con las vetas subiendo. Se tuerce un poco, como uno de verdad.
 * Al nacer crece desde el remolino de polvo; al deshacerse se abre y se
 * desvanece.
 *
 * Desde el remake lleva el color de la fase, un aro en el suelo hasta donde
 * atrapa y tres anillos de luz a su alrededor: sus tres golpes (se apaga uno con
 * cada golpe). Desde la fase III le saltan rayos dentro.
 *
 * El ciclon del Juicio es el mismo, tres veces mas grande, de tormenta y con
 * rayos, y se encoge con cada nucleo roto.
 */
public class TornadoAeralisRenderer extends EntityRenderer<TornadoAeralisEntity, TornadoAeralisRenderer.Estado> {

    private static final RenderType TIPO = RenderTypes.entityTranslucent(
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "textures/entity/aeralis/embudo.png"));
    private static final RenderType ARO = RenderTypes.entityTranslucentEmissive(
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "textures/entity/aeralis/aro.png"));
    private static final RenderType RAYO = RenderTypes.entityTranslucentEmissive(
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "textures/entity/aeralis/rayo.png"));
    private static final int ALTURAS = 14;
    private static final int LADOS = 18;
    /** Hasta donde atrapa (el RADIO del tornado y un poco). */
    private static final float ARO_RADIO = 2.4F;

    public static class Estado extends EntityRenderState {
        public float edad;
        public boolean ciclon;
        public float fuerza = 1.0F;
        public float desvanece;
        public int fase = 1;
        public int golpes;
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
        s.fase = t.getFase();
        s.golpes = t.getGolpes();
        s.desvanece = t.inicioDeshacer >= 0
                ? Mth.clamp((t.tickCount + parcial - t.inicioDeshacer) / 20.0F, 0.0F, 1.0F) : 0.0F;
    }

    @Override
    protected boolean affectedByCulling(TornadoAeralisEntity t) {
        return false;
    }

    @Override
    public void submit(Estado s, PoseStack pose, SubmitNodeCollector colector, CameraRenderState camara) {
        int color = AeralisDibujo.fase(s.fase);
        float crece = Mth.clamp((s.edad - TornadoAeralisEntity.NACER) / 10.0F, 0.0F, 1.0F);
        if (crece <= 0.0F || s.desvanece >= 1.0F) {
            return;
        }
        float esc = s.ciclon ? TornadoAeralisEntity.ESCALA_CICLON * (0.55F + 0.45F * s.fuerza) : 1.0F;
        float alto = 12.0F * esc * (float) Math.pow(crece, 0.7) * (1.0F - 0.3F * s.desvanece);
        float ancho = esc * (0.4F + 0.6F * crece) * (1.0F + 0.8F * s.desvanece);
        float alfa = (1.0F - s.desvanece) * (s.ciclon ? 0.88F : 0.82F);
        int fuera = AeralisDibujo.claro(color, s.ciclon ? 0.12F : 0.22F);
        int dentro = AeralisDibujo.tormenta(s.fase);
        colector.submitCustomGeometry(pose, TIPO, (p, buf) -> {
            capa(buf, p, s.edad, alto, ancho, 1.0F, 1.0F, alfa, fuera);
            capa(buf, p, s.edad + 13.0F, alto * 0.96F, ancho * 0.66F, 1.9F, -1.4F, alfa * 0.85F, dentro);
            faldon(buf, p, s.edad, ancho, alfa);
        });
        if (!s.ciclon) {
            // El aro del suelo: hasta donde atrapa.
            colector.submitCustomGeometry(pose, ARO, (p, buf) ->
                    AeralisDibujo.suelo(buf, p, 0.0, 0.07, 0.0, ARO_RADIO * crece, s.edad * 0.02F, color, (int) (220 * alfa)));
            // Los tres anillos de luz: los golpes que le quedan.
            int quedan = TornadoAeralisEntity.GOLPES - s.golpes;
            colector.submitCustomGeometry(pose, RAYO, (p, buf) -> {
                float[] alturas = {0.3F, 0.55F, 0.8F};
                for (int k = 0; k < quedan; k++) {
                    float h = alturas[k];
                    anillo(buf, p, ancho * (0.42F + 2.8F * (float) Math.pow(h, 1.5)) + 0.3F, h * alto,
                            s.edad * 0.08F * (k % 2 == 0 ? 1 : -1), AeralisDibujo.claro(color, 0.4F), (int) (235 * alfa));
                }
            });
        }
        // Rayos dentro: desde la fase III y siempre en el ciclon.
        Vec3 ojo = camara.pos.subtract(s.x, s.y, s.z);
        if (s.ciclon || s.fase >= 3) {
            long semilla = (long) (s.edad / 3.0F);
            int n = s.ciclon ? 3 : 1;
            colector.submitCustomGeometry(pose, RAYO, (p, buf) -> {
                for (int k = 0; k < n; k++) {
                    if (((semilla + k) % 3) == 0) {
                        continue;
                    }
                    double a = (semilla * 1.7 + k * 2.1) % (Math.PI * 2);
                    Vec3 arriba = new Vec3(Math.cos(a) * ancho, alto * 0.92, Math.sin(a) * ancho);
                    Vec3 abajo = new Vec3(Math.cos(a + 1.2) * ancho * 0.4, alto * 0.15, Math.sin(a + 1.2) * ancho * 0.4);
                    AeralisDibujo.rayo(buf, p, arriba, abajo, ojo, semilla * 31 + k, 8, 0.25 * esc, 0.12F * esc,
                            AeralisDibujo.claro(color, 0.7F), (int) (255 * alfa));
                }
            });
        }
        super.submit(s, pose, colector, camara);
    }

    /** Un anillo de luz horizontal alrededor del embudo, a la altura y. */
    private static void anillo(VertexConsumer buf, PoseStack.Pose p, float r, float y, float giro, int c, int alfa) {
        float grueso = 0.16F;
        for (int i = 0; i < 24; i++) {
            double a0 = giro + i * Mth.TWO_PI / 24, a1 = giro + (i + 1) * Mth.TWO_PI / 24;
            double x0 = Math.cos(a0) * r, z0 = Math.sin(a0) * r, x1 = Math.cos(a1) * r, z1 = Math.sin(a1) * r;
            AeralisDibujo.vertice(buf, p, x0, y - grueso, z0, 0.0F, 0.5F, AeralisDibujo.r(c), AeralisDibujo.g(c), AeralisDibujo.b(c), alfa,
                    AeralisDibujo.A_PLENA_LUZ, (float) Math.cos(a0), 0, (float) Math.sin(a0));
            AeralisDibujo.vertice(buf, p, x1, y - grueso, z1, 1.0F, 0.5F, AeralisDibujo.r(c), AeralisDibujo.g(c), AeralisDibujo.b(c), alfa,
                    AeralisDibujo.A_PLENA_LUZ, (float) Math.cos(a1), 0, (float) Math.sin(a1));
            AeralisDibujo.vertice(buf, p, x1, y + grueso, z1, 1.0F, 0.5F, AeralisDibujo.r(c), AeralisDibujo.g(c), AeralisDibujo.b(c), alfa,
                    AeralisDibujo.A_PLENA_LUZ, (float) Math.cos(a1), 0, (float) Math.sin(a1));
            AeralisDibujo.vertice(buf, p, x0, y + grueso, z0, 0.0F, 0.5F, AeralisDibujo.r(c), AeralisDibujo.g(c), AeralisDibujo.b(c), alfa,
                    AeralisDibujo.A_PLENA_LUZ, (float) Math.cos(a0), 0, (float) Math.sin(a0));
        }
    }

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

    /** Una capa del embudo: anillos que se ensanchan hacia arriba y se tuercen. */
    private static void capa(VertexConsumer buf, PoseStack.Pose p, float edad, float alto, float ancho, float giro,
                             float sube, float alfa, int c) {
        for (int j = 0; j < ALTURAS; j++) {
            for (int i = 0; i < LADOS; i++) {
                float a0 = i / (float) LADOS;
                float a1 = (i + 1) / (float) LADOS;
                float h0 = j / (float) ALTURAS;
                float h1 = (j + 1) / (float) ALTURAS;
                vertice(buf, p, edad, alto, ancho, giro, sube, alfa, a0, h0, c);
                vertice(buf, p, edad, alto, ancho, giro, sube, alfa, a1, h0, c);
                vertice(buf, p, edad, alto, ancho, giro, sube, alfa, a1, h1, c);
                vertice(buf, p, edad, alto, ancho, giro, sube, alfa, a0, h1, c);
            }
        }
    }

    private static void vertice(VertexConsumer buf, PoseStack.Pose p, float edad, float alto, float ancho, float giro,
                                float sube, float alfa, float a, float h, int c) {
        double ang = a * Mth.TWO_PI;
        float r = ancho * (0.42F + 2.8F * (float) Math.pow(h, 1.5));
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
        AeralisDibujo.vertice(buf, p, x, y, z, u, v, AeralisDibujo.r(c), AeralisDibujo.g(c), AeralisDibujo.b(c), al,
                AeralisDibujo.A_PLENA_LUZ, (float) Math.cos(ang), 0.0F, (float) Math.sin(ang));
    }
}
