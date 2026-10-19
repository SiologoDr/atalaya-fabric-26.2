package com.atalaya.mixin.cambios;

import com.atalaya.cambios.Cambio;
import com.atalaya.cambios.CambiosDificultad;
import net.minecraft.world.entity.player.Player;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.ModifyVariable;

/** El hambre de los jugadores baja el doble de rapido (ESTOMAGO SIN FONDO). */
@Mixin(Player.class)
public abstract class CambiosJugadorMixin {

    @ModifyVariable(method = "causeFoodExhaustion", at = @At("HEAD"), argsOnly = true, ordinal = 0)
    private float atalaya$hambre(float cansancio) {
        return CambiosDificultad.activo(Cambio.ESTOMAGO_SIN_FONDO) ? cansancio * 2.0F : cansancio;
    }
}
