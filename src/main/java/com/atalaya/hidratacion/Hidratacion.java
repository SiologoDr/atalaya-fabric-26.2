package com.atalaya.hidratacion;

import com.atalaya.Atalaya;
import com.mojang.serialization.Codec;
import net.fabricmc.fabric.api.attachment.v1.AttachmentRegistry;
import net.fabricmc.fabric.api.attachment.v1.AttachmentSyncPredicate;
import net.fabricmc.fabric.api.attachment.v1.AttachmentType;
import net.minecraft.network.codec.ByteBufCodecs;
import net.minecraft.resources.Identifier;
import net.minecraft.world.entity.player.Player;

/**
 * Hidratacion del jugador: el agua que le queda en el cuerpo.
 *
 * Solo baja mientras esta en el desierto. Fuera se queda QUIETA, no se
 * reinicia ni se rellena: si sales de la arena con 74, al volver sigues con 74.
 * Por eso no vale con calcularla al vuelo desde el rato que llevas dentro; hay
 * que guardarla pegada al jugador.
 *
 * Se guarda con la API de attachments de Fabric, que resuelve las tres cosas
 * que hacen falta a la vez:
 *
 *   - persistent   la escribe en el fichero del jugador, asi que aguanta
 *                  desconexiones y reinicios del servidor
 *   - initializer  quien no la tenga entra con el deposito lleno, asi que
 *                  anadir la mecanica a un mundo en marcha no deja a nadie seco
 *   - syncWith     la manda al cliente sola, que es lo que le permite pintar el
 *                  medidor sin que tengamos que montar un paquete propio
 *
 * El sincronizado va en targetOnly: cada jugador recibe SOLO la suya. La de los
 * demas no le sirve de nada y serian paquetes por cada jugador y cada cambio,
 * que con un servidor de aforo alto se nota.
 */
public final class Hidratacion {

    /** Deposito lleno. Tambien es con lo que entra quien no la tenga aun. */
    public static final int MAXIMO = 100;

    /**
     * Cada cuantos ticks se pierde un punto dentro del desierto.
     *
     * 140 ticks son 7 segundos, asi que el deposito lleno da para 700 segundos
     * de desierto: unos 11 minutos y medio de exposicion continua.
     */
    public static final int TICKS_POR_PUNTO = 140;

    /**
     * El dato en si. Se registra en {@link #registrar()}, que llama
     * {@link com.atalaya.Atalaya#onInitialize()}.
     */
    public static AttachmentType<Integer> NIVEL;

    private Hidratacion() {
    }

    public static void registrar() {
        NIVEL = AttachmentRegistry.<Integer>builder()
                .persistent(Codec.INT)
                .initializer(() -> MAXIMO)
                // Sin copyOnDeath: al morir se vuelve al deposito lleno. Es lo
                // coherente con que la muerte reinicie tambien la comida y la
                // vida, y evita el bucle de reaparecer seco y volver a morir.
                .syncWith(ByteBufCodecs.VAR_INT, AttachmentSyncPredicate.targetOnly())
                .buildAndRegister(Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "hidratacion"));
    }

    /** Cuanta hidratacion le queda, de 0 a {@link #MAXIMO}. */
    public static int de(Player jugador) {
        return jugador.getAttachedOrCreate(NIVEL);
    }

    /** La deja en ese valor, recortada al rango valido. */
    public static void poner(Player jugador, int valor) {
        jugador.setAttached(NIVEL, Math.max(0, Math.min(MAXIMO, valor)));
    }

    /** Fraccion que queda, de 0.0 a 1.0. Es lo que dibuja el medidor. */
    public static float fraccion(Player jugador) {
        return de(jugador) / (float) MAXIMO;
    }
}
