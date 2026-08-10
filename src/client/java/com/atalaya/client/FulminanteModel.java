package com.atalaya.client;

import com.atalaya.Atalaya;
import net.minecraft.client.model.geom.ModelLayerLocation;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.model.geom.PartPose;
import net.minecraft.client.model.geom.builders.CubeDeformation;
import net.minecraft.client.model.geom.builders.CubeListBuilder;
import net.minecraft.client.model.geom.builders.LayerDefinition;
import net.minecraft.client.model.geom.builders.MeshDefinition;
import net.minecraft.client.model.geom.builders.PartDefinition;
import net.minecraft.client.model.monster.creeper.CreeperModel;
import net.minecraft.resources.Identifier;

/**
 * El creeper de vanilla con un matojo seco encima de la cabeza.
 *
 * Hereda de {@link CreeperModel}, asi que las animaciones —el balanceo de las
 * patas, el girar de la cabeza, el hincharse antes de reventar— son las mismas
 * y no hay una linea escrita para eso.
 *
 * La malla si se escribe entera, con las medidas de vanilla copiadas tal cual.
 * No es por gusto: {@code createBodyLayer} devuelve una capa ya cerrada y no da
 * acceso a la malla, asi que no hay donde colgarle una pieza mas.
 *
 * El matojo cuelga de la CABEZA, no de la raiz. Asi gira con ella sin escribir
 * nada: en estos modelos las piezas hijas heredan la rotacion de su padre.
 */
public class FulminanteModel extends CreeperModel {

    public static final ModelLayerLocation CAPA = new ModelLayerLocation(
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "fulminante"), "main");

    public FulminanteModel(ModelPart raiz) {
        super(raiz);
    }

    public static LayerDefinition crear() {
        MeshDefinition malla = new MeshDefinition();
        PartDefinition raiz = malla.getRoot();

        PartDefinition cabeza = raiz.addOrReplaceChild("head",
                CubeListBuilder.create().texOffs(0, 0)
                        .addBox(-4.0F, -8.0F, -4.0F, 8.0F, 8.0F, 8.0F, CubeDeformation.NONE),
                PartPose.offset(0.0F, 6.0F, 0.0F));

        raiz.addOrReplaceChild("body",
                CubeListBuilder.create().texOffs(16, 16)
                        .addBox(-4.0F, 0.0F, -2.0F, 8.0F, 12.0F, 4.0F, CubeDeformation.NONE),
                PartPose.offset(0.0F, 6.0F, 0.0F));

        CubeListBuilder pata = CubeListBuilder.create().texOffs(0, 16)
                .addBox(-2.0F, 0.0F, -2.0F, 4.0F, 6.0F, 4.0F, CubeDeformation.NONE);
        raiz.addOrReplaceChild("right_hind_leg", pata, PartPose.offset(-2.0F, 18.0F, 4.0F));
        raiz.addOrReplaceChild("left_hind_leg", pata, PartPose.offset(2.0F, 18.0F, 4.0F));
        raiz.addOrReplaceChild("right_front_leg", pata, PartPose.offset(-2.0F, 18.0F, -4.0F));
        raiz.addOrReplaceChild("left_front_leg", pata, PartPose.offset(2.0F, 18.0F, -4.0F));

        // La hierba seca: dos planos cruzados, como cualquier planta del juego.
        //
        // Son cajas de grosor CERO, que es lo que vanilla usa para las alas de
        // la abeja. Una caja sin grosor se despliega en dos caras pegadas —la de
        // delante y la de atras— y por eso el dibujo va dos veces en la hoja,
        // en (40,0) y en (52,0), el segundo reflejado. Con 12 de ancho eso gasta
        // de x=40 a x=63, o sea justo lo que queda libre.
        //
        // La cabeza acaba en y = -8, asi que la mata arranca justo ahi.
        // Siete de alto, no doce: a doce se veia como un arbolito saliendole de
        // la cabeza. Una mata corta se lee como parte del suelo, que es de lo
        // que se trata.
        CubeListBuilder hoja = CubeListBuilder.create().texOffs(40, 0)
                .addBox(-6.0F, -7.0F, 0.0F, 12.0F, 7.0F, 0.0F, CubeDeformation.NONE);
        cabeza.addOrReplaceChild("hierba_frente", hoja,
                PartPose.offset(0.0F, -8.0F, 0.0F));
        cabeza.addOrReplaceChild("hierba_lado", hoja,
                PartPose.offsetAndRotation(0.0F, -8.0F, 0.0F,
                        0.0F, (float) (Math.PI / 2.0), 0.0F));

        return LayerDefinition.create(malla, 64, 32);
    }
}
