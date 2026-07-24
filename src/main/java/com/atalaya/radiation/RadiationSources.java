package com.atalaya.radiation;

import org.bukkit.Material;

import java.util.EnumSet;
import java.util.Set;

/**
 * Define que bloques emiten radiacion (la parte de amatista de una geoda).
 * Centralizado aqui para que el indice, el listener y el manager usen lo mismo.
 */
public final class RadiationSources {

    private static final Set<Material> FUENTES = EnumSet.of(
            Material.AMETHYST_BLOCK,
            Material.BUDDING_AMETHYST,
            Material.AMETHYST_CLUSTER,
            Material.SMALL_AMETHYST_BUD,
            Material.MEDIUM_AMETHYST_BUD,
            Material.LARGE_AMETHYST_BUD
    );

    private RadiationSources() {
    }

    public static boolean esFuente(Material material) {
        return FUENTES.contains(material);
    }
}
