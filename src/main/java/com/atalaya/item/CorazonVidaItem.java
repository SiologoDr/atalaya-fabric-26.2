package com.atalaya.item;

import com.atalaya.particula.AtalayaParticulas;
import com.atalaya.sonido.AtalayaSonidos;
import java.util.function.Consumer;
import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.item.component.TooltipDisplay;
import net.minecraft.world.level.Level;

/**
 * El Corazón de Vida (11-10-2026, Juan: "un item que te recupera todos los
 * corazones"; primero fue un elixir que se bebía, luego "cambiémoslo a un
 * corazón que se pueda comer"). Se come como la comida (su componente
 * consumable, 1,6 s), aunque tengas el hambre llena, y al acabar te deja la vida
 * llena. No da absorción, regeneración ni comida: solo eso.
 */
public class CorazonVidaItem extends Item {

    public CorazonVidaItem(Properties props) {
        super(props);
    }

    @Override
    public ItemStack finishUsingItem(ItemStack stack, Level nivel, LivingEntity quien) {
        if (nivel instanceof ServerLevel servidor) {
            quien.setHealth(quien.getMaxHealth());
            servidor.playSound(null, quien.getX(), quien.getY() + 1.0, quien.getZ(), AtalayaSonidos.OBJETO_ELIXIR,
                    SoundSource.PLAYERS, 1.0F, 1.0F);
            servidor.sendParticles(AtalayaParticulas.NOVILIS_LUZ, quien.getX(), quien.getY() + 1.0, quien.getZ(), 24, 0.35, 0.6, 0.35, 0.05);
        }
        return super.finishUsingItem(stack, nivel, quien);
    }

    @Override
    public void appendHoverText(ItemStack stack, TooltipContext contexto, TooltipDisplay mostrar,
                                Consumer<Component> linea, TooltipFlag flag) {
        super.appendHoverText(stack, contexto, mostrar, linea, flag);
        linea.accept(Component.translatable("item.atalaya.corazon_vida.efecto").withStyle(ChatFormatting.GRAY));
    }
}
