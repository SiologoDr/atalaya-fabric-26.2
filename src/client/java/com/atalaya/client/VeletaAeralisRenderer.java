package com.atalaya.client;

import com.atalaya.Atalaya;
import com.atalaya.entity.VeletaAeralisEntity;
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
 * Una veleta del Vendaval (aeralis_minijuegos.py, veleta.png): el poste de la
 * piedra de la cima con la espiral del viento tallada, la tapa, el cristal de
 * tormenta, el eje, la cruz de bronce con las letras de los vientos (N, E, S,
 * O) y, arriba, la flecha de bronce (asta, punta en escalones y la cola de
 * polilla), que gira con suavidad al rumbo que tenga. A sus pies, la rosa de los
 * vientos (rosa_vientos.png) y, delante, la cuna de luz que marca hacia donde
 * apunta (veleta_cuna.png).
 *
 * Encendida (apunta a Aeralis), la flecha, la cola, el cristal y la espiral son
 * de luz cian y brillan sin luz; enganchada (ella se acaba de salir de su
 * rumbo), parpadean. Sale del suelo y se hunde al acabar.
 */
public class VeletaAeralisRenderer extends EntityRenderer<VeletaAeralisEntity, VeletaAeralisRenderer.Estado> {

    private static final Identifier TEXTURA = Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "textures/entity/aeralis/veleta.png");
    private static final RenderType PIEZAS = RenderTypes.entityCutout(TEXTURA);
    private static final RenderType ROSA = RenderTypes.entityTranslucent(
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "textures/entity/aeralis/rosa_vientos.png"));
    private static final RenderType CUNA = RenderTypes.entityTranslucentEmissive(
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "textures/entity/aeralis/veleta_cuna.png"));
    private static final List<RajangDibujo.Cara> POSTE = new ArrayList<>();
    private static final List<RajangDibujo.Cara> ESPIRAL_LUZ = new ArrayList<>();
    private static final List<RajangDibujo.Cara> CRISTAL = new ArrayList<>();
    private static final List<RajangDibujo.Cara> CRISTAL_LUZ = new ArrayList<>();
    private static final List<RajangDibujo.Cara> FLECHA = new ArrayList<>();
    private static final List<RajangDibujo.Cara> FLECHA_LUZ = new ArrayList<>();
    private static final double Y_CRUZ = 4.05;
    private static final double Y_FLECHA = 4.45;
    private static final float ROSA_RADIO = 1.9F;

    static {
        float[] piedra = uv(0, 0, 16, 48);
        float[] espiral = uv(16, 0, 32, 48);
        float[] tapa = uv(32, 0, 48, 16);
        float[] nada = uv(96, 0, 112, 16);
        float[] bronce = uv(48, 0, 64, 8);
        float[] oscuro = uv(48, 8, 64, 16);
        RajangDibujo.caja(POSTE, -0.55, 0.0, -0.55, 0.55, 0.3, 0.55, tapa, tapa);
        RajangDibujo.caja(POSTE, -0.35, 0.3, -0.35, 0.35, 3.4, 0.35, piedra, tapa);
        RajangDibujo.caja(ESPIRAL_LUZ, -0.356, 0.3, -0.356, 0.356, 3.4, 0.356, espiral, nada);
        RajangDibujo.caja(POSTE, -0.45, 3.4, -0.45, 0.45, 3.6, 0.45, tapa, tapa);
        // El cristal de tormenta, sobre la tapa, y el eje que sale de el.
        RajangDibujo.caja(CRISTAL, -0.17, 3.6, -0.17, 0.17, 3.94, 0.17, uv(32, 16, 48, 32), uv(32, 16, 48, 32));
        RajangDibujo.caja(CRISTAL_LUZ, -0.17, 3.6, -0.17, 0.17, 3.94, 0.17, uv(48, 16, 64, 32), uv(48, 16, 64, 32));
        RajangDibujo.caja(POSTE, -0.05, 3.94, -0.05, 0.05, 4.6, 0.05, oscuro, oscuro);
        // La cruz de los vientos, con su letra en cada punta (N al norte, -Z; E, +X; S, +Z; O, -X).
        RajangDibujo.caja(POSTE, -1.05, Y_CRUZ - 0.05, -0.05, 1.05, Y_CRUZ + 0.05, 0.05, bronce, bronce);
        RajangDibujo.caja(POSTE, -0.05, Y_CRUZ - 0.05, -1.05, 0.05, Y_CRUZ + 0.05, 1.05, bronce, bronce);
        Vec3 arriba = new Vec3(0, 0.16, 0);
        letra(0, new Vec3(0, Y_CRUZ, -1.12), new Vec3(-0.16, 0, 0), arriba);
        letra(1, new Vec3(1.12, Y_CRUZ, 0), new Vec3(0, 0, -0.16), arriba);
        letra(2, new Vec3(0, Y_CRUZ, 1.12), new Vec3(0.16, 0, 0), arriba);
        letra(3, new Vec3(-1.12, Y_CRUZ, 0), new Vec3(0, 0, 0.16), arriba);
        flecha(FLECHA, uv(0, 48, 64, 56), 64);
        flecha(FLECHA_LUZ, uv(0, 56, 64, 64), 96);
    }

    /** Una letra de los vientos en su placa, por las dos caras. */
    private static void letra(int k, Vec3 c, Vec3 derecha, Vec3 arriba) {
        float u0 = (64 + (k % 2) * 8) / 128.0F;
        float v0 = ((k / 2) * 8) / 64.0F;
        List<RajangDibujo.Cara> placa = new ArrayList<>();
        RajangDibujo.panel(placa, c, derecha, arriba, u0, v0, u0 + 8 / 128.0F, v0 + 8 / 64.0F);
        POSTE.addAll(RajangDibujo.dosCaras(placa));
    }

    /**
     * La flecha, apuntando a +Z: asta, punta en escalones y la cola de polilla (dos
     * laminas de bronce recortadas, juntas, que se ven por las dos caras).
     */
    private static void flecha(List<RajangDibujo.Cara> out, float[] uv, int colaU) {
        RajangDibujo.caja(out, -0.05, Y_FLECHA - 0.05, -0.75, 0.05, Y_FLECHA + 0.05, 1.05, uv, uv);
        for (int k = 0; k < 4; k++) {
            double h = 0.3 - 0.07 * k;
            double z0 = 1.05 + 0.1 * k;
            RajangDibujo.caja(out, -0.05, Y_FLECHA - h, z0, 0.05, Y_FLECHA + h, z0 + 0.1, uv, uv);
        }
        // La cola: la raiz (u = 0) en el asta, las alas hacia atras.
        List<RajangDibujo.Cara> cola = new ArrayList<>();
        for (double x : new double[]{-0.03, 0.03}) {
            RajangDibujo.panel(cola, new Vec3(x, Y_FLECHA, -1.18), new Vec3(0, 0, -0.45), new Vec3(0, 0.45, 0),
                    colaU / 128.0F, 16 / 64.0F, (colaU + 32) / 128.0F, 48 / 64.0F);
        }
        out.addAll(RajangDibujo.dosCaras(cola));
    }

    private static float[] uv(int u0, int v0, int u1, int v1) {
        return RajangDibujo.uv(u0 / 128.0F, v0 / 64.0F, u1 / 128.0F, v1 / 64.0F);
    }

    public static class Estado extends EntityRenderState {
        public float salida;
        public float angulo;
        public int luz;
        public float tiempo;
    }

    public VeletaAeralisRenderer(EntityRendererProvider.Context contexto) {
        super(contexto);
    }

    @Override
    public Estado createRenderState() {
        return new Estado();
    }

    @Override
    public void extractRenderState(VeletaAeralisEntity v, Estado s, float parcial) {
        super.extractRenderState(v, s, parcial);
        s.salida = v.salida(parcial);
        float a = Float.isNaN(v.anguloVisto) ? VeletaAeralisEntity.grados(v.getRumbo()) : v.anguloVisto;
        float ant = Float.isNaN(v.anguloVisto) ? a : v.anguloVistoAnt;
        s.angulo = ant + Mth.wrapDegrees(a - ant) * parcial;
        s.luz = v.getLuz();
        s.tiempo = v.tickCount + parcial;
    }

    @Override
    protected boolean affectedByCulling(VeletaAeralisEntity v) {
        return false;
    }

    @Override
    public void submit(Estado s, PoseStack pose, SubmitNodeCollector colector, CameraRenderState camara) {
        if (s.salida <= 0.01F) {
            return;
        }
        int luz = s.lightCoords;
        // Encendida, fija; enganchada, parpadea.
        boolean apunta = s.luz == VeletaAeralisEntity.APUNTA;
        boolean enciende = apunta || (s.luz == VeletaAeralisEntity.ENGANCHADA && ((int) (s.tiempo / 3)) % 2 == 0);
        int late = apunta ? (int) (215 + 40 * Mth.sin(s.tiempo * 0.3F)) : 200;

        // La rosa de los vientos y la cuna, en el suelo (salen con ella).
        int alfaRosa = (int) (235 * s.salida);
        colector.submitCustomGeometry(pose, ROSA, (p, buf) -> NereaDibujo.suelo(buf, p, 0.0, 0.03, 0.0, ROSA_RADIO, 0.0F, 0xFFFFFF, alfaRosa));
        pose.pushPose();
        pose.mulPose(Axis.YP.rotationDegrees(-s.angulo));
        int alfaCuna = (int) ((enciende ? 235 : 90) * s.salida);
        int colorCuna = enciende ? 0xFFFFFF : 0x9AB8D8;
        colector.submitCustomGeometry(pose, CUNA, (p, buf) -> NereaDibujo.suelo(buf, p, 0.0, 0.05, ROSA_RADIO + 0.45, 0.42F,
                Mth.PI, colorCuna, alfaCuna));
        pose.popPose();

        pose.pushPose();
        pose.translate(0.0, -VeletaAeralisEntity.ALTO * (1.0F - s.salida), 0.0);
        colector.submitCustomGeometry(pose, PIEZAS, (p, buf) -> RajangDibujo.emitir(buf, p, POSTE, 255, 255, 255, 255, luz));
        if (enciende) {
            colector.submitCustomGeometry(pose, PIEZAS, (p, buf) -> {
                RajangDibujo.emitir(buf, p, ESPIRAL_LUZ, late, late, late, 255, AeralisDibujo.A_PLENA_LUZ);
                RajangDibujo.emitir(buf, p, CRISTAL_LUZ, late, late, late, 255, AeralisDibujo.A_PLENA_LUZ);
            });
        } else {
            colector.submitCustomGeometry(pose, PIEZAS, (p, buf) -> RajangDibujo.emitir(buf, p, CRISTAL, 255, 255, 255, 255, luz));
        }
        pose.mulPose(Axis.YP.rotationDegrees(-s.angulo));
        if (enciende) {
            colector.submitCustomGeometry(pose, PIEZAS, (p, buf) ->
                    RajangDibujo.emitir(buf, p, FLECHA_LUZ, late, late, late, 255, AeralisDibujo.A_PLENA_LUZ));
        } else {
            colector.submitCustomGeometry(pose, PIEZAS, (p, buf) -> RajangDibujo.emitir(buf, p, FLECHA, 255, 255, 255, 255, luz));
        }
        pose.popPose();
        super.submit(s, pose, colector, camara);
    }
}
