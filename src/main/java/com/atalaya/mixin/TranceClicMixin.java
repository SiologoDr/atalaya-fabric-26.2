package com.atalaya.mixin;

import com.atalaya.entity.TranceSirena;
import net.minecraft.network.protocol.game.ServerboundSwingPacket;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.server.network.ServerGamePacketListenerImpl;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/**
 * El clic izquierdo de un jugador llega al servidor como "mueve el brazo"
 * aunque no le de a nada: si esta en el trance del Canto de Sirena, cuenta para
 * salir de el (TranceSirena); en los minijuegos de Aeralis lanza la Chispa o
 * descarga el Pararrayos al que mira (MinijuegosAeralis.alBlandir).
 */
@Mixin(ServerGamePacketListenerImpl.class)
public abstract class TranceClicMixin {

    @Shadow
    public ServerPlayer player;

    @Inject(method = "handleAnimate", at = @At("TAIL"))
    private void atalaya$clicEnTrance(ServerboundSwingPacket paquete, CallbackInfo ci) {
        TranceSirena.alGolpear(player);
        com.atalaya.entity.MinijuegosAeralis.alBlandir(player);
    }
}
