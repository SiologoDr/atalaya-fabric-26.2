package com.atalaya.client;

import com.atalaya.Atalaya;
import com.atalaya.entity.AltarIdoloEntity;
import com.atalaya.item.AtalayaItems;
import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.math.Axis;
import net.minecraft.client.renderer.SubmitNodeCollector;
import net.minecraft.client.renderer.entity.EntityRenderer;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.state.EntityRenderState;
import net.minecraft.client.renderer.item.ItemModelResolver;
import net.minecraft.client.renderer.item.ItemStackRenderState;
import net.minecraft.client.renderer.rendertype.RenderType;
import net.minecraft.client.renderer.rendertype.RenderTypes;
import net.minecraft.client.renderer.state.level.CameraRenderState;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.resources.Identifier;
import net.minecraft.world.item.ItemDisplayContext;
import net.minecraft.world.item.ItemStack;
import org.jspecify.annotations.Nullable;

import java.util.ArrayList;
import java.util.List;

/**
 * El pilar del altar del Idolo de Oro: zocalo de jade, fuste de jade con el
 * jaguar tallado en oro (altar_pilar.png, de idolo_oro.py) y capitel de oro con
 * el hueco del idolo. Las vetas de oro brillan (altar_pilar_brillo.png). Sale del
 * suelo y, con el idolo puesto, lo pinta encima (el mismo modelo 3D del objeto).
 */
public class AltarIdoloRenderer extends EntityRenderer<AltarIdoloEntity, AltarIdoloRenderer.Estado> {

    private static final RenderType PIEDRA = RenderTypes.entityCutout(tex("altar_pilar"));
    private static final RenderType VETAS = RenderTypes.eyes(tex("altar_pilar_brillo"));
    /** El pilar entero, en bloques y con la UV de su textura de 64 x 64 (un pixel por dieciseisavo). */
    private static final List<RajangDibujo.Cara> CARAS = new ArrayList<>();
    /** El idolo encima: un poco menor que un bloque, como en el capitel. */
    private static final float IDOLO = 0.8F;

    static {
        double z = 23.0 / 32.0;
        double f = 0.5;
        double c = 21.0 / 32.0;
        double y1 = 4.0 / 16.0;
        double y2 = y1 + 13.0 / 16.0;
        double y3 = y2 + 4.0 / 16.0;
        RajangDibujo.caja(CARAS, -z, 0, -z, z, y1, z, uv(0, 16, 23, 20), uv(24, 24, 47, 47));
        RajangDibujo.caja(CARAS, -f, y1, -f, f, y2, f, uv(0, 0, 16, 13), uv(24, 24, 47, 47));
        RajangDibujo.caja(CARAS, -c, y2, -c, c, y3, c, uv(0, 24, 21, 28), uv(24, 0, 45, 21));
    }

    private static Identifier tex(String nombre) {
        return Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "textures/entity/rajang/" + nombre + ".png");
    }

    private static float[] uv(int u0, int v0, int u1, int v1) {
        return RajangDibujo.uv(u0 / 64.0F, v0 / 64.0F, u1 / 64.0F, v1 / 64.0F);
    }

    public static class Estado extends EntityRenderState {
        public float salida;
        public float rumbo;
        public boolean conIdolo;
        public final ItemStackRenderState idolo = new ItemStackRenderState();
    }

    private final ItemModelResolver modelos;
    /** El idolo que se pone encima (se hace al usarlo: al crear el renderer aun no hay componentes). */
    private @Nullable ItemStack idolo;

    public AltarIdoloRenderer(EntityRendererProvider.Context contexto) {
        super(contexto);
        this.modelos = contexto.getItemModelResolver();
    }

    @Override
    public Estado createRenderState() {
        return new Estado();
    }

    @Override
    public void extractRenderState(AltarIdoloEntity a, Estado s, float parcial) {
        super.extractRenderState(a, s, parcial);
        s.salida = a.salida(parcial);
        s.rumbo = a.getYRot();
        s.conIdolo = a.conIdolo();
        if (s.conIdolo) {
            if (idolo == null) {
                idolo = new ItemStack(AtalayaItems.IDOLO_ORO);
            }
            modelos.updateForNonLiving(s.idolo, idolo, ItemDisplayContext.FIXED, a);
        }
    }

    @Override
    public void submit(Estado s, PoseStack pose, SubmitNodeCollector colector, CameraRenderState camara) {
        if (s.salida > 0.01F) {
            pose.pushPose();
            pose.translate(0.0, -AltarIdoloEntity.ALTO * (1.0F - s.salida), 0.0);
            pose.mulPose(Axis.YP.rotationDegrees(180.0F - s.rumbo));
            int luz = s.lightCoords;
            colector.submitCustomGeometry(pose, PIEDRA, (p, buf) -> RajangDibujo.emitir(buf, p, CARAS, 255, 255, 255, 255, luz));
            colector.submitCustomGeometry(pose, VETAS, (p, buf) ->
                    RajangDibujo.emitir(buf, p, CARAS, 220, 220, 220, 255, AeralisDibujo.A_PLENA_LUZ));
            if (s.conIdolo) {
                pose.translate(0.0, AltarIdoloEntity.ALTO + IDOLO * 0.5F, 0.0);
                pose.scale(IDOLO, IDOLO, IDOLO);
                s.idolo.submit(pose, colector, AeralisDibujo.A_PLENA_LUZ, OverlayTexture.NO_OVERLAY, 0);
            }
            pose.popPose();
        }
        super.submit(s, pose, colector, camara);
    }
}
