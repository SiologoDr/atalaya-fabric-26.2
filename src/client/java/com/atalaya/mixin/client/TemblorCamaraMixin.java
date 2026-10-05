package com.atalaya.mixin.client;

import com.atalaya.client.NereaPresencia;
import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.math.Axis;
import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.GameRenderer;
import net.minecraft.client.renderer.state.level.CameraRenderState;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/**
 * El temblor de camara de los golpes de Nerea.
 *
 * Se engancha al final de bobHurt, el sitio donde vanilla ya inclina la vista
 * al recibir dano: se aplica siempre (no depende de la opcion de balanceo al
 * andar) y tanto al mundo como a la mano, asi que la mano tiembla con todo.
 */
@Mixin(GameRenderer.class)
public abstract class TemblorCamaraMixin {

    @Inject(method = "bobHurt", at = @At("TAIL"))
    private void atalaya$temblor(CameraRenderState camara, PoseStack pose, CallbackInfo ci) {
        float parcial = Minecraft.getInstance().getDeltaTracker().getGameTimeDeltaPartialTick(false);
        float[] a = NereaPresencia.angulos(parcial);
        if (a == null) {
            return;
        }
        pose.mulPose(Axis.ZP.rotationDegrees(a[2]));
        pose.mulPose(Axis.XP.rotationDegrees(a[1]));
        pose.mulPose(Axis.YP.rotationDegrees(a[0]));
    }
}
