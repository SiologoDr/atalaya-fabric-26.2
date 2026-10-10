package com.atalaya.client;

import com.atalaya.Atalaya;
import com.atalaya.entity.YunqueForjaEntity;
import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.math.Axis;
import java.util.ArrayList;
import java.util.List;
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
 * Un yunque de la Forja del Juramento (novilis_minijuegos.py, yunque.png, 128 x
 * 64): una peana de basalto con el sol en relieve, la cintura con su veta de
 * lava, el cuerpo de sillares con la banda de oro y, encima, la cara de acero
 * con los colores del temple; el cuerno de acero, en tres escalones hasta la
 * punta, y el talon al otro lado. Sobre la cara, la hoja al rojo con su guarda
 * y su empunadura. En los costados, seis tachones que se encienden (un sol) con
 * cada buen golpe. A sus pies, el suelo de la fragua: hollin y brasas que
 * respiran (forja_suelo.png).
 *
 * Sobre la hoja, de cara a quien mira, el aro de luz (aro_forja.png: un sol
 * con doce rayos hacia dentro) que se cierra hasta tocarla, y la mira quieta
 * del tamano de la hoja (aro_hoja.png): cuando coinciden, hay que golpear. Al
 * golpear, el destello (destello.png) del color de como ha ido. Forjada, la
 * hoja es de oro y deja de haber aro.
 */
public class YunqueForjaRenderer extends EntityRenderer<YunqueForjaEntity, YunqueForjaRenderer.Estado> {

    private static final RenderType CUERPO = RenderTypes.entityCutout(tex("yunque"));
    private static final RenderType ARO = RenderTypes.entityTranslucent(tex("aro_forja"));
    private static final RenderType MIRA = RenderTypes.entityTranslucent(tex("aro_hoja"));
    private static final RenderType DESTELLO = RenderTypes.entityTranslucent(tex("destello"));
    private static final RenderType SUELO = RenderTypes.entityTranslucent(tex("forja_suelo"));
    private static final List<RajangDibujo.Cara> YUNQUE = new ArrayList<>();
    private static final List<RajangDibujo.Cara> HOJA_ROJA = new ArrayList<>();
    private static final List<RajangDibujo.Cara> HOJA_ORO = new ArrayList<>();
    private static final List<RajangDibujo.Cara> MANGO = new ArrayList<>();
    @SuppressWarnings("unchecked")
    private static final List<RajangDibujo.Cara>[] TACHONES = new List[YunqueForjaEntity.GOLPES];
    @SuppressWarnings("unchecked")
    private static final List<RajangDibujo.Cara>[] TACHONES_ENCENDIDOS = new List[YunqueForjaEntity.GOLPES];
    private static final double HOJA_Y = 1.5;
    /** Lo alto del yunque (la caja de la entidad es mas alta, para apuntar a la hoja). */
    private static final float ALTO_DIBUJO = 1.7F;
    /** El radio del suelo de la fragua y lo que ocupa el aro dentro de su textura (el canto en 30 de 32). */
    private static final float SUELO_RADIO = 2.6F;
    private static final float ARO_EN_TEXTURA = 0.94F;
    private static final float MIRA_EN_TEXTURA = 0.9F;

    static {
        float[] lado = uv(0, 0, 48, 16);
        float[] cara = uv(48, 0, 96, 16);
        float[] cintura = uv(96, 0, 112, 16);
        float[] peanaLado = uv(0, 16, 48, 28);
        float[] peanaTapa = uv(48, 16, 96, 28);
        float[] cuerno = uv(96, 16, 128, 24);
        RajangDibujo.caja(YUNQUE, -1.25, 0.0, -0.8, 1.25, 0.3, 0.8, peanaLado, peanaTapa);
        RajangDibujo.caja(YUNQUE, -0.6, 0.3, -0.45, 0.6, 0.85, 0.45, cintura, cintura);
        RajangDibujo.caja(YUNQUE, -1.45, 0.85, -0.7, 1.45, HOJA_Y, 0.7, lado, cara);
        // El cuerno, en tres escalones hasta la punta, y el talon al otro lado.
        RajangDibujo.caja(YUNQUE, 1.45, 1.08, -0.34, 1.85, 1.46, 0.34, cuerno, cuerno);
        RajangDibujo.caja(YUNQUE, 1.85, 1.18, -0.22, 2.15, 1.42, 0.22, cuerno, cuerno);
        RajangDibujo.caja(YUNQUE, 2.15, 1.26, -0.1, 2.35, 1.38, 0.1, cuerno, cuerno);
        RajangDibujo.caja(YUNQUE, -1.72, 1.1, -0.45, -1.45, 1.46, 0.45, cuerno, cuerno);
        float[] roja = uv(0, 32, 64, 40);
        float[] oro = uv(0, 40, 64, 48);
        float[] empunadura = uv(64, 32, 80, 40);
        float[] guarda = uv(80, 32, 96, 40);
        RajangDibujo.caja(HOJA_ROJA, -1.15, HOJA_Y, -0.2, 1.15, HOJA_Y + 0.12, 0.2, roja, roja);
        RajangDibujo.caja(HOJA_ORO, -1.15, HOJA_Y, -0.2, 1.15, HOJA_Y + 0.12, 0.2, oro, oro);
        RajangDibujo.caja(HOJA_ROJA, 1.15, HOJA_Y, -0.12, 1.4, HOJA_Y + 0.12, 0.12, roja, roja);
        RajangDibujo.caja(HOJA_ORO, 1.15, HOJA_Y, -0.12, 1.4, HOJA_Y + 0.12, 0.12, oro, oro);
        RajangDibujo.caja(MANGO, -1.3, HOJA_Y, -0.45, -1.15, HOJA_Y + 0.2, 0.45, guarda, guarda);
        RajangDibujo.caja(MANGO, -1.85, HOJA_Y + 0.03, -0.07, -1.3, HOJA_Y + 0.13, 0.07, empunadura, empunadura);
        RajangDibujo.caja(MANGO, -1.97, HOJA_Y, -0.1, -1.85, HOJA_Y + 0.16, 0.1, guarda, guarda);
        // Los tachones: seis a lo largo del costado (por delante y por detras).
        float[] apagado = uv(96, 32, 104, 40);
        float[] encendido = uv(104, 32, 112, 40);
        for (int i = 0; i < YunqueForjaEntity.GOLPES; i++) {
            TACHONES[i] = new ArrayList<>();
            TACHONES_ENCENDIDOS[i] = new ArrayList<>();
            double x = -1.1 + i * 0.44;
            RajangDibujo.caja(TACHONES[i], x - 0.1, 1.04, -0.73, x + 0.1, 1.24, 0.73, apagado, apagado);
            RajangDibujo.caja(TACHONES_ENCENDIDOS[i], x - 0.1, 1.04, -0.73, x + 0.1, 1.24, 0.73, encendido, encendido);
        }
    }

    private static Identifier tex(String nombre) {
        return Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "textures/entity/novilis/" + nombre + ".png");
    }

    private static float[] uv(int u0, int v0, int u1, int v1) {
        return RajangDibujo.uv(u0 / 128.0F, v0 / 64.0F, u1 / 128.0F, v1 / 64.0F);
    }

    public static class Estado extends EntityRenderState {
        public float salida;
        public float rumbo;
        public int golpes;
        public boolean forjada;
        public boolean vuela;
        /** El radio del aro ahora (-1: no hay). */
        public float aro = -1.0F;
        /** Lo que hace del ultimo golpe (ticks) y como fue. */
        public float desdeGolpe = 100.0F;
        public int calidad;
        public float tiempo;
    }

    public YunqueForjaRenderer(EntityRendererProvider.Context contexto) {
        super(contexto);
    }

    @Override
    public Estado createRenderState() {
        return new Estado();
    }

    @Override
    public void extractRenderState(YunqueForjaEntity y, Estado s, float parcial) {
        super.extractRenderState(y, s, parcial);
        s.salida = y.salida(parcial);
        s.rumbo = y.getYRot();
        s.golpes = y.getGolpes();
        s.forjada = y.forjada();
        s.vuela = y.vuela();
        long ahora = y.level().getGameTime();
        s.aro = s.salida >= 0.99F ? y.radioAro(ahora, parcial) : -1.0F;
        s.desdeGolpe = ahora - y.getUltimo() + parcial;
        s.calidad = y.getCalidad();
        s.tiempo = y.tickCount + parcial;
    }

    @Override
    protected boolean affectedByCulling(YunqueForjaEntity y) {
        return false;
    }

    @Override
    public void submit(Estado s, PoseStack pose, SubmitNodeCollector colector, CameraRenderState camara) {
        if (s.salida <= 0.01F) {
            return;
        }
        Vec3 ojo = camara.pos.subtract(s.x, s.y, s.z);
        int luz = s.lightCoords;
        // El suelo de la fragua: hollin y brasas que respiran (mas vivas cuanto mas forjada esta la hoja).
        float respira = 0.75F + 0.25F * Mth.sin(s.tiempo * 0.12F);
        int alfaSuelo = (int) (255 * s.salida * respira);
        float giroSuelo = s.rumbo * Mth.DEG_TO_RAD;
        colector.submitCustomGeometry(pose, SUELO, (p, buf) ->
                NereaDibujo.suelo(buf, p, 0.0, 0.03, 0.0, SUELO_RADIO, giroSuelo, 0xFFFFFF, alfaSuelo));

        pose.pushPose();
        float bajar = ALTO_DIBUJO * (1.0F - s.salida);
        pose.translate(0.0, -bajar, 0.0);
        // Al recibir un golpe, el yunque da un respingo.
        if (s.desdeGolpe < 4.0F) {
            pose.translate(0.0, -0.04 * (1.0F - s.desdeGolpe / 4.0F), 0.0);
        }
        pose.mulPose(Axis.YP.rotationDegrees(180.0F - s.rumbo));
        colector.submitCustomGeometry(pose, CUERPO, (p, buf) -> RajangDibujo.emitir(buf, p, YUNQUE, 255, 255, 255, 255, luz));
        for (int i = 0; i < YunqueForjaEntity.GOLPES; i++) {
            boolean lleno = i < s.golpes;
            List<RajangDibujo.Cara> tachon = lleno ? TACHONES_ENCENDIDOS[i] : TACHONES[i];
            int brilla = lleno ? AeralisDibujo.A_PLENA_LUZ : luz;
            colector.submitCustomGeometry(pose, CUERPO, (p, buf) -> RajangDibujo.emitir(buf, p, tachon, 255, 255, 255, 255, brilla));
        }
        if (!s.vuela) {
            colector.submitCustomGeometry(pose, CUERPO, (p, buf) -> RajangDibujo.emitir(buf, p, MANGO, 255, 255, 255, 255, luz));
            if (s.forjada) {
                int late = (int) (225 + 30 * Mth.sin(s.tiempo * 0.15F));
                colector.submitCustomGeometry(pose, CUERPO, (p, buf) ->
                        RajangDibujo.emitir(buf, p, HOJA_ORO, late, late, late, 255, AeralisDibujo.A_PLENA_LUZ));
            } else {
                // Al rojo: cuantos mas golpes lleva, mas clara.
                int g = 170 + 14 * s.golpes;
                colector.submitCustomGeometry(pose, CUERPO, (p, buf) ->
                        RajangDibujo.emitir(buf, p, HOJA_ROJA, 255, g, g, 255, AeralisDibujo.A_PLENA_LUZ));
            }
        }
        pose.popPose();

        // El aro de sol, de cara a quien mira, sobre la hoja; y la mira quieta del tamano de la hoja.
        Vec3 c = new Vec3(0.0, HOJA_Y + 0.1 - bajar, 0.0);
        if (s.aro > 0.0F) {
            float cerca = 1.0F - Mth.clamp((s.aro - YunqueForjaEntity.ARO_HOJA) / (YunqueForjaEntity.ARO_SALE - YunqueForjaEntity.ARO_HOJA),
                    0.0F, 1.0F);
            int alfa = (int) (130 + 125 * cerca);
            float r = s.aro;
            // La mira se enciende cuando el aro llega: de ambar a casi blanco.
            int colorMira = cerca > 0.9F ? 0xFFF0C0 : 0xFFA040;
            float giro = s.tiempo * 0.05F;
            colector.submitCustomGeometry(pose, MIRA, (p, buf) ->
                    NovilisDibujo.cartel(buf, p, c, ojo, YunqueForjaEntity.ARO_HOJA / MIRA_EN_TEXTURA, giro, colorMira, 160 + (int) (90 * cerca)));
            colector.submitCustomGeometry(pose, ARO, (p, buf) ->
                    NovilisDibujo.cartel(buf, p, c, ojo, r / ARO_EN_TEXTURA, -giro * 0.5F, 0xFFFFFF, alfa));
        }
        if (s.desdeGolpe < 8.0F) {
            // El destello del golpe: blanco y oro si fue perfecto, oro si bien, rojo si a destiempo.
            float k = s.desdeGolpe / 8.0F;
            int color = s.calidad == YunqueForjaEntity.PERFECTO_HECHO ? 0xFFF6D0
                    : s.calidad == YunqueForjaEntity.BIEN_HECHO ? 0xFFC23A : 0xFF3A20;
            float r = (s.calidad == YunqueForjaEntity.PERFECTO_HECHO ? 1.5F : 1.0F) * (0.5F + 0.9F * k);
            int alfa = (int) (250 * (1.0F - k));
            float giro = k * 0.8F;
            colector.submitCustomGeometry(pose, DESTELLO, (p, buf) -> NovilisDibujo.cartel(buf, p, c, ojo, r, giro, color, alfa));
        }
        super.submit(s, pose, colector, camara);
    }
}
