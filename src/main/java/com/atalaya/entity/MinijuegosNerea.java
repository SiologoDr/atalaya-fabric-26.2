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
 * Los minijuegos de Nerea (octubre de 2026, Juan: "a la gente le gustan los
 * minijuegos de los jefes"): la Pesca del Abismo, los Canones del Naufragio y
 * las Morenas de las Pozas (el Duelo de Canto va aparte, en NereaEntity).
 *
 * Aqui esta lo que comparten los objetos que se reparten mientras duran (la
 * Cana del Abismo, la Perla del Abismo y la Bala de canon): cada uno lleva
 * dentro de que Nerea es, y si esa Nerea ya no esta en su minijuego, el objeto
 * se deshace (como el Idolo de Oro de Rajang). Y el corcho que tiene lanzado
 * cada jugador, para recogerlo con la cana.
 */
public final class MinijuegosNerea {

    public static final int NINGUNO = 0;
    public static final int PESCA = 1;
    public static final int CANONES = 2;
    public static final int MORENAS = 3;

    private static final Map<UUID, NereaEntity> ACTIVAS = new ConcurrentHashMap<>();
    private static final Map<UUID, CorchoAbismoEntity> CORCHOS = new ConcurrentHashMap<>();
    private static final String CLAVE = "nerea";

    private MinijuegosNerea() {
    }

    static void activar(NereaEntity n) {
        ACTIVAS.put(n.getUUID(), n);
    }

    static void desactivar(NereaEntity n) {
        ACTIVAS.remove(n.getUUID());
    }

    /** Un objeto del minijuego de esta Nerea. */
    static ItemStack crear(NereaEntity n, Item item) {
        ItemStack s = new ItemStack(item);
        CompoundTag t = new CompoundTag();
        t.putString(CLAVE, n.getUUID().toString());
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

    /** La Nerea de este objeto, si sigue en un minijuego; si no, null. */
    public static @Nullable NereaEntity de(ItemStack s) {
        UUID u = uuid(s);
        NereaEntity n = u == null ? null : ACTIVAS.get(u);
        return n != null && !n.isRemoved() && !n.isDeadOrDying() && n.minijuego() != NINGUNO ? n : null;
    }

    /** Si el objeto sigue valiendo: su Nerea esta en este minijuego. */
    public static boolean vivo(ItemStack s, int tipo) {
        NereaEntity n = de(s);
        return n != null && n.minijuego() == tipo;
    }

    /** Lo pone en el inventario (en la barra si cabe) o, si no cabe, a sus pies. */
    static void dar(Player p, ItemStack s) {
        if (!p.getInventory().add(s)) {
            p.drop(s, false);
        }
    }

    /** Quita de todos los inventarios cercanos y del suelo los objetos de esta Nerea. */
    static void quitarTodo(ServerLevel nivel, NereaEntity n) {
        UUID u = n.getUUID();
        for (Player p : nivel.players()) {
            Inventory inv = p.getInventory();
            for (int i = 0; i < inv.getContainerSize(); i++) {
                if (u.equals(uuid(inv.getItem(i)))) {
                    inv.setItem(i, ItemStack.EMPTY);
                }
            }
        }
        for (ItemEntity it : nivel.getEntitiesOfClass(ItemEntity.class, n.getBoundingBox().inflate(96, 48, 96),
                it -> u.equals(uuid(it.getItem())))) {
            it.discard();
        }
        for (Map.Entry<UUID, CorchoAbismoEntity> e : CORCHOS.entrySet()) {
            if (e.getValue().level() == nivel) {
                e.getValue().discard();
                CORCHOS.remove(e.getKey());
            }
        }
    }

    /** El corcho que tiene lanzado este jugador (vivo), o null. */
    static @Nullable CorchoAbismoEntity corcho(Player p) {
        CorchoAbismoEntity c = CORCHOS.get(p.getUUID());
        if (c != null && c.isRemoved()) {
            CORCHOS.remove(p.getUUID());
            return null;
        }
        return c;
    }

    static void ponerCorcho(Player p, CorchoAbismoEntity c) {
        CORCHOS.put(p.getUUID(), c);
    }

    static void quitarCorcho(UUID jugador, CorchoAbismoEntity c) {
        CORCHOS.remove(jugador, c);
    }
}
