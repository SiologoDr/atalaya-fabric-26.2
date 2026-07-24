package com.atalaya.radiation;

import org.bukkit.World;
import org.bukkit.block.Block;
import org.bukkit.event.EventHandler;
import org.bukkit.event.EventPriority;
import org.bukkit.event.Listener;
import org.bukkit.event.block.BlockBreakEvent;
import org.bukkit.event.world.ChunkLoadEvent;
import org.bukkit.event.world.ChunkUnloadEvent;

/**
 * Mantiene el GeodeIndex al dia sin escanear el mundo cada segundo:
 * - Al cargar un chunk overworld -> se escanea una vez (async) buscando gemacion.
 * - Al descargarlo -> se olvida.
 * - Al romper la gemacion (destruir la geoda) -> deja de radiar.
 *
 * No hay manejo de "colocar bloque" a proposito: la amatista en gemacion no se
 * puede colocar en supervivencia, y solo queremos radiacion en geodas naturales.
 */
public class GeodeListener implements Listener {

    private final GeodeIndex index;

    public GeodeListener(GeodeIndex index) {
        this.index = index;
    }

    @EventHandler
    public void onChunkLoad(ChunkLoadEvent event) {
        if (event.getWorld().getEnvironment() != World.Environment.NORMAL) {
            return; // las geodas solo generan en el overworld
        }
        index.escanearChunkAsync(event.getChunk());
    }

    @EventHandler
    public void onChunkUnload(ChunkUnloadEvent event) {
        index.quitarChunk(event.getWorld().getUID(), event.getChunk().getX(), event.getChunk().getZ());
    }

    @EventHandler(priority = EventPriority.MONITOR, ignoreCancelled = true)
    public void onBlockBreak(BlockBreakEvent event) {
        Block b = event.getBlock();
        if (RadiationSources.esFuente(b.getType())) {
            index.quitarBloque(b.getWorld().getUID(), b.getX(), b.getY(), b.getZ());
        }
    }
}
