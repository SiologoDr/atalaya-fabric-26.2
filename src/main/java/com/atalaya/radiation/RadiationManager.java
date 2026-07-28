package com.atalaya.radiation;

import com.atalaya.config.AtalayaConfig;
import com.atalaya.effect.RadiacionEffect;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.effect.MobEffectInstance;

/**
 * Aplica el efecto de radiacion a quien se acerca a una geoda.
 *
 * Corre cada tick, pero reparte a los jugadores en ranuras: cada uno se revisa
 * una vez por intervalo, no todos a la vez. Con 20 jugadores y un intervalo de
 * 20 ticks, se procesa uno por tick en vez de veinte de golpe.
 */
public final class RadiationManager {

    private static final int NIVEL_MAX = 4;
    private static final double DISTANCIA_MAXIMA = 12.0;
    private static final int INTERVALO_TICKS = 20;

    /**
     * El efecto dura mas que el intervalo a proposito: asi no parpadea el icono
     * entre una comprobacion y la siguiente.
     */
    private static final int DURACION_TICKS = INTERVALO_TICKS + 40;

    /**
     * false = marco normal de efecto (como Absorcion). true = marco "ambient",
     * el azulado de los efectos de faro. La radiacion no viene de un faro, asi
     * que el marco normal es lo coherente.
     */
    private static final boolean AMBIENTE = false;

    private static long contador = 0;

    private RadiationManager() {
    }

    public static void tick(MinecraftServer servidor) {
        long ranura = contador % INTERVALO_TICKS;
        contador++;

        if (!AtalayaConfig.get().isRadiacionActiva()) {
            return;
        }

        for (ServerPlayer jugador : servidor.getPlayerList().getPlayers()) {
            // Reparto: cada jugador cae siempre en la misma ranura.
            if (Math.floorMod(jugador.getId(), INTERVALO_TICKS) != ranura) {
                continue;
            }
            procesar(jugador);
        }
    }

    private static void procesar(ServerPlayer jugador) {
        // Creativo y espectador son inmunes.
        if (jugador.isCreative() || jugador.isSpectator()) {
            return;
        }

        ServerLevel nivel = jugador.level();
        double distancia = GeodeIndex.distanciaMasCercana(nivel, jugador.position(), DISTANCIA_MAXIMA);
        if (distancia < 0) {
            return; // fuera de alcance: el efecto se agota solo
        }

        int amplificador = nivelPorDistancia(distancia) - 1;

        // No reenviar el efecto si ya lo tiene igual y le queda cuerda de sobra.
        // Sin esto se manda un paquete por jugador y segundo aunque no cambie
        // nada; asi solo se manda cuando sube o baja de nivel o va a caducar.
        MobEffectInstance actual = jugador.getEffect(RadiacionEffect.RADIACION);
        if (actual != null
                && actual.getAmplifier() == amplificador
                && actual.getDuration() > INTERVALO_TICKS + 10) {
            return;
        }

        jugador.addEffect(new MobEffectInstance(
                RadiacionEffect.RADIACION,
                DURACION_TICKS,
                amplificador,
                AMBIENTE,
                false,  // sin particulas: molestan si estas mucho rato
                true    // mostrar icono en el HUD
        ));
    }

    /** 1 al borde del alcance, 4 pegado a la amatista. */
    private static int nivelPorDistancia(double distancia) {
        double proporcion = 1.0 - (distancia / DISTANCIA_MAXIMA);
        int nivel = (int) Math.ceil(proporcion * NIVEL_MAX);
        return Math.max(1, Math.min(NIVEL_MAX, nivel));
    }
}
