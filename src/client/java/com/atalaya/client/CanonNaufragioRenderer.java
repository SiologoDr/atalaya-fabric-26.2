package com.atalaya.client;

import com.atalaya.Atalaya;
import com.atalaya.entity.CanonNaufragioEntity;
import net.minecraft.client.renderer.rendertype.RenderType;
import net.minecraft.client.renderer.rendertype.RenderTypes;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.resources.Identifier;
import java.util.List;
import net.minecraft.client.Minecraft;
import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import net.minecraft.client.renderer.SubmitNodeCollector;
import net.minecraft.client.renderer.entity.EntityRenderer;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.state.EntityRenderState;
import net.minecraft.client.renderer.state.level.CameraRenderState;
import net.minecraft.util.Mth;
import net.minecraft.world.phys.Vec3;

/**
 * Un Canon del Naufragio: el canon de bronce verdeado sobre su cureña de madera
 * podrida con ruedas, que sale del suelo y se hunde al acabar. Apunta con el
 * rumbo de la entidad y el alza; al disparar, retrocede. Cargado, se le ve la
 * bala en la boca.
 *
 * A quien va subido le pinta ademas la mira (CanonMira): el camino de la bala
 * en puntos de luz y una marca donde caeria; dorada si da en Nerea.
 */
public class CanonNaufragioRenderer extends EntityRenderer<CanonNaufragioEntity, CanonNaufragioRenderer.Estado> {

    static final RenderType TEXTURA = RenderTypes.entityCutout(
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "textures/entity/nerea/canon.png"));
    // Las regiones de canon.png (nerea_minijuegos.py), para MorenaDibujo.caja.
    private static final int[] BRONCE = {0, 0, 32, 8};
    private static final int[] ARO = {32, 0, 8, 8};
    private static final int[] BOCA = {40, 0, 8, 8};
    private static final int[] HIERRO = {48, 0, 8, 8};
    private static final int[] PERCEBES = {56, 0, 8, 8};
    private static final int[] MADERA = {0, 8, 32, 8};
    private static final int[] VETA = {32, 8, 8, 8};
    private static final int[] RUEDA = {0, 16, 16, 16};
    private static final int[] ALGA = {16, 16, 8, 16};
    private static final int[] CUERDA = {24, 16, 8, 8};
    private static final int[] VERDIN_T = {32, 16, 8, 8};

    public static class Estado extends EntityRenderState {
        public float edad;
        public float rumbo;
        public float alza;
        public float sale;
        public float retroceso;
        public boolean cargado;
        /** Solo para quien va subido: el camino de la bala (desde la entidad) y donde acaba. */
        public List<Vec3> camino = List.of();
        public Vec3 impacto;
        public boolean enNerea;
    }

    public CanonNaufragioRenderer(EntityRendererProvider.Context contexto) {
        super(contexto);
    }

    @Override
    public Estado createRenderState() {
        return new Estado();
    }

    @Override
    public void extractRenderState(CanonNaufragioEntity c, Estado s, float parcial) {
        super.extractRenderState(c, s, parcial);
        s.edad = c.tickCount + parcial;
        s.rumbo = Mth.rotLerp(parcial, c.yRotO, c.getYRot());
        s.alza = c.alza();
        float sale = Mth.clamp(s.edad / CanonNaufragioEntity.SALE, 0.0F, 1.0F);
        if (c.hunde() >= 0) {
            sale = Math.min(sale, Mth.clamp(1.0F - (s.edad - c.hunde()) / CanonNaufragioEntity.SALE, 0.0F, 1.0F));
        }
        s.sale = sale;
        float d = s.edad - c.ultimoDisparo();
        s.retroceso = d >= 0 && d < 8 ? 0.35F * (1.0F - d / 8.0F) : 0.0F;
        s.cargado = c.cargado();
        s.camino = List.of();
        s.impacto = null;
        Minecraft mc = Minecraft.getInstance();
        if (mc.player != null && c.getFirstPassenger() == mc.player && c.hunde() < 0) {
            CanonMira.calcular(c, mc.player, parcial);
            Vec3 o = c.getPosition(parcial);
            s.camino = CanonMira.puntos().stream().map(q -> q.subtract(o)).toList();
            Vec3 i = CanonMira.impacto();
            s.impacto = i == null ? null : i.subtract(o);
            s.enNerea = CanonMira.enNerea();
        }
    }

    @Override
    protected boolean affectedByCulling(CanonNaufragioEntity c) {
        return false;
    }

    @Override
    public void submit(Estado s, PoseStack pose, SubmitNodeCollector colector, CameraRenderState camara) {
        int luz = s.lightCoords;
        colector.submitCustomGeometry(pose, TEXTURA, (p, buf) -> canon(buf, p, s, luz));
        if (s.cargado) {
            // La bala en la boca, redonda, asomando.
            colector.submitCustomGeometry(pose, BalaDibujo.HIERRO, (p, buf) -> BalaDibujo.bola(buf, p, boca(s, 1.5), 0.17,
                    0.0F, 0.0F, luz));
        }
        if (!s.camino.isEmpty()) {
            mira(s, pose, colector, camara);
        }
        super.submit(s, pose, colector, camara);
    }

    /** La mira de quien va subido: un punto de luz cada medio bloque del camino y la marca del impacto. */
    private static void mira(Estado s, PoseStack pose, SubmitNodeCollector colector, CameraRenderState camara) {
        Vec3 ojo = camara.pos.subtract(s.x, s.y, s.z);
        int color = s.enNerea ? 0xFFD24A : 0xDDF6FF;
        List<Vec3> camino = s.camino;
        float e = s.edad;
        colector.order(1).submitCustomGeometry(pose, NereaDibujo.CORAZON, (p, buf) -> {
            double resto = 0.0;
            double paso = 0.6;
            double recorrido = 0.0;
            for (int i = 1; i < camino.size(); i++) {
                Vec3 a = camino.get(i - 1);
                Vec3 b = camino.get(i);
                double largo = a.distanceTo(b);
                double en = resto;
                while (en < largo) {
                    Vec3 q = a.lerp(b, en / largo);
                    double d = recorrido + en;
                    // Los primeros, que estan junto a los ojos, no: taparian la vista.
                    if (d > 2.5) {
                        // Se mueven hacia delante, como si el camino corriera hacia el blanco.
                        float late = 0.06F + 0.03F * Mth.sin((float) (d * 1.3 - e * 0.5));
                        NereaDibujo.cartel(buf, p, q, ojo, late, 0.0F, color, 200);
                    }
                    en += paso;
                }
                resto = en - largo;
                recorrido += largo;
            }
            if (s.impacto != null) {
                float m = s.enNerea ? 0.55F + 0.1F * Mth.sin(e * 0.6F) : 0.35F;
                NereaDibujo.cartel(buf, p, s.impacto, ojo, m, e * 0.05F, color, 255);
            }
        });
        if (s.impacto != null && !s.enNerea) {
            // En el suelo, un aro donde caeria.
            Vec3 i = s.impacto;
            colector.order(1).submitCustomGeometry(pose, NereaDibujo.ARO, (p, buf) ->
                    NereaDibujo.suelo(buf, p, i.x, i.y + 0.05, i.z, 0.7F / NereaDibujo.ARO_EN_TEXTURA, e * 0.05F, 0xDDF6FF, 200));
        }
    }

    /** Un punto del eje del canon, a "largo" del munon (con el alza, el retroceso y lo que asoma del suelo). */
    private static Vec3 boca(Estado s, double largo) {
        double baja = -1.6 * (1.0 - s.sale * s.sale * (3 - 2 * s.sale));
        Vec3 f = CajaDibujo.rumbo(new Vec3(0, 0, 1), s.rumbo);
        Vec3 u = new Vec3(0, 1, 0);
        double a = s.alza * Mth.DEG_TO_RAD;
        Vec3 eje = f.scale(Math.cos(a)).add(u.scale(Math.sin(a)));
        Vec3 munon = new Vec3(0, baja, 0).add(u.scale(0.9)).subtract(eje.scale(s.retroceso));
        return munon.add(eje.scale(largo));
    }

    /**
     * El canon, de cajas con la textura de canon.png (Juan: "mejora el diseno, se
     * ve muy simple"): la cureña de barco de tablas mojadas, escalonada como las de
     * verdad, con sus ejes, el travesano y cuatro ruedas de radios; el canon de
     * bronce verdeado de ocho caras (dos cajas cruzadas por tramo), mas grueso en la
     * recamara, con sus anillos, el brocal de la boca, el cascabel de atras, los
     * munones y sus sobremunoneras de hierro; y lo del naufragio: percebes en el
     * bronce, algas que cuelgan y se mecen, y un rollo de cabo en la cureña.
     */
    private static void canon(VertexConsumer buf, PoseStack.Pose p, Estado s, int luz) {
        double baja = -1.6 * (1.0 - s.sale * s.sale * (3 - 2 * s.sale));
        Vec3 f = CajaDibujo.rumbo(new Vec3(0, 0, 1), s.rumbo);
        Vec3 r = CajaDibujo.rumbo(new Vec3(1, 0, 0), s.rumbo);
        Vec3 u = new Vec3(0, 1, 0);
        Vec3 o = new Vec3(0, baja, 0);
        int b = 0xFFFFFF;
        int ov = OverlayTexture.NO_OVERLAY;
        // La cureña: cada costado en tres escalones de tablon, mas alto donde apoyan los munones.
        double[][] escalones = {{-0.9, 0.9, 0.22, 0.5}, {-0.62, 0.55, 0.5, 0.68}, {-0.32, 0.3, 0.68, 0.84}};
        for (int lado = -1; lado <= 1; lado += 2) {
            for (double[] e : escalones) {
                Vec3 c = o.add(r.scale(0.36 * lado)).add(f.scale((e[0] + e[1]) / 2)).add(u.scale((e[2] + e[3]) / 2));
                MorenaDibujo.caja(buf, p, c, f.scale((e[1] - e[0]) / 2), r.scale(0.075), u.scale((e[3] - e[2]) / 2),
                        MADERA, MADERA, MADERA, VETA, VETA, b, luz, ov);
            }
            // El fleje de hierro que abraza cada costado.
            for (double fz : new double[]{-0.5, 0.42}) {
                Vec3 c = o.add(r.scale(0.36 * lado)).add(f.scale(fz)).add(u.scale(0.45));
                MorenaDibujo.caja(buf, p, c, f.scale(0.035), r.scale(0.085), u.scale(0.2), HIERRO, HIERRO, HIERRO, HIERRO, HIERRO, b, luz, ov);
            }
        }
        // Los ejes, el travesano de delante y la cuna de la recamara.
        for (double fz : new double[]{-0.6, 0.6}) {
            MorenaDibujo.caja(buf, p, o.add(f.scale(fz)).add(u.scale(0.27)), f.scale(0.08), r.scale(0.66), u.scale(0.07),
                    VETA, MADERA, MADERA, MADERA, MADERA, b, luz, ov);
        }
        MorenaDibujo.caja(buf, p, o.add(f.scale(0.8)).add(u.scale(0.42)), f.scale(0.06), r.scale(0.3), u.scale(0.12),
                MADERA, MADERA, MADERA, MADERA, MADERA, b, luz, ov);
        MorenaDibujo.caja(buf, p, o.add(f.scale(-0.58)).add(u.scale(0.58)), f.scale(0.2), r.scale(0.22), u.scale(0.07),
                MADERA, MADERA, MADERA, VETA, VETA, b, luz, ov);
        // Las ruedas: un disco de radios (lo de entre radios no se pinta) y su cubo.
        for (int lado = -1; lado <= 1; lado += 2) {
            for (double fz : new double[]{-0.6, 0.6}) {
                Vec3 c = o.add(r.scale(0.6 * lado)).add(f.scale(fz)).add(u.scale(0.27));
                // Dos caras de rueda (por fuera y por dentro): asi se ve redonda y con huecos, sin caja alrededor.
                for (int cara = -1; cara <= 1; cara += 2) {
                    MorenaDibujo.cara(buf, p, c.add(r.scale(0.05 * cara)), f.scale(0.27), u.scale(0.27), r.scale(cara), RUEDA, b, luz, ov);
                }
                MorenaDibujo.caja(buf, p, c.add(r.scale(0.06 * lado)), f.scale(0.06), r.scale(0.04), u.scale(0.06),
                        HIERRO, HIERRO, HIERRO, HIERRO, HIERRO, b, luz, ov);
            }
        }
        // El rollo de cabo, atras en la cureña.
        MorenaDibujo.caja(buf, p, o.add(f.scale(-0.78)).add(u.scale(0.56)).add(r.scale(0.2)), f.scale(0.1), r.scale(0.1), u.scale(0.06),
                CUERDA, CUERDA, CUERDA, CUERDA, CUERDA, b, luz, ov);
        // El canon: gira con el alza alrededor de los munones.
        double a = s.alza * Mth.DEG_TO_RAD;
        Vec3 eje = f.scale(Math.cos(a)).add(u.scale(Math.sin(a)));
        Vec3 arr = u.scale(Math.cos(a)).subtract(f.scale(Math.sin(a)));
        Vec3 munon = o.add(u.scale(0.9)).subtract(eje.scale(s.retroceso));
        // Los tramos (desde el munon, a lo largo del eje): recamara, refuerzo, caña y brocal; de ocho caras.
        double[][] tramos = {{-0.78, -0.12, 0.3}, {-0.12, 0.55, 0.265}, {0.55, 1.35, 0.225}, {1.35, 1.52, 0.27}};
        for (double[] t : tramos) {
            octogono(buf, p, munon.add(eje.scale((t[0] + t[1]) / 2)), eje.scale((t[1] - t[0]) / 2), r, arr, t[2],
                    t == tramos[3] ? BOCA : ARO, luz);
        }
        // Los anillos de refuerzo.
        for (double[] an : new double[][]{{-0.78, 0.33}, {-0.12, 0.31}, {0.55, 0.285}, {1.3, 0.25}}) {
            octogono(buf, p, munon.add(eje.scale(an[0])), eje.scale(0.04), r, arr, an[1], ARO, luz);
        }
        // El cascabel de atras y su cuello.
        MorenaDibujo.caja(buf, p, munon.add(eje.scale(-0.86)), eje.scale(0.06), r.scale(0.12), arr.scale(0.12),
                ARO, ARO, ARO, ARO, ARO, b, luz, ov);
        MorenaDibujo.caja(buf, p, munon.add(eje.scale(-0.97)), eje.scale(0.06), r.scale(0.08), arr.scale(0.08),
                BRONCE, BRONCE, BRONCE, ARO, ARO, b, luz, ov);
        // El oido (la mecha) arriba de la recamara.
        MorenaDibujo.caja(buf, p, munon.add(eje.scale(-0.55)).add(arr.scale(0.31)), eje.scale(0.04), r.scale(0.04), arr.scale(0.03),
                HIERRO, HIERRO, HIERRO, HIERRO, HIERRO, b, luz, ov);
        // Los munones y las sobremunoneras de hierro, sobre los costados.
        MorenaDibujo.caja(buf, p, munon, f.scale(0.08), r.scale(0.44), u.scale(0.08), ARO, ARO, ARO, ARO, ARO, b, luz, ov);
        for (int lado = -1; lado <= 1; lado += 2) {
            MorenaDibujo.caja(buf, p, o.add(u.scale(0.97)).add(r.scale(0.36 * lado)), f.scale(0.11), r.scale(0.09), u.scale(0.025),
                    HIERRO, HIERRO, HIERRO, HIERRO, HIERRO, b, luz, ov);
        }
        // Percebes pegados al bronce.
        double[][] percebes = {{0.2, 0.28, 0.6}, {0.95, 0.24, -0.4}, {-0.4, 0.31, -0.7}};
        for (double[] pc : percebes) {
            Vec3 c = munon.add(eje.scale(pc[0])).add(arr.scale(pc[1] * 0.92)).add(r.scale(pc[1] * pc[2] * 0.4));
            MorenaDibujo.caja(buf, p, c, eje.scale(0.06), r.scale(0.06), arr.scale(0.035), PERCEBES, PERCEBES, PERCEBES, PERCEBES,
                    PERCEBES, b, luz, ov);
        }
        // Algas que cuelgan de la caña y de la cureña, meciendose.
        double[][] algas = {{0.85, -0.2, 0.55}, {1.1, 0.15, 0.45}, {-0.2, 0.0, 0.5}};
        for (int i = 0; i < algas.length; i++) {
            double[] al = algas[i];
            Vec3 arriba = i < 2 ? munon.add(eje.scale(al[0])).add(r.scale(al[1])).subtract(arr.scale(0.2))
                    : o.add(f.scale(0.75)).add(r.scale(0.36 * (i == 2 ? 1 : -1))).add(u.scale(0.48));
            double mece = 0.12 * Math.sin(s.edad * 0.12 + i * 2.1);
            Vec3 abajo = arriba.add(new Vec3(0, -al[2], 0)).add(f.scale(mece));
            Vec3 centro = arriba.add(abajo).scale(0.5);
            Vec3 largo = abajo.subtract(arriba).scale(-0.5);
            MorenaDibujo.cara(buf, p, centro, r.scale(0.06), largo, f, ALGA, b, luz, ov);
            MorenaDibujo.cara(buf, p, centro, r.scale(0.06), largo, f.scale(-1), ALGA, b, luz, ov);
        }
    }

    /** Un tramo de ocho caras: dos cajas cruzadas a 45 grados alrededor del eje. */
    private static void octogono(VertexConsumer buf, PoseStack.Pose p, Vec3 c, Vec3 medio, Vec3 r, Vec3 arr, double radio,
                                 int[] puntas, int luz) {
        int ov = OverlayTexture.NO_OVERLAY;
        MorenaDibujo.caja(buf, p, c, medio, r.scale(radio), arr.scale(radio), BRONCE, BRONCE, VERDIN_T, puntas, ARO, 0xFFFFFF, luz, ov);
        double k = radio * 0.98;
        Vec3 d1 = r.add(arr).normalize();
        Vec3 d2 = arr.subtract(r).normalize();
        MorenaDibujo.caja(buf, p, c, medio, d1.scale(k), d2.scale(k), BRONCE, BRONCE, VERDIN_T, puntas, ARO, 0xFFFFFF, luz, ov);
    }
}
