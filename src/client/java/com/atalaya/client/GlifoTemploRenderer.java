package com.atalaya.client;

import com.atalaya.Atalaya;
import com.atalaya.entity.GlifoTemploEntity;
import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.math.Axis;
import java.util.ArrayList;
import java.util.List;
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
 * Una columna de Glifos del Templo (rajang_minijuegos.py): zocalo y capitel
 * con la greca de oro, fuste de sillares de jade y el glifo tallado en las
 * cuatro caras (glifos.png), que brilla encendido (glifos_brillo.png) y late
 * despacio. Con cada golpe a una buena tiembla y se raja (las grietas de la
 * losa encima del glifo); rota, se viene abajo; la falsa estalla y desaparece
 * entre las chispas. Sale del suelo y se hunde al acabar.
 */
public class GlifoTemploRenderer extends EntityRenderer<GlifoTemploEntity, GlifoTemploRenderer.Estado> {

    private static final RenderType PIEDRA = RenderTypes.entityCutout(tex("glifo_columna"));
    private static final RenderType GLIFOS = RenderTypes.entityCutout(tex("glifos"));
    private static final RenderType BRILLO = RenderTypes.eyes(tex("glifos_brillo"));
    private static final RenderType GRIETAS = RenderTypes.entityCutout(tex("losa_grietas"));
    private static final List<RajangDibujo.Cara> COLUMNA = new ArrayList<>();
    /** Los paneles de cada glifo (los ocho) y de cada grieta (las tres). */
    @SuppressWarnings("unchecked")
    private static final List<RajangDibujo.Cara>[] PANELES = new List[8];
    @SuppressWarnings("unchecked")
    private static final List<RajangDibujo.Cara>[] BRILLOS = new List[8];
    @SuppressWarnings("unchecked")
    private static final List<RajangDibujo.Cara>[] RAJAS = new List[3];
    private static final double FUSTE = 0.8;
    private static final double ZOCALO = 0.5;
    private static final double CAPITEL = 4.1;
    private static final double PANEL = 0.66;
    private static final double PANEL_Y = 2.35;

    static {
        double z = GlifoTemploEntity.ANCHO / 2.0;
        RajangDibujo.caja(COLUMNA, -z, 0, -z, z, ZOCALO, z, uv(26, 0, 61, 8), uv(26, 8, 61, 43));
        RajangDibujo.caja(COLUMNA, -FUSTE, ZOCALO, -FUSTE, FUSTE, CAPITEL, FUSTE, uv(0, 0, 26, 52), uv(0, 0, 26, 26));
        RajangDibujo.caja(COLUMNA, -1.0, CAPITEL, -1.0, 1.0, GlifoTemploEntity.ALTO, 1.0, uv(64, 0, 96, 8), uv(64, 8, 96, 40));
        for (int g = 0; g < 8; g++) {
            PANELES[g] = new ArrayList<>();
            caras(PANELES[g], g / 8.0F, 0.0F, (g + 1) / 8.0F, 1.0F, 0.012);
            // El brillo, algo por fuera de la talla: a la misma distancia se peleaban y parpadeaba.
            List<RajangDibujo.Cara> brillo = new ArrayList<>();
            caras(brillo, g / 8.0F, 0.0F, (g + 1) / 8.0F, 1.0F, 0.03);
            BRILLOS[g] = RajangDibujo.dosCaras(brillo);
        }
        for (int e = 0; e < 3; e++) {
            RAJAS[e] = new ArrayList<>();
            caras(RAJAS[e], 0.0F, e / 3.0F, 1.0F, (e + 1) / 3.0F, 0.045);
        }
    }

    /** Un panel en cada cara del fuste, mirando hacia fuera. */
    private static void caras(List<RajangDibujo.Cara> out, float u0, float v0, float u1, float v1, double fuera) {
        double d = FUSTE + fuera;
        Vec3 arriba = new Vec3(0, PANEL, 0);
        // Desde fuera de cada cara, su derecha: al sur (+z) es +x, al norte -x, al este -z y al oeste +z.
        RajangDibujo.panel(out, new Vec3(0, PANEL_Y, d), new Vec3(PANEL, 0, 0), arriba, u0, v0, u1, v1);
        RajangDibujo.panel(out, new Vec3(0, PANEL_Y, -d), new Vec3(-PANEL, 0, 0), arriba, u0, v0, u1, v1);
        RajangDibujo.panel(out, new Vec3(d, PANEL_Y, 0), new Vec3(0, 0, -PANEL), arriba, u0, v0, u1, v1);
        RajangDibujo.panel(out, new Vec3(-d, PANEL_Y, 0), new Vec3(0, 0, PANEL), arriba, u0, v0, u1, v1);
    }

    private static Identifier tex(String nombre) {
        return Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "textures/entity/rajang/" + nombre + ".png");
    }

    private static float[] uv(int u0, int v0, int u1, int v1) {
        return RajangDibujo.uv(u0 / 128.0F, v0 / 64.0F, u1 / 128.0F, v1 / 64.0F);
    }

    public static class Estado extends EntityRenderState {
        public float salida;
        public float rumbo;
        public int glifo;
        public int golpes;
        public float tiembla;
        /** Lo que lleva cayendose la buena rota (0 a 1); -1 entera. */
        public float rota = -1.0F;
        public boolean estallo;
        public float tiempo;
    }

    public GlifoTemploRenderer(EntityRendererProvider.Context contexto) {
        super(contexto);
    }

    @Override
    public Estado createRenderState() {
        return new Estado();
    }

    @Override
    public void extractRenderState(GlifoTemploEntity g, Estado s, float parcial) {
        super.extractRenderState(g, s, parcial);
        s.salida = g.salida(parcial);
        s.rumbo = g.getYRot();
        s.glifo = Mth.clamp(g.getGlifo(), 0, 7);
        s.golpes = g.getGolpes();
        float desde = g.tickCount - g.getGolpeada() + parcial;
        s.tiembla = desde < 8 ? 1.0F - desde / 8.0F : 0.0F;
        int rota = g.getRota();
        s.rota = rota >= 0 ? Mth.clamp((g.tickCount - rota + parcial) / GlifoTemploEntity.ROMPE, 0.0F, 1.0F) : -1.0F;
        s.estallo = g.estallo();
        s.tiempo = g.tickCount + parcial;
    }

    @Override
    public void submit(Estado s, PoseStack pose, SubmitNodeCollector colector, CameraRenderState camara) {
        if (s.salida <= 0.01F || s.estallo) {
            return;
        }
        pose.pushPose();
        float bajar = (float) (GlifoTemploEntity.ALTO * (1.0F - s.salida));
        if (s.rota >= 0.0F) {
            // Rota: se viene abajo y se inclina, hundiendose en su polvo.
            bajar += (float) (GlifoTemploEntity.ALTO * s.rota * s.rota);
        }
        pose.translate(0.0, -bajar, 0.0);
        if (s.tiembla > 0.0F) {
            float k = s.tiembla * 0.08F;
            pose.translate(Mth.sin(s.tiempo * 3.1F) * k, 0.0, Mth.cos(s.tiempo * 2.7F) * k);
        }
        pose.mulPose(Axis.YP.rotationDegrees(180.0F - s.rumbo));
        if (s.rota >= 0.0F) {
            pose.mulPose(Axis.XP.rotationDegrees(14.0F * s.rota));
        }
        int luz = s.lightCoords;
        colector.submitCustomGeometry(pose, PIEDRA, (p, buf) -> RajangDibujo.emitir(buf, p, COLUMNA, 255, 255, 255, 255, luz));
        colector.submitCustomGeometry(pose, GLIFOS, (p, buf) -> RajangDibujo.emitir(buf, p, PANELES[s.glifo], 255, 255, 255, 255, luz));
        if (s.rota < 0.0F) {
            // El glifo encendido, que respira muy despacio (Juan: que no parpadee tan rapido); igual en todas.
            int a = (int) (220 + 30 * Mth.sin(s.tiempo * 0.035F));
            colector.submitCustomGeometry(pose, BRILLO, (p, buf) ->
                    RajangDibujo.emitir(buf, p, BRILLOS[s.glifo], a, a, a, 255, AeralisDibujo.A_PLENA_LUZ));
        }
        if (s.golpes > 0) {
            int e = Mth.clamp(s.golpes - 1, 0, 2);
            colector.submitCustomGeometry(pose, GRIETAS, (p, buf) -> RajangDibujo.emitir(buf, p, RAJAS[e], 255, 255, 255, 255, luz));
        }
        pose.popPose();
        super.submit(s, pose, colector, camara);
    }
}
