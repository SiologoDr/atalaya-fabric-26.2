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
 * Enraizado: lo que dejan las plantas del bestiario (la Trampa Verde que te atrapa los pies, el Zombi Planta que te
 * clava al suelo de un golpe). No te puedes mover ni saltar, pero si pegar y usar objetos, como la Paralisis; lo que
 * sale a tu alrededor son astillas de raiz (la particula del Zombi Planta), no los rayos de Aeralis.
 */
public class EnraizadoEffect extends MobEffect {

    /** El pardo verdoso de la raiz con brote. */
    private static final int COLOR = 0x6A8A34;

    public static final ResourceKey<MobEffect> CLAVE = ResourceKey.create(
            Registries.MOB_EFFECT,
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "enraizado"));

    public static Holder<MobEffect> ENRAIZADO;

    protected EnraizadoEffect() {
        super(MobEffectCategory.HARMFUL, COLOR, Fichas.ZOMBI_PLANTA.particula("raiz"));
        addAttributeModifier(Attributes.MOVEMENT_SPEED,
                Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "effect.enraizado.quieto"),
                -1.0, AttributeModifier.Operation.ADD_MULTIPLIED_TOTAL);
        addAttributeModifier(Attributes.JUMP_STRENGTH,
                Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "effect.enraizado.salto"),
                -1.0, AttributeModifier.Operation.ADD_MULTIPLIED_TOTAL);
    }

    /** Despues de las bestias (usa una de sus particulas). */
    public static void registrar() {
        ENRAIZADO = Registry.registerForHolder(BuiltInRegistries.MOB_EFFECT, CLAVE, new EnraizadoEffect());
    }
}
