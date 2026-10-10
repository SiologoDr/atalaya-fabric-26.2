package com.atalaya.entity;

import com.atalaya.particula.AtalayaParticulas;
import com.atalaya.sonido.AtalayaSonidos;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.phys.Vec3;

/**
 * La Forja del Juramento (fase I): clava la espada y salen yunques con una
 * hoja al rojo (uno jugando solo, dos con dos o tres, y si no, tres). Sobre
 * cada hoja se cierra un aro de luz: hay que golpearla cuando el aro la toca.
 * Cada hoja pide 6 golpes buenos (YunqueForjaEntity). Mientras, el no se mueve
 * ni le entra nada, y cada 5 s alza la espada contra los herreros: el rayo del
 * Castigo bajo cada uno (sin la onda). Dura 25 s.
 *
 * Con todas las hojas forjadas, salen volando hacia el y le parten la
 * armadura: aturdido 6 s. Si no, las que quedan revientan en chispas y queman
 * a quien este al lado.
 */
final class ForjaNovilis extends MinijuegoNovilis {

    static final int DURA = 500;
    /** A cuanto de el salen los yunques. */
    private static final double RADIO = 12.0;
    /** El rayo contra los herreros: el primero y luego cada cuanto. */
    private static final int RAYO_PRIMERO = 70;
    private static final int RAYO_CADA = 100;
    /** Quien esta a menos de esto de un yunque sin forjar es un herrero. */
    private static final double HERRERO = 6.0;
    /** Lo que tardan las hojas en llegarle volando. */
    private static final int VUELO = 20;
    private static final float CHISPAS = 4.0F;
    private static final float REVIENTA = 10.0F;

    private final List<YunqueForjaEntity> yunques = new ArrayList<>();
    private final List<Player> jugadores = new ArrayList<>();
    /** Cuando salieron volando las hojas (-1: aun no). */
    private int vuelan = -1;

    ForjaNovilis(NovilisEntity n) {
        super(n, MinijuegosNovilis.FORJA, DURA);
    }

    @Override
    boolean empezar(ServerLevel nivel, List<Player> js) {
        if (js.isEmpty()) {
            return false;
        }
        jugadores.addAll(js);
        int cuantos = js.size() <= 1 ? 1 : js.size() <= 3 ? 2 : 3;
        Vec3 c = n.position();
        double giro = nivel.getRandom().nextDouble() * Math.PI * 2;
        for (int i = 0; i < cuantos; i++) {
            double a = giro + Math.PI * 2 * i / cuantos;
            Vec3 p = n.dentroArenaMini(new Vec3(c.x + Math.cos(a) * RADIO, c.y, c.z + Math.sin(a) * RADIO));
            Vec3 donde = NovilisEntity.sueloBajo(nivel, p);
            // De lado a el: la hoja de traves, y el aro se ve desde el corro.
            float rumbo = (float) (Math.atan2(c.z - donde.z, c.x - donde.x) * 180.0 / Math.PI) - 90.0F;
            yunques.add(YunqueForjaEntity.alzar(nivel, this, donde, rumbo));
        }
        necesario = cuantos * YunqueForjaEntity.GOLPES;
        nivel.playSound(null, n.getX(), n.getY() + 2, n.getZ(), AtalayaSonidos.NOVILIS_FORJA_SALE, SoundSource.HOSTILE, 6.0F, 1.0F);
        n.avisarMini(nivel, Component.translatable("hud.atalaya.novilis.forja_empieza").withStyle(ChatFormatting.GOLD));
        return true;
    }

    @Override
    void tick(ServerLevel nivel) {
        jugadores.removeIf(p -> !p.isAlive() || p.isRemoved());
        int hechos = 0;
        boolean todas = !yunques.isEmpty();
        for (YunqueForjaEntity y : yunques) {
            hechos += Math.min(YunqueForjaEntity.GOLPES, y.getGolpes());
            todas &= y.forjada();
        }
        cuenta = hechos;
        if (vuelan >= 0) {
            volando(nivel);
            return;
        }
        if (todas) {
            // Las hojas salen volando hacia el.
            vuelan = t;
            for (YunqueForjaEntity y : yunques) {
                y.volar();
            }
            nivel.playSound(null, n.getX(), n.getY() + 6, n.getZ(), AtalayaSonidos.NOVILIS_FORJA_VUELAN, SoundSource.HOSTILE, 6.0F, 1.0F);
            return;
        }
        if (t >= RAYO_PRIMERO && (t - RAYO_PRIMERO) % RAYO_CADA == 0 && t < dura - 40) {
            n.castigoMini(nivel, herreros(nivel));
        }
    }

    /** Las hojas van hacia su pecho (una estela de oro) y, al llegar, se le parte la armadura. */
    private void volando(ServerLevel nivel) {
        int k = t - vuelan;
        Vec3 pecho = n.pechoMini();
        float f = Math.min(1.0F, k / (float) VUELO);
        for (YunqueForjaEntity y : yunques) {
            Vec3 a = y.position().add(0, YunqueForjaEntity.ALTO_HOJA, 0);
            Vec3 p = a.lerp(pecho, f).add(0, Math.sin(f * Math.PI) * 4.0, 0);
            nivel.sendParticles(AtalayaParticulas.NOVILIS_LUZ, true, true, p.x, p.y, p.z, 4, 0.2, 0.2, 0.2, 0.02);
            nivel.sendParticles(AtalayaParticulas.NOVILIS_CHISPA, true, true, p.x, p.y, p.z, 2, 0.1, 0.1, 0.1, 0.1);
        }
        if (k >= VUELO) {
            nivel.sendParticles(AtalayaParticulas.NOVILIS_LUZ, true, true, pecho.x, pecho.y, pecho.z, 60, 1.5, 2.0, 1.5, 0.2);
            nivel.sendParticles(AtalayaParticulas.NOVILIS_CHISPA, true, true, pecho.x, pecho.y, pecho.z, 50, 1.5, 2.0, 1.5, 0.4);
            n.acabarMinijuego(nivel, true, true);
        }
    }

    /** Los que estan junto a un yunque sin forjar; si no hay, un tercio al azar. */
    private List<LivingEntity> herreros(ServerLevel nivel) {
        List<LivingEntity> out = new ArrayList<>();
        for (LivingEntity v : n.presasMini(nivel, 56)) {
            for (YunqueForjaEntity y : yunques) {
                if (!y.forjada() && v.distanceToSqr(y) < HERRERO * HERRERO) {
                    out.add(v);
                    break;
                }
            }
        }
        if (out.isEmpty()) {
            List<LivingEntity> todos = n.presasMini(nivel, 48);
            Collections.shuffle(todos, new java.util.Random(nivel.getRandom().nextLong()));
            out.addAll(todos.subList(0, Math.min(todos.size(), Math.max(1, (todos.size() + 2) / 3))));
        }
        return out;
    }

    /** Un golpe bueno (o perfecto). */
    void alAcertar(ServerLevel nivel, YunqueForjaEntity y, Player p, boolean perfecto) {
        p.sendOverlayMessage(Component.translatable(perfecto ? "hud.atalaya.novilis.forja_perfecto" : "hud.atalaya.novilis.forja_bien",
                y.getGolpes(), YunqueForjaEntity.GOLPES).withStyle(ChatFormatting.GOLD));
    }

    /** Un golpe a destiempo: saltan chispas y queman al que golpea. */
    void alFallar(ServerLevel nivel, YunqueForjaEntity y, Player p) {
        p.sendOverlayMessage(Component.translatable("hud.atalaya.novilis.forja_mal").withStyle(ChatFormatting.RED));
        n.quemarMini(nivel, p, CHISPAS, 1);
    }

    @Override
    boolean exitoAlAcabar() {
        return vuelan >= 0;
    }

    @Override
    void forzarExito(ServerLevel nivel) {
        n.acabarMinijuego(nivel, true, true);
    }

    @Override
    void limpiar(ServerLevel nivel, boolean exito, boolean avisar) {
        for (YunqueForjaEntity y : yunques) {
            if (!exito && avisar && !y.forjada()) {
                // Las que quedan revientan en chispas.
                Vec3 h = y.position().add(0, YunqueForjaEntity.ALTO_HOJA, 0);
                nivel.sendParticles(AtalayaParticulas.NOVILIS_CHISPA, true, true, h.x, h.y, h.z, 40, 0.8, 0.4, 0.8, 0.4);
                nivel.sendParticles(AtalayaParticulas.NOVILIS_LLAMA, true, true, h.x, h.y, h.z, 20, 1.0, 0.4, 1.0, 0.08);
                nivel.playSound(null, h.x, h.y, h.z, AtalayaSonidos.NOVILIS_FORJA_MAL, SoundSource.HOSTILE, 3.0F, 0.6F);
                for (LivingEntity v : n.presasMini(nivel, 64)) {
                    if (v.distanceToSqr(y) < 16.0) {
                        n.quemarMini(nivel, v, REVIENTA, 1);
                    }
                }
            }
            y.hundir();
        }
        yunques.clear();
        jugadores.clear();
    }
}
