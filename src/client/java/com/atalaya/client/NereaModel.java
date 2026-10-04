package com.atalaya.client;

import com.atalaya.Atalaya;
import com.atalaya.entity.NereaEntity;
import com.atalaya.entity.NereaGeometria;
import net.minecraft.client.animation.KeyframeAnimation;
import net.minecraft.client.model.EntityModel;
import net.minecraft.client.model.geom.ModelLayerLocation;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.resources.Identifier;
import net.minecraft.util.Mth;

import java.util.function.Function;

/**
 * El modelo de Nerea: la malla de {@link NereaMalla} (generada) y las
 * animaciones de {@link NereaAnimaciones} (generadas), mas lo que depende del
 * combate y no de una animacion:
 *
 *   - una cadena del pecho menos por cada fase, y en la fase IV las
 *     costillas abiertas: el corazon queda al aire;
 *   - el corazon de cada fase, cada vez mas rajado y mas apagado, y el limpio
 *     al quedar liberado;
 *   - las cadenas largas del molino, solo mientras gira;
 *   - la cadena-latigo de la mano, que desaparece mientras el gancho vuela;
 *   - los ojos que le apagan a flechazos;
 *   - el latido del corazon, desbocado cuando ya no le quedan cadenas.
 */
public class NereaModel extends EntityModel<NereaRenderState> {

    public static final ModelLayerLocation CAPA = new ModelLayerLocation(
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "nerea"), "main");

    private final ModelPart cabeza;
    private final ModelPart corazon;
    private final ModelPart[] corazones = new ModelPart[4];
    private final ModelPart corazonLibre;
    private final ModelPart costillas;
    private final ModelPart[] cadenas = new ModelPart[4];
    private final ModelPart molinoIzq;
    private final ModelPart molinoDer;
    private final ModelPart cadenaMano;
    private final ModelPart ojoIzq;
    private final ModelPart ojoDer;

    private final KeyframeAnimation reposo;
    private final KeyframeAnimation andar;
    private final KeyframeAnimation dormido;
    private final KeyframeAnimation despertar;
    private final KeyframeAnimation rompeolas;
    private final KeyframeAnimation remolino;
    private final KeyframeAnimation burbujas;
    private final KeyframeAnimation molino;
    private final KeyframeAnimation arponLanzar;
    private final KeyframeAnimation arponEspera;
    private final KeyframeAnimation arponTirar;
    private final KeyframeAnimation mirada;
    private final KeyframeAnimation aturdido;
    private final KeyframeAnimation tambaleo;
    private final KeyframeAnimation agotado;
    private final KeyframeAnimation liberacion;

    public NereaModel(ModelPart raiz) {
        super(raiz);
        Function<String, ModelPart> pieza = raiz.createPartLookup();
        this.cabeza = pieza.apply("cabeza");
        this.corazon = pieza.apply("corazon");
        for (int i = 0; i < 4; i++) {
            corazones[i] = pieza.apply("corazon_" + (i + 1));
        }
        this.corazonLibre = pieza.apply("corazon_libre");
        this.costillas = pieza.apply("costillas");
        for (int i = 0; i < 4; i++) {
            cadenas[i] = pieza.apply("cadena_" + (i + 1));
        }
        this.molinoIzq = pieza.apply("molino_izq");
        this.molinoDer = pieza.apply("molino_der");
        this.cadenaMano = pieza.apply("cadena_mano");
        this.ojoIzq = pieza.apply("ojo_izq");
        this.ojoDer = pieza.apply("ojo_der");

        this.reposo = NereaAnimaciones.REPOSO.bake(raiz);
        this.andar = NereaAnimaciones.ANDAR.bake(raiz);
        this.dormido = NereaAnimaciones.DORMIDO.bake(raiz);
        this.despertar = NereaAnimaciones.DESPERTAR.bake(raiz);
        this.rompeolas = NereaAnimaciones.ROMPEOLAS.bake(raiz);
        this.remolino = NereaAnimaciones.REMOLINO.bake(raiz);
        this.burbujas = NereaAnimaciones.BURBUJAS.bake(raiz);
        this.molino = NereaAnimaciones.MOLINO.bake(raiz);
        this.arponLanzar = NereaAnimaciones.ARPON_LANZAR.bake(raiz);
        this.arponEspera = NereaAnimaciones.ARPON_ESPERA.bake(raiz);
        this.arponTirar = NereaAnimaciones.ARPON_TIRAR.bake(raiz);
        this.mirada = NereaAnimaciones.MIRADA.bake(raiz);
        this.aturdido = NereaAnimaciones.ATURDIDO.bake(raiz);
        this.tambaleo = NereaAnimaciones.TAMBALEO.bake(raiz);
        this.agotado = NereaAnimaciones.AGOTADO.bake(raiz);
        this.liberacion = NereaAnimaciones.LIBERACION.bake(raiz);
    }

    @Override
    public void setupAnim(NereaRenderState s) {
        super.setupAnim(s);
        boolean muriendo = s.deathTime > 0;
        int e = s.estado;
        float seg = s.segundosEstado;

        // --- Lo que se ve segun el combate ---
        for (int i = 0; i < 4; i++) {
            cadenas[i].visible = !muriendo && s.cadenas > i;
        }
        costillas.visible = muriendo || s.fase < 4 || e == NereaEntity.DORMIDO;
        for (int i = 0; i < 4; i++) {
            corazones[i].visible = !s.libre && s.fase == i + 1;
        }
        corazonLibre.visible = s.libre;
        // Las cadenas del molino se desenrollan al empezar y se recogen hacia la
        // mano al parar: no se quedan tiesas en el aire mientras baja los brazos.
        float tm = seg * 20.0F;
        float largoMolino = e == NereaEntity.MOLINO && !muriendo
                ? Mth.clamp((tm - NereaGeometria.MOLINO_VISIBLE) / 5.0F, 0.0F, 1.0F)
                * Mth.clamp(1.0F - (tm - NereaGeometria.MOLINO_PARA) / 6.0F, 0.0F, 1.0F)
                : 0.0F;
        boolean molinoFuera = largoMolino > 0.01F;
        molinoIzq.visible = molinoFuera;
        molinoDer.visible = molinoFuera;
        boolean ganchoFuera = (e == NereaEntity.ARPON_LANZAR && seg * 20.0F >= NereaGeometria.ARPON_SUELTA) || e == NereaEntity.ARPON_ESPERA
                || (e == NereaEntity.ARPON_TIRAR && seg * 20.0F < NereaGeometria.ARPON_ARRASTRE + 1);
        cadenaMano.visible = !molinoFuera && !ganchoFuera;
        boolean ojosApagados = e == NereaEntity.MIRADA || e == NereaEntity.ATURDIDO;
        ojoIzq.visible = !(ojosApagados && (s.ojosRotos & 1) != 0);
        ojoDer.visible = !(ojosApagados && (s.ojosRotos & 2) != 0);

        // --- Mirar: solo andando o quieto. En los ataques manda la animacion. ---
        float peso = muriendo ? 0.0F : s.pesoLibre;
        if (peso > 0.0F) {
            cabeza.yRot += Mth.clamp(s.yRot, -35.0F, 35.0F) * Mth.DEG_TO_RAD * peso;
            cabeza.xRot += Mth.clamp(s.xRot, -25.0F, 25.0F) * 0.5F * Mth.DEG_TO_RAD * peso;
        }

        if (!muriendo) {
            // Andar y reposo se reparten el peso: cuanto mas rapido anda, menos
            // respira quieto. Y los dos se apagan mientras ataca.
            // 2,8: un ciclo de zancada por cada 3,6 bloques recorridos, lo que
            // avanzan los pies en el suelo (nerea_juego_anim.py, apoyos_andar).
            float paso = Math.min(s.walkAnimationSpeed * 2.5F, 1.0F);
            if (peso > 0.0F) {
                andar.apply((long) (s.walkAnimationPos * 50.0F * 2.8F), paso * peso);
                reposo.apply((long) (s.ageInTicks * 50.0F), (1.0F - paso) * peso);
            }
            dormido.apply(s.dormido, s.ageInTicks, s.ritmo);
            despertar.apply(s.despertar, s.ageInTicks, s.ritmo);
            rompeolas.apply(s.rompeolas, s.ageInTicks, s.ritmo);
            remolino.apply(s.remolino, s.ageInTicks, s.ritmo);
            burbujas.apply(s.burbujas, s.ageInTicks, s.ritmo);
            molino.apply(s.molino, s.ageInTicks, s.ritmo);
            arponLanzar.apply(s.arponLanzar, s.ageInTicks, s.ritmo);
            arponEspera.apply(s.arponEspera, s.ageInTicks, s.ritmo);
            arponTirar.apply(s.arponTirar, s.ageInTicks, s.ritmo);
            mirada.apply(s.mirada, s.ageInTicks, s.ritmo);
            aturdido.apply(s.aturdido, s.ageInTicks, s.ritmo);
            tambaleo.apply(s.tambaleo, s.ageInTicks, s.ritmo);
            agotado.apply(s.agotado, s.ageInTicks, s.ritmo);
        }
        liberacion.apply(s.liberacion, s.ageInTicks);

        // Mas largas que en el modelo (y algo mas gruesas): para 30-40 jugadores.
        for (ModelPart c : new ModelPart[]{molinoIzq, molinoDer}) {
            c.xScale = NereaEntity.ESCALA_MOLINO;
            c.zScale = NereaEntity.ESCALA_MOLINO;
            c.yScale = largoMolino * NereaEntity.ESCALA_MOLINO;
        }

        // --- El latido: dos golpes seguidos y una pausa, como un corazon. ---
        if (!s.libre && e != NereaEntity.DORMIDO) {
            float ritmo = 0.9F + 0.35F * s.fase;
            float fase = (s.ageInTicks / 20.0F * ritmo) % 1.0F;
            float golpe = pulso(fase, 0.0F) + 0.6F * pulso(fase, 0.22F);
            float k = 1.0F + (0.05F + 0.03F * s.fase) * golpe;
            corazon.xScale *= k;
            corazon.yScale *= k;
            corazon.zScale *= k;
        }
    }

    private static float pulso(float fase, float inicio) {
        float d = fase - inicio;
        if (d < 0 || d > 0.18F) {
            return 0.0F;
        }
        return Mth.sin(d / 0.18F * Mth.PI);
    }
}
