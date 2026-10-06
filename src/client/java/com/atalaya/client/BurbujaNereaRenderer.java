package com.atalaya.client;

import com.atalaya.Atalaya;
import com.atalaya.entity.BurbujaNereaEntity;
import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.math.Axis;
import net.minecraft.client.model.EntityModel;
import net.minecraft.client.model.geom.ModelLayerLocation;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.model.geom.PartPose;
import net.minecraft.client.model.geom.builders.CubeListBuilder;
import net.minecraft.client.model.geom.builders.LayerDefinition;
import net.minecraft.client.model.geom.builders.MeshDefinition;
import net.minecraft.client.model.geom.builders.PartDefinition;
import net.minecraft.client.renderer.SubmitNodeCollector;
import net.minecraft.client.renderer.entity.EntityRenderer;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.state.EntityRenderState;
import net.minecraft.client.renderer.rendertype.RenderType;
import net.minecraft.client.renderer.rendertype.RenderTypes;
import net.minecraft.client.renderer.state.level.CameraRenderState;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.resources.Identifier;
import net.minecraft.util.Mth;
import net.minecraft.world.level.ClipContext;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;

/**
 * La burbuja bomba: una pompa de agua translucida con el corazon maldito
 * latiendo dentro (desde el remake; antes, un nucleo magenta). Tiembla como
 * gelatina mientras flota y marca en el suelo, con un aro de espuma, hasta
 * donde llega su reventon.
 */
public class BurbujaNereaRenderer extends EntityRenderer<BurbujaNereaEntity, BurbujaNereaRenderer.Estado> {

    public static final ModelLayerLocation CAPA = new ModelLayerLocation(
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "burbuja_nerea"), "main");

    private static final RenderType POMPA = RenderTypes.entityTranslucent(
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "textures/entity/nerea/burbuja.png"));

    public static class Estado extends EntityRenderState {
        /** Hasta donde llega el reventon (bloques). */
        public float radio;
        /** El suelo bajo ella, relativo a ella (negativo), o NaN si queda muy lejos. */
        public float suelo = Float.NaN;
    }

    public static class Modelo extends EntityModel<Estado> {

        private final ModelPart pompa;
        private final ModelPart nucleo;

        public Modelo(ModelPart raiz) {
            super(raiz);
            this.pompa = raiz.getChild("pompa");
            this.nucleo = raiz.getChild("nucleo");
        }

        public static LayerDefinition crear() {
            MeshDefinition malla = new MeshDefinition();
            PartDefinition raiz = malla.getRoot();
            raiz.addOrReplaceChild("pompa",
                    CubeListBuilder.create().texOffs(0, 0).addBox(-6.0F, -6.0F, -6.0F, 12.0F, 12.0F, 12.0F),
                    PartPose.offset(0.0F, 16.0F, 0.0F));
            raiz.addOrReplaceChild("nucleo",
                    CubeListBuilder.create().texOffs(0, 24).addBox(-2.0F, -2.0F, -2.0F, 4.0F, 4.0F, 4.0F),
                    PartPose.offset(0.0F, 16.0F, 0.0F));
            return LayerDefinition.create(malla, 64, 32);
        }

        @Override
        public void setupAnim(Estado s) {
            super.setupAnim(s);
            float t = s.ageInTicks;
            // Gelatina: se estira en un eje mientras se encoge en el otro.
            float a = 0.07F * Mth.sin(t * 0.35F);
            pompa.xScale = 1.0F + a;
            pompa.yScale = 1.0F - a;
            pompa.zScale = 1.0F + a * 0.5F;
            nucleo.visible = false;
            nucleo.xRot = t * 0.11F;
            nucleo.yRot = t * 0.07F;
            float k = 1.0F + 0.25F * Math.max(0.0F, Mth.sin(t * 0.4F));
            nucleo.xScale = k;
            nucleo.yScale = k;
            nucleo.zScale = k;
        }
    }

    private final Modelo modelo;

    public BurbujaNereaRenderer(EntityRendererProvider.Context contexto) {
        super(contexto);
        this.modelo = new Modelo(contexto.bakeLayer(CAPA));
    }

    @Override
    public Estado createRenderState() {
        return new Estado();
    }

    @Override
    public void extractRenderState(BurbujaNereaEntity b, Estado s, float parcial) {
        super.extractRenderState(b, s, parcial);
        s.radio = (float) BurbujaNereaEntity.radio(b.getFase());
        Vec3 aqui = b.getPosition(parcial);
        BlockHitResult choque = b.level().clip(new ClipContext(aqui, aqui.add(0, -12, 0), ClipContext.Block.COLLIDER,
                ClipContext.Fluid.NONE, b));
        s.suelo = choque.getType() == HitResult.Type.MISS ? Float.NaN : (float) (choque.getLocation().y - aqui.y);
    }

    @Override
    protected boolean affectedByCulling(BurbujaNereaEntity b) {
        return false;
    }

    @Override
    public void submit(Estado s, PoseStack pose, SubmitNodeCollector colector, CameraRenderState camara) {
        // El corazon maldito dentro, de cara a quien mira, latiendo.
        Vec3 ojo = camara.pos.subtract(s.x, s.y, s.z);
        float late = 0.2F + 0.05F * Math.max(0.0F, Mth.sin(s.ageInTicks * 0.45F));
        colector.order(1).submitCustomGeometry(pose, NereaDibujo.CORAZON, (p, buf) ->
                NereaDibujo.cartel(buf, p, new Vec3(0, 0.5, 0), ojo, late, 0.0F, 0xFFFFFF, 255));
        pose.pushPose();
        pose.mulPose(Axis.YP.rotationDegrees(s.ageInTicks * 2.0F));
        pose.scale(-1.0F, -1.0F, 1.0F);
        pose.translate(0.0F, -1.501F, 0.0F);
        colector.order(2).submitModel(modelo, s, pose, POMPA, s.lightCoords, OverlayTexture.NO_OVERLAY, s.outlineColor, null);
        pose.popPose();
        if (!Float.isNaN(s.suelo)) {
            // El aro de espuma en el suelo: hasta donde revienta.
            float m = s.radio / NereaDibujo.ARO_EN_TEXTURA;
            colector.submitCustomGeometry(pose, NereaDibujo.ARO, (p, buf) ->
                    NereaDibujo.suelo(buf, p, 0.0, s.suelo + 0.06, 0.0, m, s.ageInTicks * 0.04F, 0xFFD8EC, 150));
        }
        super.submit(s, pose, colector, camara);
    }
}
