package com.atalaya.bestiario;

import com.atalaya.Atalaya;
import com.atalaya.catalogo.Carteles;
import com.atalaya.catalogo.Catalogo;
import com.atalaya.catalogo.Categoria;
import com.atalaya.momento.Ruleta;
import com.atalaya.net.AtalayaRed;
import com.mojang.serialization.Codec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerLifecycleEvents;
import net.minecraft.resources.Identifier;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.util.datafix.DataFixTypes;
import net.minecraft.world.level.saveddata.SavedData;
import net.minecraft.world.level.saveddata.SavedDataType;
import org.jspecify.annotations.Nullable;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

/**
 * Los mobs nuevos que estan sueltos (18-10-2026): el menu de los mobs (/atalaya menu mobs) los enciende y los apaga, y
 * se guarda en el mundo.
 *
 * Encender uno lanza la Ruleta en su final del huevo, con su nombre en el rotulo del chat y lo que hace debajo; al salir
 * el aviso empieza a aparecer solo donde le toca (sus biomas, o lo que lo hace salir: romper hierba, dormir...). Apagarlo
 * corta las apariciones al momento (los que ya estan siguen hasta que se van, como cualquier monstruo). Los huevos y los
 * comandos lo sacan siempre, este encendido o no.
 */
public final class Bestiario extends SavedData {

    private static final Codec<Bestiario> CODEC = RecordCodecBuilder.create(i -> i.group(
            Codec.STRING.listOf().optionalFieldOf("sueltos", List.of()).forGetter(b -> new ArrayList<>(b.sueltos))
    ).apply(i, Bestiario::new));

    private static final SavedDataType<Bestiario> TIPO = new SavedDataType<>(
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "bestiario"), Bestiario::new, CODEC,
            DataFixTypes.SAVED_DATA_COMMAND_STORAGE);

    private final Set<String> sueltos;
    /** Los que esperan a que pare su Ruleta (no se guardan). */
    private static final Set<String> pendientes = new HashSet<>();
    private static @Nullable MinecraftServer servidor;

    public Bestiario() {
        this(List.of());
    }

    private Bestiario(List<String> sueltos) {
        this.sueltos = new HashSet<>(sueltos);
    }

    private static Bestiario de(MinecraftServer s) {
        return s.getDataStorage().computeIfAbsent(TIPO);
    }

    public static void registrar() {
        ServerLifecycleEvents.SERVER_STARTED.register(s -> servidor = s);
        ServerLifecycleEvents.SERVER_STOPPED.register(s -> {
            servidor = null;
            pendientes.clear();
        });
    }

    /** Si ese mob esta suelto (aparece solo). */
    public static boolean suelto(@Nullable MinecraftServer s, Bestia b) {
        return s != null && de(s).sueltos.contains(b.id());
    }

    /** Lo mismo, con el servidor en marcha (para los eventos que no lo traen). */
    public static boolean suelto(Bestia b) {
        return suelto(servidor, b);
    }

    /** El interruptor del menu: encendido, se apaga al momento; apagado, sale la Ruleta y se suelta con su aviso. */
    public static void pulsar(ServerPlayer jugador, Bestia b) {
        MinecraftServer s = jugador.level().getServer();
        Bestiario d = de(s);
        if (d.sueltos.contains(b.id())) {
            d.sueltos.remove(b.id());
            d.setDirty();
            Atalaya.LOGGER.info("Mob apagado por {}: {}", jugador.getName().getString(), b.id());
            Catalogo.enviarEstado(s, Categoria.MOB);
            return;
        }
        if (!pendientes.add(b.id())) {
            return;
        }
        Ruleta.tirarCambio(s, Ruleta.Fin.MOB, b.texto(), b.cartel(), Carteles.cuadros(b.cartel()),
                () -> {
                    pendientes.remove(b.id());
                    de(s).sueltos.add(b.id());
                    de(s).setDirty();
                    Atalaya.LOGGER.info("Mob suelto: {}", b.id());
                    Catalogo.enviarEstado(s, Categoria.MOB);
                },
                () -> {
                    pendientes.remove(b.id());
                    Catalogo.enviarEstado(s, Categoria.MOB);
                });
        Atalaya.LOGGER.info("Mob encendido por {}: {} (sale al acabar la Ruleta)", jugador.getName().getString(), b.id());
        Catalogo.enviarEstado(s, Categoria.MOB);
    }

    /** Lo suelta o lo recoge ya, sin Ruleta (el comando de las pruebas). */
    public static void poner(MinecraftServer s, Bestia b, boolean soltar) {
        Bestiario d = de(s);
        if (soltar) {
            d.sueltos.add(b.id());
        } else {
            d.sueltos.remove(b.id());
        }
        d.setDirty();
        Catalogo.enviarEstado(s, Categoria.MOB);
    }

    /** Su estado para el menu. */
    public static int estado(MinecraftServer s, Bestia b) {
        if (de(s).sueltos.contains(b.id())) {
            return AtalayaRed.EstadoCambio.ENCENDIDO;
        }
        return pendientes.contains(b.id()) ? AtalayaRed.EstadoCambio.ESPERA : AtalayaRed.EstadoCambio.APAGADO;
    }
}
