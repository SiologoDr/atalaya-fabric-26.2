package com.atalaya.momento;

import com.atalaya.particula.AtalayaParticulas;
import net.minecraft.core.BlockPos;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.util.Mth;
import net.minecraft.util.RandomSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.entity.EntitySpawnReason;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.EntityTypes;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.Relative;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.phys.Vec3;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Set;
import java.util.UUID;
import java.util.function.Supplier;

/** Los momentos de SUCESOS: lo que cae, aparece o cambia mientras duran. */
final class SucesosLluvia {

    private SucesosLluvia() {
    }

    // ------------------------------------------------------------------
    //  Lo que aparece a tu lado
    // ------------------------------------------------------------------

    /** Creepers cargados de un corazon junto a cualquiera, en cualquier momento. */
    static final class Creepers implements Suceso {
        @Override
        public void tick(MinecraftServer s, int t) {
            if (t % 20 == 0) {
                for (ServerPlayer p : Peligro.jugadores(s)) {
                    if (p.getRandom().nextFloat() < 0.06F) {
                        Peligro.creeper(p);
                    }
                }
            }
        }
    }

    /**
     * Cualquier criatura a tu lado sin avisar. Los mobs del bestiario se apuntan en {@link #EXTRA} al registrarse (los
     * que esten sueltos o no: el momento los saca igual).
     */
    static final class Cualquiera implements Suceso {
        static final List<EntityType<? extends Mob>> DE_SIEMPRE = List.of(EntityTypes.ZOMBIE, EntityTypes.SKELETON,
                EntityTypes.SPIDER, EntityTypes.CAVE_SPIDER, EntityTypes.CREEPER, EntityTypes.WITCH, EntityTypes.VINDICATOR,
                EntityTypes.PILLAGER, EntityTypes.HUSK, EntityTypes.STRAY, EntityTypes.BOGGED, EntityTypes.SILVERFISH,
                EntityTypes.ENDERMITE, EntityTypes.BLAZE, EntityTypes.WITHER_SKELETON, EntityTypes.PIGLIN_BRUTE,
                EntityTypes.SLIME, EntityTypes.MAGMA_CUBE, EntityTypes.BREEZE, EntityTypes.EVOKER);

        @Override
        public void tick(MinecraftServer s, int t) {
            if (t % 20 != 0) {
                return;
            }
            for (ServerPlayer p : Peligro.jugadores(s)) {
                RandomSource r = p.getRandom();
                if (r.nextFloat() >= 0.06F) {
                    continue;
                }
                EntityType<? extends Mob> tipo;
                int total = DE_SIEMPRE.size() + Momentos.EXTRA_CUALQUIERA.size();
                int i = r.nextInt(total);
                tipo = i < DE_SIEMPRE.size() ? DE_SIEMPRE.get(i) : Momentos.EXTRA_CUALQUIERA.get(i - DE_SIEMPRE.size()).get();
                BlockPos pos = p.blockPosition().offset(r.nextInt(5) - 2, 0, r.nextInt(5) - 2);
                Mob m = tipo.spawn(p.level(), pos, EntitySpawnReason.EVENT);
                if (m != null) {
                    m.setTarget(p);
                    p.level().sendParticles(AtalayaParticulas.MALDICION_MOTA, m.getX(), m.getY() + 1, m.getZ(), 20, 0.5, 0.8, 0.5, 0.05);
                }
            }
        }
    }

    // ------------------------------------------------------------------
    //  Tornados y el cielo que arde
    // ------------------------------------------------------------------

    static final class Tornados implements Suceso {
        @Override
        public void tick(MinecraftServer s, int t) {
            if (t % 40 == 0) {
                List<ServerPlayer> todos = Peligro.jugadores(s);
                if (EfectosMomento.tornados() < Math.max(2, todos.size() * 2)) {
                    for (ServerPlayer p : todos) {
                        if (p.level().dimension() == Level.OVERWORLD && p.getRandom().nextFloat() < 0.5F) {
                            EfectosMomento.tornado(p, 500 + p.getRandom().nextInt(300));
                        }
                    }
                }
            }
        }

        @Override
        public void acaba(MinecraftServer s) {
            EfectosMomento.sinTornados();
        }
    }

    /** Un minuto para esconderse; luego, minuto y medio de bombardeo sobre lo que este al raso. */
    static final class CieloArde extends SucesosRefugio.Refugio {
        CieloArde() {
            super(60);
        }

        @Override
        public int despues() {
            return Momentos.ticks(90);
        }

        @Override
        boolean aSalvo(ServerPlayer p) {
            return SucesosRefugio.bajoTecho(p);
        }

        @Override
        String falta(ServerPlayer p) {
            return "Al raso te va a alcanzar: métete bajo tierra.";
        }

        @Override
        public void tick(MinecraftServer s, int t) {
            int cero = contador();
            if (t < cero) {
                super.tick(s, t);
                return;
            }
            // El bombardeo: explosiones por toda la superficie alrededor de cada uno, y sobre quien sigue al raso.
            if (t % 6 == 0) {
                for (ServerPlayer p : Peligro.jugadores(s)) {
                    if (p.level().dimension() != Level.OVERWORLD) {
                        continue;
                    }
                    RandomSource r = p.getRandom();
                    ServerLevel nivel = p.level();
                    double x = p.getX() + (r.nextDouble() - 0.5) * 60;
                    double z = p.getZ() + (r.nextDouble() - 0.5) * 60;
                    if (!aSalvo(p) && r.nextFloat() < 0.35F) {
                        x = p.getX() + (r.nextDouble() - 0.5) * 6;
                        z = p.getZ() + (r.nextDouble() - 0.5) * 6;
                    }
                    int y = nivel.getHeight(Heightmap.Types.MOTION_BLOCKING, Mth.floor(x), Mth.floor(z));
                    nivel.sendParticles(AtalayaParticulas.MJ_DESTELLO, x, y + 1, z, 0, 5.0, 0, 3, 1.0);
                    nivel.explode(null, x, y, z, 2.5F, true, Level.ExplosionInteraction.MOB);
                }
            }
            if ((t - cero) % 20 == 0) {
                for (ServerPlayer p : Peligro.jugadores(s)) {
                    boolean bien = aSalvo(p);
                    Peligro.barra(p, bien ? "Aguanta: el bombardeo sigue arriba." : "¡Estás al raso! Métete bajo tierra.", bien);
                }
            }
        }
    }

    // ------------------------------------------------------------------
    //  El cambio de cuerpos
    // ------------------------------------------------------------------

    /**
     * Cuatro jugadores (o los que haya, en numero par) se cambian el cuerpo por parejas: el sitio, el inventario, la
     * vida, el hambre, la experiencia y los efectos. Al acabar, cada uno recupera lo suyo (lo que quede), en el sitio
     * donde este.
     */
    static final class CambioDeCuerpos implements Suceso {
        private final List<UUID[]> parejas = new ArrayList<>();

        @Override
        public void empieza(MinecraftServer s) {
            List<ServerPlayer> todos = Peligro.jugadores(s);
            Collections.shuffle(todos);
            int n = Math.min(4, todos.size() - todos.size() % 2);
            for (int i = 0; i + 1 < n; i += 2) {
                ServerPlayer a = todos.get(i);
                ServerPlayer b = todos.get(i + 1);
                parejas.add(new UUID[]{a.getUUID(), b.getUUID()});
                cambiar(a, b, true);
                Peligro.barra(a, "Ahora eres " + b.getName().getString() + ".", false);
                Peligro.barra(b, "Ahora eres " + a.getName().getString() + ".", false);
            }
            if (parejas.isEmpty()) {
                Peligro.chat(s, "No hay con quién cambiarse el cuerpo.");
            }
        }

        @Override
        public void acaba(MinecraftServer s) {
            for (UUID[] par : parejas) {
                ServerPlayer a = s.getPlayerList().getPlayer(par[0]);
                ServerPlayer b = s.getPlayerList().getPlayer(par[1]);
                if (a != null && b != null) {
                    cambiar(a, b, false);
                }
            }
            parejas.clear();
        }

        /** Se cambian lo que llevan, la vida, el hambre, la experiencia y los efectos (y el sitio, si toca). */
        private static void cambiar(ServerPlayer a, ServerPlayer b, boolean sitio) {
            List<ItemStack> deA = new ArrayList<>();
            for (int i = 0; i < a.getInventory().getContainerSize(); i++) {
                deA.add(a.getInventory().getItem(i).copy());
            }
            for (int i = 0; i < a.getInventory().getContainerSize(); i++) {
                a.getInventory().setItem(i, b.getInventory().getItem(i).copy());
            }
            for (int i = 0; i < deA.size(); i++) {
                b.getInventory().setItem(i, deA.get(i));
            }
            float vida = a.getHealth();
            a.setHealth(Math.min(b.getHealth(), a.getMaxHealth()));
            b.setHealth(Math.min(vida, b.getMaxHealth()));
            int comida = a.getFoodData().getFoodLevel();
            a.getFoodData().setFoodLevel(b.getFoodData().getFoodLevel());
            b.getFoodData().setFoodLevel(comida);
            int nivelA = a.experienceLevel;
            float progA = a.experienceProgress;
            a.setExperienceLevels(b.experienceLevel);
            a.experienceProgress = b.experienceProgress;
            b.setExperienceLevels(nivelA);
            b.experienceProgress = progA;
            List<MobEffectInstance> efA = new ArrayList<>(a.getActiveEffects());
            List<MobEffectInstance> efB = new ArrayList<>(b.getActiveEffects());
            a.removeAllEffects();
            b.removeAllEffects();
            for (MobEffectInstance e : efB) {
                a.addEffect(new MobEffectInstance(e));
            }
            for (MobEffectInstance e : efA) {
                b.addEffect(new MobEffectInstance(e));
            }
            if (sitio) {
                ServerLevel nA = a.level();
                Vec3 pA = a.position();
                float yA = a.getYRot();
                float xA = a.getXRot();
                a.teleportTo(b.level(), b.getX(), b.getY(), b.getZ(), Set.<Relative>of(), b.getYRot(), b.getXRot(), false);
                b.teleportTo(nA, pA.x, pA.y, pA.z, Set.<Relative>of(), yA, xA, false);
            }
        }
    }

    // ------------------------------------------------------------------
    //  La horda
    // ------------------------------------------------------------------

    /**
     * Dos minutos para prepararse (el contador); luego tres oleadas de muertos alrededor de cada uno, cada una mas
     * grande. Entre una y otra, medio minuto de respiro. La barra dice la oleada y cuantos quedan.
     */
    static final class Horda implements Suceso {
        private static final int OLEADAS = 3;
        private static final List<Supplier<EntityType<? extends Mob>>> MUERTOS = List.of(() -> EntityTypes.ZOMBIE,
                () -> EntityTypes.ZOMBIE, () -> EntityTypes.HUSK, () -> EntityTypes.SKELETON, () -> EntityTypes.ZOMBIE_VILLAGER,
                () -> EntityTypes.STRAY, () -> EntityTypes.SPIDER);
        private int oleada;
        private int respiro = -1;
        private final List<UUID> vivos = new ArrayList<>();

        private final int prepara = Momentos.ticks(120);

        @Override
        public int contador() {
            return prepara;
        }

        @Override
        public int despues() {
            return 12 * 60 * 20;
        }

        @Override
        public void tick(MinecraftServer s, int t) {
            if (t < contador()) {
                return;
            }
            if (t == contador()) {
                lanzar(s);
                return;
            }
            vivos.removeIf(id -> {
                for (ServerLevel n : s.getAllLevels()) {
                    var e = n.getEntity(id);
                    if (e != null) {
                        return !e.isAlive();
                    }
                }
                return true;
            });
            if (respiro > 0) {
                respiro--;
                if (respiro == 0) {
                    lanzar(s);
                }
            } else if (vivos.isEmpty()) {
                if (oleada >= OLEADAS) {
                    Peligro.chat(s, "La horda ha caído. Habéis sobrevivido.");
                    Momentos.terminar();
                    return;
                }
                respiro = 30 * 20;
                Peligro.chat(s, "Oleada " + oleada + " superada. Medio minuto de respiro.");
            }
            if (t % 20 == 0) {
                for (ServerPlayer p : Peligro.jugadores(s)) {
                    Peligro.barra(p, respiro > 0 ? "Respiro: " + respiro / 20 + " s · luego la oleada " + (oleada + 1) + " de " + OLEADAS
                            : "Oleada " + oleada + " de " + OLEADAS + " · quedan " + vivos.size(), respiro > 0);
                }
            }
        }

        private void lanzar(MinecraftServer s) {
            oleada++;
            respiro = -1;
            Peligro.chat(s, "¡Oleada " + oleada + " de " + OLEADAS + "!");
            for (ServerPlayer p : Peligro.jugadores(s)) {
                ServerLevel nivel = p.level();
                RandomSource r = nivel.getRandom();
                int cuantos = 3 + oleada * 3;
                for (int i = 0; i < cuantos; i++) {
                    double a = r.nextDouble() * Mth.TWO_PI;
                    double d = 14 + r.nextDouble() * 10;
                    int x = Mth.floor(p.getX() + Math.cos(a) * d);
                    int z = Mth.floor(p.getZ() + Math.sin(a) * d);
                    BlockPos pos = nivel.dimension() == Level.OVERWORLD
                            ? new BlockPos(x, nivel.getHeight(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, x, z), z)
                            : BlockPos.containing(x, p.getY(), z);
                    Mob m = MUERTOS.get(r.nextInt(MUERTOS.size())).get().spawn(nivel, pos, EntitySpawnReason.EVENT);
                    if (m != null) {
                        m.setTarget(p);
                        m.setPersistenceRequired();
                        m.addEffect(new MobEffectInstance(net.minecraft.world.effect.MobEffects.FIRE_RESISTANCE, 20 * 60 * 10, 0, false, false));
                        vivos.add(m.getUUID());
                    }
                }
            }
        }

        @Override
        public void acaba(MinecraftServer s) {
            vivos.clear();
        }
    }
}
