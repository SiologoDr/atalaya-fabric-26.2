package com.atalaya.mixin;

import com.atalaya.entity.ColisionGrande;
import java.util.List;
import java.util.function.Predicate;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.AABB;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/**
 * Las busquedas de entidades por caja tambien encuentran las grandes que se
 * pisan (ColisionGrande): vanilla no las veia si su centro caia en otra seccion,
 * y los estrados de las Trompetas se atravesaban.
 */
@Mixin(Level.class)
public abstract class LevelEntidadesMixin {

    @Inject(method = "getEntities(Lnet/minecraft/world/entity/Entity;Lnet/minecraft/world/phys/AABB;Ljava/util/function/Predicate;)Ljava/util/List;",
            at = @At("RETURN"))
    private void atalaya$grandes(Entity salvo, AABB caja, Predicate<? super Entity> filtro, CallbackInfoReturnable<List<Entity>> cir) {
        ColisionGrande.completar((Level) (Object) this, salvo, caja, filtro, cir.getReturnValue());
    }
}
