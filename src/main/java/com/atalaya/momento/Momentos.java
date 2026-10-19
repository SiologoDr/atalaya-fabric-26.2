package com.atalaya.momento;

import com.atalaya.Atalaya;
import com.atalaya.catalogo.Catalogo;
import com.atalaya.catalogo.Categoria;
import com.atalaya.net.AtalayaRed;
import net.fabricmc.fabric.api.entity.event.v1.ServerPlayerEvents;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerLifecycleEvents;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerTickEvents;
import net.fabricmc.fabric.api.networking.v1.ServerPlayConnectionEvents;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerPlayer;
import org.jspecify.annotations.Nullable;

import java.util.ArrayList;
import java.util.List;

/**
 * Los momentos del catalogo en marcha (/atalaya menu momentos): uno a la vez, como el Momento Fractura, que es quien los
 * presenta. Encender uno lanza la cinematica con su titulo y, al salir el aviso del chat, empieza su Suceso; acaba con su
 * tiempo, con OFF o al encender otro. No se guarda en el mundo: si el servidor se para, el momento se acaba.
 */
public final class Momentos {

    /** Lo que sigue despues de que el contador llegue a cero, antes de irse (como la prueba de la tierra). */
    public static final int TRAS_CONTADOR = MomentoMaldicion.TRAS_PRUEBA;

    /** Los mobs del bestiario que CUALQUIER COSA puede sacar (se apuntan al registrarse). */
    public static final List<java.util.function.Supplier<net.minecraft.world.entity.EntityType<? extends net.minecraft.world.entity.Mob>>>
            EXTRA_CUALQUIERA = new ArrayList<>();
    /** Lo que los momentos cierran mientras duran: el Nether (los meteoritos) y la vuelta del Nether (la tormenta). */
    private static boolean netherCerrado;
    private static boolean vueltaCerrada;

    /** Lo que se acortan los contadores (1: normal; para las pruebas, menos). Lo leen los sucesos al crearse. */
    private static float prisa = 1.0F;

    public static void prisa(float k) {
        prisa = k;
    }

    /** Unos segundos en ticks, con la prisa de las pruebas. */
    static int ticks(int segundos) {
        return Math.max(20, Math.round(segundos * 20 * prisa));
    }

    private static @Nullable Momento actual;
    private static @Nullable Suceso suceso;
    private static boolean empezado;
    private static int t;

    private Momentos() {
    }

    public static void registrar() {
        ServerTickEvents.END_SERVER_TICK.register(Momentos::tick);
        EfectosMomento.registrar();
        // Las pruebas: lo que se rompe y lo que se mata mientras corre su contador.
        net.fabricmc.fabric.api.event.player.PlayerBlockBreakEvents.AFTER.register((nivel, jugador, pos, estado, be) -> {
            if (suceso != null && empezado && jugador instanceof ServerPlayer p) {
                SucesosPrueba.romper(suceso, p, estado, t);
            }
        });
        net.fabricmc.fabric.api.entity.event.v1.ServerLivingEntityEvents.AFTER_DEATH.register((muerto, fuente) -> {
            if (suceso != null && empezado) {
                SucesosPrueba.matar(suceso, fuente.getEntity(), muerto, t);
            }
        });
        // La sequia: los cubos no se llenan de agua.
        net.fabricmc.fabric.api.event.player.UseItemCallback.EVENT.register((jugador, mundo, mano) -> {
            if (activo(Momento.SEQUIA) && jugador.getItemInHand(mano).is(net.minecraft.world.item.Items.BUCKET)) {
                return net.minecraft.world.InteractionResult.FAIL;
            }
            return net.minecraft.world.InteractionResult.PASS;
        });
        ServerLifecycleEvents.SERVER_STOPPING.register(s -> {
            if (actual != null) {
                MomentoMaldicion.parar();
            }
        });
        ServerPlayConnectionEvents.JOIN.register((manejador, envio, s) -> {
            if (suceso != null && empezado) {
                suceso.alEntrar(manejador.getPlayer());
            }
        });
        ServerPlayerEvents.AFTER_RESPAWN.register((viejo, nuevo, vivo) -> {
            if (suceso != null && empezado) {
                suceso.alEntrar(nuevo);
            }
        });
    }

    /** El momento en marcha (o null). */
    public static @Nullable Momento actual() {
        return actual;
    }

    /** Su Suceso, si ya empezo (el aviso del chat ha salido). */
    public static @Nullable Suceso suceso() {
        return empezado ? suceso : null;
    }

    /** Si ese momento esta en marcha y ya empezo. */
    public static boolean activo(Momento m) {
        return actual == m && empezado;
    }

    /** Acaba el momento en marcha (lo piden los que terminan solos: la horda vencida, todos curados...). */
    public static void terminar() {
        if (actual != null) {
            MomentoMaldicion.parar();
        }
    }

    static void cerrarNether(boolean cerrar) {
        netherCerrado = cerrar;
    }

    static void cerrarVuelta(boolean cerrar) {
        vueltaCerrada = cerrar;
    }

    /** Si un momento tiene cerrado el Nether (los portales no llevan a el). */
    public static boolean netherCerrado() {
        return netherCerrado;
    }

    /** Si un momento tiene cerrada la vuelta del Nether al mundo. */
    public static boolean vueltaCerrada() {
        return vueltaCerrada;
    }

    /** Si los mobs no arden al sol ahora (el eclipse). */
    public static boolean sinSol() {
        return activo(Momento.EL_ECLIPSE);
    }

    /** La Pildora del Tamano: si los diminutos estan en marcha, cura a quien se la toma. */
    public static boolean pildoraTamano(ServerPlayer p) {
        return SucesosRegla.pildoraTamano(p);
    }

    /** El interruptor del menu: si esta en marcha, se acaba; si no, empieza (y acaba el que hubiera). */
    public static void pulsar(ServerPlayer jugador, Momento m) {
        prisa = 1.0F;
        MinecraftServer s = jugador.level().getServer();
        if (actual == m) {
            MomentoMaldicion.parar();
            Atalaya.LOGGER.info("Momento apagado por {}: {}", jugador.getName().getString(), m.id());
            return;
        }
        lanzar(s, m);
        Atalaya.LOGGER.info("Momento encendido por {}: {}", jugador.getName().getString(), m.id());
    }

    /** Lanza el momento para todos: la cinematica del Momento Fractura con su titulo, y luego lo suyo. */
    public static void lanzar(MinecraftServer s, Momento m) {
        Suceso nuevo = m.crear();
        int cont = nuevo.contador();
        // Con contador: acaba un rato despues de llegar a cero. Sin el: lo que diga el momento (0, hasta que se pare).
        int segundos = cont > 0 ? (cont + nuevo.despues() + 19) / 20 : m.segundos;
        MomentoMaldicion.empezarCatalogo(s, m.titulo(), m.texto(), segundos, cont,
                () -> {
                    if (suceso == nuevo) {
                        empezado = true;
                        t = 0;
                        nuevo.empieza(s);
                        Catalogo.enviarEstado(s, Categoria.MOMENTO);
                    }
                },
                () -> {
                    if (suceso == nuevo) {
                        if (empezado) {
                            nuevo.acaba(s);
                        }
                        actual = null;
                        suceso = null;
                        empezado = false;
                        netherCerrado = false;
                        vueltaCerrada = false;
                        Catalogo.enviarEstado(s, Categoria.MOMENTO);
                    }
                });
        actual = m;
        suceso = nuevo;
        empezado = false;
        t = 0;
        Catalogo.enviarEstado(s, Categoria.MOMENTO);
    }

    private static void tick(MinecraftServer s) {
        if (suceso != null && empezado) {
            suceso.tick(s, t);
            t++;
        }
    }

    /** El estado de todos, para el menu: el que esta en marcha, encendido (o en espera durante la cinematica). */
    public static List<AtalayaRed.EstadoCambio> estados(MinecraftServer s) {
        List<AtalayaRed.EstadoCambio> out = new ArrayList<>();
        for (Momento m : Momento.values()) {
            int estado = AtalayaRed.EstadoCambio.APAGADO;
            int quedan = 0;
            if (m == actual) {
                estado = empezado ? AtalayaRed.EstadoCambio.ENCENDIDO : AtalayaRed.EstadoCambio.ESPERA;
                quedan = Math.max(0, MomentoMaldicion.queda());
            }
            out.add(new AtalayaRed.EstadoCambio(m.id(), estado, quedan));
        }
        return out;
    }
}
