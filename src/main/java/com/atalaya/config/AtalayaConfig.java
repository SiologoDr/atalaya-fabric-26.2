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
 * TODO arranca APAGADO. Un mundo o servidor recien puesto se comporta como
 * vanilla, y es un operador quien va abriendo cada mecanica desde el panel
 * cuando toca. Eso es lo que permite anunciarlas como evento en vez de que
 * aparezcan solas, y evita que nadie se encuentre con la lluvia comiendole la
 * armadura sin haberlo pedido.
 *
 * Vale tambien para lo que se anada mas adelante: un campo nuevo entra en false
 * aunque el fichero de configuracion sea viejo y no lo mencione, asi que
 * actualizar el mod nunca enciende nada por su cuenta.
 *
 * Para anadir una mecanica basta con meter aqui un campo y una linea en
 * {@link com.atalaya.menu.ConfigMenu}.
 */
public final class AtalayaConfig {

    private static final Gson GSON = new GsonBuilder().setPrettyPrinting().create();
    private static final Path RUTA =
            FabricLoader.getInstance().getConfigDir().resolve("atalaya.json");

    private static AtalayaConfig instancia;

    // --- Interruptores ---
    /** Solo la mejora en la mesa de herreria: hierro + lingote -> pieza hazmat. */
    private boolean crafteoHazmat = false;
    /** Cubre craftear el lingote blindado, el material del traje. */
    private boolean lingoteActivo = false;
    /** Cubre craftear la miel cristalizada. */
    private boolean mielActiva = false;
    /** Cubre que las abejas suelten miel cristalizada al morir. */
    private boolean dropMielActivo = false;
    /** Cubre fabricar la plantilla de sellado Y duplicarla. */
    private boolean plantillaActiva = false;
    private boolean radiacionActiva = false;
    /** Que la hidratacion baje en el desierto. Apagada, el nivel se congela. */
    private boolean hidratacionActiva = false;
    /** Que la lluvia coma la armadura de quien se moja. */
    private boolean corrosionActiva = false;
    /** Que la lluvia deje empapado y a media velocidad. */
    private boolean empapadoActivo = false;
    /** Hervir la botella de agua, tanto al horno como a la fogata. */
    private boolean aguaActiva = false;
    /** Fundir carbon para obtener carbon activado, el relleno del cartucho. */
    private boolean carbonActivo = false;
    /** Montar el cartucho: carbon activado entre dos placas de hierro. */
    private boolean filtrosActivos = false;
    /** Que la arana comun suelte el colmillo seco al morir. */
    private boolean dropColmilloActivo = false;
    /** Que la arana de cueva suelte el veneno al morir. */
    private boolean dropVenenoActivo = false;
    /** Que salga el espejo de mar al pescar. */
    private boolean dropEspejoActivo = false;
    /** Que el conejo suelte la pata ligera al morir. */
    private boolean dropPataActivo = false;
    /** Que el pollo suelte el alon al morir. */
    private boolean dropAlonActivo = false;
    /** Cubre juntar colmillo y veneno Y montar la mejora en la herreria. */
    private boolean colmilloActivo = false;
    /** Vitrificar el bloque de alga seca en el horno: la mitad dura de la lente. */
    private boolean algaActiva = false;
    /** Cubre montar la lente de mar Y su mejora del visor en la herreria. */
    private boolean lenteActiva = false;
    /** Cubre montar la pata alada Y aplicarla al traje en la herreria. */
    private boolean pataAladaActiva = false;

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

    public boolean isLingoteActivo() {
        return lingoteActivo;
    }

    public void setLingoteActivo(boolean valor) {
        this.lingoteActivo = valor;
        guardar();
    }

    public boolean isMielActiva() {
        return mielActiva;
    }

    public void setMielActiva(boolean valor) {
        this.mielActiva = valor;
        guardar();
    }

    public boolean isDropMielActivo() {
        return dropMielActivo;
    }

    public void setDropMielActivo(boolean valor) {
        this.dropMielActivo = valor;
        guardar();
    }

    public boolean isPlantillaActiva() {
        return plantillaActiva;
    }

    public void setPlantillaActiva(boolean valor) {
        this.plantillaActiva = valor;
        guardar();
    }

    public boolean isRadiacionActiva() {
        return radiacionActiva;
    }

    public void setRadiacionActiva(boolean valor) {
        this.radiacionActiva = valor;
        guardar();
    }

    public boolean isHidratacionActiva() {
        return hidratacionActiva;
    }

    public void setHidratacionActiva(boolean valor) {
        this.hidratacionActiva = valor;
        guardar();
    }

    public boolean isCorrosionActiva() {
        return corrosionActiva;
    }

    public boolean isEmpapadoActivo() {
        return empapadoActivo;
    }

    public void setEmpapadoActivo(boolean valor) {
        this.empapadoActivo = valor;
        guardar();
    }

    public void setCorrosionActiva(boolean valor) {
        this.corrosionActiva = valor;
        guardar();
    }

    public boolean isAguaActiva() {
        return aguaActiva;
    }

    public void setAguaActiva(boolean valor) {
        this.aguaActiva = valor;
        guardar();
    }

    public boolean isCarbonActivo() {
        return carbonActivo;
    }

    public void setCarbonActivo(boolean valor) {
        this.carbonActivo = valor;
        guardar();
    }

    public boolean isFiltrosActivos() {
        return filtrosActivos;
    }

    public void setFiltrosActivos(boolean valor) {
        this.filtrosActivos = valor;
        guardar();
    }

    public boolean isDropColmilloActivo() {
        return dropColmilloActivo;
    }

    public void setDropColmilloActivo(boolean valor) {
        this.dropColmilloActivo = valor;
        guardar();
    }

    public boolean isDropVenenoActivo() {
        return dropVenenoActivo;
    }

    public void setDropVenenoActivo(boolean valor) {
        this.dropVenenoActivo = valor;
        guardar();
    }

    public boolean isDropEspejoActivo() {
        return dropEspejoActivo;
    }

    public void setDropEspejoActivo(boolean valor) {
        this.dropEspejoActivo = valor;
        guardar();
    }

    public boolean isColmilloActivo() {
        return colmilloActivo;
    }

    public void setColmilloActivo(boolean valor) {
        this.colmilloActivo = valor;
        guardar();
    }

    public boolean isAlgaActiva() {
        return algaActiva;
    }

    public void setAlgaActiva(boolean valor) {
        this.algaActiva = valor;
        guardar();
    }

    public boolean isLenteActiva() {
        return lenteActiva;
    }

    public void setLenteActiva(boolean valor) {
        this.lenteActiva = valor;
        guardar();
    }

    public boolean isDropPataActivo() {
        return dropPataActivo;
    }

    public void setDropPataActivo(boolean valor) {
        this.dropPataActivo = valor;
        guardar();
    }

    public boolean isDropAlonActivo() {
        return dropAlonActivo;
    }

    public void setDropAlonActivo(boolean valor) {
        this.dropAlonActivo = valor;
        guardar();
    }

    public boolean isPataAladaActiva() {
        return pataAladaActiva;
    }

    public void setPataAladaActiva(boolean valor) {
        this.pataAladaActiva = valor;
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
        // Las mejoras de herreria van con su item, no con el traje. El colmillo
        // venenoso cubre las dos cosas: juntar sus dos mitades y montarlo en la
        // pieza. Los drops de la arana comun y la de cueva van aparte.
        if (ruta.startsWith("antiveneno_") || ruta.equals("colmillo_venenoso")) {
            return colmilloActivo;
        }
        // La cadena de la lente va partida en sus dos pasos, igual que la del
        // cartucho: se puede permitir vitrificar el alga pero no montar la
        // lente, o al reves. El espejo no aparece aqui porque no es una receta:
        // sale pescando, y lo corta dropEspejoActivo desde AtalayaLoot.
        if (ruta.equals("alga_vitrificada")) {
            return algaActiva;
        }
        if (ruta.equals("lente_mar") || ruta.startsWith("visor_")) {
            return lenteActiva;
        }
        // La pata ligera y el alon ya no se craftean: los sueltan el conejo y el
        // pollo, y los cortan sus interruptores de drop desde AtalayaLoot. Aqui
        // solo queda montar la pata alada y aplicarla a las piezas.
        if (ruta.equals("pata_alada") || ruta.startsWith("ligera_")) {
            return pataAladaActiva;
        }
        // Cada paso de la cadena del traje tiene su propio interruptor, asi que
        // se puede cortar por donde interese: permitir los materiales pero
        // bloquear la herreria, o al contrario.
        if (ruta.equals("lingote_blindado")) {
            return lingoteActivo;
        }
        if (ruta.equals("miel_cristalizada")) {
            return mielActiva;
        }
        // Cubre la plantilla y su copia, que comparten prefijo.
        if (ruta.startsWith("plantilla_sellado")) {
            return plantillaActiva;
        }
        // Ya solo las cuatro recetas de herreria de las piezas.
        if (ruta.startsWith("hazmat_")) {
            return crafteoHazmat;
        }
        // El agua purificada va aparte de la sed que cura, asi que se puede
        // abrir el desierto antes que su remedio, o al reves. Cubre las dos
        // recetas, horno y fogata, que comparten prefijo.
        if (ruta.startsWith("agua_purificada")) {
            return aguaActiva;
        }
        // La cadena del cartucho va separada en sus dos pasos, igual que la del
        // traje: se puede permitir fundir el carbon pero no montar el filtro.
        if (ruta.equals("carbon_activado")) {
            return carbonActivo;
        }
        if (ruta.equals("filtro_carbon")) {
            return filtrosActivos;
        }
        return true;
    }
}
