package com.atalaya.client;

import com.atalaya.Atalaya;
import com.atalaya.entity.NereaEntity;
import com.atalaya.entity.NereaGeometria;
import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import net.minecraft.client.renderer.SubmitNodeCollector;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.MobRenderer;
import net.minecraft.client.renderer.rendertype.RenderType;
import net.minecraft.client.renderer.rendertype.RenderTypes;
import net.minecraft.client.renderer.state.level.CameraRenderState;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.resources.Identifier;
import net.minecraft.util.ARGB;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.level.ClipContext;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;
import org.jspecify.annotations.Nullable;

/**
 * Pinta a Nerea: la malla escalada x1,6 (diez bloques de alto), la capa de lo
 * que brilla y, durante la Mirada del Abismo, el rayo doble de los ojos a su
 * victima, que se corta contra el primer bloque que encuentre.
 *
 * Al final de la liberacion se deshace con el mismo efecto que el dragon del
 * End (una mascara de ruido que se va comiendo la textura), con la mascara
 * propia de nerea_extras.py.
 */
public class NereaRenderer extends MobRenderer<NereaEntity, NereaRenderState, NereaModel> {

    /** Una piel por fase: la maldicion se extiende (venas, coral muerto). */
    private static final Identifier[] TEXTURAS = new Identifier[4];
    private static final RenderType[] DISOLVER = new RenderType[4];
    private static final Identifier MASCARA = Identifier.fromNamespaceAndPath(Atalaya.MOD_ID,
            "textures/entity/nerea/nerea_disolver.png");
    private static final Identifier RAYO = Identifier.fromNamespaceAndPath(Atalaya.MOD_ID,
            "textures/entity/nerea/rayo.png");

    static {
        for (int i = 0; i < 4; i++) {
            TEXTURAS[i] = Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "textures/entity/nerea/nerea_f" + (i + 1) + ".png");
            DISOLVER[i] = RenderTypes.entityCutoutDissolve(TEXTURAS[i], MASCARA);
        }
    }
    private static final RenderType TIPO_RAYO = RenderTypes.entityTranslucentEmissive(RAYO);

    /** Desde que tick de la liberacion empieza a deshacerse. */
    private static final float DISOLVER_DESDE = 160.0F;

    public NereaRenderer(EntityRendererProvider.Context contexto) {
        super(contexto, new NereaModel(contexto.bakeLayer(NereaModel.CAPA)), 2.4F);
        addLayer(new NereaBrilloLayer(this));
    }

    @Override
    public NereaRenderState createRenderState() {
        return new NereaRenderState();
    }

    @Override
    public void extractRenderState(NereaEntity n, NereaRenderState s, float parcial) {
        super.extractRenderState(n, s, parcial);
        s.reposo.copyFrom(n.reposo);
        s.dormido.copyFrom(n.dormido);
        s.despertar.copyFrom(n.despertar);
        s.rompeolas.copyFrom(n.rompeolas);
        s.remolino.copyFrom(n.remolino);
        s.burbujas.copyFrom(n.burbujas);
        s.molino.copyFrom(n.molino);
        s.arponLanzar.copyFrom(n.arponLanzar);
        s.arponEspera.copyFrom(n.arponEspera);
        s.arponTirar.copyFrom(n.arponTirar);
        s.mirada.copyFrom(n.mirada);
        s.aturdido.copyFrom(n.aturdido);
        s.tambaleo.copyFrom(n.tambaleo);
        s.agotado.copyFrom(n.agotado);
        s.liberacion.copyFrom(n.liberacion);
        s.estado = n.getEstado();
        s.pesoLibre = Mth.lerp(parcial, n.pesoLibreAnt, n.pesoLibre);
        s.cadenas = n.getCadenas();
        s.fase = n.fase();
        s.ritmo = n.ritmoCliente;
        s.ojosRotos = n.getOjosRotos();
        // En segundos de ANIMACION: con el ritmo de la fase, como el servidor.
        s.segundosEstado = (n.tickCount - n.inicioEstado + parcial) / 20.0F * n.ritmoCliente;
        s.libre = n.deathTime >= NereaGeometria.LIBERACION_OJOS_ORO;
        s.disolver = n.deathTime > DISOLVER_DESDE
                ? Mth.clamp((n.deathTime + parcial - DISOLVER_DESDE) / (NereaGeometria.DURACION_LIBERACION - DISOLVER_DESDE), 0.0F, 1.0F)
                : 0.0F;
        // Solo el destello del golpe: la liberacion no se tine de rojo.
        s.hasRedOverlay = n.hurtTime > 0 && n.deathTime < 4;
        extraerRayo(n, s, parcial);
    }

    private void extraerRayo(NereaEntity n, NereaRenderState s, float parcial) {
        s.finRayo = null;
        float ticks = s.segundosEstado * 20.0F;
        if (s.estado != NereaEntity.MIRADA || ticks < NereaGeometria.MIRADA_FIJA || n.isDeadOrDying()) {
            return;
        }
        Entity victima = n.level().getEntity(n.getIdObjetivo());
        if (victima == null) {
            return;
        }
        Vec3 pies = n.getPosition(parcial);
        float rumbo = s.bodyRot;
        Vec3 izq = NereaEntity.puntoMundo(NereaGeometria.OJO_IZQ_MIRADA, pies, rumbo);
        Vec3 der = NereaEntity.puntoMundo(NereaGeometria.OJO_DER_MIRADA, pies, rumbo);
        Vec3 fin = victima.getEyePosition(parcial).add(0, -0.3, 0);
        Vec3 medio = izq.add(der).scale(0.5);
        BlockHitResult choque = n.level().clip(new ClipContext(medio, fin, ClipContext.Block.COLLIDER,
                ClipContext.Fluid.NONE, n));
        if (choque.getType() != HitResult.Type.MISS) {
            fin = choque.getLocation();
        }
        s.ojoIzq = izq.subtract(pies);
        s.ojoDer = der.subtract(pies);
        s.finRayo = fin.subtract(pies);
        s.cargaRayo = Mth.clamp((ticks - NereaGeometria.MIRADA_FIJA)
                / (NereaGeometria.DURACION_MIRADA - NereaGeometria.MIRADA_FIJA), 0.0F, 1.0F);
    }

    @Override
    protected void scale(NereaRenderState s, PoseStack pose) {
        pose.scale(1.6F, 1.6F, 1.6F);
    }

    /** Sin el tumbado de lado al morir: la liberacion es de rodillas. */
    @Override
    protected float getFlipDegrees() {
        return 0.0F;
    }

    @Override
    protected @Nullable RenderType getRenderType(NereaRenderState s, boolean visible, boolean transparente, boolean brilla) {
        if (s.disolver > 0.0F && visible) {
            return DISOLVER[Math.clamp(s.fase, 1, 4) - 1];
        }
        return super.getRenderType(s, visible, transparente, brilla);
    }

    /** Lo que guia la mascara de disolverse es la transparencia del color. */
    @Override
    protected int getModelTint(NereaRenderState s) {
        return s.disolver > 0.0F ? ARGB.white(1.0F - s.disolver) : -1;
    }

    /** Diez bloques de alto y un rayo de treinta: que no se corte al girar la camara. */
    @Override
    protected boolean affectedByCulling(NereaEntity n) {
        return false;
    }

    @Override
    public void submit(NereaRenderState s, PoseStack pose, SubmitNodeCollector colector, CameraRenderState camara) {
        super.submit(s, pose, colector, camara);
        if (s.finRayo == null) {
            return;
        }
        if ((s.ojosRotos & 1) == 0 && s.ojoIzq != null) {
            rayo(pose, colector, s.ojoIzq, s.finRayo, s.cargaRayo, s.ageInTicks);
        }
        if ((s.ojosRotos & 2) == 0 && s.ojoDer != null) {
            rayo(pose, colector, s.ojoDer, s.finRayo, s.cargaRayo, s.ageInTicks);
        }
    }

    /** El rayo: dos planos cruzados que engordan y se aclaran con la carga. */
    private static void rayo(PoseStack pose, SubmitNodeCollector colector, Vec3 desde, Vec3 hasta, float carga, float edad) {
        Vec3 d = hasta.subtract(desde);
        double largo = d.length();
        if (largo < 0.1) {
            return;
        }
        Vec3 dir = d.scale(1.0 / largo);
        Vec3 ref = Math.abs(dir.y) > 0.95 ? new Vec3(1, 0, 0) : new Vec3(0, 1, 0);
        // Tiembla un poco al final, cuando esta a punto de soltar.
        float ancho = 0.12F + 0.28F * carga + (carga > 0.85F ? 0.05F * Mth.sin(edad * 2.3F) : 0.0F);
        Vec3 a = dir.cross(ref).normalize().scale(ancho);
        Vec3 b = dir.cross(a).normalize().scale(ancho);
        int alfa = (int) (120 + 135 * carga);
        int g = (int) (220 + 35 * carga);
        float v0 = -edad * 0.15F;
        float v1 = v0 + (float) largo * 0.5F;
        colector.submitCustomGeometry(pose, TIPO_RAYO, (p, buf) -> {
            plano(buf, p, desde, hasta, a, v0, v1, g, alfa);
            plano(buf, p, desde, hasta, b, v0, v1, g, alfa);
        });
    }

    private static void plano(VertexConsumer buf, PoseStack.Pose p, Vec3 desde, Vec3 hasta, Vec3 lado,
                              float v0, float v1, int g, int alfa) {
        vertice(buf, p, desde.add(lado), 0.0F, v0, g, alfa);
        vertice(buf, p, desde.subtract(lado), 1.0F, v0, g, alfa);
        vertice(buf, p, hasta.subtract(lado), 1.0F, v1, g, alfa);
        vertice(buf, p, hasta.add(lado), 0.0F, v1, g, alfa);
    }

    private static void vertice(VertexConsumer buf, PoseStack.Pose p, Vec3 q, float u, float v, int g, int alfa) {
        buf.addVertex(p, (float) q.x, (float) q.y, (float) q.z)
                .setColor(g, 255, 255, alfa)
                .setUv(u, v)
                .setOverlay(OverlayTexture.NO_OVERLAY)
                .setLight(0xF000F0)
                .setNormal(p, 0.0F, 1.0F, 0.0F);
    }

    @Override
    public Identifier getTextureLocation(NereaRenderState s) {
        return TEXTURAS[Math.clamp(s.fase, 1, 4) - 1];
    }
}
