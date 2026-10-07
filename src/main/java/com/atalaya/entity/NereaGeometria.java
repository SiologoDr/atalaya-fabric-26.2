package com.atalaya.entity;

import net.minecraft.world.phys.Vec3;

/**
 * Medidas de Nerea que comparten servidor y cliente. GENERADO por
 * materiales/generadores/nerea_juego_anim.py desde las mismas poses que las
 * animaciones (ya con la fisica): si una animacion cambia, estos puntos cambian.
 *
 * Los puntos van en bloques y en el espacio del cuerpo: x hacia SU izquierda,
 * y hacia arriba desde los pies, z hacia delante. NereaEntity los pasa al
 * mundo con el giro del cuerpo.
 */
public final class NereaGeometria {

    private NereaGeometria() {
    }

    public static final Vec3 OJO_IZQ = new Vec3(0.562, 11.694, 2.441);
    public static final Vec3 OJO_DER = new Vec3(-0.562, 11.694, 2.441);
    public static final Vec3 OJO_IZQ_MIRADA = new Vec3(0.604, 10.781, 3.470);
    public static final Vec3 OJO_DER_MIRADA = new Vec3(-0.521, 10.790, 3.470);
    public static final Vec3 CORAZON = new Vec3(0.000, 8.361, 1.392);
    public static final Vec3 CORAZON_BURBUJAS = new Vec3(0.000, 7.529, 2.273);
    public static final Vec3 CORAZON_AGOTADO = new Vec3(0.000, 5.636, 1.988);
    public static final Vec3 PECHO = new Vec3(0.000, 8.150, 1.927);
    public static final Vec3 BOCA = new Vec3(0.000, 10.486, 2.243);
    public static final Vec3 MANO_IZQ_LANZAR = new Vec3(1.511, 9.477, 6.640);
    public static final Vec3 MANO_IZQ_ESPERA = new Vec3(1.188, 7.072, 6.469);
    public static final Vec3 MANO_IZQ_REMOLINO = new Vec3(2.214, 12.030, 5.465);
    public static final Vec3 PUNTA_ROMPEOLAS = new Vec3(-0.165, -0.994, 18.581);
    public static final Vec3 PUNTA_ESTOCADA = new Vec3(-1.596, -2.771, 5.727);
    public static final Vec3 PUNTA_REMOLINO = new Vec3(-2.738, -0.837, 2.422);
    public static final Vec3 PUNTA_GEISER = new Vec3(-2.575, -0.968, 4.391);
    public static final Vec3 PUNTA_MAREA = new Vec3(-0.810, -2.222, 18.237);

    public static final int DURACION_DESPERTAR = 190;
    public static final int DESPERTAR_ABRE = 40;
    public static final int DESPERTAR_SE_ALZA = 70;
    public static final int DESPERTAR_ROMPE = 86;
    public static final int DESPERTAR_ALZADO = 120;
    public static final int DESPERTAR_RUGE = 145;
    public static final int DESPERTAR_PISA_DER = 109;
    public static final int DESPERTAR_PISA_IZQ = 119;
    public static final int DURACION_ROMPEOLAS = 21;
    public static final int IMPACTO_ROMPEOLAS = 10;
    public static final int DURACION_REMOLINO = 88;
    public static final int REMOLINO_TIRA = 20;
    public static final int REMOLINO_SUELTA = 80;
    public static final int DURACION_BURBUJAS = 22;
    public static final int BURBUJAS_SUELTA = 8;
    public static final int DURACION_MOLINO = 60;
    public static final int MOLINO_VISIBLE = 5;
    public static final int MOLINO_GOLPEA = 12;
    public static final int MOLINO_PARA = 48;
    public static final int DURACION_ARPON_LANZAR = 22;
    public static final int ARPON_SUELTA = 17;
    public static final int DURACION_ARPON_TIRAR = 22;
    public static final int ARPON_ARRASTRE = 8;
    public static final int ARPON_ESTOCADA = 12;
    public static final int DURACION_MIRADA = 102;
    public static final int MIRADA_FIJA = 12;
    public static final int DURACION_ATURDIDO = 70;
    public static final int DURACION_TAMBALEO = 60;
    public static final int DURACION_AGOTADO = 90;
    public static final int DURACION_LIBERACION = 200;
    public static final int LIBERACION_OJOS_ORO = 70;
    public static final int DURACION_GEISER = 32;
    public static final int GEISER_GOLPE = 11;
    public static final int DURACION_MAREA = 60;
    public static final int MAREA_LANZA = 40;
    public static final int DURACION_CANTO = 160;
    public static final int CANTO_EMPIEZA = 12;
    public static final int DURACION_MAREA_ALTA = 200;
    public static final int MAREA_ALTA_BURBUJAS = 12;
    public static final int MAREA_ALTA_ESTALLA = 180;
    public static final int DURACION_ENCADENAR = 28;
    public static final int ENCADENAR_SUELTA = 12;

    /** La mano izquierda (donde nace la cadena del gancho), tick a tick, en el espacio del cuerpo. */
    public static final float[][] MANO_ARPON_LANZAR = {{2.61F, 4.01F, 0.92F}, {2.88F, 8.74F, 5.50F}, {2.29F, 14.46F, 0.91F}, {1.85F, 14.58F, -0.10F}, {1.60F, 14.52F, 0.22F}, {1.52F, 14.34F, 1.00F}, {1.51F, 14.21F, 1.38F}, {1.60F, 14.29F, 1.17F}, {1.81F, 14.42F, 0.81F}, {2.02F, 14.52F, 0.41F}, {2.08F, 14.57F, 0.13F}, {1.85F, 14.57F, 0.00F}, {1.45F, 14.53F, -0.01F}, {1.13F, 14.46F, 0.04F}, {1.11F, 14.46F, -0.00F}, {1.42F, 14.57F, -0.52F}, {2.20F, 14.45F, 0.48F}, {0.83F, 7.74F, 7.16F}, {0.31F, 5.40F, 6.64F}, {0.48F, 5.40F, 6.49F}, {0.72F, 5.92F, 6.55F}, {0.99F, 6.57F, 6.61F}, {1.17F, 7.00F, 6.60F}};
    public static final float[][] MANO_ARPON_ESPERA = {{1.16F, 7.02F, 6.61F}, {1.17F, 7.01F, 6.60F}, {1.17F, 6.99F, 6.60F}, {1.17F, 6.97F, 6.59F}, {1.18F, 6.95F, 6.58F}, {1.19F, 6.92F, 6.57F}, {1.19F, 6.90F, 6.56F}, {1.20F, 6.88F, 6.55F}, {1.20F, 6.87F, 6.54F}, {1.20F, 6.86F, 6.54F}, {1.20F, 6.86F, 6.54F}, {1.20F, 6.86F, 6.54F}, {1.20F, 6.88F, 6.55F}, {1.19F, 6.89F, 6.55F}, {1.19F, 6.91F, 6.56F}, {1.18F, 6.94F, 6.57F}, {1.18F, 6.96F, 6.58F}, {1.17F, 6.98F, 6.59F}, {1.17F, 7.00F, 6.60F}, {1.17F, 7.01F, 6.60F}, {1.16F, 7.02F, 6.61F}};
    public static final float[][] MANO_ARPON_TIRAR = {{1.16F, 7.02F, 6.61F}, {1.30F, 5.51F, 4.69F}, {1.38F, 6.18F, 3.64F}, {1.31F, 6.57F, 3.17F}, {1.91F, 5.68F, 2.92F}, {2.86F, 5.03F, 2.55F}, {3.47F, 5.03F, 2.49F}, {3.91F, 5.45F, 2.70F}, {4.29F, 5.86F, 2.88F}, {4.40F, 5.50F, 3.02F}, {4.40F, 4.84F, 3.10F}, {4.43F, 4.16F, 3.02F}, {4.45F, 3.55F, 2.86F}, {4.49F, 3.16F, 2.73F}, {4.60F, 3.14F, 2.68F}, {4.53F, 3.30F, 2.55F}, {4.38F, 3.38F, 2.41F}, {4.16F, 3.50F, 2.19F}, {3.87F, 3.62F, 1.91F}, {3.52F, 3.73F, 1.61F}, {3.16F, 3.84F, 1.32F}, {2.84F, 3.94F, 1.09F}, {2.61F, 4.01F, 0.92F}};

    /** Donde esta la mano del gancho a los tantos ticks de un estado del arpon. */
    public static Vec3 manoArpon(float[][] tabla, float tick, boolean bucle) {
        int n = tabla.length - 1;
        float t = bucle ? tick % n : Math.max(0, Math.min(tick, n));
        int i = Math.min((int) t, n - 1);
        float k = t - i;
        float[] a = tabla[i];
        float[] b = tabla[i + 1];
        return new Vec3(a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k, a[2] + (b[2] - a[2]) * k);
    }

    /** El giro de la pelvis en el molino (grados que se suman al rumbo), por tramos lineales. */
    public static final float[] MOLINO_GIRO_T = {0F, 5F, 12F, 16F, 44F, 48F, 54F, 60F};
    public static final float[] MOLINO_GIRO_ANG = {0F, 0F, -25F, 12F, 630F, 686F, 712F, 720F};

    /** Grados de giro del molino a los tantos ticks de empezar. */
    public static float giroMolino(float tick) {
        float[] t = MOLINO_GIRO_T;
        float[] a = MOLINO_GIRO_ANG;
        if (tick <= t[0]) {
            return a[0];
        }
        for (int i = 1; i < t.length; i++) {
            if (tick <= t[i]) {
                float k = (tick - t[i - 1]) / (t[i] - t[i - 1]);
                return a[i - 1] + (a[i] - a[i - 1]) * k;
            }
        }
        return a[a.length - 1];
    }

    /** La cara (entre los ojos) en el despertar, cada 5 ticks (bloques; la camara de la presentacion lo sigue). */
    public static final float[][] CABEZA_DESPERTAR = {{0.00F, 7.26F, 4.38F}, {0.00F, 7.59F, 4.21F}, {0.00F, 7.89F, 4.05F}, {-0.01F, 7.51F, 4.28F}, {-0.02F, 6.81F, 4.57F}, {0.30F, 7.39F, 4.34F}, {0.02F, 7.28F, 4.40F}, {-0.01F, 8.11F, 3.97F}, {-0.01F, 8.47F, 3.91F}, {0.08F, 8.84F, 3.71F}, {0.16F, 9.10F, 3.48F}, {0.05F, 9.26F, 3.30F}, {-0.12F, 9.25F, 3.32F}, {-0.13F, 8.73F, 3.89F}, {-0.01F, 7.99F, 4.37F}, {-0.22F, 8.45F, 4.03F}, {-0.20F, 8.88F, 3.71F}, {-0.16F, 9.63F, 2.80F}, {0.01F, 10.51F, 0.28F}, {0.00F, 10.04F, 2.90F}, {0.00F, 8.08F, 5.83F}, {-0.00F, 9.12F, 5.26F}, {0.00F, 10.25F, 4.30F}, {-0.01F, 11.15F, 3.21F}, {0.13F, 11.87F, 2.00F}, {-0.26F, 12.12F, 1.33F}, {-0.29F, 12.26F, 0.77F}, {-0.20F, 12.30F, 0.55F}, {0.17F, 10.17F, 3.80F}, {0.00F, 12.02F, 0.63F}, {-0.16F, 12.12F, 0.39F}, {0.09F, 12.12F, 0.23F}, {0.24F, 12.12F, 0.15F}, {0.15F, 12.12F, 0.24F}, {-0.20F, 12.09F, 0.66F}, {-0.06F, 11.58F, 2.25F}, {0.01F, 10.99F, 3.18F}, {0.01F, 11.35F, 2.87F}, {0.00F, 11.69F, 2.44F}};

    /** El pecho en el despertar, cada 5 ticks (bloques; la camara de la presentacion lo sigue). */
    public static final float[][] PECHO_DESPERTAR = {{0.00F, 5.11F, 2.55F}, {0.00F, 5.30F, 2.48F}, {0.00F, 5.45F, 2.42F}, {-0.00F, 5.23F, 2.50F}, {-0.00F, 4.87F, 2.63F}, {0.06F, 5.13F, 2.53F}, {-0.00F, 5.12F, 2.55F}, {-0.00F, 5.57F, 2.38F}, {0.00F, 5.52F, 2.39F}, {0.00F, 5.53F, 2.38F}, {0.00F, 5.56F, 2.36F}, {0.00F, 5.61F, 2.33F}, {0.00F, 5.60F, 2.33F}, {-0.01F, 5.43F, 2.44F}, {0.00F, 5.26F, 2.55F}, {-0.12F, 5.53F, 2.43F}, {-0.11F, 5.75F, 2.34F}, {-0.09F, 6.16F, 2.02F}, {0.01F, 6.62F, 1.34F}, {0.00F, 6.12F, 2.40F}, {0.00F, 5.29F, 3.44F}, {0.00F, 6.04F, 3.27F}, {0.00F, 6.86F, 2.89F}, {-0.01F, 7.53F, 2.39F}, {0.19F, 8.13F, 1.84F}, {-0.19F, 8.29F, 1.62F}, {-0.35F, 8.39F, 1.46F}, {-0.16F, 8.43F, 1.44F}, {0.14F, 7.07F, 2.22F}, {0.00F, 8.46F, 1.32F}, {-0.07F, 8.44F, 1.35F}, {0.07F, 8.47F, 1.29F}, {0.14F, 8.49F, 1.25F}, {0.07F, 8.47F, 1.29F}, {-0.14F, 8.39F, 1.45F}, {-0.06F, 7.98F, 1.91F}, {0.00F, 7.69F, 2.15F}, {0.01F, 7.90F, 2.06F}, {0.00F, 8.15F, 1.93F}};

    /** Donde esta la cara a los tantos ticks del despertar. */
    public static Vec3 cabezaDespertar(float ticks) {
        return tabla(CABEZA_DESPERTAR, ticks / 5.0F);
    }

    /** Donde esta el pecho a los tantos ticks del despertar. */
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
