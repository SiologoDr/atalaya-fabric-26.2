package com.atalaya.item;

import com.atalaya.entity.PresasJefe;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import net.minecraft.core.Holder;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.effect.MobEffect;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.monster.Enemy;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Rarity;
import net.minecraft.world.item.component.DeathProtection;
import net.minecraft.world.item.consume_effects.ApplyStatusEffectsConsumeEffect;
import net.minecraft.world.item.consume_effects.ClearAllStatusEffectsConsumeEffect;
import net.minecraft.world.item.consume_effects.TeleportRandomlyConsumeEffect;
import net.minecraft.world.phys.Vec3;

/**
 * Los tótems del mod (11-10-2026, Juan: "agrega más tipos de tótem con todo lo
 * que tenemos"). Son como el tótem de la inmortalidad ("tienen que ser como el
 * totem normal, no con colores"): ídolos de oro con la forma de su criatura, y al
 * salvarte salen las partículas, el sonido y la animación en pantalla de vanilla. Llevan su
 * componente death_protection, así que el juego los trata igual: en cualquier
 * mano, quedas a medio corazón y se gasta. Cada tipo añade lo suyo.
 *
 * <ul>
 *   <li><b>Menores</b> (los de los mini jefes): lo de vanilla y un detalle de su
 *   elemento.</li>
 *   <li><b>Mayores</b> (los de los jefes): lo de vanilla y el papel de su
 *   elemento, como en las armaduras: Nerea cura, Aeralis apoya, Rajang aguanta y
 *   Novilis pega.</li>
 *   <li><b>Otros</b>: el del Viajero y el de Dos Vidas.</li>
 * </ul>
 *
 * Por ahora no tienen receta ni los suelta nadie (Juan, 11-10-2026: "ya tengo una
 * idea para ellos"): se consiguen en creativo.
 *
 * Como las armaduras, nada se acumula (las curas de Nerea a los aliados, una vez
 * por minuto por jugador) y lo que hacen a los monstruos no toca a jefes ni a
 * mini jefes. Salvan de los golpes que "matan salvo tótem" igual que el de
 * vanilla: para eso están.
 */
public enum TotemJefe {

    MOCTEZUMA("moctezuma", Rarity.RARE, base(efecto(MobEffects.RESISTANCE, 200, 0))),
    YIATZO("yiatzo", Rarity.RARE, base(efecto(MobEffects.SPEED, 160, 1), efecto(MobEffects.SLOW_FALLING, 160, 0))),
    ATLAHUA("atlahua", Rarity.RARE,
            List.of(efecto(MobEffects.REGENERATION, 1200, 1), efecto(MobEffects.ABSORPTION, 100, 1),
                    efecto(MobEffects.FIRE_RESISTANCE, 800, 0), efecto(MobEffects.WATER_BREATHING, 2400, 0))),
    XIUHQUETZAL("xiuhquetzal", Rarity.RARE,
            List.of(efecto(MobEffects.REGENERATION, 900, 1), efecto(MobEffects.ABSORPTION, 100, 1),
                    efecto(MobEffects.FIRE_RESISTANCE, 2400, 0))),
    NEREA("nerea", Rarity.EPIC,
            List.of(efecto(MobEffects.REGENERATION, 600, 2), efecto(MobEffects.ABSORPTION, 100, 1),
                    efecto(MobEffects.FIRE_RESISTANCE, 800, 0), efecto(MobEffects.WATER_BREATHING, 2400, 0))),
    AERALIS("aeralis", Rarity.EPIC, base(efecto(MobEffects.SPEED, 200, 1), efecto(MobEffects.SLOW_FALLING, 200, 0))),
    RAJANG("rajang", Rarity.EPIC,
            List.of(efecto(MobEffects.REGENERATION, 900, 1), efecto(MobEffects.ABSORPTION, 300, 3),
                    efecto(MobEffects.FIRE_RESISTANCE, 800, 0), efecto(MobEffects.RESISTANCE, 160, 1))),
    NOVILIS("novilis", Rarity.EPIC,
            List.of(efecto(MobEffects.REGENERATION, 900, 1), efecto(MobEffects.ABSORPTION, 100, 1),
                    efecto(MobEffects.FIRE_RESISTANCE, 2400, 0), efecto(MobEffects.STRENGTH, 200, 1))),
    // Te saca de ahí: tras salvarte te lleva a otro sitio a unos 16 bloques (como la fruta coral).
    VIAJERO("viajero", Rarity.UNCOMMON, base()),
    // Aguanta dos muertes: la primera no se gasta (se apaga su brillo); la segunda, sí (AvisoTotemMixin).
    DOS_VIDAS("dos_vidas", Rarity.EPIC, base());

    /** Lo que cura la marea de Nerea a cada aliado (vida) y cada cuánto, como mucho, a cada uno (ticks). */
    public static final float CURA_NEREA = 8.0F;
    public static final int CURA_NEREA_CADA = 20 * 60;
    private static final Map<UUID, Long> CURADOS = new HashMap<>();

    public final String id;
    public final Rarity rareza;
    private final List<MobEffectInstance> efectos;

    TotemJefe(String id, Rarity rareza, List<MobEffectInstance> efectos) {
        this.id = id;
        this.rareza = rareza;
        this.efectos = efectos;
    }

    /** Lo que le pone el juego al salvarte (su death_protection): limpia los efectos y da los suyos. */
    public DeathProtection proteccion() {
        if (this == VIAJERO) {
            return new DeathProtection(List.of(ClearAllStatusEffectsConsumeEffect.INSTANCE,
                    new ApplyStatusEffectsConsumeEffect(efectos), new TeleportRandomlyConsumeEffect(32.0F)));
        }
        return new DeathProtection(List.of(ClearAllStatusEffectsConsumeEffect.INSTANCE,
                new ApplyStatusEffectsConsumeEffect(efectos)));
    }

    /** Los del tótem de la inmortalidad (Regeneración II 45 s, Absorción II 5 s, Resistencia al fuego 40 s) y más. */
    private static List<MobEffectInstance> base(MobEffectInstance... mas) {
        List<MobEffectInstance> l = new ArrayList<>(List.of(efecto(MobEffects.REGENERATION, 900, 1),
                efecto(MobEffects.ABSORPTION, 100, 1), efecto(MobEffects.FIRE_RESISTANCE, 800, 0)));
        l.addAll(List.of(mas));
        return List.copyOf(l);
    }

    private static MobEffectInstance efecto(Holder<MobEffect> e, int ticks, int nivel) {
        return new MobEffectInstance(e, ticks, nivel);
    }

    /** El tótem de este objeto, o null si no es uno de los nuestros. */
    public static TotemJefe de(ItemStack stack) {
        return stack.getItem() instanceof TotemJefeItem t ? t.totem : null;
    }

    // ------------------------------------------------------------------
    //  Lo que hace al salvarte, además de los efectos (en el servidor)
    // ------------------------------------------------------------------

    public void alSalvar(ServerLevel nivel, LivingEntity quien) {
        switch (this) {
            // La onda de jade aparta a los monstruos.
            case MOCTEZUMA -> empujar(nivel, quien, 6.0, 1.1);
            // Una ráfaga te saca de ahí: te alza (y caes despacio) y aparta a los de al lado.
            case YIATZO -> {
                alzar(quien, 1.0);
                empujar(nivel, quien, 4.0, 0.7);
            }
            case ATLAHUA, NEREA -> {
                quien.clearFire();
                if (this == NEREA) {
                    // La marea cura a los aliados más heridos de alrededor.
                    curarAliados(nivel, quien);
                }
            }
            // Renace en llamas: prende a los monstruos de alrededor.
            case XIUHQUETZAL -> prender(nivel, quien, 6.0, 100);
            // El vendaval: te alza, aparta a los monstruos y empuja a los aliados cercanos (Velocidad I).
            case AERALIS -> {
                alzar(quien, 0.8);
                empujar(nivel, quien, 8.0, 1.6);
                apoyarAliados(nivel, quien);
            }
            case RAJANG -> empujar(nivel, quien, 7.0, 1.3);
            // Un sol: prende a los monstruos de alrededor.
            case NOVILIS -> prender(nivel, quien, 8.0, 160);
            // Lo suyo lo hace su death_protection (el viaje) y AvisoTotemMixin (la segunda vida).
            case VIAJERO, DOS_VIDAS -> {
            }
        }
    }

    /** Los monstruos de alrededor: ni jefes, ni mini jefes, ni jugadores. */
    private static List<LivingEntity> monstruos(ServerLevel nivel, LivingEntity quien, double radio) {
        return nivel.getEntitiesOfClass(LivingEntity.class, quien.getBoundingBox().inflate(radio), e ->
                e != quien && e.isAlive() && e instanceof Enemy && !(e instanceof Player) && !PresasJefe.esJefe(e)
                        && e.distanceToSqr(quien) <= radio * radio);
    }

    private static void empujar(ServerLevel nivel, LivingEntity quien, double radio, double fuerza) {
        for (LivingEntity e : monstruos(nivel, quien, radio)) {
            Vec3 fuera = new Vec3(e.getX() - quien.getX(), 0.0, e.getZ() - quien.getZ());
            if (fuera.lengthSqr() < 1.0E-4) {
                fuera = new Vec3(1.0, 0.0, 0.0);
            }
            double k = fuerza * (1.0 - fuera.length() / radio * 0.5);
            fuera = fuera.normalize().scale(k);
            e.push(fuera.x, 0.35 * k, fuera.z);
            e.hurtMarked = true;
        }
    }

    private static void prender(ServerLevel nivel, LivingEntity quien, double radio, int ticks) {
        for (LivingEntity e : monstruos(nivel, quien, radio)) {
            e.igniteForTicks(ticks);
        }
    }

    private static void alzar(LivingEntity quien, double vy) {
        Vec3 v = quien.getDeltaMovement();
        quien.setDeltaMovement(v.x * 0.3, Math.max(v.y, vy), v.z * 0.3);
        quien.hurtMarked = true;
        quien.fallDistance = 0.0F;
    }

    /** Los jugadores de alrededor que pelean (supervivencia o aventura), sin el que lo usa. */
    private static List<Player> aliados(ServerLevel nivel, LivingEntity quien, double radio) {
        return nivel.getEntitiesOfClass(Player.class, quien.getBoundingBox().inflate(radio), j ->
                j != quien && j.isAlive() && !j.isSpectator() && !j.isCreative() && j.distanceToSqr(quien) <= radio * radio);
    }

    /** Nerea: cura a los 3 aliados más heridos a 8 bloques (a cada uno, como mucho una vez por minuto). */
    private static void curarAliados(ServerLevel nivel, LivingEntity quien) {
        long ahora = nivel.getGameTime();
        CURADOS.values().removeIf(t -> ahora - t > CURA_NEREA_CADA);
        List<Player> heridos = new ArrayList<>(aliados(nivel, quien, 8.0));
        heridos.removeIf(j -> j.getHealth() >= j.getMaxHealth() || CURADOS.containsKey(j.getUUID()));
        heridos.sort(Comparator.comparingDouble(j -> j.getHealth() / j.getMaxHealth()));
        for (Player j : heridos.subList(0, Math.min(3, heridos.size()))) {
            j.heal(CURA_NEREA);
            CURADOS.put(j.getUUID(), ahora);
            destello(nivel, j);
        }
    }

    /** Aeralis: Velocidad I 10 s a los 4 aliados más cercanos a 8 bloques (no se suma a la que ya tengan). */
    private static void apoyarAliados(ServerLevel nivel, LivingEntity quien) {
        List<Player> cerca = new ArrayList<>(aliados(nivel, quien, 8.0));
        cerca.sort(Comparator.comparingDouble(j -> j.distanceToSqr(quien)));
        for (Player j : cerca.subList(0, Math.min(4, cerca.size()))) {
            j.addEffect(new MobEffectInstance(MobEffects.SPEED, 200, 0));
            destello(nivel, j);
        }
    }

    /** Un poco del brillo del tótem sobre el aliado que recibe algo. */
    private static void destello(ServerLevel nivel, Player j) {
        nivel.sendParticles(ParticleTypes.TOTEM_OF_UNDYING, j.getX(), j.getY() + 1.0, j.getZ(), 20, 0.3, 0.6, 0.3, 0.3);
    }
}
