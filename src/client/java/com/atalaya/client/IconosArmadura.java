package com.atalaya.client;

import com.atalaya.Atalaya;
import com.atalaya.habilidad.Habilidades;
import com.atalaya.item.ArmadurasJefes;
import com.atalaya.item.HazmatArmor;
import java.util.HashMap;
import java.util.Map;
import net.minecraft.resources.Identifier;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.player.Player;
import org.jspecify.annotations.Nullable;

/**
 * Los iconos de la barra de armadura con un conjunto entero puesto (las cuatro
 * piezas del mismo): la pechera de ese conjunto, con sus colores y un brillo
 * que la cruza (hud/armor/<conjunto>_*.png, de iconos_armadura_hud.py). Con
 * piezas sueltas o mezcladas, los de vanilla.
 *
 * Los conjuntos: las cuatro armaduras de los jefes (mareas, jade, vendaval,
 * solar) y el traje Hazmat. Lo pinta IconosArmaduraMixin, en Hud.extractArmor.
 */
public final class IconosArmadura {

    private static final String[] CONJUNTOS = {"mareas", "jade", "vendaval", "solar", "hazmat"};
    /** Lleno, medio y vacio de cada conjunto. */
    private static final Map<String, Identifier[]> SPRITES = new HashMap<>();
    private static final EquipmentSlot[] HUECOS = {EquipmentSlot.HEAD, EquipmentSlot.CHEST, EquipmentSlot.LEGS,
            EquipmentSlot.FEET};

    static {
        for (String c : CONJUNTOS) {
            SPRITES.put(c, new Identifier[]{sprite(c, "full"), sprite(c, "half"), sprite(c, "empty")});
        }
    }

    /** El conjunto del jugador cuya barra se esta pintando (lo pone el mixin al empezar). */
    private static @Nullable String conjunto;

    private IconosArmadura() {
    }

    private static Identifier sprite(String conjunto, String que) {
        return Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "hud/armor/" + conjunto + "_" + que);
    }

    /** Antes de pintar la barra: que conjunto entero lleva (o ninguno). */
    public static void preparar(Player p) {
        ArmadurasJefes.Tema tema = Habilidades.conjunto(p);
        conjunto = tema != null ? tema.id : trajeHazmat(p) ? "hazmat" : null;
    }

    private static boolean trajeHazmat(Player p) {
        for (EquipmentSlot hueco : HUECOS) {
            if (!HazmatArmor.esPieza(p.getItemBySlot(hueco).getItem())) {
                return false;
            }
        }
        return true;
    }

    /** El icono que va en lugar del de vanilla (hud/armor_full, _half o _empty). */
    public static Identifier sprite(Identifier vanilla) {
        if (conjunto == null || !vanilla.getNamespace().equals("minecraft")) {
            return vanilla;
        }
        Identifier[] s = SPRITES.get(conjunto);
        return switch (vanilla.getPath()) {
            case "hud/armor_full" -> s[0];
            case "hud/armor_half" -> s[1];
            case "hud/armor_empty" -> s[2];
            default -> vanilla;
        };
    }
}
