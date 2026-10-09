package com.atalaya.item;

import com.atalaya.entity.MinijuegosNerea;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import org.jspecify.annotations.Nullable;

/**
 * La Bala de canon (los Canones del Naufragio de Nerea, octubre de 2026): se
 * coge de la pila y se mete en el canon con clic derecho. Solo existe mientras
 * duran los canones.
 */
public class BalaCanonItem extends Item {

    public BalaCanonItem(Properties propiedades) {
        super(propiedades);
    }

    @Override
    public void inventoryTick(ItemStack stack, ServerLevel nivel, Entity quien, @Nullable EquipmentSlot ranura) {
        super.inventoryTick(stack, nivel, quien, ranura);
        if (!MinijuegosNerea.vivo(stack, MinijuegosNerea.CANONES)) {
            stack.setCount(0);
        }
    }
}
