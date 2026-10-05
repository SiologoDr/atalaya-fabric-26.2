package com.atalaya.client;

import net.minecraft.client.renderer.entity.state.LivingEntityRenderState;
import net.minecraft.world.entity.AnimationState;

/** La foto de Rajang que el renderer saca cada fotograma. */
public class RajangRenderState extends LivingEntityRenderState {

    public final AnimationState dormido = new AnimationState();
    public final AnimationState despertar = new AnimationState();
    public final AnimationState garra = new AnimationState();
    public final AnimationState terremoto = new AnimationState();
    public final AnimationState rugido = new AnimationState();
    public final AnimationState sello = new AnimationState();
    public final AnimationState cataclismo = new AnimationState();
    public final AnimationState cataclismoSostiene = new AnimationState();
    public final AnimationState cataclismoBaja = new AnimationState();
    public final AnimationState aturdido = new AnimationState();
    public final AnimationState paralizado = new AnimationState();
    public final AnimationState salto = new AnimationState();
    public final AnimationState tambaleo = new AnimationState();
    public final AnimationState liberacion = new AnimationState();

    public int estado;
    /** Peso del reposo, el paso y el galope: se mezclan con los ataques en vez de saltar. */
    public float pesoLibre;
    /** Fase 1-4: el jade se raja, el oro se mancha, los cristales crecen y el peto se cae. */
    public int fase;
    /** Velocidad de la animacion de ataque (RajangEntity.ritmo). */
    public float ritmo = 1.0F;
    /** Bloques por tick a los que va (suavizado): decide cuanto pesa andar y correr. */
    public float velocidad;
    /** Los relojes del paso y del galope, en ms de animacion. */
    public float relojAndar;
    public float relojCorrer;
    /** Liberado y con los ojos ya en oro. */
    public boolean libre;
    /** De 0 a 1 mientras se vuelve piedra y se deshace al final. */
    public float disolver;
}
