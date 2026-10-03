package com.atalaya.sonido;

import com.atalaya.Atalaya;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.Identifier;
import net.minecraft.sounds.SoundEvent;

/**
 * Sonidos propios del mod.
 *
 * Ninguno es de vanilla: los .ogg salen de un script de sintesis que construye
 * cada uno con lo que el Vigia tiene encima —el hierro del farol, el cristal,
 * las cadenas, una garganta y la llama—, asi que todos suenan a la misma cosa.
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
    }

    private static SoundEvent registrar(String nombre) {
        Identifier id = Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, nombre);
        return Registry.register(BuiltInRegistries.SOUND_EVENT, id, SoundEvent.createVariableRangeEvent(id));
    }
}
