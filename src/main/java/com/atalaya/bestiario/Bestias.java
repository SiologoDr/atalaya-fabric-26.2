package com.atalaya.bestiario;

import com.atalaya.entity.AtalayaEntities;
import com.atalaya.item.AtalayaItems;
import com.atalaya.mixin.SpawnPlacementsInvoker;
import com.atalaya.particula.AtalayaParticulas;
import com.atalaya.sonido.AtalayaSonidos;
import net.fabricmc.fabric.api.biome.v1.BiomeModifications;
import net.fabricmc.fabric.api.object.builder.v1.entity.FabricDefaultAttributeRegistry;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.entity.EntitySpawnReason;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.SpawnEggItem;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

/**
 * Los mobs del bestiario, en el orden del menu de los mobs (/atalaya menu mobs). Cada uno con su ficha (Bestia): su
 * titulo y lo que hace (el menu y el aviso del chat), su caja, sus atributos, sus sonidos, sus particulas y donde
 * aparece cuando esta suelto.
 *
 * Todos son nuestros: la mecanica de los mobs del DEDsafio 2, 3 y 4 (materiales/ideas), con otro diseno, otro nombre y
 * otro texto.
 */
public final class Bestias {

    private static final List<Bestia> TODAS = new ArrayList<>();
    private static final List<Bestia> VISTA = Collections.unmodifiableList(TODAS);

    private Bestias() {
    }

    static Bestia nueva(String id, EntityType.EntityFactory<? extends BestiaEntity> fabrica) {
        Bestia b = new Bestia(id, fabrica);
        TODAS.add(b);
        return b;
    }

    public static List<Bestia> todas() {
        return VISTA;
    }

    public static Bestia porId(String id) {
        for (Bestia b : TODAS) {
            if (b.id().equals(id)) {
                return b;
            }
        }
        return null;
    }

    // ------------------------------------------------------------------
    //  El registro
    // ------------------------------------------------------------------

    /** Sus tipos, atributos, sonidos, particulas y apariciones: antes que los items (los huevos los necesitan). */
    public static void registrar() {
        Fichas.cargar();
        for (Bestia b : TODAS) {
            registrarTipo(b);
        }
        Fichas.eventos();
    }

    /** Una particula que no es de ningun mob (las del Limbo): su tipo, como se mueve y si brilla. */
    public record Suelta(net.minecraft.core.particles.SimpleParticleType tipo, Bestia.Vuelo vuelo, boolean luz) {
    }

    private static final List<Suelta> SUELTAS = new java.util.ArrayList<>();

    /** Registra una particula suelta (atalaya:nombre; sus sprites, de un generador como los de los mobs). */
    public static net.minecraft.core.particles.SimpleParticleType particulaSuelta(String nombre, Bestia.Vuelo vuelo,
                                                                                  boolean luz) {
        net.minecraft.core.particles.SimpleParticleType t = AtalayaParticulas.registrar(nombre, false);
        SUELTAS.add(new Suelta(t, vuelo, luz));
        return t;
    }

    public static List<Suelta> sueltas() {
        return SUELTAS;
    }

    /** Sus huevos: despues de los tipos. */
    public static void registrarHuevos() {
        for (Bestia b : TODAS) {
            EntityType<? extends BestiaEntity> tipo = b.tipo;
            b.huevo = AtalayaItems.registrar("huevo_" + b.id(), props -> new SpawnEggItem(props.spawnEgg(tipo)));
        }
    }

    /** Los huevos de todos, en orden (para la pestana del mod en creativo). */
    public static Item[] huevos() {
        Item[] out = new Item[TODAS.size()];
        for (int i = 0; i < out.length; i++) {
            out[i] = TODAS.get(i).huevo;
        }
        return out;
    }

    @SuppressWarnings({"unchecked", "rawtypes"})
    private static void registrarTipo(Bestia b) {
        ResourceKey<EntityType<?>> clave = AtalayaEntities.clave(b.id());
        EntityType.Builder<BestiaEntity> constructor = EntityType.Builder
                .of((EntityType.EntityFactory<BestiaEntity>) b.fabrica, b.categoriaMob)
                .sized(b.ancho, b.alto)
                .clientTrackingRange(b.rastreo);
        if (b.ojos > 0.0F) {
            constructor = constructor.eyeHeight(b.ojos);
        }
        if (b.inmuneFuego) {
            constructor = constructor.fireImmune();
        }
        EntityType<BestiaEntity> tipo = Registry.register(BuiltInRegistries.ENTITY_TYPE, clave, constructor.build(clave));
        b.tipo = tipo;
        FabricDefaultAttributeRegistry.register(tipo, b.atributos.get());
        for (String n : b.sonidos) {
            b.eventos.put(n, AtalayaSonidos.registrar("bestia." + b.id() + "." + n));
        }
        for (Bestia.Particula p : b.particulas.values()) {
            b.tiposParticula.put(p.nombre(), AtalayaParticulas.registrar("bestia_" + b.id() + "_" + p.nombre(), false));
        }
        // Donde aparece solo. El bioma se apunta para siempre al cargar; lo que se mira cada vez que el juego se plantea
        // sacar uno es la regla de abajo, y ahi esta el interruptor del menu: apagado, no sale (los huevos, los
        // generadores y los comandos lo sacan siempre).
        if (b.biomas != null && b.peso > 0) {
            BiomeModifications.addSpawn(b.biomas, b.categoriaMob, tipo, b.peso, b.minimo, b.maximo);
        }
        SpawnPlacementsInvoker.atalaya$registrar((EntityType) tipo, b.colocacion, b.altura,
                (t, nivel, motivo, pos, azar) -> (motivo != EntitySpawnReason.NATURAL
                        && motivo != EntitySpawnReason.CHUNK_GENERATION
                        || Bestiario.suelto(nivel.getLevel().getServer(), b))
                        && b.regla.puede((EntityType<?>) t, nivel, motivo, pos, azar));
    }
}
