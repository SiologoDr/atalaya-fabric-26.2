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
 * Bendicion de los vientos: lo que Aeralis deja, liberada, a todo el grupo que
 * estuvo en la pelea.
 *
 * El viento te lleva: corres un 20 % mas, pesas menos (caes despacio, saltas
 * algo mas) y las caidas de hasta 10 bloques no hacen dano. Con modificadores
 * del propio efecto y particula propia (la mota de cielo de Aeralis), nada de
 * Velocidad ni Caida lenta de vanilla.
 */
public class BendicionVientosEffect extends MobEffect {

    private static final int COLOR = 0xCFEEFF;

    public static final ResourceKey<MobEffect> CLAVE = ResourceKey.create(
            Registries.MOB_EFFECT,
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "bendicion_vientos"));

    public static Holder<MobEffect> BENDICION;

    protected BendicionVientosEffect() {
        super(MobEffectCategory.BENEFICIAL, COLOR, AtalayaParticulas.AERALIS_LUZ);
        addAttributeModifier(Attributes.MOVEMENT_SPEED,
                Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "effect.bendicion_vientos.velocidad"),
                0.20, AttributeModifier.Operation.ADD_MULTIPLIED_TOTAL);
        addAttributeModifier(Attributes.GRAVITY,
                Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "effect.bendicion_vientos.ligereza"),
                -0.35, AttributeModifier.Operation.ADD_MULTIPLIED_TOTAL);
        addAttributeModifier(Attributes.SAFE_FALL_DISTANCE,
                Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "effect.bendicion_vientos.caida"),
                7.0, AttributeModifier.Operation.ADD_VALUE);
    }

    public static void registrar() {
        BENDICION = Registry.registerForHolder(BuiltInRegistries.MOB_EFFECT, CLAVE, new BendicionVientosEffect());
    }
}
