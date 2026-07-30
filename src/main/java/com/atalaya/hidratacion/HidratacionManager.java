package com.atalaya.hidratacion;

import com.atalaya.config.AtalayaConfig;
import net.fabricmc.fabric.api.tag.convention.v2.ConventionalBiomeTags;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;

import java.util.List;

/**
 * Gasta la hidratacion de quien esta en el desierto.
 *
 * Reparte a los jugadores en ranuras igual que hace RadiationManager, pero aqui
 * el reparto sale gratis: como cada jugador debe perder un punto cada
 * {@link Hidratacion#TICKS_POR_PUNTO} ticks, basta con que el intervalo del
 * reparto SEA ese mismo numero. Cada jugador cae en una ranura, se le procesa
 * una vez por vuelta y se le quita un punto. Ni contadores por jugador ni un
 * pico cada siete segundos con todo el servidor a la vez.
 */
public final class HidratacionManager {

    private static long contador = 0;

    private HidratacionManager() {
    }

    public static void tick(MinecraftServer servidor) {
        long ranura = contador % Hidratacion.TICKS_POR_PUNTO;
        contador++;

        if (!AtalayaConfig.get().isHidratacionActiva()) {
            return;
        }

        List<ServerPlayer> jugadores = servidor.getPlayerList().getPlayers();
        int total = jugadores.size();
        if (total == 0) {
            return;
        }

        // Solo el tramo de esta ranura. Con el intervalo en 140 ticks y pocos
        // jugadores, la mayoria de ticks no tocan a nadie y el bucle sale
        // enseguida.
        //
        // Al entrar o salir alguien la lista se desplaza y algun jugador puede
        // repetir vuelta o saltarsela. Aqui eso es un punto de mas o de menos
        // muy de vez en cuando, sobre un deposito de cien: no merece la pena
        // llevar un contador por jugador para arreglarlo.
        int desde = (int) (total * ranura / Hidratacion.TICKS_POR_PUNTO);
        int hasta = (int) (total * (ranura + 1) / Hidratacion.TICKS_POR_PUNTO);
        for (int i = desde; i < hasta; i++) {
            procesar(jugadores.get(i));
        }
    }

    private static void procesar(ServerPlayer jugador) {
        // Creativo y espectador no se deshidratan, igual que son inmunes a la
        // radiacion.
        if (jugador.isCreative() || jugador.isSpectator()) {
            return;
        }
        if (!enDesierto(jugador)) {
            return; // fuera de la arena el nivel se queda como esta
        }

        int actual = Hidratacion.de(jugador);
        if (actual <= 0) {
            // Vacio. Por ahora no pasa nada mas: el item que rellena y lo que
            // ocurra al llegar a cero son el siguiente paso.
            return;
        }
        Hidratacion.poner(jugador, actual - 1);
    }

    /**
     * Si el jugador pisa un bioma de desierto.
     *
     * Se pregunta por la etiqueta de convencion y no por el bioma concreto de
     * vanilla, asi que los desiertos que anadan otros mods cuentan solos, sin
     * tocar nada aqui.
     */
    public static boolean enDesierto(Player jugador) {
        Level nivel = jugador.level();
        return nivel.getBiome(jugador.blockPosition()).is(ConventionalBiomeTags.IS_DESERT);
    }
}
