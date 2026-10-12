package com.atalaya.client;

import net.minecraft.client.renderer.entity.state.LivingEntityRenderState;
import net.minecraft.world.entity.AnimationState;
import net.minecraft.world.phys.Vec3;

/** La foto de un mini jefe que el renderer saca cada fotograma. */
public class MiniJefeRenderState extends LivingEntityRenderState {

    public final AnimationState dormido = new AnimationState();
    public final AnimationState despertar = new AnimationState();
    public final AnimationState normal = new AnimationState();
    public final AnimationState area = new AnimationState();
    public final AnimationState especial = new AnimationState();
    public final AnimationState muerte = new AnimationState();

    public int estado;
    /** Lo que lleva en su estado (ticks, con la fraccion del fotograma). */
    public float tiempo;
    /** Lo que pesan el reposo y el paso (1 libre, 0 atacando). */
    public float pesoLibre;
    /** Bloques por tick a los que va (suavizado) y el reloj del paso (ms de animacion). */
    public float velocidad;
    public float relojAndar;
    /** Hacia donde va el ataque en curso (grados) y su punto, respecto a sus pies. */
    public float rumbo;
    public Vec3 punto = Vec3.ZERO;
    /** De 0 a 1 mientras se deshace al morir. */
    public float disolver;
    /** Lo que le queda de vida (0 a 1). */
    public float vida = 1.0F;
    /** Su escala en el mundo (el boceto mide eso por pixel). */
    public float escala = 1.0F;
    /** Un numero suyo, para que sus efectos no sean iguales a los de otro. */
    public int semilla;
    /** Hacia donde mira la cabeza respecto al cuerpo (grados): el giro y la inclinacion (positiva hacia abajo). */
    public float miraGiro;
    public float miraAlto;
    /**
     * Cuantos pixeles de la pantalla ocupa un bloque a su distancia (con el zoom
     * del catalejo y el alto de la ventana): elige su nivel de detalle.
     */
    public float pixelesPorBloque = 1000.0F;
    /**
     * Las matrices de sus piezas en este fotograma (16 floats cada una, del
     * espacio de la pieza al del modelo, en bloques): las pone la capa del cuerpo
     * y las usan los efectos que salen de ellas (el orbe, la hoja del arma...).
     */
    public float[] huesos = new float[0];
}
