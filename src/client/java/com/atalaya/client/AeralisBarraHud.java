package com.atalaya.client;

import com.atalaya.Atalaya;
import com.atalaya.entity.AeralisEntity;
import com.atalaya.entity.AeralisGeometria;
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
 * La barra de jefe de Aeralis, propia (aeralis_hud.py): marco de marmol de
 * nube con dos alitas, el ojo de la tormenta de la fase en el emblema (cada
 * vez mas agrietado), viento que corre dentro con el color de la fase (cielo,
 * anil, violeta, magenta), un rastro blanco que se queda atras al recibir dano
 * y tres plumas en las muescas de fase, que se rasgan cuando la vida pasa por
 * ellas. "AERALIS" y la fase, en letras de pixel.
 *
 * Misma composicion y medidas que la de Nerea. Si las dos estan a la vista, la
 * de Aeralis va debajo.
 */
public class AeralisBarraHud implements HudElement {

    private static final Identifier MARCO = tex("aeralis_barra_marco");
    private static final Identifier VIENTO = tex("aeralis_barra_viento");
    private static final Identifier PLUMA = tex("aeralis_barra_pluma");
    private static final Identifier PLUMA_ROTA = tex("aeralis_barra_pluma_rota");
    private static final Identifier[] NUCLEOS = {tex("aeralis_barra_nucleo_1"), tex("aeralis_barra_nucleo_2"),
            tex("aeralis_barra_nucleo_3"), tex("aeralis_barra_nucleo_4")};
    private static final Identifier NUCLEO_LIBRE = tex("aeralis_barra_nucleo_libre");
    private static final Identifier NOMBRE = tex("aeralis_barra_nombre");
    private static final Identifier[] FASES = {tex("aeralis_barra_fase_1"), tex("aeralis_barra_fase_2"),
            tex("aeralis_barra_fase_3"), tex("aeralis_barra_fase_4")};
    private static final Identifier LIBRE = tex("aeralis_barra_libre");
    private static final int NOMBRE_ANCHO = 48;
    private static final int ROTULO_ANCHO = 64;
    private static final int LETRAS_ALTO = 10;

    /** Color del viento en cada fase, y el oro de la liberacion. */
    private static final int[] COLOR_FASE = {0x5FD2FF, 0x7F8CFF, 0xB07CFF, 0xFF4FD8};
    private static final int ORO = 0xFFC23A;

    private static final int ANCHO = 208;
    private static final int ALTO = 26;
    private static final int HUECO_X = 28;
    private static final int HUECO_Y = 9;
    private static final int HUECO_ANCHO = 172;
    private static final int HUECO_ALTO = 8;
    private static final int EMBLEMA = 13;
    private static final int NUCLEO = 16;

    private float fantasma = 1.0F;
    private int ultimo = -1;

    private static Identifier tex(String nombre) {
        return Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "textures/gui/" + nombre + ".png");
    }

    @Override
    public void extractRenderState(GuiGraphicsExtractor g, DeltaTracker delta) {
        Minecraft mc = Minecraft.getInstance();
        AeralisEntity a = cercana(mc);
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
        int x0 = (g.guiWidth() - ANCHO) / 2;
        int y0 = 5 + (NereaBarraHud.visible ? ALTO + 6 : 0);
        g.blit(RenderPipelines.GUI_TEXTURED, MARCO, x0, y0, 0.0F, 0.0F, ANCHO, ALTO, ANCHO, ALTO, ANCHO, ALTO, 0xFFFFFFFF);

        int hx = x0 + HUECO_X;
        int hy = y0 + HUECO_Y;
        int lleno = Math.round(HUECO_ANCHO * vida);
        int rastro = Math.round(HUECO_ANCHO * fantasma);
        if (rastro > lleno) {
            g.fill(hx + lleno, hy, hx + rastro, hy + HUECO_ALTO, 0xD8F4FFFF);
        }
        int color = 0xFF000000 | (libre ? ORO : COLOR_FASE[fase - 1]);
        if (fase == 4 && !libre) {
            // En la ultima fase la tormenta parpadea con los rayos.
            float k = ((a.tickCount / 3) % 9 == 0) ? 1.25F : 0.85F + 0.15F * Mth.sin((a.tickCount + parcial) * 0.4F);
            color = 0xFF000000 | escalar(COLOR_FASE[3], k);
        }
        // El viento corre hacia la derecha.
        int desplaza = 64 - (int) ((a.tickCount + parcial) * 1.2F) % 64;
        for (int x = 0; x < lleno; ) {
            int u = (x + desplaza) % 64;
            int w = Math.min(64 - u, lleno - x);
            g.blit(RenderPipelines.GUI_TEXTURED, VIENTO, hx + x, hy, u, 0.0F, w, HUECO_ALTO, w, HUECO_ALTO, 64, HUECO_ALTO, color);
            x += w;
        }
        for (float corte : new float[]{0.75F, 0.5F, 0.25F}) {
            int ex = hx + Math.round(HUECO_ANCHO * corte) - 3;
            g.blit(RenderPipelines.GUI_TEXTURED, vida < corte ? PLUMA_ROTA : PLUMA, ex, hy - 2, 0.0F, 0.0F,
                    6, 12, 6, 12, 6, 12, 0xFFFFFFFF);
        }
        Identifier nucleo = libre ? NUCLEO_LIBRE : NUCLEOS[fase - 1];
        int cx = x0 + EMBLEMA - NUCLEO / 2;
        int cy = y0 + EMBLEMA - NUCLEO / 2;
        if (!libre && a.hurtTime > 0) {
            cx += (a.hurtTime % 2 == 0) ? 1 : -1;   // tiembla al recibir el golpe
        }
        g.blit(RenderPipelines.GUI_TEXTURED, nucleo, cx, cy, 0.0F, 0.0F, NUCLEO, NUCLEO, NUCLEO, NUCLEO,
                NUCLEO, NUCLEO, 0xFFFFFFFF);

        int ly = y0 + 7 - LETRAS_ALTO;
        g.blit(RenderPipelines.GUI_TEXTURED, NOMBRE, hx, ly, 0.0F, 0.0F, NOMBRE_ANCHO, LETRAS_ALTO,
                NOMBRE_ANCHO, LETRAS_ALTO, NOMBRE_ANCHO, LETRAS_ALTO, 0xFFFFFFFF);
        g.blit(RenderPipelines.GUI_TEXTURED, libre ? LIBRE : FASES[fase - 1], hx + HUECO_ANCHO - ROTULO_ANCHO + 1, ly,
                0.0F, 0.0F, ROTULO_ANCHO, LETRAS_ALTO, ROTULO_ANCHO, LETRAS_ALTO, ROTULO_ANCHO, LETRAS_ALTO, color);
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
