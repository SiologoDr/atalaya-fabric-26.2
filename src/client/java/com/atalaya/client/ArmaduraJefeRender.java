package com.atalaya.client;

import com.atalaya.Atalaya;
import com.atalaya.item.ArmadurasJefes;
import com.mojang.blaze3d.vertex.PoseStack;
import net.fabricmc.fabric.api.client.rendering.v1.ArmorRenderer;
import net.fabricmc.fabric.api.client.rendering.v1.ModelLayerRegistry;
import net.minecraft.client.model.HumanoidModel;
import net.minecraft.client.model.Model;
import net.minecraft.client.model.geom.ModelLayerLocation;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.renderer.SubmitNodeCollector;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.state.HumanoidRenderState;
import net.minecraft.client.renderer.rendertype.RenderType;
import net.minecraft.client.renderer.rendertype.RenderTypes;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.resources.Identifier;
import net.minecraft.util.ARGB;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.item.ItemStack;

import java.util.function.Function;

/**
 * Pinta las armaduras de los jefes en 3D (Fabric ArmorRenderer: sustituye a la
 * capa plana de vanilla en jugadores, maniquies, soportes y monstruos). Cada
 * pieza es su propia malla (ArmaduraJefeMalla, generada por
 * armaduras_jefes.py): la armadura sobre el cuerpo mas sus piezas por encima,
 * que siguen al cuerpo (copia la postura del modelo de quien la lleva) y se
 * mueven solas (la capa y las aletas ondean, las alas aletean, las esquirlas
 * flotan; mas al andar). Se pinta en capas:
 *
 * <pre>
 *   base       lo opaco
 *   membrana   lo translucido (aletas, cristales, alas)
 *   brillo     lo que brilla sin luz, en 8 cuadros: la luz corre por las costuras
 *   destello   el de los encantamientos, si lo lleva
 * </pre>
 */
public final class ArmaduraJefeRender implements ArmorRenderer {

    private static final String[] PIEZAS = {"casco", "pechera", "grebas", "botas"};
    private static final int CUADROS = 8;
    /** Ticks por cuadro del brillo. */
    private static final float CADA = 2.5F;

    /** Lo que necesita la malla para moverse: la edad y lo deprisa que anda. */
    public record Estado(float edad, float andar) {
    }

    /** La malla de una pieza, con sus animaciones (no toca la postura que copia del cuerpo). */
    public static final class Modelo extends Model<Estado> {

        private final ArmaduraJefeMalla.Anim[] anims;
        private final ModelPart[] partes;

        Modelo(ModelPart raiz, ArmaduraJefeMalla.Anim[] anims) {
            super(raiz, RenderTypes::armorCutoutNoCull);
            this.anims = anims;
            Function<String, ModelPart> busca = raiz.createPartLookup();
            this.partes = new ModelPart[anims.length];
            for (int i = 0; i < anims.length; i++) {
                partes[i] = busca.apply(anims[i].parte());
            }
        }

        @Override
        public void setupAnim(Estado s) {
            // Sin resetPose: el cuerpo ya viene copiado del modelo de quien la lleva.
            float andar = Mth.clamp(s.andar() * 2.5F, 0.0F, 1.0F);
            for (int i = 0; i < anims.length; i++) {
                ArmaduraJefeMalla.Anim a = anims[i];
                ModelPart p = partes[i];
                if (p == null) {
                    continue;
                }
                float onda = Mth.sin(s.edad() * a.frecuencia() * 2.0F + a.fase())
                        * a.amplitud() * (1.0F + a.andar() * andar * 2.5F);
                switch (a.eje()) {
                    case 0 -> p.xRot += onda;
                    case 1 -> p.yRot += onda;
                    case 2 -> p.zRot += onda;
                    case 3 -> p.y += onda;
                    case 4 -> p.yRot += s.edad() * a.amplitud();
                    case 5 -> p.xRot += a.amplitud() * a.andar() * andar;
                    default -> {
                    }
                }
            }
        }
    }

    private final ArmadurasJefes.Tema tema;
    private final Modelo[] modelos = new Modelo[4];
    private final boolean[] membrana = new boolean[4];
    private final RenderType base;
    private final RenderType translucida;
    private final RenderType[] brillo = new RenderType[CUADROS];

    private ArmaduraJefeRender(ArmadurasJefes.Tema tema, EntityRendererProvider.Context contexto) {
        this.tema = tema;
        for (int i = 0; i < 4; i++) {
            modelos[i] = new Modelo(contexto.bakeLayer(capa(tema, PIEZAS[i])), ArmaduraJefeMalla.anims(tema.id, PIEZAS[i]));
            membrana[i] = ArmaduraJefeMalla.conMembrana(tema.id, PIEZAS[i]);
        }
        base = RenderTypes.armorCutoutNoCull(tex(tema.id));
        translucida = RenderTypes.armorTranslucent(tex(tema.id + "_membrana"));
        for (int k = 0; k < CUADROS; k++) {
            brillo[k] = RenderTypes.eyes(tex(tema.id + "_brillo_" + k));
        }
    }

    private static Identifier tex(String nombre) {
        return Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "textures/entity/armadura/" + nombre + ".png");
    }

    private static ModelLayerLocation capa(ArmadurasJefes.Tema tema, String pieza) {
        return new ModelLayerLocation(Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "armadura_" + tema.id), pieza);
    }

    /** Registra las mallas y quien las pinta (desde AtalayaClient). */
    public static void registrar() {
        for (ArmadurasJefes.Tema tema : ArmadurasJefes.Tema.values()) {
            for (String pieza : PIEZAS) {
                ModelLayerRegistry.registerModelLayer(capa(tema, pieza), () -> ArmaduraJefeMalla.crear(tema.id, pieza));
            }
            ArmorRenderer.register(contexto -> new ArmaduraJefeRender(tema, contexto), ArmadurasJefes.PIEZAS.get(tema));
        }
    }

    @Override
    public void render(PoseStack pose, SubmitNodeCollector colector, ItemStack stack, HumanoidRenderState s,
                       EquipmentSlot ranura, int luz, HumanoidModel<HumanoidRenderState> cuerpo) {
        int i = switch (ranura) {
            case HEAD -> 0;
            case CHEST -> 1;
            case LEGS -> 2;
            case FEET -> 3;
            default -> -1;
        };
        if (i < 0) {
            return;
        }
        Modelo modelo = modelos[i];
        Estado estado = new Estado(s.ageInTicks, s.walkAnimationSpeed);
        // OJO: el entero de despues del overlay es el color del contorno (el de los que brillan), no un tinte.
        ArmorRenderer.submitTransformCopyingModel(cuerpo, s, modelo, estado, true, colector, pose, base, luz,
                OverlayTexture.NO_OVERLAY, s.outlineColor, null);
        if (membrana[i]) {
            ArmorRenderer.submitTransformCopyingModel(cuerpo, s, modelo, estado, true, colector.order(1), pose, translucida,
                    luz, OverlayTexture.NO_OVERLAY, 0, null);
        }
        // El brillo: un cuadro se funde con el siguiente, asi la luz corre seguida.
        float t = s.ageInTicks / CADA;
        int k = Mth.floor(t) % CUADROS;
        float mezcla = t - Mth.floor(t);
        // (aqui si va un tinte: la variante con sprite lleva el color y luego el contorno)
        ArmorRenderer.submitTransformCopyingModel(cuerpo, s, modelo, estado, true, colector.order(2), pose, brillo[k],
                0xF000F0, OverlayTexture.NO_OVERLAY, ARGB.colorFromFloat(1.0F, 1.0F - mezcla, 1.0F - mezcla, 1.0F - mezcla),
                null, 0, null);
        ArmorRenderer.submitTransformCopyingModel(cuerpo, s, modelo, estado, true, colector.order(2), pose,
                brillo[(k + 1) % CUADROS], 0xF000F0, OverlayTexture.NO_OVERLAY,
                ARGB.colorFromFloat(1.0F, mezcla, mezcla, mezcla), null, 0, null);
        if (stack.hasFoil()) {
            ArmorRenderer.submitTransformCopyingModel(cuerpo, s, modelo, estado, true, colector.order(3), pose,
                    RenderTypes.armorEntityGlint(), luz, OverlayTexture.NO_OVERLAY, 0, null);
        }
    }
}
