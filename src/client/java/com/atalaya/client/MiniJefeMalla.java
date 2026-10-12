package com.atalaya.client;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.model.geom.PartPose;
import org.joml.Matrix3f;
import org.joml.Matrix4f;

import java.io.BufferedInputStream;
import java.io.DataInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.UncheckedIOException;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.zip.GZIPInputStream;

/**
 * La malla de un mini jefe, leida de assets/atalaya/minijefes/&lt;nombre&gt;.malla
 * (la escribe materiales/generadores/minijefes_juego.py desde los bocetos en
 * voxeles): sus piezas (nombre, padre, origen y giro de reposo) y, por nivel
 * de detalle y por pieza, los cuadrilateros de la piel y los de la capa de luz.
 *
 * Los niveles son la misma forma con menos cuadrilateros: el de cerca, en
 * bloques de 2 pixeles del boceto con el detalle pintado como textura, y el de
 * lejos en bloques de 4, para cuando un bloque ya no ocupa ni dos pixeles de la
 * pantalla. Asi muchos mini jefes a la vista no cuestan tanto.
 *
 * No son cajas de vanilla, pero se ven como un mob: cada cuadrilatero es una
 * cara de los bloques de su forma, con la normal plana (la luz de vanilla, por
 * cara) y su trozo del atlas pintado pixel a pixel. Las piezas son ModelPart vacias (esqueleto()),
 * solo para que las animaciones de vanilla las muevan; la malla se pinta con
 * {@link #pintar} pieza a pieza, con la matriz de cada una.
 */
public final class MiniJefeMalla {

    /** Los floats de cada vertice: x y z (bloques, en su pieza), la normal y u v (0 a 1 en el atlas). */
    static final int VERTICE = 8;

    private static final Map<String, MiniJefeMalla> LEIDAS = new HashMap<>();

    public final String nombre;
    public final String[] piezas;
    public final int[] padres;
    private final float[][] origen;
    private final float[][] giro;
    /** [nivel][pieza]: los vertices de sus cuadrilateros. */
    private final float[][][] piel;
    private final float[][][] brillo;

    private MiniJefeMalla(String nombre, String[] piezas, int[] padres, float[][] origen, float[][] giro, float[][][] piel,
                          float[][][] brillo) {
        this.nombre = nombre;
        this.piezas = piezas;
        this.padres = padres;
        this.origen = origen;
        this.giro = giro;
        this.piel = piel;
        this.brillo = brillo;
    }

    /** La malla de un mini jefe (se lee una vez). */
    public static synchronized MiniJefeMalla de(String nombre) {
        return LEIDAS.computeIfAbsent(nombre, MiniJefeMalla::leer);
    }

    private static MiniJefeMalla leer(String nombre) {
        String ruta = "/assets/atalaya/minijefes/" + nombre + ".malla";
        try (InputStream in = MiniJefeMalla.class.getResourceAsStream(ruta)) {
            if (in == null) {
                throw new IOException("No esta " + ruta);
            }
            DataInputStream d = new DataInputStream(new BufferedInputStream(new GZIPInputStream(in), 1 << 16));
            byte[] firma = new byte[4];
            d.readFully(firma);
            if (firma[0] != 'M' || firma[1] != 'J' || firma[2] != 'M' || firma[3] != '2') {
                throw new IOException(ruta + " no es una malla de mini jefe");
            }
            int ancho = d.readUnsignedShort();
            int alto = d.readUnsignedShort();
            int n = d.readUnsignedShort();
            int niveles = d.readUnsignedShort();
            String[] piezas = new String[n];
            int[] padres = new int[n];
            float[][] origen = new float[n][3];
            float[][] giro = new float[n][3];
            int[][] nPiel = new int[niveles][n];
            int[][] nBrillo = new int[niveles][n];
            for (int i = 0; i < n; i++) {
                piezas[i] = d.readUTF();
                padres[i] = d.readShort();
                for (int k = 0; k < 3; k++) {
                    origen[i][k] = d.readFloat();
                }
                for (int k = 0; k < 3; k++) {
                    giro[i][k] = d.readFloat() * ((float) Math.PI / 180.0F);
                }
                for (int k = 0; k < niveles; k++) {
                    nPiel[k][i] = d.readInt();
                    nBrillo[k][i] = d.readInt();
                }
            }
            float[][][] piel = new float[niveles][n][];
            float[][][] brillo = new float[niveles][n][];
            for (int k = 0; k < niveles; k++) {
                for (int i = 0; i < n; i++) {
                    piel[k][i] = cuadros(d, nPiel[k][i], ancho, alto);
                    brillo[k][i] = cuadros(d, nBrillo[k][i], ancho, alto);
                }
            }
            return new MiniJefeMalla(nombre, piezas, padres, origen, giro, piel, brillo);
        } catch (IOException e) {
            throw new UncheckedIOException(e);
        }
    }

    private static float[] cuadros(DataInputStream d, int n, int ancho, int alto) throws IOException {
        float[] out = new float[n * 4 * VERTICE];
        int k = 0;
        for (int i = 0; i < n * 4; i++) {
            out[k++] = d.readShort() / 128.0F / 16.0F;
            out[k++] = d.readShort() / 128.0F / 16.0F;
            out[k++] = d.readShort() / 128.0F / 16.0F;
            out[k++] = d.readByte() / 127.0F;
            out[k++] = d.readByte() / 127.0F;
            out[k++] = d.readByte() / 127.0F;
            out[k++] = d.readUnsignedShort() / 64.0F / ancho;
            out[k++] = d.readUnsignedShort() / 64.0F / alto;
        }
        return out;
    }

    /** Las piezas como ModelPart vacias, cada una con su origen y su giro de reposo, colgadas de una raiz sin nada. */
    public ModelPart esqueleto() {
        int n = piezas.length;
        ModelPart[] p = new ModelPart[n];
        @SuppressWarnings("unchecked")
        Map<String, ModelPart>[] hijos = new Map[n];
        for (int i = 0; i < n; i++) {
            hijos[i] = new HashMap<>();
            p[i] = new ModelPart(List.of(), hijos[i]);
            PartPose pose = PartPose.offsetAndRotation(origen[i][0], origen[i][1], origen[i][2], giro[i][0], giro[i][1], giro[i][2]);
            p[i].setInitialPose(pose);
            p[i].loadPose(pose);
        }
        Map<String, ModelPart> raices = new HashMap<>();
        for (int i = 0; i < n; i++) {
            (padres[i] < 0 ? raices : hijos[padres[i]]).put(piezas[i], p[i]);
        }
        return new ModelPart(List.of(), raices);
    }

    /** Cuantos niveles de detalle trae (el 0 es el de cerca). */
    public int niveles() {
        return piel.length;
    }

    /**
     * Pinta la piel (o la capa de luz) del nivel de detalle dado con las matrices
     * de las piezas (16 floats cada una, de su espacio al del modelo, en bloques):
     * cada vertice a su sitio con su normal. Las cuentas van a mano, sin objetos
     * por vertice, y la normal solo se vuelve a medir si la pieza esta estirada.
     */
    public void pintar(PoseStack.Pose p, VertexConsumer buf, float[] huesos, int nivel, boolean luz, int color, int overlay,
                       int brillo) {
        float[][] cuadros = (luz ? this.brillo : this.piel)[Math.max(0, Math.min(nivel, piel.length - 1))];
        Matrix4f h = new Matrix4f();
        Matrix4f m = new Matrix4f();
        Matrix3f r = new Matrix3f();
        Matrix3f nm = new Matrix3f();
        for (int i = 0; i < cuadros.length; i++) {
            float[] q = cuadros[i];
            if (q.length == 0) {
                continue;
            }
            h.set(huesos, i * 16);
            m.set(p.pose()).mul(h);
            nm.set(p.normal()).mul(r.set(h));
            float a00 = m.m00(), a01 = m.m01(), a02 = m.m02();
            float a10 = m.m10(), a11 = m.m11(), a12 = m.m12();
            float a20 = m.m20(), a21 = m.m21(), a22 = m.m22();
            float a30 = m.m30(), a31 = m.m31(), a32 = m.m32();
            float b00 = nm.m00, b01 = nm.m01, b02 = nm.m02;
            float b10 = nm.m10, b11 = nm.m11, b12 = nm.m12;
            float b20 = nm.m20, b21 = nm.m21, b22 = nm.m22;
            boolean medir = Math.abs(b00 * b00 + b01 * b01 + b02 * b02 - 1.0F) > 1.0E-3F
                    || Math.abs(b10 * b10 + b11 * b11 + b12 * b12 - 1.0F) > 1.0E-3F
                    || Math.abs(b20 * b20 + b21 * b21 + b22 * b22 - 1.0F) > 1.0E-3F;
            for (int k = 0; k < q.length; k += VERTICE) {
                float x = q[k], y = q[k + 1], z = q[k + 2];
                float a = q[k + 3], b = q[k + 4], c = q[k + 5];
                float nx = b00 * a + b10 * b + b20 * c;
                float ny = b01 * a + b11 * b + b21 * c;
                float nz = b02 * a + b12 * b + b22 * c;
                if (medir) {
                    float l = nx * nx + ny * ny + nz * nz;
                    if (l > 1.0E-6F) {
                        float f = 1.0F / (float) Math.sqrt(l);
                        nx *= f;
                        ny *= f;
                        nz *= f;
                    }
                }
                buf.addVertex(a00 * x + a10 * y + a20 * z + a30, a01 * x + a11 * y + a21 * z + a31,
                        a02 * x + a12 * y + a22 * z + a32, color, q[k + 6], q[k + 7], overlay, brillo, nx, ny, nz);
            }
        }
    }
}
