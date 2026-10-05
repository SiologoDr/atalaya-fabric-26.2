package com.atalaya.client;

import net.minecraft.client.renderer.entity.state.LivingEntityRenderState;
import net.minecraft.world.entity.AnimationState;

/** La foto de Aeralis que el renderer saca cada fotograma. */
public class AeralisRenderState extends LivingEntityRenderState {

    public final AnimationState dormida = new AnimationState();
    public final AnimationState despertar = new AnimationState();
    public final AnimationState aleteo = new AnimationState();
    public final AnimationState tornados = new AnimationState();
    public final AnimationState marca = new AnimationState();
    public final AnimationState rafaga = new AnimationState();
    public final AnimationState dobleRafaga = new AnimationState();
    public final AnimationState juicioSube = new AnimationState();
    public final AnimationState juicioSostiene = new AnimationState();
    public final AnimationState juicioGolpe = new AnimationState();
    public final AnimationState aturdida = new AnimationState();
    public final AnimationState agotada = new AnimationState();
    public final AnimationState tambaleo = new AnimationState();
    public final AnimationState liberacion = new AnimationState();

    public int estado;
    /** Peso del vuelo: se mezcla con los ataques en vez de saltar. */
    public float pesoLibre;
    /** Fase 1-4: las alas pasan del blanco cielo al negro tormenta. */
    public int fase;
    /** Velocidad de la animacion de ataque (AeralisEntity.ritmo). */
    public float ritmo = 1.0F;
    /** Liberada y con los ojos ya en oro: vuelve al blanco del principio. */
    public boolean libre;
    /** De 0 a 1 mientras se deshace en viento al final. */
    public float disolver;
    /** Inercia del vuelo (grados): inclinada hacia delante y ladeada en los giros. */
    public float cabeceo;
    public float alabeo;
    /** Cuanto pesa el vuelo rapido (0 a 1). */
    public float avance;
    /** El reloj de la batida, en ms de animacion. */
    public float relojVuelo;
}
