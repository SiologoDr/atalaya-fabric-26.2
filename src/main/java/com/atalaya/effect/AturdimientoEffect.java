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
 * Efecto "Aturdimiento": te deja clavado en el sitio.
 *
 * Como los otros del mod, el efecto es solo la cara visible —icono, nombre y
 * color de la barra—. Quien clava al jugador es
 * {@link com.atalaya.aturdimiento.AturdimientoManager}, colgandole modificadores
 * de velocidad y de salto.
 *
 * Y aqui hay una razon de mas para separarlo: la cuenta atras se acorta a
 * pulsaciones, y la duracion de un MobEffect no se puede recortar sin quitarlo
 * y volverlo a poner. El numero vive en un attachment aparte.
 */
public class AturdimientoEffect extends MobEffect {

    /** Amarillo de aviso, el de las estrellitas de los dibujos. */
    private static final int COLOR = 0xF2C94C;

    public static final ResourceKey<MobEffect> CLAVE = ResourceKey.create(
            Registries.MOB_EFFECT,
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "aturdimiento"));

    public static Holder<MobEffect> ATURDIMIENTO;

    protected AturdimientoEffect() {
        super(MobEffectCategory.HARMFUL, COLOR);
    }

    public static void registrar() {
        ATURDIMIENTO = Registry.registerForHolder(
                BuiltInRegistries.MOB_EFFECT, CLAVE, new AturdimientoEffect());
    }

    /** Identificadores de los modificadores que cuelga y descuelga el manager. */
    public static final Identifier ID_MOVIMIENTO = id("aturdimiento_movimiento");
    public static final Identifier ID_SALTO = id("aturdimiento_salto");

    private static Identifier id(String ruta) {
        return Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, ruta);
    }
}
