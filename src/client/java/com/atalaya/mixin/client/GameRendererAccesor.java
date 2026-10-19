package com.atalaya.mixin.client;

import net.minecraft.client.renderer.GameRenderer;
import net.minecraft.resources.Identifier;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.gen.Invoker;

/** Abre el efecto de pantalla del juego (privado): el deslumbrado de NO MIRES AL SOL pone el suyo. */
@Mixin(GameRenderer.class)
public interface GameRendererAccesor {

    @Invoker("setPostEffect")
    void atalaya$ponerEfecto(Identifier efecto);
}
