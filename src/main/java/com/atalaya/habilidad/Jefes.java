package com.atalaya.habilidad;

import com.atalaya.entity.AeralisEntity;
import com.atalaya.entity.NereaEntity;
import com.atalaya.entity.NovilisEntity;
import com.atalaya.entity.RajangEntity;
import com.atalaya.entity.VigiaEntity;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.boss.enderdragon.EnderDragon;
import net.minecraft.world.entity.boss.wither.WitherBoss;
import net.minecraft.world.entity.monster.ElderGuardian;
import net.minecraft.world.entity.monster.warden.Warden;

/**
 * Quien es jefe y quien minijefe, para lo que solo vale contra monstruos
 * normales (el fuego de la espada solar, el aturdimiento del martillo, la
 * rafaga del soporte) y para la provocacion del tanque (solo los jefes
 * elementales).
 */
public final class Jefes {

    private Jefes() {
    }

    /** Los cuatro jefes elementales: los que el tanque puede provocar. */
    public static boolean esElemental(Entity e) {
        return e instanceof NereaEntity || e instanceof AeralisEntity || e instanceof RajangEntity || e instanceof NovilisEntity;
    }

    /** Jefes y minijefes: con estos no va nada de lo que es para monstruos normales. */
    public static boolean esJefeOMinijefe(Entity e) {
        return esElemental(e) || e instanceof VigiaEntity || e instanceof WitherBoss || e instanceof EnderDragon
                || e instanceof ElderGuardian || e instanceof Warden;
    }
}
