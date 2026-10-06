package com.atalaya.client;

import com.atalaya.Atalaya;
import com.atalaya.entity.GanchoNereaEntity;
import com.atalaya.entity.NereaEntity;
import com.atalaya.entity.NereaGeometria;
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
import net.minecraft.util.Mth;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.level.ClipContext;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;
import org.jspecify.annotations.Nullable;

/**
 * El ancla del Arpon (desde el remake), con la cadena tendida hasta la mano de
 * Nerea: la misma ancla que lleva en la mano ({@link NereaMalla#crearAncla()},
 * con el mismo atlas), a la escala de su cuerpo. Vuela con la cruz y las unas
 * por delante; clavada, apunta hacia ella, que es de donde tira. Mientras
 * vuela marca con un aro de espuma el suelo de a quien va.
 */
public class GanchoNereaRenderer extends EntityRenderer<GanchoNereaEntity, GanchoNereaRenderer.Estado> {

    public static final ModelLayerLocation CAPA = new ModelLayerLocation(
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "gancho_nerea"), "main");

    /** La piel de Nerea: el ancla usa sus mismas cajas del atlas. */
    private static final RenderType TIPO = RenderTypes.entityCutout(
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "textures/entity/nerea/nerea_f1.png"));
    /** La escala de la malla de Nerea (NereaRenderer). */
    private static final float ESCALA = 2.4F;
    /** Lo que mide el aro bajo el blanco (bloques de radio). */
    private static final float ARO = 1.6F;

    public static class Estado extends EntityRenderState {
        public float yRot;
        public float xRot;
        public float edad;
        /** La mano de Nerea, relativa al ancla. */
        public @Nullable Vec3 mano;
        /** El suelo bajo a quien va, relativo al ancla (null si ya esta clavada). */
        public @Nullable Vec3 blanco;
    }

    public static class Modelo extends EntityModel<Estado> {

        public Modelo(ModelPart raiz) {
            super(raiz);
        }
    }

    private final Modelo modelo;

    public GanchoNereaRenderer(EntityRendererProvider.Context contexto) {
        super(contexto);
        this.modelo = new Modelo(contexto.bakeLayer(CAPA));
    }

    @Override
    public Estado createRenderState() {
        return new Estado();
    }

    @Override
    public void extractRenderState(GanchoNereaEntity g, Estado s, float parcial) {
        super.extractRenderState(g, s, parcial);
        s.yRot = g.getYRot(parcial);
        s.xRot = g.getXRot(parcial);
        s.edad = g.tickCount + parcial;
        s.mano = null;
        s.blanco = null;
        Vec3 aqui = g.getPosition(parcial);
        if (g.getOwner() instanceof NereaEntity nerea && nerea.isAlive()) {
            Vec3 pies = nerea.getPosition(parcial);
            // La mano de verdad: donde la tiene la animacion en este instante,
            // no un punto fijo. Al tirar, la cadena va con el brazo.
            float ticks = (nerea.tickCount - nerea.inicioEstado + parcial) * nerea.ritmoCliente;
            Vec3 local = switch (nerea.getEstado()) {
                case NereaEntity.ARPON_LANZAR -> NereaGeometria.manoArpon(NereaGeometria.MANO_ARPON_LANZAR, ticks, false);
                case NereaEntity.ARPON_TIRAR -> NereaGeometria.manoArpon(NereaGeometria.MANO_ARPON_TIRAR, ticks, false);
                default -> NereaGeometria.manoArpon(NereaGeometria.MANO_ARPON_ESPERA, ticks, true);
            };
            Vec3 mano = NereaEntity.puntoMundo(local, pies, nerea.getPreciseBodyRotation(parcial));
            s.mano = mano.subtract(aqui);
            if (g.getIdEnganchado() >= 0) {
                // Clavada: el ancla mira a la mano, que es de donde tira.
                Vec3 d = s.mano.scale(-1);
                s.yRot = (float) (Mth.atan2(d.x, d.z) * Mth.RAD_TO_DEG);
                s.xRot = (float) (Mth.atan2(d.y, d.horizontalDistance()) * Mth.RAD_TO_DEG);
            }
        }
        if (g.getIdEnganchado() < 0) {
            Entity b = g.level().getEntity(g.getIdBlanco());
            if (b != null) {
                Vec3 pie = b.getPosition(parcial);
                double y = pie.y;
                if (!b.onGround()) {
                    BlockHitResult choque = g.level().clip(new ClipContext(pie, pie.add(0, -10, 0), ClipContext.Block.COLLIDER,
                            ClipContext.Fluid.NONE, b));
                    if (choque.getType() != HitResult.Type.MISS) {
                        y = choque.getLocation().y;
                    }
                }
                s.blanco = new Vec3(pie.x, y, pie.z).subtract(aqui);
            }
        }
    }

    @Override
    protected boolean affectedByCulling(GanchoNereaEntity g) {
        return false;
    }

    @Override
    public void submit(Estado s, PoseStack pose, SubmitNodeCollector colector, CameraRenderState camara) {
        if (s.mano != null) {
            CadenaRender.dibujar(pose, colector, Vec3.ZERO, s.mano, s.lightCoords, 0.45F);
        }
        if (s.blanco != null) {
            Vec3 c = s.blanco;
            float m = ARO / NereaDibujo.ARO_EN_TEXTURA * (1.0F + 0.08F * Mth.sin(s.edad * 0.6F));
            colector.submitCustomGeometry(pose, NereaDibujo.ARO, (p, buf) ->
                    NereaDibujo.suelo(buf, p, c.x, c.y + 0.07, c.z, m, s.edad * 0.08F, 0xFFFFFF, 220));
        }
        pose.pushPose();
        // Como las flechas: Y por el rumbo, X por la inclinacion (cambiada de signo).
        pose.mulPose(Axis.YP.rotationDegrees(s.yRot));
        pose.mulPose(Axis.XP.rotationDegrees(-s.xRot));
        pose.scale(ESCALA, ESCALA, ESCALA);
        colector.submitModel(modelo, s, pose, TIPO, s.lightCoords, OverlayTexture.NO_OVERLAY, s.outlineColor, null);
        pose.popPose();
        super.submit(s, pose, colector, camara);
    }
}
