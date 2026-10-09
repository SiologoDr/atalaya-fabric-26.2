package com.atalaya.client;

import com.atalaya.entity.CorchoAbismoEntity;
import com.mojang.blaze3d.vertex.PoseStack;
import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.SubmitNodeCollector;
import net.minecraft.client.renderer.entity.EntityRenderer;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.state.EntityRenderState;
import net.minecraft.client.renderer.state.level.CameraRenderState;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.HumanoidArm;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.phys.Vec3;
import org.jspecify.annotations.Nullable;

/**
 * El corcho de la Cana del Abismo: rojo y blanco, se mece en la poza; cuando
 * pica, se hunde a tirones y le sale un aro de luz dorada que se va cerrando
 * sobre el corcho durante el segundo que hay para recoger (cuando se cierra del
 * todo, se ha escapado). Del corcho a la mano del pescador va el sedal.
 */
public class CorchoAbismoRenderer extends EntityRenderer<CorchoAbismoEntity, CorchoAbismoRenderer.Estado> {

    public static class Estado extends EntityRenderState {
        public float edad;
        public int estado;
        /** Lo que lleva picando, de 0 a 1. */
        public float picada;
        public @Nullable Vec3 mano;
        public boolean propio;
    }

    public CorchoAbismoRenderer(EntityRendererProvider.Context contexto) {
        super(contexto);
    }

    @Override
    public Estado createRenderState() {
        return new Estado();
    }

    @Override
    public void extractRenderState(CorchoAbismoEntity c, Estado s, float parcial) {
        super.extractRenderState(c, s, parcial);
        s.edad = c.tickCount + parcial;
        s.estado = c.getEstado();
        s.picada = c.picada(parcial);
        s.mano = null;
        Entity d = c.getOwner();
        if (d instanceof Player p) {
            // La mano de la cana: algo delante y a un lado de los ojos (en primera persona, abajo a la derecha).
            Minecraft mc = Minecraft.getInstance();
            s.propio = mc.getCameraEntity() == p && mc.options.getCameraType().isFirstPerson();
            float y = Mth.lerp(parcial, p.yBodyRotO, p.yBodyRot) * Mth.DEG_TO_RAD;
            int lado = p.getMainArm() == HumanoidArm.RIGHT ? 1 : -1;
            Vec3 ojo = p.getEyePosition(parcial);
            Vec3 mano;
            if (s.propio) {
                Vec3 mira = p.getViewVector(parcial);
                Vec3 der = mira.cross(new Vec3(0, 1, 0)).normalize().scale(lado);
                mano = ojo.add(mira.scale(0.9)).add(der.scale(0.45)).add(0, -0.35, 0);
            } else {
                mano = p.getPosition(parcial).add(-Mth.cos(y) * 0.45 * lado - Mth.sin(y) * 0.9, 1.9, -Mth.sin(y) * 0.45 * lado
                        + Mth.cos(y) * 0.9);
            }
            s.mano = mano.subtract(c.getPosition(parcial));
        }
    }

    @Override
    protected boolean affectedByCulling(CorchoAbismoEntity c) {
        return false;
    }

    @Override
    public void submit(Estado s, PoseStack pose, SubmitNodeCollector colector, CameraRenderState camara) {
        float e = s.edad;
        boolean pica = s.estado == CorchoAbismoEntity.PICA;
        double meneo = s.estado == CorchoAbismoEntity.VUELA ? 0.0
                : pica ? -0.12 - 0.08 * Math.abs(Math.sin(e * 1.3))
                : s.estado == CorchoAbismoEntity.ESCAPO ? -0.04 : 0.03 * Math.sin(e * 0.25);
        int luz = s.lightCoords;
        Vec3 c = new Vec3(0, 0.12 + meneo, 0);
        colector.submitCustomGeometry(pose, CajaDibujo.SOLIDO, (p, buf) -> {
            CajaDibujo.caja(buf, p, c.add(0, 0.07, 0), 0.11, 0.07, 0.11, 0xF2F2F2, luz);
            CajaDibujo.caja(buf, p, c.add(0, -0.06, 0), 0.12, 0.06, 0.12, 0xD8302C, luz);
            CajaDibujo.caja(buf, p, c.add(0, 0.2, 0), 0.025, 0.07, 0.025, 0x3A2A1E, luz);
        });
        if (pica) {
            // El aro dorado se cierra sobre el corcho: lo que queda de aro es el tiempo que queda.
            float k = s.picada;
            float m = (1.6F - 1.35F * k) / NereaDibujo.ARO_EN_TEXTURA;
            int alfa = (int) (255 * Math.min(1.0F, 4.0F * (1.0F - k) + 0.2F));
            colector.submitCustomGeometry(pose, NereaDibujo.ARO, (p, buf) -> {
                NereaDibujo.suelo(buf, p, 0.0, 0.03, 0.0, m, e * 0.15F, 0xFFD24A, alfa);
                NereaDibujo.suelo(buf, p, 0.0, 0.035, 0.0, 0.3F / NereaDibujo.ARO_EN_TEXTURA, -e * 0.2F, 0xFFF4C0, 255);
            });
        }
        if (s.mano != null) {
            Vec3 a = c.add(0, 0.26, 0);
            Vec3 b = s.mano;
            colector.submitCustomGeometry(pose, CajaDibujo.SOLIDO, (p, buf) -> {
                // El sedal: tramos cortos que cuelgan un poco por el medio.
                int n = 12;
                Vec3 antes = a;
                for (int i = 1; i <= n; i++) {
                    double k = i / (double) n;
                    Vec3 q = a.lerp(b, k).add(0, -0.6 * 4 * k * (1 - k) * (s.estado == CorchoAbismoEntity.VUELA ? 0.2 : 1.0), 0);
                    Vec3 mid = antes.add(q).scale(0.5);
                    Vec3 d = q.subtract(antes).scale(0.5);
                    CajaDibujo.caja(buf, p, mid, d, new Vec3(0, 0.012, 0), d.cross(new Vec3(0, 1, 0)).normalize().scale(0.012),
                            0x1A1A1A, luz);
                    antes = q;
                }
            });
        }
        super.submit(s, pose, colector, camara);
    }
}
