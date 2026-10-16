package com.atalaya.momento;

import com.atalaya.Atalaya;
import com.atalaya.net.AtalayaRed;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerLifecycleEvents;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerTickEvents;
import net.fabricmc.fabric.api.networking.v1.ServerPlayConnectionEvents;
import net.fabricmc.fabric.api.networking.v1.ServerPlayNetworking;
import net.minecraft.network.chat.Component;
import net.minecraft.data.AtlasIds;
import net.minecraft.network.chat.MutableComponent;
import net.minecraft.network.chat.contents.objects.AtlasSprite;
import net.minecraft.resources.Identifier;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerPlayer;
import org.jspecify.annotations.Nullable;

/**
 * El Momento Maldicion (15-10-2026): el "momento Reviil" de DEDsafio a nuestra
 * manera. Juan: "quiero que lo hagas mil veces mejor, que me sorprendas".
 *
 * <pre>
 *   /atalaya momento_maldicion "titulo" "texto" [segundos]
 *   /atalaya momento_maldicion stop
 * </pre>
 *
 * A todos les sale a la vez la cinematica (MomentoMaldicionCliente y
 * MomentoMaldicionHud): la tinta con ojos que entra por los bordes, las
 * visiones, el titulo escrito en runas que se va leyendo y la pantalla que se
 * rompe. Al acabar, el titulo y el texto salen en el chat con una campana, y el
 * mundo se queda maldito (el cielo de sangre que se raja, la niebla, la
 * musica) hasta que se para. Con segundos, se para solo al pasar ese tiempo.
 *
 * El servidor solo lleva la cuenta y avisa: todo lo que se ve y se oye lo hace
 * cada cliente. Quien entra a mitad lo recibe ya empezado, sin la cinematica.
 * No se guarda en el mundo: si el servidor se reinicia, el momento se acaba.
 */
public final class MomentoMaldicion {

    /** Lo que dura la cinematica (ticks): el chat sale al acabar y el reloj empieza a contar ahi. */
    public static final int INTRO = 224;

    private static @Nullable MinecraftServer servidor;
    private static boolean activo;
    private static String titulo = "";
    private static String texto = "";
    /** Ticks desde que empezo, y los que dura despues de la cinematica (0, hasta que se pare). */
    private static int pasado;
    private static int duracion;
    private static boolean avisado;
    /** Los ultimos que se usaron: los repite el interruptor del menu. */
    private static String ultimoTitulo = "La maldición";
    private static String ultimoTexto = "Algo ha despertado bajo Atalaya.";
    private static int ultimaDuracion;

    private MomentoMaldicion() {
    }

    public static void registrar() {
        ServerLifecycleEvents.SERVER_STARTED.register(s -> servidor = s);
        ServerLifecycleEvents.SERVER_STOPPED.register(s -> {
            servidor = null;
            activo = false;
        });
        ServerTickEvents.END_SERVER_TICK.register(MomentoMaldicion::tick);
        // Quien entra a mitad lo recibe ya empezado (sin la cinematica).
        ServerPlayConnectionEvents.JOIN.register((manejador, envio, s) -> {
            if (activo) {
                ServerPlayNetworking.send(manejador.getPlayer(),
                        new AtalayaRed.Momento(AtalayaRed.Momento.SIGUE, titulo, texto, duracion, pasado));
            }
        });
    }

    public static boolean activo() {
        return activo;
    }

    public static String titulo() {
        return titulo;
    }

    /** Lo que le queda (ticks), o -1 si no lleva reloj. */
    public static int queda() {
        return duracion <= 0 ? -1 : Math.max(0, INTRO + duracion - pasado);
    }

    /** Empieza (o vuelve a empezar, con otro titulo) el momento para todos. */
    public static void empezar(MinecraftServer s, String nuevoTitulo, String nuevoTexto, int segundos) {
        servidor = s;
        titulo = limpiar(nuevoTitulo, 64);
        texto = limpiar(nuevoTexto, 400);
        duracion = Math.max(0, segundos) * 20;
        pasado = 0;
        avisado = false;
        activo = true;
        ultimoTitulo = titulo;
        ultimoTexto = texto;
        ultimaDuracion = segundos;
        enviar(new AtalayaRed.Momento(AtalayaRed.Momento.EMPIEZA, titulo, texto, duracion, 0));
        Atalaya.LOGGER.info("Momento maldicion: «{}» ({}).", titulo, segundos > 0 ? segundos + " s" : "sin limite");
    }

    /** Lo para para todos; false si no habia ninguno. */
    public static boolean parar() {
        if (!activo) {
            return false;
        }
        activo = false;
        enviar(new AtalayaRed.Momento(AtalayaRed.Momento.PARA, titulo, texto, 0, pasado));
        Atalaya.LOGGER.info("Momento maldicion parado.");
        return true;
    }

    /** El interruptor del menu: lo enciende con el ultimo titulo y texto, o lo para. */
    public static void interruptor(boolean encender) {
        if (encender && !activo && servidor != null) {
            empezar(servidor, ultimoTitulo, ultimoTexto, ultimaDuracion);
        } else if (!encender) {
            parar();
        }
    }

    private static void tick(MinecraftServer s) {
        if (!activo) {
            return;
        }
        pasado++;
        if (!avisado && pasado >= INTRO) {
            avisado = true;
            avisoChat(s);
        }
        if (duracion > 0 && pasado >= INTRO + duracion) {
            parar();
        }
    }

    /**
     * El aviso del chat al acabar la cinematica (la campana la toca cada cliente
     * a la vez), como el del momento de DEDsafio: el sello rojo, "MOMENTO
     * FRACTURA:" en negrita (siempre ese: el titulo del comando es el de la
     * pantalla) y el texto en rojo debajo.
     */
    private static void avisoChat(MinecraftServer s) {
        MutableComponent todo = Component.empty()
                .append(Component.object(new AtlasSprite(AtlasIds.ITEMS, ICONO)).withStyle(st -> st.withoutShadow()))
                .append(" ");
        // El rotulo en letras de metal rojo con su brillo que pasa: cuadros animados que el chat pinta seguidos.
        for (int i = 0; i < CARTEL; i++) {
            Identifier cuadro = Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, String.format("item/momento_cartel_%02d", i));
            todo.append(Component.object(new AtlasSprite(AtlasIds.ITEMS, cuadro)).withStyle(st -> st.withoutShadow()));
        }
        todo.append("\n").append(Component.literal(texto).withStyle(st -> st.withColor(0xF04A40)));
        s.getPlayerList().broadcastSystemMessage(todo, false);
    }

    /** El icono del aviso: el sello rojo y rajado (momento_maldicion.py). */
    private static final Identifier ICONO = Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "item/momento_fractura");
    /** Los cuadros del rotulo MOMENTO FRACTURA: (los que dice momento_maldicion.py al hacerlo). */
    private static final int CARTEL = 12;

    private static void enviar(AtalayaRed.Momento m) {
        if (servidor == null) {
            return;
        }
        for (ServerPlayer p : servidor.getPlayerList().getPlayers()) {
            ServerPlayNetworking.send(p, m);
        }
    }

    /** Sin saltos de linea ni codigos de color, y de un largo razonable. */
    private static String limpiar(String s, int largo) {
        String t = s.replace('\n', ' ').replace('\r', ' ').replace('§', ' ').strip();
        return t.length() > largo ? t.substring(0, largo) : t;
    }
}
