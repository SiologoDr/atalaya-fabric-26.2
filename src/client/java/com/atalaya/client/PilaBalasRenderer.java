package com.atalaya.client;

import com.atalaya.entity.PilaBalasEntity;
import com.mojang.blaze3d.vertex.PoseStack;
import net.minecraft.client.renderer.SubmitNodeCollector;
import net.minecraft.client.renderer.entity.EntityRenderer;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.state.EntityRenderState;
import net.minecraft.client.renderer.state.level.CameraRenderState;
import net.minecraft.util.Mth;
import net.minecraft.world.phys.Vec3;

/**
 * La pila de balas de un Canon del Naufragio: una piramide de balas de hierro
 * redondas (3 x 3, 2 x 2 y una), cada una apoyada en el hueco de las de abajo
 * y girada a su manera, sobre unas tablas podridas. Sale del suelo con el canon.
 */
public class PilaBalasRenderer extends EntityRenderer<PilaBalasEntity, PilaBalasRenderer.Estado> {

    private static final double R = 0.17;

    public static class Estado extends EntityRenderState {
        public float sale;
        public int semilla;
    }

    public PilaBalasRenderer(EntityRendererProvider.Context contexto) {
        super(contexto);
    }

    @Override
    public Estado createRenderState() {
        return new Estado();
    }

    @Override
    public void extractRenderState(PilaBalasEntity e, Estado s, float parcial) {
        super.extractRenderState(e, s, parcial);
        s.sale = Mth.clamp((e.tickCount + parcial) / 20.0F, 0.0F, 1.0F);
        s.semilla = e.getId();
    }

    @Override
    public void submit(Estado s, PoseStack pose, SubmitNodeCollector colector, CameraRenderState camara) {
        int luz = s.lightCoords;
        double baja = -1.0 * (1.0 - s.sale);
        // Las tablas.
        colector.submitCustomGeometry(pose, CajaDibujo.SOLIDO, (p, buf) -> {
            for (int i = -1; i <= 1; i++) {
                CajaDibujo.caja(buf, p, new Vec3(i * 0.24, baja + 0.03, 0), 0.11, 0.03, 0.42, i == 0 ? 0x4A3420 : 0x3A2818, luz);
            }
        });
        colector.submitCustomGeometry(pose, BalaDibujo.HIERRO, (p, buf) -> {
            java.util.Random r = new java.util.Random(s.semilla);
            // Cada capa se apoya en el hueco que dejan cuatro de abajo: sube R * raiz de 2.
            double sube = R * Math.sqrt(2.0);
            for (int capa = 0; capa < 3; capa++) {
                int n = 3 - capa;
                double y = baja + 0.06 + R + capa * sube;
                for (int i = 0; i < n; i++) {
                    for (int j = 0; j < n; j++) {
                        double x = (i - (n - 1) / 2.0) * R * 2.02;
                        double z = (j - (n - 1) / 2.0) * R * 2.02;
                        BalaDibujo.bola(buf, p, new Vec3(x, y, z), R, r.nextFloat() * 6.3F, r.nextFloat() * 6.3F, luz);
                    }
                }
            }
        });
        super.submit(s, pose, colector, camara);
    }
}
