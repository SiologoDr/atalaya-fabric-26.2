package com.atalaya.client;

import net.minecraft.client.Minecraft;
import net.minecraft.util.Mth;
import net.minecraft.world.phys.Vec3;

/**
 * Lo que se siente cerca de Nerea (y de Aeralis y Rajang) aunque no te toque: la camara tiembla con
 * sus golpes, retumba mientras gira las cadenas o remueve el agua, y el miedo
 * oscurece los bordes de la pantalla cuando ruge o te clava la mirada.
 *
 * Todo es del cliente y se apaga solo. La fuerza de cada golpe cae con la
 * distancia, y el temblor respeta el ajuste de efectos de pantalla de
 * accesibilidad: con los efectos al 0 % no se mueve nada.
 */
public final class NereaPresencia {

    /** Grados de temblor ahora y en el tick anterior (para interpolar). */
    private static float temblor;
    private static float temblorAnt;
    /** Temblor que se mantiene mientras dura algo (molino, remolino). Se pide cada tick. */
    private static float retumbo;
    /** De 0 a 1: lo oscuros que se ponen los bordes. */
    private static float miedo;
    private static float miedoAnt;
    private static boolean miedoAire;
    private static boolean miedoTierra;

    private NereaPresencia() {
    }

    /** Un golpe en (x, y, z): tiembla mas cuanto mas cerca. */
    public static void sacudir(double x, double y, double z, float fuerza, float alcance) {
        float k = caida(x, y, z, alcance);
        temblor = Math.max(temblor, fuerza * k);
        // Un golpe gordo que se nota: la musica del jefe lo acentua (MusicaJefes).
        if (k > 0.15F) {
            MusicaJefes.golpe(fuerza);
        }
    }

    /** Temblor sostenido mientras se pida, tick a tick. */
    public static void retumbar(double x, double y, double z, float fuerza, float alcance) {
        retumbo = Math.max(retumbo, fuerza * caida(x, y, z, alcance));
    }

    /** Un rugido o una mirada: sube el miedo segun la distancia. */
    public static void asustar(double x, double y, double z, float nivel, float alcance) {
        asustar(x, y, z, nivel, alcance, false);
    }

    /**
     * Lo mismo, diciendo de quien es el miedo: el de Aeralis cierra los bordes
     * con nubes de tormenta en vez de con el fondo del mar.
     */
    public static void asustar(double x, double y, double z, float nivel, float alcance, boolean aire) {
        float m = Math.min(1.0F, nivel * caida(x, y, z, alcance));
        if (m > miedo) {
            miedo = m;
            miedoAire = aire;
            miedoTierra = false;
        }
    }

    /** El miedo de Rajang: la selva y las grietas de jade se cierran sobre los bordes. */
    public static void asustarTierra(double x, double y, double z, float nivel, float alcance) {
        float m = Math.min(1.0F, nivel * caida(x, y, z, alcance));
        if (m > miedo) {
            miedo = m;
            miedoAire = false;
            miedoTierra = true;
        }
    }

    /** Si el miedo de ahora es de Rajang. */
    public static boolean miedoDeTierra() {
        return miedoTierra;
    }

    /** Si el miedo de ahora es de Aeralis. */
    public static boolean miedoDeAire() {
        return miedoAire;
    }

    private static float caida(double x, double y, double z, float alcance) {
        Minecraft mc = Minecraft.getInstance();
        if (mc.player == null) {
            return 0.0F;
        }
        double d = mc.player.position().distanceTo(new Vec3(x, y, z));
        return (float) Mth.clamp(1.0 - d / alcance, 0.0, 1.0);
    }

    public static void tick() {
        temblorAnt = temblor;
        temblor = Math.max(temblor * 0.8F, retumbo);
        retumbo = 0.0F;
        miedoAnt = miedo;
        miedo *= 0.965F;
        if (temblor < 0.01F) {
            temblor = 0.0F;
        }
    }

    /** (guinada, cabeceo, alabeo) en grados para este fotograma, o null si no tiembla. */
    public static float[] angulos(float parcial) {
        float a = Mth.lerp(parcial, temblorAnt, temblor);
        if (a <= 0.001F) {
            return null;
        }
        Minecraft mc = Minecraft.getInstance();
        a *= mc.options.screenEffectScale().get().floatValue();
        if (a <= 0.001F) {
            return null;
        }
        // Ruido suave: senos de frecuencias que no se repiten entre si.
        float t = (System.nanoTime() % 1_000_000_000_000L) / 1.0E9F;
        float g = Mth.sin(t * 31.0F) * 0.6F + Mth.sin(t * 17.3F + 1.3F) * 0.4F;
        float c = Mth.sin(t * 27.1F + 2.1F) * 0.6F + Mth.sin(t * 13.7F + 0.4F) * 0.4F;
        float l = Mth.sin(t * 22.9F + 4.2F) * 0.7F + Mth.sin(t * 9.1F) * 0.3F;
        return new float[]{g * a * 0.6F, c * a, l * a * 0.8F};
    }

    public static float miedo(float parcial) {
        return Mth.lerp(parcial, miedoAnt, miedo);
    }
}
