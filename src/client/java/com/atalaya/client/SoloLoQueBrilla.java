package com.atalaya.client;

import com.atalaya.Atalaya;
import com.atalaya.mixin.client.ModelPartAccesor;
import com.mojang.blaze3d.platform.NativeImage;
import net.minecraft.client.Minecraft;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.resources.Identifier;

import java.io.InputStream;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;

/**
 * Para que la pasada de lo que brilla de los jefes no pinte el cuerpo entero
 * otra vez: una copia del modelo solo con los cubos que tienen algo de brillo en
 * alguna de sus caras (en cualquiera de las texturas de brillo de sus fases).
 * Los cubos sin nada de brillo solo daban fragmentos transparentes: quitarlos no
 * cambia lo que se ve y la pasada (dos, en las fases III y IV de Rajang) cuesta
 * mucho menos. Las piezas siguen todas (vacias) para que las animaciones las
 * muevan igual.
 */
public final class SoloLoQueBrilla {

    private SoloLoQueBrilla() {
    }

    /** Una textura de entidad del mod: textures/entity/&lt;carpeta&gt;/&lt;nombre&gt;.png. */
    public static Identifier textura(String carpeta, String nombre) {
        return Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "textures/entity/" + carpeta + "/" + nombre + ".png");
    }

    /** Lo mismo con las texturas de una carpeta de entidad (textures/entity/&lt;carpeta&gt;/&lt;nombre&gt;.png). */
    public static ModelPart filtrar(ModelPart raiz, String carpeta, String... nombres) {
        List<Identifier> ts = new ArrayList<>();
        for (String n : nombres) {
            ts.add(textura(carpeta, n));
        }
        return filtrar(raiz, ts);
    }

    /** La copia de "raiz" (recien horneada, para ella sola) con solo los cubos que brillan en alguna de las texturas. */
    public static ModelPart filtrar(ModelPart raiz, List<Identifier> texturas) {
        List<NativeImage> imagenes = new ArrayList<>();
        try {
            for (Identifier t : texturas) {
                Optional<net.minecraft.server.packs.resources.Resource> r = Minecraft.getInstance().getResourceManager().getResource(t);
                if (r.isPresent()) {
                    try (InputStream in = r.get().open()) {
                        imagenes.add(NativeImage.read(in));
                    }
                }
            }
            if (imagenes.isEmpty()) {
                return raiz;
            }
            int[] cuenta = new int[2];
            ModelPart copia = copiar(raiz, imagenes, cuenta);
            Atalaya.LOGGER.info("Brillo: {} de {} cubos", cuenta[0], cuenta[1]);
            return copia;
        } catch (Exception e) {
            Atalaya.LOGGER.warn("No se pudo filtrar el brillo ({}): se pinta el modelo entero", e.toString());
            return raiz;
        } finally {
            for (NativeImage i : imagenes) {
                i.close();
            }
        }
    }

    private static ModelPart copiar(ModelPart p, List<NativeImage> imagenes, int[] cuenta) {
        ModelPartAccesor a = (ModelPartAccesor) (Object) p;
        List<ModelPart.Cube> cubos = new ArrayList<>();
        for (ModelPart.Cube c : a.atalaya$cubos()) {
            cuenta[1]++;
            if (brilla(c, imagenes)) {
                cubos.add(c);
                cuenta[0]++;
            }
        }
        Map<String, ModelPart> hijos = new HashMap<>();
        for (Map.Entry<String, ModelPart> h : a.atalaya$hijos().entrySet()) {
            hijos.put(h.getKey(), copiar(h.getValue(), imagenes, cuenta));
        }
        ModelPart n = new ModelPart(cubos, hijos);
        n.setInitialPose(p.getInitialPose());
        n.loadPose(p.getInitialPose());
        n.visible = p.visible;
        return n;
    }

    /** Si alguna cara del cubo tiene algun texel con alfa en alguna de las imagenes. */
    private static boolean brilla(ModelPart.Cube c, List<NativeImage> imagenes) {
        for (ModelPart.Polygon cara : c.polygons) {
            float u0 = 1, v0 = 1, u1 = 0, v1 = 0;
            for (ModelPart.Vertex v : cara.vertices()) {
                u0 = Math.min(u0, v.u());
                v0 = Math.min(v0, v.v());
                u1 = Math.max(u1, v.u());
                v1 = Math.max(v1, v.v());
            }
            for (NativeImage img : imagenes) {
                int w = img.getWidth();
                int h = img.getHeight();
                int x0 = Math.max(0, (int) Math.floor(u0 * w));
                int x1 = Math.min(w - 1, (int) Math.ceil(u1 * w) - 1);
                int y0 = Math.max(0, (int) Math.floor(v0 * h));
                int y1 = Math.min(h - 1, (int) Math.ceil(v1 * h) - 1);
                for (int y = y0; y <= y1; y++) {
                    for (int x = x0; x <= x1; x++) {
                        if (((img.getPixel(x, y) >>> 24) & 0xFF) > 0) {
                            return true;
                        }
                    }
                }
            }
        }
        return false;
    }
}
