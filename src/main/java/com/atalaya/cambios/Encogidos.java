package com.atalaya.cambios;

import com.atalaya.Atalaya;
import com.mojang.serialization.Codec;
import net.fabricmc.fabric.api.attachment.v1.AttachmentRegistry;
import net.fabricmc.fabric.api.attachment.v1.AttachmentType;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.Identifier;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.ai.attributes.AttributeInstance;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

/**
 * ENCOGIDOS (DEDsafio 2, «Diminuto problema»): al salir el aviso, una maldicion cae sobre diez jugadores al azar (los
 * que esten) y los deja a la mitad de su tamano hasta que se apague el cambio. La marca va en el jugador (se guarda): el
 * que entra despues sigue encogido.
 */
public final class Encogidos {

    private static final Identifier MODIFICADOR = Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "cambio_encogido");
    public static AttachmentType<Boolean> MARCA;

    private Encogidos() {
    }

    static void registrar() {
        MARCA = AttachmentRegistry.<Boolean>builder()
                .persistent(Codec.BOOL)
                .copyOnDeath()
                .initializer(() -> Boolean.FALSE)
                .buildAndRegister(Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "encogido"));
    }

    static void elegir(MinecraftServer s) {
        List<ServerPlayer> todos = new ArrayList<>(s.getPlayerList().getPlayers());
        todos.removeIf(p -> p.isSpectator());
        Collections.shuffle(todos);
        for (ServerPlayer p : todos.subList(0, Math.min(10, todos.size()))) {
            p.setAttached(MARCA, true);
            poner(p, true);
            p.sendSystemMessage(Component.literal("La maldición te ha encogido.").withStyle(st -> st.withColor(0xFFD23A)));
        }
    }

    static void soltar(MinecraftServer s) {
        for (ServerPlayer p : s.getPlayerList().getPlayers()) {
            p.setAttached(MARCA, false);
            poner(p, false);
        }
    }

    static void alEntrar(ServerPlayer p) {
        boolean toca = CambiosDificultad.activo(Cambio.ENCOGIDOS) && p.getAttachedOrCreate(MARCA);
        if (!CambiosDificultad.activo(Cambio.ENCOGIDOS)) {
            p.setAttached(MARCA, false);
        }
        poner(p, toca);
    }

    private static void poner(ServerPlayer p, boolean encoger) {
        AttributeInstance escala = p.getAttribute(Attributes.SCALE);
        if (escala == null) {
            return;
        }
        if (encoger && !escala.hasModifier(MODIFICADOR)) {
            escala.addPermanentModifier(new AttributeModifier(MODIFICADOR, -0.5, AttributeModifier.Operation.ADD_MULTIPLIED_TOTAL));
        } else if (!encoger && escala.hasModifier(MODIFICADOR)) {
            escala.removeModifier(MODIFICADOR);
        }
    }
}
