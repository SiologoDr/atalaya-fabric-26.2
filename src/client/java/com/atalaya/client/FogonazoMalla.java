package com.atalaya.client;

import net.minecraft.client.model.geom.PartPose;
import net.minecraft.client.model.geom.builders.CubeListBuilder;
import net.minecraft.client.model.geom.builders.LayerDefinition;
import net.minecraft.client.model.geom.builders.MeshDefinition;
import net.minecraft.client.model.geom.builders.PartDefinition;

/**
 * La malla del Fogonazo. GENERADO por materiales/generadores/fogonazo_juego.py: no se edita a mano (la textura se
 * pinta con la misma cuadricula). Las partes con nombre son las que mueve FogonazoModel; cada caja va en su
 * propia pieza ("_c" y un numero) con su giro.
 */
public final class FogonazoMalla {

    private FogonazoMalla() {
    }

    public static LayerDefinition crear() {
        MeshDefinition malla = new MeshDefinition();
        PartDefinition raiz = malla.getRoot();
        PartDefinition p_cuerpo = raiz.addOrReplaceChild("cuerpo", CubeListBuilder.create(),
                PartPose.offsetAndRotation(0F, 15F, -0.4F, 0.05F, 0F, 0F));
        p_cuerpo.addOrReplaceChild("cuerpo_c0", CubeListBuilder.create().texOffs(0, 25).addBox(-4.6F, -2.52F, -4.2F, 9.2F, 5.04F, 8.4F),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        p_cuerpo.addOrReplaceChild("cuerpo_c1", CubeListBuilder.create().texOffs(171, 0).addBox(-3.22F, -3.6F, -4.5F, 6.44F, 7.2F, 9F),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        p_cuerpo.addOrReplaceChild("cuerpo_c2", CubeListBuilder.create().texOffs(203, 0).addBox(-3.404F, -2.664F, -5F, 6.808F, 5.328F, 10F),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        p_cuerpo.addOrReplaceChild("cuerpo_c3", CubeListBuilder.create().texOffs(99, 40).addBox(-1.8F, -1.8F, -2.5035F, 3.6F, 3.6F, 3.5835F),
                PartPose.offsetAndRotation(0F, -1F, 3.6F, 1.809F, 0F, 3.1416F));
        PartDefinition p_pecho0 = p_cuerpo.addOrReplaceChild("pecho0", CubeListBuilder.create(),
                PartPose.offsetAndRotation(0F, -3.2194F, 3.8172F, -0.6319F, 0F, 0F));
        p_pecho0.addOrReplaceChild("pecho0_c0", CubeListBuilder.create().texOffs(166, 40).addBox(-5.5F, -1.8F, -2.3F, 11F, 1.8F, 4.6F),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        p_pecho0.addOrReplaceChild("pecho0_c1", CubeListBuilder.create().texOffs(115, 40).addBox(-0.7F, -0.4F, -2.3F, 1.4F, 3F, 4.6F),
                PartPose.offsetAndRotation(-5.2F, -1.2F, 0F, 0F, 0F, 0.32F));
        p_pecho0.addOrReplaceChild("pecho0_c2", CubeListBuilder.create().texOffs(115, 40).addBox(-0.7F, -0.4F, -2.3F, 1.4F, 3F, 4.6F),
                PartPose.offsetAndRotation(5.2F, -1.2F, 0F, 0F, 0F, -0.32F));
        PartDefinition p_pecho1 = p_cuerpo.addOrReplaceChild("pecho1", CubeListBuilder.create(),
                PartPose.offsetAndRotation(0F, -4.3945F, 0.2799F, -0.0393F, 0F, 0F));
        p_pecho1.addOrReplaceChild("pecho1_c0", CubeListBuilder.create().texOffs(166, 40).addBox(-5.5F, -1.8F, -2.3F, 11F, 1.8F, 4.6F),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        p_pecho1.addOrReplaceChild("pecho1_c1", CubeListBuilder.create().texOffs(115, 40).addBox(-0.7F, -0.4F, -2.3F, 1.4F, 3F, 4.6F),
                PartPose.offsetAndRotation(-5.2F, -1.2F, 0F, 0F, 0F, 0.32F));
        p_pecho1.addOrReplaceChild("pecho1_c2", CubeListBuilder.create().texOffs(115, 40).addBox(-0.7F, -0.4F, -2.3F, 1.4F, 3F, 4.6F),
                PartPose.offsetAndRotation(5.2F, -1.2F, 0F, 0F, 0F, -0.32F));
        PartDefinition p_pecho2 = p_cuerpo.addOrReplaceChild("pecho2", CubeListBuilder.create(),
                PartPose.offsetAndRotation(0F, -3.5028F, -3.389F, 0.5384F, 0F, 0F));
        p_pecho2.addOrReplaceChild("pecho2_c0", CubeListBuilder.create().texOffs(166, 40).addBox(-5.5F, -1.8F, -2.3F, 11F, 1.8F, 4.6F),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        p_pecho2.addOrReplaceChild("pecho2_c1", CubeListBuilder.create().texOffs(115, 40).addBox(-0.7F, -0.4F, -2.3F, 1.4F, 3F, 4.6F),
                PartPose.offsetAndRotation(-5.2F, -1.2F, 0F, 0F, 0F, 0.32F));
        p_pecho2.addOrReplaceChild("pecho2_c2", CubeListBuilder.create().texOffs(115, 40).addBox(-0.7F, -0.4F, -2.3F, 1.4F, 3F, 4.6F),
                PartPose.offsetAndRotation(5.2F, -1.2F, 0F, 0F, 0F, -0.32F));
        PartDefinition p_farol = p_cuerpo.addOrReplaceChild("farol", CubeListBuilder.create(),
                PartPose.offsetAndRotation(0F, -1.8F, 4.2F, 1.1F, 0F, 0F));
        p_farol.addOrReplaceChild("farol_c0", CubeListBuilder.create().texOffs(174, 25).addBox(-6.1F, -4.248F, 2.9F, 12.2F, 8.496F, 1.4F),
                PartPose.offsetAndRotation(0F, 0F, 6.4F, 0F, 0F, -3.1416F));
        p_farol.addOrReplaceChild("farol_c1", CubeListBuilder.create().texOffs(37, 25).addBox(-4.514F, -5.9F, 2.9F, 9.028F, 11.8F, 1.4F),
                PartPose.offsetAndRotation(0F, 0F, 6.4F, 0F, 0F, -3.1416F));
        p_farol.addOrReplaceChild("farol_c2", CubeListBuilder.create().texOffs(174, 25).addBox(-6.1F, -4.248F, -0.7F, 12.2F, 8.496F, 1.4F),
                PartPose.offsetAndRotation(0F, 0F, 6.4F, 0F, 0F, -3.1416F));
        p_farol.addOrReplaceChild("farol_c3", CubeListBuilder.create().texOffs(37, 25).addBox(-4.514F, -5.9F, -0.7F, 9.028F, 11.8F, 1.4F),
                PartPose.offsetAndRotation(0F, 0F, 6.4F, 0F, 0F, -3.1416F));
        p_farol.addOrReplaceChild("farol_c4", CubeListBuilder.create().texOffs(174, 25).addBox(-6.1F, -4.248F, -4.3F, 12.2F, 8.496F, 1.4F),
                PartPose.offsetAndRotation(0F, 0F, 6.4F, 0F, 0F, -3.1416F));
        p_farol.addOrReplaceChild("farol_c5", CubeListBuilder.create().texOffs(37, 25).addBox(-4.514F, -5.9F, -4.3F, 9.028F, 11.8F, 1.4F),
                PartPose.offsetAndRotation(0F, 0F, 6.4F, 0F, 0F, -3.1416F));
        p_farol.addOrReplaceChild("farol_c6", CubeListBuilder.create().texOffs(199, 40).addBox(-2.2F, -2.2F, 0F, 4.4F, 4.4F, 2.6F),
                PartPose.offsetAndRotation(0F, 0F, 12.9F, 0F, 0F, -3.1416F));
        p_farol.addOrReplaceChild("farol_c7", CubeListBuilder.create().texOffs(40, 50).addBox(-1.2F, -1.2F, 2.4F, 2.4F, 2.4F, 2F),
                PartPose.offsetAndRotation(0F, 0F, 12.9F, 0F, 0F, -3.1416F));
        PartDefinition p_nucleo = p_farol.addOrReplaceChild("nucleo", CubeListBuilder.create(),
                PartPose.offsetAndRotation(0F, 0F, 6.4F, 0F, 0F, -3.1416F));
        p_nucleo.addOrReplaceChild("nucleo_c0", CubeListBuilder.create().texOffs(88, 0).addBox(-5.6F, -3.78F, -5.88F, 11.2F, 7.56F, 11.76F),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        p_nucleo.addOrReplaceChild("nucleo_c1", CubeListBuilder.create().texOffs(0, 0).addBox(-3.92F, -5.4F, -6.3F, 7.84F, 10.8F, 12.6F),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        p_nucleo.addOrReplaceChild("nucleo_c2", CubeListBuilder.create().texOffs(42, 0).addBox(-4.144F, -3.996F, -7F, 8.288F, 7.992F, 14F),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        PartDefinition p_placa0 = p_farol.addOrReplaceChild("placa0", CubeListBuilder.create(),
                PartPose.offsetAndRotation(0F, 3.6064F, 12.7446F, -0.8382F, 0F, -3.1416F));
        p_placa0.addOrReplaceChild("placa0_c0", CubeListBuilder.create().texOffs(128, 40).addBox(-6.8F, -1.8F, -2.45F, 13.6F, 1.8F, 4.9F),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        p_placa0.addOrReplaceChild("placa0_c1", CubeListBuilder.create().texOffs(49, 40).addBox(-0.7F, -0.4F, -2.45F, 1.4F, 3.4F, 4.9F),
                PartPose.offsetAndRotation(-6.5F, -1.2F, 0F, 0F, 0F, 0.32F));
        p_placa0.addOrReplaceChild("placa0_c2", CubeListBuilder.create().texOffs(49, 40).addBox(-0.7F, -0.4F, -2.45F, 1.4F, 3.4F, 4.9F),
                PartPose.offsetAndRotation(6.5F, -1.2F, 0F, 0F, 0F, -0.32F));
        PartDefinition p_placa1 = p_farol.addOrReplaceChild("placa1", CubeListBuilder.create(),
                PartPose.offsetAndRotation(0F, 5.8853F, 8.8536F, -0.2576F, 0F, -3.1416F));
        p_placa1.addOrReplaceChild("placa1_c0", CubeListBuilder.create().texOffs(128, 40).addBox(-6.8F, -1.8F, -2.45F, 13.6F, 1.8F, 4.9F),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        p_placa1.addOrReplaceChild("placa1_c1", CubeListBuilder.create().texOffs(49, 40).addBox(-0.7F, -0.4F, -2.45F, 1.4F, 3.4F, 4.9F),
                PartPose.offsetAndRotation(-6.5F, -1.2F, 0F, 0F, 0F, 0.32F));
        p_placa1.addOrReplaceChild("placa1_c2", CubeListBuilder.create().texOffs(49, 40).addBox(-0.7F, -0.4F, -2.45F, 1.4F, 3.4F, 4.9F),
                PartPose.offsetAndRotation(6.5F, -1.2F, 0F, 0F, 0F, -0.32F));
        PartDefinition p_placa2 = p_farol.addOrReplaceChild("placa2", CubeListBuilder.create(),
                PartPose.offsetAndRotation(0F, 5.9231F, 4.0949F, 0.2411F, 0F, -3.1416F));
        p_placa2.addOrReplaceChild("placa2_c0", CubeListBuilder.create().texOffs(128, 40).addBox(-6.8F, -1.8F, -2.45F, 13.6F, 1.8F, 4.9F),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        p_placa2.addOrReplaceChild("placa2_c1", CubeListBuilder.create().texOffs(49, 40).addBox(-0.7F, -0.4F, -2.45F, 1.4F, 3.4F, 4.9F),
                PartPose.offsetAndRotation(-6.5F, -1.2F, 0F, 0F, 0F, 0.32F));
        p_placa2.addOrReplaceChild("placa2_c2", CubeListBuilder.create().texOffs(49, 40).addBox(-0.7F, -0.4F, -2.45F, 1.4F, 3.4F, 4.9F),
                PartPose.offsetAndRotation(6.5F, -1.2F, 0F, 0F, 0F, -0.32F));
        PartDefinition p_placa3 = p_farol.addOrReplaceChild("placa3", CubeListBuilder.create(),
                PartPose.offsetAndRotation(0F, 3.854F, 0.2901F, 0.7862F, 0F, -3.1416F));
        p_placa3.addOrReplaceChild("placa3_c0", CubeListBuilder.create().texOffs(128, 40).addBox(-6.8F, -1.8F, -2.45F, 13.6F, 1.8F, 4.9F),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        p_placa3.addOrReplaceChild("placa3_c1", CubeListBuilder.create().texOffs(49, 40).addBox(-0.7F, -0.4F, -2.45F, 1.4F, 3.4F, 4.9F),
                PartPose.offsetAndRotation(-6.5F, -1.2F, 0F, 0F, 0F, 0.32F));
        p_placa3.addOrReplaceChild("placa3_c2", CubeListBuilder.create().texOffs(49, 40).addBox(-0.7F, -0.4F, -2.45F, 1.4F, 3.4F, 4.9F),
                PartPose.offsetAndRotation(6.5F, -1.2F, 0F, 0F, 0F, -0.32F));
        PartDefinition p_cabeza = p_cuerpo.addOrReplaceChild("cabeza", CubeListBuilder.create(),
                PartPose.offsetAndRotation(0F, 1.8F, -5.4F, 0.13F, 0F, 0F));
        p_cabeza.addOrReplaceChild("cabeza_c0", CubeListBuilder.create().texOffs(59, 25).addBox(-3.2F, -5F, -3.8F, 6.4F, 4.6F, 6.6F),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        p_cabeza.addOrReplaceChild("cabeza_c1", CubeListBuilder.create().texOffs(15, 50).addBox(-2.4F, -3.8F, -5F, 4.8F, 3F, 1.4F),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        p_cabeza.addOrReplaceChild("cabeza_c2", CubeListBuilder.create().texOffs(63, 40).addBox(-2.3F, -1.75F, -2.1F, 4.6F, 3.5F, 4.2F),
                PartPose.offsetAndRotation(-3.2F, -3F, -2F, 0F, 0F, 0F));
        p_cabeza.addOrReplaceChild("cabeza_c3", CubeListBuilder.create().texOffs(224, 25).addBox(-1.61F, -2.5F, -2.25F, 3.22F, 5F, 4.5F),
                PartPose.offsetAndRotation(-3.2F, -3F, -2F, 0F, 0F, 0F));
        p_cabeza.addOrReplaceChild("cabeza_c4", CubeListBuilder.create().texOffs(31, 40).addBox(-1.702F, -1.85F, -2.5F, 3.404F, 3.7F, 5F),
                PartPose.offsetAndRotation(-3.2F, -3F, -2F, 0F, 0F, 0F));
        p_cabeza.addOrReplaceChild("cabeza_c5", CubeListBuilder.create().texOffs(63, 40).addBox(-2.3F, -1.75F, -2.1F, 4.6F, 3.5F, 4.2F),
                PartPose.offsetAndRotation(3.2F, -3F, -2F, 0F, 0F, 0F));
        p_cabeza.addOrReplaceChild("cabeza_c6", CubeListBuilder.create().texOffs(224, 25).addBox(-1.61F, -2.5F, -2.25F, 3.22F, 5F, 4.5F),
                PartPose.offsetAndRotation(3.2F, -3F, -2F, 0F, 0F, 0F));
        p_cabeza.addOrReplaceChild("cabeza_c7", CubeListBuilder.create().texOffs(31, 40).addBox(-1.702F, -1.85F, -2.5F, 3.404F, 3.7F, 5F),
                PartPose.offsetAndRotation(3.2F, -3F, -2F, 0F, 0F, 0F));
        p_cabeza.addOrReplaceChild("cabeza_c8", CubeListBuilder.create().texOffs(0, 50).addBox(-2F, -0.8F, -5F, 4F, 1.6F, 2.6F),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        p_cabeza.addOrReplaceChild("cabeza_c9", CubeListBuilder.create().texOffs(24, 56).addBox(-0.4F, -2F, 0F, 0.8F, 2F, 0F),
                PartPose.offsetAndRotation(-1.5F, 1.2F, -5.1F, 0F, 0F, 0F));
        p_cabeza.addOrReplaceChild("cabeza_c10", CubeListBuilder.create().texOffs(27, 56).addBox(-0.4F, -1.6F, 0F, 0.8F, 1.6F, 0F),
                PartPose.offsetAndRotation(-0.5F, 0.8F, -5.1F, 0F, 0F, 0F));
        p_cabeza.addOrReplaceChild("cabeza_c11", CubeListBuilder.create().texOffs(27, 56).addBox(-0.4F, -1.6F, 0F, 0.8F, 1.6F, 0F),
                PartPose.offsetAndRotation(0.5F, 0.8F, -5.1F, 0F, 0F, 0F));
        p_cabeza.addOrReplaceChild("cabeza_c12", CubeListBuilder.create().texOffs(24, 56).addBox(-0.4F, -2F, 0F, 0.8F, 2F, 0F),
                PartPose.offsetAndRotation(1.5F, 1.2F, -5.1F, 0F, 0F, 0F));
        p_cabeza.addOrReplaceChild("cabeza_c13", CubeListBuilder.create().texOffs(206, 50).addBox(-0.3F, -0.3F, -1.8378F, 0.6F, 0.6F, 1.9378F),
                PartPose.offsetAndRotation(-1.5F, 0.4F, -4.6F, 0.8595F, 0.6545F, -0.1401F));
        p_cabeza.addOrReplaceChild("cabeza_c14", CubeListBuilder.create().texOffs(227, 50).addBox(-0.25F, -0.25F, -1.4601F, 0.5F, 0.5F, 1.5601F),
                PartPose.offsetAndRotation(-2F, 1.8F, -5.5F, 0.8137F, 0.2713F, -0.0506F));
        p_cabeza.addOrReplaceChild("cabeza_c15", CubeListBuilder.create().texOffs(206, 50).addBox(-0.3F, -0.3F, -1.8378F, 0.6F, 0.6F, 1.9378F),
                PartPose.offsetAndRotation(1.5F, 0.4F, -4.6F, 0.8595F, -0.6545F, 0.1401F));
        p_cabeza.addOrReplaceChild("cabeza_c16", CubeListBuilder.create().texOffs(227, 50).addBox(-0.25F, -0.25F, -1.4601F, 0.5F, 0.5F, 1.5601F),
                PartPose.offsetAndRotation(2F, 1.8F, -5.5F, 0.8137F, -0.2713F, 0.0506F));
        PartDefinition p_escudo = p_cabeza.addOrReplaceChild("escudo", CubeListBuilder.create(),
                PartPose.offsetAndRotation(0F, -5F, 1.6F, 0.22F, 0F, 0F));
        p_escudo.addOrReplaceChild("escudo_c0", CubeListBuilder.create().texOffs(107, 25).addBox(-6.2F, -1.4F, -4F, 12.4F, 1.4F, 9.6F),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        p_escudo.addOrReplaceChild("escudo_c1", CubeListBuilder.create().texOffs(0, 40).addBox(-3.8F, -2.3F, -2.8F, 7.6F, 1F, 7.4F),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        p_escudo.addOrReplaceChild("escudo_c2", CubeListBuilder.create().texOffs(159, 50).addBox(-5.4F, -1.2F, -5.4F, 10.8F, 1.3F, 1.4F),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        p_escudo.addOrReplaceChild("escudo_c3", CubeListBuilder.create().texOffs(185, 50).addBox(-4.2F, -1F, -6.6F, 8.4F, 1.2F, 1.2F),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        p_escudo.addOrReplaceChild("escudo_c4", CubeListBuilder.create().texOffs(239, 50).addBox(-2.6F, -0.8F, -7.5F, 5.2F, 1.1F, 0.9F),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        p_escudo.addOrReplaceChild("escudo_c5", CubeListBuilder.create().texOffs(86, 25).addBox(-0.6F, -0.4F, -3.8F, 1.2F, 3F, 8.4F),
                PartPose.offsetAndRotation(-6F, -0.6F, 0.8F, 0F, 0F, 0.55F));
        p_escudo.addOrReplaceChild("escudo_c6", CubeListBuilder.create().texOffs(86, 25).addBox(-0.6F, -0.4F, -3.8F, 1.2F, 3F, 8.4F),
                PartPose.offsetAndRotation(6F, -0.6F, 0.8F, 0F, 0F, -0.55F));
        PartDefinition p_quijada = p_cabeza.addOrReplaceChild("quijada", CubeListBuilder.create(),
                PartPose.offsetAndRotation(0F, 0.8F, -2.2F, 0.252F, 0F, 0F));
        p_quijada.addOrReplaceChild("quijada_c0", CubeListBuilder.create().texOffs(227, 40).addBox(-2.2F, 0F, -3.4F, 4.4F, 1.2F, 3.4F),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        p_quijada.addOrReplaceChild("quijada_c1", CubeListBuilder.create().texOffs(30, 56).addBox(-0.4F, -1.4F, 0F, 0.8F, 1.4F, 0F),
                PartPose.offsetAndRotation(-1F, -1.4F, -3.3F, -3.1416F, 0F, 0F));
        p_quijada.addOrReplaceChild("quijada_c2", CubeListBuilder.create().texOffs(30, 56).addBox(-0.4F, -1.4F, 0F, 0.8F, 1.4F, 0F),
                PartPose.offsetAndRotation(0F, -1.4F, -3.3F, -3.1416F, 0F, 0F));
        p_quijada.addOrReplaceChild("quijada_c3", CubeListBuilder.create().texOffs(30, 56).addBox(-0.4F, -1.4F, 0F, 0.8F, 1.4F, 0F),
                PartPose.offsetAndRotation(1F, -1.4F, -3.3F, -3.1416F, 0F, 0F));
        PartDefinition p_mandibula_d = p_cabeza.addOrReplaceChild("mandibula_d", CubeListBuilder.create(),
                PartPose.offsetAndRotation(-2.4F, -0.4F, -4.4F, 0F, 0F, 0F));
        p_mandibula_d.addOrReplaceChild("mandibula_d_c0", CubeListBuilder.create().texOffs(151, 50).addBox(-0.55F, -0.55F, -1.85F, 1.1F, 1.1F, 2F),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0.2722F, 0.4465F, -0.0872F));
        p_mandibula_d.addOrReplaceChild("mandibula_d_c1", CubeListBuilder.create().texOffs(213, 50).addBox(-0.425F, -0.425F, -1.85F, 0.85F, 0.85F, 2F),
                PartPose.offsetAndRotation(-0.6646F, 0.5169F, -1.4769F, 0.2903F, -0.041F, 0.0075F));
        p_mandibula_d.addOrReplaceChild("mandibula_d_c2", CubeListBuilder.create().texOffs(220, 50).addBox(-0.3F, -0.3F, -1.85F, 0.6F, 0.6F, 2F),
                PartPose.offsetAndRotation(-0.6014F, 1.0039F, -3.1044F, 0.1252F, -0.6211F, 0.1306F));
        PartDefinition p_mandibula_i = p_cabeza.addOrReplaceChild("mandibula_i", CubeListBuilder.create(),
                PartPose.offsetAndRotation(2.4F, -0.4F, -4.4F, 0F, 0F, 0F));
        p_mandibula_i.addOrReplaceChild("mandibula_i_c0", CubeListBuilder.create().texOffs(151, 50).addBox(-0.55F, -0.55F, -1.85F, 1.1F, 1.1F, 2F),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0.2722F, -0.4465F, 0.0872F));
        p_mandibula_i.addOrReplaceChild("mandibula_i_c1", CubeListBuilder.create().texOffs(213, 50).addBox(-0.425F, -0.425F, -1.85F, 0.85F, 0.85F, 2F),
                PartPose.offsetAndRotation(0.6646F, 0.5169F, -1.4769F, 0.2903F, 0.041F, -0.0075F));
        p_mandibula_i.addOrReplaceChild("mandibula_i_c2", CubeListBuilder.create().texOffs(220, 50).addBox(-0.3F, -0.3F, -1.85F, 0.6F, 0.6F, 2F),
                PartPose.offsetAndRotation(0.6014F, 1.0039F, -3.1044F, 0.1252F, 0.6211F, -0.1306F));
        PartDefinition p_antena_d = p_cabeza.addOrReplaceChild("antena_d", CubeListBuilder.create(),
                PartPose.offsetAndRotation(-1F, -3.8F, -4.8F, 0F, 0F, 0F));
        p_antena_d.addOrReplaceChild("antena_d_c0", CubeListBuilder.create().texOffs(70, 50).addBox(-0.475F, -0.475F, -2.5F, 0.95F, 0.95F, 2.6F),
                PartPose.offsetAndRotation(0F, 0F, 0F, -0.8493F, 0.583F, -0.1203F));
        p_antena_d.addOrReplaceChild("antena_d_c1", CubeListBuilder.create().texOffs(79, 50).addBox(-0.4545F, -0.4545F, -2.5F, 0.9091F, 0.9091F, 2.6F),
                PartPose.offsetAndRotation(-1.0827F, -1.6842F, -1.3233F, -1.1381F, 0.8934F, -0.2282F));
        p_antena_d.addOrReplaceChild("antena_d_c2", CubeListBuilder.create().texOffs(20, 56).addBox(-0.66F, -1.0964F, 0F, 1.32F, 1.0964F, 0F),
                PartPose.offsetAndRotation(-2.421F, -1.8397F, -1.3737F, 2.9734F, 0.266F, -2.1445F));
        p_antena_d.addOrReplaceChild("antena_d_c3", CubeListBuilder.create().texOffs(50, 50).addBox(-0.4341F, -0.4341F, -3.1F, 0.8682F, 0.8682F, 3.2F),
                PartPose.offsetAndRotation(-2.3394F, -3.6292F, -1.9541F, -1.9857F, 1.3564F, -0.9895F));
        p_antena_d.addOrReplaceChild("antena_d_c4", CubeListBuilder.create().texOffs(0, 56).addBox(-0.825F, -1.0765F, 0F, 1.65F, 1.0765F, 0F),
                PartPose.offsetAndRotation(-3.7591F, -3.9518F, -1.9208F, -3.0851F, -0.0859F, -2.1539F));
        p_antena_d.addOrReplaceChild("antena_d_c5", CubeListBuilder.create().texOffs(60, 50).addBox(-0.4136F, -0.4136F, -3.1F, 0.8273F, 0.8273F, 3.2F),
                PartPose.offsetAndRotation(-3.9851F, -6.1242F, -1.6968F, 2.5571F, 1.0421F, -2.8248F));
        p_antena_d.addOrReplaceChild("antena_d_c6", CubeListBuilder.create().texOffs(5, 56).addBox(-0.825F, -1.034F, 0F, 1.65F, 1.034F, 0F),
                PartPose.offsetAndRotation(-5.3507F, -6.4799F, -1.497F, -2.8613F, -0.4342F, -2.171F));
        p_antena_d.addOrReplaceChild("antena_d_c7", CubeListBuilder.create().texOffs(88, 50).addBox(-0.3932F, -0.3932F, -3.1F, 0.7864F, 0.7864F, 3.2F),
                PartPose.offsetAndRotation(-5.5223F, -8.3702F, -0.4348F, 2.5848F, 0.6413F, -3.0053F));
        p_antena_d.addOrReplaceChild("antena_d_c8", CubeListBuilder.create().texOffs(33, 56).addBox(-0.825F, -0.9918F, 0F, 1.65F, 0.9918F, 0F),
                PartPose.offsetAndRotation(-6.8036F, -8.7322F, -0.0192F, -2.6818F, -0.7481F, -2.2F));
        p_antena_d.addOrReplaceChild("antena_d_c9", CubeListBuilder.create().texOffs(97, 50).addBox(-0.3727F, -0.3727F, -3.1F, 0.7455F, 0.7455F, 3.2F),
                PartPose.offsetAndRotation(-6.8165F, -10.148F, 1.606F, 2.7477F, 0.4062F, -3.0632F));
        p_antena_d.addOrReplaceChild("antena_d_c10", CubeListBuilder.create().texOffs(38, 56).addBox(-0.825F, -0.9499F, 0F, 1.65F, 0.9499F, 0F),
                PartPose.offsetAndRotation(-7.9896F, -10.4527F, 2.2346F, -2.5387F, -1.0127F, -2.2525F));
        p_antena_d.addOrReplaceChild("antena_d_c11", CubeListBuilder.create().texOffs(106, 50).addBox(-0.3523F, -0.3523F, -3.1F, 0.7045F, 0.7045F, 3.2F),
                PartPose.offsetAndRotation(-7.8176F, -11.3816F, 4.1508F, 2.9131F, 0.2615F, -3.0929F));
        p_antena_d.addOrReplaceChild("antena_d_c12", CubeListBuilder.create().texOffs(43, 56).addBox(-0.825F, -0.9083F, 0F, 1.65F, 0.9083F, 0F),
                PartPose.offsetAndRotation(-8.8731F, -11.5831F, 4.9458F, -2.3825F, -1.2253F, -2.3603F));
        p_antena_d.addOrReplaceChild("antena_d_c13", CubeListBuilder.create().texOffs(115, 50).addBox(-0.3318F, -0.3318F, -3.1F, 0.6636F, 0.6636F, 3.2F),
                PartPose.offsetAndRotation(-8.5391F, -12.0971F, 6.9734F, 3.057F, 0.1655F, -3.1112F));
        p_antena_d.addOrReplaceChild("antena_d_c14", CubeListBuilder.create().texOffs(48, 56).addBox(-0.825F, -0.8671F, 0F, 1.65F, 0.8671F, 0F),
                PartPose.offsetAndRotation(-9.4802F, -12.1795F, 7.8796F, -2.0837F, -1.3851F, -2.6361F));
        p_antena_d.addOrReplaceChild("antena_d_c15", CubeListBuilder.create().texOffs(124, 50).addBox(-0.3114F, -0.3114F, -3.1F, 0.6227F, 0.6227F, 3.2F),
                PartPose.offsetAndRotation(-9.0236F, -12.3653F, 9.9219F, -3.1063F, 0.0985F, -3.1236F));
        p_antena_d.addOrReplaceChild("antena_d_c16", CubeListBuilder.create().texOffs(53, 56).addBox(-0.825F, -0.8264F, 0F, 1.65F, 0.8264F, 0F),
                PartPose.offsetAndRotation(-9.8602F, -12.3325F, 10.8934F, -1.2421F, -1.4662F, 2.8146F));
        p_antena_d.addOrReplaceChild("antena_d_c17", CubeListBuilder.create().texOffs(133, 50).addBox(-0.2909F, -0.2909F, -3.1F, 0.5818F, 0.5818F, 3.2F),
                PartPose.offsetAndRotation(-9.3202F, -12.2647F, 12.9055F, -3.0076F, 0.0503F, -3.1324F));
        p_antena_d.addOrReplaceChild("antena_d_c18", CubeListBuilder.create().texOffs(142, 50).addBox(-0.2705F, -0.2705F, -3.1F, 0.5409F, 0.5409F, 3.2F),
                PartPose.offsetAndRotation(-9.4735F, -11.8652F, 15.8748F, -2.926F, 0.0152F, -3.1388F));
        PartDefinition p_antena_i = p_cabeza.addOrReplaceChild("antena_i", CubeListBuilder.create(),
                PartPose.offsetAndRotation(1F, -3.8F, -4.8F, 0F, 0F, 0F));
        p_antena_i.addOrReplaceChild("antena_i_c0", CubeListBuilder.create().texOffs(70, 50).addBox(-0.475F, -0.475F, -2.5F, 0.95F, 0.95F, 2.6F),
                PartPose.offsetAndRotation(0F, 0F, 0F, -0.8493F, -0.583F, 0.1203F));
        p_antena_i.addOrReplaceChild("antena_i_c1", CubeListBuilder.create().texOffs(79, 50).addBox(-0.4545F, -0.4545F, -2.5F, 0.9091F, 0.9091F, 2.6F),
                PartPose.offsetAndRotation(1.0827F, -1.6842F, -1.3233F, -1.1381F, -0.8934F, 0.2282F));
        p_antena_i.addOrReplaceChild("antena_i_c2", CubeListBuilder.create().texOffs(20, 56).addBox(-0.66F, -1.0964F, 0F, 1.32F, 1.0964F, 0F),
                PartPose.offsetAndRotation(2.421F, -1.8397F, -1.3737F, 0.1682F, 0.266F, -0.9971F));
        p_antena_i.addOrReplaceChild("antena_i_c3", CubeListBuilder.create().texOffs(50, 50).addBox(-0.4341F, -0.4341F, -3.1F, 0.8682F, 0.8682F, 3.2F),
                PartPose.offsetAndRotation(2.3394F, -3.6292F, -1.9541F, -1.9857F, -1.3564F, 0.9895F));
        p_antena_i.addOrReplaceChild("antena_i_c4", CubeListBuilder.create().texOffs(0, 56).addBox(-0.825F, -1.0765F, 0F, 1.65F, 1.0765F, 0F),
                PartPose.offsetAndRotation(3.7591F, -3.9518F, -1.9208F, -0.0565F, -0.0859F, -0.9877F));
        p_antena_i.addOrReplaceChild("antena_i_c5", CubeListBuilder.create().texOffs(60, 50).addBox(-0.4136F, -0.4136F, -3.1F, 0.8273F, 0.8273F, 3.2F),
                PartPose.offsetAndRotation(3.9851F, -6.1242F, -1.6968F, 2.5571F, -1.0421F, 2.8248F));
        p_antena_i.addOrReplaceChild("antena_i_c6", CubeListBuilder.create().texOffs(5, 56).addBox(-0.825F, -1.034F, 0F, 1.65F, 1.034F, 0F),
                PartPose.offsetAndRotation(5.3507F, -6.4799F, -1.497F, -0.2803F, -0.4342F, -0.9706F));
        p_antena_i.addOrReplaceChild("antena_i_c7", CubeListBuilder.create().texOffs(88, 50).addBox(-0.3932F, -0.3932F, -3.1F, 0.7864F, 0.7864F, 3.2F),
                PartPose.offsetAndRotation(5.5223F, -8.3702F, -0.4348F, 2.5848F, -0.6413F, 3.0053F));
        p_antena_i.addOrReplaceChild("antena_i_c8", CubeListBuilder.create().texOffs(33, 56).addBox(-0.825F, -0.9918F, 0F, 1.65F, 0.9918F, 0F),
                PartPose.offsetAndRotation(6.8036F, -8.7322F, -0.0192F, -0.4598F, -0.7481F, -0.9415F));
        p_antena_i.addOrReplaceChild("antena_i_c9", CubeListBuilder.create().texOffs(97, 50).addBox(-0.3727F, -0.3727F, -3.1F, 0.7455F, 0.7455F, 3.2F),
                PartPose.offsetAndRotation(6.8165F, -10.148F, 1.606F, 2.7477F, -0.4062F, 3.0632F));
        p_antena_i.addOrReplaceChild("antena_i_c10", CubeListBuilder.create().texOffs(38, 56).addBox(-0.825F, -0.9499F, 0F, 1.65F, 0.9499F, 0F),
                PartPose.offsetAndRotation(7.9896F, -10.4527F, 2.2346F, -0.6029F, -1.0127F, -0.8891F));
        p_antena_i.addOrReplaceChild("antena_i_c11", CubeListBuilder.create().texOffs(106, 50).addBox(-0.3523F, -0.3523F, -3.1F, 0.7045F, 0.7045F, 3.2F),
                PartPose.offsetAndRotation(7.8176F, -11.3816F, 4.1508F, 2.9131F, -0.2615F, 3.0929F));
        p_antena_i.addOrReplaceChild("antena_i_c12", CubeListBuilder.create().texOffs(43, 56).addBox(-0.825F, -0.9083F, 0F, 1.65F, 0.9083F, 0F),
                PartPose.offsetAndRotation(8.8731F, -11.5831F, 4.9458F, -0.7591F, -1.2253F, -0.7813F));
        p_antena_i.addOrReplaceChild("antena_i_c13", CubeListBuilder.create().texOffs(115, 50).addBox(-0.3318F, -0.3318F, -3.1F, 0.6636F, 0.6636F, 3.2F),
                PartPose.offsetAndRotation(8.5391F, -12.0971F, 6.9734F, 3.057F, -0.1655F, 3.1112F));
        p_antena_i.addOrReplaceChild("antena_i_c14", CubeListBuilder.create().texOffs(48, 56).addBox(-0.825F, -0.8671F, 0F, 1.65F, 0.8671F, 0F),
                PartPose.offsetAndRotation(9.4802F, -12.1795F, 7.8796F, -1.0579F, -1.3851F, -0.5055F));
        p_antena_i.addOrReplaceChild("antena_i_c15", CubeListBuilder.create().texOffs(124, 50).addBox(-0.3114F, -0.3114F, -3.1F, 0.6227F, 0.6227F, 3.2F),
                PartPose.offsetAndRotation(9.0236F, -12.3653F, 9.9219F, -3.1063F, -0.0985F, 3.1236F));
        p_antena_i.addOrReplaceChild("antena_i_c16", CubeListBuilder.create().texOffs(53, 56).addBox(-0.825F, -0.8264F, 0F, 1.65F, 0.8264F, 0F),
                PartPose.offsetAndRotation(9.8602F, -12.3325F, 10.8934F, -1.8995F, -1.4662F, 0.327F));
        p_antena_i.addOrReplaceChild("antena_i_c17", CubeListBuilder.create().texOffs(133, 50).addBox(-0.2909F, -0.2909F, -3.1F, 0.5818F, 0.5818F, 3.2F),
                PartPose.offsetAndRotation(9.3202F, -12.2647F, 12.9055F, -3.0076F, -0.0503F, 3.1324F));
        p_antena_i.addOrReplaceChild("antena_i_c18", CubeListBuilder.create().texOffs(142, 50).addBox(-0.2705F, -0.2705F, -3.1F, 0.5409F, 0.5409F, 3.2F),
                PartPose.offsetAndRotation(9.4735F, -11.8652F, 15.8748F, -2.926F, -0.0152F, 3.1388F));
        PartDefinition p_pata_dd = p_cuerpo.addOrReplaceChild("pata_dd", CubeListBuilder.create(),
                PartPose.offsetAndRotation(-3.8F, 2F, -2.6F, -0.05F, 0F, 0F));
        p_pata_dd.addOrReplaceChild("pata_dd_c0", CubeListBuilder.create().texOffs(214, 40).addBox(-1.1F, -1.1F, -3.0747F, 2.2F, 2.2F, 3.7347F),
                PartPose.offsetAndRotation(0F, 0F, 0F, -0.029F, 0.8171F, 0F));
        p_pata_dd.addOrReplaceChild("pata_dd_c1", CubeListBuilder.create().texOffs(29, 50).addBox(-0.792F, -0.792F, -2.4509F, 1.584F, 1.584F, 2.9261F),
                PartPose.offsetAndRotation(-1.76F, -0.0701F, -1.6518F, -0.029F, 0.8171F, 0F));
        PartDefinition p_pata_dd_canilla = p_pata_dd.addOrReplaceChild("pata_dd_canilla", CubeListBuilder.create(),
                PartPose.offsetAndRotation(-3.2F, -0.1274F, -3.0032F, 0F, 0F, 0F));
        p_pata_dd_canilla.addOrReplaceChild("pata_dd_canilla_c0", CubeListBuilder.create().texOffs(203, 25).addBox(-0.7F, -0.7F, -7.8153F, 1.4F, 1.4F, 8.2353F),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0.9943F, -0.1244F, 0F));
        p_pata_dd_canilla.addOrReplaceChild("pata_dd_canilla_c1", CubeListBuilder.create().texOffs(233, 50).addBox(-0.45F, -0.45F, -1.0167F, 0.9F, 0.9F, 1.1667F),
                PartPose.offsetAndRotation(0.5F, 6.2F, -4F, -0.245F, 1.2308F, 0F));
        p_pata_dd_canilla.addOrReplaceChild("pata_dd_canilla_c2", CubeListBuilder.create().texOffs(10, 56).addBox(-0.375F, -0.375F, -1.0167F, 0.75F, 0.75F, 1.1667F),
                PartPose.offsetAndRotation(-0.2927F, 5.9898F, -4.2804F, 0.2954F, 1.2308F, 0F));
        p_pata_dd_canilla.addOrReplaceChild("pata_dd_canilla_c3", CubeListBuilder.create().texOffs(15, 56).addBox(-0.3F, -0.3F, -1.0167F, 0.6F, 0.6F, 1.1667F),
                PartPose.offsetAndRotation(-1.0743F, 6.2421F, -4.5569F, 0.67F, 1.2308F, 0F));
        p_pata_dd_canilla.addOrReplaceChild("pata_dd_canilla_c4", CubeListBuilder.create().texOffs(233, 50).addBox(-0.45F, -0.45F, -1.0167F, 0.9F, 0.9F, 1.1667F),
                PartPose.offsetAndRotation(0.5F, 6.2F, -4F, -0.245F, 0.6808F, 0F));
        p_pata_dd_canilla.addOrReplaceChild("pata_dd_canilla_c5", CubeListBuilder.create().texOffs(10, 56).addBox(-0.375F, -0.375F, -1.0167F, 0.75F, 0.75F, 1.1667F),
                PartPose.offsetAndRotation(-0.0292F, 5.9898F, -4.6533F, 0.2954F, 0.6808F, 0F));
        p_pata_dd_canilla.addOrReplaceChild("pata_dd_canilla_c6", CubeListBuilder.create().texOffs(15, 56).addBox(-0.3F, -0.3F, -1.0167F, 0.6F, 0.6F, 1.1667F),
                PartPose.offsetAndRotation(-0.5511F, 6.2421F, -5.2976F, 0.67F, 0.6808F, 0F));
        p_pata_dd_canilla.addOrReplaceChild("pata_dd_canilla_c7", CubeListBuilder.create().texOffs(233, 50).addBox(-0.45F, -0.45F, -1.0167F, 0.9F, 0.9F, 1.1667F),
                PartPose.offsetAndRotation(0.5F, 6.2F, -4F, -0.245F, 0.1308F, 0F));
        p_pata_dd_canilla.addOrReplaceChild("pata_dd_canilla_c8", CubeListBuilder.create().texOffs(10, 56).addBox(-0.375F, -0.375F, -1.0167F, 0.75F, 0.75F, 1.1667F),
                PartPose.offsetAndRotation(0.3903F, 5.9898F, -4.8336F, 0.2954F, 0.1308F, 0F));
        p_pata_dd_canilla.addOrReplaceChild("pata_dd_canilla_c9", CubeListBuilder.create().texOffs(15, 56).addBox(-0.3F, -0.3F, -1.0167F, 0.6F, 0.6F, 1.1667F),
                PartPose.offsetAndRotation(0.2822F, 6.2421F, -5.6556F, 0.67F, 0.1308F, 0F));
        PartDefinition p_pata_td = p_cuerpo.addOrReplaceChild("pata_td", CubeListBuilder.create(),
                PartPose.offsetAndRotation(-4F, 1.4F, 2.6F, -0.05F, 0F, 0F));
        p_pata_td.addOrReplaceChild("pata_td_c0", CubeListBuilder.create().texOffs(152, 25).addBox(-1.6F, -1.6F, -6.227F, 3.2F, 3.2F, 7.187F),
                PartPose.offsetAndRotation(0F, 0F, 0F, 2.1954F, 0.9333F, 3.1416F));
        p_pata_td.addOrReplaceChild("pata_td_c1", CubeListBuilder.create().texOffs(82, 40).addBox(-1.152F, -1.152F, -5.0006F, 2.304F, 2.304F, 5.6918F),
                PartPose.offsetAndRotation(-2.475F, -4.2726F, 1.8333F, 2.1954F, 0.9333F, -3.1416F));
        PartDefinition p_pata_td_canilla = p_pata_td.addOrReplaceChild("pata_td_canilla", CubeListBuilder.create(),
                PartPose.offsetAndRotation(-4.5F, -7.7683F, 3.3333F, 0F, 0F, 0F));
        p_pata_td_canilla.addOrReplaceChild("pata_td_canilla_c0", CubeListBuilder.create().texOffs(135, 0).addBox(-0.75F, -0.75F, -15.2854F, 1.5F, 1.5F, 15.7354F),
                PartPose.offsetAndRotation(0F, 0F, 0F, 1.4356F, 0F, 0F));
        p_pata_td_canilla.addOrReplaceChild("pata_td_canilla_c1", CubeListBuilder.create().texOffs(233, 50).addBox(-0.45F, -0.45F, -1.0167F, 0.9F, 0.9F, 1.1667F),
                PartPose.offsetAndRotation(0F, 14.7F, -2F, -0.245F, 1.4832F, 0F));
        p_pata_td_canilla.addOrReplaceChild("pata_td_canilla_c2", CubeListBuilder.create().texOffs(10, 56).addBox(-0.375F, -0.375F, -1.0167F, 0.75F, 0.75F, 1.1667F),
                PartPose.offsetAndRotation(-0.8376F, 14.4898F, -2.0735F, 0.2954F, 1.4832F, 0F));
        p_pata_td_canilla.addOrReplaceChild("pata_td_canilla_c3", CubeListBuilder.create().texOffs(15, 56).addBox(-0.3F, -0.3F, -1.0167F, 0.6F, 0.6F, 1.1667F),
                PartPose.offsetAndRotation(-1.6635F, 14.7421F, -2.146F, 0.67F, 1.4832F, 0F));
        p_pata_td_canilla.addOrReplaceChild("pata_td_canilla_c4", CubeListBuilder.create().texOffs(233, 50).addBox(-0.45F, -0.45F, -1.0167F, 0.9F, 0.9F, 1.1667F),
                PartPose.offsetAndRotation(0F, 14.7F, -2F, -0.245F, 0.9332F, 0F));
        p_pata_td_canilla.addOrReplaceChild("pata_td_canilla_c5", CubeListBuilder.create().texOffs(10, 56).addBox(-0.375F, -0.375F, -1.0167F, 0.75F, 0.75F, 1.1667F),
                PartPose.offsetAndRotation(-0.6756F, 14.4898F, -2.5005F, 0.2954F, 0.9332F, 0F));
        p_pata_td_canilla.addOrReplaceChild("pata_td_canilla_c6", CubeListBuilder.create().texOffs(15, 56).addBox(-0.3F, -0.3F, -1.0167F, 0.6F, 0.6F, 1.1667F),
                PartPose.offsetAndRotation(-1.3419F, 14.7421F, -2.994F, 0.67F, 0.9332F, 0F));
        p_pata_td_canilla.addOrReplaceChild("pata_td_canilla_c7", CubeListBuilder.create().texOffs(233, 50).addBox(-0.45F, -0.45F, -1.0167F, 0.9F, 0.9F, 1.1667F),
                PartPose.offsetAndRotation(0F, 14.7F, -2F, -0.245F, 0.3832F, 0F));
        p_pata_td_canilla.addOrReplaceChild("pata_td_canilla_c8", CubeListBuilder.create().texOffs(10, 56).addBox(-0.375F, -0.375F, -1.0167F, 0.75F, 0.75F, 1.1667F),
                PartPose.offsetAndRotation(-0.3144F, 14.4898F, -2.7798F, 0.2954F, 0.3832F, 0F));
        p_pata_td_canilla.addOrReplaceChild("pata_td_canilla_c9", CubeListBuilder.create().texOffs(15, 56).addBox(-0.3F, -0.3F, -1.0167F, 0.6F, 0.6F, 1.1667F),
                PartPose.offsetAndRotation(-0.6244F, 14.7421F, -3.5488F, 0.67F, 0.3832F, 0F));
        PartDefinition p_pata_di = p_cuerpo.addOrReplaceChild("pata_di", CubeListBuilder.create(),
                PartPose.offsetAndRotation(3.8F, 2F, -2.6F, -0.05F, 0F, 0F));
        p_pata_di.addOrReplaceChild("pata_di_c0", CubeListBuilder.create().texOffs(214, 40).addBox(-1.1F, -1.1F, -3.0747F, 2.2F, 2.2F, 3.7347F),
                PartPose.offsetAndRotation(0F, 0F, 0F, -0.029F, -0.8171F, 0F));
        p_pata_di.addOrReplaceChild("pata_di_c1", CubeListBuilder.create().texOffs(29, 50).addBox(-0.792F, -0.792F, -2.4509F, 1.584F, 1.584F, 2.9261F),
                PartPose.offsetAndRotation(1.76F, -0.0701F, -1.6518F, -0.029F, -0.8171F, 0F));
        PartDefinition p_pata_di_canilla = p_pata_di.addOrReplaceChild("pata_di_canilla", CubeListBuilder.create(),
                PartPose.offsetAndRotation(3.2F, -0.1274F, -3.0032F, 0F, 0F, 0F));
        p_pata_di_canilla.addOrReplaceChild("pata_di_canilla_c0", CubeListBuilder.create().texOffs(203, 25).addBox(-0.7F, -0.7F, -7.8153F, 1.4F, 1.4F, 8.2353F),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0.9943F, 0.1244F, 0F));
        p_pata_di_canilla.addOrReplaceChild("pata_di_canilla_c1", CubeListBuilder.create().texOffs(233, 50).addBox(-0.45F, -0.45F, -1.0167F, 0.9F, 0.9F, 1.1667F),
                PartPose.offsetAndRotation(-0.5F, 6.2F, -4F, -0.245F, -0.1308F, 0F));
        p_pata_di_canilla.addOrReplaceChild("pata_di_canilla_c2", CubeListBuilder.create().texOffs(10, 56).addBox(-0.375F, -0.375F, -1.0167F, 0.75F, 0.75F, 1.1667F),
                PartPose.offsetAndRotation(-0.3903F, 5.9898F, -4.8336F, 0.2954F, -0.1308F, 0F));
        p_pata_di_canilla.addOrReplaceChild("pata_di_canilla_c3", CubeListBuilder.create().texOffs(15, 56).addBox(-0.3F, -0.3F, -1.0167F, 0.6F, 0.6F, 1.1667F),
                PartPose.offsetAndRotation(-0.2822F, 6.2421F, -5.6556F, 0.67F, -0.1308F, 0F));
        p_pata_di_canilla.addOrReplaceChild("pata_di_canilla_c4", CubeListBuilder.create().texOffs(233, 50).addBox(-0.45F, -0.45F, -1.0167F, 0.9F, 0.9F, 1.1667F),
                PartPose.offsetAndRotation(-0.5F, 6.2F, -4F, -0.245F, -0.6808F, 0F));
        p_pata_di_canilla.addOrReplaceChild("pata_di_canilla_c5", CubeListBuilder.create().texOffs(10, 56).addBox(-0.375F, -0.375F, -1.0167F, 0.75F, 0.75F, 1.1667F),
                PartPose.offsetAndRotation(0.0292F, 5.9898F, -4.6533F, 0.2954F, -0.6808F, 0F));
        p_pata_di_canilla.addOrReplaceChild("pata_di_canilla_c6", CubeListBuilder.create().texOffs(15, 56).addBox(-0.3F, -0.3F, -1.0167F, 0.6F, 0.6F, 1.1667F),
                PartPose.offsetAndRotation(0.5511F, 6.2421F, -5.2976F, 0.67F, -0.6808F, 0F));
        p_pata_di_canilla.addOrReplaceChild("pata_di_canilla_c7", CubeListBuilder.create().texOffs(233, 50).addBox(-0.45F, -0.45F, -1.0167F, 0.9F, 0.9F, 1.1667F),
                PartPose.offsetAndRotation(-0.5F, 6.2F, -4F, -0.245F, -1.2308F, 0F));
        p_pata_di_canilla.addOrReplaceChild("pata_di_canilla_c8", CubeListBuilder.create().texOffs(10, 56).addBox(-0.375F, -0.375F, -1.0167F, 0.75F, 0.75F, 1.1667F),
                PartPose.offsetAndRotation(0.2927F, 5.9898F, -4.2804F, 0.2954F, -1.2308F, 0F));
        p_pata_di_canilla.addOrReplaceChild("pata_di_canilla_c9", CubeListBuilder.create().texOffs(15, 56).addBox(-0.3F, -0.3F, -1.0167F, 0.6F, 0.6F, 1.1667F),
                PartPose.offsetAndRotation(1.0743F, 6.2421F, -4.5569F, 0.67F, -1.2308F, 0F));
        PartDefinition p_pata_ti = p_cuerpo.addOrReplaceChild("pata_ti", CubeListBuilder.create(),
                PartPose.offsetAndRotation(4F, 1.4F, 2.6F, -0.05F, 0F, 0F));
        p_pata_ti.addOrReplaceChild("pata_ti_c0", CubeListBuilder.create().texOffs(152, 25).addBox(-1.6F, -1.6F, -6.227F, 3.2F, 3.2F, 7.187F),
                PartPose.offsetAndRotation(0F, 0F, 0F, 2.1954F, -0.9333F, -3.1416F));
        p_pata_ti.addOrReplaceChild("pata_ti_c1", CubeListBuilder.create().texOffs(82, 40).addBox(-1.152F, -1.152F, -5.0006F, 2.304F, 2.304F, 5.6918F),
                PartPose.offsetAndRotation(2.475F, -4.2726F, 1.8333F, 2.1954F, -0.9333F, 3.1416F));
        PartDefinition p_pata_ti_canilla = p_pata_ti.addOrReplaceChild("pata_ti_canilla", CubeListBuilder.create(),
                PartPose.offsetAndRotation(4.5F, -7.7683F, 3.3333F, 0F, 0F, 0F));
        p_pata_ti_canilla.addOrReplaceChild("pata_ti_canilla_c0", CubeListBuilder.create().texOffs(135, 0).addBox(-0.75F, -0.75F, -15.2854F, 1.5F, 1.5F, 15.7354F),
                PartPose.offsetAndRotation(0F, 0F, 0F, 1.4356F, 0F, 0F));
        p_pata_ti_canilla.addOrReplaceChild("pata_ti_canilla_c1", CubeListBuilder.create().texOffs(233, 50).addBox(-0.45F, -0.45F, -1.0167F, 0.9F, 0.9F, 1.1667F),
                PartPose.offsetAndRotation(0F, 14.7F, -2F, -0.245F, -0.3832F, 0F));
        p_pata_ti_canilla.addOrReplaceChild("pata_ti_canilla_c2", CubeListBuilder.create().texOffs(10, 56).addBox(-0.375F, -0.375F, -1.0167F, 0.75F, 0.75F, 1.1667F),
                PartPose.offsetAndRotation(0.3144F, 14.4898F, -2.7798F, 0.2954F, -0.3832F, 0F));
        p_pata_ti_canilla.addOrReplaceChild("pata_ti_canilla_c3", CubeListBuilder.create().texOffs(15, 56).addBox(-0.3F, -0.3F, -1.0167F, 0.6F, 0.6F, 1.1667F),
                PartPose.offsetAndRotation(0.6244F, 14.7421F, -3.5488F, 0.67F, -0.3832F, 0F));
        p_pata_ti_canilla.addOrReplaceChild("pata_ti_canilla_c4", CubeListBuilder.create().texOffs(233, 50).addBox(-0.45F, -0.45F, -1.0167F, 0.9F, 0.9F, 1.1667F),
                PartPose.offsetAndRotation(0F, 14.7F, -2F, -0.245F, -0.9332F, 0F));
        p_pata_ti_canilla.addOrReplaceChild("pata_ti_canilla_c5", CubeListBuilder.create().texOffs(10, 56).addBox(-0.375F, -0.375F, -1.0167F, 0.75F, 0.75F, 1.1667F),
                PartPose.offsetAndRotation(0.6756F, 14.4898F, -2.5005F, 0.2954F, -0.9332F, 0F));
        p_pata_ti_canilla.addOrReplaceChild("pata_ti_canilla_c6", CubeListBuilder.create().texOffs(15, 56).addBox(-0.3F, -0.3F, -1.0167F, 0.6F, 0.6F, 1.1667F),
                PartPose.offsetAndRotation(1.3419F, 14.7421F, -2.994F, 0.67F, -0.9332F, 0F));
        p_pata_ti_canilla.addOrReplaceChild("pata_ti_canilla_c7", CubeListBuilder.create().texOffs(233, 50).addBox(-0.45F, -0.45F, -1.0167F, 0.9F, 0.9F, 1.1667F),
                PartPose.offsetAndRotation(0F, 14.7F, -2F, -0.245F, -1.4832F, 0F));
        p_pata_ti_canilla.addOrReplaceChild("pata_ti_canilla_c8", CubeListBuilder.create().texOffs(10, 56).addBox(-0.375F, -0.375F, -1.0167F, 0.75F, 0.75F, 1.1667F),
                PartPose.offsetAndRotation(0.8376F, 14.4898F, -2.0735F, 0.2954F, -1.4832F, 0F));
        p_pata_ti_canilla.addOrReplaceChild("pata_ti_canilla_c9", CubeListBuilder.create().texOffs(15, 56).addBox(-0.3F, -0.3F, -1.0167F, 0.6F, 0.6F, 1.1667F),
                PartPose.offsetAndRotation(1.6635F, 14.7421F, -2.146F, 0.67F, -1.4832F, 0F));
        return LayerDefinition.create(malla, 256, 64);
    }
}
