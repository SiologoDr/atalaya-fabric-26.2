package com.atalaya.mixin;

import com.atalaya.cambios.CambiosDificultad;
import net.minecraft.core.BlockPos;
import net.minecraft.resources.ResourceKey;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.EndPortalBlock;
import net.minecraft.world.level.block.NetherPortalBlock;
import net.minecraft.world.level.portal.TeleportTransition;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/**
 * Los portales a una dimension cerrada no llevan a ninguna parte (CambiosDificultad: el menu de las dimensiones y los
 * cambios EL END, SELLADO y LOS PORTALES ARDEN). Se corta al principio, antes de que el juego busque o cree el portal de
 * salida al otro lado; y a quien lo intenta se le dice por que.
 */
@Mixin({NetherPortalBlock.class, EndPortalBlock.class})
public abstract class PortalCerradoMixin {

    @Inject(method = "getPortalDestination", at = @At("HEAD"), cancellable = true)
    private void atalaya$cerrado(ServerLevel nivel, Entity entidad, BlockPos pos, CallbackInfoReturnable<TeleportTransition> cir) {
        ResourceKey<Level> destino;
        if ((Object) this instanceof NetherPortalBlock) {
            destino = nivel.dimension() == Level.NETHER ? Level.OVERWORLD : Level.NETHER;
        } else {
            destino = nivel.dimension() == Level.END ? Level.OVERWORLD : Level.END;
        }
        if (!CambiosDificultad.abierta(nivel.getServer(), destino)) {
            cir.setReturnValue(null);
            CambiosDificultad.avisarCerrado(entidad, destino);
        }
    }
}
