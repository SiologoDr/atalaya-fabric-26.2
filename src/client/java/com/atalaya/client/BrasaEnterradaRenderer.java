package com.atalaya.client;

import com.atalaya.Atalaya;
import com.atalaya.entity.BrasaEnterradaEntity;
import com.mojang.blaze3d.vertex.PoseStack;
import net.minecraft.client.renderer.SubmitNodeCollector;
import net.minecraft.client.renderer.entity.EntityRenderer;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.state.EntityRenderState;
import net.minecraft.client.renderer.rendertype.RenderType;
import net.minecraft.client.renderer.rendertype.RenderTypes;
import net.minecraft.client.renderer.state.level.CameraRenderState;
import net.minecraft.resources.Identifier;
import net.minecraft.util.Mth;

/**
 * Una brasa de Frio o Caliente: enterrada no se ve (la busca el termometro).
 * Al sacarla, la tierra se raja y brilla (brasa_grieta.png) y se va apagando;
 * al reventar, la grieta se abre roja y grande.
 */
public class BrasaEnterradaRenderer extends EntityRenderer<BrasaEnterradaEntity, BrasaEnterradaRenderer.Estado> {

    private static final RenderType GRIETA = RenderTypes.entityTranslucent(
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "textures/entity/novilis/brasa_grieta.png"));

    public static class Estado extends EntityRenderState {
        /** Lo que hace que la sacaron o que revento (ticks); -1 si sigue enterrada. */
        public float hallada = -1.0F;
        public float revienta = -1.0F;
        public float giro;
    }

    public BrasaEnterradaRenderer(EntityRendererProvider.Context contexto) {
        super(contexto);
    }

    @Override
    public Estado createRenderState() {
        return new Estado();
    }

    @Override
    public void extractRenderState(BrasaEnterradaEntity b, Estado s, float parcial) {
        super.extractRenderState(b, s, parcial);
        s.hallada = b.getHallada() >= 0 ? b.tickCount - b.getHallada() + parcial : -1.0F;
        s.revienta = b.getRevienta() >= 0 ? b.tickCount - b.getRevienta() + parcial : -1.0F;
        s.giro = b.getYRot() * Mth.DEG_TO_RAD;
    }

    @Override
    public void submit(Estado s, PoseStack pose, SubmitNodeCollector colector, CameraRenderState camara) {
        if (s.hallada >= 0.0F) {
            float k = Mth.clamp(s.hallada / BrasaEnterradaEntity.HALLADA_DURA, 0.0F, 1.0F);
            float m = 1.1F + 0.5F * Mth.clamp(s.hallada / 6.0F, 0.0F, 1.0F);
            int alfa = (int) (240 * (1.0F - k * k));
            colector.submitCustomGeometry(pose, GRIETA, (p, buf) ->
                    NereaDibujo.suelo(buf, p, 0.0, 0.04, 0.0, m, s.giro, 0xFFFFFF, alfa));
        } else if (s.revienta >= 0.0F) {
            float k = Mth.clamp(s.revienta / BrasaEnterradaEntity.REVIENTA_DURA, 0.0F, 1.0F);
            float m = 1.6F + 2.0F * Mth.clamp(s.revienta / 5.0F, 0.0F, 1.0F);
            int alfa = (int) (250 * (1.0F - k));
            colector.submitCustomGeometry(pose, GRIETA, (p, buf) ->
                    NereaDibujo.suelo(buf, p, 0.0, 0.04, 0.0, m, s.giro, 0xFF6A3A, alfa));
        }
        super.submit(s, pose, colector, camara);
    }
}
