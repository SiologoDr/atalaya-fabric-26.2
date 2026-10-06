package com.atalaya.client;

import com.atalaya.Atalaya;
import com.atalaya.entity.NovilisEntity;
import com.atalaya.entity.NovilisGeometria;
import com.mojang.blaze3d.vertex.PoseStack;
import net.minecraft.client.renderer.SubmitNodeCollector;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.MobRenderer;
import net.minecraft.client.renderer.rendertype.RenderType;
import net.minecraft.client.renderer.rendertype.RenderTypes;
import net.minecraft.client.renderer.state.level.CameraRenderState;
import net.minecraft.resources.Identifier;
import net.minecraft.util.ARGB;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.phys.Vec3;
import org.jspecify.annotations.Nullable;

/**
 * Pinta a Novilis: la malla escalada x1,75 (16 bloques hasta el yelmo), la
 * capa de lo que brilla y las auras (la Furia azul y las llamas carmesi del Dios
 * de la Guerra), y lo que sus ataques dejan alrededor:
 *
 * <ul>
 *   <li>su sol, que flota sobre el halo: crece mientras carga las Fuentes y se
 *       vuelve de oro al liberarse;</li>
 *   <li>el Castigo solar: el haz de su sol a la punta de la espada en alto;</li>
 *   <li>la Ofrenda: el haz que senala a quien va a coger, y luego al que tiene
 *       en las manos;</li>
 *   <li>el sol que se le forma en la mano en el Sol x3.</li>
 * </ul>
 *
 * Al final de la liberacion se deshace con la mascara de novilis_disolver.png.
 */
public class NovilisRenderer extends MobRenderer<NovilisEntity, NovilisRenderState, NovilisModel> {

    /** La escala de la malla (la de novilis_juego.py): 16 bloques hasta el yelmo. */
    public static final float ESCALA = 256.0F / 146.0F;
    private static final Identifier[] TEXTURAS = new Identifier[6];
    private static final RenderType[] DISOLVER = new RenderType[6];
    private static final Identifier MASCARA = Identifier.fromNamespaceAndPath(Atalaya.MOD_ID,
            "textures/entity/novilis/novilis_disolver.png");
    private static final String[] PIELES = {"f1", "f2", "f3", "f4", "furia", "libre"};
    private static final float DISOLVER_DESDE = 160.0F;

    static {
        for (int i = 0; i < PIELES.length; i++) {
            TEXTURAS[i] = Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "textures/entity/novilis/novilis_" + PIELES[i] + ".png");
            DISOLVER[i] = RenderTypes.entityCutoutDissolve(TEXTURAS[i], MASCARA);
        }
    }

    public NovilisRenderer(EntityRendererProvider.Context contexto) {
        super(contexto, new NovilisModel(contexto.bakeLayer(NovilisModel.CAPA)), 3.4F);
        addLayer(new NovilisBrilloLayer(this));
        addLayer(new NovilisAuraLayer(this, new NovilisModel(contexto.bakeLayer(NovilisModel.CAPA_AURA))));
    }

    /** La piel de ahora: la de la fase, la de la Furia o la de liberado. */
    static int piel(NovilisRenderState s) {
        return s.libre ? 5 : s.furia ? 4 : Math.clamp(s.fase, 1, 4) - 1;
    }

    @Override
    public NovilisRenderState createRenderState() {
        return new NovilisRenderState();
    }

    @Override
    public void extractRenderState(NovilisEntity n, NovilisRenderState s, float parcial) {
        super.extractRenderState(n, s, parcial);
        s.estado = n.getEstado();
        s.pesoLibre = Mth.lerp(parcial, n.pesoLibreAnt, n.pesoLibre);
        s.fase = n.fase();
        s.ritmo = n.ritmoCliente;
        s.furia = n.tieneFuria() && !n.isDeadOrDying();
        s.grito = n.tieneGrito() && !n.isDeadOrDying();
        s.carga = n.getCarga();
        s.segundosEstado = (n.tickCount - n.inicioEstado + parcial) / 20.0F * n.ritmoCliente;
        s.segundosLibera = (n.deathTime + parcial) / 20.0F;
        s.libre = n.deathTime >= NovilisGeometria.LIBERACION_ORO;
        s.disolver = n.deathTime > DISOLVER_DESDE
                ? Mth.clamp((n.deathTime + parcial - DISOLVER_DESDE) / (NovilisGeometria.DURACION_LIBERACION - DISOLVER_DESDE), 0.0F, 1.0F)
                : 0.0F;
        s.hasRedOverlay = n.hurtTime > 0 && n.deathTime < 4;

        Vec3 pies = n.getPosition(parcial);
        float rumbo = s.bodyRot;
        s.sol = NovilisEntity.puntoMundo(NovilisGeometria.SOL_PROPIO, pies, rumbo).subtract(pies);
        float tk = s.segundosEstado * 20.0F;
        s.punta = null;
        if ((s.estado == NovilisEntity.CASTIGO || s.estado == NovilisEntity.CASTIGO_ONDA)
                && tk >= NovilisGeometria.CASTIGO_ALZA - 2 && tk < NovilisGeometria.CASTIGO_RAYO + 2) {
            s.punta = NovilisEntity.puntoMundo(NovilisGeometria.PUNTA_ALZA, pies, rumbo).subtract(pies);
        }
        s.marca = null;
        int id = n.getIdOfrenda() >= 0 ? n.getIdOfrenda() : n.getIdMarca();
        if (id >= 0 && s.estado == NovilisEntity.OFRENDA) {
            Entity v = n.level().getEntity(id);
            if (v != null) {
                s.marca = v.getPosition(parcial).add(0, v.getBbHeight() * 0.6, 0).subtract(pies);
            }
        }
        s.solMano = null;
        if (s.estado == NovilisEntity.SOL && tk > 6 && tk < NovilisGeometria.SOL_LANZA_3) {
            // Se le forma en la mano y desaparece al soltarlo (hasta que se forma el siguiente).
            boolean ve = true;
            for (int l : new int[]{NovilisGeometria.SOL_LANZA_1, NovilisGeometria.SOL_LANZA_2}) {
                if (tk >= l && tk < l + 8) {
                    ve = false;
                }
            }
            if (ve) {
                s.solMano = NovilisEntity.puntoMundo(NovilisGeometria.MANO_SOL, pies, rumbo).subtract(pies);
            }
        }
    }

    @Override
    protected void scale(NovilisRenderState s, PoseStack pose) {
        pose.scale(ESCALA, ESCALA, ESCALA);
    }

    /** Sin el tumbado de lado al morir: la liberacion es de rodilla. */
    @Override
    protected float getFlipDegrees() {
        return 0.0F;
    }

    @Override
    protected @Nullable RenderType getRenderType(NovilisRenderState s, boolean visible, boolean transparente, boolean brilla) {
        if (s.disolver > 0.0F && visible) {
            return DISOLVER[piel(s)];
        }
        return super.getRenderType(s, visible, transparente, brilla);
    }

    @Override
    protected int getModelTint(NovilisRenderState s) {
        return s.disolver > 0.0F ? ARGB.white(1.0F - s.disolver) : -1;
    }

    @Override
    protected boolean affectedByCulling(NovilisEntity n) {
        return false;
    }

    @Override
    public void submit(NovilisRenderState s, PoseStack pose, SubmitNodeCollector colector, CameraRenderState camara) {
        super.submit(s, pose, colector, camara);
        Vec3 ojo = camara.pos.subtract(s.x, s.y, s.z);
        float edad = s.ageInTicks;
        int color = s.libre ? NovilisDibujo.LIBRE : NovilisDibujo.color(s.furia ? 5 : s.fase);
        // --- Su sol, sobre el halo ---
        float radio;
        int alfa;
        if (s.deathTime > 0) {
            float k = 1.0F - s.disolver;
            radio = 2.2F * (0.6F + 0.4F * k);
            alfa = (int) (230 * k);
        } else if (s.estado == NovilisEntity.DORMIDO) {
            radio = 1.2F;
            alfa = (int) (120 + 40 * Mth.sin(edad * 0.06F));
        } else {
            radio = 2.2F + (s.estado == NovilisEntity.FUENTES ? 4.0F * s.carga : 0.0F);
            alfa = 235;
        }
        if (alfa > 4) {
            float r = radio;
            int a = alfa;
            colector.submitCustomGeometry(pose, NovilisDibujo.SOL, (p, buf) -> NovilisDibujo.sol(buf, p, s.sol, ojo, r, edad, color, a));
        }
        if (s.deathTime > 0) {
            return;
        }
        // --- El Castigo: su sol baja a la espada en alto ---
        if (s.punta != null) {
            Vec3 punta = s.punta;
            colector.submitCustomGeometry(pose, NovilisDibujo.HAZ, (p, buf) ->
                    NovilisDibujo.haz(buf, p, s.sol, punta, ojo, 0.55F + 0.1F * Mth.sin(edad * 0.8F), -edad * 0.2F, color, 220));
            colector.submitCustomGeometry(pose, NovilisDibujo.SOL, (p, buf) ->
                    NovilisDibujo.sol(buf, p, punta, ojo, 0.9F, edad, color, 230));
        }
        // --- La Ofrenda: el haz a quien senala, o al que ofrece ---
        if (s.marca != null) {
            Vec3 m = s.marca;
            colector.submitCustomGeometry(pose, NovilisDibujo.HAZ, (p, buf) ->
                    NovilisDibujo.haz(buf, p, s.sol, m, ojo, 0.9F + 0.15F * Mth.sin(edad * 0.6F), -edad * 0.15F, color, 200));
        }
        // --- El Sol x3: el que se le forma en la mano ---
        if (s.solMano != null) {
            Vec3 c = s.solMano;
            colector.submitCustomGeometry(pose, NovilisDibujo.SOL, (p, buf) -> NovilisDibujo.sol(buf, p, c, ojo, 1.1F, edad, color, 240));
        }
    }

    @Override
    public Identifier getTextureLocation(NovilisRenderState s) {
        return TEXTURAS[piel(s)];
    }
}
