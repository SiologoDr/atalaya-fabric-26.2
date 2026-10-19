package com.atalaya.effect;

import com.atalaya.Atalaya;
import net.minecraft.core.Holder;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.effect.MobEffect;
import net.minecraft.world.effect.MobEffectCategory;

/**
 * Deslumbrado (el cambio NO MIRES AL SOL; en DEDsafio 4, la miopia y el daltonismo de mirar al Sol): la vista nublada,
 * sin colores y sin ver la vida. No hace nada en el servidor: lo que se ve lo pone el cliente (CambiosCliente) mientras
 * el jugador lo lleva.
 */
public class DeslumbradoEffect extends MobEffect {

    public static final ResourceKey<MobEffect> CLAVE = ResourceKey.create(Registries.MOB_EFFECT,
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "deslumbrado"));

    public static Holder<MobEffect> DESLUMBRADO;

    protected DeslumbradoEffect() {
        super(MobEffectCategory.HARMFUL, 0xFFE27A);
    }

    public static void registrar() {
        DESLUMBRADO = Registry.registerForHolder(BuiltInRegistries.MOB_EFFECT, CLAVE, new DeslumbradoEffect());
    }
}
