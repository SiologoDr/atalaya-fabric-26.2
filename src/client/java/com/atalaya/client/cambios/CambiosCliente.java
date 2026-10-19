package com.atalaya.client.cambios;

import com.atalaya.Atalaya;
import com.atalaya.cambios.Insomnio;
import com.atalaya.cambios.Plaga;
import com.atalaya.effect.DeslumbradoEffect;
import com.atalaya.mixin.client.GameRendererAccesor;
import net.fabricmc.fabric.api.client.event.lifecycle.v1.ClientTickEvents;
import net.fabricmc.fabric.api.client.rendering.v1.hud.HudElementRegistry;
import net.fabricmc.fabric.api.client.rendering.v1.hud.VanillaHudElements;
import net.minecraft.client.DeltaTracker;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphicsExtractor;
import net.minecraft.client.player.LocalPlayer;
import net.minecraft.client.renderer.RenderPipelines;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.Identifier;
import net.minecraft.util.Mth;

/**
 * Lo que los cambios de dificultad ponen en la pantalla de cada uno:
 *
 * <pre>
 *   la plaga      su calavera verde y lo que le queda (M:SS), a la izquierda de la barra de objetos; parpadea en rojo el
 *                 ultimo minuto
 *   el insomnio   el ojo abierto y sus cinco rayas, encima de la plaga (solo si pasa de una cuarta parte)
 *   deslumbrado   la vista nublada y sin colores (el efecto de pantalla deslumbrado.json) y sin los corazones
 * </pre>
 */
public final class CambiosCliente {

    private static final Identifier PLAGA = Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "hud/plaga");
    private static final Identifier OJO = Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "hud/insomnio");
    private static final Identifier EFECTO = Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "deslumbrado");

    private CambiosCliente() {
    }

    public static void registrar() {
        HudElementRegistry.attachElementAfter(VanillaHudElements.HOTBAR,
                Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "cambios_jugador"), CambiosCliente::hud);
        HudElementRegistry.replaceElement(VanillaHudElements.HEALTH_BAR, vanilla -> (g, tiempo) -> {
            LocalPlayer p = Minecraft.getInstance().player;
            if (p == null || (!p.hasEffect(DeslumbradoEffect.DESLUMBRADO)
                    && !p.hasEffect(com.atalaya.effect.VidaOcultaEffect.VIDA_OCULTA))) {
                vanilla.extractRenderState(g, tiempo);
            }
        });
        ClientTickEvents.END_CLIENT_TICK.register(CambiosCliente::tick);
    }

    /** El efecto de pantalla del deslumbrado: puesto mientras lo lleva, quitado al acabar (si es el nuestro). */
    private static void tick(Minecraft mc) {
        if (mc.player == null) {
            return;
        }
        boolean deslumbrado = mc.player.hasEffect(DeslumbradoEffect.DESLUMBRADO);
        Identifier actual = mc.gameRenderer.currentPostEffect();
        if (deslumbrado && !EFECTO.equals(actual)) {
            ((GameRendererAccesor) mc.gameRenderer).atalaya$ponerEfecto(EFECTO);
        } else if (!deslumbrado && EFECTO.equals(actual)) {
            mc.gameRenderer.clearPostEffect();
        }
    }

    private static void hud(GuiGraphicsExtractor g, DeltaTracker tiempo) {
        Minecraft mc = Minecraft.getInstance();
        LocalPlayer p = mc.player;
        if (p == null) {
            return;
        }
        int x = g.guiWidth() / 2 - 91 - 52;
        int y = g.guiHeight() - 20;
        int plaga = p.getAttachedOrElse(Plaga.CUENTA, -1);
        if (plaga >= 0) {
            int s = plaga / 20;
            boolean final_ = s < 60;
            boolean luce = !final_ || (p.tickCount / 5) % 2 == 0;
            g.blitSprite(RenderPipelines.GUI_TEXTURED, PLAGA, x, y, 16, 16);
            String texto = s >= 3600 ? String.format("%d:%02d:%02d", s / 3600, (s / 60) % 60, s % 60)
                    : String.format("%d:%02d", s / 60, s % 60);
            g.text(mc.font, Component.literal(texto), x + 18, y + 4, luce && final_ ? 0xFFFF5A4A : 0xFFB8F08A, true);
            y -= 18;
        }
        int insomnio = p.getAttachedOrElse(Insomnio.NIVEL, 0);
        if (insomnio >= 25) {
            g.blitSprite(RenderPipelines.GUI_TEXTURED, OJO, x, y, 16, 16);
            int rayas = Mth.clamp((insomnio + 19) / 20, 1, 5);
            for (int i = 0; i < 5; i++) {
                int color = i < rayas ? (insomnio >= 50 ? 0xFFB070FF : 0xFFD8CCE4) : 0x60000000;
                g.fill(x + 19 + i * 5, y + 5, x + 23 + i * 5, y + 11, color);
            }
        }
    }
}
