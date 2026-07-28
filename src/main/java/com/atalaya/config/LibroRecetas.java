package com.atalaya.config;

import com.atalaya.Atalaya;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.item.crafting.RecipeHolder;

import java.util.ArrayList;
import java.util.List;

/**
 * Mantiene el libro de recetas de acuerdo con los interruptores del menu.
 *
 * El mixin de RecipeManager impide FABRICAR una receta desactivada, pero el
 * libro de recetas es otra cosa: lo lleva el servidor por jugador y no consulta
 * al buscador. Sin esto, una receta apagada seguiria apareciendo en el libro
 * como si se pudiera hacer.
 *
 * Solo toca recetas de este mod: las de vanilla y las de otros mods se quedan
 * como estan.
 */
public final class LibroRecetas {

    private LibroRecetas() {
    }

    /** Ajusta el libro de todos los jugadores conectados al estado actual. */
    public static void sincronizarTodos(MinecraftServer servidor) {
        for (ServerPlayer jugador : servidor.getPlayerList().getPlayers()) {
            sincronizar(jugador);
        }
    }

    /** Ajusta el libro de un jugador al estado actual de los interruptores. */
    public static void sincronizar(ServerPlayer jugador) {
        // En 26.2 ServerPlayer no expone getServer(): se llega por el nivel.
        MinecraftServer servidor = jugador.level().getServer();
        if (servidor == null) {
            return;
        }
        AtalayaConfig cfg = AtalayaConfig.get();

        List<RecipeHolder<?>> permitidas = new ArrayList<>();
        List<RecipeHolder<?>> prohibidas = new ArrayList<>();

        for (RecipeHolder<?> receta : servidor.getRecipeManager().getRecipes()) {
            var id = receta.id().identifier();
            if (!Atalaya.MOD_ID.equals(id.getNamespace())) {
                continue; // no es nuestra: ni la miramos
            }
            if (cfg.permiteReceta(id)) {
                permitidas.add(receta);
            } else {
                prohibidas.add(receta);
            }
        }

        // Quitar primero y anadir despues: si una receta cambia de lado, el
        // orden asi deja el estado correcto.
        if (!prohibidas.isEmpty()) {
            jugador.resetRecipes(prohibidas);
        }
        if (!permitidas.isEmpty()) {
            jugador.awardRecipes(permitidas);
        }
    }
}
