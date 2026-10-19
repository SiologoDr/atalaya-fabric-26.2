package com.atalaya.catalogo;

import com.atalaya.bestiario.Bestia;
import com.atalaya.bestiario.Bestias;
import com.atalaya.bestiario.Bestiario;
import com.atalaya.cambios.Cambio;
import com.atalaya.cambios.CambiosDificultad;
import com.atalaya.momento.Momento;
import com.atalaya.momento.Momentos;
import com.atalaya.net.AtalayaRed;
import net.fabricmc.fabric.api.networking.v1.ServerPlayNetworking;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerPlayer;
import org.jspecify.annotations.Nullable;

import java.util.ArrayList;
import java.util.List;

/**
 * El catalogo del evento: las tres listas (Categoria) y lo que pasa al pulsar una fila de sus menus. Cada lista lleva su
 * estado donde le toca: los cambios en CambiosDificultad, los mobs en Bestiario y los momentos en Momentos.
 */
public final class Catalogo {

    private Catalogo() {
    }

    /** Lo que hay en una lista, en el orden del menu. */
    public static List<? extends Entrada> entradas(Categoria c) {
        return switch (c) {
            case CAMBIO -> List.of(Cambio.values());
            case MOB -> Bestias.todas();
            case MOMENTO -> List.of(Momento.values());
        };
    }

    public static @Nullable Entrada buscar(Categoria c, String id) {
        for (Entrada e : entradas(c)) {
            if (e.id().equals(id)) {
                return e;
            }
        }
        return null;
    }

    /** Una fila pulsada en un menu (ya se ha mirado que quien pulsa es operador); sin id, una pestana: abre ese menu. */
    public static void pulsar(ServerPlayer jugador, Categoria c, String id) {
        if (id.isEmpty()) {
            abrir(jugador, c);
            return;
        }
        Entrada e = buscar(c, id);
        if (e == null) {
            return;
        }
        switch (c) {
            case CAMBIO -> CambiosDificultad.pulsar(jugador, (Cambio) e);
            case MOB -> Bestiario.pulsar(jugador, (Bestia) e);
            case MOMENTO -> Momentos.pulsar(jugador, (Momento) e);
        }
    }

    /** El estado de cada fila de una lista. */
    public static List<AtalayaRed.EstadoCambio> estados(MinecraftServer s, Categoria c) {
        List<AtalayaRed.EstadoCambio> out = new ArrayList<>();
        switch (c) {
            case CAMBIO -> out.addAll(CambiosDificultad.estados(s));
            case MOB -> {
                for (Bestia b : Bestias.todas()) {
                    out.add(new AtalayaRed.EstadoCambio(b.id(), Bestiario.estado(s, b), 0));
                }
            }
            case MOMENTO -> out.addAll(Momentos.estados(s));
        }
        return out;
    }

    /** Abre el menu de esa lista a ese jugador. */
    public static void abrir(ServerPlayer p, Categoria c) {
        ServerPlayNetworking.send(p, new AtalayaRed.MenuCatalogo(c.ordinal(), true, estados(p.level().getServer(), c)));
    }

    /** Manda el estado de esa lista a todos (quien tenga su menu abierto lo ve cambiar; a los demas no les hace nada). */
    public static void enviarEstado(MinecraftServer s, Categoria c) {
        AtalayaRed.MenuCatalogo m = new AtalayaRed.MenuCatalogo(c.ordinal(), false, estados(s, c));
        for (ServerPlayer p : s.getPlayerList().getPlayers()) {
            ServerPlayNetworking.send(p, m);
        }
    }
}
