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
 * Una rafaga de la Caceria, desde el remake: una polilla de viento
 * (polilla.png, tenida del color de la fase) que bate las alas de cara a la
 * camara, con un halo de aire que gira detras (rafaga.png) y tres ecos que se
 * quedan atras en su camino: la estela. Se revienta en el aire, como antes.
 */
public class RafagaAeralisRenderer extends EntityRenderer<RafagaAeralisEntity, RafagaAeralisRenderer.Estado> {

    private static final RenderType POLILLA = RenderTypes.entityTranslucentEmissive(
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "textures/entity/aeralis/polilla.png"));
    private static final RenderType HALO = RenderTypes.entityTranslucentEmissive(
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "textures/entity/aeralis/rafaga.png"));

    public static class Estado extends EntityRenderState {
        public float edad;
        public int color = 0xFFFFFF;
        public Vec3 vel = Vec3.ZERO;
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
        s.color = AeralisDibujo.fase(r.getFase());
        s.vel = r.getDeltaMovement();
    }

    @Override
    public void submit(Estado s, PoseStack pose, SubmitNodeCollector colector, CameraRenderState camara) {
        int c = s.color;
        int rr = AeralisDibujo.r(c), gg = AeralisDibujo.g(c), bb = AeralisDibujo.b(c);
        Vec3 atras = s.vel.lengthSqr() > 1.0E-4 ? s.vel.normalize().scale(-1.4) : Vec3.ZERO;
        // La estela: tres ecos de la polilla que se apagan hacia atras.
        for (int k = 3; k >= 0; k--) {
            float bate = 0.35F + 0.65F * Math.abs(Mth.sin((s.edad - k * 1.5F) * 0.9F));
            float m = 1.5F * (1.0F - 0.12F * k);
            int alfa = new int[]{250, 120, 60, 25}[k];
            pose.pushPose();
            pose.translate(atras.x * k, 0.6 + atras.y * k, atras.z * k);
            pose.mulPose(camara.orientation);
            pose.mulPose(Axis.ZP.rotation(0.25F * Mth.sin(s.edad * 0.2F)));
            colector.submitCustomGeometry(pose, POLILLA, (p, buf) ->
                    AeralisDibujo.cara(buf, p, Vec3.ZERO, new Vec3(m * bate, 0, 0), new Vec3(0, m, 0), rr, gg, bb, alfa,
                            AeralisDibujo.A_PLENA_LUZ));
            if (k == 0) {
                pose.mulPose(Axis.ZP.rotation(-s.edad * 0.2F));
                float h = 2.2F;
                colector.submitCustomGeometry(pose, HALO, (p, buf) ->
                        AeralisDibujo.cara(buf, p, new Vec3(0, 0, -0.02), new Vec3(h, 0, 0), new Vec3(0, h, 0), rr, gg, bb, 90,
                                AeralisDibujo.A_PLENA_LUZ));
            }
            pose.popPose();
        }
        super.submit(s, pose, colector, camara);
    }
}
