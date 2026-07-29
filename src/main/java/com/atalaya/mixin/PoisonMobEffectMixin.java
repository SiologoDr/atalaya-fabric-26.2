package com.atalaya.mixin;

import com.atalaya.item.HazmatArmor;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.effect.PoisonMobEffect;
import net.minecraft.world.entity.LivingEntity;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Redirect;

/**
 * Reduce el DANO del veneno segun cuantas piezas del traje lleven colmillo.
 *
 * Se toca la llamada concreta que hace PoisonMobEffect en vez de filtrar por
 * tipo de dano: el veneno usa la fuente "magic", que comparte con pociones de
 * dano y otras cosas. Interceptando aqui solo se afecta al veneno.
 *
 * Cada pieza mejorada anula un 25%: una deja el golpe en 0.75, dos en 0.5,
 * y las cuatro lo dejan en nada.
 */
@Mixin(PoisonMobEffect.class)
public class PoisonMobEffectMixin {

    @Redirect(
            method = "applyEffectTick",
            at = @At(value = "INVOKE",
                    target = "Lnet/minecraft/world/entity/LivingEntity;hurtServer("
                            + "Lnet/minecraft/server/level/ServerLevel;"
                            + "Lnet/minecraft/world/damagesource/DamageSource;F)Z"))
    private boolean atalaya$reducirDanoDeVeneno(LivingEntity entidad,
                                                ServerLevel nivel,
                                                DamageSource fuente,
                                                float dano) {
        float factor = HazmatArmor.factorVeneno(entidad);
        if (factor <= 0f) {
            return false; // traje completo con colmillos: inmune
        }
        return entidad.hurtServer(nivel, fuente, dano * factor);
    }
}
