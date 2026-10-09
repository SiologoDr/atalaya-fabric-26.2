package com.atalaya.client;

import com.atalaya.entity.BalaCanonEntity;
import com.mojang.blaze3d.vertex.PoseStack;
import net.minecraft.client.renderer.SubmitNodeCollector;
import net.minecraft.client.renderer.entity.EntityRenderer;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.state.EntityRenderState;
import net.minecraft.client.renderer.state.level.CameraRenderState;
import net.minecraft.world.phys.Vec3;

/**
 * La bala de un Canon del Naufragio en vuelo: una bola de hierro redonda
 * (BalaDibujo) que gira sobre si misma al volar; la estela de humo la echa la
 * entidad. Algo mas grande que la de la pila, para seguirla con la vista.
 */
public class BalaCanonRenderer extends EntityRenderer<BalaCanonEntity, BalaCanonRenderer.Estado> {

    public static class Estado extends EntityRenderState {
        public float edad;
    }

    public BalaCanonRenderer(EntityRendererProvider.Context contexto) {
        super(contexto);
    }

    @Override
    public Estado createRenderState() {
        return new Estado();
    }

    @Override
    public void extractRenderState(BalaCanonEntity e, Estado s, float parcial) {
        super.extractRenderState(e, s, parcial);
        s.edad = e.tickCount + parcial;
    }

    @Override
    protected boolean affectedByCulling(BalaCanonEntity e) {
        return false;
    }

    @Override
    public void submit(Estado s, PoseStack pose, SubmitNodeCollector colector, CameraRenderState camara) {
        int luz = s.lightCoords;
        float g = s.edad;
        colector.submitCustomGeometry(pose, BalaDibujo.HIERRO, (p, buf) ->
                BalaDibujo.bola(buf, p, new Vec3(0, 0.15, 0), 0.3, g * 0.3F, g * 0.45F, luz));
        super.submit(s, pose, colector, camara);
    }
}
