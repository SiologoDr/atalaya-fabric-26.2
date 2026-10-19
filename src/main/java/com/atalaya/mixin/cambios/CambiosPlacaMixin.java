package com.atalaya.mixin.cambios;

import com.atalaya.cambios.Cambio;
import com.atalaya.cambios.CambiosDificultad;
import com.atalaya.cambios.ReglasCambios;
import net.minecraft.core.BlockPos;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.InsideBlockEffectApplier;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.BasePressurePlateBlock;
import net.minecraft.world.level.block.state.BlockState;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/** PLACAS TRAMPA: pisar una placa de presion (cualquiera) mata. */
@Mixin(BasePressurePlateBlock.class)
public abstract class CambiosPlacaMixin {

    @Inject(method = "entityInside", at = @At("HEAD"))
    private void atalaya$placa(BlockState estado, Level nivel, BlockPos pos, Entity quien, InsideBlockEffectApplier efectos,
                               boolean pasando, CallbackInfo ci) {
        if (!nivel.isClientSide() && quien instanceof Player jugador && CambiosDificultad.activo(Cambio.PLACAS_TRAMPA)) {
            ReglasCambios.trampa(jugador, pos);
        }
    }
}
