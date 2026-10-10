package com.atalaya.client;

import com.atalaya.Atalaya;
import com.atalaya.entity.CirculoRayoEntity;
import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
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
 * Un circulo de los Pararrayos (aeralis_minijuegos.py): el sello de tormenta
 * tumbado en el suelo (circulo_rayo.png), que entra creciendo, gira despacio y
 * late cada vez mas deprisa; encima, un aro de luz (circulo_rayo_aro.png) que se
 * va cerrando desde el borde hasta el aro de dentro del sello: cuando lo toca,
 * cae el rayo. El rayo baja del cielo (rayo_columna.png, una tira de cara a
 * quien mira, dos cuadros que se alternan) y el suelo queda quemado con grietas
 * de luz (circulo_rayo_quemado.png) mientras el sello se apaga.
 */
public class CirculoRayoRenderer extends EntityRenderer<CirculoRayoEntity, CirculoRayoRenderer.Estado> {

    private static final RenderType SELLO = RenderTypes.entityTranslucentEmissive(tex("circulo_rayo"));
    private static final RenderType ARO = RenderTypes.entityTranslucentEmissive(tex("circulo_rayo_aro"));
    private static final RenderType QUEMADO = RenderTypes.entityTranslucent(tex("circulo_rayo_quemado"));
    private static final RenderType RAYO = RenderTypes.entityTranslucentEmissive(tex("rayo_columna"));
    /** Donde esta el aro de dentro del sello (de su medio lado): ahi cae el rayo. */
    private static final float ARO_DENTRO = 41.0F / 64.0F;
    /** Lo alto que baja el rayo y lo ancho que es. */
    private static final float RAYO_ALTO = 28.0F;
    private static final float RAYO_ANCHO = 0.8F;

    private static Identifier tex(String nombre) {
        return Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "textures/entity/aeralis/" + nombre + ".png");
    }

    public static class Estado extends EntityRenderState {
        public float edad;
        public int cuenta;
        public float desdeRayo = -1.0F;
        public float giro;
    }

    public CirculoRayoRenderer(EntityRendererProvider.Context contexto) {
        super(contexto);
    }

    @Override
    public Estado createRenderState() {
        return new Estado();
    }

    @Override
    public void extractRenderState(CirculoRayoEntity c, Estado s, float parcial) {
        super.extractRenderState(c, s, parcial);
        s.edad = c.tickCount + parcial;
        s.cuenta = Math.max(1, c.getCuenta());
        s.desdeRayo = c.getCayo() >= 0 ? c.tickCount - c.getCayo() + parcial : -1.0F;
        s.giro = c.getYRot() * Mth.DEG_TO_RAD;
    }

    @Override
    protected boolean affectedByCulling(CirculoRayoEntity c) {
        return false;
    }

    @Override
    public void submit(Estado s, PoseStack pose, SubmitNodeCollector colector, CameraRenderState camara) {
        float r = CirculoRayoEntity.RADIO;
        if (s.desdeRayo < 0.0F) {
            float k = Mth.clamp(s.edad / s.cuenta, 0.0F, 1.0F);
            float entra = Mth.clamp(s.edad / 5.0F, 0.0F, 1.0F);
            float m = r * (0.55F + 0.45F * entra);
            float prisa = 0.25F + 1.1F * k;
            int alfa = (int) ((160 + 90 * (0.5F + 0.5F * Mth.sin(s.edad * prisa))) * entra);
            float giro = s.giro + s.edad * 0.02F;
            colector.submitCustomGeometry(pose, SELLO, (p, buf) -> NereaDibujo.suelo(buf, p, 0.0, 0.06, 0.0, m, giro, 0xFFFFFF, alfa));
            // El aro que se cierra: del borde al aro de dentro, cada vez mas blanco.
            float ma = m * (1.0F - (1.0F - ARO_DENTRO) * k);
            int color = k > 0.8F && ((int) (s.edad / 2)) % 2 == 0 ? 0xFFFFFF : 0xD8C0FF;
            int alfaAro = (int) (230 * entra);
            colector.submitCustomGeometry(pose, ARO, (p, buf) -> NereaDibujo.suelo(buf, p, 0.0, 0.08, 0.0, ma, -giro * 1.5F, color, alfaAro));
            super.submit(s, pose, colector, camara);
            return;
        }
        if (s.desdeRayo < CirculoRayoEntity.QUEMADO) {
            float k = s.desdeRayo / CirculoRayoEntity.QUEMADO;
            int alfa = (int) (240 * (1.0F - k * k));
            colector.submitCustomGeometry(pose, QUEMADO, (p, buf) -> NereaDibujo.suelo(buf, p, 0.0, 0.05, 0.0, r * 1.15F, s.giro, 0xFFFFFF, alfa));
            // El sello se apaga y se abre.
            int alfaSello = (int) (200 * Math.max(0.0F, 1.0F - k * 2.5F));
            if (alfaSello > 0) {
                float m = r * (1.0F + 0.35F * k);
                colector.submitCustomGeometry(pose, SELLO, (p, buf) -> NereaDibujo.suelo(buf, p, 0.0, 0.07, 0.0, m, s.giro, 0xB090FF, alfaSello));
            }
        }
        if (s.desdeRayo < CirculoRayoEntity.RAYO) {
            float k = s.desdeRayo / CirculoRayoEntity.RAYO;
            int alfa = (int) (255 * (1.0F - k * k));
            float u0 = ((int) (s.desdeRayo / 2)) % 2 == 0 ? 0.0F : 0.5F;
            Vec3 ojo = camara.pos.subtract(s.x, s.y, s.z);
            colector.submitCustomGeometry(pose, RAYO, (p, buf) -> {
                columna(buf, p, ojo, 0.0F, RAYO_ALTO * 0.5F, u0, alfa);
                columna(buf, p, ojo, RAYO_ALTO * 0.5F, RAYO_ALTO, u0, alfa);
            });
        }
        super.submit(s, pose, colector, camara);
    }

    /** Un tramo del rayo: una tira vertical de cara a quien mira (gira solo alrededor del eje Y). */
    private static void columna(VertexConsumer buf, PoseStack.Pose p, Vec3 ojo, float y0, float y1, float u0, int alfa) {
        Vec3 d = new Vec3(ojo.x, 0, ojo.z);
        // La derecha de quien mira (asi las cuatro esquinas van en el sentido de la cara de delante).
        Vec3 der = d.lengthSqr() < 1.0E-6 ? new Vec3(1, 0, 0) : new Vec3(d.z, 0, -d.x).normalize();
        double ax = der.x * RAYO_ANCHO;
        double az = der.z * RAYO_ANCHO;
        float u1 = u0 + 0.5F;
        NereaDibujo.vertice(buf, p, -ax, y0, -az, u0, 1.0F, 0xFFFFFF, alfa, 0, 1, 0);
        NereaDibujo.vertice(buf, p, ax, y0, az, u1, 1.0F, 0xFFFFFF, alfa, 0, 1, 0);
        NereaDibujo.vertice(buf, p, ax, y1, az, u1, 0.0F, 0xFFFFFF, alfa, 0, 1, 0);
        NereaDibujo.vertice(buf, p, -ax, y1, -az, u0, 0.0F, 0xFFFFFF, alfa, 0, 1, 0);
    }
}
