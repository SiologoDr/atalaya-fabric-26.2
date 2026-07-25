package com.atalaya.menu;

import com.atalaya.Atalaya;
import net.kyori.adventure.text.Component;
import net.kyori.adventure.text.format.NamedTextColor;
import net.kyori.adventure.text.format.TextDecoration;
import org.bukkit.Bukkit;
import org.bukkit.Material;
import org.bukkit.NamespacedKey;
import org.bukkit.entity.Player;
import org.bukkit.inventory.Inventory;
import org.bukkit.inventory.InventoryHolder;
import org.bukkit.inventory.ItemStack;
import org.bukkit.inventory.meta.ItemMeta;

import java.util.List;

/**
 * Menu de configuracion (GUI) con toggles para activar/desactivar mecanicas.
 * Implementa InventoryHolder para reconocer el menu en los clicks.
 */
public class ConfigMenu implements InventoryHolder {

    public static final int SLOT_RADIACION = 11;
    public static final int SLOT_CRAFTEO = 15;

    private final Atalaya plugin;
    private Inventory inv;

    public ConfigMenu(Atalaya plugin) {
        this.plugin = plugin;
    }

    @Override
    public Inventory getInventory() {
        return inv;
    }

    public void abrir(Player player) {
        inv = Bukkit.createInventory(this, 27,
                Component.text("Atalaya - Configuracion", NamedTextColor.DARK_AQUA));
        refrescar();
        player.openInventory(inv);
    }

    /** Actualiza los iconos segun el estado actual. */
    public void refrescar() {
        var s = plugin.getSettings();
        inv.setItem(SLOT_RADIACION, toggle(new ItemStack(Material.AMETHYST_CLUSTER),
                "Radiacion de las geodas", s.isRadiacionActiva(),
                "Dana a quienes se acercan a una geoda natural."));
        inv.setItem(SLOT_CRAFTEO, toggle(iconoCasco(),
                "Crafteo del traje Hazmat", s.isCrafteoActivo(),
                "Permite craftear el traje y verlo en el libro de recetas."));
    }

    /** Casco de hierro con el icono custom del Hazmat (atalaya:hazmat_helmet). */
    private ItemStack iconoCasco() {
        ItemStack item = new ItemStack(Material.IRON_HELMET);
        ItemMeta meta = item.getItemMeta();
        meta.setItemModel(new NamespacedKey("atalaya", "hazmat_helmet"));
        item.setItemMeta(meta);
        return item;
    }

    /** Aplica nombre/lore/estado a un icono base. Brilla si esta activo. */
    private ItemStack toggle(ItemStack base, String nombre, boolean activo, String descripcion) {
        ItemMeta meta = base.getItemMeta();
        meta.displayName(txt(nombre, activo ? NamedTextColor.GREEN : NamedTextColor.RED)
                .decorate(TextDecoration.BOLD));
        meta.lore(List.of(
                txt(descripcion, NamedTextColor.GRAY),
                Component.empty(),
                txt("Estado: ", NamedTextColor.GRAY)
                        .append(txt(activo ? "ACTIVADO" : "DESACTIVADO",
                                activo ? NamedTextColor.GREEN : NamedTextColor.RED)),
                txt("Click para cambiar", NamedTextColor.YELLOW)
        ));
        meta.setEnchantmentGlintOverride(activo);
        base.setItemMeta(meta);
        return base;
    }

    private static Component txt(String s, NamedTextColor color) {
        return Component.text(s, color).decoration(TextDecoration.ITALIC, false);
    }
}
