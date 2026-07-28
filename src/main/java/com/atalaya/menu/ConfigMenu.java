package com.atalaya.menu;

import com.atalaya.config.AtalayaConfig;
import com.atalaya.config.LibroRecetas;
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

    /** Slot de cada interruptor dentro del cofre (fila de en medio). */
    public static final int SLOT_RADIACION = 10;
    public static final int SLOT_CRAFTEO = 13;
    public static final int SLOT_FILTROS = 16;

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
                Component.literal("Atalaya - Configuracion").withStyle(ChatFormatting.DARK_AQUA)
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
            if (i != SLOT_CRAFTEO && i != SLOT_RADIACION && i != SLOT_FILTROS) {
                contenedor.setItem(i, RELLENO.copy());
            }
        }

        contenedor.setItem(SLOT_RADIACION, interruptor(
                new ItemStack(Items.AMETHYST_CLUSTER),
                "Radiacion de las geodas",
                cfg.isRadiacionActiva(),
                "Dana a quien se acerca a una amatista en gemacion."
        ));

        contenedor.setItem(SLOT_CRAFTEO, interruptor(
                new ItemStack(HazmatArmor.CASCO),
                "Crafteo del traje Hazmat",
                cfg.isCrafteoHazmat(),
                "Permite fabricar el traje y verlo en el libro de recetas."
        ));

        contenedor.setItem(SLOT_FILTROS, interruptor(
                new ItemStack(AtalayaItems.FILTRO_CARBON),
                "Filtros de carbon",
                cfg.isFiltrosActivos(),
                "Cubre fundir carbon activado y fabricar el filtro."
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
        if (slot == SLOT_CRAFTEO) {
            boolean nuevo = !cfg.isCrafteoHazmat();
            cfg.setCrafteoHazmat(nuevo);
            avisar(jugador, "Crafteo Hazmat", nuevo);
            actualizarLibros(jugador);
            refrescar();
        } else if (slot == SLOT_RADIACION) {
            boolean nuevo = !cfg.isRadiacionActiva();
            cfg.setRadiacionActiva(nuevo);
            avisar(jugador, "Radiacion", nuevo);
            refrescar();
        } else if (slot == SLOT_FILTROS) {
            boolean nuevo = !cfg.isFiltrosActivos();
            cfg.setFiltrosActivos(nuevo);
            avisar(jugador, "Filtros de carbon", nuevo);
            actualizarLibros(jugador);
            refrescar();
        }
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
