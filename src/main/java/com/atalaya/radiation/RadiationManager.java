package com.atalaya.radiation;

import com.atalaya.config.AtalayaConfig;
import com.atalaya.effect.RadiacionEffect;
import com.atalaya.item.HazmatArmor;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.entity.ai.attributes.AttributeInstance;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;

import java.util.List;

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
     * Por debajo de esta distancia el nivel ya es el maximo, asi que encontrar
     * una amatista aun mas cerca no cambiaria el resultado: el indice puede
     * dejar de buscar ahi.
     *
     * Sale de la propia formula de {@link #nivelPorDistancia}: el nivel 4 pide
     * que la proporcion pase de 0.75, o sea distancia menor que un cuarto del
     * alcance. Se calcula en vez de escribir "3.0" para que siga cuadrando si
     * se tocan el alcance o el numero de niveles.
     */
    private static final double DISTANCIA_NIVEL_MAX = DISTANCIA_MAXIMA / NIVEL_MAX;

    /**
     * El efecto dura mas que el intervalo a proposito: asi no parpadea el icono
     * entre una comprobacion y la siguiente.
     */
    private static final int DURACION_TICKS = 600;

    /**
     * Por debajo de esta cuerda se renueva.
     *
     * Los dos numeros salen de un detalle de vanilla: el HUD desvanece el icono
     * de cualquier efecto al que le queden 200 ticks o menos
     * ({@code Hud} llama a {@code endsWithin(200)}). Antes la cuerda era de 60
     * ticks, o sea que estaba SIEMPRE por debajo del umbral y el icono no paraba
     * de parpadear aunque el efecto se renovara sin cortes.
     *
     * Renovando en 400 sobre una cuerda de 600, el efecto nunca baja de 400 y
     * quedan 200 ticks de margen: aunque el reparto por ranuras se salte varias
     * vueltas seguidas, no llega a parpadear.
     */
    private static final int RENOVAR_BAJO = 400;

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

        List<ServerPlayer> jugadores = servidor.getPlayerList().getPlayers();
        int total = jugadores.size();
        if (total == 0) {
            return;
        }

        // Se recorre SOLO el tramo de esta ranura, no la lista entera.
        //
        // Antes se pasaba por los N jugadores cada tick para quedarse con los de
        // una ranura: con 100 conectados son 2000 vueltas por segundo, 1900 de
        // ellas para descartar. Repartiendo por indice se tocan 5 por tick y el
        // coste deja de crecer con el aforo del servidor.
        //
        // Cada jugador se sigue revisando una vez por intervalo. Al entrar o
        // salir alguien, la lista se desplaza y algun jugador puede repetir o
        // saltarse una vuelta; es inofensivo, porque el efecto dura 60 ticks y
        // se renueva en la siguiente.
        int desde = (int) (total * ranura / INTERVALO_TICKS);
        int hasta = (int) (total * (ranura + 1) / INTERVALO_TICKS);
        for (int i = desde; i < hasta; i++) {
            procesar(jugadores.get(i));
        }
    }

    private static void procesar(ServerPlayer jugador) {
        aplicarRadiacion(jugador);
        // Va DESPUES y siempre, incluso para quien esta fuera de alcance: es lo
        // que RETIRA la compensacion a quien acaba de salir de la geoda. Si solo
        // se llamara dentro del alcance, el modificador de velocidad se quedaria
        // colgado para siempre al salir.
        ajustarAmortiguacion(jugador);
    }

    /**
     * Devuelve velocidad a quien lleva piezas con pata ligera.
     *
     * Se cuelga del jugador como modificador TEMPORAL: no se guarda en disco,
     * asi que no puede quedarse pegado si alguien se desconecta o muere dentro
     * de una geoda. Si el jugador no tiene radiacion o no lleva la mejora, se
     * retira.
     */
    private static void ajustarAmortiguacion(ServerPlayer jugador) {
        AttributeInstance velocidad = jugador.getAttribute(Attributes.MOVEMENT_SPEED);
        if (velocidad == null) {
            return;
        }

        MobEffectInstance radiacion = jugador.getEffect(RadiacionEffect.RADIACION);
        double compensacion = radiacion == null ? 0 : RadiacionEffect.compensacionPorAmortiguacion(
                radiacion.getAmplifier(), HazmatArmor.piezasAmortiguadas(jugador));

        if (compensacion <= 0) {
            // Se comprueba antes de quitar para no marcar el atributo como
            // "recalculame" cada segundo a los jugadores que no llevan la mejora,
            // que van a ser la mayoria.
            if (velocidad.getModifier(RadiacionEffect.ID_AMORTIGUACION) != null) {
                velocidad.removeModifier(RadiacionEffect.ID_AMORTIGUACION);
            }
            return;
        }

        velocidad.addOrUpdateTransientModifier(new AttributeModifier(
                RadiacionEffect.ID_AMORTIGUACION,
                compensacion,
                AttributeModifier.Operation.ADD_MULTIPLIED_TOTAL));
    }

    private static void aplicarRadiacion(ServerPlayer jugador) {
        // Creativo y espectador son inmunes.
        if (jugador.isCreative() || jugador.isSpectator()) {
            jugador.removeEffect(RadiacionEffect.RADIACION);
            return;
        }

        ServerLevel nivel = jugador.level();
        double distancia = GeodeIndex.distanciaMasCercana(
                nivel, jugador.position(), DISTANCIA_MAXIMA, DISTANCIA_NIVEL_MAX);
        if (distancia < 0) {
            // Fuera de alcance se retira A MANO, no se deja caducar. La cuerda
            // es larga a proposito para que el icono no parpadee, asi que
            // esperar a que se agote dejaria la radiacion puesta medio minuto
            // despues de haber salido de la geoda.
            jugador.removeEffect(RadiacionEffect.RADIACION);
            return;
        }

        int amplificador = nivelPorDistancia(distancia) - 1;

        // No reenviar el efecto si ya lo tiene igual y le queda cuerda de sobra.
        // Sin esto se manda un paquete por jugador y segundo aunque no cambie
        // nada; asi solo se manda cuando sube o baja de nivel o va a caducar.
        MobEffectInstance actual = jugador.getEffect(RadiacionEffect.RADIACION);
        if (actual != null
                && actual.getAmplifier() == amplificador
                && actual.getDuration() > RENOVAR_BAJO) {
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
