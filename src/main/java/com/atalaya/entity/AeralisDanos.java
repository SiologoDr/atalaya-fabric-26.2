package com.atalaya.entity;

import com.atalaya.Atalaya;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.damagesource.DamageType;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.level.Level;
import org.jspecify.annotations.Nullable;

/**
 * Los tipos de dano de Aeralis. Como los de Nerea, en data/atalaya/damage_type
 * con "scaling": "never" (los numeros son los del boceto, sin el x1,5 de
 * Dificil) y todos en no_knockback: el empujon lo da cada ataque a su manera.
 *
 * <pre>
 *   cuchilla   Aleteo Cortante: el escudo la para de frente
 *   tornado    Atrapado en un tornado, 4 por segundo: el viento y la arena
 *              pasan por la armadura (ni armadura ni escudo)
 *   estallido  El tornado que revienta: cuenta como explosion
 *   rafaga     Las rafagas de la Caceria: explosion de presion
 *   juicio     El golpe del Juicio del Ciclon: ni armadura ni escudo
 * </pre>
 */
public final class AeralisDanos {

    public static final ResourceKey<DamageType> CUCHILLA = clave("aeralis_cuchilla");
    public static final ResourceKey<DamageType> TORNADO = clave("aeralis_tornado");
    public static final ResourceKey<DamageType> ESTALLIDO = clave("aeralis_estallido");
    public static final ResourceKey<DamageType> RAFAGA = clave("aeralis_rafaga");
    public static final ResourceKey<DamageType> JUICIO = clave("aeralis_juicio");

    private AeralisDanos() {
    }

    private static ResourceKey<DamageType> clave(String nombre) {
        return ResourceKey.create(Registries.DAMAGE_TYPE, Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, nombre));
    }

    public static DamageSource fuente(Level nivel, ResourceKey<DamageType> tipo,
                                      @Nullable Entity directo, @Nullable Entity causante) {
        return new DamageSource(nivel.registryAccess().lookupOrThrow(Registries.DAMAGE_TYPE).getOrThrow(tipo),
                directo, causante);
    }
}
