package com.atalaya.client;

import com.atalaya.entity.SelloSolEntity;
import com.mojang.blaze3d.vertex.PoseStack;
import net.minecraft.client.renderer.SubmitNodeCollector;
import net.minecraft.client.renderer.entity.EntityRenderer;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.state.EntityRenderState;
import net.minecraft.client.renderer.state.level.CameraRenderState;
import net.minecraft.util.Mth;
import net.minecraft.world.phys.Vec3;

/**
 * Un sello de sol en el suelo: gira y se aprieta mientras cuenta, y parpadea
 * mas deprisa cuanto menos queda. El del rayo, al acabar, se convierte en una
 * columna de luz que cae del cielo y deja el suelo quemado un momento.
 */
public class SelloSolRenderer extends EntityRenderer<SelloSolEntity, SelloSolRenderer.Estado> {

    public static class Estado extends EntityRenderState {
        public float edad;
        public float radio;
        public int dura;
        public int tipo;
        public int color;
    }

    public SelloSolRenderer(EntityRendererProvider.Context contexto) {
        super(contexto);
    }

    @Override
    public Estado createRenderState() {
        return new Estado();
    }

    @Override
    public void extractRenderState(SelloSolEntity e, Estado s, float parcial) {
        super.extractRenderState(e, s, parcial);
        s.edad = e.tickCount + parcial;
        s.radio = e.getRadio();
        s.dura = e.getDura();
        s.tipo = e.getTipo();
        s.color = NovilisDibujo.color(e.getColor());
    }

    @Override
    protected boolean affectedByCulling(SelloSolEntity e) {
        return false;
    }

    @Override
    public void submit(Estado s, PoseStack pose, SubmitNodeCollector colector, CameraRenderState camara) {
        float e = s.edad;
        float k = Mth.clamp(e / s.dura, 0.0F, 1.0F);
        if (e < s.dura) {
            // Entra en cinco ticks; se aprieta un poco y parpadea cada vez mas deprisa.
            float entra = Mth.clamp(e / 5.0F, 0.0F, 1.0F);
            float m = s.radio * (1.15F - 0.15F * k) * (0.6F + 0.4F * entra);
            float prisa = 0.25F + 0.9F * k;
            int alfa = (int) ((150 + 90 * (0.5F + 0.5F * Mth.sin(e * prisa))) * entra);
            float giro = e * (0.02F + 0.06F * k);
            int color = NovilisDibujo.claro(s.color, 0.1F);
            colector.submitCustomGeometry(pose, NovilisDibujo.SELLO, (p, buf) -> {
                NereaDibujo.suelo(buf, p, 0.0, 0.06, 0.0, m, giro, color, alfa);
                NereaDibujo.suelo(buf, p, 0.0, 0.08, 0.0, m * 0.55F, -giro * 1.6F, NovilisDibujo.claro(s.color, 0.5F),
                        (int) (alfa * 0.8F));
            });
        }
        if (s.tipo == SelloSolEntity.RAYO) {
            float c = e - s.dura;
            if (c > -6.0F && c < SelloSolEntity.APAGA) {
                // La columna: aparece un poco antes de pegar y se apaga despues.
                float sube = Mth.clamp((c + 6.0F) / 6.0F, 0.0F, 1.0F);
                float baja = Mth.clamp(1.0F - c / SelloSolEntity.APAGA, 0.0F, 1.0F);
                float ancho = s.radio * (0.35F + 0.5F * sube) * (0.6F + 0.4F * baja);
                int alfa = (int) (235 * Math.min(sube, baja));
                Vec3 ojo = camara.pos.subtract(s.x, s.y, s.z);
                colector.submitCustomGeometry(pose, NovilisDibujo.HAZ, (p, buf) ->
                        NovilisDibujo.haz(buf, p, new Vec3(0, 34, 0), new Vec3(0, 0, 0), ojo, ancho, -e * 0.3F, s.color, alfa));
            }
            if (c >= 0.0F && c < SelloSolEntity.APAGA) {
                float m = s.radio * 1.1F;
                int alfa = (int) (230 * (1.0F - c / SelloSolEntity.APAGA));
                colector.submitCustomGeometry(pose, NovilisDibujo.QUEMADO, (p, buf) ->
                        NereaDibujo.suelo(buf, p, 0.0, 0.07, 0.0, m, 0.0F, 0xFFFFFF, alfa));
            }
        }
        super.submit(s, pose, colector, camara);
    }
}
