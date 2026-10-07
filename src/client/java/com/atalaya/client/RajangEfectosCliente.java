package com.atalaya.client;

import com.atalaya.entity.RajangEntity;
import com.atalaya.entity.RajangGeometria;
import com.atalaya.particula.AtalayaParticulas;
import net.minecraft.client.Minecraft;
import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.player.Player;

/**
 * Lo que Rajang provoca alrededor y que el servidor no necesita saber:
 *
 *   - el suelo que tiembla bajo sus pasos cuando corre, el golpe de cada
 *     zarpazo, el retumbo largo del Terremoto, del Sello y del Cataclismo;
 *   - el miedo (la selva y las grietas de jade en los bordes) al despertar,
 *     al rugir, cuando el Sello se acaba y cuando el cielo se raja;
 *   - las hojas que caen de la selva mientras pelea.
 *
 * Los golpes con onda los sacude la propia particula de la onda.
 */
public final class RajangEfectosCliente {

    private RajangEfectosCliente() {
    }

    public static void tick(Minecraft mc) {
        ClientLevel nivel = mc.level;
        if (nivel == null || mc.player == null || mc.isPaused()) {
            return;
        }
        for (Entity e : nivel.entitiesForRendering()) {
            if (e instanceof RajangEntity r && r.distanceToSqr(mc.player) < 110 * 110) {
                procesar(nivel, r, mc.player);
            }
        }
    }

    private static void procesar(ClientLevel nivel, RajangEntity r, Player yo) {
        double x = r.getX();
        double y = r.getY() + 4.0;
        double z = r.getZ();
        if (r.isDeadOrDying()) {
            if (r.deathTime == 3) {
                NereaPresencia.asustarTierra(x, y, z, 0.6F, 60);
                NereaPresencia.sacudir(x, y, z, 1.2F, 50);
            }
            return;
        }
        int e = r.getEstado();
        int t = (int) ((r.tickCount - r.inicioEstado) * r.ritmoCliente);
        switch (e) {
            case RajangEntity.LIBRE -> {
                if (r.velocidad > RajangEntity.VEL_GALOPE && r.tickCount % 12 == 0) {
                    NereaPresencia.sacudir(x, y, z, 0.25F, 24);
                }
                hojas(nivel, r, yo);
            }
            case RajangEntity.DESPERTAR -> {
                // la tierra retumba mientras saca las manos de ella, y otra vez cuando
                // muele la piedra antes del rugido
                if (t > RajangGeometria.DESPERTAR_SE_ALZA && t < RajangGeometria.DESPERTAR_SE_ALZA + 14
                        || t > RajangGeometria.DESPERTAR_RUGE - 20 && t < RajangGeometria.DESPERTAR_RUGE) {
                    NereaPresencia.retumbar(x, y, z, 0.35F, 40);
                }
                if (t == RajangGeometria.DESPERTAR_RUGE) {
                    NereaPresencia.sacudir(x, y, z, 2.4F, 56);
                    NereaPresencia.asustarTierra(x, y, z, 0.9F, 56);
                }
                if (t == RajangGeometria.DESPERTAR_APOYA) {
                    NereaPresencia.sacudir(x, y, z, 0.8F, 40);
                }
            }
            case RajangEntity.GARRA -> {
                if (t == RajangGeometria.GARRA_GOLPE) {
                    NereaPresencia.sacudir(x, y, z, 1.6F, 40);
                }
            }
            case RajangEntity.TERREMOTO -> {
                if (t >= RajangGeometria.TERREMOTO_GOLPE && t < RajangGeometria.TERREMOTO_GOLPE + 40) {
                    NereaPresencia.retumbar(x, y, z, 0.6F, 64);
                }
                if (t == RajangGeometria.TERREMOTO_GOLPE) {
                    NereaPresencia.asustarTierra(x, y, z, 0.45F, 56);
                }
            }
            case RajangEntity.RUGIDO -> {
                if (t == RajangGeometria.RUGIDO_RUGE) {
                    NereaPresencia.sacudir(x, y, z, 2.0F, 56);
                    NereaPresencia.asustarTierra(x, y, z, 0.8F, 64);
                }
            }
            case RajangEntity.SELLO -> {
                NereaPresencia.retumbar(x, y, z, 0.18F, 70);
                if (r.getSello() < 100 && r.tickCount % 20 == 0) {
                    NereaPresencia.asustarTierra(x, y, z, 0.35F + 0.4F * (1.0F - r.getSello() / 100.0F), 80);
                }
            }
            case RajangEntity.CATACLISMO -> {
                if (t == RajangGeometria.CATACLISMO_RUGE) {
                    NereaPresencia.sacudir(x, y, z, 2.6F, 70);
                    NereaPresencia.asustarTierra(x, y, z, 1.0F, 80);
                }
            }
            case RajangEntity.CATACLISMO_SOSTIENE -> NereaPresencia.retumbar(x, y, z, 0.35F, 80);
            case RajangEntity.SALTO -> {
                if (t == RajangGeometria.SALTO_ATERRIZA) {
                    NereaPresencia.sacudir(x, y, z, 2.4F, 44);
                }
            }
            case RajangEntity.TAMBALEO -> {
                if (t == 2) {
                    NereaPresencia.sacudir(x, y, z, 2.0F, 56);
                    NereaPresencia.asustarTierra(x, y, z, 0.6F, 56);
                }
            }
            case RajangEntity.EMBESTIDA_AVISO -> {
                if (t == RajangGeometria.EMBESTIDA_RASCA_1 || t == RajangGeometria.EMBESTIDA_RASCA_2) {
                    NereaPresencia.sacudir(x, y, z, 0.5F, 30);
                }
                if (t == 1) {
                    NereaPresencia.asustarTierra(x, y, z, 0.35F, 40);
                }
            }
            case RajangEntity.EMBESTIDA -> NereaPresencia.retumbar(x, y, z, 0.7F, 40);
            case RajangEntity.EMBESTIDA_FRENA -> {
                if (t < RajangGeometria.EMBESTIDA_FRENA_PARA) {
                    NereaPresencia.retumbar(x, y, z, 0.45F, 36);
                }
            }
            case RajangEntity.ESTAMPADO -> {
                if (t == 1) {
                    NereaPresencia.sacudir(x, y, z, 2.6F, 50);
                }
            }
            case RajangEntity.TUMBA -> {
                // El suelo tiembla cada vez mas mientras el circulo se llena; al llenarse, revienta.
                if (t < RajangGeometria.TUMBA_ESTALLA) {
                    NereaPresencia.retumbar(x, y, z, 0.15F + 0.5F * t / RajangGeometria.TUMBA_ESTALLA, 60);
                    if (t == 2 && yo.distanceToSqr(r) < RajangEntity.TUMBA_RADIO * RajangEntity.TUMBA_RADIO) {
                        NereaPresencia.asustarTierra(x, y, z, 0.7F, 40);
                    }
                }
                if (t == RajangGeometria.TUMBA_ESTALLA) {
                    NereaPresencia.sacudir(x, y, z, 3.0F, 64);
                    NereaPresencia.asustarTierra(x, y, z, 0.9F, 40);
                }
            }
            default -> {
            }
        }
    }

    /** Mientras pelea, a quien esta cerca le caen hojas de la selva. */
    private static void hojas(ClientLevel nivel, RajangEntity r, Player yo) {
        if (r.distanceToSqr(yo) > 48 * 48) {
            return;
        }
        RandomSource azar = yo.getRandom();
        if (azar.nextInt(6) == 0) {
            double a = azar.nextDouble() * Math.PI * 2;
            double d = 2.0 + azar.nextDouble() * 10.0;
            nivel.addParticle(AtalayaParticulas.RAJANG_HOJA, yo.getX() + Math.cos(a) * d, yo.getY() + 8.0 + azar.nextDouble() * 4.0,
                    yo.getZ() + Math.sin(a) * d, 0, -0.03, 0);
        }
    }
}
