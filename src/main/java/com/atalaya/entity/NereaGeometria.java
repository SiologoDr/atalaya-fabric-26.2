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

    public static final Vec3 OJO_IZQ = new Vec3(0.375, 7.796, 1.627);
    public static final Vec3 OJO_DER = new Vec3(-0.375, 7.796, 1.627);
    public static final Vec3 OJO_IZQ_MIRADA = new Vec3(0.403, 7.187, 2.313);
    public static final Vec3 OJO_DER_MIRADA = new Vec3(-0.347, 7.194, 2.313);
    public static final Vec3 CORAZON = new Vec3(0.000, 5.574, 0.928);
    public static final Vec3 CORAZON_BURBUJAS = new Vec3(0.000, 5.019, 1.515);
    public static final Vec3 CORAZON_AGOTADO = new Vec3(0.000, 3.757, 1.325);
    public static final Vec3 PECHO = new Vec3(0.000, 5.433, 1.285);
    public static final Vec3 BOCA = new Vec3(0.000, 6.991, 1.496);
    public static final Vec3 MANO_IZQ_LANZAR = new Vec3(1.008, 6.318, 4.427);
    public static final Vec3 MANO_IZQ_ESPERA = new Vec3(0.792, 4.715, 4.313);
    public static final Vec3 MANO_IZQ_REMOLINO = new Vec3(1.476, 8.020, 3.643);
    public static final Vec3 PUNTA_ROMPEOLAS = new Vec3(-0.343, 0.152, 10.576);
    public static final Vec3 PUNTA_ESTOCADA = new Vec3(-1.064, 0.153, 3.817);
    public static final Vec3 PUNTA_REMOLINO = new Vec3(-1.826, -0.158, 1.615);

    public static final int DURACION_DESPERTAR = 64;
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

    /** La mano izquierda (donde nace la cadena del gancho), tick a tick, en el espacio del cuerpo. */
    public static final float[][] MANO_ARPON_LANZAR = {{1.74F, 2.68F, 0.61F}, {1.92F, 5.83F, 3.67F}, {1.52F, 9.64F, 0.61F}, {1.23F, 9.72F, -0.07F}, {1.07F, 9.68F, 0.15F}, {1.01F, 9.56F, 0.67F}, {1.01F, 9.47F, 0.92F}, {1.06F, 9.52F, 0.78F}, {1.21F, 9.61F, 0.54F}, {1.34F, 9.68F, 0.27F}, {1.39F, 9.71F, 0.08F}, {1.23F, 9.71F, 0.00F}, {0.97F, 9.68F, -0.01F}, {0.75F, 9.64F, 0.03F}, {0.74F, 9.64F, -0.00F}, {0.94F, 9.71F, -0.35F}, {1.47F, 9.63F, 0.32F}, {0.55F, 5.16F, 4.78F}, {0.21F, 3.60F, 4.43F}, {0.32F, 3.60F, 4.32F}, {0.48F, 3.94F, 4.37F}, {0.66F, 4.38F, 4.41F}, {0.78F, 4.67F, 4.40F}};
    public static final float[][] MANO_ARPON_ESPERA = {{0.78F, 4.68F, 4.41F}, {0.78F, 4.67F, 4.40F}, {0.78F, 4.66F, 4.40F}, {0.78F, 4.65F, 4.39F}, {0.79F, 4.63F, 4.38F}, {0.79F, 4.62F, 4.38F}, {0.79F, 4.60F, 4.37F}, {0.80F, 4.59F, 4.37F}, {0.80F, 4.58F, 4.36F}, {0.80F, 4.57F, 4.36F}, {0.80F, 4.57F, 4.36F}, {0.80F, 4.58F, 4.36F}, {0.80F, 4.59F, 4.36F}, {0.80F, 4.60F, 4.37F}, {0.79F, 4.61F, 4.37F}, {0.79F, 4.62F, 4.38F}, {0.79F, 4.64F, 4.39F}, {0.78F, 4.65F, 4.39F}, {0.78F, 4.66F, 4.40F}, {0.78F, 4.67F, 4.40F}, {0.78F, 4.68F, 4.41F}};
    public static final float[][] MANO_ARPON_TIRAR = {{0.78F, 4.68F, 4.40F}, {0.87F, 3.67F, 3.12F}, {0.92F, 4.12F, 2.43F}, {0.87F, 4.38F, 2.11F}, {1.27F, 3.79F, 1.95F}, {1.91F, 3.35F, 1.70F}, {2.31F, 3.36F, 1.66F}, {2.61F, 3.64F, 1.80F}, {2.86F, 3.91F, 1.92F}, {2.93F, 3.66F, 2.01F}, {2.94F, 3.22F, 2.07F}, {2.95F, 2.77F, 2.01F}, {2.97F, 2.36F, 1.91F}, {2.99F, 2.10F, 1.82F}, {3.07F, 2.09F, 1.79F}, {3.02F, 2.20F, 1.70F}, {2.92F, 2.26F, 1.61F}, {2.77F, 2.33F, 1.46F}, {2.58F, 2.41F, 1.27F}, {2.35F, 2.49F, 1.07F}, {2.11F, 2.56F, 0.88F}, {1.89F, 2.63F, 0.72F}, {1.74F, 2.68F, 0.61F}};

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
}
