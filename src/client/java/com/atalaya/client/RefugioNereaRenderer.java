package com.atalaya.client;

import com.atalaya.Atalaya;
import com.atalaya.entity.RefugioNereaEntity;
import com.mojang.blaze3d.vertex.PoseStack;
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
 * Una cupula de refugio de la Marea Alta: media esfera de agua celeste apoyada
 * en el suelo (Juan: "celeste y como una cupula"), con la red de reflejos de
 * nerea_cupula.py que gira despacio y un aro de espuma donde toca el suelo. Se
 * ve por dentro y por fuera. Llena se tine de rojo. Lo que cabe ("1/2") lo pone
 * el nombre de la entidad encima.
 */
public class RefugioNereaRenderer extends EntityRenderer<RefugioNereaEntity, RefugioNereaRenderer.Estado> {

    private static final RenderType CUPULA = RenderTypes.entityTranslucent(
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "textures/entity/nerea/cupula.png"));
    /** Gajos alrededor y anillos de abajo arriba. */
    private static final int GAJOS = 32;
    private static final int ANILLOS = 10;
    /** Las veces que la textura da la vuelta. */
    private static final float VUELTAS = 4.0F;
    private static final int CELESTE = 0xFFFFFF;
    private static final int LLENA = 0xFF9A8A;

    public static class Estado extends EntityRenderState {
        public boolean llena;
        public float edad;
    }

    public RefugioNereaRenderer(EntityRendererProvider.Context contexto) {
        super(contexto);
    }

    @Override
    public Estado createRenderState() {
        return new Estado();
    }

    @Override
    public void extractRenderState(RefugioNereaEntity r, Estado s, float parcial) {
        super.extractRenderState(r, s, parcial);
        s.llena = r.getDentro() >= r.getAforo();
        s.edad = r.tickCount + parcial;
    }

    @Override
    protected boolean affectedByCulling(RefugioNereaEntity r) {
        return false;
    }

    @Override
    public void submit(Estado s, PoseStack pose, SubmitNodeCollector colector, CameraRenderState camara) {
        // Nace creciendo desde el suelo y luego respira despacio.
        float nace = Mth.clamp(s.edad / 10.0F, 0.0F, 1.0F);
        float radio = RefugioNereaEntity.RADIO * (0.2F + 0.8F * nace) * (1.0F + 0.015F * Mth.sin(s.edad * 0.25F));
        float alto = radio * nace;
        float giro = s.edad * 0.004F;
        int color = s.llena ? LLENA : CELESTE;
        int alfa = (int) (235 * nace);
        colector.submitCustomGeometry(pose, CUPULA, (p, buf) -> {
            for (int j = 0; j < ANILLOS; j++) {
                float la0 = Mth.HALF_PI * j / ANILLOS;
                float la1 = Mth.HALF_PI * (j + 1) / ANILLOS;
                float v0 = 1.0F - (float) j / ANILLOS;
                float v1 = 1.0F - (float) (j + 1) / ANILLOS;
                for (int i = 0; i < GAJOS; i++) {
                    float lo0 = Mth.TWO_PI * i / GAJOS + giro;
                    float lo1 = Mth.TWO_PI * (i + 1) / GAJOS + giro;
                    float u0 = VUELTAS * i / GAJOS;
                    float u1 = VUELTAS * (i + 1) / GAJOS;
                    punto(buf, p, radio, alto, la0, lo0, u0, v0, color, alfa);
                    punto(buf, p, radio, alto, la0, lo1, u1, v0, color, alfa);
                    punto(buf, p, radio, alto, la1, lo1, u1, v1, color, alfa);
                    punto(buf, p, radio, alto, la1, lo0, u0, v1, color, alfa);
                }
            }
        });
        colector.submitCustomGeometry(pose, NereaDibujo.ARO, (p, buf) ->
                NereaDibujo.suelo(buf, p, 0.0, 0.06, 0.0, (radio + 0.3F) / NereaDibujo.ARO_EN_TEXTURA, s.edad * 0.04F,
                        s.llena ? LLENA : 0xBFF2FF, alfa));
        super.submit(s, pose, colector, camara);
    }

    /** Un vertice de la media esfera (latitud desde el suelo, longitud alrededor). */
    private static void punto(com.mojang.blaze3d.vertex.VertexConsumer buf, PoseStack.Pose p, float radio, float alto,
                              float lat, float lon, float u, float v, int color, int alfa) {
        float c = Mth.cos(lat);
        float x = Mth.cos(lon) * c;
        float z = Mth.sin(lon) * c;
        float y = Mth.sin(lat);
        NereaDibujo.vertice(buf, p, x * radio, y * alto, z * radio, u, v, color, alfa, x, y, z);
    }
}
