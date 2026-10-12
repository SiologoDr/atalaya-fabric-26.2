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
 * Los tipos de dano de los mini jefes, uno por ataque. Como los de los jefes, en
 * data/atalaya/damage_type con "scaling": "never" (los numeros son los de la
 * ficha) y todos en no_knockback: el empujon lo da cada ataque a su manera.
 */
public final class MiniJefeDanos {

    // Moctezuma, el Guerrero Aguila de Jade
    public static final ResourceKey<DamageType> MOCTEZUMA_CORTE = clave("moctezuma_corte");
    public static final ResourceKey<DamageType> MOCTEZUMA_TERREMOTO = clave("moctezuma_terremoto");
    public static final ResourceKey<DamageType> MOCTEZUMA_TORMENTA = clave("moctezuma_tormenta");
    // Yiatzo, el Mago del Viento
    public static final ResourceKey<DamageType> YIATZO_RAFAGA = clave("yiatzo_rafaga");
    public static final ResourceKey<DamageType> YIATZO_TORMENTA = clave("yiatzo_tormenta");
    public static final ResourceKey<DamageType> YIATZO_CICLON = clave("yiatzo_ciclon");
    // Atlahua, el Triton de las Profundidades
    public static final ResourceKey<DamageType> ATLAHUA_ESTOCADA = clave("atlahua_estocada");
    public static final ResourceKey<DamageType> ATLAHUA_OLAS = clave("atlahua_olas");
    public static final ResourceKey<DamageType> ATLAHUA_TSUNAMI = clave("atlahua_tsunami");
    // Xiuhquetzal, el Fenix de Llamas
    public static final ResourceKey<DamageType> XIUHQUETZAL_PICOTAZO = clave("xiuhquetzal_picotazo");
    public static final ResourceKey<DamageType> XIUHQUETZAL_PLUMAS = clave("xiuhquetzal_plumas");
    public static final ResourceKey<DamageType> XIUHQUETZAL_LLAMARADA = clave("xiuhquetzal_llamarada");

    private MiniJefeDanos() {
    }

    private static ResourceKey<DamageType> clave(String nombre) {
        return ResourceKey.create(Registries.DAMAGE_TYPE, Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, nombre));
    }

    public static DamageSource fuente(Level nivel, ResourceKey<DamageType> tipo, @Nullable Entity directo, @Nullable Entity causante) {
        return new DamageSource(nivel.registryAccess().lookupOrThrow(Registries.DAMAGE_TYPE).getOrThrow(tipo), directo, causante);
    }
}
