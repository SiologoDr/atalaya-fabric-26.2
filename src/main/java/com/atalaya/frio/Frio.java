package com.atalaya.frio;

import com.atalaya.Atalaya;
import com.mojang.serialization.Codec;
import net.fabricmc.fabric.api.attachment.v1.AttachmentRegistry;
import net.fabricmc.fabric.api.attachment.v1.AttachmentSyncPredicate;
import net.fabricmc.fabric.api.attachment.v1.AttachmentType;
import net.minecraft.network.codec.ByteBufCodecs;
import net.minecraft.resources.Identifier;
import net.minecraft.world.entity.player.Player;

/**
 * Frio acumulado del jugador: lo contrario de la hidratacion.
 *
 * La hidratacion se GASTA y hay que rellenarla; el frio se ACUMULA y hay que
 * quitarselo. Por eso el medidor va al reves: el copo se llena segun te enfrias.
 *
 * Y la condicion tambien es la contraria. El desierto solo seca cuando te da el
 * sol, asi que una sombra o la noche te salvan. Aqui no: el frio es el bioma. En
 * una cueva a oscuras, de noche o bajo tierra sigues en la nieve, y lo unico que
 * lo detiene es el calor de verdad.
 *
 * Se guarda con la API de attachments igual que la hidratacion, por las mismas
 * tres razones: persiste en el fichero del jugador, quien no lo tenga entra a
 * cero, y viaja solo al cliente para que pueda pintar el medidor.
 */
public final class Frio {

    /** Congelado del todo. Se entra al mundo a cero, o sea sin frio. */
    public static final int MAXIMO = 50;

    /**
     * Cada cuantos ticks se gana un punto de frio en un bioma nevado.
     *
     * 140 ticks son 7 segundos, los mismos que tarda en perderse un punto de
     * hidratacion en el desierto: aguantar a la intemperie cuesta lo mismo en
     * los dos sitios, 5 min 50 s de reloj.
     */
    public static final int TICKS_POR_PUNTO = 140;

    /**
     * Cada cuantos ticks se pierde un punto junto al calor.
     *
     * Mucho mas rapido que ganarlo, un punto por segundo: entrar en calor son
     * 50 segundos desde congelado. Se calienta siete veces mas deprisa de lo que
     * se enfria porque quedarse quieto junto a una hoguera no puede ser un
     * castigo de cinco minutos.
     */
    public static final int TICKS_POR_PUNTO_CALOR = 20;

    /**
     * Cada cuantos ticks se pierde un punto solo por haberse ido del frio.
     *
     * Tres veces mas lento que junto al fuego: 2 min 30 s desde congelado. Salir
     * de la nieve tiene que servir de algo, o se sentiria uno atrapado, pero si
     * sirviera lo mismo que una hoguera nadie encenderia ninguna. La diferencia
     * ENTRE los dos numeros es lo que hace que valga la pena pararse a hacer
     * fuego.
     */
    public static final int TICKS_POR_PUNTO_FUERA = 60;

    public static AttachmentType<Integer> NIVEL;

    /**
     * Si la mecanica esta encendida. Existe solo para que el cliente sepa si
     * dibuja el medidor: la configuracion vive en el servidor y en red el
     * cliente no la ve.
     */
    public static AttachmentType<Boolean> ACTIVA;

    private Frio() {
    }

    public static void registrar() {
        NIVEL = AttachmentRegistry.<Integer>builder()
                .persistent(Codec.INT)
                // Se entra sin frio, al contrario que la hidratacion, que entra
                // llena. En los dos casos es el estado "sano".
                .initializer(() -> 0)
                // Sin copyOnDeath: al morir se vuelve a cero, como la comida y
                // la vida. Reaparecer congelado seria volver a morir.
                .syncWith(ByteBufCodecs.VAR_INT, AttachmentSyncPredicate.targetOnly())
                .buildAndRegister(Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "frio"));

        ACTIVA = AttachmentRegistry.<Boolean>builder()
                .initializer(() -> Boolean.FALSE)
                .syncWith(ByteBufCodecs.BOOL, AttachmentSyncPredicate.targetOnly())
                .buildAndRegister(Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "frio_activo"));
    }

    /** Cuanto frio lleva encima, de 0 a {@link #MAXIMO}. */
    public static int de(Player jugador) {
        return jugador.getAttachedOrCreate(NIVEL);
    }

    /** Lo deja en ese valor, recortado al rango valido. */
    public static void poner(Player jugador, int valor) {
        jugador.setAttached(NIVEL, Math.max(0, Math.min(MAXIMO, valor)));
    }

    /**
     * Fraccion de frio, de 0.0 a 1.0. Es lo que llena el copo.
     *
     * Ojo al sentido: aqui 1.0 es lo MALO, al reves que en la hidratacion.
     */
    public static float fraccion(Player jugador) {
        return de(jugador) / (float) MAXIMO;
    }

    /** Si la mecanica esta encendida. Lo pone el servidor, lo lee el HUD. */
    public static boolean activa(Player jugador) {
        return jugador.getAttachedOrCreate(ACTIVA);
    }
}
