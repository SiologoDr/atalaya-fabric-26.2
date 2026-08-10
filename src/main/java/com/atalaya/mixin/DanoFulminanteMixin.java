package com.atalaya.mixin;

import com.atalaya.entity.FulminanteEntity;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.damagesource.DamageTypes;
import net.minecraft.world.entity.LivingEntity;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.ModifyVariable;

/**
 * Sube un 25% lo que hace la explosion del fulminante.
 *
 * Hace falta un mixin porque el radio del creeper es un campo ENTERO: de 3 solo
 * se puede pasar a 4, que ya es un tercio mas de radio y bastante mas de un
 * cuarto de dano, porque el dano de una explosion no crece en linea recta con
 * el radio. Tocando el numero del golpe se consigue el 25% clavado y ademas la
 * explosion sigue rompiendo los mismos bloques que la de un creeper normal, que
 * es lo que se quiere: mas dano, no mas destrozo.
 */
@Mixin(LivingEntity.class)
public abstract class DanoFulminanteMixin {

    private static final float EXTRA = 1.25F;

    @ModifyVariable(method = "hurtServer", at = @At("HEAD"), argsOnly = true, ordinal = 0)
    private float atalaya$explosionDelFulminante(float cantidad,
                                                 ServerLevel nivel,
                                                 DamageSource fuente,
                                                 float original) {
        if (cantidad <= 0) {
            return cantidad;
        }
        if (!fuente.is(DamageTypes.EXPLOSION) && !fuente.is(DamageTypes.PLAYER_EXPLOSION)) {
            return cantidad;
        }
        // getEntity y no getDirectEntity: en una explosion el causante es el
        // bicho, y el proyectil directo no existe.
        if (!(fuente.getEntity() instanceof FulminanteEntity)) {
            return cantidad;
        }
        return cantidad * EXTRA;
    }
}
