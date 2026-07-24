package com.atalaya.radiation;

import com.atalaya.Atalaya;
import com.atalaya.items.HazmatArmor;
import org.bukkit.Bukkit;
import org.bukkit.GameMode;
import org.bukkit.Particle;
import org.bukkit.Sound;
import org.bukkit.entity.Player;
import org.bukkit.potion.PotionEffect;
import org.bukkit.potion.PotionEffectType;

import java.util.HashMap;
import java.util.Map;

/**
 * Sistema de radiacion de las geodas.
 *
 * Corre cada tick pero solo procesa una fraccion de los jugadores por tick
 * (reparto/stagger), de modo que cada jugador se revisa una vez por intervalo.
 * Para saber la fuente mas cercana consulta el {@link GeodeIndex} (barato),
 * en vez de escanear el mundo.
 */
public class RadiationManager {

    private static final int MAX_LEVEL = 4;

    private final Atalaya plugin;
    private final GeodeIndex index;

    // Valores cargados desde config.yml
    private long intervaloTicks;
    private double distanciaMaxima;
    private final Map<Integer, Double> danoPorNivel = new HashMap<>();

    private int taskId = -1;
    private long contadorTicks = 0;

    public RadiationManager(Atalaya plugin, GeodeIndex index) {
        this.plugin = plugin;
        this.index = index;
        loadConfig();
    }

    public void loadConfig() {
        var cfg = plugin.getConfig();
        intervaloTicks = Math.max(1L, cfg.getLong("radiacion.intervalo-ticks", 20L));
        distanciaMaxima = cfg.getDouble("radiacion.distancia-maxima", 12.0);
        danoPorNivel.clear();
        for (int nivel = 1; nivel <= MAX_LEVEL; nivel++) {
            danoPorNivel.put(nivel, cfg.getDouble("radiacion.dano-por-nivel." + nivel, nivel));
        }
    }

    /** Arranca (o reinicia) la tarea. Corre cada tick; el reparto lo hace tick(). */
    public void start() {
        stop();
        taskId = Bukkit.getScheduler()
                .runTaskTimer(plugin, this::tick, 1L, 1L)
                .getTaskId();
    }

    public void stop() {
        if (taskId != -1) {
            Bukkit.getScheduler().cancelTask(taskId);
            taskId = -1;
        }
    }

    private void tick() {
        long ranura = contadorTicks % intervaloTicks;
        contadorTicks++;

        for (Player player : Bukkit.getOnlinePlayers()) {
            // Reparte los jugadores: cada uno cae en una ranura fija segun su id,
            // asi se procesa una vez por intervalo y no todos en el mismo tick.
            if (Math.floorMod(player.getEntityId(), intervaloTicks) != ranura) {
                continue;
            }
            if (player.getGameMode() == GameMode.CREATIVE || player.getGameMode() == GameMode.SPECTATOR) {
                continue;
            }
            double distancia = index.distanciaMasCercana(player.getLocation(), distanciaMaxima);
            if (distancia < 0) {
                continue; // no hay amatista dentro del alcance -> sin efecto
            }
            aplicarRadiacion(player, nivelPorDistancia(distancia));
        }
    }

    private int nivelPorDistancia(double distancia) {
        double proporcion = 1.0 - (distancia / distanciaMaxima); // 1 = encima, 0 = al borde
        int nivel = (int) Math.ceil(proporcion * MAX_LEVEL);
        return Math.max(1, Math.min(MAX_LEVEL, nivel));
    }

    private void aplicarRadiacion(Player player, int nivel) {
        // Proteccion del traje Hazmat: cada pieza -25%, traje completo = inmune.
        int piezas = HazmatArmor.piezasEquipadas(player);
        if (piezas >= 4) {
            return; // inmunidad total: ni dano ni efecto
        }
        double factor = 1.0 - 0.25 * piezas;

        double dano = danoPorNivel.getOrDefault(nivel, (double) nivel) * factor;
        if (dano > 0) {
            player.damage(dano);
        }

        // Efecto "disfrazado": aparece un icono en el HUD y su nivel cambia solo.
        // El resource pack le pone tu imagen (radiacion.png) y el nombre "Radiacion".
        // amplificador = nivel-1  ->  el juego muestra el numero romano del nivel.
        int duracionTicks = (int) (intervaloTicks + 30L); // dura mas que el intervalo: no parpadea
        player.addPotionEffect(new PotionEffect(
                PotionEffectType.UNLUCK,
                duracionTicks,
                nivel - 1,
                true,   // ambient: menos intrusivo
                false,  // sin las particulas propias del efecto (usamos las nuestras)
                true    // mostrar icono en el HUD
        ));

        // Feedback extra, 100% server-side.
        player.playSound(player.getLocation(), Sound.BLOCK_AMETHYST_BLOCK_HIT, 0.6f, 0.5f);
        player.getWorld().spawnParticle(
                Particle.HAPPY_VILLAGER,
                player.getLocation().add(0, 1, 0),
                nivel * 3, 0.4, 0.6, 0.4, 0.0
        );
    }
}
