package com.atalaya.entity;

import com.atalaya.item.AtalayaItems;
import com.atalaya.particula.AtalayaParticulas;
import com.atalaya.sonido.AtalayaSonidos;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.projectile.Projectile;
import net.minecraft.world.phys.Vec3;
import org.jspecify.annotations.Nullable;

/**
 * Pararrayos (fase IV): a un tercio de los que pelean (minimo uno) les da un
 * pararrayos. Con la tormenta marca circulos donde va a caer un rayo (de cuatro
 * a diez segun cuantos sean; jugando solo, uno): el primero de cada tanda cerca
 * de cada uno de los que llevan pararrayos, los demas sobre cualquiera. Quien
 * este dentro con el pararrayos en la mano se lleva el rayo sin dano y queda
 * cargado (el pararrayos se enciende): tiene 5 s para descargarlo en ella,
 * mirandola y dando un clic (a 24 bloques), pegandole o disparandole. Cada
 * descarga le quita un 2 % de vida. Si cae sin pararrayos, revienta el suelo
 * en 5 bloques (golpe que no mata). Con tres descargas cae aturdida 6 s. Dura
 * 30 s; mientras vuela bajo y no le entra nada mas.
 *
 * Afinado el 10-10-2026: la descarga era solo con la mano y, volando a 2,5
 * bloques, costaba llegarle; ahora basta con mirarla. Y las tandas, cada 5 s.
 */
final class PararrayosAeralis extends MinijuegoAeralis {

    static final int DURA = 600;
    static final int DESCARGAS = 3;
    /** Lo que le quita cada descarga (de su vida maxima). */
    static final float PARTE = 0.02F;
    /** Cada cuanto marca otra tanda, cuanto tarda en caer y lo que dura la carga. */
    private static final int TANDA = 100;
    private static final int CUENTA = 60;
    static final int CARGA = 100;
    private static final double ESTALLA = 5.0;
    private static final float GOLPE = 8.0F;
    /** Hasta donde llega la descarga mirandola (es enorme y vuela en circulo: que no haya que perseguirla). */
    private static final double ALCANCE = 24.0;

    private final List<Player> jugadores = new ArrayList<>();
    private final List<CirculoRayoEntity> circulos = new ArrayList<>();
    /** Los cargados y los ticks que les quedan. */
    private final Map<UUID, Integer> cargados = new HashMap<>();
    private double angulo;

    PararrayosAeralis(AeralisEntity a) {
        super(a, MinijuegosAeralis.PARARRAYOS, DURA);
    }

    @Override
    boolean empezar(ServerLevel nivel, List<Player> js) {
        if (js.isEmpty()) {
            return false;
        }
        jugadores.addAll(js);
        List<Player> todos = new ArrayList<>(js);
        Collections.shuffle(todos, new java.util.Random(nivel.getRandom().nextLong()));
        int n = Math.max(1, (todos.size() + 2) / 3);
        for (int i = 0; i < n; i++) {
            Player p = todos.get(i);
            MinijuegosAeralis.dar(p, MinijuegosAeralis.crear(a, AtalayaItems.PARARRAYOS_TORMENTA));
            p.sendOverlayMessage(Component.translatable("hud.atalaya.aeralis.pararrayos_tienes").withStyle(ChatFormatting.LIGHT_PURPLE));
            nivel.sendParticles(AtalayaParticulas.AERALIS_RAYO, true, true, p.getX(), p.getY() + 2.0, p.getZ(), 4, 0.4, 0.4, 0.4, 0.0);
        }
        necesario = DESCARGAS;
        angulo = Math.atan2(a.getZ() - a.centroArenaMini().z, a.getX() - a.centroArenaMini().x);
        a.avisarMini(nivel, Component.translatable("hud.atalaya.aeralis.pararrayos_empieza", n).withStyle(ChatFormatting.LIGHT_PURPLE));
        return true;
    }

    @Override
    @Nullable double[] destino(ServerLevel nivel) {
        // Baja, a tiro de espada, y da vueltas despacio alrededor del centro.
        Vec3 c = a.centroArenaMini();
        angulo += Math.PI * 2 / 900.0;
        return new double[]{c.x + Math.cos(angulo) * 9.0, c.z + Math.sin(angulo) * 9.0, 2.5, 0.25};
    }

    @Override
    void tick(ServerLevel nivel) {
        jugadores.removeIf(p -> !p.isAlive() || p.isRemoved() || p.isSpectator() || p.isCreative());
        circulos.removeIf(Entity::isRemoved);
        if (t % TANDA == 20 && t < dura - CUENTA - 10) {
            tanda(nivel);
        }
        // Los cargados: brillan, se les cuenta y, si no descargan a tiempo, se les va.
        Iterator<Map.Entry<UUID, Integer>> it = cargados.entrySet().iterator();
        while (it.hasNext()) {
            Map.Entry<UUID, Integer> e = it.next();
            Player p = nivel.getPlayerByUUID(e.getKey());
            int queda = e.getValue() - 1;
            if (p == null || !p.isAlive() || queda <= 0) {
                if (p != null) {
                    nivel.sendParticles(AtalayaParticulas.AERALIS_ESCAMA, true, true, p.getX(), p.getY() + 1.0, p.getZ(), 12, 0.4, 0.6, 0.4, 0.05);
                    p.sendOverlayMessage(Component.translatable("hud.atalaya.aeralis.pararrayos_se_va").withStyle(ChatFormatting.GRAY));
                    MinijuegosAeralis.marcarCarga(p, a, AtalayaItems.PARARRAYOS_TORMENTA, 0L);
                }
                it.remove();
                continue;
            }
            e.setValue(queda);
            if (t % 3 == 0) {
                nivel.sendParticles(AtalayaParticulas.AERALIS_RAYO, true, true, p.getX(), p.getY() + 1.0, p.getZ(), 1, 0.4, 0.6, 0.4, 0.0);
            }
            if (queda % 20 == 0) {
                p.sendOverlayMessage(Component.translatable("hud.atalaya.aeralis.pararrayos_cargado", (queda + 19) / 20)
                        .withStyle(ChatFormatting.LIGHT_PURPLE));
            }
        }
    }

    /**
     * Una tanda de circulos: primero uno cerca de cada uno de los que llevan
     * pararrayos (a dos o cuatro pasos: hay que ir), luego sobre cualquiera (un
     * poco desplazados: hay que apartarse o que llegue uno con pararrayos).
     */
    private void tanda(ServerLevel nivel) {
        if (jugadores.isEmpty()) {
            return;
        }
        int n = jugadores.size() <= 1 ? 1 : Math.min(10, 3 + jugadores.size() / 6);
        java.util.Random azar = new java.util.Random(nivel.getRandom().nextLong());
        List<Player> con = new ArrayList<>();
        List<Player> sin = new ArrayList<>();
        for (Player p : jugadores) {
            if (MinijuegosAeralis.tiene(p, a, AtalayaItems.PARARRAYOS_TORMENTA)) {
                con.add(p);
            } else {
                sin.add(p);
            }
        }
        Collections.shuffle(con, azar);
        Collections.shuffle(sin, azar);
        List<Player> todos = new ArrayList<>(con);
        todos.addAll(sin);
        for (int i = 0; i < n; i++) {
            Player p = todos.get(i % todos.size());
            double ang = nivel.getRandom().nextDouble() * Math.PI * 2;
            double r = i < con.size() ? 2.0 + nivel.getRandom().nextDouble() * 2.0 : 1.5 + nivel.getRandom().nextDouble() * 4.0;
            double x = p.getX() + Math.cos(ang) * r;
            double z = p.getZ() + Math.sin(ang) * r;
            double y = AeralisEntity.sueloBajo(nivel, x, p.getY() + 3, z);
            circulos.add(CirculoRayoEntity.poner(nivel, this, new Vec3(x, y, z), CUENTA));
        }
    }

    /** Cae el rayo de un circulo. */
    void alCaer(ServerLevel nivel, CirculoRayoEntity c) {
        Player conPararrayos = null;
        for (Player p : jugadores) {
            if (c.dentro(p) && MinijuegosAeralis.enMano(p, a, AtalayaItems.PARARRAYOS_TORMENTA)) {
                conPararrayos = p;
                break;
            }
        }
        if (conPararrayos != null) {
            cargados.put(conPararrayos.getUUID(), CARGA);
            MinijuegosAeralis.marcarCarga(conPararrayos, a, AtalayaItems.PARARRAYOS_TORMENTA, nivel.getGameTime() + CARGA);
            nivel.playSound(null, c.getX(), c.getY(), c.getZ(), AtalayaSonidos.AERALIS_PARARRAYOS_RAYO, SoundSource.HOSTILE, 4.0F, 1.0F);
            nivel.sendParticles(AtalayaParticulas.AERALIS_LUZ, true, true, conPararrayos.getX(), conPararrayos.getY() + 1.5,
                    conPararrayos.getZ(), 30, 0.4, 0.8, 0.4, 0.1);
            conPararrayos.sendOverlayMessage(Component.translatable("hud.atalaya.aeralis.pararrayos_cargado", CARGA / 20)
                    .withStyle(ChatFormatting.LIGHT_PURPLE));
            return;
        }
        // Sin pararrayos: revienta el suelo.
        nivel.playSound(null, c.getX(), c.getY(), c.getZ(), AtalayaSonidos.AERALIS_PARARRAYOS_ESTALLA, SoundSource.HOSTILE, 4.0F, 1.0F);
        nivel.sendParticles(AtalayaParticulas.AERALIS_ONDA, true, true, c.getX(), c.getY() + 0.1, c.getZ(), 0, 1.6, ESTALLA * 1.6, 0.0, 1.0);
        nivel.sendParticles(AtalayaParticulas.AERALIS_POLVO, true, true, c.getX(), c.getY() + 0.3, c.getZ(), 20, 1.6, 0.4, 1.6, 0.08);
        for (LivingEntity v : a.presasMini(nivel, 64)) {
            if (Math.hypot(v.getX() - c.getX(), v.getZ() - c.getZ()) <= ESTALLA && Math.abs(v.getY() - c.getY()) < 4.0) {
                a.danoSinMatar(nivel, v, GOLPE);
                Vec3 fuera = new Vec3(v.getX() - c.getX(), 0, v.getZ() - c.getZ());
                fuera = fuera.lengthSqr() < 1.0E-4 ? new Vec3(1, 0, 0) : fuera.normalize();
                v.setDeltaMovement(fuera.x * 0.9, 0.45, fuera.z * 0.9);
                v.hurtMarked = true;
            }
        }
    }

    @Override
    boolean alGolpearla(ServerLevel nivel, @Nullable Entity causante, @Nullable Entity directo) {
        if (!(causante instanceof Player p) || !cargados.containsKey(p.getUUID())) {
            return false;
        }
        // La descarga: con la mano o con lo que dispare.
        if (directo != p && !(directo instanceof Projectile)) {
            return false;
        }
        descargar(nivel, p);
        return true;
    }

    /** Un clic (MinijuegosAeralis.alBlandir): si esta cargado y la mira, descarga. */
    void alBlandir(Player p) {
        if (cargados.containsKey(p.getUUID()) && p.level() instanceof ServerLevel nivel && MinijuegosAeralis.apunta(p, a, ALCANCE)) {
            descargar(nivel, p);
        }
    }

    /** La descarga: el rayo va de su pararrayos al pecho de Aeralis y le quita un 2 %. */
    private void descargar(ServerLevel nivel, Player p) {
        cargados.remove(p.getUUID());
        MinijuegosAeralis.marcarCarga(p, a, AtalayaItems.PARARRAYOS_TORMENTA, 0L);
        cuenta++;
        Vec3 pecho = a.puntoMundo(AeralisGeometria.NUCLEO);
        a.rayoMini(nivel, p.position().add(0, 1.2, 0), pecho);
        a.morderMini(nivel, PARTE);
        a.sonidoMini(AtalayaSonidos.AERALIS_PARARRAYOS_DESCARGA, 6.0F);
        a.avisarMini(nivel, Component.translatable("hud.atalaya.aeralis.pararrayos_descarga", p.getDisplayName(), cuenta, DESCARGAS)
                .withStyle(ChatFormatting.GOLD));
        if (cuenta >= DESCARGAS) {
            a.acabarMinijuego(nivel, true, true);
        }
    }

    @Override
    boolean exitoAlAcabar() {
        return cuenta >= DESCARGAS;
    }

    @Override
    void forzarExito(ServerLevel nivel) {
        cuenta = DESCARGAS;
        a.acabarMinijuego(nivel, true, true);
    }

    @Override
    void limpiar(ServerLevel nivel, boolean exito, boolean avisar) {
        for (CirculoRayoEntity c : circulos) {
            c.soltar();
            c.discard();
        }
        circulos.clear();
        cargados.clear();
        jugadores.clear();
    }
}
