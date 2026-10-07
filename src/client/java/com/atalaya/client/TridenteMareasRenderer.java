package com.atalaya.client;

import com.atalaya.entity.TridenteMareasEntity;
import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.math.Axis;
import net.minecraft.client.renderer.SubmitNodeCollector;
import net.minecraft.client.renderer.entity.EntityRenderer;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.state.EntityRenderState;
import net.minecraft.client.renderer.item.ItemModelResolver;
import net.minecraft.client.renderer.item.ItemStackRenderState;
import net.minecraft.client.renderer.state.level.CameraRenderState;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.world.item.ItemDisplayContext;

/**
 * El Tridente de las Mareas en vuelo: el mismo dibujo grande que se ve en la
 * mano (el de armaduras_iconos.py), orientado con las puntas hacia donde va,
 * como el tridente de vanilla.
 */
public class TridenteMareasRenderer extends EntityRenderer<TridenteMareasEntity, TridenteMareasRenderer.Estado> {

    private final ItemModelResolver modelos;

    public static class Estado extends EntityRenderState {
        public final ItemStackRenderState objeto = new ItemStackRenderState();
        public float rumbo;
        public float cabeceo;
    }

    public TridenteMareasRenderer(EntityRendererProvider.Context contexto) {
        super(contexto);
        this.modelos = contexto.getItemModelResolver();
    }

    @Override
    public Estado createRenderState() {
        return new Estado();
    }

    @Override
    public void extractRenderState(TridenteMareasEntity t, Estado s, float parcial) {
        super.extractRenderState(t, s, parcial);
        s.rumbo = t.getYRot(parcial);
        s.cabeceo = t.getXRot(parcial);
        modelos.updateForNonLiving(s.objeto, t.getWeaponItem(), ItemDisplayContext.NONE, t);
    }

    @Override
    public void submit(Estado s, PoseStack pose, SubmitNodeCollector colector, CameraRenderState camara) {
        pose.pushPose();
        // Como el de vanilla: el eje largo hacia donde vuela...
        pose.mulPose(Axis.YP.rotationDegrees(s.rumbo - 90.0F));
        pose.mulPose(Axis.ZP.rotationDegrees(s.cabeceo + 90.0F));
        // ...y el dibujo, que va en diagonal con las puntas arriba a la derecha:
        // girado para que miren a -Y, que es lo que los giros de arriba llevan
        // hacia donde vuela (como las puntas del modelo de vanilla).
        pose.mulPose(Axis.ZP.rotationDegrees(-135.0F));
        pose.scale(1.4F, 1.4F, 1.4F);
        s.objeto.submit(pose, colector, s.lightCoords, OverlayTexture.NO_OVERLAY, s.outlineColor);
        pose.popPose();
        super.submit(s, pose, colector, camara);
    }
}
