package com.atalaya.net;

import com.atalaya.Atalaya;
import com.atalaya.aturdimiento.AturdimientoManager;
import net.fabricmc.fabric.api.networking.v1.PayloadTypeRegistry;
import net.fabricmc.fabric.api.networking.v1.ServerPlayNetworking;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.network.protocol.common.custom.CustomPacketPayload;
import net.minecraft.resources.Identifier;

/**
 * Lo poco que el mod manda por red a mano.
 *
 * Casi todo viaja solo: los efectos y los attachments se sincronizan sin que
 * nadie escriba un paquete. La excepcion es al reves —del cliente al
 * servidor— porque el servidor no puede saber que has pulsado la barra
 * espaciadora si el salto esta anulado: sin salto no hay movimiento que
 * delate la tecla.
 */
public final class AtalayaRed {

    /**
     * "He pulsado saltar".
     *
     * No lleva datos: el hecho de que llegue ya lo dice todo, y quien lo manda
     * se sabe por la conexion. Un paquete vacio es tambien el mas barato de
     * validar.
     */
    public record Salto() implements CustomPacketPayload {

        public static final Type<Salto> TIPO = new Type<>(
                Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "salto"));

        public static final StreamCodec<FriendlyByteBuf, Salto> CODEC =
                StreamCodec.unit(new Salto());

        @Override
        public Type<Salto> type() {
            return TIPO;
        }
    }

    /**
     * Una tecla de la Ofrenda al Sol (la secuencia que sale en pantalla a quien
     * Novilis tiene en las manos): que jefe, que tecla de la secuencia y si era
     * la buena. La secuencia la saca cada lado de la misma semilla, asi que basta
     * con decir si acerto: el servidor lleva la cuenta y decide.
     */
    public record OfrendaTecla(int jefe, int indice, boolean bien) implements CustomPacketPayload {

        public static final Type<OfrendaTecla> TIPO = new Type<>(
                Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "ofrenda_tecla"));

        public static final StreamCodec<FriendlyByteBuf, OfrendaTecla> CODEC = StreamCodec.of(
                (buf, t) -> {
                    buf.writeVarInt(t.jefe());
                    buf.writeVarInt(t.indice());
                    buf.writeBoolean(t.bien());
                },
                buf -> new OfrendaTecla(buf.readVarInt(), buf.readVarInt(), buf.readBoolean()));

        @Override
        public Type<OfrendaTecla> type() {
            return TIPO;
        }
    }

    /**
     * Una nota del Duelo de Canto de Nerea (el elegido sigue el ritmo): que jefe,
     * que nota y si la acerto. Las notas las saca cada lado de la misma semilla;
     * el cliente juzga al momento (el lag no hace fallar) y el servidor cuenta.
     */
    public record DueloNota(int jefe, int indice, boolean bien) implements CustomPacketPayload {

        public static final Type<DueloNota> TIPO = new Type<>(
                Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "duelo_nota"));

        public static final StreamCodec<FriendlyByteBuf, DueloNota> CODEC = StreamCodec.of(
                (buf, t) -> {
                    buf.writeVarInt(t.jefe());
                    buf.writeVarInt(t.indice());
                    buf.writeBoolean(t.bien());
                },
                buf -> new DueloNota(buf.readVarInt(), buf.readVarInt(), buf.readBoolean()));

        @Override
        public Type<DueloNota> type() {
            return TIPO;
        }
    }

    /**
     * "He pulsado la tecla de la habilidad" (R por defecto). Sin datos: el
     * servidor mira que conjunto lleva y si la tiene lista.
     */
    public record Habilidad() implements CustomPacketPayload {

        public static final Type<Habilidad> TIPO = new Type<>(
                Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "habilidad"));

        public static final StreamCodec<FriendlyByteBuf, Habilidad> CODEC =
                StreamCodec.unit(new Habilidad());

        @Override
        public Type<Habilidad> type() {
            return TIPO;
        }
    }

    /**
     * El Momento Maldicion (MomentoMaldicion), del servidor a cada cliente: el
     * unico paquete que va en ese sentido, porque no hay entidad que lo lleve.
     *
     * @param accion   EMPIEZA (con la cinematica), SIGUE (quien entra a mitad: sin
     *                 ella) o PARA
     * @param duracion ticks que dura despues de la cinematica (0, hasta que se pare)
     * @param pasado   ticks desde que empezo (para el reloj de quien entra a mitad)
     * @param contador lo que dura el contador de la prueba, desde que acaba la cinematica (ticks; 0, sin prueba)
     * @param semilla  la del cielo roto, la misma para todos (que todos vean las mismas grietas)
     */
    public record Momento(int accion, String titulo, String texto, int duracion, int pasado, int contador, int semilla)
            implements CustomPacketPayload {

        public static final int EMPIEZA = 0;
        public static final int SIGUE = 1;
        public static final int PARA = 2;

        public static final Type<Momento> TIPO = new Type<>(
                Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "momento"));

        public static final StreamCodec<FriendlyByteBuf, Momento> CODEC = StreamCodec.of(
                (buf, m) -> {
                    buf.writeVarInt(m.accion());
                    buf.writeUtf(m.titulo(), 256);
                    buf.writeUtf(m.texto(), 1024);
                    buf.writeVarInt(m.duracion());
                    buf.writeVarInt(m.pasado());
                    buf.writeVarInt(m.contador());
                    buf.writeInt(m.semilla());
                },
                buf -> new Momento(buf.readVarInt(), buf.readUtf(256), buf.readUtf(1024), buf.readVarInt(), buf.readVarInt(),
                        buf.readVarInt(), buf.readInt()));

        @Override
        public Type<Momento> type() {
            return TIPO;
        }
    }

    /**
     * El Fogonazo te ha estallado cerca: la pantalla en blanco. "blanco" son los ticks en que se queda blanca del todo y
     * "funde" los que tarda en irse; el cliente se queda con el mas largo si le llegan dos.
     */
    public record Deslumbre(int blanco, int funde) implements CustomPacketPayload {

        public static final Type<Deslumbre> TIPO = new Type<>(
                Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "deslumbre"));

        public static final StreamCodec<FriendlyByteBuf, Deslumbre> CODEC = StreamCodec.of(
                (buf, d) -> {
                    buf.writeVarInt(d.blanco());
                    buf.writeVarInt(d.funde());
                },
                buf -> new Deslumbre(buf.readVarInt(), buf.readVarInt()));

        @Override
        public Type<Deslumbre> type() {
            return TIPO;
        }
    }

    /**
     * La Ruleta (Ruleta), del servidor a cada cliente: que salga la tragaperras y en que final para, o que se quite.
     *
     * @param accion  TIRA o PARA
     * @param fin     el final (el orden de Ruleta.Fin: mob, dificultad, penalizacion, minijuego)
     * @param semilla la de la tira de iconos del rodillo, la misma para todos
     */
    public record Ruleta(int accion, int fin, int semilla) implements CustomPacketPayload {

        public static final int TIRA = 0;
        public static final int PARA = 1;

        public static final Type<Ruleta> TIPO = new Type<>(
                Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "ruleta"));

        public static final StreamCodec<FriendlyByteBuf, Ruleta> CODEC = StreamCodec.of(
                (buf, r) -> {
                    buf.writeVarInt(r.accion());
                    buf.writeVarInt(r.fin());
                    buf.writeInt(r.semilla());
                },
                buf -> new Ruleta(buf.readVarInt(), buf.readVarInt(), buf.readInt()));

        @Override
        public Type<Ruleta> type() {
            return TIPO;
        }
    }

    /**
     * El estado de una fila de un menu del catalogo (un cambio, un mob o un momento, por su id).
     *
     * @param estado APAGADO, ENCENDIDO o ESPERA (esperando a que pare su Ruleta)
     * @param quedan los ticks que le quedan a uno que dura (0, los que no duran)
     */
    public record EstadoCambio(String id, int estado, int quedan) {
        public static final int APAGADO = 0;
        public static final int ENCENDIDO = 1;
        public static final int ESPERA = 2;
    }

    /**
     * Un menu del catalogo (la categoria: com.atalaya.catalogo.Categoria por su numero): abrirlo con su estado (abrir) o
     * solo ponerlo al dia si esta abierto.
     */
    public record MenuCatalogo(int categoria, boolean abrir, java.util.List<EstadoCambio> estados)
            implements CustomPacketPayload {

        public static final Type<MenuCatalogo> TIPO = new Type<>(
                Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "menu_catalogo"));

        public static final StreamCodec<FriendlyByteBuf, MenuCatalogo> CODEC = StreamCodec.of(
                (buf, m) -> {
                    buf.writeVarInt(m.categoria());
                    buf.writeBoolean(m.abrir());
                    buf.writeVarInt(m.estados().size());
                    for (EstadoCambio e : m.estados()) {
                        buf.writeUtf(e.id(), 64);
                        buf.writeVarInt(e.estado());
                        buf.writeVarInt(e.quedan());
                    }
                },
                buf -> {
                    int categoria = buf.readVarInt();
                    boolean abrir = buf.readBoolean();
                    int n = buf.readVarInt();
                    java.util.List<EstadoCambio> estados = new java.util.ArrayList<>();
                    for (int i = 0; i < n; i++) {
                        estados.add(new EstadoCambio(buf.readUtf(64), buf.readVarInt(), buf.readVarInt()));
                    }
                    return new MenuCatalogo(categoria, abrir, estados);
                });

        @Override
        public Type<MenuCatalogo> type() {
            return TIPO;
        }
    }

    /** El menu de las dimensiones: abrirlo (abrir) o ponerlo al dia; si el Nether y el End estan abiertos. */
    public record MenuDimensiones(boolean abrir, boolean nether, boolean end) implements CustomPacketPayload {

        public static final Type<MenuDimensiones> TIPO = new Type<>(
                Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "menu_dimensiones"));

        public static final StreamCodec<FriendlyByteBuf, MenuDimensiones> CODEC = StreamCodec.of(
                (buf, m) -> {
                    buf.writeBoolean(m.abrir());
                    buf.writeBoolean(m.nether());
                    buf.writeBoolean(m.end());
                },
                buf -> new MenuDimensiones(buf.readBoolean(), buf.readBoolean(), buf.readBoolean()));

        @Override
        public Type<MenuDimensiones> type() {
            return TIPO;
        }
    }

    /** "He pulsado esta fila de este menu del catalogo" (el servidor mira que sea operador). */
    public record PulsaCatalogo(int categoria, String id) implements CustomPacketPayload {

        public static final Type<PulsaCatalogo> TIPO = new Type<>(
                Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "pulsa_catalogo"));

        public static final StreamCodec<FriendlyByteBuf, PulsaCatalogo> CODEC = StreamCodec.of(
                (buf, m) -> {
                    buf.writeVarInt(m.categoria());
                    buf.writeUtf(m.id(), 64);
                },
                buf -> new PulsaCatalogo(buf.readVarInt(), buf.readUtf(64)));

        @Override
        public Type<PulsaCatalogo> type() {
            return TIPO;
        }
    }

    /** "He pulsado esta dimension en el menu" (0, el Nether; 1, el End). */
    public record PulsaDimension(int cual) implements CustomPacketPayload {

        public static final Type<PulsaDimension> TIPO = new Type<>(
                Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "pulsa_dimension"));

        public static final StreamCodec<FriendlyByteBuf, PulsaDimension> CODEC = StreamCodec.of(
                (buf, m) -> buf.writeVarInt(m.cual()),
                buf -> new PulsaDimension(buf.readVarInt()));

        @Override
        public Type<PulsaDimension> type() {
            return TIPO;
        }
    }

    private AtalayaRed() {
    }

    /** Registra el tipo. Tiene que correr en los DOS lados. */
    public static void registrarTipos() {
        PayloadTypeRegistry.serverboundPlay().register(Salto.TIPO, Salto.CODEC);
        PayloadTypeRegistry.serverboundPlay().register(OfrendaTecla.TIPO, OfrendaTecla.CODEC);
        PayloadTypeRegistry.serverboundPlay().register(Habilidad.TIPO, Habilidad.CODEC);
        PayloadTypeRegistry.serverboundPlay().register(DueloNota.TIPO, DueloNota.CODEC);
        PayloadTypeRegistry.clientboundPlay().register(Momento.TIPO, Momento.CODEC);
        PayloadTypeRegistry.clientboundPlay().register(Deslumbre.TIPO, Deslumbre.CODEC);
        PayloadTypeRegistry.clientboundPlay().register(Ruleta.TIPO, Ruleta.CODEC);
        PayloadTypeRegistry.clientboundPlay().register(MenuCatalogo.TIPO, MenuCatalogo.CODEC);
        PayloadTypeRegistry.clientboundPlay().register(MenuDimensiones.TIPO, MenuDimensiones.CODEC);
        PayloadTypeRegistry.serverboundPlay().register(PulsaCatalogo.TIPO, PulsaCatalogo.CODEC);
        PayloadTypeRegistry.serverboundPlay().register(PulsaDimension.TIPO, PulsaDimension.CODEC);
    }

    private static boolean esOperador(net.minecraft.server.level.ServerPlayer p) {
        return net.minecraft.commands.Commands.LEVEL_GAMEMASTERS.check(p.createCommandSourceStack().permissions());
    }

    /** Y esto solo en el servidor: quien atiende el aviso. */
    public static void registrarServidor() {
        ServerPlayNetworking.registerGlobalReceiver(Salto.TIPO, (carga, contexto) ->
                AturdimientoManager.alSaltar(contexto.player()));
        ServerPlayNetworking.registerGlobalReceiver(OfrendaTecla.TIPO, (carga, contexto) ->
                com.atalaya.entity.NovilisEntity.alPulsarTecla(contexto.player(), carga.jefe(), carga.indice(), carga.bien()));
        ServerPlayNetworking.registerGlobalReceiver(DueloNota.TIPO, (carga, contexto) ->
                com.atalaya.entity.NereaEntity.alNotaDuelo(contexto.player(), carga.jefe(), carga.indice(), carga.bien()));
        ServerPlayNetworking.registerGlobalReceiver(Habilidad.TIPO, (carga, contexto) ->
                com.atalaya.habilidad.Habilidades.activar(contexto.player()));
        // Los menus del catalogo y el de las dimensiones: solo los operadores (el menu se abre con un comando suyo, pero
        // el paquete lo podria mandar cualquiera).
        ServerPlayNetworking.registerGlobalReceiver(PulsaCatalogo.TIPO, (carga, contexto) -> {
            com.atalaya.catalogo.Categoria[] todas = com.atalaya.catalogo.Categoria.values();
            if (carga.categoria() >= 0 && carga.categoria() < todas.length && esOperador(contexto.player())) {
                com.atalaya.catalogo.Catalogo.pulsar(contexto.player(), todas[carga.categoria()], carga.id());
            }
        });
        ServerPlayNetworking.registerGlobalReceiver(PulsaDimension.TIPO, (carga, contexto) -> {
            if ((carga.cual() == 0 || carga.cual() == 1) && esOperador(contexto.player())) {
                com.atalaya.cambios.CambiosDificultad.pulsarDimension(contexto.player(), carga.cual());
            }
        });
    }
}
