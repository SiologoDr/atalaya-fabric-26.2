package com.atalaya.aturdimiento;

import com.atalaya.Atalaya;
import com.mojang.serialization.Codec;
import net.fabricmc.fabric.api.attachment.v1.AttachmentRegistry;
import net.fabricmc.fabric.api.attachment.v1.AttachmentSyncPredicate;
import net.fabricmc.fabric.api.attachment.v1.AttachmentType;
import net.minecraft.network.codec.ByteBufCodecs;
import net.minecraft.resources.Identifier;
import net.minecraft.world.entity.player.Player;

/**
 * Ticks que le quedan al jugador de aturdimiento.
 *
 * El aturdimiento tiene un efecto registrado —para que salga en el inventario
 * con su icono— pero la cuenta de verdad vive AQUI, no en la duracion del
 * efecto. La razon es que hay que poder acortarla a voluntad cada vez que el
 * jugador pulsa saltar, y la duracion de un MobEffect no se puede recortar: hay
 * que quitarlo y volverlo a poner, lo que reinicia parpadeos y sonidos.
 *
 * Con un numero propio, restar medio segundo es restar diez.
 */
public final class Aturdimiento {

    /** Lo que dura de entrada: 30 segundos. */
    public static final int DURACION = 600;

    /** Lo que descuenta cada pulsacion de saltar: medio segundo. */
    public static final int POR_SALTO = 10;

    public static AttachmentType<Integer> TICKS;

    private Aturdimiento() {
    }

    public static void registrar() {
        TICKS = AttachmentRegistry.<Integer>builder()
                // Persiste a proposito: si no, bastaria con salir y entrar para
                // quitarselo, y el castigo dejaria de serlo.
                .persistent(Codec.INT)
                .initializer(() -> 0)
                // Sin copyOnDeath: morir ya es castigo suficiente, y reaparecer
                // clavado en el sitio seria ensanarse.
                .syncWith(ByteBufCodecs.VAR_INT, AttachmentSyncPredicate.targetOnly())
                .buildAndRegister(Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "aturdimiento"));
    }

    public static int de(Player jugador) {
        return jugador.getAttachedOrCreate(TICKS);
    }

    public static void poner(Player jugador, int ticks) {
        int valor = Math.max(0, ticks);
        if (de(jugador) != valor) {
            jugador.setAttached(TICKS, valor);
        }
    }

    public static boolean aturdido(Player jugador) {
        return de(jugador) > 0;
    }
}
