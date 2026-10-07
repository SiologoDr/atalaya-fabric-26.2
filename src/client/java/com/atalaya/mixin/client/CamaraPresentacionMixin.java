package com.atalaya.mixin.client;

import com.atalaya.client.PresentacionJefe;
import net.minecraft.client.Camera;
import net.minecraft.client.DeltaTracker;
import net.minecraft.world.phys.Vec3;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/**
 * La camara de la presentacion de un jefe (PresentacionJefe): justo despues de
 * que vanilla la ponga en los ojos del jugador (o detras, en tercera persona),
 * la lleva a la toma de cine. Vanilla calcula despues la vista y el recorte
 * con esta posicion. Mientras la camara esta fuera, "detached": se ve el cuerpo
 * del jugador y no su mano.
 */
@Mixin(Camera.class)
public abstract class CamaraPresentacionMixin {

    @Shadow
    private boolean detached;

    @Shadow
    protected abstract void setPosition(Vec3 p);

    @Shadow
    protected abstract void setRotation(float yRot, float xRot);

    @Shadow
    public abstract Vec3 position();

    @Shadow
    public abstract float yRot();

    @Shadow
    public abstract float xRot();

    @Shadow
    public abstract float getCameraEntityPartialTicks(DeltaTracker delta);

    @Inject(method = "update", at = @At(value = "INVOKE", target = "Lnet/minecraft/client/Camera;alignWithEntity(F)V",
            shift = At.Shift.AFTER))
    private void atalaya$presentacion(DeltaTracker delta, CallbackInfo ci) {
        if (!PresentacionJefe.activa()) {
            return;
        }
        PresentacionJefe.Toma toma = PresentacionJefe.toma(getCameraEntityPartialTicks(delta), position(), yRot(), xRot());
        if (toma == null) {
            return;
        }
        setRotation(toma.yRot(), toma.xRot());
        setPosition(toma.pos());
        if (toma.fuera()) {
            detached = true;
        }
    }
}
