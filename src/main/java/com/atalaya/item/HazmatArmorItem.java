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
 * Su unica particularidad es que la descripcion se GENERA al mostrarla, leyendo
 * los componentes de la pieza, en vez de guardarse escrita dentro del item.
 *
 * Por que: las caracteristicas se anaden por caminos distintos (el visor sale
 * al fabricar, el antiveneno en la mesa de herreria) y cada uno escribiria su
 * propia version del lore. La herreria ademas aplica los componentes de la
 * pieza base ENCIMA del resultado, asi que un lore escrito por la receta
 * quedaria pisado por el de la pieza original: funcionaria cada mejora por
 * separado y fallaria al combinarlas.
 *
 * Generandolo aqui, cualquier combinacion sale bien sola y anadir una
 * caracteristica nueva es una linea.
 */
public class HazmatArmorItem extends Item {

    // Tonos claros, para que se lean sobre el fondo oscuro del tooltip.
    private static final int AMARILLO = 0xFCFC54;

    /**
     * Color del texto corriente de las caracteristicas. Va en gris claro a
     * proposito: asi las palabras destacadas de cada linea resaltan solas.
     */
    private static final int TEXTO = 0xC6C6C6;

    // Una palabra destacada por caracteristica, con el color de su tema.
    private static final int LILA_GEODA = 0xE4A8FF;
    private static final int ROJO_SUAVE = 0xFF8A8A;
    private static final int VERDE_SUAVE = 0x8CE05A;

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
        // tooltip lo escribe el menu: no le anadimos las caracteristicas.
        if (AtalayaComponents.ICONO_MENU != null
                && Boolean.TRUE.equals(pieza.get(AtalayaComponents.ICONO_MENU))) {
            return;
        }

        salida.accept(Component.empty());
        salida.accept(titulo());
        salida.accept(Component.empty());
        salida.accept(lineaRadiacion());

        if (HazmatArmor.tieneVisorExcelente(pieza)) {
            salida.accept(caracteristica(
                    "item.atalaya.hazmat.lore.visor_excelente",
                    "item.atalaya.hazmat.lore.visor_excelente.palabra",
                    ROJO_SUAVE));
        }
        if (HazmatArmor.esAntiveneno(pieza)) {
            salida.accept(caracteristica(
                    "item.atalaya.hazmat.lore.antiveneno",
                    "item.atalaya.hazmat.lore.antiveneno.palabra",
                    VERDE_SUAVE));
        }
    }

    /**
     * Una linea de caracteristica: texto en gris con UNA palabra destacada.
     *
     * La palabra viaja como argumento (%s) de la traduccion en vez de partir la
     * frase en dos claves, asi cada idioma decide donde colocarla.
     */
    private static Component caracteristica(String claveFrase, String clavePalabra, int colorPalabra) {
        Component palabra = Component.translatable(clavePalabra)
                .withStyle(s -> s.withColor(colorPalabra).withItalic(false));
        return Component.translatable(claveFrase, palabra)
                .withStyle(s -> s.withColor(TEXTO).withItalic(false));
    }

    /**
     * "☢ Caracteristicas" con el subrayado SOLO en la palabra: el icono va en
     * un trozo aparte, porque una linea bajo el simbolo queda sucia.
     */
    private static Component titulo() {
        return Component.literal("☢ ")
                .withStyle(s -> s.withColor(AMARILLO).withItalic(false))
                .append(Component.translatable("item.atalaya.hazmat.lore.titulo")
                        .withStyle(s -> s.withColor(AMARILLO).withUnderlined(true).withItalic(false)));
    }

    /**
     * "• Resiste un 25% la radiacion de la Geoda", con "Geoda" en lila.
     *
     * La palabra va como ARGUMENTO de la traduccion (%s) en vez de partir la
     * frase en dos claves: asi cada idioma decide donde colocarla.
     */
    private static Component lineaRadiacion() {
        return caracteristica("item.atalaya.hazmat.lore.radiacion",
                "item.atalaya.hazmat.lore.geoda", LILA_GEODA);
    }
}
