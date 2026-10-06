package com.atalaya.client;

import com.atalaya.entity.NereaEntity;
import com.atalaya.entity.OlaNereaEntity;
import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import net.minecraft.client.renderer.SubmitNodeCollector;
import net.minecraft.client.renderer.entity.EntityRenderer;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.state.EntityRenderState;
import net.minecraft.client.renderer.state.level.CameraRenderState;
import net.minecraft.util.Mth;
import net.minecraft.world.phys.Vec3;

/**
 * Una pared de agua de Nerea (OlaNereaEntity): la del Rompeolas y la Gran
 * Marea. De perfil es una ola que rompe: la ladera de atras, la cresta de
 * espuma y el labio que se riza hacia delante, y delante la cara casi
 * vertical; detras deja la estela de espuma en el suelo. La de la Marea se
 * corta en el hueco (con los bordes que se derraman) y, por delante, sigue
 * marcando el paso en el suelo.
 *
 * Esta viva: la cresta sube y baja en ondas que corren de lado a lado, el labio
 * se riza y se recoge, y por encima del agua (ola.png) suben deprisa encajes de
 * espuma (ola_flujo.png), que es lo que hace que se vea agua que se levanta y
 * no una pared que se desliza. A plena luz: tiene que verse de noche.
 */
public class OlaNereaRenderer extends EntityRenderer<OlaNereaEntity, OlaNereaRenderer.Estado> {

    /** El perfil de la ola (adelante, alto) en partes del alto, de la punta del labio a la base de atras, y su v. */
    private static final float[][] LADERA = {{0.36F, 0.66F, 0.10F}, {0.26F, 0.88F, 0.03F}, {-0.08F, 1.0F, 0.0F},
            {-0.6F, 0.78F, 0.3F}, {-1.3F, 0.38F, 0.62F}, {-2.2F, 0.0F, 1.0F}};
    /** La cara de delante: de la cresta a la base. */
    private static final float[][] CARA = {{-0.08F, 1.0F, 0.0F}, {-0.04F, 0.72F, 0.25F}, {0.02F, 0.38F, 0.6F},
            {0.0F, 0.0F, 1.0F}};
    /** Bloques de pared que cubre la textura del agua a lo ancho, y la del flujo. */
    private static final float TEXTURA_ANCHO = 6.0F;
    private static final float FLUJO_ANCHO = 4.0F;
    /** Lo deprisa que sube el flujo por la cara (alturas de textura por tick). */
    private static final float FLUJO_SUBE = 0.11F;
    /** Columnas de la malla: una cada tantos bloques. */
    private static final float PASO = 1.6F;

    public static class Estado extends EntityRenderState {
        public float edad;
        public float rumbo;
        public float ancho;
        public float alto;
        public float largo;
        public float frente;
        public float viaje;
        public float hueco;
        public float huecoAncho;
    }

    public OlaNereaRenderer(EntityRendererProvider.Context contexto) {
        super(contexto);
    }

    @Override
    public Estado createRenderState() {
        return new Estado();
    }

    @Override
    public void extractRenderState(OlaNereaEntity o, Estado s, float parcial) {
        super.extractRenderState(o, s, parcial);
        s.edad = o.tickCount + parcial;
        s.rumbo = o.getYRot();
        s.ancho = o.getAncho();
        s.alto = o.getAlto();
        s.largo = o.getLargo();
        s.frente = o.frente(s.edad);
        s.viaje = o.viaje();
        s.hueco = o.getHueco();
        s.huecoAncho = o.getHuecoAncho();
    }

    @Override
    protected boolean affectedByCulling(OlaNereaEntity o) {
        return false;
    }

    @Override
    public void submit(Estado s, PoseStack pose, SubmitNodeCollector colector, CameraRenderState camara) {
        float b = s.rumbo * Mth.DEG_TO_RAD;
        Vec3 dir = new Vec3(-Mth.sin(b), 0, Mth.cos(b));
        Vec3 lado = OlaNereaEntity.lado(dir);
        boolean marea = s.huecoAncho > 0.0F;
        // Sube al nacer (la Marea, mas despacio) y al llegar al final se hunde y se apaga.
        float sube = Mth.clamp(s.edad / (marea ? 6.0F : 2.0F), 0.0F, 1.0F);
        sube = 1.0F - (1.0F - sube) * (1.0F - sube);
        float apaga = Mth.clamp((s.edad - s.viaje) / OlaNereaEntity.APAGA, 0.0F, 1.0F);
        float alto = s.alto * (0.25F + 0.75F * sube) * (1.0F - 0.7F * apaga);
        float alfa = 1.0F - apaga;
        if (alfa <= 0.01F) {
            return;
        }
        float f = s.frente;
        float[][] tramos = marea
                ? new float[][]{{-s.ancho, s.hueco - s.huecoAncho / 2.0F}, {s.hueco + s.huecoAncho / 2.0F, s.ancho}}
                : new float[][]{{-s.ancho, s.ancho}};
        Ola ola = new Ola(dir, lado, f, alto, s.edad);
        colector.submitCustomGeometry(pose, NereaDibujo.AGUA, (p, buf) -> {
            for (float[] t : tramos) {
                if (t[1] - t[0] < 0.2F) {
                    continue;
                }
                // El agua corre de lado a lado, despacio, como la corriente de la ola.
                float desliza = s.edad * 0.012F;
                ola.pared(buf, p, t[0], t[1], LADERA, TEXTURA_ANCHO, desliza, 1.0F, 0.0F, (int) (195 * alfa));
                ola.pared(buf, p, t[0], t[1], CARA, TEXTURA_ANCHO, desliza, 1.0F, 0.0F, (int) (220 * alfa));
            }
        });
        // El flujo: encajes de espuma que suben deprisa por la cara y por la ladera.
        colector.submitCustomGeometry(pose, NereaDibujo.FLUJO, (p, buf) -> {
            float vAlto = Math.max(1.0F, alto / 3.0F);
            for (float[] t : tramos) {
                if (t[1] - t[0] < 0.2F) {
                    continue;
                }
                ola.pared(buf, p, t[0], t[1], CARA, FLUJO_ANCHO, -s.edad * 0.02F, vAlto, s.edad * FLUJO_SUBE, (int) (170 * alfa));
                ola.pared(buf, p, t[0], t[1], LADERA, FLUJO_ANCHO, s.edad * 0.02F, vAlto, s.edad * FLUJO_SUBE * 0.7F,
                        (int) (120 * alfa));
            }
        });
        // La estela de espuma en el suelo: lo que la ola ha dejado atras.
        float desde = Math.max(0.0F, f - (marea ? 16.0F : 12.0F));
        if (f - desde > 0.3F) {
            colector.submitCustomGeometry(pose, NereaDibujo.ESTELA, (p, buf) -> {
                for (float[] t : tramos) {
                    float medio = (t[0] + t[1]) / 2.0F;
                    float w = (t[1] - t[0]) / 2.0F;
                    if (w < 0.1F) {
                        continue;
                    }
                    Vec3 a = dir.scale(desde).add(lado.scale(medio)).add(0, 0.06, 0);
                    Vec3 z = dir.scale(f).add(lado.scale(medio)).add(0, 0.06, 0);
                    NereaDibujo.tira(buf, p, a, z, w, desde / 4.0F, f / 4.0F, 0xFFFFFF, (int) (110 * alfa));
                }
            });
        }
        if (marea && f < s.largo) {
            // El paso que sigue abierto por delante.
            Vec3 a = dir.scale(f + 1.0F).add(lado.scale(s.hueco)).add(0, 0.07, 0);
            Vec3 z = dir.scale(s.largo).add(lado.scale(s.hueco)).add(0, 0.07, 0);
            int brillo = (int) ((170 + 60 * Mth.sin(s.edad * 0.3F)) * alfa);
            colector.submitCustomGeometry(pose, NereaDibujo.SENDERO, (p, buf) ->
                    NereaDibujo.tira(buf, p, a, z, NereaEntity.MAREA_HUECO / 2.0F, (f + 1.0F) / 5.0F - s.edad * 0.02F,
                            s.largo / 5.0F - s.edad * 0.02F, 0xFFFFFF, brillo));
        }
        super.submit(s, pose, colector, camara);
    }

    /** La forma de la ola en este fotograma: donde va, lo alta que es y como ondula. */
    private record Ola(Vec3 dir, Vec3 lado, float f, float alto, float edad) {

        /**
         * Una lamina de la ola de lado a lado (de l0 a l1), siguiendo el perfil
         * dado. La textura: "anchoTextura" bloques a lo ancho, corrida "u0"; a lo
         * alto, "vAlto" repeticiones corridas "vSube" hacia arriba.
         */
        void pared(VertexConsumer buf, PoseStack.Pose p, float l0, float l1, float[][] perfil, float anchoTextura,
                   float u0, float vAlto, float vSube, int alfa) {
            int columnas = Math.max(1, Mth.ceil((l1 - l0) / PASO));
            for (int i = 0; i < columnas; i++) {
                float la = l0 + (l1 - l0) * i / columnas;
                float lb = l0 + (l1 - l0) * (i + 1) / columnas;
                float ua = la / anchoTextura + u0;
                float ub = lb / anchoTextura + u0;
                for (int j = 0; j < perfil.length - 1; j++) {
                    float[] q0 = perfil[j];
                    float[] q1 = perfil[j + 1];
                    Vec3 a0 = punto(la, l0, l1, q0);
                    Vec3 b0 = punto(lb, l0, l1, q0);
                    Vec3 b1 = punto(lb, l0, l1, q1);
                    Vec3 a1 = punto(la, l0, l1, q1);
                    float v0 = q0[2] * vAlto + vSube;
                    float v1 = q1[2] * vAlto + vSube;
                    NereaDibujo.cuadro(buf, p, a0, b0, b1, a1, ua, ub, v0, v1, 0xFFFFFF, alfa, alfa);
                }
            }
        }

        /**
         * Un punto del perfil: "q" es (adelante, alto) en partes del alto de esa
         * columna. La cresta sube y baja en ondas que corren de lado a lado, y lo
         * que va por delante de la cresta (el labio) se riza y se recoge.
         */
        private Vec3 punto(float l, float l0, float l1, float[] q) {
            float h = alto * borde(l, l0, l1) * (1.0F + 0.08F * Mth.sin(l * 0.45F - edad * 0.7F));
            float adelante = q[0] > 0.0F ? q[0] * (1.0F + 0.3F * Mth.sin(l * 0.6F + edad * 0.9F)) : q[0];
            return dir.scale(f + adelante * h).add(lado.scale(l)).add(0, q[1] * h + 0.02, 0);
        }

        /** Cerca de los extremos de un tramo la ola baja: el agua se derrama por el borde. */
        private static float borde(float l, float l0, float l1) {
            float d = Math.min(l - l0, l1 - l) / 2.5F;
            float k = Mth.clamp(d, 0.0F, 1.0F);
            return 0.4F + 0.6F * k * k * (3 - 2 * k);
        }
    }
}
