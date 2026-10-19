package com.atalaya.mixin;

import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.ai.goal.GoalSelector;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.gen.Accessor;

/**
 * Abre las cabezas de un mob (sus objetivos y a quien ataca), que son protegidas: los cambios de dificultad le ponen
 * cosas nuevas que hacer a los mobs de siempre (los zombis que pican y ponen bloques).
 */
@Mixin(Mob.class)
public interface MobAccessor {

    @Accessor("goalSelector")
    GoalSelector atalaya$objetivos();

    @Accessor("targetSelector")
    GoalSelector atalaya$presas();
}
