package com.atalaya.client;

import com.atalaya.Atalaya;
import com.atalaya.entity.NucleoVientoEntity;
import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.math.Axis;
import net.minecraft.client.renderer.SubmitNodeCollector;
import net.minecraft.client.renderer.entity.EntityRenderer;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.state.EntityRenderState;
import net.minecraft.client.renderer.rendertype.RenderType;
import net.minecraft.client.renderer.rendertype.RenderTypes;
import net.minecraft.client.renderer.state.level.CameraRenderState;
import net.minecraft.resources.Identifier;
import net.minecraft.util.Mth;

/**
 * Un nucleo de viento: un cristal de cielo (nucleo.png) que gira en dos ejes,
 * flotando y subiendo y bajando, dentro de una cascara de luz (nucleo_brillo)
 * que gira al reves. Con cada golpe destella y se encoge un poco; cuanto mas
 * dano lleva, mas tiembla la cascara. Una columna de luz sube al cielo desde
 * el: con 30 o 40 jugadores, hay que encontrarlos rapido.
 */
public class NucleoVientoRenderer extends EntityRenderer<NucleoVientoEntity, NucleoVientoRenderer.Estado> {

    private static final RenderType CRISTAL = RenderTypes.entityTranslucent(
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "textures/entity/aeralis/nucleo.png"));
    private static final RenderType COLUMNA = RenderTypes.entityTranslucentEmissive(
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "textures/entity/aeralis/tornado.png"));
    private static final RenderType BRILLO = RenderTypes.eyes(
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "textures/entity/aeralis/nucleo_brillo.png"));

    public static class Estado extends EntityRenderState {
        public float edad;
        public float destello;
        public float dano;
    }

    public NucleoVientoRenderer(EntityRendererProvider.Context contexto) {
        super(contexto);
    }

    @Override
    public Estado createRenderState() {
        return new Estado();
    }

    @Override
    public void extractRenderState(NucleoVientoEntity n, Estado s, float parcial) {
        super.extractRenderState(n, s, parcial);
        s.edad = n.tickCount + parcial;
        s.destello = Mth.clamp(1.0F - (n.tickCount + parcial - n.ultimoGolpe) / 6.0F, 0.0F, 1.0F);
        s.dano = n.getGolpes() / (float) Math.max(1, n.getAguanta());
    }

    @Override
    protected boolean affectedByCulling(NucleoVientoEntity n) {
        return false;
    }

    @Override
    public void submit(Estado s, PoseStack pose, SubmitNodeCollector colector, CameraRenderState camara) {
        // La columna de luz que sube al cielo: se ve desde toda la arena.
        float r = 0.35F + 0.1F * s.destello;
        float v0 = -s.edad * 0.05F;
        colector.submitCustomGeometry(pose, COLUMNA, (p, buf) -> {
            float alto = 36.0F;
            for (int k = 0; k < 2; k++) {
                float ax = k == 0 ? r : 0.0F;
                float az = k == 0 ? 0.0F : r;
                float v1 = v0 + 6.0F;
                AeralisDibujo.vertice(buf, p, -ax, 0.8, -az, 0.0F, v0, 150, 225, 255, 200, AeralisDibujo.A_PLENA_LUZ, 0, 1, 0);
                AeralisDibujo.vertice(buf, p, ax, 0.8, az, 1.0F, v0, 150, 225, 255, 200, AeralisDibujo.A_PLENA_LUZ, 0, 1, 0);
                AeralisDibujo.vertice(buf, p, ax, alto, az, 1.0F, v1, 150, 225, 255, 0, AeralisDibujo.A_PLENA_LUZ, 0, 1, 0);
                AeralisDibujo.vertice(buf, p, -ax, alto, -az, 0.0F, v1, 150, 225, 255, 0, AeralisDibujo.A_PLENA_LUZ, 0, 1, 0);
            }
        });
        pose.pushPose();
        pose.translate(0.0F, 0.8F + 0.2F * Mth.sin(s.edad * 0.12F), 0.0F);
        pose.pushPose();
        pose.mulPose(Axis.YP.rotation(s.edad * 0.08F));
        pose.mulPose(Axis.XP.rotation(0.6F + s.edad * 0.05F));
        float m = 0.75F * (1.0F - 0.15F * s.destello);
        colector.submitCustomGeometry(pose, CRISTAL, (p, buf) ->
                AeralisDibujo.cubo(buf, p, m, 255, 255, 255, 235, AeralisDibujo.A_PLENA_LUZ));
        pose.popPose();
        pose.mulPose(Axis.YP.rotation(-s.edad * 0.11F));
        pose.mulPose(Axis.ZP.rotation(0.8F - s.edad * 0.04F));
        float tiembla = s.dano > 0.5F ? 0.04F * Mth.sin(s.edad * 3.1F) * s.dano : 0.0F;
        float h = 1.1F + tiembla + 0.15F * s.destello;
        int luz = (int) (150 + 105 * s.destello);
        colector.submitCustomGeometry(pose, BRILLO, (p, buf) ->
                AeralisDibujo.cubo(buf, p, h, luz, luz, luz, 255, AeralisDibujo.A_PLENA_LUZ));
        pose.popPose();
        super.submit(s, pose, colector, camara);
    }
}
