package com.atalaya.client;

import com.atalaya.entity.AtlahuaEntity;
import com.atalaya.entity.AtlahuaGeometria;
import com.atalaya.entity.MiniJefeEntity;
import com.mojang.blaze3d.vertex.PoseStack;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.renderer.SubmitNodeCollector;
import net.minecraft.client.renderer.rendertype.RenderType;
import net.minecraft.client.renderer.state.level.CameraRenderState;
import net.minecraft.util.Mth;
import net.minecraft.world.phys.Vec3;

/**
 * Lo que se ve de Atlahua ademas de su cuerpo: la luz de las puntas del
 * tridente y de sus ojos; el chorro de agua de la Estocada (y la estela del
 * tridente); las dos olas en anillo de las Olas del Abismo, con su espuma, y el
 * Tsunami: un muro de agua de veinticuatro bloques que crece a su espalda, con
 * la cresta que se riza hacia delante, y que barre la arena.
 */
public class AtlahuaEfectos implements MiniJefeEfectos {

    private static final RenderType BRILLO = MiniJefeDibujo.luz("brillo");
    private static final RenderType TAJO = MiniJefeDibujo.luz("tajo_agua");
    private static final RenderType CHORRO = MiniJefeDibujo.luz("chorro");
    private static final RenderType OLA = MiniJefeDibujo.luz("ola");
    private static final RenderType ESPUMA = MiniJefeDibujo.luz("espuma");
    private static final RenderType TSUNAMI = MiniJefeDibujo.luz("tsunami");
    private static final int CIAN = 0x7AF0FF;
    /** Lo que ha crecido (el cuerpo) y lo que crecen las zonas de sus ataques: AtlahuaEntity.K y KA. */
    private static final float K = AtlahuaEntity.K;
    private static final float KA = AtlahuaEntity.KA;

    @Override
    public void secundario(MiniJefeModel m, MiniJefeRenderState s) {
        ModelPart mand = m.parte("mandibula");
        if (mand != null) {
            mand.zRot += Mth.sin(s.ageInTicks * 0.13F) * 0.02F;
        }
    }

    @Override
    public void submit(MiniJefeRenderState s, PoseStack pose, SubmitNodeCollector c, CameraRenderState cam) {
        float t = s.tiempo;
        if (s.deathTime <= 0) {
            float k = s.estado == MiniJefeEntity.DORMIDO ? 0.3F : s.estado == MiniJefeEntity.DESPERTAR
                    ? 0.3F + 0.7F * MiniJefeDibujo.tramo(t, AtlahuaGeometria.DESPERTAR_ABRE - 2, AtlahuaGeometria.DESPERTAR_ABRE + 10) : 1.0F;
            luces(s, pose, c, cam, k);
        }
        switch (s.estado) {
            case MiniJefeEntity.NORMAL -> {
                c.submitCustomGeometry(pose, TAJO, (p, buf) ->
                        MiniJefeDibujo.estela(buf, p, AtlahuaGeometria.TRAZO_NORMAL, t, 3.0F, 0.35F, s.rumbo, 0xFFFFFF, 0.85F));
                chorro(s, pose, c, t);
            }
            case MiniJefeEntity.AREA -> {
                c.submitCustomGeometry(pose, TAJO, (p, buf) ->
                        MiniJefeDibujo.estela(buf, p, AtlahuaGeometria.TRAZO_AREA, t, 4.0F, 0.4F, s.rumbo, 0xFFFFFF, 0.8F));
                olas(s, pose, c, t);
            }
            case MiniJefeEntity.ESPECIAL -> tsunami(s, pose, c, t);
            default -> {
            }
        }
    }

    private static void luces(MiniJefeRenderState s, PoseStack pose, SubmitNodeCollector c, CameraRenderState cam, float k) {
        Vec3 puntas = MiniJefeRenderer.punto(s, AtlahuaGeometria.PUNTAS_PIEZA, AtlahuaGeometria.PUNTAS[0], AtlahuaGeometria.PUNTAS[1],
                AtlahuaGeometria.PUNTAS[2]);
        Vec3 ojos = MiniJefeRenderer.punto(s, AtlahuaGeometria.OJOS_PIEZA, AtlahuaGeometria.OJOS[0], AtlahuaGeometria.OJOS[1],
                AtlahuaGeometria.OJOS[2]);
        float late = 0.85F + 0.15F * Mth.sin(s.ageInTicks * 0.2F);
        c.submitCustomGeometry(pose, BRILLO, (p, buf) -> {
            MiniJefeDibujo.destello(buf, p, cam, puntas, 0.9F * K * late * k, s.ageInTicks * 0.03F, MiniJefeDibujo.color(CIAN, 0.5F * k));
            MiniJefeDibujo.destello(buf, p, cam, ojos, 0.5F * K * k, 0, MiniJefeDibujo.color(CIAN, 0.6F * k));
        });
    }

    /** El chorro de la Estocada: dos lenguas de agua cruzadas que salen de las puntas hacia delante. */
    private static void chorro(MiniJefeRenderState s, PoseStack pose, SubmitNodeCollector c, float t) {
        float k = t - AtlahuaGeometria.NORMAL_GOLPE;
        if (k < -1 || k > 9) {
            return;
        }
        float sale = MiniJefeDibujo.tramo(k, -1, 1.5F);
        float alfa = 1.0F - MiniJefeDibujo.tramo(k, 3, 9);
        Vec3 f = MiniJefeEntity.frente(s.rumbo);
        Vec3 lado = new Vec3(f.z, 0, -f.x);
        Vec3 o = new Vec3(0, 2.0 * K, 0).add(f.scale(1.2 * K));
        float largo = AtlahuaEntity.CHORRO_LARGO * sale;
        // Baja hacia delante hasta la altura del pecho (sale del tridente, que con su tamano queda alto).
        Vec3 punta = o.add(f.scale(largo));
        Vec3 fin = new Vec3(punta.x, 1.0 + (o.y - 1.0) * (1.0F - sale), punta.z);
        float w0 = 0.35F * KA;
        float w1 = 1.8F * KA;
        float h1 = 1.6F * KA;
        float corre = -s.ageInTicks * 0.25F;
        c.submitCustomGeometry(pose, CHORRO, (p, buf) -> {
            MiniJefeDibujo.cuadro(buf, p, o.add(lado.scale(-w0)), o.add(lado.scale(w0)), fin.add(lado.scale(w1)),
                    fin.add(lado.scale(-w1)), 0, corre, 1, corre + 2, MiniJefeDibujo.color(0xFFFFFF, alfa),
                    MiniJefeDibujo.color(0xFFFFFF, alfa * 0.5F));
            MiniJefeDibujo.cuadro(buf, p, o.add(0, -w0, 0), o.add(0, w0, 0), fin.add(0, h1, 0), fin.add(0, -h1, 0), 0, corre, 1,
                    corre + 2, MiniJefeDibujo.color(0xFFFFFF, alfa), MiniJefeDibujo.color(0xFFFFFF, alfa * 0.5F));
        });
    }

    /** Las dos olas en anillo: una banda de agua con su cresta de espuma que crece y baja al alejarse. */
    private static void olas(MiniJefeRenderState s, PoseStack pose, SubmitNodeCollector c, float t) {
        Vec3 centro = AtlahuaEntity.centroOlas(Vec3.ZERO, s.rumbo);
        for (int i = 0; i < AtlahuaEntity.OLAS_TICK.length; i++) {
            float k = t - AtlahuaGeometria.AREA_GOLPE - AtlahuaEntity.OLAS_TICK[i];
            if (k < 0) {
                continue;
            }
            float r = 1.0F + k * AtlahuaEntity.OLA_CRECE;
            if (r > AtlahuaEntity.OLA_HASTA + 1.5F) {
                continue;
            }
            float baja = 1.0F - 0.55F * r / AtlahuaEntity.OLA_HASTA;
            float alto = AtlahuaEntity.OLA_ALTO * baja * MiniJefeDibujo.tramo(k, 0, 3);
            float alfa = 1.0F - MiniJefeDibujo.tramo(r, AtlahuaEntity.OLA_HASTA - 2.5F, AtlahuaEntity.OLA_HASTA + 1.5F);
            float g = s.ageInTicks * 0.05F + i;
            c.submitCustomGeometry(pose, OLA, (p, buf) -> {
                // La cara de fuera (inclinada hacia fuera arriba) y la de dentro, que baja despacio.
                MiniJefeDibujo.banda(buf, p, centro, r - 0.5F, r + 0.25F, 0.0F, alto, 72, 10, g, 0, 1,
                        MiniJefeDibujo.color(0xFFFFFF, 0.9F * alfa), MiniJefeDibujo.color(0xFFFFFF, 0.95F * alfa));
                MiniJefeDibujo.banda(buf, p, centro, r - 2.2F * baja, r - 0.4F, 0.0F, alto * 0.95F, 72, 10, -g, 0, 1,
                        MiniJefeDibujo.color(0xFFFFFF, 0.5F * alfa), MiniJefeDibujo.color(0xFFFFFF, 0.8F * alfa));
            });
            c.submitCustomGeometry(pose, ESPUMA, (p, buf) -> MiniJefeDibujo.corona(buf, p, centro.add(0, alto + 0.02, 0),
                    r - 0.45F, r + 0.35F, 72, 12, g * 2, MiniJefeDibujo.color(0xFFFFFF, 0.95F * alfa)));
        }
    }

    /** El Tsunami: el muro de agua que crece a su espalda, pasa por encima de el y barre la arena. */
    private static void tsunami(MiniJefeRenderState s, PoseStack pose, SubmitNodeCollector c, float t) {
        float lanza = AtlahuaGeometria.ESPECIAL_LANZA;
        Vec3 f = MiniJefeEntity.frente(s.rumbo);
        Vec3 lado = new Vec3(f.z, 0, -f.x);
        float k = Math.max(0.0F, t - lanza);
        if (k > AtlahuaEntity.TSUNAMI_TICKS + 8) {
            return;
        }
        Vec3 fr = AtlahuaEntity.frenteTsunami(Vec3.ZERO, s.rumbo, k);
        float crece = MiniJefeDibujo.tramo(t, 6, lanza);
        float alto = AtlahuaEntity.TSUNAMI_ALTO * crece * Mth.clamp(1.15F - k / AtlahuaEntity.TSUNAMI_TICKS * 0.6F, 0.0F, 1.0F);
        float rompe = MiniJefeDibujo.tramo(k, AtlahuaEntity.TSUNAMI_TICKS - 4, AtlahuaEntity.TSUNAMI_TICKS + 8);
        float alfa = 1.0F - rompe;
        if (alto < 0.1F || alfa < 0.02F) {
            return;
        }
        // La cresta se riza hacia delante cuando avanza; mientras crece, casi derecha.
        float riza = 0.6F + 2.4F * MiniJefeDibujo.tramo(k, 0, 8);
        MiniJefeDibujo.Perfil perfil = v -> -1.6F * (1 - v) + riza * v * v * v;
        float g = s.ageInTicks * 0.04F;
        c.submitCustomGeometry(pose, TSUNAMI, (p, buf) -> MiniJefeDibujo.muro(buf, p, fr, f, lado, AtlahuaEntity.TSUNAMI_ANCHO, alto,
                perfil, 24, 8, 4, g, MiniJefeDibujo.color(0xFFFFFF, 0.85F * alfa), MiniJefeDibujo.color(0xFFFFFF, 0.95F * alfa)));
        c.submitCustomGeometry(pose, ESPUMA, (p, buf) -> {
            // La espuma de la cresta y la que deja al pie.
            Vec3 cresta = fr.add(f.scale(perfil.adelanta(1.0F))).add(0, alto, 0);
            for (int i = 0; i < 12; i++) {
                float x0 = -AtlahuaEntity.TSUNAMI_ANCHO / 2 + AtlahuaEntity.TSUNAMI_ANCHO * i / 12;
                float x1 = x0 + AtlahuaEntity.TSUNAMI_ANCHO / 12;
                MiniJefeDibujo.cuadro(buf, p, cresta.add(lado.scale(x0)).add(f.scale(-0.8)), cresta.add(lado.scale(x1)).add(f.scale(-0.8)),
                        cresta.add(lado.scale(x1)).add(f.scale(0.9)).add(0, -0.3, 0), cresta.add(lado.scale(x0)).add(f.scale(0.9)).add(0, -0.3, 0),
                        g * 3 + i * 0.5F, 0, g * 3 + i * 0.5F + 0.5F, 1, MiniJefeDibujo.color(0xFFFFFF, alfa));
                MiniJefeDibujo.cuadro(buf, p, fr.add(lado.scale(x0)).add(f.scale(-2.5)).add(0, 0.05, 0),
                        fr.add(lado.scale(x1)).add(f.scale(-2.5)).add(0, 0.05, 0), fr.add(lado.scale(x1)).add(f.scale(0.5)).add(0, 0.05, 0),
                        fr.add(lado.scale(x0)).add(f.scale(0.5)).add(0, 0.05, 0), -g * 2 + i * 0.5F, 0, -g * 2 + i * 0.5F + 0.5F, 1,
                        MiniJefeDibujo.color(0xFFFFFF, 0.8F * alfa));
            }
        });
    }
}
