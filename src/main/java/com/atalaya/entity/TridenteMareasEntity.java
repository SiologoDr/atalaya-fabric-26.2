package com.atalaya.entity;

import com.atalaya.habilidad.Habilidades;
import com.atalaya.item.ArmadurasJefes;
import com.atalaya.mixin.ThrownTridentAccessor;
import com.atalaya.particula.AtalayaParticulas;
import com.atalaya.sonido.AtalayaSonidos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.projectile.arrow.ThrownTrident;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.EntityHitResult;

/**
 * El Tridente de las Mareas cuando vuela: el tridente de vanilla por dentro
 * (el vuelo, el clavarse y la vuelta), con la lealtad siempre puesta, sus
 * propios sonidos y la cura del sanador al dar. Lo dibuja
 * TridenteMareasRenderer con el modelo del objeto.
 */
public class TridenteMareasEntity extends ThrownTrident {

    /** La lealtad con la que vuelve (la de vanilla III). */
    private static final byte LEALTAD = 3;

    public TridenteMareasEntity(EntityType<? extends TridenteMareasEntity> tipo, Level nivel) {
        super(tipo, nivel);
        this.entityData.set(ThrownTridentAccessor.atalaya$lealtad(), LEALTAD);
    }

    /** Lo crea Projectile.spawnProjectileFromRotation desde el objeto. */
    public static TridenteMareasEntity crear(ServerLevel nivel, LivingEntity lanzador, ItemStack stack) {
        TridenteMareasEntity t = new TridenteMareasEntity(AtalayaEntities.TRIDENTE_MAREAS, nivel);
        t.setOwner(lanzador);
        t.setPos(lanzador.getX(), lanzador.getEyeY() - 0.1, lanzador.getZ());
        t.setPickupItemStack(stack.copy());
        return t;
    }

    @Override
    protected ItemStack getDefaultPickupItem() {
        return new ItemStack(ArmadurasJefes.ARMAS.get(ArmadurasJefes.Tema.MAREAS));
    }

    @Override
    protected void onHitEntity(EntityHitResult golpe) {
        super.onHitEntity(golpe);
        if (level() instanceof ServerLevel nivel && getOwner() instanceof Player jugador && golpe.getEntity() instanceof LivingEntity) {
            nivel.sendParticles(AtalayaParticulas.NEREA_BURBUJA, getX(), getY(), getZ(), 6, 0.2, 0.2, 0.2, 0.05);
            Habilidades.curaTridente(jugador);
        }
    }

    /** Sus sonidos en lugar de los del tridente de vanilla. */
    @Override
    public void playSound(SoundEvent sonido, float volumen, float tono) {
        if (sonido == SoundEvents.TRIDENT_RETURN) {
            sonido = AtalayaSonidos.TRIDENTE_VUELVE;
            volumen = Math.min(volumen, 2.0F);
        } else if (sonido == SoundEvents.TRIDENT_HIT || sonido == SoundEvents.TRIDENT_HIT_GROUND) {
            sonido = AtalayaSonidos.MAREAS_TRIDENTE_GOLPE;
        }
        super.playSound(sonido, volumen, tono);
    }

    @Override
    protected SoundEvent getDefaultHitGroundSoundEvent() {
        return AtalayaSonidos.MAREAS_TRIDENTE_GOLPE;
    }
}
