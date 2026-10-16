package com.atalaya.client;

import com.atalaya.Atalaya;
import com.atalaya.entity.CocoEntity;
import com.atalaya.sonido.AtalayaSonidos;
import net.fabricmc.fabric.api.client.rendering.v1.hud.HudElement;
import net.minecraft.client.DeltaTracker;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphicsExtractor;
import net.minecraft.client.renderer.RenderPipelines;
import net.minecraft.client.resources.sounds.SimpleSoundInstance;
import net.minecraft.client.resources.sounds.SoundInstance;
import net.minecraft.resources.Identifier;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.Mth;

/**
 * Lo que ve el que esta dentro del Coco: la pantalla oscura y roja, como la luz a traves de la carne, que late con un
 * corazon grande y sordo (el latido suena solo para el). Va por debajo de la barra y los corazones, para que veas como
 * se te va la vida. Entra en un momento y, al salir (cuando lo matan), se va.
 */
public class CocoDentroHud implements HudElement {

    /** La de la vineta: blanca, transparente en el centro y opaca en las esquinas. */
    private static final Identifier VINETA = Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "textures/gui/vineta.png");
    private static final int TAM = 256;
    private static final int ENTRA = 8;
    private static final int SALE = 14;
    /** Un latido cada 22 ticks (unos 55 por minuto: un corazon grande). */
    private static final int LATIDO = 22;

    /** Solo para las fotos de prueba (FotosPrueba, "COCO_HUD 0"): sin la pantalla roja, para ver el aviso de encima. */
    static boolean pruebaSinPantalla;

    private static int dentro;
    private static int fuera = SALE;
    private static int latido;

    public static void tick(Minecraft mc) {
        if (mc.level == null || mc.player == null) {
            dentro = 0;
            fuera = SALE;
            return;
        }
        if (mc.isPaused()) {
            return;
        }
        if (CocoEntity.atrapado(mc.player)) {
            if (dentro == 0) {
                latido = 4;
            }
            dentro++;
            fuera = 0;
            if (--latido <= 0) {
                latido = LATIDO;
                mc.getSoundManager().play(new SimpleSoundInstance(AtalayaSonidos.COCO_LATIDO.location(),
                        SoundSource.MASTER, 0.9F, 1.0F, SoundInstance.createUnseededRandom(), false, 0,
                        SoundInstance.Attenuation.NONE, 0.0, 0.0, 0.0, true));
            }
        } else {
            dentro = 0;
            if (fuera < SALE) {
                fuera++;
            }
        }
    }

    @Override
    public void extractRenderState(GuiGraphicsExtractor g, DeltaTracker delta) {
        if (pruebaSinPantalla) {
            return;
        }
        float parcial = delta.getGameTimeDeltaPartialTick(false);
        float k;
        if (dentro > 0) {
            k = Mth.clamp((dentro + parcial) / ENTRA, 0.0F, 1.0F);
        } else if (fuera < SALE) {
            k = 1.0F - Mth.clamp((fuera + parcial) / SALE, 0.0F, 1.0F);
        } else {
            return;
        }
        // El latido: un golpe que aclara la carne y se va.
        float desde = LATIDO - latido + parcial;
        float golpe = dentro > 0 ? (float) Math.exp(-desde / 4.0) : 0.0F;
        int alfa = (int) (k * (205 + 30 * (1.0F - golpe)));
        int rojo = (int) (70 + 60 * golpe);
        g.fill(0, 0, g.guiWidth(), g.guiHeight(), (alfa << 24) | (rojo << 16) | (8 << 8) | 6);
        // Los bordes, casi negros.
        int borde = (int) (k * 255);
        g.blit(RenderPipelines.GUI_TEXTURED, VINETA, 0, 0, 0.0F, 0.0F, g.guiWidth(), g.guiHeight(), TAM, TAM, TAM, TAM,
                (borde << 24) | 0x140202);
    }
}
