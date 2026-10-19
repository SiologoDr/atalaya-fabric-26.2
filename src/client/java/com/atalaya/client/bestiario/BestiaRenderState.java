package com.atalaya.client.bestiario;

import net.minecraft.client.renderer.entity.state.LivingEntityRenderState;
import net.minecraft.world.entity.AnimationState;

/** Lo que hace falta para pintar un mob del bestiario: sus animaciones de golpe, su estado y lo que mira. */
public class BestiaRenderState extends LivingEntityRenderState {

    public final AnimationState ataque = new AnimationState();
    public final AnimationState especial = new AnimationState();
    public final AnimationState especial2 = new AnimationState();
    public final AnimationState muerte = new AnimationState();
    public final AnimationState aparece = new AnimationState();
    /** El estado del mob (BestiaEntity.getEstado: 0, el normal; los demas, los suyos: enterrado, agarrado...). */
    public int estado;
    /** Ticks desde que cambio de estado (para las transiciones). */
    public float enEstado;
    /** Su variante (la textura): 0, la normal. */
    public int variante;
    /** Para que dos iguales juntos no se muevan a la vez (sale de su numero de entidad). */
    public float fase;
    /** Si persigue a alguien (anda mas deprisa, con otra postura). */
    public boolean caza;
    /** Un valor propio de cada mob (lo carga, lo hinchado, lo encendido...), de 0 a 1. */
    public float valor;
    /** Si es un creeper (lo hinchado de su mecha va en el valor: se hincha y parpadea en blanco). */
    public boolean creeper;
    /** El tinte de la malla (ARGB; -1, sin tinte): el verde de la hierba de su bioma si esta camuflado. */
    public int tinte = -1;
}
