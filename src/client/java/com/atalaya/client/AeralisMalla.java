package com.atalaya.client;

import net.minecraft.client.model.geom.PartPose;
import net.minecraft.client.model.geom.builders.CubeDeformation;
import net.minecraft.client.model.geom.builders.CubeListBuilder;
import net.minecraft.client.model.geom.builders.LayerDefinition;
import net.minecraft.client.model.geom.builders.MeshDefinition;
import net.minecraft.client.model.geom.builders.PartDefinition;

/**
 * La malla de Aeralis, la Reina del Vendaval. GENERADO por
 * materiales/generadores/vendaval_juego.py: no se edita a mano. Cambiar una
 * caja aqui sin cambiar el script descuadra la textura, que se pinta con la
 * misma cuadricula (a media resolucion: el atlas se declara de 1024 y el PNG
 * mide la mitad).
 */
public final class AeralisMalla {

    private AeralisMalla() {
    }

    public static LayerDefinition crear() {
        return crear(CubeDeformation.NONE);
    }

    /** La misma malla hinchada: la capa del aura de la Furia (como la de Rajang). */
    public static LayerDefinition crearAura() {
        return crear(new CubeDeformation(2.0F));
    }

    private static LayerDefinition crear(CubeDeformation infla) {
        MeshDefinition malla = new MeshDefinition();
        PartDefinition p_root = malla.getRoot();
        PartDefinition p_cuerpo = p_root.addOrReplaceChild("cuerpo", CubeListBuilder.create(),
                PartPose.offsetAndRotation(0F, -100F, 0F, 0F, 0F, 0F));
        PartDefinition p_torax = p_cuerpo.addOrReplaceChild("torax", CubeListBuilder.create()
                .texOffs(710, 676).addBox(-26F, -28F, -20F, 52F, 56F, 40F, infla)
                .texOffs(110, 966).addBox(-20F, -31F, 6F, 40F, 26F, 16F, infla)
                .texOffs(654, 966).addBox(-18F, -10F, -20.4F, 36F, 34F, 1.4F, infla)
                .texOffs(538, 966).addBox(-26.8F, -18F, -4F, 1.2F, 36F, 3F, infla)
                .texOffs(538, 966).addBox(25.6F, -18F, -4F, 1.2F, 36F, 3F, infla)
                .texOffs(224, 966).addBox(-22F, 24F, -17F, 44F, 7F, 34F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0F, -0.1396F, 0F, 0F));
        PartDefinition p_nucleo = p_torax.addOrReplaceChild("nucleo", CubeListBuilder.create()
                .texOffs(382, 966).addBox(-20F, -20F, -0.6F, 40F, 40F, 0.6F, infla),
                PartPose.offsetAndRotation(0F, 7F, -20.6F, 0F, 0F, 0F));
        p_nucleo.addOrReplaceChild("marco0", CubeListBuilder.create()
                .texOffs(756, 1046).addBox(-1.5F, -8F, -1.5F, 3F, 8F, 3F, infla),
                PartPose.offsetAndRotation(17.5537F, 7.271F, -0.4F, 0F, 0F, 1.9635F));
        p_nucleo.addOrReplaceChild("marco1", CubeListBuilder.create()
                .texOffs(756, 1046).addBox(-1.5F, -8F, -1.5F, 3F, 8F, 3F, infla),
                PartPose.offsetAndRotation(7.271F, 17.5537F, -0.4F, 0F, 0F, 2.7489F));
        p_nucleo.addOrReplaceChild("marco2", CubeListBuilder.create()
                .texOffs(756, 1046).addBox(-1.5F, -8F, -1.5F, 3F, 8F, 3F, infla),
                PartPose.offsetAndRotation(-7.271F, 17.5537F, -0.4F, 0F, 0F, 3.5343F));
        p_nucleo.addOrReplaceChild("marco3", CubeListBuilder.create()
                .texOffs(756, 1046).addBox(-1.5F, -8F, -1.5F, 3F, 8F, 3F, infla),
                PartPose.offsetAndRotation(-17.5537F, 7.271F, -0.4F, 0F, 0F, 4.3197F));
        p_nucleo.addOrReplaceChild("marco4", CubeListBuilder.create()
                .texOffs(756, 1046).addBox(-1.5F, -8F, -1.5F, 3F, 8F, 3F, infla),
                PartPose.offsetAndRotation(-17.5537F, -7.271F, -0.4F, 0F, 0F, 5.1051F));
        p_nucleo.addOrReplaceChild("marco5", CubeListBuilder.create()
                .texOffs(756, 1046).addBox(-1.5F, -8F, -1.5F, 3F, 8F, 3F, infla),
                PartPose.offsetAndRotation(-7.271F, -17.5537F, -0.4F, 0F, 0F, 5.8905F));
        p_nucleo.addOrReplaceChild("marco6", CubeListBuilder.create()
                .texOffs(756, 1046).addBox(-1.5F, -8F, -1.5F, 3F, 8F, 3F, infla),
                PartPose.offsetAndRotation(7.271F, -17.5537F, -0.4F, 0F, 0F, 6.6759F));
        p_nucleo.addOrReplaceChild("marco7", CubeListBuilder.create()
                .texOffs(756, 1046).addBox(-1.5F, -8F, -1.5F, 3F, 8F, 3F, infla),
                PartPose.offsetAndRotation(17.5537F, -7.271F, -0.4F, 0F, 0F, 7.4613F));
        PartDefinition p_melena = p_torax.addOrReplaceChild("melena", CubeListBuilder.create()
                .texOffs(0, 888).addBox(-40F, -14F, -28F, 80F, 22F, 54F, infla)
                .texOffs(430, 888).addBox(-46F, -8F, -18F, 12F, 20F, 38F, infla)
                .texOffs(430, 888).addBox(34F, -8F, -18F, 12F, 20F, 38F, infla)
                .texOffs(692, 888).addBox(-30F, -21F, -24F, 60F, 8F, 42F, infla),
                PartPose.offsetAndRotation(0F, -24F, 2F, 0F, 0F, 0F));
        p_melena.addOrReplaceChild("mechon0", CubeListBuilder.create()
                .texOffs(466, 966).addBox(-6F, -30F, -5F, 12F, 30F, 10F, infla)
                .texOffs(844, 1012).addBox(-4F, -38F, -4F, 8F, 9F, 8F, infla),
                PartPose.offsetAndRotation(-19F, -12F, -19.6506F, 0.6046F, 0F, -0.3491F));
        p_melena.addOrReplaceChild("mechon1", CubeListBuilder.create()
                .texOffs(466, 966).addBox(-6F, -30F, -5F, 12F, 30F, 10F, infla)
                .texOffs(844, 1012).addBox(-4F, -38F, -4F, 8F, 9F, 8F, infla),
                PartPose.offsetAndRotation(-33.958F, -12F, -9.22F, 0.3133F, 0F, -0.6239F));
        p_melena.addOrReplaceChild("mechon2", CubeListBuilder.create()
                .texOffs(466, 966).addBox(-6F, -30F, -5F, 12F, 30F, 10F, infla)
                .texOffs(844, 1012).addBox(-4F, -38F, -4F, 8F, 9F, 8F, infla),
                PartPose.offsetAndRotation(-37.7431F, -12F, 4.9023F, -0.081F, 0F, -0.6934F));
        p_melena.addOrReplaceChild("mechon3", CubeListBuilder.create()
                .texOffs(466, 966).addBox(-6F, -30F, -5F, 12F, 30F, 10F, infla)
                .texOffs(844, 1012).addBox(-4F, -38F, -4F, 8F, 9F, 8F, infla),
                PartPose.offsetAndRotation(-29.1097F, -12F, 18.0697F, -0.4488F, 0F, -0.5348F));
        p_melena.addOrReplaceChild("mechon4", CubeListBuilder.create()
                .texOffs(466, 966).addBox(-6F, -30F, -5F, 12F, 30F, 10F, infla)
                .texOffs(844, 1012).addBox(-4F, -38F, -4F, 8F, 9F, 8F, infla),
                PartPose.offsetAndRotation(-10.8985F, -12F, 25.9497F, -0.6688F, 0F, -0.2002F));
        p_melena.addOrReplaceChild("mechon5", CubeListBuilder.create()
                .texOffs(466, 966).addBox(-6F, -30F, -5F, 12F, 30F, 10F, infla)
                .texOffs(844, 1012).addBox(-4F, -38F, -4F, 8F, 9F, 8F, infla),
                PartPose.offsetAndRotation(10.8985F, -12F, 25.9497F, -0.6688F, 0F, 0.2002F));
        p_melena.addOrReplaceChild("mechon6", CubeListBuilder.create()
                .texOffs(466, 966).addBox(-6F, -30F, -5F, 12F, 30F, 10F, infla)
                .texOffs(844, 1012).addBox(-4F, -38F, -4F, 8F, 9F, 8F, infla),
                PartPose.offsetAndRotation(29.1097F, -12F, 18.0697F, -0.4488F, 0F, 0.5348F));
        p_melena.addOrReplaceChild("mechon7", CubeListBuilder.create()
                .texOffs(466, 966).addBox(-6F, -30F, -5F, 12F, 30F, 10F, infla)
                .texOffs(844, 1012).addBox(-4F, -38F, -4F, 8F, 9F, 8F, infla),
                PartPose.offsetAndRotation(37.7431F, -12F, 4.9023F, -0.081F, 0F, 0.6934F));
        p_melena.addOrReplaceChild("mechon8", CubeListBuilder.create()
                .texOffs(466, 966).addBox(-6F, -30F, -5F, 12F, 30F, 10F, infla)
                .texOffs(844, 1012).addBox(-4F, -38F, -4F, 8F, 9F, 8F, infla),
                PartPose.offsetAndRotation(33.958F, -12F, -9.22F, 0.3133F, 0F, 0.6239F));
        p_melena.addOrReplaceChild("mechon9", CubeListBuilder.create()
                .texOffs(466, 966).addBox(-6F, -30F, -5F, 12F, 30F, 10F, infla)
                .texOffs(844, 1012).addBox(-4F, -38F, -4F, 8F, 9F, 8F, infla),
                PartPose.offsetAndRotation(19F, -12F, -19.6506F, 0.6046F, 0F, 0.3491F));
        PartDefinition p_cabeza = p_torax.addOrReplaceChild("cabeza", CubeListBuilder.create()
                .texOffs(296, 888).addBox(-18F, -28F, -16F, 36F, 28F, 30F, infla)
                .texOffs(0, 1012).addBox(-20F, -33F, -8F, 40F, 8F, 24F, infla)
                .texOffs(974, 1046).addBox(-6F, -8F, -17.2F, 12F, 8F, 1.2F, infla)
                .texOffs(376, 1012).addBox(-11F, -2F, -13F, 22F, 7F, 16F, infla),
                PartPose.offsetAndRotation(0F, -31F, -6F, 0.2443F, 0F, 0F));
        p_cabeza.addOrReplaceChild("pua0", CubeListBuilder.create()
                .texOffs(512, 966).addBox(-3F, -33F, -3F, 6F, 33F, 6F, infla)
                .texOffs(650, 1046).addBox(-2.2F, -41F, -2.2F, 4.4F, 8F, 4.4F, infla),
                PartPose.offsetAndRotation(-12.7159F, -27F, 6F, -0.2618F, 0F, -1.3614F));
        p_cabeza.addOrReplaceChild("pua1", CubeListBuilder.create()
                .texOffs(898, 888).addBox(-3F, -40F, -3F, 6F, 40F, 6F, infla)
                .texOffs(650, 1046).addBox(-2.2F, -48F, -2.2F, 4.4F, 8F, 4.4F, infla),
                PartPose.offsetAndRotation(-10.2441F, -27F, 6F, -0.3142F, 0F, -0.9076F));
        p_cabeza.addOrReplaceChild("pua2", CubeListBuilder.create()
                .texOffs(532, 888).addBox(-3F, -47F, -3F, 6F, 47F, 6F, infla)
                .texOffs(650, 1046).addBox(-2.2F, -55F, -2.2F, 4.4F, 8F, 4.4F, infla),
                PartPose.offsetAndRotation(-5.6988F, -27F, 6F, -0.3665F, 0F, -0.4538F));
        p_cabeza.addOrReplaceChild("pua3", CubeListBuilder.create()
                .texOffs(270, 888).addBox(-3F, -54F, -3F, 6F, 54F, 6F, infla)
                .texOffs(650, 1046).addBox(-2.2F, -62F, -2.2F, 4.4F, 8F, 4.4F, infla),
                PartPose.offsetAndRotation(0F, -27F, 6F, -0.4189F, 0F, 0F));
        p_cabeza.addOrReplaceChild("pua4", CubeListBuilder.create()
                .texOffs(532, 888).addBox(-3F, -47F, -3F, 6F, 47F, 6F, infla)
                .texOffs(650, 1046).addBox(-2.2F, -55F, -2.2F, 4.4F, 8F, 4.4F, infla),
                PartPose.offsetAndRotation(5.6988F, -27F, 6F, -0.3665F, 0F, 0.4538F));
        p_cabeza.addOrReplaceChild("pua5", CubeListBuilder.create()
                .texOffs(898, 888).addBox(-3F, -40F, -3F, 6F, 40F, 6F, infla)
                .texOffs(650, 1046).addBox(-2.2F, -48F, -2.2F, 4.4F, 8F, 4.4F, infla),
                PartPose.offsetAndRotation(10.2441F, -27F, 6F, -0.3142F, 0F, 0.9076F));
        p_cabeza.addOrReplaceChild("pua6", CubeListBuilder.create()
                .texOffs(512, 966).addBox(-3F, -33F, -3F, 6F, 33F, 6F, infla)
                .texOffs(650, 1046).addBox(-2.2F, -41F, -2.2F, 4.4F, 8F, 4.4F, infla),
                PartPose.offsetAndRotation(12.7159F, -27F, 6F, -0.2618F, 0F, 1.3614F));
        p_cabeza.addOrReplaceChild("ojo_izq", CubeListBuilder.create()
                .texOffs(130, 1012).addBox(-6F, -9F, -5F, 12F, 18F, 14F, infla),
                PartPose.offsetAndRotation(12F, -15F, -13F, 0F, 0F, -0.3142F));
        p_cabeza.addOrReplaceChild("ceno_izq", CubeListBuilder.create()
                .texOffs(708, 1046).addBox(-8F, -3F, -1F, 17F, 5F, 6F, infla),
                PartPose.offsetAndRotation(9F, -23F, -17.5F, 0F, 0F, -0.384F));
        PartDefinition p_colmillo_izq = p_cabeza.addOrReplaceChild("colmillo_izq", CubeListBuilder.create()
                .texOffs(878, 1012).addBox(-2F, 0F, -2F, 4F, 13F, 4F, infla),
                PartPose.offsetAndRotation(6F, -3F, -15F, -0.2094F, 0F, -0.2793F));
        p_colmillo_izq.addOrReplaceChild("colmillo_punta_izq", CubeListBuilder.create()
                .texOffs(292, 1046).addBox(-1.4F, 0F, -1.4F, 2.8F, 11F, 2.8F, infla),
                PartPose.offsetAndRotation(0F, 13F, 0F, -0.5236F, 0F, 0.5934F));
        PartDefinition p_antena_izq = p_cabeza.addOrReplaceChild("antena_izq", CubeListBuilder.create()
                .texOffs(896, 676).addBox(-1.6F, -80F, -1.6F, 3.2F, 80F, 3.2F, infla)
                .texOffs(354, 1062).addBox(0.8F, -8F, -0.6F, 6.9F, 1.4F, 1.2F, infla)
                .texOffs(354, 1062).addBox(-7.7F, -8F, -0.6F, 6.9F, 1.4F, 1.2F, infla)
                .texOffs(334, 1062).addBox(0.8F, -12.6F, -0.6F, 7.75F, 1.4F, 1.2F, infla)
                .texOffs(334, 1062).addBox(-8.55F, -12.6F, -0.6F, 7.75F, 1.4F, 1.2F, infla)
                .texOffs(312, 1062).addBox(0.8F, -17.2F, -0.6F, 8.6F, 1.4F, 1.2F, infla)
                .texOffs(312, 1062).addBox(-9.4F, -17.2F, -0.6F, 8.6F, 1.4F, 1.2F, infla)
                .texOffs(288, 1062).addBox(0.8F, -21.8F, -0.6F, 9.45F, 1.4F, 1.2F, infla)
                .texOffs(288, 1062).addBox(-10.25F, -21.8F, -0.6F, 9.45F, 1.4F, 1.2F, infla)
                .texOffs(262, 1062).addBox(0.8F, -26.4F, -0.6F, 10.3F, 1.4F, 1.2F, infla)
                .texOffs(262, 1062).addBox(-11.1F, -26.4F, -0.6F, 10.3F, 1.4F, 1.2F, infla)
                .texOffs(234, 1062).addBox(0.8F, -31F, -0.6F, 11.15F, 1.4F, 1.2F, infla)
                .texOffs(234, 1062).addBox(-11.95F, -31F, -0.6F, 11.15F, 1.4F, 1.2F, infla)
                .texOffs(204, 1062).addBox(0.8F, -35.6F, -0.6F, 12F, 1.4F, 1.2F, infla)
                .texOffs(204, 1062).addBox(-12.8F, -35.6F, -0.6F, 12F, 1.4F, 1.2F, infla)
                .texOffs(234, 1062).addBox(0.8F, -40.2F, -0.6F, 11.15F, 1.4F, 1.2F, infla)
                .texOffs(234, 1062).addBox(-11.95F, -40.2F, -0.6F, 11.15F, 1.4F, 1.2F, infla)
                .texOffs(262, 1062).addBox(0.8F, -44.8F, -0.6F, 10.3F, 1.4F, 1.2F, infla)
                .texOffs(262, 1062).addBox(-11.1F, -44.8F, -0.6F, 10.3F, 1.4F, 1.2F, infla)
                .texOffs(288, 1062).addBox(0.8F, -49.4F, -0.6F, 9.45F, 1.4F, 1.2F, infla)
                .texOffs(288, 1062).addBox(-10.25F, -49.4F, -0.6F, 9.45F, 1.4F, 1.2F, infla)
                .texOffs(312, 1062).addBox(0.8F, -54F, -0.6F, 8.6F, 1.4F, 1.2F, infla)
                .texOffs(312, 1062).addBox(-9.4F, -54F, -0.6F, 8.6F, 1.4F, 1.2F, infla)
                .texOffs(334, 1062).addBox(0.8F, -58.6F, -0.6F, 7.75F, 1.4F, 1.2F, infla)
                .texOffs(334, 1062).addBox(-8.55F, -58.6F, -0.6F, 7.75F, 1.4F, 1.2F, infla)
                .texOffs(354, 1062).addBox(0.8F, -63.2F, -0.6F, 6.9F, 1.4F, 1.2F, infla)
                .texOffs(354, 1062).addBox(-7.7F, -63.2F, -0.6F, 6.9F, 1.4F, 1.2F, infla)
                .texOffs(374, 1062).addBox(0.8F, -67.8F, -0.6F, 6.05F, 1.4F, 1.2F, infla)
                .texOffs(374, 1062).addBox(-6.85F, -67.8F, -0.6F, 6.05F, 1.4F, 1.2F, infla)
                .texOffs(392, 1062).addBox(0.8F, -72.4F, -0.6F, 5.2F, 1.4F, 1.2F, infla)
                .texOffs(392, 1062).addBox(-6F, -72.4F, -0.6F, 5.2F, 1.4F, 1.2F, infla)
                .texOffs(408, 1062).addBox(0.8F, -77F, -0.6F, 4.35F, 1.4F, 1.2F, infla)
                .texOffs(408, 1062).addBox(-5.15F, -77F, -0.6F, 4.35F, 1.4F, 1.2F, infla),
                PartPose.offsetAndRotation(9F, -27F, -8F, -0.6981F, 0F, 0.6283F));
        p_antena_izq.addOrReplaceChild("antena_punta_izq", CubeListBuilder.create()
                .texOffs(896, 1012).addBox(-1F, -14F, -1F, 2F, 14F, 2F, infla)
                .texOffs(174, 1062).addBox(-2F, -18F, -2F, 4F, 4F, 4F, infla),
                PartPose.offsetAndRotation(0F, -80F, 0F, -0.6981F, 0F, -0.2443F));
        p_cabeza.addOrReplaceChild("ojo_der", CubeListBuilder.create()
                .texOffs(130, 1012).addBox(-6F, -9F, -5F, 12F, 18F, 14F, infla),
                PartPose.offsetAndRotation(-12F, -15F, -13F, 0F, 0F, 0.3142F));
        p_cabeza.addOrReplaceChild("ceno_der", CubeListBuilder.create()
                .texOffs(708, 1046).addBox(-9F, -3F, -1F, 17F, 5F, 6F, infla),
                PartPose.offsetAndRotation(-9F, -23F, -17.5F, 0F, 0F, 0.384F));
        PartDefinition p_colmillo_der = p_cabeza.addOrReplaceChild("colmillo_der", CubeListBuilder.create()
                .texOffs(878, 1012).addBox(-2F, 0F, -2F, 4F, 13F, 4F, infla),
                PartPose.offsetAndRotation(-6F, -3F, -15F, -0.2094F, 0F, 0.2793F));
        p_colmillo_der.addOrReplaceChild("colmillo_punta_der", CubeListBuilder.create()
                .texOffs(292, 1046).addBox(-1.4F, 0F, -1.4F, 2.8F, 11F, 2.8F, infla),
                PartPose.offsetAndRotation(0F, 13F, 0F, -0.5236F, 0F, -0.5934F));
        PartDefinition p_antena_der = p_cabeza.addOrReplaceChild("antena_der", CubeListBuilder.create()
                .texOffs(896, 676).addBox(-1.6F, -80F, -1.6F, 3.2F, 80F, 3.2F, infla)
                .texOffs(354, 1062).addBox(0.8F, -8F, -0.6F, 6.9F, 1.4F, 1.2F, infla)
                .texOffs(354, 1062).addBox(-7.7F, -8F, -0.6F, 6.9F, 1.4F, 1.2F, infla)
                .texOffs(334, 1062).addBox(0.8F, -12.6F, -0.6F, 7.75F, 1.4F, 1.2F, infla)
                .texOffs(334, 1062).addBox(-8.55F, -12.6F, -0.6F, 7.75F, 1.4F, 1.2F, infla)
                .texOffs(312, 1062).addBox(0.8F, -17.2F, -0.6F, 8.6F, 1.4F, 1.2F, infla)
                .texOffs(312, 1062).addBox(-9.4F, -17.2F, -0.6F, 8.6F, 1.4F, 1.2F, infla)
                .texOffs(288, 1062).addBox(0.8F, -21.8F, -0.6F, 9.45F, 1.4F, 1.2F, infla)
                .texOffs(288, 1062).addBox(-10.25F, -21.8F, -0.6F, 9.45F, 1.4F, 1.2F, infla)
                .texOffs(262, 1062).addBox(0.8F, -26.4F, -0.6F, 10.3F, 1.4F, 1.2F, infla)
                .texOffs(262, 1062).addBox(-11.1F, -26.4F, -0.6F, 10.3F, 1.4F, 1.2F, infla)
                .texOffs(234, 1062).addBox(0.8F, -31F, -0.6F, 11.15F, 1.4F, 1.2F, infla)
                .texOffs(234, 1062).addBox(-11.95F, -31F, -0.6F, 11.15F, 1.4F, 1.2F, infla)
                .texOffs(204, 1062).addBox(0.8F, -35.6F, -0.6F, 12F, 1.4F, 1.2F, infla)
                .texOffs(204, 1062).addBox(-12.8F, -35.6F, -0.6F, 12F, 1.4F, 1.2F, infla)
                .texOffs(234, 1062).addBox(0.8F, -40.2F, -0.6F, 11.15F, 1.4F, 1.2F, infla)
                .texOffs(234, 1062).addBox(-11.95F, -40.2F, -0.6F, 11.15F, 1.4F, 1.2F, infla)
                .texOffs(262, 1062).addBox(0.8F, -44.8F, -0.6F, 10.3F, 1.4F, 1.2F, infla)
                .texOffs(262, 1062).addBox(-11.1F, -44.8F, -0.6F, 10.3F, 1.4F, 1.2F, infla)
                .texOffs(288, 1062).addBox(0.8F, -49.4F, -0.6F, 9.45F, 1.4F, 1.2F, infla)
                .texOffs(288, 1062).addBox(-10.25F, -49.4F, -0.6F, 9.45F, 1.4F, 1.2F, infla)
                .texOffs(312, 1062).addBox(0.8F, -54F, -0.6F, 8.6F, 1.4F, 1.2F, infla)
                .texOffs(312, 1062).addBox(-9.4F, -54F, -0.6F, 8.6F, 1.4F, 1.2F, infla)
                .texOffs(334, 1062).addBox(0.8F, -58.6F, -0.6F, 7.75F, 1.4F, 1.2F, infla)
                .texOffs(334, 1062).addBox(-8.55F, -58.6F, -0.6F, 7.75F, 1.4F, 1.2F, infla)
                .texOffs(354, 1062).addBox(0.8F, -63.2F, -0.6F, 6.9F, 1.4F, 1.2F, infla)
                .texOffs(354, 1062).addBox(-7.7F, -63.2F, -0.6F, 6.9F, 1.4F, 1.2F, infla)
                .texOffs(374, 1062).addBox(0.8F, -67.8F, -0.6F, 6.05F, 1.4F, 1.2F, infla)
                .texOffs(374, 1062).addBox(-6.85F, -67.8F, -0.6F, 6.05F, 1.4F, 1.2F, infla)
                .texOffs(392, 1062).addBox(0.8F, -72.4F, -0.6F, 5.2F, 1.4F, 1.2F, infla)
                .texOffs(392, 1062).addBox(-6F, -72.4F, -0.6F, 5.2F, 1.4F, 1.2F, infla)
                .texOffs(408, 1062).addBox(0.8F, -77F, -0.6F, 4.35F, 1.4F, 1.2F, infla)
                .texOffs(408, 1062).addBox(-5.15F, -77F, -0.6F, 4.35F, 1.4F, 1.2F, infla),
                PartPose.offsetAndRotation(-9F, -27F, -8F, -0.6981F, 0F, -0.6283F));
        p_antena_der.addOrReplaceChild("antena_punta_der", CubeListBuilder.create()
                .texOffs(896, 1012).addBox(-1F, -14F, -1F, 2F, 14F, 2F, infla)
                .texOffs(174, 1062).addBox(-2F, -18F, -2F, 4F, 4F, 4F, infla),
                PartPose.offsetAndRotation(0F, -80F, 0F, -0.6981F, 0F, 0.2443F));
        PartDefinition p_ala_sup_izq = p_torax.addOrReplaceChild("ala_sup_izq", CubeListBuilder.create()
                .texOffs(0, 464).addBox(0F, -75.6F, 0F, 320F, 210F, 0F, infla),
                PartPose.offsetAndRotation(24F, -16F, 14F, 0F, -0.2094F, -0.1745F));
        p_ala_sup_izq.addOrReplaceChild("costa_sup_izq0", CubeListBuilder.create()
                .texOffs(600, 1012).addBox(0F, -4.25F, -4.25F, 111.7158F, 8.5F, 8.5F, infla),
                PartPose.offsetAndRotation(0F, -12.6F, 0F, 0F, 0F, -0.4661F));
        p_ala_sup_izq.addOrReplaceChild("costa_sup_izq1", CubeListBuilder.create()
                .texOffs(306, 1046).addBox(0F, -3.25F, -3.25F, 163.9239F, 6.5F, 6.5F, infla),
                PartPose.offsetAndRotation(96F, -60.9F, 0F, 0F, 0F, -0.0916F));
        p_ala_sup_izq.addOrReplaceChild("costa_sup_izq2", CubeListBuilder.create()
                .texOffs(22, 1062).addBox(0F, -2.25F, -2.25F, 69.6073F, 4.5F, 4.5F, infla),
                PartPose.offsetAndRotation(256F, -75.6F, 0F, 0F, 0F, 0.3171F));
        PartDefinition p_ala_inf_izq = p_torax.addOrReplaceChild("ala_inf_izq", CubeListBuilder.create()
                .texOffs(0, 0).addBox(0F, -9.44F, 0F, 216F, 236F, 0F, infla),
                PartPose.offsetAndRotation(22F, 12F, 16F, 0F, -0.3142F, -0.2094F));
        p_ala_inf_izq.addOrReplaceChild("costa_inf_izq0", CubeListBuilder.create()
                .texOffs(0, 1046).addBox(0F, -3.5F, -3.5F, 137.9389F, 7F, 7F, infla),
                PartPose.offsetAndRotation(0F, -9.44F, 0F, 0F, 0F, 0.0879F));
        p_ala_inf_izq.addOrReplaceChild("costa_inf_izq1", CubeListBuilder.create()
                .texOffs(784, 1046).addBox(0F, -2.5F, -2.5F, 88.6972F, 5F, 5F, infla),
                PartPose.offsetAndRotation(133.92F, 2.36F, 0F, 0F, 0F, 0.6812F));
        PartDefinition p_ala_sup_der = p_torax.addOrReplaceChild("ala_sup_der", CubeListBuilder.create()
                .texOffs(0, 676).addBox(-320F, -75.6F, 0F, 320F, 210F, 0F, infla),
                PartPose.offsetAndRotation(-24F, -16F, 14F, 0F, 0.2094F, 0.1745F));
        p_ala_sup_der.addOrReplaceChild("costa_sup_der0", CubeListBuilder.create()
                .texOffs(600, 1012).addBox(0F, -4.25F, -4.25F, 111.7158F, 8.5F, 8.5F, infla),
                PartPose.offsetAndRotation(0F, -12.6F, 0F, 0F, 0F, -2.6754F));
        p_ala_sup_der.addOrReplaceChild("costa_sup_der1", CubeListBuilder.create()
                .texOffs(306, 1046).addBox(0F, -3.25F, -3.25F, 163.9239F, 6.5F, 6.5F, infla),
                PartPose.offsetAndRotation(-96F, -60.9F, 0F, 0F, 0F, -3.05F));
        p_ala_sup_der.addOrReplaceChild("costa_sup_der2", CubeListBuilder.create()
                .texOffs(22, 1062).addBox(0F, -2.25F, -2.25F, 69.6073F, 4.5F, 4.5F, infla),
                PartPose.offsetAndRotation(-256F, -75.6F, 0F, 0F, 0F, 2.8245F));
        PartDefinition p_ala_inf_der = p_torax.addOrReplaceChild("ala_inf_der", CubeListBuilder.create()
                .texOffs(434, 0).addBox(-216F, -9.44F, 0F, 216F, 236F, 0F, infla),
                PartPose.offsetAndRotation(-22F, 12F, 16F, 0F, 0.3142F, 0.2094F));
        p_ala_inf_der.addOrReplaceChild("costa_inf_der0", CubeListBuilder.create()
                .texOffs(0, 1046).addBox(0F, -3.5F, -3.5F, 137.9389F, 7F, 7F, infla),
                PartPose.offsetAndRotation(0F, -9.44F, 0F, 0F, 0F, 3.0537F));
        p_ala_inf_der.addOrReplaceChild("costa_inf_der1", CubeListBuilder.create()
                .texOffs(784, 1046).addBox(0F, -2.5F, -2.5F, 88.6972F, 5F, 5F, infla),
                PartPose.offsetAndRotation(-133.92F, 2.36F, 0F, 0F, 0F, 2.4604F));
        p_torax.addOrReplaceChild("halo", CubeListBuilder.create()
                .texOffs(0, 238).addBox(-112F, -112F, 0F, 224F, 224F, 0F, infla),
                PartPose.offsetAndRotation(0F, -30F, 30F, 0F, 0F, 0F));
        PartDefinition p_pata0_izq = p_torax.addOrReplaceChild("pata0_izq", CubeListBuilder.create()
                .texOffs(732, 966).addBox(-3F, 0F, -3F, 6F, 30F, 6F, infla),
                PartPose.offsetAndRotation(16F, -6F, -12F, -0.9076F, 0F, 0.5236F));
        PartDefinition p_pata0_izq_tibia = p_pata0_izq.addOrReplaceChild("pata0_izq_tibia", CubeListBuilder.create()
                .texOffs(550, 966).addBox(-2.2F, 0F, -2.2F, 4.4F, 32F, 4.4F, infla)
                .texOffs(184, 1012).addBox(-0.6F, 3F, -7F, 1.2F, 26F, 5F, infla)
                .texOffs(192, 1062).addBox(-1F, 6F, -9.5F, 2F, 2F, 3F, infla)
                .texOffs(192, 1062).addBox(-1F, 12F, -9.5F, 2F, 2F, 3F, infla)
                .texOffs(192, 1062).addBox(-1F, 18F, -9.5F, 2F, 2F, 3F, infla)
                .texOffs(192, 1062).addBox(-1F, 24F, -9.5F, 2F, 2F, 3F, infla),
                PartPose.offsetAndRotation(0F, 30F, 0F, -1.7453F, 0F, 0F));
        p_pata0_izq_tibia.addOrReplaceChild("pata0_izq_garra", CubeListBuilder.create()
                .texOffs(670, 1046).addBox(-1.5F, 0F, -1F, 3F, 11F, 2F, infla),
                PartPose.offsetAndRotation(0F, 32F, 0F, 0.6981F, 0F, 0F));
        PartDefinition p_pata1_izq = p_torax.addOrReplaceChild("pata1_izq", CubeListBuilder.create()
                .texOffs(776, 966).addBox(-2.5F, 0F, -2.5F, 5F, 30F, 5F, infla)
                .texOffs(682, 1046).addBox(-3F, 4F, -3F, 6F, 6F, 6F, infla),
                PartPose.offsetAndRotation(17F, 5F, -4F, -0.1047F, 0F, 0.9076F));
        PartDefinition p_pata1_izq_tibia = p_pata1_izq.addOrReplaceChild("pata1_izq_tibia", CubeListBuilder.create()
                .texOffs(758, 966).addBox(-1.8F, 0F, -1.8F, 3.6F, 32F, 3.6F, infla),
                PartPose.offsetAndRotation(0F, 30F, 0F, 0.8727F, 0F, 0F));
        p_pata1_izq_tibia.addOrReplaceChild("pata1_izq_garra", CubeListBuilder.create()
                .texOffs(770, 1046).addBox(-2F, 0F, -0.75F, 4F, 9F, 1.5F, infla),
                PartPose.offsetAndRotation(0F, 32F, 0F, 0.5934F, 0F, 0F));
        PartDefinition p_pata2_izq = p_torax.addOrReplaceChild("pata2_izq", CubeListBuilder.create()
                .texOffs(776, 966).addBox(-2.5F, 0F, -2.5F, 5F, 30F, 5F, infla)
                .texOffs(682, 1046).addBox(-3F, 4F, -3F, 6F, 6F, 6F, infla),
                PartPose.offsetAndRotation(17F, 18F, 0F, 0.5236F, 0F, 0.9076F));
        PartDefinition p_pata2_izq_tibia = p_pata2_izq.addOrReplaceChild("pata2_izq_tibia", CubeListBuilder.create()
                .texOffs(758, 966).addBox(-1.8F, 0F, -1.8F, 3.6F, 32F, 3.6F, infla),
                PartPose.offsetAndRotation(0F, 30F, 0F, 0.8727F, 0F, 0F));
        p_pata2_izq_tibia.addOrReplaceChild("pata2_izq_garra", CubeListBuilder.create()
                .texOffs(770, 1046).addBox(-2F, 0F, -0.75F, 4F, 9F, 1.5F, infla),
                PartPose.offsetAndRotation(0F, 32F, 0F, 0.5934F, 0F, 0F));
        PartDefinition p_pata0_der = p_torax.addOrReplaceChild("pata0_der", CubeListBuilder.create()
                .texOffs(732, 966).addBox(-3F, 0F, -3F, 6F, 30F, 6F, infla),
                PartPose.offsetAndRotation(-16F, -6F, -12F, -0.9076F, 0F, -0.5236F));
        PartDefinition p_pata0_der_tibia = p_pata0_der.addOrReplaceChild("pata0_der_tibia", CubeListBuilder.create()
                .texOffs(550, 966).addBox(-2.2F, 0F, -2.2F, 4.4F, 32F, 4.4F, infla)
                .texOffs(184, 1012).addBox(-0.6F, 3F, -7F, 1.2F, 26F, 5F, infla)
                .texOffs(192, 1062).addBox(-1F, 6F, -9.5F, 2F, 2F, 3F, infla)
                .texOffs(192, 1062).addBox(-1F, 12F, -9.5F, 2F, 2F, 3F, infla)
                .texOffs(192, 1062).addBox(-1F, 18F, -9.5F, 2F, 2F, 3F, infla)
                .texOffs(192, 1062).addBox(-1F, 24F, -9.5F, 2F, 2F, 3F, infla),
                PartPose.offsetAndRotation(0F, 30F, 0F, -1.7453F, 0F, 0F));
        p_pata0_der_tibia.addOrReplaceChild("pata0_der_garra", CubeListBuilder.create()
                .texOffs(670, 1046).addBox(-1.5F, 0F, -1F, 3F, 11F, 2F, infla),
                PartPose.offsetAndRotation(0F, 32F, 0F, 0.6981F, 0F, 0F));
        PartDefinition p_pata1_der = p_torax.addOrReplaceChild("pata1_der", CubeListBuilder.create()
                .texOffs(776, 966).addBox(-2.5F, 0F, -2.5F, 5F, 30F, 5F, infla)
                .texOffs(682, 1046).addBox(-3F, 4F, -3F, 6F, 6F, 6F, infla),
                PartPose.offsetAndRotation(-17F, 5F, -4F, -0.1047F, 0F, -0.9076F));
        PartDefinition p_pata1_der_tibia = p_pata1_der.addOrReplaceChild("pata1_der_tibia", CubeListBuilder.create()
                .texOffs(758, 966).addBox(-1.8F, 0F, -1.8F, 3.6F, 32F, 3.6F, infla),
                PartPose.offsetAndRotation(0F, 30F, 0F, 0.8727F, 0F, 0F));
        p_pata1_der_tibia.addOrReplaceChild("pata1_der_garra", CubeListBuilder.create()
                .texOffs(770, 1046).addBox(-2F, 0F, -0.75F, 4F, 9F, 1.5F, infla),
                PartPose.offsetAndRotation(0F, 32F, 0F, 0.5934F, 0F, 0F));
        PartDefinition p_pata2_der = p_torax.addOrReplaceChild("pata2_der", CubeListBuilder.create()
                .texOffs(776, 966).addBox(-2.5F, 0F, -2.5F, 5F, 30F, 5F, infla)
                .texOffs(682, 1046).addBox(-3F, 4F, -3F, 6F, 6F, 6F, infla),
                PartPose.offsetAndRotation(-17F, 18F, 0F, 0.5236F, 0F, -0.9076F));
        PartDefinition p_pata2_der_tibia = p_pata2_der.addOrReplaceChild("pata2_der_tibia", CubeListBuilder.create()
                .texOffs(758, 966).addBox(-1.8F, 0F, -1.8F, 3.6F, 32F, 3.6F, infla),
                PartPose.offsetAndRotation(0F, 30F, 0F, 0.8727F, 0F, 0F));
        p_pata2_der_tibia.addOrReplaceChild("pata2_der_garra", CubeListBuilder.create()
                .texOffs(770, 1046).addBox(-2F, 0F, -0.75F, 4F, 9F, 1.5F, infla),
                PartPose.offsetAndRotation(0F, 32F, 0F, 0.5934F, 0F, 0F));
        PartDefinition p_abdomen = p_torax.addOrReplaceChild("abdomen", CubeListBuilder.create()
                .texOffs(558, 888).addBox(-18F, 0F, -15F, 36F, 22F, 30F, infla)
                .texOffs(798, 966).addBox(-18.6F, 20.4F, -15.6F, 37.2F, 1.6F, 31.2F, infla),
                PartPose.offsetAndRotation(0F, 25F, 4F, 0.1745F, 0F, 0F));
        PartDefinition p_abdomen2 = p_abdomen.addOrReplaceChild("abdomen2", CubeListBuilder.create()
                .texOffs(0, 966).addBox(-15F, 0F, -12F, 30F, 20F, 24F, infla)
                .texOffs(260, 1012).addBox(-15.6F, 18.4F, -12.6F, 31.2F, 1.6F, 25.2F, infla),
                PartPose.offsetAndRotation(0F, 22F, 0F, 0.1396F, 0F, 0F));
        PartDefinition p_abdomen3 = p_abdomen2.addOrReplaceChild("abdomen3", CubeListBuilder.create()
                .texOffs(570, 966).addBox(-11.5F, 0F, -9F, 23F, 18F, 18F, infla)
                .texOffs(454, 1012).addBox(-12.1F, 16.4F, -9.6F, 24.2F, 1.6F, 19.2F, infla),
                PartPose.offsetAndRotation(0F, 20F, 0F, 0.1396F, 0F, 0F));
        PartDefinition p_abdomen4 = p_abdomen3.addOrReplaceChild("abdomen4", CubeListBuilder.create()
                .texOffs(200, 1012).addBox(-8F, 0F, -6.5F, 16F, 15F, 13F, infla),
                PartPose.offsetAndRotation(0F, 18F, 0F, 0.1745F, 0F, 0F));
        PartDefinition p_punta = p_abdomen4.addOrReplaceChild("punta", CubeListBuilder.create()
                .texOffs(568, 1012).addBox(-4F, 0F, -3.5F, 8F, 11F, 7F, infla)
                .texOffs(0, 1062).addBox(-2.5F, 10F, -2.5F, 5F, 5F, 5F, infla)
                .texOffs(544, 1012).addBox(-0.6F, 1F, 3F, 1.2F, 12F, 9F, infla),
                PartPose.offsetAndRotation(0F, 15F, 0F, 0.1745F, 0F, 0F));
        p_punta.addOrReplaceChild("cinta_izq", CubeListBuilder.create()
                .texOffs(642, 676).addBox(-8F, 0F, 0F, 16F, 104F, 0F, infla),
                PartPose.offsetAndRotation(2F, 12F, 0F, 0F, 0F, -0.1396F));
        p_punta.addOrReplaceChild("cinta_der", CubeListBuilder.create()
                .texOffs(676, 676).addBox(-8F, 0F, 0F, 16F, 104F, 0F, infla),
                PartPose.offsetAndRotation(-2F, 12F, 0F, 0F, 0F, 0.1571F));
        p_punta.addOrReplaceChild("cinta_izq2", CubeListBuilder.create()
                .texOffs(912, 676).addBox(-7F, 0F, 0F, 14F, 78F, 0F, infla),
                PartPose.offsetAndRotation(3F, 12F, 0F, 0F, 0F, -0.384F));
        p_punta.addOrReplaceChild("cinta_der2", CubeListBuilder.create()
                .texOffs(942, 676).addBox(-7F, 0F, 0F, 14F, 78F, 0F, infla),
                PartPose.offsetAndRotation(-3F, 12F, 0F, 0F, 0F, 0.4189F));
        return LayerDefinition.create(malla, 1024, 2048);
    }
}
