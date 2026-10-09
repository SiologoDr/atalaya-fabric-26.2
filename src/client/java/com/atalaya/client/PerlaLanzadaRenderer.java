package com.atalaya.client;

import com.atalaya.entity.PerlaLanzadaEntity;
import com.mojang.blaze3d.vertex.PoseStack;
import net.minecraft.client.renderer.SubmitNodeCollector;
import net.minecraft.client.renderer.entity.EntityRenderer;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.state.EntityRenderState;
import net.minecraft.client.renderer.state.level.CameraRenderState;
import net.minecraft.util.Mth;

/** Una Perla del Abismo que vuela a su corazon: una perla blanca que brilla, con su halo cian. */
public class PerlaLanzadaRenderer extends EntityRenderer<PerlaLanzadaEntity, PerlaLanzadaRenderer.Estado> {

    public static class Estado extends EntityRenderState {
        public float edad;
    }

    public PerlaLanzadaRenderer(EntityRendererProvider.Context contexto) {
        super(contexto);
    }

    @Override
    public Estado createRenderState() {
        return new Estado();
    }

    @Override
    public void extractRenderState(PerlaLanzadaEntity e, Estado s, float parcial) {
        super.extractRenderState(e, s, parcial);
        s.edad = e.tickCount + parcial;
    }

    @Override
    protected boolean affectedByCulling(PerlaLanzadaEntity e) {
        return false;
    }

    @Override
    public void submit(Estado s, PoseStack pose, SubmitNodeCollector colector, CameraRenderState camara) {
        float e = s.edad;
        float late = 1.0F + 0.12F * Mth.sin(e * 0.8F);
        pose.pushPose();
        pose.mulPose(camara.orientation);
        colector.submitCustomGeometry(pose, NereaDibujo.CORAZON, (p, buf) -> {
            NereaDibujo.vertice(buf, p, -0.7 * late, -0.7 * late, 0, 0, 1, 0x7FE8FF, 200, 0, 0, 1);
            NereaDibujo.vertice(buf, p, 0.7 * late, -0.7 * late, 0, 1, 1, 0x7FE8FF, 200, 0, 0, 1);
            NereaDibujo.vertice(buf, p, 0.7 * late, 0.7 * late, 0, 1, 0, 0x7FE8FF, 200, 0, 0, 1);
            NereaDibujo.vertice(buf, p, -0.7 * late, 0.7 * late, 0, 0, 0, 0x7FE8FF, 200, 0, 0, 1);
            NereaDibujo.vertice(buf, p, -0.3, -0.3, 0.01, 0, 1, 0xFFFFFF, 255, 0, 0, 1);
            NereaDibujo.vertice(buf, p, 0.3, -0.3, 0.01, 1, 1, 0xFFFFFF, 255, 0, 0, 1);
            NereaDibujo.vertice(buf, p, 0.3, 0.3, 0.01, 1, 0, 0xFFFFFF, 255, 0, 0, 1);
            NereaDibujo.vertice(buf, p, -0.3, 0.3, 0.01, 0, 0, 0xFFFFFF, 255, 0, 0, 1);
        });
        pose.popPose();
        super.submit(s, pose, colector, camara);
    }
}
