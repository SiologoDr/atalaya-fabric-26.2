package com.atalaya.momento;

import com.atalaya.catalogo.Categoria;
import com.atalaya.catalogo.Entrada;

import java.util.function.Supplier;

/**
 * Los momentos del catalogo (/atalaya menu momentos): lo que dura un rato o hasta que se cumple una prueba, presentado
 * con el Momento Fractura (su cinematica, el cielo roto y el aviso del chat). Juan, 18-10-2026: "el cambio de dificultad
 * de 30 min a mitad de vida seria un momento fractura, es decir seria en otro menu"; y "vas a meter todo de la ficha de
 * busqueda de dedsafio con otro diseno, funcionalidad parecida pero con el mismo objetivo". Son los «Momentos Reviil»
 * del DEDsafio 2, 3 y 4 (en cada uno, de donde sale), con nuestro titulo y nuestro texto.
 *
 * Cada uno lleva su Suceso (lo que hace mientras dura) y lo que dura despues del aviso (0, hasta que se apague o hasta
 * que su contador llegue a cero). Los que tienen contador lo ponen arriba en el centro, como la prueba de la tierra.
 */
public enum Momento implements Entrada {

    // ------------------------------------------------------------------
    //  Ponte a salvo (un contador; al llegar a cero, lo que no este a salvo, muere)
    // ------------------------------------------------------------------

    /** DEDsafio 4, el gas: subir por encima de la capa 250. */
    GAS_QUE_SUBE("gas_que_sube", Grupo.SALVO, "EL GAS QUE SUBE",
            "Un gas invisible llena el mundo. Antes de que el contador llegue a cero, sube por encima de la capa 250 o morirás.",
            0, SucesosRefugio.GasSube::new),
    /** DEDsafio 4, el gas: bajar a una capa negativa. */
    GAS_QUE_BAJA("gas_que_baja", Grupo.SALVO, "EL GAS QUE BAJA",
            "Un gas invisible cae del cielo. Antes de que el contador llegue a cero, baja por debajo de la capa 0 o morirás.",
            0, SucesosRefugio.GasBaja::new),
    /** DEDsafio 4, el gas: entre las capas 120 y 130. */
    LA_FRANJA("la_franja", Grupo.SALVO, "LA FRANJA",
            "Solo una franja del cielo queda limpia. Antes de que el contador llegue a cero, ponte entre las capas 120 y 130 del mundo.",
            0, SucesosRefugio.Franja::new),
    /** DEDsafio 4, el rayo mortal (el bunker de Eon). */
    EL_RAYO("el_rayo", Grupo.SALVO, "EL RAYO",
            "Un rayo va a caer sobre todo el que esté al raso. Antes de que el contador llegue a cero, métete bajo techo.",
            0, SucesosRefugio.Rayo::new),
    /** DEDsafio 4, la lluvia de meteoritos (y el Nether cerrado). */
    LLUVIA_DE_METEORITOS("lluvia_de_meteoritos", Grupo.SALVO, "LLUVIA DE METEORITOS",
            "Caen meteoritos y el Nether se cierra. Cuando el contador llegue a cero caerá el más grande: que te pille bajo techo.",
            0, SucesosRefugio.Meteoritos::new),
    /** DEDsafio 4, el agujero negro (al bunker o te consume). */
    EL_AGUJERO_NEGRO("el_agujero_negro", Grupo.SALVO, "EL AGUJERO NEGRO",
            "Un agujero negro se abre en el cielo y tira de todo lo que está al raso. Cuando llegue a cero, quien no esté bajo techo será tragado.",
            0, SucesosRefugio.AgujeroNegro::new),
    /** DEDsafio 4, las supernovas (alejarse antes de la onda). */
    LA_SUPERNOVA("la_supernova", Grupo.SALVO, "LA SUPERNOVA",
            "Una estrella va a estallar encima de todos. Antes de que el contador llegue a cero, aléjate 300 bloques de donde estabais, o sal del mundo.",
            0, SucesosRefugio.Supernova::new),
    /** DEDsafio 4, la Luna de Sangre (a las bases, con creepers de un corazon). */
    LUNA_DE_SANGRE("luna_de_sangre", Grupo.SALVO, "LUNA DE SANGRE",
            "Cae la noche y la luna sangra. Vuelve a tu cama antes de que el contador llegue a cero. Mientras, los creepers caen sobre vosotros.",
            0, SucesosRefugio.LunaDeSangre::new),
    /** DEDsafio 3, la tormenta de Wither (salir del mundo de arriba). */
    TORMENTA_MARCHITA("tormenta_marchita", Grupo.SALVO, "TORMENTA MARCHITA",
            "Una tormenta que marchita llega al mundo. Cuando el contador llegue a cero, quien siga en él se marchitará hasta morir.",
            0, SucesosRefugio.TormentaMarchita::new),
    /** DEDsafio 4, todos bajo el agua (cinco minutos y sin salir). */
    BAJO_EL_AGUA("bajo_el_agua", Grupo.SALVO, "BAJO EL AGUA",
            "Tienes cinco minutos para meterte entero bajo el agua, y después dos más sin salir. Fuera de ella, el aire te quemará.",
            0, SucesosRefugio.BajoElAgua::new),
    /** DEDsafio 4, el Momento encadenado (cada aviso suma una condicion). */
    EL_ENCADENADO("el_encadenado", Grupo.SALVO, "EL ENCADENADO",
            "Cuatro peligros, uno detrás de otro: bajo tierra, luego al cielo, luego los tornados y al final, bajo techo. Atento al chat.",
            0, SucesosRefugio.Encadenado::new),

    // ------------------------------------------------------------------
    //  Pruebas (cumplelas antes de que llegue a cero o la fractura se te lleva)
    // ------------------------------------------------------------------

    /** DEDsafio 3, matar 4000 mobs entre todos en 10 minutos. */
    LA_GRAN_CAZA("la_gran_caza", Grupo.PRUEBAS, "LA GRAN CAZA",
            "Entre todos, matad cuarenta monstruos por cabeza antes de que el contador llegue a cero. Si no, la fractura se os lleva a todos.",
            0, SucesosPrueba.GranCaza::new),
    /** DEDsafio 3, romper un Sculk Shrieker en 10 minutos. */
    EL_GRITO_DEL_ABISMO("el_grito_del_abismo", Grupo.PRUEBAS, "EL GRITO DEL ABISMO",
            "Rompe un chillón de sculk antes de que el contador llegue a cero, o la fractura te llevará.",
            0, SucesosPrueba.Grito::new),
    /** El nuestro (16-10-2026): romper diez de tierra o cesped antes del contador. */
    LA_PRUEBA_DE_LA_TIERRA("la_prueba_de_la_tierra", Grupo.PRUEBAS, "LA PRUEBA DE LA TIERRA",
            "Rompe diez bloques de tierra o césped antes de que el contador llegue a cero, o la fractura te llevará.",
            0, SucesosPrueba.Tierra::new),

    // ------------------------------------------------------------------
    //  Mientras dura
    // ------------------------------------------------------------------

    /** DEDsafio 2, la media vida durante 30 minutos. */
    VIDA_A_MEDIAS("vida_a_medias", Grupo.MIENTRAS, "VIDA A MEDIAS",
            "Durante 30 minutos, todos los jugadores tienen la mitad de la vida máxima.", 30 * 60,
            SucesosRegla.MediaVida::new),
    /** DEDsafio 3, «Se hizo la oscuridad». */
    LA_OSCURIDAD("la_oscuridad", Grupo.MIENTRAS, "SE HIZO LA OSCURIDAD",
            "Durante cinco minutos, la oscuridad lo cubre todo y ni las pociones de visión nocturna la atraviesan.", 5 * 60,
            SucesosRegla.Oscuridad::new),
    /** DEDsafio 3, la caida lenta que deja de funcionar. */
    NADA_FRENA_LA_CAIDA("nada_frena_la_caida", Grupo.MIENTRAS, "NADA FRENA LA CAÍDA",
            "Durante cinco minutos, la caída lenta no sirve y las élitros no planean.", 5 * 60,
            SucesosRegla.SinCaidaLenta::new),
    /** DEDsafio 3, «Reviil ha removido las cubetas de agua». */
    SEQUIA("sequia", Grupo.MIENTRAS, "SEQUÍA",
            "Durante diez minutos, los cubos de agua se secan y no se pueden volver a llenar.", 10 * 60,
            SucesosRegla.Sequia::new),
    /** DEDsafio 4, intercambio de posiciones, vida oculta y sin regeneracion. */
    EL_INTERCAMBIO("el_intercambio", Grupo.MIENTRAS, "EL INTERCAMBIO",
            "Todos cambiáis de sitio al azar, dos veces. Durante cinco minutos no veis vuestra vida ni la recuperáis sola.", 5 * 60,
            SucesosRegla.Intercambio::new),
    /** DEDsafio 4, «Todos se volvieron nutrias». */
    TODOS_DIMINUTOS("todos_diminutos", Grupo.MIENTRAS, "TODOS DIMINUTOS",
            "Todos encogéis y no podéis saltar ni un bloque. Solo la Píldora del Tamaño os devuelve a vuestra altura.", 20 * 60,
            SucesosRegla.Diminutos::new),
    /** DEDsafio 4, la infeccion zombi (la plaga con 3 minutos). */
    LA_INFECCION("la_infeccion", Grupo.MIENTRAS, "LA INFECCIÓN",
            "La plaga se propaga por el aire: todos la lleváis con tres minutos. Durante un cuarto de hora, sobrevivid a base de píldoras.", 15 * 60,
            SucesosRegla.Infeccion::new),
    /** DEDsafio 4, el eclipse solar (los mobs salen de dia). */
    EL_ECLIPSE("el_eclipse", Grupo.MIENTRAS, "EL ECLIPSE",
            "Durante diez minutos el sol se apaga: los monstruos salen de día y no arden. Mantente en la superficie.", 10 * 60,
            SucesosRegla.Eclipse::new),

    // ------------------------------------------------------------------
    //  Sucesos
    // ------------------------------------------------------------------

    /** DEDsafio 3 y 4, los creepers electricos de un corazon en tu posicion. */
    LLUVIA_DE_CREEPERS("lluvia_de_creepers", Grupo.SUCESOS, "LLUVIA DE CREEPERS",
            "Durante cinco minutos, en cualquier momento puede aparecer a tu lado un creeper cargado de un solo corazón.", 5 * 60,
            SucesosLluvia.Creepers::new),
    /** DEDsafio 4, cualquier criatura en tu posicion sin previo aviso. */
    CUALQUIER_COSA("cualquier_cosa", Grupo.SUCESOS, "CUALQUIER COSA",
            "Durante cinco minutos, cualquier criatura puede aparecer a tu lado sin avisar.", 5 * 60,
            SucesosLluvia.Cualquiera::new),
    /** DEDsafio 4, la tormenta electrica con tornados. */
    TORNADOS("tornados", Grupo.SUCESOS, "TORNADOS",
            "Durante tres minutos, los tornados barren la superficie y lanzan por los aires a quien atrapan. Para escapar, una perla de ender.", 3 * 60,
            SucesosLluvia.Tornados::new),
    /** DEDsafio 4, el ataque de los Phora (el cielo naranja, la superficie en llamas). */
    EL_CIELO_ARDE("el_cielo_arde", Grupo.SUCESOS, "EL CIELO ARDE",
            "Un bombardeo va a arrasar la superficie. Tienes un minuto para meterte bajo tierra; después, durante minuto y medio, el cielo arde.",
            0, SucesosLluvia.CieloArde::new),
    /** DEDsafio 4, el intercambio de cuentas (cuatro jugadores se cambian el personaje). */
    CAMBIO_DE_CUERPOS("cambio_de_cuerpos", Grupo.SUCESOS, "CAMBIO DE CUERPOS",
            "Cuatro jugadores se cambian el cuerpo por parejas: el sitio, lo que llevan, la vida. Durante diez minutos, cada uno vive la del otro.", 10 * 60,
            SucesosLluvia.CambioDeCuerpos::new),
    /** DEDsafio 3, el apocalipsis zombi; DEDsafio 2, las hordas y la Death Raid. */
    LA_HORDA("la_horda", Grupo.SUCESOS, "LA HORDA",
            "Al llegar el contador a cero, tres oleadas de muertos vendrán a por vosotros. Preparaos y sobrevivid en grupo.",
            0, SucesosLluvia.Horda::new);

    /** Los grupos del menu, en su orden. */
    public enum Grupo {
        SALVO("PONTE A SALVO"),
        PRUEBAS("PRUEBAS"),
        MIENTRAS("MIENTRAS DURA"),
        SUCESOS("SUCESOS");

        public final String nombre;

        Grupo(String nombre) {
            this.nombre = nombre;
        }
    }

    private final String id;
    private final Grupo grupo;
    private final String titulo;
    private final String texto;
    /** Lo que dura despues del aviso (segundos); 0, hasta que se apague o acabe su contador. */
    public final int segundos;
    private final Supplier<Suceso> fabrica;

    Momento(String id, Grupo grupo, String titulo, String texto, int segundos, Supplier<Suceso> fabrica) {
        this.id = id;
        this.grupo = grupo;
        this.titulo = titulo;
        this.texto = texto;
        this.segundos = segundos;
        this.fabrica = fabrica;
    }

    /** Un Suceso nuevo para lanzarlo. */
    Suceso crear() {
        return fabrica.get();
    }

    @Override
    public String id() {
        return id;
    }

    @Override
    public String titulo() {
        return titulo;
    }

    @Override
    public String texto() {
        return texto;
    }

    @Override
    public Categoria categoria() {
        return Categoria.MOMENTO;
    }

    @Override
    public String grupo() {
        return grupo.nombre;
    }
}
