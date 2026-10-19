package com.atalaya.mixin.cambios;

import com.atalaya.cambios.Cambio;
import com.atalaya.cambios.CambiosDificultad;
import net.minecraft.world.entity.MobCategory;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/** LA NOCHE SE LLENA: caben el doble de monstruos por zona. */
@Mixin(MobCategory.class)
public abstract class CambiosMundoMixin {

    @Inject(method = "getMaxInstancesPerChunk", at = @At("RETURN"), cancellable = true)
    private void atalaya$mobcap(CallbackInfoReturnable<Integer> cir) {
        if ((Object) this == MobCategory.MONSTER && CambiosDificultad.activo(Cambio.LA_NOCHE_SE_LLENA)) {
            cir.setReturnValue(cir.getReturnValueI() * 2);
        }
    }
}
