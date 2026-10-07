package com.atalaya.item;

import com.atalaya.effect.ParalisisEffect;
import com.atalaya.habilidad.Habilidades;
import com.atalaya.habilidad.Jefes;
import com.atalaya.particula.AtalayaParticulas;
import com.atalaya.sonido.AtalayaSonidos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;

/**
 * El Martillo de Jade, el arma del tanque (tierra): 9 de dano y lento. Con el
 * golpe cargado del todo, a un monstruo normal lo deja aturdido 1 s y hace que
 * vaya a por quien lo lleva (a minijefes y jefes no les hace nada de eso).
 */
public class MartilloJadeItem extends Item {

    /** Lo cargado que tiene que estar el golpe para aturdir. */
    private static final float CARGADO = 0.9F;

    public MartilloJadeItem(Properties props) {
        super(props);
    }

    @Override
    public void postHurtEnemy(ItemStack stack, LivingEntity blanco, LivingEntity atacante) {
        super.postHurtEnemy(stack, blanco, atacante);
        if (!(atacante.level() instanceof ServerLevel nivel) || !(atacante instanceof Player jugador)) {
            return;
        }
        boolean cargado = Habilidades.carga(jugador) >= CARGADO;
        double y = blanco.getY() + blanco.getBbHeight() * 0.5;
        if (!cargado) {
            nivel.playSound(null, blanco.getX(), y, blanco.getZ(), AtalayaSonidos.MARTILLO_GOLPE, SoundSource.PLAYERS, 0.8F,
                    0.95F + nivel.getRandom().nextFloat() * 0.1F);
            return;
        }
        nivel.playSound(null, blanco.getX(), y, blanco.getZ(), AtalayaSonidos.MARTILLO_CARGA, SoundSource.PLAYERS, 1.0F,
                0.95F + nivel.getRandom().nextFloat() * 0.1F);
        nivel.sendParticles(AtalayaParticulas.RAJANG_JADE, blanco.getX(), y, blanco.getZ(), 10, 0.3, 0.3, 0.3, 0.12);
        nivel.sendParticles(AtalayaParticulas.RAJANG_POLVO, blanco.getX(), blanco.getY() + 0.1, blanco.getZ(), 6, 0.5, 0.05, 0.5, 0.03);
        if (Jefes.esJefeOMinijefe(blanco)) {
            return;
        }
        blanco.addEffect(new MobEffectInstance(ParalisisEffect.PARALISIS, 20, 0, false, true, true), jugador);
        if (blanco instanceof Mob mob) {
            mob.setTarget(jugador);
        }
    }
}
