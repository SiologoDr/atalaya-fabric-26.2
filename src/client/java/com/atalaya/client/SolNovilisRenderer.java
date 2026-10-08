package com.atalaya.client;

import com.atalaya.entity.NovilisEntity;
import com.atalaya.entity.SolNovilisEntity;
import com.mojang.blaze3d.vertex.PoseStack;
import net.minecraft.client.renderer.SubmitNodeCollector;
import net.minecraft.client.renderer.entity.EntityRenderer;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.state.EntityRenderState;
import net.minecraft.client.renderer.state.level.CameraRenderState;
import net.minecraft.util.Mth;
import net.minecraft.world.phys.Vec3;

/**
 * Un sol que Novilis lanza: vuela en arco con su estela de fuego. El del Sol
 * Abrasador enseña desde el principio su sello donde va a caer, y al llegar deja
 * el charco de lava; la Supernova, igual pero mas grande. El del Dios de la
 * Guerra cae en su zona (el sello carmesi lo pone la zona) y la llena de
 * explosiones.
 */
public class SolNovilisRenderer extends EntityRenderer<SolNovilisEntity, SolNovilisRenderer.Estado> {

    public static class Estado extends EntityRenderState {
        public float edad;
        public int vuelo;
        public int tipo;
        public int color;
        public Vec3 sol = Vec3.ZERO;
        public Vec3 destino = Vec3.ZERO;
        public Vec3 atras = Vec3.ZERO;
    }

    public SolNovilisRenderer(EntityRendererProvider.Context contexto) {
        super(contexto);
    }

    @Override
    public Estado createRenderState() {
        return new Estado();
    }

    @Override
    public void extractRenderState(SolNovilisEntity e, Estado s, float parcial) {
        super.extractRenderState(e, s, parcial);
        s.edad = e.tickCount + parcial;
        s.vuelo = e.getVuelo();
        s.tipo = e.getTipo();
        s.color = NovilisDibujo.color(e.getColor());
        s.sol = e.enVuelo(s.edad);
        s.atras = e.enVuelo(Math.max(0.0F, s.edad - 5.0F));
        s.destino = e.destinoRel();
    }

    @Override
    protected boolean affectedByCulling(SolNovilisEntity e) {
        return false;
    }

    @Override
    public void submit(Estado s, PoseStack pose, SubmitNodeCollector colector, CameraRenderState camara) {
        Vec3 ojo = camara.pos.subtract(s.x, s.y, s.z);
        float e = s.edad;
        Vec3 d = s.destino;
        if (e < s.vuelo) {
            float r = s.tipo == SolNovilisEntity.DIOS ? 0.9F : s.tipo == SolNovilisEntity.SUPERNOVA ? 2.6F : 1.25F;
            NovilisDibujo.solBomba(colector, pose, s.sol, ojo, r, e, s.color, 240, s.tipo == SolNovilisEntity.SUPERNOVA);
            colector.submitCustomGeometry(pose, NovilisDibujo.ESTELA, (p, buf) ->
                    NovilisDibujo.cinta(buf, p, s.sol, s.atras, ojo, r * 0.7F, 0.0F, 1.0F, s.color, 220));
            if (s.tipo != SolNovilisEntity.DIOS) {
                // El sello donde va a caer: se aprieta y parpadea mas deprisa al acercarse.
                float k = e / s.vuelo;
                float radio = s.tipo == SolNovilisEntity.SUPERNOVA ? NovilisEntity.RADIO_SUPERNOVA : NovilisEntity.RADIO_SOL;
                float m = radio * (1.12F - 0.12F * k);
                int alfa = (int) (160 + 80 * (0.5F + 0.5F * Mth.sin(e * (0.3F + 0.8F * k))));
                colector.submitCustomGeometry(pose, NovilisDibujo.SELLO, (p, buf) ->
                        NereaDibujo.suelo(buf, p, d.x, d.y + 0.06, d.z, m, e * 0.05F, s.color, alfa));
            }
        } else if (s.tipo != SolNovilisEntity.DIOS) {
            float c = e - s.vuelo;
            boolean nova = s.tipo == SolNovilisEntity.SUPERNOVA;
            if (c < SolNovilisEntity.CHARCO) {
                // El charco de lava: entra de golpe, burbujea y se enfria al final.
                float k = Mth.clamp(1.0F - (c - SolNovilisEntity.CHARCO + 20) / 20.0F, 0.0F, 1.0F);
                float m = (nova ? SolNovilisEntity.CHARCO_NOVA : SolNovilisEntity.CHARCO_SOL) * (0.85F + 0.15F * Mth.clamp(c / 4.0F, 0.0F, 1.0F));
                colector.submitCustomGeometry(pose, NovilisDibujo.CHARCO, (p, buf) ->
                        NereaDibujo.suelo(buf, p, d.x, d.y + 0.05, d.z, m, 0.0F, 0xFFFFFF, (int) (245 * k)));
                if (c < 6) {
                    float f = 1.0F - c / 6.0F;
                    colector.submitCustomGeometry(pose, NovilisDibujo.SOL, (p, buf) ->
                            NovilisDibujo.sol(buf, p, d.add(0, 1.5, 0), ojo, (nova ? NovilisEntity.RADIO_SUPERNOVA : NovilisEntity.RADIO_SOL)
                                    * (1.0F + c * 0.2F), e,
                                    s.color, (int) (240 * f)));
                }
            }
        }
        super.submit(s, pose, colector, camara);
    }
}
