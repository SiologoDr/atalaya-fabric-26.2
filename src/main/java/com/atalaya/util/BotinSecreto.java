package com.atalaya.util;

/**
 * Marca en un bloque cepillable para que NO se vea lo que lleva dentro hasta
 * haberlo limpiado del todo.
 *
 * Va en un paquete aparte del de los mixins a proposito: lo que hay en
 * {@code com.atalaya.mixin} se procesa como mixin, y esto es una interfaz
 * normal que tienen que poder usar las clases de siempre.
 *
 * Lo implementa {@code BotinSecretoMixin} sobre BrushableBlockEntity.
 */
public interface BotinSecreto {

    /** Que el contenido no viaje al cliente hasta la ultima pasada. */
    void atalaya$guardarElSecreto();

    boolean atalaya$esSecreto();
}
