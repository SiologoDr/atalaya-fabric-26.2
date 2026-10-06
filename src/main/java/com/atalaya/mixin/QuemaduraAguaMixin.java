package com.atalaya.mixin;

import com.atalaya.effect.QuemaduraEffect;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.alchemy.PotionContents;
import net.minecraft.world.item.alchemy.Potions;
import net.minecraft.world.item.component.Consumable;
import net.minecraft.world.level.Level;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/**
 * Beberse una botella de agua apaga la quemadura de Novilis.
 *
 * Meterse en el agua no (lo pidio asi Juan): hay que llevar botellas. Se
 * engancha al consumir el contenido de una pocion, que es lo que hace la
 * botella de agua al beberse (sus efectos son ninguno: solo importa que sea
 * agua).
 */
@Mixin(PotionContents.class)
public abstract class QuemaduraAguaMixin {

    @Inject(method = "onConsume", at = @At("HEAD"))
    private void atalaya$apagarQuemadura(Level nivel, LivingEntity entidad, ItemStack pila, Consumable consumible,
                                         CallbackInfo ci) {
        if (!nivel.isClientSide() && ((PotionContents) (Object) this).is(Potions.WATER)) {
            QuemaduraEffect.apagar(entidad);
        }
    }
}
