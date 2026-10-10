package com.atalaya.item;

import com.atalaya.entity.MinijuegosAeralis;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import org.jspecify.annotations.Nullable;

/**
 * El Pararrayos de la Tormenta (los Pararrayos de Aeralis, octubre de 2026):
 * quien lo lleve en la mano dentro de un circulo se lleva el rayo sin dano y
 * queda cargado. Lo que pasa lo decide PararrayosAeralis. Solo existe mientras
 * dura el minijuego; se pasa a otro soltandolo con la Q.
 */
public class PararrayosTormentaItem extends Item {

    public PararrayosTormentaItem(Properties propiedades) {
        super(propiedades);
    }

    @Override
    public void inventoryTick(ItemStack stack, ServerLevel nivel, Entity quien, @Nullable EquipmentSlot ranura) {
        super.inventoryTick(stack, nivel, quien, ranura);
        if (!MinijuegosAeralis.vivo(stack, MinijuegosAeralis.PARARRAYOS)) {
            stack.setCount(0);
        }
    }
}
