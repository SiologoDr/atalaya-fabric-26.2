package com.atalaya.client;

import com.atalaya.entity.MiniJefeEntity;
import com.mojang.blaze3d.vertex.PoseStack;
import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.SubmitNodeCollector;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.MobRenderer;
import net.minecraft.client.renderer.rendertype.RenderType;
import net.minecraft.client.renderer.state.level.CameraRenderState;
import net.minecraft.resources.Identifier;
import net.minecraft.util.Mth;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;
import org.joml.Matrix4f;
import org.joml.Vector3f;
import org.jspecify.annotations.Nullable;

/**
 * Pinta un mini jefe: su malla a su escala (MiniJefeCuerpoLayer), movida por
 * sus animaciones, y lo grande de sus ataques ({@link MiniJefeEfectos}). No usa
 * el modelo de cajas de vanilla: el modelo solo es el esqueleto.
 *
 * Al morir no se tumba de lado como los bichos de vanilla: hace su animacion y
 * se deshace (desde MiniJefeEntity.disolverDesde hasta que desaparece).
 */
public class MiniJefeRenderer<T extends MiniJefeEntity> extends MobRenderer<T, MiniJefeRenderState, MiniJefeModel> {

    private final MiniJefeEfectos efectos;
    private final float escala;
    private final Identifier atlas;

    /**
     * nombre: el de su malla y su atlas; escala: lo que mide su boceto en el mundo;
     * velocidadPaso: a cuantos bloques por tick ya anda del todo.
     */
    public MiniJefeRenderer(EntityRendererProvider.Context contexto, String nombre, MiniJefeAnimaciones animaciones,
                            MiniJefeEfectos efectos, float escala, float velocidadPaso, float sombra) {
        super(contexto, new MiniJefeModel(MiniJefeMalla.de(nombre), animaciones, efectos, velocidadPaso), sombra);
        this.efectos = efectos;
        this.escala = escala;
        this.atlas = MiniJefeCuerpoLayer.tex(nombre);
        addLayer(new MiniJefeCuerpoLayer(this, nombre, efectos.plenaLuz()));
    }

    @Override
    public MiniJefeRenderState createRenderState() {
        return new MiniJefeRenderState();
    }

    @Override
    public void extractRenderState(T e, MiniJefeRenderState s, float parcial) {
        super.extractRenderState(e, s, parcial);
        s.dormido.copyFrom(e.dormido);
        s.despertar.copyFrom(e.despertar);
        s.normal.copyFrom(e.normal);
        s.area.copyFrom(e.area);
        s.especial.copyFrom(e.especial);
        s.muerte.copyFrom(e.muerte);
        s.estado = e.getEstado();
        s.tiempo = e.tiempoEstado(parcial);
        s.pesoLibre = Mth.lerp(parcial, e.pesoLibreAnt, e.pesoLibre);
        s.velocidad = Mth.lerp(parcial, e.velocidadAnt, e.velocidad);
        s.relojAndar = Mth.lerp(parcial, e.relojAndarAnt, e.relojAndar);
        s.rumbo = e.getRumbo();
        s.punto = e.getPunto().subtract(e.getPosition(parcial));
        float desde = e.disolverDesde();
        s.disolver = e.deathTime > desde
                ? Mth.clamp((e.deathTime + parcial - desde) / Math.max(1.0F, e.duracionMuerte() - 4 - desde), 0.0F, 1.0F)
                : 0.0F;
        s.hasRedOverlay = e.hurtTime > 0 && e.deathTime <= 0;
        s.vida = e.getHealth() / e.getMaxHealth();
        s.escala = escala;
        s.semilla = e.getId();
        s.miraGiro = Mth.lerp(parcial, e.miraGiroAnt, e.miraGiro);
        s.miraAlto = Mth.lerp(parcial, e.miraAltoAnt, e.miraAlto);
    }

    @Override
    public void submit(MiniJefeRenderState s, PoseStack pose, SubmitNodeCollector colector, CameraRenderState camara) {
        // Lo grande que se ve: la mitad del alto de la ventana por la escala vertical de la proyeccion (1/tan de la
        // mitad del FOV, que crece con el catalejo) entre la distancia.
        float m11 = camara.projectionMatrix.m11();
        if (!(m11 > 0.01F)) {
            m11 = 1.428F;
        }
        float alto = Minecraft.getInstance().getWindow().getHeight();
        s.pixelesPorBloque = (float) (alto * 0.5F * m11 / Math.max(0.5, Math.sqrt(s.distanceToCameraSq)));
        super.submit(s, pose, colector, camara);
        if (s.huesos.length > 0) {
            efectos.submit(s, pose, colector, camara);
        }
    }

    /** El cuerpo lo pinta la capa (MiniJefeCuerpoLayer), no el modelo de cajas. */
    @Override
    protected @Nullable RenderType getRenderType(MiniJefeRenderState s, boolean visible, boolean transparente, boolean brilla) {
        return null;
    }

    @Override
    protected void scale(MiniJefeRenderState s, PoseStack pose) {
        pose.scale(escala, escala, escala);
    }

    @Override
    protected float getFlipDegrees() {
        return 0.0F;
    }

    /**
     * Andando o dormido no se pinta si su caja (agrandada con lo que sobresale:
     * MiniJefeEfectos.alcance) esta fuera de la camara. En sus ataques y al morir
     * se pinta siempre: lo grande de los ataques llega lejos de su cuerpo.
     */
    @Override
    protected boolean affectedByCulling(T e) {
        int estado = e.getEstado();
        return (estado == MiniJefeEntity.LIBRE || estado == MiniJefeEntity.DORMIDO) && e.deathTime <= 0;
    }

    @Override
    protected AABB getBoundingBoxForCulling(T e) {
        double r = efectos.alcance() * escala;
        return e.getBoundingBox().inflate(r, r * 0.5, r);
    }

    @Override
    public Identifier getTextureLocation(MiniJefeRenderState s) {
        return atlas;
    }

    /**
     * Un punto de una pieza (en sus pixeles, los de la malla) respecto a sus pies,
     * en bloques del mundo: como LivingEntityRenderer (el giro del cuerpo, la Y
     * hacia abajo, su escala y los -1,501) y la matriz de la pieza.
     */
    public static Vec3 punto(MiniJefeRenderState s, int pieza, float x, float y, float z) {
        if (pieza < 0 || s.huesos.length < (pieza + 1) * 16) {
            return Vec3.ZERO;
        }
        Matrix4f m = new Matrix4f().rotateY((180.0F - s.bodyRot) * Mth.DEG_TO_RAD)
                .scale(-s.escala, -s.escala, s.escala)
                .translate(0.0F, -1.501F, 0.0F)
                .mul(new Matrix4f().set(s.huesos, pieza * 16));
        Vector3f v = m.transformPosition(x / 16.0F, y / 16.0F, z / 16.0F, new Vector3f());
        return new Vec3(v.x, v.y, v.z);
    }
}
