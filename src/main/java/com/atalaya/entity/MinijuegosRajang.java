package com.atalaya.entity;

import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import net.minecraft.core.component.DataComponents;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.component.CustomData;
import org.jspecify.annotations.Nullable;

/**
 * Los minijuegos de Rajang (octubre de 2026). Juan, tras cinco fichas, eligio
 * uno por fase: El Rayo del Prisma (I), El Impostor de Jade (II), Glifos del
 * Templo (III) y Suelo que se Hunde (IV). Uno a la vez, como los de Nerea, y
 * como las fases se suman, en la IV pueden salir todos. Cada uno vive en su
 * clase (PrismaRajang, ImpostorRajang, GlifosRajang, SueloRajang).
 *
 * Aqui esta lo que comparten los objetos que reparte (el Prisma de Jade): cada
 * uno lleva dentro de que Rajang es, y si ese Rajang ya no esta en su minijuego,
 * el objeto se deshace (como el Idolo de Oro).
 */
public final class MinijuegosRajang {

    public static final int NINGUNO = 0;
    public static final int PRISMA = 1;
    public static final int IMPOSTOR = 2;
    public static final int GLIFOS = 3;
    public static final int SUELO = 4;
    /** La fase desde la que sale cada uno. */
    static final int[] FASE = {0, 1, 2, 3, 4};
    /** Su nombre en las claves de texto. */
    public static final String[] CLAVES = {"", "prisma", "impostor", "glifos", "suelo"};
    /**
     * Los ocho glifos del templo (rajang_minijuegos.py), por su orden en
     * glifos.png: Jaguar, Serpiente, Sol, Luna, Mano, Calavera, Piramide y Ojo.
     */
    public static final String[] NOMBRES_GLIFOS = {"jaguar", "serpiente", "sol", "luna", "mano", "calavera", "piramide", "ojo"};

    private static final Map<UUID, RajangEntity> ACTIVOS = new ConcurrentHashMap<>();
    private static final String CLAVE = "rajang";

    private MinijuegosRajang() {
    }

    static void activar(RajangEntity r) {
        ACTIVOS.put(r.getUUID(), r);
    }

    static void desactivar(RajangEntity r) {
        ACTIVOS.remove(r.getUUID());
    }

    /** Un objeto del minijuego de este Rajang. */
    static ItemStack crear(RajangEntity r, Item item) {
        ItemStack s = new ItemStack(item);
        CompoundTag t = new CompoundTag();
        t.putString(CLAVE, r.getUUID().toString());
        s.set(DataComponents.CUSTOM_DATA, CustomData.of(t));
        return s;
    }

    private static @Nullable UUID uuid(ItemStack s) {
        CustomData d = s.get(DataComponents.CUSTOM_DATA);
        if (d == null) {
            return null;
        }
        String u = d.copyTag().getStringOr(CLAVE, "");
        try {
            return u.isEmpty() ? null : UUID.fromString(u);
        } catch (IllegalArgumentException e) {
            return null;
        }
    }

    /** El Rajang de este objeto, si sigue en un minijuego; si no, null. */
    public static @Nullable RajangEntity de(ItemStack s) {
        UUID u = uuid(s);
        RajangEntity r = u == null ? null : ACTIVOS.get(u);
        return r != null && !r.isRemoved() && !r.isDeadOrDying() && r.minijuego() != NINGUNO ? r : null;
    }

    /** Si el objeto sigue valiendo: su Rajang esta en este minijuego. */
    public static boolean vivo(ItemStack s, int tipo) {
        RajangEntity r = de(s);
        return r != null && r.minijuego() == tipo;
    }

    /** Lo pone en la mano principal si esta libre; si no, en el inventario, o a sus pies. */
    static void dar(Player p, ItemStack s) {
        if (p.getMainHandItem().isEmpty()) {
            p.setItemInHand(net.minecraft.world.InteractionHand.MAIN_HAND, s);
        } else if (!p.getInventory().add(s)) {
            p.drop(s, false);
        }
    }

    /** El objeto de este Rajang tirado en el suelo (el mas nuevo), o null. */
    static @Nullable ItemEntity enSuelo(ServerLevel nivel, RajangEntity r, Item item) {
        UUID u = r.getUUID();
        ItemEntity mejor = null;
        for (ItemEntity it : nivel.getEntitiesOfClass(ItemEntity.class, r.getBoundingBox().inflate(96, 48, 96),
                it -> it.getItem().is(item) && u.equals(uuid(it.getItem())))) {
            if (mejor == null || it.tickCount < mejor.tickCount) {
                mejor = it;
            }
        }
        return mejor;
    }

    /** Antes de cualquier dano: a las copias del Impostor no les entra nada (cuenta el golpe). */
    public static boolean permitirDano(net.minecraft.world.entity.LivingEntity v, net.minecraft.world.damagesource.DamageSource fuente) {
        return ImpostorRajang.alDanar(v, fuente);
    }

    /** Al cargar una entidad: una copia del Impostor que se quedo en el mundo, fuera. */
    public static void alCargar(net.minecraft.world.entity.Entity e) {
        ImpostorRajang.alCargar(e);
    }

    /** Quita de todos los inventarios y del suelo los objetos de este Rajang. */
    static void quitarTodo(ServerLevel nivel, RajangEntity r) {
        UUID u = r.getUUID();
        for (Player p : nivel.players()) {
            Inventory inv = p.getInventory();
            for (int i = 0; i < inv.getContainerSize(); i++) {
                if (u.equals(uuid(inv.getItem(i)))) {
                    inv.setItem(i, ItemStack.EMPTY);
                }
            }
        }
        for (ItemEntity it : nivel.getEntitiesOfClass(ItemEntity.class, r.getBoundingBox().inflate(96, 48, 96),
                it -> u.equals(uuid(it.getItem())))) {
            it.discard();
        }
    }
}
