package com.atalaya.entity;

import com.atalaya.particula.AtalayaParticulas;
import com.atalaya.sonido.AtalayaSonidos;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.UUID;
import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.Mth;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;

/**
 * Suelo que se Hunde (fase IV; de la segunda ficha): ruge y la plaza a su
 * alrededor se vuelve losas de jade, en alto sobre un foso de pinchos. Juega
 * un tercio de los que pelean (al azar; al menos uno): suben a las losas y los
 * demas, si estaban debajo, salen del anillo a mirar. Cada losa que se pisa se
 * agrieta y cae al segundo: hay que no parar y no volver por donde ya se ha
 * pasado. Mientras, el, inmune en medio, sostiene la plaza (sin piedras que
 * caigan: Juan, 09-10-2026). Quien cae, o se tira, de las losas muere salvo
 * totem (Juan: "si se tiran de las plataformas popean totem, y si se caen a los
 * pinchos igual, pero si siguen y se termina el tiempo se salvan"). Dura 15 s:
 * si aguanta mas de la mitad, se queda sin aliento (aturdido 6 s). El anillo es
 * grande porque se juega con unos 60 (Juan): de 7 a 36 bloques de el.
 */
final class SueloRajang extends MinijuegoRajang {

    /** Lo que tardan en subir todas las losas (ticks) y lo que dura despues. */
    static final int SUBE = 40;
    static final int DURA = SUBE + 300;
    /** Lo alto que suben (bloques) y el anillo de losas: de 'DENTRO' a 'FUERA' de el. */
    private static final double ALTO = 3.0;
    private static final double DENTRO = 7.0;
    private static final double FUERA = 36.0;
    /** Hasta donde busca a quien juega y a quien sacar de debajo. */
    private static final double ALCANCE = 64.0;

    private final List<LosaJadeEntity> losas = new ArrayList<>();
    /** Las losas por su casilla de la rejilla (para saber cual pisa cada uno sin preguntar a cada losa). */
    private final Map<Long, LosaJadeEntity> rejilla = new HashMap<>();
    /** Los que juegan (un tercio) y los que ya han caido. */
    private final Set<UUID> elegidos = new HashSet<>();
    private final Set<UUID> caidos = new HashSet<>();
    private Vec3 c = Vec3.ZERO;
    private double origenX;
    private double origenZ;
    private double arriba;

    SueloRajang(RajangEntity r) {
        super(r, MinijuegosRajang.SUELO, DURA);
    }

    private static long casilla(int i, int k) {
        return ((long) i << 32) ^ (k & 0xFFFFFFFFL);
    }

    @Override
    boolean empezar(ServerLevel nivel, List<Player> js) {
        List<Player> todos = r.jugadoresMini(nivel, ALCANCE);
        if (todos.isEmpty()) {
            return false;
        }
        c = r.position();
        arriba = Math.floor(r.getY()) + ALTO;
        double lado = LosaJadeEntity.LADO;
        origenX = Math.floor(c.x) - lado / 2;
        origenZ = Math.floor(c.z) - lado / 2;
        int n = (int) Math.ceil(FUERA / lado) + 1;
        for (int i = -n; i <= n; i++) {
            for (int k = -n; k <= n; k++) {
                double x = origenX + i * lado + lado / 2;
                double z = origenZ + k * lado + lado / 2;
                double d = RajangEntity.horizontal(c, new Vec3(x, 0, z));
                if (d < DENTRO || d > FUERA) {
                    continue;
                }
                // Que haya sitio arriba (sin tierra ni ramas) y suelo debajo, no mas alto que el foso.
                double m = lado / 2 - 0.05;
                AABB hueco = new AABB(x - m, arriba - LosaJadeEntity.GRUESO, z - m, x + m, arriba + 2.0, z + m);
                if (!nivel.noCollision(hueco)) {
                    continue;
                }
                double suelo = RajangEntity.sueloBajo(nivel, x, arriba - LosaJadeEntity.GRUESO, z);
                if (suelo > arriba - 1.5) {
                    continue;
                }
                // Suben en ondas, de dentro afuera.
                int retraso = (int) ((d - DENTRO) / (FUERA - DENTRO) * (SUBE - LosaJadeEntity.SUBE));
                LosaJadeEntity l = LosaJadeEntity.alzar(nivel, r, x, arriba, z, suelo, retraso);
                losas.add(l);
                rejilla.put(casilla(i, k), l);
            }
        }
        if (losas.size() < 8) {
            for (LosaJadeEntity l : losas) {
                l.discard();
            }
            losas.clear();
            rejilla.clear();
            return false;
        }
        // Un tercio, al azar (al menos uno; jugando solo, tu).
        List<Player> mezcla = new ArrayList<>(todos);
        Collections.shuffle(mezcla, new java.util.Random(r.getRandom().nextLong()));
        int cuantos = Math.max(1, (mezcla.size() + 2) / 3);
        for (int i = 0; i < cuantos; i++) {
            elegidos.add(mezcla.get(i).getUUID());
        }
        necesario = cuantos;
        for (Player p : todos) {
            p.sendOverlayMessage(elegidos.contains(p.getUUID())
                    ? Component.translatable("hud.atalaya.rajang.suelo_aviso").withStyle(ChatFormatting.GREEN)
                    : Component.translatable("hud.atalaya.rajang.suelo_mira").withStyle(ChatFormatting.GRAY));
        }
        nivel.playSound(null, c.x, c.y + 2, c.z, AtalayaSonidos.RAJANG_SUELO_ALZA, SoundSource.HOSTILE, 8.0F, 1.0F);
        nivel.sendParticles(AtalayaParticulas.RAJANG_ONDA, true, true, c.x, c.y + 0.1, c.z, 0, 2.4, FUERA, 0.0, 1.0);
        return true;
    }

    @Override
    void tick(ServerLevel nivel) {
        losas.removeIf(Entity::isRemoved);
        if (t == SUBE) {
            subir(nivel);
        }
        if (t <= SUBE) {
            return;
        }
        for (Player p : r.jugadoresMini(nivel, ALCANCE)) {
            UUID u = p.getUUID();
            pisar(nivel, p);
            // Quien juega y baja de las losas (cae o se tira): muerte, salvo totem.
            if (elegidos.contains(u) && !caidos.contains(u) && p.getY() < arriba - 1.6) {
                caidos.add(u);
                cuenta = caidos.size();
                nivel.playSound(null, p.getX(), p.getY(), p.getZ(), AtalayaSonidos.RAJANG_PINCHOS, SoundSource.HOSTILE, 2.0F, 1.0F);
                nivel.sendParticles(AtalayaParticulas.RAJANG_JADE, true, true, p.getX(), p.getY() + 0.3, p.getZ(), 14, 0.4, 0.2, 0.4, 0.15);
                p.sendOverlayMessage(Component.translatable("hud.atalaya.rajang.suelo_caes").withStyle(ChatFormatting.RED));
                p.hurtServer(nivel, RajangDanos.fuente(nivel, RajangDanos.FOSO, r, r), RajangEntity.MORTAL);
                r.lastrar(p, 60);
            }
        }
    }

    /** Las losas que tiene bajo los pies (puede estar entre dos o cuatro): se agrietan. */
    private void pisar(ServerLevel nivel, Player p) {
        if (p.isSpectator() || !p.onGround() || p.getY() < arriba - 0.2 || p.getY() > arriba + 0.6) {
            return;
        }
        AABB caja = p.getBoundingBox();
        double lado = LosaJadeEntity.LADO;
        for (double x : new double[]{caja.minX + 0.05, caja.maxX - 0.05}) {
            for (double z : new double[]{caja.minZ + 0.05, caja.maxZ - 0.05}) {
                LosaJadeEntity l = rejilla.get(casilla(Mth.floor((x - origenX) / lado), Mth.floor((z - origenZ) / lado)));
                if (l != null && !l.isRemoved()) {
                    l.pisar(nivel);
                }
            }
        }
    }

    /** Los elegidos, arriba (cada uno en una losa, separados); los demas, si estaban dentro del anillo, fuera. */
    private void subir(ServerLevel nivel) {
        List<LosaJadeEntity> libres = new ArrayList<>();
        for (LosaJadeEntity l : losas) {
            if (l.firme()) {
                libres.add(l);
            }
        }
        if (libres.isEmpty()) {
            return;
        }
        Collections.shuffle(libres, new java.util.Random(r.getRandom().nextLong()));
        List<LosaJadeEntity> usadas = new ArrayList<>();
        for (Player p : r.jugadoresMini(nivel, ALCANCE)) {
            if (!elegidos.contains(p.getUUID())) {
                sacar(nivel, p);
                continue;
            }
            LosaJadeEntity l = lejosDe(libres, usadas);
            usadas.add(l);
            Vec3 q = l.arriba();
            p.teleportTo(q.x, q.y + 0.05, q.z);
            p.resetFallDistance();
            nivel.sendParticles(AtalayaParticulas.RAJANG_POLVO, true, true, q.x, q.y + 0.4, q.z, 10, 0.4, 0.3, 0.4, 0.03);
        }
    }

    /** Una losa libre lejos de las ya dadas (que no empiecen pegados). */
    private static LosaJadeEntity lejosDe(List<LosaJadeEntity> libres, List<LosaJadeEntity> usadas) {
        for (LosaJadeEntity l : libres) {
            if (usadas.contains(l)) {
                continue;
            }
            boolean lejos = true;
            for (LosaJadeEntity u : usadas) {
                if (RajangEntity.horizontal(l.position(), u.position()) < 6.0) {
                    lejos = false;
                    break;
                }
            }
            if (lejos) {
                return l;
            }
        }
        for (LosaJadeEntity l : libres) {
            if (!usadas.contains(l)) {
                return l;
            }
        }
        return libres.get(usadas.size() % libres.size());
    }

    /** Uno que no juega y estaba debajo del anillo (o en medio, junto a el): fuera, a mirar. */
    private void sacar(ServerLevel nivel, Player p) {
        double d = RajangEntity.horizontal(c, p.position());
        if (d > FUERA + 2.0) {
            return;
        }
        Vec3 fuera = RajangEntity.horizontalHacia(c, p.position());
        if (fuera.lengthSqr() < 1.0E-4) {
            fuera = new Vec3(1, 0, 0);
        }
        double x = c.x + fuera.x * (FUERA + 4.0);
        double z = c.z + fuera.z * (FUERA + 4.0);
        p.teleportTo(x, RajangEntity.sueloBajo(nivel, x, arriba + 4, z) + 0.05, z);
        p.resetFallDistance();
    }

    /** Sale bien si aguanta arriba mas de la mitad de los que juegan (Juan, 09-10-2026). */
    @Override
    boolean exitoAlAcabar() {
        int quedan = elegidos.size() - caidos.size();
        return !elegidos.isEmpty() && quedan * 2 > elegidos.size();
    }

    @Override
    boolean inmune() {
        return true;
    }

    @Override
    void limpiar(ServerLevel nivel, boolean exito, boolean avisar) {
        for (LosaJadeEntity l : losas) {
            l.caer(nivel, false);
        }
        losas.clear();
        rejilla.clear();
        // Los que aguantaron se salvan: bajan planeando.
        for (Player p : r.jugadoresMini(nivel, ALCANCE)) {
            if (elegidos.contains(p.getUUID()) && p.getY() > arriba - 1.6) {
                p.addEffect(new MobEffectInstance(MobEffects.SLOW_FALLING, 80, 0, false, false, true));
            }
        }
        nivel.playSound(null, c.x, c.y + 2, c.z, AtalayaSonidos.RAJANG_LOSA_CAE, SoundSource.HOSTILE, 6.0F, 0.7F);
    }

    @Override
    void forzarExito(ServerLevel nivel) {
        caidos.clear();
        if (elegidos.isEmpty()) {
            for (Player p : r.jugadoresMini(nivel, ALCANCE)) {
                elegidos.add(p.getUUID());
            }
        }
        r.acabarMinijuego(nivel, true, true);
    }
}
