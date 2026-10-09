package com.atalaya.item;

import com.atalaya.entity.MinijuegosRajang;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.ItemUseAnimation;
import net.minecraft.world.level.Level;
import org.jspecify.annotations.Nullable;

/**
 * El Prisma de Jade (El Rayo del Prisma de Rajang, octubre de 2026): mientras
 * se mantiene el clic derecho pinta un punto de luz donde se mira, y Rajang,
 * como un gato con un puntero, no puede evitar saltar sobre el. La luz la lleva
 * RajangEntity (que mira cada tick si alguien lo esta usando). Solo existe
 * mientras dura el minijuego; se pasa a otro soltandolo con la Q.
 */
public class PrismaJadeItem extends Item {

    public PrismaJadeItem(Properties propiedades) {
        super(propiedades);
    }

    @Override
    public InteractionResult use(Level nivel, Player p, InteractionHand mano) {
        ItemStack s = p.getItemInHand(mano);
        if (nivel instanceof ServerLevel && !MinijuegosRajang.vivo(s, MinijuegosRajang.PRISMA)) {
            s.setCount(0);
            return InteractionResult.FAIL;
        }
        p.startUsingItem(mano);
        return InteractionResult.CONSUME;
    }

    @Override
    public int getUseDuration(ItemStack s, LivingEntity quien) {
        return 72000;
    }

    @Override
    public ItemUseAnimation getUseAnimation(ItemStack s) {
        return ItemUseAnimation.NONE;
    }

    @Override
    public void inventoryTick(ItemStack stack, ServerLevel nivel, Entity quien, @Nullable EquipmentSlot ranura) {
        super.inventoryTick(stack, nivel, quien, ranura);
        if (!MinijuegosRajang.vivo(stack, MinijuegosRajang.PRISMA)) {
            stack.setCount(0);
        }
    }
}
