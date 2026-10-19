package com.atalaya.bestiario;

import com.atalaya.catalogo.Categoria;
import com.atalaya.catalogo.Entrada;
import net.fabricmc.fabric.api.biome.v1.BiomeSelectionContext;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.SimpleParticleType;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.EntitySpawnReason;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.MobCategory;
import net.minecraft.world.entity.SpawnPlacementType;
import net.minecraft.world.entity.SpawnPlacementTypes;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.item.Item;
import net.minecraft.world.level.ServerLevelAccessor;
import net.minecraft.world.level.levelgen.Heightmap;
import org.jspecify.annotations.Nullable;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.function.Predicate;
import java.util.function.Supplier;

/**
 * La ficha de un mob del bestiario: lo que hace falta para registrarlo (Bestias), para que aparezca solo cuando esta
 * encendido en el menu de los mobs (Bestiario) y para pintarlo (BestiaRenderer lee su malla y sus animaciones de
 * assets/atalaya/bestiario/&lt;id&gt;.json, que hace bestiario_juego.py).
 *
 * Todo lo suyo lleva su id: la textura (textures/entity/bestiario/&lt;id&gt;.png y _brillo), el huevo (huevo_&lt;id&gt;),
 * los sonidos (bestia.&lt;id&gt;.&lt;nombre&gt;), las particulas (bestia_&lt;id&gt;_&lt;nombre&gt;), el icono del menu
 * (menu/mob/&lt;id&gt;) y el rotulo del chat (mob_&lt;id&gt;_NN).
 */
public final class Bestia implements Entrada {

    /** Si puede aparecer ahi (ademas de estar encendido): la luz, el suelo, la altura... */
    @FunctionalInterface
    public interface Regla {
        boolean puede(EntityType<?> tipo, ServerLevelAccessor nivel, EntitySpawnReason motivo, BlockPos pos,
                      RandomSource azar);

        /** Como cualquier monstruo: a oscuras y en un suelo en el que se pueda aparecer. */
        @SuppressWarnings("unchecked")
        Regla MONSTRUO = (tipo, nivel, motivo, pos, azar) ->
                Monster.checkMonsterSpawnRules((EntityType<? extends Monster>) tipo, nivel, motivo, pos, azar);
        /** Con cualquier luz (de dia tambien): solo hace falta un suelo. */
        @SuppressWarnings("unchecked")
        Regla SIEMPRE = (tipo, nivel, motivo, pos, azar) ->
                Monster.checkAnyLightMonsterSpawnRules((EntityType<? extends Monster>) tipo, nivel, motivo, pos, azar);

        default Regla y(Regla otra) {
            return (tipo, nivel, motivo, pos, azar) -> puede(tipo, nivel, motivo, pos, azar)
                    && otra.puede(tipo, nivel, motivo, pos, azar);
        }
    }

    /** Como se mueve una de sus particulas (BestiaParticula, en el cliente). */
    public enum Vuelo {
        /** Cae con su peso y rebota (astillas, gotas, escamas). */
        CAE,
        /** Sube despacio y se apaga (chispas, esporas, ceniza encendida). */
        SUBE,
        /** Flota quieta, deriva un poco y se desvanece (polvo, humo, niebla): grande. */
        FLOTA,
        /** Pequena y ligera: deriva meciendose y cae poco a poco (petalos, ceniza, chispas, flores). */
        DERIVA,
        /** Sale disparada y frena (el estallido). */
        ESTALLA,
        /** Tumbada en el suelo, crece y se apaga (marcas, charcos, ondas). */
        SUELO,
        /** Un fogonazo quieto que crece y se va en unos ticks. */
        DESTELLO
    }

    /** Una de sus particulas: su nombre, como se mueve, si brilla (no se apaga de noche) y cuantos sprites tiene. */
    public record Particula(String nombre, Vuelo vuelo, boolean luz) {
    }

    private final String id;
    final EntityType.EntityFactory<? extends BestiaEntity> fabrica;
    private String titulo = "";
    private String texto = "";
    private String etiquetas = "";
    private String grupo = "";
    MobCategory categoriaMob = MobCategory.MONSTER;
    float ancho = 0.6F;
    float alto = 1.8F;
    float ojos = -1.0F;
    int rastreo = 8;
    boolean inmuneFuego;
    Supplier<AttributeSupplier.Builder> atributos = Monster::createMonsterAttributes;
    final List<String> sonidos = new ArrayList<>(List.of("ambiente", "herido", "muerte", "paso"));
    final Map<String, Particula> particulas = new LinkedHashMap<>();
    /** Lo que dura su animacion de muerte (ticks): hasta entonces no se va. */
    public int muerteTicks = 20;
    /** Lo que suelta al deshacerse (una de sus particulas), o null. */
    public @Nullable String particulaMuerte;
    /** Lo grande que es su sombra (radio, en bloques). */
    public float sombra = 0.5F;
    /** Donde aparece solo: los biomas (null, en ninguno: sale de otra forma), el peso y el grupo. */
    @Nullable Predicate<BiomeSelectionContext> biomas;
    int peso;
    int minimo = 1;
    int maximo = 1;
    SpawnPlacementType colocacion = SpawnPlacementTypes.ON_GROUND;
    Heightmap.Types altura = Heightmap.Types.MOTION_BLOCKING_NO_LEAVES;
    Regla regla = Regla.MONSTRUO;

    /** Lo registrado (Bestias.registrar). */
    public EntityType<? extends BestiaEntity> tipo;
    public Item huevo;
    final Map<String, SoundEvent> eventos = new HashMap<>();
    final Map<String, SimpleParticleType> tiposParticula = new HashMap<>();

    Bestia(String id, EntityType.EntityFactory<? extends BestiaEntity> fabrica) {
        this.id = id;
        this.fabrica = fabrica;
    }

    // ------------------------------------------------------------------
    //  Como se describe (en Bestias)
    // ------------------------------------------------------------------

    Bestia titulo(String titulo, String texto) {
        this.titulo = titulo;
        this.texto = texto;
        return this;
    }

    /** El grupo del menu de los mobs en el que va (CREEPERS, FANTASMAS...). */
    Bestia grupo(String grupo) {
        this.grupo = grupo;
        return this;
    }

    Bestia etiquetas(String etiquetas) {
        this.etiquetas = etiquetas;
        return this;
    }

    /** Su caja: ancho, alto y a que altura tiene los ojos (sin ojos, el 85 % del alto). */
    Bestia medidas(float ancho, float alto, float ojos) {
        this.ancho = ancho;
        this.alto = alto;
        this.ojos = ojos;
        return this;
    }

    Bestia rastreo(int chunks) {
        this.rastreo = chunks;
        return this;
    }

    Bestia inmuneFuego() {
        this.inmuneFuego = true;
        return this;
    }

    Bestia atributos(Supplier<AttributeSupplier.Builder> atributos) {
        this.atributos = atributos;
        return this;
    }

    Bestia categoria(MobCategory categoria) {
        this.categoriaMob = categoria;
        return this;
    }

    /** Sus sonidos ademas de ambiente, herido, muerte y paso. */
    Bestia sonidos(String... nombres) {
        for (String n : nombres) {
            if (!sonidos.contains(n)) {
                sonidos.add(n);
            }
        }
        return this;
    }

    /** Quita uno de los sonidos de siempre (un mob que no hace ruido al andar, por ejemplo). */
    Bestia sinSonido(String nombre) {
        sonidos.remove(nombre);
        return this;
    }

    Bestia particula(String nombre, Vuelo vuelo, boolean luz) {
        particulas.put(nombre, new Particula(nombre, vuelo, luz));
        return this;
    }

    /** Lo que dura su muerte y la particula en la que se deshace al acabar. */
    Bestia muerte(int ticks, @Nullable String particula) {
        this.muerteTicks = ticks;
        this.particulaMuerte = particula;
        return this;
    }

    Bestia sombra(float radio) {
        this.sombra = radio;
        return this;
    }

    /** Donde aparece solo, con que peso (el zombi tiene 100) y en grupos de cuantos. */
    Bestia aparece(Predicate<BiomeSelectionContext> biomas, int peso, int minimo, int maximo) {
        this.biomas = biomas;
        this.peso = peso;
        this.minimo = minimo;
        this.maximo = maximo;
        return this;
    }

    Bestia colocacion(SpawnPlacementType colocacion, Heightmap.Types altura) {
        this.colocacion = colocacion;
        this.altura = altura;
        return this;
    }

    Bestia regla(Regla regla) {
        this.regla = regla;
        return this;
    }

    // ------------------------------------------------------------------
    //  Lo que se pregunta
    // ------------------------------------------------------------------

    @Override
    public String id() {
        return id;
    }

    @Override
    public String titulo() {
        return titulo;
    }

    @Override
    public String texto() {
        return texto;
    }

    @Override
    public Categoria categoria() {
        return Categoria.MOB;
    }

    @Override
    public String etiquetas() {
        return etiquetas;
    }

    @Override
    public String grupo() {
        return grupo;
    }

    /** Uno de sus sonidos, o null si no lo tiene. */
    public @Nullable SoundEvent sonido(String nombre) {
        return eventos.get(nombre);
    }

    /** Una de sus particulas (registrada), o null si no la tiene. */
    public @Nullable SimpleParticleType particula(String nombre) {
        return tiposParticula.get(nombre);
    }

    public Map<String, Particula> particulas() {
        return particulas;
    }

    public float ancho() {
        return ancho;
    }

    public float alto() {
        return alto;
    }
}
