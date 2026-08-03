package com.atalaya.mixin.client;

import com.atalaya.effect.InsolacionEffect;
import net.minecraft.core.Holder;
import net.minecraft.world.effect.MobEffect;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.LivingEntity;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/**
 * Mareo suave para la insolacion.
 *
 * La nausea de vanilla tiene UNA sola intensidad: el amplificador no la toca, o
 * la pones entera o no la pones. Y entera marea de verdad a bastante gente.
 *
 * El truco esta en de donde sale esa intensidad. No la decide el efecto sino
 * {@code getEffectBlendFactor}, que devuelve un 0 a 1 y es lo que consultan
 * tanto GameRenderer para poner a girar la pantalla como el render para saber
 * cuanto deforma. Interceptando ese numero se gradua el mareo a voluntad.
 *
 * Asi que la insolacion NO aplica la nausea de vanilla: este mixin le dice al
 * renderizador que hay un mareo leve, y el renderizador se lo cree. Ventajas
 * sobre aplicar el efecto de verdad:
 *
 *   - la intensidad sale de la tabla de escalones, ajustable sin tocar codigo
 *   - no aparece un icono de Nausea en el inventario que no viene a cuento
 *   - no se pisa con una nausea autentica: si el jugador se ha bebido una
 *     pocion sospechosa o esta en un portal, se queda el valor mas alto
 *
 * Solo de cliente: es puro renderizado, al servidor no le consta nada de esto.
 */
@Mixin(LivingEntity.class)
public abstract class MareoInsolacionMixin {

    /**
     * Cuanto mareo produce la vision al maximo.
     *
     * Bajo a proposito. Un tercio del mareo de vanilla se nota como que la vista
     * te falla, que es lo que se busca, sin llegar a revolver el estomago.
     */
    private static final float MAREO_MAXIMO = 0.35f;

    @Inject(method = "getEffectBlendFactor", at = @At("RETURN"), cancellable = true)
    private void atalaya$mareoPorInsolacion(Holder<MobEffect> efecto,
                                            float parcial,
                                            CallbackInfoReturnable<Float> cir) {
        // Se comparan los MobEffect y no los Holder: los del registro son
        // singletons, y Holder.is(Holder) esta marcado como obsoleto.
        if (efecto.value() != MobEffects.NAUSEA.value()) {
            return;
        }
        if (InsolacionEffect.INSOLACION == null) {
            return; // todavia no se ha registrado
        }

        LivingEntity entidad = (LivingEntity) (Object) this;
        MobEffectInstance insolacion = entidad.getEffect(InsolacionEffect.INSOLACION);
        if (insolacion == null) {
            return;
        }

        // El amplificador es el nivel menos uno, tal como lo guarda el juego.
        float vision = InsolacionEffect.escalon(insolacion.getAmplifier() + 1).vision();
        if (vision <= 0) {
            return;
        }

        // Se queda el mayor de los dos: un mareo de verdad nunca se suaviza por
        // estar ademas insolado.
        cir.setReturnValue(Math.max(cir.getReturnValue(), vision * MAREO_MAXIMO));
    }
}
