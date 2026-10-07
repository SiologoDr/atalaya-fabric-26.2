package com.atalaya.item;

import com.atalaya.entity.FlechaVendavalEntity;
import com.atalaya.sonido.AtalayaSonidos;
import net.minecraft.core.registries.Registries;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundSource;
import net.minecraft.stats.Stats;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.projectile.Projectile;
import net.minecraft.world.entity.projectile.arrow.AbstractArrow;
import net.minecraft.world.item.BowItem;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.enchantment.EnchantmentHelper;
import net.minecraft.world.item.enchantment.Enchantments;
import net.minecraft.world.level.Level;

import java.util.List;

/**
 * El Arco del Vendaval, el arma del soporte (viento). Sus flechas salen un 20 %
 * mas rapidas (llegan antes y caen menos: para los ojos de Nerea y los nucleos
 * de Aeralis) y pegan como con Poder III sin encantar; encima admite Poder V
 * (en total, como un Poder VIII). Con flechas normales dispara flechas del
 * vendaval: la que da a un aliado no le hace dano y le da Velocidad I y un 5 %
 * mas durante 3 s (como mucho una vez cada 20 s por jugador).
 */
public class ArcoVendavalItem extends BowItem {

    /** Los niveles de Poder que ya trae el arco sin encantar. */
    private static final int PODER_PROPIO = 3;
    /** Lo que corren mas las flechas. */
    private static final float VELOCIDAD = 1.2F;

    public ArcoVendavalItem(Properties props) {
        super(props);
    }

    @Override
    public boolean releaseUsing(ItemStack stack, Level nivel, LivingEntity usuario, int quedan) {
        if (!(usuario instanceof Player jugador)) {
            return false;
        }
        ItemStack municion = jugador.getProjectile(stack);
        if (municion.isEmpty()) {
            return false;
        }
        float fuerza = getPowerForTime(getUseDuration(stack, usuario) - quedan);
        if (fuerza < 0.1F) {
            return false;
        }
        List<ItemStack> flechas = draw(stack, municion, jugador);
        if (nivel instanceof ServerLevel servidor && !flechas.isEmpty()) {
            shoot(servidor, jugador, jugador.getUsedItemHand(), stack, flechas, fuerza * 3.0F * VELOCIDAD, 1.0F, fuerza == 1.0F, null);
        }
        nivel.playSound(null, jugador.getX(), jugador.getY(), jugador.getZ(), AtalayaSonidos.ARCO_DISPARO, SoundSource.PLAYERS, 1.0F,
                1.0F / (nivel.getRandom().nextFloat() * 0.4F + 1.2F) + fuerza * 0.5F);
        jugador.awardStat(Stats.ITEM_USED.get(this));
        return true;
    }

    @Override
    protected Projectile createProjectile(Level nivel, LivingEntity tirador, ItemStack arma, ItemStack municion, boolean critico) {
        Projectile proyectil;
        if (municion.is(Items.ARROW)) {
            FlechaVendavalEntity flecha = new FlechaVendavalEntity(nivel, tirador, municion.copyWithCount(1), arma);
            flecha.setCritArrow(critico);
            proyectil = flecha;
        } else {
            // Las flechas con efecto y las espectrales salen como siempre, con el dano del arco.
            proyectil = super.createProjectile(nivel, tirador, arma, municion, critico);
        }
        if (proyectil instanceof AbstractArrow flecha) {
            flecha.setBaseDamage(danoBase(nivel, arma));
        }
        return proyectil;
    }

    /**
     * El dano de la flecha pasa por su velocidad, y estas corren un 20 % mas:
     * se descuenta aqui para que lo de mas sea solo rapidez. Asi pega como un
     * arco de Poder (III + el que tenga), con el Poder del encantamiento
     * sumandose despues al dar, como en vanilla.
     */
    private static double danoBase(Level nivel, ItemStack arma) {
        int encantado = EnchantmentHelper.getItemEnchantmentLevel(
                nivel.registryAccess().lookupOrThrow(Registries.ENCHANTMENT).getOrThrow(Enchantments.POWER), arma);
        double objetivo = 2.0 + poder(PODER_PROPIO + encantado);
        return objetivo / VELOCIDAD - poder(encantado);
    }

    /** Lo que suma Poder a la flecha en vanilla: 1 en el nivel I y 0,5 mas por nivel. */
    private static double poder(int nivelPoder) {
        return nivelPoder <= 0 ? 0.0 : 1.0 + 0.5 * (nivelPoder - 1);
    }
}
