package com.atalaya.client;

import com.atalaya.Atalaya;
import com.atalaya.entity.LuzPrismaEntity;
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
import net.minecraft.resources.Identifier;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.HumanoidArm;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.phys.Vec3;
import org.jspecify.annotations.Nullable;

/**
 * La luz del Prisma de Jade: el punto en el suelo (luz_prisma.png, que late y
 * gira despacio, con una columna de luz para verlo de lejos) y el rayo desde la
 * mano de quien lo lleva hasta el (luz_rayo.png, siempre de cara a la camara).
 * En primera persona el rayo sale de abajo a la derecha, donde se ve la mano.
 */
public class LuzPrismaRenderer extends EntityRenderer<LuzPrismaEntity, LuzPrismaRenderer.Estado> {

    private static final RenderType PUNTO = RenderTypes.eyes(tex("luz_prisma"));
    private static final RenderType RAYO = RenderTypes.eyes(tex("luz_rayo"));
    private static final int LUZ = AeralisDibujo.A_PLENA_LUZ;

    private static Identifier tex(String nombre) {
        return Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "textures/entity/rajang/" + nombre + ".png");
    }

    public static class Estado extends EntityRenderState {
        public boolean encendida;
        /** La mano, desde la luz. */
        public @Nullable Vec3 mano;
        public float tiempo;
    }

    public LuzPrismaRenderer(EntityRendererProvider.Context contexto) {
        super(contexto);
    }

    @Override
    public Estado createRenderState() {
        return new Estado();
    }

    @Override
    public boolean shouldRender(LuzPrismaEntity l, net.minecraft.client.renderer.culling.Frustum vista, double x, double y, double z) {
        // El rayo puede cruzar la pantalla aunque el punto este fuera.
        return l.encendida();
    }

    @Override
    public void extractRenderState(LuzPrismaEntity l, Estado s, float parcial) {
        super.extractRenderState(l, s, parcial);
        s.encendida = l.encendida();
        s.tiempo = l.tickCount + parcial;
        s.mano = null;
        Player p = l.dueno();
        if (p != null) {
            Vec3 desde = mano(p, parcial);
            s.mano = desde.subtract(l.getPosition(parcial));
        }
    }

    /** Donde esta la mano que lleva el prisma (en el mundo). */
    private static Vec3 mano(Player p, float parcial) {
        Minecraft mc = Minecraft.getInstance();
        boolean derecha = p.getMainArm() == HumanoidArm.RIGHT;
        if (p == mc.getCameraEntity() && mc.options.getCameraType().isFirstPerson()) {
            // Primera persona: un poco delante del ojo, abajo y al lado de la mano.
            Vec3 ojo = p.getEyePosition(parcial);
            Vec3 mira = p.getViewVector(parcial);
            Vec3 lado = mira.cross(new Vec3(0, 1, 0));
            lado = lado.lengthSqr() < 1.0E-6 ? new Vec3(1, 0, 0) : lado.normalize();
            Vec3 arriba = lado.cross(mira).normalize();
            return ojo.add(mira.scale(0.55)).add(lado.scale(derecha ? 0.3 : -0.3)).add(arriba.scale(-0.28));
        }
        float cuerpo = Mth.lerp(parcial, p.yBodyRotO, p.yBodyRot) * Mth.DEG_TO_RAD;
        double lado = derecha ? -0.38 : 0.38;
        Vec3 pos = p.getPosition(parcial);
        // El brazo extendido hacia delante, a la altura del pecho.
        return pos.add(Math.cos(cuerpo) * lado - Math.sin(cuerpo) * 0.45, p.getBbHeight() * 0.72,
                Math.sin(cuerpo) * lado + Math.cos(cuerpo) * 0.45);
    }

    @Override
    public void submit(Estado s, PoseStack pose, SubmitNodeCollector colector, CameraRenderState camara) {
        if (!s.encendida) {
            return;
        }
        float late = 0.85F + 0.15F * Mth.sin(s.tiempo * 0.5F);
        float giro = s.tiempo * 0.05F;
        float tam = 0.95F * late;
        colector.submitCustomGeometry(pose, PUNTO, (p, buf) -> {
            // El punto: tumbado, por las dos caras.
            Vec3 a = new Vec3(Math.cos(giro) * tam, 0, Math.sin(giro) * tam);
            Vec3 b = new Vec3(-Math.sin(giro) * tam, 0, Math.cos(giro) * tam);
            quad(buf, p, new Vec3(0, 0.06, 0), a, b, 255);
            quad(buf, p, new Vec3(0, 0.06, 0), b, a, 255);
            // Un halo mas grande y flojo.
            quad(buf, p, new Vec3(0, 0.05, 0), a.scale(1.8), b.scale(1.8), 90);
            quad(buf, p, new Vec3(0, 0.05, 0), b.scale(1.8), a.scale(1.8), 90);
        });
        Vec3 aCamara = camara.pos.subtract(s.x, s.y, s.z);
        colector.submitCustomGeometry(pose, RAYO, (p, buf) -> {
            // La columna de luz, para verla de lejos.
            cinta(buf, p, new Vec3(0, 0.05, 0), new Vec3(0, 1.6, 0), aCamara, 0.22F * late, 160);
            if (s.mano != null) {
                cinta(buf, p, s.mano, new Vec3(0, 0.08, 0), aCamara, 0.07F, 235);
            }
        });
        super.submit(s, pose, colector, camara);
    }

    /** Un cuadro centrado en c con medios ejes a y b. */
    private static void quad(VertexConsumer buf, PoseStack.Pose p, Vec3 c, Vec3 a, Vec3 b, int alfa) {
        Vec3 n = new Vec3(0, 1, 0);
        AeralisDibujo.vertice(buf, p, c.x - a.x - b.x, c.y, c.z - a.z - b.z, 0, 0, 255, 255, 255, alfa, LUZ, (float) n.x, (float) n.y,
                (float) n.z);
        AeralisDibujo.vertice(buf, p, c.x - a.x + b.x, c.y, c.z - a.z + b.z, 0, 1, 255, 255, 255, alfa, LUZ, (float) n.x, (float) n.y,
                (float) n.z);
        AeralisDibujo.vertice(buf, p, c.x + a.x + b.x, c.y, c.z + a.z + b.z, 1, 1, 255, 255, 255, alfa, LUZ, (float) n.x, (float) n.y,
                (float) n.z);
        AeralisDibujo.vertice(buf, p, c.x + a.x - b.x, c.y, c.z + a.z - b.z, 1, 0, 255, 255, 255, alfa, LUZ, (float) n.x, (float) n.y,
                (float) n.z);
    }

    /** Una cinta de 'desde' a 'hasta', de cara a la camara (aCamara: de la luz a la camara). */
    private static void cinta(VertexConsumer buf, PoseStack.Pose p, Vec3 desde, Vec3 hasta, Vec3 aCamara, float ancho, int alfa) {
        Vec3 eje = hasta.subtract(desde);
        double largo = eje.length();
        if (largo < 1.0E-4) {
            return;
        }
        Vec3 medio = desde.add(hasta).scale(0.5);
        Vec3 ver = aCamara.subtract(medio);
        Vec3 lado = eje.cross(ver);
        if (lado.lengthSqr() < 1.0E-8) {
            lado = eje.cross(new Vec3(0, 1, 0));
        }
        lado = lado.normalize().scale(ancho);
        Vec3 n = ver.lengthSqr() < 1.0E-8 ? new Vec3(0, 1, 0) : ver.normalize();
        float u = 1.0F;
        Vec3 a = desde.subtract(lado);
        Vec3 b = desde.add(lado);
        Vec3 c = hasta.add(lado);
        Vec3 d = hasta.subtract(lado);
        float nx = (float) n.x;
        float ny = (float) n.y;
        float nz = (float) n.z;
        // Por las dos caras (la capa de luz descarta la de atras).
        AeralisDibujo.vertice(buf, p, a.x, a.y, a.z, 0, 0, 255, 255, 255, alfa, LUZ, nx, ny, nz);
        AeralisDibujo.vertice(buf, p, b.x, b.y, b.z, 0, 1, 255, 255, 255, alfa, LUZ, nx, ny, nz);
        AeralisDibujo.vertice(buf, p, c.x, c.y, c.z, u, 1, 255, 255, 255, alfa, LUZ, nx, ny, nz);
        AeralisDibujo.vertice(buf, p, d.x, d.y, d.z, u, 0, 255, 255, 255, alfa, LUZ, nx, ny, nz);
        AeralisDibujo.vertice(buf, p, d.x, d.y, d.z, u, 0, 255, 255, 255, alfa, LUZ, nx, ny, nz);
        AeralisDibujo.vertice(buf, p, c.x, c.y, c.z, u, 1, 255, 255, 255, alfa, LUZ, nx, ny, nz);
        AeralisDibujo.vertice(buf, p, b.x, b.y, b.z, 0, 1, 255, 255, 255, alfa, LUZ, nx, ny, nz);
        AeralisDibujo.vertice(buf, p, a.x, a.y, a.z, 0, 0, 255, 255, 255, alfa, LUZ, nx, ny, nz);
    }
}
