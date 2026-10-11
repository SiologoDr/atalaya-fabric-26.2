package com.atalaya.client;

import com.atalaya.Atalaya;
import com.atalaya.habilidad.HabilidadEstado;
import com.atalaya.habilidad.Habilidades;
import com.atalaya.item.ArmadurasJefes;
import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.math.Axis;
import net.minecraft.client.Minecraft;
import net.minecraft.client.model.player.PlayerModel;
import net.minecraft.client.renderer.SubmitNodeCollector;
import net.minecraft.client.renderer.entity.RenderLayerParent;
import net.minecraft.client.renderer.entity.layers.RenderLayer;
import net.minecraft.client.renderer.entity.state.AvatarRenderState;
import net.minecraft.client.renderer.rendertype.RenderType;
import net.minecraft.client.renderer.rendertype.RenderTypes;
import net.minecraft.resources.Identifier;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.phys.Vec3;

/**
 * El aura de la habilidad de la armadura mientras esta activa (10-10-2026, Juan:
 * "debe de senalarte cuando la habilidad esta activa, en cada armadura;
 * actualmente sale solo un efecto de que lo activaste pero no sale si lo tienes
 * ahorita"). La ven todos alrededor de quien la tiene (el estado le llega a cada
 * cliente: Habilidades.ESTADO), los 30 s que dura, y se enciende y se apaga
 * suave. Las texturas, de auras_habilidad.py.
 *
 * <pre>
 *   Muralla de Jade      el hexagono de jade a los pies, otro grande y tenue
 *                        hasta donde protege (8 bloques) y cinco cristales que
 *                        le giran alrededor.
 *   Manantial            ondas de agua que salen de el hasta 8 bloques (una
 *                        cada 3 s, con cada cura) y un aro de agua en la cintura.
 *   Corriente Ascendente tres cintas de viento que le suben en espiral y el
 *                        remolino del suelo.
 *   Furia Solar          el sol que le arde detras de la cabeza y llamas a los
 *                        pies.
 * </pre>
 *
 * Quien la lleva, en primera persona, la ve en el marco de la pantalla y en
 * lo que le sale a los pies (HabilidadHud, HabilidadCliente).
 */
public class HabilidadAuraLayer extends RenderLayer<AvatarRenderState, PlayerModel> {

    private static final RenderType JADE_ANILLO = tipo("jade_anillo");
    private static final RenderType JADE_CRISTAL = tipo("jade_cristal");
    private static final RenderType MAREAS_ONDA = tipo("mareas_onda");
    private static final RenderType VENDAVAL_CINTA = tipo("vendaval_cinta");
    private static final RenderType VENDAVAL_REMOLINO = tipo("vendaval_remolino");
    private static final RenderType SOLAR_HALO = tipo("solar_halo");

    /** Hasta donde llegan la Muralla y el Manantial (Habilidades: MURALLA_RADIO, MANANTIAL_RADIO). */
    private static final float ZONA = 8.0F;
    /** Lo que tarda en encenderse y en apagarse (ticks). */
    private static final float ENCIENDE = 10.0F;
    private static final float APAGA = 20.0F;

    private static RenderType tipo(String nombre) {
        return RenderTypes.entityTranslucent(Identifier.fromNamespaceAndPath(Atalaya.MOD_ID,
                "textures/entity/habilidad/" + nombre + ".png"));
    }

    public HabilidadAuraLayer(RenderLayerParent<AvatarRenderState, PlayerModel> padre) {
        super(padre);
    }

    @Override
    public void submit(PoseStack pose, SubmitNodeCollector colector, int luz, AvatarRenderState s, float rumbo, float cabeceo) {
        if (s.isInvisible || s.isSpectator) {
            return;
        }
        Minecraft mc = Minecraft.getInstance();
        if (mc.level == null || !(mc.level.getEntity(s.id) instanceof Player p)) {
            return;
        }
        ArmadurasJefes.Tema tema = Habilidades.conjunto(p);
        if (tema == null) {
            return;
        }
        HabilidadEstado e = p.getAttachedOrElse(Habilidades.ESTADO, HabilidadEstado.NADA);
        float ahora = mc.level.getGameTime() + mc.getDeltaTracker().getGameTimeDeltaPartialTick(false);
        if (e.tema() != tema.ordinal() || ahora >= e.hasta()) {
            return;
        }
        float desde = e.hasta() - Habilidades.DURACION;
        float k = Mth.clamp(Math.min((ahora - desde) / ENCIENDE, (e.hasta() - ahora) / APAGA), 0.0F, 1.0F);
        float t = s.ageInTicks;
        pose.pushPose();
        // Del espacio del modelo (volteado, subido y girado con el cuerpo) a sus pies, con los ejes del mundo.
        pose.translate(0.0F, 1.501F, 0.0F);
        pose.scale(-1.0F, -1.0F, 1.0F);
        pose.mulPose(Axis.YP.rotationDegrees(s.bodyRot - 180.0F));
        Vec3 ojo = mc.gameRenderer.mainCamera().position().subtract(s.x, s.y, s.z);
        switch (tema) {
            case JADE -> jade(colector, pose, ojo, t, k);
            case MAREAS -> mareas(colector, pose, ojo, t, k);
            case VENDAVAL -> vendaval(colector, pose, ojo, t, k);
            case SOLAR -> solar(colector, pose, ojo, t, k, s.bodyRot * Mth.DEG_TO_RAD, s.isCrouching);
        }
        pose.popPose();
    }

    private static void jade(SubmitNodeCollector colector, PoseStack pose, Vec3 ojo, float t, float k) {
        colector.submitCustomGeometry(pose, JADE_ANILLO, (p, buf) -> {
            NereaDibujo.suelo(buf, p, 0.0, 0.03, 0.0, 1.15F, t * 0.01F, 0xFFFFFF, (int) (220 * k));
            NereaDibujo.suelo(buf, p, 0.0, 0.025, 0.0, ZONA, -t * 0.004F, 0xFFFFFF, (int) (60 * k));
        });
        colector.submitCustomGeometry(pose, JADE_CRISTAL, (p, buf) -> {
            for (int i = 0; i < 5; i++) {
                double a = t * 0.05 + i * Math.PI * 2 / 5;
                double y = 0.45 + 0.35 * Math.sin(t * 0.08 + i * 1.7);
                Vec3 base = new Vec3(Math.cos(a) * 0.95, y, Math.sin(a) * 0.95);
                NereaDibujo.cinta(buf, p, base, base.add(0, 0.42, 0), ojo, 0.11F, 1.0F, 0.0F, 0xFFFFFF, (int) (235 * k));
            }
        });
    }

    private static void mareas(SubmitNodeCollector colector, PoseStack pose, Vec3 ojo, float t, float k) {
        colector.submitCustomGeometry(pose, MAREAS_ONDA, (p, buf) -> {
            // Una onda cada 3 s, como las curas del Manantial, que se abre hasta donde llega.
            for (int i = 0; i < 2; i++) {
                float f = ((t + i * 30.0F) % 60.0F) / 60.0F;
                NereaDibujo.suelo(buf, p, 0.0, 0.03 + i * 0.004, 0.0, 0.6F + f * ZONA, 0.0F, 0xFFFFFF, (int) (210 * (1.0F - f) * k));
            }
            NereaDibujo.suelo(buf, p, 0.0, 0.035, 0.0, 0.9F, t * 0.02F, 0xFFFFFF, (int) (200 * k));
            // El aro de agua en la cintura, que sube y baja despacio.
            NereaDibujo.suelo(buf, p, 0.0, 0.95 + 0.08 * Math.sin(t * 0.1), 0.0, 0.85F, -t * 0.04F, 0xFFFFFF, (int) (190 * k));
        });
    }

    private static void vendaval(SubmitNodeCollector colector, PoseStack pose, Vec3 ojo, float t, float k) {
        colector.submitCustomGeometry(pose, VENDAVAL_REMOLINO, (p, buf) ->
                NereaDibujo.suelo(buf, p, 0.0, 0.03, 0.0, 1.5F, t * 0.15F, 0xFFFFFF, (int) (190 * k)));
        colector.submitCustomGeometry(pose, VENDAVAL_CINTA, (p, buf) -> {
            int tramos = 10;
            for (int i = 0; i < 3; i++) {
                Vec3 antes = null;
                for (int j = 0; j <= tramos; j++) {
                    double y = 2.2 * j / tramos;
                    double a = t * 0.14 + i * Math.PI * 2 / 3 + y * 2.4;
                    double r = 0.62 + 0.12 * Math.sin(t * 0.1 + j + i);
                    Vec3 q = new Vec3(Math.cos(a) * r, y, Math.sin(a) * r);
                    if (antes != null) {
                        // Se aclara arriba y abajo; la veta corre hacia arriba.
                        float borde = (float) Math.sin(Math.PI * (j - 0.5) / tramos);
                        float v0 = (j - 1) / (float) tramos - t * 0.04F;
                        NereaDibujo.cinta(buf, p, antes, q, ojo, 0.16F, v0, v0 + 1.0F / tramos, 0xFFFFFF, (int) (250 * k * borde));
                    }
                    antes = q;
                }
            }
        });
    }

    private static void solar(SubmitNodeCollector colector, PoseStack pose, Vec3 ojo, float t, float k, float rumbo,
                              boolean agachado) {
        // El sol detras de la cabeza: de pie, de cara hacia donde mira, girando despacio.
        Vec3 delante = new Vec3(-Mth.sin(rumbo), 0.0, Mth.cos(rumbo));
        Vec3 derecha = new Vec3(Mth.cos(rumbo), 0.0, Mth.sin(rumbo));
        Vec3 c = new Vec3(0.0, agachado ? 1.35 : 1.65, 0.0).subtract(delante.scale(0.32));
        float m = 0.72F * (0.96F + 0.04F * Mth.sin(t * 0.25F));
        double g = t * 0.03;
        Vec3 ua = derecha.scale(Math.cos(g) * m).add(0, Math.sin(g) * m, 0);
        Vec3 ub = derecha.scale(-Math.sin(g) * m).add(0, Math.cos(g) * m, 0);
        colector.submitCustomGeometry(pose, SOLAR_HALO, (p, buf) ->
                NovilisDibujo.cara(buf, p, ojo, c.subtract(ua).subtract(ub), c.add(ua).subtract(ub), c.add(ua).add(ub),
                        c.subtract(ua).add(ub), 0, 1, 1, 0, 0xFFFFFF, (int) (230 * k), (int) (230 * k)));
        // Llamas a los pies.
        colector.submitCustomGeometry(pose, NovilisDibujo.llamas(1), (p, buf) ->
                NovilisDibujo.anillo(buf, p, ojo, 0.0, 0.02, 0.0, 0.55F, 0.5F + 0.1F * Mth.sin(t * 0.3F), 12, 3.0F, t * 0.05F,
                        0xFFFFFF, (int) (200 * k)));
    }
}
