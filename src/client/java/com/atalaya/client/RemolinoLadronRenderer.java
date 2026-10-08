package com.atalaya.client;

import com.atalaya.Atalaya;
import com.atalaya.entity.RemolinoLadronEntity;
import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import com.mojang.math.Axis;
import net.minecraft.client.renderer.SubmitNodeCollector;
import net.minecraft.client.renderer.entity.EntityRenderer;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.state.EntityRenderState;
import net.minecraft.client.renderer.item.ItemModelResolver;
import net.minecraft.client.renderer.item.ItemStackRenderState;
import net.minecraft.client.renderer.rendertype.RenderType;
import net.minecraft.client.renderer.rendertype.RenderTypes;
import net.minecraft.client.renderer.state.level.CameraRenderState;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.resources.Identifier;
import net.minecraft.util.Mth;
import net.minecraft.world.item.ItemDisplayContext;

/**
 * El remolino de la Rafaga Ladrona: el arma robada girando en el centro y tres
 * anillos de luz del color de la fase alrededor, uno por golpe que le falta
 * (como los tornados). Las motas de viento en espiral las echa la entidad.
 */
public class RemolinoLadronRenderer extends EntityRenderer<RemolinoLadronEntity, RemolinoLadronRenderer.Estado> {

    private static final RenderType ARO = RenderTypes.entityTranslucentEmissive(
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "textures/entity/aeralis/rayo.png"));

    public static class Estado extends EntityRenderState {
        public final ItemStackRenderState arma = new ItemStackRenderState();
        public int golpes;
        public int color = 0xFFFFFF;
        public float edad;
    }

    private final ItemModelResolver modelos;

    public RemolinoLadronRenderer(EntityRendererProvider.Context contexto) {
        super(contexto);
        this.modelos = contexto.getItemModelResolver();
    }

    @Override
    public Estado createRenderState() {
        return new Estado();
    }

    @Override
    public void extractRenderState(RemolinoLadronEntity r, Estado s, float parcial) {
        super.extractRenderState(r, s, parcial);
        modelos.updateForNonLiving(s.arma, r.getBotin(), ItemDisplayContext.GROUND, r);
        s.golpes = r.getGolpes();
        s.color = AeralisDibujo.claro(AeralisDibujo.fase(r.getFase()), 0.25F);
        s.edad = r.tickCount + parcial;
    }

    @Override
    protected boolean affectedByCulling(RemolinoLadronEntity r) {
        return false;
    }

    @Override
    public void submit(Estado s, PoseStack pose, SubmitNodeCollector colector, CameraRenderState camara) {
        if (!s.arma.isEmpty()) {
            pose.pushPose();
            pose.translate(0.0F, 0.3F + 0.08F * Mth.sin(s.edad * 0.2F), 0.0F);
            pose.mulPose(Axis.YP.rotationDegrees(s.edad * 24.0F));
            pose.mulPose(Axis.ZP.rotationDegrees(25.0F * Mth.sin(s.edad * 0.15F)));
            pose.scale(1.7F, 1.7F, 1.7F);
            s.arma.submit(pose, colector, s.lightCoords, OverlayTexture.NO_OVERLAY, s.outlineColor);
            pose.popPose();
        }
        int quedan = Math.max(0, RemolinoLadronEntity.GOLPES - s.golpes);
        if (quedan > 0) {
            float giro = s.edad * 0.25F;
            int c = s.color;
            colector.submitCustomGeometry(pose, ARO, (p, buf) -> {
                for (int i = 0; i < quedan; i++) {
                    float y = 0.1F + 0.35F * i;
                    float r = 0.8F + 0.15F * i + 0.05F * Mth.sin(s.edad * 0.4F + i);
                    anillo(buf, p, r, y, giro * (i % 2 == 0 ? 1 : -1) + i, c, 235);
                }
            });
        }
        super.submit(s, pose, colector, camara);
    }

    /** Un anillo de luz horizontal a la altura y (como los de los tornados). */
    private static void anillo(VertexConsumer buf, PoseStack.Pose p, float r, float y, float giro, int c, int alfa) {
        float grueso = 0.09F;
        for (int i = 0; i < 20; i++) {
            double a0 = giro + i * Mth.TWO_PI / 20, a1 = giro + (i + 1) * Mth.TWO_PI / 20;
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
}
