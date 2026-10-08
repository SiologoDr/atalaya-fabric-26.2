package com.atalaya.client;

import net.minecraft.client.renderer.entity.state.LivingEntityRenderState;
import net.minecraft.world.phys.Vec3;
import org.jspecify.annotations.Nullable;

/** La foto de Novilis que el renderer saca cada fotograma. */
public class NovilisRenderState extends LivingEntityRenderState {

    public int estado;
    /** Peso de andar y reposo: se mezclan con los ataques en vez de saltar. */
    public float pesoLibre;
    /** El reloj de la animacion de andar (ms) y lo que pesa andar frente a estar quieto (0 a 1). */
    public float relojAndar;
    /** El reloj de correr (ms) y lo que pesa correr frente a andar (0 a 1). */
    public float relojCorrer;
    public float corre;
    /** La estela de la hoja: muestras (de ahora hacia atras), cada ESTELA_PASO segundos de animacion. */
    public static final int ESTELA = 9;
    public static final float ESTELA_PASO = 1.0F / 60.0F;
    public final Vec3[] estelaBase = new Vec3[ESTELA];
    public final Vec3[] estelaPunta = new Vec3[ESTELA];
    public int estelaN;
    public float andar;
    /** Desde cuando tiene la Furia (ticks; para que el fuego prenda y no aparezca de golpe). */
    public float desdeFuria = 100.0F;
    /** Fase 1-4: el color de las grietas, del nucleo y de su sol. */
    public int fase;
    /** Velocidad de la animacion de ataque (NovilisEntity.ritmo). */
    public float ritmo = 1.0F;
    /** Segundos de ANIMACION desde que empezo el estado actual (con el ritmo). */
    public float segundosEstado;
    /** La Furia (fuego azul) y el Grito de guerra. */
    public boolean furia;
    public boolean grito;
    /** Muerto del todo y con su sol ya en oro. */
    public boolean libre;
    /** Segundos desde que empezo la liberacion. */
    public float segundosLibera;
    /** De 0 a 1 mientras se deshace en brasas al final de la liberacion. */
    public float disolver;
    /** La carga de su sol en las Fuentes (0 a 1). */
    public float carga;
    /** Su sol esta en el cielo (la Sombra del Escudo). */
    public boolean solFuera;

    // --- Lo que se pinta fuera del cuerpo, relativo a los pies ---
    /** Su sol (sobre el halo). */
    public Vec3 sol = Vec3.ZERO;
    /** El haz del Castigo: de su sol a la punta de la espada (null si no toca). */
    public @Nullable Vec3 punta;
    /** El haz que senala a quien va a coger en la Ofrenda, o al que tiene en las manos. */
    public @Nullable Vec3 marca;
    /** El sol que se le forma en la mano en el Sol x3. */
    public @Nullable Vec3 solMano;
}
