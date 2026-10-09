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
 * Los tipos de dano de Nerea. Viven en data/atalaya/damage_type, con
 * "scaling": "never": en hardcore la dificultad es Dificil y vanilla
 * multiplicaria por 1,5 todo lo que pega un monstruo. Asi los numeros son los
 * del boceto y se ajustan aqui, no adivinando el multiplicador.
 *
 * <pre>
 *   ola       Rompeolas: la ola y el tridente al caer
 *   cadena    Molino: no lo para el escudo (tag bypasses_shield)
 *   burbuja   Burbujas bomba: cuenta como explosion (la Proteccion contra
 *             explosiones sirve)
 *   mirada    Mirada del Abismo: magica, ni escudo ni armadura
 *   tridente  La estocada del Arpon: esta si la para el escudo
 *   remolino  El Remolino, 10 por segundo: te ahoga, no hay armadura ni
 *             escudo que valga (solo la antorcha, que te saca de el)
 *   geiser    El Geiser del Abismo: te lanza al cielo desde abajo (el escudo
 *             no sirve)
 *   marea     La Gran Marea: la pared de agua que cruza la arena. Mata como
 *             la Mirada: solo salva un totem (todas las bypasses_* menos la de
 *             invulnerabilidad)
 *   canto     El Canto de Sirena, cada segundo de trance: pasa armadura y
 *             escudo, sin empujon
 *   marea_alta  La Marea Alta: a quien no este en una burbuja de refugio.
 *             Mata como la Gran Marea
 * </pre>
 */
public final class NereaDanos {

    public static final ResourceKey<DamageType> OLA = clave("nerea_ola");
    public static final ResourceKey<DamageType> CADENA = clave("nerea_cadena");
    public static final ResourceKey<DamageType> BURBUJA = clave("nerea_burbuja");
    public static final ResourceKey<DamageType> MIRADA = clave("nerea_mirada");
    public static final ResourceKey<DamageType> TRIDENTE = clave("nerea_tridente");
    public static final ResourceKey<DamageType> REMOLINO = clave("nerea_remolino");
    public static final ResourceKey<DamageType> GEISER = clave("nerea_geiser");
    public static final ResourceKey<DamageType> MAREA = clave("nerea_marea");
    public static final ResourceKey<DamageType> CANTO = clave("nerea_canto");
    public static final ResourceKey<DamageType> MAREA_ALTA = clave("nerea_marea_alta");
    /** Perder el Duelo de Canto: mata, salvo totem (pasa la armadura, la resistencia y el escudo). */
    public static final ResourceKey<DamageType> DUELO = clave("nerea_duelo");
    /** El mordisco de una morena (las Morenas de las Pozas y la Pesca del Abismo): pasa la armadura. */
    public static final ResourceKey<DamageType> MORENA = clave("nerea_morena");

    private NereaDanos() {
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
