package com.atalaya.entity;

import java.util.List;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.phys.Vec3;
import org.jspecify.annotations.Nullable;

/**
 * Un minijuego de Aeralis en marcha (los cuatro de MinijuegosAeralis). Lo crea
 * AeralisEntity al acabar su chillido, lo mueve cada tick antes de su estado y
 * lo recoge al acabar (bien, mal, o cortado por un cambio de fase o su muerte).
 * Mientras dura no ataca: por donde vuela (o donde se posa) lo dice cada uno.
 */
abstract class MinijuegoAeralis {

    final AeralisEntity a;
    final int tipo;
    /** Lo que dura (ticks) y lo que lleva. */
    final int dura;
    int t;
    /** Lo que lleva hecho y lo que hace falta (la barra del jefe). */
    int cuenta;
    int necesario;

    MinijuegoAeralis(AeralisEntity a, int tipo, int dura) {
        this.a = a;
        this.tipo = tipo;
        this.dura = dura;
    }

    /** Al acabar el chillido: saca lo suyo. Falso si no puede (nadie a quien jugar). */
    abstract boolean empezar(ServerLevel nivel, List<Player> js);

    /** Cada tick, antes del estado de Aeralis. */
    abstract void tick(ServerLevel nivel);

    /** Recoge lo suyo: ha salido bien, mal (avisar) o se ha cortado (sin avisar). */
    abstract void limpiar(ServerLevel nivel, boolean exito, boolean avisar);

    /** Para las pruebas: que salga bien ya. */
    abstract void forzarExito(ServerLevel nivel);

    /** Si al acabarse el tiempo ha salido bien. */
    boolean exitoAlAcabar() {
        return false;
    }

    /**
     * A donde vuela mientras dura: x, z, la altura sobre el suelo y lo deprisa
     * que va (bloques por tick); null para que vuele como siempre.
     */
    @Nullable double[] destino(ServerLevel nivel) {
        return null;
    }

    /** No le entra nada mientras dura (salvo lo que el minijuego decida, con golpeMini). */
    boolean inmune() {
        return true;
    }

    /** Alguien le pega (antes del dano): devuelve si el golpe cuenta para el minijuego (y no hace mas). */
    boolean alGolpearla(ServerLevel nivel, @Nullable Entity causante, @Nullable Entity directo) {
        return false;
    }

    /** El dato del minijuego para el cliente (DATA_MINI_INFO). */
    int info() {
        return 0;
    }

    /** Hacia donde mira mientras dura (null: a su objetivo). */
    @Nullable Vec3 mira(ServerLevel nivel, @Nullable LivingEntity objetivo) {
        return null;
    }
}
