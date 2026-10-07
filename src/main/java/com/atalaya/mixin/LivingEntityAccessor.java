package com.atalaya.mixin;

import net.minecraft.world.entity.LivingEntity;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.gen.Accessor;

/**
 * Abre el ultimo golpe recibido, que es protegido.
 *
 * La Muralla de Jade le pasa al tanque parte del dano de sus aliados. Ese golpe
 * no debe darle ni quitarle invulnerabilidad: se guarda lo de antes, se le pega
 * y se deja como estaba, y para eso hace falta tocar este campo.
 */
@Mixin(LivingEntity.class)
public interface LivingEntityAccessor {

    @Accessor("lastHurt")
    float atalaya$ultimoGolpe();

    @Accessor("lastHurt")
    void atalaya$ponerUltimoGolpe(float cantidad);
}
