package com.atalaya.client;

import net.minecraft.client.model.geom.PartPose;
import net.minecraft.client.model.geom.builders.CubeDeformation;
import net.minecraft.client.model.geom.builders.CubeListBuilder;
import net.minecraft.client.model.geom.builders.LayerDefinition;
import net.minecraft.client.model.geom.builders.MeshDefinition;
import net.minecraft.client.model.geom.builders.PartDefinition;

/**
 * Las mallas 3D de las armaduras de los jefes. GENERADO por
 * materiales/generadores/armaduras_jefes.py: no se edita a mano (las cajas
 * van con la textura, que se pinta con el mismo empaquetado).
 */
public final class ArmaduraJefeMalla {

    /** Lo que se mueve de cada pieza: parte, eje (0 x, 1 y, 2 z, 3 flota, 4 gira, 5 sube al andar, 6 se pliega al andar,
     *  7 gira en su plano, 8 late),
     *  amplitud, frecuencia, fase y cuanto crece al andar. */
    public record Anim(String parte, int eje, float amplitud, float frecuencia, float fase, float andar) {
    }

    private ArmaduraJefeMalla() {
    }

    private static PartDefinition bases(PartDefinition raiz) {
        return raiz;
    }

    public static LayerDefinition crear(String tema, String pieza) {
        return switch (tema + "/" + pieza) {
            case "mareas/casco" -> mareas_casco();
            case "mareas/pechera" -> mareas_pechera();
            case "mareas/grebas" -> mareas_grebas();
            case "mareas/botas" -> mareas_botas();
            case "jade/casco" -> jade_casco();
            case "jade/pechera" -> jade_pechera();
            case "jade/grebas" -> jade_grebas();
            case "jade/botas" -> jade_botas();
            case "vendaval/casco" -> vendaval_casco();
            case "vendaval/pechera" -> vendaval_pechera();
            case "vendaval/grebas" -> vendaval_grebas();
            case "vendaval/botas" -> vendaval_botas();
            case "solar/casco" -> solar_casco();
            case "solar/pechera" -> solar_pechera();
            case "solar/grebas" -> solar_grebas();
            case "solar/botas" -> solar_botas();
            default -> throw new IllegalArgumentException(tema + "/" + pieza);
        };
    }

    public static Anim[] anims(String tema, String pieza) {
        return switch (tema + "/" + pieza) {
            case "mareas/casco" -> new Anim[]{new Anim("branquia_izq", 1, 0.22F, 0.22F, 0F, 0.6F), new Anim("branquia_der", 1, -0.22F, 0.22F, 1.6F, 0.6F)};
            case "mareas/pechera" -> new Anim[]{new Anim("aleta_hombro_izq", 0, 0.05F, 0.2F, 0F, 0.3F), new Anim("aleta_hombro_der", 0, 0.05F, 0.2F, 1.2F, 0.3F), new Anim("halo_pecho", 7, 0.03F, 0F, 0F, 0F), new Anim("halo_pecho", 8, 0.08F, 0.13F, 0F, 0F), new Anim("capa_0", 0, 0.07F, 0.11F, 0F, 1F), new Anim("capa_0", 5, 0.9F, 0F, 0F, 1F), new Anim("capa_1", 0, 0.07F, 0.11F, 0.9F, 1F), new Anim("capa_1", 5, 0.9F, 0F, 0F, 1F), new Anim("capa_2", 0, 0.07F, 0.11F, 1.8F, 1F), new Anim("capa_2", 5, 0.9F, 0F, 0F, 1F)};
            case "mareas/grebas" -> new Anim[]{new Anim("aleta_rodilla_izq", 1, 0.12F, 0.25F, 0.7F, 0.8F), new Anim("aleta_rodilla_der", 1, -0.12F, 0.25F, -0.7F, 0.8F)};
            case "mareas/botas" -> new Anim[]{new Anim("aleta_tobillo_izq", 1, 0.18F, 0.3F, 0.4F, 1.2F), new Anim("aleta_tobillo_der", 1, -0.18F, 0.3F, -0.4F, 1.2F)};
            case "jade/pechera" -> new Anim[]{new Anim("halo_pecho", 7, 0.012F, 0F, 0F, 0F), new Anim("halo_pecho", 8, 0.12F, 0.16F, 0F, 0F)};
            case "vendaval/casco" -> new Anim[]{new Anim("ala_casco_izq", 1, 0.2F, 0.32F, 0F, 0.2F), new Anim("antena_izq", 2, 0.08F, 0.17F, 0F, 0.5F), new Anim("ala_casco_der", 1, -0.2F, 0.32F, 0F, 0.2F), new Anim("antena_der", 2, -0.08F, 0.17F, 1F, 0.5F)};
            case "vendaval/pechera" -> new Anim[]{new Anim("halo_pecho", 7, -0.09F, 0F, 0F, 0F), new Anim("halo_pecho", 8, 0.06F, 0.45F, 0F, 0F), new Anim("ala_izq", 1, 0.1F, 0.18F, 0F, 0F), new Anim("ala_izq", 6, -0.7F, 0F, 0F, 1F), new Anim("ala_der", 1, -0.1F, 0.18F, 0F, 0F), new Anim("ala_der", 6, 0.7F, 0F, 0F, 1F)};
            case "vendaval/botas" -> new Anim[]{new Anim("ala_talon_izq", 1, 0.22F, 0.4F, 0F, 0.3F), new Anim("ala_talon_der", 1, -0.22F, 0.4F, 0F, 0.3F)};
            case "solar/casco" -> new Anim[]{new Anim("llama_corona", 8, 0.12F, 0.85F, 0F, 0F), new Anim("halo", 7, 0.02F, 0F, 0F, 0F)};
            case "solar/pechera" -> new Anim[]{new Anim("llama_hombro_izq", 8, 0.12F, 0.85F, 0.6F, 0F), new Anim("llama_hombro_der", 8, 0.12F, 0.85F, 2F, 0F), new Anim("halo_pecho", 7, 0.025F, 0F, 0F, 0F), new Anim("halo_pecho", 8, 0.1F, 0.2F, 0F, 0F), new Anim("capa_0", 0, 0.06F, 0.1F, 0F, 1F), new Anim("capa_0", 5, 0.9F, 0F, 0F, 1F), new Anim("capa_1", 0, 0.06F, 0.1F, 0.9F, 1F), new Anim("capa_1", 5, 0.9F, 0F, 0F, 1F), new Anim("capa_2", 0, 0.06F, 0.1F, 1.8F, 1F), new Anim("capa_2", 5, 0.9F, 0F, 0F, 1F)};
            case "solar/botas" -> new Anim[]{new Anim("llama_talon_izq", 8, 0.15F, 1.1F, 0F, 0F), new Anim("llama_talon_der", 8, 0.15F, 1.1F, 1.5F, 0F)};
            default -> new Anim[0];
        };
    }

    /** Si la pieza lleva algo translucido (la capa de membrana). */
    public static boolean conMembrana(String tema, String pieza) {
        return switch (tema + "/" + pieza) {
            case "mareas/casco", "mareas/pechera", "mareas/grebas", "mareas/botas", "jade/casco", "jade/pechera", "jade/grebas", "vendaval/pechera" -> true;
            default -> false;
        };
    }

    private static LayerDefinition mareas_casco() {
        MeshDefinition malla = new MeshDefinition();
        PartDefinition raiz = malla.getRoot();
        PartDefinition p_head = raiz.addOrReplaceChild("head", CubeListBuilder.create(), PartPose.offset(0F, 0F, 0F));
        PartDefinition p_body = raiz.addOrReplaceChild("body", CubeListBuilder.create(), PartPose.offset(0F, 0F, 0F));
        PartDefinition p_right_arm = raiz.addOrReplaceChild("right_arm", CubeListBuilder.create(), PartPose.offset(-5F, 2F, 0F));
        PartDefinition p_left_arm = raiz.addOrReplaceChild("left_arm", CubeListBuilder.create(), PartPose.offset(5F, 2F, 0F));
        PartDefinition p_right_leg = raiz.addOrReplaceChild("right_leg", CubeListBuilder.create(), PartPose.offset(-1.9F, 12F, 0F));
        PartDefinition p_left_leg = raiz.addOrReplaceChild("left_leg", CubeListBuilder.create(), PartPose.offset(1.9F, 12F, 0F));
        PartDefinition p_casco_mareas = p_head.addOrReplaceChild("casco_mareas", CubeListBuilder.create()
                .texOffs(6, 0).addBox(-4F, -8F, -4F, 8F, 8F, 8F, new CubeDeformation(1F)),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        PartDefinition p_venera = p_head.addOrReplaceChild("venera", CubeListBuilder.create()
                .texOffs(48, 45).addBox(-1.5F, -1.5F, -0.5F, 3F, 3F, 1F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, -7F, 4.2F, -0.4887F, 0F, 0F));
        PartDefinition p_venera_0 = p_venera.addOrReplaceChild("venera_0", CubeListBuilder.create()
                .texOffs(42, 28).addBox(-1F, -8F, -0.4F, 2F, 8F, 1F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, -1.0472F));
        PartDefinition p_venera_1 = p_venera.addOrReplaceChild("venera_1", CubeListBuilder.create()
                .texOffs(40, 17).addBox(-1F, -10F, -0.4F, 2F, 10F, 1F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, -0.6981F));
        PartDefinition p_venera_2 = p_venera.addOrReplaceChild("venera_2", CubeListBuilder.create()
                .texOffs(106, 0).addBox(-1F, -11F, -0.4F, 2F, 11F, 1F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, -0.3491F));
        PartDefinition p_venera_3 = p_venera.addOrReplaceChild("venera_3", CubeListBuilder.create()
                .texOffs(112, 0).addBox(-1F, -11F, -0.4F, 2F, 11F, 1F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        PartDefinition p_venera_4 = p_venera.addOrReplaceChild("venera_4", CubeListBuilder.create()
                .texOffs(118, 0).addBox(-1F, -11F, -0.4F, 2F, 11F, 1F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0.3491F));
        PartDefinition p_venera_5 = p_venera.addOrReplaceChild("venera_5", CubeListBuilder.create()
                .texOffs(46, 17).addBox(-1F, -10F, -0.4F, 2F, 10F, 1F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0.6981F));
        PartDefinition p_venera_6 = p_venera.addOrReplaceChild("venera_6", CubeListBuilder.create()
                .texOffs(48, 28).addBox(-1F, -8F, -0.4F, 2F, 8F, 1F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 1.0472F));
        PartDefinition p_coral_izq = p_head.addOrReplaceChild("coral_izq", CubeListBuilder.create()
                .texOffs(20, 45).addBox(-0.5F, -4F, -0.5F, 1F, 4F, 1F, CubeDeformation.NONE)
                .texOffs(90, 45).addBox(0.5F, -6F, -0.5F, 1F, 2F, 1F, CubeDeformation.NONE)
                .texOffs(112, 45).addBox(-1.5F, -5F, -0.5F, 1F, 1F, 1F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(4.5F, -6.5F, -1F, 0F, 0F, 0.4363F));
        PartDefinition p_branquia_izq = p_head.addOrReplaceChild("branquia_izq", CubeListBuilder.create()
                .texOffs(0, 17).addBox(0F, -3F, -0.5F, 0F, 6F, 5F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(5F, -3.5F, 0.5F, 0F, 0.6109F, 0F));
        PartDefinition p_coral_der = p_head.addOrReplaceChild("coral_der", CubeListBuilder.create()
                .texOffs(24, 45).addBox(-0.5F, -4F, -0.5F, 1F, 4F, 1F, CubeDeformation.NONE)
                .texOffs(94, 45).addBox(-1.5F, -6F, -0.5F, 1F, 2F, 1F, CubeDeformation.NONE)
                .texOffs(116, 45).addBox(0.5F, -5F, -0.5F, 1F, 1F, 1F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(-4.5F, -6.5F, -1F, 0F, 0F, -0.4363F));
        PartDefinition p_branquia_der = p_head.addOrReplaceChild("branquia_der", CubeListBuilder.create()
                .texOffs(10, 17).addBox(0F, -3F, -0.5F, 0F, 6F, 5F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(-5F, -3.5F, 0.5F, 0F, -0.6109F, 0F));
        return LayerDefinition.create(malla, 128, 64);
    }

    private static LayerDefinition mareas_pechera() {
        MeshDefinition malla = new MeshDefinition();
        PartDefinition raiz = malla.getRoot();
        PartDefinition p_head = raiz.addOrReplaceChild("head", CubeListBuilder.create(), PartPose.offset(0F, 0F, 0F));
        PartDefinition p_body = raiz.addOrReplaceChild("body", CubeListBuilder.create(), PartPose.offset(0F, 0F, 0F));
        PartDefinition p_right_arm = raiz.addOrReplaceChild("right_arm", CubeListBuilder.create(), PartPose.offset(-5F, 2F, 0F));
        PartDefinition p_left_arm = raiz.addOrReplaceChild("left_arm", CubeListBuilder.create(), PartPose.offset(5F, 2F, 0F));
        PartDefinition p_right_leg = raiz.addOrReplaceChild("right_leg", CubeListBuilder.create(), PartPose.offset(-1.9F, 12F, 0F));
        PartDefinition p_left_leg = raiz.addOrReplaceChild("left_leg", CubeListBuilder.create(), PartPose.offset(1.9F, 12F, 0F));
        PartDefinition p_pechera_mareas = p_body.addOrReplaceChild("pechera_mareas", CubeListBuilder.create()
                .texOffs(38, 0).addBox(-4F, 0F, -2F, 8F, 12F, 4F, new CubeDeformation(0.85F)),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        PartDefinition p_manga_right_arm = p_right_arm.addOrReplaceChild("manga_right_arm", CubeListBuilder.create()
                .texOffs(52, 17).addBox(-3F, -2F, -2F, 4F, 6F, 4F, new CubeDeformation(0.85F)),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        PartDefinition p_manga_left_arm = p_left_arm.addOrReplaceChild("manga_left_arm", CubeListBuilder.create()
                .texOffs(68, 17).addBox(-1F, -2F, -2F, 4F, 6F, 4F, new CubeDeformation(0.85F)),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        PartDefinition p_lamina_izq_0 = p_left_arm.addOrReplaceChild("lamina_izq_0", CubeListBuilder.create()
                .texOffs(54, 28).addBox(-3.5F, -1F, -3.5F, 7F, 1F, 7F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0.8F, -3.4F, 0F, 0F, 0F, -0.2094F));
        PartDefinition p_lamina_izq_1 = p_left_arm.addOrReplaceChild("lamina_izq_1", CubeListBuilder.create()
                .texOffs(24, 37).addBox(-2.5F, -0.5F, -3F, 5F, 1F, 6F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(3.1F, -2.3F, 0F, 0F, 0F, -0.6632F));
        PartDefinition p_lamina_izq_2 = p_left_arm.addOrReplaceChild("lamina_izq_2", CubeListBuilder.create()
                .texOffs(88, 37).addBox(-2F, -0.5F, -2.5F, 4F, 1F, 5F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(4.4F, -0.2F, 0F, 0F, 0F, -1.0821F));
        PartDefinition p_lamina_der_0 = p_right_arm.addOrReplaceChild("lamina_der_0", CubeListBuilder.create()
                .texOffs(82, 28).addBox(-3.5F, -1F, -3.5F, 7F, 1F, 7F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(-0.8F, -3.4F, 0F, 0F, 0F, 0.2094F));
        PartDefinition p_lamina_der_1 = p_right_arm.addOrReplaceChild("lamina_der_1", CubeListBuilder.create()
                .texOffs(46, 37).addBox(-2.5F, -0.5F, -3F, 5F, 1F, 6F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(-3.1F, -2.3F, 0F, 0F, 0F, 0.6632F));
        PartDefinition p_lamina_der_2 = p_right_arm.addOrReplaceChild("lamina_der_2", CubeListBuilder.create()
                .texOffs(106, 37).addBox(-2F, -0.5F, -2.5F, 4F, 1F, 5F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(-4.4F, -0.2F, 0F, 0F, 0F, 1.0821F));
        PartDefinition p_aleta_hombro_izq = p_left_arm.addOrReplaceChild("aleta_hombro_izq", CubeListBuilder.create()
                .texOffs(20, 17).addBox(0F, -6F, -1F, 0F, 6F, 5F, CubeDeformation.NONE)
                .texOffs(16, 37).addBox(-0.5F, -6.5F, -1.5F, 1F, 7F, 1F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(2.4F, -4F, 0.5F, -0.4887F, 0F, -0.3142F));
        PartDefinition p_aleta_hombro_der = p_right_arm.addOrReplaceChild("aleta_hombro_der", CubeListBuilder.create()
                .texOffs(30, 17).addBox(0F, -6F, -1F, 0F, 6F, 5F, CubeDeformation.NONE)
                .texOffs(20, 37).addBox(-0.5F, -6.5F, -1.5F, 1F, 7F, 1F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(-2.4F, -4F, 0.5F, -0.4887F, 0F, 0.3142F));
        PartDefinition p_gola_detras = p_body.addOrReplaceChild("gola_detras", CubeListBuilder.create()
                .texOffs(0, 45).addBox(-4.5F, -4F, -0.5F, 9F, 4F, 1F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, 0.2F, 2.6F, -0.3142F, 0F, 0F));
        PartDefinition p_gola_izq = p_body.addOrReplaceChild("gola_izq", CubeListBuilder.create()
                .texOffs(68, 37).addBox(-0.5F, -3F, -2.5F, 1F, 3F, 4F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(4.4F, 0.2F, 0.6F, -0.1396F, 0F, -0.2443F));
        PartDefinition p_gola_der = p_body.addOrReplaceChild("gola_der", CubeListBuilder.create()
                .texOffs(78, 37).addBox(-0.5F, -3F, -2.5F, 1F, 3F, 4F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(-4.4F, 0.2F, 0.6F, -0.1396F, 0F, 0.2443F));
        PartDefinition p_gola_delante = p_body.addOrReplaceChild("gola_delante", CubeListBuilder.create()
                .texOffs(98, 45).addBox(-3F, -1F, -0.5F, 6F, 1F, 1F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, 0.2F, -2.9F, 0.2094F, 0F, 0F));
        PartDefinition p_halo_pecho = p_body.addOrReplaceChild("halo_pecho", CubeListBuilder.create()
                .texOffs(24, 28).addBox(-4.5F, -4.5F, 0F, 9F, 9F, 0F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, 4.6F, -3.75F, 0F, 0F, 0F));
        PartDefinition p_venera_pecho = p_body.addOrReplaceChild("venera_pecho", CubeListBuilder.create()
                .texOffs(84, 45).addBox(-1F, -1F, -0.6F, 2F, 2F, 1F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, 4.6F, -3.1F, 0F, 0F, 0F));
        PartDefinition p_venera_pecho_0 = p_venera_pecho.addOrReplaceChild("venera_pecho_0", CubeListBuilder.create()
                .texOffs(28, 45).addBox(-0.5F, -4F, -0.4F, 1F, 4F, 1F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, 0F, -0.1F, 0F, 0F, -0.9076F));
        PartDefinition p_venera_pecho_1 = p_venera_pecho.addOrReplaceChild("venera_pecho_1", CubeListBuilder.create()
                .texOffs(32, 45).addBox(-0.5F, -4F, -0.4F, 1F, 4F, 1F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, 0F, -0.1F, 0F, 0F, -0.4538F));
        PartDefinition p_venera_pecho_2 = p_venera_pecho.addOrReplaceChild("venera_pecho_2", CubeListBuilder.create()
                .texOffs(36, 45).addBox(-0.5F, -4F, -0.4F, 1F, 4F, 1F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, 0F, -0.1F, 0F, 0F, 0F));
        PartDefinition p_venera_pecho_3 = p_venera_pecho.addOrReplaceChild("venera_pecho_3", CubeListBuilder.create()
                .texOffs(40, 45).addBox(-0.5F, -4F, -0.4F, 1F, 4F, 1F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, 0F, -0.1F, 0F, 0F, 0.4538F));
        PartDefinition p_venera_pecho_4 = p_venera_pecho.addOrReplaceChild("venera_pecho_4", CubeListBuilder.create()
                .texOffs(44, 45).addBox(-0.5F, -4F, -0.4F, 1F, 4F, 1F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, 0F, -0.1F, 0F, 0F, 0.9076F));
        PartDefinition p_capa_0 = p_body.addOrReplaceChild("capa_0", CubeListBuilder.create()
                .texOffs(62, 0).addBox(-1.5F, 0F, 0F, 3F, 15F, 0F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(-3F, 0.5F, 2.9F, 0.1396F, 0F, 0.0698F));
        PartDefinition p_capa_1 = p_body.addOrReplaceChild("capa_1", CubeListBuilder.create()
                .texOffs(0, 0).addBox(-1.5F, 0F, 0F, 3F, 17F, 0F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, 0.5F, 2.9F, 0.1396F, 0F, 0F));
        PartDefinition p_capa_2 = p_body.addOrReplaceChild("capa_2", CubeListBuilder.create()
                .texOffs(68, 0).addBox(-1.5F, 0F, 0F, 3F, 15F, 0F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(3F, 0.5F, 2.9F, 0.1396F, 0F, -0.0698F));
        PartDefinition p_espina_0 = p_body.addOrReplaceChild("espina_0", CubeListBuilder.create()
                .texOffs(72, 45).addBox(-0.5F, -3F, -0.5F, 1F, 3F, 1F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, 2F, 3F, -0.8727F, 0F, 0F));
        PartDefinition p_espina_1 = p_body.addOrReplaceChild("espina_1", CubeListBuilder.create()
                .texOffs(76, 45).addBox(-0.5F, -2.5F, -0.5F, 1F, 3F, 1F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, 5F, 3F, -0.8727F, 0F, 0F));
        PartDefinition p_espina_2 = p_body.addOrReplaceChild("espina_2", CubeListBuilder.create()
                .texOffs(80, 45).addBox(-0.5F, -2F, -0.5F, 1F, 3F, 1F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, 8F, 3F, -0.8727F, 0F, 0F));
        return LayerDefinition.create(malla, 128, 64);
    }

    private static LayerDefinition mareas_grebas() {
        MeshDefinition malla = new MeshDefinition();
        PartDefinition raiz = malla.getRoot();
        PartDefinition p_head = raiz.addOrReplaceChild("head", CubeListBuilder.create(), PartPose.offset(0F, 0F, 0F));
        PartDefinition p_body = raiz.addOrReplaceChild("body", CubeListBuilder.create(), PartPose.offset(0F, 0F, 0F));
        PartDefinition p_right_arm = raiz.addOrReplaceChild("right_arm", CubeListBuilder.create(), PartPose.offset(-5F, 2F, 0F));
        PartDefinition p_left_arm = raiz.addOrReplaceChild("left_arm", CubeListBuilder.create(), PartPose.offset(5F, 2F, 0F));
        PartDefinition p_right_leg = raiz.addOrReplaceChild("right_leg", CubeListBuilder.create(), PartPose.offset(-1.9F, 12F, 0F));
        PartDefinition p_left_leg = raiz.addOrReplaceChild("left_leg", CubeListBuilder.create(), PartPose.offset(1.9F, 12F, 0F));
        PartDefinition p_cintura_mareas = p_body.addOrReplaceChild("cintura_mareas", CubeListBuilder.create()
                .texOffs(0, 28).addBox(-4F, 7F, -2F, 8F, 5F, 4F, new CubeDeformation(0.55F)),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        PartDefinition p_pernera_right_leg = p_right_leg.addOrReplaceChild("pernera_right_leg", CubeListBuilder.create()
                .texOffs(74, 0).addBox(-2F, 0F, -2F, 4F, 9F, 4F, new CubeDeformation(0.5F)),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        PartDefinition p_pernera_left_leg = p_left_leg.addOrReplaceChild("pernera_left_leg", CubeListBuilder.create()
                .texOffs(90, 0).addBox(-2F, 0F, -2F, 4F, 9F, 4F, new CubeDeformation(0.5F)),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        PartDefinition p_conchas_delante = p_body.addOrReplaceChild("conchas_delante", CubeListBuilder.create()
                .texOffs(56, 45).addBox(-3.5F, 0F, -0.5F, 3F, 3F, 1F, CubeDeformation.NONE)
                .texOffs(64, 45).addBox(0.5F, 0F, -0.5F, 3F, 3F, 1F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, 11.5F, -2.7F, 0.1396F, 0F, 0F));
        PartDefinition p_aleta_rodilla_izq = p_left_leg.addOrReplaceChild("aleta_rodilla_izq", CubeListBuilder.create()
                .texOffs(110, 28).addBox(0F, -3F, -0.5F, 0F, 4F, 4F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(2.6F, 5F, -1F, 0F, 0.4363F, 0F));
        PartDefinition p_aleta_rodilla_der = p_right_leg.addOrReplaceChild("aleta_rodilla_der", CubeListBuilder.create()
                .texOffs(118, 28).addBox(0F, -3F, -0.5F, 0F, 4F, 4F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(-2.6F, 5F, -1F, 0F, -0.4363F, 0F));
        return LayerDefinition.create(malla, 128, 64);
    }

    private static LayerDefinition mareas_botas() {
        MeshDefinition malla = new MeshDefinition();
        PartDefinition raiz = malla.getRoot();
        PartDefinition p_head = raiz.addOrReplaceChild("head", CubeListBuilder.create(), PartPose.offset(0F, 0F, 0F));
        PartDefinition p_body = raiz.addOrReplaceChild("body", CubeListBuilder.create(), PartPose.offset(0F, 0F, 0F));
        PartDefinition p_right_arm = raiz.addOrReplaceChild("right_arm", CubeListBuilder.create(), PartPose.offset(-5F, 2F, 0F));
        PartDefinition p_left_arm = raiz.addOrReplaceChild("left_arm", CubeListBuilder.create(), PartPose.offset(5F, 2F, 0F));
        PartDefinition p_right_leg = raiz.addOrReplaceChild("right_leg", CubeListBuilder.create(), PartPose.offset(-1.9F, 12F, 0F));
        PartDefinition p_left_leg = raiz.addOrReplaceChild("left_leg", CubeListBuilder.create(), PartPose.offset(1.9F, 12F, 0F));
        PartDefinition p_bota_left_leg = p_left_leg.addOrReplaceChild("bota_left_leg", CubeListBuilder.create()
                .texOffs(84, 17).addBox(-2F, 6F, -2F, 4F, 6F, 4F, new CubeDeformation(1F)),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        PartDefinition p_aleta_tobillo_izq = p_left_leg.addOrReplaceChild("aleta_tobillo_izq", CubeListBuilder.create()
                .texOffs(0, 37).addBox(0F, -3F, 0F, 0F, 4F, 4F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(3.1F, 8.5F, 1.2F, 0F, 0.5236F, 0F));
        PartDefinition p_bota_right_leg = p_right_leg.addOrReplaceChild("bota_right_leg", CubeListBuilder.create()
                .texOffs(100, 17).addBox(-2F, 6F, -2F, 4F, 6F, 4F, new CubeDeformation(1F)),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        PartDefinition p_aleta_tobillo_der = p_right_leg.addOrReplaceChild("aleta_tobillo_der", CubeListBuilder.create()
                .texOffs(8, 37).addBox(0F, -3F, 0F, 0F, 4F, 4F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(-3.1F, 8.5F, 1.2F, 0F, -0.5236F, 0F));
        return LayerDefinition.create(malla, 128, 64);
    }

    private static LayerDefinition jade_casco() {
        MeshDefinition malla = new MeshDefinition();
        PartDefinition raiz = malla.getRoot();
        PartDefinition p_head = raiz.addOrReplaceChild("head", CubeListBuilder.create(), PartPose.offset(0F, 0F, 0F));
        PartDefinition p_body = raiz.addOrReplaceChild("body", CubeListBuilder.create(), PartPose.offset(0F, 0F, 0F));
        PartDefinition p_right_arm = raiz.addOrReplaceChild("right_arm", CubeListBuilder.create(), PartPose.offset(-5F, 2F, 0F));
        PartDefinition p_left_arm = raiz.addOrReplaceChild("left_arm", CubeListBuilder.create(), PartPose.offset(5F, 2F, 0F));
        PartDefinition p_right_leg = raiz.addOrReplaceChild("right_leg", CubeListBuilder.create(), PartPose.offset(-1.9F, 12F, 0F));
        PartDefinition p_left_leg = raiz.addOrReplaceChild("left_leg", CubeListBuilder.create(), PartPose.offset(1.9F, 12F, 0F));
        PartDefinition p_casco_jade = p_head.addOrReplaceChild("casco_jade", CubeListBuilder.create()
                .texOffs(0, 0).addBox(-4F, -8F, -4F, 8F, 8F, 8F, new CubeDeformation(1F)),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        PartDefinition p_hocico = p_head.addOrReplaceChild("hocico", CubeListBuilder.create()
                .texOffs(16, 40).addBox(-3F, -1F, -1.5F, 6F, 2F, 2F, CubeDeformation.NONE)
                .texOffs(22, 45).addBox(-1F, -0.5F, -2.5F, 2F, 1F, 1F, CubeDeformation.NONE)
                .texOffs(0, 45).addBox(-2.8F, 1F, -1.2F, 1F, 2F, 1F, CubeDeformation.NONE)
                .texOffs(4, 45).addBox(1.8F, 1F, -1.2F, 1F, 2F, 1F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, -6.5F, -5.3F, 0.2094F, 0F, 0F));
        PartDefinition p_oreja_izq = p_head.addOrReplaceChild("oreja_izq", CubeListBuilder.create()
                .texOffs(80, 40).addBox(-1F, -2F, -1F, 2F, 2F, 1F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(3.2F, -8.6F, 0.5F, 0F, 0F, 0.3142F));
        PartDefinition p_oreja_der = p_head.addOrReplaceChild("oreja_der", CubeListBuilder.create()
                .texOffs(86, 40).addBox(-1F, -2F, -1F, 2F, 2F, 1F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(-3.2F, -8.6F, 0.5F, 0F, 0F, -0.3142F));
        PartDefinition p_cristal_casco_0 = p_head.addOrReplaceChild("cristal_casco_0", CubeListBuilder.create()
                .texOffs(28, 26).addBox(-1F, -6F, -1F, 2F, 6F, 2F, CubeDeformation.NONE)
                .texOffs(28, 45).addBox(-0.5F, -7F, -0.5F, 1F, 1F, 1F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, -8.6F, 0.5F, -0.1745F, 0F, 0F));
        PartDefinition p_cristal_casco_1 = p_head.addOrReplaceChild("cristal_casco_1", CubeListBuilder.create()
                .texOffs(48, 34).addBox(-1F, -4F, -1F, 2F, 4F, 2F, CubeDeformation.NONE)
                .texOffs(32, 45).addBox(-0.5F, -5F, -0.5F, 1F, 1F, 1F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(-2.2F, -8.6F, 1.6F, -0.3142F, 0F, 0.3142F));
        PartDefinition p_cristal_casco_2 = p_head.addOrReplaceChild("cristal_casco_2", CubeListBuilder.create()
                .texOffs(56, 34).addBox(-1F, -4F, -1F, 2F, 4F, 2F, CubeDeformation.NONE)
                .texOffs(36, 45).addBox(-0.5F, -5F, -0.5F, 1F, 1F, 1F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(2.2F, -8.6F, 1.6F, -0.3142F, 0F, -0.3142F));
        return LayerDefinition.create(malla, 128, 64);
    }

    private static LayerDefinition jade_pechera() {
        MeshDefinition malla = new MeshDefinition();
        PartDefinition raiz = malla.getRoot();
        PartDefinition p_head = raiz.addOrReplaceChild("head", CubeListBuilder.create(), PartPose.offset(0F, 0F, 0F));
        PartDefinition p_body = raiz.addOrReplaceChild("body", CubeListBuilder.create(), PartPose.offset(0F, 0F, 0F));
        PartDefinition p_right_arm = raiz.addOrReplaceChild("right_arm", CubeListBuilder.create(), PartPose.offset(-5F, 2F, 0F));
        PartDefinition p_left_arm = raiz.addOrReplaceChild("left_arm", CubeListBuilder.create(), PartPose.offset(5F, 2F, 0F));
        PartDefinition p_right_leg = raiz.addOrReplaceChild("right_leg", CubeListBuilder.create(), PartPose.offset(-1.9F, 12F, 0F));
        PartDefinition p_left_leg = raiz.addOrReplaceChild("left_leg", CubeListBuilder.create(), PartPose.offset(1.9F, 12F, 0F));
        PartDefinition p_pechera_jade = p_body.addOrReplaceChild("pechera_jade", CubeListBuilder.create()
                .texOffs(32, 0).addBox(-4F, 0F, -2F, 8F, 12F, 4F, new CubeDeformation(0.85F)),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        PartDefinition p_manga_right_arm = p_right_arm.addOrReplaceChild("manga_right_arm", CubeListBuilder.create()
                .texOffs(88, 0).addBox(-3F, -2F, -2F, 4F, 6F, 4F, new CubeDeformation(0.85F)),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        PartDefinition p_manga_left_arm = p_left_arm.addOrReplaceChild("manga_left_arm", CubeListBuilder.create()
                .texOffs(104, 0).addBox(-1F, -2F, -2F, 4F, 6F, 4F, new CubeDeformation(0.85F)),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        PartDefinition p_lamina_izq_0 = p_left_arm.addOrReplaceChild("lamina_izq_0", CubeListBuilder.create()
                .texOffs(74, 16).addBox(-3.5F, -1F, -3.5F, 7F, 1F, 7F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0.8F, -3.4F, 0F, 0F, 0F, -0.2094F));
        PartDefinition p_lamina_izq_1 = p_left_arm.addOrReplaceChild("lamina_izq_1", CubeListBuilder.create()
                .texOffs(44, 26).addBox(-2.5F, -0.5F, -3F, 5F, 1F, 6F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(3.1F, -2.3F, 0F, 0F, 0F, -0.6632F));
        PartDefinition p_lamina_izq_2 = p_left_arm.addOrReplaceChild("lamina_izq_2", CubeListBuilder.create()
                .texOffs(0, 34).addBox(-2F, -0.5F, -2.5F, 4F, 1F, 5F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(4.4F, -0.2F, 0F, 0F, 0F, -1.0821F));
        PartDefinition p_lamina_der_0 = p_right_arm.addOrReplaceChild("lamina_der_0", CubeListBuilder.create()
                .texOffs(0, 26).addBox(-3.5F, -1F, -3.5F, 7F, 1F, 7F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(-0.8F, -3.4F, 0F, 0F, 0F, 0.2094F));
        PartDefinition p_lamina_der_1 = p_right_arm.addOrReplaceChild("lamina_der_1", CubeListBuilder.create()
                .texOffs(66, 26).addBox(-2.5F, -0.5F, -3F, 5F, 1F, 6F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(-3.1F, -2.3F, 0F, 0F, 0F, 0.6632F));
        PartDefinition p_lamina_der_2 = p_right_arm.addOrReplaceChild("lamina_der_2", CubeListBuilder.create()
                .texOffs(18, 34).addBox(-2F, -0.5F, -2.5F, 4F, 1F, 5F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(-4.4F, -0.2F, 0F, 0F, 0F, 1.0821F));
        PartDefinition p_colmillo_hombro_izq = p_left_arm.addOrReplaceChild("colmillo_hombro_izq", CubeListBuilder.create()
                .texOffs(48, 40).addBox(-1F, -1F, -1F, 2F, 1F, 2F, CubeDeformation.NONE)
                .texOffs(72, 34).addBox(-0.5F, -6F, -0.5F, 1F, 5F, 1F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(2.6F, -4.2F, 0.3F, -0.3142F, 0F, -0.4189F));
        PartDefinition p_colmillo_hombro_izq_b = p_left_arm.addOrReplaceChild("colmillo_hombro_izq_b", CubeListBuilder.create()
                .texOffs(56, 40).addBox(-1F, -1F, -1F, 2F, 1F, 2F, CubeDeformation.NONE)
                .texOffs(32, 40).addBox(-0.5F, -4F, -0.5F, 1F, 3F, 1F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(1.6F, -4F, 2.2F, -0.6981F, 0F, -0.2443F));
        PartDefinition p_colmillo_hombro_der = p_right_arm.addOrReplaceChild("colmillo_hombro_der", CubeListBuilder.create()
                .texOffs(64, 40).addBox(-1F, -1F, -1F, 2F, 1F, 2F, CubeDeformation.NONE)
                .texOffs(76, 34).addBox(-0.5F, -6F, -0.5F, 1F, 5F, 1F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(-2.6F, -4.2F, 0.3F, -0.3142F, 0F, 0.4189F));
        PartDefinition p_colmillo_hombro_der_b = p_right_arm.addOrReplaceChild("colmillo_hombro_der_b", CubeListBuilder.create()
                .texOffs(72, 40).addBox(-1F, -1F, -1F, 2F, 1F, 2F, CubeDeformation.NONE)
                .texOffs(36, 40).addBox(-0.5F, -4F, -0.5F, 1F, 3F, 1F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(-1.6F, -4F, 2.2F, -0.6981F, 0F, 0.2443F));
        PartDefinition p_gola_detras = p_body.addOrReplaceChild("gola_detras", CubeListBuilder.create()
                .texOffs(80, 34).addBox(-4.5F, -4F, -0.5F, 9F, 4F, 1F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, 0.2F, 2.6F, -0.3142F, 0F, 0F));
        PartDefinition p_gola_izq = p_body.addOrReplaceChild("gola_izq", CubeListBuilder.create()
                .texOffs(88, 26).addBox(-0.5F, -3F, -2.5F, 1F, 3F, 4F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(4.4F, 0.2F, 0.6F, -0.1396F, 0F, -0.2443F));
        PartDefinition p_gola_der = p_body.addOrReplaceChild("gola_der", CubeListBuilder.create()
                .texOffs(98, 26).addBox(-0.5F, -3F, -2.5F, 1F, 3F, 4F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(-4.4F, 0.2F, 0.6F, -0.1396F, 0F, 0.2443F));
        PartDefinition p_gola_delante = p_body.addOrReplaceChild("gola_delante", CubeListBuilder.create()
                .texOffs(8, 45).addBox(-3F, -1F, -0.5F, 6F, 1F, 1F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, 0.2F, -2.9F, 0.2094F, 0F, 0F));
        PartDefinition p_halo_pecho = p_body.addOrReplaceChild("halo_pecho", CubeListBuilder.create()
                .texOffs(56, 16).addBox(-4.5F, -4.5F, 0F, 9F, 9F, 0F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, 4.6F, -3.75F, 0F, 0F, 0F));
        PartDefinition p_sol_pecho = p_body.addOrReplaceChild("sol_pecho", CubeListBuilder.create()
                .texOffs(36, 34).addBox(-2.5F, -2.5F, -0.5F, 5F, 5F, 1F, CubeDeformation.NONE)
                .texOffs(40, 45).addBox(-0.5F, -4F, -0.3F, 1F, 1F, 1F, CubeDeformation.NONE)
                .texOffs(44, 45).addBox(-0.5F, 3F, -0.3F, 1F, 1F, 1F, CubeDeformation.NONE)
                .texOffs(48, 45).addBox(-4F, -0.5F, -0.3F, 1F, 1F, 1F, CubeDeformation.NONE)
                .texOffs(52, 45).addBox(3F, -0.5F, -0.3F, 1F, 1F, 1F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, 4.6F, -3.1F, 0F, 0F, 0F));
        PartDefinition p_cristal_espalda_0 = p_body.addOrReplaceChild("cristal_espalda_0", CubeListBuilder.create()
                .texOffs(36, 26).addBox(-1F, -6F, -1F, 2F, 6F, 2F, CubeDeformation.NONE)
                .texOffs(56, 45).addBox(-0.5F, -7F, -0.5F, 1F, 1F, 1F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, 1F, 2.9F, -0.9076F, 0F, 0F));
        PartDefinition p_cristal_espalda_1 = p_body.addOrReplaceChild("cristal_espalda_1", CubeListBuilder.create()
                .texOffs(108, 26).addBox(-1F, -5F, -1F, 2F, 5F, 2F, CubeDeformation.NONE)
                .texOffs(60, 45).addBox(-0.5F, -6F, -0.5F, 1F, 1F, 1F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, 3.6F, 2.9F, -0.9076F, 0F, 0F));
        PartDefinition p_cristal_espalda_2 = p_body.addOrReplaceChild("cristal_espalda_2", CubeListBuilder.create()
                .texOffs(64, 34).addBox(-1F, -4F, -1F, 2F, 4F, 2F, CubeDeformation.NONE)
                .texOffs(64, 45).addBox(-0.5F, -5F, -0.5F, 1F, 1F, 1F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, 6.2F, 2.9F, -0.9076F, 0F, 0F));
        PartDefinition p_cristal_espalda_3 = p_body.addOrReplaceChild("cristal_espalda_3", CubeListBuilder.create()
                .texOffs(100, 34).addBox(-1F, -3F, -1F, 2F, 3F, 2F, CubeDeformation.NONE)
                .texOffs(68, 45).addBox(-0.5F, -4F, -0.5F, 1F, 1F, 1F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, 8.6F, 2.9F, -0.9076F, 0F, 0F));
        PartDefinition p_cristal_omoplato_izq = p_body.addOrReplaceChild("cristal_omoplato_izq", CubeListBuilder.create()
                .texOffs(40, 40).addBox(-0.5F, -3F, -0.5F, 1F, 3F, 1F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(2.6F, 2.4F, 2.9F, -0.6981F, 0F, -0.5236F));
        PartDefinition p_cristal_omoplato_der = p_body.addOrReplaceChild("cristal_omoplato_der", CubeListBuilder.create()
                .texOffs(44, 40).addBox(-0.5F, -3F, -0.5F, 1F, 3F, 1F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(-2.6F, 2.4F, 2.9F, -0.6981F, 0F, 0.5236F));
        return LayerDefinition.create(malla, 128, 64);
    }

    private static LayerDefinition jade_grebas() {
        MeshDefinition malla = new MeshDefinition();
        PartDefinition raiz = malla.getRoot();
        PartDefinition p_head = raiz.addOrReplaceChild("head", CubeListBuilder.create(), PartPose.offset(0F, 0F, 0F));
        PartDefinition p_body = raiz.addOrReplaceChild("body", CubeListBuilder.create(), PartPose.offset(0F, 0F, 0F));
        PartDefinition p_right_arm = raiz.addOrReplaceChild("right_arm", CubeListBuilder.create(), PartPose.offset(-5F, 2F, 0F));
        PartDefinition p_left_arm = raiz.addOrReplaceChild("left_arm", CubeListBuilder.create(), PartPose.offset(5F, 2F, 0F));
        PartDefinition p_right_leg = raiz.addOrReplaceChild("right_leg", CubeListBuilder.create(), PartPose.offset(-1.9F, 12F, 0F));
        PartDefinition p_left_leg = raiz.addOrReplaceChild("left_leg", CubeListBuilder.create(), PartPose.offset(1.9F, 12F, 0F));
        PartDefinition p_cintura_jade = p_body.addOrReplaceChild("cintura_jade", CubeListBuilder.create()
                .texOffs(32, 16).addBox(-4F, 7F, -2F, 8F, 5F, 4F, new CubeDeformation(0.55F)),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        PartDefinition p_pernera_right_leg = p_right_leg.addOrReplaceChild("pernera_right_leg", CubeListBuilder.create()
                .texOffs(56, 0).addBox(-2F, 0F, -2F, 4F, 9F, 4F, new CubeDeformation(0.5F)),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        PartDefinition p_pernera_left_leg = p_left_leg.addOrReplaceChild("pernera_left_leg", CubeListBuilder.create()
                .texOffs(72, 0).addBox(-2F, 0F, -2F, 4F, 9F, 4F, new CubeDeformation(0.5F)),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        PartDefinition p_faldon_delante_izq = p_body.addOrReplaceChild("faldon_delante_izq", CubeListBuilder.create()
                .texOffs(108, 34).addBox(-1.5F, 0F, -0.5F, 3F, 4F, 1F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(1.9F, 11.6F, -2.7F, 0.1396F, 0F, -0.1745F));
        PartDefinition p_faldon_delante_der = p_body.addOrReplaceChild("faldon_delante_der", CubeListBuilder.create()
                .texOffs(116, 34).addBox(-1.5F, 0F, -0.5F, 3F, 4F, 1F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(-1.9F, 11.6F, -2.7F, 0.1396F, 0F, 0.1745F));
        PartDefinition p_faldon_detras_izq = p_body.addOrReplaceChild("faldon_detras_izq", CubeListBuilder.create()
                .texOffs(0, 40).addBox(-1.5F, 0F, -0.5F, 3F, 4F, 1F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(1.9F, 11.6F, 2.7F, -0.1396F, 0F, -0.1745F));
        PartDefinition p_faldon_detras_der = p_body.addOrReplaceChild("faldon_detras_der", CubeListBuilder.create()
                .texOffs(8, 40).addBox(-1.5F, 0F, -0.5F, 3F, 4F, 1F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(-1.9F, 11.6F, 2.7F, -0.1396F, 0F, 0.1745F));
        return LayerDefinition.create(malla, 128, 64);
    }

    private static LayerDefinition jade_botas() {
        MeshDefinition malla = new MeshDefinition();
        PartDefinition raiz = malla.getRoot();
        PartDefinition p_head = raiz.addOrReplaceChild("head", CubeListBuilder.create(), PartPose.offset(0F, 0F, 0F));
        PartDefinition p_body = raiz.addOrReplaceChild("body", CubeListBuilder.create(), PartPose.offset(0F, 0F, 0F));
        PartDefinition p_right_arm = raiz.addOrReplaceChild("right_arm", CubeListBuilder.create(), PartPose.offset(-5F, 2F, 0F));
        PartDefinition p_left_arm = raiz.addOrReplaceChild("left_arm", CubeListBuilder.create(), PartPose.offset(5F, 2F, 0F));
        PartDefinition p_right_leg = raiz.addOrReplaceChild("right_leg", CubeListBuilder.create(), PartPose.offset(-1.9F, 12F, 0F));
        PartDefinition p_left_leg = raiz.addOrReplaceChild("left_leg", CubeListBuilder.create(), PartPose.offset(1.9F, 12F, 0F));
        PartDefinition p_bota_left_leg = p_left_leg.addOrReplaceChild("bota_left_leg", CubeListBuilder.create()
                .texOffs(0, 16).addBox(-2F, 6F, -2F, 4F, 6F, 4F, new CubeDeformation(1F)),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        PartDefinition p_garra_izq_0 = p_left_leg.addOrReplaceChild("garra_izq_0", CubeListBuilder.create()
                .texOffs(92, 40).addBox(-0.5F, -0.5F, -2F, 1F, 1F, 2F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(-1.6F, 11.6F, -3F, -0.4363F, 0F, 0F));
        PartDefinition p_garra_izq_1 = p_left_leg.addOrReplaceChild("garra_izq_1", CubeListBuilder.create()
                .texOffs(98, 40).addBox(-0.5F, -0.5F, -2F, 1F, 1F, 2F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, 11.6F, -3F, -0.4363F, 0F, 0F));
        PartDefinition p_garra_izq_2 = p_left_leg.addOrReplaceChild("garra_izq_2", CubeListBuilder.create()
                .texOffs(104, 40).addBox(-0.5F, -0.5F, -2F, 1F, 1F, 2F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(1.6F, 11.6F, -3F, -0.4363F, 0F, 0F));
        PartDefinition p_bota_right_leg = p_right_leg.addOrReplaceChild("bota_right_leg", CubeListBuilder.create()
                .texOffs(16, 16).addBox(-2F, 6F, -2F, 4F, 6F, 4F, new CubeDeformation(1F)),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        PartDefinition p_garra_der_0 = p_right_leg.addOrReplaceChild("garra_der_0", CubeListBuilder.create()
                .texOffs(110, 40).addBox(-0.5F, -0.5F, -2F, 1F, 1F, 2F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(-1.6F, 11.6F, -3F, -0.4363F, 0F, 0F));
        PartDefinition p_garra_der_1 = p_right_leg.addOrReplaceChild("garra_der_1", CubeListBuilder.create()
                .texOffs(116, 40).addBox(-0.5F, -0.5F, -2F, 1F, 1F, 2F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, 11.6F, -3F, -0.4363F, 0F, 0F));
        PartDefinition p_garra_der_2 = p_right_leg.addOrReplaceChild("garra_der_2", CubeListBuilder.create()
                .texOffs(122, 40).addBox(-0.5F, -0.5F, -2F, 1F, 1F, 2F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(1.6F, 11.6F, -3F, -0.4363F, 0F, 0F));
        return LayerDefinition.create(malla, 128, 64);
    }

    private static LayerDefinition vendaval_casco() {
        MeshDefinition malla = new MeshDefinition();
        PartDefinition raiz = malla.getRoot();
        PartDefinition p_head = raiz.addOrReplaceChild("head", CubeListBuilder.create(), PartPose.offset(0F, 0F, 0F));
        PartDefinition p_body = raiz.addOrReplaceChild("body", CubeListBuilder.create(), PartPose.offset(0F, 0F, 0F));
        PartDefinition p_right_arm = raiz.addOrReplaceChild("right_arm", CubeListBuilder.create(), PartPose.offset(-5F, 2F, 0F));
        PartDefinition p_left_arm = raiz.addOrReplaceChild("left_arm", CubeListBuilder.create(), PartPose.offset(5F, 2F, 0F));
        PartDefinition p_right_leg = raiz.addOrReplaceChild("right_leg", CubeListBuilder.create(), PartPose.offset(-1.9F, 12F, 0F));
        PartDefinition p_left_leg = raiz.addOrReplaceChild("left_leg", CubeListBuilder.create(), PartPose.offset(1.9F, 12F, 0F));
        PartDefinition p_casco_vendaval = p_head.addOrReplaceChild("casco_vendaval", CubeListBuilder.create()
                .texOffs(0, 0).addBox(-4F, -8F, -4F, 8F, 8F, 8F, new CubeDeformation(1F)),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        PartDefinition p_ala_casco_izq = p_head.addOrReplaceChild("ala_casco_izq", CubeListBuilder.create(),
                PartPose.offsetAndRotation(4.6F, -5.5F, 1.5F, 0F, -0.3491F, 0F));
        PartDefinition p_pluma_casco_izq_0 = p_ala_casco_izq.addOrReplaceChild("pluma_casco_izq_0", CubeListBuilder.create()
                .texOffs(36, 16).addBox(0F, -8F, 0F, 0F, 8F, 3F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, 0F, 0F, -0.1745F, 0F, 0F));
        PartDefinition p_pluma_casco_izq_1 = p_ala_casco_izq.addOrReplaceChild("pluma_casco_izq_1", CubeListBuilder.create()
                .texOffs(112, 16).addBox(0F, -7F, 0F, 0F, 7F, 3F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, 0F, 0F, -0.5585F, 0F, 0F));
        PartDefinition p_pluma_casco_izq_2 = p_ala_casco_izq.addOrReplaceChild("pluma_casco_izq_2", CubeListBuilder.create()
                .texOffs(18, 38).addBox(0F, -5F, 0F, 0F, 5F, 3F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, 0F, 0F, -0.9425F, 0F, 0F));
        PartDefinition p_antena_izq = p_head.addOrReplaceChild("antena_izq", CubeListBuilder.create()
                .texOffs(118, 38).addBox(-0.5F, -6F, -0.5F, 1F, 6F, 1F, CubeDeformation.NONE)
                .texOffs(0, 52).addBox(-0.5F, -7F, -0.5F, 1F, 1F, 1F, CubeDeformation.NONE)
                .texOffs(48, 46).addBox(0F, -6F, -2F, 0F, 4F, 2F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(1.6F, -8.6F, -2F, -0.384F, 0F, 0.2793F));
        PartDefinition p_ala_casco_der = p_head.addOrReplaceChild("ala_casco_der", CubeListBuilder.create(),
                PartPose.offsetAndRotation(-4.6F, -5.5F, 1.5F, 0F, 0.3491F, 0F));
        PartDefinition p_pluma_casco_der_0 = p_ala_casco_der.addOrReplaceChild("pluma_casco_der_0", CubeListBuilder.create()
                .texOffs(42, 16).addBox(0F, -8F, 0F, 0F, 8F, 3F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, 0F, 0F, -0.1745F, 0F, 0F));
        PartDefinition p_pluma_casco_der_1 = p_ala_casco_der.addOrReplaceChild("pluma_casco_der_1", CubeListBuilder.create()
                .texOffs(118, 16).addBox(0F, -7F, 0F, 0F, 7F, 3F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, 0F, 0F, -0.5585F, 0F, 0F));
        PartDefinition p_pluma_casco_der_2 = p_ala_casco_der.addOrReplaceChild("pluma_casco_der_2", CubeListBuilder.create()
                .texOffs(24, 38).addBox(0F, -5F, 0F, 0F, 5F, 3F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, 0F, 0F, -0.9425F, 0F, 0F));
        PartDefinition p_antena_der = p_head.addOrReplaceChild("antena_der", CubeListBuilder.create()
                .texOffs(122, 38).addBox(-0.5F, -6F, -0.5F, 1F, 6F, 1F, CubeDeformation.NONE)
                .texOffs(4, 52).addBox(-0.5F, -7F, -0.5F, 1F, 1F, 1F, CubeDeformation.NONE)
                .texOffs(52, 46).addBox(0F, -6F, -2F, 0F, 4F, 2F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(-1.6F, -8.6F, -2F, -0.384F, 0F, -0.2793F));
        return LayerDefinition.create(malla, 128, 64);
    }

    private static LayerDefinition vendaval_pechera() {
        MeshDefinition malla = new MeshDefinition();
        PartDefinition raiz = malla.getRoot();
        PartDefinition p_head = raiz.addOrReplaceChild("head", CubeListBuilder.create(), PartPose.offset(0F, 0F, 0F));
        PartDefinition p_body = raiz.addOrReplaceChild("body", CubeListBuilder.create(), PartPose.offset(0F, 0F, 0F));
        PartDefinition p_right_arm = raiz.addOrReplaceChild("right_arm", CubeListBuilder.create(), PartPose.offset(-5F, 2F, 0F));
        PartDefinition p_left_arm = raiz.addOrReplaceChild("left_arm", CubeListBuilder.create(), PartPose.offset(5F, 2F, 0F));
        PartDefinition p_right_leg = raiz.addOrReplaceChild("right_leg", CubeListBuilder.create(), PartPose.offset(-1.9F, 12F, 0F));
        PartDefinition p_left_leg = raiz.addOrReplaceChild("left_leg", CubeListBuilder.create(), PartPose.offset(1.9F, 12F, 0F));
        PartDefinition p_pechera_vendaval = p_body.addOrReplaceChild("pechera_vendaval", CubeListBuilder.create()
                .texOffs(32, 0).addBox(-4F, 0F, -2F, 8F, 12F, 4F, new CubeDeformation(0.85F)),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        PartDefinition p_manga_right_arm = p_right_arm.addOrReplaceChild("manga_right_arm", CubeListBuilder.create()
                .texOffs(48, 16).addBox(-3F, -2F, -2F, 4F, 6F, 4F, new CubeDeformation(0.85F)),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        PartDefinition p_manga_left_arm = p_left_arm.addOrReplaceChild("manga_left_arm", CubeListBuilder.create()
                .texOffs(64, 16).addBox(-1F, -2F, -2F, 4F, 6F, 4F, new CubeDeformation(0.85F)),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        PartDefinition p_lamina_izq_0 = p_left_arm.addOrReplaceChild("lamina_izq_0", CubeListBuilder.create()
                .texOffs(54, 28).addBox(-3.5F, -1F, -3.5F, 7F, 1F, 7F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0.8F, -3.4F, 0F, 0F, 0F, -0.2094F));
        PartDefinition p_lamina_izq_1 = p_left_arm.addOrReplaceChild("lamina_izq_1", CubeListBuilder.create()
                .texOffs(42, 38).addBox(-2.5F, -0.5F, -3F, 5F, 1F, 6F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(3.1F, -2.3F, 0F, 0F, 0F, -0.6632F));
        PartDefinition p_lamina_izq_2 = p_left_arm.addOrReplaceChild("lamina_izq_2", CubeListBuilder.create()
                .texOffs(0, 46).addBox(-2F, -0.5F, -2.5F, 4F, 1F, 5F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(4.4F, -0.2F, 0F, 0F, 0F, -1.0821F));
        PartDefinition p_lamina_der_0 = p_right_arm.addOrReplaceChild("lamina_der_0", CubeListBuilder.create()
                .texOffs(82, 28).addBox(-3.5F, -1F, -3.5F, 7F, 1F, 7F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(-0.8F, -3.4F, 0F, 0F, 0F, 0.2094F));
        PartDefinition p_lamina_der_1 = p_right_arm.addOrReplaceChild("lamina_der_1", CubeListBuilder.create()
                .texOffs(64, 38).addBox(-2.5F, -0.5F, -3F, 5F, 1F, 6F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(-3.1F, -2.3F, 0F, 0F, 0F, 0.6632F));
        PartDefinition p_lamina_der_2 = p_right_arm.addOrReplaceChild("lamina_der_2", CubeListBuilder.create()
                .texOffs(18, 46).addBox(-2F, -0.5F, -2.5F, 4F, 1F, 5F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(-4.4F, -0.2F, 0F, 0F, 0F, 1.0821F));
        PartDefinition p_pluma_hombro_izq_0 = p_left_arm.addOrReplaceChild("pluma_hombro_izq_0", CubeListBuilder.create()
                .texOffs(24, 16).addBox(0F, -9F, -1F, 0F, 9F, 3F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(2F, -3.8F, 0.8F, -0.2443F, 0F, -0.2443F));
        PartDefinition p_pluma_hombro_izq_1 = p_left_arm.addOrReplaceChild("pluma_hombro_izq_1", CubeListBuilder.create()
                .texOffs(0, 28).addBox(0F, -7F, -1F, 0F, 7F, 3F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(2.9F, -3.2F, 0.8F, -0.4887F, 0F, -0.5236F));
        PartDefinition p_pluma_hombro_izq_2 = p_left_arm.addOrReplaceChild("pluma_hombro_izq_2", CubeListBuilder.create()
                .texOffs(30, 38).addBox(0F, -5F, -1F, 0F, 5F, 3F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(3.8F, -2.6F, 0.8F, -0.733F, 0F, -0.8029F));
        PartDefinition p_pluma_hombro_der_0 = p_right_arm.addOrReplaceChild("pluma_hombro_der_0", CubeListBuilder.create()
                .texOffs(30, 16).addBox(0F, -9F, -1F, 0F, 9F, 3F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(-2F, -3.8F, 0.8F, -0.2443F, 0F, 0.2443F));
        PartDefinition p_pluma_hombro_der_1 = p_right_arm.addOrReplaceChild("pluma_hombro_der_1", CubeListBuilder.create()
                .texOffs(6, 28).addBox(0F, -7F, -1F, 0F, 7F, 3F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(-2.9F, -3.2F, 0.8F, -0.4887F, 0F, 0.5236F));
        PartDefinition p_pluma_hombro_der_2 = p_right_arm.addOrReplaceChild("pluma_hombro_der_2", CubeListBuilder.create()
                .texOffs(36, 38).addBox(0F, -5F, -1F, 0F, 5F, 3F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(-3.8F, -2.6F, 0.8F, -0.733F, 0F, 0.8029F));
        PartDefinition p_gola_detras = p_body.addOrReplaceChild("gola_detras", CubeListBuilder.create()
                .texOffs(56, 46).addBox(-4.5F, -4F, -0.5F, 9F, 4F, 1F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, 0.2F, 2.6F, -0.3142F, 0F, 0F));
        PartDefinition p_gola_izq = p_body.addOrReplaceChild("gola_izq", CubeListBuilder.create()
                .texOffs(86, 38).addBox(-0.5F, -3F, -2.5F, 1F, 3F, 4F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(4.4F, 0.2F, 0.6F, -0.1396F, 0F, -0.2443F));
        PartDefinition p_gola_der = p_body.addOrReplaceChild("gola_der", CubeListBuilder.create()
                .texOffs(96, 38).addBox(-0.5F, -3F, -2.5F, 1F, 3F, 4F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(-4.4F, 0.2F, 0.6F, -0.1396F, 0F, 0.2443F));
        PartDefinition p_gola_delante = p_body.addOrReplaceChild("gola_delante", CubeListBuilder.create()
                .texOffs(114, 46).addBox(-3F, -1F, -0.5F, 6F, 1F, 1F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, 0.2F, -2.9F, 0.2094F, 0F, 0F));
        PartDefinition p_halo_pecho = p_body.addOrReplaceChild("halo_pecho", CubeListBuilder.create()
                .texOffs(36, 28).addBox(-4.5F, -4.5F, 0F, 9F, 9F, 0F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, 4.6F, -3.75F, 0F, 0F, 0F));
        PartDefinition p_ojo_pecho = p_body.addOrReplaceChild("ojo_pecho", CubeListBuilder.create()
                .texOffs(76, 46).addBox(-2F, -2F, -0.5F, 4F, 4F, 1F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, 4.6F, -3.1F, 0F, 0F, 0F));
        PartDefinition p_ala_izq = p_body.addOrReplaceChild("ala_izq", CubeListBuilder.create(),
                PartPose.offsetAndRotation(1F, 3F, 3F, 0F, -0.4189F, -0.0698F));
        PartDefinition p_ala_alta_izq = p_ala_izq.addOrReplaceChild("ala_alta_izq", CubeListBuilder.create()
                .texOffs(88, 0).addBox(0F, -11F, 0F, 12F, 12F, 0F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, -0.2793F));
        PartDefinition p_ala_baja_izq = p_ala_izq.addOrReplaceChild("ala_baja_izq", CubeListBuilder.create()
                .texOffs(110, 28).addBox(0F, 0F, 0F, 9F, 8F, 0F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, 1.5F, 0F, 0F, 0F, 0.4538F));
        PartDefinition p_ala_der = p_body.addOrReplaceChild("ala_der", CubeListBuilder.create(),
                PartPose.offsetAndRotation(-1F, 3F, 3F, 0F, 0.4189F, 0.0698F));
        PartDefinition p_ala_alta_der = p_ala_der.addOrReplaceChild("ala_alta_der", CubeListBuilder.create()
                .texOffs(0, 16).addBox(-12F, -11F, 0F, 12F, 12F, 0F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0.2793F));
        PartDefinition p_ala_baja_der = p_ala_der.addOrReplaceChild("ala_baja_der", CubeListBuilder.create()
                .texOffs(0, 38).addBox(-9F, 0F, 0F, 9F, 8F, 0F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, 1.5F, 0F, 0F, 0F, -0.4538F));
        return LayerDefinition.create(malla, 128, 64);
    }

    private static LayerDefinition vendaval_grebas() {
        MeshDefinition malla = new MeshDefinition();
        PartDefinition raiz = malla.getRoot();
        PartDefinition p_head = raiz.addOrReplaceChild("head", CubeListBuilder.create(), PartPose.offset(0F, 0F, 0F));
        PartDefinition p_body = raiz.addOrReplaceChild("body", CubeListBuilder.create(), PartPose.offset(0F, 0F, 0F));
        PartDefinition p_right_arm = raiz.addOrReplaceChild("right_arm", CubeListBuilder.create(), PartPose.offset(-5F, 2F, 0F));
        PartDefinition p_left_arm = raiz.addOrReplaceChild("left_arm", CubeListBuilder.create(), PartPose.offset(5F, 2F, 0F));
        PartDefinition p_right_leg = raiz.addOrReplaceChild("right_leg", CubeListBuilder.create(), PartPose.offset(-1.9F, 12F, 0F));
        PartDefinition p_left_leg = raiz.addOrReplaceChild("left_leg", CubeListBuilder.create(), PartPose.offset(1.9F, 12F, 0F));
        PartDefinition p_cintura_vendaval = p_body.addOrReplaceChild("cintura_vendaval", CubeListBuilder.create()
                .texOffs(12, 28).addBox(-4F, 7F, -2F, 8F, 5F, 4F, new CubeDeformation(0.55F)),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        PartDefinition p_pernera_right_leg = p_right_leg.addOrReplaceChild("pernera_right_leg", CubeListBuilder.create()
                .texOffs(56, 0).addBox(-2F, 0F, -2F, 4F, 9F, 4F, new CubeDeformation(0.5F)),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        PartDefinition p_pernera_left_leg = p_left_leg.addOrReplaceChild("pernera_left_leg", CubeListBuilder.create()
                .texOffs(72, 0).addBox(-2F, 0F, -2F, 4F, 9F, 4F, new CubeDeformation(0.5F)),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        PartDefinition p_pluma_cadera_izq = p_body.addOrReplaceChild("pluma_cadera_izq", CubeListBuilder.create()
                .texOffs(86, 46).addBox(-1.5F, 0F, 0F, 3F, 5F, 0F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(2.4F, 11F, -2.6F, 0.1396F, 0F, -0.2094F));
        PartDefinition p_pluma_cadera_der = p_body.addOrReplaceChild("pluma_cadera_der", CubeListBuilder.create()
                .texOffs(92, 46).addBox(-1.5F, 0F, 0F, 3F, 5F, 0F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(-2.4F, 11F, -2.6F, 0.1396F, 0F, 0.2094F));
        return LayerDefinition.create(malla, 128, 64);
    }

    private static LayerDefinition vendaval_botas() {
        MeshDefinition malla = new MeshDefinition();
        PartDefinition raiz = malla.getRoot();
        PartDefinition p_head = raiz.addOrReplaceChild("head", CubeListBuilder.create(), PartPose.offset(0F, 0F, 0F));
        PartDefinition p_body = raiz.addOrReplaceChild("body", CubeListBuilder.create(), PartPose.offset(0F, 0F, 0F));
        PartDefinition p_right_arm = raiz.addOrReplaceChild("right_arm", CubeListBuilder.create(), PartPose.offset(-5F, 2F, 0F));
        PartDefinition p_left_arm = raiz.addOrReplaceChild("left_arm", CubeListBuilder.create(), PartPose.offset(5F, 2F, 0F));
        PartDefinition p_right_leg = raiz.addOrReplaceChild("right_leg", CubeListBuilder.create(), PartPose.offset(-1.9F, 12F, 0F));
        PartDefinition p_left_leg = raiz.addOrReplaceChild("left_leg", CubeListBuilder.create(), PartPose.offset(1.9F, 12F, 0F));
        PartDefinition p_bota_left_leg = p_left_leg.addOrReplaceChild("bota_left_leg", CubeListBuilder.create()
                .texOffs(80, 16).addBox(-2F, 6F, -2F, 4F, 6F, 4F, new CubeDeformation(1F)),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        PartDefinition p_ala_talon_izq = p_left_leg.addOrReplaceChild("ala_talon_izq", CubeListBuilder.create(),
                PartPose.offsetAndRotation(3.2F, 8.5F, 1F, 0F, -0.5236F, 0F));
        PartDefinition p_pluma_talon_izq_0 = p_ala_talon_izq.addOrReplaceChild("pluma_talon_izq_0", CubeListBuilder.create()
                .texOffs(106, 38).addBox(0F, -4F, 0F, 0F, 4F, 3F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, 0F, 0F, -0.2618F, 0F, 0F));
        PartDefinition p_pluma_talon_izq_1 = p_ala_talon_izq.addOrReplaceChild("pluma_talon_izq_1", CubeListBuilder.create()
                .texOffs(36, 46).addBox(0F, -3F, 0F, 0F, 3F, 3F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, 0F, 0F, -0.7854F, 0F, 0F));
        PartDefinition p_puntera_izq = p_left_leg.addOrReplaceChild("puntera_izq", CubeListBuilder.create()
                .texOffs(98, 46).addBox(-1F, -0.5F, -1.5F, 2F, 1F, 2F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, 11.5F, -3F, 0F, 0F, 0F));
        PartDefinition p_bota_right_leg = p_right_leg.addOrReplaceChild("bota_right_leg", CubeListBuilder.create()
                .texOffs(96, 16).addBox(-2F, 6F, -2F, 4F, 6F, 4F, new CubeDeformation(1F)),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        PartDefinition p_ala_talon_der = p_right_leg.addOrReplaceChild("ala_talon_der", CubeListBuilder.create(),
                PartPose.offsetAndRotation(-3.2F, 8.5F, 1F, 0F, 0.5236F, 0F));
        PartDefinition p_pluma_talon_der_0 = p_ala_talon_der.addOrReplaceChild("pluma_talon_der_0", CubeListBuilder.create()
                .texOffs(112, 38).addBox(0F, -4F, 0F, 0F, 4F, 3F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, 0F, 0F, -0.2618F, 0F, 0F));
        PartDefinition p_pluma_talon_der_1 = p_ala_talon_der.addOrReplaceChild("pluma_talon_der_1", CubeListBuilder.create()
                .texOffs(42, 46).addBox(0F, -3F, 0F, 0F, 3F, 3F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, 0F, 0F, -0.7854F, 0F, 0F));
        PartDefinition p_puntera_der = p_right_leg.addOrReplaceChild("puntera_der", CubeListBuilder.create()
                .texOffs(106, 46).addBox(-1F, -0.5F, -1.5F, 2F, 1F, 2F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, 11.5F, -3F, 0F, 0F, 0F));
        return LayerDefinition.create(malla, 128, 64);
    }

    private static LayerDefinition solar_casco() {
        MeshDefinition malla = new MeshDefinition();
        PartDefinition raiz = malla.getRoot();
        PartDefinition p_head = raiz.addOrReplaceChild("head", CubeListBuilder.create(), PartPose.offset(0F, 0F, 0F));
        PartDefinition p_body = raiz.addOrReplaceChild("body", CubeListBuilder.create(), PartPose.offset(0F, 0F, 0F));
        PartDefinition p_right_arm = raiz.addOrReplaceChild("right_arm", CubeListBuilder.create(), PartPose.offset(-5F, 2F, 0F));
        PartDefinition p_left_arm = raiz.addOrReplaceChild("left_arm", CubeListBuilder.create(), PartPose.offset(5F, 2F, 0F));
        PartDefinition p_right_leg = raiz.addOrReplaceChild("right_leg", CubeListBuilder.create(), PartPose.offset(-1.9F, 12F, 0F));
        PartDefinition p_left_leg = raiz.addOrReplaceChild("left_leg", CubeListBuilder.create(), PartPose.offset(1.9F, 12F, 0F));
        PartDefinition p_casco_solar = p_head.addOrReplaceChild("casco_solar", CubeListBuilder.create()
                .texOffs(18, 0).addBox(-4F, -8F, -4F, 8F, 8F, 8F, new CubeDeformation(1F)),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        PartDefinition p_cuerno_izq = p_head.addOrReplaceChild("cuerno_izq", CubeListBuilder.create()
                .texOffs(20, 45).addBox(-1F, -3F, -1F, 2F, 3F, 2F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(4.7F, -5.6F, -0.5F, 0.2094F, 0F, 1.2566F));
        PartDefinition p_cuerno_izq_2 = p_cuerno_izq.addOrReplaceChild("cuerno_izq_2", CubeListBuilder.create()
                .texOffs(28, 45).addBox(-1F, -3F, -1F, 2F, 3F, 2F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, -2.8F, 0F, 0.1396F, 0F, -0.6981F));
        PartDefinition p_cuerno_izq_3 = p_cuerno_izq_2.addOrReplaceChild("cuerno_izq_3", CubeListBuilder.create()
                .texOffs(120, 45).addBox(-0.5F, -3F, -0.5F, 1F, 3F, 1F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, -2.8F, 0F, 0.1047F, 0F, -0.5236F));
        PartDefinition p_cuerno_izq_4 = p_cuerno_izq_3.addOrReplaceChild("cuerno_izq_4", CubeListBuilder.create()
                .texOffs(40, 50).addBox(-0.5F, -2F, -0.5F, 1F, 2F, 1F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, -2.8F, 0F, 0.0698F, 0F, -0.2094F));
        PartDefinition p_cuerno_der = p_head.addOrReplaceChild("cuerno_der", CubeListBuilder.create()
                .texOffs(36, 45).addBox(-1F, -3F, -1F, 2F, 3F, 2F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(-4.7F, -5.6F, -0.5F, 0.2094F, 0F, -1.2566F));
        PartDefinition p_cuerno_der_2 = p_cuerno_der.addOrReplaceChild("cuerno_der_2", CubeListBuilder.create()
                .texOffs(44, 45).addBox(-1F, -3F, -1F, 2F, 3F, 2F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, -2.8F, 0F, 0.1396F, 0F, 0.6981F));
        PartDefinition p_cuerno_der_3 = p_cuerno_der_2.addOrReplaceChild("cuerno_der_3", CubeListBuilder.create()
                .texOffs(124, 45).addBox(-0.5F, -3F, -0.5F, 1F, 3F, 1F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, -2.8F, 0F, 0.1047F, 0F, 0.5236F));
        PartDefinition p_cuerno_der_4 = p_cuerno_der_3.addOrReplaceChild("cuerno_der_4", CubeListBuilder.create()
                .texOffs(44, 50).addBox(-0.5F, -2F, -0.5F, 1F, 2F, 1F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, -2.8F, 0F, 0.0698F, 0F, 0.2094F));
        PartDefinition p_llama_corona = p_head.addOrReplaceChild("llama_corona", CubeListBuilder.create()
                .texOffs(0, 38).addBox(-2.5F, -7F, 0F, 5F, 7F, 0F, CubeDeformation.NONE)
                .texOffs(106, 0).addBox(0F, -7F, -2.5F, 0F, 7F, 5F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, -9F, -1F, 0F, 0F, 0F));
        PartDefinition p_halo = p_head.addOrReplaceChild("halo", CubeListBuilder.create(),
                PartPose.offsetAndRotation(0F, -4.5F, 5.6F, 0F, 0F, 0F));
        PartDefinition p_halo_aro_0 = p_halo.addOrReplaceChild("halo_aro_0", CubeListBuilder.create()
                .texOffs(62, 50).addBox(-2F, -7F, -0.5F, 4F, 1F, 1F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        PartDefinition p_halo_rayo_0 = p_halo.addOrReplaceChild("halo_rayo_0", CubeListBuilder.create()
                .texOffs(84, 45).addBox(-0.5F, -11F, -0.5F, 1F, 4F, 1F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0.2618F));
        PartDefinition p_halo_aro_1 = p_halo.addOrReplaceChild("halo_aro_1", CubeListBuilder.create()
                .texOffs(72, 50).addBox(-2F, -7F, -0.5F, 4F, 1F, 1F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0.5236F));
        PartDefinition p_halo_rayo_1 = p_halo.addOrReplaceChild("halo_rayo_1", CubeListBuilder.create()
                .texOffs(0, 50).addBox(-0.5F, -10F, -0.5F, 1F, 3F, 1F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0.7854F));
        PartDefinition p_halo_aro_2 = p_halo.addOrReplaceChild("halo_aro_2", CubeListBuilder.create()
                .texOffs(82, 50).addBox(-2F, -7F, -0.5F, 4F, 1F, 1F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 1.0472F));
        PartDefinition p_halo_rayo_2 = p_halo.addOrReplaceChild("halo_rayo_2", CubeListBuilder.create()
                .texOffs(88, 45).addBox(-0.5F, -11F, -0.5F, 1F, 4F, 1F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 1.309F));
        PartDefinition p_halo_aro_3 = p_halo.addOrReplaceChild("halo_aro_3", CubeListBuilder.create()
                .texOffs(92, 50).addBox(-2F, -7F, -0.5F, 4F, 1F, 1F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 1.5708F));
        PartDefinition p_halo_rayo_3 = p_halo.addOrReplaceChild("halo_rayo_3", CubeListBuilder.create()
                .texOffs(4, 50).addBox(-0.5F, -10F, -0.5F, 1F, 3F, 1F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 1.8326F));
        PartDefinition p_halo_aro_4 = p_halo.addOrReplaceChild("halo_aro_4", CubeListBuilder.create()
                .texOffs(102, 50).addBox(-2F, -7F, -0.5F, 4F, 1F, 1F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 2.0944F));
        PartDefinition p_halo_rayo_4 = p_halo.addOrReplaceChild("halo_rayo_4", CubeListBuilder.create()
                .texOffs(92, 45).addBox(-0.5F, -11F, -0.5F, 1F, 4F, 1F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 2.3562F));
        PartDefinition p_halo_aro_5 = p_halo.addOrReplaceChild("halo_aro_5", CubeListBuilder.create()
                .texOffs(112, 50).addBox(-2F, -7F, -0.5F, 4F, 1F, 1F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 2.618F));
        PartDefinition p_halo_rayo_5 = p_halo.addOrReplaceChild("halo_rayo_5", CubeListBuilder.create()
                .texOffs(8, 50).addBox(-0.5F, -10F, -0.5F, 1F, 3F, 1F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 2.8798F));
        PartDefinition p_halo_aro_6 = p_halo.addOrReplaceChild("halo_aro_6", CubeListBuilder.create()
                .texOffs(0, 54).addBox(-2F, -7F, -0.5F, 4F, 1F, 1F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 3.1416F));
        PartDefinition p_halo_rayo_6 = p_halo.addOrReplaceChild("halo_rayo_6", CubeListBuilder.create()
                .texOffs(96, 45).addBox(-0.5F, -11F, -0.5F, 1F, 4F, 1F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 3.4034F));
        PartDefinition p_halo_aro_7 = p_halo.addOrReplaceChild("halo_aro_7", CubeListBuilder.create()
                .texOffs(10, 54).addBox(-2F, -7F, -0.5F, 4F, 1F, 1F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 3.6652F));
        PartDefinition p_halo_rayo_7 = p_halo.addOrReplaceChild("halo_rayo_7", CubeListBuilder.create()
                .texOffs(12, 50).addBox(-0.5F, -10F, -0.5F, 1F, 3F, 1F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 3.927F));
        PartDefinition p_halo_aro_8 = p_halo.addOrReplaceChild("halo_aro_8", CubeListBuilder.create()
                .texOffs(20, 54).addBox(-2F, -7F, -0.5F, 4F, 1F, 1F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 4.1888F));
        PartDefinition p_halo_rayo_8 = p_halo.addOrReplaceChild("halo_rayo_8", CubeListBuilder.create()
                .texOffs(100, 45).addBox(-0.5F, -11F, -0.5F, 1F, 4F, 1F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 4.4506F));
        PartDefinition p_halo_aro_9 = p_halo.addOrReplaceChild("halo_aro_9", CubeListBuilder.create()
                .texOffs(30, 54).addBox(-2F, -7F, -0.5F, 4F, 1F, 1F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 4.7124F));
        PartDefinition p_halo_rayo_9 = p_halo.addOrReplaceChild("halo_rayo_9", CubeListBuilder.create()
                .texOffs(16, 50).addBox(-0.5F, -10F, -0.5F, 1F, 3F, 1F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 4.9742F));
        PartDefinition p_halo_aro_10 = p_halo.addOrReplaceChild("halo_aro_10", CubeListBuilder.create()
                .texOffs(40, 54).addBox(-2F, -7F, -0.5F, 4F, 1F, 1F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 5.236F));
        PartDefinition p_halo_rayo_10 = p_halo.addOrReplaceChild("halo_rayo_10", CubeListBuilder.create()
                .texOffs(104, 45).addBox(-0.5F, -11F, -0.5F, 1F, 4F, 1F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 5.4978F));
        PartDefinition p_halo_aro_11 = p_halo.addOrReplaceChild("halo_aro_11", CubeListBuilder.create()
                .texOffs(50, 54).addBox(-2F, -7F, -0.5F, 4F, 1F, 1F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 5.7596F));
        PartDefinition p_halo_rayo_11 = p_halo.addOrReplaceChild("halo_rayo_11", CubeListBuilder.create()
                .texOffs(20, 50).addBox(-0.5F, -10F, -0.5F, 1F, 3F, 1F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 6.0214F));
        return LayerDefinition.create(malla, 128, 64);
    }

    private static LayerDefinition solar_pechera() {
        MeshDefinition malla = new MeshDefinition();
        PartDefinition raiz = malla.getRoot();
        PartDefinition p_head = raiz.addOrReplaceChild("head", CubeListBuilder.create(), PartPose.offset(0F, 0F, 0F));
        PartDefinition p_body = raiz.addOrReplaceChild("body", CubeListBuilder.create(), PartPose.offset(0F, 0F, 0F));
        PartDefinition p_right_arm = raiz.addOrReplaceChild("right_arm", CubeListBuilder.create(), PartPose.offset(-5F, 2F, 0F));
        PartDefinition p_left_arm = raiz.addOrReplaceChild("left_arm", CubeListBuilder.create(), PartPose.offset(5F, 2F, 0F));
        PartDefinition p_right_leg = raiz.addOrReplaceChild("right_leg", CubeListBuilder.create(), PartPose.offset(-1.9F, 12F, 0F));
        PartDefinition p_left_leg = raiz.addOrReplaceChild("left_leg", CubeListBuilder.create(), PartPose.offset(1.9F, 12F, 0F));
        PartDefinition p_pechera_solar = p_body.addOrReplaceChild("pechera_solar", CubeListBuilder.create()
                .texOffs(50, 0).addBox(-4F, 0F, -2F, 8F, 12F, 4F, new CubeDeformation(0.85F)),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        PartDefinition p_manga_right_arm = p_right_arm.addOrReplaceChild("manga_right_arm", CubeListBuilder.create()
                .texOffs(42, 18).addBox(-3F, -2F, -2F, 4F, 6F, 4F, new CubeDeformation(0.85F)),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        PartDefinition p_manga_left_arm = p_left_arm.addOrReplaceChild("manga_left_arm", CubeListBuilder.create()
                .texOffs(58, 18).addBox(-1F, -2F, -2F, 4F, 6F, 4F, new CubeDeformation(0.85F)),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        PartDefinition p_lamina_izq_0 = p_left_arm.addOrReplaceChild("lamina_izq_0", CubeListBuilder.create()
                .texOffs(24, 29).addBox(-3.5F, -1F, -3.5F, 7F, 1F, 7F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0.8F, -3.4F, 0F, 0F, 0F, -0.2094F));
        PartDefinition p_lamina_izq_1 = p_left_arm.addOrReplaceChild("lamina_izq_1", CubeListBuilder.create()
                .texOffs(80, 29).addBox(-2.5F, -0.5F, -3F, 5F, 1F, 6F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(3.1F, -2.3F, 0F, 0F, 0F, -0.6632F));
        PartDefinition p_lamina_izq_2 = p_left_arm.addOrReplaceChild("lamina_izq_2", CubeListBuilder.create()
                .texOffs(42, 38).addBox(-2F, -0.5F, -2.5F, 4F, 1F, 5F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(4.4F, -0.2F, 0F, 0F, 0F, -1.0821F));
        PartDefinition p_lamina_der_0 = p_right_arm.addOrReplaceChild("lamina_der_0", CubeListBuilder.create()
                .texOffs(52, 29).addBox(-3.5F, -1F, -3.5F, 7F, 1F, 7F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(-0.8F, -3.4F, 0F, 0F, 0F, 0.2094F));
        PartDefinition p_lamina_der_1 = p_right_arm.addOrReplaceChild("lamina_der_1", CubeListBuilder.create()
                .texOffs(102, 29).addBox(-2.5F, -0.5F, -3F, 5F, 1F, 6F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(-3.1F, -2.3F, 0F, 0F, 0F, 0.6632F));
        PartDefinition p_lamina_der_2 = p_right_arm.addOrReplaceChild("lamina_der_2", CubeListBuilder.create()
                .texOffs(60, 38).addBox(-2F, -0.5F, -2.5F, 4F, 1F, 5F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(-4.4F, -0.2F, 0F, 0F, 0F, 1.0821F));
        PartDefinition p_llama_hombro_izq = p_left_arm.addOrReplaceChild("llama_hombro_izq", CubeListBuilder.create()
                .texOffs(90, 38).addBox(-2.5F, -6F, 0F, 5F, 6F, 0F, CubeDeformation.NONE)
                .texOffs(22, 18).addBox(0F, -6F, -2.5F, 0F, 6F, 5F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(3.4F, -3.6F, 0.6F, -0.1396F, 0F, 0.5236F));
        PartDefinition p_llama_hombro_der = p_right_arm.addOrReplaceChild("llama_hombro_der", CubeListBuilder.create()
                .texOffs(100, 38).addBox(-2.5F, -6F, 0F, 5F, 6F, 0F, CubeDeformation.NONE)
                .texOffs(32, 18).addBox(0F, -6F, -2.5F, 0F, 6F, 5F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(-3.4F, -3.6F, 0.6F, -0.1396F, 0F, -0.5236F));
        PartDefinition p_gola_detras = p_body.addOrReplaceChild("gola_detras", CubeListBuilder.create()
                .texOffs(0, 45).addBox(-4.5F, -4F, -0.5F, 9F, 4F, 1F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, 0.2F, 2.6F, -0.3142F, 0F, 0F));
        PartDefinition p_gola_izq = p_body.addOrReplaceChild("gola_izq", CubeListBuilder.create()
                .texOffs(10, 38).addBox(-0.5F, -3F, -2.5F, 1F, 3F, 4F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(4.4F, 0.2F, 0.6F, -0.1396F, 0F, -0.2443F));
        PartDefinition p_gola_der = p_body.addOrReplaceChild("gola_der", CubeListBuilder.create()
                .texOffs(20, 38).addBox(-0.5F, -3F, -2.5F, 1F, 3F, 4F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(-4.4F, 0.2F, 0.6F, -0.1396F, 0F, 0.2443F));
        PartDefinition p_gola_delante = p_body.addOrReplaceChild("gola_delante", CubeListBuilder.create()
                .texOffs(48, 50).addBox(-3F, -1F, -0.5F, 6F, 1F, 1F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, 0.2F, -2.9F, 0.2094F, 0F, 0F));
        PartDefinition p_halo_pecho = p_body.addOrReplaceChild("halo_pecho", CubeListBuilder.create()
                .texOffs(0, 18).addBox(-5.5F, -5.5F, 0F, 11F, 11F, 0F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, 4.6F, -3.75F, 0F, 0F, 0F));
        PartDefinition p_sol_pecho = p_body.addOrReplaceChild("sol_pecho", CubeListBuilder.create()
                .texOffs(78, 38).addBox(-2.5F, -2.5F, -0.5F, 5F, 5F, 1F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, 4.6F, -3.1F, 0F, 0F, 0F));
        PartDefinition p_capa_0 = p_body.addOrReplaceChild("capa_0", CubeListBuilder.create()
                .texOffs(6, 0).addBox(-1.5F, 0F, 0F, 3F, 17F, 0F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(-3F, 0.4F, 3F, 0.1396F, 0F, 0.0698F));
        PartDefinition p_capa_1 = p_body.addOrReplaceChild("capa_1", CubeListBuilder.create()
                .texOffs(0, 0).addBox(-1.5F, 0F, 0F, 3F, 18F, 0F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, 0.4F, 3F, 0.1396F, 0F, 0F));
        PartDefinition p_capa_2 = p_body.addOrReplaceChild("capa_2", CubeListBuilder.create()
                .texOffs(12, 0).addBox(-1.5F, 0F, 0F, 3F, 17F, 0F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(3F, 0.4F, 3F, 0.1396F, 0F, -0.0698F));
        return LayerDefinition.create(malla, 128, 64);
    }

    private static LayerDefinition solar_grebas() {
        MeshDefinition malla = new MeshDefinition();
        PartDefinition raiz = malla.getRoot();
        PartDefinition p_head = raiz.addOrReplaceChild("head", CubeListBuilder.create(), PartPose.offset(0F, 0F, 0F));
        PartDefinition p_body = raiz.addOrReplaceChild("body", CubeListBuilder.create(), PartPose.offset(0F, 0F, 0F));
        PartDefinition p_right_arm = raiz.addOrReplaceChild("right_arm", CubeListBuilder.create(), PartPose.offset(-5F, 2F, 0F));
        PartDefinition p_left_arm = raiz.addOrReplaceChild("left_arm", CubeListBuilder.create(), PartPose.offset(5F, 2F, 0F));
        PartDefinition p_right_leg = raiz.addOrReplaceChild("right_leg", CubeListBuilder.create(), PartPose.offset(-1.9F, 12F, 0F));
        PartDefinition p_left_leg = raiz.addOrReplaceChild("left_leg", CubeListBuilder.create(), PartPose.offset(1.9F, 12F, 0F));
        PartDefinition p_cintura_solar = p_body.addOrReplaceChild("cintura_solar", CubeListBuilder.create()
                .texOffs(0, 29).addBox(-4F, 7F, -2F, 8F, 5F, 4F, new CubeDeformation(0.55F)),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        PartDefinition p_pernera_right_leg = p_right_leg.addOrReplaceChild("pernera_right_leg", CubeListBuilder.create()
                .texOffs(74, 0).addBox(-2F, 0F, -2F, 4F, 9F, 4F, new CubeDeformation(0.5F)),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        PartDefinition p_pernera_left_leg = p_left_leg.addOrReplaceChild("pernera_left_leg", CubeListBuilder.create()
                .texOffs(90, 0).addBox(-2F, 0F, -2F, 4F, 9F, 4F, new CubeDeformation(0.5F)),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        PartDefinition p_faldon_0 = p_body.addOrReplaceChild("faldon_0", CubeListBuilder.create()
                .texOffs(52, 45).addBox(-1.5F, 0F, -0.5F, 3F, 4F, 1F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(-2.6F, 11.6F, -2.7F, 0.1396F, 0F, 0.2443F));
        PartDefinition p_faldon_1 = p_body.addOrReplaceChild("faldon_1", CubeListBuilder.create()
                .texOffs(110, 38).addBox(-1.5F, 0F, -0.5F, 3F, 5F, 1F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, 11.6F, -2.95F, 0.1396F, 0F, 0F));
        PartDefinition p_faldon_2 = p_body.addOrReplaceChild("faldon_2", CubeListBuilder.create()
                .texOffs(60, 45).addBox(-1.5F, 0F, -0.5F, 3F, 4F, 1F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(2.6F, 11.6F, -2.7F, 0.1396F, 0F, -0.2443F));
        PartDefinition p_faldon_detras_izq = p_body.addOrReplaceChild("faldon_detras_izq", CubeListBuilder.create()
                .texOffs(68, 45).addBox(-1.5F, 0F, -0.5F, 3F, 4F, 1F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(1.9F, 11.6F, 2.7F, -0.1396F, 0F, -0.1745F));
        PartDefinition p_faldon_detras_der = p_body.addOrReplaceChild("faldon_detras_der", CubeListBuilder.create()
                .texOffs(76, 45).addBox(-1.5F, 0F, -0.5F, 3F, 4F, 1F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(-1.9F, 11.6F, 2.7F, -0.1396F, 0F, 0.1745F));
        return LayerDefinition.create(malla, 128, 64);
    }

    private static LayerDefinition solar_botas() {
        MeshDefinition malla = new MeshDefinition();
        PartDefinition raiz = malla.getRoot();
        PartDefinition p_head = raiz.addOrReplaceChild("head", CubeListBuilder.create(), PartPose.offset(0F, 0F, 0F));
        PartDefinition p_body = raiz.addOrReplaceChild("body", CubeListBuilder.create(), PartPose.offset(0F, 0F, 0F));
        PartDefinition p_right_arm = raiz.addOrReplaceChild("right_arm", CubeListBuilder.create(), PartPose.offset(-5F, 2F, 0F));
        PartDefinition p_left_arm = raiz.addOrReplaceChild("left_arm", CubeListBuilder.create(), PartPose.offset(5F, 2F, 0F));
        PartDefinition p_right_leg = raiz.addOrReplaceChild("right_leg", CubeListBuilder.create(), PartPose.offset(-1.9F, 12F, 0F));
        PartDefinition p_left_leg = raiz.addOrReplaceChild("left_leg", CubeListBuilder.create(), PartPose.offset(1.9F, 12F, 0F));
        PartDefinition p_bota_left_leg = p_left_leg.addOrReplaceChild("bota_left_leg", CubeListBuilder.create()
                .texOffs(74, 18).addBox(-2F, 6F, -2F, 4F, 6F, 4F, new CubeDeformation(1F)),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        PartDefinition p_puntera_izq = p_left_leg.addOrReplaceChild("puntera_izq", CubeListBuilder.create()
                .texOffs(24, 50).addBox(-1F, -0.5F, -1.5F, 2F, 1F, 2F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, 11.5F, -3F, 0F, 0F, 0F));
        PartDefinition p_llama_talon_izq = p_left_leg.addOrReplaceChild("llama_talon_izq", CubeListBuilder.create()
                .texOffs(108, 45).addBox(-1.5F, -4F, 0F, 3F, 4F, 0F, CubeDeformation.NONE)
                .texOffs(30, 38).addBox(0F, -4F, -1.5F, 0F, 4F, 3F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, 9.6F, 3.1F, -0.6981F, 0F, 0F));
        PartDefinition p_bota_right_leg = p_right_leg.addOrReplaceChild("bota_right_leg", CubeListBuilder.create()
                .texOffs(90, 18).addBox(-2F, 6F, -2F, 4F, 6F, 4F, new CubeDeformation(1F)),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        PartDefinition p_puntera_der = p_right_leg.addOrReplaceChild("puntera_der", CubeListBuilder.create()
                .texOffs(32, 50).addBox(-1F, -0.5F, -1.5F, 2F, 1F, 2F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, 11.5F, -3F, 0F, 0F, 0F));
        PartDefinition p_llama_talon_der = p_right_leg.addOrReplaceChild("llama_talon_der", CubeListBuilder.create()
                .texOffs(114, 45).addBox(-1.5F, -4F, 0F, 3F, 4F, 0F, CubeDeformation.NONE)
                .texOffs(36, 38).addBox(0F, -4F, -1.5F, 0F, 4F, 3F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, 9.6F, 3.1F, -0.6981F, 0F, 0F));
        return LayerDefinition.create(malla, 128, 64);
    }
}
