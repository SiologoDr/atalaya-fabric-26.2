package com.atalaya.client;

import com.atalaya.Atalaya;
import com.atalaya.entity.NereaEntity;
import com.atalaya.entity.NereaGeometria;
import com.atalaya.entity.OlaNereaEntity;
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
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.ClipContext;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;
import org.jspecify.annotations.Nullable;

/**
 * Pinta a Nerea: la malla escalada x2,4 desde el remake (unos 15 bloques de
 * alto), la capa de lo que brilla y la de la Furia de las Mareas, y lo que sus
 * ataques dejan alrededor, todo de mar:
 *
 * <ul>
 *   <li>la Mirada del Abismo: un chorro de agua del abismo de cada ojo a cada
 *       uno de los que mira (se corta contra el primer bloque), un aro de agua
 *       que gira en cada ojo encendido y las grietas que le abren los impactos;</li>
 *   <li>el Remolino: el remolino del suelo bajo ella, que crece y gira, y la
 *       burbuja de aire dorada de quien lleva una antorcha;</li>
 *   <li>el Molino: el aro de espuma de hasta donde barren las anclas;</li>
 *   <li>la Gran Marea: mientras alza el tridente, el paso que dejara la ola,
 *       marcado en el suelo con luz que se cuela bajo el agua.</li>
 * </ul>
 *
 * Al final de la liberacion se deshace con el mismo efecto que el dragon del
 * End (una mascara de ruido que se va comiendo la textura), con la mascara
 * propia de nerea_extras.py.
 */
public class NereaRenderer extends MobRenderer<NereaEntity, NereaRenderState, NereaModel> {

    /** La escala de la malla (la de nerea_juego.py): unos 15 bloques de alto. */
    public static final float ESCALA = 2.4F;
    /** Una piel por fase: la maldicion se extiende (venas, coral muerto). */
    private static final Identifier[] TEXTURAS = new Identifier[4];
    private static final RenderType[] DISOLVER = new RenderType[4];
    private static final Identifier MASCARA = Identifier.fromNamespaceAndPath(Atalaya.MOD_ID,
            "textures/entity/nerea/nerea_disolver.png");

    static {
        for (int i = 0; i < 4; i++) {
            TEXTURAS[i] = Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "textures/entity/nerea/nerea_f" + (i + 1) + ".png");
            DISOLVER[i] = RenderTypes.entityCutoutDissolve(TEXTURAS[i], MASCARA);
        }
    }

    /** Desde que tick de la liberacion empieza a deshacerse. */
    private static final float DISOLVER_DESDE = 160.0F;
    /** Lo que llega a medir el remolino que se ve bajo ella (el arrastre llega mas lejos: las particulas). */
    private static final float REMOLINO_SUELO = 26.0F;

    public NereaRenderer(EntityRendererProvider.Context contexto) {
        super(contexto, new NereaModel(contexto.bakeLayer(NereaModel.CAPA)), 3.6F);
        addLayer(new NereaBrilloLayer(this));
        addLayer(new NereaFuriaLayer(this, new NereaModel(contexto.bakeLayer(NereaModel.CAPA_AURA))));
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
        s.geiser.copyFrom(n.geiser);
        s.marea.copyFrom(n.marea);
        s.canto.copyFrom(n.canto);
        s.mareaAlta.copyFrom(n.mareaAlta);
        s.encadenar.copyFrom(n.encadenar);
        s.liberacion.copyFrom(n.liberacion);
        s.estado = n.getEstado();
        if (s.estado == NereaEntity.MAREA) {
            // La Gran Marea: el cuerpo y el paso marcado, fijos hacia donde ira la
            // ola. El cuerpo del cliente sigue a la cabeza con retraso y hacia
            // girar el camino del suelo mientras avisaba.
            s.bodyRot = n.getYRot(parcial);
            s.yRot = 0.0F;
        }
        s.pesoLibre = Mth.lerp(parcial, n.pesoLibreAnt, n.pesoLibre);
        s.cadenas = n.getCadenas();
        s.fase = n.fase();
        s.ritmo = n.ritmoCliente;
        s.ojosRotos = n.getOjosRotos();
        s.golpesIzq = n.getGolpesOjo(0);
        s.golpesDer = n.getGolpesOjo(1);
        s.golpesNecesarios = n.getGolpesNecesarios();
        s.furia = n.tieneFuria() && !n.isDeadOrDying();
        s.hueco = n.getHueco();
        // En segundos de ANIMACION: con el ritmo de la fase, como el servidor.
        s.segundosEstado = (n.tickCount - n.inicioEstado + parcial) / 20.0F * n.ritmoCliente;
        s.libre = n.deathTime >= NereaGeometria.LIBERACION_OJOS_ORO;
        s.disolver = n.deathTime > DISOLVER_DESDE
                ? Mth.clamp((n.deathTime + parcial - DISOLVER_DESDE) / (NereaGeometria.DURACION_LIBERACION - DISOLVER_DESDE), 0.0F, 1.0F)
                : 0.0F;
        // Solo el destello del golpe: la liberacion no se tine de rojo.
        s.hasRedOverlay = n.hurtTime > 0 && n.deathTime < 4;
        extraerMirada(n, s, parcial);
        extraerBurbujasAire(n, s, parcial);
    }

    /** Los ojos y el final de cada chorro de la Mirada, relativos a los pies. */
    private void extraerMirada(NereaEntity n, NereaRenderState s, float parcial) {
        s.finesRayo.clear();
        s.ojoIzq = null;
        s.ojoDer = null;
        float ticks = s.segundosEstado * 20.0F;
        boolean mira = s.estado == NereaEntity.MIRADA && ticks >= NereaGeometria.MIRADA_FIJA - 4;
        if (!(mira || s.estado == NereaEntity.ATURDIDO) || n.isDeadOrDying()) {
            return;
        }
        Vec3 pies = n.getPosition(parcial);
        float rumbo = s.bodyRot;
        Vec3 izq = NereaEntity.puntoMundo(NereaGeometria.OJO_IZQ_MIRADA, pies, rumbo);
        Vec3 der = NereaEntity.puntoMundo(NereaGeometria.OJO_DER_MIRADA, pies, rumbo);
        s.ojoIzq = izq.subtract(pies);
        s.ojoDer = der.subtract(pies);
        if (s.estado != NereaEntity.MIRADA || ticks < NereaGeometria.MIRADA_FIJA) {
            return;
        }
        Vec3 medio = izq.add(der).scale(0.5);
        for (int id : n.getIdsMirada()) {
            Entity v = n.level().getEntity(id);
            if (v == null) {
                continue;
            }
            Vec3 fin = v.getEyePosition(parcial).add(0, -0.3, 0);
            BlockHitResult choque = n.level().clip(new ClipContext(medio, fin, ClipContext.Block.COLLIDER,
                    ClipContext.Fluid.NONE, n));
            if (choque.getType() != HitResult.Type.MISS) {
                fin = choque.getLocation();
            }
            s.finesRayo.add(fin.subtract(pies));
        }
        s.cargaRayo = Mth.clamp((ticks - NereaGeometria.MIRADA_FIJA)
                / (NereaGeometria.DURACION_MIRADA - NereaGeometria.MIRADA_FIJA), 0.0F, 1.0F);
    }

    /** Quien lleva antorcha mientras el Remolino arrastra: su burbuja dorada. */
    private void extraerBurbujasAire(NereaEntity n, NereaRenderState s, float parcial) {
        s.burbujasAire.clear();
        float ticks = s.segundosEstado * 20.0F;
        if (s.estado != NereaEntity.REMOLINO || ticks < NereaGeometria.REMOLINO_TIRA || ticks > NereaGeometria.REMOLINO_SUELTA) {
            return;
        }
        Vec3 pies = n.getPosition(parcial);
        for (Player p : n.level().players()) {
            if (p.isSpectator() || !p.isAlive() || p.distanceToSqr(n) > NereaEntity.RADIO_REMOLINO * NereaEntity.RADIO_REMOLINO) {
                continue;
            }
            if (p.isHolding(Items.TORCH) || p.isHolding(Items.SOUL_TORCH) || p.isHolding(Items.COPPER_TORCH)) {
                s.burbujasAire.add(p.getPosition(parcial).add(0, p.getBbHeight() * 0.5, 0).subtract(pies));
            }
        }
    }

    @Override
    protected void scale(NereaRenderState s, PoseStack pose) {
        pose.scale(ESCALA, ESCALA, ESCALA);
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

    /** Quince bloques de alto y chorros de cincuenta: que no se corte al girar la camara. */
    @Override
    protected boolean affectedByCulling(NereaEntity n) {
        return false;
    }

    @Override
    public void submit(NereaRenderState s, PoseStack pose, SubmitNodeCollector colector, CameraRenderState camara) {
        super.submit(s, pose, colector, camara);
        if (s.deathTime > 0) {
            return;
        }
        Vec3 ojo = camara.pos.subtract(s.x, s.y, s.z);
        float ticks = s.segundosEstado * 20.0F;
        switch (s.estado) {
            case NereaEntity.MIRADA, NereaEntity.ATURDIDO -> mirada(s, pose, colector, ojo);
            case NereaEntity.REMOLINO -> remolino(s, pose, colector, ojo, ticks);
            case NereaEntity.MOLINO -> molino(s, pose, colector, ticks);
            case NereaEntity.ROMPEOLAS -> rompeolas(s, pose, colector, ticks);
            case NereaEntity.MAREA -> marea(s, pose, colector, ticks);
            default -> {
            }
        }
    }

    // ------------------------------------------------------------------
    //  La Mirada del Abismo
    // ------------------------------------------------------------------

    private static void mirada(NereaRenderState s, PoseStack pose, SubmitNodeCollector colector, Vec3 ojo) {
        int color = s.furia ? NereaDibujo.FURIA : NereaDibujo.fase(s.fase);
        Vec3[] ojos = {s.ojoIzq, s.ojoDer};
        int[] golpes = {s.golpesIzq, s.golpesDer};
        if (!s.finesRayo.isEmpty()) {
            float carga = s.cargaRayo;
            // Engorda y se aclara al cargar; tiembla un poco al final, a punto de soltar.
            float ancho = 0.28F + 0.45F * carga + (carga > 0.85F ? 0.08F * Mth.sin(s.ageInTicks * 2.3F) : 0.0F);
            int alfa = (int) (175 + 80 * carga);
            int claro = NereaDibujo.claro(color, 0.25F + 0.35F * carga);
            float v0 = -s.ageInTicks * 0.25F;
            colector.submitCustomGeometry(pose, NereaDibujo.CHORRO, (p, buf) -> {
                for (int i = 0; i < 2; i++) {
                    if ((s.ojosRotos & (1 << i)) != 0 || ojos[i] == null) {
                        continue;
                    }
                    for (Vec3 fin : s.finesRayo) {
                        float largo = (float) fin.distanceTo(ojos[i]);
                        NereaDibujo.cinta(buf, p, ojos[i], fin, ojo, ancho, v0, v0 + largo * 0.4F, claro, alfa);
                        NereaDibujo.cinta(buf, p, ojos[i], fin, ojo, ancho * 0.4F, v0 * 1.3F, v0 * 1.3F + largo * 0.4F,
                                0xFFFFFF, 255);
                    }
                }
            });
        }
        // En cada ojo encendido, el aro de agua que gira; y las grietas de los impactos.
        colector.submitCustomGeometry(pose, NereaDibujo.ARO_OJO, (p, buf) -> {
            for (int i = 0; i < 2; i++) {
                if ((s.ojosRotos & (1 << i)) != 0 || ojos[i] == null) {
                    continue;
                }
                float m = 1.1F + 0.4F * s.cargaRayo + 0.08F * Mth.sin(s.ageInTicks * 0.5F + i);
                Vec3 delante = ojos[i].add(ojo.subtract(ojos[i]).normalize().scale(0.6));
                NereaDibujo.cartel(buf, p, delante, ojo, m, s.ageInTicks * (i == 0 ? 0.12F : -0.12F),
                        NereaDibujo.claro(color, 0.3F), 230);
            }
        });
        for (int i = 0; i < 2; i++) {
            if (ojos[i] == null || golpes[i] <= 0) {
                continue;
            }
            int etapa = Math.min(4, 1 + golpes[i] * 4 / Math.max(1, s.golpesNecesarios));
            Vec3 c = ojos[i];
            // Un poco por delante del ojo, hacia quien mira: que no se meta dentro.
            Vec3 delante = c.add(ojo.subtract(c).normalize().scale(0.45));
            colector.submitCustomGeometry(pose, NereaDibujo.GRIETAS[etapa - 1], (p, buf) ->
                    NereaDibujo.cartel(buf, p, delante, ojo, 0.8F, 0.0F, 0xFFFFFF, 255));
        }
    }

    // ------------------------------------------------------------------
    //  El Remolino: el agua del suelo y las burbujas de aire doradas
    // ------------------------------------------------------------------

    private static void remolino(NereaRenderState s, PoseStack pose, SubmitNodeCollector colector, Vec3 ojo, float ticks) {
        float entra = Mth.clamp((ticks - NereaGeometria.REMOLINO_TIRA + 10) / 22.0F, 0.0F, 1.0F);
        float sale = Mth.clamp((NereaGeometria.REMOLINO_SUELTA + 10 - ticks) / 12.0F, 0.0F, 1.0F);
        float k = Math.min(entra, sale);
        if (k <= 0.01F) {
            return;
        }
        float radio = REMOLINO_SUELO * (0.3F + 0.7F * k);
        float giro = -s.ageInTicks * 0.045F;
        colector.submitCustomGeometry(pose, NereaDibujo.REMOLINO, (p, buf) -> {
            NereaDibujo.suelo(buf, p, 0.0, 0.06, 0.0, radio, giro, 0xFFFFFF, (int) (225 * k));
            NereaDibujo.suelo(buf, p, 0.0, 0.09, 0.0, radio * 0.42F, giro * 2.2F + 1.0F, 0xFFFFFF, (int) (200 * k));
        });
        if (!s.burbujasAire.isEmpty()) {
            colector.submitCustomGeometry(pose, NereaDibujo.BURBUJA_AIRE, (p, buf) -> {
                for (Vec3 c : s.burbujasAire) {
                    float m = 1.45F + 0.06F * Mth.sin(s.ageInTicks * 0.4F + (float) c.x);
                    NereaDibujo.cartel(buf, p, c, ojo, m, 0.0F, 0xFFFFFF, 235);
                }
            });
        }
    }

    // ------------------------------------------------------------------
    //  El Molino: hasta donde barren las anclas
    // ------------------------------------------------------------------

    private static void molino(NereaRenderState s, PoseStack pose, SubmitNodeCollector colector, float ticks) {
        // El aro sale desde la espera de aviso (ticks negativos: el ataque aun no corre),
        // latiendo en rojo hasta que las anclas empiezan a barrer; entonces, blanco.
        float desde = -NereaEntity.aviso(NereaEntity.MOLINO) * s.ritmo;
        float entra = Mth.clamp((ticks - desde) / 4.0F, 0.0F, 1.0F);
        float sale = Mth.clamp((NereaGeometria.MOLINO_PARA + 6 - ticks) / 8.0F, 0.0F, 1.0F);
        float k = Math.min(entra, sale);
        if (k <= 0.01F) {
            return;
        }
        boolean avisa = ticks < NereaGeometria.MOLINO_GOLPEA;
        int color = avisa ? AVISO : 0xFFFFFF;
        float late = avisa ? 0.6F + 0.4F * Math.abs(Mth.sin(s.ageInTicks * 0.45F)) : 1.0F;
        float m = (float) NereaEntity.RADIO_MOLINO / NereaDibujo.ARO_EN_TEXTURA;
        colector.submitCustomGeometry(pose, NereaDibujo.ARO, (p, buf) ->
                NereaDibujo.suelo(buf, p, 0.0, 0.07, 0.0, m, s.ageInTicks * 0.01F, color, (int) (235 * k * late)));
    }

    /** El color de los avisos en el suelo (antes de que el ataque pegue). */
    private static final int AVISO = 0xFF5A4A;

    /**
     * El Rompeolas: por donde van a correr las paredes de agua, en el suelo, desde
     * la espera de aviso hasta que clava el tridente (siguen al jefe mientras apunta).
     */
    private static void rompeolas(NereaRenderState s, PoseStack pose, SubmitNodeCollector colector, float ticks) {
        float impacto = NereaGeometria.IMPACTO_ROMPEOLAS;
        if (ticks > impacto + 1) {
            return;
        }
        float desde = -NereaEntity.aviso(NereaEntity.ROMPEOLAS) * s.ritmo;
        float k = Mth.clamp((ticks - desde) / 4.0F, 0.0F, 1.0F);
        int olas = new int[]{1, 1, 3, 5, 5}[Mth.clamp(s.fase, 1, 4)];
        float late = 0.75F + 0.25F * Math.abs(Mth.sin(s.ageInTicks * 0.5F));
        int alfa = (int) (255 * k * late);
        float corre = s.ageInTicks * 0.08F;
        for (int w = 0; w < olas; w++) {
            float b = (s.bodyRot + (w - (olas - 1) / 2.0F) * NereaEntity.ABANICO_OLAS) * Mth.DEG_TO_RAD;
            Vec3 dir = new Vec3(-Mth.sin(b), 0, Mth.cos(b));
            Vec3 a = dir.scale(3.0).add(0, 0.08, 0);
            Vec3 z = dir.scale(NereaEntity.LARGO_OLA).add(0, 0.08, 0);
            // El ancho exacto de la ola; el color va en la textura (aviso_calle.py).
            colector.submitCustomGeometry(pose, NereaDibujo.AVISO_CALLE, (p, buf) ->
                    NereaDibujo.tira(buf, p, a, z, NereaEntity.MEDIO_ANCHO_OLA, -corre,
                            (float) NereaEntity.LARGO_OLA / 5.0F - corre, 0xFFFFFF, alfa));
        }
    }

    // ------------------------------------------------------------------
    //  La Gran Marea: el paso que dejara la ola
    // ------------------------------------------------------------------

    private static void marea(NereaRenderState s, PoseStack pose, SubmitNodeCollector colector, float ticks) {
        float lanza = NereaGeometria.MAREA_LANZA;
        if (ticks > lanza + 2) {
            return;
        }
        // Sale desde la espera de aviso, con ella quieta, hasta que suelta la ola.
        float desde = -NereaEntity.aviso(NereaEntity.MAREA) * s.ritmo;
        float k = Mth.clamp((ticks - desde) / 8.0F, 0.0F, 1.0F);
        float b = s.bodyRot * Mth.DEG_TO_RAD;
        Vec3 dir = new Vec3(-Mth.sin(b), 0, Mth.cos(b));
        Vec3 lado = OlaNereaEntity.lado(dir);
        // El paso empieza donde nace la ola, por detras de ella.
        Vec3 a = dir.scale(1.0 - NereaEntity.MAREA_ATRAS).add(lado.scale(s.hueco)).add(0, 0.07, 0);
        Vec3 z = dir.scale(NereaEntity.MAREA_LARGO).add(lado.scale(s.hueco)).add(0, 0.07, 0);
        // Parpadea mas deprisa cuanto menos queda.
        float prisa = 0.25F + 0.5F * Mth.clamp((ticks - desde) / (lanza - desde), 0.0F, 1.0F);
        int brillo = (int) ((165 + 75 * Mth.sin(s.ageInTicks * prisa)) * k);
        float corre = s.ageInTicks * 0.02F;
        colector.submitCustomGeometry(pose, NereaDibujo.SENDERO, (p, buf) ->
                NereaDibujo.tira(buf, p, a, z, NereaEntity.MAREA_HUECO / 2.0F, (1.0F - NereaEntity.MAREA_ATRAS) / 5.0F - corre,
                        NereaEntity.MAREA_LARGO / 5.0F - corre, 0xFFFFFF, brillo));
    }

    @Override
    public Identifier getTextureLocation(NereaRenderState s) {
        return TEXTURAS[Math.clamp(s.fase, 1, 4) - 1];
    }
}
