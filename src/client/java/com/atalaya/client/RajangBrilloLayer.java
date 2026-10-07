package com.atalaya.client;

import com.atalaya.Atalaya;
import com.atalaya.entity.RajangEntity;
import com.atalaya.entity.RajangGeometria;
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
 * Lo que brilla de Rajang: los ojos, la boca por dentro, los cristales, el
 * sol del pecho y (de la fase II en adelante) las grietas de la maldicion,
 * del verde al lima y al amarillo. Liberado, todo en oro.
 *
 * Despierto, el brillo late con la fase: despacio y suave en la I, cada vez
 * mas deprisa y mas fuerte, y en la III y la IV con una segunda pasada que lo
 * enciende del todo. Dormido, respira despacio; al despertar sigue asi hasta
 * que abre los ojos, y la cresta erizada y el rugido lo encienden de mas
 * (brilloDespertar); mientras sostiene el Sello o
 * ruge al cielo, late fuerte; aturdido o paralizado, parpadea como una brasa
 * que se apaga. Con la Furia de Jade, todo encendido.
 */
public class RajangBrilloLayer extends RenderLayer<RajangRenderState, RajangModel> {

    private static final RenderType[] FASES = new RenderType[4];
    private static final RenderType LIBRE = RenderTypes.eyes(tex("rajang_brillo_libre"));

    static {
        for (int i = 0; i < 4; i++) {
            FASES[i] = RenderTypes.eyes(tex("rajang_brillo_f" + (i + 1)));
        }
    }

    private static Identifier tex(String nombre) {
        return Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "textures/entity/rajang/" + nombre + ".png");
    }

    public RajangBrilloLayer(RenderLayerParent<RajangRenderState, RajangModel> padre) {
        super(padre);
    }

    @Override
    public void submit(PoseStack pose, SubmitNodeCollector colector, int luz, RajangRenderState s, float yRot, float xRot) {
        float k = 1.0F - s.disolver;
        switch (s.estado) {
            case RajangEntity.DORMIDO -> k *= 0.45F + 0.25F * Mth.sin(s.ageInTicks * 0.06F);
            case RajangEntity.DESPERTAR -> {
                // Aun dormido hasta que abre los ojos; entonces se enciende de golpe.
                float abre = Mth.clamp((s.tiempoDespertar - RajangGeometria.DESPERTAR_ABRE) / 3.0F, 0.0F, 1.0F);
                k *= Mth.lerp(abre, 0.45F + 0.25F * Mth.sin(s.ageInTicks * 0.06F), 1.0F);
            }
            case RajangEntity.SELLO, RajangEntity.RUGIDO, RajangEntity.CATACLISMO, RajangEntity.CATACLISMO_SOSTIENE,
                 RajangEntity.EMBESTIDA_AVISO, RajangEntity.EMBESTIDA, RajangEntity.TUMBA ->
                    k *= 0.85F + 0.15F * Mth.sin(s.ageInTicks * 0.5F);
            case RajangEntity.ATURDIDO, RajangEntity.PARALIZADO, RajangEntity.ESTAMPADO -> {
                if (((int) s.ageInTicks % 7) < 2) {
                    k *= 0.3F;
                }
            }
            default -> {
                if (!s.libre && s.deathTime <= 0) {
                    int f = Math.clamp(s.fase, 1, 4);
                    k *= LATE_BASE[f] + (1.0F - LATE_BASE[f]) * (0.5F + 0.5F * Mth.sin(s.ageInTicks * LATE_RITMO[f]));
                }
            }
        }
        if (k <= 0.01F) {
            return;
        }
        RenderType tipo = s.libre ? LIBRE : FASES[Math.clamp(s.fase, 1, 4) - 1];
        colector.order(1).submitModel(getParentModel(), s, pose, tipo, luz, OverlayTexture.NO_OVERLAY,
                ARGB.colorFromFloat(k, k, k, k), null, s.outlineColor, null);
        // En la III y la IV la maldicion lo enciende del todo: una segunda pasada encima
        // (y con la Furia, aun mas).
        float extra = s.libre || s.deathTime > 0 ? 0.0F : s.fase >= 4 ? 0.7F : s.fase == 3 ? 0.35F : 0.0F;
        if (s.furia && !s.libre && s.deathTime <= 0) {
            extra = Math.min(1.0F, extra + 0.5F);
        }
        if (s.estado == RajangEntity.DESPERTAR && s.deathTime <= 0) {
            extra = Math.max(extra, brilloDespertar(s.tiempoDespertar));
        }
        if (extra > 0.0F) {
            float e = k * extra;
            colector.order(2).submitModel(getParentModel(), s, pose, tipo, luz, OverlayTexture.NO_OVERLAY,
                    ARGB.colorFromFloat(e, e, e, e), null, s.outlineColor, null);
        }
    }

    /**
     * Lo que se enciende de mas al despertar: un destello al abrir los ojos, la
     * cresta que se eriza mientras esta agazapado y el rugido; se apaga del todo
     * al acabar, cuando ya esta en reposo.
     */
    private static float brilloDespertar(float t) {
        float abre = t - RajangGeometria.DESPERTAR_ABRE;
        float destello = abre >= 0.0F ? 0.8F * Math.max(0.0F, 1.0F - abre / 14.0F) : 0.0F;
        float cresta = 0.45F * Mth.clamp((t - RajangGeometria.DESPERTAR_ALZADO - 3.0F) / 8.0F, 0.0F, 1.0F);
        float ruge = t >= RajangGeometria.DESPERTAR_RUGE ? 0.9F : 0.0F;
        float desde = RajangGeometria.DESPERTAR_RUGE + 20.0F;
        float apaga = 1.0F - Mth.clamp((t - desde) / (RajangGeometria.DURACION_DESPERTAR - desde), 0.0F, 1.0F);
        return Math.max(destello, Math.max(cresta, ruge) * apaga);
    }

    /** El latido del brillo en cada fase: lo que baja como mucho y lo deprisa que late. */
    private static final float[] LATE_BASE = {1.0F, 0.82F, 0.72F, 0.62F, 0.55F};
    private static final float[] LATE_RITMO = {0.0F, 0.07F, 0.11F, 0.17F, 0.25F};
}
