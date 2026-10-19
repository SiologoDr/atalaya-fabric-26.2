package com.atalaya.catalogo;

import org.jspecify.annotations.Nullable;

/**
 * Las tres listas del catalogo del evento (18-10-2026). Juan: "categorizalo bien ... el cambio de dificultad de 30 min a
 * mitad de vida seria un momento fractura, es decir seria en otro menu"; y "categorizalo en cambio de dificultad, nuevo
 * mob"; los minijuegos y las penalizaciones, "creo que no van por ahora".
 *
 * <pre>
 *   CAMBIO    /atalaya menu cambios    reglas que se quedan (al jugador, al mundo, a los objetos, a los mobs de siempre):
 *                                      ON lanza la Ruleta (final de dificultad) y se aplica al salir su aviso
 *   MOB       /atalaya menu mobs       los mobs nuevos: ON lanza la Ruleta (final del huevo) y, al salir su aviso, el mob
 *                                      empieza a aparecer en su sitio; OFF deja de aparecer
 *   MOMENTO   /atalaya menu momentos   lo que dura un rato (o hasta que se cumple una prueba): ON lanza el Momento
 *                                      Fractura con su texto y se aplica al salir el aviso; acaba solo o con OFF
 * </pre>
 */
public enum Categoria {

    CAMBIO("cambios", "cambio", "titulo_cambios", "Buscar un cambio...", 0xFFFFD23A),
    MOB("mobs", "mob", "titulo_mobs", "Buscar un mob...", 0xFFFF9A3C),
    MOMENTO("momentos", "momento", "titulo_momentos", "Buscar un momento...", 0xFFFF5A4A);

    /** Su palabra en el comando. */
    public final String nombre;
    /** Su palabra en las texturas: los iconos del menu (menu/&lt;prefijo&gt;/&lt;id&gt;) y los rotulos del chat. */
    public final String prefijo;
    /** El sprite del titulo de su menu (textures/gui/sprites/menu). */
    public final String titulo;
    /** Lo que dice el buscador vacio. */
    public final String pista;
    /** El color de los titulos de sus filas. */
    public final int color;

    Categoria(String nombre, String prefijo, String titulo, String pista, int color) {
        this.nombre = nombre;
        this.prefijo = prefijo;
        this.titulo = titulo;
        this.pista = pista;
        this.color = color;
    }

    public static @Nullable Categoria porNombre(String nombre) {
        for (Categoria c : values()) {
            if (c.nombre.equals(nombre)) {
                return c;
            }
        }
        return null;
    }
}
