package com.atalaya.entity;

import com.atalaya.habilidad.Habilidades;
import com.atalaya.particula.AtalayaParticulas;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.projectile.arrow.AbstractArrow;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.EntityHitResult;

/**
 * Una flecha del Arco del Vendaval: vuela como una flecha normal (con la
 * velocidad y el dano que le pone el arco) dejando una estela de viento. Si da
 * a un aliado (otro jugador) no le hace dano: le da el empujon del viento
 * (Habilidades.flechaAliado) y se deshace.
 */
public class FlechaVendavalEntity extends AbstractArrow {

    public FlechaVendavalEntity(EntityType<? extends FlechaVendavalEntity> tipo, Level nivel) {
        super(tipo, nivel);
    }

    public FlechaVendavalEntity(Level nivel, LivingEntity tirador, ItemStack municion, ItemStack arma) {
        super(AtalayaEntities.FLECHA_VENDAVAL, tirador, nivel, municion, arma);
    }

    @Override
    protected ItemStack getDefaultPickupItem() {
        return new ItemStack(Items.ARROW);
    }

    @Override
    public void tick() {
        super.tick();
        if (level().isClientSide() && !isInGround() && tickCount % 2 == 0) {
            level().addParticle(AtalayaParticulas.AERALIS_POLVO, getX(), getY(), getZ(), 0.0, 0.0, 0.0);
        }
    }

    @Override
    protected void onHitEntity(EntityHitResult golpe) {
        if (golpe.getEntity() instanceof Player aliado && getOwner() instanceof Player tirador && aliado != tirador) {
            if (!level().isClientSide()) {
                Habilidades.flechaAliado(aliado);
            }
            discard();
            return;
        }
        super.onHitEntity(golpe);
    }
}
