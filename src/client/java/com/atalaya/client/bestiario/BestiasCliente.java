package com.atalaya.client.bestiario;

import com.atalaya.bestiario.Bestia;
import com.atalaya.bestiario.BestiaEntity;
import com.atalaya.bestiario.Bestias;
import net.fabricmc.fabric.api.client.particle.v1.ParticleProviderRegistry;
import net.fabricmc.fabric.api.client.rendering.v1.EntityRendererRegistry;
import net.fabricmc.fabric.api.client.rendering.v1.ModelLayerRegistry;
import net.minecraft.client.renderer.entity.EntityRenderer;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.core.particles.SimpleParticleType;
import net.minecraft.world.entity.EntityType;

import java.util.HashMap;
import java.util.Map;
import java.util.function.BiFunction;

/**
 * Los mobs del bestiario en el cliente: la malla de cada uno (de su json), su render (el de todos, BestiaRenderer, o el
 * suyo si lo tiene) y sus particulas.
 */
public final class BestiasCliente {

    /** Los que se pintan con un render propio (lo que hacen mas alla de la malla: un aviso encima, un rayo...). */
    private static final Map<String, BiFunction<EntityRendererProvider.Context, Bestia, EntityRenderer<?, ?>>> PROPIOS =
            new HashMap<>();

    private BestiasCliente() {
    }

    /** Un render propio para ese mob (antes de registrar). */
    public static void propio(String id, BiFunction<EntityRendererProvider.Context, Bestia, EntityRenderer<?, ?>> render) {
        PROPIOS.put(id, render);
    }

    @SuppressWarnings({"unchecked", "rawtypes"})
    public static void registrar() {
        BestiasEfectos.registrar();
        // Lo que ponen en la pantalla (la estatica, la nata, las lianas).
        PantallasBestias.registrar();
        for (Bestia b : Bestias.todas()) {
            ModelLayerRegistry.registerModelLayer(BestiaRenderer.capa(b.id()), () -> BestiaDatos.de(b.id()).capa);
            BiFunction<EntityRendererProvider.Context, Bestia, EntityRenderer<?, ?>> propio = PROPIOS.get(b.id());
            EntityType<BestiaEntity> tipo = (EntityType<BestiaEntity>) b.tipo;
            if (propio != null) {
                EntityRendererRegistry.register(tipo, (EntityRendererProvider) ctx -> propio.apply(ctx, b));
            } else {
                EntityRendererRegistry.register(tipo, ctx -> new BestiaRenderer<>(ctx, b));
            }
            for (Bestia.Particula p : b.particulas().values()) {
                SimpleParticleType t = b.particula(p.nombre());
                if (t != null) {
                    ParticleProviderRegistry.getInstance().register(t,
                            sprites -> new BestiaParticula.Fabrica(sprites, p.vuelo(), p.luz()));
                }
            }
        }
        // Las sueltas (las del Limbo), igual que las de los mobs.
        for (Bestias.Suelta su : Bestias.sueltas()) {
            ParticleProviderRegistry.getInstance().register(su.tipo(),
                    sprites -> new BestiaParticula.Fabrica(sprites, su.vuelo(), su.luz()));
        }
    }
}
