package com.atalaya.momento;

import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.monster.Enemy;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;

import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;
import java.util.UUID;

/**
 * Los momentos de PRUEBAS: algo que hacer antes de que el contador llegue a cero. A quien no lo cumpla se lo lleva la
 * fractura (aunque tenga totems), como en la prueba de la tierra; a quien lo cumple no le pasa nada. La gran caza es de
 * todos a la vez: si entre todos no llegan, se los lleva a todos.
 */
final class SucesosPrueba {

    private SucesosPrueba() {
    }

    /** La plantilla: el contador, lo que se cuenta (Momentos se lo pasa) y el juicio al llegar a cero. */
    abstract static class Prueba implements Suceso {

        private final int ticks;
        private boolean juzgado;

        Prueba(int segundos) {
            this.ticks = Momentos.ticks(segundos);
        }

        @Override
        public int contador() {
            return ticks;
        }

        /** Si ese jugador ya ha cumplido. */
        abstract boolean cumple(ServerPlayer p);

        /** Lo que le dice la barra cada segundo (null: nada; la de la tierra no avisa). */
        String barra(ServerPlayer p) {
            return null;
        }

        /** Un bloque roto por alguien mientras corre el contador. */
        void alRomper(ServerPlayer p, BlockState estado) {
        }

        /** Un mob muerto a manos de alguien mientras corre el contador. */
        void alMatar(ServerPlayer p, LivingEntity muerto) {
        }

        boolean corre(int t) {
            return t < ticks;
        }

        @Override
        public void tick(MinecraftServer s, int t) {
            if (t < ticks) {
                if (t % 20 == 0) {
                    for (ServerPlayer p : Peligro.jugadores(s)) {
                        String b = barra(p);
                        if (b != null) {
                            Peligro.barra(p, b, cumple(p));
                        }
                    }
                }
                return;
            }
            if (!juzgado) {
                juzgado = true;
                for (ServerPlayer p : Peligro.jugadores(s)) {
                    if (!cumple(p)) {
                        Peligro.fractura(p);
                    }
                }
            }
        }
    }

    static final class GranCaza extends Prueba {
        private int meta;
        private int muertos;

        GranCaza() {
            super(600);
        }

        @Override
        public void empieza(MinecraftServer s) {
            meta = Math.max(40, 40 * Peligro.jugadores(s).size());
        }

        @Override
        boolean cumple(ServerPlayer p) {
            return muertos >= meta;
        }

        @Override
        String barra(ServerPlayer p) {
            return "Monstruos: " + Math.min(muertos, meta) + " / " + meta;
        }

        @Override
        void alMatar(ServerPlayer p, LivingEntity muerto) {
            if (muerto instanceof Enemy) {
                muertos++;
            }
        }
    }

    static final class Grito extends Prueba {
        private final Set<UUID> hecho = new HashSet<>();

        Grito() {
            super(600);
        }

        @Override
        boolean cumple(ServerPlayer p) {
            return hecho.contains(p.getUUID());
        }

        @Override
        String barra(ServerPlayer p) {
            return cumple(p) ? "Hecho: el abismo ya no te busca." : "Rompe un chillón de sculk.";
        }

        @Override
        void alRomper(ServerPlayer p, BlockState estado) {
            if (estado.is(Blocks.SCULK_SHRIEKER)) {
                hecho.add(p.getUUID());
            }
        }
    }

    /** La prueba de la tierra (16-10-2026, Juan): diez de tierra o cesped; "si cumples no te va a avisar". */
    static final class Tierra extends Prueba {
        private static final Set<Block> TIERRA = Set.of(Blocks.DIRT, Blocks.COARSE_DIRT, Blocks.ROOTED_DIRT, Blocks.GRASS_BLOCK);
        private final Map<UUID, Integer> rotos = new HashMap<>();

        Tierra() {
            super(60);
        }

        @Override
        boolean cumple(ServerPlayer p) {
            return rotos.getOrDefault(p.getUUID(), 0) >= 10;
        }

        @Override
        void alRomper(ServerPlayer p, BlockState estado) {
            if (TIERRA.contains(estado.getBlock())) {
                rotos.merge(p.getUUID(), 1, Integer::sum);
            }
        }
    }

    /** Lo que llega de los eventos del juego (Momentos los engancha): solo si el contador corre. */
    static void romper(Suceso s, ServerPlayer p, BlockState estado, int t) {
        if (s instanceof Prueba pr && pr.corre(t)) {
            pr.alRomper(p, estado);
        }
    }

    static void matar(Suceso s, Entity asesino, LivingEntity muerto, int t) {
        if (s instanceof Prueba pr && pr.corre(t) && asesino instanceof ServerPlayer p) {
            pr.alMatar(p, muerto);
        }
    }
}
