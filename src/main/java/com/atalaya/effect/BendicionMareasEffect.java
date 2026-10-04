package com.atalaya.effect;

import com.atalaya.Atalaya;
import com.atalaya.particula.AtalayaParticulas;
import net.minecraft.core.Holder;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.ResourceKey;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.effect.MobEffect;
import net.minecraft.world.effect.MobEffectCategory;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;

/**
 * Bendicion de las mareas: lo que Nerea deja, liberado, a todo el grupo que
 * estuvo en la pelea.
 *
 * Bajo el agua no te ahogas y nadas como en tierra. Va con icono y particula
 * propios (la burbuja de Nerea), no con los efectos de vanilla de respiracion
 * y gracia del delfin.
 */
public class BendicionMareasEffect extends MobEffect {

    private static final int COLOR = 0x3FE0CC;

    public static final ResourceKey<MobEffect> CLAVE = ResourceKey.create(
            Registries.MOB_EFFECT,
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "bendicion_mareas"));

    public static Holder<MobEffect> BENDICION;

    protected BendicionMareasEffect() {
        super(MobEffectCategory.BENEFICIAL, COLOR, AtalayaParticulas.NEREA_BURBUJA);
        // Como Agilidad acuatica III: bajo el agua andas como fuera.
        addAttributeModifier(Attributes.WATER_MOVEMENT_EFFICIENCY,
                Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "effect.bendicion_mareas.nado"),
                1.0, AttributeModifier.Operation.ADD_VALUE);
        // Y picas bajo el agua tan rapido como en tierra.
        addAttributeModifier(Attributes.SUBMERGED_MINING_SPEED,
                Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "effect.bendicion_mareas.minar"),
                0.8, AttributeModifier.Operation.ADD_VALUE);
    }

    public static void registrar() {
        BENDICION = Registry.registerForHolder(BuiltInRegistries.MOB_EFFECT, CLAVE, new BendicionMareasEffect());
    }

    @Override
    public boolean shouldApplyEffectTickThisTick(int duracion, int amplificador) {
        return duracion % 10 == 0;
    }

    /** El aire no baja: se rellena cada medio segundo. */
    @Override
    public boolean applyEffectTick(ServerLevel nivel, LivingEntity entidad, int amplificador) {
        if (entidad.getAirSupply() < entidad.getMaxAirSupply()) {
            entidad.setAirSupply(entidad.getMaxAirSupply());
        }
        return true;
    }
}
