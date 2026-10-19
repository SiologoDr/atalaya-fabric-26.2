package com.atalaya.mixin.cambios;

import com.atalaya.cambios.Cambio;
import com.atalaya.cambios.CambiosDificultad;
import com.atalaya.cambios.ReglasCambios;
import net.minecraft.core.BlockPos;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.DoorBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.BlockHitResult;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/**
 * PUERTAS MALDITAS: abrir a mano una puerta que se abre a mano (las de madera; las de cobre tambien) mata. Las de
 * hierro, que no se abren a mano, son las de fiar.
 */
@Mixin(DoorBlock.class)
public abstract class CambiosPuertaMixin {

    @Inject(method = "useWithoutItem", at = @At("HEAD"))
    private void atalaya$puerta(BlockState estado, Level nivel, BlockPos pos, Player jugador, BlockHitResult golpe,
                                CallbackInfoReturnable<InteractionResult> cir) {
        if (!nivel.isClientSide() && ((DoorBlock) (Object) this).type().canOpenByHand()
                && CambiosDificultad.activo(Cambio.PUERTAS_MALDITAS)) {
            ReglasCambios.trampa(jugador, pos);
        }
    }
}
