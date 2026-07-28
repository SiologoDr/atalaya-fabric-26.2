package com.atalaya;

import com.atalaya.command.AtalayaCommand;
import com.atalaya.effect.RadiacionEffect;
import com.atalaya.item.HazmatArmor;
import com.atalaya.radiation.GeodeIndex;
import com.atalaya.radiation.RadiationManager;
import net.fabricmc.api.ModInitializer;
import net.fabricmc.fabric.api.command.v2.CommandRegistrationCallback;
import net.fabricmc.fabric.api.creativetab.v1.CreativeModeTabEvents;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerChunkEvents;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerLifecycleEvents;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerTickEvents;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.item.CreativeModeTab;
import net.minecraft.world.item.Items;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Punto de entrada comun del mod (servidor y cliente).
 */
public class Atalaya implements ModInitializer {

    public static final String MOD_ID = "atalaya";
    public static final Logger LOGGER = LoggerFactory.getLogger(MOD_ID);

    /**
     * En 26.2 CreativeModeTabs ya no expone las pestanas como campos publicos,
     * asi que la clave se construye a mano.
     */
    private static final ResourceKey<CreativeModeTab> PESTANA_COMBATE =
            ResourceKey.create(Registries.CREATIVE_MODE_TAB, Identifier.withDefaultNamespace("combat"));

    @Override
    public void onInitialize() {
        HazmatArmor.registrar();
        RadiacionEffect.registrar();

        // Indice de geodas: se mantiene al dia con la carga y descarga de chunks.
        // El tercer parametro de CHUNK_LOAD (recien generado o no) no nos importa:
        // hay que escanearlo igual en ambos casos.
        ServerChunkEvents.CHUNK_LOAD.register((nivel, chunk, recienGenerado) ->
                GeodeIndex.alCargarChunk(nivel, chunk));
        ServerChunkEvents.CHUNK_UNLOAD.register(GeodeIndex::alDescargarChunk);
        ServerLifecycleEvents.SERVER_STOPPED.register(servidor -> GeodeIndex.limpiar());

        // La radiacion se aplica desde el tick del servidor.
        ServerTickEvents.END_SERVER_TICK.register(RadiationManager::tick);

        // El traje aparece en la pestana de combate, justo detras de las botas de hierro.
        CreativeModeTabEvents.modifyOutputEvent(PESTANA_COMBATE).register(salida ->
                salida.insertAfter(Items.IRON_BOOTS, HazmatArmor.todas()));

        CommandRegistrationCallback.EVENT.register(
                (dispatcher, registryAccess, entorno) -> AtalayaCommand.registrar(dispatcher));

        LOGGER.info("Atalaya iniciado (Minecraft 26.2 / Fabric).");
    }
}
