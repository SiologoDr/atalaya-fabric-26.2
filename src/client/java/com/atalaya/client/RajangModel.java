package com.atalaya.client;

import com.atalaya.Atalaya;
import com.atalaya.entity.RajangEntity;
import net.minecraft.client.animation.KeyframeAnimation;
import net.minecraft.client.model.EntityModel;
import net.minecraft.client.model.geom.ModelLayerLocation;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.renderer.rendertype.RenderTypes;
import net.minecraft.resources.Identifier;
import net.minecraft.util.Mth;

import java.util.ArrayList;
import java.util.List;
import java.util.function.Function;

/**
 * El modelo de Rajang: la malla de {@link RajangMalla} y las animaciones de
 * {@link RajangAnimaciones} (generadas desde rajang_juego*.py), mas lo que
 * depende del combate:
 *
 *   - el reposo, el paso y el galope, que se mezclan con los ataques por peso
 *     y entre si segun lo deprisa que va (cada uno con su reloj, que corre con
 *     la velocidad);
 *   - los cristales del lomo, el cuello, los hombros y la cabeza, que crecen
 *     con cada fase (escalados desde su base);
 *   - el peto de oro, que revienta en la fase IV y deja el sol al aire.
 */
public class RajangModel extends EntityModel<RajangRenderState> {

    public static final ModelLayerLocation CAPA = new ModelLayerLocation(
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "rajang"), "main");
    /** La misma malla hinchada, para el aura de la Furia. */
    public static final ModelLayerLocation CAPA_AURA = new ModelLayerLocation(
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "rajang"), "aura");

    /** Cuanto crecen los cristales en cada fase. */
    private static final float[] CRECEN = {1.0F, 1.0F, 1.12F, 1.3F, 1.55F};

    private final ModelPart peto;
    private final List<ModelPart> cristales = new ArrayList<>();

    private final KeyframeAnimation reposo;
    private final KeyframeAnimation andar;
    private final KeyframeAnimation correr;
    private final KeyframeAnimation dormido;
    private final KeyframeAnimation despertar;
    private final KeyframeAnimation garra;
    private final KeyframeAnimation terremoto;
    private final KeyframeAnimation rugido;
    private final KeyframeAnimation sello;
    private final KeyframeAnimation cataclismo;
    private final KeyframeAnimation cataclismoSostiene;
    private final KeyframeAnimation cataclismoBaja;
    private final KeyframeAnimation aturdido;
    private final KeyframeAnimation paralizado;
    private final KeyframeAnimation salto;
    private final KeyframeAnimation tambaleo;
    private final KeyframeAnimation embestidaAviso;
    private final KeyframeAnimation embestida;
    private final KeyframeAnimation embestidaFrena;
    private final KeyframeAnimation estampado;
    private final KeyframeAnimation tumba;
    private final KeyframeAnimation liberacion;

    public RajangModel(ModelPart raiz) {
        super(raiz, RenderTypes::entityCutout);
        Function<String, ModelPart> buscar = raiz.createPartLookup();
        this.peto = buscar.apply("peto");
        for (String n : RajangMalla.CRISTALES) {
            cristales.add(buscar.apply(n));
        }
        this.reposo = RajangAnimaciones.REPOSO.bake(raiz);
        this.andar = RajangAnimaciones.ANDAR.bake(raiz);
        this.correr = RajangAnimaciones.CORRER.bake(raiz);
        this.dormido = RajangAnimaciones.DORMIDO.bake(raiz);
        this.despertar = RajangAnimaciones.DESPERTAR.bake(raiz);
        this.garra = RajangAnimaciones.GARRA.bake(raiz);
        this.terremoto = RajangAnimaciones.TERREMOTO.bake(raiz);
        this.rugido = RajangAnimaciones.RUGIDO.bake(raiz);
        this.sello = RajangAnimaciones.SELLO.bake(raiz);
        this.cataclismo = RajangAnimaciones.CATACLISMO.bake(raiz);
        this.cataclismoSostiene = RajangAnimaciones.CATACLISMO_SOSTIENE.bake(raiz);
        this.cataclismoBaja = RajangAnimaciones.CATACLISMO_BAJA.bake(raiz);
        this.aturdido = RajangAnimaciones.ATURDIDO.bake(raiz);
        this.paralizado = RajangAnimaciones.PARALIZADO.bake(raiz);
        this.salto = RajangAnimaciones.SALTO.bake(raiz);
        this.tambaleo = RajangAnimaciones.TAMBALEO.bake(raiz);
        this.embestidaAviso = RajangAnimaciones.EMBESTIDA_AVISO.bake(raiz);
        this.embestida = RajangAnimaciones.EMBESTIDA.bake(raiz);
        this.embestidaFrena = RajangAnimaciones.EMBESTIDA_FRENA.bake(raiz);
        this.estampado = RajangAnimaciones.ESTAMPADO.bake(raiz);
        this.tumba = RajangAnimaciones.TUMBA.bake(raiz);
        this.liberacion = RajangAnimaciones.LIBERACION.bake(raiz);
    }

    @Override
    public void setupAnim(RajangRenderState s) {
        super.setupAnim(s);
        boolean muriendo = s.deathTime > 0;
        if (!muriendo) {
            if (s.pesoLibre > 0.0F) {
                // Quieto, al paso o al galope, segun lo deprisa que va.
                // Al paso (acechando) va a ~0.26 bloques por tick (0.35 con la Furia) y al galope
                // a ~0.7: el cambio, alrededor de RajangEntity.VEL_GALOPE, dura poco.
                float anda = Mth.clamp(s.velocidad / 0.06F, 0.0F, 1.0F);
                float corre = Mth.clamp((s.velocidad - (RajangEntity.VEL_GALOPE - 0.08F)) / 0.16F, 0.0F, 1.0F);
                reposo.apply((long) (s.ageInTicks * 50.0F), s.pesoLibre * (1.0F - anda));
                andar.apply((long) s.relojAndar, s.pesoLibre * anda * (1.0F - corre));
                correr.apply((long) s.relojCorrer, s.pesoLibre * anda * corre);
            }
            dormido.apply(s.dormido, s.ageInTicks, 1.0F);
            despertar.apply(s.despertar, s.ageInTicks, 1.0F);
            garra.apply(s.garra, s.ageInTicks, s.ritmo);
            terremoto.apply(s.terremoto, s.ageInTicks, s.ritmo);
            rugido.apply(s.rugido, s.ageInTicks, s.ritmo);
            sello.apply(s.sello, s.ageInTicks, 1.0F);
            cataclismo.apply(s.cataclismo, s.ageInTicks, s.ritmo);
            cataclismoSostiene.apply(s.cataclismoSostiene, s.ageInTicks, 1.0F);
            cataclismoBaja.apply(s.cataclismoBaja, s.ageInTicks, s.ritmo);
            aturdido.apply(s.aturdido, s.ageInTicks, 1.0F);
            paralizado.apply(s.paralizado, s.ageInTicks, 1.0F);
            salto.apply(s.salto, s.ageInTicks, s.ritmo);
            tambaleo.apply(s.tambaleo, s.ageInTicks, 1.0F);
            embestidaAviso.apply(s.embestidaAviso, s.ageInTicks, s.ritmo);
            embestida.apply(s.embestida, s.ageInTicks, 1.0F);
            embestidaFrena.apply(s.embestidaFrena, s.ageInTicks, 1.0F);
            estampado.apply(s.estampado, s.ageInTicks, 1.0F);
            tumba.apply(s.tumba, s.ageInTicks, 1.0F);
        }
        liberacion.apply(s.liberacion, s.ageInTicks);
        crecer(CRECEN[Mth.clamp(s.fase, 1, 4)]);
        peto.visible = s.fase < 4;
    }

    /** Los cristales crecen desde su base: sobre todo a lo largo, algo a lo ancho. */
    private void crecer(float k) {
        if (k == 1.0F) {
            return;
        }
        float ancho = (float) Math.sqrt(k);
        for (ModelPart c : cristales) {
            c.yScale *= k;
            c.xScale *= ancho;
            c.zScale *= ancho;
        }
    }
}
