package com.atalaya.mixin;

import net.minecraft.world.entity.decoration.Mannequin;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.gen.Invoker;

/**
 * Abre el texto de debajo del nombre del maniqui (el "NPC" de vanilla), que es
 * privado. Las copias del Impostor de Jade de Rajang lo esconden: tienen que
 * parecer jugadores, con su nombre encima y nada mas.
 */
@Mixin(Mannequin.class)
public interface ManiquiAccessor {

    @Invoker("setHideDescription")
    void atalaya$ocultarDescripcion(boolean ocultar);
}
