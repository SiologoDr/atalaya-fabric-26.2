package com.atalaya.mixin;

import com.atalaya.entity.FulminanteEntity;
import net.minecraft.world.entity.monster.Creeper;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/**
 * Avisa al fulminante en cuanto ha reventado.
 *
 * El metodo que hace estallar al creeper es privado y no hay evento al que
 * engancharse, asi que este es el unico sitio.
 *
 * Se entra por el FINAL, no por la cabecera. La primera version lo hacia antes
 * de estallar, razonando que despues no quedaria arena que convertir. Era al
 * reves: la explosion tiene el mismo alcance que el corro donde se sembraban
 * los bloques, asi que se los llevaba por delante casi todos nada mas ponerlos.
 * Y ademas un crater deja MAS arena a la vista, no menos: el suelo y las
 * paredes del hoyo quedan al descubierto.
 */
@Mixin(Creeper.class)
public abstract class VitrificarMixin {

    @Inject(method = "explodeCreeper", at = @At("RETURN"))
    private void atalaya$alReventar(CallbackInfo ci) {
        if ((Object) this instanceof FulminanteEntity fulminante) {
            fulminante.vitrificar();
        }
    }
}
