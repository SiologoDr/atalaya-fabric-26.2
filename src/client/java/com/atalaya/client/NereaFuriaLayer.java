package com.atalaya.client;

import com.atalaya.Atalaya;
import com.mojang.blaze3d.vertex.PoseStack;
import net.minecraft.client.renderer.SubmitNodeCollector;
import net.minecraft.client.renderer.entity.RenderLayerParent;
import net.minecraft.client.renderer.entity.layers.RenderLayer;
import net.minecraft.client.renderer.rendertype.RenderType;
import net.minecraft.client.renderer.rendertype.RenderTypes;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.resources.Identifier;
import net.minecraft.util.ARGB;
import net.minecraft.util.Mth;

/**
 * El aura de la Furia de las Mareas: la misma malla un poco hinchada
 * ({@link NereaMalla#crearAura()}) con la red de luz que hace el sol bajo el
 * agua (causticas) en verde abismo, que se mueve. Como las de Rajang y
 * Aeralis, pero de mar.
 *
 * La textura va sobre el mismo atlas que su piel (nerea_mejoras_extras.py), asi
 * que sigue el recorte de cada pieza. Son dieciseis cuadros en los que cada nudo
 * de la red da una vuelta pequena, y cada cuadro se funde con el siguiente: la
 * luz ondula seguido, sin saltos. Fuera de las lineas es transparente y brilla
 * sin luz.
 */
public class NereaFuriaLayer extends RenderLayer<NereaRenderState, NereaModel> {

    private static final RenderType[] CUADROS = new RenderType[16];
    /** Ticks que dura cada cuadro: el agua ondula despacio (una vuelta, 2,4 s). */
    private static final float CADA = 3.0F;

    static {
        for (int i = 0; i < CUADROS.length; i++) {
            CUADROS[i] = RenderTypes.entityTranslucentEmissive(Identifier.fromNamespaceAndPath(Atalaya.MOD_ID,
                    "textures/entity/nerea/nerea_furia_" + i + ".png"));
        }
    }

    private final NereaModel modelo;

    public NereaFuriaLayer(RenderLayerParent<NereaRenderState, NereaModel> padre, NereaModel modelo) {
        super(padre);
        this.modelo = modelo;
    }

    @Override
    public void submit(PoseStack pose, SubmitNodeCollector colector, int luz, NereaRenderState s, float yRot, float xRot) {
        if (!s.furia || s.deathTime > 0) {
            return;
        }
        float t = s.ageInTicks / CADA;
        int cuadro = Mth.floor(t) % CUADROS.length;
        int siguiente = (cuadro + 1) % CUADROS.length;
        float mezcla = t - Mth.floor(t);
        // Respira como el agua: sube y baja despacio.
        float k = 0.8F + 0.2F * Mth.sin(s.ageInTicks * 0.2F);
        // Un cuadro se va mientras entra el siguiente.
        colector.order(2).submitModel(modelo, s, pose, CUADROS[cuadro], NereaDibujo.A_PLENA_LUZ, OverlayTexture.NO_OVERLAY,
                ARGB.colorFromFloat(k * (1.0F - mezcla), 1.0F, 1.0F, 1.0F), null, s.outlineColor, null);
        colector.order(2).submitModel(modelo, s, pose, CUADROS[siguiente], NereaDibujo.A_PLENA_LUZ, OverlayTexture.NO_OVERLAY,
                ARGB.colorFromFloat(k * mezcla, 1.0F, 1.0F, 1.0F), null, s.outlineColor, null);
    }
}
