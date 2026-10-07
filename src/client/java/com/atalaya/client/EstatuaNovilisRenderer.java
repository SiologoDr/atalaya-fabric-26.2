package com.atalaya.client;

import com.atalaya.Atalaya;
import com.atalaya.entity.EstatuaNovilisEntity;
import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.math.Axis;
import net.minecraft.client.model.EntityModel;
import net.minecraft.client.model.geom.ModelLayerLocation;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.renderer.SubmitNodeCollector;
import net.minecraft.client.renderer.entity.EntityRenderer;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.state.EntityRenderState;
import net.minecraft.client.renderer.rendertype.RenderType;
import net.minecraft.client.renderer.rendertype.RenderTypes;
import net.minecraft.client.renderer.state.level.CameraRenderState;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.resources.Identifier;
import net.minecraft.util.ARGB;
import net.minecraft.util.Mth;

/**
 * Una estatua de las Trompetas del Apocalipsis: el angel de marmol de
 * novilis_props.py (7,5 bloques con el pedestal), con la campana de la
 * trompeta encendida. Sale del suelo al aparecer, tiembla con cada golpe y,
 * rota, se queda en escombros sobre el pedestal.
 */
public class EstatuaNovilisRenderer extends EntityRenderer<EstatuaNovilisEntity, EstatuaNovilisRenderer.Estado> {

    public static final ModelLayerLocation CAPA = new ModelLayerLocation(
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "estatua_novilis"), "main");
    public static final ModelLayerLocation CAPA_ROTA = new ModelLayerLocation(
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "estatua_novilis"), "rota");

    private static final Identifier TEXTURA = Identifier.fromNamespaceAndPath(Atalaya.MOD_ID,
            "textures/entity/novilis/estatua.png");
    private static final RenderType PIEL = RenderTypes.entityCutout(TEXTURA);
    private static final RenderType BRILLO = RenderTypes.eyes(Identifier.fromNamespaceAndPath(Atalaya.MOD_ID,
            "textures/entity/novilis/estatua_brillo.png"));

    public static class Estado extends EntityRenderState {
        public float edad;
        public float rumbo;
        public boolean rota;
        public float desdeGolpe = 100.0F;
        /** Va a dar su pulso: la trompeta se enciende del todo y parpadea. */
        public boolean avisa;
    }

    /** La malla tal cual (no se anima: es una estatua). */
    public static class Modelo extends EntityModel<Estado> {
        public Modelo(ModelPart raiz) {
            super(raiz);
        }
    }

    private final Modelo entera;
    private final Modelo rota;

    public EstatuaNovilisRenderer(EntityRendererProvider.Context contexto) {
        super(contexto);
        this.entera = new Modelo(contexto.bakeLayer(CAPA));
        this.rota = new Modelo(contexto.bakeLayer(CAPA_ROTA));
    }

    @Override
    public Estado createRenderState() {
        return new Estado();
    }

    @Override
    public void extractRenderState(EstatuaNovilisEntity e, Estado s, float parcial) {
        super.extractRenderState(e, s, parcial);
        s.edad = e.tickCount + parcial;
        s.rumbo = e.getYRot();
        s.rota = e.isRoto();
        s.desdeGolpe = e.tickCount - e.ultimoGolpe + parcial;
        s.avisa = e.avisa();
    }

    @Override
    protected boolean affectedByCulling(EstatuaNovilisEntity e) {
        return false;
    }

    @Override
    public void submit(Estado s, PoseStack pose, SubmitNodeCollector colector, CameraRenderState camara) {
        // Sale del suelo: sube en SALE ticks frenando al final.
        float k = Mth.clamp(s.edad / EstatuaNovilisEntity.SALE, 0.0F, 1.0F);
        float sube = (1.0F - (1.0F - k) * (1.0F - k)) * 7.5F - 7.5F;
        float tiembla = s.desdeGolpe < 6 ? 0.06F * Mth.sin(s.desdeGolpe * 2.6F) * (6 - s.desdeGolpe) : 0.0F;
        pose.pushPose();
        pose.translate(tiembla, sube, 0.0F);
        pose.mulPose(Axis.YP.rotationDegrees(180.0F - s.rumbo));
        pose.scale(-1.0F, -1.0F, 1.0F);
        pose.translate(0.0F, -1.501F, 0.0F);
        Modelo m = s.rota ? rota : entera;
        colector.order(1).submitModel(m, s, pose, PIEL, s.lightCoords, OverlayTexture.NO_OVERLAY, s.outlineColor, null);
        if (!s.rota) {
            float late = s.avisa ? 0.85F + 0.15F * Mth.sin(s.edad * 1.6F) : 0.75F + 0.25F * Mth.sin(s.edad * 0.25F);
            colector.order(2).submitModel(m, s, pose, BRILLO, NovilisDibujo.A_PLENA_LUZ, OverlayTexture.NO_OVERLAY,
                    ARGB.colorFromFloat(late, late, late, late), null, s.outlineColor, null);
        }
        pose.popPose();
        super.submit(s, pose, colector, camara);
    }
}
