package com.atalaya.client;

import com.atalaya.net.AtalayaRed;
import com.atalaya.sonido.AtalayaSonidos;
import net.minecraft.client.Minecraft;
import net.minecraft.client.resources.sounds.SimpleSoundInstance;
import net.minecraft.client.resources.sounds.SoundInstance;
import net.minecraft.sounds.SoundSource;

/**
 * Los menus de los cambios y de las dimensiones en el cliente: los abre o los pone al dia lo que manda el servidor
 * (CambiosDificultad), y suena el interruptor al pulsar.
 */
public final class MenusCliente {

    private MenusCliente() {
    }

    public static void recibirCambios(AtalayaRed.MenuCambios m) {
        Minecraft mc = Minecraft.getInstance();
        if (m.abrir()) {
            mc.gui.setScreen(new MenuCambiosScreen(m.estados()));
        } else if (mc.gui.screen() instanceof MenuCambiosScreen pantalla) {
            pantalla.actualizar(m.estados());
        }
    }

    public static void recibirDimensiones(AtalayaRed.MenuDimensiones m) {
        Minecraft mc = Minecraft.getInstance();
        if (m.abrir()) {
            mc.gui.setScreen(new MenuDimensionesScreen(m.nether(), m.end()));
        } else if (mc.gui.screen() instanceof MenuDimensionesScreen pantalla) {
            pantalla.actualizar(m.nether(), m.end());
        }
    }

    /** El interruptor: al encender, un clic que sube; al apagar, uno que baja (ruleta_sonidos.py). */
    public static void sonar(boolean enciende) {
        Minecraft mc = Minecraft.getInstance();
        mc.getSoundManager().play(new SimpleSoundInstance(
                (enciende ? AtalayaSonidos.RULETA_ENCIENDE : AtalayaSonidos.RULETA_APAGA).location(), SoundSource.MASTER,
                0.8F, 1.0F, SoundInstance.createUnseededRandom(), false, 0, SoundInstance.Attenuation.NONE, 0.0, 0.0, 0.0, true));
    }
}
