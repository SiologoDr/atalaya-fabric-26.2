package com.atalaya.client;

import com.atalaya.Atalaya;
import com.atalaya.entity.TrampaOroEntity;
import com.mojang.blaze3d.vertex.PoseStack;
import java.util.ArrayList;
import java.util.List;
import net.minecraft.client.renderer.SubmitNodeCollector;
import net.minecraft.client.renderer.entity.EntityRenderer;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.state.EntityRenderState;
import net.minecraft.client.renderer.rendertype.RenderType;
import net.minecraft.client.renderer.rendertype.RenderTypes;
import net.minecraft.client.renderer.state.level.CameraRenderState;
import net.minecraft.resources.Identifier;
import net.minecraft.util.Mth;
import net.minecraft.world.phys.Vec3;

/**
 * La trampa de oro de El Rayo del Prisma (trampa.png, de rajang_minijuegos.py):
 * el aro de oro con su greca alrededor del hoyo, una cabeza de jaguar de oro en
 * cada esquina, el fondo pintado con su hondura y nueve pinchos de jade (de
 * pixeles, en gradas). Sale del suelo al abrirse; cuando Rajang cae en ella,
 * los pinchos quedan partidos. Se hunde al acabar.
 */
public class TrampaOroRenderer extends EntityRenderer<TrampaOroEntity, TrampaOroRenderer.Estado> {

    private static final RenderType TEXTURA = RenderTypes.entityCutout(
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "textures/entity/rajang/trampa.png"));
    private static final List<RajangDibujo.Cara> ARO = new ArrayList<>();
    private static final List<RajangDibujo.Cara> PINCHOS = new ArrayList<>();
    private static final List<RajangDibujo.Cara> PINCHOS_ROTOS = new ArrayList<>();
    /** Lo que baja al abrirse y al cerrarse. */
    private static final float HONDO = 1.2F;

    static {
        float[] canto = uv(0, 0, 64, 8);
        float[] tapa = uv(0, 8, 64, 16);
        float[] fondo = uv(0, 16, 48, 64);
        float[] pincho = uv(48, 16, 64, 32);
        float[] cara = uv(48, 32, 64, 48);
        float[] cabeza = uv(48, 48, 64, 64);
        double m = TrampaOroEntity.LADO / 2.0;
        double g = 0.42;
        double alto = 0.45;
        RajangDibujo.caja(ARO, -m, 0, -m, m, alto, -m + g, canto, tapa);
        RajangDibujo.caja(ARO, -m, 0, m - g, m, alto, m, canto, tapa);
        RajangDibujo.caja(ARO, -m, 0, -m + g, -m + g, alto, m - g, canto, tapa);
        RajangDibujo.caja(ARO, m - g, 0, -m + g, m, alto, m - g, canto, tapa);
        // Las cabezas de jaguar de las esquinas.
        double c = 0.4;
        for (int sx = -1; sx <= 1; sx += 2) {
            for (int sz = -1; sz <= 1; sz += 2) {
                double x = sx * (m - c * 0.8);
                double z = sz * (m - c * 0.8);
                RajangDibujo.caja(ARO, x - c, 0, z - c, x + c, 0.85, z + c, cara, cabeza);
            }
        }
        // El fondo del hoyo, a ras de suelo (pintado con su hondura).
        double f = m - g;
        ARO.add(new RajangDibujo.Cara(new Vec3(-f, 0.03, -f), new Vec3(f, 0.03, -f), new Vec3(f, 0.03, f), new Vec3(-f, 0.03, f), fondo));
        // Los pinchos: tres gradas de jade, la de arriba fina.
        for (int i = -1; i <= 1; i++) {
            for (int k = -1; k <= 1; k++) {
                double x = i * 0.95 + (k == 0 ? 0.12 : 0);
                double z = k * 0.95 + (i == 0 ? -0.1 : 0);
                double h = 1.0 + ((i + k) & 1) * 0.25;
                RajangDibujo.caja(PINCHOS, x - 0.2, 0, z - 0.2, x + 0.2, h * 0.4, z + 0.2, pincho, pincho);
                RajangDibujo.caja(PINCHOS, x - 0.13, h * 0.4, z - 0.13, x + 0.13, h * 0.75, z + 0.13, pincho, pincho);
                RajangDibujo.caja(PINCHOS, x - 0.06, h * 0.75, z - 0.06, x + 0.06, h, z + 0.06, pincho, pincho);
                // Partidos: solo el mocho de abajo.
                RajangDibujo.caja(PINCHOS_ROTOS, x - 0.2, 0, z - 0.2, x + 0.2, 0.22, z + 0.2, pincho, pincho);
            }
        }
    }

    private static float[] uv(int u0, int v0, int u1, int v1) {
        return RajangDibujo.uv(u0 / 64.0F, v0 / 64.0F, u1 / 64.0F, v1 / 64.0F);
    }

    public static class Estado extends EntityRenderState {
        public float salida;
        public boolean usada;
    }

    public TrampaOroRenderer(EntityRendererProvider.Context contexto) {
        super(contexto);
    }

    @Override
    public Estado createRenderState() {
        return new Estado();
    }

    @Override
    public void extractRenderState(TrampaOroEntity tr, Estado s, float parcial) {
        super.extractRenderState(tr, s, parcial);
        float k = Mth.clamp((tr.tickCount + parcial) / TrampaOroEntity.ABRE, 0.0F, 1.0F);
        if (tr.cierra() >= 0) {
            k = Math.min(k, 1.0F - Mth.clamp((tr.tickCount - tr.cierra() + parcial) / TrampaOroEntity.ABRE, 0.0F, 1.0F));
        }
        s.salida = 1.0F - (1.0F - k) * (1.0F - k);
        s.usada = tr.usada();
    }

    @Override
    public void submit(Estado s, PoseStack pose, SubmitNodeCollector colector, CameraRenderState camara) {
        if (s.salida <= 0.01F) {
            return;
        }
        pose.pushPose();
        pose.translate(0.0, -HONDO * (1.0F - s.salida), 0.0);
        int luz = s.lightCoords;
        colector.submitCustomGeometry(pose, TEXTURA, (p, buf) -> {
            RajangDibujo.emitir(buf, p, ARO, 255, 255, 255, 255, luz);
            // Los pinchos brillan un poco (el jade encendido); partidos, se apagan.
            if (s.usada) {
                RajangDibujo.emitir(buf, p, PINCHOS_ROTOS, 150, 170, 150, 255, luz);
            } else {
                RajangDibujo.emitir(buf, p, PINCHOS, 255, 255, 255, 255, AeralisDibujo.A_PLENA_LUZ);
            }
        });
        pose.popPose();
        super.submit(s, pose, colector, camara);
    }
}
