package com.atalaya.client;

import com.atalaya.Atalaya;
import com.atalaya.entity.FuenteSolarEntity;
import com.atalaya.entity.NovilisEntity;
import com.atalaya.entity.NovilisGeometria;
import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.math.Axis;
import net.minecraft.client.model.EntityModel;
import net.minecraft.client.model.geom.ModelLayerLocation;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.renderer.SubmitNodeCollector;
import net.minecraft.client.renderer.entity.EntityRenderer;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.state.EntityRenderState;
import net.minecraft.client.renderer.rendertype.RenderType;
import net.minecraft.client.renderer.rendertype.RenderTypes;
import net.minecraft.client.renderer.state.level.CameraRenderState;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.resources.Identifier;
import net.minecraft.util.ARGB;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.phys.Vec3;
import org.jspecify.annotations.Nullable;

/**
 * Una fuente solar: el obelisco de novilis_props.py (5 bloques), su sol
 * flotando sobre la cuna y el haz de fuego que le manda a Novilis mientras
 * carga. Rota, se apaga: sin sol ni haz, el tocon con la cuna rajada.
 */
public class FuenteSolarRenderer extends EntityRenderer<FuenteSolarEntity, FuenteSolarRenderer.Estado> {

    public static final ModelLayerLocation CAPA = new ModelLayerLocation(
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "fuente_solar"), "main");
    public static final ModelLayerLocation CAPA_ROTA = new ModelLayerLocation(
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "fuente_solar"), "rota");

    private static final RenderType PIEL = RenderTypes.entityCutout(Identifier.fromNamespaceAndPath(Atalaya.MOD_ID,
            "textures/entity/novilis/fuente.png"));
    private static final RenderType BRILLO = RenderTypes.eyes(Identifier.fromNamespaceAndPath(Atalaya.MOD_ID,
            "textures/entity/novilis/fuente_brillo.png"));
    /** El centro del sol, sobre la base (y = -60 en la malla: 84 px por encima de y = 24). */
    private static final double ALTO_SOL = 84.0 / 16.0;

    public static class Estado extends EntityRenderState {
        public float edad;
        public float rumbo;
        public boolean rota;
        public float desdeGolpe = 100.0F;
        public int fase = 3;
        /** El pecho de Novilis, relativo a la fuente (el final del haz). */
        public @Nullable Vec3 pecho;
    }

    public static class Modelo extends EntityModel<Estado> {
        public Modelo(ModelPart raiz) {
            super(raiz);
        }
    }

    private final Modelo entera;
    private final Modelo rota;

    public FuenteSolarRenderer(EntityRendererProvider.Context contexto) {
        super(contexto);
        this.entera = new Modelo(contexto.bakeLayer(CAPA));
        this.rota = new Modelo(contexto.bakeLayer(CAPA_ROTA));
    }

    @Override
    public Estado createRenderState() {
        return new Estado();
    }

    @Override
    public void extractRenderState(FuenteSolarEntity f, Estado s, float parcial) {
        super.extractRenderState(f, s, parcial);
        s.edad = f.tickCount + parcial;
        s.rumbo = f.getYRot();
        s.rota = f.isRoto();
        s.desdeGolpe = f.tickCount - f.ultimoGolpe + parcial;
        s.pecho = null;
        Entity d = f.level().getEntity(f.getIdDueno());
        if (d instanceof NovilisEntity n) {
            s.fase = n.tieneFuria() ? 5 : n.fase();
            Vec3 pies = n.getPosition(parcial);
            s.pecho = NovilisEntity.puntoMundo(NovilisGeometria.PECHO_FUENTES, pies, n.yBodyRot).subtract(f.getPosition(parcial));
        }
    }

    @Override
    protected boolean affectedByCulling(FuenteSolarEntity f) {
        return false;
    }

    @Override
    public void submit(Estado s, PoseStack pose, SubmitNodeCollector colector, CameraRenderState camara) {
        float k = Mth.clamp(s.edad / FuenteSolarEntity.SALE, 0.0F, 1.0F);
        float sube = (1.0F - (1.0F - k) * (1.0F - k)) * 5.0F - 5.0F;
        float tiembla = s.desdeGolpe < 6 ? 0.06F * Mth.sin(s.desdeGolpe * 2.6F) * (6 - s.desdeGolpe) : 0.0F;
        pose.pushPose();
        pose.translate(tiembla, sube, 0.0F);
        pose.mulPose(Axis.YP.rotationDegrees(180.0F - s.rumbo));
        pose.scale(-1.0F, -1.0F, 1.0F);
        pose.translate(0.0F, -1.501F, 0.0F);
        Modelo m = s.rota ? rota : entera;
        colector.order(1).submitModel(m, s, pose, PIEL, s.lightCoords, OverlayTexture.NO_OVERLAY, s.outlineColor, null);
        if (!s.rota) {
            float late = 0.7F + 0.3F * Mth.sin(s.edad * 0.3F);
            colector.order(2).submitModel(m, s, pose, BRILLO, NovilisDibujo.A_PLENA_LUZ, OverlayTexture.NO_OVERLAY,
                    ARGB.colorFromFloat(late, late, late, late), null, s.outlineColor, null);
        }
        pose.popPose();
        if (!s.rota && k >= 1.0F) {
            Vec3 ojo = camara.pos.subtract(s.x, s.y, s.z);
            Vec3 sol = new Vec3(0, ALTO_SOL + 0.15 * Mth.sin(s.edad * 0.12F), 0);
            int color = NovilisDibujo.color(s.fase);
            colector.submitCustomGeometry(pose, NovilisDibujo.SOL, (p, buf) -> NovilisDibujo.sol(buf, p, sol, ojo, 0.8F, s.edad, color, 240));
            if (s.pecho != null) {
                // El haz de fuego que le manda: en arco, de su sol al pecho de Novilis.
                Vec3 fin = s.pecho;
                Vec3 medio = sol.add(fin).scale(0.5).add(0, 3.0, 0);
                colector.submitCustomGeometry(pose, NovilisDibujo.HAZ, (p, buf) -> {
                    Vec3 antes = sol;
                    for (int i = 1; i <= 12; i++) {
                        float t = i / 12.0F;
                        Vec3 q = sol.scale((1 - t) * (1 - t)).add(medio.scale(2 * (1 - t) * t)).add(fin.scale(t * t));
                        NovilisDibujo.haz(buf, p, antes, q, ojo, 0.35F, -s.edad * 0.3F + i, color, 200);
                        antes = q;
                    }
                });
            }
        }
        super.submit(s, pose, colector, camara);
    }
}
