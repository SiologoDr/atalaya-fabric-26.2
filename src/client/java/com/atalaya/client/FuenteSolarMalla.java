package com.atalaya.client;

import net.minecraft.client.model.geom.PartPose;
import net.minecraft.client.model.geom.builders.CubeDeformation;
import net.minecraft.client.model.geom.builders.CubeListBuilder;
import net.minecraft.client.model.geom.builders.LayerDefinition;
import net.minecraft.client.model.geom.builders.MeshDefinition;
import net.minecraft.client.model.geom.builders.PartDefinition;

/**
 * Las fuentes solares de Novilis. GENERADO por materiales/generadores/novilis_props.py:
 * no se edita a mano.
 *
 * Escala x1, la base en y = 24: mide 80 px = 5 bloques. El sol flota con su centro en
 * y = -55 (lo pinta el renderer aparte). Textura: textures/entity/novilis/
 * fuente.png y fuente_brillo.png (las bandas de sol). La entera y la rota comparten el atlas.
 */
public final class FuenteSolarMalla {

    private FuenteSolarMalla() {
    }

    public static LayerDefinition crear() {
        return entera(CubeDeformation.NONE);
    }

    private static LayerDefinition entera(CubeDeformation infla) {
        MeshDefinition malla = new MeshDefinition();
        PartDefinition p_root = malla.getRoot();
        PartDefinition p_fuente = p_root.addOrReplaceChild("fuente", CubeListBuilder.create(),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        p_fuente.addOrReplaceChild("base", CubeListBuilder.create()
                .texOffs(49, 0).addBox(-12F, 20.5F, -12F, 24F, 3.5F, 24F, infla)
                .texOffs(0, 30).addBox(-11.4F, 19.5F, -11.4F, 22.8F, 1F, 22.8F, infla)
                .texOffs(93, 30).addBox(-10.2F, 16.8F, -10.2F, 20.4F, 2.7F, 20.4F, infla)
                .texOffs(49, 55).addBox(-9F, 15.8F, -9F, 18F, 1F, 18F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        p_fuente.addOrReplaceChild("tramo0", CubeListBuilder.create()
                .texOffs(0, 0).addBox(-6F, -1F, -6F, 12F, 16.8F, 12F, infla)
                .texOffs(236, 0).addBox(-6.45F, -1F, -6.45F, 0.9F, 16.8F, 0.9F, infla)
                .texOffs(236, 0).addBox(-6.45F, -1F, 5.55F, 0.9F, 16.8F, 0.9F, infla)
                .texOffs(236, 0).addBox(5.55F, -1F, -6.45F, 0.9F, 16.8F, 0.9F, infla)
                .texOffs(236, 0).addBox(5.55F, -1F, 5.55F, 0.9F, 16.8F, 0.9F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        p_fuente.addOrReplaceChild("tramo1", CubeListBuilder.create()
                .texOffs(146, 0).addBox(-5.4F, -18.6F, -5.4F, 10.8F, 15.2F, 10.8F, infla)
                .texOffs(241, 0).addBox(-5.85F, -18.6F, -5.85F, 0.9F, 15.2F, 0.9F, infla)
                .texOffs(241, 0).addBox(-5.85F, -18.6F, 4.95F, 0.9F, 15.2F, 0.9F, infla)
                .texOffs(241, 0).addBox(4.95F, -18.6F, -5.85F, 0.9F, 15.2F, 0.9F, infla)
                .texOffs(241, 0).addBox(4.95F, -18.6F, 4.95F, 0.9F, 15.2F, 0.9F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        p_fuente.addOrReplaceChild("tramo2", CubeListBuilder.create()
                .texOffs(176, 30).addBox(-4.8F, -34.6F, -4.8F, 9.6F, 13.6F, 9.6F, infla)
                .texOffs(251, 0).addBox(-5.25F, -34.6F, -5.25F, 0.9F, 13.6F, 0.9F, infla)
                .texOffs(251, 0).addBox(-5.25F, -34.6F, 4.35F, 0.9F, 13.6F, 0.9F, infla)
                .texOffs(251, 0).addBox(4.35F, -34.6F, -5.25F, 0.9F, 13.6F, 0.9F, infla)
                .texOffs(251, 0).addBox(4.35F, -34.6F, 4.35F, 0.9F, 13.6F, 0.9F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        p_fuente.addOrReplaceChild("tramo3", CubeListBuilder.create()
                .texOffs(0, 76).addBox(-4.2F, -43F, -4.2F, 8.4F, 6F, 8.4F, infla)
                .texOffs(245, 106).addBox(-4.65F, -43F, -4.65F, 0.9F, 6F, 0.9F, infla)
                .texOffs(245, 106).addBox(-4.65F, -43F, 3.75F, 0.9F, 6F, 0.9F, infla)
                .texOffs(245, 106).addBox(3.75F, -43F, -4.65F, 0.9F, 6F, 0.9F, infla)
                .texOffs(245, 106).addBox(3.75F, -43F, 3.75F, 0.9F, 6F, 0.9F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        p_fuente.addOrReplaceChild("banda0", CubeListBuilder.create()
                .texOffs(122, 55).addBox(-6.3F, -3.4F, -6.3F, 12.6F, 2.4F, 12.6F, infla)
                .texOffs(35, 76).addBox(-6.65F, -3.9F, -6.65F, 13.3F, 0.7F, 13.3F, infla)
                .texOffs(35, 76).addBox(-6.65F, -1.2F, -6.65F, 13.3F, 0.7F, 13.3F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        p_fuente.addOrReplaceChild("banda1", CubeListBuilder.create()
                .texOffs(192, 76).addBox(-5.7F, -21F, -5.7F, 11.4F, 2.4F, 11.4F, infla)
                .texOffs(0, 92).addBox(-6.05F, -21.5F, -6.05F, 12.1F, 0.7F, 12.1F, infla)
                .texOffs(0, 92).addBox(-6.05F, -18.8F, -6.05F, 12.1F, 0.7F, 12.1F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        p_fuente.addOrReplaceChild("banda2", CubeListBuilder.create()
                .texOffs(185, 92).addBox(-5.1F, -37F, -5.1F, 10.2F, 2.4F, 10.2F, infla)
                .texOffs(0, 106).addBox(-5.45F, -37.5F, -5.45F, 10.9F, 0.7F, 10.9F, infla)
                .texOffs(0, 106).addBox(-5.45F, -34.8F, -5.45F, 10.9F, 0.7F, 10.9F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        p_fuente.addOrReplaceChild("disco0", CubeListBuilder.create()
                .texOffs(37, 119).addBox(-2F, -2F, -0.5F, 4F, 4F, 0.6F, infla),
                PartPose.offsetAndRotation(0F, -11F, -5.4F, 0F, 0F, 0F));
        p_fuente.addOrReplaceChild("disco_r0", CubeListBuilder.create()
                .texOffs(94, 119).addBox(-1.7F, -1.7F, -0.35F, 3.4F, 3.4F, 0.4F, infla),
                PartPose.offsetAndRotation(0F, -11F, -5.4F, 0F, 0F, 0.7854F));
        p_fuente.addOrReplaceChild("disco1", CubeListBuilder.create()
                .texOffs(37, 119).addBox(-2F, -2F, -0.5F, 4F, 4F, 0.6F, infla),
                PartPose.offsetAndRotation(-5.4F, -11F, 0F, 0F, 1.5708F, 0F));
        p_fuente.addOrReplaceChild("disco_r1", CubeListBuilder.create()
                .texOffs(94, 119).addBox(-1.7F, -1.7F, -0.35F, 3.4F, 3.4F, 0.4F, infla),
                PartPose.offsetAndRotation(-5.4F, -11F, 0F, 1.5708F, 0.7854F, 1.5708F));
        p_fuente.addOrReplaceChild("disco2", CubeListBuilder.create()
                .texOffs(37, 119).addBox(-2F, -2F, -0.5F, 4F, 4F, 0.6F, infla),
                PartPose.offsetAndRotation(0F, -11F, 5.4F, 3.1416F, 0F, 3.1416F));
        p_fuente.addOrReplaceChild("disco_r2", CubeListBuilder.create()
                .texOffs(94, 119).addBox(-1.7F, -1.7F, -0.35F, 3.4F, 3.4F, 0.4F, infla),
                PartPose.offsetAndRotation(0F, -11F, 5.4F, 3.1416F, 0F, 2.3562F));
        p_fuente.addOrReplaceChild("disco3", CubeListBuilder.create()
                .texOffs(37, 119).addBox(-2F, -2F, -0.5F, 4F, 4F, 0.6F, infla),
                PartPose.offsetAndRotation(5.4F, -11F, 0F, 0F, -1.5708F, 0F));
        p_fuente.addOrReplaceChild("disco_r3", CubeListBuilder.create()
                .texOffs(94, 119).addBox(-1.7F, -1.7F, -0.35F, 3.4F, 3.4F, 0.4F, infla),
                PartPose.offsetAndRotation(5.4F, -11F, 0F, -1.5708F, -0.7854F, 1.5708F));
        PartDefinition p_cuna = p_fuente.addOrReplaceChild("cuna", CubeListBuilder.create()
                .texOffs(131, 106).addBox(-4.6F, -1.6F, -4.6F, 9.2F, 1.6F, 9.2F, infla)
                .texOffs(90, 76).addBox(-6.2F, -3.2F, -6.2F, 12.4F, 1.6F, 12.4F, infla)
                .texOffs(88, 106).addBox(-5.2F, -4.4F, -5.2F, 10.4F, 1.3F, 10.4F, infla),
                PartPose.offsetAndRotation(0F, -43F, 0F, 0F, 0F, 0F));
        p_cuna.addOrReplaceChild("cuna_b", CubeListBuilder.create()
                .texOffs(95, 92).addBox(-5.4F, -3F, -5.4F, 10.8F, 1.4F, 10.8F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0.7854F, 0F));
        PartDefinition p_cuna_brazo0 = p_cuna.addOrReplaceChild("cuna_brazo0", CubeListBuilder.create()
                .texOffs(239, 76).addBox(-0.8F, -6.6F, -0.8F, 1.6F, 7.1F, 1.6F, infla),
                PartPose.offsetAndRotation(0F, -3.4F, -5.4F, 0.6632F, 0F, 0F));
        p_cuna_brazo0.addOrReplaceChild("cuna_punta0", CubeListBuilder.create()
                .texOffs(248, 92).addBox(-0.7F, -5.2F, -0.7F, 1.4F, 5.6F, 1.4F, infla)
                .texOffs(58, 119).addBox(-1.1F, -7.2F, -1.1F, 2.2F, 2.2F, 2.2F, infla),
                PartPose.offsetAndRotation(0F, -6.4F, 0F, -0.5236F, 0F, 0F));
        PartDefinition p_cuna_brazo1 = p_cuna.addOrReplaceChild("cuna_brazo1", CubeListBuilder.create()
                .texOffs(239, 76).addBox(-0.8F, -6.6F, -0.8F, 1.6F, 7.1F, 1.6F, infla),
                PartPose.offsetAndRotation(-3.8184F, -3.4F, -3.8184F, 0.6632F, 0.7854F, 0F));
        p_cuna_brazo1.addOrReplaceChild("cuna_punta1", CubeListBuilder.create()
                .texOffs(248, 92).addBox(-0.7F, -5.2F, -0.7F, 1.4F, 5.6F, 1.4F, infla)
                .texOffs(58, 119).addBox(-1.1F, -7.2F, -1.1F, 2.2F, 2.2F, 2.2F, infla),
                PartPose.offsetAndRotation(0F, -6.4F, 0F, -0.5236F, 0F, 0F));
        PartDefinition p_cuna_brazo2 = p_cuna.addOrReplaceChild("cuna_brazo2", CubeListBuilder.create()
                .texOffs(239, 76).addBox(-0.8F, -6.6F, -0.8F, 1.6F, 7.1F, 1.6F, infla),
                PartPose.offsetAndRotation(-5.4F, -3.4F, 0F, 0.6632F, 1.5708F, 0F));
        p_cuna_brazo2.addOrReplaceChild("cuna_punta2", CubeListBuilder.create()
                .texOffs(248, 92).addBox(-0.7F, -5.2F, -0.7F, 1.4F, 5.6F, 1.4F, infla)
                .texOffs(58, 119).addBox(-1.1F, -7.2F, -1.1F, 2.2F, 2.2F, 2.2F, infla),
                PartPose.offsetAndRotation(0F, -6.4F, 0F, -0.5236F, 0F, 0F));
        PartDefinition p_cuna_brazo3 = p_cuna.addOrReplaceChild("cuna_brazo3", CubeListBuilder.create()
                .texOffs(239, 76).addBox(-0.8F, -6.6F, -0.8F, 1.6F, 7.1F, 1.6F, infla),
                PartPose.offsetAndRotation(-3.8184F, -3.4F, 3.8184F, -2.4784F, 0.7854F, 3.1416F));
        p_cuna_brazo3.addOrReplaceChild("cuna_punta3", CubeListBuilder.create()
                .texOffs(248, 92).addBox(-0.7F, -5.2F, -0.7F, 1.4F, 5.6F, 1.4F, infla)
                .texOffs(58, 119).addBox(-1.1F, -7.2F, -1.1F, 2.2F, 2.2F, 2.2F, infla),
                PartPose.offsetAndRotation(0F, -6.4F, 0F, -0.5236F, 0F, 0F));
        PartDefinition p_cuna_brazo4 = p_cuna.addOrReplaceChild("cuna_brazo4", CubeListBuilder.create()
                .texOffs(239, 76).addBox(-0.8F, -6.6F, -0.8F, 1.6F, 7.1F, 1.6F, infla),
                PartPose.offsetAndRotation(0F, -3.4F, 5.4F, -2.4784F, 0F, 3.1416F));
        p_cuna_brazo4.addOrReplaceChild("cuna_punta4", CubeListBuilder.create()
                .texOffs(248, 92).addBox(-0.7F, -5.2F, -0.7F, 1.4F, 5.6F, 1.4F, infla)
                .texOffs(58, 119).addBox(-1.1F, -7.2F, -1.1F, 2.2F, 2.2F, 2.2F, infla),
                PartPose.offsetAndRotation(0F, -6.4F, 0F, -0.5236F, 0F, 0F));
        PartDefinition p_cuna_brazo5 = p_cuna.addOrReplaceChild("cuna_brazo5", CubeListBuilder.create()
                .texOffs(239, 76).addBox(-0.8F, -6.6F, -0.8F, 1.6F, 7.1F, 1.6F, infla),
                PartPose.offsetAndRotation(3.8184F, -3.4F, 3.8184F, -2.4784F, -0.7854F, 3.1416F));
        p_cuna_brazo5.addOrReplaceChild("cuna_punta5", CubeListBuilder.create()
                .texOffs(248, 92).addBox(-0.7F, -5.2F, -0.7F, 1.4F, 5.6F, 1.4F, infla)
                .texOffs(58, 119).addBox(-1.1F, -7.2F, -1.1F, 2.2F, 2.2F, 2.2F, infla),
                PartPose.offsetAndRotation(0F, -6.4F, 0F, -0.5236F, 0F, 0F));
        PartDefinition p_cuna_brazo6 = p_cuna.addOrReplaceChild("cuna_brazo6", CubeListBuilder.create()
                .texOffs(239, 76).addBox(-0.8F, -6.6F, -0.8F, 1.6F, 7.1F, 1.6F, infla),
                PartPose.offsetAndRotation(5.4F, -3.4F, 0F, 0.6632F, -1.5708F, 0F));
        p_cuna_brazo6.addOrReplaceChild("cuna_punta6", CubeListBuilder.create()
                .texOffs(248, 92).addBox(-0.7F, -5.2F, -0.7F, 1.4F, 5.6F, 1.4F, infla)
                .texOffs(58, 119).addBox(-1.1F, -7.2F, -1.1F, 2.2F, 2.2F, 2.2F, infla),
                PartPose.offsetAndRotation(0F, -6.4F, 0F, -0.5236F, 0F, 0F));
        PartDefinition p_cuna_brazo7 = p_cuna.addOrReplaceChild("cuna_brazo7", CubeListBuilder.create()
                .texOffs(239, 76).addBox(-0.8F, -6.6F, -0.8F, 1.6F, 7.1F, 1.6F, infla),
                PartPose.offsetAndRotation(3.8184F, -3.4F, -3.8184F, 0.6632F, -0.7854F, 0F));
        p_cuna_brazo7.addOrReplaceChild("cuna_punta7", CubeListBuilder.create()
                .texOffs(248, 92).addBox(-0.7F, -5.2F, -0.7F, 1.4F, 5.6F, 1.4F, infla)
                .texOffs(58, 119).addBox(-1.1F, -7.2F, -1.1F, 2.2F, 2.2F, 2.2F, infla),
                PartPose.offsetAndRotation(0F, -6.4F, 0F, -0.5236F, 0F, 0F));
        return LayerDefinition.create(malla, 256, 128);
    }

    public static LayerDefinition crearRota() {
        return rota(CubeDeformation.NONE);
    }

    private static LayerDefinition rota(CubeDeformation infla) {
        MeshDefinition malla = new MeshDefinition();
        PartDefinition p_root = malla.getRoot();
        PartDefinition p_fuente = p_root.addOrReplaceChild("fuente", CubeListBuilder.create(),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        p_fuente.addOrReplaceChild("base", CubeListBuilder.create()
                .texOffs(49, 0).addBox(-12F, 20.5F, -12F, 24F, 3.5F, 24F, infla)
                .texOffs(0, 30).addBox(-11.4F, 19.5F, -11.4F, 22.8F, 1F, 22.8F, infla)
                .texOffs(93, 30).addBox(-10.2F, 16.8F, -10.2F, 20.4F, 2.7F, 20.4F, infla)
                .texOffs(49, 55).addBox(-9F, 15.8F, -9F, 18F, 1F, 18F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        p_fuente.addOrReplaceChild("tramo0", CubeListBuilder.create()
                .texOffs(0, 55).addBox(-6F, 8F, -6F, 12F, 7.8F, 12F, infla)
                .texOffs(216, 30).addBox(-6F, 3F, -6F, 6.6F, 5.2F, 12F, infla)
                .texOffs(207, 106).addBox(-1.2F, 5.5F, -6F, 7.2F, 2.7F, 7.8F, infla)
                .texOffs(227, 55).addBox(-6F, 1.2F, -0.6F, 6F, 2.2F, 6.6F, infla)
                .texOffs(227, 92).addBox(-6.45F, 8F, -6.45F, 0.9F, 7.8F, 0.9F, infla)
                .texOffs(222, 55).addBox(-6.45F, 4.8F, 5.55F, 0.9F, 11F, 0.9F, infla)
                .texOffs(222, 55).addBox(5.55F, 4.8F, -6.45F, 0.9F, 11F, 0.9F, infla)
                .texOffs(246, 0).addBox(5.55F, 1.6F, 5.55F, 0.9F, 14.2F, 0.9F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        PartDefinition p_cuna_caida = p_fuente.addOrReplaceChild("cuna_caida", CubeListBuilder.create(),
                PartPose.offsetAndRotation(13F, 17.4244F, -6F, 0.4189F, 0.5236F, 1.3614F));
        PartDefinition p_cuna = p_cuna_caida.addOrReplaceChild("cuna", CubeListBuilder.create()
                .texOffs(169, 106).addBox(-4.6F, -1.6F, -4.6F, 9.2F, 1.6F, 9.2F, infla)
                .texOffs(141, 76).addBox(-6.2F, -3.2F, -6.2F, 12.4F, 1.6F, 12.4F, infla)
                .texOffs(45, 106).addBox(-5.2F, -4.4F, -5.2F, 10.4F, 1.3F, 10.4F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        p_cuna.addOrReplaceChild("cuna_b", CubeListBuilder.create()
                .texOffs(140, 92).addBox(-5.4F, -3F, -5.4F, 10.8F, 1.4F, 10.8F, infla),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0.7854F, 0F));
        PartDefinition p_cuna_brazo0 = p_cuna.addOrReplaceChild("cuna_brazo0", CubeListBuilder.create()
                .texOffs(247, 76).addBox(-0.8F, -6.6F, -0.8F, 1.6F, 7.1F, 1.6F, infla),
                PartPose.offsetAndRotation(0F, -3.4F, -5.4F, 0.6632F, 0F, 0F));
        p_cuna_brazo0.addOrReplaceChild("cuna_punta0", CubeListBuilder.create()
                .texOffs(78, 119).addBox(-0.7F, -2.5F, -0.7F, 1.4F, 2.9F, 1.4F, infla),
                PartPose.offsetAndRotation(0F, -6.4F, 0F, -0.5236F, 0F, 0F));
        PartDefinition p_cuna_brazo1 = p_cuna.addOrReplaceChild("cuna_brazo1", CubeListBuilder.create()
                .texOffs(247, 76).addBox(-0.8F, -6.6F, -0.8F, 1.6F, 7.1F, 1.6F, infla),
                PartPose.offsetAndRotation(-3.8184F, -3.4F, -3.8184F, 0.6632F, 0.7854F, 0F));
        p_cuna_brazo1.addOrReplaceChild("cuna_punta1", CubeListBuilder.create()
                .texOffs(238, 106).addBox(-0.7F, -5.2F, -0.7F, 1.4F, 5.6F, 1.4F, infla)
                .texOffs(68, 119).addBox(-1.1F, -7.2F, -1.1F, 2.2F, 2.2F, 2.2F, infla),
                PartPose.offsetAndRotation(0F, -6.4F, 0F, -0.5236F, 0F, 0F));
        PartDefinition p_cuna_brazo3 = p_cuna.addOrReplaceChild("cuna_brazo3", CubeListBuilder.create()
                .texOffs(247, 76).addBox(-0.8F, -6.6F, -0.8F, 1.6F, 7.1F, 1.6F, infla),
                PartPose.offsetAndRotation(-3.8184F, -3.4F, 3.8184F, -2.4784F, 0.7854F, -3.1416F));
        p_cuna_brazo3.addOrReplaceChild("cuna_punta3", CubeListBuilder.create()
                .texOffs(78, 119).addBox(-0.7F, -2.5F, -0.7F, 1.4F, 2.9F, 1.4F, infla),
                PartPose.offsetAndRotation(0F, -6.4F, 0F, -0.5236F, 0F, 0F));
        PartDefinition p_cuna_brazo4 = p_cuna.addOrReplaceChild("cuna_brazo4", CubeListBuilder.create()
                .texOffs(247, 76).addBox(-0.8F, -6.6F, -0.8F, 1.6F, 7.1F, 1.6F, infla),
                PartPose.offsetAndRotation(0F, -3.4F, 5.4F, -2.4784F, 0F, -3.1416F));
        p_cuna_brazo4.addOrReplaceChild("cuna_punta4", CubeListBuilder.create()
                .texOffs(238, 106).addBox(-0.7F, -5.2F, -0.7F, 1.4F, 5.6F, 1.4F, infla)
                .texOffs(68, 119).addBox(-1.1F, -7.2F, -1.1F, 2.2F, 2.2F, 2.2F, infla),
                PartPose.offsetAndRotation(0F, -6.4F, 0F, -0.5236F, 0F, 0F));
        PartDefinition p_cuna_brazo6 = p_cuna.addOrReplaceChild("cuna_brazo6", CubeListBuilder.create()
                .texOffs(247, 76).addBox(-0.8F, -6.6F, -0.8F, 1.6F, 7.1F, 1.6F, infla),
                PartPose.offsetAndRotation(5.4F, -3.4F, 0F, 0.6632F, -1.5708F, 0F));
        p_cuna_brazo6.addOrReplaceChild("cuna_punta6", CubeListBuilder.create()
                .texOffs(78, 119).addBox(-0.7F, -2.5F, -0.7F, 1.4F, 2.9F, 1.4F, infla),
                PartPose.offsetAndRotation(0F, -6.4F, 0F, -0.5236F, 0F, 0F));
        PartDefinition p_cuna_brazo7 = p_cuna.addOrReplaceChild("cuna_brazo7", CubeListBuilder.create()
                .texOffs(247, 76).addBox(-0.8F, -6.6F, -0.8F, 1.6F, 7.1F, 1.6F, infla),
                PartPose.offsetAndRotation(3.8184F, -3.4F, -3.8184F, 0.6632F, -0.7854F, 0F));
        p_cuna_brazo7.addOrReplaceChild("cuna_punta7", CubeListBuilder.create()
                .texOffs(238, 106).addBox(-0.7F, -5.2F, -0.7F, 1.4F, 5.6F, 1.4F, infla)
                .texOffs(68, 119).addBox(-1.1F, -7.2F, -1.1F, 2.2F, 2.2F, 2.2F, infla),
                PartPose.offsetAndRotation(0F, -6.4F, 0F, -0.5236F, 0F, 0F));
        p_fuente.addOrReplaceChild("trozo0", CubeListBuilder.create()
                .texOffs(191, 0).addBox(-5.4F, -8F, -5.4F, 10.8F, 15F, 10.8F, infla)
                .texOffs(174, 55).addBox(-5.85F, -6.6F, -5.85F, 11.7F, 2.4F, 11.7F, infla)
                .texOffs(50, 92).addBox(-5.4F, 7F, -5.4F, 10.8F, 2.2F, 10.8F, infla),
                PartPose.offsetAndRotation(-13F, 16.1164F, 8F, 0.0698F, 0.6109F, 1.5359F));
        p_fuente.addOrReplaceChild("cascote_0", CubeListBuilder.create()
                .texOffs(232, 92).addBox(-2F, -2F, -1.6F, 4F, 3.6F, 3.2F, infla),
                PartPose.offsetAndRotation(-8F, 22.6002F, -13F, 0.3708F, 1.4901F, 0.3425F));
        p_fuente.addOrReplaceChild("cascote_1", CubeListBuilder.create()
                .texOffs(0, 119).addBox(-1.7F, -1.7F, -1.36F, 3.4F, 3.06F, 2.72F, infla),
                PartPose.offsetAndRotation(9.5F, 22.5237F, 12F, -0.3634F, 0.93F, -0.0665F));
        p_fuente.addOrReplaceChild("cascote_2", CubeListBuilder.create()
                .texOffs(26, 119).addBox(-1.3F, -1.3F, -1.04F, 2.6F, 2.34F, 2.08F, infla),
                PartPose.offsetAndRotation(15F, 22.8787F, 4F, 0.0263F, 0.2047F, -0.2688F));
        p_fuente.addOrReplaceChild("cascote_3", CubeListBuilder.create()
                .texOffs(48, 119).addBox(-1.2F, -1.2F, -0.96F, 2.4F, 2.16F, 1.92F, infla),
                PartPose.offsetAndRotation(-15F, 23.2634F, -4F, -0.0484F, 0.3472F, -0.0392F));
        p_fuente.addOrReplaceChild("cascote_4", CubeListBuilder.create()
                .texOffs(85, 119).addBox(-1.1F, -1.1F, -0.88F, 2.2F, 1.98F, 1.76F, infla),
                PartPose.offsetAndRotation(3F, 22.9498F, -14.5F, -0.4147F, 0.1347F, 0.1833F));
        p_fuente.addOrReplaceChild("cascote_5", CubeListBuilder.create()
                .texOffs(14, 119).addBox(-1.5F, -1.5F, -1.2F, 3F, 2.7F, 2.4F, infla),
                PartPose.offsetAndRotation(-3F, 22.673F, 14F, -0.0687F, 0.8052F, 0.2044F));
        return LayerDefinition.create(malla, 256, 128);
    }
}
