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
 * Bendicion de la tierra: lo que Rajang deja, liberado, a todo el grupo que
 * estuvo en la pelea. La piedra del templo te cubre: +6 de armadura y +3 de
 * dureza, y nada te empuja (resistencia al empuje total). Con modificadores
 * del propio efecto y la particula de oro de Rajang.
 */
public class BendicionTierraEffect extends MobEffect {

    private static final int COLOR = 0x7CD08A;

    public static final ResourceKey<MobEffect> CLAVE = ResourceKey.create(
            Registries.MOB_EFFECT,
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "bendicion_tierra"));

    public static Holder<MobEffect> BENDICION;

    protected BendicionTierraEffect() {
        super(MobEffectCategory.BENEFICIAL, COLOR, AtalayaParticulas.RAJANG_ORO);
        addAttributeModifier(Attributes.ARMOR,
                Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "effect.bendicion_tierra.armadura"),
                6.0, AttributeModifier.Operation.ADD_VALUE);
        addAttributeModifier(Attributes.ARMOR_TOUGHNESS,
                Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "effect.bendicion_tierra.dureza"),
                3.0, AttributeModifier.Operation.ADD_VALUE);
        addAttributeModifier(Attributes.KNOCKBACK_RESISTANCE,
                Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "effect.bendicion_tierra.firme"),
                1.0, AttributeModifier.Operation.ADD_VALUE);
    }

    public static void registrar() {
        BENDICION = Registry.registerForHolder(BuiltInRegistries.MOB_EFFECT, CLAVE, new BendicionTierraEffect());
    }
}
