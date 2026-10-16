package com.atalaya.mixin.client;

import com.atalaya.entity.CocoEntity;
import net.minecraft.client.renderer.culling.Frustum;
import net.minecraft.client.renderer.entity.EntityRenderDispatcher;
import net.minecraft.world.entity.Entity;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/**
 * El que va dentro del Coco no se ve: esta en su barriga (Juan: «no quiero panza translucida»). Lo que dice que esta ahi
 * es el aviso de encima del Coco.
 */
@Mixin(EntityRenderDispatcher.class)
public abstract class CocoOcultarMixin {

    @Inject(method = "shouldRender", at = @At("HEAD"), cancellable = true)
    private <E extends Entity> void atalaya$dentroNoSeVe(E entidad, Frustum frustum, double x, double y, double z,
                                                          CallbackInfoReturnable<Boolean> cir) {
        if (CocoEntity.atrapado(entidad)) {
            cir.setReturnValue(false);
        }
    }
}
