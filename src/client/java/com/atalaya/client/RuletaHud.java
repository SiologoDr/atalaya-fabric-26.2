package com.atalaya.client;

import com.atalaya.Atalaya;
import net.fabricmc.fabric.api.client.rendering.v1.hud.HudElement;
import net.minecraft.client.DeltaTracker;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphicsExtractor;
import net.minecraft.client.renderer.RenderPipelines;
import net.minecraft.resources.Identifier;
import net.minecraft.util.Mth;

/**
 * Lo que se ve de la Ruleta (el calendario, en RuletaCliente): un medallon de casino, a pixeles (ruleta.py), en el
 * que el rodillo lo ocupa casi todo. Segunda version (17-10-2026). Juan: "usar bien su espacio, asi como hace la ruleta
 * de DEDsafio, que es su circulo"; "mas inmersivo y dar esa tension".
 *
 * Se pinta a la resolucion de la pantalla, con el medallon a una escala entera (los pixeles de su dibujo, todos
 * iguales). Lo de la hoja es fijo; lo que se mueve o se enciende va encima:
 * <pre>
 *   el fondo       el mundo se apaga y se cierra la vineta (mas en el suspense, y late con el corazon); detras del
 *                  medallon, la luz del icono que pasa por la linea de premio, rayos que giran con el rodillo y
 *                  chispas que el medallon se traga en espiral
 *   el rodillo     detras del hueco redondo: un tambor crema, con los iconos aplastados segun su giro y corridos cuando
 *                  va deprisa, y la sombra de la lente en el borde
 *   las luces      la luz corre por las 22 bombillas del aro con el rodillo; en el suspense se apagan y solo laten; la
 *                  gema del icono que pasa se enciende; al parar, todo del color del final
 *   el medallon    entra girando sobre si mismo; en el suspense se acerca; el cerrojo lo sacude; al final se va girando
 *   el final       el icono salta con su brillo, los rayos de su color, destellos y monedas; despues vuela al chat
 * </pre>
 */
public class RuletaHud implements HudElement {

    // La hoja del medallon (ruleta.py: las mismas medidas).
    private static final Identifier MAQUINA = textura("maquina");
    private static final Identifier ICONOS = textura("iconos");
    private static final Identifier BORROSOS = textura("iconos_borrosos");
    private static final int HOJA = 256;
    private static final int MED_W = 176;
    private static final int MED_H = 196;
    private static final float CX = 88.0F;
    private static final float CY = 106.0F;
    private static final float R_VENTANA = 57.0F;
    private static final float R_CROMO = 62.0F;
    private static final float R_ARO = 86.0F;
    private static final float FAROL_X = 88.5F;
    private static final float FAROL_Y = 14.4F;
    private static final int ICONO = 48;
    /** Las 22 bombillas del aro, en el orden en que corre la luz (ruleta.py, bombillas()). */
    private static final int[][] BOMBILLAS = {{119, 32}, {137, 42}, {152, 57}, {162, 75}, {168, 95}, {168, 117},
            {162, 137}, {152, 155}, {137, 170}, {119, 180}, {99, 186}, {77, 186}, {57, 180}, {39, 170}, {24, 155},
            {14, 137}, {8, 117}, {8, 95}, {14, 75}, {24, 57}, {39, 42}, {57, 32}};
    /** Las gemas, una por final (mob, dificultad, penalizacion, minijuego). */
    private static final int[][] GEMAS = {{40, 58}, {136, 58}, {136, 154}, {40, 154}};
    // Las piezas suaves del Momento (blancas: se tiñen).
    private static final Identifier BRILLO = suave("brillo");
    private static final Identifier HAZ = suave("haz");
    private static final Identifier VINETA = suave("vineta");

    /** El tambor: el angulo entre dos iconos y su radio (en pixeles del medallon). */
    private static final float PASO = 50.0F * Mth.DEG_TO_RAD;
    private static final float RADIO = 61.5F;

    /** Los colores de los finales (los del chat): mob, dificultad, penalizacion y minijuego. */
    private static final int[] COLOR = {0xFFFF9A3C, 0xFFFFD23A, 0xFF7FD8FF, 0xFF6EE36E};
    private static final int CALIDO = 0xFFFFE6A8;
    private static final int CREMA = 0xFFF7ECD6;

    /** Para las fotos de prueba (FotosPrueba, RULETA_FILM): el tiempo fijo con el que se pinto el ultimo fotograma. */
    public static float pintadoCon = -1;

    private static Identifier textura(String nombre) {
        return Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "textures/gui/ruleta/" + nombre + ".png");
    }

    private static Identifier suave(String nombre) {
        return Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "textures/gui/momento/" + nombre + ".png");
    }

    @Override
    public void extractRenderState(GuiGraphicsExtractor g, DeltaTracker delta) {
        if (!RuletaCliente.activa()) {
            return;
        }
        pintadoCon = RuletaCliente.pruebaT;
        Minecraft mc = Minecraft.getInstance();
        float tt = RuletaCliente.tiempo(delta.getGameTimeDeltaPartialTick(false));
        int gs = Math.max(1, mc.getWindow().getGuiScale());
        int SW = g.guiWidth() * gs;
        int SH = g.guiHeight() * gs;
        int f = Math.max(1, Math.round(SH / 330.0F));
        int fin = RuletaCliente.fin();
        int color = COLOR[fin];
        float p = RuletaCliente.posicion(tt);
        float v = Math.abs(RuletaCliente.velocidad(tt));
        float d = tt - RuletaCliente.T_PARA;
        float tension = RuletaCliente.tension(tt);
        float latido = RuletaCliente.latido(tt) * tension;
        // Lo despacio que va (0 a tope, 1 casi parado) y el icono que pasa por la linea de premio.
        float lento = 1.0F - Mth.clamp((v - 0.15F) / 0.5F, 0.0F, 1.0F);
        int bajo = RuletaCliente.icono(Math.round(p));
        int ambiente = d >= 0 ? color : mezcla(CALIDO, COLOR[bajo], lento);
        float mx = Math.round(SW / 2.0F);
        float my = Math.round(SH / 2.0F);
        float env = tt < 6 ? suave(tt / 6.0F)
                : tt < RuletaCliente.T_SALE ? 1.0F : 1.0F - suave((tt - RuletaCliente.T_SALE) / 12.0F);

        g.pose().pushMatrix();
        g.pose().scale(1.0F / gs, 1.0F / gs);
        // El mundo se apaga y la vineta se cierra (mas en el suspense, y late con el corazon).
        g.fill(0, 0, SW, SH, conAlfa(0xFF000000, (0.3F + 0.2F * tension) * env));
        pieza(g, VINETA, 256, 144, mx, my, SW, SH, 0.0F, conAlfa(0xFF000000, (0.72F + 0.25F * tension + 0.15F * latido) * env));
        if (d >= 0 && d < 5) {
            g.fill(0, 0, SW, SH, conAlfa(color, 0.26F * (1.0F - d / 5.0F)));
        }
        // Detras del medallon: la luz del icono que pasa, los rayos y las chispas que se traga.
        float rf = R_ARO * f;
        float k = d >= 0 ? (d < 3 ? d / 3.0F : Math.max(0.0F, 1.0F - (d - 3) / 26.0F)) : 0.0F;
        pieza(g, BRILLO, 128, 128, mx, my, rf * 3.8F, rf * 3.8F, 0.0F,
                conAlfa(ambiente, (0.32F + 0.18F * lento + 0.3F * k + 0.1F * latido) * env));
        if (tt < RuletaCliente.T_PARA) {
            float giro = p * 0.045F;
            for (int i = 0; i < 12; i++) {
                float a = giro + i * Mth.TWO_PI / 12;
                float largo = rf * 2.8F;
                pieza(g, HAZ, 128, 32, mx + Mth.cos(a) * largo / 2, my + Mth.sin(a) * largo / 2, largo, rf * 0.3F, a,
                        conAlfa(i % 2 == 0 ? CALIDO : ambiente, 0.1F * env * (1.0F - 0.5F * tension)));
            }
            chispas(g, tt, mx, my, rf, f, ambiente, env * (1.0F - 0.6F * tension));
        } else if (k > 0) {
            for (int i = 0; i < 12; i++) {
                float a = i * Mth.TWO_PI / 12 + tt * 0.02F;
                float largo = rf * 3.6F;
                pieza(g, HAZ, 128, 32, mx + Mth.cos(a) * largo / 2, my + Mth.sin(a) * largo / 2, largo,
                        rf * (i % 2 == 0 ? 0.62F : 0.38F), a, conAlfa(i % 2 == 0 ? color : 0xFFFFFFFF, (i % 2 == 0 ? 0.5F : 0.26F) * k));
            }
            // La onda del cerrojo.
            if (d < 8) {
                float o = rf * (2.0F + 3.0F * d / 8.0F);
                pieza(g, BRILLO, 128, 128, mx, my, o, o, 0.0F, conAlfa(0xFFFFFFFF, 0.45F * (1.0F - d / 8.0F)));
            }
        }

        // El medallon: entra girando, se acerca en el suspense, el cerrojo lo sacude y se va girando.
        float s = 1.0F + 0.065F * tension + 0.018F * latido;
        float rot = 0.0F;
        float dx = 0.0F;
        float dy = 0.0F;
        if (tt < RuletaCliente.T_ENTRA) {
            float e = tt / RuletaCliente.T_ENTRA;
            s *= atras(e);
            rot = -0.9F * (1.0F - e) * (1.0F - e);
        }
        if (d >= 0 && d < 12) {
            float sacude = (float) Math.exp(-d / 2.0F);
            s *= 1.0F + 0.05F * sacude;
            dx = 2.4F * f * Mth.sin(d * 2.9F) * sacude;
            dy = 1.4F * f * Mth.sin(d * 3.7F + 1.0F) * sacude;
        }
        float sale = tt - RuletaCliente.T_SALE;
        if (sale >= 0) {
            float e = sale / 10.0F;
            s *= e < 0.2F ? 1.0F + 0.06F * Mth.sin(e / 0.2F * Mth.HALF_PI)
                    : 1.06F * (1.0F - (float) Math.pow(Mth.clamp((e - 0.2F) / 0.8F, 0.0F, 1.0F), 2.2));
            rot = 0.7F * e * e;
        }
        if (s > 0.01F) {
            g.pose().pushMatrix();
            g.pose().translate(mx + dx, my + dy);
            if (rot != 0.0F) {
                g.pose().rotate(rot);
            }
            g.pose().scale(s * f, s * f);
            g.pose().translate(-CX, -CY);
            medallon(g, tt, p, v, fin, color, bajo, lento, latido, tension, env);
            g.pose().popMatrix();
        }

        // Lo que sale al parar (sin girar ni aplastarse con el medallon).
        if (d >= 0) {
            g.pose().pushMatrix();
            g.pose().translate(mx, my);
            g.pose().scale(f, f);
            monedas(g, d);
            destellos(g, d, color);
            g.pose().popMatrix();
            iconoFinal(g, tt, fin, color, f, mx + dx, my + dy, SW, SH, gs, g.guiHeight());
        }
        g.pose().popMatrix();
    }

    // ------------------------------------------------------------------
    //  El medallon
    // ------------------------------------------------------------------

    private static void medallon(GuiGraphicsExtractor g, float tt, float p, float v, int fin, int color, int bajo,
                                 float lento, float latido, float tension, float env) {
        // La sombra que lo despega del mundo.
        pieza(g, BRILLO, 128, 128, CX, CY, R_ARO * 2.5F, R_ARO * 2.5F, 0.0F, conAlfa(0xFF000000, 0.6F * env));
        rodillo(g, tt, p, v, color);
        g.blit(RenderPipelines.GUI_TEXTURED, MAQUINA, 0, 0, 0, 0, MED_W, MED_H, MED_W, MED_H, HOJA, HOJA, 0xFFFFFFFF);
        // Las luces en dos tandas (el juego junta lo seguido de la misma textura): primero todos los brillos y despues
        // todos los nucleos y las flechas. Con la grafica del procesador, ir alternando bajaba de 60 a 30 FPS.
        luces(tt, p, fin, color, bajo, lento, latido, tension);
        for (int i = 0; i < LUCES; i++) {
            if (luzBrillo[i] > 0) {
                pieza(g, BRILLO, 128, 128, luzX[i], luzY[i], luzTam[i], luzTam[i], 0.0F, conAlfa(luzColor[i], luzBrillo[i]));
            }
        }
        farol(g, tt, color, latido);
        flechas(g, tt, color, latido, true);
        for (int i = 0; i < LUCES; i++) {
            if (luzNucleo[i] > 0) {
                g.blit(RenderPipelines.GUI_TEXTURED, MAQUINA, Math.round(luzX[i] - 3.5F), Math.round(luzY[i] - 3.5F), 176, 0,
                        7, 7, 7, 7, HOJA, HOJA, conAlfa(luzNucleoColor[i], luzNucleo[i]));
            }
        }
        flechas(g, tt, color, latido, false);
    }

    // Las luces del medallon (las 22 bombillas y las 4 gemas), calculadas una vez por fotograma.
    private static final int LUCES = 26;
    private static final float[] luzX = new float[LUCES];
    private static final float[] luzY = new float[LUCES];
    private static final float[] luzTam = new float[LUCES];
    private static final float[] luzBrillo = new float[LUCES];
    private static final int[] luzColor = new int[LUCES];
    private static final float[] luzNucleo = new float[LUCES];
    private static final int[] luzNucleoColor = new int[LUCES];

    private static void luces(float tt, float p, int fin, int color, int bajo, float lento, float latido, float tension) {
        for (int i = 0; i < BOMBILLAS.length; i++) {
            float b = bombilla(i, tt, p, latido, tension);
            int c = bombillaColor(i, tt, p, color, tension);
            luzX[i] = BOMBILLAS[i][0] + 0.5F;
            luzY[i] = BOMBILLAS[i][1] + 0.5F;
            luzTam[i] = 18;
            luzBrillo[i] = b <= 0.02F ? 0 : 0.5F * Math.min(1.0F, b);
            luzColor[i] = c;
            luzNucleo[i] = b <= 0.02F ? 0 : Math.min(1.0F, b);
            luzNucleoColor[i] = mezcla(c, 0xFFFFFFFF, Mth.clamp(b - 1.0F, 0.0F, 1.0F));
        }
        float d = tt - RuletaCliente.T_PARA;
        for (int i = 0; i < 4; i++) {
            float b;
            if (d >= 0) {
                b = i == fin ? 1.3F + 0.3F * Mth.sin(d * 0.8F) : 0.0F;
            } else if (lento < 0.3F) {
                b = 0.25F + 0.35F * Math.abs(Mth.sin(tt * 1.7F + i * 1.9F));
            } else {
                b = i == bajo ? 0.4F + 0.7F * lento : 0.1F;
            }
            int k = BOMBILLAS.length + i;
            luzX[k] = GEMAS[i][0] + 0.5F;
            luzY[k] = GEMAS[i][1] + 0.5F;
            luzTam[k] = 20;
            luzBrillo[k] = b <= 0.02F ? 0 : 0.6F * Math.min(1.0F, b);
            luzColor[k] = COLOR[i];
            luzNucleo[k] = b <= 0.02F ? 0 : 0.85F * Math.min(1.0F, b);
            luzNucleoColor[k] = mezcla(COLOR[i], 0xFFFFFFFF, Mth.clamp(b - 1.0F, 0.0F, 1.0F));
        }
    }

    /**
     * El rodillo, detras del hueco redondo (el medallon tapa lo que se sale): el tambor crema, los iconos en su giro y,
     * por encima, la sombra de la lente y el reflejo del cristal.
     */
    private static void rodillo(GuiGraphicsExtractor g, float tt, float p, float v, int color) {
        int x0 = Mth.floor(CX - R_VENTANA) - 1;
        int x1 = Mth.ceil(CX + R_VENTANA) + 1;
        int y0 = Mth.floor(CY - R_VENTANA) - 1;
        int y1 = Mth.ceil(CY + R_VENTANA) + 1;
        for (int y = y0; y < y1; y += 8) {
            int y2 = Math.min(y1, y + 8);
            g.fillGradient(x0, y, x1, y2, mezcla(0xFF000000, CREMA, luzTambor(y)), mezcla(0xFF000000, CREMA, luzTambor(y2)));
        }
        float d = tt - RuletaCliente.T_PARA;
        if (d >= 0) {
            float k = d < 2 ? d / 2.0F : 0.75F + 0.25F * Mth.sin(d * 0.5F);
            pieza(g, BRILLO, 128, 128, CX, CY, 110, 84, 0.0F, conAlfa(color, 0.8F * k));
        }
        float rapido = Mth.clamp((v - 0.12F) / 0.45F, 0.0F, 1.0F);
        int base = Mth.floor(p);
        // Las rayas entre icono e icono (deprisa, casi no se ven).
        for (int i = base - 2; i <= base + 3; i++) {
            float th = (p - i - 0.5F) * PASO;
            if (Math.abs(th) < Mth.HALF_PI * 0.95F) {
                float y = CY + RADIO * Mth.sin(th);
                franja(g, x0, x1, y - 0.5F, 1.0F, conAlfa(0xFF6A5236, 0.5F * Mth.cos(th) * (1.0F - 0.85F * rapido)));
            }
        }
        // Los iconos, aplastados segun su giro; deprisa, corridos.
        for (int i = base - 2; i <= base + 3; i++) {
            float th = (p - i) * PASO;
            if (Math.abs(th) >= Mth.HALF_PI * 0.97F) {
                continue;
            }
            float cy = CY + RADIO * Mth.sin(th);
            float cs = Mth.cos(th);
            int tinte = mezcla(0xFF000000, 0xFFFFFFFF, 0.22F + 0.78F * (float) Math.pow(cs, 1.4));
            int u = RuletaCliente.icono(i) * ICONO;
            g.pose().pushMatrix();
            g.pose().translate(CX, cy);
            if (rapido > 0) {
                g.pose().pushMatrix();
                g.pose().scale(1.0F, cs * (1.0F + 0.15F * rapido));
                g.blit(RenderPipelines.GUI_TEXTURED, BORROSOS, -ICONO / 2, -ICONO / 2, u, 0, ICONO, ICONO, ICONO, ICONO,
                        ICONO * 4, ICONO, conAlfa(tinte, rapido));
                g.pose().popMatrix();
            }
            if (rapido < 1) {
                g.pose().scale(1.0F, cs);
                g.blit(RenderPipelines.GUI_TEXTURED, ICONOS, -ICONO / 2, -ICONO / 2, u, 0, ICONO, ICONO, ICONO, ICONO,
                        ICONO * 4, ICONO, conAlfa(tinte, 1.0F - rapido));
            }
            g.pose().popMatrix();
        }
        // La lente: el borde de la ventana en sombra, y el reflejo del cristal arriba a la izquierda.
        pieza(g, VINETA, 256, 144, CX, CY, R_VENTANA * 2.3F, R_VENTANA * 2.3F, 0.0F, 0xF0000000);
        pieza(g, BRILLO, 128, 128, CX - 20, CY - 33, 64, 9, -0.55F, conAlfa(0xFFFFFFFF, 0.2F));
        pieza(g, BRILLO, 128, 128, CX - 33, CY - 22, 10, 10, 0.0F, conAlfa(0xFFFFFFFF, 0.28F));
    }

    /** Lo iluminado del tambor a la altura y (pixeles del medallon). */
    private static float luzTambor(float y) {
        float s = Mth.clamp((y - CY) / RADIO, -1.0F, 1.0F);
        float c = (float) Math.sqrt(1.0F - s * s);
        return 0.25F + 0.75F * (float) Math.pow(c, 1.5);
    }

    /**
     * Lo que luce una bombilla: al entrar se encienden de una pasada; mientras gira, dos cometas de luz corren por el
     * aro con el rodillo (frenan con el); en el suspense se apagan y solo laten con el corazon; al parar, parpadean.
     */
    private static float bombilla(int i, float tt, float p, float latido, float tension) {
        float d = tt - RuletaCliente.T_PARA;
        int n = BOMBILLAS.length;
        if (d < 0) {
            float b = 0.18F + 1.1F * (float) Math.exp(-cometa(i, p) / 2.2F);
            b = b * (1.0F - 0.85F * tension) + tension * (0.12F + 0.95F * latido);
            if (tt < RuletaCliente.T_ENTRA) {
                b *= Mth.clamp((tt * n / RuletaCliente.T_ENTRA - i) / 2.0F, 0.0F, 1.0F);
            }
            return b;
        }
        if (tt < RuletaCliente.T_SALE) {
            if (d < 1.5F) {
                return 1.8F;
            }
            if (d < 14) {
                return Mth.floor(d / 2.0F) % 2 == 0 ? 1.3F : 0.2F;
            }
            return Math.floorMod(i + Mth.floor(d * 0.5F), 2) == 0 ? 1.15F : 0.4F;
        }
        return Math.max(0.0F, 1.0F - (tt - RuletaCliente.T_SALE) / 6.0F);
    }

    /** El color de una bombilla: la cabeza de la cometa, blanca; la cola, de los cuatro finales; al parar, el del final. */
    private static int bombillaColor(int i, float tt, float p, int color, float tension) {
        if (tt >= RuletaCliente.T_PARA) {
            return color;
        }
        int c = cometa(i, p) < 0.8F ? 0xFFFFFFFF : COLOR[Math.floorMod(i, 4)];
        return tension > 0.5F ? mezcla(c, 0xFFFFFFFF, tension) : c;
    }

    /** Lo que le falta a la bombilla i para que llegue la cabeza de una de las dos cometas (que van con el rodillo). */
    private static float cometa(int i, float p) {
        int n = BOMBILLAS.length;
        float mejor = 99;
        for (int k = 0; k < 2; k++) {
            float dist = p * 0.55F + k * n / 2.0F - i;
            dist -= Mth.floor(dist / n) * n;
            mejor = Math.min(mejor, dist);
        }
        return mejor;
    }

    /** El farol de la atalaya de la cresta: late con el corazon y, al parar, arde del color del final. */
    private static void farol(GuiGraphicsExtractor g, float tt, int color, float latido) {
        float d = tt - RuletaCliente.T_PARA;
        float k = d >= 0 ? 0.9F + 0.1F * Mth.sin(d * 1.7F) : 0.35F + 0.15F * Mth.sin(tt * 0.9F) + 0.5F * latido;
        int c = d >= 0 ? color : CALIDO;
        pieza(g, BRILLO, 128, 128, FAROL_X, FAROL_Y, d >= 0 ? 34 : 22, d >= 0 ? 26 : 16, 0.0F, conAlfa(c, 0.85F * k));
    }

    /**
     * Las flechas de la linea de premio: en el suspense se acercan con cada latido; al parar, se encienden. Con brillo,
     * solo su brillo; sin el, solo las flechas.
     */
    private static void flechas(GuiGraphicsExtractor g, float tt, int color, float latido, boolean brillo) {
        float d = tt - RuletaCliente.T_PARA;
        float va = d < 0 ? Math.round(1.6F * latido) : 0;
        int tinte = d >= 0 ? mezcla(0xFFFFFFFF, color, 0.35F + 0.25F * Mth.sin(d * 0.9F)) : 0xFFFFFFFF;
        if (brillo) {
            if (d < 0 && latido <= 0.05F) {
                return;
            }
            float k = d >= 0 ? (d < 2 ? 1.0F : 0.55F + 0.2F * Mth.sin(d * 0.9F)) : 0.6F * latido;
            int c = d >= 0 ? color : 0xFFFFFFFF;
            pieza(g, BRILLO, 128, 128, CX - R_CROMO + 2, CY, 26, 26, 0.0F, conAlfa(c, 0.7F * k));
            pieza(g, BRILLO, 128, 128, CX + R_CROMO - 2, CY, 26, 26, 0.0F, conAlfa(c, 0.7F * k));
            return;
        }
        g.pose().pushMatrix();
        g.pose().translate(CX - R_CROMO - 4 + va, CY - 7);
        g.blit(RenderPipelines.GUI_TEXTURED, MAQUINA, 0, 0, 194, 0, 12, 14, 12, 14, HOJA, HOJA, tinte);
        g.pose().popMatrix();
        g.pose().pushMatrix();
        g.pose().translate(CX + R_CROMO + 4 - va, CY - 7);
        g.pose().scale(-1.0F, 1.0F);
        g.blit(RenderPipelines.GUI_TEXTURED, MAQUINA, 0, 0, 194, 0, 12, 14, 12, 14, HOJA, HOJA, tinte);
        g.pose().popMatrix();
    }

    // ------------------------------------------------------------------
    //  Lo de alrededor
    // ------------------------------------------------------------------

    /** Las chispas que el medallon se traga en espiral mientras gira (en pixeles de pantalla, alrededor del centro). */
    private static void chispas(GuiGraphicsExtractor g, float tt, float mx, float my, float rf, int f, int color, float alfa) {
        if (alfa <= 0.02F) {
            return;
        }
        for (int pasada = 0; pasada < 2; pasada++) for (int i = 0; i < 18; i++) {
            float fase = (tt * (0.028F + 0.012F * hash(i, 9)) + hash(i, 1)) % 1.0F;
            float r = rf * (2.1F - 1.0F * fase);
            float a = hash(i, 2) * Mth.TWO_PI + fase * 2.4F;
            float x = mx + Mth.cos(a) * r;
            float y = my + Mth.sin(a) * r;
            float k = Mth.sin(fase * Mth.PI) * alfa;
            float t = (1.0F + 1.2F * hash(i, 3)) * f;
            int c = i % 3 == 0 ? 0xFFFFFFFF : color;
            if (pasada == 0) {
                pieza(g, BRILLO, 128, 128, x, y, 9 * t, 9 * t, 0.0F, conAlfa(c, 0.35F * k));
                continue;
            }
            g.pose().pushMatrix();
            g.pose().translate(x, y);
            g.pose().rotate(tt * 0.1F + i);
            g.pose().scale(t * 0.7F, t * 0.7F);
            g.blit(RenderPipelines.GUI_TEXTURED, MAQUINA, -4, -4, 184, 0, 9, 9, 9, 9, HOJA, HOJA, conAlfa(mezcla(c, 0xFFFFFFFF, 0.5F), k));
            g.pose().popMatrix();
        }
    }

    /** Las monedas que salen disparadas de la ventana al parar, girando, y caen. */
    private static void monedas(GuiGraphicsExtractor g, float d) {
        for (int i = 0; i < 12; i++) {
            float a = d - 0.5F - i * 0.4F;
            if (a < 0 || a > 30) {
                continue;
            }
            float ang = -Mth.HALF_PI + (hash(i, 1) - 0.5F) * 2.6F;
            float vel = 4.0F + 3.0F * hash(i, 2);
            float x = Mth.cos(ang) * vel * a;
            float y = Mth.sin(ang) * vel * a + 0.5F * 0.6F * a * a;
            float giro = Math.abs(Mth.cos(a * (0.45F + 0.3F * hash(i, 3)) + hash(i, 4) * 6.0F));
            g.pose().pushMatrix();
            g.pose().translate(x, y);
            g.pose().scale(Math.max(0.15F, giro) * 1.3F, 1.3F);
            g.blit(RenderPipelines.GUI_TEXTURED, MAQUINA, -6, -6, 208, 0, 12, 12, 12, 12, HOJA, HOJA, 0xFFFFFFFF);
            g.pose().popMatrix();
        }
    }

    /** Los destellos que salen de la ventana al parar, frenando, y se apagan. */
    private static void destellos(GuiGraphicsExtractor g, float d, int color) {
        for (int pasada = 0; pasada < 2; pasada++) for (int i = 0; i < 22; i++) {
            float a = d - i * 0.12F;
            if (a < 0 || a > 16) {
                continue;
            }
            float ang = hash(i, 5) * Mth.TWO_PI;
            float r = (40 + 50 * hash(i, 6)) * (1.0F - (float) Math.exp(-a / 4.0F));
            float x = Mth.cos(ang) * r;
            float y = Mth.sin(ang) * r;
            float k = 1.0F - a / 16.0F;
            float s = (0.8F + 0.9F * hash(i, 7)) * (0.4F + 0.6F * k);
            int c = i % 3 == 0 ? 0xFFFFFFFF : color;
            if (pasada == 0) {
                pieza(g, BRILLO, 128, 128, x, y, 14 * s, 14 * s, 0.0F, conAlfa(c, 0.45F * k));
                continue;
            }
            g.pose().pushMatrix();
            g.pose().translate(x, y);
            g.pose().rotate(a * 0.15F);
            g.pose().scale(s, s);
            g.blit(RenderPipelines.GUI_TEXTURED, MAQUINA, -4, -4, 184, 0, 9, 9, 9, 9, HOJA, HOJA,
                    conAlfa(mezcla(c, 0xFFFFFFFF, 0.5F), k));
            g.pose().popMatrix();
        }
    }

    /**
     * El icono del final: al parar salta con su brillo (y se queda a una escala entera, para que se vea nitido); al
     * irse el medallon, vuela hacia el chat, donde sale el aviso, encogiendo y dejando estela.
     */
    private static void iconoFinal(GuiGraphicsExtractor g, float tt, int fin, int color, int f, float cx, float cy,
                                   int SW, int SH, int gs, int guiAlto) {
        float d = tt - RuletaCliente.T_PARA;
        float tope = Math.max(1, Math.round(1.3F * f)) / (float) f;
        float s = d < 3 ? 1.0F + (tope + 0.3F - 1.0F) * suave(d / 3.0F)
                : tope + 0.3F * (float) Math.exp(-(d - 3) / 1.8F) * Mth.cos((d - 3) * 1.6F);
        float sale = tt - RuletaCliente.T_SALE;
        if (sale < 0) {
            if (d < 4) {
                pieza(g, BRILLO, 128, 128, cx, cy, 130 * f * (0.5F + d / 4.0F), 130 * f * (0.5F + d / 4.0F), 0.0F,
                        conAlfa(0xFFFFFFFF, 0.85F * (1.0F - d / 4.0F)));
            }
            pieza(g, BRILLO, 128, 128, cx, cy, 84 * f * s, 84 * f * s, 0.0F, conAlfa(color, 0.6F));
            icono(g, fin, cx, cy, s * f, 1.0F);
            return;
        }
        // El vuelo al chat: del centro a la primera letra del aviso (arriba del todo de sus dos lineas).
        float e = suave(Mth.clamp(sale / 8.0F, 0.0F, 1.0F));
        float tx = 8.0F * gs;
        float ty = (guiAlto - 54.0F) * gs;
        float s1 = 8.0F * gs / ICONO;
        for (int k = 3; k >= 0; k--) {
            float ek = Math.max(0.0F, e - k * 0.06F);
            float qx = cx + (tx - cx) * ek - (1 - ek) * ek * SW * 0.12F;
            float qy = cy + (ty - cy) * ek - (1 - ek) * ek * SH * 0.35F;
            float sk = tope * f + (s1 - tope * f) * ek;
            float a = (k == 0 ? 1.0F : 0.35F / k) * (1.0F - Mth.clamp((e - 0.85F) / 0.15F, 0.0F, 1.0F));
            if (k == 0) {
                pieza(g, BRILLO, 128, 128, qx, qy, 70 * sk, 70 * sk, 0.0F, conAlfa(color, 0.5F * a));
            }
            icono(g, fin, qx, qy, sk, a);
        }
        if (sale > 7 && sale < 13) {
            float k = (sale - 7) / 6.0F;
            pieza(g, BRILLO, 128, 128, tx, ty, 40 * gs * (0.4F + k), 40 * gs * (0.4F + k), 0.0F, conAlfa(color, 0.6F * (1 - k)));
        }
    }

    /** Un icono del rodillo, con el centro en (x, y) y a s pixeles de pantalla por pixel de su dibujo. */
    private static void icono(GuiGraphicsExtractor g, int fin, float x, float y, float s, float alfa) {
        if (alfa <= 0.01F) {
            return;
        }
        g.pose().pushMatrix();
        g.pose().translate(x, y);
        g.pose().scale(s, s);
        g.blit(RenderPipelines.GUI_TEXTURED, ICONOS, -ICONO / 2, -ICONO / 2, fin * ICONO, 0, ICONO, ICONO, ICONO, ICONO,
                ICONO * 4, ICONO, conAlfa(0xFFFFFFFF, alfa));
        g.pose().popMatrix();
    }

    // ------------------------------------------------------------------
    //  Utilidades
    // ------------------------------------------------------------------

    /** Sale de 0, se pasa un poco de 1 y vuelve (la entrada del medallon). */
    private static float atras(float e) {
        e = Mth.clamp(e, 0.0F, 1.0F);
        float c = 1.9F;
        float u = e - 1.0F;
        return 1.0F + (c + 1.0F) * u * u * u + c * u * u;
    }

    /** Una franja horizontal de x0 a x1 a la altura y (con decimales) y de un alto (con decimales). */
    private static void franja(GuiGraphicsExtractor g, int x0, int x1, float y, float alto, int color) {
        g.pose().pushMatrix();
        g.pose().translate(0.0F, y);
        g.pose().scale(1.0F, alto);
        g.fill(x0, 0, x1, 1, color);
        g.pose().popMatrix();
    }

    /** Una pieza suave de tw x th estirada a w x h, con el centro en (cx, cy), girada ang y teñida de color. */
    private static void pieza(GuiGraphicsExtractor g, Identifier id, int tw, int th, float cx, float cy, float w, float h,
                              float ang, int color) {
        if (((color >>> 24) & 255) == 0 || w < 0.5F || h < 0.5F) {
            return;
        }
        g.pose().pushMatrix();
        g.pose().translate(cx, cy);
        if (ang != 0.0F) {
            g.pose().rotate(ang);
        }
        g.pose().scale(w / tw, h / th);
        g.blit(RenderPipelines.GUI_TEXTURED, id, -tw / 2, -th / 2, 0, 0, tw, th, tw, th, tw, th, color);
        g.pose().popMatrix();
    }

    private static float hash(int a, int b) {
        long h = (a * 73856093L) ^ (b * 19349663L) ^ 0x5DEECE66DL;
        h ^= (h >>> 13);
        h *= 0x5bd1e995L;
        h ^= (h >>> 15);
        return (h & 0xFFFF) / 65535.0F;
    }

    private static int conAlfa(int argb, float k) {
        int a = Math.round(((argb >>> 24) & 255) * Mth.clamp(k, 0.0F, 1.0F));
        return (a << 24) | (argb & 0xFFFFFF);
    }

    private static int mezcla(int a, int b, float k) {
        k = Mth.clamp(k, 0.0F, 1.0F);
        int r = (int) Mth.lerp(k, (a >> 16) & 255, (b >> 16) & 255);
        int gg = (int) Mth.lerp(k, (a >> 8) & 255, (b >> 8) & 255);
        int bl = (int) Mth.lerp(k, a & 255, b & 255);
        int al = (int) Mth.lerp(k, (a >>> 24) & 255, (b >>> 24) & 255);
        return (al << 24) | (r << 16) | (gg << 8) | bl;
    }

    private static float suave(float x) {
        x = Mth.clamp(x, 0.0F, 1.0F);
        return x * x * (3 - 2 * x);
    }
}
