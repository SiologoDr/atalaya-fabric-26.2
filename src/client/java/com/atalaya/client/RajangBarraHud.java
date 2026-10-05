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
 * La barra de jefe de Rajang, propia (rajang_hud.py): marco de bloques de jade
 * con incrustaciones de oro y la cresta de cristales, el sol de jade de la
 * fase en el emblema (cada vez mas agrietado), la energia de la tierra dentro
 * con el color de la maldicion (jade, verde, lima, amarillo), un rastro claro
 * que se queda atras al recibir dano y tres colmillos en las muescas de fase,
 * que se parten cuando la vida pasa por ellos. "RAJANG" y la fase, en letras
 * de pixel.
 *
 * Durante el Sello de la Tierra, debajo, el tiempo que queda (una losa que se
 * vacia, roja al final) y los cuatro totems: encendidos los que siguen en pie.
 * Con la Furia de Jade, la energia late en verde vivo y el rotulo dice FURIA.
 *
 * Misma composicion y medidas que las de Nerea y Aeralis. Si estan a la vista,
 * la de Rajang va debajo.
 */
public class RajangBarraHud implements HudElement {

    private static final Identifier MARCO = tex("rajang_barra_marco");
    private static final Identifier RELLENO = tex("rajang_barra_relleno");
    private static final Identifier MUESCA = tex("rajang_barra_muesca");
    private static final Identifier MUESCA_ROTA = tex("rajang_barra_muesca_rota");
    private static final Identifier[] SOLES = {tex("rajang_barra_sol_1"), tex("rajang_barra_sol_2"),
            tex("rajang_barra_sol_3"), tex("rajang_barra_sol_4")};
    private static final Identifier SOL_LIBRE = tex("rajang_barra_sol_libre");
    private static final Identifier NOMBRE = tex("rajang_barra_nombre");
    private static final Identifier[] FASES = {tex("rajang_barra_fase_1"), tex("rajang_barra_fase_2"),
            tex("rajang_barra_fase_3"), tex("rajang_barra_fase_4")};
    private static final Identifier LIBRE = tex("rajang_barra_libre");
    private static final Identifier FURIA = tex("rajang_barra_furia");
    /** El verde vivo de la Furia de Jade. */
    private static final int COLOR_FURIA = 0x7CFF3A;
    private static final int NOMBRE_ANCHO = 48;
    private static final int ROTULO_ANCHO = 64;
    private static final int LETRAS_ALTO = 10;

    /** Color de la energia en cada fase, y el oro de la liberacion. */
    private static final int[] COLOR_FASE = {0x58C886, 0x8CFF5A, 0xC8FF2A, 0xE6FF4A};
    private static final int ORO = 0xF8D97C;

    private static final int ANCHO = 208;
    private static final int ALTO = 26;
    private static final int HUECO_X = 28;
    private static final int HUECO_Y = 9;
    private static final int HUECO_ANCHO = 172;
    private static final int HUECO_ALTO = 8;
    private static final int EMBLEMA = 13;
    private static final int SOL = 16;

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
        int x0 = (g.guiWidth() - ANCHO) / 2;
        int y0 = 5 + (NereaBarraHud.visible ? ALTO + 6 : 0) + (AeralisBarraHud.visible ? ALTO + 6 : 0);
        g.blit(RenderPipelines.GUI_TEXTURED, MARCO, x0, y0, 0.0F, 0.0F, ANCHO, ALTO, ANCHO, ALTO, ANCHO, ALTO, 0xFFFFFFFF);

        int hx = x0 + HUECO_X;
        int hy = y0 + HUECO_Y;
        int lleno = Math.round(HUECO_ANCHO * vida);
        int rastro = Math.round(HUECO_ANCHO * fantasma);
        if (rastro > lleno) {
            g.fill(hx + lleno, hy, hx + rastro, hy + HUECO_ALTO, 0xD8F0FFE0);
        }
        int color = 0xFF000000 | (libre ? ORO : COLOR_FASE[fase - 1]);
        boolean furia = r.tieneFuria() && !libre;
        if (furia) {
            // Con la Furia, la energia late en verde vivo, deprisa.
            float k = 0.8F + 0.25F * Mth.sin((r.tickCount + parcial) * 0.45F);
            color = 0xFF000000 | escalar(COLOR_FURIA, k);
        } else if (fase == 4 && !libre) {
            // En la ultima fase el sol late con la maldicion.
            float k = 0.85F + 0.2F * Mth.sin((r.tickCount + parcial) * 0.25F);
            color = 0xFF000000 | escalar(COLOR_FASE[3], k);
        }
        // La energia de la tierra corre despacio hacia la derecha.
        int desplaza = 64 - (int) ((r.tickCount + parcial) * 0.6F) % 64;
        for (int x = 0; x < lleno; ) {
            int u = (x + desplaza) % 64;
            int w = Math.min(64 - u, lleno - x);
            g.blit(RenderPipelines.GUI_TEXTURED, RELLENO, hx + x, hy, u, 0.0F, w, HUECO_ALTO, w, HUECO_ALTO, 64, HUECO_ALTO, color);
            x += w;
        }
        for (float corte : new float[]{0.75F, 0.5F, 0.25F}) {
            int ex = hx + Math.round(HUECO_ANCHO * corte) - 3;
            g.blit(RenderPipelines.GUI_TEXTURED, vida < corte ? MUESCA_ROTA : MUESCA, ex, hy - 2, 0.0F, 0.0F,
                    6, 12, 6, 12, 6, 12, 0xFFFFFFFF);
        }
        Identifier sol = libre ? SOL_LIBRE : SOLES[fase - 1];
        int cx = x0 + EMBLEMA - SOL / 2;
        int cy = y0 + EMBLEMA - SOL / 2;
        if (!libre && r.hurtTime > 0) {
            cx += (r.hurtTime % 2 == 0) ? 1 : -1;   // tiembla al recibir el golpe
        }
        g.blit(RenderPipelines.GUI_TEXTURED, sol, cx, cy, 0.0F, 0.0F, SOL, SOL, SOL, SOL, SOL, SOL, 0xFFFFFFFF);

        int ly = y0 + 7 - LETRAS_ALTO;
        g.blit(RenderPipelines.GUI_TEXTURED, NOMBRE, hx, ly, 0.0F, 0.0F, NOMBRE_ANCHO, LETRAS_ALTO,
                NOMBRE_ANCHO, LETRAS_ALTO, NOMBRE_ANCHO, LETRAS_ALTO, 0xFFFFFFFF);
        g.blit(RenderPipelines.GUI_TEXTURED, libre ? LIBRE : furia ? FURIA : FASES[fase - 1], hx + HUECO_ANCHO - ROTULO_ANCHO + 1, ly,
                0.0F, 0.0F, ROTULO_ANCHO, LETRAS_ALTO, ROTULO_ANCHO, LETRAS_ALTO, ROTULO_ANCHO, LETRAS_ALTO, color);

        int sello = r.getSello();
        if (sello > 0 && !libre) {
            selloBajo(g, r, hx, y0 + ALTO + 1, sello, parcial);
        }
    }

    /** El tiempo del Sello y sus cuatro totems, bajo la barra. */
    private static void selloBajo(GuiGraphicsExtractor g, RajangEntity r, int x0, int y0, int sello, float parcial) {
        float k = Mth.clamp(sello / (float) RajangEntity.SELLO_TICKS, 0.0F, 1.0F);
        int ancho = HUECO_ANCHO - 44;
        int x = x0 + 44;
        g.fill(x - 1, y0 - 1, x + ancho + 1, y0 + 4, 0xC0102016);
        int color = k > 0.25F ? 0xFF7CFF5A : ((r.tickCount / 3) % 2 == 0 ? 0xFFFF5A3A : 0xFFFFC23A);
        g.fill(x, y0, x + Math.round(ancho * k), y0 + 3, color);
        int rotos = r.getTotemsRotos();
        for (int i = 0; i < 4; i++) {
            int tx = x0 + i * 10;
            boolean roto = (rotos & (1 << i)) != 0;
            g.fill(tx, y0 - 1, tx + 7, y0 + 5, 0xD0182A1E);
            g.fill(tx + 1, y0, tx + 6, y0 + 4, roto ? 0xFF3A3A32 : 0xFF8CFF5A);
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
