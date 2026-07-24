package com.atalaya.listeners;

import net.kyori.adventure.text.Component;
import net.kyori.adventure.text.format.NamedTextColor;
import org.bukkit.event.EventHandler;
import org.bukkit.event.Listener;
import org.bukkit.event.player.PlayerJoinEvent;

/**
 * Ejemplo de EVENTO: se dispara cuando un jugador entra al servidor.
 * Todo esto ocurre en el servidor; el cliente no necesita nada instalado.
 */
public class PlayerJoinListener implements Listener {

    @EventHandler
    public void onJoin(PlayerJoinEvent event) {
        event.getPlayer().sendMessage(
                Component.text("Bienvenido a la Atalaya, ", NamedTextColor.GOLD)
                        .append(Component.text(event.getPlayer().getName(), NamedTextColor.YELLOW))
        );
    }
}
