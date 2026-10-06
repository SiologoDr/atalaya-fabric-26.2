package com.atalaya.client;

import net.minecraft.client.model.geom.PartPose;
import net.minecraft.client.model.geom.builders.CubeDeformation;
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
        return crear(CubeDeformation.NONE);
    }

    /** La misma malla hinchada: la capa del aura de la Furia (como las de Rajang y Aeralis). */
    public static LayerDefinition crearAura() {
        return crear(new CubeDeformation(1.2F));
    }

    private static LayerDefinition crear(CubeDeformation infla) {
        MeshDefinition malla = new MeshDefinition();
        PartDefinition p_root = malla.getRoot();
        PartDefinition p_pelvis = p_root.addOrReplaceChild("pelvis", CubeListBuilder.create()
                .texOffs(106, 130).addBox(-10F, -4F, -6F, 20F, 8F, 12F, infla)
                .texOffs(138, 156).addBox(-11F, 2F, -6.5F, 22F, 4F, 13F, infla),
                PartPose.offsetAndRotation(0F, -12F, 0F, 0F, 0F, 0F));
        p_pelvis.addOrReplaceChild("algas_del", CubeListBuilder.create()
                .texOffs(47, 156).addBox(-10F, -2.7F, 0F, 3F, 18.9F, 0F, infla)
                .texOffs(84, 100).addBox(-2F, -2.7F, 0F, 3F, 28.35F, 0F, infla)
                .texOffs(200, 100).addBox(6F, -2.7F, 0F, 3F, 25.65F, 0F, infla),
                PartPose.offsetAndRotation(0F, 5F, -6.3F, 0F, 0F, 0F));
        p_pelvis.addOrReplaceChild("algas_tras", CubeListBuilder.create()
                .texOffs(131, 156).addBox(-6F, -2.7F, 0F, 3F, 17.55F, 0F, infla)
                .texOffs(0, 130).addBox(2F, -2.7F, 0F, 3F, 24.3F, 0F, infla)
                .texOffs(99, 130).addBox(10F, -2.7F, 0F, 3F, 20.25F, 0F, infla),
                PartPose.offsetAndRotation(0F, 5F, 6.3F, 0F, 0F, 0F));
        PartDefinition p_pierna_izq = p_pelvis.addOrReplaceChild("pierna_izq", CubeListBuilder.create()
                .texOffs(148, 100).addBox(-5.49F, 0F, -5.49F, 10.98F, 16F, 10.98F, infla),
                PartPose.offsetAndRotation(6F, 2F, 0F, -0.1047F, 0F, 0F));
        PartDefinition p_espinilla_izq = p_pierna_izq.addOrReplaceChild("espinilla_izq", CubeListBuilder.create()
                .texOffs(7, 130).addBox(-4.27F, 0F, -4.27F, 8.54F, 15F, 8.54F, infla)
                .texOffs(224, 212).addBox(-4.88F, 1F, -5.612F, 9.76F, 9F, 2.44F, infla),
                PartPose.offsetAndRotation(0F, 16F, 0F, 0.1745F, 0F, 0F));
        p_espinilla_izq.addOrReplaceChild("pie_izq", CubeListBuilder.create()
                .texOffs(0, 176).addBox(-5.49F, 0F, -8.54F, 10.98F, 3F, 13.42F, infla),
                PartPose.offsetAndRotation(0F, 15F, 0F, -0.0698F, 0F, 0F));
        PartDefinition p_pierna_der = p_pelvis.addOrReplaceChild("pierna_der", CubeListBuilder.create()
                .texOffs(148, 100).addBox(-5.49F, 0F, -5.49F, 10.98F, 16F, 10.98F, infla),
                PartPose.offsetAndRotation(-6F, 2F, 0F, -0.1047F, 0F, 0F));
        PartDefinition p_espinilla_der = p_pierna_der.addOrReplaceChild("espinilla_der", CubeListBuilder.create()
                .texOffs(7, 130).addBox(-4.27F, 0F, -4.27F, 8.54F, 15F, 8.54F, infla)
                .texOffs(224, 212).addBox(-4.88F, 1F, -5.612F, 9.76F, 9F, 2.44F, infla),
                PartPose.offsetAndRotation(0F, 16F, 0F, 0.1745F, 0F, 0F));
        p_espinilla_der.addOrReplaceChild("pie_der", CubeListBuilder.create()
                .texOffs(0, 176).addBox(-5.49F, 0F, -8.54F, 10.98F, 3F, 13.42F, infla),
                PartPose.offsetAndRotation(0F, 15F, 0F, -0.0698F, 0F, 0F));
        PartDefinition p_torso = p_pelvis.addOrReplaceChild("torso", CubeListBuilder.create()
                .texOffs(51, 0).addBox(-12F, -28F, -6F, 24F, 28F, 13F, infla)
                .texOffs(126, 0).addBox(-12.5F, -28.5F, 0F, 25F, 29F, 7.5F, infla)
                .texOffs(13, 194).addBox(-12.5F, -9F, -7F, 25F, 9F, 7F, infla)
                .texOffs(76, 250).addBox(-9F, -27F, 7F, 3F, 3F, 2F, infla)
                .texOffs(76, 250).addBox(5F, -12F, 7F, 3F, 3F, 2F, infla),
                PartPose.offsetAndRotation(0F, -4F, 0F, 0.2443F, 0F, 0F));
        p_torso.addOrReplaceChild("costillas", CubeListBuilder.create()
                .texOffs(186, 250).addBox(-9F, -24.5F, -8.6F, 18F, 1.4F, 1.6F, infla)
                .texOffs(186, 250).addBox(-9F, -20.3F, -8.6F, 18F, 1.4F, 1.6F, infla)
                .texOffs(186, 250).addBox(-9F, -16.1F, -8.6F, 18F, 1.4F, 1.6F, infla)
                .texOffs(186, 250).addBox(-9F, -11.9F, -8.6F, 18F, 1.4F, 1.6F, infla)
                .texOffs(171, 130).addBox(-1.5F, -27F, -8.9F, 3F, 18F, 1.4F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        PartDefinition p_corazon = p_torso.addOrReplaceChild("corazon", CubeListBuilder.create(),
                PartPose.offsetAndRotation(0F, -17.5F, -5.2F, 0F, 0F, 0F));
        p_corazon.addOrReplaceChild("corazon_1", CubeListBuilder.create()
                .texOffs(87, 176).addBox(-5F, -5.5F, -3F, 10F, 11F, 6F, infla)
                .texOffs(148, 241).addBox(-3F, -7.5F, -2.4F, 6F, 2F, 4F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        p_corazon.addOrReplaceChild("corazon_2", CubeListBuilder.create()
                .texOffs(120, 176).addBox(-5F, -5.5F, -3F, 10F, 11F, 6F, infla)
                .texOffs(169, 241).addBox(-3F, -7.5F, -2.4F, 6F, 2F, 4F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        p_corazon.addOrReplaceChild("corazon_3", CubeListBuilder.create()
                .texOffs(153, 176).addBox(-5F, -5.5F, -3F, 10F, 11F, 6F, infla)
                .texOffs(190, 241).addBox(-3F, -7.5F, -2.4F, 6F, 2F, 4F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        p_corazon.addOrReplaceChild("corazon_4", CubeListBuilder.create()
                .texOffs(186, 176).addBox(-5F, -5.5F, -3F, 10F, 11F, 6F, infla)
                .texOffs(211, 241).addBox(-3F, -7.5F, -2.4F, 6F, 2F, 4F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        p_corazon.addOrReplaceChild("corazon_libre", CubeListBuilder.create()
                .texOffs(219, 176).addBox(-5F, -5.5F, -3F, 10F, 11F, 6F, infla)
                .texOffs(232, 241).addBox(-3F, -7.5F, -2.4F, 6F, 2F, 4F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        p_torso.addOrReplaceChild("cadena_1", CubeListBuilder.create()
                .texOffs(25, 250).addBox(-1.65F, 0F, -0.55F, 3.3F, 4.4F, 1.1F, infla)
                .texOffs(48, 241).addBox(-0.55F, 3.52F, -1.65F, 1.1F, 4.4F, 3.3F, infla)
                .texOffs(25, 250).addBox(-1.65F, 7.04F, -0.55F, 3.3F, 4.4F, 1.1F, infla)
                .texOffs(48, 241).addBox(-0.55F, 10.56F, -1.65F, 1.1F, 4.4F, 3.3F, infla)
                .texOffs(25, 250).addBox(-1.65F, 14.08F, -0.55F, 3.3F, 4.4F, 1.1F, infla)
                .texOffs(48, 241).addBox(-0.55F, 17.6F, -1.65F, 1.1F, 4.4F, 3.3F, infla)
                .texOffs(25, 250).addBox(-1.65F, 21.12F, -0.55F, 3.3F, 4.4F, 1.1F, infla)
                .texOffs(48, 241).addBox(-0.55F, 24.64F, -1.65F, 1.1F, 4.4F, 3.3F, infla)
                .texOffs(25, 250).addBox(-1.65F, 28.16F, -0.55F, 3.3F, 4.4F, 1.1F, infla),
                PartPose.offsetAndRotation(-11F, -27F, -9.6F, 0.8086F, 1.5708F, 0F));
        p_torso.addOrReplaceChild("cadena_2", CubeListBuilder.create()
                .texOffs(25, 250).addBox(-1.65F, 0F, -0.55F, 3.3F, 4.4F, 1.1F, infla)
                .texOffs(48, 241).addBox(-0.55F, 3.52F, -1.65F, 1.1F, 4.4F, 3.3F, infla)
                .texOffs(25, 250).addBox(-1.65F, 7.04F, -0.55F, 3.3F, 4.4F, 1.1F, infla)
                .texOffs(48, 241).addBox(-0.55F, 10.56F, -1.65F, 1.1F, 4.4F, 3.3F, infla)
                .texOffs(25, 250).addBox(-1.65F, 14.08F, -0.55F, 3.3F, 4.4F, 1.1F, infla)
                .texOffs(48, 241).addBox(-0.55F, 17.6F, -1.65F, 1.1F, 4.4F, 3.3F, infla)
                .texOffs(25, 250).addBox(-1.65F, 21.12F, -0.55F, 3.3F, 4.4F, 1.1F, infla)
                .texOffs(48, 241).addBox(-0.55F, 24.64F, -1.65F, 1.1F, 4.4F, 3.3F, infla)
                .texOffs(25, 250).addBox(-1.65F, 28.16F, -0.55F, 3.3F, 4.4F, 1.1F, infla),
                PartPose.offsetAndRotation(11F, -27F, -9.6F, 0.8086F, -1.5708F, 0F));
        p_torso.addOrReplaceChild("cadena_3", CubeListBuilder.create()
                .texOffs(87, 250).addBox(-1.5F, 0F, -0.5F, 3F, 4F, 1F, infla)
                .texOffs(111, 241).addBox(-0.5F, 3.2F, -1.5F, 1F, 4F, 3F, infla)
                .texOffs(87, 250).addBox(-1.5F, 6.4F, -0.5F, 3F, 4F, 1F, infla)
                .texOffs(111, 241).addBox(-0.5F, 9.6F, -1.5F, 1F, 4F, 3F, infla)
                .texOffs(87, 250).addBox(-1.5F, 12.8F, -0.5F, 3F, 4F, 1F, infla)
                .texOffs(111, 241).addBox(-0.5F, 16F, -1.5F, 1F, 4F, 3F, infla)
                .texOffs(87, 250).addBox(-1.5F, 19.2F, -0.5F, 3F, 4F, 1F, infla)
                .texOffs(111, 241).addBox(-0.5F, 22.4F, -1.5F, 1F, 4F, 3F, infla),
                PartPose.offsetAndRotation(-12.5F, -4F, -7.6F, 1.5708F, 1.5708F, 0F));
        p_torso.addOrReplaceChild("cadena_4", CubeListBuilder.create()
                .texOffs(87, 250).addBox(-1.5F, 0F, -0.5F, 3F, 4F, 1F, infla)
                .texOffs(111, 241).addBox(-0.5F, 3.2F, -1.5F, 1F, 4F, 3F, infla)
                .texOffs(87, 250).addBox(-1.5F, 6.4F, -0.5F, 3F, 4F, 1F, infla)
                .texOffs(111, 241).addBox(-0.5F, 9.6F, -1.5F, 1F, 4F, 3F, infla)
                .texOffs(87, 250).addBox(-1.5F, 12.8F, -0.5F, 3F, 4F, 1F, infla)
                .texOffs(111, 241).addBox(-0.5F, 16F, -1.5F, 1F, 4F, 3F, infla)
                .texOffs(87, 250).addBox(-1.5F, 19.2F, -0.5F, 3F, 4F, 1F, infla)
                .texOffs(111, 241).addBox(-0.5F, 22.4F, -1.5F, 1F, 4F, 3F, infla),
                PartPose.offsetAndRotation(-12F, -26.4F, -9.9F, 1.5708F, 1.5708F, 0F));
        PartDefinition p_cuello = p_torso.addOrReplaceChild("cuello", CubeListBuilder.create()
                .texOffs(21, 228).addBox(-3F, -5F, -3F, 6F, 5F, 6F, infla),
                PartPose.offsetAndRotation(0F, -28F, -2F, -0.2094F, 0F, 0F));
        PartDefinition p_cabeza = p_cuello.addOrReplaceChild("cabeza", CubeListBuilder.create()
                .texOffs(91, 100).addBox(-7F, -13F, -7F, 14F, 13F, 14F, infla)
                .texOffs(61, 156).addBox(-7.5F, -14F, -7.5F, 15F, 3F, 15F, infla)
                .texOffs(141, 250).addBox(-5.5F, -7.5F, -7.3F, 3.5F, 3F, 0.6F, infla)
                .texOffs(141, 250).addBox(2F, -7.5F, -7.3F, 3.5F, 3F, 0.6F, infla)
                .texOffs(227, 250).addBox(-1F, -4.5F, -7.2F, 2F, 2F, 0.4F, infla),
                PartPose.offsetAndRotation(0F, -5F, 0F, -0.0698F, 0F, 0F));
        p_cabeza.addOrReplaceChild("ojo_izq", CubeListBuilder.create()
                .texOffs(151, 250).addBox(-1.6875F, -1.35F, -0.54F, 3.375F, 2.7F, 1.08F, infla),
                PartPose.offsetAndRotation(3.75F, -6F, -7.6F, 0F, 0F, 0F));
        p_cabeza.addOrReplaceChild("ojo_der", CubeListBuilder.create()
                .texOffs(151, 250).addBox(-1.6875F, -1.35F, -0.54F, 3.375F, 2.7F, 1.08F, infla),
                PartPose.offsetAndRotation(-3.75F, -6F, -7.6F, 0F, 0F, 0F));
        PartDefinition p_mandibula = p_cabeza.addOrReplaceChild("mandibula", CubeListBuilder.create()
                .texOffs(0, 212).addBox(-6F, 0F, -11F, 12F, 4F, 11F, infla)
                .texOffs(233, 250).addBox(-5F, -1.3F, -10.8F, 1.2F, 1.5F, 1.2F, infla)
                .texOffs(233, 250).addBox(-2.8F, -1.3F, -10.8F, 1.2F, 1.5F, 1.2F, infla)
                .texOffs(233, 250).addBox(-0.6F, -1.3F, -10.8F, 1.2F, 1.5F, 1.2F, infla)
                .texOffs(233, 250).addBox(1.6F, -1.3F, -10.8F, 1.2F, 1.5F, 1.2F, infla)
                .texOffs(233, 250).addBox(3.8F, -1.3F, -10.8F, 1.2F, 1.5F, 1.2F, infla),
                PartPose.offsetAndRotation(0F, 0F, 3F, 0F, 0F, 0F));
        p_cabeza.addOrReplaceChild("puas_0", CubeListBuilder.create()
                .texOffs(145, 212).addBox(-1F, -11.4F, -1F, 2F, 11.4F, 2F, infla),
                PartPose.offsetAndRotation(-6F, -14F, -6F, -0.1745F, 0F, -0.2094F));
        p_cabeza.addOrReplaceChild("puas_1", CubeListBuilder.create()
                .texOffs(122, 156).addBox(-1F, -15.2F, -1F, 2F, 15.2F, 2F, infla),
                PartPose.offsetAndRotation(0F, -14F, -7F, -0.2443F, 0F, 0F));
        p_cabeza.addOrReplaceChild("puas_2", CubeListBuilder.create()
                .texOffs(90, 130).addBox(-1F, -19F, -1F, 2F, 19F, 2F, infla),
                PartPose.offsetAndRotation(6F, -14F, -6F, -0.1745F, 0F, 0.2094F));
        p_cabeza.addOrReplaceChild("puas_3", CubeListBuilder.create()
                .texOffs(145, 212).addBox(-1F, -11.4F, -1F, 2F, 11.4F, 2F, infla),
                PartPose.offsetAndRotation(-6.5F, -14F, 0F, 0F, 0F, -0.2793F));
        p_cabeza.addOrReplaceChild("puas_4", CubeListBuilder.create()
                .texOffs(122, 156).addBox(-1F, -15.2F, -1F, 2F, 15.2F, 2F, infla),
                PartPose.offsetAndRotation(6.5F, -14F, 0F, 0F, 0F, 0.2793F));
        p_cabeza.addOrReplaceChild("puas_5", CubeListBuilder.create()
                .texOffs(90, 130).addBox(-1F, -19F, -1F, 2F, 19F, 2F, infla),
                PartPose.offsetAndRotation(0F, -14F, 6F, 0.2094F, 0F, 0F));
        PartDefinition p_corona_c1 = p_cabeza.addOrReplaceChild("corona_c1", CubeListBuilder.create()
                .texOffs(38, 156).addBox(-1F, -17F, -1F, 2F, 17F, 2F, infla),
                PartPose.offsetAndRotation(-4F, -14F, -3F, -0.1047F, 0F, -0.3142F));
        p_corona_c1.addOrReplaceChild("corona_c1_a", CubeListBuilder.create()
                .texOffs(99, 228).addBox(-0.75F, -8.5F, -0.75F, 1.5F, 8.5F, 1.5F, infla),
                PartPose.offsetAndRotation(0F, -9.35F, 0F, 0F, 0F, 0.6632F));
        p_corona_c1.addOrReplaceChild("corona_c1_b", CubeListBuilder.create()
                .texOffs(163, 228).addBox(-0.75F, -6.8F, -0.75F, 1.5F, 6.8F, 1.5F, infla),
                PartPose.offsetAndRotation(0F, -12.75F, 0F, 0F, 0F, -0.5934F));
        PartDefinition p_corona_c2 = p_cabeza.addOrReplaceChild("corona_c2", CubeListBuilder.create()
                .texOffs(194, 194).addBox(-1F, -13.6F, -1F, 2F, 13.6F, 2F, infla),
                PartPose.offsetAndRotation(3F, -14F, 2F, 0.1396F, 0F, 0.384F));
        p_corona_c2.addOrReplaceChild("corona_c2_a", CubeListBuilder.create()
                .texOffs(170, 228).addBox(-0.75F, -6.8F, -0.75F, 1.5F, 6.8F, 1.5F, infla),
                PartPose.offsetAndRotation(0F, -7.48F, 0F, 0F, 0F, 0.6632F));
        p_corona_c2.addOrReplaceChild("corona_c2_b", CubeListBuilder.create()
                .texOffs(120, 241).addBox(-0.75F, -5.44F, -0.75F, 1.5F, 5.44F, 1.5F, infla),
                PartPose.offsetAndRotation(0F, -10.2F, 0F, 0F, 0F, -0.5934F));
        PartDefinition p_corona_c3 = p_cabeza.addOrReplaceChild("corona_c3", CubeListBuilder.create()
                .texOffs(154, 212).addBox(-1F, -11.9F, -1F, 2F, 11.9F, 2F, infla),
                PartPose.offsetAndRotation(5F, -14F, -4F, -0.2094F, 0F, 0.5236F));
        p_corona_c3.addOrReplaceChild("corona_c3_a", CubeListBuilder.create()
                .texOffs(58, 241).addBox(-0.75F, -5.95F, -0.75F, 1.5F, 5.95F, 1.5F, infla),
                PartPose.offsetAndRotation(0F, -6.545F, 0F, 0F, 0F, 0.6632F));
        p_corona_c3.addOrReplaceChild("corona_c3_b", CubeListBuilder.create()
                .texOffs(127, 241).addBox(-0.75F, -4.76F, -0.75F, 1.5F, 4.76F, 1.5F, infla),
                PartPose.offsetAndRotation(0F, -8.925F, 0F, 0F, 0F, -0.5934F));
        PartDefinition p_corona_c4 = p_cabeza.addOrReplaceChild("corona_c4", CubeListBuilder.create()
                .texOffs(173, 212).addBox(-1F, -10.2F, -1F, 2F, 10.2F, 2F, infla),
                PartPose.offsetAndRotation(-2F, -14F, 5F, 0.2793F, 0F, -0.1396F));
        p_corona_c4.addOrReplaceChild("corona_c4_a", CubeListBuilder.create()
                .texOffs(134, 241).addBox(-0.75F, -5.1F, -0.75F, 1.5F, 5.1F, 1.5F, infla),
                PartPose.offsetAndRotation(0F, -5.61F, 0F, 0F, 0F, 0.6632F));
        p_corona_c4.addOrReplaceChild("corona_c4_b", CubeListBuilder.create()
                .texOffs(54, 250).addBox(-0.75F, -4.08F, -0.75F, 1.5F, 4.08F, 1.5F, infla),
                PartPose.offsetAndRotation(0F, -7.65F, 0F, 0F, 0F, -0.5934F));
        PartDefinition p_hombro_izq = p_torso.addOrReplaceChild("hombro_izq", CubeListBuilder.create()
                .texOffs(0, 100).addBox(-8.45F, -6.5F, -8.45F, 16.9F, 11.7F, 16.9F, infla)
                .texOffs(78, 194).addBox(-7.15F, -7.8F, -7.15F, 14.3F, 1.3F, 14.3F, infla)
                .texOffs(13, 250).addBox(2.6F, -9.1F, 2.6F, 2.6F, 2.6F, 2.6F, infla),
                PartPose.offsetAndRotation(15F, -25F, 0F, 0F, 0F, 0F));
        PartDefinition p_coral_h1_izq = p_hombro_izq.addOrReplaceChild("coral_h1_izq", CubeListBuilder.create()
                .texOffs(203, 194).addBox(-1F, -13.5F, -1F, 2F, 13.5F, 2F, infla),
                PartPose.offsetAndRotation(2F, -6F, -2F, 0.1396F, 0F, 0.1745F));
        p_coral_h1_izq.addOrReplaceChild("coral_h1_izq_a", CubeListBuilder.create()
                .texOffs(14, 228).addBox(-0.75F, -10.125F, -0.75F, 1.5F, 10.125F, 1.5F, infla),
                PartPose.offsetAndRotation(0F, -7.425F, 0F, 0F, 0F, 0.6632F));
        p_coral_h1_izq.addOrReplaceChild("coral_h1_izq_b", CubeListBuilder.create()
                .texOffs(106, 228).addBox(-0.75F, -8.1F, -0.75F, 1.5F, 8.1F, 1.5F, infla),
                PartPose.offsetAndRotation(0F, -10.125F, 0F, 0F, 0F, -0.5934F));
        PartDefinition p_coral_h2_izq = p_hombro_izq.addOrReplaceChild("coral_h2_izq", CubeListBuilder.create()
                .texOffs(78, 228).addBox(-1F, -9F, -1F, 2F, 9F, 2F, infla),
                PartPose.offsetAndRotation(-3F, -6F, 3F, -0.1745F, 0F, -0.2443F));
        p_coral_h2_izq.addOrReplaceChild("coral_h2_izq_a", CubeListBuilder.create()
                .texOffs(177, 228).addBox(-0.75F, -6.75F, -0.75F, 1.5F, 6.75F, 1.5F, infla),
                PartPose.offsetAndRotation(0F, -4.95F, 0F, 0F, 0F, 0.6632F));
        p_coral_h2_izq.addOrReplaceChild("coral_h2_izq_b", CubeListBuilder.create()
                .texOffs(141, 241).addBox(-0.75F, -5.4F, -0.75F, 1.5F, 5.4F, 1.5F, infla),
                PartPose.offsetAndRotation(0F, -6.75F, 0F, 0F, 0F, -0.5934F));
        PartDefinition p_coral_h3_izq = p_hombro_izq.addOrReplaceChild("coral_h3_izq", CubeListBuilder.create()
                .texOffs(182, 212).addBox(-1F, -10.5F, -1F, 2F, 10.5F, 2F, infla),
                PartPose.offsetAndRotation(4F, -6F, 4F, -0.1047F, 0F, 0.384F));
        p_coral_h3_izq.addOrReplaceChild("coral_h3_izq_a", CubeListBuilder.create()
                .texOffs(113, 228).addBox(-0.75F, -7.875F, -0.75F, 1.5F, 7.875F, 1.5F, infla),
                PartPose.offsetAndRotation(0F, -5.775F, 0F, 0F, 0F, 0.6632F));
        p_coral_h3_izq.addOrReplaceChild("coral_h3_izq_b", CubeListBuilder.create()
                .texOffs(65, 241).addBox(-0.75F, -6.3F, -0.75F, 1.5F, 6.3F, 1.5F, infla),
                PartPose.offsetAndRotation(0F, -7.875F, 0F, 0F, 0F, -0.5934F));
        PartDefinition p_brazo_izq = p_hombro_izq.addOrReplaceChild("brazo_izq", CubeListBuilder.create()
                .texOffs(214, 100).addBox(-4.27F, 0F, -4.27F, 8.54F, 16F, 8.54F, infla)
                .texOffs(93, 212).addBox(-4.88F, 4F, -4.88F, 9.76F, 4F, 9.76F, infla),
                PartPose.offsetAndRotation(0F, 2F, 0F, -0.1047F, 0F, -0.0698F));
        PartDefinition p_antebrazo_izq = p_brazo_izq.addOrReplaceChild("antebrazo_izq", CubeListBuilder.create()
                .texOffs(59, 130).addBox(-3.66F, 0F, -3.66F, 7.32F, 15F, 7.32F, infla)
                .texOffs(50, 176).addBox(-4.392F, 6F, -4.392F, 8.784F, 8F, 8.784F, infla),
                PartPose.offsetAndRotation(0F, 16F, 0F, -0.2793F, 0F, 0F));
        PartDefinition p_mano_izq = p_antebrazo_izq.addOrReplaceChild("mano_izq", CubeListBuilder.create()
                .texOffs(47, 212).addBox(-4.27F, 0F, -4.27F, 8.54F, 6F, 8.54F, infla),
                PartPose.offsetAndRotation(0F, 15F, 0F, 0F, 0F, 0F));
        PartDefinition p_hombro_der = p_torso.addOrReplaceChild("hombro_der", CubeListBuilder.create()
                .texOffs(0, 100).addBox(-8.45F, -6.5F, -8.45F, 16.9F, 11.7F, 16.9F, infla)
                .texOffs(78, 194).addBox(-7.15F, -7.8F, -7.15F, 14.3F, 1.3F, 14.3F, infla)
                .texOffs(13, 250).addBox(-5.2F, -9.1F, 2.6F, 2.6F, 2.6F, 2.6F, infla),
                PartPose.offsetAndRotation(-15F, -25F, 0F, 0F, 0F, 0F));
        PartDefinition p_coral_h1_der = p_hombro_der.addOrReplaceChild("coral_h1_der", CubeListBuilder.create()
                .texOffs(203, 194).addBox(-1F, -13.5F, -1F, 2F, 13.5F, 2F, infla),
                PartPose.offsetAndRotation(-2F, -6F, -2F, 0.1396F, 0F, -0.1745F));
        p_coral_h1_der.addOrReplaceChild("coral_h1_der_a", CubeListBuilder.create()
                .texOffs(14, 228).addBox(-0.75F, -10.125F, -0.75F, 1.5F, 10.125F, 1.5F, infla),
                PartPose.offsetAndRotation(0F, -7.425F, 0F, 0F, 0F, 0.6632F));
        p_coral_h1_der.addOrReplaceChild("coral_h1_der_b", CubeListBuilder.create()
                .texOffs(106, 228).addBox(-0.75F, -8.1F, -0.75F, 1.5F, 8.1F, 1.5F, infla),
                PartPose.offsetAndRotation(0F, -10.125F, 0F, 0F, 0F, -0.5934F));
        PartDefinition p_coral_h2_der = p_hombro_der.addOrReplaceChild("coral_h2_der", CubeListBuilder.create()
                .texOffs(78, 228).addBox(-1F, -9F, -1F, 2F, 9F, 2F, infla),
                PartPose.offsetAndRotation(3F, -6F, 3F, -0.1745F, 0F, 0.2443F));
        p_coral_h2_der.addOrReplaceChild("coral_h2_der_a", CubeListBuilder.create()
                .texOffs(177, 228).addBox(-0.75F, -6.75F, -0.75F, 1.5F, 6.75F, 1.5F, infla),
                PartPose.offsetAndRotation(0F, -4.95F, 0F, 0F, 0F, 0.6632F));
        p_coral_h2_der.addOrReplaceChild("coral_h2_der_b", CubeListBuilder.create()
                .texOffs(141, 241).addBox(-0.75F, -5.4F, -0.75F, 1.5F, 5.4F, 1.5F, infla),
                PartPose.offsetAndRotation(0F, -6.75F, 0F, 0F, 0F, -0.5934F));
        PartDefinition p_coral_h3_der = p_hombro_der.addOrReplaceChild("coral_h3_der", CubeListBuilder.create()
                .texOffs(182, 212).addBox(-1F, -10.5F, -1F, 2F, 10.5F, 2F, infla),
                PartPose.offsetAndRotation(-4F, -6F, 4F, -0.1047F, 0F, -0.384F));
        p_coral_h3_der.addOrReplaceChild("coral_h3_der_a", CubeListBuilder.create()
                .texOffs(113, 228).addBox(-0.75F, -7.875F, -0.75F, 1.5F, 7.875F, 1.5F, infla),
                PartPose.offsetAndRotation(0F, -5.775F, 0F, 0F, 0F, 0.6632F));
        p_coral_h3_der.addOrReplaceChild("coral_h3_der_b", CubeListBuilder.create()
                .texOffs(65, 241).addBox(-0.75F, -6.3F, -0.75F, 1.5F, 6.3F, 1.5F, infla),
                PartPose.offsetAndRotation(0F, -7.875F, 0F, 0F, 0F, -0.5934F));
        PartDefinition p_brazo_der = p_hombro_der.addOrReplaceChild("brazo_der", CubeListBuilder.create()
                .texOffs(214, 100).addBox(-4.27F, 0F, -4.27F, 8.54F, 16F, 8.54F, infla)
                .texOffs(93, 212).addBox(-4.88F, 4F, -4.88F, 9.76F, 4F, 9.76F, infla),
                PartPose.offsetAndRotation(0F, 2F, 0F, -0.4189F, 0F, 0.1047F));
        PartDefinition p_antebrazo_der = p_brazo_der.addOrReplaceChild("antebrazo_der", CubeListBuilder.create()
                .texOffs(59, 130).addBox(-3.66F, 0F, -3.66F, 7.32F, 15F, 7.32F, infla)
                .texOffs(50, 176).addBox(-4.392F, 6F, -4.392F, 8.784F, 8F, 8.784F, infla),
                PartPose.offsetAndRotation(0F, 16F, 0F, -1.0821F, 0F, 0F));
        PartDefinition p_mano_der = p_antebrazo_der.addOrReplaceChild("mano_der", CubeListBuilder.create()
                .texOffs(47, 212).addBox(-4.27F, 0F, -4.27F, 8.54F, 6F, 8.54F, infla),
                PartPose.offsetAndRotation(0F, 15F, 0F, 0F, 0F, 0F));
        PartDefinition p_cadena_mano = p_mano_izq.addOrReplaceChild("cadena_mano", CubeListBuilder.create()
                .texOffs(87, 241).addBox(-1.95F, 0F, -0.65F, 3.9F, 5.2F, 1.3F, infla)
                .texOffs(87, 228).addBox(-0.65F, 4.16F, -1.95F, 1.3F, 5.2F, 3.9F, infla)
                .texOffs(87, 241).addBox(-1.95F, 8.32F, -0.65F, 3.9F, 5.2F, 1.3F, infla)
                .texOffs(87, 228).addBox(-0.65F, 12.48F, -1.95F, 1.3F, 5.2F, 3.9F, infla),
                PartPose.offsetAndRotation(0F, 5F, 0F, 0.3218F, 0F, 0F));
        PartDefinition p_gancho_mano = p_cadena_mano.addOrReplaceChild("gancho_mano", CubeListBuilder.create()
                .texOffs(61, 250).addBox(-2.6F, -2.5F, -0.9F, 5.2F, 3F, 1.8F, infla)
                .texOffs(182, 194).addBox(-1.3F, 0F, -1.3F, 2.6F, 13F, 2.6F, infla)
                .texOffs(0, 156).addBox(-1.1F, 2.5F, -8F, 2.2F, 2.2F, 16F, infla)
                .texOffs(237, 228).addBox(-2F, 12F, -2F, 4F, 3.5F, 4F, infla)
                .texOffs(161, 250).addBox(-1F, 5F, 1.2F, 2F, 2F, 2F, infla)
                .texOffs(170, 250).addBox(0.6F, 9F, -2.2F, 2F, 2F, 1.5F, infla),
                PartPose.offsetAndRotation(0F, 15.8114F, 0F, 0F, 0F, 0F));
        p_gancho_mano.addOrReplaceChild("gancho_mano_a", CubeListBuilder.create()
                .texOffs(134, 212).addBox(-1.2F, 0F, -1.2F, 2.4F, 11F, 2.4F, infla)
                .texOffs(142, 228).addBox(-3.4F, 7F, -1.4F, 6.8F, 6F, 2.8F, infla),
                PartPose.offsetAndRotation(0F, 14F, 0F, 0F, 0F, 2.234F));
        p_gancho_mano.addOrReplaceChild("gancho_mano_b", CubeListBuilder.create()
                .texOffs(134, 212).addBox(-1.2F, 0F, -1.2F, 2.4F, 11F, 2.4F, infla)
                .texOffs(142, 228).addBox(-3.4F, 7F, -1.4F, 6.8F, 6F, 2.8F, infla),
                PartPose.offsetAndRotation(0F, 14F, 0F, 0F, 0F, -2.234F));
        PartDefinition p_tridente = p_mano_der.addOrReplaceChild("tridente", CubeListBuilder.create()
                .texOffs(0, 0).addBox(-1.3F, -30F, -1.3F, 2.6F, 96F, 2.6F, infla)
                .texOffs(0, 241).addBox(-2F, 64F, -2F, 4F, 4F, 4F, infla)
                .texOffs(184, 228).addBox(-11F, 67F, -2F, 22F, 3.5F, 4F, infla)
                .texOffs(43, 130).addBox(-1.8F, 70F, -1.8F, 3.6F, 20F, 3.6F, infla)
                .texOffs(0, 194).addBox(-10.5F, 70F, -1.5F, 3F, 14F, 3F, infla)
                .texOffs(0, 194).addBox(7.5F, 70F, -1.5F, 3F, 14F, 3F, infla)
                .texOffs(35, 250).addBox(-4.5F, 81F, -1F, 2.5F, 4F, 2F, infla)
                .texOffs(35, 250).addBox(2F, 81F, -1F, 2.5F, 4F, 2F, infla)
                .texOffs(45, 250).addBox(-11.5F, 81F, -1F, 2F, 4F, 2F, infla)
                .texOffs(45, 250).addBox(9.5F, 81F, -1F, 2F, 4F, 2F, infla),
                PartPose.offsetAndRotation(0F, 4F, 0F, -1.2399F, 0F, 2.8241F));
        PartDefinition p_molino_izq = p_pelvis.addOrReplaceChild("molino_izq", CubeListBuilder.create()
                .texOffs(34, 241).addBox(-2.4F, 0F, -0.8F, 4.8F, 6.4F, 1.6F, infla)
                .texOffs(0, 228).addBox(-0.8F, 5.12F, -2.4F, 1.6F, 6.4F, 4.8F, infla)
                .texOffs(34, 241).addBox(-2.4F, 10.24F, -0.8F, 4.8F, 6.4F, 1.6F, infla)
                .texOffs(0, 228).addBox(-0.8F, 15.36F, -2.4F, 1.6F, 6.4F, 4.8F, infla)
                .texOffs(34, 241).addBox(-2.4F, 20.48F, -0.8F, 4.8F, 6.4F, 1.6F, infla)
                .texOffs(0, 228).addBox(-0.8F, 25.6F, -2.4F, 1.6F, 6.4F, 4.8F, infla)
                .texOffs(34, 241).addBox(-2.4F, 30.72F, -0.8F, 4.8F, 6.4F, 1.6F, infla)
                .texOffs(0, 228).addBox(-0.8F, 35.84F, -2.4F, 1.6F, 6.4F, 4.8F, infla)
                .texOffs(34, 241).addBox(-2.4F, 40.96F, -0.8F, 4.8F, 6.4F, 1.6F, infla)
                .texOffs(0, 228).addBox(-0.8F, 46.08F, -2.4F, 1.6F, 6.4F, 4.8F, infla)
                .texOffs(34, 241).addBox(-2.4F, 51.2F, -0.8F, 4.8F, 6.4F, 1.6F, infla)
                .texOffs(0, 228).addBox(-0.8F, 56.32F, -2.4F, 1.6F, 6.4F, 4.8F, infla)
                .texOffs(34, 241).addBox(-2.4F, 61.44F, -0.8F, 4.8F, 6.4F, 1.6F, infla),
                PartPose.offsetAndRotation(45.6957F, -12.3757F, -10.1514F, 0.8458F, 1.5708F, 0F));
        PartDefinition p_ancla_molino_izq = p_molino_izq.addOrReplaceChild("ancla_molino_izq", CubeListBuilder.create()
                .texOffs(61, 250).addBox(-2.6F, -2.5F, -0.9F, 5.2F, 3F, 1.8F, infla)
                .texOffs(182, 194).addBox(-1.3F, 0F, -1.3F, 2.6F, 13F, 2.6F, infla)
                .texOffs(0, 156).addBox(-1.1F, 2.5F, -8F, 2.2F, 2.2F, 16F, infla)
                .texOffs(237, 228).addBox(-2F, 12F, -2F, 4F, 3.5F, 4F, infla)
                .texOffs(161, 250).addBox(-1F, 5F, 1.2F, 2F, 2F, 2F, infla)
                .texOffs(170, 250).addBox(0.6F, 9F, -2.2F, 2F, 2F, 1.5F, infla),
                PartPose.offsetAndRotation(0F, 63.6446F, 0F, 0F, 0F, 0F));
        p_ancla_molino_izq.addOrReplaceChild("ancla_molino_izq_a", CubeListBuilder.create()
                .texOffs(134, 212).addBox(-1.2F, 0F, -1.2F, 2.4F, 11F, 2.4F, infla)
                .texOffs(142, 228).addBox(-3.4F, 7F, -1.4F, 6.8F, 6F, 2.8F, infla),
                PartPose.offsetAndRotation(0F, 14F, 0F, 0F, 0F, 2.234F));
        p_ancla_molino_izq.addOrReplaceChild("ancla_molino_izq_b", CubeListBuilder.create()
                .texOffs(134, 212).addBox(-1.2F, 0F, -1.2F, 2.4F, 11F, 2.4F, infla)
                .texOffs(142, 228).addBox(-3.4F, 7F, -1.4F, 6.8F, 6F, 2.8F, infla),
                PartPose.offsetAndRotation(0F, 14F, 0F, 0F, 0F, -2.234F));
        PartDefinition p_molino_der = p_pelvis.addOrReplaceChild("molino_der", CubeListBuilder.create()
                .texOffs(34, 241).addBox(-2.4F, 0F, -0.8F, 4.8F, 6.4F, 1.6F, infla)
                .texOffs(0, 228).addBox(-0.8F, 5.12F, -2.4F, 1.6F, 6.4F, 4.8F, infla)
                .texOffs(34, 241).addBox(-2.4F, 10.24F, -0.8F, 4.8F, 6.4F, 1.6F, infla)
                .texOffs(0, 228).addBox(-0.8F, 15.36F, -2.4F, 1.6F, 6.4F, 4.8F, infla)
                .texOffs(34, 241).addBox(-2.4F, 20.48F, -0.8F, 4.8F, 6.4F, 1.6F, infla)
                .texOffs(0, 228).addBox(-0.8F, 25.6F, -2.4F, 1.6F, 6.4F, 4.8F, infla)
                .texOffs(34, 241).addBox(-2.4F, 30.72F, -0.8F, 4.8F, 6.4F, 1.6F, infla)
                .texOffs(0, 228).addBox(-0.8F, 35.84F, -2.4F, 1.6F, 6.4F, 4.8F, infla)
                .texOffs(34, 241).addBox(-2.4F, 40.96F, -0.8F, 4.8F, 6.4F, 1.6F, infla)
                .texOffs(0, 228).addBox(-0.8F, 46.08F, -2.4F, 1.6F, 6.4F, 4.8F, infla)
                .texOffs(34, 241).addBox(-2.4F, 51.2F, -0.8F, 4.8F, 6.4F, 1.6F, infla)
                .texOffs(0, 228).addBox(-0.8F, 56.32F, -2.4F, 1.6F, 6.4F, 4.8F, infla)
                .texOffs(34, 241).addBox(-2.4F, 61.44F, -0.8F, 4.8F, 6.4F, 1.6F, infla),
                PartPose.offsetAndRotation(-46.1161F, -12.2636F, -8.4176F, 0.8427F, -1.5708F, 0F));
        PartDefinition p_ancla_molino_der = p_molino_der.addOrReplaceChild("ancla_molino_der", CubeListBuilder.create()
                .texOffs(61, 250).addBox(-2.6F, -2.5F, -0.9F, 5.2F, 3F, 1.8F, infla)
                .texOffs(182, 194).addBox(-1.3F, 0F, -1.3F, 2.6F, 13F, 2.6F, infla)
                .texOffs(0, 156).addBox(-1.1F, 2.5F, -8F, 2.2F, 2.2F, 16F, infla)
                .texOffs(237, 228).addBox(-2F, 12F, -2F, 4F, 3.5F, 4F, infla)
                .texOffs(161, 250).addBox(-1F, 5F, 1.2F, 2F, 2F, 2F, infla)
                .texOffs(170, 250).addBox(0.6F, 9F, -2.2F, 2F, 2F, 1.5F, infla),
                PartPose.offsetAndRotation(0F, 63.2559F, 0F, 0F, 0F, 0F));
        p_ancla_molino_der.addOrReplaceChild("ancla_molino_der_a", CubeListBuilder.create()
                .texOffs(134, 212).addBox(-1.2F, 0F, -1.2F, 2.4F, 11F, 2.4F, infla)
                .texOffs(142, 228).addBox(-3.4F, 7F, -1.4F, 6.8F, 6F, 2.8F, infla),
                PartPose.offsetAndRotation(0F, 14F, 0F, 0F, 0F, 2.234F));
        p_ancla_molino_der.addOrReplaceChild("ancla_molino_der_b", CubeListBuilder.create()
                .texOffs(134, 212).addBox(-1.2F, 0F, -1.2F, 2.4F, 11F, 2.4F, infla)
                .texOffs(142, 228).addBox(-3.4F, 7F, -1.4F, 6.8F, 6F, 2.8F, infla),
                PartPose.offsetAndRotation(0F, 14F, 0F, 0F, 0F, -2.234F));
        PartDefinition p_concha = p_cabeza.addOrReplaceChild("concha", CubeListBuilder.create()
                .texOffs(46, 228).addBox(-4F, -4F, -1.2F, 8F, 8F, 2.4F, infla),
                PartPose.offsetAndRotation(0F, -8F, 10F, 0.1745F, 0F, 0F));
        p_concha.addOrReplaceChild("concha_r0", CubeListBuilder.create()
                .texOffs(192, 0).addBox(-2.8F, -30F, -0.7F, 5.6F, 30F, 1.4F, infla)
                .texOffs(96, 250).addBox(-3F, -31.4F, -0.8F, 6F, 1.6F, 1.6F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, -1.2217F));
        p_concha.addOrReplaceChild("concha_r1", CubeListBuilder.create()
                .texOffs(69, 100).addBox(-2.8F, -28F, -0.5F, 5.6F, 28F, 1F, infla)
                .texOffs(96, 250).addBox(-3F, -29.4F, -0.8F, 6F, 1.6F, 1.6F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0.6F, 0F, 0F, -1.0472F));
        p_concha.addOrReplaceChild("concha_r2", CubeListBuilder.create()
                .texOffs(192, 0).addBox(-2.8F, -30F, -0.7F, 5.6F, 30F, 1.4F, infla)
                .texOffs(96, 250).addBox(-3F, -31.4F, -0.8F, 6F, 1.6F, 1.6F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, -0.8727F));
        p_concha.addOrReplaceChild("concha_r3", CubeListBuilder.create()
                .texOffs(69, 100).addBox(-2.8F, -28F, -0.5F, 5.6F, 28F, 1F, infla)
                .texOffs(96, 250).addBox(-3F, -29.4F, -0.8F, 6F, 1.6F, 1.6F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0.6F, 0F, 0F, -0.6981F));
        p_concha.addOrReplaceChild("concha_r4", CubeListBuilder.create()
                .texOffs(192, 0).addBox(-2.8F, -30F, -0.7F, 5.6F, 30F, 1.4F, infla)
                .texOffs(96, 250).addBox(-3F, -31.4F, -0.8F, 6F, 1.6F, 1.6F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, -0.5236F));
        p_concha.addOrReplaceChild("concha_r5", CubeListBuilder.create()
                .texOffs(69, 100).addBox(-2.8F, -28F, -0.5F, 5.6F, 28F, 1F, infla)
                .texOffs(96, 250).addBox(-3F, -29.4F, -0.8F, 6F, 1.6F, 1.6F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0.6F, 0F, 0F, -0.3491F));
        p_concha.addOrReplaceChild("concha_r6", CubeListBuilder.create()
                .texOffs(192, 0).addBox(-2.8F, -30F, -0.7F, 5.6F, 30F, 1.4F, infla)
                .texOffs(96, 250).addBox(-3F, -31.4F, -0.8F, 6F, 1.6F, 1.6F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, -0.1745F));
        p_concha.addOrReplaceChild("concha_r7", CubeListBuilder.create()
                .texOffs(69, 100).addBox(-2.8F, -28F, -0.5F, 5.6F, 28F, 1F, infla)
                .texOffs(96, 250).addBox(-3F, -29.4F, -0.8F, 6F, 1.6F, 1.6F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0.6F, 0F, 0F, 0F));
        p_concha.addOrReplaceChild("concha_r8", CubeListBuilder.create()
                .texOffs(192, 0).addBox(-2.8F, -30F, -0.7F, 5.6F, 30F, 1.4F, infla)
                .texOffs(96, 250).addBox(-3F, -31.4F, -0.8F, 6F, 1.6F, 1.6F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0.1745F));
        p_concha.addOrReplaceChild("concha_r9", CubeListBuilder.create()
                .texOffs(69, 100).addBox(-2.8F, -28F, -0.5F, 5.6F, 28F, 1F, infla)
                .texOffs(96, 250).addBox(-3F, -29.4F, -0.8F, 6F, 1.6F, 1.6F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0.6F, 0F, 0F, 0.3491F));
        p_concha.addOrReplaceChild("concha_r10", CubeListBuilder.create()
                .texOffs(192, 0).addBox(-2.8F, -30F, -0.7F, 5.6F, 30F, 1.4F, infla)
                .texOffs(96, 250).addBox(-3F, -31.4F, -0.8F, 6F, 1.6F, 1.6F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0.5236F));
        p_concha.addOrReplaceChild("concha_r11", CubeListBuilder.create()
                .texOffs(69, 100).addBox(-2.8F, -28F, -0.5F, 5.6F, 28F, 1F, infla)
                .texOffs(96, 250).addBox(-3F, -29.4F, -0.8F, 6F, 1.6F, 1.6F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0.6F, 0F, 0F, 0.6981F));
        p_concha.addOrReplaceChild("concha_r12", CubeListBuilder.create()
                .texOffs(192, 0).addBox(-2.8F, -30F, -0.7F, 5.6F, 30F, 1.4F, infla)
                .texOffs(96, 250).addBox(-3F, -31.4F, -0.8F, 6F, 1.6F, 1.6F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0.8727F));
        p_concha.addOrReplaceChild("concha_r13", CubeListBuilder.create()
                .texOffs(69, 100).addBox(-2.8F, -28F, -0.5F, 5.6F, 28F, 1F, infla)
                .texOffs(96, 250).addBox(-3F, -29.4F, -0.8F, 6F, 1.6F, 1.6F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0.6F, 0F, 0F, 1.0472F));
        p_concha.addOrReplaceChild("concha_r14", CubeListBuilder.create()
                .texOffs(192, 0).addBox(-2.8F, -30F, -0.7F, 5.6F, 30F, 1.4F, infla)
                .texOffs(96, 250).addBox(-3F, -31.4F, -0.8F, 6F, 1.6F, 1.6F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 1.2217F));
        p_concha.addOrReplaceChild("perla", CubeListBuilder.create()
                .texOffs(17, 241).addBox(-2.4F, -2.4F, -1.4F, 4.8F, 4.8F, 2.8F, infla),
                PartPose.offsetAndRotation(0F, 0F, -1.8F, 0F, 0F, 0F));
        p_mandibula.addOrReplaceChild("barba_0", CubeListBuilder.create()
                .texOffs(181, 130).addBox(-1.2F, 0F, 0F, 2.6F, 20F, 0F, infla),
                PartPose.offsetAndRotation(-4F, 3.6F, -11.2F, 0.2443F, 0F, -0.1745F));
        p_mandibula.addOrReplaceChild("barba_1", CubeListBuilder.create()
                .texOffs(193, 100).addBox(-1.2F, 0F, 0F, 2.6F, 27F, 0F, infla),
                PartPose.offsetAndRotation(-2F, 3.6F, -11.2F, 0.2443F, 0F, -0.0873F));
        p_mandibula.addOrReplaceChild("barba_2", CubeListBuilder.create()
                .texOffs(207, 0).addBox(-1.2F, 0F, 0F, 2.6F, 32F, 0F, infla),
                PartPose.offsetAndRotation(0F, 3.6F, -11.2F, 0.2443F, 0F, 0F));
        p_mandibula.addOrReplaceChild("barba_3", CubeListBuilder.create()
                .texOffs(207, 100).addBox(-1.2F, 0F, 0F, 2.6F, 26F, 0F, infla),
                PartPose.offsetAndRotation(2F, 3.6F, -11.2F, 0.2443F, 0F, 0.0873F));
        p_mandibula.addOrReplaceChild("barba_4", CubeListBuilder.create()
                .texOffs(54, 156).addBox(-1.2F, 0F, 0F, 2.6F, 19F, 0F, infla),
                PartPose.offsetAndRotation(4F, 3.6F, -11.2F, 0.2443F, 0F, 0.1745F));
        p_torso.addOrReplaceChild("capa_0", CubeListBuilder.create()
                .texOffs(38, 0).addBox(-3F, 0F, 0F, 6F, 52F, 0F, infla),
                PartPose.offsetAndRotation(-11F, -27F, 8.2F, 0.4189F, 0F, 0.1047F));
        p_torso.addOrReplaceChild("capa_1", CubeListBuilder.create()
                .texOffs(25, 0).addBox(-3F, 0F, 0F, 6F, 60F, 0F, infla),
                PartPose.offsetAndRotation(-5.5F, -27F, 8.2F, 0.4189F, 0F, 0.0524F));
        p_torso.addOrReplaceChild("capa_2", CubeListBuilder.create()
                .texOffs(12, 0).addBox(-3F, 0F, 0F, 6F, 64F, 0F, infla),
                PartPose.offsetAndRotation(0F, -27F, 8.2F, 0.4189F, 0F, 0F));
        p_torso.addOrReplaceChild("capa_3", CubeListBuilder.create()
                .texOffs(25, 0).addBox(-3F, 0F, 0F, 6F, 60F, 0F, infla),
                PartPose.offsetAndRotation(5.5F, -27F, 8.2F, 0.4189F, 0F, -0.0524F));
        p_torso.addOrReplaceChild("capa_4", CubeListBuilder.create()
                .texOffs(38, 0).addBox(-3F, 0F, 0F, 6F, 52F, 0F, infla),
                PartPose.offsetAndRotation(11F, -27F, 8.2F, 0.4189F, 0F, -0.1047F));
        p_torso.addOrReplaceChild("espina_0", CubeListBuilder.create()
                .texOffs(83, 212).addBox(-1.1F, -12F, -1.1F, 2.2F, 12F, 2.2F, infla),
                PartPose.offsetAndRotation(0F, -26F, 8F, -0.9599F, 0F, 0F));
        p_torso.addOrReplaceChild("espina_1", CubeListBuilder.create()
                .texOffs(163, 212).addBox(-1.1F, -10F, -1.1F, 2.2F, 10F, 2.2F, infla),
                PartPose.offsetAndRotation(0F, -20F, 8F, -0.9599F, 0F, 0F));
        p_torso.addOrReplaceChild("espina_2", CubeListBuilder.create()
                .texOffs(68, 228).addBox(-1.1F, -8F, -1.1F, 2.2F, 8F, 2.2F, infla),
                PartPose.offsetAndRotation(0F, -14F, 8F, -0.9599F, 0F, 0F));
        p_hombro_izq.addOrReplaceChild("caracola", CubeListBuilder.create()
                .texOffs(188, 130).addBox(-7F, -5F, -7F, 14F, 5F, 14F, infla)
                .texOffs(137, 194).addBox(-5.5F, -9.5F, -5.5F, 11F, 4.5F, 11F, infla)
                .texOffs(191, 212).addBox(-4F, -13F, -4F, 8F, 3.5F, 8F, infla)
                .texOffs(120, 228).addBox(-2.6F, -16F, -2.6F, 5.2F, 3F, 5.2F, infla)
                .texOffs(99, 241).addBox(-1.3F, -19.5F, -1.3F, 2.6F, 3.5F, 2.6F, infla)
                .texOffs(113, 250).addBox(6.5F, -4F, -1F, 5F, 2F, 2F, infla)
                .texOffs(72, 241).addBox(-1F, -8F, 5F, 2F, 2F, 5F, infla)
                .texOffs(128, 250).addBox(-9.5F, -7F, -1F, 4F, 2F, 2F, infla)
                .texOffs(0, 250).addBox(-1F, -3F, -10F, 2F, 2F, 4F, infla),
                PartPose.offsetAndRotation(1F, -7F, 0F, 0F, 0F, 0.3142F));
        p_tridente.addOrReplaceChild("espiral", CubeListBuilder.create()
                .texOffs(178, 250).addBox(2.4F, -22F, -0.8F, 1.6F, 1.6F, 1.6F, infla)
                .texOffs(178, 250).addBox(1.8044F, -18.7F, 1.0593F, 1.6F, 1.6F, 1.6F, infla)
                .texOffs(178, 250).addBox(0.2393F, -15.4F, 2.2265F, 1.6F, 1.6F, 1.6F, infla)
                .texOffs(178, 250).addBox(-1.7126F, -12.1F, 2.2671F, 1.6F, 1.6F, 1.6F, infla)
                .texOffs(178, 250).addBox(-3.3248F, -8.8F, 1.166F, 1.6F, 1.6F, 1.6F, infla)
                .texOffs(178, 250).addBox(-3.9972F, -5.5F, -0.6669F, 1.6F, 1.6F, 1.6F, infla)
                .texOffs(178, 250).addBox(-3.4795F, -2.2F, -2.5494F, 1.6F, 1.6F, 1.6F, infla)
                .texOffs(178, 250).addBox(-1.9643F, 1.1F, -3.7807F, 1.6F, 1.6F, 1.6F, infla)
                .texOffs(178, 250).addBox(-0.0157F, 4.4F, -3.9024F, 1.6F, 1.6F, 1.6F, infla)
                .texOffs(178, 250).addBox(1.6409F, 7.7F, -2.8693F, 1.6F, 1.6F, 1.6F, infla)
                .texOffs(178, 250).addBox(2.3889F, 11F, -1.0659F, 1.6F, 1.6F, 1.6F, infla)
                .texOffs(178, 250).addBox(1.9499F, 14.3F, 0.8365F, 1.6F, 1.6F, 1.6F, infla)
                .texOffs(178, 250).addBox(0.4872F, 17.6F, 2.1297F, 1.6F, 1.6F, 1.6F, infla)
                .texOffs(178, 250).addBox(-1.4546F, 20.9F, 2.3323F, 1.6F, 1.6F, 1.6F, infla)
                .texOffs(178, 250).addBox(-3.1528F, 24.2F, 1.369F, 1.6F, 1.6F, 1.6F, infla)
                .texOffs(178, 250).addBox(-3.9751F, 27.5F, -0.4017F, 1.6F, 1.6F, 1.6F, infla)
                .texOffs(178, 250).addBox(-3.6156F, 30.8F, -2.3207F, 1.6F, 1.6F, 1.6F, infla)
                .texOffs(178, 250).addBox(-2.2079F, 34.1F, -3.6736F, 1.6F, 1.6F, 1.6F, infla)
                .texOffs(178, 250).addBox(-0.2762F, 37.4F, -3.9568F, 1.6F, 1.6F, 1.6F, infla)
                .texOffs(178, 250).addBox(1.4605F, 40.7F, -3.0649F, 1.6F, 1.6F, 1.6F, infla)
                .texOffs(178, 250).addBox(2.3558F, 44F, -1.3299F, 1.6F, 1.6F, 1.6F, infla)
                .texOffs(178, 250).addBox(2.0764F, 47.3F, 0.6023F, 1.6F, 1.6F, 1.6F, infla)
                .texOffs(178, 250).addBox(0.7262F, 50.6F, 2.0126F, 1.6F, 1.6F, 1.6F, infla)
                .texOffs(178, 250).addBox(-1.1921F, 53.9F, 2.3759F, 1.6F, 1.6F, 1.6F, infla)
                .texOffs(178, 250).addBox(-2.9644F, 57.2F, 1.557F, 1.6F, 1.6F, 1.6F, infla)
                .texOffs(178, 250).addBox(-3.9311F, 60.5F, -0.1393F, 1.6F, 1.6F, 1.6F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        return LayerDefinition.create(malla, 256, 512);
    }

    /** El ancla del Arpon cuando vuela: la de la mano, con la cruz por delante (+Z). */
    public static LayerDefinition crearAncla() {
        CubeDeformation infla = CubeDeformation.NONE;
        MeshDefinition malla = new MeshDefinition();
        PartDefinition p_root = malla.getRoot();
        PartDefinition p_ancla = p_root.addOrReplaceChild("ancla", CubeListBuilder.create()
                .texOffs(61, 250).addBox(-2.6F, -2.5F, -0.9F, 5.2F, 3F, 1.8F, infla)
                .texOffs(182, 194).addBox(-1.3F, 0F, -1.3F, 2.6F, 13F, 2.6F, infla)
                .texOffs(0, 156).addBox(-1.1F, 2.5F, -8F, 2.2F, 2.2F, 16F, infla)
                .texOffs(237, 228).addBox(-2F, 12F, -2F, 4F, 3.5F, 4F, infla)
                .texOffs(161, 250).addBox(-1F, 5F, 1.2F, 2F, 2F, 2F, infla)
                .texOffs(170, 250).addBox(0.6F, 9F, -2.2F, 2F, 2F, 1.5F, infla),
                PartPose.offsetAndRotation(0F, 0F, -6.5F, 1.5708F, 0F, 0F));
        p_ancla.addOrReplaceChild("gancho_mano_a", CubeListBuilder.create()
                .texOffs(134, 212).addBox(-1.2F, 0F, -1.2F, 2.4F, 11F, 2.4F, infla)
                .texOffs(142, 228).addBox(-3.4F, 7F, -1.4F, 6.8F, 6F, 2.8F, infla),
                PartPose.offsetAndRotation(0F, 14F, 0F, 0F, 0F, 2.234F));
        p_ancla.addOrReplaceChild("gancho_mano_b", CubeListBuilder.create()
                .texOffs(134, 212).addBox(-1.2F, 0F, -1.2F, 2.4F, 11F, 2.4F, infla)
                .texOffs(142, 228).addBox(-3.4F, 7F, -1.4F, 6.8F, 6F, 2.8F, infla),
                PartPose.offsetAndRotation(0F, 14F, 0F, 0F, 0F, -2.234F));
        return LayerDefinition.create(malla, 256, 512);
    }
}
