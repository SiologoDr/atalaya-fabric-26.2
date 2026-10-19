package com.atalaya.cambios;

import com.atalaya.mixin.CreeperAccessor;
import net.minecraft.core.Holder;
import net.minecraft.core.component.DataComponents;
import net.minecraft.core.registries.Registries;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.util.RandomSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.monster.Creeper;
import net.minecraft.world.entity.monster.illager.Pillager;
import net.minecraft.world.entity.monster.piglin.Piglin;
import net.minecraft.world.entity.monster.spider.Spider;
import net.minecraft.world.entity.monster.zombie.Zombie;
import net.minecraft.world.entity.monster.zombie.ZombifiedPiglin;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.component.FireworkExplosion;
import net.minecraft.world.item.component.Fireworks;
import net.minecraft.world.item.enchantment.Enchantment;
import net.minecraft.world.item.enchantment.Enchantments;
import it.unimi.dsi.fastutil.ints.IntList;

import java.util.List;

/**
 * Lo que los cambios de dificultad le ponen a los mobs de siempre al aparecer (o al cargarse sin tenerlo, o al encender
 * el cambio con ellos ya en el mundo). Cada cosa deja una marca en el mob para no repetirse, y al apagar el cambio se
 * les quita a los que la llevan.
 *
 * <pre>
 *   ARANAS DE GUERRA          Velocidad I y Fuerza IV para siempre
 *   ZOMBIS TREPADORES         espada de hierro con Filo V
 *   ZOMBIS LISTOS             pico de diamante, armadura, perlas y, a veces, un totem; y su IA de picar y poner
 *   TORMENTA EN LOS CREEPERS  cargados
 *   POLVORA EN LAS BALLESTAS  cohetes que estallan en la otra mano (la ballesta los dispara)
 * </pre>
 */
public final class EquipoMobs {

    private static final String M_ARANA = "atalaya_arana_guerra";
    private static final String M_ESPADA = "atalaya_zombi_espada";
    private static final String M_LISTO = "atalaya_zombi_listo";
    private static final String M_CARGADO = "atalaya_creeper_cargado";
    private static final String M_COHETES = "atalaya_cohetes";

    private EquipoMobs() {
    }

    static boolean tocaMobs(Cambio c) {
        return c == Cambio.ARANAS_DE_GUERRA || c == Cambio.ZOMBIS_TREPADORES || c == Cambio.ZOMBIS_LISTOS
                || c == Cambio.CREEPERS_CARGADOS || c == Cambio.POLVORA_EN_LAS_BALLESTAS;
    }

    /** Un mob que se carga en el mundo: lo que le toque de los cambios encendidos. */
    static void alCargar(Entity e) {
        if (!(e instanceof Mob mob) || !(mob.level() instanceof ServerLevel)) {
            return;
        }
        if (mob instanceof Spider && CambiosDificultad.activo(Cambio.ARANAS_DE_GUERRA)) {
            aranaDeGuerra(mob);
        }
        if (mob instanceof Zombie z && !(mob instanceof ZombifiedPiglin)) {
            if (CambiosDificultad.activo(Cambio.ZOMBIS_TREPADORES)) {
                espada(z);
            }
            if (CambiosDificultad.activo(Cambio.ZOMBIS_LISTOS)) {
                ZombisListos.preparar(z);
            }
        }
        if (mob instanceof Creeper c && CambiosDificultad.activo(Cambio.CREEPERS_CARGADOS) && !c.entityTags().contains(M_CARGADO)) {
            c.addTag(M_CARGADO);
            cargar(c, true);
        }
        if ((mob instanceof Piglin || mob instanceof Pillager) && CambiosDificultad.activo(Cambio.POLVORA_EN_LAS_BALLESTAS)) {
            cohetes(mob);
        }
    }

    /** Al encender uno: a los que ya estan cargados. */
    static void aplicarCargados(MinecraftServer s, Cambio c) {
        for (ServerLevel nivel : s.getAllLevels()) {
            for (Entity e : nivel.getAllEntities()) {
                alCargar(e);
            }
        }
    }

    /** Al apagarlo: se les quita a los que lo llevan. */
    static void quitarCargados(MinecraftServer s, Cambio c) {
        for (ServerLevel nivel : s.getAllLevels()) {
            for (Entity e : nivel.getAllEntities()) {
                if (!(e instanceof Mob mob)) {
                    continue;
                }
                switch (c) {
                    case ARANAS_DE_GUERRA -> {
                        if (mob.removeTag(M_ARANA)) {
                            mob.removeEffect(MobEffects.SPEED);
                            mob.removeEffect(MobEffects.STRENGTH);
                        }
                    }
                    case CREEPERS_CARGADOS -> {
                        if (mob instanceof Creeper cr && mob.removeTag(M_CARGADO)) {
                            cargar(cr, false);
                        }
                    }
                    case POLVORA_EN_LAS_BALLESTAS -> {
                        if (mob.removeTag(M_COHETES)) {
                            mob.setItemSlot(EquipmentSlot.OFFHAND, ItemStack.EMPTY);
                        }
                    }
                    default -> {
                    }
                }
            }
        }
    }

    private static void aranaDeGuerra(Mob m) {
        if (m.entityTags().contains(M_ARANA) && m.hasEffect(MobEffects.STRENGTH)) {
            return;
        }
        m.addTag(M_ARANA);
        m.addEffect(new MobEffectInstance(MobEffects.SPEED, MobEffectInstance.INFINITE_DURATION, 0, false, false));
        m.addEffect(new MobEffectInstance(MobEffects.STRENGTH, MobEffectInstance.INFINITE_DURATION, 3, false, false));
    }

    private static void espada(Zombie z) {
        if (z.entityTags().contains(M_ESPADA) || !z.getMainHandItem().isEmpty()) {
            return;
        }
        z.addTag(M_ESPADA);
        ItemStack espada = new ItemStack(Items.IRON_SWORD);
        Holder<Enchantment> filo = z.level().registryAccess().lookupOrThrow(Registries.ENCHANTMENT).getOrThrow(Enchantments.SHARPNESS);
        espada.enchant(filo, 5);
        z.setItemSlot(EquipmentSlot.MAINHAND, espada);
        z.setDropChance(EquipmentSlot.MAINHAND, 0.05F);
    }

    /** Carga (o descarga) a un creeper, como si le hubiera caido un rayo. */
    public static void cargar(Creeper c, boolean cargado) {
        c.getEntityData().set(CreeperAccessor.atalaya$datoCargado(), cargado);
    }

    private static void cohetes(Mob m) {
        boolean ballesta = m.getMainHandItem().is(Items.CROSSBOW);
        if (!ballesta || m.entityTags().contains(M_COHETES)) {
            return;
        }
        m.addTag(M_COHETES);
        ItemStack cohete = new ItemStack(Items.FIREWORK_ROCKET, 64);
        RandomSource r = m.getRandom();
        cohete.set(DataComponents.FIREWORKS, new Fireworks(1, List.of(
                new FireworkExplosion(FireworkExplosion.Shape.LARGE_BALL, IntList.of(0xFF5A2A, 0xFFD23A), IntList.of(0xFFFFFF), r.nextBoolean(), true),
                new FireworkExplosion(FireworkExplosion.Shape.BURST, IntList.of(0xFF9A3C), IntList.of(), false, false))));
        m.setItemSlot(EquipmentSlot.OFFHAND, cohete);
        m.setDropChance(EquipmentSlot.OFFHAND, 0.0F);
    }
}
