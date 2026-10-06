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
 * Bendicion del Sol: lo que Novilis deja, liberado, a todo el grupo que estuvo
 * en la pelea. El sol te da fuerza: +3 de dano de ataque, y el fuego no te
 * prende (se te apaga en cuanto te toca, y la lava solo quema lo de siempre).
 * Con modificadores del propio efecto y la luz dorada de Novilis.
 */
public class BendicionSolEffect extends MobEffect {

    private static final int COLOR = 0xFFC23A;

    public static final ResourceKey<MobEffect> CLAVE = ResourceKey.create(
            Registries.MOB_EFFECT,
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "bendicion_sol"));

    public static Holder<MobEffect> BENDICION;

    protected BendicionSolEffect() {
        super(MobEffectCategory.BENEFICIAL, COLOR, AtalayaParticulas.NOVILIS_LUZ);
        addAttributeModifier(Attributes.ATTACK_DAMAGE,
                Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "effect.bendicion_sol.fuerza"),
                3.0, AttributeModifier.Operation.ADD_VALUE);
    }

    public static void registrar() {
        BENDICION = Registry.registerForHolder(BuiltInRegistries.MOB_EFFECT, CLAVE, new BendicionSolEffect());
    }

    @Override
    public boolean shouldApplyEffectTickThisTick(int duracion, int amplificador) {
        return true;
    }

    @Override
    public boolean applyEffectTick(ServerLevel nivel, LivingEntity v, int amplificador) {
        if (v.getRemainingFireTicks() > 0) {
            v.clearFire();
        }
        return true;
    }
}
