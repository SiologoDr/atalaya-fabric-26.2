package com.atalaya.client;

import com.atalaya.Atalaya;
import com.atalaya.entity.EgidaNovilisEntity;
import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.SubmitNodeCollector;
import net.minecraft.client.renderer.entity.EntityRenderer;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.state.EntityRenderState;
import net.minecraft.client.renderer.rendertype.RenderType;
import net.minecraft.client.renderer.rendertype.RenderTypes;
import net.minecraft.client.renderer.state.level.CameraRenderState;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.resources.Identifier;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.phys.Vec3;

/**
 * La Egida y su sombra (novilis_egida.py): el escudo enorme que el portador
 * lleva en alto delante de el, de cara a donde mira, y la sombra que echa en el
 * suelo hacia el lado contrario al sol, con la misma cuenta que usa el servidor
 * (EgidaNovilisEntity.aLaSombra). Cuanto mas de lado mira, mas estrecha.
 *
 * El escudo va con la luz del mundo; el sol de su emblema y el canto brillan
 * (egida_brillo, a plena luz) cuanto mas de cara al sol esta: asi el portador
 * sabe que lo esta haciendo bien. A quien lo lleva, en primera persona, se le
 * dibuja casi transparente para que vea a traves.
 */
public class EgidaNovilisRenderer extends EntityRenderer<EgidaNovilisEntity, EgidaNovilisRenderer.Estado> {

    private static final RenderType ESCUDO = translucido("egida");
    private static final RenderType BRILLO = translucido("egida_brillo");
    private static final RenderType SOMBRA = translucido("sombra");
    /** El escudo: media anchura, media altura, medio grueso y a que altura va su centro (bloques). */
    private static final float MEDIO_ANCHO = 1.3F;
    private static final float MEDIO_ALTO = 1.6F;
    private static final float MEDIO_GRUESO = 0.07F;
    private static final float CENTRO_ALTO = 2.5F;
    /** El canto de oro en la textura (lo que se usa para los lados del escudo). */
    private static final float U_CANTO = 1.5F / 26.0F;
    private static final int COLOR_SOMBRA = 0x160C08;

    private static RenderType translucido(String nombre) {
        return RenderTypes.entityTranslucent(Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "textures/entity/novilis/" + nombre + ".png"));
    }

    public static class Estado extends EntityRenderState {
        public boolean ve;
        /** Los pies del portador y el sol, relativos a la Egida (que va en el suelo). */
        public Vec3 pies = Vec3.ZERO;
        public Vec3 sol = Vec3.ZERO;
        public float alto;
        public float rumbo;
        public double cara;
        public boolean propio;
        public float edad;
    }

    public EgidaNovilisRenderer(EntityRendererProvider.Context contexto) {
        super(contexto);
    }

    @Override
    public Estado createRenderState() {
        return new Estado();
    }

    @Override
    public void extractRenderState(EgidaNovilisEntity e, Estado s, float parcial) {
        super.extractRenderState(e, s, parcial);
        s.edad = e.tickCount + parcial;
        Entity b = e.level().getEntity(e.getIdPortador());
        Entity sol = e.level().getEntity(e.getIdSol());
        s.ve = b instanceof LivingEntity && sol != null && b.isAlive();
        if (!s.ve) {
            return;
        }
        Vec3 aqui = new Vec3(s.x, s.y, s.z);
        Vec3 bp = b.getPosition(parcial);
        s.pies = new Vec3(bp.x - aqui.x, 0.0, bp.z - aqui.z);
        s.alto = (float) (bp.y - aqui.y);
        s.rumbo = Mth.rotLerp(parcial, b.yRotO, b.getYRot());
        s.sol = sol.getPosition(parcial).subtract(aqui);
        s.cara = EgidaNovilisEntity.deCara(s.rumbo, s.pies, s.sol);
        Minecraft mc = Minecraft.getInstance();
        s.propio = mc.getCameraEntity() == b && mc.options.getCameraType().isFirstPerson();
    }

    @Override
    protected boolean affectedByCulling(EgidaNovilisEntity e) {
        return false;
    }

    @Override
    public void submit(Estado s, PoseStack pose, SubmitNodeCollector colector, CameraRenderState camara) {
        if (!s.ve) {
            return;
        }
        Vec3 f = EgidaNovilisEntity.frente(s.rumbo);
        Vec3 haciaSol = EgidaNovilisEntity.haciaSol(s.pies, s.sol);
        double cara = s.cara;
        // --- La sombra en el suelo: del escudo hacia el lado contrario al sol ---
        if (cara >= EgidaNovilisEntity.MIN_CARA) {
            Vec3 lat = new Vec3(-haciaSol.z, 0, haciaSol.x);
            Vec3 o = s.pies.add(f.scale(EgidaNovilisEntity.DELANTE));
            Vec3 lejos = o.subtract(haciaSol.scale(EgidaNovilisEntity.LARGO));
            double a0 = EgidaNovilisEntity.ANCHO_CERCA * cara;
            double a1 = EgidaNovilisEntity.ANCHO_LEJOS * cara;
            int alfa = (int) (175 * Mth.clamp((cara - EgidaNovilisEntity.MIN_CARA) / 0.15, 0.0, 1.0));
            Vec3 q0 = o.subtract(lat.scale(a0)).add(0, 0.06, 0);
            Vec3 q1 = o.add(lat.scale(a0)).add(0, 0.06, 0);
            Vec3 q2 = lejos.add(lat.scale(a1)).add(0, 0.06, 0);
            Vec3 q3 = lejos.subtract(lat.scale(a1)).add(0, 0.06, 0);
            colector.submitCustomGeometry(pose, SOMBRA, (p, buf) -> {
                NereaDibujo.vertice(buf, p, q0.x, q0.y, q0.z, 0, 0, COLOR_SOMBRA, alfa, 0, 1, 0);
                NereaDibujo.vertice(buf, p, q1.x, q1.y, q1.z, 1, 0, COLOR_SOMBRA, alfa, 0, 1, 0);
                NereaDibujo.vertice(buf, p, q2.x, q2.y, q2.z, 1, 1, COLOR_SOMBRA, alfa, 0, 1, 0);
                NereaDibujo.vertice(buf, p, q3.x, q3.y, q3.z, 0, 1, COLOR_SOMBRA, alfa, 0, 1, 0);
            });
        }
        // --- El escudo: una losa delante del portador, de cara a donde mira ---
        Vec3 der = new Vec3(-f.z, 0, f.x);
        Vec3 c = s.pies.add(f.scale(EgidaNovilisEntity.DELANTE)).add(0, s.alto + CENTRO_ALTO, 0);
        Vec3 w = der.scale(MEDIO_ANCHO);
        Vec3 h = new Vec3(0, MEDIO_ALTO, 0);
        Vec3 g = f.scale(MEDIO_GRUESO);
        int alfaEscudo = s.propio ? 60 : 255;
        int luz = s.lightCoords;
        colector.submitCustomGeometry(pose, ESCUDO, (p, buf) -> {
            Vec3 fr = c.add(g);
            Vec3 tr = c.subtract(g);
            // la cara del sol y la de detras
            losa(buf, p, fr.subtract(w).subtract(h), fr.add(w).subtract(h), fr.add(w).add(h), fr.subtract(w).add(h), 0, 1, f, luz, alfaEscudo);
            losa(buf, p, tr.add(w).subtract(h), tr.subtract(w).subtract(h), tr.subtract(w).add(h), tr.add(w).add(h), 0, 1, f.scale(-1), luz,
                    alfaEscudo);
            // los cantos, con el oro del borde
            Vec3[] e = {c.subtract(w).subtract(h), c.add(w).subtract(h), c.add(w).add(h), c.subtract(w).add(h)};
            Vec3[] n = {h.scale(-1).normalize(), w.normalize(), h.normalize(), w.scale(-1).normalize()};
            for (int i = 0; i < 4; i++) {
                Vec3 a = e[i];
                Vec3 b = e[(i + 1) % 4];
                losa(buf, p, a.subtract(g), b.subtract(g), b.add(g), a.add(g), 0, U_CANTO, n[i], luz, alfaEscudo);
            }
        });
        // --- El brillo: el sol del emblema y el canto, cuanto mas de cara al sol ---
        float brilla = (float) Mth.clamp((cara - EgidaNovilisEntity.MIN_CARA) / 0.45, 0.0, 1.0);
        int alfaFrente = (int) (255 * brilla * (s.propio ? 0.0F : 1.0F));
        int alfaDetras = (int) (255 * brilla * (s.propio ? 0.3F : 0.55F));
        if (alfaFrente > 4 || alfaDetras > 4) {
            float late = 0.9F + 0.1F * Mth.sin(s.edad * 0.25F);
            colector.submitCustomGeometry(pose, BRILLO, (p, buf) -> {
                Vec3 fr = c.add(g.scale(1.3));
                Vec3 tr = c.subtract(g.scale(1.3));
                if (alfaFrente > 4) {
                    losa(buf, p, fr.subtract(w).subtract(h), fr.add(w).subtract(h), fr.add(w).add(h), fr.subtract(w).add(h), 0, 1, f,
                            NereaDibujo.A_PLENA_LUZ, (int) (alfaFrente * late));
                }
                if (alfaDetras > 4) {
                    losa(buf, p, tr.add(w).subtract(h), tr.subtract(w).subtract(h), tr.subtract(w).add(h), tr.add(w).add(h), 0, 1, f.scale(-1),
                            NereaDibujo.A_PLENA_LUZ, (int) (alfaDetras * late));
                }
            });
        }
        super.submit(s, pose, colector, camara);
    }

    /** Un cuadrilatero con la textura (u de u0 a u1, v de abajo arriba), la luz dada y su normal. */
    private static void losa(VertexConsumer buf, PoseStack.Pose p, Vec3 q0, Vec3 q1, Vec3 q2, Vec3 q3, float u0, float u1, Vec3 n,
                             int luz, int alfa) {
        vertice(buf, p, q0, u0, 1, luz, alfa, n);
        vertice(buf, p, q1, u1, 1, luz, alfa, n);
        vertice(buf, p, q2, u1, 0, luz, alfa, n);
        vertice(buf, p, q3, u0, 0, luz, alfa, n);
    }

    private static void vertice(VertexConsumer buf, PoseStack.Pose p, Vec3 q, float u, float v, int luz, int alfa, Vec3 n) {
        buf.addVertex(p, (float) q.x, (float) q.y, (float) q.z)
                .setColor(255, 255, 255, Math.clamp(alfa, 0, 255))
                .setUv(u, v)
                .setOverlay(OverlayTexture.NO_OVERLAY)
                .setLight(luz)
                .setNormal(p, (float) n.x, (float) n.y, (float) n.z);
    }
}
