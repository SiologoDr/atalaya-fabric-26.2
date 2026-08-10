package com.atalaya.client;

import com.atalaya.aturdimiento.Aturdimiento;
import com.atalaya.net.AtalayaRed;
import net.fabricmc.fabric.api.client.networking.v1.ClientPlayNetworking;
import net.minecraft.client.KeyMapping;
import net.minecraft.client.Minecraft;

/**
 * Cuenta las pulsaciones de saltar mientras estas aturdido y se las manda al
 * servidor.
 *
 * Hace falta avisar a mano porque el aturdimiento anula el salto: sin salto no
 * hay movimiento, y sin movimiento el servidor no tiene por donde enterarse de
 * que has tocado la tecla.
 *
 * Se cuentan FLANCOS, no ticks con la tecla abajo. Si valiera tenerla apretada,
 * dejar algo encima del teclado bastaria para librarse; asi hay que aporrearla,
 * que es lo que se pedia.
 */
public final class AturdimientoTeclado {

    private static boolean estabaAbajo = false;

    private AturdimientoTeclado() {
    }

    public static void tick(Minecraft mc) {
        if (mc.player == null) {
            estabaAbajo = false;
            return;
        }

        if (Aturdimiento.aturdido(mc.player)) {
            tragarTeclas(mc);
        }

        boolean abajo = mc.options.keyJump.isDown();
        boolean flanco = abajo && !estabaAbajo;
        estabaAbajo = abajo;

        if (!flanco) {
            return;
        }
        // Solo se manda si de verdad estas aturdido. El cliente ya sabe si lo
        // esta —el dato le llega solo—, asi que filtrar aqui ahorra un paquete
        // por cada salto normal de la partida, que son muchisimos.
        if (!Aturdimiento.aturdido(mc.player)) {
            return;
        }
        ClientPlayNetworking.send(new AtalayaRed.Salto());
    }

    /**
     * Se come las pulsaciones que abren el inventario, sueltan el objeto o lo
     * cambian de mano.
     *
     * Estas TIENEN que pararse en el cliente, porque son cosas suyas: el
     * inventario propio se abre sin preguntar al servidor. Lo demas —usar,
     * pegar, cambiar de ranura— se corta en el servidor, que es donde no se
     * puede hacer trampa.
     *
     * Funciona porque esto corre al PRINCIPIO del tick, antes de que el juego
     * mire las teclas. Cuando le toca, ya no queda ninguna pulsacion pendiente.
     */
    private static void tragarTeclas(Minecraft mc) {
        vaciar(mc.options.keyInventory);
        vaciar(mc.options.keyDrop);
        vaciar(mc.options.keySwapOffhand);
    }

    private static void vaciar(KeyMapping tecla) {
        // En bucle: consumeClick descuenta UNA pulsacion, y en un tick puede
        // haber varias si el jugador esta aporreando.
        while (tecla.consumeClick()) {
            // nada que hacer con ella, solo que no llegue
        }
    }
}
