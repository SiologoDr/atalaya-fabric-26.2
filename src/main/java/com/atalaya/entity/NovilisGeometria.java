package com.atalaya.entity;

import net.minecraft.world.phys.Vec3;

/**
 * Medidas de Novilis que comparten servidor y cliente. GENERADO por
 * materiales/generadores/novilis_juego_anim.py desde las mismas poses que las
 * animaciones (ya con la fisica): si una animacion cambia, estos puntos cambian.
 *
 * Los puntos van en bloques y en el espacio del cuerpo: x hacia SU izquierda,
 * y hacia arriba desde los pies, z hacia delante. NovilisEntity los pasa al
 * mundo con el giro del cuerpo.
 */
public final class NovilisGeometria {

    private NovilisGeometria() {
    }

    /** Lo que alcanza la hoja en el Barrido, desde sus pies (bloques). */
    public static final double ALCANCE_HOJA = 13.56;
    /** Lo que avanza el cuerpo por vuelta de la animacion de andar (bloques): con los pies en el suelo, sin patinar. */
    public static final float ZANCADA = 8.329F;
    /** Lo que dura una vuelta de la animacion de andar (segundos de animacion). */
    public static final float PERIODO_ANDAR = 1.400F;
    /** Lo mismo al correr: lo que avanza por vuelta (bloques) y lo que dura (s). */
    public static final float ZANCADA_CORRER = 14.247F;
    public static final float PERIODO_CORRER = 1.100F;

    public static final Vec3 PECHO = new Vec3(0.000, 11.344, 1.753);
    public static final Vec3 CABEZA = new Vec3(0.000, 14.632, 0.110);
    public static final Vec3 HALO = new Vec3(0.000, 15.289, -1.370);
    public static final Vec3 PUNTA_ALZA = new Vec3(-0.005, 25.173, -0.253);
    public static final Vec3 PUNTA_CLAVA = new Vec3(-0.248, -4.306, 3.859);
    public static final Vec3 PUNTA_FUENTES = new Vec3(-0.090, -4.247, 2.815);
    public static final Vec3 PECHO_FUENTES = new Vec3(-0.002, 7.784, 2.242);
    public static final Vec3 MANO_SOL = new Vec3(4.161, 15.936, 0.082);
    public static final Vec3 MANO_INVOCA = new Vec3(-3.118, 24.976, 1.713);
    public static final Vec3 OFRENDA_ALZADO_P = new Vec3(-0.002, 14.620, 3.313);
    public static final Vec3 DIOS_MANO_IZQ = new Vec3(4.820, 15.285, 1.131);
    public static final Vec3 DIOS_MANO_DER = new Vec3(-4.824, 15.286, 1.114);
    public static final Vec3 SOL_PROPIO = new Vec3(0.000, 24.500, -1.500);
    public static final Vec3 PUNTA_TAJO_1 = new Vec3(4.869, 10.013, 12.010);
    public static final Vec3 PUNTA_TAJO_2 = new Vec3(-5.452, 8.420, 12.421);
    public static final Vec3 PUNTA_TAJO_3 = new Vec3(0.562, 4.191, 13.417);
    public static final Vec3 PUNTA_TAJO_4 = new Vec3(6.155, 9.472, 11.861);
    public static final Vec3 MANO_LANZA_1 = new Vec3(1.475, 9.226, 5.209);
    public static final Vec3 MANO_LANZA_2 = new Vec3(1.516, 9.247, 5.187);
    public static final Vec3 MANO_LANZA_3 = new Vec3(1.516, 9.247, 5.187);
    public static final Vec3 DIOS_LANZA_1_P = new Vec3(0.000, 10.386, 4.547);
    public static final Vec3 DIOS_LANZA_2_P = new Vec3(0.000, 10.386, 4.547);
    public static final Vec3 DIOS_LANZA_3_P = new Vec3(0.000, 10.386, 4.547);

    public static final int DURACION_REPOSO = 64;
    public static final int DURACION_ANDAR = 28;
    public static final int DURACION_CORRER = 22;
    public static final int DURACION_DORMIDO = 120;
    public static final int DURACION_DESPERTAR = 190;
    public static final int DURACION_BARRIDO = 52;
    public static final int DURACION_CASTIGO = 44;
    public static final int DURACION_CASTIGO_ONDA = 60;
    public static final int DURACION_SOL = 50;
    public static final int DURACION_TROMPETAS = 36;
    public static final int DURACION_FUENTES = 24;
    public static final int DURACION_FUENTES_CARGA = 40;
    public static final int DURACION_OFRENDA = 40;
    public static final int DURACION_OFRENDA_SOSTIENE = 40;
    public static final int DURACION_DIOS = 80;
    public static final int DURACION_GRITO = 36;
    public static final int DURACION_ATURDIDO = 18;
    public static final int DURACION_ATURDIDO_BUCLE = 48;
    public static final int DURACION_TAMBALEO = 44;
    public static final int DURACION_LIBERACION = 200;
    public static final int DESPERTAR_RUGE = 145;
    public static final int DESPERTAR_ABRE = 40;
    public static final int DESPERTAR_SE_ALZA = 70;
    public static final int DESPERTAR_ALZADO = 120;
    public static final int TAJO_1 = 8;
    public static final int TAJO_2 = 20;
    public static final int TAJO_3 = 30;
    public static final int TAJO_4 = 42;
    public static final int CASTIGO_ALZA = 6;
    public static final int CASTIGO_MARCA = 10;
    public static final int CASTIGO_RAYO = 32;
    public static final int ONDA_CLAVA = 42;
    public static final int SOL_LANZA_1 = 12;
    public static final int SOL_LANZA_2 = 24;
    public static final int SOL_LANZA_3 = 36;
    public static final int TROMPETAS_ALZA = 14;
    public static final int FUENTES_CLAVA = 11;
    public static final int OFRENDA_SUELTA = 8;
    public static final int OFRENDA_AGARRA = 19;
    public static final int OFRENDA_ALZADO = 34;
    public static final int DIOS_SUELTA = 8;
    public static final int DIOS_MARCA = 15;
    public static final int DIOS_RECOGE = 70;
    public static final int DIOS_LANZA_1 = 25;
    public static final int DIOS_LANZA_2 = 41;
    public static final int DIOS_LANZA_3 = 57;
    public static final int GRITO_RUGE = 11;
    public static final int TAMBALEO_RUGE = 24;
    public static final int LIBERACION_ORO = 70;

    /** Cabeza en el despertar, cada 5 ticks (bloques; la camara de la presentacion la sigue). */
    public static final float[][] CABEZA_DESPERTAR = {{0.00F, 10.58F, 2.85F}, {0.00F, 10.62F, 2.80F}, {0.00F, 10.77F, 2.59F}, {0.00F, 10.88F, 2.42F}, {-0.04F, 10.77F, 2.60F}, {-0.11F, 10.46F, 3.04F}, {-0.09F, 10.44F, 3.06F}, {-0.00F, 10.57F, 2.86F}, {0.00F, 10.58F, 2.85F}, {0.00F, 11.08F, 1.89F}, {0.00F, 11.22F, 1.23F}, {0.00F, 11.23F, 1.09F}, {0.03F, 11.23F, 1.10F}, {0.06F, 11.23F, 1.12F}, {0.00F, 11.23F, 1.06F}, {0.00F, 11.34F, 1.36F}, {0.00F, 11.57F, 2.34F}, {0.00F, 11.58F, 2.92F}, {0.00F, 12.45F, 2.52F}, {0.00F, 13.16F, 2.10F}, {0.00F, 13.48F, 1.89F}, {0.00F, 13.54F, 1.86F}, {0.00F, 13.22F, 2.24F}, {0.00F, 13.04F, 2.50F}, {0.00F, 14.32F, -0.70F}, {-0.00F, 14.55F, -1.11F}, {0.01F, 14.55F, -1.17F}, {0.05F, 14.42F, -1.62F}, {-0.01F, 12.88F, 3.09F}, {-0.00F, 14.11F, -0.86F}, {0.05F, 13.63F, -2.23F}, {0.03F, 13.67F, -2.14F}, {-0.06F, 13.77F, -1.90F}, {-0.02F, 13.76F, -1.90F}, {0.04F, 13.75F, -1.91F}, {0.02F, 13.79F, -1.86F}, {-0.00F, 13.83F, -1.82F}, {0.00F, 14.41F, -0.78F}, {0.00F, 14.63F, 0.10F}};
    /** Pecho en el despertar, cada 5 ticks (bloques; la camara de la presentacion la sigue). */
    public static final float[][] PECHO_DESPERTAR = {{0.00F, 7.33F, 2.82F}, {0.00F, 7.37F, 2.80F}, {0.00F, 7.51F, 2.70F}, {0.00F, 7.60F, 2.63F}, {-0.04F, 7.51F, 2.71F}, {-0.14F, 7.27F, 2.89F}, {-0.12F, 7.25F, 2.90F}, {-0.00F, 7.33F, 2.82F}, {0.00F, 7.33F, 2.82F}, {0.00F, 7.55F, 2.57F}, {0.00F, 7.66F, 2.42F}, {0.00F, 7.68F, 2.39F}, {0.00F, 7.69F, 2.39F}, {0.00F, 7.69F, 2.38F}, {0.00F, 7.69F, 2.38F}, {0.00F, 7.75F, 2.55F}, {0.00F, 7.84F, 3.11F}, {0.00F, 7.80F, 3.41F}, {0.00F, 8.71F, 3.21F}, {0.00F, 9.49F, 2.98F}, {0.00F, 9.85F, 2.86F}, {0.00F, 9.92F, 2.84F}, {0.00F, 9.55F, 3.01F}, {0.00F, 9.34F, 3.12F}, {0.00F, 11.23F, 1.50F}, {-0.00F, 11.61F, 1.32F}, {-0.01F, 11.64F, 1.30F}, {-0.06F, 11.70F, 1.08F}, {-0.01F, 9.39F, 3.05F}, {0.00F, 11.06F, 1.37F}, {0.00F, 11.23F, 0.75F}, {0.00F, 11.22F, 0.81F}, {0.00F, 11.19F, 0.94F}, {0.00F, 11.19F, 0.94F}, {0.00F, 11.19F, 0.95F}, {0.00F, 11.19F, 0.95F}, {0.00F, 11.20F, 0.96F}, {0.00F, 11.33F, 1.41F}, {0.00F, 11.35F, 1.75F}};

    public static Vec3 cabezaDespertar(float ticks) {
        return tabla(CABEZA_DESPERTAR, ticks / 5.0F);
    }

    public static Vec3 pechoDespertar(float ticks) {
        return tabla(PECHO_DESPERTAR, ticks / 5.0F);
    }

    private static Vec3 tabla(float[][] t, float f) {
        int n = t.length - 1;
        f = Math.max(0.0F, Math.min(n, f));
        int i = Math.min((int) f, n - 1);
        float k = f - i;
        return new Vec3(t[i][0] + (t[i + 1][0] - t[i][0]) * k, t[i][1] + (t[i + 1][1] - t[i][1]) * k,
                t[i][2] + (t[i + 1][2] - t[i][2]) * k);
    }

    /** Entre las dos manos en la Ofrenda, desde OFRENDA_AGARRA hasta el final, tick a tick. */
    public static final float[][] MANOS_OFRENDA = {{-0.00F, 7.18F, 4.82F}, {-0.00F, 7.21F, 4.82F}, {-0.00F, 7.40F, 4.80F}, {-0.00F, 7.76F, 4.74F}, {-0.00F, 8.13F, 4.67F}, {-0.00F, 8.39F, 4.61F}, {-0.00F, 8.49F, 4.58F}, {-0.00F, 9.42F, 5.06F}, {-0.00F, 10.68F, 5.21F}, {-0.00F, 11.95F, 5.02F}, {-0.00F, 12.97F, 4.64F}, {-0.00F, 13.67F, 4.24F}, {-0.00F, 14.17F, 3.82F}, {-0.00F, 14.45F, 3.53F}, {-0.00F, 14.57F, 3.38F}, {-0.00F, 14.63F, 3.30F}, {-0.00F, 14.63F, 3.30F}, {-0.00F, 14.63F, 3.29F}, {-0.00F, 14.63F, 3.29F}, {-0.00F, 14.63F, 3.29F}, {-0.00F, 14.63F, 3.29F}, {-0.00F, 14.63F, 3.29F}};

    /** Donde estan las manos en la Ofrenda a los tantos ticks (de animacion) de empezar. */
    public static Vec3 manosOfrenda(float ticks) {
        float t = ticks - OFRENDA_AGARRA;
        int n = MANOS_OFRENDA.length - 1;
        if (t >= n) {
            return OFRENDA_ALZADO_P;
        }
        t = Math.max(0, t);
        int i = Math.min((int) t, n - 1);
        float k = t - i;
        float[] a = MANOS_OFRENDA[i];
        float[] b = MANOS_OFRENDA[i + 1];
        return new Vec3(a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k, a[2] + (b[2] - a[2]) * k);
    }
}
