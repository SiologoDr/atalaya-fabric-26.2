package com.atalaya.catalogo;

/**
 * Una entrada del catalogo del evento: un cambio de dificultad, un mob nuevo o un momento. Su titulo es tambien el de su
 * rotulo del chat (los cuadros &lt;prefijo&gt;_&lt;id&gt;_NN que hace catalogo.py; cuantos son lo dice Carteles) y su
 * icono el del menu (textures/gui/sprites/menu/&lt;prefijo&gt;/&lt;id&gt;).
 */
public interface Entrada {

    /** Su nombre en el codigo, en las texturas y en lo que se guarda. */
    String id();

    /** El titulo (el del menu y el del rotulo del chat). */
    String titulo();

    /** Lo que dice el aviso del chat debajo del titulo (y el menu). */
    String texto();

    Categoria categoria();

    /** El nombre de los cuadros de su rotulo del chat (sin el numero). */
    default String cartel() {
        return categoria().prefijo + "_" + id();
    }

    /** El sprite de su icono en el menu. */
    default String icono() {
        return categoria().prefijo + "/" + id();
    }

    /** El grupo del menu en el que va (el nombre que sale encima de los suyos), o "" si no va en ninguno. */
    default String grupo() {
        return "";
    }

    /** Las palabras por las que tambien se encuentra en el buscador (ademas del titulo y el texto). */
    default String etiquetas() {
        return "";
    }
}
