package com.atalaya.client;

import com.atalaya.entity.SolCenitEntity;
import com.mojang.blaze3d.vertex.PoseStack;
import net.minecraft.client.renderer.SubmitNodeCollector;
import net.minecraft.client.renderer.entity.EntityRenderer;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.state.EntityRenderState;
import net.minecraft.client.renderer.state.level.CameraRenderState;
import net.minecraft.util.Mth;
import net.minecraft.world.phys.Vec3;

/**
 * El sol de la Sombra del Escudo: enorme y bajo en el cielo (el mismo dibujo
 * que el sol de su espalda, mas grande), se ve desde toda la arena. Al acabar, si nadie se quemo, se apaga (se
 * encoge y se vuelve gris ceniza); si no, se desvanece.
 */
public class SolCenitRenderer extends EntityRenderer<SolCenitEntity, SolCenitRenderer.Estado> {

    /** El radio del sol (bloques): a 40 de distancia se ve como un sol de verdad, pero mas grande. */
    private static final float RADIO = 5.5F;
    private static final int CENIZA = 0x5E5048;

    public static class Estado extends EntityRenderState {
        public float edad;
        public int color;
        public float apaga;
        public boolean exito;
    }

    public SolCenitRenderer(EntityRendererProvider.Context contexto) {
        super(contexto);
    }

    @Override
    public Estado createRenderState() {
        return new Estado();
    }

    @Override
    public void extractRenderState(SolCenitEntity e, Estado s, float parcial) {
        super.extractRenderState(e, s, parcial);
        s.edad = e.tickCount + parcial;
        s.color = NovilisDibujo.color(e.getColor());
        s.exito = e.isExito();
        s.apaga = e.getFin() < 0 ? 0.0F : Mth.clamp((s.edad - e.getFin()) / SolCenitEntity.APAGA, 0.0F, 1.0F);
    }

    @Override
    protected boolean affectedByCulling(SolCenitEntity e) {
        return false;
    }

    @Override
    public void submit(Estado s, PoseStack pose, SubmitNodeCollector colector, CameraRenderState camara) {
        Vec3 ojo = camara.pos.subtract(s.x, s.y, s.z);
        float k = s.apaga;
        // Mientras sube, crece de lo que era a su espalda (2,2) a su tamano en el cielo.
        float sube = Mth.clamp(s.edad / SolCenitEntity.SUBE, 0.0F, 1.0F);
        float r = 2.2F + (RADIO - 2.2F) * sube * sube * (3 - 2 * sube);
        int color = s.color;
        int alfa = (int) (245 * (1.0F - k));
        if (s.exito && k > 0.0F) {
            // Apagado: se encoge y se vuelve ceniza antes de irse.
            r *= 1.0F - 0.55F * k;
            color = mezcla(s.color, CENIZA, Math.min(1.0F, k * 2.0F));
            alfa = (int) (245 * (1.0F - k * k));
        } else if (k > 0.0F) {
            r *= 1.0F + 0.3F * k;
        }
        if (alfa < 4) {
            return;
        }
        float radio = r;
        int c = color;
        int a = alfa;
        float edad = s.edad;
        colector.submitCustomGeometry(pose, NovilisDibujo.SOL, (p, buf) -> NovilisDibujo.sol(buf, p, Vec3.ZERO, ojo, radio, edad, c, a));
        super.submit(s, pose, colector, camara);
    }

    private static int mezcla(int a, int b, float k) {
        int r = (int) Mth.lerp(k, (a >> 16) & 255, (b >> 16) & 255);
        int g = (int) Mth.lerp(k, (a >> 8) & 255, (b >> 8) & 255);
        int z = (int) Mth.lerp(k, a & 255, b & 255);
        return (r << 16) | (g << 8) | z;
    }
}
