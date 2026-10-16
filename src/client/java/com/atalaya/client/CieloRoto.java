package com.atalaya.client;

import com.atalaya.Atalaya;
import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import net.fabricmc.fabric.api.client.rendering.v1.level.LevelRenderContext;
import net.fabricmc.fabric.api.client.rendering.v1.level.LevelRenderEvents;
import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.rendertype.RenderType;
import net.minecraft.client.renderer.rendertype.RenderTypes;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.resources.Identifier;
import net.minecraft.util.Mth;
import org.joml.Vector3fc;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Random;

/**
 * El cielo que se rompe en el Momento Fractura (Juan, 15-10-2026: "el cielo
 * esta god... podrias hacer que el cielo se este fracturando"; 16-10-2026, con
 * fotos de cristales con un impacto: "en el centro arriba sea el unico hueco y
 * nada mas"; "las grietas se ven raras, puedes hacer algo asi").
 *
 * Es un cristal golpeado justo encima de cada jugador: en el cenit, un solo
 * hueco pequeño, casi redondo y apenas dentado; de cada una de sus puntas sale
 * una grieta fina (unas doce; Juan: "que de cada punto del hueco salga una
 * grieta, debes ser fiel a una ruptura"; "has hecho muchas puntas, sigue la
 * referencia"), cada una a su aire: curvas, de largos distintos (alguna casi
 * hasta el horizonte), alguna partida en dos; y unos pocos arcos sueltos unen
 * dos de ellas. Nada de telaraña regular. Con la
 * fractura se rajan del centro hacia fuera; por ellas corren ondas de luz y todo
 * late con el corazon de la musica.
 *
 * Por el hueco se ve otro sitio, sin hondura (Juan: "negros y gris, no morado";
 * "quitemos la profundidad del hueco"): negro, con una niebla gris que se mueve
 * despacio en dos capas. Desde dentro
 * miran unos ojos: cuadrados rojos lisos (Juan, con una imagen de dos cuadrados
 * rojos en lo negro: "no quiero algo detallado sino cuadrados rojos"), que
 * aparecen poco a poco, parpadean y miran a los lados; detras de cada par, su
 * cuerpo, una silueta casi negra que apenas se adivina (Juan: "que no se vea,
 * solo que se note un poco, dando ese misterio"). Giran con el jugador: siempre
 * los ve derechos.
 *
 * Al pararlo, todo se cierra hacia el centro.
 *
 * Son cintas y abanicos emisivos en una cupula alrededor de la camara (se
 * mueven con ella: parecen estar infinitamente lejos), con una sola hoja
 * (textures/entity/momento/cielo.png, momento_maldicion.py).
 */
public final class CieloRoto {

    private static final RenderType CIELO = RenderTypes.entityTranslucentEmissive(
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "textures/entity/momento/cielo.png"));
    /** Las partes de la hoja (en UV): el blanco liso, la cinta de las grietas y la niebla. */
    private static final float LISO_U = 0.75F;
    private static final float LISO_V = 0.3125F;
    private static final float CINTA_U0 = 0.502F;
    private static final float CINTA_U1 = 0.998F;
    private static final float CINTA_V0 = 0.127F;
    private static final float CINTA_V1 = 0.248F;
    private static final float NIEBLA_V0 = 0.125F;
    /** El radio de la cupula (bloques): dentro de la niebla del cielo maldito. */
    private static final float RADIO = 42.0F;
    private static final int A_PLENA_LUZ = 0xF000F0;
    /** Las grietas van un pelo por delante de lo demas. */
    private static final float DELANTE = 0.992F;
    /**
     * Lo de dentro del hueco (el negro y la niebla), mas cerca: a la distancia de las grietas, la niebla
     * roja del cielo lo teñia de granate. Los ojos, aun mas.
     */
    private static final float HONDO = 0.5F;
    private static final float CERCA = 0.45F;
    /** Lo que mide el hueco (grados desde el cenit; el borde va dentado alrededor) y las grietas que salen de el. */
    private static final float HUECO = 9.0F;
    private static final int GRIETAS = 12;

    private static long semilla = Long.MIN_VALUE;

    /** El borde del hueco: rumbo (radianes) y grados de cada punto, alrededor. */
    private static float[][] borde = new float[0][];
    /**
     * Las grietas: x0, y0, z0, x1, y1, z1, cuando se abre (0 a 1), grosor, la distancia al cenit (para las ondas) y su
     * luz (de 0 a 1).
     */
    private static float[][] tramos = new float[0][];
    /**
     * Los pares de ojos: x, y (grados desde el cenit, en el plano del hueco), lo que mide un cuadrado (grados), cuando
     * aparecen (ticks maldito) y su parpadeo y su mirada.
     */
    private static float[][] ojos = new float[0][];
    /** La derecha de la pantalla del jugador, en horizontal (para girar los ojos con el). */
    private static float[] derecha = {1, 0, 0};

    private CieloRoto() {
    }

    public static void registrar() {
        LevelRenderEvents.COLLECT_SUBMITS.register(CieloRoto::pintar);
    }

    private static void pintar(LevelRenderContext ctx) {
        Minecraft mc = Minecraft.getInstance();
        float parcial = mc.getDeltaTracker().getGameTimeDeltaPartialTick(false);
        float abierto = MomentoMaldicionCliente.grietasCielo(parcial);
        if (abierto <= 0) {
            return;
        }
        long s = MomentoMaldicionCliente.semilla();
        if (s != semilla) {
            semilla = s;
            preparar(s);
        }
        float late = MomentoMaldicionCliente.latido(parcial);
        float destello = MomentoMaldicionCliente.destelloCielo(parcial);
        float reloj = MomentoMaldicionCliente.relojCielo(parcial);
        float maldito = MomentoMaldicionCliente.malditoCielo(parcial);
        Vector3fc f = mc.gameRenderer.mainCamera().forwardVector();
        // La derecha sale del vector izquierdo de la camara (siempre horizontal, aunque se mire justo arriba).
        Vector3fc izq = mc.gameRenderer.mainCamera().leftVector();
        float h = (float) Math.hypot(izq.x(), izq.z());
        if (h > 1.0E-3F) {
            derecha = new float[]{-izq.x() / h, 0, -izq.z() / h};
        }
        boolean mirando = f.y() > 0.9F;
        ctx.submitNodeCollector().submitCustomGeometry(ctx.poseStack(), CIELO, (p, buf) -> {
            // El hueco, lo que se ve por el y los ojos que miran desde dentro.
            hueco(buf, p, abierto, reloj);
            ojos(buf, p, abierto, reloj, late, maldito, mirando);
            // Las grietas, finas, con las ondas de luz que salen del centro.
            float onda = (reloj / 40.0F) % 1.0F;
            for (float[] q : tramos) {
                if (q[6] > abierto) {
                    continue;
                }
                float nuevo = Mth.clamp(1.0F - (abierto - q[6]) * 5.0F, 0.0F, 1.0F);
                float pulso = (float) Math.exp(-Math.pow((q[8] - onda) / 0.06F, 2))
                        + 0.6F * (float) Math.exp(-Math.pow((q[8] - (onda + 0.5F) % 1.0F) / 0.05F, 2));
                float g = q[7] * (1.0F + 0.2F * late + 0.5F * pulso);
                float luz = q[9];
                float brillo = Mth.clamp(0.45F + 0.25F * late + 0.55F * pulso + 0.5F * nuevo + 0.4F * destello, 0.0F, 1.0F);
                if (q[7] > 0.5F) {
                    cinta(buf, p, q, g * 3.2F, 0xFF1E10,
                            (int) (255 * luz * Mth.clamp(0.05F + 0.08F * late + 0.15F * pulso + 0.25F * destello, 0, 1)));
                }
                cinta(buf, p, q, g * 1.2F, 0xFF3A20, (int) (230 * luz * brillo));
                cinta(buf, p, q, g * 0.4F, pulso > 0.35F || nuevo > 0.3F || destello > 0.4F ? 0xFFFFFF : 0xFFDCC8,
                        (int) (250 * Math.min(1.0F, luz * 1.3F)));
            }
        });
    }

    // ------------------------------------------------------------------
    //  El hueco
    // ------------------------------------------------------------------

    /** Una direccion de la cupula por rumbo (radianes) y distancia al cenit (grados). */
    private static float[] dir(float rumbo, float grados) {
        float z = (float) Math.toRadians(grados);
        return new float[]{Mth.sin(z) * Mth.cos(rumbo), Mth.cos(z), Mth.sin(z) * Mth.sin(rumbo)};
    }

    /**
     * El hueco del impacto: lo de detras es negro, con una niebla gris que se mueve despacio en dos capas (en el
     * centro, entera; hacia el borde se apaga). Sin hondura (Juan: "quitemos la profundidad del hueco"): ni el grueso
     * del cristal ni el filo rojo de dentro. Se abre desde el centro con la fractura.
     */
    private static void hueco(VertexConsumer buf, PoseStack.Pose p, float abierto, float reloj) {
        float k = Mth.clamp((abierto - 0.05F) * 1.6F, 0.0F, 1.0F);
        if (k <= 0 || borde.length == 0) {
            return;
        }
        int n = borde.length;
        float[][] d = new float[n][];
        for (int i = 0; i < n; i++) {
            d[i] = dir(borde[i][0], borde[i][1] * k);
        }
        float[] c = {0, 1, 0};
        int a = (int) (255 * k);
        // El negro.
        abanico(buf, p, c, d, HONDO, 0x020203, a);
        // La niebla: dos capas que se pasean por la hoja, la de delante mas fina y mas deprisa.
        niebla(buf, p, k, HONDO * 0.999F, 0.25F, 0.125F + 0.125F * Mth.sin(reloj * 0.0021F),
                0.125F + 0.125F * Mth.cos(reloj * 0.0017F), 0x9C9C9C, (int) (165 * k));
        niebla(buf, p, k, HONDO * 0.998F, 0.17F, 0.165F + 0.165F * Mth.sin(-reloj * 0.0033F + 1.0F),
                0.165F + 0.165F * Mth.cos(reloj * 0.0029F + 2.0F), 0xC8C8C8, (int) (95 * k));
    }

    /**
     * Una capa de niebla en el hueco: la hoja de niebla vista por una ventana de 'ventana' (en UV de la hoja) que se
     * pasea por ella (ox, oy); cada punto va a su sitio en la ventana segun su sitio en el hueco. En el centro, entera;
     * en el borde, nada.
     */
    private static void niebla(VertexConsumer buf, PoseStack.Pose p, float k, float r, float ventana, float ox, float oy,
                               int color, int alfa) {
        if (alfa <= 0) {
            return;
        }
        float limite = 0.5F - ventana;
        ox = Mth.clamp(ox, 0, limite);
        oy = Mth.clamp(oy, 0, limite);
        float uc = ox + 0.5F * ventana;
        float vc = NIEBLA_V0 + oy + 0.5F * ventana;
        float maximo = HUECO * 1.5F;
        int cr = (color >> 16) & 255, cg = (color >> 8) & 255, cb = color & 255;
        float R = RADIO * r;
        int n = borde.length;
        for (int i = 0; i < n; i++) {
            float[] a0 = borde[i];
            float[] a1 = borde[(i + 1) % n];
            // La niebla va por dentro del borde (al 80 %), sin pisarse.
            float[] e0 = dir(a0[0], a0[1] * k * 0.8F);
            float[] e1 = dir(a1[0], a1[1] * k * 0.8F);
            float u0 = uc + Mth.cos(a0[0]) * a0[1] * 0.8F / maximo * 0.5F * ventana;
            float v0 = vc + Mth.sin(a0[0]) * a0[1] * 0.8F / maximo * 0.5F * ventana;
            float u1 = uc + Mth.cos(a1[0]) * a1[1] * 0.8F / maximo * 0.5F * ventana;
            float v1 = vc + Mth.sin(a1[0]) * a1[1] * 0.8F / maximo * 0.5F * ventana;
            cara(buf, p, new float[][]{
                    {0, R, 0, uc, vc, alfa},
                    {e0[0] * R, e0[1] * R, e0[2] * R, u0, v0, 0},
                    {e1[0] * R, e1[1] * R, e1[2] * R, u1, v1, 0},
                    {0, R, 0, uc, vc, alfa}}, cr, cg, cb);
        }
    }

    /**
     * La silueta de lo que mira desde el hueco, en pixeles del tamaño de un ojo (un cuadrado rojo): una cabeza con dos
     * cuernos cortos, el cuello y unos hombros que se pierden hacia abajo. Los ojos van en la fila FILA_OJOS, en las
     * columnas 4 y 7, que van vacias: el cuerpo nunca pisa los ojos (el juego no siempre pinta lo de delante encima).
     */
    private static final String[] CUERPO = {
            "..#......#..",
            "..##....##..",
            "..########..",
            "..########..",
            "..########..",
            "..##.##.##..",
            "..########..",
            "...######...",
            "....####....",
            "..########..",
            ".##########.",
            "############",
            "############",
            "############",
    };
    private static final int FILA_OJOS = 5;

    /**
     * Los ojos que miran desde el hueco: pares de cuadrados rojos lisos, con dos cuadrados de hueco entre ellos, y
     * detras su cuerpo, que casi no se ve (Juan: "demosle un cuerpo a los ojos, que no se vea, solo que se note un
     * poco, dando ese misterio"). Aparecen poco a poco, parpadean a su aire y miran a un lado y a otro (la cabeza se
     * gira un poco con ellos, y el cuerpo respira); si el jugador mira arriba, se quedan quietos, mirandole. Van
     * derechos para quien los mira.
     */
    private static void ojos(VertexConsumer buf, PoseStack.Pose p, float abierto, float reloj, float late, float maldito,
                             boolean mirando) {
        // Derecha y arriba en la pantalla de quien mira hacia lo alto.
        float[] e1 = derecha;
        float[] e2 = {-derecha[2], 0, derecha[0]};
        int rojo = (int) (205 + 50 * late);
        // Donde va cada ojo (en el plano del jugador: derecha y arriba), para que ningun cuerpo lo pise: el juego no
        // siempre pinta encima lo que esta delante.
        List<float[]> sitios = new ArrayList<>();
        for (float[] o : ojos) {
            float lado = mirando ? 0 : Mth.clamp(Mth.sin(reloj * 0.012F + o[6]) * 1.6F, -1.0F, 1.0F);
            float respira = Mth.sin(reloj * 0.05F + o[6]) * 0.12F * o[2];
            float u0 = o[0] * e1[0] + o[1] * e1[2];
            float v0 = o[0] * e2[0] + o[1] * e2[2];
            for (int s = -1; s <= 1; s += 2) {
                sitios.add(new float[]{u0 + (s * 1.5F + lado * 0.5F) * o[2], v0 + respira, o[2] / 2});
            }
        }
        for (int pasada = 0; pasada < 2; pasada++) {
            for (float[] o : ojos) {
                ojo(buf, p, o, e1, e2, pasada == 0, abierto, reloj, maldito, mirando, rojo, sitios);
            }
        }
    }

    /** Un par de ojos (o su cuerpo, si 'esCuerpo'). */
    private static void ojo(VertexConsumer buf, PoseStack.Pose p, float[] o, float[] e1, float[] e2, boolean esCuerpo,
                            float abierto, float reloj, float maldito, boolean mirando, int rojo, List<float[]> sitios) {
        float desde = maldito - o[3];
        float k = Mth.clamp(desde / 30.0F, 0.0F, 1.0F) * Mth.clamp((abierto - 0.6F) * 2.5F, 0.0F, 1.0F);
        if (k <= 0) {
            return;
        }
        float lado = mirando ? 0 : Mth.clamp(Mth.sin(reloj * 0.012F + o[6]) * 1.6F, -1.0F, 1.0F);
        float a = o[2];
        if (esCuerpo) {
            cuerpo(buf, p, o, e1, e2, a, lado, reloj, k, sitios);
            return;
        }
        // El parpadeo: los ojos se apagan un momento (el cuerpo sigue ahi).
        float ciclo = (reloj + o[4]) % o[5];
        if (ciclo < 4 || desde < 3) {
            return;
        }
        float respira = Mth.sin(reloj * 0.05F + o[6]) * 0.12F * a;
        for (int s = -1; s <= 1; s += 2) {
            float x = (s * 1.5F + lado * 0.5F) * a;
            float[] centro = {o[0] + e1[0] * x + e2[0] * respira, o[1] + e1[2] * x + e2[2] * respira};
            cuadrado(buf, p, centro, e1, e2, a, rojo, (int) (255 * k));
        }
    }

    /**
     * El cuerpo de un par de ojos: la silueta de CUERPO, casi negra (sobre la niebla gris del hueco se adivina; sobre
     * lo negro, apenas), pixel a pixel, saltandose los que caen encima de cualquier ojo. Hacia abajo y hacia el borde
     * del hueco se pierde.
     */
    private static void cuerpo(VertexConsumer buf, PoseStack.Pose p, float[] o, float[] e1, float[] e2, float a, float lado,
                               float reloj, float k, List<float[]> sitios) {
        // Se mueve con los ojos (la cabeza se gira con la mirada y respira), sin pisarlos.
        float gira = lado * 0.5F * a;
        float respira = Mth.sin(reloj * 0.05F + o[6]) * 0.12F * a;
        float limite = HUECO * 0.78F;
        for (int f = 0; f < CUERPO.length; f++) {
            String fila = CUERPO[f];
            for (int i = 0; i < fila.length(); i++) {
                if (fila.charAt(i) != '#') {
                    continue;
                }
                int i1 = i;
                float x0 = (i - 6) * a + gira, x1 = (i1 - 5) * a + gira;
                float y1 = (FILA_OJOS - f + 0.5F) * a + respira, y0 = y1 - a;
                float mx = (x0 + x1) / 2, my = (y0 + y1) / 2;
                float cx = o[0] + e1[0] * mx + e2[0] * my;
                float cz = o[1] + e1[2] * mx + e2[2] * my;
                // Si cae encima de un ojo (de este o de otro par), ese pixel no se pinta.
                float pu = o[0] * e1[0] + o[1] * e1[2] + mx;
                float pv = o[0] * e2[0] + o[1] * e2[2] + my;
                boolean pisa = false;
                for (float[] q : sitios) {
                    if (Math.abs(pu - q[0]) < a / 2 + q[2] && Math.abs(pv - q[1]) < a / 2 + q[2]) {
                        pisa = true;
                        break;
                    }
                }
                if (pisa) {
                    continue;
                }
                float baja = Mth.clamp((CUERPO.length - 0.5F - f) / 4.5F, 0.0F, 1.0F);
                float borde = Mth.clamp((limite - (float) Math.hypot(cx, cz)) / 2.5F, 0.0F, 1.0F);
                float al = k * baja * borde;
                if (al > 0.01F) {
                    rect(buf, p, o, e1, e2, x0, x1, y0, y1, CERCA * 1.03F, 0x0B090A, (int) (235 * al));
                }
            }
        }
    }

    /**
     * Un rectangulo de color liso en el plano del cenit: de x0 a x1 (hacia la derecha del jugador) y de y0 a y1 (hacia
     * arriba de su pantalla), en grados, alrededor del centro o (x, z en grados), a 'r' del radio de la cupula.
     */
    private static void rect(VertexConsumer buf, PoseStack.Pose p, float[] o, float[] e1, float[] e2, float x0, float x1, float y0,
                             float y1, float r, int color, int alfa) {
        float R = RADIO * r;
        float[][] es = {{x0, y0}, {x1, y0}, {x1, y1}, {x0, y1}};
        float[][] q = new float[4][];
        for (int i = 0; i < 4; i++) {
            float x = (float) Math.tan(Math.toRadians(o[0] + e1[0] * es[i][0] + e2[0] * es[i][1]));
            float z = (float) Math.tan(Math.toRadians(o[1] + e1[2] * es[i][0] + e2[2] * es[i][1]));
            float l = (float) Math.sqrt(x * x + 1 + z * z);
            q[i] = new float[]{x / l * R, 1 / l * R, z / l * R};
        }
        cara(buf, p, liso(q, alfa), (color >> 16) & 255, (color >> 8) & 255, color & 255);
    }

    /** Un cuadrado rojo de lado 'a' (grados) centrado en (x, z) del plano del cenit (grados), derecho para el jugador. */
    private static void cuadrado(VertexConsumer buf, PoseStack.Pose p, float[] centro, float[] e1, float[] e2, float a, int rojo,
                                 int alfa) {
        float t = (float) Math.tan(Math.toRadians(a / 2));
        float cx = (float) Math.tan(Math.toRadians(centro[0]));
        float cz = (float) Math.tan(Math.toRadians(centro[1]));
        float R = RADIO * CERCA;
        float[][] q = new float[4][];
        float[][] es = {{-1, -1}, {1, -1}, {1, 1}, {-1, 1}};
        for (int i = 0; i < 4; i++) {
            float x = cx + (e1[0] * es[i][0] + e2[0] * es[i][1]) * t;
            float z = cz + (e1[2] * es[i][0] + e2[2] * es[i][1]) * t;
            float l = (float) Math.sqrt(x * x + 1 + z * z);
            q[i] = new float[]{x / l * R, 1 / l * R, z / l * R};
        }
        cara(buf, p, liso(q, alfa), rojo, 10, 8);
    }

    /** Un abanico de un solo color del centro c al borde b, a 'r' del radio de la cupula. */
    private static void abanico(VertexConsumer buf, PoseStack.Pose p, float[] c, float[][] b, float r, int color, int alfa) {
        float R = RADIO * r;
        int cr = (color >> 16) & 255, cg = (color >> 8) & 255, cb = color & 255;
        for (int i = 0; i < b.length; i++) {
            float[] e0 = b[i];
            float[] e1 = b[(i + 1) % b.length];
            cara(buf, p, new float[][]{
                    {c[0] * R, c[1] * R, c[2] * R, LISO_U, LISO_V, alfa},
                    {e0[0] * R, e0[1] * R, e0[2] * R, LISO_U, LISO_V, alfa},
                    {e1[0] * R, e1[1] * R, e1[2] * R, LISO_U, LISO_V, alfa},
                    {c[0] * R, c[1] * R, c[2] * R, LISO_U, LISO_V, alfa}}, cr, cg, cb);
        }
    }

    /** Una cinta entre dos direcciones de la cupula, de cara a la camara (en el centro). */
    private static void cinta(VertexConsumer buf, PoseStack.Pose p, float[] q, float ancho, int color, int alfa) {
        float R = RADIO * DELANTE;
        float ax = q[0] * R, ay = q[1] * R, az = q[2] * R;
        float bx = q[3] * R, by = q[4] * R, bz = q[5] * R;
        float dx = bx - ax, dy = by - ay, dz = bz - az;
        float mx = (ax + bx) / 2, my = (ay + by) / 2, mz = (az + bz) / 2;
        float lx = dy * mz - dz * my;
        float ly = dz * mx - dx * mz;
        float lz = dx * my - dy * mx;
        float l = (float) Math.sqrt(lx * lx + ly * ly + lz * lz);
        if (l < 1.0E-5F || alfa <= 0) {
            return;
        }
        alfa = Math.min(255, alfa);
        lx *= ancho / 2 / l;
        ly *= ancho / 2 / l;
        lz *= ancho / 2 / l;
        cara(buf, p, new float[][]{
                {ax - lx, ay - ly, az - lz, CINTA_U0, CINTA_V0, alfa},
                {ax + lx, ay + ly, az + lz, CINTA_U1, CINTA_V0, alfa},
                {bx + lx, by + ly, bz + lz, CINTA_U1, CINTA_V1, alfa},
                {bx - lx, by - ly, bz - lz, CINTA_U0, CINTA_V1, alfa}}, (color >> 16) & 255, (color >> 8) & 255, color & 255);
    }

    /**
     * Cuatro vertices (x, y, z, u, v, alfa) por una sola cara: la que mira a la camara, que esta en el centro de la
     * cupula. Antes iba todo por las dos caras, una encima de otra; pero en 26.2 la cara que se ve por detras se
     * alumbra solo con la luz de ambiente (un 40 %, PER_FACE_LIGHTING, como en NovilisDibujo), y segun el fotograma
     * salia una u otra: los ojos se apagaban a ratos. (entityTranslucent no recorta caras: con una basta.)
     */
    private static void cara(VertexConsumer buf, PoseStack.Pose p, float[][] v, int r, int g, int b) {
        float[] o = v[0], s = v[1], t = v[2];
        float ax = s[0] - o[0], ay = s[1] - o[1], az = s[2] - o[2];
        float bx = t[0] - o[0], by = t[1] - o[1], bz = t[2] - o[2];
        float nx = ay * bz - az * by, ny = az * bx - ax * bz, nz = ax * by - ay * bx;
        // De frente si la normal (por la regla de la mano derecha) apunta hacia la camara.
        boolean deFrente = nx * o[0] + ny * o[1] + nz * o[2] < 0;
        for (int i = 0; i < 4; i++) {
            float[] w = v[deFrente ? i : 3 - i];
            vertice(buf, p, w[0], w[1], w[2], w[3], w[4], r, g, b, (int) w[5]);
        }
    }

    /** Cuatro puntos de la cupula con el blanco liso de la hoja, para cara(). */
    private static float[][] liso(float[][] q, int alfa) {
        float[][] v = new float[4][];
        for (int i = 0; i < 4; i++) {
            v[i] = new float[]{q[i][0], q[i][1], q[i][2], LISO_U, LISO_V, alfa};
        }
        return v;
    }

    private static void vertice(VertexConsumer buf, PoseStack.Pose p, float x, float y, float z, float u, float v, int r, int g,
                                int b, int a) {
        buf.addVertex(p, x, y, z).setColor(r, g, b, a).setUv(u, v).setOverlay(OverlayTexture.NO_OVERLAY)
                .setLight(A_PLENA_LUZ).setNormal(p, 0, 1, 0);
    }

    // ------------------------------------------------------------------
    //  El cristal golpeado
    // ------------------------------------------------------------------

    /**
     * El dibujo del cristal, como un cristal golpeado de verdad (las fotos de Juan): el borde del hueco, casi redondo
     * y apenas dentado, y de cada una de sus puntas una grieta (Juan: "que de cada punto del hueco salga una grieta,
     * debes ser fiel a una ruptura"), curvada a su manera y de su largo, alguna partida en dos; y unos pocos arcos
     * que unen dos grietas vecinas, a distintas distancias.
     */
    private static void preparar(long s) {
        Random r = new Random(s ^ 0x5EEDL);
        // Las puntas: rumbos al azar (sin dos casi encima), unas juntas y otras separadas.
        float[] rumbos = new float[GRIETAS];
        int puestas = 0;
        for (int intento = 0; intento < 400 && puestas < GRIETAS; intento++) {
            float rumbo = r.nextFloat() * Mth.TWO_PI;
            boolean lejos = true;
            for (int k = 0; k < puestas; k++) {
                if (Math.abs(Mth.wrapDegrees((float) Math.toDegrees(rumbo - rumbos[k]))) < 13) {
                    lejos = false;
                }
            }
            if (lejos) {
                rumbos[puestas++] = rumbo;
            }
        }
        Arrays.sort(rumbos, 0, puestas);
        // El borde del hueco, como en la foto de Juan ("has hecho muchas puntas, sigue la referencia"): casi redondo y
        // apenas dentado. Cada punta sale un poco (de ahi arranca su grieta) y, hasta la siguiente, el borde se mete
        // un poco y vuelve, irregular.
        float[] puntas = new float[puestas];
        List<float[]> b = new ArrayList<>();
        for (int k = 0; k < puestas; k++) {
            puntas[k] = HUECO * (1.0F + 0.16F * r.nextFloat());
            b.add(new float[]{rumbos[k], puntas[k]});
            float siguiente = k + 1 < puestas ? rumbos[k + 1] : rumbos[0] + Mth.TWO_PI;
            float hueco = siguiente - rumbos[k];
            int cuantos = hueco > Math.toRadians(45) ? 3 : 2;
            for (int m = 1; m <= cuantos; m++) {
                float t = m / (float) (cuantos + 1) + (r.nextFloat() - 0.5F) * 0.2F / cuantos;
                b.add(new float[]{rumbos[k] + hueco * t, HUECO * (0.8F + 0.13F * r.nextFloat())});
            }
        }
        borde = b.toArray(new float[0][]);
        int nb = borde.length;
        List<float[]> lista = new ArrayList<>();
        // El borde del hueco: una grieta fina y encendida.
        for (int i = 0; i < nb; i++) {
            float[] a = borde[i];
            float[] c = borde[(i + 1) % nb];
            float rc = c[0] + (c[0] < a[0] ? Mth.TWO_PI : 0);
            lista.add(tramo(dir(a[0], a[1]), dir(rc, c[1]), 0.75F, 1.0F));
        }
        // De cada punta, su grieta: curvada y de su largo.
        List<float[][]> caminos = new ArrayList<>();
        for (int k = 0; k < puestas; k++) {
            float largo = 26 + 44 * (float) Math.pow(r.nextFloat(), 0.7);
            float curva = (r.nextFloat() - 0.5F) * 0.001F;
            float[][] camino = curva(r, rumbos[k], puntas[k], puntas[k] + largo, curva);
            caminos.add(camino);
            anadir(lista, camino, 0.95F, 0.28F, 1.0F, 0.55F);
            // Alguna se parte en dos: de un punto de en medio sale otra que se va abriendo.
            if (r.nextFloat() < 0.45F) {
                int i = (int) (camino.length * (0.35F + 0.35F * r.nextFloat()));
                float[] q = camino[i];
                float lado = r.nextBoolean() ? 1 : -1;
                float[][] rama = curva(r, q[0], q[1], q[1] + largo * (0.3F + 0.35F * r.nextFloat()),
                        curva + lado * (0.0006F + 0.0006F * r.nextFloat()));
                anadir(lista, rama, 0.55F, 0.2F, 0.8F, 0.45F);
            }
        }
        // Unos pocos arcos que unen dos grietas vecinas, a distintas distancias (alguno se queda a medias).
        int arcos = 3 + r.nextInt(3);
        for (int a = 0; a < arcos && caminos.size() > 1; a++) {
            int k = r.nextInt(caminos.size());
            float[][] c0 = caminos.get(k);
            float[][] c1 = caminos.get((k + 1) % caminos.size());
            int i0 = (int) (c0.length * (0.3F + 0.45F * r.nextFloat()));
            int i1 = Math.min(c1.length - 1, (int) (i0 * (0.8F + 0.4F * r.nextFloat())));
            float[] p0 = c0[Math.min(i0, c0.length - 1)];
            float[] p1 = c1[i1];
            float hasta = r.nextFloat() < 0.3F ? 0.55F : 1.0F;
            float comba = (r.nextFloat() - 0.2F) * 4.0F;
            float r1 = p1[0] + (p1[0] < p0[0] ? Mth.TWO_PI : 0);
            List<float[]> arco = new ArrayList<>();
            int pasos = 7;
            for (int i = 0; i <= pasos * hasta; i++) {
                float t = i / (float) pasos;
                float g = Mth.lerp(t, p0[1], p1[1]) + comba * Mth.sin(t * Mth.PI) + (r.nextFloat() - 0.5F) * 0.6F;
                arco.add(new float[]{Mth.lerp(t, p0[0], r1), g});
            }
            anadir(lista, arco.toArray(new float[0][]), 0.45F, 0.35F, 0.7F, 0.6F);
        }
        tramos = lista.toArray(new float[0][]);
        // Los ojos: tres pares, pequeños, que salen poco a poco en el hueco.
        List<float[]> os = new ArrayList<>();
        float giro = r.nextFloat() * Mth.TWO_PI;
        float[][] sitios = {{0, -1.6F, 1.05F}, {-3.0F, 2.0F, 0.75F}, {2.8F, 1.5F, 0.6F}};
        for (int i = 0; i < sitios.length; i++) {
            float ang = giro + r.nextFloat() * 0.6F;
            float x = sitios[i][0] * Mth.cos(ang) - sitios[i][1] * Mth.sin(ang);
            float y = sitios[i][0] * Mth.sin(ang) + sitios[i][1] * Mth.cos(ang);
            os.add(new float[]{x, y, sitios[i][2], 30 + 90 * i + r.nextInt(30), r.nextFloat() * 200, 70 + r.nextInt(80),
                    r.nextFloat() * Mth.TWO_PI});
        }
        ojos = os.toArray(new float[0][]);
        Atalaya.LOGGER.info("Cielo roto: el impacto en lo alto, {} grietas (una por punta del hueco) en {} tramos.", puestas,
                tramos.length);
    }

    /**
     * Una grieta curva de 'desde' a 'hasta' grados del cenit, empezando en 'rumbo': el rumbo se tuerce poco a poco
     * ('curva', por grado al cuadrado) y tiembla un poco; un punto cada 2,5 grados. Cada punto: rumbo y grados.
     */
    private static float[][] curva(Random r, float rumbo, float desde, float hasta, float curva) {
        int pasos = Math.max(2, (int) ((hasta - desde) / 2.5F));
        float[][] c = new float[pasos + 1][];
        float tiembla = 0;
        for (int i = 0; i <= pasos; i++) {
            float g = Mth.lerp(i / (float) pasos, desde, hasta);
            float d = g - desde;
            tiembla += (r.nextFloat() - 0.5F) * 0.006F;
            tiembla *= 0.85F;
            c[i] = new float[]{rumbo + curva * d * d / Math.max(1.0F, g * 0.08F) + tiembla, g};
        }
        return c;
    }

    /** Añade los tramos de un camino (rumbo, grados), cada vez mas finos y mas flojos hacia el final. */
    private static void anadir(List<float[]> lista, float[][] camino, float g0, float g1, float l0, float l1) {
        for (int i = 0; i + 1 < camino.length; i++) {
            float t = i / (float) Math.max(1, camino.length - 2);
            lista.add(tramo(dir(camino[i][0], camino[i][1]), dir(camino[i + 1][0], camino[i + 1][1]), Mth.lerp(t, g0, g1),
                    Mth.lerp(t, l0, l1)));
        }
    }

    /** Un tramo de grieta de a a b: x0, y0, z0, x1, y1, z1, cuando se abre, grosor, la distancia al cenit y su luz. */
    private static float[] tramo(float[] a, float[] b, float grosor, float luz) {
        float hacia = (float) Math.acos(Mth.clamp(normal(lerp(a, b, 0.5F))[1], -1, 1)) / Mth.HALF_PI;
        return new float[]{a[0], a[1], a[2], b[0], b[1], b[2], Mth.clamp(hacia * 1.4F, 0, 1), grosor, hacia, luz};
    }

    private static float[] lerp(float[] a, float[] b, float f) {
        return new float[]{Mth.lerp(f, a[0], b[0]), Mth.lerp(f, a[1], b[1]), Mth.lerp(f, a[2], b[2])};
    }

    private static float[] normal(float[] a) {
        float l = (float) Math.sqrt(a[0] * a[0] + a[1] * a[1] + a[2] * a[2]);
        return l < 1.0E-7F ? new float[]{0, 1, 0} : new float[]{a[0] / l, a[1] / l, a[2] / l};
    }

    /** La direccion del hueco (para FotosPrueba: solo hay uno, en lo alto). */
    public static float[] centroHueco(int i) {
        return i == 0 ? new float[]{0, 1, 0} : null;
    }
}
