package com.atalaya.item;

import com.atalaya.Atalaya;
import net.minecraft.core.Registry;
import net.minecraft.core.component.DataComponents;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.component.ItemLore;

import java.util.List;
import net.minecraft.world.item.equipment.ArmorMaterial;
import net.minecraft.world.item.equipment.ArmorMaterials;
import net.minecraft.world.item.equipment.ArmorType;
import net.minecraft.world.item.equipment.EquipmentAsset;
import net.minecraft.world.item.equipment.EquipmentAssets;
import net.minecraft.world.item.equipment.Equippable;

/**
 * Traje anti-radiacion (Hazmat): las cuatro piezas de armadura.
 *
 * Aspecto: el aspecto del traje puesto lo define
 * assets/atalaya/equipment/hazmat.json (dos capas: humanoid y humanoid_leggings).
 * El icono de cada pieza sale de assets/atalaya/items/hazmat_*.json.
 *
 * Solo el casco lleva visor: el cliente dibuja hazmat_visor.png a pantalla
 * completa mientras esta puesto, igual que hace la calabaza tallada.
 */
public final class HazmatArmor {

    /** Enlaza con assets/atalaya/equipment/hazmat.json. */
    public static final ResourceKey<EquipmentAsset> ASSET =
            ResourceKey.create(EquipmentAssets.ROOT_ID, id("hazmat"));

    /** textures/misc/hazmat_visor.png */
    private static final Identifier VISOR = id("misc/hazmat_visor");

    public static final ArmorMaterial MATERIAL = materialComoElHierro();

    // Tonos claros, para que se lean sobre el fondo oscuro del tooltip.
    private static final int AMARILLO = 0xFCFC54;
    private static final int VERDE_RAD = 0x8CE05A;
    private static final int LILA_GEODA = 0xE4A8FF;

    /**
     * Descripcion que sale en el tooltip. Vanilla pinta el lore en morado y en
     * cursiva por defecto, asi que cada linea fija su color y desactiva la
     * cursiva explicitamente.
     */
    private static final ItemLore LORE = new ItemLore(List.of(
            Component.empty(),
            tituloCaracteristicas(),
            Component.empty(),
            lineaRadiacion()
    ));

    /**
     * "☢ Caracteristicas" con el subrayado SOLO en la palabra: el icono va en un
     * trozo aparte sin subrayar, porque una linea bajo el simbolo queda sucia.
     */
    private static Component tituloCaracteristicas() {
        return Component.literal("☢ ")
                .withStyle(s -> s.withColor(AMARILLO).withItalic(false))
                .append(Component.translatable("item.atalaya.hazmat.lore.titulo")
                        .withStyle(s -> s.withColor(AMARILLO).withUnderlined(true).withItalic(false)));
    }

    /**
     * "• Resiste un 25% la radiacion de la Geoda", con "Geoda" en lila.
     *
     * La palabra va como ARGUMENTO de la traduccion (%s) en vez de partir la
     * frase en dos claves: asi cada idioma decide donde colocarla y no damos por
     * hecho el orden de las palabras del espanol.
     */
    private static Component lineaRadiacion() {
        Component geoda = Component.translatable("item.atalaya.hazmat.lore.geoda")
                .withStyle(s -> s.withColor(LILA_GEODA).withItalic(false));

        return Component.translatable("item.atalaya.hazmat.lore.radiacion", geoda)
                .withStyle(s -> s.withColor(VERDE_RAD).withItalic(false));
    }

    public static Item CASCO;
    public static Item PECHERA;
    public static Item PANTALON;
    public static Item BOTAS;

    private HazmatArmor() {
    }

    private static Identifier id(String ruta) {
        return Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, ruta);
    }

    /**
     * Mismo material que el hierro (durabilidad 165/240/225/195, proteccion
     * 2/6/5/2, reparable con lingotes...) pero con NUESTRO aspecto.
     *
     * Los valores se leen del material vanilla en vez de copiarlos a mano: si
     * Mojang los cambia en una actualizacion, el traje los sigue solo.
     */
    private static ArmorMaterial materialComoElHierro() {
        ArmorMaterial hierro = ArmorMaterials.IRON;
        return new ArmorMaterial(
                hierro.durability(),
                hierro.defense(),
                hierro.enchantmentValue(),
                hierro.equipSound(),
                hierro.toughness(),
                hierro.knockbackResistance(),
                hierro.repairIngredient(),
                ASSET
        );
    }

    public static void registrar() {
        CASCO = pieza("hazmat_helmet", ArmorType.HELMET, true);
        PECHERA = pieza("hazmat_chestplate", ArmorType.CHESTPLATE, false);
        PANTALON = pieza("hazmat_leggings", ArmorType.LEGGINGS, false);
        BOTAS = pieza("hazmat_boots", ArmorType.BOOTS, false);
    }

    private static Item pieza(String nombre, ArmorType tipo, boolean conVisor) {
        ResourceKey<Item> clave = ResourceKey.create(Registries.ITEM, id(nombre));

        Item.Properties props = new Item.Properties()
                .setId(clave)
                .humanoidArmor(MATERIAL, tipo)
                .component(DataComponents.LORE, LORE);

        if (conVisor) {
            // humanoidArmor() ya deja puesto un componente equippable; lo
            // reemplazamos por uno igual pero con la textura del visor.
            props.component(DataComponents.EQUIPPABLE,
                    Equippable.builder(tipo.getSlot())
                            .setAsset(ASSET)
                            .setEquipSound(MATERIAL.equipSound())
                            .setCameraOverlay(VISOR)
                            .setDamageOnHurt(true)
                            .build());
        }

        return Registry.register(BuiltInRegistries.ITEM, clave, new Item(props));
    }

    /** Las cuatro piezas, en orden de cabeza a pies. */
    public static Item[] todas() {
        return new Item[]{CASCO, PECHERA, PANTALON, BOTAS};
    }

    /**
     * true si el item es una pieza del traje.
     *
     * Comparacion por referencia: los Item son singletons del registro, asi que
     * son cuatro comparaciones de puntero. Se usa desde el mixin del crafteo,
     * donde conviene no tocar el registro.
     */
    public static boolean esPieza(Item item) {
        return item == CASCO || item == PECHERA || item == PANTALON || item == BOTAS;
    }

    /**
     * Cuantas piezas del traje lleva puestas la entidad (0 a 4).
     *
     * Se cuenta por SLOT, no por inventario: llevar cuatro cascos en la mochila
     * no protege de nada.
     */
    public static int piezasEquipadas(LivingEntity entidad) {
        int n = 0;
        for (EquipmentSlot slot : RANURAS_ARMADURA) {
            if (esPieza(entidad.getItemBySlot(slot).getItem())) {
                n++;
            }
        }
        return n;
    }

    private static final EquipmentSlot[] RANURAS_ARMADURA = {
            EquipmentSlot.HEAD, EquipmentSlot.CHEST, EquipmentSlot.LEGS, EquipmentSlot.FEET
    };
}
