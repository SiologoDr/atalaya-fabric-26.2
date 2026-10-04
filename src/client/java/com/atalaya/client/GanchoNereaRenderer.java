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
import net.minecraft.client.model.geom.PartPose;
import net.minecraft.client.model.geom.builders.CubeListBuilder;
import net.minecraft.client.model.geom.builders.LayerDefinition;
import net.minecraft.client.model.geom.builders.MeshDefinition;
import net.minecraft.client.model.geom.builders.PartDefinition;
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
import net.minecraft.world.phys.Vec3;
import org.jspecify.annotations.Nullable;

/**
 * El gancho del Arpon, con la cadena tendida hasta la mano de Nerea. Vuela con
 * las puas por delante; clavado, apunta hacia ella, que es de donde tira.
 */
public class GanchoNereaRenderer extends EntityRenderer<GanchoNereaEntity, GanchoNereaRenderer.Estado> {

    public static final ModelLayerLocation CAPA = new ModelLayerLocation(
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "gancho_nerea"), "main");

    private static final RenderType TIPO = RenderTypes.entityCutout(
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "textures/entity/nerea/gancho.png"));

    public static class Estado extends EntityRenderState {
        public float yRot;
        public float xRot;
        /** La mano de Nerea, relativa al gancho. */
        public @Nullable Vec3 mano;
    }

    /** Las mismas cajas que el gancho de la mano en NereaMalla (GANCHO en nerea_juego.py). */
    public static class Modelo extends EntityModel<Estado> {

        public Modelo(ModelPart raiz) {
            super(raiz);
        }

        public static LayerDefinition crear() {
            MeshDefinition malla = new MeshDefinition();
            PartDefinition raiz = malla.getRoot();
            // Eje del gancho en +Y local; se gira para que apunte a Z, el sentido de vuelo.
            raiz.addOrReplaceChild("gancho", CubeListBuilder.create()
                            .texOffs(0, 0).addBox(-1.5F, 0.0F, -1.5F, 3.0F, 3.0F, 3.0F)
                            .texOffs(0, 8).addBox(-0.75F, 3.0F, -0.75F, 1.5F, 6.0F, 1.5F)
                            .texOffs(0, 8).addBox(-4.5F, 7.0F, -0.75F, 9.0F, 1.5F, 1.5F)
                            .texOffs(0, 8).addBox(-4.5F, 3.5F, -0.75F, 1.5F, 4.0F, 1.5F)
                            .texOffs(0, 8).addBox(3.0F, 3.5F, -0.75F, 1.5F, 4.0F, 1.5F)
                            .texOffs(0, 8).addBox(-0.75F, 7.0F, -4.5F, 1.5F, 1.5F, 9.0F)
                            .texOffs(0, 8).addBox(-0.75F, 3.5F, -4.5F, 1.5F, 4.0F, 1.5F)
                            .texOffs(0, 8).addBox(-0.75F, 3.5F, 3.0F, 1.5F, 4.0F, 1.5F),
                    PartPose.offsetAndRotation(0.0F, 0.0F, -4.0F, Mth.PI / 2.0F, 0.0F, 0.0F));
            return LayerDefinition.create(malla, 32, 32);
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
        s.mano = null;
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
            s.mano = mano.subtract(g.getPosition(parcial));
            if (g.getIdEnganchado() >= 0) {
                // Clavado: el gancho mira a la mano, que es de donde tira.
                Vec3 d = s.mano.scale(-1);
                s.yRot = (float) (Mth.atan2(d.x, d.z) * Mth.RAD_TO_DEG);
                s.xRot = (float) (Mth.atan2(d.y, d.horizontalDistance()) * Mth.RAD_TO_DEG);
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
            CadenaRender.dibujar(pose, colector, Vec3.ZERO, s.mano, s.lightCoords, 0.3F);
        }
        pose.pushPose();
        // Como las flechas: Y por el rumbo, X por la inclinacion (cambiada de signo).
        pose.mulPose(Axis.YP.rotationDegrees(s.yRot));
        pose.mulPose(Axis.XP.rotationDegrees(-s.xRot));
        pose.scale(1.6F, 1.6F, 1.6F);
        colector.submitModel(modelo, s, pose, TIPO, s.lightCoords, OverlayTexture.NO_OVERLAY, s.outlineColor, null);
        pose.popPose();
        super.submit(s, pose, colector, camara);
    }
}
