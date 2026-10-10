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
    public final AnimationState picadoAviso = new AnimationState();
    public final AnimationState picado = new AnimationState();
    public final AnimationState posada = new AnimationState();
    public final AnimationState escamas = new AnimationState();
    /** La Furia del Vendaval: el aura de rayos. */
    public boolean furia;
    /** La linea del Picado: lo que mide por delante (0: no hay), lo llenado (0 a 1) y el suelo bajo ella (bloques, negativo). */
    public float picadoLargo;
    public float picadoLleno;
    public float picadoSuelo;

    public int estado;
    /** Peso del vuelo: se mezcla con los ataques en vez de saltar. */
    public float pesoLibre;
    /** Fase 1-4: las alas pasan del blanco cielo al negro tormenta. */
    public int fase;
    /** Velocidad de la animacion de ataque (AeralisEntity.ritmo). */
    public float ritmo = 1.0F;
    /** Lo que dura la aturdida en curso (ticks). */
    public int duracionAturdida = 100;
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
    /** Lo abiertos que estan los ocelos (los Ocelos, el minijuego): 0 a 1. */
    public float ocelos;
    /** Si estan entornados (el aviso de que van a abrirse: de ambar). */
    public boolean ocelosAviso;
    /** El reloj, para el latido del aviso. */
    public float ocelosReloj;
}
