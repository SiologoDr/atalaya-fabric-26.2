package com.atalaya.cambios;

import net.fabricmc.fabric.api.event.lifecycle.v1.ServerTickEvents;
import net.minecraft.core.BlockPos;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.tags.BlockTags;
import net.minecraft.util.Mth;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.EntitySpawnReason;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.EntityTypes;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.biome.Biomes;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.phys.AABB;

/**
 * Los mobs de siempre que, con un cambio encendido, salen donde antes no: un aparecedor propio que, cada dos segundos y
 * junto a cada jugador, intenta sacar los que toquen (lejos de el, sobre suelo firme, con su sitio libre y sin pasar de
 * los que ya hay cerca). Asi se enciende y se apaga al momento, sin tocar los biomas.
 *
 * <pre>
 *   LOS MUERTOS BAJAN         zombis por el Nether, con cualquier luz
 *   BLAZES SUELTOS            blazes por todo el Nether
 *   HUESOS NEGROS             esqueletos wither por el Nether, y de noche en el mundo
 *   LA NOCHE HELADA           esqueletos glaciales y cenagosos, de noche en el mundo
 *   ESQUELETOS EN EL NETHER   esqueletos por el Nether, tambien encima de su techo
 *   LAS ARANAS SUBEN          aranas de cueva de noche en la superficie, y sobre el hielo con cualquier luz
 *   EL ABISMO DESPIERTA       wardens en la oscuridad profunda
 *   WARDENS EN LA SUPERFICIE  wardens de noche en la superficie
 *   TORMENTA EN LOS CREEPERS  creepers tambien de dia
 * </pre>
 */
public final class AparicionesExtra {

    private AparicionesExtra() {
    }

    static void registrar() {
        ServerTickEvents.END_SERVER_TICK.register(AparicionesExtra::tick);
    }

    private static void tick(MinecraftServer s) {
        if (s.getTickCount() % 40 != 17) {
            return;
        }
        for (ServerPlayer p : s.getPlayerList().getPlayers()) {
            if (p.isSpectator() || !p.isAlive()) {
                continue;
            }
            ServerLevel nivel = p.level();
            RandomSource r = nivel.getRandom();
            boolean nether = nivel.dimension() == Level.NETHER;
            boolean mundo = nivel.dimension() == Level.OVERWORLD;
            boolean noche = mundo && !nivel.isBrightOutside();
            if (nether) {
                if (CambiosDificultad.activo(Cambio.LOS_MUERTOS_BAJAN) && r.nextFloat() < 0.35F) {
                    intentar(nivel, p, EntityTypes.ZOMBIE, 8, Donde.CUALQUIERA);
                }
                if (CambiosDificultad.activo(Cambio.BLAZES_SUELTOS) && r.nextFloat() < 0.2F) {
                    intentar(nivel, p, EntityTypes.BLAZE, 4, Donde.CUALQUIERA);
                }
                if (CambiosDificultad.activo(Cambio.HUESOS_NEGROS) && r.nextFloat() < 0.2F) {
                    intentar(nivel, p, EntityTypes.WITHER_SKELETON, 4, Donde.CUALQUIERA);
                }
                if (CambiosDificultad.activo(Cambio.ESQUELETOS_EN_EL_NETHER) && r.nextFloat() < 0.3F) {
                    intentar(nivel, p, EntityTypes.SKELETON, 6, p.getY() > 127 ? Donde.TECHO : Donde.CUALQUIERA);
                }
            }
            if (mundo) {
                if (noche && CambiosDificultad.activo(Cambio.HUESOS_NEGROS) && r.nextFloat() < 0.12F) {
                    intentar(nivel, p, EntityTypes.WITHER_SKELETON, 3, Donde.SUPERFICIE);
                }
                if (noche && CambiosDificultad.activo(Cambio.LA_NOCHE_HELADA) && r.nextFloat() < 0.3F) {
                    intentar(nivel, p, r.nextBoolean() ? EntityTypes.STRAY : EntityTypes.BOGGED, 6, Donde.SUPERFICIE);
                }
                if (CambiosDificultad.activo(Cambio.LAS_ARANAS_SUBEN) && r.nextFloat() < 0.3F) {
                    intentar(nivel, p, EntityTypes.CAVE_SPIDER, 5, noche ? Donde.SUPERFICIE : Donde.HIELO);
                }
                if (CambiosDificultad.activo(Cambio.EL_ABISMO_DESPIERTA) && r.nextFloat() < 0.04F
                        && nivel.getBiome(p.blockPosition()).is(Biomes.DEEP_DARK)) {
                    intentar(nivel, p, EntityTypes.WARDEN, 1, Donde.CUALQUIERA);
                }
                if (noche && CambiosDificultad.activo(Cambio.WARDENS_EN_LA_SUPERFICIE) && r.nextFloat() < 0.02F) {
                    intentar(nivel, p, EntityTypes.WARDEN, 1, Donde.SUPERFICIE);
                }
                if (!noche && CambiosDificultad.activo(Cambio.CREEPERS_CARGADOS) && r.nextFloat() < 0.25F) {
                    intentar(nivel, p, EntityTypes.CREEPER, 4, Donde.SUPERFICIE);
                }
            }
        }
    }

    private enum Donde { CUALQUIERA, SUPERFICIE, TECHO, HIELO }

    /** Intenta sacar uno de esos entre 20 y 44 bloques del jugador, si no hay ya demasiados cerca. */
    private static void intentar(ServerLevel nivel, ServerPlayer p, EntityType<? extends Mob> tipo, int tope, Donde donde) {
        AABB zona = p.getBoundingBox().inflate(48.0, 24.0, 48.0);
        if (nivel.getEntities(tipo, zona, e -> true).size() >= tope) {
            return;
        }
        RandomSource r = nivel.getRandom();
        for (int intento = 0; intento < 6; intento++) {
            double a = r.nextDouble() * Mth.TWO_PI;
            double d = 20 + r.nextDouble() * 24;
            int x = Mth.floor(p.getX() + Math.cos(a) * d);
            int z = Mth.floor(p.getZ() + Math.sin(a) * d);
            BlockPos pos = switch (donde) {
                case SUPERFICIE, HIELO -> new BlockPos(x, nivel.getHeight(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, x, z), z);
                case TECHO -> new BlockPos(x, 128, z);
                case CUALQUIERA -> suelo(nivel, x, Mth.floor(p.getY()), z);
            };
            if (pos == null || !cabe(nivel, pos, tipo) || nivel.getNearestPlayer(pos.getX(), pos.getY(), pos.getZ(), 16, false) != null) {
                continue;
            }
            if (donde == Donde.HIELO && !nivel.getBlockState(pos.below()).is(BlockTags.ICE)) {
                continue;
            }
            if (donde == Donde.TECHO && !nivel.getBlockState(pos.below()).is(net.minecraft.world.level.block.Blocks.BEDROCK)) {
                continue;
            }
            tipo.spawn(nivel, pos, EntitySpawnReason.NATURAL);
            return;
        }
    }

    /** El primer suelo firme con sitio encima, buscando hacia arriba y hacia abajo desde la altura del jugador. */
    private static BlockPos suelo(ServerLevel nivel, int x, int y, int z) {
        for (int dy = 0; dy < 12; dy++) {
            for (int s : new int[]{-1, 1}) {
                BlockPos q = new BlockPos(x, y + s * dy, z);
                if (nivel.getBlockState(q.below()).isFaceSturdy(nivel, q.below(), net.minecraft.core.Direction.UP)
                        && nivel.getBlockState(q).isAir() && nivel.getBlockState(q.above()).isAir()) {
                    return q;
                }
            }
        }
        return null;
    }

    private static boolean cabe(ServerLevel nivel, BlockPos pos, EntityType<?> tipo) {
        int alto = Mth.ceil(tipo.getHeight());
        for (int i = 0; i < alto; i++) {
            if (!nivel.getBlockState(pos.above(i)).isAir() || !nivel.getFluidState(pos.above(i)).isEmpty()) {
                return false;
            }
        }
        return nivel.getBlockState(pos.below()).isFaceSturdy(nivel, pos.below(), net.minecraft.core.Direction.UP);
    }
}
