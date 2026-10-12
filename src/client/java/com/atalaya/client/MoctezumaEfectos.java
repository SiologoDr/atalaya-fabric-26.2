package com.atalaya.client;

import com.atalaya.entity.MiniJefeEntity;
import com.atalaya.entity.MoctezumaEntity;
import com.atalaya.entity.MoctezumaGeometria;
import com.mojang.blaze3d.vertex.PoseStack;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.renderer.SubmitNodeCollector;
import net.minecraft.client.renderer.rendertype.RenderType;
import net.minecraft.client.renderer.state.level.CameraRenderState;
import net.minecraft.util.Mth;
import net.minecraft.util.RandomSource;
import net.minecraft.world.phys.Vec3;

/**
 * Lo que se ve de Moctezuma ademas de su cuerpo: la estela de obsidiana del
 * macuahuitl en el Corte, las tres coronas de pinchos de jade del Terremoto, el
 * remolino de esquirlas de la Tormenta y los pilares de jade de la erupcion, la
 * luz de sus ojos al despertar y la de la hoja cuando llama a la tormenta. Y el
 * penacho, que tiembla con el aire.
 */
public class MoctezumaEfectos implements MiniJefeEfectos {

    private static final RenderType TAJO = MiniJefeDibujo.luz("tajo_obsidiana");
    private static final RenderType BRILLO = MiniJefeDibujo.luz("brillo");
    // Los cristales son jade macizo (no luz que se suma): a plena luz, pero opacos.
    private static final RenderType CRISTAL = net.minecraft.client.renderer.rendertype.RenderTypes.entityCutout(
            MiniJefeDibujo.tex("cristal_jade"));
    private static final RenderType REMOLINO = MiniJefeDibujo.luz("remolino_jade");
    private static final int JADE = 0x6CFFB0;
    /** Lo que ha crecido (el cuerpo) y lo que crecen las zonas de sus ataques: MoctezumaEntity.K y KA. */
    private static final float K = MoctezumaEntity.K;
    private static final float KA = MoctezumaEntity.KA;

    @Override
    public void secundario(MiniJefeModel m, MiniJefeRenderState s) {
        float t = s.ageInTicks;
        ModelPart penacho = m.parte("penacho");
        if (penacho != null) {
            penacho.xRot += Mth.sin(t * 0.21F) * 0.025F + Mth.sin(t * 0.53F) * 0.01F;
            penacho.zRot += Mth.sin(t * 0.17F + 1.3F) * 0.02F;
        }
        for (String n : new String[]{"hombrera_izq", "hombrera_der"}) {
            ModelPart h = m.parte(n);
            if (h != null) {
                h.zRot += Mth.sin(t * 0.3F + n.length()) * 0.02F;
            }
        }
    }

    @Override
    public void submit(MiniJefeRenderState s, PoseStack pose, SubmitNodeCollector c, CameraRenderState cam) {
        float t = s.tiempo;
        float r = s.rumbo;
        switch (s.estado) {
            case MiniJefeEntity.DESPERTAR -> ojos(s, pose, c, cam, MiniJefeDibujo.tramo(t, MoctezumaGeometria.DESPERTAR_ABRE - 4,
                    MoctezumaGeometria.DESPERTAR_ABRE + 6) * (1.0F + 0.6F * MiniJefeDibujo.tramo(t, MoctezumaGeometria.DESPERTAR_RUGE - 2,
                    MoctezumaGeometria.DESPERTAR_RUGE) * (1.0F - MiniJefeDibujo.tramo(t, MoctezumaGeometria.DESPERTAR_RUGE + 10,
                    MoctezumaGeometria.DESPERTAR_RUGE + 30))));
            case MiniJefeEntity.NORMAL -> c.submitCustomGeometry(pose, TAJO, (p, buf) -> {
                MiniJefeDibujo.estela(buf, p, MoctezumaGeometria.TRAZO_NORMAL, t, 4.0F, 0.35F, r, 0xFFFFFF, 0.95F);
            });
            case MiniJefeEntity.AREA -> {
                c.submitCustomGeometry(pose, TAJO, (p, buf) ->
                        MiniJefeDibujo.estela(buf, p, MoctezumaGeometria.TRAZO_AREA, t, 3.0F, 0.5F, r, 0xFFFFFF, 0.8F));
                coronas(s, pose, c, t);
            }
            case MiniJefeEntity.ESPECIAL -> tormenta(s, pose, c, cam, t);
            default -> {
            }
        }
        if (s.estado != MiniJefeEntity.DORMIDO && s.estado != MiniJefeEntity.DESPERTAR && s.deathTime <= 0) {
            ojos(s, pose, c, cam, 0.55F);
        }
    }

    /** La luz de jade de los ojos del yelmo. */
    private static void ojos(MiniJefeRenderState s, PoseStack pose, SubmitNodeCollector c, CameraRenderState cam, float k) {
        if (k <= 0.01F) {
            return;
        }
        Vec3 o = MiniJefeRenderer.punto(s, MoctezumaGeometria.OJOS_PIEZA, MoctezumaGeometria.OJOS[0], MoctezumaGeometria.OJOS[1],
                MoctezumaGeometria.OJOS[2]);
        float late = 0.85F + 0.15F * Mth.sin(s.ageInTicks * 0.3F);
        c.submitCustomGeometry(pose, BRILLO, (p, buf) -> {
            MiniJefeDibujo.destello(buf, p, cam, o, 0.55F * K * k * late, 0.0F, MiniJefeDibujo.color(JADE, 0.75F * Math.min(1.0F, k)));
            MiniJefeDibujo.destello(buf, p, cam, o, 0.22F * K * k, 0.6F, MiniJefeDibujo.color(0xEFFFF4, Math.min(1.0F, k)));
        });
    }

    /** Las tres coronas de pinchos de jade del Terremoto: brotan, se quedan y se hunden. */
    private static void coronas(MiniJefeRenderState s, PoseStack pose, SubmitNodeCollector c, float t) {
        float cae = MoctezumaGeometria.AREA_CAE;
        if (t < cae) {
            return;
        }
        Vec3 centro = MiniJefeDibujo.cuerpo((float) MoctezumaGeometria.GOLPE_AREA.x, 0.0F, (float) MoctezumaGeometria.GOLPE_AREA.z,
                s.rumbo);
        c.submitCustomGeometry(pose, CRISTAL, (p, buf) -> {
            for (int i = 0; i < MoctezumaEntity.CORONAS.length; i++) {
                float k = t - cae - MoctezumaEntity.CORONAS_TICK[i];
                if (k < 0 || k > 20) {
                    continue;
                }
                float sale = MiniJefeDibujo.tramo(k, 0, 2.5F) * (1.0F - MiniJefeDibujo.tramo(k, 12, 20));
                float radio = MoctezumaEntity.CORONAS[i];
                int n = Math.round(radio * 1.7F);
                RandomSource azar = RandomSource.create(s.semilla * 31L + i);
                for (int j = 0; j < n; j++) {
                    double a = Mth.TWO_PI * j / n + i * 0.4 + azar.nextFloat() * 0.2;
                    float alto = (2.0F + azar.nextFloat() * 1.8F) * KA * (1.0F - i * 0.1F) * sale;
                    if (alto < 0.05F) {
                        continue;
                    }
                    Vec3 b = centro.add(Math.cos(a) * radio, -0.3, Math.sin(a) * radio);
                    Vec3 d = new Vec3(Math.cos(a) * 0.35, 1.0, Math.sin(a) * 0.35).normalize();
                    MiniJefeDibujo.cristal(buf, p, b, d, (0.36F + azar.nextFloat() * 0.16F) * KA, alto, 5, azar.nextFloat() * 6, 0xFFFFFFFF);
                }
            }
        });
    }

    /** La Tormenta: el remolino de esquirlas sobre el, la hoja que brilla y los pilares de la erupcion. */
    private static void tormenta(MiniJefeRenderState s, PoseStack pose, SubmitNodeCollector c, CameraRenderState cam, float t) {
        float alza = MoctezumaGeometria.ESPECIAL_ALZA;
        float clava = MoctezumaGeometria.ESPECIAL_CLAVA;
        float k = MiniJefeDibujo.tramo(t, alza - 4, alza + 12) * (1.0F - MiniJefeDibujo.tramo(t, clava - 6, clava + 2));
        if (k > 0.01F) {
            // La hoja del macuahuitl brilla de jade de la base a la punta.
            Vec3 b = MiniJefeRenderer.punto(s, MoctezumaGeometria.HOJA_BASE_PIEZA, MoctezumaGeometria.HOJA_BASE[0],
                    MoctezumaGeometria.HOJA_BASE[1], MoctezumaGeometria.HOJA_BASE[2]);
            Vec3 e = MiniJefeRenderer.punto(s, MoctezumaGeometria.HOJA_PUNTA_PIEZA, MoctezumaGeometria.HOJA_PUNTA[0],
                    MoctezumaGeometria.HOJA_PUNTA[1], MoctezumaGeometria.HOJA_PUNTA[2]);
            float late = 0.8F + 0.2F * Mth.sin(s.ageInTicks * 0.5F);
            c.submitCustomGeometry(pose, BRILLO, (p, buf) -> {
                for (int i = 0; i <= 6; i++) {
                    Vec3 q = b.lerp(e, i / 6.0);
                    MiniJefeDibujo.destello(buf, p, cam, q, 0.55F * K * k * late, i, MiniJefeDibujo.color(JADE, 0.55F * k));
                }
            });
            // El remolino: un disco que gira sobre el y las esquirlas que le dan vueltas.
            Vec3 cielo = new Vec3(0, 9.0 * K, 0);
            float giro = s.ageInTicks * 0.12F;
            c.submitCustomGeometry(pose, REMOLINO, (p, buf) -> {
                MiniJefeDibujo.tumbado(buf, p, cielo, 6.5F * K * k, giro, MiniJefeDibujo.color(0xFFFFFF, 0.75F * k));
                MiniJefeDibujo.tumbado(buf, p, cielo.add(0, 0.3 * K, 0), 4.2F * K * k, -giro * 1.6F, MiniJefeDibujo.color(0xFFFFFF, 0.6F * k));
            });
            c.submitCustomGeometry(pose, CRISTAL, (p, buf) -> {
                RandomSource azar = RandomSource.create(s.semilla * 17L);
                for (int i = 0; i < 26; i++) {
                    float rr = (2.5F + azar.nextFloat() * 4.0F) * K * k;
                    float vel = 0.08F + azar.nextFloat() * 0.06F;
                    double a = azar.nextFloat() * Mth.TWO_PI + s.ageInTicks * vel;
                    Vec3 q = cielo.add(Math.cos(a) * rr, (azar.nextFloat() - 0.5F) * 2.0F * K, Math.sin(a) * rr);
                    Vec3 d = new Vec3(-Math.sin(a), 0.3, Math.cos(a)).normalize();
                    MiniJefeDibujo.cristal(buf, p, q, d, (0.14F + azar.nextFloat() * 0.1F) * K, (0.7F + azar.nextFloat() * 0.6F) * K, 4,
                            azar.nextFloat() * 6, i % 3 == 0 ? 0xFF6A50A0 : 0xFFFFFFFF);
                }
            });
        }
        // La erupcion: pilares de jade que revientan alrededor y se hunden.
        float e = t - clava;
        if (e >= 0 && e < 34) {
            float sale = MiniJefeDibujo.tramo(e, 0, 3) * (1.0F - MiniJefeDibujo.tramo(e, 22, 34));
            c.submitCustomGeometry(pose, CRISTAL, (p, buf) -> {
                RandomSource azar = RandomSource.create(s.semilla * 7L);
                for (int i = 0; i < 14; i++) {
                    double a = Mth.TWO_PI * i / 14 + azar.nextFloat() * 0.3;
                    float rr = (2.8F + azar.nextFloat() * 4.0F) * KA;
                    Vec3 b = new Vec3(Math.cos(a) * rr, -0.4, Math.sin(a) * rr);
                    Vec3 d = new Vec3(Math.cos(a) * 0.4, 1.0, Math.sin(a) * 0.4).normalize();
                    MiniJefeDibujo.cristal(buf, p, b, d, (0.45F + azar.nextFloat() * 0.25F) * KA, (2.4F + azar.nextFloat() * 2.4F) * K * sale, 6,
                            azar.nextFloat() * 6, 0xFFFFFFFF);
                }
            });
        }
    }
}
