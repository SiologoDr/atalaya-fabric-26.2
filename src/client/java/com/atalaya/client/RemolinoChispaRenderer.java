package com.atalaya.client;

import com.atalaya.Atalaya;
import com.atalaya.entity.RemolinoChispaEntity;
import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import net.minecraft.client.renderer.SubmitNodeCollector;
import net.minecraft.client.renderer.entity.EntityRenderer;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.state.EntityRenderState;
import net.minecraft.client.renderer.rendertype.RenderType;
import net.minecraft.client.renderer.rendertype.RenderTypes;
import net.minecraft.client.renderer.state.level.CameraRenderState;
import net.minecraft.resources.Identifier;
import net.minecraft.util.Mth;
import net.minecraft.world.phys.Vec3;

/**
 * Un remolino de La Chispa, jugando solo (aeralis_minijuegos.py, remolino.png):
 * un torbellino estrecho abajo y ancho arriba, de rachas claras que suben
 * girando (cuatro cuadros que se suceden), de cara a quien mira y girando solo
 * alrededor del eje Y, como un poste. Entra creciendo desde el suelo; las motas
 * de viento las echa la entidad.
 */
public class RemolinoChispaRenderer extends EntityRenderer<RemolinoChispaEntity, RemolinoChispaRenderer.Estado> {

    private static final RenderType REMOLINO = RenderTypes.entityTranslucentEmissive(
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "textures/entity/aeralis/remolino.png"));
    private static final float ANCHO = 0.85F;
    private static final float ALTO = 2.8F;

    public static class Estado extends EntityRenderState {
        public float edad;
    }

    public RemolinoChispaRenderer(EntityRendererProvider.Context contexto) {
        super(contexto);
    }

    @Override
    public Estado createRenderState() {
        return new Estado();
    }

    @Override
    public void extractRenderState(RemolinoChispaEntity r, Estado s, float parcial) {
        super.extractRenderState(r, s, parcial);
        s.edad = r.tickCount + parcial;
    }

    @Override
    public void submit(Estado s, PoseStack pose, SubmitNodeCollector colector, CameraRenderState camara) {
        Vec3 ojo = camara.pos.subtract(s.x, s.y, s.z);
        float entra = Mth.clamp(s.edad / 10.0F, 0.0F, 1.0F);
        float u0 = (((int) (s.edad / 2)) % 4) * 0.25F;
        int alfa = (int) (220 * entra);
        float alto = ALTO * (0.3F + 0.7F * entra);
        float ancho = ANCHO * (1.0F + 0.05F * Mth.sin(s.edad * 0.7F));
        colector.submitCustomGeometry(pose, REMOLINO, (p, buf) -> tira(buf, p, ojo, ancho, alto, u0, alfa));
        super.submit(s, pose, colector, camara);
    }

    /** Una tira vertical de cara a quien mira (gira solo alrededor del eje Y). */
    private static void tira(VertexConsumer buf, PoseStack.Pose p, Vec3 ojo, float ancho, float alto, float u0, int alfa) {
        Vec3 d = new Vec3(ojo.x, 0, ojo.z);
        // La derecha de quien mira (asi las cuatro esquinas van en el sentido de la cara de delante).
        Vec3 der = d.lengthSqr() < 1.0E-6 ? new Vec3(1, 0, 0) : new Vec3(d.z, 0, -d.x).normalize();
        double ax = der.x * ancho;
        double az = der.z * ancho;
        float u1 = u0 + 0.25F;
        NereaDibujo.vertice(buf, p, -ax, 0.0, -az, u0, 1.0F, 0xFFFFFF, alfa, 0, 1, 0);
        NereaDibujo.vertice(buf, p, ax, 0.0, az, u1, 1.0F, 0xFFFFFF, alfa, 0, 1, 0);
        NereaDibujo.vertice(buf, p, ax, alto, az, u1, 0.0F, 0xFFFFFF, alfa, 0, 1, 0);
        NereaDibujo.vertice(buf, p, -ax, alto, -az, u0, 0.0F, 0xFFFFFF, alfa, 0, 1, 0);
    }
}
