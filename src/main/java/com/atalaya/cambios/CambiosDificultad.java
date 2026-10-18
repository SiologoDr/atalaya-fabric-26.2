package com.atalaya.cambios;

import com.atalaya.Atalaya;
import com.atalaya.momento.Ruleta;
import com.atalaya.net.AtalayaRed;
import com.mojang.serialization.Codec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import net.fabricmc.fabric.api.entity.event.v1.ServerPlayerEvents;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerLifecycleEvents;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerTickEvents;
import net.fabricmc.fabric.api.loot.v3.LootTableEvents;
import net.fabricmc.fabric.api.networking.v1.ServerPlayConnectionEvents;
import net.fabricmc.fabric.api.networking.v1.ServerPlayNetworking;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.ResourceKey;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.util.datafix.DataFixTypes;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityTypes;
import net.minecraft.world.entity.ai.attributes.AttributeInstance;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.portal.TeleportTransition;
import net.minecraft.world.level.saveddata.SavedData;
import net.minecraft.world.level.saveddata.SavedDataType;
import net.minecraft.world.level.storage.loot.parameters.LootContextParams;
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
 * sigue sellado al reiniciar, y la media vida sigue contando donde se quedo (cuenta el tiempo de juego).
 *
 * <pre>
 *   /atalaya menu cambios       el menu de los cambios (MenuCambiosScreen): encender uno lanza la Ruleta en su final
 *                               de dificultad, con el titulo del cambio en el rotulo del chat, y el cambio se aplica al
 *                               salir el aviso; apagarlo lo quita al momento, sin animacion ni aviso (Juan: "si esta
 *                               ON y le doy no se hace nada, solo se desactiva")
 *   /atalaya menu dimensiones   el menu de las dimensiones (MenuDimensionesScreen): el Nether y el End, abiertos o
 *                               cerrados, al momento
 * </pre>
 *
 * Lo que hace cada cambio:
 * <pre>
 *   NI UN TOTEM MAS       los evocadores no sueltan totems de la inmortalidad (se quitan de lo que sueltan al morir)
 *   EL END, SELLADO       cierra el End: sus portales no llevan a ninguna parte y quien este dentro vuelve al
 *                         Overworld. Al apagarlo, el End vuelve a como estaba antes
 *   VIDA A MEDIAS         la mitad de la vida maxima a todos durante 30 minutos de juego (a quien entre o reaparezca
 *                         mientras dura, tambien); al acabar se apaga sola y lo dice el chat
 *   LOS PORTALES ARDEN    abre el Nether. Al apagarlo, el Nether vuelve a como estaba antes
 * </pre>
 *
 * Una dimension cerrada: sus portales no llevan a ella (PortalCerradoMixin) y quien este dentro cuando se cierra vuelve
 * al Overworld. Los comandos de los operadores (/tp, /execute in) siguen funcionando.
 */
public final class CambiosDificultad extends SavedData {

    private static final Codec<CambiosDificultad> CODEC = RecordCodecBuilder.create(i -> i.group(
            Codec.STRING.listOf().optionalFieldOf("activos", List.of()).forGetter(c -> new ArrayList<>(c.activos)),
            Codec.unboundedMap(Codec.STRING, Codec.LONG).optionalFieldOf("hasta", Map.of()).forGetter(c -> c.hasta),
            Codec.unboundedMap(Codec.STRING, Codec.BOOL).optionalFieldOf("antes", Map.of()).forGetter(c -> c.antes),
            Codec.BOOL.optionalFieldOf("nether", true).forGetter(c -> c.nether),
            Codec.BOOL.optionalFieldOf("end", true).forGetter(c -> c.end)
    ).apply(i, CambiosDificultad::new));

    /** El tipo de datafix no se usa (los datos se escriben siempre en la version actual), pero no puede ser null. */
    private static final SavedDataType<CambiosDificultad> TIPO = new SavedDataType<>(
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "cambios"), CambiosDificultad::new, CODEC,
            DataFixTypes.SAVED_DATA_COMMAND_STORAGE);

    /** La media vida: un modificador de la vida maxima de -50 %, que no se guarda (se pone al entrar si toca). */
    private static final Identifier MEDIA_VIDA = Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "cambio_vida_a_medias");

    private final Set<String> activos;
    /** Cuando acaban los que duran (tiempo de juego del Overworld). */
    private final Map<String, Long> hasta;
    /** Como estaba su dimension antes de encender los que la tocan, para dejarla igual al apagarlos. */
    private final Map<String, Boolean> antes;
    private boolean nether;
    private boolean end;

    /** Los que estan esperando a que pare su Ruleta (no se guardan: si el servidor se para, no se aplican). */
    private static final Set<Cambio> pendientes = EnumSet.noneOf(Cambio.class);
    private static @Nullable MinecraftServer servidor;
    /** Cuando se le dijo a cada uno por ultima vez que un portal no responde (para no repetirlo en cada tick). */
    private static final Map<UUID, Long> avisados = new HashMap<>();

    public CambiosDificultad() {
        this(List.of(), Map.of(), Map.of(), true, true);
    }

    private CambiosDificultad(List<String> activos, Map<String, Long> hasta, Map<String, Boolean> antes, boolean nether,
                              boolean end) {
        this.activos = new HashSet<>(activos);
        this.hasta = new HashMap<>(hasta);
        this.antes = new HashMap<>(antes);
        this.nether = nether;
        this.end = end;
    }

    private static CambiosDificultad de(MinecraftServer s) {
        return s.getDataStorage().computeIfAbsent(TIPO);
    }

    public static void registrar() {
        ServerLifecycleEvents.SERVER_STARTED.register(s -> servidor = s);
        ServerLifecycleEvents.SERVER_STOPPED.register(s -> {
            servidor = null;
            pendientes.clear();
            avisados.clear();
        });
        ServerTickEvents.END_SERVER_TICK.register(CambiosDificultad::tick);
        // La media vida a quien entra o reaparece mientras dura (y se le quita si ya no toca).
        ServerPlayConnectionEvents.JOIN.register((manejador, envio, s) ->
                mediaVida(manejador.getPlayer(), activo(s, Cambio.VIDA_A_MEDIAS)));
        ServerPlayerEvents.AFTER_RESPAWN.register((viejo, nuevo, vivo) ->
                mediaVida(nuevo, activo(nuevo.level().getServer(), Cambio.VIDA_A_MEDIAS)));
        // Ni un totem mas: se quitan de lo que sueltan los evocadores (al momento, sin recargar las tablas).
        LootTableEvents.MODIFY_DROPS.register((tabla, contexto, drops) -> {
            if (servidor == null || !activo(servidor, Cambio.NI_UN_TOTEM_MAS)) {
                return;
            }
            Entity quien = contexto.getOptionalParameter(LootContextParams.THIS_ENTITY);
            if (quien != null && quien.getType() == EntityTypes.EVOKER) {
                drops.removeIf(p -> p.is(Items.TOTEM_OF_UNDYING));
            }
        });
    }

    // ------------------------------------------------------------------
    //  Lo que se pregunta
    // ------------------------------------------------------------------

    public static boolean activo(MinecraftServer s, Cambio c) {
        return de(s).activos.contains(c.id);
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
        if (activo(s, c)) {
            desactivar(s, c);
            Atalaya.LOGGER.info("Cambio de dificultad apagado por {}: {}", jugador.getName().getString(), c.id);
            return;
        }
        if (pendientes.contains(c)) {
            return;
        }
        pendientes.add(c);
        Ruleta.tirarCambio(s, Ruleta.Fin.DIFICULTAD, c.texto, "cambio_" + c.id, c.cartel,
                () -> {
                    pendientes.remove(c);
                    activar(s, c);
                },
                () -> {
                    pendientes.remove(c);
                    enviarEstado(s, null);
                });
        Atalaya.LOGGER.info("Cambio de dificultad encendido por {}: {} (se aplica al acabar la Ruleta)",
                jugador.getName().getString(), c.id);
        enviarEstado(s, null);
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
        enviarEstado(s, null);
        enviarDimensiones(s, null);
    }

    /** Lo quita sin deshacer nada (cuando ya lo deshizo el menu de las dimensiones). */
    private void quitar(Cambio c) {
        activos.remove(c.id);
        hasta.remove(c.id);
        antes.remove(c.id);
    }

    // ------------------------------------------------------------------
    //  Aplicar y quitar
    // ------------------------------------------------------------------

    private static void activar(MinecraftServer s, Cambio c) {
        CambiosDificultad d = de(s);
        d.activos.add(c.id);
        switch (c) {
            case END_SELLADO -> {
                d.antes.put(c.id, d.end);
                d.end = false;
                expulsar(s, Level.END, "El End se ha sellado: vuelves al mundo.");
                enviarDimensiones(s, null);
            }
            case PORTALES_ARDEN -> {
                d.antes.put(c.id, d.nether);
                d.nether = true;
                enviarDimensiones(s, null);
            }
            case VIDA_A_MEDIAS -> {
                d.hasta.put(c.id, s.overworld().getGameTime() + c.duracion);
                for (ServerPlayer p : s.getPlayerList().getPlayers()) {
                    mediaVida(p, true);
                }
            }
            default -> {
            }
        }
        d.setDirty();
        Atalaya.LOGGER.info("Cambio de dificultad aplicado: {}", c.id);
        enviarEstado(s, null);
    }

    private static void desactivar(MinecraftServer s, Cambio c) {
        CambiosDificultad d = de(s);
        Boolean previo = d.antes.get(c.id);
        d.quitar(c);
        switch (c) {
            case END_SELLADO -> {
                d.end = previo == null || previo;
                enviarDimensiones(s, null);
            }
            case PORTALES_ARDEN -> {
                d.nether = previo != null && previo;
                if (!d.nether) {
                    expulsar(s, Level.NETHER, "Los portales se han apagado: el Nether se cierra.");
                }
                enviarDimensiones(s, null);
            }
            case VIDA_A_MEDIAS -> {
                for (ServerPlayer p : s.getPlayerList().getPlayers()) {
                    mediaVida(p, false);
                }
            }
            default -> {
            }
        }
        d.setDirty();
        enviarEstado(s, null);
    }

    private static void tick(MinecraftServer s) {
        if (s.getTickCount() % 20 != 0) {
            return;
        }
        CambiosDificultad d = de(s);
        long ahora = s.overworld().getGameTime();
        for (Cambio c : Cambio.values()) {
            Long fin = d.hasta.get(c.id);
            if (c.duracion > 0 && fin != null && ahora >= fin && d.activos.contains(c.id)) {
                desactivar(s, c);
                s.getPlayerList().broadcastSystemMessage(Component.literal("Se acabó «" + c.titulo + "».")
                        .withStyle(st -> st.withColor(Ruleta.Fin.DIFICULTAD.color)), false);
                Atalaya.LOGGER.info("Cambio de dificultad acabado: {}", c.id);
            }
        }
    }

    /** Pone o quita la media vida (y si quedaba mas vida que la nueva maxima, la recorta). */
    private static void mediaVida(ServerPlayer p, boolean poner) {
        AttributeInstance vida = p.getAttribute(Attributes.MAX_HEALTH);
        if (vida == null) {
            return;
        }
        if (poner && !vida.hasModifier(MEDIA_VIDA)) {
            vida.addTransientModifier(new AttributeModifier(MEDIA_VIDA, -0.5, AttributeModifier.Operation.ADD_MULTIPLIED_TOTAL));
            if (p.getHealth() > p.getMaxHealth()) {
                p.setHealth(p.getMaxHealth());
            }
        } else if (!poner && vida.hasModifier(MEDIA_VIDA)) {
            vida.removeModifier(MEDIA_VIDA);
        }
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
    private static List<AtalayaRed.EstadoCambio> estados(MinecraftServer s) {
        CambiosDificultad d = de(s);
        long ahora = s.overworld().getGameTime();
        List<AtalayaRed.EstadoCambio> out = new ArrayList<>();
        for (Cambio c : Cambio.values()) {
            int estado = d.activos.contains(c.id) ? AtalayaRed.EstadoCambio.ENCENDIDO
                    : pendientes.contains(c) ? AtalayaRed.EstadoCambio.ESPERA : AtalayaRed.EstadoCambio.APAGADO;
            Long fin = d.hasta.get(c.id);
            int quedan = fin != null && estado == AtalayaRed.EstadoCambio.ENCENDIDO ? (int) Math.max(0, fin - ahora) : 0;
            out.add(new AtalayaRed.EstadoCambio(c.id, estado, quedan));
        }
        return out;
    }

    /** Abre el menu de los cambios a ese jugador. */
    public static void abrirCambios(ServerPlayer p) {
        ServerPlayNetworking.send(p, new AtalayaRed.MenuCambios(true, estados(p.level().getServer())));
    }

    /** Abre el menu de las dimensiones a ese jugador. */
    public static void abrirDimensiones(ServerPlayer p) {
        CambiosDificultad d = de(p.level().getServer());
        ServerPlayNetworking.send(p, new AtalayaRed.MenuDimensiones(true, d.nether, d.end));
    }

    /** Manda el estado a todos (quien tenga el menu abierto lo ve cambiar; a los demas no les hace nada). */
    private static void enviarEstado(MinecraftServer s, @Nullable ServerPlayer solo) {
        AtalayaRed.MenuCambios m = new AtalayaRed.MenuCambios(false, estados(s));
        for (ServerPlayer p : s.getPlayerList().getPlayers()) {
            ServerPlayNetworking.send(p, m);
        }
    }

    private static void enviarDimensiones(MinecraftServer s, @Nullable ServerPlayer solo) {
        CambiosDificultad d = de(s);
        AtalayaRed.MenuDimensiones m = new AtalayaRed.MenuDimensiones(false, d.nether, d.end);
        for (ServerPlayer p : s.getPlayerList().getPlayers()) {
            ServerPlayNetworking.send(p, m);
        }
    }
}
