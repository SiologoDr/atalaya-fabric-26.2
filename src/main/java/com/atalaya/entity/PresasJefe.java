package com.atalaya.entity;

import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.ClipContext;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;
import org.jspecify.annotations.Nullable;

/**
 * A quien persiguen los jefes y cuando despiertan.
 *
 * <p>El objetivo de vanilla (NearestAttackableTargetGoal) solo se elige si el
 * jefe LO VE: un rayo de su ojo al tuyo que no choque con nada. Con jefes de 8 a
 * 24 bloques el ojo se queda entre las hojas, tras una loma o por encima de un
 * techo, el rayo no pasa, y el jefe despierto se quedaba quieto sin objetivo (o
 * ni siquiera despertaba) aunque hubiera alguien en supervivencia al lado. Aqui
 * se elige al jugador mas cercano sin pedir que lo vea, y para despertar vale
 * verlo desde los ojos, el pecho o las rodillas, o tenerlo muy cerca.
 */
public final class PresasJefe {

    /**
     * Lo que sigue la presentacion de un jefe tras acabar de despertar (ticks):
     * unos 5 s mas con su cartel, para que se lea. Mientras esta en escena no se
     * mueve, no ataca y no se le hace dano (Juan, 07-10-2026: "en ese tiempo el
     * jefe no podra golpear porque estara en escena").
     */
    public static final int ESCENA = 100;

    /** Lo que sigue quieto e inmune tras despertar: la escena y la vuelta de la camara (ticks). */
    public static final int ESCENA_QUIETO = ESCENA + 26;

    /**
     * Lo minimo que espera un jefe tras despertar antes de su primer ataque
     * (ticks): la escena, la vuelta de la camara a los ojos de los jugadores y
     * un poco mas para que se ubiquen.
     */
    public static final int RESPIRO_PRESENTACION = ESCENA_QUIETO + 30;


    /**
     * Lo que dura la Furia de los cuatro jefes: 30 s, y mientras dura es inmune
     * (solo toca esquivar). Antes duraba hasta que lo derribaran y en Rajang
     * podian ser minutos (testers, 07-10-2026). Si lo derriban antes, se acaba antes.
     */
    public static final int FURIA_TICKS = 600;

    /** Avisa en la barra de accion a los que pelean de que empieza o se acaba la Furia. */
    public static void avisarFuria(ServerLevel nivel, LivingEntity jefe, boolean empieza) {
        net.minecraft.network.chat.Component texto = net.minecraft.network.chat.Component
                .translatable(empieza ? "hud.atalaya.jefe.furia" : "hud.atalaya.jefe.furia_fin")
                .withStyle(empieza ? net.minecraft.ChatFormatting.GOLD : net.minecraft.ChatFormatting.YELLOW);
        for (Player p : nivel.getEntitiesOfClass(Player.class, jefe.getBoundingBox().inflate(64))) {
            if (!p.isCreative() && !p.isSpectator() && p.isAlive()) {
                p.sendOverlayMessage(texto);
            }
        }
    }

    /** Cada cuanto se revisa el objetivo (ticks). */
    public static final int CADA = 10;
    /** Tan cerca, despierta aunque no lo vea (detras de un arbol, debajo de un techo). */
    public static final double DESPIERTA_SIN_VER = 16.0;

    private PresasJefe() {
    }

    /** Si vale como objetivo: vivo, y si es un jugador, ni en creativo ni en espectador. */
    public static boolean vale(LivingEntity v) {
        return presa(v);
    }

    /**
     * Lo que un jefe ataca y persigue: solo jugadores (en supervivencia o
     * aventura) y los maniquies, que hacen de jugador en las escenas de prueba.
     * Nunca a otro jefe ni a otros bichos (Juan, 07-10-2026).
     */
    public static boolean presa(LivingEntity v) {
        if (!v.isAlive() || v.isRemoved()) {
            return false;
        }
        if (v instanceof Player p) {
            return !p.isCreative() && !p.isSpectator();
        }
        return v instanceof net.minecraft.world.entity.decoration.Mannequin;
    }

    /** Es uno de los cuatro jefes: lo suyo no le hace nada a otro jefe. */
    public static boolean esJefe(@Nullable Entity e) {
        return e instanceof NereaEntity || e instanceof AeralisEntity || e instanceof RajangEntity || e instanceof NovilisEntity;
    }

    /**
     * El jugador (supervivencia o aventura) mas cercano al jefe a menos de
     * "radio" bloques, que ademas este a menos de "correa" del centro de su
     * templo. Sin pedir que lo vea.
     */
    public static @Nullable Player masCercano(ServerLevel nivel, Mob jefe, double radio, Vec3 centro, double correa) {
        Player mejor = null;
        double d = radio * radio;
        for (Player p : nivel.players()) {
            if (!vale(p)) {
                continue;
            }
            double dd = p.distanceToSqr(jefe);
            if (dd < d && p.distanceToSqr(centro) < correa * correa) {
                d = dd;
                mejor = p;
            }
        }
        return mejor;
    }

    /**
     * Revisa el objetivo del jefe: suelta el que ya no vale y, si no tiene
     * ninguno (o persigue a un bicho y hay un jugador a tiro), elige al jugador
     * mas cercano. Devuelve el objetivo con el que se queda.
     */
    public static @Nullable LivingEntity revisar(ServerLevel nivel, Mob jefe, @Nullable LivingEntity objetivo, Vec3 centro,
                                                 double correa) {
        if (objetivo != null && !vale(objetivo)) {
            jefe.setTarget(null);
            objetivo = null;
        }
        if ((objetivo == null || !(objetivo instanceof Player)) && jefe.tickCount % CADA == 0) {
            Player p = masCercano(nivel, jefe, correa, centro, correa);
            if (p != null) {
                jefe.setTarget(p);
                objetivo = p;
            }
        }
        return objetivo;
    }

    /**
     * Si el jefe ve a alguien: desde los ojos, el pecho o las rodillas (con un
     * arbol o un techo sobre la cabeza tambien lo ve), o lo tiene tan cerca que
     * da igual.
     */
    public static boolean despierta(ServerLevel nivel, Mob jefe, Entity p) {
        if (p.distanceToSqr(jefe) < DESPIERTA_SIN_VER * DESPIERTA_SIN_VER) {
            return true;
        }
        Vec3 hasta = p.getEyePosition();
        for (double k : new double[]{1.0, 0.55, 0.15}) {
            Vec3 desde = new Vec3(jefe.getX(), jefe.getY() + Math.max(0.5, jefe.getEyeHeight() * k), jefe.getZ());
            if (nivel.clip(new ClipContext(desde, hasta, ClipContext.Block.COLLIDER, ClipContext.Fluid.NONE, jefe)).getType()
                    == HitResult.Type.MISS) {
                return true;
            }
        }
        return false;
    }
}
