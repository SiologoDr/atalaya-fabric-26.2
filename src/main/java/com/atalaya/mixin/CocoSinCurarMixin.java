package com.atalaya.mixin;

import com.atalaya.entity.CocoEntity;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.food.FoodData;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/**
 * Dentro del Coco no te curas solo: la comida se queda como estaba, sin regenerar ni gastarse. Si no, con el hambre llena
 * la regeneracion rapida de vanilla (medio corazon cada medio segundo) le ganaba a lo que te quita el Coco (medio cada dos
 * segundos) y no habria peligro aunque estuvieras solo.
 */
@Mixin(FoodData.class)
public abstract class CocoSinCurarMixin {

    @Inject(method = "tick", at = @At("HEAD"), cancellable = true)
    private void atalaya$dentroNoSeCura(ServerPlayer jugador, CallbackInfo ci) {
        if (CocoEntity.atrapado(jugador)) {
            ci.cancel();
        }
    }
}
