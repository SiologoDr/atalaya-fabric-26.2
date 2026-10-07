package com.atalaya.mixin.client;

import com.atalaya.client.IndicadorGolpe;
import net.minecraft.client.Minecraft;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.phys.Vec3;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/**
 * El cliente se entera de que al jugador le han hecho dano (el paquete del evento
 * de dano): si el golpe viene de un sitio, se lo pasa a IndicadorGolpe.
 */
@Mixin(LivingEntity.class)
public abstract class GolpeRecibidoMixin {

    @Inject(method = "handleDamageEvent", at = @At("HEAD"))
    private void atalaya$deDonde(DamageSource fuente, CallbackInfo ci) {
        if ((Object) this != Minecraft.getInstance().player) {
            return;
        }
        Vec3 desde = fuente.getSourcePosition();
        if (desde != null) {
            IndicadorGolpe.registrar(desde);
        }
    }
}
