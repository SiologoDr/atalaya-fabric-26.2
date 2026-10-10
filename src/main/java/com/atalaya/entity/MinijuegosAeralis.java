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
import net.minecraft.world.item.component.CustomModelData;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;
import java.util.List;
import org.jspecify.annotations.Nullable;

/**
 * Los minijuegos de Aeralis (octubre de 2026). Juan eligio tres de la tercera
 * ficha de mecanicas (Ocelos, Pararrayos y Veletas del Vendaval) y La Chispa de
 * la cuarta, y pidio ponerlos en las fases que no tienen nada interactivo: la I
 * (la II tiene la Rafaga Ladrona y la III el Juicio del Ciclon) y la IV. Los
 * de viento en la I y los de rayo en la IV. Uno a la vez, como los de los
 * otros jefes, y como las fases se suman, en la IV pueden salir todos. Cada uno
 * vive en su clase (OcelosAeralis, VeletasAeralis, PararrayosAeralis,
 * ChispaAeralis).
 *
 * Aqui esta tambien lo de los pararrayos que reparte: cada uno lleva dentro de
 * que Aeralis es, y si esa Aeralis ya no esta en el minijuego, se deshace.
 */
public final class MinijuegosAeralis {

    public static final int NINGUNO = 0;
    public static final int OCELOS = 1;
    public static final int VELETAS = 2;
    public static final int PARARRAYOS = 3;
    public static final int CHISPA = 4;
    /** La fase desde la que sale cada uno. */
    static final int[] FASE = {0, 1, 1, 4, 4};
    /** Su nombre en las claves de texto. */
    public static final String[] CLAVES = {"", "ocelos", "veletas", "pararrayos", "chispa"};

    /** Los Ocelos: cerrados, a punto de abrirse o mirando. */
    public static final int OJOS_CERRADOS = 0;
    public static final int OJOS_AVISO = 1;
    public static final int OJOS_ABIERTOS = 2;

    private static final Map<UUID, AeralisEntity> ACTIVOS = new ConcurrentHashMap<>();
    private static final String CLAVE = "aeralis";
    private static final String CARGA = "carga";

    private MinijuegosAeralis() {
    }

    static void activar(AeralisEntity a) {
        ACTIVOS.put(a.getUUID(), a);
    }

    static void desactivar(AeralisEntity a) {
        ACTIVOS.remove(a.getUUID());
    }

    /** Un objeto del minijuego de esta Aeralis. */
    static ItemStack crear(AeralisEntity a, Item item) {
        ItemStack s = new ItemStack(item);
        CompoundTag t = new CompoundTag();
        t.putString(CLAVE, a.getUUID().toString());
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

    /** La Aeralis de este objeto, si sigue en un minijuego; si no, null. */
    public static @Nullable AeralisEntity de(ItemStack s) {
        UUID u = uuid(s);
        AeralisEntity a = u == null ? null : ACTIVOS.get(u);
        return a != null && !a.isRemoved() && !a.isDeadOrDying() && a.minijuego() != NINGUNO ? a : null;
    }

    /** Si el objeto sigue valiendo: su Aeralis esta en este minijuego. */
    public static boolean vivo(ItemStack s, int tipo) {
        AeralisEntity a = de(s);
        return a != null && a.minijuego() == tipo;
    }

    /** Lo pone en la mano principal si esta libre; si no, en el inventario, o a sus pies. */
    static void dar(Player p, ItemStack s) {
        if (p.getMainHandItem().isEmpty()) {
            p.setItemInHand(net.minecraft.world.InteractionHand.MAIN_HAND, s);
        } else if (!p.getInventory().add(s)) {
            p.drop(s, false);
        }
    }

    /** Si lleva en alguna mano un objeto de esta Aeralis. */
    static boolean enMano(Player p, AeralisEntity a, Item item) {
        UUID u = a.getUUID();
        for (ItemStack s : new ItemStack[]{p.getMainHandItem(), p.getOffhandItem()}) {
            if (s.is(item) && u.equals(uuid(s))) {
                return true;
            }
        }
        return false;
    }

    /** Si lleva en el inventario (en cualquier sitio) un objeto de esta Aeralis. */
    static boolean tiene(Player p, AeralisEntity a, Item item) {
        UUID u = a.getUUID();
        Inventory inv = p.getInventory();
        for (int i = 0; i < inv.getContainerSize(); i++) {
            ItemStack s = inv.getItem(i);
            if (s.is(item) && u.equals(uuid(s))) {
                return true;
            }
        }
        return false;
    }

    /** Quita de todos los inventarios y del suelo los objetos de esta Aeralis. */
    static void quitarTodo(ServerLevel nivel, AeralisEntity a) {
        UUID u = a.getUUID();
        for (Player p : nivel.players()) {
            Inventory inv = p.getInventory();
            for (int i = 0; i < inv.getContainerSize(); i++) {
                if (u.equals(uuid(inv.getItem(i)))) {
                    inv.setItem(i, ItemStack.EMPTY);
                }
            }
        }
        for (ItemEntity it : nivel.getEntitiesOfClass(ItemEntity.class, a.getBoundingBox().inflate(96, 48, 96),
                it -> u.equals(uuid(it.getItem())))) {
            it.discard();
        }
    }

    /**
     * Alguien pega a una entidad (AttackEntityCallback, en el servidor): si lleva
     * la Chispa, se la pasa (a quien le pega o al que tenga en la mira). Devuelve
     * si el golpe se queda en eso (sin dano).
     */
    public static boolean alAtacar(Player p, net.minecraft.world.entity.Entity blanco) {
        for (AeralisEntity a : ACTIVOS.values()) {
            if (!a.isRemoved() && a.level() == p.level() && a.minijuegoEnMarcha() instanceof ChispaAeralis c) {
                if (c.alAtacar(p, blanco)) {
                    return true;
                }
            }
        }
        return false;
    }

    /**
     * Alguien da un clic izquierdo (al aire, a un bloque o a una entidad; llega
     * como "mueve el brazo", TranceClicMixin): con la Chispa, la lanza al que
     * mira; cargado de un Pararrayos, descarga el rayo en Aeralis si la mira.
     * Asi no hace falta llegarle con la mano: vuela bajo, pero vuela.
     */
    public static void alBlandir(Player p) {
        if (p.isSpectator()) {
            return;
        }
        for (AeralisEntity a : ACTIVOS.values()) {
            if (!a.isRemoved() && a.level() == p.level()) {
                MinijuegoAeralis m = a.minijuegoEnMarcha();
                if (m instanceof ChispaAeralis c) {
                    c.alBlandir(p);
                } else if (m instanceof PararrayosAeralis pr) {
                    pr.alBlandir(p);
                }
            }
        }
    }

    /** Si p mira a e (su caja, algo agrandada) a menos de 'alcance' bloques. */
    static boolean apunta(Player p, Entity e, double alcance) {
        Vec3 ojo = p.getEyePosition();
        Vec3 fin = ojo.add(p.getLookAngle().scale(alcance));
        AABB caja = e.getBoundingBox().inflate(0.6);
        return caja.contains(ojo) || caja.clip(ojo, fin).isPresent();
    }

    /** De los candidatos, el que p tiene mas en la mira (a su pecho) dentro del cono y del alcance; null si ninguno. */
    static <T extends Entity> T enLaMira(Player p, List<T> candidatos, double alcance, double cosMin) {
        Vec3 ojo = p.getEyePosition();
        Vec3 mira = p.getLookAngle();
        T mejor = null;
        double mejorCos = cosMin;
        for (T e : candidatos) {
            if (e == p || e.isRemoved()) {
                continue;
            }
            Vec3 d = new Vec3(e.getX(), e.getY() + e.getBbHeight() * 0.6, e.getZ()).subtract(ojo);
            double l = d.length();
            if (l > alcance || l < 1.0E-3) {
                continue;
            }
            double c = d.dot(mira) / l;
            // A igual punteria, el de mas cerca (un pelo de ventaja por bloque).
            c += (alcance - l) * 0.0005;
            if (c > mejorCos) {
                mejorCos = c;
                mejor = e;
            }
        }
        return mejor;
    }

    /**
     * La carga de un Pararrayos en los de este jugador (de esta Aeralis): se ve
     * (otro dibujo, por el custom_model_data) y la pantalla sabe hasta cuando
     * (fin, en tiempo del mundo; 0 la quita).
     */
    static void marcarCarga(Player p, AeralisEntity a, Item item, long fin) {
        UUID u = a.getUUID();
        Inventory inv = p.getInventory();
        for (int i = 0; i < inv.getContainerSize(); i++) {
            ItemStack s = inv.getItem(i);
            if (!s.is(item) || !u.equals(uuid(s))) {
                continue;
            }
            CompoundTag t = s.getOrDefault(DataComponents.CUSTOM_DATA, CustomData.EMPTY).copyTag();
            if (fin > 0) {
                t.putLong(CARGA, fin);
                s.set(DataComponents.CUSTOM_MODEL_DATA, new CustomModelData(List.of(), List.of(true), List.of(), List.of()));
            } else {
                t.remove(CARGA);
                s.remove(DataComponents.CUSTOM_MODEL_DATA);
            }
            s.set(DataComponents.CUSTOM_DATA, CustomData.of(t));
        }
    }

    /** Hasta cuando esta cargado este pararrayos (tiempo del mundo; 0: no lo esta). */
    public static long finCarga(ItemStack s) {
        CustomData d = s.get(DataComponents.CUSTOM_DATA);
        return d == null ? 0L : d.copyTag().getLongOr(CARGA, 0L);
    }

    // --- El dato del minijuego (DATA_MINI_INFO) de cada uno ---

    /** Los Ocelos: como estan los ojos (OJOS_*) y cuanto estan abiertos (0 a 100). */
    public static int infoOcelos(int ojos, int apertura) {
        return (ojos & 3) | ((apertura & 127) << 2);
    }

    public static int ojosOcelos(int info) {
        return info & 3;
    }

    /** La Chispa: los segundos que le quedan a quien la lleva (0: vuela o no hay) y si esta cargada. */
    public static int infoChispa(int segundos, boolean cargada) {
        return (segundos & 15) | (cargada ? 16 : 0);
    }

    public static int segundosChispa(int info) {
        return info & 15;
    }

    public static boolean cargadaChispa(int info) {
        return (info & 16) != 0;
    }
}
