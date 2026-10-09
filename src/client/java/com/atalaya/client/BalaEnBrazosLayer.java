package com.atalaya.client;

import com.atalaya.item.AtalayaItems;
import com.mojang.blaze3d.vertex.PoseStack;
import net.minecraft.client.model.player.PlayerModel;
import net.minecraft.client.renderer.SubmitNodeCollector;
import net.minecraft.client.renderer.entity.RenderLayerParent;
import net.minecraft.client.renderer.entity.layers.RenderLayer;
import net.minecraft.client.renderer.entity.state.AvatarRenderState;
import net.minecraft.client.renderer.entity.state.HumanoidRenderState;
import net.minecraft.world.phys.Vec3;

/**
 * La Bala de canon en brazos, vista desde fuera: una bala redonda entre las dos
 * manos, delante del pecho (los brazos los pone BalaBrazosMixin; el objeto plano
 * de la mano lo quita BalaCuerpoMixin). En primera persona la pinta
 * BalaManosMixin.
 */
public class BalaEnBrazosLayer extends RenderLayer<AvatarRenderState, PlayerModel> {

    public BalaEnBrazosLayer(RenderLayerParent<AvatarRenderState, PlayerModel> padre) {
        super(padre);
    }

    /** Si lleva una bala en la mano principal. */
    public static boolean lleva(HumanoidRenderState s) {
        return s.getMainHandItemStack().is(AtalayaItems.BALA_CANON);
    }

    @Override
    public void submit(PoseStack pose, SubmitNodeCollector colector, int luz, AvatarRenderState s, float rumbo, float cabeceo) {
        if (!lleva(s) || s.isInvisible) {
            return;
        }
        pose.pushPose();
        getParentModel().body.translateAndRotate(pose);
        // Entre las manos: delante del pecho (en el modelo, delante es -z y abajo es +y).
        colector.submitCustomGeometry(pose, BalaDibujo.HIERRO, (p, buf) ->
                BalaDibujo.bola(buf, p, new Vec3(0.0, 9.0 / 16.0, -8.5 / 16.0), 0.27, 0.0F, 0.0F, luz));
        pose.popPose();
    }
}
