package com.atalaya.client;

import com.atalaya.entity.TajoNovilisEntity;
import com.mojang.blaze3d.vertex.PoseStack;
import net.minecraft.client.renderer.SubmitNodeCollector;
import net.minecraft.client.renderer.entity.EntityRenderer;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.state.EntityRenderState;
import net.minecraft.client.renderer.state.level.CameraRenderState;
import net.minecraft.util.Mth;
import net.minecraft.world.phys.Vec3;

/**
 * Una media luna de fuego del Barrido: de pie, de cara a donde vuela (se ve
 * entera viniendo hacia ti) y tumbada a la vez (se ve desde arriba), con una
 * estela detras. Se apaga al final de su vuelo.
 */
public class TajoNovilisRenderer extends EntityRenderer<TajoNovilisEntity, TajoNovilisRenderer.Estado> {

    public static class Estado extends EntityRenderState {
        public float edad;
        public float rumbo;
        public boolean grande;
        public int color;
    }

    public TajoNovilisRenderer(EntityRendererProvider.Context contexto) {
        super(contexto);
    }

    @Override
    public Estado createRenderState() {
        return new Estado();
    }

    @Override
    public void extractRenderState(TajoNovilisEntity t, Estado s, float parcial) {
        super.extractRenderState(t, s, parcial);
        s.edad = t.tickCount + parcial;
        s.rumbo = t.getYRot();
        s.grande = t.esGrande();
        s.color = NovilisDibujo.color(t.esFuria() ? 5 : t.getFase());
    }

    @Override
    protected boolean affectedByCulling(TajoNovilisEntity t) {
        return false;
    }

    @Override
    public void submit(Estado s, PoseStack pose, SubmitNodeCollector colector, CameraRenderState camara) {
        float e = s.edad;
        if (e > TajoNovilisEntity.VUELO + 4) {
            return;
        }
        float b = s.rumbo * Mth.DEG_TO_RAD;
        Vec3 dir = new Vec3(-Mth.sin(b), 0, Mth.cos(b));
        Vec3 lado = new Vec3(-dir.z, 0, dir.x);
        float avance = Math.min(TajoNovilisEntity.VEL * TajoNovilisEntity.VUELO, e * TajoNovilisEntity.VEL);
        Vec3 c = dir.scale(avance);
        float w = TajoNovilisEntity.MEDIO_ANCHO * (s.grande ? 1.5F : 1.0F) * (0.7F + 0.3F * Mth.clamp(e / 4.0F, 0, 1));
        float h = TajoNovilisEntity.ALTO * (s.grande ? 1.3F : 1.0F);
        int alfa = (int) (240 * Mth.clamp((TajoNovilisEntity.VUELO + 4 - e) / 6.0F, 0.0F, 1.0F));
        int color = NovilisDibujo.claro(s.color, 0.15F);
        Vec3 ojo = camara.pos.subtract(s.x, s.y, s.z);
        colector.submitCustomGeometry(pose, NovilisDibujo.MEDIA_LUNA, (p, buf) -> {
            // De pie, de cara a donde vuela: el lomo arriba, los cuernos abajo.
            Vec3 a0 = c.add(lado.scale(-w));
            Vec3 a1 = c.add(lado.scale(w));
            NovilisDibujo.cara(buf, p, ojo, a0, a1, a1.add(0, h, 0), a0.add(0, h, 0), 0, 1, 1, 0, color, alfa, alfa);
            // Tumbada, un poco por encima del suelo: el arco hacia delante.
            Vec3 t0 = c.add(lado.scale(-w)).add(0, 0.6, 0);
            Vec3 t1 = c.add(lado.scale(w)).add(0, 0.6, 0);
            NovilisDibujo.cara(buf, p, ojo, t0.add(dir.scale(-h * 0.5)), t1.add(dir.scale(-h * 0.5)), t1.add(dir.scale(h * 0.5)),
                    t0.add(dir.scale(h * 0.5)), 0, 1, 1, 0, color, (int) (alfa * 0.8F), (int) (alfa * 0.8F));
        });
        // La estela: una cinta de fuego desde donde nacio.
        float atras = Math.max(0.0F, avance - 6.0F);
        colector.submitCustomGeometry(pose, NovilisDibujo.ESTELA, (p, buf) ->
                NovilisDibujo.cinta(buf, p, c.add(0, h * 0.4, 0), dir.scale(atras).add(0, h * 0.4, 0), ojo, w * 0.45F, 0.0F, 1.0F,
                        s.color, (int) (alfa * 0.7F)));
        super.submit(s, pose, colector, camara);
    }
}
