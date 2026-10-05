package com.atalaya.client;

import com.atalaya.Atalaya;
import com.atalaya.entity.RajangEntity;
import com.atalaya.entity.RajangGeometria;
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
 * Pinta a Rajang: la malla a tamano real (8 bloques a la cruz, 25 de largo con
 * la cola) con la piel pintada de cada fase (rajang_juego.py: el mosaico de
 * jade, las espirales de oro y las grietas que nacen del sol del pecho) y la
 * capa de lo que brilla. Liberado, el jade vuelve al de la fase I con las
 * grietas cerradas en oro, y al final la piedra se deshace a terrones con la
 * mascara de rajang_piezas.py.
 */
public class RajangRenderer extends MobRenderer<RajangEntity, RajangRenderState, RajangModel> {

    private static final Identifier[] TEXTURAS = new Identifier[4];
    private static final Identifier LIBRE = tex("rajang_libre");
    private static final Identifier MASCARA = tex("rajang_disolver");
    private static final RenderType DISOLVER = RenderTypes.entityCutoutDissolve(LIBRE, MASCARA);

    static {
        for (int i = 0; i < 4; i++) {
            TEXTURAS[i] = tex("rajang_f" + (i + 1));
        }
    }

    /** Desde que tick de la liberacion empieza a deshacerse. */
    private static final float DISOLVER_DESDE = 160.0F;

    private static Identifier tex(String nombre) {
        return Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "textures/entity/rajang/" + nombre + ".png");
    }

    public RajangRenderer(EntityRendererProvider.Context contexto) {
        super(contexto, new RajangModel(contexto.bakeLayer(RajangModel.CAPA)), 4.5F);
        addLayer(new RajangBrilloLayer(this));
    }

    @Override
    public RajangRenderState createRenderState() {
        return new RajangRenderState();
    }

    @Override
    public void extractRenderState(RajangEntity r, RajangRenderState s, float parcial) {
        super.extractRenderState(r, s, parcial);
        s.dormido.copyFrom(r.dormido);
        s.despertar.copyFrom(r.despertar);
        s.garra.copyFrom(r.garra);
        s.terremoto.copyFrom(r.terremoto);
        s.rugido.copyFrom(r.rugido);
        s.sello.copyFrom(r.sello);
        s.cataclismo.copyFrom(r.cataclismo);
        s.cataclismoSostiene.copyFrom(r.cataclismoSostiene);
        s.cataclismoBaja.copyFrom(r.cataclismoBaja);
        s.aturdido.copyFrom(r.aturdido);
        s.paralizado.copyFrom(r.paralizado);
        s.salto.copyFrom(r.salto);
        s.tambaleo.copyFrom(r.tambaleo);
        s.liberacion.copyFrom(r.liberacion);
        s.estado = r.getEstado();
        s.pesoLibre = Mth.lerp(parcial, r.pesoLibreAnt, r.pesoLibre);
        s.fase = r.fase();
        s.ritmo = r.ritmoCliente;
        s.velocidad = Mth.lerp(parcial, r.velocidadAnt, r.velocidad);
        s.relojAndar = Mth.lerp(parcial, r.relojAndarAnt, r.relojAndar);
        s.relojCorrer = Mth.lerp(parcial, r.relojCorrerAnt, r.relojCorrer);
        s.libre = r.deathTime >= RajangGeometria.LIBERACION_OJOS_ORO;
        s.disolver = r.deathTime > DISOLVER_DESDE
                ? Mth.clamp((r.deathTime + parcial - DISOLVER_DESDE) / (RajangGeometria.DURACION_LIBERACION - DISOLVER_DESDE), 0.0F, 1.0F)
                : 0.0F;
        s.hasRedOverlay = r.hurtTime > 0 && r.deathTime < 4;
    }

    /** Sin el tumbado de lado al morir: la liberacion es tumbarse como una esfinge. */
    @Override
    protected float getFlipDegrees() {
        return 0.0F;
    }

    @Override
    protected @Nullable RenderType getRenderType(RajangRenderState s, boolean visible, boolean transparente, boolean brilla) {
        if (s.disolver > 0.0F && visible) {
            return DISOLVER;
        }
        return super.getRenderType(s, visible, transparente, brilla);
    }

    @Override
    protected int getModelTint(RajangRenderState s) {
        return s.disolver > 0.0F ? ARGB.white(1.0F - s.disolver) : -1;
    }

    /** Veinticinco bloques de largo: que no desaparezca al girar la camara. */
    @Override
    protected boolean affectedByCulling(RajangEntity r) {
        return false;
    }

    @Override
    protected void scale(RajangRenderState s, PoseStack pose) {
    }

    @Override
    public Identifier getTextureLocation(RajangRenderState s) {
        return s.libre ? LIBRE : TEXTURAS[Math.clamp(s.fase, 1, 4) - 1];
    }
}
