package com.atalaya.cambios;

import com.atalaya.Atalaya;
import net.fabricmc.fabric.api.attachment.v1.AttachmentRegistry;
import net.fabricmc.fabric.api.attachment.v1.AttachmentSyncPredicate;
import net.fabricmc.fabric.api.attachment.v1.AttachmentType;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerTickEvents;
import net.minecraft.core.BlockPos;
import net.minecraft.network.codec.ByteBufCodecs;
import net.minecraft.resources.Identifier;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.stats.Stats;
import net.minecraft.util.Mth;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.EntitySpawnReason;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.EntityTypes;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.levelgen.Heightmap;

import java.util.ArrayList;
import java.util.List;
import java.util.function.Supplier;

/**
 * INSOMNIO (DEDsafio 4, las pesadillas): cada jugador lleva un insomnio de 0 a 100 que sube mientras no duerme (el
 * tiempo desde el ultimo descanso: dos dias enteros sin dormir lo llenan) y solo baja durmiendo. Con la mitad, de noche
 * y al raso, bajan las pesadillas a buscarlo: cuanto mas alto, mas a menudo y mas a la vez.
 *
 * Las pesadillas son los mobs de la lista {@link #PESADILLAS} (los del bestiario se apuntan ahi); sin ellos, phantoms.
 */
public final class Insomnio {

    /** El insomnio de cada uno (0 a 100), que ve el suyo (InsomnioHud). */
    public static AttachmentType<Integer> NIVEL;
    /** Lo que baja del cielo en las pesadillas. */
    public static final List<Supplier<EntityType<? extends Mob>>> PESADILLAS = new ArrayList<>();
    private static final int TICKS_POR_PUNTO = 480;

    private Insomnio() {
    }

    static void registrar() {
        NIVEL = AttachmentRegistry.<Integer>builder()
                .initializer(() -> 0)
                .syncWith(ByteBufCodecs.VAR_INT, AttachmentSyncPredicate.targetOnly())
                .buildAndRegister(Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "insomnio"));
        ServerTickEvents.END_SERVER_TICK.register(Insomnio::tick);
    }

    public static int de(ServerPlayer p) {
        return p.getAttachedOrCreate(NIVEL);
    }

    private static void tick(MinecraftServer s) {
        if (s.getTickCount() % 20 != 3) {
            return;
        }
        boolean activo = CambiosDificultad.activo(Cambio.INSOMNIO);
        for (ServerPlayer p : s.getPlayerList().getPlayers()) {
            int nivel = 0;
            if (activo) {
                int sinDormir = p.getStats().getValue(Stats.CUSTOM.get(Stats.TIME_SINCE_REST));
                nivel = Mth.clamp(sinDormir / TICKS_POR_PUNTO, 0, 100);
            }
            if (p.getAttachedOrCreate(NIVEL) != nivel) {
                p.setAttached(NIVEL, nivel);
            }
            if (activo && nivel >= 50 && !p.isCreative() && !p.isSpectator() && p.isAlive()
                    && s.getTickCount() % 600 == 3) {
                pesadilla(p, nivel);
            }
        }
    }

    /** Una pesadilla: de noche, al raso; con mas insomnio, mas probable y mas grande. */
    private static void pesadilla(ServerPlayer p, int nivel) {
        ServerLevel mundo = p.level();
        if (mundo.dimension() != Level.OVERWORLD || mundo.isBrightOutside()) {
            return;
        }
        BlockPos pies = p.blockPosition();
        if (mundo.getHeight(Heightmap.Types.MOTION_BLOCKING, pies.getX(), pies.getZ()) > pies.getY() + 1) {
            return;
        }
        RandomSource r = p.getRandom();
        if (r.nextInt(100) > nivel - 30) {
            return;
        }
        int cuantos = 1 + (nivel >= 80 ? r.nextInt(3) : r.nextInt(2));
        for (int i = 0; i < cuantos; i++) {
            EntityType<? extends Mob> tipo = PESADILLAS.isEmpty() ? EntityTypes.PHANTOM
                    : PESADILLAS.get(r.nextInt(PESADILLAS.size())).get();
            double a = r.nextDouble() * Mth.TWO_PI;
            BlockPos donde = BlockPos.containing(p.getX() + Math.cos(a) * 12, p.getY() + 18 + r.nextInt(6),
                    p.getZ() + Math.sin(a) * 12);
            Mob m = tipo.spawn(mundo, donde, EntitySpawnReason.EVENT);
            if (m != null) {
                m.setTarget(p);
            }
        }
    }
}
