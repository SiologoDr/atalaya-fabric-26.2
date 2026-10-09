package com.atalaya.mixin.client;

import com.atalaya.client.DueloCantoCliente;
import com.atalaya.client.OfrendaCliente;
import net.minecraft.client.KeyboardHandler;
import net.minecraft.client.Minecraft;
import net.minecraft.client.input.KeyEvent;
import org.lwjgl.glfw.GLFW;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/**
 * Las teclas de la Ofrenda al Sol.
 *
 * Mientras Novilis tiene al jugador en las manos, cada letra que pulsa va a la
 * secuencia (OfrendaCliente) y NO al juego: si no, la W andaria, la E abriria
 * el inventario y la Q tiraria lo que lleva en la mano. Las demas teclas
 * (numeros, espacio, mayusculas...) ni cuentan ni fallan: tambien se tragan.
 * Escape y las F siguen funcionando.
 *
 * La letra sale de la distribucion del teclado (glfwGetKeyName), no de la
 * posicion: en un teclado AZERTY, la A es la A. Solo cuenta al pulsar, no al
 * mantener (las repeticiones del teclado no fallan).
 */
@Mixin(KeyboardHandler.class)
public abstract class OfrendaTecladoMixin {

    @Inject(method = "keyPress", at = @At("HEAD"), cancellable = true)
    private void atalaya$ofrenda(long ventana, int accion, KeyEvent evento, CallbackInfo ci) {
        // Lo mismo para el Duelo de Canto de Nerea (las teclas A, S, D y F de sus carriles).
        boolean duelo = DueloCantoCliente.activo();
        if ((!OfrendaCliente.activo() && !duelo) || Minecraft.getInstance().gui.screen() != null) {
            return;
        }
        int tecla = evento.key();
        if (tecla == GLFW.GLFW_KEY_ESCAPE || (tecla >= GLFW.GLFW_KEY_F1 && tecla <= GLFW.GLFW_KEY_F25)) {
            return;
        }
        ci.cancel();
        if (accion != GLFW.GLFW_PRESS) {
            return;
        }
        String nombre = GLFW.glfwGetKeyName(tecla, evento.scancode());
        if (nombre == null || nombre.length() != 1) {
            return;
        }
        char c = Character.toUpperCase(nombre.charAt(0));
        if (c >= 'A' && c <= 'Z') {
            if (duelo) {
                DueloCantoCliente.pulsar(c);
            } else {
                OfrendaCliente.pulsar(c);
            }
        }
    }
}
