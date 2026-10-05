package com.atalaya.client;

import net.minecraft.client.renderer.entity.state.LivingEntityRenderState;
import net.minecraft.world.entity.AnimationState;

/**
 * Lo que el renderer copia de la entidad cada fotograma. Desde 1.21.2 el
 * modelo ya no ve la entidad: solo esta foto.
 */
public class VigiaRenderState extends LivingEntityRenderState {

    public final AnimationState reposo = new AnimationState();
    public final AnimationState alerta = new AnimationState();
    public final AnimationState cepo = new AnimationState();
    public final AnimationState mirada = new AnimationState();
    public final AnimationState tambaleo = new AnimationState();
    public final AnimationState buscar = new AnimationState();
    public final AnimationState muerte = new AnimationState();

    /** Con presa: el ojo pasa de ambar a rojo. */
    public boolean cazando;

    public int estado;
}
