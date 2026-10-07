package com.atalaya.client;

import com.atalaya.entity.CadenaNereaEntity;
import com.mojang.blaze3d.vertex.PoseStack;
import net.minecraft.client.renderer.SubmitNodeCollector;
import net.minecraft.client.renderer.entity.EntityRenderer;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.state.EntityRenderState;
import net.minecraft.client.renderer.state.level.CameraRenderState;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.phys.Vec3;
import org.jspecify.annotations.Nullable;

/**
 * La cadena de los Encadenados: los eslabones oxidados del Arpon (CadenaRender)
 * de un pecho a otro, o al ancla clavada, con un hilo de agua encima que se
 * pone rojo y tiembla cuanto mas tensa esta (al llegar a su largo, tira). En el
 * ancla, un aro de espuma en el suelo.
 */
public class CadenaNereaRenderer extends EntityRenderer<CadenaNereaEntity, CadenaNereaRenderer.Estado> {

    private static final int AGUA = 0x7FE6F2;
    private static final int TENSA = 0xFF5A4A;

    public static class Estado extends EntityRenderState {
        public @Nullable Vec3 a;
        public @Nullable Vec3 b;
        public boolean ancla;
        public float tension;
        public float edad;
    }

    public CadenaNereaRenderer(EntityRendererProvider.Context contexto) {
        super(contexto);
    }

    @Override
    public Estado createRenderState() {
        return new Estado();
    }

    @Override
    public void extractRenderState(CadenaNereaEntity c, Estado s, float parcial) {
        super.extractRenderState(c, s, parcial);
        Vec3 aqui = c.getPosition(parcial);
        s.a = pecho(c.level().getEntity(c.getIdA()), aqui, parcial);
        s.ancla = c.getIdB() < 0;
        s.b = s.ancla ? Vec3.atBottomCenterOf(c.getAncla()).add(0, 0.15, 0).subtract(aqui)
                : pecho(c.level().getEntity(c.getIdB()), aqui, parcial);
        s.tension = c.getTension();
        s.edad = c.tickCount + parcial;
    }

    private static @Nullable Vec3 pecho(@Nullable Entity e, Vec3 aqui, float parcial) {
        return e == null ? null : e.getPosition(parcial).add(0, e.getBbHeight() * 0.55, 0).subtract(aqui);
    }

    @Override
    protected boolean affectedByCulling(CadenaNereaEntity c) {
        return false;
    }

    @Override
    public void submit(Estado s, PoseStack pose, SubmitNodeCollector colector, CameraRenderState camara) {
        if (s.a == null || s.b == null) {
            return;
        }
        Vec3 a = s.a;
        Vec3 b = s.b;
        CadenaRender.dibujar(pose, colector, a, b, s.lightCoords, 0.3F);
        float k = Mth.clamp((s.tension - 0.55F) / 0.45F, 0.0F, 1.0F);
        int color = mezclar(AGUA, TENSA, k);
        float temblor = k > 0.7F ? 0.04F * Mth.sin(s.edad * 2.1F) : 0.0F;
        Vec3 ojo = camara.pos.subtract(s.x, s.y, s.z);
        float largo = (float) a.distanceTo(b);
        float v0 = -s.edad * 0.2F;
        colector.submitCustomGeometry(pose, NereaDibujo.CHORRO, (p, buf) ->
                NereaDibujo.cinta(buf, p, a, b, ojo, 0.16F + 0.08F * k + temblor, v0, v0 + largo * 0.4F, color,
                        (int) (150 + 90 * k)));
        if (s.ancla) {
            colector.submitCustomGeometry(pose, NereaDibujo.ARO, (p, buf) ->
                    NereaDibujo.suelo(buf, p, b.x, b.y - 0.08, b.z, 1.2F / NereaDibujo.ARO_EN_TEXTURA, s.edad * 0.05F, 0xFFFFFF,
                            200));
        }
        super.submit(s, pose, colector, camara);
    }

    private static int mezclar(int a, int b, float k) {
        int r = Math.round(((a >> 16) & 0xFF) * (1 - k) + ((b >> 16) & 0xFF) * k);
        int g = Math.round(((a >> 8) & 0xFF) * (1 - k) + ((b >> 8) & 0xFF) * k);
        int bl = Math.round((a & 0xFF) * (1 - k) + (b & 0xFF) * k);
        return (r << 16) | (g << 8) | bl;
    }
}
