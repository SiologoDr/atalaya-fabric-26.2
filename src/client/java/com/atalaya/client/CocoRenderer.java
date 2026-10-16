package com.atalaya.client;

import com.atalaya.Atalaya;
import com.atalaya.entity.CocoEntity;
import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import net.minecraft.ChatFormatting;
import net.minecraft.client.renderer.SubmitNodeCollector;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.MobRenderer;
import net.minecraft.client.renderer.rendertype.RenderType;
import net.minecraft.client.renderer.rendertype.RenderTypes;
import net.minecraft.client.renderer.state.level.CameraRenderState;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.Identifier;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.AnimationState;
import net.minecraft.world.phys.Vec3;

/**
 * Pinta el Coco: su malla, su piel y lo que brilla (CocoBrilloLayer). Y, si tiene a alguien dentro, el aviso de encima
 * (Juan, 16-10-2026: «que arriba del mob salga el nombre de la persona y diga ¡ha sido atrapado!, y un icono de alerta»):
 * arriba el icono, debajo el nombre del jugador y debajo «¡ha sido atrapado!» en rojo. Va como los nombres de vanilla
 * (de cara a la camara, con el fondo oscuro) y se ve a traves de las paredes hasta 48 bloques, para que los demas lo
 * encuentren.
 */
public class CocoRenderer extends MobRenderer<CocoEntity, CocoRenderState, CocoModel> {

    private static final Identifier TEXTURA =
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "textures/entity/coco/coco.png");
    private static final Identifier ICONO =
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "textures/gui/coco_alerta.png");
    private static final RenderType ICONO_NORMAL = RenderTypes.text(ICONO);
    private static final RenderType ICONO_A_TRAVES = RenderTypes.textSeeThrough(ICONO);
    /** Hasta donde se ve el aviso. */
    private static final double DISTANCIA_AVISO = 48.0;
    private static final int LUZ_PLENA = 0xF000F0;

    public CocoRenderer(EntityRendererProvider.Context contexto) {
        super(contexto, new CocoModel(contexto.bakeLayer(CocoModel.CAPA)), 1.0F);
        addLayer(new CocoBrilloLayer(this));
    }

    @Override
    public CocoRenderState createRenderState() {
        return new CocoRenderState();
    }

    @Override
    public void extractRenderState(CocoEntity coco, CocoRenderState estado, float parcial) {
        super.extractRenderState(coco, estado, parcial);
        estado.estado = coco.getEstado();
        estado.aviso = tiempo(coco.aviso, estado.ageInTicks);
        estado.traga = tiempo(coco.traga, estado.ageInTicks);
        estado.manotazo = tiempo(coco.manotazo, estado.ageInTicks);
        estado.atrapado = coco.getAtrapado();
        estado.fase = (coco.getId() * 0.61803F % 1.0F) * Mth.TWO_PI;
    }

    private static float tiempo(AnimationState animacion, float edad) {
        return animacion.isStarted() ? animacion.getTimeInMillis(edad) / 50.0F : -1.0F;
    }

    @Override
    public Identifier getTextureLocation(CocoRenderState estado) {
        return TEXTURA;
    }

    @Override
    public void submit(CocoRenderState estado, PoseStack pose, SubmitNodeCollector colector, CameraRenderState camara) {
        super.submit(estado, pose, colector, camara);
        if (estado.atrapado == null || estado.atrapado.isEmpty() || estado.deathTime > 0
                || estado.distanceToCameraSq > DISTANCIA_AVISO * DISTANCIA_AVISO) {
            return;
        }
        // Por encima de la cresta, que asoma casi un bloque sobre su caja.
        Vec3 encima = new Vec3(0.0, estado.boundingBoxHeight + 0.9, 0.0);
        // De abajo arriba, como los nombres de vanilla (el numero es la altura en pixeles de la letra, hacia abajo).
        colector.submitNameTag(pose, encima, 0,
                Component.translatable("entity.atalaya.coco.atrapado").withStyle(ChatFormatting.RED), true,
                estado.lightCoords, camara);
        colector.submitNameTag(pose, encima, -10, Component.literal(estado.atrapado), true, estado.lightCoords, camara);
        // El icono, encima del nombre: de cara a la camara, como el texto.
        pose.pushPose();
        pose.translate(encima.x, encima.y + 0.5, encima.z);
        pose.mulPose(camara.orientation);
        pose.scale(0.025F, -0.025F, 0.025F);
        colector.submitCustomGeometry(pose, ICONO_A_TRAVES, (p, buf) -> icono(p, buf, 0x80FFFFFF));
        colector.submitCustomGeometry(pose, ICONO_NORMAL, (p, buf) -> icono(p, buf, 0xFFFFFFFF));
        pose.popPose();
    }

    /** El icono de alerta: 16 x 16 pixeles de letra, centrado, encima de las dos lineas. */
    private static void icono(PoseStack.Pose p, VertexConsumer buf, int color) {
        float x0 = -8.0F, x1 = 8.0F, y0 = -30.0F, y1 = -14.0F;
        buf.addVertex(p, x0, y0, 0.0F).setColor(color).setUv(0.0F, 0.0F).setLight(LUZ_PLENA);
        buf.addVertex(p, x0, y1, 0.0F).setColor(color).setUv(0.0F, 1.0F).setLight(LUZ_PLENA);
        buf.addVertex(p, x1, y1, 0.0F).setColor(color).setUv(1.0F, 1.0F).setLight(LUZ_PLENA);
        buf.addVertex(p, x1, y0, 0.0F).setColor(color).setUv(1.0F, 0.0F).setLight(LUZ_PLENA);
    }
}
