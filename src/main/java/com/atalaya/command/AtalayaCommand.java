package com.atalaya.command;

import com.atalaya.config.AtalayaConfig;
import com.atalaya.effect.HipotermiaEffect;
import com.atalaya.entity.AtalayaEntities;
import net.fabricmc.fabric.api.tag.convention.v2.ConventionalBiomeTags;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Holder;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.EntitySpawnReason;
import net.minecraft.world.entity.MobCategory;
import net.minecraft.world.entity.SpawnPlacements;
import net.minecraft.world.level.LightLayer;
import net.minecraft.world.level.biome.Biome;
import com.atalaya.effect.InsolacionEffect;
import com.atalaya.frio.Frio;
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
 *   /atalaya frio &lt;0-50&gt;          -> fija tu frio, para probar
 *
 * Todos piden permiso de operador.
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
                        .then(Commands.literal("diagnostico")
                                .requires(AtalayaCommand::esOperador)
                                .executes(ctx -> diagnostico(ctx.getSource())))
                        .then(Commands.literal("frio")
                                .requires(AtalayaCommand::esOperador)
                                .then(Commands.argument("puntos",
                                                IntegerArgumentType.integer(0, Frio.MAXIMO))
                                        .executes(ctx -> fijarFrio(ctx.getSource(),
                                                IntegerArgumentType.getInteger(ctx, "puntos")))))
        );
    }

    /**
     * Dice por que no aparece el fulminante donde estas.
     *
     * Son cuatro cosas que tienen que cumplirse a la vez, y desde dentro del
     * juego no hay forma de ver ninguna. Preguntarlas de una en una a base de
     * esperar noches enteras no es manera.
     */
    private static int diagnostico(CommandSourceStack fuente) {
        ServerPlayer jugador = fuente.getPlayer();
        if (jugador == null) {
            fuente.sendFailure(Component.literal("Hace falta estar en el mundo."));
            return 0;
        }
        ServerLevel nivel = jugador.level();
        BlockPos pos = jugador.blockPosition();
        Holder<Biome> bioma = nivel.getBiome(pos);

        StringBuilder sb = new StringBuilder();
        sb.append("\n--- fulminante aqui ---");
        sb.append("\n interruptor: ")
          .append(AtalayaConfig.get().isFulminanteActivo() ? "ENCENDIDO" : "APAGADO");
        sb.append("\n bioma: ").append(bioma.getRegisteredName());
        sb.append("\n  es desierto: ").append(bioma.is(ConventionalBiomeTags.IS_DESERT));

        // Lo que de verdad decide: si el bicho esta en la lista del bioma
        int peso = -1;
        for (var entrada : bioma.value().getMobSettings().getMobs(MobCategory.MONSTER).unwrap()) {
            if (entrada.value().type() == AtalayaEntities.FULMINANTE) {
                peso = entrada.weight();
            }
        }
        sb.append("\n  en la lista de monstruos: ")
          .append(peso >= 0 ? ("SI, peso " + peso) : "NO");

        sb.append("\n luz de bloque: ").append(
                nivel.getLightEngine().getLayerListener(LightLayer.BLOCK).getLightValue(pos));
        sb.append("\n regla de sitio: ").append(
                SpawnPlacements.checkSpawnRules(AtalayaEntities.FULMINANTE, nivel,
                        EntitySpawnReason.NATURAL, pos, nivel.getRandom()));

        String texto = sb.toString();
        fuente.sendSuccess(() -> Component.literal(texto), false);
        return 1;
    }

    /**
     * Fija el frio del que lo escribe. Misma razon que el de hidratacion:
     * helarse del todo a la intemperie son casi seis minutos de espera.
     */
    private static int fijarFrio(CommandSourceStack fuente, int puntos) {
        ServerPlayer jugador = fuente.getPlayer();
        if (jugador == null) {
            fuente.sendFailure(Component.literal("Solo un jugador pasa frio."));
            return 0;
        }
        Frio.poner(jugador, puntos);
        boolean encendida = AtalayaConfig.get().isFrioActivo();
        int nivel = HipotermiaEffect.nivelPorFrio(puntos);
        fuente.sendSuccess(() -> Component.literal(
                "Frio: " + puntos + " / " + Frio.MAXIMO
                        + (!encendida ? "  (mecanica APAGADA, no se aplica nada)"
                           : nivel > 0 ? "  (hipotermia nivel " + nivel + ")"
                           : "  (sin hipotermia)")), false);
        return puntos;
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
        // Si la mecanica esta apagada hay que DECIRLO. Antes se anunciaba el
        // nivel que tocaria por esos puntos aunque no fuera a aplicarse nada, y
        // eso hace perder el tiempo buscando un fallo donde no lo hay.
        boolean encendida = AtalayaConfig.get().isHidratacionActiva();
        int nivel = InsolacionEffect.nivelPorHidratacion(puntos);
        fuente.sendSuccess(() -> Component.literal(
                "Hidratacion: " + puntos + " / " + Hidratacion.MAXIMO
                        + (!encendida ? "  (mecanica APAGADA, no se aplica nada)"
                           : nivel > 0 ? "  (insolacion nivel " + nivel + ")"
                           : "  (sin insolacion)")), false);
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
