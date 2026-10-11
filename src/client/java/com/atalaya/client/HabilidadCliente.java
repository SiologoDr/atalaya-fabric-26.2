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
            alrededor(mc);
        });
        ItemTooltipCallback.EVENT.register((stack, contexto, flag, lineas) -> describir(stack.getItem(), lineas));
    }

    /**
     * Con la activa en marcha y en primera persona, a sus pies y alrededor sale lo
     * de su elemento (el aura entera solo se ve desde fuera: HabilidadAuraLayer).
     */
    private static void alrededor(net.minecraft.client.Minecraft mc) {
        net.minecraft.client.player.LocalPlayer p = mc.player;
        if (p == null || mc.level == null || mc.isPaused() || !mc.options.getCameraType().isFirstPerson() || p.tickCount % 3 != 0) {
            return;
        }
        ArmadurasJefes.Tema tema = Habilidades.conjunto(p);
        com.atalaya.habilidad.HabilidadEstado e = p.getAttachedOrElse(Habilidades.ESTADO, com.atalaya.habilidad.HabilidadEstado.NADA);
        if (tema == null || !e.activa(mc.level.getGameTime(), tema.ordinal())) {
            return;
        }
        net.minecraft.core.particles.SimpleParticleType tipo = switch (tema) {
            case JADE -> com.atalaya.particula.AtalayaParticulas.RAJANG_JADE;
            case MAREAS -> com.atalaya.particula.AtalayaParticulas.NEREA_BURBUJA;
            case VENDAVAL -> com.atalaya.particula.AtalayaParticulas.AERALIS_LUZ;
            case SOLAR -> com.atalaya.particula.AtalayaParticulas.NOVILIS_BRASA;
        };
        for (int i = 0; i < 2; i++) {
            double a = p.getRandom().nextDouble() * Math.PI * 2;
            double r = 0.8 + p.getRandom().nextDouble() * 0.5;
            mc.level.addParticle(tipo, p.getX() + Math.cos(a) * r, p.getY() + 0.1 + p.getRandom().nextDouble() * 0.6,
                    p.getZ() + Math.sin(a) * r, 0.0, 0.04, 0.0);
        }
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
