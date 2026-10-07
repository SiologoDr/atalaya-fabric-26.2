package com.atalaya.client;

import com.atalaya.Atalaya;
import com.atalaya.habilidad.Habilidades;
import com.atalaya.item.ArmadurasJefes;
import com.atalaya.net.AtalayaRed;
import com.mojang.blaze3d.platform.InputConstants;
import net.fabricmc.fabric.api.client.event.lifecycle.v1.ClientTickEvents;
import net.fabricmc.fabric.api.client.item.v1.ItemTooltipCallback;
import net.fabricmc.fabric.api.client.keymapping.v1.KeyMappingHelper;
import net.fabricmc.fabric.api.client.networking.v1.ClientPlayNetworking;
import net.minecraft.ChatFormatting;
import net.minecraft.client.KeyMapping;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.Identifier;
import net.minecraft.world.item.Item;
import org.lwjgl.glfw.GLFW;

import java.util.List;
import java.util.Map;

/**
 * Lo del cliente de las habilidades de las armaduras: la tecla (R por defecto,
 * se cambia en Controles, categoria Atalaya), que solo avisa al servidor (el
 * decide si hay conjunto y si esta lista), y lo que dicen las piezas y las
 * armas al pasar el raton por encima.
 */
public final class HabilidadCliente {

    public static final KeyMapping.Category CATEGORIA = KeyMapping.Category.register(
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "atalaya"));
    public static KeyMapping TECLA;

    private static final Map<ArmadurasJefes.Tema, ChatFormatting> COLOR = Map.of(
            ArmadurasJefes.Tema.MAREAS, ChatFormatting.AQUA,
            ArmadurasJefes.Tema.JADE, ChatFormatting.GREEN,
            ArmadurasJefes.Tema.VENDAVAL, ChatFormatting.LIGHT_PURPLE,
            ArmadurasJefes.Tema.SOLAR, ChatFormatting.GOLD);

    private HabilidadCliente() {
    }

    public static void registrar() {
        TECLA = KeyMappingHelper.registerKeyMapping(new KeyMapping("key.atalaya.habilidad", InputConstants.Type.KEYSYM,
                GLFW.GLFW_KEY_R, CATEGORIA));
        ClientTickEvents.END_CLIENT_TICK.register(mc -> {
            while (TECLA.consumeClick()) {
                if (mc.player != null && Habilidades.conjunto(mc.player) != null) {
                    ClientPlayNetworking.send(new AtalayaRed.Habilidad());
                }
            }
        });
        ItemTooltipCallback.EVENT.register((stack, contexto, flag, lineas) -> describir(stack.getItem(), lineas));
    }

    private static void describir(Item item, List<Component> lineas) {
        ArmadurasJefes.Tema tema = ArmadurasJefes.temaDe(item);
        if (tema != null) {
            ChatFormatting color = COLOR.get(tema);
            lineas.add(Component.empty());
            lineas.add(Component.translatable("habilidad.atalaya.conjunto").withStyle(ChatFormatting.GRAY)
                    .append(Component.literal(" "))
                    .append(Component.translatable("habilidad.atalaya.rol." + tema.id).withStyle(color, ChatFormatting.BOLD)));
            lineas.add(Component.translatable("habilidad.atalaya.pasiva." + tema.id).withStyle(color));
            Component tecla = TECLA != null ? TECLA.getTranslatedKeyMessage() : Component.literal("R");
            lineas.add(Component.translatable("habilidad.atalaya.activa." + tema.id, tecla).withStyle(color));
            lineas.add(Component.translatable("habilidad.atalaya.recarga_info").withStyle(ChatFormatting.DARK_GRAY));
            return;
        }
        for (Map.Entry<ArmadurasJefes.Tema, Item> arma : ArmadurasJefes.ARMAS.entrySet()) {
            if (arma.getValue() == item) {
                String id = net.minecraft.core.registries.BuiltInRegistries.ITEM.getKey(item).getPath();
                lineas.add(Component.translatable("item.atalaya." + id + ".efecto").withStyle(COLOR.get(arma.getKey())));
                lineas.add(Component.translatable("habilidad.atalaya.rol." + arma.getKey().id).withStyle(ChatFormatting.DARK_GRAY));
            }
        }
    }
}
