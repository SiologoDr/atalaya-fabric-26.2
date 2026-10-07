package com.atalaya.mixin;

import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.world.entity.projectile.arrow.ThrownTrident;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.gen.Accessor;

/**
 * La lealtad del tridente es un dato sincronizado privado: el Tridente de las
 * Mareas la pone a mano para volver siempre sin estar encantado.
 */
@Mixin(ThrownTrident.class)
public interface ThrownTridentAccessor {

    @Accessor("ID_LOYALTY")
    static EntityDataAccessor<Byte> atalaya$lealtad() {
        throw new AssertionError();
    }
}
