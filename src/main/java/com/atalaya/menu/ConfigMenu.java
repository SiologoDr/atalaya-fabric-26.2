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

import java.util.ArrayList;
import java.util.List;
import java.util.function.BooleanSupplier;
import java.util.function.Consumer;
import java.util.function.Supplier;

/**
 * Panel de configuracion: un interruptor por mecanica, con paginas.
 *
 * Lo dibuja y lo maneja el SERVIDOR, asi que no hace falta codigo de cliente.
 *
 * NADA se coloca a mano. Antes cada interruptor tenia su constante de ranura y
 * anadir uno obligaba a recolocar los demas; ahora se declaran como datos en
 * {@link #GRUPOS} y la posicion se calcula. Anadir una mecanica es escribir una
 * linea al final de su grupo, y si ya no cabe se abre una pagina sola.
 */
public class ConfigMenu extends ChestMenu {

    private static final int ANCHO = 9;
    private static final int FILAS = 6;

    /** La ultima fila es la navegacion; el resto es contenido. */
    private static final int FILAS_CONTENIDO = FILAS - 1;
    private static final int TAMANO = FILAS * ANCHO;
    private static final int INICIO_NAVEGACION = FILAS_CONTENIDO * ANCHO;

    private static final int SLOT_ANTERIOR = INICIO_NAVEGACION;
    private static final int SLOT_PAGINA = INICIO_NAVEGACION + 4;
    private static final int SLOT_SIGUIENTE = INICIO_NAVEGACION + 8;

    // ------------------------------------------------------------------
    //  Los interruptores, como datos
    // ------------------------------------------------------------------

    /**
     * Un interruptor del panel.
     *
     * El icono es un proveedor y no un ItemStack porque los items del mod no
     * existen todavia cuando se carga esta clase: se piden al dibujar.
     *
     * @param tocaRecetas si al cambiarlo hay que rehacer el libro de recetas.
     *                    Los drops no son recetas, asi que no lo tocan.
     */
    private record Interruptor(Supplier<ItemStack> icono,
                               String nombre,
                               String descripcion,
                               BooleanSupplier estado,
                               Consumer<Boolean> poner,
                               boolean tocaRecetas) {
    }

    private static Interruptor mecanica(Supplier<ItemStack> icono, String nombre, String desc,
                                        BooleanSupplier estado, Consumer<Boolean> poner) {
        return new Interruptor(icono, nombre, desc, estado, poner, false);
    }

    private static Interruptor receta(Supplier<ItemStack> icono, String nombre, String desc,
                                      BooleanSupplier estado, Consumer<Boolean> poner) {
        return new Interruptor(icono, nombre, desc, estado, poner, true);
    }

    private static Supplier<ItemStack> pila(Supplier<net.minecraft.world.item.Item> item) {
        return () -> new ItemStack(item.get());
    }

    /**
     * Los grupos, en el orden en que se pintan. Cada uno empieza SIEMPRE en una
     * fila nueva, asi que la separacion visual sale sola sin rellenos.
     *
     * Un grupo de mas de nueve parte a la fila siguiente por su cuenta.
     */
    private static final List<List<Interruptor>> GRUPOS = List.of(
            // --- Lo que hace el mundo ---
            List.of(
                    mecanica(pila(() -> Items.AMETHYST_CLUSTER), "Radiacion de las geodas",
                            "Dana a quien se acerca a una amatista en gemacion.",
                            () -> AtalayaConfig.get().isRadiacionActiva(),
                            v -> AtalayaConfig.get().setRadiacionActiva(v)),
                    mecanica(pila(() -> Items.DEAD_BUSH), "Hidratacion en el desierto",
                            "Gasta un punto al sol, e insola al quedarte seco.",
                            () -> AtalayaConfig.get().isHidratacionActiva(),
                            v -> AtalayaConfig.get().setHidratacionActiva(v)),
                    mecanica(() -> new ItemStack(Items.COPPER_BLOCK.weathering().oxidized()),
                            "Lluvia corrosiva",
                            "Funde cualquier armadura en 15 s a la intemperie.",
                            () -> AtalayaConfig.get().isCorrosionActiva(),
                            v -> AtalayaConfig.get().setCorrosionActiva(v)),
                    mecanica(pila(() -> Items.WATER_BUCKET), "Empapado por la lluvia",
                            "A la intemperie te deja a la mitad de velocidad.",
                            () -> AtalayaConfig.get().isEmpapadoActivo(),
                            v -> AtalayaConfig.get().setEmpapadoActivo(v))
            ),
            // --- Lo que sueltan los mobs ---
            List.of(
                    mecanica(pila(() -> Items.BEE_SPAWN_EGG), "Miel de las abejas",
                            "Las abejas sueltan miel cristalizada al matarlas.",
                            () -> AtalayaConfig.get().isDropMielActivo(),
                            v -> AtalayaConfig.get().setDropMielActivo(v)),
                    mecanica(pila(() -> AtalayaItems.COLMILLO), "Colmillo de arana",
                            "Las aranas comunes sueltan el colmillo seco.",
                            () -> AtalayaConfig.get().isDropColmilloActivo(),
                            v -> AtalayaConfig.get().setDropColmilloActivo(v)),
                    mecanica(pila(() -> AtalayaItems.VENENO), "Veneno de arana de cueva",
                            "Solo la de cueva lo suelta: es la que envenena.",
                            () -> AtalayaConfig.get().isDropVenenoActivo(),
                            v -> AtalayaConfig.get().setDropVenenoActivo(v)),
                    mecanica(pila(() -> AtalayaItems.ESPEJO_MAR), "Espejo de mar",
                            "Sale al pescar, en cualquier agua.",
                            () -> AtalayaConfig.get().isDropEspejoActivo(),
                            v -> AtalayaConfig.get().setDropEspejoActivo(v)),
                    mecanica(pila(() -> AtalayaItems.PATA_LIGERA), "Pata ligera",
                            "Los conejos la sueltan al matarlos.",
                            () -> AtalayaConfig.get().isDropPataActivo(),
                            v -> AtalayaConfig.get().setDropPataActivo(v)),
                    mecanica(pila(() -> AtalayaItems.ALON), "Alon",
                            "Los pollos lo sueltan al matarlos.",
                            () -> AtalayaConfig.get().isDropAlonActivo(),
                            v -> AtalayaConfig.get().setDropAlonActivo(v))
            ),
            // --- La cadena del traje, en el orden en que la recorre el jugador ---
            List.of(
                    receta(pila(() -> AtalayaItems.LINGOTE_BLINDADO), "Lingote blindado",
                            "El material del traje: oro aleado con hierro.",
                            () -> AtalayaConfig.get().isLingoteActivo(),
                            v -> AtalayaConfig.get().setLingoteActivo(v)),
                    receta(pila(() -> AtalayaItems.MIEL_CRISTALIZADA), "Miel cristalizada",
                            "La resina con la que se marcan las juntas.",
                            () -> AtalayaConfig.get().isMielActiva(),
                            v -> AtalayaConfig.get().setMielActiva(v)),
                    receta(pila(() -> AtalayaItems.PLANTILLA_SELLADO), "Plantilla de sellado",
                            "Cubre fabricarla y duplicarla.",
                            () -> AtalayaConfig.get().isPlantillaActiva(),
                            v -> AtalayaConfig.get().setPlantillaActiva(v)),
                    receta(() -> new ItemStack(HazmatArmor.CASCO), "Traje en la mesa de herreria",
                            "Mejorar armadura de hierro para obtener el traje.",
                            () -> AtalayaConfig.get().isCrafteoHazmat(),
                            v -> AtalayaConfig.get().setCrafteoHazmat(v))
            ),
            // --- Items y mejoras ---
            List.of(
                    receta(pila(() -> AtalayaItems.CARBON_ACTIVADO), "Carbon activado",
                            "Fundir carbon para obtener el relleno del cartucho.",
                            () -> AtalayaConfig.get().isCarbonActivo(),
                            v -> AtalayaConfig.get().setCarbonActivo(v)),
                    receta(pila(() -> AtalayaItems.FILTRO_CARBON), "Filtro de carbon",
                            "Montar el cartucho que recarga el traje.",
                            () -> AtalayaConfig.get().isFiltrosActivos(),
                            v -> AtalayaConfig.get().setFiltrosActivos(v)),
                    receta(pila(() -> AtalayaItems.ALGA_VITRIFICADA), "Alga vitrificada",
                            "Fundir un bloque de alga seca.",
                            () -> AtalayaConfig.get().isAlgaActiva(),
                            v -> AtalayaConfig.get().setAlgaActiva(v)),
                    receta(pila(() -> AtalayaItems.LENTE_MAR), "Lente de mar",
                            "Juntar espejo con alga y montarlo en el casco.",
                            () -> AtalayaConfig.get().isLenteActiva(),
                            v -> AtalayaConfig.get().setLenteActiva(v)),
                    receta(pila(() -> AtalayaItems.COLMILLO_VENENOSO), "Colmillo venenoso",
                            "Juntar colmillo con veneno y montarlo en el traje.",
                            () -> AtalayaConfig.get().isColmilloActivo(),
                            v -> AtalayaConfig.get().setColmilloActivo(v)),
                    receta(pila(() -> AtalayaItems.PATA_ALADA), "Pata alada",
                            "Juntar pata con alon y montarla en el traje.",
                            () -> AtalayaConfig.get().isPataAladaActiva(),
                            v -> AtalayaConfig.get().setPataAladaActiva(v)),
                    receta(pila(() -> AtalayaItems.AGUA_PURIFICADA), "Agua purificada",
                            "Hervir una botella de agua para rehidratarte.",
                            () -> AtalayaConfig.get().isAguaActiva(),
                            v -> AtalayaConfig.get().setAguaActiva(v))
            )
    );

    /**
     * Los grupos ya repartidos en filas. Se calcula una vez: no depende del
     * estado, solo de cuantos interruptores hay.
     */
    private static final List<List<Interruptor>> FILAS_PINTADAS = repartir();

    private static final int PAGINAS =
            Math.max(1, (FILAS_PINTADAS.size() + FILAS_CONTENIDO - 1) / FILAS_CONTENIDO);

    private static List<List<Interruptor>> repartir() {
        List<List<Interruptor>> filas = new ArrayList<>();
        for (List<Interruptor> grupo : GRUPOS) {
            for (int i = 0; i < grupo.size(); i += ANCHO) {
                filas.add(grupo.subList(i, Math.min(i + ANCHO, grupo.size())));
            }
        }
        return List.copyOf(filas);
    }

    // ------------------------------------------------------------------

    private final Container contenedor;
    private int pagina = 0;

    public ConfigMenu(int id, Inventory inventarioJugador, Container contenedor) {
        super(net.minecraft.world.inventory.MenuType.GENERIC_9x6, id, inventarioJugador, contenedor, FILAS);
        this.contenedor = contenedor;
        refrescar();
    }

    /** Abre el panel a un jugador. */
    public static void abrir(ServerPlayer jugador) {
        Container contenedor = new SimpleContainer(TAMANO);
        jugador.openMenu(new SimpleMenuProvider(
                (id, inv, p) -> new ConfigMenu(id, inv, contenedor),
                // Sin color: el titulo de un contenedor va en el gris oscuro de
                // vanilla, como el de un cofre. Coloreado desentona.
                Component.literal("Atalaya - Configuracion")
        ));
    }

    /**
     * Vuelve a pintar el panel segun el estado actual.
     *
     * Se llama al abrir y en cada click, que son eventos raros: no hay ninguna
     * ventaja en cachear los ItemStack y si el riesgo de mostrar un estado viejo.
     */
    public void refrescar() {
        // Los huecos van VACIOS, sin cristal de relleno. Nadie puede meter nada:
        // los clicks en la zona del panel no mueven items y el shift-click esta
        // desactivado, asi que el relleno solo era decoracion que estorbaba.
        for (int i = 0; i < contenedor.getContainerSize(); i++) {
            contenedor.setItem(i, ItemStack.EMPTY);
        }

        for (int fila = 0; fila < FILAS_CONTENIDO; fila++) {
            int global = pagina * FILAS_CONTENIDO + fila;
            if (global >= FILAS_PINTADAS.size()) {
                break;
            }
            List<Interruptor> contenido = FILAS_PINTADAS.get(global);
            for (int col = 0; col < contenido.size(); col++) {
                contenedor.setItem(fila * ANCHO + col, dibujar(contenido.get(col)));
            }
        }

        pintarNavegacion();
        // Empuja el cambio al cliente ya, sin esperar al barrido del siguiente tick.
        broadcastChanges();
    }

    /**
     * La fila de abajo. Las flechas solo aparecen si hay adonde ir, para que no
     * haya botones que no hacen nada.
     */
    private void pintarNavegacion() {
        if (pagina > 0) {
            contenedor.setItem(SLOT_ANTERIOR, boton(Items.ARROW, "Pagina anterior"));
        }
        if (pagina < PAGINAS - 1) {
            contenedor.setItem(SLOT_SIGUIENTE, boton(Items.ARROW, "Pagina siguiente"));
        }

        ItemStack indicador = new ItemStack(Items.BOOK, Math.max(1, pagina + 1));
        indicador.set(AtalayaComponents.ICONO_MENU, true);
        indicador.set(DataComponents.CUSTOM_NAME,
                Component.literal("Pagina " + (pagina + 1) + " de " + PAGINAS)
                        .withStyle(ChatFormatting.WHITE)
                        .withStyle(ChatFormatting.BOLD));
        indicador.set(DataComponents.TOOLTIP_DISPLAY,
                TooltipDisplay.DEFAULT.withHidden(DataComponents.ATTRIBUTE_MODIFIERS, true));
        contenedor.setItem(SLOT_PAGINA, indicador);
    }

    private static ItemStack boton(net.minecraft.world.item.Item item, String nombre) {
        ItemStack pila = new ItemStack(item);
        pila.set(AtalayaComponents.ICONO_MENU, true);
        pila.set(DataComponents.CUSTOM_NAME,
                Component.literal(nombre).withStyle(ChatFormatting.YELLOW));
        pila.set(DataComponents.TOOLTIP_DISPLAY,
                TooltipDisplay.DEFAULT.withHidden(DataComponents.ATTRIBUTE_MODIFIERS, true));
        return pila;
    }

    /**
     * Un icono de interruptor: nombre en verde o rojo, estado en el tooltip y
     * brillo de encantamiento cuando esta activo.
     */
    private static ItemStack dibujar(Interruptor interruptor) {
        ItemStack base = interruptor.icono().get();
        boolean activo = interruptor.estado().getAsBoolean();

        // Marca de icono: las piezas del traje generan su propia descripcion al
        // mostrarse, y sin esto el icono del crafteo arrastraria al panel la
        // lista de caracteristicas mezclada con el texto del interruptor.
        base.set(AtalayaComponents.ICONO_MENU, true);

        base.set(DataComponents.CUSTOM_NAME,
                Component.literal(interruptor.nombre())
                        .withStyle(activo ? ChatFormatting.GREEN : ChatFormatting.RED)
                        .withStyle(ChatFormatting.BOLD));

        base.set(DataComponents.LORE, new ItemLore(List.of(
                Component.literal(interruptor.descripcion()).withStyle(ChatFormatting.GRAY),
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
     * Intercepta los clicks: los de la zona del panel cambian interruptores o
     * pasan pagina, y nunca mueven items; los del inventario se dejan pasar.
     */
    @Override
    public void clicked(int slot, int boton, ContainerInput tipo, Player jugador) {
        if (slot < 0 || slot >= contenedor.getContainerSize()) {
            super.clicked(slot, boton, tipo, jugador);
            return;
        }

        if (slot >= INICIO_NAVEGACION) {
            navegar(slot);
            return;
        }

        Interruptor interruptor = enRanura(slot);
        if (interruptor == null) {
            return; // hueco vacio
        }

        boolean nuevo = !interruptor.estado().getAsBoolean();
        interruptor.poner().accept(nuevo);
        avisar(jugador, interruptor.nombre(), nuevo);
        if (interruptor.tocaRecetas()) {
            actualizarLibros(jugador);
        }
        refrescar();
    }

    private void navegar(int slot) {
        if (slot == SLOT_ANTERIOR && pagina > 0) {
            pagina--;
            refrescar();
        } else if (slot == SLOT_SIGUIENTE && pagina < PAGINAS - 1) {
            pagina++;
            refrescar();
        }
        // El indicador y los huecos no hacen nada.
    }

    /** Que interruptor hay en esa ranura de la pagina actual, o null. */
    private Interruptor enRanura(int slot) {
        int global = pagina * FILAS_CONTENIDO + slot / ANCHO;
        if (global >= FILAS_PINTADAS.size()) {
            return null;
        }
        List<Interruptor> contenido = FILAS_PINTADAS.get(global);
        int col = slot % ANCHO;
        return col < contenido.size() ? contenido.get(col) : null;
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

    /** El panel no tiene "quick move": evita que shift-click saque los iconos. */
    @Override
    public ItemStack quickMoveStack(Player jugador, int slot) {
        return ItemStack.EMPTY;
    }
}
