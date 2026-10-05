package com.atalaya.client;

import com.atalaya.Atalaya;
import com.atalaya.entity.NereaEntity;
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
 * Lo que brilla de Nerea a oscuras: los ojos y las puntas del tridente, el
 * corazon y la maldicion. Cambia con la fase: los ojos pasan de cian a violeta,
 * a magenta y a rojo, y las venas magenta se le extienden por el cuerpo.
 *
 * Al quedar liberado cambia de textura: ojos y puntas en oro, el corazon
 * limpio en verde agua. Mientras se deshace, el brillo se apaga con el cuerpo.
 */
public class NereaBrilloLayer extends RenderLayer<NereaRenderState, NereaModel> {

    /** Lo que brilla en cada fase: ojos de cian a rojo y venas de la maldicion. */
    private static final RenderType[] MALDITO = new RenderType[4];

    static {
        for (int i = 0; i < 4; i++) {
            MALDITO[i] = RenderTypes.eyes(Identifier.fromNamespaceAndPath(Atalaya.MOD_ID,
                    "textures/entity/nerea/nerea_brillo_f" + (i + 1) + ".png"));
        }
    }
    private static final RenderType LIBRE = RenderTypes.eyes(
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "textures/entity/nerea/nerea_brillo_libre.png"));

    public NereaBrilloLayer(RenderLayerParent<NereaRenderState, NereaModel> padre) {
        super(padre);
    }

    @Override
    public void submit(PoseStack pose, SubmitNodeCollector colector, int luz, NereaRenderState s, float yRot, float xRot) {
        float k = 1.0F - s.disolver;
        // Aturdido, los ojos parpadean como una lampara que falla.
        if (s.estado == NereaEntity.ATURDIDO && ((int) s.ageInTicks % 5) < 2) {
            k *= 0.35F;
        }
        // Dormido, el brillo respira despacio.
        if (s.estado == NereaEntity.DORMIDO) {
            k *= 0.55F + 0.25F * Mth.sin(s.ageInTicks * 0.08F);
        }
        if (k <= 0.01F) {
            return;
        }
        colector.order(1).submitModel(getParentModel(), s, pose, s.libre ? LIBRE : MALDITO[Math.clamp(s.fase, 1, 4) - 1], luz,
                OverlayTexture.NO_OVERLAY, ARGB.colorFromFloat(k, k, k, k), null, s.outlineColor, null);
    }
}
