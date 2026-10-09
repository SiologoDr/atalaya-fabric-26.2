package com.atalaya.client;

import com.atalaya.entity.MorenaSaltoEntity;
import com.mojang.blaze3d.vertex.PoseStack;
import net.minecraft.client.renderer.SubmitNodeCollector;
import net.minecraft.client.renderer.entity.EntityRenderer;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.state.EntityRenderState;
import net.minecraft.client.renderer.state.level.CameraRenderState;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.util.Mth;
import net.minecraft.world.phys.Vec3;

/**
 * La morena que salta de una poza de la Pesca (MorenaSaltoEntity): asoma recta
 * del agua con la boca abierta, salta en arco hasta el pescador con la segunda
 * mandibula fuera, cierra de golpe al llegar y cae, encogiendose y deshaciendose
 * en agua. El cuerpo va por el camino del salto: la cola sigue a la cabeza.
 */
public class MorenaSaltoRenderer extends EntityRenderer<MorenaSaltoEntity, MorenaSaltoRenderer.Estado> {

    private static final Vec3 ARRIBA = new Vec3(0, 1, 0);
    /** Lo que mide la morena de la cola al cuello (bloques). */
    private static final double LARGO = 2.6;
    /** Lo que baja el camino por la poza antes de salir (la cola sale de ahi). */
    private static final double HONDO = 3.0;

    public static class Estado extends EntityRenderState {
        public float edad;
        public Vec3 destino = new Vec3(0, 1, 2);
    }

    public MorenaSaltoRenderer(EntityRendererProvider.Context contexto) {
        super(contexto);
    }

    @Override
    public Estado createRenderState() {
        return new Estado();
    }

    @Override
    public void extractRenderState(MorenaSaltoEntity m, Estado s, float parcial) {
        super.extractRenderState(m, s, parcial);
        s.edad = m.tickCount + parcial;
        s.destino = m.destino(parcial).subtract(m.getPosition(parcial));
    }

    @Override
    protected boolean affectedByCulling(MorenaSaltoEntity m) {
        return false;
    }

    @Override
    public void submit(Estado s, PoseStack pose, SubmitNodeCollector colector, CameraRenderState camara) {
        float t = s.edad;
        int asoma = MorenaSaltoEntity.T_ASOMA;
        int salto = MorenaSaltoEntity.T_SALTO;
        int cae = MorenaSaltoEntity.T_CAE;
        if (t > asoma + salto + cae) {
            return;
        }
        // El camino: baja por la poza y sale en arco hasta el pescador.
        Vec3 a = new Vec3(0, 0.7, 0);
        Vec3 b = s.destino;
        double lejos = Math.sqrt(b.x * b.x + b.z * b.z);
        Vec3 c = a.add(b).scale(0.5).add(0, 1.0 + 0.12 * lejos, 0);
        int n = 48;
        Vec3[] camino = new Vec3[n + 1];
        double[] largo = new double[n + 1];
        for (int i = 0; i <= n; i++) {
            double k = i / (double) n;
            Vec3 q;
            if (k < 0.25) {
                q = new Vec3(0, -HONDO + (HONDO + a.y) * (k / 0.25), 0);
            } else {
                double u = (k - 0.25) / 0.75;
                q = a.scale((1 - u) * (1 - u)).add(c.scale(2 * u * (1 - u))).add(b.scale(u * u));
            }
            camino[i] = q;
            largo[i] = i == 0 ? 0 : largo[i - 1] + q.distanceTo(camino[i - 1]);
        }
        double total = largo[n];
        double superficie = HONDO;
        // Por donde va la cabeza.
        double cabezaEn;
        float boca;
        float faringe = 0;
        if (t <= asoma) {
            double k = t / asoma;
            cabezaEn = superficie + (a.y + 0.2) * (1 - (1 - k) * (1 - k));
            boca = 0.7F;
        } else if (t <= asoma + salto) {
            double k = (t - asoma) / salto;
            double desde = superficie + a.y + 0.2;
            cabezaEn = desde + (total - desde) * (k * k * (3 - 2 * k));
            boca = k < 0.75 ? 1.0F : 1.0F - 3.6F * (float) (k - 0.75);
            faringe = (float) Mth.clamp((k - 0.4) / 0.4, 0, 1);
        } else {
            cabezaEn = total;
            boca = 0.1F;
        }
        // Al caer: baja, gira y encoge hasta deshacerse.
        double caida = Math.max(0, t - asoma - salto);
        float escala = (float) Mth.clamp(1.0 - caida / cae, 0.0, 1.0);
        if (escala <= 0.02F) {
            return;
        }
        Vec3 bajar = new Vec3(0, -0.035 * caida * caida, 0);
        Vec3[] espina = new Vec3[13];
        for (int i = 0; i < espina.length; i++) {
            double en = cabezaEn - 0.3 - LARGO * (espina.length - 1 - i) / (espina.length - 1);
            Vec3 q = sobre(camino, largo, Math.max(0, en));
            espina[i] = caida > 0 ? b.add(q.subtract(b).scale(escala)).add(bajar) : q;
        }
        Vec3 cuello = espina[espina.length - 1];
        Vec3 delante = sobre(camino, largo, Math.min(total, cabezaEn + 0.05));
        Vec3 frente = delante.subtract(sobre(camino, largo, Math.max(0, cabezaEn - 0.4)));
        if (frente.lengthSqr() < 1.0E-6) {
            frente = ARRIBA;
        }
        if (caida > 0) {
            frente = frente.normalize().yRot((float) (caida * 0.5)).add(0, -0.08 * caida, 0);
        }
        Vec3 fr = frente.normalize();
        float bocaF = boca;
        float faringeF = faringe;
        int luz = s.lightCoords;
        colector.submitCustomGeometry(pose, MorenaDibujo.PIEL, (p, buf) -> {
            MorenaDibujo.cuerpo(buf, p, espina, escala, luz, OverlayTexture.NO_OVERLAY, 0xFFFFFF);
            MorenaDibujo.cabeza(buf, p, cuello, fr, ARRIBA, bocaF, faringeF, escala, luz, OverlayTexture.NO_OVERLAY, 0xFFFFFF);
        });
        super.submit(s, pose, colector, camara);
    }

    /** El punto del camino a esa distancia de su principio. */
    private static Vec3 sobre(Vec3[] camino, double[] largo, double en) {
        int n = camino.length - 1;
        if (en >= largo[n]) {
            return camino[n];
        }
        int j = 0;
        while (j < n - 1 && largo[j + 1] < en) {
            j++;
        }
        double tramo = largo[j + 1] - largo[j];
        return camino[j].lerp(camino[j + 1], tramo < 1.0E-9 ? 0 : (en - largo[j]) / tramo);
    }
}
