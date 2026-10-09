package com.atalaya.client;

import com.atalaya.Atalaya;
import com.atalaya.entity.LosaJadeEntity;
import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.math.Axis;
import java.util.ArrayList;
import java.util.List;
import java.util.Random;
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
 * Una losa de Suelo que se Hunde (losa.png): jade pulido con el filo de oro y
 * el rombo del templo. Pisada, se le abren las grietas (losa_grietas.png) con
 * la luz verde dentro y tiembla; al segundo cae girando y se apaga. Debajo, en
 * el suelo del foso, cinco pinchos de jade (los de la trampa de oro), que se
 * ven entre las losas que faltan. Sube del suelo al empezar.
 */
public class LosaJadeRenderer extends EntityRenderer<LosaJadeEntity, LosaJadeRenderer.Estado> {

    private static final RenderType LOSA = RenderTypes.entityCutout(tex("losa"));
    private static final RenderType GRIETAS = RenderTypes.entityCutout(tex("losa_grietas"));
    private static final RenderType PINCHOS = RenderTypes.entityCutout(tex("trampa"));
    private static final List<RajangDibujo.Cara> CAJA = new ArrayList<>();
    @SuppressWarnings("unchecked")
    private static final List<RajangDibujo.Cara>[] RAJAS = new List[3];

    static {
        double m = LosaJadeEntity.LADO / 2.0;
        double g = LosaJadeEntity.GRUESO;
        RajangDibujo.caja(CAJA, -m, 0, -m, m, g, m, RajangDibujo.uv(0, 48 / 64.0F, 1, 56 / 64.0F), RajangDibujo.uv(0, 0, 1, 48 / 64.0F));
        for (int e = 0; e < 3; e++) {
            RAJAS[e] = new ArrayList<>();
            float v0 = e / 3.0F;
            float v1 = (e + 1) / 3.0F;
            Vec3 a = new Vec3(-m, g + 0.012, -m);
            Vec3 b = new Vec3(m, g + 0.012, -m);
            Vec3 c = new Vec3(m, g + 0.012, m);
            Vec3 d = new Vec3(-m, g + 0.012, m);
            RAJAS[e].add(new RajangDibujo.Cara(a, b, c, d, RajangDibujo.uv(0, v0, 1, v1)));
        }
    }

    private static Identifier tex(String nombre) {
        return Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "textures/entity/rajang/" + nombre + ".png");
    }

    public static class Estado extends EntityRenderState {
        public float subida;
        /** Ticks desde que la pisaron (-1: entera) y desde que cae (-1: en su sitio). */
        public float pisada = -1.0F;
        public float cae = -1.0F;
        public float hondo;
        public int semilla;
    }

    /** Los pinchos de debajo de cada losa (con su semilla, para que no sean todos iguales). */
    private final java.util.Map<Integer, List<RajangDibujo.Cara>> pinchos = new java.util.HashMap<>();

    public LosaJadeRenderer(EntityRendererProvider.Context contexto) {
        super(contexto);
    }

    /** Para no dejar de pintarla mientras se vean sus pinchos, abajo en el foso. */
    @Override
    protected net.minecraft.world.phys.AABB getBoundingBoxForCulling(LosaJadeEntity l) {
        return l.getBoundingBox().expandTowards(0.0, -l.getHondo() - 1.5, 0.0);
    }

    @Override
    public Estado createRenderState() {
        return new Estado();
    }

    @Override
    public void extractRenderState(LosaJadeEntity l, Estado s, float parcial) {
        super.extractRenderState(l, s, parcial);
        s.subida = l.subida(parcial);
        s.pisada = l.getPisada() >= 0 ? l.tickCount - l.getPisada() + parcial : -1.0F;
        s.cae = l.getCae() >= 0 ? l.tickCount - l.getCae() + parcial : -1.0F;
        s.hondo = l.getHondo();
        s.semilla = l.getSemilla();
    }

    private List<RajangDibujo.Cara> pinchos(int semilla) {
        if (pinchos.size() > 256) {
            pinchos.clear();
        }
        return pinchos.computeIfAbsent(semilla, k -> {
            List<RajangDibujo.Cara> out = new ArrayList<>();
            Random r = new Random(k);
            float[] uv = RajangDibujo.uv(48 / 64.0F, 16 / 64.0F, 1.0F, 32 / 64.0F);
            // Cinco por losa: uno en cada esquina y el del medio, mas alto.
            for (int i = 0; i < 5; i++) {
                double x = i == 4 ? 0 : (i % 2 == 0 ? -0.8 : 0.8) + (r.nextDouble() - 0.5) * 0.5;
                double z = i == 4 ? 0 : (i < 2 ? -0.8 : 0.8) + (r.nextDouble() - 0.5) * 0.5;
                double h = (i == 4 ? 1.2 : 0.8) + r.nextDouble() * 0.5;
                RajangDibujo.caja(out, x - 0.2, 0, z - 0.2, x + 0.2, h * 0.4, z + 0.2, uv, uv);
                RajangDibujo.caja(out, x - 0.13, h * 0.4, z - 0.13, x + 0.13, h * 0.75, z + 0.13, uv, uv);
                RajangDibujo.caja(out, x - 0.06, h * 0.75, z - 0.06, x + 0.06, h, z + 0.06, uv, uv);
            }
            return out;
        });
    }

    @Override
    public void submit(Estado s, PoseStack pose, SubmitNodeCollector colector, CameraRenderState camara) {
        int luz = s.lightCoords;
        // Los pinchos del foso, en el suelo de debajo.
        float sale = s.subida;
        if (sale > 0.01F) {
            List<RajangDibujo.Cara> ps = pinchos(s.semilla);
            pose.pushPose();
            pose.translate(0.0, -s.hondo - 1.3 * (1.0F - sale), 0.0);
            colector.submitCustomGeometry(pose, PINCHOS, (p, buf) -> RajangDibujo.emitir(buf, p, ps, 255, 255, 255, 255, luz));
            pose.popPose();
        }
        float caida = s.cae >= 0.0F ? Mth.clamp(s.cae / LosaJadeEntity.CAE, 0.0F, 1.0F) : 0.0F;
        if (caida >= 1.0F || s.subida <= 0.01F) {
            super.submit(s, pose, colector, camara);
            return;
        }
        pose.pushPose();
        // Sube del foso; cae con su peso, girando un poco.
        double y = -s.hondo * (1.0F - s.subida);
        if (s.cae >= 0.0F) {
            y -= 0.02 * s.cae * s.cae;
        }
        pose.translate(0.0, y, 0.0);
        if (s.pisada >= 0.0F && s.cae < 0.0F) {
            float k = Mth.clamp(s.pisada / LosaJadeEntity.CRUJE, 0.0F, 1.0F) * 0.05F;
            pose.translate(Mth.sin(s.pisada * 2.9F) * k, 0.0, Mth.cos(s.pisada * 3.3F) * k);
        }
        if (s.cae >= 0.0F) {
            pose.mulPose(Axis.XP.rotationDegrees(((s.semilla & 1) == 0 ? 1 : -1) * 25.0F * caida));
            pose.mulPose(Axis.ZP.rotationDegrees(((s.semilla & 2) == 0 ? 1 : -1) * 18.0F * caida));
        }
        int c = s.cae >= 0.0F ? (int) (255 * (1.0F - 0.5F * caida)) : 255;
        colector.submitCustomGeometry(pose, LOSA, (p, buf) -> RajangDibujo.emitir(buf, p, CAJA, c, c, c, 255, luz));
        if (s.pisada >= 0.0F) {
            int e = s.cae >= 0.0F ? 2 : Mth.clamp((int) (s.pisada / (LosaJadeEntity.CRUJE / 3.0F)), 0, 2);
            colector.submitCustomGeometry(pose, GRIETAS, (p, buf) ->
                    RajangDibujo.emitir(buf, p, RAJAS[e], 255, 255, 255, 255, AeralisDibujo.A_PLENA_LUZ));
        }
        pose.popPose();
        super.submit(s, pose, colector, camara);
    }
}
