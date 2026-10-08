package com.atalaya.client;

import com.atalaya.Atalaya;
import net.fabricmc.loader.api.FabricLoader;
import net.fabricmc.fabric.api.client.message.v1.ClientReceiveMessageEvents;
import net.minecraft.client.Minecraft;
import net.minecraft.client.Screenshot;

import java.io.File;

/**
 * Herramienta de desarrollo: capturas de pantalla a la orden de un datapack.
 *
 * Solo se activa si en la carpeta del juego existe "atalaya_fotos.flag" (en el
 * entorno de pruebas, run/). Entonces un mensaje de sistema "FOTO nombre" (un
 * tellraw desde una funcion) guarda el fotograma como screenshots/nombre.png y
 * no se muestra en el chat. Asi las escenas de prueba se fotografian en el
 * tick exacto, aunque la ventana este tapada o sin foco.
 */
public final class FotosPrueba {

    private static final String PREFIJO = "FOTO ";
    /** "VISTA 0|1|2": primera persona, tercera por detras o por delante (para ver lo que lleva uno encima). */
    private static final String VISTA = "VISTA ";

    private FotosPrueba() {
    }

    public static void registrar() {
        if (!new File(FabricLoader.getInstance().getGameDir().toFile(), "atalaya_fotos.flag").exists()) {
            return;
        }
        Atalaya.LOGGER.info("Fotos de prueba activadas (atalaya_fotos.flag).");
        ClientReceiveMessageEvents.ALLOW_GAME.register((mensaje, encima) -> {
            String texto = mensaje.getString();
            if (texto.startsWith(VISTA)) {
                int v = Math.clamp(Integer.parseInt(texto.substring(VISTA.length()).trim()), 0, 2);
                Minecraft.getInstance().options.setCameraType(net.minecraft.client.CameraType.values()[v]);
                return false;
            }
            if (!texto.startsWith(PREFIJO)) {
                return true;
            }
            Minecraft mc = Minecraft.getInstance();
            String nombre = texto.substring(PREFIJO.length()).trim().replaceAll("[^A-Za-z0-9_\\-]", "_");
            Screenshot.grab(mc.gameDirectory, nombre + ".png", mc.gameRenderer.mainRenderTarget(), 1, c -> {
            });
            return false;
        });
    }
}
