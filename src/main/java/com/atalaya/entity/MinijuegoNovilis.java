package com.atalaya.entity;

import java.util.List;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import org.jspecify.annotations.Nullable;

/**
 * Un minijuego de Novilis en marcha (los cuatro de MinijuegosNovilis). Lo crea
 * NovilisEntity al clavar la espada (o al alzar el puno), lo mueve cada tick
 * antes de su estado y lo recoge al acabar (bien, mal, o cortado por un cambio
 * de fase o su muerte). Lo que hace Novilis mientras dura lo decide cada uno.
 */
abstract class MinijuegoNovilis {

    final NovilisEntity n;
    final int tipo;
    /** Lo que dura (ticks) y lo que lleva. */
    final int dura;
    int t;
    /** Lo que lleva hecho y lo que hace falta (la barra del jefe). */
    int cuenta;
    int necesario;

    MinijuegoNovilis(NovilisEntity n, int tipo, int dura) {
        this.n = n;
        this.tipo = tipo;
        this.dura = dura;
    }

    /** Al clavar la espada: saca lo suyo. Falso si no puede (nadie a quien jugar). */
    abstract boolean empezar(ServerLevel nivel, List<Player> js);

    /** Cada tick, antes del estado de Novilis. */
    abstract void tick(ServerLevel nivel);

    /** Recoge lo suyo: ha salido bien, mal (avisar) o se ha cortado (sin avisar). */
    abstract void limpiar(ServerLevel nivel, boolean exito, boolean avisar);

    /** Para las pruebas: que salga bien ya. */
    abstract void forzarExito(ServerLevel nivel);

    /** Si al acabarse el tiempo ha salido bien. */
    boolean exitoAlAcabar() {
        return false;
    }

    /** Si manda en Novilis cuando esta libre (entonces no ataca: lo que haga lo dice libre()). */
    boolean controlaLibre() {
        return true;
    }

    /** Novilis libre mientras dura (si controlaLibre): por defecto, plantado mirando a los suyos. */
    void libre(ServerLevel nivel, @Nullable LivingEntity objetivo) {
        n.quietoMini(objetivo);
    }

    /** No le entra nada mientras dura. */
    boolean inmune() {
        return true;
    }

    /** El dato del minijuego para el cliente (DATA_MINI_INFO). */
    int info() {
        return 0;
    }
}
