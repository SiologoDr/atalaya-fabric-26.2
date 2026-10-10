package com.atalaya.entity;

import com.atalaya.particula.AtalayaParticulas;
import com.atalaya.sonido.AtalayaSonidos;
import java.util.ArrayList;
import java.util.List;
import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.phys.Vec3;
import org.jspecify.annotations.Nullable;

/**
 * Veletas del Vendaval (fase I): salen veletas alrededor de la cima (dos
 * jugando solo, tres con dos o tres, y si no, cuatro), cada una con su flecha
 * de bronce. Un clic derecho la gira 45 grados (agachado, al reves). Ella no
 * para quieta: da vueltas a la arena y cambia de sentido, asi que hay que ir
 * corrigiendolas. Cuando todas estan encendidas a la vez, el viento la atrapa y
 * la baja al suelo: aturdida 5 s. Dura 25 s y mientras ni ataca ni le entra nada.
 *
 * Afinado el 10-10-2026: cuenta que apunta con 30 grados a cada lado (con ocho
 * rumbos de 45 se solapan un poco) y, cuando ella se sale de su rumbo, la
 * veleta aguanta enganchada 3 s (5 jugando solo, y entonces salen mas juntas):
 * un grupo pequeno puede ir de una a otra.
 */
final class VeletasAeralis extends MinijuegoAeralis {

    static final int SALE = 30;
    static final int DURA = SALE + 500;
    /** A cuanto del centro salen las veletas y a cuanto da ella las vueltas. */
    private static final double RADIO_VELETAS = 12.0;
    private static final double RADIO_VELETAS_SOLO = 8.0;
    /** Lo que se perdona (grados a cada lado) para contar que apunta. */
    private static final double TOLERANCIA = 30.0;
    /** Lo que aguanta encendida cuando ella se sale de su rumbo (ticks). */
    private static final int ENGANCHE = 60;
    private static final int ENGANCHE_SOLO = 100;
    private static final double RADIO_VUELO = 18.0;
    /** Lo que tarda en dar la vuelta entera (ticks) y cada cuanto puede cambiar de sentido. */
    private static final double VUELTA = 520.0;
    private static final int CAMBIO = 140;
    /** Lo que tarda el viento en atraparla al encenderse todas. */
    private static final int ATRAPA = 24;
    static final int ATURDIDA = 100;

    private final List<VeletaAeralisEntity> veletas = new ArrayList<>();
    private double angulo;
    private int sentido = 1;
    private int atrapada = -1;
    private int enganche = ENGANCHE;

    VeletasAeralis(AeralisEntity a) {
        super(a, MinijuegosAeralis.VELETAS, DURA);
    }

    @Override
    boolean empezar(ServerLevel nivel, List<Player> js) {
        if (js.isEmpty()) {
            return false;
        }
        int n = js.size() <= 1 ? 2 : js.size() <= 3 ? 3 : 4;
        double radio = js.size() <= 1 ? RADIO_VELETAS_SOLO : RADIO_VELETAS;
        enganche = js.size() <= 1 ? ENGANCHE_SOLO : ENGANCHE;
        Vec3 c = a.centroArenaMini();
        double giro = nivel.getRandom().nextDouble() * Math.PI * 2;
        angulo = Math.atan2(a.getZ() - c.z, a.getX() - c.x);
        for (int i = 0; i < n; i++) {
            double ang = giro + Math.PI * 2 * i / n;
            Vec3 p = new Vec3(c.x + Math.cos(ang) * radio, c.y, c.z + Math.sin(ang) * radio);
            double y = AeralisEntity.sueloBajo(nivel, p.x, c.y + 4, p.z);
            // Empiezan mirando a cualquier sitio menos a ella.
            int rumbo = nivel.getRandom().nextInt(8);
            veletas.add(VeletaAeralisEntity.alzar(nivel, this, new Vec3(p.x, y, p.z), rumbo));
        }
        necesario = n;
        a.sonidoMini(AtalayaSonidos.AERALIS_VELETA_SALE, 6.0F);
        a.avisarMini(nivel, Component.translatable("hud.atalaya.aeralis.veletas_empieza").withStyle(ChatFormatting.AQUA));
        return true;
    }

    @Override
    @Nullable double[] destino(ServerLevel nivel) {
        Vec3 c = a.centroArenaMini();
        if (atrapada >= 0) {
            // El viento la baja al suelo, en medio de las veletas.
            return new double[]{a.getX(), a.getZ(), 0.0, 0.05};
        }
        double x = c.x + Math.cos(angulo) * RADIO_VUELO;
        double z = c.z + Math.sin(angulo) * RADIO_VUELO;
        return new double[]{x, z, 5.0, 0.6};
    }

    @Override
    @Nullable Vec3 mira(ServerLevel nivel, @Nullable LivingEntity objetivo) {
        return a.centroArenaMini();
    }

    @Override
    void tick(ServerLevel nivel) {
        veletas.removeIf(v -> v.isRemoved());
        if (atrapada >= 0) {
            // Las veletas la sujetan con su viento.
            if ((t - atrapada) % 2 == 0) {
                Vec3 pecho = a.puntoMundo(AeralisGeometria.NUCLEO);
                for (VeletaAeralisEntity v : veletas) {
                    Vec3 desde = v.position().add(0, VeletaAeralisEntity.ALTO, 0);
                    for (int k = 1; k < 8; k++) {
                        Vec3 p = desde.lerp(pecho, k / 8.0);
                        nivel.sendParticles(AtalayaParticulas.AERALIS_VIENTO, true, true, p.x, p.y, p.z, 1, 0.2, 0.2, 0.2, 0.02);
                    }
                }
            }
            if (t - atrapada >= ATRAPA) {
                a.acabarMinijuego(nivel, true, true);
            }
            return;
        }
        if (t < SALE) {
            return;
        }
        // Da vueltas a la arena; de vez en cuando cambia de sentido.
        if ((t - SALE) % CAMBIO == CAMBIO - 1 && nivel.getRandom().nextInt(3) > 0) {
            sentido = -sentido;
        }
        angulo += sentido * Math.PI * 2 / VUELTA;
        Vec3 ella = a.position();
        int encendidas = 0;
        for (VeletaAeralisEntity v : veletas) {
            boolean apunta = v.apuntaA(ella, TOLERANCIA);
            if (apunta) {
                v.enganche = enganche;
            } else if (v.enganche > 0) {
                v.enganche--;
            }
            v.encender(nivel, apunta ? VeletaAeralisEntity.APUNTA : v.enganche > 0 ? VeletaAeralisEntity.ENGANCHADA
                    : VeletaAeralisEntity.APAGADA);
            if (v.encendida()) {
                encendidas++;
            }
            if (apunta) {
                if (t % 6 == 0) {
                    // El punteado de la encendida hasta ella.
                    Vec3 desde = v.position().add(0, VeletaAeralisEntity.ALTO, 0);
                    Vec3 hasta = a.puntoMundo(AeralisGeometria.NUCLEO);
                    for (int k = 1; k < 6; k++) {
                        Vec3 p = desde.lerp(hasta, k / 6.0);
                        nivel.sendParticles(AtalayaParticulas.AERALIS_LUZ, true, true, p.x, p.y, p.z, 1, 0.0, 0.0, 0.0, 0.0);
                    }
                }
            }
        }
        cuenta = encendidas;
        if (!veletas.isEmpty() && encendidas >= veletas.size()) {
            atrapada = t;
            a.sonidoMini(AtalayaSonidos.AERALIS_VELETA_ATRAPA, 7.0F);
            a.avisarMini(nivel, Component.translatable("hud.atalaya.aeralis.veletas_atrapa").withStyle(ChatFormatting.GOLD));
        }
    }

    /** Alguien ha girado una (VeletaAeralisEntity). */
    void alGirar(ServerLevel nivel, VeletaAeralisEntity v, Player p) {
    }

    @Override
    boolean exitoAlAcabar() {
        return atrapada >= 0;
    }

    @Override
    void forzarExito(ServerLevel nivel) {
        for (VeletaAeralisEntity v : veletas) {
            v.encender(nivel, VeletaAeralisEntity.APUNTA);
        }
        atrapada = t;
        a.sonidoMini(AtalayaSonidos.AERALIS_VELETA_ATRAPA, 7.0F);
    }

    @Override
    void limpiar(ServerLevel nivel, boolean exito, boolean avisar) {
        for (VeletaAeralisEntity v : veletas) {
            v.hundir();
        }
        veletas.clear();
    }
}
