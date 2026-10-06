package com.atalaya.item;

import com.atalaya.Atalaya;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.ResourceKey;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.tags.BlockTags;
import net.minecraft.tags.ItemTags;
import net.minecraft.world.entity.EquipmentSlotGroup;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.Rarity;
import net.minecraft.world.item.ToolMaterial;
import net.minecraft.world.item.equipment.ArmorMaterial;
import net.minecraft.world.item.equipment.ArmorMaterials;
import net.minecraft.world.item.equipment.ArmorType;
import net.minecraft.world.item.equipment.EquipmentAsset;
import net.minecraft.world.item.equipment.EquipmentAssets;

import java.util.ArrayList;
import java.util.EnumMap;
import java.util.List;
import java.util.Map;

/**
 * Las armaduras y las espadas de los tres jefes (octubre de 2026): la netherite
 * mejorada con lo de cada uno. Las texturas salen de armaduras_jefes.py.
 *
 * <pre>
 *   mareas    Nerea, agua     metal abisal, prismarina, nacar y coral
 *   jade      Rajang, tierra  metal verde, jade y oro
 *   vendaval  Aeralis, viento metal anil, celeste, violeta y plumas
 * </pre>
 *
 * Protegen como el doble que la netherite: 24 puntos de armadura (4/9/7/4,
 * la netherite 20), el doble de dureza (6 por pieza) y un poco mas contra el
 * empuje; y cada pieza da medio corazon mas (la armadura entera, dos). Contra
 * un golpe de 60 de un jefe, la netherite para un 32 % y estas un 66 %.
 *
 * Por ahora no se fabrican: solo salen del inventario de creativo. Se reparan
 * con netherite, como la de netherite.
 */
public final class ArmadurasJefes {

    public enum Tema {
        MAREAS("mareas"), JADE("jade"), VENDAVAL("vendaval");

        public final String id;
        public final ResourceKey<EquipmentAsset> asset;
        public final ArmorMaterial material;

        Tema(String id) {
            this.id = id;
            this.asset = ResourceKey.create(EquipmentAssets.ROOT_ID, Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, id));
            this.material = material(asset);
        }
    }

    /** Medio corazon por pieza: la armadura entera, dos corazones. */
    private static final double VIDA_POR_PIEZA = 1.0;

    /**
     * El material de las espadas: el de la netherite con mas aguante y el doble
     * de filo. Una espada hace 16 de dano (la de netherite, 8: el doble) y
     * aguanta 3046 usos.
     */
    public static final ToolMaterial ESPADA = new ToolMaterial(BlockTags.INCORRECT_FOR_NETHERITE_TOOL, 3046, 9.0F, 12.0F, 18,
            ItemTags.NETHERITE_TOOL_MATERIALS);

    public static final Map<Tema, Item[]> PIEZAS = new EnumMap<>(Tema.class);
    public static final Map<Tema, Item> ESPADAS = new EnumMap<>(Tema.class);

    private ArmadurasJefes() {
    }

    private static ArmorMaterial material(ResourceKey<EquipmentAsset> asset) {
        ArmorMaterial netherite = ArmorMaterials.NETHERITE;
        Map<ArmorType, Integer> defensa = new EnumMap<>(netherite.defense());
        defensa.put(ArmorType.HELMET, 4);
        defensa.put(ArmorType.CHESTPLATE, 9);
        defensa.put(ArmorType.LEGGINGS, 7);
        defensa.put(ArmorType.BOOTS, 4);
        return new ArmorMaterial(
                (int) (netherite.durability() * 1.5F),
                Map.copyOf(defensa),
                18,
                SoundEvents.ARMOR_EQUIP_NETHERITE,
                6.0F,
                0.15F,
                ItemTags.REPAIRS_NETHERITE_ARMOR,
                asset);
    }

    public static void registrar() {
        for (Tema tema : Tema.values()) {
            PIEZAS.put(tema, new Item[]{
                    pieza(tema, ArmorType.HELMET, "helmet"),
                    pieza(tema, ArmorType.CHESTPLATE, "chestplate"),
                    pieza(tema, ArmorType.LEGGINGS, "leggings"),
                    pieza(tema, ArmorType.BOOTS, "boots")});
            ResourceKey<Item> clave = clave(tema.id + "_sword");
            ESPADAS.put(tema, Registry.register(BuiltInRegistries.ITEM, clave, new EspadaJefeItem(tema,
                    new Item.Properties().setId(clave).sword(ESPADA, 3.0F, -2.4F).fireResistant().rarity(Rarity.EPIC))));
        }
    }

    private static Item pieza(Tema tema, ArmorType tipo, String nombre) {
        ResourceKey<Item> clave = clave(tema.id + "_" + nombre);
        // Lo de la netherite mejorada (armadura, dureza y empuje) mas el medio corazon.
        Item.Properties props = new Item.Properties().setId(clave)
                .humanoidArmor(tema.material, tipo)
                .attributes(tema.material.createAttributes(tipo).withModifierAdded(Attributes.MAX_HEALTH,
                        new AttributeModifier(Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "vida_extra." + nombre),
                                VIDA_POR_PIEZA, AttributeModifier.Operation.ADD_VALUE),
                        EquipmentSlotGroup.bySlot(tipo.getSlot())))
                .fireResistant()
                .rarity(Rarity.EPIC);
        return Registry.register(BuiltInRegistries.ITEM, clave, new Item(props));
    }

    private static ResourceKey<Item> clave(String nombre) {
        return ResourceKey.create(Registries.ITEM, Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, nombre));
    }

    /** Las doce piezas, por temas (casco, pechera, pantalon y botas). */
    public static Item[] armaduras() {
        List<Item> out = new ArrayList<>();
        for (Tema tema : Tema.values()) {
            out.addAll(List.of(PIEZAS.get(tema)));
        }
        return out.toArray(new Item[0]);
    }

    public static Item[] espadas() {
        return ESPADAS.values().toArray(new Item[0]);
    }
}
