package com.atalaya.client;

import com.atalaya.entity.AeralisEntity;
import com.atalaya.entity.NereaEntity;
import com.atalaya.entity.RajangEntity;
import com.atalaya.sonido.AtalayaSonidos;
import net.minecraft.client.Minecraft;
import net.minecraft.client.resources.sounds.AbstractTickableSoundInstance;
import net.minecraft.client.resources.sounds.SoundInstance;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.Entity;
import org.jspecify.annotations.Nullable;

import java.util.ArrayList;
import java.util.List;

/**
 * La musica de los jefes (musica_jefes.py): cada uno con la suya mientras pelea
 * cerca (Nerea, el mar; Aeralis, la tormenta; Rajang, la tierra). Suena en la
 * categoria de musica, asi que la regula su barra de volumen; entra y sale
 * fundiendose, y al cambiar de jefe una se funde con la otra. Mientras suena,
 * la musica de vanilla calla (MusicaJefesMixin) y vuelve sola al acabar.
 *
 * Se apaga al liberarlo: el final de la pelea es su sonido de liberacion.
 */
public final class MusicaJefes {

    /** Hasta donde se oye la de un jefe (bloques). */
    private static final double CERCA = 96.0;
    private static final int FUNDE_ENTRA = 50;
    private static final int FUNDE_SALE = 70;

    /** Las que suenan: normalmente una; dos mientras se funden al cambiar de jefe. */
    private static final List<Pista> PISTAS = new ArrayList<>();

    private MusicaJefes() {
    }

    /** Si suena la de algun jefe: la de vanilla, mientras, calla. */
    public static boolean sonando() {
        return !PISTAS.isEmpty();
    }

    public static void tick(Minecraft mc) {
        SoundEvent quiere = mc.level == null || mc.player == null ? null : pistaCercana(mc);
        // Las que se han parado (o que el motor ha cortado, al salir del mundo) se olvidan.
        PISTAS.removeIf(p -> p.isStopped() || (p.edad > 20 && !mc.getSoundManager().isActive(p)));
        boolean ya = false;
        for (Pista p : PISTAS) {
            if (p.evento == quiere && !p.apagando) {
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
    }

    /** La pista del jefe despierto mas cercano, o null si no hay ninguno. */
    private static @Nullable SoundEvent pistaCercana(Minecraft mc) {
        SoundEvent mejor = null;
        double d = CERCA * CERCA;
        for (Entity e : mc.level.entitiesForRendering()) {
            SoundEvent s = pista(e);
            if (s == null) {
                continue;
            }
            double dd = e.distanceToSqr(mc.player);
            if (dd < d) {
                d = dd;
                mejor = s;
            }
        }
        return mejor;
    }

    /** La de un jefe despierto y peleando; null si no es un jefe, duerme o ya esta liberado. */
    private static @Nullable SoundEvent pista(Entity e) {
        if (e.isRemoved()) {
            return null;
        }
        if (e instanceof NereaEntity n) {
            return n.getEstado() != NereaEntity.DORMIDO && !n.isDeadOrDying() ? AtalayaSonidos.MUSICA_NEREA : null;
        }
        if (e instanceof AeralisEntity a) {
            return a.getEstado() != AeralisEntity.DORMIDA && !a.isDeadOrDying() ? AtalayaSonidos.MUSICA_AERALIS : null;
        }
        if (e instanceof RajangEntity r) {
            return r.getEstado() != RajangEntity.DORMIDO && !r.isDeadOrDying() ? AtalayaSonidos.MUSICA_RAJANG : null;
        }
        return null;
    }

    /** Una pista en bucle, sin posicion (suena igual en los dos oidos), que se funde al entrar y al salir. */
    private static final class Pista extends AbstractTickableSoundInstance {

        final SoundEvent evento;
        boolean apagando;
        int edad;
        private float fundido;

        Pista(SoundEvent evento) {
            super(evento, SoundSource.MUSIC, SoundInstance.createUnseededRandom());
            this.evento = evento;
            this.looping = true;
            this.delay = 0;
            this.volume = 0.001F;
            this.pitch = 1.0F;
            this.relative = true;
            this.attenuation = Attenuation.NONE;
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
            // Curva de volumen: el oido lo nota mas lineal asi.
            volume = Math.max(0.001F, fundido * fundido);
        }
    }
}
