package com.atalaya.entity;

import java.util.List;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.phys.Vec3;
import org.jspecify.annotations.Nullable;

/**
 * Un minijuego de Rajang en marcha (los cuatro de MinijuegosRajang). Lo crea
 * RajangEntity al rugir, lo mueve cada tick antes de su estado y lo recoge al
 * acabar (bien, mal, o cortado por un cambio de fase o su muerte). Lo que hace
 * Rajang mientras dura lo decide cada uno.
 */
abstract class MinijuegoRajang {

    final RajangEntity r;
    final int tipo;
    /** Lo que dura (ticks) y lo que lleva. */
    final int dura;
    int t;
    /** Lo que lleva hecho y lo que hace falta (la barra del jefe). */
    int cuenta;
    int necesario;

    MinijuegoRajang(RajangEntity r, int tipo, int dura) {
        this.r = r;
        this.tipo = tipo;
        this.dura = dura;
    }

    /** Al rugir: saca lo suyo. Falso si no puede (nadie a quien jugar). */
    abstract boolean empezar(ServerLevel nivel, List<Player> js);

    /** Cada tick, antes del estado de Rajang. */
    abstract void tick(ServerLevel nivel);

    /** Recoge lo suyo: ha salido bien, mal (avisar) o se ha cortado (sin avisar). */
    abstract void limpiar(ServerLevel nivel, boolean exito, boolean avisar);

    /** Para las pruebas: que salga bien ya. */
    abstract void forzarExito(ServerLevel nivel);

    /** Si al acabarse el tiempo ha salido bien (Suelo que se Hunde: si nadie ha caido). */
    boolean exitoAlAcabar() {
        return false;
    }

    /** Si manda en Rajang cuando esta libre (entonces no ataca: lo que haga lo dice libre()). */
    boolean controlaLibre() {
        return true;
    }

    /** Rajang libre mientras dura (si controlaLibre). */
    void libre(ServerLevel nivel) {
        r.quietoMini();
    }

    /** No le entra nada mientras dura. */
    boolean inmune() {
        return false;
    }

    /** Hacia donde salta, si es a un sitio que se mueve (la luz del prisma). */
    @Nullable Vec3 destinoSalto() {
        return null;
    }

    /** Ha caido de un salto: sus zarpas, aqui; iba a por 'destino' (la luz). */
    void alAterrizar(ServerLevel nivel, Vec3 donde, @Nullable Vec3 destino) {
    }
}
