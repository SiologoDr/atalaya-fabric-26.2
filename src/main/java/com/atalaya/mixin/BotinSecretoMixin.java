package com.atalaya.mixin;

import com.atalaya.util.BotinSecreto;
import net.minecraft.core.HolderLookup;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.entity.BrushableBlockEntity;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.level.storage.ValueInput;
import net.minecraft.world.level.storage.ValueOutput;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/**
 * Esconde lo que lleva dentro un bloque cepillable hasta la ultima pasada.
 *
 * Vanilla ensena el objeto asomando desde el primer cepillazo, y eso ahi esta
 * bien: en la arqueologia ver salir el casco de vasija poco a poco ES la
 * gracia. Pero con un botin de veinte por ciento lo estropea, porque en cuanto
 * asoma ya sabes si has ganado y las otras cuatro veces ni te molestas en
 * terminar. La tirada deja de costar nada.
 *
 * El truco esta en de donde saca el cliente lo que dibuja: del paquete de
 * sincronizacion. Si el objeto no viaja, no hay nada que ensenar. En el
 * servidor sigue estando y al acabar cae igual.
 *
 * Solo afecta a los bloques MARCADOS, no a todos. La arqueologia de vanilla se
 * queda tal cual, que para eso esta pensada.
 */
@Mixin(BrushableBlockEntity.class)
public abstract class BotinSecretoMixin implements BotinSecreto {

    @Unique
    private boolean atalaya$secreto;

    @Override
    public void atalaya$guardarElSecreto() {
        this.atalaya$secreto = true;
    }

    @Override
    public boolean atalaya$esSecreto() {
        return this.atalaya$secreto;
    }

    @Inject(method = "saveAdditional", at = @At("TAIL"))
    private void atalaya$guardar(ValueOutput salida, CallbackInfo ci) {
        if (this.atalaya$secreto) {
            salida.putBoolean("atalaya_secreto", true);
        }
    }

    @Inject(method = "loadAdditional", at = @At("TAIL"))
    private void atalaya$cargar(ValueInput entrada, CallbackInfo ci) {
        this.atalaya$secreto = entrada.getBooleanOr("atalaya_secreto", false);
    }

    @Inject(method = "getUpdateTag", at = @At("RETURN"))
    private void atalaya$noEnsenarNada(HolderLookup.Provider registros,
                                       CallbackInfoReturnable<CompoundTag> cir) {
        if (!this.atalaya$secreto) {
            return;
        }
        BlockEntity yo = (BlockEntity) (Object) this;
        // Hasta la ultima pasada. Al llegar a tres el bloque se rompe en el
        // mismo instante, asi que ensenarlo entonces no adelanta nada.
        Integer limpieza = yo.getBlockState().getValue(BlockStateProperties.DUSTED);
        if (limpieza != null && limpieza < 3) {
            cir.getReturnValue().remove("item");
        }
    }
}
