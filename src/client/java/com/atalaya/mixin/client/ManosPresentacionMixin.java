package com.atalaya.mixin.client;

import com.atalaya.client.PresentacionJefe;
import net.minecraft.client.renderer.GameRenderer;
import net.minecraft.client.renderer.state.level.CameraRenderState;
import org.joml.Matrix4fc;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/**
 * En la presentacion de un jefe no se ven las manos del jugador en primera
 * persona ni lo que lleva en ellas: es una escena de cine, y al volver la camara
 * a los ojos el cartel aun se esta leyendo. Lo que lleva en las manos visto
 * desde fuera lo quita ManosPresentacionCuerpoMixin.
 */
@Mixin(GameRenderer.class)
public abstract class ManosPresentacionMixin {

    @Inject(method = "renderItemInHand", at = @At("HEAD"), cancellable = true)
    private void atalaya$sinManos(CameraRenderState camara, float parcial, Matrix4fc vista, CallbackInfo ci) {
        if (PresentacionJefe.activa()) {
            ci.cancel();
        }
    }
}
