package com.atalaya.client;

import com.atalaya.entity.VigiaEntity;
import net.minecraft.client.animation.AnimationChannel;
import net.minecraft.client.animation.AnimationDefinition;
import net.minecraft.client.animation.Keyframe;
import net.minecraft.client.animation.KeyframeAnimations;

/**
 * Las animaciones del Vigia, con el sistema de keyframes de vanilla —el mismo
 * del warden, la brisa o el creaking—. Sin librerias: lo que exporta Blockbench
 * con "Animation to Java" tiene exactamente esta forma.
 *
 * Tres reglas para leerlas:
 *
 *   - Todo SUMA sobre la postura de reposo de {@link VigiaModel}. Un 0 es "como
 *     esta", no "recto".
 *   - Rotacion en grados. X positivo inclina hacia delante lo que sube (el
 *     torso) y hacia atras lo que cuelga (brazos, espinillas, capa).
 *   - Escala relativa: 1 es su tamano.
 *
 * Las de accion duran lo mismo que su estado en {@link VigiaEntity}. Si no
 * cuadran, o se cortan o el bicho se queda posando.
 */
public final class VigiaAnimaciones {

    private VigiaAnimaciones() {
    }

    private static final float T = 1.0F / 20.0F;

    // ------------------------------------------------------------------
    //  Atajos para que cada canal quepa en una linea
    // ------------------------------------------------------------------

    private static Keyframe rot(float t, float x, float y, float z) {
        return new Keyframe(t, KeyframeAnimations.degreeVec(x, y, z), AnimationChannel.Interpolations.CATMULLROM);
    }

    /** Lo mismo, pero sin suavizar: para los golpes, que tienen que ser secos. */
    private static Keyframe seco(float t, float x, float y, float z) {
        return new Keyframe(t, KeyframeAnimations.degreeVec(x, y, z), AnimationChannel.Interpolations.LINEAR);
    }

    private static Keyframe pos(float t, float x, float y, float z) {
        return new Keyframe(t, KeyframeAnimations.posVec(x, y, z), AnimationChannel.Interpolations.CATMULLROM);
    }

    private static Keyframe esc(float t, float s) {
        return new Keyframe(t, KeyframeAnimations.scaleVec(s, s, s), AnimationChannel.Interpolations.CATMULLROM);
    }

    private static Keyframe posSeco(float t, float x, float y, float z) {
        return new Keyframe(t, KeyframeAnimations.posVec(x, y, z), AnimationChannel.Interpolations.LINEAR);
    }

    private static Keyframe escXYZ(float t, float x, float y, float z) {
        return new Keyframe(t, KeyframeAnimations.scaleVec(x, y, z), AnimationChannel.Interpolations.CATMULLROM);
    }

    private static AnimationChannel giro(Keyframe... k) {
        return new AnimationChannel(AnimationChannel.Targets.ROTATION, k);
    }

    private static AnimationChannel mover(Keyframe... k) {
        return new AnimationChannel(AnimationChannel.Targets.POSITION, k);
    }

    private static AnimationChannel escala(Keyframe... k) {
        return new AnimationChannel(AnimationChannel.Targets.SCALE, k);
    }

    // ------------------------------------------------------------------
    //  Vigilar: en calma y quieto. Es su oficio y tiene que leerse como tal:
    //  barre el horizonte con el farol, despacio, como un faro. Se para a
    //  escuchar a cada lado, alza la vista al cielo y vuelve. Respira, cambia
    //  el peso de pierna, crispa una garra, parpadea.
    // ------------------------------------------------------------------

    public static final AnimationDefinition VIGILAR = AnimationDefinition.Builder.withLength(8.0F).looping()
            .addAnimation("cabeza", giro(rot(0, 0, 0, 0), rot(1.6F, 0, 55, 0), rot(2.6F, 0, 55, 8), rot(3.0F, 0, 52, 0),
                    rot(4.8F, 0, -55, 0), rot(5.8F, 0, -55, -8), rot(6.2F, 0, -50, 0), rot(7.0F, -22, -10, 0),
                    rot(8.0F, 0, 0, 0)))
            // El torso acompana un poco el barrido: girar solo la cabeza 55
            // grados se ve de muneco; con el cuerpo detras, se ve de animal.
            .addAnimation("torso", giro(rot(0, 0, 0, 0), rot(1.6F, 2, 12, 0), rot(3.0F, 0, 10, 0), rot(4.8F, 2, -12, 0),
                    rot(6.2F, 0, -10, 0), rot(7.0F, -6, 0, 0), rot(8.0F, 0, 0, 0)))
            // Cambio de peso: la cadera se va un pelo a cada lado.
            .addAnimation("torso", mover(pos(0, 0, 0, 0), pos(2.0F, 0.6F, 0, 0), pos(6.0F, -0.6F, 0, 0), pos(8.0F, 0, 0, 0)))
            .addAnimation("capa", giro(rot(0, 0, 0, 0), rot(2.0F, 6, 0, 3), rot(4.0F, 2, 0, -3), rot(6.0F, 7, 0, 2), rot(8.0F, 0, 0, 0)))
            .addAnimation("brazo_izq", giro(rot(0, 0, 0, 0), rot(2.0F, -3, 0, -3), rot(4.0F, 0, 0, 0), rot(6.0F, -3, 0, -2), rot(8.0F, 0, 0, 0)))
            .addAnimation("brazo_der", giro(rot(0, 0, 0, 0), rot(3.0F, -3, 0, 3), rot(5.0F, 0, 0, 0), rot(7.0F, -2, 0, 2), rot(8.0F, 0, 0, 0)))
            // Crispa las garras de vez en cuando, cada mano a su hora.
            .addAnimation("garras_izq", giro(rot(0, 0, 0, 0), rot(3.1F, 0, 0, 0), seco(3.2F, -30, 0, 0), rot(3.45F, 0, 0, 0),
                    rot(6.8F, 0, 0, 0), seco(6.9F, -25, 0, 0), rot(7.15F, 0, 0, 0), rot(8.0F, 0, 0, 0)))
            .addAnimation("garras_der", giro(rot(0, 0, 0, 0), rot(1.2F, 0, 0, 0), seco(1.3F, -28, 0, 0), rot(1.55F, 0, 0, 0),
                    rot(8.0F, 0, 0, 0)))
            // Un parpadeo lento a mitad del barrido: el ojo se cierra en vertical.
            .addAnimation("ojo", escala(esc(0, 1), esc(3.95F, 1), escXYZ(4.05F, 1.1F, 0.1F, 1), escXYZ(4.2F, 1, 1, 1), esc(8.0F, 1)))
            .build();

    // ------------------------------------------------------------------
    //  Acecho: con presa pero parado. Respira hondo, la capa se mece.
    // ------------------------------------------------------------------

    public static final AnimationDefinition ACECHO = AnimationDefinition.Builder.withLength(4.0F).looping()
            .addAnimation("torso", giro(rot(0, 0, 0, 0), rot(2.0F, 3, 0, 0), rot(4.0F, 0, 0, 0)))
            .addAnimation("capa", giro(rot(0, 0, 0, 0), rot(1.4F, 7, 0, 2), rot(2.8F, 2, 0, -2), rot(4.0F, 0, 0, 0)))
            .addAnimation("brazo_izq", giro(rot(0, 0, 0, 0), rot(2.0F, -6, 0, -4), rot(4.0F, 0, 0, 0)))
            .addAnimation("brazo_der", giro(rot(0, 0, 0, 0), rot(2.0F, -6, 0, 4), rot(4.0F, 0, 0, 0)))
            .addAnimation("garras_izq", giro(rot(0, 0, 0, 0), rot(2.0F, 25, 0, 0), rot(4.0F, 0, 0, 0)))
            .addAnimation("garras_der", giro(rot(0, 0, 0, 0), rot(2.2F, 25, 0, 0), rot(4.0F, 0, 0, 0)))
            .build();

    // ------------------------------------------------------------------
    //  Patrulla: andar en calma. Paso medido, erguido, la cabeza quieta
    //  mientras el cuerpo se balancea debajo. Lo reproduce applyWalk.
    // ------------------------------------------------------------------

    public static final AnimationDefinition PATRULLA = AnimationDefinition.Builder.withLength(1.6F).looping()
            // Pierna adelante (-) y atras (+). La rodilla solo se dobla en el
            // tramo en que la pierna vuelve por el aire.
            .addAnimation("pierna_izq", giro(rot(0, -20, 0, 0), rot(0.8F, 20, 0, 0), rot(1.6F, -20, 0, 0)))
            .addAnimation("espinilla_izq", giro(rot(0, 0, 0, 0), rot(0.8F, 0, 0, 0), rot(1.2F, 40, 0, 0), rot(1.6F, 0, 0, 0)))
            .addAnimation("pierna_der", giro(rot(0, 20, 0, 0), rot(0.8F, -20, 0, 0), rot(1.6F, 20, 0, 0)))
            .addAnimation("espinilla_der", giro(rot(0, 0, 0, 0), rot(0.4F, 40, 0, 0), rot(0.8F, 0, 0, 0), rot(1.6F, 0, 0, 0)))
            .addAnimation("brazo_izq", giro(rot(0, 10, 0, -2), rot(0.8F, -10, 0, -2), rot(1.6F, 10, 0, -2)))
            .addAnimation("brazo_der", giro(rot(0, -10, 0, 2), rot(0.8F, 10, 0, 2), rot(1.6F, -10, 0, 2)))
            // El antebrazo va con retraso: es lo que da peso a unos brazos tan largos.
            .addAnimation("antebrazo_izq", giro(rot(0, -5, 0, 0), rot(0.8F, -15, 0, 0), rot(1.6F, -5, 0, 0)))
            .addAnimation("antebrazo_der", giro(rot(0, -15, 0, 0), rot(0.8F, -5, 0, 0), rot(1.6F, -15, 0, 0)))
            .addAnimation("torso", giro(rot(0, 0, 4, 0), rot(0.8F, 0, -4, 0), rot(1.6F, 0, 4, 0)))
            .addAnimation("torso", mover(pos(0, 0, 0, 0), pos(0.4F, 0, -0.5F, 0), pos(0.8F, 0, 0, 0),
                    pos(1.2F, 0, -0.5F, 0), pos(1.6F, 0, 0, 0)))
            // La cabeza deshace el giro del torso: el farol avanza estable.
            .addAnimation("cabeza", giro(rot(0, 0, -4, 0), rot(0.8F, 0, 4, 0), rot(1.6F, 0, -4, 0)))
            .addAnimation("capa", giro(rot(0, 6, 0, 0), rot(0.4F, 10, 0, 0), rot(0.8F, 6, 0, 0), rot(1.2F, 10, 0, 0), rot(1.6F, 6, 0, 0)))
            .build();

    // ------------------------------------------------------------------
    //  Persecucion: andar con presa. Otro bicho: postura baja, zancadas
    //  largas con la rodilla alta, la cabeza adelantada y nivelada, y los dos
    //  brazos estirados hacia ti cerrando las garras por turnos, como si ya
    //  te estuviera agarrando. La capa vuela detras.
    // ------------------------------------------------------------------

    public static final AnimationDefinition PERSECUCION = AnimationDefinition.Builder.withLength(1.0F).looping()
            .addAnimation("torso", giro(rot(0, 18, 6, 0), rot(0.5F, 18, -6, 0), rot(1.0F, 18, 6, 0)))
            .addAnimation("torso", mover(pos(0, 0, 0, -1), pos(0.25F, 0, -1.2F, -1), pos(0.5F, 0, 0, -1),
                    pos(0.75F, 0, -1.2F, -1), pos(1.0F, 0, 0, -1)))
            .addAnimation("cuello", giro(rot(0, -10, 0, 0), rot(1.0F, -10, 0, 0)))
            // Compensa la inclinacion y el giro: el ojo no se despega de ti.
            .addAnimation("cabeza", giro(rot(0, -12, -6, 0), rot(0.5F, -12, 6, 0), rot(1.0F, -12, -6, 0)))
            .addAnimation("pierna_izq", giro(rot(0, -40, 0, 0), rot(0.5F, 35, 0, 0), rot(1.0F, -40, 0, 0)))
            .addAnimation("espinilla_izq", giro(rot(0, 5, 0, 0), rot(0.5F, 5, 0, 0), rot(0.7F, 70, 0, 0), rot(0.9F, 20, 0, 0), rot(1.0F, 5, 0, 0)))
            .addAnimation("pierna_der", giro(rot(0, 35, 0, 0), rot(0.5F, -40, 0, 0), rot(1.0F, 35, 0, 0)))
            .addAnimation("espinilla_der", giro(rot(0, 5, 0, 0), rot(0.2F, 70, 0, 0), rot(0.4F, 20, 0, 0), rot(0.5F, 5, 0, 0), rot(1.0F, 5, 0, 0)))
            .addAnimation("brazo_izq", giro(rot(0, -75, 0, -8), rot(0.5F, -45, 0, -8), rot(1.0F, -75, 0, -8)))
            .addAnimation("brazo_der", giro(rot(0, -45, 0, 8), rot(0.5F, -75, 0, 8), rot(1.0F, -45, 0, 8)))
            .addAnimation("antebrazo_izq", giro(rot(0, -10, 0, 0), rot(0.5F, -35, 0, 0), rot(1.0F, -10, 0, 0)))
            .addAnimation("antebrazo_der", giro(rot(0, -35, 0, 0), rot(0.5F, -10, 0, 0), rot(1.0F, -35, 0, 0)))
            // Cada garra se cierra cuando su brazo llega al frente.
            .addAnimation("garras_izq", giro(rot(0, -35, 0, 0), rot(0.25F, 35, 0, 0), rot(0.9F, 35, 0, 0), seco(1.0F, -35, 0, 0)))
            .addAnimation("garras_der", giro(rot(0, 35, 0, 0), rot(0.4F, 35, 0, 0), seco(0.5F, -35, 0, 0), rot(0.75F, 35, 0, 0), rot(1.0F, 35, 0, 0)))
            .addAnimation("capa", giro(rot(0, 35, 0, 3), rot(0.25F, 45, 0, -3), rot(0.5F, 35, 0, 3), rot(0.75F, 45, 0, -3), rot(1.0F, 35, 0, 3)))
            .addAnimation("ojo", escala(esc(0, 1.1F), esc(0.5F, 1.2F), esc(1.0F, 1.1F)))
            .build();

    // ------------------------------------------------------------------
    //  Buscar: te ha perdido. Olfatea tres veces (los tres soplos del sonido),
    //  barre a un lado y al otro mucho mas rapido que vigilando, mira al suelo
    //  y al cielo, y se rinde. Con el ojo dilatado todo el rato.
    // ------------------------------------------------------------------

    public static final AnimationDefinition BUSCAR = AnimationDefinition.Builder
            .withLength(VigiaEntity.DURACION_BUSCAR * T)
            .addAnimation("cuello", giro(rot(0, 0, 0, 0), seco(0.1F, -9, 0, 0), rot(0.2F, 0, 0, 0), seco(0.32F, -9, 0, 0),
                    rot(0.42F, 0, 0, 0), seco(0.54F, -9, 0, 0), rot(0.66F, 0, 0, 0), rot(2.5F, 0, 0, 0)))
            .addAnimation("torso", giro(rot(0, 0, 0, 0), rot(0.3F, -12, 0, 0), rot(0.8F, -12, 20, 0), rot(1.3F, -12, -20, 0),
                    rot(1.8F, -12, 8, 0), rot(2.2F, -12, 0, 0), rot(2.5F, 0, 0, 0)))
            .addAnimation("cabeza", giro(rot(0, 0, 0, 0), rot(0.66F, 0, 0, 0), rot(0.85F, 5, 50, 0), rot(1.0F, 5, 50, 6),
                    rot(1.25F, 5, -50, 0), rot(1.45F, 5, -50, -6), rot(1.7F, 18, 0, 0), rot(1.95F, -18, 0, 0),
                    rot(2.2F, 0, 15, 0), rot(2.5F, 0, 0, 0)))
            .addAnimation("brazo_izq", giro(rot(0, 0, 0, 0), rot(0.5F, -30, 0, -20), rot(2.2F, -30, 0, -20), rot(2.5F, 0, 0, 0)))
            .addAnimation("brazo_der", giro(rot(0, 0, 0, 0), rot(0.5F, -30, 0, 20), rot(2.2F, -30, 0, 20), rot(2.5F, 0, 0, 0)))
            .addAnimation("garras_izq", giro(rot(0, 0, 0, 0), rot(0.5F, 30, 0, 0), seco(1.1F, -20, 0, 0), rot(1.3F, 30, 0, 0), rot(2.5F, 0, 0, 0)))
            .addAnimation("garras_der", giro(rot(0, 0, 0, 0), rot(0.5F, 30, 0, 0), seco(1.6F, -20, 0, 0), rot(1.8F, 30, 0, 0), rot(2.5F, 0, 0, 0)))
            .addAnimation("ojo", escala(esc(0, 1), esc(0.4F, 1.4F), esc(2.2F, 1.4F), esc(2.5F, 1)))
            .build();

    // ------------------------------------------------------------------
    //  Muerte: la ultima guardia. Tres segundos, seis tiempos.
    //
    //    0,00-0,30  ACUSA      el golpe le echa atras, los brazos se abren
    //    0,30-0,90  RODILLAS   se le doblan las piernas y cae arrodillado
    //    0,90-1,60  ULTIMA     alza el farol una vez mas y tiende una garra
    //               MIRADA     hacia quien le ha matado; el ojo se dilata
    //    1,60-2,20  SE APAGA   la mano cae y el ojo se encoge hasta cerrarse
    //                          (la capa de brillo parpadea y muere en el 44)
    //    2,20-2,60  DESPLOME   se vence hacia delante y el farol se desprende
    //    2,60-3,00  REPOSO     el farol golpea el suelo (tick 52) y rueda
    //
    //  Tiene que leerse a distancia: rodillas, cabeza arriba, luz que muere.
    //  Es la recompensa visual de haberlo tumbado.
    // ------------------------------------------------------------------

    public static final AnimationDefinition MUERTE = AnimationDefinition.Builder
            .withLength(VigiaEntity.DURACION_MUERTE * T)
            .addAnimation("torso", giro(rot(0, 0, 0, 0), seco(0.15F, -25, 0, 8), rot(0.3F, -20, 0, 6),
                    rot(0.9F, 15, 0, 4), rot(1.3F, -5, 0, 0), rot(1.6F, -5, 0, 0), rot(2.2F, 15, 0, 3),
                    seco(2.55F, 78, 0, 6), rot(2.7F, 72, 0, 6), rot(3.0F, 75, 0, 6)))
            // Bajar a las rodillas es bajar la cadera 11 pixeles; el desplome,
            // 3 mas y hacia delante.
            .addAnimation("torso", mover(pos(0, 0, 0, 0), pos(0.3F, 0, 0, 0), pos(0.9F, 0, -11, 0), pos(2.2F, 0, -11, 0),
                    posSeco(2.55F, 0, -14, -4), pos(3.0F, 0, -14, -4)))
            .addAnimation("pierna_izq", mover(pos(0, 0, 0, 0), pos(0.3F, 0, 0, 0), pos(0.9F, 0, -11, 0), pos(3.0F, 0, -11, 0)))
            .addAnimation("pierna_der", mover(pos(0, 0, 0, 0), pos(0.3F, 0, 0, 0), pos(0.9F, 0, -11, 0), pos(3.0F, 0, -11, 0)))
            .addAnimation("pierna_izq", giro(rot(0, 0, 0, 0), rot(0.3F, 0, 0, 0), rot(0.9F, -15, 0, -18), rot(3.0F, -15, 0, -18)))
            .addAnimation("pierna_der", giro(rot(0, 0, 0, 0), rot(0.3F, 0, 0, 0), rot(0.9F, -15, 0, 18), rot(3.0F, -15, 0, 18)))
            .addAnimation("espinilla_izq", giro(rot(0, 0, 0, 0), rot(0.3F, 10, 0, 0), rot(0.9F, 100, 0, 0), rot(3.0F, 100, 0, 0)))
            .addAnimation("espinilla_der", giro(rot(0, 0, 0, 0), rot(0.3F, 10, 0, 0), rot(0.9F, 100, 0, 0), rot(3.0F, 100, 0, 0)))
            .addAnimation("pie_izq", giro(rot(0, 0, 0, 0), rot(0.9F, -60, 0, 0), rot(3.0F, -60, 0, 0)))
            .addAnimation("pie_der", giro(rot(0, 0, 0, 0), rot(0.9F, -60, 0, 0), rot(3.0F, -60, 0, 0)))
            .addAnimation("cuello", giro(rot(0, 0, 0, 0), rot(0.9F, 10, 0, 0), rot(1.3F, -15, 0, 0), rot(1.6F, -15, 0, 0),
                    rot(2.2F, 15, 0, 0), rot(3.0F, 15, 0, 0)))
            // La ultima mirada: el farol se alza al cielo y tiembla.
            .addAnimation("cabeza", giro(rot(0, 0, 0, 0), seco(0.15F, -30, 0, 0), rot(0.9F, 25, 0, 0),
                    rot(1.3F, -35, 0, 0), rot(1.4F, -35, 0, 3), rot(1.5F, -35, 0, -3), rot(1.6F, -33, 0, 0),
                    rot(2.2F, 20, 0, 0), seco(2.55F, 55, 0, 40), rot(2.7F, 60, 0, 80), rot(3.0F, 62, 0, 90)))
            // ...y al desplomarse se suelta del cuello y cae rodando por delante.
            .addAnimation("cabeza", mover(pos(0, 0, 0, 0), pos(2.2F, 0, 0, 0), posSeco(2.55F, 0, -7, -6),
                    pos(2.65F, 0, -5.5F, -7), pos(2.8F, 0, -7, -8), pos(3.0F, 0, -7, -8.5F)))
            .addAnimation("brazo_izq", giro(rot(0, 0, 0, 0), seco(0.15F, -10, 0, -45), rot(0.9F, 10, 0, -8),
                    rot(2.2F, 10, 0, -8), seco(2.55F, -70, 0, -25), rot(3.0F, -80, 0, -30)))
            // La garra que se tiende: tiembla y cae.
            .addAnimation("brazo_der", giro(rot(0, 0, 0, 0), seco(0.15F, -10, 0, 45), rot(0.9F, 10, 0, 8),
                    rot(1.25F, -80, 0, 10), rot(1.35F, -80, 0, 14), rot(1.45F, -78, 0, 8), rot(1.55F, -80, 0, 13),
                    rot(1.65F, -76, 0, 9), seco(2.0F, 10, 0, 6), rot(2.2F, 10, 0, 6), seco(2.55F, -70, 0, 25),
                    rot(3.0F, -80, 0, 30)))
            .addAnimation("antebrazo_der", giro(rot(0, 0, 0, 0), rot(1.25F, -20, 0, 0), rot(1.65F, -20, 0, 0), rot(2.0F, 0, 0, 0)))
            .addAnimation("garras_der", giro(rot(0, 0, 0, 0), rot(1.25F, 40, 0, 0), rot(1.65F, 40, 0, 0), rot(2.0F, -10, 0, 0),
                    rot(3.0F, -10, 0, 0)))
            .addAnimation("garras_izq", giro(rot(0, 0, 0, 0), rot(0.9F, -10, 0, 0), rot(3.0F, -10, 0, 0)))
            // El ojo: se dilata en la ultima mirada y se cierra para siempre.
            .addAnimation("ojo", escala(esc(0, 1), esc(0.9F, 1.0F), esc(1.3F, 1.7F), esc(1.6F, 1.6F), esc(1.9F, 0.8F),
                    seco(2.2F, 0.0F), esc(3.0F, 0.0F)))
            .addAnimation("capa", giro(rot(0, 0, 0, 0), seco(0.15F, 30, 0, 0), rot(0.9F, 10, 0, 0), rot(2.2F, 5, 0, 0),
                    seco(2.55F, -50, 0, 6), rot(3.0F, -60, 0, 8)))
            .build();

    // ------------------------------------------------------------------
    //  Alerta: se yergue, abre los brazos y ruge sacudiendo el farol.
    // ------------------------------------------------------------------

    public static final AnimationDefinition ALERTA = AnimationDefinition.Builder
            .withLength(VigiaEntity.DURACION_ALERTA * T)
            .addAnimation("torso", giro(rot(0, 0, 0, 0), rot(0.25F, -25, 0, 0), rot(0.9F, -25, 0, 0), rot(1.2F, 0, 0, 0)))
            .addAnimation("cabeza", giro(rot(0, 0, 0, 0), rot(0.25F, -25, 0, 0), rot(0.4F, 10, 0, 6),
                    rot(0.5F, 10, 0, -6), rot(0.6F, 10, 0, 6), rot(0.7F, 10, 0, -6), rot(0.8F, 10, 0, 0),
                    rot(1.2F, 0, 0, 0)))
            .addAnimation("brazo_izq", giro(rot(0, 0, 0, 0), rot(0.3F, -20, 0, -70), rot(0.9F, -20, 0, -70), rot(1.2F, 0, 0, 0)))
            .addAnimation("brazo_der", giro(rot(0, 0, 0, 0), rot(0.3F, -20, 0, 70), rot(0.9F, -20, 0, 70), rot(1.2F, 0, 0, 0)))
            .addAnimation("antebrazo_izq", giro(rot(0, 0, 0, 0), rot(0.3F, -35, 0, 0), rot(0.9F, -35, 0, 0), rot(1.2F, 0, 0, 0)))
            .addAnimation("antebrazo_der", giro(rot(0, 0, 0, 0), rot(0.3F, -35, 0, 0), rot(0.9F, -35, 0, 0), rot(1.2F, 0, 0, 0)))
            .addAnimation("garras_izq", giro(rot(0, 0, 0, 0), rot(0.3F, 25, 0, 0), rot(0.9F, 25, 0, 0), rot(1.2F, 0, 0, 0)))
            .addAnimation("garras_der", giro(rot(0, 0, 0, 0), rot(0.3F, 25, 0, 0), rot(0.9F, 25, 0, 0), rot(1.2F, 0, 0, 0)))
            .addAnimation("ojo", escala(esc(0, 1), esc(0.3F, 1.5F), esc(0.9F, 1.5F), esc(1.2F, 1)))
            .addAnimation("capa", giro(rot(0, 0, 0, 0), rot(0.3F, 30, 0, 0), rot(0.9F, 25, 0, 0), rot(1.2F, 0, 0, 0)))
            .build();

    // ------------------------------------------------------------------
    //  Cepo: el ataque cuerpo a cuerpo. No es un golpe, es una trampa que
    //  se cierra. Cuatro tiempos:
    //
    //    0,00-0,50  ANTICIPACION  se echa atras, flexiona, abre los brazos
    //                             en cruz con las garras abiertas al frente
    //    0,50-0,55  GOLPE         seco: se lanza y cierra los brazos delante
    //    0,55-0,75  RETENCION     sobrepasa y sacude lo que ha atrapado
    //    0,75-1,10  RECUPERACION  vuelve despacio, la capa arrastrando
    //
    //  La firma del Vigia: el cuerpo entero se mueve, pero la CABEZA
    //  compensa cada inclinacion del torso, asi que el ojo no deja de
    //  mirarte en ningun momento del ataque.
    //
    //  El dano entra en el tick 11 (0,55 s), cuando los brazos se cierran.
    // ------------------------------------------------------------------

    public static final AnimationDefinition CEPO = AnimationDefinition.Builder
            .withLength(VigiaEntity.DURACION_CEPO * T)
            .addAnimation("torso", giro(rot(0, 0, 0, 0), rot(0.15F, -6, 0, 0), rot(0.5F, -22, 8, 0),
                    seco(0.55F, 35, -8, 0), rot(0.62F, 40, -8, 0), rot(0.75F, 32, -4, 0), rot(1.1F, 0, 0, 0)))
            // Se agacha y recula para coger impulso; luego se mete cuatro
            // pixeles hacia delante: el alcance extra se VE, no solo se nota.
            .addAnimation("torso", mover(pos(0, 0, 0, 0), pos(0.5F, 0, -1.5F, 2), posSeco(0.55F, 0, -1, -4),
                    pos(0.75F, 0, -1, -3.5F), pos(1.1F, 0, 0, 0)))
            // Contraria al torso en cada fotograma: el ojo queda fijo.
            .addAnimation("cabeza", giro(rot(0, 0, 0, 0), rot(0.5F, 20, -8, 0), seco(0.55F, -28, 8, 0),
                    rot(0.62F, -32, 8, 0), rot(0.66F, -28, 8, 5), rot(0.70F, -28, 8, -5), rot(0.75F, -28, 6, 0),
                    rot(1.1F, 0, 0, 0)))
            .addAnimation("brazo_izq", giro(rot(0, 0, 0, 0), rot(0.15F, 5, 0, -15), rot(0.5F, 25, -20, -100),
                    seco(0.55F, -85, 25, -10), rot(0.62F, -95, 30, -2), rot(0.68F, -88, 25, -8),
                    rot(0.75F, -90, 25, -5), rot(1.1F, 0, 0, 0)))
            .addAnimation("brazo_der", giro(rot(0, 0, 0, 0), rot(0.15F, 5, 0, 15), rot(0.5F, 25, 20, 100),
                    seco(0.55F, -85, -25, 10), rot(0.62F, -95, -30, 2), rot(0.68F, -88, -25, 8),
                    rot(0.75F, -90, -25, 5), rot(1.1F, 0, 0, 0)))
            // Antebrazos doblados al frente en la apertura: los dos brazos
            // abiertos forman las fauces de la trampa.
            .addAnimation("antebrazo_izq", giro(rot(0, 0, 0, 0), rot(0.5F, -55, 0, 0), seco(0.55F, -20, 0, 0),
                    rot(0.62F, -30, 0, 0), rot(1.1F, 0, 0, 0)))
            .addAnimation("antebrazo_der", giro(rot(0, 0, 0, 0), rot(0.5F, -55, 0, 0), seco(0.55F, -20, 0, 0),
                    rot(0.62F, -30, 0, 0), rot(1.1F, 0, 0, 0)))
            .addAnimation("garras_izq", giro(rot(0, 0, 0, 0), rot(0.5F, 45, 0, 0), seco(0.55F, -45, 0, 0),
                    rot(0.75F, -45, 0, 0), rot(1.1F, 0, 0, 0)))
            .addAnimation("garras_der", giro(rot(0, 0, 0, 0), rot(0.5F, 45, 0, 0), seco(0.55F, -45, 0, 0),
                    rot(0.75F, -45, 0, 0), rot(1.1F, 0, 0, 0)))
            // Piernas: abre la base y flexiona; en el golpe la de delante
            // avanza y la de atras empuja.
            .addAnimation("pierna_izq", giro(rot(0, 0, 0, 0), rot(0.5F, -15, 0, -6), seco(0.55F, -30, 0, -6),
                    rot(0.75F, -28, 0, -4), rot(1.1F, 0, 0, 0)))
            .addAnimation("espinilla_izq", giro(rot(0, 0, 0, 0), rot(0.5F, 25, 0, 0), seco(0.55F, 10, 0, 0),
                    rot(1.1F, 0, 0, 0)))
            .addAnimation("pierna_der", giro(rot(0, 0, 0, 0), rot(0.5F, 10, 0, 6), seco(0.55F, 22, 0, 6),
                    rot(0.75F, 20, 0, 4), rot(1.1F, 0, 0, 0)))
            .addAnimation("espinilla_der", giro(rot(0, 0, 0, 0), rot(0.5F, 15, 0, 0), seco(0.55F, 0, 0, 0),
                    rot(1.1F, 0, 0, 0)))
            // La pupila se dilata al apuntar y se contrae en el golpe.
            .addAnimation("ojo", escala(esc(0, 1), esc(0.45F, 1.35F), seco(0.55F, 0.9F), esc(0.7F, 1.1F), esc(1.1F, 1)))
            .addAnimation("capa", giro(rot(0, 0, 0, 0), rot(0.5F, -5, 0, 0), seco(0.55F, 35, 0, 0),
                    rot(0.75F, 40, 0, 4), rot(1.1F, 0, 0, 0)))
            .build();

    // ------------------------------------------------------------------
    //  Mirada: se clava, abre los brazos, el ojo crece y al final retrocede
    //  con el disparo. Es la animacion que el jugador tiene que aprender.
    // ------------------------------------------------------------------

    public static final AnimationDefinition MIRADA = AnimationDefinition.Builder
            .withLength(VigiaEntity.DURACION_MIRADA * T)
            .addAnimation("torso", giro(rot(0, 0, 0, 0), rot(0.3F, -20, 0, 0), rot(1.8F, -24, 0, 0),
                    seco(1.95F, 8, 0, 0), rot(2.0F, 5, 0, 0)))
            .addAnimation("brazo_izq", giro(rot(0, 0, 0, 0), rot(0.4F, -20, 0, -35), rot(1.8F, -25, 0, -50),
                    seco(1.95F, -5, 0, -15), rot(2.0F, 0, 0, -10)))
            .addAnimation("brazo_der", giro(rot(0, 0, 0, 0), rot(0.4F, -20, 0, 35), rot(1.8F, -25, 0, 50),
                    seco(1.95F, -5, 0, 15), rot(2.0F, 0, 0, 10)))
            .addAnimation("antebrazo_izq", giro(rot(0, 0, 0, 0), rot(0.4F, -60, 0, 0), rot(2.0F, -50, 0, 0)))
            .addAnimation("antebrazo_der", giro(rot(0, 0, 0, 0), rot(0.4F, -60, 0, 0), rot(2.0F, -50, 0, 0)))
            .addAnimation("garras_izq", giro(rot(0, 0, 0, 0), rot(0.4F, 40, 0, 0), rot(2.0F, 40, 0, 0)))
            .addAnimation("garras_der", giro(rot(0, 0, 0, 0), rot(0.4F, 40, 0, 0), rot(2.0F, 40, 0, 0)))
            // El cuello tiembla en el ultimo medio segundo: el aviso final.
            .addAnimation("cuello", giro(rot(0, 0, 0, 0), rot(1.5F, 0, 0, 0), rot(1.6F, 0, 0, 3),
                    rot(1.7F, 0, 0, -3), rot(1.8F, 0, 0, 3), rot(1.9F, 0, 0, -3), rot(2.0F, 0, 0, 0)))
            .addAnimation("ojo", escala(esc(0, 1), esc(0.4F, 1.2F), esc(1.0F, 1.3F), esc(1.4F, 1.45F),
                    esc(1.8F, 1.6F), esc(1.9F, 1.9F), esc(2.0F, 1.0F)))
            .addAnimation("capa", giro(rot(0, 0, 0, 0), rot(0.4F, 25, 0, 0), rot(1.8F, 32, 0, 0), rot(2.0F, 12, 0, 0)))
            .build();

    // ------------------------------------------------------------------
    //  Tambaleo: le han dado por la espalda. Se dobla, se tuerce, recupera.
    // ------------------------------------------------------------------

    public static final AnimationDefinition TAMBALEO = AnimationDefinition.Builder
            .withLength(VigiaEntity.DURACION_TAMBALEO * T)
            .addAnimation("torso", giro(rot(0, 0, 0, 0), seco(0.15F, 15, 0, 15), rot(0.4F, 12, 0, -10),
                    rot(0.7F, 8, 0, 6), rot(1.0F, 3, 0, -2), rot(1.2F, 0, 0, 0)))
            .addAnimation("cabeza", giro(rot(0, 0, 0, 0), seco(0.15F, 25, 0, -10), rot(1.0F, 10, 0, 0), rot(1.2F, 0, 0, 0)))
            .addAnimation("brazo_izq", giro(rot(0, 0, 0, 0), seco(0.15F, 0, 0, -30), rot(0.5F, 10, 0, 10), rot(1.2F, 0, 0, 0)))
            .addAnimation("brazo_der", giro(rot(0, 0, 0, 0), seco(0.15F, 0, 0, 30), rot(0.5F, 10, 0, -5), rot(1.2F, 0, 0, 0)))
            .addAnimation("pierna_izq", giro(rot(0, 0, 0, 0), seco(0.15F, -15, 0, 0), rot(0.5F, 5, 0, 0), rot(1.2F, 0, 0, 0)))
            .addAnimation("espinilla_izq", giro(rot(0, 0, 0, 0), seco(0.15F, 20, 0, 0), rot(0.5F, 0, 0, 0)))
            .addAnimation("ojo", escala(esc(0, 1), seco(0.15F, 0.6F), esc(0.5F, 1.0F)))
            .build();

    /** El atajo de escala sin suavizar, para el parpadeo del golpe. */
    private static Keyframe seco(float t, float s) {
        return new Keyframe(t, KeyframeAnimations.scaleVec(s, s, s), AnimationChannel.Interpolations.LINEAR);
    }
}
