package com.atalaya.bestiario;

import com.atalaya.Atalaya;
import com.atalaya.bestiario.mobs.BombasVoladoras;
import com.atalaya.bestiario.mobs.AtomicoEntity;
import com.atalaya.bestiario.mobs.CiegoEntity;
import com.atalaya.bestiario.mobs.EnredaderaEntity;
import com.atalaya.bestiario.mobs.Fantasmas;
import com.atalaya.bestiario.mobs.GelatinaEntity;
import com.atalaya.bestiario.mobs.Hormigas;
import com.atalaya.bestiario.mobs.MarchitoEntity;
import com.atalaya.bestiario.mobs.MatojoEntity;
import com.atalaya.bestiario.mobs.Plantas;
import com.atalaya.bestiario.mobs.TartaEntity;
import net.fabricmc.fabric.api.biome.v1.BiomeSelectors;
import net.fabricmc.fabric.api.networking.v1.ServerPlayConnectionEvents;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.ResourceKey;
import net.minecraft.tags.BiomeTags;
import net.minecraft.world.entity.SpawnPlacementTypes;
import net.minecraft.world.level.biome.Biome;
import net.minecraft.world.level.biome.Biomes;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.levelgen.Heightmap;

/**
 * Las fichas de los mobs del bestiario, en el orden del menu de los mobs. Cada una se apunta en Bestias al cargar esta
 * clase (Bestias.registrar la carga antes de registrar nada). Lo de cada una: su titulo y lo que hace (el menu y el
 * aviso del chat: el titulo es tambien el de su rotulo), su caja, sus atributos, sus sonidos, sus particulas y donde
 * sale cuando esta suelto (sin biomas: sale de otra forma, que engancha su clase en registrarEventos).
 */
public final class Fichas {

    private Fichas() {
    }

    // ------------------------------------------------------------------
    //  Los creepers
    // ------------------------------------------------------------------

    /** El Creeper Matojo (DEDsafio 4, el Creeper de Pasto). */
    public static final Bestia MATOJO = Bestias.nueva("matojo", MatojoEntity::new)
            .grupo("CREEPERS")
            .titulo("CREEPER MATOJO", "Un creeper chico de hierba apelmazada: salta de los matojos al romperlos, corre como el viento y estalla en un suspiro.")
            .etiquetas("pasto hierba arbusto creeper")
            .medidas(0.45F, 0.8F, 0.6F)
            .atributos(MatojoEntity::atributos)
            .sonidos("mecha", "estalla", "aparece")
            .particula("brizna", Bestia.Vuelo.ESTALLA, false)
            .muerte(18, "brizna")
            .sombra(0.28F);

    /** El Creeper Marchito (DEDsafio, el Creeper de Wither Rose). */
    public static final Bestia MARCHITO = Bestias.nueva("marchito", MarchitoEntity::new)
            .grupo("CREEPERS")
            .titulo("CREEPER MARCHITO", "La rosa marchita hecha creeper: su estallido deja el Wither a todo lo que pilla cerca y siembra rosas marchitas alrededor. Sale en el Nether.")
            .etiquetas("wither rosa marchita flor nether creeper")
            .medidas(0.6F, 1.8F, -1.0F)
            .atributos(MarchitoEntity::atributos)
            .sonidos("mecha", "estalla")
            .particula("petalo", Bestia.Vuelo.DERIVA, false)
            .particula("ceniza", Bestia.Vuelo.DERIVA, false)
            .muerte(20, "petalo")
            .aparece(BiomeSelectors.includeByKey(Biomes.SOUL_SAND_VALLEY, Biomes.NETHER_WASTES), 25, 1, 2);

    /** El Creeper Enredadera (DEDsafio, el Creeper de Raiz de Azalea). */
    public static final Bestia ENREDADERA = Bestias.nueva("enredadera", EnredaderaEntity::new)
            .grupo("CREEPERS")
            .titulo("CREEPER ENREDADERA", "Te lanza sus lianas desde lejos y te arrastra hasta él con la mecha encendida: aporrea la tecla de saltar para soltarte. Bajo el agua, te ahoga. Sale de día y de noche en las llanuras y en las cuevas frondosas.")
            .etiquetas("lianas raiz azalea enredadera atrapa llanura cueva creeper")
            .medidas(0.6F, 1.8F, -1.0F)
            .atributos(EnredaderaEntity::atributos)
            .sonidos("mecha", "estalla", "latigo", "atrapa", "suelta")
            .particula("hoja", Bestia.Vuelo.CAE, false)
            .particula("flor", Bestia.Vuelo.DERIVA, false)
            .muerte(20, "hoja")
            .aparece(BiomeSelectors.includeByKey(Biomes.PLAINS, Biomes.SUNFLOWER_PLAINS, Biomes.MEADOW, Biomes.FLOWER_FOREST,
                    Biomes.LUSH_CAVES), 30, 1, 1)
            .regla(Bestia.Regla.SIEMPRE);

    /** El Creeper Gelatina (DEDsafio, el Creeper de Fluido). */
    public static final Bestia GELATINA = Bestias.nueva("gelatina", GelatinaEntity::new)
            .grupo("CREEPERS")
            .titulo("CREEPER GELATINA", "De gel translúcido: trepa por las paredes y su estallido te deja sin señal ocho segundos, sin ver nada y sin fuerzas. Sale en los pantanos.")
            .etiquetas("gel gelatina fluido slime trepa pantano señal creeper")
            .medidas(0.65F, 1.85F, -1.0F)
            .atributos(GelatinaEntity::atributos)
            .sonidos("mecha", "estalla", "estatica")
            .particula("burbuja", Bestia.Vuelo.SUBE, false)
            .particula("gota", Bestia.Vuelo.CAE, false)
            .muerte(20, "gota")
            .aparece(BiomeSelectors.includeByKey(Biomes.SWAMP, Biomes.MANGROVE_SWAMP), 40, 1, 2);

    /** El Creeper Atomico (DEDsafio, el Creeper Nuclear). */
    public static final Bestia ATOMICO = Bestias.nueva("atomico", AtomicoEntity::new)
            .grupo("CREEPERS")
            .titulo("CREEPER ATÓMICO", "Su mecha es una sirena de tres segundos y su estallido arrasa: un cráter enorme, un destello que ciega y una onda que llega a cuarenta bloques con lluvia radiactiva. Solo te salva un escudo, y se rompe. Sale en la nieve y en el techo del Nether.")
            .etiquetas("nuclear atomico bomba radiacion sirena nieve nether creeper")
            .medidas(0.8F, 2.2F, -1.0F)
            .rastreo(10)
            .atributos(AtomicoEntity::atributos)
            .sonidos("mecha", "estalla", "onda")
            .particula("radiacion", Bestia.Vuelo.SUBE, true)
            .particula("chapa", Bestia.Vuelo.CAE, false)
            .muerte(20, "chapa")
            .sombra(0.7F)
            .aparece(BiomeSelectors.includeByKey(Biomes.SNOWY_PLAINS, Biomes.ICE_SPIKES, Biomes.SNOWY_TAIGA,
                    Biomes.SNOWY_SLOPES, Biomes.FROZEN_PEAKS, Biomes.GROVE, Biomes.SNOWY_BEACH, Biomes.FROZEN_RIVER), 6, 1, 1);

    /** El Creeper Ciego (DEDsafio, el Creeper Warden). */
    public static final Bestia CIEGO = Bestias.nueva("ciego", CiegoEntity::new)
            .grupo("CREEPERS")
            .titulo("CREEPER CIEGO", "De sculk y sin ojos: no te ve, te oye. Correr se oye de lejos; agáchate y quédate quieto y se perderá. Su estallido deja la oscuridad. Sale en la Oscuridad Profunda.")
            .etiquetas("sculk warden ciego oido ruido oscuridad profunda creeper")
            .medidas(0.6F, 1.8F, -1.0F)
            .atributos(CiegoEntity::atributos)
            .sonidos("mecha", "estalla", "escucha", "chillido")
            .particula("vibracion", Bestia.Vuelo.DERIVA, true)
            .particula("sculk", Bestia.Vuelo.CAE, false)
            .muerte(20, "sculk")
            .aparece(BiomeSelectors.includeByKey(Biomes.DEEP_DARK), 60, 1, 2);

    /** El Creeper Tarta (DEDsafio, el Creeper Cake). */
    public static final Bestia TARTA = Bestias.nueva("tarta", TartaEntity::new)
            .grupo("CREEPERS")
            .titulo("CREEPER TARTA", "Un creeper con la cabeza de tarta, rapidísimo: su mecha dura un suspiro y te pringa la pantalla de nata. Sale por los caminos de tierra y salta de las mesas de crafteo.")
            .etiquetas("tarta pastel cake nata camino mesa crafteo creeper")
            .medidas(0.6F, 1.8F, -1.0F)
            .atributos(TartaEntity::atributos)
            .sonidos("mecha", "estalla", "aparece", "pringue")
            .particula("nata", Bestia.Vuelo.CAE, false)
            .particula("miga", Bestia.Vuelo.CAE, false)
            .muerte(20, "miga")
            .sombra(0.5F)
            .aparece(BiomeSelectors.foundInOverworld(), 25, 1, 1)
            .regla(Bestia.Regla.SIEMPRE.y(TartaEntity::puedeSalir));

    // ------------------------------------------------------------------
    //  Las bombas voladoras
    // ------------------------------------------------------------------

    /** La Bomba Ambar (DEDsafio 3, la bomba amarilla). */
    public static final Bestia AMBAR = Bestias.nueva("ambar", BombasVoladoras.Ambar::new)
            .grupo("BOMBAS")
            .titulo("BOMBA ÁMBAR", "Un cubo de ámbar con la mecha encendida y alas de pluma doradas: te ve desde treinta bloques, se te pone encima y revienta; su estallido seca el agua de alrededor. Sale de noche, también en el aire y bajo tierra.")
            .etiquetas("bomba amarilla ambar voladora agua seca")
            .medidas(0.75F, 0.9F, 0.5F)
            .atributos(BombasVoladoras.Ambar::atributos)
            .sonidos("mecha", "estalla")
            .sinSonido("paso")
            .particula("vapor", Bestia.Vuelo.FLOTA, false)
            .particula("chispa", Bestia.Vuelo.DERIVA, true)
            .particula("cristal", Bestia.Vuelo.CAE, false)
            .muerte(20, "cristal")
            .sombra(0.3F)
            .aparece(BiomeSelectors.foundInOverworld(), 15, 1, 2)
            .colocacion(SpawnPlacementTypes.NO_RESTRICTIONS, Heightmap.Types.MOTION_BLOCKING_NO_LEAVES)
            .regla(BombasVoladoras.Ambar::enLaOscuridad);

    /** La Bomba Carmesi (DEDsafio 3, la bomba roja). */
    public static final Bestia CARMESI = Bestias.nueva("carmesi", BombasVoladoras.Carmesi::new)
            .grupo("BOMBAS")
            .titulo("BOMBA CARMESÍ", "Un cubo de chapa lacada roja con la mecha encendida y alas de murciélago, la más rápida de las bombas: se te pone encima y revienta prendiéndolo todo. Sale de noche y en el Nether.")
            .etiquetas("bomba roja carmesi voladora fuego nether")
            .medidas(0.7F, 0.85F, 0.5F)
            .atributos(BombasVoladoras.Carmesi::atributos)
            .sonidos("mecha", "estalla")
            .sinSonido("paso")
            .particula("brasa", Bestia.Vuelo.SUBE, true)
            .particula("esquirla", Bestia.Vuelo.CAE, false)
            .muerte(20, "esquirla")
            .sombra(0.3F)
            .aparece(BiomeSelectors.foundInOverworld().or(BiomeSelectors.foundInTheNether()), 10, 1, 2)
            .colocacion(SpawnPlacementTypes.NO_RESTRICTIONS, Heightmap.Types.MOTION_BLOCKING_NO_LEAVES)
            .regla(BombasVoladoras.Carmesi::enLaOscuridad);

    /** La Bomba Negra (DEDsafio 3 y 4). */
    public static final Bestia NEGRA = Bestias.nueva("negra", BombasVoladoras.Negra::new)
            .grupo("BOMBAS")
            .titulo("BOMBA NEGRA", "Un cubo de hierro negro en placas, con la mecha encendida y alas de cuervo, la más grande: no hay forma de empujarla y su estallido es el más fuerte. Sale de noche al aire libre.")
            .etiquetas("bomba negra hierro voladora murcielago fuerte")
            .medidas(0.95F, 1.1F, 0.6F)
            .atributos(BombasVoladoras.Negra::atributos)
            .sonidos("mecha", "estalla")
            .sinSonido("paso")
            .particula("humo", Bestia.Vuelo.FLOTA, false)
            .particula("esquirla", Bestia.Vuelo.CAE, false)
            .muerte(20, "esquirla")
            .sombra(0.45F)
            .aparece(BiomeSelectors.foundInOverworld(), 8, 1, 1)
            .colocacion(SpawnPlacementTypes.NO_RESTRICTIONS, Heightmap.Types.MOTION_BLOCKING_NO_LEAVES)
            .regla(((Bestia.Regla) BombasVoladoras.Negra::enLaOscuridad).y(BombasVoladoras.Negra::alAireLibre));

    /** La Bomba del Abismo (DEDsafio 4, las Bombas Warden Voladoras). */
    public static final Bestia ABISMO = Bestias.nueva("abismo", BombasVoladoras.Abismo::new)
            .grupo("BOMBAS")
            .titulo("BOMBA DEL ABISMO", "Un cubo de sculk con la mecha detrás y alas de sculk con las venas encendidas: no te ve, te oye, y en cuanto te oye va a por ti; su estallido deja la oscuridad. Sale en la Oscuridad Profunda.")
            .etiquetas("bomba warden sculk abismo voladora ciega oido oscuridad")
            .medidas(0.75F, 0.9F, 0.5F)
            .atributos(BombasVoladoras.Abismo::atributos)
            .sonidos("mecha", "estalla")
            .sinSonido("paso")
            .particula("alma", Bestia.Vuelo.SUBE, true)
            .particula("sculk", Bestia.Vuelo.CAE, false)
            .muerte(20, "sculk")
            .sombra(0.3F)
            .aparece(BiomeSelectors.includeByKey(Biomes.DEEP_DARK), 25, 1, 2)
            .colocacion(SpawnPlacementTypes.NO_RESTRICTIONS, Heightmap.Types.MOTION_BLOCKING_NO_LEAVES)
            .regla(BombasVoladoras.Abismo::enLaOscuridad);

    // ------------------------------------------------------------------
    //  Las hormigas
    // ------------------------------------------------------------------

    /** La Hormiga Lancera (DEDsafio 2, Cantimplo). */
    public static final Bestia LANCERA = Bestias.nueva("lancera", Hormigas.Lancera::new)
            .grupo("HORMIGAS")
            .titulo("HORMIGA LANCERA", "La soldado del hormiguero, erguida sobre cuatro patas: parda, con la cúpula de una bellota por casco y una lanza de pedernal en la mano; va en grupo y pega fuerte desde más lejos que las demás. Sale por todas partes, también en las cuevas y en el Nether.")
            .etiquetas("hormiga lancera soldado lanza grupo")
            .medidas(0.9F, 1.5F, 1.3F)
            .atributos(Hormigas.Lancera::atributos)
            .sonidos("mordisco")
            .particula("astilla", Bestia.Vuelo.CAE, false)
            .muerte(20, "astilla")
            .sombra(0.5F)
            .aparece(BiomeSelectors.foundInOverworld().or(BiomeSelectors.foundInTheNether()), 24, 2, 4);

    /** La Hormiga Polvorin (DEDsafio 2, Bombermant). */
    public static final Bestia POLVORIN = Bestias.nueva("polvorin", Hormigas.Polvorin::new)
            .grupo("HORMIGAS")
            .titulo("HORMIGA POLVORÍN", "Lleva en alto, con los dos brazos, una bomba de barro con la mecha encendida: cuando te tiene cerca, revienta, y todo el que esté a quince bloques se queda alucinando diez segundos.")
            .etiquetas("hormiga polvorin bomba explota alucinacion")
            .medidas(0.9F, 1.5F, 1.3F)
            .atributos(Hormigas.Polvorin::atributos)
            .sonidos("mordisco", "mecha", "estalla")
            .particula("chispa", Bestia.Vuelo.DERIVA, true)
            .particula("barro", Bestia.Vuelo.CAE, false)
            .particula("humo", Bestia.Vuelo.FLOTA, false)
            .muerte(20, "barro")
            .sombra(0.5F)
            .aparece(BiomeSelectors.foundInOverworld().or(BiomeSelectors.foundInTheNether()), 10, 1, 2);

    /** La Hormiga Cabezona (DEDsafio 2, Parapona). */
    public static final Bestia CABEZONA = Bestias.nueva("cabezona", Hormigas.Cabezona::new)
            .grupo("HORMIGAS")
            .titulo("HORMIGA CABEZONA", "Una cabeza ámbar enorme con mandíbulas de tenaza: su mordisco te deja lentísimo cinco segundos (y las demás te alcanzan).")
            .etiquetas("hormiga cabezona mandibula lentitud grupo")
            .medidas(1.0F, 1.5F, 1.3F)
            .atributos(Hormigas.Cabezona::atributos)
            .sonidos("mordisco")
            .particula("astilla", Bestia.Vuelo.CAE, false)
            .muerte(20, "astilla")
            .sombra(0.55F)
            .aparece(BiomeSelectors.foundInOverworld().or(BiomeSelectors.foundInTheNether()), 18, 1, 3);

    /** La Hormiga Radiactiva (DEDsafio 2, Compona). */
    public static final Bestia RADIACTIVA = Bestias.nueva("radiactiva", Hormigas.Radiactiva::new)
            .grupo("HORMIGAS")
            .titulo("HORMIGA RADIACTIVA", "Negra como el carbón, con los ojos y el gáster hinchado brillando de verde entre las placas: su mordisco te deja radiación cinco segundos.")
            .etiquetas("hormiga radiactiva negra radiacion verde")
            .medidas(0.9F, 1.5F, 1.3F)
            .atributos(Hormigas.Radiactiva::atributos)
            .sonidos("mordisco")
            .particula("radiacion", Bestia.Vuelo.SUBE, true)
            .muerte(20, "radiacion")
            .sombra(0.5F)
            .aparece(BiomeSelectors.foundInOverworld().or(BiomeSelectors.foundInTheNether()), 14, 1, 3);

    /** La Hormiga Brasa (DEDsafio 2, Solvetus). */
    public static final Bestia BRASA = Bestias.nueva("brasa", Hormigas.Brasa::new)
            .grupo("HORMIGAS")
            .titulo("HORMIGA BRASA", "Roja como el carbón encendido, con grietas de brasa y una tea en la mano: si te muerde o la tocas, te prende un fuego que no se apaga hasta que te metes en el agua o te llueve encima.")
            .etiquetas("hormiga brasa roja fuego quema agua nether")
            .medidas(0.9F, 1.5F, 1.3F)
            .inmuneFuego()
            .atributos(Hormigas.Brasa::atributos)
            .sonidos("mordisco", "quema")
            .particula("brasa", Bestia.Vuelo.SUBE, true)
            .muerte(20, "brasa")
            .sombra(0.5F)
            .aparece(BiomeSelectors.foundInOverworld().or(BiomeSelectors.foundInTheNether()), 14, 1, 3);

    // ------------------------------------------------------------------
    //  Las plantas
    // ------------------------------------------------------------------

    /** Lo que crece en la hierba (la Trampa Verde): solo sobre un bloque de hierba. */
    private static final Bestia.Regla EN_HIERBA = (tipo, nivel, motivo, pos, azar) ->
            nivel.getBlockState(pos.below()).is(Blocks.GRASS_BLOCK);

    /** La Fauces Verde (DEDsafio 2, Carnivenus verde). */
    public static final Bestia FAUCES_VERDE = Bestias.nueva("fauces_verde", Plantas.FaucesVerde::new)
            .grupo("PLANTAS")
            .titulo("FAUCES VERDE", "Una planta carnívora plantada en el suelo: no se mueve, pero te sigue con la cabeza y, si te acercas a menos de tres bloques, se echa atrás y te muerde. Su mordisco te envenena (veneno II, cinco segundos). Crece en selvas, bosques y pantanos.")
            .etiquetas("fauces planta carnivora verde veneno mordisco plantada")
            .medidas(1.1F, 1.85F, 1.55F)
            .atributos(Plantas.FaucesVerde::atributos)
            .sonidos("mordisco", "acido")
            .sinSonido("paso")
            .particula("savia", Bestia.Vuelo.CAE, true)
            .particula("hoja", Bestia.Vuelo.DERIVA, false)
            .muerte(20, "hoja")
            .sombra(0.5F)
            .regla(Bestia.Regla.SIEMPRE)
            .aparece(BiomeSelectors.tag(BiomeTags.IS_JUNGLE).or(BiomeSelectors.tag(BiomeTags.IS_FOREST))
                    .or(BiomeSelectors.includeByKey(Biomes.SWAMP, Biomes.MANGROVE_SWAMP)), 12, 1, 2);

    /** La Fauces Carmin (DEDsafio 2, Carnivenus roja). */
    public static final Bestia FAUCES_CARMIN = Bestias.nueva("fauces_carmin", Plantas.FaucesCarmin::new)
            .grupo("PLANTAS")
            .titulo("FAUCES CARMÍN", "La Fauces del Nether: roja por dentro, con espinas en el tallo y el fuego no le hace nada. Si te acercas, te muerde y te prende fuego cinco segundos.")
            .etiquetas("fauces planta carnivora roja carmin fuego quema nether mordisco plantada")
            .medidas(1.1F, 1.85F, 1.55F)
            .inmuneFuego()
            .atributos(Plantas.FaucesCarmin::atributos)
            .sonidos("mordisco", "quema")
            .sinSonido("paso")
            .particula("savia", Bestia.Vuelo.SUBE, true)
            .particula("hoja", Bestia.Vuelo.DERIVA, false)
            .muerte(20, "hoja")
            .sombra(0.5F)
            .regla(Bestia.Regla.SIEMPRE)
            .aparece(BiomeSelectors.foundInTheNether(), 10, 1, 2);

    /** La Fauces de Escarcha (DEDsafio 2, Carnivenus azul). */
    public static final Bestia FAUCES_ESCARCHA = Bestias.nueva("fauces_escarcha", Plantas.FaucesEscarcha::new)
            .grupo("PLANTAS")
            .titulo("FAUCES DE ESCARCHA", "La Fauces de la nieve, con carámbanos y dientes de hielo: su mordisco te deja congelado cinco segundos (sin poder moverte, con la escarcha cubriéndote la vista) y envenenado dos.")
            .etiquetas("fauces planta carnivora azul escarcha hielo congela nieve mordisco plantada")
            .medidas(1.1F, 1.85F, 1.55F)
            .atributos(Plantas.FaucesEscarcha::atributos)
            .sonidos("mordisco", "hiela")
            .sinSonido("paso")
            .particula("savia", Bestia.Vuelo.DERIVA, false)
            .particula("hoja", Bestia.Vuelo.DERIVA, false)
            .particula("escarcha", Bestia.Vuelo.DERIVA, true)
            .muerte(20, "escarcha")
            .sombra(0.5F)
            .regla(Bestia.Regla.SIEMPRE)
            .aparece(BiomeSelectors.tag(BiomeTags.SPAWNS_SNOW_FOXES), 12, 1, 2);

    /** La Trampa Verde (DEDsafio 2, Tramplanta). */
    public static final Bestia TRAMPA = Bestias.nueva("trampa", Plantas.Trampa::new)
            .grupo("PLANTAS")
            .titulo("TRAMPA VERDE", "Escondida en la hierba (casi no se ve: solo un flequillo de pestañas claras): si la pisas, se cierra de golpe y te tiene tres segundos enraizado y envenenado. Luego se abre y se vuelve a esconder.")
            .etiquetas("trampa planta escondida hierba pisar atrapa enraizado veneno")
            .medidas(1.2F, 0.35F, 0.2F)
            .atributos(Plantas.Trampa::atributos)
            .sonidos("cierra", "mastica", "abre")
            .sinSonido("paso")
            .particula("hoja", Bestia.Vuelo.DERIVA, false)
            .particula("pestana", Bestia.Vuelo.CAE, false)
            .muerte(20, "hoja")
            .sombra(0.0F)
            .regla(Bestia.Regla.SIEMPRE.y(EN_HIERBA))
            .aparece(BiomeSelectors.includeByKey(Biomes.PLAINS, Biomes.SUNFLOWER_PLAINS, Biomes.MEADOW, Biomes.FLOWER_FOREST)
                    .or(BiomeSelectors.tag(BiomeTags.IS_FOREST)).or(BiomeSelectors.tag(BiomeTags.IS_SAVANNA)), 14, 1, 3);

    /** La Pina Brava (DEDsafio 2, Pina Malibu). */
    public static final Bestia PINA = Bestias.nueva("pina", Plantas.Pina::new)
            .grupo("PLANTAS")
            .titulo("PIÑA BRAVA", "Una piña chica, con patas, puños de hoja y muy mala leche: corre detrás de ti y te da puñetazos sin parar (uno cada ocho ticks, y todos cuentan). Sale en selvas, playas y sabanas.")
            .etiquetas("pina piña fruta rapida punetazos tropical playa")
            .medidas(0.6F, 1.0F, 0.75F)
            .atributos(Plantas.Pina::atributos)
            .sonidos("puno")
            .particula("jugo", Bestia.Vuelo.CAE, false)
            .particula("hoja", Bestia.Vuelo.DERIVA, false)
            .muerte(20, "jugo")
            .sombra(0.4F)
            .aparece(BiomeSelectors.tag(BiomeTags.IS_JUNGLE).or(BiomeSelectors.tag(BiomeTags.IS_BEACH))
                    .or(BiomeSelectors.tag(BiomeTags.IS_SAVANNA)), 14, 1, 3);

    /** El Zombi Planta (DEDsafio 4, Zombie Planta). */
    public static final Bestia ZOMBI_PLANTA = Bestias.nueva("zombi_planta", Plantas.ZombiPlanta::new)
            .grupo("PLANTAS")
            .titulo("ZOMBI PLANTA", "Un zombi al que se ha comido la planta: musgo, hiedra, una flor en el ojo y un arbolito a la espalda. Cada golpe suyo te clava al suelo (un segundo sin moverte y luego muy lento). Al sol no arde: florece y se cura.")
            .etiquetas("zombi zombie planta flores enraizado raices sol cura")
            .medidas(0.6F, 1.95F, 1.74F)
            .atributos(Plantas.ZombiPlanta::atributos)
            .sonidos("enraiza", "florece")
            .particula("polen", Bestia.Vuelo.SUBE, true)
            .particula("hoja", Bestia.Vuelo.DERIVA, false)
            .particula("raiz", Bestia.Vuelo.CAE, false)
            .muerte(20, "hoja")
            .sombra(0.5F)
            .aparece(BiomeSelectors.foundInOverworld(), 18, 1, 2);

    // ------------------------------------------------------------------
    //  Los fantasmas
    // ------------------------------------------------------------------

    /** El bioma del Limbo (la dimension del laberinto). */
    private static final ResourceKey<Biome> LIMBO = ResourceKey.create(Registries.BIOME,
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "limbo"));

    /** El Espectro Blanco (DEDsafio 4, el Fantasma Blanco; y los fantasmas blancos del 3). */
    public static final Bestia ESPECTRO_BLANCO = Bestias.nueva("espectro_blanco", Fantasmas.Blanco::new)
            .grupo("FANTASMAS")
            .titulo("ESPECTRO BLANCO", "El fantasma de la máscara triste: vuela, te da zarpazos rapidísimos (uno cada ocho ticks) y cada zarpazo te deja con Lentitud. Sale de noche por todas partes, también en el Nether y en el Limbo.")
            .etiquetas("fantasma espectro blanco rapido lentitud vuela limbo")
            .medidas(0.8F, 1.7F, 1.3F)
            .atributos(Fantasmas.Blanco::atributos)
            .sonidos("zarpazo")
            .sinSonido("paso")
            .particula("alma", Bestia.Vuelo.FLOTA, false)
            .particula("escarcha", Bestia.Vuelo.DERIVA, true)
            .muerte(20, "alma")
            .sombra(0.4F)
            .aparece(BiomeSelectors.foundInOverworld().or(BiomeSelectors.foundInTheNether())
                    .or(BiomeSelectors.includeByKey(LIMBO)), 10, 1, 2)
            .colocacion(SpawnPlacementTypes.NO_RESTRICTIONS, Heightmap.Types.MOTION_BLOCKING_NO_LEAVES)
            .regla(BombaBestia::enLaOscuridad);

    /** El Espectro Negro (DEDsafio 4, el Fantasma Negro). */
    public static final Bestia ESPECTRO_NEGRO = Bestias.nueva("espectro_negro", Fantasmas.Negro::new)
            .grupo("FANTASMAS")
            .titulo("ESPECTRO NEGRO", "El fantasma del Limbo que roba corazones: cada golpe suyo te quita un corazón para siempre (aunque mueras). Al morir suelta un Corazón Blanco por cada corazón que robó: comiéndolo, recuperas uno.")
            .etiquetas("fantasma espectro negro corazon roba vida limbo vuela")
            .medidas(0.8F, 1.7F, 1.3F)
            .atributos(Fantasmas.Negro::atributos)
            .sonidos("zarpazo", "roba")
            .sinSonido("paso")
            .particula("humo", Bestia.Vuelo.FLOTA, false)
            .particula("corazon", Bestia.Vuelo.SUBE, true)
            .muerte(20, "humo")
            .sombra(0.4F)
            .aparece(BiomeSelectors.includeByKey(LIMBO), 8, 1, 1)
            .colocacion(SpawnPlacementTypes.NO_RESTRICTIONS, Heightmap.Types.MOTION_BLOCKING_NO_LEAVES)
            .regla(BombaBestia::enLaOscuridad);

    /** El Espectro Amarillo (DEDsafio 4, el Fantasma Amarillo). */
    public static final Bestia ESPECTRO_AMARILLO = Bestias.nueva("espectro_amarillo", Fantasmas.Amarillo::new)
            .grupo("FANTASMAS")
            .titulo("ESPECTRO AMARILLO", "El fantasma del Limbo que se te mete dentro: su golpe te hace gastar el tótem que lleves en la mano; luego se te mete en el cuerpo y, a los cinco segundos, sale a por otro jugador de cerca.")
            .etiquetas("fantasma espectro amarillo totem posee cuerpo limbo vuela")
            .medidas(0.8F, 1.7F, 1.3F)
            .atributos(Fantasmas.Amarillo::atributos)
            .sonidos("zarpazo", "posee", "sale")
            .sinSonido("paso")
            .particula("chispa", Bestia.Vuelo.DERIVA, true)
            .particula("alma", Bestia.Vuelo.FLOTA, false)
            .muerte(20, "alma")
            .sombra(0.4F)
            .aparece(BiomeSelectors.includeByKey(LIMBO), 8, 1, 1)
            .colocacion(SpawnPlacementTypes.NO_RESTRICTIONS, Heightmap.Types.MOTION_BLOCKING_NO_LEAVES)
            .regla(BombaBestia::enLaOscuridad);

    /** El Espectro Rojo (DEDsafio 3, los fantas rojos; y el Fantasma Rojo del 4). */
    public static final Bestia ESPECTRO_ROJO = Bestias.nueva("espectro_rojo", Fantasmas.Rojo::new)
            .grupo("FANTASMAS")
            .titulo("ESPECTRO ROJO", "El fantasma que te agarra y no te suelta: te deja clavado donde estás y te sigue pegando hasta que muere él o mueres tú, tótem tras tótem. Sale de noche por todas partes, también en el Nether y en el Limbo.")
            .etiquetas("fantasma espectro rojo agarra sujeta totems limbo vuela")
            .medidas(0.8F, 1.7F, 1.3F)
            .atributos(Fantasmas.Rojo::atributos)
            .sonidos("zarpazo", "agarra")
            .sinSonido("paso")
            .particula("brasa", Bestia.Vuelo.SUBE, true)
            .particula("ceniza", Bestia.Vuelo.DERIVA, false)
            .muerte(20, "ceniza")
            .sombra(0.4F)
            .aparece(BiomeSelectors.foundInOverworld().or(BiomeSelectors.foundInTheNether())
                    .or(BiomeSelectors.includeByKey(LIMBO)), 10, 1, 2)
            .colocacion(SpawnPlacementTypes.NO_RESTRICTIONS, Heightmap.Types.MOTION_BLOCKING_NO_LEAVES)
            .regla(BombaBestia::enLaOscuridad);

    /** Carga la clase (y con ella todas las fichas) y lo que van a necesitar: las lianas, la red y los corazones. */
    static void cargar() {
        Atrapado.registrar();
        BestiaRed.registrar();
        CorazonesRobados.registrar();
    }

    /** Lo que hace salir a cada uno (sus eventos): despues de registrar los tipos. */
    static void eventos() {
        MatojoEntity.registrarEventos();
        AtomicoEntity.registrarEventos();
        TartaEntity.registrarEventos();
        Hormigas.registrarEventos();
        CorazonesRobados.registrarEventos();
        ServerPlayConnectionEvents.JOIN.register((manejador, emisor, servidor) -> EnredaderaEntity.alEntrar(manejador.player));
    }
}
