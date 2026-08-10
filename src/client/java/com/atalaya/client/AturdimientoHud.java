package com.atalaya.client;

import com.atalaya.Atalaya;
import com.atalaya.aturdimiento.Aturdimiento;
import net.fabricmc.fabric.api.client.rendering.v1.hud.HudElement;
import net.minecraft.client.DeltaTracker;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphicsExtractor;
import net.minecraft.client.player.LocalPlayer;
import net.minecraft.client.renderer.RenderPipelines;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.Identifier;

/**
 * La tecla que hay que aporrear para soltarse del aturdimiento.
 *
 * Un aviso que no dice QUE hacer no sirve de nada: quien se queda clavado sin
 * explicacion cree que el juego se ha colgado. Por eso el dibujo de la tecla va
 * con su frase debajo.
 *
 * La animacion es una sola imagen con dos fotogramas, uno encima del otro:
 * arriba la tecla suelta y abajo la pulsada. Cambiar de uno a otro es mover la
 * V del blit dieciseis pixeles, sin tocar de textura. Sale gratis y ademas
 * responde en el mismo fotograma en que se aprieta.
 */
public class AturdimientoHud implements HudElement {

    private static final Identifier TECLA =
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "textures/gui/tecla_espacio.png");

    private static final int ANCHO = 48;
    private static final int ALTO = 16;
    /** La imagen lleva los dos fotogramas apilados, asi que mide el doble. */
    private static final int ALTO_TEXTURA = 32;

    /** Cuanto sube el conjunto respecto al borde de abajo. */
    private static final int ALTURA = 96;

    /** Blanco lleno para la tecla: el color va en la propia imagen. */
    private static final int SIN_TENIR = 0xFFFFFFFF;

    @Override
    public void extractRenderState(GuiGraphicsExtractor grafico, DeltaTracker delta) {
        Minecraft mc = Minecraft.getInstance();
        LocalPlayer jugador = mc.player;
        if (jugador == null || !Aturdimiento.aturdido(jugador)) {
            return;
        }

        // Se mira si la tecla esta ABAJO, no si se ha pulsado: lo que se dibuja
        // es el estado actual del dedo, no un suceso. Quien la deja apretada ve
        // la tecla hundida, que es lo que espera.
        boolean pulsada = mc.options.keyJump.isDown();

        int x = grafico.guiWidth() / 2 - ANCHO / 2;
        int y = grafico.guiHeight() - ALTURA;

        // El fotograma se elige moviendo la V: 0 la suelta, 16 la pulsada.
        grafico.blit(RenderPipelines.GUI_TEXTURED, TECLA,
                x, y, 0f, (pulsada ? ALTO : 0),
                ANCHO, ALTO, ANCHO, ALTO_TEXTURA, SIN_TENIR);

        grafico.centeredText(mc.font,
                Component.translatable("hud.atalaya.aturdimiento"),
                grafico.guiWidth() / 2, y + ALTO + 4, 0xFFFFFFFF);
    }
}
