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

import java.util.function.Function;

/**
 * El modelo de Novilis: la malla de {@link NovilisMalla} y las animaciones de
 * {@link NovilisAnimaciones} (las dos generadas), mas lo que depende del
 * combate y no de una animacion:
 *
 *   - la espada de la mano o la clavada en el suelo (en la Ofrenda y el Dios
 *     de la Guerra la clava para tener las dos manos libres);
 *   - las animaciones de entrada y de bucle (las Fuentes, la Ofrenda y el
 *     aturdido entran una vez y luego siguen en bucle mientras dure);
 *   - el halo que gira despacio y late.
 *
 * La misma malla, hinchada (CAPA_AURA), es la del aura de la Furia y del Dios
 * de la Guerra (NovilisAuraLayer).
 */
public class NovilisModel extends EntityModel<NovilisRenderState> {

    public static final ModelLayerLocation CAPA = new ModelLayerLocation(
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "novilis"), "main");
    public static final ModelLayerLocation CAPA_AURA = new ModelLayerLocation(
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "novilis"), "aura");

    private final ModelPart cabeza;
    private final ModelPart espada;
    private final ModelPart espadaSuelta;
    private final ModelPart halo;

    private final KeyframeAnimation reposo;
    private final KeyframeAnimation andar;
    private final KeyframeAnimation dormido;
    private final KeyframeAnimation despertar;
    private final KeyframeAnimation barrido;
    private final KeyframeAnimation castigo;
    private final KeyframeAnimation castigoOnda;
    private final KeyframeAnimation sol;
    private final KeyframeAnimation trompetas;
    private final KeyframeAnimation fuentes;
    private final KeyframeAnimation fuentesCarga;
    private final KeyframeAnimation ofrenda;
    private final KeyframeAnimation ofrendaSostiene;
    private final KeyframeAnimation dios;
    private final KeyframeAnimation grito;
    private final KeyframeAnimation aturdido;
    private final KeyframeAnimation aturdidoBucle;
    private final KeyframeAnimation tambaleo;
    private final KeyframeAnimation liberacion;

    public NovilisModel(ModelPart raiz) {
        super(raiz);
        Function<String, ModelPart> pieza = raiz.createPartLookup();
        this.cabeza = pieza.apply("cabeza");
        this.espada = pieza.apply("espada");
        this.espadaSuelta = pieza.apply("espada_suelta");
        this.halo = pieza.apply("halo");

        this.reposo = NovilisAnimaciones.REPOSO.bake(raiz);
        this.andar = NovilisAnimaciones.ANDAR.bake(raiz);
        this.dormido = NovilisAnimaciones.DORMIDO.bake(raiz);
        this.despertar = NovilisAnimaciones.DESPERTAR.bake(raiz);
        this.barrido = NovilisAnimaciones.BARRIDO.bake(raiz);
        this.castigo = NovilisAnimaciones.CASTIGO.bake(raiz);
        this.castigoOnda = NovilisAnimaciones.CASTIGO_ONDA.bake(raiz);
        this.sol = NovilisAnimaciones.SOL.bake(raiz);
        this.trompetas = NovilisAnimaciones.TROMPETAS.bake(raiz);
        this.fuentes = NovilisAnimaciones.FUENTES.bake(raiz);
        this.fuentesCarga = NovilisAnimaciones.FUENTES_CARGA.bake(raiz);
        this.ofrenda = NovilisAnimaciones.OFRENDA.bake(raiz);
        this.ofrendaSostiene = NovilisAnimaciones.OFRENDA_SOSTIENE.bake(raiz);
        this.dios = NovilisAnimaciones.DIOS.bake(raiz);
        this.grito = NovilisAnimaciones.GRITO.bake(raiz);
        this.aturdido = NovilisAnimaciones.ATURDIDO.bake(raiz);
        this.aturdidoBucle = NovilisAnimaciones.ATURDIDO_BUCLE.bake(raiz);
        this.tambaleo = NovilisAnimaciones.TAMBALEO.bake(raiz);
        this.liberacion = NovilisAnimaciones.LIBERACION.bake(raiz);
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
                || (e == NovilisEntity.DIOS && tk >= NovilisGeometria.DIOS_SUELTA && tk < NovilisGeometria.DIOS_RECOGE));
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
            float paso = Math.min(s.walkAnimationSpeed * 2.5F, 1.0F);
            if (peso > 0.0F) {
                // Una vuelta de la animacion (2 s) cada ZANCADA bloques; walkAnimationPos sube unas 4 por bloque.
                andar.apply((long) (s.walkAnimationPos * 500.0F / NovilisGeometria.ZANCADA), paso * peso);
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
                case NovilisEntity.TROMPETAS -> trompetas.apply(ms, 1.0F);
                case NovilisEntity.FUENTES -> entradaYBucle(fuentes, fuentesCarga, NovilisGeometria.DURACION_FUENTES, seg);
                case NovilisEntity.OFRENDA -> entradaYBucle(ofrenda, ofrendaSostiene, NovilisGeometria.DURACION_OFRENDA, seg);
                case NovilisEntity.DIOS -> dios.apply(ms, 1.0F);
                case NovilisEntity.GRITO -> grito.apply(ms, 1.0F);
                case NovilisEntity.ATURDIDO -> entradaYBucle(aturdido, aturdidoBucle, NovilisGeometria.DURACION_ATURDIDO, seg);
                case NovilisEntity.TAMBALEO -> tambaleo.apply(ms, 1.0F);
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
