package com.atalaya.config;

import com.atalaya.Atalaya;
import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import net.fabricmc.loader.api.FabricLoader;
import net.minecraft.resources.Identifier;

import java.io.IOException;
import java.io.Reader;
import java.io.Writer;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;

/**
 * Interruptores de las mecanicas del mod, persistidos en
 * config/atalaya.json.
 *
 * Para anadir una mecanica nueva basta con meter aqui un campo y darle un slot
 * en {@link com.atalaya.menu.ConfigMenu}.
 */
public final class AtalayaConfig {

    private static final Gson GSON = new GsonBuilder().setPrettyPrinting().create();
    private static final Path RUTA =
            FabricLoader.getInstance().getConfigDir().resolve("atalaya.json");

    private static AtalayaConfig instancia;

    // --- Interruptores ---
    private boolean crafteoHazmat = true;
    private boolean radiacionActiva = true;
    /** Cubre las dos: fundir carbon activado y craftear el filtro. */
    private boolean filtrosActivos = true;
    /** Cubre el drop del colmillo Y su mejora en la herreria. */
    private boolean colmilloActivo = true;
    /** Cubre craftear el cristal pulido Y su mejora en la herreria. */
    private boolean cristalActivo = true;

    public static AtalayaConfig get() {
        if (instancia == null) {
            instancia = cargar();
        }
        return instancia;
    }

    private static AtalayaConfig cargar() {
        if (Files.exists(RUTA)) {
            try (Reader r = Files.newBufferedReader(RUTA, StandardCharsets.UTF_8)) {
                AtalayaConfig leido = GSON.fromJson(r, AtalayaConfig.class);
                if (leido != null) {
                    return leido;
                }
            } catch (IOException | RuntimeException e) {
                Atalaya.LOGGER.error("No pude leer {}: {}. Uso los valores por defecto.",
                        RUTA, e.getMessage());
            }
        }
        AtalayaConfig nuevo = new AtalayaConfig();
        nuevo.guardar();
        return nuevo;
    }

    public void guardar() {
        try {
            Files.createDirectories(RUTA.getParent());
            try (Writer w = Files.newBufferedWriter(RUTA, StandardCharsets.UTF_8)) {
                GSON.toJson(this, w);
            }
        } catch (IOException e) {
            Atalaya.LOGGER.error("No pude guardar {}: {}", RUTA, e.getMessage());
        }
    }

    // ------------------------------------------------------------------

    public boolean isCrafteoHazmat() {
        return crafteoHazmat;
    }

    public void setCrafteoHazmat(boolean valor) {
        this.crafteoHazmat = valor;
        guardar();
    }

    public boolean isRadiacionActiva() {
        return radiacionActiva;
    }

    public void setRadiacionActiva(boolean valor) {
        this.radiacionActiva = valor;
        guardar();
    }

    public boolean isFiltrosActivos() {
        return filtrosActivos;
    }

    public void setFiltrosActivos(boolean valor) {
        this.filtrosActivos = valor;
        guardar();
    }

    public boolean isColmilloActivo() {
        return colmilloActivo;
    }

    public void setColmilloActivo(boolean valor) {
        this.colmilloActivo = valor;
        guardar();
    }

    public boolean isCristalActivo() {
        return cristalActivo;
    }

    public void setCristalActivo(boolean valor) {
        this.cristalActivo = valor;
        guardar();
    }


    /**
     * Decide si una receta de este mod se puede usar ahora mismo.
     *
     * Es el unico sitio que ata recetas a interruptores; lo consulta el mixin de
     * RecipeManager, que cubre por igual la mesa de crafteo y el horno.
     * Las recetas de otros mods y las de vanilla nunca se tocan.
     */
    public boolean permiteReceta(Identifier id) {
        if (!Atalaya.MOD_ID.equals(id.getNamespace())) {
            return true;
        }
        String ruta = id.getPath();
        // Las mejoras de herreria van con su item, no con el traje: apagar el
        // colmillo apaga tanto su drop como su mejora.
        if (ruta.startsWith("antiveneno_")) {
            return colmilloActivo;
        }
        if (ruta.equals("cristal_pulido") || ruta.startsWith("visor_")) {
            return cristalActivo;
        }
        if (ruta.startsWith("hazmat_")) {
            return crafteoHazmat;
        }
        if (ruta.equals("carbon_activado") || ruta.equals("filtro_carbon")) {
            return filtrosActivos;
        }
        return true;
    }
}
