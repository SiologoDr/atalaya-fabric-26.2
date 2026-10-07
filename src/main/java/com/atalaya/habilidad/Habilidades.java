package com.atalaya.habilidad;

import com.atalaya.Atalaya;
import com.atalaya.entity.AeralisDanos;
import com.atalaya.item.ArmadurasJefes;
import com.atalaya.item.ArmadurasJefes.Tema;
import com.atalaya.item.MartilloJadeItem;
import com.atalaya.mixin.LivingEntityAccessor;
import com.atalaya.particula.AtalayaParticulas;
import com.atalaya.sonido.AtalayaSonidos;
import net.fabricmc.fabric.api.attachment.v1.AttachmentRegistry;
import net.fabricmc.fabric.api.attachment.v1.AttachmentSyncPredicate;
import net.fabricmc.fabric.api.attachment.v1.AttachmentType;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerLifecycleEvents;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerTickEvents;
import net.fabricmc.fabric.api.event.player.AttackEntityCallback;
import net.minecraft.core.Holder;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.network.protocol.game.ClientboundSoundPacket;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.ResourceKey;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundSource;
import net.minecraft.tags.DamageTypeTags;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.effect.MobEffect;
import net.minecraft.world.effect.MobEffectCategory;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.AttributeInstance;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.monster.Enemy;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.phys.Vec3;
import org.jspecify.annotations.Nullable;

import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;

/**
 * Las habilidades de las armaduras elementales: cada conjunto entero (las
 * cuatro piezas del mismo tema) da su pasiva siempre y su activa con la tecla
 * de habilidad (R por defecto): 30 s de efecto y 120 s de recarga.
 *
 * <pre>
 *   jade      tanque    Guardian / Muralla de Jade
 *   mareas    sanador   Marea Viva / Manantial
 *   vendaval  soporte   Viento a Favor / Corriente Ascendente
 *   solar     DPS       Corazon de Brasa / Furia Solar
 * </pre>
 *
 * Pensado para combates de 60 jugadores: nada se acumula (un jugador recibe
 * una sola aura de cada tipo, la haya puesto quien la haya puesto), las curas
 * tienen un tope por quien las recibe y las activas cubren a pocos aliados.
 * Y nada toca las mecanicas letales de los jefes (la Mirada, el Rugido de
 * Jade, el meteorito, el Juicio...): esos golpes ni se reducen ni se desvian.
 *
 * "Aliado" es cualquier otro jugador: el mod es para eventos contra jefes.
 */
public final class Habilidades {

    /** Lo que tarda la activa en volver: 120 s. */
    public static final int RECARGA = 2400;
    /** Lo que dura la activa: 30 s. */
    public static final int DURACION = 600;

    // --- Tierra: tanque ---
    private static final double GUARDIAN_RADIO = 4.0;
    private static final float GUARDIAN = 0.95F;
    private static final float MURALLA_PROPIA = 0.8F;
    private static final float MURALLA_DESVIO = 0.3F;
    /** El dano que se lleva el tanque por sus aliados: con armadura y sin empuje. */
    private static final ResourceKey<net.minecraft.world.damagesource.DamageType> MURALLA_JADE = ResourceKey.create(
            Registries.DAMAGE_TYPE, Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "muralla_jade"));
    private static final double MURALLA_RADIO = 8.0;
    // --- Agua: sanador ---
    private static final int MAREA_CADA = 100;
    private static final double MAREA_RADIO = 6.0;
    private static final int MANANTIAL_CADA = 60;
    private static final double MANANTIAL_RADIO = 8.0;
    private static final int TRIDENTE_CADA = 160;
    // --- Viento: soporte ---
    private static final double VIENTO_RADIO = 6.0;
    private static final double CORRIENTE_RADIO = 8.0;
    private static final double RAFAGA_RADIO = 4.5;
    private static final int FLECHA_CADA = 400;
    private static final int FLECHA_DURA = 60;
    // --- Fuego: DPS ---
    private static final float BRASA = 1.10F;
    private static final float FURIA = 1.20F;
    private static final float FURIA_ALIADO = 1.05F;
    private static final int FURIA_ALIADO_CADA = 400;
    private static final double FURIA_RADIO = 8.0;

    private static final Identifier VIENTO_A_FAVOR = Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "viento_a_favor");
    private static final Identifier FLECHA_VENDAVAL = Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "flecha_vendaval");
    private static final EquipmentSlot[] ARMADURA = {EquipmentSlot.HEAD, EquipmentSlot.CHEST, EquipmentSlot.LEGS, EquipmentSlot.FEET};

    public static AttachmentType<HabilidadEstado> ESTADO;

    // Topes por quien recibe (no se guardan: son de pocos segundos).
    private static final Map<UUID, Long> MAREA_RECIBIDA = new HashMap<>();
    private static final Map<UUID, Long> MANANTIAL_RECIBIDO = new HashMap<>();
    private static final Map<UUID, Long> CORRIENTE_HASTA = new HashMap<>();
    private static final Map<UUID, Long> FURIA_ALIADO_HASTA = new HashMap<>();
    private static final Map<UUID, Long> FURIA_RECIBIDA = new HashMap<>();
    private static final Map<UUID, Long> FLECHA_RECIBIDA = new HashMap<>();
    private static final Map<UUID, Long> FLECHA_HASTA = new HashMap<>();
    private static final Map<UUID, Long> TRIDENTE_CURO = new HashMap<>();
    /** Lo cargado que estaba el ultimo golpe de cada jugador (para el martillo). */
    private static final Map<UUID, Float> CARGA = new HashMap<>();
    /** Mientras se le pasa al tanque su parte, ese golpe no se vuelve a desviar. */
    private static final ThreadLocal<Boolean> DESVIANDO = ThreadLocal.withInitial(() -> false);

    private Habilidades() {
    }

    public static void registrar() {
        ESTADO = AttachmentRegistry.<HabilidadEstado>builder()
                // Persiste: salir y entrar no recarga la habilidad.
                .persistent(HabilidadEstado.CODEC)
                .initializer(() -> HabilidadEstado.NADA)
                .syncWith(HabilidadEstado.RED, AttachmentSyncPredicate.targetOnly())
                .buildAndRegister(Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "habilidad"));
        ServerTickEvents.END_SERVER_TICK.register(Habilidades::tick);
        ServerLifecycleEvents.SERVER_STOPPED.register(s -> {
            Provocacion.limpiar();
            for (Map<UUID, ?> m : List.of(MAREA_RECIBIDA, MANANTIAL_RECIBIDO, CORRIENTE_HASTA, FURIA_ALIADO_HASTA, FURIA_RECIBIDA,
                    FLECHA_RECIBIDA, FLECHA_HASTA, TRIDENTE_CURO, CARGA)) {
                m.clear();
            }
        });
        // Lo cargado del golpe se mira antes de que el juego lo reinicie.
        AttackEntityCallback.EVENT.register((jugador, nivel, mano, entidad, golpe) -> {
            if (!nivel.isClientSide() && jugador.getMainHandItem().getItem() instanceof MartilloJadeItem) {
                CARGA.put(jugador.getUUID(), jugador.getAttackStrengthScale(0.5F));
            }
            return InteractionResult.PASS;
        });
    }

    // ------------------------------------------------------------------
    //  Conjunto y estado
    // ------------------------------------------------------------------

    /** El tema del conjunto entero que lleva (las cuatro piezas del mismo), o nada. */
    public static @Nullable Tema conjunto(LivingEntity e) {
        Tema tema = null;
        for (EquipmentSlot hueco : ARMADURA) {
            Tema t = ArmadurasJefes.temaDe(e.getItemBySlot(hueco).getItem());
            if (t == null || (tema != null && t != tema)) {
                return null;
            }
            tema = t;
        }
        return tema;
    }

    public static HabilidadEstado estado(Player p) {
        return p.getAttachedOrCreate(ESTADO);
    }

    private static boolean activa(Player p, Tema tema) {
        return estado(p).activa(p.level().getGameTime(), tema.ordinal()) && conjunto(p) == tema;
    }

    /** Lo cargado del ultimo golpe del jugador (1 = cargado del todo). */
    public static float carga(Player p) {
        return CARGA.getOrDefault(p.getUUID(), 1.0F);
    }

    // ------------------------------------------------------------------
    //  La activa (llega por red al pulsar la tecla)
    // ------------------------------------------------------------------

    public static void activar(ServerPlayer p) {
        Tema tema = conjunto(p);
        if (tema == null || !p.isAlive() || p.isSpectator()) {
            return;
        }
        long ahora = p.level().getGameTime();
        HabilidadEstado e = estado(p);
        if (ahora < e.lista()) {
            p.sendOverlayMessage(Component.translatable("habilidad.atalaya.recarga", (e.lista() - ahora + 19) / 20));
            return;
        }
        p.setAttached(ESTADO, new HabilidadEstado(ahora + RECARGA, ahora + DURACION, tema.ordinal()));
        ServerLevel nivel = p.level();
        switch (tema) {
            case JADE -> {
                sonar(nivel, p, AtalayaSonidos.HABILIDAD_MURALLA, 1.4F);
                aro(nivel, p, AtalayaParticulas.RAJANG_JADE, 2.2, 28);
                Provocacion.reclamar(p, ahora + DURACION);
            }
            case MAREAS -> {
                sonar(nivel, p, AtalayaSonidos.HABILIDAD_MANANTIAL, 1.2F);
                aro(nivel, p, AtalayaParticulas.NEREA_BURBUJA, MANANTIAL_RADIO * 0.5, 30);
                for (Player a : masHeridos(p, MANANTIAL_RADIO, 3, true)) {
                    limpiar(a);
                }
            }
            case VENDAVAL -> {
                sonar(nivel, p, AtalayaSonidos.HABILIDAD_CORRIENTE, 1.2F);
                aro(nivel, p, AtalayaParticulas.AERALIS_POLVO, 2.5, 30);
                List<Player> grupo = new ArrayList<>();
                grupo.add(p);
                grupo.addAll(cercanos(p, CORRIENTE_RADIO, 4));
                for (Player a : grupo) {
                    if (CORRIENTE_HASTA.getOrDefault(a.getUUID(), 0L) > ahora) {
                        continue;
                    }
                    CORRIENTE_HASTA.put(a.getUUID(), ahora + DURACION);
                    a.addEffect(new MobEffectInstance(MobEffects.SPEED, DURACION, 0, false, true, true));
                    a.addEffect(new MobEffectInstance(MobEffects.ABSORPTION, DURACION, 0, false, true, true));
                }
                rafaga(nivel, p, 1.0);
            }
            case SOLAR -> {
                sonar(nivel, p, AtalayaSonidos.HABILIDAD_FURIA, 1.3F);
                aro(nivel, p, AtalayaParticulas.NOVILIS_LLAMA, 1.6, 26);
                for (Player a : cercanos(p, FURIA_RADIO, 3)) {
                    if (!puede(FURIA_RECIBIDA, a.getUUID(), ahora, FURIA_ALIADO_CADA)) {
                        continue;
                    }
                    FURIA_RECIBIDA.put(a.getUUID(), ahora);
                    FURIA_ALIADO_HASTA.put(a.getUUID(), ahora + DURACION);
                    sobre(nivel, a, AtalayaParticulas.NOVILIS_BRASA, 1.0, 10, 0.3, 0.5, 0.02);
                }
            }
        }
    }

    // ------------------------------------------------------------------
    //  Cada tick: pasivas y lo que dura de las activas
    // ------------------------------------------------------------------

    private static void tick(MinecraftServer servidor) {
        List<ServerPlayer> todos = servidor.getPlayerList().getPlayers();
        for (ServerPlayer p : todos) {
            if (!p.isAlive() || p.isSpectator()) {
                continue;
            }
            ServerLevel nivel = p.level();
            long ahora = nivel.getGameTime();
            Tema tema = conjunto(p);
            HabilidadEstado e = estado(p);
            if (tema != null && e.lista() == ahora && e.tema() >= 0) {
                // Lista otra vez: un aviso solo para el.
                p.connection.send(new ClientboundSoundPacket(BuiltInRegistries.SOUND_EVENT.wrapAsHolder(AtalayaSonidos.HABILIDAD_LISTA),
                        SoundSource.PLAYERS, p.getX(), p.getY(), p.getZ(), 0.7F, 1.0F, nivel.getRandom().nextLong()));
            }
            boolean activa = tema != null && e.activa(ahora, tema.ordinal());
            if (tema == Tema.MAREAS) {
                if ((ahora + p.getId()) % MAREA_CADA == 0) {
                    mareaViva(nivel, p, ahora);
                }
                long inicio = e.hasta() - DURACION;
                if (activa && ahora > inicio && (ahora - inicio) % MANANTIAL_CADA == 0) {
                    manantial(nivel, p, ahora);
                }
            } else if (tema == Tema.JADE && activa && (ahora + p.getId()) % 10 == 0) {
                Provocacion.reclamar(p, e.hasta());
                if (ahora % 20 == 0) {
                    aura(nivel, p, AtalayaParticulas.RAJANG_JADE, 3, 0.4, 0.6, 0.0);
                }
            } else if (tema == Tema.VENDAVAL && activa && ahora % 2 == 0) {
                rafaga(nivel, p, 0.35);
            } else if (tema == Tema.SOLAR && activa && ahora % 8 == 0) {
                aura(nivel, p, AtalayaParticulas.NOVILIS_BRASA, 2, 0.3, 0.5, 0.01);
            }
            if ((ahora + p.getId()) % 10 == 0) {
                vientoAFavor(p, todos);
            }
            Long flecha = FLECHA_HASTA.get(p.getUUID());
            if (flecha != null && ahora >= flecha) {
                FLECHA_HASTA.remove(p.getUUID());
                AttributeInstance v = p.getAttribute(Attributes.MOVEMENT_SPEED);
                if (v != null) {
                    v.removeModifier(FLECHA_VENDAVAL);
                }
            }
        }
    }

    /** Marea Viva: medio corazon al aliado mas herido a 6 bloques (cada uno, como mucho uno cada 5 s). */
    private static void mareaViva(ServerLevel nivel, Player sanador, long ahora) {
        for (Player a : masHeridos(sanador, MAREA_RADIO, 1, false)) {
            if (!puede(MAREA_RECIBIDA, a.getUUID(), ahora, MAREA_CADA)) {
                continue;
            }
            MAREA_RECIBIDA.put(a.getUUID(), ahora);
            a.heal(1.0F);
            sobre(nivel, a, AtalayaParticulas.NEREA_LUZ, 1.2, 4, 0.3, 0.4, 0.01);
        }
    }

    /** Un pulso del Manantial: medio corazon a los 3 mas heridos a 8 bloques (cada uno, como mucho uno cada 3 s). */
    private static void manantial(ServerLevel nivel, Player sanador, long ahora) {
        boolean curo = false;
        for (Player a : masHeridos(sanador, MANANTIAL_RADIO, 3, false)) {
            if (!puede(MANANTIAL_RECIBIDO, a.getUUID(), ahora, MANANTIAL_CADA)) {
                continue;
            }
            MANANTIAL_RECIBIDO.put(a.getUUID(), ahora);
            a.heal(1.0F);
            sobre(nivel, a, AtalayaParticulas.NEREA_BURBUJA, 0.8, 5, 0.3, 0.4, 0.02);
            curo = true;
        }
        nivel.sendParticles(AtalayaParticulas.NEREA_LUZ, sanador.getX(), sanador.getY() + 0.2, sanador.getZ(), 8, 1.5, 0.1, 1.5, 0.01);
        if (curo) {
            sonar(nivel, sanador, AtalayaSonidos.HABILIDAD_MANANTIAL_PULSO, 0.5F);
        }
    }

    /** Viento a Favor: +10 % de velocidad a quien tenga un soporte a 6 bloques (uno o veinte, da igual). */
    private static void vientoAFavor(ServerPlayer p, List<ServerPlayer> todos) {
        boolean cerca = false;
        for (ServerPlayer s : todos) {
            if (s.level() == p.level() && s.isAlive() && !s.isSpectator() && s.distanceToSqr(p) <= VIENTO_RADIO * VIENTO_RADIO
                    && conjunto(s) == Tema.VENDAVAL) {
                cerca = true;
                break;
            }
        }
        AttributeInstance v = p.getAttribute(Attributes.MOVEMENT_SPEED);
        if (v == null) {
            return;
        }
        if (cerca && !v.hasModifier(VIENTO_A_FAVOR)) {
            v.addTransientModifier(new AttributeModifier(VIENTO_A_FAVOR, 0.10, AttributeModifier.Operation.ADD_MULTIPLIED_BASE));
        } else if (!cerca && v.hasModifier(VIENTO_A_FAVOR)) {
            v.removeModifier(VIENTO_A_FAVOR);
        }
    }

    /** La rafaga del soporte: aparta a los monstruos normales de su alrededor (solo de el). */
    private static void rafaga(ServerLevel nivel, Player soporte, double fuerza) {
        for (LivingEntity m : nivel.getEntitiesOfClass(LivingEntity.class, soporte.getBoundingBox().inflate(RAFAGA_RADIO),
                x -> x instanceof Enemy && !Jefes.esJefeOMinijefe(x) && x.isAlive())) {
            Vec3 fuera = new Vec3(m.getX() - soporte.getX(), 0, m.getZ() - soporte.getZ());
            double d = fuera.length();
            if (d > RAFAGA_RADIO) {
                continue;
            }
            fuera = d < 1.0E-3 ? new Vec3(1, 0, 0) : fuera.scale(1.0 / d);
            m.setDeltaMovement(fuera.x * 0.9 * fuerza + m.getDeltaMovement().x * 0.2, 0.25 * fuerza, fuera.z * 0.9 * fuerza + m.getDeltaMovement().z * 0.2);
            m.hurtMarked = true;
            if (fuerza > 0.5 || nivel.getRandom().nextInt(4) == 0) {
                nivel.sendParticles(AtalayaParticulas.AERALIS_POLVO, m.getX(), m.getY() + 0.5, m.getZ(), 2, 0.2, 0.2, 0.2, 0.05);
            }
        }
    }

    // ------------------------------------------------------------------
    //  El dano: lo llama DanoHabilidadesMixin al entrar en hurtServer
    // ------------------------------------------------------------------

    /** Los golpes que matan por mecanica: con estos no se mete ninguna habilidad. */
    private static boolean letal(DamageSource fuente) {
        return fuente.is(DamageTypeTags.BYPASSES_INVULNERABILITY) || fuente.is(DamageTypeTags.BYPASSES_RESISTANCE)
                || fuente.is(AeralisDanos.JUICIO);
    }

    public static float modificarDano(LivingEntity victima, DamageSource fuente, float cantidad) {
        if (cantidad <= 0.0F || !(victima.level() instanceof ServerLevel nivel) || letal(fuente)) {
            return cantidad;
        }
        long ahora = nivel.getGameTime();
        // Quien pega: el fuego pega mas.
        if (fuente.getEntity() instanceof Player a && a != victima) {
            float k = 1.0F;
            if (conjunto(a) == Tema.SOLAR) {
                k *= BRASA;
                if (activa(a, Tema.SOLAR)) {
                    k *= FURIA;
                }
            } else if (FURIA_ALIADO_HASTA.getOrDefault(a.getUUID(), 0L) > ahora) {
                k *= FURIA_ALIADO;
            }
            if (fuente.getDirectEntity() instanceof com.atalaya.entity.TridenteMareasEntity) {
                // El tridente lanzado pega lo mismo que en la mano: 9 (el de vanilla, 8).
                k *= 9.0F / 8.0F;
            }
            cantidad *= k;
        }
        if (!(victima instanceof Player v)) {
            return cantidad;
        }
        // Quien recibe.
        if (activa(v, Tema.JADE)) {
            cantidad *= MURALLA_PROPIA;
        }
        if (guardianCerca(v)) {
            cantidad *= GUARDIAN;
        }
        if (fuente.is(DamageTypeTags.IS_FALL) && conjunto(v) == Tema.VENDAVAL) {
            cantidad *= 0.75F;
        }
        // Solo lo que pega un enemigo: caidas, fuego o hambre no van al tanque.
        boolean deEnemigo = fuente.getEntity() instanceof LivingEntity atacante && !(atacante instanceof Player);
        if (deEnemigo && !DESVIANDO.get() && v.invulnerableTime <= 10) {
            ServerPlayer tanque = tanqueQueProtege(v);
            if (tanque != null) {
                float parte = cantidad * MURALLA_DESVIO;
                cantidad -= parte;
                // Se lo come el tanque con su armadura, aunque el golpe del jefe
                // la atraviese: va como dano propio de la Muralla, que no empuja.
                // Ni le da invulnerabilidad ni se la gasta: queda como estaba.
                DamageSource muralla = new DamageSource(
                        nivel.registryAccess().lookupOrThrow(Registries.DAMAGE_TYPE).getOrThrow(MURALLA_JADE),
                        fuente.getEntity(), fuente.getEntity());
                LivingEntityAccessor t = (LivingEntityAccessor) tanque;
                int invulnerable = tanque.invulnerableTime;
                float ultimo = t.atalaya$ultimoGolpe();
                DESVIANDO.set(true);
                try {
                    tanque.invulnerableTime = 0;
                    tanque.hurtServer(nivel, muralla, parte);
                } finally {
                    DESVIANDO.set(false);
                    tanque.invulnerableTime = invulnerable;
                    t.atalaya$ponerUltimoGolpe(ultimo);
                }
                Vec3 a = v.position().add(0, 1.0, 0);
                Vec3 b = tanque.position().add(0, 1.0, 0);
                for (int i = 1; i < 6; i++) {
                    Vec3 q = a.lerp(b, i / 6.0);
                    nivel.sendParticles(AtalayaParticulas.RAJANG_JADE, q.x, q.y, q.z, 1, 0.02, 0.02, 0.02, 0.0);
                }
            }
        }
        return cantidad;
    }

    /** Hay otro jugador con el conjunto de jade a 4 bloques (uno o veinte: el 5 % es el mismo). */
    private static boolean guardianCerca(Player v) {
        for (Player o : v.level().players()) {
            if (o != v && o.isAlive() && !o.isSpectator() && o.distanceToSqr(v) <= GUARDIAN_RADIO * GUARDIAN_RADIO
                    && conjunto(o) == Tema.JADE) {
                return true;
            }
        }
        return false;
    }

    /** El tanque con la Muralla puesta que cubre a este jugador (es uno de sus dos aliados mas cercanos), el mas cercano. */
    private static @Nullable ServerPlayer tanqueQueProtege(Player v) {
        ServerPlayer mejor = null;
        double dMejor = Double.MAX_VALUE;
        for (Player o : v.level().players()) {
            if (o == v || !(o instanceof ServerPlayer t) || !t.isAlive() || t.isSpectator()
                    || t.distanceToSqr(v) > MURALLA_RADIO * MURALLA_RADIO || !activa(t, Tema.JADE)) {
                continue;
            }
            if (cercanos(t, MURALLA_RADIO, 2).contains(v) && t.distanceToSqr(v) < dMejor) {
                dMejor = t.distanceToSqr(v);
                mejor = t;
            }
        }
        return mejor;
    }

    // ------------------------------------------------------------------
    //  Lo que llaman las armas
    // ------------------------------------------------------------------

    /** El tridente cura medio corazon al aliado mas herido, como mucho una vez cada 8 s por portador. */
    public static void curaTridente(Player portador) {
        if (!(portador.level() instanceof ServerLevel nivel)) {
            return;
        }
        long ahora = nivel.getGameTime();
        if (!puede(TRIDENTE_CURO, portador.getUUID(), ahora, TRIDENTE_CADA)) {
            return;
        }
        List<Player> heridos = masHeridos(portador, MANANTIAL_RADIO, 1, false);
        if (heridos.isEmpty()) {
            return;
        }
        TRIDENTE_CURO.put(portador.getUUID(), ahora);
        Player a = heridos.get(0);
        a.heal(1.0F);
        sobre(nivel, a, AtalayaParticulas.NEREA_LUZ, 1.2, 6, 0.3, 0.4, 0.01);
        nivel.playSound(null, a.getX(), a.getY(), a.getZ(), AtalayaSonidos.TRIDENTE_CURA, SoundSource.PLAYERS, 0.7F, 1.0F);
    }

    /**
     * Una flecha del Arco del Vendaval ha dado a un aliado: Velocidad I y un 5 %
     * mas durante 3 s, como mucho una vez cada 20 s por jugador. Devuelve si se
     * lo ha dado.
     */
    public static boolean flechaAliado(Player aliado) {
        if (!(aliado.level() instanceof ServerLevel nivel)) {
            return false;
        }
        long ahora = nivel.getGameTime();
        if (!puede(FLECHA_RECIBIDA, aliado.getUUID(), ahora, FLECHA_CADA)) {
            return false;
        }
        FLECHA_RECIBIDA.put(aliado.getUUID(), ahora);
        aliado.addEffect(new MobEffectInstance(MobEffects.SPEED, FLECHA_DURA, 0, false, true, true));
        AttributeInstance v = aliado.getAttribute(Attributes.MOVEMENT_SPEED);
        if (v != null && !v.hasModifier(FLECHA_VENDAVAL)) {
            v.addTransientModifier(new AttributeModifier(FLECHA_VENDAVAL, 0.05, AttributeModifier.Operation.ADD_MULTIPLIED_BASE));
        }
        FLECHA_HASTA.put(aliado.getUUID(), ahora + FLECHA_DURA);
        sobre(nivel, aliado, AtalayaParticulas.AERALIS_POLVO, 1.0, 8, 0.3, 0.5, 0.03);
        nivel.playSound(null, aliado.getX(), aliado.getY(), aliado.getZ(), AtalayaSonidos.FLECHA_ALIADO, SoundSource.PLAYERS, 0.8F, 1.0F);
        return true;
    }

    // ------------------------------------------------------------------
    //  Ayudas
    // ------------------------------------------------------------------

    /** Si ya han pasado 'cada' ticks desde la ultima vez que este jugador recibio esto. */
    private static boolean puede(Map<UUID, Long> ultima, UUID id, long ahora, int cada) {
        Long u = ultima.get(id);
        return u == null || ahora - u >= cada;
    }

    /** Los n jugadores mas cercanos (sin contarle a el) a menos de r bloques. */
    private static List<Player> cercanos(Player p, double r, int n) {
        List<Player> lista = new ArrayList<>();
        for (Player o : p.level().players()) {
            if (o != p && o.isAlive() && !o.isSpectator() && o.distanceToSqr(p) <= r * r) {
                lista.add(o);
            }
        }
        lista.sort(Comparator.comparingDouble(o -> o.distanceToSqr(p)));
        return lista.size() > n ? lista.subList(0, n) : lista;
    }

    /** Los n aliados mas heridos a menos de r bloques (sin contarle a el). Con 'todos', aunque esten sanos. */
    private static List<Player> masHeridos(Player p, double r, int n, boolean todos) {
        List<Player> lista = new ArrayList<>();
        for (Player o : p.level().players()) {
            if (o != p && o.isAlive() && !o.isSpectator() && o.distanceToSqr(p) <= r * r && (todos || o.getHealth() < o.getMaxHealth())) {
                lista.add(o);
            }
        }
        lista.sort(Comparator.comparingDouble(o -> o.getHealth() / o.getMaxHealth()));
        return lista.size() > n ? lista.subList(0, n) : lista;
    }

    /** Le quita todos los efectos negativos. */
    private static void limpiar(Player a) {
        List<Holder<MobEffect>> malos = new ArrayList<>();
        for (MobEffectInstance i : a.getActiveEffects()) {
            if (i.getEffect().value().getCategory() == MobEffectCategory.HARMFUL) {
                malos.add(i.getEffect());
            }
        }
        for (Holder<MobEffect> m : malos) {
            a.removeEffect(m);
        }
        if (a.level() instanceof ServerLevel nivel) {
            sobre(nivel, a, AtalayaParticulas.NEREA_LUZ, 1.0, 10, 0.3, 0.6, 0.02);
        }
    }

    private static void sonar(ServerLevel nivel, Player p, SoundEvent s, float volumen) {
        nivel.playSound(null, p.getX(), p.getY(), p.getZ(), s, SoundSource.PLAYERS, volumen, 1.0F);
    }

    /**
     * Particulas sobre un jugador: los demas las ven alrededor de su cuerpo;
     * el, solo unas pocas a los pies, para que no le tapen la vista en primera
     * persona (las brasas y luces de los jefes son grandes).
     */
    private static void sobre(ServerLevel nivel, Player quien, net.minecraft.core.particles.SimpleParticleType tipo, double alto,
                              int n, double ancho, double dy, double vel) {
        for (ServerPlayer o : nivel.players()) {
            if (o == quien) {
                nivel.sendParticles(o, tipo, false, false, quien.getX(), quien.getY() + 0.1, quien.getZ(), Math.max(1, n / 3),
                        ancho, 0.05, ancho, vel * 0.5);
            } else {
                nivel.sendParticles(o, tipo, false, false, quien.getX(), quien.getY() + alto, quien.getZ(), n, ancho, dy, ancho, vel);
            }
        }
    }

    /** El aura de una activa que dura: solo la ven los demas (al que la lleva le basta el HUD). */
    private static void aura(ServerLevel nivel, Player quien, net.minecraft.core.particles.SimpleParticleType tipo, int n,
                             double ancho, double dy, double vel) {
        for (ServerPlayer o : nivel.players()) {
            if (o != quien) {
                nivel.sendParticles(o, tipo, false, false, quien.getX(), quien.getY() + 1.0, quien.getZ(), n, ancho, dy, ancho, vel);
            }
        }
    }

    private static void aro(ServerLevel nivel, Player p, net.minecraft.core.particles.SimpleParticleType tipo, double r, int n) {
        for (int i = 0; i < n; i++) {
            double a = Math.PI * 2 * i / n;
            nivel.sendParticles(tipo, p.getX() + Math.cos(a) * r, p.getY() + 0.3, p.getZ() + Math.sin(a) * r, 1, 0.05, 0.1, 0.05, 0.01);
        }
    }
}
