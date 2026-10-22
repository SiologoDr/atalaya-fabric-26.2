package com.atalaya.client.bestiario;

import net.minecraft.client.animation.KeyframeAnimation;
import net.minecraft.client.model.EntityModel;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.util.Mth;
import org.jspecify.annotations.Nullable;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * El modelo de un mob del bestiario: su malla (BestiaDatos) y sus animaciones de keyframes, todas suyas.
 *
 * <pre>
 *   reposo          en bucle mientras esta quieto (respira, mira, se rasca...)
 *   andar, correr   el paso al andar y al perseguir, al ritmo de lo que avanza
 *   estado&lt;n&gt;       en bucle mientras esta en ese estado (enterrado, agarrado, cargando...): manda sobre las de arriba
 *   siempre         en bucle siempre que este vivo, ande o no (el corazon que late, la baliza que gira, las llamas)
 *   hinchado        (los creepers) de un segundo, recorrida con lo que va de la mecha: la boca que se abre
 *   ataque, especial, especial2, aparece, muerte
 *                   las de golpe, que arranca el servidor (BestiaEntity.animar); suman encima
 * </pre>
 *
 * Las animaciones suman a la postura de reposo de la malla. La cabeza (lo que diga "mira") sigue la mirada.
 */
public class BestiaModel extends EntityModel<BestiaRenderState> {

    private final Map<String, KeyframeAnimation> anim = new HashMap<>();
    private final List<ModelPart> mira = new ArrayList<>();
    private final List<Float> cuantoMira;
    private final float pasoTiempo;
    private final @Nullable ModelPart silla;

    public BestiaModel(ModelPart raiz, BestiaDatos.Datos datos) {
        super(raiz);
        datos.animaciones.forEach((nombre, def) -> anim.put(nombre, def.bake(raiz)));
        java.util.function.Function<String, ModelPart> buscar = raiz.createPartLookup();
        for (String m : datos.mira) {
            mira.add(buscar.apply(m));
        }
        cuantoMira = datos.cuantoMira;
        pasoTiempo = datos.paso;
        silla = buscar.apply("silla");
    }

    public @Nullable KeyframeAnimation animacion(String nombre) {
        return anim.get(nombre);
    }

    @Override
    public void setupAnim(BestiaRenderState s) {
        super.setupAnim(s);
        if (silla != null) {
            silla.visible = s.valor > 0.5F;
        }
        float t = s.ageInTicks + s.fase * 40.0F;
        boolean muerto = s.deathTime > 0.0F;
        KeyframeAnimation enEstado = s.estado != 0 ? anim.get("estado" + s.estado) : null;
        if (!muerto) {
            if (enEstado != null) {
                enEstado.apply((long) (t * 50.0F), 1.0F);
            } else {
                float anda = Mth.clamp(s.walkAnimationSpeed * 1.6F, 0.0F, 1.0F);
                KeyframeAnimation reposo = anim.get("reposo");
                if (reposo != null && anda < 1.0F) {
                    reposo.apply((long) (t * 50.0F), 1.0F - anda);
                }
                KeyframeAnimation paso = s.caza && anim.containsKey("correr") ? anim.get("correr") : anim.get("andar");
                if (paso != null) {
                    paso.applyWalk(s.walkAnimationPos, s.walkAnimationSpeed, pasoTiempo, 2.5F);
                }
            }
            KeyframeAnimation siempre = anim.get("siempre");
            if (siempre != null) {
                siempre.apply((long) (t * 50.0F), 1.0F);
            }
            // Lo hinchado de la mecha de los creepers: "hinchado" (de un segundo) se recorre con lo que va de mecha, de
            // 0 a 1 (la boca se abre, la cabeza se echa atras...).
            KeyframeAnimation hinchado = anim.get("hinchado");
            if (hinchado != null && s.creeper && s.valor > 0.0F) {
                hinchado.apply((long) (s.valor * 1000.0F), 1.0F);
            }
            // La mirada.
            for (int i = 0; i < mira.size(); i++) {
                ModelPart p = mira.get(i);
                if (p != null) {
                    float k = cuantoMira.get(i);
                    p.yRot += s.yRot * Mth.DEG_TO_RAD * k;
                    p.xRot += s.xRot * Mth.DEG_TO_RAD * k;
                }
            }
        }
        golpe("aparece", s.aparece, s.ageInTicks);
        golpe("ataque", s.ataque, s.ageInTicks);
        golpe("especial", s.especial, s.ageInTicks);
        golpe("especial2", s.especial2, s.ageInTicks);
        golpe("muerte", s.muerte, s.ageInTicks);
    }

    private void golpe(String nombre, net.minecraft.world.entity.AnimationState estado, float edad) {
        KeyframeAnimation a = anim.get(nombre);
        if (a != null && estado.isStarted()) {
            a.apply(estado, edad);
        }
    }
}
