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
 * El aura de la Furia del Vendaval: la misma malla un poco hinchada
 * ({@link AeralisMalla#crearAura()}) con rayos violetas en zigzag que le corren
 * por encima, como la Furia de Jade de Rajang ({@link RajangFuriaLayer}).
 *
 * <p>No es la capa del creeper que usa Rajang: esa pinta la caja entera, y las
 * alas de Aeralis son laminas recortadas (se veian rectangulos). Aqui la textura
 * va sobre el mismo atlas que su piel (aeralis_mejoras_extras.py), asi que
 * sigue el recorte. Son doce cuadros con las bandas corridas un poco cada uno,
 * y cada cuadro se funde con el siguiente: los rayos corren seguidos, sin
 * tirones (con cuatro cuadros alternados se veia raro). Fuera de los rayos es
 * transparente y brillan sin luz.
 */
public class AeralisFuriaLayer extends RenderLayer<AeralisRenderState, AeralisModel> {

    private static final RenderType[] CUADROS = new RenderType[12];
    /** Ticks que dura cada cuadro: las bandas dan la vuelta en 1,2 s. */
    private static final float CADA = 2.0F;

    static {
        for (int i = 0; i < CUADROS.length; i++) {
            CUADROS[i] = RenderTypes.entityTranslucentEmissive(Identifier.fromNamespaceAndPath(Atalaya.MOD_ID,
                    "textures/entity/aeralis/aeralis_furia_" + i + ".png"));
        }
    }

    private final AeralisModel modelo;

    public AeralisFuriaLayer(RenderLayerParent<AeralisRenderState, AeralisModel> padre, AeralisModel modelo) {
        super(padre);
        this.modelo = modelo;
    }

    @Override
    public void submit(PoseStack pose, SubmitNodeCollector colector, int luz, AeralisRenderState s, float yRot, float xRot) {
        if (!s.furia || s.deathTime > 0) {
            return;
        }
        float t = s.ageInTicks / CADA;
        int cuadro = Mth.floor(t) % CUADROS.length;
        int siguiente = (cuadro + 1) % CUADROS.length;
        float mezcla = t - Mth.floor(t);
        // Late deprisa, como la tormenta de la barra.
        float k = 0.85F + 0.15F * Mth.sin(s.ageInTicks * 0.45F);
        // Un cuadro se va mientras entra el siguiente.
        colector.order(2).submitModel(modelo, s, pose, CUADROS[cuadro], AeralisDibujo.A_PLENA_LUZ, OverlayTexture.NO_OVERLAY,
                ARGB.colorFromFloat(k * (1.0F - mezcla), 1.0F, 1.0F, 1.0F), null, s.outlineColor, null);
        colector.order(2).submitModel(modelo, s, pose, CUADROS[siguiente], AeralisDibujo.A_PLENA_LUZ, OverlayTexture.NO_OVERLAY,
                ARGB.colorFromFloat(k * mezcla, 1.0F, 1.0F, 1.0F), null, s.outlineColor, null);
    }
}
