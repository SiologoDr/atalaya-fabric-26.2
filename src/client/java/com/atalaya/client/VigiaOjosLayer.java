package com.atalaya.client;

import com.atalaya.Atalaya;
import com.atalaya.entity.VigiaEntity;
import com.mojang.blaze3d.vertex.PoseStack;
import net.minecraft.client.renderer.SubmitNodeCollector;
import net.minecraft.client.renderer.entity.RenderLayerParent;
import net.minecraft.client.renderer.entity.layers.RenderLayer;
import net.minecraft.client.renderer.rendertype.RenderType;
import net.minecraft.client.renderer.rendertype.RenderTypes;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.resources.Identifier;

/**
 * Lo que brilla del Vigia: el ojo, la luz que se escapa del farol y el
 * rescoldo entre las costillas.
 *
 * Es lo mismo que hace vanilla con los ojos de la arana —el tipo de render
 * "eyes", que ignora la luz del mundo—, pero con DOS texturas: ambar mientras
 * vaga y rojo en cuanto tiene presa. EyesLayer solo admite una, asi que se
 * copia su unica llamada y se elige la textura con el estado.
 *
 * De noche es lo primero que se ve de el, y a proposito: un ojo rojo a lo
 * lejos tiene que leerse como "ya te ha visto" antes de distinguir la forma.
 */
public class VigiaOjosLayer extends RenderLayer<VigiaRenderState, VigiaModel> {

    private static final RenderType CALMA = RenderTypes.eyes(
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "textures/entity/vigia/vigia_ojo.png"));
    private static final RenderType CAZA = RenderTypes.eyes(
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "textures/entity/vigia/vigia_ojo_caza.png"));

    public VigiaOjosLayer(RenderLayerParent<VigiaRenderState, VigiaModel> padre) {
        super(padre);
    }

    @Override
    public void submit(PoseStack pose, SubmitNodeCollector colector, int luz,
                       VigiaRenderState estado, float yRot, float xRot) {
        // Al tambalearse el farol parpadea: se le va la luz por el golpe.
        if (estado.estado == VigiaEntity.TAMBALEO && ((int) estado.ageInTicks & 2) == 0) {
            return;
        }
        // Al morir la luz aguanta la ultima mirada, titila diez ticks y se va
        // en el mismo tick en que suena el apagarse.
        if (estado.deathTime >= VigiaEntity.MUERTE_APAGARSE) {
            return;
        }
        if (estado.deathTime >= VigiaEntity.MUERTE_APAGARSE - 10 && ((int) estado.ageInTicks % 3) == 0) {
            return;
        }
        colector.order(1).submitModel(getParentModel(), estado, pose,
                estado.cazando ? CAZA : CALMA, luz, OverlayTexture.NO_OVERLAY, estado.outlineColor, null);
    }
}
