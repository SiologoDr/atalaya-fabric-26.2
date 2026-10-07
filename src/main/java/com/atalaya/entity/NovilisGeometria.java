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
    public static final int DURACION_DESPERTAR = 48;
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
    public static final int DESPERTAR_RUGE = 29;
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
