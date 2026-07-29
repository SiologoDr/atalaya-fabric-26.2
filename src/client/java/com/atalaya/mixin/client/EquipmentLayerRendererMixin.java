package com.atalaya.mixin.client;

import com.atalaya.Atalaya;
import net.minecraft.client.renderer.entity.layers.EquipmentLayerRenderer;
import net.minecraft.client.renderer.rendertype.RenderType;
import net.minecraft.client.renderer.rendertype.RenderTypes;
import net.minecraft.resources.Identifier;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Redirect;

/**
 * Hace que el traje Hazmat se dibuje con transparencia REAL.
 *
 * Minecraft dibuja todas las armaduras con armorCutoutNoCull: un render de
 * recorte que decide cada pixel por un umbral de alfa. Un pixel a medias no
 * existe: o se descarta o se pinta opaco. Por eso un visor semitransparente
 * salia negro solido.
 *
 * Aqui se sustituye por armorTranslucent, que si mezcla el alfa, y SOLO para
 * las texturas de este mod: el resto de armaduras del juego siguen con el
 * comportamiento de siempre.
 *
 * Esto es exactamente lo que un plugin no podia hacer. No es que fuera
 * incomodo: el renderizado vive en el cliente y no habia forma de tocarlo.
 */
@Mixin(EquipmentLayerRenderer.class)
public class EquipmentLayerRendererMixin {

    /**
     * Hay DOS sobrecargas de renderLayers y la llamada esta solo en la de 11
     * argumentos, asi que hace falta el descriptor completo: con el nombre a
     * secas Mixin no resuelve cual es y no inyecta en ninguna.
     */
    private static final String RENDER_LAYERS =
            "renderLayers(Lnet/minecraft/client/resources/model/EquipmentClientInfo$LayerType;"
                    + "Lnet/minecraft/resources/ResourceKey;"
                    + "Lnet/minecraft/client/model/Model;"
                    + "Ljava/lang/Object;"
                    + "Lnet/minecraft/world/item/ItemStack;"
                    + "Lcom/mojang/blaze3d/vertex/PoseStack;"
                    + "Lnet/minecraft/client/renderer/SubmitNodeCollector;"
                    + "ILnet/minecraft/resources/Identifier;II)V";

    @Redirect(
            method = RENDER_LAYERS,
            at = @At(value = "INVOKE",
                    target = "Lnet/minecraft/client/renderer/rendertype/RenderTypes;armorCutoutNoCull("
                            + "Lnet/minecraft/resources/Identifier;)"
                            + "Lnet/minecraft/client/renderer/rendertype/RenderType;"))
    private RenderType atalaya$translucidoParaNuestrasTexturas(Identifier textura) {
        if (Atalaya.MOD_ID.equals(textura.getNamespace())) {
            return RenderTypes.armorTranslucent(textura);
        }
        return RenderTypes.armorCutoutNoCull(textura);
    }
}
