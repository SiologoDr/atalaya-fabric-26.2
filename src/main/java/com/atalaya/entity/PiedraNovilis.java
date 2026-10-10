package com.atalaya.entity;

import com.atalaya.particula.AtalayaParticulas;
import com.atalaya.sonido.AtalayaSonidos;
import java.util.ArrayList;
import java.util.List;
import net.minecraft.ChatFormatting;
import net.minecraft.core.particles.SimpleParticleType;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.phys.Vec3;

/**
 * Piedra, Papel o Tijera (fase III): reta a todo el grupo a la vez. Alza el
 * puno: "Piedra... papel... ¡tijera!". Durante la cuenta cada uno elige con
 * las teclas 1, 2 y 3 (la casilla de la barra que tenga elegida) y le sale
 * encima; al "¡tijera!", el saca lo suyo en su puno de fuego. A veces se le
 * escapa una pista: el yelmo le brilla del color de lo que va a sacar.
 *
 * En cada ronda cuenta lo que saca la mayoria: si le gana, la ronda es del
 * grupo. Cada uno que pierde (o no saca nada) se quema, sin morir. Cinco rondas
 * (se acaba antes si ya esta decidido): si el grupo gana mas que el, aturdido
 * 6 s. Mientras, ni ataca ni le entra nada.
 */
final class PiedraNovilis extends MinijuegoNovilis {

    static final int PREPARA = 30;
    static final int RONDAS = 5;
    static final int RONDA = 80;
    /** Los golpes de la cuenta (ticks desde que empieza la ronda): piedra, papel y ¡tijera! (cuando se saca). */
    static final int GOLPE_1 = 10;
    static final int GOLPE_2 = 25;
    static final int SACA = 40;
    /** Cuando alza el puno (la animacion lo tiene arriba 14 ticks despues). */
    private static final int ALZA = SACA - 18;
    /** Cuando se mira si ya esta decidido (tras ver el resultado). */
    private static final int MIRA = 70;
    static final int DURA = PREPARA + RONDAS * RONDA + 10;
    private static final float PIERDE = 5.0F;

    private final List<Player> jugadores = new ArrayList<>();
    private int ronda;
    private int golpe;
    private int suya;
    private boolean pista;
    private int resultado;
    private int grupo;
    private int el;
    private boolean decidido;

    PiedraNovilis(NovilisEntity n) {
        super(n, MinijuegosNovilis.PIEDRA, DURA);
    }

    @Override
    boolean empezar(ServerLevel nivel, List<Player> js) {
        if (js.isEmpty()) {
            return false;
        }
        jugadores.addAll(js);
        necesario = RONDAS;
        n.avisarMini(nivel, Component.translatable("hud.atalaya.novilis.piedra_empieza").withStyle(ChatFormatting.GOLD));
        return true;
    }

    @Override
    int info() {
        return MinijuegosNovilis.infoPiedra(ronda, golpe, golpe >= 3 ? suya : 0, resultado, grupo, el);
    }

    @Override
    void tick(ServerLevel nivel) {
        jugadores.removeIf(p -> !p.isAlive() || p.isRemoved() || p.isSpectator() || p.isCreative());
        if (decidido || t < PREPARA) {
            return;
        }
        int k = (t - PREPARA) % RONDA;
        int r = (t - PREPARA) / RONDA + 1;
        if (r > RONDAS) {
            return;
        }
        if (k == 0) {
            ronda = r;
            golpe = 0;
            resultado = 0;
            suya = 1 + nivel.getRandom().nextInt(3);
            pista = nivel.getRandom().nextBoolean();
        }
        cuenta = ronda;
        if (k == GOLPE_1 || k == GOLPE_2) {
            golpe = k == GOLPE_1 ? 1 : 2;
            nivel.playSound(null, n.getX(), n.getY() + 8, n.getZ(), AtalayaSonidos.NOVILIS_PIEDRA_CUENTA, SoundSource.HOSTILE, 6.0F,
                    k == GOLPE_1 ? 0.9F : 1.0F);
        }
        if (k == ALZA) {
            n.alzarMini();
        }
        if (k < SACA && k % 4 == 0) {
            // Lo que lleva elegido cada uno, encima de su cabeza.
            for (Player p : jugadores) {
                int m = mano(p);
                if (m != MinijuegosNovilis.NADA) {
                    icono(nivel, m, p.getX(), p.getY() + p.getBbHeight() + 0.7, p.getZ(), 0.45F, 6);
                }
            }
        }
        if (pista && k >= GOLPE_1 && k < SACA && k % 3 == 0) {
            // La pista: el yelmo le brilla del color de lo que va a sacar.
            Vec3 c = n.yelmoMini();
            nivel.sendParticles(tipo(suya), true, true, c.x, c.y, c.z, 0, 0.18, 8, 0, 1.0);
            nivel.sendParticles(tipo(suya), true, true, c.x + 0.6, c.y + 0.2, c.z, 0, 0.14, 8, 0, 1.0);
            nivel.sendParticles(tipo(suya), true, true, c.x - 0.6, c.y + 0.2, c.z, 0, 0.14, 8, 0, 1.0);
        }
        if (k == SACA) {
            sacar(nivel);
        }
        if (k == MIRA) {
            int quedan = RONDAS - ronda;
            if (grupo > el + quedan || el >= grupo + quedan) {
                decidido = true;
                n.acabarMinijuego(nivel, grupo > el, true);
            }
        }
    }

    /** ¡Tijera!: saca lo suyo y se ve quien gana. */
    private void sacar(ServerLevel nivel) {
        golpe = 3;
        Vec3 c = n.yelmoMini().add(0, 5.5, 0);
        icono(nivel, suya, c.x, c.y, c.z, 3.0F, 44);
        nivel.sendParticles(AtalayaParticulas.NOVILIS_LLAMA, true, true, c.x, c.y, c.z, 30, 1.2, 1.2, 1.2, 0.08);
        nivel.playSound(null, c.x, c.y, c.z, AtalayaSonidos.NOVILIS_PIEDRA_REVELA, SoundSource.HOSTILE, 7.0F, 1.0F);
        int[] votos = new int[4];
        for (Player p : jugadores) {
            int m = mano(p);
            votos[m]++;
            icono(nivel, m == MinijuegosNovilis.NADA ? suya : m, p.getX(), p.getY() + p.getBbHeight() + 0.8, p.getZ(),
                    m == MinijuegosNovilis.NADA ? 0.0F : 0.6F, 36);
            if (MinijuegosNovilis.gana(m, suya)) {
                p.sendOverlayMessage(Component.translatable("hud.atalaya.novilis.piedra_ganas").withStyle(ChatFormatting.GOLD));
                if (p instanceof ServerPlayer sp) {
                    NovilisEntity.sonidoPara(sp, AtalayaSonidos.NOVILIS_PIEDRA_GANA, 1.0F);
                }
                nivel.sendParticles(AtalayaParticulas.NOVILIS_LUZ, true, true, p.getX(), p.getY() + 2.2, p.getZ(), 8, 0.3, 0.2, 0.3, 0.04);
            } else if (MinijuegosNovilis.gana(suya, m)) {
                p.sendOverlayMessage(Component.translatable(m == MinijuegosNovilis.NADA ? "hud.atalaya.novilis.piedra_nada"
                        : "hud.atalaya.novilis.piedra_pierdes").withStyle(ChatFormatting.RED));
                nivel.playSound(null, p.getX(), p.getY(), p.getZ(), AtalayaSonidos.NOVILIS_PIEDRA_PIERDE, SoundSource.HOSTILE, 1.2F, 1.0F);
                nivel.sendParticles(AtalayaParticulas.NOVILIS_LLAMA, true, true, p.getX(), p.getY() + 1.0, p.getZ(), 10, 0.3, 0.6, 0.3, 0.03);
                n.quemarMini(nivel, p, PIERDE, 1);
            } else {
                p.sendOverlayMessage(Component.translatable("hud.atalaya.novilis.piedra_empate").withStyle(ChatFormatting.GRAY));
            }
        }
        // Lo que saca el grupo: lo que mas han sacado (a suertes si empatan).
        int mejor = 0;
        List<Integer> empatan = new ArrayList<>();
        for (int m = 1; m <= 3; m++) {
            if (votos[m] > mejor) {
                mejor = votos[m];
                empatan.clear();
            }
            if (votos[m] == mejor && mejor > 0) {
                empatan.add(m);
            }
        }
        int delGrupo = empatan.isEmpty() ? MinijuegosNovilis.NADA : empatan.get(nivel.getRandom().nextInt(empatan.size()));
        if (MinijuegosNovilis.gana(delGrupo, suya)) {
            resultado = 1;
            grupo++;
        } else if (MinijuegosNovilis.gana(suya, delGrupo)) {
            resultado = 2;
            el++;
        } else {
            resultado = 3;
        }
        n.avisarMini(nivel, Component.translatable("hud.atalaya.novilis.piedra_ronda_" + resultado,
                Component.translatable("hud.atalaya.novilis.mano_" + MinijuegosNovilis.MANOS[delGrupo]),
                Component.translatable("hud.atalaya.novilis.mano_" + MinijuegosNovilis.MANOS[suya]))
                .withStyle(resultado == 1 ? ChatFormatting.GOLD : resultado == 2 ? ChatFormatting.RED : ChatFormatting.GRAY));
    }

    /** Lo que saca este: la casilla 1, 2 o 3 de la barra (cualquier otra: nada). */
    static int mano(Player p) {
        int s = p.getInventory().getSelectedSlot();
        return s >= 0 && s <= 2 ? s + 1 : MinijuegosNovilis.NADA;
    }

    static SimpleParticleType tipo(int m) {
        return m == MinijuegosNovilis.PAPEL ? AtalayaParticulas.NOVILIS_PAPEL
                : m == MinijuegosNovilis.TIJERA ? AtalayaParticulas.NOVILIS_TIJERA : AtalayaParticulas.NOVILIS_PIEDRA;
    }

    /** Un icono quieto en el aire (la velocidad X es su tamano y la Y lo que dura). */
    private static void icono(ServerLevel nivel, int m, double x, double y, double z, float tam, int dura) {
        if (tam <= 0.0F) {
            return;
        }
        nivel.sendParticles(tipo(m), true, true, x, y, z, 0, tam, dura, 0, 1.0);
    }

    @Override
    boolean exitoAlAcabar() {
        return grupo > el;
    }

    @Override
    void forzarExito(ServerLevel nivel) {
        decidido = true;
        n.acabarMinijuego(nivel, true, true);
    }

    @Override
    void limpiar(ServerLevel nivel, boolean exito, boolean avisar) {
        jugadores.clear();
    }
}
