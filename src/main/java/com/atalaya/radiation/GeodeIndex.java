package com.atalaya.radiation;

import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.chunk.LevelChunk;
import net.minecraft.world.level.chunk.LevelChunkSection;
import net.minecraft.world.phys.Vec3;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Indice de las amatistas en gemacion (las fuentes de radiacion).
 *
 * En vez de mirar el mundo alrededor de cada jugador cada segundo, se apuntan
 * las posiciones una sola vez al cargar el chunk. Consultar "que tengo cerca"
 * pasa a ser barato.
 *
 * La clave del rendimiento es {@code LevelChunkSection.maybeHas(...)}: cada
 * seccion de 16x16x16 lleva una paleta con los bloques que contiene, asi que se
 * descarta entera con una sola comprobacion. Como la amatista en gemacion solo
 * aparece en geodas, la inmensa mayoria de secciones se saltan sin mirar un
 * solo bloque.
 */
public final class GeodeIndex {

    /** mundo -> (chunk -> posiciones de amatista en gemacion). */
    private static final Map<ServerLevel, Map<Long, List<BlockPos>>> POR_MUNDO = new ConcurrentHashMap<>();

    private GeodeIndex() {
    }

    private static long clave(ChunkPos pos) {
        return pos.pack();
    }

    private static boolean esFuente(BlockState estado) {
        return estado.is(Blocks.BUDDING_AMETHYST);
    }

    // ------------------------------------------------------------------
    //  Mantenimiento del indice
    // ------------------------------------------------------------------

    public static void alCargarChunk(ServerLevel nivel, LevelChunk chunk) {
        List<BlockPos> encontradas = escanear(chunk);
        Map<Long, List<BlockPos>> mapa = POR_MUNDO.computeIfAbsent(nivel, k -> new ConcurrentHashMap<>());
        if (encontradas.isEmpty()) {
            mapa.remove(clave(chunk.getPos()));
        } else {
            mapa.put(clave(chunk.getPos()), encontradas);
        }
    }

    public static void alDescargarChunk(ServerLevel nivel, LevelChunk chunk) {
        Map<Long, List<BlockPos>> mapa = POR_MUNDO.get(nivel);
        if (mapa != null) {
            mapa.remove(clave(chunk.getPos()));
        }
    }

    /** Al apagar el servidor: que no queden mundos retenidos en memoria. */
    public static void limpiar() {
        POR_MUNDO.clear();
    }

    /**
     * Da de alta una fuente colocada en caliente.
     *
     * Sin esto, colocar amatista en un chunk ya cargado no emitiria radiacion
     * hasta que el chunk se descargara y volviera.
     */
    public static void agregar(ServerLevel nivel, BlockPos pos) {
        long clave = ChunkPos.pack(pos.getX() >> 4, pos.getZ() >> 4);
        POR_MUNDO.computeIfAbsent(nivel, k -> new ConcurrentHashMap<>())
                .computeIfAbsent(clave, k -> new ArrayList<>())
                .add(pos.immutable());
    }

    /**
     * Da de baja una fuente que se ha roto.
     *
     * Sin esto quedaria "radiacion fantasma": el indice seguiria creyendo que
     * hay amatista donde ya no la hay. Es el caso que si pasa en supervivencia,
     * porque la amatista en gemacion se puede romper (aunque no suelte nada).
     */
    public static void quitar(ServerLevel nivel, BlockPos pos) {
        Map<Long, List<BlockPos>> mapa = POR_MUNDO.get(nivel);
        if (mapa == null) {
            return;
        }
        long clave = ChunkPos.pack(pos.getX() >> 4, pos.getZ() >> 4);
        List<BlockPos> lista = mapa.get(clave);
        if (lista == null) {
            return;
        }
        lista.removeIf(p -> p.equals(pos));
        if (lista.isEmpty()) {
            mapa.remove(clave);
        }
    }

    /** true si el bloque es una fuente de radiacion. */
    public static boolean esFuenteDeRadiacion(BlockState estado) {
        return esFuente(estado);
    }

    private static List<BlockPos> escanear(LevelChunk chunk) {
        List<BlockPos> encontradas = new ArrayList<>();
        LevelChunkSection[] secciones = chunk.getSections();
        int baseX = chunk.getPos().getMinBlockX();
        int baseZ = chunk.getPos().getMinBlockZ();

        for (int i = 0; i < secciones.length; i++) {
            LevelChunkSection seccion = secciones[i];
            // Descarte rapido: la paleta dice si la seccion puede contenerlo.
            if (seccion.hasOnlyAir() || !seccion.maybeHas(GeodeIndex::esFuente)) {
                continue;
            }
            int baseY = chunk.getMinY() + (i << 4);
            for (int y = 0; y < 16; y++) {
                for (int z = 0; z < 16; z++) {
                    for (int x = 0; x < 16; x++) {
                        if (esFuente(seccion.getBlockState(x, y, z))) {
                            encontradas.add(new BlockPos(baseX + x, baseY + y, baseZ + z));
                        }
                    }
                }
            }
        }
        return encontradas;
    }

    // ------------------------------------------------------------------
    //  Consulta
    // ------------------------------------------------------------------

    /**
     * Distancia a la amatista mas cercana dentro de maxDist, o -1 si no hay
     * ninguna. Solo mira los chunks vecinos, no el mundo entero.
     */
    public static double distanciaMasCercana(ServerLevel nivel, Vec3 desde, double maxDist) {
        Map<Long, List<BlockPos>> mapa = POR_MUNDO.get(nivel);
        if (mapa == null || mapa.isEmpty()) {
            return -1; // salida instantanea: este mundo no tiene amatistas indexadas
        }

        int cx = ((int) Math.floor(desde.x)) >> 4;
        int cz = ((int) Math.floor(desde.z)) >> 4;
        int radioChunks = (int) Math.ceil(maxDist / 16.0);
        double mejorSq = Double.MAX_VALUE;
        double maxSq = maxDist * maxDist;

        for (int dx = -radioChunks; dx <= radioChunks; dx++) {
            for (int dz = -radioChunks; dz <= radioChunks; dz++) {
                List<BlockPos> lista = mapa.get(ChunkPos.pack(cx + dx, cz + dz));
                if (lista == null) {
                    continue;
                }
                for (BlockPos p : lista) {
                    double ex = (p.getX() + 0.5) - desde.x;
                    double ey = (p.getY() + 0.5) - desde.y;
                    double ez = (p.getZ() + 0.5) - desde.z;
                    double sq = ex * ex + ey * ey + ez * ez;
                    if (sq < mejorSq) {
                        mejorSq = sq;
                    }
                }
            }
        }

        return (mejorSq <= maxSq) ? Math.sqrt(mejorSq) : -1;
    }

    /** Cuantas fuentes hay indexadas (para diagnostico). */
    public static int totalIndexadas() {
        int n = 0;
        for (Map<Long, List<BlockPos>> mapa : POR_MUNDO.values()) {
            for (List<BlockPos> lista : mapa.values()) {
                n += lista.size();
            }
        }
        return n;
    }
}
