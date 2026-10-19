package com.atalaya.momento;

import com.atalaya.particula.AtalayaParticulas;
import net.minecraft.core.BlockPos;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.tags.FluidTags;
import net.minecraft.util.Mth;
import net.minecraft.util.RandomSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.EntityTypes;
import net.minecraft.world.entity.LightningBolt;
import net.minecraft.world.entity.EntitySpawnReason;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.storage.LevelData;
import net.minecraft.world.phys.Vec3;

import java.util.List;

/**
 * Los momentos de PONTE A SALVO: un contador arriba y, mientras corre, la barra le dice a cada uno si ya esta a salvo o
 * que le falta; al llegar a cero, a quien no lo este le cae lo suyo (el gas, el rayo, el meteorito...) con un dano que
 * crece cada segundo hasta matarlo (aunque tenga totems, no aguanta mucho). Mientras corre, cada uno hace lo suyo: caen
 * meteoritos, tira el agujero negro, llueven creepers...
 */
final class SucesosRefugio {

    private SucesosRefugio() {
    }

    /** La plantilla: el contador, el aviso de la barra y el castigo al llegar a cero. */
    abstract static class Refugio implements Suceso {

        private final int ticks;
        /** Los que ya cayeron (al reaparecer, ya han pagado: no se les vuelve a castigar). */
        private final java.util.Set<java.util.UUID> caidos = new java.util.HashSet<>();

        Refugio(int segundos) {
            this.ticks = Momentos.ticks(segundos);
        }

        @Override
        public int contador() {
            return ticks;
        }

        /** Si ese jugador esta a salvo. */
        abstract boolean aSalvo(ServerPlayer p);

        /** Lo que le dice la barra si aun no lo esta. */
        abstract String falta(ServerPlayer p);

        /** Lo que pasa mientras corre el contador (cada tick). */
        void durante(MinecraftServer s, int t) {
        }

        /** Lo que le pasa, al llegar a cero, al que no esta a salvo (una vez; luego el dano que crece). */
        void alCaer(ServerPlayer p) {
        }

        /** Lo que se ve al llegar a cero (una vez). */
        void alFinal(MinecraftServer s) {
        }

        @Override
        public void tick(MinecraftServer s, int t) {
            if (t < ticks) {
                durante(s, t);
                if (t % 20 == 0) {
                    for (ServerPlayer p : Peligro.jugadores(s)) {
                        boolean bien = aSalvo(p);
                        Peligro.barra(p, bien ? "A salvo. Quédate ahí." : falta(p), bien);
                    }
                }
                return;
            }
            if (t == ticks) {
                alFinal(s);
                for (ServerPlayer p : Peligro.jugadores(s)) {
                    if (!aSalvo(p)) {
                        alCaer(p);
                    }
                }
            }
            if ((t - ticks) % 20 == 0) {
                int k = (t - ticks) / 20;
                for (ServerPlayer p : Peligro.jugadores(s)) {
                    if (!aSalvo(p) && !caidos.contains(p.getUUID())) {
                        Peligro.danar(p, 4.0F * (1 << Math.min(k, 8)));
                        if (p.isDeadOrDying()) {
                            caidos.add(p.getUUID());
                        }
                    }
                }
            }
        }
    }

    // ------------------------------------------------------------------
    //  El gas
    // ------------------------------------------------------------------

    /** El gas: verde alrededor de quien esta fuera de la franja buena. */
    abstract static class Gas extends Refugio {
        Gas() {
            super(300);
        }

        @Override
        void durante(MinecraftServer s, int t) {
            if (t % 10 == 0) {
                for (ServerPlayer p : Peligro.jugadores(s)) {
                    if (!aSalvo(p)) {
                        p.level().sendParticles(AtalayaParticulas.MALDICION_MOTA, p.getX(), p.getY() + 1, p.getZ(), 3, 2.5, 1.5, 2.5, 0.0);
                    }
                }
            }
        }

        @Override
        void alCaer(ServerPlayer p) {
            p.addEffect(new MobEffectInstance(MobEffects.NAUSEA, 200, 0, false, false));
        }
    }

    static final class GasSube extends Gas {
        @Override
        boolean aSalvo(ServerPlayer p) {
            return p.getY() >= 250;
        }

        @Override
        String falta(ServerPlayer p) {
            return "Sube: estás en la capa " + Mth.floor(p.getY()) + " y el aire limpio empieza en la 250.";
        }
    }

    static final class GasBaja extends Gas {
        @Override
        boolean aSalvo(ServerPlayer p) {
            return p.level().dimension() == Level.OVERWORLD && p.getY() < 0;
        }

        @Override
        String falta(ServerPlayer p) {
            return p.level().dimension() != Level.OVERWORLD ? "Vuelve al mundo y baja por debajo de la capa 0."
                    : "Baja: estás en la capa " + Mth.floor(p.getY()) + " y hay que estar por debajo de la 0.";
        }
    }

    static final class Franja extends Gas {
        @Override
        boolean aSalvo(ServerPlayer p) {
            return p.level().dimension() == Level.OVERWORLD && p.getY() >= 120 && p.getY() <= 131;
        }

        @Override
        String falta(ServerPlayer p) {
            return p.level().dimension() != Level.OVERWORLD ? "Vuelve al mundo: entre las capas 120 y 130."
                    : "Ponte entre las capas 120 y 130: estás en la " + Mth.floor(p.getY()) + ".";
        }
    }

    // ------------------------------------------------------------------
    //  Bajo techo: el rayo, los meteoritos y el agujero negro
    // ------------------------------------------------------------------

    /** Si tiene techo de verdad encima (nada de cielo sobre su cabeza). */
    static boolean bajoTecho(ServerPlayer p) {
        return !p.level().canSeeSky(BlockPos.containing(p.getEyePosition()));
    }

    static final class Rayo extends Refugio {
        Rayo() {
            super(180);
        }

        @Override
        boolean aSalvo(ServerPlayer p) {
            return bajoTecho(p);
        }

        @Override
        String falta(ServerPlayer p) {
            return "Estás al raso: métete bajo techo antes de que caiga el rayo.";
        }

        @Override
        void durante(MinecraftServer s, int t) {
            // Truenos lejanos, cada vez mas seguidos.
            int cada = Math.max(40, 300 - t / 6);
            if (t % cada == 0) {
                for (ServerPlayer p : Peligro.jugadores(s)) {
                    RandomSource r = p.getRandom();
                    double a = r.nextDouble() * Mth.TWO_PI;
                    rayo(p.level(), p.getX() + Math.cos(a) * 60, p.getZ() + Math.sin(a) * 60, true);
                }
            }
        }

        @Override
        void alCaer(ServerPlayer p) {
            rayo(p.level(), p.getX(), p.getZ(), true);
        }
    }

    static void rayo(ServerLevel nivel, double x, double z, boolean soloVisual) {
        LightningBolt rayo = EntityTypes.LIGHTNING_BOLT.create(nivel, EntitySpawnReason.EVENT);
        if (rayo != null) {
            int y = nivel.getHeight(net.minecraft.world.level.levelgen.Heightmap.Types.MOTION_BLOCKING, Mth.floor(x), Mth.floor(z));
            rayo.setPos(x, y, z);
            rayo.setVisualOnly(soloVisual);
            nivel.addFreshEntity(rayo);
        }
    }

    static final class Meteoritos extends Refugio {
        Meteoritos() {
            super(240);
        }

        @Override
        public void empieza(MinecraftServer s) {
            Momentos.cerrarNether(true);
        }

        @Override
        public void acaba(MinecraftServer s) {
            Momentos.cerrarNether(false);
        }

        @Override
        boolean aSalvo(ServerPlayer p) {
            return bajoTecho(p) && p.level().dimension() != Level.NETHER;
        }

        @Override
        String falta(ServerPlayer p) {
            return "Estás al raso: busca techo antes de que caiga el grande.";
        }

        @Override
        void durante(MinecraftServer s, int t) {
            // Cada vez mas: al principio uno cada pocos segundos; al final, una lluvia.
            int cada = Math.max(8, 70 - t / 80);
            if (t % cada != 0) {
                return;
            }
            List<ServerPlayer> todos = Peligro.jugadores(s);
            if (todos.isEmpty()) {
                return;
            }
            ServerPlayer p = todos.get(s.overworld().getRandom().nextInt(todos.size()));
            if (p.level().dimension() == Level.OVERWORLD) {
                RandomSource r = p.getRandom();
                EfectosMomento.meteorito(p.level(), p.getX() + (r.nextDouble() - 0.5) * 50, p.getZ() + (r.nextDouble() - 0.5) * 50,
                        1.5F + r.nextFloat() * 1.5F);
            }
        }

        @Override
        void alCaer(ServerPlayer p) {
            EfectosMomento.meteorito(p.level(), p.getX(), p.getZ(), 4.0F);
        }
    }

    static final class AgujeroNegro extends Refugio {
        AgujeroNegro() {
            super(180);
        }

        @Override
        boolean aSalvo(ServerPlayer p) {
            return bajoTecho(p);
        }

        @Override
        String falta(ServerPlayer p) {
            return "El agujero tira de ti: métete bajo techo.";
        }

        @Override
        void durante(MinecraftServer s, int t) {
            float fuerza = t / (float) contador();
            for (ServerPlayer p : Peligro.jugadores(s)) {
                if (aSalvo(p) || p.level().dimension() != Level.OVERWORLD) {
                    continue;
                }
                if (t % 4 == 0) {
                    p.level().sendParticles(AtalayaParticulas.MALDICION_MOTA, p.getX(), p.getY() + 2, p.getZ(), 2, 1.5, 1.0, 1.5, 0.05);
                }
                // Tira hacia arriba, mas cuanto mas se acerca el cero.
                if (t % 20 == 0 && p.getRandom().nextFloat() < fuerza) {
                    p.setDeltaMovement(p.getDeltaMovement().add(0, 0.35 + fuerza * 0.4, 0));
                    p.hurtMarked = true;
                }
            }
        }

        @Override
        void alCaer(ServerPlayer p) {
            p.addEffect(new MobEffectInstance(MobEffects.LEVITATION, 120, 6, false, false));
        }
    }

    // ------------------------------------------------------------------
    //  La supernova
    // ------------------------------------------------------------------

    static final class Supernova extends Refugio {
        private Vec3 centro = Vec3.ZERO;

        Supernova() {
            super(300);
        }

        @Override
        public void empieza(MinecraftServer s) {
            double x = 0, z = 0;
            int n = 0;
            for (ServerPlayer p : Peligro.jugadores(s)) {
                if (p.level().dimension() == Level.OVERWORLD) {
                    x += p.getX();
                    z += p.getZ();
                    n++;
                }
            }
            centro = n == 0 ? Vec3.atBottomCenterOf(s.overworld().getRespawnData().pos()) : new Vec3(x / n, 0, z / n);
        }

        @Override
        boolean aSalvo(ServerPlayer p) {
            return p.level().dimension() != Level.OVERWORLD || distancia(p) >= 300;
        }

        private double distancia(ServerPlayer p) {
            return Math.hypot(p.getX() - centro.x, p.getZ() - centro.z);
        }

        @Override
        String falta(ServerPlayer p) {
            return "Aléjate: estás a " + Mth.floor(distancia(p)) + " bloques de la estrella (hacen falta 300).";
        }

        @Override
        void durante(MinecraftServer s, int t) {
            if (t % 4 != 0) {
                return;
            }
            // La estrella en lo alto, para cada uno en su direccion: a unos setenta bloques (dentro de la niebla del
            // cielo roto) y alta, sobre el sitio de donde hay que huir. Crece y late hasta el cero.
            float k = t / (float) contador();
            for (ServerPlayer p : Peligro.jugadores(s)) {
                if (p.level().dimension() != Level.OVERWORLD) {
                    continue;
                }
                Vec3 hacia = new Vec3(centro.x - p.getX(), 0, centro.z - p.getZ());
                double lejos = hacia.length();
                Vec3 dir = lejos < 1 ? new Vec3(0, 0, 0) : hacia.scale(1.0 / lejos);
                double horizontal = Math.min(lejos, 40);
                Vec3 punto = p.getEyePosition().add(dir.scale(horizontal)).add(0, 55, 0);
                ServerLevel n = p.level();
                n.sendParticles(p, AtalayaParticulas.MJ_DESTELLO, true, true, punto.x, punto.y, punto.z, 0, 4 + k * 10, 0, 4, 1.0);
                n.sendParticles(p, AtalayaParticulas.NOVILIS_LUZ, true, true, punto.x, punto.y, punto.z, 4 + (int) (k * 10),
                        1 + k * 3, 1 + k * 3, 1 + k * 3, 0.04);
            }
        }

        @Override
        void alFinal(MinecraftServer s) {
            for (ServerPlayer p : Peligro.jugadores(s)) {
                if (p.level().dimension() == Level.OVERWORLD) {
                    p.level().sendParticles(p, AtalayaParticulas.MJ_DESTELLO, true, true, p.getX(), p.getEyeY(), p.getZ(), 0, 40, 0, 4, 1.0);
                }
            }
        }
    }

    // ------------------------------------------------------------------
    //  La luna de sangre, la tormenta marchita y bajo el agua
    // ------------------------------------------------------------------

    static final class LunaDeSangre extends Refugio {
        LunaDeSangre() {
            super(240);
        }

        @Override
        public void empieza(MinecraftServer s) {
            // Se hace de noche: el reloj del mundo salta a la medianoche.
            ServerLevel mundo = s.overworld();
            mundo.dimensionType().defaultClock().ifPresent(reloj ->
                    mundo.clockManager().moveToTimeMarker(reloj, net.minecraft.world.clock.ClockTimeMarkers.MIDNIGHT));
        }

        /** Su cama (o el punto de aparicion del mundo, si no tiene). */
        private static Vec3 casa(ServerPlayer p) {
            ServerPlayer.RespawnConfig c = p.getRespawnConfig();
            LevelData.RespawnData datos = c != null ? c.respawnData() : p.level().getServer().overworld().getRespawnData();
            return Vec3.atBottomCenterOf(datos.pos());
        }

        @Override
        boolean aSalvo(ServerPlayer p) {
            return p.position().distanceTo(casa(p)) <= 24;
        }

        @Override
        String falta(ServerPlayer p) {
            return "Vuelve a tu cama: estás a " + Mth.floor(p.position().distanceTo(casa(p))) + " bloques.";
        }

        @Override
        void durante(MinecraftServer s, int t) {
            if (t % 40 == 0) {
                for (ServerPlayer p : Peligro.jugadores(s)) {
                    if (p.getRandom().nextFloat() < 0.18F) {
                        Peligro.creeper(p);
                    }
                }
            }
        }
    }

    static final class TormentaMarchita extends Refugio {
        TormentaMarchita() {
            super(240);
        }

        @Override
        public void empieza(MinecraftServer s) {
            Momentos.cerrarVuelta(true);
        }

        @Override
        public void acaba(MinecraftServer s) {
            Momentos.cerrarVuelta(false);
        }

        @Override
        boolean aSalvo(ServerPlayer p) {
            return p.level().dimension() != Level.OVERWORLD;
        }

        @Override
        String falta(ServerPlayer p) {
            return "La tormenta llega: sal del mundo (al Nether o al End). Del Nether no se puede volver.";
        }

        @Override
        void durante(MinecraftServer s, int t) {
            if (t % 10 == 0) {
                for (ServerPlayer p : Peligro.jugadores(s)) {
                    if (!aSalvo(p)) {
                        p.level().sendParticles(AtalayaParticulas.NOVILIS_CENIZA, p.getX(), p.getY() + 3, p.getZ(), 6, 6, 3, 6, 0.0);
                    }
                }
            }
            if (t % 60 == 0) {
                for (ServerPlayer p : Peligro.jugadores(s)) {
                    if (p.getRandom().nextFloat() < 0.12F) {
                        Peligro.creeper(p);
                    }
                }
            }
        }

        @Override
        void alCaer(ServerPlayer p) {
            p.addEffect(new MobEffectInstance(MobEffects.WITHER, 2400, 2, false, true));
        }
    }

    static final class BajoElAgua extends Refugio {
        BajoElAgua() {
            super(300);
        }

        @Override
        public int despues() {
            return Momentos.ticks(120);
        }

        @Override
        boolean aSalvo(ServerPlayer p) {
            return p.isEyeInFluid(FluidTags.WATER) && p.isInWater();
        }

        @Override
        String falta(ServerPlayer p) {
            return "Métete entero bajo el agua (y que no te asome la cabeza).";
        }

        @Override
        public void tick(MinecraftServer s, int t) {
            super.tick(s, t);
            int fin = contador();
            if (t >= fin && (t - fin) % 20 == 0) {
                for (ServerPlayer p : Peligro.jugadores(s)) {
                    Peligro.barra(p, aSalvo(p) ? "Aguanta bajo el agua: quedan " + (despues() - (t - fin)) / 20 + " s."
                            : "¡Fuera del agua te quemas! Vuelve dentro.", aSalvo(p));
                    if (aSalvo(p) && p.getRandom().nextFloat() < 0.06F) {
                        Peligro.creeper(p);
                    }
                }
            }
        }
    }

    // ------------------------------------------------------------------
    //  El encadenado
    // ------------------------------------------------------------------

    /**
     * El encadenado (DEDsafio 4): cuatro pasos, cada uno con su contador en la barra y su aviso en el chat, y lo de
     * antes sigue (los creepers de un corazon, desde el primero): bajo la capa 0, luego por encima de la 250, luego los
     * tornados y al final, bajo techo. Quien no cumple un paso, cae (con el dano que crece unos segundos).
     */
    static final class Encadenado implements Suceso {
        private final int[] DURA = {Momentos.ticks(180), Momentos.ticks(300), Momentos.ticks(120), Momentos.ticks(120)};
        private static final String[] AVISO = {
                "Primer peligro: el gas cae. Baja por debajo de la capa 0. Y desde ahora, los creepers pueden caerte encima.",
                "Segundo peligro: el gas sube. Ahora, por encima de la capa 250.",
                "Tercer peligro: tornados por toda la superficie. Para escapar de uno, una perla de ender.",
                "Último peligro: va a caer el rayo. Métete bajo techo."};
        private int paso = -1;
        private int inicio;

        @Override
        public void empieza(MinecraftServer s) {
            siguiente(s, 0);
        }

        private void siguiente(MinecraftServer s, int t) {
            paso++;
            inicio = t;
            if (paso < AVISO.length) {
                Peligro.chat(s, AVISO[paso]);
            }
        }

        private boolean aSalvo(ServerPlayer p) {
            return switch (paso) {
                case 0 -> p.level().dimension() == Level.OVERWORLD && p.getY() < 0;
                case 1 -> p.getY() >= 250;
                case 3 -> bajoTecho(p);
                default -> true;
            };
        }

        @Override
        public void tick(MinecraftServer s, int t) {
            if (paso >= DURA.length) {
                return;
            }
            int dentro = t - inicio;
            int queda = DURA[paso] - dentro;
            if (t % 20 == 0) {
                for (ServerPlayer p : Peligro.jugadores(s)) {
                    String reloj = String.format("%d:%02d", Math.max(0, queda) / 1200, (Math.max(0, queda) / 20) % 60);
                    boolean bien = aSalvo(p);
                    Peligro.barra(p, reloj + "  ·  " + (paso == 2 ? "Huye de los tornados." : bien ? "A salvo." : AVISO[paso]), bien);
                    if (p.getRandom().nextFloat() < 0.05F) {
                        Peligro.creeper(p);
                    }
                }
            }
            if (paso == 2 && t % 30 == 0 && EfectosMomento.tornados() < Peligro.jugadores(s).size() * 2) {
                for (ServerPlayer p : Peligro.jugadores(s)) {
                    if (p.level().dimension() == Level.OVERWORLD) {
                        EfectosMomento.tornado(p, 600);
                    }
                }
            }
            if (queda <= 0) {
                if (queda > -100) {
                    if (queda % 20 == 0) {
                        int k = -queda / 20;
                        for (ServerPlayer p : Peligro.jugadores(s)) {
                            if (!aSalvo(p)) {
                                if (paso == 3 && k == 0) {
                                    SucesosRefugio.rayo(p.level(), p.getX(), p.getZ(), true);
                                }
                                Peligro.danar(p, 4.0F * (1 << Math.min(k, 8)));
                            }
                        }
                    }
                    return;
                }
                if (paso == 2) {
                    EfectosMomento.sinTornados();
                }
                siguiente(s, t);
                if (paso >= DURA.length) {
                    Momentos.terminar();
                }
            }
        }

        @Override
        public void acaba(MinecraftServer s) {
            EfectosMomento.sinTornados();
        }
    }
}
