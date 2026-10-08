package com.atalaya.mixin.client;

import com.atalaya.client.PresentacionJefe;
import net.minecraft.client.Minecraft;
import net.minecraft.client.model.HumanoidModel;
import net.minecraft.client.renderer.entity.player.AvatarRenderer;
import net.minecraft.client.renderer.entity.state.AvatarRenderState;
import net.minecraft.world.entity.Avatar;
import net.minecraft.world.item.ItemStack;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/**
 * En la presentacion de un jefe la camara sale del jugador y se le ve el cuerpo:
 * sin lo que lleva en la mano derecha y en la izquierda (ni la postura de
 * sujetarlo), para que la escena sea solo el jefe.
 */
@Mixin(AvatarRenderer.class)
public abstract class ManosPresentacionCuerpoMixin {

    @Inject(method = "extractRenderState(Lnet/minecraft/world/entity/Avatar;Lnet/minecraft/client/renderer/entity/state/AvatarRenderState;F)V",
            at = @At("TAIL"))
    private void atalaya$sinObjetos(Avatar avatar, AvatarRenderState s, float parcial, CallbackInfo ci) {
        Minecraft mc = Minecraft.getInstance();
        if (!PresentacionJefe.activa() || mc.player == null || s.id != mc.player.getId()) {
            return;
        }
        s.rightHandItemState.clear();
        s.leftHandItemState.clear();
        s.rightHandItemStack = ItemStack.EMPTY;
        s.leftHandItemStack = ItemStack.EMPTY;
        s.rightArmPose = HumanoidModel.ArmPose.EMPTY;
        s.leftArmPose = HumanoidModel.ArmPose.EMPTY;
        s.heldOnHead.clear();
    }
}
