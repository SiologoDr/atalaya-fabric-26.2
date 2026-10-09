package com.atalaya.entity;

import com.atalaya.sonido.AtalayaSonidos;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import net.minecraft.ChatFormatting;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.network.chat.Component;
import net.minecraft.network.protocol.game.ClientboundSoundPacket;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;
import org.jspecify.annotations.Nullable;

/**
 * Glifos del Templo (fase III; de la segunda ficha): ruge y salen seis columnas
 * con un glifo cada una. Solo el Vidente (uno al azar) ve en su pantalla
 * cuales son los tres verdaderos; tiene que decirselo a los demas (por voz o
 * por el chat) y entre todos romperlos: tres golpes cada uno. Una falsa estalla
 * al primer golpe y lanza a quien le pego (dano sin matar). Con los tres
 * verdaderos rotos, el templo le castiga: aturdido 6 s. Dura 25 s y mientras,
 * Rajang sigue peleando. Jugando solo, tu ves y tu golpeas.
 */
final class GlifosRajang extends MinijuegoRajang {

    static final int DURA = 500;
    private static final int COLUMNAS = 6;
    private static final double RADIO = 13.0;
    private static final int GOLPES = 3;
    private static final float DANO_FALSO = 6.0F;

    private final List<GlifoTemploEntity> columnas = new ArrayList<>();
    private @Nullable Player vidente;

    GlifosRajang(RajangEntity r) {
        super(r, MinijuegosRajang.GLIFOS, DURA);
    }

    @Override
    boolean empezar(ServerLevel nivel, List<Player> js) {
        if (js.isEmpty()) {
            return false;
        }
        necesario = 3;
        vidente = js.get(r.getRandom().nextInt(js.size()));
        // Seis de los ocho glifos, en orden al azar; los tres primeros son los buenos.
        List<Integer> glifos = new ArrayList<>();
        for (int i = 0; i < MinijuegosRajang.NOMBRES_GLIFOS.length; i++) {
            glifos.add(i);
        }
        Collections.shuffle(glifos, new java.util.Random(r.getRandom().nextLong()));
        List<Integer> elegidos = new ArrayList<>(glifos.subList(0, COLUMNAS));
        int mascara = 0;
        for (int i = 0; i < 3; i++) {
            mascara |= 1 << elegidos.get(i);
        }
        Collections.shuffle(elegidos, new java.util.Random(r.getRandom().nextLong()));
        Vec3 c = r.centroArena();
        double giro = r.getRandom().nextDouble() * Math.PI * 2;
        for (int i = 0; i < COLUMNAS; i++) {
            double a = giro + Math.PI * 2 * i / COLUMNAS;
            double x = c.x + Math.cos(a) * RADIO;
            double z = c.z + Math.sin(a) * RADIO;
            double y = RajangEntity.sueloBajo(nivel, x, c.y + 6, z);
            int glifo = elegidos.get(i);
            // De cara al centro de la plaza.
            float rumbo = (float) (Mth.atan2(c.z - z, c.x - x) * Mth.RAD_TO_DEG) - 90.0F;
            columnas.add(GlifoTemploEntity.alzar(nivel, this, new Vec3(x, y, z), glifo, (mascara & (1 << glifo)) != 0, rumbo));
        }
        r.ponerGlifos(vidente.getId(), mascara);
        nivel.playSound(null, c.x, c.y + 2, c.z, AtalayaSonidos.RAJANG_GLIFO_ALZA, SoundSource.HOSTILE, 6.0F, 1.0F);
        for (Player p : js) {
            if (p == vidente) {
                p.sendOverlayMessage(Component.translatable("hud.atalaya.rajang.glifos_vidente").withStyle(ChatFormatting.GOLD));
            } else {
                p.sendOverlayMessage(Component.translatable("hud.atalaya.rajang.glifos_aviso", vidente.getDisplayName())
                        .withStyle(ChatFormatting.GREEN));
            }
        }
        if (vidente instanceof ServerPlayer sp) {
            // Un aviso solo para el Vidente.
            sp.connection.send(new ClientboundSoundPacket(BuiltInRegistries.SOUND_EVENT.wrapAsHolder(AtalayaSonidos.RAJANG_VIDENTE),
                    SoundSource.HOSTILE, sp.getX(), sp.getEyeY(), sp.getZ(), 1.0F, 1.0F, nivel.getRandom().nextLong()));
        }
        return true;
    }

    @Override
    void tick(ServerLevel nivel) {
        columnas.removeIf(Entity::isRemoved);
        // Si el Vidente se va o muere, lo es otro (el que tenga mas cerca).
        if (vidente == null || !vidente.isAlive() || vidente.isRemoved()) {
            List<Player> js = r.jugadoresMini(nivel, 56);
            if (!js.isEmpty()) {
                vidente = js.get(r.getRandom().nextInt(js.size()));
                r.ponerGlifos(vidente.getId(), r.getGlifosBuenos());
                vidente.sendOverlayMessage(Component.translatable("hud.atalaya.rajang.glifos_vidente").withStyle(ChatFormatting.GOLD));
            }
        }
    }

    @Override
    boolean controlaLibre() {
        // Mientras, pelea como siempre.
        return false;
    }

    /** Un golpe a una columna. */
    void alGolpear(ServerLevel nivel, GlifoTemploEntity g, Player quien) {
        if (r.getMinijuegoEnMarcha() != this) {
            return;
        }
        if (g.esBuena()) {
            if (g.rajar(nivel) >= GOLPES) {
                g.romper(nivel);
                cuenta++;
                if (cuenta >= necesario) {
                    r.acabarMinijuego(nivel, true, true);
                }
            }
            return;
        }
        g.estallar(nivel);
        Vec3 p = g.position();
        for (LivingEntity v : nivel.getEntitiesOfClass(LivingEntity.class, new AABB(p, p).inflate(3.2, 5, 3.2), r::esPresa)) {
            if (RajangEntity.horizontal(p, v.position()) > 3.2) {
                continue;
            }
            Vec3 fuera = RajangEntity.horizontalHacia(p, v.position());
            RajangEntity.lanzar(v, fuera.scale(1.3), 0.75);
            r.danoSinMatar(nivel, v, DANO_FALSO);
        }
    }

    @Override
    void limpiar(ServerLevel nivel, boolean exito, boolean avisar) {
        for (GlifoTemploEntity g : columnas) {
            g.hundir(nivel);
        }
        columnas.clear();
    }

    @Override
    void forzarExito(ServerLevel nivel) {
        for (GlifoTemploEntity g : new ArrayList<>(columnas)) {
            if (g.esBuena() && g.entera()) {
                g.romper(nivel);
            }
        }
        cuenta = necesario;
        r.acabarMinijuego(nivel, true, true);
    }
}
