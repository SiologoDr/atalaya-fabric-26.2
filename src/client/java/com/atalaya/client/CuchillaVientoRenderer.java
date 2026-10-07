package com.atalaya.client;

import com.atalaya.Atalaya;
import com.atalaya.entity.CuchillaVientoEntity;
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
 * La cuchilla de viento: una media luna de aire (cuchilla.png) de cinco
 * bloques, curvada hacia delante, tumbada y de pie a la vez (dos tiras
 * cruzadas) para que se lea desde cualquier lado, con tres ecos detras que
 * hacen de estela. Brilla: hay que verla venir.
 *
 * Desde el remake se tine: las BAJAS van en el color de la fase (se saltan) y
 * las ALTAS en blanco lila (hay que agacharse). Se distinguen de un vistazo. Lo
 * que se ve de pie mide lo mismo que lo que corta (medioAlto).
 */
public class CuchillaVientoRenderer extends EntityRenderer<CuchillaVientoEntity, CuchillaVientoRenderer.Estado> {

    private static final RenderType TIPO = RenderTypes.entityTranslucentEmissive(
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "textures/entity/aeralis/cuchilla.png"));
    private static final int TRAMOS = 12;
    private static final float MEDIO_ANCHO = 2.6F;
    /** El blanco lila de las cuchillas altas. */
    private static final int ALTA = 0xECE8FF;

    public static class Estado extends EntityRenderState {
        public float rumbo;
        public float edad;
        public int color = 0xFFFFFF;
        public float medioAlto = 0.25F;
    }

    public CuchillaVientoRenderer(EntityRendererProvider.Context contexto) {
        super(contexto);
    }

    @Override
    public Estado createRenderState() {
        return new Estado();
    }

    @Override
    public void extractRenderState(CuchillaVientoEntity c, Estado s, float parcial) {
        super.extractRenderState(c, s, parcial);
        s.rumbo = c.getYRot(parcial);
        s.edad = c.tickCount + parcial;
        s.color = c.isAlta() ? ALTA : AeralisDibujo.claro(AeralisDibujo.fase(c.getFase()), 0.15F);
        s.medioAlto = (float) c.medioAlto();
    }

    @Override
    public void submit(Estado s, PoseStack pose, SubmitNodeCollector colector, CameraRenderState camara) {
        float b = s.rumbo * Mth.DEG_TO_RAD;
        Vec3 frente = new Vec3(-Mth.sin(b), 0, Mth.cos(b));
        Vec3 lado = new Vec3(Mth.cos(b), 0, Mth.sin(b));
        Vec3 arriba = new Vec3(0, 1, 0);
        // Aparece de golpe y tiembla un poco al cortar el aire.
        float nace = Mth.clamp(s.edad / 3.0F, 0.0F, 1.0F);
        float temblor = 1.0F + 0.06F * Mth.sin(s.edad * 2.7F);
        int color = s.color;
        float alto = s.medioAlto;
        colector.submitCustomGeometry(pose, TIPO, (p, buf) -> {
            // La cuchilla y tres ecos detras: la estela que deja al cortar el aire.
            for (int k = 0; k < 4; k++) {
                Vec3 atras = frente.scale(-1.1 * k);
                float a = nace * new float[]{1.0F, 0.5F, 0.25F, 0.1F}[k];
                float e = 1.0F - 0.08F * k;
                tira(buf, p, atras, frente, lado.scale(e), frente.scale(0.65 * temblor), a, color);
                tira(buf, p, atras, frente, lado.scale(e), arriba.scale(alto * temblor), a * 0.85F, color);
            }
        });
        super.submit(s, pose, colector, camara);
    }

    /** Una tira curvada de punta a punta: el centro va adelantado, las puntas atras. */
    private static void tira(VertexConsumer buf, PoseStack.Pose p, Vec3 base, Vec3 frente, Vec3 lado, Vec3 grosor, float k, int c) {
        int alfa = (int) (250 * Math.min(1.0F, k));
        int rr = AeralisDibujo.r(c), gg = AeralisDibujo.g(c), bb = AeralisDibujo.b(c);
        for (int i = 0; i < TRAMOS; i++) {
            float u0 = i / (float) TRAMOS;
            float u1 = (i + 1) / (float) TRAMOS;
            Vec3 c0 = base.add(centro(frente, lado, u0));
            Vec3 c1 = base.add(centro(frente, lado, u1));
            AeralisDibujo.vertice(buf, p, c0.x - grosor.x, c0.y - grosor.y, c0.z - grosor.z, u0, 1.0F, rr, gg, bb, alfa,
                    AeralisDibujo.A_PLENA_LUZ, 0, 1, 0);
            AeralisDibujo.vertice(buf, p, c1.x - grosor.x, c1.y - grosor.y, c1.z - grosor.z, u1, 1.0F, rr, gg, bb, alfa,
                    AeralisDibujo.A_PLENA_LUZ, 0, 1, 0);
            AeralisDibujo.vertice(buf, p, c1.x + grosor.x, c1.y + grosor.y, c1.z + grosor.z, u1, 0.0F, rr, gg, bb, alfa,
                    AeralisDibujo.A_PLENA_LUZ, 0, 1, 0);
            AeralisDibujo.vertice(buf, p, c0.x + grosor.x, c0.y + grosor.y, c0.z + grosor.z, u0, 0.0F, rr, gg, bb, alfa,
                    AeralisDibujo.A_PLENA_LUZ, 0, 1, 0);
        }
    }

    private static Vec3 centro(Vec3 frente, Vec3 lado, float u) {
        float x = (u * 2.0F - 1.0F);
        double curva = 0.9 * (1.0 - x * x);
        return lado.scale(x * MEDIO_ANCHO).add(frente.scale(curva));
    }
}
