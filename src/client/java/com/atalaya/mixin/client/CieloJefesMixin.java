package com.atalaya.mixin.client;

import com.atalaya.client.CieloJefes;
import net.minecraft.client.Minecraft;
import net.minecraft.world.attribute.EnvironmentAttribute;
import net.minecraft.world.attribute.EnvironmentAttributeProbe;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/**
 * El cielo del jefe (CieloJefes): a lo que lee la camara de los atributos de
 * ambiente (el color del cielo, la niebla, las nubes, el ocaso, la luz del
 * mundo, las estrellas) se le mezcla el del jefe con el que se pelea. Solo a la
 * sonda de la camara: lo demas (el servidor, el juego) no se entera.
 */
@Mixin(EnvironmentAttributeProbe.class)
public abstract class CieloJefesMixin {

    @Inject(method = "getValue", at = @At("RETURN"), cancellable = true)
    private void atalaya$cieloDelJefe(EnvironmentAttribute<?> atributo, float parcial, CallbackInfoReturnable<Object> cir) {
        if (!CieloJefes.activo()) {
            return;
        }
        Minecraft mc = Minecraft.getInstance();
        if (mc.gameRenderer == null || mc.gameRenderer.mainCamera().attributeProbe() != (Object) this) {
            return;
        }
        Object nuevo = CieloJefes.mezclar(atributo, cir.getReturnValue());
        if (nuevo != null) {
            cir.setReturnValue(nuevo);
        }
    }
}
