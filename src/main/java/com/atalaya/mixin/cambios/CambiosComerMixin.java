package com.atalaya.mixin.cambios;

import com.atalaya.cambios.Cambio;
import com.atalaya.cambios.CambiosDificultad;
import com.atalaya.cambios.Plaga;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.Level;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/**
 * Lo que pasa al acabar de comer o beber algo:
 * <pre>
 *   MANZANAS VACIAS    la manzana de oro (y la encantada) ya no deja absorcion
 *   MORDISCO PUTRIDO   la manzana de oro con debilidad cura la plaga del mordisco
 * </pre>
 */
@Mixin(ItemStack.class)
public abstract class CambiosComerMixin {

    @Unique
    private boolean atalaya$manzana;

    @Inject(method = "finishUsingItem", at = @At("HEAD"))
    private void atalaya$antes(Level nivel, LivingEntity quien, CallbackInfoReturnable<ItemStack> cir) {
        ItemStack yo = (ItemStack) (Object) this;
        atalaya$manzana = yo.is(Items.GOLDEN_APPLE) || yo.is(Items.ENCHANTED_GOLDEN_APPLE);
        if (atalaya$manzana && !nivel.isClientSide() && quien instanceof Player p) {
            // La cura va antes de que la manzana quite nada (la debilidad tiene que seguir puesta).
            Plaga.alComerManzana(p);
        }
    }

    @Inject(method = "finishUsingItem", at = @At("RETURN"))
    private void atalaya$despues(Level nivel, LivingEntity quien, CallbackInfoReturnable<ItemStack> cir) {
        if (atalaya$manzana && !nivel.isClientSide() && CambiosDificultad.activo(Cambio.MANZANAS_VACIAS)) {
            quien.removeEffect(MobEffects.ABSORPTION);
        }
        atalaya$manzana = false;
    }
}
