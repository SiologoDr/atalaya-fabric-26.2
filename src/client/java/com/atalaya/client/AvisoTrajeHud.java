package com.atalaya.client;

import com.atalaya.Atalaya;
import com.atalaya.item.HazmatArmor;
import net.fabricmc.fabric.api.client.rendering.v1.hud.HudElement;
import net.minecraft.client.DeltaTracker;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphicsExtractor;
import net.minecraft.client.player.LocalPlayer;
import net.minecraft.client.renderer.RenderPipelines;
import net.minecraft.resources.Identifier;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.item.ItemStack;

/**
 * Aviso en pantalla de que el traje se esta quedando sin filtro.
 *
 * Aparece por debajo del 30% de durabilidad de la pieza mas gastada y
 * desaparece cuando ya no queda ninguna pieza puesta.
 *
 * Se dibuja entero en el CLIENTE y no viaja ni un byte por la red: el cliente
 * ya conoce su propia armadura y su durabilidad, asi que puede decidir solo si
 * mostrar el simbolo. Es de las pocas cosas que salen gratis en un mod y que un
 * plugin no podria hacer de ninguna manera.
 */
public class AvisoTrajeHud implements HudElement {

    private static final Identifier TEXTURA =
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "textures/gui/aviso_traje.png");

    private static final int TAM = 16;

    /** Tinte en formato ARGB. La textura es blanca, asi que el tinte manda. */
    private static final int AMARILLO = 0xFFFFD24A;
    private static final int AMARILLO_APAGADO = 0xFF6B551C;
    private static final int ROJO = 0xFFFF4444;
    private static final int ROJO_APAGADO = 0xFF6A1010;

    /**
     * Ticks que dura cada mitad del parpadeo. El rojo late mas rapido que el
     * amarillo: asi los dos estados se distinguen aunque no mires el color.
     */
    private static final int PARPADEO_AVISO = 12;
    private static final int PARPADEO_FALLO = 6;

    /** Margen respecto a la esquina inferior derecha. */
    private static final int MARGEN = 10;

    private static final EquipmentSlot[] RANURAS = {
            EquipmentSlot.HEAD, EquipmentSlot.CHEST, EquipmentSlot.LEGS, EquipmentSlot.FEET
    };

    @Override
    public void extractRenderState(GuiGraphicsExtractor grafico, DeltaTracker delta) {
        Minecraft mc = Minecraft.getInstance();
        LocalPlayer jugador = mc.player;
        if (jugador == null) {
            return;
        }

        float peor = peorPieza(jugador);
        if (peor > HazmatArmor.UMBRAL_AVISO) {
            return; // todo en orden, no molestamos
        }

        // Los dos estados parpadean; el rojo late al doble de rapido.
        // El rojo entra ANTES de que la pieza deje de filtrar (21.5% frente a
        // 20%): son unos segundos de margen para cambiar el filtro a tiempo.
        boolean fallando = peor < HazmatArmor.UMBRAL_CRITICO;
        int ritmo = fallando ? PARPADEO_FALLO : PARPADEO_AVISO;
        boolean encendido = (jugador.tickCount / ritmo) % 2 == 0;

        int color;
        if (fallando) {
            color = encendido ? ROJO : ROJO_APAGADO;
        } else {
            color = encendido ? AMARILLO : AMARILLO_APAGADO;
        }

        // Esquina inferior derecha.
        int x = grafico.guiWidth() - TAM - MARGEN;
        int y = grafico.guiHeight() - TAM - MARGEN;

        grafico.blit(RenderPipelines.GUI_TEXTURED, TEXTURA,
                x, y, 0f, 0f, TAM, TAM, TAM, TAM, color);
    }

    /**
     * Fraccion de durabilidad de la pieza del traje mas gastada que lleve
     * puesta, o 1.0 si no lleva ninguna (y entonces no hay nada que avisar).
     */
    private static float peorPieza(LocalPlayer jugador) {
        float peor = 1f;
        boolean alguna = false;
        for (EquipmentSlot slot : RANURAS) {
            ItemStack pieza = jugador.getItemBySlot(slot);
            if (!HazmatArmor.esPieza(pieza.getItem())) {
                continue;
            }
            alguna = true;
            peor = Math.min(peor, HazmatArmor.durabilidadRestante(pieza));
        }
        return alguna ? peor : 1f;
    }
}
