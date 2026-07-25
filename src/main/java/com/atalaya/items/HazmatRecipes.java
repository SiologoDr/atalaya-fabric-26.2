package com.atalaya.items;

import com.atalaya.Atalaya;
import org.bukkit.Bukkit;
import org.bukkit.Material;
import org.bukkit.NamespacedKey;
import org.bukkit.entity.Player;
import org.bukkit.inventory.ItemStack;
import org.bukkit.inventory.ShapedRecipe;

import java.util.ArrayList;
import java.util.List;

/**
 * Recetas de crafteo del traje Hazmat.
 *
 * Base tematica: oro (recubrimiento amarillo) + hierro (estructura) +
 * amatista (forro anti-radiacion, obtenida de las geodas). Al llevar amatista,
 * la forma no choca con la armadura de hierro vanilla.
 */
public final class HazmatRecipes {

    // Claves de las recetas, para desbloquearlas en el libro de cada jugador.
    private static final List<NamespacedKey> CLAVES = new ArrayList<>();

    private HazmatRecipes() {
    }

    public static void registrar(Atalaya plugin) {
        CLAVES.clear();
        // Idea: la pieza de armadura de HIERRO en el centro (X), recubierta de ORO (G).
        add(plugin, "receta_hazmat_casco", HazmatArmor.casco(), Material.IRON_HELMET,
                "GGG",
                "GXG");

        // Pechera: forma de chaleco (hueco en el cuello, arriba-centro).
        add(plugin, "receta_hazmat_pechera", HazmatArmor.pechera(), Material.IRON_CHESTPLATE,
                "G G",
                "GXG",
                "GGG");

        // Pantalon: forma de pantalon (hueco entre las piernas, abajo-centro).
        add(plugin, "receta_hazmat_pantalon", HazmatArmor.pantalon(), Material.IRON_LEGGINGS,
                "GGG",
                "GXG",
                "G G");

        add(plugin, "receta_hazmat_botas", HazmatArmor.botas(), Material.IRON_BOOTS,
                "GGG",
                "GXG");
    }

    private static void add(Atalaya plugin, String id, ItemStack resultado, Material nucleo, String... shape) {
        NamespacedKey key = new NamespacedKey(plugin, id);
        Bukkit.removeRecipe(key); // evita "duplicado" si el plugin se recarga

        ShapedRecipe receta = new ShapedRecipe(key, resultado);
        receta.shape(shape);

        // G = oro (recubrimiento);  X = la pieza de hierro que se recubre.
        String todo = String.join("", shape);
        if (todo.indexOf('G') >= 0) receta.setIngredient('G', Material.GOLD_INGOT);
        if (todo.indexOf('X') >= 0) receta.setIngredient('X', nucleo);

        Bukkit.addRecipe(receta);
        CLAVES.add(key);
    }

    /** Desbloquea las recetas en el libro de recetas del jugador. */
    public static void desbloquear(Player player) {
        player.discoverRecipes(CLAVES);
    }

    /** Activa el crafteo: registra las recetas y las desbloquea a los conectados. */
    public static void activar(Atalaya plugin) {
        registrar(plugin);
        for (Player p : plugin.getServer().getOnlinePlayers()) {
            p.discoverRecipes(CLAVES);
        }
    }

    /** Desactiva el crafteo: quita las recetas del juego y del libro de recetas. */
    public static void desactivar(Atalaya plugin) {
        List<NamespacedKey> claves = new ArrayList<>(CLAVES);
        for (Player p : plugin.getServer().getOnlinePlayers()) {
            p.undiscoverRecipes(claves); // fuera del libro de cada jugador
        }
        for (NamespacedKey key : claves) {
            Bukkit.removeRecipe(key);    // ya no se puede craftear
        }
        CLAVES.clear();
    }
}
