package com.atalaya.client;

import com.atalaya.Atalaya;
import com.atalaya.entity.FogonazoEntity;
import com.mojang.blaze3d.vertex.PoseStack;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.MobRenderer;
import net.minecraft.resources.Identifier;
import net.minecraft.util.Mth;

/**
 * Pinta el Fogonazo: su malla, su piel y encima lo que brilla (FogonazoBrilloLayer). Al cebarse se hincha y parpadea en
 * blanco como un creeper (las mismas cuentas que CreeperRenderer), y el modelo se abre (FogonazoModel).
 */
public class FogonazoRenderer extends MobRenderer<FogonazoEntity, FogonazoRenderState, FogonazoModel> {

    private static final Identifier TEXTURA =
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "textures/entity/fogonazo/fogonazo.png");

    public FogonazoRenderer(EntityRendererProvider.Context contexto) {
        super(contexto, new FogonazoModel(contexto.bakeLayer(FogonazoModel.CAPA)), 0.6F);
        addLayer(new FogonazoBrilloLayer(this));
    }

    @Override
    public FogonazoRenderState createRenderState() {
        return new FogonazoRenderState();
    }

    @Override
    public void extractRenderState(FogonazoEntity fogonazo, FogonazoRenderState estado, float parcial) {
        super.extractRenderState(fogonazo, estado, parcial);
        estado.swelling = fogonazo.getSwelling(parcial);
        estado.isPowered = fogonazo.isPowered();
        estado.fase = (fogonazo.getId() * 0.61803F % 1.0F) * Mth.TWO_PI;
    }

    /** Hincharse, como el creeper: mas ancho que alto y temblando. */
    @Override
    protected void scale(FogonazoRenderState estado, PoseStack pose) {
        float f = estado.swelling;
        float tiembla = 1.0F + Mth.sin(f * 100.0F) * f * 0.01F;
        f = Mth.clamp(f, 0.0F, 1.0F);
        f *= f;
        f *= f;
        float ancho = (1.0F + f * 0.4F) * tiembla;
        float alto = (1.0F + f * 0.1F) / tiembla;
        pose.scale(ancho, alto, ancho);
    }

    /** El parpadeo blanco del creeper que va a estallar. */
    @Override
    protected float getWhiteOverlayProgress(FogonazoRenderState estado) {
        float f = estado.swelling;
        return (int) (f * 10.0F) % 2 == 0 ? 0.0F : Mth.clamp(f, 0.5F, 1.0F);
    }

    @Override
    public Identifier getTextureLocation(FogonazoRenderState estado) {
        return TEXTURA;
    }
}
