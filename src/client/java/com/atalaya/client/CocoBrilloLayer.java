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

/**
 * Lo que brilla del Coco en la oscuridad: la brasa del fondo de los ojos y la garganta (y la luz del paladar cuando abre
 * la boca). Es el tipo de render "eyes" de vanilla (el de los ojos de la arana), que no se apaga de noche.
 */
public class CocoBrilloLayer extends RenderLayer<CocoRenderState, CocoModel> {

    private static final RenderType BRILLO = RenderTypes.eyes(
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "textures/entity/coco/coco_brillo.png"));

    public CocoBrilloLayer(RenderLayerParent<CocoRenderState, CocoModel> padre) {
        super(padre);
    }

    @Override
    public void submit(PoseStack pose, SubmitNodeCollector colector, int luz, CocoRenderState estado, float yRot,
                       float xRot) {
        colector.order(1).submitModel(getParentModel(), estado, pose, BRILLO, luz, OverlayTexture.NO_OVERLAY,
                estado.outlineColor, null);
    }
}
