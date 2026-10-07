package com.atalaya.client;

import com.atalaya.Atalaya;
import com.atalaya.entity.AeralisEntity;
import com.atalaya.entity.NereaEntity;
import com.atalaya.entity.NovilisEntity;
import com.atalaya.entity.RajangEntity;
import java.util.HashMap;
import java.util.Map;
import net.minecraft.client.Minecraft;
import net.minecraft.resources.Identifier;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;
import org.jspecify.annotations.Nullable;

/**
 * Los corazones del jugador en combate con un jefe: los corazones normales y su
 * hueco vacio se pintan con los de ese jefe (hud/heart/<jefe>_*.png, en el atlas
 * de la interfaz, animados: corazones_jefes.py, opcion C). Los de veneno,
 * wither, congelado y absorcion se quedan como en vanilla: son datos y no se tocan.
 *
 * Duran la batalla entera (Juan, 07-10-2026: que no cambien al acercarse o
 * alejarse del jefe): empieza cuando hay uno despierto a menos de CERCA (lo que
 * hace salir su barra) y acaba cuando muere. Si deja de verse sin morir (el
 * jugador se fue lejos), se siguen viendo OLVIDO ticks por si vuelve. Al cambiar
 * de mundo o de dimension se acaba, y vuelve a empezar al acercarse otra vez.
 *
 * Solo se cambia el dibujo (el mixin CorazonesJefeMixin, en HeartType.getSprite):
 * el parpadeo al recibir dano, el temblor con poca vida y el salto al regenerar
 * siguen siendo los de vanilla.
 */
public final class CorazonesJefe {

    /** Hasta donde cuenta como combate (bloques): lo mismo que las barras de los jefes. */
    private static final double CERCA = 120.0;
    private static final String[] JEFES = {"nerea", "aeralis", "rajang", "novilis"};
    /** Los sprites de cada jefe: lleno, lleno al parpadear, medio, medio al parpadear, hueco, hueco al parpadear. */
    private static final Map<String, Identifier[]> SPRITES = new HashMap<>();

    static {
        for (String j : JEFES) {
            SPRITES.put(j, new Identifier[]{sprite(j, "full"), sprite(j, "full_blinking"), sprite(j, "half"),
                    sprite(j, "half_blinking"), sprite(j, "container"), sprite(j, "container_blinking")});
        }
    }

    /** Lo que se espera a un jefe que dejo de verse sin morir (ticks): 5 minutos. */
    private static final long OLVIDO = 20 * 60 * 5;
    /**
     * Si el jugador esta a menos de esto (bloques) de donde se le vio y no esta,
     * es que ya no existe (murio sin que se viera, o lo quitaron): los jefes se
     * siguen viendo desde mucho mas lejos (clientTrackingRange 16 chunks).
     */
    private static final double SITIO = 64.0;

    /** El jefe de la batalla en curso (cual y su id de entidad), o null. */
    private static @Nullable String jefe;
    private static int combate = -1;
    private static long vistoAntes;
    /** Donde se le vio por ultima vez. */
    private static Vec3 vistoEn = Vec3.ZERO;
    /** Los ticks seguidos que el jugador lleva en su sitio sin verlo (al volver tarda un poco en llegar). */
    private static int ausente;
    private static @Nullable Level nivel;

    private CorazonesJefe() {
    }

    private static Identifier sprite(String jefe, String que) {
        return Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "hud/heart/" + jefe + "_" + que);
    }

    /** Cada tick: si sigue la batalla, y si no la hay, si empieza una (el jefe despierto mas cercano). */
    public static void tick(Minecraft mc) {
        if (mc.level == null || mc.player == null || mc.level != nivel) {
            acabar();
            nivel = mc.level;
            if (mc.level == null || mc.player == null) {
                return;
            }
        }
        long ahora = mc.level.getGameTime();
        if (jefe != null) {
            Entity e = mc.level.getEntity(combate);
            if (e == null) {
                // No se ve (el jugador se fue lejos): se le espera un rato. Pero si el
                // jugador esta en su sitio y no esta, ya no existe.
                ausente = mc.player.position().closerThan(vistoEn, SITIO) ? ausente + 1 : 0;
                if (ahora - vistoAntes > OLVIDO || ausente > 40) {
                    acabar();
                }
                return;
            }
            if (despierto(e) == null) {
                // Ha muerto (empieza su liberacion): se acabo la batalla.
                acabar();
            } else {
                vistoAntes = ahora;
                vistoEn = e.position();
                ausente = 0;
                return;
            }
        }
        double mejor = CERCA * CERCA;
        for (Entity e : mc.level.entitiesForRendering()) {
            String id = despierto(e);
            if (id != null) {
                double d = e.distanceToSqr(mc.player);
                if (d < mejor) {
                    mejor = d;
                    jefe = id;
                    combate = e.getId();
                    vistoAntes = ahora;
                    vistoEn = e.position();
                }
            }
        }
    }

    private static void acabar() {
        jefe = null;
        combate = -1;
        ausente = 0;
    }

    /** Cual es, si es un jefe despierto y vivo; si no, null. */
    private static @Nullable String despierto(Entity e) {
        if (e.isRemoved() || (e instanceof LivingEntity v && v.isDeadOrDying())) {
            return null;
        }
        if (e instanceof NereaEntity n) {
            return n.getEstado() != NereaEntity.DORMIDO ? "nerea" : null;
        }
        if (e instanceof AeralisEntity a) {
            return a.getEstado() != AeralisEntity.DORMIDA ? "aeralis" : null;
        }
        if (e instanceof RajangEntity r) {
            return r.getEstado() != RajangEntity.DORMIDO ? "rajang" : null;
        }
        if (e instanceof NovilisEntity n) {
            return n.getEstado() != NovilisEntity.DORMIDO ? "novilis" : null;
        }
        return null;
    }

    /**
     * El sprite que va en lugar del de vanilla, o null si se queda el suyo.
     * "tipo" es el nombre del HeartType (NORMAL, CONTAINER...).
     */
    public static @Nullable Identifier sprite(String tipo, boolean mitad, boolean parpadea) {
        if (jefe == null) {
            return null;
        }
        Identifier[] s = SPRITES.get(jefe);
        return switch (tipo) {
            case "NORMAL" -> s[(mitad ? 2 : 0) + (parpadea ? 1 : 0)];
            case "CONTAINER" -> s[4 + (parpadea ? 1 : 0)];
            default -> null;
        };
    }
}
