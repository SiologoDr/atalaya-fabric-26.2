package com.atalaya.entity;

import net.minecraft.world.phys.Vec3;

/**
 * Medidas de Yiatzo, el Mago del Viento que comparten servidor y cliente. GENERADO por
 * materiales/generadores/minijefes_anim.py desde las mismas poses que las animaciones.
 *
 * Los puntos van en bloques y en el espacio del cuerpo: x hacia SU izquierda, y hacia
 * arriba desde los pies, z hacia delante (puntoMundo los pasa al mundo con su giro).
 * Las anclas son de los efectos del cliente: la pieza (su indice en la malla) y un punto
 * suyo en pixeles de la malla.
 */
public final class YiatzoGeometria {

    private YiatzoGeometria() {
    }

    /** Lo que mide el boceto en el mundo: el renderer escala la malla por esto (bloques por 16 pixeles). */
    public static final float ESCALA = 2.159F;

    public static final Vec3 CABEZA = new Vec3(0.000, 8.536, 0.435);
    public static final Vec3 PECHO = new Vec3(0.000, 6.747, 0.540);
    public static final Vec3 ORBE_SUELTA = new Vec3(1.717, 5.289, 9.474);
    public static final Vec3 ORBE_AREA = new Vec3(-0.132, 11.491, 4.447);
    public static final Vec3 ORBE_ALZADO = new Vec3(-1.612, 16.012, 5.672);

    public static final int DESPERTAR_ABRE = 20;
    public static final int DESPERTAR_SE_ALZA = 40;
    public static final int DESPERTAR_ALZADO = 68;
    public static final int DESPERTAR_RUGE = 88;
    public static final int DURACION_DESPERTAR = 130;
    public static final int DURACION_NORMAL = 28;
    public static final int NORMAL_CARGA = 8;
    public static final int NORMAL_SUELTA = 12;
    public static final int DURACION_AREA = 48;
    public static final int AREA_SUELTA = 22;
    public static final int DURACION_ESPECIAL = 120;
    public static final int ESPECIAL_FORMA = 20;
    public static final int ESPECIAL_ESTALLA = 94;
    public static final int DURACION_MUERTE = 110;
    public static final int MUERTE_CAE = 38;
    public static final int DISOLVER_DESDE = 50;
    public static final int PERIODO_ANDAR = 80;
    public static final float ZANCADA = 0.12F;

    /** baston */
    public static final int ORBE_PIEZA = 7;
    public static final float[] ORBE = {0F, -46F, 0F};
    /** capucha */
    public static final int OJOS_PIEZA = 2;
    public static final float[] OJOS = {0F, -6F, -2F};
    /** libro */
    public static final int LIBRO_PIEZA = 12;
    public static final float[] LIBRO = {0F, -3.75F, 0F};
    /** piedra0 */
    public static final int LOSA_0_PIEZA = 13;
    public static final float[] LOSA_0 = {0F, 0F, 0F};
    /** piedra1 */
    public static final int LOSA_1_PIEZA = 14;
    public static final float[] LOSA_1 = {0F, 0F, 0F};
    /** piedra2 */
    public static final int LOSA_2_PIEZA = 15;
    public static final float[] LOSA_2 = {0F, 0F, 0F};
    /** piedra3 */
    public static final int LOSA_3_PIEZA = 16;
    public static final float[] LOSA_3 = {0F, 0F, 0F};
    /** piedra4 */
    public static final int LOSA_4_PIEZA = 17;
    public static final float[] LOSA_4 = {0F, 0F, 0F};

    /** La base y la punta de baston en cada tick de NORMAL (bloques, en el cuerpo): su estela. */
    public static final float[][] TRAZO_NORMAL = {{-1.02F, 9.94F, 1.97F, -0.84F, 12.09F, 2.02F}, {-0.81F, 10.04F, 1.94F, -0.41F, 12.17F, 1.98F}, {-0.30F, 10.22F, 1.90F, 0.52F, 12.21F, 1.94F}, {0.18F, 10.26F, 1.90F, 1.35F, 12.07F, 1.98F}, {0.12F, 9.40F, 3.31F, 1.52F, 10.69F, 4.31F}, {-2.95F, 8.03F, 4.41F, -2.70F, 8.21F, 6.54F}, {-5.49F, 9.25F, 2.88F, -6.58F, 9.51F, 4.73F}, {-5.87F, 11.06F, 1.23F, -7.42F, 11.87F, 2.51F}, {-5.52F, 12.04F, 0.43F, -7.08F, 13.18F, 1.40F}, {-5.41F, 12.03F, 1.19F, -6.88F, 13.14F, 2.33F}, {-3.91F, 9.84F, 5.76F, -4.69F, 10.21F, 7.75F}, {-0.50F, 6.25F, 7.97F, -0.18F, 6.06F, 10.10F}, {2.60F, 5.43F, 7.67F, 3.43F, 5.01F, 9.62F}, {3.48F, 4.79F, 7.02F, 4.56F, 4.27F, 8.82F}, {3.84F, 4.40F, 6.61F, 5.02F, 3.81F, 8.31F}, {3.91F, 4.32F, 6.51F, 5.11F, 3.72F, 8.19F}, {3.82F, 4.39F, 6.56F, 5.01F, 3.80F, 8.27F}, {3.67F, 4.49F, 6.65F, 4.80F, 3.92F, 8.39F}, {3.49F, 4.60F, 6.75F, 4.58F, 4.04F, 8.53F}, {3.35F, 4.67F, 6.81F, 4.39F, 4.13F, 8.62F}, {3.30F, 4.68F, 6.83F, 4.33F, 4.13F, 8.65F}, {2.96F, 4.87F, 6.99F, 3.88F, 4.44F, 8.90F}, {2.05F, 5.55F, 7.27F, 2.65F, 5.47F, 9.34F}, {0.85F, 6.70F, 7.18F, 1.06F, 7.20F, 9.27F}, {-0.21F, 8.05F, 6.40F, -0.29F, 9.24F, 8.20F}, {-0.81F, 9.19F, 5.03F, -0.94F, 10.93F, 6.29F}, {-0.95F, 9.81F, 3.53F, -0.95F, 11.87F, 4.20F}, {-0.87F, 9.99F, 2.40F, -0.69F, 12.13F, 2.62F}, {-0.82F, 9.97F, 1.97F, -0.55F, 12.12F, 2.02F}};

    /** Cabeza en el despertar, cada 5 ticks (bloques; la camara de la presentacion la sigue). */
    public static final float[][] CABEZA_DESPERTAR = {{-0.04F, 6.97F, 1.43F}, {-0.06F, 6.98F, 1.44F}, {-0.07F, 7.01F, 1.43F}, {-0.08F, 7.04F, 1.40F}, {-0.09F, 7.05F, 1.37F}, {-0.09F, 7.08F, 1.30F}, {-0.08F, 7.13F, 1.15F}, {-0.07F, 7.18F, 1.00F}, {0.01F, 7.21F, 0.90F}, {0.14F, 7.52F, 0.84F}, {0.24F, 8.19F, 0.67F}, {0.26F, 8.96F, 0.41F}, {0.27F, 9.63F, 0.15F}, {0.27F, 10.04F, -0.04F}, {0.24F, 10.10F, -0.11F}, {0.21F, 10.19F, -0.34F}, {0.17F, 10.27F, -0.61F}, {0.15F, 8.99F, 1.11F}, {0.13F, 8.49F, 1.54F}, {0.10F, 8.31F, 1.67F}, {0.05F, 8.50F, 1.52F}, {0.00F, 8.80F, 1.33F}, {-0.05F, 8.99F, 1.25F}, {-0.10F, 8.98F, 1.14F}, {-0.16F, 8.87F, 0.86F}, {-0.21F, 8.72F, 0.58F}, {-0.25F, 8.68F, 0.48F}};
    /** Pecho en el despertar, cada 5 ticks (bloques; la camara de la presentacion la sigue). */
    public static final float[][] PECHO_DESPERTAR = {{0.00F, 5.39F, 0.99F}, {-0.01F, 5.38F, 1.00F}, {-0.02F, 5.38F, 1.01F}, {-0.03F, 5.38F, 1.01F}, {-0.04F, 5.38F, 1.00F}, {-0.04F, 5.40F, 0.96F}, {-0.04F, 5.43F, 0.88F}, {-0.04F, 5.46F, 0.80F}, {0.03F, 5.48F, 0.76F}, {0.14F, 5.78F, 0.76F}, {0.21F, 6.41F, 0.72F}, {0.22F, 7.15F, 0.62F}, {0.22F, 7.82F, 0.51F}, {0.20F, 8.23F, 0.42F}, {0.18F, 8.29F, 0.37F}, {0.15F, 8.40F, 0.23F}, {0.11F, 8.51F, 0.06F}, {0.07F, 7.21F, 0.87F}, {0.03F, 6.81F, 1.06F}, {0.00F, 6.69F, 1.11F}, {-0.04F, 6.85F, 1.04F}, {-0.08F, 7.11F, 0.96F}, {-0.11F, 7.28F, 0.94F}, {-0.15F, 7.26F, 0.90F}, {-0.18F, 7.11F, 0.78F}, {-0.21F, 6.95F, 0.65F}, {-0.22F, 6.90F, 0.62F}};

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
}
