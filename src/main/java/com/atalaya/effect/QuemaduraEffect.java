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
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.entity.LivingEntity;
import org.jspecify.annotations.Nullable;

/**
 * Quemadura: lo que deja el fuego de Novilis. Tres niveles (I leve, II fuerte,
 * III grave); cada golpe de fuego suma. Por si sola no quita vida: es una
 * marca. Con la III, el Dios de la Guerra mata (salvo totem).
 *
 * Baja sola, un nivel cada 10 s sin quemarse: se pone como una cadena de
 * efectos ocultos (el III esconde al II, que esconde al I), igual que hace
 * vanilla cuando un efecto fuerte tapa a uno mas largo. El agua NO la quita;
 * beberse una botella de agua, si (QuemaduraAguaMixin).
 */
public class QuemaduraEffect extends MobEffect {

    private static final int COLOR = 0xFF6A1E;
    /** Lo que dura cada nivel antes de bajar al siguiente. */
    public static final int POR_NIVEL = 200;

    public static final ResourceKey<MobEffect> CLAVE = ResourceKey.create(
            Registries.MOB_EFFECT,
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "quemadura"));

    public static Holder<MobEffect> QUEMADURA;

    protected QuemaduraEffect() {
        super(MobEffectCategory.HARMFUL, COLOR, AtalayaParticulas.NOVILIS_BRASA);
    }

    public static void registrar() {
        QUEMADURA = Registry.registerForHolder(BuiltInRegistries.MOB_EFFECT, CLAVE, new QuemaduraEffect());
    }

    /** El nivel de quemadura (0 sin quemar, 1 leve, 2 fuerte, 3 grave). */
    public static int nivel(LivingEntity v) {
        MobEffectInstance e = v.getEffect(QUEMADURA);
        return e == null ? 0 : e.getAmplifier() + 1;
    }

    /** Suma niveles de quemadura (hasta la III) y vuelve a empezar la cuenta atras. */
    public static void quemar(LivingEntity v, int niveles) {
        if (v.level().isClientSide() || niveles <= 0) {
            return;
        }
        int nuevo = Math.min(3, nivel(v) + niveles);
        poner(v, nuevo);
    }

    /** Pone justo ese nivel (la Supernova deja la III directamente). */
    public static void poner(LivingEntity v, int nivel) {
        v.removeEffect(QUEMADURA);
        if (nivel <= 0) {
            return;
        }
        // De abajo arriba: el I dura mas que el II, que dura mas que el III, y cada
        // uno queda oculto bajo el siguiente hasta que este se acaba.
        @Nullable MobEffectInstance oculto = null;
        for (int k = 1; k <= nivel; k++) {
            int dura = (nivel - k + 1) * POR_NIVEL;
            oculto = new MobEffectInstance(QUEMADURA, dura, k - 1, false, true, true, oculto);
        }
        v.addEffect(oculto);
    }

    /** Beberse una botella de agua la quita entera. */
    public static void apagar(LivingEntity v) {
        v.removeEffect(QUEMADURA);
    }
}
