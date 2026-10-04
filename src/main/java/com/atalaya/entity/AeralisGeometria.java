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

    public static final Vec3 NUCLEO = new Vec3(0.000, 6.284, 1.159);
    public static final Vec3 CABEZA = new Vec3(0.000, 9.045, 0.750);
    public static final Vec3 OJO_IZQ = new Vec3(0.750, 9.161, 0.884);
    public static final Vec3 OJO_DER = new Vec3(-0.750, 9.161, 0.884);
    public static final Vec3 BOCA = new Vec3(0.000, 8.520, 1.090);
    public static final Vec3 BOCA_MARCA = new Vec3(0.000, 7.941, 1.963);
    public static final Vec3 NUCLEO_JUICIO = new Vec3(0.000, 5.319, 1.644);
    public static final Vec3 NUCLEO_TORNADOS = new Vec3(0.000, 4.768, 0.953);
    public static final Vec3 PUNTA_ALA_IZQ_ALETEO = new Vec3(2.812, 6.431, 12.532);
    public static final Vec3 PUNTA_ALA_DER_ALETEO = new Vec3(-11.181, 7.941, 5.444);
    public static final Vec3 PUNTA_ALA_IZQ = new Vec3(10.970, 11.846, -5.002);
    public static final Vec3 PUNTA_ALA_DER = new Vec3(-10.970, 11.846, -5.002);
    public static final Vec3 PUNTA_ABDOMEN = new Vec3(0.000, 0.522, -1.363);

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
}
