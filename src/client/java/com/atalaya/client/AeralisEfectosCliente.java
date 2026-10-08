package com.atalaya.client;

import com.atalaya.entity.AeralisEntity;
import com.atalaya.entity.AeralisGeometria;
import com.atalaya.particula.AtalayaParticulas;
import net.minecraft.client.Minecraft;
import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.util.Mth;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.player.Player;

/**
 * Lo que Aeralis provoca alrededor y que el servidor no necesita saber:
 *
 *   - el VENDAVAL: mientras esta despierta cerca, el viento corre alrededor de
 *     cada jugador (estelas y polvo girando en torno a ella). En el silencio
 *     del Juicio se para de golpe: eso es lo que se nota;
 *   - el temblor de cada batida cerca, el del chillido y el sostenido del
 *     ciclon del Juicio;
 *   - el miedo (nubes de tormenta en los bordes) al chillar, al marcarte, en el
 *     silencio y mientras eres tu el marcado.
 *
 * Los golpes con onda de presion los sacude la propia particula de la onda.
 */
public final class AeralisEfectosCliente {

    private AeralisEfectosCliente() {
    }

    public static void tick(Minecraft mc) {
        ClientLevel nivel = mc.level;
        if (nivel == null || mc.player == null || mc.isPaused()) {
            return;
        }
        AeralisEntity viento = null;
        double mejor = 72 * 72;
        for (Entity e : nivel.entitiesForRendering()) {
            if (e instanceof AeralisEntity a && a.distanceToSqr(mc.player) < 110 * 110) {
                procesar(a, mc.player);
                double d = a.distanceToSqr(mc.player);
                if (d < mejor && a.getEstado() != AeralisEntity.DORMIDA && !a.isDeadOrDying()) {
                    mejor = d;
                    viento = a;
                }
            }
        }
        if (viento != null && viento.getEstado() != AeralisEntity.JUICIO_SUBE) {
            vendaval(nivel, viento, mc.player);
        }
    }

    /** El viento que corre alrededor del jugador, girando en torno a ella. */
    private static void vendaval(ClientLevel nivel, AeralisEntity a, Player yo) {
        RandomSource r = yo.getRandom();
        int n = 1 + a.fase() / 2;
        for (int i = 0; i < n; i++) {
            double ang = r.nextDouble() * Math.PI * 2;
            double d = 3.0 + r.nextDouble() * 12.0;
            double x = yo.getX() + Math.cos(ang) * d;
            double z = yo.getZ() + Math.sin(ang) * d;
            double y = yo.getY() + 0.3 + r.nextDouble() * 5.0;
            // Gira alrededor de ella (en el sentido de las agujas) y algo hacia fuera.
            double dx = x - a.getX();
            double dz = z - a.getZ();
            double l = Math.max(1.0, Math.sqrt(dx * dx + dz * dz));
            double vel = 0.55 + 0.12 * a.fase();
            double vx = (-dz / l * 0.9 + dx / l * 0.25) * vel;
            double vz = (dx / l * 0.9 + dz / l * 0.25) * vel;
            nivel.addParticle(AtalayaParticulas.AERALIS_VIENTO, x, y, z, vx, (r.nextDouble() - 0.5) * 0.05, vz);
        }
        if (r.nextInt(5) == 0) {
            double ang = r.nextDouble() * Math.PI * 2;
            double d = 2.0 + r.nextDouble() * 8.0;
            nivel.addParticle(AtalayaParticulas.AERALIS_POLVO, yo.getX() + Math.cos(ang) * d, yo.getY() + 0.1,
                    yo.getZ() + Math.sin(ang) * d, Math.cos(ang + 1.6) * 0.15, 0.02, Math.sin(ang + 1.6) * 0.15);
        }
    }

    private static void procesar(AeralisEntity a, Player yo) {
        double x = a.getX();
        double y = a.getY() + 6.0;
        double z = a.getZ();
        if (a.isDeadOrDying()) {
            if (a.deathTime == 3) {
                NereaPresencia.asustar(x, y, z, 0.7F, 60, true);
                NereaPresencia.sacudir(x, y, z, 1.4F, 50);
            }
            return;
        }
        int e = a.getEstado();
        int t = (int) ((a.tickCount - a.inicioEstado) * a.ritmoCliente);
        boolean soyYo = a.getIdObjetivo() == yo.getId();
        switch (e) {
            case AeralisEntity.LIBRE -> {
                if (a.tickCount % AeralisGeometria.PERIODO_VUELO == AeralisGeometria.VUELO_GOLPE) {
                    NereaPresencia.sacudir(x, y, z, 0.35F, 24);
                }
            }
            case AeralisEntity.DESPERTAR -> {
                // Se revuelve en el suelo desde que abre los ojos hasta que despega;
                // cada batida sacude (la primera, la que la despega, mas).
                if (t >= AeralisGeometria.DESPERTAR_ABRE && t < AeralisGeometria.DESPERTAR_ALZA) {
                    NereaPresencia.retumbar(x, y, z, 0.25F, 40);
                }
                int[] batidas = AeralisGeometria.DESPERTAR_BATIDAS;
                for (int i = 0; i < batidas.length; i++) {
                    if (t == batidas[i]) {
                        NereaPresencia.sacudir(x, y, z, i == 0 ? 1.2F : 0.5F, 40);
                    }
                }
                if (t == AeralisGeometria.DESPERTAR_CHILLA) {
                    NereaPresencia.sacudir(x, y, z, 2.6F, 56);
                    NereaPresencia.asustar(x, y, z, 0.9F, 56, true);
                }
            }
            case AeralisEntity.ALETEO -> {
                if (t == AeralisGeometria.ALETEO_SUELTA) {
                    NereaPresencia.sacudir(x, y, z, 1.1F, 34);
                }
            }
            case AeralisEntity.TORNADOS -> {
                if (t == 2) {
                    NereaPresencia.asustar(x, y, z, 0.35F, 48, true);
                }
            }
            case AeralisEntity.LADRONA -> {
                if (t == AeralisGeometria.RAFAGA_SUELTA) {
                    NereaPresencia.sacudir(x, y, z, 0.5F, 32);
                }
            }
            case AeralisEntity.MARCA -> {
                if (t == AeralisGeometria.MARCA_FIJA) {
                    NereaPresencia.asustar(x, y, z, soyYo ? 1.0F : 0.35F, soyYo ? 400 : 48, true);
                }
            }
            case AeralisEntity.RAFAGA, AeralisEntity.DOBLE_RAFAGA -> {
                if (soyYo) {
                    NereaPresencia.asustar(x, y, z, 0.45F, 400, true);
                }
            }
            case AeralisEntity.JUICIO_SUBE -> {
                // El silencio pesa: el miedo sube poco a poco sin que pase nada.
                float k = Mth.clamp(t / (float) AeralisGeometria.DURACION_JUICIO_SUBE, 0.0F, 1.0F);
                NereaPresencia.asustar(x, y, z, 0.25F + 0.5F * k, 90, true);
            }
            case AeralisEntity.JUICIO_SOSTIENE -> {
                NereaPresencia.retumbar(x, y, z, 0.3F, 70);
                if (soyYo) {
                    NereaPresencia.asustar(x, y, z, 0.85F, 400, true);
                }
            }
            case AeralisEntity.TAMBALEO -> {
                if (t == 2) {
                    NereaPresencia.sacudir(x, y, z, 2.2F, 56);
                    NereaPresencia.asustar(x, y, z, 0.6F, 56, true);
                }
            }
            default -> {
            }
        }
    }
}
