package com.atalaya.mixin.cambios;

import com.atalaya.cambios.Cambio;
import com.atalaya.cambios.CambiosDificultad;
import net.minecraft.world.level.LevelReader;
import net.minecraft.world.level.material.LavaFluid;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/** LAVA DESBOCADA: la lava corre como el agua (cada 5 ticks, 4 bloques de busqueda y 1 de caida por bloque). */
@Mixin(LavaFluid.class)
public abstract class CambiosLavaMixin {

    @Inject(method = "getTickDelay", at = @At("HEAD"), cancellable = true)
    private void atalaya$ritmo(LevelReader nivel, CallbackInfoReturnable<Integer> cir) {
        if (CambiosDificultad.activo(Cambio.LAVA_DESBOCADA)) {
            cir.setReturnValue(5);
        }
    }

    @Inject(method = "getSlopeFindDistance", at = @At("HEAD"), cancellable = true)
    private void atalaya$busca(LevelReader nivel, CallbackInfoReturnable<Integer> cir) {
        if (CambiosDificultad.activo(Cambio.LAVA_DESBOCADA)) {
            cir.setReturnValue(4);
        }
    }

    @Inject(method = "getDropOff", at = @At("HEAD"), cancellable = true)
    private void atalaya$alcance(LevelReader nivel, CallbackInfoReturnable<Integer> cir) {
        if (CambiosDificultad.activo(Cambio.LAVA_DESBOCADA)) {
            cir.setReturnValue(1);
        }
    }
}
