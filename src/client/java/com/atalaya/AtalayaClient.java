package com.atalaya;

import com.atalaya.client.AvisoTrajeHud;
import com.atalaya.client.HidratacionHud;
import com.atalaya.client.InsolacionHud;
import net.fabricmc.api.ClientModInitializer;
import net.fabricmc.fabric.api.client.rendering.v1.hud.HudElementRegistry;
import net.fabricmc.fabric.api.client.rendering.v1.hud.VanillaHudElements;
import net.minecraft.resources.Identifier;

/**
 * Punto de entrada del CLIENTE.
 *
 * Aqui va todo lo que solo existe en el cliente: renderizado, HUD, modelos.
 * Es justo lo que un plugin no podia tocar.
 */
public class AtalayaClient implements ClientModInitializer {

    @Override
    public void onInitializeClient() {
        // Aviso de traje sin filtro. Se dibuja despues de la hotbar para que
        // quede por encima y no lo tape.
        HudElementRegistry.attachElementAfter(
                VanillaHudElements.HOTBAR,
                Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "aviso_traje"),
                new AvisoTrajeHud());

        // El medidor de hidratacion se engancha al numero de experiencia, que es
        // justo debajo de donde se dibuja. Va DESPUES para quedar por encima si
        // algun dia se solaparan.
        //
        // Es un elemento aparte del aviso del traje a proposito: cada uno se
        // registra por su cuenta, asi que no compiten por el mismo sitio ni se
        // tapan. Y ademas viven en esquinas distintas de la pantalla.
        HudElementRegistry.attachElementAfter(
                VanillaHudElements.EXPERIENCE_LEVEL,
                Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "hidratacion"),
                new HidratacionHud());

        // El halo de calor va ANTES de la hotbar, al contrario que los otros
        // dos: es un velo a pantalla completa, asi que tiene que quedar por
        // DEBAJO de todo lo demas del HUD. Si no, teniria los corazones y la
        // barra de experiencia de naranja.
        HudElementRegistry.attachElementBefore(
                VanillaHudElements.HOTBAR,
                Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "insolacion"),
                new InsolacionHud());

        Atalaya.LOGGER.info("Atalaya (cliente) iniciado.");
    }
}
