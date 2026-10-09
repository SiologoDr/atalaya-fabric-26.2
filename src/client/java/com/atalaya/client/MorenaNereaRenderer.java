package com.atalaya.client;

import com.atalaya.entity.MorenaNereaEntity;
import com.mojang.blaze3d.vertex.PoseStack;
import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.SubmitNodeCollector;
import net.minecraft.client.renderer.entity.EntityRenderer;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.state.EntityRenderState;
import net.minecraft.client.renderer.state.level.CameraRenderState;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.phys.Vec3;

/**
 * Un agujero de las Morenas de las Pozas: un brocal de rocas con musgo y el
 * agua oscura que gira dentro. Cuando asoma, la morena (MorenaDibujo):
 *
 *   - SUBE: el agua hierve un instante y la morena revienta hacia arriba con la
 *     boca abierta, pasandose un poco (salto de muelle);
 *   - FUERA: se mece, abre y cierra la boca como respiran las morenas y vuelve
 *     la cabeza hacia el jugador mas cercano. En su ultimo tercio de segundo se
 *     echa atras con la boca abierta de par en par: el aviso de que va a morder;
 *   - BAJA tras morder: se lanza hacia delante, saca la segunda mandibula, cierra
 *     de golpe y se mete;
 *   - BAJA tras un golpe: se pone roja como cualquier bicho al que le pegan, da
 *     un respingo hacia atras y se mete enroscandose.
 */
public class MorenaNereaRenderer extends EntityRenderer<MorenaNereaEntity, MorenaNereaRenderer.Estado> {

    private static final Vec3 ARRIBA = new Vec3(0, 1, 0);
    /** Lo alto que asoma la cabeza (bloques sobre el agua). */
    private static final double ALTO = 2.1;

    public static class Estado extends EntityRenderState {
        public float edad;
        public int fase;
        public float desde;
        public int dura;
        public boolean golpeada;
        /** Hacia donde mira (horizontal): al jugador mas cercano. */
        public Vec3 mira = new Vec3(0, 0, 1);
        /** Una semilla por agujero, para que no se muevan todas igual. */
        public float semilla;
    }

    public MorenaNereaRenderer(EntityRendererProvider.Context contexto) {
        super(contexto);
    }

    @Override
    public Estado createRenderState() {
        return new Estado();
    }

    @Override
    public void extractRenderState(MorenaNereaEntity m, Estado s, float parcial) {
        super.extractRenderState(m, s, parcial);
        s.edad = m.tickCount + parcial;
        s.fase = m.getFase();
        s.desde = m.desde() + parcial;
        s.dura = m.dura();
        s.golpeada = m.golpeada();
        s.semilla = (m.getId() * 37 % 100) / 100.0F * Mth.TWO_PI;
        // Mira al jugador mas cercano (solo se ve: no cambia lo que hace).
        Vec3 c = m.getPosition(parcial);
        Player cerca = null;
        double mejor = 24 * 24;
        if (Minecraft.getInstance().level != null) {
            for (Player p : Minecraft.getInstance().level.players()) {
                double d = p.distanceToSqr(c);
                if (d < mejor && !p.isSpectator()) {
                    mejor = d;
                    cerca = p;
                }
            }
        }
        if (cerca != null) {
            Vec3 d = cerca.getPosition(parcial).subtract(c);
            Vec3 h = new Vec3(d.x, 0, d.z);
            if (h.lengthSqr() > 1.0E-4) {
                s.mira = h.normalize();
            }
        }
    }

    @Override
    protected boolean affectedByCulling(MorenaNereaEntity m) {
        return false;
    }

    @Override
    public void submit(Estado s, PoseStack pose, SubmitNodeCollector colector, CameraRenderState camara) {
        float e = s.edad;
        int luz = s.lightCoords;
        // El agua del agujero y su espuma; hierve mas justo antes de salir.
        boolean hierve = s.fase == MorenaNereaEntity.SUBE && s.desde < 2;
        colector.submitCustomGeometry(pose, NereaDibujo.REMOLINO, (p, buf) ->
                NereaDibujo.suelo(buf, p, 0.0, 0.05, 0.0, 0.95F, -e * (hierve ? 0.25F : 0.05F), 0x3A5A80, 235));
        float m = 0.9F / NereaDibujo.ARO_EN_TEXTURA;
        colector.submitCustomGeometry(pose, NereaDibujo.ARO, (p, buf) ->
                NereaDibujo.suelo(buf, p, 0.0, 0.07, 0.0, m * (hierve ? 1.15F : 1.0F), e * 0.02F, 0xDDF6FF, hierve ? 255 : 170));
        // El brocal: nueve rocas con musgo alrededor.
        colector.submitCustomGeometry(pose, MorenaDibujo.PIEL, (p, buf) -> brocal(buf, p, s.semilla, luz));
        Pose po = pose(s);
        if (po == null) {
            super.submit(s, pose, colector, camara);
            return;
        }
        int overlay = s.fase == MorenaNereaEntity.BAJA && s.golpeada && s.desde < 5
                ? OverlayTexture.pack(OverlayTexture.u(0.0F), OverlayTexture.v(true)) : OverlayTexture.NO_OVERLAY;
        colector.submitCustomGeometry(pose, MorenaDibujo.PIEL, (p, buf) -> {
            MorenaDibujo.cuerpo(buf, p, po.espina, 1.0F, luz, overlay, 0xFFFFFF);
            Vec3 cuello = po.espina[po.espina.length - 1];
            MorenaDibujo.cabeza(buf, p, cuello, po.frente, ARRIBA, po.boca, po.faringe, 1.0F, luz, overlay, 0xFFFFFF);
        });
        super.submit(s, pose, colector, camara);
    }

    /** La postura de este instante: la espina, hacia donde mira la cabeza y la boca. */
    private record Pose(Vec3[] espina, Vec3 frente, float boca, float faringe) {
    }

    private static Pose pose(Estado s) {
        float e = s.edad + s.semilla * 10;
        float d = s.desde;
        double alto;
        double inclina = 0;     // < 0 se echa atras, > 0 se lanza
        float boca;
        float faringe = 0;
        double giro = 0;        // se enrosca al meterse tras un golpe
        double meneo = 1.0;
        switch (s.fase) {
            case MorenaNereaEntity.SUBE -> {
                if (d < 2) {
                    return null;
                }
                double k = Mth.clamp((d - 2) / (MorenaNereaEntity.T_SUBE - 2), 0, 1);
                alto = ALTO * salto(k);
                boca = 0.7F - 0.4F * (float) k;
                meneo = 0.4;
            }
            case MorenaNereaEntity.FUERA -> {
                alto = ALTO + 0.06 * Math.sin(e * 0.3);
                float quedan = s.dura - d;
                if (quedan <= MorenaNereaEntity.T_AVISO) {
                    double a = Mth.clamp(1.0 - quedan / MorenaNereaEntity.T_AVISO, 0, 1);
                    double suave = a * a * (3 - 2 * a);
                    inclina = -0.75 * suave;
                    alto += 0.2 * suave;
                    boca = 0.35F + 0.65F * (float) suave;
                    faringe = 0.2F * (float) suave;
                    meneo = 1.0 - suave;
                } else {
                    boca = 0.12F + 0.22F * Math.max(0.0F, Mth.sin(e * 0.42F));
                    inclina = 0.12 * Math.sin(e * 0.17);
                }
            }
            case MorenaNereaEntity.BAJA -> {
                if (s.golpeada) {
                    // Respingo y adentro, enroscandose.
                    double k = Mth.clamp((d - 2) / (MorenaNereaEntity.T_BAJA - 2), 0, 1);
                    inclina = d < 3 ? -0.9 * Math.sin(d / 3.0 * Math.PI / 2) : -0.9 * (1 - k);
                    alto = ALTO * (1 - k * k) - 0.8 * k;
                    boca = d < 3 ? 0.8F : 0.4F * (float) (1 - k);
                    giro = k * 2.6;
                    meneo = 0.3;
                } else {
                    // El mordisco: se lanza, saca la segunda mandibula, cierra de golpe y se mete.
                    if (d < 3) {
                        double k = d / 3.0;
                        inclina = Math.sin(k * Math.PI / 2);
                        alto = ALTO + 0.1;
                        boca = k < 0.5 ? 1.0F : 1.0F - 1.8F * (float) (k - 0.5);
                        faringe = (float) Math.sin(k * Math.PI);
                    } else {
                        double k = Mth.clamp((d - 3) / (MorenaNereaEntity.T_BAJA - 3), 0, 1);
                        inclina = 1.0 - k;
                        alto = (ALTO + 0.1) * (1 - k * k) - 0.8 * k;
                        boca = 0.1F;
                    }
                    meneo = 0.2;
                }
            }
            default -> {
                return null;
            }
        }
        if (alto < -0.4) {
            return null;
        }
        Vec3 l = s.mira.yRot((float) giro);
        Vec3 lado = l.cross(ARRIBA).normalize();
        double ola = 0.18 * meneo * Math.sin(e * 0.33);
        double adelante = Math.max(inclina, 0);
        double atras = Math.max(-inclina, 0);
        // La cabeza: un poco por delante del agujero; al lanzarse, lejos y hacia abajo; al echarse atras, arriba.
        Vec3 cabeza = new Vec3(0, alto - 0.75 * adelante + 0.15 * atras, 0)
                .add(l.scale(0.35 + 1.35 * adelante - 0.55 * atras))
                .add(lado.scale(ola));
        double cabeceo = 0.25 - 0.75 * adelante + 0.5 * atras + 0.08 * Math.sin(e * 0.21);
        Vec3 frente = l.scale(Math.cos(cabeceo)).add(ARRIBA.scale(Math.sin(cabeceo))).add(lado.scale(ola * 0.6)).normalize();
        // La espina, de la cola (bajo tierra) al cuello: sube recta por el agujero y se dobla hacia delante.
        Vec3 cuello = cabeza.subtract(frente.scale(0.3));
        Vec3[] control = {
                new Vec3(0, -2.8, 0).add(lado.scale(0.25)),
                new Vec3(0, -1.4, 0).add(lado.scale(-0.1)),
                new Vec3(0, Math.max(-0.6, alto * 0.3), 0).add(lado.scale(ola * 0.6)).subtract(l.scale(0.15 * atras)),
                cuello.subtract(frente.scale(0.75)).add(lado.scale(-ola * 0.4)),
                cuello
        };
        return new Pose(MorenaDibujo.repartir(control, 13), frente, boca, faringe);
    }

    /** Sale de golpe y se pasa un poco (como un muelle). */
    private static double salto(double k) {
        double c1 = 1.9;
        double c3 = c1 + 1;
        double x = k - 1;
        return 1 + c3 * x * x * x + c1 * x * x;
    }

    /** El brocal del agujero: rocas de tamano y giro distintos, medio enterradas. */
    private static void brocal(com.mojang.blaze3d.vertex.VertexConsumer buf, PoseStack.Pose p, float semilla, int luz) {
        java.util.Random r = new java.util.Random((long) (semilla * 1000));
        int n = 9;
        for (int i = 0; i < n; i++) {
            double a = (i + r.nextDouble() * 0.4) / n * Math.PI * 2;
            double radio = 0.95 + r.nextDouble() * 0.15;
            double tam = 0.13 + r.nextDouble() * 0.09;
            Vec3 c = new Vec3(Math.cos(a) * radio, tam * 0.45, Math.sin(a) * radio);
            Vec3 f = new Vec3(-Math.sin(a), 0, Math.cos(a));
            Vec3 s = new Vec3(Math.cos(a), 0, Math.sin(a));
            MorenaDibujo.caja(buf, p, c, f.scale(tam * (1.1 + r.nextDouble() * 0.5)), s.scale(tam), ARRIBA.scale(tam * 0.8),
                    MorenaDibujo.ROCA, MorenaDibujo.ROCA, MorenaDibujo.ROCA, MorenaDibujo.ROCA, MorenaDibujo.ROCA, 0xFFFFFF, luz,
                    OverlayTexture.NO_OVERLAY);
        }
    }
}
