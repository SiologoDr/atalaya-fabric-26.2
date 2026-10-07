package com.atalaya.entity;

import net.minecraft.world.phys.Vec3;

/**
 * Medidas de Aeralis que comparten servidor y cliente. GENERADO
 * por materiales/generadores/vendaval_juego_anim.py desde las mismas poses que
 * las animaciones (ya con la fisica): si una animacion cambia, esto cambia.
 *
 * Los puntos van en bloques y en el espacio del cuerpo: x hacia SU izquierda,
 * y hacia arriba desde la base de la caja, z hacia delante. AeralisEntity los
 * pasa al mundo con el giro del cuerpo.
 */
public final class AeralisGeometria {

    private AeralisGeometria() {
    }

    public static final Vec3 NUCLEO = new Vec3(0.000, 7.497, 1.336);
    public static final Vec3 CABEZA = new Vec3(0.000, 10.402, 0.802);
    public static final Vec3 OJO_IZQ = new Vec3(0.750, 10.569, 1.008);
    public static final Vec3 OJO_DER = new Vec3(-0.750, 10.569, 1.008);
    public static final Vec3 BOCA = new Vec3(0.000, 9.866, 1.122);
    public static final Vec3 BOCA_MARCA = new Vec3(0.000, 9.274, 2.040);
    public static final Vec3 NUCLEO_JUICIO = new Vec3(0.000, 6.418, 1.840);
    public static final Vec3 NUCLEO_TORNADOS = new Vec3(0.000, 5.853, 1.146);
    public static final Vec3 PUNTA_ALA_IZQ_ALETEO = new Vec3(2.692, 5.710, 20.257);
    public static final Vec3 PUNTA_ALA_DER_ALETEO = new Vec3(-17.815, 7.628, 9.785);
    public static final Vec3 PUNTA_ALA_IZQ = new Vec3(19.187, 14.721, -5.852);
    public static final Vec3 PUNTA_ALA_DER = new Vec3(-19.187, 14.721, -5.852);
    public static final Vec3 NUCLEO_PICADO = new Vec3(0.000, 6.483, 0.492);
    public static final Vec3 CABEZA_PICADO = new Vec3(0.000, 8.981, 2.663);
    public static final Vec3 NUCLEO_POSADA = new Vec3(0.000, 4.521, 1.313);
    public static final Vec3 NUCLEO_ESCAMAS = new Vec3(0.000, 8.827, 1.358);
    public static final Vec3 PUNTA_ABDOMEN = new Vec3(0.000, 1.223, -1.429);

    public static final int DURACION_DESPERTAR = 190;
    public static final int DESPERTAR_ALZA = 100;
    public static final int DESPERTAR_CHILLA = 145;
    public static final int DESPERTAR_ABRE = 40;
    public static final int DESPERTAR_SE_ALZA = 70;
    public static final int DESPERTAR_ALZADO = 120;
    public static final int DESPERTAR_RUGE = 145;
    public static final int DURACION_ALETEO = 30;
    public static final int ALETEO_CARGA = 2;
    public static final int ALETEO_SUELTA = 14;
    public static final int DURACION_TORNADOS = 38;
    public static final int TORNADOS_GOLPE = 15;
    public static final int DURACION_MARCA = 28;
    public static final int MARCA_FIJA = 12;
    public static final int DURACION_RAFAGA = 15;
    public static final int RAFAGA_SUELTA = 7;
    public static final int DURACION_DOBLE_RAFAGA = 22;
    public static final int DOBLE_SUELTA_1 = 6;
    public static final int DOBLE_SUELTA_2 = 14;
    public static final int DURACION_JUICIO_SUBE = 64;
    public static final int DURACION_JUICIO_GOLPE = 34;
    public static final int JUICIO_GOLPE = 14;
    public static final int DURACION_ATURDIDA = 100;
    public static final int DURACION_AGOTADA = 100;
    public static final int AGOTADA_CAE = 6;
    public static final int AGOTADA_ALZA = 78;
    public static final int DURACION_TAMBALEO = 52;
    public static final int DURACION_LIBERACION = 200;
    public static final int LIBERACION_OJOS_ORO = 70;
    public static final int PERIODO_VUELO = 22;
    public static final int VUELO_GOLPE = 1;
    public static final int DURACION_PICADO_AVISO = 28;
    public static final int PERIODO_PICADO = 10;
    public static final int DURACION_POSADA = 68;
    public static final int POSADA_CHOQUE = 2;
    public static final int POSADA_ALZA = 59;
    public static final int DURACION_ESCAMAS = 52;
    public static final int ESCAMAS_SUELTA = 18;
    public static final int ESCAMAS_ACABA = 44;

    /** Los golpes de alas del despertar (ticks): el primero la despega; los dos ultimos suenan en despertar.ogg. */
    public static final int[] DESPERTAR_BATIDAS = {103, 115, 128, 138};

    /** Cabeza en el despertar, cada 5 ticks (bloques; sin la altura que le da el servidor). */
    public static final float[][] CABEZA_DESPERTAR = {{0.00F, 7.00F, 1.27F}, {0.00F, 7.08F, 1.22F}, {0.00F, 7.17F, 1.15F}, {0.00F, 7.20F, 1.14F}, {0.00F, 7.16F, 1.17F}, {0.00F, 7.02F, 1.26F}, {0.00F, 6.99F, 1.27F}, {0.00F, 7.19F, 1.16F}, {0.00F, 6.75F, 1.39F}, {0.00F, 7.46F, 0.99F}, {-0.01F, 7.68F, 0.84F}, {-0.29F, 7.68F, 0.77F}, {-0.10F, 7.71F, 0.80F}, {0.14F, 7.71F, 0.79F}, {-0.01F, 7.07F, 1.27F}, {0.00F, 7.27F, 1.09F}, {0.00F, 7.67F, 0.72F}, {0.00F, 7.96F, 0.36F}, {0.00F, 8.25F, -0.03F}, {0.00F, 8.37F, -0.22F}, {0.00F, 7.83F, 1.13F}, {0.00F, 9.39F, 1.21F}, {0.00F, 9.96F, 0.61F}, {0.00F, 10.39F, 1.16F}, {0.00F, 10.82F, 0.29F}, {0.00F, 10.96F, 0.91F}, {0.00F, 11.05F, 1.27F}, {0.00F, 11.23F, 0.04F}, {0.00F, 9.86F, 2.05F}, {0.00F, 11.92F, -0.75F}, {0.00F, 11.91F, -0.88F}, {-0.01F, 11.86F, -0.01F}, {0.00F, 11.87F, -0.08F}, {0.00F, 11.87F, -0.10F}, {0.01F, 11.58F, 0.43F}, {0.00F, 10.97F, 0.88F}, {0.00F, 10.71F, 0.76F}, {0.00F, 10.50F, 0.80F}, {0.00F, 10.40F, 0.80F}};
    /** Pecho en el despertar, cada 5 ticks (bloques; sin la altura que le da el servidor). */
    public static final float[][] PECHO_DESPERTAR = {{0.00F, 4.48F, 1.30F}, {0.00F, 4.56F, 1.31F}, {0.00F, 4.64F, 1.32F}, {0.00F, 4.65F, 1.32F}, {0.00F, 4.62F, 1.32F}, {0.00F, 4.50F, 1.30F}, {0.00F, 4.48F, 1.30F}, {0.00F, 4.66F, 1.32F}, {0.00F, 4.35F, 1.28F}, {0.00F, 4.53F, 1.31F}, {-0.01F, 4.71F, 1.33F}, {-0.11F, 4.70F, 1.32F}, {-0.01F, 4.70F, 1.33F}, {0.03F, 4.70F, 1.33F}, {0.00F, 4.14F, 1.27F}, {0.00F, 4.36F, 1.30F}, {0.00F, 4.71F, 1.34F}, {0.00F, 5.06F, 1.36F}, {0.00F, 5.45F, 1.36F}, {0.00F, 5.62F, 1.35F}, {0.00F, 4.90F, 1.29F}, {0.00F, 6.48F, 1.28F}, {0.00F, 7.09F, 1.35F}, {0.00F, 7.44F, 1.29F}, {0.00F, 7.94F, 1.36F}, {0.00F, 7.98F, 1.32F}, {0.00F, 8.14F, 1.27F}, {0.00F, 8.41F, 1.36F}, {0.00F, 7.53F, 1.02F}, {0.00F, 9.48F, 1.31F}, {0.00F, 9.39F, 1.33F}, {0.00F, 9.05F, 1.36F}, {0.00F, 9.07F, 1.36F}, {0.00F, 9.09F, 1.36F}, {0.00F, 8.59F, 1.35F}, {0.00F, 7.97F, 1.32F}, {0.00F, 7.78F, 1.34F}, {0.00F, 7.59F, 1.34F}, {0.00F, 7.50F, 1.34F}};

    /** Donde va la cabeza a los tantos ticks (de animacion) de empezar a despertar. */
    public static Vec3 cabezaDespertar(float ticks) {
        return tabla(CABEZA_DESPERTAR, ticks / 5.0F);
    }

    /** Donde va el pecho a los tantos ticks (de animacion) de empezar a despertar. */
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
