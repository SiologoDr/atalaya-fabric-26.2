package com.atalaya.item;

import com.atalaya.entity.JefesUnicos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.SpawnEggItem;
import net.minecraft.world.item.context.UseOnContext;
import net.minecraft.world.level.Level;
import org.jspecify.annotations.Nullable;

/**
 * El huevo de un jefe: como el de vanilla, pero si ya hay uno de ese jefe en el
 * mundo no lo suelta (ni se gasta) y dice donde esta. Un jefe de cada tipo por
 * mundo: JefesUnicos.
 */
public class HuevoJefeItem extends SpawnEggItem {

    public HuevoJefeItem(Properties propiedades) {
        super(propiedades);
    }

    @Override
    public InteractionResult useOn(UseOnContext ctx) {
        if (yaHay(ctx.getLevel(), ctx.getItemInHand(), ctx.getPlayer())) {
            return InteractionResult.FAIL;
        }
        return super.useOn(ctx);
    }

    @Override
    public InteractionResult use(Level nivel, Player jugador, InteractionHand mano) {
        if (yaHay(nivel, jugador.getItemInHand(mano), jugador)) {
            return InteractionResult.FAIL;
        }
        return super.use(nivel, jugador, mano);
    }

    /** En el servidor: si ya hay un jefe de los de este huevo, se lo dice al jugador. */
    private static boolean yaHay(Level nivel, ItemStack huevo, @Nullable Player jugador) {
        if (!(nivel instanceof ServerLevel servidor)) {
            return false;
        }
        EntityType<?> tipo = SpawnEggItem.getType(huevo);
        JefesUnicos.Registro otro = JefesUnicos.ocupado(servidor.getServer(), tipo, null);
        if (otro == null) {
            return false;
        }
        if (jugador != null) {
            jugador.sendOverlayMessage(JefesUnicos.aviso(tipo, otro));
        }
        return true;
    }
}
