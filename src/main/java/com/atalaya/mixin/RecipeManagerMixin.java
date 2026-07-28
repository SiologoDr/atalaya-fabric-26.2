package com.atalaya.mixin;

import com.atalaya.config.AtalayaConfig;
import net.minecraft.world.item.crafting.RecipeHolder;
import net.minecraft.world.item.crafting.RecipeManager;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

import java.util.Optional;

/**
 * Hace cumplir los interruptores de recetas del menu.
 *
 * Las recetas son datos y no se pueden quitar del juego en caliente, asi que se
 * filtra la BUSQUEDA: si la receta encontrada es nuestra y su interruptor esta
 * apagado, se devuelve vacio y para el juego es como si no existiera.
 *
 * Se engancha en RecipeManager y no en la mesa de crafteo porque por aqui pasan
 * TODAS las recetas: mesa, horno, alto horno, ahumador y las que anadamos luego.
 * Un solo punto en vez de uno por tipo de estacion.
 *
 * Hay dos inyecciones a proposito. Las tres sobrecargas de getRecipeFor se
 * delegan en cascada, pero la que recibe un RecipeHolder tiene SALIDA TEMPRANA
 * cuando la receta cacheada de la vez anterior sigue encajando: por ese camino
 * no se llega a la version de tres argumentos. Sin cubrir las dos, una receta
 * recien desactivada seguiria saliendo mientras durase esa cache.
 */
@Mixin(RecipeManager.class)
public class RecipeManagerMixin {

    private static final String TIPO = "Lnet/minecraft/world/item/crafting/RecipeType;";
    private static final String ENTRADA = "Lnet/minecraft/world/item/crafting/RecipeInput;";
    private static final String NIVEL = "Lnet/minecraft/world/level/Level;";
    private static final String SOSTEN = "Lnet/minecraft/world/item/crafting/RecipeHolder;";
    private static final String OPCIONAL = "Ljava/util/Optional;";

    /** Version terminal: la que consulta de verdad el mapa de recetas. */
    @Inject(method = "getRecipeFor(" + TIPO + ENTRADA + NIVEL + ")" + OPCIONAL,
            at = @At("RETURN"), cancellable = true)
    private void atalaya$filtrarBusqueda(CallbackInfoReturnable<Optional<RecipeHolder<?>>> cir) {
        filtrar(cir);
    }

    /** Version con receta cacheada: puede devolver sin pasar por la terminal. */
    @Inject(method = "getRecipeFor(" + TIPO + ENTRADA + NIVEL + SOSTEN + ")" + OPCIONAL,
            at = @At("RETURN"), cancellable = true)
    private void atalaya$filtrarCache(CallbackInfoReturnable<Optional<RecipeHolder<?>>> cir) {
        filtrar(cir);
    }

    private static void filtrar(CallbackInfoReturnable<Optional<RecipeHolder<?>>> cir) {
        Optional<RecipeHolder<?>> resultado = cir.getReturnValue();
        if (resultado == null || resultado.isEmpty()) {
            return;
        }
        if (!AtalayaConfig.get().permiteReceta(resultado.get().id().identifier())) {
            cir.setReturnValue(Optional.empty());
        }
    }
}
