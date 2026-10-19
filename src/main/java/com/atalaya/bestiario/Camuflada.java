package com.atalaya.bestiario;

/**
 * Un mob del bestiario que se esconde tomando el color del suelo (la Trampa Verde): mientras esta camuflado, el render
 * lo tine del verde de la hierba de su bioma (su textura de camuflaje va en grises, como la hierba de Minecraft).
 */
public interface Camuflada {

    /** Si ahora mismo esta escondido (y hay que tenirlo). */
    boolean camuflada();
}
