package com.atalaya.client;

import com.atalaya.entity.GeiserNereaEntity;
import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import net.minecraft.client.renderer.SubmitNodeCollector;
import net.minecraft.client.renderer.entity.EntityRenderer;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.state.EntityRenderState;
import net.minecraft.client.renderer.state.level.CameraRenderState;
import net.minecraft.util.Mth;
import net.minecraft.world.phys.Vec3;

/**
 * Un Geiser del Abismo: mientras avisa, un remolino oscuro que se abre en el
 * suelo y gira cada vez mas deprisa, con el aro de espuma de hasta donde
 * alcanza; al reventar, una columna de agua de catorce bloques que sale de
 * golpe (y se pasa un poco), con el agua subiendo a chorro, bultos que le
 * suben por el cuerpo como borbotones, un nucleo mas claro que sube aun mas
 * deprisa y una corona de espuma arriba que se abre y cae. Al final se
 * desploma desde arriba.
 */
public class GeiserNereaRenderer extends EntityRenderer<GeiserNereaEntity, GeiserNereaRenderer.Estado> {

    private static final int LADOS = 14;
    private static final int ALTURAS = 14;

    public static class Estado extends EntityRenderState {
        public float edad;
    }

    public GeiserNereaRenderer(EntityRendererProvider.Context contexto) {
        super(contexto);
    }

    @Override
    public Estado createRenderState() {
        return new Estado();
    }

    @Override
    public void extractRenderState(GeiserNereaEntity g, Estado s, float parcial) {
        super.extractRenderState(g, s, parcial);
        s.edad = g.tickCount + parcial;
    }

    @Override
    protected boolean affectedByCulling(GeiserNereaEntity g) {
        return false;
    }

    @Override
    public void submit(Estado s, PoseStack pose, SubmitNodeCollector colector, CameraRenderState camara) {
        float aviso = GeiserNereaEntity.AVISO;
        float e = s.edad;
        // El remolino: crece y acelera mientras avisa; al reventar se borra en cinco ticks.
        float k = Mth.clamp(e / aviso, 0.0F, 1.0F);
        float sobra = Mth.clamp(1.0F - (e - aviso) / 5.0F, 0.0F, 1.0F);
        if (sobra > 0.0F) {
            float radio = GeiserNereaEntity.RADIO * (0.45F + 0.65F * k) + 0.3F;
            float giro = -(e * 0.09F + e * e * 0.006F);
            int alfa = (int) ((130 + 120 * k) * sobra);
            colector.submitCustomGeometry(pose, NereaDibujo.REMOLINO, (p, buf) ->
                    NereaDibujo.suelo(buf, p, 0.0, 0.05, 0.0, radio, giro, 0xFFFFFF, alfa));
            float pulso = 0.5F + 0.5F * Mth.sin(e * (0.4F + 0.7F * k));
            float m = GeiserNereaEntity.RADIO / NereaDibujo.ARO_EN_TEXTURA;
            colector.submitCustomGeometry(pose, NereaDibujo.ARO, (p, buf) ->
                    NereaDibujo.suelo(buf, p, 0.0, 0.07, 0.0, m, e * 0.03F, 0xFFFFFF, (int) ((110 + 120 * pulso) * k * sobra)));
        }
        float c = e - aviso;
        if (c >= 0.0F && c < GeiserNereaEntity.CHORRO + 8) {
            // Sale de golpe en tres ticks y se pasa un poco; respira mientras aguanta;
            // al final se desploma desde arriba en seis.
            float sale = Mth.clamp(c / 3.0F, 0.0F, 1.0F);
            float pasa = 1.0F + 0.15F * Mth.sin(Mth.clamp((c - 3.0F) / 6.0F, 0.0F, 1.0F) * Mth.PI);
            float cae = Mth.clamp((c - GeiserNereaEntity.CHORRO + 2) / 6.0F, 0.0F, 1.0F);
            float respira = 1.0F + 0.05F * Mth.sin(c * 0.9F);
            float alto = GeiserNereaEntity.ALTO * sale * pasa * respira * (1.0F - cae * cae);
            float alfa = 1.0F - cae * cae * cae;
            if (alto > 0.2F) {
                colector.submitCustomGeometry(pose, NereaDibujo.COLUMNA, (p, buf) -> {
                    columna(buf, p, c, alto, 1.25F, 0.9F, 0.0F, (int) (215 * alfa), 0xFFFFFF);
                    columna(buf, p, c + 5.0F, alto * 0.97F, 0.7F, 1.5F, 0.4F, (int) (235 * alfa), 0xE8FFFF);
                    corona(buf, p, c, alto, (int) (225 * alfa));
                });
            }
            // El aro de espuma que se abre en la base.
            float abre = Mth.clamp(c / 10.0F, 0.0F, 1.0F);
            float m = (GeiserNereaEntity.RADIO + 2.2F * abre) / NereaDibujo.ARO_EN_TEXTURA;
            colector.submitCustomGeometry(pose, NereaDibujo.ARO, (p, buf) ->
                    NereaDibujo.suelo(buf, p, 0.0, 0.08, 0.0, m, c * 0.05F, 0xFFFFFF, (int) (230 * (1.0F - abre) * alfa + 50 * alfa)));
        }
        super.submit(s, pose, colector, camara);
    }

    /**
     * Un cilindro de agua con los chorros subiendo (v corre hacia arriba a
     * "vel") y bultos que le suben por el cuerpo, como borbotones.
     */
    private static void columna(VertexConsumer buf, PoseStack.Pose p, float c, float alto, float radio, float vel,
                                float giro, int alfa, int color) {
        for (int j = 0; j < ALTURAS; j++) {
            float h0 = j / (float) ALTURAS;
            float h1 = (j + 1) / (float) ALTURAS;
            for (int i = 0; i < LADOS; i++) {
                float a0 = i / (float) LADOS;
                float a1 = (i + 1) / (float) LADOS;
                Vec3 q0 = anillo(c, a0, h0, alto, radio, giro);
                Vec3 q1 = anillo(c, a1, h0, alto, radio, giro);
                Vec3 q2 = anillo(c, a1, h1, alto, radio, giro);
                Vec3 q3 = anillo(c, a0, h1, alto, radio, giro);
                float v0 = -h0 * alto / 4.0F + c * vel;
                float v1 = -h1 * alto / 4.0F + c * vel;
                // Se deshace un poco arriba del todo.
                int al0 = (int) (alfa * Math.min(1.0F, (1.0F - h0) / 0.12F));
                int al1 = (int) (alfa * Math.min(1.0F, (1.0F - h1) / 0.12F));
                NereaDibujo.cuadro(buf, p, q0, q1, q2, q3, a0 * 3.0F + giro, a1 * 3.0F + giro, v0, v1, color, al0, al1);
            }
        }
    }

    private static Vec3 anillo(float c, float a, float h, float alto, float radio, float giro) {
        double ang = a * Mth.TWO_PI + giro + c * 0.05;
        // Bultos que suben (la onda corre hacia arriba con el tiempo), algo de temblor
        // de lado y, arriba, se abre como un surtidor.
        float bulto = 1.0F + 0.2F * Mth.sin(h * 12.0F - c * 1.3F) + 0.06F * Mth.sin(a * 18.0F + c * 2.1F);
        float r = radio * bulto * (1.0F + 0.9F * h * h * h);
        return new Vec3(Math.cos(ang) * r, h * alto, Math.sin(ang) * r);
    }

    /** La corona de espuma de arriba: un anillo que se abre hacia fuera y cae, y late. */
    private static void corona(VertexConsumer buf, PoseStack.Pose p, float c, float alto, int alfa) {
        float abre = 1.0F + 0.25F * Mth.sin(c * 1.1F);
        for (int i = 0; i < LADOS; i++) {
            float a0 = i / (float) LADOS;
            float a1 = (i + 1) / (float) LADOS;
            double g0 = a0 * Mth.TWO_PI + c * 0.08;
            double g1 = a1 * Mth.TWO_PI + c * 0.08;
            float rIn = 1.9F;
            float rOut0 = (3.3F + 0.5F * Mth.sin(c * 0.9F + a0 * 9.0F)) * abre;
            float rOut1 = (3.3F + 0.5F * Mth.sin(c * 0.9F + a1 * 9.0F)) * abre;
            Vec3 q0 = new Vec3(Math.cos(g0) * rIn, alto * 0.98, Math.sin(g0) * rIn);
            Vec3 q1 = new Vec3(Math.cos(g1) * rIn, alto * 0.98, Math.sin(g1) * rIn);
            Vec3 q2 = new Vec3(Math.cos(g1) * rOut1, alto * 0.84, Math.sin(g1) * rOut1);
            Vec3 q3 = new Vec3(Math.cos(g0) * rOut0, alto * 0.84, Math.sin(g0) * rOut0);
            NereaDibujo.cuadro(buf, p, q0, q1, q2, q3, a0 * 3.0F, a1 * 3.0F, c * 0.6F, c * 0.6F + 0.35F, 0xFFFFFF, alfa, alfa / 3);
        }
    }
}
