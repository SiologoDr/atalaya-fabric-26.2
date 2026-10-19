package com.atalaya.mixin.cambios;

import com.atalaya.cambios.Cambio;
import com.atalaya.cambios.CambiosDificultad;
import com.atalaya.cambios.ReglasCambios;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.npc.villager.Villager;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/** ALDEAS VIGILADAS: cuando los aldeanos llaman a su golem de hierro, sale un warden. */
@Mixin(Villager.class)
public abstract class CambiosGolemAldeaMixin {

    @Inject(method = "spawnGolemIfNeeded", at = @At("HEAD"), cancellable = true)
    private void atalaya$warden(ServerLevel nivel, long ahora, int cuantos, CallbackInfo ci) {
        if (CambiosDificultad.activo(Cambio.ALDEAS_VIGILADAS)) {
            Villager yo = (Villager) (Object) this;
            if (yo.wantsToSpawnGolem(ahora)) {
                ReglasCambios.wardenDeAldea(nivel, yo, cuantos);
            }
            ci.cancel();
        }
    }
}
