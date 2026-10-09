package com.atalaya.client;

import com.atalaya.entity.PozaAbismoEntity;
import com.mojang.blaze3d.vertex.PoseStack;
import net.minecraft.client.renderer.SubmitNodeCollector;
import net.minecraft.client.renderer.entity.EntityRenderer;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.state.EntityRenderState;
import net.minecraft.client.renderer.state.level.CameraRenderState;
import net.minecraft.util.Mth;

/**
 * Una poza de la Pesca del Abismo: el remolino oscuro del Geiser, quieto y
 * lento, con su borde de espuma cian que late. Se abre y se cierra en un
 * momento.
 */
public class PozaAbismoRenderer extends EntityRenderer<PozaAbismoEntity, PozaAbismoRenderer.Estado> {

    public static class Estado extends EntityRenderState {
        public float edad;
        public float abre;
    }

    public PozaAbismoRenderer(EntityRendererProvider.Context contexto) {
        super(contexto);
    }

    @Override
    public Estado createRenderState() {
        return new Estado();
    }

    @Override
    public void extractRenderState(PozaAbismoEntity e, Estado s, float parcial) {
        super.extractRenderState(e, s, parcial);
        s.edad = e.tickCount + parcial;
        float abre = Mth.clamp(s.edad / PozaAbismoEntity.ABRE, 0.0F, 1.0F);
        if (e.getCierra() >= 0) {
            abre = Math.min(abre, Mth.clamp(1.0F - (s.edad - e.getCierra()) / PozaAbismoEntity.ABRE, 0.0F, 1.0F));
        }
        s.abre = abre;
    }

    @Override
    protected boolean affectedByCulling(PozaAbismoEntity e) {
        return false;
    }

    @Override
    public void submit(Estado s, PoseStack pose, SubmitNodeCollector colector, CameraRenderState camara) {
        float k = s.abre;
        if (k <= 0.01F) {
            return;
        }
        float e = s.edad;
        float radio = PozaAbismoEntity.RADIO * (0.4F + 0.6F * k) + 0.25F;
        colector.submitCustomGeometry(pose, NereaDibujo.REMOLINO, (p, buf) ->
                NereaDibujo.suelo(buf, p, 0.0, 0.05, 0.0, radio, -e * 0.03F, 0x6A8CB0, (int) (235 * k)));
        float pulso = 0.5F + 0.5F * Mth.sin(e * 0.15F);
        float m = (PozaAbismoEntity.RADIO + 0.15F) / NereaDibujo.ARO_EN_TEXTURA;
        colector.submitCustomGeometry(pose, NereaDibujo.ARO, (p, buf) ->
                NereaDibujo.suelo(buf, p, 0.0, 0.07, 0.0, m, e * 0.02F, 0x7FE8FF, (int) ((150 + 90 * pulso) * k)));
        super.submit(s, pose, colector, camara);
    }
}
