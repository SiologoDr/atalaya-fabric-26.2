package com.atalaya.entity;

import net.minecraft.world.phys.Vec3;

/**
 * Medidas de Xiuhquetzal, el Fenix de Llamas que comparten servidor y cliente. GENERADO por
 * materiales/generadores/minijefes_anim.py desde las mismas poses que las animaciones.
 *
 * Los puntos van en bloques y en el espacio del cuerpo: x hacia SU izquierda, y hacia
 * arriba desde los pies, z hacia delante (puntoMundo los pasa al mundo con su giro).
 * Las anclas son de los efectos del cliente: la pieza (su indice en la malla) y un punto
 * suyo en pixeles de la malla.
 */
public final class XiuhquetzalGeometria {

    private XiuhquetzalGeometria() {
    }

    /** Lo que mide el boceto en el mundo: el renderer escala la malla por esto (bloques por 16 pixeles). */
    public static final float ESCALA = 2F;

    public static final Vec3 CABEZA = new Vec3(0.000, 5.600, 2.494);
    public static final Vec3 PECHO = new Vec3(0.000, 2.788, 1.254);
    public static final Vec3 PICO_GOLPE = new Vec3(0.000, 0.920, 4.085);
    public static final Vec3 PICO = new Vec3(0.000, 4.656, 3.888);
    public static final Vec3 ALA_IZQ = new Vec3(8.717, 3.578, -2.122);
    public static final Vec3 ALA_DER = new Vec3(-8.717, 3.578, -2.122);
    public static final Vec3 GARRAS = new Vec3(0.450, 0.069, -0.760);

    public static final int DESPERTAR_ABRE = 28;
    public static final int DESPERTAR_SE_ALZA = 40;
    public static final int DESPERTAR_ALZADO = 68;
    public static final int DESPERTAR_RUGE = 86;
    public static final int DURACION_DESPERTAR = 130;
    public static final int DURACION_NORMAL = 32;
    public static final int NORMAL_CARGA = 8;
    public static final int NORMAL_GOLPE = 14;
    public static final int DURACION_AREA = 52;
    public static final int AREA_BATIDA_1 = 16;
    public static final int AREA_BATIDA_2 = 26;
    public static final int AREA_BATIDA_3 = 36;
    public static final int DURACION_ESPECIAL = 110;
    public static final int ESPECIAL_ENVUELVE = 24;
    public static final int ESPECIAL_ESTALLA = 56;
    public static final int ESPECIAL_FIN = 84;
    public static final int DURACION_MUERTE = 122;
    public static final int MUERTE_SUELO = 38;
    public static final int DISOLVER_DESDE = 58;
    public static final int PERIODO_ANDAR = 18;
    public static final int PERIODO_BATIDA = 30;
    public static final float ZANCADA = 0.2F;

    /** cuerpo */
    public static final int PECHO_BRASA_PIEZA = 1;
    public static final float[] PECHO_BRASA = {0F, -8F, -6F};
    /** cabeza */
    public static final int OJOS_PIEZA = 16;
    public static final float[] OJOS = {0F, -4.55F, -3.25F};
    /** pico */
    public static final int PUNTA_PICO_PIEZA = 17;
    public static final float[] PUNTA_PICO = {0F, 3.9F, -7.8F};
    /** mano_ala_izq */
    public static final int PUNTA_ALA_IZQ_PIEZA = 10;
    public static final float[] PUNTA_ALA_IZQ = {44F, 0F, 24F};
    /** mano_ala_der */
    public static final int PUNTA_ALA_DER_PIEZA = 12;
    public static final float[] PUNTA_ALA_DER = {-44F, 0F, 24F};
    /** cola3 */
    public static final int COLA_PUNTA_PIEZA = 22;
    public static final float[] COLA_PUNTA = {0F, 22F, 0F};
    /** cresta */
    public static final int CRESTA_PIEZA = 19;
    public static final float[] CRESTA = {0F, -18.2F, 7.8F};

    /** La base y la punta de pico en cada tick de NORMAL (bloques, en el cuerpo): su estela. */
    public static final float[][] TRAZO_NORMAL = {{0.00F, 5.27F, 3.35F, 0.00F, 4.62F, 4.05F}, {0.00F, 5.83F, 3.06F, 0.00F, 5.19F, 3.76F}, {0.00F, 6.03F, 2.94F, 0.00F, 5.38F, 3.64F}, {0.00F, 6.07F, 2.91F, 0.00F, 5.43F, 3.61F}, {0.00F, 6.08F, 2.91F, 0.00F, 5.43F, 3.61F}, {0.00F, 6.51F, 2.10F, 0.00F, 5.94F, 2.86F}, {0.00F, 6.65F, 1.41F, 0.00F, 6.15F, 2.22F}, {0.00F, 6.65F, 0.94F, 0.00F, 6.20F, 1.77F}, {0.00F, 6.63F, 0.72F, 0.00F, 6.19F, 1.56F}, {0.00F, 6.58F, 0.96F, 0.00F, 6.11F, 1.79F}, {0.00F, 5.93F, 2.51F, 0.00F, 5.26F, 3.18F}, {0.00F, 3.19F, 4.31F, 0.00F, 2.28F, 4.55F}, {0.00F, 2.13F, 4.40F, 0.00F, 1.18F, 4.47F}, {0.00F, 1.34F, 4.34F, 0.00F, 0.40F, 4.19F}, {0.00F, 0.02F, 3.89F, 0.00F, -0.78F, 3.38F}, {0.00F, 4.23F, 3.91F, 0.00F, 3.32F, 4.19F}, {0.00F, 6.56F, 1.71F, 0.00F, 6.06F, 2.52F}, {0.00F, 6.77F, 1.23F, 0.00F, 6.37F, 2.09F}, {0.00F, 6.77F, 1.22F, 0.00F, 6.37F, 2.08F}, {0.00F, 6.77F, 1.22F, 0.00F, 6.37F, 2.08F}, {0.00F, 6.77F, 1.22F, 0.00F, 6.37F, 2.08F}, {0.00F, 6.77F, 1.22F, 0.00F, 6.37F, 2.08F}, {0.00F, 6.74F, 1.30F, 0.00F, 6.33F, 2.16F}, {0.00F, 6.57F, 1.68F, 0.00F, 6.12F, 2.52F}, {0.00F, 6.34F, 2.18F, 0.00F, 5.84F, 2.98F}, {0.00F, 6.24F, 2.50F, 0.00F, 5.71F, 3.29F}, {0.00F, 6.29F, 2.62F, 0.00F, 5.74F, 3.40F}, {0.00F, 6.23F, 2.76F, 0.00F, 5.67F, 3.52F}, {0.00F, 6.02F, 2.93F, 0.00F, 5.44F, 3.68F}, {0.00F, 5.71F, 3.11F, 0.00F, 5.10F, 3.83F}, {0.00F, 5.37F, 3.26F, 0.00F, 4.74F, 3.97F}, {0.00F, 5.16F, 3.36F, 0.00F, 4.50F, 4.05F}, {0.00F, 5.03F, 3.41F, 0.00F, 4.37F, 4.09F}};

    /** Cabeza en el despertar, cada 5 ticks (bloques; la camara de la presentacion la sigue). */
    public static final float[][] CABEZA_DESPERTAR = {{0.00F, 3.81F, 2.52F}, {0.00F, 3.84F, 2.52F}, {0.00F, 3.92F, 2.51F}, {0.00F, 4.03F, 2.50F}, {0.00F, 4.13F, 2.47F}, {0.00F, 4.20F, 2.45F}, {0.04F, 4.14F, 2.53F}, {0.02F, 4.13F, 2.59F}, {0.00F, 6.61F, -0.19F}, {0.00F, 6.67F, -0.25F}, {0.00F, 6.93F, 0.23F}, {0.00F, 6.30F, 1.19F}, {0.00F, 6.25F, 1.73F}, {0.00F, 6.28F, 2.03F}, {0.00F, 5.85F, 2.23F}, {0.00F, 6.20F, 2.27F}, {0.00F, 6.03F, 2.42F}, {0.00F, 5.91F, 1.14F}, {0.00F, 5.77F, 1.12F}, {0.00F, 5.92F, 1.07F}, {0.00F, 6.30F, 0.96F}, {0.00F, 6.35F, 0.95F}, {0.00F, 5.97F, 1.12F}, {0.00F, 5.75F, 1.50F}, {0.00F, 5.72F, 1.95F}, {0.00F, 5.92F, 2.26F}, {0.00F, 6.01F, 2.39F}};
    /** Pecho en el despertar, cada 5 ticks (bloques; la camara de la presentacion la sigue). */
    public static final float[][] PECHO_DESPERTAR = {{0.00F, 2.45F, 0.70F}, {0.00F, 2.45F, 0.70F}, {0.00F, 2.45F, 0.70F}, {0.00F, 2.45F, 0.70F}, {0.00F, 2.45F, 0.70F}, {0.00F, 2.45F, 0.70F}, {0.01F, 2.43F, 0.74F}, {0.01F, 2.41F, 0.76F}, {0.00F, 3.71F, 0.27F}, {0.00F, 3.76F, 0.28F}, {0.00F, 3.93F, 0.50F}, {0.00F, 3.25F, 0.86F}, {0.00F, 3.24F, 1.06F}, {0.00F, 3.32F, 1.15F}, {0.00F, 2.95F, 1.19F}, {0.00F, 3.34F, 1.17F}, {0.00F, 3.25F, 1.17F}, {0.00F, 2.96F, 1.16F}, {0.00F, 2.83F, 1.16F}, {0.00F, 2.98F, 1.15F}, {0.00F, 3.36F, 1.13F}, {0.00F, 3.40F, 1.13F}, {0.00F, 3.01F, 1.16F}, {0.00F, 2.77F, 1.19F}, {0.00F, 2.76F, 1.22F}, {0.00F, 3.02F, 1.24F}, {0.00F, 3.15F, 1.24F}};

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
