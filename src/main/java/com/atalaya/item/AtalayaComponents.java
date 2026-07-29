package com.atalaya.item;

import com.atalaya.Atalaya;
import com.mojang.serialization.Codec;
import net.minecraft.core.Registry;
import net.minecraft.core.component.DataComponentType;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.network.codec.ByteBufCodecs;
import net.minecraft.resources.Identifier;

/**
 * Componentes de datos propios del mod.
 *
 * Un componente es lo que en la version de plugin era el PersistentDataContainer:
 * informacion pegada a un ItemStack concreto que sobrevive a guardados y viaja
 * al cliente.
 */
public final class AtalayaComponents {

    /**
     * Marca una pieza del traje que salio con filtro reforzado.
     *
     * Se pone al craftear, con probabilidad, y reduce la duracion del veneno.
     * Es un simple marcador: su presencia es la informacion.
     */
    public static DataComponentType<Boolean> ANTIVENENO;

    /**
     * Marca un casco que salio con el visor bien pulido.
     *
     * Se decide al fabricarlo. El casco normal oscurece la pantalla; el de
     * visor excelente no, asi que ves con claridad sin renunciar al traje.
     */
    public static DataComponentType<Boolean> VISOR_EXCELENTE;

    /**
     * Marca una pieza usada como ICONO en el menu de configuracion.
     *
     * Sin esto, el icono del crafteo (que es un casco de verdad) arrastraria
     * al menu la lista de caracteristicas del traje, mezclada con el texto del
     * interruptor. Es solo cosmetico y no viaja a disco.
     */
    public static DataComponentType<Boolean> ICONO_MENU;

    private AtalayaComponents() {
    }

    public static void registrar() {
        ANTIVENENO = marcador("antiveneno");
        VISOR_EXCELENTE = marcador("visor_excelente");
        ICONO_MENU = marcador("icono_menu");
    }

    /** Componente booleano simple: su presencia es la informacion. */
    private static DataComponentType<Boolean> marcador(String nombre) {
        return Registry.register(
                BuiltInRegistries.DATA_COMPONENT_TYPE,
                Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, nombre),
                DataComponentType.<Boolean>builder()
                        .persistent(Codec.BOOL)                  // se guarda en disco
                        .networkSynchronized(ByteBufCodecs.BOOL) // y viaja al cliente
                        .build());
    }
}
