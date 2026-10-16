package com.atalaya.mixin;

import com.atalaya.entity.FogonazoEntity;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.monster.Creeper;
import net.minecraft.world.level.Level;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Redirect;

/**
 * El estallido del Fogonazo: la explosion del creeper se cambia por la suya (la misma, con su sonido, el destello y el
 * blanco en la pantalla). El metodo que hace estallar al creeper es privado, asi que se entra por la llamada a explode;
 * los demas creepers siguen como siempre.
 */
@Mixin(Creeper.class)
public abstract class FogonazoMixin {

    @Redirect(method = "explodeCreeper", at = @At(value = "INVOKE",
            target = "Lnet/minecraft/server/level/ServerLevel;explode(Lnet/minecraft/world/entity/Entity;DDDFLnet/minecraft/world/level/Level$ExplosionInteraction;)V"))
    private void atalaya$estallar(ServerLevel nivel, Entity quien, double x, double y, double z, float radio,
                                 Level.ExplosionInteraction interaccion) {
        if (quien instanceof FogonazoEntity fogonazo) {
            fogonazo.estallar(nivel, x, y, z, radio, interaccion);
        } else {
            nivel.explode(quien, x, y, z, radio, interaccion);
        }
    }
}
