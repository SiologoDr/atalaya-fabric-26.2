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

    private AtalayaRed() {
    }

    /** Registra el tipo. Tiene que correr en los DOS lados. */
    public static void registrarTipos() {
        PayloadTypeRegistry.serverboundPlay().register(Salto.TIPO, Salto.CODEC);
    }

    /** Y esto solo en el servidor: quien atiende el aviso. */
    public static void registrarServidor() {
        ServerPlayNetworking.registerGlobalReceiver(Salto.TIPO, (carga, contexto) ->
                AturdimientoManager.alSaltar(contexto.player()));
    }
}
