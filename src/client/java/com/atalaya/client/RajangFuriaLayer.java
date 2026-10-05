package com.atalaya.client;

import com.atalaya.Atalaya;
import com.mojang.blaze3d.vertex.PoseStack;
import net.minecraft.client.renderer.SubmitNodeCollector;
import net.minecraft.client.renderer.entity.RenderLayerParent;
import net.minecraft.client.renderer.entity.layers.EnergySwirlLayer;
import net.minecraft.client.renderer.rendertype.RenderTypes;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.resources.Identifier;

/**
 * El aura de la Furia de Jade: la misma malla un poco hinchada
 * ({@link RajangMalla#crearAura()}), con bandas verdes que le corren por encima,
 * como la carga del creeper (es la misma capa de vanilla, con la textura de
 * rajang_mejoras_extras.py). Solo mientras tiene la Furia.
 *
 * <p>Las bandas van a un quinto de lo que corren en el creeper (mas deprisa
 * molestaban a la vista): vanilla deja fijo el avance vertical, asi que el
 * dibujo se hace aqui con los dos.
 */
public class RajangFuriaLayer extends EnergySwirlLayer<RajangRenderState, RajangModel> {

    private static final Identifier TEXTURA = Identifier.fromNamespaceAndPath(Atalaya.MOD_ID,
            "textures/entity/rajang/rajang_furia.png");
    /** Lo que se corre la textura por tick, de lado y hacia arriba (en el creeper, 0,01 las dos). */
    private static final float CORRE_X = 0.0024F;
    private static final float CORRE_Y = 0.002F;
    /** El gris de vanilla: las bandas a media luz. */
    private static final int COLOR = 0xFF808080;

    private final RajangModel modelo;

    public RajangFuriaLayer(RenderLayerParent<RajangRenderState, RajangModel> padre, RajangModel modelo) {
        super(padre);
        this.modelo = modelo;
    }

    @Override
    public void submit(PoseStack pose, SubmitNodeCollector colector, int luz, RajangRenderState s, float yRot, float xRot) {
        if (!isPowered(s)) {
            return;
        }
        float edad = s.ageInTicks;
        colector.order(1).submitModel(modelo, s, pose,
                RenderTypes.energySwirl(TEXTURA, xOffset(edad) % 1.0F, edad * CORRE_Y % 1.0F), luz,
                OverlayTexture.NO_OVERLAY, COLOR, null, s.outlineColor, null);
    }

    @Override
    protected boolean isPowered(RajangRenderState s) {
        return s.furia && s.deathTime <= 0;
    }

    @Override
    protected float xOffset(float edad) {
        return edad * CORRE_X;
    }

    @Override
    protected Identifier getTextureLocation() {
        return TEXTURA;
    }

    @Override
    protected RajangModel model() {
        return modelo;
    }
}
