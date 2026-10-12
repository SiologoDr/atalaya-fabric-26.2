package com.atalaya.entity;

import net.minecraft.world.phys.Vec3;

/**
 * Medidas de Moctezuma, el Guerrero Aguila de Jade que comparten servidor y cliente. GENERADO por
 * materiales/generadores/minijefes_anim.py desde las mismas poses que las animaciones.
 *
 * Los puntos van en bloques y en el espacio del cuerpo: x hacia SU izquierda, y hacia
 * arriba desde los pies, z hacia delante (puntoMundo los pasa al mundo con su giro).
 * Las anclas son de los efectos del cliente: la pieza (su indice en la malla) y un punto
 * suyo en pixeles de la malla.
 */
public final class MoctezumaGeometria {

    private MoctezumaGeometria() {
    }

    /** Lo que mide el boceto en el mundo: el renderer escala la malla por esto (bloques por 16 pixeles). */
    public static final float ESCALA = 2.394F;

    public static final Vec3 CABEZA = new Vec3(0.000, 8.523, 0.395);
    public static final Vec3 PECHO = new Vec3(0.000, 6.135, 0.599);
    public static final Vec3 ARMA_BARRIDO = new Vec3(2.801, 5.522, 4.398);
    public static final Vec3 ARMA_TAJO = new Vec3(-1.172, 4.433, 8.183);
    public static final Vec3 GOLPE_AREA = new Vec3(2.153, 1.592, 3.411);
    public static final Vec3 PUNTA_ALZADA = new Vec3(-3.775, 13.664, -2.924);
    public static final Vec3 CLAVA = new Vec3(-1.632, 0.583, 6.024);

    public static final int DESPERTAR_ABRE = 20;
    public static final int DESPERTAR_SE_ALZA = 44;
    public static final int DESPERTAR_ALZADO = 72;
    public static final int DESPERTAR_RUGE = 98;
    public static final int DURACION_DESPERTAR = 140;
    public static final int DESPERTAR_ARRANCA = 58;
    public static final int DESPERTAR_CHOQUE_1 = 83;
    public static final int DESPERTAR_CHOQUE_2 = 92;
    public static final int DURACION_NORMAL = 34;
    public static final int NORMAL_CARGA = 7;
    public static final int NORMAL_GOLPE_1 = 10;
    public static final int NORMAL_GOLPE_2 = 20;
    public static final int DURACION_AREA = 46;
    public static final int AREA_DESPEGA = 10;
    public static final int AREA_CAE = 24;
    public static final int DURACION_ESPECIAL = 100;
    public static final int ESPECIAL_ALZA = 16;
    public static final int ESPECIAL_CLAVA = 74;
    public static final int ESPECIAL_LLUVIA_1 = 32;
    public static final int ESPECIAL_LLUVIA_2 = 44;
    public static final int ESPECIAL_LLUVIA_3 = 56;
    public static final int DURACION_MUERTE = 114;
    public static final int MUERTE_RODILLAS = 26;
    public static final int MUERTE_CAE = 48;
    public static final int DISOLVER_DESDE = 58;
    public static final int PERIODO_ANDAR = 24;
    public static final float ZANCADA = 0.173F;

    /** macuahuitl */
    public static final int HOJA_BASE_PIEZA = 23;
    public static final float[] HOJA_BASE = {0F, 4F, 0F};
    /** macuahuitl */
    public static final int HOJA_PUNTA_PIEZA = 23;
    public static final float[] HOJA_PUNTA = {0F, 31F, 0F};
    /** cabeza */
    public static final int OJOS_PIEZA = 10;
    public static final float[] OJOS = {0F, -6.16F, -4.4F};
    /** pelvis */
    public static final int GEMA_PIEZA = 1;
    public static final float[] GEMA = {0F, -1.5F, -6F};
    /** escudo */
    public static final int ESCUDO_PIEZA = 16;
    public static final float[] ESCUDO = {0F, 1.15F, 0F};

    /** La base y la punta de macuahuitl en cada tick de NORMAL (bloques, en el cuerpo): su estela. */
    public static final float[][] TRAZO_NORMAL = {{-1.96F, 5.03F, 2.55F, -1.39F, 8.28F, 5.13F}, {-3.43F, 5.17F, 1.52F, -2.44F, 7.14F, 5.08F}, {-4.14F, 5.77F, 0.34F, -3.88F, 6.43F, 4.47F}, {-4.20F, 6.46F, -0.57F, -5.05F, 6.28F, 3.53F}, {-3.96F, 7.02F, -1.12F, -5.75F, 6.45F, 2.63F}, {-3.68F, 7.39F, -1.37F, -6.07F, 6.70F, 1.99F}, {-3.48F, 7.57F, -1.47F, -6.19F, 6.88F, 1.65F}, {-3.95F, 4.85F, 1.16F, -3.67F, 5.51F, 5.29F}, {2.51F, 5.53F, 2.33F, 2.37F, 5.73F, 6.51F}, {2.77F, 5.82F, 2.18F, 2.81F, 5.27F, 6.33F}, {2.78F, 5.82F, 2.17F, 2.82F, 5.26F, 6.33F}, {2.92F, 5.82F, 1.98F, 3.25F, 5.26F, 6.12F}, {2.98F, 5.82F, 1.88F, 3.45F, 5.26F, 6.01F}, {2.87F, 5.62F, 1.92F, 3.41F, 5.75F, 6.07F}, {1.68F, 4.53F, 2.81F, 3.26F, 6.93F, 5.86F}, {-1.63F, 5.32F, 4.21F, 1.54F, 6.61F, 6.63F}, {-2.89F, 8.37F, 2.74F, -1.20F, 8.59F, 6.57F}, {-1.81F, 9.27F, 1.51F, -1.20F, 10.04F, 5.59F}, {-2.47F, 3.43F, 4.71F, -0.33F, 4.47F, 8.16F}, {-1.89F, 2.79F, 4.88F, -1.04F, 4.59F, 8.57F}, {-1.87F, 2.77F, 4.89F, -1.09F, 4.59F, 8.58F}, {-1.87F, 2.82F, 4.90F, -1.09F, 4.69F, 8.57F}, {-1.87F, 2.88F, 4.91F, -1.09F, 4.81F, 8.54F}, {-1.87F, 2.93F, 4.91F, -1.09F, 4.90F, 8.52F}, {-1.87F, 2.95F, 4.91F, -1.09F, 4.96F, 8.51F}, {-1.87F, 2.96F, 4.91F, -1.09F, 4.98F, 8.51F}, {-1.87F, 3.04F, 4.85F, -1.10F, 5.10F, 8.41F}, {-1.89F, 3.24F, 4.65F, -1.14F, 5.43F, 8.15F}, {-1.91F, 3.53F, 4.37F, -1.19F, 5.90F, 7.74F}, {-1.93F, 3.87F, 4.01F, -1.24F, 6.44F, 7.24F}, {-1.95F, 4.21F, 3.61F, -1.29F, 7.00F, 6.68F}, {-1.96F, 4.53F, 3.22F, -1.33F, 7.50F, 6.11F}, {-1.96F, 4.79F, 2.88F, -1.36F, 7.91F, 5.62F}, {-1.96F, 4.97F, 2.64F, -1.38F, 8.18F, 5.26F}, {-1.96F, 5.03F, 2.55F, -1.39F, 8.28F, 5.13F}};
    /** La base y la punta de macuahuitl en cada tick de AREA (bloques, en el cuerpo): su estela. */
    public static final float[][] TRAZO_AREA = {{-1.96F, 5.03F, 2.55F, -1.39F, 8.28F, 5.13F}, {-2.24F, 4.73F, 2.68F, -1.17F, 7.51F, 5.63F}, {-2.45F, 4.49F, 2.81F, -1.00F, 6.77F, 6.01F}, {-2.61F, 4.29F, 2.92F, -0.89F, 6.07F, 6.30F}, {-2.72F, 4.13F, 3.03F, -0.81F, 5.46F, 6.51F}, {-2.80F, 4.00F, 3.12F, -0.76F, 4.95F, 6.65F}, {-2.85F, 3.89F, 3.19F, -0.73F, 4.54F, 6.75F}, {-2.88F, 3.81F, 3.25F, -0.71F, 4.25F, 6.81F}, {-2.89F, 3.77F, 3.28F, -0.71F, 4.07F, 6.84F}, {-2.90F, 3.75F, 3.29F, -0.70F, 4.01F, 6.85F}, {-3.39F, 6.62F, 3.17F, -1.28F, 6.16F, 6.76F}, {-3.56F, 9.31F, 2.88F, -1.94F, 8.56F, 6.66F}, {-3.43F, 11.62F, 2.43F, -2.37F, 10.99F, 6.43F}, {-3.12F, 13.43F, 1.92F, -2.52F, 13.15F, 6.06F}, {-2.76F, 14.74F, 1.46F, -2.44F, 14.87F, 5.63F}, {-2.44F, 15.61F, 1.10F, -2.28F, 16.07F, 5.26F}, {-2.23F, 16.09F, 0.88F, -2.14F, 16.78F, 5.01F}, {-2.16F, 16.25F, 0.81F, -2.09F, 17.01F, 4.93F}, {-2.16F, 16.14F, 0.81F, -2.09F, 16.90F, 4.93F}, {-2.16F, 15.89F, 0.81F, -2.09F, 16.65F, 4.93F}, {-2.16F, 15.60F, 0.81F, -2.09F, 16.36F, 4.93F}, {-2.16F, 15.39F, 0.81F, -2.09F, 16.15F, 4.93F}, {-2.19F, 15.31F, 0.84F, -2.11F, 16.04F, 4.96F}, {-3.24F, 13.04F, 2.08F, -2.82F, 12.85F, 6.25F}, {-2.36F, 1.43F, 3.13F, -1.55F, 0.56F, 7.14F}, {-2.36F, 1.57F, 3.18F, -1.55F, 0.87F, 7.23F}, {-2.36F, 1.47F, 3.14F, -1.55F, 0.65F, 7.17F}, {-2.36F, 1.51F, 3.16F, -1.55F, 0.75F, 7.20F}, {-2.36F, 1.64F, 3.20F, -1.55F, 1.03F, 7.27F}, {-2.36F, 1.61F, 3.19F, -1.55F, 0.96F, 7.25F}, {-2.36F, 1.60F, 3.19F, -1.55F, 0.95F, 7.25F}, {-2.36F, 1.65F, 3.21F, -1.55F, 1.06F, 7.27F}, {-2.36F, 1.65F, 3.21F, -1.55F, 1.06F, 7.27F}, {-2.36F, 1.65F, 3.21F, -1.55F, 1.06F, 7.27F}, {-2.36F, 1.71F, 3.21F, -1.54F, 1.19F, 7.28F}, {-2.34F, 1.87F, 3.20F, -1.52F, 1.55F, 7.30F}, {-2.32F, 2.12F, 3.19F, -1.49F, 2.10F, 7.30F}, {-2.29F, 2.43F, 3.17F, -1.46F, 2.80F, 7.26F}, {-2.25F, 2.79F, 3.13F, -1.43F, 3.61F, 7.16F}, {-2.21F, 3.18F, 3.08F, -1.40F, 4.46F, 6.98F}, {-2.16F, 3.57F, 3.00F, -1.38F, 5.32F, 6.73F}, {-2.11F, 3.95F, 2.91F, -1.37F, 6.13F, 6.41F}, {-2.07F, 4.30F, 2.81F, -1.37F, 6.85F, 6.06F}, {-2.03F, 4.60F, 2.72F, -1.37F, 7.45F, 5.72F}, {-1.99F, 4.83F, 2.63F, -1.38F, 7.90F, 5.42F}, {-1.97F, 4.98F, 2.57F, -1.39F, 8.18F, 5.21F}, {-1.96F, 5.03F, 2.55F, -1.39F, 8.28F, 5.13F}};

    /** Cabeza en el despertar, cada 5 ticks (bloques; la camara de la presentacion la sigue). */
    public static final float[][] CABEZA_DESPERTAR = {{0.20F, 6.13F, 1.67F}, {0.20F, 6.16F, 1.66F}, {0.19F, 6.23F, 1.62F}, {0.19F, 6.30F, 1.58F}, {0.19F, 6.33F, 1.56F}, {0.18F, 6.39F, 1.49F}, {0.16F, 6.51F, 1.33F}, {0.14F, 6.63F, 1.12F}, {0.12F, 6.72F, 0.94F}, {0.11F, 6.87F, 0.93F}, {0.10F, 7.34F, 1.10F}, {0.09F, 7.58F, 1.19F}, {0.07F, 7.67F, 1.14F}, {-0.01F, 8.03F, 0.61F}, {0.03F, 8.32F, 0.07F}, {0.03F, 8.27F, 0.13F}, {0.03F, 8.08F, 0.62F}, {-0.02F, 8.16F, 0.41F}, {0.12F, 8.01F, 0.77F}, {0.02F, 8.14F, -0.29F}, {0.12F, 7.97F, -1.13F}, {0.12F, 7.96F, -1.16F}, {0.12F, 7.96F, -1.16F}, {0.12F, 7.97F, -1.14F}, {0.12F, 7.98F, -1.13F}, {0.09F, 8.09F, -0.92F}, {0.00F, 8.38F, 0.25F}, {0.00F, 8.46F, 0.34F}, {0.00F, 8.52F, 0.40F}};
    /** Pecho en el despertar, cada 5 ticks (bloques; la camara de la presentacion la sigue). */
    public static final float[][] PECHO_DESPERTAR = {{0.11F, 4.25F, 0.84F}, {0.11F, 4.25F, 0.84F}, {0.11F, 4.25F, 0.84F}, {0.11F, 4.25F, 0.84F}, {0.11F, 4.25F, 0.84F}, {0.11F, 4.27F, 0.82F}, {0.11F, 4.30F, 0.78F}, {0.10F, 4.33F, 0.73F}, {0.10F, 4.35F, 0.68F}, {0.09F, 4.47F, 0.71F}, {0.08F, 4.92F, 0.83F}, {0.07F, 5.16F, 0.90F}, {0.06F, 5.24F, 0.89F}, {-0.04F, 5.59F, 0.70F}, {-0.08F, 5.91F, 0.49F}, {-0.13F, 5.89F, 0.48F}, {0.05F, 5.71F, 0.67F}, {-0.07F, 5.78F, 0.59F}, {0.15F, 5.64F, 0.72F}, {-0.04F, 5.72F, 0.49F}, {-0.03F, 5.77F, 0.25F}, {-0.02F, 5.77F, 0.23F}, {-0.02F, 5.77F, 0.23F}, {-0.02F, 5.77F, 0.22F}, {-0.02F, 5.77F, 0.21F}, {-0.03F, 5.81F, 0.26F}, {-0.04F, 5.98F, 0.55F}, {-0.02F, 6.07F, 0.58F}, {0.00F, 6.13F, 0.60F}};

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
