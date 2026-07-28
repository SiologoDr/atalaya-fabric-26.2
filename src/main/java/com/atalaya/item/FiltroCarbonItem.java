package com.atalaya.item;

import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;

/**
 * Filtro de carbon: se usa con click derecho para cambiar el cartucho del traje.
 *
 * No se repara en yunque a proposito. Ademas de que cambiar un cartucho encaja
 * mejor que "arreglar una armadura a martillazos", el yunque tiene un problema
 * de vanilla: encarece cada reparacion y a los 40 niveles se planta con
 * "Demasiado caro". Un traje pensado para repararse de continuo quedaria
 * inservible por diseno.
 *
 * Y al no depender de un bloque, puedes cambiar el filtro DENTRO de la geoda,
 * con el traje fallando, que es justo donde la mecanica tiene gracia.
 */
public class FiltroCarbonItem extends Item {

    /**
     * Durabilidad que devuelve un filtro. Un cartucho = una carga fija.
     *
     * Es la mitad de la durabilidad de una pieza (200), asi que dos filtros la
     * dejan como nueva sin desperdiciar nada.
     */
    private static final int REPARACION = 100;

    public FiltroCarbonItem(Properties propiedades) {
        super(propiedades);
    }

    @Override
    public InteractionResult use(Level nivel, Player jugador, InteractionHand mano) {
        ItemStack filtro = jugador.getItemInHand(mano);

        ItemStack objetivo = piezaMasDanada(jugador);
        if (objetivo == null) {
            // Nada que rellenar: no gastamos el filtro.
            avisar(jugador, Component.literal("El traje no necesita un filtro nuevo.")
                    .withStyle(ChatFormatting.GRAY));
            return InteractionResult.FAIL;
        }

        if (nivel.isClientSide()) {
            return InteractionResult.SUCCESS;
        }

        int antes = objetivo.getDamageValue();
        objetivo.setDamageValue(Math.max(0, antes - REPARACION));

        if (!jugador.hasInfiniteMaterials()) {
            filtro.shrink(1);
        }

        // Sonido de cambio de cartucho: enganche metalico + siseo de aire.
        nivel.playSound(null, jugador.blockPosition(),
                SoundEvents.ARMOR_EQUIP_IRON.value(), SoundSource.PLAYERS, 0.9f, 1.4f);
        nivel.playSound(null, jugador.blockPosition(),
                SoundEvents.BOTTLE_FILL_DRAGONBREATH, SoundSource.PLAYERS, 0.5f, 1.6f);

        int recuperado = antes - objetivo.getDamageValue();
        avisar(jugador, Component.literal("Filtro cambiado (+" + recuperado + ")")
                .withStyle(ChatFormatting.GREEN));

        return InteractionResult.SUCCESS;
    }

    /**
     * Mensaje sobre la hotbar. Solo el ServerPlayer sabe mandarlo ahi;
     * displayClientMessage ya no existe en 26.2.
     */
    private static void avisar(Player jugador, Component texto) {
        if (jugador instanceof ServerPlayer sp) {
            sp.sendOverlayMessage(texto);
        }
    }

    /**
     * La pieza del traje mas gastada de entre las EQUIPADAS.
     *
     * Se mira solo lo equipado: un filtro sirve para el traje que llevas puesto,
     * no para el que tengas en un cofre. Devuelve null si no hay nada que
     * rellenar.
     */
    private static ItemStack piezaMasDanada(Player jugador) {
        ItemStack peor = null;
        int masDano = 0;
        for (EquipmentSlot slot : new EquipmentSlot[]{
                EquipmentSlot.HEAD, EquipmentSlot.CHEST, EquipmentSlot.LEGS, EquipmentSlot.FEET}) {
            ItemStack pieza = jugador.getItemBySlot(slot);
            if (!HazmatArmor.esPieza(pieza.getItem())) {
                continue;
            }
            int dano = pieza.getDamageValue();
            if (dano > masDano) {
                masDano = dano;
                peor = pieza;
            }
        }
        return peor;
    }
}
