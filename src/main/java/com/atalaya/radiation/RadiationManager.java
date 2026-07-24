package com.atalaya.radiation;

import com.atalaya.Atalaya;
import net.kyori.adventure.text.Component;
import net.kyori.adventure.text.format.NamedTextColor;
import org.bukkit.Bukkit;
import org.bukkit.GameMode;
import org.bukkit.Location;
import org.bukkit.Material;
import org.bukkit.Particle;
import org.bukkit.Sound;
import org.bukkit.World;
import org.bukkit.block.Block;
import org.bukkit.entity.Player;

import java.util.EnumSet;
import java.util.HashMap;
import java.util.Map;
import java.util.Set;

/**
 * Sistema de radiacion de las geodas.
 *
 * Cada cierto intervalo revisa, para cada jugador, cual es el bloque de amatista
 * mas cercano. Segun la distancia asigna un NIVEL (1 a 4) y le drena vida:
 * cuanto mas cerca de la amatista, mayor el nivel y mas dano. Pasada la
 * distancia maxima, no hay radiacion.
 */
public class RadiationManager {

    private static final int MAX_LEVEL = 4;

    // Bloques que emiten radiacion (todo lo que forma la parte de amatista de una geoda).
    private static final Set<Material> FUENTES = EnumSet.of(
            Material.AMETHYST_BLOCK,
            Material.BUDDING_AMETHYST,
            Material.AMETHYST_CLUSTER,
            Material.SMALL_AMETHYST_BUD,
            Material.MEDIUM_AMETHYST_BUD,
            Material.LARGE_AMETHYST_BUD
    );

    private final Atalaya plugin;

    // Valores cargados desde config.yml
    private long intervaloTicks;
    private double distanciaMaxima;
    private final Map<Integer, Double> danoPorNivel = new HashMap<>();

    private int taskId = -1;

    public RadiationManager(Atalaya plugin) {
        this.plugin = plugin;
        loadConfig();
    }

    /** Lee (o relee) los valores desde config.yml. */
    public void loadConfig() {
        var cfg = plugin.getConfig();
        intervaloTicks = cfg.getLong("radiacion.intervalo-ticks", 20L);
        distanciaMaxima = cfg.getDouble("radiacion.distancia-maxima", 12.0);
        danoPorNivel.clear();
        for (int nivel = 1; nivel <= MAX_LEVEL; nivel++) {
            danoPorNivel.put(nivel, cfg.getDouble("radiacion.dano-por-nivel." + nivel, nivel));
        }
    }

    /** Arranca (o reinicia) la tarea periodica. */
    public void start() {
        stop();
        taskId = Bukkit.getScheduler()
                .runTaskTimer(plugin, this::tick, 0L, intervaloTicks)
                .getTaskId();
    }

    /** Detiene la tarea periodica. */
    public void stop() {
        if (taskId != -1) {
            Bukkit.getScheduler().cancelTask(taskId);
            taskId = -1;
        }
    }

    private void tick() {
        for (Player player : Bukkit.getOnlinePlayers()) {
            // Creativo y espectador no reciben radiacion.
            if (player.getGameMode() == GameMode.CREATIVE || player.getGameMode() == GameMode.SPECTATOR) {
                continue;
            }
            double distancia = distanciaFuenteMasCercana(player);
            if (distancia < 0) {
                continue; // no hay amatista dentro del alcance -> sin efecto
            }
            aplicarRadiacion(player, nivelPorDistancia(distancia));
        }
    }

    /** Convierte una distancia (dentro del alcance) en un nivel 1..4. */
    private int nivelPorDistancia(double distancia) {
        double proporcion = 1.0 - (distancia / distanciaMaxima); // 1 = encima, 0 = al borde
        int nivel = (int) Math.ceil(proporcion * MAX_LEVEL);
        return Math.max(1, Math.min(MAX_LEVEL, nivel));
    }

    private void aplicarRadiacion(Player player, int nivel) {
        double dano = danoPorNivel.getOrDefault(nivel, (double) nivel);
        player.damage(dano);

        // Feedback 100% server-side (el jugador no descarga nada).
        player.sendActionBar(
                Component.text("☢ Radiacion - Nivel " + nivel, colorPorNivel(nivel))
        );
        player.playSound(player.getLocation(), Sound.BLOCK_AMETHYST_BLOCK_HIT, 0.6f, 0.5f);
        player.getWorld().spawnParticle(
                Particle.HAPPY_VILLAGER,
                player.getLocation().add(0, 1, 0),
                nivel * 3, 0.4, 0.6, 0.4, 0.0
        );
    }

    private NamedTextColor colorPorNivel(int nivel) {
        return switch (nivel) {
            case 4 -> NamedTextColor.DARK_RED;
            case 3 -> NamedTextColor.RED;
            case 2 -> NamedTextColor.GOLD;
            default -> NamedTextColor.YELLOW;
        };
    }

    /**
     * Busca el bloque de amatista mas cercano al jugador dentro de la distancia
     * maxima. Devuelve la distancia (en bloques) o -1 si no hay ninguno cerca.
     */
    private double distanciaFuenteMasCercana(Player player) {
        Location loc = player.getLocation();
        World world = player.getWorld();

        int radio = (int) Math.ceil(distanciaMaxima);
        int bx = loc.getBlockX();
        int by = loc.getBlockY();
        int bz = loc.getBlockZ();

        int minY = world.getMinHeight();
        int maxY = world.getMaxHeight() - 1;

        double mejorSq = Double.MAX_VALUE;
        double maxSq = distanciaMaxima * distanciaMaxima;

        for (int x = -radio; x <= radio; x++) {
            for (int y = -radio; y <= radio; y++) {
                int yy = by + y;
                if (yy < minY || yy > maxY) {
                    continue;
                }
                for (int z = -radio; z <= radio; z++) {
                    Block block = world.getBlockAt(bx + x, yy, bz + z);
                    if (!FUENTES.contains(block.getType())) {
                        continue;
                    }
                    double dx = (bx + x + 0.5) - loc.getX();
                    double dy = (yy + 0.5) - loc.getY();
                    double dz = (bz + z + 0.5) - loc.getZ();
                    double sq = dx * dx + dy * dy + dz * dz;
                    if (sq < mejorSq) {
                        mejorSq = sq;
                    }
                }
            }
        }

        return (mejorSq <= maxSq) ? Math.sqrt(mejorSq) : -1;
    }
}
