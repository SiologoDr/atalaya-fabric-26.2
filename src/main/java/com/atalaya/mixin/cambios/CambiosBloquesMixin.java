package com.atalaya.mixin.cambios;

import com.atalaya.cambios.Cambio;
import com.atalaya.cambios.CambiosDificultad;
import com.atalaya.cambios.ReglasCambios;
import net.minecraft.core.BlockPos;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.ButtonBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.BlockHitResult;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/** NO TOQUES ESE BOTON: pulsar un boton mata (el boton se pulsa igual). */
@Mixin(ButtonBlock.class)
public abstract class CambiosBloquesMixin {

    @Inject(method = "useWithoutItem", at = @At("HEAD"))
    private void atalaya$boton(BlockState estado, Level nivel, BlockPos pos, Player jugador, BlockHitResult golpe,
                               CallbackInfoReturnable<InteractionResult> cir) {
        if (!nivel.isClientSide() && CambiosDificultad.activo(Cambio.NO_TOQUES_ESE_BOTON)) {
            ReglasCambios.trampa(jugador, pos);
        }
    }
}
