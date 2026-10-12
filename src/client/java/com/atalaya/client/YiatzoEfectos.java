package com.atalaya.client;

import com.atalaya.entity.MiniJefeEntity;
import com.atalaya.entity.YiatzoEntity;
import com.atalaya.entity.YiatzoGeometria;
import com.mojang.blaze3d.vertex.PoseStack;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.renderer.SubmitNodeCollector;
import net.minecraft.client.renderer.rendertype.RenderType;
import net.minecraft.client.renderer.state.level.CameraRenderState;
import net.minecraft.util.Mth;
import net.minecraft.world.phys.Vec3;

/**
 * Lo que se ve de Yiatzo ademas de su cuerpo: el orbe del baston, que brilla
 * siempre; las tres cuchillas de viento de la Rafaga (y la estela del baston);
 * el anillo de viento de la Tormenta, y el Ciclon, tres embudos que giran a
 * distinto ritmo donde estaba su presa, con su estallido. Las losas tiemblan
 * un poco en el aire y la luz de la capucha se enciende al despertar.
 */
public class YiatzoEfectos implements MiniJefeEfectos {

    private static final RenderType BRILLO = MiniJefeDibujo.luz("brillo");
    private static final RenderType TAJO = MiniJefeDibujo.luz("tajo_viento");
    private static final RenderType CUCHILLA = MiniJefeDibujo.luz("cuchilla_viento");
    private static final RenderType ANILLO = MiniJefeDibujo.luz("anillo_viento");
    private static final RenderType CICLON = MiniJefeDibujo.luz("ciclon");
    private static final int CIAN = 0x8FE8FF;
    /** Lo que ha crecido (el cuerpo) y lo que crecen las zonas de sus ataques: YiatzoEntity.K y KA. */
    private static final float K = YiatzoEntity.K;
    private static final float KA = YiatzoEntity.KA;

    @Override
    public void secundario(MiniJefeModel m, MiniJefeRenderState s) {
        float t = s.ageInTicks;
        for (int i = 0; i < 5; i++) {
            ModelPart p = m.parte("piedra" + i);
            if (p != null) {
                p.xRot += Mth.sin(t * 0.11F + i * 1.7F) * 0.06F;
                p.zRot += Mth.sin(t * 0.09F + i * 2.3F) * 0.06F;
            }
        }
    }

    @Override
    public void submit(MiniJefeRenderState s, PoseStack pose, SubmitNodeCollector c, CameraRenderState cam) {
        float t = s.tiempo;
        if (s.deathTime <= 0 && s.estado != MiniJefeEntity.DORMIDO) {
            orbe(s, pose, c, cam, s.estado == MiniJefeEntity.DESPERTAR
                    ? MiniJefeDibujo.tramo(t, YiatzoGeometria.DESPERTAR_ABRE - 2, YiatzoGeometria.DESPERTAR_ABRE + 10) : 1.0F);
        }
        switch (s.estado) {
            case MiniJefeEntity.NORMAL -> {
                c.submitCustomGeometry(pose, TAJO, (p, buf) ->
                        MiniJefeDibujo.estela(buf, p, YiatzoGeometria.TRAZO_NORMAL, t, 3.5F, 0.3F, s.rumbo, 0xFFFFFF, 0.9F));
                cuchillas(s, pose, c, t);
            }
            case MiniJefeEntity.AREA -> anillo(s, pose, c, cam, t);
            case MiniJefeEntity.ESPECIAL -> ciclon(s, pose, c, cam, t);
            default -> {
            }
        }
    }

    /** El orbe: un halo celeste que late y un nucleo blanco. */
    private static void orbe(MiniJefeRenderState s, PoseStack pose, SubmitNodeCollector c, CameraRenderState cam, float k) {
        if (k <= 0.01F) {
            return;
        }
        Vec3 o = MiniJefeRenderer.punto(s, YiatzoGeometria.ORBE_PIEZA, YiatzoGeometria.ORBE[0], YiatzoGeometria.ORBE[1],
                YiatzoGeometria.ORBE[2]);
        float late = 0.85F + 0.15F * Mth.sin(s.ageInTicks * 0.25F);
        float extra = s.estado == MiniJefeEntity.AREA || s.estado == MiniJefeEntity.ESPECIAL ? 1.5F : 1.0F;
        c.submitCustomGeometry(pose, BRILLO, (p, buf) -> {
            MiniJefeDibujo.destello(buf, p, cam, o, 1.1F * K * late * extra * k, s.ageInTicks * 0.02F, MiniJefeDibujo.color(CIAN, 0.55F * k));
            MiniJefeDibujo.destello(buf, p, cam, o, 0.45F * K * extra * k, -s.ageInTicks * 0.05F, MiniJefeDibujo.color(0xF2FDFF, 0.9F * k));
        });
    }

    /** Las tres cuchillas de viento: medias lunas que vuelan en abanico con su estela. */
    private static void cuchillas(MiniJefeRenderState s, PoseStack pose, SubmitNodeCollector c, float t) {
        float k = t - YiatzoGeometria.NORMAL_SUELTA;
        float hasta = YiatzoEntity.ALCANCE_CUCHILLA / YiatzoEntity.VEL_CUCHILLA;
        if (k < 0 || k > hasta) {
            return;
        }
        Vec3 pies = Vec3.ZERO;
        Vec3 o = YiatzoEntity.origenCuchillas(pies, s.rumbo);
        float alfa = 1.0F - MiniJefeDibujo.tramo(k, hasta - 4, hasta);
        c.submitCustomGeometry(pose, CUCHILLA, (p, buf) -> {
            for (int i = 0; i < YiatzoEntity.CUCHILLAS; i++) {
                Vec3 d = YiatzoEntity.rumboCuchilla(s.rumbo, i);
                Vec3 lado = new Vec3(d.z, 0, -d.x);
                Vec3 q = YiatzoEntity.cuchilla(o, pies.y, s.rumbo, i, k);
                float w = 1.6F * KA;
                float h = 0.8F * KA;
                // La media luna, tumbada y de pie (se ve desde todas partes).
                MiniJefeDibujo.cuadro(buf, p, q.add(lado.scale(-w)).add(d.scale(-h)), q.add(lado.scale(w)).add(d.scale(-h)),
                        q.add(lado.scale(w)).add(d.scale(h)), q.add(lado.scale(-w)).add(d.scale(h)), 0, 0, 1, 1,
                        MiniJefeDibujo.color(0xFFFFFF, alfa));
                MiniJefeDibujo.cuadro(buf, p, q.add(lado.scale(-w)).add(0, -h, 0), q.add(lado.scale(w)).add(0, -h, 0),
                        q.add(lado.scale(w)).add(0, h, 0), q.add(lado.scale(-w)).add(0, h, 0), 0, 0, 1, 1,
                        MiniJefeDibujo.color(0xFFFFFF, alfa * 0.7F));
            }
        });
        c.submitCustomGeometry(pose, TAJO, (p, buf) -> {
            for (int i = 0; i < YiatzoEntity.CUCHILLAS; i++) {
                Vec3 d = YiatzoEntity.rumboCuchilla(s.rumbo, i);
                Vec3 lado = new Vec3(d.z, 0, -d.x);
                int n = 6;
                Vec3[] a = new Vec3[n];
                Vec3[] b = new Vec3[n];
                for (int j = 0; j < n; j++) {
                    float kk = Math.max(0, k - 3.0F + 3.0F * j / (n - 1));
                    Vec3 q = YiatzoEntity.cuchilla(o, pies.y, s.rumbo, i, kk);
                    a[j] = q.add(lado.scale(-1.2 * KA));
                    b[j] = q.add(lado.scale(1.2 * KA));
                }
                MiniJefeDibujo.cinta(buf, p, a, b, n, 0xFFFFFF, 0.7F * alfa);
            }
        });
    }

    /** El anillo de viento de la Tormenta: dos bandas que salen de el y se apagan al llegar lejos. */
    private static void anillo(MiniJefeRenderState s, PoseStack pose, SubmitNodeCollector c, CameraRenderState cam, float t) {
        float k = t - YiatzoGeometria.AREA_SUELTA;
        if (k < 0) {
            // Mientras carga, el viento se le junta: una banda que se cierra hacia el.
            float carga = MiniJefeDibujo.tramo(t, 2, YiatzoGeometria.AREA_SUELTA);
            float rr = (7.0F - 5.0F * carga) * K;
            c.submitCustomGeometry(pose, ANILLO, (p, buf) -> MiniJefeDibujo.banda(buf, p, Vec3.ZERO, rr, rr * 0.8F, 0.0F, 4.5F * K, 48,
                    6, -s.ageInTicks * 0.05F, 0, 1, MiniJefeDibujo.color(0xFFFFFF, 0.45F * carga), MiniJefeDibujo.color(0xFFFFFF, 0.0F)));
            return;
        }
        float r = YiatzoEntity.ANILLO_DESDE + k * YiatzoEntity.ANILLO_CRECE;
        if (r > YiatzoEntity.ANILLO_HASTA + 2.0F) {
            return;
        }
        float alfa = 1.0F - MiniJefeDibujo.tramo(r, YiatzoEntity.ANILLO_HASTA - 3.0F, YiatzoEntity.ANILLO_HASTA + 2.0F);
        c.submitCustomGeometry(pose, ANILLO, (p, buf) -> {
            MiniJefeDibujo.banda(buf, p, Vec3.ZERO, r, r + 0.6F, 0.0F, 2.6F * KA, 64, 8, s.ageInTicks * 0.08F, 0, 1,
                    MiniJefeDibujo.color(0xFFFFFF, 0.9F * alfa), MiniJefeDibujo.color(0xFFFFFF, 0.0F));
            MiniJefeDibujo.banda(buf, p, Vec3.ZERO, r * 0.82F, r * 0.82F + 0.4F, 0.2F, 1.8F * KA, 64, 6, -s.ageInTicks * 0.06F, 0, 1,
                    MiniJefeDibujo.color(0xFFFFFF, 0.6F * alfa), MiniJefeDibujo.color(0xFFFFFF, 0.0F));
        });
        if (k < 6) {
            c.submitCustomGeometry(pose, BRILLO, (p, buf) -> MiniJefeDibujo.destello(buf, p, cam, new Vec3(0, 2.0 * K, 0), (3.0F + k) * K,
                    0, MiniJefeDibujo.color(CIAN, 0.6F * (1 - k / 6.0F))));
        }
    }

    /** El Ciclon: tres embudos que giran a distinto ritmo, del suelo hasta lo alto; al final estalla. */
    private static void ciclon(MiniJefeRenderState s, PoseStack pose, SubmitNodeCollector c, CameraRenderState cam, float t) {
        float forma = YiatzoGeometria.ESPECIAL_FORMA;
        float estalla = YiatzoGeometria.ESPECIAL_ESTALLA;
        Vec3 centro = s.punto;
        float crece = MiniJefeDibujo.tramo(t, forma, forma + 24);
        float apaga = 1.0F - MiniJefeDibujo.tramo(t, estalla, estalla + 4);
        if (t > forma && t < estalla + 4) {
            float alto = YiatzoEntity.CICLON_ALTO * crece;
            float g = s.ageInTicks;
            c.submitCustomGeometry(pose, CICLON, (p, buf) -> {
                for (int capa = 0; capa < 3; capa++) {
                    float r0 = 0.6F + capa * 0.5F;
                    float r1 = r0 + alto * (0.36F + capa * 0.05F);
                    float corre = g * (0.06F + capa * 0.035F) * (capa % 2 == 0 ? 1 : -1);
                    float alfa = (0.75F - capa * 0.18F) * apaga;
                    MiniJefeDibujo.banda(buf, p, centro, r0, r1, 0.0F, alto, 40, 3 + capa, corre, 0, 1,
                            MiniJefeDibujo.color(0xFFFFFF, alfa), MiniJefeDibujo.color(0xFFFFFF, alfa * 0.5F));
                }
            });
        }
        float e = t - estalla;
        if (e >= 0 && e < 14) {
            float k = e / 14.0F;
            c.submitCustomGeometry(pose, BRILLO, (p, buf) -> MiniJefeDibujo.destello(buf, p, cam, centro.add(0, 4.0, 0),
                    3.0F + 9.0F * k, 0, MiniJefeDibujo.color(CIAN, 0.85F * (1 - k))));
            c.submitCustomGeometry(pose, ANILLO, (p, buf) -> {
                float r = 1.0F + YiatzoEntity.CICLON_ESTALLA * 1.6F * (1 - (1 - k) * (1 - k));
                MiniJefeDibujo.banda(buf, p, centro, r, r + 0.8F, 0.0F, 3.2F * (1 - k), 64, 8, k * 2, 0, 1,
                        MiniJefeDibujo.color(0xFFFFFF, 0.9F * (1 - k)), MiniJefeDibujo.color(0xFFFFFF, 0.0F));
            });
        }
    }
}
