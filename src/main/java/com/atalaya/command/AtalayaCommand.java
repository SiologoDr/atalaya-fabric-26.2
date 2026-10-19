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
import com.mojang.brigadier.builder.LiteralArgumentBuilder;
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
 *   /atalaya menu cambios         -> el menu de los cambios de dificultad (encender uno lanza la Ruleta y se aplica al
 *                                    salir su aviso; apagarlo lo quita al momento)
 *   /atalaya menu dimensiones     -> el menu de las dimensiones: el Nether y el End, abiertos o cerrados
 *   /atalaya hidratacion &lt;0-100&gt;  -> fija tu hidratacion, para probar
 *   /atalaya frio &lt;0-50&gt;          -> fija tu frio, para probar
 *   /atalaya momento_fractura "titulo" "texto" [segundos]
 *                                 -> el Momento Fractura para todos (con segundos, se para solo);
 *                                    tambien vale momento_maldicion, su nombre de antes
 *   /atalaya momento_fractura prueba tierra <segundos> [cantidad]
 *                                 -> la prueba: romper tierra o cesped (10 si no se dice) antes de que el
 *                                    contador llegue a cero; a quien no, lo mata (aunque tenga totems)
 *   /atalaya momento_fractura stop -> lo para
 *   /atalaya ruleta &lt;final&gt; [texto]
 *                                 -> la Ruleta para todos: la tragaperras gira y para en su final (mob,
 *                                    dificultad, penalizacion o minijuego) y el texto sale en el chat del
 *                                    color del final; si hay otra girando, espera su turno
 *   /atalaya ruleta stop          -> quita la que gira y las que esperan
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
 *                                    barrido, castigo, onda, sol, espada, trompetas,
 *                                    estatua, sombra, infernal, ofrenda, mar, dios,
 *                                    aturdido, furia, perseguir, fase, liberar).
 *
 *   /atalaya habilidad            -> lanza la habilidad de tu armadura, como la tecla R
 *   /atalaya habilidad lista      -> te la deja lista ya (sin recarga), para probar
 *   /repair [jugadores]           -> deja como nueva la armadura puesta (casco,
 *                                    peto o elitros, grebas y botas) tuya o de
 *                                    los jugadores que digas.
 *
 * Todos piden permiso de operador.
 *
 * El traje se consigue crafteandolo o desde la pestana Atalaya en creativo,
 * asi que no hace falta un comando para darlo.
 */
public final class AtalayaCommand {

    private AtalayaCommand() {
    }

    public static void registrar(CommandDispatcher<CommandSourceStack> dispatcher) {
        dispatcher.register(
                Commands.literal("atalaya")
                        // Encender o apagar un cambio de dificultad al momento, sin la Ruleta (para probar y para
                        // arreglar): /atalaya cambio <id> on|off. Sin on/off, dice si esta encendido.
                        .then(Commands.literal("cambio")
                                .requires(AtalayaCommand::esOperador)
                                .then(Commands.argument("id", StringArgumentType.word())
                                        .suggests((ctx, b) -> net.minecraft.commands.SharedSuggestionProvider.suggest(
                                                java.util.Arrays.stream(com.atalaya.cambios.Cambio.values()).map(c -> c.id), b))
                                        .executes(ctx -> cambioDirecto(ctx.getSource(), StringArgumentType.getString(ctx, "id"), null))
                                        .then(Commands.literal("on")
                                                .executes(ctx -> cambioDirecto(ctx.getSource(), StringArgumentType.getString(ctx, "id"), true)))
                                        .then(Commands.literal("off")
                                                .executes(ctx -> cambioDirecto(ctx.getSource(), StringArgumentType.getString(ctx, "id"), false)))))
                        // Soltar o recoger un mob del bestiario al momento, sin la Ruleta: /atalaya mob <id> on|off.
                        .then(Commands.literal("mob")
                                .requires(AtalayaCommand::esOperador)
                                .then(Commands.argument("id", StringArgumentType.word())
                                        .suggests((ctx, b) -> net.minecraft.commands.SharedSuggestionProvider.suggest(
                                                com.atalaya.bestiario.Bestias.todas().stream().map(x -> x.id()), b))
                                        .then(Commands.literal("on")
                                                .executes(ctx -> mobDirecto(ctx.getSource(), StringArgumentType.getString(ctx, "id"), true)))
                                        .then(Commands.literal("off")
                                                .executes(ctx -> mobDirecto(ctx.getSource(), StringArgumentType.getString(ctx, "id"), false)))))
                        .then(Commands.literal("menu")
                                .requires(AtalayaCommand::esOperador)
                                .executes(ctx -> abrirMenu(ctx.getSource()))
                                .then(Commands.literal("cambios")
                                        .executes(ctx -> abrirMenuCatalogo(ctx.getSource(), com.atalaya.catalogo.Categoria.CAMBIO)))
                                .then(Commands.literal("mobs")
                                        .executes(ctx -> abrirMenuCatalogo(ctx.getSource(), com.atalaya.catalogo.Categoria.MOB)))
                                .then(Commands.literal("momentos")
                                        .executes(ctx -> abrirMenuCatalogo(ctx.getSource(), com.atalaya.catalogo.Categoria.MOMENTO)))
                                .then(Commands.literal("dimensiones")
                                        .executes(ctx -> abrirMenuCatalogo(ctx.getSource(), null))))
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
                                })
                                .then(Commands.literal("lista")
                                        .executes(ctx -> {
                                            // Para probar: la deja lista ya (sin recarga ni activa en marcha).
                                            ctx.getSource().getPlayerOrException().setAttached(com.atalaya.habilidad.Habilidades.ESTADO,
                                                    com.atalaya.habilidad.HabilidadEstado.NADA);
                                            return 1;
                                        })))
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
                        .then(Commands.literal("minijefe")
                                .requires(AtalayaCommand::esOperador)
                                .then(Commands.argument("orden", StringArgumentType.word())
                                        .suggests((ctx, sb) -> SharedSuggestionProvider.suggest(ORDENES_MINIJEFE, sb))
                                        .executes(ctx -> probarMiniJefe(ctx.getSource(),
                                                StringArgumentType.getString(ctx, "orden")))))
                        .then(Commands.literal("novilis")
                                .requires(AtalayaCommand::esOperador)
                                .then(Commands.argument("orden", StringArgumentType.word())
                                        .suggests((ctx, sb) -> SharedSuggestionProvider.suggest(ORDENES_NOVILIS, sb))
                                        .executes(ctx -> probarNovilis(ctx.getSource(),
                                                StringArgumentType.getString(ctx, "orden")))))
                        // Un momento del catalogo, sin pasar por el menu (para probar): /atalaya momento <id> [rapido].
                        // Rapido acorta los contadores veinte veces (solo para las pruebas).
                        .then(Commands.literal("momento")
                                .requires(AtalayaCommand::esOperador)
                                .then(Commands.argument("id", StringArgumentType.word())
                                        .suggests((ctx, b) -> net.minecraft.commands.SharedSuggestionProvider.suggest(
                                                java.util.Arrays.stream(com.atalaya.momento.Momento.values()).map(m -> m.id()), b))
                                        .executes(ctx -> momentoDirecto(ctx.getSource(), StringArgumentType.getString(ctx, "id"), false))
                                        .then(Commands.literal("rapido")
                                                .executes(ctx -> momentoDirecto(ctx.getSource(), StringArgumentType.getString(ctx, "id"), true)))))
                        .then(ordenMomento("momento_fractura"))
                        .then(ordenMomento("momento_maldicion"))
                        .then(ordenRuleta())
                        .then(com.atalaya.limbo.Limbo.orden())
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

    /**
     * La orden del momento: momento_fractura (el nombre que se ve: el chat dice MOMENTO FRACTURA) y momento_maldicion
     * (el de antes), las dos iguales.
     */
    private static LiteralArgumentBuilder<CommandSourceStack> ordenMomento(String nombre) {
        return Commands.literal(nombre)
                .requires(AtalayaCommand::esOperador)
                .executes(ctx -> estadoMomento(ctx.getSource()))
                .then(Commands.literal("stop")
                        .executes(ctx -> pararMomento(ctx.getSource())))
                .then(Commands.literal("prueba")
                        .then(Commands.literal("tierra")
                                .then(Commands.argument("segundos", IntegerArgumentType.integer(5, 3600))
                                        .executes(ctx -> pruebaTierra(ctx.getSource(),
                                                IntegerArgumentType.getInteger(ctx, "segundos"), 10))
                                        .then(Commands.argument("cantidad", IntegerArgumentType.integer(1, 640))
                                                .executes(ctx -> pruebaTierra(ctx.getSource(),
                                                        IntegerArgumentType.getInteger(ctx, "segundos"),
                                                        IntegerArgumentType.getInteger(ctx, "cantidad")))))))
                .then(Commands.argument("titulo", StringArgumentType.string())
                        .then(Commands.argument("texto", StringArgumentType.string())
                                .executes(ctx -> empezarMomento(ctx.getSource(),
                                        StringArgumentType.getString(ctx, "titulo"),
                                        StringArgumentType.getString(ctx, "texto"), 0))
                                .then(Commands.argument("segundos", IntegerArgumentType.integer(1, 86400))
                                        .executes(ctx -> empezarMomento(ctx.getSource(),
                                                StringArgumentType.getString(ctx, "titulo"),
                                                StringArgumentType.getString(ctx, "texto"),
                                                IntegerArgumentType.getInteger(ctx, "segundos"))))));
    }

    private static int empezarMomento(CommandSourceStack fuente, String titulo, String texto, int segundos) {
        if (titulo.isBlank()) {
            fuente.sendFailure(Component.literal("El titulo no puede ir vacio."));
            return 0;
        }
        com.atalaya.momento.MomentoMaldicion.empezar(fuente.getServer(), titulo, texto, segundos);
        fuente.sendSuccess(() -> Component.literal("Momento fractura: «" + titulo + "»"
                + (segundos > 0 ? " durante " + segundos + " s." : ", hasta /atalaya momento_fractura stop.")), true);
        return 1;
    }

    private static int pruebaTierra(CommandSourceStack fuente, int segundos, int cantidad) {
        com.atalaya.momento.MomentoMaldicion.empezarPruebaTierra(fuente.getServer(), segundos, cantidad);
        fuente.sendSuccess(() -> Component.literal("Momento fractura, prueba de la tierra: " + cantidad
                + " bloques en " + segundos + " s (el contador empieza al acabar la cinematica)."), true);
        return 1;
    }

    private static int pararMomento(CommandSourceStack fuente) {
        if (!com.atalaya.momento.MomentoMaldicion.parar()) {
            fuente.sendFailure(Component.literal("No hay ningun momento fractura en marcha."));
            return 0;
        }
        fuente.sendSuccess(() -> Component.literal("Momento fractura parado."), true);
        return 1;
    }

    private static int estadoMomento(CommandSourceStack fuente) {
        if (!com.atalaya.momento.MomentoMaldicion.activo()) {
            fuente.sendSuccess(() -> Component.literal(
                    "Uso: /atalaya momento_fractura \"titulo\" \"texto\" [segundos]  ·  /atalaya momento_fractura stop"), false);
            return 0;
        }
        int queda = com.atalaya.momento.MomentoMaldicion.queda();
        fuente.sendSuccess(() -> Component.literal("En marcha: «" + com.atalaya.momento.MomentoMaldicion.titulo() + "»"
                + (queda >= 0 ? ", quedan " + queda / 20 + " s." : ", sin limite.")), false);
        return 1;
    }

    /**
     * La Ruleta: /atalaya ruleta &lt;final&gt; [texto] (el texto sin comillas, o con ellas) y /atalaya ruleta stop.
     */
    private static LiteralArgumentBuilder<CommandSourceStack> ordenRuleta() {
        LiteralArgumentBuilder<CommandSourceStack> raiz = Commands.literal("ruleta")
                .requires(AtalayaCommand::esOperador)
                .executes(ctx -> {
                    ctx.getSource().sendSuccess(() -> Component.literal(
                            "Uso: /atalaya ruleta <mob|dificultad|penalizacion|minijuego> [texto]  ·  /atalaya ruleta stop"), false);
                    return 0;
                })
                .then(Commands.literal("stop")
                        .executes(ctx -> pararRuleta(ctx.getSource())));
        for (com.atalaya.momento.Ruleta.Fin fin : com.atalaya.momento.Ruleta.Fin.values()) {
            raiz.then(Commands.literal(fin.nombre)
                    .executes(ctx -> tirarRuleta(ctx.getSource(), fin, ""))
                    .then(Commands.argument("texto", StringArgumentType.greedyString())
                            .executes(ctx -> tirarRuleta(ctx.getSource(), fin, StringArgumentType.getString(ctx, "texto")))));
        }
        return raiz;
    }

    private static int tirarRuleta(CommandSourceStack fuente, com.atalaya.momento.Ruleta.Fin fin, String texto) {
        String t = texto.strip();
        if (t.length() >= 2 && t.startsWith("\"") && t.endsWith("\"")) {
            t = t.substring(1, t.length() - 1);
        }
        int delante = com.atalaya.momento.Ruleta.tirar(fuente.getServer(), fin, t);
        fuente.sendSuccess(() -> Component.literal("Ruleta: " + fin.dicho
                + (delante > 0 ? " (espera su turno: " + delante + " delante)." : ".")), true);
        return 1;
    }

    private static int pararRuleta(CommandSourceStack fuente) {
        int habia = com.atalaya.momento.Ruleta.parar(fuente.getServer());
        if (habia == 0) {
            fuente.sendFailure(Component.literal("No hay ninguna ruleta girando."));
            return 0;
        }
        fuente.sendSuccess(() -> Component.literal("Ruleta parada" + (habia > 1 ? " (y la cola vacia)." : ".")), true);
        return 1;
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
            "arpon", "lejano", "mirada", "ojo", "geiser", "marea", "furia", "aturdido", "agotado", "fase", "canto", "clic", "cadenas", "marea_alta", "pesca", "cana", "cana_auto", "perla", "canones", "canon", "cargar", "disparo", "bala", "morenas", "morena_ver", "duelo", "duelo_bien", "liberar"};

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

    private static final String[] ORDENES_MINIJEFE = {"despertar", "normal", "area", "especial", "dormir", "libre", "morir"};

    /** Fuerza al mini jefe mas cercano (en 80 bloques) a hacer algo ya. */
    private static int probarMiniJefe(CommandSourceStack fuente, String orden) {
        ServerLevel nivel = fuente.getLevel();
        Vec3 desde = fuente.getPosition();
        com.atalaya.entity.MiniJefeEntity mini = null;
        double mejor = 80 * 80;
        for (com.atalaya.entity.MiniJefeEntity m : nivel.getEntitiesOfClass(com.atalaya.entity.MiniJefeEntity.class,
                new AABB(desde, desde).inflate(80))) {
            if (m.isAlive() && m.distanceToSqr(desde) < mejor) {
                mejor = m.distanceToSqr(desde);
                mini = m;
            }
        }
        if (mini == null) {
            fuente.sendFailure(Component.literal("No hay ningun mini jefe a menos de 80 bloques."));
            return 0;
        }
        if (!mini.forzar(nivel, orden)) {
            fuente.sendFailure(Component.literal("Orden desconocida: " + orden));
            return 0;
        }
        String nombre = mini.getName().getString();
        fuente.sendSuccess(() -> Component.literal(nombre + ": " + orden), false);
        return 1;
    }

    private static final String[] ORDENES_NOVILIS = {"despertar", "barrido", "castigo", "onda", "sol", "espada", "trompetas",
            "sombra", "estatua", "infernal", "ofrenda", "mar", "dios", "aturdido", "furia", "fase", "liberar", "perseguir",
            "manda", "forja", "piedra", "caliente", "mini_bien", "mini_fin"};

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
            "prisma", "impostor", "glifos", "suelo", "mini_bien", "mini_fin", "liberar"};

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
            "juicio", "picado", "posada", "escamas", "rasante", "ladrona", "romper", "viento", "mancha", "nucleo", "furia", "aturdida", "agotada", "fase", "liberar",
            "ocelos", "veletas", "pararrayos", "chispa", "mini_bien", "mini_fin"};

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

    /** Los menus propios (pantallas del cliente): los del catalogo (una categoria) o, sin ella, el de las dimensiones. */
    private static int abrirMenuCatalogo(CommandSourceStack fuente, com.atalaya.catalogo.@org.jspecify.annotations.Nullable Categoria categoria) {
        ServerPlayer jugador = fuente.getPlayer();
        if (jugador == null) {
            fuente.sendFailure(Component.literal("Solo un jugador puede abrir el menu."));
            return 0;
        }
        if (categoria == null) {
            com.atalaya.cambios.CambiosDificultad.abrirDimensiones(jugador);
        } else {
            com.atalaya.catalogo.Catalogo.abrir(jugador, categoria);
        }
        return 1;
    }

    /** /atalaya momento: lanza ese momento del catalogo (rapido: con los contadores veinte veces mas cortos). */
    private static int momentoDirecto(CommandSourceStack fuente, String id, boolean rapido) {
        for (com.atalaya.momento.Momento m : com.atalaya.momento.Momento.values()) {
            if (m.id().equals(id)) {
                com.atalaya.momento.Momentos.prisa(rapido ? 0.05F : 1.0F);
                com.atalaya.momento.Momentos.lanzar(fuente.getServer(), m);
                fuente.sendSuccess(() -> Component.literal("Momento: " + m.titulo() + (rapido ? " (rápido)" : "")), true);
                return 1;
            }
        }
        fuente.sendFailure(Component.literal("No hay ningún momento «" + id + "»."));
        return 0;
    }

    /** /atalaya mob: suelta o recoge ese mob ya (sin Ruleta). */
    private static int mobDirecto(CommandSourceStack fuente, String id, boolean soltar) {
        com.atalaya.bestiario.Bestia b = com.atalaya.bestiario.Bestias.porId(id);
        if (b == null) {
            fuente.sendFailure(Component.literal("No hay ningún mob «" + id + "»."));
            return 0;
        }
        com.atalaya.bestiario.Bestiario.poner(fuente.getServer(), b, soltar);
        fuente.sendSuccess(() -> Component.literal(b.titulo() + ": " + (soltar ? "suelto" : "recogido")), true);
        return 1;
    }

    /** /atalaya cambio: lo enciende o lo apaga ya (sin Ruleta), o dice como esta. */
    private static int cambioDirecto(CommandSourceStack fuente, String id, @org.jspecify.annotations.Nullable Boolean encender) {
        com.atalaya.cambios.Cambio c = com.atalaya.cambios.Cambio.porId(id);
        if (c == null) {
            fuente.sendFailure(Component.literal("No hay ningún cambio «" + id + "»."));
            return 0;
        }
        boolean esta = com.atalaya.cambios.CambiosDificultad.activo(c);
        if (encender == null) {
            fuente.sendSuccess(() -> Component.literal(c.titulo + ": " + (esta ? "ON" : "OFF")), false);
            return esta ? 1 : 0;
        }
        if (encender && !esta) {
            com.atalaya.cambios.CambiosDificultad.activar(fuente.getServer(), c);
        } else if (!encender && esta) {
            com.atalaya.cambios.CambiosDificultad.desactivar(fuente.getServer(), c);
        }
        fuente.sendSuccess(() -> Component.literal(c.titulo + ": " + (encender ? "ON" : "OFF")), true);
        return 1;
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
