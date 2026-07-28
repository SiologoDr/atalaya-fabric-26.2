package com.atalaya.item;

import com.atalaya.Atalaya;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.item.Item;

import java.util.function.Function;

/**
 * Items del mod que no son armadura.
 *
 * La cadena es corta a proposito: carbon -> carbon activado (fundiendolo) ->
 * filtro de carbon (con carcasa de hierro). El filtro es lo unico que repara el
 * traje Hazmat, asi que mantenerlo es un gasto continuo y no una compra unica.
 */
public final class AtalayaItems {

    /**
     * Carbon activado: se fabrica CALENTANDO carbon, que es como se hace de
     * verdad. La receta es el proceso real, asi no hay que memorizar nada raro.
     */
    public static Item CARBON_ACTIVADO;

    /** Cartucho filtrante. Repara el traje Hazmat en el yunque. */
    public static Item FILTRO_CARBON;

    private AtalayaItems() {
    }

    public static void registrar() {
        CARBON_ACTIVADO = registrar("carbon_activado", Item::new);
        FILTRO_CARBON = registrar("filtro_carbon", FiltroCarbonItem::new);
    }

    private static Item registrar(String nombre, Function<Item.Properties, Item> constructor) {
        ResourceKey<Item> clave = ResourceKey.create(
                Registries.ITEM,
                Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, nombre));
        return Registry.register(BuiltInRegistries.ITEM, clave,
                constructor.apply(new Item.Properties().setId(clave)));
    }

    public static Item[] todos() {
        return new Item[]{CARBON_ACTIVADO, FILTRO_CARBON};
    }
}
