package com.atalaya.mixin.cambios;

import com.atalaya.cambios.ObjetosCambios;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.player.Player;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/** El Fruto del Recuerdo: quien lo ha comido no suelta nada al morir (lo recupera al reaparecer). */
@Mixin(Player.class)
public abstract class CambiosRecuerdoMixin {

    @Inject(method = "dropEquipment", at = @At("HEAD"), cancellable = true)
    private void atalaya$recuerdo(ServerLevel nivel, CallbackInfo ci) {
        if (((Player) (Object) this).entityTags().contains(ObjetosCambios.RECUERDO)) {
            ci.cancel();
        }
    }
}
