package com.atalaya.bestiario;

import com.atalaya.Atalaya;
import com.mojang.serialization.Codec;
import net.fabricmc.fabric.api.attachment.v1.AttachmentRegistry;
import net.fabricmc.fabric.api.attachment.v1.AttachmentSyncPredicate;
import net.fabricmc.fabric.api.attachment.v1.AttachmentType;
import net.fabricmc.fabric.api.entity.event.v1.ServerPlayerEvents;
import net.fabricmc.fabric.api.networking.v1.ServerPlayConnectionEvents;
import net.minecraft.network.codec.ByteBufCodecs;
import net.minecraft.resources.Identifier;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.ai.attributes.AttributeInstance;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;

/**
 * Los corazones que le ha robado el Espectro Negro a un jugador: son para siempre (se guardan y siguen al morir) y le
 * bajan la vida maxima, uno por cada uno. Se recupera uno con cada Corazon Blanco (Juan, 19-10-2026: «se puede volver a
 * recuperar, pero con un corazon blanco»). Nunca le deja menos de uno.
 */
public final class CorazonesRobados {

    /** Los que puede robar como mucho (de diez, siempre le queda uno). */
    public static final int MAXIMO = 9;
    private static final Identifier MODIFICADOR = Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "corazones_robados");

    public static AttachmentType<Integer> ROBADOS;

    private CorazonesRobados() {
    }

    static void registrar() {
        ROBADOS = AttachmentRegistry.<Integer>builder()
                .persistent(Codec.INT)
                .copyOnDeath()
                .syncWith(ByteBufCodecs.VAR_INT, AttachmentSyncPredicate.targetOnly())
                .initializer(() -> 0)
                .buildAndRegister(Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "corazones_robados"));
    }

    /** Al entrar y al reaparecer, la vida maxima con los que le faltan. */
    static void registrarEventos() {
        ServerPlayConnectionEvents.JOIN.register((manejador, emisor, servidor) -> aplicar(manejador.player));
        ServerPlayerEvents.AFTER_RESPAWN.register((viejo, nuevo, vivo) -> aplicar(nuevo));
    }

    public static int cuantos(ServerPlayer p) {
        return p.getAttachedOrCreate(ROBADOS);
    }

    /** Le roba uno (si le queda mas de uno). Si se lo ha robado. */
    public static boolean robar(ServerPlayer p) {
        int n = cuantos(p);
        if (n >= MAXIMO) {
            return false;
        }
        p.setAttached(ROBADOS, n + 1);
        aplicar(p);
        return true;
    }

    /** Le devuelve uno (lleno). Si le faltaba alguno. */
    public static boolean devolver(ServerPlayer p) {
        int n = cuantos(p);
        if (n <= 0) {
            return false;
        }
        p.setAttached(ROBADOS, n - 1);
        aplicar(p);
        p.heal(2.0F);
        return true;
    }

    private static void aplicar(ServerPlayer p) {
        AttributeInstance vida = p.getAttribute(Attributes.MAX_HEALTH);
        if (vida == null) {
            return;
        }
        vida.removeModifier(MODIFICADOR);
        int n = cuantos(p);
        if (n > 0) {
            vida.addTransientModifier(new AttributeModifier(MODIFICADOR, -2.0 * n, AttributeModifier.Operation.ADD_VALUE));
        }
        if (p.getHealth() > p.getMaxHealth()) {
            p.setHealth(p.getMaxHealth());
        }
    }
}
