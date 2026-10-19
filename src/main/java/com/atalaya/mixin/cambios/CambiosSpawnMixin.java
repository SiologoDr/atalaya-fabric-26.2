package com.atalaya.mixin.cambios;

import com.atalaya.cambios.ReglasCambios;
import net.minecraft.core.BlockPos;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.EntitySpawnReason;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.MobCategory;
import net.minecraft.world.entity.SpawnPlacements;
import net.minecraft.world.level.ServerLevelAccessor;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/** EXTINCION: los animales ya no salen solos (ni al generarse el mundo). */
@Mixin(SpawnPlacements.class)
public abstract class CambiosSpawnMixin {

    @Inject(method = "checkSpawnRules", at = @At("HEAD"), cancellable = true)
    private static void atalaya$extincion(EntityType<?> tipo, ServerLevelAccessor nivel, EntitySpawnReason motivo,
                                          BlockPos pos, RandomSource azar, CallbackInfoReturnable<Boolean> cir) {
        if (tipo.getCategory() == MobCategory.CREATURE && !ReglasCambios.animalPuedeSalir(motivo)) {
            cir.setReturnValue(false);
        }
    }
}
