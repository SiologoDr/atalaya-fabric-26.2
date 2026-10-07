package com.atalaya.mixin;

import com.atalaya.habilidad.Habilidades;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.LivingEntity;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.ModifyVariable;

/**
 * El dano que entra en cualquier ser vivo pasa por las habilidades de las
 * armaduras: lo que pega de mas el fuego, lo que aguanta de menos el tanque y
 * quien tiene cerca, la parte que la Muralla de Jade le pasa al tanque. Los
 * golpes letales de los jefes pasan sin tocar (lo decide Habilidades).
 */
@Mixin(LivingEntity.class)
public abstract class DanoHabilidadesMixin {

    @ModifyVariable(method = "hurtServer", at = @At("HEAD"), argsOnly = true, ordinal = 0)
    private float atalaya$habilidades(float cantidad, ServerLevel nivel, DamageSource fuente, float original) {
        return Habilidades.modificarDano((LivingEntity) (Object) this, fuente, cantidad);
    }
}
