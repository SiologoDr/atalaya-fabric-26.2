package com.atalaya.entity;

import net.minecraft.world.phys.Vec3;

/**
 * Medidas de Novilis que comparten servidor y cliente. GENERADO por
 * materiales/generadores/novilis_juego_anim.py desde las mismas poses que las
 * animaciones: si una animacion cambia, estos puntos cambian.
 *
 * Los puntos van en bloques y en el espacio del cuerpo: x hacia SU izquierda,
 * y hacia arriba desde los pies, z hacia delante. NovilisEntity los pasa al
 * mundo con el giro del cuerpo.
 */
public final class NovilisGeometria {

    private NovilisGeometria() {
    }

    /** Lo que alcanza la hoja en el Barrido, desde sus pies (bloques). */
    public static final double ALCANCE_HOJA = 13.37;
    /** Lo que avanza el cuerpo por vuelta de la animacion de andar (bloques). */
    public static final float ZANCADA = 11.411F;

    public static final Vec3 PECHO = new Vec3(0.000, 11.618, 1.753);
    public static final Vec3 CABEZA = new Vec3(0.000, 14.906, 0.110);
    public static final Vec3 HALO = new Vec3(0.000, 15.563, -1.370);
    public static final Vec3 PUNTA_ALZA = new Vec3(0.198, 25.449, -1.070);
    public static final Vec3 PUNTA_CLAVA = new Vec3(-0.248, -4.418, 2.841);
    public static final Vec3 PUNTA_FUENTES = new Vec3(-0.090, -3.971, 2.820);
    public static final Vec3 PECHO_FUENTES = new Vec3(0.000, 8.050, 2.255);
    public static final Vec3 MANO_SOL = new Vec3(4.164, 16.221, 1.096);
    public static final Vec3 MANO_INVOCA = new Vec3(-3.078, 25.331, 0.624);
    public static final Vec3 OFRENDA_ALZADO_P = new Vec3(0.000, 14.906, 3.288);
    public static final Vec3 DIOS_MANO_IZQ = new Vec3(4.822, 15.563, 1.096);
    public static final Vec3 DIOS_MANO_DER = new Vec3(-4.822, 15.564, 1.096);
    public static final Vec3 SOL_PROPIO = new Vec3(0.000, 24.500, -1.500);
    public static final Vec3 PUNTA_TAJO_1 = new Vec3(9.570, 9.120, 8.437);
    public static final Vec3 PUNTA_TAJO_2 = new Vec3(-10.638, 8.921, 8.104);
    public static final Vec3 PUNTA_TAJO_3 = new Vec3(3.871, 1.759, 10.184);
    public static final Vec3 PUNTA_TAJO_4 = new Vec3(10.642, 9.648, 7.262);
    public static final Vec3 MANO_LANZA_1 = new Vec3(0.877, 9.207, 5.041);
    public static final Vec3 MANO_LANZA_2 = new Vec3(0.877, 9.207, 5.041);
    public static final Vec3 MANO_LANZA_3 = new Vec3(0.877, 9.207, 5.041);
    public static final Vec3 DIOS_LANZA_1_P = new Vec3(-0.000, 10.303, 4.603);
    public static final Vec3 DIOS_LANZA_2_P = new Vec3(-0.000, 10.303, 4.603);
    public static final Vec3 DIOS_LANZA_3_P = new Vec3(-0.000, 10.303, 4.603);

    public static final int DURACION_REPOSO = 80;
    public static final int DURACION_ANDAR = 40;
    public static final int DURACION_DORMIDO = 120;
    public static final int DURACION_DESPERTAR = 68;
    public static final int DURACION_BARRIDO = 76;
    public static final int DURACION_CASTIGO = 56;
    public static final int DURACION_CASTIGO_ONDA = 84;
    public static final int DURACION_SOL = 76;
    public static final int DURACION_TROMPETAS = 52;
    public static final int DURACION_FUENTES = 32;
    public static final int DURACION_FUENTES_CARGA = 40;
    public static final int DURACION_OFRENDA = 52;
    public static final int DURACION_OFRENDA_SOSTIENE = 40;
    public static final int DURACION_DIOS = 100;
    public static final int DURACION_GRITO = 48;
    public static final int DURACION_ATURDIDO = 24;
    public static final int DURACION_ATURDIDO_BUCLE = 48;
    public static final int DURACION_TAMBALEO = 60;
    public static final int DURACION_LIBERACION = 200;
    public static final int DESPERTAR_RUGE = 48;
    public static final int TAJO_1 = 12;
    public static final int TAJO_2 = 28;
    public static final int TAJO_3 = 44;
    public static final int TAJO_4 = 62;
    public static final int CASTIGO_ALZA = 14;
    public static final int CASTIGO_MARCA = 20;
    public static final int CASTIGO_RAYO = 42;
    public static final int ONDA_CLAVA = 52;
    public static final int SOL_LANZA_1 = 20;
    public static final int SOL_LANZA_2 = 40;
    public static final int SOL_LANZA_3 = 60;
    public static final int TROMPETAS_ALZA = 22;
    public static final int FUENTES_CLAVA = 16;
    public static final int OFRENDA_SUELTA = 14;
    public static final int OFRENDA_AGARRA = 26;
    public static final int OFRENDA_ALZADO = 48;
    public static final int DIOS_SUELTA = 12;
    public static final int DIOS_MARCA = 20;
    public static final int DIOS_RECOGE = 90;
    public static final int DIOS_LANZA_1 = 32;
    public static final int DIOS_LANZA_2 = 52;
    public static final int DIOS_LANZA_3 = 72;
    public static final int GRITO_RUGE = 18;
    public static final int TAMBALEO_RUGE = 42;
    public static final int LIBERACION_ORO = 70;

    /** Entre las dos manos en la Ofrenda, desde OFRENDA_AGARRA hasta el final, tick a tick. */
    public static final float[][] MANOS_OFRENDA = {{0.00F, 7.67F, 4.60F}, {0.00F, 7.79F, 4.69F}, {0.00F, 7.94F, 4.78F}, {0.00F, 8.13F, 4.89F}, {-0.00F, 8.37F, 5.00F}, {-0.00F, 8.65F, 5.11F}, {-0.00F, 8.98F, 5.21F}, {-0.00F, 9.35F, 5.30F}, {-0.00F, 9.76F, 5.36F}, {-0.00F, 10.20F, 5.39F}, {-0.00F, 10.67F, 5.39F}, {-0.00F, 11.16F, 5.35F}, {-0.00F, 11.65F, 5.27F}, {-0.00F, 12.13F, 5.15F}, {-0.00F, 12.59F, 4.99F}, {-0.00F, 13.03F, 4.80F}, {-0.00F, 13.43F, 4.59F}, {-0.00F, 13.79F, 4.36F}, {-0.00F, 14.11F, 4.12F}, {0.00F, 14.37F, 3.88F}, {0.00F, 14.59F, 3.66F}, {0.00F, 14.77F, 3.46F}, {0.00F, 14.91F, 3.29F}, {0.00F, 15.22F, 2.79F}, {0.00F, 15.19F, 2.85F}, {0.00F, 15.02F, 3.13F}, {0.00F, 14.91F, 3.29F}};

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
