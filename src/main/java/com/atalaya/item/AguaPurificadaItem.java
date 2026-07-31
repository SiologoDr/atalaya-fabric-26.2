package com.atalaya.item;

import com.atalaya.hidratacion.Hidratacion;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;

/**
 * Agua purificada: se bebe y devuelve hidratacion.
 *
 * Casi todo lo hace vanilla y no este fichero. El item lleva puesto el
 * componente CONSUMABLE, asi que la animacion de beber, el temblor de la mano,
 * el sonido de trago y las particulas salen solos; y lleva USE_REMAINDER, que
 * es quien devuelve la botella vacia al terminar (y la tira al suelo si el
 * inventario esta lleno, igual que hace una pocion). Aqui solo queda lo que
 * vanilla no puede saber: cuanta hidratacion sube y cuando no vale la pena
 * beber.
 *
 * A diferencia de {@link FiltroCarbonItem}, que se usa de golpe porque hay que
 * poder cambiar el filtro con la radiacion encima, esta SI hace esperar: beber
 * en mitad del desierto no es una urgencia.
 */
public class AguaPurificadaItem extends Item {

    /**
     * Puntos que devuelve cada botella.
     *
     * Veinte de cien, o sea que cinco botellas llenan el deposito vacio. Y como
     * se pierde un punto cada siete segundos, cada botella son 2 min 20 s mas
     * de desierto.
     */
    private static final int RESTAURA = 20;

    public AguaPurificadaItem(Properties propiedades) {
        super(propiedades);
    }

    /**
     * Con el deposito lleno no se bebe.
     *
     * Cortar aqui, ANTES de delegar en vanilla, es lo que evita que el jugador
     * se quede tres cuartos de segundo bebiendo para tirar la botella a la
     * basura. El cliente conoce su propia hidratacion porque el dato viaja
     * solo, asi que ni siquiera empieza la animacion.
     */
    @Override
    public InteractionResult use(Level nivel, Player jugador, InteractionHand mano) {
        if (Hidratacion.de(jugador) >= Hidratacion.MAXIMO) {
            return InteractionResult.FAIL;
        }
        return super.use(nivel, jugador, mano);
    }

    /**
     * Al terminar el trago. La llamada a super es la que gasta la botella y
     * deja el vidrio vacio, asi que va DESPUES de sumar.
     */
    @Override
    public ItemStack finishUsingItem(ItemStack pila, Level nivel, LivingEntity entidad) {
        if (!nivel.isClientSide() && entidad instanceof Player jugador) {
            Hidratacion.poner(jugador, Hidratacion.de(jugador) + RESTAURA);
        }
        return super.finishUsingItem(pila, nivel, entidad);
    }
}
