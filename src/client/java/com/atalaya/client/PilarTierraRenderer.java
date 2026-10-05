package com.atalaya.client;

import com.atalaya.Atalaya;
import com.atalaya.entity.PilarTierraEntity;
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

import java.util.ArrayList;
import java.util.List;
import java.util.Random;

/**
 * Un grupo de pilares del Terremoto Ancestral: el grande en el centro y dos a
 * cuatro menores alrededor, cada uno una torre de bloques de roca algo
 * torcidos con la punta en esquirla. Mientras avisa no se ve (el aviso es el
 * hexagono del suelo); luego revienta con rebote y al final se hunde.
 */
public class PilarTierraRenderer extends EntityRenderer<PilarTierraEntity, PilarTierraRenderer.Estado> {

    private static final RenderType ROCA = RenderTypes.entityCutout(
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "textures/entity/rajang/roca.png"));
    private static final RenderType VETAS = RenderTypes.eyes(
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "textures/entity/rajang/roca_brillo.png"));

    public static class Estado extends EntityRenderState {
        public float edad;
        public float tam;
        public int semilla;
        public int aviso;
        public float rumbo;
    }

    public PilarTierraRenderer(EntityRendererProvider.Context contexto) {
        super(contexto);
    }

    @Override
    public Estado createRenderState() {
        return new Estado();
    }

    @Override
    public void extractRenderState(PilarTierraEntity p, Estado s, float parcial) {
        super.extractRenderState(p, s, parcial);
        s.edad = p.tickCount + parcial;
        s.tam = p.getTam();
        s.semilla = p.getSemilla();
        s.aviso = p.getAviso();
        s.rumbo = p.getYRot();
    }

    @Override
    protected boolean affectedByCulling(PilarTierraEntity p) {
        return false;
    }

    @Override
    public void submit(Estado s, PoseStack pose, SubmitNodeCollector colector, CameraRenderState camara) {
        float k = PilarTierraEntity.salida(s.edad, s.aviso);
        if (k <= 0.01F) {
            return;
        }
        double alto = PilarTierraEntity.ALTO * s.tam;
        double ancho = 1.5 + 0.5 * s.tam;
        List<RajangDibujo.Cara> caras = new ArrayList<>();
        Random r = new Random(s.semilla);
        RajangDibujo.pilar(caras, r, 0, 0, alto, ancho);
        int n = 2 + r.nextInt(3);
        for (int i = 0; i < n; i++) {
            double a = r.nextDouble() * Math.PI * 2;
            double d = ancho * (0.85 + r.nextDouble() * 0.45);
            RajangDibujo.pilar(caras, r, Math.cos(a) * d, Math.sin(a) * d, alto * (0.4 + r.nextDouble() * 0.4),
                    ancho * (0.6 + r.nextDouble() * 0.3));
        }
        for (int i = 0; i < 7; i++) {
            double a = r.nextDouble() * Math.PI * 2;
            double d = ancho * (1.5 + r.nextDouble() * 0.8);
            RajangDibujo.roca(caras, r, Math.cos(a) * d, 0.12, Math.sin(a) * d, 0.2 + r.nextDouble() * 0.25, 0.8,
                    r.nextDouble() * 60 - 30, r.nextDouble() * 360, r.nextDouble() * 60 - 30);
        }
        float sube = s.edad - s.aviso;
        pose.pushPose();
        pose.mulPose(Axis.YP.rotationDegrees(-s.rumbo));
        if (sube < PilarTierraEntity.SUBE) {
            pose.translate(0.0, -alto * (1.0F - k), 0.0);
        } else if (sube > PilarTierraEntity.DURA) {
            pose.translate(0.0, -alto * (1.0F - k), 0.0);
        }
        int luz = s.lightCoords;
        colector.submitCustomGeometry(pose, ROCA, (p, buf) -> RajangDibujo.emitir(buf, p, caras, 255, 255, 255, 255, luz));
        colector.submitCustomGeometry(pose, VETAS, (p, buf) ->
                RajangDibujo.emitir(buf, p, caras, 200, 200, 200, 255, AeralisDibujo.A_PLENA_LUZ));
        pose.popPose();
        super.submit(s, pose, colector, camara);
    }
}
