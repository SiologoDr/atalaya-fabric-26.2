package com.atalaya.menu;

import com.atalaya.Atalaya;
import com.atalaya.items.HazmatRecipes;
import net.kyori.adventure.text.Component;
import net.kyori.adventure.text.format.NamedTextColor;
import org.bukkit.entity.Player;
import org.bukkit.event.EventHandler;
import org.bukkit.event.Listener;
import org.bukkit.event.inventory.InventoryClickEvent;

/**
 * Maneja los clicks en el menu de configuracion.
 */
public class ConfigMenuListener implements Listener {

    private final Atalaya plugin;

    public ConfigMenuListener(Atalaya plugin) {
        this.plugin = plugin;
    }

    @EventHandler
    public void onClick(InventoryClickEvent event) {
        if (!(event.getInventory().getHolder() instanceof ConfigMenu menu)) {
            return;
        }
        event.setCancelled(true); // evita que se saquen los iconos

        if (!(event.getWhoClicked() instanceof Player player)) {
            return;
        }

        var s = plugin.getSettings();
        int slot = event.getRawSlot();

        if (slot == ConfigMenu.SLOT_RADIACION) {
            boolean nuevoRad = !s.isRadiacionActiva();
            s.setRadiacionActiva(nuevoRad);
            if (!nuevoRad) {
                plugin.getRadiationManager().limpiarLentitudTodos(); // quita la lentitud al instante
            }
            avisar(player, "Radiacion", nuevoRad);
        } else if (slot == ConfigMenu.SLOT_CRAFTEO) {
            boolean nuevo = !s.isCrafteoActivo();
            s.setCrafteoActivo(nuevo);
            if (nuevo) {
                HazmatRecipes.activar(plugin);   // registra + desbloquea en el libro
            } else {
                HazmatRecipes.desactivar(plugin); // quita del crafteo y del libro
            }
            avisar(player, "Crafteo Hazmat", nuevo);
        } else {
            return;
        }

        menu.refrescar();
    }

    private void avisar(Player player, String que, boolean activo) {
        player.sendMessage(
                Component.text(que + ": ", NamedTextColor.GRAY)
                        .append(Component.text(activo ? "ACTIVADO" : "DESACTIVADO",
                                activo ? NamedTextColor.GREEN : NamedTextColor.RED))
        );
    }
}
