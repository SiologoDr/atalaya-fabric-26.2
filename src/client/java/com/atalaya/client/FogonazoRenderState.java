package com.atalaya.client;

import net.minecraft.client.renderer.entity.state.CreeperRenderState;

/** Lo que hace falta para pintar el Fogonazo: lo del creeper (lo hinchado y si esta cargado) y su fase. */
public class FogonazoRenderState extends CreeperRenderState {

    /** Para que dos Fogonazos juntos no se muevan a la vez (sale de su numero de entidad). */
    public float fase;
}
