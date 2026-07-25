package com.atalaya.commands;

import com.atalaya.Atalaya;
import com.atalaya.items.HazmatArmor;
import com.atalaya.menu.ConfigMenu;
import net.kyori.adventure.text.Component;
import net.kyori.adventure.text.format.NamedTextColor;
import org.bukkit.command.Command;
import org.bukkit.command.CommandExecutor;
import org.bukkit.command.CommandSender;
import org.bukkit.command.TabCompleter;
import org.bukkit.entity.Player;

import java.util.ArrayList;
import java.util.List;
import java.util.Locale;

/**
 * Comando principal /atalaya con autocompletado.
 * Subcomandos: traje, menu (admin), reload.
 */
public class AtalayaCommand implements CommandExecutor, TabCompleter {

    private static final List<String> SUBCOMANDOS = List.of("traje", "menu", "reload");

    @Override
    public boolean onCommand(CommandSender sender, Command command, String label, String[] args) {
        if (!(sender instanceof Player player)) {
            sender.sendMessage("Solo un jugador puede usar este comando.");
            return true;
        }

        if (args.length == 1 && args[0].equalsIgnoreCase("traje")) {
            player.getInventory().addItem(
                    HazmatArmor.casco(),
                    HazmatArmor.pechera(),
                    HazmatArmor.pantalon(),
                    HazmatArmor.botas()
            );
            player.sendMessage(Component.text("Recibiste el traje Hazmat completo.", NamedTextColor.GREEN));
            return true;
        }

        if (args.length == 1 && args[0].equalsIgnoreCase("menu")) {
            if (!player.hasPermission("atalaya.admin")) {
                player.sendMessage(Component.text("No tienes permiso para esto.", NamedTextColor.RED));
                return true;
            }
            new ConfigMenu(Atalaya.getInstance()).abrir(player);
            return true;
        }

        if (args.length == 1 && args[0].equalsIgnoreCase("reload")) {
            Atalaya plugin = Atalaya.getInstance();
            plugin.reloadConfig();
            plugin.getSettings().load();
            plugin.getGeodeIndex().loadConfig();
            plugin.getRadiationManager().loadConfig();
            plugin.getRadiationManager().start(); // reinicia con el nuevo intervalo
            player.sendMessage(Component.text("Configuracion de Atalaya recargada.", NamedTextColor.GREEN));
            return true;
        }

        player.sendMessage(Component.text("Uso: /atalaya <traje|menu|reload>", NamedTextColor.RED));
        return true;
    }

    @Override
    public List<String> onTabComplete(CommandSender sender, Command command, String alias, String[] args) {
        if (args.length != 1) {
            return List.of();
        }
        String prefijo = args[0].toLowerCase(Locale.ROOT);
        List<String> sugerencias = new ArrayList<>();
        for (String sub : SUBCOMANDOS) {
            // 'menu' solo se sugiere a quien tiene permiso.
            if (sub.equals("menu")
                    && !(sender instanceof Player p && p.hasPermission("atalaya.admin"))) {
                continue;
            }
            if (sub.startsWith(prefijo)) {
                sugerencias.add(sub);
            }
        }
        return sugerencias;
    }
}
