package com.atalaya.entity;

/**
 * Los minijuegos de Novilis (octubre de 2026). Juan, tras cinco fichas, eligio
 * cuatro y los repartio para que cada fase tenga algo nuevo: El Caballero Manda
 * y la Forja del Juramento en la I (que no tenia nada que hacer en grupo),
 * ninguno en la II (ya tiene las Trompetas y la Sombra del Escudo), Piedra,
 * Papel o Tijera en la III y Frio o Caliente en la IV. Uno a la vez, como los
 * de Nerea y Rajang, y como las fases se suman, en la IV pueden salir todos.
 * Cada uno vive en su clase (MandaNovilis, ForjaNovilis, PiedraNovilis,
 * CalienteNovilis).
 */
public final class MinijuegosNovilis {

    public static final int NINGUNO = 0;
    public static final int MANDA = 1;
    public static final int FORJA = 2;
    public static final int PIEDRA = 3;
    public static final int CALIENTE = 4;
    /** La fase desde la que sale cada uno. */
    static final int[] FASE = {0, 1, 1, 3, 4};
    /** Su nombre en las claves de texto. */
    public static final String[] CLAVES = {"", "manda", "forja", "piedra", "caliente"};

    /** Las ordenes del Caballero Manda, por su orden en novilis_ordenes.png. */
    public static final int ARRODILLAOS = 0;
    public static final int SALTAD = 1;
    public static final int MIRAD_SOL = 2;
    public static final int QUIETOS = 3;
    public static final String[] ORDENES = {"arrodillaos", "saltad", "mirad_sol", "quietos"};

    /** Piedra, Papel o Tijera: lo que saca cada uno (0: nada), por su orden en novilis_rps.png. */
    public static final int NADA = 0;
    public static final int PIEDRA_SACA = 1;
    public static final int PAPEL = 2;
    public static final int TIJERA = 3;
    public static final String[] MANOS = {"nada", "piedra", "papel", "tijera"};

    private MinijuegosNovilis() {
    }

    /** Si a gana a b (piedra a tijera, tijera a papel, papel a piedra); nada pierde con todo. */
    public static boolean gana(int a, int b) {
        if (a == NADA) {
            return false;
        }
        if (b == NADA) {
            return true;
        }
        return (a == PIEDRA_SACA && b == TIJERA) || (a == TIJERA && b == PAPEL) || (a == PAPEL && b == PIEDRA_SACA);
    }

    // --- El dato del minijuego (DATA_MINI_INFO) de cada uno ---

    /** El Caballero Manda: la orden, si es de verdad (con "¡Por el Sol...!") y su numero (0: aun no ha dado ninguna). */
    public static int infoManda(int orden, boolean deVerdad, int numero) {
        return (orden & 7) | (deVerdad ? 8 : 0) | ((numero & 15) << 4);
    }

    public static int ordenManda(int info) {
        return info & 7;
    }

    public static boolean deVerdadManda(int info) {
        return (info & 8) != 0;
    }

    public static int numeroManda(int info) {
        return (info >> 4) & 15;
    }

    /**
     * Piedra, Papel o Tijera: la ronda (1 a 5), el golpe de la cuenta (0 antes,
     * 1 piedra, 2 papel, 3 ¡tijera!), lo que ha sacado el (al revelarlo), como
     * ha ido la ronda (0 nada aun, 1 el grupo, 2 el, 3 empate) y las rondas de
     * cada uno.
     */
    public static int infoPiedra(int ronda, int golpe, int suya, int resultado, int grupo, int el) {
        return (ronda & 15) | ((golpe & 3) << 4) | ((suya & 3) << 6) | ((resultado & 3) << 8) | ((grupo & 15) << 10)
                | ((el & 15) << 14);
    }

    public static int rondaPiedra(int info) {
        return info & 15;
    }

    public static int golpePiedra(int info) {
        return (info >> 4) & 3;
    }

    public static int suyaPiedra(int info) {
        return (info >> 6) & 3;
    }

    public static int resultadoPiedra(int info) {
        return (info >> 8) & 3;
    }

    public static int grupoPiedra(int info) {
        return (info >> 10) & 15;
    }

    public static int elPiedra(int info) {
        return (info >> 14) & 15;
    }
}
