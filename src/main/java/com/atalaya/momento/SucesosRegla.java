package com.atalaya.momento;

import com.atalaya.Atalaya;
import com.atalaya.cambios.Plaga;
import com.atalaya.effect.VidaOcultaEffect;
import net.minecraft.core.BlockPos;
import net.minecraft.resources.Identifier;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.util.Mth;
import net.minecraft.util.RandomSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.EntitySpawnReason;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.EntityTypes;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.Relative;
import net.minecraft.world.entity.ai.attributes.AttributeInstance;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.gamerules.GameRules;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Set;

/** Los momentos de MIENTRAS DURA: una regla que se pone al salir el aviso y se quita al acabar. */
final class SucesosRegla {

    private SucesosRegla() {
    }

    /** Pone o quita un modificador de atributo a un jugador. */
    static void modificar(ServerPlayer p, net.minecraft.core.Holder<net.minecraft.world.entity.ai.attributes.Attribute> atributo,
                          Identifier id, double cantidad, AttributeModifier.Operation op, boolean poner) {
        AttributeInstance a = p.getAttribute(atributo);
        if (a == null) {
            return;
        }
        if (poner && !a.hasModifier(id)) {
            a.addTransientModifier(new AttributeModifier(id, cantidad, op));
        } else if (!poner && a.hasModifier(id)) {
            a.removeModifier(id);
        }
    }

    // ------------------------------------------------------------------
    //  Vida a medias
    // ------------------------------------------------------------------

    /** Vida a medias: la mitad de la vida maxima a todos (a quien entre o reaparezca mientras dura, tambien). */
    static final class MediaVida implements Suceso {
        private static final Identifier ID = Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "momento_vida_a_medias");

        @Override
        public void empieza(MinecraftServer s) {
            for (ServerPlayer p : s.getPlayerList().getPlayers()) {
                alEntrar(p);
            }
        }

        @Override
        public void alEntrar(ServerPlayer p) {
            modificar(p, Attributes.MAX_HEALTH, ID, -0.5, AttributeModifier.Operation.ADD_MULTIPLIED_TOTAL, true);
            if (p.getHealth() > p.getMaxHealth()) {
                p.setHealth(p.getMaxHealth());
            }
        }

        @Override
        public void acaba(MinecraftServer s) {
            for (ServerPlayer p : s.getPlayerList().getPlayers()) {
                modificar(p, Attributes.MAX_HEALTH, ID, 0, AttributeModifier.Operation.ADD_MULTIPLIED_TOTAL, false);
            }
        }
    }

    // ------------------------------------------------------------------
    //  La oscuridad, sin caida lenta y la sequia
    // ------------------------------------------------------------------

    static final class Oscuridad implements Suceso {
        @Override
        public void tick(MinecraftServer s, int t) {
            if (t % 10 == 0) {
                for (ServerPlayer p : s.getPlayerList().getPlayers()) {
                    if (p.isSpectator()) {
                        continue;
                    }
                    p.removeEffect(MobEffects.NIGHT_VISION);
                    p.addEffect(new MobEffectInstance(MobEffects.DARKNESS, 60, 0, false, false));
                    p.addEffect(new MobEffectInstance(MobEffects.BLINDNESS, 30, 0, false, false));
                }
            }
        }
    }

    static final class SinCaidaLenta implements Suceso {
        @Override
        public void tick(MinecraftServer s, int t) {
            for (ServerPlayer p : s.getPlayerList().getPlayers()) {
                if (p.hasEffect(MobEffects.SLOW_FALLING)) {
                    p.removeEffect(MobEffects.SLOW_FALLING);
                }
                if (p.isFallFlying()) {
                    p.stopFallFlying();
                }
            }
        }
    }

    static final class Sequia implements Suceso {
        @Override
        public void tick(MinecraftServer s, int t) {
            if (t % 5 != 0) {
                return;
            }
            for (ServerPlayer p : s.getPlayerList().getPlayers()) {
                Inventory inv = p.getInventory();
                for (int i = 0; i < inv.getContainerSize(); i++) {
                    if (inv.getItem(i).is(Items.WATER_BUCKET)) {
                        inv.setItem(i, new ItemStack(Items.BUCKET));
                    }
                }
            }
        }
    }

    /** Si los cubos no se pueden llenar de agua ahora (lo pregunta el evento de usar objetos de Momentos). */
    static boolean secos() {
        return Momentos.activo(Momento.SEQUIA);
    }

    // ------------------------------------------------------------------
    //  El intercambio
    // ------------------------------------------------------------------

    /** Todos cambian de sitio al azar (nadie se queda en el suyo), al empezar y a mitad; sin ver la vida ni regenerar. */
    static final class Intercambio implements Suceso {
        private Boolean regeneraba;

        @Override
        public void empieza(MinecraftServer s) {
            GameRules reglas = s.overworld().getGameRules();
            regeneraba = reglas.get(GameRules.NATURAL_HEALTH_REGENERATION);
            reglas.set(GameRules.NATURAL_HEALTH_REGENERATION, false, s);
            cambiarSitios(Peligro.jugadores(s));
            for (ServerPlayer p : s.getPlayerList().getPlayers()) {
                alEntrar(p);
            }
        }

        @Override
        public void alEntrar(ServerPlayer p) {
            p.addEffect(new MobEffectInstance(VidaOcultaEffect.VIDA_OCULTA, 5 * 60 * 20, 0, false, false, true));
        }

        @Override
        public void tick(MinecraftServer s, int t) {
            if (t == 150 * 20) {
                Peligro.chat(s, "El intercambio vuelve a girar.");
                cambiarSitios(Peligro.jugadores(s));
            }
        }

        @Override
        public void acaba(MinecraftServer s) {
            if (regeneraba != null) {
                s.overworld().getGameRules().set(GameRules.NATURAL_HEALTH_REGENERATION, regeneraba, s);
            }
            for (ServerPlayer p : s.getPlayerList().getPlayers()) {
                p.removeEffect(VidaOcultaEffect.VIDA_OCULTA);
            }
        }
    }

    /** Cambia de sitio a todos al azar, sin que nadie se quede en el suyo (cada uno al del siguiente, barajados). */
    static void cambiarSitios(List<ServerPlayer> jugadores) {
        if (jugadores.size() < 2) {
            return;
        }
        List<ServerPlayer> orden = new ArrayList<>(jugadores);
        Collections.shuffle(orden);
        List<Object[]> sitios = new ArrayList<>();
        for (ServerPlayer p : orden) {
            sitios.add(new Object[]{p.level(), p.position(), p.getYRot(), p.getXRot()});
        }
        for (int i = 0; i < orden.size(); i++) {
            Object[] otro = sitios.get((i + 1) % orden.size());
            Vec3 pos = (Vec3) otro[1];
            orden.get(i).teleportTo((ServerLevel) otro[0], pos.x, pos.y, pos.z, Set.<Relative>of(), (Float) otro[2], (Float) otro[3], false);
        }
    }

    // ------------------------------------------------------------------
    //  Todos diminutos
    // ------------------------------------------------------------------

    /** Todos encogidos y sin poder saltar un bloque, hasta tomarse la Pildora del Tamano (o hasta que acabe). */
    static final class Diminutos implements Suceso {
        private static final Identifier ESCALA = Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "momento_diminuto");
        private static final Identifier SALTO = Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "momento_diminuto_salto");
        private final Set<java.util.UUID> curados = new java.util.HashSet<>();

        @Override
        public void empieza(MinecraftServer s) {
            for (ServerPlayer p : s.getPlayerList().getPlayers()) {
                alEntrar(p);
            }
        }

        @Override
        public void alEntrar(ServerPlayer p) {
            if (!curados.contains(p.getUUID())) {
                poner(p, true);
            }
        }

        static void poner(ServerPlayer p, boolean encoger) {
            modificar(p, Attributes.SCALE, ESCALA, -0.65, AttributeModifier.Operation.ADD_MULTIPLIED_TOTAL, encoger);
            modificar(p, Attributes.JUMP_STRENGTH, SALTO, -0.45, AttributeModifier.Operation.ADD_MULTIPLIED_TOTAL, encoger);
        }

        /** La Pildora del Tamano: vuelve a su altura. Devuelve si ha hecho algo. */
        boolean curar(ServerPlayer p) {
            if (!curados.add(p.getUUID())) {
                return false;
            }
            poner(p, false);
            return true;
        }

        @Override
        public void tick(MinecraftServer s, int t) {
            if (t % 40 == 0 && t > 0) {
                boolean alguno = false;
                for (ServerPlayer p : Peligro.jugadores(s)) {
                    if (!curados.contains(p.getUUID())) {
                        alguno = true;
                    }
                }
                if (!alguno && !Peligro.jugadores(s).isEmpty()) {
                    Peligro.chat(s, "Todos habéis vuelto a vuestra altura.");
                    Momentos.terminar();
                }
            }
        }

        @Override
        public void acaba(MinecraftServer s) {
            for (ServerPlayer p : s.getPlayerList().getPlayers()) {
                poner(p, false);
            }
        }
    }

    /** La Pildora del Tamano tomada por alguien: si el momento de los diminutos esta en marcha, lo cura. */
    static boolean pildoraTamano(ServerPlayer p) {
        return Momentos.suceso() instanceof Diminutos d && d.curar(p);
    }

    // ------------------------------------------------------------------
    //  La infeccion y el eclipse
    // ------------------------------------------------------------------

    /** La infeccion: todos con la plaga a tres minutos (con LA PLAGA encendida, se queda; si no, se va al acabar). */
    static final class Infeccion implements Suceso {
        @Override
        public void empieza(MinecraftServer s) {
            for (ServerPlayer p : s.getPlayerList().getPlayers()) {
                alEntrar(p);
            }
        }

        @Override
        public void alEntrar(ServerPlayer p) {
            Plaga.infectar(p, Plaga.TRAS_TOTEM);
        }

        @Override
        public void acaba(MinecraftServer s) {
            for (ServerPlayer p : s.getPlayerList().getPlayers()) {
                Plaga.curarMomento(p);
            }
        }
    }

    /** El eclipse: los monstruos salen de dia (alrededor de cada uno, en la superficie) y no arden. */
    static final class Eclipse implements Suceso {
        private static final List<EntityType<? extends Mob>> MONSTRUOS = List.of(EntityTypes.ZOMBIE, EntityTypes.SKELETON,
                EntityTypes.SPIDER, EntityTypes.CREEPER, EntityTypes.HUSK, EntityTypes.STRAY);

        @Override
        public void tick(MinecraftServer s, int t) {
            if (t % 40 != 0) {
                return;
            }
            for (ServerPlayer p : Peligro.jugadores(s)) {
                ServerLevel nivel = p.level();
                if (nivel.dimension() != Level.OVERWORLD || !nivel.isBrightOutside()) {
                    continue;
                }
                AABB zona = p.getBoundingBox().inflate(40);
                if (nivel.getEntitiesOfClass(net.minecraft.world.entity.monster.Monster.class, zona).size() > 14) {
                    continue;
                }
                RandomSource r = nivel.getRandom();
                double a = r.nextDouble() * Mth.TWO_PI;
                double d = 18 + r.nextDouble() * 18;
                int x = Mth.floor(p.getX() + Math.cos(a) * d);
                int z = Mth.floor(p.getZ() + Math.sin(a) * d);
                BlockPos pos = new BlockPos(x, nivel.getHeight(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, x, z), z);
                if (nivel.getBlockState(pos).isAir() && nivel.getBlockState(pos.above()).isAir()) {
                    MONSTRUOS.get(r.nextInt(MONSTRUOS.size())).spawn(nivel, pos, EntitySpawnReason.EVENT);
                }
            }
        }
    }

    /** Si los muertos no arden al sol ahora (el eclipse). */
    static boolean sinSol() {
        return Momentos.activo(Momento.EL_ECLIPSE);
    }
}
