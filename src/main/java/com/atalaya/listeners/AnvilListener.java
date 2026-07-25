package com.atalaya.listeners;

import com.atalaya.items.HazmatArmor;
import net.kyori.adventure.text.serializer.plain.PlainTextComponentSerializer;
import org.bukkit.event.EventHandler;
import org.bukkit.event.Listener;
import org.bukkit.event.inventory.PrepareAnvilEvent;
import org.bukkit.inventory.AnvilInventory;
import org.bukkit.inventory.ItemStack;
import org.bukkit.inventory.meta.ItemMeta;

/**
 * Impide renombrar las piezas del traje Hazmat en el yunque.
 *
 * Bloquea cualquier cambio de nombre (escribir uno nuevo O borrarlo para
 * resetearlo), comparando el nombre del resultado con el original.
 * La reparacion/combinacion normal (que conserva el nombre) si se permite.
 */
public class AnvilListener implements Listener {

    @EventHandler
    public void onPrepareAnvil(PrepareAnvilEvent event) {
        AnvilInventory inv = event.getInventory();
        ItemStack base = inv.getItem(0); // el item que se renombra/repara

        if (!HazmatArmor.esHazmat(base)) {
            return; // no es una pieza Hazmat -> no nos metemos
        }

        ItemStack resultado = event.getResult();
        if (resultado == null) {
            return;
        }

        // Si el nombre del resultado cambia respecto al original, es un renombrado.
        if (!nombrePlano(base).equals(nombrePlano(resultado))) {
            event.setResult(null); // sin resultado -> no se puede renombrar
        }
    }

    private static String nombrePlano(ItemStack item) {
        ItemMeta meta = item.getItemMeta();
        if (meta == null || !meta.hasDisplayName()) {
            return "";
        }
        return PlainTextComponentSerializer.plainText().serialize(meta.displayName());
    }
}
