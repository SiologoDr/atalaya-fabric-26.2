package com.atalaya.mixin.client;

import com.atalaya.client.PresentacionJefe;
import net.minecraft.client.player.ClientInput;
import net.minecraft.client.player.KeyboardInput;
import net.minecraft.world.entity.player.Input;
import net.minecraft.world.phys.Vec2;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/**
 * Mientras la camara de la presentacion de un jefe esta fuera, el jugador no
 * anda ni salta (la presentacion no se puede saltar).
 */
@Mixin(KeyboardInput.class)
public abstract class TecladoPresentacionMixin {

    @Inject(method = "tick", at = @At("TAIL"))
    private void atalaya$quieto(CallbackInfo ci) {
        if (PresentacionJefe.ocultaHud()) {
            ClientInput yo = (ClientInput) (Object) this;
            yo.keyPresses = Input.EMPTY;
            ((ClientInputAccesor) yo).atalaya$setMoveVector(Vec2.ZERO);
        }
    }
}
