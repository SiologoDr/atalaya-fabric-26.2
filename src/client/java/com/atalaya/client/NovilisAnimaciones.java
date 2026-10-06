package com.atalaya.client;

import net.minecraft.client.animation.AnimationChannel;
import net.minecraft.client.animation.AnimationDefinition;
import net.minecraft.client.animation.Keyframe;
import net.minecraft.client.animation.KeyframeAnimations;

/**
 * Las animaciones de Novilis. GENERADO por materiales/generadores/novilis_juego_anim.py:
 * no se editan a mano. El servidor saca de las mismas poses por donde pasan las
 * manos y la espada (NovilisGeometria).
 */
public final class NovilisAnimaciones {

    public static final AnimationDefinition REPOSO = reposo();
    public static final AnimationDefinition ANDAR = andar();
    public static final AnimationDefinition DORMIDO = dormido();
    public static final AnimationDefinition DESPERTAR = despertar();
    public static final AnimationDefinition BARRIDO = barrido();
    public static final AnimationDefinition CASTIGO = castigo();
    public static final AnimationDefinition CASTIGO_ONDA = castigo_onda();
    public static final AnimationDefinition SOL = sol();
    public static final AnimationDefinition TROMPETAS = trompetas();
    public static final AnimationDefinition FUENTES = fuentes();
    public static final AnimationDefinition FUENTES_CARGA = fuentes_carga();
    public static final AnimationDefinition OFRENDA = ofrenda();
    public static final AnimationDefinition OFRENDA_SOSTIENE = ofrenda_sostiene();
    public static final AnimationDefinition DIOS = dios();
    public static final AnimationDefinition GRITO = grito();
    public static final AnimationDefinition ATURDIDO = aturdido();
    public static final AnimationDefinition ATURDIDO_BUCLE = aturdido_bucle();
    public static final AnimationDefinition TAMBALEO = tambaleo();
    public static final AnimationDefinition LIBERACION = liberacion();

    private NovilisAnimaciones() {
    }

    private static Keyframe rot(float t, float x, float y, float z) {
        return new Keyframe(t, KeyframeAnimations.degreeVec(x, y, z), AnimationChannel.Interpolations.CATMULLROM);
    }

    private static Keyframe seco(float t, float x, float y, float z) {
        return new Keyframe(t, KeyframeAnimations.degreeVec(x, y, z), AnimationChannel.Interpolations.LINEAR);
    }

    private static Keyframe pos(float t, float x, float y, float z) {
        return new Keyframe(t, KeyframeAnimations.posVec(x, y, z), AnimationChannel.Interpolations.CATMULLROM);
    }

    private static Keyframe posSeco(float t, float x, float y, float z) {
        return new Keyframe(t, KeyframeAnimations.posVec(x, y, z), AnimationChannel.Interpolations.LINEAR);
    }

    private static Keyframe esc(float t, float x, float y, float z) {
        return new Keyframe(t, KeyframeAnimations.scaleVec(x, y, z), AnimationChannel.Interpolations.CATMULLROM);
    }

    private static Keyframe escSeco(float t, float x, float y, float z) {
        return new Keyframe(t, KeyframeAnimations.scaleVec(x, y, z), AnimationChannel.Interpolations.LINEAR);
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

    private static AnimationDefinition reposo() {
        return AnimationDefinition.Builder.withLength(4F).looping()
                .addAnimation("brazo_der", giro(rot(0F, 0F, 0F, 0F),
                        rot(2F, 2.5F, 0F, 0F),
                        rot(4F, 0F, 0F, 0F)))
                .addAnimation("torso", giro(rot(0F, 0F, 0F, 0F),
                        rot(2F, 1.8F, 0F, 0F),
                        rot(4F, 0F, 0F, 0F)))
                .addAnimation("cabeza", giro(rot(0F, 0F, 0F, 0F),
                        rot(2F, -2F, 4F, 0F),
                        rot(4F, 0F, 0F, 0F)))
                .addAnimation("pelvis", mover(pos(0F, 0F, 0F, 0F),
                        pos(2F, 0F, -0.8F, 0F),
                        pos(4F, 0F, 0F, 0F)))
                .addAnimation("capa_1", giro(rot(0F, 0F, 0F, 0F),
                        rot(2F, 3F, 0F, 0F),
                        rot(4F, 0F, 0F, 0F)))
                .addAnimation("capa_2", giro(rot(0F, 0F, 0F, 0F),
                        rot(2F, 2F, 0F, 0F),
                        rot(4F, 0F, 0F, 0F)))
                .build();
    }

    private static AnimationDefinition andar() {
        return AnimationDefinition.Builder.withLength(2F).looping()
                .addAnimation("brazo_izq", giro(rot(0F, 14F, 0F, 0F),
                        rot(0.5F, 14F, 0F, 0F),
                        rot(1F, -14F, 0F, 0F),
                        rot(1.5F, -14F, 0F, 0F),
                        rot(2F, 14F, 0F, 0F)))
                .addAnimation("pierna_izq", giro(rot(0F, -24F, 0F, 0F),
                        rot(0.5F, 4F, 0F, 0F),
                        rot(1F, 24F, 0F, 0F),
                        rot(1.5F, -18F, 0F, 0F),
                        rot(2F, -24F, 0F, 0F)))
                .addAnimation("espinilla_izq", giro(rot(0F, 8F, 0F, 0F),
                        rot(0.5F, 6F, 0F, 0F),
                        rot(1F, 26F, 0F, 0F),
                        rot(1.5F, 46F, 0F, 0F),
                        rot(2F, 8F, 0F, 0F)))
                .addAnimation("pie_izq", giro(rot(0F, 6F, 0F, 0F),
                        rot(0.5F, -4F, 0F, 0F),
                        rot(1F, -10F, 0F, 0F),
                        rot(1.5F, -6F, 0F, 0F),
                        rot(2F, 6F, 0F, 0F)))
                .addAnimation("pierna_der", giro(rot(0F, 24F, 0F, 0F),
                        rot(0.5F, -18F, 0F, 0F),
                        rot(1F, -24F, 0F, 0F),
                        rot(1.5F, 4F, 0F, 0F),
                        rot(2F, 24F, 0F, 0F)))
                .addAnimation("espinilla_der", giro(rot(0F, 26F, 0F, 0F),
                        rot(0.5F, 46F, 0F, 0F),
                        rot(1F, 8F, 0F, 0F),
                        rot(1.5F, 6F, 0F, 0F),
                        rot(2F, 26F, 0F, 0F)))
                .addAnimation("pie_der", giro(rot(0F, -10F, 0F, 0F),
                        rot(0.5F, -6F, 0F, 0F),
                        rot(1F, 6F, 0F, 0F),
                        rot(1.5F, -4F, 0F, 0F),
                        rot(2F, -10F, 0F, 0F)))
                .addAnimation("pelvis", mover(pos(0F, 0F, -2F, 0F),
                        pos(0.5F, 0F, 0.6F, 0F),
                        pos(1F, 0F, -2F, 0F),
                        pos(1.5F, 0F, 0.6F, 0F),
                        pos(2F, 0F, -2F, 0F)))
                .addAnimation("torso", giro(rot(0F, 3F, 5F, 0F),
                        rot(0.5F, 3F, 5F, 0F),
                        rot(1F, 3F, -5F, 0F),
                        rot(1.5F, 3F, -5F, 0F),
                        rot(2F, 3F, 5F, 0F)))
                .addAnimation("cabeza", giro(rot(0F, 0F, -4F, 0F),
                        rot(0.5F, 0F, -4F, 0F),
                        rot(1F, 0F, 4F, 0F),
                        rot(1.5F, 0F, 4F, 0F),
                        rot(2F, 0F, -4F, 0F)))
                .addAnimation("capa_1", giro(rot(0F, 6F, 0F, 0F),
                        rot(0.5F, 9F, 0F, 0F),
                        rot(1F, 6F, 0F, 0F),
                        rot(1.5F, 9F, 0F, 0F),
                        rot(2F, 6F, 0F, 0F)))
                .addAnimation("capa_2", giro(rot(0F, 3F, 0F, 0F),
                        rot(0.5F, 3F, 0F, 0F),
                        rot(1F, 3F, 0F, 0F),
                        rot(1.5F, 3F, 0F, 0F),
                        rot(2F, 3F, 0F, 0F)))
                .addAnimation("capa_3", giro(rot(0F, 4F, 0F, 0F),
                        rot(0.5F, 4F, 0F, 0F),
                        rot(1F, 4F, 0F, 0F),
                        rot(1.5F, 4F, 0F, 0F),
                        rot(2F, 4F, 0F, 0F)))
                .build();
    }

    private static AnimationDefinition dormido() {
        return AnimationDefinition.Builder.withLength(6F).looping()
                .addAnimation("pelvis", mover(pos(0F, 0F, -30F, 0F),
                        pos(3F, 0F, -30F, 0F),
                        pos(6F, 0F, -30F, 0F)))
                .addAnimation("tabardo", giro(rot(0F, -70F, 0F, 0F),
                        rot(3F, -70F, 0F, 0F),
                        rot(6F, -70F, 0F, 0F)))
                .addAnimation("pierna_izq", giro(rot(0F, -86F, 0F, -6F),
                        rot(3F, -86F, 0F, -6F),
                        rot(6F, -86F, 0F, -6F)))
                .addAnimation("espinilla_izq", giro(rot(0F, 86F, 0F, 0F),
                        rot(3F, 86F, 0F, 0F),
                        rot(6F, 86F, 0F, 0F)))
                .addAnimation("pierna_der", giro(rot(0F, 6F, 0F, 5F),
                        rot(3F, 6F, 0F, 5F),
                        rot(6F, 6F, 0F, 5F)))
                .addAnimation("espinilla_der", giro(rot(0F, 86F, 0F, 0F),
                        rot(3F, 86F, 0F, 0F),
                        rot(6F, 86F, 0F, 0F)))
                .addAnimation("pie_der", giro(rot(0F, -62F, 0F, 0F),
                        rot(3F, -62F, 0F, 0F),
                        rot(6F, -62F, 0F, 0F)))
                .addAnimation("capa_1", giro(rot(0F, 8F, 0F, 0F),
                        rot(3F, 8F, 0F, 0F),
                        rot(6F, 8F, 0F, 0F)))
                .addAnimation("capa_2", giro(rot(0F, 24F, 0F, 0F),
                        rot(3F, 24F, 0F, 0F),
                        rot(6F, 24F, 0F, 0F)))
                .addAnimation("capa_3", giro(rot(0F, 50F, 0F, 0F),
                        rot(3F, 50F, 0F, 0F),
                        rot(6F, 50F, 0F, 0F)))
                .addAnimation("torso", giro(rot(0F, 18F, 0F, 0F),
                        rot(3F, 20F, 0F, 0F),
                        rot(6F, 18F, 0F, 0F)))
                .addAnimation("cuello", giro(rot(0F, 8F, 0F, 0F),
                        rot(3F, 8F, 0F, 0F),
                        rot(6F, 8F, 0F, 0F)))
                .addAnimation("cabeza", giro(rot(0F, 26F, 0F, 0F),
                        rot(3F, 30F, 0F, 0F),
                        rot(6F, 26F, 0F, 0F)))
                .addAnimation("brazo_der", giro(rot(0F, -32.299F, -0.008F, -38.553F),
                        rot(3F, -32.299F, -0.008F, -38.553F),
                        rot(6F, -32.299F, -0.008F, -38.553F)))
                .addAnimation("antebrazo_der", giro(rot(0F, 38.214F, 0F, 0F),
                        rot(3F, 38.214F, 0F, 0F),
                        rot(6F, 38.214F, 0F, 0F)))
                .addAnimation("brazo_izq", giro(rot(0F, -28.094F, -0.012F, 49.168F),
                        rot(3F, -28.094F, -0.012F, 49.168F),
                        rot(6F, -28.094F, -0.012F, 49.168F)))
                .addAnimation("antebrazo_izq", giro(rot(0F, -7.727F, 0F, 0F),
                        rot(3F, -7.727F, 0F, 0F),
                        rot(6F, -7.727F, 0F, 0F)))
                .addAnimation("agarre", giro(rot(0F, 28.177F, -9.668F, 27.123F),
                        rot(3F, 28.177F, -9.668F, 27.123F),
                        rot(6F, 28.177F, -9.668F, 27.123F)))
                .build();
    }

    private static AnimationDefinition despertar() {
        return AnimationDefinition.Builder.withLength(3.4F)
                .addAnimation("pelvis", mover(pos(0F, 0F, -30F, 0F),
                        pos(0.5F, 0F, -30F, 0F),
                        pos(1.3F, 0F, -12F, 0F),
                        pos(1.9F, 0F, 0F, 0F),
                        posSeco(2.4F, 0F, -1F, 0F),
                        pos(2.9F, 0F, -1F, 0F),
                        pos(3.4F, 0F, 0F, 0F)))
                .addAnimation("tabardo", giro(rot(0F, -70F, 0F, 0F),
                        rot(0.5F, -70F, 0F, 0F),
                        rot(1.3F, 0F, 0F, 0F),
                        rot(1.9F, 0F, 0F, 0F),
                        seco(2.4F, 0F, 0F, 0F),
                        rot(2.9F, 0F, 0F, 0F),
                        rot(3.4F, 0F, 0F, 0F)))
                .addAnimation("pierna_izq", giro(rot(0F, -86F, 0F, -6F),
                        rot(0.5F, -86F, 0F, -6F),
                        rot(1.3F, -50F, 0F, -6F),
                        rot(1.9F, 0F, 0F, 0F),
                        seco(2.4F, -14F, 0F, -8F),
                        rot(2.9F, -14F, 0F, -8F),
                        rot(3.4F, 0F, 0F, 0F)))
                .addAnimation("espinilla_izq", giro(rot(0F, 86F, 0F, 0F),
                        rot(0.5F, 86F, 0F, 0F),
                        rot(1.3F, 60F, 0F, 0F),
                        rot(1.9F, 0F, 0F, 0F),
                        seco(2.4F, 16F, 0F, 0F),
                        rot(2.9F, 16F, 0F, 0F),
                        rot(3.4F, 0F, 0F, 0F)))
                .addAnimation("pierna_der", giro(rot(0F, 6F, 0F, 5F),
                        rot(0.5F, 6F, 0F, 5F),
                        rot(1.3F, 10F, 0F, 5F),
                        rot(1.9F, 0F, 0F, 0F),
                        seco(2.4F, 12F, 0F, 8F),
                        rot(2.9F, 12F, 0F, 8F),
                        rot(3.4F, 0F, 0F, 0F)))
                .addAnimation("espinilla_der", giro(rot(0F, 86F, 0F, 0F),
                        rot(0.5F, 86F, 0F, 0F),
                        rot(1.3F, 50F, 0F, 0F),
                        rot(1.9F, 0F, 0F, 0F),
                        seco(2.4F, 0F, 0F, 0F),
                        rot(2.9F, 0F, 0F, 0F),
                        rot(3.4F, 0F, 0F, 0F)))
                .addAnimation("pie_der", giro(rot(0F, -62F, 0F, 0F),
                        rot(0.5F, -62F, 0F, 0F),
                        rot(1.3F, -30F, 0F, 0F),
                        rot(1.9F, 0F, 0F, 0F),
                        seco(2.4F, -14F, 0F, 0F),
                        rot(2.9F, -14F, 0F, 0F),
                        rot(3.4F, 0F, 0F, 0F)))
                .addAnimation("capa_1", giro(rot(0F, 8F, 0F, 0F),
                        rot(0.5F, 8F, 0F, 0F),
                        rot(1.3F, 0F, 0F, 0F),
                        rot(1.9F, 20F, 0F, 0F),
                        seco(2.4F, 20F, 0F, 0F),
                        rot(2.9F, 20F, 0F, 0F),
                        rot(3.4F, 0F, 0F, 0F)))
                .addAnimation("capa_2", giro(rot(0F, 24F, 0F, 0F),
                        rot(0.5F, 24F, 0F, 0F),
                        rot(1.3F, 0F, 0F, 0F),
                        rot(1.9F, 10F, 0F, 0F),
                        seco(2.4F, 10F, 0F, 0F),
                        rot(2.9F, 10F, 0F, 0F),
                        rot(3.4F, 0F, 0F, 0F)))
                .addAnimation("capa_3", giro(rot(0F, 50F, 0F, 0F),
                        rot(0.5F, 50F, 0F, 0F),
                        rot(1.3F, 0F, 0F, 0F),
                        rot(1.9F, 12F, 0F, 0F),
                        seco(2.4F, 12F, 0F, 0F),
                        rot(2.9F, 12F, 0F, 0F),
                        rot(3.4F, 0F, 0F, 0F)))
                .addAnimation("torso", giro(rot(0F, 18F, 0F, 0F),
                        rot(0.5F, 18F, 0F, 0F),
                        rot(1.3F, 16F, 0F, 0F),
                        rot(1.9F, -6F, 0F, 0F),
                        seco(2.4F, -10F, 0F, 0F),
                        rot(2.9F, -10F, 0F, 0F),
                        rot(3.4F, 0F, 0F, 0F)))
                .addAnimation("cuello", giro(rot(0F, 8F, 0F, 0F),
                        rot(0.5F, 8F, 0F, 0F),
                        rot(1.3F, 0F, 0F, 0F),
                        rot(1.9F, 0F, 0F, 0F),
                        seco(2.4F, 0F, 0F, 0F),
                        rot(2.9F, 0F, 0F, 0F),
                        rot(3.4F, 0F, 0F, 0F)))
                .addAnimation("cabeza", giro(rot(0F, 26F, 0F, 0F),
                        rot(0.5F, -10F, 0F, 0F),
                        rot(1.3F, -4F, 0F, 0F),
                        rot(1.9F, -20F, 0F, 0F),
                        seco(2.4F, -26F, 0F, 0F),
                        rot(2.9F, -30F, 4F, 0F),
                        rot(3.4F, 0F, 0F, 0F)))
                .addAnimation("brazo_der", giro(rot(0F, -32.299F, -0.008F, -38.553F),
                        rot(0.5F, -32.299F, -0.008F, -38.553F),
                        rot(1.3F, -38.188F, -0.007F, -28.617F),
                        rot(1.9F, -123.391F, -0.03F, 4.58F),
                        seco(2.4F, 9.304F, -0.009F, 21.179F),
                        rot(2.9F, 9.304F, -0.009F, 21.179F),
                        rot(3.4F, 0F, 0F, 0F)))
                .addAnimation("antebrazo_der", giro(rot(0F, 38.214F, 0F, 0F),
                        rot(0.5F, 38.214F, 0F, 0F),
                        rot(1.3F, 47.447F, 0F, 0F),
                        rot(1.9F, -9.497F, 0F, 0F),
                        seco(2.4F, -2.939F, 0F, 0F),
                        rot(2.9F, -2.939F, 0F, 0F),
                        rot(3.4F, 0F, 0F, 0F)))
                .addAnimation("brazo_izq", giro(rot(0F, -28.094F, -0.012F, 49.168F),
                        rot(0.5F, -28.094F, -0.012F, 49.168F),
                        rot(1.3F, 15.271F, -0.008F, 1.327F),
                        rot(1.9F, -1.477F, -0.006F, -24.465F),
                        seco(2.4F, -15.581F, 0.007F, -20.098F),
                        rot(2.9F, -15.581F, 0.007F, -20.098F),
                        rot(3.4F, 0F, 0F, 0F)))
                .addAnimation("antebrazo_izq", giro(rot(0F, -7.727F, 0F, 0F),
                        rot(0.5F, -7.727F, 0F, 0F),
                        rot(1.3F, -38.041F, 0F, 0F),
                        rot(1.9F, -16.863F, 0F, 0F),
                        seco(2.4F, 8.586F, 0F, 0F),
                        rot(2.9F, 8.586F, 0F, 0F),
                        rot(3.4F, 0F, 0F, 0F)))
                .addAnimation("agarre", giro(rot(0F, 28.177F, -9.668F, 27.123F),
                        rot(0.5F, 28.177F, -9.668F, 27.123F),
                        rot(1.3F, 33.919F, -19.229F, 13.004F),
                        rot(1.9F, 11.845F, -27.138F, 10.068F),
                        seco(2.4F, -1.107F, 13.903F, 7.53F),
                        rot(2.9F, -1.107F, 13.903F, 7.53F),
                        rot(3.4F, 0F, 0F, 0F)))
                .build();
    }

    private static AnimationDefinition barrido() {
        return AnimationDefinition.Builder.withLength(3.8F)
                .addAnimation("brazo_der", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.32F, -81.661F, -0.02F, 218.305F),
                        seco(0.6F, -57.191F, -0.005F, -51.697F),
                        rot(0.85F, -57.191F, -0.005F, -51.697F),
                        rot(1.12F, 7.312F, -0.009F, -81.468F),
                        seco(1.4F, -60.895F, -0.002F, -37.046F),
                        rot(1.62F, -60.895F, -0.002F, -37.046F),
                        rot(1.9F, -34.117F, -0.033F, -172.509F),
                        seco(2.2F, -48.902F, -0.009F, -42.494F),
                        rot(2.45F, -48.902F, -0.009F, -42.494F),
                        rot(2.78F, 56.451F, 0.011F, 38.276F),
                        seco(3.1F, -55.483F, -0.011F, -60.439F),
                        rot(3.35F, -55.483F, -0.011F, -60.439F),
                        rot(3.8F, 0F, 0F, 0F)))
                .addAnimation("antebrazo_der", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.32F, -86.403F, 0F, 0F),
                        seco(0.6F, 47.467F, 0F, 0F),
                        rot(0.85F, 47.467F, 0F, 0F),
                        rot(1.12F, 12.743F, 0F, 0F),
                        seco(1.4F, 47.442F, 0F, 0F),
                        rot(1.62F, 47.442F, 0F, 0F),
                        rot(1.9F, -246.569F, 0F, 0F),
                        seco(2.2F, 47.449F, 0F, 0F),
                        rot(2.45F, 47.449F, 0F, 0F),
                        rot(2.78F, -71.996F, 0F, 0F),
                        seco(3.1F, 47.456F, 0F, 0F),
                        rot(3.35F, 47.456F, 0F, 0F),
                        rot(3.8F, 0F, 0F, 0F)))
                .addAnimation("brazo_izq", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.32F, 20.205F, 0.007F, -19.863F),
                        seco(0.6F, 25.767F, 0.004F, -16.804F),
                        rot(0.85F, 25.767F, 0.004F, -16.804F),
                        rot(1.12F, 29.757F, -0.001F, -16.92F),
                        seco(1.4F, 17.827F, -0.013F, -19.466F),
                        rot(1.62F, 17.827F, -0.013F, -19.466F),
                        rot(1.9F, -1.816F, -0.007F, -13.291F),
                        seco(2.2F, 36.191F, -0.006F, -15.216F),
                        rot(2.45F, 36.191F, -0.006F, -15.216F),
                        rot(2.78F, 27.11F, 0.02F, -20.644F),
                        seco(3.1F, 19.426F, 0.005F, -16.135F),
                        rot(3.35F, 19.426F, 0.005F, -16.135F),
                        rot(3.8F, 0F, 0F, 0F)))
                .addAnimation("antebrazo_izq", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.32F, -41.686F, 0F, 0F),
                        seco(0.6F, -38.209F, 0F, 0F),
                        rot(0.85F, -38.209F, 0F, 0F),
                        rot(1.12F, -37.892F, 0F, 0F),
                        seco(1.4F, -41.427F, 0F, 0F),
                        rot(1.62F, -41.427F, 0F, 0F),
                        rot(1.9F, -36.124F, 0F, 0F),
                        seco(2.2F, -29.791F, 0F, 0F),
                        rot(2.45F, -29.791F, 0F, 0F),
                        rot(2.78F, -41.951F, 0F, 0F),
                        seco(3.1F, -38.026F, 0F, 0F),
                        rot(3.35F, -38.026F, 0F, 0F),
                        rot(3.8F, 0F, 0F, 0F)))
                .addAnimation("agarre", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.32F, -82.197F, -97.22F, 25.751F),
                        seco(0.6F, 2.99F, -5.97F, -28.478F),
                        rot(0.85F, 2.99F, -5.97F, -28.478F),
                        rot(1.12F, -65.869F, -131.42F, 30.574F),
                        seco(1.4F, -46.204F, 31.496F, 1.158F),
                        rot(1.62F, -46.204F, 31.496F, 1.158F),
                        rot(1.9F, -0.114F, 2.308F, -37.721F),
                        seco(2.2F, -11.589F, -1.945F, -1.675F),
                        rot(2.45F, -11.589F, -1.945F, -1.675F),
                        rot(2.78F, -79.678F, 126.017F, -8.952F),
                        seco(3.1F, 2.376F, -20.08F, -23.931F),
                        rot(3.35F, 2.376F, -20.08F, -23.931F),
                        rot(3.8F, 0F, 0F, 0F)))
                .addAnimation("torso", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.32F, 4F, 26F, 0F),
                        seco(0.6F, 4F, -26F, 0F),
                        rot(0.85F, 4F, -26F, 0F),
                        rot(1.12F, 4F, -22F, 0F),
                        seco(1.4F, 4F, 24F, 0F),
                        rot(1.62F, 4F, 24F, 0F),
                        rot(1.9F, 4F, 8F, 0F),
                        seco(2.2F, 22F, -14F, 0F),
                        rot(2.45F, 22F, -14F, 0F),
                        rot(2.78F, 4F, 32F, 0F),
                        seco(3.1F, 4F, -32F, 0F),
                        rot(3.35F, 4F, -32F, 0F),
                        rot(3.8F, 0F, 0F, 0F)))
                .addAnimation("cabeza", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.32F, 0F, -15.6F, 0F),
                        seco(0.6F, 0F, 15.6F, 0F),
                        rot(0.85F, 0F, 15.6F, 0F),
                        rot(1.12F, 0F, 13.2F, 0F),
                        seco(1.4F, 0F, -14.4F, 0F),
                        rot(1.62F, 0F, -14.4F, 0F),
                        rot(1.9F, -14F, 0F, 0F),
                        seco(2.2F, 0F, 8.4F, 0F),
                        rot(2.45F, 0F, 8.4F, 0F),
                        rot(2.78F, 0F, -19.2F, 0F),
                        seco(3.1F, 0F, 19.2F, 0F),
                        rot(3.35F, 0F, 19.2F, 0F),
                        rot(3.8F, 0F, 0F, 0F)))
                .addAnimation("pelvis", mover(pos(0F, 0F, 0F, 0F),
                        pos(0.32F, 0F, -2F, 0F),
                        posSeco(0.6F, 0F, -2F, 0F),
                        pos(0.85F, 0F, -2F, 0F),
                        pos(1.12F, 0F, -2F, 0F),
                        posSeco(1.4F, 0F, -2F, 0F),
                        pos(1.62F, 0F, -2F, 0F),
                        pos(1.9F, 0F, -2F, 0F),
                        posSeco(2.2F, 0F, -2F, 0F),
                        pos(2.45F, 0F, -2F, 0F),
                        pos(2.78F, 0F, -2F, 0F),
                        posSeco(3.1F, 0F, -2F, 0F),
                        pos(3.35F, 0F, -2F, 0F),
                        pos(3.8F, 0F, 0F, 0F)))
                .addAnimation("pierna_izq", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.32F, -14F, 0F, -8F),
                        seco(0.6F, -20F, 0F, -8F),
                        rot(0.85F, -20F, 0F, -8F),
                        rot(1.12F, -14F, 0F, -8F),
                        seco(1.4F, -20F, 0F, -8F),
                        rot(1.62F, -20F, 0F, -8F),
                        rot(1.9F, -14F, 0F, -8F),
                        seco(2.2F, -24F, 0F, -8F),
                        rot(2.45F, -24F, 0F, -8F),
                        rot(2.78F, -14F, 0F, -8F),
                        seco(3.1F, -24F, 0F, -8F),
                        rot(3.35F, -24F, 0F, -8F),
                        rot(3.8F, 0F, 0F, 0F)))
                .addAnimation("espinilla_izq", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.32F, 18F, 0F, 0F),
                        seco(0.6F, 24F, 0F, 0F),
                        rot(0.85F, 24F, 0F, 0F),
                        rot(1.12F, 18F, 0F, 0F),
                        seco(1.4F, 24F, 0F, 0F),
                        rot(1.62F, 24F, 0F, 0F),
                        rot(1.9F, 18F, 0F, 0F),
                        seco(2.2F, 28F, 0F, 0F),
                        rot(2.45F, 28F, 0F, 0F),
                        rot(2.78F, 18F, 0F, 0F),
                        seco(3.1F, 28F, 0F, 0F),
                        rot(3.35F, 28F, 0F, 0F),
                        rot(3.8F, 0F, 0F, 0F)))
                .addAnimation("pierna_der", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.32F, 14F, 0F, 8F),
                        seco(0.6F, 14F, 0F, 8F),
                        rot(0.85F, 14F, 0F, 8F),
                        rot(1.12F, 14F, 0F, 8F),
                        seco(1.4F, 14F, 0F, 8F),
                        rot(1.62F, 14F, 0F, 8F),
                        rot(1.9F, 14F, 0F, 8F),
                        seco(2.2F, 14F, 0F, 8F),
                        rot(2.45F, 14F, 0F, 8F),
                        rot(2.78F, 14F, 0F, 8F),
                        seco(3.1F, 14F, 0F, 8F),
                        rot(3.35F, 14F, 0F, 8F),
                        rot(3.8F, 0F, 0F, 0F)))
                .addAnimation("espinilla_der", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.32F, 10F, 0F, 0F),
                        seco(0.6F, 10F, 0F, 0F),
                        rot(0.85F, 10F, 0F, 0F),
                        rot(1.12F, 10F, 0F, 0F),
                        seco(1.4F, 10F, 0F, 0F),
                        rot(1.62F, 10F, 0F, 0F),
                        rot(1.9F, 10F, 0F, 0F),
                        seco(2.2F, 10F, 0F, 0F),
                        rot(2.45F, 10F, 0F, 0F),
                        rot(2.78F, 10F, 0F, 0F),
                        seco(3.1F, 10F, 0F, 0F),
                        rot(3.35F, 10F, 0F, 0F),
                        rot(3.8F, 0F, 0F, 0F)))
                .addAnimation("pie_der", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.32F, -20F, 0F, 0F),
                        seco(0.6F, -20F, 0F, 0F),
                        rot(0.85F, -20F, 0F, 0F),
                        rot(1.12F, -20F, 0F, 0F),
                        seco(1.4F, -20F, 0F, 0F),
                        rot(1.62F, -20F, 0F, 0F),
                        rot(1.9F, -20F, 0F, 0F),
                        seco(2.2F, -20F, 0F, 0F),
                        rot(2.45F, -20F, 0F, 0F),
                        rot(2.78F, -20F, 0F, 0F),
                        seco(3.1F, -20F, 0F, 0F),
                        rot(3.35F, -20F, 0F, 0F),
                        rot(3.8F, 0F, 0F, 0F)))
                .addAnimation("capa_1", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.32F, 20F, 0F, 0F),
                        seco(0.6F, 20F, 0F, 0F),
                        rot(0.85F, 20F, 0F, 0F),
                        rot(1.12F, 20F, 0F, 0F),
                        seco(1.4F, 20F, 0F, 0F),
                        rot(1.62F, 20F, 0F, 0F),
                        rot(1.9F, 20F, 0F, 0F),
                        seco(2.2F, 20F, 0F, 0F),
                        rot(2.45F, 20F, 0F, 0F),
                        rot(2.78F, 20F, 0F, 0F),
                        seco(3.1F, 20F, 0F, 0F),
                        rot(3.35F, 20F, 0F, 0F),
                        rot(3.8F, 0F, 0F, 0F)))
                .addAnimation("capa_2", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.32F, 10F, 0F, 0F),
                        seco(0.6F, 10F, 0F, 0F),
                        rot(0.85F, 10F, 0F, 0F),
                        rot(1.12F, 10F, 0F, 0F),
                        seco(1.4F, 10F, 0F, 0F),
                        rot(1.62F, 10F, 0F, 0F),
                        rot(1.9F, 10F, 0F, 0F),
                        seco(2.2F, 10F, 0F, 0F),
                        rot(2.45F, 10F, 0F, 0F),
                        rot(2.78F, 10F, 0F, 0F),
                        seco(3.1F, 10F, 0F, 0F),
                        rot(3.35F, 10F, 0F, 0F),
                        rot(3.8F, 0F, 0F, 0F)))
                .addAnimation("capa_3", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.32F, 12F, 0F, 0F),
                        seco(0.6F, 12F, 0F, 0F),
                        rot(0.85F, 12F, 0F, 0F),
                        rot(1.12F, 12F, 0F, 0F),
                        seco(1.4F, 12F, 0F, 0F),
                        rot(1.62F, 12F, 0F, 0F),
                        rot(1.9F, 12F, 0F, 0F),
                        seco(2.2F, 12F, 0F, 0F),
                        rot(2.45F, 12F, 0F, 0F),
                        rot(2.78F, 12F, 0F, 0F),
                        seco(3.1F, 12F, 0F, 0F),
                        rot(3.35F, 12F, 0F, 0F),
                        rot(3.8F, 0F, 0F, 0F)))
                .build();
    }

    private static AnimationDefinition castigo() {
        return AnimationDefinition.Builder.withLength(2.8F)
                .addAnimation("brazo_der", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.7F, -152.555F, -0.017F, 21.565F),
                        rot(1.4F, -152.555F, -0.017F, 21.565F),
                        rot(2.1F, -152.555F, -0.017F, 21.565F),
                        rot(2.8F, 0F, 0F, 0F)))
                .addAnimation("antebrazo_der", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.7F, 33.519F, 0F, 0F),
                        rot(1.4F, 33.519F, 0F, 0F),
                        rot(2.1F, 33.519F, 0F, 0F),
                        rot(2.8F, 0F, 0F, 0F)))
                .addAnimation("brazo_izq", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.7F, -139.742F, -0.015F, -27.093F),
                        rot(1.4F, -139.742F, -0.015F, -27.093F),
                        rot(2.1F, -139.742F, -0.015F, -27.093F),
                        rot(2.8F, 0F, 0F, 0F)))
                .addAnimation("antebrazo_izq", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.7F, -16.144F, 0F, 0F),
                        rot(1.4F, -16.144F, 0F, 0F),
                        rot(2.1F, -16.144F, 0F, 0F),
                        rot(2.8F, 0F, 0F, 0F)))
                .addAnimation("agarre", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.7F, -49.449F, 77.91F, -34.315F),
                        rot(1.4F, -49.449F, 77.91F, -34.315F),
                        rot(2.1F, -49.449F, 77.91F, -34.315F),
                        rot(2.8F, 0F, 0F, 0F)))
                .addAnimation("cabeza", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.7F, -24F, 0F, 0F),
                        rot(1.4F, -28F, -3F, 0F),
                        rot(2.1F, -24F, 0F, 0F),
                        rot(2.8F, 0F, 0F, 0F)))
                .addAnimation("torso", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.7F, -6F, 0F, 0F),
                        rot(1.4F, -8F, 2F, 0F),
                        rot(2.1F, -6F, 0F, 0F),
                        rot(2.8F, 0F, 0F, 0F)))
                .addAnimation("capa_1", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.7F, 20F, 0F, 0F),
                        rot(1.4F, 20F, 0F, 0F),
                        rot(2.1F, 20F, 0F, 0F),
                        rot(2.8F, 0F, 0F, 0F)))
                .addAnimation("capa_2", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.7F, 10F, 0F, 0F),
                        rot(1.4F, 10F, 0F, 0F),
                        rot(2.1F, 10F, 0F, 0F),
                        rot(2.8F, 0F, 0F, 0F)))
                .addAnimation("capa_3", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.7F, 12F, 0F, 0F),
                        rot(1.4F, 12F, 0F, 0F),
                        rot(2.1F, 12F, 0F, 0F),
                        rot(2.8F, 0F, 0F, 0F)))
                .build();
    }

    private static AnimationDefinition castigo_onda() {
        return AnimationDefinition.Builder.withLength(4.2F)
                .addAnimation("brazo_der", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.7F, -152.555F, -0.017F, 21.565F),
                        rot(1.4F, -152.555F, -0.017F, 21.565F),
                        rot(2.1F, -152.555F, -0.017F, 21.565F),
                        rot(2.35F, -152.555F, -0.017F, 21.565F),
                        seco(2.6F, -37.145F, -0.008F, -35.142F),
                        rot(3.3F, -37.145F, -0.008F, -35.142F),
                        rot(4.2F, 0F, 0F, 0F)))
                .addAnimation("antebrazo_der", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.7F, 33.519F, 0F, 0F),
                        rot(1.4F, 33.519F, 0F, 0F),
                        rot(2.1F, 33.519F, 0F, 0F),
                        rot(2.35F, 33.519F, 0F, 0F),
                        seco(2.6F, 47.465F, 0F, 0F),
                        rot(3.3F, 47.465F, 0F, 0F),
                        rot(4.2F, 0F, 0F, 0F)))
                .addAnimation("brazo_izq", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.7F, -139.742F, -0.015F, -27.093F),
                        rot(1.4F, -139.742F, -0.015F, -27.093F),
                        rot(2.1F, -139.742F, -0.015F, -27.093F),
                        rot(2.35F, -139.742F, -0.015F, -27.093F),
                        seco(2.6F, -43.963F, -0.01F, 44.223F),
                        rot(3.3F, -43.963F, -0.01F, 44.223F),
                        rot(4.2F, 0F, 0F, 0F)))
                .addAnimation("antebrazo_izq", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.7F, -16.144F, 0F, 0F),
                        rot(1.4F, -16.144F, 0F, 0F),
                        rot(2.1F, -16.144F, 0F, 0F),
                        rot(2.35F, -16.144F, 0F, 0F),
                        seco(2.6F, 18.908F, 0F, 0F),
                        rot(3.3F, 18.908F, 0F, 0F),
                        rot(4.2F, 0F, 0F, 0F)))
                .addAnimation("agarre", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.7F, -49.449F, 77.91F, -34.315F),
                        rot(1.4F, -49.449F, 77.91F, -34.315F),
                        rot(2.1F, -49.449F, 77.91F, -34.315F),
                        rot(2.35F, -49.449F, 77.91F, -34.315F),
                        seco(2.6F, 31.305F, -10.108F, 24.52F),
                        rot(3.3F, 31.305F, -10.108F, 24.52F),
                        rot(4.2F, 0F, 0F, 0F)))
                .addAnimation("cabeza", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.7F, -24F, 0F, 0F),
                        rot(1.4F, -28F, -3F, 0F),
                        rot(2.1F, -24F, 0F, 0F),
                        rot(2.35F, -24F, 0F, 0F),
                        seco(2.6F, 10F, 0F, 0F),
                        rot(3.3F, -6F, 0F, 0F),
                        rot(4.2F, 0F, 0F, 0F)))
                .addAnimation("torso", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.7F, -6F, 0F, 0F),
                        rot(1.4F, -8F, 2F, 0F),
                        rot(2.1F, -6F, 0F, 0F),
                        rot(2.35F, -12F, 0F, 0F),
                        seco(2.6F, 12F, 0F, 0F),
                        rot(3.3F, 12F, 0F, 0F),
                        rot(4.2F, 0F, 0F, 0F)))
                .addAnimation("capa_1", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.7F, 20F, 0F, 0F),
                        rot(1.4F, 20F, 0F, 0F),
                        rot(2.1F, 20F, 0F, 0F),
                        rot(2.35F, 20F, 0F, 0F),
                        seco(2.6F, 8F, 0F, 0F),
                        rot(3.3F, 8F, 0F, 0F),
                        rot(4.2F, 0F, 0F, 0F)))
                .addAnimation("capa_2", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.7F, 10F, 0F, 0F),
                        rot(1.4F, 10F, 0F, 0F),
                        rot(2.1F, 10F, 0F, 0F),
                        rot(2.35F, 10F, 0F, 0F),
                        seco(2.6F, 24F, 0F, 0F),
                        rot(3.3F, 24F, 0F, 0F),
                        rot(4.2F, 0F, 0F, 0F)))
                .addAnimation("capa_3", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.7F, 12F, 0F, 0F),
                        rot(1.4F, 12F, 0F, 0F),
                        rot(2.1F, 12F, 0F, 0F),
                        rot(2.35F, 12F, 0F, 0F),
                        seco(2.6F, 50F, 0F, 0F),
                        rot(3.3F, 50F, 0F, 0F),
                        rot(4.2F, 0F, 0F, 0F)))
                .addAnimation("pelvis", mover(pos(0F, 0F, 0F, 0F),
                        pos(0.7F, 0F, 0F, 0F),
                        pos(1.4F, 0F, 0F, 0F),
                        pos(2.1F, 0F, 0F, 0F),
                        pos(2.35F, 0F, 6F, 0F),
                        posSeco(2.6F, 0F, -30F, 0F),
                        pos(3.3F, 0F, -30F, 0F),
                        pos(4.2F, 0F, 0F, 0F)))
                .addAnimation("tabardo", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.7F, 0F, 0F, 0F),
                        rot(1.4F, 0F, 0F, 0F),
                        rot(2.1F, 0F, 0F, 0F),
                        rot(2.35F, 0F, 0F, 0F),
                        seco(2.6F, -70F, 0F, 0F),
                        rot(3.3F, -70F, 0F, 0F),
                        rot(4.2F, 0F, 0F, 0F)))
                .addAnimation("pierna_izq", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.7F, 0F, 0F, 0F),
                        rot(1.4F, 0F, 0F, 0F),
                        rot(2.1F, 0F, 0F, 0F),
                        rot(2.35F, 0F, 0F, 0F),
                        seco(2.6F, -86F, 0F, -6F),
                        rot(3.3F, -86F, 0F, -6F),
                        rot(4.2F, 0F, 0F, 0F)))
                .addAnimation("espinilla_izq", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.7F, 0F, 0F, 0F),
                        rot(1.4F, 0F, 0F, 0F),
                        rot(2.1F, 0F, 0F, 0F),
                        rot(2.35F, 0F, 0F, 0F),
                        seco(2.6F, 86F, 0F, 0F),
                        rot(3.3F, 86F, 0F, 0F),
                        rot(4.2F, 0F, 0F, 0F)))
                .addAnimation("pierna_der", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.7F, 0F, 0F, 0F),
                        rot(1.4F, 0F, 0F, 0F),
                        rot(2.1F, 0F, 0F, 0F),
                        rot(2.35F, 0F, 0F, 0F),
                        seco(2.6F, 6F, 0F, 5F),
                        rot(3.3F, 6F, 0F, 5F),
                        rot(4.2F, 0F, 0F, 0F)))
                .addAnimation("espinilla_der", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.7F, 0F, 0F, 0F),
                        rot(1.4F, 0F, 0F, 0F),
                        rot(2.1F, 0F, 0F, 0F),
                        rot(2.35F, 0F, 0F, 0F),
                        seco(2.6F, 86F, 0F, 0F),
                        rot(3.3F, 86F, 0F, 0F),
                        rot(4.2F, 0F, 0F, 0F)))
                .addAnimation("pie_der", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.7F, 0F, 0F, 0F),
                        rot(1.4F, 0F, 0F, 0F),
                        rot(2.1F, 0F, 0F, 0F),
                        rot(2.35F, 0F, 0F, 0F),
                        seco(2.6F, -62F, 0F, 0F),
                        rot(3.3F, -62F, 0F, 0F),
                        rot(4.2F, 0F, 0F, 0F)))
                .build();
    }

    private static AnimationDefinition sol() {
        return AnimationDefinition.Builder.withLength(3.8F)
                .addAnimation("brazo_der", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.55F, 12.04F, -0.003F, 3.994F),
                        seco(1F, 4.806F, -0.003F, 0.84F),
                        rot(1.45F, 12.04F, -0.003F, 3.994F),
                        seco(2F, 4.806F, -0.003F, 0.84F),
                        rot(2.45F, 12.04F, -0.003F, 3.994F),
                        seco(3F, 4.806F, -0.003F, 0.84F),
                        rot(3.8F, 0F, 0F, 0F)))
                .addAnimation("antebrazo_der", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.55F, 1.081F, 0F, 0F),
                        seco(1F, -8.16F, 0F, 0F),
                        rot(1.45F, 1.081F, 0F, 0F),
                        seco(2F, -8.16F, 0F, 0F),
                        rot(2.45F, 1.081F, 0F, 0F),
                        seco(3F, -8.16F, 0F, 0F),
                        rot(3.8F, 0F, 0F, 0F)))
                .addAnimation("brazo_izq", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.55F, -149.242F, -0.014F, 29.061F),
                        seco(1F, -56.442F, -0.009F, 4.306F),
                        rot(1.45F, -149.242F, -0.014F, 29.061F),
                        seco(2F, -56.442F, -0.009F, 4.306F),
                        rot(2.45F, -149.242F, -0.014F, 29.061F),
                        seco(3F, -56.442F, -0.009F, 4.306F),
                        rot(3.8F, 0F, 0F, 0F)))
                .addAnimation("antebrazo_izq", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.55F, 16.724F, 0F, 0F),
                        seco(1F, 1.392F, 0F, 0F),
                        rot(1.45F, 16.724F, 0F, 0F),
                        seco(2F, 1.392F, 0F, 0F),
                        rot(2.45F, 16.724F, 0F, 0F),
                        seco(3F, 1.392F, 0F, 0F),
                        rot(3.8F, 0F, 0F, 0F)))
                .addAnimation("agarre", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.55F, -7.336F, -44.786F, 19.365F),
                        seco(1F, -10.531F, -3.398F, -4.393F),
                        rot(1.45F, -7.336F, -44.786F, 19.365F),
                        seco(2F, -10.531F, -3.398F, -4.393F),
                        rot(2.45F, -7.336F, -44.786F, 19.365F),
                        seco(3F, -10.531F, -3.398F, -4.393F),
                        rot(3.8F, 0F, 0F, 0F)))
                .addAnimation("cabeza", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.55F, -24F, 10F, 0F),
                        seco(1F, 4F, -10F, 0F),
                        rot(1.45F, -24F, 10F, 0F),
                        seco(2F, 4F, -10F, 0F),
                        rot(2.45F, -24F, 10F, 0F),
                        seco(3F, 4F, -10F, 0F),
                        rot(3.8F, 0F, 0F, 0F)))
                .addAnimation("torso", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.55F, -6F, -10F, 0F),
                        seco(1F, 10F, 18F, 0F),
                        rot(1.45F, -6F, -10F, 0F),
                        seco(2F, 10F, 18F, 0F),
                        rot(2.45F, -6F, -10F, 0F),
                        seco(3F, 10F, 18F, 0F),
                        rot(3.8F, 0F, 0F, 0F)))
                .addAnimation("pierna_izq", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.55F, -16F, 0F, -6F),
                        seco(1F, -24F, 0F, -6F),
                        rot(1.45F, -16F, 0F, -6F),
                        seco(2F, -24F, 0F, -6F),
                        rot(2.45F, -16F, 0F, -6F),
                        seco(3F, -24F, 0F, -6F),
                        rot(3.8F, 0F, 0F, 0F)))
                .addAnimation("espinilla_izq", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.55F, 18F, 0F, 0F),
                        seco(1F, 24F, 0F, 0F),
                        rot(1.45F, 18F, 0F, 0F),
                        seco(2F, 24F, 0F, 0F),
                        rot(2.45F, 18F, 0F, 0F),
                        seco(3F, 24F, 0F, 0F),
                        rot(3.8F, 0F, 0F, 0F)))
                .addAnimation("pierna_der", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.55F, 14F, 0F, 8F),
                        seco(1F, 18F, 0F, 8F),
                        rot(1.45F, 14F, 0F, 8F),
                        seco(2F, 18F, 0F, 8F),
                        rot(2.45F, 14F, 0F, 8F),
                        seco(3F, 18F, 0F, 8F),
                        rot(3.8F, 0F, 0F, 0F)))
                .addAnimation("pie_der", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.55F, -20F, 0F, 0F),
                        seco(1F, -24F, 0F, 0F),
                        rot(1.45F, -20F, 0F, 0F),
                        seco(2F, -24F, 0F, 0F),
                        rot(2.45F, -20F, 0F, 0F),
                        seco(3F, -24F, 0F, 0F),
                        rot(3.8F, 0F, 0F, 0F)))
                .addAnimation("capa_1", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.55F, 20F, 0F, 0F),
                        seco(1F, 20F, 0F, 0F),
                        rot(1.45F, 20F, 0F, 0F),
                        seco(2F, 20F, 0F, 0F),
                        rot(2.45F, 20F, 0F, 0F),
                        seco(3F, 20F, 0F, 0F),
                        rot(3.8F, 0F, 0F, 0F)))
                .addAnimation("capa_2", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.55F, 10F, 0F, 0F),
                        seco(1F, 10F, 0F, 0F),
                        rot(1.45F, 10F, 0F, 0F),
                        seco(2F, 10F, 0F, 0F),
                        rot(2.45F, 10F, 0F, 0F),
                        seco(3F, 10F, 0F, 0F),
                        rot(3.8F, 0F, 0F, 0F)))
                .addAnimation("capa_3", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.55F, 12F, 0F, 0F),
                        seco(1F, 12F, 0F, 0F),
                        rot(1.45F, 12F, 0F, 0F),
                        seco(2F, 12F, 0F, 0F),
                        rot(2.45F, 12F, 0F, 0F),
                        seco(3F, 12F, 0F, 0F),
                        rot(3.8F, 0F, 0F, 0F)))
                .build();
    }

    private static AnimationDefinition trompetas() {
        return AnimationDefinition.Builder.withLength(2.6F)
                .addAnimation("brazo_der", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.8F, -128.334F, -0.018F, 1.343F),
                        seco(1.1F, -128.334F, -0.018F, 1.343F),
                        rot(1.9F, -128.334F, -0.018F, 1.343F),
                        rot(2.6F, 0F, 0F, 0F)))
                .addAnimation("antebrazo_der", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.8F, -4.343F, 0F, 0F),
                        seco(1.1F, -4.343F, 0F, 0F),
                        rot(1.9F, -4.343F, 0F, 0F),
                        rot(2.6F, 0F, 0F, 0F)))
                .addAnimation("brazo_izq", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.8F, -12.505F, -0.007F, -33.62F),
                        seco(1.1F, -12.505F, -0.007F, -33.62F),
                        rot(1.9F, -12.505F, -0.007F, -33.62F),
                        rot(2.6F, 0F, 0F, 0F)))
                .addAnimation("antebrazo_izq", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.8F, -19.433F, 0F, 0F),
                        seco(1.1F, -19.433F, 0F, 0F),
                        rot(1.9F, -19.433F, 0F, 0F),
                        rot(2.6F, 0F, 0F, 0F)))
                .addAnimation("agarre", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.8F, 16.121F, -2.658F, 11.343F),
                        seco(1.1F, 16.121F, -2.658F, 11.343F),
                        rot(1.9F, 16.121F, -2.658F, 11.343F),
                        rot(2.6F, 0F, 0F, 0F)))
                .addAnimation("cabeza", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.8F, -22F, 0F, 0F),
                        seco(1.1F, -26F, 0F, 0F),
                        rot(1.9F, -22F, 0F, 0F),
                        rot(2.6F, 0F, 0F, 0F)))
                .addAnimation("torso", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.8F, -8F, 0F, 0F),
                        seco(1.1F, -8F, 0F, 0F),
                        rot(1.9F, -8F, 0F, 0F),
                        rot(2.6F, 0F, 0F, 0F)))
                .addAnimation("capa_1", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.8F, 20F, 0F, 0F),
                        seco(1.1F, 20F, 0F, 0F),
                        rot(1.9F, 20F, 0F, 0F),
                        rot(2.6F, 0F, 0F, 0F)))
                .addAnimation("capa_2", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.8F, 10F, 0F, 0F),
                        seco(1.1F, 10F, 0F, 0F),
                        rot(1.9F, 10F, 0F, 0F),
                        rot(2.6F, 0F, 0F, 0F)))
                .addAnimation("capa_3", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.8F, 12F, 0F, 0F),
                        seco(1.1F, 12F, 0F, 0F),
                        rot(1.9F, 12F, 0F, 0F),
                        rot(2.6F, 0F, 0F, 0F)))
                .build();
    }

    private static AnimationDefinition fuentes() {
        return AnimationDefinition.Builder.withLength(1.6F)
                .addAnimation("brazo_der", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.45F, -152.555F, -0.017F, 21.565F),
                        seco(0.8F, -37.145F, -0.008F, -35.142F),
                        rot(1.6F, -25.856F, -0.002F, -39.118F)))
                .addAnimation("antebrazo_der", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.45F, 33.519F, 0F, 0F),
                        seco(0.8F, 47.465F, 0F, 0F),
                        rot(1.6F, 26.36F, 0F, 0F)))
                .addAnimation("brazo_izq", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.45F, -139.742F, -0.015F, -27.093F),
                        seco(0.8F, -43.963F, -0.01F, 44.223F),
                        rot(1.6F, -31.01F, -0.01F, 50.545F)))
                .addAnimation("antebrazo_izq", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.45F, -16.144F, 0F, 0F),
                        seco(0.8F, 18.908F, 0F, 0F),
                        rot(1.6F, -6.36F, 0F, 0F)))
                .addAnimation("agarre", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.45F, -49.449F, 77.91F, -34.315F),
                        seco(0.8F, 31.305F, -10.108F, 24.52F),
                        rot(1.6F, -62.008F, 121.775F, -29.557F)))
                .addAnimation("cabeza", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.45F, -24F, 0F, 0F),
                        seco(0.8F, 10F, 0F, 0F),
                        rot(1.6F, -30F, 0F, 0F)))
                .addAnimation("torso", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.45F, -12F, 0F, 0F),
                        seco(0.8F, 12F, 0F, 0F),
                        rot(1.6F, 8F, 0F, 0F)))
                .addAnimation("capa_1", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.45F, 20F, 0F, 0F),
                        seco(0.8F, 8F, 0F, 0F),
                        rot(1.6F, 8F, 0F, 0F)))
                .addAnimation("capa_2", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.45F, 10F, 0F, 0F),
                        seco(0.8F, 24F, 0F, 0F),
                        rot(1.6F, 24F, 0F, 0F)))
                .addAnimation("capa_3", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.45F, 12F, 0F, 0F),
                        seco(0.8F, 50F, 0F, 0F),
                        rot(1.6F, 50F, 0F, 0F)))
                .addAnimation("pelvis", mover(pos(0F, 0F, 0F, 0F),
                        pos(0.45F, 0F, 3F, 0F),
                        posSeco(0.8F, 0F, -30F, 0F),
                        pos(1.6F, 0F, -30F, 0F)))
                .addAnimation("tabardo", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.45F, 0F, 0F, 0F),
                        seco(0.8F, -70F, 0F, 0F),
                        rot(1.6F, -70F, 0F, 0F)))
                .addAnimation("pierna_izq", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.45F, 0F, 0F, 0F),
                        seco(0.8F, -86F, 0F, -6F),
                        rot(1.6F, -86F, 0F, -6F)))
                .addAnimation("espinilla_izq", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.45F, 0F, 0F, 0F),
                        seco(0.8F, 86F, 0F, 0F),
                        rot(1.6F, 86F, 0F, 0F)))
                .addAnimation("pierna_der", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.45F, 0F, 0F, 0F),
                        seco(0.8F, 6F, 0F, 5F),
                        rot(1.6F, 6F, 0F, 5F)))
                .addAnimation("espinilla_der", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.45F, 0F, 0F, 0F),
                        seco(0.8F, 86F, 0F, 0F),
                        rot(1.6F, 86F, 0F, 0F)))
                .addAnimation("pie_der", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.45F, 0F, 0F, 0F),
                        seco(0.8F, -62F, 0F, 0F),
                        rot(1.6F, -62F, 0F, 0F)))
                .build();
    }

    private static AnimationDefinition fuentes_carga() {
        return AnimationDefinition.Builder.withLength(2F).looping()
                .addAnimation("pelvis", mover(pos(0F, 0F, -30F, 0F),
                        pos(1F, 0F, -30F, 0F),
                        pos(2F, 0F, -30F, 0F)))
                .addAnimation("tabardo", giro(rot(0F, -70F, 0F, 0F),
                        rot(1F, -70F, 0F, 0F),
                        rot(2F, -70F, 0F, 0F)))
                .addAnimation("pierna_izq", giro(rot(0F, -86F, 0F, -6F),
                        rot(1F, -86F, 0F, -6F),
                        rot(2F, -86F, 0F, -6F)))
                .addAnimation("espinilla_izq", giro(rot(0F, 86F, 0F, 0F),
                        rot(1F, 86F, 0F, 0F),
                        rot(2F, 86F, 0F, 0F)))
                .addAnimation("pierna_der", giro(rot(0F, 6F, 0F, 5F),
                        rot(1F, 6F, 0F, 5F),
                        rot(2F, 6F, 0F, 5F)))
                .addAnimation("espinilla_der", giro(rot(0F, 86F, 0F, 0F),
                        rot(1F, 86F, 0F, 0F),
                        rot(2F, 86F, 0F, 0F)))
                .addAnimation("pie_der", giro(rot(0F, -62F, 0F, 0F),
                        rot(1F, -62F, 0F, 0F),
                        rot(2F, -62F, 0F, 0F)))
                .addAnimation("capa_1", giro(rot(0F, 8F, 0F, 0F),
                        rot(1F, 8F, 0F, 0F),
                        rot(2F, 8F, 0F, 0F)))
                .addAnimation("capa_2", giro(rot(0F, 24F, 0F, 0F),
                        rot(1F, 24F, 0F, 0F),
                        rot(2F, 24F, 0F, 0F)))
                .addAnimation("capa_3", giro(rot(0F, 50F, 0F, 0F),
                        rot(1F, 50F, 0F, 0F),
                        rot(2F, 50F, 0F, 0F)))
                .addAnimation("torso", giro(rot(0F, 8F, 0F, 0F),
                        rot(1F, 4F, 2F, 0F),
                        rot(2F, 8F, 0F, 0F)))
                .addAnimation("cabeza", giro(rot(0F, -30F, 0F, 0F),
                        rot(1F, -34F, 3F, 0F),
                        rot(2F, -30F, 0F, 0F)))
                .addAnimation("brazo_der", giro(rot(0F, -25.856F, -0.002F, -39.118F),
                        rot(1F, -25.856F, -0.002F, -39.118F),
                        rot(2F, -25.856F, -0.002F, -39.118F)))
                .addAnimation("antebrazo_der", giro(rot(0F, 26.36F, 0F, 0F),
                        rot(1F, 26.36F, 0F, 0F),
                        rot(2F, 26.36F, 0F, 0F)))
                .addAnimation("brazo_izq", giro(rot(0F, -31.01F, -0.01F, 50.545F),
                        rot(1F, -31.01F, -0.01F, 50.545F),
                        rot(2F, -31.01F, -0.01F, 50.545F)))
                .addAnimation("antebrazo_izq", giro(rot(0F, -6.36F, 0F, 0F),
                        rot(1F, -6.36F, 0F, 0F),
                        rot(2F, -6.36F, 0F, 0F)))
                .addAnimation("agarre", giro(rot(0F, -62.008F, 121.775F, -29.557F),
                        rot(1F, -62.008F, 121.775F, -29.557F),
                        rot(2F, -62.008F, 121.775F, -29.557F)))
                .build();
    }

    private static AnimationDefinition ofrenda() {
        return AnimationDefinition.Builder.withLength(2.6F)
                .addAnimation("brazo_der", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.45F, -25.862F, -0.006F, 7.465F),
                        rot(0.7F, -25.862F, -0.006F, 7.465F),
                        rot(1F, -26.149F, -0.009F, -37.013F),
                        rot(1.3F, -26.149F, -0.009F, -37.013F),
                        rot(2.4F, -95.449F, 0.016F, 19.323F),
                        rot(2.6F, -95.449F, 0.016F, 19.323F)))
                .addAnimation("antebrazo_der", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.45F, 47.463F, 0F, 0F),
                        rot(0.7F, 47.463F, 0F, 0F),
                        rot(1F, -15.197F, 0F, 0F),
                        rot(1.3F, -15.197F, 0F, 0F),
                        rot(2.4F, -4.128F, 0F, 0F),
                        rot(2.6F, -4.128F, 0F, 0F)))
                .addAnimation("brazo_izq", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.45F, 17.327F, -0.005F, 1.201F),
                        rot(0.7F, 17.327F, -0.005F, 1.201F),
                        rot(1F, -51.04F, -0.014F, 38.106F),
                        rot(1.3F, -51.04F, -0.014F, 38.106F),
                        rot(2.4F, -120.329F, -0.016F, -18.208F),
                        rot(2.6F, -120.329F, -0.016F, -18.208F)))
                .addAnimation("antebrazo_izq", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.45F, -20.535F, 0F, 0F),
                        rot(0.7F, -20.535F, 0F, 0F),
                        rot(1F, -3.664F, 0F, 0F),
                        rot(1.3F, -3.664F, 0F, 0F),
                        rot(2.4F, 7.417F, 0F, 0F),
                        rot(2.6F, 7.417F, 0F, 0F)))
                .addAnimation("agarre", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.45F, 14.69F, 20.319F, -8.308F),
                        rot(0.7F, 14.69F, 20.319F, -8.308F),
                        rot(1F, 0F, 0F, 0F),
                        rot(1.3F, 0F, 0F, 0F),
                        rot(2.4F, 0F, 0F, 0F),
                        rot(2.6F, 0F, 0F, 0F)))
                .addAnimation("torso", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.45F, 14F, 10F, 0F),
                        rot(0.7F, 14F, 10F, 0F),
                        rot(1F, 24F, 0F, 0F),
                        rot(1.3F, 24F, 0F, 0F),
                        rot(2.4F, -6F, 0F, 0F),
                        rot(2.6F, -6F, 0F, 0F)))
                .addAnimation("cabeza", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.45F, 14F, 0F, 0F),
                        rot(0.7F, 14F, 0F, 0F),
                        rot(1F, 18F, 0F, 0F),
                        rot(1.3F, 18F, 0F, 0F),
                        rot(2.4F, -34F, 0F, 0F),
                        rot(2.6F, -34F, 0F, 0F)))
                .addAnimation("pelvis", mover(pos(0F, 0F, 0F, 0F),
                        pos(0.45F, 0F, -4F, 0F),
                        pos(0.7F, 0F, -4F, 0F),
                        pos(1F, 0F, -6F, 0F),
                        pos(1.3F, 0F, -6F, 0F),
                        pos(2.4F, 0F, 0F, 0F),
                        pos(2.6F, 0F, 0F, 0F)))
                .addAnimation("pierna_der", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.45F, -10F, 0F, 6F),
                        rot(0.7F, -10F, 0F, 6F),
                        rot(1F, 14F, 0F, 6F),
                        rot(1.3F, 14F, 0F, 6F),
                        rot(2.4F, 0F, 0F, 0F),
                        rot(2.6F, 0F, 0F, 0F)))
                .addAnimation("espinilla_der", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.45F, 14F, 0F, 0F),
                        rot(0.7F, 14F, 0F, 0F),
                        rot(1F, 20F, 0F, 0F),
                        rot(1.3F, 20F, 0F, 0F),
                        rot(2.4F, 0F, 0F, 0F),
                        rot(2.6F, 0F, 0F, 0F)))
                .addAnimation("pierna_izq", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.45F, 0F, 0F, 0F),
                        rot(0.7F, 0F, 0F, 0F),
                        rot(1F, -20F, 0F, -6F),
                        rot(1.3F, -20F, 0F, -6F),
                        rot(2.4F, 0F, 0F, 0F),
                        rot(2.6F, 0F, 0F, 0F)))
                .addAnimation("espinilla_izq", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.45F, 0F, 0F, 0F),
                        rot(0.7F, 0F, 0F, 0F),
                        rot(1F, 30F, 0F, 0F),
                        rot(1.3F, 30F, 0F, 0F),
                        rot(2.4F, 0F, 0F, 0F),
                        rot(2.6F, 0F, 0F, 0F)))
                .addAnimation("capa_1", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.45F, 0F, 0F, 0F),
                        rot(0.7F, 0F, 0F, 0F),
                        rot(1F, 0F, 0F, 0F),
                        rot(1.3F, 0F, 0F, 0F),
                        rot(2.4F, 20F, 0F, 0F),
                        rot(2.6F, 20F, 0F, 0F)))
                .addAnimation("capa_2", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.45F, 0F, 0F, 0F),
                        rot(0.7F, 0F, 0F, 0F),
                        rot(1F, 0F, 0F, 0F),
                        rot(1.3F, 0F, 0F, 0F),
                        rot(2.4F, 10F, 0F, 0F),
                        rot(2.6F, 10F, 0F, 0F)))
                .addAnimation("capa_3", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.45F, 0F, 0F, 0F),
                        rot(0.7F, 0F, 0F, 0F),
                        rot(1F, 0F, 0F, 0F),
                        rot(1.3F, 0F, 0F, 0F),
                        rot(2.4F, 12F, 0F, 0F),
                        rot(2.6F, 12F, 0F, 0F)))
                .build();
    }

    private static AnimationDefinition ofrenda_sostiene() {
        return AnimationDefinition.Builder.withLength(2F).looping()
                .addAnimation("cabeza", giro(rot(0F, -34F, 0F, 0F),
                        rot(1F, -37F, 0F, 0F),
                        rot(2F, -34F, 0F, 0F)))
                .addAnimation("torso", giro(rot(0F, -6F, 0F, 0F),
                        rot(1F, -8F, 2F, 0F),
                        rot(2F, -6F, 0F, 0F)))
                .addAnimation("capa_1", giro(rot(0F, 20F, 0F, 0F),
                        rot(1F, 20F, 0F, 0F),
                        rot(2F, 20F, 0F, 0F)))
                .addAnimation("capa_2", giro(rot(0F, 10F, 0F, 0F),
                        rot(1F, 10F, 0F, 0F),
                        rot(2F, 10F, 0F, 0F)))
                .addAnimation("capa_3", giro(rot(0F, 12F, 0F, 0F),
                        rot(1F, 12F, 0F, 0F),
                        rot(2F, 12F, 0F, 0F)))
                .addAnimation("brazo_der", giro(rot(0F, -95.449F, 0.016F, 19.323F),
                        rot(1F, -95.449F, 0.016F, 19.323F),
                        rot(2F, -95.449F, 0.016F, 19.323F)))
                .addAnimation("antebrazo_der", giro(rot(0F, -4.128F, 0F, 0F),
                        rot(1F, -4.128F, 0F, 0F),
                        rot(2F, -4.128F, 0F, 0F)))
                .addAnimation("brazo_izq", giro(rot(0F, -120.329F, -0.016F, -18.208F),
                        rot(1F, -120.329F, -0.016F, -18.208F),
                        rot(2F, -120.329F, -0.016F, -18.208F)))
                .addAnimation("antebrazo_izq", giro(rot(0F, 7.417F, 0F, 0F),
                        rot(1F, 7.417F, 0F, 0F),
                        rot(2F, 7.417F, 0F, 0F)))
                .build();
    }

    private static AnimationDefinition dios() {
        return AnimationDefinition.Builder.withLength(5F)
                .addAnimation("brazo_der", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.4F, -25.862F, -0.006F, 7.465F),
                        rot(0.6F, -25.862F, -0.006F, 7.465F),
                        rot(1F, -119.096F, -0.007F, -43.252F),
                        seco(1.6F, -26.4F, -0.015F, 48.505F),
                        rot(2.1F, -119.096F, -0.007F, -43.252F),
                        seco(2.6F, -26.4F, -0.015F, 48.505F),
                        rot(3.1F, -119.096F, -0.007F, -43.252F),
                        seco(3.6F, -26.4F, -0.015F, 48.505F),
                        rot(4.1F, -119.096F, -0.007F, -43.252F),
                        rot(4.5F, -25.862F, -0.006F, 7.465F),
                        rot(5F, 0F, 0F, 0F)))
                .addAnimation("antebrazo_der", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.4F, 47.463F, 0F, 0F),
                        rot(0.6F, 47.463F, 0F, 0F),
                        rot(1F, -12.323F, 0F, 0F),
                        seco(1.6F, -34.515F, 0F, 0F),
                        rot(2.1F, -12.323F, 0F, 0F),
                        seco(2.6F, -34.515F, 0F, 0F),
                        rot(3.1F, -12.323F, 0F, 0F),
                        seco(3.6F, -34.515F, 0F, 0F),
                        rot(4.1F, -12.323F, 0F, 0F),
                        rot(4.5F, 47.463F, 0F, 0F),
                        rot(5F, 0F, 0F, 0F)))
                .addAnimation("brazo_izq", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.4F, 17.327F, -0.005F, 1.201F),
                        rot(0.6F, 17.327F, -0.005F, 1.201F),
                        rot(1F, -143.96F, -0.062F, 44.314F),
                        seco(1.6F, -51.273F, -0.014F, -47.386F),
                        rot(2.1F, -143.96F, -0.062F, 44.314F),
                        seco(2.6F, -51.273F, -0.014F, -47.386F),
                        rot(3.1F, -143.96F, -0.062F, 44.314F),
                        seco(3.6F, -51.273F, -0.014F, -47.386F),
                        rot(4.1F, -143.96F, -0.062F, 44.314F),
                        rot(4.5F, 17.327F, -0.005F, 1.201F),
                        rot(5F, 0F, 0F, 0F)))
                .addAnimation("antebrazo_izq", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.4F, -20.535F, 0F, 0F),
                        rot(0.6F, -20.535F, 0F, 0F),
                        rot(1F, -0.822F, 0F, 0F),
                        seco(1.6F, -23.008F, 0F, 0F),
                        rot(2.1F, -0.822F, 0F, 0F),
                        seco(2.6F, -23.008F, 0F, 0F),
                        rot(3.1F, -0.822F, 0F, 0F),
                        seco(3.6F, -23.008F, 0F, 0F),
                        rot(4.1F, -0.822F, 0F, 0F),
                        rot(4.5F, -20.535F, 0F, 0F),
                        rot(5F, 0F, 0F, 0F)))
                .addAnimation("agarre", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.4F, 14.69F, 20.319F, -8.308F),
                        rot(0.6F, 14.69F, 20.319F, -8.308F),
                        rot(1F, 0F, 0F, 0F),
                        seco(1.6F, 0F, 0F, 0F),
                        rot(2.1F, 0F, 0F, 0F),
                        seco(2.6F, 0F, 0F, 0F),
                        rot(3.1F, 0F, 0F, 0F),
                        seco(3.6F, 0F, 0F, 0F),
                        rot(4.1F, 0F, 0F, 0F),
                        rot(4.5F, 14.69F, 20.319F, -8.308F),
                        rot(5F, 0F, 0F, 0F)))
                .addAnimation("torso", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.4F, 14F, 10F, 0F),
                        rot(0.6F, 14F, 10F, 0F),
                        rot(1F, -8F, 0F, 0F),
                        seco(1.6F, 14F, 0F, 0F),
                        rot(2.1F, -8F, 0F, 0F),
                        seco(2.6F, 14F, 0F, 0F),
                        rot(3.1F, -8F, 0F, 0F),
                        seco(3.6F, 14F, 0F, 0F),
                        rot(4.1F, -8F, 0F, 0F),
                        rot(4.5F, 14F, 10F, 0F),
                        rot(5F, 0F, 0F, 0F)))
                .addAnimation("cabeza", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.4F, 14F, 0F, 0F),
                        rot(0.6F, 14F, 0F, 0F),
                        rot(1F, -16F, 0F, 0F),
                        seco(1.6F, 4F, 0F, 0F),
                        rot(2.1F, -16F, 0F, 0F),
                        seco(2.6F, 4F, 0F, 0F),
                        rot(3.1F, -16F, 0F, 0F),
                        seco(3.6F, 4F, 0F, 0F),
                        rot(4.1F, -16F, 0F, 0F),
                        rot(4.5F, 14F, 0F, 0F),
                        rot(5F, 0F, 0F, 0F)))
                .addAnimation("pelvis", mover(pos(0F, 0F, 0F, 0F),
                        pos(0.4F, 0F, -4F, 0F),
                        pos(0.6F, 0F, -4F, 0F),
                        pos(1F, 0F, 0F, 0F),
                        posSeco(1.6F, 0F, 0F, 0F),
                        pos(2.1F, 0F, 0F, 0F),
                        posSeco(2.6F, 0F, 0F, 0F),
                        pos(3.1F, 0F, 0F, 0F),
                        posSeco(3.6F, 0F, 0F, 0F),
                        pos(4.1F, 0F, 0F, 0F),
                        pos(4.5F, 0F, -4F, 0F),
                        pos(5F, 0F, 0F, 0F)))
                .addAnimation("pierna_der", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.4F, -10F, 0F, 6F),
                        rot(0.6F, -10F, 0F, 6F),
                        rot(1F, 14F, 0F, 8F),
                        seco(1.6F, 18F, 0F, 8F),
                        rot(2.1F, 14F, 0F, 8F),
                        seco(2.6F, 18F, 0F, 8F),
                        rot(3.1F, 14F, 0F, 8F),
                        seco(3.6F, 18F, 0F, 8F),
                        rot(4.1F, 14F, 0F, 8F),
                        rot(4.5F, -10F, 0F, 6F),
                        rot(5F, 0F, 0F, 0F)))
                .addAnimation("espinilla_der", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.4F, 14F, 0F, 0F),
                        rot(0.6F, 14F, 0F, 0F),
                        rot(1F, 0F, 0F, 0F),
                        seco(1.6F, 0F, 0F, 0F),
                        rot(2.1F, 0F, 0F, 0F),
                        seco(2.6F, 0F, 0F, 0F),
                        rot(3.1F, 0F, 0F, 0F),
                        seco(3.6F, 0F, 0F, 0F),
                        rot(4.1F, 0F, 0F, 0F),
                        rot(4.5F, 14F, 0F, 0F),
                        rot(5F, 0F, 0F, 0F)))
                .addAnimation("pierna_izq", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.4F, 0F, 0F, 0F),
                        rot(0.6F, 0F, 0F, 0F),
                        rot(1F, -16F, 0F, -8F),
                        seco(1.6F, -22F, 0F, -8F),
                        rot(2.1F, -16F, 0F, -8F),
                        seco(2.6F, -22F, 0F, -8F),
                        rot(3.1F, -16F, 0F, -8F),
                        seco(3.6F, -22F, 0F, -8F),
                        rot(4.1F, -16F, 0F, -8F),
                        rot(4.5F, 0F, 0F, 0F),
                        rot(5F, 0F, 0F, 0F)))
                .addAnimation("espinilla_izq", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.4F, 0F, 0F, 0F),
                        rot(0.6F, 0F, 0F, 0F),
                        rot(1F, 18F, 0F, 0F),
                        seco(1.6F, 24F, 0F, 0F),
                        rot(2.1F, 18F, 0F, 0F),
                        seco(2.6F, 24F, 0F, 0F),
                        rot(3.1F, 18F, 0F, 0F),
                        seco(3.6F, 24F, 0F, 0F),
                        rot(4.1F, 18F, 0F, 0F),
                        rot(4.5F, 0F, 0F, 0F),
                        rot(5F, 0F, 0F, 0F)))
                .addAnimation("pie_der", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.4F, 0F, 0F, 0F),
                        rot(0.6F, 0F, 0F, 0F),
                        rot(1F, -18F, 0F, 0F),
                        seco(1.6F, -22F, 0F, 0F),
                        rot(2.1F, -18F, 0F, 0F),
                        seco(2.6F, -22F, 0F, 0F),
                        rot(3.1F, -18F, 0F, 0F),
                        seco(3.6F, -22F, 0F, 0F),
                        rot(4.1F, -18F, 0F, 0F),
                        rot(4.5F, 0F, 0F, 0F),
                        rot(5F, 0F, 0F, 0F)))
                .addAnimation("capa_1", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.4F, 0F, 0F, 0F),
                        rot(0.6F, 0F, 0F, 0F),
                        rot(1F, 20F, 0F, 0F),
                        seco(1.6F, 20F, 0F, 0F),
                        rot(2.1F, 20F, 0F, 0F),
                        seco(2.6F, 20F, 0F, 0F),
                        rot(3.1F, 20F, 0F, 0F),
                        seco(3.6F, 20F, 0F, 0F),
                        rot(4.1F, 20F, 0F, 0F),
                        rot(4.5F, 0F, 0F, 0F),
                        rot(5F, 0F, 0F, 0F)))
                .addAnimation("capa_2", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.4F, 0F, 0F, 0F),
                        rot(0.6F, 0F, 0F, 0F),
                        rot(1F, 10F, 0F, 0F),
                        seco(1.6F, 10F, 0F, 0F),
                        rot(2.1F, 10F, 0F, 0F),
                        seco(2.6F, 10F, 0F, 0F),
                        rot(3.1F, 10F, 0F, 0F),
                        seco(3.6F, 10F, 0F, 0F),
                        rot(4.1F, 10F, 0F, 0F),
                        rot(4.5F, 0F, 0F, 0F),
                        rot(5F, 0F, 0F, 0F)))
                .addAnimation("capa_3", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.4F, 0F, 0F, 0F),
                        rot(0.6F, 0F, 0F, 0F),
                        rot(1F, 12F, 0F, 0F),
                        seco(1.6F, 12F, 0F, 0F),
                        rot(2.1F, 12F, 0F, 0F),
                        seco(2.6F, 12F, 0F, 0F),
                        rot(3.1F, 12F, 0F, 0F),
                        seco(3.6F, 12F, 0F, 0F),
                        rot(4.1F, 12F, 0F, 0F),
                        rot(4.5F, 0F, 0F, 0F),
                        rot(5F, 0F, 0F, 0F)))
                .build();
    }

    private static AnimationDefinition grito() {
        return AnimationDefinition.Builder.withLength(2.4F)
                .addAnimation("brazo_der", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.5F, 21.094F, -0.008F, -14.618F),
                        seco(0.9F, 9.304F, -0.009F, 21.179F),
                        rot(1.9F, 9.304F, -0.009F, 21.179F),
                        rot(2.4F, 0F, 0F, 0F)))
                .addAnimation("antebrazo_der", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.5F, -65.895F, 0F, 0F),
                        seco(0.9F, -2.939F, 0F, 0F),
                        rot(1.9F, -2.939F, 0F, 0F),
                        rot(2.4F, 0F, 0F, 0F)))
                .addAnimation("brazo_izq", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.5F, -3.794F, -0.005F, 15.69F),
                        seco(0.9F, -15.581F, 0.007F, -20.098F),
                        rot(1.9F, -15.581F, 0.007F, -20.098F),
                        rot(2.4F, 0F, 0F, 0F)))
                .addAnimation("antebrazo_izq", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.5F, -54.381F, 0F, 0F),
                        seco(0.9F, 8.586F, 0F, 0F),
                        rot(1.9F, 8.586F, 0F, 0F),
                        rot(2.4F, 0F, 0F, 0F)))
                .addAnimation("agarre", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.5F, -41.437F, 102.664F, -26.053F),
                        seco(0.9F, -1.107F, 13.903F, 7.53F),
                        rot(1.9F, -1.107F, 13.903F, 7.53F),
                        rot(2.4F, 0F, 0F, 0F)))
                .addAnimation("torso", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.5F, 18F, 0F, 0F),
                        seco(0.9F, -10F, 0F, 0F),
                        rot(1.9F, -10F, 0F, 0F),
                        rot(2.4F, 0F, 0F, 0F)))
                .addAnimation("cabeza", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.5F, 14F, 0F, 0F),
                        seco(0.9F, -26F, 0F, 0F),
                        rot(1.9F, -30F, 3F, 0F),
                        rot(2.4F, 0F, 0F, 0F)))
                .addAnimation("pelvis", mover(pos(0F, 0F, 0F, 0F),
                        pos(0.5F, 0F, -4F, 0F),
                        posSeco(0.9F, 0F, -1F, 0F),
                        pos(1.9F, 0F, -1F, 0F),
                        pos(2.4F, 0F, 0F, 0F)))
                .addAnimation("pierna_izq", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.5F, 0F, 0F, 0F),
                        seco(0.9F, -14F, 0F, -8F),
                        rot(1.9F, -14F, 0F, -8F),
                        rot(2.4F, 0F, 0F, 0F)))
                .addAnimation("espinilla_izq", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.5F, 0F, 0F, 0F),
                        seco(0.9F, 16F, 0F, 0F),
                        rot(1.9F, 16F, 0F, 0F),
                        rot(2.4F, 0F, 0F, 0F)))
                .addAnimation("pierna_der", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.5F, 0F, 0F, 0F),
                        seco(0.9F, 12F, 0F, 8F),
                        rot(1.9F, 12F, 0F, 8F),
                        rot(2.4F, 0F, 0F, 0F)))
                .addAnimation("pie_der", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.5F, 0F, 0F, 0F),
                        seco(0.9F, -14F, 0F, 0F),
                        rot(1.9F, -14F, 0F, 0F),
                        rot(2.4F, 0F, 0F, 0F)))
                .addAnimation("capa_1", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.5F, 0F, 0F, 0F),
                        seco(0.9F, 20F, 0F, 0F),
                        rot(1.9F, 20F, 0F, 0F),
                        rot(2.4F, 0F, 0F, 0F)))
                .addAnimation("capa_2", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.5F, 0F, 0F, 0F),
                        seco(0.9F, 10F, 0F, 0F),
                        rot(1.9F, 10F, 0F, 0F),
                        rot(2.4F, 0F, 0F, 0F)))
                .addAnimation("capa_3", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.5F, 0F, 0F, 0F),
                        seco(0.9F, 12F, 0F, 0F),
                        rot(1.9F, 12F, 0F, 0F),
                        rot(2.4F, 0F, 0F, 0F)))
                .build();
    }

    private static AnimationDefinition aturdido() {
        return AnimationDefinition.Builder.withLength(1.2F)
                .addAnimation("brazo_der", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.3F, 0F, 0F, 0F),
                        rot(1.2F, -29.453F, -0.008F, -36.878F)))
                .addAnimation("antebrazo_der", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.3F, 0F, 0F, 0F),
                        rot(1.2F, 28.995F, 0F, 0F)))
                .addAnimation("brazo_izq", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.3F, 0F, 0F, 0F),
                        rot(1.2F, -2.489F, -0.01F, -1.853F)))
                .addAnimation("antebrazo_izq", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.3F, 0F, 0F, 0F),
                        rot(1.2F, -38.04F, 0F, 0F)))
                .addAnimation("agarre", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.3F, 0F, 0F, 0F),
                        rot(1.2F, -47.874F, 108.739F, -27.738F)))
                .addAnimation("torso", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.3F, -14F, 0F, 0F),
                        rot(1.2F, 26F, 8F, 0F)))
                .addAnimation("cabeza", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.3F, -18F, 0F, 0F),
                        rot(1.2F, 30F, 12F, 0F)))
                .addAnimation("pelvis", mover(pos(0F, 0F, 0F, 0F),
                        pos(0.3F, 0F, 0F, 0F),
                        pos(1.2F, 0F, -30F, 0F)))
                .addAnimation("tabardo", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.3F, 0F, 0F, 0F),
                        rot(1.2F, -70F, 0F, 0F)))
                .addAnimation("pierna_izq", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.3F, 0F, 0F, 0F),
                        rot(1.2F, -86F, 0F, -6F)))
                .addAnimation("espinilla_izq", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.3F, 0F, 0F, 0F),
                        rot(1.2F, 86F, 0F, 0F)))
                .addAnimation("pierna_der", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.3F, 0F, 0F, 0F),
                        rot(1.2F, 6F, 0F, 5F)))
                .addAnimation("espinilla_der", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.3F, 0F, 0F, 0F),
                        rot(1.2F, 86F, 0F, 0F)))
                .addAnimation("pie_der", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.3F, 0F, 0F, 0F),
                        rot(1.2F, -62F, 0F, 0F)))
                .addAnimation("capa_1", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.3F, 0F, 0F, 0F),
                        rot(1.2F, 8F, 0F, 0F)))
                .addAnimation("capa_2", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.3F, 0F, 0F, 0F),
                        rot(1.2F, 24F, 0F, 0F)))
                .addAnimation("capa_3", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.3F, 0F, 0F, 0F),
                        rot(1.2F, 50F, 0F, 0F)))
                .build();
    }

    private static AnimationDefinition aturdido_bucle() {
        return AnimationDefinition.Builder.withLength(2.4F).looping()
                .addAnimation("pelvis", mover(pos(0F, 0F, -30F, 0F),
                        pos(1.2F, 0F, -30F, 0F),
                        pos(2.4F, 0F, -30F, 0F)))
                .addAnimation("tabardo", giro(rot(0F, -70F, 0F, 0F),
                        rot(1.2F, -70F, 0F, 0F),
                        rot(2.4F, -70F, 0F, 0F)))
                .addAnimation("pierna_izq", giro(rot(0F, -86F, 0F, -6F),
                        rot(1.2F, -86F, 0F, -6F),
                        rot(2.4F, -86F, 0F, -6F)))
                .addAnimation("espinilla_izq", giro(rot(0F, 86F, 0F, 0F),
                        rot(1.2F, 86F, 0F, 0F),
                        rot(2.4F, 86F, 0F, 0F)))
                .addAnimation("pierna_der", giro(rot(0F, 6F, 0F, 5F),
                        rot(1.2F, 6F, 0F, 5F),
                        rot(2.4F, 6F, 0F, 5F)))
                .addAnimation("espinilla_der", giro(rot(0F, 86F, 0F, 0F),
                        rot(1.2F, 86F, 0F, 0F),
                        rot(2.4F, 86F, 0F, 0F)))
                .addAnimation("pie_der", giro(rot(0F, -62F, 0F, 0F),
                        rot(1.2F, -62F, 0F, 0F),
                        rot(2.4F, -62F, 0F, 0F)))
                .addAnimation("capa_1", giro(rot(0F, 8F, 0F, 0F),
                        rot(1.2F, 8F, 0F, 0F),
                        rot(2.4F, 8F, 0F, 0F)))
                .addAnimation("capa_2", giro(rot(0F, 24F, 0F, 0F),
                        rot(1.2F, 24F, 0F, 0F),
                        rot(2.4F, 24F, 0F, 0F)))
                .addAnimation("capa_3", giro(rot(0F, 50F, 0F, 0F),
                        rot(1.2F, 50F, 0F, 0F),
                        rot(2.4F, 50F, 0F, 0F)))
                .addAnimation("torso", giro(rot(0F, 26F, 8F, 0F),
                        rot(1.2F, 30F, -6F, 0F),
                        rot(2.4F, 26F, 8F, 0F)))
                .addAnimation("cabeza", giro(rot(0F, 30F, 12F, 0F),
                        rot(1.2F, 36F, -14F, 0F),
                        rot(2.4F, 30F, 12F, 0F)))
                .addAnimation("brazo_der", giro(rot(0F, -29.453F, -0.008F, -36.878F),
                        rot(1.2F, -29.453F, -0.008F, -36.878F),
                        rot(2.4F, -29.453F, -0.008F, -36.878F)))
                .addAnimation("antebrazo_der", giro(rot(0F, 28.995F, 0F, 0F),
                        rot(1.2F, 28.995F, 0F, 0F),
                        rot(2.4F, 28.995F, 0F, 0F)))
                .addAnimation("brazo_izq", giro(rot(0F, -2.489F, -0.01F, -1.853F),
                        rot(1.2F, -2.489F, -0.01F, -1.853F),
                        rot(2.4F, -2.489F, -0.01F, -1.853F)))
                .addAnimation("antebrazo_izq", giro(rot(0F, -38.04F, 0F, 0F),
                        rot(1.2F, -38.04F, 0F, 0F),
                        rot(2.4F, -38.04F, 0F, 0F)))
                .addAnimation("agarre", giro(rot(0F, -47.874F, 108.739F, -27.738F),
                        rot(1.2F, -47.874F, 108.739F, -27.738F),
                        rot(2.4F, -47.874F, 108.739F, -27.738F)))
                .build();
    }

    private static AnimationDefinition tambaleo() {
        return AnimationDefinition.Builder.withLength(3F)
                .addAnimation("brazo_der", giro(rot(0F, 0F, 0F, 0F),
                        seco(0.15F, 67.87F, 0.004F, 10.314F),
                        rot(0.7F, 67.87F, 0.004F, 10.314F),
                        rot(1.3F, -20.745F, -0.007F, -7.405F),
                        rot(2.1F, 9.304F, -0.009F, 21.179F),
                        rot(2.5F, 9.304F, -0.009F, 21.179F),
                        rot(3F, 0F, 0F, 0F)))
                .addAnimation("antebrazo_der", giro(rot(0F, 0F, 0F, 0F),
                        seco(0.15F, -55.13F, 0F, 0F),
                        rot(0.7F, -55.13F, 0F, 0F),
                        rot(1.3F, 7.874F, 0F, 0F),
                        rot(2.1F, -2.939F, 0F, 0F),
                        rot(2.5F, -2.939F, 0F, 0F),
                        rot(3F, 0F, 0F, 0F)))
                .addAnimation("brazo_izq", giro(rot(0F, 0F, 0F, 0F),
                        seco(0.15F, -107.686F, -0.02F, -219.297F),
                        rot(0.7F, -107.686F, -0.02F, -219.297F),
                        rot(1.3F, -27.552F, -0.006F, 15.668F),
                        rot(2.1F, -15.581F, 0.007F, -20.098F),
                        rot(2.5F, -15.581F, 0.007F, -20.098F),
                        rot(3F, 0F, 0F, 0F)))
                .addAnimation("antebrazo_izq", giro(rot(0F, 0F, 0F, 0F),
                        seco(0.15F, -67.395F, 0F, 0F),
                        rot(0.7F, -67.395F, 0F, 0F),
                        rot(1.3F, -5.5F, 0F, 0F),
                        rot(2.1F, 8.586F, 0F, 0F),
                        rot(2.5F, 8.586F, 0F, 0F),
                        rot(3F, 0F, 0F, 0F)))
                .addAnimation("agarre", giro(rot(0F, 0F, 0F, 0F),
                        seco(0.15F, -251.814F, -13.061F, -34.601F),
                        rot(0.7F, -251.814F, -13.061F, -34.601F),
                        rot(1.3F, 48.022F, -3.399F, -4.393F),
                        rot(2.1F, -1.107F, 13.903F, 7.53F),
                        rot(2.5F, -1.107F, 13.903F, 7.53F),
                        rot(3F, 0F, 0F, 0F)))
                .addAnimation("torso", giro(rot(0F, 0F, 0F, 0F),
                        seco(0.15F, -16F, -6F, 0F),
                        rot(0.7F, -16F, -6F, 0F),
                        rot(1.3F, 26F, 0F, 0F),
                        rot(2.1F, -10F, 0F, 0F),
                        rot(2.5F, -10F, 0F, 0F),
                        rot(3F, 0F, 0F, 0F)))
                .addAnimation("cabeza", giro(rot(0F, 0F, 0F, 0F),
                        seco(0.15F, -20F, 0F, 0F),
                        rot(0.7F, -20F, 0F, 0F),
                        rot(1.3F, 20F, 0F, 0F),
                        rot(2.1F, -26F, 0F, 0F),
                        rot(2.5F, -30F, 0F, 0F),
                        rot(3F, 0F, 0F, 0F)))
                .addAnimation("pelvis", mover(pos(0F, 0F, 0F, 0F),
                        posSeco(0.15F, 0F, -3F, 4F),
                        pos(0.7F, 0F, -3F, 4F),
                        pos(1.3F, 0F, -8F, 0F),
                        pos(2.1F, 0F, -1F, 0F),
                        pos(2.5F, 0F, -1F, 0F),
                        pos(3F, 0F, 0F, 0F)))
                .addAnimation("pierna_der", giro(rot(0F, 0F, 0F, 0F),
                        seco(0.15F, 24F, 0F, 8F),
                        rot(0.7F, 24F, 0F, 8F),
                        rot(1.3F, 10F, 0F, 0F),
                        rot(2.1F, 12F, 0F, 8F),
                        rot(2.5F, 12F, 0F, 8F),
                        rot(3F, 0F, 0F, 0F)))
                .addAnimation("espinilla_der", giro(rot(0F, 0F, 0F, 0F),
                        seco(0.15F, 30F, 0F, 0F),
                        rot(0.7F, 30F, 0F, 0F),
                        rot(1.3F, 36F, 0F, 0F),
                        rot(2.1F, 0F, 0F, 0F),
                        rot(2.5F, 0F, 0F, 0F),
                        rot(3F, 0F, 0F, 0F)))
                .addAnimation("pierna_izq", giro(rot(0F, 0F, 0F, 0F),
                        seco(0.15F, -6F, 0F, 0F),
                        rot(0.7F, -6F, 0F, 0F),
                        rot(1.3F, -24F, 0F, 0F),
                        rot(2.1F, -14F, 0F, -8F),
                        rot(2.5F, -14F, 0F, -8F),
                        rot(3F, 0F, 0F, 0F)))
                .addAnimation("espinilla_izq", giro(rot(0F, 0F, 0F, 0F),
                        seco(0.15F, 0F, 0F, 0F),
                        rot(0.7F, 0F, 0F, 0F),
                        rot(1.3F, 40F, 0F, 0F),
                        rot(2.1F, 16F, 0F, 0F),
                        rot(2.5F, 16F, 0F, 0F),
                        rot(3F, 0F, 0F, 0F)))
                .addAnimation("pie_der", giro(rot(0F, 0F, 0F, 0F),
                        seco(0.15F, 0F, 0F, 0F),
                        rot(0.7F, 0F, 0F, 0F),
                        rot(1.3F, 0F, 0F, 0F),
                        rot(2.1F, -14F, 0F, 0F),
                        rot(2.5F, -14F, 0F, 0F),
                        rot(3F, 0F, 0F, 0F)))
                .addAnimation("capa_1", giro(rot(0F, 0F, 0F, 0F),
                        seco(0.15F, 0F, 0F, 0F),
                        rot(0.7F, 0F, 0F, 0F),
                        rot(1.3F, 0F, 0F, 0F),
                        rot(2.1F, 20F, 0F, 0F),
                        rot(2.5F, 20F, 0F, 0F),
                        rot(3F, 0F, 0F, 0F)))
                .addAnimation("capa_2", giro(rot(0F, 0F, 0F, 0F),
                        seco(0.15F, 0F, 0F, 0F),
                        rot(0.7F, 0F, 0F, 0F),
                        rot(1.3F, 0F, 0F, 0F),
                        rot(2.1F, 10F, 0F, 0F),
                        rot(2.5F, 10F, 0F, 0F),
                        rot(3F, 0F, 0F, 0F)))
                .addAnimation("capa_3", giro(rot(0F, 0F, 0F, 0F),
                        seco(0.15F, 0F, 0F, 0F),
                        rot(0.7F, 0F, 0F, 0F),
                        rot(1.3F, 0F, 0F, 0F),
                        rot(2.1F, 12F, 0F, 0F),
                        rot(2.5F, 12F, 0F, 0F),
                        rot(3F, 0F, 0F, 0F)))
                .build();
    }

    private static AnimationDefinition liberacion() {
        return AnimationDefinition.Builder.withLength(10F)
                .addAnimation("brazo_der", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.6F, 67.87F, 0.004F, 10.314F),
                        rot(1.6F, -37.145F, -0.008F, -35.142F),
                        rot(3.5F, -25.856F, -0.002F, -39.118F),
                        rot(6F, -22.601F, -0.002F, -38.166F),
                        rot(10F, -22.601F, -0.002F, -38.166F)))
                .addAnimation("antebrazo_der", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.6F, -55.13F, 0F, 0F),
                        rot(1.6F, 47.465F, 0F, 0F),
                        rot(3.5F, 26.36F, 0F, 0F),
                        rot(6F, 24.491F, 0F, 0F),
                        rot(10F, 24.491F, 0F, 0F)))
                .addAnimation("brazo_izq", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.6F, -107.686F, -0.02F, -219.297F),
                        rot(1.6F, -43.963F, -0.01F, 44.223F),
                        rot(3.5F, -31.01F, -0.01F, 50.545F),
                        rot(6F, -176.633F, -0.036F, 18.184F),
                        rot(10F, -176.633F, -0.036F, 18.184F)))
                .addAnimation("antebrazo_izq", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.6F, -67.395F, 0F, 0F),
                        rot(1.6F, 18.908F, 0F, 0F),
                        rot(3.5F, -6.36F, 0F, 0F),
                        rot(6F, 45.413F, 0F, 0F),
                        rot(10F, 45.413F, 0F, 0F)))
                .addAnimation("agarre", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.6F, -251.814F, -13.061F, -34.601F),
                        rot(1.6F, 31.305F, -10.108F, 24.52F),
                        rot(3.5F, -62.008F, 121.775F, -29.557F),
                        rot(6F, 48.949F, -24.301F, 21.177F),
                        rot(10F, 48.949F, -24.301F, 21.177F)))
                .addAnimation("torso", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.6F, -16F, -6F, 0F),
                        rot(1.6F, 12F, 0F, 0F),
                        rot(3.5F, 8F, 0F, 0F),
                        rot(6F, 2F, 0F, 0F),
                        rot(10F, 2F, 0F, 0F)))
                .addAnimation("cabeza", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.6F, -20F, 0F, 0F),
                        rot(1.6F, 10F, 0F, 0F),
                        rot(3.5F, -36F, 0F, 0F),
                        rot(6F, -38F, 0F, 0F),
                        rot(10F, -38F, 0F, 0F)))
                .addAnimation("pelvis", mover(pos(0F, 0F, 0F, 0F),
                        pos(0.6F, 0F, -3F, 4F),
                        pos(1.6F, 0F, -30F, 0F),
                        pos(3.5F, 0F, -30F, 0F),
                        pos(6F, 0F, -30F, 0F),
                        pos(10F, 0F, -30F, 0F)))
                .addAnimation("pierna_der", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.6F, 24F, 0F, 8F),
                        rot(1.6F, 6F, 0F, 5F),
                        rot(3.5F, 6F, 0F, 5F),
                        rot(6F, 6F, 0F, 5F),
                        rot(10F, 6F, 0F, 5F)))
                .addAnimation("espinilla_der", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.6F, 30F, 0F, 0F),
                        rot(1.6F, 86F, 0F, 0F),
                        rot(3.5F, 86F, 0F, 0F),
                        rot(6F, 86F, 0F, 0F),
                        rot(10F, 86F, 0F, 0F)))
                .addAnimation("pierna_izq", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.6F, -6F, 0F, 0F),
                        rot(1.6F, -86F, 0F, -6F),
                        rot(3.5F, -86F, 0F, -6F),
                        rot(6F, -86F, 0F, -6F),
                        rot(10F, -86F, 0F, -6F)))
                .addAnimation("tabardo", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.6F, 0F, 0F, 0F),
                        rot(1.6F, -70F, 0F, 0F),
                        rot(3.5F, -70F, 0F, 0F),
                        rot(6F, -70F, 0F, 0F),
                        rot(10F, -70F, 0F, 0F)))
                .addAnimation("espinilla_izq", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.6F, 0F, 0F, 0F),
                        rot(1.6F, 86F, 0F, 0F),
                        rot(3.5F, 86F, 0F, 0F),
                        rot(6F, 86F, 0F, 0F),
                        rot(10F, 86F, 0F, 0F)))
                .addAnimation("pie_der", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.6F, 0F, 0F, 0F),
                        rot(1.6F, -62F, 0F, 0F),
                        rot(3.5F, -62F, 0F, 0F),
                        rot(6F, -62F, 0F, 0F),
                        rot(10F, -62F, 0F, 0F)))
                .addAnimation("capa_1", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.6F, 0F, 0F, 0F),
                        rot(1.6F, 8F, 0F, 0F),
                        rot(3.5F, 8F, 0F, 0F),
                        rot(6F, 8F, 0F, 0F),
                        rot(10F, 8F, 0F, 0F)))
                .addAnimation("capa_2", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.6F, 0F, 0F, 0F),
                        rot(1.6F, 24F, 0F, 0F),
                        rot(3.5F, 24F, 0F, 0F),
                        rot(6F, 24F, 0F, 0F),
                        rot(10F, 24F, 0F, 0F)))
                .addAnimation("capa_3", giro(rot(0F, 0F, 0F, 0F),
                        rot(0.6F, 0F, 0F, 0F),
                        rot(1.6F, 50F, 0F, 0F),
                        rot(3.5F, 50F, 0F, 0F),
                        rot(6F, 50F, 0F, 0F),
                        rot(10F, 50F, 0F, 0F)))
                .build();
    }

}
