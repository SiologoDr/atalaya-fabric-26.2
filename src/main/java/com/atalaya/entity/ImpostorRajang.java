package com.atalaya.entity;

import com.atalaya.mixin.ManiquiAccessor;
import com.atalaya.particula.AtalayaParticulas;
import com.atalaya.sonido.AtalayaSonidos;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import net.minecraft.ChatFormatting;
import net.minecraft.core.component.DataComponents;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.Mth;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntitySpawnReason;
import net.minecraft.world.entity.EntityTypes;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.decoration.Mannequin;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.component.ResolvableProfile;
import net.minecraft.world.phys.Vec3;
import org.jspecify.annotations.Nullable;

/**
 * El Impostor de Jade (fase II; Juan, 09-10-2026: "que agarre la forma que
 * tiene ahorita una persona, su armadura, skin, nombre arriba, todo igual, y
 * que por 1 s se muestre en sus pasos unas huellas de jade sutiles pero un
 * poco visibles"). Ruge, se envuelve en polvo de jade y desaparece: ahora es
 * una copia de uno de los jugadores (un maniqui de vanilla con su cara, su
 * nombre, su armadura y lo que lleva en las manos) que anda entre el grupo.
 * La pista: cada pocos segundos, durante uno, deja huellas de zarpa de jade
 * al andar. Pegarle al falso le hace volver a su forma de golpe (aturdido
 * 6 s). Si no le pillan en 20 s, reaparece y salta sobre el jugador que
 * copio (golpe fuerte, sin matar).
 *
 * Con poca gente la copia se esconde entre copias de mentira (jugando solo,
 * tres tuyas y una es el): pegarle a una de mentira la deshace en arenilla
 * de jade y te empuja.
 */
final class ImpostorRajang extends MinijuegoRajang {

    static final int DURA = 400;
    /** La etiqueta de las copias: no son presa de nadie y no se quedan en el mundo. */
    static final String ETIQUETA = "atalaya_impostor";
    /** Cada cuanto deja huellas y cuanto (ticks): un segundo de cada cuatro. */
    private static final int HUELLAS_CADA = 80;
    private static final int HUELLAS_DURAN = 20;
    private static final double PASO = 0.7;
    /** Lo que vive cada huella (ticks) y lo que mide. */
    private static final double HUELLA_VIDA = 30.0;
    private static final double HUELLA_TAM = 0.42;
    private static final float DANO_SENUELO = 4.0F;

    /** Cada copia viva, por su UUID, con su juego (para el golpe, que llega por un evento). */
    private static final Map<UUID, ImpostorRajang> COPIAS = new ConcurrentHashMap<>();

    private static final class Copia {
        final Mannequin m;
        final boolean real;
        @Nullable Vec3 meta;
        int espera;
        int pasos;
        Vec3 ultimaHuella;
        boolean izquierda;

        Copia(Mannequin m, boolean real) {
            this.m = m;
            this.real = real;
            this.ultimaHuella = m.position();
        }
    }

    private final List<Copia> copias = new ArrayList<>();
    private @Nullable Player copiado;
    private Vec3 escondite = Vec3.ZERO;
    private boolean descubierto;

    ImpostorRajang(RajangEntity r) {
        super(r, MinijuegosRajang.IMPOSTOR, DURA);
    }

    @Override
    boolean empezar(ServerLevel nivel, List<Player> js) {
        if (js.isEmpty()) {
            return false;
        }
        necesario = 1;
        escondite = r.position();
        copiado = js.get(r.getRandom().nextInt(js.size()));
        // Se envuelve en polvo de jade: una nube que tapa por donde se va.
        Vec3 c = r.puntoMundo(RajangGeometria.PECHO);
        nivel.sendParticles(AtalayaParticulas.RAJANG_POLVO, true, true, c.x, c.y - 2, c.z, 120, 4.0, 3.0, 5.0, 0.05);
        nivel.sendParticles(AtalayaParticulas.RAJANG_JADE, true, true, c.x, c.y, c.z, 60, 3.0, 2.5, 4.0, 0.2);
        nivel.sendParticles(AtalayaParticulas.RAJANG_CHISPA, true, true, c.x, c.y, c.z, 50, 3.0, 2.5, 4.0, 0.1);
        nivel.playSound(null, c.x, c.y, c.z, AtalayaSonidos.RAJANG_IMPOSTOR_DISFRAZ, SoundSource.HOSTILE, 6.0F, 1.0F);
        // El de verdad y, con poca gente, las de mentira (jugando solo, dos; con dos, una).
        int senuelos = js.size() == 1 ? 2 : js.size() == 2 ? 1 : 0;
        copias.add(crear(nivel, copiado, true, js));
        for (int i = 0; i < senuelos; i++) {
            copias.add(crear(nivel, js.get(r.getRandom().nextInt(js.size())), false, js));
        }
        r.avisarMini(nivel, Component.translatable("hud.atalaya.rajang.impostor_aviso").withStyle(ChatFormatting.GREEN));
        return true;
    }

    /** Una copia de p, entre el grupo (cerca de alguien, pero no encima). */
    private Copia crear(ServerLevel nivel, Player p, boolean real, List<Player> js) {
        Player junto = js.get(r.getRandom().nextInt(js.size()));
        double a = r.getRandom().nextDouble() * Math.PI * 2;
        double d = 3.0 + r.getRandom().nextDouble() * 4.0;
        Vec3 q = r.dentroArena(junto.position().add(Math.cos(a) * d, 0, Math.sin(a) * d));
        double y = RajangEntity.sueloBajo(nivel, q.x, junto.getY() + 2, q.z);
        Mannequin m = EntityTypes.MANNEQUIN.create(nivel, EntitySpawnReason.EVENT);
        m.setComponent(DataComponents.PROFILE, ResolvableProfile.createResolved(p.getGameProfile()));
        ((ManiquiAccessor) m).atalaya$ocultarDescripcion(true);
        m.setCustomName(p.getDisplayName());
        m.setCustomNameVisible(true);
        for (EquipmentSlot ranura : EquipmentSlot.values()) {
            if (ranura.getType() == EquipmentSlot.Type.HUMANOID_ARMOR || ranura.getType() == EquipmentSlot.Type.HAND) {
                m.setItemSlot(ranura, p.getItemBySlot(ranura).copy());
            }
        }
        m.setMainArm(p.getMainArm());
        m.addTag(ETIQUETA);
        if (real) {
            // Para las pruebas (un selector puede encontrarlo); en el juego no se ve.
            m.addTag(ETIQUETA + "_real");
        }
        float rumbo = r.getRandom().nextFloat() * 360.0F;
        m.snapTo(q.x, y, q.z, rumbo, 0.0F);
        m.setYHeadRot(rumbo);
        m.yBodyRot = rumbo;
        // Apuntada antes de entrar en el mundo: al entrar salta alCargar, que quita las que no lo esten.
        COPIAS.put(m.getUUID(), this);
        nivel.addFreshEntity(m);
        nivel.sendParticles(AtalayaParticulas.RAJANG_POLVO, true, true, q.x, y + 1.0, q.z, 14, 0.4, 0.6, 0.4, 0.02);
        return new Copia(m, real);
    }

    @Override
    void tick(ServerLevel nivel) {
        List<Player> js = r.jugadoresMini(nivel, 56);
        for (Copia c : new ArrayList<>(copias)) {
            if (c.m.isRemoved()) {
                copias.remove(c);
                COPIAS.remove(c.m.getUUID());
                if (c.real && !descubierto) {
                    // Se ha ido sin que nadie le pegue (lo han quitado): se acabo.
                    r.acabarMinijuego(nivel, false, true);
                    return;
                }
                continue;
            }
            andar(c, js);
            if (c.real) {
                huellas(nivel, c);
            }
        }
    }

    /** Anda como uno mas: de uno a otro del grupo, a paso de jugador, y a ratos se para a mirar. */
    private void andar(Copia c, List<Player> js) {
        Mannequin m = c.m;
        // Si se ha ido muy lejos (o se ha caido), vuelve con el grupo.
        Vec3 casa = r.centroArena();
        if (RajangEntity.horizontal(m.position(), casa) > 44 || m.getY() < casa.y - 12) {
            Player p = js.isEmpty() ? null : js.get(r.getRandom().nextInt(js.size()));
            Vec3 q = p != null ? p.position().add(2, 0, 2) : casa;
            m.teleportTo(q.x, q.y, q.z);
            c.meta = null;
        }
        if (c.espera > 0) {
            c.espera--;
            m.zza = 0.0F;
            Player mira = null;
            double mejor = 1.0E9;
            for (Player p : js) {
                double d = p.distanceToSqr(m);
                if (d < mejor) {
                    mejor = d;
                    mira = p;
                }
            }
            if (mira != null) {
                girar(m, mira.position(), 8.0F);
            }
            return;
        }
        if (c.meta == null || RajangEntity.horizontal(m.position(), c.meta) < 1.2 || ++c.pasos > 140) {
            c.pasos = 0;
            if (!js.isEmpty()) {
                Player p = js.get(r.getRandom().nextInt(js.size()));
                double a = r.getRandom().nextDouble() * Math.PI * 2;
                double d = 2.5 + r.getRandom().nextDouble() * 4.0;
                c.meta = r.dentroArena(p.position().add(Math.cos(a) * d, 0, Math.sin(a) * d));
            } else {
                c.meta = casa;
            }
            if (r.getRandom().nextFloat() < 0.35F) {
                c.espera = 10 + r.getRandom().nextInt(30);
                return;
            }
        }
        girar(m, c.meta, 20.0F);
        m.zza = 1.0F;
        m.setSpeed(0.1F);
        m.setJumping(m.horizontalCollision && m.onGround());
    }

    private static void girar(Mannequin m, Vec3 hacia, float paso) {
        float quiere = (float) (Mth.atan2(hacia.z - m.getZ(), hacia.x - m.getX()) * Mth.RAD_TO_DEG) - 90.0F;
        float rumbo = Mth.approachDegrees(m.getYRot(), quiere, paso);
        m.setYRot(rumbo);
        m.yBodyRot = rumbo;
        m.setYHeadRot(rumbo);
    }

    /** Un segundo de cada cuatro: huellas de zarpa de jade a cada paso, que se apagan enseguida. */
    private void huellas(ServerLevel nivel, Copia c) {
        Mannequin m = c.m;
        boolean toca = (t + 30) % HUELLAS_CADA < HUELLAS_DURAN;
        if (!toca || !m.onGround()) {
            c.ultimaHuella = m.position();
            return;
        }
        if (RajangEntity.horizontal(m.position(), c.ultimaHuella) < PASO) {
            return;
        }
        c.ultimaHuella = m.position();
        c.izquierda = !c.izquierda;
        float rumbo = m.yBodyRot * Mth.DEG_TO_RAD;
        double lado = c.izquierda ? 0.17 : -0.17;
        double x = m.getX() + Math.cos(rumbo) * lado;
        double z = m.getZ() + Math.sin(rumbo) * lado;
        // La huella mira hacia donde anda (la particula gira lo que se le pase en la Z).
        nivel.sendParticles(AtalayaParticulas.RAJANG_HUELLA, true, true, x, m.getY() + 0.02, z, 0, HUELLA_TAM, HUELLA_VIDA,
                -rumbo, 1.0);
    }

    @Override
    boolean inmune() {
        return true;
    }

    /**
     * Le han pegado a una copia: si es el, vuelve a su forma de golpe; si es de
     * mentira, se deshace en arenilla y empuja a quien le pego.
     */
    private void golpeada(ServerLevel nivel, Mannequin m, @Nullable Entity quien) {
        Copia c = null;
        for (Copia x : copias) {
            if (x.m == m) {
                c = x;
            }
        }
        if (c == null || descubierto) {
            return;
        }
        if (c.real) {
            descubierto = true;
            cuenta = 1;
            r.acabarMinijuego(nivel, true, true);
            return;
        }
        copias.remove(c);
        COPIAS.remove(m.getUUID());
        Vec3 p = m.position();
        nivel.sendParticles(AtalayaParticulas.RAJANG_JADE, true, true, p.x, p.y + 1.0, p.z, 30, 0.3, 0.6, 0.3, 0.15);
        nivel.sendParticles(AtalayaParticulas.RAJANG_POLVO, true, true, p.x, p.y + 0.8, p.z, 20, 0.3, 0.6, 0.3, 0.03);
        nivel.playSound(null, p.x, p.y + 1, p.z, AtalayaSonidos.RAJANG_SENUELO_ROMPE, SoundSource.HOSTILE, 2.0F, 1.0F);
        m.discard();
        if (quien instanceof LivingEntity v) {
            Vec3 fuera = RajangEntity.horizontalHacia(p, v.position());
            RajangEntity.lanzar(v, fuera.scale(1.1), 0.45);
            r.danoSinMatar(nivel, v, DANO_SENUELO);
        }
    }

    @Override
    void limpiar(ServerLevel nivel, boolean exito, boolean avisar) {
        Vec3 donde = escondite;
        for (Copia c : copias) {
            COPIAS.remove(c.m.getUUID());
            if (c.real && !c.m.isRemoved()) {
                donde = c.m.position();
            }
            Vec3 p = c.m.position();
            nivel.sendParticles(AtalayaParticulas.RAJANG_POLVO, true, true, p.x, p.y + 1.0, p.z, 24, 0.4, 0.8, 0.4, 0.04);
            c.m.discard();
        }
        copias.clear();
        if (!avisar && !exito) {
            // Cortado (cambio de fase, su muerte): vuelve donde estaba, sin mas.
            r.reaparecerMini(nivel, escondite, false);
            return;
        }
        Vec3 sale = RajangEntity.horizontal(donde, r.centroArena()) < 40 ? donde : escondite;
        r.reaparecerMini(nivel, sale, true);
        if (!exito && copiado != null && copiado.isAlive() && !copiado.isSpectator()) {
            // No le han pillado: salta sobre el que copio.
            r.saltarMini(nivel, copiado.position(), copiado);
        }
    }

    @Override
    void forzarExito(ServerLevel nivel) {
        for (Copia c : copias) {
            if (c.real) {
                golpeada(nivel, c.m, null);
                return;
            }
        }
    }

    // ------------------------------------------------------------------
    //  Lo que llega de fuera
    // ------------------------------------------------------------------

    /** Antes de cualquier dano a un ser vivo: a una copia no le entra nada, pero cuenta el golpe. */
    public static boolean alDanar(LivingEntity v, DamageSource fuente) {
        if (!(v instanceof Mannequin m) || !m.entityTags().contains(ETIQUETA)) {
            return true;
        }
        ImpostorRajang juego = COPIAS.get(m.getUUID());
        if (juego != null && v.level() instanceof ServerLevel nivel) {
            Entity quien = fuente.getEntity();
            if (quien instanceof Player || fuente.getDirectEntity() instanceof net.minecraft.world.entity.projectile.Projectile) {
                juego.golpeada(nivel, m, quien != null ? quien : fuente.getDirectEntity());
            }
        }
        return false;
    }

    /** Una copia que se quedo en el mundo (se cerro a medias): fuera. */
    public static void alCargar(Entity e) {
        if (e instanceof Mannequin m && m.entityTags().contains(ETIQUETA) && !COPIAS.containsKey(m.getUUID())) {
            m.discard();
        }
    }

    /** Una copia no es presa de ningun jefe. */
    public static boolean esCopia(Entity e) {
        return e instanceof Mannequin m && m.entityTags().contains(ETIQUETA);
    }
}
