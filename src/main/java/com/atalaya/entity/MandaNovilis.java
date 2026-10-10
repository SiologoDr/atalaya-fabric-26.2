package com.atalaya.entity;

import com.atalaya.particula.AtalayaParticulas;
import com.atalaya.sonido.AtalayaSonidos;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.UUID;
import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.phys.Vec3;

/**
 * El Caballero Manda (fase I; "Simon dice", con un caballero). Planta la
 * espada y da seis ordenes, una cada 2,5 s: arrodillaos (Shift), saltad, mirad
 * al sol y quietos. Solo se obedece si la orden empieza por "¡Por el Sol...!";
 * si no lo dice, es una trampa y el que la hace, falla (quietos nunca es
 * trampa). Mientras, ni ataca ni le entra nada.
 *
 * Fallar quema: Quemadura I y un golpe que no mata. Si mas de la mitad acaba
 * sin fallar ninguna, "¡Dignos!": se arrodilla, aturdido 6 s.
 */
final class MandaNovilis extends MinijuegoNovilis {

    /** Lo que tarda en dar la primera orden (el estandarte se presenta). */
    static final int PREPARA = 40;
    static final int ORDENES = 6;
    /** Una orden cada 2,5 s. */
    static final int CADA = 50;
    /** Cuando empieza y acaba de mirarse cada orden (ticks desde que la da). */
    static final int MIRA_DESDE = 8;
    static final int MIRA_HASTA = 46;
    static final int DURA = PREPARA + ORDENES * CADA + 10;
    /** Cuantas son trampa (sin "¡Por el Sol...!"). */
    private static final int TRAMPAS = 2;
    /** Lo que se puede mover quien tiene que quedarse quieto (bloques) y lo que sube quien salta. */
    private static final double QUIETO = 0.35;
    private static final double SALTO = 0.45;
    private static final float GOLPE = 6.0F;

    private final int[] ordenes = new int[ORDENES];
    private final boolean[] deVerdad = new boolean[ORDENES];
    private final List<Player> jugadores = new ArrayList<>();
    private final Set<UUID> fallados = new HashSet<>();
    /** Lo de la orden en curso: quien la ha hecho, y donde estaba y lo mas bajo que ha estado cada uno. */
    private final Set<UUID> hecha = new HashSet<>();
    private final Map<UUID, Vec3> desde = new HashMap<>();
    private final Map<UUID, Double> masBajo = new HashMap<>();
    private int actual = -1;

    MandaNovilis(NovilisEntity n) {
        super(n, MinijuegosNovilis.MANDA, DURA);
    }

    @Override
    boolean empezar(ServerLevel nivel, List<Player> js) {
        if (js.isEmpty()) {
            return false;
        }
        jugadores.addAll(js);
        // Las ordenes: sin repetir la misma dos veces seguidas, y las trampas nunca la primera ni quietos.
        int antes = -1;
        for (int i = 0; i < ORDENES; i++) {
            int o;
            do {
                o = nivel.getRandom().nextInt(4);
            } while (o == antes);
            ordenes[i] = o;
            deVerdad[i] = true;
            antes = o;
        }
        List<Integer> posibles = new ArrayList<>();
        for (int i = 1; i < ORDENES; i++) {
            if (ordenes[i] != MinijuegosNovilis.QUIETOS) {
                posibles.add(i);
            }
        }
        java.util.Collections.shuffle(posibles, new java.util.Random(nivel.getRandom().nextLong()));
        for (int k = 0; k < Math.min(TRAMPAS, posibles.size()); k++) {
            deVerdad[posibles.get(k)] = false;
        }
        necesario = jugadores.size();
        cuenta = necesario;
        n.avisarMini(nivel, Component.translatable("hud.atalaya.novilis.manda_empieza").withStyle(ChatFormatting.GOLD));
        return true;
    }

    @Override
    int info() {
        return actual < 0 ? 0 : MinijuegosNovilis.infoManda(ordenes[actual], deVerdad[actual], actual + 1);
    }

    @Override
    void tick(ServerLevel nivel) {
        jugadores.removeIf(p -> !p.isAlive() || p.isRemoved() || p.isSpectator() || p.isCreative());
        int k = t - PREPARA;
        if (k >= 0 && k % CADA == 0 && k / CADA < ORDENES) {
            ordenar(nivel, k / CADA);
        }
        if (actual >= 0) {
            int dentro = t - PREPARA - actual * CADA;
            if (dentro == MIRA_DESDE) {
                for (Player p : jugadores) {
                    desde.put(p.getUUID(), p.position());
                    masBajo.put(p.getUUID(), p.getY());
                }
            }
            if (dentro > MIRA_DESDE && dentro <= MIRA_HASTA) {
                for (Player p : jugadores) {
                    if (loHace(p)) {
                        hecha.add(p.getUUID());
                    }
                    masBajo.merge(p.getUUID(), p.getY(), Math::min);
                }
            }
            if (dentro == MIRA_HASTA) {
                juzgar(nivel);
            }
        }
        int limpios = 0;
        for (Player p : jugadores) {
            if (!fallados.contains(p.getUUID())) {
                limpios++;
            }
        }
        cuenta = limpios;
    }

    private void ordenar(ServerLevel nivel, int i) {
        actual = i;
        hecha.clear();
        desde.clear();
        masBajo.clear();
        n.ordenMini();
    }

    /** Si ahora mismo esta haciendo la orden en curso. */
    private boolean loHace(Player p) {
        UUID u = p.getUUID();
        return switch (ordenes[actual]) {
            case MinijuegosNovilis.ARRODILLAOS -> p.isShiftKeyDown() || p.isCrouching();
            case MinijuegosNovilis.SALTAD -> p.getY() - masBajo.getOrDefault(u, p.getY()) > SALTO;
            case MinijuegosNovilis.MIRAD_SOL -> miraAlSol(p);
            // Quietos: aqui se apunta a quien se MUEVE, andando o saltando (al juzgar se da la vuelta).
            default -> {
                Vec3 d = desde.get(u);
                yield d != null && (Math.hypot(p.getX() - d.x, p.getZ() - d.z) > QUIETO
                        || p.getY() - masBajo.getOrDefault(u, p.getY()) > SALTO);
            }
        };
    }

    /** Mira a su sol (el que flota sobre el, a menos de 13 grados) o muy hacia arriba. */
    private boolean miraAlSol(Player p) {
        Vec3 sol = n.solPropio();
        Vec3 hacia = sol.subtract(p.getEyePosition());
        if (hacia.lengthSqr() < 1.0E-4) {
            return true;
        }
        return p.getLookAngle().dot(hacia.normalize()) > 0.975 || p.getXRot() < -60.0F;
    }

    private void juzgar(ServerLevel nivel) {
        boolean quietos = ordenes[actual] == MinijuegosNovilis.QUIETOS;
        for (Player p : jugadores) {
            boolean laHizo = quietos ? !hecha.contains(p.getUUID()) : hecha.contains(p.getUUID());
            boolean bien = deVerdad[actual] == laHizo;
            if (bien) {
                if (p instanceof ServerPlayer sp) {
                    NovilisEntity.sonidoPara(sp, AtalayaSonidos.NOVILIS_MANDA_BIEN, 1.0F);
                }
                p.sendOverlayMessage(Component.translatable("hud.atalaya.novilis.manda_bien").withStyle(ChatFormatting.GOLD));
                continue;
            }
            fallados.add(p.getUUID());
            String por = deVerdad[actual] ? "hud.atalaya.novilis.manda_lento" : "hud.atalaya.novilis.manda_trampa";
            p.sendOverlayMessage(Component.translatable(por).withStyle(ChatFormatting.RED));
            n.quemarMini(nivel, p, GOLPE, 1);
            nivel.sendParticles(AtalayaParticulas.NOVILIS_LLAMA, true, true, p.getX(), p.getY() + 1.0, p.getZ(), 12, 0.3, 0.6, 0.3, 0.03);
            nivel.playSound(null, p.getX(), p.getY(), p.getZ(), AtalayaSonidos.NOVILIS_MANDA_FALLO,
                    net.minecraft.sounds.SoundSource.HOSTILE, 1.2F, 1.0F);
        }
    }

    @Override
    boolean exitoAlAcabar() {
        return !jugadores.isEmpty() && cuenta * 2 > necesario;
    }

    @Override
    void forzarExito(ServerLevel nivel) {
        fallados.clear();
        n.acabarMinijuego(nivel, true, true);
    }

    @Override
    void limpiar(ServerLevel nivel, boolean exito, boolean avisar) {
        jugadores.clear();
    }
}
