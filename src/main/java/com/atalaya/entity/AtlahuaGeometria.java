package com.atalaya.entity;

import net.minecraft.world.phys.Vec3;

/**
 * Medidas de Atlahua, el Triton de las Profundidades que comparten servidor y cliente. GENERADO por
 * materiales/generadores/minijefes_anim.py desde las mismas poses que las animaciones.
 *
 * Los puntos van en bloques y en el espacio del cuerpo: x hacia SU izquierda, y hacia
 * arriba desde los pies, z hacia delante (puntoMundo los pasa al mundo con su giro).
 * Las anclas son de los efectos del cliente: la pieza (su indice en la malla) y un punto
 * suyo en pixeles de la malla.
 */
public final class AtlahuaGeometria {

    private AtlahuaGeometria() {
    }

    /** Lo que mide el boceto en el mundo: el renderer escala la malla por esto (bloques por 16 pixeles). */
    public static final float ESCALA = 2.155F;

    public static final Vec3 CABEZA = new Vec3(0.000, 7.747, 0.372);
    public static final Vec3 PECHO = new Vec3(0.000, 5.657, 0.673);
    public static final Vec3 PUNTA_ESTOCADA = new Vec3(3.890, 3.210, 9.822);
    public static final Vec3 PUNTA_GOLPE = new Vec3(-1.990, -4.588, 2.883);
    public static final Vec3 PUNTA_LANZA = new Vec3(-1.249, 1.039, 9.984);
    public static final Vec3 PUNTA_CLAVA = new Vec3(-3.759, 1.679, 2.509);

    public static final int DESPERTAR_ABRE = 20;
    public static final int DESPERTAR_SE_ALZA = 44;
    public static final int DESPERTAR_ALZADO = 70;
    public static final int DESPERTAR_RUGE = 96;
    public static final int DURACION_DESPERTAR = 140;
    public static final int DESPERTAR_CLAVA = 121;
    public static final int DURACION_NORMAL = 30;
    public static final int NORMAL_CARGA = 9;
    public static final int NORMAL_GOLPE = 12;
    public static final int DURACION_AREA = 48;
    public static final int AREA_GOLPE = 20;
    public static final int DURACION_ESPECIAL = 110;
    public static final int ESPECIAL_RUGE = 28;
    public static final int ESPECIAL_LANZA = 54;
    public static final int DURACION_MUERTE = 118;
    public static final int MUERTE_RODILLA = 28;
    public static final int MUERTE_CAE = 50;
    public static final int DISOLVER_DESDE = 62;
    public static final int PERIODO_ANDAR = 29;
    public static final float ZANCADA = 0.119F;

    /** tridente */
    public static final int PUNTAS_PIEZA = 20;
    public static final float[] PUNTAS = {0F, -44F, 0F};
    /** cabeza */
    public static final int OJOS_PIEZA = 10;
    public static final float[] OJOS = {0F, -5.52F, -4.6F};
    /** torso */
    public static final int SENUELO_PIEZA = 8;
    public static final float[] SENUELO = {0F, -12F, -8F};
    /** mandibula */
    public static final int BOCA_PIEZA = 11;
    public static final float[] BOCA = {0F, 0.92F, -4.6F};

    /** La base y la punta de tridente en cada tick de NORMAL (bloques, en el cuerpo): su estela. */
    public static final float[][] TRAZO_NORMAL = {{-1.43F, 7.18F, 1.72F, -1.03F, 9.98F, 1.72F}, {-1.94F, 6.25F, 2.72F, -1.28F, 8.41F, 4.42F}, {-3.20F, 5.00F, 2.78F, -3.20F, 6.01F, 5.43F}, {-4.58F, 4.10F, 1.81F, -5.66F, 4.09F, 4.42F}, {-5.55F, 3.74F, 0.23F, -7.55F, 3.13F, 2.14F}, {-5.93F, 3.80F, -1.42F, -8.47F, 2.99F, -0.46F}, {-5.87F, 4.07F, -2.78F, -8.59F, 3.29F, -2.69F}, {-5.62F, 4.37F, -3.73F, -8.31F, 3.69F, -4.27F}, {-5.37F, 4.58F, -4.27F, -7.99F, 3.99F, -5.17F}, {-5.28F, 4.65F, -4.44F, -7.86F, 4.10F, -5.46F}, {2.41F, 3.90F, 7.44F, 3.95F, 3.36F, 9.74F}, {2.42F, 3.73F, 7.64F, 3.96F, 3.14F, 9.93F}, {2.41F, 3.78F, 7.63F, 3.96F, 3.21F, 9.93F}, {2.41F, 3.89F, 7.62F, 3.96F, 3.36F, 9.92F}, {2.40F, 3.97F, 7.61F, 3.96F, 3.48F, 9.92F}, {2.39F, 4.03F, 7.60F, 3.95F, 3.57F, 9.91F}, {2.39F, 4.06F, 7.59F, 3.95F, 3.62F, 9.91F}, {2.39F, 4.08F, 7.59F, 3.95F, 3.63F, 9.91F}, {2.30F, 4.08F, 7.60F, 3.78F, 3.61F, 9.96F}, {2.02F, 4.11F, 7.61F, 3.26F, 3.58F, 10.09F}, {1.57F, 4.21F, 7.58F, 2.41F, 3.67F, 10.23F}, {0.95F, 4.43F, 7.45F, 1.25F, 4.05F, 10.24F}, {0.25F, 4.80F, 7.15F, -0.04F, 4.79F, 9.97F}, {-0.44F, 5.31F, 6.63F, -1.22F, 5.89F, 9.29F}, {-0.99F, 5.89F, 5.87F, -2.04F, 7.16F, 8.17F}, {-1.35F, 6.42F, 4.96F, -2.38F, 8.35F, 6.75F}, {-1.50F, 6.81F, 3.99F, -2.27F, 9.24F, 5.22F}, {-1.52F, 7.05F, 3.09F, -1.90F, 9.76F, 3.82F}, {-1.49F, 7.15F, 2.37F, -1.47F, 9.96F, 2.70F}, {-1.44F, 7.18F, 1.89F, -1.15F, 9.99F, 1.98F}, {-1.43F, 7.18F, 1.72F, -1.03F, 9.98F, 1.72F}};
    /** La base y la punta de tridente en cada tick de AREA (bloques, en el cuerpo): su estela. */
    public static final float[][] TRAZO_AREA = {{-1.43F, 7.18F, 1.72F, -1.03F, 9.98F, 1.72F}, {-1.03F, 6.81F, 2.20F, 0.83F, 8.87F, 2.75F}, {-1.07F, 6.41F, 2.60F, 1.41F, 7.24F, 3.68F}, {-1.35F, 6.26F, 2.91F, 0.99F, 6.02F, 4.47F}, {-1.64F, 6.40F, 3.11F, 0.19F, 5.48F, 5.07F}, {-1.79F, 6.69F, 3.22F, -0.55F, 5.49F, 5.46F}, {-1.80F, 6.99F, 3.26F, -1.03F, 5.75F, 5.69F}, {-1.63F, 7.24F, 3.26F, -1.14F, 6.08F, 5.79F}, {-1.17F, 7.21F, 3.13F, -0.69F, 6.04F, 5.66F}, {-1.13F, 6.70F, 2.86F, -0.68F, 5.30F, 5.27F}, {-1.81F, 6.55F, 2.83F, -1.69F, 5.07F, 5.24F}, {-1.99F, 7.24F, 3.14F, -1.95F, 6.10F, 5.73F}, {-1.21F, 7.40F, 3.07F, -0.80F, 6.36F, 5.66F}, {-1.20F, 6.76F, 2.68F, -0.79F, 5.43F, 5.14F}, {-1.90F, 6.77F, 2.67F, -1.82F, 5.47F, 5.18F}, {-2.05F, 7.34F, 2.85F, -2.03F, 6.33F, 5.49F}, {-1.77F, 7.66F, 2.88F, -1.62F, 6.82F, 5.58F}, {-1.62F, 7.73F, 2.85F, -1.40F, 6.93F, 5.56F}, {-1.64F, 7.73F, 2.87F, -1.41F, 6.95F, 5.58F}, {-2.68F, 7.30F, 4.04F, -2.18F, 6.95F, 6.80F}, {-1.86F, -1.95F, 2.37F, -2.00F, -4.72F, 2.91F}, {-1.86F, -1.85F, 2.53F, -2.00F, -4.60F, 3.18F}, {-1.86F, -1.95F, 2.37F, -2.00F, -4.72F, 2.90F}, {-1.86F, -1.84F, 2.55F, -2.00F, -4.59F, 3.21F}, {-1.86F, -1.81F, 2.61F, -2.00F, -4.55F, 3.30F}, {-1.86F, -1.86F, 2.53F, -2.00F, -4.61F, 3.16F}, {-1.86F, -1.78F, 2.65F, -2.00F, -4.52F, 3.36F}, {-1.86F, -1.78F, 2.65F, -2.00F, -4.51F, 3.36F}, {-1.86F, -1.79F, 2.64F, -2.00F, -4.52F, 3.35F}, {-1.86F, -1.77F, 2.66F, -2.00F, -4.50F, 3.39F}, {-1.86F, -1.77F, 2.66F, -2.00F, -4.50F, 3.39F}, {-1.86F, -1.73F, 2.74F, -1.99F, -4.44F, 3.54F}, {-1.86F, -1.59F, 2.97F, -1.99F, -4.23F, 3.97F}, {-1.86F, -1.33F, 3.32F, -1.97F, -3.85F, 4.61F}, {-1.85F, -0.95F, 3.74F, -1.95F, -3.24F, 5.39F}, {-1.83F, -0.41F, 4.19F, -1.91F, -2.37F, 6.22F}, {-1.80F, 0.29F, 4.60F, -1.85F, -1.22F, 6.99F}, {-1.77F, 1.14F, 4.91F, -1.77F, 0.18F, 7.58F}, {-1.72F, 2.08F, 5.08F, -1.67F, 1.77F, 7.89F}, {-1.67F, 3.07F, 5.06F, -1.56F, 3.43F, 7.87F}, {-1.62F, 4.03F, 4.86F, -1.44F, 5.04F, 7.50F}, {-1.56F, 4.91F, 4.50F, -1.34F, 6.50F, 6.82F}, {-1.52F, 5.65F, 4.01F, -1.24F, 7.71F, 5.93F}, {-1.48F, 6.23F, 3.46F, -1.16F, 8.63F, 4.93F}, {-1.46F, 6.64F, 2.92F, -1.10F, 9.26F, 3.93F}, {-1.44F, 6.92F, 2.44F, -1.07F, 9.66F, 3.03F}, {-1.43F, 7.08F, 2.05F, -1.05F, 9.87F, 2.33F}, {-1.43F, 7.16F, 1.81F, -1.04F, 9.96F, 1.88F}, {-1.43F, 7.18F, 1.72F, -1.03F, 9.98F, 1.72F}};

    /** Cabeza en el despertar, cada 5 ticks (bloques; la camara de la presentacion la sigue). */
    public static final float[][] CABEZA_DESPERTAR = {{0.00F, 5.42F, 1.58F}, {0.00F, 5.44F, 1.58F}, {0.00F, 5.48F, 1.56F}, {0.00F, 5.51F, 1.55F}, {0.00F, 5.53F, 1.54F}, {0.00F, 5.57F, 1.48F}, {0.00F, 5.66F, 1.36F}, {0.00F, 5.76F, 1.20F}, {0.00F, 5.82F, 1.06F}, {0.00F, 5.97F, 1.02F}, {0.00F, 6.46F, 1.00F}, {0.00F, 6.75F, 0.99F}, {0.00F, 6.85F, 0.99F}, {0.00F, 7.26F, 0.30F}, {0.00F, 7.53F, -0.39F}, {0.00F, 7.48F, -0.46F}, {0.00F, 7.35F, -0.60F}, {0.00F, 7.19F, -0.77F}, {0.00F, 7.07F, -0.88F}, {0.00F, 7.03F, -1.01F}, {0.00F, 7.02F, -1.05F}, {0.00F, 7.01F, -1.07F}, {0.00F, 7.02F, -1.05F}, {0.00F, 7.02F, -1.05F}, {0.00F, 7.08F, -0.01F}, {0.00F, 6.90F, 0.80F}, {0.00F, 6.94F, 0.56F}, {0.00F, 7.35F, 0.47F}, {0.00F, 7.75F, 0.37F}};
    /** Pecho en el despertar, cada 5 ticks (bloques; la camara de la presentacion la sigue). */
    public static final float[][] PECHO_DESPERTAR = {{0.00F, 3.69F, 1.08F}, {0.00F, 3.69F, 1.08F}, {0.00F, 3.69F, 1.08F}, {0.00F, 3.69F, 1.08F}, {0.00F, 3.69F, 1.08F}, {0.00F, 3.70F, 1.06F}, {0.00F, 3.73F, 1.02F}, {0.00F, 3.76F, 0.96F}, {0.00F, 3.79F, 0.92F}, {0.00F, 3.91F, 0.92F}, {0.00F, 4.35F, 0.95F}, {0.00F, 4.62F, 0.96F}, {0.00F, 4.71F, 0.97F}, {0.00F, 5.11F, 0.70F}, {0.00F, 5.46F, 0.42F}, {0.00F, 5.42F, 0.40F}, {0.00F, 5.32F, 0.35F}, {0.00F, 5.20F, 0.28F}, {0.00F, 5.11F, 0.24F}, {0.00F, 5.09F, 0.23F}, {0.00F, 5.09F, 0.23F}, {0.00F, 5.09F, 0.23F}, {0.00F, 5.09F, 0.23F}, {0.00F, 5.09F, 0.23F}, {0.00F, 4.93F, 0.62F}, {0.00F, 4.75F, 0.90F}, {0.00F, 4.80F, 0.79F}, {0.00F, 5.23F, 0.73F}, {0.00F, 5.66F, 0.67F}};

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
