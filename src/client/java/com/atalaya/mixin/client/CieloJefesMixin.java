package com.atalaya.mixin.client;

import com.atalaya.client.CieloJefes;
import com.atalaya.client.MomentoMaldicionCliente;
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
 * mundo, las estrellas) se le mezcla el del jefe con el que se pelea, y encima
 * el del Momento Maldicion (MomentoMaldicionCliente) si lo hay. Solo a la
 * sonda de la camara: lo demas (el servidor, el juego) no se entera.
 */
@Mixin(EnvironmentAttributeProbe.class)
public abstract class CieloJefesMixin {

    @Inject(method = "getValue", at = @At("RETURN"), cancellable = true)
    private void atalaya$cieloDelJefe(EnvironmentAttribute<?> atributo, float parcial, CallbackInfoReturnable<Object> cir) {
        boolean jefe = CieloJefes.activo();
        boolean maldito = MomentoMaldicionCliente.cieloActivo();
        if (!jefe && !maldito) {
            return;
        }
        Minecraft mc = Minecraft.getInstance();
        if (mc.gameRenderer == null || mc.gameRenderer.mainCamera().attributeProbe() != (Object) this) {
            return;
        }
        Object valor = cir.getReturnValue();
        if (jefe) {
            Object nuevo = CieloJefes.mezclar(atributo, valor);
            if (nuevo != null) {
                valor = nuevo;
            }
        }
        // El Momento Maldicion va encima del cielo del jefe: la maldicion manda.
        if (maldito) {
            Object nuevo = MomentoMaldicionCliente.mezclar(atributo, valor);
            if (nuevo != null) {
                valor = nuevo;
            }
        }
        cir.setReturnValue(valor);
    }
}
