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
 * Corriente Abismal: el agua del fondo de Nerea. Te la deja su Remolino al
 * arrastrarte y su Arpon al engancharte: el agua sigue tirando de las piernas
 * un rato despues, y cuesta alejarse de ella.
 *
 * Frena un 20 % por nivel (I, II, III), con el modificador del propio efecto,
 * que se retira solo al acabar. Icono propio y su propia particula (las gotas
 * de Nerea que te chorrean), nada de la Lentitud de vanilla.
 */
public class CorrienteAbismalEffect extends MobEffect {

    /** Azul de fondo marino, el del icono. */
    private static final int COLOR = 0x1B4F7A;

    /** Fraccion de velocidad que resta por nivel (ADD_MULTIPLIED_TOTAL, se multiplica por el nivel). */
    private static final double LENTITUD = -0.20;

    public static final ResourceKey<MobEffect> CLAVE = ResourceKey.create(
            Registries.MOB_EFFECT,
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "corriente_abismal"));

    public static Holder<MobEffect> CORRIENTE;

    protected CorrienteAbismalEffect() {
        super(MobEffectCategory.HARMFUL, COLOR, AtalayaParticulas.NEREA_GOTA);
        addAttributeModifier(Attributes.MOVEMENT_SPEED,
                Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "effect.corriente_abismal.lentitud"),
                LENTITUD, AttributeModifier.Operation.ADD_MULTIPLIED_TOTAL);
    }

    public static void registrar() {
        CORRIENTE = Registry.registerForHolder(BuiltInRegistries.MOB_EFFECT, CLAVE, new CorrienteAbismalEffect());
    }
}
