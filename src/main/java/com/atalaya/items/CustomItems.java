package com.atalaya.items;

import net.kyori.adventure.text.Component;
import net.kyori.adventure.text.format.NamedTextColor;
import org.bukkit.Material;
import org.bukkit.NamespacedKey;
import org.bukkit.inventory.ItemStack;
import org.bukkit.inventory.meta.ItemMeta;
import org.bukkit.persistence.PersistentDataType;
import org.bukkit.plugin.Plugin;

import java.util.List;

/**
 * Fabrica de items custom del plugin.
 *
 * Idea clave (server-side): un item "nuevo" es en realidad un item vanilla
 * (aqui un BLAZE_ROD) al que le cambiamos nombre, descripcion y comportamiento,
 * y le pegamos una marca invisible en su PersistentDataContainer para poder
 * reconocerlo despues aunque el jugador lo mueva, tire o guarde en un cofre.
 */
public final class CustomItems {

    // Llave que identifica nuestro "Baston de la Atalaya". Se inicializa en init().
    public static NamespacedKey BASTON_KEY;

    private CustomItems() {
    }

    /** Debe llamarse una vez en onEnable() antes de crear items. */
    public static void init(Plugin plugin) {
        BASTON_KEY = new NamespacedKey(plugin, "baston_atalaya");
    }

    /** Crea el Baston de la Atalaya. */
    public static ItemStack crearBaston() {
        ItemStack item = new ItemStack(Material.BLAZE_ROD);
        ItemMeta meta = item.getItemMeta();

        meta.displayName(Component.text("Baston de la Atalaya", NamedTextColor.GOLD));
        meta.lore(List.of(
                Component.text("Un baston con poder oculto.", NamedTextColor.GRAY),
                Component.text("Click derecho para invocar un rayo.", NamedTextColor.DARK_GRAY)
        ));

        // Marca invisible: byte = 1 bajo nuestra llave. Asi sabemos que es "nuestro".
        meta.getPersistentDataContainer().set(BASTON_KEY, PersistentDataType.BYTE, (byte) 1);

        item.setItemMeta(meta);
        return item;
    }

    /** Devuelve true si el item recibido es el Baston de la Atalaya. */
    public static boolean esBaston(ItemStack item) {
        if (item == null) {
            return false;
        }
        ItemMeta meta = item.getItemMeta();
        if (meta == null) {
            return false;
        }
        return meta.getPersistentDataContainer().has(BASTON_KEY, PersistentDataType.BYTE);
    }
}
