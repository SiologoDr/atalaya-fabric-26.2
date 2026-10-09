package com.atalaya.item;

import com.atalaya.entity.MinijuegosNerea;
import com.atalaya.entity.NereaEntity;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import org.jspecify.annotations.Nullable;

/**
 * La Cana del Abismo (la Pesca del Abismo de Nerea, octubre de 2026). Solo
 * existe mientras dura la pesca: clic derecho la lanza (el corcho cae en arco);
 * otro clic derecho la recoge. Si el corcho picaba en una poza, sale una Perla
 * del Abismo.
 */
public class CanaAbismoItem extends Item {

    public CanaAbismoItem(Properties propiedades) {
        super(propiedades);
    }

    @Override
    public InteractionResult use(Level nivel, Player p, InteractionHand mano) {
        ItemStack s = p.getItemInHand(mano);
        if (nivel instanceof ServerLevel sn) {
            NereaEntity n = MinijuegosNerea.de(s);
            if (n == null || n.minijuego() != MinijuegosNerea.PESCA) {
                s.setCount(0);
                return InteractionResult.FAIL;
            }
            n.usarCana(sn, p);
        }
        return InteractionResult.SUCCESS;
    }

    @Override
    public void inventoryTick(ItemStack stack, ServerLevel nivel, Entity quien, @Nullable EquipmentSlot ranura) {
        super.inventoryTick(stack, nivel, quien, ranura);
        if (!MinijuegosNerea.vivo(stack, MinijuegosNerea.PESCA)) {
            stack.setCount(0);
        }
    }
}
