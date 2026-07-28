package com.atalaya.mixin;

import com.atalaya.radiation.GeodeIndex;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.context.BlockPlaceContext;
import net.minecraft.world.level.block.state.BlockState;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/**
 * Mantiene el indice de geodas al dia cuando alguien COLOCA amatista en gemacion.
 *
 * Se engancha en BlockItem.placeBlock y no en Level.setBlock a proposito:
 * setBlock es la ruta mas caliente del juego (agua que fluye, cultivos que
 * crecen, explosiones...) y filtrar ahi cuesta de verdad. placeBlock solo corre
 * cuando un jugador coloca un bloque desde un item, que es una accion puntual.
 *
 * En la practica esto solo pasa en creativo: la amatista en gemacion no se
 * puede obtener en supervivencia ni con Toque de Seda.
 */
@Mixin(BlockItem.class)
public class BlockItemMixin {

    @Inject(method = "placeBlock", at = @At("RETURN"))
    private void atalaya$indexarSiEsFuente(BlockPlaceContext contexto,
                                           BlockState estado,
                                           CallbackInfoReturnable<Boolean> cir) {
        if (!Boolean.TRUE.equals(cir.getReturnValue())) {
            return; // la colocacion no prospero
        }
        if (!GeodeIndex.esFuenteDeRadiacion(estado)) {
            return;
        }
        if (contexto.getLevel() instanceof ServerLevel nivel) {
            GeodeIndex.agregar(nivel, contexto.getClickedPos());
        }
    }
}
