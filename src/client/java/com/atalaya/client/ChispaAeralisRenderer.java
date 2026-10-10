package com.atalaya.client;

import com.atalaya.Atalaya;
import com.atalaya.entity.ChispaAeralisEntity;
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
import net.minecraft.world.entity.Entity;
import net.minecraft.world.phys.Vec3;

/**
 * La Chispa de Aeralis (aeralis_minijuegos.py): una bola de rayos que
 * chisporrotea (chispa.png, cuatro cuadros que se suceden; cargada, la fila de
 * oro, y crece) con un halo, de cara a quien mira. Encima, la cuenta atras en
 * cifras grandes (chispa_cuenta.png: 3, 2, 1) cuando le quedan tres segundos o
 * menos. Y en el suelo, alrededor de quien la lleva, el aro que chisporrotea
 * (chispa_aro.png) hasta donde llega al reventar: violeta, de oro cargada y, el
 * ultimo segundo, rojo y parpadeando.
 */
public class ChispaAeralisRenderer extends EntityRenderer<ChispaAeralisEntity, ChispaAeralisRenderer.Estado> {

    private static final RenderType ESTRELLA = RenderTypes.entityTranslucentEmissive(tex("chispa"));
    private static final RenderType CUENTA = RenderTypes.entityTranslucentEmissive(tex("chispa_cuenta"));
    private static final RenderType ARO = RenderTypes.entityTranslucentEmissive(tex("chispa_aro"));
    /** Hasta donde llega al reventar (ChispaAeralis.REVIENTA). */
    private static final float REVIENTA = 3.0F;

    private static Identifier tex(String nombre) {
        return Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "textures/entity/aeralis/" + nombre + ".png");
    }

    public static class Estado extends EntityRenderState {
        public float edad;
        public boolean cargada;
        /** Los segundos que le quedan (0: no cuenta). */
        public int segundos;
        /** Donde esta el suelo de quien la lleva, desde ella (NaN: nadie la lleva). */
        public float suelo = Float.NaN;
    }

    public ChispaAeralisRenderer(EntityRendererProvider.Context contexto) {
        super(contexto);
    }

    @Override
    public Estado createRenderState() {
        return new Estado();
    }

    @Override
    public void extractRenderState(ChispaAeralisEntity c, Estado s, float parcial) {
        super.extractRenderState(c, s, parcial);
        s.edad = c.tickCount + parcial;
        s.cargada = c.cargada();
        long fin = c.getFin();
        s.segundos = fin > 0 && c.getPortador() >= 0 ? (int) Math.ceil((fin - (c.level().getGameTime() + parcial)) / 20.0) : 0;
        Entity quien = c.getPortador() >= 0 ? c.level().getEntity(c.getPortador()) : null;
        s.suelo = quien != null ? (float) (Mth.lerp(parcial, quien.yo, quien.getY()) - Mth.lerp(parcial, c.yo, c.getY())) : Float.NaN;
    }

    @Override
    protected boolean affectedByCulling(ChispaAeralisEntity c) {
        return false;
    }

    @Override
    public void submit(Estado s, PoseStack pose, SubmitNodeCollector colector, CameraRenderState camara) {
        Vec3 ojo = camara.pos.subtract(s.x, s.y, s.z);
        Vec3 c = new Vec3(0, 0.3, 0);
        int cuadro = ((int) (s.edad / 2)) % 4;
        float u0 = cuadro * 0.25F;
        float vAbajo = s.cargada ? 1.0F : 0.5F;
        float late = 1.0F + 0.12F * Mth.sin(s.edad * 1.3F);
        float m = (s.cargada ? 0.8F : 0.55F) * late;
        float giro = s.edad * 0.05F;
        colector.submitCustomGeometry(pose, ESTRELLA, (p, buf) -> {
            cartel(buf, p, c, ojo, m * 2.0F, -giro, u0, u0 + 0.25F, vAbajo, vAbajo - 0.5F, 0xFFFFFF, 60);
            cartel(buf, p, c, ojo, m, giro * 0.3F, u0, u0 + 0.25F, vAbajo, vAbajo - 0.5F, 0xFFFFFF, 255);
        });
        if (s.segundos >= 1 && s.segundos <= 3) {
            // 3, 2, 1: en la textura van en ese orden.
            int k = 3 - s.segundos;
            float cu0 = k / 3.0F;
            Vec3 arriba = new Vec3(0, 1.25, 0);
            int rojo = s.segundos == 1 && ((int) (s.edad / 3)) % 2 == 0 ? 0xFF8080 : 0xFFFFFF;
            float salta = 0.5F + 0.06F * Math.max(0.0F, 1.0F - (s.edad % 20.0F) / 6.0F);
            colector.submitCustomGeometry(pose, CUENTA, (p, buf) ->
                    cartel(buf, p, arriba, ojo, salta, 0.0F, cu0, cu0 + 1 / 3.0F, 1.0F, 0.0F, rojo, 255));
        }
        if (!Float.isNaN(s.suelo) && s.segundos > 0) {
            // El aro del suelo: hasta donde llega si revienta.
            boolean ultimo = s.segundos <= 1;
            int color = ultimo ? (((int) (s.edad / 2)) % 2 == 0 ? 0xFF5A5A : 0xFFB0A0) : s.cargada ? 0xFFD86A : 0xC8A8FF;
            float r = REVIENTA * (1.0F + 0.03F * Mth.sin(s.edad * (ultimo ? 1.4F : 0.5F)));
            int alfa = ultimo ? 235 : 190;
            float y = s.suelo + 0.06F;
            colector.submitCustomGeometry(pose, ARO, (p, buf) -> NereaDibujo.suelo(buf, p, 0.0, y, 0.0, r, s.edad * 0.04F, color, alfa));
        }
        super.submit(s, pose, colector, camara);
    }

    /** Un cuadrado de cara a quien mira, de medio lado m, girado en su plano, con su trozo de textura. */
    private static void cartel(VertexConsumer buf, PoseStack.Pose p, Vec3 c, Vec3 ojo, float m, float giro, float u0, float u1,
                               float v0, float v1, int color, int alfa) {
        Vec3 haciaOjo = ojo.subtract(c);
        if (haciaOjo.lengthSqr() < 1.0E-6) {
            return;
        }
        Vec3 d = haciaOjo.normalize();
        Vec3 der = d.cross(new Vec3(0, 1, 0));
        der = der.lengthSqr() < 1.0E-6 ? new Vec3(1, 0, 0) : der.normalize();
        Vec3 arr = der.cross(d).normalize();
        double co = Math.cos(giro), si = Math.sin(giro);
        Vec3 a = der.scale(co * m).add(arr.scale(si * m));
        Vec3 b = der.scale(-si * m).add(arr.scale(co * m));
        NovilisDibujo.cara(buf, p, ojo, c.subtract(a).subtract(b), c.add(a).subtract(b), c.add(a).add(b), c.subtract(a).add(b),
                u0, u1, v0, v1, color, alfa, alfa);
    }
}
