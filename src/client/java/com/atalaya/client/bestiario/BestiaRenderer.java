package com.atalaya.client.bestiario;

import com.atalaya.Atalaya;
import com.atalaya.bestiario.Bestia;
import com.atalaya.bestiario.BestiaEntity;
import com.mojang.blaze3d.vertex.PoseStack;
import net.minecraft.client.model.geom.ModelLayerLocation;
import net.minecraft.client.renderer.SubmitNodeCollector;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.MobRenderer;
import net.minecraft.client.renderer.entity.RenderLayerParent;
import net.minecraft.client.renderer.entity.layers.RenderLayer;
import net.minecraft.client.renderer.rendertype.RenderType;
import net.minecraft.client.renderer.rendertype.RenderTypes;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.resources.Identifier;

/**
 * Pinta un mob del bestiario: su malla con su textura (la de su variante), lo que brilla en la oscuridad (la capa de
 * ojos de vanilla, que no se apaga de noche) y sus animaciones. Al morir no se tumba de lado ni se pone rojo: hace su
 * propia animacion de muerte.
 */
public class BestiaRenderer<T extends BestiaEntity> extends MobRenderer<T, BestiaRenderState, BestiaModel> {

    protected final Bestia bestia;
    protected final BestiaDatos.Datos datos;
    private final Identifier[] texturas;
    private final RenderType[] brillos;
    private final RenderType[] geles;

    public BestiaRenderer(EntityRendererProvider.Context contexto, Bestia bestia) {
        this(contexto, bestia, BestiaDatos.de(bestia.id()));
    }

    private BestiaRenderer(EntityRendererProvider.Context contexto, Bestia bestia, BestiaDatos.Datos datos) {
        super(contexto, new BestiaModel(contexto.bakeLayer(capa(bestia.id())), datos), bestia.sombra);
        this.bestia = bestia;
        this.datos = datos;
        texturas = new Identifier[datos.variantes];
        brillos = new RenderType[datos.variantes];
        geles = new RenderType[datos.variantes];
        for (int i = 0; i < datos.variantes; i++) {
            String base = "textures/entity/bestiario/" + bestia.id() + (i == 0 ? "" : "_" + i);
            texturas[i] = Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, base + ".png");
            brillos[i] = RenderTypes.eyes(Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, base + "_brillo.png"));
            geles[i] = RenderTypes.entityTranslucent(Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, base + "_gel.png"));
        }
        if (datos.translucido) {
            addLayer(new Gel(this));
        }
        if (datos.brillo) {
            addLayer(new Brillo(this));
        }
    }

    /** La capa de su malla (BestiasCliente la registra con lo que lee BestiaDatos). */
    public static ModelLayerLocation capa(String id) {
        return new ModelLayerLocation(Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "bestia_" + id), "main");
    }

    @Override
    public BestiaRenderState createRenderState() {
        return new BestiaRenderState();
    }

    @Override
    public void extractRenderState(T e, BestiaRenderState s, float parcial) {
        super.extractRenderState(e, s, parcial);
        s.ataque.copyFrom(e.ataque);
        s.especial.copyFrom(e.especial);
        s.especial2.copyFrom(e.especial2);
        s.muerte.copyFrom(e.muerte);
        s.aparece.copyFrom(e.aparece);
        s.estado = e.getEstado();
        s.enEstado = e.tickCount - e.estadoDesde + parcial;
        s.variante = Math.min(Math.max(0, e.getVariante()), texturas.length - 1);
        s.fase = (e.getId() * 0.61803F) % 1.0F;
        s.caza = e.isAggressive();
        s.valor = e.valorCliente(parcial);
        s.creeper = e instanceof com.atalaya.bestiario.ConMecha;
        s.hasRedOverlay = e.hurtTime > 0 && e.deathTime <= 0;
        s.tinte = e instanceof com.atalaya.bestiario.Camuflada c && c.camuflada()
                && e.level() instanceof net.minecraft.client.renderer.block.BlockAndTintGetter g
                ? 0xFF000000 | net.minecraft.client.renderer.BiomeColors.getAverageGrassColor(g, e.blockPosition())
                : -1;
    }

    /** Lo camuflado, del verde de la hierba de donde esta (como los bloques de hierba). */
    @Override
    protected int getModelTint(BestiaRenderState s) {
        return s.tinte;
    }

    @Override
    public Identifier getTextureLocation(BestiaRenderState s) {
        return texturas[s.variante];
    }

    @Override
    protected void scale(BestiaRenderState s, PoseStack pose) {
        float k = datos.escala;
        if (s.creeper && s.valor > 0.0F) {
            // Como el creeper de vanilla: se hincha a lo ancho y algo a lo alto, temblando, segun avanza la mecha.
            float f = s.valor;
            float g = 1.0F + net.minecraft.util.Mth.sin(f * 100.0F) * f * 0.01F;
            f = f * f * f;
            float xz = (1.0F + f * 0.4F) * g;
            float y = (1.0F + f * 0.1F) / g;
            pose.scale(k * xz, k * y, k * xz);
        } else if (k != 1.0F) {
            pose.scale(k, k, k);
        }
    }

    @Override
    protected float getWhiteOverlayProgress(BestiaRenderState s) {
        if (!s.creeper || s.valor <= 0.0F) {
            return 0.0F;
        }
        float f = s.valor;
        return (int) (f * 10.0F) % 2 == 0 ? 0.0F : net.minecraft.util.Mth.clamp(f, 0.5F, 1.0F);
    }

    @Override
    protected float getFlipDegrees() {
        return 0.0F;
    }

    /** Lo translucido (el gel), encima de lo opaco: se ve lo de dentro a traves. Parpadea en blanco con la mecha. */
    private class Gel extends RenderLayer<BestiaRenderState, BestiaModel> {

        Gel(RenderLayerParent<BestiaRenderState, BestiaModel> padre) {
            super(padre);
        }

        @Override
        public void submit(PoseStack pose, SubmitNodeCollector colector, int luz, BestiaRenderState s, float yRot,
                           float xRot) {
            if (s.isInvisible) {
                return;
            }
            colector.order(1).submitModel(getParentModel(), s, pose, geles[s.variante], luz,
                    net.minecraft.client.renderer.entity.LivingEntityRenderer.getOverlayCoords(s, getWhiteOverlayProgress(s)),
                    s.outlineColor, null);
        }
    }

    /** Lo que brilla: la textura _brillo de su variante, con la luz de los ojos de vanilla. */
    private class Brillo extends RenderLayer<BestiaRenderState, BestiaModel> {

        Brillo(RenderLayerParent<BestiaRenderState, BestiaModel> padre) {
            super(padre);
        }

        @Override
        public void submit(PoseStack pose, SubmitNodeCollector colector, int luz, BestiaRenderState s, float yRot,
                           float xRot) {
            if (s.isInvisible) {
                return;
            }
            colector.order(1).submitModel(getParentModel(), s, pose, brillos[s.variante], luz, OverlayTexture.NO_OVERLAY,
                    s.outlineColor, null);
        }
    }
}
