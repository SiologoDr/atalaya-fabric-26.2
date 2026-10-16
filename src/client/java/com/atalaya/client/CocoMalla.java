package com.atalaya.client;

import net.minecraft.client.model.geom.PartPose;
import net.minecraft.client.model.geom.builders.CubeListBuilder;
import net.minecraft.client.model.geom.builders.LayerDefinition;
import net.minecraft.client.model.geom.builders.MeshDefinition;
import net.minecraft.client.model.geom.builders.PartDefinition;

/**
 * La malla del Coco. GENERADO por materiales/generadores/coco_juego.py: no se edita a mano (la textura se pinta
 * con la misma cuadricula). Las partes con nombre son las que mueve CocoModel; cada caja va en su propia pieza
 * ("_c" y un numero) con su giro.
 */
public final class CocoMalla {

    private CocoMalla() {
    }

    public static LayerDefinition crear() {
        MeshDefinition malla = new MeshDefinition();
        PartDefinition raiz = malla.getRoot();
        PartDefinition p_cuerpo = raiz.addOrReplaceChild("cuerpo", CubeListBuilder.create(),
                PartPose.offsetAndRotation(0F, 11F, 7.5F, 0F, 0F, 0F));
        p_cuerpo.addOrReplaceChild("cuerpo_c0", CubeListBuilder.create().texOffs(56, 106).addBox(-10.5F, -20.5F, 3.5F, 21F, 10F, 6F),
                PartPose.offsetAndRotation(0F, 13F, -4F, 0F, 0F, 0F));
        p_cuerpo.addOrReplaceChild("cuerpo_c1", CubeListBuilder.create().texOffs(208, 61).addBox(-8F, -23F, 3.5F, 16F, 15F, 6F),
                PartPose.offsetAndRotation(0F, 13F, -4F, 0F, 0F, 0F));
        p_cuerpo.addOrReplaceChild("cuerpo_c2", CubeListBuilder.create().texOffs(153, 61).addBox(-8F, -20.5F, 1F, 16F, 10F, 11F),
                PartPose.offsetAndRotation(0F, 13F, -4F, 0F, 0F, 0F));
        PartDefinition p_tronco = p_cuerpo.addOrReplaceChild("tronco", CubeListBuilder.create(),
                PartPose.offsetAndRotation(0F, -7F, 2F, 0.38F, 0F, 0F));
        p_tronco.addOrReplaceChild("tronco_c0", CubeListBuilder.create().texOffs(0, 85).addBox(-13F, -33F, -2F, 26F, 10F, 10F),
                PartPose.offsetAndRotation(0F, 20F, -6F, 0F, 0F, 0F));
        p_tronco.addOrReplaceChild("tronco_c1", CubeListBuilder.create().texOffs(73, 34).addBox(-10F, -36F, -2F, 20F, 16F, 10F),
                PartPose.offsetAndRotation(0F, 20F, -6F, 0F, 0F, 0F));
        p_tronco.addOrReplaceChild("tronco_c2", CubeListBuilder.create().texOffs(0, 34).addBox(-10F, -33F, -5F, 20F, 10F, 16F),
                PartPose.offsetAndRotation(0F, 20F, -6F, 0F, 0F, 0F));
        p_tronco.addOrReplaceChild("tronco_c3", CubeListBuilder.create().texOffs(137, 139).addBox(-9.6F, -39.8F, 3.8F, 19.2F, 2.6F, 5.6F),
                PartPose.offsetAndRotation(0F, 20F, -6F, 0F, 0F, 0F));
        p_tronco.addOrReplaceChild("tronco_c4", CubeListBuilder.create().texOffs(134, 124).addBox(-7.4F, -42F, 3.8F, 14.8F, 7F, 5.6F),
                PartPose.offsetAndRotation(0F, 20F, -6F, 0F, 0F, 0F));
        p_tronco.addOrReplaceChild("tronco_c5", CubeListBuilder.create().texOffs(37, 124).addBox(-7.4F, -39.8F, 1.6F, 14.8F, 2.6F, 10F),
                PartPose.offsetAndRotation(0F, 20F, -6F, 0F, 0F, 0F));
        p_tronco.addOrReplaceChild("tronco_c6", CubeListBuilder.create().texOffs(23, 139).addBox(-19.4F, -36.2F, 0.4F, 9.2F, 5.2F, 5.2F),
                PartPose.offsetAndRotation(0F, 20F, -6F, 0F, 0F, 0F));
        p_tronco.addOrReplaceChild("tronco_c7", CubeListBuilder.create().texOffs(174, 106).addBox(-17.4F, -38.2F, 0.4F, 5.2F, 9.2F, 5.2F),
                PartPose.offsetAndRotation(0F, 20F, -6F, 0F, 0F, 0F));
        p_tronco.addOrReplaceChild("tronco_c8", CubeListBuilder.create().texOffs(144, 106).addBox(-17.4F, -36.2F, -1.6F, 5.2F, 5.2F, 9.2F),
                PartPose.offsetAndRotation(0F, 20F, -6F, 0F, 0F, 0F));
        p_tronco.addOrReplaceChild("tronco_c9", CubeListBuilder.create().texOffs(23, 139).addBox(10.2F, -36.2F, 0.4F, 9.2F, 5.2F, 5.2F),
                PartPose.offsetAndRotation(0F, 20F, -6F, 0F, 0F, 0F));
        p_tronco.addOrReplaceChild("tronco_c10", CubeListBuilder.create().texOffs(174, 106).addBox(12.2F, -38.2F, 0.4F, 5.2F, 9.2F, 5.2F),
                PartPose.offsetAndRotation(0F, 20F, -6F, 0F, 0F, 0F));
        p_tronco.addOrReplaceChild("tronco_c11", CubeListBuilder.create().texOffs(144, 106).addBox(12.2F, -36.2F, -1.6F, 5.2F, 5.2F, 9.2F),
                PartPose.offsetAndRotation(0F, 20F, -6F, 0F, 0F, 0F));
        p_tronco.addOrReplaceChild("tronco_c12", CubeListBuilder.create().texOffs(134, 34).addBox(-5F, -4F, -14.7155F, 10F, 8F, 17.7155F),
                PartPose.offsetAndRotation(0F, -14F, -6F, -1.2689F, 0F, 0F));
        p_tronco.addOrReplaceChild("tronco_c13", CubeListBuilder.create().texOffs(131, 161).addBox(-1.3F, -3.85F, 0F, 2.6F, 3.85F, 0F),
                PartPose.offsetAndRotation(0F, -24.8063F, -0.5949F, 2.4669F, 0F, 0F));
        p_tronco.addOrReplaceChild("tronco_c14", CubeListBuilder.create().texOffs(131, 161).addBox(-1.3F, -3.85F, 0F, 2.6F, 3.85F, 0F),
                PartPose.offsetAndRotation(0F, -24.8063F, -0.5949F, 1.5708F, -0.8961F, 1.5708F));
        p_tronco.addOrReplaceChild("tronco_c15", CubeListBuilder.create().texOffs(197, 161).addBox(-0.975F, -3.15F, 0F, 1.95F, 3.15F, 0F),
                PartPose.offsetAndRotation(0F, -26.648F, 1.9606F, 2.1953F, 0F, 0F));
        p_tronco.addOrReplaceChild("tronco_c16", CubeListBuilder.create().texOffs(197, 161).addBox(-0.975F, -3.15F, 0F, 1.95F, 3.15F, 0F),
                PartPose.offsetAndRotation(0F, -26.648F, 1.9606F, 1.5708F, -0.6245F, 1.5708F));
        p_tronco.addOrReplaceChild("tronco_c17", CubeListBuilder.create().texOffs(51, 161).addBox(-1.3F, -4.4F, 0F, 2.6F, 4.4F, 0F),
                PartPose.offsetAndRotation(0F, -25.2358F, 2.7487F, 2.4669F, 0F, 0F));
        p_tronco.addOrReplaceChild("tronco_c18", CubeListBuilder.create().texOffs(51, 161).addBox(-1.3F, -4.4F, 0F, 2.6F, 4.4F, 0F),
                PartPose.offsetAndRotation(0F, -25.2358F, 2.7487F, 1.5708F, -0.8961F, 1.5708F));
        p_tronco.addOrReplaceChild("tronco_c19", CubeListBuilder.create().texOffs(202, 161).addBox(-0.975F, -3.6F, 0F, 1.95F, 3.6F, 0F),
                PartPose.offsetAndRotation(0F, -27.3406F, 5.6693F, 2.1953F, 0F, 0F));
        p_tronco.addOrReplaceChild("tronco_c20", CubeListBuilder.create().texOffs(202, 161).addBox(-0.975F, -3.6F, 0F, 1.95F, 3.6F, 0F),
                PartPose.offsetAndRotation(0F, -27.3406F, 5.6693F, 1.5708F, -0.6245F, 1.5708F));
        p_tronco.addOrReplaceChild("tronco_c21", CubeListBuilder.create().texOffs(138, 161).addBox(-1.3F, -3.575F, 0F, 2.6F, 3.575F, 0F),
                PartPose.offsetAndRotation(0F, -24.5916F, 5.2333F, 2.4669F, 0F, 0F));
        p_tronco.addOrReplaceChild("tronco_c22", CubeListBuilder.create().texOffs(138, 161).addBox(-1.3F, -3.575F, 0F, 2.6F, 3.575F, 0F),
                PartPose.offsetAndRotation(0F, -24.5916F, 5.2333F, 1.5708F, -0.8961F, 1.5708F));
        p_tronco.addOrReplaceChild("tronco_c23", CubeListBuilder.create().texOffs(71, 167).addBox(-0.975F, -2.925F, 0F, 1.95F, 2.925F, 0F),
                PartPose.offsetAndRotation(0F, -26.3017F, 7.6063F, 2.1953F, 0F, 0F));
        p_tronco.addOrReplaceChild("tronco_c24", CubeListBuilder.create().texOffs(71, 167).addBox(-0.975F, -2.925F, 0F, 1.95F, 2.925F, 0F),
                PartPose.offsetAndRotation(0F, -26.3017F, 7.6063F, 1.5708F, -0.6245F, 1.5708F));
        PartDefinition p_barriga = p_cuerpo.addOrReplaceChild("barriga", CubeListBuilder.create(),
                PartPose.offsetAndRotation(0F, -1.6F, -5F, 0F, 0F, 0F));
        p_barriga.addOrReplaceChild("barriga_c0", CubeListBuilder.create().texOffs(128, 0).addBox(-11.5F, -23F, -10.4F, 23F, 16.8F, 10.8F),
                PartPose.offsetAndRotation(0F, 14.6F, 1F, 0F, 0F, 0F));
        p_barriga.addOrReplaceChild("barriga_c1", CubeListBuilder.create().texOffs(69, 0).addBox(-8.9F, -25.6F, -10.4F, 17.8F, 22F, 10.8F),
                PartPose.offsetAndRotation(0F, 14.6F, 1F, 0F, 0F, 0F));
        p_barriga.addOrReplaceChild("barriga_c2", CubeListBuilder.create().texOffs(0, 0).addBox(-8.9F, -23F, -13F, 17.8F, 16.8F, 16F),
                PartPose.offsetAndRotation(0F, 14.6F, 1F, 0F, 0F, 0F));
        p_barriga.addOrReplaceChild("barriga_c3", CubeListBuilder.create().texOffs(0, 124).addBox(-8.5F, -21F, -14.6F, 17F, 12.8F, 1F),
                PartPose.offsetAndRotation(0F, 14.6F, 1F, 0F, 0F, 0F));
        p_barriga.addOrReplaceChild("barriga_c4", CubeListBuilder.create().texOffs(0, 106).addBox(-6.9F, -22.6F, -14.6F, 13.8F, 16F, 1F),
                PartPose.offsetAndRotation(0F, 14.6F, 1F, 0F, 0F, 0F));
        p_barriga.addOrReplaceChild("barriga_c5", CubeListBuilder.create().texOffs(192, 85).addBox(-6.9F, -21F, -16.2F, 13.8F, 12.8F, 4.2F),
                PartPose.offsetAndRotation(0F, 14.6F, 1F, 0F, 0F, 0F));
        PartDefinition p_pierna_d = p_cuerpo.addOrReplaceChild("pierna_d", CubeListBuilder.create(),
                PartPose.offsetAndRotation(-8.6F, 0F, 3F, 0F, 0F, 0F));
        p_pierna_d.addOrReplaceChild("pierna_d_c0", CubeListBuilder.create().texOffs(109, 61).addBox(-4F, -4F, -11.0441F, 8F, 8F, 13.4441F),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0.534F, 0.938F, 0F));
        PartDefinition p_canilla_d = p_pierna_d.addOrReplaceChild("canilla_d", CubeListBuilder.create(),
                PartPose.offsetAndRotation(-6F, 4.4F, -4.4F, 0F, 0F, 0F));
        p_canilla_d.addOrReplaceChild("canilla_d_c0", CubeListBuilder.create().texOffs(111, 106).addBox(-3.1F, -3.1F, -7.5801F, 6.2F, 6.2F, 9.4401F),
                PartPose.offsetAndRotation(0F, 0F, 0F, 1.2347F, -1.0122F, 0F));
        PartDefinition p_pie_d = p_canilla_d.addOrReplaceChild("pie_d", CubeListBuilder.create(),
                PartPose.offsetAndRotation(1.6F, 5.4F, -1F, 0F, 0F, 0F));
        p_pie_d.addOrReplaceChild("pie_d_c0", CubeListBuilder.create().texOffs(53, 139).addBox(-3.4F, -0.2F, -4F, 6.8F, 3.4F, 7.6F),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0.3F, 0F));
        p_pie_d.addOrReplaceChild("pie_d_c1", CubeListBuilder.create().texOffs(112, 161).addBox(-3.2F, 1.4F, -6F, 2F, 1.8F, 2.2F),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0.3F, 0F));
        p_pie_d.addOrReplaceChild("pie_d_c2", CubeListBuilder.create().texOffs(35, 167).addBox(-0.65F, -0.65F, -1.0167F, 1.3F, 1.3F, 1.1667F),
                PartPose.offsetAndRotation(-3.8158F, 2.2F, -4.8908F, 0.25F, 0.3F, 0F));
        p_pie_d.addOrReplaceChild("pie_d_c3", CubeListBuilder.create().texOffs(41, 167).addBox(-0.455F, -0.455F, -1.0167F, 0.91F, 0.91F, 1.1667F),
                PartPose.offsetAndRotation(-4.0639F, 2.4144F, -5.693F, 0.65F, 0.3F, 0F));
        p_pie_d.addOrReplaceChild("pie_d_c4", CubeListBuilder.create().texOffs(91, 167).addBox(-0.26F, -0.26F, -1.0167F, 0.52F, 0.52F, 1.1667F),
                PartPose.offsetAndRotation(-4.2678F, 2.9389F, -6.3522F, 1.05F, 0.3F, 0F));
        p_pie_d.addOrReplaceChild("pie_d_c5", CubeListBuilder.create().texOffs(112, 161).addBox(-1F, 1.4F, -6F, 2F, 1.8F, 2.2F),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0.3F, 0F));
        p_pie_d.addOrReplaceChild("pie_d_c6", CubeListBuilder.create().texOffs(35, 167).addBox(-0.65F, -0.65F, -1.0167F, 1.3F, 1.3F, 1.1667F),
                PartPose.offsetAndRotation(-1.714F, 2.2F, -5.541F, 0.25F, 0.3F, 0F));
        p_pie_d.addOrReplaceChild("pie_d_c7", CubeListBuilder.create().texOffs(41, 167).addBox(-0.455F, -0.455F, -1.0167F, 0.91F, 0.91F, 1.1667F),
                PartPose.offsetAndRotation(-1.9622F, 2.4144F, -6.3432F, 0.65F, 0.3F, 0F));
        p_pie_d.addOrReplaceChild("pie_d_c8", CubeListBuilder.create().texOffs(91, 167).addBox(-0.26F, -0.26F, -1.0167F, 0.52F, 0.52F, 1.1667F),
                PartPose.offsetAndRotation(-2.1661F, 2.9389F, -7.0023F, 1.05F, 0.3F, 0F));
        p_pie_d.addOrReplaceChild("pie_d_c9", CubeListBuilder.create().texOffs(112, 161).addBox(1.2F, 1.4F, -6F, 2F, 1.8F, 2.2F),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0.3F, 0F));
        p_pie_d.addOrReplaceChild("pie_d_c10", CubeListBuilder.create().texOffs(35, 167).addBox(-0.65F, -0.65F, -1.0167F, 1.3F, 1.3F, 1.1667F),
                PartPose.offsetAndRotation(0.3877F, 2.2F, -6.1911F, 0.25F, 0.3F, 0F));
        p_pie_d.addOrReplaceChild("pie_d_c11", CubeListBuilder.create().texOffs(41, 167).addBox(-0.455F, -0.455F, -1.0167F, 0.91F, 0.91F, 1.1667F),
                PartPose.offsetAndRotation(0.1396F, 2.4144F, -6.9933F, 0.65F, 0.3F, 0F));
        p_pie_d.addOrReplaceChild("pie_d_c12", CubeListBuilder.create().texOffs(91, 167).addBox(-0.26F, -0.26F, -1.0167F, 0.52F, 0.52F, 1.1667F),
                PartPose.offsetAndRotation(-0.0643F, 2.9389F, -7.6524F, 1.05F, 0.3F, 0F));
        PartDefinition p_pierna_i = p_cuerpo.addOrReplaceChild("pierna_i", CubeListBuilder.create(),
                PartPose.offsetAndRotation(8.6F, 0F, 3F, 0F, 0F, 0F));
        p_pierna_i.addOrReplaceChild("pierna_i_c0", CubeListBuilder.create().texOffs(109, 61).addBox(-4F, -4F, -11.0441F, 8F, 8F, 13.4441F),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0.534F, -0.938F, 0F));
        PartDefinition p_canilla_i = p_pierna_i.addOrReplaceChild("canilla_i", CubeListBuilder.create(),
                PartPose.offsetAndRotation(6F, 4.4F, -4.4F, 0F, 0F, 0F));
        p_canilla_i.addOrReplaceChild("canilla_i_c0", CubeListBuilder.create().texOffs(111, 106).addBox(-3.1F, -3.1F, -7.5801F, 6.2F, 6.2F, 9.4401F),
                PartPose.offsetAndRotation(0F, 0F, 0F, 1.2347F, 1.0122F, 0F));
        PartDefinition p_pie_i = p_canilla_i.addOrReplaceChild("pie_i", CubeListBuilder.create(),
                PartPose.offsetAndRotation(-1.6F, 5.4F, -1F, 0F, 0F, 0F));
        p_pie_i.addOrReplaceChild("pie_i_c0", CubeListBuilder.create().texOffs(53, 139).addBox(-3.4F, -0.2F, -4F, 6.8F, 3.4F, 7.6F),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, -0.3F, 0F));
        p_pie_i.addOrReplaceChild("pie_i_c1", CubeListBuilder.create().texOffs(112, 161).addBox(-3.2F, 1.4F, -6F, 2F, 1.8F, 2.2F),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, -0.3F, 0F));
        p_pie_i.addOrReplaceChild("pie_i_c2", CubeListBuilder.create().texOffs(35, 167).addBox(-0.65F, -0.65F, -1.0167F, 1.3F, 1.3F, 1.1667F),
                PartPose.offsetAndRotation(-0.3877F, 2.2F, -6.1911F, 0.25F, -0.3F, 0F));
        p_pie_i.addOrReplaceChild("pie_i_c3", CubeListBuilder.create().texOffs(41, 167).addBox(-0.455F, -0.455F, -1.0167F, 0.91F, 0.91F, 1.1667F),
                PartPose.offsetAndRotation(-0.1396F, 2.4144F, -6.9933F, 0.65F, -0.3F, 0F));
        p_pie_i.addOrReplaceChild("pie_i_c4", CubeListBuilder.create().texOffs(91, 167).addBox(-0.26F, -0.26F, -1.0167F, 0.52F, 0.52F, 1.1667F),
                PartPose.offsetAndRotation(0.0643F, 2.9389F, -7.6524F, 1.05F, -0.3F, 0F));
        p_pie_i.addOrReplaceChild("pie_i_c5", CubeListBuilder.create().texOffs(112, 161).addBox(-1F, 1.4F, -6F, 2F, 1.8F, 2.2F),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, -0.3F, 0F));
        p_pie_i.addOrReplaceChild("pie_i_c6", CubeListBuilder.create().texOffs(35, 167).addBox(-0.65F, -0.65F, -1.0167F, 1.3F, 1.3F, 1.1667F),
                PartPose.offsetAndRotation(1.714F, 2.2F, -5.541F, 0.25F, -0.3F, 0F));
        p_pie_i.addOrReplaceChild("pie_i_c7", CubeListBuilder.create().texOffs(41, 167).addBox(-0.455F, -0.455F, -1.0167F, 0.91F, 0.91F, 1.1667F),
                PartPose.offsetAndRotation(1.9622F, 2.4144F, -6.3432F, 0.65F, -0.3F, 0F));
        p_pie_i.addOrReplaceChild("pie_i_c8", CubeListBuilder.create().texOffs(91, 167).addBox(-0.26F, -0.26F, -1.0167F, 0.52F, 0.52F, 1.1667F),
                PartPose.offsetAndRotation(2.1661F, 2.9389F, -7.0023F, 1.05F, -0.3F, 0F));
        p_pie_i.addOrReplaceChild("pie_i_c9", CubeListBuilder.create().texOffs(112, 161).addBox(1.2F, 1.4F, -6F, 2F, 1.8F, 2.2F),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, -0.3F, 0F));
        p_pie_i.addOrReplaceChild("pie_i_c10", CubeListBuilder.create().texOffs(35, 167).addBox(-0.65F, -0.65F, -1.0167F, 1.3F, 1.3F, 1.1667F),
                PartPose.offsetAndRotation(3.8158F, 2.2F, -4.8908F, 0.25F, -0.3F, 0F));
        p_pie_i.addOrReplaceChild("pie_i_c11", CubeListBuilder.create().texOffs(41, 167).addBox(-0.455F, -0.455F, -1.0167F, 0.91F, 0.91F, 1.1667F),
                PartPose.offsetAndRotation(4.0639F, 2.4144F, -5.693F, 0.65F, -0.3F, 0F));
        p_pie_i.addOrReplaceChild("pie_i_c12", CubeListBuilder.create().texOffs(91, 167).addBox(-0.26F, -0.26F, -1.0167F, 0.52F, 0.52F, 1.1667F),
                PartPose.offsetAndRotation(4.2678F, 2.9389F, -6.3522F, 1.05F, -0.3F, 0F));
        PartDefinition p_cabeza = p_cuerpo.addOrReplaceChild("cabeza", CubeListBuilder.create(),
                PartPose.offsetAndRotation(0F, -25.4F, -20F, 0F, 0F, 0F));
        p_cabeza.addOrReplaceChild("cabeza_c0", CubeListBuilder.create().texOffs(0, 61).addBox(-8F, -5.5F, -7.6F, 16F, 7.5F, 14.6F),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0.12F, 0F, 0F));
        p_cabeza.addOrReplaceChild("cabeza_c1", CubeListBuilder.create().texOffs(133, 85).addBox(-7.4F, -8.6F, -7.4F, 14.8F, 3.1F, 14F),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0.12F, 0F, 0F));
        p_cabeza.addOrReplaceChild("cabeza_c2", CubeListBuilder.create().texOffs(88, 124).addBox(-5.8F, -10.4F, -5.6F, 11.6F, 1.8F, 10.8F),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0.12F, 0F, 0F));
        p_cabeza.addOrReplaceChild("cabeza_c3", CubeListBuilder.create().texOffs(0, 152).addBox(-3.4F, -11.3F, -3.6F, 6.8F, 0.9F, 7F),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0.12F, 0F, 0F));
        p_cabeza.addOrReplaceChild("cabeza_c4", CubeListBuilder.create().texOffs(188, 139).addBox(-7F, -6.6F, 7F, 14F, 7.6F, 1.4F),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0.12F, 0F, 0F));
        p_cabeza.addOrReplaceChild("cabeza_c5", CubeListBuilder.create().texOffs(61, 152).addBox(-5F, -6F, 8.4F, 10F, 6F, 1F),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0.12F, 0F, 0F));
        p_cabeza.addOrReplaceChild("cabeza_c6", CubeListBuilder.create().texOffs(31, 106).addBox(-9F, -4.6F, -5.6F, 1F, 5.8F, 10.6F),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0.12F, 0F, 0F));
        p_cabeza.addOrReplaceChild("cabeza_c7", CubeListBuilder.create().texOffs(0, 139).addBox(-8.4F, -7.7F, -5.2F, 1F, 2.2F, 9.8F),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0.12F, 0F, 0F));
        p_cabeza.addOrReplaceChild("cabeza_c8", CubeListBuilder.create().texOffs(31, 106).addBox(8F, -4.6F, -5.6F, 1F, 5.8F, 10.6F),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0.12F, 0F, 0F));
        p_cabeza.addOrReplaceChild("cabeza_c9", CubeListBuilder.create().texOffs(0, 139).addBox(7.4F, -7.7F, -5.2F, 1F, 2.2F, 9.8F),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0.12F, 0F, 0F));
        p_cabeza.addOrReplaceChild("cabeza_c10", CubeListBuilder.create().texOffs(220, 139).addBox(-6.6F, -6F, -8.8F, 13.2F, 7.4F, 1.2F),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0.12F, 0F, 0F));
        p_cabeza.addOrReplaceChild("cabeza_c11", CubeListBuilder.create().texOffs(112, 139).addBox(-5.4F, -7.4F, -8.8F, 10.8F, 8.8F, 1.2F),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0.12F, 0F, 0F));
        p_cabeza.addOrReplaceChild("cabeza_c12", CubeListBuilder.create().texOffs(122, 161).addBox(-7.2F, -1.4F, -9.6F, 2.8F, 2.2F, 1.2F),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0.12F, 0F, 0F));
        p_cabeza.addOrReplaceChild("cabeza_c13", CubeListBuilder.create().texOffs(122, 161).addBox(4.4F, -1.4F, -9.6F, 2.8F, 2.2F, 1.2F),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0.12F, 0F, 0F));
        p_cabeza.addOrReplaceChild("cabeza_c14", CubeListBuilder.create().texOffs(199, 152).addBox(-6.2F, -6.9F, -8.85F, 5F, 5F, 0.3F),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0.12F, 0F, 0F));
        p_cabeza.addOrReplaceChild("cabeza_c15", CubeListBuilder.create().texOffs(199, 152).addBox(1.2F, -6.9F, -8.85F, 5F, 5F, 0.3F),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0.12F, 0F, 0F));
        p_cabeza.addOrReplaceChild("cabeza_c16", CubeListBuilder.create().texOffs(217, 161).addBox(-1.4F, -1.3F, -8.85F, 2.8F, 2.2F, 0.3F),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0.12F, 0F, 0F));
        p_cabeza.addOrReplaceChild("cabeza_c17", CubeListBuilder.create().texOffs(176, 124).addBox(-1F, -10.4F, -6F, 2F, 1F, 11.6F),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0.12F, 0F, 0F));
        p_cabeza.addOrReplaceChild("cabeza_c18", CubeListBuilder.create().texOffs(27, 161).addBox(-1F, -0.4F, -3.2F, 2F, 1.4F, 3.6F),
                PartPose.offsetAndRotation(0F, -8.8127F, -7.1061F, 0.82F, 0F, 0F));
        p_cabeza.addOrReplaceChild("cabeza_c19", CubeListBuilder.create().texOffs(92, 161).addBox(-3.6F, -1F, -0.6F, 7.2F, 1.9F, 2F),
                PartPose.offsetAndRotation(-3.6F, -6.5398F, -9.2494F, 0.1124F, -0.0422F, 0.3576F));
        p_cabeza.addOrReplaceChild("cabeza_c20", CubeListBuilder.create().texOffs(205, 124).addBox(-0.8F, -1F, -6F, 1.6F, 1F, 12F),
                PartPose.offsetAndRotation(-6.6F, -6.0357F, -1.735F, 0.1206F, 0.0993F, 0.012F));
        p_cabeza.addOrReplaceChild("cabeza_c21", CubeListBuilder.create().texOffs(92, 161).addBox(-3.6F, -1F, -0.6F, 7.2F, 1.9F, 2F),
                PartPose.offsetAndRotation(3.6F, -6.5398F, -9.2494F, 0.1124F, 0.0422F, -0.3576F));
        p_cabeza.addOrReplaceChild("cabeza_c22", CubeListBuilder.create().texOffs(205, 124).addBox(-0.8F, -1F, -6F, 1.6F, 1F, 12F),
                PartPose.offsetAndRotation(6.6F, -6.0357F, -1.735F, 0.1206F, -0.0993F, -0.012F));
        p_cabeza.addOrReplaceChild("cabeza_c23", CubeListBuilder.create().texOffs(127, 152).addBox(-5F, 1.8F, 5.2F, 10F, 4.2F, 1F),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0.12F, 0F, 0F));
        p_cabeza.addOrReplaceChild("cabeza_c24", CubeListBuilder.create().texOffs(173, 161).addBox(-1.1691F, -3.4092F, 0F, 2.3383F, 3.4092F, 0F),
                PartPose.offsetAndRotation(-5.6571F, 5.9996F, -7.9892F, 0.0466F, 0F, 0F));
        p_cabeza.addOrReplaceChild("cabeza_c25", CubeListBuilder.create().texOffs(173, 161).addBox(-1.1691F, -3.4092F, 0F, 2.3383F, 3.4092F, 0F),
                PartPose.offsetAndRotation(-5.6571F, 5.9996F, -7.9892F, 0.1062F, 0.7264F, 0.1073F));
        p_cabeza.addOrReplaceChild("cabeza_c26", CubeListBuilder.create().texOffs(47, 167).addBox(-1.1691F, -2.413F, 0F, 2.3383F, 2.413F, 0F),
                PartPose.offsetAndRotation(-3.7714F, 5.0067F, -8.1089F, 0.0162F, 0F, 0F));
        p_cabeza.addOrReplaceChild("cabeza_c27", CubeListBuilder.create().texOffs(47, 167).addBox(-1.1691F, -2.413F, 0F, 2.3383F, 2.413F, 0F),
                PartPose.offsetAndRotation(-3.7714F, 5.0067F, -8.1089F, 0.0835F, 0.7264F, 0.1073F));
        p_cabeza.addOrReplaceChild("cabeza_c28", CubeListBuilder.create().texOffs(65, 161).addBox(-1.1691F, -4.2074F, 0F, 2.3383F, 4.2074F, 0F),
                PartPose.offsetAndRotation(-1.8857F, 6.7938F, -7.8935F, 0.0605F, 0F, 0F));
        p_cabeza.addOrReplaceChild("cabeza_c29", CubeListBuilder.create().texOffs(65, 161).addBox(-1.1691F, -4.2074F, 0F, 2.3383F, 4.2074F, 0F),
                PartPose.offsetAndRotation(-1.8857F, 6.7938F, -7.8935F, 0.1166F, 0.7264F, 0.1073F));
        p_cabeza.addOrReplaceChild("cabeza_c30", CubeListBuilder.create().texOffs(53, 167).addBox(-1.1691F, -2.8111F, 0F, 2.3383F, 2.8111F, 0F),
                PartPose.offsetAndRotation(0F, 5.4039F, -8.0611F, 0.031F, 0F, 0F));
        p_cabeza.addOrReplaceChild("cabeza_c31", CubeListBuilder.create().texOffs(53, 167).addBox(-1.1691F, -2.8111F, 0F, 2.3383F, 2.8111F, 0F),
                PartPose.offsetAndRotation(0F, 5.4039F, -8.0611F, 0.0946F, 0.7264F, 0.1073F));
        p_cabeza.addOrReplaceChild("cabeza_c32", CubeListBuilder.create().texOffs(179, 161).addBox(-1.1691F, -3.8082F, 0F, 2.3383F, 3.8082F, 0F),
                PartPose.offsetAndRotation(1.8857F, 6.3967F, -7.9413F, 0.0543F, 0F, 0F));
        p_cabeza.addOrReplaceChild("cabeza_c33", CubeListBuilder.create().texOffs(179, 161).addBox(-1.1691F, -3.8082F, 0F, 2.3383F, 3.8082F, 0F),
                PartPose.offsetAndRotation(1.8857F, 6.3967F, -7.9413F, 0.112F, 0.7264F, 0.1073F));
        p_cabeza.addOrReplaceChild("cabeza_c34", CubeListBuilder.create().texOffs(59, 167).addBox(-1.1691F, -2.2142F, 0F, 2.3383F, 2.2142F, 0F),
                PartPose.offsetAndRotation(3.7714F, 4.8082F, -8.1329F, 0.0068F, 0F, 0F));
        p_cabeza.addOrReplaceChild("cabeza_c35", CubeListBuilder.create().texOffs(59, 167).addBox(-1.1691F, -2.2142F, 0F, 2.3383F, 2.2142F, 0F),
                PartPose.offsetAndRotation(3.7714F, 4.8082F, -8.1329F, 0.0766F, 0.7264F, 0.1073F));
        p_cabeza.addOrReplaceChild("cabeza_c36", CubeListBuilder.create().texOffs(185, 161).addBox(-1.1691F, -3.6087F, 0F, 2.3383F, 3.6087F, 0F),
                PartPose.offsetAndRotation(5.6571F, 6.1981F, -7.9653F, 0.0507F, 0F, 0F));
        p_cabeza.addOrReplaceChild("cabeza_c37", CubeListBuilder.create().texOffs(185, 161).addBox(-1.1691F, -3.6087F, 0F, 2.3383F, 3.6087F, 0F),
                PartPose.offsetAndRotation(5.6571F, 6.1981F, -7.9653F, 0.1093F, 0.7264F, 0.1073F));
        p_cabeza.addOrReplaceChild("cabeza_c38", CubeListBuilder.create().texOffs(145, 161).addBox(-1.395F, -3.0104F, 0F, 2.79F, 3.0104F, 0F),
                PartPose.offsetAndRotation(-7.55F, 5.2223F, -4.885F, 1.4877F, -1.4508F, -1.5708F));
        p_cabeza.addOrReplaceChild("cabeza_c39", CubeListBuilder.create().texOffs(145, 161).addBox(-1.395F, -3.0104F, 0F, 2.79F, 3.0104F, 0F),
                PartPose.offsetAndRotation(-7.55F, 5.2223F, -4.885F, 0.1165F, -0.83F, -0.1322F));
        p_cabeza.addOrReplaceChild("cabeza_c40", CubeListBuilder.create().texOffs(241, 161).addBox(-1.395F, -2.2142F, 0F, 2.79F, 2.2142F, 0F),
                PartPose.offsetAndRotation(-7.55F, 4.1587F, -2.7469F, 1.4576F, -1.4508F, -1.5708F));
        p_cabeza.addOrReplaceChild("cabeza_c41", CubeListBuilder.create().texOffs(241, 161).addBox(-1.395F, -2.2142F, 0F, 2.79F, 2.2142F, 0F),
                PartPose.offsetAndRotation(-7.55F, 4.1587F, -2.7469F, 0.0941F, -0.83F, -0.1322F));
        p_cabeza.addOrReplaceChild("cabeza_c42", CubeListBuilder.create().texOffs(248, 161).addBox(-1.395F, -2.612F, 0F, 2.79F, 2.612F, 0F),
                PartPose.offsetAndRotation(-7.55F, 4.2865F, -0.4652F, 1.4749F, -1.4508F, -1.5708F));
        p_cabeza.addOrReplaceChild("cabeza_c43", CubeListBuilder.create().texOffs(248, 161).addBox(-1.395F, -2.612F, 0F, 2.79F, 2.612F, 0F),
                PartPose.offsetAndRotation(-7.55F, 4.2865F, -0.4652F, 0.107F, -0.83F, -0.1322F));
        p_cabeza.addOrReplaceChild("cabeza_c44", CubeListBuilder.create().texOffs(84, 167).addBox(-1.395F, -1.8173F, 0F, 2.79F, 1.8173F, 0F),
                PartPose.offsetAndRotation(-7.55F, 3.2229F, 1.6729F, 1.4328F, -1.4508F, -1.5708F));
        p_cabeza.addOrReplaceChild("cabeza_c45", CubeListBuilder.create().texOffs(84, 167).addBox(-1.395F, -1.8173F, 0F, 2.79F, 1.8173F, 0F),
                PartPose.offsetAndRotation(-7.55F, 3.2229F, 1.6729F, 0.0755F, -0.83F, -0.1322F));
        p_cabeza.addOrReplaceChild("cabeza_c46", CubeListBuilder.create().texOffs(145, 161).addBox(-1.395F, -3.0104F, 0F, 2.79F, 3.0104F, 0F),
                PartPose.offsetAndRotation(8.05F, 5.2223F, -4.885F, 1.4877F, -1.4508F, -1.5708F));
        p_cabeza.addOrReplaceChild("cabeza_c47", CubeListBuilder.create().texOffs(145, 161).addBox(-1.395F, -3.0104F, 0F, 2.79F, 3.0104F, 0F),
                PartPose.offsetAndRotation(8.05F, 5.2223F, -4.885F, 0.1165F, -0.83F, -0.1322F));
        p_cabeza.addOrReplaceChild("cabeza_c48", CubeListBuilder.create().texOffs(241, 161).addBox(-1.395F, -2.2142F, 0F, 2.79F, 2.2142F, 0F),
                PartPose.offsetAndRotation(8.05F, 4.1587F, -2.7469F, 1.4576F, -1.4508F, -1.5708F));
        p_cabeza.addOrReplaceChild("cabeza_c49", CubeListBuilder.create().texOffs(241, 161).addBox(-1.395F, -2.2142F, 0F, 2.79F, 2.2142F, 0F),
                PartPose.offsetAndRotation(8.05F, 4.1587F, -2.7469F, 0.0941F, -0.83F, -0.1322F));
        p_cabeza.addOrReplaceChild("cabeza_c50", CubeListBuilder.create().texOffs(248, 161).addBox(-1.395F, -2.612F, 0F, 2.79F, 2.612F, 0F),
                PartPose.offsetAndRotation(8.05F, 4.2865F, -0.4652F, 1.4749F, -1.4508F, -1.5708F));
        p_cabeza.addOrReplaceChild("cabeza_c51", CubeListBuilder.create().texOffs(248, 161).addBox(-1.395F, -2.612F, 0F, 2.79F, 2.612F, 0F),
                PartPose.offsetAndRotation(8.05F, 4.2865F, -0.4652F, 0.107F, -0.83F, -0.1322F));
        p_cabeza.addOrReplaceChild("cabeza_c52", CubeListBuilder.create().texOffs(84, 167).addBox(-1.395F, -1.8173F, 0F, 2.79F, 1.8173F, 0F),
                PartPose.offsetAndRotation(8.05F, 3.2229F, 1.6729F, 1.4328F, -1.4508F, -1.5708F));
        p_cabeza.addOrReplaceChild("cabeza_c53", CubeListBuilder.create().texOffs(84, 167).addBox(-1.395F, -1.8173F, 0F, 2.79F, 1.8173F, 0F),
                PartPose.offsetAndRotation(8.05F, 3.2229F, 1.6729F, 0.0755F, -0.83F, -0.1322F));
        PartDefinition p_quijada = p_cabeza.addOrReplaceChild("quijada", CubeListBuilder.create(),
                PartPose.offsetAndRotation(0F, 1.2195F, 6.5934F, 0.16F, 0F, 0F));
        p_quijada.addOrReplaceChild("quijada_c0", CubeListBuilder.create().texOffs(73, 85).addBox(-7.4F, 0F, -14.6F, 14.8F, 4.6F, 14.6F),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        p_quijada.addOrReplaceChild("quijada_c1", CubeListBuilder.create().texOffs(196, 106).addBox(-5.8F, 4.5F, -13.8F, 11.6F, 1.3F, 12.6F),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        p_quijada.addOrReplaceChild("quijada_c2", CubeListBuilder.create().texOffs(0, 161).addBox(-6F, 0F, -15.3F, 12F, 4F, 0.8F),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        p_quijada.addOrReplaceChild("quijada_c3", CubeListBuilder.create().texOffs(0, 167).addBox(-1.3227F, -2.612F, 0F, 2.6453F, 2.612F, 0F),
                PartPose.offsetAndRotation(-5.3333F, -2.6F, -14.25F, -3.0457F, 0F, 0F));
        p_quijada.addOrReplaceChild("quijada_c4", CubeListBuilder.create().texOffs(0, 167).addBox(-1.3227F, -2.612F, 0F, 2.6453F, 2.612F, 0F),
                PartPose.offsetAndRotation(-5.3333F, -2.6F, -14.25F, -3.0702F, 0.7328F, 0F));
        p_quijada.addOrReplaceChild("quijada_c5", CubeListBuilder.create().texOffs(152, 161).addBox(-1.3227F, -3.6087F, 0F, 2.6453F, 3.6087F, 0F),
                PartPose.offsetAndRotation(-3.2F, -3.6F, -14.25F, -3.0723F, 0F, 0F));
        p_quijada.addOrReplaceChild("quijada_c6", CubeListBuilder.create().texOffs(152, 161).addBox(-1.3227F, -3.6087F, 0F, 2.6453F, 3.6087F, 0F),
                PartPose.offsetAndRotation(-3.2F, -3.6F, -14.25F, -3.09F, 0.7328F, 0F));
        p_quijada.addOrReplaceChild("quijada_c7", CubeListBuilder.create().texOffs(7, 167).addBox(-1.3227F, -2.0156F, 0F, 2.6453F, 2.0156F, 0F),
                PartPose.offsetAndRotation(-1.0667F, -2F, -14.25F, -3.0172F, 0F, 0F));
        p_quijada.addOrReplaceChild("quijada_c8", CubeListBuilder.create().texOffs(7, 167).addBox(-1.3227F, -2.0156F, 0F, 2.6453F, 2.0156F, 0F),
                PartPose.offsetAndRotation(-1.0667F, -2F, -14.25F, -3.0489F, 0.7328F, 0F));
        p_quijada.addOrReplaceChild("quijada_c9", CubeListBuilder.create().texOffs(159, 161).addBox(-1.3227F, -3.2098F, 0F, 2.6453F, 3.2098F, 0F),
                PartPose.offsetAndRotation(1.0667F, -3.2F, -14.25F, -3.0636F, 0F, 0F));
        p_quijada.addOrReplaceChild("quijada_c10", CubeListBuilder.create().texOffs(159, 161).addBox(-1.3227F, -3.2098F, 0F, 2.6453F, 3.2098F, 0F),
                PartPose.offsetAndRotation(1.0667F, -3.2F, -14.25F, -3.0836F, 0.7328F, 0F));
        p_quijada.addOrReplaceChild("quijada_c11", CubeListBuilder.create().texOffs(14, 167).addBox(-1.3227F, -2.413F, 0F, 2.6453F, 2.413F, 0F),
                PartPose.offsetAndRotation(3.2F, -2.4F, -14.25F, -3.0378F, 0F, 0F));
        p_quijada.addOrReplaceChild("quijada_c12", CubeListBuilder.create().texOffs(14, 167).addBox(-1.3227F, -2.413F, 0F, 2.6453F, 2.413F, 0F),
                PartPose.offsetAndRotation(3.2F, -2.4F, -14.25F, -3.0643F, 0.7328F, 0F));
        p_quijada.addOrReplaceChild("quijada_c13", CubeListBuilder.create().texOffs(166, 161).addBox(-1.3227F, -3.4092F, 0F, 2.6453F, 3.4092F, 0F),
                PartPose.offsetAndRotation(5.3333F, -3.4F, -14.25F, -3.0682F, 0F, 0F));
        p_quijada.addOrReplaceChild("quijada_c14", CubeListBuilder.create().texOffs(166, 161).addBox(-1.3227F, -3.4092F, 0F, 2.6453F, 3.4092F, 0F),
                PartPose.offsetAndRotation(5.3333F, -3.4F, -14.25F, -3.087F, 0.7328F, 0F));
        p_quijada.addOrReplaceChild("quijada_c15", CubeListBuilder.create().texOffs(225, 161).addBox(-1.736F, -2.413F, 0F, 3.472F, 2.413F, 0F),
                PartPose.offsetAndRotation(-6.95F, -2.4F, -11F, -3.0378F, -1.5708F, 0F));
        p_quijada.addOrReplaceChild("quijada_c16", CubeListBuilder.create().texOffs(225, 161).addBox(-1.736F, -2.413F, 0F, 3.472F, 2.413F, 0F),
                PartPose.offsetAndRotation(-6.95F, -2.4F, -11F, -3.0643F, -0.838F, 0F));
        p_quijada.addOrReplaceChild("quijada_c17", CubeListBuilder.create().texOffs(76, 167).addBox(-1.736F, -1.8173F, 0F, 3.472F, 1.8173F, 0F),
                PartPose.offsetAndRotation(-6.95F, -1.8F, -8.2F, -3.0036F, -1.5708F, 0F));
        p_quijada.addOrReplaceChild("quijada_c18", CubeListBuilder.create().texOffs(76, 167).addBox(-1.736F, -1.8173F, 0F, 3.472F, 1.8173F, 0F),
                PartPose.offsetAndRotation(-6.95F, -1.8F, -8.2F, -3.0387F, -0.838F, 0F));
        p_quijada.addOrReplaceChild("quijada_c19", CubeListBuilder.create().texOffs(233, 161).addBox(-1.736F, -2.0156F, 0F, 3.472F, 2.0156F, 0F),
                PartPose.offsetAndRotation(-6.95F, -2F, -5.4F, -3.0172F, -1.5708F, 0F));
        p_quijada.addOrReplaceChild("quijada_c20", CubeListBuilder.create().texOffs(233, 161).addBox(-1.736F, -2.0156F, 0F, 3.472F, 2.0156F, 0F),
                PartPose.offsetAndRotation(-6.95F, -2F, -5.4F, -3.0489F, -0.838F, 0F));
        p_quijada.addOrReplaceChild("quijada_c21", CubeListBuilder.create().texOffs(225, 161).addBox(-1.736F, -2.413F, 0F, 3.472F, 2.413F, 0F),
                PartPose.offsetAndRotation(7.45F, -2.4F, -11F, -3.0378F, -1.5708F, 0F));
        p_quijada.addOrReplaceChild("quijada_c22", CubeListBuilder.create().texOffs(225, 161).addBox(-1.736F, -2.413F, 0F, 3.472F, 2.413F, 0F),
                PartPose.offsetAndRotation(7.45F, -2.4F, -11F, -3.0643F, -0.838F, 0F));
        p_quijada.addOrReplaceChild("quijada_c23", CubeListBuilder.create().texOffs(76, 167).addBox(-1.736F, -1.8173F, 0F, 3.472F, 1.8173F, 0F),
                PartPose.offsetAndRotation(7.45F, -1.8F, -8.2F, -3.0036F, -1.5708F, 0F));
        p_quijada.addOrReplaceChild("quijada_c24", CubeListBuilder.create().texOffs(76, 167).addBox(-1.736F, -1.8173F, 0F, 3.472F, 1.8173F, 0F),
                PartPose.offsetAndRotation(7.45F, -1.8F, -8.2F, -3.0387F, -0.838F, 0F));
        p_quijada.addOrReplaceChild("quijada_c25", CubeListBuilder.create().texOffs(233, 161).addBox(-1.736F, -2.0156F, 0F, 3.472F, 2.0156F, 0F),
                PartPose.offsetAndRotation(7.45F, -2F, -5.4F, -3.0172F, -1.5708F, 0F));
        p_quijada.addOrReplaceChild("quijada_c26", CubeListBuilder.create().texOffs(233, 161).addBox(-1.736F, -2.0156F, 0F, 3.472F, 2.0156F, 0F),
                PartPose.offsetAndRotation(7.45F, -2F, -5.4F, -3.0489F, -0.838F, 0F));
        PartDefinition p_cresta = p_cabeza.addOrReplaceChild("cresta", CubeListBuilder.create(),
                PartPose.offsetAndRotation(0F, -9.3324F, -1.1253F, 0.12F, 0F, 0F));
        p_cresta.addOrReplaceChild("cresta_c0", CubeListBuilder.create().texOffs(113, 152).addBox(-1.3F, -6.05F, 0F, 2.6F, 6.05F, 0F),
                PartPose.offsetAndRotation(0F, -5.4113F, -1.2944F, 2.6779F, 0F, 0F));
        p_cresta.addOrReplaceChild("cresta_c1", CubeListBuilder.create().texOffs(113, 152).addBox(-1.3F, -6.05F, 0F, 2.6F, 6.05F, 0F),
                PartPose.offsetAndRotation(0F, -5.4113F, -1.2944F, 1.5708F, -1.1071F, 1.5708F));
        p_cresta.addOrReplaceChild("cresta_c2", CubeListBuilder.create().texOffs(77, 161).addBox(-0.975F, -4.95F, 0F, 1.95F, 4.95F, 0F),
                PartPose.offsetAndRotation(0F, -8.4937F, 2.5788F, 2.243F, 0F, 0F));
        p_cresta.addOrReplaceChild("cresta_c3", CubeListBuilder.create().texOffs(77, 161).addBox(-0.975F, -4.95F, 0F, 1.95F, 4.95F, 0F),
                PartPose.offsetAndRotation(0F, -8.4937F, 2.5788F, 1.5708F, -0.6722F, 1.5708F));
        p_cresta.addOrReplaceChild("cresta_c4", CubeListBuilder.create().texOffs(223, 152).addBox(-1.3F, -5.5F, 0F, 2.6F, 5.5F, 0F),
                PartPose.offsetAndRotation(-2.4546F, -4.4511F, 1.1157F, 2.5022F, -0.3197F, 0.0399F));
        p_cresta.addOrReplaceChild("cresta_c5", CubeListBuilder.create().texOffs(223, 152).addBox(-1.3F, -5.5F, 0F, 2.6F, 5.5F, 0F),
                PartPose.offsetAndRotation(-2.4546F, -4.4511F, 1.1157F, 1.0642F, -0.866F, 2.0106F));
        p_cresta.addOrReplaceChild("cresta_c6", CubeListBuilder.create().texOffs(82, 161).addBox(-0.975F, -4.5F, 0F, 1.95F, 4.5F, 0F),
                PartPose.offsetAndRotation(-3.7015F, -6.1651F, 5.0853F, 1.9493F, -0.3197F, 0.0399F));
        p_cresta.addOrReplaceChild("cresta_c7", CubeListBuilder.create().texOffs(82, 161).addBox(-0.975F, -4.5F, 0F, 1.95F, 4.5F, 0F),
                PartPose.offsetAndRotation(-3.7015F, -6.1651F, 5.0853F, 1.2285F, -0.3584F, 1.7351F));
        p_cresta.addOrReplaceChild("cresta_c8", CubeListBuilder.create().texOffs(223, 152).addBox(-1.3F, -5.5F, 0F, 2.6F, 5.5F, 0F),
                PartPose.offsetAndRotation(2.4546F, -4.4511F, 1.1157F, 2.5022F, 0.3197F, -0.0399F));
        p_cresta.addOrReplaceChild("cresta_c9", CubeListBuilder.create().texOffs(223, 152).addBox(-1.3F, -5.5F, 0F, 2.6F, 5.5F, 0F),
                PartPose.offsetAndRotation(2.4546F, -4.4511F, 1.1157F, 2.0774F, -0.866F, 1.131F));
        p_cresta.addOrReplaceChild("cresta_c10", CubeListBuilder.create().texOffs(82, 161).addBox(-0.975F, -4.5F, 0F, 1.95F, 4.5F, 0F),
                PartPose.offsetAndRotation(3.7015F, -6.1651F, 5.0853F, 1.9493F, 0.3197F, -0.0399F));
        p_cresta.addOrReplaceChild("cresta_c11", CubeListBuilder.create().texOffs(82, 161).addBox(-0.975F, -4.5F, 0F, 1.95F, 4.5F, 0F),
                PartPose.offsetAndRotation(3.7015F, -6.1651F, 5.0853F, 1.9131F, -0.3584F, 1.4065F));
        p_cresta.addOrReplaceChild("cresta_c12", CubeListBuilder.create().texOffs(120, 152).addBox(-1.3F, -6.6F, 0F, 2.6F, 6.6F, 0F),
                PartPose.offsetAndRotation(-1.2698F, -4.8933F, 4.904F, 2.4043F, -0.1225F, 0.0149F));
        p_cresta.addOrReplaceChild("cresta_c13", CubeListBuilder.create().texOffs(120, 152).addBox(-1.3F, -6.6F, 0F, 2.6F, 6.6F, 0F),
                PartPose.offsetAndRotation(-1.2698F, -4.8933F, 4.904F, 1.3896F, -0.8253F, 1.7194F));
        p_cresta.addOrReplaceChild("cresta_c14", CubeListBuilder.create().texOffs(230, 152).addBox(-0.975F, -5.4F, 0F, 1.95F, 5.4F, 0F),
                PartPose.offsetAndRotation(-1.8926F, -6.1684F, 10.1142F, 1.8074F, -0.1225F, 0.0149F));
        p_cresta.addOrReplaceChild("cresta_c15", CubeListBuilder.create().texOffs(230, 152).addBox(-0.975F, -5.4F, 0F, 1.95F, 5.4F, 0F),
                PartPose.offsetAndRotation(-1.8926F, -6.1684F, 10.1142F, 1.4448F, -0.2348F, 1.6151F));
        p_cresta.addOrReplaceChild("cresta_c16", CubeListBuilder.create().texOffs(120, 152).addBox(-1.3F, -6.6F, 0F, 2.6F, 6.6F, 0F),
                PartPose.offsetAndRotation(1.2698F, -4.8933F, 4.904F, 2.4043F, 0.1225F, -0.0149F));
        p_cresta.addOrReplaceChild("cresta_c17", CubeListBuilder.create().texOffs(120, 152).addBox(-1.3F, -6.6F, 0F, 2.6F, 6.6F, 0F),
                PartPose.offsetAndRotation(1.2698F, -4.8933F, 4.904F, 1.752F, -0.8253F, 1.4222F));
        p_cresta.addOrReplaceChild("cresta_c18", CubeListBuilder.create().texOffs(230, 152).addBox(-0.975F, -5.4F, 0F, 1.95F, 5.4F, 0F),
                PartPose.offsetAndRotation(1.8926F, -6.1684F, 10.1142F, 1.8074F, 0.1225F, -0.0149F));
        p_cresta.addOrReplaceChild("cresta_c19", CubeListBuilder.create().texOffs(230, 152).addBox(-0.975F, -5.4F, 0F, 1.95F, 5.4F, 0F),
                PartPose.offsetAndRotation(1.8926F, -6.1684F, 10.1142F, 1.6968F, -0.2348F, 1.5265F));
        p_cresta.addOrReplaceChild("cresta_c20", CubeListBuilder.create().texOffs(58, 161).addBox(-1.3F, -4.95F, 0F, 2.6F, 4.95F, 0F),
                PartPose.offsetAndRotation(-3.6167F, -3.2587F, 6.0846F, 2.2783F, -0.3082F, 0.0384F));
        p_cresta.addOrReplaceChild("cresta_c21", CubeListBuilder.create().texOffs(58, 161).addBox(-1.3F, -4.95F, 0F, 2.6F, 4.95F, 0F),
                PartPose.offsetAndRotation(-3.6167F, -3.2587F, 6.0846F, 1.1741F, -0.6679F, 1.863F));
        p_cresta.addOrReplaceChild("cresta_c22", CubeListBuilder.create().texOffs(87, 161).addBox(-0.975F, -4.05F, 0F, 1.95F, 4.05F, 0F),
                PartPose.offsetAndRotation(-4.828F, -3.6282F, 9.9315F, 1.6506F, -0.3082F, 0.0384F));
        p_cresta.addOrReplaceChild("cresta_c23", CubeListBuilder.create().texOffs(87, 161).addBox(-0.975F, -4.05F, 0F, 1.95F, 4.05F, 0F),
                PartPose.offsetAndRotation(-4.828F, -3.6282F, 9.9315F, 1.2617F, -0.076F, 1.6334F));
        p_cresta.addOrReplaceChild("cresta_c24", CubeListBuilder.create().texOffs(58, 161).addBox(-1.3F, -4.95F, 0F, 2.6F, 4.95F, 0F),
                PartPose.offsetAndRotation(3.6167F, -3.2587F, 6.0846F, 2.2783F, 0.3082F, -0.0384F));
        p_cresta.addOrReplaceChild("cresta_c25", CubeListBuilder.create().texOffs(58, 161).addBox(-1.3F, -4.95F, 0F, 2.6F, 4.95F, 0F),
                PartPose.offsetAndRotation(3.6167F, -3.2587F, 6.0846F, 1.9675F, -0.6679F, 1.2786F));
        p_cresta.addOrReplaceChild("cresta_c26", CubeListBuilder.create().texOffs(87, 161).addBox(-0.975F, -4.05F, 0F, 1.95F, 4.05F, 0F),
                PartPose.offsetAndRotation(4.828F, -3.6282F, 9.9315F, 1.6506F, 0.3082F, -0.0384F));
        p_cresta.addOrReplaceChild("cresta_c27", CubeListBuilder.create().texOffs(87, 161).addBox(-0.975F, -4.05F, 0F, 1.95F, 4.05F, 0F),
                PartPose.offsetAndRotation(4.828F, -3.6282F, 9.9315F, 1.8799F, -0.076F, 1.5082F));
        p_cresta.addOrReplaceChild("cresta_c28", CubeListBuilder.create().texOffs(113, 152).addBox(-1.3F, -6.05F, 0F, 2.6F, 6.05F, 0F),
                PartPose.offsetAndRotation(0F, -3.8731F, 8.1477F, 2.2655F, 0F, 0F));
        p_cresta.addOrReplaceChild("cresta_c29", CubeListBuilder.create().texOffs(113, 152).addBox(-1.3F, -6.05F, 0F, 2.6F, 6.05F, 0F),
                PartPose.offsetAndRotation(0F, -3.8731F, 8.1477F, 1.5708F, -0.6947F, 1.5708F));
        p_cresta.addOrReplaceChild("cresta_c30", CubeListBuilder.create().texOffs(77, 161).addBox(-0.975F, -4.95F, 0F, 1.95F, 4.95F, 0F),
                PartPose.offsetAndRotation(0F, -4.1888F, 13.0877F, 1.6346F, 0F, 0F));
        p_cresta.addOrReplaceChild("cresta_c31", CubeListBuilder.create().texOffs(77, 161).addBox(-0.975F, -4.95F, 0F, 1.95F, 4.95F, 0F),
                PartPose.offsetAndRotation(0F, -4.1888F, 13.0877F, 1.5708F, -0.0638F, 1.5708F));
        p_cresta.addOrReplaceChild("cresta_c32", CubeListBuilder.create().texOffs(51, 161).addBox(-1.3F, -4.4F, 0F, 2.6F, 4.4F, 0F),
                PartPose.offsetAndRotation(-2.088F, -2.5417F, 8.5583F, 2.1841F, -0.1489F, 0.0181F));
        p_cresta.addOrReplaceChild("cresta_c33", CubeListBuilder.create().texOffs(51, 161).addBox(-1.3F, -4.4F, 0F, 2.6F, 4.4F, 0F),
                PartPose.offsetAndRotation(-2.088F, -2.5417F, 8.5583F, 1.3893F, -0.6055F, 1.6929F));
        p_cresta.addOrReplaceChild("cresta_c34", CubeListBuilder.create().texOffs(202, 161).addBox(-0.975F, -3.6F, 0F, 1.95F, 3.6F, 0F),
                PartPose.offsetAndRotation(-2.6236F, -2.4546F, 12.1172F, 1.5439F, -0.1489F, 0.0181F));
        p_cresta.addOrReplaceChild("cresta_c35", CubeListBuilder.create().texOffs(202, 161).addBox(-0.975F, -3.6F, 0F, 1.95F, 3.6F, 0F),
                PartPose.offsetAndRotation(-2.6236F, -2.4546F, 12.1172F, 1.4218F, 0.0266F, 1.5849F));
        p_cresta.addOrReplaceChild("cresta_c36", CubeListBuilder.create().texOffs(51, 161).addBox(-1.3F, -4.4F, 0F, 2.6F, 4.4F, 0F),
                PartPose.offsetAndRotation(2.088F, -2.5417F, 8.5583F, 2.1841F, 0.1489F, -0.0181F));
        p_cresta.addOrReplaceChild("cresta_c37", CubeListBuilder.create().texOffs(51, 161).addBox(-1.3F, -4.4F, 0F, 2.6F, 4.4F, 0F),
                PartPose.offsetAndRotation(2.088F, -2.5417F, 8.5583F, 1.7523F, -0.6055F, 1.4486F));
        p_cresta.addOrReplaceChild("cresta_c38", CubeListBuilder.create().texOffs(202, 161).addBox(-0.975F, -3.6F, 0F, 1.95F, 3.6F, 0F),
                PartPose.offsetAndRotation(2.6236F, -2.4546F, 12.1172F, 1.5439F, 0.1489F, -0.0181F));
        p_cresta.addOrReplaceChild("cresta_c39", CubeListBuilder.create().texOffs(202, 161).addBox(-0.975F, -3.6F, 0F, 1.95F, 3.6F, 0F),
                PartPose.offsetAndRotation(2.6236F, -2.4546F, 12.1172F, 1.7198F, 0.0266F, 1.5567F));
        p_cresta.addOrReplaceChild("cresta_c40", CubeListBuilder.create().texOffs(71, 161).addBox(-1.2F, -4.4F, 0F, 2.4F, 4.4F, 0F),
                PartPose.offsetAndRotation(-10.8312F, 4.6563F, 4.7187F, 1.7023F, -0.55F, 0.074F));
        p_cresta.addOrReplaceChild("cresta_c41", CubeListBuilder.create().texOffs(71, 161).addBox(-1.2F, -4.4F, 0F, 2.4F, 4.4F, 0F),
                PartPose.offsetAndRotation(-10.8312F, 4.6563F, 4.7187F, 1.0169F, -0.112F, 1.7138F));
        p_cresta.addOrReplaceChild("cresta_c42", CubeListBuilder.create().texOffs(207, 161).addBox(-0.9F, -3.6F, 0F, 1.8F, 3.6F, 0F),
                PartPose.offsetAndRotation(-12.4166F, 6.9214F, 7.0242F, 0.8499F, -0.55F, 0.074F));
        p_cresta.addOrReplaceChild("cresta_c43", CubeListBuilder.create().texOffs(207, 161).addBox(-0.9F, -3.6F, 0F, 1.8F, 3.6F, 0F),
                PartPose.offsetAndRotation(-12.4166F, 6.9214F, 7.0242F, 0.8863F, 0.5976F, 1.2143F));
        p_cresta.addOrReplaceChild("cresta_c44", CubeListBuilder.create().texOffs(191, 161).addBox(-1.2F, -3.85F, 0F, 2.4F, 3.85F, 0F),
                PartPose.offsetAndRotation(-10.5523F, 4.7492F, 7.2538F, 1.7023F, -0.55F, 0.074F));
        p_cresta.addOrReplaceChild("cresta_c45", CubeListBuilder.create().texOffs(191, 161).addBox(-1.2F, -3.85F, 0F, 2.4F, 3.85F, 0F),
                PartPose.offsetAndRotation(-10.5523F, 4.7492F, 7.2538F, 1.0169F, -0.112F, 1.7138F));
        p_cresta.addOrReplaceChild("cresta_c46", CubeListBuilder.create().texOffs(212, 161).addBox(-0.9F, -3.15F, 0F, 1.8F, 3.15F, 0F),
                PartPose.offsetAndRotation(-11.9396F, 6.7312F, 9.2712F, 0.8499F, -0.55F, 0.074F));
        p_cresta.addOrReplaceChild("cresta_c47", CubeListBuilder.create().texOffs(212, 161).addBox(-0.9F, -3.15F, 0F, 1.8F, 3.15F, 0F),
                PartPose.offsetAndRotation(-11.9396F, 6.7312F, 9.2712F, 0.8863F, 0.5976F, 1.2143F));
        p_cresta.addOrReplaceChild("cresta_c48", CubeListBuilder.create().texOffs(71, 161).addBox(-1.2F, -4.4F, 0F, 2.4F, 4.4F, 0F),
                PartPose.offsetAndRotation(10.8312F, 4.6563F, 4.7187F, 1.7023F, 0.55F, -0.074F));
        p_cresta.addOrReplaceChild("cresta_c49", CubeListBuilder.create().texOffs(71, 161).addBox(-1.2F, -4.4F, 0F, 2.4F, 4.4F, 0F),
                PartPose.offsetAndRotation(10.8312F, 4.6563F, 4.7187F, 2.1247F, -0.112F, 1.4278F));
        p_cresta.addOrReplaceChild("cresta_c50", CubeListBuilder.create().texOffs(207, 161).addBox(-0.9F, -3.6F, 0F, 1.8F, 3.6F, 0F),
                PartPose.offsetAndRotation(12.4166F, 6.9214F, 7.0242F, 0.8499F, 0.55F, -0.074F));
        p_cresta.addOrReplaceChild("cresta_c51", CubeListBuilder.create().texOffs(207, 161).addBox(-0.9F, -3.6F, 0F, 1.8F, 3.6F, 0F),
                PartPose.offsetAndRotation(12.4166F, 6.9214F, 7.0242F, 2.2553F, 0.5976F, 1.9273F));
        p_cresta.addOrReplaceChild("cresta_c52", CubeListBuilder.create().texOffs(191, 161).addBox(-1.2F, -3.85F, 0F, 2.4F, 3.85F, 0F),
                PartPose.offsetAndRotation(10.5523F, 4.7492F, 7.2538F, 1.7023F, 0.55F, -0.074F));
        p_cresta.addOrReplaceChild("cresta_c53", CubeListBuilder.create().texOffs(191, 161).addBox(-1.2F, -3.85F, 0F, 2.4F, 3.85F, 0F),
                PartPose.offsetAndRotation(10.5523F, 4.7492F, 7.2538F, 2.1247F, -0.112F, 1.4278F));
        p_cresta.addOrReplaceChild("cresta_c54", CubeListBuilder.create().texOffs(212, 161).addBox(-0.9F, -3.15F, 0F, 1.8F, 3.15F, 0F),
                PartPose.offsetAndRotation(11.9396F, 6.7312F, 9.2712F, 0.8499F, 0.55F, -0.074F));
        p_cresta.addOrReplaceChild("cresta_c55", CubeListBuilder.create().texOffs(212, 161).addBox(-0.9F, -3.15F, 0F, 1.8F, 3.15F, 0F),
                PartPose.offsetAndRotation(11.9396F, 6.7312F, 9.2712F, 2.2553F, 0.5976F, 1.9273F));
        PartDefinition p_brazo_i = p_tronco.addOrReplaceChild("brazo_i", CubeListBuilder.create(),
                PartPose.offsetAndRotation(14.8F, -13.6F, -3F, -0.38F, 0F, 0F));
        p_brazo_i.addOrReplaceChild("brazo_i_c0", CubeListBuilder.create().texOffs(63, 61).addBox(-2.9F, -2.9F, -14.5271F, 5.8F, 5.8F, 16.2671F),
                PartPose.offsetAndRotation(0F, 0F, 0F, -2.1758F, -1.1711F, 3.1416F));
        PartDefinition p_antebrazo_i = p_brazo_i.addOrReplaceChild("antebrazo_i", CubeListBuilder.create(),
                PartPose.offsetAndRotation(6.7F, 10.5171F, 2.8305F, 0F, 0F, 0F));
        p_antebrazo_i.addOrReplaceChild("antebrazo_i_c0", CubeListBuilder.create().texOffs(191, 34).addBox(-2.7F, -2.7F, -17.6624F, 5.4F, 5.4F, 19.2824F),
                PartPose.offsetAndRotation(0F, 0F, 0F, 1.1143F, 0.1419F, 0F));
        PartDefinition p_mano_i = p_antebrazo_i.addOrReplaceChild("mano_i", CubeListBuilder.create(),
                PartPose.offsetAndRotation(-1F, 14.4F, -7F, 0F, 0F, 0F));
        p_mano_i.addOrReplaceChild("mano_i_c0", CubeListBuilder.create().texOffs(83, 139).addBox(-3.6F, -1.5F, -5.8F, 7.2F, 3F, 6.4F),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0.3373F, -0.0917F, -0.023F));
        p_mano_i.addOrReplaceChild("mano_i_c1", CubeListBuilder.create().texOffs(150, 152).addBox(-3F, -2F, -5.2F, 6F, 0.8F, 4.6F),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0.3373F, -0.0917F, -0.023F));
        PartDefinition p_mano_i_dedo0 = p_mano_i.addOrReplaceChild("mano_i_dedo0", CubeListBuilder.create(),
                PartPose.offsetAndRotation(-2.1805F, 1.8378F, -5.3215F, 0.876F, 0.0332F, 0.0207F));
        p_mano_i_dedo0.addOrReplaceChild("mano_i_dedo0_c0", CubeListBuilder.create().texOffs(84, 152).addBox(-1F, -1F, -4.4F, 2F, 2F, 4.7F),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        PartDefinition p_mano_i_dedo0b = p_mano_i_dedo0.addOrReplaceChild("mano_i_dedo0b", CubeListBuilder.create(),
                PartPose.offsetAndRotation(0F, 0F, -4.4F, 0.72F, 0F, 0F));
        p_mano_i_dedo0b.addOrReplaceChild("mano_i_dedo0b_c0", CubeListBuilder.create().texOffs(211, 152).addBox(-0.85F, -0.85F, -3.3F, 1.7F, 1.7F, 3.6F),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        p_mano_i_dedo0b.addOrReplaceChild("mano_i_dedo0b_c1", CubeListBuilder.create().texOffs(21, 167).addBox(-0.75F, -0.75F, -1.35F, 1.5F, 1.5F, 1.5F),
                PartPose.offsetAndRotation(0F, 0.1F, -3.3F, 0.45F, 0F, 0F));
        p_mano_i_dedo0b.addOrReplaceChild("mano_i_dedo0b_c2", CubeListBuilder.create().texOffs(28, 167).addBox(-0.525F, -0.525F, -1.35F, 1.05F, 1.05F, 1.5F),
                PartPose.offsetAndRotation(0F, 0.622F, -4.3805F, 0.85F, 0F, 0F));
        p_mano_i_dedo0b.addOrReplaceChild("mano_i_dedo0b_c3", CubeListBuilder.create().texOffs(65, 167).addBox(-0.3F, -0.3F, -1.35F, 0.6F, 0.6F, 1.5F),
                PartPose.offsetAndRotation(0F, 1.5235F, -5.1725F, 1.25F, 0F, 0F));
        PartDefinition p_mano_i_dedo1 = p_mano_i.addOrReplaceChild("mano_i_dedo1", CubeListBuilder.create(),
                PartPose.offsetAndRotation(-0.3886F, 1.7966F, -5.1567F, 0.8763F, -0.05F, -0.0084F));
        p_mano_i_dedo1.addOrReplaceChild("mano_i_dedo1_c0", CubeListBuilder.create().texOffs(29, 152).addBox(-1F, -1F, -5.2F, 2F, 2F, 5.5F),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        PartDefinition p_mano_i_dedo1b = p_mano_i_dedo1.addOrReplaceChild("mano_i_dedo1b", CubeListBuilder.create(),
                PartPose.offsetAndRotation(0F, 0F, -5.2F, 0.72F, 0F, 0F));
        p_mano_i_dedo1b.addOrReplaceChild("mano_i_dedo1b_c0", CubeListBuilder.create().texOffs(173, 152).addBox(-0.85F, -0.85F, -3.9F, 1.7F, 1.7F, 4.2F),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        p_mano_i_dedo1b.addOrReplaceChild("mano_i_dedo1b_c1", CubeListBuilder.create().texOffs(21, 167).addBox(-0.75F, -0.75F, -1.35F, 1.5F, 1.5F, 1.5F),
                PartPose.offsetAndRotation(0F, 0.1F, -3.9F, 0.45F, 0F, 0F));
        p_mano_i_dedo1b.addOrReplaceChild("mano_i_dedo1b_c2", CubeListBuilder.create().texOffs(28, 167).addBox(-0.525F, -0.525F, -1.35F, 1.05F, 1.05F, 1.5F),
                PartPose.offsetAndRotation(0F, 0.622F, -4.9805F, 0.85F, 0F, 0F));
        p_mano_i_dedo1b.addOrReplaceChild("mano_i_dedo1b_c3", CubeListBuilder.create().texOffs(65, 167).addBox(-0.3F, -0.3F, -1.35F, 0.6F, 0.6F, 1.5F),
                PartPose.offsetAndRotation(0F, 1.5235F, -5.7725F, 1.25F, 0F, 0F));
        PartDefinition p_mano_i_dedo2 = p_mano_i.addOrReplaceChild("mano_i_dedo2", CubeListBuilder.create(),
                PartPose.offsetAndRotation(1.4034F, 1.7554F, -4.9919F, 0.879F, -0.1333F, -0.0377F));
        p_mano_i_dedo2.addOrReplaceChild("mano_i_dedo2_c0", CubeListBuilder.create().texOffs(45, 152).addBox(-1F, -1F, -5F, 2F, 2F, 5.3F),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        PartDefinition p_mano_i_dedo2b = p_mano_i_dedo2.addOrReplaceChild("mano_i_dedo2b", CubeListBuilder.create(),
                PartPose.offsetAndRotation(0F, 0F, -5F, 0.72F, 0F, 0F));
        p_mano_i_dedo2b.addOrReplaceChild("mano_i_dedo2b_c0", CubeListBuilder.create().texOffs(186, 152).addBox(-0.85F, -0.85F, -3.75F, 1.7F, 1.7F, 4.05F),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        p_mano_i_dedo2b.addOrReplaceChild("mano_i_dedo2b_c1", CubeListBuilder.create().texOffs(21, 167).addBox(-0.75F, -0.75F, -1.35F, 1.5F, 1.5F, 1.5F),
                PartPose.offsetAndRotation(0F, 0.1F, -3.75F, 0.45F, 0F, 0F));
        p_mano_i_dedo2b.addOrReplaceChild("mano_i_dedo2b_c2", CubeListBuilder.create().texOffs(28, 167).addBox(-0.525F, -0.525F, -1.35F, 1.05F, 1.05F, 1.5F),
                PartPose.offsetAndRotation(0F, 0.622F, -4.8305F, 0.85F, 0F, 0F));
        p_mano_i_dedo2b.addOrReplaceChild("mano_i_dedo2b_c3", CubeListBuilder.create().texOffs(65, 167).addBox(-0.3F, -0.3F, -1.35F, 0.6F, 0.6F, 1.5F),
                PartPose.offsetAndRotation(0F, 1.5235F, -5.6225F, 1.25F, 0F, 0F));
        PartDefinition p_mano_i_dedo3 = p_mano_i.addOrReplaceChild("mano_i_dedo3", CubeListBuilder.create(),
                PartPose.offsetAndRotation(3.1954F, 1.7142F, -4.8271F, 0.8842F, -0.2164F, -0.0677F));
        p_mano_i_dedo3.addOrReplaceChild("mano_i_dedo3_c0", CubeListBuilder.create().texOffs(99, 152).addBox(-1F, -1F, -4F, 2F, 2F, 4.3F),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        PartDefinition p_mano_i_dedo3b = p_mano_i_dedo3.addOrReplaceChild("mano_i_dedo3b", CubeListBuilder.create(),
                PartPose.offsetAndRotation(0F, 0F, -4F, 0.72F, 0F, 0F));
        p_mano_i_dedo3b.addOrReplaceChild("mano_i_dedo3b_c0", CubeListBuilder.create().texOffs(40, 161).addBox(-0.85F, -0.85F, -3F, 1.7F, 1.7F, 3.3F),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        p_mano_i_dedo3b.addOrReplaceChild("mano_i_dedo3b_c1", CubeListBuilder.create().texOffs(21, 167).addBox(-0.75F, -0.75F, -1.35F, 1.5F, 1.5F, 1.5F),
                PartPose.offsetAndRotation(0F, 0.1F, -3F, 0.45F, 0F, 0F));
        p_mano_i_dedo3b.addOrReplaceChild("mano_i_dedo3b_c2", CubeListBuilder.create().texOffs(28, 167).addBox(-0.525F, -0.525F, -1.35F, 1.05F, 1.05F, 1.5F),
                PartPose.offsetAndRotation(0F, 0.622F, -4.0805F, 0.85F, 0F, 0F));
        p_mano_i_dedo3b.addOrReplaceChild("mano_i_dedo3b_c3", CubeListBuilder.create().texOffs(65, 167).addBox(-0.3F, -0.3F, -1.35F, 0.6F, 0.6F, 1.5F),
                PartPose.offsetAndRotation(0F, 1.5235F, -4.8725F, 1.25F, 0F, 0F));
        PartDefinition p_brazo_d = p_tronco.addOrReplaceChild("brazo_d", CubeListBuilder.create(),
                PartPose.offsetAndRotation(-14.8F, -13.6F, -3F, -0.38F, 0F, 0F));
        p_brazo_d.addOrReplaceChild("brazo_d_c0", CubeListBuilder.create().texOffs(63, 61).addBox(-2.9F, -2.9F, -14.5271F, 5.8F, 5.8F, 16.2671F),
                PartPose.offsetAndRotation(0F, 0F, 0F, -2.1758F, 1.1711F, 3.1416F));
        PartDefinition p_antebrazo_d = p_brazo_d.addOrReplaceChild("antebrazo_d", CubeListBuilder.create(),
                PartPose.offsetAndRotation(-6.7F, 10.5171F, 2.8305F, 0F, 0F, 0F));
        p_antebrazo_d.addOrReplaceChild("antebrazo_d_c0", CubeListBuilder.create().texOffs(191, 34).addBox(-2.7F, -2.7F, -17.6624F, 5.4F, 5.4F, 19.2824F),
                PartPose.offsetAndRotation(0F, 0F, 0F, 1.1143F, -0.1419F, 0F));
        PartDefinition p_mano_d = p_antebrazo_d.addOrReplaceChild("mano_d", CubeListBuilder.create(),
                PartPose.offsetAndRotation(1F, 14.4F, -7F, 0F, 0F, 0F));
        p_mano_d.addOrReplaceChild("mano_d_c0", CubeListBuilder.create().texOffs(83, 139).addBox(-3.6F, -1.5F, -5.8F, 7.2F, 3F, 6.4F),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0.3373F, 0.0917F, 0.023F));
        p_mano_d.addOrReplaceChild("mano_d_c1", CubeListBuilder.create().texOffs(150, 152).addBox(-3F, -2F, -5.2F, 6F, 0.8F, 4.6F),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0.3373F, 0.0917F, 0.023F));
        PartDefinition p_mano_d_dedo0 = p_mano_d.addOrReplaceChild("mano_d_dedo0", CubeListBuilder.create(),
                PartPose.offsetAndRotation(-3.1954F, 1.7142F, -4.8271F, 0.8842F, 0.2164F, 0.0677F));
        p_mano_d_dedo0.addOrReplaceChild("mano_d_dedo0_c0", CubeListBuilder.create().texOffs(84, 152).addBox(-1F, -1F, -4.4F, 2F, 2F, 4.7F),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        PartDefinition p_mano_d_dedo0b = p_mano_d_dedo0.addOrReplaceChild("mano_d_dedo0b", CubeListBuilder.create(),
                PartPose.offsetAndRotation(0F, 0F, -4.4F, 0.72F, 0F, 0F));
        p_mano_d_dedo0b.addOrReplaceChild("mano_d_dedo0b_c0", CubeListBuilder.create().texOffs(211, 152).addBox(-0.85F, -0.85F, -3.3F, 1.7F, 1.7F, 3.6F),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        p_mano_d_dedo0b.addOrReplaceChild("mano_d_dedo0b_c1", CubeListBuilder.create().texOffs(21, 167).addBox(-0.75F, -0.75F, -1.35F, 1.5F, 1.5F, 1.5F),
                PartPose.offsetAndRotation(0F, 0.1F, -3.3F, 0.45F, 0F, 0F));
        p_mano_d_dedo0b.addOrReplaceChild("mano_d_dedo0b_c2", CubeListBuilder.create().texOffs(28, 167).addBox(-0.525F, -0.525F, -1.35F, 1.05F, 1.05F, 1.5F),
                PartPose.offsetAndRotation(0F, 0.622F, -4.3805F, 0.85F, 0F, 0F));
        p_mano_d_dedo0b.addOrReplaceChild("mano_d_dedo0b_c3", CubeListBuilder.create().texOffs(65, 167).addBox(-0.3F, -0.3F, -1.35F, 0.6F, 0.6F, 1.5F),
                PartPose.offsetAndRotation(0F, 1.5235F, -5.1725F, 1.25F, 0F, 0F));
        PartDefinition p_mano_d_dedo1 = p_mano_d.addOrReplaceChild("mano_d_dedo1", CubeListBuilder.create(),
                PartPose.offsetAndRotation(-1.4034F, 1.7554F, -4.9919F, 0.879F, 0.1333F, 0.0377F));
        p_mano_d_dedo1.addOrReplaceChild("mano_d_dedo1_c0", CubeListBuilder.create().texOffs(29, 152).addBox(-1F, -1F, -5.2F, 2F, 2F, 5.5F),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        PartDefinition p_mano_d_dedo1b = p_mano_d_dedo1.addOrReplaceChild("mano_d_dedo1b", CubeListBuilder.create(),
                PartPose.offsetAndRotation(0F, 0F, -5.2F, 0.72F, 0F, 0F));
        p_mano_d_dedo1b.addOrReplaceChild("mano_d_dedo1b_c0", CubeListBuilder.create().texOffs(173, 152).addBox(-0.85F, -0.85F, -3.9F, 1.7F, 1.7F, 4.2F),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        p_mano_d_dedo1b.addOrReplaceChild("mano_d_dedo1b_c1", CubeListBuilder.create().texOffs(21, 167).addBox(-0.75F, -0.75F, -1.35F, 1.5F, 1.5F, 1.5F),
                PartPose.offsetAndRotation(0F, 0.1F, -3.9F, 0.45F, 0F, 0F));
        p_mano_d_dedo1b.addOrReplaceChild("mano_d_dedo1b_c2", CubeListBuilder.create().texOffs(28, 167).addBox(-0.525F, -0.525F, -1.35F, 1.05F, 1.05F, 1.5F),
                PartPose.offsetAndRotation(0F, 0.622F, -4.9805F, 0.85F, 0F, 0F));
        p_mano_d_dedo1b.addOrReplaceChild("mano_d_dedo1b_c3", CubeListBuilder.create().texOffs(65, 167).addBox(-0.3F, -0.3F, -1.35F, 0.6F, 0.6F, 1.5F),
                PartPose.offsetAndRotation(0F, 1.5235F, -5.7725F, 1.25F, 0F, 0F));
        PartDefinition p_mano_d_dedo2 = p_mano_d.addOrReplaceChild("mano_d_dedo2", CubeListBuilder.create(),
                PartPose.offsetAndRotation(0.3886F, 1.7966F, -5.1567F, 0.8763F, 0.05F, 0.0084F));
        p_mano_d_dedo2.addOrReplaceChild("mano_d_dedo2_c0", CubeListBuilder.create().texOffs(45, 152).addBox(-1F, -1F, -5F, 2F, 2F, 5.3F),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        PartDefinition p_mano_d_dedo2b = p_mano_d_dedo2.addOrReplaceChild("mano_d_dedo2b", CubeListBuilder.create(),
                PartPose.offsetAndRotation(0F, 0F, -5F, 0.72F, 0F, 0F));
        p_mano_d_dedo2b.addOrReplaceChild("mano_d_dedo2b_c0", CubeListBuilder.create().texOffs(186, 152).addBox(-0.85F, -0.85F, -3.75F, 1.7F, 1.7F, 4.05F),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        p_mano_d_dedo2b.addOrReplaceChild("mano_d_dedo2b_c1", CubeListBuilder.create().texOffs(21, 167).addBox(-0.75F, -0.75F, -1.35F, 1.5F, 1.5F, 1.5F),
                PartPose.offsetAndRotation(0F, 0.1F, -3.75F, 0.45F, 0F, 0F));
        p_mano_d_dedo2b.addOrReplaceChild("mano_d_dedo2b_c2", CubeListBuilder.create().texOffs(28, 167).addBox(-0.525F, -0.525F, -1.35F, 1.05F, 1.05F, 1.5F),
                PartPose.offsetAndRotation(0F, 0.622F, -4.8305F, 0.85F, 0F, 0F));
        p_mano_d_dedo2b.addOrReplaceChild("mano_d_dedo2b_c3", CubeListBuilder.create().texOffs(65, 167).addBox(-0.3F, -0.3F, -1.35F, 0.6F, 0.6F, 1.5F),
                PartPose.offsetAndRotation(0F, 1.5235F, -5.6225F, 1.25F, 0F, 0F));
        PartDefinition p_mano_d_dedo3 = p_mano_d.addOrReplaceChild("mano_d_dedo3", CubeListBuilder.create(),
                PartPose.offsetAndRotation(2.1805F, 1.8378F, -5.3215F, 0.876F, -0.0332F, -0.0207F));
        p_mano_d_dedo3.addOrReplaceChild("mano_d_dedo3_c0", CubeListBuilder.create().texOffs(99, 152).addBox(-1F, -1F, -4F, 2F, 2F, 4.3F),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        PartDefinition p_mano_d_dedo3b = p_mano_d_dedo3.addOrReplaceChild("mano_d_dedo3b", CubeListBuilder.create(),
                PartPose.offsetAndRotation(0F, 0F, -4F, 0.72F, 0F, 0F));
        p_mano_d_dedo3b.addOrReplaceChild("mano_d_dedo3b_c0", CubeListBuilder.create().texOffs(40, 161).addBox(-0.85F, -0.85F, -3F, 1.7F, 1.7F, 3.3F),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        p_mano_d_dedo3b.addOrReplaceChild("mano_d_dedo3b_c1", CubeListBuilder.create().texOffs(21, 167).addBox(-0.75F, -0.75F, -1.35F, 1.5F, 1.5F, 1.5F),
                PartPose.offsetAndRotation(0F, 0.1F, -3F, 0.45F, 0F, 0F));
        p_mano_d_dedo3b.addOrReplaceChild("mano_d_dedo3b_c2", CubeListBuilder.create().texOffs(28, 167).addBox(-0.525F, -0.525F, -1.35F, 1.05F, 1.05F, 1.5F),
                PartPose.offsetAndRotation(0F, 0.622F, -4.0805F, 0.85F, 0F, 0F));
        p_mano_d_dedo3b.addOrReplaceChild("mano_d_dedo3b_c3", CubeListBuilder.create().texOffs(65, 167).addBox(-0.3F, -0.3F, -1.35F, 0.6F, 0.6F, 1.5F),
                PartPose.offsetAndRotation(0F, 1.5235F, -4.8725F, 1.25F, 0F, 0F));
        return LayerDefinition.create(malla, 256, 256);
    }
}
