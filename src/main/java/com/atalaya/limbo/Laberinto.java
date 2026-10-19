package com.atalaya.limbo;

import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;

import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Deque;
import java.util.List;

/**
 * El laberinto del Limbo: una cuadricula de celdas de 3 x 3 (pasillos de tres de ancho y cinco de alto, con muros de
 * uno), cerrada por fuera, con suelo y techo. Se hace con un recorrido en profundidad (un laberinto perfecto: de
 * cualquier celda a cualquier otra hay un solo camino) y luego se le abren unos cuantos muros mas, para que haya
 * vueltas y no sea solo ir y volver de callejones. Tiene cuatro salas grandes (3 x 3 celdas sin muros por dentro),
 * donde caben los colosos, y faroles en algunos muros.
 *
 * <pre>
 *   y = 64        el suelo (suelo_limbo; la salida, salida_limbo, ocupa el suelo de una celda entera)
 *   y = 65..69    los pasillos
 *   y = 70        el techo (piedra_limbo)
 * </pre>
 */
public final class Laberinto {

    /** Si cambia lo que se construye, se sube y los mundos con el laberinto viejo lo rehacen. */
    public static final int VERSION = 1;
    /** Celdas por lado, lo que mide cada una con su muro y la esquina de abajo del laberinto. */
    public static final int CELDAS = 25;
    static final int PASO = 4;
    public static final int X0 = -50;
    public static final int Z0 = -50;
    public static final int SUELO = 64;
    public static final int ALTO = 5;
    public static final int TECHO = SUELO + ALTO + 1;
    /** Lo que mide de lado (en bloques). */
    public static final int LADO = CELDAS * PASO + 1;

    /** Las salas: la celda de su esquina (i, j); cada una ocupa 3 x 3 celdas. */
    static final int[][] SALAS = {{3, 3}, {CELDAS - 6, 3}, {3, CELDAS - 6}, {CELDAS - 6, CELDAS - 6}};

    private Laberinto() {
    }

    /** El centro de una celda, a ras de suelo (donde se pone uno de pie). */
    public static BlockPos centro(int i, int j) {
        return new BlockPos(X0 + i * PASO + 2, SUELO + 1, Z0 + j * PASO + 2);
    }

    /** La celda en la que cae ese sitio (o -1 si esta fuera). */
    public static int celdaI(double x) {
        int i = (int) Math.floor((x - X0) / PASO);
        return i >= 0 && i < CELDAS ? i : -1;
    }

    public static int celdaJ(double z) {
        int j = (int) Math.floor((z - Z0) / PASO);
        return j >= 0 && j < CELDAS ? j : -1;
    }

    /** Si ese sitio esta dentro del laberinto (por dentro de los muros de fuera y entre el suelo y el techo). */
    public static boolean dentro(double x, double y, double z) {
        return x > X0 + 1 && x < X0 + LADO - 1 && z > Z0 + 1 && z < Z0 + LADO - 1 && y > SUELO - 0.5 && y < TECHO;
    }

    static boolean enSala(int i, int j) {
        for (int[] s : SALAS) {
            if (i >= s[0] && i < s[0] + 3 && j >= s[1] && j < s[1] + 3) {
                return true;
            }
        }
        return false;
    }

    // ------------------------------------------------------------------
    //  El trazado
    // ------------------------------------------------------------------

    /**
     * Los muros que quedan: este[i][j], el muro entre la celda (i, j) y la (i + 1, j); sur[i][j], entre (i, j) y
     * (i, j + 1).
     */
    record Trazado(boolean[][] este, boolean[][] sur) {
    }

    static Trazado trazar(long semilla) {
        RandomSource azar = RandomSource.create(semilla);
        boolean[][] este = new boolean[CELDAS][CELDAS];
        boolean[][] sur = new boolean[CELDAS][CELDAS];
        for (int i = 0; i < CELDAS; i++) {
            for (int j = 0; j < CELDAS; j++) {
                este[i][j] = true;
                sur[i][j] = true;
            }
        }
        boolean[][] visto = new boolean[CELDAS][CELDAS];
        Deque<int[]> pila = new ArrayDeque<>();
        pila.push(new int[]{CELDAS / 2, CELDAS / 2});
        visto[CELDAS / 2][CELDAS / 2] = true;
        int[][] dirs = {{1, 0}, {-1, 0}, {0, 1}, {0, -1}};
        while (!pila.isEmpty()) {
            int[] c = pila.peek();
            List<int[]> libres = new ArrayList<>();
            for (int[] d : dirs) {
                int ni = c[0] + d[0];
                int nj = c[1] + d[1];
                if (ni >= 0 && nj >= 0 && ni < CELDAS && nj < CELDAS && !visto[ni][nj]) {
                    libres.add(d);
                }
            }
            if (libres.isEmpty()) {
                pila.pop();
                continue;
            }
            int[] d = libres.get(azar.nextInt(libres.size()));
            int ni = c[0] + d[0];
            int nj = c[1] + d[1];
            abrir(este, sur, c[0], c[1], d);
            visto[ni][nj] = true;
            pila.push(new int[]{ni, nj});
        }
        // Unas cuantas vueltas mas (uno de cada nueve muros que quedan).
        for (int i = 0; i < CELDAS; i++) {
            for (int j = 0; j < CELDAS; j++) {
                if (i < CELDAS - 1 && este[i][j] && azar.nextInt(9) == 0) {
                    este[i][j] = false;
                }
                if (j < CELDAS - 1 && sur[i][j] && azar.nextInt(9) == 0) {
                    sur[i][j] = false;
                }
            }
        }
        // Las salas: sin muros por dentro.
        for (int[] s : SALAS) {
            for (int i = s[0]; i < s[0] + 3; i++) {
                for (int j = s[1]; j < s[1] + 3; j++) {
                    if (i < s[0] + 2) {
                        este[i][j] = false;
                    }
                    if (j < s[1] + 2) {
                        sur[i][j] = false;
                    }
                }
            }
        }
        return new Trazado(este, sur);
    }

    private static void abrir(boolean[][] este, boolean[][] sur, int i, int j, int[] d) {
        if (d[0] == 1) {
            este[i][j] = false;
        } else if (d[0] == -1) {
            este[i - 1][j] = false;
        } else if (d[1] == 1) {
            sur[i][j] = false;
        } else {
            sur[i][j - 1] = false;
        }
    }

    // ------------------------------------------------------------------
    //  La construccion
    // ------------------------------------------------------------------

    /** Lo construye entero (suelo, techo, muros, faroles y la salida en su celda). */
    static void construir(ServerLevel nivel, long semilla, int salidaI, int salidaJ) {
        Trazado t = trazar(semilla);
        RandomSource azar = RandomSource.create(semilla ^ 0x5DEECE66DL);
        BlockState piedra = Limbo.PIEDRA.defaultBlockState();
        BlockState suelo = Limbo.SUELO.defaultBlockState();
        BlockState farol = Limbo.FAROL.defaultBlockState();
        BlockState aire = Blocks.AIR.defaultBlockState();
        int flags = Block.UPDATE_CLIENTS | Block.UPDATE_KNOWN_SHAPE;
        BlockPos.MutableBlockPos p = new BlockPos.MutableBlockPos();
        // Que esten generados los trozos de mundo (aunque esten vacios).
        for (int cx = (X0 >> 4) - 1; cx <= ((X0 + LADO) >> 4) + 1; cx++) {
            for (int cz = (Z0 >> 4) - 1; cz <= ((Z0 + LADO) >> 4) + 1; cz++) {
                nivel.getChunk(cx, cz);
            }
        }
        for (int dx = 0; dx < LADO; dx++) {
            for (int dz = 0; dz < LADO; dz++) {
                int x = X0 + dx;
                int z = Z0 + dz;
                nivel.setBlock(p.set(x, SUELO, z), suelo, flags);
                nivel.setBlock(p.set(x, TECHO, z), piedra, flags);
                boolean lineaX = dx % PASO == 0;
                boolean lineaZ = dz % PASO == 0;
                boolean muro;
                if (lineaX && lineaZ) {
                    // Las esquinas de las celdas: muro siempre, salvo dentro de las salas.
                    int i = dx / PASO;
                    int j = dz / PASO;
                    muro = !(i > 0 && j > 0 && i < CELDAS && j < CELDAS && enSala(i - 1, j - 1) && enSala(i, j)
                            && enSala(i - 1, j) && enSala(i, j - 1));
                } else if (lineaX) {
                    int i = dx / PASO;
                    int j = dz / PASO;
                    muro = i == 0 || i == CELDAS || t.este()[i - 1][j];
                } else if (lineaZ) {
                    int i = dx / PASO;
                    int j = dz / PASO;
                    muro = j == 0 || j == CELDAS || t.sur()[i][j - 1];
                } else {
                    muro = false;
                }
                for (int y = SUELO + 1; y < TECHO; y++) {
                    nivel.setBlock(p.set(x, y, z), muro ? piedra : aire, flags);
                }
                // Un farol en el medio de algunos muros (no en las esquinas), a media altura.
                if (muro && (lineaX ^ lineaZ) && ((lineaX ? dz : dx) % PASO == 2) && azar.nextInt(6) == 0) {
                    nivel.setBlock(p.set(x, SUELO + 3, z), farol, flags);
                }
            }
        }
        ponerSalida(nivel, salidaI, salidaJ, true);
    }

    /** Pone (o quita, si 'poner' es falso) la salida en el suelo de esa celda. */
    static void ponerSalida(ServerLevel nivel, int i, int j, boolean poner) {
        if (i < 0 || j < 0) {
            return;
        }
        BlockState b = (poner ? Limbo.SALIDA : Limbo.SUELO).defaultBlockState();
        BlockPos c = centro(i, j);
        for (int dx = -1; dx <= 1; dx++) {
            for (int dz = -1; dz <= 1; dz++) {
                nivel.setBlock(new BlockPos(c.getX() + dx, SUELO, c.getZ() + dz), b, Block.UPDATE_ALL);
            }
        }
    }
}
