package com.atalaya.client;

import com.atalaya.entity.GrietaNovilisEntity;
import com.mojang.blaze3d.vertex.PoseStack;
import net.minecraft.client.renderer.SubmitNodeCollector;
import net.minecraft.client.renderer.entity.EntityRenderer;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.state.EntityRenderState;
import net.minecraft.client.renderer.rendertype.RenderType;
import net.minecraft.client.renderer.state.level.CameraRenderState;
import net.minecraft.util.Mth;
import net.minecraft.world.phys.Vec3;

/**
 * Las grietas de fuego de Novilis (GrietaNovilisEntity), teñidas del color de
 * la fase:
 *
 * <ul>
 *   <li>LINEA (Furia Infernal): la raja en el suelo (grieta.png a lo largo)
 *       que se abre de cerca a lejos y, cuando revienta, una pared de llamas
 *       que sale de toda ella.</li>
 *   <li>BOCA (Mar de Llamas): el agujero con sus grietas (grieta_boca.png),
 *       que late mas deprisa al acercarse el fuego; luego la columna de fuego:
 *       un aro de llamas por fuera y, dentro, otro mas alto y estrecho con dos
 *       lenguas cruzadas (08-10-2026: el haz del medio parecia una raya, no una
 *       llama).</li>
 * </ul>
 */
public class GrietaNovilisRenderer extends EntityRenderer<GrietaNovilisEntity, GrietaNovilisRenderer.Estado> {

    public static class Estado extends EntityRenderState {
        public float edad;
        public int tipo;
        public float tam;
        public float rumbo;
        public float abierta;
        public float fuego;
        public int aviso;
        public int color;
        public RenderType llamas = NovilisDibujo.LLAMAS_N;
        public Vec3 frente = new Vec3(0, 0, 1);
    }

    public GrietaNovilisRenderer(EntityRendererProvider.Context contexto) {
        super(contexto);
    }

    @Override
    public Estado createRenderState() {
        return new Estado();
    }

    @Override
    public void extractRenderState(GrietaNovilisEntity e, Estado s, float parcial) {
        super.extractRenderState(e, s, parcial);
        s.edad = e.tickCount + parcial;
        s.tipo = e.getTipo();
        s.tam = e.getTam();
        s.rumbo = e.getRumbo();
        s.abierta = e.abierta(s.edad);
        s.fuego = e.fuego(s.edad);
        s.aviso = e.getAviso();
        s.color = NovilisDibujo.color(e.getColor());
        s.llamas = NovilisDibujo.llamas(e.getColor());
        s.frente = e.frente();
    }

    @Override
    protected boolean affectedByCulling(GrietaNovilisEntity e) {
        return false;
    }

    @Override
    public void submit(Estado s, PoseStack pose, SubmitNodeCollector colector, CameraRenderState camara) {
        Vec3 ojo = camara.pos.subtract(s.x, s.y, s.z);
        int tinte = NovilisDibujo.claro(s.color, 0.25F);
        if (s.tipo == GrietaNovilisEntity.LINEA) {
            linea(s, pose, colector, ojo, tinte);
        } else {
            boca(s, pose, colector, ojo, tinte);
        }
        super.submit(s, pose, colector, camara);
    }

    private static void linea(Estado s, PoseStack pose, SubmitNodeCollector colector, Vec3 ojo, int tinte) {
        float largo = s.tam * s.abierta;
        if (largo < 0.1F) {
            return;
        }
        Vec3 f = s.frente;
        Vec3 izq = new Vec3(f.z, 0, -f.x);
        // Se ve entera hasta que el fuego, al final, se apaga: entonces se va con el.
        float apaga = s.edad < s.aviso + 4 ? 1.0F : s.fuego;
        int alfa = (int) (245 * apaga);
        double w = 0.95;
        colector.submitCustomGeometry(pose, NovilisDibujo.GRIETA, (p, buf) -> {
            Vec3 q0 = izq.scale(w).add(0, 0.06, 0);
            Vec3 q1 = izq.scale(-w).add(0, 0.06, 0);
            Vec3 q2 = q1.add(f.scale(largo));
            Vec3 q3 = q0.add(f.scale(largo));
            NovilisDibujo.cara(buf, p, ojo, q0, q1, q2, q3, 0.0F, 1.0F, 0.0F, largo / 4.0F, tinte, alfa, alfa);
        });
        if (s.fuego > 0.01F) {
            float alto = 2.6F * s.fuego * (0.9F + 0.1F * Mth.sin(s.edad * 0.7F));
            float corre = -s.edad * 0.09F;
            colector.submitCustomGeometry(pose, s.llamas, (p, buf) -> {
                Vec3 q0 = new Vec3(0, 0.05, 0);
                Vec3 q1 = f.scale(largo).add(0, 0.05, 0);
                Vec3 q2 = q1.add(0, alto, 0);
                Vec3 q3 = q0.add(0, alto, 0);
                NovilisDibujo.cara(buf, p, ojo, q0, q1, q2, q3, corre, corre + largo / 3.0F, 1.0F, 0.0F, 0xFFFFFF,
                        (int) (235 * s.fuego), (int) (235 * s.fuego));
            });
        }
    }

    private static void boca(Estado s, PoseStack pose, SubmitNodeCollector colector, Vec3 ojo, int tinte) {
        // El aviso: la grieta late cada vez mas deprisa hasta que sale el fuego.
        int alfa;
        if (s.fuego <= 0.0F) {
            float k = Mth.clamp(s.edad / s.aviso, 0.0F, 1.0F);
            float late = 0.5F + 0.5F * Mth.sin(s.edad * (0.3F + 0.9F * k));
            alfa = (int) ((120 + 120 * late) * Math.min(1.0F, s.edad / 4.0F));
        } else {
            alfa = (int) (245 * Math.max(0.35F, s.fuego));
        }
        float m = s.tam * (0.85F + 0.6F * s.abierta);
        float giro = s.rumbo * Mth.DEG_TO_RAD;
        colector.submitCustomGeometry(pose, NovilisDibujo.GRIETA_BOCA, (p, buf) ->
                NereaDibujo.suelo(buf, p, 0.0, 0.06, 0.0, m, giro, tinte, alfa));
        if (s.fuego <= 0.01F) {
            return;
        }
        float alto = 5.5F * s.fuego * (0.9F + 0.1F * Mth.sin(s.edad * 0.5F + s.rumbo));
        float r = s.tam * 0.7F;
        int alfaFuego = (int) (235 * s.fuego);
        colector.submitCustomGeometry(pose, s.llamas, (p, buf) -> {
            // por fuera, el aro; dentro, otro mas alto y estrecho que corre al reves
            NovilisDibujo.anillo(buf, p, ojo, 0.0, 0.05, 0.0, r, alto, 10, 2.0F, -s.edad * 0.05F, 0xFFFFFF, alfaFuego);
            NovilisDibujo.anillo(buf, p, ojo, 0.0, 0.05, 0.0, r * 0.45F, alto * 1.3F, 7, 1.0F, s.edad * 0.07F, 0xFFFFFF, alfaFuego);
            // y en medio, dos lenguas cruzadas: desde cualquier lado se ve fuego, no una raya
            for (int k = 0; k < 2; k++) {
                double a = giro + k * Math.PI / 2;
                Vec3 l = new Vec3(Math.cos(a) * r * 0.75, 0, Math.sin(a) * r * 0.75);
                Vec3 q0 = l.scale(-1).add(0, 0.05, 0);
                Vec3 q1 = l.add(0, 0.05, 0);
                float u0 = -s.edad * 0.06F + k * 0.5F;
                NovilisDibujo.cara(buf, p, ojo, q0, q1, q1.add(0, alto * 1.15, 0), q0.add(0, alto * 1.15, 0), u0, u0 + 0.7F,
                        1.0F, 0.0F, 0xFFFFFF, alfaFuego, alfaFuego);
            }
        });
    }
}
