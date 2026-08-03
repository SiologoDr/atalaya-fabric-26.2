package com.atalaya.menu;

import com.atalaya.config.AtalayaConfig;
import com.atalaya.config.LibroRecetas;
import com.atalaya.item.AtalayaComponents;
import com.atalaya.item.AtalayaItems;
import com.atalaya.item.HazmatArmor;
import net.minecraft.ChatFormatting;
import net.minecraft.core.component.DataComponents;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.Container;
import net.minecraft.world.SimpleContainer;
import net.minecraft.world.SimpleMenuProvider;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.inventory.ChestMenu;
import net.minecraft.world.inventory.ContainerInput;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.component.ItemLore;
import net.minecraft.world.item.component.TooltipDisplay;

import java.util.LinkedHashSet;
import java.util.List;

/**
 * Menu de configuracion: un cofre de 3 filas con un icono por mecanica.
 * Click izquierdo sobre un icono = activar/desactivar.
 *
 * Lo dibuja y lo maneja el SERVIDOR, asi que no hace falta codigo de cliente.
 */
public class ConfigMenu extends ChestMenu {

    // Fila de arriba: todo lo que el MUNDO te da sin pasar por una receta.
    // El desgaste del traje NO tiene interruptor propio: solo ocurre mientras
    // hay radiacion, asi que apagar la radiacion ya lo apaga.
    //
    // Con seis drops ya no caben separados de dos en dos, asi que se apinan a
    // la derecha y las MECANICAS se quedan juntas en el extremo izquierdo. El
    // hueco del medio no es decorativo: separa las mecanicas de los drops, que
    // es la unica division que de verdad hay en esta fila.
    public static final int SLOT_RADIACION = 0;
    public static final int SLOT_HIDRATACION = 1;
    public static final int SLOT_DROP_MIEL = 3;
    public static final int SLOT_DROP_COLMILLO = 4;
    public static final int SLOT_DROP_VENENO = 5;
    public static final int SLOT_DROP_ESPEJO = 6;
    public static final int SLOT_DROP_PATA = 7;
    public static final int SLOT_DROP_ALON = 8;

    // Fila de en medio: la CADENA DE FABRICACION del traje, en el mismo orden en
    // que la recorre el jugador. Cada paso tiene su interruptor, asi que se
    // puede cortar la cadena por donde se quiera: dejar la miel pero no la
    // plantilla, o permitir los materiales pero bloquear la mesa de herreria.
    public static final int SLOT_LINGOTE = 10;
    public static final int SLOT_MIEL = 12;
    public static final int SLOT_PLANTILLA = 14;
    public static final int SLOT_CRAFTEO = 16;

    // Fila de abajo: los ITEMS y sus recetas (slots 18 a 26).
    //
    // Aqui NO van a huecos iguales como las otras dos filas: se agrupan por
    // cadena, pegadas dentro del grupo y con un hueco entre grupos. Las dos
    // cadenas de dos pasos quedan juntas (carbon -> filtro y alga -> lente) y
    // las de un paso van sueltas, asi que el reparto ya cuenta que el segundo
    // interruptor depende del primero sin tener que abrir el tooltip.
    //
    // Con SIETE ya no hay huecos para aislar los cuatro grupos: nueve ranuras
    // solo dan para dos separadores. Se gastan en apartar el agua purificada,
    // que es de otra mecanica (la sed) y no pinta nada con el traje, y en
    // dejar sola la cadena del cartucho. Los cuatro del medio se juntan.
    public static final int SLOT_CARBON = 18;
    public static final int SLOT_FILTROS = 19;
    public static final int SLOT_ALGA = 21;
    public static final int SLOT_LENTE = 22;
    public static final int SLOT_COLMILLO = 23;
    public static final int SLOT_PATA_ALADA = 24;
    public static final int SLOT_AGUA = 26;


    /** Se construye una vez: los rellenos son todos iguales. */
    private static final ItemStack RELLENO = crearRelleno();

    private final Container contenedor;

    public ConfigMenu(int id, Inventory inventarioJugador, Container contenedor) {
        super(net.minecraft.world.inventory.MenuType.GENERIC_9x3, id, inventarioJugador, contenedor, 3);
        this.contenedor = contenedor;
        refrescar();
    }

    /** Abre el menu a un jugador. */
    public static void abrir(ServerPlayer jugador) {
        Container contenedor = new SimpleContainer(27);
        jugador.openMenu(new SimpleMenuProvider(
                (id, inv, p) -> new ConfigMenu(id, inv, contenedor),
                // Sin color: el titulo de un contenedor va en el gris oscuro de
                // vanilla, como el de un cofre. Coloreado desentona.
                Component.literal("Atalaya - Configuracion")
        ));
    }

    /**
     * Vuelve a pintar el menu segun el estado actual.
     *
     * Se llama al abrir y en cada click, que son eventos raros: no hay ninguna
     * ventaja en cachear los ItemStack y si el riesgo de mostrar un estado viejo.
     */
    public void refrescar() {
        AtalayaConfig cfg = AtalayaConfig.get();

        // Fondo: cristal gris en todo lo que no sea un interruptor, para que se
        // vea como un panel y no como un cofre a medio llenar.
        for (int i = 0; i < contenedor.getContainerSize(); i++) {
            contenedor.setItem(i, RELLENO.copy());
        }

        // --- Fila de arriba: mecanicas del mundo ---
        contenedor.setItem(SLOT_RADIACION, interruptor(
                new ItemStack(Items.AMETHYST_CLUSTER),
                "Radiacion de las geodas",
                cfg.isRadiacionActiva(),
                "Dana a quien se acerca a una amatista en gemacion."
        ));

        // Arbusto muerto: dice "aqui no hay agua" mejor que un cubo lleno, y va
        // en la misma linea que la amatista de la radiacion, que tambien es la
        // causa y no el remedio.
        contenedor.setItem(SLOT_HIDRATACION, interruptor(
                new ItemStack(Items.DEAD_BUSH),
                "Hidratacion en el desierto",
                cfg.isHidratacionActiva(),
                "Gasta un punto al sol, e insola al quedarte seco."
        ));

        contenedor.setItem(SLOT_DROP_MIEL, interruptor(
                new ItemStack(Items.BEE_SPAWN_EGG),
                "Miel de las abejas",
                cfg.isDropMielActivo(),
                "Las abejas sueltan miel cristalizada al matarlas."
        ));

        contenedor.setItem(SLOT_DROP_COLMILLO, interruptor(
                new ItemStack(AtalayaItems.COLMILLO),
                "Colmillo de arana",
                cfg.isDropColmilloActivo(),
                "Las aranas comunes sueltan el colmillo seco."
        ));

        contenedor.setItem(SLOT_DROP_VENENO, interruptor(
                new ItemStack(AtalayaItems.VENENO),
                "Veneno de arana de cueva",
                cfg.isDropVenenoActivo(),
                "Solo la de cueva lo suelta: es la que envenena."
        ));

        contenedor.setItem(SLOT_DROP_ESPEJO, interruptor(
                new ItemStack(AtalayaItems.ESPEJO_MAR),
                "Espejo de mar",
                cfg.isDropEspejoActivo(),
                "Sale al pescar, en cualquier agua."
        ));

        contenedor.setItem(SLOT_DROP_PATA, interruptor(
                new ItemStack(AtalayaItems.PATA_LIGERA),
                "Pata ligera",
                cfg.isDropPataActivo(),
                "Los conejos la sueltan al matarlos."
        ));

        contenedor.setItem(SLOT_DROP_ALON, interruptor(
                new ItemStack(AtalayaItems.ALON),
                "Alon",
                cfg.isDropAlonActivo(),
                "Los pollos lo sueltan al matarlos."
        ));

        // --- Fila de en medio: la cadena de fabricacion, en orden ---
        contenedor.setItem(SLOT_LINGOTE, interruptor(
                new ItemStack(AtalayaItems.LINGOTE_BLINDADO),
                "Lingote blindado",
                cfg.isLingoteActivo(),
                "El material del traje: oro aleado con hierro."
        ));

        contenedor.setItem(SLOT_MIEL, interruptor(
                new ItemStack(AtalayaItems.MIEL_CRISTALIZADA),
                "Miel cristalizada",
                cfg.isMielActiva(),
                "La resina con la que se marcan las juntas."
        ));

        contenedor.setItem(SLOT_PLANTILLA, interruptor(
                new ItemStack(AtalayaItems.PLANTILLA_SELLADO),
                "Plantilla de sellado",
                cfg.isPlantillaActiva(),
                "Cubre fabricarla y duplicarla."
        ));

        contenedor.setItem(SLOT_CRAFTEO, interruptor(
                new ItemStack(HazmatArmor.CASCO),
                "Traje en la mesa de herreria",
                cfg.isCrafteoHazmat(),
                "Mejorar armadura de hierro para obtener el traje."
        ));

        // --- Fila de abajo: items y sus recetas ---
        contenedor.setItem(SLOT_CARBON, interruptor(
                new ItemStack(AtalayaItems.CARBON_ACTIVADO),
                "Carbon activado",
                cfg.isCarbonActivo(),
                "Fundir carbon para obtener el relleno del cartucho."
        ));

        contenedor.setItem(SLOT_FILTROS, interruptor(
                new ItemStack(AtalayaItems.FILTRO_CARBON),
                "Filtro de carbon",
                cfg.isFiltrosActivos(),
                "Montar el cartucho que recarga el traje."
        ));

        contenedor.setItem(SLOT_ALGA, interruptor(
                new ItemStack(AtalayaItems.ALGA_VITRIFICADA),
                "Alga vitrificada",
                cfg.isAlgaActiva(),
                "Fundir un bloque de alga seca hasta que vitrifica."
        ));

        contenedor.setItem(SLOT_LENTE, interruptor(
                new ItemStack(AtalayaItems.LENTE_MAR),
                "Lente de mar",
                cfg.isLenteActiva(),
                "Montar la lente y aplicarla al visor del casco."
        ));

        contenedor.setItem(SLOT_COLMILLO, interruptor(
                new ItemStack(AtalayaItems.COLMILLO_VENENOSO),
                "Colmillo venenoso",
                cfg.isColmilloActivo(),
                "Juntar colmillo con veneno y montarlo en el traje."
        ));

        contenedor.setItem(SLOT_PATA_ALADA, interruptor(
                new ItemStack(AtalayaItems.PATA_ALADA),
                "Pata alada",
                cfg.isPataAladaActiva(),
                "Juntar pata y alon, y montarlo contra la lentitud."
        ));

        contenedor.setItem(SLOT_AGUA, interruptor(
                new ItemStack(AtalayaItems.AGUA_PURIFICADA),
                "Agua purificada",
                cfg.isAguaActiva(),
                "Hervir una botella de agua, al horno o a la fogata."
        ));

        // Empuja el cambio al cliente ya, sin esperar al barrido del siguiente tick.
        broadcastChanges();
    }

    /**
     * Cristal gris sin nombre ni tooltip, para el fondo del panel.
     *
     * En 26.2 los cristales de color viven en una ColorCollection en vez de
     * tener una constante por color, de ahi el .gray().
     */
    private static ItemStack crearRelleno() {
        ItemStack relleno = new ItemStack(Items.STAINED_GLASS_PANE.gray());
        relleno.set(DataComponents.CUSTOM_NAME, Component.empty());
        // TooltipDisplay es un record (ocultarTodo, componentesOcultos).
        relleno.set(DataComponents.TOOLTIP_DISPLAY,
                new TooltipDisplay(true, new LinkedHashSet<>()));
        return relleno;
    }

    /**
     * Un icono de interruptor: nombre en verde o rojo, estado en el tooltip y
     * brillo de encantamiento cuando esta activo.
     */
    private static ItemStack interruptor(ItemStack base, String nombre, boolean activo, String descripcion) {
        // Marca de icono: las piezas del traje generan su propia descripcion al
        // mostrarse, y sin esto el icono del crafteo arrastraria al menu la
        // lista de caracteristicas mezclada con el texto del interruptor.
        base.set(AtalayaComponents.ICONO_MENU, true);

        base.set(DataComponents.CUSTOM_NAME,
                Component.literal(nombre)
                        .withStyle(activo ? ChatFormatting.GREEN : ChatFormatting.RED)
                        .withStyle(ChatFormatting.BOLD));

        base.set(DataComponents.LORE, new ItemLore(List.of(
                Component.literal(descripcion).withStyle(ChatFormatting.GRAY),
                Component.empty(),
                Component.literal("Estado: ").withStyle(ChatFormatting.GRAY)
                        .append(Component.literal(activo ? "ACTIVADO" : "DESACTIVADO")
                                .withStyle(activo ? ChatFormatting.GREEN : ChatFormatting.RED)),
                Component.literal("Click para cambiar").withStyle(ChatFormatting.YELLOW)
        )));

        base.set(DataComponents.ENCHANTMENT_GLINT_OVERRIDE, activo);
        // Sin esto se verian los atributos de armadura del casco en el tooltip.
        base.set(DataComponents.TOOLTIP_DISPLAY,
                TooltipDisplay.DEFAULT.withHidden(DataComponents.ATTRIBUTE_MODIFIERS, true));
        return base;
    }

    /**
     * Intercepta los clicks: los de la zona del cofre cambian interruptores y
     * nunca mueven items; los del inventario del jugador se dejan pasar.
     */
    @Override
    public void clicked(int slot, int boton, ContainerInput tipo, Player jugador) {
        boolean esZonaMenu = slot >= 0 && slot < contenedor.getContainerSize();
        if (!esZonaMenu) {
            super.clicked(slot, boton, tipo, jugador);
            return;
        }

        AtalayaConfig cfg = AtalayaConfig.get();
        switch (slot) {
            case SLOT_RADIACION -> {
                cfg.setRadiacionActiva(!cfg.isRadiacionActiva());
                avisar(jugador, "Radiacion", cfg.isRadiacionActiva());
            }
            // Los tres drops no tocan el libro de recetas: no son recetas.
            case SLOT_HIDRATACION -> {
                cfg.setHidratacionActiva(!cfg.isHidratacionActiva());
                avisar(jugador, "Hidratacion", cfg.isHidratacionActiva());
            }
            case SLOT_DROP_MIEL -> {
                cfg.setDropMielActivo(!cfg.isDropMielActivo());
                avisar(jugador, "Miel de las abejas", cfg.isDropMielActivo());
            }
            case SLOT_DROP_COLMILLO -> {
                cfg.setDropColmilloActivo(!cfg.isDropColmilloActivo());
                avisar(jugador, "Colmillo de arana", cfg.isDropColmilloActivo());
            }
            case SLOT_DROP_VENENO -> {
                cfg.setDropVenenoActivo(!cfg.isDropVenenoActivo());
                avisar(jugador, "Veneno de arana de cueva", cfg.isDropVenenoActivo());
            }
            case SLOT_DROP_ESPEJO -> {
                cfg.setDropEspejoActivo(!cfg.isDropEspejoActivo());
                avisar(jugador, "Espejo de mar", cfg.isDropEspejoActivo());
            }
            case SLOT_DROP_PATA -> {
                cfg.setDropPataActivo(!cfg.isDropPataActivo());
                avisar(jugador, "Pata ligera", cfg.isDropPataActivo());
            }
            case SLOT_DROP_ALON -> {
                cfg.setDropAlonActivo(!cfg.isDropAlonActivo());
                avisar(jugador, "Alon", cfg.isDropAlonActivo());
            }
            case SLOT_LINGOTE -> {
                cfg.setLingoteActivo(!cfg.isLingoteActivo());
                avisar(jugador, "Lingote blindado", cfg.isLingoteActivo());
                actualizarLibros(jugador);
            }
            case SLOT_MIEL -> {
                cfg.setMielActiva(!cfg.isMielActiva());
                avisar(jugador, "Miel cristalizada", cfg.isMielActiva());
                actualizarLibros(jugador);
            }
            case SLOT_PLANTILLA -> {
                cfg.setPlantillaActiva(!cfg.isPlantillaActiva());
                avisar(jugador, "Plantilla de sellado", cfg.isPlantillaActiva());
                actualizarLibros(jugador);
            }
            case SLOT_CRAFTEO -> {
                cfg.setCrafteoHazmat(!cfg.isCrafteoHazmat());
                avisar(jugador, "Traje en la herreria", cfg.isCrafteoHazmat());
                actualizarLibros(jugador);
            }
            case SLOT_CARBON -> {
                cfg.setCarbonActivo(!cfg.isCarbonActivo());
                avisar(jugador, "Carbon activado", cfg.isCarbonActivo());
                actualizarLibros(jugador);
            }
            case SLOT_FILTROS -> {
                cfg.setFiltrosActivos(!cfg.isFiltrosActivos());
                avisar(jugador, "Filtro de carbon", cfg.isFiltrosActivos());
                actualizarLibros(jugador);
            }
            case SLOT_COLMILLO -> {
                cfg.setColmilloActivo(!cfg.isColmilloActivo());
                avisar(jugador, "Colmillo venenoso", cfg.isColmilloActivo());
                actualizarLibros(jugador);
            }
            case SLOT_ALGA -> {
                cfg.setAlgaActiva(!cfg.isAlgaActiva());
                avisar(jugador, "Alga vitrificada", cfg.isAlgaActiva());
                actualizarLibros(jugador);
            }
            case SLOT_LENTE -> {
                cfg.setLenteActiva(!cfg.isLenteActiva());
                avisar(jugador, "Lente de mar", cfg.isLenteActiva());
                actualizarLibros(jugador);
            }
            case SLOT_PATA_ALADA -> {
                cfg.setPataAladaActiva(!cfg.isPataAladaActiva());
                avisar(jugador, "Pata alada", cfg.isPataAladaActiva());
                actualizarLibros(jugador);
            }
            case SLOT_AGUA -> {
                cfg.setAguaActiva(!cfg.isAguaActiva());
                avisar(jugador, "Agua purificada", cfg.isAguaActiva());
                actualizarLibros(jugador);
            }
            default -> {
                return; // click en el fondo: no hace nada
            }
        }
        refrescar();
        // Cualquier otro click dentro del menu se ignora: los iconos no se sacan.
    }

    /**
     * Rehace el libro de recetas de TODOS los conectados, no solo del que pulsa:
     * el interruptor es del servidor, asi que el cambio les afecta a todos.
     */
    private static void actualizarLibros(Player quienPulsa) {
        if (quienPulsa instanceof ServerPlayer sp && sp.level().getServer() != null) {
            LibroRecetas.sincronizarTodos(sp.level().getServer());
        }
    }

    private static void avisar(Player jugador, String que, boolean activo) {
        jugador.sendSystemMessage(
                Component.literal(que + ": ").withStyle(ChatFormatting.GRAY)
                        .append(Component.literal(activo ? "ACTIVADO" : "DESACTIVADO")
                                .withStyle(activo ? ChatFormatting.GREEN : ChatFormatting.RED)));
    }

    /** El menu no tiene "quick move": evita que shift-click saque los iconos. */
    @Override
    public ItemStack quickMoveStack(Player jugador, int slot) {
        return ItemStack.EMPTY;
    }
}
