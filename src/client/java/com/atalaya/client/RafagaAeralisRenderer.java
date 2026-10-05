package com.atalaya.client;

import com.atalaya.Atalaya;
import com.atalaya.entity.RafagaAeralisEntity;
import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.math.Axis;
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
 * Una rafaga: la bola de viento en espiral (rafaga.png), siempre de cara a la
 * camara y girando, con un halo mas grande que gira al reves. Late un poco,
 * como el aire comprimido que es.
 */
public class RafagaAeralisRenderer extends EntityRenderer<RafagaAeralisEntity, RafagaAeralisRenderer.Estado> {

    private static final RenderType TIPO = RenderTypes.entityTranslucentEmissive(
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "textures/entity/aeralis/rafaga.png"));

    public static class Estado extends EntityRenderState {
        public float edad;
    }

    public RafagaAeralisRenderer(EntityRendererProvider.Context contexto) {
        super(contexto);
    }

    @Override
    public Estado createRenderState() {
        return new Estado();
    }

    @Override
    public void extractRenderState(RafagaAeralisEntity r, Estado s, float parcial) {
        super.extractRenderState(r, s, parcial);
        s.edad = r.tickCount + parcial;
    }

    @Override
    public void submit(Estado s, PoseStack pose, SubmitNodeCollector colector, CameraRenderState camara) {
        float late = 1.0F + 0.08F * Mth.sin(s.edad * 0.9F);
        pose.pushPose();
        pose.translate(0.0F, 0.6F, 0.0F);
        pose.mulPose(camara.orientation);
        pose.pushPose();
        pose.mulPose(Axis.ZP.rotation(s.edad * 0.35F));
        float m = 0.85F * late;
        colector.submitCustomGeometry(pose, TIPO, (p, buf) ->
                AeralisDibujo.cara(buf, p, Vec3.ZERO, new Vec3(m, 0, 0), new Vec3(0, m, 0), 255, 255, 255, 240,
                        AeralisDibujo.A_PLENA_LUZ));
        pose.popPose();
        pose.mulPose(Axis.ZP.rotation(-s.edad * 0.2F));
        float h = 1.35F * late;
        colector.submitCustomGeometry(pose, TIPO, (p, buf) ->
                AeralisDibujo.cara(buf, p, Vec3.ZERO, new Vec3(h, 0, 0), new Vec3(0, h, 0), 200, 230, 255, 110,
                        AeralisDibujo.A_PLENA_LUZ));
        pose.popPose();
        super.submit(s, pose, colector, camara);
    }
}
