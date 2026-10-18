package com.atalaya.cambios;

import org.jspecify.annotations.Nullable;

/**
 * Los cambios de dificultad (17-10-2026). Juan: "ahora haremos cambios de dificultad, los quiero en un menu ... y ahi
 * esten todos los cambios de dificultad que te diga"; y de los primeros, que son los de DEDsafio 2: "el titulo y
 * contenido cambialo para que no sea lo mismo". Asi que la mecanica es la misma y el titulo y el texto, nuestros.
 *
 * Cada cambio se enciende desde el menu (/atalaya menu cambios): sale la Ruleta en su final de dificultad, con el
 * titulo del cambio como rotulo del chat y su texto debajo, y al salir el aviso se aplica (CambiosDificultad). Apagarlo
 * lo quita al momento, sin animacion.
 *
 * El titulo es tambien el de su rotulo del chat: los cuadros cambio_<id>_NN que hace menus_cambios.py, cuantos dice al
 * hacerlos (cartel).
 */
public enum Cambio {

    /** Los evocadores no sueltan totems (en DEDsafio 2, "Solo se vive una vez"). */
    NI_UN_TOTEM_MAS("ni_un_totem_mas", "NI UN TÓTEM MÁS",
            "Los evocadores ya no sueltan tótems de la inmortalidad. Los que tengas son los últimos.", 13, 0),
    /** El End, cerrado para siempre (en DEDsafio 2, "Confinamiento dimensional"). */
    END_SELLADO("end_sellado", "EL END, SELLADO",
            "Los portales del End ya no llevan a ninguna parte: el End queda cerrado para siempre.", 13, 0),
    /** Media vida durante media hora (en DEDsafio 2 no tenia titulo). */
    VIDA_A_MEDIAS("vida_a_medias", "VIDA A MEDIAS",
            "Durante 30 minutos, todos los jugadores tienen la mitad de la vida máxima.", 11, 30 * 60 * 20),
    /** Se abre el Nether (en DEDsafio 2, "Las puertas al infierno"). */
    PORTALES_ARDEN("portales_arden", "LOS PORTALES ARDEN",
            "Los portales vuelven a encenderse: el Nether queda abierto.", 16, 0);

    /** Su nombre en el codigo, en las texturas y en lo que se guarda. */
    public final String id;
    /** El titulo (el del menu y el del rotulo del chat). */
    public final String titulo;
    /** Lo que dice el aviso del chat debajo del titulo (y el menu). */
    public final String texto;
    /** Los cuadros de su rotulo del chat. */
    public final int cartel;
    /** Lo que dura (ticks de juego); 0, hasta que se apague. */
    public final int duracion;

    Cambio(String id, String titulo, String texto, int cartel, int duracion) {
        this.id = id;
        this.titulo = titulo;
        this.texto = texto;
        this.cartel = cartel;
        this.duracion = duracion;
    }

    public static @Nullable Cambio porId(String id) {
        for (Cambio c : values()) {
            if (c.id.equals(id)) {
                return c;
            }
        }
        return null;
    }
}
