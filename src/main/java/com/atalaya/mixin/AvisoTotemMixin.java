package com.atalaya.mixin;

import net.minecraft.ChatFormatting;
import net.minecraft.data.AtlasIds;
import net.minecraft.network.chat.Component;
import net.minecraft.network.chat.contents.objects.AtlasSprite;
import net.minecraft.resources.Identifier;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.LivingEntity;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/**
 * Cuando un jugador gasta un totem de la inmortalidad, lo sabe todo el
 * servidor: "<b>Manu</b> ha usado un totem de la inmortalidad [icono]", con el
 * nombre en negrita y el icono del totem dentro del propio chat (un sprite del
 * atlas de objetos, sin texturas nuevas).
 *
 * Va siempre encendido: es un aviso, no una mecanica.
 */
@Mixin(LivingEntity.class)
public abstract class AvisoTotemMixin {

    private static final Identifier TOTEM = Identifier.withDefaultNamespace("item/totem_of_undying");

    @Inject(method = "checkTotemDeathProtection", at = @At("RETURN"))
    private void atalaya$avisarTotem(DamageSource fuente, CallbackInfoReturnable<Boolean> cir) {
        if (!cir.getReturnValueZ() || !((Object) this instanceof ServerPlayer jugador)) {
            return;
        }
        Component nombre = jugador.getDisplayName().copy().withStyle(ChatFormatting.BOLD);
        Component icono = Component.object(new AtlasSprite(AtlasIds.ITEMS, TOTEM));
        Component aviso = Component.translatable("chat.atalaya.totem", nombre, icono).withStyle(ChatFormatting.YELLOW);
        jugador.level().getServer().getPlayerList().broadcastSystemMessage(aviso, false);
    }
}
