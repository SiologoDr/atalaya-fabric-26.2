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
 * Los tipos de dano de Rajang. Como los de Nerea y Aeralis, en
 * data/atalaya/damage_type con "scaling": "never" (los numeros son los de la
 * ficha) y todos en no_knockback: el empujon lo da cada ataque a su manera.
 *
 * <pre>
 *   garra       Los picos de la Garra Terrestre: el escudo los para de frente
 *   terremoto   Los pilares del Terremoto Ancestral
 *   salto       La caida del salto de la fase IV
 *   rugido      El Rugido de Jade (el Sello fallido): ni armadura ni escudo
 *   fragmento   Un fragmento del Cataclismo dentro de su marca: la muerte (ni
 *               armadura, ni escudo, ni encantamientos, ni Resistencia; el
 *               totem de la inmortalidad si vale). Fuera de la marca no pega
 *   embestida   Su cuerpo a la carrera y los pinchos de la Embestida: la muerte,
 *               como el fragmento (solo salva un totem)
 *   raiz        La Tumba de Raices llena: la muerte, igual
 *   pulso       El pulso de tierra de un totem del Sello roto
 * </pre>
 */
public final class RajangDanos {

    public static final ResourceKey<DamageType> GARRA = clave("rajang_garra");
    public static final ResourceKey<DamageType> TERREMOTO = clave("rajang_terremoto");
    public static final ResourceKey<DamageType> SALTO = clave("rajang_salto");
    public static final ResourceKey<DamageType> RUGIDO = clave("rajang_rugido");
    public static final ResourceKey<DamageType> FRAGMENTO = clave("rajang_fragmento");
    public static final ResourceKey<DamageType> EMBESTIDA = clave("rajang_embestida");
    public static final ResourceKey<DamageType> RAIZ = clave("rajang_raiz");
    public static final ResourceKey<DamageType> PULSO = clave("rajang_pulso");

    private RajangDanos() {
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
