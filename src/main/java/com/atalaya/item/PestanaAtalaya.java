package com.atalaya.item;

import com.atalaya.Atalaya;
import com.atalaya.bestiario.Bestias;
import com.atalaya.cambios.ObjetosCambios;
import net.fabricmc.fabric.api.creativetab.v1.FabricCreativeModeTab;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.Identifier;
import net.minecraft.world.item.CreativeModeTab;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;

/**
 * La pestana del mod en el inventario de creativo (Juan, 19-10-2026: «todos los mobs, armaduras, armas, etc., todos
 * separemoslos en un apartado del inventario de creativo»). Todo lo del mod va aqui y ya no en las pestanas de
 * Minecraft, en este orden:
 *
 * <pre>
 *   los huevos      los jefes, los mini jefes, los mobs y los del bestiario (en el orden del menu de los mobs)
 *   las armaduras   el traje hazmat y las de los jefes
 *   las armas       las cuatro de rol de los jefes
 *   lo que salva    los totems, el kit de reparacion y los corazones de vida y blanco
 *   los cambios     lo de los cambios de dificultad (la pildora de la plaga y las ayudas)
 *   los materiales  lo que sueltan los mobs y los jefes, y lo que se craftea con ello
 * </pre>
 *
 * Lo de los minijuegos de los jefes (el idolo, la cana, el prisma...) sigue sin salir: solo se tiene durante la pelea.
 */
public final class PestanaAtalaya {

    private PestanaAtalaya() {
    }

    /** Despues de registrar todos los items. */
    public static void registrar() {
        CreativeModeTab pestana = FabricCreativeModeTab.builder()
                .title(Component.translatable("itemGroup.atalaya"))
                .icon(() -> new ItemStack(AtalayaItems.OJO_VIGIA))
                .displayItems((parametros, salida) -> {
                    for (Item[] grupo : grupos()) {
                        for (Item item : grupo) {
                            salida.accept(item);
                        }
                    }
                })
                .build();
        Registry.register(BuiltInRegistries.CREATIVE_MODE_TAB, Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "atalaya"),
                pestana);
    }

    private static Item[][] grupos() {
        return new Item[][]{
                {AtalayaItems.HUEVO_VIGIA, AtalayaItems.HUEVO_NEREA, AtalayaItems.HUEVO_AERALIS, AtalayaItems.HUEVO_RAJANG,
                        AtalayaItems.HUEVO_NOVILIS},
                {AtalayaItems.HUEVO_MOCTEZUMA, AtalayaItems.HUEVO_YIATZO, AtalayaItems.HUEVO_ATLAHUA,
                        AtalayaItems.HUEVO_XIUHQUETZAL},
                {AtalayaItems.HUEVO_FULMINANTE, AtalayaItems.HUEVO_FOGONAZO, AtalayaItems.HUEVO_COCO},
                Bestias.huevos(),
                HazmatArmor.todas(),
                ArmadurasJefes.armaduras(),
                ArmadurasJefes.armas(),
                AtalayaItems.TOTEMS,
                {AtalayaItems.KIT_REPARACION, AtalayaItems.CORAZON_VIDA, AtalayaItems.CORAZON_BLANCO},
                {ObjetosCambios.PILDORA_PLAGA, ObjetosCambios.BOLSA_VACIO, ObjetosCambios.YUNQUE_DORADO,
                        ObjetosCambios.FRUTO_RECUERDO, ObjetosCambios.RAIZ_AGUA, ObjetosCambios.PILDORA_TAMANO},
                AtalayaItems.todos(),
        };
    }
}
