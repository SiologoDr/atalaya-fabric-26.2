package com.atalaya.client;

import com.atalaya.entity.MiniJefeEntity;
import com.atalaya.entity.XiuhquetzalEntity;
import com.atalaya.entity.XiuhquetzalGeometria;
import com.mojang.blaze3d.vertex.PoseStack;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.renderer.SubmitNodeCollector;
import net.minecraft.client.renderer.rendertype.RenderType;
import net.minecraft.client.renderer.state.level.CameraRenderState;
import net.minecraft.util.Mth;
import net.minecraft.world.phys.Vec3;

/**
 * Lo que se ve de Xiuhquetzal ademas de su cuerpo (que es fuego: se pinta a
 * plena luz): la brasa del pecho y los ojos; el capullo que late mientras
 * duerme y el estallido al renacer; las plumas de fuego de la Tormenta en vuelo
 * hacia el suelo, y la Llamarada: el sol en que se convierte, el anillo de fuego
 * que barre el suelo y la columna de llamas que cae bajo el. La cresta y las
 * puntas de la cola tiemblan como llamas.
 */
public class XiuhquetzalEfectos implements MiniJefeEfectos {

    private static final RenderType BRILLO = MiniJefeDibujo.luz("brillo");
    private static final RenderType SOL = MiniJefeDibujo.luz("sol");
    private static final RenderType PLUMA = MiniJefeDibujo.luz("pluma_fuego");
    private static final RenderType ANILLO = MiniJefeDibujo.luz("anillo_fuego");
    private static final RenderType LLAMAS = MiniJefeDibujo.luz("llamas");
    private static final int BRASA = 0xFF9A30;
    /** Lo que ha crecido (el cuerpo) y lo que crecen las zonas de sus ataques: XiuhquetzalEntity.K y KA. */
    private static final float K = XiuhquetzalEntity.K;
    private static final float KA = XiuhquetzalEntity.KA;

    @Override
    public boolean plenaLuz() {
        return true;
    }

    /** Las alas abiertas y la cola de plumas llegan lejos de su caja. */
    @Override
    public float alcance() {
        return 5.0F;
    }

    @Override
    public void secundario(MiniJefeModel m, MiniJefeRenderState s) {
        float t = s.ageInTicks;
        ModelPart cresta = m.parte("cresta");
        if (cresta != null) {
            cresta.xRot += Mth.sin(t * 0.9F) * 0.035F + Mth.sin(t * 2.3F) * 0.015F;
            cresta.zRot += Mth.sin(t * 0.7F + 1.0F) * 0.03F;
        }
        ModelPart cola = m.parte("cola3");
        if (cola != null) {
            cola.xRot += Mth.sin(t * 0.8F + 0.5F) * 0.05F;
            cola.zRot += Mth.sin(t * 0.6F) * 0.05F;
        }
        // Mira a su presa: el giro y la inclinacion se reparten por el cuello y la cabeza (andando o cernido; en los
        // ataques manda la animacion).
        float k = s.pesoLibre;
        if (k > 0.01F) {
            float giro = s.miraGiro * Mth.DEG_TO_RAD * k;
            float alto = s.miraAlto * Mth.DEG_TO_RAD * k;
            String[] piezas = {"cuello", "cuello2", "cabeza"};
            float[] reparto = {0.3F, 0.3F, 0.4F};
            for (int i = 0; i < piezas.length; i++) {
                ModelPart p = m.parte(piezas[i]);
                if (p != null) {
                    p.yRot += giro * reparto[i];
                    p.xRot += alto * reparto[i];
                }
            }
        }
    }

    @Override
    public void submit(MiniJefeRenderState s, PoseStack pose, SubmitNodeCollector c, CameraRenderState cam) {
        float t = s.tiempo;
        if (s.deathTime <= 0) {
            pecho(s, pose, c, cam);
        }
        switch (s.estado) {
            case MiniJefeEntity.DORMIDO -> capullo(s, pose, c, cam, 1.0F);
            case MiniJefeEntity.DESPERTAR -> {
                float abre = XiuhquetzalGeometria.DESPERTAR_SE_ALZA;
                capullo(s, pose, c, cam, 1.0F + 0.8F * MiniJefeDibujo.tramo(t, XiuhquetzalGeometria.DESPERTAR_ABRE, abre)
                        - 2.0F * MiniJefeDibujo.tramo(t, abre, abre + 3));
                float e = t - abre;
                if (e >= 0 && e < 16) {
                    float k = e / 16.0F;
                    c.submitCustomGeometry(pose, SOL, (p, buf) -> MiniJefeDibujo.destello(buf, p, cam, new Vec3(0, 1.8 * K, 0),
                            (2.0F + 8.0F * k) * K, k, MiniJefeDibujo.color(0xFFFFFF, 0.95F * (1 - k))));
                }
            }
            case MiniJefeEntity.AREA -> plumas(s, pose, c, cam, t);
            case MiniJefeEntity.ESPECIAL -> llamarada(s, pose, c, cam, t);
            default -> {
            }
        }
    }

    /** La brasa del pecho y los ojos de oro: laten despacio. */
    private static void pecho(MiniJefeRenderState s, PoseStack pose, SubmitNodeCollector c, CameraRenderState cam) {
        Vec3 pe = MiniJefeRenderer.punto(s, XiuhquetzalGeometria.PECHO_BRASA_PIEZA, XiuhquetzalGeometria.PECHO_BRASA[0],
                XiuhquetzalGeometria.PECHO_BRASA[1], XiuhquetzalGeometria.PECHO_BRASA[2]);
        Vec3 ojos = MiniJefeRenderer.punto(s, XiuhquetzalGeometria.OJOS_PIEZA, XiuhquetzalGeometria.OJOS[0],
                XiuhquetzalGeometria.OJOS[1], XiuhquetzalGeometria.OJOS[2]);
        float late = 0.8F + 0.2F * Mth.sin(s.ageInTicks * 0.22F);
        c.submitCustomGeometry(pose, BRILLO, (p, buf) -> {
            MiniJefeDibujo.destello(buf, p, cam, pe, 1.3F * K * late, s.ageInTicks * 0.02F, MiniJefeDibujo.color(BRASA, 0.55F));
            MiniJefeDibujo.destello(buf, p, cam, pe, 0.5F * K, 0, MiniJefeDibujo.color(0xFFF2C0, 0.8F));
            MiniJefeDibujo.destello(buf, p, cam, ojos, 0.45F * K, 0, MiniJefeDibujo.color(0xFFD060, 0.6F));
        });
    }

    /** El capullo: una luz de brasa que late a traves de las alas. */
    private static void capullo(MiniJefeRenderState s, PoseStack pose, SubmitNodeCollector c, CameraRenderState cam, float k) {
        if (k <= 0.01F) {
            return;
        }
        float late = 0.75F + 0.25F * Mth.sin(s.ageInTicks * 0.16F);
        c.submitCustomGeometry(pose, SOL, (p, buf) -> MiniJefeDibujo.destello(buf, p, cam, new Vec3(0, 1.3 * K, 0), 2.2F * K * late * k,
                s.ageInTicks * 0.01F, MiniJefeDibujo.color(0xFFFFFF, 0.45F * Math.min(1.0F, k))));
    }

    /** Las plumas de fuego de cada batida, en vuelo de sus alas al suelo. */
    private static void plumas(MiniJefeRenderState s, PoseStack pose, SubmitNodeCollector c, CameraRenderState cam, float t) {
        int[] batidas = {XiuhquetzalGeometria.AREA_BATIDA_1, XiuhquetzalGeometria.AREA_BATIDA_2, XiuhquetzalGeometria.AREA_BATIDA_3};
        Vec3 desde = new Vec3(0, 2.4 * K, 0);
        c.submitCustomGeometry(pose, PLUMA, (p, buf) -> {
            for (int b = 0; b < batidas.length; b++) {
                float k = (t - batidas[b]) / XiuhquetzalEntity.PLUMA_VUELA;
                if (k < 0 || k > 1) {
                    continue;
                }
                for (int i = 0; i < XiuhquetzalEntity.PLUMAS; i++) {
                    Vec3 hasta = XiuhquetzalEntity.caidaPluma(s.punto, b, i);
                    // Un arco: sale hacia fuera y arriba y cae.
                    for (int j = 0; j < 3; j++) {
                        float kk = Math.max(0, k - j * 0.06F);
                        Vec3 q = desde.lerp(hasta, kk).add(0, 3.0 * K * kk * (1 - kk) * 2.0, 0);
                        MiniJefeDibujo.destello(buf, p, cam, q, (0.7F - j * 0.18F) * KA, kk * 6 + i, MiniJefeDibujo.color(0xFFFFFF, 1.0F - j * 0.3F));
                    }
                }
            }
        });
    }

    /** La Llamarada: el sol, el anillo de fuego que barre el suelo y la columna de llamas bajo el. */
    private static void llamarada(MiniJefeRenderState s, PoseStack pose, SubmitNodeCollector c, CameraRenderState cam, float t) {
        float envuelve = XiuhquetzalGeometria.ESPECIAL_ENVUELVE;
        float estalla = XiuhquetzalGeometria.ESPECIAL_ESTALLA;
        float fin = XiuhquetzalGeometria.ESPECIAL_FIN;
        float sol = MiniJefeDibujo.tramo(t, envuelve - 6, estalla) * (1.0F - MiniJefeDibujo.tramo(t, estalla, estalla + 10));
        if (sol > 0.01F) {
            float late = 0.85F + 0.15F * Mth.sin(s.ageInTicks * 0.9F);
            c.submitCustomGeometry(pose, SOL, (p, buf) -> {
                MiniJefeDibujo.destello(buf, p, cam, new Vec3(0, 1.8 * K, 0), (1.5F + 4.5F * sol) * K * late, s.ageInTicks * 0.03F,
                        MiniJefeDibujo.color(0xFFFFFF, 0.95F * sol));
                MiniJefeDibujo.destello(buf, p, cam, new Vec3(0, 1.8 * K, 0), (1.0F + 2.5F * sol) * K, -s.ageInTicks * 0.05F,
                        MiniJefeDibujo.color(0xFFF4D0, sol));
            });
        }
        float e = t - estalla;
        if (e < 0) {
            return;
        }
        // El suelo bajo el (la entidad vuela): el anillo y la columna bajan hasta alli.
        float suelo = -(float) XiuhquetzalEntity.ALTURA - (float) XiuhquetzalEntity.LLAMARADA_SUBE * (1.0F - MiniJefeDibujo.tramo(t, fin, fin + 20));
        float r = 1.0F + e * XiuhquetzalEntity.NOVA_CRECE;
        if (r < XiuhquetzalEntity.NOVA_HASTA + 2.0F) {
            float alfa = 1.0F - MiniJefeDibujo.tramo(r, XiuhquetzalEntity.NOVA_HASTA - 3.0F, XiuhquetzalEntity.NOVA_HASTA + 2.0F);
            Vec3 g = new Vec3(0, suelo, 0);
            c.submitCustomGeometry(pose, ANILLO, (p, buf) -> {
                MiniJefeDibujo.banda(buf, p, g, r, r + 0.5F * KA, 0.0F, 2.4F * KA * alfa, 72, 10, s.ageInTicks * 0.06F, 0, 1,
                        MiniJefeDibujo.color(0xFFFFFF, alfa), MiniJefeDibujo.color(0xFFFFFF, 0.0F));
                MiniJefeDibujo.banda(buf, p, g, r * 0.85F, r * 0.85F + 0.3F * KA, 0.0F, 1.4F * KA * alfa, 72, 8, -s.ageInTicks * 0.05F, 0, 1,
                        MiniJefeDibujo.color(0xFFFFFF, alfa * 0.7F), MiniJefeDibujo.color(0xFFFFFF, 0.0F));
            });
        }
        if (t < fin + 6) {
            float alfa = MiniJefeDibujo.tramo(e, 0, 3) * (1.0F - MiniJefeDibujo.tramo(t, fin - 4, fin + 6));
            float cr = XiuhquetzalEntity.COLUMNA_RADIO;
            c.submitCustomGeometry(pose, LLAMAS, (p, buf) -> {
                MiniJefeDibujo.banda(buf, p, new Vec3(0, suelo, 0), cr, cr * 0.45F, 0.0F, -suelo + 1.6F * K, 36, 3,
                        s.ageInTicks * 0.02F, s.ageInTicks * 0.12F, s.ageInTicks * 0.12F + 1, MiniJefeDibujo.color(0xFFFFFF, 0.9F * alfa),
                        MiniJefeDibujo.color(0xFFFFFF, 0.6F * alfa));
                MiniJefeDibujo.banda(buf, p, new Vec3(0, suelo, 0), cr * 0.6F, cr * 0.25F, 0.0F, -suelo + 1.4F * K, 28, 2,
                        -s.ageInTicks * 0.03F, s.ageInTicks * 0.18F, s.ageInTicks * 0.18F + 1, MiniJefeDibujo.color(0xFFFFFF, 0.8F * alfa),
                        MiniJefeDibujo.color(0xFFFFFF, 0.5F * alfa));
            });
        }
    }
}
