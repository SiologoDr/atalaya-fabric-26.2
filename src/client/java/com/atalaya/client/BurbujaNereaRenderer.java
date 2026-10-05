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

/**
 * La burbuja bomba: una pompa de agua translucida con el nucleo de la
 * maldicion latiendo dentro, en magenta. Tiembla como gelatina mientras flota.
 */
public class BurbujaNereaRenderer extends EntityRenderer<BurbujaNereaEntity, BurbujaNereaRenderer.Estado> {

    public static final ModelLayerLocation CAPA = new ModelLayerLocation(
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "burbuja_nerea"), "main");

    private static final RenderType POMPA = RenderTypes.entityTranslucent(
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "textures/entity/nerea/burbuja.png"));
    private static final RenderType NUCLEO = RenderTypes.eyes(
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "textures/entity/nerea/burbuja_brillo.png"));

    public static class Estado extends EntityRenderState {
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
    public void submit(Estado s, PoseStack pose, SubmitNodeCollector colector, CameraRenderState camara) {
        pose.pushPose();
        pose.mulPose(Axis.YP.rotationDegrees(s.ageInTicks * 2.0F));
        pose.scale(-1.0F, -1.0F, 1.0F);
        pose.translate(0.0F, -1.501F, 0.0F);
        colector.order(1).submitModel(modelo, s, pose, NUCLEO, 0xF000F0, OverlayTexture.NO_OVERLAY, s.outlineColor, null);
        colector.order(2).submitModel(modelo, s, pose, POMPA, s.lightCoords, OverlayTexture.NO_OVERLAY, s.outlineColor, null);
        pose.popPose();
        super.submit(s, pose, colector, camara);
    }
}
