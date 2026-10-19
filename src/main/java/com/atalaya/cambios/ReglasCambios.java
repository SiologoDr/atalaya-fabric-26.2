package com.atalaya.cambios;

import com.atalaya.Atalaya;
import net.fabricmc.fabric.api.entity.event.v1.ServerLivingEntityEvents;
import net.fabricmc.fabric.api.entity.event.v1.ServerPlayerEvents;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerEntityEvents;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerTickEvents;
import net.fabricmc.fabric.api.event.player.PlayerBlockBreakEvents;
import net.fabricmc.fabric.api.event.player.UseBlockCallback;
import net.fabricmc.fabric.api.event.player.UseEntityCallback;
import net.fabricmc.fabric.api.loot.v3.LootTableEvents;
import net.fabricmc.fabric.api.networking.v1.ServerPlayConnectionEvents;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.ResourceKey;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.tags.BlockTags;
import net.minecraft.tags.ItemTags;
import net.minecraft.util.Mth;
import net.minecraft.util.RandomSource;
import net.minecraft.util.SpawnUtil;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.damagesource.DamageType;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntitySpawnReason;
import net.minecraft.world.entity.EntityTypes;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.AttributeInstance;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.animal.Animal;
import net.minecraft.world.entity.animal.cow.AbstractCow;
import net.minecraft.world.entity.animal.goat.Goat;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.entity.monster.Creeper;
import net.minecraft.world.entity.monster.Phantom;
import net.minecraft.world.entity.monster.spider.Spider;
import net.minecraft.world.entity.monster.warden.Warden;
import net.minecraft.world.entity.monster.Witch;
import net.minecraft.world.entity.monster.zombie.Zombie;
import net.minecraft.world.entity.monster.zombie.ZombifiedPiglin;
import net.minecraft.world.entity.monster.piglin.Piglin;
import net.minecraft.world.entity.npc.villager.AbstractVillager;
import net.minecraft.world.entity.npc.villager.Villager;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.BeehiveBlock;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.gamerules.GameRules;
import net.minecraft.world.level.storage.loot.parameters.LootContextParams;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;

import java.util.ArrayList;
import java.util.List;

/**
 * Lo que hace cada cambio de dificultad: los eventos que miran si esta encendido (CambiosDificultad.activo), lo que se
 * hace en cada tick y lo que se hace al encenderlo o al apagarlo. Lo que no tiene evento de Fabric va en los mixins de
 * com.atalaya.mixin.cambios; el dano, en DanoCambios; los mobs de siempre que salen donde antes no, en
 * AparicionesExtra; la plaga y el insomnio, en sus clases.
 */
public final class ReglasCambios {

    public static final ResourceKey<DamageType> TRAMPA = ResourceKey.create(Registries.DAMAGE_TYPE,
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "cambio_trampa"));
    public static final ResourceKey<DamageType> GAS = ResourceKey.create(Registries.DAMAGE_TYPE,
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "cambio_gas"));
    private static final Identifier PROTA_VIDA = Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "cambio_protagonista");
    private static final Identifier ENCOGIDO = Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "cambio_encogidos");
    /** La marca de lo que ya se le hizo a un mob (para no repetirlo cada vez que se carga). */
    private static final String MARCA = "atalaya_cambios";

    private ReglasCambios() {
    }

    static void registrar() {
        LootTableEvents.MODIFY_DROPS.register((tabla, contexto, drops) -> {
            Entity quien = contexto.getOptionalParameter(LootContextParams.THIS_ENTITY);
            // Ni un totem mas: se quitan de lo que sueltan los evocadores (al momento, sin recargar las tablas).
            if (CambiosDificultad.activo(Cambio.NI_UN_TOTEM_MAS) && quien != null && quien.getType() == EntityTypes.EVOKER) {
                drops.removeIf(p -> p.is(Items.TOTEM_OF_UNDYING));
            }
            // Piglins generosos: unas pepitas de oro.
            if (CambiosDificultad.activo(Cambio.PIGLINS_GENEROSOS) && quien instanceof Piglin p) {
                drops.add(new ItemStack(Items.GOLD_NUGGET, 2 + p.getRandom().nextInt(5)));
            }
            // Bosques sin futuro: las hojas no sueltan brotes (ni propagulos).
            BlockState bloque = contexto.getOptionalParameter(LootContextParams.BLOCK_STATE);
            if (CambiosDificultad.activo(Cambio.BOSQUES_SIN_FUTURO) && bloque != null && bloque.is(BlockTags.LEAVES)) {
                drops.removeIf(p -> p.is(ItemTags.SAPLINGS) || p.is(Items.MANGROVE_PROPAGULE));
            }
        });

        // Vacas secas: el cubo no saca leche de vacas, champinacas ni cabras.
        UseEntityCallback.EVENT.register((jugador, mundo, mano, quien, golpe) -> {
            if (CambiosDificultad.activo(Cambio.VACAS_SECAS) && jugador.getItemInHand(mano).is(Items.BUCKET)
                    && (quien instanceof AbstractCow || quien instanceof Goat)) {
                return InteractionResult.FAIL;
            }
            return InteractionResult.PASS;
        });

        // Panales trampa: ni miel ni panal (el frasco y las tijeras no hacen nada en ellos).
        UseBlockCallback.EVENT.register((jugador, mundo, mano, golpe) -> {
            if (CambiosDificultad.activo(Cambio.PANALES_TRAMPA)
                    && mundo.getBlockState(golpe.getBlockPos()).getBlock() instanceof BeehiveBlock) {
                ItemStack en = jugador.getItemInHand(mano);
                if (en.is(Items.GLASS_BOTTLE) || en.is(Items.SHEARS)) {
                    return InteractionResult.FAIL;
                }
            }
            return InteractionResult.PASS;
        });

        // Generadores eternos: no se rompen (en creativo, si).
        PlayerBlockBreakEvents.BEFORE.register((mundo, jugador, pos, estado, be) ->
                !(CambiosDificultad.activo(Cambio.SPAWNERS_ETERNOS) && !jugador.isCreative()
                        && (estado.is(Blocks.SPAWNER) || estado.is(Blocks.TRIAL_SPAWNER))));

        PlayerBlockBreakEvents.AFTER.register((mundo, jugador, pos, estado, be) -> {
            if (!(mundo instanceof ServerLevel nivel)) {
                return;
            }
            // Panales trampa: estallan al romperlos.
            if (CambiosDificultad.activo(Cambio.PANALES_TRAMPA) && estado.getBlock() instanceof BeehiveBlock) {
                nivel.explode(null, pos.getX() + 0.5, pos.getY() + 0.5, pos.getZ() + 0.5, 3.0F, Level.ExplosionInteraction.BLOCK);
            }
            // Nidos ocultos: de la telarana rota puede saltar una arana de cueva.
            if (CambiosDificultad.activo(Cambio.NIDOS_OCULTOS) && estado.is(Blocks.COBWEB) && nivel.getRandom().nextFloat() < 0.4F) {
                var arana = EntityTypes.CAVE_SPIDER.spawn(nivel, pos, EntitySpawnReason.EVENT);
                if (arana != null) {
                    arana.setTarget(jugador);
                }
            }
        });

        ServerLivingEntityEvents.AFTER_DAMAGE.register((victima, fuente, dado, recibido, bloqueado) -> {
            if (!(victima.level() instanceof ServerLevel nivel) || recibido <= 0.0F) {
                return;
            }
            Entity atacante = fuente.getDirectEntity();
            if (victima instanceof ServerPlayer p) {
                if (CambiosDificultad.activo(Cambio.TELARANA_EN_LOS_PIES) && atacante instanceof Spider) {
                    telarana(nivel, p.blockPosition());
                }
                if (CambiosDificultad.activo(Cambio.PHANTOMS_LADRONES) && atacante instanceof Phantom) {
                    phantomLadron(p);
                }
                if (CambiosDificultad.activo(Cambio.MORDISCO_PUTRIDO) && atacante instanceof Zombie
                        && !(atacante instanceof ZombifiedPiglin)) {
                    Plaga.contagiar(p);
                }
            }
        });

        ServerLivingEntityEvents.AFTER_DEATH.register((muerto, fuente) -> {
            if (!(muerto.level() instanceof ServerLevel nivel)) {
                return;
            }
            if (CambiosDificultad.activo(Cambio.TELARANA_EN_LOS_PIES) && muerto instanceof Spider) {
                telarana(nivel, muerto.blockPosition());
            }
            if (CambiosDificultad.activo(Cambio.EL_ABISMO_DESPIERTA) && muerto instanceof Warden) {
                BlockPos pos = muerto.blockPosition();
                if (nivel.getBlockState(pos).canBeReplaced()) {
                    nivel.setBlockAndUpdate(pos, Blocks.SCULK_SHRIEKER.defaultBlockState()
                            .setValue(net.minecraft.world.level.block.SculkShriekerBlock.CAN_SUMMON, true));
                }
            }
            if (CambiosDificultad.activo(Cambio.CADA_MUERTE_CUENTA) && muerto instanceof ServerPlayer caido) {
                for (ServerPlayer vivo : nivel.getServer().getPlayerList().getPlayers()) {
                    if (vivo != caido && vivo.isAlive() && !vivo.isSpectator() && !vivo.isCreative()) {
                        creeperDeUnCorazon(vivo);
                    }
                }
            }
        });

        // Lo que se le pone a los mobs que aparecen (o que se cargan sin tenerlo).
        ServerEntityEvents.ENTITY_LOAD.register((entidad, mundo) -> EquipoMobs.alCargar(entidad));

        ServerPlayConnectionEvents.JOIN.register((manejador, envio, s) -> alEntrar(manejador.getPlayer()));
        ServerPlayerEvents.AFTER_RESPAWN.register((viejo, nuevo, vivo) -> alEntrar(nuevo));
        ServerTickEvents.END_SERVER_TICK.register(ReglasCambios::tick);
        Plaga.registrar();
        Insomnio.registrar();
        Encogidos.registrar();
        AparicionesExtra.registrar();
    }

    // ------------------------------------------------------------------
    //  Al encender y al apagar
    // ------------------------------------------------------------------

    /** Lo que se hace al encender uno (lo que no se pregunta solo). */
    static void alEncender(MinecraftServer s, Cambio c) {
        switch (c) {
            case HERIDAS_ABIERTAS -> {
                GameRules reglas = s.overworld().getGameRules();
                CambiosDificultad.recordarAntes(s, c, reglas.get(GameRules.NATURAL_HEALTH_REGENERATION));
                reglas.set(GameRules.NATURAL_HEALTH_REGENERATION, false, s);
            }
            case EXTINCION -> gasDeExtincion(s);
            case ENCOGIDOS -> Encogidos.elegir(s);
            case PROTAGONISTA, MAL_AGUERO -> {
                for (ServerPlayer p : s.getPlayerList().getPlayers()) {
                    alEntrar(p);
                }
            }
            case LA_PLAGA -> Plaga.alEncender(s);
            default -> {
            }
        }
        if (EquipoMobs.tocaMobs(c)) {
            EquipoMobs.aplicarCargados(s, c);
        }
    }

    /** Lo que se deshace al apagarlo. */
    static void alApagar(MinecraftServer s, Cambio c) {
        switch (c) {
            case HERIDAS_ABIERTAS -> {
                Boolean antes = CambiosDificultad.antes(s, c);
                s.overworld().getGameRules().set(GameRules.NATURAL_HEALTH_REGENERATION, antes == null || antes, s);
            }
            case ENCOGIDOS -> Encogidos.soltar(s);
            case PROTAGONISTA -> {
                for (ServerPlayer p : s.getPlayerList().getPlayers()) {
                    protagonista(p, false);
                }
            }
            case MAL_AGUERO -> {
                for (ServerPlayer p : s.getPlayerList().getPlayers()) {
                    p.removeEffect(MobEffects.BAD_OMEN);
                }
            }
            case LA_PLAGA -> Plaga.alApagar(s);
            default -> {
            }
        }
        if (EquipoMobs.tocaMobs(c)) {
            EquipoMobs.quitarCargados(s, c);
        }
    }

    /** Quien entra o reaparece: lo que le toca de los cambios encendidos. */
    private static void alEntrar(ServerPlayer p) {
        protagonista(p, CambiosDificultad.activo(Cambio.PROTAGONISTA));
        Encogidos.alEntrar(p);
        if (CambiosDificultad.activo(Cambio.MAL_AGUERO)) {
            malAguero(p);
        }
        Plaga.alEntrar(p);
    }

    // ------------------------------------------------------------------
    //  Cada tick
    // ------------------------------------------------------------------

    private static void tick(MinecraftServer s) {
        int t = s.getTickCount();
        Estalactitas.tick(t);
        for (ServerPlayer p : s.getPlayerList().getPlayers()) {
            if (!p.isAlive() || p.isSpectator()) {
                continue;
            }
            boolean creativo = p.isCreative();
            ServerLevel nivel = p.level();
            // Piedra ardiente: el magma por cualquier lado.
            if (!creativo && CambiosDificultad.activo(Cambio.PIEDRA_ARDIENTE) && tocaMagma(p)) {
                trampa(p, p.blockPosition());
            }
            if (t % 5 == 0 && CambiosDificultad.activo(Cambio.LAVA_SIN_TREGUA) && p.isInLava()) {
                p.removeEffect(MobEffects.FIRE_RESISTANCE);
            }
            if (t % 10 == 0 && !creativo && CambiosDificultad.activo(Cambio.EL_NETHER_NO_PERDONA)
                    && nivel.dimension() == Level.NETHER && !p.isInWater()) {
                if (!armaduraCompleta(p) || p.getRemainingFireTicks() > 0) {
                    p.setRemainingFireTicks(Math.max(p.getRemainingFireTicks(), 60));
                }
            }
            if (t % 20 == 0 && !creativo) {
                gas(p, nivel);
            }
            if (t % 100 == 0) {
                if (CambiosDificultad.activo(Cambio.MAL_AGUERO)) {
                    malAguero(p);
                }
                if (CambiosDificultad.activo(Cambio.PROTAGONISTA)) {
                    protagonista(p, true);
                }
            }
            if (t % 20 == 7 && !creativo && CambiosDificultad.activo(Cambio.TECHOS_QUE_CAEN)) {
                Estalactitas.quizas(p, nivel);
            }
            if (t % 200 == 13 && CambiosDificultad.activo(Cambio.SE_PUDRE_LA_CARNE)) {
                CarnePodrida.revisar(p);
            }
            if (t % 4 == 0 && !creativo && CambiosDificultad.activo(Cambio.NO_MIRES_AL_SOL)) {
                MirarAlCielo.sol(p);
            }
        }
    }

    private static boolean tocaMagma(Player p) {
        AABB caja = p.getBoundingBox().inflate(0.02);
        BlockPos a = BlockPos.containing(caja.minX, caja.minY, caja.minZ);
        BlockPos b = BlockPos.containing(caja.maxX, caja.maxY, caja.maxZ);
        for (BlockPos q : BlockPos.betweenClosed(a, b)) {
            if (p.level().getBlockState(q).is(Blocks.MAGMA_BLOCK)) {
                return true;
            }
        }
        return false;
    }

    private static boolean armaduraCompleta(Player p) {
        for (EquipmentSlot s : new EquipmentSlot[]{EquipmentSlot.HEAD, EquipmentSlot.CHEST, EquipmentSlot.LEGS, EquipmentSlot.FEET}) {
            if (p.getItemBySlot(s).isEmpty()) {
                return false;
            }
        }
        return true;
    }

    /** El gas por encima de la capa 150 (o de la 130): hace dano hasta matar. Solo en el mundo de arriba. */
    private static void gas(ServerPlayer p, ServerLevel nivel) {
        int techo = CambiosDificultad.activo(Cambio.EL_GAS_BAJA) ? 130 : CambiosDificultad.activo(Cambio.TECHO_DE_GAS) ? 150 : -1;
        if (techo < 0 || nivel.dimension() != Level.OVERWORLD || p.getY() < techo) {
            return;
        }
        DamageSource fuente = new DamageSource(nivel.registryAccess().lookupOrThrow(Registries.DAMAGE_TYPE).getOrThrow(GAS));
        p.hurtServer(nivel, fuente, 2.0F + (float) Math.min(6.0, (p.getY() - techo) / 10.0));
        p.addEffect(new MobEffectInstance(MobEffects.NAUSEA, 120, 0, false, false, false));
        p.sendOverlayMessage(Component.literal("El aire aquí arriba es veneno: ¡baja!").withStyle(st -> st.withColor(0x9AD04A)));
    }

    private static void malAguero(ServerPlayer p) {
        if (!p.hasEffect(MobEffects.BAD_OMEN) && !p.hasEffect(MobEffects.RAID_OMEN)) {
            p.addEffect(new MobEffectInstance(MobEffects.BAD_OMEN, MobEffectInstance.INFINITE_DURATION, 0, false, false, true));
        }
    }

    /** Protagonista: tres corazones, sin hambre y con Fuerza III (o se le quita). */
    private static void protagonista(ServerPlayer p, boolean poner) {
        AttributeInstance vida = p.getAttribute(Attributes.MAX_HEALTH);
        if (vida == null) {
            return;
        }
        if (poner) {
            if (!vida.hasModifier(PROTA_VIDA)) {
                vida.addPermanentModifier(new AttributeModifier(PROTA_VIDA, -14.0, AttributeModifier.Operation.ADD_VALUE));
                if (p.getHealth() > p.getMaxHealth()) {
                    p.setHealth(p.getMaxHealth());
                }
            }
            p.addEffect(new MobEffectInstance(MobEffects.STRENGTH, 220, 2, false, false, true));
            p.addEffect(new MobEffectInstance(MobEffects.SATURATION, 220, 0, false, false, false));
        } else if (vida.hasModifier(PROTA_VIDA)) {
            vida.removeModifier(PROTA_VIDA);
            p.removeEffect(MobEffects.STRENGTH);
        }
    }

    // ------------------------------------------------------------------
    //  Ayudas que usan los mixins y los eventos
    // ------------------------------------------------------------------

    /** Una trampa mortal (boton, puerta, placa, magma): un dano que ninguna armadura para (un totem si salva). */
    public static void trampa(Player jugador, BlockPos pos) {
        if (!(jugador.level() instanceof ServerLevel nivel) || jugador.isCreative() || jugador.isSpectator()
                || !jugador.isAlive()) {
            return;
        }
        DamageSource fuente = new DamageSource(nivel.registryAccess().lookupOrThrow(Registries.DAMAGE_TYPE).getOrThrow(TRAMPA));
        jugador.hurtServer(nivel, fuente, 4.0E9F);
    }

    /** CARA O CRUZ: el totem ha salido cruz. */
    public static void totemFallido(LivingEntity quien) {
        if (quien instanceof ServerPlayer p) {
            p.sendSystemMessage(Component.literal("La moneda salió cruz: el tótem no te ha salvado.")
                    .withStyle(st -> st.withColor(0xFFD23A)));
        }
    }

    /** TRATOS MALDITOS: un aquelarre de tres a cinco brujas a por quien ha tratado. */
    public static void aquelarre(ServerLevel nivel, AbstractVillager aldeano) {
        Player quien = aldeano.getTradingPlayer();
        if (quien == null) {
            quien = nivel.getNearestPlayer(aldeano, 8.0);
        }
        if (quien == null) {
            return;
        }
        RandomSource r = nivel.getRandom();
        int n = 3 + r.nextInt(3);
        for (int i = 0; i < n; i++) {
            double a = r.nextDouble() * Mth.TWO_PI;
            double d = 12 + r.nextDouble() * 8;
            BlockPos cerca = BlockPos.containing(quien.getX() + Math.cos(a) * d, quien.getY(), quien.getZ() + Math.sin(a) * d);
            final Player presa = quien;
            SpawnUtil.trySpawnMob(EntityTypes.WITCH, EntitySpawnReason.EVENT, nivel, cerca, 4, 4, 8,
                    SpawnUtil.Strategy.ON_TOP_OF_COLLIDER, false).ifPresent(b -> b.setTarget(presa));
        }
        quien.sendSystemMessage(Component.literal("Un aquelarre de brujas ha sentido el trato y viene a por ti.")
                .withStyle(st -> st.withColor(0xB070E0)));
    }

    /** ALDEAS VIGILADAS: el warden que sale en lugar del golem (uno por aldea: si ya hay uno cerca, no sale). */
    public static void wardenDeAldea(ServerLevel nivel, Villager aldeano, int cuantos) {
        AABB zona = aldeano.getBoundingBox().inflate(32.0);
        if (!nivel.getEntitiesOfClass(Warden.class, zona).isEmpty()) {
            return;
        }
        List<Villager> vecinos = nivel.getEntitiesOfClass(Villager.class, aldeano.getBoundingBox().inflate(10.0));
        long quieren = vecinos.stream().filter(v -> v.wantsToSpawnGolem(nivel.getGameTime())).count();
        if (quieren < cuantos) {
            return;
        }
        SpawnUtil.trySpawnMob(EntityTypes.WARDEN, EntitySpawnReason.MOB_SUMMONED, nivel, aldeano.blockPosition(), 10, 8, 6,
                SpawnUtil.Strategy.ON_TOP_OF_COLLIDER, false);
    }

    /** Una telarana en esa posicion (o justo encima, si ahi no cabe). */
    private static void telarana(ServerLevel nivel, BlockPos pos) {
        for (BlockPos q : new BlockPos[]{pos, pos.above()}) {
            if (nivel.getBlockState(q).canBeReplaced() && nivel.getFluidState(q).isEmpty()) {
                nivel.setBlockAndUpdate(q, Blocks.COBWEB.defaultBlockState());
                return;
            }
        }
    }

    /** PHANTOMS LADRONES: te arranca un hueco del inventario (y lo tira lejos) o te revuelve la barra, y te nubla. */
    private static void phantomLadron(ServerPlayer p) {
        RandomSource r = p.getRandom();
        var inv = p.getInventory();
        if (r.nextBoolean()) {
            List<Integer> llenos = new ArrayList<>();
            for (int i = 0; i < inv.getContainerSize(); i++) {
                if (!inv.getItem(i).isEmpty()) {
                    llenos.add(i);
                }
            }
            if (!llenos.isEmpty()) {
                int i = llenos.get(r.nextInt(llenos.size()));
                ItemStack robado = inv.removeItemNoUpdate(i);
                ItemEntity suelto = p.drop(robado, true, false);
                if (suelto != null) {
                    suelto.setDeltaMovement(new Vec3((r.nextDouble() - 0.5) * 0.9, 0.5, (r.nextDouble() - 0.5) * 0.9));
                    suelto.setPickUpDelay(40);
                }
            }
        } else {
            List<ItemStack> barra = new ArrayList<>();
            for (int i = 0; i < 9; i++) {
                barra.add(inv.getItem(i));
            }
            java.util.Collections.shuffle(barra, new java.util.Random(r.nextLong()));
            for (int i = 0; i < 9; i++) {
                inv.setItem(i, barra.get(i));
            }
        }
        p.addEffect(new MobEffectInstance(MobEffects.BLINDNESS, 50, 0, false, false, true));
    }

    /** CADA MUERTE CUENTA: un creeper cargado de un corazon junto a ese jugador. */
    private static void creeperDeUnCorazon(ServerPlayer p) {
        ServerLevel nivel = p.level();
        RandomSource r = nivel.getRandom();
        for (int intento = 0; intento < 8; intento++) {
            double a = r.nextDouble() * Mth.TWO_PI;
            BlockPos pos = BlockPos.containing(p.getX() + Math.cos(a) * 2.5, p.getY(), p.getZ() + Math.sin(a) * 2.5);
            if (nivel.getBlockState(pos).isAir() && nivel.getBlockState(pos.above()).isAir()) {
                Creeper c = EntityTypes.CREEPER.spawn(nivel, pos, EntitySpawnReason.EVENT);
                if (c != null) {
                    EquipoMobs.cargar(c, true);
                    c.setHealth(1.0F);
                    c.setTarget(p);
                }
                return;
            }
        }
    }

    /** EXTINCION: el gas se lleva a los animales cargados (los que tienen nombre o dueno, no). */
    private static void gasDeExtincion(MinecraftServer s) {
        int muertos = 0;
        for (ServerLevel nivel : s.getAllLevels()) {
            List<Animal> animales = new ArrayList<>();
            for (Entity e : nivel.getAllEntities()) {
                if (e instanceof Animal a && !a.hasCustomName() && !(a instanceof net.minecraft.world.entity.TamableAnimal t && t.isTame())
                        && !a.isLeashed()) {
                    animales.add(a);
                }
            }
            for (Animal a : animales) {
                nivel.sendParticles(net.minecraft.core.particles.ParticleTypes.SNEEZE, a.getX(), a.getY() + 0.5, a.getZ(), 8, 0.3, 0.3, 0.3, 0.02);
                a.kill(nivel);
                muertos++;
            }
        }
        Atalaya.LOGGER.info("Extincion: el gas se ha llevado {} animales.", muertos);
    }

    /** Si un animal puede salir solo (lo pregunta CambiosSpawnMixin). */
    public static boolean animalPuedeSalir(EntitySpawnReason motivo) {
        return !CambiosDificultad.activo(Cambio.EXTINCION)
                || (motivo != EntitySpawnReason.NATURAL && motivo != EntitySpawnReason.CHUNK_GENERATION);
    }

    /** Lo que se hace con un nivel cerca de una cara (lo usan los que buscan techo y suelo). */
    static boolean solido(ServerLevel nivel, BlockPos pos) {
        return nivel.getBlockState(pos).isFaceSturdy(nivel, pos, Direction.UP);
    }
}
