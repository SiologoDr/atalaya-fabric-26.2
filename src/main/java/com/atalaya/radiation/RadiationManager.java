package com.atalaya.radiation;

import com.atalaya.Atalaya;
import com.atalaya.items.HazmatArmor;
import org.bukkit.Bukkit;
import org.bukkit.GameMode;
import org.bukkit.NamespacedKey;
import org.bukkit.Particle;
import org.bukkit.Sound;
import org.bukkit.attribute.Attribute;
import org.bukkit.attribute.AttributeInstance;
import org.bukkit.attribute.AttributeModifier;
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
 * Consulta el {@link GeodeIndex} (barato) para saber la fuente mas cercana.
 *
 * Ademas del dano, aplica LENTITUD segun el nivel, integrada dentro del efecto
 * de radiacion (via modificador de atributo, sin un efecto de pocion aparte).
 */
public class RadiationManager {

    private static final int MAX_LEVEL = 4;
    // Lentitud por defecto por nivel (fraccion de velocidad restada). Acumulado.
    private static final double[] LENTITUD_DEFECTO = {0.10, 0.20, 0.30, 0.50};

    private final Atalaya plugin;
    private final GeodeIndex index;
    private final NamespacedKey lentitudKey;

    // Valores cargados desde config.yml
    private long intervaloTicks;
    private double distanciaMaxima;
    private final Map<Integer, Double> danoPorNivel = new HashMap<>();
    private final Map<Integer, Double> lentitudPorNivel = new HashMap<>();

    private int taskId = -1;
    private long contadorTicks = 0;

    public RadiationManager(Atalaya plugin, GeodeIndex index) {
        this.plugin = plugin;
        this.index = index;
        this.lentitudKey = new NamespacedKey(plugin, "radiacion_lentitud");
        loadConfig();
    }

    public void loadConfig() {
        var cfg = plugin.getConfig();
        intervaloTicks = Math.max(1L, cfg.getLong("radiacion.intervalo-ticks", 20L));
        distanciaMaxima = cfg.getDouble("radiacion.distancia-maxima", 12.0);
        danoPorNivel.clear();
        lentitudPorNivel.clear();
        for (int nivel = 1; nivel <= MAX_LEVEL; nivel++) {
            danoPorNivel.put(nivel, cfg.getDouble("radiacion.dano-por-nivel." + nivel, nivel));
            lentitudPorNivel.put(nivel, cfg.getDouble(
                    "radiacion.lentitud-por-nivel." + nivel, LENTITUD_DEFECTO[nivel - 1]));
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
        boolean activa = plugin.getSettings().isRadiacionActiva();

        long ranura = contadorTicks % intervaloTicks;
        contadorTicks++;

        for (Player player : Bukkit.getOnlinePlayers()) {
            // Reparte los jugadores: cada uno cae en una ranura fija segun su id.
            if (Math.floorMod(player.getEntityId(), intervaloTicks) != ranura) {
                continue;
            }
            if (!activa) {
                quitarLentitud(player); // si esta desactivada, aseguramos que no quede lentitud
                continue;
            }
            procesarJugador(player);
        }
    }

    private void procesarJugador(Player player) {
        // Creativo/espectador: inmunes -> sin dano ni lentitud.
        if (player.getGameMode() == GameMode.CREATIVE || player.getGameMode() == GameMode.SPECTATOR) {
            quitarLentitud(player);
            return;
        }

        // Traje Hazmat completo: inmune -> sin dano ni lentitud.
        int piezas = HazmatArmor.piezasEquipadas(player);
        if (piezas >= 4) {
            quitarLentitud(player);
            return;
        }

        double distancia = index.distanciaMasCercana(player.getLocation(), distanciaMaxima);
        if (distancia < 0) {
            quitarLentitud(player); // fuera de alcance -> se quita la lentitud
            return;
        }

        int nivel = nivelPorDistancia(distancia);
        double factor = 1.0 - 0.25 * piezas; // el traje parcial reduce el dano

        // Dano
        double dano = danoPorNivel.getOrDefault(nivel, (double) nivel) * factor;
        if (dano > 0) {
            player.damage(dano);
        }

        // Efecto visual (icono en HUD) + feedback
        mostrarEfecto(player, nivel);

        // Lentitud integrada, segun el nivel (mas nivel = mas lento).
        aplicarLentitud(player, lentitudPorNivel.getOrDefault(nivel, 0.0));
    }

    private int nivelPorDistancia(double distancia) {
        double proporcion = 1.0 - (distancia / distanciaMaxima); // 1 = encima, 0 = al borde
        int nivel = (int) Math.ceil(proporcion * MAX_LEVEL);
        return Math.max(1, Math.min(MAX_LEVEL, nivel));
    }

    private void mostrarEfecto(Player player, int nivel) {
        // Efecto "disfrazado": icono en el HUD cuyo nivel cambia solo.
        // El resource pack le pone la imagen (radiacion.png) y el nombre "Radiacion".
        int duracionTicks = (int) (intervaloTicks + 30L); // dura mas que el intervalo: no parpadea
        player.addPotionEffect(new PotionEffect(
                PotionEffectType.UNLUCK,
                duracionTicks,
                nivel - 1,
                true,   // ambient
                false,  // sin las particulas propias del efecto
                true    // mostrar icono
        ));

        player.playSound(player.getLocation(), Sound.BLOCK_AMETHYST_BLOCK_HIT, 0.6f, 0.5f);
        player.getWorld().spawnParticle(
                Particle.HAPPY_VILLAGER,
                player.getLocation().add(0, 1, 0),
                nivel * 3, 0.4, 0.6, 0.4, 0.0
        );
    }

    // ------------------------------------------------------------------
    //  Lentitud (modificador de atributo, sin efecto de pocion aparte)
    // ------------------------------------------------------------------

    private void aplicarLentitud(Player player, double fraccion) {
        if (fraccion <= 0) {
            quitarLentitud(player);
            return;
        }
        AttributeInstance attr = player.getAttribute(Attribute.MOVEMENT_SPEED);
        if (attr == null) {
            return;
        }
        AttributeModifier actual = attr.getModifier(lentitudKey);
        if (actual != null) {
            if (actual.getAmount() == -fraccion) {
                return; // ya esta puesto el valor correcto
            }
            attr.removeModifier(lentitudKey);
        }
        // ADD_SCALAR con -fraccion => resta ese % de la velocidad. Transitorio (no se guarda).
        attr.addTransientModifier(new AttributeModifier(
                lentitudKey, -fraccion, AttributeModifier.Operation.ADD_SCALAR));
    }

    private void quitarLentitud(Player player) {
        AttributeInstance attr = player.getAttribute(Attribute.MOVEMENT_SPEED);
        if (attr != null && attr.getModifier(lentitudKey) != null) {
            attr.removeModifier(lentitudKey);
        }
    }

    /** Quita la lentitud a todos (al desactivar la radiacion o al apagar el plugin). */
    public void limpiarLentitudTodos() {
        for (Player p : Bukkit.getOnlinePlayers()) {
            quitarLentitud(p);
        }
    }
}
