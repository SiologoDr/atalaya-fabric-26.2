package com.atalaya.item;

import com.atalaya.Atalaya;
import net.minecraft.core.Registry;
import net.minecraft.core.component.DataComponents;
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
import net.minecraft.world.item.Items;
import net.minecraft.world.item.Rarity;
import net.minecraft.world.item.ToolMaterial;
import net.minecraft.world.item.TridentItem;
import net.minecraft.world.item.component.ItemAttributeModifiers;
import net.minecraft.world.item.component.Weapon;
import net.minecraft.world.item.equipment.ArmorMaterial;
import net.minecraft.world.item.equipment.ArmorMaterials;
import net.minecraft.world.item.equipment.ArmorType;
import net.minecraft.world.item.equipment.EquipmentAsset;
import net.minecraft.world.item.equipment.EquipmentAssets;
import org.jspecify.annotations.Nullable;

import java.util.ArrayList;
import java.util.EnumMap;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * Las armaduras elementales y sus armas: la netherite mejorada con lo de cada
 * jefe, y cada elemento con su rol (las habilidades estan en
 * com.atalaya.habilidad.Habilidades). Las texturas salen de armaduras_jefes.py
 * y armaduras_iconos.py.
 *
 * <pre>
 *   mareas    Nerea, agua      sanador   netherita y 1 corazon mas    Tridente de las Mareas
 *   jade      Rajang, tierra   tanque    4/9/7/4                      Martillo de Jade
 *   vendaval  Aeralis, viento  soporte   netherita                    Arco del Vendaval
 *   solar     Novilis, fuego   DPS       netherita                    Gran Espada Solar
 * </pre>
 *
 * La dureza y el empuje son los de la netherita: la ventaja esta en el rol, no
 * en aguantar mas. Las armas pegan un poco mas que la netherita, no el doble.
 * Por ahora solo salen del inventario de creativo. Se reparan con netherite.
 *
 * Las espadas de antes (mareas_sword, jade_sword, vendaval_sword) siguen
 * registradas para que no desaparezcan de los mundos donde ya estan, pero ya
 * no salen en creativo: las sustituyen las armas de cada rol.
 */
public final class ArmadurasJefes {

    public enum Tema {
        MAREAS("mareas", 3, 8, 6, 3, 0.5),
        JADE("jade", 4, 9, 7, 4, 0.0),
        VENDAVAL("vendaval", 3, 8, 6, 3, 0.0),
        SOLAR("solar", 3, 8, 6, 3, 0.0);

        public final String id;
        public final ResourceKey<EquipmentAsset> asset;
        public final ArmorMaterial material;
        /** La vida que da cada pieza: el sanador, medio punto por pieza (un corazon con las cuatro). */
        public final double vidaPorPieza;

        Tema(String id, int casco, int pechera, int grebas, int botas, double vidaPorPieza) {
            this.id = id;
            this.asset = ResourceKey.create(EquipmentAssets.ROOT_ID, Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, id));
            this.material = material(asset, casco, pechera, grebas, botas);
            this.vidaPorPieza = vidaPorPieza;
        }
    }

    /**
     * El material de las espadas de antes: la netherite con el doble de filo
     * (16 de dano). Solo para las que ya existen.
     */
    public static final ToolMaterial ESPADA = new ToolMaterial(BlockTags.INCORRECT_FOR_NETHERITE_TOOL, 3046, 9.0F, 12.0F, 18,
            ItemTags.NETHERITE_TOOL_MATERIALS);

    /** El de las armas de rol: la netherite (su mismo filo) con mas aguante. */
    public static final ToolMaterial ARMA = new ToolMaterial(BlockTags.INCORRECT_FOR_NETHERITE_TOOL, 3046, 9.0F, 4.0F, 18,
            ItemTags.NETHERITE_TOOL_MATERIALS);

    public static final Map<Tema, Item[]> PIEZAS = new EnumMap<>(Tema.class);
    public static final Map<Tema, Item> ESPADAS = new EnumMap<>(Tema.class);
    public static final Map<Tema, Item> ARMAS = new EnumMap<>(Tema.class);
    private static final Map<Item, Tema> TEMA_DE = new HashMap<>();

    private ArmadurasJefes() {
    }

    private static ArmorMaterial material(ResourceKey<EquipmentAsset> asset, int casco, int pechera, int grebas, int botas) {
        ArmorMaterial netherite = ArmorMaterials.NETHERITE;
        Map<ArmorType, Integer> defensa = new EnumMap<>(netherite.defense());
        defensa.put(ArmorType.HELMET, casco);
        defensa.put(ArmorType.CHESTPLATE, pechera);
        defensa.put(ArmorType.LEGGINGS, grebas);
        defensa.put(ArmorType.BOOTS, botas);
        return new ArmorMaterial(
                (int) (netherite.durability() * 1.5F),
                Map.copyOf(defensa),
                18,
                SoundEvents.ARMOR_EQUIP_NETHERITE,
                netherite.toughness(),
                netherite.knockbackResistance(),
                ItemTags.REPAIRS_NETHERITE_ARMOR,
                asset);
    }

    public static void registrar() {
        for (Tema tema : Tema.values()) {
            Item[] piezas = {
                    pieza(tema, ArmorType.HELMET, "helmet"),
                    pieza(tema, ArmorType.CHESTPLATE, "chestplate"),
                    pieza(tema, ArmorType.LEGGINGS, "leggings"),
                    pieza(tema, ArmorType.BOOTS, "boots")};
            PIEZAS.put(tema, piezas);
            for (Item p : piezas) {
                TEMA_DE.put(p, tema);
            }
            if (tema != Tema.SOLAR) {
                // La espada de antes: solo las tres que ya existian.
                ResourceKey<Item> clave = clave(tema.id + "_sword");
                ESPADAS.put(tema, Registry.register(BuiltInRegistries.ITEM, clave, new EspadaJefeItem(tema,
                        new Item.Properties().setId(clave).sword(ESPADA, 3.0F, -2.4F).fireResistant().rarity(Rarity.EPIC))));
            }
        }
        // Las armas de cada rol.
        ResourceKey<Item> k = clave("mareas_trident");
        ARMAS.put(Tema.MAREAS, Registry.register(BuiltInRegistries.ITEM, k, new TridenteMareasItem(new Item.Properties().setId(k)
                .durability(1500).attributes(TridentItem.createAttributes())
                .component(DataComponents.TOOL, TridentItem.createToolProperties())
                .component(DataComponents.WEAPON, new Weapon(1)).enchantable(18).repairable(Items.NETHERITE_INGOT)
                .fireResistant().rarity(Rarity.EPIC))));
        k = clave("jade_hammer");
        // 9 de dano (1 + 4 de la netherita + 4) y lento: 0,8 golpes por segundo.
        ARMAS.put(Tema.JADE, Registry.register(BuiltInRegistries.ITEM, k, new MartilloJadeItem(new Item.Properties().setId(k)
                .sword(ARMA, 4.0F, -3.2F).fireResistant().rarity(Rarity.EPIC))));
        k = clave("vendaval_bow");
        ARMAS.put(Tema.VENDAVAL, Registry.register(BuiltInRegistries.ITEM, k, new ArcoVendavalItem(new Item.Properties().setId(k)
                .durability(1152).enchantable(18).repairable(Items.NETHERITE_INGOT).fireResistant().rarity(Rarity.EPIC))));
        k = clave("solar_greatsword");
        // 10 de dano (1 + 4 + 5) a 1,4 golpes por segundo: algo mas por segundo que la netherita.
        ARMAS.put(Tema.SOLAR, Registry.register(BuiltInRegistries.ITEM, k, new EspadaSolarItem(new Item.Properties().setId(k)
                .sword(ARMA, 5.0F, -2.6F).fireResistant().rarity(Rarity.EPIC))));
    }

    private static Item pieza(Tema tema, ArmorType tipo, String nombre) {
        ResourceKey<Item> clave = clave(tema.id + "_" + nombre);
        ItemAttributeModifiers atributos = tema.material.createAttributes(tipo);
        if (tema.vidaPorPieza > 0) {
            atributos = atributos.withModifierAdded(Attributes.MAX_HEALTH,
                    new AttributeModifier(Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "vida_extra." + nombre),
                            tema.vidaPorPieza, AttributeModifier.Operation.ADD_VALUE),
                    EquipmentSlotGroup.bySlot(tipo.getSlot()));
        }
        Item.Properties props = new Item.Properties().setId(clave)
                .humanoidArmor(tema.material, tipo)
                .attributes(atributos)
                .fireResistant()
                .rarity(Rarity.EPIC);
        return Registry.register(BuiltInRegistries.ITEM, clave, new Item(props));
    }

    private static ResourceKey<Item> clave(String nombre) {
        return ResourceKey.create(Registries.ITEM, Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, nombre));
    }

    /** De que tema es esta pieza de armadura (o nada si no es de estas). */
    public static @Nullable Tema temaDe(Item item) {
        return TEMA_DE.get(item);
    }

    /** Las dieciseis piezas, por temas (casco, pechera, pantalon y botas). */
    public static Item[] armaduras() {
        List<Item> out = new ArrayList<>();
        for (Tema tema : Tema.values()) {
            out.addAll(List.of(PIEZAS.get(tema)));
        }
        return out.toArray(new Item[0]);
    }

    /** Las cuatro armas de rol. */
    public static Item[] armas() {
        return ARMAS.values().toArray(new Item[0]);
    }

    public static Item[] espadas() {
        return ESPADAS.values().toArray(new Item[0]);
    }
}
