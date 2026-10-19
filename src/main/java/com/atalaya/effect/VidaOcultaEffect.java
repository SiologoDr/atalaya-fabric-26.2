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
 * Vida oculta (el momento EL INTERCAMBIO; en DEDsafio 4, «hasta que termine el contador no podran ver su vida»): no se
 * ven los corazones. No hace nada en el servidor: los esconde el cliente (CambiosCliente) mientras se lleva.
 */
public class VidaOcultaEffect extends MobEffect {

    public static final ResourceKey<MobEffect> CLAVE = ResourceKey.create(Registries.MOB_EFFECT,
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "vida_oculta"));

    public static Holder<MobEffect> VIDA_OCULTA;

    protected VidaOcultaEffect() {
        super(MobEffectCategory.HARMFUL, 0x6A1A2A);
    }

    public static void registrar() {
        VIDA_OCULTA = Registry.registerForHolder(BuiltInRegistries.MOB_EFFECT, CLAVE, new VidaOcultaEffect());
    }
}
