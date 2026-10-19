package com.atalaya.mixin.cambios;

import com.atalaya.cambios.Cambio;
import com.atalaya.cambios.CambiosDificultad;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.tags.FluidTags;
import net.minecraft.tags.TagKey;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.material.Fluid;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/**
 * SIN BOLSAS DE AIRE: el truco de meter la cabeza en una puerta, una trampilla o una antorcha bajo el agua ya no da
 * aire. Si los ojos del jugador estan en un bloque que no es agua pero tiene agua encima o a los lados, cuenta como si
 * estuvieran en el agua.
 */
@Mixin(Entity.class)
public abstract class CambiosAireMixin {

    @Inject(method = "isEyeInFluid", at = @At("RETURN"), cancellable = true)
    private void atalaya$sinBolsas(TagKey<Fluid> fluido, CallbackInfoReturnable<Boolean> cir) {
        if (cir.getReturnValueZ() || fluido != FluidTags.WATER || !((Object) this instanceof Player p) || p.isCreative()
                || p.isSpectator() || !CambiosDificultad.activo(Cambio.SIN_BOLSAS_DE_AIRE)) {
            return;
        }
        Level nivel = p.level();
        BlockPos ojos = BlockPos.containing(p.getX(), p.getEyeY(), p.getZ());
        if (nivel.getFluidState(ojos).is(FluidTags.WATER) || nivel.getBlockState(ojos).isAir()) {
            return;
        }
        int agua = 0;
        for (Direction d : Direction.values()) {
            if (d != Direction.DOWN && nivel.getFluidState(ojos.relative(d)).is(FluidTags.WATER)) {
                agua++;
            }
        }
        if (agua >= 2 || nivel.getFluidState(ojos.above()).is(FluidTags.WATER)) {
            cir.setReturnValue(true);
        }
    }
}
