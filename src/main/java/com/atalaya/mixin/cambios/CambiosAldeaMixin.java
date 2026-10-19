package com.atalaya.mixin.cambios;

import com.atalaya.cambios.Cambio;
import com.atalaya.cambios.CambiosDificultad;
import com.atalaya.cambios.ReglasCambios;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.npc.villager.AbstractVillager;
import net.minecraft.world.item.trading.MerchantOffer;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/**
 * Lo de los aldeanos:
 * <pre>
 *   ALDEAS VIGILADAS   cuando los aldeanos llaman a su golem de hierro, sale un warden
 *   TRATOS MALDITOS    cada trato tiene un 20 % de traer un aquelarre de brujas
 * </pre>
 */
@Mixin(AbstractVillager.class)
public abstract class CambiosAldeaMixin {

    @Inject(method = "notifyTrade", at = @At("TAIL"))
    private void atalaya$trato(MerchantOffer oferta, CallbackInfo ci) {
        AbstractVillager yo = (AbstractVillager) (Object) this;
        if (yo.level() instanceof ServerLevel nivel && CambiosDificultad.activo(Cambio.TRATOS_MALDITOS)
                && yo.getRandom().nextFloat() < 0.2F) {
            ReglasCambios.aquelarre(nivel, yo);
        }
    }
}
