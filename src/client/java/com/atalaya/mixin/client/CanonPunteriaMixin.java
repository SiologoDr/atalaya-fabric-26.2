package com.atalaya.mixin.client;

import com.atalaya.entity.CanonNaufragioEntity;
import com.llamalad7.mixinextras.injector.ModifyExpressionValue;
import net.minecraft.client.Minecraft;
import net.minecraft.client.MouseHandler;
import net.minecraft.client.player.LocalPlayer;
import org.spongepowered.asm.mixin.Final;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;

/**
 * Por el catalejo del canon se apunta despacio, como por el de vanilla: vanilla
 * frena el raton cuando se mira por un catalejo, y aqui tambien cuando se va
 * subido a un Canon del Naufragio.
 */
@Mixin(MouseHandler.class)
public abstract class CanonPunteriaMixin {

    @Shadow
    @Final
    private Minecraft minecraft;

    @ModifyExpressionValue(method = "turnPlayer",
            at = @At(value = "INVOKE", target = "Lnet/minecraft/client/player/LocalPlayer;isScoping()Z"))
    private boolean atalaya$despacioEnElCanon(boolean mirando) {
        LocalPlayer yo = minecraft.player;
        return mirando || (yo != null && yo.getVehicle() instanceof CanonNaufragioEntity);
    }
}
