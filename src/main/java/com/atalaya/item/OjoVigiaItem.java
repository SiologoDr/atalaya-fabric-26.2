package com.atalaya.item;

import net.minecraft.server.level.ServerLevel;
import com.atalaya.sonido.AtalayaSonidos;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;

/**
 * Ojo del Vigia: lo que queda del farol cuando el bicho cae.
 *
 * Es su mirada vuelta del reves. El Vigia te hacia brillar a ti para que todo
 * te encontrara; el ojo hace brillar a todo lo que hay alrededor para que lo
 * encuentres tu. Clic derecho y, durante diez segundos, los monstruos a 32
 * bloques se ven a traves de las paredes.
 *
 * Ocho usos y un minuto de espera entre uno y otro: sirve para decidir por donde
 * entrar en una cueva, no para llevar un radar encendido.
 */
public class OjoVigiaItem extends Item {

    private static final double RADIO = 32.0;
    private static final int DURACION_BRILLO = 200;
    private static final int ESPERA = 1200;

    public OjoVigiaItem(Properties propiedades) {
        super(propiedades);
    }

    @Override
    public InteractionResult use(Level nivel, Player jugador, InteractionHand mano) {
        ItemStack pila = jugador.getItemInHand(mano);
        if (nivel instanceof ServerLevel servidor) {
            for (Monster monstruo : servidor.getEntitiesOfClass(Monster.class,
                    jugador.getBoundingBox().inflate(RADIO))) {
                monstruo.addEffect(new MobEffectInstance(MobEffects.GLOWING, DURACION_BRILLO, 0, false, false), jugador);
            }
            servidor.playSound(null, jugador.getX(), jugador.getY(), jugador.getZ(),
                    AtalayaSonidos.OJO_VIGIA_USAR, SoundSource.PLAYERS, 1.0F, 1.0F);
            jugador.getCooldowns().addCooldown(pila, ESPERA);
            pila.hurtAndBreak(1, jugador, mano);
        }
        return InteractionResult.SUCCESS;
    }
}
