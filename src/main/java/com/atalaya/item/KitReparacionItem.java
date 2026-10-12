package com.atalaya.item;

import com.atalaya.particula.AtalayaParticulas;
import com.atalaya.sonido.AtalayaSonidos;
import java.util.function.Consumer;
import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.item.component.TooltipDisplay;
import net.minecraft.world.level.Level;

/**
 * El Kit de Reparación (11-10-2026, Juan: "un item para reparar la armadura de
 * un compañero, que no se pueda a ti mismo"). Clic derecho sobre otro jugador:
 * le deja nuevas las piezas de armadura que lleve puestas, y se gasta uno. Sobre
 * ti mismo, al aire o sobre otra cosa no hace nada (te lo dice). Si su armadura
 * no tiene ni un rasguño, tampoco se gasta.
 */
public class KitReparacionItem extends Item {

    private static final EquipmentSlot[] ARMADURA = {EquipmentSlot.HEAD, EquipmentSlot.CHEST, EquipmentSlot.LEGS,
            EquipmentSlot.FEET};

    public KitReparacionItem(Properties props) {
        super(props);
    }

    @Override
    public InteractionResult interactLivingEntity(ItemStack kit, Player jugador, LivingEntity objetivo, InteractionHand mano) {
        if (!(objetivo instanceof Player compa) || compa == jugador) {
            return InteractionResult.PASS;
        }
        if (!(jugador.level() instanceof ServerLevel nivel)) {
            return InteractionResult.SUCCESS;
        }
        int piezas = 0;
        for (EquipmentSlot hueco : ARMADURA) {
            ItemStack pieza = compa.getItemBySlot(hueco);
            if (!pieza.isEmpty() && pieza.isDamageableItem() && pieza.isDamaged()) {
                pieza.setDamageValue(0);
                piezas++;
            }
        }
        if (piezas == 0) {
            jugador.sendOverlayMessage(Component.translatable("item.atalaya.kit_reparacion.entera", compa.getDisplayName())
                    .withStyle(ChatFormatting.YELLOW));
            return InteractionResult.FAIL;
        }
        nivel.playSound(null, compa.getX(), compa.getY() + 1.0, compa.getZ(), AtalayaSonidos.OBJETO_REPARAR,
                SoundSource.PLAYERS, 1.0F, 0.95F + nivel.getRandom().nextFloat() * 0.1F);
        // Las chispas del martillo y un brillo de metal nuevo (partículas propias).
        nivel.sendParticles(AtalayaParticulas.VIGIA_CHISPA, compa.getX(), compa.getY() + 1.0, compa.getZ(), 18, 0.35, 0.5, 0.35, 0.15);
        nivel.sendParticles(AtalayaParticulas.RAJANG_ORO, compa.getX(), compa.getY() + 1.0, compa.getZ(), 12, 0.4, 0.6, 0.4, 0.05);
        jugador.sendOverlayMessage(Component.translatable("item.atalaya.kit_reparacion.hecho", compa.getDisplayName())
                .withStyle(ChatFormatting.GREEN));
        if (compa instanceof ServerPlayer sp) {
            sp.sendOverlayMessage(Component.translatable("item.atalaya.kit_reparacion.recibido", jugador.getDisplayName())
                    .withStyle(ChatFormatting.GREEN));
        }
        kit.consume(1, jugador);
        return InteractionResult.SUCCESS_SERVER;
    }

    /** Al aire (o sobre ti mismo): no sirve, solo para un compañero. */
    @Override
    public InteractionResult use(Level nivel, Player jugador, InteractionHand mano) {
        if (!nivel.isClientSide()) {
            jugador.sendOverlayMessage(Component.translatable("item.atalaya.kit_reparacion.solo_compa")
                    .withStyle(ChatFormatting.YELLOW));
        }
        return InteractionResult.FAIL;
    }

    @Override
    public void appendHoverText(ItemStack stack, TooltipContext contexto, TooltipDisplay mostrar,
                                Consumer<Component> linea, TooltipFlag flag) {
        super.appendHoverText(stack, contexto, mostrar, linea, flag);
        linea.accept(Component.translatable("item.atalaya.kit_reparacion.efecto").withStyle(ChatFormatting.GRAY));
    }
}
