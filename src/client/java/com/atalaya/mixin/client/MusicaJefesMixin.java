package com.atalaya.mixin.client;

import com.atalaya.client.MusicaJefes;
import net.minecraft.client.sounds.MusicManager;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/**
 * Mientras suena la musica de un jefe (MusicaJefes), la de vanilla no se
 * mueve: ni empieza una pista nueva ni cambia la que hubiera. Al acabar la
 * pelea, MusicManager sigue como siempre y la musica del juego vuelve sola.
 */
@Mixin(MusicManager.class)
public abstract class MusicaJefesMixin {

    @Inject(method = "tick", at = @At("HEAD"), cancellable = true)
    private void atalaya$callarConJefe(CallbackInfo ci) {
        if (MusicaJefes.sonando()) {
            ci.cancel();
        }
    }
}
