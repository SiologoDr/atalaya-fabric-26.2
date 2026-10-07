package com.atalaya.client;

import com.atalaya.Atalaya;
import com.atalaya.entity.EstradoNovilisEntity;
import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import net.minecraft.client.renderer.SubmitNodeCollector;
import net.minecraft.client.renderer.entity.EntityRenderer;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.state.EntityRenderState;
import net.minecraft.client.renderer.rendertype.RenderType;
import net.minecraft.client.renderer.rendertype.RenderTypes;
import net.minecraft.client.renderer.state.level.CameraRenderState;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.resources.Identifier;

/**
 * Un escalon del estrado de un angel: una losa de marmol (estrado_cima arriba,
 * estrado_lado en los cantos, que se repite cada dos bloques) del tamano de su
 * caja, que crece desde el suelo a la vez que el angel. Con la luz del mundo:
 * es piedra, no brilla.
 */
public class EstradoNovilisRenderer extends EntityRenderer<EstradoNovilisEntity, EstradoNovilisRenderer.Estado> {

    private static final RenderType CIMA = RenderTypes.entityCutout(Identifier.fromNamespaceAndPath(Atalaya.MOD_ID,
            "textures/entity/novilis/estrado_cima.png"));
    private static final RenderType LADO = RenderTypes.entityCutout(Identifier.fromNamespaceAndPath(Atalaya.MOD_ID,
            "textures/entity/novilis/estrado_lado.png"));

    public static class Estado extends EntityRenderState {
        public float ancho = 1.0F;
        public float alto = 1.0F;
    }

    public EstradoNovilisRenderer(EntityRendererProvider.Context contexto) {
        super(contexto);
    }

    @Override
    public Estado createRenderState() {
        return new Estado();
    }

    @Override
    public void extractRenderState(EstradoNovilisEntity e, Estado s, float parcial) {
        super.extractRenderState(e, s, parcial);
        s.ancho = e.getAncho();
        s.alto = e.getAlto() * e.salida(parcial);
    }

    @Override
    protected boolean affectedByCulling(EstradoNovilisEntity e) {
        return false;
    }

    @Override
    public void submit(Estado s, PoseStack pose, SubmitNodeCollector colector, CameraRenderState camara) {
        if (s.alto > 0.01F) {
            float m = s.ancho / 2.0F;
            float h = s.alto;
            int luz = s.lightCoords;
            // La losa de arriba, entera; un pelo por encima para que no se pelee con la de abajo.
            float yc = h + 0.002F;
            colector.submitCustomGeometry(pose, CIMA, (p, buf) -> {
                vertice(buf, p, -m, yc, -m, 0, 0, luz, 0, 1, 0);
                vertice(buf, p, -m, yc, m, 0, 1, luz, 0, 1, 0);
                vertice(buf, p, m, yc, m, 1, 1, luz, 0, 1, 0);
                vertice(buf, p, m, yc, -m, 1, 0, luz, 0, 1, 0);
            });
            // Los cuatro cantos: la textura se repite cada dos bloques de ancho, y de arriba abajo cada dos de alto.
            float u = s.ancho / 2.0F;
            float v = h / 2.0F;
            colector.submitCustomGeometry(pose, LADO, (p, buf) -> {
                // norte (-z)
                vertice(buf, p, m, h, -m, 0, 0, luz, 0, 0, -1);
                vertice(buf, p, m, 0, -m, 0, v, luz, 0, 0, -1);
                vertice(buf, p, -m, 0, -m, u, v, luz, 0, 0, -1);
                vertice(buf, p, -m, h, -m, u, 0, luz, 0, 0, -1);
                // sur (+z)
                vertice(buf, p, -m, h, m, 0, 0, luz, 0, 0, 1);
                vertice(buf, p, -m, 0, m, 0, v, luz, 0, 0, 1);
                vertice(buf, p, m, 0, m, u, v, luz, 0, 0, 1);
                vertice(buf, p, m, h, m, u, 0, luz, 0, 0, 1);
                // oeste (-x)
                vertice(buf, p, -m, h, -m, 0, 0, luz, -1, 0, 0);
                vertice(buf, p, -m, 0, -m, 0, v, luz, -1, 0, 0);
                vertice(buf, p, -m, 0, m, u, v, luz, -1, 0, 0);
                vertice(buf, p, -m, h, m, u, 0, luz, -1, 0, 0);
                // este (+x)
                vertice(buf, p, m, h, m, 0, 0, luz, 1, 0, 0);
                vertice(buf, p, m, 0, m, 0, v, luz, 1, 0, 0);
                vertice(buf, p, m, 0, -m, u, v, luz, 1, 0, 0);
                vertice(buf, p, m, h, -m, u, 0, luz, 1, 0, 0);
            });
        }
        super.submit(s, pose, colector, camara);
    }

    private static void vertice(VertexConsumer buf, PoseStack.Pose p, float x, float y, float z, float u, float v, int luz,
                                float nx, float ny, float nz) {
        buf.addVertex(p, x, y, z)
                .setColor(255, 255, 255, 255)
                .setUv(u, v)
                .setOverlay(OverlayTexture.NO_OVERLAY)
                .setLight(luz)
                .setNormal(p, nx, ny, nz);
    }
}
