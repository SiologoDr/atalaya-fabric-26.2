package com.atalaya.item;

import com.atalaya.Atalaya;
import net.minecraft.ChatFormatting;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.SmithingTemplateItem;

import java.util.List;
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

    /** Colmillo seco: lo suelta la arana comun. Por si solo no hace nada. */
    public static Item COLMILLO;

    /** Veneno: lo suelta la arana de cueva, la que si envenena al morder. */
    public static Item VENENO;

    /**
     * Colmillo venenoso: el colmillo de una arana comun impregnado con el veneno
     * de una de cueva.
     *
     * Hacen falta las dos aranas, que es lo que le da sentido: la comun tiene el
     * colmillo pero no envenena, y la de cueva tiene la toxina. Ninguna de las
     * dos por separado sirve.
     *
     * Se monta en una pieza del traje en la mesa de herreria para que filtre
     * toxinas. Tiene sentido quimico: los antivenenos se fabrican A PARTIR del
     * propio veneno, asi que el traje neutraliza la toxina usando la toxina.
     */
    public static Item COLMILLO_VENENOSO;

    /**
     * Espejo de mar: lo saca el jugador pescando.
     *
     * Es lo unico del mod que ni se fabrica ni lo suelta un mob al morir: hay
     * que ir a buscarlo al agua. Ya viene con la superficie lisa; lo que le
     * falta es aguante, y eso lo pone la alga vitrificada.
     */
    public static Item ESPEJO_MAR;

    /**
     * Alga vitrificada: un bloque de alga seca llevado al horno hasta que
     * vitrifica, que es lo que le pasa de verdad a la silice del alga cuando se
     * calienta lo suficiente.
     *
     * Parte del BLOQUE y no del alga suelta por dos razones. La primera es
     * tecnica: vanilla ya funde el alga suelta para secarla, y dos recetas de
     * horno con la misma entrada se pisan, asi que solo una de las dos seria
     * alcanzable. La segunda es de coste: nueve algas secas por unidad es lo
     * que hace que valga algo al lado de un espejo que sale pescando.
     */
    public static Item ALGA_VITRIFICADA;

    /**
     * Lente de mar: el espejo templado con la alga vitrificada en la mesa de
     * herreria.
     *
     * Sustituye el visor ahumado del casco por uno claro. Ninguna de las dos
     * mitades sirve sola, igual que pasa con el colmillo venenoso: el espejo
     * pone la superficie y el alga la dureza para aguantar montada en un casco.
     */
    public static Item LENTE_MAR;

    /**
     * Pata ligera: pata de conejo montada entre plumas y resina de slime.
     *
     * Se monta en una pieza del traje en la mesa de herreria y recorta la
     * lentitud que impone la radiacion. Los tres ingredientes son los tres
     * papeles de una junta amortiguada: el tendon que hace de muelle, la pluma
     * que quita peso y la resina que absorbe el tiron.
     */
    public static Item PATA_LIGERA;

    /**
     * Lingote blindado: oro aleado con hierro. Lo que convierte una armadura de
     * hierro corriente en una pieza del traje.
     *
     * Cuesta 5 de oro y 4 de hierro, y hace falta UNO por pieza: es caro a
     * proposito porque cada uno mejora una pieza entera. La receta imita al
     * propio lingote, con el oro arriba y el hierro debajo.
     *
     * La mejora se hace en la mesa de herreria, como las demas del traje. Eso
     * trae de regalo que los encantamientos de la armadura de hierro se
     * conservan al pasar a hazmat, igual que ocurre al subir a netherita.
     */
    public static Item LINGOTE_BLINDADO;

    /**
     * Miel cristalizada: panal horneado hasta que la cera se vuelve resina dura.
     *
     * Sale del horno, que es justo lo que le pasa a la cera al calentarla: deja
     * de ser blanda y queda un ambar que sella. Es el material con el que se
     * marcan las juntas del traje.
     */
    public static Item MIEL_CRISTALIZADA;

    /**
     * Plantilla de sellado: la plantilla de herreria del traje.
     *
     * Lo dificil de un traje anti-radiacion no es el metal, son las juntas. El
     * lingote blindado para la radiacion y la plantilla para todo lo demas; sin
     * ella, el traje seria una armadura pesada con agujeros.
     *
     * Va sobre papel con respaldo de cuero, porque entra en la forja una y otra
     * vez y el papel solo no aguantaria.
     *
     * Al ser un SmithingTemplateItem, la mesa de herreria dibuja las siluetas de
     * lo que va en cada hueco y el tooltip explica a que se aplica. Eso resuelve
     * un problema que el mod tenia: las recetas de herreria no salen en el libro
     * de recetas, asi que nada le decia al jugador donde usar el lingote.
     */
    public static Item PLANTILLA_SELLADO;

    private AtalayaItems() {
    }

    // ------------------------------------------------------------------
    //  Textos del patron en la mesa de herreria
    // ------------------------------------------------------------------

    /**
     * Las etiquetas ("Se aplica a:", "Ingredientes:") las pone vanilla y vienen
     * ya traducidas a todos los idiomas. Aqui solo van los valores.
     *
     * Los colores imitan a las plantillas de vanilla: azul en la ficha de
     * arriba, gris en la explicacion de cada hueco.
     */
    private static Component azul(String clave) {
        return Component.translatable(clave).withStyle(ChatFormatting.BLUE);
    }

    private static Component gris(String clave) {
        return Component.translatable(clave).withStyle(ChatFormatting.GRAY);
    }

    /** Siluetas de los huecos vacios. Son sprites de vanilla: no hay que dibujar nada. */
    private static Identifier sprite(String nombre) {
        return Identifier.withDefaultNamespace("container/slot/" + nombre);
    }

    public static void registrar() {
        CARBON_ACTIVADO = registrar("carbon_activado", Item::new);
        FILTRO_CARBON = registrar("filtro_carbon", FiltroCarbonItem::new);
        COLMILLO = registrar("colmillo", Item::new);
        VENENO = registrar("veneno", Item::new);
        COLMILLO_VENENOSO = registrar("colmillo_venenoso", Item::new);
        ESPEJO_MAR = registrar("espejo_mar", Item::new);
        ALGA_VITRIFICADA = registrar("alga_vitrificada", Item::new);
        LENTE_MAR = registrar("lente_mar", Item::new);
        PATA_LIGERA = registrar("pata_ligera", Item::new);
        LINGOTE_BLINDADO = registrar("lingote_blindado", Item::new);
        MIEL_CRISTALIZADA = registrar("miel_cristalizada", Item::new);

        PLANTILLA_SELLADO = registrar("plantilla_sellado", props -> new SmithingTemplateItem(
                azul("item.atalaya.plantilla_sellado.aplica_a"),
                azul("item.atalaya.plantilla_sellado.ingredientes"),
                gris("item.atalaya.plantilla_sellado.hueco_base"),
                gris("item.atalaya.plantilla_sellado.hueco_adicion"),
                // Hueco de la izquierda: cualquier pieza de armadura de hierro.
                List.of(sprite("helmet"), sprite("chestplate"), sprite("leggings"), sprite("boots")),
                // Hueco de la derecha: el lingote.
                List.of(sprite("ingot")),
                props));
    }

    private static Item registrar(String nombre, Function<Item.Properties, Item> constructor) {
        ResourceKey<Item> clave = ResourceKey.create(
                Registries.ITEM,
                Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, nombre));
        return Registry.register(BuiltInRegistries.ITEM, clave,
                constructor.apply(new Item.Properties().setId(clave)));
    }

    public static Item[] todos() {
        return new Item[]{
                CARBON_ACTIVADO, FILTRO_CARBON,
                COLMILLO, VENENO, COLMILLO_VENENOSO,
                ESPEJO_MAR, ALGA_VITRIFICADA, LENTE_MAR,
                PATA_LIGERA, LINGOTE_BLINDADO,
                MIEL_CRISTALIZADA, PLANTILLA_SELLADO
        };
    }
}
