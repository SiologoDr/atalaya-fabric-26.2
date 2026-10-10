package com.atalaya.entity;

import com.atalaya.sonido.AtalayaSonidos;
import java.util.ArrayList;
import java.util.List;
import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.phys.Vec3;

/**
 * Frio o Caliente (fase IV): clava la espada y entierra sus brasas bajo el
 * suelo del altar (dos jugando solo, tres con un grupo y una mas por cada ocho
 * jugadores pasados los ocho, hasta ocho). A cada uno le sale un termometro
 * (TermometroHud): frio, templado, caliente, ¡ardiendo! Con "¡ardiendo!",
 * golpear el suelo saca la brasa (BrasaEnterradaEntity). Dura 30 s y mientras
 * el sigue peleando (y le entra el dano).
 *
 * Todas fuera: se le apaga el pecho, aturdido 6 s. Si no, las que quedan
 * revientan en lava donde estaban.
 */
final class CalienteNovilis extends MinijuegoNovilis {

    static final int DURA = 600;
    /** Donde se entierran: entre estos radios del centro del altar, y apartadas entre si y de el. */
    private static final double DESDE = 8.0;
    private static final double HASTA = 26.0;
    private static final double APARTE = 8.0;
    private static final double DE_EL = 6.0;

    private final List<BrasaEnterradaEntity> brasas = new ArrayList<>();
    private boolean hecho;

    CalienteNovilis(NovilisEntity n) {
        super(n, MinijuegosNovilis.CALIENTE, DURA);
    }

    /** Cuantas brasas entierra para tantos jugadores. */
    static int cuantas(int jugadores) {
        if (jugadores <= 1) {
            return 2;
        }
        return Math.min(8, 3 + Math.max(0, jugadores - 8) / 8);
    }

    @Override
    boolean empezar(ServerLevel nivel, List<Player> js) {
        if (js.isEmpty()) {
            return false;
        }
        int cuantas = cuantas(js.size());
        Vec3 c = n.centroArenaMini();
        List<Vec3> puestas = new ArrayList<>();
        for (int intento = 0; intento < 200 && puestas.size() < cuantas; intento++) {
            double a = nivel.getRandom().nextDouble() * Math.PI * 2;
            double r = DESDE + nivel.getRandom().nextDouble() * (HASTA - DESDE);
            Vec3 p = new Vec3(c.x + Math.cos(a) * r, c.y, c.z + Math.sin(a) * r);
            if (Math.hypot(p.x - n.getX(), p.z - n.getZ()) < DE_EL) {
                continue;
            }
            boolean junta = false;
            for (Vec3 q : puestas) {
                if (Math.hypot(p.x - q.x, p.z - q.z) < (intento < 150 ? APARTE : APARTE / 2)) {
                    junta = true;
                    break;
                }
            }
            if (!junta) {
                puestas.add(p);
            }
        }
        for (Vec3 p : puestas) {
            brasas.add(BrasaEnterradaEntity.enterrar(nivel, this, NovilisEntity.sueloBajo(nivel, p)));
        }
        if (brasas.isEmpty()) {
            return false;
        }
        necesario = brasas.size();
        nivel.playSound(null, n.getX(), n.getY() + 2, n.getZ(), AtalayaSonidos.NOVILIS_CALIENTE_ENTIERRA, SoundSource.HOSTILE, 7.0F, 1.0F);
        n.avisarMini(nivel, Component.translatable("hud.atalaya.novilis.caliente_empieza", brasas.size()).withStyle(ChatFormatting.GOLD));
        return true;
    }

    @Override
    void tick(ServerLevel nivel) {
        int halladas = 0;
        for (BrasaEnterradaEntity b : brasas) {
            if (b.getHallada() >= 0) {
                halladas++;
            }
        }
        cuenta = halladas;
        if (!hecho && halladas >= necesario) {
            hecho = true;
            n.acabarMinijuego(nivel, true, true);
        }
    }

    /** Alguien ha sacado una. */
    void alHallar(ServerLevel nivel, BrasaEnterradaEntity b, Player p) {
        int halladas = 0;
        for (BrasaEnterradaEntity o : brasas) {
            if (o.getHallada() >= 0) {
                halladas++;
            }
        }
        n.avisarMini(nivel, Component.translatable("hud.atalaya.novilis.caliente_hallada", p.getDisplayName(), halladas, necesario)
                .withStyle(ChatFormatting.GOLD));
    }

    @Override
    boolean controlaLibre() {
        return false;
    }

    @Override
    boolean inmune() {
        return false;
    }

    @Override
    boolean exitoAlAcabar() {
        return cuenta >= necesario;
    }

    @Override
    void forzarExito(ServerLevel nivel) {
        hecho = true;
        n.acabarMinijuego(nivel, true, true);
    }

    @Override
    void limpiar(ServerLevel nivel, boolean exito, boolean avisar) {
        for (BrasaEnterradaEntity b : brasas) {
            if (!exito && avisar && b.enterrada()) {
                b.reventar(nivel, n);
            } else if (b.enterrada()) {
                b.discard();
            }
            b.soltar();
        }
        brasas.clear();
    }
}
