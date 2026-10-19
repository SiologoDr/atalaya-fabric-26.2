package com.atalaya.cambios;

import com.atalaya.catalogo.Categoria;
import com.atalaya.catalogo.Entrada;
import org.jspecify.annotations.Nullable;

/**
 * Los cambios de dificultad (17-10-2026): reglas que se quedan hasta que se apagan. Juan: "ahora haremos cambios de
 * dificultad, los quiero en un menu ... y ahi esten todos los cambios de dificultad"; de los de DEDsafio, "el titulo y
 * contenido cambialo para que no sea lo mismo"; y luego (18-10-2026) "vas a meter todo de la ficha de busqueda de
 * dedsafio con otro diseno, funcionalidad parecida pero con el mismo objetivo". Asi que la mecanica es la de alli y el
 * titulo y el texto, nuestros (en cada uno, de donde sale). Lo que dura un rato no esta aqui: es un momento
 * (com.atalaya.momento.Momento).
 *
 * Cada cambio se enciende desde el menu (/atalaya menu cambios): sale la Ruleta en su final de dificultad, con el
 * titulo del cambio como rotulo del chat y su texto debajo, y al salir el aviso se aplica (CambiosDificultad). Apagarlo
 * lo quita al momento, sin animacion. Lo que hace cada uno esta en ReglasCambios y en los mixins de cambios.
 */
public enum Cambio implements Entrada {

    // ------------------------------------------------------------------
    //  Al jugador
    // ------------------------------------------------------------------

    /** DEDsafio 3, «Pies debiles» (y la caida x2 del 4). */
    PIES_DE_CRISTAL("pies_de_cristal", Grupo.JUGADOR, "PIES DE CRISTAL",
            "El daño por caída se triplica. Cada escalón mal medido puede ser el último."),
    /** DEDsafio 3, «Hambruna». */
    ESTOMAGO_SIN_FONDO("estomago_sin_fondo", Grupo.JUGADOR, "ESTÓMAGO SIN FONDO",
            "La barra de hambre baja el doble de rápido."),
    /** DEDsafio 4, «Ahogarse». */
    PULMONES_DE_PAPEL("pulmones_de_papel", Grupo.JUGADOR, "PULMONES DE PAPEL",
            "Bajo el agua el aire se acaba cinco veces más rápido, y ahogarse hace diez veces más daño."),
    /** DEDsafio 3, el del primer dia (ni pociones, ni puertas, ni antorchas); y el 4, puertas y trampillas. */
    SIN_BOLSAS_DE_AIRE("sin_bolsas_de_aire", Grupo.JUGADOR, "SIN BOLSAS DE AIRE",
            "Las puertas, las trampillas y las antorchas ya no dan aire bajo el agua, y nada te deja respirar en ella."),
    /** DEDsafio 4, la regeneracion natural desactivada para siempre. */
    HERIDAS_ABIERTAS("heridas_abiertas", Grupo.JUGADOR, "HERIDAS ABIERTAS",
            "La vida ya no se regenera sola: solo vuelve con pociones, tótems y comida dorada."),
    /** DEDsafio 4, el fuego infinito del Nether y la armadura completa. */
    EL_NETHER_NO_PERDONA("el_nether_no_perdona", Grupo.JUGADOR, "EL NETHER NO PERDONA",
            "En el Nether, quien arde ya no se apaga, y quien no lleva las cuatro piezas de armadura se prende."),
    /** DEDsafio 4, fuego y lava x10 (y el «Infernus» y la «Lava mortal» del 3). */
    BRASAS_VORACES("brasas_voraces", Grupo.JUGADOR, "BRASAS VORACES",
            "El fuego y la lava hacen diez veces más daño."),
    /** DEDsafio 2, «El ser humano vs. el planeta». */
    EL_MUNDO_CONTRAATACA("el_mundo_contraataca", Grupo.JUGADOR, "EL MUNDO CONTRAATACA",
            "Todo el daño que no viene de un monstruo se triplica: caídas, fuego, asfixia, cactus..."),
    /** DEDsafio 3, «Venganza». */
    MAL_AGUERO("mal_aguero", Grupo.JUGADOR, "MAL AGÜERO",
            "Todos llevan el mal presagio para siempre: cada aldea que pisas trae su invasión."),
    /** DEDsafio 3 y 4, la zombificacion permanente («El ultimo de nosotros»). */
    LA_PLAGA("la_plaga", Grupo.JUGADOR, "LA PLAGA",
            "Todos llevan la plaga dentro: al llegar su cuenta a cero se cobra un tótem, o la vida. La Píldora la alarga."),
    /** DEDsafio 4, las pesadillas y el indicador de insomnio. */
    INSOMNIO("insomnio", Grupo.JUGADOR, "INSOMNIO",
            "Quien no duerme acumula insomnio, y con el insomnio alto bajan las pesadillas a buscarlo."),
    /** DEDsafio 4, «Mirar al Sol» (miopia y daltonismo). */
    NO_MIRES_AL_SOL("no_mires_al_sol", Grupo.JUGADOR, "NO MIRES AL SOL",
            "Quien mira al Sol se queda tres minutos con la vista nublada, sin colores y sin ver su vida."),
    /** DEDsafio 2, «Diminuto problema». */
    ENCOGIDOS("encogidos", Grupo.JUGADOR, "ENCOGIDOS",
            "Una maldición encoge a diez jugadores al azar hasta la mitad de su tamaño."),
    /** DEDsafio 2, el «sindrome del prota» (la idea de los tres corazones). */
    PROTAGONISTA("protagonista", Grupo.JUGADOR, "PROTAGONISTA",
            "Todos se quedan con tres corazones, pero sin hambre y con Fuerza III."),

    // ------------------------------------------------------------------
    //  Al mundo
    // ------------------------------------------------------------------

    /** DEDsafio 2, «Confinamiento dimensional». */
    END_SELLADO("end_sellado", Grupo.MUNDO, "EL END, SELLADO",
            "Los portales del End ya no llevan a ninguna parte: el End queda cerrado para siempre."),
    /** DEDsafio 2, «Las puertas al infierno». */
    PORTALES_ARDEN("portales_arden", Grupo.MUNDO, "LOS PORTALES ARDEN",
            "Los portales vuelven a encenderse: el Nether queda abierto."),
    /** DEDsafio 3, «Lava rapida». */
    LAVA_DESBOCADA("lava_desbocada", Grupo.MUNDO, "LAVA DESBOCADA",
            "La lava corre tan rápido y tan lejos como el agua."),
    /** DEDsafio 3, «Control de plagas», y 4, «Animales extintos». */
    EXTINCION("extincion", Grupo.MUNDO, "EXTINCIÓN",
            "Un gas se lleva a los animales que hay cerca y ya no vuelve a salir ninguno."),
    /** DEDsafio 3, «Radiacion» (los cultivos no crecen). */
    TIERRA_YERMA("tierra_yerma", Grupo.MUNDO, "TIERRA YERMA",
            "Los cultivos no crecen, los árboles no brotan y el polvo de hueso no hace nada."),
    /** DEDsafio 3, «Fiesta puntiaguda». */
    ESPINAS_MORTALES("espinas_mortales", Grupo.MUNDO, "ESPINAS MORTALES",
            "Rozar un cactus te hace un daño que ninguna armadura aguanta."),
    /** DEDsafio 3 y 4, los botones que matan. */
    NO_TOQUES_ESE_BOTON("no_toques_ese_boton", Grupo.MUNDO, "NO TOQUES ESE BOTÓN",
            "Pulsar un botón te mata."),
    /** DEDsafio 3, «Toc toc... quien es?», y 4: solo las puertas de hierro son de fiar. */
    PUERTAS_MALDITAS("puertas_malditas", Grupo.MUNDO, "PUERTAS MALDITAS",
            "Abrir una puerta de madera te mata. Solo las de hierro son de fiar."),
    /** DEDsafio 4, las placas de presion letales. */
    PLACAS_TRAMPA("placas_trampa", Grupo.MUNDO, "PLACAS TRAMPA",
            "Pisar una placa de presión te mata."),
    /** DEDsafio 4, el magma letal por cualquier cara. */
    PIEDRA_ARDIENTE("piedra_ardiente", Grupo.MUNDO, "PIEDRA ARDIENTE",
            "Tocar un bloque de magma, por cualquier lado, te mata."),
    /** DEDsafio 3, «Lava purificadora». */
    LAVA_SIN_TREGUA("lava_sin_tregua", Grupo.MUNDO, "LAVA SIN TREGUA",
            "Tocar la lava te quita la resistencia al fuego."),
    /** DEDsafio 4, «Sin brotes de arbol». */
    BOSQUES_SIN_FUTURO("bosques_sin_futuro", Grupo.MUNDO, "BOSQUES SIN FUTURO",
            "Las hojas ya no sueltan brotes: el árbol que talas no vuelve."),
    /** DEDsafio 4, «Vacas sin leche». */
    VACAS_SECAS("vacas_secas", Grupo.MUNDO, "VACAS SECAS",
            "Las vacas, las cabras y los champiñacas ya no dan leche."),
    /** DEDsafio 4, los panales que explotan y sin miel. */
    PANALES_TRAMPA("panales_trampa", Grupo.MUNDO, "PANALES TRAMPA",
            "Los panales y las colmenas estallan al romperlos, y ya no dan miel."),
    /** DEDsafio 4, el gas por encima de la capa 150. */
    TECHO_DE_GAS("techo_de_gas", Grupo.MUNDO, "TECHO DE GAS",
            "Por encima de la capa 150 el aire es veneno: hace daño hasta matar."),
    /** DEDsafio 4, el gas que baja a la capa 130. */
    EL_GAS_BAJA("el_gas_baja", Grupo.MUNDO, "EL GAS BAJA",
            "El gas venenoso baja hasta la capa 130."),
    /** DEDsafio 2, «Mobcap cambiada». */
    LA_NOCHE_SE_LLENA("la_noche_se_llena", Grupo.MUNDO, "LA NOCHE SE LLENA",
            "Caben el doble de monstruos: la oscuridad se llena."),
    /** DEDsafio 2, las estalactitas que caen de la mazmorra de las aranas. */
    TECHOS_QUE_CAEN("techos_que_caen", Grupo.MUNDO, "TECHOS QUE CAEN",
            "En las cuevas se desprenden estalactitas del techo sobre los que pasan por debajo."),
    /** DEDsafio 2, los generadores irrompibles. */
    SPAWNERS_ETERNOS("spawners_eternos", Grupo.MUNDO, "GENERADORES ETERNOS",
            "Los generadores de monstruos ya no se pueden romper."),
    /** DEDsafio 4, «Sin golems». */
    CALABAZAS_DORMIDAS("calabazas_dormidas", Grupo.MUNDO, "CALABAZAS DORMIDAS",
            "Las calabazas ya no cobran vida: no se pueden hacer gólems de hierro ni de nieve."),

    // ------------------------------------------------------------------
    //  Lo que sale al hacer algo
    // ------------------------------------------------------------------

    /** DEDsafio 3, «Fiebre aracnida», y 4, telaranas con arana. */
    NIDOS_OCULTOS("nidos_ocultos", Grupo.APARICIONES, "NIDOS OCULTOS",
            "Al romper una telaraña puede saltar una araña de cueva."),
    /** DEDsafio 3, «Alianza» (al tradear, una raid de brujas). */
    TRATOS_MALDITOS("tratos_malditos", Grupo.APARICIONES, "TRATOS MALDITOS",
            "Cada trato con un aldeano tiene un 20 % de traer un aquelarre de brujas."),
    /** DEDsafio 4, el «Momento Reviil permanente». */
    CADA_MUERTE_CUENTA("cada_muerte_cuenta", Grupo.APARICIONES, "CADA MUERTE CUENTA",
            "Cada vez que muere un jugador, aparece un creeper cargado de un corazón junto a cada uno de los vivos."),

    // ------------------------------------------------------------------
    //  A los mobs de siempre
    // ------------------------------------------------------------------

    /** DEDsafio 2, «Bienvenidos al 2012», y 3, «Terror triple». */
    GOLPES_TRIPLES("golpes_triples", Grupo.MOBS, "GOLPES TRIPLES",
            "Los monstruos de siempre hacen el triple de daño."),
    /** DEDsafio 2, «Del descuento a la inflacion». */
    PIEL_MAS_GRUESA("piel_mas_gruesa", Grupo.MOBS, "PIEL MÁS GRUESA",
            "Todos los mobs, sin excepción, aguantan un 10 % más."),
    /** DEDsafio 3, el Enderman x4. */
    LA_IRA_DEL_END("la_ira_del_end", Grupo.MOBS, "LA IRA DEL END",
            "Los endermen pegan cuatro veces más fuerte."),
    /** DEDsafio 4, Enderman y Endermite con 100 de dano. */
    CIEN_DE_UN_GOLPE("cien_de_un_golpe", Grupo.MOBS, "CIEN DE UN GOLPE",
            "Los endermen y los endermites hacen 100 de daño."),
    /** DEDsafio 4, las aranas con Velocidad I y Fuerza III y IV. */
    ARANAS_DE_GUERRA("aranas_de_guerra", Grupo.MOBS, "ARAÑAS DE GUERRA",
            "Todas las arañas llevan Velocidad I y Fuerza IV."),
    /** DEDsafio 3, «Fiebre tejedora», y 4, las aranas que dejan telarana. */
    TELARANA_EN_LOS_PIES("telarana_en_los_pies", Grupo.MOBS, "TELARAÑA EN LOS PIES",
            "Cada golpe de una araña te deja una telaraña a los pies, y al morir dejan otra."),
    /** DEDsafio 4, las aranas de cueva de noche en la superficie y en el hielo. */
    LAS_ARANAS_SUBEN("las_aranas_suben", Grupo.MOBS, "LAS ARAÑAS SUBEN",
            "Las arañas de cueva salen de noche a la superficie, y sobre el hielo con cualquier luz."),
    /** DEDsafio 4, los zombis trepadores con espada de Filo V e inmunes al sol. */
    ZOMBIS_TREPADORES("zombis_trepadores", Grupo.MOBS, "ZOMBIS TREPADORES",
            "Los zombis trepan paredes, no arden al sol y salen con espada de hierro con Filo V."),
    /** DEDsafio 3, «Zombis listos» y con totem; 4, los de pico de diamante y los de bajo la capa 40. */
    ZOMBIS_LISTOS("zombis_listos", Grupo.MOBS, "ZOMBIS LISTOS",
            "Los zombis pican y ponen bloques para llegar a ti, y salen armados, con perlas y, a veces, un tótem."),
    /** DEDsafio 3, «Infeccion» (los zombis contagian la zombificacion). */
    MORDISCO_PUTRIDO("mordisco_putrido", Grupo.MOBS, "MORDISCO PÚTRIDO",
            "El mordisco de un zombi contagia la plaga. Se cura con una poción de debilidad y una manzana de oro."),
    /** DEDsafio 3 y 4, los zombis en el Nether. */
    LOS_MUERTOS_BAJAN("los_muertos_bajan", Grupo.MOBS, "LOS MUERTOS BAJAN",
            "Los zombis aparecen también en el Nether, con cualquier luz."),
    /** DEDsafio 3, «Creeper mania», y 4, todos los creepers electricos. */
    CREEPERS_CARGADOS("creepers_cargados", Grupo.MOBS, "TORMENTA EN LOS CREEPERS",
            "Todos los creepers salen cargados, también de día. Solo un escudo salva de su explosión."),
    /** DEDsafio 2, «Y mi cartera?», y 3, «Adivinen quienes llegaron». */
    PHANTOMS_LADRONES("phantoms_ladrones", Grupo.MOBS, "PHANTOMS LADRONES",
            "Los phantoms, al golpearte, te arrancan algo del inventario o te lo revuelven, y te nublan la vista."),
    /** DEDsafio 4, los Warden naturales que dejan un chillon. */
    EL_ABISMO_DESPIERTA("el_abismo_despierta", Grupo.MOBS, "EL ABISMO DESPIERTA",
            "Los wardens salen solos en la oscuridad profunda, y al morir dejan un chillón de sculk."),
    /** DEDsafio 2, los wardens que suben de las profundidades. */
    WARDENS_EN_LA_SUPERFICIE("wardens_en_la_superficie", Grupo.MOBS, "WARDENS EN LA SUPERFICIE",
            "Los wardens suben a la superficie por la noche."),
    /** DEDsafio 3, «Atte: Reviil» (los golems de las aldeas, wardens). */
    ALDEAS_VIGILADAS("aldeas_vigiladas", Grupo.MOBS, "ALDEAS VIGILADAS",
            "Los gólems que defienden las aldeas ahora son wardens."),
    /** DEDsafio 3, «Feliz ano nuevo». */
    POLVORA_EN_LAS_BALLESTAS("polvora_en_las_ballestas", Grupo.MOBS, "PÓLVORA EN LAS BALLESTAS",
            "Los piglins y los saqueadores cargan sus ballestas con cohetes que estallan."),
    /** DEDsafio 3, «Fiebre del oro» (una ayuda). */
    PIGLINS_GENEROSOS("piglins_generosos", Grupo.MOBS, "PIGLINS GENEROSOS",
            "Los piglins sueltan pepitas de oro al morir."),
    /** DEDsafio 4, los blazes por todo el Nether. */
    BLAZES_SUELTOS("blazes_sueltos", Grupo.MOBS, "BLAZES SUELTOS",
            "Los blazes salen por todo el Nether, no solo en las fortalezas."),
    /** DEDsafio 4, los esqueletos wither en el Nether y de noche en el mundo. */
    HUESOS_NEGROS("huesos_negros", Grupo.MOBS, "HUESOS NEGROS",
            "Los esqueletos wither salen por todo el Nether, y de noche también en el mundo."),
    /** DEDsafio 4, los strays y los bogged de noche. */
    LA_NOCHE_HELADA("la_noche_helada", Grupo.MOBS, "LA NOCHE HELADA",
            "Los esqueletos glaciales y los cenagosos salen de noche en cualquier parte."),
    /** DEDsafio 4, los esqueletos en el Nether y en su techo. */
    ESQUELETOS_EN_EL_NETHER("esqueletos_en_el_nether", Grupo.MOBS, "ESQUELETOS EN EL NETHER",
            "Los esqueletos salen por todo el Nether con cualquier luz, también encima de su techo."),
    /** DEDsafio 4, «Olfato». */
    NARIZ_DE_SABUESO("nariz_de_sabueso", Grupo.MOBS, "NARIZ DE SABUESO",
            "Todos los mobs te encuentran aunque seas invisible."),

    // ------------------------------------------------------------------
    //  A los objetos y las curas
    // ------------------------------------------------------------------

    /** DEDsafio 2, «Solo se vive una vez». */
    NI_UN_TOTEM_MAS("ni_un_totem_mas", Grupo.OBJETOS, "NI UN TÓTEM MÁS",
            "Los evocadores ya no sueltan tótems de la inmortalidad. Los que tengas son los últimos."),
    /** DEDsafio 2, «Precipitacion de muerte» (los totems al 50 %). */
    CARA_O_CRUZ("cara_o_cruz", Grupo.OBJETOS, "CARA O CRUZ",
            "Los tótems de la inmortalidad solo funcionan la mitad de las veces."),
    /** DEDsafio 4, las perlas que hacen 10 de dano atravesando la armadura. */
    PERLAS_AFILADAS("perlas_afiladas", Grupo.OBJETOS, "PERLAS AFILADAS",
            "Cada perla de ender hace 10 de daño, y la armadura no lo para."),
    /** DEDsafio 3, «Ender pearlll» (media vida por perla). */
    SALTOS_CAROS("saltos_caros", Grupo.OBJETOS, "SALTOS CAROS",
            "Cada perla de ender te quita la mitad de la vida que te queda."),
    /** DEDsafio 3, «Enderpeeeearls» (solo en la misma dimension). */
    PERLAS_QUE_NO_CRUZAN("perlas_que_no_cruzan", Grupo.OBJETOS, "PERLAS QUE NO CRUZAN",
            "Una perla de ender solo te lleva si sigues en su misma dimensión."),
    /** DEDsafio 4, las manzanas de oro sin absorcion. */
    MANZANAS_VACIAS("manzanas_vacias", Grupo.OBJETOS, "MANZANAS VACÍAS",
            "Las manzanas de oro, también las encantadas, ya no dan absorción."),
    /** DEDsafio 4, la carne, el pollo y el pescado se pudren. */
    SE_PUDRE_LA_CARNE("se_pudre_la_carne", Grupo.OBJETOS, "SE PUDRE LA CARNE",
            "La carne, el pollo y el pescado se pudren a los veinte minutos de cogerlos."),
    /** DEDsafio 3, «Grindstone magico» (una ayuda). */
    PIEDRA_SABIA("piedra_sabia", Grupo.AYUDAS, "PIEDRA SABIA",
            "La piedra de afilar con un libro pasa los encantamientos de un objeto al libro, a cambio de niveles."),
    /** DEDsafio 3, la «Bolsa de Ender» (una ayuda). */
    BOLSA_DEL_VACIO("bolsa_del_vacio", Grupo.AYUDAS, "BOLSA DEL VACÍO",
            "Se puede fabricar una bolsa que abre tu cofre de ender desde cualquier sitio."),
    /** DEDsafio 3, el «Yunque dorado» (una ayuda). */
    YUNQUE_DORADO("yunque_dorado", Grupo.AYUDAS, "YUNQUE DORADO",
            "Se puede fabricar un yunque de oro de bolsillo que repara de golpe toda la armadura que llevas."),
    /** DEDsafio 3, la pocion de Keep Inventory, y 4, el Fruto de Quiu (una ayuda). */
    FRUTO_DEL_RECUERDO("fruto_del_recuerdo", Grupo.AYUDAS, "FRUTO DEL RECUERDO",
            "Se puede fabricar un fruto que, comido, te deja conservar el inventario la próxima vez que mueras."),
    /** DEDsafio 3, la «Rabanagua» (una ayuda). */
    RAIZ_DE_AGUA("raiz_de_agua", Grupo.AYUDAS, "RAÍZ DE AGUA",
            "Se puede fabricar una raíz que, comida, quita la fatiga minera.");

    /** Los grupos del menu, en su orden. */
    public enum Grupo {
        JUGADOR("AL JUGADOR"),
        MUNDO("AL MUNDO"),
        APARICIONES("LO QUE SALE AL HACER ALGO"),
        MOBS("A LOS MOBS DE SIEMPRE"),
        OBJETOS("A LOS OBJETOS"),
        AYUDAS("AYUDAS");

        public final String nombre;

        Grupo(String nombre) {
            this.nombre = nombre;
        }
    }

    /** Su nombre en el codigo, en las texturas y en lo que se guarda. */
    public final String id;
    public final Grupo grupo;
    /** El titulo (el del menu y el del rotulo del chat). */
    public final String titulo;
    /** Lo que dice el aviso del chat debajo del titulo (y el menu). */
    public final String texto;

    Cambio(String id, Grupo grupo, String titulo, String texto) {
        this.id = id;
        this.grupo = grupo;
        this.titulo = titulo;
        this.texto = texto;
    }

    public static @Nullable Cambio porId(String id) {
        for (Cambio c : values()) {
            if (c.id.equals(id)) {
                return c;
            }
        }
        return null;
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
        return Categoria.CAMBIO;
    }

    @Override
    public String grupo() {
        return grupo.nombre;
    }
}
