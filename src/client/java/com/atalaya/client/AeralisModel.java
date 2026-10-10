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
 *     quedar liberada; y el halo de viento de la espalda, que gira al reves,
 *     mas despacio.
 *
 * Se pinta translucida: las alas son de viento y se ve el cielo a traves.
 */
public class AeralisModel extends EntityModel<AeralisRenderState> {

    public static final ModelLayerLocation CAPA = new ModelLayerLocation(
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "aeralis"), "main");
    /** La misma malla hinchada, para el aura de la Furia. */
    public static final ModelLayerLocation CAPA_AURA = new ModelLayerLocation(
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "aeralis"), "aura");

    private final ModelPart cuerpo;
    private final ModelPart nucleo;
    private final ModelPart halo;
    /** Las alas de arriba, que se abren en los Ocelos. */
    private final ModelPart alaSupIzq;
    private final ModelPart alaSupDer;
    private final ModelPart alaInfIzq;
    private final ModelPart alaInfDer;

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
    private final KeyframeAnimation picadoAviso;
    private final KeyframeAnimation picado;
    private final KeyframeAnimation posada;
    private final KeyframeAnimation escamas;

    public AeralisModel(ModelPart raiz) {
        super(raiz, RenderTypes::entityTranslucent);
        this.cuerpo = raiz.createPartLookup().apply("cuerpo");
        this.nucleo = raiz.createPartLookup().apply("nucleo");
        this.halo = raiz.createPartLookup().apply("halo");
        this.alaSupIzq = raiz.createPartLookup().apply("ala_sup_izq");
        this.alaSupDer = raiz.createPartLookup().apply("ala_sup_der");
        this.alaInfIzq = raiz.createPartLookup().apply("ala_inf_izq");
        this.alaInfDer = raiz.createPartLookup().apply("ala_inf_der");
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
        this.picadoAviso = AeralisAnimaciones.PICADO_AVISO.bake(raiz);
        this.picado = AeralisAnimaciones.PICADO.bake(raiz);
        this.posada = AeralisAnimaciones.POSADA.bake(raiz);
        this.escamas = AeralisAnimaciones.ESCAMAS.bake(raiz);
    }

    /**
     * La animacion de la aturdida dura 5 s: cae (0-1,5), se retuerce (1,5-3,5) y
     * se levanta (3,5-5). Si la aturdida dura mas (el viento de vuelta: 10 s),
     * el retorcerse se repite, algo mas lento, hasta que toca levantarse: asi no
     * se queda tiesa ni se levanta antes de tiempo.
     */
    private static long tiempoAturdida(float s, float total) {
        float caida = 3.5F;
        float levanta = 1.5F;
        if (total <= 5.0F + 1.0E-3F || s < caida) {
            return (long) (s * 1000.0F);
        }
        if (s >= total - levanta) {
            return (long) ((caida + (s - (total - levanta))) * 1000.0F);
        }
        // Vueltas enteras del retorcerse (1,5-3,5: empieza y acaba en la misma pose).
        float medio = total - caida - levanta;
        int vueltas = Math.max(1, Math.round(medio / 2.0F));
        float k = medio / (vueltas * 2.0F);
        return (long) ((1.5F + ((s - caida) / k) % 2.0F) * 1000.0F);
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
            if (s.aturdida.isStarted()) {
                aturdida.apply(tiempoAturdida(s.aturdida.getTimeInMillis(s.ageInTicks) / 1000.0F, s.duracionAturdida / 20.0F), 1.0F);
            }
            agotada.apply(s.agotada, s.ageInTicks, s.ritmo);
            tambaleo.apply(s.tambaleo, s.ageInTicks, s.ritmo);
            picadoAviso.apply(s.picadoAviso, s.ageInTicks, s.ritmo);
            picado.apply(s.picado, s.ageInTicks, 1.0F);
            if (s.estado == AeralisEntity.OCELOS) {
                // Los Ocelos: posada (sin el despegue del final de la animacion) y las alas
                // de arriba se abren cuando miran, para que se vean los ojos.
                long ms = Math.min(2000L, (long) s.posada.getTimeInMillis(s.ageInTicks));
                posada.apply(ms, 1.0F);
                float abre = Math.min(1.0F, s.ocelos);
                alaSupIzq.zRot += 38.0F * Mth.DEG_TO_RAD * abre;
                alaSupDer.zRot -= 38.0F * Mth.DEG_TO_RAD * abre;
                alaSupIzq.yRot += 18.0F * Mth.DEG_TO_RAD * abre;
                alaSupDer.yRot -= 18.0F * Mth.DEG_TO_RAD * abre;
                alaInfIzq.yRot += 22.0F * Mth.DEG_TO_RAD * abre;
                alaInfDer.yRot -= 22.0F * Mth.DEG_TO_RAD * abre;
            } else {
                posada.apply(s.posada, s.ageInTicks, 1.0F);
            }
            escamas.apply(s.escamas, s.ageInTicks, s.ritmo);
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
        halo.zRot -= s.ageInTicks * vel * 0.25F;
    }
}
