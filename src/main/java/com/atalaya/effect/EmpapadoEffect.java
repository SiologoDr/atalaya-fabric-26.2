package com.atalaya.effect;

import com.atalaya.Atalaya;
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
 * Efecto de estado "Empapado": la ropa calada pesa y te frena.
 *
 * Comparte disparador con la corrosion —te esta lloviendo encima— pero es otra
 * cosa y va por su lado: la corrosion se come la armadura y esta te frena, asi
 * que cada una tiene su interruptor y se pueden usar por separado.
 *
 * A diferencia de la insolacion, aqui SI se usa el modificador del propio
 * efecto. La insolacion suma castigos distintos en cada escalon y eso el efecto
 * no lo sabe expresar; esta tiene una sola penalizacion sobre un solo atributo,
 * que es exactamente para lo que sirve el mecanismo de vanilla. Ademas se
 * retira sola al quitar el efecto, sin que nadie tenga que acordarse.
 *
 * Sin niveles, como la corrosion: o te llueve encima o no.
 */
public class EmpapadoEffect extends MobEffect {

    /** Azul de lluvia, tomado del propio icono. Libre entre los otros tres:
     *  morado la radiacion, naranja la insolacion, verde la corrosion. */
    private static final int COLOR = 0x3A8FC8;

    /**
     * Fraccion de velocidad que resta.
     *
     * Va como ADD_MULTIPLIED_TOTAL, asi que -0.50 deja la velocidad a la mitad.
     * Es tanto como una Lentitud IV de vanilla: cruzar un aguacero a pie tiene
     * que doler, y el remedio es el mismo que el de la corrosion — cubrirse.
     */
    private static final double LENTITUD = -0.50;

    public static final ResourceKey<MobEffect> CLAVE = ResourceKey.create(
            Registries.MOB_EFFECT,
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "empapado"));

    public static Holder<MobEffect> EMPAPADO;

    protected EmpapadoEffect() {
        super(MobEffectCategory.HARMFUL, COLOR);
    }

    public static void registrar() {
        MobEffect efecto = new EmpapadoEffect()
                .addAttributeModifier(
                        Attributes.MOVEMENT_SPEED,
                        Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "empapado_lentitud"),
                        LENTITUD,
                        AttributeModifier.Operation.ADD_MULTIPLIED_TOTAL);

        EMPAPADO = Registry.registerForHolder(BuiltInRegistries.MOB_EFFECT, CLAVE, efecto);
    }
}
