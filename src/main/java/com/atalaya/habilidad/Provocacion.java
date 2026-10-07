package com.atalaya.habilidad;

import com.atalaya.item.ArmadurasJefes;
import com.atalaya.particula.AtalayaParticulas;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.phys.Vec3;
import org.jspecify.annotations.Nullable;

import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

/**
 * La provocacion de la Muralla de Jade: mientras dura, los ataques de un solo
 * objetivo del jefe van a por el tanque si lo tiene a su alcance. Las
 * mecanicas cooperativas y letales (la Mirada, el Juicio, la Ofrenda, el
 * Cataclismo...) eligen a quien quieren, como siempre.
 *
 * Un jefe solo atiende a un tanque a la vez, y cuando la provocacion se acaba
 * (o el tanque cae o se quita la armadura) no se le puede volver a atraer
 * hasta 15 s despues: por muchos tanques que haya, no lo tienen clavado todo
 * el combate.
 */
public final class Provocacion {

    /** Lo que descansa el jefe antes de poder ser provocado otra vez: 15 s. */
    public static final int DESCANSO = 300;
    /** Hasta donde llega la provocacion. */
    public static final double ALCANCE = 48.0;

    private record Estado(@Nullable UUID tanque, long hasta, long libreDesde) {
    }

    private static final Map<UUID, Estado> JEFES = new HashMap<>();

    private Provocacion() {
    }

    /** El tanque con la Muralla puesta reclama a los jefes que tenga cerca (se llama cada medio segundo). */
    public static void reclamar(ServerPlayer tanque, long hasta) {
        ServerLevel nivel = tanque.level();
        long ahora = nivel.getGameTime();
        for (Mob jefe : nivel.getEntitiesOfClass(Mob.class, tanque.getBoundingBox().inflate(ALCANCE), Jefes::esElemental)) {
            if (!jefe.isAlive() || tanque.distanceToSqr(jefe) > ALCANCE * ALCANCE) {
                continue;
            }
            Estado e = JEFES.get(jefe.getUUID());
            if (e != null && (ahora < e.libreDesde() || (e.tanque() != null && ahora < e.hasta()))) {
                continue;
            }
            JEFES.put(jefe.getUUID(), new Estado(tanque.getUUID(), hasta, hasta + DESCANSO));
            com.atalaya.Atalaya.LOGGER.info("Muralla de Jade: {} provoca a {}", tanque.getName().getString(),
                    jefe.getName().getString());
            // Un hilo de jade del tanque al jefe: se ve a quien ha atraido.
            Vec3 a = tanque.position().add(0, 1.2, 0);
            Vec3 b = jefe.position().add(0, jefe.getBbHeight() * 0.6, 0);
            for (int i = 0; i <= 16; i++) {
                Vec3 p = a.lerp(b, i / 16.0);
                nivel.sendParticles(AtalayaParticulas.RAJANG_JADE, p.x, p.y, p.z, 1, 0.05, 0.05, 0.05, 0.0);
            }
        }
    }

    /** El tanque que tiene provocado a este jefe ahora mismo (o nada). */
    public static @Nullable ServerPlayer tanque(Mob jefe) {
        Estado e = JEFES.get(jefe.getUUID());
        if (e == null || e.tanque() == null || !(jefe.level() instanceof ServerLevel nivel)) {
            return null;
        }
        long ahora = nivel.getGameTime();
        ServerPlayer t = nivel.getServer().getPlayerList().getPlayer(e.tanque());
        boolean vale = ahora < e.hasta() && t != null && t.isAlive() && !t.isSpectator() && t.level() == nivel
                && Habilidades.conjunto(t) == ArmadurasJefes.Tema.JADE;
        if (!vale) {
            // Se acabo (o el tanque cayo): el jefe descansa 15 s desde ahora.
            JEFES.put(jefe.getUUID(), new Estado(null, 0L, Math.min(e.libreDesde(), ahora + DESCANSO)));
            return null;
        }
        return t;
    }

    /**
     * El objetivo de un ataque de un solo objetivo: el tanque que lo provoca si
     * esta a su alcance, y si no el que el jefe habia elegido.
     */
    public static @Nullable LivingEntity objetivo(Mob jefe, @Nullable LivingEntity elegido, double alcance) {
        ServerPlayer t = tanque(jefe);
        if (t != null && t.distanceToSqr(jefe) <= alcance * alcance) {
            return t;
        }
        return elegido;
    }

    /** Cada tick, desde el jefe: mientras le provoca, el tanque es su objetivo. */
    public static void aplicar(Mob jefe) {
        ServerPlayer t = tanque(jefe);
        if (t != null && jefe.getTarget() != t && t.distanceToSqr(jefe) <= ALCANCE * ALCANCE) {
            jefe.setTarget(t);
        }
    }

    /** Al cerrar el servidor o cambiar de mundo no queda nada colgando. */
    public static void limpiar() {
        JEFES.clear();
    }
}
