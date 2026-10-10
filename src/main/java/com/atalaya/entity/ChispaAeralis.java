package com.atalaya.entity;

import com.atalaya.particula.AtalayaParticulas;
import com.atalaya.sonido.AtalayaSonidos;
import java.util.ArrayList;
import java.util.List;
import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.phys.Vec3;
import org.jspecify.annotations.Nullable;

/**
 * La Chispa (fase IV; la patata caliente): le cae a uno encima una chispa de
 * tormenta con una cuenta atras de 3 s. Antes de que reviente, la pasa mirando
 * a un companero y dando un clic (o pegandole; no le hace dano) y la cuenta
 * vuelve a empezar. Cada pase la carga: con 8 pases esta cargada y quien la
 * lleva tiene 5 s para lanzarsela a ella (mirarla y clic, a 24 bloques, o pegarle). Si sale
 * bien, aturdida 6 s. Si revienta: Paralisis y un golpe que no mata a quien la
 * lleva y a los de al lado (el aro del suelo marca hasta donde), y la carga
 * vuelve a cero (al rato cae otra). Jugando solo salen tres remolinos a su
 * alrededor: pasarsela a uno cuenta como un pase y te la devuelve. Dura 30 s;
 * mientras vuela bajo y no le entra nada mas.
 *
 * Afinado el 10-10-2026: el pase era solo pegando al companero y, con ella
 * volando al lado, el golpe se lo llevaba su cuerpo. Ahora se lanza al que mas
 * se mira (a 14 bloques, en un cono de 25 grados).
 */
final class ChispaAeralis extends MinijuegoAeralis {

    static final int DURA = 600;
    static final int PASES = 8;
    private static final int PASES_SOLO = 6;
    /** La cuenta atras (3 s), la cargada (5 s), lo que tarda en volar de uno a otro y en caer otra. */
    private static final int CUENTA = 60;
    private static final int CARGADA = 100;
    private static final int VUELO = 8;
    private static final int OTRA = 30;
    private static final double REVIENTA = 3.0;
    private static final float GOLPE = 6.0F;
    /** A que altura sobre la cabeza va. */
    private static final double ENCIMA = 0.9;
    /** Hasta donde se lanza a un companero y lo que se perdona de punteria (coseno: 25 grados). */
    private static final double ALCANCE = 14.0;
    private static final double PUNTERIA = 0.906;
    /** Hasta donde se le lanza a ella, cargada (es enorme y vuela en circulo: que no haya que perseguirla). */
    private static final double ALCANCE_ELLA = 24.0;

    private final List<Player> jugadores = new ArrayList<>();
    private final List<RemolinoChispaEntity> remolinos = new ArrayList<>();
    private @Nullable ChispaAeralisEntity chispa;
    private @Nullable Entity portador;
    /** El vuelo de uno a otro: desde donde, a quien y cuando salio (-1: no vuela). */
    private Vec3 vueloDesde = Vec3.ZERO;
    private @Nullable Entity vueloA;
    private int vueloT = -1;
    /** Cuando revienta (t del minijuego) y cuando cae la siguiente (-1: no hay que esperar). */
    private int revienta;
    /** Cuando le llego a quien la lleva (t del minijuego). */
    private int llego;
    private int siguiente = -1;
    private boolean cargada;
    private boolean solo;
    private double angulo;

    ChispaAeralis(AeralisEntity a) {
        super(a, MinijuegosAeralis.CHISPA, DURA);
    }

    @Override
    boolean empezar(ServerLevel nivel, List<Player> js) {
        if (js.isEmpty()) {
            return false;
        }
        jugadores.addAll(js);
        solo = js.size() <= 1;
        necesario = solo ? PASES_SOLO : PASES;
        if (solo) {
            Player p = js.get(0);
            for (int i = 0; i < 3; i++) {
                double ang = Math.PI * 2 * i / 3 + nivel.getRandom().nextDouble();
                double x = p.getX() + Math.cos(ang) * 4.0;
                double z = p.getZ() + Math.sin(ang) * 4.0;
                remolinos.add(RemolinoChispaEntity.crear(nivel, this, new Vec3(x, AeralisEntity.sueloBajo(nivel, x, p.getY() + 2, z), z)));
            }
        }
        Vec3 pecho = a.puntoMundo(AeralisGeometria.NUCLEO);
        chispa = ChispaAeralisEntity.crear(nivel, this, pecho.x, pecho.y, pecho.z);
        caerSobre(nivel, pecho, jugadores.get(nivel.getRandom().nextInt(jugadores.size())));
        angulo = Math.atan2(a.getZ() - a.centroArenaMini().z, a.getX() - a.centroArenaMini().x);
        a.avisarMini(nivel, Component.translatable("hud.atalaya.aeralis.chispa_empieza").withStyle(ChatFormatting.LIGHT_PURPLE));
        return true;
    }

    @Override
    int info() {
        int seg = portador != null && vueloT < 0 ? Math.max(1, (revienta - t + 19) / 20) : 0;
        return MinijuegosAeralis.infoChispa(seg, cargada);
    }

    @Override
    @Nullable double[] destino(ServerLevel nivel) {
        // Baja, a tiro de espada, y da vueltas despacio cerca del grupo.
        Vec3 c = a.centroArenaMini();
        angulo += Math.PI * 2 / 800.0;
        return new double[]{c.x + Math.cos(angulo) * 8.0, c.z + Math.sin(angulo) * 8.0, 2.5, 0.25};
    }

    /** La chispa sale de 'desde' y vuela hasta 'quien'. */
    private void caerSobre(ServerLevel nivel, Vec3 desde, Entity quien) {
        vueloDesde = desde;
        vueloA = quien;
        vueloT = t;
        portador = null;
        if (chispa != null) {
            chispa.ponerPortador(null, 0L);
        }
        nivel.playSound(null, desde.x, desde.y, desde.z, AtalayaSonidos.AERALIS_CHISPA_PASA, SoundSource.HOSTILE, 2.0F, 1.0F);
    }

    @Override
    void tick(ServerLevel nivel) {
        jugadores.removeIf(p -> !p.isAlive() || p.isRemoved() || p.isSpectator() || p.isCreative());
        remolinos.removeIf(Entity::isRemoved);
        if (chispa == null || chispa.isRemoved()) {
            return;
        }
        if (siguiente >= 0) {
            if (t >= siguiente && !jugadores.isEmpty()) {
                siguiente = -1;
                Vec3 pecho = a.puntoMundo(AeralisGeometria.NUCLEO);
                chispa.setPos(pecho.x, pecho.y, pecho.z);
                caerSobre(nivel, pecho, jugadores.get(nivel.getRandom().nextInt(jugadores.size())));
            }
            return;
        }
        if (vueloT >= 0) {
            Entity b = vueloA;
            if (b == null || !b.isAlive() || b.isRemoved()) {
                b = jugadores.isEmpty() ? null : jugadores.get(0);
                vueloA = b;
            }
            if (b == null) {
                return;
            }
            float k = Math.min(1.0F, (t - vueloT) / (float) VUELO);
            Vec3 hasta = encima(b);
            Vec3 p = vueloDesde.lerp(hasta, k).add(0, Math.sin(k * Math.PI) * 2.0, 0);
            chispa.setPos(p.x, p.y, p.z);
            nivel.sendParticles(AtalayaParticulas.AERALIS_RAYO, true, true, p.x, p.y, p.z, 1, 0.1, 0.1, 0.1, 0.0);
            if (k >= 1.0F) {
                llega(nivel, b);
            }
            return;
        }
        Entity p = portador;
        if (p == null || !p.isAlive() || p.isRemoved()) {
            // Se ha muerto o se ha ido: cae sobre otro.
            if (!jugadores.isEmpty()) {
                caerSobre(nivel, chispa.position(), jugadores.get(nivel.getRandom().nextInt(jugadores.size())));
            }
            return;
        }
        Vec3 sobre = encima(p);
        chispa.setPos(sobre.x, sobre.y, sobre.z);
        int queda = revienta - t;
        if (queda > 0 && queda % 20 == 0) {
            nivel.playSound(null, sobre.x, sobre.y, sobre.z, AtalayaSonidos.AERALIS_CHISPA_TIC, SoundSource.HOSTILE, 1.5F,
                    cargada ? 1.3F : 1.0F + 0.15F * (3 - queda / 20));
        }
        if (queda <= 0) {
            reventar(nivel, p);
            return;
        }
        // Si se la pasan a un remolino (jugando solo), te la devuelve al llegar (cargada o no).
        if (p instanceof RemolinoChispaEntity && t - llego > 6 && !jugadores.isEmpty()) {
            pase(nivel, p, jugadores.get(0));
        }
    }

    private static Vec3 encima(Entity e) {
        return new Vec3(e.getX(), e.getY() + e.getBbHeight() + ENCIMA, e.getZ());
    }

    /** La chispa llega a alguien: empieza su cuenta. */
    private void llega(ServerLevel nivel, Entity b) {
        vueloT = -1;
        portador = b;
        llego = t;
        revienta = t + (cargada ? CARGADA : CUENTA);
        if (chispa != null) {
            chispa.ponerPortador(b, nivel.getGameTime() + (cargada ? CARGADA : CUENTA));
        }
        Vec3 p = encima(b);
        nivel.playSound(null, p.x, p.y, p.z, AtalayaSonidos.AERALIS_CHISPA_CAE, SoundSource.HOSTILE, 2.0F, 1.0F);
        nivel.sendParticles(AtalayaParticulas.AERALIS_LUZ, true, true, p.x, p.y, p.z, 10, 0.3, 0.3, 0.3, 0.1);
        if (b instanceof Player pl) {
            // Lo grande (la llevas, la cuenta) va arriba en la pantalla; abajo, que hacer.
            pl.sendOverlayMessage(Component.translatable(cargada ? "hud.atalaya.aeralis.chispa_cargada_pista" : "hud.atalaya.aeralis.chispa_pista")
                    .withStyle(cargada ? ChatFormatting.GOLD : ChatFormatting.LIGHT_PURPLE));
        }
    }

    /** De quien la lleva a otro (o a un remolino, o de vuelta). */
    private void pase(ServerLevel nivel, Entity de, Entity a2) {
        boolean deRemolino = de instanceof RemolinoChispaEntity;
        if (!deRemolino) {
            cuenta++;
            if (cuenta >= necesario && !cargada) {
                cargada = true;
                if (chispa != null) {
                    chispa.cargar(true);
                }
                a.sonidoMini(AtalayaSonidos.AERALIS_CHISPA_CARGADA, 5.0F);
                a.avisarMini(nivel, Component.translatable("hud.atalaya.aeralis.chispa_carga_todos").withStyle(ChatFormatting.GOLD));
            }
        }
        caerSobre(nivel, encima(de), a2);
    }

    /** Revienta en las manos: Paralisis y golpe a quien la lleva y a los de al lado; la carga vuelve a cero. */
    private void reventar(ServerLevel nivel, Entity p) {
        Vec3 c = encima(p);
        nivel.playSound(null, c.x, c.y, c.z, AtalayaSonidos.AERALIS_CHISPA_REVIENTA, SoundSource.HOSTILE, 4.0F, 1.0F);
        nivel.sendParticles(AtalayaParticulas.AERALIS_RAYO, true, true, c.x, c.y, c.z, 14, 1.2, 1.0, 1.2, 0.0);
        nivel.sendParticles(AtalayaParticulas.AERALIS_LUZ, true, true, c.x, c.y, c.z, 30, 1.0, 1.0, 1.0, 0.2);
        nivel.sendParticles(AtalayaParticulas.AERALIS_ONDA, true, true, p.getX(), p.getY() + 0.1, p.getZ(), 0, 1.4, REVIENTA * 2, 0.0, 1.0);
        for (LivingEntity v : a.presasMini(nivel, 64)) {
            if (v.distanceToSqr(p) <= REVIENTA * REVIENTA || v == p) {
                a.danoSinMatar(nivel, v, GOLPE);
                a.paralizarMini(v);
            }
        }
        a.avisarMini(nivel, Component.translatable("hud.atalaya.aeralis.chispa_revienta").withStyle(ChatFormatting.RED));
        cuenta = 0;
        cargada = false;
        portador = null;
        if (chispa != null) {
            chispa.cargar(false);
            chispa.ponerPortador(null, 0L);
            chispa.setPos(a.getX(), a.getY() + 30, a.getZ());
        }
        siguiente = t + OTRA;
    }

    /** Alguien pega a algo (AttackEntityCallback): si lleva la chispa, la pasa o se la da a ella. */
    boolean alAtacar(Player p, Entity blanco) {
        if (portador != p || vueloT >= 0 || siguiente >= 0 || !(p.level() instanceof ServerLevel nivel)) {
            return false;
        }
        if (cargada) {
            if (blanco == a || MinijuegosAeralis.apunta(p, a, ALCANCE_ELLA)) {
                aElla(nivel, p);
                return true;
            }
            return false;
        }
        if (blanco instanceof RemolinoChispaEntity || (blanco instanceof LivingEntity v && blanco != a && a.esPresa(v))) {
            pase(nivel, p, blanco);
            return true;
        }
        // Le ha dado a otra cosa (su cuerpo, que vuela al lado): vale si miraba a alguien.
        Entity b = enLaMira(nivel, p);
        if (b != null) {
            pase(nivel, p, b);
            return true;
        }
        return false;
    }

    /** Un clic al aire (MinijuegosAeralis.alBlandir): se la lanza al que mira (o a ella, cargada). */
    void alBlandir(Player p) {
        if (portador != p || vueloT >= 0 || siguiente >= 0 || !(p.level() instanceof ServerLevel nivel)) {
            return;
        }
        if (cargada) {
            if (MinijuegosAeralis.apunta(p, a, ALCANCE_ELLA)) {
                aElla(nivel, p);
            }
            return;
        }
        Entity b = enLaMira(nivel, p);
        if (b != null) {
            pase(nivel, p, b);
        }
    }

    /** A quien se la puede pasar: los companeros (o lo que haya de presa) y los remolinos; el que mas mira. */
    private @Nullable Entity enLaMira(ServerLevel nivel, Player p) {
        List<Entity> candidatos = new ArrayList<>(a.presasMini(nivel, 64));
        candidatos.addAll(remolinos);
        return MinijuegosAeralis.enLaMira(p, candidatos, ALCANCE, PUNTERIA);
    }

    /** ¡A ella! La chispa cargada le revienta en el pecho. */
    private void aElla(ServerLevel nivel, Player p) {
        Vec3 pecho = a.puntoMundo(AeralisGeometria.NUCLEO);
        a.rayoMini(nivel, encima(p), pecho);
        if (chispa != null) {
            chispa.setPos(pecho.x, pecho.y, pecho.z);
            chispa.ponerPortador(null, 0L);
        }
        a.avisarMini(nivel, Component.translatable("hud.atalaya.aeralis.chispa_a_ella", p.getDisplayName()).withStyle(ChatFormatting.GOLD));
        a.acabarMinijuego(nivel, true, true);
    }

    @Override
    boolean alGolpearla(ServerLevel nivel, @Nullable Entity causante, @Nullable Entity directo) {
        // Lo de pegarle con la chispa cargada va por alAtacar (antes del golpe); aqui no hace nada mas.
        return false;
    }

    @Override
    boolean exitoAlAcabar() {
        return false;
    }

    @Override
    void forzarExito(ServerLevel nivel) {
        a.acabarMinijuego(nivel, true, true);
    }

    @Override
    void limpiar(ServerLevel nivel, boolean exito, boolean avisar) {
        if (chispa != null) {
            chispa.soltar();
            chispa.discard();
            chispa = null;
        }
        for (RemolinoChispaEntity r : remolinos) {
            r.soltar();
            r.discard();
        }
        remolinos.clear();
        jugadores.clear();
        portador = null;
    }
}
