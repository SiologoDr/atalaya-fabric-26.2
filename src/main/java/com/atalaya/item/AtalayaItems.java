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

    /** Cartucho filtrante. Cambia el filtro del traje con click derecho. */
    public static Item FILTRO_CARBON;

    /**
     * Colmillo venenoso: lo sueltan las aranas de cueva, raramente.
     *
     * Se monta en una pieza del traje en la mesa de herreria para que filtre
     * toxinas. Tiene sentido quimico: los antivenenos se fabrican A PARTIR del
     * propio veneno, asi que el traje neutraliza la toxina usando la toxina.
     */
    public static Item COLMILLO_VENENOSO;

    /**
     * Cristal pulido: vidrio trabajado con pedernal hasta dejarlo transparente.
     *
     * Sustituye el visor ahumado del casco por uno claro, en la mesa de
     * herreria. El nombre y la receta dicen lo mismo: el pedernal es el
     * abrasivo con el que se pule.
     */
    public static Item CRISTAL_PULIDO;

    /**
     * Pata ligera: pata de conejo montada entre plumas y resina de slime.
     *
     * Se monta en una pieza del traje en la mesa de herreria y recorta la
     * lentitud que impone la radiacion. Los tres ingredientes son los tres
     * papeles de una junta amortiguada: el tendon que hace de muelle, la pluma
     * que quita peso y la resina que absorbe el tiron.
     */
    public static Item PATA_LIGERA;

    private AtalayaItems() {
    }

    public static void registrar() {
        CARBON_ACTIVADO = registrar("carbon_activado", Item::new);
        FILTRO_CARBON = registrar("filtro_carbon", FiltroCarbonItem::new);
        COLMILLO_VENENOSO = registrar("colmillo_venenoso", Item::new);
        CRISTAL_PULIDO = registrar("cristal_pulido", Item::new);
        PATA_LIGERA = registrar("pata_ligera", Item::new);
    }

    private static Item registrar(String nombre, Function<Item.Properties, Item> constructor) {
        ResourceKey<Item> clave = ResourceKey.create(
                Registries.ITEM,
                Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, nombre));
        return Registry.register(BuiltInRegistries.ITEM, clave,
                constructor.apply(new Item.Properties().setId(clave)));
    }

    public static Item[] todos() {
        return new Item[]{CARBON_ACTIVADO, FILTRO_CARBON, COLMILLO_VENENOSO, CRISTAL_PULIDO, PATA_LIGERA};
    }
}
