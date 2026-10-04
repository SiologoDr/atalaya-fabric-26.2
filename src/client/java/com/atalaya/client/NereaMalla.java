package com.atalaya.client;

import net.minecraft.client.model.geom.PartPose;
import net.minecraft.client.model.geom.builders.CubeListBuilder;
import net.minecraft.client.model.geom.builders.LayerDefinition;
import net.minecraft.client.model.geom.builders.MeshDefinition;
import net.minecraft.client.model.geom.builders.PartDefinition;

/**
 * La malla de Nerea. GENERADO por materiales/generadores/nerea_juego.py: no se
 * edita a mano. Cambiar una caja aqui sin cambiar el script descuadra la
 * textura, que se pinta con la misma cuadricula.
 */
public final class NereaMalla {

    private NereaMalla() {
    }

    public static LayerDefinition crear() {
        MeshDefinition malla = new MeshDefinition();
        PartDefinition p_root = malla.getRoot();
        PartDefinition p_pelvis = p_root.addOrReplaceChild("pelvis", CubeListBuilder.create()
                .texOffs(143, 87).addBox(-10F, -4F, -6F, 20F, 8F, 12F)
                .texOffs(68, 111).addBox(-11F, 2F, -6.5F, 22F, 4F, 13F),
                PartPose.offsetAndRotation(0F, -12F, 0F, 0F, 0F, 0F));
        p_pelvis.addOrReplaceChild("algas_del", CubeListBuilder.create()
                .texOffs(41, 148).addBox(-10F, -2F, 0F, 3F, 14F, 0F)
                .texOffs(136, 87).addBox(-2F, -2F, 0F, 3F, 21F, 0F)
                .texOffs(218, 87).addBox(6F, -2F, 0F, 3F, 19F, 0F),
                PartPose.offsetAndRotation(0F, 5F, -6.3F, 0F, 0F, 0F));
        p_pelvis.addOrReplaceChild("algas_tras", CubeListBuilder.create()
                .texOffs(77, 148).addBox(-6F, -2F, 0F, 3F, 13F, 0F)
                .texOffs(61, 111).addBox(2F, -2F, 0F, 3F, 18F, 0F)
                .texOffs(219, 130).addBox(10F, -2F, 0F, 3F, 15F, 0F),
                PartPose.offsetAndRotation(0F, 5F, 6.3F, 0F, 0F, 0F));
        PartDefinition p_pierna_izq = p_pelvis.addOrReplaceChild("pierna_izq", CubeListBuilder.create()
                .texOffs(207, 0).addBox(-4.5F, 0F, -4.5F, 9F, 16F, 9F),
                PartPose.offsetAndRotation(6F, 2F, 0F, -0.1047F, 0F, 0F));
        PartDefinition p_espinilla_izq = p_pierna_izq.addOrReplaceChild("espinilla_izq", CubeListBuilder.create()
                .texOffs(82, 87).addBox(-3.5F, 0F, -3.5F, 7F, 15F, 7F)
                .texOffs(0, 163).addBox(-4F, 1F, -4.6F, 8F, 9F, 2F),
                PartPose.offsetAndRotation(0F, 16F, 0F, 0.1745F, 0F, 0F));
        p_espinilla_izq.addOrReplaceChild("pie_izq", CubeListBuilder.create()
                .texOffs(0, 148).addBox(-4.5F, 0F, -7F, 9F, 3F, 11F),
                PartPose.offsetAndRotation(0F, 15F, 0F, -0.0698F, 0F, 0F));
        PartDefinition p_pierna_der = p_pelvis.addOrReplaceChild("pierna_der", CubeListBuilder.create()
                .texOffs(207, 0).addBox(-4.5F, 0F, -4.5F, 9F, 16F, 9F),
                PartPose.offsetAndRotation(-6F, 2F, 0F, -0.1047F, 0F, 0F));
        PartDefinition p_espinilla_der = p_pierna_der.addOrReplaceChild("espinilla_der", CubeListBuilder.create()
                .texOffs(82, 87).addBox(-3.5F, 0F, -3.5F, 7F, 15F, 7F)
                .texOffs(0, 163).addBox(-4F, 1F, -4.6F, 8F, 9F, 2F),
                PartPose.offsetAndRotation(0F, 16F, 0F, 0.1745F, 0F, 0F));
        p_espinilla_der.addOrReplaceChild("pie_der", CubeListBuilder.create()
                .texOffs(0, 148).addBox(-4.5F, 0F, -7F, 9F, 3F, 11F),
                PartPose.offsetAndRotation(0F, 15F, 0F, -0.0698F, 0F, 0F));
        PartDefinition p_torso = p_pelvis.addOrReplaceChild("torso", CubeListBuilder.create()
                .texOffs(9, 0).addBox(-12F, -28F, -6F, 24F, 28F, 13F)
                .texOffs(84, 0).addBox(-12.5F, -28.5F, 0F, 25F, 29F, 7.5F)
                .texOffs(66, 130).addBox(-12.5F, -9F, -7F, 25F, 9F, 7F)
                .texOffs(134, 175).addBox(-9F, -27F, 7F, 3F, 3F, 2F)
                .texOffs(134, 175).addBox(5F, -12F, 7F, 3F, 3F, 2F),
                PartPose.offsetAndRotation(0F, -4F, 0F, 0.2443F, 0F, 0F));
        p_torso.addOrReplaceChild("costillas", CubeListBuilder.create()
                .texOffs(0, 182).addBox(-9F, -24.5F, -8.6F, 18F, 1.4F, 1.6F)
                .texOffs(0, 182).addBox(-9F, -20.3F, -8.6F, 18F, 1.4F, 1.6F)
                .texOffs(0, 182).addBox(-9F, -16.1F, -8.6F, 18F, 1.4F, 1.6F)
                .texOffs(0, 182).addBox(-9F, -11.9F, -8.6F, 18F, 1.4F, 1.6F)
                .texOffs(208, 87).addBox(-1.5F, -27F, -8.9F, 3F, 18F, 1.4F),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        PartDefinition p_corazon = p_torso.addOrReplaceChild("corazon", CubeListBuilder.create(),
                PartPose.offsetAndRotation(0F, -17.5F, -5.2F, 0F, 0F, 0F));
        p_corazon.addOrReplaceChild("corazon_1", CubeListBuilder.create()
                .texOffs(139, 111).addBox(-5F, -5.5F, -3F, 10F, 11F, 6F)
                .texOffs(203, 163).addBox(-3F, -7.5F, -2.4F, 6F, 2F, 4F),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        p_corazon.addOrReplaceChild("corazon_2", CubeListBuilder.create()
                .texOffs(172, 111).addBox(-5F, -5.5F, -3F, 10F, 11F, 6F)
                .texOffs(224, 163).addBox(-3F, -7.5F, -2.4F, 6F, 2F, 4F),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        p_corazon.addOrReplaceChild("corazon_3", CubeListBuilder.create()
                .texOffs(205, 111).addBox(-5F, -5.5F, -3F, 10F, 11F, 6F)
                .texOffs(0, 175).addBox(-3F, -7.5F, -2.4F, 6F, 2F, 4F),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        p_corazon.addOrReplaceChild("corazon_4", CubeListBuilder.create()
                .texOffs(0, 130).addBox(-5F, -5.5F, -3F, 10F, 11F, 6F)
                .texOffs(21, 175).addBox(-3F, -7.5F, -2.4F, 6F, 2F, 4F),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        p_corazon.addOrReplaceChild("corazon_libre", CubeListBuilder.create()
                .texOffs(33, 130).addBox(-5F, -5.5F, -3F, 10F, 11F, 6F)
                .texOffs(42, 175).addBox(-3F, -7.5F, -2.4F, 6F, 2F, 4F),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        p_torso.addOrReplaceChild("cadena_1", CubeListBuilder.create()
                .texOffs(89, 175).addBox(-1.65F, 0F, -0.55F, 3.3F, 4.4F, 1.1F)
                .texOffs(92, 163).addBox(-0.55F, 3.52F, -1.65F, 1.1F, 4.4F, 3.3F)
                .texOffs(89, 175).addBox(-1.65F, 7.04F, -0.55F, 3.3F, 4.4F, 1.1F)
                .texOffs(92, 163).addBox(-0.55F, 10.56F, -1.65F, 1.1F, 4.4F, 3.3F)
                .texOffs(89, 175).addBox(-1.65F, 14.08F, -0.55F, 3.3F, 4.4F, 1.1F)
                .texOffs(92, 163).addBox(-0.55F, 17.6F, -1.65F, 1.1F, 4.4F, 3.3F)
                .texOffs(89, 175).addBox(-1.65F, 21.12F, -0.55F, 3.3F, 4.4F, 1.1F)
                .texOffs(92, 163).addBox(-0.55F, 24.64F, -1.65F, 1.1F, 4.4F, 3.3F)
                .texOffs(89, 175).addBox(-1.65F, 28.16F, -0.55F, 3.3F, 4.4F, 1.1F),
                PartPose.offsetAndRotation(-11F, -27F, -9.6F, 0.8086F, 1.5708F, 0F));
        p_torso.addOrReplaceChild("cadena_2", CubeListBuilder.create()
                .texOffs(89, 175).addBox(-1.65F, 0F, -0.55F, 3.3F, 4.4F, 1.1F)
                .texOffs(92, 163).addBox(-0.55F, 3.52F, -1.65F, 1.1F, 4.4F, 3.3F)
                .texOffs(89, 175).addBox(-1.65F, 7.04F, -0.55F, 3.3F, 4.4F, 1.1F)
                .texOffs(92, 163).addBox(-0.55F, 10.56F, -1.65F, 1.1F, 4.4F, 3.3F)
                .texOffs(89, 175).addBox(-1.65F, 14.08F, -0.55F, 3.3F, 4.4F, 1.1F)
                .texOffs(92, 163).addBox(-0.55F, 17.6F, -1.65F, 1.1F, 4.4F, 3.3F)
                .texOffs(89, 175).addBox(-1.65F, 21.12F, -0.55F, 3.3F, 4.4F, 1.1F)
                .texOffs(92, 163).addBox(-0.55F, 24.64F, -1.65F, 1.1F, 4.4F, 3.3F)
                .texOffs(89, 175).addBox(-1.65F, 28.16F, -0.55F, 3.3F, 4.4F, 1.1F),
                PartPose.offsetAndRotation(11F, -27F, -9.6F, 0.8086F, -1.5708F, 0F));
        p_torso.addOrReplaceChild("cadena_3", CubeListBuilder.create()
                .texOffs(145, 175).addBox(-1.5F, 0F, -0.5F, 3F, 4F, 1F)
                .texOffs(148, 163).addBox(-0.5F, 3.2F, -1.5F, 1F, 4F, 3F)
                .texOffs(145, 175).addBox(-1.5F, 6.4F, -0.5F, 3F, 4F, 1F)
                .texOffs(148, 163).addBox(-0.5F, 9.6F, -1.5F, 1F, 4F, 3F)
                .texOffs(145, 175).addBox(-1.5F, 12.8F, -0.5F, 3F, 4F, 1F)
                .texOffs(148, 163).addBox(-0.5F, 16F, -1.5F, 1F, 4F, 3F)
                .texOffs(145, 175).addBox(-1.5F, 19.2F, -0.5F, 3F, 4F, 1F)
                .texOffs(148, 163).addBox(-0.5F, 22.4F, -1.5F, 1F, 4F, 3F),
                PartPose.offsetAndRotation(-12.5F, -4F, -7.6F, 1.5708F, 1.5708F, 0F));
        p_torso.addOrReplaceChild("cadena_4", CubeListBuilder.create()
                .texOffs(145, 175).addBox(-1.5F, 0F, -0.5F, 3F, 4F, 1F)
                .texOffs(148, 163).addBox(-0.5F, 3.2F, -1.5F, 1F, 4F, 3F)
                .texOffs(145, 175).addBox(-1.5F, 6.4F, -0.5F, 3F, 4F, 1F)
                .texOffs(148, 163).addBox(-0.5F, 9.6F, -1.5F, 1F, 4F, 3F)
                .texOffs(145, 175).addBox(-1.5F, 12.8F, -0.5F, 3F, 4F, 1F)
                .texOffs(148, 163).addBox(-0.5F, 16F, -1.5F, 1F, 4F, 3F)
                .texOffs(145, 175).addBox(-1.5F, 19.2F, -0.5F, 3F, 4F, 1F)
                .texOffs(148, 163).addBox(-0.5F, 22.4F, -1.5F, 1F, 4F, 3F),
                PartPose.offsetAndRotation(-12F, -26.4F, -9.9F, 1.5708F, 1.5708F, 0F));
        PartDefinition p_cuello = p_torso.addOrReplaceChild("cuello", CubeListBuilder.create()
                .texOffs(194, 148).addBox(-3F, -5F, -3F, 6F, 5F, 6F),
                PartPose.offsetAndRotation(0F, -28F, -2F, -0.2094F, 0F, 0F));
        PartDefinition p_cabeza = p_cuello.addOrReplaceChild("cabeza", CubeListBuilder.create()
                .texOffs(150, 0).addBox(-7F, -13F, -7F, 14F, 13F, 14F)
                .texOffs(0, 111).addBox(-7.5F, -14F, -7.5F, 15F, 3F, 15F)
                .texOffs(196, 175).addBox(-5.5F, -7.5F, -7.3F, 3.5F, 3F, 0.6F)
                .texOffs(196, 175).addBox(2F, -7.5F, -7.3F, 3.5F, 3F, 0.6F)
                .texOffs(71, 182).addBox(-1F, -4.5F, -7.2F, 2F, 2F, 0.4F),
                PartPose.offsetAndRotation(0F, -5F, 0F, -0.0698F, 0F, 0F));
        p_cabeza.addOrReplaceChild("ojo_izq", CubeListBuilder.create()
                .texOffs(63, 182).addBox(-1.25F, -1F, -0.4F, 2.5F, 2F, 0.8F),
                PartPose.offsetAndRotation(3.75F, -6F, -7.6F, 0F, 0F, 0F));
        p_cabeza.addOrReplaceChild("ojo_der", CubeListBuilder.create()
                .texOffs(63, 182).addBox(-1.25F, -1F, -0.4F, 2.5F, 2F, 0.8F),
                PartPose.offsetAndRotation(-3.75F, -6F, -7.6F, 0F, 0F, 0F));
        p_cabeza.addOrReplaceChild("mandibula", CubeListBuilder.create()
                .texOffs(172, 130).addBox(-6F, 0F, -11F, 12F, 4F, 11F)
                .texOffs(77, 182).addBox(-5F, -1.3F, -10.8F, 1.2F, 1.5F, 1.2F)
                .texOffs(77, 182).addBox(-2.8F, -1.3F, -10.8F, 1.2F, 1.5F, 1.2F)
                .texOffs(77, 182).addBox(-0.6F, -1.3F, -10.8F, 1.2F, 1.5F, 1.2F)
                .texOffs(77, 182).addBox(1.6F, -1.3F, -10.8F, 1.2F, 1.5F, 1.2F)
                .texOffs(77, 182).addBox(3.8F, -1.3F, -10.8F, 1.2F, 1.5F, 1.2F),
                PartPose.offsetAndRotation(0F, 0F, 3F, 0F, 0F, 0F));
        p_cabeza.addOrReplaceChild("puas_0", CubeListBuilder.create()
                .texOffs(102, 163).addBox(-1F, -6F, -1F, 2F, 6F, 2F),
                PartPose.offsetAndRotation(-6F, -14F, -6F, -0.1745F, 0F, -0.2094F));
        p_cabeza.addOrReplaceChild("puas_1", CubeListBuilder.create()
                .texOffs(51, 163).addBox(-1F, -8F, -1F, 2F, 8F, 2F),
                PartPose.offsetAndRotation(0F, -14F, -7F, -0.2443F, 0F, 0F));
        p_cabeza.addOrReplaceChild("puas_2", CubeListBuilder.create()
                .texOffs(176, 148).addBox(-1F, -10F, -1F, 2F, 10F, 2F),
                PartPose.offsetAndRotation(6F, -14F, -6F, -0.1745F, 0F, 0.2094F));
        p_cabeza.addOrReplaceChild("puas_3", CubeListBuilder.create()
                .texOffs(102, 163).addBox(-1F, -6F, -1F, 2F, 6F, 2F),
                PartPose.offsetAndRotation(-6.5F, -14F, 0F, 0F, 0F, -0.2793F));
        p_cabeza.addOrReplaceChild("puas_4", CubeListBuilder.create()
                .texOffs(51, 163).addBox(-1F, -8F, -1F, 2F, 8F, 2F),
                PartPose.offsetAndRotation(6.5F, -14F, 0F, 0F, 0F, 0.2793F));
        p_cabeza.addOrReplaceChild("puas_5", CubeListBuilder.create()
                .texOffs(176, 148).addBox(-1F, -10F, -1F, 2F, 10F, 2F),
                PartPose.offsetAndRotation(0F, -14F, 6F, 0.2094F, 0F, 0F));
        PartDefinition p_corona_c1 = p_cabeza.addOrReplaceChild("corona_c1", CubeListBuilder.create()
                .texOffs(185, 148).addBox(-1F, -10F, -1F, 2F, 10F, 2F),
                PartPose.offsetAndRotation(-4F, -14F, -3F, -0.1047F, 0F, -0.3142F));
        p_corona_c1.addOrReplaceChild("corona_c1_a", CubeListBuilder.create()
                .texOffs(157, 163).addBox(-0.75F, -5F, -0.75F, 1.5F, 5F, 1.5F),
                PartPose.offsetAndRotation(0F, -5.5F, 0F, 0F, 0F, 0.6632F));
        p_corona_c1.addOrReplaceChild("corona_c1_b", CubeListBuilder.create()
                .texOffs(99, 175).addBox(-0.75F, -4F, -0.75F, 1.5F, 4F, 1.5F),
                PartPose.offsetAndRotation(0F, -7.5F, 0F, 0F, 0F, -0.5934F));
        PartDefinition p_corona_c2 = p_cabeza.addOrReplaceChild("corona_c2", CubeListBuilder.create()
                .texOffs(60, 163).addBox(-1F, -8F, -1F, 2F, 8F, 2F),
                PartPose.offsetAndRotation(3F, -14F, 2F, 0.1396F, 0F, 0.384F));
        p_corona_c2.addOrReplaceChild("corona_c2_a", CubeListBuilder.create()
                .texOffs(106, 175).addBox(-0.75F, -4F, -0.75F, 1.5F, 4F, 1.5F),
                PartPose.offsetAndRotation(0F, -4.4F, 0F, 0F, 0F, 0.6632F));
        p_corona_c2.addOrReplaceChild("corona_c2_b", CubeListBuilder.create()
                .texOffs(154, 175).addBox(-0.75F, -3.2F, -0.75F, 1.5F, 3.2F, 1.5F),
                PartPose.offsetAndRotation(0F, -6F, 0F, 0F, 0F, -0.5934F));
        PartDefinition p_corona_c3 = p_cabeza.addOrReplaceChild("corona_c3", CubeListBuilder.create()
                .texOffs(69, 163).addBox(-1F, -7F, -1F, 2F, 7F, 2F),
                PartPose.offsetAndRotation(5F, -14F, -4F, -0.2094F, 0F, 0.5236F));
        p_corona_c3.addOrReplaceChild("corona_c3_a", CubeListBuilder.create()
                .texOffs(161, 175).addBox(-0.75F, -3.5F, -0.75F, 1.5F, 3.5F, 1.5F),
                PartPose.offsetAndRotation(0F, -3.85F, 0F, 0F, 0F, 0.6632F));
        p_corona_c3.addOrReplaceChild("corona_c3_b", CubeListBuilder.create()
                .texOffs(168, 175).addBox(-0.75F, -2.8F, -0.75F, 1.5F, 2.8F, 1.5F),
                PartPose.offsetAndRotation(0F, -5.25F, 0F, 0F, 0F, -0.5934F));
        PartDefinition p_corona_c4 = p_cabeza.addOrReplaceChild("corona_c4", CubeListBuilder.create()
                .texOffs(111, 163).addBox(-1F, -6F, -1F, 2F, 6F, 2F),
                PartPose.offsetAndRotation(-2F, -14F, 5F, 0.2793F, 0F, -0.1396F));
        p_corona_c4.addOrReplaceChild("corona_c4_a", CubeListBuilder.create()
                .texOffs(175, 175).addBox(-0.75F, -3F, -0.75F, 1.5F, 3F, 1.5F),
                PartPose.offsetAndRotation(0F, -3.3F, 0F, 0F, 0F, 0.6632F));
        p_corona_c4.addOrReplaceChild("corona_c4_b", CubeListBuilder.create()
                .texOffs(215, 175).addBox(-0.75F, -2.4F, -0.75F, 1.5F, 2.4F, 1.5F),
                PartPose.offsetAndRotation(0F, -4.5F, 0F, 0F, 0F, -0.5934F));
        PartDefinition p_hombro_izq = p_torso.addOrReplaceChild("hombro_izq", CubeListBuilder.create()
                .texOffs(29, 87).addBox(-6.5F, -5F, -6.5F, 13F, 9F, 13F)
                .texOffs(84, 148).addBox(-5.5F, -6F, -5.5F, 11F, 1F, 11F)
                .texOffs(206, 175).addBox(2F, -7F, 2F, 2F, 2F, 2F),
                PartPose.offsetAndRotation(15F, -25F, 0F, 0F, 0F, 0F));
        PartDefinition p_coral_h1_izq = p_hombro_izq.addOrReplaceChild("coral_h1_izq", CubeListBuilder.create()
                .texOffs(21, 163).addBox(-1F, -9F, -1F, 2F, 9F, 2F),
                PartPose.offsetAndRotation(2F, -6F, -2F, 0.1396F, 0F, 0.1745F));
        p_coral_h1_izq.addOrReplaceChild("coral_h1_izq_a", CubeListBuilder.create()
                .texOffs(113, 175).addBox(-0.75F, -4.5F, -0.75F, 1.5F, 4.5F, 1.5F),
                PartPose.offsetAndRotation(0F, -4.95F, 0F, 0F, 0F, 0.6632F));
        p_coral_h1_izq.addOrReplaceChild("coral_h1_izq_b", CubeListBuilder.create()
                .texOffs(120, 175).addBox(-0.75F, -3.6F, -0.75F, 1.5F, 3.6F, 1.5F),
                PartPose.offsetAndRotation(0F, -6.75F, 0F, 0F, 0F, -0.5934F));
        PartDefinition p_coral_h2_izq = p_hombro_izq.addOrReplaceChild("coral_h2_izq", CubeListBuilder.create()
                .texOffs(120, 163).addBox(-1F, -6F, -1F, 2F, 6F, 2F),
                PartPose.offsetAndRotation(-3F, -6F, 3F, -0.1745F, 0F, -0.2443F));
        p_coral_h2_izq.addOrReplaceChild("coral_h2_izq_a", CubeListBuilder.create()
                .texOffs(182, 175).addBox(-0.75F, -3F, -0.75F, 1.5F, 3F, 1.5F),
                PartPose.offsetAndRotation(0F, -3.3F, 0F, 0F, 0F, 0.6632F));
        p_coral_h2_izq.addOrReplaceChild("coral_h2_izq_b", CubeListBuilder.create()
                .texOffs(222, 175).addBox(-0.75F, -2.4F, -0.75F, 1.5F, 2.4F, 1.5F),
                PartPose.offsetAndRotation(0F, -4.5F, 0F, 0F, 0F, -0.5934F));
        PartDefinition p_coral_h3_izq = p_hombro_izq.addOrReplaceChild("coral_h3_izq", CubeListBuilder.create()
                .texOffs(69, 163).addBox(-1F, -7F, -1F, 2F, 7F, 2F),
                PartPose.offsetAndRotation(4F, -6F, 4F, -0.1047F, 0F, 0.384F));
        p_coral_h3_izq.addOrReplaceChild("coral_h3_izq_a", CubeListBuilder.create()
                .texOffs(161, 175).addBox(-0.75F, -3.5F, -0.75F, 1.5F, 3.5F, 1.5F),
                PartPose.offsetAndRotation(0F, -3.85F, 0F, 0F, 0F, 0.6632F));
        p_coral_h3_izq.addOrReplaceChild("coral_h3_izq_b", CubeListBuilder.create()
                .texOffs(168, 175).addBox(-0.75F, -2.8F, -0.75F, 1.5F, 2.8F, 1.5F),
                PartPose.offsetAndRotation(0F, -5.25F, 0F, 0F, 0F, -0.5934F));
        PartDefinition p_brazo_izq = p_hombro_izq.addOrReplaceChild("brazo_izq", CubeListBuilder.create()
                .texOffs(0, 87).addBox(-3.5F, 0F, -3.5F, 7F, 16F, 7F)
                .texOffs(129, 148).addBox(-4F, 4F, -4F, 8F, 4F, 8F),
                PartPose.offsetAndRotation(0F, 2F, 0F, -0.1047F, 0F, -0.0698F));
        PartDefinition p_antebrazo_izq = p_brazo_izq.addOrReplaceChild("antebrazo_izq", CubeListBuilder.create()
                .texOffs(111, 87).addBox(-3F, 0F, -3F, 6F, 15F, 6F)
                .texOffs(131, 130).addBox(-3.6F, 6F, -3.6F, 7.2F, 8F, 7.2F),
                PartPose.offsetAndRotation(0F, 16F, 0F, -0.2793F, 0F, 0F));
        PartDefinition p_mano_izq = p_antebrazo_izq.addOrReplaceChild("mano_izq", CubeListBuilder.create()
                .texOffs(48, 148).addBox(-3.5F, 0F, -3.5F, 7F, 6F, 7F),
                PartPose.offsetAndRotation(0F, 15F, 0F, 0F, 0F, 0F));
        PartDefinition p_hombro_der = p_torso.addOrReplaceChild("hombro_der", CubeListBuilder.create()
                .texOffs(29, 87).addBox(-6.5F, -5F, -6.5F, 13F, 9F, 13F)
                .texOffs(84, 148).addBox(-5.5F, -6F, -5.5F, 11F, 1F, 11F)
                .texOffs(206, 175).addBox(-4F, -7F, 2F, 2F, 2F, 2F),
                PartPose.offsetAndRotation(-15F, -25F, 0F, 0F, 0F, 0F));
        PartDefinition p_coral_h1_der = p_hombro_der.addOrReplaceChild("coral_h1_der", CubeListBuilder.create()
                .texOffs(21, 163).addBox(-1F, -9F, -1F, 2F, 9F, 2F),
                PartPose.offsetAndRotation(-2F, -6F, -2F, 0.1396F, 0F, -0.1745F));
        p_coral_h1_der.addOrReplaceChild("coral_h1_der_a", CubeListBuilder.create()
                .texOffs(113, 175).addBox(-0.75F, -4.5F, -0.75F, 1.5F, 4.5F, 1.5F),
                PartPose.offsetAndRotation(0F, -4.95F, 0F, 0F, 0F, 0.6632F));
        p_coral_h1_der.addOrReplaceChild("coral_h1_der_b", CubeListBuilder.create()
                .texOffs(120, 175).addBox(-0.75F, -3.6F, -0.75F, 1.5F, 3.6F, 1.5F),
                PartPose.offsetAndRotation(0F, -6.75F, 0F, 0F, 0F, -0.5934F));
        PartDefinition p_coral_h2_der = p_hombro_der.addOrReplaceChild("coral_h2_der", CubeListBuilder.create()
                .texOffs(120, 163).addBox(-1F, -6F, -1F, 2F, 6F, 2F),
                PartPose.offsetAndRotation(3F, -6F, 3F, -0.1745F, 0F, 0.2443F));
        p_coral_h2_der.addOrReplaceChild("coral_h2_der_a", CubeListBuilder.create()
                .texOffs(182, 175).addBox(-0.75F, -3F, -0.75F, 1.5F, 3F, 1.5F),
                PartPose.offsetAndRotation(0F, -3.3F, 0F, 0F, 0F, 0.6632F));
        p_coral_h2_der.addOrReplaceChild("coral_h2_der_b", CubeListBuilder.create()
                .texOffs(222, 175).addBox(-0.75F, -2.4F, -0.75F, 1.5F, 2.4F, 1.5F),
                PartPose.offsetAndRotation(0F, -4.5F, 0F, 0F, 0F, -0.5934F));
        PartDefinition p_coral_h3_der = p_hombro_der.addOrReplaceChild("coral_h3_der", CubeListBuilder.create()
                .texOffs(69, 163).addBox(-1F, -7F, -1F, 2F, 7F, 2F),
                PartPose.offsetAndRotation(-4F, -6F, 4F, -0.1047F, 0F, -0.384F));
        p_coral_h3_der.addOrReplaceChild("coral_h3_der_a", CubeListBuilder.create()
                .texOffs(161, 175).addBox(-0.75F, -3.5F, -0.75F, 1.5F, 3.5F, 1.5F),
                PartPose.offsetAndRotation(0F, -3.85F, 0F, 0F, 0F, 0.6632F));
        p_coral_h3_der.addOrReplaceChild("coral_h3_der_b", CubeListBuilder.create()
                .texOffs(168, 175).addBox(-0.75F, -2.8F, -0.75F, 1.5F, 2.8F, 1.5F),
                PartPose.offsetAndRotation(0F, -5.25F, 0F, 0F, 0F, -0.5934F));
        PartDefinition p_brazo_der = p_hombro_der.addOrReplaceChild("brazo_der", CubeListBuilder.create()
                .texOffs(0, 87).addBox(-3.5F, 0F, -3.5F, 7F, 16F, 7F)
                .texOffs(129, 148).addBox(-4F, 4F, -4F, 8F, 4F, 8F),
                PartPose.offsetAndRotation(0F, 2F, 0F, -0.4189F, 0F, 0.1047F));
        PartDefinition p_antebrazo_der = p_brazo_der.addOrReplaceChild("antebrazo_der", CubeListBuilder.create()
                .texOffs(111, 87).addBox(-3F, 0F, -3F, 6F, 15F, 6F)
                .texOffs(131, 130).addBox(-3.6F, 6F, -3.6F, 7.2F, 8F, 7.2F),
                PartPose.offsetAndRotation(0F, 16F, 0F, -1.0821F, 0F, 0F));
        PartDefinition p_mano_der = p_antebrazo_der.addOrReplaceChild("mano_der", CubeListBuilder.create()
                .texOffs(48, 148).addBox(-3.5F, 0F, -3.5F, 7F, 6F, 7F),
                PartPose.offsetAndRotation(0F, 15F, 0F, 0F, 0F, 0F));
        PartDefinition p_cadena_mano = p_mano_izq.addOrReplaceChild("cadena_mano", CubeListBuilder.create()
                .texOffs(136, 163).addBox(-1.95F, 0F, -0.65F, 3.9F, 5.2F, 1.3F)
                .texOffs(39, 163).addBox(-0.65F, 4.16F, -1.95F, 1.3F, 5.2F, 3.9F)
                .texOffs(136, 163).addBox(-1.95F, 8.32F, -0.65F, 3.9F, 5.2F, 1.3F)
                .texOffs(39, 163).addBox(-0.65F, 12.48F, -1.95F, 1.3F, 5.2F, 3.9F),
                PartPose.offsetAndRotation(0F, 5F, 0F, 0.3218F, 0F, 0F));
        p_cadena_mano.addOrReplaceChild("gancho_mano", CubeListBuilder.create()
                .texOffs(63, 175).addBox(-1.5F, 0F, -1.5F, 3F, 3F, 3F)
                .texOffs(129, 163).addBox(-0.75F, 3F, -0.75F, 1.5F, 6F, 1.5F)
                .texOffs(41, 182).addBox(-4.5F, 7F, -0.75F, 9F, 1.5F, 1.5F)
                .texOffs(127, 175).addBox(-4.5F, 3.5F, -0.75F, 1.5F, 4F, 1.5F)
                .texOffs(127, 175).addBox(3F, 3.5F, -0.75F, 1.5F, 4F, 1.5F)
                .texOffs(219, 148).addBox(-0.75F, 7F, -4.5F, 1.5F, 1.5F, 9F)
                .texOffs(127, 175).addBox(-0.75F, 3.5F, -4.5F, 1.5F, 4F, 1.5F)
                .texOffs(127, 175).addBox(-0.75F, 3.5F, 3F, 1.5F, 4F, 1.5F),
                PartPose.offsetAndRotation(0F, 15.8114F, 0F, 0F, 0F, 0F));
        p_mano_der.addOrReplaceChild("tridente", CubeListBuilder.create()
                .texOffs(0, 0).addBox(-1F, -26F, -1F, 2F, 84F, 2F)
                .texOffs(76, 175).addBox(-1.5F, 52F, -1.5F, 3F, 3F, 3F)
                .texOffs(164, 163).addBox(-8F, 55F, -1.5F, 16F, 2.5F, 3F)
                .texOffs(161, 130).addBox(-1.25F, 57F, -1.25F, 2.5F, 13F, 2.5F)
                .texOffs(30, 163).addBox(-7.5F, 57F, -1F, 2F, 9F, 2F)
                .texOffs(30, 163).addBox(5.5F, 57F, -1F, 2F, 9F, 2F)
                .texOffs(189, 175).addBox(-3F, 64F, -0.75F, 1.5F, 3F, 1.5F)
                .texOffs(189, 175).addBox(1.5F, 64F, -0.75F, 1.5F, 3F, 1.5F),
                PartPose.offsetAndRotation(0F, 4F, 0F, -1.2399F, 0F, 2.8241F));
        p_pelvis.addOrReplaceChild("molino_izq", CubeListBuilder.create()
                .texOffs(78, 163).addBox(-2.4F, 0F, -0.8F, 4.8F, 6.4F, 1.6F)
                .texOffs(162, 148).addBox(-0.8F, 5.12F, -2.4F, 1.6F, 6.4F, 4.8F)
                .texOffs(78, 163).addBox(-2.4F, 10.24F, -0.8F, 4.8F, 6.4F, 1.6F)
                .texOffs(162, 148).addBox(-0.8F, 15.36F, -2.4F, 1.6F, 6.4F, 4.8F)
                .texOffs(78, 163).addBox(-2.4F, 20.48F, -0.8F, 4.8F, 6.4F, 1.6F)
                .texOffs(162, 148).addBox(-0.8F, 25.6F, -2.4F, 1.6F, 6.4F, 4.8F)
                .texOffs(78, 163).addBox(-2.4F, 30.72F, -0.8F, 4.8F, 6.4F, 1.6F)
                .texOffs(162, 148).addBox(-0.8F, 35.84F, -2.4F, 1.6F, 6.4F, 4.8F)
                .texOffs(78, 163).addBox(-2.4F, 40.96F, -0.8F, 4.8F, 6.4F, 1.6F)
                .texOffs(162, 148).addBox(-0.8F, 46.08F, -2.4F, 1.6F, 6.4F, 4.8F)
                .texOffs(78, 163).addBox(-2.4F, 51.2F, -0.8F, 4.8F, 6.4F, 1.6F)
                .texOffs(162, 148).addBox(-0.8F, 56.32F, -2.4F, 1.6F, 6.4F, 4.8F)
                .texOffs(78, 163).addBox(-2.4F, 61.44F, -0.8F, 4.8F, 6.4F, 1.6F)
                .texOffs(162, 148).addBox(-0.8F, 66.56F, -2.4F, 1.6F, 6.4F, 4.8F)
                .texOffs(78, 163).addBox(-2.4F, 71.68F, -0.8F, 4.8F, 6.4F, 1.6F)
                .texOffs(162, 148).addBox(-0.8F, 76.8F, -2.4F, 1.6F, 6.4F, 4.8F)
                .texOffs(78, 163).addBox(-2.4F, 81.92F, -0.8F, 4.8F, 6.4F, 1.6F)
                .texOffs(162, 148).addBox(-0.8F, 87.04F, -2.4F, 1.6F, 6.4F, 4.8F)
                .texOffs(78, 163).addBox(-2.4F, 92.16F, -0.8F, 4.8F, 6.4F, 1.6F)
                .texOffs(162, 148).addBox(-0.8F, 97.28F, -2.4F, 1.6F, 6.4F, 4.8F),
                PartPose.offsetAndRotation(45.6957F, -12.3757F, -10.1514F, 1.15F, 1.5708F, 0F));
        p_pelvis.addOrReplaceChild("molino_der", CubeListBuilder.create()
                .texOffs(78, 163).addBox(-2.4F, 0F, -0.8F, 4.8F, 6.4F, 1.6F)
                .texOffs(162, 148).addBox(-0.8F, 5.12F, -2.4F, 1.6F, 6.4F, 4.8F)
                .texOffs(78, 163).addBox(-2.4F, 10.24F, -0.8F, 4.8F, 6.4F, 1.6F)
                .texOffs(162, 148).addBox(-0.8F, 15.36F, -2.4F, 1.6F, 6.4F, 4.8F)
                .texOffs(78, 163).addBox(-2.4F, 20.48F, -0.8F, 4.8F, 6.4F, 1.6F)
                .texOffs(162, 148).addBox(-0.8F, 25.6F, -2.4F, 1.6F, 6.4F, 4.8F)
                .texOffs(78, 163).addBox(-2.4F, 30.72F, -0.8F, 4.8F, 6.4F, 1.6F)
                .texOffs(162, 148).addBox(-0.8F, 35.84F, -2.4F, 1.6F, 6.4F, 4.8F)
                .texOffs(78, 163).addBox(-2.4F, 40.96F, -0.8F, 4.8F, 6.4F, 1.6F)
                .texOffs(162, 148).addBox(-0.8F, 46.08F, -2.4F, 1.6F, 6.4F, 4.8F)
                .texOffs(78, 163).addBox(-2.4F, 51.2F, -0.8F, 4.8F, 6.4F, 1.6F)
                .texOffs(162, 148).addBox(-0.8F, 56.32F, -2.4F, 1.6F, 6.4F, 4.8F)
                .texOffs(78, 163).addBox(-2.4F, 61.44F, -0.8F, 4.8F, 6.4F, 1.6F)
                .texOffs(162, 148).addBox(-0.8F, 66.56F, -2.4F, 1.6F, 6.4F, 4.8F)
                .texOffs(78, 163).addBox(-2.4F, 71.68F, -0.8F, 4.8F, 6.4F, 1.6F)
                .texOffs(162, 148).addBox(-0.8F, 76.8F, -2.4F, 1.6F, 6.4F, 4.8F)
                .texOffs(78, 163).addBox(-2.4F, 81.92F, -0.8F, 4.8F, 6.4F, 1.6F)
                .texOffs(162, 148).addBox(-0.8F, 87.04F, -2.4F, 1.6F, 6.4F, 4.8F)
                .texOffs(78, 163).addBox(-2.4F, 92.16F, -0.8F, 4.8F, 6.4F, 1.6F)
                .texOffs(162, 148).addBox(-0.8F, 97.28F, -2.4F, 1.6F, 6.4F, 4.8F),
                PartPose.offsetAndRotation(-46.1161F, -12.2636F, -8.4176F, 1.1493F, -1.5708F, 0F));
        return LayerDefinition.create(malla, 256, 256);
    }
}
