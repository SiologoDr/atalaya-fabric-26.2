package com.atalaya.client;

import com.atalaya.Atalaya;
import com.atalaya.entity.RajangEntity;
import com.atalaya.entity.RajangGeometria;
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
import org.jspecify.annotations.Nullable;

/**
 * Pinta a Rajang: la malla a tamano real (8 bloques a la cruz, 25 de largo con
 * la cola) con la piel pintada de cada fase (rajang_juego.py: el mosaico de
 * jade, las espirales de oro y las grietas que nacen del sol del pecho) y la
 * capa de lo que brilla. Liberado, el jade vuelve al de la fase I con las
 * grietas cerradas en oro, y al final la piedra se deshace a terrones con la
 * mascara de rajang_piezas.py.
 *
 * Con la Furia de Jade, el aura verde por encima ({@link RajangFuriaLayer}).
 * Durante el aviso de la Embestida, la flecha en el suelo hacia donde va a
 * cargar (se llena mientras se agazapa) con las dos filas de rombos donde van a
 * reventar los pinchos; durante la carga, lo que le queda por delante.
 *
 * Durante la Tumba de Raices, el circulo bajo el: lo pinta aqui y no una
 * particula porque el juego descarta las particulas cuyo centro no se ve, y con
 * 36 bloques de radio quien huye mirando hacia fuera dejaria de ver el borde.
 */
public class RajangRenderer extends MobRenderer<RajangEntity, RajangRenderState, RajangModel> {

    private static final Identifier[] TEXTURAS = new Identifier[4];
    private static final Identifier LIBRE = tex("rajang_libre");
    private static final Identifier MASCARA = tex("rajang_disolver");
    private static final RenderType DISOLVER = RenderTypes.entityCutoutDissolve(LIBRE, MASCARA);

    static {
        for (int i = 0; i < 4; i++) {
            TEXTURAS[i] = tex("rajang_f" + (i + 1));
        }
    }

    /** Desde que tick de la liberacion empieza a deshacerse. */
    private static final float DISOLVER_DESDE = 160.0F;

    /** La flecha de la Embestida: los galones (se repiten cada GALON bloques), la punta y los rombos de los pinchos. */
    private static final RenderType FLECHA = RenderTypes.entityTranslucentEmissive(tex("flecha"));
    private static final RenderType PUNTA = RenderTypes.entityTranslucentEmissive(tex("flecha_punta"));
    private static final RenderType ROMBO = RenderTypes.entityTranslucentEmissive(tex("rombo"));
    private static final float GALON = 6.0F;
    /** Desde donde sale (sus manos), lo ancho que es (su cuerpo) y donde van los pinchos. */
    private static final float FLECHA_DESDE = 2.2F;
    private static final float FLECHA_ANCHO = 3.0F;
    private static final float PINCHOS_LADO = 4.2F;

    /** La Tumba de Raices: el borde (y su parpadeo) y lo llenado, tumbados bajo el. */
    private static final RenderType BORDE = RenderTypes.entityTranslucentEmissive(tex("tumba_borde"));
    private static final RenderType BORDE_AVISO = RenderTypes.entityTranslucentEmissive(tex("tumba_borde_aviso"));
    private static final RenderType RAIZ = RenderTypes.entityTranslucentEmissive(tex("tumba_raiz"));
    /** La Tumba en anillo: el borde con las flechas hacia dentro y el circulo dorado donde se salva. */
    private static final RenderType BORDE_ANILLO = RenderTypes.entityTranslucentEmissive(tex("tumba_borde_anillo"));
    private static final RenderType BORDE_ANILLO_AVISO = RenderTypes.entityTranslucentEmissive(tex("tumba_borde_anillo_aviso"));
    private static final RenderType SEGURO = RenderTypes.entityTranslucentEmissive(tex("tumba_seguro"));
    /** El radio (en la textura de lo llenado, de 0 a 0,5) de su frente encendido. */
    private static final float FRENTE_TEX = 30.0F / 64.0F;
    /** Lo que sigue el borde tras reventar (ticks) y desde cuando antes parpadea. */
    private static final float TUMBA_QUEDA = 6.0F;
    private static final float TUMBA_PARPADEO = 30.0F;

    private static Identifier tex(String nombre) {
        return Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "textures/entity/rajang/" + nombre + ".png");
    }

    public RajangRenderer(EntityRendererProvider.Context contexto) {
        super(contexto, new RajangModel(contexto.bakeLayer(RajangModel.CAPA)), 4.5F);
        addLayer(new RajangBrilloLayer(this));
        addLayer(new RajangFuriaLayer(this, new RajangModel(contexto.bakeLayer(RajangModel.CAPA_AURA))));
    }

    @Override
    public RajangRenderState createRenderState() {
        return new RajangRenderState();
    }

    @Override
    public void extractRenderState(RajangEntity r, RajangRenderState s, float parcial) {
        super.extractRenderState(r, s, parcial);
        s.dormido.copyFrom(r.dormido);
        s.despertar.copyFrom(r.despertar);
        s.garra.copyFrom(r.garra);
        s.terremoto.copyFrom(r.terremoto);
        s.rugido.copyFrom(r.rugido);
        s.sello.copyFrom(r.sello);
        s.cataclismo.copyFrom(r.cataclismo);
        s.cataclismoSostiene.copyFrom(r.cataclismoSostiene);
        s.cataclismoBaja.copyFrom(r.cataclismoBaja);
        s.aturdido.copyFrom(r.aturdido);
        s.paralizado.copyFrom(r.paralizado);
        s.salto.copyFrom(r.salto);
        s.tambaleo.copyFrom(r.tambaleo);
        s.embestidaAviso.copyFrom(r.embestidaAviso);
        s.embestida.copyFrom(r.embestida);
        s.embestidaFrena.copyFrom(r.embestidaFrena);
        s.estampado.copyFrom(r.estampado);
        s.tumba.copyFrom(r.tumba);
        s.liberacion.copyFrom(r.liberacion);
        s.estado = r.getEstado();
        s.pesoLibre = Mth.lerp(parcial, r.pesoLibreAnt, r.pesoLibre);
        s.fase = r.fase();
        s.ritmo = r.ritmoCliente;
        s.velocidad = Mth.lerp(parcial, r.velocidadAnt, r.velocidad);
        s.relojAndar = Mth.lerp(parcial, r.relojAndarAnt, r.relojAndar);
        s.relojCorrer = Mth.lerp(parcial, r.relojCorrerAnt, r.relojCorrer);
        s.libre = r.deathTime >= RajangGeometria.LIBERACION_OJOS_ORO;
        s.disolver = r.deathTime > DISOLVER_DESDE
                ? Mth.clamp((r.deathTime + parcial - DISOLVER_DESDE) / (RajangGeometria.DURACION_LIBERACION - DISOLVER_DESDE), 0.0F, 1.0F)
                : 0.0F;
        s.hasRedOverlay = r.hurtTime > 0 && r.deathTime < 4;
        s.furia = r.tieneFuria();
        int e = r.getEstado();
        s.carga = (e == RajangEntity.EMBESTIDA_AVISO || e == RajangEntity.EMBESTIDA) && r.deathTime <= 0 ? r.getCarga() : 0.0F;
        s.cargaLlena = e == RajangEntity.EMBESTIDA_AVISO
                ? Mth.clamp((r.tickCount - r.inicioEstado + parcial) * r.ritmoCliente / RajangGeometria.DURACION_EMBESTIDA_AVISO, 0.0F, 1.0F)
                : 1.0F;
        s.circuloTumba = e == RajangEntity.TUMBA && r.deathTime <= 0 ? r.tickCount - r.inicioEstado + parcial : -1.0F;
        s.tumbaAnillo = r.isTumbaAnillo();
        s.tiempoDespertar = e == RajangEntity.DESPERTAR && r.deathTime <= 0 ? r.tickCount - r.inicioEstado + parcial : -1.0F;
    }

    @Override
    public void submit(RajangRenderState s, PoseStack pose, SubmitNodeCollector colector, CameraRenderState camara) {
        super.submit(s, pose, colector, camara);
        if (s.carga > 0.5F) {
            flecha(s, pose, colector);
        }
        if (s.circuloTumba >= 0.0F) {
            tumba(s, pose, colector);
        }
    }

    /**
     * El circulo de la Tumba: el borde entero desde el principio (para saber
     * adonde correr) y parpadeando el ultimo segundo y medio; lo llenado crece
     * desde el a ritmo fijo hasta que revienta. Giran despacio, en sentidos
     * contrarios.
     */
    private static void tumba(RajangRenderState s, PoseStack pose, SubmitNodeCollector colector) {
        float t = s.circuloTumba;
        float estalla = RajangGeometria.TUMBA_ESTALLA;
        if (t > estalla + TUMBA_QUEDA) {
            return;
        }
        float radio = (float) RajangEntity.TUMBA_RADIO;
        float entra = Mth.clamp(t / 3.0F, 0.0F, 1.0F);
        float sale = Mth.clamp((estalla + TUMBA_QUEDA - t) / TUMBA_QUEDA, 0.0F, 1.0F);
        boolean parpadea = estalla - t < TUMBA_PARPADEO && ((int) t / 3) % 2 == 0;
        int alfaBorde = (int) (255 * entra * sale);
        if (s.tumbaAnillo) {
            anilloTumba(s, pose, colector, t, estalla, radio, entra, parpadea, alfaBorde);
            return;
        }
        colector.submitCustomGeometry(pose, parpadea ? BORDE_AVISO : BORDE, (p, buf) ->
                disco(buf, p, radio, t * 0.006F, 0.09F, alfaBorde));
        if (t < estalla) {
            float lleno = Math.max(0.05F, radio * t / estalla);
            int alfaRaiz = (int) (217 * entra);
            colector.submitCustomGeometry(pose, RAIZ, (p, buf) -> disco(buf, p, lleno, -t * 0.003F, 0.07F, alfaRaiz));
        }
    }

    /**
     * La Tumba en anillo: el borde con las flechas hacia dentro, el circulo dorado
     * a su alrededor (donde se salva) desde el principio, y lo llenado, que avanza
     * del borde hacia el con su frente encendido.
     */
    private static void anilloTumba(RajangRenderState s, PoseStack pose, SubmitNodeCollector colector, float t, float estalla,
                                    float radio, float entra, boolean parpadea, int alfaBorde) {
        float seguro = (float) RajangEntity.TUMBA_SEGURO;
        colector.submitCustomGeometry(pose, parpadea ? BORDE_ANILLO_AVISO : BORDE_ANILLO, (p, buf) ->
                disco(buf, p, radio, t * 0.006F, 0.09F, alfaBorde));
        colector.submitCustomGeometry(pose, SEGURO, (p, buf) -> disco(buf, p, seguro, -t * 0.01F, 0.11F, alfaBorde));
        if (t < estalla) {
            float dentro = Math.max(seguro, radio - (radio - seguro) * t / estalla);
            int alfaRaiz = (int) (217 * entra);
            colector.submitCustomGeometry(pose, RAIZ, (p, buf) -> {
                anillo(buf, p, dentro, radio, radio, -t * 0.003F, 0.07F, alfaRaiz, 0.0F);
                anillo(buf, p, dentro, Math.min(radio, dentro + 0.8F), radio, 0.0F, 0.075F, (int) (255 * entra), FRENTE_TEX);
            });
        }
    }

    /**
     * Una corona tumbada entre rDentro y rFuera. Si rTex es 0, la textura va como
     * en disco() (un cuadrado de medio lado 'escala'), recortada; si no, cada punto
     * toma el color de ese radio de la textura (para pintar un frente encendido).
     */
    private static void anillo(VertexConsumer buf, PoseStack.Pose p, float rDentro, float rFuera, float escala, float giro, float y,
                               int alfa, float rTex) {
        int n = 96;
        float cg = Mth.cos(giro);
        float sg = Mth.sin(giro);
        float[] x = new float[4];
        float[] z = new float[4];
        float[] u = new float[4];
        float[] v = new float[4];
        for (int i = 0; i < n; i++) {
            float a0 = Mth.TWO_PI * i / n;
            float a1 = Mth.TWO_PI * (i + 1) / n;
            float[] ang = {a0, a0, a1, a1};
            float[] rr = {rDentro, rFuera, rFuera, rDentro};
            for (int k = 0; k < 4; k++) {
                float ca = Mth.cos(ang[k]);
                float sa = Mth.sin(ang[k]);
                x[k] = ca * rr[k];
                z[k] = sa * rr[k];
                if (rTex > 0.0F) {
                    u[k] = 0.5F + ca * rTex;
                    v[k] = 0.5F + sa * rTex;
                } else {
                    u[k] = 0.5F + (x[k] * cg + z[k] * sg) / (2.0F * escala);
                    v[k] = 0.5F + (z[k] * cg - x[k] * sg) / (2.0F * escala);
                }
            }
            for (int k = 0; k < 4; k++) {
                vertice(buf, p, x[k], y, z[k], u[k], v[k], alfa);
            }
            for (int k = 3; k >= 0; k--) {
                vertice(buf, p, x[k], y, z[k], u[k], v[k], alfa);
            }
        }
    }

    /** Un cuadrado tumbado de medio lado 'r' centrado en el, girado 'giro' (radianes), por las dos caras. */
    private static void disco(VertexConsumer buf, PoseStack.Pose p, float r, float giro, float y, int alfa) {
        float c = Mth.cos(giro) * r;
        float sn = Mth.sin(giro) * r;
        // Las esquinas (-1,-1), (1,-1), (1,1), (-1,1) giradas, con su u y su v.
        float[] x = {-c + sn, c + sn, c - sn, -c - sn};
        float[] z = {-sn - c, sn - c, sn + c, -sn + c};
        float[] u = {0.0F, 1.0F, 1.0F, 0.0F};
        float[] v = {0.0F, 0.0F, 1.0F, 1.0F};
        for (int i = 0; i < 4; i++) {
            vertice(buf, p, x[i], y, z[i], u[i], v[i], alfa);
        }
        for (int i = 3; i >= 0; i--) {
            vertice(buf, p, x[i], y, z[i], u[i], v[i], alfa);
        }
    }

    /**
     * La flecha de la Embestida, tumbada en el suelo delante de el: lo llenado
     * brillante y lo que falta apagado, la punta al final y, a cada lado, la fila
     * de rombos donde van a reventar los pinchos. Sigue al cuerpo mientras se gira.
     */
    private static void flecha(RajangRenderState s, PoseStack pose, SubmitNodeCollector colector) {
        float b = s.bodyRot * Mth.DEG_TO_RAD;
        float fx = -Mth.sin(b);
        float fz = Mth.cos(b);
        float ix = fz;
        float iz = -fx;
        float largo = s.carga;
        float lleno = largo * s.cargaLlena;
        float y = 0.08F;
        float desde = FLECHA_DESDE;
        float hasta = desde + largo;
        float medio = desde + lleno;
        int luzBrilla = (int) (150 + 105 * s.cargaLlena);
        int punta = s.cargaLlena >= 1.0F ? 255 : 110;
        colector.submitCustomGeometry(pose, FLECHA, (p, buf) -> {
            tira(buf, p, fx, fz, ix, iz, desde, Math.min(medio, hasta - 3.0F), FLECHA_ANCHO, 0.0F, y, 1.0F / GALON, luzBrilla);
            tira(buf, p, fx, fz, ix, iz, Math.min(medio, hasta - 3.0F), hasta - 3.0F, FLECHA_ANCHO, 0.0F, y, 1.0F / GALON, 70);
        });
        colector.submitCustomGeometry(pose, PUNTA, (p, buf) ->
                tira(buf, p, fx, fz, ix, iz, hasta - 3.0F, hasta, FLECHA_ANCHO, 0.0F, y + 0.01F, 1.0F / 3.0F, punta));
        colector.submitCustomGeometry(pose, ROMBO, (p, buf) -> {
            for (int lado = -1; lado <= 1; lado += 2) {
                tira(buf, p, fx, fz, ix, iz, desde, medio, 0.5F, lado * PINCHOS_LADO, y, 1.0F / 2.2F, luzBrilla);
                tira(buf, p, fx, fz, ix, iz, medio, hasta, 0.5F, lado * PINCHOS_LADO, y, 1.0F / 2.2F, 60);
            }
        });
    }

    /** Una tira tumbada de d0 a d1 por delante de el, de medio ancho 'ancho', apartada 'lado' de su linea. */
    private static void tira(VertexConsumer buf, PoseStack.Pose p, float fx, float fz, float ix, float iz, float d0, float d1,
                             float ancho, float lado, float y, float vPorBloque, int alfa) {
        if (d1 - d0 < 0.05F) {
            return;
        }
        float cx = ix * lado;
        float cz = iz * lado;
        float v0 = d0 * vPorBloque;
        float v1 = d1 * vPorBloque;
        // Por las dos caras: se ve aunque el suelo suba por delante de el.
        for (int cara = 0; cara < 2; cara++) {
            float k = cara == 0 ? 1.0F : -1.0F;
            float u0 = cara == 0 ? 0.0F : 1.0F;
            vertice(buf, p, cx + fx * d0 - ix * ancho * k, y, cz + fz * d0 - iz * ancho * k, u0, v0, alfa);
            vertice(buf, p, cx + fx * d0 + ix * ancho * k, y, cz + fz * d0 + iz * ancho * k, 1.0F - u0, v0, alfa);
            vertice(buf, p, cx + fx * d1 + ix * ancho * k, y, cz + fz * d1 + iz * ancho * k, 1.0F - u0, v1, alfa);
            vertice(buf, p, cx + fx * d1 - ix * ancho * k, y, cz + fz * d1 - iz * ancho * k, u0, v1, alfa);
        }
    }

    private static void vertice(VertexConsumer buf, PoseStack.Pose p, float x, float y, float z, float u, float v, int alfa) {
        buf.addVertex(p, x, y, z)
                .setColor(255, 255, 255, alfa)
                .setUv(u, v)
                .setOverlay(OverlayTexture.NO_OVERLAY)
                .setLight(0xF000F0)
                .setNormal(p, 0.0F, 1.0F, 0.0F);
    }

    /** Sin el tumbado de lado al morir: la liberacion es tumbarse como una esfinge. */
    @Override
    protected float getFlipDegrees() {
        return 0.0F;
    }

    @Override
    protected @Nullable RenderType getRenderType(RajangRenderState s, boolean visible, boolean transparente, boolean brilla) {
        if (s.disolver > 0.0F && visible) {
            return DISOLVER;
        }
        return super.getRenderType(s, visible, transparente, brilla);
    }

    @Override
    protected int getModelTint(RajangRenderState s) {
        return s.disolver > 0.0F ? ARGB.white(1.0F - s.disolver) : -1;
    }

    /** Veinticinco bloques de largo: que no desaparezca al girar la camara. */
    @Override
    protected boolean affectedByCulling(RajangEntity r) {
        return false;
    }

    @Override
    protected void scale(RajangRenderState s, PoseStack pose) {
    }

    @Override
    public Identifier getTextureLocation(RajangRenderState s) {
        return s.libre ? LIBRE : TEXTURAS[Math.clamp(s.fase, 1, 4) - 1];
    }
}
