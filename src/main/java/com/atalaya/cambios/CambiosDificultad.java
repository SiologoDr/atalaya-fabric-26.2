package com.atalaya.cambios;

import com.atalaya.Atalaya;
import com.atalaya.catalogo.Carteles;
import com.atalaya.catalogo.Catalogo;
import com.atalaya.catalogo.Categoria;
import com.atalaya.momento.Ruleta;
import com.atalaya.net.AtalayaRed;
import com.mojang.serialization.Codec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerLifecycleEvents;
import net.fabricmc.fabric.api.networking.v1.ServerPlayNetworking;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.ResourceKey;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.util.datafix.DataFixTypes;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.portal.TeleportTransition;
import net.minecraft.world.level.saveddata.SavedData;
import net.minecraft.world.level.saveddata.SavedDataType;
import org.jspecify.annotations.Nullable;

import java.util.ArrayList;
import java.util.EnumSet;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.UUID;

/**
 * Los cambios de dificultad en marcha y las dimensiones abiertas (17-10-2026). Se guarda en el mundo: un End sellado
 * sigue sellado al reiniciar.
 *
 * <pre>
 *   /atalaya menu cambios       el menu de los cambios (MenuCatalogoScreen): encender uno lanza la Ruleta en su final
 *                               de dificultad, con el titulo del cambio en el rotulo del chat, y el cambio se aplica al
 *                               salir el aviso; apagarlo lo quita al momento, sin animacion ni aviso (Juan: "si esta
 *                               ON y le doy no se hace nada, solo se desactiva")
 *   /atalaya menu dimensiones   el menu de las dimensiones (MenuDimensionesScreen): el Nether y el End, abiertos o
 *                               cerrados, al momento
 * </pre>
 *
 * Lo que hace cada cambio esta en ReglasCambios y en los mixins que preguntan {@link #activo(Cambio)}: una pregunta
 * rapida (un EnumSet en memoria, al dia con lo guardado), que algunos se hacen en cada golpe o en cada tick.
 *
 * Una dimension cerrada: sus portales no llevan a ella (PortalCerradoMixin) y quien este dentro cuando se cierra vuelve
 * al Overworld. Los comandos de los operadores (/tp, /execute in) siguen funcionando.
 */
public final class CambiosDificultad extends SavedData {

    private static final Codec<CambiosDificultad> CODEC = RecordCodecBuilder.create(i -> i.group(
            Codec.STRING.listOf().optionalFieldOf("activos", List.of()).forGetter(c -> new ArrayList<>(c.activos)),
            Codec.unboundedMap(Codec.STRING, Codec.BOOL).optionalFieldOf("antes", Map.of()).forGetter(c -> c.antes),
            Codec.BOOL.optionalFieldOf("nether", true).forGetter(c -> c.nether),
            Codec.BOOL.optionalFieldOf("end", true).forGetter(c -> c.end)
    ).apply(i, CambiosDificultad::new));

    /** El tipo de datafix no se usa (los datos se escriben siempre en la version actual), pero no puede ser null. */
    private static final SavedDataType<CambiosDificultad> TIPO = new SavedDataType<>(
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "cambios"), CambiosDificultad::new, CODEC,
            DataFixTypes.SAVED_DATA_COMMAND_STORAGE);

    private final Set<String> activos;
    /** Como estaba su dimension antes de encender los que la tocan, para dejarla igual al apagarlos. */
    private final Map<String, Boolean> antes;
    private boolean nether;
    private boolean end;

    /** Los encendidos, en memoria (lo que preguntan las reglas). */
    private static final Set<Cambio> ENCENDIDOS = EnumSet.noneOf(Cambio.class);
    /** Los que estan esperando a que pare su Ruleta (no se guardan: si el servidor se para, no se aplican). */
    private static final Set<Cambio> pendientes = EnumSet.noneOf(Cambio.class);
    private static @Nullable MinecraftServer servidor;
    /** Cuando se le dijo a cada uno por ultima vez que un portal no responde (para no repetirlo en cada tick). */
    private static final Map<UUID, Long> avisados = new HashMap<>();

    public CambiosDificultad() {
        this(List.of(), Map.of(), true, true);
    }

    private CambiosDificultad(List<String> activos, Map<String, Boolean> antes, boolean nether, boolean end) {
        this.activos = new HashSet<>(activos);
        this.antes = new HashMap<>(antes);
        this.nether = nether;
        this.end = end;
    }

    private static CambiosDificultad de(MinecraftServer s) {
        return s.getDataStorage().computeIfAbsent(TIPO);
    }

    public static void registrar() {
        ServerLifecycleEvents.SERVER_STARTED.register(s -> {
            servidor = s;
            recordar(s);
        });
        ServerLifecycleEvents.SERVER_STOPPED.register(s -> {
            servidor = null;
            ENCENDIDOS.clear();
            pendientes.clear();
            avisados.clear();
        });
        ReglasCambios.registrar();
    }

    /** Pone al dia lo que hay en memoria con lo guardado. */
    private static void recordar(MinecraftServer s) {
        ENCENDIDOS.clear();
        for (String id : de(s).activos) {
            Cambio c = Cambio.porId(id);
            if (c != null) {
                ENCENDIDOS.add(c);
            }
        }
    }

    // ------------------------------------------------------------------
    //  Lo que se pregunta
    // ------------------------------------------------------------------

    /** Si ese cambio esta en marcha (rapido: se puede preguntar en cada golpe). */
    public static boolean activo(Cambio c) {
        return ENCENDIDOS.contains(c);
    }

    public static boolean activo(MinecraftServer s, Cambio c) {
        return ENCENDIDOS.contains(c);
    }

    /** El servidor en marcha (para las reglas que no lo traen). */
    public static @Nullable MinecraftServer servidor() {
        return servidor;
    }

    /** Si se puede entrar en esa dimension por sus portales. */
    public static boolean abierta(MinecraftServer s, ResourceKey<Level> dimension) {
        if (dimension == Level.NETHER) {
            return de(s).nether;
        }
        if (dimension == Level.END) {
            return de(s).end;
        }
        return true;
    }

    // ------------------------------------------------------------------
    //  Lo que se pulsa en los menus
    // ------------------------------------------------------------------

    /**
     * Un cambio pulsado en el menu: si esta encendido, se apaga al momento; si no, sale la Ruleta y se aplica cuando
     * sale su aviso (mientras, queda en espera y pulsarlo no hace nada).
     */
    public static void pulsar(ServerPlayer jugador, Cambio c) {
        MinecraftServer s = jugador.level().getServer();
        if (activo(c)) {
            desactivar(s, c);
            Atalaya.LOGGER.info("Cambio de dificultad apagado por {}: {}", jugador.getName().getString(), c.id);
            return;
        }
        if (pendientes.contains(c)) {
            return;
        }
        pendientes.add(c);
        Ruleta.tirarCambio(s, Ruleta.Fin.DIFICULTAD, c.texto, c.cartel(), Carteles.cuadros(c.cartel()),
                () -> {
                    pendientes.remove(c);
                    activar(s, c);
                },
                () -> {
                    pendientes.remove(c);
                    Catalogo.enviarEstado(s, Categoria.CAMBIO);
                });
        Atalaya.LOGGER.info("Cambio de dificultad encendido por {}: {} (se aplica al acabar la Ruleta)",
                jugador.getName().getString(), c.id);
        Catalogo.enviarEstado(s, Categoria.CAMBIO);
    }

    /** Una dimension pulsada en el menu (0, el Nether; 1, el End): se abre o se cierra al momento. */
    public static void pulsarDimension(ServerPlayer jugador, int cual) {
        MinecraftServer s = jugador.level().getServer();
        CambiosDificultad d = de(s);
        if (cual == 0) {
            d.nether = !d.nether;
            if (!d.nether) {
                // Cerrado a mano: los portales ya no arden.
                d.quitar(Cambio.PORTALES_ARDEN);
                expulsar(s, Level.NETHER, "El Nether se ha cerrado: vuelves al mundo.");
            }
        } else {
            d.end = !d.end;
            if (d.end) {
                // Abierto a mano: ya no esta sellado.
                d.quitar(Cambio.END_SELLADO);
            } else {
                expulsar(s, Level.END, "El End se ha cerrado: vuelves al mundo.");
            }
        }
        d.setDirty();
        Atalaya.LOGGER.info("Dimensiones ({}): Nether {}, End {}", jugador.getName().getString(),
                d.nether ? "abierto" : "cerrado", d.end ? "abierto" : "cerrado");
        Catalogo.enviarEstado(s, Categoria.CAMBIO);
        enviarDimensiones(s);
    }

    /** Apunta como estaba algo antes de encender ese cambio (para dejarlo igual al apagarlo). */
    static void recordarAntes(MinecraftServer s, Cambio c, boolean valor) {
        CambiosDificultad d = de(s);
        d.antes.put(c.id, valor);
        d.setDirty();
    }

    /** Como estaba antes de encenderlo (o null si no se apunto). */
    static @Nullable Boolean antes(MinecraftServer s, Cambio c) {
        return de(s).antes.get(c.id);
    }

    /** Lo quita sin deshacer nada (cuando ya lo deshizo el menu de las dimensiones). */
    private void quitar(Cambio c) {
        activos.remove(c.id);
        antes.remove(c.id);
        ENCENDIDOS.remove(c);
    }

    // ------------------------------------------------------------------
    //  Aplicar y quitar
    // ------------------------------------------------------------------

    /** Lo enciende ya, sin Ruleta (tambien lo usan las pruebas). */
    public static void activar(MinecraftServer s, Cambio c) {
        CambiosDificultad d = de(s);
        d.activos.add(c.id);
        ENCENDIDOS.add(c);
        switch (c) {
            case END_SELLADO -> {
                d.antes.put(c.id, d.end);
                d.end = false;
                expulsar(s, Level.END, "El End se ha sellado: vuelves al mundo.");
                enviarDimensiones(s);
            }
            case PORTALES_ARDEN -> {
                d.antes.put(c.id, d.nether);
                d.nether = true;
                enviarDimensiones(s);
            }
            default -> ReglasCambios.alEncender(s, c);
        }
        d.setDirty();
        com.atalaya.config.LibroRecetas.sincronizarTodos(s);
        Atalaya.LOGGER.info("Cambio de dificultad aplicado: {}", c.id);
        Catalogo.enviarEstado(s, Categoria.CAMBIO);
    }

    public static void desactivar(MinecraftServer s, Cambio c) {
        CambiosDificultad d = de(s);
        Boolean previo = d.antes.get(c.id);
        if (c != Cambio.END_SELLADO && c != Cambio.PORTALES_ARDEN) {
            // Lo de cada uno se deshace con el cambio aun apuntado (y lo que se recordo de antes, a mano).
            ENCENDIDOS.remove(c);
            ReglasCambios.alApagar(s, c);
        }
        d.quitar(c);
        switch (c) {
            case END_SELLADO -> {
                d.end = previo == null || previo;
                enviarDimensiones(s);
            }
            case PORTALES_ARDEN -> {
                d.nether = previo != null && previo;
                if (!d.nether) {
                    expulsar(s, Level.NETHER, "Los portales se han apagado: el Nether se cierra.");
                }
                enviarDimensiones(s);
            }
            default -> {
            }
        }
        d.setDirty();
        com.atalaya.config.LibroRecetas.sincronizarTodos(s);
        Catalogo.enviarEstado(s, Categoria.CAMBIO);
    }

    /** Quien este en esa dimension vuelve al Overworld (al punto de aparicion del mundo), con un aviso. */
    private static void expulsar(MinecraftServer s, ResourceKey<Level> dimension, String mensaje) {
        ServerLevel nivel = s.getLevel(dimension);
        if (nivel == null) {
            return;
        }
        for (ServerPlayer p : List.copyOf(nivel.players())) {
            p.teleport(TeleportTransition.createDefault(p, TeleportTransition.DO_NOTHING));
            p.sendSystemMessage(Component.literal(mensaje).withStyle(st -> st.withColor(0xFFC060)));
        }
    }

    /** Un portal a una dimension cerrada: se le dice a quien lo intenta (cada pocos segundos, no en cada tick). */
    public static void avisarCerrado(Entity quien, ResourceKey<Level> dimension) {
        if (!(quien instanceof ServerPlayer p)) {
            return;
        }
        long ahora = p.level().getGameTime();
        Long antes = avisados.get(p.getUUID());
        if (antes != null && ahora - antes < 60) {
            return;
        }
        avisados.put(p.getUUID(), ahora);
        String texto = dimension == Level.END ? "El End está sellado: el portal no responde."
                : "El Nether está cerrado: el portal no responde.";
        p.sendOverlayMessage(Component.literal(texto).withStyle(st -> st.withColor(0xFFC060)));
    }

    // ------------------------------------------------------------------
    //  Lo que se manda a los menus
    // ------------------------------------------------------------------

    /** El estado de todos los cambios, para el menu. */
    public static List<AtalayaRed.EstadoCambio> estados(MinecraftServer s) {
        List<AtalayaRed.EstadoCambio> out = new ArrayList<>();
        for (Cambio c : Cambio.values()) {
            int estado = ENCENDIDOS.contains(c) ? AtalayaRed.EstadoCambio.ENCENDIDO
                    : pendientes.contains(c) ? AtalayaRed.EstadoCambio.ESPERA : AtalayaRed.EstadoCambio.APAGADO;
            out.add(new AtalayaRed.EstadoCambio(c.id, estado, 0));
        }
        return out;
    }

    /** Abre el menu de las dimensiones a ese jugador. */
    public static void abrirDimensiones(ServerPlayer p) {
        CambiosDificultad d = de(p.level().getServer());
        ServerPlayNetworking.send(p, new AtalayaRed.MenuDimensiones(true, d.nether, d.end));
    }

    private static void enviarDimensiones(MinecraftServer s) {
        CambiosDificultad d = de(s);
        AtalayaRed.MenuDimensiones m = new AtalayaRed.MenuDimensiones(false, d.nether, d.end);
        for (ServerPlayer p : s.getPlayerList().getPlayers()) {
            ServerPlayNetworking.send(p, m);
        }
    }
}
