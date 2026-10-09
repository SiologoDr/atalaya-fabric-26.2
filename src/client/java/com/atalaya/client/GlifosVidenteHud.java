package com.atalaya.client;

import com.atalaya.Atalaya;
import com.atalaya.entity.MinijuegosRajang;
import com.atalaya.entity.RajangEntity;
import net.fabricmc.fabric.api.client.rendering.v1.hud.HudElement;
import net.minecraft.client.DeltaTracker;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphicsExtractor;
import net.minecraft.client.renderer.RenderPipelines;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.Identifier;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.Entity;
import org.jspecify.annotations.Nullable;

/**
 * Glifos del Templo: lo que solo ve el Vidente. A la derecha, en un panel de
 * jade con el filo de oro, los tres glifos verdaderos (rajang_glifos.png, en
 * oro y al doble) con su nombre debajo, para que pueda decirselos a los demas.
 * Los demas no ven nada (en la barra del jefe pone quien es el Vidente).
 */
public class GlifosVidenteHud implements HudElement {

    private static final Identifier GLIFOS = Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "textures/gui/rajang_glifos.png");
    private static final int LADO = 24;
    private static final int GRANDE = 40;
    private static final int ORO = 0xFFF8D97C;
    private static final int ORO_OSCURO = 0xFF6E4610;
    private static final int FONDO = 0xE0081A10;

    /** Desde cuando se ve (para que entre deslizando). */
    private int visto = -1;

    @Override
    public void extractRenderState(GuiGraphicsExtractor g, DeltaTracker delta) {
        Minecraft mc = Minecraft.getInstance();
        RajangEntity r = rajangVidente(mc);
        if (r == null || mc.player == null) {
            visto = -1;
            return;
        }
        if (visto < 0) {
            visto = mc.player.tickCount;
        }
        float parcial = delta.getGameTimeDeltaPartialTick(false);
        float entra = Mth.clamp((mc.player.tickCount - visto + parcial) / 8.0F, 0.0F, 1.0F);
        int buenos = r.getGlifosBuenos();
        int ancho = GRANDE * 3 + 4 * 8;
        int alto = GRANDE + 44;
        int x0 = g.guiWidth() - (int) ((ancho + 8) * (1.0F - (1.0F - entra) * (1.0F - entra)));
        int y0 = g.guiHeight() / 2 - alto / 2 - 10;
        g.fill(x0 - 2, y0 - 2, x0 + ancho + 2, y0 + alto + 2, ORO_OSCURO);
        g.fill(x0 - 1, y0 - 1, x0 + ancho + 1, y0 + alto + 1, ORO);
        g.fill(x0, y0, x0 + ancho, y0 + alto, FONDO);
        Component titulo = Component.translatable("hud.atalaya.rajang.vidente_titulo");
        g.text(mc.font, titulo, x0 + ancho / 2 - mc.font.width(titulo) / 2, y0 + 4, ORO, true);
        int i = 0;
        for (int glifo = 0; glifo < MinijuegosRajang.NOMBRES_GLIFOS.length && i < 3; glifo++) {
            if ((buenos & (1 << glifo)) == 0) {
                continue;
            }
            int gx = x0 + 8 + i * (GRANDE + 8);
            int gy = y0 + 16;
            g.blit(RenderPipelines.GUI_TEXTURED, GLIFOS, gx, gy, glifo * LADO, 0.0F, GRANDE, GRANDE, LADO, LADO,
                    LADO * MinijuegosRajang.NOMBRES_GLIFOS.length, LADO, 0xFFFFFFFF);
            Component nombre = Component.translatable("hud.atalaya.rajang.glifo." + MinijuegosRajang.NOMBRES_GLIFOS[glifo]);
            g.text(mc.font, nombre, gx + GRANDE / 2 - mc.font.width(nombre) / 2, gy + GRANDE + 3, 0xFFE8FFE8, true);
            i++;
        }
        Component dile = Component.translatable("hud.atalaya.rajang.vidente_dile");
        g.text(mc.font, dile, x0 + ancho / 2 - mc.font.width(dile) / 2, y0 + alto - 11, 0xFFB8D8C0, true);
    }

    /** El Rajang con Glifos del Templo en marcha del que este jugador es el Vidente. */
    private static @Nullable RajangEntity rajangVidente(Minecraft mc) {
        if (mc.level == null || mc.player == null) {
            return null;
        }
        for (Entity e : mc.level.entitiesForRendering()) {
            if (e instanceof RajangEntity r && r.minijuego() == MinijuegosRajang.GLIFOS && r.getVidente() == mc.player.getId()) {
                return r;
            }
        }
        return null;
    }
}
