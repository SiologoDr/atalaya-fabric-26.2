package com.atalaya.client;

import com.atalaya.Atalaya;
import com.atalaya.entity.NovilisEntity;
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
 * Lo que brilla de Novilis a oscuras: las grietas de lava, el nucleo solar, la
 * T del yelmo, el halo y los filos de la espada. Cambia con la fase (ambar,
 * oro, blanco solar, carmesi), azul con la Furia y oro calmo al liberarse.
 * Dormido respira despacio; aturdido parpadea como una brasa que se apaga.
 */
public class NovilisBrilloLayer extends RenderLayer<NovilisRenderState, NovilisModel> {

    private static final RenderType[] BRILLO = new RenderType[6];
    private static final String[] PIELES = {"f1", "f2", "f3", "f4", "furia", "libre"};

    static {
        for (int i = 0; i < PIELES.length; i++) {
            BRILLO[i] = RenderTypes.eyes(Identifier.fromNamespaceAndPath(Atalaya.MOD_ID,
                    "textures/entity/novilis/novilis_brillo_" + PIELES[i] + ".png"));
        }
    }

    public NovilisBrilloLayer(RenderLayerParent<NovilisRenderState, NovilisModel> padre) {
        super(padre);
    }

    @Override
    public void submit(PoseStack pose, SubmitNodeCollector colector, int luz, NovilisRenderState s, float yRot, float xRot) {
        float k = 1.0F - s.disolver;
        if (s.estado == NovilisEntity.ATURDIDO && ((int) s.ageInTicks % 6) < 2) {
            k *= 0.4F;
        }
        if (s.estado == NovilisEntity.DORMIDO) {
            k *= 0.5F + 0.25F * Mth.sin(s.ageInTicks * 0.07F);
        }
        if (k <= 0.01F) {
            return;
        }
        colector.order(1).submitModel(getParentModel(), s, pose, BRILLO[NovilisRenderer.piel(s)], luz,
                OverlayTexture.NO_OVERLAY, ARGB.colorFromFloat(k, k, k, k), null, s.outlineColor, null);
    }
}
