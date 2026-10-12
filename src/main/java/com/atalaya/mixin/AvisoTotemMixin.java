package com.atalaya.mixin;

import com.atalaya.item.TotemJefe;
import com.llamalad7.mixinextras.sugar.Local;
import net.minecraft.ChatFormatting;
import net.minecraft.core.component.DataComponents;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.data.AtlasIds;
import net.minecraft.network.chat.Component;
import net.minecraft.network.chat.contents.objects.AtlasSprite;
import net.minecraft.resources.Identifier;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.ItemStack;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/**
 * Cuando un tótem salva a alguien.
 *
 * <ul>
 *   <li>Si es un jugador, lo sabe todo el servidor: "<b>Manu</b> ha usado un tótem
 *   de la inmortalidad [icono]", con el nombre en negrita y el icono del tótem
 *   dentro del propio chat (un sprite del atlas de objetos). Con los tótems de los
 *   jefes dice cuál: "<b>Manu</b> ha usado el Tótem de Rajang [icono]".</li>
 *   <li>Si es un tótem del mod (TotemJefe), hace lo suyo alrededor. Lo que te da a
 *   ti (los efectos) ya lo puso el juego con su death_protection, y las partículas,
 *   el sonido y la animación en pantalla son los del tótem de vanilla. El de Dos
 *   Vidas, la primera vez, vuelve a la mano (sin su brillo).</li>
 * </ul>
 *
 * Se engancha justo antes del aviso de vanilla a los clientes (el evento 35), con
 * el tótem que se ha gastado ya en la mano: así se sabe cuál fue.
 */
@Mixin(LivingEntity.class)
public abstract class AvisoTotemMixin {

    private static final Identifier TOTEM = Identifier.withDefaultNamespace("item/totem_of_undying");

    /** La mano del tótem que va a usar (la busca igual que vanilla: la principal y luego la otra). */
    @Unique
    private InteractionHand atalaya$mano;

    @Inject(method = "checkTotemDeathProtection", at = @At("HEAD"))
    private void atalaya$buscarMano(DamageSource fuente, CallbackInfoReturnable<Boolean> cir) {
        LivingEntity yo = (LivingEntity) (Object) this;
        atalaya$mano = null;
        for (InteractionHand mano : InteractionHand.values()) {
            if (yo.getItemInHand(mano).has(DataComponents.DEATH_PROTECTION)) {
                atalaya$mano = mano;
                return;
            }
        }
    }

    @Inject(method = "checkTotemDeathProtection", at = @At(value = "INVOKE",
            target = "Lnet/minecraft/world/level/Level;broadcastEntityEvent(Lnet/minecraft/world/entity/Entity;B)V"))
    private void atalaya$alSalvar(DamageSource fuente, CallbackInfoReturnable<Boolean> cir, @Local(ordinal = 0) ItemStack usado) {
        LivingEntity yo = (LivingEntity) (Object) this;
        TotemJefe totem = TotemJefe.de(usado);
        if (yo instanceof ServerPlayer jugador) {
            Component nombre = jugador.getDisplayName().copy().withStyle(ChatFormatting.BOLD);
            Component aviso;
            if (totem == null) {
                Component icono = Component.object(new AtlasSprite(AtlasIds.ITEMS, TOTEM));
                aviso = Component.translatable("chat.atalaya.totem", nombre, icono).withStyle(ChatFormatting.YELLOW);
            } else {
                Identifier id = BuiltInRegistries.ITEM.getKey(usado.getItem());
                Component icono = Component.object(new AtlasSprite(AtlasIds.ITEMS,
                        Identifier.fromNamespaceAndPath(id.getNamespace(), "item/" + id.getPath())));
                Component cual = usado.getHoverName().copy().withStyle(ChatFormatting.GOLD);
                aviso = Component.translatable("chat.atalaya.totem_jefe", nombre, cual, icono).withStyle(ChatFormatting.YELLOW);
            }
            jugador.level().getServer().getPlayerList().broadcastSystemMessage(aviso, false);
        }
        if (totem != null && yo.level() instanceof ServerLevel nivel) {
            totem.alSalvar(nivel, yo);
            // El de Dos Vidas: la primera vez vuelve a la mano, ya sin brillo (le queda una).
            if (totem == TotemJefe.DOS_VIDAS && atalaya$mano != null && yo.getItemInHand(atalaya$mano).isEmpty()
                    && usado.getOrDefault(DataComponents.ENCHANTMENT_GLINT_OVERRIDE, false)) {
                ItemStack queda = usado.copyWithCount(1);
                queda.set(DataComponents.ENCHANTMENT_GLINT_OVERRIDE, false);
                yo.setItemInHand(atalaya$mano, queda);
            }
        }
    }
}
