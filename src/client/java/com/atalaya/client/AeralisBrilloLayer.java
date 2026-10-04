package com.atalaya.client;

import com.atalaya.Atalaya;
import com.atalaya.entity.AeralisEntity;
import com.mojang.blaze3d.vertex.PoseStack;
import net.minecraft.client.renderer.SubmitNodeCollector;
import net.minecraft.client.renderer.entity.RenderLayerParent;
import net.minecraft.client.renderer.entity.layers.RenderLayer;
import net.minecraft.client.renderer.rendertype.RenderType;
import net.minecraft.client.renderer.rendertype.RenderTypes;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.resources.Identifier;
import net.minecraft.util.ARGB;
import net.minecraft.util.Mth;

/**
 * Lo que brilla de Aeralis: los ojos compuestos, las puntas de las antenas, el
 * ojo de la tormenta y las vetas de las alas. Cambia con la fase (del cian al
 * anil, al violeta con rayos y al magenta de la tormenta) y, liberada, en oro.
 *
 * Dormida, respira despacio; aturdida, parpadea; en el silencio del Juicio se
 * apaga casi del todo.
 */
public class AeralisBrilloLayer extends RenderLayer<AeralisRenderState, AeralisModel> {

    private static final RenderType[] FASES = new RenderType[4];

    static {
        for (int i = 0; i < 4; i++) {
            FASES[i] = RenderTypes.eyes(Identifier.fromNamespaceAndPath(Atalaya.MOD_ID,
                    "textures/entity/aeralis/aeralis_brillo_f" + (i + 1) + ".png"));
        }
    }
    private static final RenderType LIBRE = RenderTypes.eyes(
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "textures/entity/aeralis/aeralis_brillo_libre.png"));

    public AeralisBrilloLayer(RenderLayerParent<AeralisRenderState, AeralisModel> padre) {
        super(padre);
    }

    @Override
    public void submit(PoseStack pose, SubmitNodeCollector colector, int luz, AeralisRenderState s, float yRot, float xRot) {
        float k = 1.0F - s.disolver;
        if (s.estado == AeralisEntity.ATURDIDA && ((int) s.ageInTicks % 5) < 2) {
            k *= 0.3F;
        }
        if (s.estado == AeralisEntity.DORMIDA) {
            k *= 0.5F + 0.25F * Mth.sin(s.ageInTicks * 0.07F);
        }
        if (s.estado == AeralisEntity.JUICIO_SUBE) {
            k *= 0.25F;
        }
        if (k <= 0.01F) {
            return;
        }
        colector.order(1).submitModel(getParentModel(), s, pose, s.libre ? LIBRE : FASES[Math.clamp(s.fase, 1, 4) - 1], luz,
                OverlayTexture.NO_OVERLAY, ARGB.colorFromFloat(k, k, k, k), null, s.outlineColor, null);
    }
}
