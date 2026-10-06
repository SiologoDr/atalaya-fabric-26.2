package com.atalaya.client;

import net.minecraft.client.model.geom.PartPose;
import net.minecraft.client.model.geom.builders.CubeDeformation;
import net.minecraft.client.model.geom.builders.CubeListBuilder;
import net.minecraft.client.model.geom.builders.LayerDefinition;
import net.minecraft.client.model.geom.builders.MeshDefinition;
import net.minecraft.client.model.geom.builders.PartDefinition;

/**
 * Las estatuas de angel de Novilis (Trompetas del Apocalipsis). GENERADO por
 * materiales/generadores/novilis_props.py: no se edita a mano.
 *
 * Escala x1 (un texel por pixel), la base en y = 24: mide 120 px = 7,5 bloques.
 * Textura: textures/entity/novilis/estatua.png (y estatua_brillo.png, la luz de
 * la campana de la trompeta). La entera y la rota comparten el atlas.
 */
public final class EstatuaNovilisMalla {

    private EstatuaNovilisMalla() {
    }

    public static LayerDefinition crear() {
        return entera(CubeDeformation.NONE);
    }

    private static LayerDefinition entera(CubeDeformation infla) {
        MeshDefinition malla = new MeshDefinition();
        PartDefinition p_root = malla.getRoot();
        PartDefinition p_estatua = p_root.addOrReplaceChild("estatua", CubeListBuilder.create(),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        entera_pedestal(p_estatua, infla);
        p_estatua.addOrReplaceChild("pie_der", CubeListBuilder.create()
                .texOffs(31, 351).addBox(-1.55F, -2F, -4.6F, 3.1F, 2F, 6F, infla)
                .texOffs(65, 385).addBox(-1.35F, -1.45F, -5.9F, 2.7F, 1.45F, 1.5F, infla)
                .texOffs(99, 385).addBox(-1.7F, -2.25F, -2.8F, 3.4F, 0.5F, 0.8F, infla)
                .texOffs(8, 351).addBox(-1.65F, -0.45F, -6F, 3.3F, 0.45F, 7.4F, infla),
                PartPose.offsetAndRotation(-3.3F, 6F, -5.3F, 0F, 0.1396F, 0F));
        p_estatua.addOrReplaceChild("pie_izq", CubeListBuilder.create()
                .texOffs(31, 351).addBox(-1.55F, -2F, -4.6F, 3.1F, 2F, 6F, infla)
                .texOffs(65, 385).addBox(-1.35F, -1.45F, -5.9F, 2.7F, 1.45F, 1.5F, infla)
                .texOffs(99, 385).addBox(-1.7F, -2.25F, -2.8F, 3.4F, 0.5F, 0.8F, infla)
                .texOffs(8, 351).addBox(-1.65F, -0.45F, -6F, 3.3F, 0.45F, 7.4F, infla),
                PartPose.offsetAndRotation(3.9F, 6F, -6.6F, 0.1047F, -0.2793F, 0F));
        entera_falda(p_estatua, infla);
        PartDefinition p_torso = p_estatua.addOrReplaceChild("torso", CubeListBuilder.create()
                .texOffs(207, 223).addBox(-5F, -15F, -3F, 10F, 15.6F, 6.4F, infla)
                .texOffs(164, 317).addBox(-4.6F, -17F, -2.72F, 9.2F, 3.8F, 5.44F, infla)
                .texOffs(33, 317).addBox(-3.68F, -17F, -3.4F, 7.36F, 3.8F, 6.8F, infla)
                .texOffs(194, 303).addBox(-5.95F, -1F, -4.2F, 11.9F, 1.7F, 8.4F, infla)
                .texOffs(0, 385).addBox(-1F, -1.5F, -4.65F, 2F, 2.6F, 0.6F, infla),
                PartPose.offsetAndRotation(0F, -53F, 0.3F, -0.0524F, 0.1396F, -0.0524F));
        p_torso.addOrReplaceChild("corpino_0_0", CubeListBuilder.create()
                .texOffs(17, 370).addBox(-1.523F, -0.4F, -0.6F, 3.046F, 5.4899F, 1.2F, infla)
                .texOffs(44, 385).addBox(-1.573F, -0.55F, -0.85F, 3.146F, 0.75F, 1.5F, infla),
                PartPose.offsetAndRotation(0F, -14.7F, -3.82F, -0.2855F, 0F, 0F));
        p_torso.addOrReplaceChild("corpino_0_1", CubeListBuilder.create()
                .texOffs(206, 370).addBox(-1.5037F, -0.4F, -0.6F, 3.0073F, 4.331F, 1.2F, infla),
                PartPose.offsetAndRotation(0F, -10.2F, -5.1411F, 0.2733F, 0F, 0F));
        p_torso.addOrReplaceChild("corpino_0_2", CubeListBuilder.create()
                .texOffs(229, 329).addBox(-1.3188F, -0.4F, -0.6F, 2.6377F, 8.2068F, 1.2F, infla),
                PartPose.offsetAndRotation(0F, -6.8F, -4.1881F, 0.043F, 0F, 0F));
        p_torso.addOrReplaceChild("corpino_1_0", CubeListBuilder.create()
                .texOffs(77, 361).addBox(-1.523F, -0.4F, -0.6F, 3.046F, 6.0917F, 1.2F, infla)
                .texOffs(44, 385).addBox(-1.573F, -0.55F, -0.85F, 3.146F, 0.75F, 1.5F, infla),
                PartPose.offsetAndRotation(2.7737F, -14.9824F, -3.083F, -0.4421F, -0.271F, -0.0008F));
        p_torso.addOrReplaceChild("corpino_1_1", CubeListBuilder.create()
                .texOffs(216, 370).addBox(-1.5037F, -0.4F, -0.6F, 3.0073F, 4.6292F, 1.2F, infla),
                PartPose.offsetAndRotation(3.3838F, -10.2F, -5.2645F, 0.4553F, -0.2862F, 0.0663F));
        p_torso.addOrReplaceChild("corpino_1_2", CubeListBuilder.create()
                .texOffs(238, 329).addBox(-1.3188F, -0.4F, -0.6F, 2.6377F, 8.2312F, 1.2F, infla),
                PartPose.offsetAndRotation(2.6816F, -6.8F, -3.649F, 0.0735F, -0.3071F, 0.037F));
        p_torso.addOrReplaceChild("corpino_2_0", CubeListBuilder.create()
                .texOffs(87, 361).addBox(-1.523F, -0.4F, -0.6F, 3.046F, 6.2575F, 1.2F, infla)
                .texOffs(44, 385).addBox(-1.573F, -0.55F, -0.85F, 3.146F, 0.75F, 1.5F, infla),
                PartPose.offsetAndRotation(5.2087F, -15.6169F, -2.4595F, -0.1212F, -0.6296F, -0.0014F));
        p_torso.addOrReplaceChild("corpino_2_1", CubeListBuilder.create()
                .texOffs(226, 370).addBox(-1.5037F, -0.4F, -0.6F, 3.0073F, 4.2962F, 1.2F, infla),
                PartPose.offsetAndRotation(5.6049F, -10.2F, -2.9931F, 0.1378F, -0.6541F, 0.1245F));
        p_torso.addOrReplaceChild("corpino_2_2", CubeListBuilder.create()
                .texOffs(247, 329).addBox(-1.3188F, -0.4F, -0.6F, 2.6377F, 8.2254F, 1.2F, infla),
                PartPose.offsetAndRotation(4.8851F, -6.8F, -2.6121F, 0.0248F, -0.6937F, 0.0646F));
        p_torso.addOrReplaceChild("corpino_3_0", CubeListBuilder.create()
                .texOffs(97, 361).addBox(-1.523F, -0.4F, -0.6F, 3.046F, 6.7295F, 1.2F, infla)
                .texOffs(44, 385).addBox(-1.573F, -0.55F, -0.85F, 3.146F, 0.75F, 1.5F, infla),
                PartPose.offsetAndRotation(6.1699F, -16.1257F, -0.7603F, -0.0354F, -1.1999F, -0.0003F));
        p_torso.addOrReplaceChild("corpino_3_1", CubeListBuilder.create()
                .texOffs(236, 370).addBox(-1.5037F, -0.4F, -0.6F, 3.0073F, 4.2689F, 1.2F, infla),
                PartPose.offsetAndRotation(6.3674F, -10.2F, -0.8364F, 0.0334F, -1.2142F, 0.168F));
        p_torso.addOrReplaceChild("corpino_3_2", CubeListBuilder.create()
                .texOffs(0, 340).addBox(-1.3188F, -0.4F, -0.6F, 2.6377F, 8.2317F, 1.2F, infla),
                PartPose.offsetAndRotation(5.6809F, -6.8F, -0.796F, 0.0073F, -1.2426F, 0.0854F));
        p_torso.addOrReplaceChild("corpino_4_0", CubeListBuilder.create()
                .texOffs(107, 361).addBox(-1.523F, -0.4F, -0.6F, 3.046F, 6.7293F, 1.2F, infla)
                .texOffs(44, 385).addBox(-1.573F, -0.55F, -0.85F, 3.146F, 0.75F, 1.5F, infla),
                PartPose.offsetAndRotation(6.5418F, -16.1257F, 0.9222F, 3.1138F, -1.2039F, 3.1344F));
        p_torso.addOrReplaceChild("corpino_4_1", CubeListBuilder.create()
                .texOffs(246, 370).addBox(-1.5037F, -0.4F, -0.6F, 3.0073F, 4.2677F, 1.2F, infla),
                PartPose.offsetAndRotation(6.7379F, -10.2F, 0.9812F, -3.1083F, -1.2175F, -2.9752F));
        p_torso.addOrReplaceChild("corpino_4_2", CubeListBuilder.create()
                .texOffs(238, 329).addBox(-1.3188F, -0.4F, -0.6F, 2.6377F, 8.2313F, 1.2F, infla),
                PartPose.offsetAndRotation(6.0572F, -6.8F, 0.9413F, -3.1296F, -1.2471F, -3.0613F));
        p_torso.addOrReplaceChild("corpino_5_0", CubeListBuilder.create()
                .texOffs(117, 361).addBox(-1.523F, -0.4F, -0.6F, 3.046F, 6.2212F, 1.2F, infla)
                .texOffs(44, 385).addBox(-1.573F, -0.55F, -0.85F, 3.146F, 0.75F, 1.5F, infla),
                PartPose.offsetAndRotation(4.9747F, -15.6169F, 2.2518F, 3.107F, -0.6451F, 3.1339F));
        p_torso.addOrReplaceChild("corpino_5_1", CubeListBuilder.create()
                .texOffs(0, 378).addBox(-1.5037F, -0.4F, -0.6F, 3.0073F, 4.2455F, 1.2F, infla),
                PartPose.offsetAndRotation(5.129F, -10.2F, 2.4015F, -3.1136F, -0.6663F, -2.9977F));
        p_torso.addOrReplaceChild("corpino_5_2", CubeListBuilder.create()
                .texOffs(9, 340).addBox(-1.3188F, -0.4F, -0.6F, 2.6377F, 8.2209F, 1.2F, infla),
                PartPose.offsetAndRotation(4.5763F, -6.8F, 2.3258F, -3.1315F, -0.7137F, -3.0735F));
        p_torso.addOrReplaceChild("corpino_6_0", CubeListBuilder.create()
                .texOffs(27, 370).addBox(-1.523F, -0.4F, -0.6F, 3.046F, 5.5869F, 1.2F, infla)
                .texOffs(44, 385).addBox(-1.573F, -0.55F, -0.85F, 3.146F, 0.75F, 1.5F, infla),
                PartPose.offsetAndRotation(2.8811F, -14.9824F, 3.7118F, 3.1005F, -0.2833F, 3.1347F));
        p_torso.addOrReplaceChild("corpino_6_1", CubeListBuilder.create()
                .texOffs(10, 378).addBox(-1.5037F, -0.4F, -0.6F, 3.0073F, 4.2145F, 1.2F, infla),
                PartPose.offsetAndRotation(2.9691F, -10.2F, 3.9006F, -3.1115F, -0.2971F, -3.0628F));
        p_torso.addOrReplaceChild("corpino_6_2", CubeListBuilder.create()
                .texOffs(229, 329).addBox(-1.3188F, -0.4F, -0.6F, 2.6377F, 8.2066F, 1.2F, infla),
                PartPose.offsetAndRotation(2.6704F, -6.8F, 3.8023F, -3.1285F, -0.3245F, -3.1056F));
        p_torso.addOrReplaceChild("corpino_7_0", CubeListBuilder.create()
                .texOffs(37, 370).addBox(-1.523F, -0.4F, -0.6F, 3.046F, 5.3044F, 1.2F, infla)
                .texOffs(44, 385).addBox(-1.573F, -0.55F, -0.85F, 3.146F, 0.75F, 1.5F, infla),
                PartPose.offsetAndRotation(0F, -14.7F, 3.72F, 3.0972F, 0F, 3.1416F));
        p_torso.addOrReplaceChild("corpino_7_1", CubeListBuilder.create()
                .texOffs(20, 378).addBox(-1.5037F, -0.4F, -0.6F, 3.0073F, 4.2015F, 1.2F, infla),
                PartPose.offsetAndRotation(0F, -10.2F, 3.92F, -3.1122F, 0F, -3.1416F));
        p_torso.addOrReplaceChild("corpino_7_2", CubeListBuilder.create()
                .texOffs(18, 340).addBox(-1.3188F, -0.4F, -0.6F, 2.6377F, 8.2007F, 1.2F, infla),
                PartPose.offsetAndRotation(0F, -6.8F, 3.82F, -3.1281F, 0F, -3.1416F));
        p_torso.addOrReplaceChild("corpino_8_0", CubeListBuilder.create()
                .texOffs(27, 370).addBox(-1.523F, -0.4F, -0.6F, 3.046F, 5.5869F, 1.2F, infla)
                .texOffs(44, 385).addBox(-1.573F, -0.55F, -0.85F, 3.146F, 0.75F, 1.5F, infla),
                PartPose.offsetAndRotation(-2.8811F, -14.9824F, 3.7118F, 3.1005F, 0.2833F, -3.1347F));
        p_torso.addOrReplaceChild("corpino_8_1", CubeListBuilder.create()
                .texOffs(10, 378).addBox(-1.5037F, -0.4F, -0.6F, 3.0073F, 4.2145F, 1.2F, infla),
                PartPose.offsetAndRotation(-2.9691F, -10.2F, 3.9006F, -3.1115F, 0.2971F, 3.0628F));
        p_torso.addOrReplaceChild("corpino_8_2", CubeListBuilder.create()
                .texOffs(229, 329).addBox(-1.3188F, -0.4F, -0.6F, 2.6377F, 8.2066F, 1.2F, infla),
                PartPose.offsetAndRotation(-2.6704F, -6.8F, 3.8023F, -3.1285F, 0.3245F, 3.1056F));
        p_torso.addOrReplaceChild("corpino_9_0", CubeListBuilder.create()
                .texOffs(117, 361).addBox(-1.523F, -0.4F, -0.6F, 3.046F, 6.2212F, 1.2F, infla)
                .texOffs(44, 385).addBox(-1.573F, -0.55F, -0.85F, 3.146F, 0.75F, 1.5F, infla),
                PartPose.offsetAndRotation(-4.9747F, -15.6169F, 2.2518F, 3.107F, 0.6451F, -3.1339F));
        p_torso.addOrReplaceChild("corpino_9_1", CubeListBuilder.create()
                .texOffs(0, 378).addBox(-1.5037F, -0.4F, -0.6F, 3.0073F, 4.2455F, 1.2F, infla),
                PartPose.offsetAndRotation(-5.129F, -10.2F, 2.4015F, -3.1136F, 0.6663F, 2.9977F));
        p_torso.addOrReplaceChild("corpino_9_2", CubeListBuilder.create()
                .texOffs(9, 340).addBox(-1.3188F, -0.4F, -0.6F, 2.6377F, 8.2209F, 1.2F, infla),
                PartPose.offsetAndRotation(-4.5763F, -6.8F, 2.3258F, -3.1315F, 0.7137F, 3.0735F));
        p_torso.addOrReplaceChild("corpino_10_0", CubeListBuilder.create()
                .texOffs(107, 361).addBox(-1.523F, -0.4F, -0.6F, 3.046F, 6.7293F, 1.2F, infla)
                .texOffs(44, 385).addBox(-1.573F, -0.55F, -0.85F, 3.146F, 0.75F, 1.5F, infla),
                PartPose.offsetAndRotation(-6.5418F, -16.1257F, 0.9222F, 3.1138F, 1.2039F, -3.1344F));
        p_torso.addOrReplaceChild("corpino_10_1", CubeListBuilder.create()
                .texOffs(246, 370).addBox(-1.5037F, -0.4F, -0.6F, 3.0073F, 4.2677F, 1.2F, infla),
                PartPose.offsetAndRotation(-6.7379F, -10.2F, 0.9812F, -3.1083F, 1.2175F, 2.9752F));
        p_torso.addOrReplaceChild("corpino_10_2", CubeListBuilder.create()
                .texOffs(238, 329).addBox(-1.3188F, -0.4F, -0.6F, 2.6377F, 8.2313F, 1.2F, infla),
                PartPose.offsetAndRotation(-6.0572F, -6.8F, 0.9413F, -3.1296F, 1.2471F, 3.0613F));
        p_torso.addOrReplaceChild("corpino_11_0", CubeListBuilder.create()
                .texOffs(97, 361).addBox(-1.523F, -0.4F, -0.6F, 3.046F, 6.7295F, 1.2F, infla)
                .texOffs(44, 385).addBox(-1.573F, -0.55F, -0.85F, 3.146F, 0.75F, 1.5F, infla),
                PartPose.offsetAndRotation(-6.1699F, -16.1257F, -0.7603F, -0.0354F, 1.1999F, 0.0003F));
        p_torso.addOrReplaceChild("corpino_11_1", CubeListBuilder.create()
                .texOffs(236, 370).addBox(-1.5037F, -0.4F, -0.6F, 3.0073F, 4.2689F, 1.2F, infla),
                PartPose.offsetAndRotation(-6.3674F, -10.2F, -0.8364F, 0.0334F, 1.2142F, -0.168F));
        p_torso.addOrReplaceChild("corpino_11_2", CubeListBuilder.create()
                .texOffs(0, 340).addBox(-1.3188F, -0.4F, -0.6F, 2.6377F, 8.2317F, 1.2F, infla),
                PartPose.offsetAndRotation(-5.6809F, -6.8F, -0.796F, 0.0073F, 1.2426F, -0.0854F));
        p_torso.addOrReplaceChild("corpino_12_0", CubeListBuilder.create()
                .texOffs(87, 361).addBox(-1.523F, -0.4F, -0.6F, 3.046F, 6.2575F, 1.2F, infla)
                .texOffs(44, 385).addBox(-1.573F, -0.55F, -0.85F, 3.146F, 0.75F, 1.5F, infla),
                PartPose.offsetAndRotation(-5.2087F, -15.6169F, -2.4595F, -0.1212F, 0.6296F, 0.0014F));
        p_torso.addOrReplaceChild("corpino_12_1", CubeListBuilder.create()
                .texOffs(226, 370).addBox(-1.5037F, -0.4F, -0.6F, 3.0073F, 4.2962F, 1.2F, infla),
                PartPose.offsetAndRotation(-5.6049F, -10.2F, -2.9931F, 0.1378F, 0.6541F, -0.1245F));
        p_torso.addOrReplaceChild("corpino_12_2", CubeListBuilder.create()
                .texOffs(247, 329).addBox(-1.3188F, -0.4F, -0.6F, 2.6377F, 8.2254F, 1.2F, infla),
                PartPose.offsetAndRotation(-4.8851F, -6.8F, -2.6121F, 0.0248F, 0.6937F, -0.0646F));
        p_torso.addOrReplaceChild("corpino_13_0", CubeListBuilder.create()
                .texOffs(77, 361).addBox(-1.523F, -0.4F, -0.6F, 3.046F, 6.0917F, 1.2F, infla)
                .texOffs(44, 385).addBox(-1.573F, -0.55F, -0.85F, 3.146F, 0.75F, 1.5F, infla),
                PartPose.offsetAndRotation(-2.7737F, -14.9824F, -3.083F, -0.4421F, 0.271F, 0.0008F));
        p_torso.addOrReplaceChild("corpino_13_1", CubeListBuilder.create()
                .texOffs(216, 370).addBox(-1.5037F, -0.4F, -0.6F, 3.0073F, 4.6292F, 1.2F, infla),
                PartPose.offsetAndRotation(-3.3838F, -10.2F, -5.2645F, 0.4553F, 0.2862F, -0.0663F));
        p_torso.addOrReplaceChild("corpino_13_2", CubeListBuilder.create()
                .texOffs(238, 329).addBox(-1.3188F, -0.4F, -0.6F, 2.6377F, 8.2312F, 1.2F, infla),
                PartPose.offsetAndRotation(-2.6816F, -6.8F, -3.649F, 0.0735F, 0.3071F, -0.037F));
        p_torso.addOrReplaceChild("trapecio_izq", CubeListBuilder.create()
                .texOffs(89, 340).addBox(0F, 0F, -3F, 4.8F, 2.4F, 6F, infla),
                PartPose.offsetAndRotation(2F, -17F, 0.2F, 0F, 0F, 0.4189F));
        p_torso.addOrReplaceChild("fibula_izq", CubeListBuilder.create()
                .texOffs(228, 378).addBox(-1F, -1F, -1F, 2F, 1.3F, 2F, infla),
                PartPose.offsetAndRotation(5.6F, -16F, -0.4F, 0F, 0F, 0.384F));
        p_torso.addOrReplaceChild("trapecio_der", CubeListBuilder.create()
                .texOffs(89, 340).addBox(-4.8F, 0F, -3F, 4.8F, 2.4F, 6F, infla),
                PartPose.offsetAndRotation(-2F, -17F, 0.2F, 0F, 0F, -0.4189F));
        p_torso.addOrReplaceChild("fibula_der", CubeListBuilder.create()
                .texOffs(228, 378).addBox(-1F, -1F, -1F, 2F, 1.3F, 2F, infla),
                PartPose.offsetAndRotation(-5.6F, -16F, -0.4F, 0F, 0F, -0.384F));
        PartDefinition p_cuello = p_torso.addOrReplaceChild("cuello", CubeListBuilder.create()
                .texOffs(183, 351).addBox(-1.7F, -4F, -1.35F, 3.4F, 4.6F, 2.7F, infla)
                .texOffs(127, 340).addBox(-1.275F, -4F, -1.8F, 2.55F, 4.6F, 3.6F, infla),
                PartPose.offsetAndRotation(0F, -16.3F, -0.2F, -0.0873F, 0.1396F, 0.0349F));
        entera_cabeza(p_cuello, infla);
        PartDefinition p_halo = p_torso.addOrReplaceChild("halo", CubeListBuilder.create(),
                PartPose.offsetAndRotation(1.1967F, -28.5218F, 9.8923F, -0.1745F, 0F, 0F));
        p_halo.addOrReplaceChild("halo_disco0", CubeListBuilder.create()
                .texOffs(63, 317).addBox(-4.9F, -4.9F, 0.1F, 9.8F, 9.8F, 0.5F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        p_halo.addOrReplaceChild("halo_disco1", CubeListBuilder.create()
                .texOffs(63, 317).addBox(-4.9F, -4.9F, 0.1F, 9.8F, 9.8F, 0.5F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0.3927F));
        p_halo.addOrReplaceChild("halo_disco2", CubeListBuilder.create()
                .texOffs(63, 317).addBox(-4.9F, -4.9F, 0.1F, 9.8F, 9.8F, 0.5F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0.7854F));
        p_halo.addOrReplaceChild("halo_disco3", CubeListBuilder.create()
                .texOffs(63, 317).addBox(-4.9F, -4.9F, 0.1F, 9.8F, 9.8F, 0.5F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 1.1781F));
        p_halo.addOrReplaceChild("halo_0", CubeListBuilder.create()
                .texOffs(75, 385).addBox(-1.1F, -5.9F, -0.45F, 2.2F, 0.95F, 1.1F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        p_halo.addOrReplaceChild("halo_1", CubeListBuilder.create()
                .texOffs(75, 385).addBox(-1.1F, -5.9F, -0.45F, 2.2F, 0.95F, 1.1F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0.3927F));
        p_halo.addOrReplaceChild("halo_2", CubeListBuilder.create()
                .texOffs(75, 385).addBox(-1.1F, -5.9F, -0.45F, 2.2F, 0.95F, 1.1F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0.7854F));
        p_halo.addOrReplaceChild("halo_3", CubeListBuilder.create()
                .texOffs(75, 385).addBox(-1.1F, -5.9F, -0.45F, 2.2F, 0.95F, 1.1F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 1.1781F));
        p_halo.addOrReplaceChild("halo_4", CubeListBuilder.create()
                .texOffs(75, 385).addBox(-1.1F, -5.9F, -0.45F, 2.2F, 0.95F, 1.1F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 1.5708F));
        p_halo.addOrReplaceChild("halo_5", CubeListBuilder.create()
                .texOffs(75, 385).addBox(-1.1F, -5.9F, -0.45F, 2.2F, 0.95F, 1.1F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 1.9635F));
        p_halo.addOrReplaceChild("halo_6", CubeListBuilder.create()
                .texOffs(75, 385).addBox(-1.1F, -5.9F, -0.45F, 2.2F, 0.95F, 1.1F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 2.3562F));
        p_halo.addOrReplaceChild("halo_7", CubeListBuilder.create()
                .texOffs(75, 385).addBox(-1.1F, -5.9F, -0.45F, 2.2F, 0.95F, 1.1F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 2.7489F));
        p_halo.addOrReplaceChild("halo_8", CubeListBuilder.create()
                .texOffs(75, 385).addBox(-1.1F, -5.9F, -0.45F, 2.2F, 0.95F, 1.1F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 3.1416F));
        p_halo.addOrReplaceChild("halo_9", CubeListBuilder.create()
                .texOffs(75, 385).addBox(-1.1F, -5.9F, -0.45F, 2.2F, 0.95F, 1.1F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 3.5343F));
        p_halo.addOrReplaceChild("halo_10", CubeListBuilder.create()
                .texOffs(75, 385).addBox(-1.1F, -5.9F, -0.45F, 2.2F, 0.95F, 1.1F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 3.927F));
        p_halo.addOrReplaceChild("halo_11", CubeListBuilder.create()
                .texOffs(75, 385).addBox(-1.1F, -5.9F, -0.45F, 2.2F, 0.95F, 1.1F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 4.3197F));
        p_halo.addOrReplaceChild("halo_12", CubeListBuilder.create()
                .texOffs(75, 385).addBox(-1.1F, -5.9F, -0.45F, 2.2F, 0.95F, 1.1F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 4.7124F));
        p_halo.addOrReplaceChild("halo_13", CubeListBuilder.create()
                .texOffs(75, 385).addBox(-1.1F, -5.9F, -0.45F, 2.2F, 0.95F, 1.1F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 5.1051F));
        p_halo.addOrReplaceChild("halo_14", CubeListBuilder.create()
                .texOffs(75, 385).addBox(-1.1F, -5.9F, -0.45F, 2.2F, 0.95F, 1.1F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 5.4978F));
        p_halo.addOrReplaceChild("halo_15", CubeListBuilder.create()
                .texOffs(75, 385).addBox(-1.1F, -5.9F, -0.45F, 2.2F, 0.95F, 1.1F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 5.8905F));
        p_torso.addOrReplaceChild("melena_00_0", CubeListBuilder.create()
                .texOffs(175, 329).addBox(-1.2F, -0.5F, -0.65F, 2.4F, 8.4147F, 1.3F, infla),
                PartPose.offsetAndRotation(0.3204F, -22.8928F, 6.1177F, -0.0699F, 0F, 0.5271F));
        p_torso.addOrReplaceChild("melena_00_1", CubeListBuilder.create()
                .texOffs(127, 361).addBox(-1.152F, -0.5F, -0.65F, 2.304F, 6.6626F, 1.3F, infla),
                PartPose.offsetAndRotation(-3.4F, -16.5F, 5.6F, -0.0557F, 0F, 0.1381F));
        p_torso.addOrReplaceChild("melena_00_2", CubeListBuilder.create()
                .texOffs(188, 340).addBox(-1.104F, -0.5F, -0.65F, 2.208F, 6.7011F, 1.3F, infla),
                PartPose.offsetAndRotation(-4.1785F, -10.9F, 5.285F, -0.0553F, 0F, -0.1804F));
        p_torso.addOrReplaceChild("melena_00_3", CubeListBuilder.create()
                .texOffs(163, 361).addBox(-1.056F, -0.5F, -0.65F, 2.112F, 5.9943F, 1.3F, infla),
                PartPose.offsetAndRotation(-3.157F, -5.3F, 4.97F, -0.0541F, 0F, 0.2747F));
        p_torso.addOrReplaceChild("melena_01_0", CubeListBuilder.create()
                .texOffs(184, 329).addBox(-1.2F, -0.5F, -0.65F, 2.4F, 8.0501F, 1.3F, infla),
                PartPose.offsetAndRotation(1.426F, -22.8189F, 5.6654F, -0.0093F, 0F, 0.4594F));
        p_torso.addOrReplaceChild("melena_01_1", CubeListBuilder.create()
                .texOffs(193, 329).addBox(-1.152F, -0.5F, -0.65F, 2.304F, 8.0257F, 1.3F, infla),
                PartPose.offsetAndRotation(-1.7F, -16.5F, 5.6F, -0.0449F, 0F, -0.0728F));
        p_torso.addOrReplaceChild("melena_01_2", CubeListBuilder.create()
                .texOffs(202, 329).addBox(-1.104F, -0.5F, -0.65F, 2.208F, 8.1247F, 1.3F, infla),
                PartPose.offsetAndRotation(-1.1892F, -9.5F, 5.285F, -0.0442F, 0F, 0.1821F));
        p_torso.addOrReplaceChild("melena_01_3", CubeListBuilder.create()
                .texOffs(224, 340).addBox(-1.056F, -0.5F, -0.65F, 2.112F, 7.1102F, 1.3F, infla),
                PartPose.offsetAndRotation(-2.4785F, -2.5F, 4.97F, -0.0442F, 0F, -0.1851F));
        p_torso.addOrReplaceChild("melena_02_0", CubeListBuilder.create()
                .texOffs(211, 329).addBox(-1.2F, -0.5F, -0.65F, 2.4F, 7.7496F, 1.3F, infla),
                PartPose.offsetAndRotation(2.5316F, -22.7449F, 5.2132F, 0.0573F, 0F, 0.3851F));
        p_torso.addOrReplaceChild("melena_02_1", CubeListBuilder.create()
                .texOffs(146, 317).addBox(-1.152F, -0.5F, -0.65F, 2.304F, 9.0785F, 1.3F, infla),
                PartPose.offsetAndRotation(0F, -16.5F, 5.6F, -0.039F, 0F, 0.0744F));
        p_torso.addOrReplaceChild("melena_02_2", CubeListBuilder.create()
                .texOffs(155, 317).addBox(-1.104F, -0.5F, -0.65F, 2.208F, 9.145F, 1.3F, infla),
                PartPose.offsetAndRotation(-0.6F, -8.45F, 5.285F, -0.0387F, 0F, -0.148F));
        p_torso.addOrReplaceChild("melena_02_3", CubeListBuilder.create()
                .texOffs(27, 340).addBox(-1.056F, -0.5F, -0.65F, 2.112F, 8.0088F, 1.3F, infla),
                PartPose.offsetAndRotation(0.6F, -0.4F, 4.97F, -0.0385F, 0F, 0.1722F));
        p_torso.addOrReplaceChild("melena_03_0", CubeListBuilder.create()
                .texOffs(197, 340).addBox(-1.2F, -0.5F, -0.65F, 2.4F, 7.5221F, 1.3F, infla),
                PartPose.offsetAndRotation(3.6371F, -22.671F, 4.7609F, 0.129F, 0F, 0.3042F));
        p_torso.addOrReplaceChild("melena_03_1", CubeListBuilder.create()
                .texOffs(206, 340).addBox(-1.152F, -0.5F, -0.65F, 2.304F, 7.693F, 1.3F, infla),
                PartPose.offsetAndRotation(1.7F, -16.5F, 5.6F, -0.0471F, 0F, -0.1033F));
        p_torso.addOrReplaceChild("melena_03_2", CubeListBuilder.create()
                .texOffs(220, 329).addBox(-1.104F, -0.5F, -0.65F, 2.208F, 7.7495F, 1.3F, infla),
                PartPose.offsetAndRotation(2.3893F, -9.85F, 5.285F, -0.0467F, 0F, 0.1655F));
        p_torso.addOrReplaceChild("melena_03_3", CubeListBuilder.create()
                .texOffs(232, 340).addBox(-1.056F, -0.5F, -0.65F, 2.112F, 6.8474F, 1.3F, infla),
                PartPose.offsetAndRotation(1.2785F, -3.2F, 4.97F, -0.0462F, 0F, -0.2203F));
        p_torso.addOrReplaceChild("melena_04_0", CubeListBuilder.create()
                .texOffs(215, 340).addBox(-1.2F, -0.5F, -0.65F, 2.4F, 7.3753F, 1.3F, infla),
                PartPose.offsetAndRotation(4.7427F, -22.5971F, 4.3087F, 0.204F, 0F, 0.2168F));
        p_torso.addOrReplaceChild("melena_04_1", CubeListBuilder.create()
                .texOffs(136, 361).addBox(-1.152F, -0.5F, -0.65F, 2.304F, 6.2763F, 1.3F, infla),
                PartPose.offsetAndRotation(3.4F, -16.5F, 5.6F, -0.0597F, 0F, 0.0801F));
        p_torso.addOrReplaceChild("melena_04_2", CubeListBuilder.create()
                .texOffs(145, 361).addBox(-1.104F, -0.5F, -0.65F, 2.208F, 6.4371F, 1.3F, infla),
                PartPose.offsetAndRotation(2.9785F, -11.25F, 5.285F, -0.058F, 0F, -0.2568F));
        p_torso.addOrReplaceChild("melena_04_3", CubeListBuilder.create()
                .texOffs(56, 370).addBox(-1.056F, -0.5F, -0.65F, 2.112F, 5.6281F, 1.3F, infla),
                PartPose.offsetAndRotation(4.357F, -6F, 4.97F, -0.0584F, 0F, 0.2286F));
        p_torso.addOrReplaceChild("melena_10_0", CubeListBuilder.create()
                .texOffs(35, 340).addBox(-1.1F, -0.5F, -0.6F, 2.2F, 8.2556F, 1.2F, infla),
                PartPose.offsetAndRotation(0.9057F, -22.8537F, 5.8783F, 0.1135F, 0F, 0.492F));
        p_torso.addOrReplaceChild("melena_10_1", CubeListBuilder.create()
                .texOffs(64, 370).addBox(-1.056F, -0.5F, -0.6F, 2.112F, 5.2378F, 1.2F, infla),
                PartPose.offsetAndRotation(-2.5F, -16.5F, 6.7F, -0.0744F, 0F, -0.1111F));
        p_torso.addOrReplaceChild("melena_10_2", CubeListBuilder.create()
                .texOffs(72, 370).addBox(-1.012F, -0.5F, -0.6F, 2.024F, 5.4172F, 1.2F, infla),
                PartPose.offsetAndRotation(-2.0312F, -12.3F, 6.385F, -0.0714F, 0F, 0.3069F));
        p_torso.addOrReplaceChild("melena_10_3", CubeListBuilder.create()
                .texOffs(48, 378).addBox(-0.968F, -0.5F, -0.6F, 1.936F, 4.7704F, 1.2F, infla),
                PartPose.offsetAndRotation(-3.3625F, -8.1F, 6.07F, -0.0717F, 0F, -0.2934F));
        p_torso.addOrReplaceChild("melena_11_0", CubeListBuilder.create()
                .texOffs(43, 340).addBox(-1.1F, -0.5F, -0.6F, 2.2F, 7.9972F, 1.2F, infla),
                PartPose.offsetAndRotation(2.0113F, -22.7797F, 5.426F, 0.1831F, 0F, 0.4209F));
        p_torso.addOrReplaceChild("melena_11_1", CubeListBuilder.create()
                .texOffs(171, 361).addBox(-1.056F, -0.5F, -0.6F, 2.112F, 6.2985F, 1.2F, infla),
                PartPose.offsetAndRotation(-0.8F, -16.5F, 6.7F, -0.0595F, 0F, 0.1217F));
        p_torso.addOrReplaceChild("melena_11_2", CubeListBuilder.create()
                .texOffs(179, 361).addBox(-1.012F, -0.5F, -0.6F, 2.024F, 6.3854F, 1.2F, infla),
                PartPose.offsetAndRotation(-1.442F, -11.25F, 6.385F, -0.0585F, 0F, -0.2171F));
        p_torso.addOrReplaceChild("melena_11_3", CubeListBuilder.create()
                .texOffs(80, 370).addBox(-0.968F, -0.5F, -0.6F, 1.936F, 5.6745F, 1.2F, infla),
                PartPose.offsetAndRotation(-0.284F, -6F, 6.07F, -0.0578F, 0F, 0.2681F));
        p_torso.addOrReplaceChild("melena_12_0", CubeListBuilder.create()
                .texOffs(51, 340).addBox(-1.1F, -0.5F, -0.6F, 2.2F, 7.8122F, 1.2F, infla),
                PartPose.offsetAndRotation(3.1169F, -22.7058F, 4.9737F, 0.2562F, 0F, 0.3431F));
        p_torso.addOrReplaceChild("melena_12_1", CubeListBuilder.create()
                .texOffs(187, 361).addBox(-1.056F, -0.5F, -0.6F, 2.112F, 5.9526F, 1.2F, infla),
                PartPose.offsetAndRotation(0.9F, -16.5F, 6.7F, -0.0636F, 0F, -0.1313F));
        p_torso.addOrReplaceChild("melena_12_2", CubeListBuilder.create()
                .texOffs(195, 361).addBox(-1.012F, -0.5F, -0.6F, 2.024F, 6.0436F, 1.2F, infla),
                PartPose.offsetAndRotation(1.5473F, -11.6F, 6.385F, -0.0625F, 0F, 0.2311F));
        p_torso.addOrReplaceChild("melena_12_3", CubeListBuilder.create()
                .texOffs(88, 370).addBox(-0.968F, -0.5F, -0.6F, 1.936F, 5.3877F, 1.2F, infla),
                PartPose.offsetAndRotation(0.3945F, -6.7F, 6.07F, -0.0616F, 0F, -0.2872F));
        p_torso.addOrReplaceChild("melena_13_0", CubeListBuilder.create()
                .texOffs(240, 340).addBox(-1.1F, -0.5F, -0.6F, 2.2F, 7.7066F, 1.2F, infla),
                PartPose.offsetAndRotation(4.2225F, -22.6319F, 4.5215F, 0.3308F, 0F, 0.2587F));
        p_torso.addOrReplaceChild("melena_13_1", CubeListBuilder.create()
                .texOffs(96, 370).addBox(-1.056F, -0.5F, -0.6F, 2.112F, 4.8906F, 1.2F, infla),
                PartPose.offsetAndRotation(2.6F, -16.5F, 6.7F, -0.0811F, 0F, 0.1198F));
        p_torso.addOrReplaceChild("melena_13_2", CubeListBuilder.create()
                .texOffs(104, 370).addBox(-1.012F, -0.5F, -0.6F, 2.024F, 5.0875F, 1.2F, infla),
                PartPose.offsetAndRotation(2.1365F, -12.65F, 6.385F, -0.0771F, 0F, -0.3341F));
        p_torso.addOrReplaceChild("melena_13_3", CubeListBuilder.create()
                .texOffs(56, 378).addBox(-0.968F, -0.5F, -0.6F, 1.936F, 4.4836F, 1.2F, infla),
                PartPose.offsetAndRotation(3.473F, -8.8F, 6.07F, -0.0776F, 0F, 0.3171F));
        p_torso.addOrReplaceChild("mechon_0_0", CubeListBuilder.create()
                .texOffs(248, 340).addBox(-1.1F, -0.5F, -0.6F, 2.2F, 7.5428F, 1.2F, infla),
                PartPose.offsetAndRotation(-1.3991F, -23.0832F, 2.5352F, -2.7924F, -0.5268F, -2.8935F));
        p_torso.addOrReplaceChild("mechon_0_1", CubeListBuilder.create()
                .texOffs(112, 370).addBox(-1.056F, -0.5F, -0.6F, 2.112F, 5.6733F, 1.2F, infla),
                PartPose.offsetAndRotation(-4F, -17.4F, 0.6F, -1.857F, -0.4686F, 2.5749F));
        p_torso.addOrReplaceChild("mechon_0_2", CubeListBuilder.create()
                .texOffs(120, 370).addBox(-1.012F, -0.5F, -0.6F, 2.024F, 5.4091F, 1.2F, infla),
                PartPose.offsetAndRotation(-5F, -15.2F, -3.4F, -2.5367F, -0.5002F, 2.7166F));
        p_torso.addOrReplaceChild("mechon_0_3", CubeListBuilder.create()
                .texOffs(203, 361).addBox(-0.968F, -0.5F, -0.6F, 1.936F, 6.0319F, 1.2F, infla),
                PartPose.offsetAndRotation(-4.6F, -11.4F, -5.6F, 3.0488F, -0.5402F, 3.1096F));
        p_torso.addOrReplaceChild("mechon_1_0", CubeListBuilder.create()
                .texOffs(0, 351).addBox(-0.95F, -0.5F, -0.6F, 1.9F, 7.3178F, 1.2F, infla),
                PartPose.offsetAndRotation(-1.7162F, -23.1044F, 2.6649F, -2.751F, -0.5386F, -3.0498F));
        p_torso.addOrReplaceChild("mechon_1_1", CubeListBuilder.create()
                .texOffs(128, 370).addBox(-0.912F, -0.5F, -0.6F, 1.824F, 5.6472F, 1.2F, infla),
                PartPose.offsetAndRotation(-3.48F, -17.4F, 0.6F, -1.8564F, -0.4577F, 2.5339F));
        p_torso.addOrReplaceChild("mechon_1_2", CubeListBuilder.create()
                .texOffs(144, 370).addBox(-0.874F, -0.5F, -0.6F, 1.748F, 5.4228F, 1.2F, infla),
                PartPose.offsetAndRotation(-4.35F, -15.2F, -3.4F, -2.5409F, -0.4947F, 2.6885F));
        p_torso.addOrReplaceChild("mechon_1_3", CubeListBuilder.create()
                .texOffs(151, 370).addBox(-0.836F, -0.5F, -0.6F, 1.672F, 5.0547F, 1.2F, infla),
                PartPose.offsetAndRotation(-3.82F, -11.4F, -5.6F, 3.0264F, -0.5393F, 3.0692F));
        PartDefinition p_trompeta = p_torso.addOrReplaceChild("trompeta", CubeListBuilder.create()
                .texOffs(237, 378).addBox(-0.95F, -0.4F, -0.95F, 1.9F, 1.5F, 1.9F, infla)
                .texOffs(225, 0).addBox(-0.7F, 0.8F, -0.7F, 1.4F, 29.4F, 1.4F, infla)
                .texOffs(190, 378).addBox(-1.1F, 6F, -1.1F, 2.2F, 1.2F, 2.2F, infla)
                .texOffs(190, 378).addBox(-1.1F, 15.5F, -1.1F, 2.2F, 1.2F, 2.2F, infla)
                .texOffs(246, 378).addBox(-1F, 28.6F, -1F, 2F, 1.2F, 2F, infla),
                PartPose.offsetAndRotation(-1.2589F, -22.6276F, -3.8805F, -1.1076F, -0.7296F, -3.0494F));
        PartDefinition p_campana = p_trompeta.addOrReplaceChild("campana", CubeListBuilder.create()
                .texOffs(158, 370).addBox(-2.6F, 4F, -2.6F, 5.2F, 0.6F, 5.2F, infla),
                PartPose.offsetAndRotation(0F, 29.6F, 0F, 0F, 0F, 0F));
        p_campana.addOrReplaceChild("campana_0_0", CubeListBuilder.create()
                .texOffs(250, 303).addBox(-0.725F, -0.3F, -0.3F, 1.45F, 4.0355F, 0.6F, infla),
                PartPose.offsetAndRotation(0F, 0F, -0.75F, -0.3724F, 0F, 0F));
        p_campana.addOrReplaceChild("campana_0_1", CubeListBuilder.create()
                .texOffs(30, 378).addBox(-1.7F, -0.3F, -0.3F, 3.4F, 4.4184F, 0.6F, infla)
                .texOffs(20, 385).addBox(-2.1551F, 3.2184F, -0.75F, 4.3103F, 1.1F, 1.1F, infla),
                PartPose.offsetAndRotation(0F, 3.2F, -2F, -0.7854F, 0F, 0F));
        p_campana.addOrReplaceChild("campana_1_0", CubeListBuilder.create()
                .texOffs(250, 303).addBox(-0.725F, -0.3F, -0.3F, 1.45F, 4.0355F, 0.6F, infla),
                PartPose.offsetAndRotation(-0.5303F, 0F, -0.5303F, -0.3724F, 0.7854F, 0F));
        p_campana.addOrReplaceChild("campana_1_1", CubeListBuilder.create()
                .texOffs(30, 378).addBox(-1.7F, -0.3F, -0.3F, 3.4F, 4.4184F, 0.6F, infla)
                .texOffs(20, 385).addBox(-2.1551F, 3.2184F, -0.75F, 4.3103F, 1.1F, 1.1F, infla),
                PartPose.offsetAndRotation(-1.4142F, 3.2F, -1.4142F, -0.7854F, 0.7854F, 0F));
        p_campana.addOrReplaceChild("campana_2_0", CubeListBuilder.create()
                .texOffs(250, 303).addBox(-0.725F, -0.3F, -0.3F, 1.45F, 4.0355F, 0.6F, infla),
                PartPose.offsetAndRotation(-0.75F, 0F, 0F, -0.3724F, 1.5708F, 0F));
        p_campana.addOrReplaceChild("campana_2_1", CubeListBuilder.create()
                .texOffs(30, 378).addBox(-1.7F, -0.3F, -0.3F, 3.4F, 4.4184F, 0.6F, infla)
                .texOffs(20, 385).addBox(-2.1551F, 3.2184F, -0.75F, 4.3103F, 1.1F, 1.1F, infla),
                PartPose.offsetAndRotation(-2F, 3.2F, 0F, -0.7854F, 1.5708F, 0F));
        p_campana.addOrReplaceChild("campana_3_0", CubeListBuilder.create()
                .texOffs(250, 303).addBox(-0.725F, -0.3F, -0.3F, 1.45F, 4.0355F, 0.6F, infla),
                PartPose.offsetAndRotation(-0.5303F, 0F, 0.5303F, 2.7692F, 0.7854F, -3.1416F));
        p_campana.addOrReplaceChild("campana_3_1", CubeListBuilder.create()
                .texOffs(30, 378).addBox(-1.7F, -0.3F, -0.3F, 3.4F, 4.4184F, 0.6F, infla)
                .texOffs(20, 385).addBox(-2.1551F, 3.2184F, -0.75F, 4.3103F, 1.1F, 1.1F, infla),
                PartPose.offsetAndRotation(-1.4142F, 3.2F, 1.4142F, 2.3562F, 0.7854F, 3.1416F));
        p_campana.addOrReplaceChild("campana_4_0", CubeListBuilder.create()
                .texOffs(250, 303).addBox(-0.725F, -0.3F, -0.3F, 1.45F, 4.0355F, 0.6F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0.75F, 2.7692F, 0F, 3.1416F));
        p_campana.addOrReplaceChild("campana_4_1", CubeListBuilder.create()
                .texOffs(30, 378).addBox(-1.7F, -0.3F, -0.3F, 3.4F, 4.4184F, 0.6F, infla)
                .texOffs(20, 385).addBox(-2.1551F, 3.2184F, -0.75F, 4.3103F, 1.1F, 1.1F, infla),
                PartPose.offsetAndRotation(0F, 3.2F, 2F, 2.3562F, 0F, 3.1416F));
        p_campana.addOrReplaceChild("campana_5_0", CubeListBuilder.create()
                .texOffs(250, 303).addBox(-0.725F, -0.3F, -0.3F, 1.45F, 4.0355F, 0.6F, infla),
                PartPose.offsetAndRotation(0.5303F, 0F, 0.5303F, 2.7692F, -0.7854F, -3.1416F));
        p_campana.addOrReplaceChild("campana_5_1", CubeListBuilder.create()
                .texOffs(30, 378).addBox(-1.7F, -0.3F, -0.3F, 3.4F, 4.4184F, 0.6F, infla)
                .texOffs(20, 385).addBox(-2.1551F, 3.2184F, -0.75F, 4.3103F, 1.1F, 1.1F, infla),
                PartPose.offsetAndRotation(1.4142F, 3.2F, 1.4142F, 2.3562F, -0.7854F, 3.1416F));
        p_campana.addOrReplaceChild("campana_6_0", CubeListBuilder.create()
                .texOffs(250, 303).addBox(-0.725F, -0.3F, -0.3F, 1.45F, 4.0355F, 0.6F, infla),
                PartPose.offsetAndRotation(0.75F, 0F, 0F, -0.3724F, -1.5708F, 0F));
        p_campana.addOrReplaceChild("campana_6_1", CubeListBuilder.create()
                .texOffs(30, 378).addBox(-1.7F, -0.3F, -0.3F, 3.4F, 4.4184F, 0.6F, infla)
                .texOffs(20, 385).addBox(-2.1551F, 3.2184F, -0.75F, 4.3103F, 1.1F, 1.1F, infla),
                PartPose.offsetAndRotation(2F, 3.2F, 0F, -0.7854F, -1.5708F, 0F));
        p_campana.addOrReplaceChild("campana_7_0", CubeListBuilder.create()
                .texOffs(250, 303).addBox(-0.725F, -0.3F, -0.3F, 1.45F, 4.0355F, 0.6F, infla),
                PartPose.offsetAndRotation(0.5303F, 0F, -0.5303F, -0.3724F, -0.7854F, 0F));
        p_campana.addOrReplaceChild("campana_7_1", CubeListBuilder.create()
                .texOffs(30, 378).addBox(-1.7F, -0.3F, -0.3F, 3.4F, 4.4184F, 0.6F, infla)
                .texOffs(20, 385).addBox(-2.1551F, 3.2184F, -0.75F, 4.3103F, 1.1F, 1.1F, infla),
                PartPose.offsetAndRotation(1.4142F, 3.2F, -1.4142F, -0.7854F, -0.7854F, 0F));
        p_campana.addOrReplaceChild("campana_luz", CubeListBuilder.create()
                .texOffs(158, 370).addBox(-2.6F, 4.05F, -2.6F, 5.2F, 0.6F, 5.2F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0.7854F, 0F));
        PartDefinition p_brazo_izq = p_torso.addOrReplaceChild("brazo_izq", CubeListBuilder.create()
                .texOffs(153, 351).addBox(-1.9F, -2F, -1.368F, 3.8F, 5F, 2.736F, infla)
                .texOffs(112, 340).addBox(-1.368F, -2F, -1.9F, 2.736F, 5F, 3.8F, infla)
                .texOffs(197, 351).addBox(-1.6F, 2.6F, -1.184F, 3.2F, 5.6F, 2.368F, infla)
                .texOffs(141, 340).addBox(-1.184F, 2.6F, -1.6F, 2.368F, 5.6F, 3.2F, infla)
                .texOffs(166, 340).addBox(-1.35F, 7.8F, -1.036F, 2.7F, 6.4F, 2.072F, infla)
                .texOffs(164, 329).addBox(-0.999F, 7.8F, -1.4F, 1.998F, 6.4F, 2.8F, infla)
                .texOffs(72, 378).addBox(-1.72F, 4.6F, -1.72F, 3.44F, 0.8F, 3.44F, infla),
                PartPose.offsetAndRotation(7.3F, -14.4F, 0.2F, -0.84F, -0.0504F, 1.5848F));
        PartDefinition p_antebrazo_izq = p_brazo_izq.addOrReplaceChild("antebrazo_izq", CubeListBuilder.create()
                .texOffs(222, 351).addBox(-1.35F, -0.9F, -1.036F, 2.7F, 5.4F, 2.072F, infla)
                .texOffs(177, 340).addBox(-0.999F, -0.9F, -1.4F, 1.998F, 5.4F, 2.8F, infla)
                .texOffs(47, 370).addBox(-1.1F, 4.2F, -0.851F, 2.2F, 4.8F, 1.702F, infla)
                .texOffs(154, 361).addBox(-0.814F, 4.2F, -1.15F, 1.628F, 4.8F, 2.3F, infla)
                .texOffs(64, 378).addBox(-0.9F, 8.6F, -0.703F, 1.8F, 4.2F, 1.406F, infla)
                .texOffs(136, 370).addBox(-0.666F, 8.6F, -0.95F, 1.332F, 4.2F, 1.9F, infla)
                .texOffs(55, 385).addBox(-1.05F, 10.3F, -1.1F, 2.1F, 0.8F, 2.2F, infla),
                PartPose.offsetAndRotation(0F, 13.4F, 0F, 0.3723F, -0.6522F, 1.1366F));
        p_antebrazo_izq.addOrReplaceChild("mano_izq", CubeListBuilder.create()
                .texOffs(233, 351).addBox(-2.2F, -0.4F, -1.7F, 1.6F, 4F, 3.4F, infla)
                .texOffs(14, 385).addBox(-0.8F, 0.1F, -2.75F, 1.2F, 2.2F, 1.1F, infla)
                .texOffs(7, 385).addBox(-0.7F, 1F, -1.66F, 2F, 2.6F, 0.78F, infla)
                .texOffs(7, 385).addBox(-0.7F, 1.15F, -0.82F, 2F, 2.6F, 0.78F, infla)
                .texOffs(7, 385).addBox(-0.7F, 1F, 0.02F, 2F, 2.6F, 0.78F, infla)
                .texOffs(7, 385).addBox(-0.7F, 1.15F, 0.86F, 2F, 2.6F, 0.78F, infla),
                PartPose.offsetAndRotation(0F, 12.2F, 0F, -2.6733F, 0.0166F, 2.5706F));
        PartDefinition p_brazo_der = p_torso.addOrReplaceChild("brazo_der", CubeListBuilder.create()
                .texOffs(153, 351).addBox(-1.9F, -2F, -1.368F, 3.8F, 5F, 2.736F, infla)
                .texOffs(112, 340).addBox(-1.368F, -2F, -1.9F, 2.736F, 5F, 3.8F, infla)
                .texOffs(197, 351).addBox(-1.6F, 2.6F, -1.184F, 3.2F, 5.6F, 2.368F, infla)
                .texOffs(141, 340).addBox(-1.184F, 2.6F, -1.6F, 2.368F, 5.6F, 3.2F, infla)
                .texOffs(166, 340).addBox(-1.35F, 7.8F, -1.036F, 2.7F, 6.4F, 2.072F, infla)
                .texOffs(164, 329).addBox(-0.999F, 7.8F, -1.4F, 1.998F, 6.4F, 2.8F, infla)
                .texOffs(72, 378).addBox(-1.72F, 4.6F, -1.72F, 3.44F, 0.8F, 3.44F, infla),
                PartPose.offsetAndRotation(-7.3F, -14.4F, 0.2F, -0.7413F, 0.0292F, 2.1232F));
        PartDefinition p_antebrazo_der = p_brazo_der.addOrReplaceChild("antebrazo_der", CubeListBuilder.create()
                .texOffs(222, 351).addBox(-1.35F, -0.9F, -1.036F, 2.7F, 5.4F, 2.072F, infla)
                .texOffs(177, 340).addBox(-0.999F, -0.9F, -1.4F, 1.998F, 5.4F, 2.8F, infla)
                .texOffs(47, 370).addBox(-1.1F, 4.2F, -0.851F, 2.2F, 4.8F, 1.702F, infla)
                .texOffs(154, 361).addBox(-0.814F, 4.2F, -1.15F, 1.628F, 4.8F, 2.3F, infla)
                .texOffs(64, 378).addBox(-0.9F, 8.6F, -0.703F, 1.8F, 4.2F, 1.406F, infla)
                .texOffs(136, 370).addBox(-0.666F, 8.6F, -0.95F, 1.332F, 4.2F, 1.9F, infla)
                .texOffs(55, 385).addBox(-1.05F, 10.3F, -1.1F, 2.1F, 0.8F, 2.2F, infla),
                PartPose.offsetAndRotation(0F, 13.4F, 0F, -0.3708F, -0.5767F, 1.2895F));
        p_antebrazo_der.addOrReplaceChild("mano_der", CubeListBuilder.create()
                .texOffs(233, 351).addBox(-2.2F, -0.4F, -1.7F, 1.6F, 4F, 3.4F, infla)
                .texOffs(14, 385).addBox(-0.8F, 0.1F, -2.75F, 1.2F, 2.2F, 1.1F, infla)
                .texOffs(7, 385).addBox(-0.7F, 1F, -1.66F, 2F, 2.6F, 0.78F, infla)
                .texOffs(7, 385).addBox(-0.7F, 1.15F, -0.82F, 2F, 2.6F, 0.78F, infla)
                .texOffs(7, 385).addBox(-0.7F, 1F, 0.02F, 2F, 2.6F, 0.78F, infla)
                .texOffs(7, 385).addBox(-0.7F, 1.15F, 0.86F, 2F, 2.6F, 0.78F, infla),
                PartPose.offsetAndRotation(0F, 12.2F, 0F, -2.4229F, 1.2004F, -2.9925F));
        entera_ala_izq(p_torso, infla);
        entera_ala_der(p_torso, infla);
        return LayerDefinition.create(malla, 256, 512);
    }

    private static void entera_pedestal(PartDefinition p_estatua, CubeDeformation infla) {
        PartDefinition p_pedestal = p_estatua.addOrReplaceChild("pedestal", CubeListBuilder.create()
                .texOffs(0, 98).addBox(-15F, 20.5F, -15F, 30F, 3.5F, 30F, infla)
                .texOffs(0, 133).addBox(-14.4F, 19.4F, -14.4F, 28.8F, 1.1F, 28.8F, infla)
                .texOffs(0, 164).addBox(-13.7F, 18.3F, -13.7F, 27.4F, 1.1F, 27.4F, infla)
                .texOffs(121, 98).addBox(-12.5F, 9.4F, -12.5F, 25F, 8.9F, 25F, infla)
                .texOffs(0, 164).addBox(-13.7F, 8.3F, -13.7F, 27.4F, 1.1F, 27.4F, infla)
                .texOffs(117, 133).addBox(-14.3F, 7.3F, -14.3F, 28.6F, 1F, 28.6F, infla)
                .texOffs(111, 164).addBox(-13.5F, 6F, -13.5F, 27F, 1.3F, 27F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        p_pedestal.addOrReplaceChild("pedestal_sol0", CubeListBuilder.create()
                .texOffs(99, 378).addBox(-2.2F, -2.2F, -0.55F, 4.4F, 4.4F, 0.6F, infla),
                PartPose.offsetAndRotation(0F, 13.85F, -12.5F, 0F, 0F, 0F));
        p_pedestal.addOrReplaceChild("pedestal_rayos0", CubeListBuilder.create()
                .texOffs(120, 378).addBox(-2F, -2F, -0.35F, 4F, 4F, 0.4F, infla)
                .texOffs(251, 0).addBox(-0.5F, -3.4F, -0.3F, 1F, 6.8F, 0.3F, infla)
                .texOffs(83, 385).addBox(-3.4F, -0.5F, -0.3F, 6.8F, 1F, 0.3F, infla),
                PartPose.offsetAndRotation(0F, 13.85F, -12.5F, 0F, 0F, 0.7854F));
        p_pedestal.addOrReplaceChild("pedestal_sol1", CubeListBuilder.create()
                .texOffs(99, 378).addBox(-2.2F, -2.2F, -0.55F, 4.4F, 4.4F, 0.6F, infla),
                PartPose.offsetAndRotation(-12.5F, 13.85F, 0F, 0F, 1.5708F, 0F));
        p_pedestal.addOrReplaceChild("pedestal_rayos1", CubeListBuilder.create()
                .texOffs(120, 378).addBox(-2F, -2F, -0.35F, 4F, 4F, 0.4F, infla)
                .texOffs(251, 0).addBox(-0.5F, -3.4F, -0.3F, 1F, 6.8F, 0.3F, infla)
                .texOffs(83, 385).addBox(-3.4F, -0.5F, -0.3F, 6.8F, 1F, 0.3F, infla),
                PartPose.offsetAndRotation(-12.5F, 13.85F, 0F, 1.5708F, 0.7854F, 1.5708F));
        p_pedestal.addOrReplaceChild("pedestal_sol2", CubeListBuilder.create()
                .texOffs(99, 378).addBox(-2.2F, -2.2F, -0.55F, 4.4F, 4.4F, 0.6F, infla),
                PartPose.offsetAndRotation(0F, 13.85F, 12.5F, 3.1416F, 0F, 3.1416F));
        p_pedestal.addOrReplaceChild("pedestal_rayos2", CubeListBuilder.create()
                .texOffs(120, 378).addBox(-2F, -2F, -0.35F, 4F, 4F, 0.4F, infla)
                .texOffs(251, 0).addBox(-0.5F, -3.4F, -0.3F, 1F, 6.8F, 0.3F, infla)
                .texOffs(83, 385).addBox(-3.4F, -0.5F, -0.3F, 6.8F, 1F, 0.3F, infla),
                PartPose.offsetAndRotation(0F, 13.85F, 12.5F, 3.1416F, 0F, 2.3562F));
        p_pedestal.addOrReplaceChild("pedestal_sol3", CubeListBuilder.create()
                .texOffs(99, 378).addBox(-2.2F, -2.2F, -0.55F, 4.4F, 4.4F, 0.6F, infla),
                PartPose.offsetAndRotation(12.5F, 13.85F, 0F, 0F, -1.5708F, 0F));
        p_pedestal.addOrReplaceChild("pedestal_rayos3", CubeListBuilder.create()
                .texOffs(120, 378).addBox(-2F, -2F, -0.35F, 4F, 4F, 0.4F, infla)
                .texOffs(251, 0).addBox(-0.5F, -3.4F, -0.3F, 1F, 6.8F, 0.3F, infla)
                .texOffs(83, 385).addBox(-3.4F, -0.5F, -0.3F, 6.8F, 1F, 0.3F, infla),
                PartPose.offsetAndRotation(12.5F, 13.85F, 0F, -1.5708F, -0.7854F, 1.5708F));
    }

    private static void entera_falda(PartDefinition p_estatua, CubeDeformation infla) {
        PartDefinition p_falda = p_estatua.addOrReplaceChild("falda", CubeListBuilder.create(),
                PartPose.offsetAndRotation(0F, -53F, 0F, 0F, 0F, 0F));
        p_falda.addOrReplaceChild("falda_0_0", CubeListBuilder.create()
                .texOffs(146, 288).addBox(-1.4543F, -0.5F, -0.9F, 2.9087F, 10.4425F, 1.8F, infla),
                PartPose.offsetAndRotation(0F, 0.3F, -4.45F, -0.1703F, 0F, 0.151F));
        p_falda.addOrReplaceChild("falda_0_1", CubeListBuilder.create()
                .texOffs(235, 98).addBox(-1.9499F, -0.5F, -0.9F, 3.8999F, 27.0578F, 1.8F, infla)
                .texOffs(246, 164).addBox(-0.6F, -0.2F, -1.6F, 1.2F, 26.4578F, 1F, infla),
                PartPose.offsetAndRotation(-1.4F, 9.5F, -6.05F, -0.0591F, 0F, -0.0308F));
        p_falda.addOrReplaceChild("falda_0_2", CubeListBuilder.create()
                .texOffs(42, 223).addBox(-2.4135F, -0.5F, -0.9F, 4.8269F, 23.8537F, 1.8F, infla)
                .texOffs(173, 223).addBox(-0.6F, -0.2F, -1.6F, 1.2F, 23.2537F, 1F, infla)
                .texOffs(136, 378).addBox(-2.4635F, 21.7537F, -1.2F, 4.9269F, 1.5F, 2.15F, infla),
                PartPose.offsetAndRotation(-0.6F, 35.5F, -7.5883F, -0.0859F, 0F, -0.0132F));
        p_falda.addOrReplaceChild("falda_1_0", CubeListBuilder.create()
                .texOffs(157, 288).addBox(-1.4543F, -0.5F, -0.9F, 2.9087F, 10.9634F, 1.8F, infla),
                PartPose.offsetAndRotation(1.9776F, 0.3F, -3.182F, -0.1562F, -0.2677F, 0.0462F));
        p_falda.addOrReplaceChild("falda_1_1", CubeListBuilder.create()
                .texOffs(233, 133).addBox(-1.9499F, -0.5F, -0.9F, 3.8999F, 26.7215F, 1.8F, infla),
                PartPose.offsetAndRotation(1.9331F, 10.1506F, -4.6769F, -0.1586F, -0.2583F, -0.0336F));
        p_falda.addOrReplaceChild("falda_1_2", CubeListBuilder.create()
                .texOffs(57, 223).addBox(-2.4135F, -0.5F, -0.9F, 4.8269F, 23.8177F, 1.8F, infla)
                .texOffs(136, 378).addBox(-2.4635F, 21.7177F, -1.2F, 4.9269F, 1.5F, 2.15F, infla),
                PartPose.offsetAndRotation(3.8239F, 35.5F, -8.6043F, 0.028F, -0.2814F, -0.0293F));
        p_falda.addOrReplaceChild("falda_2_0", CubeListBuilder.create()
                .texOffs(245, 251).addBox(-1.4543F, -0.5F, -0.9F, 2.9087F, 11.5247F, 1.8F, infla),
                PartPose.offsetAndRotation(4.2096F, 0.3F, -3.2357F, -0.1392F, -0.5905F, -0.0224F));
        p_falda.addOrReplaceChild("falda_2_1", CubeListBuilder.create()
                .texOffs(150, 194).addBox(-1.9499F, -0.5F, -0.9F, 3.8999F, 26.1423F, 1.8F, infla)
                .texOffs(30, 223).addBox(-0.6F, -0.2F, -1.6F, 1.2F, 25.5423F, 1F, infla),
                PartPose.offsetAndRotation(5.2557F, 10.7021F, -4.4485F, -0.1427F, -0.5765F, -0.0368F));
        p_falda.addOrReplaceChild("falda_2_2", CubeListBuilder.create()
                .texOffs(221, 194).addBox(-2.4135F, -0.5F, -0.9F, 4.8269F, 24.3878F, 1.8F, infla)
                .texOffs(179, 223).addBox(-0.6F, -0.2F, -1.6F, 1.2F, 23.7878F, 1F, infla)
                .texOffs(136, 378).addBox(-2.4635F, 22.2878F, -1.2F, 4.9269F, 1.5F, 2.15F, infla),
                PartPose.offsetAndRotation(8.1204F, 35.5F, -7.4472F, 0.0176F, -0.6222F, -0.0394F));
        p_falda.addOrReplaceChild("falda_3_0", CubeListBuilder.create()
                .texOffs(198, 272).addBox(-1.4543F, -0.5F, -0.9F, 2.9087F, 11.9477F, 1.8F, infla),
                PartPose.offsetAndRotation(4.6905F, 0.3F, -1.3049F, -0.1166F, -1.0239F, -0.0701F));
        p_falda.addOrReplaceChild("falda_3_1", CubeListBuilder.create()
                .texOffs(163, 194).addBox(-1.9499F, -0.5F, -0.9F, 3.8999F, 25.5022F, 1.8F, infla),
                PartPose.offsetAndRotation(6.5368F, 11.0706F, -1.9671F, -0.0485F, -1.0163F, -0.0315F));
        p_falda.addOrReplaceChild("falda_3_2", CubeListBuilder.create()
                .texOffs(236, 194).addBox(-2.4135F, -0.5F, -0.9F, 4.8269F, 25.1118F, 1.8F, infla)
                .texOffs(136, 378).addBox(-2.4635F, 23.0118F, -1.2F, 4.9269F, 1.5F, 2.15F, infla),
                PartPose.offsetAndRotation(8.3173F, 35.5F, -2.593F, -0.0855F, -1.0641F, -0.0267F));
        p_falda.addOrReplaceChild("falda_4_0", CubeListBuilder.create()
                .texOffs(209, 272).addBox(-1.4543F, -0.5F, -0.9F, 2.9087F, 12.1005F, 1.8F, infla),
                PartPose.offsetAndRotation(6.05F, 0.3F, 0F, -0.1903F, -1.5708F, 0F));
        p_falda.addOrReplaceChild("falda_4_1", CubeListBuilder.create()
                .texOffs(176, 194).addBox(-1.9499F, -0.5F, -0.9F, 3.8999F, 25.3413F, 1.8F, infla)
                .texOffs(72, 223).addBox(-0.6F, -0.2F, -1.6F, 1.2F, 24.7413F, 1F, infla),
                PartPose.offsetAndRotation(8.15F, 11.2F, 0F, -0.0583F, -1.5708F, 0F));
        p_falda.addOrReplaceChild("falda_4_2", CubeListBuilder.create()
                .texOffs(0, 194).addBox(-2.4135F, -0.5F, -0.9F, 4.8269F, 25.3877F, 1.8F, infla)
                .texOffs(78, 223).addBox(-0.6F, -0.2F, -1.6F, 1.2F, 24.7877F, 1F, infla)
                .texOffs(136, 378).addBox(-2.4635F, 23.2877F, -1.2F, 4.9269F, 1.5F, 2.15F, infla),
                PartPose.offsetAndRotation(9.5675F, 35.5F, 0F, -0.1267F, -1.5708F, 0F));
        p_falda.addOrReplaceChild("falda_5_0", CubeListBuilder.create()
                .texOffs(220, 272).addBox(-1.4543F, -0.5F, -0.9F, 2.9087F, 11.9532F, 1.8F, infla),
                PartPose.offsetAndRotation(4.6878F, 0.3F, 1.3536F, 3.0041F, -1.0436F, 3.0911F));
        p_falda.addOrReplaceChild("falda_5_1", CubeListBuilder.create()
                .texOffs(189, 194).addBox(-1.9499F, -0.5F, -0.9F, 3.8999F, 25.4701F, 1.8F, infla),
                PartPose.offsetAndRotation(6.5306F, 11.0706F, 2.1088F, 3.1067F, -1.0449F, 3.1168F));
        p_falda.addOrReplaceChild("falda_5_2", CubeListBuilder.create()
                .texOffs(15, 194).addBox(-2.4135F, -0.5F, -0.9F, 4.8269F, 25.4167F, 1.8F, infla)
                .texOffs(136, 378).addBox(-2.4635F, 23.3167F, -1.2F, 4.9269F, 1.5F, 2.15F, infla),
                PartPose.offsetAndRotation(7.8754F, 35.5F, 2.5373F, 3.0044F, -1.1013F, -3.1372F));
        p_falda.addOrReplaceChild("falda_6_0", CubeListBuilder.create()
                .texOffs(231, 272).addBox(-1.4543F, -0.5F, -0.9F, 2.9087F, 11.5636F, 1.8F, infla),
                PartPose.offsetAndRotation(4.2207F, 0.3F, 3.3776F, 2.9645F, -0.6277F, -3.1382F));
        p_falda.addOrReplaceChild("falda_6_1", CubeListBuilder.create()
                .texOffs(202, 194).addBox(-1.9499F, -0.5F, -0.9F, 3.8999F, 25.8418F, 1.8F, infla)
                .texOffs(36, 223).addBox(-0.6F, -0.2F, -1.6F, 1.2F, 25.2418F, 1F, infla),
                PartPose.offsetAndRotation(5.2783F, 10.7021F, 4.8836F, 3.1021F, -0.6327F, 3.1148F));
        p_falda.addOrReplaceChild("falda_6_2", CubeListBuilder.create()
                .texOffs(30, 194).addBox(-2.4135F, -0.5F, -0.9F, 4.8269F, 25.4835F, 1.8F, infla)
                .texOffs(84, 223).addBox(-0.6F, -0.2F, -1.6F, 1.2F, 24.8835F, 1F, infla)
                .texOffs(136, 378).addBox(-2.4635F, 23.3835F, -1.2F, 4.9269F, 1.5F, 2.15F, infla),
                PartPose.offsetAndRotation(6.5243F, 35.5F, 5.6748F, 2.9855F, -0.7038F, -3.1356F));
        p_falda.addOrReplaceChild("falda_7_0", CubeListBuilder.create()
                .texOffs(168, 288).addBox(-1.4543F, -0.5F, -0.9F, 2.9087F, 11.0534F, 1.8F, infla),
                PartPose.offsetAndRotation(1.9694F, 0.3F, 3.4406F, 2.9312F, -0.2947F, -3.0744F));
        p_falda.addOrReplaceChild("falda_7_1", CubeListBuilder.create()
                .texOffs(220, 164).addBox(-1.9499F, -0.5F, -0.9F, 3.8999F, 26.3936F, 1.8F, infla),
                PartPose.offsetAndRotation(1.9176F, 10.1506F, 5.4493F, 3.0963F, -0.2999F, 3.1149F));
        p_falda.addOrReplaceChild("falda_7_2", CubeListBuilder.create()
                .texOffs(45, 194).addBox(-2.4135F, -0.5F, -0.9F, 4.8269F, 25.5676F, 1.8F, infla)
                .texOffs(136, 378).addBox(-2.4635F, 23.4676F, -1.2F, 4.9269F, 1.5F, 2.15F, infla),
                PartPose.offsetAndRotation(2.9344F, 35.5F, 6.5479F, 2.967F, -0.3464F, -3.1373F));
        p_falda.addOrReplaceChild("falda_8_0", CubeListBuilder.create()
                .texOffs(179, 288).addBox(-1.4543F, -0.5F, -0.9F, 2.9087F, 10.5624F, 1.8F, infla),
                PartPose.offsetAndRotation(0F, 0.3F, 4.75F, 2.9094F, 0F, -2.9906F));
        p_falda.addOrReplaceChild("falda_8_1", CubeListBuilder.create()
                .texOffs(233, 164).addBox(-1.9499F, -0.5F, -0.9F, 3.8999F, 27.04F, 1.8F, infla)
                .texOffs(215, 194).addBox(-0.6F, -0.2F, -1.6F, 1.2F, 26.44F, 1F, infla),
                PartPose.offsetAndRotation(-1.4F, 9.5F, 6.95F, 3.0955F, 0F, 3.1108F));
        p_falda.addOrReplaceChild("falda_8_2", CubeListBuilder.create()
                .texOffs(60, 194).addBox(-2.4135F, -0.5F, -0.9F, 4.8269F, 25.5986F, 1.8F, infla)
                .texOffs(90, 223).addBox(-0.6F, -0.2F, -1.6F, 1.2F, 24.9986F, 1F, infla)
                .texOffs(136, 378).addBox(-2.4635F, 23.4986F, -1.2F, 4.9269F, 1.5F, 2.15F, infla),
                PartPose.offsetAndRotation(-0.6F, 35.5F, 8.15F, 2.9618F, 0F, 3.1292F));
        p_falda.addOrReplaceChild("falda_9_0", CubeListBuilder.create()
                .texOffs(190, 288).addBox(-1.4543F, -0.5F, -0.9F, 2.9087F, 10.2022F, 1.8F, infla),
                PartPose.offsetAndRotation(-1.9694F, 0.3F, 3.4406F, 2.912F, 0.287F, -2.8966F));
        p_falda.addOrReplaceChild("falda_9_1", CubeListBuilder.create()
                .texOffs(232, 0).addBox(-1.9499F, -0.5F, -0.9F, 3.8999F, 27.6796F, 1.8F, infla),
                PartPose.offsetAndRotation(-4.7176F, 8.8494F, 5.4493F, 3.0985F, 0.2998F, 3.107F));
        p_falda.addOrReplaceChild("falda_9_2", CubeListBuilder.create()
                .texOffs(75, 194).addBox(-2.4135F, -0.5F, -0.9F, 4.8269F, 25.5421F, 1.8F, infla)
                .texOffs(136, 378).addBox(-2.4635F, 23.4421F, -1.2F, 4.9269F, 1.5F, 2.15F, infla),
                PartPose.offsetAndRotation(-4.1344F, 35.5F, 6.5479F, 2.9668F, 0.3463F, 3.1125F));
        p_falda.addOrReplaceChild("falda_10_0", CubeListBuilder.create()
                .texOffs(62, 303).addBox(-1.4543F, -0.5F, -0.9F, 2.9087F, 10.0064F, 1.8F, infla),
                PartPose.offsetAndRotation(-4.2207F, 0.3F, 3.3776F, 2.9374F, 0.6011F, -2.8088F));
        p_falda.addOrReplaceChild("falda_10_1", CubeListBuilder.create()
                .texOffs(160, 0).addBox(-1.9499F, -0.5F, -0.9F, 3.8999F, 28.2159F, 1.8F, infla)
                .texOffs(248, 98).addBox(-0.6F, -0.2F, -1.6F, 1.2F, 27.6159F, 1F, infla),
                PartPose.offsetAndRotation(-8.0783F, 8.2979F, 4.8836F, 3.1055F, 0.6326F, 3.1073F));
        p_falda.addOrReplaceChild("falda_10_2", CubeListBuilder.create()
                .texOffs(90, 194).addBox(-2.4135F, -0.5F, -0.9F, 4.8269F, 25.4339F, 1.8F, infla)
                .texOffs(96, 223).addBox(-0.6F, -0.2F, -1.6F, 1.2F, 24.8339F, 1F, infla)
                .texOffs(136, 378).addBox(-2.4635F, 23.3339F, -1.2F, 4.9269F, 1.5F, 2.15F, infla),
                PartPose.offsetAndRotation(-7.7243F, 35.5F, 5.6748F, 2.9852F, 0.7036F, 3.1108F));
        p_falda.addOrReplaceChild("falda_11_0", CubeListBuilder.create()
                .texOffs(73, 303).addBox(-1.4543F, -0.5F, -0.9F, 2.9087F, 9.9629F, 1.8F, infla),
                PartPose.offsetAndRotation(-4.6878F, 0.3F, 1.3536F, 2.9837F, 1.0051F, -2.7285F));
        p_falda.addOrReplaceChild("falda_11_1", CubeListBuilder.create()
                .texOffs(173, 0).addBox(-1.9499F, -0.5F, -0.9F, 3.8999F, 28.5751F, 1.8F, infla),
                PartPose.offsetAndRotation(-9.3306F, 7.9294F, 2.1088F, 3.1106F, 1.0447F, 3.1056F));
        p_falda.addOrReplaceChild("falda_11_2", CubeListBuilder.create()
                .texOffs(105, 194).addBox(-2.4135F, -0.5F, -0.9F, 4.8269F, 25.3534F, 1.8F, infla)
                .texOffs(136, 378).addBox(-2.4635F, 23.2534F, -1.2F, 4.9269F, 1.5F, 2.15F, infla),
                PartPose.offsetAndRotation(-9.0753F, 35.5F, 2.5373F, 3.004F, 1.1012F, 3.1124F));
        p_falda.addOrReplaceChild("falda_12_0", CubeListBuilder.create()
                .texOffs(84, 303).addBox(-1.4543F, -0.5F, -0.9F, 2.9087F, 9.9588F, 1.8F, infla),
                PartPose.offsetAndRotation(-6.05F, 0.3F, 0F, -0.5787F, 1.5708F, 0F));
        p_falda.addOrReplaceChild("falda_12_1", CubeListBuilder.create()
                .texOffs(186, 0).addBox(-1.9499F, -0.5F, -0.9F, 3.8999F, 28.7007F, 1.8F, infla)
                .texOffs(245, 0).addBox(-0.6F, -0.2F, -1.6F, 1.2F, 28.1007F, 1F, infla),
                PartPose.offsetAndRotation(-10.95F, 7.8F, 0F, 0.0072F, 1.5708F, 0F));
        p_falda.addOrReplaceChild("falda_12_2", CubeListBuilder.create()
                .texOffs(120, 194).addBox(-2.4135F, -0.5F, -0.9F, 4.8269F, 25.3288F, 1.8F, infla)
                .texOffs(102, 223).addBox(-0.6F, -0.2F, -1.6F, 1.2F, 24.7288F, 1F, infla)
                .texOffs(136, 378).addBox(-2.4635F, 23.2288F, -1.2F, 4.9269F, 1.5F, 2.15F, infla),
                PartPose.offsetAndRotation(-10.75F, 35.5F, 0F, -0.1029F, 1.5708F, 0F));
        p_falda.addOrReplaceChild("falda_13_0", CubeListBuilder.create()
                .texOffs(95, 303).addBox(-1.4543F, -0.5F, -0.9F, 2.9087F, 9.9574F, 1.8F, infla),
                PartPose.offsetAndRotation(-4.6905F, 0.3F, -1.3049F, -0.1332F, 0.9805F, 0.4361F));
        p_falda.addOrReplaceChild("falda_13_1", CubeListBuilder.create()
                .texOffs(199, 0).addBox(-1.9499F, -0.5F, -0.9F, 3.8999F, 28.5742F, 1.8F, infla),
                PartPose.offsetAndRotation(-9.3368F, 7.9294F, -1.9671F, -0.0253F, 1.0163F, -0.0308F));
        p_falda.addOrReplaceChild("falda_13_2", CubeListBuilder.create()
                .texOffs(135, 194).addBox(-2.4135F, -0.5F, -0.9F, 4.8269F, 25.324F, 1.8F, infla)
                .texOffs(136, 378).addBox(-2.4635F, 23.224F, -1.2F, 4.9269F, 1.5F, 2.15F, infla),
                PartPose.offsetAndRotation(-9.0822F, 35.5F, -2.3348F, -0.1067F, 1.0643F, 0.0004F));
        p_falda.addOrReplaceChild("falda_14_0", CubeListBuilder.create()
                .texOffs(95, 303).addBox(-1.4543F, -0.5F, -0.9F, 2.9087F, 9.9571F, 1.8F, infla),
                PartPose.offsetAndRotation(-4.2096F, 0.3F, -3.2357F, -0.1605F, 0.56F, 0.3625F));
        p_falda.addOrReplaceChild("falda_14_1", CubeListBuilder.create()
                .texOffs(212, 0).addBox(-1.9499F, -0.5F, -0.9F, 3.8999F, 28.211F, 1.8F, infla)
                .texOffs(246, 133).addBox(-0.6F, -0.2F, -1.6F, 1.2F, 27.611F, 1F, infla),
                PartPose.offsetAndRotation(-8.0557F, 8.2979F, -4.4485F, -0.0262F, 0.5766F, -0.0275F));
        p_falda.addOrReplaceChild("falda_14_2", CubeListBuilder.create()
                .texOffs(0, 223).addBox(-2.4135F, -0.5F, -0.9F, 4.8269F, 25.0666F, 1.8F, infla)
                .texOffs(108, 223).addBox(-0.6F, -0.2F, -1.6F, 1.2F, 24.4666F, 1F, infla)
                .texOffs(136, 378).addBox(-2.4635F, 22.9666F, -1.2F, 4.9269F, 1.5F, 2.15F, infla),
                PartPose.offsetAndRotation(-7.6964F, 35.5F, -5.0453F, -0.1059F, 0.6226F, 0.0092F));
        p_falda.addOrReplaceChild("falda_15_0", CubeListBuilder.create()
                .texOffs(106, 303).addBox(-1.4543F, -0.5F, -0.9F, 2.9087F, 10.1061F, 1.8F, infla),
                PartPose.offsetAndRotation(-1.9776F, 0.3F, -3.182F, -0.1706F, 0.2588F, 0.2677F));
        p_falda.addOrReplaceChild("falda_15_1", CubeListBuilder.create()
                .texOffs(222, 98).addBox(-1.9499F, -0.5F, -0.9F, 3.8999F, 27.6683F, 1.8F, infla),
                PartPose.offsetAndRotation(-4.7331F, 8.8494F, -4.6769F, -0.0305F, 0.2583F, -0.0292F));
        p_falda.addOrReplaceChild("falda_15_2", CubeListBuilder.create()
                .texOffs(15, 223).addBox(-2.4135F, -0.5F, -0.9F, 4.8269F, 24.4487F, 1.8F, infla)
                .texOffs(136, 378).addBox(-2.4635F, 22.3487F, -1.2F, 4.9269F, 1.5F, 2.15F, infla),
                PartPose.offsetAndRotation(-4.1635F, 35.5F, -5.4638F, -0.1124F, 0.2815F, 0.0009F));
        p_falda.addOrReplaceChild("sobre_0_0", CubeListBuilder.create()
                .texOffs(201, 288).addBox(-1.5798F, -0.5F, -0.75F, 3.1596F, 10.5859F, 1.5F, infla),
                PartPose.offsetAndRotation(0F, 0.3F, -4.65F, -0.2423F, 0F, 0.151F));
        p_falda.addOrReplaceChild("sobre_0_1", CubeListBuilder.create()
                .texOffs(172, 272).addBox(-2.0921F, -0.5F, -0.75F, 4.1842F, 12.0612F, 1.5F, infla)
                .texOffs(245, 288).addBox(-0.6F, -0.2F, -1.45F, 1.2F, 11.4612F, 1F, infla)
                .texOffs(152, 378).addBox(-2.1421F, 9.9612F, -1.05F, 4.2842F, 1.5F, 1.85F, infla),
                PartPose.offsetAndRotation(-1.4F, 9.5F, -6.95F, -0.095F, 0F, -0.0454F));
        p_falda.addOrReplaceChild("sobre_1_0", CubeListBuilder.create()
                .texOffs(212, 288).addBox(-1.5798F, -0.5F, -0.75F, 3.1596F, 11.084F, 1.5F, infla),
                PartPose.offsetAndRotation(2.0526F, 0.3F, -3.3637F, -0.2231F, -0.2763F, 0.0396F));
        p_falda.addOrReplaceChild("sobre_1_1", CubeListBuilder.create()
                .texOffs(15, 272).addBox(-2.0921F, -0.5F, -0.75F, 4.1842F, 13.0239F, 1.5F, infla)
                .texOffs(152, 378).addBox(-2.1421F, 10.9239F, -1.05F, 4.2842F, 1.5F, 1.85F, infla),
                PartPose.offsetAndRotation(2.2716F, 10.1506F, -5.5099F, -0.154F, -0.2653F, -0.0521F));
        p_falda.addOrReplaceChild("sobre_2_0", CubeListBuilder.create()
                .texOffs(242, 272).addBox(-1.5798F, -0.5F, -0.75F, 3.1596F, 11.6555F, 1.5F, infla),
                PartPose.offsetAndRotation(4.3532F, 0.3F, -3.3653F, -0.1966F, -0.6048F, -0.0351F));
        p_falda.addOrReplaceChild("sobre_2_1", CubeListBuilder.create()
                .texOffs(122, 251).addBox(-2.0921F, -0.5F, -0.75F, 4.1842F, 15.0955F, 1.5F, infla)
                .texOffs(206, 251).addBox(-0.6F, -0.2F, -1.45F, 1.2F, 14.4955F, 1F, infla)
                .texOffs(152, 378).addBox(-2.1421F, 12.9955F, -1.05F, 4.2842F, 1.5F, 1.85F, infla),
                PartPose.offsetAndRotation(5.9032F, 10.7021F, -5.0778F, -0.1191F, -0.5876F, -0.0515F));
        p_falda.addOrReplaceChild("sobre_3_0", CubeListBuilder.create()
                .texOffs(0, 288).addBox(-1.5798F, -0.5F, -0.75F, 3.1596F, 12.095F, 1.5F, infla),
                PartPose.offsetAndRotation(4.8747F, 0.3F, -1.3706F, -0.1687F, -1.036F, -0.0815F));
        p_falda.addOrReplaceChild("sobre_3_1", CubeListBuilder.create()
                .texOffs(41, 251).addBox(-2.0921F, -0.5F, -0.75F, 4.1842F, 17.0991F, 1.5F, infla)
                .texOffs(152, 378).addBox(-2.1421F, 14.9991F, -1.05F, 4.2842F, 1.5F, 1.85F, infla),
                PartPose.offsetAndRotation(7.3629F, 11.0706F, -2.32F, -0.0506F, -1.0245F, -0.0464F));
        p_falda.addOrReplaceChild("sobre_4_0", CubeListBuilder.create()
                .texOffs(11, 288).addBox(-1.5798F, -0.5F, -0.75F, 3.1596F, 12.2539F, 1.5F, infla),
                PartPose.offsetAndRotation(6.25F, 0.3F, 0F, -0.2514F, -1.5708F, 0F));
        p_falda.addOrReplaceChild("sobre_4_1", CubeListBuilder.create()
                .texOffs(15, 251).addBox(-2.0921F, -0.5F, -0.75F, 4.1842F, 17.9449F, 1.5F, infla)
                .texOffs(80, 251).addBox(-0.6F, -0.2F, -1.45F, 1.2F, 17.3449F, 1F, infla)
                .texOffs(152, 378).addBox(-2.1421F, 15.8449F, -1.05F, 4.2842F, 1.5F, 1.85F, infla),
                PartPose.offsetAndRotation(9.05F, 11.2F, 0F, -0.0728F, -1.5708F, 0F));
        p_falda.addOrReplaceChild("sobre_5_0", CubeListBuilder.create()
                .texOffs(22, 288).addBox(-1.5798F, -0.5F, -0.75F, 3.1596F, 12.104F, 1.5F, infla),
                PartPose.offsetAndRotation(4.873F, 0.3F, 1.4029F, 2.9484F, -1.0517F, 3.0831F));
        p_falda.addOrReplaceChild("sobre_5_1", CubeListBuilder.create()
                .texOffs(54, 251).addBox(-2.0921F, -0.5F, -0.75F, 4.1842F, 17.0719F, 1.5F, infla)
                .texOffs(152, 378).addBox(-2.1421F, 14.9719F, -1.05F, 4.2842F, 1.5F, 1.85F, infla),
                PartPose.offsetAndRotation(7.3578F, 11.0706F, 2.4604F, 3.1092F, -1.0468F, 3.0983F));
        p_falda.addOrReplaceChild("sobre_6_0", CubeListBuilder.create()
                .texOffs(33, 288).addBox(-1.5798F, -0.5F, -0.75F, 3.1596F, 11.7175F, 1.5F, infla),
                PartPose.offsetAndRotation(4.3603F, 0.3F, 3.46F, 2.9012F, -0.6349F, 3.1368F));
        p_falda.addOrReplaceChild("sobre_6_1", CubeListBuilder.create()
                .texOffs(135, 251).addBox(-2.0921F, -0.5F, -0.75F, 4.1842F, 14.9734F, 1.5F, infla)
                .texOffs(212, 251).addBox(-0.6F, -0.2F, -1.45F, 1.2F, 14.3734F, 1F, infla)
                .texOffs(152, 378).addBox(-2.1421F, 12.8734F, -1.05F, 4.2842F, 1.5F, 1.85F, infla),
                PartPose.offsetAndRotation(5.9229F, 10.7021F, 5.5142F, 3.0989F, -0.6317F, 3.0951F));
        p_falda.addOrReplaceChild("sobre_7_0", CubeListBuilder.create()
                .texOffs(223, 288).addBox(-1.5798F, -0.5F, -0.75F, 3.1596F, 11.2283F, 1.5F, infla),
                PartPose.offsetAndRotation(2.0473F, 0.3F, 3.5361F, 2.8569F, -0.2982F, -3.0772F));
        p_falda.addOrReplaceChild("sobre_7_1", CubeListBuilder.create()
                .texOffs(28, 272).addBox(-2.0921F, -0.5F, -0.75F, 4.1842F, 12.8826F, 1.5F, infla)
                .texOffs(152, 378).addBox(-2.1421F, 10.7826F, -1.05F, 4.2842F, 1.5F, 1.85F, infla),
                PartPose.offsetAndRotation(2.2577F, 10.1506F, 6.2821F, 3.0849F, -0.2981F, 3.0937F));
        p_falda.addOrReplaceChild("sobre_8_0", CubeListBuilder.create()
                .texOffs(234, 288).addBox(-1.5798F, -0.5F, -0.75F, 3.1596F, 10.7775F, 1.5F, infla),
                PartPose.offsetAndRotation(0F, 0.3F, 4.85F, 2.8297F, 0F, -2.9906F));
        p_falda.addOrReplaceChild("sobre_8_1", CubeListBuilder.create()
                .texOffs(185, 272).addBox(-2.0921F, -0.5F, -0.75F, 4.1842F, 12.0336F, 1.5F, infla)
                .texOffs(0, 303).addBox(-0.6F, -0.2F, -1.45F, 1.2F, 11.4336F, 1F, infla)
                .texOffs(152, 378).addBox(-2.1421F, 9.9336F, -1.05F, 4.2842F, 1.5F, 1.85F, infla),
                PartPose.offsetAndRotation(-1.4F, 9.5F, 7.85F, 3.0781F, 0F, 3.0962F));
        p_falda.addOrReplaceChild("sobre_9_0", CubeListBuilder.create()
                .texOffs(117, 303).addBox(-1.5798F, -0.5F, -0.75F, 3.1596F, 10.4708F, 1.5F, infla),
                PartPose.offsetAndRotation(-2.0473F, 0.3F, 3.5361F, 2.8342F, 0.2901F, -2.8936F));
        p_falda.addOrReplaceChild("sobre_9_1", CubeListBuilder.create()
                .texOffs(41, 272).addBox(-2.0921F, -0.5F, -0.75F, 4.1842F, 12.9367F, 1.5F, infla)
                .texOffs(152, 378).addBox(-2.1421F, 10.8367F, -1.05F, 4.2842F, 1.5F, 1.85F, infla),
                PartPose.offsetAndRotation(-5.0577F, 8.8494F, 6.2821F, 3.0851F, 0.2982F, 3.1053F));
        p_falda.addOrReplaceChild("sobre_10_0", CubeListBuilder.create()
                .texOffs(128, 303).addBox(-1.5798F, -0.5F, -0.75F, 3.1596F, 10.3391F, 1.5F, infla),
                PartPose.offsetAndRotation(-4.3603F, 0.3F, 3.46F, 2.8706F, 0.6066F, -2.7993F));
        p_falda.addOrReplaceChild("sobre_10_1", CubeListBuilder.create()
                .texOffs(148, 251).addBox(-2.0921F, -0.5F, -0.75F, 4.1842F, 15.0789F, 1.5F, infla)
                .texOffs(218, 251).addBox(-0.6F, -0.2F, -1.45F, 1.2F, 14.4789F, 1F, infla)
                .texOffs(152, 378).addBox(-2.1421F, 12.9789F, -1.05F, 4.2842F, 1.5F, 1.85F, infla),
                PartPose.offsetAndRotation(-8.7229F, 8.2979F, 5.5142F, 3.0992F, 0.632F, 3.1165F));
        p_falda.addOrReplaceChild("sobre_11_0", CubeListBuilder.create()
                .texOffs(139, 303).addBox(-1.5798F, -0.5F, -0.75F, 3.1596F, 10.3411F, 1.5F, infla),
                PartPose.offsetAndRotation(-4.873F, 0.3F, 1.4029F, 2.9265F, 1.0119F, -2.719F));
        p_falda.addOrReplaceChild("sobre_11_1", CubeListBuilder.create()
                .texOffs(67, 251).addBox(-2.0921F, -0.5F, -0.75F, 4.1842F, 17.2164F, 1.5F, infla)
                .texOffs(152, 378).addBox(-2.1421F, 15.1164F, -1.05F, 4.2842F, 1.5F, 1.85F, infla),
                PartPose.offsetAndRotation(-10.1578F, 7.9294F, 2.4604F, 3.1095F, 1.0471F, 3.1227F));
        p_falda.addOrReplaceChild("sobre_12_0", CubeListBuilder.create()
                .texOffs(150, 303).addBox(-1.5798F, -0.5F, -0.75F, 3.1596F, 10.36F, 1.5F, infla),
                PartPose.offsetAndRotation(-6.25F, 0.3F, 0F, -0.6414F, 1.5708F, 0F));
        p_falda.addOrReplaceChild("sobre_12_1", CubeListBuilder.create()
                .texOffs(28, 251).addBox(-2.0921F, -0.5F, -0.75F, 4.1842F, 18.1012F, 1.5F, infla)
                .texOffs(86, 251).addBox(-0.6F, -0.2F, -1.45F, 1.2F, 17.5012F, 1F, infla)
                .texOffs(152, 378).addBox(-2.1421F, 16.0012F, -1.05F, 4.2842F, 1.5F, 1.85F, infla),
                PartPose.offsetAndRotation(-11.85F, 7.8F, 0F, -0.0117F, 1.5708F, 0F));
        p_falda.addOrReplaceChild("sobre_13_0", CubeListBuilder.create()
                .texOffs(161, 303).addBox(-1.5798F, -0.5F, -0.75F, 3.1596F, 10.3314F, 1.5F, infla),
                PartPose.offsetAndRotation(-4.8747F, 0.3F, -1.3706F, -0.1867F, 0.9905F, 0.4495F));
        p_falda.addOrReplaceChild("sobre_13_1", CubeListBuilder.create()
                .texOffs(67, 251).addBox(-2.0921F, -0.5F, -0.75F, 4.1842F, 17.2162F, 1.5F, infla)
                .texOffs(152, 378).addBox(-2.1421F, 15.1162F, -1.05F, 4.2842F, 1.5F, 1.85F, infla),
                PartPose.offsetAndRotation(-10.1629F, 7.9294F, -2.32F, -0.0291F, 1.0249F, -0.016F));
        p_falda.addOrReplaceChild("sobre_14_0", CubeListBuilder.create()
                .texOffs(172, 303).addBox(-1.5798F, -0.5F, -0.75F, 3.1596F, 10.264F, 1.5F, infla),
                PartPose.offsetAndRotation(-4.3532F, 0.3F, -3.3653F, -0.2216F, 0.5715F, 0.3769F));
        p_falda.addOrReplaceChild("sobre_14_1", CubeListBuilder.create()
                .texOffs(161, 251).addBox(-2.0921F, -0.5F, -0.75F, 4.1842F, 15.0774F, 1.5F, infla)
                .texOffs(224, 251).addBox(-0.6F, -0.2F, -1.45F, 1.2F, 14.4774F, 1F, infla)
                .texOffs(152, 378).addBox(-2.1421F, 12.9774F, -1.05F, 4.2842F, 1.5F, 1.85F, infla),
                PartPose.offsetAndRotation(-8.7032F, 8.2979F, -5.0778F, -0.037F, 0.5881F, -0.0205F));
        p_falda.addOrReplaceChild("sobre_15_0", CubeListBuilder.create()
                .texOffs(183, 303).addBox(-1.5798F, -0.5F, -0.75F, 3.1596F, 10.3174F, 1.5F, infla),
                PartPose.offsetAndRotation(-2.0526F, 0.3F, -3.3637F, -0.2411F, 0.2666F, 0.2748F));
        p_falda.addOrReplaceChild("sobre_15_1", CubeListBuilder.create()
                .texOffs(54, 272).addBox(-2.0921F, -0.5F, -0.75F, 4.1842F, 12.9345F, 1.5F, infla)
                .texOffs(152, 378).addBox(-2.1421F, 10.8345F, -1.05F, 4.2842F, 1.5F, 1.85F, infla),
                PartPose.offsetAndRotation(-5.0716F, 8.8494F, -5.5099F, -0.0528F, 0.2655F, -0.0324F));
    }

    private static void entera_ala_izq(PartDefinition p_torso, CubeDeformation infla) {
        PartDefinition p_ala_izq = p_torso.addOrReplaceChild("ala_izq", CubeListBuilder.create()
                .texOffs(0, 0).addBox(-0.5F, -31F, -4F, 1F, 46F, 51F, infla),
                PartPose.offsetAndRotation(5F, -12.5F, 4.4F, -0.0698F, 0.733F, 0.2094F));
        p_ala_izq.addOrReplaceChild("ala_izq_hueso0", CubeListBuilder.create()
                .texOffs(95, 272).addBox(-2F, -0.9F, -1.7F, 4F, 10.3586F, 3.4F, infla)
                .texOffs(69, 351).addBox(-2.15F, -1.9F, -2F, 4.3F, 3.8F, 4F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0F, 3.0245F, 0F, 0F));
        p_ala_izq.addOrReplaceChild("ala_izq_hueso1", CubeListBuilder.create()
                .texOffs(111, 272).addBox(-1.85F, -0.9F, -1.7F, 3.7F, 10.5801F, 3.4F, infla)
                .texOffs(87, 351).addBox(-2F, -1.9F, -2F, 4F, 3.8F, 4F, infla),
                PartPose.offsetAndRotation(0F, -8.5F, 1F, 2.8883F, 0F, 0F));
        p_ala_izq.addOrReplaceChild("ala_izq_hueso2", CubeListBuilder.create()
                .texOffs(127, 272).addBox(-1.7F, -0.9F, -1.7F, 3.4F, 10.1193F, 3.4F, infla)
                .texOffs(104, 351).addBox(-1.85F, -1.9F, -2F, 3.7F, 3.8F, 4F, infla),
                PartPose.offsetAndRotation(0F, -17F, 3.2F, 2.6941F, 0F, 0F));
        p_ala_izq.addOrReplaceChild("ala_izq_hueso3", CubeListBuilder.create()
                .texOffs(36, 303).addBox(-1.55F, -0.9F, -1.7F, 3.1F, 7.9717F, 3.4F, infla)
                .texOffs(121, 351).addBox(-1.7F, -1.9F, -2F, 3.4F, 3.8F, 4F, infla),
                PartPose.offsetAndRotation(0F, -24.5F, 6.8F, 2.2759F, 0F, 0F));
        p_ala_izq.addOrReplaceChild("ala_izq_hueso4", CubeListBuilder.create()
                .texOffs(236, 303).addBox(-1.4F, -0.9F, -1.7F, 2.8F, 6.809F, 3.4F, infla)
                .texOffs(137, 351).addBox(-1.55F, -1.9F, -2F, 3.1F, 3.8F, 4F, infla),
                PartPose.offsetAndRotation(0F, -28.5F, 11.5F, 1.6307F, 0F, 0F));
        p_ala_izq.addOrReplaceChild("ala_izq_hueso5", CubeListBuilder.create()
                .texOffs(85, 317).addBox(-1.25F, -0.9F, -1.7F, 2.5F, 7.1F, 3.4F, infla)
                .texOffs(168, 351).addBox(-1.4F, -1.9F, -2F, 2.8F, 3.8F, 4F, infla),
                PartPose.offsetAndRotation(0F, -28.8F, 16.5F, 1.0142F, 0F, 0F));
        p_ala_izq.addOrReplaceChild("ala_izq_menor0", CubeListBuilder.create()
                .texOffs(116, 329).addBox(1.55F, -0.6F, -2.1F, 1.1F, 5.1F, 4.2F, infla)
                .texOffs(116, 329).addBox(-2.65F, -0.6F, -2.1F, 1.1F, 5.1F, 4.2F, infla),
                PartPose.offsetAndRotation(0F, -1.3925F, 0.7462F, 0.1857F, 0.087F, 0.0163F));
        p_ala_izq.addOrReplaceChild("ala_izq_menor1", CubeListBuilder.create()
                .texOffs(128, 329).addBox(1.75F, -0.6F, -2.1F, 1.1F, 5.325F, 4.2F, infla)
                .texOffs(128, 329).addBox(-2.85F, -0.6F, -2.1F, 1.1F, 5.325F, 4.2F, infla),
                PartPose.offsetAndRotation(0F, -6.1006F, 1.3001F, 0.2096F, 0.0969F, 0.0206F));
        p_ala_izq.addOrReplaceChild("ala_izq_menor2", CubeListBuilder.create()
                .texOffs(140, 329).addBox(1.55F, -0.6F, -2.1F, 1.1F, 5.55F, 4.2F, infla)
                .texOffs(140, 329).addBox(-2.65F, -0.6F, -2.1F, 1.1F, 5.55F, 4.2F, infla),
                PartPose.offsetAndRotation(0F, -10.7329F, 2.2591F, 0.234F, 0.1249F, 0.0297F));
        p_ala_izq.addOrReplaceChild("ala_izq_menor3", CubeListBuilder.create()
                .texOffs(152, 329).addBox(1.75F, -0.6F, -2.1F, 1.1F, 5.775F, 4.2F, infla)
                .texOffs(152, 329).addBox(-2.85F, -0.6F, -2.1F, 1.1F, 5.775F, 4.2F, infla),
                PartPose.offsetAndRotation(0F, -15.3222F, 3.4469F, 0.2588F, 0.1537F, 0.0405F));
        p_ala_izq.addOrReplaceChild("ala_izq_menor4", CubeListBuilder.create()
                .texOffs(98, 317).addBox(1.55F, -0.6F, -2.1F, 1.1F, 6F, 4.2F, infla)
                .texOffs(98, 317).addBox(-2.65F, -0.6F, -2.1F, 1.1F, 6F, 4.2F, infla),
                PartPose.offsetAndRotation(0F, -19.6632F, 5.3144F, 0.2806F, 0.0978F, 0.0281F));
        p_ala_izq.addOrReplaceChild("ala_izq_menor5", CubeListBuilder.create()
                .texOffs(110, 317).addBox(1.75F, -0.6F, -2.1F, 1.1F, 6.225F, 4.2F, infla)
                .texOffs(110, 317).addBox(-2.85F, -0.6F, -2.1F, 1.1F, 6.225F, 4.2F, infla),
                PartPose.offsetAndRotation(0F, -23.8985F, 7.4157F, 0.3268F, 0.0938F, 0.0318F));
        p_ala_izq.addOrReplaceChild("ala_izq_menor6", CubeListBuilder.create()
                .texOffs(122, 317).addBox(1.55F, -0.6F, -2.1F, 1.1F, 6.45F, 4.2F, infla)
                .texOffs(122, 317).addBox(-2.65F, -0.6F, -2.1F, 1.1F, 6.45F, 4.2F, infla),
                PartPose.offsetAndRotation(0F, -26.971F, 11.0259F, 0.4028F, 0.1027F, 0.0437F));
        p_ala_izq.addOrReplaceChild("ala_izq_menor7", CubeListBuilder.create()
                .texOffs(134, 317).addBox(1.75F, -0.6F, -2.1F, 1.1F, 6.675F, 4.2F, infla)
                .texOffs(134, 317).addBox(-2.85F, -0.6F, -2.1F, 1.1F, 6.675F, 4.2F, infla),
                PartPose.offsetAndRotation(0F, -28.0073F, 15.4552F, 0.4869F, 0.1475F, 0.0777F));
        p_ala_izq.addOrReplaceChild("ala_izq_menor8", CubeListBuilder.create()
                .texOffs(50, 303).addBox(1.55F, -0.6F, -2.1F, 1.1F, 6.9F, 4.2F, infla)
                .texOffs(50, 303).addBox(-2.65F, -0.6F, -2.1F, 1.1F, 6.9F, 4.2F, infla),
                PartPose.offsetAndRotation(0F, -26.4131F, 19.7111F, 0.5455F, 0.0879F, 0.0532F));
        p_ala_izq.addOrReplaceChild("ala_izq_marginal0", CubeListBuilder.create()
                .texOffs(244, 351).addBox(1.9F, -0.6F, -1.8F, 1.2F, 3.47F, 3.6F, infla)
                .texOffs(244, 351).addBox(-3.1F, -0.6F, -1.8F, 1.2F, 3.47F, 3.6F, infla),
                PartPose.offsetAndRotation(0F, -2.2295F, 0.8446F, 0.4183F, 0.1508F, 0.0667F));
        p_ala_izq.addOrReplaceChild("ala_izq_marginal1", CubeListBuilder.create()
                .texOffs(0, 361).addBox(2.1F, -0.6F, -1.8F, 1.2F, 3.5914F, 3.6F, infla)
                .texOffs(0, 361).addBox(-3.3F, -0.6F, -1.8F, 1.2F, 3.5914F, 3.6F, infla),
                PartPose.offsetAndRotation(0F, -7.3113F, 1.4425F, 0.4691F, 0.1399F, 0.0706F));
        p_ala_izq.addOrReplaceChild("ala_izq_marginal2", CubeListBuilder.create()
                .texOffs(11, 361).addBox(1.9F, -0.6F, -1.8F, 1.2F, 3.7129F, 3.6F, infla)
                .texOffs(11, 361).addBox(-3.1F, -0.6F, -1.8F, 1.2F, 3.7129F, 3.6F, infla),
                PartPose.offsetAndRotation(0F, -12.2772F, 2.6588F, 0.5172F, 0.0884F, 0.0502F));
        p_ala_izq.addOrReplaceChild("ala_izq_marginal3", CubeListBuilder.create()
                .texOffs(22, 361).addBox(2.1F, -0.6F, -1.8F, 1.2F, 3.8343F, 3.6F, infla)
                .texOffs(22, 361).addBox(-3.3F, -0.6F, -1.8F, 1.2F, 3.8343F, 3.6F, infla),
                PartPose.offsetAndRotation(0F, -17.1668F, 4.1161F, 0.5706F, 0.1209F, 0.0772F));
        p_ala_izq.addOrReplaceChild("ala_izq_marginal4", CubeListBuilder.create()
                .texOffs(33, 361).addBox(1.9F, -0.6F, -1.8F, 1.2F, 3.9557F, 3.6F, infla)
                .texOffs(33, 361).addBox(-3.1F, -0.6F, -1.8F, 1.2F, 3.9557F, 3.6F, infla),
                PartPose.offsetAndRotation(0F, -21.7798F, 6.3303F, 0.621F, 0.1093F, 0.0779F));
        p_ala_izq.addOrReplaceChild("ala_izq_marginal5", CubeListBuilder.create()
                .texOffs(44, 361).addBox(2.1F, -0.6F, -1.8F, 1.2F, 4.0771F, 3.6F, infla)
                .texOffs(44, 361).addBox(-3.3F, -0.6F, -1.8F, 1.2F, 4.0771F, 3.6F, infla),
                PartPose.offsetAndRotation(0F, -25.6639F, 9.4901F, 0.6718F, 0.1023F, 0.0811F));
        p_ala_izq.addOrReplaceChild("ala_izq_marginal6", CubeListBuilder.create()
                .texOffs(55, 361).addBox(1.9F, -0.6F, -1.8F, 1.2F, 4.1986F, 3.6F, infla)
                .texOffs(55, 361).addBox(-3.1F, -0.6F, -1.8F, 1.2F, 4.1986F, 3.6F, infla),
                PartPose.offsetAndRotation(0F, -27.9091F, 13.8178F, 0.7276F, 0.1439F, 0.127F));
        p_ala_izq.addOrReplaceChild("ala_izq_marginal7", CubeListBuilder.create()
                .texOffs(66, 361).addBox(2.1F, -0.6F, -1.8F, 1.2F, 4.32F, 3.6F, infla)
                .texOffs(66, 361).addBox(-3.3F, -0.6F, -1.8F, 1.2F, 4.32F, 3.6F, infla),
                PartPose.offsetAndRotation(0F, -27.081F, 18.6378F, 0.7717F, 0.0696F, 0.0676F));
    }

    private static void entera_ala_der(PartDefinition p_torso, CubeDeformation infla) {
        PartDefinition p_ala_der = p_torso.addOrReplaceChild("ala_der", CubeListBuilder.create()
                .texOffs(0, 0).addBox(-0.5F, -31F, -4F, 1F, 46F, 51F, infla),
                PartPose.offsetAndRotation(-5F, -12.5F, 4.4F, -0.0698F, -0.733F, -0.2094F));
        p_ala_der.addOrReplaceChild("ala_der_hueso0", CubeListBuilder.create()
                .texOffs(95, 272).addBox(-2F, -0.9F, -1.7F, 4F, 10.3586F, 3.4F, infla)
                .texOffs(69, 351).addBox(-2.15F, -1.9F, -2F, 4.3F, 3.8F, 4F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0F, 3.0245F, 0F, 0F));
        p_ala_der.addOrReplaceChild("ala_der_hueso1", CubeListBuilder.create()
                .texOffs(111, 272).addBox(-1.85F, -0.9F, -1.7F, 3.7F, 10.5801F, 3.4F, infla)
                .texOffs(87, 351).addBox(-2F, -1.9F, -2F, 4F, 3.8F, 4F, infla),
                PartPose.offsetAndRotation(0F, -8.5F, 1F, 2.8883F, 0F, 0F));
        p_ala_der.addOrReplaceChild("ala_der_hueso2", CubeListBuilder.create()
                .texOffs(127, 272).addBox(-1.7F, -0.9F, -1.7F, 3.4F, 10.1193F, 3.4F, infla)
                .texOffs(104, 351).addBox(-1.85F, -1.9F, -2F, 3.7F, 3.8F, 4F, infla),
                PartPose.offsetAndRotation(0F, -17F, 3.2F, 2.6941F, 0F, 0F));
        p_ala_der.addOrReplaceChild("ala_der_hueso3", CubeListBuilder.create()
                .texOffs(36, 303).addBox(-1.55F, -0.9F, -1.7F, 3.1F, 7.9717F, 3.4F, infla)
                .texOffs(121, 351).addBox(-1.7F, -1.9F, -2F, 3.4F, 3.8F, 4F, infla),
                PartPose.offsetAndRotation(0F, -24.5F, 6.8F, 2.2759F, 0F, 0F));
        p_ala_der.addOrReplaceChild("ala_der_hueso4", CubeListBuilder.create()
                .texOffs(236, 303).addBox(-1.4F, -0.9F, -1.7F, 2.8F, 6.809F, 3.4F, infla)
                .texOffs(137, 351).addBox(-1.55F, -1.9F, -2F, 3.1F, 3.8F, 4F, infla),
                PartPose.offsetAndRotation(0F, -28.5F, 11.5F, 1.6307F, 0F, 0F));
        p_ala_der.addOrReplaceChild("ala_der_hueso5", CubeListBuilder.create()
                .texOffs(85, 317).addBox(-1.25F, -0.9F, -1.7F, 2.5F, 7.1F, 3.4F, infla)
                .texOffs(168, 351).addBox(-1.4F, -1.9F, -2F, 2.8F, 3.8F, 4F, infla),
                PartPose.offsetAndRotation(0F, -28.8F, 16.5F, 1.0142F, 0F, 0F));
        p_ala_der.addOrReplaceChild("ala_der_menor0", CubeListBuilder.create()
                .texOffs(116, 329).addBox(-2.65F, -0.6F, -2.1F, 1.1F, 5.1F, 4.2F, infla)
                .texOffs(116, 329).addBox(1.55F, -0.6F, -2.1F, 1.1F, 5.1F, 4.2F, infla),
                PartPose.offsetAndRotation(0F, -1.3925F, 0.7462F, 0.1857F, -0.087F, -0.0163F));
        p_ala_der.addOrReplaceChild("ala_der_menor1", CubeListBuilder.create()
                .texOffs(128, 329).addBox(-2.85F, -0.6F, -2.1F, 1.1F, 5.325F, 4.2F, infla)
                .texOffs(128, 329).addBox(1.75F, -0.6F, -2.1F, 1.1F, 5.325F, 4.2F, infla),
                PartPose.offsetAndRotation(0F, -6.1006F, 1.3001F, 0.2096F, -0.0969F, -0.0206F));
        p_ala_der.addOrReplaceChild("ala_der_menor2", CubeListBuilder.create()
                .texOffs(140, 329).addBox(-2.65F, -0.6F, -2.1F, 1.1F, 5.55F, 4.2F, infla)
                .texOffs(140, 329).addBox(1.55F, -0.6F, -2.1F, 1.1F, 5.55F, 4.2F, infla),
                PartPose.offsetAndRotation(0F, -10.7329F, 2.2591F, 0.234F, -0.1249F, -0.0297F));
        p_ala_der.addOrReplaceChild("ala_der_menor3", CubeListBuilder.create()
                .texOffs(152, 329).addBox(-2.85F, -0.6F, -2.1F, 1.1F, 5.775F, 4.2F, infla)
                .texOffs(152, 329).addBox(1.75F, -0.6F, -2.1F, 1.1F, 5.775F, 4.2F, infla),
                PartPose.offsetAndRotation(0F, -15.3222F, 3.4469F, 0.2588F, -0.1537F, -0.0405F));
        p_ala_der.addOrReplaceChild("ala_der_menor4", CubeListBuilder.create()
                .texOffs(98, 317).addBox(-2.65F, -0.6F, -2.1F, 1.1F, 6F, 4.2F, infla)
                .texOffs(98, 317).addBox(1.55F, -0.6F, -2.1F, 1.1F, 6F, 4.2F, infla),
                PartPose.offsetAndRotation(0F, -19.6632F, 5.3144F, 0.2806F, -0.0978F, -0.0281F));
        p_ala_der.addOrReplaceChild("ala_der_menor5", CubeListBuilder.create()
                .texOffs(110, 317).addBox(-2.85F, -0.6F, -2.1F, 1.1F, 6.225F, 4.2F, infla)
                .texOffs(110, 317).addBox(1.75F, -0.6F, -2.1F, 1.1F, 6.225F, 4.2F, infla),
                PartPose.offsetAndRotation(0F, -23.8985F, 7.4157F, 0.3268F, -0.0938F, -0.0318F));
        p_ala_der.addOrReplaceChild("ala_der_menor6", CubeListBuilder.create()
                .texOffs(122, 317).addBox(-2.65F, -0.6F, -2.1F, 1.1F, 6.45F, 4.2F, infla)
                .texOffs(122, 317).addBox(1.55F, -0.6F, -2.1F, 1.1F, 6.45F, 4.2F, infla),
                PartPose.offsetAndRotation(0F, -26.971F, 11.0259F, 0.4028F, -0.1027F, -0.0437F));
        p_ala_der.addOrReplaceChild("ala_der_menor7", CubeListBuilder.create()
                .texOffs(134, 317).addBox(-2.85F, -0.6F, -2.1F, 1.1F, 6.675F, 4.2F, infla)
                .texOffs(134, 317).addBox(1.75F, -0.6F, -2.1F, 1.1F, 6.675F, 4.2F, infla),
                PartPose.offsetAndRotation(0F, -28.0073F, 15.4552F, 0.4869F, -0.1475F, -0.0777F));
        p_ala_der.addOrReplaceChild("ala_der_menor8", CubeListBuilder.create()
                .texOffs(50, 303).addBox(-2.65F, -0.6F, -2.1F, 1.1F, 6.9F, 4.2F, infla)
                .texOffs(50, 303).addBox(1.55F, -0.6F, -2.1F, 1.1F, 6.9F, 4.2F, infla),
                PartPose.offsetAndRotation(0F, -26.4131F, 19.7111F, 0.5455F, -0.0879F, -0.0532F));
        p_ala_der.addOrReplaceChild("ala_der_marginal0", CubeListBuilder.create()
                .texOffs(244, 351).addBox(-3.1F, -0.6F, -1.8F, 1.2F, 3.47F, 3.6F, infla)
                .texOffs(244, 351).addBox(1.9F, -0.6F, -1.8F, 1.2F, 3.47F, 3.6F, infla),
                PartPose.offsetAndRotation(0F, -2.2295F, 0.8446F, 0.4183F, -0.1508F, -0.0667F));
        p_ala_der.addOrReplaceChild("ala_der_marginal1", CubeListBuilder.create()
                .texOffs(0, 361).addBox(-3.3F, -0.6F, -1.8F, 1.2F, 3.5914F, 3.6F, infla)
                .texOffs(0, 361).addBox(2.1F, -0.6F, -1.8F, 1.2F, 3.5914F, 3.6F, infla),
                PartPose.offsetAndRotation(0F, -7.3113F, 1.4425F, 0.4691F, -0.1399F, -0.0706F));
        p_ala_der.addOrReplaceChild("ala_der_marginal2", CubeListBuilder.create()
                .texOffs(11, 361).addBox(-3.1F, -0.6F, -1.8F, 1.2F, 3.7129F, 3.6F, infla)
                .texOffs(11, 361).addBox(1.9F, -0.6F, -1.8F, 1.2F, 3.7129F, 3.6F, infla),
                PartPose.offsetAndRotation(0F, -12.2772F, 2.6588F, 0.5172F, -0.0884F, -0.0502F));
        p_ala_der.addOrReplaceChild("ala_der_marginal3", CubeListBuilder.create()
                .texOffs(22, 361).addBox(-3.3F, -0.6F, -1.8F, 1.2F, 3.8343F, 3.6F, infla)
                .texOffs(22, 361).addBox(2.1F, -0.6F, -1.8F, 1.2F, 3.8343F, 3.6F, infla),
                PartPose.offsetAndRotation(0F, -17.1668F, 4.1161F, 0.5706F, -0.1209F, -0.0772F));
        p_ala_der.addOrReplaceChild("ala_der_marginal4", CubeListBuilder.create()
                .texOffs(33, 361).addBox(-3.1F, -0.6F, -1.8F, 1.2F, 3.9557F, 3.6F, infla)
                .texOffs(33, 361).addBox(1.9F, -0.6F, -1.8F, 1.2F, 3.9557F, 3.6F, infla),
                PartPose.offsetAndRotation(0F, -21.7798F, 6.3303F, 0.621F, -0.1093F, -0.0779F));
        p_ala_der.addOrReplaceChild("ala_der_marginal5", CubeListBuilder.create()
                .texOffs(44, 361).addBox(-3.3F, -0.6F, -1.8F, 1.2F, 4.0771F, 3.6F, infla)
                .texOffs(44, 361).addBox(2.1F, -0.6F, -1.8F, 1.2F, 4.0771F, 3.6F, infla),
                PartPose.offsetAndRotation(0F, -25.6639F, 9.4901F, 0.6718F, -0.1023F, -0.0811F));
        p_ala_der.addOrReplaceChild("ala_der_marginal6", CubeListBuilder.create()
                .texOffs(55, 361).addBox(-3.1F, -0.6F, -1.8F, 1.2F, 4.1986F, 3.6F, infla)
                .texOffs(55, 361).addBox(1.9F, -0.6F, -1.8F, 1.2F, 4.1986F, 3.6F, infla),
                PartPose.offsetAndRotation(0F, -27.9091F, 13.8178F, 0.7276F, -0.1439F, -0.127F));
        p_ala_der.addOrReplaceChild("ala_der_marginal7", CubeListBuilder.create()
                .texOffs(66, 361).addBox(-3.3F, -0.6F, -1.8F, 1.2F, 4.32F, 3.6F, infla)
                .texOffs(66, 361).addBox(2.1F, -0.6F, -1.8F, 1.2F, 4.32F, 3.6F, infla),
                PartPose.offsetAndRotation(0F, -27.081F, 18.6378F, 0.7717F, -0.0696F, -0.0676F));
    }

    private static void entera_cabeza(PartDefinition p_cuello, CubeDeformation infla) {
        PartDefinition p_cabeza = p_cuello.addOrReplaceChild("cabeza", CubeListBuilder.create()
                .texOffs(79, 288).addBox(-3.432F, -8.448F, -2.2352F, 6.864F, 5.984F, 6.0544F, infla)
                .texOffs(67, 272).addBox(-2.7456F, -8.448F, -2.992F, 5.4912F, 5.984F, 7.568F, infla)
                .texOffs(21, 329).addBox(-2.728F, -7.568F, -3.96F, 5.456F, 5.104F, 4.224F, infla)
                .texOffs(236, 361).addBox(-1.936F, -2.728F, -3.872F, 3.872F, 2.112F, 4.576F, infla)
                .texOffs(200, 378).addBox(-0.924F, -0.968F, -4.268F, 1.848F, 1.276F, 2.64F, infla)
                .texOffs(115, 385).addBox(-2.376F, -5.544F, -4.356F, 4.752F, 0.484F, 0.44F, infla)
                .texOffs(251, 194).addBox(-0.396F, -5.192F, -4.708F, 0.792F, 1.936F, 0.748F, infla)
                .texOffs(109, 385).addBox(-0.484F, -3.432F, -5.06F, 0.968F, 0.88F, 1.1F, infla)
                .texOffs(137, 385).addBox(-0.704F, -1.892F, -4.18F, 1.408F, 0.484F, 0.308F, infla)
                .texOffs(252, 133).addBox(-0.616F, -1.408F, -4.136F, 1.232F, 0.396F, 0.264F, infla)
                .texOffs(59, 340).addBox(-3.872F, -9.328F, -1.9448F, 7.744F, 1.936F, 6.2656F, infla)
                .texOffs(195, 317).addBox(-3.0976F, -9.328F, -2.728F, 6.1952F, 1.936F, 7.832F, infla)
                .texOffs(211, 361).addBox(-2.904F, -9.856F, -1.936F, 5.808F, 0.704F, 6.16F, infla)
                .texOffs(0, 329).addBox(-3.696F, -8.448F, 2.816F, 7.392F, 7.04F, 2.112F, infla)
                .texOffs(0, 370).addBox(-3.168F, -7.744F, 4.752F, 6.336F, 5.632F, 1.232F, infla)
                .texOffs(102, 329).addBox(-3.916F, -8.096F, -2.552F, 1.012F, 3.872F, 5.368F, infla)
                .texOffs(102, 329).addBox(2.904F, -8.096F, -2.552F, 1.012F, 3.872F, 5.368F, infla)
                .texOffs(154, 340).addBox(-3.784F, -4.576F, -1.144F, 0.968F, 4.224F, 4.312F, infla)
                .texOffs(154, 340).addBox(2.816F, -4.576F, -1.144F, 0.968F, 4.224F, 4.312F, infla)
                .texOffs(251, 288).addBox(-0.572F, -8.58F, -4.62F, 1.144F, 1.144F, 0.396F, infla),
                PartPose.offsetAndRotation(0F, -3.5F, -0.3F, -0.1571F, 0.2443F, 0.0524F));
        p_cabeza.addOrReplaceChild("mandibula_izq", CubeListBuilder.create()
                .texOffs(210, 351).addBox(-0.88F, 0F, -2.64F, 0.88F, 3.256F, 4.576F, infla),
                PartPose.offsetAndRotation(2.596F, -3.168F, 0F, 0F, 0F, 0.4712F));
        p_cabeza.addOrReplaceChild("flequillo_izq", CubeListBuilder.create()
                .texOffs(166, 378).addBox(0F, 0F, -0.836F, 3.784F, 1.32F, 1.936F, infla),
                PartPose.offsetAndRotation(0.132F, -8.536F, -3.52F, 0F, 0F, 0.3491F));
        p_cabeza.addOrReplaceChild("diadema_izq", CubeListBuilder.create()
                .texOffs(127, 385).addBox(0F, -0.088F, -0.22F, 3.696F, 0.484F, 0.352F, infla),
                PartPose.offsetAndRotation(0F, -7.964F, -4.356F, 0F, 0F, 0.2443F));
        p_cabeza.addOrReplaceChild("mandibula_der", CubeListBuilder.create()
                .texOffs(210, 351).addBox(0F, 0F, -2.64F, 0.88F, 3.256F, 4.576F, infla),
                PartPose.offsetAndRotation(-2.596F, -3.168F, 0F, 0F, 0F, -0.4712F));
        p_cabeza.addOrReplaceChild("flequillo_der", CubeListBuilder.create()
                .texOffs(166, 378).addBox(-3.784F, 0F, -0.836F, 3.784F, 1.32F, 1.936F, infla),
                PartPose.offsetAndRotation(-0.132F, -8.536F, -3.52F, 0F, 0F, -0.3491F));
        p_cabeza.addOrReplaceChild("diadema_der", CubeListBuilder.create()
                .texOffs(127, 385).addBox(-3.696F, -0.088F, -0.22F, 3.696F, 0.484F, 0.352F, infla),
                PartPose.offsetAndRotation(0F, -7.964F, -4.356F, 0F, 0F, -0.2443F));
    }

    public static LayerDefinition crearRota() {
        return rota(CubeDeformation.NONE);
    }

    private static LayerDefinition rota(CubeDeformation infla) {
        MeshDefinition malla = new MeshDefinition();
        PartDefinition p_root = malla.getRoot();
        PartDefinition p_estatua = p_root.addOrReplaceChild("estatua", CubeListBuilder.create(),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        rota_pedestal(p_estatua, infla);
        p_estatua.addOrReplaceChild("pie_der", CubeListBuilder.create()
                .texOffs(31, 351).addBox(-1.55F, -2F, -4.6F, 3.1F, 2F, 6F, infla)
                .texOffs(65, 385).addBox(-1.35F, -1.45F, -5.9F, 2.7F, 1.45F, 1.5F, infla)
                .texOffs(99, 385).addBox(-1.7F, -2.25F, -2.8F, 3.4F, 0.5F, 0.8F, infla)
                .texOffs(8, 351).addBox(-1.65F, -0.45F, -6F, 3.3F, 0.45F, 7.4F, infla),
                PartPose.offsetAndRotation(-3.3F, 6F, -5.3F, 0F, 0.1396F, 0F));
        p_estatua.addOrReplaceChild("pie_izq", CubeListBuilder.create()
                .texOffs(31, 351).addBox(-1.55F, -2F, -4.6F, 3.1F, 2F, 6F, infla)
                .texOffs(65, 385).addBox(-1.35F, -1.45F, -5.9F, 2.7F, 1.45F, 1.5F, infla)
                .texOffs(99, 385).addBox(-1.7F, -2.25F, -2.8F, 3.4F, 0.5F, 0.8F, infla)
                .texOffs(8, 351).addBox(-1.65F, -0.45F, -6F, 3.3F, 0.45F, 7.4F, infla),
                PartPose.offsetAndRotation(3.9F, 6F, -6.6F, 0.1047F, -0.2793F, 0F));
        rota_falda(p_estatua, infla);
        p_estatua.addOrReplaceChild("rotura", CubeListBuilder.create()
                .texOffs(114, 223).addBox(-8.5F, -7F, -5.5F, 17F, 13F, 12F, infla)
                .texOffs(44, 288).addBox(-6.5F, -10.5F, -4F, 8F, 4F, 9F, infla)
                .texOffs(225, 317).addBox(1.5F, -9F, -3F, 6F, 2.5F, 7F, infla)
                .texOffs(106, 288).addBox(-7.5F, -13.5F, 1.5F, 6F, 7F, 6F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        rota_ala_rota(p_estatua, infla);
        PartDefinition p_trompeta_caida = p_estatua.addOrReplaceChild("trompeta_caida", CubeListBuilder.create()
                .texOffs(200, 223).addBox(-0.7F, 0F, -0.7F, 1.4F, 21F, 1.4F, infla)
                .texOffs(179, 378).addBox(-1.25F, 6F, -1.25F, 2.5F, 1.4F, 2.5F, infla),
                PartPose.offsetAndRotation(-8F, 0.3147F, -10.5F, 1.5708F, 0F, -0.4189F));
        PartDefinition p_campana_caida = p_trompeta_caida.addOrReplaceChild("campana_caida", CubeListBuilder.create(),
                PartPose.offsetAndRotation(0F, 21F, 0F, 0F, 0F, 0F));
        p_campana_caida.addOrReplaceChild("campana_caida_0_0", CubeListBuilder.create()
                .texOffs(130, 378).addBox(-0.725F, -0.3F, -0.3F, 1.45F, 4.0355F, 0.6F, infla),
                PartPose.offsetAndRotation(0F, 0F, -0.75F, -0.3724F, 0F, 0F));
        p_campana_caida.addOrReplaceChild("campana_caida_0_1", CubeListBuilder.create()
                .texOffs(39, 378).addBox(-1.7F, -0.3F, -0.3F, 3.4F, 4.4184F, 0.6F, infla)
                .texOffs(32, 385).addBox(-2.1551F, 3.2184F, -0.75F, 4.3103F, 1.1F, 1.1F, infla),
                PartPose.offsetAndRotation(0F, 3.2F, -2F, -0.7854F, 0F, 0F));
        p_campana_caida.addOrReplaceChild("campana_caida_1_0", CubeListBuilder.create()
                .texOffs(130, 378).addBox(-0.725F, -0.3F, -0.3F, 1.45F, 4.0355F, 0.6F, infla),
                PartPose.offsetAndRotation(-0.5303F, 0F, -0.5303F, -0.3724F, 0.7854F, 0F));
        p_campana_caida.addOrReplaceChild("campana_caida_1_1", CubeListBuilder.create()
                .texOffs(39, 378).addBox(-1.7F, -0.3F, -0.3F, 3.4F, 4.4184F, 0.6F, infla)
                .texOffs(32, 385).addBox(-2.1551F, 3.2184F, -0.75F, 4.3103F, 1.1F, 1.1F, infla),
                PartPose.offsetAndRotation(-1.4142F, 3.2F, -1.4142F, -0.7854F, 0.7854F, 0F));
        p_campana_caida.addOrReplaceChild("campana_caida_2_0", CubeListBuilder.create()
                .texOffs(130, 378).addBox(-0.725F, -0.3F, -0.3F, 1.45F, 4.0355F, 0.6F, infla),
                PartPose.offsetAndRotation(-0.75F, 0F, 0F, -0.3724F, 1.5708F, 0F));
        p_campana_caida.addOrReplaceChild("campana_caida_2_1", CubeListBuilder.create()
                .texOffs(39, 378).addBox(-1.7F, -0.3F, -0.3F, 3.4F, 4.4184F, 0.6F, infla)
                .texOffs(32, 385).addBox(-2.1551F, 3.2184F, -0.75F, 4.3103F, 1.1F, 1.1F, infla),
                PartPose.offsetAndRotation(-2F, 3.2F, 0F, -0.7854F, 1.5708F, 0F));
        p_campana_caida.addOrReplaceChild("campana_caida_3_0", CubeListBuilder.create()
                .texOffs(130, 378).addBox(-0.725F, -0.3F, -0.3F, 1.45F, 4.0355F, 0.6F, infla),
                PartPose.offsetAndRotation(-0.5303F, 0F, 0.5303F, 2.7692F, 0.7854F, -3.1416F));
        p_campana_caida.addOrReplaceChild("campana_caida_3_1", CubeListBuilder.create()
                .texOffs(39, 378).addBox(-1.7F, -0.3F, -0.3F, 3.4F, 4.4184F, 0.6F, infla)
                .texOffs(32, 385).addBox(-2.1551F, 3.2184F, -0.75F, 4.3103F, 1.1F, 1.1F, infla),
                PartPose.offsetAndRotation(-1.4142F, 3.2F, 1.4142F, 2.3562F, 0.7854F, 3.1416F));
        p_campana_caida.addOrReplaceChild("campana_caida_4_0", CubeListBuilder.create()
                .texOffs(130, 378).addBox(-0.725F, -0.3F, -0.3F, 1.45F, 4.0355F, 0.6F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0.75F, 2.7692F, 0F, 3.1416F));
        p_campana_caida.addOrReplaceChild("campana_caida_4_1", CubeListBuilder.create()
                .texOffs(39, 378).addBox(-1.7F, -0.3F, -0.3F, 3.4F, 4.4184F, 0.6F, infla)
                .texOffs(32, 385).addBox(-2.1551F, 3.2184F, -0.75F, 4.3103F, 1.1F, 1.1F, infla),
                PartPose.offsetAndRotation(0F, 3.2F, 2F, 2.3562F, 0F, 3.1416F));
        p_campana_caida.addOrReplaceChild("campana_caida_5_0", CubeListBuilder.create()
                .texOffs(130, 378).addBox(-0.725F, -0.3F, -0.3F, 1.45F, 4.0355F, 0.6F, infla),
                PartPose.offsetAndRotation(0.5303F, 0F, 0.5303F, 2.7692F, -0.7854F, -3.1416F));
        p_campana_caida.addOrReplaceChild("campana_caida_5_1", CubeListBuilder.create()
                .texOffs(39, 378).addBox(-1.7F, -0.3F, -0.3F, 3.4F, 4.4184F, 0.6F, infla)
                .texOffs(32, 385).addBox(-2.1551F, 3.2184F, -0.75F, 4.3103F, 1.1F, 1.1F, infla),
                PartPose.offsetAndRotation(1.4142F, 3.2F, 1.4142F, 2.3562F, -0.7854F, 3.1416F));
        p_campana_caida.addOrReplaceChild("campana_caida_6_0", CubeListBuilder.create()
                .texOffs(130, 378).addBox(-0.725F, -0.3F, -0.3F, 1.45F, 4.0355F, 0.6F, infla),
                PartPose.offsetAndRotation(0.75F, 0F, 0F, -0.3724F, -1.5708F, 0F));
        p_campana_caida.addOrReplaceChild("campana_caida_6_1", CubeListBuilder.create()
                .texOffs(39, 378).addBox(-1.7F, -0.3F, -0.3F, 3.4F, 4.4184F, 0.6F, infla)
                .texOffs(32, 385).addBox(-2.1551F, 3.2184F, -0.75F, 4.3103F, 1.1F, 1.1F, infla),
                PartPose.offsetAndRotation(2F, 3.2F, 0F, -0.7854F, -1.5708F, 0F));
        p_campana_caida.addOrReplaceChild("campana_caida_7_0", CubeListBuilder.create()
                .texOffs(130, 378).addBox(-0.725F, -0.3F, -0.3F, 1.45F, 4.0355F, 0.6F, infla),
                PartPose.offsetAndRotation(0.5303F, 0F, -0.5303F, -0.3724F, -0.7854F, 0F));
        p_campana_caida.addOrReplaceChild("campana_caida_7_1", CubeListBuilder.create()
                .texOffs(39, 378).addBox(-1.7F, -0.3F, -0.3F, 3.4F, 4.4184F, 0.6F, infla)
                .texOffs(32, 385).addBox(-2.1551F, 3.2184F, -0.75F, 4.3103F, 1.1F, 1.1F, infla),
                PartPose.offsetAndRotation(1.4142F, 3.2F, -1.4142F, -0.7854F, -0.7854F, 0F));
        p_estatua.addOrReplaceChild("cascote_0", CubeListBuilder.create()
                .texOffs(51, 351).addBox(-2.25F, -2.25F, -1.8F, 4.5F, 4.05F, 3.6F, infla),
                PartPose.offsetAndRotation(10F, 3.7278F, -9F, 0.0192F, 1.2671F, 0.4019F));
        p_estatua.addOrReplaceChild("cascote_1", CubeListBuilder.create()
                .texOffs(180, 370).addBox(-1.75F, -1.75F, -1.4F, 3.5F, 3.15F, 2.8F, infla),
                PartPose.offsetAndRotation(-11F, 4.3969F, 4F, -0.1836F, 1.2034F, 0.1782F));
        p_estatua.addOrReplaceChild("cascote_2", CubeListBuilder.create()
                .texOffs(110, 378).addBox(-1.25F, -1.25F, -1F, 2.5F, 2.25F, 2F, infla),
                PartPose.offsetAndRotation(6F, 4.7118F, -12F, 0.1408F, 0.173F, -0.4128F));
        p_estatua.addOrReplaceChild("cascote_3", CubeListBuilder.create()
                .texOffs(194, 370).addBox(-1.5F, -1.5F, -1.2F, 3F, 2.7F, 2.4F, infla),
                PartPose.offsetAndRotation(-4F, 4.8675F, 10.5F, -0.1011F, 1.1724F, -0.2161F));
        p_estatua.addOrReplaceChild("cascote_4", CubeListBuilder.create()
                .texOffs(87, 378).addBox(-1.4F, -1.4F, -1.12F, 2.8F, 2.52F, 2.24F, infla),
                PartPose.offsetAndRotation(12F, 4.7066F, 9F, 0.0014F, 0.4986F, 0.3022F));
        p_estatua.addOrReplaceChild("cascote_5", CubeListBuilder.create()
                .texOffs(210, 378).addBox(-1.1F, -1.1F, -0.88F, 2.2F, 1.98F, 1.76F, infla),
                PartPose.offsetAndRotation(-12F, 5.0044F, -11.5F, 0.3885F, 0.6308F, 0.435F));
        p_estatua.addOrReplaceChild("cascote_6", CubeListBuilder.create()
                .texOffs(219, 378).addBox(-1F, -1F, -0.8F, 2F, 1.8F, 1.6F, infla),
                PartPose.offsetAndRotation(0.5F, 5.0847F, -12.6F, -0.3821F, 1.2764F, 0.3275F));
        p_estatua.addOrReplaceChild("cabeza_caida", CubeListBuilder.create()
                .texOffs(174, 251).addBox(-3.608F, -3.696F, -4.048F, 7.216F, 7.304F, 7.92F, infla)
                .texOffs(0, 317).addBox(-3.96F, -4.488F, -3.432F, 7.92F, 2.024F, 8.008F, infla),
                PartPose.offsetAndRotation(-8.5F, 0.0828F, 9F, 0.1396F, 0.6981F, 1.2566F));
        return LayerDefinition.create(malla, 256, 512);
    }

    private static void rota_pedestal(PartDefinition p_estatua, CubeDeformation infla) {
        PartDefinition p_pedestal = p_estatua.addOrReplaceChild("pedestal", CubeListBuilder.create()
                .texOffs(0, 98).addBox(-15F, 20.5F, -15F, 30F, 3.5F, 30F, infla)
                .texOffs(0, 133).addBox(-14.4F, 19.4F, -14.4F, 28.8F, 1.1F, 28.8F, infla)
                .texOffs(0, 164).addBox(-13.7F, 18.3F, -13.7F, 27.4F, 1.1F, 27.4F, infla)
                .texOffs(121, 98).addBox(-12.5F, 9.4F, -12.5F, 25F, 8.9F, 25F, infla)
                .texOffs(0, 164).addBox(-13.7F, 8.3F, -13.7F, 27.4F, 1.1F, 27.4F, infla)
                .texOffs(117, 133).addBox(-14.3F, 7.3F, -14.3F, 28.6F, 1F, 28.6F, infla)
                .texOffs(111, 164).addBox(-13.5F, 6F, -13.5F, 27F, 1.3F, 27F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        p_pedestal.addOrReplaceChild("pedestal_sol0", CubeListBuilder.create()
                .texOffs(99, 378).addBox(-2.2F, -2.2F, -0.55F, 4.4F, 4.4F, 0.6F, infla),
                PartPose.offsetAndRotation(0F, 13.85F, -12.5F, 0F, 0F, 0F));
        p_pedestal.addOrReplaceChild("pedestal_rayos0", CubeListBuilder.create()
                .texOffs(120, 378).addBox(-2F, -2F, -0.35F, 4F, 4F, 0.4F, infla)
                .texOffs(251, 0).addBox(-0.5F, -3.4F, -0.3F, 1F, 6.8F, 0.3F, infla)
                .texOffs(83, 385).addBox(-3.4F, -0.5F, -0.3F, 6.8F, 1F, 0.3F, infla),
                PartPose.offsetAndRotation(0F, 13.85F, -12.5F, 0F, 0F, 0.7854F));
        p_pedestal.addOrReplaceChild("pedestal_sol1", CubeListBuilder.create()
                .texOffs(99, 378).addBox(-2.2F, -2.2F, -0.55F, 4.4F, 4.4F, 0.6F, infla),
                PartPose.offsetAndRotation(-12.5F, 13.85F, 0F, 0F, 1.5708F, 0F));
        p_pedestal.addOrReplaceChild("pedestal_rayos1", CubeListBuilder.create()
                .texOffs(120, 378).addBox(-2F, -2F, -0.35F, 4F, 4F, 0.4F, infla)
                .texOffs(251, 0).addBox(-0.5F, -3.4F, -0.3F, 1F, 6.8F, 0.3F, infla)
                .texOffs(83, 385).addBox(-3.4F, -0.5F, -0.3F, 6.8F, 1F, 0.3F, infla),
                PartPose.offsetAndRotation(-12.5F, 13.85F, 0F, 1.5708F, 0.7854F, 1.5708F));
        p_pedestal.addOrReplaceChild("pedestal_sol2", CubeListBuilder.create()
                .texOffs(99, 378).addBox(-2.2F, -2.2F, -0.55F, 4.4F, 4.4F, 0.6F, infla),
                PartPose.offsetAndRotation(0F, 13.85F, 12.5F, 3.1416F, 0F, 3.1416F));
        p_pedestal.addOrReplaceChild("pedestal_rayos2", CubeListBuilder.create()
                .texOffs(120, 378).addBox(-2F, -2F, -0.35F, 4F, 4F, 0.4F, infla)
                .texOffs(251, 0).addBox(-0.5F, -3.4F, -0.3F, 1F, 6.8F, 0.3F, infla)
                .texOffs(83, 385).addBox(-3.4F, -0.5F, -0.3F, 6.8F, 1F, 0.3F, infla),
                PartPose.offsetAndRotation(0F, 13.85F, 12.5F, 3.1416F, 0F, 2.3562F));
        p_pedestal.addOrReplaceChild("pedestal_sol3", CubeListBuilder.create()
                .texOffs(99, 378).addBox(-2.2F, -2.2F, -0.55F, 4.4F, 4.4F, 0.6F, infla),
                PartPose.offsetAndRotation(12.5F, 13.85F, 0F, 0F, -1.5708F, 0F));
        p_pedestal.addOrReplaceChild("pedestal_rayos3", CubeListBuilder.create()
                .texOffs(120, 378).addBox(-2F, -2F, -0.35F, 4F, 4F, 0.4F, infla)
                .texOffs(251, 0).addBox(-0.5F, -3.4F, -0.3F, 1F, 6.8F, 0.3F, infla)
                .texOffs(83, 385).addBox(-3.4F, -0.5F, -0.3F, 6.8F, 1F, 0.3F, infla),
                PartPose.offsetAndRotation(12.5F, 13.85F, 0F, -1.5708F, -0.7854F, 1.5708F));
    }

    private static void rota_falda(PartDefinition p_estatua, CubeDeformation infla) {
        PartDefinition p_falda = p_estatua.addOrReplaceChild("falda", CubeListBuilder.create(),
                PartPose.offsetAndRotation(0F, -53F, 0F, 0F, 0F, 0F));
        p_falda.addOrReplaceChild("falda_0_2", CubeListBuilder.create()
                .texOffs(142, 272).addBox(-2.4135F, 11.9694F, -0.9F, 4.8269F, 11.3843F, 1.8F, infla)
                .texOffs(136, 378).addBox(-2.4635F, 21.7537F, -1.2F, 4.9269F, 1.5F, 2.15F, infla),
                PartPose.offsetAndRotation(-0.6F, 35.5F, -7.5883F, -0.0859F, 0F, -0.0132F));
        p_falda.addOrReplaceChild("falda_1_2", CubeListBuilder.create()
                .texOffs(6, 303).addBox(-2.4135F, 13.5782F, -0.9F, 4.8269F, 9.7395F, 1.8F, infla)
                .texOffs(136, 378).addBox(-2.4635F, 21.7177F, -1.2F, 4.9269F, 1.5F, 2.15F, infla),
                PartPose.offsetAndRotation(3.8239F, 35.5F, -8.6043F, 0.028F, -0.2814F, -0.0293F));
        p_falda.addOrReplaceChild("falda_2_2", CubeListBuilder.create()
                .texOffs(21, 303).addBox(-2.4135F, 14.6669F, -0.9F, 4.8269F, 9.2209F, 1.8F, infla)
                .texOffs(136, 378).addBox(-2.4635F, 22.2878F, -1.2F, 4.9269F, 1.5F, 2.15F, infla),
                PartPose.offsetAndRotation(8.1204F, 35.5F, -7.4472F, 0.0176F, -0.6222F, -0.0394F));
        p_falda.addOrReplaceChild("falda_3_2", CubeListBuilder.create()
                .texOffs(42, 329).addBox(-2.4135F, 17.2513F, -0.9F, 4.8269F, 7.3605F, 1.8F, infla)
                .texOffs(136, 378).addBox(-2.4635F, 23.0118F, -1.2F, 4.9269F, 1.5F, 2.15F, infla),
                PartPose.offsetAndRotation(8.3173F, 35.5F, -2.593F, -0.0855F, -1.0641F, -0.0267F));
        p_falda.addOrReplaceChild("falda_4_2", CubeListBuilder.create()
                .texOffs(131, 288).addBox(-2.4135F, 14.4848F, -0.9F, 4.8269F, 10.4029F, 1.8F, infla)
                .texOffs(136, 378).addBox(-2.4635F, 23.2877F, -1.2F, 4.9269F, 1.5F, 2.15F, infla),
                PartPose.offsetAndRotation(9.5675F, 35.5F, 0F, -0.1267F, -1.5708F, 0F));
        p_falda.addOrReplaceChild("falda_5_2", CubeListBuilder.create()
                .texOffs(57, 329).addBox(-2.4135F, 17.1746F, -0.9F, 4.8269F, 7.7421F, 1.8F, infla)
                .texOffs(136, 378).addBox(-2.4635F, 23.3167F, -1.2F, 4.9269F, 1.5F, 2.15F, infla),
                PartPose.offsetAndRotation(7.8754F, 35.5F, 2.5373F, 3.0044F, -1.1013F, -3.1372F));
        p_falda.addOrReplaceChild("falda_6_2", CubeListBuilder.create()
                .texOffs(185, 223).addBox(-2.4135F, 4.0986F, -0.9F, 4.8269F, 20.8848F, 1.8F, infla)
                .texOffs(136, 378).addBox(-2.4635F, 23.3835F, -1.2F, 4.9269F, 1.5F, 2.15F, infla),
                PartPose.offsetAndRotation(6.5243F, 35.5F, 5.6748F, 2.9855F, -0.7038F, -3.1356F));
        p_falda.addOrReplaceChild("falda_7_2", CubeListBuilder.create()
                .texOffs(92, 251).addBox(-2.4135F, 10.5487F, -0.9F, 4.8269F, 14.5189F, 1.8F, infla)
                .texOffs(136, 378).addBox(-2.4635F, 23.4676F, -1.2F, 4.9269F, 1.5F, 2.15F, infla),
                PartPose.offsetAndRotation(2.9344F, 35.5F, 6.5479F, 2.967F, -0.3464F, -3.1373F));
        p_falda.addOrReplaceChild("falda_8_2", CubeListBuilder.create()
                .texOffs(72, 329).addBox(-2.4135F, 17.6129F, -0.9F, 4.8269F, 7.4857F, 1.8F, infla)
                .texOffs(136, 378).addBox(-2.4635F, 23.4986F, -1.2F, 4.9269F, 1.5F, 2.15F, infla),
                PartPose.offsetAndRotation(-0.6F, 35.5F, 8.15F, 2.9618F, 0F, 3.1292F));
        p_falda.addOrReplaceChild("falda_9_2", CubeListBuilder.create()
                .texOffs(157, 272).addBox(-2.4135F, 13.2376F, -0.9F, 4.8269F, 11.8045F, 1.8F, infla)
                .texOffs(136, 378).addBox(-2.4635F, 23.4421F, -1.2F, 4.9269F, 1.5F, 2.15F, infla),
                PartPose.offsetAndRotation(-4.1344F, 35.5F, 6.5479F, 2.9668F, 0.3463F, 3.1125F));
        p_falda.addOrReplaceChild("falda_10_2", CubeListBuilder.create()
                .texOffs(87, 329).addBox(-2.4135F, 16.8726F, -0.9F, 4.8269F, 8.0613F, 1.8F, infla)
                .texOffs(136, 378).addBox(-2.4635F, 23.3339F, -1.2F, 4.9269F, 1.5F, 2.15F, infla),
                PartPose.offsetAndRotation(-7.7243F, 35.5F, 5.6748F, 2.9852F, 0.7036F, 3.1108F));
        p_falda.addOrReplaceChild("falda_11_2", CubeListBuilder.create()
                .texOffs(241, 223).addBox(-2.4135F, 5.3072F, -0.9F, 4.8269F, 19.5462F, 1.8F, infla)
                .texOffs(136, 378).addBox(-2.4635F, 23.2534F, -1.2F, 4.9269F, 1.5F, 2.15F, infla),
                PartPose.offsetAndRotation(-9.0753F, 35.5F, 2.5373F, 3.004F, 1.1012F, 3.1124F));
        p_falda.addOrReplaceChild("falda_12_2", CubeListBuilder.create()
                .texOffs(107, 251).addBox(-2.4135F, 10.4964F, -0.9F, 4.8269F, 14.3323F, 1.8F, infla)
                .texOffs(136, 378).addBox(-2.4635F, 23.2288F, -1.2F, 4.9269F, 1.5F, 2.15F, infla),
                PartPose.offsetAndRotation(-10.75F, 35.5F, 0F, -0.1029F, 1.5708F, 0F));
        p_falda.addOrReplaceChild("falda_13_2", CubeListBuilder.create()
                .texOffs(0, 251).addBox(-2.4135F, 7.2472F, -0.9F, 4.8269F, 17.5768F, 1.8F, infla)
                .texOffs(136, 378).addBox(-2.4635F, 23.224F, -1.2F, 4.9269F, 1.5F, 2.15F, infla),
                PartPose.offsetAndRotation(-9.0822F, 35.5F, -2.3348F, -0.1067F, 1.0643F, 0.0004F));
        p_falda.addOrReplaceChild("falda_14_2", CubeListBuilder.create()
                .texOffs(230, 251).addBox(-2.4135F, 11.4619F, -0.9F, 4.8269F, 13.1047F, 1.8F, infla)
                .texOffs(136, 378).addBox(-2.4635F, 22.9666F, -1.2F, 4.9269F, 1.5F, 2.15F, infla),
                PartPose.offsetAndRotation(-7.6964F, 35.5F, -5.0453F, -0.1059F, 0.6226F, 0.0092F));
        p_falda.addOrReplaceChild("falda_15_2", CubeListBuilder.create()
                .texOffs(0, 272).addBox(-2.4135F, 11.5922F, -0.9F, 4.8269F, 12.3565F, 1.8F, infla)
                .texOffs(136, 378).addBox(-2.4635F, 22.3487F, -1.2F, 4.9269F, 1.5F, 2.15F, infla),
                PartPose.offsetAndRotation(-4.1635F, 35.5F, -5.4638F, -0.1124F, 0.2815F, 0.0009F));
    }

    private static void rota_ala_rota(PartDefinition p_estatua, CubeDeformation infla) {
        PartDefinition p_ala_rota = p_estatua.addOrReplaceChild("ala_rota", CubeListBuilder.create()
                .texOffs(105, 0).addBox(-0.5F, -30F, -4F, 1F, 45F, 26F, infla),
                PartPose.offsetAndRotation(9.5F, -2.502F, 4F, 0F, 0.3142F, 1.4661F));
        p_ala_rota.addOrReplaceChild("ala_rota_hueso0", CubeListBuilder.create()
                .texOffs(95, 272).addBox(-2F, -0.9F, -1.7F, 4F, 10.3586F, 3.4F, infla)
                .texOffs(69, 351).addBox(-2.15F, -1.9F, -2F, 4.3F, 3.8F, 4F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0F, 3.0245F, 0F, 0F));
        p_ala_rota.addOrReplaceChild("ala_rota_hueso1", CubeListBuilder.create()
                .texOffs(111, 272).addBox(-1.85F, -0.9F, -1.7F, 3.7F, 10.5801F, 3.4F, infla)
                .texOffs(87, 351).addBox(-2F, -1.9F, -2F, 4F, 3.8F, 4F, infla),
                PartPose.offsetAndRotation(0F, -8.5F, 1F, 2.8883F, 0F, 0F));
        p_ala_rota.addOrReplaceChild("ala_rota_menor0", CubeListBuilder.create()
                .texOffs(116, 329).addBox(1.55F, -0.6F, -2.1F, 1.1F, 5.1F, 4.2F, infla)
                .texOffs(116, 329).addBox(-2.65F, -0.6F, -2.1F, 1.1F, 5.1F, 4.2F, infla),
                PartPose.offsetAndRotation(0F, -1.3925F, 0.7462F, 0.1857F, 0.087F, 0.0163F));
        p_ala_rota.addOrReplaceChild("ala_rota_menor1", CubeListBuilder.create()
                .texOffs(128, 329).addBox(1.75F, -0.6F, -2.1F, 1.1F, 5.325F, 4.2F, infla)
                .texOffs(128, 329).addBox(-2.85F, -0.6F, -2.1F, 1.1F, 5.325F, 4.2F, infla),
                PartPose.offsetAndRotation(0F, -6.1006F, 1.3001F, 0.2096F, 0.0969F, 0.0206F));
        p_ala_rota.addOrReplaceChild("ala_rota_menor2", CubeListBuilder.create()
                .texOffs(140, 329).addBox(1.55F, -0.6F, -2.1F, 1.1F, 5.55F, 4.2F, infla)
                .texOffs(140, 329).addBox(-2.65F, -0.6F, -2.1F, 1.1F, 5.55F, 4.2F, infla),
                PartPose.offsetAndRotation(0F, -10.7329F, 2.2591F, 0.234F, 0.1249F, 0.0297F));
        p_ala_rota.addOrReplaceChild("ala_rota_marginal0", CubeListBuilder.create()
                .texOffs(244, 351).addBox(1.9F, -0.6F, -1.8F, 1.2F, 3.47F, 3.6F, infla)
                .texOffs(244, 351).addBox(-3.1F, -0.6F, -1.8F, 1.2F, 3.47F, 3.6F, infla),
                PartPose.offsetAndRotation(0F, -2.2295F, 0.8446F, 0.418F, 0.1454F, 0.0643F));
        p_ala_rota.addOrReplaceChild("ala_rota_marginal1", CubeListBuilder.create()
                .texOffs(0, 361).addBox(2.1F, -0.6F, -1.8F, 1.2F, 3.5914F, 3.6F, infla)
                .texOffs(0, 361).addBox(-3.3F, -0.6F, -1.8F, 1.2F, 3.5914F, 3.6F, infla),
                PartPose.offsetAndRotation(0F, -7.3113F, 1.4425F, 0.4662F, 0.091F, 0.0457F));
        p_ala_rota.addOrReplaceChild("ala_rota_marginal2", CubeListBuilder.create()
                .texOffs(11, 361).addBox(1.9F, -0.6F, -1.8F, 1.2F, 3.7129F, 3.6F, infla)
                .texOffs(11, 361).addBox(-3.1F, -0.6F, -1.8F, 1.2F, 3.7129F, 3.6F, infla),
                PartPose.offsetAndRotation(0F, -12.2772F, 2.6588F, 0.5171F, 0.0862F, 0.0489F));
    }
}
