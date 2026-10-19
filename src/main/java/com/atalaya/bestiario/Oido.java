package com.atalaya.bestiario;

import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.phys.Vec3;

/**
 * El oido de los mobs ciegos del bestiario (el Creeper Ciego, la Bomba del Abismo): hasta donde se oye a un jugador.
 * Correr se oye de lejos, andar menos, saltar y pegar tambien suenan; agachado no se oye nada (salvo que te rocen: eso
 * lo mira cada uno).
 */
public final class Oido {

    private Oido() {
    }

    /** Hasta donde se oye a ese jugador (0: no se le oye). */
    public static double alcance(ServerPlayer p) {
        if (p.isShiftKeyDown()) {
            return 0.0;
        }
        Vec3 m = p.getKnownMovement();
        double h = m.x * m.x + m.z * m.z;
        double alcance = 0.0;
        if (p.isSprinting() && h > 0.01) {
            alcance = 22.0;
        } else if (h > 0.002) {
            alcance = 12.0;
        }
        if (!p.onGround() && m.y > 0.05) {
            alcance = Math.max(alcance, 14.0);
        }
        if (p.swinging) {
            alcance = Math.max(alcance, 16.0);
        }
        return alcance;
    }
}
