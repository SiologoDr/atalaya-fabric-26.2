package com.atalaya.entity;

import net.minecraft.world.phys.Vec3;

/**
 * Medidas de Rajang que comparten servidor y cliente. GENERADO por
 * materiales/generadores/rajang_juego_anim.py desde las mismas poses que las
 * animaciones: si una animacion cambia, esto cambia.
 *
 * Los puntos van en bloques y en el espacio del cuerpo: x hacia SU izquierda,
 * y hacia arriba desde los pies, z hacia delante. RajangEntity los pasa al
 * mundo con el giro del cuerpo.
 */
public final class RajangGeometria {

    private RajangGeometria() {
    }

    public static final Vec3 CABEZA = new Vec3(0.000, 6.222, 7.536);
    public static final Vec3 BOCA = new Vec3(0.000, 5.195, 8.936);
    public static final Vec3 BOCA_RUGIDO = new Vec3(-0.018, 8.316, 9.033);
    public static final Vec3 BOCA_CATACLISMO = new Vec3(0.000, 15.229, 5.794);
    public static final Vec3 PECHO = new Vec3(0.000, 5.813, 3.906);
    public static final Vec3 LOMO = new Vec3(0.000, 8.251, 0.875);
    public static final Vec3 GRUPA = new Vec3(0.000, 6.251, -6.000);
    public static final Vec3 COSTILLAS = new Vec3(0.000, 6.251, -1.625);
    public static final Vec3 ZARPA_GARRA = new Vec3(2.148, 0.501, 6.248);
    public static final Vec3 ZARPA_CARGA = new Vec3(-3.392, 7.903, 6.366);
    public static final Vec3 ZARPA_RASCA = new Vec3(-1.920, -0.483, -0.597);
    public static final Vec3 ZARPA_IZQ_TERREMOTO = new Vec3(0.700, -0.869, 5.500);
    public static final Vec3 ZARPA_DER_TERREMOTO = new Vec3(-0.724, -0.769, 5.660);
    public static final Vec3 ZARPA_IZQ = new Vec3(1.375, 0.233, 2.207);
    public static final Vec3 ZARPA_DER = new Vec3(-1.375, 0.233, 2.207);
    public static final Vec3 PATA_IZQ = new Vec3(1.375, 0.126, -5.723);
    public static final Vec3 PATA_DER = new Vec3(-1.375, 0.126, -5.723);
    public static final Vec3 PUNTA_COLA = new Vec3(0.000, 7.332, -17.149);
    public static final Vec3 MANOS_DESPERTAR = new Vec3(0.000, 0.236, 4.811);

    public static final int DURACION_DESPERTAR = 190;
    public static final int DESPERTAR_ABRE = 40;
    public static final int DESPERTAR_SE_ALZA = 70;
    public static final int DESPERTAR_ALZADO = 120;
    public static final int DESPERTAR_RUGE = 145;
    public static final int DESPERTAR_APOYA = 174;
    public static final int DURACION_GARRA = 21;
    public static final int GARRA_ALZA = 2;
    public static final int GARRA_GOLPE = 8;
    public static final int DURACION_TERREMOTO = 38;
    public static final int TERREMOTO_GOLPE = 16;
    public static final int DURACION_RUGIDO = 40;
    public static final int RUGIDO_RUGE = 10;
    public static final int DURACION_CATACLISMO = 52;
    public static final int CATACLISMO_RUGE = 26;
    public static final int DURACION_CATACLISMO_BAJA = 26;
    public static final int CATACLISMO_BAJA_GOLPE = 11;
    public static final int DURACION_ATURDIDO = 120;
    public static final int ATURDIDO_CAE = 16;
    public static final int DURACION_PARALIZADO = 200;
    public static final int DURACION_SALTO = 36;
    public static final int SALTO_DESPEGA = 7;
    public static final int SALTO_ATERRIZA = 24;
    public static final int DURACION_TAMBALEO = 50;
    public static final int TAMBALEO_RUGE = 22;
    public static final int DURACION_LIBERACION = 200;
    public static final int LIBERACION_OJOS_ORO = 80;
    public static final int PERIODO_ANDAR = 26;
    public static final int PERIODO_CORRER = 16;
    public static final int DURACION_EMBESTIDA_AVISO = 24;
    public static final int EMBESTIDA_RASCA_1 = 8;
    public static final int EMBESTIDA_RASCA_2 = 14;
    public static final int DURACION_EMBESTIDA_FRENA = 34;
    public static final int EMBESTIDA_FRENA_PARA = 14;
    public static final int DURACION_ESTAMPADO = 40;
    public static final int DURACION_TUMBA = 142;
    public static final int TUMBA_ESTALLA = 120;
    public static final int TUMBA_RUGE_2 = 69;

    public static final float ZANCADA_ANDAR = 0.176F;
    public static final float ZANCADA_CORRER = 1.039F;

    /** Cabeza en el despertar, cada 5 ticks (bloques; la camara de la presentacion la sigue). */
    public static final float[][] CABEZA_DESPERTAR = {{0.00F, 4.90F, 7.18F}, {0.00F, 4.84F, 7.19F}, {0.00F, 4.77F, 7.21F}, {0.00F, 4.68F, 7.22F}, {0.00F, 4.62F, 7.23F}, {0.00F, 4.61F, 7.23F}, {-0.06F, 4.70F, 7.19F}, {-0.23F, 4.90F, 7.13F}, {-0.14F, 5.13F, 7.07F}, {-0.06F, 6.42F, 6.66F}, {0.00F, 6.21F, 6.81F}, {-0.82F, 6.03F, 6.75F}, {-0.77F, 5.83F, 6.82F}, {-0.25F, 5.58F, 7.02F}, {0.36F, 4.83F, 7.29F}, {0.20F, 4.37F, 7.36F}, {0.05F, 3.80F, 7.27F}, {0.00F, 3.33F, 6.98F}, {0.00F, 3.39F, 6.47F}, {0.00F, 3.54F, 6.45F}, {0.00F, 4.28F, 7.19F}, {0.00F, 6.65F, 8.61F}, {0.00F, 6.14F, 8.90F}, {0.00F, 4.24F, 8.13F}, {0.00F, 3.63F, 6.57F}, {-0.35F, 2.74F, 6.78F}, {-0.31F, 2.93F, 6.88F}, {0.44F, 3.19F, 6.93F}, {0.11F, 1.60F, 6.35F}, {0.00F, 12.58F, 5.77F}, {-0.01F, 13.37F, 5.35F}, {0.02F, 13.25F, 5.45F}, {-0.01F, 12.74F, 5.72F}, {0.00F, 11.73F, 6.16F}, {0.00F, 7.68F, 7.35F}, {0.00F, 4.34F, 7.45F}, {-0.20F, 6.34F, 7.57F}, {0.06F, 6.25F, 7.55F}, {0.00F, 6.22F, 7.54F}};
    /** Pecho en el despertar, cada 5 ticks (bloques; la camara de la presentacion la sigue). */
    public static final float[][] PECHO_DESPERTAR = {{0.00F, 2.45F, 3.91F}, {0.00F, 2.41F, 3.91F}, {0.00F, 2.35F, 3.91F}, {0.00F, 2.28F, 3.91F}, {0.00F, 2.24F, 3.91F}, {0.00F, 2.22F, 3.91F}, {0.00F, 2.28F, 3.91F}, {0.00F, 2.42F, 3.91F}, {0.00F, 2.59F, 3.91F}, {0.00F, 2.71F, 3.91F}, {0.00F, 2.73F, 3.91F}, {0.00F, 2.63F, 3.91F}, {0.00F, 2.46F, 3.91F}, {0.00F, 2.29F, 3.91F}, {0.00F, 2.12F, 3.91F}, {0.00F, 2.33F, 3.77F}, {0.00F, 2.22F, 3.56F}, {0.00F, 1.77F, 3.19F}, {0.00F, 1.47F, 2.83F}, {0.00F, 1.59F, 2.84F}, {0.00F, 2.71F, 3.48F}, {0.00F, 5.42F, 5.00F}, {0.00F, 5.58F, 5.26F}, {0.00F, 5.47F, 5.02F}, {0.00F, 5.42F, 3.86F}, {0.00F, 3.85F, 3.59F}, {0.05F, 3.80F, 3.58F}, {0.00F, 3.96F, 3.59F}, {0.00F, 3.18F, 3.42F}, {0.00F, 10.22F, 2.82F}, {-0.02F, 10.68F, 2.64F}, {0.04F, 10.66F, 2.65F}, {-0.02F, 10.41F, 2.75F}, {-0.01F, 9.89F, 2.95F}, {0.00F, 6.92F, 3.79F}, {0.00F, 4.92F, 3.99F}, {0.00F, 5.96F, 4.00F}, {0.00F, 5.84F, 3.94F}, {0.00F, 5.81F, 3.91F}};

    /** Donde esta la cabeza a los tantos ticks del despertar (entre filas, en linea recta). */
    public static Vec3 cabezaDespertar(float ticks) {
        return tabla(CABEZA_DESPERTAR, ticks / 5.0F);
    }

    /** Donde esta el pecho a los tantos ticks del despertar (entre filas, en linea recta). */
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
