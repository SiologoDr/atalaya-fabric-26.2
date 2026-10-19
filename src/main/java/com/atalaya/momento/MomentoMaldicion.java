package com.atalaya.momento;

import com.atalaya.Atalaya;
import com.atalaya.net.AtalayaRed;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerLifecycleEvents;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerTickEvents;
import net.fabricmc.fabric.api.event.player.PlayerBlockBreakEvents;
import net.fabricmc.fabric.api.networking.v1.ServerPlayConnectionEvents;
import net.fabricmc.fabric.api.networking.v1.ServerPlayNetworking;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.data.AtlasIds;
import net.minecraft.network.chat.MutableComponent;
import net.minecraft.network.chat.contents.objects.AtlasSprite;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.ResourceKey;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.damagesource.DamageType;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import org.jspecify.annotations.Nullable;

import java.util.HashMap;
import java.util.Map;
import java.util.Set;
import java.util.UUID;

/**
 * El Momento Fractura (nacio como Momento Maldicion, 15-10-2026): el "momento
 * Reviil" de DEDsafio a nuestra manera. Juan: "quiero que lo hagas mil veces
 * mejor, que me sorprendas".
 *
 * <pre>
 *   /atalaya momento_fractura "titulo" "texto" [segundos]
 *   /atalaya momento_fractura prueba tierra &lt;segundos&gt; [cantidad]
 *   /atalaya momento_fractura stop
 * </pre>
 *
 * A todos les sale a la vez la cinematica (MomentoMaldicionCliente y
 * MomentoMaldicionHud). Al acabar, el texto sale en el chat con una campana, y
 * el mundo se queda maldito (el cielo roto, la niebla, la musica) hasta que se
 * para. Con segundos, se para solo al pasar ese tiempo.
 *
 * LA PRUEBA (16-10-2026, Juan: "un momento fractura de prueba de romper 10 de
 * tierra o cesped; arriba en el centro un contador; si llega a cero, aunque
 * tenga totems, te mata; si cumples no te va a avisar; cuando se termine el
 * contador, que pasen 10 s y luego se vaya"): al acabar la cinematica empieza
 * el contador. Cada jugador lleva la cuenta de los bloques de tierra o cesped
 * que rompe mientras corre; al llegar a cero, a quien no haya llegado lo mata
 * la fractura (un dano que se salta los totems) y, 10 s despues, el momento se
 * va. A quien cumple no se le dice nada.
 *
 * El servidor elige la semilla del cielo roto, para que todos lo vean igual.
 *
 * El servidor solo lleva la cuenta y avisa: todo lo que se ve y se oye lo hace
 * cada cliente. Quien entra a mitad lo recibe ya empezado. No se guarda en el
 * mundo: si el servidor se reinicia, el momento se acaba.
 */
public final class MomentoMaldicion {

    /** Lo que dura la cinematica (ticks): el chat sale al acabar y el reloj empieza a contar ahi. */
    public static final int INTRO = 224;
    /** Lo que sigue despues de que el contador de una prueba llegue a cero (ticks), antes de irse. */
    public static final int TRAS_PRUEBA = 200;
    /** La prueba de la tierra: lo que se cuenta al romperlo. */
    public static final int PRUEBA_TIERRA = 1;
    private static final Set<Block> TIERRA = Set.of(Blocks.DIRT, Blocks.COARSE_DIRT, Blocks.ROOTED_DIRT, Blocks.GRASS_BLOCK);
    /** El dano de la fractura: mata aunque haya totems (bypasses_invulnerability). */
    public static final ResourceKey<DamageType> DANO = ResourceKey.create(Registries.DAMAGE_TYPE,
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "momento_fractura"));

    private static @Nullable MinecraftServer servidor;
    private static boolean activo;
    private static String titulo = "";
    private static String texto = "";
    /** Ticks desde que empezo, y los que dura despues de la cinematica (0, hasta que se pare). */
    private static int pasado;
    private static int duracion;
    private static boolean avisado;
    /** La prueba en marcha (0, ninguna), lo que hay que romper, lo que dura el contador (ticks) y si ya llego a cero. */
    private static int prueba;
    private static int cantidad;
    private static int contador;
    private static boolean juzgado;
    /** La semilla del cielo roto del momento en marcha. */
    private static int semilla;
    private static final java.util.Random AZAR = new java.util.Random();
    /** Lo que lleva roto cada jugador mientras corre el contador. */
    private static final Map<UUID, Integer> rotos = new HashMap<>();
    /**
     * Un momento del catalogo (com.atalaya.catalogo.Momentos): lo que se hace al salir su aviso (se aplica) y al acabar
     * (se deshace), sea porque se acaba el tiempo, porque lo paran o porque empieza otro momento.
     */
    private static @Nullable Runnable alAvisar;
    private static @Nullable Runnable alAcabar;
    /** Los ultimos que se usaron: los repite el interruptor del menu. */
    private static String ultimoTitulo = "La maldición";
    private static String ultimoTexto = "Algo ha despertado bajo Atalaya.";
    private static int ultimaDuracion;

    private MomentoMaldicion() {
    }

    public static void registrar() {
        ServerLifecycleEvents.SERVER_STARTED.register(s -> servidor = s);
        ServerLifecycleEvents.SERVER_STOPPED.register(s -> {
            servidor = null;
            activo = false;
            prueba = 0;
            rotos.clear();
        });
        ServerTickEvents.END_SERVER_TICK.register(MomentoMaldicion::tick);
        // Quien entra a mitad lo recibe ya empezado (sin la cinematica).
        ServerPlayConnectionEvents.JOIN.register((manejador, envio, s) -> {
            if (activo) {
                ServerPlayNetworking.send(manejador.getPlayer(),
                        new AtalayaRed.Momento(AtalayaRed.Momento.SIGUE, titulo, texto, duracion, pasado, contador, semilla));
            }
        });
        // La prueba de la tierra: cuenta lo que rompe cada uno mientras corre el contador.
        PlayerBlockBreakEvents.AFTER.register((nivel, jugador, pos, estado, bloqueEntidad) -> {
            if (activo && prueba == PRUEBA_TIERRA && corre() && TIERRA.contains(estado.getBlock())) {
                rotos.merge(jugador.getUUID(), 1, Integer::sum);
            }
        });
    }

    public static boolean activo() {
        return activo;
    }

    public static String titulo() {
        return titulo;
    }

    /** Lo que le queda (ticks), o -1 si no lleva reloj. */
    public static int queda() {
        return duracion <= 0 ? -1 : Math.max(0, INTRO + duracion - pasado);
    }

    /** Los ticks desde que salio el aviso (desde que acabo la cinematica), o -1 si no ha salido. */
    public static int desdeAviso() {
        return activo && pasado >= INTRO ? pasado - INTRO : -1;
    }

    /** Si el contador de la prueba esta corriendo. */
    private static boolean corre() {
        return prueba != 0 && pasado >= INTRO && pasado < INTRO + contador;
    }

    /** Empieza (o vuelve a empezar, con otro titulo) el momento para todos, sin prueba. */
    public static void empezar(MinecraftServer s, String nuevoTitulo, String nuevoTexto, int segundos) {
        acabarCatalogo();
        prueba = 0;
        contador = 0;
        lanzar(s, nuevoTitulo, nuevoTexto, Math.max(0, segundos) * 20);
        ultimoTitulo = titulo;
        ultimoTexto = texto;
        ultimaDuracion = segundos;
        Atalaya.LOGGER.info("Momento fractura: «{}» ({}).", titulo, segundos > 0 ? segundos + " s" : "sin limite");
    }

    /**
     * La prueba de la tierra: romper 'cuantos' bloques de tierra o cesped antes
     * de que el contador ('segundos', desde que acaba la cinematica) llegue a cero.
     */
    public static void empezarPruebaTierra(MinecraftServer s, int segundos, int cuantos) {
        acabarCatalogo();
        prueba = PRUEBA_TIERRA;
        cantidad = Math.max(1, cuantos);
        contador = Math.max(1, segundos) * 20;
        lanzar(s, "Prueba de la tierra", "Rompe " + cantidad + (cantidad == 1 ? " bloque" : " bloques")
                + " de tierra o césped antes de que el contador llegue a cero.", contador + TRAS_PRUEBA);
        Atalaya.LOGGER.info("Momento fractura, prueba de la tierra: {} bloques en {} s.", cantidad, segundos);
    }

    /**
     * Un momento del catalogo: la misma cinematica y el mismo cielo, con su texto; al salir el aviso se hace 'avisar'
     * y al acabar (el tiempo, stop u otro momento) se hace 'acabar'. Con segundos 0 dura hasta que se pare. Con
     * ticksContador, arriba sale el contador (lo que pasa al llegar a cero lo hace el momento).
     */
    public static void empezarCatalogo(MinecraftServer s, String nuevoTitulo, String nuevoTexto, int segundos,
                                       int ticksContador, Runnable avisar, Runnable acabar) {
        acabarCatalogo();
        prueba = 0;
        contador = Math.max(0, ticksContador);
        lanzar(s, nuevoTitulo, nuevoTexto, Math.max(0, segundos) * 20);
        alAvisar = avisar;
        alAcabar = acabar;
        Atalaya.LOGGER.info("Momento fractura del catalogo: «{}» ({}).", titulo, segundos > 0 ? segundos + " s" : "sin limite");
    }

    /** Si el momento en marcha es uno del catalogo, se deshace (una sola vez). */
    private static void acabarCatalogo() {
        Runnable fin = alAcabar;
        alAvisar = null;
        alAcabar = null;
        if (fin != null) {
            fin.run();
        }
    }

    private static void lanzar(MinecraftServer s, String nuevoTitulo, String nuevoTexto, int ticks) {
        servidor = s;
        titulo = limpiar(nuevoTitulo, 64);
        texto = limpiar(nuevoTexto, 400);
        duracion = ticks;
        pasado = 0;
        avisado = false;
        juzgado = false;
        rotos.clear();
        activo = true;
        semilla = AZAR.nextInt();
        enviar(new AtalayaRed.Momento(AtalayaRed.Momento.EMPIEZA, titulo, texto, duracion, 0, contador, semilla));
    }

    /** Lo para para todos; false si no habia ninguno. Parado a mano, la prueba no mata a nadie. */
    public static boolean parar() {
        if (!activo) {
            return false;
        }
        activo = false;
        prueba = 0;
        rotos.clear();
        enviar(new AtalayaRed.Momento(AtalayaRed.Momento.PARA, titulo, texto, 0, pasado, 0, semilla));
        Atalaya.LOGGER.info("Momento fractura parado.");
        acabarCatalogo();
        return true;
    }

    /** El interruptor del menu: lo enciende con el ultimo titulo y texto, o lo para. */
    public static void interruptor(boolean encender) {
        if (encender && !activo && servidor != null) {
            empezar(servidor, ultimoTitulo, ultimoTexto, ultimaDuracion);
        } else if (!encender) {
            parar();
        }
    }

    private static void tick(MinecraftServer s) {
        if (!activo) {
            return;
        }
        pasado++;
        if (!avisado && pasado >= INTRO) {
            avisado = true;
            avisoChat(s);
            Runnable aplicar = alAvisar;
            alAvisar = null;
            if (aplicar != null) {
                aplicar.run();
            }
        }
        if (prueba != 0 && !juzgado && pasado >= INTRO + contador) {
            juzgado = true;
            juzgar(s);
        }
        if (duracion > 0 && pasado >= INTRO + duracion) {
            parar();
        }
    }

    /**
     * El contador ha llegado a cero: la fractura se lleva a quien no haya roto lo que tocaba (aunque tenga totems).
     * A quien cumple no se le dice nada. Los de creativo y los espectadores no cuentan.
     */
    private static void juzgar(MinecraftServer s) {
        int muertos = 0;
        for (ServerPlayer jugador : s.getPlayerList().getPlayers()) {
            if (!jugador.isAlive() || jugador.isSpectator() || jugador.isCreative()) {
                continue;
            }
            if (rotos.getOrDefault(jugador.getUUID(), 0) >= cantidad) {
                continue;
            }
            ServerLevel nivel = jugador.level();
            DamageSource fuente = new DamageSource(nivel.registryAccess().lookupOrThrow(Registries.DAMAGE_TYPE).getOrThrow(DANO));
            jugador.hurtServer(nivel, fuente, 1.0E6F);
            muertos++;
        }
        Atalaya.LOGGER.info("Momento fractura: el contador llego a cero; la fractura se lleva a {}.", muertos);
    }

    /**
     * El aviso del chat al acabar la cinematica (la campana la toca cada cliente
     * a la vez), como el del momento de DEDsafio: el sello rojo, "MOMENTO
     * FRACTURA:" en negrita (siempre ese: el titulo del comando es el de la
     * pantalla) y el texto en rojo debajo.
     */
    private static void avisoChat(MinecraftServer s) {
        MutableComponent todo = Component.empty()
                .append(Component.object(new AtlasSprite(AtlasIds.ITEMS, ICONO)).withStyle(st -> st.withoutShadow()))
                .append(" ");
        // El rotulo en letras de metal rojo con su brillo que pasa: cuadros animados que el chat pinta seguidos.
        for (int i = 0; i < CARTEL; i++) {
            Identifier cuadro = Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, String.format("item/momento_cartel_%02d", i));
            todo.append(Component.object(new AtlasSprite(AtlasIds.ITEMS, cuadro)).withStyle(st -> st.withoutShadow()));
        }
        todo.append("\n").append(Component.literal(texto).withStyle(st -> st.withColor(0xF04A40)));
        s.getPlayerList().broadcastSystemMessage(todo, false);
    }

    /** El icono del aviso: el sello rojo y rajado (momento_maldicion.py). */
    private static final Identifier ICONO = Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "item/momento_fractura");
    /** Los cuadros del rotulo MOMENTO FRACTURA: (los que dice momento_maldicion.py al hacerlo). */
    private static final int CARTEL = 12;

    private static void enviar(AtalayaRed.Momento m) {
        if (servidor == null) {
            return;
        }
        for (ServerPlayer p : servidor.getPlayerList().getPlayers()) {
            ServerPlayNetworking.send(p, m);
        }
    }

    /** Sin saltos de linea ni codigos de color, y de un largo razonable. */
    private static String limpiar(String s, int largo) {
        String t = s.replace('\n', ' ').replace('\r', ' ').replace('§', ' ').strip();
        return t.length() > largo ? t.substring(0, largo) : t;
    }
}
