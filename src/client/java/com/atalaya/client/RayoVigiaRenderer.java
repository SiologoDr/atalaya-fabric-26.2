package com.atalaya.client;

import com.atalaya.Atalaya;
import com.atalaya.entity.RayoVigiaEntity;
import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.math.Axis;
import net.minecraft.client.renderer.SubmitNodeCollector;
import net.minecraft.client.renderer.entity.EntityRenderer;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.rendertype.RenderType;
import net.minecraft.client.renderer.rendertype.RenderTypes;
import net.minecraft.client.renderer.state.level.CameraRenderState;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.resources.Identifier;

/**
 * Pinta el rayo como una flecha de luz: la malla apuntada hacia donde vuela,
 * a brillo completo y translucida.
 *
 * El giro es el mismo que usa vanilla con las flechas. El proyectil guarda
 * yRot = atan2(vx, vz) y xRot = atan2(vy, horizontal); girar Y por el primero
 * y X por el segundo, cambiado de signo, deja el eje Z de la malla —su largo—
 * sobre la velocidad.
 */
public class RayoVigiaRenderer extends EntityRenderer<RayoVigiaEntity, RayoVigiaRenderState> {

    private static final Identifier TEXTURA =
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "textures/entity/vigia/rayo.png");

    /** Brillo completo: el rayo alumbra, no se ilumina. */
    private static final int A_PLENA_LUZ = 0xF000F0;

    private final RayoVigiaModel modelo;
    private final RenderType tipo;

    public RayoVigiaRenderer(EntityRendererProvider.Context contexto) {
        super(contexto);
        this.modelo = new RayoVigiaModel(contexto.bakeLayer(RayoVigiaModel.CAPA));
        this.tipo = RenderTypes.entityTranslucentEmissive(TEXTURA);
    }

    @Override
    public RayoVigiaRenderState createRenderState() {
        return new RayoVigiaRenderState();
    }

    @Override
    public void extractRenderState(RayoVigiaEntity rayo, RayoVigiaRenderState estado, float parcial) {
        super.extractRenderState(rayo, estado, parcial);
        estado.yRot = rayo.getYRot(parcial);
        estado.xRot = rayo.getXRot(parcial);
    }

    @Override
    public void submit(RayoVigiaRenderState estado, PoseStack pose, SubmitNodeCollector colector,
                       CameraRenderState camara) {
        pose.pushPose();
        pose.mulPose(Axis.YP.rotationDegrees(estado.yRot));
        pose.mulPose(Axis.XP.rotationDegrees(-estado.xRot));
        // Un tercio mas grande que la malla: a diez bloques tiene que leerse.
        pose.scale(1.3F, 1.3F, 1.3F);
        colector.submitModel(modelo, estado, pose, tipo, A_PLENA_LUZ,
                OverlayTexture.NO_OVERLAY, estado.outlineColor, null);
        pose.popPose();
        super.submit(estado, pose, colector, camara);
    }
}
