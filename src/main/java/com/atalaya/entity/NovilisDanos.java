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
 * Los tipos de dano de Novilis. Viven en data/atalaya/damage_type, con
 * "scaling": "never", como los de los otros jefes. Ninguno cuenta como fuego
 * de vanilla (is_fire): una pocion de resistencia al fuego no basta contra el
 * sol.
 *
 * <pre>
 *   hoja       Barrido de fuego: la hoja de cerca. La para el escudo
 *   tajo       Barrido de fuego: la media luna que vuela. La para el escudo
 *   rayo       Castigo solar: el rayo que cae del cielo (sin escudo)
 *   onda       Castigo solar: la onda de fuego por el suelo (sin escudo; se salta)
 *   sol        Sol x3: la explosion de fuego y lava (cuenta como explosion)
 *   supernova  el cuarto sol del Sol Abrasador, el grande (explosion, sin escudo)
 *   embestida  Espada del Fuego: su cuerpo y la hoja a la carrera (sin escudo)
 *   llamas     el camino de llamas malditas y las bocas del Mar de Llamas: arde
 *              mientras se pisa (no empuja; la armadura cuenta)
 *   infernal   Furia Infernal: la caida, los chorros de la grieta y la explosion
 *              (explosion, sin escudo)
 *   dios       Dios de la Guerra: las explosiones en cadena (explosion, sin escudo)
 *   calor      lo que quema estar en sus manos en la Ofrenda: pasa la armadura
 *   abrasa     el sol de la Sombra del Escudo, cada segundo al sol: pasa la armadura
 *              y el escudo y no empuja (lo que vale es la sombra de la Egida)
 *   mortal     lo que mata salvo totem: la Ofrenda fallada y el Dios de la Guerra
 *              contra quien tiene quemadura grave
 *              (todas las bypasses_* menos la de invulnerabilidad)
 * </pre>
 */
public final class NovilisDanos {

    public static final ResourceKey<DamageType> HOJA = clave("novilis_hoja");
    public static final ResourceKey<DamageType> TAJO = clave("novilis_tajo");
    public static final ResourceKey<DamageType> RAYO = clave("novilis_rayo");
    public static final ResourceKey<DamageType> ONDA = clave("novilis_onda");
    public static final ResourceKey<DamageType> SOL = clave("novilis_sol");
    public static final ResourceKey<DamageType> SUPERNOVA = clave("novilis_supernova");
    public static final ResourceKey<DamageType> DIOS = clave("novilis_dios");
    public static final ResourceKey<DamageType> CALOR = clave("novilis_calor");
    public static final ResourceKey<DamageType> ABRASA = clave("novilis_abrasa");
    public static final ResourceKey<DamageType> MORTAL = clave("novilis_mortal");
    public static final ResourceKey<DamageType> EMBESTIDA = clave("novilis_embestida");
    public static final ResourceKey<DamageType> LLAMAS = clave("novilis_llamas");
    public static final ResourceKey<DamageType> INFERNAL = clave("novilis_infernal");

    private NovilisDanos() {
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
