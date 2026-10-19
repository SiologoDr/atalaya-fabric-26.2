package com.atalaya.mixin.cambios;

import com.atalaya.cambios.Cambio;
import com.atalaya.cambios.CambiosDificultad;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.projectile.throwableitemprojectile.ThrownEnderpearl;
import net.minecraft.world.phys.HitResult;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/** PERLAS QUE NO CRUZAN: la perla que cae en otra dimension que la de su dueno se rompe sin llevarlo. */
@Mixin(ThrownEnderpearl.class)
public abstract class CambiosPerlaMixin {

    @Inject(method = "onHit", at = @At("HEAD"), cancellable = true)
    private void atalaya$noCruza(HitResult golpe, CallbackInfo ci) {
        ThrownEnderpearl perla = (ThrownEnderpearl) (Object) this;
        Entity dueno = perla.getOwner();
        if (!perla.level().isClientSide() && dueno != null && dueno.level() != perla.level()
                && CambiosDificultad.activo(Cambio.PERLAS_QUE_NO_CRUZAN)) {
            perla.discard();
            ci.cancel();
        }
    }
}
