package com.atalaya.mixin;

import com.atalaya.aturdimiento.Aturdimiento;
import net.minecraft.world.entity.player.Inventory;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/**
 * Impide cambiar de ranura de la barra mientras estas aturdido.
 *
 * Se corta aqui, en el inventario, y no en el teclado del cliente, porque a la
 * ranura se llega por tres caminos —la rueda del raton, las teclas del uno al
 * nueve y el "coger bloque"— y los tres acaban en este metodo. Un solo sitio
 * cubre los tres.
 *
 * Y al ser una clase comun, vale para el cliente Y para el servidor: aunque
 * alguien se traiga un cliente tocado, el servidor tampoco le deja cambiar.
 */
@Mixin(Inventory.class)
public abstract class RanuraAturdidoMixin {

    @Shadow
    public net.minecraft.world.entity.player.Player player;

    @Inject(method = "setSelectedSlot", at = @At("HEAD"), cancellable = true)
    private void atalaya$quietoAhi(int ranura, CallbackInfo ci) {
        if (player != null && Aturdimiento.aturdido(player)) {
            ci.cancel();
        }
    }
}
