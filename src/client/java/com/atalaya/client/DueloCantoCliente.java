package com.atalaya.client;

import com.atalaya.entity.NereaEntity;
import com.atalaya.net.AtalayaRed;
import com.atalaya.sonido.AtalayaSonidos;
import net.fabricmc.fabric.api.client.networking.v1.ClientPlayNetworking;
import net.minecraft.client.Minecraft;
import net.minecraft.client.resources.sounds.SimpleSoundInstance;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.world.entity.Entity;
import org.jspecify.annotations.Nullable;

/**
 * El Duelo de Canto de Nerea (octubre de 2026, fase IV), en el cliente del
 * elegido: las notas bajan por cuatro carriles (A, S, D y F) y hay que pulsar
 * cada una al llegar a la cuerda. Las notas salen de la misma semilla que en el
 * servidor (NereaEntity.notasDuelo); cada nota se juzga aqui al momento y se le
 * manda (AtalayaRed.DueloNota): el lag no hace fallar.
 *
 * Lo que lo hace un duelo y no solo un panel (Juan: "mas interactivo"): cada
 * nota acertada suena con el arpa del abismo (un tono por carril) y, en el
 * mundo, te sale una nota encima de la cabeza (la pone el servidor: la ven
 * todos); a Nerea le salen las suyas a ritmo, como si tambien tocara. Nada vuela
 * entre ella y los duelistas: con un tercio del grupo cantando, la pantalla se
 * llenaria (Juan). Si la fallas, la pantalla se tine de violeta (el trance que
 * se acerca) y se corta la racha. La cuenta atras suena, y al final, o le vuelves
 * el canto o caes en el.
 *
 * Las teclas llegan por OfrendaTecladoMixin (como las de la Ofrenda de Novilis):
 * mientras dura, no van al juego. DueloCantoHud lo pinta.
 */
public final class DueloCantoCliente {

    /** La ventana para acertar una nota (ticks a cada lado de la cuerda): 0,15 s. */
    public static final float VENTANA = 3.0F;
    /** Por debajo de esto (ticks), la nota es perfecta. */
    public static final float PERFECTA = 1.2F;
    /** Lo que se ve por delante (ticks): una nota tarda esto en bajar del todo, y en volar de su boca a ti. */
    public static final float ANTES = 30.0F;
    private static final String CARRILES = "ASDF";
    private static final int[] COLOR = {0x4FD8F0, 0x9A7BFF, 0xD45AF0, 0xF06AA8};

    private static boolean activo;
    private static int jefe = -1;
    private static int semilla;
    private static int[][] notas = new int[0][2];
    /** 0 sin juzgar, 1 bien, 2 perfecta, 3 fallada. */
    private static int[] juicio = new int[0];
    private static int aciertos;
    private static int fallos;
    private static int racha;
    private static int rachaMejor;
    private static long rachaEn = -100;
    /** El ultimo juicio (para el letrero) y cuando, en ticks del reloj. */
    private static int ultimoJuicio;
    private static long cuandoJuicio = -100;
    /** Por carril: cuando se pulso su tecla, cuando se acerto (y si perfecta) y cuando se fallo. */
    private static final long[] pulsadoEn = {-100, -100, -100, -100};
    private static final long[] aciertoEn = {-100, -100, -100, -100};
    private static final boolean[] perfectoEn = new boolean[4];
    private static final long[] falloEn = {-100, -100, -100, -100};
    /** El trance que se acerca: sube con cada fallo y baja solo (la vineta violeta). */
    private static float trance;
    private static int cuenta = 99;
    private static long reloj;
    private static long fin = -1000;
    private static boolean gano;
    private static @Nullable NereaEntity nerea;
    /** Solo pruebas (FotosPrueba, "DUELO_AUTO 1"): se toca solo, para fotografiarlo. */
    static boolean auto;

    private DueloCantoCliente() {
    }

    public static boolean activo() {
        return activo;
    }

    public static int[][] notas() {
        return notas;
    }

    public static int[] juicio() {
        return juicio;
    }

    public static int aciertos() {
        return aciertos;
    }

    public static int fallos() {
        return fallos;
    }

    public static int racha() {
        return racha;
    }

    public static int rachaMejor() {
        return rachaMejor;
    }

    /** El dibujo de la nota i (0 corchea, 1 dos corcheas, 2 negra): el mismo en el panel y en la que vuela. */
    public static int forma(int i) {
        return Math.floorMod(semilla + i, 3);
    }

    public static int ultimoJuicio() {
        return ultimoJuicio;
    }

    public static float desdeJuicio(float parcial) {
        return reloj - cuandoJuicio + parcial;
    }

    public static float desdeRacha(float parcial) {
        return reloj - rachaEn + parcial;
    }

    public static float desdePulsado(int carril, float parcial) {
        return reloj - pulsadoEn[carril] + parcial;
    }

    public static float desdeAcierto(int carril, float parcial) {
        return reloj - aciertoEn[carril] + parcial;
    }

    public static boolean perfecto(int carril) {
        return perfectoEn[carril];
    }

    public static float desdeFallo(int carril, float parcial) {
        return reloj - falloEn[carril] + parcial;
    }

    public static float trance() {
        return trance;
    }

    public static float desdeFin(float parcial) {
        return reloj - fin + parcial;
    }

    public static float reloj(float parcial) {
        return reloj + parcial;
    }

    public static boolean gano() {
        return gano;
    }

    /** Ticks desde que acabo la preparacion (negativo mientras se prepara). */
    public static float ahora(float parcial) {
        NereaEntity n = nerea;
        if (n == null) {
            return -999;
        }
        return n.tickCount - n.inicioEstado + parcial;
    }

    public static void tick(Minecraft mc) {
        reloj++;
        trance = Math.max(0.0F, trance - 0.015F);
        if (mc.level == null || mc.player == null) {
            activo = false;
            nerea = null;
            return;
        }
        NereaEntity encontrada = null;
        for (Entity e : mc.level.entitiesForRendering()) {
            if (e instanceof NereaEntity n && n.isAlive() && n.getEstado() == NereaEntity.DUELO && n.esDuelista(mc.player.getId())) {
                encontrada = n;
                break;
            }
        }
        if (encontrada != null && (!activo || encontrada.getId() != jefe || encontrada.getSemillaDuelo() != semilla)) {
            empezar(encontrada);
        } else if (encontrada == null && activo) {
            activo = false;
            fin = reloj;
            gano = aciertos >= NereaEntity.DUELO_ACIERTOS;
            sonar(mc, gano ? AtalayaSonidos.NEREA_DUELO_GANA : AtalayaSonidos.NEREA_DUELO_PIERDE, 1.0F, 1.0F);
            if (gano) {
                trance = 0.0F;
            }
            nerea = null;
        }
        if (!activo) {
            return;
        }
        float ahora = ahora(0.0F);
        // La cuenta atras: 3, 2, 1... y a cantar (la ultima, mas aguda).
        int c = ahora < 0 ? (int) Math.ceil(-ahora / 20.0F) : 0;
        if (c != cuenta) {
            cuenta = c;
            if (c <= 3) {
                sonar(mc, AtalayaSonidos.NEREA_DUELO_CUENTA, 0.9F, c == 0 ? 2.0F : 1.0F);
            }
        }
        for (int i = 0; i < notas.length; i++) {
            float faltan = notas[i][0] - ahora;
            if (auto && juicio[i] == 0 && i % 5 != 3 && Math.abs(notas[i][0] - ahora) <= 0.6F) {
                pulsar(CARRILES.charAt(notas[i][1]));
            }
            // Las que pasan la cuerda sin pulsar: falladas.
            if (juicio[i] == 0 && ahora > notas[i][0] + VENTANA) {
                juzgar(mc, i, false, 3);
            }
        }
    }

    private static void empezar(NereaEntity n) {
        activo = true;
        nerea = n;
        jefe = n.getId();
        semilla = n.getSemillaDuelo();
        notas = NereaEntity.notasDuelo(semilla);
        juicio = new int[notas.length];
        aciertos = 0;
        fallos = 0;
        racha = 0;
        rachaMejor = 0;
        rachaEn = -100;
        ultimoJuicio = 0;
        cuandoJuicio = -100;
        cuenta = 99;
        trance = 0.0F;
        fin = -1000;
        gano = false;
        for (int c = 0; c < 4; c++) {
            pulsadoEn[c] = -100;
            aciertoEn[c] = -100;
            falloEn[c] = -100;
        }
    }

    private static void juzgar(Minecraft mc, int i, boolean bien, int valor) {
        juicio[i] = valor;
        ultimoJuicio = valor;
        cuandoJuicio = reloj;
        int carril = notas[i][1];
        if (bien) {
            aciertos++;
            racha++;
            rachaMejor = Math.max(rachaMejor, racha);
            rachaEn = reloj;
            aciertoEn[carril] = reloj;
            perfectoEn[carril] = valor == 2;
            sonar(mc, nota(carril), 1.0F, 1.0F);
            if (valor == 2) {
                sonar(mc, AtalayaSonidos.NEREA_DUELO_PERFECTO, 0.6F, 1.0F);
            }
        } else {
            fallos++;
            racha = 0;
            falloEn[carril] = reloj;
            trance = Math.min(1.0F, trance + 0.3F);
            sonar(mc, AtalayaSonidos.NEREA_DUELO_FALLO, 0.9F, 1.0F);
        }
        ClientPlayNetworking.send(new AtalayaRed.DueloNota(jefe, i, bien));
    }

    private static SoundEvent nota(int carril) {
        return switch (carril) {
            case 0 -> AtalayaSonidos.NEREA_DUELO_NOTA1;
            case 1 -> AtalayaSonidos.NEREA_DUELO_NOTA2;
            case 2 -> AtalayaSonidos.NEREA_DUELO_NOTA3;
            default -> AtalayaSonidos.NEREA_DUELO_NOTA4;
        };
    }

    private static void sonar(Minecraft mc, SoundEvent s, float volumen, float tono) {
        mc.getSoundManager().play(SimpleSoundInstance.forUI(s, tono, volumen));
    }

    /**
     * Una letra pulsada (en mayuscula, segun la distribucion del teclado). Las que
     * no son de un carril, o las que no tienen nota cerca, se tragan sin fallar
     * (pero la tecla se hunde igual: se ve que la has pulsado).
     *
     * @return si se la ha quedado el Duelo (no debe llegar al juego)
     */
    public static boolean pulsar(char letra) {
        if (!activo) {
            return false;
        }
        int carril = CARRILES.indexOf(letra);
        if (carril >= 0) {
            pulsadoEn[carril] = reloj;
        }
        float ahora = ahora(0.0F);
        if (carril < 0 || ahora < 0) {
            return true;
        }
        int mejor = -1;
        float dist = VENTANA + 0.001F;
        for (int i = 0; i < notas.length; i++) {
            if (juicio[i] != 0 || notas[i][1] != carril) {
                continue;
            }
            float d = Math.abs(notas[i][0] - ahora);
            if (d < dist) {
                dist = d;
                mejor = i;
            }
        }
        if (mejor >= 0) {
            juzgar(Minecraft.getInstance(), mejor, true, dist <= PERFECTA ? 2 : 1);
        }
        return true;
    }
}
