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
 * Paralisis: lo que deja la descarga de una mancha de las Escamas de Tormenta
 * de Aeralis. No te puedes mover ni saltar, pero si pegar, abrir el inventario
 * y usar objetos (a diferencia del Aturdimiento, que lo bloquea todo). Con
 * modificadores propios y los rayos de Aeralis como particula.
 */
public class ParalisisEffect extends MobEffect {

    /** El violeta de la Tempestad, la fase en que aparecen las Escamas. */
    private static final int COLOR = 0xB98CFF;

    public static final ResourceKey<MobEffect> CLAVE = ResourceKey.create(
            Registries.MOB_EFFECT,
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "paralisis"));

    public static Holder<MobEffect> PARALISIS;

    protected ParalisisEffect() {
        super(MobEffectCategory.HARMFUL, COLOR, AtalayaParticulas.AERALIS_RAYO);
        addAttributeModifier(Attributes.MOVEMENT_SPEED,
                Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "effect.paralisis.quieto"),
                -1.0, AttributeModifier.Operation.ADD_MULTIPLIED_TOTAL);
        addAttributeModifier(Attributes.JUMP_STRENGTH,
                Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "effect.paralisis.salto"),
                -1.0, AttributeModifier.Operation.ADD_MULTIPLIED_TOTAL);
    }

    public static void registrar() {
        PARALISIS = Registry.registerForHolder(BuiltInRegistries.MOB_EFFECT, CLAVE, new ParalisisEffect());
    }
}
