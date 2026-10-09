package com.atalaya.mixin.client;

import com.atalaya.entity.CanonNaufragioEntity;
import net.minecraft.client.Minecraft;
import net.minecraft.client.player.AbstractClientPlayer;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/**
 * El catalejo del Canon del Naufragio acerca la vista, como el de vanilla pero
 * menos (tres aumentos: Nerea es grande y hay que verla entera). Solo en primera
 * persona y solo a quien va subido. El catalejo en pantalla: CanonMiraHud; la
 * punteria mas lenta: CanonPunteriaMixin.
 */
@Mixin(AbstractClientPlayer.class)
public abstract class CanonZoomMixin {

    /** Lo que se acerca (el de vanilla, 0,1). */
    private static final float AUMENTO = 0.33F;

    @Inject(method = "getFieldOfViewModifier", at = @At("RETURN"), cancellable = true)
    private void atalaya$catalejoDelCanon(boolean primeraPersona, float escala, CallbackInfoReturnable<Float> cir) {
        AbstractClientPlayer yo = (AbstractClientPlayer) (Object) this;
        if (primeraPersona && yo == Minecraft.getInstance().player && yo.getVehicle() instanceof CanonNaufragioEntity) {
            cir.setReturnValue(AUMENTO);
        }
    }
}
