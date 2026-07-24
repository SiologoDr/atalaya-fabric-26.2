package com.atalaya;

import com.atalaya.commands.AtalayaCommand;
import com.atalaya.items.CustomItems;
import com.atalaya.listeners.ItemListener;
import com.atalaya.listeners.PlayerJoinListener;
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

    @Override
    public void onEnable() {
        instance = this;

        // Prepara los items custom (crea sus llaves a partir de este plugin).
        CustomItems.init(this);

        // Registra los listeners de eventos.
        getServer().getPluginManager().registerEvents(new PlayerJoinListener(), this);
        getServer().getPluginManager().registerEvents(new ItemListener(), this);

        // Enlaza el comando /atalaya (declarado en plugin.yml) con su ejecutor.
        var atalayaCommand = getCommand("atalaya");
        if (atalayaCommand != null) {
            atalayaCommand.setExecutor(new AtalayaCommand());
        }

        getLogger().info("Atalaya activado correctamente (Minecraft 26.2 / Paper).");
    }

    @Override
    public void onDisable() {
        getLogger().info("Atalaya desactivado.");
    }

    public static Atalaya getInstance() {
        return instance;
    }
}
