package com.atalaya.client.bestiario;

import com.atalaya.Atalaya;
import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import net.minecraft.client.animation.AnimationChannel;
import net.minecraft.client.animation.AnimationDefinition;
import net.minecraft.client.animation.Keyframe;
import net.minecraft.client.model.geom.PartPose;
import net.minecraft.client.model.geom.builders.CubeListBuilder;
import net.minecraft.client.model.geom.builders.LayerDefinition;
import net.minecraft.client.model.geom.builders.MeshDefinition;
import net.minecraft.client.model.geom.builders.PartDefinition;
import net.minecraft.util.Mth;
import org.joml.Vector3f;

import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/**
 * La malla y las animaciones de un mob del bestiario, leidas de assets/atalaya/bestiario/&lt;id&gt;.json (las escribe
 * bestiario_juego.py desde su boceto; no se editan a mano).
 *
 * <pre>
 *   "textura": [ancho, alto]          la cuadricula de la textura (el png es K veces mas fino)
 *   "partes": [{"n", "p", "o", "r", "c"}]
 *                                     cada parte: su nombre, su padre (o null), su sitio y su giro (grados), y sus
 *                                     cajas [u, v, x, y, z, ancho, alto, fondo, ox, oy, oz, rx, ry, rz]: cada caja en su
 *                                     propia pieza (n_c0, n_c1...) con su giro, que una caja de ModelPart no se gira sola
 *   "anim": {nombre: {"largo", "bucle", "canales": [{"p", "t", "k"}]}}
 *                                     t: "r" giro (grados), "m" movimiento (pixeles, en el sentido de Minecraft) o
 *                                     "e" escala; k: [[segundo, x, y, z, suave], ...] (suave 0: lineal)
 *   "mira": [[parte, cuanto], ...]    las partes que siguen la mirada (la cabeza, el cuello...)
 *   "escala", "brillo", "paso"        a que tamano se pinta, si tiene textura de lo que brilla y el ritmo del paso
 *   "variantes"                       cuantas texturas tiene (&lt;id&gt;.png, &lt;id&gt;_1.png...)
 *   "translucido"                     si tiene una parte translucida (el gel): va en &lt;id&gt;_gel.png y se pinta
 *                                     encima, en otra pasada (como el slime)
 * </pre>
 */
public final class BestiaDatos {

    /** Lo leido de un mob. */
    public static final class Datos {
        public final String id;
        public final LayerDefinition capa;
        public final Map<String, AnimationDefinition> animaciones = new LinkedHashMap<>();
        public final List<String> mira = new ArrayList<>();
        public final List<Float> cuantoMira = new ArrayList<>();
        public final float escala;
        public final boolean brillo;
        /** Cuanto tiempo de la animacion de andar por cada paso que avanza (como applyWalk). */
        public float paso = 2.0F;
        /** Cuantas variantes de textura tiene (la 0 es la normal). */
        public int variantes = 1;
        /** Si lleva una capa translucida (&lt;id&gt;_gel.png) que se pinta encima de lo opaco. */
        public boolean translucido;

        Datos(String id, LayerDefinition capa, float escala, boolean brillo) {
            this.id = id;
            this.capa = capa;
            this.escala = escala;
            this.brillo = brillo;
        }
    }

    private static final Map<String, Datos> LEIDOS = new HashMap<>();

    private BestiaDatos() {
    }

    /** Los datos de ese mob (se leen una vez y se guardan). */
    public static synchronized Datos de(String id) {
        return LEIDOS.computeIfAbsent(id, BestiaDatos::leer);
    }

    private static Datos leer(String id) {
        String ruta = "/assets/atalaya/bestiario/" + id + ".json";
        try (InputStream in = BestiaDatos.class.getResourceAsStream(ruta)) {
            if (in == null) {
                Atalaya.LOGGER.error("Falta {}: el mob {} saldra vacio.", ruta, id);
                return new Datos(id, LayerDefinition.create(new MeshDefinition(), 16, 16), 1.0F, false);
            }
            JsonObject raiz = JsonParser.parseReader(new InputStreamReader(in, StandardCharsets.UTF_8)).getAsJsonObject();
            JsonArray tex = raiz.getAsJsonArray("textura");
            MeshDefinition malla = new MeshDefinition();
            Map<String, PartDefinition> partes = new HashMap<>();
            partes.put(null, malla.getRoot());
            for (JsonElement el : raiz.getAsJsonArray("partes")) {
                JsonObject p = el.getAsJsonObject();
                String nombre = p.get("n").getAsString();
                String padre = p.get("p").isJsonNull() ? null : p.get("p").getAsString();
                float[] o = floats(p.getAsJsonArray("o"));
                float[] r = floats(p.getAsJsonArray("r"));
                PartDefinition def = partes.get(padre).addOrReplaceChild(nombre, CubeListBuilder.create(),
                        PartPose.offsetAndRotation(o[0], o[1], o[2], r[0] * Mth.DEG_TO_RAD, r[1] * Mth.DEG_TO_RAD,
                                r[2] * Mth.DEG_TO_RAD));
                partes.put(nombre, def);
                JsonArray cajas = p.getAsJsonArray("c");
                for (int i = 0; i < cajas.size(); i++) {
                    float[] c = floats(cajas.get(i).getAsJsonArray());
                    def.addOrReplaceChild(nombre + "_c" + i,
                            CubeListBuilder.create().texOffs((int) c[0], (int) c[1]).addBox(c[2], c[3], c[4], c[5], c[6], c[7]),
                            PartPose.offsetAndRotation(c[8], c[9], c[10], c[11] * Mth.DEG_TO_RAD, c[12] * Mth.DEG_TO_RAD,
                                    c[13] * Mth.DEG_TO_RAD));
                }
            }
            LayerDefinition capa = LayerDefinition.create(malla, tex.get(0).getAsInt(), tex.get(1).getAsInt());
            Datos d = new Datos(id, capa, raiz.has("escala") ? raiz.get("escala").getAsFloat() : 1.0F,
                    raiz.has("brillo") && raiz.get("brillo").getAsBoolean());
            if (raiz.has("paso")) {
                d.paso = raiz.get("paso").getAsFloat();
            }
            if (raiz.has("translucido")) {
                d.translucido = raiz.get("translucido").getAsBoolean();
            }
            if (raiz.has("variantes")) {
                d.variantes = Math.max(1, raiz.get("variantes").getAsInt());
            }
            if (raiz.has("anim")) {
                JsonObject anims = raiz.getAsJsonObject("anim");
                for (String nombre : anims.keySet()) {
                    d.animaciones.put(nombre, animacion(anims.getAsJsonObject(nombre)));
                }
            }
            if (raiz.has("mira")) {
                for (JsonElement el : raiz.getAsJsonArray("mira")) {
                    JsonArray m = el.getAsJsonArray();
                    d.mira.add(m.get(0).getAsString());
                    d.cuantoMira.add(m.get(1).getAsFloat());
                }
            }
            return d;
        } catch (Exception e) {
            Atalaya.LOGGER.error("No se pudo leer " + ruta, e);
            return new Datos(id, LayerDefinition.create(new MeshDefinition(), 16, 16), 1.0F, false);
        }
    }

    private static AnimationDefinition animacion(JsonObject a) {
        AnimationDefinition.Builder b = AnimationDefinition.Builder.withLength(a.get("largo").getAsFloat());
        if (a.has("bucle") && a.get("bucle").getAsBoolean()) {
            b.looping();
        }
        for (JsonElement el : a.getAsJsonArray("canales")) {
            JsonObject c = el.getAsJsonObject();
            String tipo = c.get("t").getAsString();
            AnimationChannel.Target destino = switch (tipo) {
                case "m" -> AnimationChannel.Targets.POSITION;
                case "e" -> AnimationChannel.Targets.SCALE;
                default -> AnimationChannel.Targets.ROTATION;
            };
            JsonArray ks = c.getAsJsonArray("k");
            Keyframe[] claves = new Keyframe[ks.size()];
            for (int i = 0; i < ks.size(); i++) {
                float[] k = floats(ks.get(i).getAsJsonArray());
                Vector3f v = switch (tipo) {
                    case "m" -> new Vector3f(k[1], k[2], k[3]);
                    case "e" -> new Vector3f(k[1] - 1.0F, k[2] - 1.0F, k[3] - 1.0F);
                    default -> new Vector3f(k[1] * Mth.DEG_TO_RAD, k[2] * Mth.DEG_TO_RAD, k[3] * Mth.DEG_TO_RAD);
                };
                boolean suave = k.length < 5 || k[4] != 0.0F;
                claves[i] = new Keyframe(k[0], v, suave ? AnimationChannel.Interpolations.CATMULLROM
                        : AnimationChannel.Interpolations.LINEAR);
            }
            b.addAnimation(c.get("p").getAsString(), new AnimationChannel(destino, claves));
        }
        return b.build();
    }

    private static float[] floats(JsonArray a) {
        float[] out = new float[a.size()];
        for (int i = 0; i < out.length; i++) {
            out[i] = a.get(i).getAsFloat();
        }
        return out;
    }
}
