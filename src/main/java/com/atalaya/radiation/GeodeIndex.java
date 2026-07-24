package com.atalaya.radiation;

import com.atalaya.Atalaya;
import org.bukkit.Chunk;
import org.bukkit.ChunkSnapshot;
import org.bukkit.Location;
import org.bukkit.Material;
import org.bukkit.World;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;

/**
 * Indice espacial de las amatistas (fuentes de radiacion).
 *
 * En vez de escanear el mundo cada segundo, guardamos las posiciones de amatista
 * una sola vez (al cargar cada chunk) y las mantenemos al dia con los eventos de
 * romper/colocar. Consultar "cual es la fuente mas cercana" pasa a ser barato.
 *
 * Regla de hilos: TODA modificacion del mapa ocurre en el hilo principal.
 * El escaneo pesado corre async sobre un ChunkSnapshot (thread-safe) y el
 * resultado se guarda de vuelta en el hilo principal.
 */
public class GeodeIndex {

    private final Atalaya plugin;

    // mundo -> (clave de chunk -> lista de posiciones {x, y, z} en coordenadas absolutas)
    private final Map<UUID, Map<Long, List<int[]>>> porMundo = new HashMap<>();

    // Rango de altura donde se buscan geodas al escanear (optimizacion).
    private int escaneoYMin;
    private int escaneoYMax;

    public GeodeIndex(Atalaya plugin) {
        this.plugin = plugin;
        loadConfig();
    }

    public void loadConfig() {
        var cfg = plugin.getConfig();
        escaneoYMin = cfg.getInt("radiacion.escaneo-y-min", -64);
        escaneoYMax = cfg.getInt("radiacion.escaneo-y-max", 40);
    }

    private static long claveChunk(int cx, int cz) {
        return ((long) cx & 0xFFFFFFFFL) | (((long) cz & 0xFFFFFFFFL) << 32);
    }

    // ---------------------------------------------------------------------
    //  Escaneo
    // ---------------------------------------------------------------------

    /** Escanea todos los chunks ya cargados de los mundos overworld (al arrancar). */
    public void escanearMundosCargados() {
        for (World world : plugin.getServer().getWorlds()) {
            if (world.getEnvironment() != World.Environment.NORMAL) {
                continue;
            }
            for (Chunk chunk : world.getLoadedChunks()) {
                escanearChunkAsync(chunk);
            }
        }
    }

    /**
     * Toma una foto del chunk (en el hilo principal) y la escanea en un hilo
     * aparte para no tocar el TPS. Guarda el resultado de vuelta en el hilo principal.
     */
    public void escanearChunkAsync(Chunk chunk) {
        final ChunkSnapshot snapshot = chunk.getChunkSnapshot(false, false, false);
        final UUID mundo = chunk.getWorld().getUID();
        final int cx = chunk.getX();
        final int cz = chunk.getZ();
        final int minY = Math.max(chunk.getWorld().getMinHeight(), escaneoYMin);
        final int maxY = Math.min(chunk.getWorld().getMaxHeight() - 1, escaneoYMax);

        plugin.getServer().getScheduler().runTaskAsynchronously(plugin, () -> {
            List<int[]> encontradas = new ArrayList<>();
            for (int x = 0; x < 16; x++) {
                for (int z = 0; z < 16; z++) {
                    for (int y = minY; y <= maxY; y++) {
                        Material tipo = snapshot.getBlockType(x, y, z);
                        if (RadiationSources.esFuente(tipo)) {
                            encontradas.add(new int[]{(cx << 4) + x, y, (cz << 4) + z});
                        }
                    }
                }
            }
            // De vuelta al hilo principal para guardar.
            plugin.getServer().getScheduler().runTask(plugin, () -> guardarChunk(mundo, cx, cz, encontradas));
        });
    }

    // ---------------------------------------------------------------------
    //  Mutaciones (siempre en hilo principal)
    // ---------------------------------------------------------------------

    private void guardarChunk(UUID mundo, int cx, int cz, List<int[]> fuentes) {
        Map<Long, List<int[]>> mapa = porMundo.computeIfAbsent(mundo, k -> new HashMap<>());
        long clave = claveChunk(cx, cz);
        if (fuentes.isEmpty()) {
            mapa.remove(clave);
        } else {
            mapa.put(clave, fuentes);
        }
    }

    public void quitarChunk(UUID mundo, int cx, int cz) {
        Map<Long, List<int[]>> mapa = porMundo.get(mundo);
        if (mapa != null) {
            mapa.remove(claveChunk(cx, cz));
        }
    }

    public void agregarBloque(UUID mundo, int x, int y, int z) {
        Map<Long, List<int[]>> mapa = porMundo.computeIfAbsent(mundo, k -> new HashMap<>());
        mapa.computeIfAbsent(claveChunk(x >> 4, z >> 4), k -> new ArrayList<>())
                .add(new int[]{x, y, z});
    }

    public void quitarBloque(UUID mundo, int x, int y, int z) {
        Map<Long, List<int[]>> mapa = porMundo.get(mundo);
        if (mapa == null) {
            return;
        }
        long clave = claveChunk(x >> 4, z >> 4);
        List<int[]> lista = mapa.get(clave);
        if (lista == null) {
            return;
        }
        lista.removeIf(p -> p[0] == x && p[1] == y && p[2] == z);
        if (lista.isEmpty()) {
            mapa.remove(clave);
        }
    }

    public void limpiar() {
        porMundo.clear();
    }

    // ---------------------------------------------------------------------
    //  Consulta
    // ---------------------------------------------------------------------

    /**
     * Distancia a la amatista mas cercana dentro de maxDist, o -1 si no hay
     * ninguna cerca. Solo mira los chunks vecinos al jugador, no el mundo entero.
     */
    public double distanciaMasCercana(Location loc, double maxDist) {
        World world = loc.getWorld();
        if (world == null) {
            return -1;
        }
        Map<Long, List<int[]>> mapa = porMundo.get(world.getUID());
        if (mapa == null || mapa.isEmpty()) {
            return -1; // salida instantanea: este mundo no tiene amatistas indexadas
        }

        int cx = loc.getBlockX() >> 4;
        int cz = loc.getBlockZ() >> 4;
        int radioChunks = (int) Math.ceil(maxDist / 16.0);

        double px = loc.getX();
        double py = loc.getY();
        double pz = loc.getZ();
        double mejorSq = Double.MAX_VALUE;
        double maxSq = maxDist * maxDist;

        for (int dx = -radioChunks; dx <= radioChunks; dx++) {
            for (int dz = -radioChunks; dz <= radioChunks; dz++) {
                List<int[]> lista = mapa.get(claveChunk(cx + dx, cz + dz));
                if (lista == null) {
                    continue;
                }
                for (int[] p : lista) {
                    double ex = (p[0] + 0.5) - px;
                    double ey = (p[1] + 0.5) - py;
                    double ez = (p[2] + 0.5) - pz;
                    double sq = ex * ex + ey * ey + ez * ez;
                    if (sq < mejorSq) {
                        mejorSq = sq;
                    }
                }
            }
        }

        return (mejorSq <= maxSq) ? Math.sqrt(mejorSq) : -1;
    }
}
