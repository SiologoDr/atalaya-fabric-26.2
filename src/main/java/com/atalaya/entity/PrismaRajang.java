package com.atalaya.entity;

import com.atalaya.item.AtalayaItems;
import com.atalaya.particula.AtalayaParticulas;
import com.atalaya.sonido.AtalayaSonidos;
import java.util.ArrayList;
import java.util.List;
import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.ClipContext;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;
import org.jspecify.annotations.Nullable;

/**
 * El Rayo del Prisma (fase I; Juan lo eligio de la cuarta ficha): como un gato
 * con un puntero, Rajang no puede evitar saltar sobre el punto de luz del
 * Prisma de Jade. A uno le cae el prisma del cielo; manteniendo el clic
 * derecho pinta la luz donde mira (hasta 30 bloques) y Rajang salta sobre ella
 * cada poco. En la plaza salen tres trampas de oro: cada una en la que cae le
 * muerde (un 2 % de su vida) y con las tres queda aturdido 6 s. El prisma se
 * pasa con la Q (sale lanzado hacia donde se mira). Si la luz cae sobre un
 * companero, Rajang le cae encima (golpe fuerte, sin matar). No mata.
 */
final class PrismaRajang extends MinijuegoRajang {

    static final int DURA = 500;
    static final double ALCANCE = 30.0;
    private static final double RADIO_TRAMPAS = 13.0;
    /** Lo que le muerde cada trampa (de su vida maxima): la mitad que al principio (Juan, 09-10-2026). */
    private static final float MUERDE = 0.02F;
    /** Lo que espera entre un salto y el siguiente, ya en el suelo (ticks). */
    private static final int ENTRE_SALTOS = 8;

    private final List<TrampaOroEntity> trampas = new ArrayList<>();
    private @Nullable LuzPrismaEntity luz;
    /** Donde esta la luz (null: apagada) y quien la pinta. */
    private @Nullable Vec3 punto;
    private @Nullable Player usando;
    private @Nullable Player portador;
    private @Nullable Player portadorAntes;
    private @Nullable Player avisado;
    private int lanzado = -1;
    private int sinPrisma;
    private int espera = 20;

    PrismaRajang(RajangEntity r) {
        super(r, MinijuegosRajang.PRISMA, DURA);
    }

    @Override
    boolean empezar(ServerLevel nivel, List<Player> js) {
        if (js.isEmpty()) {
            return false;
        }
        necesario = 3;
        Vec3 c = r.centroArena();
        double giro = r.getRandom().nextDouble() * Math.PI * 2;
        for (int i = 0; i < 3; i++) {
            double a = giro + Math.PI * 2 * i / 3;
            double x = c.x + Math.cos(a) * RADIO_TRAMPAS;
            double z = c.z + Math.sin(a) * RADIO_TRAMPAS;
            trampas.add(TrampaOroEntity.abrir(nivel, r, new Vec3(x, RajangEntity.sueloBajo(nivel, x, c.y + 6, z), z)));
        }
        luz = LuzPrismaEntity.crear(nivel, r, r.position());
        r.avisarMini(nivel, Component.translatable("hud.atalaya.rajang.prisma_aviso").withStyle(ChatFormatting.GREEN));
        darPrisma(nivel, js.get(r.getRandom().nextInt(js.size())));
        return true;
    }

    /** Le cae el prisma del cielo: una estela de luz que baja hasta sus manos. */
    private void darPrisma(ServerLevel nivel, Player p) {
        MinijuegosRajang.dar(p, MinijuegosRajang.crear(r, AtalayaItems.PRISMA_JADE));
        for (int k = 0; k < 14; k++) {
            nivel.sendParticles(AtalayaParticulas.RAJANG_CHISPA, true, true, p.getX(), p.getY() + 2.2 + k * 0.8, p.getZ(), 2,
                    0.08, 0.2, 0.08, 0.0);
        }
        nivel.sendParticles(AtalayaParticulas.RAJANG_ORO, true, true, p.getX(), p.getY() + 1.4, p.getZ(), 16, 0.3, 0.4, 0.3, 0.05);
        nivel.playSound(null, p.getX(), p.getY() + 1, p.getZ(), AtalayaSonidos.RAJANG_PRISMA_CAE, SoundSource.HOSTILE, 2.0F, 1.0F);
    }

    private static boolean esPrisma(ItemStack s) {
        return s.is(AtalayaItems.PRISMA_JADE);
    }

    @Override
    void tick(ServerLevel nivel) {
        trampas.removeIf(Entity::isRemoved);
        // Quien lleva el prisma y si lo esta usando.
        portador = null;
        usando = null;
        for (Player p : r.jugadoresMini(nivel, 80)) {
            boolean lleva = false;
            for (InteractionHand mano : InteractionHand.values()) {
                ItemStack s = p.getItemInHand(mano);
                if (esPrisma(s) && MinijuegosRajang.vivo(s, MinijuegosRajang.PRISMA)) {
                    lleva = true;
                }
            }
            if (!lleva) {
                for (int i = 0; i < p.getInventory().getContainerSize(); i++) {
                    ItemStack s = p.getInventory().getItem(i);
                    if (esPrisma(s) && MinijuegosRajang.vivo(s, MinijuegosRajang.PRISMA)) {
                        lleva = true;
                        break;
                    }
                }
            }
            if (lleva) {
                portador = p;
                if (p.isUsingItem() && esPrisma(p.getUseItem())) {
                    usando = p;
                }
                break;
            }
        }
        ItemEntity suelo = portador == null ? MinijuegosRajang.enSuelo(nivel, r, AtalayaItems.PRISMA_JADE) : null;
        // Con la Q sale lanzado hacia donde mira, para pasarselo a otro.
        if (portador == null && suelo != null && portadorAntes != null && suelo.getId() != lanzado && suelo.tickCount <= 2) {
            lanzado = suelo.getId();
            Vec3 mira = portadorAntes.getLookAngle();
            Vec3 h = new Vec3(mira.x, 0, mira.z);
            h = h.lengthSqr() < 1.0E-4 ? Vec3.directionFromRotation(0, portadorAntes.getYRot()) : h.normalize();
            suelo.setDeltaMovement(h.x * 0.6, 0.32 + Math.max(0.0, mira.y) * 0.3, h.z * 0.6);
            suelo.setPickUpDelay(8);
            suelo.setGlowingTag(true);
            nivel.playSound(null, portadorAntes.getX(), portadorAntes.getEyeY(), portadorAntes.getZ(), AtalayaSonidos.RAJANG_PRISMA_LUZ,
                    SoundSource.PLAYERS, 1.0F, 1.6F);
        }
        portadorAntes = portador;
        if (portador != null && portador != avisado) {
            avisado = portador;
            portador.sendOverlayMessage(Component.translatable("hud.atalaya.rajang.prisma_tienes", Component.keybind("key.use"),
                    Component.keybind("key.drop")).withStyle(ChatFormatting.GREEN));
        }
        if (suelo != null && t % 3 == 0) {
            nivel.sendParticles(AtalayaParticulas.RAJANG_CHISPA, true, true, suelo.getX(), suelo.getY() + 0.5 + r.getRandom().nextDouble() * 4,
                    suelo.getZ(), 2, 0.06, 0.3, 0.06, 0.0);
        }
        // Nadie lo tiene y no esta en el suelo (lo han guardado o se ha perdido): le cae a otro.
        if (portador == null && suelo == null) {
            if (++sinPrisma > 30) {
                sinPrisma = 0;
                List<Player> js = r.jugadoresMini(nivel, 48);
                if (!js.isEmpty()) {
                    darPrisma(nivel, js.get(r.getRandom().nextInt(js.size())));
                }
            }
        } else {
            sinPrisma = 0;
        }
        // La luz: donde mira quien lo usa (contra el suelo o una pared; al cielo, nada).
        Vec3 antes = punto;
        punto = null;
        if (usando != null) {
            Vec3 ojo = usando.getEyePosition();
            BlockHitResult hit = nivel.clip(new ClipContext(ojo, ojo.add(usando.getLookAngle().scale(ALCANCE)), ClipContext.Block.COLLIDER,
                    ClipContext.Fluid.NONE, usando));
            if (hit.getType() == HitResult.Type.BLOCK) {
                Vec3 h = hit.getLocation();
                Vec3 q = r.dentroArena(new Vec3(h.x, h.y, h.z));
                punto = new Vec3(q.x, RajangEntity.sueloBajo(nivel, q.x, h.y + 0.6, q.z), q.z);
            }
        }
        if (luz != null && !luz.isRemoved()) {
            luz.encender(punto != null ? usando : null, punto != null ? punto : luz.position());
        }
        if (punto != null && antes == null && usando != null) {
            nivel.playSound(null, usando.getX(), usando.getEyeY(), usando.getZ(), AtalayaSonidos.RAJANG_PRISMA_LUZ, SoundSource.PLAYERS,
                    0.8F, 1.0F);
        }
        if (espera > 0) {
            espera--;
        }
    }

    @Override
    void libre(ServerLevel nivel) {
        r.quietoMini();
        if (punto != null) {
            // Hipnotizado: no le quita ojo a la luz y, en cuanto puede, salta.
            r.girarMini(punto, 25.0F);
            if (espera <= 0) {
                espera = ENTRE_SALTOS;
                r.saltarMini(nivel, punto, null);
            }
        } else if (portador != null) {
            r.girarMini(portador.position(), 6.0F);
        }
    }

    @Override
    @Nullable Vec3 destinoSalto() {
        return punto;
    }

    @Override
    void alAterrizar(ServerLevel nivel, Vec3 donde, @Nullable Vec3 destino) {
        for (TrampaOroEntity tr : trampas) {
            // Es enorme: vale que caigan en ella sus zarpas o el sitio de la luz al que saltaba.
            double d = RajangEntity.horizontal(donde, tr.position());
            if (destino != null) {
                d = Math.min(d, RajangEntity.horizontal(destino, tr.position()));
            }
            if (tr.usada() || tr.cierra() >= 0 || d > TrampaOroEntity.CAE_DENTRO) {
                continue;
            }
            tr.usar(nivel);
            cuenta++;
            r.morderMini(nivel, MUERDE);
            if (cuenta >= necesario) {
                r.acabarMinijuego(nivel, true, true);
            }
            return;
        }
    }

    @Override
    void limpiar(ServerLevel nivel, boolean exito, boolean avisar) {
        for (TrampaOroEntity tr : trampas) {
            tr.cerrar();
        }
        trampas.clear();
        if (luz != null) {
            luz.discard();
            luz = null;
        }
    }

    @Override
    void forzarExito(ServerLevel nivel) {
        for (TrampaOroEntity tr : new ArrayList<>(trampas)) {
            if (!tr.usada()) {
                tr.usar(nivel);
            }
        }
        cuenta = necesario;
        r.acabarMinijuego(nivel, true, true);
    }
}
