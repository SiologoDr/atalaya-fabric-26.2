package com.atalaya.mixin.cambios;

import com.atalaya.cambios.Cambio;
import com.atalaya.cambios.CambiosDificultad;
import net.minecraft.world.entity.monster.zombie.Zombie;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/** ZOMBIS TREPADORES: el sol ya no los quema. */
@Mixin(Zombie.class)
public abstract class CambiosZombiMixin {

    @Inject(method = "isSunSensitive", at = @At("HEAD"), cancellable = true)
    private void atalaya$sinSol(CallbackInfoReturnable<Boolean> cir) {
        if (CambiosDificultad.activo(Cambio.ZOMBIS_TREPADORES)) {
            cir.setReturnValue(false);
        }
    }
}
