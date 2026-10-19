package com.atalaya.item;

import com.atalaya.bestiario.CorazonesRobados;
import com.atalaya.bestiario.Fichas;
import com.atalaya.sonido.AtalayaSonidos;
import java.util.function.Consumer;
import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.item.component.TooltipDisplay;
import net.minecraft.world.level.Level;

/**
 * El Corazon Blanco (19-10-2026, Juan: «el corazon que quita el Negro se puede volver a recuperar, pero con un corazon
 * blanco, no uno dorado»). Se come como el Corazon de Vida y te devuelve, lleno, uno de los corazones que te robo el
 * Espectro Negro. Si no te falta ninguno, no se puede comer. Lo suelta el Espectro Negro al morir: uno por cada corazon
 * que habia robado.
 */
public class CorazonBlancoItem extends Item {

    public CorazonBlancoItem(Properties props) {
        super(props);
    }

    @Override
    public InteractionResult use(Level nivel, Player jugador, InteractionHand mano) {
        if (jugador.getAttachedOrCreate(CorazonesRobados.ROBADOS) <= 0) {
            if (jugador instanceof ServerPlayer p) {
                p.sendOverlayMessage(Component.translatable("item.atalaya.corazon_blanco.nada").withStyle(ChatFormatting.GRAY));
            }
            return InteractionResult.FAIL;
        }
        return super.use(nivel, jugador, mano);
    }

    @Override
    public ItemStack finishUsingItem(ItemStack stack, Level nivel, LivingEntity quien) {
        if (nivel instanceof ServerLevel servidor && quien instanceof ServerPlayer p && CorazonesRobados.devolver(p)) {
            servidor.playSound(null, p.getX(), p.getY() + 1.0, p.getZ(), AtalayaSonidos.OBJETO_ELIXIR, SoundSource.PLAYERS,
                    1.0F, 1.2F);
            servidor.sendParticles(Fichas.ESPECTRO_BLANCO.particula("alma"), p.getX(), p.getY() + 1.0, p.getZ(), 16, 0.35,
                    0.5, 0.35, 0.02);
        }
        return super.finishUsingItem(stack, nivel, quien);
    }

    @Override
    public void appendHoverText(ItemStack stack, TooltipContext contexto, TooltipDisplay mostrar,
                                Consumer<Component> linea, TooltipFlag flag) {
        super.appendHoverText(stack, contexto, mostrar, linea, flag);
        linea.accept(Component.translatable("item.atalaya.corazon_blanco.efecto").withStyle(ChatFormatting.GRAY));
    }
}
