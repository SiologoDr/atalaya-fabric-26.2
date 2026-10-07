package com.atalaya.client;

import com.atalaya.Atalaya;
import com.atalaya.entity.FlechaVendavalEntity;
import net.minecraft.client.renderer.entity.ArrowRenderer;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.state.ArrowRenderState;
import net.minecraft.resources.Identifier;

/** Las flechas del Arco del Vendaval: el modelo de flecha con su textura de viento. */
public class FlechaVendavalRenderer extends ArrowRenderer<FlechaVendavalEntity, ArrowRenderState> {

    private static final Identifier TEXTURA = Identifier.fromNamespaceAndPath(Atalaya.MOD_ID,
            "textures/entity/projectiles/vendaval_arrow.png");

    public FlechaVendavalRenderer(EntityRendererProvider.Context contexto) {
        super(contexto);
    }

    @Override
    public ArrowRenderState createRenderState() {
        return new ArrowRenderState();
    }

    @Override
    protected Identifier getTextureLocation(ArrowRenderState s) {
        return TEXTURA;
    }
}
