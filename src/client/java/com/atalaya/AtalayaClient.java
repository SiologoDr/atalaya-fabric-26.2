package com.atalaya;

import net.fabricmc.api.ClientModInitializer;

/**
 * Punto de entrada del CLIENTE.
 *
 * Aqui va todo lo que solo existe en el cliente: renderizado, HUD, modelos.
 * Es justo lo que un plugin no podia tocar.
 */
public class AtalayaClient implements ClientModInitializer {

    @Override
    public void onInitializeClient() {
        Atalaya.LOGGER.info("Atalaya (cliente) iniciado.");
    }
}
