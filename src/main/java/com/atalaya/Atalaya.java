package com.atalaya;

import com.atalaya.commands.AtalayaCommand;
import com.atalaya.items.CustomItems;
import com.atalaya.items.HazmatArmor;
import com.atalaya.listeners.ItemListener;
import com.atalaya.listeners.PlayerJoinListener;
import com.atalaya.radiation.GeodeIndex;
import com.atalaya.radiation.GeodeListener;
import com.atalaya.radiation.RadiationManager;
import org.bukkit.plugin.java.JavaPlugin;

/**
 * Clase principal del plugin Atalaya.
 *
 * onEnable() se ejecuta cuando el servidor carga el plugin,
 * onDisable() cuando lo apaga. Aqui se registran comandos y eventos.
 */
public final class Atalaya extends JavaPlugin {

    // Acceso global a la instancia del plugin (util para NamespacedKey, tareas, etc.)
    private static Atalaya instance;
    private GeodeIndex geodeIndex;
    private RadiationManager radiationManager;

    @Override
    public void onEnable() {
        instance = this;

        // Carga config.yml (crea el archivo por defecto la primera vez).
        saveDefaultConfig();

        // Prepara los items custom (crea sus llaves a partir de este plugin).
        CustomItems.init(this);
        HazmatArmor.init(this);

        // Registra los listeners de eventos.
        getServer().getPluginManager().registerEvents(new PlayerJoinListener(), this);
        getServer().getPluginManager().registerEvents(new ItemListener(), this);

        // Sistema de radiacion de las geodas.
        // 1) Indice de amatistas (cache) + listener que lo mantiene al dia.
        geodeIndex = new GeodeIndex(this);
        getServer().getPluginManager().registerEvents(new GeodeListener(geodeIndex), this);
        // 2) Escanea lo ya cargado al arrancar (los ChunkLoadEvent no disparan para eso).
        geodeIndex.escanearMundosCargados();
        // 3) Tarea que aplica la radiacion consultando el indice.
        radiationManager = new RadiationManager(this, geodeIndex);
        radiationManager.start();

        // Enlaza el comando /atalaya (declarado en plugin.yml) con su ejecutor.
        var atalayaCommand = getCommand("atalaya");
        if (atalayaCommand != null) {
            atalayaCommand.setExecutor(new AtalayaCommand());
        }

        getLogger().info("Atalaya activado correctamente (Minecraft 26.2 / Paper).");
    }

    @Override
    public void onDisable() {
        if (radiationManager != null) {
            radiationManager.stop();
        }
        getLogger().info("Atalaya desactivado.");
    }

    public static Atalaya getInstance() {
        return instance;
    }

    public RadiationManager getRadiationManager() {
        return radiationManager;
    }

    public GeodeIndex getGeodeIndex() {
        return geodeIndex;
    }
}
