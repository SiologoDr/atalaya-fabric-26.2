package com.atalaya.bestiario;

import com.atalaya.Atalaya;
import net.fabricmc.fabric.api.attachment.v1.AttachmentRegistry;
import net.fabricmc.fabric.api.attachment.v1.AttachmentSyncPredicate;
import net.fabricmc.fabric.api.attachment.v1.AttachmentType;
import net.minecraft.network.codec.ByteBufCodecs;
import net.minecraft.resources.Identifier;
import net.minecraft.world.entity.player.Player;

/**
 * Lo que le falta a un jugador para soltarse de las lianas del Creeper Enredadera: cuantas pulsaciones (0: libre) y de
 * que tecla (cada vez que te atrapa, una al azar: saltar, adelante, atras, izquierda o derecha). Va en un numero (las
 * pulsaciones mas cien por la tecla).
 *
 * Va al cliente del atrapado (la barra de las lianas y la tecla que aporrear) y no se guarda: si sale del mundo, al
 * volver ya no esta atrapado (la Enredadera que lo tenia lo suelta en cuanto no lo encuentra).
 */
public final class Atrapado {

    /** Las que hacen falta para soltarse. */
    public static final int PULSACIONES = 7;
    /** Las teclas: saltar, adelante, atras, izquierda y derecha. */
    public static final int SALTAR = 0;
    public static final int ADELANTE = 1;
    public static final int ATRAS = 2;
    public static final int IZQUIERDA = 3;
    public static final int DERECHA = 4;
    public static final int TECLAS = 5;

    public static AttachmentType<Integer> FALTAN;

    private Atrapado() {
    }

    public static void registrar() {
        FALTAN = AttachmentRegistry.<Integer>builder()
                .initializer(() -> 0)
                .syncWith(ByteBufCodecs.VAR_INT, AttachmentSyncPredicate.targetOnly())
                .buildAndRegister(Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "atrapado"));
    }

    private static int valor(Player jugador) {
        return jugador.getAttachedOrCreate(FALTAN);
    }

    public static int faltan(Player jugador) {
        return valor(jugador) % 100;
    }

    public static int tecla(Player jugador) {
        return valor(jugador) / 100;
    }

    public static void poner(Player jugador, int faltan, int tecla) {
        int v = faltan <= 0 ? 0 : faltan + 100 * tecla;
        if (valor(jugador) != v) {
            jugador.setAttached(FALTAN, v);
        }
    }

    public static void soltar(Player jugador) {
        poner(jugador, 0, 0);
    }

    public static boolean atrapado(Player jugador) {
        return faltan(jugador) > 0;
    }
}
