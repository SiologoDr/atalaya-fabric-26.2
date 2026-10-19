package com.atalaya.mixin.cambios;

import com.atalaya.cambios.Cambio;
import com.atalaya.cambios.CambiosDificultad;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.block.BambooSaplingBlock;
import net.minecraft.world.level.block.BambooStalkBlock;
import net.minecraft.world.level.block.CactusBlock;
import net.minecraft.world.level.block.ChorusFlowerBlock;
import net.minecraft.world.level.block.CocoaBlock;
import net.minecraft.world.level.block.CropBlock;
import net.minecraft.world.level.block.MangrovePropaguleBlock;
import net.minecraft.world.level.block.NetherWartBlock;
import net.minecraft.world.level.block.PitcherCropBlock;
import net.minecraft.world.level.block.SaplingBlock;
import net.minecraft.world.level.block.StemBlock;
import net.minecraft.world.level.block.SugarCaneBlock;
import net.minecraft.world.level.block.SweetBerryBushBlock;
import net.minecraft.world.level.block.TorchflowerCropBlock;
import net.minecraft.world.level.block.state.BlockState;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/** TIERRA YERMA: los cultivos, los brotes y lo que crece solo ya no crecen (se salta su tick aleatorio). */
@Mixin({CropBlock.class, StemBlock.class, SaplingBlock.class, CocoaBlock.class, NetherWartBlock.class,
        SweetBerryBushBlock.class, SugarCaneBlock.class, CactusBlock.class, BambooStalkBlock.class,
        BambooSaplingBlock.class, TorchflowerCropBlock.class, PitcherCropBlock.class, ChorusFlowerBlock.class,
        MangrovePropaguleBlock.class})
public abstract class CambiosCrecerMixin {

    @Inject(method = "randomTick", at = @At("HEAD"), cancellable = true)
    private void atalaya$yerma(BlockState estado, ServerLevel nivel, BlockPos pos, RandomSource azar, CallbackInfo ci) {
        if (CambiosDificultad.activo(Cambio.TIERRA_YERMA)) {
            ci.cancel();
        }
    }
}
