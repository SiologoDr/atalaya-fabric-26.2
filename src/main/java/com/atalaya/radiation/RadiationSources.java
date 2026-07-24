package com.atalaya.radiation;

import org.bukkit.Material;

import java.util.EnumSet;
import java.util.Set;

/**
 * Define que bloques emiten radiacion.
 *
 * Solo la AMATISTA EN GEMACION (budding_amethyst), el corazon de la geoda.
 * La clave del lore: este bloque NO se puede obtener ni colocar en supervivencia
 * (ni con Silk Touch suelta nada), asi que solo existe generado de forma natural.
 * Usarlo como fuente garantiza "radiacion solo en geodas naturales" sin tener
 * que rastrear que bloque coloco o movio un jugador.
 */
public final class RadiationSources {

    private static final Set<Material> FUENTES = EnumSet.of(
            Material.BUDDING_AMETHYST
    );

    private RadiationSources() {
    }

    public static boolean esFuente(Material material) {
        return FUENTES.contains(material);
    }
}
