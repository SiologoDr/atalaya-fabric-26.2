package com.atalaya.mixin;

import com.atalaya.config.AtalayaConfig;
import com.atalaya.item.HazmatArmor;
import net.minecraft.network.protocol.game.ClientboundContainerSetSlotPacket;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.inventory.AbstractContainerMenu;
import net.minecraft.world.inventory.CraftingContainer;
import net.minecraft.world.inventory.CraftingMenu;
import net.minecraft.world.inventory.ResultContainer;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.crafting.CraftingRecipe;
import net.minecraft.world.item.crafting.RecipeHolder;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/**
 * Hace cumplir el interruptor de crafteo del menu.
 *
 * Las recetas son datos y no se pueden quitar del juego en caliente, asi que
 * vaciamos la casilla de resultado cuando el interruptor esta apagado.
 *
 * Se inyecta al FINAL y no al principio a proposito: el parametro
 * RecipeHolder que recibe el metodo es solo una PISTA de la receta usada la vez
 * anterior (suele venir null), porque la busqueda de verdad la hace dentro con
 * RecipeManager.getRecipeFor(...). Por eso no sirve mirar ese parametro:
 * hay que mirar el item que ha quedado en la casilla de salida.
 *
 * Como el metodo original ya mando el resultado al cliente, hay que reenviar
 * el paquete con la casilla vacia; si no, el cliente seguiria dibujando el item.
 */
@Mixin(CraftingMenu.class)
public class CraftingMenuMixin {

    private static final int SLOT_RESULTADO = 0;

    @Inject(method = "slotChangedCraftingGrid", at = @At("RETURN"))
    private static void atalaya$bloquearSiEstaDesactivado(
            AbstractContainerMenu menu,
            ServerLevel nivel,
            Player jugador,
            CraftingContainer rejilla,
            ResultContainer resultado,
            RecipeHolder<CraftingRecipe> pistaReceta,
            CallbackInfo ci) {

        // Salida temprana en el caso normal (crafteo activado): una lectura de
        // boolean. Mientras nadie apague el interruptor, este mixin no cuesta nada.
        if (AtalayaConfig.get().isCrafteoHazmat()) {
            return;
        }

        ItemStack salida = resultado.getItem(SLOT_RESULTADO);
        if (salida.isEmpty() || !HazmatArmor.esPieza(salida.getItem())) {
            return; // vacio o receta ajena: no tocamos nada
        }

        resultado.setItem(SLOT_RESULTADO, ItemStack.EMPTY);
        menu.setRemoteSlot(SLOT_RESULTADO, ItemStack.EMPTY);
        if (jugador instanceof ServerPlayer sp) {
            sp.connection.send(new ClientboundContainerSetSlotPacket(
                    menu.containerId, menu.incrementStateId(), SLOT_RESULTADO, ItemStack.EMPTY));
        }
    }

}
