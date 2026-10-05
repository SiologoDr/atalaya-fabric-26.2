package com.atalaya.client;

import com.atalaya.entity.RajangParteEntity;
import com.mojang.blaze3d.vertex.PoseStack;
import net.minecraft.client.renderer.SubmitNodeCollector;
import net.minecraft.client.renderer.entity.EntityRenderer;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.state.EntityRenderState;
import net.minecraft.client.renderer.state.level.CameraRenderState;

/** Las cajas de la cabeza y la grupa de Rajang no se ven: lo que se ve es el. */
public class RajangParteRenderer extends EntityRenderer<RajangParteEntity, EntityRenderState> {

    public RajangParteRenderer(EntityRendererProvider.Context contexto) {
        super(contexto);
    }

    @Override
    public EntityRenderState createRenderState() {
        return new EntityRenderState();
    }

    @Override
    public void submit(EntityRenderState s, PoseStack pose, SubmitNodeCollector colector, CameraRenderState camara) {
    }
}
