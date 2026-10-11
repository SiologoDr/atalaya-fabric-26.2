package com.atalaya.mixin.client;

import com.atalaya.item.AtalayaItems;
import net.minecraft.client.model.HumanoidModel;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.renderer.entity.state.HumanoidRenderState;
import org.spongepowered.asm.mixin.Final;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/**
 * Quien lleva en la mano un Pararrayos de la Tormenta (los Pararrayos de
 * Aeralis) lo lleva alzado (Juan, 10-10-2026: "al mantener vas a levantar tu
 * mano arriba y ahi va a estar el pararrayos"): ese brazo, recto hacia arriba y
 * un poco hacia fuera, sin balancearse al andar. El pararrayos sigue al brazo
 * (su modelo en tercera persona apunta a lo largo del brazo, mas alla del puno:
 * pararrayos_tormenta.json), asi que queda de pie sobre la mano. Va al final
 * de la postura, despues de todo lo de vanilla, y vale tambien para la
 * armadura, que copia la postura.
 */
@Mixin(HumanoidModel.class)
public abstract class PararrayosBrazoMixin {

    @Shadow
    @Final
    public ModelPart rightArm;

    @Shadow
    @Final
    public ModelPart leftArm;

    /** El brazo alzado: casi vertical (un pelo hacia delante) y algo abierto hacia fuera. */
    private static final float ALZADO = -2.95F;
    private static final float ABIERTO = 0.12F;

    @Inject(method = "setupAnim(Lnet/minecraft/client/renderer/entity/state/HumanoidRenderState;)V", at = @At("TAIL"))
    private void atalaya$alzarPararrayos(HumanoidRenderState s, CallbackInfo ci) {
        if (s.rightHandItemStack.is(AtalayaItems.PARARRAYOS_TORMENTA)) {
            rightArm.xRot = ALZADO;
            rightArm.yRot = 0.0F;
            rightArm.zRot = -ABIERTO;
        }
        if (s.leftHandItemStack.is(AtalayaItems.PARARRAYOS_TORMENTA)) {
            leftArm.xRot = ALZADO;
            leftArm.yRot = 0.0F;
            leftArm.zRot = ABIERTO;
        }
    }
}
