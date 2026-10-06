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

    /** Lo que se mueve de cada pieza: parte, eje (0 x, 1 y, 2 z, 3 flota, 4 gira, 5 sube al andar),
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
            default -> throw new IllegalArgumentException(tema + "/" + pieza);
        };
    }

    public static Anim[] anims(String tema, String pieza) {
        return switch (tema + "/" + pieza) {
            case "mareas/casco" -> new Anim[]{new Anim("branquia_izq", 1, 0.22F, 0.22F, 0F, 0.6F), new Anim("branquia_der", 1, -0.22F, 0.22F, 1.6F, 0.6F)};
            case "mareas/pechera" -> new Anim[]{new Anim("capa_0", 0, 0.07F, 0.11F, 0F, 1F), new Anim("capa_0", 5, 0.9F, 0F, 0F, 1F), new Anim("capa_1", 0, 0.07F, 0.11F, 0.9F, 1F), new Anim("capa_1", 5, 0.9F, 0F, 0F, 1F), new Anim("capa_2", 0, 0.07F, 0.11F, 1.8F, 1F), new Anim("capa_2", 5, 0.9F, 0F, 0F, 1F)};
            case "mareas/grebas" -> new Anim[]{new Anim("aleta_rodilla_izq", 1, 0.12F, 0.25F, 0.7F, 0.8F), new Anim("aleta_rodilla_der", 1, -0.12F, 0.25F, -0.7F, 0.8F)};
            case "mareas/botas" -> new Anim[]{new Anim("aleta_tobillo_izq", 1, 0.18F, 0.3F, 0.4F, 1.2F), new Anim("aleta_tobillo_der", 1, -0.18F, 0.3F, -0.4F, 1.2F)};
            case "jade/pechera" -> new Anim[]{new Anim("esquirla_izq", 3, 0.8F, 0.12F, 0F, 0F), new Anim("esquirla_izq", 4, 0.06F, 0F, 0F, 0F), new Anim("esquirla_der", 3, 0.8F, 0.12F, 2F, 0F), new Anim("esquirla_der", 4, 0.06F, 0F, 0F, 0F)};
            case "vendaval/casco" -> new Anim[]{new Anim("ala_casco_izq", 1, 0.25F, 0.32F, 0F, 0.8F), new Anim("antena_izq", 2, 0.08F, 0.17F, 0F, 0.5F), new Anim("ala_casco_der", 1, -0.25F, 0.32F, 0F, 0.8F), new Anim("antena_der", 2, -0.08F, 0.17F, 1F, 0.5F)};
            case "vendaval/pechera" -> new Anim[]{new Anim("hombrera_izq", 2, 0.03F, 0.4F, 0F, 0.5F), new Anim("hombrera_der", 2, -0.03F, 0.4F, 0F, 0.5F), new Anim("ala_izq", 1, 0.32F, 0.22F, 0F, 1.5F), new Anim("ala_der", 1, -0.32F, 0.22F, 0F, 1.5F)};
            case "vendaval/botas" -> new Anim[]{new Anim("ala_talon_izq", 1, 0.3F, 0.4F, 0F, 1.2F), new Anim("ala_talon_der", 1, -0.3F, 0.4F, 0F, 1.2F)};
            default -> new Anim[0];
        };
    }

    /** Si la pieza lleva algo translucido (la capa de membrana). */
    public static boolean conMembrana(String tema, String pieza) {
        return switch (tema + "/" + pieza) {
            case "mareas/casco", "mareas/grebas", "mareas/botas", "jade/casco", "jade/pechera", "jade/grebas", "vendaval/pechera" -> true;
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
                .texOffs(0, 39).addBox(-1.5F, -1.5F, -0.5F, 3F, 3F, 1F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, -7F, 4.2F, -0.4887F, 0F, 0F));
        PartDefinition p_venera_0 = p_venera.addOrReplaceChild("venera_0", CubeListBuilder.create()
                .texOffs(122, 17).addBox(-1F, -8F, -0.4F, 2F, 8F, 1F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, -1.0472F));
        PartDefinition p_venera_1 = p_venera.addOrReplaceChild("venera_1", CubeListBuilder.create()
                .texOffs(54, 17).addBox(-1F, -10F, -0.4F, 2F, 10F, 1F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, -0.6981F));
        PartDefinition p_venera_2 = p_venera.addOrReplaceChild("venera_2", CubeListBuilder.create()
                .texOffs(16, 17).addBox(-1F, -11F, -0.4F, 2F, 11F, 1F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, -0.3491F));
        PartDefinition p_venera_3 = p_venera.addOrReplaceChild("venera_3", CubeListBuilder.create()
                .texOffs(22, 17).addBox(-1F, -11F, -0.4F, 2F, 11F, 1F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        PartDefinition p_venera_4 = p_venera.addOrReplaceChild("venera_4", CubeListBuilder.create()
                .texOffs(28, 17).addBox(-1F, -11F, -0.4F, 2F, 11F, 1F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0.3491F));
        PartDefinition p_venera_5 = p_venera.addOrReplaceChild("venera_5", CubeListBuilder.create()
                .texOffs(60, 17).addBox(-1F, -10F, -0.4F, 2F, 10F, 1F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0.6981F));
        PartDefinition p_venera_6 = p_venera.addOrReplaceChild("venera_6", CubeListBuilder.create()
                .texOffs(0, 30).addBox(-1F, -8F, -0.4F, 2F, 8F, 1F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 1.0472F));
        PartDefinition p_coral_izq = p_head.addOrReplaceChild("coral_izq", CubeListBuilder.create()
                .texOffs(114, 30).addBox(-0.5F, -4F, -0.5F, 1F, 4F, 1F, CubeDeformation.NONE)
                .texOffs(64, 39).addBox(0.5F, -6F, -0.5F, 1F, 2F, 1F, CubeDeformation.NONE)
                .texOffs(84, 39).addBox(-1.5F, -5F, -0.5F, 1F, 1F, 1F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(4.5F, -6.5F, -1F, 0F, 0F, 0.4363F));
        PartDefinition p_branquia_izq = p_head.addOrReplaceChild("branquia_izq", CubeListBuilder.create()
                .texOffs(34, 17).addBox(0F, -3F, -0.5F, 0F, 6F, 5F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(5F, -3.5F, 0.5F, 0F, 0.6109F, 0F));
        PartDefinition p_coral_der = p_head.addOrReplaceChild("coral_der", CubeListBuilder.create()
                .texOffs(118, 30).addBox(-0.5F, -4F, -0.5F, 1F, 4F, 1F, CubeDeformation.NONE)
                .texOffs(68, 39).addBox(-1.5F, -6F, -0.5F, 1F, 2F, 1F, CubeDeformation.NONE)
                .texOffs(88, 39).addBox(0.5F, -5F, -0.5F, 1F, 1F, 1F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(-4.5F, -6.5F, -1F, 0F, 0F, -0.4363F));
        PartDefinition p_branquia_der = p_head.addOrReplaceChild("branquia_der", CubeListBuilder.create()
                .texOffs(44, 17).addBox(0F, -3F, -0.5F, 0F, 6F, 5F, CubeDeformation.NONE),
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
                .texOffs(38, 0).addBox(-4F, 0F, -2F, 8F, 12F, 4F, new CubeDeformation(1F)),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        PartDefinition p_manga_right_arm = p_right_arm.addOrReplaceChild("manga_right_arm", CubeListBuilder.create()
                .texOffs(62, 0).addBox(-3F, -2F, -2F, 4F, 12F, 4F, new CubeDeformation(1F)),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        PartDefinition p_manga_left_arm = p_left_arm.addOrReplaceChild("manga_left_arm", CubeListBuilder.create()
                .texOffs(78, 0).addBox(-1F, -2F, -2F, 4F, 12F, 4F, new CubeDeformation(1F)),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        PartDefinition p_caracola = p_left_arm.addOrReplaceChild("caracola", CubeListBuilder.create()
                .texOffs(6, 30).addBox(-3F, -2F, -3F, 6F, 2F, 6F, CubeDeformation.NONE)
                .texOffs(86, 30).addBox(-2F, -4F, -2F, 4F, 2F, 4F, CubeDeformation.NONE)
                .texOffs(102, 30).addBox(-1.5F, -6F, -1.5F, 3F, 2F, 3F, CubeDeformation.NONE)
                .texOffs(8, 39).addBox(-1F, -8F, -1F, 2F, 2F, 2F, CubeDeformation.NONE)
                .texOffs(92, 39).addBox(-0.5F, -9F, -0.5F, 1F, 1F, 1F, CubeDeformation.NONE)
                .texOffs(48, 39).addBox(2.5F, -1.5F, -1F, 2F, 1F, 2F, CubeDeformation.NONE)
                .texOffs(56, 39).addBox(-1F, -1.5F, 2.5F, 2F, 1F, 2F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(1.5F, -3.2F, 0F, 0F, 0F, -0.3142F));
        PartDefinition p_coral_hombro = p_right_arm.addOrReplaceChild("coral_hombro", CubeListBuilder.create()
                .texOffs(62, 30).addBox(-3F, -1F, -3F, 6F, 1F, 6F, CubeDeformation.NONE)
                .texOffs(122, 30).addBox(-2F, -5F, -1F, 1F, 4F, 1F, CubeDeformation.NONE)
                .texOffs(72, 39).addBox(-3F, -6F, -1F, 1F, 2F, 1F, CubeDeformation.NONE)
                .texOffs(32, 39).addBox(0F, -4F, 1F, 1F, 3F, 1F, CubeDeformation.NONE)
                .texOffs(96, 39).addBox(1F, -5F, 1F, 1F, 1F, 1F, CubeDeformation.NONE)
                .texOffs(76, 39).addBox(1F, -3F, -2F, 1F, 2F, 1F, CubeDeformation.NONE)
                .texOffs(80, 39).addBox(-1F, -7F, -1F, 1F, 2F, 1F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(-1.5F, -3F, 0F, 0F, 0F, 0.2618F));
        PartDefinition p_capa_0 = p_body.addOrReplaceChild("capa_0", CubeListBuilder.create()
                .texOffs(94, 0).addBox(-1.5F, 0F, 0F, 3F, 15F, 0F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(-3F, 0.5F, 2.9F, 0.1396F, 0F, 0.0698F));
        PartDefinition p_capa_1 = p_body.addOrReplaceChild("capa_1", CubeListBuilder.create()
                .texOffs(0, 0).addBox(-1.5F, 0F, 0F, 3F, 17F, 0F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, 0.5F, 2.9F, 0.1396F, 0F, 0F));
        PartDefinition p_capa_2 = p_body.addOrReplaceChild("capa_2", CubeListBuilder.create()
                .texOffs(100, 0).addBox(-1.5F, 0F, 0F, 3F, 15F, 0F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(3F, 0.5F, 2.9F, 0.1396F, 0F, -0.0698F));
        PartDefinition p_espina_0 = p_body.addOrReplaceChild("espina_0", CubeListBuilder.create()
                .texOffs(36, 39).addBox(-0.5F, -3F, -0.5F, 1F, 3F, 1F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, 2F, 3F, -0.8727F, 0F, 0F));
        PartDefinition p_espina_1 = p_body.addOrReplaceChild("espina_1", CubeListBuilder.create()
                .texOffs(40, 39).addBox(-0.5F, -2.5F, -0.5F, 1F, 3F, 1F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, 5F, 3F, -0.8727F, 0F, 0F));
        PartDefinition p_espina_2 = p_body.addOrReplaceChild("espina_2", CubeListBuilder.create()
                .texOffs(44, 39).addBox(-0.5F, -2F, -0.5F, 1F, 3F, 1F, CubeDeformation.NONE),
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
                .texOffs(98, 17).addBox(-4F, 7F, -2F, 8F, 5F, 4F, new CubeDeformation(0.55F)),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        PartDefinition p_pernera_right_leg = p_right_leg.addOrReplaceChild("pernera_right_leg", CubeListBuilder.create()
                .texOffs(106, 0).addBox(-2F, 0F, -2F, 4F, 9F, 4F, new CubeDeformation(0.5F)),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        PartDefinition p_pernera_left_leg = p_left_leg.addOrReplaceChild("pernera_left_leg", CubeListBuilder.create()
                .texOffs(0, 17).addBox(-2F, 0F, -2F, 4F, 9F, 4F, new CubeDeformation(0.5F)),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        PartDefinition p_conchas_delante = p_body.addOrReplaceChild("conchas_delante", CubeListBuilder.create()
                .texOffs(16, 39).addBox(-3.5F, 0F, -0.5F, 3F, 3F, 1F, CubeDeformation.NONE)
                .texOffs(24, 39).addBox(0.5F, 0F, -0.5F, 3F, 3F, 1F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, 11.5F, -2.7F, 0.1396F, 0F, 0F));
        PartDefinition p_aleta_rodilla_izq = p_left_leg.addOrReplaceChild("aleta_rodilla_izq", CubeListBuilder.create()
                .texOffs(30, 30).addBox(0F, -3F, -0.5F, 0F, 4F, 4F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(2.6F, 5F, -1F, 0F, 0.4363F, 0F));
        PartDefinition p_aleta_rodilla_der = p_right_leg.addOrReplaceChild("aleta_rodilla_der", CubeListBuilder.create()
                .texOffs(38, 30).addBox(0F, -3F, -0.5F, 0F, 4F, 4F, CubeDeformation.NONE),
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
                .texOffs(66, 17).addBox(-2F, 6F, -2F, 4F, 6F, 4F, new CubeDeformation(1F)),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        PartDefinition p_aleta_tobillo_izq = p_left_leg.addOrReplaceChild("aleta_tobillo_izq", CubeListBuilder.create()
                .texOffs(46, 30).addBox(0F, -3F, 0F, 0F, 4F, 4F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(3.1F, 8.5F, 1.2F, 0F, 0.5236F, 0F));
        PartDefinition p_bota_right_leg = p_right_leg.addOrReplaceChild("bota_right_leg", CubeListBuilder.create()
                .texOffs(82, 17).addBox(-2F, 6F, -2F, 4F, 6F, 4F, new CubeDeformation(1F)),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        PartDefinition p_aleta_tobillo_der = p_right_leg.addOrReplaceChild("aleta_tobillo_der", CubeListBuilder.create()
                .texOffs(54, 30).addBox(0F, -3F, 0F, 0F, 4F, 4F, CubeDeformation.NONE),
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
                .texOffs(0, 33).addBox(-3F, -1F, -1.5F, 6F, 2F, 2F, CubeDeformation.NONE)
                .texOffs(96, 33).addBox(-1F, -0.5F, -2.5F, 2F, 1F, 1F, CubeDeformation.NONE)
                .texOffs(88, 33).addBox(-2.8F, 1F, -1.2F, 1F, 2F, 1F, CubeDeformation.NONE)
                .texOffs(92, 33).addBox(1.8F, 1F, -1.2F, 1F, 2F, 1F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, -6.5F, -5.3F, 0.2094F, 0F, 0F));
        PartDefinition p_oreja_izq = p_head.addOrReplaceChild("oreja_izq", CubeListBuilder.create()
                .texOffs(40, 33).addBox(-1F, -2F, -1F, 2F, 2F, 1F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(3.2F, -8.6F, 0.5F, 0F, 0F, 0.3142F));
        PartDefinition p_oreja_der = p_head.addOrReplaceChild("oreja_der", CubeListBuilder.create()
                .texOffs(46, 33).addBox(-1F, -2F, -1F, 2F, 2F, 1F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(-3.2F, -8.6F, 0.5F, 0F, 0F, -0.3142F));
        PartDefinition p_cristal_casco_0 = p_head.addOrReplaceChild("cristal_casco_0", CubeListBuilder.create()
                .texOffs(112, 16).addBox(-1F, -6F, -1F, 2F, 6F, 2F, CubeDeformation.NONE)
                .texOffs(114, 33).addBox(-0.5F, -7F, -0.5F, 1F, 1F, 1F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, -8.6F, 0.5F, -0.1745F, 0F, 0F));
        PartDefinition p_cristal_casco_1 = p_head.addOrReplaceChild("cristal_casco_1", CubeListBuilder.create()
                .texOffs(64, 26).addBox(-1F, -4F, -1F, 2F, 4F, 2F, CubeDeformation.NONE)
                .texOffs(118, 33).addBox(-0.5F, -5F, -0.5F, 1F, 1F, 1F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(-2.2F, -8.6F, 1.6F, -0.3142F, 0F, 0.3142F));
        PartDefinition p_cristal_casco_2 = p_head.addOrReplaceChild("cristal_casco_2", CubeListBuilder.create()
                .texOffs(72, 26).addBox(-1F, -4F, -1F, 2F, 4F, 2F, CubeDeformation.NONE)
                .texOffs(122, 33).addBox(-0.5F, -5F, -0.5F, 1F, 1F, 1F, CubeDeformation.NONE),
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
                .texOffs(32, 0).addBox(-4F, 0F, -2F, 8F, 12F, 4F, new CubeDeformation(1F)),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        PartDefinition p_manga_right_arm = p_right_arm.addOrReplaceChild("manga_right_arm", CubeListBuilder.create()
                .texOffs(56, 0).addBox(-3F, -2F, -2F, 4F, 12F, 4F, new CubeDeformation(1F)),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        PartDefinition p_manga_left_arm = p_left_arm.addOrReplaceChild("manga_left_arm", CubeListBuilder.create()
                .texOffs(72, 0).addBox(-1F, -2F, -2F, 4F, 12F, 4F, new CubeDeformation(1F)),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        PartDefinition p_hombrera_izq = p_left_arm.addOrReplaceChild("hombrera_izq", CubeListBuilder.create()
                .texOffs(32, 16).addBox(-3.5F, -1F, -3.5F, 7F, 2F, 7F, CubeDeformation.NONE)
                .texOffs(0, 26).addBox(-3F, 1F, -3F, 6F, 1F, 6F, CubeDeformation.NONE)
                .texOffs(16, 33).addBox(1.2F, -2.5F, -1F, 2F, 2F, 2F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(1.2F, -2.9F, 0F, 0F, 0F, -0.2094F));
        PartDefinition p_esquirla_izq = p_left_arm.addOrReplaceChild("esquirla_izq", CubeListBuilder.create()
                .texOffs(32, 33).addBox(-0.5F, -1.5F, -0.5F, 1F, 3F, 1F, CubeDeformation.NONE)
                .texOffs(102, 33).addBox(-1F, -0.5F, -0.5F, 2F, 1F, 1F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(3.5F, -7.5F, 0F, 0F, 0F, 0F));
        PartDefinition p_hombrera_der = p_right_arm.addOrReplaceChild("hombrera_der", CubeListBuilder.create()
                .texOffs(60, 16).addBox(-3.5F, -1F, -3.5F, 7F, 2F, 7F, CubeDeformation.NONE)
                .texOffs(24, 26).addBox(-3F, 1F, -3F, 6F, 1F, 6F, CubeDeformation.NONE)
                .texOffs(24, 33).addBox(-3.2F, -2.5F, -1F, 2F, 2F, 2F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(-1.2F, -2.9F, 0F, 0F, 0F, 0.2094F));
        PartDefinition p_esquirla_der = p_right_arm.addOrReplaceChild("esquirla_der", CubeListBuilder.create()
                .texOffs(36, 33).addBox(-0.5F, -1.5F, -0.5F, 1F, 3F, 1F, CubeDeformation.NONE)
                .texOffs(108, 33).addBox(-1F, -0.5F, -0.5F, 2F, 1F, 1F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(-3.5F, -7.5F, 0F, 0F, 0F, 0F));
        PartDefinition p_cristal_espalda_0 = p_body.addOrReplaceChild("cristal_espalda_0", CubeListBuilder.create()
                .texOffs(120, 16).addBox(-1F, -6F, -1F, 2F, 6F, 2F, CubeDeformation.NONE)
                .texOffs(0, 37).addBox(-0.5F, -7F, -0.5F, 1F, 1F, 1F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, 2.5F, 2.8F, -0.6632F, 0F, 0F));
        PartDefinition p_cristal_espalda_1 = p_body.addOrReplaceChild("cristal_espalda_1", CubeListBuilder.create()
                .texOffs(48, 26).addBox(-1F, -5F, -1F, 2F, 5F, 2F, CubeDeformation.NONE)
                .texOffs(4, 37).addBox(-0.5F, -6F, -0.5F, 1F, 1F, 1F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(-2.5F, 4.5F, 2.8F, -0.6632F, 0F, 0.384F));
        PartDefinition p_cristal_espalda_2 = p_body.addOrReplaceChild("cristal_espalda_2", CubeListBuilder.create()
                .texOffs(56, 26).addBox(-1F, -5F, -1F, 2F, 5F, 2F, CubeDeformation.NONE)
                .texOffs(8, 37).addBox(-0.5F, -6F, -0.5F, 1F, 1F, 1F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(2.5F, 4.5F, 2.8F, -0.6632F, 0F, -0.384F));
        PartDefinition p_cristal_espalda_3 = p_body.addOrReplaceChild("cristal_espalda_3", CubeListBuilder.create()
                .texOffs(80, 26).addBox(-1F, -4F, -1F, 2F, 4F, 2F, CubeDeformation.NONE)
                .texOffs(12, 37).addBox(-0.5F, -5F, -0.5F, 1F, 1F, 1F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, 7.5F, 2.8F, -0.6632F, 0F, 0F));
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
                .texOffs(88, 16).addBox(-4F, 7F, -2F, 8F, 5F, 4F, new CubeDeformation(0.55F)),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        PartDefinition p_pernera_right_leg = p_right_leg.addOrReplaceChild("pernera_right_leg", CubeListBuilder.create()
                .texOffs(88, 0).addBox(-2F, 0F, -2F, 4F, 9F, 4F, new CubeDeformation(0.5F)),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        PartDefinition p_pernera_left_leg = p_left_leg.addOrReplaceChild("pernera_left_leg", CubeListBuilder.create()
                .texOffs(104, 0).addBox(-2F, 0F, -2F, 4F, 9F, 4F, new CubeDeformation(0.5F)),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        PartDefinition p_faldon_delante = p_body.addOrReplaceChild("faldon_delante", CubeListBuilder.create()
                .texOffs(88, 26).addBox(-3F, 0F, -0.5F, 6F, 4F, 1F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, 11.6F, -2.7F, 0.1047F, 0F, 0F));
        PartDefinition p_faldon_detras = p_body.addOrReplaceChild("faldon_detras", CubeListBuilder.create()
                .texOffs(102, 26).addBox(-3F, 0F, -0.5F, 6F, 4F, 1F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, 11.6F, 2.7F, -0.1047F, 0F, 0F));
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
                .texOffs(52, 33).addBox(-0.5F, -0.5F, -2F, 1F, 1F, 2F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(-1.6F, 11.6F, -3F, -0.4363F, 0F, 0F));
        PartDefinition p_garra_izq_1 = p_left_leg.addOrReplaceChild("garra_izq_1", CubeListBuilder.create()
                .texOffs(58, 33).addBox(-0.5F, -0.5F, -2F, 1F, 1F, 2F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, 11.6F, -3F, -0.4363F, 0F, 0F));
        PartDefinition p_garra_izq_2 = p_left_leg.addOrReplaceChild("garra_izq_2", CubeListBuilder.create()
                .texOffs(64, 33).addBox(-0.5F, -0.5F, -2F, 1F, 1F, 2F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(1.6F, 11.6F, -3F, -0.4363F, 0F, 0F));
        PartDefinition p_bota_right_leg = p_right_leg.addOrReplaceChild("bota_right_leg", CubeListBuilder.create()
                .texOffs(16, 16).addBox(-2F, 6F, -2F, 4F, 6F, 4F, new CubeDeformation(1F)),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        PartDefinition p_garra_der_0 = p_right_leg.addOrReplaceChild("garra_der_0", CubeListBuilder.create()
                .texOffs(70, 33).addBox(-0.5F, -0.5F, -2F, 1F, 1F, 2F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(-1.6F, 11.6F, -3F, -0.4363F, 0F, 0F));
        PartDefinition p_garra_der_1 = p_right_leg.addOrReplaceChild("garra_der_1", CubeListBuilder.create()
                .texOffs(76, 33).addBox(-0.5F, -0.5F, -2F, 1F, 1F, 2F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, 11.6F, -3F, -0.4363F, 0F, 0F));
        PartDefinition p_garra_der_2 = p_right_leg.addOrReplaceChild("garra_der_2", CubeListBuilder.create()
                .texOffs(82, 33).addBox(-0.5F, -0.5F, -2F, 1F, 1F, 2F, CubeDeformation.NONE),
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
                .texOffs(62, 16).addBox(0F, -8F, 0F, 0F, 8F, 3F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, 0F, 0F, -0.1745F, 0F, 0F));
        PartDefinition p_pluma_casco_izq_1 = p_ala_casco_izq.addOrReplaceChild("pluma_casco_izq_1", CubeListBuilder.create()
                .texOffs(32, 29).addBox(0F, -7F, 0F, 0F, 7F, 3F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, 0F, 0F, -0.5585F, 0F, 0F));
        PartDefinition p_pluma_casco_izq_2 = p_ala_casco_izq.addOrReplaceChild("pluma_casco_izq_2", CubeListBuilder.create()
                .texOffs(0, 39).addBox(0F, -5F, 0F, 0F, 5F, 3F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, 0F, 0F, -0.9425F, 0F, 0F));
        PartDefinition p_antena_izq = p_head.addOrReplaceChild("antena_izq", CubeListBuilder.create()
                .texOffs(48, 39).addBox(-0.5F, -6F, -0.5F, 1F, 6F, 1F, CubeDeformation.NONE)
                .texOffs(104, 39).addBox(-0.5F, -7F, -0.5F, 1F, 1F, 1F, CubeDeformation.NONE)
                .texOffs(68, 39).addBox(0F, -6F, -2F, 0F, 4F, 2F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(1.6F, -8.6F, -2F, -0.384F, 0F, 0.2793F));
        PartDefinition p_ala_casco_der = p_head.addOrReplaceChild("ala_casco_der", CubeListBuilder.create(),
                PartPose.offsetAndRotation(-4.6F, -5.5F, 1.5F, 0F, 0.3491F, 0F));
        PartDefinition p_pluma_casco_der_0 = p_ala_casco_der.addOrReplaceChild("pluma_casco_der_0", CubeListBuilder.create()
                .texOffs(68, 16).addBox(0F, -8F, 0F, 0F, 8F, 3F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, 0F, 0F, -0.1745F, 0F, 0F));
        PartDefinition p_pluma_casco_der_1 = p_ala_casco_der.addOrReplaceChild("pluma_casco_der_1", CubeListBuilder.create()
                .texOffs(38, 29).addBox(0F, -7F, 0F, 0F, 7F, 3F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, 0F, 0F, -0.5585F, 0F, 0F));
        PartDefinition p_pluma_casco_der_2 = p_ala_casco_der.addOrReplaceChild("pluma_casco_der_2", CubeListBuilder.create()
                .texOffs(6, 39).addBox(0F, -5F, 0F, 0F, 5F, 3F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, 0F, 0F, -0.9425F, 0F, 0F));
        PartDefinition p_antena_der = p_head.addOrReplaceChild("antena_der", CubeListBuilder.create()
                .texOffs(52, 39).addBox(-0.5F, -6F, -0.5F, 1F, 6F, 1F, CubeDeformation.NONE)
                .texOffs(108, 39).addBox(-0.5F, -7F, -0.5F, 1F, 1F, 1F, CubeDeformation.NONE)
                .texOffs(72, 39).addBox(0F, -6F, -2F, 0F, 4F, 2F, CubeDeformation.NONE),
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
                .texOffs(32, 0).addBox(-4F, 0F, -2F, 8F, 12F, 4F, new CubeDeformation(1F)),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        PartDefinition p_manga_right_arm = p_right_arm.addOrReplaceChild("manga_right_arm", CubeListBuilder.create()
                .texOffs(56, 0).addBox(-3F, -2F, -2F, 4F, 12F, 4F, new CubeDeformation(1F)),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        PartDefinition p_manga_left_arm = p_left_arm.addOrReplaceChild("manga_left_arm", CubeListBuilder.create()
                .texOffs(72, 0).addBox(-1F, -2F, -2F, 4F, 12F, 4F, new CubeDeformation(1F)),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        PartDefinition p_hombrera_izq = p_left_arm.addOrReplaceChild("hombrera_izq", CubeListBuilder.create()
                .texOffs(80, 29).addBox(-3F, -1F, -3F, 6F, 2F, 6F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(1.2F, -2.9F, 0F, 0F, 0F, -0.1745F));
        PartDefinition p_pluma_hombro_izq_0 = p_hombrera_izq.addOrReplaceChild("pluma_hombro_izq_0", CubeListBuilder.create()
                .texOffs(68, 29).addBox(0F, -6F, -1.5F, 0F, 6F, 3F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(2.8F, -0.5F, 0F, 0F, 0F, -0.4363F));
        PartDefinition p_pluma_hombro_izq_1 = p_hombrera_izq.addOrReplaceChild("pluma_hombro_izq_1", CubeListBuilder.create()
                .texOffs(12, 39).addBox(0F, -5F, -1.5F, 0F, 5F, 3F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(2.8F, -0.5F, 0F, 0F, 0F, -0.8727F));
        PartDefinition p_pluma_hombro_izq_2 = p_hombrera_izq.addOrReplaceChild("pluma_hombro_izq_2", CubeListBuilder.create()
                .texOffs(24, 39).addBox(0F, -4F, -1.5F, 0F, 4F, 3F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(2.8F, -0.5F, 0F, 0F, 0F, -1.309F));
        PartDefinition p_hombrera_der = p_right_arm.addOrReplaceChild("hombrera_der", CubeListBuilder.create()
                .texOffs(104, 29).addBox(-3F, -1F, -3F, 6F, 2F, 6F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(-1.2F, -2.9F, 0F, 0F, 0F, 0.1745F));
        PartDefinition p_pluma_hombro_der_0 = p_hombrera_der.addOrReplaceChild("pluma_hombro_der_0", CubeListBuilder.create()
                .texOffs(74, 29).addBox(0F, -6F, -1.5F, 0F, 6F, 3F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(-2.8F, -0.5F, 0F, 0F, 0F, 0.4363F));
        PartDefinition p_pluma_hombro_der_1 = p_hombrera_der.addOrReplaceChild("pluma_hombro_der_1", CubeListBuilder.create()
                .texOffs(18, 39).addBox(0F, -5F, -1.5F, 0F, 5F, 3F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(-2.8F, -0.5F, 0F, 0F, 0F, 0.8727F));
        PartDefinition p_pluma_hombro_der_2 = p_hombrera_der.addOrReplaceChild("pluma_hombro_der_2", CubeListBuilder.create()
                .texOffs(30, 39).addBox(0F, -4F, -1.5F, 0F, 4F, 3F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(-2.8F, -0.5F, 0F, 0F, 0F, 1.309F));
        PartDefinition p_ala_izq = p_body.addOrReplaceChild("ala_izq", CubeListBuilder.create(),
                PartPose.offsetAndRotation(1F, 3F, 2.9F, 0F, -0.6632F, -0.1047F));
        PartDefinition p_ala_alta_izq = p_ala_izq.addOrReplaceChild("ala_alta_izq", CubeListBuilder.create()
                .texOffs(88, 0).addBox(0F, -12F, 0F, 15F, 13F, 0F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, -0.2443F));
        PartDefinition p_ala_baja_izq = p_ala_izq.addOrReplaceChild("ala_baja_izq", CubeListBuilder.create()
                .texOffs(74, 16).addBox(0F, 0F, 0F, 11F, 10F, 0F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, 1.5F, 0F, 0F, 0F, 0.4189F));
        PartDefinition p_ala_der = p_body.addOrReplaceChild("ala_der", CubeListBuilder.create(),
                PartPose.offsetAndRotation(-1F, 3F, 2.9F, 0F, 0.6632F, 0.1047F));
        PartDefinition p_ala_alta_der = p_ala_der.addOrReplaceChild("ala_alta_der", CubeListBuilder.create()
                .texOffs(0, 16).addBox(-15F, -12F, 0F, 15F, 13F, 0F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0.2443F));
        PartDefinition p_ala_baja_der = p_ala_der.addOrReplaceChild("ala_baja_der", CubeListBuilder.create()
                .texOffs(96, 16).addBox(-11F, 0F, 0F, 11F, 10F, 0F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, 1.5F, 0F, 0F, 0F, -0.4189F));
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
                .texOffs(44, 29).addBox(-4F, 7F, -2F, 8F, 5F, 4F, new CubeDeformation(0.55F)),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        PartDefinition p_pernera_right_leg = p_right_leg.addOrReplaceChild("pernera_right_leg", CubeListBuilder.create()
                .texOffs(30, 16).addBox(-2F, 0F, -2F, 4F, 9F, 4F, new CubeDeformation(0.5F)),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        PartDefinition p_pernera_left_leg = p_left_leg.addOrReplaceChild("pernera_left_leg", CubeListBuilder.create()
                .texOffs(46, 16).addBox(-2F, 0F, -2F, 4F, 9F, 4F, new CubeDeformation(0.5F)),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        PartDefinition p_pluma_cadera_izq = p_body.addOrReplaceChild("pluma_cadera_izq", CubeListBuilder.create()
                .texOffs(76, 39).addBox(-1.5F, 0F, 0F, 3F, 5F, 0F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(2.4F, 11F, -2.6F, 0.1396F, 0F, -0.2094F));
        PartDefinition p_pluma_cadera_der = p_body.addOrReplaceChild("pluma_cadera_der", CubeListBuilder.create()
                .texOffs(82, 39).addBox(-1.5F, 0F, 0F, 3F, 5F, 0F, CubeDeformation.NONE),
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
                .texOffs(0, 29).addBox(-2F, 6F, -2F, 4F, 6F, 4F, new CubeDeformation(1F)),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        PartDefinition p_ala_talon_izq = p_left_leg.addOrReplaceChild("ala_talon_izq", CubeListBuilder.create(),
                PartPose.offsetAndRotation(3.2F, 8.5F, 1F, 0F, -0.5236F, 0F));
        PartDefinition p_pluma_talon_izq_0 = p_ala_talon_izq.addOrReplaceChild("pluma_talon_izq_0", CubeListBuilder.create()
                .texOffs(36, 39).addBox(0F, -4F, 0F, 0F, 4F, 3F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, 0F, 0F, -0.2618F, 0F, 0F));
        PartDefinition p_pluma_talon_izq_1 = p_ala_talon_izq.addOrReplaceChild("pluma_talon_izq_1", CubeListBuilder.create()
                .texOffs(56, 39).addBox(0F, -3F, 0F, 0F, 3F, 3F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, 0F, 0F, -0.7854F, 0F, 0F));
        PartDefinition p_puntera_izq = p_left_leg.addOrReplaceChild("puntera_izq", CubeListBuilder.create()
                .texOffs(88, 39).addBox(-1F, -0.5F, -1.5F, 2F, 1F, 2F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, 11.5F, -3F, 0F, 0F, 0F));
        PartDefinition p_bota_right_leg = p_right_leg.addOrReplaceChild("bota_right_leg", CubeListBuilder.create()
                .texOffs(16, 29).addBox(-2F, 6F, -2F, 4F, 6F, 4F, new CubeDeformation(1F)),
                PartPose.offsetAndRotation(0F, 0F, 0F, 0F, 0F, 0F));
        PartDefinition p_ala_talon_der = p_right_leg.addOrReplaceChild("ala_talon_der", CubeListBuilder.create(),
                PartPose.offsetAndRotation(-3.2F, 8.5F, 1F, 0F, 0.5236F, 0F));
        PartDefinition p_pluma_talon_der_0 = p_ala_talon_der.addOrReplaceChild("pluma_talon_der_0", CubeListBuilder.create()
                .texOffs(42, 39).addBox(0F, -4F, 0F, 0F, 4F, 3F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, 0F, 0F, -0.2618F, 0F, 0F));
        PartDefinition p_pluma_talon_der_1 = p_ala_talon_der.addOrReplaceChild("pluma_talon_der_1", CubeListBuilder.create()
                .texOffs(62, 39).addBox(0F, -3F, 0F, 0F, 3F, 3F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, 0F, 0F, -0.7854F, 0F, 0F));
        PartDefinition p_puntera_der = p_right_leg.addOrReplaceChild("puntera_der", CubeListBuilder.create()
                .texOffs(96, 39).addBox(-1F, -0.5F, -1.5F, 2F, 1F, 2F, CubeDeformation.NONE),
                PartPose.offsetAndRotation(0F, 11.5F, -3F, 0F, 0F, 0F));
        return LayerDefinition.create(malla, 128, 64);
    }
}
