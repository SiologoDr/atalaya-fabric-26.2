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
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;

/**
 * Peso de la Tierra: lo que deja el Terremoto Ancestral de Rajang a todos los
 * que pisan su templo. La tierra tira de ti: andas un 35 % mas despacio y
 * saltas la mitad. Con modificadores propios y su particula (el polvo de
 * Rajang), nada de la Lentitud de vanilla.
 */
public class PesoTierraEffect extends MobEffect {

    private static final int COLOR = 0xB08850;

    public static final ResourceKey<MobEffect> CLAVE = ResourceKey.create(
            Registries.MOB_EFFECT,
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "peso_tierra"));

    public static Holder<MobEffect> PESO;

    protected PesoTierraEffect() {
        super(MobEffectCategory.HARMFUL, COLOR, AtalayaParticulas.RAJANG_POLVO);
        addAttributeModifier(Attributes.MOVEMENT_SPEED,
                Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "effect.peso_tierra.lento"),
                -0.35, AttributeModifier.Operation.ADD_MULTIPLIED_TOTAL);
        addAttributeModifier(Attributes.JUMP_STRENGTH,
                Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "effect.peso_tierra.salto"),
                -0.5, AttributeModifier.Operation.ADD_MULTIPLIED_TOTAL);
    }

    public static void registrar() {
        PESO = Registry.registerForHolder(BuiltInRegistries.MOB_EFFECT, CLAVE, new PesoTierraEffect());
    }
}
