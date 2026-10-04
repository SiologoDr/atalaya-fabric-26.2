package com.atalaya.client;

import net.minecraft.client.model.geom.PartPose;
import net.minecraft.client.model.geom.builders.CubeListBuilder;
import net.minecraft.client.model.geom.builders.LayerDefinition;
import net.minecraft.client.model.geom.builders.MeshDefinition;
import net.minecraft.client.model.geom.builders.PartDefinition;

/**
 * La malla de Aeralis, la Mariposa del Vendaval. GENERADO por
 * materiales/generadores/vendaval_juego.py: no se edita a mano. Cambiar una
 * caja aqui sin cambiar el script descuadra la textura, que se pinta con la
 * misma cuadricula (a media resolucion: el atlas se declara de 1024 y el PNG
 * mide la mitad).
 */
public final class AeralisMalla {

    private AeralisMalla() {
    }

    public static LayerDefinition crear() {
        MeshDefinition malla = new MeshDefinition();
        PartDefinition p_root = malla.getRoot();
        PartDefinition p_cuerpo = p_root.addOrReplaceChild("cuerpo", CubeListBuilder.create(),
                PartPose.offsetAndRotation(0F, -82F, 0F, 0F, 0F, 0F));
        PartDefinition p_torax = p_cuerpo.addOrReplaceChild("torax", CubeListBuilder.create()
                .texOffs(462, 148).addBox(-21F, -24F, -16F, 42F, 48F, 32F)
                .texOffs(626, 148).addBox(-24F, -29F, -19F, 48F, 17F, 38F)
                .texOffs(228, 282).addBox(-28F, -26F, -8F, 8F, 14F, 24F)
                .texOffs(228, 282).addBox(20F, -26F, -8F, 8F, 14F, 24F)
                .texOffs(524, 282).addBox(-15F, -9F, -17.2F, 30F, 30F, 1.2F)
                .texOffs(294, 282).addBox(-19F, 22F, -15F, 38F, 4F, 30F),
                PartPose.offsetAndRotation(0F, 0F, 0F, -0.1396F, 0F, 0F));
        p_torax.addOrReplaceChild("nucleo", CubeListBuilder.create()
                .texOffs(774, 282).addBox(-13F, -13F, -0.6F, 26F, 26F, 0.6F),
                PartPose.offsetAndRotation(0F, 8F, -17.6F, 0F, 0F, 0F));
        PartDefinition p_cabeza = p_torax.addOrReplaceChild("cabeza", CubeListBuilder.create()
                .texOffs(800, 148).addBox(-16F, -26F, -14F, 32F, 26F, 27F)
                .texOffs(608, 282).addBox(-18F, -31F, -7F, 36F, 9F, 22F)
                .texOffs(0, 332).addBox(-5F, -7F, -15F, 10F, 7F, 1.2F),
                PartPose.offsetAndRotation(0F, -27F, -5F, 0.2094F, 0F, 0F));
        p_cabeza.addOrReplaceChild("ojo_izq", CubeListBuilder.create()
                .texOffs(726, 282).addBox(-5F, -8F, -4F, 10F, 15F, 13F),
                PartPose.offsetAndRotation(12F, -14F, -12F, 0F, 0F, -0.3142F));
        p_cabeza.addOrReplaceChild("ceno_izq", CubeListBuilder.create()
                .texOffs(970, 282).addBox(-7F, -2.5F, -1F, 15F, 4F, 5F),
                PartPose.offsetAndRotation(8F, -21F, -16.5F, 0F, 0F, -0.3491F));
        PartDefinition p_colmillo_izq = p_cabeza.addOrReplaceChild("colmillo_izq", CubeListBuilder.create()
                .texOffs(928, 282).addBox(-1.6F, 0F, -1.6F, 3.2F, 10F, 3.2F),
                PartPose.offsetAndRotation(5F, -3F, -14F, -0.2094F, 0F, -0.2793F));
        p_colmillo_izq.addOrReplaceChild("colmillo_punta_izq", CubeListBuilder.create()
                .texOffs(944, 282).addBox(-1.1F, 0F, -1.1F, 2.2F, 8F, 2.2F),
                PartPose.offsetAndRotation(0F, 10F, 0F, -0.5236F, 0F, 0.5934F));
        PartDefinition p_antena_izq = p_cabeza.addOrReplaceChild("antena_izq", CubeListBuilder.create()
                .texOffs(612, 148).addBox(-1.4F, -64F, -1.4F, 2.8F, 64F, 2.8F)
                .texOffs(168, 332).addBox(0.8F, -8F, -0.6F, 5.5F, 1.4F, 1.2F)
                .texOffs(168, 332).addBox(-6.3F, -8F, -0.6F, 5.5F, 1.4F, 1.2F)
                .texOffs(150, 332).addBox(0.8F, -12.4F, -0.6F, 6.4F, 1.4F, 1.2F)
                .texOffs(150, 332).addBox(-7.2F, -12.4F, -0.6F, 6.4F, 1.4F, 1.2F)
                .texOffs(130, 332).addBox(0.8F, -16.8F, -0.6F, 7.3F, 1.4F, 1.2F)
                .texOffs(130, 332).addBox(-8.1F, -16.8F, -0.6F, 7.3F, 1.4F, 1.2F)
                .texOffs(108, 332).addBox(0.8F, -21.2F, -0.6F, 8.2F, 1.4F, 1.2F)
                .texOffs(108, 332).addBox(-9F, -21.2F, -0.6F, 8.2F, 1.4F, 1.2F)
                .texOffs(84, 332).addBox(0.8F, -25.6F, -0.6F, 9.1F, 1.4F, 1.2F)
                .texOffs(84, 332).addBox(-9.9F, -25.6F, -0.6F, 9.1F, 1.4F, 1.2F)
                .texOffs(58, 332).addBox(0.8F, -30F, -0.6F, 10F, 1.4F, 1.2F)
                .texOffs(58, 332).addBox(-10.8F, -30F, -0.6F, 10F, 1.4F, 1.2F)
                .texOffs(84, 332).addBox(0.8F, -34.4F, -0.6F, 9.1F, 1.4F, 1.2F)
                .texOffs(84, 332).addBox(-9.9F, -34.4F, -0.6F, 9.1F, 1.4F, 1.2F)
                .texOffs(108, 332).addBox(0.8F, -38.8F, -0.6F, 8.2F, 1.4F, 1.2F)
                .texOffs(108, 332).addBox(-9F, -38.8F, -0.6F, 8.2F, 1.4F, 1.2F)
                .texOffs(130, 332).addBox(0.8F, -43.2F, -0.6F, 7.3F, 1.4F, 1.2F)
                .texOffs(130, 332).addBox(-8.1F, -43.2F, -0.6F, 7.3F, 1.4F, 1.2F)
                .texOffs(150, 332).addBox(0.8F, -47.6F, -0.6F, 6.4F, 1.4F, 1.2F)
                .texOffs(150, 332).addBox(-7.2F, -47.6F, -0.6F, 6.4F, 1.4F, 1.2F)
                .texOffs(168, 332).addBox(0.8F, -52F, -0.6F, 5.5F, 1.4F, 1.2F)
                .texOffs(168, 332).addBox(-6.3F, -52F, -0.6F, 5.5F, 1.4F, 1.2F)
                .texOffs(184, 332).addBox(0.8F, -56.4F, -0.6F, 4.6F, 1.4F, 1.2F)
                .texOffs(184, 332).addBox(-5.4F, -56.4F, -0.6F, 4.6F, 1.4F, 1.2F)
                .texOffs(198, 332).addBox(0.8F, -60.8F, -0.6F, 3.7F, 1.4F, 1.2F)
                .texOffs(198, 332).addBox(-4.5F, -60.8F, -0.6F, 3.7F, 1.4F, 1.2F),
                PartPose.offsetAndRotation(8F, -24F, -6F, -0.5236F, 0F, 0.4189F));
        p_antena_izq.addOrReplaceChild("antena_punta_izq", CubeListBuilder.create()
                .texOffs(890, 282).addBox(-1F, -14F, -1F, 2F, 14F, 2F)
                .texOffs(44, 332).addBox(-1.5F, -17F, -1.5F, 3F, 3F, 3F),
                PartPose.offsetAndRotation(0F, -64F, 0F, -0.8029F, 0F, -0.2094F));
        p_cabeza.addOrReplaceChild("ojo_der", CubeListBuilder.create()
                .texOffs(726, 282).addBox(-5F, -8F, -4F, 10F, 15F, 13F),
                PartPose.offsetAndRotation(-12F, -14F, -12F, 0F, 0F, 0.3142F));
        p_cabeza.addOrReplaceChild("ceno_der", CubeListBuilder.create()
                .texOffs(970, 282).addBox(-8F, -2.5F, -1F, 15F, 4F, 5F),
                PartPose.offsetAndRotation(-8F, -21F, -16.5F, 0F, 0F, 0.3491F));
        PartDefinition p_colmillo_der = p_cabeza.addOrReplaceChild("colmillo_der", CubeListBuilder.create()
                .texOffs(928, 282).addBox(-1.6F, 0F, -1.6F, 3.2F, 10F, 3.2F),
                PartPose.offsetAndRotation(-5F, -3F, -14F, -0.2094F, 0F, 0.2793F));
        p_colmillo_der.addOrReplaceChild("colmillo_punta_der", CubeListBuilder.create()
                .texOffs(944, 282).addBox(-1.1F, 0F, -1.1F, 2.2F, 8F, 2.2F),
                PartPose.offsetAndRotation(0F, 10F, 0F, -0.5236F, 0F, -0.5934F));
        PartDefinition p_antena_der = p_cabeza.addOrReplaceChild("antena_der", CubeListBuilder.create()
                .texOffs(612, 148).addBox(-1.4F, -64F, -1.4F, 2.8F, 64F, 2.8F)
                .texOffs(168, 332).addBox(0.8F, -8F, -0.6F, 5.5F, 1.4F, 1.2F)
                .texOffs(168, 332).addBox(-6.3F, -8F, -0.6F, 5.5F, 1.4F, 1.2F)
                .texOffs(150, 332).addBox(0.8F, -12.4F, -0.6F, 6.4F, 1.4F, 1.2F)
                .texOffs(150, 332).addBox(-7.2F, -12.4F, -0.6F, 6.4F, 1.4F, 1.2F)
                .texOffs(130, 332).addBox(0.8F, -16.8F, -0.6F, 7.3F, 1.4F, 1.2F)
                .texOffs(130, 332).addBox(-8.1F, -16.8F, -0.6F, 7.3F, 1.4F, 1.2F)
                .texOffs(108, 332).addBox(0.8F, -21.2F, -0.6F, 8.2F, 1.4F, 1.2F)
                .texOffs(108, 332).addBox(-9F, -21.2F, -0.6F, 8.2F, 1.4F, 1.2F)
                .texOffs(84, 332).addBox(0.8F, -25.6F, -0.6F, 9.1F, 1.4F, 1.2F)
                .texOffs(84, 332).addBox(-9.9F, -25.6F, -0.6F, 9.1F, 1.4F, 1.2F)
                .texOffs(58, 332).addBox(0.8F, -30F, -0.6F, 10F, 1.4F, 1.2F)
                .texOffs(58, 332).addBox(-10.8F, -30F, -0.6F, 10F, 1.4F, 1.2F)
                .texOffs(84, 332).addBox(0.8F, -34.4F, -0.6F, 9.1F, 1.4F, 1.2F)
                .texOffs(84, 332).addBox(-9.9F, -34.4F, -0.6F, 9.1F, 1.4F, 1.2F)
                .texOffs(108, 332).addBox(0.8F, -38.8F, -0.6F, 8.2F, 1.4F, 1.2F)
                .texOffs(108, 332).addBox(-9F, -38.8F, -0.6F, 8.2F, 1.4F, 1.2F)
                .texOffs(130, 332).addBox(0.8F, -43.2F, -0.6F, 7.3F, 1.4F, 1.2F)
                .texOffs(130, 332).addBox(-8.1F, -43.2F, -0.6F, 7.3F, 1.4F, 1.2F)
                .texOffs(150, 332).addBox(0.8F, -47.6F, -0.6F, 6.4F, 1.4F, 1.2F)
                .texOffs(150, 332).addBox(-7.2F, -47.6F, -0.6F, 6.4F, 1.4F, 1.2F)
                .texOffs(168, 332).addBox(0.8F, -52F, -0.6F, 5.5F, 1.4F, 1.2F)
                .texOffs(168, 332).addBox(-6.3F, -52F, -0.6F, 5.5F, 1.4F, 1.2F)
                .texOffs(184, 332).addBox(0.8F, -56.4F, -0.6F, 4.6F, 1.4F, 1.2F)
                .texOffs(184, 332).addBox(-5.4F, -56.4F, -0.6F, 4.6F, 1.4F, 1.2F)
                .texOffs(198, 332).addBox(0.8F, -60.8F, -0.6F, 3.7F, 1.4F, 1.2F)
                .texOffs(198, 332).addBox(-4.5F, -60.8F, -0.6F, 3.7F, 1.4F, 1.2F),
                PartPose.offsetAndRotation(-8F, -24F, -6F, -0.5236F, 0F, -0.4189F));
        p_antena_der.addOrReplaceChild("antena_punta_der", CubeListBuilder.create()
                .texOffs(890, 282).addBox(-1F, -14F, -1F, 2F, 14F, 2F)
                .texOffs(44, 332).addBox(-1.5F, -17F, -1.5F, 3F, 3F, 3F),
                PartPose.offsetAndRotation(0F, -64F, 0F, -0.8029F, 0F, 0.2094F));
        p_torax.addOrReplaceChild("ala_sup_izq", CubeListBuilder.create()
                .texOffs(516, 0).addBox(0F, -55.44F, 0F, 200F, 132F, 0F),
                PartPose.offsetAndRotation(19F, -14F, 12F, 0F, -0.3142F, -0.2443F));
        p_torax.addOrReplaceChild("ala_inf_izq", CubeListBuilder.create()
                .texOffs(0, 0).addBox(0F, -11.68F, 0F, 128F, 146F, 0F),
                PartPose.offsetAndRotation(18F, 10F, 13F, 0F, -0.4538F, 0.1745F));
        p_torax.addOrReplaceChild("ala_sup_der", CubeListBuilder.create()
                .texOffs(0, 148).addBox(-200F, -55.44F, 0F, 200F, 132F, 0F),
                PartPose.offsetAndRotation(-19F, -14F, 12F, 0F, 0.3142F, 0.2443F));
        p_torax.addOrReplaceChild("ala_inf_der", CubeListBuilder.create()
                .texOffs(258, 0).addBox(-128F, -11.68F, 0F, 128F, 146F, 0F),
                PartPose.offsetAndRotation(-18F, 10F, 13F, 0F, 0.4538F, -0.1745F));
        PartDefinition p_pata0_izq = p_torax.addOrReplaceChild("pata0_izq", CubeListBuilder.create()
                .texOffs(590, 282).addBox(-2F, 0F, -2F, 4F, 28F, 4F),
                PartPose.offsetAndRotation(17F, -8F, -8F, -0.6632F, 0F, 0.5934F));
        PartDefinition p_pata0_izq_tibia = p_pata0_izq.addOrReplaceChild("pata0_izq_tibia", CubeListBuilder.create()
                .texOffs(510, 282).addBox(-1.5F, 0F, -1.5F, 3F, 30F, 3F)
                .texOffs(884, 282).addBox(-2.5F, 6F, -2F, 1F, 16F, 1F),
                PartPose.offsetAndRotation(0F, 28F, 0F, -1.2217F, 0F, 0F));
        p_pata0_izq_tibia.addOrReplaceChild("pata0_izq_garra", CubeListBuilder.create()
                .texOffs(956, 282).addBox(-2F, 0F, -0.75F, 4F, 8F, 1.5F),
                PartPose.offsetAndRotation(0F, 30F, 0F, 0.5934F, 0F, 0F));
        PartDefinition p_pata1_izq = p_torax.addOrReplaceChild("pata1_izq", CubeListBuilder.create()
                .texOffs(590, 282).addBox(-2F, 0F, -2F, 4F, 28F, 4F),
                PartPose.offsetAndRotation(17F, 5F, -4F, -0.1047F, 0F, 0.9076F));
        PartDefinition p_pata1_izq_tibia = p_pata1_izq.addOrReplaceChild("pata1_izq_tibia", CubeListBuilder.create()
                .texOffs(510, 282).addBox(-1.5F, 0F, -1.5F, 3F, 30F, 3F),
                PartPose.offsetAndRotation(0F, 28F, 0F, 0.8727F, 0F, 0F));
        p_pata1_izq_tibia.addOrReplaceChild("pata1_izq_garra", CubeListBuilder.create()
                .texOffs(956, 282).addBox(-2F, 0F, -0.75F, 4F, 8F, 1.5F),
                PartPose.offsetAndRotation(0F, 30F, 0F, 0.5934F, 0F, 0F));
        PartDefinition p_pata2_izq = p_torax.addOrReplaceChild("pata2_izq", CubeListBuilder.create()
                .texOffs(590, 282).addBox(-2F, 0F, -2F, 4F, 28F, 4F),
                PartPose.offsetAndRotation(17F, 18F, 0F, 0.5236F, 0F, 0.9076F));
        PartDefinition p_pata2_izq_tibia = p_pata2_izq.addOrReplaceChild("pata2_izq_tibia", CubeListBuilder.create()
                .texOffs(510, 282).addBox(-1.5F, 0F, -1.5F, 3F, 30F, 3F),
                PartPose.offsetAndRotation(0F, 28F, 0F, 0.8727F, 0F, 0F));
        p_pata2_izq_tibia.addOrReplaceChild("pata2_izq_garra", CubeListBuilder.create()
                .texOffs(956, 282).addBox(-2F, 0F, -0.75F, 4F, 8F, 1.5F),
                PartPose.offsetAndRotation(0F, 30F, 0F, 0.5934F, 0F, 0F));
        PartDefinition p_pata0_der = p_torax.addOrReplaceChild("pata0_der", CubeListBuilder.create()
                .texOffs(590, 282).addBox(-2F, 0F, -2F, 4F, 28F, 4F),
                PartPose.offsetAndRotation(-17F, -8F, -8F, -0.6632F, 0F, -0.5934F));
        PartDefinition p_pata0_der_tibia = p_pata0_der.addOrReplaceChild("pata0_der_tibia", CubeListBuilder.create()
                .texOffs(510, 282).addBox(-1.5F, 0F, -1.5F, 3F, 30F, 3F)
                .texOffs(884, 282).addBox(-2.5F, 6F, -2F, 1F, 16F, 1F),
                PartPose.offsetAndRotation(0F, 28F, 0F, -1.2217F, 0F, 0F));
        p_pata0_der_tibia.addOrReplaceChild("pata0_der_garra", CubeListBuilder.create()
                .texOffs(956, 282).addBox(-2F, 0F, -0.75F, 4F, 8F, 1.5F),
                PartPose.offsetAndRotation(0F, 30F, 0F, 0.5934F, 0F, 0F));
        PartDefinition p_pata1_der = p_torax.addOrReplaceChild("pata1_der", CubeListBuilder.create()
                .texOffs(590, 282).addBox(-2F, 0F, -2F, 4F, 28F, 4F),
                PartPose.offsetAndRotation(-17F, 5F, -4F, -0.1047F, 0F, -0.9076F));
        PartDefinition p_pata1_der_tibia = p_pata1_der.addOrReplaceChild("pata1_der_tibia", CubeListBuilder.create()
                .texOffs(510, 282).addBox(-1.5F, 0F, -1.5F, 3F, 30F, 3F),
                PartPose.offsetAndRotation(0F, 28F, 0F, 0.8727F, 0F, 0F));
        p_pata1_der_tibia.addOrReplaceChild("pata1_der_garra", CubeListBuilder.create()
                .texOffs(956, 282).addBox(-2F, 0F, -0.75F, 4F, 8F, 1.5F),
                PartPose.offsetAndRotation(0F, 30F, 0F, 0.5934F, 0F, 0F));
        PartDefinition p_pata2_der = p_torax.addOrReplaceChild("pata2_der", CubeListBuilder.create()
                .texOffs(590, 282).addBox(-2F, 0F, -2F, 4F, 28F, 4F),
                PartPose.offsetAndRotation(-17F, 18F, 0F, 0.5236F, 0F, -0.9076F));
        PartDefinition p_pata2_der_tibia = p_pata2_der.addOrReplaceChild("pata2_der_tibia", CubeListBuilder.create()
                .texOffs(510, 282).addBox(-1.5F, 0F, -1.5F, 3F, 30F, 3F),
                PartPose.offsetAndRotation(0F, 28F, 0F, 0.8727F, 0F, 0F));
        p_pata2_der_tibia.addOrReplaceChild("pata2_der_garra", CubeListBuilder.create()
                .texOffs(956, 282).addBox(-2F, 0F, -0.75F, 4F, 8F, 1.5F),
                PartPose.offsetAndRotation(0F, 30F, 0F, 0.5934F, 0F, 0F));
        PartDefinition p_abdomen = p_torax.addOrReplaceChild("abdomen", CubeListBuilder.create()
                .texOffs(0, 282).addBox(-17F, 0F, -14F, 34F, 20F, 28F),
                PartPose.offsetAndRotation(0F, 24F, 4F, 0.1745F, 0F, 0F));
        PartDefinition p_abdomen2 = p_abdomen.addOrReplaceChild("abdomen2", CubeListBuilder.create()
                .texOffs(126, 282).addBox(-14F, 0F, -11F, 28F, 18F, 22F),
                PartPose.offsetAndRotation(0F, 20F, 0F, 0.1396F, 0F, 0F));
        PartDefinition p_abdomen3 = p_abdomen2.addOrReplaceChild("abdomen3", CubeListBuilder.create()
                .texOffs(432, 282).addBox(-10.5F, 0F, -8.5F, 21F, 17F, 17F),
                PartPose.offsetAndRotation(0F, 18F, 0F, 0.1396F, 0F, 0F));
        PartDefinition p_abdomen4 = p_abdomen3.addOrReplaceChild("abdomen4", CubeListBuilder.create()
                .texOffs(830, 282).addBox(-7F, 0F, -6F, 14F, 14F, 12F),
                PartPose.offsetAndRotation(0F, 17F, 0F, 0.1745F, 0F, 0F));
        PartDefinition p_punta = p_abdomen4.addOrReplaceChild("punta", CubeListBuilder.create()
                .texOffs(900, 282).addBox(-3.5F, 0F, -3F, 7F, 9F, 6F)
                .texOffs(26, 332).addBox(-2F, 8F, -2F, 4F, 4F, 4F),
                PartPose.offsetAndRotation(0F, 14F, 0F, 0.1745F, 0F, 0F));
        p_punta.addOrReplaceChild("cinta_izq", CubeListBuilder.create()
                .texOffs(402, 148).addBox(-7F, 0F, 0F, 14F, 96F, 0F),
                PartPose.offsetAndRotation(1.5F, 10F, 0F, 0F, 0F, -0.1396F));
        p_punta.addOrReplaceChild("cinta_der", CubeListBuilder.create()
                .texOffs(432, 148).addBox(-7F, 0F, 0F, 14F, 84F, 0F),
                PartPose.offsetAndRotation(-1.5F, 10F, 0F, 0F, 0F, 0.1745F));
        return LayerDefinition.create(malla, 1024, 512);
    }
}
