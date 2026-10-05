package com.atalaya.client;

import com.atalaya.Atalaya;
import com.atalaya.entity.AeralisEntity;
import com.atalaya.entity.AeralisGeometria;
import com.atalaya.entity.NucleoVientoEntity;
import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import com.mojang.math.Axis;
import net.minecraft.client.renderer.SubmitNodeCollector;
import net.minecraft.client.renderer.entity.EntityRenderer;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.state.EntityRenderState;
import net.minecraft.client.renderer.rendertype.RenderType;
import net.minecraft.client.renderer.rendertype.RenderTypes;
import net.minecraft.client.renderer.state.level.CameraRenderState;
import net.minecraft.resources.Identifier;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.phys.Vec3;

/**
 * Un nucleo de viento del Juicio, desde el remake: un cristal de tormenta de
 * ocho caras (nucleo.png, tenido del color de la fase) que gira flotando dentro
 * de una cascara de luz que gira al reves, con una columna de luz que sube al
 * cielo (con 30 o 40 jugadores, hay que encontrarlos rapido) y un RAYO que lo
 * ata al pecho de Aeralis: al romperlo, el rayo se corta. Con cada golpe destella
 * y se encoge un poco; cuanto mas dano lleva, mas tiembla.
 */
public class NucleoVientoRenderer extends EntityRenderer<NucleoVientoEntity, NucleoVientoRenderer.Estado> {

    private static final RenderType CRISTAL = RenderTypes.entityTranslucentEmissive(
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "textures/entity/aeralis/nucleo.png"));
    private static final RenderType COLUMNA = RenderTypes.entityTranslucentEmissive(
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "textures/entity/aeralis/tornado.png"));
    private static final RenderType BRILLO = RenderTypes.eyes(
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "textures/entity/aeralis/nucleo_brillo.png"));
    private static final RenderType RAYO = RenderTypes.entityTranslucentEmissive(
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "textures/entity/aeralis/rayo.png"));

    public static class Estado extends EntityRenderState {
        public float edad;
        public float destello;
        public float dano;
        public int color = 0xFFFFFF;
        public int id;
        /** Del cristal al pecho de Aeralis (null si no se la ve). */
        public Vec3 alPecho;
    }

    public NucleoVientoRenderer(EntityRendererProvider.Context contexto) {
        super(contexto);
    }

    @Override
    public Estado createRenderState() {
        return new Estado();
    }

    @Override
    public void extractRenderState(NucleoVientoEntity n, Estado s, float parcial) {
        super.extractRenderState(n, s, parcial);
        s.edad = n.tickCount + parcial;
        s.destello = Mth.clamp(1.0F - (n.tickCount + parcial - n.ultimoGolpe) / 6.0F, 0.0F, 1.0F);
        s.dano = n.getGolpes() / (float) Math.max(1, n.getAguanta());
        s.color = AeralisDibujo.fase(n.getFase());
        s.id = n.getId();
        Entity d = n.level().getEntity(n.getIdDuena());
        if (d instanceof AeralisEntity a && a.isAlive()) {
            Vec3 pecho = a.puntoMundo(AeralisGeometria.NUCLEO);
            Vec3 aqui = n.getPosition(parcial).add(0, 1.2, 0);
            s.alPecho = pecho.subtract(aqui);
        } else {
            s.alPecho = null;
        }
    }

    @Override
    protected boolean affectedByCulling(NucleoVientoEntity n) {
        return false;
    }

    @Override
    public void submit(Estado s, PoseStack pose, SubmitNodeCollector colector, CameraRenderState camara) {
        int c = s.color;
        int claro = AeralisDibujo.claro(c, 0.5F);
        // La columna de luz que sube al cielo: se ve desde toda la arena.
        float r = 0.35F + 0.1F * s.destello;
        float v0 = -s.edad * 0.05F;
        colector.submitCustomGeometry(pose, COLUMNA, (p, buf) -> {
            float alto = 36.0F;
            for (int k = 0; k < 2; k++) {
                float ax = k == 0 ? r : 0.0F;
                float az = k == 0 ? 0.0F : r;
                float v1 = v0 + 6.0F;
                AeralisDibujo.vertice(buf, p, -ax, 0.8, -az, 0.0F, v0, AeralisDibujo.r(claro), AeralisDibujo.g(claro), AeralisDibujo.b(claro),
                        200, AeralisDibujo.A_PLENA_LUZ, 0, 1, 0);
                AeralisDibujo.vertice(buf, p, ax, 0.8, az, 1.0F, v0, AeralisDibujo.r(claro), AeralisDibujo.g(claro), AeralisDibujo.b(claro),
                        200, AeralisDibujo.A_PLENA_LUZ, 0, 1, 0);
                AeralisDibujo.vertice(buf, p, ax, alto, az, 1.0F, v1, AeralisDibujo.r(claro), AeralisDibujo.g(claro), AeralisDibujo.b(claro),
                        0, AeralisDibujo.A_PLENA_LUZ, 0, 1, 0);
                AeralisDibujo.vertice(buf, p, -ax, alto, -az, 0.0F, v1, AeralisDibujo.r(claro), AeralisDibujo.g(claro), AeralisDibujo.b(claro),
                        0, AeralisDibujo.A_PLENA_LUZ, 0, 1, 0);
            }
        });
        // El rayo que lo ata a su pecho: cambia de quiebro cada dos ticks.
        if (s.alPecho != null) {
            Vec3 hasta = s.alPecho;
            Vec3 ojo = camara.pos.subtract(s.x, s.y, s.z);
            long semilla = (long) (s.edad / 2.0F) * 7 + s.id * 131L;
            colector.submitCustomGeometry(pose, RAYO, (p, buf) -> {
                Vec3 desde = new Vec3(0, 1.2, 0);
                // El rayo grueso del color de la fase y su alma blanca encima.
                AeralisDibujo.rayo(buf, p, desde, desde.add(hasta), ojo, semilla, 14, 0.8, 0.32F, AeralisDibujo.claro(c, 0.3F), 230);
                AeralisDibujo.rayo(buf, p, desde, desde.add(hasta), ojo, semilla, 14, 0.8, 0.12F, 0xFFFFFF, 255);
            });
        }
        pose.pushPose();
        pose.translate(0.0F, 1.2F + 0.2F * Mth.sin(s.edad * 0.12F), 0.0F);
        float tiembla = s.dano > 0.5F ? 0.05F * Mth.sin(s.edad * 3.1F) * s.dano : 0.0F;
        pose.pushPose();
        pose.mulPose(Axis.YP.rotation(s.edad * 0.08F));
        pose.translate(tiembla, 0, 0);
        float m = 0.95F * (1.0F - 0.15F * s.destello);
        int luzCristal = (int) (200 + 55 * s.destello);
        colector.submitCustomGeometry(pose, CRISTAL, (p, buf) -> octaedro(buf, p, m, 1.8F * m, AeralisDibujo.claro(c, 0.2F), luzCristal));
        pose.popPose();
        pose.mulPose(Axis.YP.rotation(-s.edad * 0.11F));
        pose.mulPose(Axis.ZP.rotation(0.8F - s.edad * 0.04F));
        float h = 1.2F + tiembla + 0.15F * s.destello;
        int luz = (int) (150 + 105 * s.destello);
        colector.submitCustomGeometry(pose, BRILLO, (p, buf) ->
                AeralisDibujo.cubo(buf, p, h, luz, luz, luz, 255, AeralisDibujo.A_PLENA_LUZ));
        pose.popPose();
        super.submit(s, pose, colector, camara);
    }

    /** Un cristal de ocho caras: cuatro arriba y cuatro abajo, de anchura r y semialtura alto. */
    private static void octaedro(VertexConsumer buf, PoseStack.Pose p, float r, float alto, int c, int alfa) {
        Vec3 arriba = new Vec3(0, alto, 0);
        Vec3 abajo = new Vec3(0, -alto, 0);
        Vec3[] anillo = {new Vec3(r, 0, 0), new Vec3(0, 0, r), new Vec3(-r, 0, 0), new Vec3(0, 0, -r)};
        int rr = AeralisDibujo.r(c), gg = AeralisDibujo.g(c), bb = AeralisDibujo.b(c);
        for (int k = 0; k < 4; k++) {
            Vec3 a = anillo[k], b = anillo[(k + 1) % 4];
            for (Vec3 pico : new Vec3[]{arriba, abajo}) {
                Vec3 n = b.subtract(a).cross(pico.subtract(a)).normalize();
                float v = pico == arriba ? 0.0F : 1.0F;
                // Por las dos caras: asi da igual el sentido de giro de los vertices.
                for (Vec3[] t : new Vec3[][]{{a, b, pico}, {b, a, pico}}) {
                    AeralisDibujo.vertice(buf, p, t[0].x, t[0].y, t[0].z, 0.0F, 0.5F, rr, gg, bb, alfa, AeralisDibujo.A_PLENA_LUZ,
                            (float) n.x, (float) n.y, (float) n.z);
                    AeralisDibujo.vertice(buf, p, t[1].x, t[1].y, t[1].z, 1.0F, 0.5F, rr, gg, bb, alfa, AeralisDibujo.A_PLENA_LUZ,
                            (float) n.x, (float) n.y, (float) n.z);
                    AeralisDibujo.vertice(buf, p, t[2].x, t[2].y, t[2].z, 0.5F, v, rr, gg, bb, alfa, AeralisDibujo.A_PLENA_LUZ,
                            (float) n.x, (float) n.y, (float) n.z);
                    AeralisDibujo.vertice(buf, p, t[2].x, t[2].y, t[2].z, 0.5F, v, rr, gg, bb, alfa, AeralisDibujo.A_PLENA_LUZ,
                            (float) n.x, (float) n.y, (float) n.z);
                }
            }
        }
    }
}
