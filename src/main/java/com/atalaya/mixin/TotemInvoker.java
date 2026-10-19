package com.atalaya.mixin;

import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.LivingEntity;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.gen.Invoker;

/**
 * Abre el totem de vanilla (privado): si lleva uno en la mano, lo gasta como si fuera a morir (se queda a medio
 * corazon, con los efectos del totem, su animacion y su aviso). El Espectro Amarillo te hace gastar uno de un golpe.
 */
@Mixin(LivingEntity.class)
public interface TotemInvoker {

    @Invoker("checkTotemDeathProtection")
    boolean atalaya$gastarTotem(DamageSource fuente);
}
