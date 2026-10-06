package com.atalaya.client;

import com.atalaya.entity.AeralisEntity;
import com.atalaya.entity.NereaEntity;
import com.atalaya.entity.NovilisEntity;
import com.atalaya.entity.RajangEntity;
import com.atalaya.sonido.AtalayaSonidos;
import net.minecraft.client.Minecraft;
import net.minecraft.client.resources.sounds.AbstractTickableSoundInstance;
import net.minecraft.client.resources.sounds.SimpleSoundInstance;
import net.minecraft.client.resources.sounds.SoundInstance;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.Entity;
import org.jspecify.annotations.Nullable;

import java.util.ArrayList;
import java.util.List;

/**
 * La musica de los jefes (musica_jefes.py): cada uno con la suya mientras pelea
 * cerca (Nerea, el mar; Aeralis, la tormenta; Rajang, la tierra; Novilis, el fuego). Suena en la
 * categoria de musica, asi que la regula su barra de volumen; entra y sale
 * fundiendose, y al cambiar de jefe una se funde con la otra. Mientras suena,
 * la musica de vanilla calla (MusicaJefesMixin) y vuelve sola al acabar.
 *
 * Va a la par de sus golpes: cada golpe gordo que sacude el suelo
 * (NereaPresencia.sacudir, el mismo aviso que mueve la camara) suelta un acento
 * de la propia musica (en su tono y con sus instrumentos) y la pista baja un
 * momento para que el golpe se oiga; el cambio de fase y la entrada en Furia
 * tienen los suyos, mas grandes.
 *
 * Se apaga al liberarlo: el final de la pelea es su sonido de liberacion.
 */
public final class MusicaJefes {

    /** Hasta donde se oye la de un jefe (bloques). */
    private static final double CERCA = 96.0;
    private static final int FUNDE_ENTRA = 50;
    private static final int FUNDE_SALE = 70;
    /** Desde que fuerza de temblor un golpe se acentua (las pisadas no llegan). */
    private static final float GOLPE_MINIMO = 2.0F;
    /** Ticks entre acentos de golpe: una lluvia de golpes (meteoritos, burbujas) suena como uno. */
    private static final int ENTRE_GOLPES = 12;

    /** Cada jefe: su pista y sus acentos. */
    private enum Jefe {
        NEREA, AERALIS, RAJANG, NOVILIS;

        SoundEvent pista() {
            return switch (this) {
                case NEREA -> AtalayaSonidos.MUSICA_NEREA;
                case AERALIS -> AtalayaSonidos.MUSICA_AERALIS;
                case RAJANG -> AtalayaSonidos.MUSICA_RAJANG;
                case NOVILIS -> AtalayaSonidos.MUSICA_NOVILIS;
            };
        }

        SoundEvent golpe() {
            return switch (this) {
                case NEREA -> AtalayaSonidos.MUSICA_NEREA_GOLPE;
                case AERALIS -> AtalayaSonidos.MUSICA_AERALIS_GOLPE;
                case RAJANG -> AtalayaSonidos.MUSICA_RAJANG_GOLPE;
                case NOVILIS -> AtalayaSonidos.MUSICA_NOVILIS_GOLPE;
            };
        }

        SoundEvent grande() {
            return switch (this) {
                case NEREA -> AtalayaSonidos.MUSICA_NEREA_GRANDE;
                case AERALIS -> AtalayaSonidos.MUSICA_AERALIS_GRANDE;
                case RAJANG -> AtalayaSonidos.MUSICA_RAJANG_GRANDE;
                case NOVILIS -> AtalayaSonidos.MUSICA_NOVILIS_GRANDE;
            };
        }

        SoundEvent fase() {
            return switch (this) {
                case NEREA -> AtalayaSonidos.MUSICA_NEREA_FASE;
                case AERALIS -> AtalayaSonidos.MUSICA_AERALIS_FASE;
                case RAJANG -> AtalayaSonidos.MUSICA_RAJANG_FASE;
                case NOVILIS -> AtalayaSonidos.MUSICA_NOVILIS_FASE;
            };
        }
    }

    /** Las que suenan: normalmente una; dos mientras se funden al cambiar de jefe. */
    private static final List<Pista> PISTAS = new ArrayList<>();
    private static int reloj;
    private static int ultimoGolpe = -1000;
    /** El jefe que se seguia el tick anterior, su fase y si estaba en Furia. */
    private static int ultimoJefe = -1;
    private static int ultimaFase;
    private static boolean ultimaFuria;

    private MusicaJefes() {
    }

    /** Si suena la de algun jefe: la de vanilla, mientras, calla. */
    public static boolean sonando() {
        return !PISTAS.isEmpty();
    }

    public static void tick(Minecraft mc) {
        reloj++;
        Entity cercano = mc.level == null || mc.player == null ? null : jefeCercano(mc);
        Jefe quiere = cercano == null ? null : jefe(cercano);
        // Las que se han parado (o que el motor ha cortado, al salir del mundo) se olvidan.
        PISTAS.removeIf(p -> p.isStopped() || (p.edad > 20 && !mc.getSoundManager().isActive(p)));
        boolean ya = false;
        for (Pista p : PISTAS) {
            if (p.jefe == quiere && !p.apagando) {
                ya = true;
            } else {
                p.apagando = true;
            }
        }
        if (quiere != null && !ya) {
            Pista nueva = new Pista(quiere);
            mc.getMusicManager().stopPlaying();
            mc.getSoundManager().play(nueva);
            PISTAS.add(nueva);
        }
        // El cambio de fase y la entrada en Furia del jefe que se sigue.
        if (cercano == null) {
            ultimoJefe = -1;
            return;
        }
        int fase = fase(cercano);
        boolean furia = furia(cercano);
        if (cercano.getId() == ultimoJefe) {
            if (fase > ultimaFase) {
                acento(mc, quiere.fase(), 0.4F, 50);
            } else if (furia && !ultimaFuria) {
                acento(mc, quiere.grande(), 0.4F, 50);
            }
        }
        ultimoJefe = cercano.getId();
        ultimaFase = fase;
        ultimaFuria = furia;
    }

    /**
     * Un golpe que sacude el suelo cerca de quien juega (lo avisa
     * NereaPresencia.sacudir, el mismo que mueve la camara): si suena la musica
     * de un jefe y el golpe es gordo, su acento.
     */
    public static void golpe(float fuerza) {
        if (fuerza < GOLPE_MINIMO || reloj - ultimoGolpe < ENTRE_GOLPES) {
            return;
        }
        Pista p = activa();
        if (p == null) {
            return;
        }
        ultimoGolpe = reloj;
        acento(Minecraft.getInstance(), p.jefe.golpe(), 0.55F, 26);
    }

    /** Suena un acento de la musica y la pista baja un momento debajo. */
    private static void acento(Minecraft mc, SoundEvent evento, float baja, int ticks) {
        Pista p = activa();
        if (p == null) {
            return;
        }
        mc.getSoundManager().play(SimpleSoundInstance.forMusic(evento));
        p.agachar(baja, ticks);
    }

    /** La pista que suena y no se esta apagando. */
    private static @Nullable Pista activa() {
        for (Pista p : PISTAS) {
            if (!p.apagando) {
                return p;
            }
        }
        return null;
    }

    /** El jefe despierto mas cercano, o null si no hay ninguno. */
    private static @Nullable Entity jefeCercano(Minecraft mc) {
        Entity mejor = null;
        double d = CERCA * CERCA;
        for (Entity e : mc.level.entitiesForRendering()) {
            if (jefe(e) == null) {
                continue;
            }
            double dd = e.distanceToSqr(mc.player);
            if (dd < d) {
                d = dd;
                mejor = e;
            }
        }
        return mejor;
    }

    /** El jefe que es, si esta despierto y peleando; null si no es un jefe, duerme o ya esta liberado. */
    private static @Nullable Jefe jefe(Entity e) {
        if (e.isRemoved()) {
            return null;
        }
        if (e instanceof NereaEntity n) {
            return n.getEstado() != NereaEntity.DORMIDO && !n.isDeadOrDying() ? Jefe.NEREA : null;
        }
        if (e instanceof AeralisEntity a) {
            return a.getEstado() != AeralisEntity.DORMIDA && !a.isDeadOrDying() ? Jefe.AERALIS : null;
        }
        if (e instanceof RajangEntity r) {
            return r.getEstado() != RajangEntity.DORMIDO && !r.isDeadOrDying() ? Jefe.RAJANG : null;
        }
        if (e instanceof NovilisEntity v) {
            return v.getEstado() != NovilisEntity.DORMIDO && !v.isDeadOrDying() ? Jefe.NOVILIS : null;
        }
        return null;
    }

    private static int fase(Entity e) {
        return e instanceof NereaEntity n ? n.fase() : e instanceof AeralisEntity a ? a.fase()
                : e instanceof RajangEntity r ? r.fase() : e instanceof NovilisEntity v ? v.fase() : 0;
    }

    private static boolean furia(Entity e) {
        return e instanceof NereaEntity n ? n.tieneFuria() : e instanceof AeralisEntity a ? a.tieneFuria()
                : e instanceof RajangEntity r ? r.tieneFuria() : e instanceof NovilisEntity v && v.tieneFuria();
    }

    /** Una pista en bucle, sin posicion (suena igual en los dos oidos), que se funde al entrar y al salir. */
    private static final class Pista extends AbstractTickableSoundInstance {

        final Jefe jefe;
        boolean apagando;
        int edad;
        private float fundido;
        /** Lo que baja con un acento (1 = nada) y los ticks que aguanta abajo. */
        private float agacha = 1.0F;
        private int aguanta;

        Pista(Jefe jefe) {
            super(jefe.pista(), SoundSource.MUSIC, SoundInstance.createUnseededRandom());
            this.jefe = jefe;
            this.looping = true;
            this.delay = 0;
            this.volume = 0.001F;
            this.pitch = 1.0F;
            this.relative = true;
            this.attenuation = Attenuation.NONE;
        }

        void agachar(float hasta, int ticks) {
            agacha = Math.min(agacha, hasta);
            aguanta = Math.max(aguanta, ticks / 3);
        }

        @Override
        public boolean canStartSilent() {
            return true;
        }

        @Override
        public void tick() {
            edad++;
            fundido = apagando ? fundido - 1.0F / FUNDE_SALE : Math.min(1.0F, fundido + 1.0F / FUNDE_ENTRA);
            if (fundido <= 0.0F) {
                stop();
                return;
            }
            // Tras el acento aguanta abajo un momento y vuelve poco a poco.
            if (aguanta > 0) {
                aguanta--;
            } else {
                agacha += (1.0F - agacha) * 0.08F;
            }
            // Curva de volumen: el oido lo nota mas lineal asi.
            volume = Math.max(0.001F, fundido * fundido * agacha);
        }
    }
}
