package com.atalaya.mixin.cambios;

import com.atalaya.cambios.Cambio;
import com.atalaya.cambios.CambiosDificultad;
import com.atalaya.cambios.DanoCambios;
import com.atalaya.cambios.ReglasCambios;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.monster.zombie.Zombie;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.ModifyVariable;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/**
 * Lo que los cambios de dificultad tocan en cualquier ser vivo:
 *
 * <pre>
 *   hurtServer                   el dano (DanoCambios)
 *   decreaseAirSupply            el aire bajo el agua se acaba x5 (PULMONES DE PAPEL)
 *   canBreatheUnderwater         nada deja respirar bajo el agua (SIN BOLSAS DE AIRE)
 *   getVisibilityPercent         la invisibilidad no esconde (NARIZ DE SABUESO)
 *   onClimbable                  los zombis trepan como las aranas (ZOMBIS TREPADORES)
 *   checkTotemDeathProtection    el totem, a cara o cruz (CARA O CRUZ)
 * </pre>
 */
@Mixin(LivingEntity.class)
public abstract class CambiosVivosMixin {

    @ModifyVariable(method = "hurtServer", at = @At("HEAD"), argsOnly = true, ordinal = 0)
    private float atalaya$danoCambios(float cantidad, ServerLevel nivel, DamageSource fuente, float original) {
        return DanoCambios.modificar((LivingEntity) (Object) this, fuente, cantidad);
    }

    @Inject(method = "decreaseAirSupply", at = @At("RETURN"), cancellable = true)
    private void atalaya$pulmones(int aire, CallbackInfoReturnable<Integer> cir) {
        if ((Object) this instanceof Player p && !p.isCreative() && CambiosDificultad.activo(Cambio.PULMONES_DE_PAPEL)
                && cir.getReturnValueI() < aire) {
            cir.setReturnValue(aire - 5);
        }
    }

    @Inject(method = "canBreatheUnderwater", at = @At("HEAD"), cancellable = true)
    private void atalaya$sinBolsas(CallbackInfoReturnable<Boolean> cir) {
        if ((Object) this instanceof Player p && !p.isCreative() && CambiosDificultad.activo(Cambio.SIN_BOLSAS_DE_AIRE)) {
            cir.setReturnValue(false);
        }
    }

    @Inject(method = "getVisibilityPercent", at = @At("RETURN"), cancellable = true)
    private void atalaya$olfato(Entity quienMira, CallbackInfoReturnable<Double> cir) {
        LivingEntity yo = (LivingEntity) (Object) this;
        if (yo.isInvisible() && CambiosDificultad.activo(Cambio.NARIZ_DE_SABUESO)) {
            // Como si no fuera invisible: lo de la armadura y las cabezas sigue contando, la invisibilidad no.
            cir.setReturnValue(Math.max(cir.getReturnValueD(), 1.0));
        }
    }

    @Inject(method = "onClimbable", at = @At("HEAD"), cancellable = true)
    private void atalaya$zombiTrepa(CallbackInfoReturnable<Boolean> cir) {
        if ((Object) this instanceof Zombie z && z.horizontalCollision && !z.isNoGravity()
                && CambiosDificultad.activo(Cambio.ZOMBIS_TREPADORES)) {
            cir.setReturnValue(true);
        }
    }

    @Inject(method = "checkTotemDeathProtection", at = @At("HEAD"), cancellable = true)
    private void atalaya$caraOCruz(DamageSource fuente, CallbackInfoReturnable<Boolean> cir) {
        LivingEntity yo = (LivingEntity) (Object) this;
        if (!CambiosDificultad.activo(Cambio.CARA_O_CRUZ) || yo.level().isClientSide()) {
            return;
        }
        // Solo el totem de la inmortalidad de siempre (los del mod son de otra pasta).
        ItemStack principal = yo.getMainHandItem();
        ItemStack otra = yo.getOffhandItem();
        boolean vanilla = principal.is(Items.TOTEM_OF_UNDYING)
                || (!principal.has(net.minecraft.core.component.DataComponents.DEATH_PROTECTION) && otra.is(Items.TOTEM_OF_UNDYING));
        if (vanilla && yo.getRandom().nextBoolean()) {
            ReglasCambios.totemFallido(yo);
            cir.setReturnValue(false);
        }
    }
}
