package com.atalaya.client;

import com.atalaya.entity.NovilisEntity;
import com.atalaya.net.AtalayaRed;
import com.atalaya.sonido.AtalayaSonidos;
import net.fabricmc.fabric.api.client.networking.v1.ClientPlayNetworking;
import net.minecraft.client.CameraType;
import net.minecraft.client.Minecraft;
import net.minecraft.client.resources.sounds.SimpleSoundInstance;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.phys.Vec3;
import org.jspecify.annotations.Nullable;

/**
 * La secuencia de teclas de la Ofrenda al Sol, en el cliente del atrapado.
 *
 * Cuando Novilis tiene en las manos al jugador local, la secuencia sale de la
 * misma semilla que en el servidor (NovilisEntity.teclasOfrenda): solo letras
 * de la A a la Z. Cada tecla que se pulsa (OfrendaTecladoMixin) se comprueba
 * aqui al momento, sin esperar al servidor, y se le manda (el lag no hace
 * fallar). Una mal: se acabo. El tiempo lo lleva tambien el servidor, con un
 * poco de margen.
 *
 * Mientras dura, la camara se aleja (como con F5) para que se vea que te tiene;
 * al acabar vuelve a la que habia. OfrendaHud lo pinta.
 *
 * Al agarrarte hay 3 s para prepararse (NovilisEntity.OFRENDA_PREPARA): la
 * cuenta atras 3, 2, 1 con su tic; mientras, las teclas se tragan sin contar
 * (antes la gente tocaba algo sin enterarse y fallaba). Luego empieza el tiempo.
 */
public final class OfrendaCliente {

    private static boolean activo;
    private static int jefe = -1;
    private static int semilla;
    private static char[] teclas = new char[0];
    private static int indice;
    private static long inicio;
    private static boolean fallo;
    private static boolean exito;
    private static long fin = -1000;
    private static @Nullable CameraType camaraAntes;
    /** El ultimo segundo de la cuenta atras que sono (para el tic de cada uno). */
    private static int cuentaSonada = -1;

    private OfrendaCliente() {
    }

    public static boolean activo() {
        return activo;
    }

    public static char[] teclas() {
        return teclas;
    }

    public static int indice() {
        return indice;
    }

    public static boolean fallo() {
        return fallo;
    }

    public static boolean exito() {
        return exito;
    }

    /** Lo que queda de tiempo, de 1 a 0 (lleno mientras se prepara). */
    public static float tiempoRestante(float parcial) {
        Minecraft mc = Minecraft.getInstance();
        if (mc.level == null) {
            return 0.0F;
        }
        float pasado = mc.level.getGameTime() - inicio - NovilisEntity.OFRENDA_PREPARA + parcial;
        return Mth.clamp(1.0F - pasado / NovilisEntity.OFRENDA_TIEMPO, 0.0F, 1.0F);
    }

    /** Los segundos que quedan para prepararse (0: ya cuentan las teclas). */
    public static float preparacion(float parcial) {
        Minecraft mc = Minecraft.getInstance();
        if (!activo || mc.level == null) {
            return 0.0F;
        }
        float pasado = mc.level.getGameTime() - inicio + parcial;
        return Math.max(0.0F, (NovilisEntity.OFRENDA_PREPARA - pasado) / 20.0F);
    }

    /** Ticks desde que acabo (bien o mal). */
    public static float ticksDesdeFin(float parcial) {
        Minecraft mc = Minecraft.getInstance();
        if (mc.level == null) {
            return 1000.0F;
        }
        return mc.level.getGameTime() - fin + parcial;
    }

    /** Cada tick: mira si algun Novilis tiene al jugador local en las manos. */
    public static void tick(Minecraft mc) {
        if (mc.level == null || mc.player == null) {
            terminar(mc, false);
            return;
        }
        NovilisEntity dueno = null;
        for (Entity e : mc.level.entitiesForRendering()) {
            if (e instanceof NovilisEntity n && n.getIdOfrenda() == mc.player.getId() && n.getTeclasOfrenda() > 0) {
                dueno = n;
                break;
            }
        }
        if (dueno != null && (!activo || dueno.getId() != jefe || dueno.getSemillaOfrenda() != semilla)) {
            empezar(mc, dueno);
        } else if (dueno == null && activo) {
            terminar(mc, indice >= teclas.length && teclas.length > 0);
        }
        if (activo && !fallo) {
            // La cuenta atras: un tic por segundo y uno mas agudo al empezar.
            int seg = (int) Math.ceil(preparacion(0.0F));
            if (seg != cuentaSonada) {
                cuentaSonada = seg;
                mc.getSoundManager().play(SimpleSoundInstance.forUI(AtalayaSonidos.NOVILIS_OFRENDA_TECLA, seg > 0 ? 0.6F : 1.4F));
            }
        }
        if (activo && preparacion(0.0F) <= 0.0F && tiempoRestante(0.0F) <= 0.0F && !fallo) {
            // Se acabo el tiempo: el servidor tambien lo vera (con su margen).
            fallar(mc);
        }
    }

    private static void empezar(Minecraft mc, NovilisEntity n) {
        activo = true;
        jefe = n.getId();
        semilla = n.getSemillaOfrenda();
        teclas = NovilisEntity.teclasOfrenda(semilla, n.getTeclasOfrenda());
        indice = 0;
        inicio = mc.level.getGameTime();
        fallo = false;
        exito = false;
        fin = -1000;
        cuentaSonada = -1;
        if (camaraAntes == null) {
            camaraAntes = mc.options.getCameraType();
            mc.options.setCameraType(CameraType.THIRD_PERSON_BACK);
        }
        // De cara a el y mirando un poco arriba: con la camara detras (y lejos,
        // camera_distance) se ve el atrapado en sus manos, su cara y su sol.
        Vec3 hacia = n.position().subtract(mc.player.position());
        float giro = (float) (Mth.atan2(hacia.z, hacia.x) * Mth.RAD_TO_DEG) - 90.0F;
        mc.player.setYRot(giro);
        mc.player.setXRot(-12.0F);
        mc.player.yRotO = mc.player.getYRot();
        mc.player.xRotO = mc.player.getXRot();
        mc.player.setYHeadRot(giro);
    }

    private static void terminar(Minecraft mc, boolean bien) {
        if (!activo) {
            return;
        }
        activo = false;
        if (!fallo) {
            exito = bien;
            fallo = !bien;
        }
        if (mc.level != null) {
            fin = mc.level.getGameTime();
        }
        if (camaraAntes != null) {
            mc.options.setCameraType(camaraAntes);
            camaraAntes = null;
        }
    }

    private static void fallar(Minecraft mc) {
        fallo = true;
        if (mc.level != null) {
            fin = mc.level.getGameTime();
        }
        mc.getSoundManager().play(SimpleSoundInstance.forUI(AtalayaSonidos.NOVILIS_OFRENDA_FALLO, 1.0F));
    }

    /**
     * Una letra pulsada (ya en mayuscula, segun la distribucion del teclado).
     *
     * @return si se la ha quedado la Ofrenda (y no debe llegar al juego)
     */
    public static boolean pulsar(char letra) {
        if (!activo) {
            return false;
        }
        Minecraft mc = Minecraft.getInstance();
        if (fallo || indice >= teclas.length || preparacion(0.0F) > 0.0F) {
            // Acabada, o aun preparandose: la tecla se traga sin contar.
            return true;
        }
        boolean bien = teclas[indice] == letra;
        ClientPlayNetworking.send(new AtalayaRed.OfrendaTecla(jefe, indice, bien));
        if (bien) {
            indice++;
            float tono = 0.8F + 0.6F * indice / Math.max(1, teclas.length);
            mc.getSoundManager().play(SimpleSoundInstance.forUI(AtalayaSonidos.NOVILIS_OFRENDA_TECLA, tono));
        } else {
            fallar(mc);
        }
        return true;
    }
}
