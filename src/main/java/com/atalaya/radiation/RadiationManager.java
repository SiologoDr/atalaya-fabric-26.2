package com.atalaya.radiation;

import com.atalaya.Atalaya;
import com.atalaya.items.HazmatArmor;
import net.kyori.adventure.key.Key;
import net.kyori.adventure.text.Component;
import net.kyori.adventure.text.format.NamedTextColor;
import net.kyori.adventure.text.format.TextColor;
import net.kyori.adventure.text.format.TextDecoration;
import org.bukkit.Bukkit;
import org.bukkit.GameMode;
import org.bukkit.NamespacedKey;
import org.bukkit.Particle;
import org.bukkit.Sound;
import org.bukkit.attribute.Attribute;
import org.bukkit.attribute.AttributeInstance;
import org.bukkit.attribute.AttributeModifier;
import org.bukkit.entity.Player;

import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;
import java.util.UUID;

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

    // --- Indicador en pantalla -------------------------------------------
    // No usamos un efecto de pocion: los efectos no se pueden registrar nuevos
    // y secuestrar uno vanilla (antes usabamos UNLUCK) renombraba ese efecto en
    // TODO el juego y ademas tocaba el atributo de suerte, que afecta al botin.
    // En su lugar dibujamos nuestro propio icono con una fuente del resource pack.
    private static final Key FUENTE_ICONOS = Key.key("atalaya", "iconos");
    private static final String ICONO_RADIACION = ""; // ver assets/atalaya/font/iconos.json
    private static final String[] ROMANOS = {"I", "II", "III", "IV"};

    // Quien tiene el aviso puesto ahora mismo, para poder borrarlo al alejarse.
    private final Set<UUID> avisados = new HashSet<>();

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
                limpiar(player); // desactivada: ni lentitud ni aviso pegados
                continue;
            }
            procesarJugador(player);
        }
    }

    private void procesarJugador(Player player) {
        // Creativo/espectador: inmunes -> sin dano ni lentitud.
        if (player.getGameMode() == GameMode.CREATIVE || player.getGameMode() == GameMode.SPECTATOR) {
            limpiar(player);
            return;
        }

        // Traje Hazmat completo: inmune -> sin dano ni lentitud.
        int piezas = HazmatArmor.piezasEquipadas(player);
        if (piezas >= 4) {
            limpiar(player);
            return;
        }

        double distancia = index.distanciaMasCercana(player.getLocation(), distanciaMaxima);
        if (distancia < 0) {
            limpiar(player); // fuera de alcance -> se quita lentitud y aviso
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

    /**
     * Dibuja el aviso de radiacion sobre la hotbar: nuestro icono (via la fuente
     * atalaya:iconos del resource pack) mas el nivel en romanos, coloreado segun
     * lo fuerte que sea.
     */
    private void mostrarEfecto(Player player, int nivel) {
        player.sendActionBar(
                Component.text()
                        // El icono lleva la fuente; el texto NO (si no, saldria
                        // tambien mapeado a la imagen).
                        .append(Component.text(ICONO_RADIACION).font(FUENTE_ICONOS))
                        .append(Component.text("  RADIACION " + ROMANOS[nivel - 1],
                                colorPorNivel(nivel)).decorate(TextDecoration.BOLD))
                        .build()
        );
        avisados.add(player.getUniqueId());

        player.playSound(player.getLocation(), Sound.BLOCK_AMETHYST_BLOCK_HIT, 0.6f, 0.5f);
        player.getWorld().spawnParticle(
                Particle.HAPPY_VILLAGER,
                player.getLocation().add(0, 1, 0),
                nivel * 3, 0.4, 0.6, 0.4, 0.0
        );
    }

    private static TextColor colorPorNivel(int nivel) {
        return switch (nivel) {
            case 1 -> NamedTextColor.YELLOW;
            case 2 -> NamedTextColor.GOLD;
            case 3 -> NamedTextColor.RED;
            default -> NamedTextColor.DARK_RED;
        };
    }

    /**
     * Borra el aviso al salir del alcance. Sin esto la barra de accion se queda
     * hasta que se desvanece sola (unos 3 segundos) diciendo que sigues irradiado.
     */
    private void quitarAviso(Player player) {
        if (avisados.remove(player.getUniqueId())) {
            player.sendActionBar(Component.empty());
        }
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

    /** Deja a un jugador sin rastro de radiacion (lentitud + aviso en pantalla). */
    private void limpiar(Player player) {
        quitarLentitud(player);
        quitarAviso(player);
    }

    /** Limpia a todos (al desactivar la radiacion o al apagar el plugin). */
    public void limpiarLentitudTodos() {
        for (Player p : Bukkit.getOnlinePlayers()) {
            limpiar(p);
        }
    }
}
