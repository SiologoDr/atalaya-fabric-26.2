package com.atalaya.item;

import java.util.function.Consumer;
import net.minecraft.ChatFormatting;
import net.minecraft.core.component.DataComponents;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.item.component.TooltipDisplay;

/**
 * Un tótem del mod (TotemJefe): un objeto con death_protection, así que lo que
 * hace al salvarte lo pone el juego, y lo de alrededor, AvisoTotemMixin. Su ficha
 * dice qué hace.
 */
public class TotemJefeItem extends Item {

    public final TotemJefe totem;

    public TotemJefeItem(TotemJefe totem, Properties props) {
        super(props);
        this.totem = totem;
    }

    @Override
    public void appendHoverText(ItemStack stack, TooltipContext contexto, TooltipDisplay mostrar,
                                Consumer<Component> linea, TooltipFlag flag) {
        super.appendHoverText(stack, contexto, mostrar, linea, flag);
        linea.accept(Component.translatable("item.atalaya.totem.salva").withStyle(ChatFormatting.GRAY));
        linea.accept(Component.translatable("item.atalaya.totem_" + totem.id + ".efecto").withStyle(ChatFormatting.GOLD));
        if (totem == TotemJefe.DOS_VIDAS) {
            boolean dos = stack.getOrDefault(DataComponents.ENCHANTMENT_GLINT_OVERRIDE, false);
            linea.accept(Component.translatable(dos ? "item.atalaya.totem_dos_vidas.quedan_2" : "item.atalaya.totem_dos_vidas.queda_1")
                    .withStyle(ChatFormatting.YELLOW));
        }
    }
}
