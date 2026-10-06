package com.atalaya.client;

import net.minecraft.client.renderer.entity.state.LivingEntityRenderState;
import net.minecraft.world.entity.AnimationState;
import net.minecraft.world.phys.Vec3;
import org.jspecify.annotations.Nullable;

import java.util.ArrayList;
import java.util.List;

/** La foto de Nerea que el renderer saca cada fotograma. */
public class NereaRenderState extends LivingEntityRenderState {

    public final AnimationState reposo = new AnimationState();
    public final AnimationState dormido = new AnimationState();
    public final AnimationState despertar = new AnimationState();
    public final AnimationState rompeolas = new AnimationState();
    public final AnimationState remolino = new AnimationState();
    public final AnimationState burbujas = new AnimationState();
    public final AnimationState molino = new AnimationState();
    public final AnimationState arponLanzar = new AnimationState();
    public final AnimationState arponEspera = new AnimationState();
    public final AnimationState arponTirar = new AnimationState();
    public final AnimationState mirada = new AnimationState();
    public final AnimationState aturdido = new AnimationState();
    public final AnimationState tambaleo = new AnimationState();
    public final AnimationState agotado = new AnimationState();
    public final AnimationState geiser = new AnimationState();
    public final AnimationState marea = new AnimationState();
    public final AnimationState liberacion = new AnimationState();

    public int estado;
    /** Peso de andar y reposo: se mezclan con los ataques en vez de saltar. */
    public float pesoLibre;
    public int cadenas;
    /** Fase 1-4: el estado del corazon (cada vez mas rajado y apagado). */
    public int fase;
    /** Velocidad de la animacion de ataque: sube con la fase (NereaEntity.ritmo). */
    public float ritmo = 1.0F;
    public int ojosRotos;
    /** Segundos desde que empezo el estado actual (para ocultar piezas a destiempo). */
    public float segundosEstado;
    /** Muerto del todo y con los ojos ya en oro. */
    public boolean libre;
    /** De 0 a 1 mientras se deshace en agua al final de la liberacion. */
    public float disolver;
    /** La Furia de las Mareas: el aura de causticas (NereaFuriaLayer). */
    public boolean furia;

    // --- La Mirada, relativo a los pies ---
    public @Nullable Vec3 ojoIzq;
    public @Nullable Vec3 ojoDer;
    /** Donde acaba cada chorro (uno por cada mirado; se corta contra el primer bloque). */
    public final List<Vec3> finesRayo = new ArrayList<>();
    public float cargaRayo;
    /** Impactos en cada ojo: las grietas. */
    public int golpesIzq;
    public int golpesDer;

    // --- Lo que se pinta en el suelo, relativo a los pies ---
    /** Donde cae el hueco de la Gran Marea (bloques a un lado de su rumbo). */
    public float hueco;
    /** Las burbujas de aire doradas de quien lleva antorcha en el Remolino (el centro de cada una). */
    public final List<Vec3> burbujasAire = new ArrayList<>();
}
