package com.atalaya.command;

import com.atalaya.effect.InsolacionEffect;
import com.atalaya.hidratacion.Hidratacion;
import com.atalaya.menu.ConfigMenu;
import com.mojang.brigadier.CommandDispatcher;
import com.mojang.brigadier.arguments.IntegerArgumentType;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.Commands;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;

/**
 * Comando /atalaya.
 *
 * Subcomandos:
 *   /atalaya menu                 -> panel de interruptores
 *   /atalaya hidratacion &lt;0-100&gt;  -> fija tu hidratacion, para probar
 *
 * Los dos piden permiso de operador.
 *
 * El traje se consigue crafteandolo o desde la pestana de Combate en creativo,
 * asi que no hace falta un comando para darlo.
 */
public final class AtalayaCommand {

    private AtalayaCommand() {
    }

    public static void registrar(CommandDispatcher<CommandSourceStack> dispatcher) {
        dispatcher.register(
                Commands.literal("atalaya")
                        .then(Commands.literal("menu")
                                .requires(AtalayaCommand::esOperador)
                                .executes(ctx -> abrirMenu(ctx.getSource())))
                        .then(Commands.literal("hidratacion")
                                .requires(AtalayaCommand::esOperador)
                                .then(Commands.argument("puntos",
                                                IntegerArgumentType.integer(0, Hidratacion.MAXIMO))
                                        .executes(ctx -> fijarHidratacion(ctx.getSource(),
                                                IntegerArgumentType.getInteger(ctx, "puntos")))))
        );
    }

    /**
     * Fija la hidratacion del que lo escribe.
     *
     * Es para probar: llegar al nivel 4 de insolacion esperando en la arena son
     * casi doce minutos, y ajustar los numeros de la tabla a base de esperas asi
     * no es viable. Poner 9 puntos deja el nivel 3 al instante.
     */
    private static int fijarHidratacion(CommandSourceStack fuente, int puntos) {
        ServerPlayer jugador = fuente.getPlayer();
        if (jugador == null) {
            fuente.sendFailure(Component.literal("Solo un jugador tiene hidratacion."));
            return 0;
        }
        Hidratacion.poner(jugador, puntos);
        int nivel = InsolacionEffect.nivelPorHidratacion(puntos);
        fuente.sendSuccess(() -> Component.literal(
                "Hidratacion: " + puntos + " / " + Hidratacion.MAXIMO
                        + (nivel > 0 ? "  (insolacion nivel " + nivel + ")" : "  (sin insolacion)")), false);
        return puntos;
    }

    /**
     * Solo operadores. En 26.2 los niveles enteros (hasPermission(2)) ya no
     * existen: se comprueba con un PermissionCheck contra los permisos de la fuente.
     */
    private static boolean esOperador(CommandSourceStack fuente) {
        return Commands.LEVEL_GAMEMASTERS.check(fuente.permissions());
    }

    private static int abrirMenu(CommandSourceStack fuente) {
        ServerPlayer jugador = fuente.getPlayer();
        if (jugador == null) {
            fuente.sendFailure(Component.literal("Solo un jugador puede abrir el menu."));
            return 0;
        }
        ConfigMenu.abrir(jugador);
        return 1;
    }
}
