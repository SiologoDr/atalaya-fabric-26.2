package com.atalaya.client;

import com.atalaya.Atalaya;
import com.atalaya.entity.TotemSelloEntity;
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
import net.minecraft.util.Mth;
import net.minecraft.world.phys.Vec3;

import java.util.ArrayList;
import java.util.List;

/**
 * Un totem del Sello de la Tierra: la base, tres tramos de piedra verde (cada
 * cara con su glifo de totem.png: el numero maya, el ojo, la espiral y la
 * mascara del jaguar), las bandas de oro y el remate. Vivo, los glifos
 * brillan (totem_brillo), late con cada golpe y sube un haz de luz al cielo;
 * roto, se le apagan los glifos, se raja y el tramo de arriba se cae.
 */
public class TotemSelloRenderer extends EntityRenderer<TotemSelloEntity, TotemSelloRenderer.Estado> {

    private static final RenderType PIEDRA = RenderTypes.entityCutout(
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "textures/entity/rajang/totem.png"));
    private static final RenderType GLIFOS = RenderTypes.eyes(
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "textures/entity/rajang/totem_brillo.png"));
    private static final RenderType ORO = RenderTypes.entityCutout(
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "textures/entity/rajang/oro.png"));
    private static final RenderType HAZ = RenderTypes.entityTranslucentEmissive(
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "textures/entity/rajang/haz.png"));

    private static final double BASE = 0.45;
    private static final double TRAMO = 1.3;
    private static final double BANDA = 0.18;
    private static final double ANCHO = 1.5;

    public static class Estado extends EntityRenderState {
        public float edad;
        public float destello;
        public float cambio;
        public boolean roto;
        public float rumbo;
        public float dano;
    }

    public TotemSelloRenderer(EntityRendererProvider.Context contexto) {
        super(contexto);
    }

    @Override
    public Estado createRenderState() {
        return new Estado();
    }

    @Override
    public void extractRenderState(TotemSelloEntity t, Estado s, float parcial) {
        super.extractRenderState(t, s, parcial);
        s.edad = t.tickCount + parcial;
        s.destello = Mth.clamp(1.0F - (t.tickCount + parcial - t.ultimoGolpe) / 6.0F, 0.0F, 1.0F);
        s.cambio = Mth.clamp((t.tickCount + parcial - t.cambio) / 10.0F, 0.0F, 1.0F);
        s.roto = t.isRoto();
        s.rumbo = t.getYRot();
        s.dano = t.getGolpes() / (float) Math.max(1, t.getAguanta());
    }

    @Override
    protected boolean affectedByCulling(TotemSelloEntity t) {
        return false;
    }

    @Override
    public void submit(Estado s, PoseStack pose, SubmitNodeCollector colector, CameraRenderState camara) {
        List<RajangDibujo.Cara> piedra = new ArrayList<>();
        List<RajangDibujo.Cara> glifos = new ArrayList<>();
        List<RajangDibujo.Cara> oro = new ArrayList<>();
        // La base, mas ancha.
        double b = ANCHO * 0.68;
        RajangDibujo.caja(piedra, -b, 0, -b, b, BASE, b, RajangDibujo.uv(0.25F, 0.0F, 0.5F, 0.11F),
                RajangDibujo.uv(0.25F, 0.2F, 0.5F, 0.45F));
        int tramos = s.roto ? 2 : 3;
        double y = BASE;
        for (int t = 0; t < tramos; t++) {
            double w = ANCHO * (1.0 - 0.05 * t) / 2;
            Vec3[] q = {new Vec3(-w, y, -w), new Vec3(w, y, -w), new Vec3(w, y, w), new Vec3(-w, y, w)};
            for (int k = 0; k < 4; k++) {
                int glifo = (k + t) % 4;
                float u0 = glifo / 4.0F;
                float u1 = (glifo + 1) / 4.0F;
                float v0 = s.roto ? 0.5F : 0.0F;
                float v1 = v0 + 0.5F;
                Vec3 a = q[k];
                Vec3 c = q[(k + 1) % 4];
                RajangDibujo.Cara cara = new RajangDibujo.Cara(a, c, c.add(0, TRAMO, 0), a.add(0, TRAMO, 0),
                        RajangDibujo.uv(u0, v0, u1, v1));
                piedra.add(cara);
                glifos.add(cara);
            }
            y += TRAMO;
            double wb = w * 1.12;
            RajangDibujo.caja(oro, -wb, y - 0.05, -wb, wb, y + BANDA, wb, RajangDibujo.uv(0, 0, 1, 1), RajangDibujo.uv(0, 0, 1, 1));
            y += BANDA;
        }
        if (!s.roto) {
            double w = ANCHO * 0.58;
            RajangDibujo.caja(piedra, -w, y, -w, w, y + 0.35, w, RajangDibujo.uv(0.75F, 0.0F, 1.0F, 0.1F),
                    RajangDibujo.uv(0.25F, 0.2F, 0.5F, 0.45F));
        } else {
            // El tramo de arriba, caido de lado junto a la base.
            double w = ANCHO * 0.45;
            float en = s.cambio;
            List<RajangDibujo.Cara> caido = new ArrayList<>();
            RajangDibujo.caja(caido, -w, 0, -w, w, TRAMO, w, RajangDibujo.uv(0.5F, 0.5F, 0.75F, 1.0F), RajangDibujo.uv(0.5F, 0.5F, 0.75F, 0.6F));
            for (RajangDibujo.Cara c : caido) {
                piedra.add(new RajangDibujo.Cara(caer(c.a(), en), caer(c.b(), en), caer(c.c(), en), caer(c.d(), en), c.uv()));
            }
        }
        float tiembla = !s.roto && s.dano > 0.5F ? 0.03F * Mth.sin(s.edad * 3.1F) * s.dano : 0.0F;
        pose.pushPose();
        pose.mulPose(Axis.YP.rotationDegrees(-s.rumbo));
        pose.translate(tiembla, 0, 0);
        if (s.destello > 0) {
            float e = 1.0F + 0.05F * s.destello;
            pose.scale(e, 1.0F, e);
        }
        int luz = s.lightCoords;
        colector.submitCustomGeometry(pose, PIEDRA, (p, buf) -> RajangDibujo.emitir(buf, p, piedra, 255, 255, 255, 255, luz));
        colector.submitCustomGeometry(pose, ORO, (p, buf) -> RajangDibujo.emitir(buf, p, oro, 255, 255, 255, 255, luz));
        if (!s.roto) {
            float k = 0.75F + 0.25F * Mth.sin(s.edad * 0.15F) + 0.4F * s.destello;
            int g = Mth.clamp((int) (255 * k), 0, 255);
            colector.submitCustomGeometry(pose, GLIFOS, (p, buf) ->
                    RajangDibujo.emitir(buf, p, glifos, g, g, g, 255, AeralisDibujo.A_PLENA_LUZ));
        }
        pose.popPose();
        if (!s.roto) {
            // El haz que sube al cielo: se ve desde toda la arena.
            float r = 0.5F + 0.15F * s.destello;
            float v0 = -s.edad * 0.04F;
            float yb = (float) (BASE + 3 * (TRAMO + BANDA) + 0.4);
            colector.submitCustomGeometry(pose, HAZ, (p, buf) -> {
                for (int k = 0; k < 2; k++) {
                    float ax = k == 0 ? r : 0.0F;
                    float az = k == 0 ? 0.0F : r;
                    AeralisDibujo.vertice(buf, p, -ax, yb, -az, 0.0F, v0, 150, 255, 160, 220, AeralisDibujo.A_PLENA_LUZ, 0, 1, 0);
                    AeralisDibujo.vertice(buf, p, ax, yb, az, 1.0F, v0, 150, 255, 160, 220, AeralisDibujo.A_PLENA_LUZ, 0, 1, 0);
                    AeralisDibujo.vertice(buf, p, ax, yb + 26.0F, az, 1.0F, v0 + 1.0F, 150, 255, 160, 0, AeralisDibujo.A_PLENA_LUZ, 0, 1, 0);
                    AeralisDibujo.vertice(buf, p, -ax, yb + 26.0F, -az, 0.0F, v0 + 1.0F, 150, 255, 160, 0, AeralisDibujo.A_PLENA_LUZ, 0, 1, 0);
                }
            });
        }
        super.submit(s, pose, colector, camara);
    }

    /** El tramo que se cae: gira 80 grados y se aparta a un lado. */
    private static Vec3 caer(Vec3 p, float k) {
        double ang = Math.toRadians(80 * k);
        double y = p.y * Math.cos(ang) - p.x * Math.sin(ang);
        double x = p.y * Math.sin(ang) + p.x * Math.cos(ang);
        return new Vec3(x + 1.1 * k, y + (BASE + 2 * (TRAMO + BANDA)) * (1 - k) + 0.6 * k, p.z);
    }
}
