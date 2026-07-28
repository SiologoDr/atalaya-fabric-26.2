package com.atalaya;

import net.fabricmc.api.ModInitializer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Punto de entrada comun del mod (servidor y cliente).
 *
 * Equivale al onEnable() del antiguo plugin, pero aqui corre tanto en el
 * servidor dedicado como dentro del cliente.
 */
public class Atalaya implements ModInitializer {

    public static final String MOD_ID = "atalaya";
    public static final Logger LOGGER = LoggerFactory.getLogger(MOD_ID);

    @Override
    public void onInitialize() {
        LOGGER.info("Atalaya iniciado (Minecraft 26.2 / Fabric).");
    }
}
