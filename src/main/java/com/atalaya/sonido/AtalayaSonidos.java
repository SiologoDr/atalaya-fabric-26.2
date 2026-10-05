package com.atalaya.sonido;

import com.atalaya.Atalaya;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.Identifier;
import net.minecraft.sounds.SoundEvent;

/**
 * Sonidos propios del mod.
 *
 * Ninguno es de vanilla: los .ogg salen de scripts de sintesis que construyen
 * cada uno con lo que el bicho tiene encima. Los del Vigia, con el hierro del
 * farol, el cristal, las cadenas, una garganta y la llama; los de Nerea
 * (nerea_sonidos.py), con agua, piedra, hueso, cadenas y una voz sumergida; los de
 * Aeralis (aeralis_sonidos.py), con viento, alas, quitina, tornados y truenos.
 *
 * Aqui solo se registra el NOMBRE de cada evento. Que fichero suena, con que
 * variantes y con que subtitulo lo dice assets/atalaya/sounds.json.
 */
public final class AtalayaSonidos {

    public static SoundEvent VIGIA_AMBIENTE;
    public static SoundEvent VIGIA_ACECHO;
    public static SoundEvent VIGIA_PASO;
    public static SoundEvent VIGIA_HERIDO;
    public static SoundEvent VIGIA_MUERTE;
    public static SoundEvent VIGIA_APAGARSE;
    public static SoundEvent VIGIA_FAROL_CAE;
    public static SoundEvent VIGIA_ALERTA;
    public static SoundEvent VIGIA_CEPO_ABRIR;
    public static SoundEvent VIGIA_CEPO_CERRAR;
    public static SoundEvent VIGIA_CEPO_FALLO;
    public static SoundEvent VIGIA_MIRADA_CARGA;
    public static SoundEvent VIGIA_MIRADA_DISPARO;
    public static SoundEvent VIGIA_MIRADA_CORTE;
    public static SoundEvent VIGIA_RAYO_VUELO;
    public static SoundEvent VIGIA_RAYO_IMPACTO;
    public static SoundEvent VIGIA_TAMBALEO;
    public static SoundEvent VIGIA_BUSCAR;
    public static SoundEvent OJO_VIGIA_USAR;

    // --- Nerea: agua, piedra, hueso, cadenas y una voz bajo el agua ---
    public static SoundEvent NEREA_AMBIENTE;
    public static SoundEvent NEREA_PASO;
    public static SoundEvent NEREA_INMUNE;
    public static SoundEvent NEREA_HERIDO;
    public static SoundEvent NEREA_RUGIDO;
    public static SoundEvent NEREA_DESPERTAR;
    public static SoundEvent NEREA_ROMPEOLAS_ALZAR;
    public static SoundEvent NEREA_ROMPEOLAS_GOLPE;
    public static SoundEvent NEREA_OLA;
    public static SoundEvent NEREA_REMOLINO_AVISO;
    public static SoundEvent NEREA_REMOLINO;
    public static SoundEvent NEREA_ANTORCHA;
    public static SoundEvent NEREA_BURBUJAS;
    public static SoundEvent NEREA_BURBUJA_REVIENTA;
    public static SoundEvent NEREA_BURBUJA_POMPA;
    public static SoundEvent NEREA_MOLINO_ARRASTRE;
    public static SoundEvent NEREA_MOLINO_GIRO;
    public static SoundEvent NEREA_ARPON_LANZAR;
    public static SoundEvent NEREA_ARPON_ENGANCHA;
    public static SoundEvent NEREA_ARPON_REBOTA;
    public static SoundEvent NEREA_ESTOCADA;
    public static SoundEvent NEREA_MIRADA_CARGA;
    public static SoundEvent NEREA_MIRADA_RAYO;
    public static SoundEvent NEREA_MIRADA_IMPACTO;
    public static SoundEvent NEREA_OJO_ROTO;
    public static SoundEvent NEREA_ATURDIDO;
    public static SoundEvent NEREA_SELLO_GOLPE;
    public static SoundEvent NEREA_SELLO_ROTO;
    public static SoundEvent NEREA_CADENA_ROMPE;
    public static SoundEvent NEREA_TAMBALEO;
    public static SoundEvent NEREA_AGOTADO;
    public static SoundEvent NEREA_LATIDO;
    public static SoundEvent NEREA_LIBERACION;
    public static SoundEvent NEREA_DISOLVER;

    public static SoundEvent AERALIS_AMBIENTE;
    public static SoundEvent AERALIS_ALETEO;
    public static SoundEvent AERALIS_INMUNE;
    public static SoundEvent AERALIS_HERIDO;
    public static SoundEvent AERALIS_CHILLIDO;
    public static SoundEvent AERALIS_DESPERTAR;
    public static SoundEvent AERALIS_ALETEO_CARGA;
    public static SoundEvent AERALIS_ALETEO_CORTE;
    public static SoundEvent AERALIS_CUCHILLA_GOLPE;
    public static SoundEvent AERALIS_TORNADOS_GOLPE;
    public static SoundEvent AERALIS_TORNADO_NACE;
    public static SoundEvent AERALIS_TORNADO;
    public static SoundEvent AERALIS_TORNADO_ATRAPA;
    public static SoundEvent AERALIS_TORNADO_EXPLOTA;
    public static SoundEvent AERALIS_TORNADO_ROMPE;
    public static SoundEvent AERALIS_MARCA;
    public static SoundEvent AERALIS_RAFAGA;
    public static SoundEvent AERALIS_RAFAGA_ROMPE;
    public static SoundEvent AERALIS_RAFAGA_GOLPE;
    public static SoundEvent AERALIS_JUICIO_SILENCIO;
    public static SoundEvent AERALIS_JUICIO_CIRCULO;
    public static SoundEvent AERALIS_JUICIO_CICLON;
    public static SoundEvent AERALIS_NUCLEO;
    public static SoundEvent AERALIS_NUCLEO_GOLPE;
    public static SoundEvent AERALIS_NUCLEO_ROTO;
    public static SoundEvent AERALIS_JUICIO_GOLPE;
    public static SoundEvent AERALIS_TRUENO;
    public static SoundEvent AERALIS_TAMBALEO;
    public static SoundEvent AERALIS_ATURDIDA;
    public static SoundEvent AERALIS_AGOTADA;
    public static SoundEvent AERALIS_JADEO;
    public static SoundEvent AERALIS_LIBERACION;
    public static SoundEvent AERALIS_DISOLVER;

    // Rajang, el Jaguar de Jade (rajang_sonidos.py)
    public static SoundEvent RAJANG_AMBIENTE;
    public static SoundEvent RAJANG_DORMIDO;
    public static SoundEvent RAJANG_PASO;
    public static SoundEvent RAJANG_HERIDO;
    public static SoundEvent RAJANG_INMUNE;
    public static SoundEvent RAJANG_DESPERTAR;
    public static SoundEvent RAJANG_RUGIDO;
    public static SoundEvent RAJANG_GRUNIDO;
    public static SoundEvent RAJANG_ZARPAZO;
    public static SoundEvent RAJANG_GARRA_ALZA;
    public static SoundEvent RAJANG_GARRA_GOLPE;
    public static SoundEvent RAJANG_GRIETA;
    public static SoundEvent RAJANG_PICO;
    public static SoundEvent RAJANG_PICO_GOLPE;
    public static SoundEvent RAJANG_TERREMOTO;
    public static SoundEvent RAJANG_ONDA;
    public static SoundEvent RAJANG_PILAR;
    public static SoundEvent RAJANG_AVISO;
    public static SoundEvent RAJANG_PIEL_JADE;
    public static SoundEvent RAJANG_LASTRE;
    public static SoundEvent RAJANG_SELLO;
    public static SoundEvent RAJANG_PLATAFORMA;
    public static SoundEvent RAJANG_TOTEM;
    public static SoundEvent RAJANG_TOTEM_GOLPE;
    public static SoundEvent RAJANG_TOTEM_ROTO;
    public static SoundEvent RAJANG_TOTEM_REHACE;
    public static SoundEvent RAJANG_COLUMNA;
    public static SoundEvent RAJANG_RUGIDO_JADE;
    public static SoundEvent RAJANG_RELOJ;
    public static SoundEvent RAJANG_CATACLISMO;
    public static SoundEvent RAJANG_CIELO;
    public static SoundEvent RAJANG_FRAGMENTO;
    public static SoundEvent RAJANG_IMPACTO;
    public static SoundEvent RAJANG_MARCA;
    public static SoundEvent RAJANG_SALTO;
    public static SoundEvent RAJANG_ATERRIZA;
    public static SoundEvent RAJANG_ATURDIDO;
    public static SoundEvent RAJANG_PARALIZADO;
    public static SoundEvent RAJANG_CURA;
    public static SoundEvent RAJANG_TAMBALEO;
    public static SoundEvent RAJANG_LIBERACION;
    public static SoundEvent RAJANG_DISOLVER;

    private AtalayaSonidos() {
    }

    public static void registrar() {
        VIGIA_AMBIENTE = registrar("vigia.ambiente");
        VIGIA_ACECHO = registrar("vigia.acecho");
        VIGIA_PASO = registrar("vigia.paso");
        VIGIA_HERIDO = registrar("vigia.herido");
        VIGIA_MUERTE = registrar("vigia.muerte");
        VIGIA_APAGARSE = registrar("vigia.apagarse");
        VIGIA_FAROL_CAE = registrar("vigia.farol_cae");
        VIGIA_ALERTA = registrar("vigia.alerta");
        VIGIA_CEPO_ABRIR = registrar("vigia.cepo_abrir");
        VIGIA_CEPO_CERRAR = registrar("vigia.cepo_cerrar");
        VIGIA_CEPO_FALLO = registrar("vigia.cepo_fallo");
        VIGIA_MIRADA_CARGA = registrar("vigia.mirada_carga");
        VIGIA_MIRADA_DISPARO = registrar("vigia.mirada_disparo");
        VIGIA_MIRADA_CORTE = registrar("vigia.mirada_corte");
        VIGIA_RAYO_VUELO = registrar("vigia.rayo_vuelo");
        VIGIA_RAYO_IMPACTO = registrar("vigia.rayo_impacto");
        VIGIA_TAMBALEO = registrar("vigia.tambaleo");
        VIGIA_BUSCAR = registrar("vigia.buscar");
        OJO_VIGIA_USAR = registrar("ojo_vigia.usar");

        NEREA_AMBIENTE = registrar("nerea.ambiente");
        NEREA_PASO = registrar("nerea.paso");
        NEREA_INMUNE = registrar("nerea.inmune");
        NEREA_HERIDO = registrar("nerea.herido");
        NEREA_RUGIDO = registrar("nerea.rugido");
        NEREA_DESPERTAR = registrar("nerea.despertar");
        NEREA_ROMPEOLAS_ALZAR = registrar("nerea.rompeolas_alzar");
        NEREA_ROMPEOLAS_GOLPE = registrar("nerea.rompeolas_golpe");
        NEREA_OLA = registrar("nerea.ola");
        NEREA_REMOLINO_AVISO = registrar("nerea.remolino_aviso");
        NEREA_REMOLINO = registrar("nerea.remolino");
        NEREA_ANTORCHA = registrar("nerea.antorcha");
        NEREA_BURBUJAS = registrar("nerea.burbujas");
        NEREA_BURBUJA_REVIENTA = registrar("nerea.burbuja_revienta");
        NEREA_BURBUJA_POMPA = registrar("nerea.burbuja_pompa");
        NEREA_MOLINO_ARRASTRE = registrar("nerea.molino_arrastre");
        NEREA_MOLINO_GIRO = registrar("nerea.molino_giro");
        NEREA_ARPON_LANZAR = registrar("nerea.arpon_lanzar");
        NEREA_ARPON_ENGANCHA = registrar("nerea.arpon_engancha");
        NEREA_ARPON_REBOTA = registrar("nerea.arpon_rebota");
        NEREA_ESTOCADA = registrar("nerea.estocada");
        NEREA_MIRADA_CARGA = registrar("nerea.mirada_carga");
        NEREA_MIRADA_RAYO = registrar("nerea.mirada_rayo");
        NEREA_MIRADA_IMPACTO = registrar("nerea.mirada_impacto");
        NEREA_OJO_ROTO = registrar("nerea.ojo_roto");
        NEREA_ATURDIDO = registrar("nerea.aturdido");
        NEREA_SELLO_GOLPE = registrar("nerea.sello_golpe");
        NEREA_SELLO_ROTO = registrar("nerea.sello_roto");
        NEREA_CADENA_ROMPE = registrar("nerea.cadena_rompe");
        NEREA_TAMBALEO = registrar("nerea.tambaleo");
        NEREA_AGOTADO = registrar("nerea.agotado");
        NEREA_LATIDO = registrar("nerea.latido");
        NEREA_LIBERACION = registrar("nerea.liberacion");
        NEREA_DISOLVER = registrar("nerea.disolver");

        AERALIS_AMBIENTE = registrar("aeralis.ambiente");
        AERALIS_ALETEO = registrar("aeralis.aleteo");
        AERALIS_INMUNE = registrar("aeralis.inmune");
        AERALIS_HERIDO = registrar("aeralis.herido");
        AERALIS_CHILLIDO = registrar("aeralis.chillido");
        AERALIS_DESPERTAR = registrar("aeralis.despertar");
        AERALIS_ALETEO_CARGA = registrar("aeralis.aleteo_carga");
        AERALIS_ALETEO_CORTE = registrar("aeralis.aleteo_corte");
        AERALIS_CUCHILLA_GOLPE = registrar("aeralis.cuchilla_golpe");
        AERALIS_TORNADOS_GOLPE = registrar("aeralis.tornados_golpe");
        AERALIS_TORNADO_NACE = registrar("aeralis.tornado_nace");
        AERALIS_TORNADO = registrar("aeralis.tornado");
        AERALIS_TORNADO_ATRAPA = registrar("aeralis.tornado_atrapa");
        AERALIS_TORNADO_EXPLOTA = registrar("aeralis.tornado_explota");
        AERALIS_TORNADO_ROMPE = registrar("aeralis.tornado_rompe");
        AERALIS_MARCA = registrar("aeralis.marca");
        AERALIS_RAFAGA = registrar("aeralis.rafaga");
        AERALIS_RAFAGA_ROMPE = registrar("aeralis.rafaga_rompe");
        AERALIS_RAFAGA_GOLPE = registrar("aeralis.rafaga_golpe");
        AERALIS_JUICIO_SILENCIO = registrar("aeralis.juicio_silencio");
        AERALIS_JUICIO_CIRCULO = registrar("aeralis.juicio_circulo");
        AERALIS_JUICIO_CICLON = registrar("aeralis.juicio_ciclon");
        AERALIS_NUCLEO = registrar("aeralis.nucleo");
        AERALIS_NUCLEO_GOLPE = registrar("aeralis.nucleo_golpe");
        AERALIS_NUCLEO_ROTO = registrar("aeralis.nucleo_roto");
        AERALIS_JUICIO_GOLPE = registrar("aeralis.juicio_golpe");
        AERALIS_TRUENO = registrar("aeralis.trueno");
        AERALIS_TAMBALEO = registrar("aeralis.tambaleo");
        AERALIS_ATURDIDA = registrar("aeralis.aturdida");
        AERALIS_AGOTADA = registrar("aeralis.agotada");
        AERALIS_JADEO = registrar("aeralis.jadeo");
        AERALIS_LIBERACION = registrar("aeralis.liberacion");
        AERALIS_DISOLVER = registrar("aeralis.disolver");
        RAJANG_AMBIENTE = registrar("rajang.ambiente");
        RAJANG_DORMIDO = registrar("rajang.dormido");
        RAJANG_PASO = registrar("rajang.paso");
        RAJANG_HERIDO = registrar("rajang.herido");
        RAJANG_INMUNE = registrar("rajang.inmune");
        RAJANG_DESPERTAR = registrar("rajang.despertar");
        RAJANG_RUGIDO = registrar("rajang.rugido");
        RAJANG_GRUNIDO = registrar("rajang.grunido");
        RAJANG_ZARPAZO = registrar("rajang.zarpazo");
        RAJANG_GARRA_ALZA = registrar("rajang.garra_alza");
        RAJANG_GARRA_GOLPE = registrar("rajang.garra_golpe");
        RAJANG_GRIETA = registrar("rajang.grieta");
        RAJANG_PICO = registrar("rajang.pico");
        RAJANG_PICO_GOLPE = registrar("rajang.pico_golpe");
        RAJANG_TERREMOTO = registrar("rajang.terremoto");
        RAJANG_ONDA = registrar("rajang.onda");
        RAJANG_PILAR = registrar("rajang.pilar");
        RAJANG_AVISO = registrar("rajang.aviso");
        RAJANG_PIEL_JADE = registrar("rajang.piel_jade");
        RAJANG_LASTRE = registrar("rajang.lastre");
        RAJANG_SELLO = registrar("rajang.sello");
        RAJANG_PLATAFORMA = registrar("rajang.plataforma");
        RAJANG_TOTEM = registrar("rajang.totem");
        RAJANG_TOTEM_GOLPE = registrar("rajang.totem_golpe");
        RAJANG_TOTEM_ROTO = registrar("rajang.totem_roto");
        RAJANG_TOTEM_REHACE = registrar("rajang.totem_rehace");
        RAJANG_COLUMNA = registrar("rajang.columna");
        RAJANG_RUGIDO_JADE = registrar("rajang.rugido_jade");
        RAJANG_RELOJ = registrar("rajang.reloj");
        RAJANG_CATACLISMO = registrar("rajang.cataclismo");
        RAJANG_CIELO = registrar("rajang.cielo");
        RAJANG_FRAGMENTO = registrar("rajang.fragmento");
        RAJANG_IMPACTO = registrar("rajang.impacto");
        RAJANG_MARCA = registrar("rajang.marca");
        RAJANG_SALTO = registrar("rajang.salto");
        RAJANG_ATERRIZA = registrar("rajang.aterriza");
        RAJANG_ATURDIDO = registrar("rajang.aturdido");
        RAJANG_PARALIZADO = registrar("rajang.paralizado");
        RAJANG_CURA = registrar("rajang.cura");
        RAJANG_TAMBALEO = registrar("rajang.tambaleo");
        RAJANG_LIBERACION = registrar("rajang.liberacion");
        RAJANG_DISOLVER = registrar("rajang.disolver");
    }

    private static SoundEvent registrar(String nombre) {
        Identifier id = Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, nombre);
        return Registry.register(BuiltInRegistries.SOUND_EVENT, id, SoundEvent.createVariableRangeEvent(id));
    }
}
