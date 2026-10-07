package com.atalaya.client;

import com.atalaya.Atalaya;
import com.atalaya.entity.RajangEntity;
import com.atalaya.entity.RajangGeometria;
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
 * La barra de jefe de Rajang, propia (rajang_remake_hud.py --juego), desde
 * octubre de 2026 del tamano y el estilo de las de Nerea y Aeralis: la cresta
 * de cristales de jade de su lomo sale del emblema por encima del marco de
 * bloques de jade con incrustaciones de oro y la punta de templo; el emblema es
 * el sol de jade de la fase (la placa de oro en espiral, cada vez mas rajado);
 * dentro corre la energia de la tierra en el color de la fase (jade, verde,
 * lima, amarillo) con su frente encendido y un rastro claro que se queda atras
 * al recibir dano; las muescas son colmillos de jade que se parten al pasarlos.
 * "RAJANG" y la fase, en letras de pixel.
 *
 * Durante el Sello de la Tierra, debajo, los cuatro totems tal como se ven en el
 * juego (enteros o partidos y apagados) y la losa del tiempo que queda, roja al
 * final. Con la Furia de Jade, todo en verde vivo y el rotulo FURIA. Si estan a
 * la vista las de Nerea o Aeralis, va debajo.
 */
public class RajangBarraHud implements HudElement {

    private static final String[] CLAVES = {"1", "2", "3", "4", "furia", "libre"};
    private static final Identifier[] MARCOS = new Identifier[6];
    private static final Identifier[] RELLENOS = new Identifier[6];
    private static final Identifier[] NUCLEOS = new Identifier[6];
    private static final Identifier COLMILLO = tex("rajang_barra_colmillo");
    private static final Identifier COLMILLO_ROTO = tex("rajang_barra_colmillo_roto");
    private static final Identifier TOTEM = tex("rajang_barra_totem");
    private static final Identifier TOTEM_ROTO = tex("rajang_barra_totem_roto");
    private static final Identifier NOMBRE = tex("rajang_barra_nombre");
    private static final Identifier[] FASES = {tex("rajang_barra_fase_1"), tex("rajang_barra_fase_2"),
            tex("rajang_barra_fase_3"), tex("rajang_barra_fase_4")};
    private static final Identifier LIBRE = tex("rajang_barra_libre");
    private static final Identifier FURIA = tex("rajang_barra_furia");

    static {
        for (int i = 0; i < CLAVES.length; i++) {
            MARCOS[i] = tex("rajang_barra_marco_" + CLAVES[i]);
            RELLENOS[i] = tex("rajang_barra_relleno_" + CLAVES[i]);
            NUCLEOS[i] = tex("rajang_barra_nucleo_" + CLAVES[i]);
        }
    }

    private static final int NOMBRE_ANCHO = 48;
    private static final int ROTULO_ANCHO = 64;
    private static final int LETRAS_ALTO = 10;

    /** Color de cada fase (rotulos), el verde vivo de la Furia de Jade y el oro de la liberacion. */
    private static final int[] COLOR_FASE = {0x58C886, 0x8CFF5A, 0xC8FF2A, 0xE6FF4A};
    /** El frente encendido de la energia en cada fase (el ultimo paso de su rampa). */
    private static final int[] CLARO_FASE = {0xDFFFE8, 0xF0FFE0, 0xFBFFE0, 0xFFFFFF};
    private static final int COLOR_FURIA = 0x7CFF3A;
    private static final int ORO = 0xF8D97C;

    /** Las medidas de rajang_remake_hud.py (las mismas que las de Nerea y Aeralis). */
    private static final int ANCHO = 240;
    public static final int ALTO = 44;
    private static final int HUECO_X = 40;
    private static final int HUECO_Y = 22;
    private static final int HUECO_ANCHO = 190;
    private static final int HUECO_ALTO = 9;
    private static final int EMBLEMA_X = 19;
    private static final int EMBLEMA_Y = 26;
    private static final int NUCLEO = 24;

    private float fantasma = 1.0F;
    private int ultimo = -1;

    private static Identifier tex(String nombre) {
        return Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "textures/gui/" + nombre + ".png");
    }

    @Override
    public void extractRenderState(GuiGraphicsExtractor g, DeltaTracker delta) {
        Minecraft mc = Minecraft.getInstance();
        RajangEntity r = cercano(mc);
        if (r == null) {
            ultimo = -1;
            return;
        }
        float parcial = delta.getGameTimeDeltaPartialTick(false);
        boolean libre = r.isDeadOrDying();
        float vida = libre ? 0.0F : Mth.clamp(r.getHealth() / r.getMaxHealth(), 0.0F, 1.0F);
        if (r.getEstado() == RajangEntity.DESPERTAR) {
            vida *= Mth.clamp((r.tickCount - r.inicioEstado + parcial) / RajangGeometria.DURACION_DESPERTAR, 0.0F, 1.0F);
        }
        if (r.getId() != ultimo) {
            ultimo = r.getId();
            fantasma = vida;
        }
        fantasma = vida > fantasma ? vida : fantasma + (vida - fantasma) * 0.04F;

        int fase = Mth.clamp(r.fase(), 1, 4);
        boolean furia = r.tieneFuria() && !libre;
        int i = libre ? 5 : furia ? 4 : fase - 1;
        int x0 = (g.guiWidth() - ANCHO) / 2;
        int y0 = 5 + (NereaBarraHud.visible ? NereaBarraHud.ALTO + 6 : 0) + (AeralisBarraHud.visible ? AeralisBarraHud.ALTO + 6 : 0);
        g.blit(RenderPipelines.GUI_TEXTURED, MARCOS[i], x0, y0, 0.0F, 0.0F, ANCHO, ALTO, ANCHO, ALTO, ANCHO, ALTO, 0xFFFFFFFF);

        int hx = x0 + HUECO_X;
        int hy = y0 + HUECO_Y;
        int lleno = Math.round(HUECO_ANCHO * vida);
        int rastro = Math.round(HUECO_ANCHO * fantasma);
        if (rastro > lleno) {
            g.fill(hx + lleno, hy, hx + rastro, hy + HUECO_ALTO, 0xD8F0FFE0);
        }
        int color = 0xFF000000 | (libre ? ORO : furia ? COLOR_FURIA : COLOR_FASE[fase - 1]);
        int tinte = 0xFFFFFFFF;
        if (furia) {
            // Con la Furia, la energia y el rotulo laten deprisa.
            float k = 0.8F + 0.25F * Mth.sin((r.tickCount + parcial) * 0.45F);
            color = 0xFF000000 | escalar(COLOR_FURIA, k);
            tinte = 0xFF000000 | escalar(0xFFFFFF, 0.88F + 0.15F * Mth.sin((r.tickCount + parcial) * 0.45F));
        } else if (fase == 4 && !libre) {
            // En la ultima fase la energia late con la maldicion.
            tinte = 0xFF000000 | escalar(0xFFFFFF, 0.85F + 0.15F * Mth.sin((r.tickCount + parcial) * 0.25F));
        }
        // La energia de la tierra corre despacio hacia la derecha.
        int desplaza = 64 - (int) ((r.tickCount + parcial) * 0.6F) % 64;
        for (int x = 0; x < lleno; ) {
            int u = (x + desplaza) % 64;
            int w = Math.min(64 - u, lleno - x);
            g.blit(RenderPipelines.GUI_TEXTURED, RELLENOS[i], hx + x, hy, u, 0.0F, w, HUECO_ALTO, w, HUECO_ALTO, 64, HUECO_ALTO, tinte);
            x += w;
        }
        if (lleno >= 2) {
            // El frente encendido.
            int claro = 0xFF000000 | (libre ? 0xFFFBE8 : furia ? 0xF4FFF0 : CLARO_FASE[fase - 1]);
            g.fill(hx + lleno - 2, hy, hx + lleno, hy + HUECO_ALTO, claro);
        }
        // Las muescas: un colmillo de jade que se parte al pasar la vida por el.
        for (float corte : new float[]{0.75F, 0.5F, 0.25F}) {
            int ex = hx + Math.round(HUECO_ANCHO * corte) - 3;
            g.blit(RenderPipelines.GUI_TEXTURED, vida < corte ? COLMILLO_ROTO : COLMILLO, ex, hy - 4, 0.0F, 0.0F,
                    7, 12, 7, 12, 7, 12, 0xFFFFFFFF);
        }
        int cx = x0 + EMBLEMA_X - NUCLEO / 2;
        int cy = y0 + EMBLEMA_Y - NUCLEO / 2;
        if (!libre && r.hurtTime > 0) {
            cx += (r.hurtTime % 2 == 0) ? 1 : -1;   // tiembla al recibir el golpe
        }
        g.blit(RenderPipelines.GUI_TEXTURED, NUCLEOS[i], cx, cy, 0.0F, 0.0F, NUCLEO, NUCLEO, NUCLEO, NUCLEO, NUCLEO, NUCLEO,
                0xFFFFFFFF);

        g.blit(RenderPipelines.GUI_TEXTURED, NOMBRE, x0 + 92, y0 + 9, 0.0F, 0.0F, NOMBRE_ANCHO, LETRAS_ALTO,
                NOMBRE_ANCHO, LETRAS_ALTO, NOMBRE_ANCHO, LETRAS_ALTO, 0xFFFFFFFF);
        if (furia) {
            FuriaHud.cuentaAtras(g, r.getFuriaFin(), hx, hy, HUECO_ANCHO, COLOR_FURIA, parcial);
        }
        g.blit(RenderPipelines.GUI_TEXTURED, libre ? LIBRE : furia ? FURIA : FASES[fase - 1], hx + HUECO_ANCHO - ROTULO_ANCHO + 1, y0 + 8,
                0.0F, 0.0F, ROTULO_ANCHO, LETRAS_ALTO, ROTULO_ANCHO, LETRAS_ALTO, ROTULO_ANCHO, LETRAS_ALTO, color);

        int sello = r.getSello();
        if (sello > 0 && !libre) {
            selloBajo(g, r, hx, y0 + 35, sello, color);
        }
    }

    /** Los cuatro totems del Sello (en pie o partidos) y la losa del tiempo, bajo la barra. */
    private static void selloBajo(GuiGraphicsExtractor g, RajangEntity r, int x0, int y0, int sello, int color) {
        int rotos = r.getTotemsRotos();
        for (int i = 0; i < 4; i++) {
            boolean roto = (rotos & (1 << i)) != 0;
            // Un fondo oscuro detras, para que se lean sobre su cuerpo o el cielo.
            g.fill(x0 + 5 + i * 10, y0 - 1, x0 + 14 + i * 10, y0 + 10, 0xB0061209);
            g.blit(RenderPipelines.GUI_TEXTURED, roto ? TOTEM_ROTO : TOTEM, x0 + 6 + i * 10, y0, 0.0F, 0.0F,
                    7, 9, 7, 9, 7, 9, 0xFFFFFFFF);
        }
        float k = Mth.clamp(sello / (float) RajangEntity.SELLO_TICKS, 0.0F, 1.0F);
        int lx0 = x0 + 50;
        int lx1 = x0 + HUECO_ANCHO - 2;
        int ly = y0 + 2;
        g.fill(lx0, ly, lx1, ly + 5, 0xFF07160E);
        g.fill(lx0 + 1, ly + 1, lx1 - 1, ly + 4, 0xFF06120C);
        int w = Math.round((lx1 - lx0 - 2) * k);
        if (w > 0) {
            int c = k > 0.25F ? color : ((r.tickCount / 3) % 2 == 0 ? 0xFFFF5A3A : 0xFFFFC23A);
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

    /** El Rajang despierto mas cercano, a menos de 120 bloques. */
    private static @Nullable RajangEntity cercano(Minecraft mc) {
        if (mc.level == null || mc.player == null) {
            return null;
        }
        RajangEntity mejor = null;
        double d = 120 * 120;
        for (Entity e : mc.level.entitiesForRendering()) {
            if (e instanceof RajangEntity r && r.getEstado() != RajangEntity.DORMIDO && !r.isRemoved()) {
                double dd = r.distanceToSqr(mc.player);
                if (dd < d) {
                    d = dd;
                    mejor = r;
                }
            }
        }
        return mejor;
    }
}
