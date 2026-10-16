package com.atalaya.client;

import net.minecraft.client.renderer.entity.state.LivingEntityRenderState;

/** Lo que hace falta para pintar el Coco: en que esta, cuanto lleva de cada animacion y a quien tiene dentro. */
public class CocoRenderState extends LivingEntityRenderState {

    /** LIBRE, AVISANDO, TRAGANDO o LLENO (los de CocoEntity). */
    public byte estado;
    /** Ticks desde que empezo cada animacion, o -1 si no esta en marcha. */
    public float aviso = -1.0F;
    public float traga = -1.0F;
    public float manotazo = -1.0F;
    /** El nombre del que tiene dentro ("" si no tiene a nadie): el aviso de encima. */
    public String atrapado = "";
    /** Para que dos Cocos juntos no se muevan a la vez (sale de su numero de entidad). */
    public float fase;
}
