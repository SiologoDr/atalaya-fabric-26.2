package com.atalaya.cambios;

import net.minecraft.core.component.DataComponents;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.component.CustomData;

import java.util.Set;

/**
 * SE PUDRE LA CARNE (DEDsafio 4): la carne, el pollo y el pescado (crudos o hechos) se pudren a los veinte minutos de
 * cogerlos: se apunta cuando entraron en el inventario y, pasado ese rato, se vuelven carne podrida.
 */
public final class CarnePodrida {

    private static final Set<Item> CARNE = Set.of(Items.BEEF, Items.COOKED_BEEF, Items.PORKCHOP, Items.COOKED_PORKCHOP,
            Items.MUTTON, Items.COOKED_MUTTON, Items.CHICKEN, Items.COOKED_CHICKEN, Items.RABBIT, Items.COOKED_RABBIT,
            Items.COD, Items.COOKED_COD, Items.SALMON, Items.COOKED_SALMON, Items.TROPICAL_FISH, Items.PUFFERFISH);
    private static final String CLAVE = "atalaya_fresca_desde";
    /** Veinte minutos de juego. */
    private static final long DURA = 20 * 60 * 20L;

    private CarnePodrida() {
    }

    static void revisar(ServerPlayer p) {
        long ahora = p.level().getGameTime();
        Inventory inv = p.getInventory();
        for (int i = 0; i < inv.getContainerSize(); i++) {
            ItemStack s = inv.getItem(i);
            if (s.isEmpty() || !CARNE.contains(s.getItem())) {
                continue;
            }
            CustomData datos = s.get(DataComponents.CUSTOM_DATA);
            CompoundTag tag = datos == null ? new CompoundTag() : datos.copyTag();
            if (!tag.contains(CLAVE)) {
                tag.putLong(CLAVE, ahora);
                s.set(DataComponents.CUSTOM_DATA, CustomData.of(tag));
                continue;
            }
            if (ahora - tag.getLongOr(CLAVE, ahora) >= DURA) {
                inv.setItem(i, new ItemStack(Items.ROTTEN_FLESH, s.getCount()));
            }
        }
    }
}
