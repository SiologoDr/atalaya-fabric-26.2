package com.atalaya.commands;

import com.atalaya.Atalaya;
import com.atalaya.items.CustomItems;
import net.kyori.adventure.text.Component;
import net.kyori.adventure.text.format.NamedTextColor;
import org.bukkit.command.Command;
import org.bukkit.command.CommandExecutor;
import org.bukkit.command.CommandSender;
import org.bukkit.entity.Player;

/**
 * Ejemplo de COMANDO: /atalaya baston
 * Entrega al jugador el item custom para probarlo en el juego.
 */
public class AtalayaCommand implements CommandExecutor {

    @Override
    public boolean onCommand(CommandSender sender, Command command, String label, String[] args) {
        if (!(sender instanceof Player player)) {
            sender.sendMessage("Solo un jugador puede usar este comando.");
            return true;
        }

        if (args.length == 1 && args[0].equalsIgnoreCase("baston")) {
            player.getInventory().addItem(CustomItems.crearBaston());
            player.sendMessage(Component.text("Recibiste el Baston de la Atalaya.", NamedTextColor.GREEN));
            return true;
        }

        if (args.length == 1 && args[0].equalsIgnoreCase("reload")) {
            Atalaya plugin = Atalaya.getInstance();
            plugin.reloadConfig();
            plugin.getRadiationManager().loadConfig();
            plugin.getRadiationManager().start(); // reinicia con el nuevo intervalo
            player.sendMessage(Component.text("Configuracion de Atalaya recargada.", NamedTextColor.GREEN));
            return true;
        }

        player.sendMessage(Component.text("Uso: /atalaya <baston|reload>", NamedTextColor.RED));
        return true;
    }
}
