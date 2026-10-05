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
 * La barra de jefe de Nerea, propia: un marco de prismarina vieja con coral
 * (nerea_hud.py), el corazon de la fase en el emblema, agua que corre dentro
 * con el color de la maldicion (cian, violeta, magenta, rojo), un rastro blanco
 * que se queda atras al recibir dano y tres eslabones en las muescas de fase,
 * que se parten cuando la vida pasa por ellos.
 *
 * No usa la barra de vanilla: lee la vida y la fase de la Nerea mas cercana,
 * que el cliente ya tiene sincronizadas.
 */
public class NereaBarraHud implements HudElement {

    private static final Identifier MARCO = tex("nerea_barra_marco");
    private static final Identifier AGUA = tex("nerea_barra_agua");
    private static final Identifier ESLABON = tex("nerea_barra_eslabon");
    private static final Identifier ESLABON_ROTO = tex("nerea_barra_eslabon_roto");
    private static final Identifier[] CORAZONES = {tex("nerea_barra_corazon_1"), tex("nerea_barra_corazon_2"),
            tex("nerea_barra_corazon_3"), tex("nerea_barra_corazon_4")};
    private static final Identifier CORAZON_LIBRE = tex("nerea_barra_corazon_libre");
    /** Las letras, en pixel (nerea_hud.py): nada de la fuente de Minecraft. */
    private static final Identifier NOMBRE = tex("nerea_barra_nombre");
    private static final Identifier[] FASES = {tex("nerea_barra_fase_1"), tex("nerea_barra_fase_2"),
            tex("nerea_barra_fase_3"), tex("nerea_barra_fase_4")};
    private static final Identifier LIBRE = tex("nerea_barra_libre");
    private static final int NOMBRE_ANCHO = 36;
    private static final int ROTULO_ANCHO = 64;
    private static final int LETRAS_ALTO = 10;

    /** Color del agua en cada fase, y el oro de la liberacion. */
    private static final int[] COLOR_FASE = {0x3FE0CC, 0x9A6BFF, 0xD43CFF, 0xFF2050};
    private static final int ORO = 0xFFC23A;

    // Medidas del marco (nerea_barra_marco.png, 208x26). Compacto: con 30 o
    // 40 jugadores la pelea se mira hacia arriba, y la barra no debe taparla.
    private static final int ANCHO = 208;
    public static final int ALTO = 26;
    private static final int HUECO_X = 28;
    private static final int HUECO_Y = 9;
    private static final int HUECO_ANCHO = 172;
    private static final int HUECO_ALTO = 8;
    /** Centro del emblema redondo y lado del corazon que va dentro. */
    private static final int EMBLEMA = 13;
    private static final int CORAZON = 16;

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
        int x0 = (g.guiWidth() - ANCHO) / 2;
        int y0 = 5;
        g.blit(RenderPipelines.GUI_TEXTURED, MARCO, x0, y0, 0.0F, 0.0F, ANCHO, ALTO, ANCHO, ALTO, ANCHO, ALTO, 0xFFFFFFFF);

        int hx = x0 + HUECO_X;
        int hy = y0 + HUECO_Y;
        int lleno = Math.round(HUECO_ANCHO * vida);
        int rastro = Math.round(HUECO_ANCHO * fantasma);
        if (rastro > lleno) {
            g.fill(hx + lleno, hy, hx + rastro, hy + HUECO_ALTO, 0xD8F4FFFF);
        }
        // El agua corre hacia la izquierda: el relleno es un mosaico que se desplaza.
        int color = 0xFF000000 | (libre ? ORO : COLOR_FASE[fase - 1]);
        if (fase == 4 && !libre) {
            // En la ultima fase late: el color sube y baja con el corazon.
            float k = 0.75F + 0.25F * Mth.sin((n.tickCount + parcial) * 0.5F);
            color = 0xFF000000 | escalar(COLOR_FASE[3], k);
        }
        int desplaza = (int) ((n.tickCount + parcial) * 0.8F) % 64;
        for (int x = 0; x < lleno; ) {
            int u = (x + desplaza) % 64;
            int w = Math.min(64 - u, lleno - x);
            g.blit(RenderPipelines.GUI_TEXTURED, AGUA, hx + x, hy, u, 0.0F, w, HUECO_ALTO, w, HUECO_ALTO, 64, HUECO_ALTO, color);
            x += w;
        }
        // Las muescas de fase: un eslabon que se parte al pasar la vida por el.
        for (float corte : new float[]{0.75F, 0.5F, 0.25F}) {
            int ex = hx + Math.round(HUECO_ANCHO * corte) - 3;
            g.blit(RenderPipelines.GUI_TEXTURED, vida < corte ? ESLABON_ROTO : ESLABON, ex, hy - 2, 0.0F, 0.0F,
                    6, 12, 6, 12, 6, 12, 0xFFFFFFFF);
        }
        // El emblema: el corazon de la fase (o el liberado).
        Identifier corazon = libre ? CORAZON_LIBRE : CORAZONES[fase - 1];
        int cx = x0 + EMBLEMA - CORAZON / 2;
        int cy = y0 + EMBLEMA - CORAZON / 2;
        if (!libre && n.hurtTime > 0) {
            cy += (n.hurtTime % 2 == 0) ? 1 : -1;   // da un respingo al recibir el golpe
        }
        g.blit(RenderPipelines.GUI_TEXTURED, corazon, cx, cy, 0.0F, 0.0F, CORAZON, CORAZON, CORAZON, CORAZON,
                CORAZON, CORAZON, 0xFFFFFFFF);

        // Encima del marco: el nombre a la izquierda y la fase a la derecha
        // (tenida con el color de la fase, como el agua), donde no hay coral.
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
