package com.atalaya.client;

import com.atalaya.Atalaya;
import com.atalaya.entity.AeralisEntity;
import com.atalaya.entity.AeralisGeometria;
import com.mojang.blaze3d.vertex.PoseStack;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.MobRenderer;
import net.minecraft.client.renderer.rendertype.RenderType;
import net.minecraft.client.renderer.rendertype.RenderTypes;
import net.minecraft.resources.Identifier;
import net.minecraft.util.ARGB;
import net.minecraft.util.Mth;
import org.jspecify.annotations.Nullable;

/**
 * Pinta a Aeralis: la malla a tamano real (17 bloques de alto, 22 de punta a
 * punta de ala), translucida, con la piel de cada fase y la capa de lo que
 * brilla. Liberada vuelve a la piel blanca del principio y al final se deshace
 * con la mascara de aeralis_extras.py.
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

    public AeralisRenderer(EntityRendererProvider.Context contexto) {
        super(contexto, new AeralisModel(contexto.bakeLayer(AeralisModel.CAPA)), 3.2F);
        addLayer(new AeralisBrilloLayer(this));
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
        s.estado = a.getEstado();
        s.pesoLibre = Mth.lerp(parcial, a.pesoLibreAnt, a.pesoLibre);
        s.fase = a.fase();
        s.ritmo = a.ritmoCliente;
        s.libre = a.deathTime >= AeralisGeometria.LIBERACION_OJOS_ORO;
        s.disolver = a.deathTime > DISOLVER_DESDE
                ? Mth.clamp((a.deathTime + parcial - DISOLVER_DESDE) / (AeralisGeometria.DURACION_LIBERACION - DISOLVER_DESDE), 0.0F, 1.0F)
                : 0.0F;
        s.hasRedOverlay = a.hurtTime > 0 && a.deathTime < 4;
        s.cabeceo = Mth.lerp(parcial, a.cabeceoAnt, a.cabeceo);
        s.alabeo = Mth.lerp(parcial, a.alabeoAnt, a.alabeo);
        s.avance = Mth.lerp(parcial, a.avanceAnt, a.avance);
        s.relojVuelo = Mth.lerp(parcial, a.relojVueloAnt, a.relojVuelo);
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

    /** Veintidos bloques de alas: que no desaparezca al girar la camara. */
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
