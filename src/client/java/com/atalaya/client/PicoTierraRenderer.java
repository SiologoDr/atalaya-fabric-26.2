package com.atalaya.client;

import com.atalaya.Atalaya;
import com.atalaya.entity.PicoTierraEntity;
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
 * Un golpe de pinchos de la Garra Terrestre, en bloques como los pilares del
 * Terremoto: el pincho grande (tramos de roca apilados que se estrechan hasta
 * un taco en la punta) inclinado hacia donde corre la grieta, dos a cuatro
 * menores abiertos alrededor y los terrones del suelo roto. Roca parda
 * (roca.png) con sus vetas verdes encendidas (roca_brillo). Sale de golpe con
 * un rebote y al final se hunde en el suelo.
 */
public class PicoTierraRenderer extends EntityRenderer<PicoTierraEntity, PicoTierraRenderer.Estado> {

    private static final RenderType ROCA = RenderTypes.entityCutout(
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "textures/entity/rajang/roca.png"));
    private static final RenderType VETAS = RenderTypes.eyes(
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "textures/entity/rajang/roca_brillo.png"));

    public static class Estado extends EntityRenderState {
        public float edad;
        public float tam;
        public int semilla;
        public float rumbo;
        /** Uno de la Embestida: las vetas encendidas del todo (mata). */
        public boolean mortal;
    }

    public PicoTierraRenderer(EntityRendererProvider.Context contexto) {
        super(contexto);
    }

    @Override
    public Estado createRenderState() {
        return new Estado();
    }

    @Override
    public void extractRenderState(PicoTierraEntity p, Estado s, float parcial) {
        super.extractRenderState(p, s, parcial);
        s.edad = p.tickCount + parcial;
        s.tam = p.getTam();
        s.semilla = p.getSemilla();
        s.rumbo = p.getYRot();
        s.mortal = p.isMortal();
    }

    @Override
    protected boolean affectedByCulling(PicoTierraEntity p) {
        return false;
    }

    @Override
    public void submit(Estado s, PoseStack pose, SubmitNodeCollector colector, CameraRenderState camara) {
        float k = PicoTierraEntity.salida(s.edad);
        if (k <= 0.01F) {
            return;
        }
        double alto = PicoTierraEntity.ALTO * s.tam;
        List<RajangDibujo.Cara> caras = new ArrayList<>();
        Random r = new Random(s.semilla);
        double ancho = 0.5 + 1.25 * s.tam;
        RajangDibujo.pincho(caras, r, 0, 0, alto, ancho, 16 + r.nextDouble() * 10, (r.nextDouble() - 0.5) * 12);
        if (s.tam > 0.25F) {
            int n = 2 + r.nextInt(3);
            for (int i = 0; i < n; i++) {
                double a = (i + r.nextDouble() * 0.5) / n * Math.PI * 2;
                double d = ancho * (0.55 + r.nextDouble() * 0.3);
                double abre = 22 + r.nextDouble() * 18;
                RajangDibujo.pincho(caras, r, Math.cos(a) * d, Math.sin(a) * d, alto * (0.3 + r.nextDouble() * 0.3),
                        ancho * (0.45 + r.nextDouble() * 0.2), Math.sin(a) * abre, Math.cos(a) * abre);
            }
            for (int i = 0; i < 6; i++) {
                double a = r.nextDouble() * Math.PI * 2;
                double d = ancho * (0.9 + r.nextDouble() * 0.7);
                double t = ancho * (0.12 + r.nextDouble() * 0.1);
                RajangDibujo.bloque(caras, null, r, Math.cos(a) * d, t * 0.4, Math.sin(a) * d, t, t * 0.7, t, 0.2,
                        (r.nextDouble() - 0.5) * 50, r.nextDouble() * 90, (r.nextDouble() - 0.5) * 50, 12, 32, 64);
            }
        }
        pose.pushPose();
        pose.mulPose(Axis.YP.rotationDegrees(-s.rumbo));
        if (s.edad < PicoTierraEntity.SUBE) {
            pose.scale(0.8F + 0.2F * k, k, 0.8F + 0.2F * k);
        } else if (s.edad > PicoTierraEntity.DURA) {
            pose.translate(0.0, -alto * (1.0F - k), 0.0);
        }
        int luz = s.lightCoords;
        colector.submitCustomGeometry(pose, ROCA, (p, buf) -> RajangDibujo.emitir(buf, p, caras, 255, 255, 255, 255, luz));
        int brillo = (int) (255 * k);
        colector.submitCustomGeometry(pose, VETAS, (p, buf) ->
                RajangDibujo.emitir(buf, p, caras, brillo, brillo, brillo, 255, AeralisDibujo.A_PLENA_LUZ));
        if (s.mortal) {
            // Los de la Embestida matan: las vetas, el doble de encendidas.
            colector.submitCustomGeometry(pose, VETAS, (p, buf) ->
                    RajangDibujo.emitir(buf, p, caras, brillo, brillo, brillo, 255, AeralisDibujo.A_PLENA_LUZ));
        }
        pose.popPose();
        super.submit(s, pose, colector, camara);
    }
}
