package com.atalaya.client;

import com.atalaya.entity.NereaEntity;
import com.atalaya.entity.NereaGeometria;
import com.atalaya.particula.AtalayaParticulas;
import net.minecraft.client.Minecraft;
import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.phys.Vec3;

import java.util.Map;
import java.util.WeakHashMap;

/**
 * Lo que Nerea provoca alrededor y que el servidor no necesita saber: el suelo
 * que retumba con cada pisada (y el polvo que levanta), el temblor sostenido
 * mientras gira las cadenas o remueve el agua, los rugidos que meten miedo y
 * la mirada que oscurece la pantalla de quien la recibe.
 *
 * Se calcula cada tick con el estado sincronizado de cada Nerea cercana: en
 * que estado esta y cuantos ticks lleva en el. Los golpes con onda expansiva
 * (tridente, burbujas, sellos) los dispara la particula de la onda.
 */
public final class NereaEfectosCliente {

    /** Lo que avanza la animacion de andar entre pisada y pisada (2,8 = factor de NereaModel). */
    private static final float PASO = 2000.0F / (50.0F * 2.8F) / 2.0F;

    private static final Map<NereaEntity, Float> ULTIMO_PASO = new WeakHashMap<>();

    private NereaEfectosCliente() {
    }

    public static void tick(Minecraft mc) {
        ClientLevel nivel = mc.level;
        if (nivel == null || mc.player == null || mc.isPaused()) {
            return;
        }
        for (Entity e : nivel.entitiesForRendering()) {
            if (e instanceof NereaEntity n && n.distanceToSqr(mc.player) < 80 * 80) {
                procesar(nivel, n, mc);
            }
        }
        NereaPresencia.tick();
    }

    private static void procesar(ClientLevel nivel, NereaEntity n, Minecraft mc) {
        double x = n.getX();
        double y = n.getY();
        double z = n.getZ();
        if (n.isDeadOrDying()) {
            int d = n.deathTime;
            if (d == 6) {
                NereaPresencia.asustar(x, y, z, 0.7F, 40);
                NereaPresencia.sacudir(x, y, z, 1.2F, 40);
            }
            if (d == 46) {
                NereaPresencia.sacudir(x, y, z, 2.0F, 36);
            }
            return;
        }
        int estado = n.getEstado();
        // Ticks de animacion: con el ritmo de la fase, como el servidor.
        int t = (int) ((n.tickCount - n.inicioEstado) * n.ritmoCliente);
        switch (estado) {
            case NereaEntity.DESPERTAR -> {
                if (t < 30) {
                    NereaPresencia.retumbar(x, y, z, 0.35F, 40);
                }
                if (t == 40) {
                    NereaPresencia.sacudir(x, y, z, 2.6F, 48);
                    NereaPresencia.asustar(x, y, z, 0.9F, 44);
                }
            }
            case NereaEntity.REMOLINO -> {
                if (t >= NereaGeometria.REMOLINO_TIRA && t < NereaGeometria.REMOLINO_SUELTA) {
                    NereaPresencia.retumbar(x, y, z, 0.45F, 36);
                    remolinoGigante(nivel, n, t, mc);
                }
            }
            case NereaEntity.MOLINO -> {
                if (t >= NereaGeometria.MOLINO_GOLPEA && t <= NereaGeometria.MOLINO_PARA) {
                    NereaPresencia.retumbar(x, y, z, 0.9F, 30);
                }
            }
            case NereaEntity.MIRADA -> {
                if (t == 2) {
                    NereaPresencia.sacudir(x, y, z, 1.4F, 40);
                    NereaPresencia.asustar(x, y, z, 0.55F, 40);
                }
                if (t >= NereaGeometria.MIRADA_FIJA && n.getIdObjetivo() == mc.player.getId()) {
                    // A quien mira: la pantalla se cierra a medida que carga.
                    float k = (float) (t - NereaGeometria.MIRADA_FIJA) / (NereaGeometria.DURACION_MIRADA - NereaGeometria.MIRADA_FIJA);
                    Vec3 p = mc.player.position();
                    NereaPresencia.asustar(p.x, p.y, p.z, 0.35F + 0.6F * k, 1000);
                    NereaPresencia.retumbar(p.x, p.y, p.z, 0.12F + 0.35F * k, 1000);
                }
            }
            case NereaEntity.TAMBALEO -> {
                if (t == 1) {
                    NereaPresencia.sacudir(x, y, z, 2.2F, 44);
                }
                if (t == 42) {
                    NereaPresencia.sacudir(x, y, z, 1.6F, 44);
                    NereaPresencia.asustar(x, y, z, 0.6F, 40);
                }
            }
            case NereaEntity.AGOTADO -> {
                if (t == 12) {
                    NereaPresencia.sacudir(x, y, z, 1.8F, 32);
                    polvo(nivel, n, 0.0, 0.0, 14, 1.8);
                }
            }
            default -> {
            }
        }
        pisadas(nivel, n);
    }

    /**
     * El gran remolino: brazos de agua en espiral que cubren todo su radio
     * de arrastre y giran hacia ella, mas rapido cuanto mas cerca. Lo dibuja
     * cada cliente solo alrededor de su jugador (lo de lejos no se veria).
     */
    private static void remolinoGigante(ClientLevel nivel, NereaEntity n, int t, Minecraft mc) {
        double cx = n.getX();
        double cy = n.getY() + 0.2;
        double cz = n.getZ();
        Vec3 yo = mc.player.position();
        // Entra creciendo desde el centro durante el primer segundo.
        double alcance = NereaEntity.RADIO_REMOLINO * Math.min(1.0, (t - NereaGeometria.REMOLINO_TIRA + 1) / 20.0);
        double giro = n.tickCount * 0.16;
        for (int brazo = 0; brazo < 6; brazo++) {
            double base = giro + brazo * Math.PI / 3.0;
            for (double r = 3.5; r < alcance; r += 1.8) {
                double a = base + Math.log(r) * 2.4;
                double px = cx + Math.cos(a) * r + (n.getRandom().nextDouble() - 0.5) * 0.8;
                double pz = cz + Math.sin(a) * r + (n.getRandom().nextDouble() - 0.5) * 0.8;
                double dx = px - yo.x;
                double dz = pz - yo.z;
                if (dx * dx + dz * dz > 36 * 36) {
                    continue;
                }
                double tang = 0.22 + 3.5 / r;
                double vx = -Math.sin(a) * tang - Math.cos(a) * 0.1;
                double vz = Math.cos(a) * tang - Math.sin(a) * 0.1;
                boolean cresta = n.getRandom().nextInt(3) == 0;
                nivel.addParticle(cresta ? AtalayaParticulas.NEREA_OLA : AtalayaParticulas.NEREA_ESPUMA,
                        px, cy, pz, vx, 0.01, vz);
                if (n.getRandom().nextInt(6) == 0) {
                    nivel.addParticle(AtalayaParticulas.NEREA_GOTA, px, cy + 0.2, pz, vx * 0.5, 0.15, vz * 0.5);
                }
            }
        }
        // El ojo del remolino: el agua se hunde en espiral a sus pies.
        for (int k = 0; k < 3; k++) {
            double a = giro * 2.0 + k * Math.PI * 2 / 3;
            nivel.addParticle(AtalayaParticulas.NEREA_REMOLINO, cx + Math.cos(a) * 2.5, cy, cz + Math.sin(a) * 2.5, 0.0, 0.0, 0.0);
        }
    }

    /** Cada pisada retumba y levanta polvo bajo el pie que apoya. */
    private static void pisadas(ClientLevel nivel, NereaEntity n) {
        float pos = n.walkAnimation.position();
        Float antes = ULTIMO_PASO.put(n, pos);
        if (antes == null || n.walkAnimation.speed() < 0.08F) {
            return;
        }
        int pasoAntes = (int) Math.floor(antes / PASO);
        int pasoAhora = (int) Math.floor(pos / PASO);
        if (pasoAhora == pasoAntes) {
            return;
        }
        boolean izquierdo = (pasoAhora & 1) == 0;
        NereaPresencia.sacudir(n.getX(), n.getY(), n.getZ(), 0.7F, 24);
        polvo(nivel, n, izquierdo ? 0.6 : -0.6, -0.9, 7, 0.5);
    }

    private static void polvo(ClientLevel nivel, NereaEntity n, double izq, double frente, int cuantos, double abre) {
        Vec3 c = NereaEntity.puntoMundo(new Vec3(izq, 0.1, frente), n.position(), n.yBodyRot);
        for (int i = 0; i < cuantos; i++) {
            double a = n.getRandom().nextDouble() * Math.PI * 2;
            double v = 0.04 + n.getRandom().nextDouble() * 0.06;
            nivel.addParticle(AtalayaParticulas.NEREA_POLVO, c.x + Math.cos(a) * abre * 0.5, c.y, c.z + Math.sin(a) * abre * 0.5,
                    Math.cos(a) * v, 0.02, Math.sin(a) * v);
        }
    }
}
