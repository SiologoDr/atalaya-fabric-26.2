package com.atalaya.client;

import com.atalaya.Atalaya;
import com.atalaya.entity.AeralisEntity;
import com.atalaya.entity.AeralisGeometria;
import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import net.minecraft.client.renderer.SubmitNodeCollector;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.MobRenderer;
import net.minecraft.client.renderer.rendertype.RenderType;
import net.minecraft.client.renderer.rendertype.RenderTypes;
import net.minecraft.client.renderer.state.level.CameraRenderState;
import net.minecraft.resources.Identifier;
import net.minecraft.util.ARGB;
import net.minecraft.util.Mth;
import org.jspecify.annotations.Nullable;

/**
 * Pinta a Aeralis: la malla a tamano real (unos 24 bloques de alto y 38 de punta
 * a punta de ala desde el remake), translucida, con la piel de cada fase y la
 * capa de lo que brilla. Liberada vuelve a la piel blanca del principio y al
 * final se deshace con la mascara de aeralis_extras.py.
 *
 * Con la Furia del Vendaval, el aura de rayos por encima ({@link AeralisFuriaLayer}).
 *
 * Durante el Picado, la linea en el suelo por donde se va a lanzar: galones en
 * el color de la fase que se encienden mientras sube (lo llenado brilla, lo que
 * falta apenas) y el aro de donde se posara al final.
 */
public class AeralisRenderer extends MobRenderer<AeralisEntity, AeralisRenderState, AeralisModel> {

    private static final Identifier[] TEXTURAS = new Identifier[4];
    private static final RenderType[] DISOLVER = new RenderType[4];
    private static final Identifier MASCARA = Identifier.fromNamespaceAndPath(Atalaya.MOD_ID,
            "textures/entity/aeralis/aeralis_disolver.png");

    static {
        for (int i = 0; i < 4; i++) {
            TEXTURAS[i] = Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "textures/entity/aeralis/aeralis_f" + (i + 1) + ".png");
            DISOLVER[i] = RenderTypes.entityCutoutDissolve(TEXTURAS[i], MASCARA);
        }
    }

    /** Desde que tick de la liberacion empieza a deshacerse. */
    private static final float DISOLVER_DESDE = 150.0F;

    /** La linea del Picado: los galones (cada GALON bloques), el aro del final y su medio ancho. */
    private static final RenderType GALONES = RenderTypes.entityTranslucentEmissive(
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "textures/entity/aeralis/picado_galon.png"));
    private static final RenderType PUNTA = RenderTypes.entityTranslucentEmissive(
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "textures/entity/aeralis/picado_punta.png"));
    private static final float GALON = 4.0F;
    private static final float LINEA_ANCHO = 2.4F;

    public AeralisRenderer(EntityRendererProvider.Context contexto) {
        super(contexto, new AeralisModel(contexto.bakeLayer(AeralisModel.CAPA)), 3.2F);
        addLayer(new AeralisBrilloLayer(this));
        addLayer(new AeralisFuriaLayer(this, new AeralisModel(contexto.bakeLayer(AeralisModel.CAPA_AURA))));
        addLayer(new AeralisOcelosLayer(this));
    }

    @Override
    public AeralisRenderState createRenderState() {
        return new AeralisRenderState();
    }

    @Override
    public void extractRenderState(AeralisEntity a, AeralisRenderState s, float parcial) {
        super.extractRenderState(a, s, parcial);
        s.dormida.copyFrom(a.dormida);
        s.despertar.copyFrom(a.despertar);
        s.aleteo.copyFrom(a.aleteo);
        s.tornados.copyFrom(a.tornados);
        s.marca.copyFrom(a.marca);
        s.rafaga.copyFrom(a.rafaga);
        s.dobleRafaga.copyFrom(a.dobleRafaga);
        s.juicioSube.copyFrom(a.juicioSube);
        s.juicioSostiene.copyFrom(a.juicioSostiene);
        s.juicioGolpe.copyFrom(a.juicioGolpe);
        s.aturdida.copyFrom(a.aturdida);
        s.agotada.copyFrom(a.agotada);
        s.tambaleo.copyFrom(a.tambaleo);
        s.liberacion.copyFrom(a.liberacion);
        s.picadoAviso.copyFrom(a.picadoAviso);
        s.picado.copyFrom(a.picado);
        s.posada.copyFrom(a.posada);
        s.escamas.copyFrom(a.escamas);
        s.furia = a.tieneFuria();
        int e = a.getEstado();
        s.picadoLargo = (e == AeralisEntity.PICADO_AVISO || e == AeralisEntity.PICADO) && a.deathTime <= 0 ? a.getPicado() : 0.0F;
        s.picadoLleno = e == AeralisEntity.PICADO_AVISO
                ? Mth.clamp((a.tickCount - a.inicioEstado + parcial) * a.ritmoCliente / AeralisGeometria.DURACION_PICADO_AVISO, 0.0F, 1.0F)
                : 1.0F;
        if (s.picadoLargo > 0.0F) {
            double x = Mth.lerp(parcial, a.xo, a.getX());
            double y = Mth.lerp(parcial, a.yo, a.getY());
            double z = Mth.lerp(parcial, a.zo, a.getZ());
            s.picadoSuelo = (float) (AeralisEntity.sueloBajo(a.level(), x, y, z) - y);
        }
        s.estado = a.getEstado();
        s.pesoLibre = Mth.lerp(parcial, a.pesoLibreAnt, a.pesoLibre);
        s.fase = a.fase();
        s.ritmo = a.ritmoCliente;
        s.duracionAturdida = a.getDuracionAturdida();
        s.libre = a.deathTime >= AeralisGeometria.LIBERACION_OJOS_ORO;
        s.disolver = a.deathTime > DISOLVER_DESDE
                ? Mth.clamp((a.deathTime + parcial - DISOLVER_DESDE) / (AeralisGeometria.DURACION_LIBERACION - DISOLVER_DESDE), 0.0F, 1.0F)
                : 0.0F;
        s.hasRedOverlay = a.hurtTime > 0 && a.deathTime < 4;
        s.cabeceo = Mth.lerp(parcial, a.cabeceoAnt, a.cabeceo);
        s.alabeo = Mth.lerp(parcial, a.alabeoAnt, a.alabeo);
        s.avance = Mth.lerp(parcial, a.avanceAnt, a.avance);
        s.relojVuelo = Mth.lerp(parcial, a.relojVueloAnt, a.relojVuelo);
        s.ocelos = Mth.lerp(parcial, a.ocelosAnt, a.ocelos);
        s.ocelosAviso = a.getEstado() == AeralisEntity.OCELOS
                && com.atalaya.entity.MinijuegosAeralis.ojosOcelos(a.getMiniInfo()) == com.atalaya.entity.MinijuegosAeralis.OJOS_AVISO;
        s.ocelosReloj = a.tickCount + parcial;
    }

    @Override
    public void submit(AeralisRenderState s, PoseStack pose, SubmitNodeCollector colector, CameraRenderState camara) {
        super.submit(s, pose, colector, camara);
        if (s.picadoLargo > 0.5F) {
            linea(s, pose, colector);
        }
    }

    /** La linea del Picado, tumbada en el suelo delante de ella (sigue su rumbo mientras se gira). */
    private static void linea(AeralisRenderState s, PoseStack pose, SubmitNodeCollector colector) {
        float b = s.bodyRot * Mth.DEG_TO_RAD;
        float fx = -Mth.sin(b);
        float fz = Mth.cos(b);
        float ix = fz;
        float iz = -fx;
        float y = s.picadoSuelo + 0.08F;
        float largo = s.picadoLargo;
        float lleno = largo * s.picadoLleno;
        int color = AeralisDibujo.claro(AeralisDibujo.fase(s.fase), 0.2F);
        int brilla = (int) (130 + 125 * s.picadoLleno);
        colector.submitCustomGeometry(pose, GALONES, (p, buf) -> {
            tira(buf, p, fx, fz, ix, iz, 0.0F, lleno, y, color, brilla);
            tira(buf, p, fx, fz, ix, iz, lleno, largo, y, color, 60);
        });
        colector.submitCustomGeometry(pose, PUNTA, (p, buf) ->
                AeralisDibujo.suelo(buf, p, fx * largo, y + 0.01F, fz * largo, 3.2F, s.ageInTicks * 0.05F, color,
                        s.picadoLleno >= 1.0F ? 250 : 120));
    }

    /** Una tira tumbada de d0 a d1 por delante de ella, por las dos caras. */
    private static void tira(VertexConsumer buf, PoseStack.Pose p, float fx, float fz, float ix, float iz, float d0, float d1,
                             float y, int c, int alfa) {
        if (d1 - d0 < 0.05F) {
            return;
        }
        float v0 = d0 / GALON;
        float v1 = d1 / GALON;
        int rr = AeralisDibujo.r(c);
        int gg = AeralisDibujo.g(c);
        int bb = AeralisDibujo.b(c);
        for (int cara = 0; cara < 2; cara++) {
            float k = cara == 0 ? 1.0F : -1.0F;
            float u0 = cara == 0 ? 0.0F : 1.0F;
            AeralisDibujo.vertice(buf, p, fx * d0 - ix * LINEA_ANCHO * k, y, fz * d0 - iz * LINEA_ANCHO * k, u0, v0, rr, gg, bb, alfa,
                    AeralisDibujo.A_PLENA_LUZ, 0, 1, 0);
            AeralisDibujo.vertice(buf, p, fx * d0 + ix * LINEA_ANCHO * k, y, fz * d0 + iz * LINEA_ANCHO * k, 1.0F - u0, v0, rr, gg, bb,
                    alfa, AeralisDibujo.A_PLENA_LUZ, 0, 1, 0);
            AeralisDibujo.vertice(buf, p, fx * d1 + ix * LINEA_ANCHO * k, y, fz * d1 + iz * LINEA_ANCHO * k, 1.0F - u0, v1, rr, gg, bb,
                    alfa, AeralisDibujo.A_PLENA_LUZ, 0, 1, 0);
            AeralisDibujo.vertice(buf, p, fx * d1 - ix * LINEA_ANCHO * k, y, fz * d1 - iz * LINEA_ANCHO * k, u0, v1, rr, gg, bb, alfa,
                    AeralisDibujo.A_PLENA_LUZ, 0, 1, 0);
        }
    }

    /** Sin el tumbado de lado al morir: la liberacion es posandose. */
    @Override
    protected float getFlipDegrees() {
        return 0.0F;
    }

    @Override
    protected @Nullable RenderType getRenderType(AeralisRenderState s, boolean visible, boolean transparente, boolean brilla) {
        if (s.disolver > 0.0F && visible) {
            return DISOLVER[0];
        }
        return super.getRenderType(s, visible, transparente, brilla);
    }

    @Override
    protected int getModelTint(AeralisRenderState s) {
        return s.disolver > 0.0F ? ARGB.white(1.0F - s.disolver) : -1;
    }

    /** Treinta y ocho bloques de alas: que no desaparezca al girar la camara. */
    @Override
    protected boolean affectedByCulling(AeralisEntity a) {
        return false;
    }

    @Override
    protected void scale(AeralisRenderState s, PoseStack pose) {
    }

    @Override
    public Identifier getTextureLocation(AeralisRenderState s) {
        return s.libre ? TEXTURAS[0] : TEXTURAS[Math.clamp(s.fase, 1, 4) - 1];
    }
}
