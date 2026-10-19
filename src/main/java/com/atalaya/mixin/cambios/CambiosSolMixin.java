package com.atalaya.mixin.cambios;

import com.atalaya.momento.Momentos;
import net.minecraft.world.entity.Mob;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/** EL ECLIPSE (el momento): mientras dura, ningun mob arde al sol. */
@Mixin(Mob.class)
public abstract class CambiosSolMixin {

    @Inject(method = "isSunBurnTick", at = @At("HEAD"), cancellable = true)
    private void atalaya$eclipse(CallbackInfoReturnable<Boolean> cir) {
        if (Momentos.sinSol()) {
            cir.setReturnValue(false);
        }
    }
}
