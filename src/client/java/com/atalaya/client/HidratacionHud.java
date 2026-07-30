package com.atalaya.client;

import com.atalaya.Atalaya;
import com.atalaya.hidratacion.Hidratacion;
import com.atalaya.hidratacion.HidratacionManager;
import net.fabricmc.fabric.api.client.rendering.v1.hud.HudElement;
import net.minecraft.client.DeltaTracker;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphicsExtractor;
import net.minecraft.client.player.LocalPlayer;
import net.minecraft.client.renderer.RenderPipelines;
import net.minecraft.resources.Identifier;

/**
 * Medidor de hidratacion: una gota que se vacia, con el porcentaje encima.
 *
 * Solo aparece dentro del desierto, que es el unico sitio donde el nivel se
 * mueve. Fuera no se dibuja nada, para no ocupar pantalla con un numero que no
 * va a cambiar.
 *
 * El nivel lo trae solo la API de attachments (ver {@link Hidratacion}), asi
 * que aqui no hay red que gestionar: el cliente ya tiene el dato de su propio
 * jugador cuando le toca dibujar.
 *
 * COLOCACION. Las tres medidas de vanilla que hay que esquivar, sacadas del
 * bytecode de ContextualBar y del HUD:
 *
 *   guiHeight - 29   arriba de la barra de experiencia
 *   guiHeight - 35   el numero de nivel, centrado
 *   guiHeight - 39   la fila de corazones y muslos
 *   guiHeight - 49   la armadura (izquierda) y las burbujas (derecha)
 *
 * Los corazones llegan hasta centerX - 11 y los muslos empiezan en centerX + 10,
 * asi que en el centro queda un pasillo de unos 21 pixeles. La gota mide 9 de
 * ancho y le sobra sitio.
 *
 * No lleva numero: el nivel se lee por lo que queda de celeste. Como son 12
 * pixeles de alto para 100 puntos, cada pixel vale unos 8 puntos, asi que esto
 * informa de un vistazo y no al detalle, que es justo lo que se quiere.
 *
 * Y no choca con {@link AvisoTrajeHud}, que vive pegado a la esquina inferior
 * derecha: este va centrado. Son ademas dos elementos de HUD distintos, cada
 * uno con su registro, asi que ninguno puede tapar al otro por orden de pintado.
 */
public class HidratacionHud implements HudElement {

    private static final Identifier TEXTURA =
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "textures/gui/hidratacion.png");

    private static final int TAM = 16;

    /**
     * La gota NO llena el lienzo: mide 9x12 y ocupa de la fila 2 a la 13, con
     * aire arriba y abajo. El medidor tiene que recortar por esas filas y no
     * por el lienzo entero, o el agua se quedaria a media altura al llenarse.
     */
    private static final int GOTA_ARRIBA = 2;
    private static final int GOTA_ALTO = 12;

    /**
     * Cuanto sube la gota respecto al borde inferior.
     *
     * 55 la deja justo encima del numero de experiencia (que esta en 35) y con
     * su base rozando la fila de corazones (39), dentro del pasillo central.
     */
    private static final int ALTURA_GOTA = 55;

    /**
     * Lo que queda por beber: celeste.
     *
     * El degradado NO se hace aqui. El relleno de la textura ya es una rampa de
     * gris, clara arriba y oscura abajo, y como el tinte MULTIPLICA, pintarla
     * de un solo celeste conserva la rampa: sale celeste claro arriba y hondo
     * abajo sin dibujar el medidor por franjas.
     */
    private static final int AGUA = 0xFF6FD9FF;

    /**
     * El hueco vacio. Es el mismo dibujo en un azul casi negro, no un agujero:
     * asi se ve el tamano del deposito aunque este seco, y el contraste con el
     * celeste hace evidente por donde va el nivel.
     *
     * El contorno de la textura es negro, y negro por cualquier color sigue
     * siendo negro, asi que la misma imagen vale para los dos estados.
     */
    private static final int VACIO = 0xFF33444C;

    @Override
    public void extractRenderState(GuiGraphicsExtractor grafico, DeltaTracker delta) {
        Minecraft mc = Minecraft.getInstance();
        LocalPlayer jugador = mc.player;
        // Sin comprobar el F1: en 26.2 ese estado ya no vive en Options, lo
        // lleva el propio pipeline del HUD, que se salta los elementos enteros.
        // Por eso AvisoTrajeHud tampoco lo mira.
        if (jugador == null) {
            return;
        }
        if (!HidratacionManager.enDesierto(jugador)) {
            return; // fuera del desierto no se gasta, asi que no se ensena
        }

        float fraccion = Hidratacion.fraccion(jugador);

        int x = grafico.guiWidth() / 2 - TAM / 2;
        int y = grafico.guiHeight() - ALTURA_GOTA;

        // Primero la gota entera apagada: es el fondo del medidor.
        grafico.blit(RenderPipelines.GUI_TEXTURED, TEXTURA,
                x, y, 0f, 0f, TAM, TAM, TAM, TAM, VACIO);

        // Y encima solo la parte de abajo, que es la que sigue llena. Se
        // recorta por la V de la textura ademas de por la posicion, para que el
        // agua aparezca subiendo desde la base y no cayendo desde arriba.
        int lleno = Math.round(GOTA_ALTO * fraccion);
        if (lleno > 0) {
            int desde = GOTA_ARRIBA + (GOTA_ALTO - lleno);
            grafico.blit(RenderPipelines.GUI_TEXTURED, TEXTURA,
                    x, y + desde, 0f, desde, TAM, lleno, TAM, TAM, AGUA);
        }
    }
}
