package com.atalaya.cambios;

import com.atalaya.effect.DeslumbradoEffect;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.util.Mth;
import net.minecraft.world.attribute.EnvironmentAttributes;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;

/**
 * Mirar al cielo (DEDsafio 4): lo que pasa si miras al Sol o a la Luna.
 *
 * <pre>
 *   NO MIRES AL SOL   quien lo mira se queda tres minutos deslumbrado: la vista nublada, sin colores y sin ver su vida
 *                     (DeslumbradoEffect; lo que se ve lo hace el cliente)
 * </pre>
 *
 * Donde esta el Sol: el angulo del cielo de 26.2 (EnvironmentAttributes.SUN_ANGLE, en grados), con el mismo giro que el
 * render del cielo (90 grados sobre Y y luego el angulo sobre X): (-sen a, cos a, 0), que al mediodia es la vertical.
 */
public final class MirarAlCielo {

    /** Cuanto tiene que acertar la mirada (coseno: unos 6 grados del centro del disco). */
    private static final double CERCA = Math.cos(Math.toRadians(6.0));

    private MirarAlCielo() {
    }

    /** Hacia donde esta el Sol (o la Luna) desde cualquier sitio. */
    public static Vec3 direccion(ServerLevel nivel, boolean sol, Vec3 desde) {
        float grados = nivel.environmentAttributes().getValue(sol ? EnvironmentAttributes.SUN_ANGLE : EnvironmentAttributes.MOON_ANGLE, desde);
        double a = grados * Mth.DEG_TO_RAD;
        return new Vec3(-Math.sin(a), Math.cos(a), 0.0);
    }

    /** Si ese jugador esta mirando al Sol (o a la Luna) a cielo abierto. */
    public static boolean mira(ServerPlayer p, boolean sol) {
        ServerLevel nivel = p.level();
        if (nivel.dimension() != Level.OVERWORLD || nivel.isRaining()) {
            return false;
        }
        if (sol ? !nivel.isBrightOutside() : nivel.isBrightOutside()) {
            return false;
        }
        Vec3 ojos = p.getEyePosition();
        Vec3 astro = direccion(nivel, sol, ojos);
        if (astro.y < 0.05) {
            return false;
        }
        if (p.getViewVector(1.0F).dot(astro) < CERCA) {
            return false;
        }
        return nivel.canSeeSky(BlockPos.containing(ojos));
    }

    /** NO MIRES AL SOL: tres minutos deslumbrado. */
    static void sol(ServerPlayer p) {
        if (!p.hasEffect(DeslumbradoEffect.DESLUMBRADO) && mira(p, true)) {
            p.addEffect(new MobEffectInstance(DeslumbradoEffect.DESLUMBRADO, 3 * 60 * 20, 0, false, false, true));
        }
    }
}
