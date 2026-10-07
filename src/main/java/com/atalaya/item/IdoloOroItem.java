package com.atalaya.item;

import com.atalaya.entity.IdoloOro;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import org.jspecify.annotations.Nullable;

/**
 * El Idolo de Oro de Rajang. No es un trofeo: solo existe mientras su Rajang lo
 * busca; si no, en cuanto alguien lo tiene en el inventario se deshace.
 */
public class IdoloOroItem extends Item {

    public IdoloOroItem(Properties propiedades) {
        super(propiedades);
    }

    @Override
    public void inventoryTick(ItemStack stack, ServerLevel nivel, Entity quien, @Nullable EquipmentSlot ranura) {
        super.inventoryTick(stack, nivel, quien, ranura);
        if (!IdoloOro.vivo(stack)) {
            stack.setCount(0);
        }
    }
}
