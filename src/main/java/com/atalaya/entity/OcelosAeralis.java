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
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.phys.Vec3;
import org.jspecify.annotations.Nullable;

/**
 * Ocelos (fase I; "luz roja, luz verde"): se posa donde esta y aparta al grupo
 * a 16 bloques. Luego abre y cierra las alas: con los ocelos abiertos (los ojos
 * de sus alas miran, rojos; justo antes se entornan, de ambar) quien se mueva
 * recibe el rayo de un ocelo (un golpe que no mata y Paralisis 2 s; uno por
 * cada vez que se abren); con los ojos cerrados hay que avanzar. El primero que
 * le toque el cuerpo (llegar o pegarle) con los ojos cerrados la tumba:
 * aturdida 6 s. Si a los 20 s nadie ha llegado, levanta el vuelo con una
 * rafaga. Mientras, no le entra nada.
 *
 * Afinado el 10-10-2026: a 14 bloques y con 2 s de ojos cerrados se llegaba en
 * la primera carrera. Ahora se sale de mas lejos, los ojos se cierran menos
 * rato y, con alguien cerca, miran mas: hacen falta tres o cuatro carreras.
 */
final class OcelosAeralis extends MinijuegoAeralis {

    /** Lo que tarda en posarse y apartar al grupo, y el juego despues (20 s). */
    static final int POSA = 50;
    static final int DURA = POSA + 400;
    /** A cuanto aparta al grupo al empezar. */
    static final double SALIDA = 16.0;
    /** Lo cerca que hay que llegar (bloques, en horizontal, desde su centro) para tocarla. */
    private static final double TOCA = 3.4;
    /** El aviso antes de abrir y lo que se perdona al abrir (el tiempo de pararse). */
    private static final int AVISO = 12;
    private static final int PERDON = 4;
    /** Lo que se puede mover quien tiene que estar quieto (bloques) y lo que sube quien salta. */
    private static final double QUIETO = 0.3;
    private static final double SALTO = 0.45;
    private static final float GOLPE = 6.0F;
    /** Lo que estan cerrados (ticks: de 24 a 44) y abiertos (de 24 a 64; con alguien a menos de CERCA, de 40 a 80). */
    private static final int CERRADOS = 24;
    private static final int CERRADOS_MAS = 21;
    private static final int ABIERTOS = 24;
    private static final int ABIERTOS_CERCA = 40;
    private static final int ABIERTOS_MAS = 41;
    private static final double CERCA = 8.0;

    private final List<Player> jugadores = new ArrayList<>();
    private final Map<UUID, Vec3> desde = new HashMap<>();
    private final Map<UUID, Double> masBajo = new HashMap<>();
    /** Los que ya se han llevado el rayo con los ojos abiertos esta vez (el retroceso no les vuelve a contar). */
    private final Set<UUID> rayados = new HashSet<>();
    private int ojos = MinijuegosAeralis.OJOS_CERRADOS;
    private int reloj;
    private int abiertoDesde;
    private boolean hecho;

    OcelosAeralis(AeralisEntity a) {
        super(a, MinijuegosAeralis.OCELOS, DURA);
    }

    @Override
    boolean empezar(ServerLevel nivel, List<Player> js) {
        if (js.isEmpty()) {
            return false;
        }
        jugadores.addAll(js);
        necesario = (int) SALIDA;
        cuenta = necesario;
        a.posarMini();
        a.avisarMini(nivel, Component.translatable("hud.atalaya.aeralis.ocelos_empieza").withStyle(ChatFormatting.AQUA));
        return true;
    }

    @Override
    int info() {
        int apertura = ojos == MinijuegosAeralis.OJOS_ABIERTOS ? 100 : ojos == MinijuegosAeralis.OJOS_AVISO ? 35 : 0;
        return MinijuegosAeralis.infoOcelos(ojos, apertura);
    }

    @Override
    @Nullable double[] destino(ServerLevel nivel) {
        // Posada donde esta.
        return new double[]{a.getX(), a.getZ(), 0.0, 0.0};
    }

    @Override
    @Nullable Vec3 mira(ServerLevel nivel, @Nullable LivingEntity objetivo) {
        Player cerca = masCercano();
        return cerca != null ? cerca.position() : null;
    }

    @Override
    void tick(ServerLevel nivel) {
        jugadores.removeIf(p -> !p.isAlive() || p.isRemoved() || p.isSpectator() || p.isCreative());
        if (hecho) {
            return;
        }
        if (t == POSA - 10) {
            apartar(nivel);
        }
        Player cerca = masCercano();
        cuenta = cerca == null ? necesario : (int) Math.max(0, Math.round(distancia(cerca) - TOCA));
        if (t < POSA) {
            return;
        }
        if (t == POSA) {
            cerrar(nivel, 30);
        }
        if (--reloj <= 0) {
            switch (ojos) {
                case MinijuegosAeralis.OJOS_CERRADOS -> {
                    ojos = MinijuegosAeralis.OJOS_AVISO;
                    reloj = AVISO;
                    a.sonidoMini(AtalayaSonidos.AERALIS_OCELOS_AVISO, 5.0F);
                }
                case MinijuegosAeralis.OJOS_AVISO -> abrir(nivel);
                default -> cerrar(nivel, CERRADOS + nivel.getRandom().nextInt(CERRADOS_MAS));
            }
        }
        if (ojos == MinijuegosAeralis.OJOS_ABIERTOS) {
            int dentro = t - abiertoDesde;
            for (Player p : jugadores) {
                UUID u = p.getUUID();
                if (rayados.contains(u)) {
                    continue;
                }
                if (dentro <= PERDON) {
                    desde.put(u, p.position());
                    masBajo.put(u, p.getY());
                    continue;
                }
                masBajo.merge(u, p.getY(), Math::min);
                Vec3 d = desde.get(u);
                boolean seMueve = d != null && (Math.hypot(p.getX() - d.x, p.getZ() - d.z) > QUIETO
                        || p.getY() - masBajo.getOrDefault(u, p.getY()) > SALTO);
                if (seMueve) {
                    rayo(nivel, p);
                }
            }
        } else if (cerca != null && distancia(cerca) <= TOCA) {
            tocada(nivel, cerca);
        }
    }

    private void abrir(ServerLevel nivel) {
        ojos = MinijuegosAeralis.OJOS_ABIERTOS;
        // Mas rato abiertos si alguien esta cerca: el ultimo tramo es el que cuesta.
        Player cerca = masCercano();
        boolean hayCerca = cerca != null && distancia(cerca) < CERCA;
        reloj = (hayCerca ? ABIERTOS_CERCA : ABIERTOS) + nivel.getRandom().nextInt(ABIERTOS_MAS);
        abiertoDesde = t;
        desde.clear();
        masBajo.clear();
        rayados.clear();
        a.sonidoMini(AtalayaSonidos.AERALIS_OCELOS_ABRE, 6.0F);
        for (Player p : jugadores) {
            p.sendOverlayMessage(Component.translatable("hud.atalaya.aeralis.ocelos_quietos").withStyle(ChatFormatting.RED));
        }
    }

    private void cerrar(ServerLevel nivel, int ticks) {
        ojos = MinijuegosAeralis.OJOS_CERRADOS;
        reloj = ticks;
        a.sonidoMini(AtalayaSonidos.AERALIS_OCELOS_CIERRA, 4.0F);
        for (Player p : jugadores) {
            p.sendOverlayMessage(Component.translatable("hud.atalaya.aeralis.ocelos_avanza").withStyle(ChatFormatting.GREEN));
        }
    }

    /** Al empezar: los que estan a menos de SALIDA salen despedidos hasta el corro. */
    private void apartar(ServerLevel nivel) {
        Vec3 c = a.position();
        for (Player p : jugadores) {
            double d = Math.hypot(p.getX() - c.x, p.getZ() - c.z);
            if (d >= SALIDA) {
                continue;
            }
            Vec3 fuera = d < 0.1 ? new Vec3(1, 0, 0) : new Vec3(p.getX() - c.x, 0, p.getZ() - c.z).normalize();
            Vec3 a2 = c.add(fuera.scale(SALIDA));
            double y = AeralisEntity.sueloBajo(nivel, a2.x, p.getY() + 4, a2.z);
            if (p instanceof ServerPlayer sp) {
                sp.teleportTo(nivel, a2.x, y, a2.z, java.util.Set.of(), p.getYRot(), p.getXRot(), false);
            } else {
                p.teleportTo(a2.x, y, a2.z);
            }
        }
        a.golpeAireMini(nivel, 2.0F, SALIDA);
    }

    /** El rayo de un ocelo: dano que no mata y Paralisis (una vez por cada vez que se abren). */
    private void rayo(ServerLevel nivel, Player p) {
        if (!rayados.add(p.getUUID())) {
            return;
        }
        a.rayoMini(nivel, a.puntoMundo(AeralisGeometria.NUCLEO), p.position().add(0, 1.0, 0));
        a.danoSinMatar(nivel, p, GOLPE);
        a.paralizarMini(p);
        nivel.playSound(null, p.getX(), p.getY(), p.getZ(), AtalayaSonidos.AERALIS_OCELOS_RAYO, SoundSource.HOSTILE, 2.0F, 1.0F);
        p.sendOverlayMessage(Component.translatable("hud.atalaya.aeralis.ocelos_rayo").withStyle(ChatFormatting.RED));
    }

    private void tocada(ServerLevel nivel, Player p) {
        hecho = true;
        Vec3 c = a.puntoMundo(AeralisGeometria.NUCLEO);
        nivel.sendParticles(AtalayaParticulas.AERALIS_LUZ, true, true, c.x, c.y, c.z, 50, 2.0, 2.0, 2.0, 0.2);
        a.sonidoMini(AtalayaSonidos.AERALIS_OCELOS_TOCA, 7.0F);
        a.avisarMini(nivel, Component.translatable("hud.atalaya.aeralis.ocelos_tocada", p.getDisplayName()).withStyle(ChatFormatting.GOLD));
        a.acabarMinijuego(nivel, true, true);
    }

    @Override
    boolean alGolpearla(ServerLevel nivel, @Nullable Entity causante, @Nullable Entity directo) {
        if (!(causante instanceof Player p) || hecho || t < POSA) {
            return false;
        }
        if (ojos == MinijuegosAeralis.OJOS_ABIERTOS) {
            // Pegarle con los ojos abiertos es moverse.
            rayo(nivel, p);
        } else if (directo == p) {
            // Un golpe con la mano (no una flecha) es tocarla.
            tocada(nivel, p);
        }
        return true;
    }

    private double distancia(Player p) {
        return Math.hypot(p.getX() - a.getX(), p.getZ() - a.getZ());
    }

    private @Nullable Player masCercano() {
        Player mejor = null;
        double d = Double.MAX_VALUE;
        for (Player p : jugadores) {
            double dd = distancia(p);
            if (dd < d) {
                d = dd;
                mejor = p;
            }
        }
        return mejor;
    }

    @Override
    void forzarExito(ServerLevel nivel) {
        Player p = masCercano();
        if (p != null) {
            tocada(nivel, p);
        } else {
            a.acabarMinijuego(nivel, true, true);
        }
    }

    @Override
    void limpiar(ServerLevel nivel, boolean exito, boolean avisar) {
        if (!exito && avisar) {
            // Nadie ha llegado: levanta el vuelo con una rafaga que aparta a los de cerca.
            a.golpeAireMini(nivel, 2.6F, 12.0);
            for (Player p : jugadores) {
                if (distancia(p) < 12.0) {
                    Vec3 fuera = new Vec3(p.getX() - a.getX(), 0, p.getZ() - a.getZ()).normalize();
                    p.setDeltaMovement(fuera.x * 1.4, 0.5, fuera.z * 1.4);
                    p.hurtMarked = true;
                }
            }
        }
        jugadores.clear();
    }
}
