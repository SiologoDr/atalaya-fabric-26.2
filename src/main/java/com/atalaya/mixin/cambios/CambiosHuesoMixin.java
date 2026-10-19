package com.atalaya.mixin.cambios;

import com.atalaya.cambios.Cambio;
import com.atalaya.cambios.CambiosDificultad;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.world.item.BoneMealItem;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/** TIERRA YERMA: el polvo de hueso no hace crecer nada (ni en tierra ni en el agua). */
@Mixin(BoneMealItem.class)
public abstract class CambiosHuesoMixin {

    @Inject(method = "growCrop", at = @At("HEAD"), cancellable = true)
    private static void atalaya$yerma(ItemStack polvo, Level nivel, BlockPos pos, CallbackInfoReturnable<Boolean> cir) {
        if (CambiosDificultad.activo(Cambio.TIERRA_YERMA)) {
            cir.setReturnValue(false);
        }
    }

    @Inject(method = "growWaterPlant", at = @At("HEAD"), cancellable = true)
    private static void atalaya$yermaAgua(ItemStack polvo, Level nivel, BlockPos pos, Direction cara,
                                          CallbackInfoReturnable<Boolean> cir) {
        if (CambiosDificultad.activo(Cambio.TIERRA_YERMA)) {
            cir.setReturnValue(false);
        }
    }
}
