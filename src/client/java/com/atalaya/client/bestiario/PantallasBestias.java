package com.atalaya.client.bestiario;

import com.atalaya.Atalaya;
import com.atalaya.bestiario.Atrapado;
import com.atalaya.bestiario.BestiaRed;
import com.atalaya.bestiario.Fichas;
import com.atalaya.effect.CongeladoEffect;
import net.fabricmc.fabric.api.client.event.lifecycle.v1.ClientTickEvents;
import net.fabricmc.fabric.api.client.networking.v1.ClientPlayConnectionEvents;
import net.fabricmc.fabric.api.client.networking.v1.ClientPlayNetworking;
import net.fabricmc.fabric.api.client.rendering.v1.hud.HudElementRegistry;
import net.fabricmc.fabric.api.client.rendering.v1.hud.VanillaHudElements;
import net.minecraft.client.DeltaTracker;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphicsExtractor;
import net.minecraft.client.player.LocalPlayer;
import net.minecraft.client.renderer.RenderPipelines;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.Identifier;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.util.Mth;
import net.minecraft.util.RandomSource;
import net.minecraft.world.effect.MobEffectInstance;

import java.util.ArrayList;
import java.util.List;

/**
 * Lo que los mobs del bestiario te ponen en la pantalla (las texturas, de bestiario_pantallas.py):
 *
 * <pre>
 *   la estatica    SIN SENAL (el Creeper Gelatina): la pantalla entera de grano que se mueve cada fotograma, con su
 *                  rotulo en medio que parpadea; por encima de todo el HUD (no ves nada)
 *   la nata        los pegotes del Creeper Tarta: caen sobre la pantalla, chorrean despacio y se van borrando; por
 *                  debajo de la barra y los corazones (para que veas como estas)
 *   las lianas     mientras el Creeper Enredadera te tiene: la barra de lo que te falta para soltarte (crece con cada
 *                  salto) y la tecla que aporrear
 *   la alucinacion la Hormiga Polvorin: franjas de colores que se mueven y respiran por encima de todo (por debajo del
 *                  HUD), cada vez mas flojas
 *   la escarcha    mientras estas Congelado (la Fauces de Escarcha): los cristales que te cubren los bordes de la vista
 *                  y un velo celeste; entra en un momento y se derrite en el ultimo segundo
 * </pre>
 */
public final class PantallasBestias {

    private static final Identifier ESTATICA = Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "textures/gui/bestiario/estatica.png");
    private static final Identifier SIN_SENAL = Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "textures/gui/bestiario/sin_senal.png");
    private static final Identifier NATA = Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "textures/gui/bestiario/nata.png");
    private static final Identifier LIANAS = Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "textures/gui/bestiario/lianas.png");
    private static final Identifier ESPACIO = Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "textures/gui/tecla_espacio.png");
    private static final Identifier TECLA = Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "textures/gui/bestiario/tecla.png");
    private static final Identifier ESCARCHA = Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "textures/gui/bestiario/escarcha.png");
    private static final int ROTULO_ANCHO = 238;
    private static final int ROTULO_ALTO = 44;

    private static final RandomSource AZAR = RandomSource.create();
    private static int senal;
    private static int senalTotal;
    private static int nata;
    private static int nataTotal;
    private static int alucina;
    private static int alucinaTotal;
    /** Los ticks que lleva congelado (para que la escarcha entre poco a poco). */
    private static int helado;
    /** Los pegotes: x e y (en fraccion de la pantalla), tamano (fraccion del alto), cual (0-3) y lo que chorrea. */
    private static final List<float[]> PEGOTES = new ArrayList<>();
    /** Si la tecla de las lianas estaba abajo el tick anterior (se cuentan los flancos: hay que aporrearla). */
    private static boolean teclaAbajo;

    private PantallasBestias() {
    }

    public static void registrar() {
        ClientPlayNetworking.registerGlobalReceiver(BestiaRed.Pantalla.TIPO, (carga, contexto) -> recibir(carga));
        ClientTickEvents.END_CLIENT_TICK.register(PantallasBestias::tick);
        ClientPlayConnectionEvents.DISCONNECT.register((manejador, cliente) -> olvidar());
        HudElementRegistry.attachElementBefore(VanillaHudElements.HOTBAR,
                Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "bestias_nata"), PantallasBestias::pintarNata);
        HudElementRegistry.attachElementBefore(VanillaHudElements.HOTBAR,
                Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "bestias_alucinacion"), PantallasBestias::pintarAlucinacion);
        HudElementRegistry.attachElementBefore(VanillaHudElements.HOTBAR,
                Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "bestias_escarcha"), PantallasBestias::pintarEscarcha);
        HudElementRegistry.attachElementAfter(VanillaHudElements.HOTBAR,
                Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "bestias_lianas"), PantallasBestias::pintarLianas);
        HudElementRegistry.addLast(Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "bestias_sin_senal"),
                PantallasBestias::pintarSinSenal);
    }

    private static void recibir(BestiaRed.Pantalla p) {
        Minecraft mc = Minecraft.getInstance();
        if (p.cual() == BestiaRed.SIN_SENAL) {
            senal = Math.max(senal, p.ticks());
            senalTotal = Math.max(senal, senalTotal);
            sonar(mc, Fichas.GELATINA.sonido("estatica"), 0.8F);
        } else if (p.cual() == BestiaRed.ALUCINACION) {
            alucina = Math.max(alucina, p.ticks());
            alucinaTotal = Math.max(alucina, alucinaTotal);
        } else if (p.cual() == BestiaRed.NATA) {
            nata = Math.max(nata, p.ticks());
            nataTotal = Math.max(nata, nataTotal);
            int cuantos = 5 + AZAR.nextInt(3);
            for (int i = 0; i < cuantos; i++) {
                PEGOTES.add(new float[]{0.08F + AZAR.nextFloat() * 0.84F, 0.05F + AZAR.nextFloat() * 0.7F,
                        0.32F + AZAR.nextFloat() * 0.28F, AZAR.nextInt(4), 0.0F});
            }
            sonar(mc, Fichas.TARTA.sonido("pringue"), 1.0F);
        }
    }

    private static void sonar(Minecraft mc, SoundEvent s, float volumen) {
        if (s != null && mc.player != null) {
            mc.player.playSound(s, volumen, 1.0F);
        }
    }

    /** La tecla que piden las lianas. */
    private static net.minecraft.client.KeyMapping teclaDe(Minecraft mc, int t) {
        return switch (t) {
            case Atrapado.ADELANTE -> mc.options.keyUp;
            case Atrapado.ATRAS -> mc.options.keyDown;
            case Atrapado.IZQUIERDA -> mc.options.keyLeft;
            case Atrapado.DERECHA -> mc.options.keyRight;
            default -> mc.options.keyJump;
        };
    }

    private static void tick(Minecraft mc) {
        // Las lianas: cada vez que se baja la tecla que toca, una pulsacion menos (lo cuenta el servidor).
        if (mc.player != null && Atrapado.atrapado(mc.player)) {
            boolean abajo = teclaDe(mc, Atrapado.tecla(mc.player)).isDown();
            if (abajo && !teclaAbajo && ClientPlayNetworking.canSend(BestiaRed.Forcejeo.TIPO)) {
                ClientPlayNetworking.send(new BestiaRed.Forcejeo());
            }
            teclaAbajo = abajo;
        } else {
            teclaAbajo = false;
        }
        if (senal > 0 && --senal == 0) {
            senalTotal = 0;
        }
        helado = mc.player != null && mc.player.hasEffect(CongeladoEffect.CONGELADO) ? helado + 1 : 0;
        if (alucina > 0 && --alucina == 0) {
            alucinaTotal = 0;
        }
        if (nata > 0) {
            for (float[] g : PEGOTES) {
                g[4] += 0.0006F;
            }
            if (--nata == 0) {
                nataTotal = 0;
                PEGOTES.clear();
            }
        }
    }

    private static void olvidar() {
        senal = senalTotal = nata = nataTotal = alucina = alucinaTotal = helado = 0;
        PEGOTES.clear();
    }

    private static int blanco(float alfa) {
        return ((int) (Mth.clamp(alfa, 0.0F, 1.0F) * 255.0F) << 24) | 0xFFFFFF;
    }

    // ------------------------------------------------------------------
    //  SIN SENAL
    // ------------------------------------------------------------------

    private static void pintarSinSenal(GuiGraphicsExtractor g, DeltaTracker delta) {
        if (senal <= 0) {
            return;
        }
        int w = g.guiWidth();
        int h = g.guiHeight();
        float pasado = senalTotal - senal;
        float alfa = Math.min(1.0F, pasado / 3.0F) * Math.min(1.0F, senal / 20.0F);
        int u = AZAR.nextInt(256);
        int v = AZAR.nextInt(256);
        g.blit(RenderPipelines.GUI_TEXTURED, ESTATICA, 0, 0, u, v, w, h, 256, 256, 512, 512, blanco(alfa));
        // El rotulo, en medio, a la mitad del ancho como mucho; parpadea como en una tele sin antena.
        if ((senal / 6) % 5 != 0) {
            float k = Math.min(1.0F, w * 0.5F / ROTULO_ANCHO);
            int rw = Math.round(ROTULO_ANCHO * k);
            int rh = Math.round(ROTULO_ALTO * k);
            g.blit(RenderPipelines.GUI_TEXTURED, SIN_SENAL, (w - rw) / 2, (h - rh) / 2, 0, 0, rw, rh,
                    ROTULO_ANCHO, ROTULO_ALTO, ROTULO_ANCHO, ROTULO_ALTO, blanco(alfa));
        }
    }

    // ------------------------------------------------------------------
    //  La nata
    // ------------------------------------------------------------------

    private static void pintarNata(GuiGraphicsExtractor g, DeltaTracker delta) {
        if (nata <= 0 || PEGOTES.isEmpty()) {
            return;
        }
        int w = g.guiWidth();
        int h = g.guiHeight();
        float alfa = Math.min(1.0F, nata / 40.0F);
        for (float[] p : PEGOTES) {
            int tam = Math.round(p[2] * h);
            int x = Math.round(p[0] * w - tam / 2.0F);
            int y = Math.round((p[1] + p[4]) * h - tam / 2.0F);
            g.blit(RenderPipelines.GUI_TEXTURED, NATA, x, y, (int) p[3] * 64, 0, tam, tam, 64, 64, 256, 64, blanco(alfa));
        }
    }

    // ------------------------------------------------------------------
    //  La escarcha
    // ------------------------------------------------------------------

    private static void pintarEscarcha(GuiGraphicsExtractor g, DeltaTracker delta) {
        LocalPlayer p = Minecraft.getInstance().player;
        MobEffectInstance e = p != null ? p.getEffect(CongeladoEffect.CONGELADO) : null;
        if (e == null || helado <= 0) {
            return;
        }
        int w = g.guiWidth();
        int h = g.guiHeight();
        float parcial = delta.getGameTimeDeltaPartialTick(false);
        float alfa = Math.min(1.0F, (helado + parcial) / 6.0F) * Math.min(1.0F, (e.getDuration() - parcial) / 20.0F);
        if (alfa <= 0.0F) {
            return;
        }
        g.fill(0, 0, w, h, ((int) (alfa * 46.0F) << 24) | 0x9EE6FF);
        g.blit(RenderPipelines.GUI_TEXTURED, ESCARCHA, 0, 0, 0.0F, 0.0F, w, h, 320, 180, 320, 180, blanco(alfa));
    }

    // ------------------------------------------------------------------
    //  La alucinacion
    // ------------------------------------------------------------------

    private static void pintarAlucinacion(GuiGraphicsExtractor g, DeltaTracker delta) {
        if (alucina <= 0) {
            return;
        }
        int w = g.guiWidth();
        int h = g.guiHeight();
        float t = (alucinaTotal - alucina) + delta.getGameTimeDeltaPartialTick(false);
        float fuerza = Math.min(1.0F, (alucinaTotal - alucina) / 10.0F) * Math.min(1.0F, alucina / 60.0F);
        int franjas = 18;
        for (int i = 0; i < franjas; i++) {
            float fase = i / (float) franjas;
            float tono = (fase + t * 0.015F) % 1.0F;
            int color = Mth.hsvToRgb(tono, 0.75F, 1.0F);
            float onda = 0.5F + 0.5F * Mth.sin(t * 0.18F + i * 0.9F);
            int a = (int) (fuerza * (40 + 50 * onda));
            int y0 = Math.round(h * fase + Mth.sin(t * 0.11F + i) * 6);
            int y1 = Math.round(h * (fase + 1.0F / franjas) + Mth.sin(t * 0.11F + i + 1) * 6);
            g.fill(0, y0, w, y1, (a << 24) | (color & 0xFFFFFF));
        }
        // Y unas columnas que cruzan, mas flojas, al reves.
        for (int i = 0; i < 10; i++) {
            float fase = i / 10.0F;
            float tono = (1.0F - fase + t * 0.02F) % 1.0F;
            int color = Mth.hsvToRgb(tono, 0.6F, 1.0F);
            int a = (int) (fuerza * (20 + 25 * (0.5F + 0.5F * Mth.sin(t * 0.13F + i * 1.3F))));
            int x0 = Math.round(w * fase + Mth.cos(t * 0.09F + i) * 10);
            g.fill(x0, 0, x0 + w / 20, h, (a << 24) | (color & 0xFFFFFF));
        }
    }

    // ------------------------------------------------------------------
    //  Las lianas
    // ------------------------------------------------------------------

    private static void pintarLianas(GuiGraphicsExtractor g, DeltaTracker delta) {
        Minecraft mc = Minecraft.getInstance();
        LocalPlayer j = mc.player;
        if (j == null || !Atrapado.atrapado(j)) {
            return;
        }
        int hechas = Atrapado.PULSACIONES - Atrapado.faltan(j);
        int cx = g.guiWidth() / 2;
        int y = g.guiHeight() - 96;
        int bx = cx - 63;
        int by = y - 20;
        g.blit(RenderPipelines.GUI_TEXTURED, LIANAS, bx, by, 0, 0, 126, 12, 128, 32);
        int relleno = Math.round(116.0F * hechas / Atrapado.PULSACIONES);
        if (relleno > 0) {
            g.blit(RenderPipelines.GUI_TEXTURED, LIANAS, bx + 4, by + 2, 4, 18, relleno, 8, 128, 32);
        }
        net.minecraft.client.KeyMapping tecla = teclaDe(mc, Atrapado.tecla(j));
        boolean pulsada = tecla.isDown();
        Component nombre = tecla.getTranslatedKeyMessage();
        if (Atrapado.tecla(j) == Atrapado.SALTAR) {
            g.blit(RenderPipelines.GUI_TEXTURED, ESPACIO, cx - 24, y, 0f, pulsada ? 16 : 0, 48, 16, 48, 32, 0xFFFFFFFF);
        } else {
            // La tecla en blanco con su letra encima (la de los controles de cada uno).
            g.blit(RenderPipelines.GUI_TEXTURED, TECLA, cx - 8, y, 0f, pulsada ? 16 : 0, 16, 16, 16, 32, 0xFFFFFFFF);
            g.text(mc.font, nombre, cx - mc.font.width(nombre) / 2 + 1, y + (pulsada ? 6 : 4), 0xFF2A2622, false);
        }
        g.centeredText(mc.font, Component.translatable("hud.atalaya.lianas", nombre), cx, y + 20, 0xFFFFFFFF);
    }
}
