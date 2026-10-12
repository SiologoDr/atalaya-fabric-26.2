package com.atalaya.client;

import net.minecraft.client.animation.KeyframeAnimation;
import net.minecraft.client.model.EntityModel;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.renderer.rendertype.RenderTypes;
import net.minecraft.util.Mth;
import org.joml.Matrix4f;

import java.util.function.Function;

/**
 * El modelo de un mini jefe: el esqueleto de su {@link MiniJefeMalla} (piezas
 * vacias) movido por sus animaciones (las de &lt;Nombre&gt;Animaciones, de
 * minijefes_anim.py) y por lo que ondea solo ({@link MiniJefeEfectos#secundario}).
 * La malla la pinta {@link MiniJefeCuerpoLayer} con las matrices de las piezas.
 *
 * El reposo y el paso se mezclan por peso con los ataques (pesoLibre) y entre si
 * segun lo deprisa que va; el paso corre con su reloj, que va con el suelo.
 */
public class MiniJefeModel extends EntityModel<MiniJefeRenderState> {

    public final MiniJefeMalla malla;
    private final ModelPart[] partes;
    private final MiniJefeEfectos efectos;
    private final KeyframeAnimation reposo;
    private final KeyframeAnimation andar;
    private final KeyframeAnimation dormido;
    private final KeyframeAnimation despertar;
    private final KeyframeAnimation normal;
    private final KeyframeAnimation area;
    private final KeyframeAnimation especial;
    private final KeyframeAnimation muerte;
    private final float velocidadPaso;

    /** velocidadPaso: a cuantos bloques por tick ya anda del todo (el reposo se apaga). */
    public MiniJefeModel(MiniJefeMalla malla, MiniJefeAnimaciones a, MiniJefeEfectos efectos, float velocidadPaso) {
        super(malla.esqueleto(), RenderTypes::entityCutout);
        this.malla = malla;
        this.efectos = efectos;
        this.velocidadPaso = velocidadPaso;
        Function<String, ModelPart> buscar = root().createPartLookup();
        this.partes = new ModelPart[malla.piezas.length];
        for (int i = 0; i < partes.length; i++) {
            partes[i] = buscar.apply(malla.piezas[i]);
        }
        this.reposo = a.reposo().bake(root());
        this.andar = a.andar().bake(root());
        this.dormido = a.dormido().bake(root());
        this.despertar = a.despertar().bake(root());
        this.normal = a.normal().bake(root());
        this.area = a.area().bake(root());
        this.especial = a.especial().bake(root());
        this.muerte = a.muerte().bake(root());
    }

    @Override
    public void setupAnim(MiniJefeRenderState s) {
        super.setupAnim(s);
        if (!s.muerte.isStarted()) {
            if (s.pesoLibre > 0.0F) {
                float anda = Mth.clamp(s.velocidad / velocidadPaso, 0.0F, 1.0F);
                reposo.apply((long) (s.ageInTicks * 50.0F), s.pesoLibre * (1.0F - anda));
                andar.apply((long) s.relojAndar, s.pesoLibre * anda);
            }
            dormido.apply(s.dormido, s.ageInTicks);
            despertar.apply(s.despertar, s.ageInTicks);
            normal.apply(s.normal, s.ageInTicks);
            area.apply(s.area, s.ageInTicks);
            especial.apply(s.especial, s.ageInTicks);
        }
        muerte.apply(s.muerte, s.ageInTicks);
        efectos.secundario(this, s);
    }

    /** Una pieza por su nombre (null si no la tiene). */
    public ModelPart parte(String nombre) {
        int i = indice(nombre);
        return i < 0 ? null : partes[i];
    }

    /** El indice de una pieza (para sacar su matriz de MiniJefeRenderState.huesos), o -1. */
    public int indice(String nombre) {
        for (int i = 0; i < partes.length; i++) {
            if (malla.piezas[i].equals(nombre)) {
                return i;
            }
        }
        return -1;
    }

    /**
     * Las matrices de las piezas en la pose de ahora (16 floats cada una, en
     * columnas, del espacio de la pieza al del modelo, en bloques): como
     * ModelPart.translateAndRotate de padre a hijo. Una pieza escondida se
     * encoge a nada (y con ella sus hijas).
     */
    public float[] matrices() {
        int n = partes.length;
        float[] out = new float[n * 16];
        Matrix4f[] m = new Matrix4f[n];
        for (int i = 0; i < n; i++) {
            ModelPart p = partes[i];
            int padre = malla.padres[i];
            Matrix4f x = padre < 0 ? new Matrix4f() : new Matrix4f(m[padre]);
            x.translate(p.x / 16.0F, p.y / 16.0F, p.z / 16.0F);
            if (p.xRot != 0.0F || p.yRot != 0.0F || p.zRot != 0.0F) {
                x.rotateZYX(p.zRot, p.yRot, p.xRot);
            }
            if (p.xScale != 1.0F || p.yScale != 1.0F || p.zScale != 1.0F) {
                x.scale(p.xScale, p.yScale, p.zScale);
            }
            if (!p.visible) {
                x.scale(0.0F);
            }
            m[i] = x;
            x.get(out, i * 16);
        }
        return out;
    }
}
