package com.atalaya.client;

import com.atalaya.Atalaya;
import com.atalaya.entity.NovilisEntity;
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
 * Las auras de Novilis: la misma malla un poco hinchada
 * ({@link NovilisMalla#crearAura()}) con lenguas de fuego que le suben por
 * encima (novilis_auras.py), como las Furias de los otros tres.
 *
 *   - la Furia: fuego azul;
 *   - el Dios de la Guerra: llamas carmesi; con el Grito de guerra puesto,
 *     tambien fuera del Dios, mas tenues.
 *
 * Doce cuadros, y cada uno se funde con el siguiente: el fuego sube seguido.
 */
public class NovilisAuraLayer extends RenderLayer<NovilisRenderState, NovilisModel> {

    private static final int CUADROS = 12;
    private static final RenderType[] AZUL = new RenderType[CUADROS];
    private static final RenderType[] CARMESI = new RenderType[CUADROS];
    /** Ticks que dura cada cuadro. */
    private static final float CADA = 1.6F;

    static {
        for (int i = 0; i < CUADROS; i++) {
            AZUL[i] = RenderTypes.entityTranslucentEmissive(Identifier.fromNamespaceAndPath(Atalaya.MOD_ID,
                    "textures/entity/novilis/novilis_aura_azul_" + i + ".png"));
            CARMESI[i] = RenderTypes.entityTranslucentEmissive(Identifier.fromNamespaceAndPath(Atalaya.MOD_ID,
                    "textures/entity/novilis/novilis_aura_carmesi_" + i + ".png"));
        }
    }

    private final NovilisModel modelo;

    public NovilisAuraLayer(RenderLayerParent<NovilisRenderState, NovilisModel> padre, NovilisModel modelo) {
        super(padre);
        this.modelo = modelo;
    }

    @Override
    public void submit(PoseStack pose, SubmitNodeCollector colector, int luz, NovilisRenderState s, float yRot, float xRot) {
        if (s.deathTime > 0) {
            return;
        }
        RenderType[] cuadros;
        float k;
        if (s.furia) {
            cuadros = AZUL;
            k = 0.85F;
        } else if (s.estado == NovilisEntity.DIOS) {
            cuadros = CARMESI;
            k = 0.95F;
        } else if (s.grito) {
            cuadros = CARMESI;
            k = 0.45F;
        } else {
            return;
        }
        float t = s.ageInTicks / CADA;
        int cuadro = Mth.floor(t) % CUADROS;
        int siguiente = (cuadro + 1) % CUADROS;
        float mezcla = t - Mth.floor(t);
        k *= 0.85F + 0.15F * Mth.sin(s.ageInTicks * 0.3F);
        colector.order(2).submitModel(modelo, s, pose, cuadros[cuadro], NovilisDibujo.A_PLENA_LUZ, OverlayTexture.NO_OVERLAY,
                ARGB.colorFromFloat(k * (1.0F - mezcla), 1.0F, 1.0F, 1.0F), null, s.outlineColor, null);
        colector.order(2).submitModel(modelo, s, pose, cuadros[siguiente], NovilisDibujo.A_PLENA_LUZ, OverlayTexture.NO_OVERLAY,
                ARGB.colorFromFloat(k * mezcla, 1.0F, 1.0F, 1.0F), null, s.outlineColor, null);
    }
}
