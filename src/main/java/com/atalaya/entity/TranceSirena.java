package com.atalaya.entity;

import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import net.fabricmc.fabric.api.event.player.AttackEntityCallback;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;

/**
 * El trance del Canto de Sirena (Nerea, octubre de 2026). Quien lo sufre anda
 * solo hacia ella y pierde vida cada segundo; no puede atacar. Sale con clics:
 *
 * - un companero que le da (clic izquierdo, sin hacerle dano): CLIC_COMPANERO;
 * - el mismo, haciendo clic (aunque sea al aire): CLIC_PROPIO, mucho menos, para
 *   que jugando solo se pueda pero cueste.
 *
 * Aqui solo esta el indice (quien esta en trance de que Nerea) para los eventos
 * del juego; lo demas lo lleva NereaEntity.
 */
public final class TranceSirena {

    /** Los puntos de clic para salir del trance. */
    public static final int NECESARIO = 12;
    public static final int CLIC_COMPANERO = 3;
    public static final int CLIC_PROPIO = 1;

    private static final Map<UUID, NereaEntity> DE = new ConcurrentHashMap<>();

    private TranceSirena() {
    }

    static void apuntar(LivingEntity v, NereaEntity n) {
        DE.put(v.getUUID(), n);
    }

    static void quitar(LivingEntity v) {
        DE.remove(v.getUUID());
    }

    public static boolean enTrance(Entity e) {
        NereaEntity n = DE.get(e.getUUID());
        if (n == null) {
            return false;
        }
        if (n.isRemoved() || n.isDeadOrDying()) {
            DE.remove(e.getUUID());
            return false;
        }
        return true;
    }

    /** Un clic al hechizado "v" (de "quien": el mismo u otro). */
    public static void clic(ServerLevel nivel, LivingEntity v, Player quien, int puntos) {
        NereaEntity n = DE.get(v.getUUID());
        if (n != null && !n.isRemoved()) {
            n.clicTrance(nivel, v, quien, puntos);
        }
    }

    /** Lo llama la red cuando un jugador hace clic izquierdo (el brazo se mueve), aunque sea al aire. */
    public static void alGolpear(ServerPlayer jugador) {
        if (enTrance(jugador)) {
            clic((ServerLevel) jugador.level(), jugador, jugador, CLIC_PROPIO);
        }
    }

    public static void registrar() {
        // En trance no se pega a nadie; y pegarle a un hechizado lo despierta (sin hacerle dano).
        AttackEntityCallback.EVENT.register((jugador, nivel, mano, entidad, golpe) -> {
            if (nivel.isClientSide()) {
                return InteractionResult.PASS;
            }
            if (enTrance(jugador)) {
                return InteractionResult.FAIL;
            }
            if (entidad instanceof LivingEntity v && enTrance(v)) {
                clic((ServerLevel) nivel, v, jugador, CLIC_COMPANERO);
                return InteractionResult.FAIL;
            }
            return InteractionResult.PASS;
        });
    }
}
