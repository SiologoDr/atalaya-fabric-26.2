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
    public final AnimationState embestidaAviso = new AnimationState();
    public final AnimationState embestida = new AnimationState();
    public final AnimationState embestidaFrena = new AnimationState();
    public final AnimationState estampado = new AnimationState();
    public final AnimationState tumba = new AnimationState();
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
    /** Con la Furia de Jade: el aura verde. */
    public boolean furia;
    /** La flecha de la Embestida: lo que mide desde sus manos (0: no hay) y lo llenado (0 a 1). */
    public float carga;
    public float cargaLlena;
    /** La Tumba de Raices: ticks desde que clavo las garras (negativo: no hay circulo). */
    public float circuloTumba = -1.0F;
    /** La Tumba de ahora es en anillo (se salva cerca de el). */
    public boolean tumbaAnillo;
    /** El despertar: ticks desde que empezo (negativo: no esta despertando). Le enciende los ojos y la cresta. */
    public float tiempoDespertar = -1.0F;
    /** El Idolo de Oro en la cabeza de quien lo lleva: donde, respecto a sus pies (null si nadie lo lleva). */
    public net.minecraft.world.phys.@org.jspecify.annotations.Nullable Vec3 idoloCabeza;
    /** Hacia donde mira el portador (grados): el idolo mira igual. */
    public float idoloRumbo;
    public final net.minecraft.client.renderer.item.ItemStackRenderState idolo =
            new net.minecraft.client.renderer.item.ItemStackRenderState();
}
