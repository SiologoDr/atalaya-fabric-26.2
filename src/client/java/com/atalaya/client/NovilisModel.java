package com.atalaya.client;

import com.atalaya.Atalaya;
import com.atalaya.entity.NovilisEntity;
import com.atalaya.entity.NovilisGeometria;
import net.minecraft.client.animation.KeyframeAnimation;
import net.minecraft.client.model.EntityModel;
import net.minecraft.client.model.geom.ModelLayerLocation;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.resources.Identifier;
import net.minecraft.util.Mth;
import com.mojang.blaze3d.vertex.PoseStack;

import java.util.HashMap;
import java.util.Map;
import java.util.function.Function;

/**
 * El modelo de Novilis: la malla de {@link NovilisMalla} y las animaciones de
 * {@link NovilisAnimaciones} (las dos generadas), mas lo que depende del
 * combate y no de una animacion:
 *
 *   - la espada de la mano o la clavada en el suelo (en la Ofrenda y el Dios
 *     de la Guerra la clava para tener las dos manos libres; dormido la tiene
 *     clavada a su lado; al despertar la agarra, se apoya en ella sin moverla
 *     y luego la saca);
 *   - las animaciones de entrada y de bucle (la Ofrenda y el aturdido entran
 *     una vez y luego siguen en bucle mientras dure);
 *   - el halo que gira despacio y late;
 *   - el reloj de andar, que lleva la entidad: la animacion avanza lo que el
 *     anda, y asi los pies no patinan ni a 8 bloques por segundo.
 *
 * aPieza() lleva una PoseStack a cualquier hueso: con eso NovilisLlamasLayer
 * pone el fuego de la Furia y del Dios de la Guerra donde toca, siga la
 * animacion que siga.
 */
public class NovilisModel extends EntityModel<NovilisRenderState> {

    public static final ModelLayerLocation CAPA = new ModelLayerLocation(
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "novilis"), "main");

    private final ModelPart cabeza;
    private final ModelPart espada;
    private final ModelPart espadaSuelta;
    private final ModelPart halo;
    /** De la raiz a cada hueso que lleva fuego. */
    private final Map<String, ModelPart[]> cadenas = new HashMap<>();

    private final KeyframeAnimation reposo;
    private final KeyframeAnimation andar;
    private final KeyframeAnimation correr;
    private final KeyframeAnimation dormido;
    private final KeyframeAnimation despertar;
    private final KeyframeAnimation barrido;
    private final KeyframeAnimation castigo;
    private final KeyframeAnimation castigoOnda;
    private final KeyframeAnimation sol;
    private final KeyframeAnimation trompetas;
    private final KeyframeAnimation ofrenda;
    private final KeyframeAnimation ofrendaSostiene;
    private final KeyframeAnimation dios;
    private final KeyframeAnimation grito;
    private final KeyframeAnimation aturdido;
    private final KeyframeAnimation aturdidoBucle;
    private final KeyframeAnimation tambaleo;
    private final KeyframeAnimation liberacion;
    private final KeyframeAnimation espadaFuego;
    private final KeyframeAnimation infernal;
    private final KeyframeAnimation mar;

    public NovilisModel(ModelPart raiz) {
        super(raiz);
        Function<String, ModelPart> pieza = raiz.createPartLookup();
        this.cabeza = pieza.apply("cabeza");
        this.espada = pieza.apply("espada");
        this.espadaSuelta = pieza.apply("espada_suelta");
        this.halo = pieza.apply("halo");
        String[] cuerpo = {"raiz", "pelvis", "torso"};
        cadena(pieza, "cabeza", cuerpo, "cuello", "cabeza");
        cadena(pieza, "hombro_izq", cuerpo, "hombro_izq");
        cadena(pieza, "hombro_der", cuerpo, "hombro_der");
        cadena(pieza, "mano_izq", cuerpo, "hombro_izq", "brazo_izq", "antebrazo_izq", "mano_izq");
        cadena(pieza, "mano_der", cuerpo, "hombro_der", "brazo_der", "antebrazo_der", "mano_der");
        cadena(pieza, "espada", cuerpo, "hombro_der", "brazo_der", "antebrazo_der", "mano_der", "agarre", "espada");
        cadena(pieza, "espada_suelta", new String[]{"raiz"}, "espada_suelta");
        cadena(pieza, "torso", new String[]{"raiz", "pelvis"}, "torso");

        this.reposo = NovilisAnimaciones.REPOSO.bake(raiz);
        this.andar = NovilisAnimaciones.ANDAR.bake(raiz);
        this.correr = NovilisAnimaciones.CORRER.bake(raiz);
        this.dormido = NovilisAnimaciones.DORMIDO.bake(raiz);
        this.despertar = NovilisAnimaciones.DESPERTAR.bake(raiz);
        this.barrido = NovilisAnimaciones.BARRIDO.bake(raiz);
        this.castigo = NovilisAnimaciones.CASTIGO.bake(raiz);
        this.castigoOnda = NovilisAnimaciones.CASTIGO_ONDA.bake(raiz);
        this.sol = NovilisAnimaciones.SOL.bake(raiz);
        this.trompetas = NovilisAnimaciones.TROMPETAS.bake(raiz);
        this.ofrenda = NovilisAnimaciones.OFRENDA.bake(raiz);
        this.ofrendaSostiene = NovilisAnimaciones.OFRENDA_SOSTIENE.bake(raiz);
        this.dios = NovilisAnimaciones.DIOS.bake(raiz);
        this.grito = NovilisAnimaciones.GRITO.bake(raiz);
        this.aturdido = NovilisAnimaciones.ATURDIDO.bake(raiz);
        this.aturdidoBucle = NovilisAnimaciones.ATURDIDO_BUCLE.bake(raiz);
        this.tambaleo = NovilisAnimaciones.TAMBALEO.bake(raiz);
        this.liberacion = NovilisAnimaciones.LIBERACION.bake(raiz);
        this.espadaFuego = NovilisAnimaciones.ESPADA.bake(raiz);
        this.infernal = NovilisAnimaciones.INFERNAL.bake(raiz);
        this.mar = NovilisAnimaciones.MAR.bake(raiz);
    }

    private void cadena(Function<String, ModelPart> pieza, String nombre, String[] desde, String... resto) {
        ModelPart[] c = new ModelPart[desde.length + resto.length];
        for (int i = 0; i < desde.length; i++) {
            c[i] = pieza.apply(desde[i]);
        }
        for (int i = 0; i < resto.length; i++) {
            c[desde.length + i] = pieza.apply(resto[i]);
        }
        cadenas.put(nombre, c);
    }

    /** Lleva la pose (la del modelo, tras setupAnim) al espacio de un hueso (en bloques: 16 px de modelo = 1). */
    public void aPieza(PoseStack pose, String nombre) {
        root().translateAndRotate(pose);
        for (ModelPart p : cadenas.get(nombre)) {
            p.translateAndRotate(pose);
        }
    }

    public boolean espadaEnMano() {
        return espada.visible;
    }

    @Override
    public void setupAnim(NovilisRenderState s) {
        super.setupAnim(s);
        boolean muriendo = s.deathTime > 0;
        int e = s.estado;
        float seg = s.segundosEstado;
        float tk = seg * 20.0F;

        // --- La espada: en la mano o clavada a su lado ---
        boolean clavada = !muriendo && ((e == NovilisEntity.OFRENDA && tk >= NovilisGeometria.OFRENDA_SUELTA)
                || (e == NovilisEntity.DIOS && tk >= NovilisGeometria.DIOS_SUELTA && tk < NovilisGeometria.DIOS_RECOGE)
                || e == NovilisEntity.DORMIDO || (e == NovilisEntity.DESPERTAR && tk < NovilisGeometria.DESPERTAR_SACA));
        espada.visible = !clavada;
        espadaSuelta.visible = clavada;

        // --- Mirar: solo andando o quieto. En los ataques manda la animacion. ---
        float peso = muriendo ? 0.0F : s.pesoLibre;
        if (peso > 0.0F) {
            cabeza.yRot += Mth.clamp(s.yRot, -35.0F, 35.0F) * Mth.DEG_TO_RAD * peso;
            cabeza.xRot += Mth.clamp(s.xRot, -25.0F, 25.0F) * 0.5F * Mth.DEG_TO_RAD * peso;
        }

        if (muriendo) {
            liberacion.apply((long) (s.segundosLibera * 1000.0F), 1.0F);
        } else {
            float paso = s.andar;
            if (peso > 0.0F) {
                // Los relojes de andar y correr los lleva la entidad: avanzan lo que anda
                // (sin patinar). Entre los dos se funde segun la velocidad.
                andar.apply((long) s.relojAndar, paso * peso * (1.0F - s.corre));
                if (s.corre > 0.0F) {
                    correr.apply((long) s.relojCorrer, paso * peso * s.corre);
                }
                reposo.apply((long) (s.ageInTicks * 50.0F), (1.0F - paso) * peso);
            }
            long ms = (long) (seg * 1000.0F);
            switch (e) {
                case NovilisEntity.DORMIDO -> dormido.apply((long) (s.ageInTicks * 50.0F), 1.0F);
                case NovilisEntity.DESPERTAR -> despertar.apply(ms, 1.0F);
                case NovilisEntity.BARRIDO -> barrido.apply(ms, 1.0F);
                case NovilisEntity.CASTIGO -> castigo.apply(ms, 1.0F);
                case NovilisEntity.CASTIGO_ONDA -> castigoOnda.apply(ms, 1.0F);
                case NovilisEntity.SOL -> sol.apply(ms, 1.0F);
                case NovilisEntity.TROMPETAS, NovilisEntity.SOMBRA, NovilisEntity.MINI_ALZA -> trompetas.apply(ms, 1.0F);
                case NovilisEntity.OFRENDA -> entradaYBucle(ofrenda, ofrendaSostiene, NovilisGeometria.DURACION_OFRENDA, seg);
                case NovilisEntity.DIOS -> dios.apply(ms, 1.0F);
                case NovilisEntity.GRITO, NovilisEntity.MANDA -> grito.apply(ms, 1.0F);
                case NovilisEntity.ATURDIDO -> entradaYBucle(aturdido, aturdidoBucle, NovilisGeometria.DURACION_ATURDIDO, seg);
                case NovilisEntity.TAMBALEO -> tambaleo.apply(ms, 1.0F);
                case NovilisEntity.ESPADA -> espadaFuego.apply(ms, 1.0F);
                case NovilisEntity.INFERNAL -> infernal.apply(ms, 1.0F);
                case NovilisEntity.MAR, NovilisEntity.MINI_CLAVA -> mar.apply(ms, 1.0F);
                default -> {
                }
            }
        }

        // --- El halo gira despacio y late; mas deprisa en la IV y con la Furia ---
        float vel = (s.furia ? 0.03F : 0.012F) * (s.fase >= 4 ? 1.6F : 1.0F);
        halo.zRot += s.ageInTicks * vel;
        float late = 1.0F + 0.035F * Mth.sin(s.ageInTicks * 0.15F);
        halo.xScale *= late;
        halo.yScale *= late;
    }

    /** Una animacion que entra una vez y despues sigue en bucle mientras dure el estado. */
    private static void entradaYBucle(KeyframeAnimation entrada, KeyframeAnimation bucle, int ticksEntrada, float seg) {
        float dur = ticksEntrada / 20.0F;
        if (seg < dur) {
            entrada.apply((long) (seg * 1000.0F), 1.0F);
        } else {
            bucle.apply((long) ((seg - dur) * 1000.0F), 1.0F);
        }
    }
}
