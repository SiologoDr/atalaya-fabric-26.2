package com.atalaya.mixin.cambios;

import com.atalaya.cambios.Cambio;
import com.atalaya.cambios.CambiosDificultad;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.CarvedPumpkinBlock;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/** CALABAZAS DORMIDAS: la calabaza ya no da vida a ningun golem (ni de hierro, ni de nieve, ni de cobre). */
@Mixin(CarvedPumpkinBlock.class)
public abstract class CambiosGolemMixin {

    @Inject(method = "trySpawnGolem", at = @At("HEAD"), cancellable = true)
    private void atalaya$dormidas(Level nivel, BlockPos pos, CallbackInfo ci) {
        if (CambiosDificultad.activo(Cambio.CALABAZAS_DORMIDAS)) {
            ci.cancel();
        }
    }
}
