package com.atalaya.client;

import net.minecraft.client.model.geom.PartPose;
import net.minecraft.client.model.geom.builders.CubeDeformation;
import net.minecraft.client.model.geom.builders.CubeListBuilder;
import net.minecraft.client.model.geom.builders.LayerDefinition;
import net.minecraft.client.model.geom.builders.MeshDefinition;
import net.minecraft.client.model.geom.builders.PartDefinition;

/**
 * La malla de Rajang, el Jaguar de Jade. GENERADO por
 * materiales/generadores/rajang_juego.py: no se edita a mano. Cada caja tiene su
 * hueco en el atlas (1024x1024, un texel por pixel) y se pinta segun
 * donde cae en el cuerpo: cambiar una caja aqui sin el script descuadra la piel.
 */
public final class RajangMalla {

    /** Las piezas de cristal, que crecen con la fase (escaladas desde su base). */
    public static final String[] CRISTALES = {"cresta0_a", "cresta0_0", "cresta0_1", "cresta1_a", "cresta1_0", "cresta1_1", "cresta2_a", "cresta2_0", "cresta2_1", "cresta3_a", "cresta3_0", "cresta3_1", "cresta3_2", "cresta4_a", "cresta4_0", "cresta4_1", "cresta4_2", "cresta5_a", "cresta5_0", "cresta5_1", "cresta5_2", "cresta6_a", "cresta6_0", "cresta6_1", "cresta7_a", "cresta7_0", "cresta7_1", "cresta7_2", "hombro_izq_a", "hombro_izq_0", "hombro_izq_1", "hombro_izq_2", "hombro_der_a", "hombro_der_0", "hombro_der_1", "hombro_der_2", "corona_i", "corona_d", "corona_c_a", "corona_c_0", "corona_c_1", "corona_c_2", "cresta_cuello_a", "cresta_cuello_0", "cresta_cuello_1", "cresta_cuello_2", "punta_cola"};

    private RajangMalla() {
    }

    public static LayerDefinition crear() {
        return crear(CubeDeformation.NONE);
    }

    /** La misma malla hinchada: la capa del aura de la Furia (como la carga del creeper). */
    public static LayerDefinition crearAura() {
        return crear(new CubeDeformation(1.5F));
    }

    private static LayerDefinition crear(CubeDeformation infla) {
        MeshDefinition malla = new MeshDefinition();
        PartDefinition p_root = malla.getRoot();
        PartDefinition p_raiz = p_root.addOrReplaceChild("raiz", CubeListBuilder.create(),
                PartPose.offsetAndRotation(0F, 0F, 56F, 0F, 0F, 0F));
        PartDefinition p_cuerpo = p_raiz.addOrReplaceChild("cuerpo", CubeListBuilder.create()
                .texOffs(0, 0).addBox(-32F, -30F, -115F, 64F, 64F, 64F, infla)
                .texOffs(398, 130).addBox(-36F, -22F, -104F, 8F, 36F, 40F, infla)
                .texOffs(496, 130).addBox(28F, -22F, -104F, 8F, 36F, 40F, infla)
                .texOffs(72, 288).addBox(-23F, -36F, -108F, 46F, 12F, 38F, infla)
                .texOffs(258, 0).addBox(-28F, -28F, -52F, 56F, 56F, 38F, infla)
                .texOffs(594, 130).addBox(-22F, -24F, -14F, 44F, 38F, 34F, infla)
                .texOffs(448, 0).addBox(-26F, -26F, 18F, 52F, 48F, 44F, infla)
                .texOffs(750, 288).addBox(-22F, -30F, 22F, 44F, 6F, 36F, infla)
                .texOffs(242, 218).addBox(-25F, 32F, -110F, 50F, 4F, 56F, infla)
                .texOffs(164, 342).addBox(-20F, 26F, -50F, 40F, 4F, 34F, infla)
                .texOffs(914, 130).addBox(-40F, -28F, -114F, 4F, 34F, 34F, infla)
                .texOffs(0, 218).addBox(36F, -28F, -114F, 4F, 34F, 34F, infla)
                .texOffs(610, 218).addBox(-31F, -18F, -44F, 3F, 28F, 28F, infla)
                .texOffs(674, 218).addBox(28F, -18F, -44F, 3F, 28F, 28F, infla)
                .texOffs(464, 342).addBox(-18F, -31F, -40F, 36F, 4F, 34F, infla)
                .texOffs(976, 547).addBox(-13.8438F, -38.2466F, -83.4694F, 6F, 4.2466F, 8F, infla)
                .texOffs(22, 578).addBox(10.7455F, -38.5056F, -103.7372F, 4F, 4.5056F, 6F, infla)
                .texOffs(878, 547).addBox(2.3894F, -38.9002F, -101.5952F, 8F, 4.9002F, 8F, infla)
                .texOffs(0, 563).addBox(-12.9472F, -38.3452F, -104.6653F, 6F, 4.3452F, 8F, infla)
                .texOffs(633, 547).addBox(13.7115F, -39.2435F, -104.3535F, 4F, 5.2435F, 8F, infla)
                .texOffs(318, 563).addBox(6.8434F, -39.0792F, -80.2692F, 8F, 5.0792F, 6F, infla)
                .texOffs(433, 563).addBox(9.7198F, -29.9486F, -26.871F, 4F, 3.9486F, 8F, infla)
                .texOffs(392, 578).addBox(-9.0169F, -30.2931F, -48.7042F, 6F, 4.2931F, 4F, infla)
                .texOffs(66, 578).addBox(-20.0276F, -31.2587F, -38.6355F, 8F, 5.2587F, 4F, infla)
                .texOffs(926, 578).addBox(-5.8604F, -29.547F, -22.8077F, 6F, 3.547F, 4F, infla)
                .texOffs(459, 563).addBox(8.5745F, -29.5077F, -44.8606F, 4F, 3.5077F, 8F, infla)
                .texOffs(168, 578).addBox(-18.6599F, -29.5165F, -34.8865F, 4F, 3.5165F, 6F, infla)
                .texOffs(485, 563).addBox(-2.1043F, -25.6697F, 8.2604F, 4F, 3.6697F, 8F, infla)
                .texOffs(414, 578).addBox(1.1615F, -26.2963F, -9.5711F, 6F, 4.2963F, 4F, infla)
                .texOffs(900, 578).addBox(-0.9511F, -25.8451F, 12.9165F, 8F, 3.8451F, 4F, infla)
                .texOffs(44, 578).addBox(1.4042F, -26.6101F, -8.4167F, 4F, 4.6101F, 6F, infla)
                .texOffs(494, 547).addBox(11.9389F, -27.4898F, -9.3306F, 6F, 5.4898F, 8F, infla)
                .texOffs(348, 563).addBox(-11.37F, -27.4018F, 2.6671F, 8F, 5.4018F, 6F, infla)
                .texOffs(60, 563).addBox(4.2685F, -32.2319F, 39.3467F, 4F, 4.2319F, 8F, infla)
                .texOffs(92, 578).addBox(-16.4811F, -33.2347F, 50.4513F, 8F, 5.2347F, 4F, infla)
                .texOffs(118, 578).addBox(-13.2417F, -31.9201F, 50.5133F, 6F, 3.9201F, 6F, infla)
                .texOffs(366, 578).addBox(-0.5521F, -32.2579F, 24.0184F, 8F, 4.2579F, 4F, infla)
                .texOffs(20, 592).addBox(-10.2931F, -31.9434F, 48.441F, 4F, 3.9434F, 4F, infla)
                .texOffs(30, 563).addBox(-2.4049F, -32.0698F, 25.4343F, 6F, 4.0698F, 8F, infla)
                .texOffs(524, 547).addBox(30F, -2.1175F, -77.9465F, 4.7113F, 6F, 8F, infla)
                .texOffs(552, 547).addBox(30F, 13.8357F, -94.2707F, 4.0595F, 6F, 8F, infla)
                .texOffs(856, 547).addBox(30F, 11.4175F, -99.0544F, 3.7566F, 8F, 6F, infla)
                .texOffs(38, 592).addBox(30F, -3.2799F, -71.0979F, 3.5732F, 4F, 4F, infla)
                .texOffs(659, 547).addBox(-33.5222F, 11.1422F, -98.3195F, 3.5222F, 6F, 8F, infla)
                .texOffs(685, 547).addBox(-33.9166F, 18.318F, -76.1201F, 3.9166F, 6F, 8F, infla)
                .texOffs(787, 547).addBox(-34.3823F, 9.7153F, -78.8406F, 4.3823F, 8F, 6F, infla)
                .texOffs(406, 563).addBox(26F, 15.9646F, -36.0788F, 4.2231F, 4F, 8F, infla)
                .texOffs(579, 547).addBox(20F, -6.2175F, -11.4286F, 4.2054F, 6F, 8F, infla)
                .texOffs(190, 578).addBox(20F, -10.2846F, -0.8676F, 3.6269F, 4F, 6F, infla)
                .texOffs(711, 547).addBox(20F, -9.506F, -1.4788F, 3.7229F, 6F, 8F, infla)
                .texOffs(948, 578).addBox(20F, -1.8903F, -0.2614F, 4.839F, 4F, 4F, infla)
                .texOffs(968, 578).addBox(20F, -15.3894F, -10.629F, 4.953F, 4F, 4F, infla)
                .texOffs(378, 563).addBox(20F, -9.0617F, 4.3032F, 4.9643F, 4F, 8F, infla)
                .texOffs(606, 547).addBox(-24.283F, -9.8713F, 1.9637F, 4.283F, 6F, 8F, infla)
                .texOffs(56, 592).addBox(-23.8845F, -5.5721F, -6.8687F, 3.8845F, 4F, 4F, infla)
                .texOffs(937, 563).addBox(-24.9159F, -17.5109F, -9.5219F, 4.9159F, 6F, 6F, infla)
                .texOffs(212, 578).addBox(-24.8484F, -7.5373F, -3.8075F, 4.8484F, 6F, 4F, infla)
                .texOffs(511, 563).addBox(-23.5879F, -11.3956F, -5.3967F, 3.5879F, 4F, 8F, infla)
                .texOffs(144, 578).addBox(-24.6794F, 3.642F, 10.3363F, 4.6794F, 4F, 6F, infla)
                .texOffs(232, 578).addBox(24F, -6.8204F, 34.9968F, 3.5442F, 6F, 4F, infla)
                .texOffs(985, 563).addBox(24F, 6.4248F, 50.3438F, 4.3451F, 6F, 6F, infla)
                .texOffs(250, 578).addBox(24F, -10.9734F, 36.798F, 3.6178F, 6F, 4F, infla)
                .texOffs(810, 547).addBox(24F, -14.7826F, 33.6736F, 4.1599F, 8F, 6F, infla)
                .texOffs(268, 578).addBox(24F, -3.6836F, 26.7882F, 3.7559F, 6F, 4F, infla)
                .texOffs(833, 547).addBox(24F, -16.1446F, 41.2626F, 4.4881F, 8F, 6F, infla)
                .texOffs(961, 563).addBox(-28.9435F, -2.0147F, 51.9782F, 4.9435F, 6F, 6F, infla)
                .texOffs(90, 529).addBox(-28.0773F, -0.4838F, 44.6841F, 4.0773F, 8F, 8F, infla)
                .texOffs(988, 578).addBox(-28.5047F, -6.5016F, 28.1845F, 4.5047F, 4F, 4F, infla)
                .texOffs(763, 547).addBox(-28.6459F, 2.377F, 37.0798F, 4.6459F, 8F, 6F, infla)
                .texOffs(737, 547).addBox(-27.5048F, 7.53F, 26.5637F, 3.5048F, 6F, 8F, infla)
                .texOffs(0, 592).addBox(-28.9748F, -9.9312F, 23.2937F, 4.9748F, 4F, 4F, infla),
                PartPose.offsetAndRotation(0F, -72F, 0F, 0F, 0F, 0F));
        p_cuerpo.addOrReplaceChild("peto", CubeListBuilder.create()
                .texOffs(394, 422).addBox(-14F, -10F, -117.5F, 28F, 26F, 3F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        p_cuerpo.addOrReplaceChild("sol", CubeListBuilder.create()
                .texOffs(542, 483).addBox(-10F, -7F, -118.5F, 20F, 20F, 0F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        PartDefinition p_cresta0 = p_cuerpo.addOrReplaceChild("cresta0", CubeListBuilder.create()
                .texOffs(60, 456).addBox(-9F, -3F, -9F, 18F, 6F, 18F, infla),
                PartPose.offsetAndRotation(0F, -36F, -102F, -0.6283F, 0F, 0F));
        p_cresta0.addOrReplaceChild("cresta0_a", CubeListBuilder.create()
                .texOffs(814, 384).addBox(-5F, -22.5F, -5F, 10F, 22.5F, 10F, infla)
                .texOffs(802, 483).addBox(-6.5F, -5F, -6.5F, 13F, 5F, 13F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        p_cresta0.addOrReplaceChild("cresta0_0", CubeListBuilder.create()
                .texOffs(216, 483).addBox(-3.5F, -15.2153F, -3.5F, 7F, 15.2153F, 7F, infla)
                .texOffs(169, 529).addBox(-5F, -5F, -5F, 10F, 5F, 10F, infla),
                PartPose.offsetAndRotation(5.5197F, 1F, 1.3573F, 0.0356F, -0.2308F, 0.31F));
        p_cresta0.addOrReplaceChild("cresta0_1", CubeListBuilder.create()
                .texOffs(584, 483).addBox(-4F, -11.9202F, -4F, 8F, 11.9202F, 8F, infla)
                .texOffs(698, 509).addBox(-5.5F, -5F, -5.5F, 11F, 5F, 11F, infla),
                PartPose.offsetAndRotation(-6.9877F, 1F, -3.9675F, -0.0247F, -0.2034F, -0.2869F));
        PartDefinition p_cresta1 = p_cuerpo.addOrReplaceChild("cresta1", CubeListBuilder.create()
                .texOffs(134, 456).addBox(-9F, -3F, -9F, 18F, 6F, 18F, infla),
                PartPose.offsetAndRotation(0F, -37F, -88F, -0.6981F, 0F, 0F));
        p_cresta1.addOrReplaceChild("cresta1_a", CubeListBuilder.create()
                .texOffs(912, 288).addBox(-5F, -31.5F, -5F, 10F, 31.5F, 10F, infla)
                .texOffs(856, 483).addBox(-6.5F, -5F, -6.5F, 13F, 5F, 13F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        p_cresta1.addOrReplaceChild("cresta1_0", CubeListBuilder.create()
                .texOffs(276, 483).addBox(-3F, -16.3899F, -3F, 6F, 16.3899F, 6F, infla)
                .texOffs(843, 529).addBox(-4.5F, -5F, -4.5F, 9F, 5F, 9F, infla),
                PartPose.offsetAndRotation(5.836F, 1F, -0.8197F, 0.2393F, -0.0177F, 0.4448F));
        p_cresta1.addOrReplaceChild("cresta1_1", CubeListBuilder.create()
                .texOffs(836, 422).addBox(-3F, -20.3837F, -3F, 6F, 20.3837F, 6F, infla)
                .texOffs(881, 529).addBox(-4.5F, -5F, -4.5F, 9F, 5F, 9F, infla),
                PartPose.offsetAndRotation(-5.3672F, 1F, 0.2755F, -0.063F, 0.0596F, -0.2264F));
        PartDefinition p_cresta2 = p_cuerpo.addOrReplaceChild("cresta2", CubeListBuilder.create()
                .texOffs(208, 456).addBox(-9F, -3F, -9F, 18F, 6F, 18F, infla),
                PartPose.offsetAndRotation(0F, -36F, -74F, -0.7679F, 0F, 0F));
        p_cresta2.addOrReplaceChild("cresta2_a", CubeListBuilder.create()
                .texOffs(122, 342).addBox(-5F, -30F, -5F, 10F, 30F, 10F, infla)
                .texOffs(910, 483).addBox(-6.5F, -5F, -6.5F, 13F, 5F, 13F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        p_cresta2.addOrReplaceChild("cresta2_0", CubeListBuilder.create()
                .texOffs(970, 422).addBox(-4F, -16.8535F, -4F, 8F, 16.8535F, 8F, infla)
                .texOffs(744, 509).addBox(-5.5F, -5F, -5.5F, 11F, 5F, 11F, infla),
                PartPose.offsetAndRotation(5.4852F, 1F, 1.1309F, -0.1854F, 0.1057F, 0.2939F));
        p_cresta2.addOrReplaceChild("cresta2_1", CubeListBuilder.create()
                .texOffs(764, 422).addBox(-3.5F, -20.6961F, -3.5F, 7F, 20.6961F, 7F, infla)
                .texOffs(211, 529).addBox(-5F, -5F, -5F, 10F, 5F, 10F, infla),
                PartPose.offsetAndRotation(-6.7791F, 1F, -2.6826F, 0.2327F, -0.224F, -0.3443F));
        PartDefinition p_cresta3 = p_cuerpo.addOrReplaceChild("cresta3", CubeListBuilder.create()
                .texOffs(282, 456).addBox(-9F, -3F, -9F, 18F, 6F, 18F, infla),
                PartPose.offsetAndRotation(0F, -29F, -58F, -0.8378F, 0F, 0F));
        p_cresta3.addOrReplaceChild("cresta3_a", CubeListBuilder.create()
                .texOffs(180, 384).addBox(-5F, -25.5F, -5F, 10F, 25.5F, 10F, infla)
                .texOffs(964, 483).addBox(-6.5F, -5F, -6.5F, 13F, 5F, 13F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        p_cresta3.addOrReplaceChild("cresta3_0", CubeListBuilder.create()
                .texOffs(246, 483).addBox(-3.5F, -15.2492F, -3.5F, 7F, 15.2492F, 7F, infla)
                .texOffs(253, 529).addBox(-5F, -5F, -5F, 10F, 5F, 10F, infla),
                PartPose.offsetAndRotation(6.7849F, 1F, -4.1645F, -0.059F, -0.0991F, 0.3868F));
        p_cresta3.addOrReplaceChild("cresta3_1", CubeListBuilder.create()
                .texOffs(368, 483).addBox(-3F, -15.4285F, -3F, 6F, 15.4285F, 6F, infla)
                .texOffs(919, 529).addBox(-4.5F, -5F, -4.5F, 9F, 5F, 9F, infla),
                PartPose.offsetAndRotation(-5.5348F, 1F, -4.8592F, -0.1926F, 0.336F, -0.3312F));
        p_cresta3.addOrReplaceChild("cresta3_2", CubeListBuilder.create()
                .texOffs(490, 483).addBox(-3F, -14.2245F, -3F, 6F, 14.2245F, 6F, infla)
                .texOffs(957, 529).addBox(-4.5F, -5F, -4.5F, 9F, 5F, 9F, infla),
                PartPose.offsetAndRotation(5.0392F, 1F, 1.2767F, -0.1439F, -0.3244F, 0.2996F));
        PartDefinition p_cresta4 = p_cuerpo.addOrReplaceChild("cresta4", CubeListBuilder.create()
                .texOffs(356, 456).addBox(-9F, -3F, -9F, 18F, 6F, 18F, infla),
                PartPose.offsetAndRotation(0F, -28F, -42F, -0.9076F, 0F, 0F));
        p_cresta4.addOrReplaceChild("cresta4_a", CubeListBuilder.create()
                .texOffs(922, 384).addBox(-5F, -21.6F, -5F, 10F, 21.6F, 10F, infla)
                .texOffs(0, 509).addBox(-6.5F, -5F, -6.5F, 13F, 5F, 13F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        p_cresta4.addOrReplaceChild("cresta4_0", CubeListBuilder.create()
                .texOffs(394, 483).addBox(-3F, -15.1107F, -3F, 6F, 15.1107F, 6F, infla)
                .texOffs(0, 547).addBox(-4.5F, -5F, -4.5F, 9F, 5F, 9F, infla),
                PartPose.offsetAndRotation(6.6796F, 1F, -3.1741F, -0.1616F, 0.1268F, 0.3819F));
        p_cresta4.addOrReplaceChild("cresta4_1", CubeListBuilder.create()
                .texOffs(568, 509).addBox(-3F, -11.2502F, -3F, 6F, 11.2502F, 6F, infla)
                .texOffs(38, 547).addBox(-4.5F, -5F, -4.5F, 9F, 5F, 9F, infla),
                PartPose.offsetAndRotation(-6.9975F, 1F, 3.0638F, -0.0286F, 0.2554F, -0.4508F));
        p_cresta4.addOrReplaceChild("cresta4_2", CubeListBuilder.create()
                .texOffs(182, 483).addBox(-4F, -14.8941F, -4F, 8F, 14.8941F, 8F, infla)
                .texOffs(790, 509).addBox(-5.5F, -5F, -5.5F, 11F, 5F, 11F, infla),
                PartPose.offsetAndRotation(5.2312F, 1F, 0.1689F, 0.1687F, 0.127F, 0.3316F));
        PartDefinition p_cresta5 = p_cuerpo.addOrReplaceChild("cresta5", CubeListBuilder.create()
                .texOffs(430, 456).addBox(-9F, -3F, -9F, 18F, 6F, 18F, infla),
                PartPose.offsetAndRotation(0F, -25F, -26F, -0.9774F, 0F, 0F));
        p_cresta5.addOrReplaceChild("cresta5_a", CubeListBuilder.create()
                .texOffs(638, 422).addBox(-5F, -18F, -5F, 10F, 18F, 10F, infla)
                .texOffs(54, 509).addBox(-6.5F, -5F, -6.5F, 13F, 5F, 13F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        p_cresta5.addOrReplaceChild("cresta5_0", CubeListBuilder.create()
                .texOffs(0, 529).addBox(-3.5F, -8.169F, -3.5F, 7F, 8.169F, 7F, infla)
                .texOffs(295, 529).addBox(-5F, -5F, -5F, 10F, 5F, 10F, infla),
                PartPose.offsetAndRotation(6.537F, 1F, 3.4354F, 0.0667F, -0.3195F, 0.4423F));
        p_cresta5.addOrReplaceChild("cresta5_1", CubeListBuilder.create()
                .texOffs(768, 483).addBox(-4F, -10.0084F, -4F, 8F, 10.0084F, 8F, infla)
                .texOffs(836, 509).addBox(-5.5F, -5F, -5.5F, 11F, 5F, 11F, infla),
                PartPose.offsetAndRotation(-5.5114F, 1F, -1.941F, 0.1753F, 0.053F, -0.3876F));
        p_cresta5.addOrReplaceChild("cresta5_2", CubeListBuilder.create()
                .texOffs(652, 483).addBox(-3.5F, -12.3536F, -3.5F, 7F, 12.3536F, 7F, infla)
                .texOffs(337, 529).addBox(-5F, -5F, -5F, 10F, 5F, 10F, infla),
                PartPose.offsetAndRotation(5.3943F, 1F, 4.6348F, 0.1587F, -0.2227F, 0.2971F));
        PartDefinition p_cresta6 = p_cuerpo.addOrReplaceChild("cresta6", CubeListBuilder.create()
                .texOffs(504, 456).addBox(-9F, -3F, -9F, 18F, 6F, 18F, infla),
                PartPose.offsetAndRotation(0F, -25F, -8F, -1.0472F, 0F, 0F));
        p_cresta6.addOrReplaceChild("cresta6_a", CubeListBuilder.create()
                .texOffs(928, 422).addBox(-5F, -15F, -5F, 10F, 15F, 10F, infla)
                .texOffs(108, 509).addBox(-6.5F, -5F, -6.5F, 13F, 5F, 13F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        p_cresta6.addOrReplaceChild("cresta6_0", CubeListBuilder.create()
                .texOffs(673, 529).addBox(-3F, -8.7901F, -3F, 6F, 8.7901F, 6F, infla)
                .texOffs(76, 547).addBox(-4.5F, -5F, -4.5F, 9F, 5F, 9F, infla),
                PartPose.offsetAndRotation(6.319F, 1F, -0.6754F, 0.135F, 0.1846F, 0.2196F));
        p_cresta6.addOrReplaceChild("cresta6_1", CubeListBuilder.create()
                .texOffs(117, 529).addBox(-3F, -9.1329F, -3F, 6F, 9.1329F, 6F, infla)
                .texOffs(114, 547).addBox(-4.5F, -5F, -4.5F, 9F, 5F, 9F, infla),
                PartPose.offsetAndRotation(-6.3668F, 1F, 0.0274F, 0.2379F, -0.0634F, -0.4157F));
        PartDefinition p_cresta7 = p_cuerpo.addOrReplaceChild("cresta7", CubeListBuilder.create()
                .texOffs(578, 456).addBox(-9F, -3F, -9F, 18F, 6F, 18F, infla),
                PartPose.offsetAndRotation(0F, -31F, 12F, -1.117F, 0F, 0F));
        p_cresta7.addOrReplaceChild("cresta7_a", CubeListBuilder.create()
                .texOffs(0, 483).addBox(-5F, -13.5F, -5F, 10F, 13.5F, 10F, infla)
                .texOffs(162, 509).addBox(-6.5F, -5F, -6.5F, 13F, 5F, 13F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        p_cresta7.addOrReplaceChild("cresta7_0", CubeListBuilder.create()
                .texOffs(86, 563).addBox(-3F, -6.7379F, -3F, 6F, 6.7379F, 6F, infla)
                .texOffs(152, 547).addBox(-4.5F, -5F, -4.5F, 9F, 5F, 9F, infla),
                PartPose.offsetAndRotation(6.4027F, 1F, 4.5705F, -0.12F, 0.0276F, 0.2712F));
        p_cresta7.addOrReplaceChild("cresta7_1", CubeListBuilder.create()
                .texOffs(112, 563).addBox(-3F, -6.9115F, -3F, 6F, 6.9115F, 6F, infla)
                .texOffs(190, 547).addBox(-4.5F, -5F, -4.5F, 9F, 5F, 9F, infla),
                PartPose.offsetAndRotation(-6.6683F, 1F, -0.971F, -0.0043F, -0.2993F, -0.4337F));
        p_cresta7.addOrReplaceChild("cresta7_2", CubeListBuilder.create()
                .texOffs(30, 529).addBox(-3.5F, -8.9052F, -3.5F, 7F, 8.9052F, 7F, infla)
                .texOffs(379, 529).addBox(-5F, -5F, -5F, 10F, 5F, 10F, infla),
                PartPose.offsetAndRotation(6.146F, 1F, -4.2127F, 0.1174F, 0.11F, 0.452F));
        PartDefinition p_hombro_izq = p_cuerpo.addOrReplaceChild("hombro_izq", CubeListBuilder.create()
                .texOffs(652, 456).addBox(-9F, -3F, -9F, 18F, 6F, 18F, infla),
                PartPose.offsetAndRotation(26F, -24F, -98F, -0.5236F, 0F, -0.5236F));
        p_hombro_izq.addOrReplaceChild("hombro_izq_a", CubeListBuilder.create()
                .texOffs(680, 422).addBox(-5F, -18F, -5F, 10F, 18F, 10F, infla)
                .texOffs(216, 509).addBox(-6.5F, -5F, -6.5F, 13F, 5F, 13F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        p_hombro_izq.addOrReplaceChild("hombro_izq_0", CubeListBuilder.create()
                .texOffs(682, 483).addBox(-3.5F, -12.159F, -3.5F, 7F, 12.159F, 7F, infla)
                .texOffs(421, 529).addBox(-5F, -5F, -5F, 10F, 5F, 10F, infla),
                PartPose.offsetAndRotation(5.6644F, 1F, 4.926F, 0.0381F, 0.1327F, 0.3446F));
        p_hombro_izq.addOrReplaceChild("hombro_izq_1", CubeListBuilder.create()
                .texOffs(646, 509).addBox(-3F, -10.6939F, -3F, 6F, 10.6939F, 6F, infla)
                .texOffs(228, 547).addBox(-4.5F, -5F, -4.5F, 9F, 5F, 9F, infla),
                PartPose.offsetAndRotation(-5.7671F, 1F, 2.3162F, 0.079F, 0.2369F, -0.3168F));
        p_hombro_izq.addOrReplaceChild("hombro_izq_2", CubeListBuilder.create()
                .texOffs(594, 509).addBox(-3F, -11.3543F, -3F, 6F, 11.3543F, 6F, infla)
                .texOffs(266, 547).addBox(-4.5F, -5F, -4.5F, 9F, 5F, 9F, infla),
                PartPose.offsetAndRotation(5.3101F, 1F, -3.5016F, -0.1185F, 0.1335F, 0.3521F));
        PartDefinition p_hombro_der = p_cuerpo.addOrReplaceChild("hombro_der", CubeListBuilder.create()
                .texOffs(726, 456).addBox(-9F, -3F, -9F, 18F, 6F, 18F, infla),
                PartPose.offsetAndRotation(-26F, -24F, -98F, -0.5236F, 0F, 0.5236F));
        p_hombro_der.addOrReplaceChild("hombro_der_a", CubeListBuilder.create()
                .texOffs(722, 422).addBox(-5F, -18F, -5F, 10F, 18F, 10F, infla)
                .texOffs(270, 509).addBox(-6.5F, -5F, -6.5F, 13F, 5F, 13F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        p_hombro_der.addOrReplaceChild("hombro_der_0", CubeListBuilder.create()
                .texOffs(470, 509).addBox(-4F, -9.2038F, -4F, 8F, 9.2038F, 8F, infla)
                .texOffs(882, 509).addBox(-5.5F, -5F, -5.5F, 11F, 5F, 11F, infla),
                PartPose.offsetAndRotation(6.159F, 1F, 0.2397F, 0.2257F, 0.1147F, 0.2408F));
        p_hombro_der.addOrReplaceChild("hombro_der_1", CubeListBuilder.create()
                .texOffs(672, 509).addBox(-3F, -10.0834F, -3F, 6F, 10.0834F, 6F, infla)
                .texOffs(304, 547).addBox(-4.5F, -5F, -4.5F, 9F, 5F, 9F, infla),
                PartPose.offsetAndRotation(-5.6968F, 1F, 3.7975F, 0.0134F, 0.1652F, -0.2239F));
        p_hombro_der.addOrReplaceChild("hombro_der_2", CubeListBuilder.create()
                .texOffs(620, 509).addBox(-3F, -11.9245F, -3F, 6F, 11.9245F, 6F, infla)
                .texOffs(342, 547).addBox(-4.5F, -5F, -4.5F, 9F, 5F, 9F, infla),
                PartPose.offsetAndRotation(5.404F, 1F, 2.0712F, -0.1581F, 0.0731F, 0.2372F));
        PartDefinition p_cuello = p_cuerpo.addOrReplaceChild("cuello", CubeListBuilder.create()
                .texOffs(0, 130).addBox(-20F, -22F, -42F, 40F, 42F, 44F, infla)
                .texOffs(464, 288).addBox(-21F, 12F, -40F, 42F, 8F, 38F, infla)
                .texOffs(735, 529).addBox(-22F, -24F, -12F, 44F, 5F, 9F, infla)
                .texOffs(174, 563).addBox(-22F, -24F, -30F, 44F, 5F, 7F, infla),
                PartPose.offsetAndRotation(0F, -16F, -112F, 0.4189F, 0F, 0F));
        PartDefinition p_cabeza = p_cuello.addOrReplaceChild("cabeza", CubeListBuilder.create()
                .texOffs(752, 130).addBox(-22F, -22F, -36F, 44F, 32F, 36F, infla)
                .texOffs(682, 342).addBox(-20F, -27F, -34F, 40F, 8F, 28F, infla)
                .texOffs(314, 342).addBox(-27F, -10F, -28F, 54F, 18F, 20F, infla)
                .texOffs(242, 288).addBox(-13F, -14F, -60F, 26F, 20F, 28F, infla)
                .texOffs(288, 422).addBox(-14F, 4F, -58F, 28F, 6F, 24F, infla)
                .texOffs(278, 563).addBox(-7F, -16F, -62F, 14F, 7F, 5F, infla)
                .texOffs(712, 483).addBox(-12F, -34F, -39.5F, 24F, 16F, 3F, infla)
                .texOffs(463, 529).addBox(-23F, -30F, -37F, 11F, 6F, 9F, infla)
                .texOffs(505, 529).addBox(12F, -30F, -37F, 11F, 6F, 9F, infla)
                .texOffs(862, 422).addBox(-5F, -18F, -56F, 10F, 4F, 22F, infla)
                .texOffs(964, 384).addBox(-30F, -12F, -28F, 3F, 16F, 16F, infla)
                .texOffs(0, 422).addBox(27F, -12F, -28F, 3F, 16F, 16F, infla)
                .texOffs(302, 483).addBox(-9F, -38F, -31F, 18F, 8F, 14F, infla)
                .texOffs(118, 422).addBox(-11F, 10F, -54F, 22F, 0.8F, 30F, infla)
                .texOffs(74, 592).addBox(-6.5F, 9.5F, -58.5F, 2.6F, 3.5F, 2.6F, infla)
                .texOffs(87, 592).addBox(-3F, 9.5F, -58.5F, 2.6F, 3.5F, 2.6F, infla)
                .texOffs(100, 592).addBox(0.4F, 9.5F, -58.5F, 2.6F, 3.5F, 2.6F, infla)
                .texOffs(113, 592).addBox(3.9F, 9.5F, -58.5F, 2.6F, 3.5F, 2.6F, infla),
                PartPose.offsetAndRotation(0F, 2F, -38F, -0.3142F, 0F, 0F));
        p_cabeza.addOrReplaceChild("ojo_izq", CubeListBuilder.create()
                .texOffs(126, 592).addBox(-6F, -2F, -1F, 12F, 4F, 2F, infla),
                PartPose.offsetAndRotation(13F, -12F, -36.6F, 0F, 0F, -0.2793F));
        p_cabeza.addOrReplaceChild("ojo_der", CubeListBuilder.create()
                .texOffs(156, 592).addBox(-6F, -2F, -1F, 12F, 4F, 2F, infla),
                PartPose.offsetAndRotation(-13F, -12F, -36.6F, 0F, 0F, 0.2793F));
        p_cabeza.addOrReplaceChild("ceno", CubeListBuilder.create()
                .texOffs(740, 578).addBox(-20F, -2F, -2F, 40F, 4F, 4F, infla),
                PartPose.offsetAndRotation(0F, -17F, -37F, 0F, 0F, 0F));
        p_cabeza.addOrReplaceChild("oreja_izq", CubeListBuilder.create()
                .texOffs(912, 547).addBox(-5F, -8F, -3F, 10F, 8F, 5F, infla)
                .texOffs(286, 578).addBox(-6F, -3F, -4F, 12F, 2F, 7F, infla),
                PartPose.offsetAndRotation(16F, -22F, -6F, -0.5236F, 0F, -0.1745F));
        p_cabeza.addOrReplaceChild("oreja_der", CubeListBuilder.create()
                .texOffs(944, 547).addBox(-5F, -8F, -3F, 10F, 8F, 5F, infla)
                .texOffs(326, 578).addBox(-6F, -3F, -4F, 12F, 2F, 7F, infla),
                PartPose.offsetAndRotation(-16F, -22F, -6F, -0.5236F, 0F, 0.1745F));
        PartDefinition p_sable_izq = p_cabeza.addOrReplaceChild("sable_izq", CubeListBuilder.create()
                .texOffs(610, 384).addBox(-2.5F, 0F, -3.5F, 5F, 28F, 6F, infla),
                PartPose.offsetAndRotation(8F, 6F, -50F, -0.1396F, 0F, 0.0524F));
        p_sable_izq.addOrReplaceChild("sable_punta_izq", CubeListBuilder.create()
                .texOffs(699, 529).addBox(-1.8F, 0F, -2.5F, 3.6F, 11F, 4F, infla),
                PartPose.offsetAndRotation(0F, 28F, 0F, 0.3142F, 0F, 0F));
        PartDefinition p_sable_der = p_cabeza.addOrReplaceChild("sable_der", CubeListBuilder.create()
                .texOffs(634, 384).addBox(-2.5F, 0F, -3.5F, 5F, 28F, 6F, infla),
                PartPose.offsetAndRotation(-8F, 6F, -50F, -0.1396F, 0F, -0.0524F));
        p_sable_der.addOrReplaceChild("sable_punta_der", CubeListBuilder.create()
                .texOffs(717, 529).addBox(-1.8F, 0F, -2.5F, 3.6F, 11F, 4F, infla),
                PartPose.offsetAndRotation(0F, 28F, 0F, 0.3142F, 0F, 0F));
        p_cabeza.addOrReplaceChild("mandibula", CubeListBuilder.create()
                .texOffs(456, 218).addBox(-14F, 0F, -48F, 28F, 10F, 48F, infla)
                .texOffs(0, 342).addBox(-11F, -2F, -44F, 22F, 2F, 38F, infla)
                .texOffs(138, 563).addBox(-11.5F, -9F, -46.5F, 4F, 9F, 4F, infla)
                .texOffs(156, 563).addBox(7.5F, -9F, -46.5F, 4F, 9F, 4F, infla)
                .texOffs(186, 592).addBox(-11.5F, -3.5F, -39F, 2.4F, 3.5F, 2.4F, infla)
                .texOffs(198, 592).addBox(-11.5F, -3.5F, -33F, 2.4F, 3.5F, 2.4F, infla)
                .texOffs(210, 592).addBox(-11.5F, -3.5F, -27F, 2.4F, 3.5F, 2.4F, infla)
                .texOffs(222, 592).addBox(-11.5F, -3.5F, -21F, 2.4F, 3.5F, 2.4F, infla)
                .texOffs(234, 592).addBox(9.1F, -3.5F, -39F, 2.4F, 3.5F, 2.4F, infla)
                .texOffs(246, 592).addBox(9.1F, -3.5F, -33F, 2.4F, 3.5F, 2.4F, infla)
                .texOffs(258, 592).addBox(9.1F, -3.5F, -27F, 2.4F, 3.5F, 2.4F, infla)
                .texOffs(270, 592).addBox(9.1F, -3.5F, -21F, 2.4F, 3.5F, 2.4F, infla)
                .texOffs(830, 578).addBox(-15F, 3F, -40F, 30F, 4F, 4F, infla),
                PartPose.offsetAndRotation(0F, 8F, -6F, 0.4189F, 0F, 0F));
        p_cabeza.addOrReplaceChild("corona_i", CubeListBuilder.create()
                .texOffs(0, 456).addBox(-3.5F, -18F, -3.5F, 7F, 18F, 7F, infla)
                .texOffs(547, 529).addBox(-5F, -5F, -5F, 10F, 5F, 10F, infla),
                PartPose.offsetAndRotation(10F, -30F, -18F, -0.8378F, 0F, -0.2793F));
        p_cabeza.addOrReplaceChild("corona_d", CubeListBuilder.create()
                .texOffs(30, 456).addBox(-3.5F, -18F, -3.5F, 7F, 18F, 7F, infla)
                .texOffs(589, 529).addBox(-5F, -5F, -5F, 10F, 5F, 10F, infla),
                PartPose.offsetAndRotation(-10F, -30F, -18F, -0.8378F, 0F, 0.2793F));
        PartDefinition p_corona_c = p_cabeza.addOrReplaceChild("corona_c", CubeListBuilder.create()
                .texOffs(800, 456).addBox(-9F, -3F, -9F, 18F, 6F, 18F, infla),
                PartPose.offsetAndRotation(0F, -34F, -10F, -0.9774F, 0F, 0F));
        p_corona_c.addOrReplaceChild("corona_c_a", CubeListBuilder.create()
                .texOffs(222, 384).addBox(-5F, -25.5F, -5F, 10F, 25.5F, 10F, infla)
                .texOffs(324, 509).addBox(-6.5F, -5F, -6.5F, 13F, 5F, 13F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        p_corona_c.addOrReplaceChild("corona_c_0", CubeListBuilder.create()
                .texOffs(618, 483).addBox(-4F, -11.7828F, -4F, 8F, 11.7828F, 8F, infla)
                .texOffs(928, 509).addBox(-5.5F, -5F, -5.5F, 11F, 5F, 11F, infla),
                PartPose.offsetAndRotation(6.8957F, 1F, -1.0518F, -0.1983F, 0.0578F, 0.4317F));
        p_corona_c.addOrReplaceChild("corona_c_1", CubeListBuilder.create()
                .texOffs(516, 483).addBox(-3F, -14.1408F, -3F, 6F, 14.1408F, 6F, infla)
                .texOffs(380, 547).addBox(-4.5F, -5F, -4.5F, 9F, 5F, 9F, infla),
                PartPose.offsetAndRotation(-5.4294F, 1F, -4.1405F, -0.2F, -0.0527F, -0.4115F));
        p_corona_c.addOrReplaceChild("corona_c_2", CubeListBuilder.create()
                .texOffs(420, 483).addBox(-3F, -15.4749F, -3F, 6F, 15.4749F, 6F, infla)
                .texOffs(418, 547).addBox(-4.5F, -5F, -4.5F, 9F, 5F, 9F, infla),
                PartPose.offsetAndRotation(5.2476F, 1F, -2.7676F, 0.0377F, -0.0721F, 0.448F));
        PartDefinition p_cresta_cuello = p_cuello.addOrReplaceChild("cresta_cuello", CubeListBuilder.create()
                .texOffs(874, 456).addBox(-9F, -3F, -9F, 18F, 6F, 18F, infla),
                PartPose.offsetAndRotation(0F, -22F, -24F, -0.5236F, 0F, 0F));
        p_cresta_cuello.addOrReplaceChild("cresta_cuello_a", CubeListBuilder.create()
                .texOffs(794, 422).addBox(-5F, -16.5F, -5F, 10F, 16.5F, 10F, infla)
                .texOffs(378, 509).addBox(-6.5F, -5F, -6.5F, 13F, 5F, 13F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        p_cresta_cuello.addOrReplaceChild("cresta_cuello_0", CubeListBuilder.create()
                .texOffs(538, 509).addBox(-3.5F, -10.8366F, -3.5F, 7F, 10.8366F, 7F, infla)
                .texOffs(631, 529).addBox(-5F, -5F, -5F, 10F, 5F, 10F, infla),
                PartPose.offsetAndRotation(6.222F, 1F, 1.2188F, -0.2207F, -0.0864F, 0.2422F));
        p_cresta_cuello.addOrReplaceChild("cresta_cuello_1", CubeListBuilder.create()
                .texOffs(143, 529).addBox(-3F, -9.5797F, -3F, 6F, 9.5797F, 6F, infla)
                .texOffs(456, 547).addBox(-4.5F, -5F, -4.5F, 9F, 5F, 9F, infla),
                PartPose.offsetAndRotation(-5.1626F, 1F, -4.9239F, -0.2317F, 0.349F, -0.4314F));
        p_cresta_cuello.addOrReplaceChild("cresta_cuello_2", CubeListBuilder.create()
                .texOffs(504, 509).addBox(-4F, -9.0823F, -4F, 8F, 9.0823F, 8F, infla)
                .texOffs(974, 509).addBox(-5.5F, -5F, -5.5F, 11F, 5F, 11F, infla),
                PartPose.offsetAndRotation(6.6322F, 1F, 0.3082F, -0.0741F, 0.2667F, 0.3075F));
        PartDefinition p_brazo_izq = p_cuerpo.addOrReplaceChild("brazo_izq", CubeListBuilder.create()
                .texOffs(170, 130).addBox(-12F, -10F, -16F, 24F, 46F, 32F, infla)
                .texOffs(894, 218).addBox(-8F, -14F, -12F, 9F, 26F, 26F, infla),
                PartPose.offsetAndRotation(22F, 6F, -92F, 0.3491F, 0F, 0F));
        PartDefinition p_antebrazo_izq = p_brazo_izq.addOrReplaceChild("antebrazo_izq", CubeListBuilder.create()
                .texOffs(78, 218).addBox(-10F, 0F, -10F, 20F, 46F, 20F, infla)
                .texOffs(458, 422).addBox(-11F, 28F, -11F, 22F, 6F, 22F, infla)
                .texOffs(726, 384).addBox(-9F, 4F, 8F, 18F, 30F, 3F, infla)
                .texOffs(40, 422).addBox(10F, 7F, -8F, 2.5F, 16F, 16F, infla),
                PartPose.offsetAndRotation(0F, 34F, -1F, -0.3491F, 0F, 0F));
        p_antebrazo_izq.addOrReplaceChild("mano_izq", CubeListBuilder.create()
                .texOffs(820, 342).addBox(-13F, 0F, -16F, 26F, 10F, 26F, infla)
                .texOffs(537, 563).addBox(-12.48F, 2F, -19F, 5.46F, 6F, 6F, infla)
                .texOffs(436, 578).addBox(-10.95F, 5F, -24F, 2.4F, 3F, 6F, infla)
                .texOffs(562, 563).addBox(-5.98F, 2F, -19F, 5.46F, 6F, 6F, infla)
                .texOffs(455, 578).addBox(-4.45F, 5F, -24F, 2.4F, 3F, 6F, infla)
                .texOffs(587, 563).addBox(0.52F, 2F, -19F, 5.46F, 6F, 6F, infla)
                .texOffs(474, 578).addBox(2.05F, 5F, -24F, 2.4F, 3F, 6F, infla)
                .texOffs(612, 563).addBox(7.02F, 2F, -19F, 5.46F, 6F, 6F, infla)
                .texOffs(493, 578).addBox(8.55F, 5F, -24F, 2.4F, 3F, 6F, infla),
                PartPose.offsetAndRotation(0F, 46F, -2F, 0F, 0F, 0F));
        PartDefinition p_brazo_der = p_cuerpo.addOrReplaceChild("brazo_der", CubeListBuilder.create()
                .texOffs(284, 130).addBox(-12F, -10F, -16F, 24F, 46F, 32F, infla)
                .texOffs(0, 288).addBox(-18F, -14F, -12F, 9F, 26F, 26F, infla),
                PartPose.offsetAndRotation(-22F, 6F, -92F, 0.3491F, 0F, 0F));
        PartDefinition p_antebrazo_der = p_brazo_der.addOrReplaceChild("antebrazo_der", CubeListBuilder.create()
                .texOffs(160, 218).addBox(-10F, 0F, -10F, 20F, 46F, 20F, infla)
                .texOffs(548, 422).addBox(-11F, 28F, -11F, 22F, 6F, 22F, infla)
                .texOffs(770, 384).addBox(-9F, 4F, 8F, 18F, 30F, 3F, infla)
                .texOffs(79, 422).addBox(-12.5F, 7F, -8F, 2.5F, 16F, 16F, infla),
                PartPose.offsetAndRotation(0F, 34F, -1F, -0.3491F, 0F, 0F));
        p_antebrazo_der.addOrReplaceChild("mano_der", CubeListBuilder.create()
                .texOffs(0, 384).addBox(-13F, 0F, -16F, 26F, 10F, 26F, infla)
                .texOffs(637, 563).addBox(-12.48F, 2F, -19F, 5.46F, 6F, 6F, infla)
                .texOffs(512, 578).addBox(-10.95F, 5F, -24F, 2.4F, 3F, 6F, infla)
                .texOffs(662, 563).addBox(-5.98F, 2F, -19F, 5.46F, 6F, 6F, infla)
                .texOffs(531, 578).addBox(-4.45F, 5F, -24F, 2.4F, 3F, 6F, infla)
                .texOffs(687, 563).addBox(0.52F, 2F, -19F, 5.46F, 6F, 6F, infla)
                .texOffs(550, 578).addBox(2.05F, 5F, -24F, 2.4F, 3F, 6F, infla)
                .texOffs(712, 563).addBox(7.02F, 2F, -19F, 5.46F, 6F, 6F, infla)
                .texOffs(569, 578).addBox(8.55F, 5F, -24F, 2.4F, 3F, 6F, infla),
                PartPose.offsetAndRotation(0F, 46F, -2F, 0F, 0F, 0F));
        PartDefinition p_muslo_izq = p_cuerpo.addOrReplaceChild("muslo_izq", CubeListBuilder.create()
                .texOffs(642, 0).addBox(-14F, -14F, -18F, 28F, 52F, 36F, infla)
                .texOffs(352, 288).addBox(14F, -6F, -12F, 3F, 24F, 24F, infla),
                PartPose.offsetAndRotation(22F, 2F, 46F, -0.5236F, 0F, 0F));
        PartDefinition p_tibia_izq = p_muslo_izq.addOrReplaceChild("tibia_izq", CubeListBuilder.create()
                .texOffs(738, 218).addBox(-9F, 0F, -10F, 18F, 34F, 20F, infla),
                PartPose.offsetAndRotation(0F, 36F, 2F, 1.1345F, 0F, 0F));
        PartDefinition p_tarso_izq = p_tibia_izq.addOrReplaceChild("tarso_izq", CubeListBuilder.create()
                .texOffs(626, 288).addBox(-7F, 0F, -8F, 14F, 28F, 16F, infla)
                .texOffs(42, 483).addBox(-8F, 8F, -9F, 16F, 5F, 18F, infla),
                PartPose.offsetAndRotation(0F, 32F, 0F, -0.7854F, 0F, 0F));
        p_tarso_izq.addOrReplaceChild("pie_izq", CubeListBuilder.create()
                .texOffs(264, 384).addBox(-12F, 0F, -18F, 24F, 9F, 26F, infla)
                .texOffs(737, 563).addBox(-11.52F, 1F, -21F, 5.04F, 6F, 6F, infla)
                .texOffs(588, 578).addBox(-10.2F, 4F, -26F, 2.4F, 3F, 6F, infla)
                .texOffs(762, 563).addBox(-5.52F, 1F, -21F, 5.04F, 6F, 6F, infla)
                .texOffs(607, 578).addBox(-4.2F, 4F, -26F, 2.4F, 3F, 6F, infla)
                .texOffs(787, 563).addBox(0.48F, 1F, -21F, 5.04F, 6F, 6F, infla)
                .texOffs(626, 578).addBox(1.8F, 4F, -26F, 2.4F, 3F, 6F, infla)
                .texOffs(812, 563).addBox(6.48F, 1F, -21F, 5.04F, 6F, 6F, infla)
                .texOffs(645, 578).addBox(7.8F, 4F, -26F, 2.4F, 3F, 6F, infla),
                PartPose.offsetAndRotation(0F, 26F, 0F, 0.1745F, 0F, 0F));
        PartDefinition p_muslo_der = p_cuerpo.addOrReplaceChild("muslo_der", CubeListBuilder.create()
                .texOffs(772, 0).addBox(-14F, -14F, -18F, 28F, 52F, 36F, infla)
                .texOffs(408, 288).addBox(-17F, -6F, -12F, 3F, 24F, 24F, infla),
                PartPose.offsetAndRotation(-22F, 2F, 46F, -0.5236F, 0F, 0F));
        PartDefinition p_tibia_der = p_muslo_der.addOrReplaceChild("tibia_der", CubeListBuilder.create()
                .texOffs(816, 218).addBox(-9F, 0F, -10F, 18F, 34F, 20F, infla),
                PartPose.offsetAndRotation(0F, 36F, 2F, 1.1345F, 0F, 0F));
        PartDefinition p_tarso_der = p_tibia_der.addOrReplaceChild("tarso_der", CubeListBuilder.create()
                .texOffs(688, 288).addBox(-7F, 0F, -8F, 14F, 28F, 16F, infla)
                .texOffs(112, 483).addBox(-8F, 8F, -9F, 16F, 5F, 18F, infla),
                PartPose.offsetAndRotation(0F, 32F, 0F, -0.7854F, 0F, 0F));
        p_tarso_der.addOrReplaceChild("pie_der", CubeListBuilder.create()
                .texOffs(366, 384).addBox(-12F, 0F, -18F, 24F, 9F, 26F, infla)
                .texOffs(837, 563).addBox(-11.52F, 1F, -21F, 5.04F, 6F, 6F, infla)
                .texOffs(664, 578).addBox(-10.2F, 4F, -26F, 2.4F, 3F, 6F, infla)
                .texOffs(862, 563).addBox(-5.52F, 1F, -21F, 5.04F, 6F, 6F, infla)
                .texOffs(683, 578).addBox(-4.2F, 4F, -26F, 2.4F, 3F, 6F, infla)
                .texOffs(887, 563).addBox(0.48F, 1F, -21F, 5.04F, 6F, 6F, infla)
                .texOffs(702, 578).addBox(1.8F, 4F, -26F, 2.4F, 3F, 6F, infla)
                .texOffs(912, 563).addBox(6.48F, 1F, -21F, 5.04F, 6F, 6F, infla)
                .texOffs(721, 578).addBox(7.8F, 4F, -26F, 2.4F, 3F, 6F, infla),
                PartPose.offsetAndRotation(0F, 26F, 0F, 0.1745F, 0F, 0F));
        PartDefinition p_cola_base = p_cuerpo.addOrReplaceChild("cola_base", CubeListBuilder.create(),
                PartPose.offsetAndRotation(0F, -20F, 62F, -0.2443F, 0F, 0F));
        PartDefinition p_cola0 = p_cola_base.addOrReplaceChild("cola0", CubeListBuilder.create()
                .texOffs(606, 342).addBox(-7F, -7F, 0F, 14F, 14F, 23F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0F, -0.1047F, 0F, 0F));
        PartDefinition p_cola1 = p_cola0.addOrReplaceChild("cola1", CubeListBuilder.create()
                .texOffs(106, 384).addBox(-6.5F, -6.5F, 0F, 13F, 13F, 23F, infla)
                .texOffs(446, 483).addBox(-8F, -8F, 8F, 16F, 16F, 5F, infla),
                PartPose.offsetAndRotation(0F, 0F, 22F, 0.2443F, 0F, 0F));
        PartDefinition p_cola2 = p_cola1.addOrReplaceChild("cola2", CubeListBuilder.create()
                .texOffs(468, 384).addBox(-6F, -6F, 0F, 12F, 12F, 23F, infla),
                PartPose.offsetAndRotation(0F, 0F, 22F, 0.2094F, 0F, 0F));
        PartDefinition p_cola3 = p_cola2.addOrReplaceChild("cola3", CubeListBuilder.create()
                .texOffs(540, 384).addBox(-5.5F, -5.5F, 0F, 11F, 11F, 23F, infla),
                PartPose.offsetAndRotation(0F, 0F, 22F, 0.1396F, 0F, 0F));
        PartDefinition p_cola4 = p_cola3.addOrReplaceChild("cola4", CubeListBuilder.create()
                .texOffs(658, 384).addBox(-5F, -5F, 0F, 10F, 10F, 23F, infla)
                .texOffs(432, 509).addBox(-6.5F, -6.5F, 8F, 13F, 13F, 5F, infla),
                PartPose.offsetAndRotation(0F, 0F, 22F, 0.0349F, 0F, 0F));
        PartDefinition p_cola5 = p_cola4.addOrReplaceChild("cola5", CubeListBuilder.create()
                .texOffs(856, 384).addBox(-4.5F, -4.5F, 0F, 9F, 9F, 23F, infla),
                PartPose.offsetAndRotation(0F, 0F, 22F, -0.1745F, 0F, 0F));
        PartDefinition p_cola6 = p_cola5.addOrReplaceChild("cola6", CubeListBuilder.create()
                .texOffs(224, 422).addBox(-4F, -4F, 0F, 8F, 8F, 23F, infla),
                PartPose.offsetAndRotation(0F, 0F, 22F, -0.2793F, 0F, 0F));
        p_cola6.addOrReplaceChild("punta_cola", CubeListBuilder.create()
                .texOffs(948, 456).addBox(-6F, -6F, 0F, 12F, 12F, 12F, infla)
                .texOffs(60, 529).addBox(-3.5F, -13F, 2F, 7F, 9F, 7F, infla)
                .texOffs(0, 578).addBox(-2.5F, -17F, 7F, 5F, 7F, 5F, infla),
                PartPose.offsetAndRotation(0F, 0F, 22F, 0F, 0F, 0F));
        return LayerDefinition.create(malla, 1024, 1024);
    }
}
