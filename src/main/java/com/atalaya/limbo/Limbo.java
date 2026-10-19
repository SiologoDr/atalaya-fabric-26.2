package com.atalaya.limbo;

import com.atalaya.Atalaya;
import com.atalaya.bestiario.Bestia;
import com.atalaya.bestiario.Bestias;
import com.atalaya.sonido.AtalayaSonidos;
import com.mojang.brigadier.builder.LiteralArgumentBuilder;
import net.fabricmc.fabric.api.entity.event.v1.ServerPlayerEvents;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerLifecycleEvents;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerTickEvents;
import net.minecraft.ChatFormatting;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.Commands;
import net.minecraft.core.BlockPos;
import net.minecraft.core.GlobalPos;
import net.minecraft.core.Registry;
import net.minecraft.core.particles.SimpleParticleType;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.ResourceKey;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.material.MapColor;
import net.minecraft.world.level.material.PushReaction;
import net.minecraft.world.level.storage.LevelData;
import org.jspecify.annotations.Nullable;

import java.util.List;
import java.util.Set;
import java.util.function.Function;

/**
 * El Limbo (DEDsafio 3 y 4): una dimension aparte, oscura y con niebla, que es un laberinto lleno de fantasmas. Te
 * mandan ahi (te «destierran») la hoz de la Parca Menor, mirar a la luna o el momento «todos al Limbo»; para volver
 * hay que encontrar la salida, una losa de luz en el suelo que cada cinco minutos cambia de sitio. Se la oye de lejos
 * (zumba) y le suben motas de luz. Al pisarla vuelves a donde estabas.
 *
 * <pre>
 *   la dimension   data/atalaya/dimension/limbo.json: vacia (plana, sin capas), con su niebla violeta, su musica y sin
 *                  cama ni ancla; el laberinto lo construye Laberinto al arrancar el servidor (una vez: LimboDatos)
 *   los bloques    piedra_limbo (muros y techo), suelo_limbo, farol_limbo (la luz fria de los muros) y salida_limbo;
 *                  ninguno se puede romper ni mover, y encima de los muros y del techo no sale nada
 *   la vuelta      donde estaba cada uno al entrar (dimension y sitio); si muere dentro, se olvida (reaparece donde le
 *                  toque, como siempre)
 *   las pruebas    /atalaya limbo ir | salir | salida | mover | rehacer
 * </pre>
 */
public final class Limbo {

    public static final ResourceKey<Level> LIMBO = ResourceKey.create(Registries.DIMENSION,
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "limbo"));

    /** Cada cuanto cambia la salida de sitio (ticks), y cada cuanto zumba. */
    private static final int CAMBIO = 6000;
    private static final int ZUMBIDO = 40;
    /** Lo lejos (en celdas) que sale uno de la salida al entrar, y la salida de los que estan dentro al moverse. */
    private static final int LEJOS = 9;

    public static Block PIEDRA;
    public static Block SUELO;
    public static Block FAROL;
    public static Block SALIDA;
    public static @Nullable SimpleParticleType LUZ;
    public static @Nullable SimpleParticleType BRUMA;
    public static SoundEvent MUSICA;
    public static SoundEvent SUSURRO;
    public static SoundEvent DESTIERRO;
    public static SoundEvent SALIDA_ZUMBA;
    public static SoundEvent CAMBIA;
    public static SoundEvent ESCAPA;

    private Limbo() {
    }

    // ------------------------------------------------------------------
    //  El registro
    // ------------------------------------------------------------------

    /** Sus sonidos, sus bloques y sus particulas; y los eventos (antes de las bestias que lo usan). */
    public static void registrar() {
        MUSICA = AtalayaSonidos.registrar("limbo.musica");
        SUSURRO = AtalayaSonidos.registrar("limbo.susurro");
        DESTIERRO = AtalayaSonidos.registrar("limbo.destierro");
        SALIDA_ZUMBA = AtalayaSonidos.registrar("limbo.salida");
        CAMBIA = AtalayaSonidos.registrar("limbo.cambia");
        ESCAPA = AtalayaSonidos.registrar("limbo.escapa");
        SoundType sonido = new SoundType(1.0F, 1.0F, AtalayaSonidos.registrar("limbo.bloque.romper"),
                AtalayaSonidos.registrar("limbo.bloque.paso"), AtalayaSonidos.registrar("limbo.bloque.poner"),
                AtalayaSonidos.registrar("limbo.bloque.golpe"), AtalayaSonidos.registrar("limbo.bloque.caida"));
        PIEDRA = bloque("piedra_limbo", Block::new, irrompible(sonido, MapColor.COLOR_PURPLE)
                .isValidSpawn((estado, nivel, pos, tipo) -> false));
        SUELO = bloque("suelo_limbo", Block::new, irrompible(sonido, MapColor.COLOR_BLACK));
        FAROL = bloque("farol_limbo", Block::new, irrompible(sonido, MapColor.COLOR_PURPLE)
                .lightLevel(estado -> 11).isValidSpawn((estado, nivel, pos, tipo) -> false));
        SALIDA = bloque("salida_limbo", SalidaLimbo::new, irrompible(sonido, MapColor.GOLD)
                .lightLevel(estado -> 15).isValidSpawn((estado, nivel, pos, tipo) -> false));
        LUZ = Bestias.particulaSuelta("bestia_limbo_luz", Bestia.Vuelo.SUBE, true);
        BRUMA = Bestias.particulaSuelta("bestia_limbo_bruma", Bestia.Vuelo.FLOTA, false);
        ServerLifecycleEvents.SERVER_STARTED.register(Limbo::alArrancar);
        ServerTickEvents.END_SERVER_TICK.register(Limbo::tick);
        // Si muere dentro, la vuelta se olvida (reaparece donde le toque).
        ServerPlayerEvents.AFTER_RESPAWN.register((viejo, nuevo, vivo) -> {
            if (!vivo) {
                LimboDatos d = LimboDatos.de(nuevo.level().getServer());
                if (d.vueltas.remove(nuevo.getUUID()) != null) {
                    d.setDirty();
                }
            }
        });
    }

    private static BlockBehaviour.Properties irrompible(SoundType sonido, MapColor color) {
        return BlockBehaviour.Properties.of().mapColor(color).strength(-1.0F, 3600000.0F).noLootTable().sound(sonido)
                .pushReaction(PushReaction.BLOCK);
    }

    private static Block bloque(String nombre, Function<BlockBehaviour.Properties, Block> fabrica,
                                BlockBehaviour.Properties propiedades) {
        ResourceKey<Block> clave = ResourceKey.create(Registries.BLOCK, Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, nombre));
        return Registry.register(BuiltInRegistries.BLOCK, clave, fabrica.apply(propiedades.setId(clave)));
    }

    // ------------------------------------------------------------------
    //  Lo que se pregunta
    // ------------------------------------------------------------------

    public static boolean enLimbo(Entity e) {
        return e.level().dimension() == LIMBO;
    }

    public static @Nullable ServerLevel nivel(MinecraftServer s) {
        return s.getLevel(LIMBO);
    }

    /** Donde esta ahora la salida (el centro de su celda, a ras de suelo), o null si aun no hay laberinto. */
    public static @Nullable BlockPos salida(MinecraftServer s) {
        LimboDatos d = LimboDatos.de(s);
        return d.salidaI < 0 ? null : Laberinto.centro(d.salidaI, d.salidaJ);
    }

    // ------------------------------------------------------------------
    //  Entrar y salir
    // ------------------------------------------------------------------

    /**
     * Destierra a un jugador al Limbo: se apunta donde estaba (para volver) y aparece en una celda lejos de la salida.
     * Si ya esta dentro, no pasa nada (la hoz de la Parca Menor solo hace dano).
     */
    public static boolean desterrar(ServerPlayer p) {
        MinecraftServer s = p.level().getServer();
        ServerLevel limbo = nivel(s);
        if (limbo == null || enLimbo(p) || p.isSpectator()) {
            return false;
        }
        LimboDatos d = asegurar(limbo);
        d.vueltas.put(p.getUUID(), GlobalPos.of(p.level().dimension(), p.blockPosition()));
        d.setDirty();
        BlockPos destino = celdaLejos(limbo.getRandom(), d.salidaI, d.salidaJ, List.of());
        p.teleportTo(limbo, destino.getX() + 0.5, destino.getY(), destino.getZ() + 0.5, Set.of(),
                p.getYRot(), 0.0F, true);
        p.setDeltaMovement(net.minecraft.world.phys.Vec3.ZERO);
        p.fallDistance = 0.0F;
        limbo.playSound(null, p.getX(), p.getY(), p.getZ(), DESTIERRO, SoundSource.HOSTILE, 1.2F, 1.0F);
        s.getPlayerList().broadcastSystemMessage(Component.translatable("atalaya.limbo.desterrado", p.getDisplayName())
                .withStyle(ChatFormatting.DARK_PURPLE), false);
        return true;
    }

    /** Lo saca del Limbo: a donde estaba al entrar (o a donde reaparece, si no hay vuelta apuntada). */
    public static void salir(ServerPlayer p) {
        MinecraftServer s = p.level().getServer();
        if (!enLimbo(p)) {
            return;
        }
        LimboDatos d = LimboDatos.de(s);
        GlobalPos vuelta = d.vueltas.remove(p.getUUID());
        d.setDirty();
        ServerLevel destino = vuelta != null ? s.getLevel(vuelta.dimension()) : null;
        BlockPos pos;
        if (destino == null || destino.dimension() == LIMBO) {
            LevelData.RespawnData r = s.getRespawnData();
            destino = s.getLevel(r.dimension()) != null ? s.getLevel(r.dimension()) : s.overworld();
            pos = r.pos();
        } else {
            pos = vuelta.pos();
        }
        p.teleportTo(destino, pos.getX() + 0.5, pos.getY(), pos.getZ() + 0.5, Set.of(), p.getYRot(), p.getXRot(), true);
        p.setDeltaMovement(net.minecraft.world.phys.Vec3.ZERO);
        p.fallDistance = 0.0F;
        destino.playSound(null, p.getX(), p.getY(), p.getZ(), ESCAPA, SoundSource.PLAYERS, 1.0F, 1.0F);
        s.getPlayerList().broadcastSystemMessage(Component.translatable("atalaya.limbo.escapo", p.getDisplayName())
                .withStyle(ChatFormatting.LIGHT_PURPLE), false);
    }

    /** Una celda al azar lejos de la salida y de esos jugadores (si se puede; si no, cualquiera que no sea la salida). */
    private static BlockPos celdaLejos(RandomSource azar, int si, int sj, List<ServerPlayer> lejosDe) {
        for (int intento = 0; intento < 60; intento++) {
            int i = azar.nextInt(Laberinto.CELDAS);
            int j = azar.nextInt(Laberinto.CELDAS);
            if (Math.max(Math.abs(i - si), Math.abs(j - sj)) < LEJOS) {
                continue;
            }
            boolean cerca = false;
            for (ServerPlayer p : lejosDe) {
                int pi = Laberinto.celdaI(p.getX());
                int pj = Laberinto.celdaJ(p.getZ());
                if (pi >= 0 && pj >= 0 && Math.max(Math.abs(i - pi), Math.abs(j - pj)) < LEJOS) {
                    cerca = true;
                    break;
                }
            }
            if (!cerca) {
                return Laberinto.centro(i, j);
            }
        }
        int i = (si + Laberinto.CELDAS / 2) % Laberinto.CELDAS;
        return Laberinto.centro(i, (sj + Laberinto.CELDAS / 2) % Laberinto.CELDAS);
    }

    // ------------------------------------------------------------------
    //  El laberinto y la salida
    // ------------------------------------------------------------------

    private static void alArrancar(MinecraftServer s) {
        ServerLevel limbo = nivel(s);
        if (limbo != null) {
            asegurar(limbo);
        }
    }

    /** Que este construido (y con la version de ahora); devuelve sus datos. */
    static LimboDatos asegurar(ServerLevel limbo) {
        LimboDatos d = LimboDatos.de(limbo.getServer());
        if (d.version != Laberinto.VERSION) {
            rehacer(limbo, d);
        }
        return d;
    }

    private static void rehacer(ServerLevel limbo, LimboDatos d) {
        long t0 = System.currentTimeMillis();
        if (d.semilla == 0L) {
            d.semilla = limbo.getRandom().nextLong() | 1L;
        }
        RandomSource azar = RandomSource.create(d.semilla);
        d.salidaI = azar.nextInt(Laberinto.CELDAS);
        d.salidaJ = azar.nextInt(Laberinto.CELDAS);
        Laberinto.construir(limbo, d.semilla, d.salidaI, d.salidaJ);
        d.version = Laberinto.VERSION;
        d.movida = limbo.getServer().getTickCount();
        d.setDirty();
        Atalaya.LOGGER.info("El laberinto del Limbo, construido en {} ms", System.currentTimeMillis() - t0);
    }

    /** Mueve la salida a otra celda, lejos de donde estaba y de los que estan dentro; suena en todo el Limbo. */
    static void moverSalida(ServerLevel limbo) {
        LimboDatos d = asegurar(limbo);
        List<ServerPlayer> dentro = limbo.players();
        BlockPos nueva = celdaLejos(limbo.getRandom(), d.salidaI, d.salidaJ, dentro);
        Laberinto.ponerSalida(limbo, d.salidaI, d.salidaJ, false);
        d.salidaI = Laberinto.celdaI(nueva.getX());
        d.salidaJ = Laberinto.celdaJ(nueva.getZ());
        Laberinto.ponerSalida(limbo, d.salidaI, d.salidaJ, true);
        d.movida = limbo.getServer().getTickCount();
        d.setDirty();
        for (ServerPlayer p : dentro) {
            limbo.playSound(null, p.getX(), p.getY(), p.getZ(), CAMBIA, SoundSource.AMBIENT, 1.0F, 1.0F);
            p.sendSystemMessage(Component.translatable("atalaya.limbo.cambia").withStyle(ChatFormatting.DARK_PURPLE));
        }
    }

    // ------------------------------------------------------------------
    //  El tick
    // ------------------------------------------------------------------

    private static void tick(MinecraftServer s) {
        ServerLevel limbo = nivel(s);
        if (limbo == null || limbo.players().isEmpty()) {
            return;
        }
        LimboDatos d = LimboDatos.de(s);
        int t = s.getTickCount();
        if (d.salidaI >= 0) {
            BlockPos c = Laberinto.centro(d.salidaI, d.salidaJ);
            if (t % ZUMBIDO == 0) {
                limbo.playSound(null, c.getX() + 0.5, c.getY() + 0.5, c.getZ() + 0.5, SALIDA_ZUMBA, SoundSource.AMBIENT,
                        4.0F, 1.0F);
            }
            if (t % 3 == 0 && LUZ != null) {
                limbo.sendParticles(LUZ, c.getX() + 0.5, c.getY() + 0.3, c.getZ() + 0.5, 3, 1.2, 0.2, 1.2, 0.02);
            }
            if (t - d.movida >= CAMBIO) {
                moverSalida(limbo);
            }
        }
        for (ServerPlayer p : limbo.players()) {
            // La bruma: alguna que otra voluta cerca de cada uno.
            if (t % 8 == 0 && BRUMA != null) {
                RandomSource r = p.getRandom();
                limbo.sendParticles(p, BRUMA, false, false, p.getX() + (r.nextDouble() - 0.5) * 12, p.getY() + r.nextDouble() * 3,
                        p.getZ() + (r.nextDouble() - 0.5) * 12, 1, 0.3, 0.2, 0.3, 0.0);
            }
            // Si alguien se sale (vuela, cae al vacio...), de vuelta a una celda.
            if (!p.isSpectator() && !p.isCreative() && !Laberinto.dentro(p.getX(), p.getY(), p.getZ())) {
                BlockPos c = celdaLejos(p.getRandom(), d.salidaI, d.salidaJ, List.of());
                p.teleportTo(limbo, c.getX() + 0.5, c.getY(), c.getZ() + 0.5, Set.of(), p.getYRot(), p.getXRot(), true);
                p.fallDistance = 0.0F;
            }
        }
    }

    // ------------------------------------------------------------------
    //  Las pruebas
    // ------------------------------------------------------------------

    /** /atalaya limbo ir | salir | salida | mover | rehacer */
    public static LiteralArgumentBuilder<CommandSourceStack> orden() {
        return Commands.literal("limbo")
                .requires(src -> Commands.LEVEL_GAMEMASTERS.check(src.permissions()))
                .then(Commands.literal("ir").executes(ctx -> desterrar(ctx.getSource().getPlayerOrException()) ? 1 : 0))
                .then(Commands.literal("salir").executes(ctx -> {
                    salir(ctx.getSource().getPlayerOrException());
                    return 1;
                }))
                .then(Commands.literal("salida").executes(ctx -> {
                    ServerPlayer p = ctx.getSource().getPlayerOrException();
                    BlockPos c = salida(ctx.getSource().getServer());
                    ServerLevel limbo = nivel(ctx.getSource().getServer());
                    if (c == null || limbo == null) {
                        return 0;
                    }
                    p.teleportTo(limbo, c.getX() + 0.5, c.getY() + 0.2, c.getZ() + 2.0, Set.of(), 180.0F, 30.0F, true);
                    return 1;
                }))
                .then(Commands.literal("mover").executes(ctx -> {
                    ServerLevel limbo = nivel(ctx.getSource().getServer());
                    if (limbo != null) {
                        moverSalida(limbo);
                    }
                    return 1;
                }))
                .then(Commands.literal("rehacer").executes(ctx -> {
                    ServerLevel limbo = nivel(ctx.getSource().getServer());
                    if (limbo != null) {
                        LimboDatos d = LimboDatos.de(ctx.getSource().getServer());
                        d.semilla = 0L;
                        rehacer(limbo, d);
                    }
                    return 1;
                }));
    }
}
