package com.atalaya.client;

import com.atalaya.Atalaya;
import net.minecraft.client.renderer.entity.CreeperRenderer;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.state.CreeperRenderState;
import net.minecraft.resources.Identifier;

/**
 * Pinta el fulminante.
 *
 * Hereda del renderer del creeper y solo le cambia dos cosas: el modelo y la
 * textura. Todo lo demas viene puesto y no se toca:
 *
 *   - el estiron y el destello blanco de cuando se hincha
 *   - la capa azul del creeper cargado por un rayo
 *   - la sombra, el nombre flotante, el fuego, todo lo de MobRenderer
 *
 * El campo del modelo no es final en LivingEntityRenderer, asi que basta con
 * reemplazarlo despues de llamar al padre. Es la via corta y ademas la que
 * sigue funcionando si Mojang mete algo nuevo en el renderer del creeper.
 */
public class FulminanteRenderer extends CreeperRenderer {

    private static final Identifier TEXTURA =
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "textures/entity/fulminante/fulminante.png");

    public FulminanteRenderer(EntityRendererProvider.Context contexto) {
        super(contexto);
        this.model = new FulminanteModel(contexto.bakeLayer(FulminanteModel.CAPA));
    }

    @Override
    public Identifier getTextureLocation(CreeperRenderState estado) {
        return TEXTURA;
    }
}
