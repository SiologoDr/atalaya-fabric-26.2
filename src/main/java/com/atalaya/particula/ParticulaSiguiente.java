package com.atalaya.particula;

/**
 * Lo que lleva la siguiente particula de Nerea que se cree en el cliente: el
 * tamano (la mecha del canon echa un humo fino; la bala, uno mediano), el color
 * y la forma de una nota (el Duelo de Canto: cada carril el suyo) y lo que vive
 * (la nota que vuela de su boca llega justo cuando la nota del panel llega a la
 * linea). Las particulas se crean al momento de anadirlas, asi que basta con
 * ponerlo justo antes de level().addParticle; NereaParticula lo lee y lo vuelve
 * a dejar como estaba. Esta en el codigo comun porque tambien lo ponen las
 * entidades (en su lado del cliente).
 */
public final class ParticulaSiguiente {

    public static float escala = 1.0F;
    /** RGB, o -1 para el de siempre. */
    public static int color = -1;
    /** Ticks, o -1 para lo de siempre. */
    public static int vida = -1;
    /** El fotograma (en las notas: 0 corchea, 1 dos corcheas, 2 negra, 3 rota), o -1 al azar. */
    public static int forma = -1;

    private ParticulaSiguiente() {
    }

    /** Lo vuelve a dejar como siempre (lo llama la particula al nacer). */
    public static void olvidar() {
        escala = 1.0F;
        color = -1;
        vida = -1;
        forma = -1;
    }
}
