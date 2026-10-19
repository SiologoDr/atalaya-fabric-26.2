package com.atalaya.momento;

import com.atalaya.particula.AtalayaParticulas;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerLifecycleEvents;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerTickEvents;
import net.minecraft.core.BlockPos;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.util.Mth;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.phys.Vec3;

import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;

/**
 * Lo que los momentos echan al mundo sin ser entidades: los meteoritos (una roca encendida que cae dejando su estela y
 * revienta al tocar el suelo) y los tornados (una columna de viento que vaga y lanza por los aires a quien atrapa). Son
 * solo puntos que mueve el servidor y particulas que ven todos: nada que se guarde, nada que se quede.
 */
public final class EfectosMomento {

    private static final class Meteorito {
        final ServerLevel nivel;
        Vec3 pos;
        final Vec3 vel;
        final float fuerza;

        Meteorito(ServerLevel nivel, Vec3 pos, Vec3 vel, float fuerza) {
            this.nivel = nivel;
            this.pos = pos;
            this.vel = vel;
            this.fuerza = fuerza;
        }
    }

    private static final class Tornado {
        final ServerLevel nivel;
        double x;
        double z;
        double rumbo;
        int vida;

        Tornado(ServerLevel nivel, double x, double z, double rumbo, int vida) {
            this.nivel = nivel;
            this.x = x;
            this.z = z;
            this.rumbo = rumbo;
            this.vida = vida;
        }
    }

    private static final List<Meteorito> METEORITOS = new ArrayList<>();
    private static final List<Tornado> TORNADOS = new ArrayList<>();

    private EfectosMomento() {
    }

    public static void registrar() {
        ServerTickEvents.END_SERVER_TICK.register(EfectosMomento::tick);
        ServerLifecycleEvents.SERVER_STOPPED.register(s -> limpiar());
    }

    static void limpiar() {
        METEORITOS.clear();
        TORNADOS.clear();
    }

    /** Un meteorito que cae desde muy alto hacia ese punto (con su fuerza de explosion). */
    static void meteorito(ServerLevel nivel, double x, double z, float fuerza) {
        RandomSource r = nivel.getRandom();
        double a = r.nextDouble() * Mth.TWO_PI;
        Vec3 destino = new Vec3(x, nivel.getHeight(Heightmap.Types.MOTION_BLOCKING, Mth.floor(x), Mth.floor(z)), z);
        Vec3 desde = destino.add(Math.cos(a) * 40, 90, Math.sin(a) * 40);
        Vec3 vel = destino.subtract(desde).normalize().scale(1.6);
        METEORITOS.add(new Meteorito(nivel, desde, vel, fuerza));
    }

    /** Un tornado que nace cerca de ese jugador y vaga un rato. */
    static void tornado(ServerPlayer p, int ticks) {
        RandomSource r = p.getRandom();
        double a = r.nextDouble() * Mth.TWO_PI;
        double d = 18 + r.nextDouble() * 14;
        TORNADOS.add(new Tornado(p.level(), p.getX() + Math.cos(a) * d, p.getZ() + Math.sin(a) * d, a + Math.PI, ticks));
    }

    static int tornados() {
        return TORNADOS.size();
    }

    static void sinTornados() {
        TORNADOS.clear();
    }

    private static void tick(MinecraftServer s) {
        for (Iterator<Meteorito> it = METEORITOS.iterator(); it.hasNext(); ) {
            Meteorito m = it.next();
            m.pos = m.pos.add(m.vel);
            ServerLevel n = m.nivel;
            n.sendParticles(AtalayaParticulas.NOVILIS_LLAMA, m.pos.x, m.pos.y, m.pos.z, 4, 0.4, 0.4, 0.4, 0.02);
            n.sendParticles(AtalayaParticulas.NOVILIS_HUMO, m.pos.x - m.vel.x, m.pos.y - m.vel.y, m.pos.z - m.vel.z, 2, 0.3, 0.3, 0.3, 0.01);
            BlockPos aqui = BlockPos.containing(m.pos);
            if (!n.isLoaded(aqui) || m.pos.y < n.getMinY()) {
                it.remove();
                continue;
            }
            if (!n.getBlockState(aqui).isAir() || !n.getFluidState(aqui).isEmpty()) {
                n.sendParticles(AtalayaParticulas.MJ_DESTELLO, m.pos.x, m.pos.y + 1, m.pos.z, 0, 3.0 + m.fuerza, 0, 3, 1.0);
                n.sendParticles(AtalayaParticulas.NOVILIS_ROCA, m.pos.x, m.pos.y + 0.5, m.pos.z, 20, 0.6, 0.4, 0.6, 0.35);
                n.explode(null, m.pos.x, m.pos.y, m.pos.z, m.fuerza, true, Level.ExplosionInteraction.MOB);
                it.remove();
            }
        }
        for (Iterator<Tornado> it = TORNADOS.iterator(); it.hasNext(); ) {
            Tornado t = it.next();
            if (--t.vida <= 0) {
                it.remove();
                continue;
            }
            ServerLevel n = t.nivel;
            RandomSource r = n.getRandom();
            t.rumbo += (r.nextDouble() - 0.5) * 0.25;
            t.x += Math.cos(t.rumbo) * 0.22;
            t.z += Math.sin(t.rumbo) * 0.22;
            int suelo = n.getHeight(Heightmap.Types.MOTION_BLOCKING, Mth.floor(t.x), Mth.floor(t.z));
            // La columna: un cono de viento que se ensancha hacia arriba y gira.
            if (n.getGameTime() % 2 == 0) {
                for (int i = 0; i < 9; i++) {
                    double h = i * 2.2;
                    double radio = 0.6 + h * 0.18;
                    double ang = n.getGameTime() * 0.5 + i * 1.3;
                    n.sendParticles(AtalayaParticulas.AERALIS_REMOLINO, t.x + Math.cos(ang) * radio, suelo + h, t.z + Math.sin(ang) * radio,
                            0, -Math.sin(ang) * 0.3, 0.12, Math.cos(ang) * 0.3, 1.0);
                }
                n.sendParticles(AtalayaParticulas.MJ_POLVO, t.x, suelo + 0.3, t.z, 3, 1.2, 0.1, 1.2, 0.05);
            }
            // Lanza por los aires a quien atrapa.
            for (ServerPlayer p : n.players()) {
                if (!Suceso.cuenta(p)) {
                    continue;
                }
                double dx = p.getX() - t.x;
                double dz = p.getZ() - t.z;
                if (dx * dx + dz * dz < 6.25 && p.getY() < suelo + 18 && p.getY() > suelo - 2) {
                    p.setDeltaMovement(-dz * 0.25 + (r.nextDouble() - 0.5) * 0.4, 1.6 + r.nextDouble() * 0.5, dx * 0.25 + (r.nextDouble() - 0.5) * 0.4);
                    p.hurtMarked = true;
                }
            }
        }
    }
}
