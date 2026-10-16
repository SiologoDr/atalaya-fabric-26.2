package com.atalaya.mixin.client;

import com.atalaya.client.MomentoMaldicionCliente;
import net.minecraft.client.Camera;
import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.client.renderer.SkyRenderer;
import net.minecraft.client.renderer.state.level.SkyRenderState;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/**
 * Mientras dura el Momento Maldicion no se ven el sol ni la luna: el cielo es
 * el cristal roto (CieloRoto), y el sol de mediodia asomaba por la grieta de
 * lo alto (revision del 16-10-2026). Se apagan como con lluvia, con el mismo
 * fundido que el cielo maldito.
 */
@Mixin(SkyRenderer.class)
public abstract class SolMomentoMixin {

    @Inject(method = "extractRenderState", at = @At("RETURN"))
    private void atalaya$sinSol(ClientLevel nivel, float parcial, Camera camara, SkyRenderState estado, CallbackInfo ci) {
        float k = MomentoMaldicionCliente.cielo(parcial);
        if (k > 0.0F) {
            estado.rainBrightness *= 1.0F - k;
        }
    }
}
