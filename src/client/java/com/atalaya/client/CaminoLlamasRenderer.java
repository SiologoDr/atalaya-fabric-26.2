package com.atalaya.client;

import com.atalaya.entity.CaminoLlamasEntity;
import com.mojang.blaze3d.vertex.PoseStack;
import net.minecraft.client.renderer.SubmitNodeCollector;
import net.minecraft.client.renderer.entity.EntityRenderer;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.state.EntityRenderState;
import net.minecraft.client.renderer.rendertype.RenderType;
import net.minecraft.client.renderer.state.level.CameraRenderState;
import net.minecraft.world.phys.Vec3;

/**
 * El camino de llamas malditas de la Espada del Fuego: el suelo quemado a
 * tramos (la quemadura del Castigo, chispas_suelo.png) y tres paredes de
 * llamas a lo largo (los dos cantos y el medio), con la textura de pared del
 * color de la fase corriendo. Prende de atras hacia delante y baja al final.
 */
public class CaminoLlamasRenderer extends EntityRenderer<CaminoLlamasEntity, CaminoLlamasRenderer.Estado> {

    public static class Estado extends EntityRenderState {
        public float edad;
        public float largo;
        public float ancho;
        public float fuerza;
        public int color;
        public RenderType llamas = NovilisDibujo.LLAMAS_N;
        public Vec3 frente = new Vec3(0, 0, 1);
    }

    public CaminoLlamasRenderer(EntityRendererProvider.Context contexto) {
        super(contexto);
    }

    @Override
    public Estado createRenderState() {
        return new Estado();
    }

    @Override
    public void extractRenderState(CaminoLlamasEntity e, Estado s, float parcial) {
        super.extractRenderState(e, s, parcial);
        s.edad = e.tickCount + parcial;
        s.largo = e.encendido(s.edad);
        s.ancho = e.getAncho();
        s.fuerza = e.fuerza(s.edad);
        s.color = NovilisDibujo.color(e.getColor());
        s.llamas = NovilisDibujo.llamas(e.getColor());
        s.frente = e.frente();
    }

    @Override
    protected boolean affectedByCulling(CaminoLlamasEntity e) {
        return false;
    }

    @Override
    public void submit(Estado s, PoseStack pose, SubmitNodeCollector colector, CameraRenderState camara) {
        if (s.largo < 0.1F || s.fuerza <= 0.01F) {
            return;
        }
        Vec3 ojo = camara.pos.subtract(s.x, s.y, s.z);
        Vec3 f = s.frente;
        Vec3 izq = new Vec3(f.z, 0, -f.x);
        float k = s.fuerza;
        // El suelo quemado: cuadros de la quemadura que se pisan unos a otros.
        int alfaSuelo = (int) (225 * Math.min(1.0F, k * 1.5F));
        float m = s.ancho * 0.6F;
        colector.submitCustomGeometry(pose, NovilisDibujo.QUEMADO, (p, buf) -> {
            for (float a = m * 0.6F; a < s.largo; a += m * 1.1F) {
                Vec3 c = f.scale(a);
                NereaDibujo.suelo(buf, p, c.x, 0.05 + a * 0.0005, c.z, m, a * 1.7F, 0xFFFFFF, alfaSuelo);
            }
        });
        // Las llamas: tres paredes a lo largo, la del medio mas alta.
        float corre = -s.edad * 0.06F;
        colector.submitCustomGeometry(pose, s.llamas, (p, buf) -> {
            for (int lado = -1; lado <= 1; lado++) {
                double l = lado * s.ancho * 0.42;
                float alto = (lado == 0 ? 1.7F : 1.15F) * k;
                Vec3 q0 = izq.scale(l);
                Vec3 q1 = q0.add(f.scale(s.largo));
                Vec3 q2 = q1.add(0, alto, 0);
                Vec3 q3 = q0.add(0, alto, 0);
                float u0 = corre + lado * 0.37F;
                float u1 = u0 + s.largo / 3.0F;
                NovilisDibujo.cara(buf, p, ojo, q0, q1, q2, q3, u0, u1, 1.0F, 0.0F, 0xFFFFFF, (int) (230 * k), (int) (230 * k));
            }
        });
        super.submit(s, pose, colector, camara);
    }
}
