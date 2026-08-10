package com.atalaya.mixin;

import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.SpawnPlacementType;
import net.minecraft.world.entity.SpawnPlacements;
import net.minecraft.world.level.levelgen.Heightmap;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.gen.Invoker;

/**
 * Abre el registro de reglas de aparicion, que es privado.
 *
 * Sin esto no hay forma de decirle al juego DONDE puede aparecer un bicho
 * propio: en que suelo, a que altura y con que condiciones. Vanilla lo apunta
 * todo en un mapa interno desde un bloque estatico y no deja mas puerta.
 *
 * El predicado usa el tipo de vanilla tal cual. Se probo a declarar una copia
 * aqui dentro y el juego no arranca: todo lo que vive en un paquete de mixins
 * lo reclama el motor de mixins y no se puede referenciar desde codigo normal
 * —"is in a defined mixin package ... and cannot be referenced directly"—.
 */
@Mixin(SpawnPlacements.class)
public interface SpawnPlacementsInvoker {

    @Invoker("register")
    static <T extends Mob> void atalaya$registrar(EntityType<T> tipo,
                                                  SpawnPlacementType colocacion,
                                                  Heightmap.Types mapaAlturas,
                                                  SpawnPlacements.SpawnPredicate<T> condicion) {
        throw new AssertionError("lo reemplaza el mixin");
    }
}
