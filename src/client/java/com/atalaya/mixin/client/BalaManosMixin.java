package com.atalaya.mixin.client;

import com.atalaya.client.BalaDibujo;
import com.atalaya.item.AtalayaItems;
import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.math.Axis;
import net.minecraft.client.player.AbstractClientPlayer;
import net.minecraft.client.renderer.ItemInHandRenderer;
import net.minecraft.client.renderer.SubmitNodeCollector;
import net.minecraft.util.Mth;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.entity.HumanoidArm;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.phys.Vec3;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/**
 * En primera persona, la Bala de canon se lleva con las dos manos, abajo en el
 * centro, como vanilla lleva un mapa con las dos manos (las mismas manos y el
 * mismo vaiven), pero con la bala redonda entre ellas en vez del mapa y sin
 * inclinarse con la vista: pesa, va siempre abajo.
 */
@Mixin(ItemInHandRenderer.class)
public abstract class BalaManosMixin {

    @Shadow
    private void renderMapHand(PoseStack pose, SubmitNodeCollector colector, int luz, HumanoidArm brazo) {
    }

    @Inject(method = "submitArmWithItem", at = @At("HEAD"), cancellable = true)
    private void atalaya$balaConLasDosManos(AbstractClientPlayer jugador, float parcial, float cabeceo, InteractionHand mano,
                                            float golpe, ItemStack objeto, float bajada, PoseStack pose,
                                            SubmitNodeCollector colector, int luz, CallbackInfo ci) {
        if (!jugador.getMainHandItem().is(AtalayaItems.BALA_CANON)) {
            return;
        }
        ci.cancel();
        if (mano != InteractionHand.MAIN_HAND) {
            return;
        }
        pose.pushPose();
        float raiz = Mth.sqrt(golpe);
        pose.translate(0.0F, 0.1F * Mth.sin(golpe * Mth.PI), -0.4F * Mth.sin(raiz * Mth.PI));
        // La del mapa mirando al frente, siempre: abajo y casi tumbada.
        float inclina = 1.0F;
        pose.translate(0.0F, 0.04F + bajada * -1.2F + inclina * -0.5F, -0.72F);
        pose.mulPose(Axis.XP.rotationDegrees(inclina * -85.0F));
        if (!jugador.isInvisible()) {
            pose.pushPose();
            pose.mulPose(Axis.YP.rotationDegrees(90.0F));
            renderMapHand(pose, colector, luz, HumanoidArm.RIGHT);
            renderMapHand(pose, colector, luz, HumanoidArm.LEFT);
            pose.popPose();
        }
        colector.submitCustomGeometry(pose, BalaDibujo.HIERRO, (p, buf) ->
                BalaDibujo.bola(buf, p, new Vec3(0.0, -0.09, 0.14), 0.17, 0.0F, 0.0F, luz));
        pose.popPose();
    }
}
