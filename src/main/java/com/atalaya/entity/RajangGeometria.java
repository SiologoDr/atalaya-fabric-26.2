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
    public static final Vec3 ZARPA_GARRA = new Vec3(1.598, 0.415, 6.002);
    public static final Vec3 ZARPA_CARGA = new Vec3(-3.205, 7.203, 6.660);
    public static final Vec3 ZARPA_IZQ_TERREMOTO = new Vec3(0.700, -0.722, 5.482);
    public static final Vec3 ZARPA_DER_TERREMOTO = new Vec3(-0.724, -0.619, 5.641);
    public static final Vec3 ZARPA_IZQ = new Vec3(1.375, 0.233, 2.207);
    public static final Vec3 ZARPA_DER = new Vec3(-1.375, 0.233, 2.207);
    public static final Vec3 PATA_IZQ = new Vec3(1.375, 0.126, -5.723);
    public static final Vec3 PATA_DER = new Vec3(-1.375, 0.126, -5.723);
    public static final Vec3 PUNTA_COLA = new Vec3(0.000, 7.332, -17.149);

    public static final int DURACION_DESPERTAR = 72;
    public static final int DESPERTAR_SE_ALZA = 30;
    public static final int DESPERTAR_RUGE = 46;
    public static final int DURACION_GARRA = 26;
    public static final int GARRA_ALZA = 2;
    public static final int GARRA_GOLPE = 10;
    public static final int DURACION_TERREMOTO = 46;
    public static final int TERREMOTO_GOLPE = 19;
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
    public static final int PERIODO_ANDAR = 32;
    public static final int PERIODO_CORRER = 16;
}
