package com.atalaya.entity;

import com.atalaya.item.AtalayaItems;
import com.atalaya.sonido.AtalayaSonidos;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import net.fabricmc.fabric.api.event.player.AttackEntityCallback;
import net.minecraft.ChatFormatting;
import net.minecraft.core.component.DataComponents;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.component.CustomData;
import org.jspecify.annotations.Nullable;

/**
 * El Idolo de Oro de Rajang (octubre de 2026): lo arranca de su templo y lo
 * lanza; quien lo coge tiene que llevarlo al altar mientras el le persigue. Es
 * un objeto de verdad: se suelta con la Q y se recoge andando por encima, y
 * quien lo lleva se lo pasa a un companero dandole un clic (sin hacerle dano).
 *
 * Cada idolo lleva dentro de que Rajang es; si ese Rajang ya no lo busca, el
 * idolo se deshace (IdoloOroItem). Aqui estan el indice de los Rajang con el
 * idolo fuera y las ayudas para encontrarlo.
 */
public final class IdoloOro {

    private static final Map<UUID, RajangEntity> ACTIVOS = new ConcurrentHashMap<>();
    private static final String CLAVE = "rajang";

    private IdoloOro() {
    }

    static void activar(RajangEntity r) {
        ACTIVOS.put(r.getUUID(), r);
    }

    static void desactivar(RajangEntity r) {
        ACTIVOS.remove(r.getUUID());
    }

    /** Un idolo nuevo, de este Rajang. */
    static ItemStack crear(RajangEntity r) {
        ItemStack s = new ItemStack(AtalayaItems.IDOLO_ORO);
        CompoundTag t = new CompoundTag();
        t.putString(CLAVE, r.getUUID().toString());
        s.set(DataComponents.CUSTOM_DATA, CustomData.of(t));
        return s;
    }

    public static boolean es(ItemStack s) {
        return !s.isEmpty() && s.is(AtalayaItems.IDOLO_ORO);
    }

    private static @Nullable UUID de(ItemStack s) {
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

    /** Hay un Rajang que todavia busca este idolo. */
    public static boolean vivo(ItemStack s) {
        UUID u = de(s);
        RajangEntity r = u == null ? null : ACTIVOS.get(u);
        return r != null && !r.isRemoved() && !r.isDeadOrDying() && r.idoloFuera();
    }

    private static boolean deRajang(ItemStack s, RajangEntity r) {
        return es(s) && r.getUUID().equals(de(s));
    }

    /** Quien lleva el idolo de este Rajang (a 96 bloques), o null. */
    static @Nullable Player portador(ServerLevel nivel, RajangEntity r) {
        for (Player p : nivel.players()) {
            if (p.isAlive() && p.distanceToSqr(r) < 96 * 96 && hueco(p.getInventory(), r) >= 0) {
                return p;
            }
        }
        return null;
    }

    /** El idolo de este Rajang tirado en el suelo, o null. */
    static @Nullable ItemEntity enSuelo(ServerLevel nivel, RajangEntity r) {
        for (ItemEntity it : nivel.getEntitiesOfClass(ItemEntity.class, r.getBoundingBox().inflate(96, 48, 96),
                it -> deRajang(it.getItem(), r))) {
            return it;
        }
        return null;
    }

    private static int hueco(Inventory inv, RajangEntity r) {
        for (int i = 0; i < inv.getContainerSize(); i++) {
            if (deRajang(inv.getItem(i), r)) {
                return i;
            }
        }
        return -1;
    }

    /** Le quita el idolo a quien lo lleve. */
    static void quitar(Player p, RajangEntity r) {
        int i = hueco(p.getInventory(), r);
        if (i >= 0) {
            p.getInventory().setItem(i, ItemStack.EMPTY);
        }
    }

    /** Se acaba: fuera el idolo de todos los inventarios cercanos y del suelo. */
    static void quitarTodos(ServerLevel nivel, RajangEntity r) {
        for (Player p : nivel.players()) {
            quitar(p, r);
        }
        ItemEntity it;
        while ((it = enSuelo(nivel, r)) != null) {
            it.discard();
        }
    }

    public static void registrar() {
        // Pasarlo de mano en mano: quien lo lleva le da un clic a un companero (no le hace dano).
        AttackEntityCallback.EVENT.register((jugador, nivel, mano, entidad, golpe) -> {
            if (nivel.isClientSide() || !(entidad instanceof Player otro) || otro.isSpectator() || !otro.isAlive()) {
                return InteractionResult.PASS;
            }
            Inventory inv = jugador.getInventory();
            for (int i = 0; i < inv.getContainerSize(); i++) {
                ItemStack s = inv.getItem(i);
                if (es(s) && vivo(s)) {
                    inv.setItem(i, ItemStack.EMPTY);
                    if (!otro.getInventory().add(s)) {
                        otro.drop(s, false);
                    }
                    ServerLevel sn = (ServerLevel) nivel;
                    sn.playSound(null, otro.getX(), otro.getEyeY(), otro.getZ(), AtalayaSonidos.RAJANG_TOTEM, SoundSource.PLAYERS,
                            1.5F, 1.4F);
                    otro.sendOverlayMessage(Component.translatable("hud.atalaya.rajang.idolo_portador").withStyle(ChatFormatting.GOLD));
                    return InteractionResult.FAIL;
                }
            }
            return InteractionResult.PASS;
        });
    }
}
