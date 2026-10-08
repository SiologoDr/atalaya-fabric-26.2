package com.atalaya.client;

import net.minecraft.client.model.geom.PartPose;
import net.minecraft.client.model.geom.builders.CubeDeformation;
import net.minecraft.client.model.geom.builders.CubeListBuilder;
import net.minecraft.client.model.geom.builders.LayerDefinition;
import net.minecraft.client.model.geom.builders.MeshDefinition;
import net.minecraft.client.model.geom.builders.PartDefinition;

/**
 * La malla de Novilis, el Caballero Solar. GENERADO por
 * materiales/generadores/novilis_juego.py (y novilis_juego_anim.py): no se edita
 * a mano. Cambiar una caja aqui sin cambiar el script descuadra la textura,
 * que se pinta con la misma cuadricula.
 */
public final class NovilisMalla {

    private NovilisMalla() {
    }

    public static LayerDefinition crear() {
        CubeDeformation infla = CubeDeformation.NONE;
        MeshDefinition malla = new MeshDefinition();
        PartDefinition p_root = malla.getRoot();
        PartDefinition p_raiz = p_root.addOrReplaceChild("raiz", CubeListBuilder.create(),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        PartDefinition p_pelvis = p_raiz.addOrReplaceChild("pelvis", CubeListBuilder.create()
                .texOffs(0, 127).addBox(-15F, -6F, -10F, 30F, 8F, 20F, infla)
                .texOffs(0, 156).addBox(-16F, -2.5F, -11F, 32F, 3.5F, 22F, infla)
                .texOffs(33, 349).addBox(-13F, -2F, -11.6F, 2F, 2F, 0.8F, infla)
                .texOffs(33, 349).addBox(-8F, -2F, -11.6F, 2F, 2F, 0.8F, infla)
                .texOffs(33, 349).addBox(6F, -2F, -11.6F, 2F, 2F, 0.8F, infla)
                .texOffs(33, 349).addBox(11F, -2F, -11.6F, 2F, 2F, 0.8F, infla)
                .texOffs(252, 316).addBox(-4.5F, -5F, -12.2F, 9F, 9F, 1.6F, infla)
                .texOffs(218, 341).addBox(-2.5F, -3F, -13F, 5F, 5F, 1F, infla),
                PartPose.offsetAndRotation(0F, -39.5F, 0F, 0F, 0F, 0F));
        p_pelvis.addOrReplaceChild("falda_izq", CubeListBuilder.create()
                .texOffs(432, 316).addBox(-7F, 0F, 0F, 14F, 7F, 2.4F, infla)
                .texOffs(359, 316).addBox(-7.5F, 6F, -0.4F, 15F, 7F, 2.6F, infla)
                .texOffs(152, 330).addBox(-8F, 12F, -0.8F, 16F, 6F, 2.8F, infla)
                .texOffs(226, 349).addBox(-7.3F, 6F, -0.7F, 14.6F, 0.8F, 0.6F, infla)
                .texOffs(192, 349).addBox(-7.8F, 12F, -1.1F, 15.6F, 0.8F, 0.6F, infla)
                .texOffs(298, 341).addBox(-8.3F, 17.6F, -1F, 16.6F, 1.2F, 3F, infla),
                PartPose.offsetAndRotation(9.5F, 1F, -10.4F, -0.1047F, 0F, 0.1745F));
        p_pelvis.addOrReplaceChild("falda_der", CubeListBuilder.create()
                .texOffs(432, 316).addBox(-7F, 0F, 0F, 14F, 7F, 2.4F, infla)
                .texOffs(359, 316).addBox(-7.5F, 6F, -0.4F, 15F, 7F, 2.6F, infla)
                .texOffs(152, 330).addBox(-8F, 12F, -0.8F, 16F, 6F, 2.8F, infla)
                .texOffs(226, 349).addBox(-7.3F, 6F, -0.7F, 14.6F, 0.8F, 0.6F, infla)
                .texOffs(192, 349).addBox(-7.8F, 12F, -1.1F, 15.6F, 0.8F, 0.6F, infla)
                .texOffs(298, 341).addBox(-8.3F, 17.6F, -1F, 16.6F, 1.2F, 3F, infla),
                PartPose.offsetAndRotation(-9.5F, 1F, -10.4F, -0.1047F, 0F, -0.1745F));
        p_pelvis.addOrReplaceChild("falda_lizq", CubeListBuilder.create()
                .texOffs(381, 0).addBox(-1.2F, 0F, -10F, 2.4F, 16F, 20F, infla)
                .texOffs(221, 235).addBox(-1.5F, 15.4F, -10.3F, 3F, 1.2F, 20.6F, infla),
                PartPose.offsetAndRotation(16F, 1F, 0F, 0F, 0F, 0.2094F));
        p_pelvis.addOrReplaceChild("falda_lder", CubeListBuilder.create()
                .texOffs(381, 0).addBox(-1.2F, 0F, -10F, 2.4F, 16F, 20F, infla)
                .texOffs(221, 235).addBox(-1.5F, 15.4F, -10.3F, 3F, 1.2F, 20.6F, infla),
                PartPose.offsetAndRotation(-16F, 1F, 0F, 0F, 0F, -0.2094F));
        p_pelvis.addOrReplaceChild("tabardo", CubeListBuilder.create()
                .texOffs(88, 0).addBox(-6F, 0F, 0F, 12F, 40F, 1.2F, infla)
                .texOffs(121, 316).addBox(-6F, 40F, 0F, 12F, 10F, 1.2F, infla)
                .texOffs(29, 0).addBox(-6.4F, 0F, -0.3F, 0.8F, 48F, 1.6F, infla)
                .texOffs(29, 0).addBox(5.6F, 0F, -0.3F, 0.8F, 48F, 1.6F, infla)
                .texOffs(231, 341).addBox(-2.5F, 6F, -0.6F, 5F, 5F, 0.8F, infla)
                .texOffs(489, 341).addBox(-1.5F, 7F, -0.9F, 3F, 3F, 0.6F, infla),
                PartPose.offsetAndRotation(0F, 1F, -11.4F, -0.0698F, 0F, 0F));
        PartDefinition p_pierna_izq = p_pelvis.addOrReplaceChild("pierna_izq", CubeListBuilder.create()
                .texOffs(35, 0).addBox(-6.5F, 0F, -6.5F, 13F, 30F, 13F, infla)
                .texOffs(209, 259).addBox(-7.5F, 1F, -8F, 15F, 11F, 9F, infla)
                .texOffs(107, 259).addBox(-7.8F, 11F, -8.4F, 15.6F, 10F, 9.4F, infla)
                .texOffs(176, 316).addBox(-7.8F, 0.4F, -8.3F, 15.6F, 1.2F, 9.6F, infla)
                .texOffs(38, 316).addBox(-8.1F, 20.4F, -8.7F, 16.2F, 1.2F, 10F, infla)
                .texOffs(212, 96).addBox(5.7F, 2F, -6F, 1.6F, 18F, 12F, infla),
                PartPose.offsetAndRotation(8.5F, 2F, 0F, -0.3648F, -0.1047F, -0.0321F));
        PartDefinition p_espinilla_izq = p_pierna_izq.addOrReplaceChild("espinilla_izq", CubeListBuilder.create()
                .texOffs(0, 300).addBox(-7F, -5F, -10F, 14F, 9F, 5.5F, infla)
                .texOffs(446, 330).addBox(-7.3F, -5.4F, -10.3F, 14.6F, 1F, 6F, infla)
                .texOffs(69, 341).addBox(-3F, -3F, -10.8F, 6F, 6F, 1F, infla)
                .texOffs(498, 341).addBox(-1.5F, -1.5F, -11.4F, 3F, 3F, 0.8F, infla)
                .texOffs(338, 96).addBox(-6.5F, 0F, -7F, 13F, 15F, 14F, infla)
                .texOffs(55, 259).addBox(-6F, 15F, -6.6F, 12F, 6F, 13.2F, infla)
                .texOffs(395, 235).addBox(-7.2F, 21F, -7.6F, 14.4F, 5F, 15.2F, infla)
                .texOffs(310, 281).addBox(-7.5F, 25.2F, -7.9F, 15F, 1F, 15.8F, infla)
                .texOffs(373, 281).addBox(-1F, 3F, -7.6F, 2F, 16F, 1F, infla),
                PartPose.offsetAndRotation(0F, 30F, 0F, 0.5325F, 0F, 0F));
        p_espinilla_izq.addOrReplaceChild("aleta_rodilla_izq", CubeListBuilder.create()
                .texOffs(371, 259).addBox(-0.8F, -7F, -3F, 1.6F, 10F, 9F, infla)
                .texOffs(228, 316).addBox(-1F, -7.8F, -3.2F, 2F, 1F, 9.4F, infla),
                PartPose.offsetAndRotation(6.6F, -1F, -6F, 0F, 0F, 0.384F));
        p_espinilla_izq.addOrReplaceChild("pie_izq", CubeListBuilder.create()
                .texOffs(0, 210).addBox(-7F, -8F, -9F, 14F, 8F, 16F, infla)
                .texOffs(396, 316).addBox(-6.4F, -5F, -13F, 12.8F, 5F, 4.4F, infla)
                .texOffs(39, 341).addBox(-5.4F, -3.6F, -16F, 10.8F, 3.6F, 3.4F, infla)
                .texOffs(116, 281).addBox(-7.3F, -8.4F, -9.3F, 14.6F, 1.2F, 16.6F, infla)
                .texOffs(244, 341).addBox(-1F, -4F, 6.5F, 2F, 2F, 4F, infla),
                PartPose.offsetAndRotation(0F, 34F, 0F, -0.1677F, 0F, 0F));
        PartDefinition p_pierna_der = p_pelvis.addOrReplaceChild("pierna_der", CubeListBuilder.create()
                .texOffs(35, 0).addBox(-6.5F, 0F, -6.5F, 13F, 30F, 13F, infla)
                .texOffs(209, 259).addBox(-7.5F, 1F, -8F, 15F, 11F, 9F, infla)
                .texOffs(107, 259).addBox(-7.8F, 11F, -8.4F, 15.6F, 10F, 9.4F, infla)
                .texOffs(176, 316).addBox(-7.8F, 0.4F, -8.3F, 15.6F, 1.2F, 9.6F, infla)
                .texOffs(38, 316).addBox(-8.1F, 20.4F, -8.7F, 16.2F, 1.2F, 10F, infla)
                .texOffs(212, 96).addBox(-7.3F, 2F, -6F, 1.6F, 18F, 12F, infla),
                PartPose.offsetAndRotation(-8.5F, 2F, 0F, -0.1799F, 0.1047F, 0.0509F));
        PartDefinition p_espinilla_der = p_pierna_der.addOrReplaceChild("espinilla_der", CubeListBuilder.create()
                .texOffs(0, 300).addBox(-7F, -5F, -10F, 14F, 9F, 5.5F, infla)
                .texOffs(446, 330).addBox(-7.3F, -5.4F, -10.3F, 14.6F, 1F, 6F, infla)
                .texOffs(69, 341).addBox(-3F, -3F, -10.8F, 6F, 6F, 1F, infla)
                .texOffs(498, 341).addBox(-1.5F, -1.5F, -11.4F, 3F, 3F, 0.8F, infla)
                .texOffs(338, 96).addBox(-6.5F, 0F, -7F, 13F, 15F, 14F, infla)
                .texOffs(55, 259).addBox(-6F, 15F, -6.6F, 12F, 6F, 13.2F, infla)
                .texOffs(395, 235).addBox(-7.2F, 21F, -7.6F, 14.4F, 5F, 15.2F, infla)
                .texOffs(310, 281).addBox(-7.5F, 25.2F, -7.9F, 15F, 1F, 15.8F, infla)
                .texOffs(373, 281).addBox(-1F, 3F, -7.6F, 2F, 16F, 1F, infla),
                PartPose.offsetAndRotation(0F, 30F, 0F, 0.5218F, 0F, 0F));
        p_espinilla_der.addOrReplaceChild("aleta_rodilla_der", CubeListBuilder.create()
                .texOffs(371, 259).addBox(-0.8F, -7F, -3F, 1.6F, 10F, 9F, infla)
                .texOffs(228, 316).addBox(-1F, -7.8F, -3.2F, 2F, 1F, 9.4F, infla),
                PartPose.offsetAndRotation(-6.6F, -1F, -6F, 0F, 0F, -0.384F));
        p_espinilla_der.addOrReplaceChild("pie_der", CubeListBuilder.create()
                .texOffs(0, 210).addBox(-7F, -8F, -9F, 14F, 8F, 16F, infla)
                .texOffs(396, 316).addBox(-6.4F, -5F, -13F, 12.8F, 5F, 4.4F, infla)
                .texOffs(39, 341).addBox(-5.4F, -3.6F, -16F, 10.8F, 3.6F, 3.4F, infla)
                .texOffs(116, 281).addBox(-7.3F, -8.4F, -9.3F, 14.6F, 1.2F, 16.6F, infla)
                .texOffs(244, 341).addBox(-1F, -4F, 6.5F, 2F, 2F, 4F, infla),
                PartPose.offsetAndRotation(0F, 34F, 0F, -0.3419F, 0F, 0F));
        PartDefinition p_torso = p_pelvis.addOrReplaceChild("torso", CubeListBuilder.create()
                .texOffs(272, 61).addBox(-14F, -14F, -9.5F, 28F, 14F, 19F, infla)
                .texOffs(109, 156).addBox(-15F, -4F, -10.6F, 30F, 4F, 21.2F, infla)
                .texOffs(213, 156).addBox(-14.4F, -8F, -10.6F, 28.8F, 4F, 21.2F, infla)
                .texOffs(314, 156).addBox(-13.8F, -12F, -10.6F, 27.6F, 4F, 21.2F, infla)
                .texOffs(141, 210).addBox(-15.3F, -4.6F, -10.9F, 30.6F, 0.8F, 21.8F, infla)
                .texOffs(247, 210).addBox(-14.7F, -8.6F, -10.9F, 29.4F, 0.8F, 21.8F, infla)
                .texOffs(351, 210).addBox(-14.1F, -12.6F, -10.9F, 28.2F, 0.8F, 21.8F, infla)
                .texOffs(0, 96).addBox(-21F, -46F, -12F, 42F, 12F, 18F, infla)
                .texOffs(393, 96).addBox(-19.5F, -34F, -12.6F, 39F, 10F, 18F, infla)
                .texOffs(188, 127).addBox(-16.5F, -24F, -12F, 33F, 10F, 16.5F, infla)
                .texOffs(46, 349).addBox(-19F, -34.4F, -12.9F, 38F, 0.8F, 0.6F, infla)
                .texOffs(125, 349).addBox(-16F, -24.4F, -12.3F, 32F, 0.8F, 0.6F, infla)
                .texOffs(40, 300).addBox(-19F, -44F, -13.6F, 17F, 13F, 2F, infla)
                .texOffs(40, 300).addBox(2F, -44F, -13.6F, 17F, 13F, 2F, infla)
                .texOffs(379, 341).addBox(-19.4F, -31.4F, -14F, 17.8F, 1.4F, 2.4F, infla)
                .texOffs(379, 341).addBox(1.6F, -31.4F, -14F, 17.8F, 1.4F, 2.4F, infla)
                .texOffs(270, 235).addBox(-21.4F, -46.6F, -12.4F, 42.8F, 1.4F, 18.8F, infla)
                .texOffs(412, 61).addBox(-1.5F, -44F, -14.4F, 3F, 30F, 2F, infla)
                .texOffs(421, 341).addBox(-8F, -42F, -15.4F, 16F, 2F, 1.6F, infla)
                .texOffs(421, 341).addBox(-8F, -28F, -15.4F, 16F, 2F, 1.6F, infla)
                .texOffs(419, 300).addBox(-8F, -40F, -15.4F, 2F, 12F, 1.6F, infla)
                .texOffs(419, 300).addBox(6F, -40F, -15.4F, 2F, 12F, 1.6F, infla)
                .texOffs(349, 300).addBox(-6F, -40F, -15.8F, 12F, 12F, 1.6F, infla)
                .texOffs(116, 0).addBox(-20F, -46F, 5F, 40F, 32F, 7F, infla)
                .texOffs(262, 61).addBox(-1.5F, -46F, 11.8F, 3F, 32F, 1.5F, infla)
                .texOffs(172, 183).addBox(-11F, -51F, -10F, 22F, 6F, 19F, infla)
                .texOffs(134, 235).addBox(-11.5F, -51.8F, -10.5F, 23F, 1.4F, 20F, infla),
                PartPose.offsetAndRotation(0F, -6F, 0F, 0F, 0F, 0F));
        p_torso.addOrReplaceChild("gola_izq", CubeListBuilder.create()
                .texOffs(106, 210).addBox(-1.5F, -10F, -7F, 3F, 10F, 14F, infla)
                .texOffs(380, 281).addBox(-1.8F, -10.8F, -7.3F, 3.6F, 1.2F, 14.6F, infla),
                PartPose.offsetAndRotation(11F, -50F, -2F, 0F, 0F, 0.2793F));
        p_torso.addOrReplaceChild("gola_der", CubeListBuilder.create()
                .texOffs(106, 210).addBox(-1.5F, -10F, -7F, 3F, 10F, 14F, infla)
                .texOffs(380, 281).addBox(-1.8F, -10.8F, -7.3F, 3.6F, 1.2F, 14.6F, infla),
                PartPose.offsetAndRotation(-11F, -50F, -2F, 0F, 0F, -0.2793F));
        PartDefinition p_rayos_pecho = p_torso.addOrReplaceChild("rayos_pecho", CubeListBuilder.create(),
                PartPose.offsetAndRotation(0F, -34F, 0F, 0F, 0F, 0F));
        p_rayos_pecho.addOrReplaceChild("rayos_pecho_0", CubeListBuilder.create()
                .texOffs(269, 330).addBox(-1.2F, -15.2F, -15.6F, 2.4F, 7F, 2F, infla)
                .texOffs(9, 349).addBox(-0.72F, -16.8F, -15.3F, 1.44F, 1.8F, 1.4F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        p_rayos_pecho.addOrReplaceChild("rayos_pecho_1", CubeListBuilder.create()
                .texOffs(107, 341).addBox(-1.2F, -12.7F, -15.6F, 2.4F, 4.5F, 2F, infla)
                .texOffs(9, 349).addBox(-0.72F, -14.3F, -15.3F, 1.44F, 1.8F, 1.4F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0.7854F));
        p_rayos_pecho.addOrReplaceChild("rayos_pecho_2", CubeListBuilder.create()
                .texOffs(269, 330).addBox(-1.2F, -15.2F, -15.6F, 2.4F, 7F, 2F, infla)
                .texOffs(9, 349).addBox(-0.72F, -16.8F, -15.3F, 1.44F, 1.8F, 1.4F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 1.5708F));
        p_rayos_pecho.addOrReplaceChild("rayos_pecho_3", CubeListBuilder.create()
                .texOffs(107, 341).addBox(-1.2F, -12.7F, -15.6F, 2.4F, 4.5F, 2F, infla)
                .texOffs(9, 349).addBox(-0.72F, -14.3F, -15.3F, 1.44F, 1.8F, 1.4F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 2.3562F));
        p_rayos_pecho.addOrReplaceChild("rayos_pecho_4", CubeListBuilder.create()
                .texOffs(269, 330).addBox(-1.2F, -15.2F, -15.6F, 2.4F, 7F, 2F, infla)
                .texOffs(9, 349).addBox(-0.72F, -16.8F, -15.3F, 1.44F, 1.8F, 1.4F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 3.1416F));
        p_rayos_pecho.addOrReplaceChild("rayos_pecho_5", CubeListBuilder.create()
                .texOffs(107, 341).addBox(-1.2F, -12.7F, -15.6F, 2.4F, 4.5F, 2F, infla)
                .texOffs(9, 349).addBox(-0.72F, -14.3F, -15.3F, 1.44F, 1.8F, 1.4F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 3.927F));
        p_rayos_pecho.addOrReplaceChild("rayos_pecho_6", CubeListBuilder.create()
                .texOffs(269, 330).addBox(-1.2F, -15.2F, -15.6F, 2.4F, 7F, 2F, infla)
                .texOffs(9, 349).addBox(-0.72F, -16.8F, -15.3F, 1.44F, 1.8F, 1.4F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 4.7124F));
        p_rayos_pecho.addOrReplaceChild("rayos_pecho_7", CubeListBuilder.create()
                .texOffs(107, 341).addBox(-1.2F, -12.7F, -15.6F, 2.4F, 4.5F, 2F, infla)
                .texOffs(9, 349).addBox(-0.72F, -14.3F, -15.3F, 1.44F, 1.8F, 1.4F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 5.4978F));
        PartDefinition p_capa_1 = p_torso.addOrReplaceChild("capa_1", CubeListBuilder.create()
                .texOffs(335, 330).addBox(-26F, -2F, -1F, 52F, 4F, 3F, infla)
                .texOffs(108, 61).addBox(-24F, 0F, 0F, 48F, 32F, 1.5F, infla)
                .texOffs(427, 0).addBox(-24.6F, 0F, -0.3F, 1.2F, 32F, 2.1F, infla)
                .texOffs(427, 0).addBox(23.4F, 0F, -0.3F, 1.2F, 32F, 2.1F, infla)
                .texOffs(79, 300).addBox(-7F, 8F, 1.5F, 14F, 14F, 0.8F, infla)
                .texOffs(0, 330).addBox(-4.5F, 10.5F, 2F, 9F, 9F, 0.8F, infla)
                .texOffs(40, 349).addBox(9.2F, 14.2F, 1.6F, 1.6F, 1.6F, 0.6F, infla)
                .texOffs(40, 349).addBox(6.2711F, 21.2711F, 1.6F, 1.6F, 1.6F, 0.6F, infla)
                .texOffs(40, 349).addBox(-0.8F, 24.2F, 1.6F, 1.6F, 1.6F, 0.6F, infla)
                .texOffs(40, 349).addBox(-7.8711F, 21.2711F, 1.6F, 1.6F, 1.6F, 0.6F, infla)
                .texOffs(40, 349).addBox(-10.8F, 14.2F, 1.6F, 1.6F, 1.6F, 0.6F, infla)
                .texOffs(40, 349).addBox(-7.8711F, 7.1289F, 1.6F, 1.6F, 1.6F, 0.6F, infla)
                .texOffs(40, 349).addBox(-0.8F, 4.2F, 1.6F, 1.6F, 1.6F, 0.6F, infla)
                .texOffs(40, 349).addBox(6.2711F, 7.1289F, 1.6F, 1.6F, 1.6F, 0.6F, infla),
                PartPose.offsetAndRotation(0F, -44F, 11F, 0.1222F, 0F, 0F));
        PartDefinition p_capa_2 = p_capa_1.addOrReplaceChild("capa_2", CubeListBuilder.create()
                .texOffs(0, 61).addBox(-26F, 0F, 0F, 52F, 32F, 1.5F, infla)
                .texOffs(427, 0).addBox(-26.6F, 0F, -0.3F, 1.2F, 32F, 2.1F, infla)
                .texOffs(427, 0).addBox(25.4F, 0F, -0.3F, 1.2F, 32F, 2.1F, infla),
                PartPose.offsetAndRotation(0F, 32F, 0F, 0.0698F, 0F, 0F));
        p_capa_2.addOrReplaceChild("capa_3", CubeListBuilder.create()
                .texOffs(0, 281).addBox(-28F, 0F, 0F, 56F, 16F, 1.5F, infla)
                .texOffs(140, 300).addBox(-28F, 16F, 0F, 56F, 12F, 1.5F, infla)
                .texOffs(394, 259).addBox(-28.6F, 0F, -0.3F, 1.2F, 16F, 2.1F, infla)
                .texOffs(394, 259).addBox(27.4F, 0F, -0.3F, 1.2F, 16F, 2.1F, infla)
                .texOffs(257, 341).addBox(-26F, 26F, 0F, 3.8F, 4F, 1.5F, infla)
                .texOffs(21, 316).addBox(-20.4F, 26F, 0F, 3.8F, 11F, 1.5F, infla)
                .texOffs(164, 316).addBox(-14.8F, 26F, 0F, 3.8F, 10F, 1.5F, infla)
                .texOffs(330, 316).addBox(-9.2F, 26F, 0F, 3.8F, 9F, 1.5F, infla)
                .texOffs(66, 330).addBox(-3.6F, 26F, 0F, 3.8F, 8F, 1.5F, infla)
                .texOffs(257, 330).addBox(2F, 26F, 0F, 3.8F, 7F, 1.5F, infla)
                .texOffs(303, 330).addBox(7.6F, 26F, 0F, 3.8F, 6F, 1.5F, infla)
                .texOffs(84, 341).addBox(13.2F, 26F, 0F, 3.8F, 5F, 1.5F, infla)
                .texOffs(257, 341).addBox(18.8F, 26F, 0F, 3.8F, 4F, 1.5F, infla)
                .texOffs(21, 316).addBox(24.4F, 26F, 0F, 3.8F, 11F, 1.5F, infla),
                PartPose.offsetAndRotation(0F, 32F, 0F, 0.0873F, 0F, 0F));
        PartDefinition p_cuello = p_torso.addOrReplaceChild("cuello", CubeListBuilder.create()
                .texOffs(308, 300).addBox(-5F, -4F, -5F, 10F, 4F, 10F, infla),
                PartPose.offsetAndRotation(0F, -50F, -1F, 0F, 0F, 0F));
        PartDefinition p_cabeza = p_cuello.addOrReplaceChild("cabeza", CubeListBuilder.create()
                .texOffs(211, 0).addBox(-9.5F, -20F, -9.5F, 19F, 20F, 19F, infla)
                .texOffs(135, 341).addBox(-10F, -15F, -10.3F, 20F, 2.8F, 2.6F, infla)
                .texOffs(458, 341).addBox(-7F, -11.8F, -10.25F, 14F, 2.4F, 0.8F, infla)
                .texOffs(351, 316).addBox(-1.2F, -11.8F, -10.3F, 2.4F, 9.2F, 0.9F, infla)
                .texOffs(304, 259).addBox(-10.4F, -11.5F, -9.6F, 3.4F, 11.5F, 8F, infla)
                .texOffs(304, 259).addBox(7F, -11.5F, -9.6F, 3.4F, 11.5F, 8F, infla)
                .texOffs(33, 316).addBox(-10.6F, -11.5F, -10F, 1F, 11.5F, 1F, infla)
                .texOffs(33, 316).addBox(9.6F, -11.5F, -10F, 1F, 11.5F, 1F, infla)
                .texOffs(0, 341).addBox(-7.6F, -3F, -10.8F, 15.2F, 3.6F, 3.4F, infla)
                .texOffs(498, 341).addBox(-1.5F, -19.4F, -10.1F, 3F, 3F, 0.8F, infla)
                .texOffs(149, 316).addBox(-10.2F, -10F, -2F, 1F, 6F, 6F, infla)
                .texOffs(149, 316).addBox(9.2F, -10F, -2F, 1F, 6F, 6F, infla)
                .texOffs(61, 210).addBox(-1.3F, -23.5F, -9F, 2.6F, 4.8F, 19F, infla)
                .texOffs(311, 183).addBox(-10.2F, -22F, -10.2F, 20.4F, 2.8F, 20.4F, infla)
                .texOffs(117, 341).addBox(-8.8F, -27F, -10.4F, 2F, 5F, 2F, infla)
                .texOffs(279, 330).addBox(-6.2F, -29F, -10.4F, 2F, 7F, 2F, infla)
                .texOffs(342, 316).addBox(-3.6F, -31F, -10.4F, 2F, 9F, 2F, infla)
                .texOffs(428, 300).addBox(-1F, -34F, -10.4F, 2F, 12F, 2F, infla)
                .texOffs(342, 316).addBox(1.6F, -31F, -10.4F, 2F, 9F, 2F, infla)
                .texOffs(279, 330).addBox(4.2F, -29F, -10.4F, 2F, 7F, 2F, infla)
                .texOffs(117, 341).addBox(6.8F, -27F, -10.4F, 2F, 5F, 2F, infla)
                .texOffs(369, 341).addBox(-1.5F, -31F, -10.9F, 3F, 3F, 1.2F, infla),
                PartPose.offsetAndRotation(0F, -4F, 0F, 0F, 0F, 0F));
        PartDefinition p_cuerno_izq = p_cabeza.addOrReplaceChild("cuerno_izq", CubeListBuilder.create()
                .texOffs(378, 300).addBox(-3F, -8F, -3F, 6F, 8F, 6F, infla),
                PartPose.offsetAndRotation(9F, -14F, 1F, 0.1396F, 0F, 1.3614F));
        PartDefinition p_cuerno2_izq = p_cuerno_izq.addOrReplaceChild("cuerno2_izq", CubeListBuilder.create()
                .texOffs(0, 316).addBox(-2.4F, -8F, -2.4F, 4.8F, 8F, 4.8F, infla),
                PartPose.offsetAndRotation(0F, -8F, 0F, 0.3142F, 0F, -0.6632F));
        PartDefinition p_cuerno3_izq = p_cuerno2_izq.addOrReplaceChild("cuerno3_izq", CubeListBuilder.create()
                .texOffs(315, 316).addBox(-1.7F, -7F, -1.7F, 3.4F, 7F, 3.4F, infla),
                PartPose.offsetAndRotation(0F, -8F, 0F, 0.3491F, 0F, -0.5934F));
        p_cuerno3_izq.addOrReplaceChild("cuerno4_izq", CubeListBuilder.create()
                .texOffs(326, 330).addBox(-1F, -6F, -1F, 2F, 6F, 2F, infla),
                PartPose.offsetAndRotation(0F, -7F, 0F, 0.2793F, 0F, -0.3142F));
        PartDefinition p_cuerno_der = p_cabeza.addOrReplaceChild("cuerno_der", CubeListBuilder.create()
                .texOffs(378, 300).addBox(-3F, -8F, -3F, 6F, 8F, 6F, infla),
                PartPose.offsetAndRotation(-9F, -14F, 1F, 0.1396F, 0F, -1.3614F));
        PartDefinition p_cuerno2_der = p_cuerno_der.addOrReplaceChild("cuerno2_der", CubeListBuilder.create()
                .texOffs(0, 316).addBox(-2.4F, -8F, -2.4F, 4.8F, 8F, 4.8F, infla),
                PartPose.offsetAndRotation(0F, -8F, 0F, 0.3142F, 0F, 0.6632F));
        PartDefinition p_cuerno3_der = p_cuerno2_der.addOrReplaceChild("cuerno3_der", CubeListBuilder.create()
                .texOffs(315, 316).addBox(-1.7F, -7F, -1.7F, 3.4F, 7F, 3.4F, infla),
                PartPose.offsetAndRotation(0F, -8F, 0F, 0.3491F, 0F, 0.5934F));
        p_cuerno3_der.addOrReplaceChild("cuerno4_der", CubeListBuilder.create()
                .texOffs(326, 330).addBox(-1F, -6F, -1F, 2F, 6F, 2F, infla),
                PartPose.offsetAndRotation(0F, -7F, 0F, 0.2793F, 0F, 0.3142F));
        PartDefinition p_halo = p_cabeza.addOrReplaceChild("halo", CubeListBuilder.create()
                .texOffs(191, 330).addBox(-4F, -4F, -0.5F, 8F, 8F, 1F, infla),
                PartPose.offsetAndRotation(0F, -16F, 13.5F, 0F, 0F, 0F));
        p_halo.addOrReplaceChild("halo_aro_0", CubeListBuilder.create()
                .texOffs(182, 341).addBox(-3.6F, -26.6F, -1F, 7.2F, 3.2F, 2F, infla)
                .texOffs(16, 349).addBox(-3.4F, -23.4F, -0.6F, 6.8F, 1.2F, 1.2F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        p_halo.addOrReplaceChild("halo_aro_1", CubeListBuilder.create()
                .texOffs(182, 341).addBox(-3.6F, -26.6F, -1F, 7.2F, 3.2F, 2F, infla)
                .texOffs(16, 349).addBox(-3.4F, -23.4F, -0.6F, 6.8F, 1.2F, 1.2F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0.2618F));
        p_halo.addOrReplaceChild("halo_aro_2", CubeListBuilder.create()
                .texOffs(182, 341).addBox(-3.6F, -26.6F, -1F, 7.2F, 3.2F, 2F, infla)
                .texOffs(16, 349).addBox(-3.4F, -23.4F, -0.6F, 6.8F, 1.2F, 1.2F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0.5236F));
        p_halo.addOrReplaceChild("halo_aro_3", CubeListBuilder.create()
                .texOffs(182, 341).addBox(-3.6F, -26.6F, -1F, 7.2F, 3.2F, 2F, infla)
                .texOffs(16, 349).addBox(-3.4F, -23.4F, -0.6F, 6.8F, 1.2F, 1.2F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0.7854F));
        p_halo.addOrReplaceChild("halo_aro_4", CubeListBuilder.create()
                .texOffs(182, 341).addBox(-3.6F, -26.6F, -1F, 7.2F, 3.2F, 2F, infla)
                .texOffs(16, 349).addBox(-3.4F, -23.4F, -0.6F, 6.8F, 1.2F, 1.2F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 1.0472F));
        p_halo.addOrReplaceChild("halo_aro_5", CubeListBuilder.create()
                .texOffs(182, 341).addBox(-3.6F, -26.6F, -1F, 7.2F, 3.2F, 2F, infla)
                .texOffs(16, 349).addBox(-3.4F, -23.4F, -0.6F, 6.8F, 1.2F, 1.2F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 1.309F));
        p_halo.addOrReplaceChild("halo_aro_6", CubeListBuilder.create()
                .texOffs(182, 341).addBox(-3.6F, -26.6F, -1F, 7.2F, 3.2F, 2F, infla)
                .texOffs(16, 349).addBox(-3.4F, -23.4F, -0.6F, 6.8F, 1.2F, 1.2F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 1.5708F));
        p_halo.addOrReplaceChild("halo_aro_7", CubeListBuilder.create()
                .texOffs(182, 341).addBox(-3.6F, -26.6F, -1F, 7.2F, 3.2F, 2F, infla)
                .texOffs(16, 349).addBox(-3.4F, -23.4F, -0.6F, 6.8F, 1.2F, 1.2F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 1.8326F));
        p_halo.addOrReplaceChild("halo_aro_8", CubeListBuilder.create()
                .texOffs(182, 341).addBox(-3.6F, -26.6F, -1F, 7.2F, 3.2F, 2F, infla)
                .texOffs(16, 349).addBox(-3.4F, -23.4F, -0.6F, 6.8F, 1.2F, 1.2F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 2.0944F));
        p_halo.addOrReplaceChild("halo_aro_9", CubeListBuilder.create()
                .texOffs(182, 341).addBox(-3.6F, -26.6F, -1F, 7.2F, 3.2F, 2F, infla)
                .texOffs(16, 349).addBox(-3.4F, -23.4F, -0.6F, 6.8F, 1.2F, 1.2F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 2.3562F));
        p_halo.addOrReplaceChild("halo_aro_10", CubeListBuilder.create()
                .texOffs(182, 341).addBox(-3.6F, -26.6F, -1F, 7.2F, 3.2F, 2F, infla)
                .texOffs(16, 349).addBox(-3.4F, -23.4F, -0.6F, 6.8F, 1.2F, 1.2F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 2.618F));
        p_halo.addOrReplaceChild("halo_aro_11", CubeListBuilder.create()
                .texOffs(182, 341).addBox(-3.6F, -26.6F, -1F, 7.2F, 3.2F, 2F, infla)
                .texOffs(16, 349).addBox(-3.4F, -23.4F, -0.6F, 6.8F, 1.2F, 1.2F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 2.8798F));
        p_halo.addOrReplaceChild("halo_aro_12", CubeListBuilder.create()
                .texOffs(182, 341).addBox(-3.6F, -26.6F, -1F, 7.2F, 3.2F, 2F, infla)
                .texOffs(16, 349).addBox(-3.4F, -23.4F, -0.6F, 6.8F, 1.2F, 1.2F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 3.1416F));
        p_halo.addOrReplaceChild("halo_aro_13", CubeListBuilder.create()
                .texOffs(182, 341).addBox(-3.6F, -26.6F, -1F, 7.2F, 3.2F, 2F, infla)
                .texOffs(16, 349).addBox(-3.4F, -23.4F, -0.6F, 6.8F, 1.2F, 1.2F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 3.4034F));
        p_halo.addOrReplaceChild("halo_aro_14", CubeListBuilder.create()
                .texOffs(182, 341).addBox(-3.6F, -26.6F, -1F, 7.2F, 3.2F, 2F, infla)
                .texOffs(16, 349).addBox(-3.4F, -23.4F, -0.6F, 6.8F, 1.2F, 1.2F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 3.6652F));
        p_halo.addOrReplaceChild("halo_aro_15", CubeListBuilder.create()
                .texOffs(182, 341).addBox(-3.6F, -26.6F, -1F, 7.2F, 3.2F, 2F, infla)
                .texOffs(16, 349).addBox(-3.4F, -23.4F, -0.6F, 6.8F, 1.2F, 1.2F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 3.927F));
        p_halo.addOrReplaceChild("halo_aro_16", CubeListBuilder.create()
                .texOffs(182, 341).addBox(-3.6F, -26.6F, -1F, 7.2F, 3.2F, 2F, infla)
                .texOffs(16, 349).addBox(-3.4F, -23.4F, -0.6F, 6.8F, 1.2F, 1.2F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 4.1888F));
        p_halo.addOrReplaceChild("halo_aro_17", CubeListBuilder.create()
                .texOffs(182, 341).addBox(-3.6F, -26.6F, -1F, 7.2F, 3.2F, 2F, infla)
                .texOffs(16, 349).addBox(-3.4F, -23.4F, -0.6F, 6.8F, 1.2F, 1.2F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 4.4506F));
        p_halo.addOrReplaceChild("halo_aro_18", CubeListBuilder.create()
                .texOffs(182, 341).addBox(-3.6F, -26.6F, -1F, 7.2F, 3.2F, 2F, infla)
                .texOffs(16, 349).addBox(-3.4F, -23.4F, -0.6F, 6.8F, 1.2F, 1.2F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 4.7124F));
        p_halo.addOrReplaceChild("halo_aro_19", CubeListBuilder.create()
                .texOffs(182, 341).addBox(-3.6F, -26.6F, -1F, 7.2F, 3.2F, 2F, infla)
                .texOffs(16, 349).addBox(-3.4F, -23.4F, -0.6F, 6.8F, 1.2F, 1.2F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 4.9742F));
        p_halo.addOrReplaceChild("halo_aro_20", CubeListBuilder.create()
                .texOffs(182, 341).addBox(-3.6F, -26.6F, -1F, 7.2F, 3.2F, 2F, infla)
                .texOffs(16, 349).addBox(-3.4F, -23.4F, -0.6F, 6.8F, 1.2F, 1.2F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 5.236F));
        p_halo.addOrReplaceChild("halo_aro_21", CubeListBuilder.create()
                .texOffs(182, 341).addBox(-3.6F, -26.6F, -1F, 7.2F, 3.2F, 2F, infla)
                .texOffs(16, 349).addBox(-3.4F, -23.4F, -0.6F, 6.8F, 1.2F, 1.2F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 5.4978F));
        p_halo.addOrReplaceChild("halo_aro_22", CubeListBuilder.create()
                .texOffs(182, 341).addBox(-3.6F, -26.6F, -1F, 7.2F, 3.2F, 2F, infla)
                .texOffs(16, 349).addBox(-3.4F, -23.4F, -0.6F, 6.8F, 1.2F, 1.2F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 5.7596F));
        p_halo.addOrReplaceChild("halo_aro_23", CubeListBuilder.create()
                .texOffs(182, 341).addBox(-3.6F, -26.6F, -1F, 7.2F, 3.2F, 2F, infla)
                .texOffs(16, 349).addBox(-3.4F, -23.4F, -0.6F, 6.8F, 1.2F, 1.2F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 6.0214F));
        PartDefinition p_halo_rayo_0 = p_halo.addOrReplaceChild("halo_rayo_0", CubeListBuilder.create(),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0.2618F));
        PartDefinition p_halo_rayo_0_l = p_halo_rayo_0.addOrReplaceChild("halo_rayo_0_l", CubeListBuilder.create()
                .texOffs(403, 300).addBox(-1.8F, -9.92F, -1.8F, 3.6F, 9.92F, 3.6F, infla),
                PartPose.offsetAndRotation(0F, -26.4F, 0F, 0F, 0F, 0F));
        p_halo_rayo_0_l.addOrReplaceChild("halo_rayo_0_l_p", CubeListBuilder.create()
                .texOffs(78, 330).addBox(-1.152F, -6.72F, -1.152F, 2.304F, 6.72F, 2.304F, infla),
                PartPose.offsetAndRotation(0F, -9.92F, 0F, 0F, 0F, 0F));
        p_halo.addOrReplaceChild("halo_pua_0", CubeListBuilder.create()
                .texOffs(291, 341).addBox(-0.9F, -31F, -0.6F, 1.8F, 4.6F, 1.2F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        PartDefinition p_halo_rayo_1 = p_halo.addOrReplaceChild("halo_rayo_1", CubeListBuilder.create(),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0.7854F));
        PartDefinition p_halo_rayo_1_l = p_halo_rayo_1.addOrReplaceChild("halo_rayo_1_l", CubeListBuilder.create()
                .texOffs(21, 330).addBox(-1.8F, -5.58F, -1.8F, 3.6F, 5.58F, 3.6F, infla),
                PartPose.offsetAndRotation(0F, -26.4F, 0F, 0F, 0F, 0F));
        p_halo_rayo_1_l.addOrReplaceChild("halo_rayo_1_l_p", CubeListBuilder.create()
                .texOffs(96, 341).addBox(-1.152F, -3.78F, -1.152F, 2.304F, 3.78F, 2.304F, infla),
                PartPose.offsetAndRotation(0F, -5.58F, 0F, 0F, 0F, 0F));
        p_halo.addOrReplaceChild("halo_pua_1", CubeListBuilder.create()
                .texOffs(291, 341).addBox(-0.9F, -31F, -0.6F, 1.8F, 4.6F, 1.2F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0.5236F));
        PartDefinition p_halo_rayo_2 = p_halo.addOrReplaceChild("halo_rayo_2", CubeListBuilder.create(),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 1.309F));
        PartDefinition p_halo_rayo_2_l = p_halo_rayo_2.addOrReplaceChild("halo_rayo_2_l", CubeListBuilder.create()
                .texOffs(403, 300).addBox(-1.8F, -9.92F, -1.8F, 3.6F, 9.92F, 3.6F, infla),
                PartPose.offsetAndRotation(0F, -26.4F, 0F, 0F, 0F, 0F));
        p_halo_rayo_2_l.addOrReplaceChild("halo_rayo_2_l_p", CubeListBuilder.create()
                .texOffs(78, 330).addBox(-1.152F, -6.72F, -1.152F, 2.304F, 6.72F, 2.304F, infla),
                PartPose.offsetAndRotation(0F, -9.92F, 0F, 0F, 0F, 0F));
        p_halo.addOrReplaceChild("halo_pua_2", CubeListBuilder.create()
                .texOffs(291, 341).addBox(-0.9F, -31F, -0.6F, 1.8F, 4.6F, 1.2F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 1.0472F));
        PartDefinition p_halo_rayo_3 = p_halo.addOrReplaceChild("halo_rayo_3", CubeListBuilder.create(),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 1.8326F));
        PartDefinition p_halo_rayo_3_l = p_halo_rayo_3.addOrReplaceChild("halo_rayo_3_l", CubeListBuilder.create()
                .texOffs(21, 330).addBox(-1.8F, -5.58F, -1.8F, 3.6F, 5.58F, 3.6F, infla),
                PartPose.offsetAndRotation(0F, -26.4F, 0F, 0F, 0F, 0F));
        p_halo_rayo_3_l.addOrReplaceChild("halo_rayo_3_l_p", CubeListBuilder.create()
                .texOffs(96, 341).addBox(-1.152F, -3.78F, -1.152F, 2.304F, 3.78F, 2.304F, infla),
                PartPose.offsetAndRotation(0F, -5.58F, 0F, 0F, 0F, 0F));
        p_halo.addOrReplaceChild("halo_pua_3", CubeListBuilder.create()
                .texOffs(291, 341).addBox(-0.9F, -31F, -0.6F, 1.8F, 4.6F, 1.2F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 1.5708F));
        PartDefinition p_halo_rayo_4 = p_halo.addOrReplaceChild("halo_rayo_4", CubeListBuilder.create(),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 2.3562F));
        PartDefinition p_halo_rayo_4_l = p_halo_rayo_4.addOrReplaceChild("halo_rayo_4_l", CubeListBuilder.create()
                .texOffs(403, 300).addBox(-1.8F, -9.92F, -1.8F, 3.6F, 9.92F, 3.6F, infla),
                PartPose.offsetAndRotation(0F, -26.4F, 0F, 0F, 0F, 0F));
        p_halo_rayo_4_l.addOrReplaceChild("halo_rayo_4_l_p", CubeListBuilder.create()
                .texOffs(78, 330).addBox(-1.152F, -6.72F, -1.152F, 2.304F, 6.72F, 2.304F, infla),
                PartPose.offsetAndRotation(0F, -9.92F, 0F, 0F, 0F, 0F));
        p_halo.addOrReplaceChild("halo_pua_4", CubeListBuilder.create()
                .texOffs(291, 341).addBox(-0.9F, -31F, -0.6F, 1.8F, 4.6F, 1.2F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 2.0944F));
        PartDefinition p_halo_rayo_5 = p_halo.addOrReplaceChild("halo_rayo_5", CubeListBuilder.create(),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 2.8798F));
        PartDefinition p_halo_rayo_5_l = p_halo_rayo_5.addOrReplaceChild("halo_rayo_5_l", CubeListBuilder.create()
                .texOffs(21, 330).addBox(-1.8F, -5.58F, -1.8F, 3.6F, 5.58F, 3.6F, infla),
                PartPose.offsetAndRotation(0F, -26.4F, 0F, 0F, 0F, 0F));
        p_halo_rayo_5_l.addOrReplaceChild("halo_rayo_5_l_p", CubeListBuilder.create()
                .texOffs(96, 341).addBox(-1.152F, -3.78F, -1.152F, 2.304F, 3.78F, 2.304F, infla),
                PartPose.offsetAndRotation(0F, -5.58F, 0F, 0F, 0F, 0F));
        p_halo.addOrReplaceChild("halo_pua_5", CubeListBuilder.create()
                .texOffs(291, 341).addBox(-0.9F, -31F, -0.6F, 1.8F, 4.6F, 1.2F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 2.618F));
        PartDefinition p_halo_rayo_6 = p_halo.addOrReplaceChild("halo_rayo_6", CubeListBuilder.create(),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 3.4034F));
        PartDefinition p_halo_rayo_6_l = p_halo_rayo_6.addOrReplaceChild("halo_rayo_6_l", CubeListBuilder.create()
                .texOffs(403, 300).addBox(-1.8F, -9.92F, -1.8F, 3.6F, 9.92F, 3.6F, infla),
                PartPose.offsetAndRotation(0F, -26.4F, 0F, 0F, 0F, 0F));
        p_halo_rayo_6_l.addOrReplaceChild("halo_rayo_6_l_p", CubeListBuilder.create()
                .texOffs(78, 330).addBox(-1.152F, -6.72F, -1.152F, 2.304F, 6.72F, 2.304F, infla),
                PartPose.offsetAndRotation(0F, -9.92F, 0F, 0F, 0F, 0F));
        p_halo.addOrReplaceChild("halo_pua_6", CubeListBuilder.create()
                .texOffs(291, 341).addBox(-0.9F, -31F, -0.6F, 1.8F, 4.6F, 1.2F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 3.1416F));
        PartDefinition p_halo_rayo_7 = p_halo.addOrReplaceChild("halo_rayo_7", CubeListBuilder.create(),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 3.927F));
        PartDefinition p_halo_rayo_7_l = p_halo_rayo_7.addOrReplaceChild("halo_rayo_7_l", CubeListBuilder.create()
                .texOffs(21, 330).addBox(-1.8F, -5.58F, -1.8F, 3.6F, 5.58F, 3.6F, infla),
                PartPose.offsetAndRotation(0F, -26.4F, 0F, 0F, 0F, 0F));
        p_halo_rayo_7_l.addOrReplaceChild("halo_rayo_7_l_p", CubeListBuilder.create()
                .texOffs(96, 341).addBox(-1.152F, -3.78F, -1.152F, 2.304F, 3.78F, 2.304F, infla),
                PartPose.offsetAndRotation(0F, -5.58F, 0F, 0F, 0F, 0F));
        p_halo.addOrReplaceChild("halo_pua_7", CubeListBuilder.create()
                .texOffs(291, 341).addBox(-0.9F, -31F, -0.6F, 1.8F, 4.6F, 1.2F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 3.6652F));
        PartDefinition p_halo_rayo_8 = p_halo.addOrReplaceChild("halo_rayo_8", CubeListBuilder.create(),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 4.4506F));
        PartDefinition p_halo_rayo_8_l = p_halo_rayo_8.addOrReplaceChild("halo_rayo_8_l", CubeListBuilder.create()
                .texOffs(403, 300).addBox(-1.8F, -9.92F, -1.8F, 3.6F, 9.92F, 3.6F, infla),
                PartPose.offsetAndRotation(0F, -26.4F, 0F, 0F, 0F, 0F));
        p_halo_rayo_8_l.addOrReplaceChild("halo_rayo_8_l_p", CubeListBuilder.create()
                .texOffs(78, 330).addBox(-1.152F, -6.72F, -1.152F, 2.304F, 6.72F, 2.304F, infla),
                PartPose.offsetAndRotation(0F, -9.92F, 0F, 0F, 0F, 0F));
        p_halo.addOrReplaceChild("halo_pua_8", CubeListBuilder.create()
                .texOffs(291, 341).addBox(-0.9F, -31F, -0.6F, 1.8F, 4.6F, 1.2F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 4.1888F));
        PartDefinition p_halo_rayo_9 = p_halo.addOrReplaceChild("halo_rayo_9", CubeListBuilder.create(),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 4.9742F));
        PartDefinition p_halo_rayo_9_l = p_halo_rayo_9.addOrReplaceChild("halo_rayo_9_l", CubeListBuilder.create()
                .texOffs(21, 330).addBox(-1.8F, -5.58F, -1.8F, 3.6F, 5.58F, 3.6F, infla),
                PartPose.offsetAndRotation(0F, -26.4F, 0F, 0F, 0F, 0F));
        p_halo_rayo_9_l.addOrReplaceChild("halo_rayo_9_l_p", CubeListBuilder.create()
                .texOffs(96, 341).addBox(-1.152F, -3.78F, -1.152F, 2.304F, 3.78F, 2.304F, infla),
                PartPose.offsetAndRotation(0F, -5.58F, 0F, 0F, 0F, 0F));
        p_halo.addOrReplaceChild("halo_pua_9", CubeListBuilder.create()
                .texOffs(291, 341).addBox(-0.9F, -31F, -0.6F, 1.8F, 4.6F, 1.2F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 4.7124F));
        PartDefinition p_halo_rayo_10 = p_halo.addOrReplaceChild("halo_rayo_10", CubeListBuilder.create(),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 5.4978F));
        PartDefinition p_halo_rayo_10_l = p_halo_rayo_10.addOrReplaceChild("halo_rayo_10_l", CubeListBuilder.create()
                .texOffs(403, 300).addBox(-1.8F, -9.92F, -1.8F, 3.6F, 9.92F, 3.6F, infla),
                PartPose.offsetAndRotation(0F, -26.4F, 0F, 0F, 0F, 0F));
        p_halo_rayo_10_l.addOrReplaceChild("halo_rayo_10_l_p", CubeListBuilder.create()
                .texOffs(78, 330).addBox(-1.152F, -6.72F, -1.152F, 2.304F, 6.72F, 2.304F, infla),
                PartPose.offsetAndRotation(0F, -9.92F, 0F, 0F, 0F, 0F));
        p_halo.addOrReplaceChild("halo_pua_10", CubeListBuilder.create()
                .texOffs(291, 341).addBox(-0.9F, -31F, -0.6F, 1.8F, 4.6F, 1.2F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 5.236F));
        PartDefinition p_halo_rayo_11 = p_halo.addOrReplaceChild("halo_rayo_11", CubeListBuilder.create(),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 6.0214F));
        PartDefinition p_halo_rayo_11_l = p_halo_rayo_11.addOrReplaceChild("halo_rayo_11_l", CubeListBuilder.create()
                .texOffs(21, 330).addBox(-1.8F, -5.58F, -1.8F, 3.6F, 5.58F, 3.6F, infla),
                PartPose.offsetAndRotation(0F, -26.4F, 0F, 0F, 0F, 0F));
        p_halo_rayo_11_l.addOrReplaceChild("halo_rayo_11_l_p", CubeListBuilder.create()
                .texOffs(96, 341).addBox(-1.152F, -3.78F, -1.152F, 2.304F, 3.78F, 2.304F, infla),
                PartPose.offsetAndRotation(0F, -5.58F, 0F, 0F, 0F, 0F));
        p_halo.addOrReplaceChild("halo_pua_11", CubeListBuilder.create()
                .texOffs(291, 341).addBox(-0.9F, -31F, -0.6F, 1.8F, 4.6F, 1.2F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 5.7596F));
        PartDefinition p_hombro_izq = p_torso.addOrReplaceChild("hombro_izq", CubeListBuilder.create()
                .texOffs(288, 0).addBox(-6.5F, -9F, -13F, 20F, 11F, 26F, infla)
                .texOffs(381, 127).addBox(-5.5F, -12.4F, -11.5F, 18F, 3.6F, 23F, infla)
                .texOffs(413, 156).addBox(-5.9F, -13.2F, -12F, 18.8F, 1.2F, 24F, infla)
                .texOffs(241, 96).addBox(-6.9F, -9.6F, -13.6F, 20.8F, 1.2F, 27.2F, infla)
                .texOffs(275, 316).addBox(5.5F, -7F, 10.5F, 8F, 8F, 3F, infla)
                .texOffs(218, 341).addBox(7F, -5.5F, 13.2F, 5F, 5F, 1F, infla),
                PartPose.offsetAndRotation(21F, -42F, 0F, 0F, 0F, 0F));
        p_hombro_izq.addOrReplaceChild("lama0_izq", CubeListBuilder.create()
                .texOffs(121, 96).addBox(-9.5F, 0F, -12.4F, 20F, 5F, 24.8F, infla)
                .texOffs(288, 127).addBox(-9.8F, 4.2F, -12.7F, 20.6F, 1F, 25.4F, infla),
                PartPose.offsetAndRotation(6F, 2F, 0F, 0F, 0F, 0.1571F));
        p_hombro_izq.addOrReplaceChild("lama1_izq", CubeListBuilder.create()
                .texOffs(101, 127).addBox(-9.5F, 0F, -11.4F, 20F, 5F, 22.8F, infla)
                .texOffs(83, 183).addBox(-9.8F, 4.2F, -11.7F, 20.6F, 1F, 23.4F, infla),
                PartPose.offsetAndRotation(6F, 6.6F, 0F, 0F, 0F, 0.2793F));
        p_hombro_izq.addOrReplaceChild("lama2_izq", CubeListBuilder.create()
                .texOffs(0, 183).addBox(-9.5F, 0F, -10.4F, 20F, 5F, 20.8F, infla)
                .texOffs(0, 235).addBox(-9.8F, 4.2F, -10.7F, 20.6F, 1F, 21.4F, infla),
                PartPose.offsetAndRotation(6F, 11.2F, 0F, 0F, 0F, 0.4014F));
        p_hombro_izq.addOrReplaceChild("guarda_izq", CubeListBuilder.create()
                .texOffs(208, 61).addBox(-1.7F, -9F, -11.5F, 3.4F, 11F, 23F, infla)
                .texOffs(0, 259).addBox(-1.5F, -13F, -8.5F, 3F, 4F, 17F, infla)
                .texOffs(477, 300).addBox(-1.3F, -16F, -5F, 2.6F, 3F, 10F, infla)
                .texOffs(255, 183).addBox(-1.9F, -9.6F, -11.8F, 3.8F, 1F, 23.6F, infla)
                .texOffs(328, 259).addBox(-1.7F, -13.6F, -8.8F, 3.4F, 1F, 17.6F, infla)
                .texOffs(92, 316).addBox(-1.5F, -16.6F, -5.3F, 3F, 1F, 10.6F, infla)
                .texOffs(418, 281).addBox(1.7F, -7F, -4.5F, 1F, 8F, 8F, infla)
                .texOffs(53, 330).addBox(2.2F, -5.5F, -3F, 1F, 5F, 5F, infla),
                PartPose.offsetAndRotation(13F, -7F, 0F, 0F, 0F, 0.6981F));
        PartDefinition p_llama_h0_izq = p_hombro_izq.addOrReplaceChild("llama_h0_izq", CubeListBuilder.create()
                .texOffs(210, 330).addBox(-1.9F, -4.96F, -1.9F, 3.8F, 4.96F, 3.8F, infla),
                PartPose.offsetAndRotation(2F, -13F, -6F, -0.2094F, 0F, 0.2443F));
        p_llama_h0_izq.addOrReplaceChild("llama_h0_izq_p", CubeListBuilder.create()
                .texOffs(269, 341).addBox(-1.216F, -3.36F, -1.216F, 2.432F, 3.36F, 2.432F, infla),
                PartPose.offsetAndRotation(0F, -4.96F, 0F, -0.0838F, 0F, 0.1222F));
        PartDefinition p_llama_h1_izq = p_hombro_izq.addOrReplaceChild("llama_h1_izq", CubeListBuilder.create()
                .texOffs(298, 316).addBox(-1.9F, -6.82F, -1.9F, 3.8F, 6.82F, 3.8F, infla),
                PartPose.offsetAndRotation(6.5F, -13F, 0F, 0F, 0F, 0.2443F));
        p_llama_h1_izq.addOrReplaceChild("llama_h1_izq_p", CubeListBuilder.create()
                .texOffs(315, 330).addBox(-1.216F, -4.62F, -1.216F, 2.432F, 4.62F, 2.432F, infla),
                PartPose.offsetAndRotation(0F, -6.82F, 0F, 0F, 0F, 0.1222F));
        PartDefinition p_llama_h2_izq = p_hombro_izq.addOrReplaceChild("llama_h2_izq", CubeListBuilder.create()
                .texOffs(227, 330).addBox(-1.9F, -4.34F, -1.9F, 3.8F, 4.34F, 3.8F, infla),
                PartPose.offsetAndRotation(11F, -13F, 6F, 0.2094F, 0F, 0.2443F));
        p_llama_h2_izq.addOrReplaceChild("llama_h2_izq_p", CubeListBuilder.create()
                .texOffs(280, 341).addBox(-1.216F, -2.94F, -1.216F, 2.432F, 2.94F, 2.432F, infla),
                PartPose.offsetAndRotation(0F, -4.34F, 0F, 0.0838F, 0F, 0.1222F));
        PartDefinition p_brazo_izq = p_hombro_izq.addOrReplaceChild("brazo_izq", CubeListBuilder.create()
                .texOffs(367, 61).addBox(-5.5F, 0F, -5.5F, 11F, 22F, 11F, infla)
                .texOffs(85, 235).addBox(-6F, 6F, -6F, 12F, 11F, 12F, infla)
                .texOffs(256, 300).addBox(-6.3F, 16.4F, -6.3F, 12.6F, 1.2F, 12.6F, infla),
                PartPose.offsetAndRotation(0F, 4F, 0F, 0.3291F, 0.0001F, -0.0928F));
        PartDefinition p_antebrazo_izq = p_brazo_izq.addOrReplaceChild("antebrazo_izq", CubeListBuilder.create()
                .texOffs(158, 259).addBox(-6F, -3F, -6.5F, 12F, 7F, 13F, infla)
                .texOffs(437, 281).addBox(-6.3F, 3.4F, -6.8F, 12.6F, 1F, 13.6F, infla)
                .texOffs(456, 235).addBox(-6F, 4F, -6F, 12F, 9F, 12F, infla)
                .texOffs(394, 183).addBox(-7.6F, 12F, -7.6F, 15.2F, 8F, 15.2F, infla)
                .texOffs(180, 281).addBox(-7.9F, 19.2F, -7.9F, 15.8F, 1.2F, 15.8F, infla)
                .texOffs(245, 281).addBox(-7.9F, 12F, -7.9F, 15.8F, 1F, 15.8F, infla)
                .texOffs(53, 330).addBox(7.6F, 14F, -2.5F, 1F, 5F, 5F, infla),
                PartPose.offsetAndRotation(0F, 22F, 0F, -0.9233F, 0F, 0F));
        p_antebrazo_izq.addOrReplaceChild("pua_codo_izq", CubeListBuilder.create()
                .texOffs(244, 330).addBox(-1.5F, -6F, -1.5F, 3F, 6F, 3F, infla),
                PartPose.offsetAndRotation(0F, 0F, 6.5F, -1.2217F, 0F, 0F));
        PartDefinition p_mano_izq = p_antebrazo_izq.addOrReplaceChild("mano_izq", CubeListBuilder.create()
                .texOffs(258, 259).addBox(-5.6F, 0F, -5.6F, 11.2F, 8.5F, 11.2F, infla)
                .texOffs(339, 341).addBox(-5.9F, 0.8F, -6.4F, 11.8F, 2.4F, 2.4F, infla)
                .texOffs(0, 349).addBox(-4.4F, 0.4F, -8F, 1.8F, 1.8F, 1.8F, infla)
                .texOffs(0, 349).addBox(-0.9F, 0.4F, -8F, 1.8F, 1.8F, 1.8F, infla)
                .texOffs(0, 349).addBox(2.6F, 0.4F, -8F, 1.8F, 1.8F, 1.8F, infla)
                .texOffs(437, 300).addBox(-5.2F, 8.5F, -4.4F, 10.4F, 3.8F, 8.8F, infla),
                PartPose.offsetAndRotation(0F, 21F, 0F, 0F, 0F, 0F));
        p_mano_izq.addOrReplaceChild("sol_mano", CubeListBuilder.create(),
                PartPose.offsetAndRotation(0F, 4F, -2F, 0F, 0F, 0F));
        PartDefinition p_hombro_der = p_torso.addOrReplaceChild("hombro_der", CubeListBuilder.create()
                .texOffs(288, 0).addBox(-13.5F, -9F, -13F, 20F, 11F, 26F, infla)
                .texOffs(381, 127).addBox(-12.5F, -12.4F, -11.5F, 18F, 3.6F, 23F, infla)
                .texOffs(413, 156).addBox(-12.9F, -13.2F, -12F, 18.8F, 1.2F, 24F, infla)
                .texOffs(241, 96).addBox(-13.9F, -9.6F, -13.6F, 20.8F, 1.2F, 27.2F, infla)
                .texOffs(275, 316).addBox(-13.5F, -7F, 10.5F, 8F, 8F, 3F, infla)
                .texOffs(218, 341).addBox(-12F, -5.5F, 13.2F, 5F, 5F, 1F, infla),
                PartPose.offsetAndRotation(-21F, -42F, 0F, 0F, 0F, 0F));
        p_hombro_der.addOrReplaceChild("lama0_der", CubeListBuilder.create()
                .texOffs(121, 96).addBox(-9.5F, 0F, -12.4F, 20F, 5F, 24.8F, infla)
                .texOffs(288, 127).addBox(-9.8F, 4.2F, -12.7F, 20.6F, 1F, 25.4F, infla),
                PartPose.offsetAndRotation(-6F, 2F, 0F, 0F, 0F, -0.1571F));
        p_hombro_der.addOrReplaceChild("lama1_der", CubeListBuilder.create()
                .texOffs(101, 127).addBox(-9.5F, 0F, -11.4F, 20F, 5F, 22.8F, infla)
                .texOffs(83, 183).addBox(-9.8F, 4.2F, -11.7F, 20.6F, 1F, 23.4F, infla),
                PartPose.offsetAndRotation(-6F, 6.6F, 0F, 0F, 0F, -0.2793F));
        p_hombro_der.addOrReplaceChild("lama2_der", CubeListBuilder.create()
                .texOffs(0, 183).addBox(-9.5F, 0F, -10.4F, 20F, 5F, 20.8F, infla)
                .texOffs(0, 235).addBox(-9.8F, 4.2F, -10.7F, 20.6F, 1F, 21.4F, infla),
                PartPose.offsetAndRotation(-6F, 11.2F, 0F, 0F, 0F, -0.4014F));
        p_hombro_der.addOrReplaceChild("guarda_der", CubeListBuilder.create()
                .texOffs(208, 61).addBox(-1.7F, -9F, -11.5F, 3.4F, 11F, 23F, infla)
                .texOffs(0, 259).addBox(-1.5F, -13F, -8.5F, 3F, 4F, 17F, infla)
                .texOffs(477, 300).addBox(-1.3F, -16F, -5F, 2.6F, 3F, 10F, infla)
                .texOffs(255, 183).addBox(-1.9F, -9.6F, -11.8F, 3.8F, 1F, 23.6F, infla)
                .texOffs(328, 259).addBox(-1.7F, -13.6F, -8.8F, 3.4F, 1F, 17.6F, infla)
                .texOffs(92, 316).addBox(-1.5F, -16.6F, -5.3F, 3F, 1F, 10.6F, infla)
                .texOffs(418, 281).addBox(-2.7F, -7F, -4.5F, 1F, 8F, 8F, infla)
                .texOffs(53, 330).addBox(-3.2F, -5.5F, -3F, 1F, 5F, 5F, infla),
                PartPose.offsetAndRotation(-13F, -7F, 0F, 0F, 0F, -0.6981F));
        PartDefinition p_llama_h0_der = p_hombro_der.addOrReplaceChild("llama_h0_der", CubeListBuilder.create()
                .texOffs(210, 330).addBox(-1.9F, -4.96F, -1.9F, 3.8F, 4.96F, 3.8F, infla),
                PartPose.offsetAndRotation(-2F, -13F, -6F, -0.2094F, 0F, -0.2443F));
        p_llama_h0_der.addOrReplaceChild("llama_h0_der_p", CubeListBuilder.create()
                .texOffs(269, 341).addBox(-1.216F, -3.36F, -1.216F, 2.432F, 3.36F, 2.432F, infla),
                PartPose.offsetAndRotation(0F, -4.96F, 0F, -0.0838F, 0F, -0.1222F));
        PartDefinition p_llama_h1_der = p_hombro_der.addOrReplaceChild("llama_h1_der", CubeListBuilder.create()
                .texOffs(298, 316).addBox(-1.9F, -6.82F, -1.9F, 3.8F, 6.82F, 3.8F, infla),
                PartPose.offsetAndRotation(-6.5F, -13F, 0F, 0F, 0F, -0.2443F));
        p_llama_h1_der.addOrReplaceChild("llama_h1_der_p", CubeListBuilder.create()
                .texOffs(315, 330).addBox(-1.216F, -4.62F, -1.216F, 2.432F, 4.62F, 2.432F, infla),
                PartPose.offsetAndRotation(0F, -6.82F, 0F, 0F, 0F, -0.1222F));
        PartDefinition p_llama_h2_der = p_hombro_der.addOrReplaceChild("llama_h2_der", CubeListBuilder.create()
                .texOffs(227, 330).addBox(-1.9F, -4.34F, -1.9F, 3.8F, 4.34F, 3.8F, infla),
                PartPose.offsetAndRotation(-11F, -13F, 6F, 0.2094F, 0F, -0.2443F));
        p_llama_h2_der.addOrReplaceChild("llama_h2_der_p", CubeListBuilder.create()
                .texOffs(280, 341).addBox(-1.216F, -2.94F, -1.216F, 2.432F, 2.94F, 2.432F, infla),
                PartPose.offsetAndRotation(0F, -4.34F, 0F, 0.0838F, 0F, -0.1222F));
        PartDefinition p_brazo_der = p_hombro_der.addOrReplaceChild("brazo_der", CubeListBuilder.create()
                .texOffs(367, 61).addBox(-5.5F, 0F, -5.5F, 11F, 22F, 11F, infla)
                .texOffs(85, 235).addBox(-6F, 6F, -6F, 12F, 11F, 12F, infla)
                .texOffs(256, 300).addBox(-6.3F, 16.4F, -6.3F, 12.6F, 1.2F, 12.6F, infla),
                PartPose.offsetAndRotation(0F, 4F, 0F, 0.314F, 0F, 0.1244F));
        PartDefinition p_antebrazo_der = p_brazo_der.addOrReplaceChild("antebrazo_der", CubeListBuilder.create()
                .texOffs(158, 259).addBox(-6F, -3F, -6.5F, 12F, 7F, 13F, infla)
                .texOffs(437, 281).addBox(-6.3F, 3.4F, -6.8F, 12.6F, 1F, 13.6F, infla)
                .texOffs(456, 235).addBox(-6F, 4F, -6F, 12F, 9F, 12F, infla)
                .texOffs(394, 183).addBox(-7.6F, 12F, -7.6F, 15.2F, 8F, 15.2F, infla)
                .texOffs(180, 281).addBox(-7.9F, 19.2F, -7.9F, 15.8F, 1.2F, 15.8F, infla)
                .texOffs(245, 281).addBox(-7.9F, 12F, -7.9F, 15.8F, 1F, 15.8F, infla)
                .texOffs(53, 330).addBox(-8.6F, 14F, -2.5F, 1F, 5F, 5F, infla),
                PartPose.offsetAndRotation(0F, 22F, 0F, -1.084F, 0F, 0F));
        p_antebrazo_der.addOrReplaceChild("pua_codo_der", CubeListBuilder.create()
                .texOffs(244, 330).addBox(-1.5F, -6F, -1.5F, 3F, 6F, 3F, infla),
                PartPose.offsetAndRotation(0F, 0F, 6.5F, -1.2217F, 0F, 0F));
        PartDefinition p_mano_der = p_antebrazo_der.addOrReplaceChild("mano_der", CubeListBuilder.create()
                .texOffs(258, 259).addBox(-5.6F, 0F, -5.6F, 11.2F, 8.5F, 11.2F, infla)
                .texOffs(339, 341).addBox(-5.9F, 0.8F, -6.4F, 11.8F, 2.4F, 2.4F, infla)
                .texOffs(0, 349).addBox(-4.4F, 0.4F, -8F, 1.8F, 1.8F, 1.8F, infla)
                .texOffs(0, 349).addBox(-0.9F, 0.4F, -8F, 1.8F, 1.8F, 1.8F, infla)
                .texOffs(0, 349).addBox(2.6F, 0.4F, -8F, 1.8F, 1.8F, 1.8F, infla)
                .texOffs(437, 300).addBox(-5.2F, 8.5F, -4.4F, 10.4F, 3.8F, 8.8F, infla),
                PartPose.offsetAndRotation(0F, 21F, 0F, 0F, 0F, 0F));
        PartDefinition p_agarre = p_mano_der.addOrReplaceChild("agarre", CubeListBuilder.create(),
                PartPose.offsetAndRotation(0F, 5F, 0F, -0.1365F, -0.3826F, 0.1753F));
        PartDefinition p_espada = p_agarre.addOrReplaceChild("espada", CubeListBuilder.create()
                .texOffs(41, 259).addBox(-1.6F, -9F, -1.6F, 3.2F, 17F, 3.2F, infla)
                .texOffs(490, 316).addBox(-2.6F, -13F, -2.6F, 5.2F, 4.5F, 5.2F, infla)
                .texOffs(202, 341).addBox(-1.8F, -15F, -1.8F, 3.6F, 2.2F, 3.6F, infla)
                .texOffs(89, 330).addBox(-13F, 8F, -2.4F, 26F, 4F, 4.8F, infla)
                .texOffs(37, 330).addBox(-15F, 3F, -2F, 3.5F, 6F, 4F, infla)
                .texOffs(37, 330).addBox(11.5F, 3F, -2F, 3.5F, 6F, 4F, infla)
                .texOffs(110, 300).addBox(-4F, 5.5F, -3.2F, 8F, 8F, 6.4F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        p_espada.addOrReplaceChild("espada_hoja", CubeListBuilder.create()
                .texOffs(0, 0).addBox(-3.2F, 12F, -1F, 6.4F, 58F, 2F, infla)
                .texOffs(18, 0).addBox(-1.1F, 14F, -1.25F, 2.2F, 52F, 2.5F, infla)
                .texOffs(466, 316).addBox(-3.7F, 13F, -0.8F, 9.6F, 7.4286F, 1.6F, infla)
                .texOffs(466, 316).addBox(-5.9F, 20.4286F, -0.8F, 9.6F, 7.4286F, 1.6F, infla)
                .texOffs(466, 316).addBox(-3.7F, 27.8571F, -0.8F, 9.6F, 7.4286F, 1.6F, infla)
                .texOffs(466, 316).addBox(-5.9F, 35.2857F, -0.8F, 9.6F, 7.4286F, 1.6F, infla)
                .texOffs(466, 316).addBox(-3.7F, 42.7143F, -0.8F, 9.6F, 7.4286F, 1.6F, infla)
                .texOffs(466, 316).addBox(-5.9F, 50.1429F, -0.8F, 9.6F, 7.4286F, 1.6F, infla)
                .texOffs(466, 316).addBox(-3.7F, 57.5714F, -0.8F, 9.6F, 7.4286F, 1.6F, infla)
                .texOffs(288, 330).addBox(-2.6F, 70F, -0.8F, 5.2F, 6F, 1.6F, infla)
                .texOffs(126, 341).addBox(-1.2F, 76F, -0.6F, 2.4F, 5F, 1.2F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        PartDefinition p_espada_suelta = p_raiz.addOrReplaceChild("espada_suelta", CubeListBuilder.create()
                .texOffs(41, 259).addBox(-1.6F, -9F, -1.6F, 3.2F, 17F, 3.2F, infla)
                .texOffs(490, 316).addBox(-2.6F, -13F, -2.6F, 5.2F, 4.5F, 5.2F, infla)
                .texOffs(202, 341).addBox(-1.8F, -15F, -1.8F, 3.6F, 2.2F, 3.6F, infla)
                .texOffs(89, 330).addBox(-13F, 8F, -2.4F, 26F, 4F, 4.8F, infla)
                .texOffs(37, 330).addBox(-15F, 3F, -2F, 3.5F, 6F, 4F, infla)
                .texOffs(37, 330).addBox(11.5F, 3F, -2F, 3.5F, 6F, 4F, infla)
                .texOffs(110, 300).addBox(-4F, 5.5F, -3.2F, 8F, 8F, 6.4F, infla),
                PartPose.offsetAndRotation(-33.7455F, -46.1309F, -13.1677F, -0.0859F, -0.0279F, 0.1214F));
        p_espada_suelta.addOrReplaceChild("espada_suelta_hoja", CubeListBuilder.create()
                .texOffs(0, 0).addBox(-3.2F, 12F, -1F, 6.4F, 58F, 2F, infla)
                .texOffs(18, 0).addBox(-1.1F, 14F, -1.25F, 2.2F, 52F, 2.5F, infla)
                .texOffs(466, 316).addBox(-3.7F, 13F, -0.8F, 9.6F, 7.4286F, 1.6F, infla)
                .texOffs(466, 316).addBox(-5.9F, 20.4286F, -0.8F, 9.6F, 7.4286F, 1.6F, infla)
                .texOffs(466, 316).addBox(-3.7F, 27.8571F, -0.8F, 9.6F, 7.4286F, 1.6F, infla)
                .texOffs(466, 316).addBox(-5.9F, 35.2857F, -0.8F, 9.6F, 7.4286F, 1.6F, infla)
                .texOffs(466, 316).addBox(-3.7F, 42.7143F, -0.8F, 9.6F, 7.4286F, 1.6F, infla)
                .texOffs(466, 316).addBox(-5.9F, 50.1429F, -0.8F, 9.6F, 7.4286F, 1.6F, infla)
                .texOffs(466, 316).addBox(-3.7F, 57.5714F, -0.8F, 9.6F, 7.4286F, 1.6F, infla)
                .texOffs(288, 330).addBox(-2.6F, 70F, -0.8F, 5.2F, 6F, 1.6F, infla)
                .texOffs(126, 341).addBox(-1.2F, 76F, -0.6F, 2.4F, 5F, 1.2F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        return LayerDefinition.create(malla, 512, 512);
    }
}
