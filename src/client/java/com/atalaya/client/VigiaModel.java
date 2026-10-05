package com.atalaya.client;

import com.atalaya.Atalaya;
import net.minecraft.client.animation.KeyframeAnimation;
import net.minecraft.client.model.EntityModel;
import net.minecraft.client.model.geom.ModelLayerLocation;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.model.geom.PartPose;
import net.minecraft.client.model.geom.builders.CubeListBuilder;
import net.minecraft.client.model.geom.builders.LayerDefinition;
import net.minecraft.client.model.geom.builders.MeshDefinition;
import net.minecraft.client.model.geom.builders.PartDefinition;
import net.minecraft.resources.Identifier;
import net.minecraft.util.Mth;

/**
 * La malla del Vigia: la primera del mod que no se presta de vanilla.
 *
 * <pre>
 *   torso ─┬─ cuello ── cabeza ─┬─ ojo
 *          │                    ├─ cuerno_izq ── punta_izq
 *          │                    └─ cuerno_der ── punta_der
 *          ├─ brazo_izq ─┬─ hombrera_izq
 *          │             └─ antebrazo_izq ── garras_izq
 *          ├─ brazo_der  (igual)
 *          └─ capa
 *   pierna_izq ── espinilla_izq ── pie_izq
 *   pierna_der    (igual)
 * </pre>
 *
 * Los nombres no son decoracion: las animaciones de {@link VigiaAnimaciones}
 * buscan las piezas por nombre, asi que renombrar una aqui sin cambiarla alli
 * la deja quieta sin dar ningun error.
 *
 * La postura de reposo es encorvada —torso a 25 grados— y cada hijo la
 * compensa para quedar recto en el mundo: el cuello y la cabeza deshacen la
 * inclinacion para mirar al frente, y los brazos y la capa para colgar a
 * plomo. Las animaciones SUMAN sobre esta postura, no la sustituyen.
 *
 * La cuadricula UV la comparte con el script que pinta la textura; cambiar un
 * tamano aqui obliga a cambiarlo alli.
 */
public class VigiaModel extends EntityModel<VigiaRenderState> {

    public static final ModelLayerLocation CAPA = new ModelLayerLocation(
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "vigia"), "main");

    /** Lo encorvado que va. Todo lo que cuelga del torso lo deshace. */
    private static final float JOROBA = 25.0F * Mth.DEG_TO_RAD;

    private final ModelPart cabeza;

    private final KeyframeAnimation patrulla;
    private final KeyframeAnimation persecucion;
    private final KeyframeAnimation vigilar;
    private final KeyframeAnimation acecho;
    private final KeyframeAnimation buscar;
    private final KeyframeAnimation muerte;
    private final KeyframeAnimation alerta;
    private final KeyframeAnimation cepo;
    private final KeyframeAnimation mirada;
    private final KeyframeAnimation tambaleo;

    public VigiaModel(ModelPart raiz) {
        super(raiz);
        this.cabeza = raiz.getChild("torso").getChild("cuello").getChild("cabeza");
        this.patrulla = VigiaAnimaciones.PATRULLA.bake(raiz);
        this.persecucion = VigiaAnimaciones.PERSECUCION.bake(raiz);
        this.vigilar = VigiaAnimaciones.VIGILAR.bake(raiz);
        this.acecho = VigiaAnimaciones.ACECHO.bake(raiz);
        this.buscar = VigiaAnimaciones.BUSCAR.bake(raiz);
        this.muerte = VigiaAnimaciones.MUERTE.bake(raiz);
        this.alerta = VigiaAnimaciones.ALERTA.bake(raiz);
        this.cepo = VigiaAnimaciones.CEPO.bake(raiz);
        this.mirada = VigiaAnimaciones.MIRADA.bake(raiz);
        this.tambaleo = VigiaAnimaciones.TAMBALEO.bake(raiz);
    }

    private static float grados(float g) {
        return g * Mth.DEG_TO_RAD;
    }

    public static LayerDefinition crear() {
        MeshDefinition malla = new MeshDefinition();
        PartDefinition raiz = malla.getRoot();

        // --- Torso: la cadera esta en y=0, bloque y medio sobre el suelo ---
        PartDefinition torso = raiz.addOrReplaceChild("torso",
                CubeListBuilder.create().texOffs(0, 16).addBox(-5.0F, -16.0F, -3.0F, 10.0F, 16.0F, 6.0F),
                PartPose.offsetAndRotation(0.0F, 0.0F, 0.0F, JOROBA, 0.0F, 0.0F));

        // La capa: un plano de grosor cero a la espalda, como la hierba del
        // fulminante. Deshace la joroba y se abre 8 grados hacia atras para no
        // atravesar las piernas al andar.
        torso.addOrReplaceChild("capa",
                CubeListBuilder.create().texOffs(64, 0).addBox(-5.0F, 0.0F, 0.0F, 10.0F, 18.0F, 0.0F),
                PartPose.offsetAndRotation(0.0F, -15.0F, 3.05F, -JOROBA + grados(8.0F), 0.0F, 0.0F));

        PartDefinition cuello = torso.addOrReplaceChild("cuello",
                CubeListBuilder.create().texOffs(32, 0).addBox(-1.5F, -5.0F, -1.5F, 3.0F, 5.0F, 3.0F),
                PartPose.offsetAndRotation(0.0F, -16.0F, -1.0F, grados(-10.0F), 0.0F, 0.0F));

        // Cuello y cabeza suman -25: la cara queda al frente aunque vaya encorvado.
        PartDefinition cabeza = cuello.addOrReplaceChild("cabeza",
                CubeListBuilder.create().texOffs(0, 0).addBox(-4.0F, -8.0F, -4.0F, 8.0F, 8.0F, 8.0F),
                PartPose.offsetAndRotation(0.0F, -5.0F, 0.0F, grados(-15.0F), 0.0F, 0.0F));

        // El ojo es pieza aparte para poder ESCALARLO al cargar la mirada. Por
        // eso el pivote va en su centro: escalar desde una esquina lo haria
        // crecer torcido.
        cabeza.addOrReplaceChild("ojo",
                CubeListBuilder.create().texOffs(32, 8).addBox(-2.0F, -2.0F, -0.5F, 4.0F, 4.0F, 1.0F),
                PartPose.offset(0.0F, -4.0F, -4.0F));

        cuerno(cabeza, "izq", 1.0F);
        cuerno(cabeza, "der", -1.0F);

        brazo(torso, "izq", 1.0F);
        brazo(torso, "der", -1.0F);

        pierna(raiz, "izq", 1.0F);
        pierna(raiz, "der", -1.0F);

        return LayerDefinition.create(malla, 128, 64);
    }

    /**
     * Astas sobre el farol. Es lo que hace la silueta: a contraluz, de noche,
     * un farol con cuernos no se confunde con nada de vanilla.
     *
     * @param lado +1 a la izquierda del bicho (+X), -1 a la derecha
     */
    private static void cuerno(PartDefinition cabeza, String nombre, float lado) {
        PartDefinition cuerno = cabeza.addOrReplaceChild("cuerno_" + nombre,
                CubeListBuilder.create().texOffs(44, 0).addBox(-0.5F, -7.0F, -0.5F, 1.0F, 7.0F, 1.0F),
                PartPose.offsetAndRotation(2.5F * lado, -8.0F, 0.5F,
                        grados(-12.0F), 0.0F, grados(25.0F) * lado));
        cuerno.addOrReplaceChild("punta_" + nombre,
                CubeListBuilder.create().texOffs(48, 0).addBox(-0.5F, -3.0F, -0.5F, 1.0F, 3.0F, 1.0F),
                PartPose.offsetAndRotation(0.0F, -4.0F, 0.0F, 0.0F, 0.0F, grados(40.0F) * lado));
    }

    /**
     * Brazos que llegan a las rodillas: 33 pixeles de hombro a garra. Cuelgan
     * a plomo deshaciendo la joroba, y el antebrazo se dobla un poco hacia
     * delante, que en reposo es lo que les da aspecto de estar al acecho.
     */
    private static void brazo(PartDefinition torso, String nombre, float lado) {
        boolean espejo = lado < 0;
        PartDefinition brazo = torso.addOrReplaceChild("brazo_" + nombre,
                CubeListBuilder.create().texOffs(32, 16).mirror(espejo)
                        .addBox(-1.5F, -1.5F, -1.5F, 3.0F, 14.0F, 3.0F),
                PartPose.offsetAndRotation(6.5F * lado, -14.0F, 0.0F, -JOROBA, 0.0F, 0.0F));
        brazo.addOrReplaceChild("hombrera_" + nombre,
                CubeListBuilder.create().texOffs(88, 0).mirror(espejo)
                        .addBox(-2.0F, -2.5F, -2.5F, 4.0F, 3.0F, 5.0F),
                PartPose.ZERO);
        PartDefinition antebrazo = brazo.addOrReplaceChild("antebrazo_" + nombre,
                CubeListBuilder.create().texOffs(44, 16).mirror(espejo)
                        .addBox(-1.0F, 0.0F, -1.0F, 2.0F, 14.0F, 2.0F),
                PartPose.offsetAndRotation(0.0F, 12.5F, 0.0F, grados(-10.0F), 0.0F, 0.0F));
        // Tres dedos en una sola pieza: se mueven juntos, y asi la garra se
        // cierra entera con una rotacion.
        antebrazo.addOrReplaceChild("garras_" + nombre,
                CubeListBuilder.create().texOffs(52, 16)
                        .addBox(-1.6F, 0.0F, -0.5F, 1.0F, 6.0F, 1.0F)
                        .addBox(-0.5F, 0.0F, -1.2F, 1.0F, 6.0F, 1.0F)
                        .addBox(0.6F, 0.0F, -0.5F, 1.0F, 6.0F, 1.0F),
                PartPose.offsetAndRotation(0.0F, 13.5F, 0.0F, grados(-15.0F), 0.0F, 0.0F));
    }

    /**
     * Zancos con rodilla: muslo hacia delante, espinilla hacia atras y el pie
     * plano. Las tres inclinaciones (-10, +20, -10) se anulan, asi que el pie
     * apoya recto y la cadera cae a 23,7 pixeles: a ras de suelo.
     */
    private static void pierna(PartDefinition raiz, String nombre, float lado) {
        boolean espejo = lado < 0;
        PartDefinition muslo = raiz.addOrReplaceChild("pierna_" + nombre,
                CubeListBuilder.create().texOffs(0, 40).mirror(espejo)
                        .addBox(-1.5F, 0.0F, -1.5F, 3.0F, 11.0F, 3.0F),
                PartPose.offsetAndRotation(2.5F * lado, 0.0F, 0.5F, grados(-10.0F), 0.0F, 0.0F));
        PartDefinition espinilla = muslo.addOrReplaceChild("espinilla_" + nombre,
                CubeListBuilder.create().texOffs(12, 40).mirror(espejo)
                        .addBox(-1.0F, 0.0F, -1.0F, 2.0F, 11.0F, 2.0F),
                PartPose.offsetAndRotation(0.0F, 11.0F, 0.0F, grados(20.0F), 0.0F, 0.0F));
        espinilla.addOrReplaceChild("pie_" + nombre,
                CubeListBuilder.create().texOffs(20, 40).mirror(espejo)
                        .addBox(-1.5F, 0.0F, -3.5F, 3.0F, 2.0F, 5.0F),
                PartPose.offsetAndRotation(0.0F, 11.0F, 0.0F, grados(-10.0F), 0.0F, 0.0F));
    }

    @Override
    public void setupAnim(VigiaRenderState estado) {
        // Vuelve a la postura de reposo: las animaciones suman, y sin esto
        // sumarian sobre lo del fotograma anterior.
        super.setupAnim(estado);

        boolean muriendo = estado.deathTime > 0;

        // Mirar a la presa, solo cuando la tiene. En calma a donde mira lo
        // decide la animacion de vigilar, y muerto no mira nada.
        if (estado.cazando && !muriendo) {
            cabeza.yRot += estado.yRot * Mth.DEG_TO_RAD;
            cabeza.xRot += estado.xRot * Mth.DEG_TO_RAD;
        }

        if (!muriendo) {
            // Dos maneras de andar segun tenga presa o no. La de persecucion
            // va con menos ciclos por bloque: zancadas mas largas.
            if (estado.cazando) {
                persecucion.applyWalk(estado.walkAnimationPos, estado.walkAnimationSpeed, 1.4F, 2.5F);
            } else {
                patrulla.applyWalk(estado.walkAnimationPos, estado.walkAnimationSpeed, 2.0F, 2.5F);
            }
            // El mismo reloj de reposo, dos posturas: vigilar el horizonte en
            // calma, o respirar hondo mirandote si ya te tiene.
            (estado.cazando ? acecho : vigilar).apply(estado.reposo, estado.ageInTicks);
        }
        muerte.apply(estado.muerte, estado.ageInTicks);
        buscar.apply(estado.buscar, estado.ageInTicks);
        alerta.apply(estado.alerta, estado.ageInTicks);
        cepo.apply(estado.cepo, estado.ageInTicks);
        mirada.apply(estado.mirada, estado.ageInTicks);
        tambaleo.apply(estado.tambaleo, estado.ageInTicks);
    }
}
