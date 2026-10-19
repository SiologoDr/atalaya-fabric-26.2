package com.atalaya.effect;

import com.atalaya.Atalaya;
import com.atalaya.bestiario.Fichas;
import net.minecraft.core.Holder;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.effect.MobEffect;
import net.minecraft.world.effect.MobEffectCategory;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;

/**
 * Congelado: el mordisco de la Fauces de Escarcha. Te quedas clavado (sin moverte ni saltar) y, mientras dura, la
 * escarcha te cubre los bordes de la pantalla (PantallasBestias, con su textura propia: nada de la nieve polvo de
 * vanilla). Alrededor, copos de escarcha (la particula de la Fauces).
 *
 * No toca el frio de Atalaya (FrioManager): es un golpe, no la temperatura del sitio.
 */
public class CongeladoEffect extends MobEffect {

    /** Celeste de hielo. */
    private static final int COLOR = 0x8EE2F6;

    public static final ResourceKey<MobEffect> CLAVE = ResourceKey.create(
            Registries.MOB_EFFECT,
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "congelado"));

    public static Holder<MobEffect> CONGELADO;

    protected CongeladoEffect() {
        super(MobEffectCategory.HARMFUL, COLOR, Fichas.FAUCES_ESCARCHA.particula("escarcha"));
        addAttributeModifier(Attributes.MOVEMENT_SPEED,
                Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "effect.congelado.quieto"),
                -1.0, AttributeModifier.Operation.ADD_MULTIPLIED_TOTAL);
        addAttributeModifier(Attributes.JUMP_STRENGTH,
                Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "effect.congelado.salto"),
                -1.0, AttributeModifier.Operation.ADD_MULTIPLIED_TOTAL);
    }

    /** Despues de las bestias (usa una de sus particulas). */
    public static void registrar() {
        CONGELADO = Registry.registerForHolder(BuiltInRegistries.MOB_EFFECT, CLAVE, new CongeladoEffect());
    }
}
