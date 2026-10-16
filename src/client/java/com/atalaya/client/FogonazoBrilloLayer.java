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
 * Lo que brilla del Fogonazo, de noche y en la cueva: el farol, la boca, las rajas de las placas y el canto de los ojos.
 * Es el tipo de render "eyes" de vanilla (el de los ojos de la arana), que no se apaga con la oscuridad.
 */
public class FogonazoBrilloLayer extends RenderLayer<FogonazoRenderState, FogonazoModel> {

    private static final RenderType BRILLO = RenderTypes.eyes(
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "textures/entity/fogonazo/fogonazo_brillo.png"));

    public FogonazoBrilloLayer(RenderLayerParent<FogonazoRenderState, FogonazoModel> padre) {
        super(padre);
    }

    @Override
    public void submit(PoseStack pose, SubmitNodeCollector colector, int luz, FogonazoRenderState estado, float yRot,
                       float xRot) {
        colector.order(1).submitModel(getParentModel(), estado, pose, BRILLO, luz, OverlayTexture.NO_OVERLAY,
                estado.outlineColor, null);
    }
}
