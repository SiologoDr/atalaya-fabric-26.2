package com.atalaya.catalogo;

import com.atalaya.Atalaya;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;

import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.HashMap;
import java.util.Map;

/**
 * Cuantos cuadros tiene cada rotulo del chat del catalogo (los titulos de los cambios, los mobs y los momentos). Lo
 * escribe catalogo.py al hacerlos, en assets/atalaya/carteles.json, y se lee del propio jar (tambien en el servidor, que
 * es quien escribe el aviso del chat).
 */
public final class Carteles {

    private static Map<String, Integer> cuadros;

    private Carteles() {
    }

    /** Los cuadros del rotulo con ese nombre (sin el numero), o 0 si no esta. */
    public static synchronized int cuadros(String nombre) {
        if (cuadros == null) {
            cuadros = leer();
        }
        return cuadros.getOrDefault(nombre, 0);
    }

    private static Map<String, Integer> leer() {
        Map<String, Integer> out = new HashMap<>();
        try (InputStream in = Carteles.class.getResourceAsStream("/assets/atalaya/carteles.json")) {
            if (in == null) {
                Atalaya.LOGGER.warn("No esta assets/atalaya/carteles.json: los rotulos del catalogo saldran sin titulo.");
                return out;
            }
            JsonObject raiz = JsonParser.parseReader(new InputStreamReader(in, StandardCharsets.UTF_8)).getAsJsonObject();
            for (String clave : raiz.keySet()) {
                out.put(clave, raiz.get(clave).getAsInt());
            }
        } catch (Exception e) {
            Atalaya.LOGGER.error("No se pudo leer carteles.json", e);
        }
        return out;
    }
}
