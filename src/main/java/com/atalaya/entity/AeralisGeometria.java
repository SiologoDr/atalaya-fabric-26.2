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

    public static final int DURACION_DESPERTAR = 72;
    public static final int DESPERTAR_ALZA = 25;
    public static final int DESPERTAR_CHILLA = 44;
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
}
