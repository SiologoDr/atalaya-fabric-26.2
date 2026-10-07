package com.atalaya.item;

import com.atalaya.entity.TridenteMareasEntity;
import com.atalaya.habilidad.Habilidades;
import com.atalaya.sonido.AtalayaSonidos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundSource;
import net.minecraft.stats.Stats;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.projectile.Projectile;
import net.minecraft.world.entity.projectile.arrow.AbstractArrow;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TridentItem;
import net.minecraft.world.level.Level;

/**
 * El Tridente de las Mareas, el arma del sanador (agua): 9 de dano en la mano
 * y lanzado, y siempre vuelve a quien lo lanzo (lleva la lealtad dentro, sin
 * encantar). Cada golpe, en la mano o lanzado, cura medio corazon al aliado
 * mas herido cerca, como mucho una vez cada 8 s por portador.
 *
 * No hace la acometida: es para curar y pegar, no para volar.
 */
public class TridenteMareasItem extends TridentItem {

    public TridenteMareasItem(Properties props) {
        super(props);
    }

    @Override
    public boolean releaseUsing(ItemStack stack, Level nivel, LivingEntity usuario, int quedan) {
        if (!(usuario instanceof Player jugador)) {
            return false;
        }
        int usado = getUseDuration(stack, usuario) - quedan;
        if (usado < 10 || stack.nextDamageWillBreak()) {
            return false;
        }
        if (nivel instanceof ServerLevel servidor) {
            stack.hurtWithoutBreaking(1, jugador);
            ItemStack lanzado = stack.consumeAndReturn(1, jugador);
            TridenteMareasEntity t = Projectile.spawnProjectileFromRotation(TridenteMareasEntity::crear, servidor, lanzado, jugador,
                    0.0F, 2.5F, 1.0F);
            if (jugador.hasInfiniteMaterials()) {
                t.pickup = AbstractArrow.Pickup.CREATIVE_ONLY;
            }
            servidor.playSound(null, t, AtalayaSonidos.TRIDENTE_LANZAR, SoundSource.PLAYERS, 1.0F, 1.0F);
        }
        jugador.awardStat(Stats.ITEM_USED.get(this));
        return true;
    }

    @Override
    public void postHurtEnemy(ItemStack stack, LivingEntity blanco, LivingEntity atacante) {
        super.postHurtEnemy(stack, blanco, atacante);
        if (atacante.level() instanceof ServerLevel nivel && atacante instanceof Player jugador) {
            nivel.playSound(null, blanco.getX(), blanco.getY() + 1.0, blanco.getZ(), AtalayaSonidos.MAREAS_TRIDENTE_GOLPE,
                    SoundSource.PLAYERS, 0.8F, 0.95F + nivel.getRandom().nextFloat() * 0.1F);
            Habilidades.curaTridente(jugador);
        }
    }
}
