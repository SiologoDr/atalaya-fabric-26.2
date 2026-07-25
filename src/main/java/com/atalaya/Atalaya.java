package com.atalaya;

import com.atalaya.commands.AtalayaCommand;
import com.atalaya.items.HazmatArmor;
import com.atalaya.items.HazmatRecipes;
import com.atalaya.listeners.AnvilListener;
import com.atalaya.listeners.PlayerJoinListener;
import com.atalaya.menu.ConfigMenuListener;
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
    private Settings settings;
    private GeodeIndex geodeIndex;
    private RadiationManager radiationManager;

    @Override
    public void onEnable() {
        instance = this;

        // Carga config.yml (crea el archivo por defecto la primera vez).
        saveDefaultConfig();
        settings = new Settings(this);

        // Prepara los items custom (crea sus llaves a partir de este plugin).
        HazmatArmor.init(this);

        // Registra las recetas de crafteo del traje Hazmat (solo si el crafteo esta activo).
        if (settings.isCrafteoActivo()) {
            HazmatRecipes.registrar(this);
            getServer().getOnlinePlayers().forEach(HazmatRecipes::desbloquear);
        }

        // Registra los listeners de eventos.
        getServer().getPluginManager().registerEvents(new PlayerJoinListener(), this);
        getServer().getPluginManager().registerEvents(new AnvilListener(), this);
        getServer().getPluginManager().registerEvents(new ConfigMenuListener(this), this);

        // Sistema de radiacion de las geodas.
        // 1) Indice de amatistas (cache) + listener que lo mantiene al dia.
        geodeIndex = new GeodeIndex(this);
        getServer().getPluginManager().registerEvents(new GeodeListener(geodeIndex), this);
        // 2) Escanea lo ya cargado al arrancar (los ChunkLoadEvent no disparan para eso).
        geodeIndex.escanearMundosCargados();
        // 3) Tarea que aplica la radiacion consultando el indice.
        radiationManager = new RadiationManager(this, geodeIndex);
        radiationManager.start();

        // Enlaza el comando /atalaya (ejecutor + autocompletado).
        var atalayaCommand = getCommand("atalaya");
        if (atalayaCommand != null) {
            AtalayaCommand ejecutor = new AtalayaCommand();
            atalayaCommand.setExecutor(ejecutor);
            atalayaCommand.setTabCompleter(ejecutor);
        }

        getLogger().info("Atalaya activado correctamente (Minecraft 26.2 / Paper).");
    }

    @Override
    public void onDisable() {
        if (radiationManager != null) {
            radiationManager.stop();
            radiationManager.limpiarLentitudTodos(); // no dejar lentitud pegada tras un reload
        }
        getLogger().info("Atalaya desactivado.");
    }

    public static Atalaya getInstance() {
        return instance;
    }

    public Settings getSettings() {
        return settings;
    }

    public RadiationManager getRadiationManager() {
        return radiationManager;
    }

    public GeodeIndex getGeodeIndex() {
        return geodeIndex;
    }
}
