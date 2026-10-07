package com.atalaya.client;

import com.atalaya.Atalaya;
import com.atalaya.habilidad.HabilidadEstado;
import com.atalaya.habilidad.Habilidades;
import com.atalaya.item.ArmadurasJefes;
import net.fabricmc.fabric.api.client.rendering.v1.hud.HudElement;
import net.minecraft.client.DeltaTracker;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphicsExtractor;
import net.minecraft.client.player.LocalPlayer;
import net.minecraft.client.renderer.RenderPipelines;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.Identifier;
import net.minecraft.util.Mth;

/**
 * El icono de la habilidad de la armadura, a la derecha de la hotbar: solo con
 * un conjunto entero puesto. Lista, el icono limpio; activa, late y una barra
 * del color del elemento se va gastando debajo; en recarga, se oscurece desde
 * arriba lo que le falta y dice los segundos que quedan.
 *
 * A su derecha, la tecla que la lanza (la que haya en Controles, categoria
 * Atalaya; R por defecto), dibujada como una tecla: encendida del color del
 * elemento cuando esta lista, apagada mientras esta activa o en recarga.
 */
public class HabilidadHud implements HudElement {

    private static final Identifier MARCO = tex("marco");
    private static final Identifier[] ICONOS = {tex("manantial"), tex("muralla"), tex("corriente"), tex("furia")};
    /** El color de cada elemento, en el orden de ArmadurasJefes.Tema. */
    private static final int[] COLOR = {0xFF4FD8E8, 0xFF5BE38A, 0xFFC9A6FF, 0xFFFFB238};

    private static final int MARCO_TAM = 22;
    private static final int ICONO = 18;
    private static final int MEDIA_HOTBAR = 91;
    private static final int SEPARACION = 6;
    /** La tecla dibujada: alto, hueco con el marco y lo que puede medir de ancho. */
    private static final int TECLA_ALTO = 12;
    private static final int TECLA_HUECO = 3;
    private static final int TECLA_MAX = 60;

    private static Identifier tex(String nombre) {
        return Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "textures/gui/habilidad/" + nombre + ".png");
    }

    @Override
    public void extractRenderState(GuiGraphicsExtractor g, DeltaTracker delta) {
        Minecraft mc = Minecraft.getInstance();
        LocalPlayer jugador = mc.player;
        if (jugador == null || jugador.isSpectator()) {
            return;
        }
        ArmadurasJefes.Tema tema = Habilidades.conjunto(jugador);
        if (tema == null) {
            return;
        }
        HabilidadEstado e = jugador.getAttachedOrElse(Habilidades.ESTADO, HabilidadEstado.NADA);
        float parcial = delta.getGameTimeDeltaPartialTick(false);
        float ahora = jugador.level().getGameTime() + parcial;
        int x = g.guiWidth() / 2 + MEDIA_HOTBAR + SEPARACION;
        int y = g.guiHeight() - MARCO_TAM - 1;
        int i = tema.ordinal();
        g.blit(RenderPipelines.GUI_TEXTURED, MARCO, x, y, 0.0F, 0.0F, MARCO_TAM, MARCO_TAM, MARCO_TAM, MARCO_TAM);
        boolean activa = e.tema() == i && ahora < e.hasta();
        boolean recarga = ahora < e.lista();
        int tinte = 0xFFFFFFFF;
        if (activa) {
            float k = 0.8F + 0.2F * Mth.sin(ahora * 0.3F);
            int v = Math.round(255 * k);
            tinte = 0xFF000000 | (v << 16) | (v << 8) | v;
        } else if (recarga) {
            tinte = 0xFF6A6A6A;
        }
        g.blit(RenderPipelines.GUI_TEXTURED, ICONOS[i], x + 2, y + 2, 0.0F, 0.0F, ICONO, ICONO, ICONO, ICONO, tinte);
        if (activa) {
            // Lo que queda de la activa: una barra del color del elemento bajo el marco.
            float queda = Mth.clamp((e.hasta() - ahora) / Habilidades.DURACION, 0.0F, 1.0F);
            g.fill(x + 1, y + MARCO_TAM - 3, x + MARCO_TAM - 1, y + MARCO_TAM - 1, 0xAA000000);
            g.fill(x + 1, y + MARCO_TAM - 3, x + 1 + Math.round((MARCO_TAM - 2) * queda), y + MARCO_TAM - 1, COLOR[i]);
        } else if (recarga) {
            // La recarga: se oscurece lo que falta, de arriba abajo, y los segundos encima.
            float falta = Mth.clamp((e.lista() - ahora) / Habilidades.RECARGA, 0.0F, 1.0F);
            g.fill(x + 2, y + 2, x + 2 + ICONO, y + 2 + Math.round(ICONO * falta), 0x99000000);
            String segundos = Integer.toString(Mth.ceil((e.lista() - ahora) / 20.0F));
            g.text(mc.font, segundos, x + MARCO_TAM / 2 - mc.font.width(segundos) / 2, y + 7, 0xFFFFFFFF, true);
        }
        tecla(g, mc, x + MARCO_TAM + TECLA_HUECO, y + (MARCO_TAM - TECLA_ALTO) / 2, !activa && !recarga ? COLOR[i] : 0xFF5A5A5A);
    }

    /** La tecla de la habilidad, como una tecla de teclado: borde, cara y la letra. */
    private static void tecla(GuiGraphicsExtractor g, Minecraft mc, int x, int y, int borde) {
        if (HabilidadCliente.TECLA == null) {
            return;
        }
        String nombre = HabilidadCliente.TECLA.isUnbound() ? "?" : HabilidadCliente.TECLA.getTranslatedKeyMessage().getString();
        if (mc.font.width(nombre) > TECLA_MAX - 6) {
            nombre = mc.font.plainSubstrByWidth(nombre, TECLA_MAX - 10) + "..";
        }
        int ancho = Math.max(TECLA_ALTO, mc.font.width(nombre) + 6);
        boolean lista = borde != 0xFF5A5A5A;
        // borde del color del elemento, la cara oscura y, debajo, el canto de la tecla
        g.fill(x, y, x + ancho, y + TECLA_ALTO, borde);
        g.fill(x + 1, y + 1, x + ancho - 1, y + TECLA_ALTO - 2, 0xFF1C1C22);
        g.fill(x + 1, y + TECLA_ALTO - 2, x + ancho - 1, y + TECLA_ALTO - 1, 0xFF0C0C10);
        g.text(mc.font, Component.literal(nombre), x + (ancho - mc.font.width(nombre) + 1) / 2, y + 2,
                lista ? 0xFFFFFFFF : 0xFF9A9A9A, true);
    }
}
