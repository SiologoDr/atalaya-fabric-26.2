package com.atalaya.client;

import com.atalaya.Atalaya;
import com.atalaya.entity.BrasaEnterradaEntity;
import com.atalaya.entity.MinijuegosNovilis;
import com.atalaya.entity.NovilisEntity;
import net.fabricmc.fabric.api.client.rendering.v1.hud.HudElement;
import net.minecraft.client.DeltaTracker;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphicsExtractor;
import net.minecraft.client.renderer.RenderPipelines;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.Identifier;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.phys.AABB;
import org.jspecify.annotations.Nullable;

/**
 * Lo que se ve en pantalla en los minijuegos de Novilis (novilis_minijuegos.py):
 *
 *   El Caballero Manda   su estandarte baja con la orden: el icono en el
 *                        medallon, la orden en el cartucho y, encima, la cinta
 *                        de oro con "¡Por el Sol...!" solo si es de verdad.
 *                        Una mecha se consume mientras se mira. Antes de la
 *                        primera, la regla.
 *   Piedra, Papel o T.   sobre la barra, las tres manos en sus casillas de
 *                        basalto con su tecla (la elegida, con llamas), la
 *                        cuenta, lo que saca el en su casilla y el marcador.
 *   Frio o Caliente      a la derecha, el termometro, que es su espada: el
 *                        fuego sube por la hoja de cristal (de frio a
 *                        ¡ardiendo!) y el pomo de sol brilla del color del
 *                        grado, segun lo cerca que este la brasa mas cercana.
 *
 * Lo de cada uno (la barra del tiempo y la cuenta) va en NovilisBarraHud.
 */
public class NovilisMinijuegosHud implements HudElement {

    private static final Identifier ESTANDARTE = tex("novilis_manda");
    private static final Identifier CINTA = tex("novilis_manda_cinta");
    private static final Identifier ORDENES = tex("novilis_ordenes");
    private static final Identifier MANOS = tex("novilis_rps");
    private static final Identifier CASILLA = tex("novilis_rps_casilla");
    private static final Identifier TERMOMETRO = tex("novilis_termometro");

    // Las medidas de novilis_minijuegos.py (cada texel, un pixel de interfaz).
    private static final int ESTANDARTE_ANCHO = 240;
    private static final int ESTANDARTE_ALTO = 72;
    /** El medallon del icono (su esquina) y el cartucho del texto (de x a x). */
    private static final int ICONO_X = 24;
    private static final int ICONO_Y = 19;
    private static final int CARTUCHO_X0 = 66;
    private static final int CARTUCHO_X1 = 222;
    private static final int CINTA_ANCHO = 112;
    private static final int CINTA_ALTO = 13;
    private static final int CASILLA_LADO = 40;
    /** El termometro: cada region mide 32 x 128; el cristal se llena de la fila 90 a la 8. */
    private static final int TERMO_ANCHO = 32;
    private static final int TERMO_ALTO = 128;
    private static final int TUBO_ABAJO = 90;
    private static final int TUBO_ARRIBA = 8;
    private static final int TINTA = 0xFF4A240A;
    /** Lo que sigue a la vista cada orden (ticks; el servidor la mira hasta el 46). */
    private static final int ORDEN_VISTA = 46;
    /** Las distancias del termometro (bloques): por debajo de cada una, el siguiente grado. */
    public static final double TEMPLADO = 14.0;
    public static final double CALIENTE = 8.0;
    public static final double ARDIENDO = 3.0;
    private static final int[] COLOR_GRADO = {0xFF5AB4FF, 0xFFFFD040, 0xFFFF8A1E, 0xFFFF3A20};
    private static final String[] GRADOS = {"frio", "templado", "caliente", "ardiendo"};

    /** El numero de la ultima orden vista y cuando llego (tick del cliente). */
    private int numeroVisto = -1;
    private float ordenDesde;

    private static Identifier tex(String nombre) {
        return Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "textures/gui/" + nombre + ".png");
    }

    @Override
    public void extractRenderState(GuiGraphicsExtractor g, DeltaTracker delta) {
        Minecraft mc = Minecraft.getInstance();
        NovilisEntity n = enMinijuego(mc);
        if (n == null || mc.player == null) {
            numeroVisto = -1;
            return;
        }
        float ahora = mc.player.tickCount + delta.getGameTimeDeltaPartialTick(false);
        switch (n.minijuego()) {
            case MinijuegosNovilis.MANDA -> manda(g, mc, n, ahora);
            case MinijuegosNovilis.PIEDRA -> piedra(g, mc, n, ahora);
            case MinijuegosNovilis.CALIENTE -> termometro(g, mc, ahora);
            default -> {
            }
        }
    }

    // ------------------------------------------------------------------
    //  El Caballero Manda: el estandarte con la orden
    // ------------------------------------------------------------------

    private void manda(GuiGraphicsExtractor g, Minecraft mc, NovilisEntity n, float ahora) {
        int info = n.getMiniInfo();
        int numero = MinijuegosNovilis.numeroManda(info);
        if (numero != numeroVisto) {
            numeroVisto = numero;
            ordenDesde = ahora;
        }
        float desde = ahora - ordenDesde;
        // Baja en 4 ticks y, pasada la orden, se enrolla (antes de la primera, se queda).
        float abierto = Mth.clamp(desde / 4.0F, 0.0F, 1.0F);
        if (numero > 0 && desde > ORDEN_VISTA) {
            abierto = Mth.clamp(1.0F - (desde - ORDEN_VISTA) / 4.0F, 0.0F, 1.0F);
        }
        if (abierto <= 0.0F) {
            return;
        }
        int x0 = (g.guiWidth() - ESTANDARTE_ANCHO) / 2;
        int y0 = Math.min(84, g.guiHeight() / 4 + 8);
        int alto = Math.max(9, Math.round(ESTANDARTE_ALTO * abierto));
        // El pano se desenrolla de arriba abajo (la vara siempre entera).
        g.blit(RenderPipelines.GUI_TEXTURED, ESTANDARTE, x0, y0, 0.0F, 0.0F, ESTANDARTE_ANCHO, alto, ESTANDARTE_ANCHO, alto,
                ESTANDARTE_ANCHO, ESTANDARTE_ALTO, 0xFFFFFFFF);
        if (abierto < 0.9F) {
            return;
        }
        int tx = x0 + (CARTUCHO_X0 + CARTUCHO_X1) / 2;
        int cabe = CARTUCHO_X1 - CARTUCHO_X0 - 14;
        if (numero == 0) {
            // La regla: el titulo, la cinta de oro y "solo si lo digo asi"; en el medallon, el ojo que mira al sol.
            g.blit(RenderPipelines.GUI_TEXTURED, ORDENES, x0 + ICONO_X, y0 + ICONO_Y, 64.0F, 0.0F, 32, 32, 32, 32, 128, 32, 0xFFFFFFFF);
            textoCabe(g, mc, Component.translatable("hud.atalaya.novilis.manda_titulo"), tx, y0 + 22, 2.0F, cabe, 0xFFFFD86A);
            cinta(g, mc, tx, y0 + 29);
            textoCabe(g, mc, Component.translatable("hud.atalaya.novilis.manda_regla_corta"), tx, y0 + 48, 1.0F, cabe, 0xFFE8D8B8);
            return;
        }
        int orden = Mth.clamp(MinijuegosNovilis.ordenManda(info), 0, 3);
        boolean deVerdad = MinijuegosNovilis.deVerdadManda(info);
        // El icono de la orden, en el medallon, a su tamano (cada texel un pixel).
        g.blit(RenderPipelines.GUI_TEXTURED, ORDENES, x0 + ICONO_X, y0 + ICONO_Y, orden * 32.0F, 0.0F, 32, 32, 32, 32, 128, 32,
                0xFFFFFFFF);
        // "¡Por el Sol...!" va en su cinta de oro: si no esta, es trampa.
        if (deVerdad) {
            cinta(g, mc, tx, y0 + 16);
        }
        textoCabe(g, mc, Component.translatable("hud.atalaya.novilis.orden_" + MinijuegosNovilis.ORDENES[orden]), tx,
                deVerdad ? y0 + 39 : y0 + 34, 2.0F, cabe, 0xFFFFFFFF);
        // La mecha de esta orden: se consume mientras se mira, con una brasa en la punta.
        float k = Mth.clamp(1.0F - (desde - 8.0F) / (ORDEN_VISTA - 8.0F), 0.0F, 1.0F);
        int w = Math.round(110 * k);
        int my = y0 + 50;
        g.fill(tx - 55, my, tx + 55, my + 2, 0xFF2B1D1C);
        if (w > 0) {
            g.fill(tx - 55, my, tx - 55 + w, my + 2, 0xFFC07C22);
            g.fill(tx - 55, my, tx - 55 + w, my + 1, 0xFFFFD77A);
            int bx = tx - 55 + w;
            int brillo = ((int) (ahora * 2) % 2 == 0) ? 0xFFFFF0D0 : 0xFFFF8A1E;
            g.fill(bx - 1, my - 1, bx + 1, my + 3, brillo);
        }
    }

    /** La cinta de oro con "¡Por el Sol...!" en tinta, centrada en x. */
    private static void cinta(GuiGraphicsExtractor g, Minecraft mc, int x, int y) {
        g.blit(RenderPipelines.GUI_TEXTURED, CINTA, x - CINTA_ANCHO / 2, y, 0.0F, 0.0F, CINTA_ANCHO, CINTA_ALTO, CINTA_ANCHO,
                CINTA_ALTO, CINTA_ANCHO, CINTA_ALTO, 0xFFFFFFFF);
        Component t = Component.translatable("hud.atalaya.novilis.manda_por_el_sol");
        g.text(mc.font, t, x - mc.font.width(t) / 2, y + 2, TINTA, false);
    }

    /** Un texto centrado a la escala dada, o a la que quepa en 'cabe' pixeles. */
    private static void textoCabe(GuiGraphicsExtractor g, Minecraft mc, Component t, int x, int y, float escala, int cabe, int color) {
        float e = Math.min(escala, cabe / (float) Math.max(1, mc.font.width(t)));
        g.pose().pushMatrix();
        g.pose().translate(x, y);
        g.pose().scale(e, e);
        g.centeredText(mc.font, t, 0, -4, color);
        g.pose().popMatrix();
    }

    // ------------------------------------------------------------------
    //  Piedra, Papel o Tijera: las tres manos, la cuenta y el marcador
    // ------------------------------------------------------------------

    private static void piedra(GuiGraphicsExtractor g, Minecraft mc, NovilisEntity n, float ahora) {
        int info = n.getMiniInfo();
        int ronda = MinijuegosNovilis.rondaPiedra(info);
        int golpe = MinijuegosNovilis.golpePiedra(info);
        int suya = MinijuegosNovilis.suyaPiedra(info);
        int resultado = MinijuegosNovilis.resultadoPiedra(info);
        int cx = g.guiWidth() / 2;
        // Por encima de la barra de accion (donde salen los avisos de cada ronda).
        int y = g.guiHeight() - 128;
        int elegida = mc.player == null ? -1 : mc.player.getInventory().getSelectedSlot();
        // Las tres manos en sus casillas de basalto, con su tecla; la elegida, encendida y algo mas arriba.
        for (int i = 0; i < 3; i++) {
            int x = cx - 66 + i * 46;
            boolean esta = elegida == i;
            int dy = esta ? -3 : 0;
            casilla(g, x, y + dy, esta);
            g.blit(RenderPipelines.GUI_TEXTURED, MANOS, x + 4, y + 5 + dy, i * 32.0F, 0.0F, 32, 32, 32, 32, 96, 32,
                    esta ? 0xFFFFFFFF : 0xFFB8A898);
            g.centeredText(mc.font, Integer.toString(i + 1), x + CASILLA_LADO / 2, y + CASILLA_LADO + 2 + dy,
                    esta ? 0xFFFFD86A : 0xFFB0A8A0);
        }
        // La cuenta, o lo que ha sacado el (en su casilla, encendida) y como ha ido.
        if (golpe >= 1 && golpe <= 2) {
            String clave = golpe == 1 ? "hud.atalaya.novilis.piedra_1" : "hud.atalaya.novilis.piedra_2";
            textoCabe(g, mc, Component.translatable(clave), cx, y - 18, 2.0F, 200, 0xFFFFF0C8);
        } else if (golpe == 3 && suya > 0) {
            int sx = cx + 8;
            int sy = y - 48;
            casilla(g, sx, sy, true);
            g.blit(RenderPipelines.GUI_TEXTURED, MANOS, sx + 4, sy + 5, (suya - 1) * 32.0F, 0.0F, 32, 32, 32, 32, 96, 32, 0xFFFFFFFF);
            Component t = Component.translatable("hud.atalaya.novilis.piedra_3");
            float e = 2.0F;
            g.pose().pushMatrix();
            g.pose().translate(sx - 6 - mc.font.width(t) * e, sy + 14);
            g.pose().scale(e, e);
            g.text(mc.font, t, 0, 0, 0xFFFFD86A, true);
            g.pose().popMatrix();
            if (resultado > 0) {
                int color = resultado == 1 ? 0xFFFFD86A : resultado == 2 ? 0xFFFF6A4A : 0xFFD8D0C8;
                // A la derecha de su casilla, frente al "¡Tijera!" de la izquierda.
                g.text(mc.font, Component.translatable("hud.atalaya.novilis.piedra_resultado_" + resultado), sx + CASILLA_LADO + 6, sy + 16,
                        color, true);
            }
        } else if (ronda > 0) {
            g.centeredText(mc.font, Component.translatable("hud.atalaya.novilis.piedra_elige"), cx, y - 14, 0xFFE8E2D6);
        }
        // El marcador, a la derecha de las casillas.
        g.text(mc.font, Component.translatable("hud.atalaya.novilis.piedra_marcador",
                MinijuegosNovilis.grupoPiedra(info), MinijuegosNovilis.elPiedra(info)), cx + 78, y + 16, 0xFFFFF0C8, true);
    }

    private static void casilla(GuiGraphicsExtractor g, int x, int y, boolean encendida) {
        g.blit(RenderPipelines.GUI_TEXTURED, CASILLA, x, y, encendida ? CASILLA_LADO : 0.0F, 0.0F, CASILLA_LADO, CASILLA_LADO,
                CASILLA_LADO, CASILLA_LADO, CASILLA_LADO * 2, CASILLA_LADO, 0xFFFFFFFF);
    }

    // ------------------------------------------------------------------
    //  Frio o Caliente: el termometro es su espada
    // ------------------------------------------------------------------

    private static void termometro(GuiGraphicsExtractor g, Minecraft mc, float ahora) {
        if (mc.level == null || mc.player == null) {
            return;
        }
        double d = Double.MAX_VALUE;
        AABB caja = mc.player.getBoundingBox().inflate(96, 32, 96);
        for (BrasaEnterradaEntity b : mc.level.getEntitiesOfClass(BrasaEnterradaEntity.class, caja, BrasaEnterradaEntity::enterrada)) {
            d = Math.min(d, Math.hypot(b.getX() - mc.player.getX(), b.getZ() - mc.player.getZ()));
        }
        if (d == Double.MAX_VALUE) {
            return;
        }
        int grado = d >= TEMPLADO ? 0 : d >= CALIENTE ? 1 : d >= ARDIENDO ? 2 : 3;
        // Lo que sube el fuego por la hoja: casi nada a 30 bloques, lleno encima.
        float lleno = (float) Mth.clamp(1.0 - d / 30.0, 0.04, 1.0);
        int color = COLOR_GRADO[grado];
        int tinte = 0xFFFFFFFF;
        if (grado == 3) {
            // Ardiendo: late.
            float late = 0.8F + 0.2F * Mth.sin(ahora * 0.8F);
            int v = (int) (255 * late);
            tinte = 0xFF000000 | (v << 16) | (v << 8) | v;
        }
        int x = g.guiWidth() - TERMO_ANCHO - 10;
        int y = g.guiHeight() / 2 - TERMO_ALTO / 2;
        // El fondo, el fuego que sube (recortado desde abajo), el pomo del color del grado y, encima, el frente.
        pieza(g, x, y, 0, 0, TERMO_ALTO, 0xFFFFFFFF);
        int arriba = Math.round(TUBO_ABAJO - lleno * (TUBO_ABAJO - TUBO_ARRIBA));
        pieza(g, x, y, 1, arriba, TUBO_ABAJO + 1 - arriba, tinte);
        pieza(g, x, y, 3, 0, TERMO_ALTO, color);
        pieza(g, x, y, 2, 0, TERMO_ALTO, 0xFFFFFFFF);
        Component nombre = Component.translatable("hud.atalaya.novilis.termometro_" + GRADOS[grado]);
        int tw = mc.font.width(nombre);
        g.text(mc.font, nombre, Math.min(x + TERMO_ANCHO / 2 - tw / 2, g.guiWidth() - tw - 4), y + TERMO_ALTO + 3, color, true);
    }

    /** Las filas desde 'desde' (alto filas) de la region 'region' del termometro, en su sitio. */
    private static void pieza(GuiGraphicsExtractor g, int x, int y, int region, int desde, int alto, int tinte) {
        if (alto <= 0) {
            return;
        }
        g.blit(RenderPipelines.GUI_TEXTURED, TERMOMETRO, x, y + desde, region * (float) TERMO_ANCHO, desde, TERMO_ANCHO, alto,
                TERMO_ANCHO, alto, TERMO_ANCHO * 4, TERMO_ALTO, tinte);
    }

    /** El Novilis con un minijuego en marcha mas cercano (a menos de 120 bloques). */
    private static @Nullable NovilisEntity enMinijuego(Minecraft mc) {
        if (mc.level == null || mc.player == null) {
            return null;
        }
        NovilisEntity mejor = null;
        double d = 120 * 120;
        for (Entity e : mc.level.entitiesForRendering()) {
            if (e instanceof NovilisEntity n && n.minijuego() != MinijuegosNovilis.NINGUNO && !n.isRemoved() && !n.isDeadOrDying()) {
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
