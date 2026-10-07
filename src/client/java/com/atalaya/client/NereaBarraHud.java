package com.atalaya.client;

import com.atalaya.Atalaya;
import com.atalaya.entity.NereaEntity;
import com.atalaya.entity.NereaGeometria;
import net.fabricmc.fabric.api.client.rendering.v1.hud.HudElement;
import net.minecraft.client.DeltaTracker;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphicsExtractor;
import net.minecraft.client.renderer.RenderPipelines;
import net.minecraft.resources.Identifier;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.Entity;
import org.jspecify.annotations.Nullable;

/**
 * La barra de jefe de Nerea, propia (nerea_hud.py), desde el remake de
 * octubre de 2026 del tamano y el estilo de la de Aeralis: una ola sale del
 * emblema y rompe por encima del marco de prismarina vieja (con percebes y
 * corales); el emblema es el corazon maldito de la fase entre dos costillas
 * (abiertas en la IV); dentro corre el agua del color de la maldicion (cian,
 * violeta, magenta, rojo) con su cresta de espuma y un rastro blanco que se
 * queda atras al recibir dano; las muescas de fase son eslabones que se parten
 * al pasarlos. "NEREA" y la fase, en letras de pixel.
 *
 * Durante la Mirada del Abismo la barra cambia de vista, como el Sello de
 * Rajang y el Juicio de Aeralis: en el emblema, su calavera con los dos ojos,
 * que se rajan con cada impacto y se revientan al romperse; debajo, la marea
 * que baja (el tiempo que le queda al chorro, roja al final). Con la Furia de
 * las Mareas, todo en verde abismo y el rotulo FURIA.
 */
public class NereaBarraHud implements HudElement {

    private static final String[] CLAVES = {"1", "2", "3", "4", "furia", "libre"};
    private static final Identifier[] MARCOS = new Identifier[6];
    private static final Identifier[] RELLENOS = new Identifier[6];
    private static final Identifier[] CORAZONES = new Identifier[6];
    private static final Identifier ESLABON = tex("nerea_barra_eslabon");
    private static final Identifier ESLABON_ROTO = tex("nerea_barra_eslabon_roto");
    private static final Identifier MASCARA = tex("nerea_barra_mascara");
    private static final Identifier OJO = tex("nerea_barra_ojo");
    private static final Identifier OJO_ROTO = tex("nerea_barra_ojo_roto");
    private static final Identifier[] GRIETAS = {tex("nerea_barra_grieta_1"), tex("nerea_barra_grieta_2"),
            tex("nerea_barra_grieta_3"), tex("nerea_barra_grieta_4")};
    private static final Identifier MAREA = tex("nerea_barra_marea");
    /** Las letras, en pixel (nerea_hud.py): nada de la fuente de Minecraft. */
    private static final Identifier NOMBRE = tex("nerea_barra_nombre");
    private static final Identifier[] FASES = {tex("nerea_barra_fase_1"), tex("nerea_barra_fase_2"),
            tex("nerea_barra_fase_3"), tex("nerea_barra_fase_4")};
    private static final Identifier LIBRE = tex("nerea_barra_libre");
    private static final Identifier FURIA = tex("nerea_barra_furia");

    static {
        for (int i = 0; i < CLAVES.length; i++) {
            MARCOS[i] = tex("nerea_barra_marco_" + CLAVES[i]);
            RELLENOS[i] = tex("nerea_barra_relleno_" + CLAVES[i]);
            CORAZONES[i] = tex("nerea_barra_corazon_" + CLAVES[i]);
        }
    }

    private static final int NOMBRE_ANCHO = 36;
    private static final int ROTULO_ANCHO = 64;
    private static final int LETRAS_ALTO = 10;

    /** Color de cada fase (el agua, los rotulos y los ojos), el verde abismo de la Furia y el oro de la liberacion. */
    private static final int[] COLOR_FASE = {0x3FE0FF, 0x9A6BFF, 0xD43CFF, 0xFF2050};
    private static final int COLOR_FURIA = 0x20F0B0;
    private static final int ORO = 0xFFC23A;

    /** Las medidas de nerea_hud.py. ALTO lo usan las barras de Aeralis y Rajang para ir debajo. */
    private static final int ANCHO = 240;
    public static final int ALTO = 44;
    private static final int HUECO_X = 40;
    private static final int HUECO_Y = 22;
    private static final int HUECO_ANCHO = 190;
    private static final int HUECO_ALTO = 9;
    private static final int EMBLEMA_X = 19;
    private static final int EMBLEMA_Y = 26;
    private static final int NUCLEO = 24;
    /** Los ojos de la calavera: donde caen sus cuencas dentro de la mascara, y su lado. */
    private static final int[] CUENCA_X = {5, 13};
    private static final int CUENCA_Y = 10;
    private static final int OJO_LADO = 6;
    /** La marea que baja durante la Mirada: bajo la barra. */
    private static final int MAREA_X = 44;
    private static final int MAREA_Y = 36;
    private static final int MAREA_ANCHO = 150;
    private static final int MAREA_ALTO = 5;

    /** Si se ha dibujado este fotograma: la de Aeralis se pone debajo. */
    public static boolean visible;

    private float fantasma = 1.0F;
    private int ultimo = -1;

    private static Identifier tex(String nombre) {
        return Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "textures/gui/" + nombre + ".png");
    }

    @Override
    public void extractRenderState(GuiGraphicsExtractor g, DeltaTracker delta) {
        Minecraft mc = Minecraft.getInstance();
        NereaEntity n = cercana(mc);
        visible = n != null;
        if (n == null) {
            ultimo = -1;
            return;
        }
        float parcial = delta.getGameTimeDeltaPartialTick(false);
        boolean libre = n.isDeadOrDying();
        float vida = libre ? 0.0F : Mth.clamp(n.getHealth() / n.getMaxHealth(), 0.0F, 1.0F);
        if (n.getEstado() == NereaEntity.DESPERTAR) {
            // Al despertar la barra se llena: entra en escena.
            vida *= Mth.clamp((n.tickCount - n.inicioEstado + parcial) / NereaGeometria.DURACION_DESPERTAR, 0.0F, 1.0F);
        }
        if (n.getId() != ultimo) {
            ultimo = n.getId();
            fantasma = vida;
        }
        // El rastro blanco del dano se queda atras y alcanza a la vida poco a poco.
        fantasma = vida > fantasma ? vida : fantasma + (vida - fantasma) * 0.04F;

        int fase = Mth.clamp(n.fase(), 1, 4);
        boolean furia = n.tieneFuria() && !libre;
        int i = libre ? 5 : furia ? 4 : fase - 1;
        int x0 = (g.guiWidth() - ANCHO) / 2;
        int y0 = 5;
        g.blit(RenderPipelines.GUI_TEXTURED, MARCOS[i], x0, y0, 0.0F, 0.0F, ANCHO, ALTO, ANCHO, ALTO, ANCHO, ALTO, 0xFFFFFFFF);

        int hx = x0 + HUECO_X;
        int hy = y0 + HUECO_Y;
        int lleno = Math.round(HUECO_ANCHO * vida);
        int rastro = Math.round(HUECO_ANCHO * fantasma);
        if (rastro > lleno) {
            g.fill(hx + lleno, hy, hx + rastro, hy + HUECO_ALTO, 0xD8F4FFFF);
        }
        int color = 0xFF000000 | (libre ? ORO : furia ? COLOR_FURIA : COLOR_FASE[fase - 1]);
        int tinte = 0xFFFFFFFF;
        if (furia) {
            // Con la Furia, el agua y el rotulo laten.
            float k = 0.85F + 0.2F * Mth.sin((n.tickCount + parcial) * 0.35F);
            color = 0xFF000000 | escalar(COLOR_FURIA, k);
            tinte = 0xFF000000 | escalar(0xFFFFFF, 0.9F + 0.12F * Mth.sin((n.tickCount + parcial) * 0.35F));
        } else if (fase == 4 && !libre) {
            // En la ultima fase late con el corazon.
            tinte = 0xFF000000 | escalar(0xFFFFFF, 0.82F + 0.18F * Mth.sin((n.tickCount + parcial) * 0.5F));
        }
        // El agua corre hacia la izquierda: el relleno es un mosaico que se desplaza.
        int desplaza = (int) ((n.tickCount + parcial) * 0.8F) % 64;
        for (int x = 0; x < lleno; ) {
            int u = (x + desplaza) % 64;
            int w = Math.min(64 - u, lleno - x);
            g.blit(RenderPipelines.GUI_TEXTURED, RELLENOS[i], hx + x, hy, u, 0.0F, w, HUECO_ALTO, w, HUECO_ALTO, 64, HUECO_ALTO, tinte);
            x += w;
        }
        // Las muescas de fase: un eslabon que se parte al pasar la vida por el.
        for (float corte : new float[]{0.75F, 0.5F, 0.25F}) {
            int ex = hx + Math.round(HUECO_ANCHO * corte) - 3;
            g.blit(RenderPipelines.GUI_TEXTURED, vida < corte ? ESLABON_ROTO : ESLABON, ex, hy - 1, 0.0F, 0.0F,
                    7, 10, 7, 10, 7, 10, 0xFFFFFFFF);
        }
        // El emblema: el corazon (o, mientras mira, la calavera con los ojos).
        int e = n.getEstado();
        boolean mirada = !libre && (e == NereaEntity.MIRADA || e == NereaEntity.ATURDIDO);
        int cx = x0 + EMBLEMA_X - NUCLEO / 2;
        int cy = y0 + EMBLEMA_Y - NUCLEO / 2;
        if (!libre && n.hurtTime > 0) {
            cy += (n.hurtTime % 2 == 0) ? 1 : -1;   // da un respingo al recibir el golpe
        }
        if (mirada) {
            calavera(g, n, cx, cy, color);
            // Cuantos impactos lleva cada ojo de los que hacen falta (testers: no sabian que se paraba asi).
            if (e == NereaEntity.MIRADA) {
                int falta = n.getGolpesNecesarios();
                String txt = Math.min(falta, n.getGolpesOjo(0)) + "/" + falta + "  " + Math.min(falta, n.getGolpesOjo(1)) + "/"
                        + falta;
                int w = mc.font.width(txt);
                g.text(mc.font, txt, cx + NUCLEO / 2 - w / 2, cy + NUCLEO + 2, 0xFFFFFFFF, true);
            }
            if (e == NereaEntity.MIRADA) {
                marea(g, n, x0, y0, color, parcial);
            }
        } else {
            g.blit(RenderPipelines.GUI_TEXTURED, CORAZONES[i], cx, cy, 0.0F, 0.0F, NUCLEO, NUCLEO, NUCLEO, NUCLEO,
                    NUCLEO, NUCLEO, 0xFFFFFFFF);
        }

        // Encima del marco: el nombre junto a la ola y la fase a la derecha.
        g.blit(RenderPipelines.GUI_TEXTURED, NOMBRE, x0 + 98, y0 + 9, 0.0F, 0.0F, NOMBRE_ANCHO, LETRAS_ALTO,
                NOMBRE_ANCHO, LETRAS_ALTO, NOMBRE_ANCHO, LETRAS_ALTO, 0xFFFFFFFF);
        if (furia) {
            FuriaHud.cuentaAtras(g, n.getFuriaFin(), hx, hy, HUECO_ANCHO, COLOR_FURIA, parcial);
        }
        g.blit(RenderPipelines.GUI_TEXTURED, libre ? LIBRE : furia ? FURIA : FASES[fase - 1], hx + HUECO_ANCHO - ROTULO_ANCHO + 1, y0 + 8,
                0.0F, 0.0F, ROTULO_ANCHO, LETRAS_ALTO, ROTULO_ANCHO, LETRAS_ALTO, ROTULO_ANCHO, LETRAS_ALTO, color);
    }

    /** La calavera de la Mirada con sus dos ojos: rajados con los impactos, reventados al romperse. */
    private static void calavera(GuiGraphicsExtractor g, NereaEntity n, int cx, int cy, int color) {
        g.blit(RenderPipelines.GUI_TEXTURED, MASCARA, cx, cy, 0.0F, 0.0F, NUCLEO, NUCLEO, NUCLEO, NUCLEO, NUCLEO, NUCLEO, 0xFFFFFFFF);
        int rotos = n.getOjosRotos();
        for (int ojo = 0; ojo < 2; ojo++) {
            int ox = cx + CUENCA_X[ojo];
            int oy = cy + CUENCA_Y;
            if ((rotos & (1 << ojo)) != 0) {
                g.blit(RenderPipelines.GUI_TEXTURED, OJO_ROTO, ox, oy, 0.0F, 0.0F, OJO_LADO, OJO_LADO, OJO_LADO, OJO_LADO,
                        OJO_LADO, OJO_LADO, 0xFFFFFFFF);
                continue;
            }
            int golpes = n.getGolpesOjo(ojo);
            // Late mas deprisa cuantos mas impactos lleva.
            float k = 0.85F + 0.15F * Mth.sin(n.tickCount * (0.3F + 0.08F * golpes));
            g.blit(RenderPipelines.GUI_TEXTURED, OJO, ox, oy, 0.0F, 0.0F, OJO_LADO, OJO_LADO, OJO_LADO, OJO_LADO,
                    OJO_LADO, OJO_LADO, 0xFF000000 | escalar(color & 0xFFFFFF, k));
            if (golpes > 0) {
                int etapa = Math.min(4, 1 + golpes * 4 / Math.max(1, n.getGolpesNecesarios()));
                g.blit(RenderPipelines.GUI_TEXTURED, GRIETAS[etapa - 1], ox, oy, 0.0F, 0.0F, OJO_LADO, OJO_LADO, OJO_LADO,
                        OJO_LADO, OJO_LADO, OJO_LADO, 0xFFFFFFFF);
            }
        }
    }

    /** La marea que baja: lo que le queda al chorro de la Mirada para soltar (roja al final). */
    private static void marea(GuiGraphicsExtractor g, NereaEntity n, int x0, int y0, int color, float parcial) {
        float total = NereaGeometria.DURACION_MIRADA / Math.max(0.01F, n.ritmoCliente);
        float k = Mth.clamp(1.0F - (n.tickCount - n.inicioEstado + parcial) / total, 0.0F, 1.0F);
        int mx = x0 + MAREA_X;
        int my = y0 + MAREA_Y;
        // Un fondo oscuro detras, para que se lea sobre su cuerpo o el cielo.
        g.fill(mx - 1, my - 1, mx + MAREA_ANCHO + 1, my + MAREA_ALTO + 1, 0xB0061214);
        int w = Math.round(MAREA_ANCHO * k);
        int c = k > 0.25F ? color : ((n.tickCount / 3) % 2 == 0 ? 0xFFFF5A3A : 0xFFFFC23A);
        int corre = (int) ((n.tickCount + parcial) * 0.6F) % 64;
        for (int x = 0; x < w; ) {
            int u = (x + corre) % 64;
            int ancho = Math.min(64 - u, w - x);
            g.blit(RenderPipelines.GUI_TEXTURED, MAREA, mx + x, my, u, 0.0F, ancho, MAREA_ALTO, ancho, MAREA_ALTO, 64, MAREA_ALTO, c);
            x += ancho;
        }
    }

    private static int escalar(int rgb, float k) {
        int r = Math.min(255, (int) (((rgb >> 16) & 255) * k));
        int gr = Math.min(255, (int) (((rgb >> 8) & 255) * k));
        int b = Math.min(255, (int) ((rgb & 255) * k));
        return (r << 16) | (gr << 8) | b;
    }

    /** La Nerea despierta mas cercana, a menos de 100 bloques. */
    private static @Nullable NereaEntity cercana(Minecraft mc) {
        if (mc.level == null || mc.player == null) {
            return null;
        }
        NereaEntity mejor = null;
        double d = 100 * 100;
        for (Entity e : mc.level.entitiesForRendering()) {
            if (e instanceof NereaEntity n && n.getEstado() != NereaEntity.DORMIDO && !n.isRemoved()) {
                double dd = n.distanceToSqr(mc.player);
                if (dd < d) {
                    d = dd;
                    mejor = n;
                }
            }
        }
        return mejor;
    }
}
