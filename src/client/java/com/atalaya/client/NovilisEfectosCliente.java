package com.atalaya.client;

import com.atalaya.entity.NovilisEntity;
import com.atalaya.entity.NovilisGeometria;
import net.minecraft.client.Minecraft;
import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.world.entity.Entity;

/**
 * Lo que Novilis provoca alrededor y que el servidor no necesita saber:
 *
 *   - el suelo que tiembla con sus pasos y el golpe de cada tajo;
 *   - el miedo (los bordes que se queman) al despertar, al rugir, en el Dios
 *     de la Guerra y en el Mar de Llamas;
 *   - el retumbo mientras carga la Espada del Fuego, el golpe al salir, la caida
 *     y la explosion de la Furia Infernal.
 *
 * Los golpes con onda los sacude la propia particula de la onda.
 */
public final class NovilisEfectosCliente {

    private NovilisEfectosCliente() {
    }

    public static void tick(Minecraft mc) {
        ClientLevel nivel = mc.level;
        if (nivel == null || mc.player == null || mc.isPaused()) {
            return;
        }
        for (Entity e : nivel.entitiesForRendering()) {
            if (e instanceof NovilisEntity n && n.distanceToSqr(mc.player) < 120 * 120) {
                procesar(n);
            }
        }
    }

    private static void procesar(NovilisEntity n) {
        double x = n.getX();
        double y = n.getY() + 6.0;
        double z = n.getZ();
        if (n.isDeadOrDying()) {
            if (n.deathTime == 3) {
                NereaPresencia.asustarFuego(x, y, z, 0.6F, 64);
                NereaPresencia.sacudir(x, y, z, 1.2F, 50);
            }
            return;
        }
        int t = (int) ((n.tickCount - n.inicioEstado) * n.ritmoCliente);
        switch (n.getEstado()) {
            case NovilisEntity.LIBRE -> {
                if (n.walkAnimation.speed() > 0.2F && n.tickCount % 18 == 0) {
                    NereaPresencia.sacudir(x, y, z, 0.35F, 28);
                }
            }
            case NovilisEntity.DESPERTAR -> {
                if (t == NovilisGeometria.DESPERTAR_RUGE) {
                    NereaPresencia.sacudir(x, y, z, 2.4F, 60);
                    NereaPresencia.asustarFuego(x, y, z, 0.9F, 60);
                }
            }
            case NovilisEntity.BARRIDO -> {
                if (t == NovilisGeometria.TAJO_1 || t == NovilisGeometria.TAJO_2 || t == NovilisGeometria.TAJO_3
                        || t == NovilisGeometria.TAJO_4) {
                    NereaPresencia.sacudir(x, y, z, 1.2F, 36);
                }
            }
            case NovilisEntity.CASTIGO, NovilisEntity.CASTIGO_ONDA -> {
                if (t >= NovilisGeometria.CASTIGO_ALZA && t < NovilisGeometria.CASTIGO_RAYO) {
                    NereaPresencia.retumbar(x, y, z, 0.25F, 60);
                }
            }
            case NovilisEntity.ESPADA -> {
                if (t < NovilisGeometria.ESPADA_SALE) {
                    NereaPresencia.retumbar(x, y, z, 0.08F + 0.3F * t / NovilisGeometria.ESPADA_SALE, 48);
                } else if (t == NovilisGeometria.ESPADA_SALE) {
                    NereaPresencia.sacudir(x, y, z, 1.6F, 48);
                }
            }
            case NovilisEntity.INFERNAL -> {
                if (t == NovilisGeometria.INFERNAL_ATERRIZA) {
                    NereaPresencia.sacudir(x, y, z, 2.6F, 64);
                } else if (t == NovilisGeometria.INFERNAL_EXPLOTA) {
                    NereaPresencia.sacudir(x, y, z, 2.8F, 72);
                    NereaPresencia.asustarFuego(x, y, z, 0.8F, 56);
                }
            }
            case NovilisEntity.MAR -> {
                if (t == NovilisGeometria.MAR_CLAVA) {
                    NereaPresencia.sacudir(x, y, z, 2.4F, 90);
                    NereaPresencia.asustarFuego(x, y, z, 1.0F, 90);
                }
            }
            case NovilisEntity.MINI_CLAVA -> {
                // Clava la espada para un minijuego: sacude, pero sin el miedo del Mar.
                if (t == NovilisGeometria.MAR_CLAVA) {
                    NereaPresencia.sacudir(x, y, z, 1.6F, 64);
                }
            }
            case NovilisEntity.DIOS -> {
                if (t == NovilisGeometria.DIOS_MARCA) {
                    NereaPresencia.sacudir(x, y, z, 2.0F, 64);
                    NereaPresencia.asustarFuego(x, y, z, 1.0F, 80);
                }
            }
            case NovilisEntity.GRITO -> {
                if (t == NovilisGeometria.GRITO_RUGE) {
                    NereaPresencia.sacudir(x, y, z, 2.2F, 60);
                    NereaPresencia.asustarFuego(x, y, z, 0.85F, 64);
                }
            }
            case NovilisEntity.TAMBALEO -> {
                if (t == 2) {
                    NereaPresencia.sacudir(x, y, z, 2.0F, 56);
                    NereaPresencia.asustarFuego(x, y, z, 0.6F, 56);
                }
            }
            default -> {
            }
        }
    }
}
