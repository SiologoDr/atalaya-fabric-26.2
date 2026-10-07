package com.atalaya.command;

import com.atalaya.Atalaya;
import com.mojang.authlib.GameProfile;
import com.mojang.brigadier.CommandDispatcher;
import com.mojang.brigadier.arguments.FloatArgumentType;
import com.mojang.brigadier.arguments.StringArgumentType;
import com.mojang.brigadier.context.CommandContext;
import net.fabricmc.fabric.api.entity.FakePlayer;
import net.fabricmc.loader.api.FabricLoader;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.Commands;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.phys.Vec3;

import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;

/**
 * Solo en el entorno de pruebas (con run/atalaya_fotos.flag): aliados de
 * mentira para probar las habilidades de grupo con un solo jugador. Todo lo
 * que miden sale en el registro con la palabra PRUEBA.
 *
 * <pre>
 *   /atalaya aliado &lt;nombre&gt; &lt;vida&gt;            un jugador falso donde estas, con esa vida
 *   /atalaya aliado_info &lt;nombre&gt;              su vida, absorcion, velocidad y efectos
 *   /atalaya aliado_dano &lt;nombre&gt; &lt;cantidad&gt; [tipo]  que reciba ese dano del bicho mas cercano
 *   /atalaya aliado_usa &lt;nombre&gt; &lt;arma&gt;      que use martillo, tridente, arco o espada
 *   /atalaya aliado_pega &lt;nombre&gt; &lt;cantidad&gt;  que pegue ese dano al ser vivo mas cercano
 *   /atalaya prueba_lista                       la habilidad de todos, lista otra vez
 * </pre>
 */
public final class PruebaAliados {

    private static final Map<String, Aliado> ALIADOS = new HashMap<>();

    /** Un jugador falso que si recibe dano (el de Fabric es invulnerable) y no se mueve. */
    private static final class Aliado extends FakePlayer {
        Aliado(ServerLevel nivel, GameProfile perfil) {
            super(nivel, perfil);
        }

        @Override
        public boolean isInvulnerableTo(ServerLevel nivel, DamageSource fuente) {
            return false;
        }
    }

    private PruebaAliados() {
    }

    public static boolean activo() {
        return Files.exists(FabricLoader.getInstance().getGameDir().resolve("atalaya_fotos.flag"));
    }

    public static void registrar(CommandDispatcher<CommandSourceStack> dispatcher) {
        if (!activo()) {
            return;
        }
        dispatcher.register(Commands.literal("atalaya")
                .then(Commands.literal("prueba_lista")
                        .requires(PruebaAliados::op)
                        .executes(ctx -> {
                            for (var p : ctx.getSource().getServer().getPlayerList().getPlayers()) {
                                p.setAttached(com.atalaya.habilidad.Habilidades.ESTADO, com.atalaya.habilidad.HabilidadEstado.NADA);
                            }
                            return 1;
                        }))
                .then(Commands.literal("aliado")
                        .requires(PruebaAliados::op)
                        .then(Commands.argument("nombre", StringArgumentType.word())
                                .then(Commands.argument("vida", FloatArgumentType.floatArg(1.0F, 20.0F))
                                        .executes(ctx -> crear(ctx.getSource(), nombre(ctx), FloatArgumentType.getFloat(ctx, "vida"))))))
                .then(Commands.literal("aliado_info")
                        .requires(PruebaAliados::op)
                        .then(Commands.argument("nombre", StringArgumentType.word()).executes(ctx -> info(nombre(ctx)))))
                .then(Commands.literal("aliado_dano")
                        .requires(PruebaAliados::op)
                        .then(Commands.argument("nombre", StringArgumentType.word())
                                .then(Commands.argument("cantidad", FloatArgumentType.floatArg(0.0F))
                                        .executes(ctx -> dano(nombre(ctx), FloatArgumentType.getFloat(ctx, "cantidad"), ""))
                                        .then(Commands.argument("tipo", StringArgumentType.word())
                                                .executes(ctx -> dano(nombre(ctx), FloatArgumentType.getFloat(ctx, "cantidad"),
                                                        StringArgumentType.getString(ctx, "tipo")))))))
                .then(Commands.literal("aliado_pega")
                        .requires(PruebaAliados::op)
                        .then(Commands.argument("nombre", StringArgumentType.word())
                                .then(Commands.argument("cantidad", FloatArgumentType.floatArg(0.0F))
                                        .executes(ctx -> pega(nombre(ctx), FloatArgumentType.getFloat(ctx, "cantidad"))))))
                .then(Commands.literal("aliado_usa")
                        .requires(PruebaAliados::op)
                        .then(Commands.argument("nombre", StringArgumentType.word())
                                .then(Commands.argument("arma", StringArgumentType.word())
                                        .executes(ctx -> usa(nombre(ctx), StringArgumentType.getString(ctx, "arma")))))));
    }

    /**
     * Que el aliado use un arma de rol: martillo o espada (golpea al bicho mas
     * cercano), tridente (se lo lanza) o arco (dispara al jugador de verdad mas
     * cercano, para probar la flecha que da a un aliado).
     */
    private static int usa(String nombre, String arma) {
        Aliado a = ALIADOS.get(nombre);
        if (a == null) {
            return 0;
        }
        ServerLevel nivel = (ServerLevel) a.level();
        com.atalaya.item.ArmadurasJefes.Tema tema = switch (arma) {
            case "tridente" -> com.atalaya.item.ArmadurasJefes.Tema.MAREAS;
            case "martillo" -> com.atalaya.item.ArmadurasJefes.Tema.JADE;
            case "arco" -> com.atalaya.item.ArmadurasJefes.Tema.VENDAVAL;
            default -> com.atalaya.item.ArmadurasJefes.Tema.SOLAR;
        };
        net.minecraft.world.item.ItemStack stack = new net.minecraft.world.item.ItemStack(com.atalaya.item.ArmadurasJefes.ARMAS.get(tema));
        a.setItemInHand(net.minecraft.world.InteractionHand.MAIN_HAND, stack);
        LivingEntity blanco = null;
        double mejor = 400.0;
        for (LivingEntity v : nivel.getEntitiesOfClass(LivingEntity.class, a.getBoundingBox().inflate(20.0),
                v -> v.isAlive() && (arma.equals("arco") ? v instanceof net.minecraft.server.level.ServerPlayer && !(v instanceof FakePlayer)
                        : !(v instanceof Player)))) {
            double d = v.distanceToSqr(a);
            if (d < mejor) {
                mejor = d;
                blanco = v;
            }
        }
        if (blanco == null) {
            return 0;
        }
        a.lookAt(net.minecraft.commands.arguments.EntityAnchorArgument.Anchor.EYES, blanco.getEyePosition());
        switch (arma) {
            case "tridente", "arco" -> {
                if (arma.equals("arco")) {
                    a.getInventory().add(new net.minecraft.world.item.ItemStack(net.minecraft.world.item.Items.ARROW, 8));
                }
                int dura = stack.getUseDuration(a);
                stack.getItem().releaseUsing(stack, nivel, a, dura - 25);
            }
            default -> {
                // El aliado no se actualiza solo: unos ticks para que coja el arma y cargue el golpe.
                for (int i = 0; i < 30; i++) {
                    a.doTick();
                }
                float antes = blanco.getHealth();
                a.attack(blanco);
                Atalaya.LOGGER.info("PRUEBA aliado {} pega {} con {} (dano del atributo {}); efectos del bicho: {}", nombre,
                        antes - blanco.getHealth(), arma, a.getAttributeValue(Attributes.ATTACK_DAMAGE),
                        blanco.getActiveEffects().stream().map(e -> e.getEffect().getRegisteredName()).toList());
            }
        }
        Atalaya.LOGGER.info("PRUEBA aliado {} usa {} contra {}", nombre, arma, blanco.getName().getString());
        return 1;
    }

    private static boolean op(CommandSourceStack f) {
        return Commands.LEVEL_GAMEMASTERS.check(f.permissions());
    }

    private static String nombre(CommandContext<CommandSourceStack> ctx) {
        return StringArgumentType.getString(ctx, "nombre");
    }

    private static int crear(CommandSourceStack fuente, String nombre, float vida) {
        ServerLevel nivel = fuente.getLevel();
        Aliado a = ALIADOS.computeIfAbsent(nombre, n -> new Aliado(nivel,
                new GameProfile(UUID.nameUUIDFromBytes(("atalaya-aliado-" + n).getBytes(StandardCharsets.UTF_8)), n)));
        Vec3 p = fuente.getPosition();
        a.snapTo(p.x, p.y, p.z, 0.0F, 0.0F);
        if (!nivel.players().contains(a)) {
            nivel.addNewPlayer(a);
        }
        a.setHealth(vida);
        Atalaya.LOGGER.info("PRUEBA aliado {} en {} con {} de vida", nombre, p, vida);
        return 1;
    }

    private static int info(String nombre) {
        Aliado a = ALIADOS.get(nombre);
        if (a == null) {
            return 0;
        }
        List<String> efectos = new ArrayList<>();
        for (MobEffectInstance e : a.getActiveEffects()) {
            efectos.add(e.getEffect().getRegisteredName() + " " + (e.getAmplifier() + 1) + " (" + e.getDuration() + " t)");
        }
        Atalaya.LOGGER.info("PRUEBA aliado {}: vida={} absorcion={} velocidad={} efectos={}", nombre, a.getHealth(),
                a.getAbsorptionAmount(), a.getAttributeValue(Attributes.MOVEMENT_SPEED), efectos);
        return 1;
    }

    /**
     * Sin tipo, golpe de bicho del mas cercano (o generico si no hay); con tipo,
     * ese dano de Atalaya (p. ej. aeralis_tornado) con el bicho como causante.
     */
    private static int dano(String nombre, float cantidad, String tipo) {
        Aliado a = ALIADOS.get(nombre);
        if (a == null) {
            return 0;
        }
        ServerLevel nivel = (ServerLevel) a.level();
        net.minecraft.world.entity.Mob bicho = null;
        double mejor = 1024.0;
        for (net.minecraft.world.entity.Mob m : nivel.getEntitiesOfClass(net.minecraft.world.entity.Mob.class, a.getBoundingBox().inflate(32.0))) {
            double d = m.distanceToSqr(a);
            if (d < mejor) {
                mejor = d;
                bicho = m;
            }
        }
        DamageSource fuente;
        if (bicho == null) {
            fuente = nivel.damageSources().generic();
        } else if (tipo.isEmpty()) {
            fuente = nivel.damageSources().mobAttack(bicho);
        } else {
            fuente = new DamageSource(nivel.registryAccess().lookupOrThrow(net.minecraft.core.registries.Registries.DAMAGE_TYPE)
                    .getOrThrow(net.minecraft.resources.ResourceKey.create(net.minecraft.core.registries.Registries.DAMAGE_TYPE,
                            net.minecraft.resources.Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, tipo))), bicho, bicho);
        }
        a.invulnerableTime = 0;
        a.hurtServer(nivel, fuente, cantidad);
        Atalaya.LOGGER.info("PRUEBA aliado {} recibe {} de {}", nombre, cantidad, fuente.getMsgId());
        return 1;
    }

    private static int pega(String nombre, float cantidad) {
        Aliado a = ALIADOS.get(nombre);
        if (a == null) {
            return 0;
        }
        ServerLevel nivel = (ServerLevel) a.level();
        LivingEntity blanco = null;
        double mejor = 100.0;
        for (LivingEntity v : nivel.getEntitiesOfClass(LivingEntity.class, a.getBoundingBox().inflate(10.0), v -> !(v instanceof Player))) {
            double d = v.distanceToSqr(a);
            if (d < mejor) {
                mejor = d;
                blanco = v;
            }
        }
        if (blanco != null) {
            blanco.invulnerableTime = 0;
            blanco.hurtServer(nivel, nivel.damageSources().playerAttack(a), cantidad);
        }
        return 1;
    }
}
