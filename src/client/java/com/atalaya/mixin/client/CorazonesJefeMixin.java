package com.atalaya.mixin.client;

import com.atalaya.client.CorazonesJefe;
import net.minecraft.resources.Identifier;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/**
 * Los corazones del jugador en combate con un jefe (CorazonesJefe): cambia el
 * dibujo de los normales y del hueco; lo demas lo sigue haciendo vanilla.
 */
@Mixin(targets = "net.minecraft.client.gui.Hud$HeartType")
public abstract class CorazonesJefeMixin {

    @Inject(method = "getSprite", at = @At("HEAD"), cancellable = true)
    private void atalaya$corazonDeJefe(boolean hardcore, boolean mitad, boolean parpadea,
                                       CallbackInfoReturnable<Identifier> cir) {
        Identifier propio = CorazonesJefe.sprite(((Enum<?>) (Object) this).name(), mitad, parpadea);
        if (propio != null) {
            cir.setReturnValue(propio);
        }
    }
}
