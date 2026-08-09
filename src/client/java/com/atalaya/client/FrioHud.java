package com.atalaya.client;

import com.atalaya.Atalaya;
import com.atalaya.frio.Frio;
import com.atalaya.frio.FrioManager;
import net.fabricmc.fabric.api.client.rendering.v1.hud.HudElement;
import net.minecraft.client.DeltaTracker;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphicsExtractor;
import net.minecraft.client.player.LocalPlayer;
import net.minecraft.client.renderer.RenderPipelines;
import net.minecraft.resources.Identifier;

/**
 * Medidor de frio: un copo de nieve que se LLENA, al reves que la gota.
 *
 * Es la contraparte de {@link HidratacionHud} y se lee al reves a proposito. La
 * gota vacia avisa de que falta algo; el copo lleno avisa de que sobra. En los
 * dos casos "mucho color" significa peligro, que es lo que importa de un
 * vistazo.
 *
 * COLOCACION. Va 18 pixeles por encima de la gota, no en su sitio, porque los
 * dos medidores pueden coincidir: se puede salir de la nieve todavia helado y
 * entrar en un desierto, y entonces harian falta los dos a la vez. Un sitio fijo
 * vale mas que uno optimo cuando esta solo: el jugador aprende donde mirar.
 *
 *   guiHeight - 55   la gota de hidratacion
 *   guiHeight - 73   el copo
 *
 * Sigue dentro del pasillo central que dejan libre los corazones y los muslos,
 * asi que no tapa nada de vanilla.
 */
public class FrioHud implements HudElement {

    private static final Identifier TEXTURA =
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "textures/gui/frio.png");

    /**
     * Las dos flechas de aviso.
     *
     * Es la misma imagen de la hidratacion y su reflejo vertical, para que las
     * dos mecanicas hablen el mismo idioma: una punta hacia donde va el numero.
     * Llevan el borde negro dibujado dentro; como el tinte MULTIPLICA, el negro
     * aguanta con cualquier color y una sola imagen sirve para el rojo y para el
     * verde.
     */
    private static final Identifier FLECHA_SUBE =
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "textures/gui/flecha_sube.png");
    private static final Identifier FLECHA_BAJA =
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "textures/gui/flecha_baja.png");

    /**
     * El copo se dibuja a 17, uno mas que la gota.
     *
     * Lo manda la textura: mide 17 y aqui se pinta al mismo tamano, asi que
     * cada texel cae justo en un pixel de interfaz. Estirarla o encogerla seria
     * emborronar un dibujo hecho pixel a pixel.
     */
    private static final int TAM = 17;
    private static final int TAM_FLECHA = 11;

    /** Rojo de aviso: te estas helando. El mismo tono que usa la hidratacion. */
    private static final int ROJO = 0xFFFF5555;

    /** Verde de alivio: estas entrando en calor. */
    private static final int VERDE = 0xFF55FF55;

    /**
     * El copo llena el lienzo ENTERO, al contrario que la gota.
     *
     * La gota deja aire arriba y abajo porque es una forma compacta a la que le
     * sobra sitio. Un copo no: tiene seis brazos y un dibujo de ramas dentro, y
     * en las doce filas que usa la gota no cabia nada legible. Con las dieciseis
     * hay un tercio mas de alto y el copo se lee de un vistazo.
     */
    private static final int COPO_ARRIBA = 0;
    private static final int COPO_ALTO = TAM;

    /**
     * Cuanto sube el copo respecto al borde inferior.
     *
     * El copo va DONDE LA GOTA, no encima de ella.
     *
     * Antes vivia mas arriba, para que los dos medidores cupieran a la vez. Pero
     * coincidir es la rareza —hay que salir de la nieve todavia helado y entrar
     * en un desierto— y por cubrir ese caso el copo quedaba flotando lejos del
     * resto del HUD el 99% del tiempo, que es cuando esta solo.
     *
     * Asi que ocupa el sitio bueno, y solo cuando la gota tambien esta puesta se
     * aparta hacia arriba. El caso raro se paga en el caso raro.
     */
    private static final int ALTURA_COPO = 55;

    /** Cuanto se sube el copo si la gota le esta ocupando el sitio. */
    private static final int APARTARSE = 18;

    /**
     * El frio que ya llevas encima: blanco, o sea SIN tenir.
     *
     * El color vive en la textura, no aqui, al reves que en la gota. Se hizo
     * asi porque el tinte MULTIPLICA, y multiplicar una rampa de gris por un
     * solo color encierra el degradado en un unico matiz: solo puede ir de
     * claro a oscuro del mismo tono. Con un celeste palido encima, la diferencia
     * entre la punta y la base no se veia.
     *
     * Con el color dentro de la imagen, el copo va de blanco casi puro a azul
     * cielo vivo, que si se lee. Y el truco de las dos pasadas sigue en pie:
     * blanco deja la imagen tal cual y {@link #VACIO} la apaga entera.
     */
    private static final int HIELO = 0xFFFFFFFF;

    /**
     * Lo que aun no se ha helado. Es el mismo dibujo apagado, no un agujero:
     * asi se ve el tamano del medidor aunque este a cero.
     */
    private static final int VACIO = 0xFF2E3E46;

    /**
     * Cada cuantos ticks se vuelven a mirar bioma y fuentes de calor.
     *
     * Esto NO es un adorno. Buscar una hoguera recorre casi mil bloques, y aqui
     * se dibuja en cada fotograma: a 60 fps serian sesenta mil consultas por
     * segundo en el cliente por una flecha que solo puede cambiar una vez por
     * segundo, que es el ritmo al que el servidor mueve el numero.
     *
     * Diez ticks —medio segundo— dejan la flecha respondiendo antes de que el
     * nivel se mueva, con la vigesima parte del trabajo.
     */
    private static final int TICKS_CACHE = 10;

    private int ultimoTick = Integer.MIN_VALUE;
    private boolean cacheHaceFrio;
    private boolean cacheSeEnfria;

    @Override
    public void extractRenderState(GuiGraphicsExtractor grafico, DeltaTracker delta) {
        LocalPlayer jugador = Minecraft.getInstance().player;
        if (jugador == null) {
            return;
        }
        // Con la mecanica apagada no se dibuja nada, aunque el jugador conserve
        // puntos de una partida anterior. El dato lo manda el servidor, porque
        // en red el cliente no ve su configuracion.
        if (!Frio.activa(jugador)) {
            return;
        }

        refrescar(jugador);

        // Se ensena donde hace frio, y ademas SIEMPRE que quede frio encima,
        // hasta que llegue a cero.
        //
        // Esto es distinto de la gota, y a proposito. Alli el medidor se esconde
        // fuera del desierto porque la hidratacion se queda quieta: no hay nada
        // que mirar. Aqui el frio se esta yendo solo mientras andas, asi que
        // esconderlo al salir del bioma se lee como que te lo han quitado de
        // golpe, cuando en realidad quedan dos minutos y medio de deshielo.
        //
        // Ver la cuenta atras ES la informacion: te dice si ya puedes darte la
        // vuelta o todavia no.
        float fraccion = Frio.fraccion(jugador);
        if (!cacheHaceFrio && fraccion <= 0) {
            return;
        }

        int x = grafico.guiWidth() / 2 - TAM / 2;
        int y = grafico.guiHeight() - ALTURA_COPO
                - (HidratacionHud.visible(jugador) ? APARTARSE : 0);

        // Primero el copo entero apagado: es el fondo del medidor.
        grafico.blit(RenderPipelines.GUI_TEXTURED, TEXTURA,
                x, y, 0f, 0f, TAM, TAM, TAM, TAM, VACIO);

        // Y encima solo la parte de abajo, la que ya se ha helado. Sube desde la
        // base igual que la gota, aunque aqui signifique lo contrario.
        int lleno = Math.round(COPO_ALTO * fraccion);
        if (lleno > 0) {
            int desde = COPO_ARRIBA + (COPO_ALTO - lleno);
            grafico.blit(RenderPipelines.GUI_TEXTURED, TEXTURA,
                    x, y + desde, 0f, desde, TAM, lleno, TAM, TAM, HIELO);
        }

        // Flecha de direccion.
        //
        // Distingue lo que el copo solo no puede: estar helado no es lo mismo
        // que estarse helando. Junto a una hoguera el medidor baja, y sin este
        // aviso el jugador no sabria si le vale con quedarse quieto o tiene que
        // encender algo ya.
        //
        // Hay dos porque aqui, a diferencia de la hidratacion, el nivel se mueve
        // en los dos sentidos por si solo: se sube pasando frio y se baja junto
        // al fuego. Roja arriba avisa; verde abajo tranquiliza.
        //
        // La condicion se calcula aqui en el cliente: bioma, luz y bloques son
        // datos que ya tiene, asi que no hay que mandarle nada.
        //
        // Va FUERA del lienzo, no pisandolo como en la gota. Aquella ocupa nueve
        // pixeles de los dieciseis y deja sitio de sobra a la derecha; el copo
        // los usa todos, asi que ahi la flecha caeria justo encima de un brazo.
        if (cacheSeEnfria) {
            grafico.blit(RenderPipelines.GUI_TEXTURED, FLECHA_SUBE,
                    x + TAM, y + COPO_ARRIBA + 2, 0f, 0f,
                    TAM_FLECHA, TAM_FLECHA, TAM_FLECHA, TAM_FLECHA, ROJO);
        } else if (fraccion > 0) {
            grafico.blit(RenderPipelines.GUI_TEXTURED, FLECHA_BAJA,
                    x + TAM, y + COPO_ARRIBA + 2, 0f, 0f,
                    TAM_FLECHA, TAM_FLECHA, TAM_FLECHA, TAM_FLECHA, VERDE);
        }
    }

    /**
     * Vuelve a mirar bioma y calor si ya toca, y si no deja lo de la ultima vez.
     *
     * El reloj es el tickCount del jugador y no un contador propio: asi la cache
     * sigue el ritmo del mundo y no el de los fotogramas, que puede ir a 30 o a
     * 200 segun la maquina.
     */
    private void refrescar(LocalPlayer jugador) {
        int ahora = jugador.tickCount;
        if (ahora - ultimoTick < TICKS_CACHE && ultimoTick != Integer.MIN_VALUE) {
            return;
        }
        ultimoTick = ahora;
        cacheHaceFrio = FrioManager.haceFrio(jugador);
        // Solo se busca fuego si de verdad hace frio aqui. Fuera, la flecha ya
        // va a ser la verde de todas formas, y buscarlo es la parte cara.
        cacheSeEnfria = cacheHaceFrio && !FrioManager.cercaDeCalor(jugador);
    }
}
