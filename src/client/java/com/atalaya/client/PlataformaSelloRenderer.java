package com.atalaya.client;

import com.atalaya.Atalaya;
import com.atalaya.entity.PlataformaSelloEntity;
import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.math.Axis;
import net.minecraft.client.renderer.SubmitNodeCollector;
import net.minecraft.client.renderer.entity.EntityRenderer;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.state.EntityRenderState;
import net.minecraft.client.renderer.rendertype.RenderType;
import net.minecraft.client.renderer.rendertype.RenderTypes;
import net.minecraft.client.renderer.state.level.CameraRenderState;
import net.minecraft.resources.Identifier;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Random;

/**
 * Las piezas del Sello de la Tierra, en bloques de roca hechos a mano:
 *
 *   - la columna: capas de dos bloques de roca a soga y tizon, cada uno algo
 *     torcido, con salientes, cristales de jade clavados y los terrones del
 *     pie; arriba, la losa con la hierba y la hierba que cuelga por los
 *     lados. Sube desde el suelo a empellones y al final se hunde;
 *   - la piedra: la losa con hierba y, debajo, la roca que se estrecha como
 *     si la hubieran arrancado del suelo, con un cristal colgando. Sube
 *     volando y girando a su sitio y al final se desmorona.
 *
 * Lo de arriba (la hierba) coincide con la caja de choque: se pisa donde se ve.
 */
public class PlataformaSelloRenderer extends EntityRenderer<PlataformaSelloEntity, PlataformaSelloRenderer.Estado> {

    private static final RenderType ROCA = RenderTypes.entityCutout(tex("roca"));
    private static final RenderType VETAS = RenderTypes.eyes(tex("roca_brillo"));
    private static final RenderType CESPED = RenderTypes.entityCutout(tex("cesped"));
    private static final RenderType BORDE = RenderTypes.entityCutout(tex("cesped_borde"));
    private static final RenderType JADE = RenderTypes.entityCutout(tex("fragmento"));
    private static final RenderType JADE_BRILLO = RenderTypes.eyes(tex("fragmento_brillo"));

    private static Identifier tex(String nombre) {
        return Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "textures/entity/rajang/" + nombre + ".png");
    }

    public static class Estado extends EntityRenderState {
        public float edad;
        public int tipo;
        public float ancho;
        public float alto;
        public int semilla;
        public int nace;
        public int seVa;
        public float vuelo;
    }

    /** La geometria de una pieza (sale de su semilla: se calcula una vez). */
    private record Piezas(List<RajangDibujo.Cara> roca, List<RajangDibujo.Cara> cesped, List<RajangDibujo.Cara> borde,
                          List<RajangDibujo.Cara> jade) {
    }

    private final Map<Long, Piezas> cache = new HashMap<>();

    public PlataformaSelloRenderer(EntityRendererProvider.Context contexto) {
        super(contexto);
    }

    @Override
    public Estado createRenderState() {
        return new Estado();
    }

    @Override
    public void extractRenderState(PlataformaSelloEntity p, Estado s, float parcial) {
        super.extractRenderState(p, s, parcial);
        s.edad = p.tickCount + parcial;
        s.tipo = p.getTipo();
        s.ancho = p.getAncho();
        s.alto = p.getAlto();
        s.semilla = p.getSemilla();
        s.nace = p.getNace();
        s.seVa = p.getSeVa();
        s.vuelo = p.getVuelo();
    }

    @Override
    protected boolean affectedByCulling(PlataformaSelloEntity p) {
        return false;
    }

    @Override
    public void submit(Estado s, PoseStack pose, SubmitNodeCollector colector, CameraRenderState camara) {
        float k = PlataformaSelloEntity.salida(s.tipo, s.edad, s.nace, s.seVa);
        if (s.tipo == PlataformaSelloEntity.TRAMO || k <= 0.001F) {
            return;
        }
        Piezas g = piezas(s);
        boolean seVa = s.seVa >= 0 && s.edad >= s.seVa;
        pose.pushPose();
        if (s.tipo == PlataformaSelloEntity.COLUMNA) {
            pose.translate(0.0, -s.alto * (1.0F - k), 0.0);
        } else if (seVa) {
            // Se desmorona: cae y se encoge.
            float c = 1.0F - k;
            pose.translate(0.0, -3.0F * c * c - 0.4F * c, 0.0);
            pose.scale(0.4F + 0.6F * k, 0.4F + 0.6F * k, 0.4F + 0.6F * k);
        } else if (k < 1.0F) {
            // Sube volando desde el suelo, girando.
            pose.translate(0.0, -s.vuelo * (1.0F - k), 0.0);
            pose.mulPose(Axis.YP.rotationDegrees(220.0F * (1.0F - k)));
        }
        int luz = s.lightCoords;
        colector.submitCustomGeometry(pose, ROCA, (p, buf) -> RajangDibujo.emitir(buf, p, g.roca(), 255, 255, 255, 255, luz));
        colector.submitCustomGeometry(pose, VETAS, (p, buf) ->
                RajangDibujo.emitir(buf, p, g.roca(), 170, 170, 170, 255, AeralisDibujo.A_PLENA_LUZ));
        colector.submitCustomGeometry(pose, CESPED, (p, buf) -> RajangDibujo.emitir(buf, p, g.cesped(), 255, 255, 255, 255, luz));
        colector.submitCustomGeometry(pose, BORDE, (p, buf) -> RajangDibujo.emitir(buf, p, g.borde(), 255, 255, 255, 255, luz));
        if (!g.jade().isEmpty()) {
            colector.submitCustomGeometry(pose, JADE, (p, buf) -> RajangDibujo.emitir(buf, p, g.jade(), 255, 255, 255, 255, luz));
            int b = (int) (200 + 55 * Math.sin(s.edad * 0.12F));
            colector.submitCustomGeometry(pose, JADE_BRILLO, (p, buf) ->
                    RajangDibujo.emitir(buf, p, g.jade(), b, b, b, 255, AeralisDibujo.A_PLENA_LUZ));
        }
        pose.popPose();
        super.submit(s, pose, colector, camara);
    }

    private Piezas piezas(Estado s) {
        long clave = ((long) s.semilla << 2) | s.tipo;
        Piezas g = cache.get(clave);
        if (g == null) {
            if (cache.size() > 96) {
                cache.clear();
            }
            g = s.tipo == PlataformaSelloEntity.COLUMNA ? columna(s.semilla, s.ancho, s.alto) : piedra(s.semilla, s.ancho);
            cache.put(clave, g);
        }
        return g;
    }

    /** La columna: capas a soga y tizon, salientes, cristales, terrones al pie y la losa con hierba. */
    private static Piezas columna(int semilla, float ancho, float alto) {
        Random r = new Random(semilla);
        Piezas g = new Piezas(new ArrayList<>(), new ArrayList<>(), new ArrayList<>(), new ArrayList<>());
        double m = ancho / 2.0;
        double tope = alto - 0.9;
        double y = -1.2;
        int capa = 0;
        while (y < tope - 0.25) {
            double h = Math.min(tope - y, 1.1 + r.nextDouble() * 0.6);
            if (tope - y - h < 0.6) {
                h = tope - y;
            }
            boolean enX = capa % 2 == 0;
            double corte = (r.nextDouble() - 0.5) * m * 0.5;
            for (int lado = -1; lado <= 1; lado += 2) {
                double a0 = lado < 0 ? -m : corte;
                double a1 = lado < 0 ? corte : m;
                double medio = (a1 - a0) / 2 * (0.96 + r.nextDouble() * 0.06);
                double centro = (a0 + a1) / 2;
                double otro = m * (0.9 + r.nextDouble() * 0.1);
                double fuera = (r.nextDouble() - 0.5) * 0.14;
                double gy = (r.nextDouble() - 0.5) * 9;
                if (enX) {
                    RajangDibujo.bloque(g.roca(), null, r, centro, y + h / 2, fuera, medio, h / 2 * 1.03, otro, 0.08,
                            (r.nextDouble() - 0.5) * 3, gy, (r.nextDouble() - 0.5) * 3, 12, 32, 64);
                } else {
                    RajangDibujo.bloque(g.roca(), null, r, fuera, y + h / 2, centro, otro, h / 2 * 1.03, medio, 0.08,
                            (r.nextDouble() - 0.5) * 3, gy, (r.nextDouble() - 0.5) * 3, 12, 32, 64);
                }
            }
            // Salientes: alguna roca que asoma por los lados.
            int n = r.nextInt(3);
            for (int i = 0; i < n; i++) {
                double a = r.nextDouble() * Math.PI * 2;
                double t = 0.3 + r.nextDouble() * 0.3;
                RajangDibujo.bloque(g.roca(), null, r, Math.cos(a) * m * 0.92, y + h * r.nextDouble(), Math.sin(a) * m * 0.92,
                        t, t * (0.6 + r.nextDouble() * 0.4), t, 0.2, (r.nextDouble() - 0.5) * 30, r.nextDouble() * 90,
                        (r.nextDouble() - 0.5) * 30, 12, 32, 64);
            }
            y += h;
            capa++;
        }
        // Los cristales de jade clavados en la roca, apuntando hacia fuera y arriba.
        int cristales = 3 + r.nextInt(2);
        for (int i = 0; i < cristales; i++) {
            double a = (i + r.nextDouble() * 0.6) / cristales * Math.PI * 2;
            double cy = 2.5 + r.nextDouble() * (alto - 5.5);
            cristal(g.jade(), r, Math.cos(a) * m * 0.95, cy, Math.sin(a) * m * 0.95, a, 0.6 + r.nextDouble() * 0.4);
        }
        // La losa de arriba, recta (la caja de choque) y con la hierba.
        RajangDibujo.bloque(g.roca(), g.cesped(), r, 0, alto - 0.45, 0, m, 0.45, m, 0.0, 0, 0, 0, 12, 32, 64);
        RajangDibujo.borde(g.borde(), m, alto, 1.0);
        // Los terrones del suelo roto, al pie.
        for (int i = 0; i < 9; i++) {
            double a = r.nextDouble() * Math.PI * 2;
            double d = m + 0.3 + r.nextDouble() * 1.1;
            double t = 0.25 + r.nextDouble() * 0.3;
            RajangDibujo.bloque(g.roca(), null, r, Math.cos(a) * d, t * 0.35, Math.sin(a) * d, t, t * 0.7, t * (0.8 + r.nextDouble() * 0.3),
                    0.2, (r.nextDouble() - 0.5) * 40, r.nextDouble() * 90, (r.nextDouble() - 0.5) * 40, 12, 32, 64);
        }
        return g;
    }

    /** La piedra del parkour: la losa con hierba y la roca que cuelga debajo, con un cristal. */
    private static Piezas piedra(int semilla, float ancho) {
        Random r = new Random(semilla);
        Piezas g = new Piezas(new ArrayList<>(), new ArrayList<>(), new ArrayList<>(), new ArrayList<>());
        double m = ancho / 2.0;
        float grueso = PlataformaSelloEntity.GRUESO;
        RajangDibujo.bloque(g.roca(), g.cesped(), r, 0, grueso / 2.0, 0, m, grueso / 2.0, m, 0.0, 0, 0, 0, 12, 32, 64);
        RajangDibujo.borde(g.borde(), m, grueso, 0.75);
        double y = 0.02;
        double ox = 0;
        double oz = 0;
        double[] anchos = {0.82, 0.58, 0.34};
        double[] altos = {0.34, 0.3, 0.26};
        for (int i = 0; i < 3; i++) {
            double h = altos[i] * (0.9 + r.nextDouble() * 0.3);
            double w = m * anchos[i] * (0.9 + r.nextDouble() * 0.2);
            ox += (r.nextDouble() - 0.5) * 0.18;
            oz += (r.nextDouble() - 0.5) * 0.18;
            RajangDibujo.bloque(g.roca(), null, r, ox, y - h, oz, w, h, w * (0.8 + r.nextDouble() * 0.3), 0.12,
                    (r.nextDouble() - 0.5) * 8, r.nextDouble() * 90, (r.nextDouble() - 0.5) * 8, 12, 32, 64);
            y -= h * 1.7;
        }
        // El cristal que cuelga de la punta (y alguna raiz de terron suelto).
        double t = 0.09 + r.nextDouble() * 0.04;
        RajangDibujo.bloque(g.jade(), null, r, ox, y - 0.18, oz, t, 0.24, t, 0.05, (r.nextDouble() - 0.5) * 16,
                r.nextDouble() * 90, (r.nextDouble() - 0.5) * 16, 16, 32, 32);
        return g;
    }

    /** Un racimo de dos o tres cristales de jade en bloque, abiertos hacia fuera (a: angulo de la cara). */
    private static void cristal(List<RajangDibujo.Cara> out, Random r, double x, double y, double z, double a, double tam) {
        int n = 2 + r.nextInt(2);
        double gy = -Math.toDegrees(a) + 90;
        for (int i = 0; i < n; i++) {
            double largo = tam * (i == 0 ? 1.0 : 0.55 + r.nextDouble() * 0.3);
            double grueso = largo * 0.22;
            double inclina = 35 + r.nextDouble() * 25;
            double abre = (i - (n - 1) / 2.0) * 22;
            // El cristal sale de la pared: el centro va medio largo hacia fuera de donde nace.
            double ex = Math.cos(a) * Math.sin(Math.toRadians(inclina)) * largo * 0.5;
            double ez = Math.sin(a) * Math.sin(Math.toRadians(inclina)) * largo * 0.5;
            double ey = Math.cos(Math.toRadians(inclina)) * largo * 0.5;
            RajangDibujo.bloque(out, null, r, x + ex, y + ey + i * 0.15, z + ez, grueso, largo / 2, grueso, 0.05,
                    -inclina, gy + abre, 0, 16, 32, 32);
        }
    }
}
