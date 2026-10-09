package com.atalaya.mixin.client;

import com.atalaya.client.BalaEnBrazosLayer;
import net.minecraft.client.model.HumanoidModel;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.renderer.entity.state.HumanoidRenderState;
import org.spongepowered.asm.mixin.Final;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/**
 * Quien lleva una Bala de canon la carga en brazos (Juan: "en vez de tenerlo
 * como item, que se vea que la esta cargando la persona"): los dos brazos hacia
 * delante y algo hacia dentro, sin balancearse al andar. La bala la pinta
 * BalaEnBrazosLayer entre las manos. Va al final de la postura, despues de todo
 * lo de vanilla (el jugador llama a esto al final de la suya), y vale tambien
 * para la armadura, que copia la postura.
 */
@Mixin(HumanoidModel.class)
public abstract class BalaBrazosMixin {

    @Shadow
    @Final
    public ModelPart rightArm;

    @Shadow
    @Final
    public ModelPart leftArm;

    @Inject(method = "setupAnim(Lnet/minecraft/client/renderer/entity/state/HumanoidRenderState;)V", at = @At("TAIL"))
    private void atalaya$cargarBala(HumanoidRenderState s, CallbackInfo ci) {
        if (!BalaEnBrazosLayer.lleva(s)) {
            return;
        }
        // Un poco de vaiven al andar, con el peso.
        float vaiven = s.isCrouching ? 0.0F : 0.06F * net.minecraft.util.Mth.sin(s.walkAnimationPos * 0.6662F) * s.walkAnimationSpeed;
        rightArm.xRot = -0.92F + vaiven;
        rightArm.yRot = -0.42F;
        rightArm.zRot = 0.08F;
        leftArm.xRot = -0.92F + vaiven;
        leftArm.yRot = 0.42F;
        leftArm.zRot = -0.08F;
    }
}
