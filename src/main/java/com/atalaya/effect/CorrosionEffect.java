package com.atalaya.effect;

import com.atalaya.Atalaya;
import net.minecraft.core.Holder;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.effect.MobEffect;
import net.minecraft.world.effect.MobEffectCategory;

/**
 * Efecto de estado "Corrosion": la lluvia se come la armadura.
 *
 * No tiene niveles, y es a proposito. La radiacion y la insolacion miden "lo
 * cerca" o "lo seco" que estas; aqui no hay grados: o te esta cayendo encima o
 * no. Un solo escalon dice justo eso.
 *
 * Como la insolacion, el efecto es solo la cara visible — icono, nombre y color
 * de la barra. Quien desgasta las piezas es
 * {@link com.atalaya.corrosion.CorrosionManager}.
 */
public class CorrosionEffect extends MobEffect {

    /** Verde acido, tomado del propio icono. Lo separa del morado de la
     *  radiacion y del naranja de la insolacion cuando coinciden en la barra. */
    private static final int COLOR = 0x6FBF2A;

    public static final ResourceKey<MobEffect> CLAVE = ResourceKey.create(
            Registries.MOB_EFFECT,
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "corrosion"));

    public static Holder<MobEffect> CORROSION;

    protected CorrosionEffect() {
        super(MobEffectCategory.HARMFUL, COLOR);
    }

    public static void registrar() {
        CORROSION = Registry.registerForHolder(
                BuiltInRegistries.MOB_EFFECT, CLAVE, new CorrosionEffect());
    }

    // ------------------------------------------------------------------
    //  Cuanto come por segundo
    // ------------------------------------------------------------------

    /** Segundos de lluvia que funden una pieza entera. */
    public static final int SEGUNDOS_PARA_FUNDIR = 15;

    /**
     * Durabilidad que pierde una pieza por segundo bajo la lluvia.
     *
     * Es PROPORCIONAL al maximo de cada pieza, no una cantidad fija, y ahi esta
     * toda la idea: el cuero y la netherita se funden en el mismo tiempo. Con un
     * desgaste plano, la netherita (407) aguantaria seis veces mas que unas
     * botas de cuero (65), y la lluvia dejaria de dar miedo en cuanto tuvieras
     * buen equipo. Asi la amenaza no se compra con material.
     *
     * Se redondea hacia ARRIBA para que las piezas mas baratas no se queden
     * cortas por el resto de la division: eso las funde algo antes de los quince
     * segundos, nunca despues.
     */
    public static int desgastePorSegundo(int durabilidadMaxima) {
        return Math.max(1, (int) Math.ceil(durabilidadMaxima / (double) SEGUNDOS_PARA_FUNDIR));
    }
}
