package com.atalaya.momento;

import com.atalaya.Atalaya;
import com.atalaya.net.AtalayaRed;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerLifecycleEvents;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerTickEvents;
import net.fabricmc.fabric.api.networking.v1.ServerPlayNetworking;
import net.minecraft.data.AtlasIds;
import net.minecraft.network.chat.Component;
import net.minecraft.network.chat.MutableComponent;
import net.minecraft.network.chat.contents.objects.AtlasSprite;
import net.minecraft.resources.Identifier;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerPlayer;
import org.jspecify.annotations.Nullable;

import java.util.ArrayDeque;

/**
 * La Ruleta (17-10-2026): los cambios de dificultad de Atalaya, como la ruleta de DEDsafio pero a nuestra manera.
 * Juan: "vamos a hacer como un casino pero no de 3 sino de solo 1 ... la casilla se mueva, mueva, mueva y pare"; una
 * misma animacion con cuatro finales, cada uno con su color en el chat: el huevo con la interrogacion (un mob nuevo,
 * naranja), la advertencia (un cambio de dificultad, amarillo), la penalizacion (celeste) y el minijuego (verde).
 *
 * <pre>
 *   /atalaya ruleta mob|dificultad|penalizacion|minijuego [texto]
 *   /atalaya ruleta stop
 * </pre>
 *
 * A todos les sale a la vez la tragaperras (RuletaCliente y RuletaHud), un medallon que entra ya girando: el rodillo
 * va a tope, frena con suspense y para en el final que toca. Cuando se va, sale el aviso en el chat: el icono del final, su rotulo
 * en letras de su color (NUEVO MOB:, CAMBIO DE DIFICULTAD:, PENALIZACION:, MINIJUEGO:, con el brillo que lo cruza) y el
 * texto de ese color debajo.
 *
 * Si se tiran varias seguidas, esperan su turno: cada una sale cuando acaba la anterior. El servidor solo lleva la
 * cola y el aviso; lo que se ve y se oye lo hace cada cliente. Quien entra a mitad de una tirada no la ve (le llega el
 * aviso igual). No se guarda en el mundo.
 */
public final class Ruleta {

    /** Los finales, en el orden del rodillo (el mismo que ruleta.py y RuletaHud). */
    public enum Fin {
        MOB("mob", "nuevo mob", 0xFF9A3C, 9),
        DIFICULTAD("dificultad", "cambio de dificultad", 0xFFD23A, 18),
        PENALIZACION("penalizacion", "penalización", 0x7FD8FF, 12),
        MINIJUEGO("minijuego", "minijuego", 0x6EE36E, 9);

        /** La palabra del comando (y el nombre de sus texturas). */
        public final String nombre;
        /** Como se dice al confirmar el comando. */
        public final String dicho;
        /** El color del texto en el chat. */
        public final int color;
        /** Los cuadros de su rotulo (los que dice ruleta.py al hacerlo). */
        public final int cartel;

        Fin(String nombre, String dicho, int color, int cartel) {
            this.nombre = nombre;
            this.dicho = dicho;
            this.color = color;
            this.cartel = cartel;
        }
    }

    /** Ticks desde que sale la tragaperras hasta el aviso del chat (RuletaCliente.T_AVISO). */
    public static final int AVISO = 206;
    /** Lo que dura una tirada en el cliente (RuletaCliente.T_FIN) mas un respiro: la siguiente de la cola sale despues. */
    public static final int TURNO = 214 + 16;
    private static final java.util.Random AZAR = new java.util.Random();

    /**
     * Una tirada: el final, el texto del aviso y, si es la de un cambio de dificultad (CambiosDificultad), su propio
     * rotulo (los cuadros cartel_NN, en vez del del final) y lo que hay que hacer al salir el aviso o si se quita antes.
     */
    private record Tirada(Fin fin, String texto, @Nullable String cartel, int cuadros, @Nullable Runnable alAvisar,
                          @Nullable Runnable alQuitar) {
    }

    private static final ArrayDeque<Tirada> cola = new ArrayDeque<>();
    private static @Nullable Tirada actual;
    private static int pasado;

    private Ruleta() {
    }

    public static void registrar() {
        ServerLifecycleEvents.SERVER_STOPPED.register(s -> {
            cola.clear();
            actual = null;
        });
        ServerTickEvents.END_SERVER_TICK.register(Ruleta::tick);
    }

    /**
     * Tira la ruleta para todos con ese final y ese texto (puede ir vacio: solo sale el rotulo). Devuelve las que
     * tiene delante en la cola (0, sale ya).
     */
    public static int tirar(MinecraftServer s, Fin fin, String texto) {
        return encolar(s, new Tirada(fin, limpiar(texto, 400), null, 0, null, null), texto);
    }

    /**
     * La tirada de un cambio de dificultad: el rotulo del chat es el de su titulo (los cuadros item/cartel_NN) y, al
     * salir el aviso, alAvisar (se aplica el cambio); si se quita antes con stop, alQuitar.
     */
    public static int tirarCambio(MinecraftServer s, Fin fin, String texto, String cartel, int cuadros, Runnable alAvisar,
                                  Runnable alQuitar) {
        return encolar(s, new Tirada(fin, limpiar(texto, 400), cartel, cuadros, alAvisar, alQuitar), texto);
    }

    private static int encolar(MinecraftServer s, Tirada tirada, String texto) {
        Fin fin = tirada.fin();
        cola.add(tirada);
        int delante = cola.size() - 1 + (actual != null ? 1 : 0);
        if (actual == null) {
            siguiente(s);
        }
        Atalaya.LOGGER.info("Ruleta: {} «{}»{}.", fin.nombre, texto, delante > 0 ? " (en cola, " + delante + " delante)" : "");
        return delante;
    }

    /** Quita la tirada en marcha y vacia la cola; devuelve cuantas habia (0, ninguna). */
    public static int parar(MinecraftServer s) {
        int habia = cola.size() + (actual != null ? 1 : 0);
        for (Tirada t : cola) {
            if (t.alQuitar() != null) {
                t.alQuitar().run();
            }
        }
        cola.clear();
        if (actual != null) {
            // Si ya salio su aviso (el cambio ya se aplico), no hay nada que deshacer.
            if (actual.alQuitar() != null && pasado < AVISO) {
                actual.alQuitar().run();
            }
            actual = null;
            for (ServerPlayer p : s.getPlayerList().getPlayers()) {
                ServerPlayNetworking.send(p, new AtalayaRed.Ruleta(AtalayaRed.Ruleta.PARA, 0, 0));
            }
        }
        return habia;
    }

    private static void siguiente(MinecraftServer s) {
        actual = cola.poll();
        pasado = 0;
        if (actual == null) {
            return;
        }
        // La semilla de la tira de iconos: la misma para todos, distinta en cada tirada.
        AtalayaRed.Ruleta tirada = new AtalayaRed.Ruleta(AtalayaRed.Ruleta.TIRA, actual.fin().ordinal(), AZAR.nextInt());
        for (ServerPlayer p : s.getPlayerList().getPlayers()) {
            ServerPlayNetworking.send(p, tirada);
        }
    }

    private static void tick(MinecraftServer s) {
        if (actual == null) {
            return;
        }
        pasado++;
        if (pasado == AVISO) {
            avisoChat(s, actual);
        }
        if (pasado >= TURNO) {
            siguiente(s);
        }
    }

    /**
     * El aviso del chat, a la vez que el icono llega volando: el icono del final, el rotulo en letras de su color
     * (cuadros animados que el chat pinta seguidos) y el texto de su color debajo.
     */
    private static void avisoChat(MinecraftServer s, Tirada tirada) {
        Fin fin = tirada.fin();
        MutableComponent todo = Component.empty()
                .append(sprite("item/ruleta_" + fin.nombre))
                .append(" ");
        if (tirada.cartel() != null) {
            // Un cambio de dificultad: su titulo en vez de CAMBIO DE DIFICULTAD.
            for (int i = 0; i < tirada.cuadros(); i++) {
                todo.append(sprite(String.format("item/%s_%02d", tirada.cartel(), i)));
            }
        } else {
            for (int i = 0; i < fin.cartel; i++) {
                todo.append(sprite(String.format("item/ruleta_%s_cartel_%02d", fin.nombre, i)));
            }
        }
        if (!tirada.texto().isEmpty()) {
            todo.append("\n").append(Component.literal(tirada.texto()).withStyle(st -> st.withColor(fin.color)));
        }
        s.getPlayerList().broadcastSystemMessage(todo, false);
        if (tirada.alAvisar() != null) {
            tirada.alAvisar().run();
        }
    }

    private static MutableComponent sprite(String ruta) {
        return Component.object(new AtlasSprite(AtlasIds.ITEMS, Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, ruta)))
                .withStyle(st -> st.withoutShadow());
    }

    /** Sin saltos de linea ni codigos de color, y de un largo razonable. */
    private static String limpiar(String s, int largo) {
        String t = s.replace('\n', ' ').replace('\r', ' ').replace('§', ' ').strip();
        return t.length() > largo ? t.substring(0, largo) : t;
    }
}
