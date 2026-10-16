package com.atalaya.mixin;

import com.atalaya.entity.CocoEntity;
import net.minecraft.world.entity.player.Player;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/**
 * Dentro del Coco no se sale con mayusculas, como de un caballo o una barca: el servidor pregunta aqui si el jugador
 * quiere bajarse, y dentro de un Coco la respuesta es que no. Solo sales si alguien lo mata.
 */
@Mixin(Player.class)
public abstract class CocoDentroMixin {

    @Inject(method = "wantsToStopRiding", at = @At("HEAD"), cancellable = true)
    private void atalaya$noSeSale(CallbackInfoReturnable<Boolean> cir) {
        if (CocoEntity.atrapado((Player) (Object) this)) {
            cir.setReturnValue(false);
        }
    }
}
