package com.atalaya.client;

import com.atalaya.Atalaya;
import com.mojang.blaze3d.vertex.PoseStack;
import net.minecraft.client.renderer.SubmitNodeCollector;
import net.minecraft.client.renderer.entity.RenderLayerParent;
import net.minecraft.client.renderer.entity.layers.RenderLayer;
import net.minecraft.client.renderer.rendertype.RenderType;
import net.minecraft.client.renderer.rendertype.RenderTypes;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.resources.Identifier;
import net.minecraft.util.ARGB;

/**
 * Los Ocelos de Aeralis (el minijuego de "luz roja, luz verde"): cuando miran,
 * los ocelos de sus alas son ojos abiertos (aeralis_minijuegos.py,
 * aeralis_ocelos.png: va sobre el mismo atlas que su piel, solo en los ocelos),
 * rojos, con su halo y brillando sin luz. Se encienden con lo abiertos que esten
 * (el cliente lo suaviza). Justo antes de abrirse estan entornados, de ambar
 * (aeralis_ocelos_aviso.png), y laten.
 */
public class AeralisOcelosLayer extends RenderLayer<AeralisRenderState, AeralisModel> {

    private static final RenderType OJOS = RenderTypes.entityTranslucentEmissive(
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "textures/entity/aeralis/aeralis_ocelos.png"));
    private static final RenderType ENTORNADOS = RenderTypes.entityTranslucentEmissive(
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "textures/entity/aeralis/aeralis_ocelos_aviso.png"));

    public AeralisOcelosLayer(RenderLayerParent<AeralisRenderState, AeralisModel> padre) {
        super(padre);
    }

    @Override
    public void submit(PoseStack pose, SubmitNodeCollector colector, int luz, AeralisRenderState s, float yRot, float xRot) {
        if (s.deathTime > 0) {
            return;
        }
        if (s.ocelosAviso) {
            float late = 0.75F + 0.25F * net.minecraft.util.Mth.sin(s.ocelosReloj * 1.2F);
            colector.order(2).submitModel(getParentModel(), s, pose, ENTORNADOS, AeralisDibujo.A_PLENA_LUZ, OverlayTexture.NO_OVERLAY,
                    ARGB.colorFromFloat(late, 1.0F, 1.0F, 1.0F), null, s.outlineColor, null);
            return;
        }
        if (s.ocelos <= 0.02F) {
            return;
        }
        float k = Math.min(1.0F, s.ocelos);
        colector.order(2).submitModel(getParentModel(), s, pose, OJOS, AeralisDibujo.A_PLENA_LUZ, OverlayTexture.NO_OVERLAY,
                ARGB.colorFromFloat(k, 1.0F, 1.0F, 1.0F), null, s.outlineColor, null);
    }
}
