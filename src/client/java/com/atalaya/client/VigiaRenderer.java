package com.atalaya.client;

import com.atalaya.Atalaya;
import com.atalaya.entity.VigiaEntity;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.MobRenderer;
import net.minecraft.resources.Identifier;

/**
 * Pinta el Vigia: su malla, su piel y encima la capa de lo que alumbra.
 */
public class VigiaRenderer extends MobRenderer<VigiaEntity, VigiaRenderState, VigiaModel> {

    private static final Identifier TEXTURA =
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "textures/entity/vigia/vigia.png");

    public VigiaRenderer(EntityRendererProvider.Context contexto) {
        super(contexto, new VigiaModel(contexto.bakeLayer(VigiaModel.CAPA)), 0.7F);
        addLayer(new VigiaOjosLayer(this));
    }

    @Override
    public VigiaRenderState createRenderState() {
        return new VigiaRenderState();
    }

    @Override
    public void extractRenderState(VigiaEntity vigia, VigiaRenderState estado, float parcial) {
        super.extractRenderState(vigia, estado, parcial);
        estado.reposo.copyFrom(vigia.reposo);
        estado.alerta.copyFrom(vigia.alerta);
        estado.cepo.copyFrom(vigia.cepo);
        estado.mirada.copyFrom(vigia.mirada);
        estado.tambaleo.copyFrom(vigia.tambaleo);
        estado.buscar.copyFrom(vigia.buscar);
        estado.muerte.copyFrom(vigia.muerte);
        estado.cazando = vigia.isCazando();
        estado.estado = vigia.getEstado();
        // Vanilla tine de rojo todo el cuerpo mientras muere. Aqui la muerte
        // es una animacion de tres segundos y tenida de rojo no se leeria:
        // solo el destello del golpe que lo mata.
        estado.hasRedOverlay = vigia.hurtTime > 0 && vigia.deathTime < 4;
    }

    /**
     * Cero: sin el tumbado de lado de vanilla al morir. La caida la hace la
     * animacion de muerte, de rodillas y hacia delante.
     */
    @Override
    protected float getFlipDegrees() {
        return 0.0F;
    }

    @Override
    public Identifier getTextureLocation(VigiaRenderState estado) {
        return TEXTURA;
    }
}
