package com.atalaya.bestiario;

import com.atalaya.Atalaya;
import net.fabricmc.fabric.api.networking.v1.PayloadTypeRegistry;
import net.fabricmc.fabric.api.networking.v1.ServerPlayNetworking;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.network.protocol.common.custom.CustomPacketPayload;
import net.minecraft.resources.Identifier;
import net.minecraft.server.level.ServerPlayer;

/**
 * Lo que los mobs del bestiario le ponen en la pantalla a un jugador (lo pinta PantallasBestias, en el cliente):
 *
 * <pre>
 *   SIN_SENAL   la estatica con su rotulo (el Creeper Gelatina)
 *   NATA        los pegotes de nata que chorrean (el Creeper Tarta)
 *   ALUCINACION la pantalla que se tuerce de colores (la Hormiga Polvorin)
 * </pre>
 *
 * Y del cliente al servidor, el forcejeo con las lianas del Creeper Enredadera: «he pulsado la tecla que toca» (el
 * servidor no se entera solo: atrapado no se mueve).
 */
public final class BestiaRed {

    public static final int SIN_SENAL = 0;
    public static final int NATA = 1;
    public static final int ALUCINACION = 2;

    /** Que pantalla y cuanto dura (ticks). */
    public record Pantalla(int cual, int ticks) implements CustomPacketPayload {

        public static final Type<Pantalla> TIPO = new Type<>(Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "pantalla_bestia"));

        public static final StreamCodec<FriendlyByteBuf, Pantalla> CODEC = StreamCodec.of(
                (buf, p) -> {
                    buf.writeVarInt(p.cual());
                    buf.writeVarInt(p.ticks());
                },
                buf -> new Pantalla(buf.readVarInt(), buf.readVarInt()));

        @Override
        public Type<Pantalla> type() {
            return TIPO;
        }
    }

    /** Una pulsacion de la tecla que suelta las lianas. */
    public record Forcejeo() implements CustomPacketPayload {

        public static final Type<Forcejeo> TIPO = new Type<>(Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "forcejeo"));

        public static final StreamCodec<FriendlyByteBuf, Forcejeo> CODEC = StreamCodec.unit(new Forcejeo());

        @Override
        public Type<Forcejeo> type() {
            return TIPO;
        }
    }

    private BestiaRed() {
    }

    public static void registrar() {
        PayloadTypeRegistry.clientboundPlay().register(Pantalla.TIPO, Pantalla.CODEC);
        PayloadTypeRegistry.serverboundPlay().register(Forcejeo.TIPO, Forcejeo.CODEC);
        ServerPlayNetworking.registerGlobalReceiver(Forcejeo.TIPO, (carga, contexto) ->
                com.atalaya.bestiario.mobs.EnredaderaEntity.alForcejear(contexto.player()));
    }

    public static void pantalla(ServerPlayer jugador, int cual, int ticks) {
        if (ServerPlayNetworking.canSend(jugador, Pantalla.TIPO)) {
            ServerPlayNetworking.send(jugador, new Pantalla(cual, ticks));
        }
    }
}
