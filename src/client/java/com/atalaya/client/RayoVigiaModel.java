package com.atalaya.client;

import com.atalaya.Atalaya;
import net.minecraft.client.model.Model;
import net.minecraft.client.model.geom.ModelLayerLocation;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.model.geom.PartPose;
import net.minecraft.client.model.geom.builders.CubeListBuilder;
import net.minecraft.client.model.geom.builders.LayerDefinition;
import net.minecraft.client.model.geom.builders.MeshDefinition;
import net.minecraft.client.model.geom.builders.PartDefinition;
import net.minecraft.client.renderer.rendertype.RenderTypes;
import net.minecraft.resources.Identifier;
import net.minecraft.util.Mth;

/**
 * La malla del rayo: geometria, no particulas. Un nucleo fino e incandescente,
 * dos halos rojos cruzados a 45 grados alrededor, una punta ambar delante y
 * una cola que se desvanece detras: un solo trazo de luz.
 *
 * Todo a lo largo del eje Z, que el renderer apunta hacia donde vuela. La
 * punta queda en el origen —donde esta la entidad— y el resto se estira hacia
 * atras: lo que se ve es la cabeza del disparo y la cola que deja.
 *
 * Gira sobre su eje y el halo late: un cilindro quieto se lee como un palo
 * brillante; girando y latiendo se lee como energia.
 */
public class RayoVigiaModel extends Model<RayoVigiaRenderState> {

    public static final ModelLayerLocation CAPA = new ModelLayerLocation(
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "rayo_vigia"), "main");

    private final ModelPart giro;
    private final ModelPart halo;
    private final ModelPart halo45;

    public RayoVigiaModel(ModelPart raiz) {
        super(raiz, RenderTypes::entityTranslucentEmissive);
        this.giro = raiz.getChild("giro");
        this.halo = giro.getChild("halo");
        this.halo45 = giro.getChild("halo45");
    }

    public static LayerDefinition crear() {
        MeshDefinition malla = new MeshDefinition();
        PartDefinition giro = malla.getRoot().addOrReplaceChild("giro", CubeListBuilder.create(), PartPose.ZERO);
        giro.addOrReplaceChild("nucleo",
                CubeListBuilder.create().texOffs(0, 0).addBox(-1.0F, -1.0F, -24.0F, 2.0F, 2.0F, 28.0F),
                PartPose.ZERO);
        CubeListBuilder halo = CubeListBuilder.create().texOffs(0, 30)
                .addBox(-2.5F, -2.5F, -20.0F, 5.0F, 5.0F, 22.0F);
        giro.addOrReplaceChild("halo", halo, PartPose.ZERO);
        giro.addOrReplaceChild("halo45", halo,
                PartPose.rotation(0.0F, 0.0F, (float) (Math.PI / 4.0)));
        giro.addOrReplaceChild("punta",
                CubeListBuilder.create().texOffs(64, 0).addBox(-2.0F, -2.0F, 0.0F, 4.0F, 4.0F, 4.0F),
                PartPose.ZERO);
        // La estela, pegada detras del halo. Su textura se va a transparente.
        giro.addOrReplaceChild("cola",
                CubeListBuilder.create().texOffs(60, 30).addBox(-1.5F, -1.5F, -48.0F, 3.0F, 3.0F, 30.0F),
                PartPose.ZERO);
        return LayerDefinition.create(malla, 128, 64);
    }

    @Override
    public void setupAnim(RayoVigiaRenderState estado) {
        super.setupAnim(estado);
        float t = estado.ageInTicks;
        giro.zRot = t * 0.6F;
        // Los dos halos laten a destiempo: el borde del rayo nunca esta quieto.
        float a = 1.0F + 0.18F * Mth.sin(t * 1.7F);
        float b = 1.0F + 0.18F * Mth.sin(t * 1.7F + Mth.PI);
        halo.xScale = a;
        halo.yScale = a;
        halo45.xScale = b;
        halo45.yScale = b;
    }
}
