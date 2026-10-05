package com.atalaya.client;

import com.atalaya.Atalaya;
import com.atalaya.entity.FragmentoJadeEntity;
import com.mojang.blaze3d.vertex.PoseStack;
import net.minecraft.client.renderer.SubmitNodeCollector;
import net.minecraft.client.renderer.entity.EntityRenderer;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.state.EntityRenderState;
import net.minecraft.client.renderer.rendertype.RenderType;
import net.minecraft.client.renderer.rendertype.RenderTypes;
import net.minecraft.client.renderer.state.level.CameraRenderState;
import net.minecraft.resources.Identifier;
import net.minecraft.util.Mth;
import net.minecraft.world.phys.Vec3;
import org.joml.Quaternionf;
import org.joml.Vector3f;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Random;

/**
 * Un fragmento del Cataclismo: un racimo de cristales de jade en bloque (el
 * nucleo y cuatro a seis puntas, fragmento.png encendido por dentro con
 * fragmento_brillo) que cae dando vueltas, envuelto en llama verde y con la
 * estela detras (tres cintas de llama.png abiertas en abanico, que se apagan
 * hacia la cola). Clavado en el suelo, medio enterrado entre los terrones del
 * crater, brilla cada vez menos hasta apagarse.
 */
public class FragmentoJadeRenderer extends EntityRenderer<FragmentoJadeEntity, FragmentoJadeRenderer.Estado> {

    private static final RenderType JADE = RenderTypes.entityCutout(tex("fragmento"));
    private static final RenderType BRILLO = RenderTypes.eyes(tex("fragmento_brillo"));
    private static final RenderType LLAMA = RenderTypes.entityTranslucentEmissive(tex("llama"));
    private static final RenderType ROCA = RenderTypes.entityCutout(tex("roca"));

    private static Identifier tex(String nombre) {
        return Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "textures/entity/rajang/" + nombre + ".png");
    }

    public static class Estado extends EntityRenderState {
        public float edad;
        public float tam;
        public int caida;
        public int semilla;
    }

    private record Piezas(List<RajangDibujo.Cara> jade, List<RajangDibujo.Cara> aura, List<RajangDibujo.Cara> crater) {
    }

    private final Map<Long, Piezas> cache = new HashMap<>();

    public FragmentoJadeRenderer(EntityRendererProvider.Context contexto) {
        super(contexto);
    }

    @Override
    public Estado createRenderState() {
        return new Estado();
    }

    @Override
    public void extractRenderState(FragmentoJadeEntity f, Estado s, float parcial) {
        super.extractRenderState(f, s, parcial);
        s.edad = f.tickCount + parcial;
        s.tam = f.getTam();
        s.caida = f.getCaida();
        s.semilla = f.getSemilla();
    }

    @Override
    protected boolean affectedByCulling(FragmentoJadeEntity f) {
        return false;
    }

    @Override
    public void submit(Estado s, PoseStack pose, SubmitNodeCollector colector, CameraRenderState camara) {
        boolean clavado = s.edad >= s.caida;
        Vec3 d = FragmentoJadeEntity.DESDE.normalize().scale(-1);
        float tam = s.tam;
        Piezas g = piezas(s.semilla, tam);
        float apaga = clavado ? Mth.clamp(1.0F - (s.edad - s.caida) / FragmentoJadeEntity.CLAVADO, 0.0F, 1.0F) : 1.0F;
        int luz = s.lightCoords;

        // El crater: terrones alrededor del impacto (sin girar).
        if (clavado) {
            float sale = Mth.clamp((s.edad - s.caida) / 3.0F, 0.0F, 1.0F);
            float hunde = Mth.clamp((s.edad - s.caida - FragmentoJadeEntity.CLAVADO + 12) / 12.0F, 0.0F, 1.0F);
            pose.pushPose();
            pose.translate(0.0, -0.6 * (1.0F - sale) - 0.7 * hunde, 0.0);
            colector.submitCustomGeometry(pose, ROCA, (p, buf) -> RajangDibujo.emitir(buf, p, g.crater(), 255, 255, 255, 255, luz));
            pose.popPose();
        }

        // El racimo: da vueltas mientras cae; clavado, se queda como cayo, medio enterrado.
        float giro = Math.min(s.edad, s.caida);
        Vector3f eje = new Vector3f((float) d.z, 0.0F, (float) -d.x).normalize();
        Quaternionf q = new Quaternionf().rotateAxis(giro * 0.32F, eje)
                .rotateAxis(giro * 0.21F, new Vector3f((float) d.x, (float) d.y, (float) d.z));
        pose.pushPose();
        if (clavado) {
            float hunde = Mth.clamp((s.edad - s.caida - FragmentoJadeEntity.CLAVADO + 12) / 12.0F, 0.0F, 1.0F);
            Vec3 c = d.scale((0.45 + 0.8 * hunde) * tam);
            pose.translate(c.x, c.y, c.z);
        }
        pose.mulPose(q);
        pose.scale(tam, tam, tam);
        colector.submitCustomGeometry(pose, JADE, (p, buf) -> RajangDibujo.emitir(buf, p, g.jade(), 255, 255, 255, 255, luz));
        int b = (int) (255 * apaga);
        colector.submitCustomGeometry(pose, BRILLO, (p, buf) ->
                RajangDibujo.emitir(buf, p, g.jade(), b, b, b, 255, AeralisDibujo.A_PLENA_LUZ));
        if (!clavado) {
            // La llama que lo envuelve, latiendo.
            int a = (int) (70 + 35 * Math.sin(s.edad * 1.3F));
            colector.submitCustomGeometry(pose, LLAMA, (p, buf) ->
                    RajangDibujo.emitir(buf, p, g.aura(), 255, 255, 255, a, AeralisDibujo.A_PLENA_LUZ));
        }
        pose.popPose();

        if (!clavado) {
            // La estela: tres cintas en abanico de la cabeza a la cola, que se apagan hacia atras.
            Vec3 cabeza = d.scale(0.4 * tam);
            Vec3 cola = d.scale(-10.0 * tam);
            Vec3 l0 = d.cross(new Vec3(1, 0, 0)).normalize();
            Vec3 m0 = d.cross(l0).normalize();
            float ancho = 1.5F * tam;
            colector.submitCustomGeometry(pose, LLAMA, (p, buf) -> {
                for (int k = 0; k < 3; k++) {
                    double ang = Math.PI * k / 3.0 + s.edad * 0.15;
                    Vec3 l = l0.scale(Math.cos(ang)).add(m0.scale(Math.sin(ang)));
                    Vec3 lc = l.scale(ancho);
                    Vec3 lt = l.scale(ancho * 0.25);
                    AeralisDibujo.vertice(buf, p, cabeza.x - lc.x, cabeza.y - lc.y, cabeza.z - lc.z, 0, 0, 255, 255, 255, 230,
                            AeralisDibujo.A_PLENA_LUZ, 0, 1, 0);
                    AeralisDibujo.vertice(buf, p, cabeza.x + lc.x, cabeza.y + lc.y, cabeza.z + lc.z, 1, 0, 255, 255, 255, 230,
                            AeralisDibujo.A_PLENA_LUZ, 0, 1, 0);
                    AeralisDibujo.vertice(buf, p, cola.x + lt.x, cola.y + lt.y, cola.z + lt.z, 1, 1, 255, 255, 255, 0,
                            AeralisDibujo.A_PLENA_LUZ, 0, 1, 0);
                    AeralisDibujo.vertice(buf, p, cola.x - lt.x, cola.y - lt.y, cola.z - lt.z, 0, 1, 255, 255, 255, 0,
                            AeralisDibujo.A_PLENA_LUZ, 0, 1, 0);
                }
            });
        }
        super.submit(s, pose, colector, camara);
    }

    private Piezas piezas(int semilla, float tam) {
        long clave = semilla;
        Piezas g = cache.get(clave);
        if (g == null) {
            if (cache.size() > 64) {
                cache.clear();
            }
            g = racimo(semilla, tam);
            cache.put(clave, g);
        }
        return g;
    }

    /** El nucleo de jade, sus puntas hacia todos lados, la llama que lo envuelve y los terrones del crater. */
    private static Piezas racimo(int semilla, float tam) {
        Random r = new Random(semilla);
        Piezas g = new Piezas(new ArrayList<>(), new ArrayList<>(), new ArrayList<>());
        // El nucleo: dos bloques de jade cruzados (un terron, no una bola).
        double n = 0.75 + r.nextDouble() * 0.1;
        RajangDibujo.bloque(g.jade(), null, r, 0, 0, 0, n, n * (0.85 + r.nextDouble() * 0.2), n, 0.18,
                r.nextDouble() * 30, r.nextDouble() * 90, r.nextDouble() * 30, 16, 32, 32);
        RajangDibujo.bloque(g.jade(), null, r, n * 0.3, n * 0.2, -n * 0.2, n * 0.8, n * 0.7, n * 0.8, 0.18,
                30 + r.nextDouble() * 30, 45 + r.nextDouble() * 30, r.nextDouble() * 30, 16, 32, 32);
        int puntas = 3 + r.nextInt(2);
        for (int k = 0; k < puntas; k++) {
            double theta = Math.acos(1.0 - 2.0 * (k + r.nextDouble() * 0.6) / puntas);
            double phi = r.nextDouble() * Math.PI * 2;
            double largo = 0.5 + r.nextDouble() * 0.45;
            double grueso = 0.22 + r.nextDouble() * 0.1;
            Vec3 dir = new Vec3(Math.sin(theta) * Math.sin(phi), Math.cos(theta), Math.sin(theta) * Math.cos(phi));
            Vec3 c = dir.scale(n * 0.7 + largo / 2);
            RajangDibujo.bloque(g.jade(), null, r, c.x, c.y, c.z, grueso, largo / 2, grueso, 0.1,
                    -Math.toDegrees(theta), Math.toDegrees(phi), 0, 16, 32, 32);
            // la punta afilada: un taco mas fino al final
            Vec3 t = dir.scale(n * 0.7 + largo + 0.12);
            RajangDibujo.bloque(g.jade(), null, r, t.x, t.y, t.z, grueso * 0.5, 0.16, grueso * 0.5, 0.1,
                    -Math.toDegrees(theta), Math.toDegrees(phi), 0, 16, 32, 32);
        }
        double a = n * 1.3;
        RajangDibujo.bloque(g.aura(), null, r, 0, 0, 0, a, a, a, 0.25, r.nextDouble() * 45, r.nextDouble() * 45, 0, 8, 16, 32);
        for (int k = 0; k < 8; k++) {
            double ang = Math.PI * 2 * k / 8 + r.nextDouble() * 0.5;
            double d = (1.0 + r.nextDouble() * 0.9) * tam;
            double t = (0.22 + r.nextDouble() * 0.22) * tam;
            RajangDibujo.bloque(g.crater(), null, r, Math.cos(ang) * d, t * 0.3, Math.sin(ang) * d, t, t * 0.7, t * (0.8 + r.nextDouble() * 0.3),
                    0.2, 15 + r.nextDouble() * 30, Math.toDegrees(-ang), (r.nextDouble() - 0.5) * 30, 12, 32, 64);
        }
        return g;
    }
}
