package com.atalaya.mixin.client;

import com.atalaya.client.IconosArmadura;
import net.minecraft.client.gui.GuiGraphicsExtractor;
import net.minecraft.client.gui.Hud;
import net.minecraft.resources.Identifier;
import net.minecraft.world.entity.player.Player;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.ModifyArg;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/**
 * La barra de armadura con un conjunto entero puesto (IconosArmadura): al
 * empezar se mira que lleva, y cada icono (lleno, medio o vacio) se cambia por
 * el de su conjunto. El resto (cuantos, donde) lo sigue haciendo vanilla.
 */
@Mixin(Hud.class)
public abstract class IconosArmaduraMixin {

    @Inject(method = "extractArmor", at = @At("HEAD"))
    private static void atalaya$conjunto(GuiGraphicsExtractor g, Player p, int a, int b, int c, int d, CallbackInfo ci) {
        IconosArmadura.preparar(p);
    }

    @ModifyArg(method = "extractArmor", at = @At(value = "INVOKE",
            target = "Lnet/minecraft/client/gui/GuiGraphicsExtractor;blitSprite(Lcom/mojang/blaze3d/pipeline/RenderPipeline;Lnet/minecraft/resources/Identifier;IIII)V"),
            index = 1)
    private static Identifier atalaya$icono(Identifier vanilla) {
        return IconosArmadura.sprite(vanilla);
    }
}
