package com.atalaya.listeners;

import com.atalaya.items.CustomItems;
import org.bukkit.block.Block;
import org.bukkit.entity.Player;
import org.bukkit.event.EventHandler;
import org.bukkit.event.Listener;
import org.bukkit.event.block.Action;
import org.bukkit.event.player.PlayerInteractEvent;

/**
 * Ejemplo de COMPORTAMIENTO custom de un item.
 * Al hacer click derecho con el Baston de la Atalaya, cae un rayo
 * donde el jugador esta mirando.
 */
public class ItemListener implements Listener {

    @EventHandler
    public void onInteract(PlayerInteractEvent event) {
        Action action = event.getAction();
        if (action != Action.RIGHT_CLICK_AIR && action != Action.RIGHT_CLICK_BLOCK) {
            return;
        }

        // Solo reacciona si el item en la mano es nuestro baston.
        if (!CustomItems.esBaston(event.getItem())) {
            return;
        }

        Player player = event.getPlayer();

        // Punto al que mira el jugador (hasta 50 bloques); si no hay bloque, su posicion.
        Block target = player.getTargetBlockExact(50);
        var location = (target != null) ? target.getLocation() : player.getLocation();

        player.getWorld().strikeLightning(location);
        event.setCancelled(true);
    }
}
