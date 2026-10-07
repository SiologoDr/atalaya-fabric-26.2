package com.atalaya.client;

import com.atalaya.Atalaya;
import com.atalaya.entity.AeralisEntity;
import com.atalaya.entity.AeralisGeometria;
import net.fabricmc.fabric.api.client.rendering.v1.hud.HudElement;
import net.minecraft.client.DeltaTracker;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphicsExtractor;
import net.minecraft.client.renderer.RenderPipelines;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.Identifier;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.Entity;
import org.jspecify.annotations.Nullable;

/**
 * La barra de jefe de Aeralis, propia (aeralis_hud.py), desde el remake de
 * octubre de 2026: un ala de tormenta sale del emblema por encima del marco de
 * nube; el emblema es el ojo de la tormenta de la fase con la corona de puas;
 * dentro corre la tormenta en el color de la fase (cielo, anil, violeta,
 * magenta), con su frente encendido y un rastro blanco que se queda atras al
 * recibir dano; las muescas de fase son ojos de tormenta que se apagan al
 * pasarlos. "AERALIS" y la fase, en letras de pixel.
 *
 * Desde la fase II, una raya fina bajo la barra se llena con el viento de los
 * tornados rotos (10, 20 o 30 segun la fase); llena, Aeralis cae aturdida 5 s.
 * Con la Furia del Vendaval (el Juicio fallido), la tormenta late en violeta
 * vivo y el rotulo dice FURIA.
 * Durante el Juicio del Ciclon, en su lugar, como el Sello de Rajang: los cuatro
 * nucleos (encendidos los que siguen en pie, partidos los rotos) y la losa del
 * tiempo que le queda al ciclon, roja al final. Si la de Nerea esta a la vista, la de Aeralis va
 * debajo; la de Rajang, debajo de las dos.
 */
public class AeralisBarraHud implements HudElement {

    private static final Identifier[] MARCOS = new Identifier[5];
    private static final Identifier[] RELLENOS = new Identifier[5];
    private static final Identifier[] NUCLEOS = new Identifier[5];
    private static final Identifier OJO = tex("aeralis_barra_ojo");
    private static final Identifier OJO_APAGADO = tex("aeralis_barra_ojo_apagado");
    private static final Identifier CRISTAL = tex("aeralis_barra_cristal");
    private static final Identifier CRISTAL_ROTO = tex("aeralis_barra_cristal_roto");
    private static final Identifier NOMBRE = tex("aeralis_barra_nombre");
    private static final Identifier[] FASES = {tex("aeralis_barra_fase_1"), tex("aeralis_barra_fase_2"),
            tex("aeralis_barra_fase_3"), tex("aeralis_barra_fase_4")};
    private static final Identifier LIBRE = tex("aeralis_barra_libre");
    private static final Identifier FURIA = tex("aeralis_barra_furia");
    /** El violeta electrico de la Furia del Vendaval. */
    private static final int COLOR_FURIA = 0xC56BFF;

    static {
        String[] claves = {"1", "2", "3", "4", "libre"};
        for (int i = 0; i < 5; i++) {
            MARCOS[i] = tex("aeralis_barra_marco_" + claves[i]);
            RELLENOS[i] = tex("aeralis_barra_relleno_" + claves[i]);
            NUCLEOS[i] = tex("aeralis_barra_nucleo_" + claves[i]);
        }
    }

    private static final int NOMBRE_ANCHO = 48;
    private static final int ROTULO_ANCHO = 64;
    private static final int LETRAS_ALTO = 10;

    /** Color de cada fase (el de los rotulos, las muescas y los cristales) y el oro de la liberacion. */
    private static final int[] COLOR_FASE = {0x5FD2FF, 0x7F8CFF, 0xB07CFF, 0xFF4FD8};
    private static final int[] CLARO_FASE = {0xF2FFFF, 0xEEF0FF, 0xFFF7D6, 0xFFFFFF};
    private static final int ORO = 0xFFC23A;

    /** Las medidas de aeralis_hud.py. ALTO lo usa la barra de Rajang para ir debajo. */
    private static final int ANCHO = 240;
    public static final int ALTO = 44;
    private static final int HUECO_X = 40;
    private static final int HUECO_Y = 22;
    private static final int HUECO_ANCHO = 190;
    private static final int HUECO_ALTO = 9;
    private static final int EMBLEMA_X = 19;
    private static final int EMBLEMA_Y = 26;
    private static final int NUCLEO = 24;
    /** La raya del viento de vuelta, bajo las muescas. */
    private static final int VIENTO_Y = 38;

    private float fantasma = 1.0F;
    private int ultimo = -1;
    /** Si se esta dibujando (la de Rajang va debajo). */
    public static boolean visible;

    private static Identifier tex(String nombre) {
        return Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "textures/gui/" + nombre + ".png");
    }

    @Override
    public void extractRenderState(GuiGraphicsExtractor g, DeltaTracker delta) {
        Minecraft mc = Minecraft.getInstance();
        AeralisEntity a = cercana(mc);
        visible = a != null;
        if (a == null) {
            ultimo = -1;
            return;
        }
        float parcial = delta.getGameTimeDeltaPartialTick(false);
        boolean libre = a.isDeadOrDying();
        float vida = libre ? 0.0F : Mth.clamp(a.getHealth() / a.getMaxHealth(), 0.0F, 1.0F);
        if (a.getEstado() == AeralisEntity.DESPERTAR) {
            vida *= Mth.clamp((a.tickCount - a.inicioEstado + parcial) / AeralisGeometria.DURACION_DESPERTAR, 0.0F, 1.0F);
        }
        if (a.getId() != ultimo) {
            ultimo = a.getId();
            fantasma = vida;
        }
        fantasma = vida > fantasma ? vida : fantasma + (vida - fantasma) * 0.04F;

        int fase = Mth.clamp(a.fase(), 1, 4);
        int i = libre ? 4 : fase - 1;
        int x0 = (g.guiWidth() - ANCHO) / 2;
        int y0 = 5 + (NereaBarraHud.visible ? NereaBarraHud.ALTO + 6 : 0);
        g.blit(RenderPipelines.GUI_TEXTURED, MARCOS[i], x0, y0, 0.0F, 0.0F, ANCHO, ALTO, ANCHO, ALTO, ANCHO, ALTO, 0xFFFFFFFF);

        int hx = x0 + HUECO_X;
        int hy = y0 + HUECO_Y;
        int lleno = Math.round(HUECO_ANCHO * vida);
        int rastro = Math.round(HUECO_ANCHO * fantasma);
        if (rastro > lleno) {
            g.fill(hx + lleno, hy, hx + rastro, hy + HUECO_ALTO, 0xD8F4FFFF);
        }
        int color = 0xFF000000 | (libre ? ORO : COLOR_FASE[fase - 1]);
        int tinte = 0xFFFFFFFF;
        boolean furia = a.tieneFuria() && !libre;
        if (furia) {
            // Con la Furia, la tormenta y el rotulo laten deprisa.
            float k = 0.8F + 0.25F * Mth.sin((a.tickCount + parcial) * 0.45F);
            color = 0xFF000000 | escalar(COLOR_FURIA, k);
            tinte = 0xFF000000 | escalar(0xFFE6FF, 0.9F + 0.15F * Mth.sin((a.tickCount + parcial) * 0.45F));
        } else if (fase == 4 && !libre) {
            // En la ultima fase la tormenta parpadea con los rayos.
            float k = ((a.tickCount / 3) % 9 == 0) ? 1.2F : 0.88F + 0.12F * Mth.sin((a.tickCount + parcial) * 0.4F);
            tinte = 0xFF000000 | escalar(0xFFFFFF, k);
        }
        // La tormenta corre hacia la derecha.
        int desplaza = 64 - (int) ((a.tickCount + parcial) * 1.2F) % 64;
        for (int x = 0; x < lleno; ) {
            int u = (x + desplaza) % 64;
            int w = Math.min(64 - u, lleno - x);
            g.blit(RenderPipelines.GUI_TEXTURED, RELLENOS[i], hx + x, hy, u, 0.0F, w, HUECO_ALTO, w, HUECO_ALTO, 64, HUECO_ALTO, tinte);
            x += w;
        }
        if (lleno >= 2) {
            // El frente encendido.
            g.fill(hx + lleno - 2, hy, hx + lleno, hy + HUECO_ALTO, 0xFF000000 | (libre ? 0xFFFBE0 : CLARO_FASE[fase - 1]));
        }
        for (float corte : new float[]{0.75F, 0.5F, 0.25F}) {
            int ex = hx + Math.round(HUECO_ANCHO * corte) - 3;
            boolean pasado = vida < corte;
            g.blit(RenderPipelines.GUI_TEXTURED, pasado ? OJO_APAGADO : OJO, ex, hy + HUECO_ALTO - 2, 0.0F, 0.0F,
                    7, 7, 7, 7, 7, 7, pasado ? 0xFFFFFFFF : color);
        }
        int e = a.getEstado();
        boolean juicio = e == AeralisEntity.JUICIO_SUBE || e == AeralisEntity.JUICIO_SOSTIENE || e == AeralisEntity.JUICIO_GOLPE;
        if (!libre && !juicio && fase >= 2) {
            // El viento de vuelta: la raya que se llena con los tornados rotos y la
            // cuenta al lado (testers, 07-10-2026: antes apenas se veia).
            int vy = y0 + VIENTO_Y;
            int necesario = a.getVientoNecesario();
            Component cuenta = Component.translatable("hud.atalaya.aeralis.viento", Math.min(a.getViento(), necesario), necesario);
            int tw = mc.font.width(cuenta);
            int largo = HUECO_ANCHO - tw - 4;
            g.fill(hx - 1, vy - 1, hx + largo + 1, vy + 3, 0xB00A0E18);
            float k = Mth.clamp(a.getViento() / (float) necesario, 0.0F, 1.0F);
            int w = Math.round(largo * k);
            if (w > 0) {
                g.fill(hx, vy, hx + w, vy + 2, 0xF0000000 | COLOR_FASE[fase - 1]);
                g.fill(hx + w - 1, vy, hx + w, vy + 2, 0xFF000000 | CLARO_FASE[fase - 1]);
            }
            g.text(mc.font, cuenta, hx + HUECO_ANCHO - tw, vy - 3, 0xFF000000 | CLARO_FASE[fase - 1], true);
        }
        // El Juicio, como el Sello de Rajang: los cuatro nucleos y el tiempo que le queda.
        if (!libre && (e == AeralisEntity.JUICIO_SOSTIENE || e == AeralisEntity.JUICIO_GOLPE)) {
            juicioBajo(g, a, hx, y0 + 35, color, parcial);
        }
        int cx = x0 + EMBLEMA_X - NUCLEO / 2;
        int cy = y0 + EMBLEMA_Y - NUCLEO / 2;
        if (!libre && a.hurtTime > 0) {
            cx += (a.hurtTime % 2 == 0) ? 1 : -1;   // tiembla al recibir el golpe
        }
        g.blit(RenderPipelines.GUI_TEXTURED, NUCLEOS[i], cx, cy, 0.0F, 0.0F, NUCLEO, NUCLEO, NUCLEO, NUCLEO, NUCLEO, NUCLEO,
                0xFFFFFFFF);

        g.blit(RenderPipelines.GUI_TEXTURED, NOMBRE, x0 + 100, y0 + 9, 0.0F, 0.0F, NOMBRE_ANCHO, LETRAS_ALTO,
                NOMBRE_ANCHO, LETRAS_ALTO, NOMBRE_ANCHO, LETRAS_ALTO, 0xFFFFFFFF);
        if (furia) {
            FuriaHud.cuentaAtras(g, a.getFuriaFin(), hx, hy, HUECO_ANCHO, COLOR_FURIA, parcial);
        }
        g.blit(RenderPipelines.GUI_TEXTURED, libre ? LIBRE : furia ? FURIA : FASES[fase - 1], hx + HUECO_ANCHO - ROTULO_ANCHO + 1, y0 + 8,
                0.0F, 0.0F, ROTULO_ANCHO, LETRAS_ALTO, ROTULO_ANCHO, LETRAS_ALTO, ROTULO_ANCHO, LETRAS_ALTO, color);
    }

    /** Los cuatro nucleos del Juicio (rotos o en pie) y la losa del tiempo, bajo la barra. */
    private static void juicioBajo(GuiGraphicsExtractor g, AeralisEntity a, int x0, int y0, int color, float parcial) {
        int rotos = a.getNucleosRotos();
        for (int i = 0; i < 4; i++) {
            boolean roto = (rotos & (1 << i)) != 0;
            // Un fondo oscuro detras, para que se lean sobre su cuerpo o el cielo.
            g.fill(x0 + 5 + i * 10, y0 - 1, x0 + 14 + i * 10, y0 + 9, 0xB00A0E18);
            g.blit(RenderPipelines.GUI_TEXTURED, roto ? CRISTAL_ROTO : CRISTAL, x0 + 6 + i * 10, y0, 0.0F, 0.0F,
                    7, 9, 7, 9, 7, 9, roto ? 0xFFFFFFFF : color);
        }
        float k = a.getEstado() == AeralisEntity.JUICIO_SOSTIENE
                ? Mth.clamp(1.0F - (a.tickCount - a.inicioEstado + parcial) / AeralisEntity.JUICIO_TICKS, 0.0F, 1.0F) : 0.0F;
        int lx0 = x0 + 50;
        int lx1 = x0 + HUECO_ANCHO - 2;
        int ly = y0 + 2;
        g.fill(lx0, ly, lx1, ly + 5, 0xFF0A0E18);
        g.fill(lx0 + 1, ly + 1, lx1 - 1, ly + 4, 0xFF101826);
        int w = Math.round((lx1 - lx0 - 2) * k);
        if (w > 0) {
            int c = k > 0.25F ? color : ((a.tickCount / 3) % 2 == 0 ? 0xFFFF5A3A : 0xFFFFC23A);
            g.fill(lx0 + 1, ly + 1, lx0 + 1 + w, ly + 4, c);
            g.fill(lx0 + 1, ly + 1, lx0 + 1 + w, ly + 2, 0x60FFFFFF);
        }
    }

    private static int escalar(int rgb, float k) {
        int r = Math.min(255, (int) (((rgb >> 16) & 255) * k));
        int gr = Math.min(255, (int) (((rgb >> 8) & 255) * k));
        int b = Math.min(255, (int) ((rgb & 255) * k));
        return (r << 16) | (gr << 8) | b;
    }

    /** La Aeralis despierta mas cercana, a menos de 120 bloques. */
    private static @Nullable AeralisEntity cercana(Minecraft mc) {
        if (mc.level == null || mc.player == null) {
            return null;
        }
        AeralisEntity mejor = null;
        double d = 120 * 120;
        for (Entity e : mc.level.entitiesForRendering()) {
            if (e instanceof AeralisEntity a && a.getEstado() != AeralisEntity.DORMIDA && !a.isRemoved()) {
                double dd = a.distanceToSqr(mc.player);
                if (dd < d) {
                    d = dd;
                    mejor = a;
                }
            }
        }
        return mejor;
    }
}
