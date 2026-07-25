package com.atalaya;

/**
 * Estado de las mecanicas del plugin, persistido en config.yml.
 * Se puede cambiar en caliente desde el menu (/atalaya menu).
 */
public class Settings {

    private final Atalaya plugin;
    private boolean radiacionActiva;
    private boolean crafteoActivo;

    public Settings(Atalaya plugin) {
        this.plugin = plugin;
        load();
    }

    public void load() {
        var c = plugin.getConfig();
        radiacionActiva = c.getBoolean("radiacion.activa", true);
        crafteoActivo = c.getBoolean("hazmat.crafteo-activo", true);
    }

    public boolean isRadiacionActiva() {
        return radiacionActiva;
    }

    public boolean isCrafteoActivo() {
        return crafteoActivo;
    }

    public void setRadiacionActiva(boolean valor) {
        radiacionActiva = valor;
        plugin.getConfig().set("radiacion.activa", valor);
        plugin.saveConfig();
    }

    public void setCrafteoActivo(boolean valor) {
        crafteoActivo = valor;
        plugin.getConfig().set("hazmat.crafteo-activo", valor);
        plugin.saveConfig();
    }
}
