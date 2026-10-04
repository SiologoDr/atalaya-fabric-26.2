package com.atalaya.client;

import com.atalaya.Atalaya;
import com.atalaya.entity.AeralisEntity;
import net.minecraft.client.animation.KeyframeAnimation;
import net.minecraft.client.model.EntityModel;
import net.minecraft.client.model.geom.ModelLayerLocation;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.renderer.rendertype.RenderTypes;
import net.minecraft.resources.Identifier;
import net.minecraft.util.Mth;

/**
 * El modelo de Aeralis: la malla de {@link AeralisMalla} y las animaciones de
 * {@link AeralisAnimaciones} (generadas, con la fisica ya horneada), mas lo que
 * depende del combate:
 *
 *   - el vuelo, que se mezcla con los ataques por peso en vez de saltar, y
 *     con el vuelo rapido segun lo deprisa que va (la batida se acelera);
 *   - la inercia: se inclina hacia donde avanza y se ladea en los giros;
 *   - el ojo de la tormenta del pecho, que gira cada vez mas rapido con la
 *     fase, se detiene en el silencio del Juicio y gira despacio, limpio, al
 *     quedar liberada.
 *
 * Se pinta translucida: las alas son de viento y se ve el cielo a traves.
 */
public class AeralisModel extends EntityModel<AeralisRenderState> {

    public static final ModelLayerLocation CAPA = new ModelLayerLocation(
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "aeralis"), "main");

    private final ModelPart cuerpo;
    private final ModelPart nucleo;

    private final KeyframeAnimation vuelo;
    private final KeyframeAnimation avance;
    private final KeyframeAnimation dormida;
    private final KeyframeAnimation despertar;
    private final KeyframeAnimation aleteo;
    private final KeyframeAnimation tornados;
    private final KeyframeAnimation marca;
    private final KeyframeAnimation rafaga;
    private final KeyframeAnimation dobleRafaga;
    private final KeyframeAnimation juicioSube;
    private final KeyframeAnimation juicioSostiene;
    private final KeyframeAnimation juicioGolpe;
    private final KeyframeAnimation aturdida;
    private final KeyframeAnimation agotada;
    private final KeyframeAnimation tambaleo;
    private final KeyframeAnimation liberacion;

    public AeralisModel(ModelPart raiz) {
        super(raiz, RenderTypes::entityTranslucent);
        this.cuerpo = raiz.createPartLookup().apply("cuerpo");
        this.nucleo = raiz.createPartLookup().apply("nucleo");
        this.vuelo = AeralisAnimaciones.VUELO.bake(raiz);
        this.avance = AeralisAnimaciones.AVANCE.bake(raiz);
        this.dormida = AeralisAnimaciones.DORMIDA.bake(raiz);
        this.despertar = AeralisAnimaciones.DESPERTAR.bake(raiz);
        this.aleteo = AeralisAnimaciones.ALETEO.bake(raiz);
        this.tornados = AeralisAnimaciones.TORNADOS.bake(raiz);
        this.marca = AeralisAnimaciones.MARCA.bake(raiz);
        this.rafaga = AeralisAnimaciones.RAFAGA.bake(raiz);
        this.dobleRafaga = AeralisAnimaciones.DOBLE_RAFAGA.bake(raiz);
        this.juicioSube = AeralisAnimaciones.JUICIO_SUBE.bake(raiz);
        this.juicioSostiene = AeralisAnimaciones.JUICIO_SOSTIENE.bake(raiz);
        this.juicioGolpe = AeralisAnimaciones.JUICIO_GOLPE.bake(raiz);
        this.aturdida = AeralisAnimaciones.ATURDIDA.bake(raiz);
        this.agotada = AeralisAnimaciones.AGOTADA.bake(raiz);
        this.tambaleo = AeralisAnimaciones.TAMBALEO.bake(raiz);
        this.liberacion = AeralisAnimaciones.LIBERACION.bake(raiz);
    }

    @Override
    public void setupAnim(AeralisRenderState s) {
        super.setupAnim(s);
        boolean muriendo = s.deathTime > 0;
        if (!muriendo) {
            if (s.pesoLibre > 0.0F) {
                // Las dos batidas tienen el mismo periodo y van con el mismo
                // reloj: se mezclan segun lo rapido que vuela sin desfasarse.
                long reloj = (long) s.relojVuelo;
                vuelo.apply(reloj, s.pesoLibre * (1.0F - s.avance));
                avance.apply(reloj, s.pesoLibre * s.avance);
            }
            dormida.apply(s.dormida, s.ageInTicks, s.ritmo);
            despertar.apply(s.despertar, s.ageInTicks, s.ritmo);
            aleteo.apply(s.aleteo, s.ageInTicks, s.ritmo);
            tornados.apply(s.tornados, s.ageInTicks, s.ritmo);
            marca.apply(s.marca, s.ageInTicks, s.ritmo);
            rafaga.apply(s.rafaga, s.ageInTicks, s.ritmo);
            dobleRafaga.apply(s.dobleRafaga, s.ageInTicks, s.ritmo);
            juicioSube.apply(s.juicioSube, s.ageInTicks, s.ritmo);
            juicioSostiene.apply(s.juicioSostiene, s.ageInTicks, s.ritmo);
            juicioGolpe.apply(s.juicioGolpe, s.ageInTicks, s.ritmo);
            aturdida.apply(s.aturdida, s.ageInTicks, s.ritmo);
            agotada.apply(s.agotada, s.ageInTicks, s.ritmo);
            tambaleo.apply(s.tambaleo, s.ageInTicks, s.ritmo);
        }
        liberacion.apply(s.liberacion, s.ageInTicks);

        // La inercia del vuelo: se inclina hacia donde va y se ladea al girar.
        if (!muriendo) {
            cuerpo.xRot += s.cabeceo * Mth.DEG_TO_RAD;
            cuerpo.zRot += s.alabeo * Mth.DEG_TO_RAD;
        }

        // El ojo de la tormenta gira en su plano.
        float vel;
        if (s.libre) {
            vel = 0.03F;
        } else if (s.estado == AeralisEntity.JUICIO_SUBE || s.estado == AeralisEntity.DORMIDA) {
            vel = 0.01F;
        } else {
            vel = 0.05F + 0.035F * s.fase;
        }
        nucleo.zRot += s.ageInTicks * vel;
    }
}
