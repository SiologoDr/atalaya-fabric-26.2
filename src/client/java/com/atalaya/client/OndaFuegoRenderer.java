package com.atalaya.client;

import com.atalaya.entity.OndaFuegoEntity;
import com.mojang.blaze3d.vertex.PoseStack;
import net.minecraft.client.renderer.SubmitNodeCollector;
import net.minecraft.client.renderer.entity.EntityRenderer;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.state.EntityRenderState;
import net.minecraft.client.renderer.state.level.CameraRenderState;
import net.minecraft.util.Mth;
import net.minecraft.world.phys.Vec3;

/**
 * La onda de fuego del Castigo solar: un muro de llamas en anillo que corre por
 * el suelo, con el suelo quemado detras. Al llegar al final se apaga. El pulso
 * de los angeles va en cuadro, como sus escalones, y solo se ve por la pisada
 * de su escalon.
 */
public class OndaFuegoRenderer extends EntityRenderer<OndaFuegoEntity, OndaFuegoRenderer.Estado> {

    public static class Estado extends EntityRenderState {
        public float edad;
        public float radio;
        public float viaje;
        public int fase;
        public boolean cuadro;
        public float desde;
        public float max;
    }

    public OndaFuegoRenderer(EntityRendererProvider.Context contexto) {
        super(contexto);
    }

    @Override
    public Estado createRenderState() {
        return new Estado();
    }

    @Override
    public void extractRenderState(OndaFuegoEntity o, Estado s, float parcial) {
        super.extractRenderState(o, s, parcial);
        s.edad = o.tickCount + parcial;
        s.radio = o.radio(s.edad);
        s.viaje = o.viaje();
        s.fase = o.getColor();
        s.cuadro = o.esCuadro();
        s.desde = o.getDesde();
        s.max = o.getMax();
    }

    @Override
    protected boolean affectedByCulling(OndaFuegoEntity o) {
        return false;
    }

    @Override
    public void submit(Estado s, PoseStack pose, SubmitNodeCollector colector, CameraRenderState camara) {
        float apaga = Mth.clamp(1.0F - (s.edad - s.viaje) / 8.0F, 0.0F, 1.0F);
        if (apaga <= 0.0F) {
            return;
        }
        if (s.cuadro) {
            cuadro(s, pose, colector, camara, apaga);
            return;
        }
        float r = Math.max(0.5F, s.radio);
        int lados = Math.max(16, (int) (r * 3.2F));
        float vueltas = Math.max(2.0F, r * 0.9F);
        float alto = OndaFuegoEntity.ALTO * (0.8F + 0.2F * Mth.sin(s.edad * 0.9F));
        int alfa = (int) (240 * apaga);
        Vec3 ojo = camara.pos.subtract(s.x, s.y, s.z);
        colector.submitCustomGeometry(pose, NovilisDibujo.llamas(s.fase), (p, buf) -> {
            NovilisDibujo.anillo(buf, p, ojo, 0, 0.02, 0, r, alto, lados, vueltas, s.edad * 0.03F, 0xFFFFFF, alfa);
            NovilisDibujo.anillo(buf, p, ojo, 0, 0.02, 0, r - 0.5F, alto * 0.7F, lados, vueltas * 0.8F, -s.edad * 0.04F, 0xFFFFFF,
                    (int) (alfa * 0.7F));
        });
        super.submit(s, pose, colector, camara);
    }

    /** El pulso de un escalon: el cuadro de llamas, solo mientras corre por su pisada (y un pelo fuera del canto). */
    private void cuadro(Estado s, PoseStack pose, SubmitNodeCollector colector, CameraRenderState camara, float apaga) {
        float r = Math.min(s.radio, s.max) + 0.05F;
        if (r < s.desde) {
            return;
        }
        float alto = OndaFuegoEntity.ALTO_PULSO * (0.8F + 0.2F * Mth.sin(s.edad * 0.9F));
        int alfa = (int) (240 * apaga);
        Vec3 ojo = camara.pos.subtract(s.x, s.y, s.z);
        colector.submitCustomGeometry(pose, NovilisDibujo.llamas(s.fase), (p, buf) -> {
            NovilisDibujo.cuadro(buf, p, ojo, 0.02, r, alto, s.edad * 0.03F, 0xFFFFFF, alfa);
            if (r - 0.35F > s.desde) {
                NovilisDibujo.cuadro(buf, p, ojo, 0.02, r - 0.35F, alto * 0.7F, -s.edad * 0.04F, 0xFFFFFF, (int) (alfa * 0.7F));
            }
        });
        super.submit(s, pose, colector, camara);
    }
}
