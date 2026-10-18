package com.atalaya.client;

import com.atalaya.net.AtalayaRed;
import com.atalaya.sonido.AtalayaSonidos;
import net.minecraft.client.Minecraft;
import net.minecraft.client.resources.sounds.SimpleSoundInstance;
import net.minecraft.client.resources.sounds.SoundInstance;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.Mth;
import org.jspecify.annotations.Nullable;

import java.util.ArrayList;
import java.util.List;
import java.util.Random;

/**
 * La Ruleta en el cliente (la tira y la quita el servidor: com.atalaya.momento.Ruleta). Lleva el calendario de la
 * tirada, que va a la par de sus sonidos (ruleta_sonidos.py), la curva del rodillo y su tira de iconos; lo que se ve lo
 * pinta RuletaHud.
 *
 * Segunda version (17-10-2026). Juan: "para que los usuarios no sepan que accion es, con el inicio de la animacion
 * deberia aparecer ya girando, y debe de ser mas inmersivo y dar esa tension"; "mas rapido el giro y que dure mas
 * tiempo, el doble o un poco mas". Asi que sale ya girando a tope (nunca se ve un icono quieto al principio), gira mas
 * deprisa y el doble de tiempo, y la tira de iconos es al azar en cada tirada (la misma para todos: la semilla la manda
 * el servidor), asi que el icono en el que casi se para tampoco dice nada.
 *
 * <pre>
 *   0      el medallon entra girando sobre si mismo, ya con el rodillo a tope
 *   0-60   a tope: un borron de colores; la luz corre por el aro
 *   60-128 frena; los iconos empiezan a leerse y cada uno suena al pasar
 *   126    el corazon: latidos cada vez mas seguidos, el medallon se acerca y todo se oscurece
 *   146    casi parado en un icono (el señuelo)... y en 156 se mueve otra vez
 *   170    el cerrojo: para en su final; el icono salta, todo se pone de su color, la camara da un golpe
 *   200    el medallon se va y el icono vuela al chat
 *   206    el aviso del chat (lo manda el servidor a la vez) y la campanilla
 * </pre>
 */
public final class RuletaCliente {

    public static final int T_ENTRA = 8;
    public static final int T_FRENA = 60;
    public static final int T_LENTO = 128;
    public static final int T_PARA = 170;
    public static final int T_SALE = 200;
    public static final int T_AVISO = 206;
    public static final int T_FIN = 214;
    /** Los iconos que pasan desde que sale hasta que para (el ultimo es el del final). */
    public static final int VUELTAS = 164;
    /** Los latidos del suspense (ticks): cada vez mas seguidos hasta el cerrojo. */
    public static final int[] LATIDOS = {126, 137, 146, 153, 159, 164, 168};
    /**
     * La curva del rodillo: tick, posicion (iconos) y velocidad (iconos por tick); entre dos puntos, una cubica de
     * Hermite. Sale ya a tope (1,8 iconos por tick), frena, pasa despacio un par de iconos, se queda casi parado en el
     * señuelo (el 163) y pasa al bueno (el 164). La misma que ruleta_sonidos.py, que saca de ella los clics y las notas.
     */
    private static final float[][] RODILLO = {
            {0, 0.0F, 1.8F}, {60, 108.0F, 1.8F}, {128, 161.5F, 0.12F}, {146, 162.82F, 0.03F}, {156, 163.02F, 0.005F},
            {170, 164.0F, 0.0F}};

    /** Para las fotos de prueba (FotosPrueba, RULETA_FILM): el tiempo fijo de la tirada (-1, el de verdad). */
    public static float pruebaT = -1;
    private static boolean activa;
    private static int fin;
    private static int t;
    /** Los iconos de la tira, uno por casilla (0 a VUELTAS + 4): al azar, sin dos iguales seguidos. */
    private static int[] tira = new int[VUELTAS + 5];
    private static final List<SoundInstance> sonando = new ArrayList<>();

    private RuletaCliente() {
    }

    public static void recibir(AtalayaRed.Ruleta r) {
        Minecraft mc = Minecraft.getInstance();
        callar(mc);
        if (r.accion() == AtalayaRed.Ruleta.PARA) {
            activa = false;
            return;
        }
        fin = Mth.clamp(r.fin(), 0, 3);
        tira = tira(r.semilla(), fin);
        t = 0;
        activa = true;
        sonar(mc, AtalayaSonidos.RULETA_ANIMACION, 1.0F);
    }

    /**
     * La tira: al azar con la semilla, sin dos iconos iguales seguidos; en VUELTAS, el final, y justo antes, el señuelo
     * (otro cualquiera).
     */
    private static int[] tira(int semilla, int fin) {
        Random azar = new Random(semilla);
        int[] out = new int[VUELTAS + 5];
        for (int i = 0; i < out.length; i++) {
            int antes = i > 0 ? out[i - 1] : -1;
            int icono;
            if (i == VUELTAS) {
                icono = fin;
            } else {
                do {
                    icono = azar.nextInt(4);
                } while (icono == antes || (i == VUELTAS - 1 && icono == fin) || (i == VUELTAS + 1 && icono == fin));
            }
            out[i] = icono;
        }
        return out;
    }

    public static void olvidar() {
        activa = false;
        sonando.clear();
    }

    public static void tick(Minecraft mc) {
        if (!activa) {
            return;
        }
        if (mc.level == null) {
            olvidar();
            return;
        }
        if (mc.isPaused() || pruebaT >= 0) {
            return;
        }
        t++;
        if (t == T_PARA) {
            sonar(mc, switch (fin) {
                case 0 -> AtalayaSonidos.RULETA_MOB;
                case 1 -> AtalayaSonidos.RULETA_DIFICULTAD;
                case 2 -> AtalayaSonidos.RULETA_PENALIZACION;
                default -> AtalayaSonidos.RULETA_MINIJUEGO;
            }, 1.0F);
        } else if (t == T_SALE) {
            sonar(mc, AtalayaSonidos.RULETA_SALE, 0.9F);
        } else if (t == T_AVISO) {
            sonar(mc, AtalayaSonidos.RULETA_AVISO, 0.9F);
        }
        if (t >= T_FIN) {
            activa = false;
            sonando.clear();
        }
    }

    public static boolean activa() {
        return activa;
    }

    /** El final en el que para (0 mob, 1 dificultad, 2 penalizacion, 3 minijuego). */
    public static int fin() {
        return fin;
    }

    /** El icono de la casilla i de la tira. */
    public static int icono(int i) {
        return tira[Mth.clamp(i, 0, tira.length - 1)];
    }

    /** Ticks desde que salio, con la parte del tick que va. */
    public static float tiempo(float parcial) {
        if (pruebaT >= 0) {
            return pruebaT;
        }
        return activa ? t + (Minecraft.getInstance().isPaused() ? 0.0F : parcial) : 0.0F;
    }

    /**
     * Donde va el rodillo (iconos desde que sale) en el tick tt: la curva y, al parar, el golpe del cerrojo (se pasa un
     * poco y vuelve).
     */
    public static float posicion(float tt) {
        if (tt <= RODILLO[0][0]) {
            return RODILLO[0][2] * tt;
        }
        for (int i = 0; i + 1 < RODILLO.length; i++) {
            float[] a = RODILLO[i];
            float[] b = RODILLO[i + 1];
            if (tt <= b[0]) {
                float h = b[0] - a[0];
                float s = (tt - a[0]) / h;
                float s2 = s * s;
                float s3 = s2 * s;
                return (2 * s3 - 3 * s2 + 1) * a[1] + (s3 - 2 * s2 + s) * h * a[2] + (-2 * s3 + 3 * s2) * b[1]
                        + (s3 - s2) * h * b[2];
            }
        }
        float d = tt - T_PARA;
        return VUELTAS + (d < 14 ? 0.09F * Mth.sin(d * Mth.PI / 2.4F) * (float) Math.exp(-d / 2.2F) : 0.0F);
    }

    /** Lo deprisa que va (iconos por tick). */
    public static float velocidad(float tt) {
        return (posicion(tt + 0.05F) - posicion(tt - 0.05F)) / 0.1F;
    }

    /** El latido del suspense (0 a 1): sube de golpe en cada latido y se apaga. */
    public static float latido(float tt) {
        float v = 0.0F;
        for (int l : LATIDOS) {
            float d = tt - l;
            if (d >= 0 && d < 12) {
                v = Math.max(v, (float) Math.exp(-d / 2.6F));
            }
        }
        return v;
    }

    /** Lo metido que esta uno en el suspense (0 a 1): crece desde que frena del todo hasta el cerrojo. */
    public static float tension(float tt) {
        if (tt >= T_PARA) {
            return Math.max(0.0F, 1.0F - (tt - T_PARA) / 6.0F);
        }
        float k = Mth.clamp((tt - 112) / (T_PARA - 112.0F), 0.0F, 1.0F);
        return k * k * (3 - 2 * k);
    }

    /** El temblor de la camara (yaw, pitch, roll en grados), o null si no tiembla: los latidos y el golpe del cerrojo. */
    public static float @Nullable [] angulos(float parcial) {
        if (!activa) {
            return null;
        }
        float tt = tiempo(parcial);
        float fuerza = 0.35F * latido(tt) * tension(tt);
        float d = tt - T_PARA;
        if (d >= 0 && d < 16) {
            fuerza = Math.max(fuerza, 1.7F * (float) Math.exp(-d / 3.2F));
        }
        if (fuerza <= 0.01F) {
            return null;
        }
        float a = tt * 3.1F;
        return new float[]{Mth.sin(a * 1.3F) * fuerza, Mth.sin(a * 1.7F + 1.0F) * fuerza * 0.8F, Mth.sin(a * 0.9F + 2.0F) * fuerza * 0.5F};
    }

    private static void sonar(Minecraft mc, SoundEvent evento, float volumen) {
        SoundInstance s = new SimpleSoundInstance(evento.location(), SoundSource.MASTER, volumen, 1.0F,
                SoundInstance.createUnseededRandom(), false, 0, SoundInstance.Attenuation.NONE, 0.0, 0.0, 0.0, true);
        sonando.add(s);
        mc.getSoundManager().play(s);
    }

    /** Si la quitan a mitad, se callan sus sonidos. */
    private static void callar(Minecraft mc) {
        for (SoundInstance s : sonando) {
            mc.getSoundManager().stop(s);
        }
        sonando.clear();
    }
}
