package com.atalaya.momento;

import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerPlayer;

/**
 * Lo que hace un momento del catalogo mientras dura (cada vez que se lanza, uno nuevo: lleva su propia cuenta). Empieza
 * al salir el aviso del chat (despues de la cinematica del Momento Fractura) y acaba con el tiempo, con OFF o cuando
 * empieza otro momento: entonces deshace lo suyo.
 */
public interface Suceso {

    /** Al salir el aviso del chat: se aplica. */
    default void empieza(MinecraftServer s) {
    }

    /** Cada tick mientras dura; t son los ticks desde el aviso. */
    default void tick(MinecraftServer s, int t) {
    }

    /** Al acabar (sea como sea): se deshace. Solo si llego a empezar. */
    default void acaba(MinecraftServer s) {
    }

    /** El contador de arriba (ticks desde el aviso hasta que llega a cero), o 0 si no lleva. */
    default int contador() {
        return 0;
    }

    /** Lo que sigue despues de que el contador llegue a cero, antes de irse (ticks). */
    default int despues() {
        return Momentos.TRAS_CONTADOR;
    }

    /** Quien entra (o reaparece) mientras dura: lo que haga falta ponerle. */
    default void alEntrar(ServerPlayer p) {
    }

    /** Si un jugador cuenta para las pruebas (los de creativo y los espectadores, no). */
    static boolean cuenta(ServerPlayer p) {
        return p.isAlive() && !p.isSpectator() && !p.isCreative();
    }
}
