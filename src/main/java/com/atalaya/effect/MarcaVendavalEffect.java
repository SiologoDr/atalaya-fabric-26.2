package com.atalaya.effect;

import com.atalaya.Atalaya;
import com.atalaya.particula.AtalayaParticulas;
import net.minecraft.core.Holder;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.effect.MobEffect;
import net.minecraft.world.effect.MobEffectCategory;

/**
 * Marca del Vendaval: la presa de La Caceria. Mientras la lleva, Aeralis solo
 * ataca a ese jugador y le lanza rafagas una tras otra.
 *
 * El efecto en si no hace dano ni frena: es la senal (icono propio y las
 * runas de viento azules que le giran alrededor). No se puede quitar: si la
 * leche o un comando la borran, Aeralis se la vuelve a poner mientras dura la
 * caza (AeralisEntity).
 */
public class MarcaVendavalEffect extends MobEffect {

    /** El cian de los ojos de Aeralis, el del icono. */
    private static final int COLOR = 0x5FD2FF;

    public static final ResourceKey<MobEffect> CLAVE = ResourceKey.create(
            Registries.MOB_EFFECT,
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "marca_vendaval"));

    public static Holder<MobEffect> MARCA;

    protected MarcaVendavalEffect() {
        super(MobEffectCategory.HARMFUL, COLOR, AtalayaParticulas.AERALIS_MARCA);
    }

    public static void registrar() {
        MARCA = Registry.registerForHolder(BuiltInRegistries.MOB_EFFECT, CLAVE, new MarcaVendavalEffect());
    }
}
