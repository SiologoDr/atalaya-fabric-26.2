package com.atalaya.client;

import com.atalaya.net.AtalayaRed;
import com.atalaya.sonido.AtalayaSonidos;
import net.fabricmc.fabric.api.client.rendering.v1.hud.HudElement;
import net.minecraft.client.DeltaTracker;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphicsExtractor;
import net.minecraft.client.resources.sounds.SimpleSoundInstance;
import net.minecraft.client.resources.sounds.SoundInstance;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.Mth;

/**
 * La pantalla en blanco del Fogonazo: cuando te estalla cerca y lo ves, la pantalla se queda blanca del todo (4 s) y luego
 * el blanco se va (2 s). Va por encima de todo el HUD: ciega de verdad. Mientras, el pitido en el oido.
 */
public class DeslumbreHud implements HudElement {

    private static int blanco;
    private static int funde;
    private static int t = -1;

    /** Llega del servidor. Si ya estaba ciego, se queda con lo que dure mas. */
    public static void recibir(AtalayaRed.Deslumbre d) {
        int queda = t < 0 ? 0 : blanco + funde - t;
        if (d.blanco() + d.funde() < queda) {
            return;
        }
        blanco = d.blanco();
        funde = Math.max(1, d.funde());
        t = 0;
        Minecraft mc = Minecraft.getInstance();
        mc.getSoundManager().play(new SimpleSoundInstance(AtalayaSonidos.FOGONAZO_PITIDO.location(), SoundSource.MASTER,
                0.8F, 1.0F, SoundInstance.createUnseededRandom(), false, 0, SoundInstance.Attenuation.NONE, 0.0, 0.0,
                0.0, true));
    }

    public static void tick(Minecraft mc) {
        if (t < 0) {
            return;
        }
        if (mc.level == null || mc.player == null) {
            olvidar();
            return;
        }
        if (mc.isPaused()) {
            return;
        }
        t++;
        if (t > blanco + funde) {
            t = -1;
        }
    }

    public static void olvidar() {
        t = -1;
    }

    @Override
    public void extractRenderState(GuiGraphicsExtractor g, DeltaTracker delta) {
        if (t < 0) {
            return;
        }
        float ahora = t + delta.getGameTimeDeltaPartialTick(false);
        float alfa;
        if (ahora < blanco) {
            alfa = 1.0F;
        } else {
            float k = Mth.clamp((ahora - blanco) / funde, 0.0F, 1.0F);
            alfa = (float) Math.pow(1.0F - k, 1.6F);
        }
        if (alfa <= 0.0F) {
            return;
        }
        // Blanco calido, como la luz del farol.
        int a = (int) (alfa * 255.0F);
        g.fill(0, 0, g.guiWidth(), g.guiHeight(), (a << 24) | 0xFFFCF4);
    }
}
