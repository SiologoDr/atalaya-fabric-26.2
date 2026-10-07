package com.atalaya.command;

import com.atalaya.config.AtalayaConfig;
import com.atalaya.effect.HipotermiaEffect;
import com.atalaya.entity.AtalayaEntities;
import com.atalaya.entity.AeralisEntity;
import com.atalaya.entity.NovilisEntity;
import com.atalaya.entity.RajangEntity;
import com.atalaya.entity.NereaEntity;
import com.mojang.brigadier.arguments.StringArgumentType;
import net.minecraft.commands.SharedSuggestionProvider;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;
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
import net.minecraft.commands.arguments.EntityArgument;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.item.ItemStack;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;

import java.util.Collection;
import java.util.List;

/**
 * Comando /atalaya.
 *
 * Subcomandos:
 *   /atalaya menu                 -> panel de interruptores
 *   /atalaya hidratacion &lt;0-100&gt;  -> fija tu hidratacion, para probar
 *   /atalaya frio &lt;0-50&gt;          -> fija tu frio, para probar
 *   /atalaya nerea &lt;orden&gt;         -> fuerza a la Nerea mas cercana un ataque o
 *                                    momento del combate (despertar, rompeolas,
 *                                    remolino, burbujas, molino, arpon, lejano,
 *                                    mirada, ojo, geiser, marea, furia, aturdido,
 *                                    agotado, fase, liberar).
 *                                    Nerea se invoca con su huevo generador.
 *   /atalaya aeralis &lt;orden&gt;       -> lo mismo con la Aeralis mas cercana (despertar,
 *                                    aleteo, tornados, caceria, rafaga, doble,
 *                                    juicio, aturdida, agotada, fase, liberar).
 *   /atalaya rajang &lt;orden&gt;        -> lo mismo con el Rajang mas cercano (despertar,
 *                                    perseguir, garra, terremoto, embestida, tumba,
 *                                    sello, romper, escalon, cataclismo, salto,
 *                                    aturdido, paralizado, estampado, furia, fase,
 *                                    liberar).
 *   /atalaya novilis &lt;orden&gt;       -> lo mismo con el Novilis mas cercano (despertar,
 *                                    barrido, castigo, onda, sol, trompetas, estatua,
 *                                    fuentes, fuente, ofrenda, dios, aturdido, furia,
 *                                    grito, fase, liberar).
 *
 *   /atalaya habilidad            -> lanza la habilidad de tu armadura, como la tecla R
 *   /repair [jugadores]           -> deja como nueva la armadura puesta (casco,
 *                                    peto o elitros, grebas y botas) tuya o de
 *                                    los jugadores que digas.
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
                        .then(Commands.literal("habilidad")
                                .requires(AtalayaCommand::esOperador)
                                .executes(ctx -> {
                                    // Lo mismo que pulsar la tecla de la habilidad (para probar).
                                    com.atalaya.habilidad.Habilidades.activar(ctx.getSource().getPlayerOrException());
                                    return 1;
                                }))
                        .then(Commands.literal("nerea")
                                .requires(AtalayaCommand::esOperador)
                                .then(Commands.argument("orden", StringArgumentType.word())
                                        .suggests((ctx, sb) -> SharedSuggestionProvider.suggest(ORDENES_NEREA, sb))
                                        .executes(ctx -> probarNerea(ctx.getSource(),
                                                StringArgumentType.getString(ctx, "orden")))))
                        .then(Commands.literal("aeralis")
                                .requires(AtalayaCommand::esOperador)
                                .then(Commands.argument("orden", StringArgumentType.word())
                                        .suggests((ctx, sb) -> SharedSuggestionProvider.suggest(ORDENES_AERALIS, sb))
                                        .executes(ctx -> probarAeralis(ctx.getSource(),
                                                StringArgumentType.getString(ctx, "orden")))))
                        .then(Commands.literal("rajang")
                                .requires(AtalayaCommand::esOperador)
                                .then(Commands.argument("orden", StringArgumentType.word())
                                        .suggests((ctx, sb) -> SharedSuggestionProvider.suggest(ORDENES_RAJANG, sb))
                                        .executes(ctx -> probarRajang(ctx.getSource(),
                                                StringArgumentType.getString(ctx, "orden")))))
                        .then(Commands.literal("novilis")
                                .requires(AtalayaCommand::esOperador)
                                .then(Commands.argument("orden", StringArgumentType.word())
                                        .suggests((ctx, sb) -> SharedSuggestionProvider.suggest(ORDENES_NOVILIS, sb))
                                        .executes(ctx -> probarNovilis(ctx.getSource(),
                                                StringArgumentType.getString(ctx, "orden")))))
                        .then(Commands.literal("frio")
                                .requires(AtalayaCommand::esOperador)
                                .then(Commands.argument("puntos",
                                                IntegerArgumentType.integer(0, Frio.MAXIMO))
                                        .executes(ctx -> fijarFrio(ctx.getSource(),
                                                IntegerArgumentType.getInteger(ctx, "puntos")))))
        );
        dispatcher.register(
                Commands.literal("repair")
                        .requires(AtalayaCommand::esOperador)
                        .executes(ctx -> reparar(ctx.getSource(), List.of(ctx.getSource().getPlayerOrException())))
                        .then(Commands.argument("jugadores", EntityArgument.players())
                                .executes(ctx -> reparar(ctx.getSource(), EntityArgument.getPlayers(ctx, "jugadores"))))
        );
    }

    private static final EquipmentSlot[] ARMADURA = {EquipmentSlot.HEAD, EquipmentSlot.CHEST, EquipmentSlot.LEGS, EquipmentSlot.FEET};

    /** Repara la armadura que lleva puesta cada jugador (lo que no tiene durabilidad se deja). */
    private static int reparar(CommandSourceStack fuente, Collection<ServerPlayer> jugadores) {
        int piezas = 0;
        for (ServerPlayer jugador : jugadores) {
            for (EquipmentSlot hueco : ARMADURA) {
                ItemStack pieza = jugador.getItemBySlot(hueco);
                if (!pieza.isEmpty() && pieza.isDamageableItem() && pieza.isDamaged()) {
                    pieza.setDamageValue(0);
                    piezas++;
                }
            }
        }
        int reparadas = piezas;
        String quien = jugadores.size() == 1 ? jugadores.iterator().next().getName().getString() : jugadores.size() + " jugadores";
        fuente.sendSuccess(() -> Component.literal("Armadura reparada (" + quien + "): " + reparadas
                + (reparadas == 1 ? " pieza." : " piezas.")), true);
        return reparadas;
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

    private static final String[] ORDENES_NEREA = {"despertar", "rompeolas", "remolino", "burbujas", "molino",
            "arpon", "lejano", "mirada", "ojo", "geiser", "marea", "furia", "aturdido", "agotado", "fase", "canto", "clic", "cadenas", "marea_alta", "liberar"};

    /** Fuerza a la Nerea mas cercana (en 64 bloques) a hacer algo ya. */
    private static int probarNerea(CommandSourceStack fuente, String orden) {
        ServerLevel nivel = fuente.getLevel();
        Vec3 desde = fuente.getPosition();
        NereaEntity nerea = null;
        double mejor = 64 * 64;
        for (NereaEntity n : nivel.getEntitiesOfClass(NereaEntity.class, new AABB(desde, desde).inflate(64))) {
            if (n.isAlive() && n.distanceToSqr(desde) < mejor) {
                mejor = n.distanceToSqr(desde);
                nerea = n;
            }
        }
        if (nerea == null) {
            fuente.sendFailure(Component.literal("No hay ninguna Nerea a menos de 64 bloques."));
            return 0;
        }
        if (!nerea.forzar(nivel, orden)) {
            fuente.sendFailure(Component.literal("Orden desconocida: " + orden));
            return 0;
        }
        fuente.sendSuccess(() -> Component.literal("Nerea: " + orden), false);
        return 1;
    }

    private static final String[] ORDENES_NOVILIS = {"despertar", "barrido", "castigo", "onda", "sol", "trompetas",
            "estatua", "fuentes", "fuente", "ofrenda", "dios", "aturdido", "furia", "grito", "fase", "liberar", "perseguir"};

    /** Fuerza al Novilis mas cercano (en 80 bloques) a hacer algo ya. */
    private static int probarNovilis(CommandSourceStack fuente, String orden) {
        ServerLevel nivel = fuente.getLevel();
        Vec3 desde = fuente.getPosition();
        NovilisEntity novilis = null;
        double mejor = 80 * 80;
        for (NovilisEntity n : nivel.getEntitiesOfClass(NovilisEntity.class, new AABB(desde, desde).inflate(80))) {
            if (n.isAlive() && n.distanceToSqr(desde) < mejor) {
                mejor = n.distanceToSqr(desde);
                novilis = n;
            }
        }
        if (novilis == null) {
            fuente.sendFailure(Component.literal("No hay ningun Novilis a menos de 80 bloques."));
            return 0;
        }
        if (!novilis.forzar(nivel, orden)) {
            fuente.sendFailure(Component.literal("Orden desconocida: " + orden));
            return 0;
        }
        fuente.sendSuccess(() -> Component.literal("Novilis: " + orden), false);
        return 1;
    }

    private static final String[] ORDENES_RAJANG = {"despertar", "perseguir", "garra", "terremoto", "embestida", "tumba", "anillo", "idolo",
            "sello", "romper", "escalon", "cataclismo", "salto", "aturdido", "paralizado", "estampado", "furia", "fase",
            "liberar"};

    /** Fuerza al Rajang mas cercano (en 80 bloques) a hacer algo ya. */
    private static int probarRajang(CommandSourceStack fuente, String orden) {
        ServerLevel nivel = fuente.getLevel();
        Vec3 desde = fuente.getPosition();
        RajangEntity rajang = null;
        double mejor = 80 * 80;
        for (RajangEntity r : nivel.getEntitiesOfClass(RajangEntity.class, new AABB(desde, desde).inflate(80))) {
            if (r.isAlive() && r.distanceToSqr(desde) < mejor) {
                mejor = r.distanceToSqr(desde);
                rajang = r;
            }
        }
        if (rajang == null) {
            fuente.sendFailure(Component.literal("No hay ningun Rajang a menos de 80 bloques."));
            return 0;
        }
        if (!rajang.forzar(nivel, orden)) {
            fuente.sendFailure(Component.literal("Orden desconocida: " + orden));
            return 0;
        }
        fuente.sendSuccess(() -> Component.literal("Rajang: " + orden), false);
        return 1;
    }

    private static final String[] ORDENES_AERALIS = {"despertar", "aleteo", "tornados", "caceria", "rafaga", "doble",
            "juicio", "picado", "posada", "escamas", "rasante", "romper", "viento", "mancha", "nucleo", "furia", "aturdida", "agotada", "fase", "liberar"};

    /** Fuerza a la Aeralis mas cercana (en 80 bloques) a hacer algo ya. */
    private static int probarAeralis(CommandSourceStack fuente, String orden) {
        ServerLevel nivel = fuente.getLevel();
        Vec3 desde = fuente.getPosition();
        AeralisEntity aeralis = null;
        double mejor = 80 * 80;
        for (AeralisEntity a : nivel.getEntitiesOfClass(AeralisEntity.class, new AABB(desde, desde).inflate(80))) {
            if (a.isAlive() && a.distanceToSqr(desde) < mejor) {
                mejor = a.distanceToSqr(desde);
                aeralis = a;
            }
        }
        if (aeralis == null) {
            fuente.sendFailure(Component.literal("No hay ninguna Aeralis a menos de 80 bloques."));
            return 0;
        }
        if (!aeralis.forzar(nivel, orden)) {
            fuente.sendFailure(Component.literal("Orden desconocida: " + orden));
            return 0;
        }
        fuente.sendSuccess(() -> Component.literal("Aeralis: " + orden), false);
        return 1;
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
