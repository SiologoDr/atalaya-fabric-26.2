package com.atalaya.item;

import net.minecraft.network.chat.Component;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.item.component.TooltipDisplay;

import java.util.function.Consumer;

/**
 * Pieza del traje Hazmat.
 *
 * La descripcion se GENERA al mostrarla leyendo los componentes de la pieza, no
 * se guarda escrita dentro del item.
 *
 * Por que: las mejoras se anaden por caminos distintos y cada una escribiria su
 * propia version del lore. La herreria ademas aplica los componentes de la
 * pieza base ENCIMA del resultado, asi que un lore escrito por la receta
 * quedaria pisado por el de la pieza original: funcionaria cada mejora por
 * separado y fallaria al combinarlas.
 *
 * Solo se listan las MEJORAS. La resistencia a la radiacion que da cada pieza
 * de base no se menciona: es propia del traje, no algo que el jugador haya
 * conseguido, y repetirla en las cuatro piezas solo ensucia el tooltip.
 */
public class HazmatArmorItem extends Item {

    /** Cada mejora se nombra con el color de su item, para reconocerla de un vistazo. */
    private static final int VERDE_COLMILLO = 0x8CE05A;
    private static final int AZUL_CRISTAL = 0x8CD8FF;
    private static final int CANELA_PATA = 0xD9A86C;

    /** Gris claro para el "Mejora de": lo que destaca es el nombre del item. */
    private static final int GRIS = 0xAAAAAA;

    /** Vineta al inicio de cada mejora. */
    private static final String VINETA = "• ";

    public HazmatArmorItem(Properties propiedades) {
        super(propiedades);
    }

    @Override
    public void appendHoverText(ItemStack pieza,
                                TooltipContext contexto,
                                TooltipDisplay display,
                                Consumer<Component> salida,
                                TooltipFlag bandera) {
        // Si la pieza esta haciendo de icono en el menu de configuracion, su
        // tooltip lo escribe el menu.
        if (AtalayaComponents.ICONO_MENU != null
                && Boolean.TRUE.equals(pieza.get(AtalayaComponents.ICONO_MENU))) {
            return;
        }

        boolean colmillo = HazmatArmor.esAntiveneno(pieza);
        boolean cristal = HazmatArmor.tieneVisorExcelente(pieza);
        boolean pata = HazmatArmor.esAmortiguada(pieza);
        if (!colmillo && !cristal && !pata) {
            return;
        }

        // Linea en blanco para separar las mejoras del nombre de la pieza.
        salida.accept(Component.empty());

        if (colmillo) {
            salida.accept(mejora("item.atalaya.colmillo_venenoso", VERDE_COLMILLO));
        }
        if (cristal) {
            salida.accept(mejora("item.atalaya.cristal_pulido", AZUL_CRISTAL));
        }
        if (pata) {
            salida.accept(mejora("item.atalaya.pata_ligera", CANELA_PATA));
        }
    }

    /**
     * "• Mejora de <item>", con el nombre del item en color y el resto en gris.
     *
     * El nombre se toma de la clave de traduccion del propio item, asi que si
     * se renombra el item la mejora lo sigue sola.
     */
    private static Component mejora(String claveItem, int color) {
        Component nombre = Component.translatable(claveItem)
                .withStyle(s -> s.withColor(color).withItalic(false));

        return Component.literal(VINETA)
                .withStyle(s -> s.withColor(GRIS).withItalic(false))
                .append(Component.translatable("item.atalaya.hazmat.mejora", nombre)
                        .withStyle(s -> s.withColor(GRIS).withItalic(false)));
    }
}
