package com.atalaya.mixin.client;

import com.atalaya.client.BalaEnBrazosLayer;
import net.minecraft.client.model.HumanoidModel;
import net.minecraft.client.renderer.entity.player.AvatarRenderer;
import net.minecraft.client.renderer.entity.state.AvatarRenderState;
import net.minecraft.world.entity.Avatar;
import net.minecraft.world.entity.HumanoidArm;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/**
 * Quien carga una Bala de canon no la lleva como un objeto plano en la mano: se
 * quita el dibujo del objeto (y la postura de sujetarlo) y la bala la pinta
 * BalaEnBrazosLayer entre las dos manos. Lo que lleva sigue siendo lo mismo: solo
 * cambia como se ve.
 */
@Mixin(AvatarRenderer.class)
public abstract class BalaCuerpoMixin {

    @Inject(method = "extractRenderState(Lnet/minecraft/world/entity/Avatar;Lnet/minecraft/client/renderer/entity/state/AvatarRenderState;F)V",
            at = @At("TAIL"))
    private void atalaya$balaEnBrazos(Avatar avatar, AvatarRenderState s, float parcial, CallbackInfo ci) {
        if (!BalaEnBrazosLayer.lleva(s)) {
            return;
        }
        if (s.mainArm == HumanoidArm.RIGHT) {
            s.rightHandItemState.clear();
        } else {
            s.leftHandItemState.clear();
        }
        s.rightArmPose = HumanoidModel.ArmPose.EMPTY;
        s.leftArmPose = HumanoidModel.ArmPose.EMPTY;
    }
}
