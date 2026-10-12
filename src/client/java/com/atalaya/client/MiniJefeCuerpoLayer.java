package com.atalaya.client;

import com.atalaya.Atalaya;
import com.mojang.blaze3d.vertex.PoseStack;
import net.minecraft.client.renderer.SubmitNodeCollector;
import net.minecraft.client.renderer.entity.LivingEntityRenderer;
import net.minecraft.client.renderer.entity.RenderLayerParent;
import net.minecraft.client.renderer.entity.layers.RenderLayer;
import net.minecraft.client.renderer.rendertype.RenderType;
import net.minecraft.client.renderer.rendertype.RenderTypes;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.resources.Identifier;
import net.minecraft.util.ARGB;

/**
 * Pinta el cuerpo de un mini jefe: su {@link MiniJefeMalla} con las matrices de
 * las piezas en la pose de este fotograma. La piel con su atlas (a la luz del
 * sitio, o a plena luz el fenix) y encima lo que brilla, que no se apaga de
 * noche. Al morir, la piel se deshace con la mascara de disolverse
 * (minijefes_extras.py: se va de arriba abajo, o de las puntas al pecho en el
 * fenix) y la luz se apaga con ella.
 *
 * Deja las matrices en el estado (huesos) para los efectos que salen de una
 * pieza: el orbe del baston, la hoja del macuahuitl, las puntas del tridente...
 *
 * Segun lo grande que se vea en la pantalla pinta un nivel de detalle de la
 * malla u otro (MiniJefeMalla): a ese tamano la diferencia no se ve.
 */
public class MiniJefeCuerpoLayer extends RenderLayer<MiniJefeRenderState, MiniJefeModel> {

    private final RenderType piel;
    private final RenderType brillo;
    private final RenderType disolver;
    private final boolean plenaLuz;

    /**
     * Los pixeles de la pantalla que ocupa un bloque de la malla (2 pixeles del
     * boceto) por debajo de los cuales se pinta el nivel de lejos (bloques de 4):
     * entonces ya no se distinguen. Con el catalejo o en una pantalla mas alta se
     * ve el de cerca hasta mas lejos.
     */
    private static final float LEJOS = 2.0F;

    public MiniJefeCuerpoLayer(RenderLayerParent<MiniJefeRenderState, MiniJefeModel> padre, String nombre, boolean plenaLuz) {
        super(padre);
        Identifier atlas = tex(nombre);
        this.piel = RenderTypes.entityCutout(atlas);
        this.brillo = RenderTypes.entityTranslucentEmissive(tex(nombre + "_brillo"));
        this.disolver = RenderTypes.entityCutoutDissolve(atlas, tex(nombre + "_disolver"));
        this.plenaLuz = plenaLuz;
    }

    static Identifier tex(String nombre) {
        return Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "textures/entity/minijefes/" + nombre + ".png");
    }

    @Override
    public void submit(PoseStack pose, SubmitNodeCollector colector, int luz, MiniJefeRenderState s, float yRot, float xRot) {
        MiniJefeModel m = getParentModel();
        MiniJefeMalla malla = m.malla;
        float[] huesos = m.matrices();
        s.huesos = huesos;
        float d = s.disolver;
        if (d >= 1.0F) {
            return;
        }
        int overlay = LivingEntityRenderer.getOverlayCoords(s, 0.0F);
        int luzPiel = plenaLuz ? 0xF000F0 : luz;
        int color = d > 0.0F ? ARGB.white(1.0F - d) : -1;
        int nivel = s.pixelesPorBloque * s.escala / 8.0F > LEJOS ? 0 : 1;
        colector.submitCustomGeometry(pose, d > 0.0F ? disolver : piel,
                (p, buf) -> malla.pintar(p, buf, huesos, nivel, false, color, overlay, luzPiel));
        int colorBrillo = ARGB.white((1.0F - d) * (1.0F - d));
        colector.submitCustomGeometry(pose, brillo,
                (p, buf) -> malla.pintar(p, buf, huesos, nivel, true, colorBrillo, OverlayTexture.NO_OVERLAY, 0xF000F0));
    }
}
