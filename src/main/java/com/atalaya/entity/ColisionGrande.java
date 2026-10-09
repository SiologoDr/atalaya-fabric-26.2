package com.atalaya.entity;

import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.WeakHashMap;
import java.util.concurrent.ConcurrentHashMap;
import java.util.function.Predicate;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.AABB;
import org.jspecify.annotations.Nullable;

/**
 * Las entidades grandes que se pisan (los estrados de las Trompetas, las
 * piedras del Sello de Rajang, el altar del Idolo).
 *
 * Vanilla guarda cada entidad en la seccion de 16 bloques donde esta su centro
 * y, al buscar con que choca alguien, solo mira las secciones a 2 bloques de su
 * caja. Un escalon de 13 bloques de ancho tiene el centro a 6,5 de su borde: a
 * un lado de una frontera de seccion no se encontraba, no chocaba y se
 * atravesaba (09-10-2026, Juan: en las Trompetas "si no das espacio
 * constantemente traspasas la estructura"). Aqui se apuntan y
 * LevelEntidadesMixin las anade a las busquedas cuya caja tocan.
 *
 * Una lista por mundo: las entidades son iguales si tienen el mismo id, y en un
 * solo jugador la copia del cliente y la del servidor comparten id (en un solo
 * conjunto se pisaban y el servidor se quedaba sin las suyas).
 */
public final class ColisionGrande {

    private static final Map<Level, Set<Entity>> GRANDES = Collections.synchronizedMap(new WeakHashMap<>());

    private ColisionGrande() {
    }

    /** Se apunta en su mundo (cada tick, por si acaso; es un conjunto). */
    public static void apuntar(Entity e) {
        GRANDES.computeIfAbsent(e.level(), k -> ConcurrentHashMap.newKeySet()).add(e);
    }

    /** Anade a "lista" las grandes de este mundo que tocan la caja y cumplen el filtro. */
    public static void completar(Level nivel, @Nullable Entity salvo, AABB caja, Predicate<? super Entity> filtro, List<Entity> lista) {
        Set<Entity> estas = GRANDES.get(nivel);
        if (estas == null || estas.isEmpty()) {
            return;
        }
        for (Entity e : estas) {
            if (e.isRemoved()) {
                estas.remove(e);
                continue;
            }
            if (e == salvo || !e.getBoundingBox().intersects(caja) || lista.contains(e) || !filtro.test(e)) {
                continue;
            }
            lista.add(e);
        }
    }
}
