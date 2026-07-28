package com.atalaya.items;

import net.kyori.adventure.text.Component;
import net.kyori.adventure.text.format.TextColor;
import net.kyori.adventure.text.format.TextDecoration;
import org.bukkit.Material;
import org.bukkit.NamespacedKey;
import org.bukkit.entity.Player;
import org.bukkit.inventory.EquipmentSlot;
import org.bukkit.inventory.ItemStack;
import org.bukkit.inventory.meta.ItemMeta;
import org.bukkit.inventory.meta.components.EquippableComponent;
import org.bukkit.persistence.PersistentDataType;
import org.bukkit.plugin.Plugin;

import java.util.ArrayList;
import java.util.List;

/**
 * Traje anti-radiacion (Hazmat).
 *
 * Base = armadura de HIERRO (misma proteccion). Aspecto custom via item_model.
 * Cada pieza lleva una marca (PersistentDataContainer) para reconocerla y saber
 * cuantas piezas del traje lleva puesto un jugador (para la proteccion).
 */
public final class HazmatArmor {

    // Tonos CLAROS para que el texto se lea sobre el fondo oscuro del tooltip.
    private static final TextColor AMARILLO = TextColor.color(0xFCFC54);    // titulos
    private static final TextColor GRIS = TextColor.color(0xA8A8A8);        // tipo de pieza
    private static final TextColor VERDE_RAD = TextColor.color(0x8CE05A);   // verde
    private static final TextColor LILA_GEODA = TextColor.color(0xE4A8FF);  // lila

    // Marca que identifica una pieza del traje. Se inicializa en init().
    public static NamespacedKey HAZMAT_KEY;

    private HazmatArmor() {
    }

    public static void init(Plugin plugin) {
        HAZMAT_KEY = new NamespacedKey(plugin, "hazmat");
    }

    /**
     * Textura que el cliente dibuja a pantalla completa mientras llevas el casco:
     * el cristal ahumado del visor. Es el mismo mecanismo que usa la calabaza
     * tallada (camera_overlay del componente equippable).
     */
    private static final NamespacedKey VISOR = new NamespacedKey("atalaya", "misc/hazmat_visor");

    public static ItemStack casco() {
        return pieza(Material.IRON_HELMET, "hazmat_helmet", "Casco", EquipmentSlot.HEAD, VISOR);
    }

    public static ItemStack pechera() {
        return pieza(Material.IRON_CHESTPLATE, "hazmat_chestplate", "Pechera", EquipmentSlot.CHEST, null);
    }

    public static ItemStack pantalon() {
        return pieza(Material.IRON_LEGGINGS, "hazmat_leggings", "Pantalon", EquipmentSlot.LEGS, null);
    }

    public static ItemStack botas() {
        return pieza(Material.IRON_BOOTS, "hazmat_boots", "Botas", EquipmentSlot.FEET, null);
    }

    /**
     * @param overlay textura a pantalla completa mientras la pieza esta puesta,
     *                o null si la pieza no tapa la vista (todas menos el casco)
     */
    private static ItemStack pieza(Material base, String modelo, String tipo,
                                   EquipmentSlot slot, NamespacedKey overlay) {
        ItemStack item = new ItemStack(base);
        ItemMeta meta = item.getItemMeta();

        // Titulo: el tipo en gris + "Hazmat" pintado y en negrita.
        meta.displayName(
                txt(tipo + " ", GRIS)
                        .append(txt("Hazmat", AMARILLO).decorate(TextDecoration.BOLD))
        );
        meta.lore(construirLore());

        // Icono en inventario/mano (item_model).
        meta.setItemModel(new NamespacedKey("atalaya", modelo));

        // Aspecto del traje PUESTO sobre el cuerpo: equipment atalaya:hazmat (2 capas).
        EquippableComponent eq = meta.getEquippable();
        eq.setSlot(slot);
        eq.setModel(new NamespacedKey("atalaya", "hazmat"));
        if (overlay != null) {
            eq.setCameraOverlay(overlay);
        }
        meta.setEquippable(eq);

        meta.getPersistentDataContainer().set(HAZMAT_KEY, PersistentDataType.BYTE, (byte) 1);

        item.setItemMeta(meta);
        return item;
    }

    private static List<Component> construirLore() {
        List<Component> l = new ArrayList<>();
        l.add(Component.empty());
        // El icono NO se subraya; solo la palabra "Caracteristicas".
        l.add(txt("☢ ", AMARILLO)
                .append(txt("Caracteristicas", AMARILLO).decorate(TextDecoration.UNDERLINED)));
        l.add(Component.empty()); // espacio entre el titulo y los puntos
        l.add(txt("• Resiste un 25% la radiacion de la ", VERDE_RAD)
                .append(txt("Geoda", LILA_GEODA)));
        return l;
    }

    private static Component txt(String s, TextColor color) {
        return Component.text(s, color).decoration(TextDecoration.ITALIC, false);
    }

    // ------------------------------------------------------------------
    //  Deteccion de piezas
    // ------------------------------------------------------------------

    public static boolean esHazmat(ItemStack item) {
        if (item == null || HAZMAT_KEY == null) {
            return false;
        }
        ItemMeta meta = item.getItemMeta();
        return meta != null
                && meta.getPersistentDataContainer().has(HAZMAT_KEY, PersistentDataType.BYTE);
    }

    /** Cuantas piezas del traje lleva puestas el jugador (0 a 4). */
    public static int piezasEquipadas(Player player) {
        var inv = player.getInventory();
        int n = 0;
        if (esHazmat(inv.getHelmet())) n++;
        if (esHazmat(inv.getChestplate())) n++;
        if (esHazmat(inv.getLeggings())) n++;
        if (esHazmat(inv.getBoots())) n++;
        return n;
    }
}
